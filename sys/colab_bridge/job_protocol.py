"""Bounded, hashed job bundles and metadata-only desktop result acceptance."""
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import zipfile
from .protocol import stamp, file_hash

MAX_BUNDLE = 1_000_000_000
MAX_FILES = 512
MAX_RESULT = 2_000_000_000


def safe_path(name):
    p = PurePosixPath(name)
    return isinstance(name, str) and bool(name) and '\\' not in name and not p.is_absolute() and all(x not in ('..', '.') for x in p.parts) and str(p) == name


def build_render_request(root, brief, content, images, audio, resolve):
    root = Path(root)
    assets, mapped = [], {}
    def asset(name):
        if name not in mapped:
            src = Path(resolve(name))
            if not src.is_file() or src.is_symlink(): raise ValueError('Missing or unsafe render asset')
            dest = 'assets/' + str(len(mapped)) + src.suffix.lower()
            mapped[name] = dest
            assets.append({'name': dest, 'local_path': str(src.resolve()), 'sha256': file_hash(src), 'size': src.stat().st_size})
        return mapped[name]
    images = json.loads(json.dumps(images))
    for item in images['items']: item['path'] = asset(item['path'])
    audio = json.loads(json.dumps(audio))
    for track in [audio] + list(audio.get('tracks', {}).values()) + ([audio['en']] if audio.get('en') else []):
        track['wav'] = asset(track['wav'])
    sources = []
    names = ['output_contract.py', 'scripts/story_plan.py', 'scripts/subtitles.py',
             'renderer/render.mjs', 'renderer/index.tsx', 'renderer/outputs.mjs', 'renderer/captions.mjs',
             'package.json', 'package-lock.json']
    if any(scene.get('layers') for scene in content.get('scenes', [])):
        names.insert(3, 'tools/matte_sticker.py')  # layered jobs matte stickers remotely, never locally
    for name in names:
        path = root / name
        if not path.is_file() or path.is_symlink(): raise ValueError('Missing remote source: ' + name)
        sources.append({'name': 'source/' + name, 'local_path': str(path.resolve()), 'sha256': file_hash(path), 'size': path.stat().st_size})
    worker = Path(__file__).with_name('job_worker.py')
    request = {'version': 1, 'operation': 'render', 'brief': brief, 'content': content,
               'images': images, 'audio': audio, 'files': sources + assets,
               'worker_sha256': file_hash(worker)}
    total = sum(f['size'] for f in request['files'])
    if len(request['files']) > MAX_FILES or total > MAX_BUNDLE: raise ValueError('Remote job bundle exceeds bounds')
    identity = dict(request, files=[{k:v for k,v in f.items() if k != 'local_path'} for f in request['files']])
    request['request_id'] = stamp(identity)
    return request


def bundle(request, path):
    remote = dict(request, files=[{k:v for k,v in f.items() if k != 'local_path'} for f in request['files']])
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('request.json', json.dumps(remote, ensure_ascii=False))
        for entry in request['files']:
            src = Path(entry['local_path'])
            if not safe_path(entry['name']) or src.is_symlink() or src.stat().st_size != entry['size'] or file_hash(src) != entry['sha256']:
                raise ValueError('Remote bundle input changed or unsafe')
            archive.write(src, entry['name'])
    return remote


def extract(archive, target, *, limit=MAX_RESULT, flat=False):
    with zipfile.ZipFile(archive) as source:
        entries = source.infolist()
        names = [e.filename for e in entries]
        if len(entries) > MAX_FILES or sum(e.file_size for e in entries) > limit or len(names) != len(set(names)):
            raise ValueError('Remote archive exceeds bounds or repeats a path')
        for entry in entries:
            if not safe_path(entry.filename) or entry.is_dir() or (flat and Path(entry.filename).name != entry.filename) or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Unsafe remote archive path')
        source.extractall(target)


def validate_render_result(folder, request):
    folder = Path(folder)
    result = json.loads((folder / 'render-result.json').read_text())
    if result.get('request_id') != request['request_id'] or result.get('operation') != 'render' or result.get('processing_location') != 'colab':
        raise ValueError('Remote render provenance mismatch')
    if 'T4' not in result.get('device', ''): raise ValueError('Remote render runtime T4 provenance missing')
    files = result.get('files', {})
    if not {'video.mp4', 'layout.json', 'editorial-audit.json', 'props.json'} <= files.keys() or len(files) > MAX_FILES: raise ValueError('Incomplete remote render manifest')
    for name, record in files.items():
        path = folder / name
        if Path(name).name != name or path.is_symlink() or path.suffix not in ('.mp4', '.png', '.json', '.srt'):
            raise ValueError('Unsafe remote render artifact')
        if not path.is_file() or not path.stat().st_size or path.stat().st_size != record['size'] or file_hash(path) != record['sha256']:
            raise ValueError('Remote render artifact changed or missing')
    layout = json.loads((folder / 'layout.json').read_text())
    if layout.get('passed') is not True or layout.get('failures'): raise ValueError('Remote caption layout failed')
    props = json.loads((folder / 'props.json').read_text())
    if props.get('outputs') != request['brief']['outputs'] or props.get('aspect_ratio') != request['brief']['aspect_ratio']:
        raise ValueError('Remote props output contract mismatch')
    plans = request['brief']['outputs']
    requested_languages = list(dict.fromkeys(plan['language'] for plan in plans))
    if props.get('primary_language') != requested_languages[0] or set(props.get('tracks', {})) != set(requested_languages):
        raise ValueError('Remote props primary language/tracks mismatch')
    # Metadata reconciliation only: no local audio, image or render processing.
    from scripts.subtitles import subtitle_cues
    for language in requested_languages:
        track = props['tracks'][language]
        source = request['audio']['tracks'][language]
        expected_cues = source['cues'] if 'cues' in source else subtitle_cues(source.get('segments', []))
        expected_aspects = {plan['aspect_ratio'] for plan in plans if plan['language'] == language}
        if (track.get('audioSrc') != language + '.wav' or track.get('duration') != source['duration']
                or track.get('cues') != expected_cues or set(track.get('scenesByAspect', {})) != expected_aspects):
            raise ValueError('Remote props language audio/captions/timeline contract mismatch')
        for aspect in expected_aspects:
            actual_scenes = track['scenesByAspect'][aspect]
            scenes = request.get('content', {}).get('scenes', [])
            if not isinstance(actual_scenes, list) or [scene.get('id') for scene in actual_scenes] != [scene['id'] for scene in scenes]:
                raise ValueError('Remote props scene ordering mismatch')
            images = {(item.get('image_id', item['scene_id']), item.get('ratio', aspect)): item for item in request.get('images', {}).get('items', [])}
            for got, scene in zip(actual_scenes, scenes):
                spans = [part for part in source.get('segments', []) if part['scene_id'] == scene['id']]
                if not spans or got.get('start') != spans[0]['start'] or got.get('end') != spans[-1]['end']:
                    raise ValueError('Remote props scene/audio timing mismatch')
                wanted_beats = scene.get('beats', [])
                actual_beats = got.get('images', [])
                if wanted_beats:
                    if len(actual_beats) != len(wanted_beats): raise ValueError('Remote props visual beat count mismatch')
                    last = -1
                    for beat, wanted in zip(actual_beats, wanted_beats):
                        expected_asset = Path(images[(wanted['image_id'], aspect)]['path']).name
                        at = beat.get('at')
                        if (beat.get('id'), beat.get('src'), beat.get('effect'), beat.get('focus')) != (wanted['id'], expected_asset, wanted['effect'], wanted['focus']):
                            raise ValueError('Remote props visual asset/beat mismatch')
                        if isinstance(at, bool) or not isinstance(at, (int, float)) or not math.isfinite(at) or at <= last or not 0 <= at < got['end'] - got['start']:
                            raise ValueError('Remote props visual beat timing mismatch')
                        last = at
                    if actual_beats[0]['at'] != 0 or got.get('image') != actual_beats[0]['src']:
                        raise ValueError('Remote props first image mismatch')
                elif got.get('image') != Path(images[(scene['id'], aspect)]['path']).name:
                    raise ValueError('Remote props scene image mismatch')
                wanted_layers, got_layers = scene.get('layers', []), got.get('layers')
                if wanted_layers:
                    if (not isinstance(got_layers, list) or len(got_layers) != len(wanted_layers) + 1 or not got_layers[0].get('bg')
                            or [x.get('id') for x in got_layers[1:]] != [x['id'] for x in wanted_layers]):
                        raise ValueError('Remote props layer contract mismatch')
                    for layer in got_layers:
                        if not isinstance(layer.get('src'), str) or not layer['src'].endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            raise ValueError('Remote props layer asset mismatch')
                        start = layer.get('start', 0)
                        if isinstance(start, bool) or not isinstance(start, (int, float)) or not math.isfinite(start) or not 0 <= start < got['end'] - got['start']:
                            raise ValueError('Remote props layer timing mismatch')
                elif got_layers:
                    raise ValueError('Remote props unexpected layers')
    deliveries = result.get('outputs', [])
    if len(plans) != len(deliveries): raise ValueError('Remote render missing requested outputs')
    for plan, got in zip(plans, deliveries):
        w, h = (1080, 1920) if plan['aspect_ratio'] == '9:16' else (1920, 1080)
        wanted_duration = request['audio']['tracks'][plan['language']]['duration']
        if (got.get('language'), got.get('aspect_ratio'), got.get('subtitles'), got.get('width'), got.get('height')) != (plan['language'], plan['aspect_ratio'], plan['subtitles'], w, h):
            raise ValueError('Remote render output contract mismatch')
        if got.get('file') not in files or not got['file'].endswith('.mp4') or got.get('video_codec') != 'h264' or got.get('audio_codec') != 'aac':
            raise ValueError('Remote MP4 streams invalid')
        with (folder / got['file']).open('rb') as handle:
            if handle.read(12)[4:8] != b'ftyp': raise ValueError('Invalid MP4 container header')
        duration = got.get('duration', 0)
        if not isinstance(duration, (int, float)) or not math.isfinite(duration) or abs(duration - wanted_duration) > .25:
            raise ValueError('Remote MP4 duration mismatch')
    if files['video.mp4']['sha256'] != files[deliveries[0]['file']]['sha256']:
        raise ValueError('Primary video differs from first delivery')
    return ['render-result.json', *files]
