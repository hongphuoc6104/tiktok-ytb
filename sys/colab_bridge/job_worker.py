"""Remote worker: verifies bounded inputs; builds timeline/captions and MP4 on Colab."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile


def run(bundle_path, output_dir, expected_id, expected_worker):
    from pathlib import PurePosixPath
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != expected_worker:
        raise ValueError('Remote worker checksum mismatch')
    device = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True).strip()
    if 'T4' not in device: raise RuntimeError('COLAB_GPU_REQUIRED: expected an actual NVIDIA T4 runtime')
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    inputs = output.parent / 'inputs'; inputs.mkdir(exist_ok=True)
    with zipfile.ZipFile(bundle_path) as archive:
        entries = archive.infolist()
        if len(entries) > 513 or len({e.filename for e in entries}) != len(entries) or sum(e.file_size for e in entries) > 1_001_000_000:
            raise ValueError('Invalid job bundle bounds')
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in entry.filename or entry.is_dir() or str(name) != entry.filename or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Unsafe job bundle path')
        archive.extractall(inputs)
    request = json.loads((inputs / 'request.json').read_text())
    if request.get('operation') != 'render' or request.get('request_id') != expected_id or request.get('worker_sha256') != expected_worker:
        raise ValueError('Remote job identity mismatch')
    identity = {key:value for key,value in request.items() if key != 'request_id'}
    digest = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if digest != expected_id: raise ValueError('Job contract checksum mismatch')
    expected_names = {'request.json', *(entry['name'] for entry in request['files'])}
    if expected_names != {entry.filename for entry in entries}: raise ValueError('Job bundle contains unlisted input')
    for entry in request['files']:
        source = inputs / entry['name']
        if source.stat().st_size != entry['size'] or hashlib.sha256(source.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Job bundle hash mismatch')
    source = inputs / 'source'
    sys.path.insert(0, str(source))
    # Load from this immutable bundle, not modules retained by another job kernel.
    import importlib.util
    def load(name, relative):
        spec = importlib.util.spec_from_file_location(name, source / relative)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module
    contract = load('vp_output_contract', 'output_contract.py')
    sys.modules['output_contract'] = contract
    story = load('vp_story_plan', 'scripts/story_plan.py')
    captions = load('vp_subtitles', 'scripts/subtitles.py')
    public = output / 'public'; public.mkdir(exist_ok=True)
    tracks = {}
    audits = {}
    brief, audio = request['brief'], request['audio']
    for language in contract.languages(brief):
        track = audio['tracks'][language]
        wav = language + '.wav'; shutil.copy2(inputs / track['wav'], public / wav)
        cues = captions.subtitle_cues(track['segments'])
        audit = captions.audit_cues(cues)
        audits[language] = audit
        if any(plan['subtitles'] for plan in brief['outputs'] if plan['language'] == language) and audit['errors']:
            raise ValueError('Subtitle technical defects: ' + json.dumps(audit['errors']))
        def timestamp(seconds):
            ms = round(seconds * 1000)
            return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
        (output / ('subtitles_' + language + '.srt')).write_text('\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1)))
        by_aspect = {}
        for plan in brief['outputs']:
            if plan['language'] != language: continue
            scenes = story.timeline(request['content'], request['images'], audio, language, plan['aspect_ratio'])
            for scene in scenes:
                for beat in scene.get('images', []):
                    name = Path(beat['src']).name; shutil.copy2(inputs / beat['src'], public / name); beat['src'] = name
                name = Path(scene['image']).name; shutil.copy2(inputs / scene['image'], public / name); scene['image'] = name
            by_aspect[plan['aspect_ratio']] = scenes
        tracks[language] = {'audioSrc': wav, 'duration': track['duration'], 'cues': cues, 'scenesByAspect': by_aspect}
    props = {'aspect_ratio': brief['aspect_ratio'], 'outputs': brief['outputs'], 'primary_language': contract.primary_language(brief),
             'tracks': tracks, 'render_concurrency': 2, 'modern_style': True}
    (output / 'editorial-audit.json').write_text(json.dumps({'tracks': audits, 'processing_location': 'colab', 'quality_approval': False}, ensure_ascii=False, indent=2))
    (output / 'props.json').write_text(json.dumps(props, ensure_ascii=False, indent=2))
    # Remote dependencies are cached by the pinned source package lock.
    runtime = output.parent.parent / ('render-runtime-' + hashlib.sha256((source / 'package-lock.json').read_bytes()).hexdigest()[:16])
    runtime.mkdir(exist_ok=True)
    for name in ('package.json', 'package-lock.json'): shutil.copy2(source / name, runtime / name)
    if not (runtime / 'node_modules/@remotion/renderer').is_dir():
        subprocess.run(['npm', 'ci', '--no-audit', '--no-fund'], cwd=runtime, check=True, timeout=900)
    shutil.copytree(source / 'renderer', runtime / 'renderer', dirs_exist_ok=True)
    chrome = subprocess.check_output(['node', '--input-type=module', '-e', "import {chromium} from 'playwright'; console.log(chromium.executablePath())"], cwd=runtime, text=True).strip()
    if not Path(chrome).is_file():
        subprocess.run(['npx', '--no-install', 'playwright', 'install', '--with-deps', 'chromium'], cwd=runtime, check=True, timeout=900)
    env = dict(os.environ, VP_CHROME_PATH=chrome)
    started = time.monotonic()
    subprocess.run(['node', str(runtime / 'renderer/render.mjs'), str(output.resolve())], cwd=runtime, env=env, check=True, timeout=3600)
    deliveries = []
    for plan in brief['outputs']:
        file = 'video.mp4' if len(brief['outputs']) == 1 else ('video_9x16.mp4' if plan['aspect_ratio'] == '9:16' else 'video_16x9.mp4')
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output / file)], text=True))
        video = [s for s in probe['streams'] if s['codec_type'] == 'video']
        sound = [s for s in probe['streams'] if s['codec_type'] == 'audio']
        if len(video) != 1 or len(sound) != 1: raise ValueError('MP4 must have one video and one audio stream')
        wanted_size = (1080, 1920) if plan['aspect_ratio'] == '9:16' else (1920, 1080)
        if (video[0]['width'], video[0]['height']) != wanted_size or video[0]['codec_name'] != 'h264' or sound[0]['codec_name'] != 'aac':
            raise ValueError('Encoded MP4 stream/size mismatch')
        if abs(float(probe['format']['duration']) - audio['tracks'][plan['language']]['duration']) > .25:
            raise ValueError('Encoded MP4 duration mismatch')
        deliveries.append(dict(plan, file=file, width=video[0]['width'], height=video[0]['height'], duration=float(probe['format']['duration']),
                               video_codec=video[0]['codec_name'], audio_codec=sound[0]['codec_name']))
    files = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'size': p.stat().st_size}
             for p in output.iterdir() if p.is_file() and p.suffix in ('.mp4', '.png', '.srt', '.json') and p.name != 'render-result.json'}
    result = {'request_id': expected_id, 'operation': 'render', 'processing_location': 'colab', 'outputs': deliveries,
              'device': device, 'files': files, 'elapsed_seconds': time.monotonic() - started,
              'processing': ['timeline', 'subtitles', 'layout', 'render', 'encode', 'ffprobe'], 'quality_approval': False}
    (output / 'render-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(output.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ['render-result.json', *files]: archive.write(output / name, name)
    return result
