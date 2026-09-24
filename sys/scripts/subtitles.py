"""Lossless, phrase-aware captions. Timing remains an explicit interpolation."""
import math
import re

MAX_CUE_CHARS = 56
MAX_LINE_CHARS = 30
_WEAK_END = {'a', 'an', 'the', 'to', 'of', 'at', 'on', 'in', 'for', 'with',
             'và', 'là', 'của', 'với', 'để', 'nhưng', 'một', 'những', 'các'}


def has_words(text):
    return any(c.isalnum() for c in text)


def phrase_chunks(text, max_len=MAX_CUE_CHARS):
    """Choose word boundaries globally; never split a token or drop punctuation.

    A short final fragment costs more than a slightly earlier balanced break.
    Punctuation stays attached to its token, including closing quotation marks.
    Long tokens are preserved and reported by QA rather than truncated.
    """
    words = text.split()
    if not words:
        return []
    n = len(words)
    costs = [math.inf] * (n + 1)
    paths = [None] * (n + 1)
    costs[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            phrase = ' '.join(words[i:j])
            if len(phrase) > max_len and j > i + 1:
                break
            if not has_words(phrase) and n > 1:
                continue
            length = len(phrase)
            penalty = 1 + ((max_len - min(length, max_len)) / max_len) ** 2
            if n > j and not has_words(words[j]):
                penalty += 100  # Do not strand closing punctuation.
            if j - i == 1 and n > 1:
                penalty += 8
            last = words[j - 1].strip('"\'“”‘’.,!?;:').lower()
            if j < n and last in _WEAK_END:
                penalty += 2
            if re.search(r'[.!?;:,]["”’\']?$', phrase):
                penalty -= .3
            if penalty + costs[j] < costs[i]:
                costs[i], paths[i] = penalty + costs[j], j
    result, i = [], 0
    while i < n:
        j = paths[i] or n
        result.append(' '.join(words[i:j]))
        i = j
    return result


def wrap_phrase(text, max_len=MAX_LINE_CHARS):
    """At most two balanced lines, favoring a grammatical boundary."""
    if len(text) <= max_len:
        return text
    words = text.split()
    candidates = []
    for i in range(1, len(words)):
        left, right = ' '.join(words[:i]), ' '.join(words[i:])
        if max(len(left), len(right)) > max_len:
            continue
        if not has_words(left) or not has_words(right):
            continue
        penalty = abs(len(left) - len(right))
        if words[i - 1].strip('.,!?;:"').lower() in _WEAK_END:
            penalty += 12
        if re.search(r'[.!?;:,]["”’\']?$', left):
            penalty -= 6
        candidates.append((penalty, left + '\n' + right))
    return min(candidates, default=(0, text))[1]


def subtitle_cues(segments):
    cues = []
    for seg in segments:
        text = ' '.join((seg.get('text') or '').split())
        start, end = seg['start'], seg['end']
        if not all(math.isfinite(float(x)) for x in (start, end)) or start < 0 or end <= start:
            raise ValueError('Invalid caption segment interval')
        content_end = seg.get('content_end', end)
        if not math.isfinite(float(content_end)) or not start < content_end <= end:
            raise ValueError('Invalid content interval before added silence')
        if not text:
            continue  # An explicit silent interval is not a visible caption.
        scene = seg.get('scene_id')
        if not has_words(text) and cues and cues[-1]['scene_id'] == scene and abs(cues[-1]['end'] - start) < .001:
            cues[-1]['text'] = wrap_phrase(' '.join((cues[-1]['text'] + ' ' + text).split()))
            cues[-1]['end'] = end
            continue
        chunks = phrase_chunks(text)
        weights = [len(c) for c in chunks]
        total = sum(weights)
        used = 0
        for chunk, weight in zip(chunks, weights):
            a = start + (content_end - start) * used / total
            used += weight
            z = end if used == total else start + (content_end - start) * used / total
            cues.append({'text': wrap_phrase(chunk), 'start': a, 'end': z, 'scene_id': scene})
    return cues


def audit_cues(cues):
    """Technical defects and editorial warnings, never a semantic approval."""
    errors, warnings = [], []
    last = 0.
    for i, cue in enumerate(cues):
        text = cue.get('text', '')
        start, end = cue['start'], cue['end']
        ref = {'cue': i + 1, 'start': start, 'end': end, 'text': text}
        if not all(math.isfinite(float(x)) for x in (start, end)) or start < last - .001 or end <= start:
            errors.append(dict(ref, code='CAPTION_TIMELINE', message='Thời gian phụ đề không hợp lệ hoặc chồng lấn.'))
        if not has_words(text):
            errors.append(dict(ref, code='CAPTION_ORPHAN', message='Phụ đề rỗng hoặc chỉ có dấu câu.'))
        lines = text.splitlines()
        if len(lines) > 2 or any(len(line) > MAX_LINE_CHARS for line in lines):
            warnings.append(dict(ref, code='CAPTION_LAYOUT', message='Cần kiểm tra độ dài dòng trên khung thật.'))
        duration = end - start
        if duration > 0 and len(''.join(text.split())) / duration > 20:
            warnings.append(dict(ref, code='CAPTION_READING_RATE', message='Mật độ trên 20 ký tự/giây; đây là ngưỡng gợi ý, cần thử đọc với người học.'))
        if duration < .7:
            warnings.append(dict(ref, code='CAPTION_SHORT_HOLD', message='Thẻ dưới 0,7 giây; kiểm tra đọc và ngắt cụm, không tự kéo lệch lời.'))
        last = end
    return {'errors': errors, 'warnings': warnings,
            'timing_method': 'segment_character_interpolation_not_word_alignment',
            'quality_approval': False}
