#!/usr/bin/env python3
"""Synthetic long-form 16:9 render benchmark (offline; no Flow, no TTS).

Builds props.json + public/ like adapters.render does -- placeholder doodle
PNGs, a few short MP4 clips, a sine narration WAV, Vietnamese cues and
overlays on every effect -- then runs renderer/render.mjs and prints render
seconds per video second (render-timing.json).

  sys/.venv/bin/python sys/scripts/render_benchmark.py OUT --seconds 600
"""
import argparse
import json
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.subtitles import subtitle_cues  # noqa: E402

EFFECTS = ['hold', 'cut', 'fade', 'slide_left', 'zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pop']
LINES = ['Năm mươi nghìn năm trước, bạn sẽ thức dậy trong một hang đá lạnh ngắt.',
         'Việc đầu tiên không phải là ăn sáng, mà là giữ cho đống lửa còn cháy.',
         'Người săn bắt hái lượm biết rõ từng loại quả mọc quanh nơi họ sống.',
         'Mưa kéo dài cả tuần nghĩa là củi ướt, thức ăn khan hiếm và bệnh tật.',
         'Các nhà khảo cổ tìm thấy dấu vết bếp lửa ở rất nhiều hang động châu Âu.']


def images(public, scenes, per_scene, clips, width, height):
    from PIL import Image, ImageDraw
    rnd = random.Random(7)
    names = {}
    for s in range(scenes):
        for k in range(per_scene):
            im = Image.new('RGB', (width, height), (250, 244, 228))
            d = ImageDraw.Draw(im)
            for _ in range(14):
                x, y = rnd.randrange(width), rnd.randrange(height)
                r = rnd.randrange(40, 260)
                d.ellipse([x - r, y - r, x + r, y + r], outline=(30, 30, 30), width=6)
            d.line([(width * .45, height * .3), (width * .5, height * .7)], fill=(20, 20, 20), width=10)
            d.ellipse([width * .43, height * .18, width * .52, height * .32], outline=(20, 20, 20), width=10)
            name = f'{s}-{k}.png'
            im.save(public / name, optimize=False, compress_level=1)
            names[(s, k)] = name
    for c in range(clips):
        name = f'clip-{c}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'testsrc2=size={width}x{height}:rate=24',
                        '-t', str(3 + 4 * c), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-an', str(public / name)], check=True)
    return names


def build(out, seconds, scenes, beat_seconds, concurrency, preset, clips, gl=None):
    public = out / 'public'; public.mkdir(parents=True, exist_ok=True)
    width, height = 1920, 1080
    per_scene = 6
    names = images(public, scenes, per_scene, clips, width, height)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=180:sample_rate=24000',
                    '-t', str(seconds), '-ac', '1', str(public / 'narration.wav')], check=True)
    scene_len = seconds / scenes
    props_scenes, segments = [], []
    n = 0
    for s in range(scenes):
        start = s * scene_len
        beats = []
        at = 0.
        while at < scene_len - 1:
            src = names[(s, len(beats) % per_scene)]
            if len(beats) == 0 and clips: src = f'clip-{s % clips}.mp4'
            beat = {'id': f'B{n:03}', 'src': src, 'at': round(at, 3), 'effect': EFFECTS[n % len(EFFECTS)],
                    'focus': {'x': .5, 'y': .45}}
            ovs = []
            if len(beats) == 0: ovs.append({'type': 'chapter_title', 'text': f'Chương {s + 1}: Lửa và hang đá', 'x': .5, 'y': .2, 'at': 0})
            kind = n % 4
            if kind == 1: ovs.append({'type': 'label', 'text': 'Đá lửa (flint)', 'x': .3, 'y': .7, 'at': .4})
            if kind == 2: ovs.append({'type': 'counter', 'text': 'năm trước', 'to': 50000, 'x': .8, 'y': .25, 'at': .2})
            if kind == 3:
                ovs.append({'type': 'map_pin', 'text': 'Hang Chauvet, Pháp', 'x': .62, 'y': .5, 'at': .2})
                ovs.append({'type': 'arrow', 'text': 'lối vào', 'x': .4, 'y': .55, 'angle': 20, 'at': .8})
            if ovs: beat['overlays'] = ovs
            beats.append(beat); n += 1
            at += beat_seconds
        props_scenes.append({'id': f'SC{s + 1:02}', 'title': f'Cảnh {s + 1}', 'start': start, 'end': start + scene_len,
                             'image': beats[0]['src'], 'images': beats, 'chapter': f'Chương {s + 1}'})
        t = start
        while t < start + scene_len - .01:
            d = min(6., start + scene_len - t)
            segments.append({'scene_id': f'SC{s + 1:02}', 'text': LINES[len(segments) % len(LINES)], 'start': t, 'end': t + d})
            t += d
    props = {'duration': seconds, 'scenes': props_scenes, 'segments': segments, 'cues': subtitle_cues(segments),
             'aspect_ratio': '16:9', 'voice_language': 'vi', 'subtitles': True, 'render_concurrency': concurrency}
    if preset: props['render_x264_preset'] = preset
    if gl: props['render_gl'] = gl
    (out / 'props.json').write_text(json.dumps(props, ensure_ascii=False, indent=1))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('out', type=Path)
    ap.add_argument('--seconds', type=float, default=600)
    ap.add_argument('--scenes', type=int, default=8)
    ap.add_argument('--beat-seconds', type=float, default=5)
    ap.add_argument('--clips', type=int, default=2)
    ap.add_argument('--concurrency', type=int, default=6)
    ap.add_argument('--preset', default=None, help='x264 preset, e.g. veryfast')
    ap.add_argument('--gl', default=None, help='Chrome GL backend, e.g. angle, vulkan, swangle')
    ap.add_argument('--build-only', action='store_true')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    beats = build(a.out.resolve(), a.seconds, a.scenes, a.beat_seconds, a.concurrency, a.preset, a.clips, a.gl)
    print(f'fixture: {a.seconds:.0f}s, {a.scenes} scenes, {beats} beats -> {a.out}')
    if a.build_only: return
    t = time.time()
    r = subprocess.run(['node', str(ROOT / 'renderer/render.mjs'), str(a.out.resolve())], cwd=ROOT)
    total = time.time() - t
    if r.returncode: raise SystemExit(r.returncode)
    timing = json.loads((a.out / 'render-timing.json').read_text())
    print(json.dumps({'total_seconds_incl_bundle_and_stills': round(total, 1), 'timings': timing}, indent=1))


if __name__ == '__main__':
    main()
