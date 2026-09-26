"""Build the AI-illustrated variants of a Mơ script from one shared narration.

  python3 -m doodle.build_ai tts    SCRIPT_MODULE WORK            # narration (local VieNeu) -> WORK/audio.json
  python3 -m doodle.build_ai render SCRIPT_MODULE WORK images NAME  # stills: every shot, 1–2 per line (+ reaction inserts)
  python3 -m doodle.build_ai render SCRIPT_MODULE WORK clips NAME   # Flow clips where available (shot id .mp4), stills otherwise

Images come from doodle.aigen manifests (IMG_DIR), clips from CLIP_DIR/<shot>.mp4.
"""
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYS))
import adapters  # noqa: E402
import video_packaging  # noqa: E402
from doodle.build import tts as run_tts  # noqa: E402

IMG_DIR = SYS / 'scratch' / 'ai' / 'mo'
CLIP_DIR = SYS / 'scratch' / 'ai' / 'clips'


def stage_tts(script, work):
    work.mkdir(parents=True, exist_ok=True)
    a = run_tts(script, work)
    (work / 'audio.json').write_text(json.dumps({'wav': str(a['wav']), 'segments': a['segments'], 'duration': a['duration']}, ensure_ascii=False))
    print(json.dumps({'duration': round(a['duration'], 1), 'segments': len(a['segments'])}))


def clip_info(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def plan(script, audio, mode):
    """Beats per scene. Stills: each line's shots split its time evenly; a reaction insert
    (script.REACT[shot_id]) takes the last 40% of that shot. Clips: a shot's clip covers its span,
    slowed down to at most 25% (rate .8) when the span is longer, looped beyond that."""
    manifest = json.loads((IMG_DIR / 'manifest.json').read_text())
    react = getattr(script, 'REACT', {})
    reuse = getattr(script, 'REUSE', {})
    segs = audio['segments']
    lines = [(sc['id'], text, shots) for sc in script.SCENES for text, shots in sc['lines']]
    assert len(lines) == len(segs), (len(lines), len(segs))
    used, scenes, i = {}, [], 0
    for sc in script.SCENES:
        n = len(sc['lines'])
        s0 = segs[i]['start']
        s1 = segs[i + n]['start'] if i + n < len(segs) else audio['duration']
        beats = []
        for k in range(n):
            _, _, shots = lines[i + k]
            a = segs[i + k]['start']
            b = segs[i + k + 1]['start'] if i + k + 1 < len(segs) else audio['duration']
            step = (b - a) / len(shots)
            for j, shot in enumerate(shots):
                sid, _, effect, overlays = shot[:4]
                t0 = a + j * step
                clip = CLIP_DIR / f'{sid}.mp4'
                if mode == 'clips' and clip.exists():
                    d = clip_info(clip)
                    beats.append({'src': f'{sid}.mp4', 'kind': 'clip', 'clip_seconds': round(d, 3), 'rate': round(max(.8, min(1, d / step)), 3),
                                  'at': round(t0 - s0, 3), 'effect': 'cut' if j or k else 'fade', 'focus': {'x': .5, 'y': .5}, 'overlays': overlays})
                    used[f'{sid}.mp4'] = clip
                    continue
                img = sid if sid in manifest else reuse.get(sid)
                if img not in manifest:
                    raise SystemExit(f'missing image {sid}')
                src = f'{img}{Path(manifest[img]["path"]).suffix}'
                used[src] = Path(manifest[img]['path'])
                beats.append({'src': src, 'at': round(t0 - s0, 3), 'effect': effect, 'focus': {'x': .5, 'y': .45}, 'overlays': overlays})
                if mode == 'images' and sid in react and react[sid] in manifest and step > 3.2:
                    rid = react[sid]
                    rsrc = f'{rid}{Path(manifest[rid]["path"]).suffix}'
                    used[rsrc] = Path(manifest[rid]['path'])
                    beats.append({'src': rsrc, 'at': round(t0 + step * .6 - s0, 3), 'effect': 'pop', 'focus': {'x': .5, 'y': .45}, 'overlays': []})
        scenes.append({'id': sc['id'], 'title': sc['chapter'], 'start': round(s0, 3), 'end': round(s1, 3), 'image': beats[0]['src'], 'images': beats})
        i += n
    return scenes, used


def stage_render(script, work, mode, name):
    audio = json.loads((work / 'audio.json').read_text())
    out = work / mode
    public = out / 'public'
    if public.exists():
        shutil.rmtree(public)
    public.mkdir(parents=True)
    shutil.copy(audio['wav'], public / 'narration.wav')
    scenes, used = plan(script, audio, mode)
    for dst, src in used.items():
        shutil.copy(src, public / dst)
    cfg = json.loads((SYS / 'config.json').read_text())
    segs = audio['segments']
    props = {'duration': audio['duration'], 'scenes': scenes, 'segments': segs, 'cues': adapters.subtitle_cues(segs),
             'aspect_ratio': '16:9', 'voice_language': 'vi', 'subtitles': False, 'render_concurrency': cfg.get('render_concurrency', 6)}
    (out / 'props.json').write_text(json.dumps(props, ensure_ascii=False))
    r = subprocess.run(['node', str(SYS / 'renderer' / 'render.mjs'), str(out)], cwd=str(SYS), capture_output=True, text=True)
    (out / 'render.log').write_text(r.stdout + '\n' + r.stderr)
    if r.returncode or not (out / 'video.mp4').exists():
        raise SystemExit('render failed, see ' + str(out / 'render.log'))
    dest = SYS.parent / 'video' / name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(out / 'video.mp4', dest / f'{name}.mp4')
    (dest / f'{name}.vi.srt').write_text(adapters.make_srt(segs))
    manifest = json.loads((IMG_DIR / 'manifest.json').read_text())
    video_packaging.write_thumbnails(Path(manifest[script.THUMB['shot']]['path']), script.THUMB['text'], dest)
    content = {'scenes': [{'id': sc['id'], 'chapter': sc['chapter']} for sc in script.SCENES]}
    chapters = video_packaging.build_chapters(content, {'segments': segs})
    desc = video_packaging.build_description(script.HOOK, chapters, [])
    desc = '\n'.join(l for l in desc.splitlines() if 'Nguồn tham khảo' not in l and 'chưa khai báo nguồn' not in l).rstrip()
    how = 'Hình minh họa tạo bằng AI (Google Flow)' + (', chuyển động bằng Omni Flash' if mode == 'clips' else '')
    desc += f'\n\n{how}; nhân vật Mơ là nhân vật hư cấu. Các con số là ước lượng từ nghiên cứu khảo cổ và nhân học, còn nhiều tranh luận.\n'
    (dest / 'description.txt').write_text(desc)
    meta = video_packaging.build_metadata({'titles': script.TITLES, 'tags': script.TAGS, 'hook': script.HOOK}, chapters, [], audio['duration'], desc)
    (dest / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    n_clip = sum(1 for s in scenes for b in s['images'] if b.get('kind') == 'clip')
    print(json.dumps({'video': str(dest / f'{name}.mp4'), 'duration': round(audio['duration'], 1),
                      'beats': sum(len(s['images']) for s in scenes), 'clips': n_clip}, ensure_ascii=False))


if __name__ == '__main__':
    stage, module, work = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
    script = importlib.import_module(module)
    if stage == 'tts':
        stage_tts(script, work)
    else:
        stage_render(script, work, sys.argv[4], sys.argv[5])
