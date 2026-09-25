"""Deterministic local character board for Flow's two ingredient slots.

The board is only a prompt ingredient. Source images remain the approved,
hash-checked outputs of this job; the board is never presented as media.
"""
import hashlib
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

from pilot import digest


def ingredient(paths, directory):
    paths = [Path(p).resolve() for p in paths]
    if not paths:
        raise ValueError('CHARACTER_REFERENCE_REQUIRED: no character source images')
    shas = []
    for source in paths:
        if not source.is_file():
            raise ValueError(f'CHARACTER_REFERENCE_MISSING: {source}')
        try:
            with Image.open(source) as image:
                image.verify()
        except (OSError, ValueError) as ex:
            raise ValueError(f'CHARACTER_REFERENCE_INVALID: {source}: {ex}') from ex
        shas.append(digest(source))
    if len(paths) == 1:
        return str(paths[0]), shas

    key = hashlib.sha256('|'.join(shas).encode('ascii')).hexdigest()[:24]
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / f'characters-{key}.png'
    tile = (640, 720)
    board = Image.new('RGB', (tile[0] * len(paths), tile[1]), 'white')
    for index, source in enumerate(paths):
        with Image.open(source) as raw:
            image = ImageOps.exif_transpose(raw).convert('RGBA')
            image.thumbnail((tile[0] - 24, tile[1] - 24), Image.Resampling.LANCZOS)
            left = index * tile[0] + (tile[0] - image.width) // 2
            top = (tile[1] - image.height) // 2
            board.paste(image, (left, top), image)
        if digest(source) != shas[index]:
            raise ValueError(f'CHARACTER_REFERENCE_CHANGED: {source}')
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{dest.name}.', suffix='.tmp', dir=directory)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        board.save(tmp, format='PNG')
        if dest.is_file():
            if digest(dest) != digest(tmp):
                raise ValueError(f'CHARACTER_REFERENCE_SHEET_CHANGED: {dest}')
        else:
            os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    return str(dest), shas
