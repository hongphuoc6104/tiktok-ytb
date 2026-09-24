#!/usr/bin/env python3
"""Read-only editorial preflight for render props; does not approve a job."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.subtitles import audit_cues


def audit(props):
    # Horizontal output deliberately hides Vietnamese captions.
    applicable = props.get('aspect_ratio', '9:16') != '16:9'
    report = audit_cues(props.get('cues', [])) if applicable else {
        'errors': [], 'warnings': [], 'quality_approval': False}
    report['captions_applicable'] = applicable
    report['beats'] = []
    for scene in props.get('scenes', []):
        beats = scene.get('images', [])
        for i, beat in enumerate(beats):
            start = scene['start'] + beat['at']
            end = scene['start'] + beats[i + 1]['at'] if i + 1 < len(beats) else scene['end']
            row = {'scene_id': scene['id'], 'id': beat.get('id'), 'start': start, 'end': end}
            report['beats'].append(row)
            if end <= start:
                report['errors'].append(dict(row, code='BEAT_TIMELINE', message='Nhịp hình có thời gian không hợp lệ.'))
    report['requires_actual_inspection'] = ['image_meaning', 'character_identity', 'pronunciation', 'practice_pause', 'full_playback']
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kiểm tra kỹ thuật biên tập, không duyệt chất lượng.')
    parser.add_argument('--props', type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.props.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result['errors'] else 0)
