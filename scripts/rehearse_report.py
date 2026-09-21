#!/usr/bin/env python3
"""Rehearsal report: measure, don't narrate.

Given a completed dry-run job directory (a "rehearsal"), this tool re-derives
every number an operator would need to judge whether the real pipeline would
actually break in production -- durations, audio/video sync, subtitle cues,
visual-beat timing against the *real* measured audio, the 16:9 no-subtitle
guarantee, loudness, and per-stage wall time versus the hard subprocess
timeouts baked into adapters.py.

Design choice: this script never imports pilot.py/adapters.py/story_plan.py
from the rehearsed job's own tree. It reads only the artifacts those modules
already wrote to disk (JSON envelopes, .srt, .wav, .mp4, the sqlite events
log) and re-measures them independently with ffprobe/ffmpeg. An auditor that
recomputes a value with the same code under audit isn't auditing anything --
it is just checking the code agrees with itself. Every artifact path/shape
referenced below is a black-box read that matches the current schemas
(schemas/*.json), adapters.py (subtitle_cues/make_srt/master/render),
workflow.py (reviews/<stage>/<rev>/{manifest.json,visual-timing.json}) and
scripts/story_plan.py (timeline()) as of this writing -- if those shapes
change, the checks below should be updated to match, not "fixed" by making
this tool trust the pipeline's own recomputation instead of its output.

Anything this tool cannot verify (missing tool, missing artifact, ambiguous
data) is reported as status "unsupported" with a reason. It is never guessed
into a pass. See AGENTS.md: "Thiếu khả năng nghe/xem phải báo unsupported và
giữ job chưa hoàn tất."

CLI:
    python3 scripts/rehearse_report.py --root <sandbox_root> --job <job_id> --out <dir> [--no-frames] [--frame-limit N]

Library:
    from scripts.rehearse_report import rehearse_report
    report = rehearse_report(root, job, out_dir, extract_frames=True, frame_limit=None)
"""
import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

OK, WARN, FAIL, UNSUPPORTED = 'ok', 'warn', 'fail', 'unsupported'
DEFAULT_MIN_SEC, DEFAULT_MAX_SEC = 45, 60  # pilot.checks() fallback when a job has no brief.
# Hard ceilings from adapters.py subprocess calls; a stage creeping toward
# these in a *rehearsal* is the whole point of measuring wall time at all.
STAGE_TIMEOUT_S = {'audio': 1800, 'images': None, 'render': 3600, 'control': None, 'content': None}
EN_WORKER_TIMEOUT_S = 7200  # adapters.english() -> scripts/en_worker.py subprocess


# ---------- generic helpers ----------

def load_json(path):
    return json.loads(Path(path).read_text())


def which_or_none(name):
    return shutil.which(name)


def run(cmd, timeout=120):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None


def ffprobe_json(path):
    """Full ffprobe -show_streams -show_format dump, or None if ffprobe/file missing."""
    if not which_or_none('ffprobe') or not Path(path).is_file():
        return None
    r = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])
    if not r or r.returncode:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def stream_duration(probe, codec_type):
    if not probe:
        return None
    for s in probe.get('streams', []):
        if s.get('codec_type') == codec_type and s.get('duration') is not None:
            try:
                return float(s['duration'])
            except ValueError:
                continue
    fmt = probe.get('format', {})
    if codec_type is None and fmt.get('duration') is not None:
        try:
            return float(fmt['duration'])
        except ValueError:
            return None
    return None


def format_duration(probe):
    if not probe:
        return None
    try:
        return float(probe['format']['duration'])
    except (KeyError, ValueError, TypeError):
        return None


def extract_frame(video_path, t_seconds, out_path):
    if not which_or_none('ffmpeg'):
        return False, 'ffmpeg not on PATH'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = run(['ffmpeg', '-y', '-ss', f'{max(0.0, t_seconds):.3f}', '-i', str(video_path),
             '-frames:v', '1', '-q:v', '2', str(out_path)], timeout=60)
    if r is None or r.returncode or not out_path.is_file() or not out_path.stat().st_size:
        return False, (r.stderr[-500:] if r else 'ffmpeg not found or timed out')
    return True, None


def measure_loudness(path):
    """Single-pass loudnorm analysis -- the exact method adapters.master() uses
    to compute its gain, reused here to check the RESULT, not to recompute it."""
    if not which_or_none('ffmpeg') or not Path(path).is_file():
        return None, 'ffmpeg missing or file missing'
    r = run(['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], timeout=120)
    if r is None:
        return None, 'ffmpeg failed or timed out'
    try:
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        return {'input_i': float(m['input_i']), 'input_tp': float(m['input_tp']),
                'input_lra': float(m['input_lra']), 'input_thresh': float(m['input_thresh'])}, None
    except (ValueError, KeyError):
        return None, 'could not parse loudnorm output; see stderr tail: ' + r.stderr[-300:]


_SRT_TIME = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d)')


def srt_time_to_seconds(s):
    m = _SRT_TIME.match(s.strip())
    if not m:
        return None
    h, mi, sec, ms = (int(x) for x in m.groups())
    return h * 3600 + mi * 60 + sec + ms / 1000.0


def parse_srt(text):
    """Minimal, tolerant .srt parser: index line, time-range line, text lines, blank."""
    blocks = re.split(r'\n\s*\n', text.strip() + '\n')
    cues = []
    for block in blocks:
        lines = [l for l in block.splitlines() if l.strip() != '']
        if len(lines) < 2:
            continue
        time_line_idx = 1 if lines[0].strip().isdigit() else 0
        if '-->' not in lines[time_line_idx]:
            continue
        start_s, end_s = [x.strip() for x in lines[time_line_idx].split('-->')]
        start, end = srt_time_to_seconds(start_s), srt_time_to_seconds(end_s)
        text_lines = lines[time_line_idx + 1:]
        cues.append({'start': start, 'end': end, 'text': '\n'.join(text_lines)})
    return cues


def issue(bucket, status, check, detail, **extra):
    row = {'check': check, 'status': status, 'detail': detail}
    row.update(extra)
    bucket.append(row)
    return row


# ---------- artifact discovery (all black-box: read what the pipeline wrote) ----------

def job_dir(root, job):
    return Path(root) / 'runs' / job


def latest_module_revision(jdir, module):
    """Highest revisions/<module>/<N>/ that actually has output.json (a run
    that ended in failure.json only is skipped but still surfaced separately)."""
    base = jdir / 'revisions' / module
    if not base.is_dir():
        return None, None, []
    all_revs = sorted((int(d.name) for d in base.iterdir() if d.is_dir() and d.name.isdigit()))
    blocked = [n for n in all_revs if (base / str(n) / 'failure.json').is_file()]
    ok_revs = [n for n in all_revs if (base / str(n) / 'output.json').is_file()]
    if not ok_revs:
        return None, None, blocked
    rev = max(ok_revs)
    envelope = load_json(base / str(rev) / 'output.json')
    return rev, envelope, blocked


def read_brief(jdir):
    pointer = jdir / 'brief-current.json'
    if not pointer.is_file():
        return None, None
    meta = load_json(pointer)
    path = jdir / 'briefs' / f"{int(meta['revision'])}.json"
    if not path.is_file():
        return None, None
    return meta['revision'], load_json(path)


def find_visual_timing(jdir):
    base = jdir / 'reviews' / 'media'
    if not base.is_dir():
        return None, None
    revs = sorted((int(d.name) for d in base.iterdir() if d.is_dir() and d.name.isdigit() and (d / 'visual-timing.json').is_file()))
    if not revs:
        return None, None
    rev = revs[-1]
    return rev, load_json(base / str(rev) / 'visual-timing.json')


def find_stage_manifest(jdir, stage):
    base = jdir / 'reviews' / stage
    if not base.is_dir():
        return None, None
    revs = sorted((int(d.name) for d in base.iterdir() if d.is_dir() and d.name.isdigit() and (d / 'manifest.json').is_file()))
    if not revs:
        return None, None
    rev = revs[-1]
    return rev, load_json(base / str(rev) / 'manifest.json')


def read_events(root, job):
    db_path = Path(root) / '.state' / 'jobs.sqlite'
    if not db_path.is_file():
        return None, 'Không thấy .state/jobs.sqlite; không đo được thời gian từng công đoạn'
    try:
        con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        con.row_factory = sqlite3.Row
        rows = con.execute('SELECT id, at, module, event, detail FROM events WHERE job=? ORDER BY id', (job,)).fetchall()
        con.close()
        return [dict(r) for r in rows], None
    except sqlite3.Error as ex:
        return None, f'Không đọc được jobs.sqlite (read-only): {ex}'


# ---------- checks ----------

def check_durations(jdir, brief, content, audio_env, render_env, issues):
    result = {'status': UNSUPPORTED, 'reason': None}
    if not audio_env:
        result['reason'] = 'Chưa có audio đã chạy (revisions/audio/*/output.json)'
        issue(issues, UNSUPPORTED, 'duration', result['reason'])
        return result
    audio = audio_env['payload']
    min_sec, max_sec = DEFAULT_MIN_SEC, DEFAULT_MAX_SEC
    if brief:
        min_sec, max_sec = brief['duration']['min_seconds'], brief['duration']['max_seconds']
    result['brief_window'] = {'min_seconds': min_sec, 'max_seconds': max_sec}

    def measure_track(label, segments, master_path):
        rows = []
        measured_sum = 0.0
        for seg in segments:
            p = jdir / seg['path']
            probe = ffprobe_json(p)
            d = format_duration(probe)
            rows.append({'scene_id': seg['scene_id'], 'recorded_start': seg['start'], 'recorded_end': seg['end'],
                         'recorded_duration': round(seg['end'] - seg['start'], 4),
                         'ffprobe_duration': round(d, 4) if d is not None else None,
                         'path': seg['path']})
            if d is not None:
                measured_sum += d
        master_probe = ffprobe_json(jdir / master_path) if master_path else None
        master_duration = format_duration(master_probe)
        return {'scenes': rows, 'measured_scene_sum': round(measured_sum, 4),
                'master_measured_duration': round(master_duration, 4) if master_duration is not None else None,
                'master_recorded_duration': audio.get('duration') if label == 'vi' else audio.get('en', {}).get('duration')}

    result['vi'] = measure_track('vi', audio['segments'], audio['wav'])
    if audio.get('en'):
        result['en'] = measure_track('en', audio['en']['scenes'], audio['en']['wav'])

    for lang in ['vi'] + (['en'] if audio.get('en') else []):
        d = result[lang]
        md = d['master_measured_duration']
        if md is None:
            issue(issues, UNSUPPORTED, f'duration/{lang}/master_wav', 'ffprobe không đọc được audio master')
        else:
            if abs(md - d['measured_scene_sum']) > 0.05:
                issue(issues, WARN, f'duration/{lang}/scene_sum_vs_master',
                      f'Tổng cảnh đo được {d["measured_scene_sum"]:.3f}s khác audio master {md:.3f}s (lệch {md - d["measured_scene_sum"]:+.3f}s)')
            if not (min_sec <= md <= max_sec):
                issue(issues, FAIL, f'duration/{lang}/window',
                      f'Audio master {lang} = {md:.3f}s, ngoài khoảng brief [{min_sec}, {max_sec}]s')

    video_probe = ffprobe_json(jdir / render_env['payload']['video']) if render_env else None
    if video_probe:
        vdur = format_duration(video_probe)
        result['video_duration'] = round(vdur, 4) if vdur is not None else None
        ref = result.get('vi', {}).get('master_measured_duration')
        # For a pure 16:9 job the video is timed to the EN track instead.
        if brief and brief.get('aspect_ratio') == '16:9' and result.get('en'):
            ref = result['en']['master_measured_duration']
        if vdur is not None and ref is not None:
            delta = vdur - ref
            status = OK if abs(delta) <= 0.15 else (WARN if abs(delta) <= 0.5 else FAIL)
            issue(issues, status, 'duration/video_vs_master',
                  f'mp4={vdur:.3f}s, audio master tương ứng={ref:.3f}s, lệch={delta:+.3f}s')
            if not (min_sec <= vdur <= max_sec):
                issue(issues, FAIL, 'duration/video_window', f'mp4 = {vdur:.3f}s, ngoài khoảng brief [{min_sec},{max_sec}]s')
    else:
        issue(issues, UNSUPPORTED, 'duration/video', 'Không có render đã chạy hoặc ffprobe lỗi')

    for key in ('video_9x16', 'video_16x9'):
        if render_env and render_env['payload'].get(key):
            p2 = ffprobe_json(jdir / render_env['payload'][key])
            d2 = format_duration(p2)
            result[key + '_duration'] = round(d2, 4) if d2 is not None else None

    result['status'] = OK
    return result


def check_av_sync(jdir, render_env, issues):
    if not render_env:
        issue(issues, UNSUPPORTED, 'av_sync', 'Chưa có render')
        return {'status': UNSUPPORTED}
    out = {'files': {}}
    files = {'main': render_env['payload'].get('video'), '9x16': render_env['payload'].get('video_9x16'),
             '16x9': render_env['payload'].get('video_16x9')}
    any_checked = False
    for label, rel in files.items():
        if not rel:
            continue
        probe = ffprobe_json(jdir / rel)
        if not probe:
            issue(issues, UNSUPPORTED, f'av_sync/{label}', f'Không đọc được {rel} bằng ffprobe')
            continue
        vdur = stream_duration(probe, 'video')
        adur = stream_duration(probe, 'audio')
        if vdur is None or adur is None:
            issue(issues, UNSUPPORTED, f'av_sync/{label}', 'Thiếu luồng video hoặc audio trong mp4')
            continue
        delta = vdur - adur
        status = OK if abs(delta) <= 0.05 else (WARN if abs(delta) <= 0.2 else FAIL)
        out['files'][label] = {'path': rel, 'video_stream_duration': round(vdur, 4),
                                'audio_stream_duration': round(adur, 4), 'delta': round(delta, 4)}
        issue(issues, status, f'av_sync/{label}', f'{rel}: video={vdur:.3f}s audio={adur:.3f}s lệch={delta:+.3f}s')
        any_checked = True
    out['status'] = OK if any_checked else UNSUPPORTED
    return out


def check_subtitles(jdir, audio_env, render_env, issues):
    if not audio_env:
        issue(issues, UNSUPPORTED, 'subtitles', 'Chưa có audio')
        return {'status': UNSUPPORTED}
    audio = audio_env['payload']
    srt_rel = audio.get('srt')
    if not srt_rel or not (jdir / srt_rel).is_file():
        issue(issues, UNSUPPORTED, 'subtitles', 'Không có file .srt')
        return {'status': UNSUPPORTED}
    srt_cues = parse_srt((jdir / srt_rel).read_text())
    if not render_env:
        issue(issues, UNSUPPORTED, 'subtitles/props_cues', 'Chưa có render nên chưa có props.json để đối chiếu')
        return {'status': UNSUPPORTED, 'srt_cue_count': len(srt_cues)}
    props_path = None
    for rev_dir in sorted((jdir / 'revisions' / 'render').glob('*'), key=lambda d: int(d.name) if d.name.isdigit() else -1, reverse=True):
        cand = rev_dir / 'props.json'
        if cand.is_file():
            props_path = cand
            break
    if not props_path:
        issue(issues, UNSUPPORTED, 'subtitles/props_cues', 'Không tìm thấy props.json đã lưu ở revisions/render/*')
        return {'status': UNSUPPORTED, 'srt_cue_count': len(srt_cues)}
    props = load_json(props_path)
    props_cues = props.get('cues', [])
    out = {'srt_cue_count': len(srt_cues), 'props_cue_count': len(props_cues), 'mismatches': []}
    if len(srt_cues) != len(props_cues):
        issue(issues, FAIL, 'subtitles/count', f'.srt có {len(srt_cues)} cue, props.cues có {len(props_cues)} cue')
    n = min(len(srt_cues), len(props_cues))
    for i in range(n):
        s, c = srt_cues[i], props_cues[i]
        row = {'index': i, 'srt_text': s['text'], 'props_text': c.get('text'),
               'srt_start': s['start'], 'props_start': c.get('start'),
               'srt_end': s['end'], 'props_end': c.get('end')}
        text_ok = s['text'] == c.get('text')
        start_ok = s['start'] is not None and c.get('start') is not None and abs(s['start'] - c['start']) <= 0.002
        end_ok = s['end'] is not None and c.get('end') is not None and abs(s['end'] - c['end']) <= 0.002
        if not (text_ok and start_ok and end_ok):
            row['text_match'], row['start_match'], row['end_match'] = text_ok, start_ok, end_ok
            out['mismatches'].append(row)
    if out['mismatches']:
        issue(issues, FAIL, 'subtitles/content', f'{len(out["mismatches"])}/{n} cue lệch giữa .srt và props.cues (xem report.json)')
    else:
        issue(issues, OK, 'subtitles/content', f'{n} cue khớp .srt và props.cues (văn bản + thời gian trong 2ms)')
    out['status'] = OK
    return out


def check_visual_timing(jdir, content, audio_env, issues):
    rev, timing = find_visual_timing(jdir)
    if not timing:
        issue(issues, UNSUPPORTED, 'visual_timing', 'Không có reviews/media/*/visual-timing.json')
        return {'status': UNSUPPORTED}
    if not audio_env:
        issue(issues, UNSUPPORTED, 'visual_timing', 'Có visual-timing.json nhưng chưa có audio để đối chiếu')
        return {'status': UNSUPPORTED, 'revision': rev}
    audio = audio_env['payload']
    out = {'status': OK, 'revision': rev, 'languages': {}}
    span_source = {'vi': audio['segments'], 'en': audio.get('en', {}).get('scenes', [])}
    for lang, scenes in timing.items():
        spans = {s['scene_id']: s for s in span_source.get(lang, [])}
        lang_out = []
        for sc in scenes:
            real = spans.get(sc['id'])
            row = {'scene_id': sc['id'], 'timeline_start': sc['start'], 'timeline_end': sc['end']}
            if not real:
                row['note'] = 'Không tìm thấy cảnh tương ứng trong audio thật'
                issue(issues, FAIL, f'visual_timing/{lang}/{sc["id"]}', 'Cảnh trong visual-timing.json không khớp audio thật')
                lang_out.append(row)
                continue
            row['audio_real_start'] = real['start']
            row['audio_real_end'] = real['end']
            drift_start = sc['start'] - real['start']
            drift_end = sc['end'] - real['end']
            row['start_drift'] = round(drift_start, 4)
            row['end_drift'] = round(drift_end, 4)
            if abs(drift_start) > 0.05 or abs(drift_end) > 0.05:
                issue(issues, WARN, f'visual_timing/{lang}/{sc["id"]}/scene_bounds',
                      f'Mốc cảnh lệch so với audio thật: start {drift_start:+.3f}s, end {drift_end:+.3f}s')
            beats = []
            prev_abs = None
            for bt in sc.get('images', []):
                abs_t = sc['start'] + bt['at']
                beat_row = {'beat_id': bt['id'], 'image_id': None, 'src': bt['src'],
                            'relative_at': bt['at'], 'absolute_time': round(abs_t, 4), 'effect': bt.get('effect')}
                if abs_t < sc['start'] - 1e-6 or abs_t > sc['end'] + 1e-6:
                    issue(issues, FAIL, f'visual_timing/{lang}/{sc["id"]}/{bt["id"]}',
                          f'Nhịp {bt["id"]} rơi ngoài khoảng cảnh thật [{sc["start"]:.3f}, {sc["end"]:.3f}]: t={abs_t:.3f}')
                if prev_abs is not None and abs_t - prev_abs < 1 / 30:
                    issue(issues, WARN, f'visual_timing/{lang}/{sc["id"]}/{bt["id"]}',
                          f'Nhịp {bt["id"]} cách nhịp trước dưới 1 khung hình (30fps): {abs_t - prev_abs:.4f}s')
                prev_abs = abs_t
                beats.append(beat_row)
            row['beats'] = beats
            lang_out.append(row)
        out['languages'][lang] = lang_out
    return out


def extract_beat_frames(jdir, out_dir, timing, render_env, content, brief, issues, frame_limit=None):
    if not render_env:
        issue(issues, UNSUPPORTED, 'frames', 'Chưa có render, không trích được khung hình theo nhịp')
        return {'status': UNSUPPORTED, 'frames': []}
    payload = render_env['payload']
    ratio = brief.get('aspect_ratio', '9:16') if brief else '9:16'
    video_for_lang = {}
    if ratio == 'dual':
        video_for_lang = {'vi': payload.get('video_9x16'), 'en': payload.get('video_16x9')}
    elif ratio == '16:9':
        video_for_lang = {'en': payload.get('video')}
    else:
        video_for_lang = {'vi': payload.get('video')}
    frames_dir = Path(out_dir) / 'frames'
    frames = []
    count = 0
    images_by_id = {}
    if content and content.get('schema_version') == '3.0':
        for sc in content['scenes']:
            for im in sc.get('images', []):
                images_by_id[im['id']] = im
    for lang, scenes in timing.items():
        video_rel = video_for_lang.get(lang)
        if not video_rel:
            issue(issues, UNSUPPORTED, f'frames/{lang}', f'Không có file video cho ngôn ngữ {lang} (tỷ lệ job={ratio})')
            continue
        video_path = jdir / video_rel
        for sc in scenes:
            for bt in sc.get('images', []):
                if frame_limit and count >= frame_limit:
                    issue(issues, WARN, 'frames/limit', f'Đã đạt giới hạn {frame_limit} khung hình; dừng trích thêm')
                    break
                abs_t = sc['start'] + bt['at']
                image_id = None
                # bt['src'] is a copied public/ filename, not the original image_id;
                # resolve image_id from content beats by matching beat id.
                for beat in (im for s2 in (content['scenes'] if content else []) if s2['id'] == sc['id'] for im in s2.get('beats', [])):
                    if beat['id'] == bt['id']:
                        image_id = beat['image_id']
                        break
                name = f"{lang}_{sc['id']}_{image_id or 'unknown'}_{bt['id']}_t{round(abs_t * 1000)}ms.png"
                dest = frames_dir / name
                success, err = extract_frame(video_path, abs_t, dest)
                row = {'lang': lang, 'scene_id': sc['id'], 'beat_id': bt['id'], 'image_id': image_id,
                       'time_seconds': round(abs_t, 4), 'video': video_rel,
                       'frame_path': str(dest.relative_to(out_dir)) if success else None,
                       'status': OK if success else FAIL, 'error': err}
                if not success:
                    issue(issues, FAIL, f'frames/{lang}/{sc["id"]}/{bt["id"]}', f'Trích khung hình thất bại: {err}')
                frames.append(row)
                count += 1
            if frame_limit and count >= frame_limit:
                break
    return {'status': OK if frames else UNSUPPORTED, 'frames': frames}


def check_layout_16x9(jdir, out_dir, render_env, brief, issues):
    if not render_env:
        issue(issues, UNSUPPORTED, 'layout_16x9', 'Chưa có render')
        return {'status': UNSUPPORTED}
    payload = render_env['payload']
    layout_rel = payload.get('layout_report')
    if not layout_rel or not (jdir / layout_rel).is_file():
        issue(issues, UNSUPPORTED, 'layout_16x9', 'Không có layout.json')
        return {'status': UNSUPPORTED}
    layout = load_json(jdir / layout_rel)
    ratio = brief.get('aspect_ratio', '9:16') if brief else '9:16'
    out = {'layout_json': layout, 'job_aspect_ratio': ratio}
    if ratio == '16:9':
        if layout.get('applies') is not False:
            issue(issues, FAIL, 'layout_16x9/applies',
                  f"Job tỷ lệ 16:9 nhưng layout.json applies={layout.get('applies')!r} (kỳ vọng false)")
        else:
            issue(issues, OK, 'layout_16x9/applies', 'layout.json applies=false đúng như kỳ vọng cho job 16:9')
    elif ratio == 'dual':
        issue(issues, WARN, 'layout_16x9/dual_caveat',
              "Job dual: layout.json.applies=" + repr(layout.get('applies')) +
              " phản ánh kiểm tra cue của BẢN 9:16, không phải bằng chứng bản 16:9 (video_16x9.mp4) ẩn phụ đề. "
              "Chỉ khung hình trích từ video_16x9.mp4 mới là bằng chứng cho bản 16:9.")
    else:
        issue(issues, UNSUPPORTED, 'layout_16x9', f'Job tỷ lệ {ratio}; mục này chỉ áp dụng cho 16:9/dual')

    video_16x9_rel = payload.get('video_16x9') or (payload.get('video') if ratio == '16:9' else None)
    if not video_16x9_rel:
        issue(issues, UNSUPPORTED, 'layout_16x9/frame', 'Không có file video 16:9 để trích khung hình')
        out['frame'] = None
        return {**out, 'status': OK}
    video_path = jdir / video_16x9_rel
    probe = ffprobe_json(video_path)
    dur = format_duration(probe) or 1.0
    dest = Path(out_dir) / 'frames' / '16x9_no_subtitle_proof.png'
    success, err = extract_frame(video_path, dur / 2, dest)
    if success:
        out['frame'] = str(dest.relative_to(out_dir))
        issue(issues, OK, 'layout_16x9/frame', f'Đã trích khung hình giữa video 16:9 tại {video_16x9_rel}; xem ảnh để tự xác nhận không có phụ đề')
    else:
        out['frame'] = None
        issue(issues, FAIL, 'layout_16x9/frame', f'Không trích được khung hình 16:9: {err}')
    return {**out, 'status': OK}


def check_loudness(jdir, cfg, audio_env, render_env, issues):
    if not audio_env:
        issue(issues, UNSUPPORTED, 'loudness', 'Chưa có audio')
        return {'status': UNSUPPORTED}
    audio = audio_env['payload']
    target_lufs = cfg.get('audio_lufs')
    target_peak = cfg.get('audio_peak_db')
    out = {'target_lufs': target_lufs, 'target_peak_db': target_peak, 'tracks': {}}
    if target_lufs is None or target_peak is None:
        issue(issues, UNSUPPORTED, 'loudness/config', 'config.json thiếu audio_lufs/audio_peak_db')
        return {'status': UNSUPPORTED, **out}

    def measure_and_report(label, path):
        if not path:
            return None
        m, err = measure_loudness(jdir / path)
        if not m:
            issue(issues, UNSUPPORTED, f'loudness/{label}', f'Không đo được LUFS: {err}')
            return None
        lufs_delta = m['input_i'] - target_lufs
        peak_delta = m['input_tp'] - target_peak
        status = OK if abs(lufs_delta) <= 1.0 and peak_delta <= 0.3 else (WARN if abs(lufs_delta) <= 2.0 and peak_delta <= 1.0 else FAIL)
        issue(issues, status, f'loudness/{label}',
              f'{label}: đo {m["input_i"]:.2f} LUFS (mục tiêu {target_lufs}, lệch {lufs_delta:+.2f}), '
              f'true peak {m["input_tp"]:.2f} dB (trần {target_peak}, lệch {peak_delta:+.2f})')
        return {'measured': m, 'lufs_delta': round(lufs_delta, 3), 'peak_delta': round(peak_delta, 3), 'path': path}

    out['tracks']['vi_wav'] = measure_and_report('vi_wav (nguồn)', audio.get('wav'))
    if audio.get('en'):
        out['tracks']['en_wav'] = measure_and_report('en_wav (nguồn)', audio['en'].get('wav'))
    if render_env:
        payload = render_env['payload']
        for label, key in [('mp4_main', 'video'), ('mp4_9x16', 'video_9x16'), ('mp4_16x9', 'video_16x9')]:
            if payload.get(key):
                out['tracks'][label] = measure_and_report(f'{label} (đã qua AAC)', payload[key])
    out['status'] = OK
    return out


def check_stage_timing(root, job, issues):
    events, err = read_events(root, job)
    if events is None:
        issue(issues, UNSUPPORTED, 'stage_timing', err)
        return {'status': UNSUPPORTED, 'reason': err}
    pending = {}
    runs = []
    for row in events:
        m, e, detail = row['module'], row['event'], row['detail']
        if e == 'started':
            pending.setdefault(m, {})[detail] = row['at']
        elif e in ('awaiting_review', 'blocked') and detail in pending.get(m, {}):
            started_at = pending[m].pop(detail)
            elapsed = row['at'] - started_at
            timeout = STAGE_TIMEOUT_S.get(m)
            runs.append({'module': m, 'revision': detail, 'outcome': e, 'elapsed_seconds': round(elapsed, 2),
                         'timeout_ceiling_seconds': timeout,
                         'pct_of_timeout': round(100 * elapsed / timeout, 1) if timeout else None})
    if not runs:
        issue(issues, UNSUPPORTED, 'stage_timing', 'Không tìm được cặp sự kiện started/awaiting_review|blocked trong events')
        return {'status': UNSUPPORTED}
    for r in runs:
        if r['outcome'] == 'blocked':
            issue(issues, FAIL, f"stage_timing/{r['module']}/rev{r['revision']}",
                  f"{r['module']} rev {r['revision']} thất bại sau {r['elapsed_seconds']}s")
        elif r['pct_of_timeout'] is not None and r['pct_of_timeout'] >= 50:
            issue(issues, WARN, f"stage_timing/{r['module']}/rev{r['revision']}",
                  f"{r['module']} rev {r['revision']} chạy {r['elapsed_seconds']}s = {r['pct_of_timeout']}% giới hạn timeout {r['timeout_ceiling_seconds']}s")
    slowest = max(runs, key=lambda r: r['elapsed_seconds'])
    issue(issues, OK if slowest['outcome'] != 'blocked' else FAIL, 'stage_timing/slowest',
          f"Khâu chậm nhất: {slowest['module']} rev {slowest['revision']} = {slowest['elapsed_seconds']}s")
    return {'status': OK, 'runs': runs, 'slowest': slowest}


# ---------- report assembly ----------

def rehearse_report(root, job, out_dir, extract_frames=True, frame_limit=None):
    root = Path(root).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'frames').mkdir(exist_ok=True)
    jdir = job_dir(root, job)
    issues = []
    if not jdir.is_dir():
        raise SystemExit(f'Job không tồn tại: {jdir}')

    cfg = load_json(root / 'config.json') if (root / 'config.json').is_file() else {}
    brief_rev, brief = read_brief(jdir)
    content_rev, content_env, content_blocked = latest_module_revision(jdir, 'content')
    audio_rev, audio_env, audio_blocked = latest_module_revision(jdir, 'audio')
    images_rev, images_env, images_blocked = latest_module_revision(jdir, 'images')
    render_rev, render_env, render_blocked = latest_module_revision(jdir, 'render')
    content = content_env['payload'] if content_env else None

    report = {
        'schema_version': '1.0',
        'generated_at': time.time(),
        'root': str(root),
        'job': job,
        'brief': {'revision': brief_rev, 'aspect_ratio': brief.get('aspect_ratio') if brief else None,
                  'duration_window': brief.get('duration') if brief else None} if brief else None,
        'module_revisions': {
            'content': {'revision': content_rev, 'blocked_revisions': content_blocked},
            'audio': {'revision': audio_rev, 'blocked_revisions': audio_blocked},
            'images': {'revision': images_rev, 'blocked_revisions': images_blocked},
            'render': {'revision': render_rev, 'blocked_revisions': render_blocked},
        },
        'checks': {},
        'issues': [],
    }

    if not brief:
        issue(issues, UNSUPPORTED, 'brief', 'Không có brief-current.json / briefs/<rev>.json đọc được; dùng ngưỡng mặc định 45-60s cho các kiểm tra thời lượng')

    report['checks']['duration'] = check_durations(jdir, brief, content, audio_env, render_env, issues)
    report['checks']['av_sync'] = check_av_sync(jdir, render_env, issues)
    report['checks']['subtitles'] = check_subtitles(jdir, audio_env, render_env, issues)
    vt_rev, timing = find_visual_timing(jdir)
    report['checks']['visual_timing'] = check_visual_timing(jdir, content, audio_env, issues)
    if extract_frames and timing:
        report['checks']['frames'] = extract_beat_frames(jdir, out_dir, timing, render_env, content, brief, issues, frame_limit)
    else:
        reason = 'Bỏ qua trích khung hình (--no-frames)' if not extract_frames else 'Không có visual-timing.json nên không biết mốc nhịp'
        issue(issues, UNSUPPORTED, 'frames', reason)
        report['checks']['frames'] = {'status': UNSUPPORTED, 'frames': []}
    report['checks']['layout_16x9'] = check_layout_16x9(jdir, out_dir, render_env, brief, issues)
    report['checks']['loudness'] = check_loudness(jdir, cfg, audio_env, render_env, issues)
    report['checks']['stage_timing'] = check_stage_timing(root, job, issues)

    report['issues'] = issues
    write_json_report(report, out_dir / 'report.json')
    write_markdown_report(report, out_dir / 'report.md')
    return report


def write_json_report(report, path):
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2))


def write_markdown_report(report, path):
    sev_order = {FAIL: 0, WARN: 1, UNSUPPORTED: 2, OK: 3}
    issues = sorted(report['issues'], key=lambda x: sev_order.get(x['status'], 9))
    bad = [x for x in issues if x['status'] != OK]
    good = [x for x in issues if x['status'] == OK]

    def label(status):
        return {FAIL: 'SAI', WARN: 'ĐÁNG NGỜ', UNSUPPORTED: 'KHÔNG ĐO ĐƯỢC', OK: 'ĐẠT'}[status]

    lines = [f"# Báo cáo diễn tập — job `{report['job']}`", '',
             f"Sinh lúc: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report['generated_at']))}",
             f"Root: `{report['root']}`", '']
    n_fail = sum(1 for x in issues if x['status'] == FAIL)
    n_warn = sum(1 for x in issues if x['status'] == WARN)
    n_unsup = sum(1 for x in issues if x['status'] == UNSUPPORTED)
    lines += [f"**{n_fail} SAI · {n_warn} ĐÁNG NGỜ · {n_unsup} KHÔNG ĐO ĐƯỢC · {len(good)} ĐẠT**", '']

    lines.append('## SAI hoặc ĐÁNG NGỜ hoặc KHÔNG ĐO ĐƯỢC (đọc trước)')
    lines.append('')
    if not bad:
        lines.append('Không có mục nào trong nhóm này.')
    else:
        for x in bad:
            lines.append(f"- **[{label(x['status'])}] {x['check']}** — {x['detail']}")
    lines.append('')
    lines.append('## Đạt')
    lines.append('')
    if not good:
        lines.append('(không có)')
    else:
        for x in good:
            lines.append(f"- [{label(x['status'])}] {x['check']} — {x['detail']}")
    lines.append('')

    lines.append('## Số liệu thô theo mục')
    lines.append('')
    checks = report['checks']
    if report.get('brief'):
        lines.append(f"Brief: tỷ lệ={report['brief']['aspect_ratio']}, khoảng thời lượng={report['brief']['duration_window']}")
    else:
        lines.append('Brief: không đọc được; dùng ngưỡng mặc định 45–60s.')
    lines.append('')

    d = checks.get('duration', {})
    if d.get('status') == OK:
        lines.append('### 1. Thời lượng')
        for lang in ['vi', 'en']:
            if lang in d:
                t = d[lang]
                lines.append(f"- {lang}: tổng cảnh đo được = {t['measured_scene_sum']}s; audio master đo được = {t['master_measured_duration']}s; "
                              f"audio master ghi trong payload = {t['master_recorded_duration']}s")
        if 'video_duration' in d:
            lines.append(f"- mp4 chính đo được = {d['video_duration']}s")
        for k in ('video_9x16_duration', 'video_16x9_duration'):
            if k in d:
                lines.append(f"- {k} = {d[k]}s")
        lines.append(f"- Cửa sổ brief: {d.get('brief_window')}")
        lines.append('')

    sync = checks.get('av_sync', {})
    if sync.get('status') == OK:
        lines.append('### 2. Lệch tiếng-hình (theo luồng bên trong mp4)')
        for label_, row in sync.get('files', {}).items():
            lines.append(f"- {label_} ({row['path']}): video={row['video_stream_duration']}s, audio={row['audio_stream_duration']}s, lệch={row['delta']:+.4f}s")
        lines.append('')

    sub = checks.get('subtitles', {})
    if sub.get('status') == OK:
        lines.append('### 4. Phụ đề (.srt vs props.cues)')
        lines.append(f"- .srt: {sub['srt_cue_count']} cue; props.cues: {sub['props_cue_count']} cue; lệch nội dung/thời gian: {len(sub.get('mismatches', []))}")
        for m in sub.get('mismatches', [])[:20]:
            lines.append(f"  - cue #{m['index']}: srt=({m['srt_start']}, {m['srt_end']}, {m['srt_text']!r}) "
                          f"props=({m['props_start']}, {m['props_end']}, {m['props_text']!r})")
        lines.append('')

    vt = checks.get('visual_timing', {})
    if vt.get('status') == OK:
        lines.append('### 5. visual-timing.json đối chiếu mốc âm thanh thật')
        for lang, scenes in vt.get('languages', {}).items():
            lines.append(f"- Ngôn ngữ {lang}:")
            for sc in scenes:
                lines.append(f"  - {sc['scene_id']}: lệch cảnh start={sc.get('start_drift')}s end={sc.get('end_drift')}s; "
                              f"{len(sc.get('beats', []))} nhịp")
        lines.append('')

    fr = checks.get('frames', {})
    if fr.get('status') == OK:
        lines.append('### 3. Khung hình trích theo nhịp')
        lines.append(f"- Tổng số khung hình đã trích: {len(fr['frames'])} (xem thư mục frames/)")
        lines.append('')

    lo = checks.get('layout_16x9', {})
    if lo.get('status') == OK:
        lines.append('### 6. Layout 16:9')
        lines.append(f"- layout.json: {json.dumps(lo.get('layout_json'), ensure_ascii=False)}")
        if lo.get('frame'):
            lines.append(f"- Khung hình chứng minh: {lo['frame']}")
        lines.append('')

    ld = checks.get('loudness', {})
    if ld.get('status') == OK:
        lines.append('### 7. Mức âm lượng (LUFS / true peak)')
        lines.append(f"- Mục tiêu: {ld.get('target_lufs')} LUFS, đỉnh {ld.get('target_peak_db')} dB")
        for label_, row in ld.get('tracks', {}).items():
            if row:
                lines.append(f"  - {label_}: {row['measured']['input_i']:.2f} LUFS (lệch {row['lufs_delta']:+.2f}), "
                              f"true peak {row['measured']['input_tp']:.2f} dB (lệch {row['peak_delta']:+.2f})")
        lines.append('')

    st = checks.get('stage_timing', {})
    if st.get('status') == OK:
        lines.append('### 8. Thời gian từng công đoạn')
        for r in sorted(st.get('runs', []), key=lambda r: -r['elapsed_seconds']):
            pct = f", {r['pct_of_timeout']}% timeout {r['timeout_ceiling_seconds']}s" if r['pct_of_timeout'] is not None else ''
            lines.append(f"- {r['module']} rev {r['revision']} ({r['outcome']}): {r['elapsed_seconds']}s{pct}")
        lines.append('')

    path.write_text('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description='Đo và soi kết quả một lần diễn tập toàn tuyến Video Pilot.')
    ap.add_argument('--root', required=True, help='Sandbox root chứa runs/, config.json, .state/')
    ap.add_argument('--job', required=True, help='Job id trong runs/<job>')
    ap.add_argument('--out', required=True, help='Thư mục ghi report.md, report.json, frames/')
    ap.add_argument('--no-frames', action='store_true', help='Bỏ qua trích khung hình theo nhịp (nhanh hơn)')
    ap.add_argument('--frame-limit', type=int, default=None, help='Giới hạn số khung hình trích tối đa')
    args = ap.parse_args()
    report = rehearse_report(args.root, args.job, args.out, extract_frames=not args.no_frames, frame_limit=args.frame_limit)
    n_fail = sum(1 for x in report['issues'] if x['status'] == FAIL)
    n_warn = sum(1 for x in report['issues'] if x['status'] == WARN)
    n_unsup = sum(1 for x in report['issues'] if x['status'] == UNSUPPORTED)
    print(json.dumps({'report_md': str(Path(args.out) / 'report.md'), 'report_json': str(Path(args.out) / 'report.json'),
                       'fail': n_fail, 'warn': n_warn, 'unsupported': n_unsup}, ensure_ascii=False, indent=2))
    if n_fail:
        sys.exit(2)


if __name__ == '__main__':
    main()
