"""Cheap local ranking of generated variants (no model, no network).

Checks per variant: aspect/size, blank or near-uniform frames, text-like
regions (the channel draws all text in Remotion, so letters in the image are a
defect), and perceptual-hash similarity to the references (mascot, based_on
still / clip start frame) as a continuity signal. The best score is the default
pick; the dashboard can override it.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat

RATIOS = {'16:9': 16 / 9, '9:16': 9 / 16}


def dhash(img, size=8):
    g = img.convert('L').resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for row in range(size):
        for col in range(size):
            left, right = px[row * (size + 1) + col], px[row * (size + 1) + col + 1]
            bits = (bits << 1) | (left > right)
    return bits


def similarity(a, b):
    """1.0 = identical dHash, 0.0 = all 64 bits differ."""
    return 1 - bin(a ^ b).count('1') / 64


def blankness(img):
    """Standard deviation of luminance; near 0 means an empty/flat frame."""
    return ImageStat.Stat(img.convert('L').resize((128, 128))).stddev[0]


def text_likeness(img):
    """Fraction of the frame covered by text-like runs: many short, dense edge
    blocks lined up horizontally (letters), as opposed to long doodle strokes."""
    g = img.convert('L').resize((256, 144) if img.width >= img.height else (144, 256))
    edges = g.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 60 else 0)
    w, h = edges.size
    bs = 8
    cols, rows = w // bs, h // bs
    dense = [[False] * cols for _ in range(rows)]
    px = edges.load()
    for r in range(rows):
        for c in range(cols):
            on = sum(1 for y in range(r * bs, r * bs + bs) for x in range(c * bs, c * bs + bs) if px[x, y])
            # letters give many edge pixels per small block; strokes give few
            dense[r][c] = 0.18 <= on / (bs * bs) <= 0.6
    hits = 0
    for r in range(rows):
        run = 0
        for c in range(cols + 1):
            if c < cols and dense[r][c]:
                run += 1
                continue
            if run >= 4:
                hits += run
            run = 0
    return hits / max(1, rows * cols)


def frame_of(path):
    """A still for scoring: the image itself, or a clip frame at 1 s (needs ffmpeg)."""
    path = Path(path)
    if path.suffix.lower() not in ('.mp4', '.mov', '.webm'):
        return Image.open(path)
    if not shutil.which('ffmpeg'):
        return None
    out = Path(tempfile.mkstemp(suffix='.png')[1])
    try:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(path), '-frames:v', '1', str(out)],
                       check=True, timeout=60)
        with Image.open(out) as im:
            return im.copy()
    except (subprocess.SubprocessError, OSError):
        return None
    finally:
        out.unlink(missing_ok=True)


def score(path, ratio, refs=()):
    """{'score', 'checks'} for one variant. Higher is better; negative = defective."""
    img = frame_of(path)
    if img is None:
        return {'path': str(path), 'score': 0.0, 'checks': {'scored': False}}
    with img:
        w, h = img.size
        checks = {'width': w, 'height': h}
        s = 1.0
        ratio_error = abs(w / h - RATIOS.get(ratio, w / h)) / RATIOS.get(ratio, 1)
        checks['ratio_error'] = round(ratio_error, 4)
        if ratio_error > 0.05:
            s -= 1.0
        if min(w, h) < 360:
            s -= 0.5
        std = blankness(img)
        checks['luma_std'] = round(std, 2)
        if std < 6:
            s -= 1.5
        text = text_likeness(img)
        checks['text_likeness'] = round(text, 4)
        s -= min(1.0, text * 4)
        own = dhash(img)
        sims = []
        for ref in refs or ():
            try:
                with Image.open(ref) as r:
                    sims.append(similarity(own, dhash(r)))
            except OSError:
                continue
        if sims:
            checks['reference_similarity'] = [round(x, 3) for x in sims]
            s += 0.3 * max(sims)
    return {'path': str(path), 'score': round(s, 4), 'checks': checks}


def rank(paths, ratio, refs=()):
    """Variants best-first (stable for ties)."""
    scored = [dict(score(p, ratio, refs), index=i) for i, p in enumerate(paths)]
    return sorted(scored, key=lambda x: (-x['score'], x['index']))
