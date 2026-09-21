#!/usr/bin/env python3
"""
Video Pilot v3 — Standalone Re-renderer for 16:9 Explainer Videos.
Safely re-renders 16:9 videos with a new voice while preserving repository integrity.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_PAUSE = {'para': 0.70, 'sentence': 0.50, 'minor': 0.30, 'tail': 0.35}


def gap_after(text, g):
    return g.get('sentence', DEFAULT_PAUSE['sentence']) if text.rstrip()[-1:] in '.!?…' else g.get('minor', DEFAULT_PAUSE['minor'])


def frames_of(path):
    with wave.open(str(path)) as wav:
        return wav.getnframes()


def timestamp(t):
    ms = round(t * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def make_srt(segs):
    return '\n'.join(f"{i}\n{timestamp(s['start'])} --> {timestamp(s['end'])}\n{s['text']}\n" for i, s in enumerate(segs, 1))


def chunks(text):
    import re
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    parts = []
    for s in raw:
        s = s.strip()
        if not s:
            continue
        if len(s) > 180:
            sub = re.split(r'(?<=[,;:\-])\s+', s)
            parts.extend([x.strip() for x in sub if x.strip()])
        else:
            parts.append(s)
    return parts if parts else [text.strip()]


def master_audio(src, dst, lufs=-14.0, peak_db=-1.5):
    """EQ and loudness normalization matching Video Pilot standards."""
    eq = 'equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=7000:t=q:w=2:g=-2.5'
    subprocess.run(['ffmpeg', '-y', '-i', str(src), '-af', eq, '-ar', '48000', '-c:a', 'pcm_s16le', str(dst)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if not (dst.exists() and dst.stat().st_size > 1000):
        return
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(dst), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    try:
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    except (ValueError, KeyError):
        dst.unlink(missing_ok=True)
        return
    gain = float(lufs) - float(m['input_i'])
    final = dst.with_name(dst.stem + '_lv.wav')
    subprocess.run(['ffmpeg', '-y', '-i', str(dst), '-af',
                    f'volume={gain:.2f}dB,alimiter=limit={10**(peak_db/20):.4f}:level=disabled',
                    '-ar', '48000', '-c:a', 'pcm_s16le', str(final)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    dst.unlink(missing_ok=True)
    if final.exists() and final.stat().st_size > 1000 and frames_of(final) == frames_of(src):
        shutil.move(str(final), str(src))
    else:
        final.unlink(missing_ok=True)


def synthesize_vieneu(content_scenes, voice_name, work_dir, cfg):
    """Synthesizes speech using Vieneu ONNX in .venv-tts."""
    py = ROOT / '.venv-tts/bin/python'
    if not py.exists():
        raise RuntimeError('.venv-tts not found')
    
    work_dir.mkdir(parents=True, exist_ok=True)
    g = cfg.get('tts_pause', DEFAULT_PAUSE)
    scenes = [{'scene_id': s['id'], 'narration': s['narration'], 'texts': chunks(s['narration'])} for s in content_scenes]
    for k, sc in enumerate(scenes):
        sc['gaps'] = [gap_after(t, g) for t in sc['texts'][:-1]]
        sc['tail'] = g.get('tail', DEFAULT_PAUSE['tail']) if k == len(scenes) - 1 else g.get('para', DEFAULT_PAUSE['para'])
    
    settings_payload = {
        'tts_voice': voice_name,
        'tts_temperature': cfg.get('tts_temperature', 0.65),
        'tts_top_p': cfg.get('tts_top_p', 0.95),
        'tts_max_chars': cfg.get('tts_max_chars', 256),
        'tts_scene_synthesis': cfg.get('tts_scene_synthesis', True),
        'tts_backend': cfg.get('tts_backend', 'onnx'),
        'tts_precision': cfg.get('tts_precision', 'fp32'),
    }
    
    req_file = work_dir / 'request.json'
    req_file.write_text(json.dumps({'settings': settings_payload, 'scenes': scenes}, ensure_ascii=False, indent=2))
    
    print(f"[TTS] Synthesizing {len(scenes)} scenes with Vieneu voice '{voice_name}'...")
    res = subprocess.run([str(py), str(ROOT / 'tts_worker.py'), str(req_file), str(work_dir)],
                         capture_output=True, text=True)
    (work_dir / 'tts.log').write_text(res.stdout + '\n' + res.stderr)
    if res.returncode != 0:
        raise RuntimeError(f"Vieneu TTS failed: {res.stderr[:500]}")
    
    meta = json.loads((work_dir / 'tts-result.json').read_text())
    segments = []
    cursor = 0.0
    frames = []
    params = None
    scene_timings = {}
    
    for x in meta['segments']:
        file = work_dir / x['path']
        with wave.open(str(file)) as wav:
            fmt = (wav.getnchannels(), wav.getsampwidth(), wav.getframerate())
            if params and fmt != params:
                raise RuntimeError('Inconsistent audio formats')
            params = fmt
            duration = wav.getnframes() / wav.getframerate()
            frames.append(wav.readframes(wav.getnframes()))
        
        start_t = cursor
        end_t = cursor + duration
        segments.append({'scene_id': x['scene_id'], 'text': x['text'], 'start': start_t, 'end': end_t, 'path': str(file.name)})
        
        sc_id = x['scene_id']
        if sc_id not in scene_timings:
            scene_timings[sc_id] = {'start': start_t, 'end': end_t}
        else:
            scene_timings[sc_id]['end'] = end_t
        cursor += duration
        
    combined = work_dir / 'narration.wav'
    with wave.open(str(combined), 'wb') as wav:
        wav.setnchannels(params[0])
        wav.setsampwidth(params[1])
        wav.setframerate(params[2])
        wav.writeframes(b''.join(frames))
        
    print(f"[TTS] Combined WAV duration: {cursor:.2f}s. Mastering audio...")
    eq_wav = work_dir / 'narration_eq.wav'
    master_audio(combined, eq_wav, lufs=cfg.get('audio_lufs', -14.0), peak_db=cfg.get('audio_peak_db', -1.5))
    
    srt_file = work_dir / 'subtitles.srt'
    srt_file.write_text(make_srt(segments))
    
    return {
        'wav': combined,
        'duration': cursor,
        'segments': segments,
        'scene_timings': scene_timings,
        'srt': srt_file
    }


def main():
    parser = argparse.ArgumentParser(description="Re-render 16:9 Explainer Video with a New Voice")
    parser.add_argument('--content', default=str(ROOT / 'exports/stickman-long-001/content.json'), help="Path to content.json")
    parser.add_argument('--images-dir', default=str(ROOT / 'runs/stickman-long-001/revisions/images/18'), help="Path to images directory")
    parser.add_argument('--voice', default="Anh Khôi", help="Vieneu voice name (e.g. 'Anh Khôi', 'Trúc Ly', 'Mai Anh')")
    parser.add_argument('--work-dir', default=str(ROOT / 'scratch/rerender_stickman_16x9'), help="Working scratch directory")
    parser.add_argument('--output-dir', default=str(ROOT / 'exports/stickman-long-001'), help="Final export destination")
    args = parser.parse_args()

    content_path = Path(args.content)
    images_dir = Path(args.images_dir)
    work_dir = Path(args.work_dir)
    output_dir = Path(args.output_dir)

    if not content_path.exists():
        print(f"Error: Content file not found: {content_path}", file=sys.stderr)
        sys.exit(1)
    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}", file=sys.stderr)
        sys.exit(1)

    cfg = json.loads((ROOT / 'config.json').read_text())
    content = json.loads(content_path.read_text())
    content_scenes = content['scenes']

    print(f"=== Starting 16:9 Re-render for {content.get('topic', 'stickman-long-001')} ===")
    print(f"Voice: {args.voice}")
    print(f"Total scenes: {len(content_scenes)}")

    # 1. Synthesize Audio
    audio_dir = work_dir / 'audio'
    audio_res = synthesize_vieneu(content_scenes, args.voice, audio_dir, cfg)

    # 2. Prepare Remotion public directory
    public_dir = work_dir / 'public'
    if public_dir.exists():
        shutil.rmtree(public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)

    # Copy audio files into public
    shutil.copy(audio_res['wav'], public_dir / 'narration.wav')
    shutil.copy(audio_res['wav'], public_dir / 'narration_en.wav')

    # Copy and map 16:9 images
    planned_scenes = []
    print("[Render] Mapping 16:9 scenes and copying visual assets...")
    for s in content_scenes:
        sc_id = s['id']
        timing = audio_res['scene_timings'].get(sc_id, {'start': 0.0, 'end': 10.0})
        
        # Look for 16x9 specific image first
        img_name_16x9 = f"{sc_id}_16x9.png"
        img_src = images_dir / img_name_16x9
        if not img_src.exists():
            img_src = images_dir / f"{sc_id}.png"
        if not img_src.exists():
            raise FileNotFoundError(f"Missing image for scene {sc_id}")
        
        dest_name = f"{sc_id}_16x9.png"
        shutil.copy(img_src, public_dir / dest_name)
        
        planned_scenes.append({
            'id': sc_id,
            'title': s.get('title', sc_id),
            'image': dest_name,
            'start': timing['start'],
            'end': timing['end']
        })

    # 3. Create props.json conforming to outputs.mjs
    props = {
        'aspect_ratio': '16:9',
        'width': 1920,
        'height': 1080,
        'duration': audio_res['duration'],
        'scenes': planned_scenes,
        'en_duration': audio_res['duration'],
        'en_scenes': planned_scenes,
        'segments': audio_res['segments'],
        'hideSubtitles': True,
        'audioSrc': 'narration_en.wav',
        'render_concurrency': 2
    }
    props_file = work_dir / 'props.json'
    props_file.write_text(json.dumps(props, ensure_ascii=False, indent=2))

    # 4. Run Remotion render
    print(f"[Render] Invoking Remotion render engine (duration: {audio_res['duration']:.2f}s, 1920x1080)...")
    start_time = time.time()
    render_script = ROOT / 'renderer/render.mjs'
    env = os.environ.copy()
    res = subprocess.run(['node', str(render_script), str(work_dir)],
                         cwd=ROOT, env=env, capture_output=True, text=True)
    (work_dir / 'render.log').write_text(res.stdout + '\n' + res.stderr)
    
    if res.returncode != 0:
        print(f"Error: Remotion render failed: {res.stderr[-1000:]}", file=sys.stderr)
        sys.exit(2)
    
    elapsed = time.time() - start_time
    print(f"[Render] Render completed successfully in {elapsed:.1f}s.")

    # 5. Locate output video and verify with ffprobe
    rendered_video = work_dir / 'video.mp4'
    if not rendered_video.exists():
        rendered_video = work_dir / 'video_16x9.mp4'
    if not rendered_video.exists():
        print(f"Error: Expected rendered MP4 not found in {work_dir}", file=sys.stderr)
        sys.exit(2)

    probe_raw = subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(rendered_video)])
    probe = json.loads(probe_raw)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    actual_width = int(video_stream['width'])
    actual_height = int(video_stream['height'])
    actual_duration = float(probe['format']['duration'])

    print(f"[Verification] Stream Info: {actual_width}x{actual_height}, Duration: {actual_duration:.2f}s, Format: {probe['format']['format_name']}")
    assert actual_width == 1920 and actual_height == 1080, f"Dimensions mismatch: {actual_width}x{actual_height}"
    assert abs(actual_duration - audio_res['duration']) < 1.0, f"Duration mismatch: {actual_duration} vs {audio_res['duration']}"

    # 6. Copy artifacts to output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    voice_slug = args.voice.replace(' ', '_').lower()
    target_new_voice = output_dir / f"stickman-long-001_16x9_{voice_slug}.mp4"
    target_16x9 = output_dir / "video_16x9.mp4"
    target_named_16x9 = output_dir / "stickman-long-001_16x9.mp4"

    shutil.copy(rendered_video, target_new_voice)
    shutil.copy(rendered_video, target_16x9)
    shutil.copy(rendered_video, target_named_16x9)
    audio_export = output_dir / f"narration_16x9_{voice_slug}.wav"
    srt_export = output_dir / f"subtitles_16x9_{voice_slug}.srt"
    shutil.copy(audio_res['wav'], audio_export)
    shutil.copy(audio_res['srt'], srt_export)

    print("\n=== SUCCESS: 16:9 Video Successfully Created ===")
    print(f"File 1 (Dedicated voice): {target_new_voice} ({target_new_voice.stat().st_size / (1024*1024):.2f} MB)")
    print(f"File 2 (Default 16:9)   : {target_16x9}")
    print(f"Audio track             : {audio_export}")
    print(f"Subtitles (SRT)         : {srt_export}")


if __name__ == '__main__':
    main()
