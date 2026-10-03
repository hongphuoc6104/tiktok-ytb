"""Desktop control for explicit output contracts; all audio processing is remote."""
import copy
import json
from pathlib import Path

from output_contract import languages, primary_language, narration, voice_settings


def produce(pilot, job, out):
    from pilot import Blocked, read, write
    from adapters import config, retakes, scene_tail, DEFAULT_PAUSE, english_parts, is_english
    from colab_bridge.client import Client, ColabError, enabled
    from colab_bridge.protocol import build_request

    brief = pilot.brief(job)[0]
    content = pilot.payload(job, 'content')
    cfg = copy.deepcopy(config(pilot))
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        cfg['colab_tts']['management_session'] = selection
        selected = selection.get('runtime_bindings', {}).get('colab', {}).get('account') or selection.get('defaults', {}).get('colab')
        if selected:
            cfg['colab_tts']['account'] = selected.removeprefix('colab:')
    if not enabled(cfg):
        raise Blocked('COLAB_REQUIRED: explicit output jobs never fall back to local TTS')
    requested = languages(brief)
    primary = primary_language(brief)
    for language in requested:
        settings = voice_settings(brief, language, cfg)
        # Resolve the chosen identity; a default for a different voice cannot win.
        matches = []
        for path in (pilot.root / 'assets/voices').glob('*/profile.json'):
            profile = read(path)
            if profile.get('language') == language and profile.get('voice', '').casefold() == settings['voice'].casefold():
                matches.append((path, profile))
        if len(matches) != 1:
            raise Blocked('VOICE_REFERENCE_REQUIRED: missing or ambiguous ' + settings['voice'])
        path, profile = matches[0]
        cfg['colab_tts']['voices'][language] = str(path.relative_to(pilot.root))
        cfg['en_voice' if language == 'en' else 'tts_voice'] = profile['voice']
        cfg['en_speed' if language == 'en' else 'tts_speed'] = settings['speed']
    takes = retakes(pilot, job)
    gaps = cfg.get('tts_pause', DEFAULT_PAUSE)
    scenes = []
    for i, scene in enumerate(content['scenes']):
        text = narration(scene, primary)
        if not text.strip():
            raise Blocked('NARRATION_REQUIRED: ' + primary + '/' + scene['id'])
        item = {'scene_id': scene['id'], 'narration': text, 'texts': [text],
                'retake': takes.get(scene['id'], 0), 'gaps': [],
                'tail': scene_tail(scene, primary, gaps, i == len(content['scenes']) - 1)}
        if primary == 'vi':
            words = [v['word'] for v in scene.get('vocabulary', []) if is_english(v.get('word', ''))]
            parts = english_parts(text, words)
            if any(x['lang'] == 'en' for x in parts):
                item['parts'] = [parts]
        scenes.append(item)
    secondary = []
    if primary != 'en' and 'en' in requested:
        secondary = [{'scene_id': scene['id'], 'narration_en': narration(scene, 'en'),
                      'retake': takes.get(scene['id'], 0),
                      'tail': scene_tail(scene, 'en', gaps, i == len(content['scenes']) - 1)}
                     for i, scene in enumerate(content['scenes'])]
    secondary_vi = []
    if primary == 'en' and 'vi' in requested:
        secondary_vi = [{'scene_id': scene['id'], 'language': 'vi', 'text': narration(scene, 'vi'),
                         'retake': takes.get(scene['id'], 0),
                         'tail': scene_tail(scene, 'vi', gaps, i == len(content['scenes']) - 1)}
                        for i,scene in enumerate(content['scenes'])]
    try:
        request = build_request(pilot.root, cfg, scenes, secondary,
                                primary_language=primary, assemble=True, secondary_scenes=secondary_vi)
        write(out / 'request-colab.json', request)
        import execution
        guard = (lambda: execution.before_submit(pilot, job)) if execution.is_job(pilot, job) else None
        Client(pilot.root, cfg).synthesize(request, out, pilot.job(job) / 'cache/colab-tts', before_submit=guard)
        report = read(out / 'audio-result.json')
        if report.get('processing_location') != 'colab' or report.get('language') != primary:
            raise Blocked('COLAB_ASSEMBLY_REQUIRED: prepared remote result missing')
    except (ColabError, ValueError, OSError) as ex:
        raise Blocked(str(ex)) from ex
    payload = report['payload']

    def asset(name):
        if Path(name).name != name:
            raise Blocked('Unsafe remote audio path')
        return str((out / name).relative_to(pilot.job(job)))

    def convert(track):
        for key in ('wav', 'srt', 'generation_report'):
            if key in track:
                track[key] = asset(track[key])
        for field in ('segments', 'scenes'):
            for item in track.get(field, []):
                item['path'] = asset(item['path'])

    convert(payload)
    for track in payload['tracks'].values():
        convert(track)
    if payload.get('en'):
        convert(payload['en'])
    return payload


def render(pilot, job, out):
    """Control/collect only; remote worker owns timeline, captions, media and encoding."""
    from pilot import Blocked, read, write
    from adapters import config
    from colab_bridge.client import Client, ColabError, enabled
    from colab_bridge.job_protocol import build_render_request
    cfg = copy.deepcopy(config(pilot))
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        cfg['colab_tts']['management_session'] = selection
        selected = selection.get('runtime_bindings', {}).get('colab', {}).get('account') or selection.get('defaults', {}).get('colab')
        if selected:
            cfg['colab_tts']['account'] = selected.removeprefix('colab:')
    if not enabled(cfg): raise Blocked('COLAB_REQUIRED: explicit outputs never render locally')
    try:
        request = build_render_request(pilot.root, pilot.brief(job)[0], pilot.payload(job, 'content'),
                                       pilot.payload(job, 'images'), pilot.payload(job, 'audio'),
                                       lambda name: pilot.path(job, name))
        write(out / 'request-colab-render.json', request)
        import execution
        guard = (lambda: execution.before_submit(pilot, job)) if execution.is_job(pilot, job) else None
        Client(pilot.root, cfg).render(request, out, pilot.job(job) / 'cache/colab-render', before_submit=guard)
        report = read(out / 'render-result.json')
    except (ColabError, ValueError, OSError) as ex: raise Blocked(str(ex)) from ex
    def path(name): return str((out / name).relative_to(pilot.job(job)))
    result = {'video': path('video.mp4'), 'stills': [path(name) for name in report['files'] if name.endswith('.png')],
              'layout_report': path('layout.json'), 'editorial_report': path('editorial-audit.json'),
              'remote_report': path('render-result.json'), 'language': report['outputs'][0]['language'],
              'duration': report['outputs'][0]['duration']}
    for delivery in report['outputs']:
        if len(report['outputs']) > 1:
            result['video_9x16' if delivery['aspect_ratio'] == '9:16' else 'video_16x9'] = path(delivery['file'])
    return result
