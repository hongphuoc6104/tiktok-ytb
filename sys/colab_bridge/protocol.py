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
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''): digest.update(chunk)
    return digest.hexdigest()


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


def build_request(root, cfg, scenes, english_scenes=(), *, primary_language='vi', assemble=False, secondary_scenes=()):
    """Keep subtitle chunks, language switches, retakes and learner holds intact."""
    if primary_language not in ('vi', 'en'): raise ValueError('Unsupported primary language')
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
            chunks = parts[n] if parts else [{'text': text, 'lang': primary_language}]
            indexes = [item(x['text'], x['lang'], sc.get('retake', 0),
                            cfg['tts_speed'] if x['lang'] == 'vi' else cfg.get('en_speed', cfg.get('audio_english_spans_rate', 1.)))
                       for x in chunks]
            pause = sc['tail'] if n == len(sc['texts']) - 1 else sc['gaps'][n]
            if not math.isfinite(float(pause)) or not 0 <= float(pause) <= 8:
                raise ValueError('Invalid pause')
            segments.append(dict(scene_id=scene_id, text=text, items=indexes, pause=float(pause)))
    for sc in english_scenes:
        english.append(dict(scene_id=safe_id(sc['scene_id']),
                            item=item(sc['narration_en'], 'en', sc.get('retake', 0), cfg.get('en_speed', 1.)),
                            pause=float(sc['tail']), retake=int(sc.get('retake', 0))))
    secondary = []
    for sc in secondary_scenes:
        language = sc['language']
        if language not in ('vi', 'en') or language == primary_language:
            raise ValueError('Invalid secondary language')
        pause = float(sc['tail'])
        if not math.isfinite(pause) or not 0 <= pause <= 8: raise ValueError('Invalid secondary pause')
        secondary.append(dict(scene_id=safe_id(sc['scene_id']), language=language, text=sc['text'],
                              items=[item(sc['text'], language, sc.get('retake', 0), cfg['tts_speed'] if language == 'vi' else cfg.get('en_speed', 1.))], pause=pause))
    profiles = load_profiles(root, cfg, {x['language'] for x in items} | {primary_language})
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
    if secondary: request['secondary'] = secondary
    if primary_language != 'vi': request['primary_language'] = primary_language
    if assemble:
        support = []
        for name, source in [('audio_processing.py', 'audio_processing.py'), ('subtitles.py', 'scripts/subtitles.py'), ('media_packaging.py', 'media_packaging.py')]:
            path = Path(root) / source
            if not path.is_file(): raise ValueError('Missing remote processing module: ' + source)
            support.append({'name': name, 'local_path': str(path.resolve()), 'sha256': file_hash(path)})
        request['assemble'] = True
        request['assembly_settings'] = {key: cfg[key] for key in ('audio_lufs', 'audio_peak_db') if key in cfg}
        request['support_files'] = support
    # Local paths are transport details, never content identity.
    identity = dict(request, profiles={k: {a: b for a, b in v.items() if a != 'local_wav'} for k, v in profiles.items()})
    if 'support_files' in request:
        identity['support_files'] = [{k: v for k,v in f.items() if k != 'local_path'} for f in request['support_files']]
    request['request_id'] = stamp(identity)
    return request


def validate_result(folder, req):
    """Verify provenance, complete ordering, waveforms and practice holds before import."""
    folder = Path(folder)
    result = json.loads((folder / 'tts-result.json').read_text())
    if result.get('request_id') != req['request_id'] or result.get('voice') != req['profiles'][req.get('primary_language','vi')]['voice']:
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
    if req.get('secondary'):
        extra = json.loads((folder / 'secondary-result.json').read_text())
        if extra.get('request_id') != req['request_id'] or len(extra.get('segments', [])) != len(req['secondary']):
            raise ValueError('Secondary track provenance or segment count mismatch')
        names.append('secondary-result.json')
        for got, wanted in zip(extra['segments'], req['secondary']):
            if (got['scene_id'], got['language'], got['text']) != (wanted['scene_id'], wanted['language'], wanted['text']):
                raise ValueError('Secondary track scene/text/language mismatch')
            names.append(wav(got['path'], got['content_duration'], wanted['pause']))
    if req.get('assemble'):
        assembled = json.loads((folder / 'audio-result.json').read_text())
        if (assembled.get('request_id') != req['request_id'] or assembled.get('processing_location') != 'colab'
                or assembled.get('language') != req.get('primary_language', 'vi')):
            raise ValueError('Remote assembly provenance mismatch')
        payload = assembled['payload']
        if payload.get('voice') != req['profiles'][req.get('primary_language', 'vi')]['voice']:
            raise ValueError('Remote assembled voice mismatch')
        primary = req.get('primary_language', 'vi')
        expected_tracks = {primary} | ({'en'} if req['english'] else set()) | {part['language'] for part in req.get('secondary', [])}
        if set(payload.get('tracks', {})) != expected_tracks:
            raise ValueError('Remote assembled language tracks mismatch')
        for language, track in payload['tracks'].items():
            if track.get('language') != language or track.get('voice') != req['profiles'][language]['voice']:
                raise ValueError('Remote track language/voice mismatch')
            expected_speed = next(item['speed'] for item in req['items'] if item['language'] == language)
            if track.get('speed') != expected_speed: raise ValueError('Remote track speed mismatch')
            if Path(track['wav']).name != track['wav'] or track['wav'] not in assembled.get('files', {}) or not math.isfinite(track['duration']):
                raise ValueError('Unsafe remote track WAV or duration')
            track_path = folder / track['wav']
            if track_path.is_symlink() or not track_path.is_file() or file_hash(track_path) != assembled['files'][track['wav']]:
                raise ValueError('Assembled artifact missing or changed')
            with wave.open(str(folder / track['wav'])) as handle:
                if (handle.getnchannels(), handle.getsampwidth(), handle.getframerate()) != (1, 2, 48000) or abs(handle.getnframes() / handle.getframerate() - track['duration']) > 2 / 48000:
                    raise ValueError('Remote track WAV format/duration mismatch')
            if language == primary: wanted = req['segments']
            elif language == 'en' and req['english']:
                wanted = [dict(part, text=req['items'][part['item']]['text']) for part in req['english']]
            else: wanted = [part for part in req['secondary'] if part['language'] == language]
            segments = track.get('segments', [])
            if len(segments) != len(wanted): raise ValueError('Remote track segment count mismatch')
            cursor = 0.
            for got, expected in zip(segments, wanted):
                if not all(math.isfinite(got[key]) for key in ('start', 'end', 'content_end')): raise ValueError('Nonfinite remote track timeline')
                if (got['scene_id'], got['text']) != (expected['scene_id'], expected['text']) or abs(got['start'] - cursor) > 2 / 48000:
                    raise ValueError('Remote track text/order/timeline mismatch')
                if abs(got['end'] - got['content_end'] - expected['pause']) > 2 / 48000:
                    raise ValueError('Remote track learner pause mismatch')
                cursor = got['end']
            if abs(cursor - track['duration']) > 2 / 48000: raise ValueError('Remote track timeline duration mismatch')

        if not assembled.get('files') or payload['wav'] not in assembled['files'] or payload['srt'] not in assembled['files']:
            raise ValueError('Missing assembled output manifest')
        referenced = {payload['wav'], payload['srt'], payload['generation_report']}
        for track in payload['tracks'].values():
            referenced.update((track['wav'], track['srt']))
            referenced.update(part['path'] for part in track['segments'])
            referenced.update(part['path'] for part in track['scenes'])
        if not referenced <= assembled['files'].keys(): raise ValueError('Unhashed audio payload artifact')
        names.append('audio-result.json')
        for name, expected_hash in assembled['files'].items():
            path = folder / name
            if Path(name).name != name or path.is_symlink() or (path.suffix not in ('.wav', '.srt') and name not in ('tts-result.json', 'en-result.json', 'secondary-result.json')):
                raise ValueError('Unsafe assembled artifact path')
            if not path.is_file() or not path.stat().st_size or file_hash(path) != expected_hash:
                raise ValueError('Assembled artifact missing or changed')
            if name not in names: names.append(name)
        with wave.open(str(folder / payload['wav'])) as handle:
            if (handle.getnchannels(), handle.getsampwidth(), handle.getframerate()) != (1, 2, 48000):
                raise ValueError('Invalid assembled audio format')
            if abs(handle.getnframes() / handle.getframerate() - payload['duration']) > 2 / 48000:
                raise ValueError('Assembled duration mismatch')
    if len(names) != len(set(names)):
        raise ValueError('Duplicate remote output path')
    return names
