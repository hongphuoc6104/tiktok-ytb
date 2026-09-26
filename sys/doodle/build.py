"""Build a finished long-form video from a self-written doodle script, end to end on this
machine: local VieNeu TTS → mastered WAV + subtitle cues → doodle images → Remotion 16:9
render → thumbnail/metadata/description. No AI image/video service, no reviewer.

Usage (from sys/): .venv/bin/python -m doodle.build doodle.scripts.ngay_tien_su OUTNAME
"""
import importlib
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYS))
import adapters  # noqa: E402  (reuse pipeline helpers: pauses, mastering, cues)
import video_packaging  # noqa: E402
from doodle.draw import render as draw  # noqa: E402


def tts(script, work):
    cfg = json.loads((SYS / 'config.json').read_text())
    g = cfg.get('tts_pause', adapters.DEFAULT_PAUSE)
    scenes = []
    for k, sc in enumerate(script.SCENES):
        texts = [t for t, _ in sc['lines']]
        scenes.append({'scene_id': sc['id'], 'narration': ' '.join(texts), 'texts': texts, 'retake': 0,
                       'gaps': [adapters.gap_after(t, g) for t in texts[:-1]],
                       'tail': g.get('tail', .35) if k == len(script.SCENES) - 1 else g.get('para', .7)})
    keys = ('tts_voice', 'tts_temperature', 'tts_top_p', 'tts_max_chars', 'tts_scene_synthesis', 'tts_backend', 'tts_precision',
            'tts_speed', 'tts_device', 'tts_gpu_dtype', 'tts_batch_size')
    out = work / 'audio'
    out.mkdir(parents=True, exist_ok=True)
    req = out / 'request.json'
    req.write_text(json.dumps({'settings': {k: cfg[k] for k in keys if k in cfg}, 'cache_dir': str(work / 'tts-cache'),
                               'scenes': scenes}, ensure_ascii=False))
    py = adapters.tts_python(SYS, cfg)
    r = subprocess.run([str(py), str(SYS / 'tts_worker.py'), str(req), str(out)], capture_output=True, text=True, timeout=7200)
    (out / 'tts.log').write_text(r.stdout + '\n' + r.stderr)
    if r.returncode:
        raise SystemExit('TTS failed, see ' + str(out / 'tts.log'))
    meta = json.loads((out / 'tts-result.json').read_text())
    segs, frames, cursor, params = [], [], 0.0, None
    for x in meta['segments']:
        with wave.open(str(out / x['path'])) as w:
            params = params or (w.getnchannels(), w.getsampwidth(), w.getframerate())
            d = w.getnframes() / w.getframerate()
            frames.append(w.readframes(w.getnframes()))
        segs.append({'scene_id': x['scene_id'], 'text': x['text'], 'start': cursor, 'end': cursor + d,
                     'content_end': cursor + x.get('content_duration', d)})
        cursor += d
    raw = out / 'narration.wav'
    with wave.open(str(raw), 'wb') as w:
        w.setnchannels(params[0]); w.setsampwidth(params[1]); w.setframerate(params[2]); w.writeframes(b''.join(frames))
    adapters.master(raw, out / 'narration_eq.wav', cfg)  # masters raw in place (as the pipeline does)
    return {'wav': out / 'narration.wav', 'segments': segs, 'duration': cursor}


def build(module, name):
    script = importlib.import_module(module)
    work = SYS / 'scratch' / 'doodle-build' / name
    public = work / 'public'
    public.mkdir(parents=True, exist_ok=True)
    audio = tts(script, work)
    shutil.copy(audio['wav'], public / 'narration.wav')
    # images: one render per scene key actually used
    used = {b[0] for sc in script.SCENES for _, b in sc['lines'] if b}
    for i, key in enumerate(sorted(used)):
        draw(script.IMAGES[key], public / f'{key}.png', seed=i + 7)
    # timeline: each line maps to its own TTS segment (same order)
    segs = audio['segments']
    lines = [(sc['id'], b) for sc in script.SCENES for _, b in sc['lines']]
    assert len(lines) == len(segs), (len(lines), len(segs))
    scenes, i = [], 0
    for sc in script.SCENES:
        n = len(sc['lines'])
        s0 = segs[i]['start']
        s1 = segs[i + n]['start'] if i + n < len(segs) else audio['duration']
        beats, last = [], None
        for k in range(n):
            b = lines[i + k][1]
            if b:
                last = b
                beats.append({'src': f'{b[0]}.png', 'at': round(segs[i + k]['start'] - s0, 3), 'effect': b[1],
                              'focus': {'x': .5, 'y': .45}, 'overlays': b[2]})
        if not beats:
            raise SystemExit(f'{sc["id"]} has no image')
        scenes.append({'id': sc['id'], 'title': sc['chapter'], 'start': round(s0, 3), 'end': round(s1, 3),
                       'image': beats[0]['src'], 'images': beats})
        i += n
    cfg = json.loads((SYS / 'config.json').read_text())
    props = {'duration': audio['duration'], 'scenes': scenes, 'segments': segs, 'cues': adapters.subtitle_cues(segs),
             'aspect_ratio': '16:9', 'voice_language': 'vi', 'subtitles': getattr(script, 'BURN_SUBTITLES', False),
             'render_concurrency': cfg.get('render_concurrency', 6)}
    (work / 'props.json').write_text(json.dumps(props, ensure_ascii=False))
    r = subprocess.run(['node', str(SYS / 'renderer' / 'render.mjs'), str(work)], cwd=str(SYS), capture_output=True, text=True)
    (work / 'render.log').write_text(r.stdout + '\n' + r.stderr)
    if r.returncode or not (work / 'video.mp4').exists():
        raise SystemExit('render failed, see ' + str(work / 'render.log'))
    # deliverables
    dest = SYS.parent / 'video' / name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(work / 'video.mp4', dest / f'{name}.mp4')
    (dest / f'{name}.vi.srt').write_text(adapters.make_srt(segs))  # upload as YouTube captions
    video_packaging.write_thumbnails(public / f'{script.THUMB["image"]}.png', script.THUMB['text'], dest)
    content = {'scenes': [{'id': sc['id'], 'chapter': sc['chapter']} for sc in script.SCENES]}
    chapters = video_packaging.build_chapters(content, {'segments': segs})
    desc = video_packaging.build_description(script.HOOK, chapters, [])
    desc = '\n'.join(l for l in desc.splitlines() if 'AI' not in l and 'Nguồn tham khảo' not in l and 'chưa khai báo nguồn' not in l).rstrip()
    desc += '\n\nHình minh họa vẽ tay kiểu doodle; các con số là ước lượng từ nghiên cứu khảo cổ và nhân học, còn nhiều tranh luận.\n'
    (dest / 'description.txt').write_text(desc)
    meta = video_packaging.build_metadata({'titles': script.TITLES, 'tags': script.TAGS, 'hook': script.HOOK},
                                          chapters, [], audio['duration'], desc)
    (dest / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps({'video': str(dest / f'{name}.mp4'), 'duration': round(audio['duration'], 1), 'scenes': len(scenes),
                      'beats': sum(len(s['images']) for s in scenes), 'images': len(used)}, ensure_ascii=False))


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
