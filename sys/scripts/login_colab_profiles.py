#!/usr/bin/env python3
"""Human-assisted OAuth in a visible terminal; never capture secrets in reports."""
import json
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from colab_bridge.accounts import add, command, registry
from account_catalog import probe_colab


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--total', type=int, help='Tổng số hồ sơ mong muốn; giữ các hồ sơ hiện có.')
    parser.add_argument('--new-only', action='store_true', help='Chỉ mở OAuth cho hồ sơ chưa có token.')
    args = parser.parse_args()
    binary = shutil.which('colab') or str(Path.home() / '.local/bin/colab')
    if args.total is not None:
        if not 1 <= args.total <= 100:
            parser.error('Tổng số hồ sơ phải trong 1–100.')
        existing = {entry['id'] for entry in registry()['accounts']}
        number = 1
        while len(existing) < args.total:
            name = f'account-{number:02d}'
            number += 1
            if name not in existing:
                add(name)
                existing.add(name)
    entries = [entry for entry in registry()['accounts'] if entry.get('enabled', True)]
    if args.new_only:
        from colab_bridge.accounts import folder
        entries = [entry for entry in entries if not (folder(entry['id']) / 'token.json').is_file()]
    if not entries:
        print('Chưa có hồ sơ. Tạo hồ sơ bằng colab_bridge.accounts login-many trong terminal này.')
        return 2
    print('ĐĂNG NHẬP COLAB — người dùng thao tác OAuth trực tiếp tại terminal này.', flush=True)
    print('Kiểm lần lượt các hồ sơ đã lưu. Không cấp GPU, không chạy generation.', flush=True)
    suggestions_path = ROOT / '.state/colab-login-suggestions.json'
    suggestions = json.loads(suggestions_path.read_text()) if suggestions_path.exists() else []
    if suggestions:
        print('\nCác tài khoản Chrome chưa xuất hiện trong danh sách Colab đã xác minh:', flush=True)
        for item in suggestions:
            print(f"  {item['email']} — {item['profile']} / {item['label']}", flush=True)
        print('Chọn các tài khoản trên nếu đúng. Thông tin gợi ý từ Chrome; vẫn phải xác minh sau OAuth.', flush=True)
    target = ROOT / '.state/colab-login-progress.json'
    previous = json.loads(target.read_text()) if target.exists() else {}
    results = previous.get('accounts', [])
    for index, entry in enumerate(entries, 1):
        name = entry['id']
        print(f'\n[{index}/{len(entries)}] {name}: mở link Google nếu được yêu cầu, chọn đúng tài khoản của hồ sơ.', flush=True)
        if index <= len(suggestions):
            item = suggestions[index-1]
            print(f"Gợi ý lượt này: {item['email']} — {item['profile']} / {item['label']}", flush=True)
        # CLI performs ordinary credential refresh. Any required OAuth code is
        # entered by the human here and is never included in our report.
        result = subprocess.run(command(binary, name, ['sessions']))
        observed = probe_colab('colab:' + name)
        results = [item for item in results if item['account'] != name]
        results.append({'account': name, 'cli_exit': result.returncode,
                        'auth': observed.get('auth'), 'capability': observed.get('capability'),
                        'reason': observed.get('reason')})
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({'at': time.time(), 'accounts': results, 'gpu_allocated': False}, ensure_ascii=False, indent=2))
        target.chmod(0o600)
        print(f"Kết quả {name}: {observed.get('auth')} / {observed.get('capability')}", flush=True)
        if observed.get('identity'):
            from account_catalog import observations
            aliases = [alias for alias, saved in observations().items()
                       if alias.startswith('colab:') and alias != 'colab:' + name and saved.get('identity') == observed['identity']]
            if aliases:
                print('Tài khoản Google này đã xuất hiện ở: ' + ', '.join(aliases) + '. Bộ đếm sẽ dùng chung; không tính là tài khoản mới.', flush=True)
        if result.returncode:
            print('Giữ hồ sơ này để đăng nhập lại; các hồ sơ còn lại vẫn được kiểm tra.', flush=True)
    print('\nĐã kiểm hết hồ sơ. Trạng thái được cập nhật trên trang quản lý.', flush=True)
    input('Nhấn Enter để đóng terminal đăng nhập...')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
