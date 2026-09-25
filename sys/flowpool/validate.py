"""Technical validation of downloaded outputs (decoded bytes, not metadata)."""
import json
import shutil
import subprocess

from .journal import sha256_file

RATIOS = {'16:9': 16 / 9, '9:16': 9 / 16}


class ValidationError(Exception):
    pass


def _ratio_ok(width, height, ratio, tol=0.05):
    return width and height and abs(width / height - RATIOS[ratio]) <= tol


def validate_image(path, ratio):
    from PIL import Image
    try:
        with Image.open(path) as im:
            im.load()
            w, h = im.size
    except Exception as ex:
        raise ValidationError(f'IMAGE_DECODE_FAILED: {path}: {ex}')
    if not _ratio_ok(w, h, ratio):
        raise ValidationError(f'IMAGE_RATIO: {w}x{h} is not {ratio}')
    if min(w, h) < 360:
        raise ValidationError(f'IMAGE_TOO_SMALL: {w}x{h}')
    return {'width': w, 'height': h}


def validate_clip(path, ratio, seconds=8, tolerance=2.5):
    with open(path, 'rb') as f:
        head = f.read(12)
    if len(head) < 12 or head[4:8] != b'ftyp':
        raise ValidationError(f'CLIP_NOT_MP4: {path}')
    info = {'container': 'mp4'}
    if shutil.which('ffprobe'):
        try:
            data = json.loads(subprocess.check_output(
                ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], timeout=60))
        except (subprocess.SubprocessError, ValueError) as ex:
            raise ValidationError(f'CLIP_PROBE_FAILED: {ex}')
        video = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        if not video:
            raise ValidationError('CLIP_NO_VIDEO_STREAM')
        duration = float(data.get('format', {}).get('duration') or video.get('duration') or 0)
        if abs(duration - seconds) > tolerance:
            raise ValidationError(f'CLIP_DURATION: {duration:.2f}s, expected about {seconds}s')
        w, h = int(video.get('width') or 0), int(video.get('height') or 0)
        if not _ratio_ok(w, h, ratio):
            raise ValidationError(f'CLIP_RATIO: {w}x{h} is not {ratio}')
        info.update(width=w, height=h, duration=duration)
    return info


def validate_output(path, kind, ratio, seconds=8):
    info = validate_image(path, ratio) if kind == 'image' else validate_clip(path, ratio, seconds)
    info.update(path=str(path), sha256=sha256_file(path))
    return info
