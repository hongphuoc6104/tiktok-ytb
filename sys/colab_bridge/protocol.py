"""Pure request planning and result validation; no model or network imports."""
import hashlib
import json
import math
import re
import wave
from pathlib import Path

VERSION = 1


def stamp(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def positive(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')
    return value


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise ValueError('Invalid scene ID')
    return value


def load_profiles(root, cfg, languages):
    profiles = {}
    expected = {'vi': cfg['tts_voice'], 'en': cfg['en_voice']}
    for lang in sorted(languages):
        path = root / cfg['colab_tts']['voices'][lang]
        profile = json.loads(path.read_text())
        if profile['voice'] != expected[lang] or profile['language'] != lang:
            raise ValueError(f'Colab reference does not match current {lang} voice')
        wav = path.parent / profile['reference_wav']
        if not profile.get('reference_text', '').strip() or file_hash(wav) != profile['sha256']:
            raise ValueError(f'Invalid {lang} voice reference or checksum')
        positive(profile['source_speed'], 'source_speed')
        with wave.open(str(wav)) as handle:
            if not 3 <= handle.getnframes() / handle.getframerate() <= 15:
                raise ValueError('Voice reference must be 3–15 seconds')
        profiles[lang] = dict(profile, local_wav=str(wav.resolve()))
    return profiles


def build_request(root, cfg, scenes, english_scenes=()):
    """Keep subtitle chunks, language switches, retakes and learner holds intact."""
    items, lookup, segments, english = [], {}, [], []
    def item(text, lang, retake, rate):
        text = text.strip()
        if not text:
            raise ValueError('Empty synthesis text')
        value = dict(text=text, language=lang, retake=int(retake), speed=positive(rate, 'speed'))
        key = stamp(value)
        if key not in lookup:
            lookup[key] = len(items)
            items.append(dict(value, id=f'u{len(items):05d}'))
        return lookup[key]
    for sc in scenes:
        scene_id = safe_id(sc['scene_id'])
        parts = sc.get('parts')
        if parts is not None and len(parts) != len(sc['texts']):
            raise ValueError('Language parts do not match subtitle chunks')
        for n, text in enumerate(sc['texts']):
            chunks = parts[n] if parts else [{'text': text, 'lang': 'vi'}]
            indexes = [item(x['text'], x['lang'], sc.get('retake', 0),
                            cfg['tts_speed'] if x['lang'] == 'vi' else cfg.get('audio_english_spans_rate', 1.))
                       for x in chunks]
            pause = sc['tail'] if n == len(sc['texts']) - 1 else sc['gaps'][n]
            if not math.isfinite(float(pause)) or not 0 <= float(pause) <= 8:
                raise ValueError('Invalid pause')
            segments.append(dict(scene_id=scene_id, text=text, items=indexes, pause=float(pause)))
    for sc in english_scenes:
        english.append(dict(scene_id=safe_id(sc['scene_id']),
                            item=item(sc['narration_en'], 'en', sc.get('retake', 0), 1.),
                            pause=float(sc['tail']), retake=int(sc.get('retake', 0))))
    profiles = load_profiles(root, cfg, {x['language'] for x in items} | {'vi'})
    models = cfg['colab_tts']['models']
    for lang in profiles:
        if not re.fullmatch(r'[a-f0-9]{40}', models[lang]['revision']):
            raise ValueError('Model revision must be a pinned Hugging Face commit')
    request = dict(version=VERSION, items=items, segments=segments, english=english,
                   profiles=profiles, models=models, batch_size=int(cfg['colab_tts'].get('batch_size', 4)),
                   num_step=int(cfg['colab_tts'].get('num_step', 32)), seed=int(cfg.get('en_seed', 42)),
                   span_gap=float(cfg.get('audio_english_spans_gap', .18)))
    if not 1 <= request['batch_size'] <= 8 or not 8 <= request['num_step'] <= 64:
        raise ValueError('Unsupported batch size or diffusion steps')
    # Local paths are transport details, never content identity.
    identity = dict(request, profiles={k: {a: b for a, b in v.items() if a != 'local_wav'} for k, v in profiles.items()})
    request['request_id'] = stamp(identity)
    return request


def validate_result(folder, req):
    """Verify provenance, complete ordering, waveforms and practice holds before import."""
    folder = Path(folder)
    result = json.loads((folder / 'tts-result.json').read_text())
    if result.get('request_id') != req['request_id'] or result.get('voice') != req['profiles']['vi']['voice']:
        raise ValueError('Remote result provenance mismatch')
    engine = result.get('engine', {})
    if engine.get('backend') != 'colab-omnivoice' or engine.get('models') != req['models'] or 'T4' not in engine.get('device', ''):
        raise ValueError('Remote engine/model/GPU provenance mismatch')
    def wav(name, content, pause):
        if Path(name).name != name or not name.endswith('.wav'):
            raise ValueError('Remote artifact path is not a plain WAV filename')
        path = folder / name
        if path.is_symlink():
            raise ValueError('Symlink in remote output')
        with wave.open(str(path)) as w:
            if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, 48000):
                raise ValueError('Remote WAV must be mono PCM16 at 48 kHz')
            duration = w.getnframes() / w.getframerate()
            if not math.isfinite(content) or content <= 0 or abs(duration - content - pause) > 2 / 48000:
                raise ValueError('Remote duration/learner pause mismatch')
            w.setpos(round(content * 48000))
            if any(w.readframes(w.getnframes())):
                raise ValueError('Learner pause is not silent')
        return name
    actual = result.get('segments', [])
    if len(actual) != len(req['segments']):
        raise ValueError('Missing remote subtitle chunks')
    names = ['tts-result.json']
    for got, wanted in zip(actual, req['segments']):
        if (got['scene_id'], got['text']) != (wanted['scene_id'], wanted['text']):
            raise ValueError('Remote scene/text order mismatch')
        names.append(wav(got['path'], got['content_duration'], wanted['pause']))
    if req['english']:
        en = json.loads((folder / 'en-result.json').read_text())
        if en.get('request_id') != req['request_id'] or en.get('voice') != req['profiles']['en']['voice']:
            raise ValueError('Remote English provenance mismatch')
        if len(en['scenes']) != len(req['english']):
            raise ValueError('Missing English scenes')
        names.append('en-result.json')
        for got, wanted in zip(en['scenes'], req['english']):
            if got['scene_id'] != wanted['scene_id']:
                raise ValueError('Remote English scene order mismatch')
            names.append(wav(got['path'], got['content_duration'], wanted['pause']))
    if len(names) != len(set(names)):
        raise ValueError('Duplicate remote output path')
    return names
