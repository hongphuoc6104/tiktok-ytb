"""Language, aspect, captions and voice are independent delivery choices.

Missing outputs preserves v3 ratio routing except explicitly English briefs.
New jobs freeze explicit outputs; legacy snapshots are never rewritten here.
"""
import math


def outputs(brief):
    ratio = brief.get('aspect_ratio', '9:16')
    expected = ['9:16', '16:9'] if ratio == 'dual' else [ratio]
    plans = brief.get('outputs')
    if plans is None:
        english = brief.get('language', '').strip().lower() in ('en', 'english')
        plans = [{'aspect_ratio': aspect,
                  'language': 'en' if english or aspect == '16:9' else 'vi',
                  'subtitles': aspect == '9:16'} for aspect in expected]
    if not isinstance(plans, list) or not plans:
        raise ValueError('OUTPUT_CONTRACT: nonempty outputs required')
    if any(not isinstance(plan, dict) for plan in plans):
        raise ValueError('OUTPUT_CONTRACT: each output must be an object')
    if [x.get('aspect_ratio') for x in plans] != expected:
        raise ValueError('OUTPUT_CONTRACT: outputs must match requested aspects in order')
    for plan in plans:
        if plan.get('language') not in ('vi', 'en') or type(plan.get('subtitles')) is not bool:
            raise ValueError('OUTPUT_CONTRACT: language and subtitles must be explicit')
        if 'speed' in plan:
            speed = plan['speed']
            if isinstance(speed, bool) or not isinstance(speed, (int, float)) or not math.isfinite(speed) or speed <= 0:
                raise ValueError('OUTPUT_CONTRACT: speed must be positive and finite')
        if 'voice' in plan and (not isinstance(plan['voice'], str) or not plan['voice'].strip()):
            raise ValueError('OUTPUT_CONTRACT: voice must be a nonempty name')
    return [dict(x) for x in plans]


def languages(brief):
    return list(dict.fromkeys(x['language'] for x in outputs(brief)))


def primary_language(brief):
    return languages(brief)[0]


def narration(scene, language):
    return scene.get('narration_en' if language == 'en' else 'narration', '')


def voice_settings(brief, language, config):
    selected = [x for x in outputs(brief) if x['language'] == language]
    values = {(x.get('voice'), x.get('speed')) for x in selected}
    if len(values) > 1:
        raise ValueError('OUTPUT_CONTRACT: one language track cannot have conflicting voice/rate')
    plan = selected[0]
    return {'voice': plan.get('voice', config.get('en_voice' if language == 'en' else 'tts_voice')),
            'speed': plan.get('speed', config.get('en_speed', 1.) if language == 'en' else config.get('tts_speed', 1.))}
