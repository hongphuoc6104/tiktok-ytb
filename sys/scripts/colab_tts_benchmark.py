#!/usr/bin/env python3
"""Prepare/run/report a voice-preserving A/B sample outside production jobs."""
import argparse
import json
from pathlib import Path
import sys
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from colab_bridge.client import Client
from colab_bridge.protocol import build_request


def duration(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['prepare', 'run', 'collect', 'report'])
    ap.add_argument('--out', type=Path, default=ROOT / 'scratch/colab-tts-benchmark')
    args = ap.parse_args()
    cfg = json.loads((ROOT / 'config.json').read_text())
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    request = out / 'request.json'
    if args.action == 'prepare':
        profiles = {k: json.loads((ROOT / v).read_text()) for k, v in cfg['colab_tts']['voices'].items()}
        vi, en = profiles['vi']['reference_text'], profiles['en']['reference_text']
        scenes = [dict(scene_id='AB01', narration=vi, texts=[vi], retake=0, gaps=[], tail=2.)]
        english = [dict(scene_id='AB01', narration_en=en, retake=0, tail=2.)]
        req = build_request(ROOT, cfg, scenes, english)
        request.write_text(json.dumps(req, ensure_ascii=False, indent=2))
        baseline = {k: dict(path=str((ROOT / cfg['colab_tts']['voices'][k]).parent / v['reference_wav']),
                           duration=duration((ROOT / cfg['colab_tts']['voices'][k]).parent / v['reference_wav']),
                           voice=v['voice'], speed=v['source_speed']) for k, v in profiles.items()}
        (out / 'baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2))
        print(request)
        return
    if args.action in ('run', 'collect'):
        start = time.monotonic()
        Client(ROOT, cfg).synthesize(json.loads(request.read_text()), out / 'result', out / 'cache',
                                     collect_only=args.action == 'collect')
        (out / 'wall-time.json').write_text(json.dumps({'elapsed_seconds': time.monotonic() - start, 'action': args.action}))
    baseline = json.loads((out / 'baseline.json').read_text())
    result = json.loads((out / 'result/tts-result.json').read_text())
    en = json.loads((out / 'result/en-result.json').read_text())
    report = {'production_approval': False, 'listening_status': 'pending', 'gpu': result['engine']['device'],
              'synthesis_seconds': result['elapsed_seconds'], 'comparisons': {}}
    for lang, meta in [('vi', result['segments'][0]), ('en', en['scenes'][0])]:
        measured = meta['content_duration']
        report['comparisons'][lang] = dict(baseline[lang], candidate=str(out / 'result' / meta['path']),
                                           candidate_speech_seconds=measured,
                                           duration_ratio=measured / baseline[lang]['duration'],
                                           measured_tail_seconds=duration(out / 'result' / meta['path']) - measured)
    (out / 'comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
