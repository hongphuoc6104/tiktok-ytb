"""Load local craft instructions explicitly for tool-free generation/review."""
from pathlib import Path

ROLES = {
    'outline': ('vp-script-director', 'vp-visual-director'),
    'detail': ('vp-edit-director', 'vp-audio-director'),
    'content': ('vp-script-director', 'vp-visual-director', 'vp-edit-director', 'vp-audio-director'),
    'media': ('vp-visual-director', 'vp-audio-director', 'vp-edit-director'),
    'video': ('vp-edit-director', 'vp-audio-director', 'vp-visual-director'),
    'registration': ('vp-visual-director',),
}


def vocabulary_brief(brief):
    requirements = brief.get('planning', {}).get('domain_requirements', [])
    text = ' '.join(str(brief.get(k, '')) for k in ('topic', 'goal', 'video_type')).lower()
    return any(x.startswith('Mã mục trong kho từ vựng:') for x in requirements) or any(
        x in text for x in ('từ vựng', 'tu vung', 'vocabulary', 'học từ ', 'word of the day'))


def context(root, stage, brief):
    base = Path(root) / '.agents/skills'
    paths = [base / 'vp-content/references/director-contract.md']
    paths += [base / name / 'SKILL.md' for name in ROLES[stage]]
    if stage in ('outline', 'content') and vocabulary_brief(brief):
        paths.append(base / 'vp-content/references/vocab-pedagogy.md')
    text = '\n\n'.join(f'Local craft guidance ({p.relative_to(base)}):\n{p.read_text()}' for p in paths)
    return text + '\n\n' + tolerance_guidance(root) if stage in TOLERANCE_STAGES else text


# 80/20 brand tolerance: reviewers fail identity/continuity only for these blocking categories.
TOLERANCE_STAGES = ('media', 'video', 'registration')
TOLERANCE_CHECKS = ('character_consistency', 'visual_continuity', 'character_identity')
CORE_DEFECTS = {
    'multiple_bodies_or_shirts': 'two overlapping bodies/torsos/shirts or layered shirts on one character',
    'extra_or_missing_limbs': 'a third arm/leg, stray limb branches, or missing limbs',
    'wrong_shirt_color': 'mascot shirt not light-blue #8CCFE8 short-sleeve T-shirt',
    'head_or_eyes_changed': 'head not round/white or without dark navy outline; anime/pixar/realistic eyes with large whites, irises or glossy pupils (eyebrows, creases, sweat and mouth shapes are NOT this)',
    'realistic_human_anatomy': 'realistic or muscular human body, realistic detailed fingers/toes/nails (simple rounded, white or mitten-like cartoon hands are NOT this)',
    'art_style_changed': 'no longer flat minimal 2D stickman illustration',
    'character_missing_or_replaced': 'required character absent or replaced by a different character or reference identity',
    'meaning_broken': 'the deviation makes the image contradict or fail to show its teaching meaning/action (explain how)',
}
TOLERANCE_FALLBACK = """80/20 brand tolerance policy (built-in summary; .agents/rules/brand_tolerance.md missing).
Core identity (80%, mandatory for CH01 mascot): exactly one stickman body; white round head with bold dark navy outline; simple solid black oval eyes; light-blue #8CCFE8 short-sleeve T-shirt; minimal navy stick arms and legs; flat minimal 2D style.
Core violations (must fail): wrong shirt colour; two overlapping shirts/bodies or extra limbs; realistic/muscular human anatomy or realistic detailed fingers/toes; anime/pixar eyes with large whites or glossy pupils.
Tolerated (20%, must never fail): expressive eyebrows, small forehead creases, sweat drops, any mouth shape, slightly rounded/white/mitten-like hands, rounded/flat/hollow-outline feet in motion, minor prop/furniture/background differences that keep the teaching meaning."""


def tolerance_guidance(root):
    """Binding reviewer policy; the lead-owned rule file wins, the built-in summary is only a fallback."""
    rule = Path(root) / '.agents/rules/brand_tolerance.md'
    policy = f'Brand tolerance rule ({rule.name}):\n{rule.read_text()}' if rule.is_file() else TOLERANCE_FALLBACK
    categories = '; '.join(f'{k} = {v}' for k, v in CORE_DEFECTS.items())
    return (policy + '\n\nBinding review directive for ' + ', '.join(TOLERANCE_CHECKS) + ': these checks fail ONLY when '
            'blocking_defects is non-empty. A blocking defect is a core-identity violation or a defect that breaks the '
            f'image meaning, with exactly one category: {categories}. List every tolerated (20%) deviation you notice in '
            'tolerated_deviations; tolerated details never go in blocking_defects and never make a check fail. Variation of '
            'tolerated details between images (eyebrows in one frame but not the next, hand/foot rendering, mouth, sweat '
            'drops, minor props/background) is not a visual_continuity failure. Earlier repair instructions forbidding '
            'tolerated details (e.g. "NO eyebrows", "feet must be solid ovals") do not override this policy. In video review, '
            'identity drift inside any visual check follows the same rule: only blocking categories fail. Do not weaken '
            'text, relevance, audio or pronunciation criteria because of this policy.')


REVIEW_GUIDANCE = {
    'content': 'Hook promises a specific benefit and has a payoff. Story links are causal or purposeful, not merely scene labels. Learning examples match the selected sense and learner level. Practice includes a feasible response and feedback; verify requested holds are declared. Do not impose vocabulary criteria on unrelated topics.',
    'media': 'Inspect every image against the actual mascot reference and adjacent frames, judging identity by the 80/20 brand tolerance policy. Test target action versus thematic illustration, exact teaching text and space for captions. Listen to each full language track, including mixed-language examples, stress and real learner response intervals. Intent fields are not proof of performed emotion.',
    'video': 'Watch full delivery files and listen throughout. Check opening/payoff, reading time, grammatical caption groups, punctuation-only cues, phone-size legibility, actual visual/word synchronization, identity drift, image crops, and learner response holds. Technical audit warnings require judgment, not automatic pass or fail.',
    'registration': 'Compare the actual reference and registered image, including forbidden added anatomy, by the 80/20 brand tolerance policy; IDs and hashes cannot prove visual identity.',
}


def review_checklist(stage):
    return {
        'content': 'Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có.',
        'media': 'Đạo diễn: xem từng ảnh và đối chiếu mascot; nghe đủ WAV; kiểm tra phát âm và khoảng chờ; chữ đúng; nhịp nội suy phải đối chiếu âm thanh thật.',
        'video': 'Đạo diễn: xem/nghe toàn bộ MP4; đọc thử ở kích thước điện thoại; không cue dấu câu; cắt cảnh đúng ý; không mất chữ; có lượt thực hành và payoff.',
    }[stage] + ' Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.'
