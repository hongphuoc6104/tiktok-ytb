"""Audio assembly, mastering and captions executed beside the Colab worker.

Only standard-library modules are imported here; processing helpers are
versioned uploaded sources. The desktop receives the finished manifest.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import wave


def _load(folder, name):
    path = Path(folder) / (name + '.py')
    spec = importlib.util.spec_from_file_location('vp_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _join(folder, name, parts):
    frames = []
    for part in parts:
        path = Path(folder) / part['path']
        if Path(part['path']).name != part['path'] or path.is_symlink():
            raise ValueError('Unsafe audio segment path')
        with wave.open(str(path)) as handle:
            if (handle.getnchannels(), handle.getsampwidth(), handle.getframerate()) != (1, 2, 48000):
                raise ValueError('Remote assembly expects mono PCM16/48k')
            frames.append(handle.readframes(handle.getnframes()))
    with wave.open(str(Path(folder) / name), 'wb') as handle:
        handle.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        handle.writeframes(b''.join(frames))


def _srt(cues):
    def timestamp(seconds):
        value = round(seconds * 1000)
        hours, value = divmod(value, 3600000)
        minutes, value = divmod(value, 60000)
        seconds, ms = divmod(value, 1000)
        return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'
    return '\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n"
                     for i, c in enumerate(cues, 1))


def assemble(request, folder, support_folder):
    folder = Path(folder)
    processing = _load(support_folder, 'audio_processing')
    captions = _load(support_folder, 'subtitles')
    primary = request.get('primary_language', 'vi')
    meta = json.loads((folder / 'tts-result.json').read_text())
    primary_parts = meta['segments']
    tracks, artifacts = {}, ['tts-result.json']
    artifacts.extend(part['path'] for part in primary_parts)

    def make_track(language, pieces, texts):
        cursor, segments = 0., []
        for part, text in zip(pieces, texts):
            with wave.open(str(folder / part['path'])) as handle:
                seconds = handle.getnframes() / handle.getframerate()
            segment = {'scene_id': part['scene_id'], 'text': text, 'path': part['path'],
                       'start': cursor, 'end': cursor + seconds,
                       'content_end': cursor + part['content_duration']}
            segments.append(segment)
            cursor += seconds
        name = 'narration.wav' if language == primary else 'narration_' + language + '.wav'
        _join(folder, name, pieces)
        processing.master(folder / name, folder / ('eq_' + language + '.wav'),
                          request.get('assembly_settings', {}))
        cues = captions.subtitle_cues(segments)
        srt_name = 'subtitles.srt' if language == primary else 'subtitles_' + language + '.srt'
        (folder / srt_name).write_text(_srt(cues))
        artifacts.extend([name, srt_name])
        scenes = []
        for scene_id in dict.fromkeys(s['scene_id'] for s in segments):
            grouped = [s for s in segments if s['scene_id'] == scene_id]
            scene_name = language + '-' + scene_id + '-assembled.wav'
            _join(folder, scene_name, grouped)
            artifacts.append(scene_name)
            scenes.append({'scene_id': scene_id, 'path': scene_name, 'start': grouped[0]['start'],
                           'end': grouped[-1]['end'], 'content_end': grouped[-1]['content_end']})
        return {'voice': request['profiles'][language]['voice'], 'engine': 'colab-omnivoice',
                'language': language, 'speed': next(x['speed'] for x in request['items'] if x['language'] == language),
                'wav': name, 'srt': srt_name, 'duration': cursor, 'segments': segments,
                'scenes': scenes, 'cues': cues}

    tracks[primary] = make_track(primary, primary_parts, [s['text'] for s in request['segments']])
    if request['english']:
        english = json.loads((folder / 'en-result.json').read_text())
        artifacts.append('en-result.json')
        artifacts.extend(part['path'] for part in english['scenes'])
        tracks['en'] = make_track('en', english['scenes'],
                                  [request['items'][s['item']]['text'] for s in request['english']])
    if request.get('secondary'):
        pieces = json.loads((folder / 'secondary-result.json').read_text())['segments']
        artifacts.append('secondary-result.json')
        artifacts.extend(part['path'] for part in pieces)
        for language in dict.fromkeys(part['language'] for part in request['secondary']):
            grouped = [part for part in pieces if part['language'] == language]
            tracks[language] = make_track(language, grouped, [part['text'] for part in grouped])
    selected = tracks[primary]
    payload = {key: selected[key] for key in ('voice', 'wav', 'srt', 'duration', 'segments')}
    payload.update(language=primary, backend='colab-omnivoice', tracks=tracks,
                   generation_report='tts-result.json')
    if 'en' in tracks:
        payload['en'] = {key: tracks['en'][key] for key in ('engine', 'voice', 'wav', 'duration', 'scenes')}
    report = {'request_id': request['request_id'], 'processing_location': 'colab',
              'language': primary, 'payload': payload,
              'files': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                        for name in dict.fromkeys(artifacts)}}
    (folder / 'audio-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report
