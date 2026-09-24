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
    return '\n\n'.join(f'Local craft guidance ({p.relative_to(base)}):\n{p.read_text()}' for p in paths)


REVIEW_GUIDANCE = {
    'content': 'Hook promises a specific benefit and has a payoff. Story links are causal or purposeful, not merely scene labels. Learning examples match the selected sense and learner level. Practice includes a feasible response and feedback; verify requested holds are declared. Do not impose vocabulary criteria on unrelated topics.',
    'media': 'Inspect every image against the actual mascot reference and adjacent frames. Test target action versus thematic illustration, exact teaching text and space for captions. Listen to each full language track, including mixed-language examples, stress and real learner response intervals. Intent fields are not proof of performed emotion.',
    'video': 'Watch full delivery files and listen throughout. Check opening/payoff, reading time, grammatical caption groups, punctuation-only cues, phone-size legibility, actual visual/word synchronization, identity drift, image crops, and learner response holds. Technical audit warnings require judgment, not automatic pass or fail.',
    'registration': 'Compare the actual reference and registered image, including forbidden added anatomy; IDs and hashes cannot prove visual identity.',
}


def review_checklist(stage):
    return {
        'content': 'Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có.',
        'media': 'Đạo diễn: xem từng ảnh và đối chiếu mascot; nghe đủ WAV; kiểm tra phát âm và khoảng chờ; chữ đúng; nhịp nội suy phải đối chiếu âm thanh thật.',
        'video': 'Đạo diễn: xem/nghe toàn bộ MP4; đọc thử ở kích thước điện thoại; không cue dấu câu; cắt cảnh đúng ý; không mất chữ; có lượt thực hành và payoff.',
    }[stage] + ' Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.'
