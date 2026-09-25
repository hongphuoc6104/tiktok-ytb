"""GD5 'Dong goi': thumbnail + metadata + description written to video/<job>/.

Runs only when content.packaging is present (tiensu channel). Vocab/legacy jobs
have no `packaging` field on their content payload, so build() is a no-op for
them -- this module changes nothing about existing pipelines.

Called from workflow.publish_videos right after the approved MP4(s) are copied
into video/<job>/. See sys/docs/tien-su-plan.md section 8 ("Dong goi") for the
binding data contract this follows.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageStat

from pilot import Blocked, write

THUMB_W, THUMB_H = 1280, 720
YELLOW = (255, 225, 77)   # #FFE14D
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Bold, Vietnamese-capable font. Prefer the vendored OFL font (works on any
# machine); fall back to system fonts confirmed (via fc-list) to cover every
# Vietnamese diacritic on the dev box.
FONT_DIR = Path(__file__).resolve().parent / 'assets' / 'fonts'
FONT_CANDIDATES = [
    FONT_DIR / 'BeVietnamPro-ExtraBold.ttf',
    Path('/usr/share/fonts/truetype/noto/NotoSans-Black.ttf'),
    Path('/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf'),
    Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
]


def thumbnail_font_path():
    for candidate in FONT_CANDIDATES:
        if candidate.is_file():
            return str(candidate)
    raise Blocked('No bold Vietnamese-capable font found; vendor one under sys/assets/fonts/ (see tien-su-plan.md GD5)')


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------

def _fit_16x9(img):
    img = ImageOps.exif_transpose(img).convert('RGB')
    w, h = img.size
    target = THUMB_W / THUMB_H
    cur = w / h
    if cur > target:
        new_w = round(h * target)
        x0 = (w - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, h))
    elif cur < target:
        new_h = round(w / target)
        y0 = (h - new_h) // 2
        img = img.crop((0, y0, w, y0 + new_h))
    return img.resize((THUMB_W, THUMB_H), Image.LANCZOS)


def _region_flatness(img, box):
    region = img.crop(box).convert('L')
    return ImageStat.Stat(region).stddev[0]


def _ranked_sides(img):
    """Least-detail (flattest) band first == where text covers least character.

    Simple heuristic (explicitly allowed by the packaging spec): grayscale
    stddev of the top band vs. the left/right bands; lower stddev usually
    means flat background rather than a busy, detailed character/subject.
    """
    w, h = img.size
    scores = {
        'top': _region_flatness(img, (0, 0, w, round(h * 0.40))),
        'left': _region_flatness(img, (0, 0, round(w * 0.40), h)),
        'right': _region_flatness(img, (round(w * 0.60), 0, w, h)),
    }
    return sorted(scores, key=scores.get)


def _wrap_to_width(words, font, draw, stroke, max_width, max_lines):
    lines, cur = [], []
    for word in words:
        candidate = cur + [word]
        width = draw.textbbox((0, 0), ' '.join(candidate), font=font, stroke_width=stroke)[2]
        if width <= max_width or not cur:
            cur = candidate
        else:
            lines.append(' '.join(cur))
            cur = [word]
            if len(lines) >= max_lines:
                return None
    if cur:
        lines.append(' '.join(cur))
    return lines if len(lines) <= max_lines else None


def _fit_text(text, font_path, box_w, box_h, max_lines=2):
    """Largest font (any Vietnamese-capable bold face) whose wrapped block
    still fits box_w x box_h -- in practice this lands the text near the top
    of its allowed width band, i.e. ~45-60% of the thumbnail width."""
    words = text.split()
    scratch = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    for size in range(300, 30, -6):
        font = ImageFont.truetype(font_path, size)
        stroke = max(3, size // 14)
        lines = _wrap_to_width(words, font, scratch, stroke, box_w, max_lines)
        if lines is None:
            continue
        joined = '\n'.join(lines)
        bbox = scratch.multiline_textbbox((0, 0), joined, font=font, stroke_width=stroke, align='center')
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= box_w and h <= box_h:
            return font, lines, stroke
    font = ImageFont.truetype(font_path, 30)
    return font, [text], 4


def _compose_thumbnail(base, text, side, fill_color):
    img = _fit_16x9(base)
    w, h = img.size
    text = ' '.join(text.upper().split())
    box_w, box_h = round(w * 0.60), round(h * 0.46)
    font, lines, stroke = _fit_text(text, thumbnail_font_path(), box_w, box_h)
    joined = '\n'.join(lines)

    if side == 'top':
        pos, anchor, align = (w // 2, round(h * 0.08)), 'ma', 'center'
    elif side == 'left':
        pos, anchor, align = (round(w * 0.06), h // 2), 'lm', 'left'
    else:
        pos, anchor, align = (round(w * 0.94), h // 2), 'rm', 'right'

    # Soft shadow: blurred, offset, semi-transparent copy of the same glyphs.
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    offset = max(4, font.size // 14)
    sdraw.multiline_text((pos[0] + offset, pos[1] + offset), joined, font=font, fill=(0, 0, 0, 170),
                          stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 170), anchor=anchor, align=align)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(3, font.size // 20)))
    img = Image.alpha_composite(img.convert('RGBA'), shadow).convert('RGB')

    # Crisp bold text: thick black outline, requested fill on top.
    draw = ImageDraw.Draw(img)
    draw.multiline_text(pos, joined, font=font, fill=fill_color, stroke_width=stroke, stroke_fill=BLACK,
                         anchor=anchor, align=align)
    return img


def write_thumbnails(source_path, text, folder):
    """Writes thumbnail.jpg (yellow), thumbnail-b.jpg (white, same side) and
    thumbnail-c.jpg (yellow, the other side) into folder. Returns their paths."""
    with Image.open(source_path) as im:
        base = im.copy()
    sides = _ranked_sides(base)
    primary, alt = sides[0], sides[1]
    variants = [
        ('thumbnail.jpg', primary, YELLOW),
        ('thumbnail-b.jpg', primary, WHITE),
        ('thumbnail-c.jpg', alt, YELLOW),
    ]
    paths = []
    for name, side, color in variants:
        out = _compose_thumbnail(base, text, side, color)
        target = folder / name
        out.save(target, 'JPEG', quality=92)
        paths.append(target)
    return paths


# ---------------------------------------------------------------------------
# Chapters / metadata / description
# ---------------------------------------------------------------------------

def _mmss(seconds):
    total = max(0, round(seconds))
    return f'{total // 60}:{total % 60:02d}'


def _chapter_candidates(content, audio):
    first_start = {}
    for seg in audio.get('segments', []):
        sid = seg.get('scene_id')
        if sid is not None and sid not in first_start:
            first_start[sid] = float(seg.get('start', 0.0))
    out = []
    for scene in content.get('scenes', []):
        sid = scene.get('id')
        if sid not in first_start:
            continue
        label = scene.get('chapter') or scene.get('purpose') or sid
        out.append({'scene_id': sid, 'start_seconds': round(first_start[sid], 2), 'label': label})
    out.sort(key=lambda c: c['start_seconds'])
    return out


def build_chapters(content, audio, min_gap=10.0):
    """Real per-scene start times from the final narration WAV timeline
    (audio payload's segments); first chapter is always 0:00. Chapters closer
    together than min_gap are dropped (never the first) to keep the YouTube
    chapter list valid."""
    candidates = _chapter_candidates(content, audio)
    if not candidates:
        return []
    kept = [dict(candidates[0], start_seconds=0.0)]
    for c in candidates[1:]:
        if c['start_seconds'] - kept[-1]['start_seconds'] >= min_gap:
            kept.append(c)
    return kept


def _sources(brief_doc, content):
    brief_sources = (brief_doc or {}).get('sources', [])
    used_ids = {c.get('source_id') for c in content.get('claims', []) if c.get('source_id')}
    sources = [s for s in brief_sources if s.get('id') in used_ids] if used_ids else list(brief_sources)
    if used_ids and not sources:
        sources = list(brief_sources)
    return [{'id': s.get('id'), 'title': s.get('title'), 'reference': s.get('reference')} for s in sources]


NOTE = ('Ghi chú: hình minh họa trong video là tranh vẽ cách điệu, có sự hỗ trợ của AI, '
        'không phải ảnh chụp hay tư liệu lịch sử xác thực.')


def build_description(hook, chapters, sources):
    lines = [hook.strip(), '']
    for i, c in enumerate(chapters, 1):
        lines.append(f"{_mmss(c['start_seconds'])} Chương {i}: {c['label']}")
    lines.append('')
    lines.append('Nguồn tham khảo:')
    if sources:
        for s in sources:
            ref = f" — {s['reference']}" if s.get('reference') else ''
            lines.append(f"- {s.get('title') or s.get('id')}{ref}")
    else:
        lines.append('- (chưa khai báo nguồn)')
    lines.append('')
    lines.append(NOTE)
    return '\n'.join(lines) + '\n'


def build_metadata(packaging, chapters, sources, duration, description):
    titles = list(packaging.get('titles') or [])
    return {
        'titles': titles,
        'title': titles[0] if titles else '',
        'description': description,
        'chapters': chapters,
        'tags': list(packaging.get('tags') or []),
        'sources': sources,
        'duration': duration,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _thumbnail_source(p, job, images_payload, image_id):
    items = images_payload.get('items', [])
    match = next((it for it in items if it.get('image_id') == image_id), None)
    if match is None:
        match = next((it for it in items if it.get('scene_id') == image_id), None)
    if match is None:
        raise Blocked(f'packaging.thumbnail.image_id "{image_id}" khong khop anh still da duyet nao')
    return p.path(job, match['path'])


def build(p, job, folder):
    """Called from workflow.publish_videos with folder = video/<job>/ (already
    created). No-op (returns None) when content has no `packaging` field."""
    content = p.payload(job, 'content')
    pkg = content.get('packaging')
    if not pkg:
        return None
    images = p.payload(job, 'images')
    audio = p.payload(job, 'audio')
    try:
        render = p.payload(job, 'render')
    except Blocked:
        render = {}
    brief = p.brief(job)
    brief_doc = brief[0] if brief else {}

    folder.mkdir(parents=True, exist_ok=True)

    thumb = pkg.get('thumbnail') or {}
    source = _thumbnail_source(p, job, images, thumb.get('image_id'))
    thumb_paths = write_thumbnails(source, thumb.get('text', ''), folder)

    chapters = build_chapters(content, audio)
    sources = _sources(brief_doc, content)
    duration = render.get('duration', audio.get('duration', 0.0))
    description = build_description(pkg.get('hook', ''), chapters, sources)
    metadata = build_metadata(pkg, chapters, sources, duration, description)

    write(folder / 'metadata.json', metadata)
    (folder / 'description.txt').write_text(description, encoding='utf-8')

    return {
        'thumbnails': [str(x) for x in thumb_paths],
        'metadata': str(folder / 'metadata.json'),
        'description': str(folder / 'description.txt'),
    }
