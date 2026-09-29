"""Editorial voice direction, kept separate from speech and engine parameters."""
from __future__ import annotations

import copy
import hashlib
import json


def direction_schema():
    return {
        'type': 'object',
        'properties': {
            'delivery': {'type': 'string', 'minLength': 10},
            'ending': {'type': 'string', 'minLength': 10},
            'cues': {'type': 'array', 'minItems': 1, 'maxItems': 12, 'items': {
                'type': 'object', 'properties': {
                    'quote': {'type': 'string', 'minLength': 3, 'maxLength': 180},
                    'intent': {'type': 'string', 'minLength': 5},
                }, 'required': ['quote', 'intent'], 'additionalProperties': False}},
        }, 'required': ['delivery', 'ending', 'cues'], 'additionalProperties': False,
    }


DIRECTION_INSTRUCTIONS = '''
Create voice_direction separately for each part, in Vietnamese. It is editorial
intent, NOT an engine command. delivery describes a warm, close, unhurried voice;
ending describes a smooth handoff (P01-P03) or a quiet gradual close (P04).
Include 1-12 cues, each with an exact unique contiguous quote from the FINAL
spoken text and intent describing a natural phrase boundary or gentle emphasis.
Write the speech first, then anchor cues. Repair both together when necessary.
The engine accepts the selected voice and fixed speed 0.90/pitch 1.0. It does NOT
accept SSML, emotion tags, exact pause durations, word emphasis controls or a
per-paragraph energy envelope. Express pacing through natural wording and
punctuation in the spoken text; never promise precise control of prosody.
Do not insert instructions into script. No forced whisper, dramatic rises,
uppercase emphasis, or punctuation chains. Do not change voice/speed/pitch.
'''


def validate_direction(part):
    direction = part.get('voice_direction')
    if not isinstance(direction, dict) or set(direction) != {'delivery', 'ending', 'cues'}:
        raise ValueError(f"{part.get('id')}: thiếu kịch bản giọng đọc hợp lệ.")
    for key in ('delivery', 'ending'):
        if not isinstance(direction[key], str) or len(direction[key].strip()) < 10:
            raise ValueError(f"Chỉ dẫn {key} bị rỗng hoặc quá ngắn.")
    cues = direction['cues']
    if not isinstance(cues, list) or not 1 <= len(cues) <= 12:
        raise ValueError('Cần 1–12 neo chỉ dẫn giọng mỗi phần.')
    for cue in cues:
        if not isinstance(cue, dict) or set(cue) != {'quote', 'intent'}:
            raise ValueError('Neo giọng đọc không đúng cấu trúc.')
        quote, intent = cue['quote'], cue['intent']
        if not isinstance(quote, str) or not 3 <= len(quote) <= 180 or part['script'].count(quote) != 1:
            raise ValueError('Neo giọng phải khớp nguyên văn đúng một vị trí trong lời đọc.')
        if not isinstance(intent, str) or len(intent.strip()) < 5:
            raise ValueError('Neo giọng thiếu mục đích đọc.')
    return copy.deepcopy(direction)


def direction_evidence(part):
    direction = part.get('voice_direction', {})
    return [direction.get('delivery', ''), direction.get('ending', ''),
            *[cue.get('intent', '') for cue in direction.get('cues', [])]]


def locked_content(script, generation_signature):
    """Bind exact reviewed speech AND editorial direction to engine identity."""
    parts = []
    for part in script['parts']:
        parts.append({'id': part['id'], 'script': part['script'],
                      'voice_direction': validate_direction(part)})
    value = {'parts': parts, 'generation_signature': generation_signature,
             'direction_mode': 'editorial_via_wording_and_punctuation'}
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return {**value, 'sha256': hashlib.sha256(encoded).hexdigest()}
