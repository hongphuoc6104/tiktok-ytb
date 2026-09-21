"""User-provided templates; provider execution still goes through image-only gates."""
from pilot import Blocked

TEMPLATES = {
    'image': 'Generate one separate 16:9 image for every scene prompt provided below. Produce all images in a single batch and in sequence, following each prompt exactly and maintaining consistent visual quality throughout. Scene prompts: [INSERT ALL SCENE PROMPTS HERE]',
    'text-to-video': 'Generate one separate 16:9 video for every scene prompt provided below. Produce all video in a single batch and in sequence, following each prompt exactly and maintaining consistent visual quality throughout. Scene prompts: [INSERT ALL SCENE PROMPTS HERE]',
    'image-to-video': 'Generate one separate 16:9 video for every scene prompt provided below by taking the reference from all the scene images attached alongwith. Produce all video in a single batch and in sequence, following each prompt exactly and maintaining consistent visual quality throughout. Scene prompts: [INSERT ALL SCENE PROMPTS HERE]',
}


def image_prompt(scene_prompt, ratio='9:16'):
    """Explicit pilot adaptation, not the original tested 16:9 batch template."""
    if ratio not in ('9:16', '16:9'):
        raise Blocked('Unsupported image ratio')
    wide_rule = ('The 16:9 frame is wider than the 9:16 version of this same scene: extend the '
                 'environment on both sides with details consistent with the setting, so the wider '
                 'canvas is filled rather than cropped. Keep the same characters, action, central '
                 'composition and text placement as the 9:16 version. Do not add any text, numbers, '
                 'labels, or logos anywhere in the extended sides. '
                 ) if ratio == '16:9' else ''
    return (f'Generate one separate {ratio} image for the scene prompt provided below. '
            'Follow the prompt exactly and maintain consistent visual quality with the approved character references. '
            + wide_rule +
            'Scene prompt: ' + scene_prompt)


def batch_prompt(kind, prompts, ratio='16:9'):
    if kind not in ('image', 'text-to-video', 'image-to-video'):
        raise Blocked(f'Unsupported template kind: {kind}')
    if ratio not in ('9:16', '16:9') or not prompts or any(not isinstance(x, str) or not x.strip() for x in prompts):
        raise Blocked('Template requires 9:16 or 16:9 and nonempty scene prompts')
    return TEMPLATES[kind].replace('16:9', ratio).replace('[INSERT ALL SCENE PROMPTS HERE]', '\n'.join(prompts))
