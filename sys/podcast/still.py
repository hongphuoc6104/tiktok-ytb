"""Use the user's selected still; no generation, external service or quality gate."""
import hashlib
import json
import os
from pathlib import Path
import shutil


def selected_still(sys_root):
    root = Path(sys_root).resolve()
    config = json.loads((root / 'assets/podcast/still.json').read_text())
    path = (root / config['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Thiếu ảnh podcast mặc định trong dự án.')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != config['sha256']:
        raise ValueError('Ảnh mặc định khác ảnh người dùng đã chọn.')
    return path, config


def copy_selected_still(ctx, manifest=None):
    source, config = selected_still(ctx.coordinator.sys_root)
    target = ctx.artifact_path('image/user-selected.png')
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != config['sha256']:
            raise ValueError('Ảnh đã lưu cho tập bị thay đổi.')
    else:
        temporary = target.with_suffix('.tmp')
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
    return {'state': 'complete', 'path': str(target), 'sha256': config['sha256'],
            'source': 'user_selected', 'layout': 'contain'}
