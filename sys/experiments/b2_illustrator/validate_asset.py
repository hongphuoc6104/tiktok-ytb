"""Read-only verification of downloaded bytes, never trusts a UI extension."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def validate_asset(file, ratio, declared_mime=None):
    if ratio not in ('16:9', '9:16'):
        raise ValueError('Unsupported ratio')
    file = Path(file).resolve(strict=True)
    with Image.open(file) as image:
        fmt = image.format
        image.verify()
    allowed = {'PNG': ('image/png', '.png'), 'JPEG': ('image/jpeg', '.jpg'), 'WEBP': ('image/webp', '.webp')}
    if fmt not in allowed:
        raise ValueError('Unsupported actual image format')
    with Image.open(file) as image:
        image.load()
        width, height = image.size
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Animated image not accepted')
    mime, extension = allowed[fmt]
    if declared_mime and declared_mime != mime:
        raise ValueError('Declared MIME differs from actual bytes')
    numerator, denominator = map(int, ratio.split(':'))
    if abs(width / height - numerator / denominator) > .04:
        raise ValueError('Actual aspect ratio differs from request')
    with file.open('rb') as stream:
        if hasattr(hashlib, 'file_digest'):
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        else:
            h = hashlib.sha256()
            while chunk := stream.read(65536):
                h.update(chunk)
            digest = h.hexdigest()
    return {'path': str(file), 'sha256': digest,
            'mimeType': mime, 'extension': extension, 'width': width, 'height': height,
            'ratio': ratio, 'technicalValidation': 'pass', 'visualReview': 'pending'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--ratio', required=True, choices=['16:9', '9:16'])
    parser.add_argument('--declared-mime')
    args = parser.parse_args()
    print(json.dumps(validate_asset(args.file, args.ratio, args.declared_mime), indent=2))
