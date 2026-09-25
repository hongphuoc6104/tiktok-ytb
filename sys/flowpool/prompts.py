"""Prompt builder for FlowPool: channel style + mascot identity + scene + negatives.

The pipeline's own prompt (prompt_templates / story_plan, kept unchanged) is the
scene part; this module wraps it with the channel's visual rules so every
image and clip looks the same, and records what was actually sent.
"""
import json
from pathlib import Path

HOUSE_STYLE = ('Bold clean outlines, flat muted earth-tone palette, one clear focal subject, '
               'uncluttered composition with empty margins so labels can be overlaid later.')
NEGATIVE = ('Do not draw any text, letters, numbers, captions, labels, logos or watermarks. '
            'No photorealism, no 3D render, no heavy gradients, no extra characters beyond those described.')
CLIP_RULES = ('Same flat ink doodle style as the start frame, same characters and background, '
              'no new characters, no text or letters, no camera cuts; subtle, smooth motion. Muted, no audio needed.')
CHANNEL_FILES = {'tiensu': 'tiensu/channel.json'}


def channel_style(root, channel):
    """The channel's `style` line (e.g. tiensu/channel.json), or None."""
    rel = CHANNEL_FILES.get(channel or '')
    if not rel:
        return None
    try:
        return json.loads((Path(root) / rel).read_text(encoding='utf-8')).get('style')
    except (OSError, ValueError):
        return None


def mascot_lines(mascot):
    """Identity lines from the mascot's character.json (via characters.mascot_for)."""
    if not mascot:
        return None
    ident = mascot.get('appearance') or {}
    if not ident:
        return 'Main character: keep exactly the design of the attached character reference.'
    parts = '; '.join(f'{k}: {v}' for k, v in ident.items())
    return f'Main character (attached reference, keep identity exactly): {parts}.'


def _ratio_line(ratio):
    return ('Wide 16:9 landscape frame.' if ratio == '16:9' else 'Tall 9:16 portrait frame.')


def image_prompt(scene, ratio='16:9', style=None, mascot=None, has_base=False):
    lines = [f'Style: {style}' if style else None, HOUSE_STYLE, _ratio_line(ratio), mascot_lines(mascot),
             'Keep the camera angle, background and props of the attached base scene image.' if has_base else None,
             'Scene:', scene.strip(), NEGATIVE]
    return '\n'.join(x for x in lines if x)


def clip_prompt(motion, seconds=8, style=None):
    """Veo frames-to-video prompt: short camera + subject motion, style locked to the start frame."""
    motion = ' '.join(motion.split())
    lines = [f'{seconds}-second shot animating the attached start frame.', f'Motion: {motion}',
             f'Style: {style}' if style else None, CLIP_RULES]
    return '\n'.join(x for x in lines if x)
