"""Read-only dependency checks before expensive production steps."""
import json
import shutil
from pathlib import Path


def check_environment(sys_root, *, need_audio=True):
    from .colab_deploy import _load_state, _session_exists, _profile_cli
    from .still import selected_still
    results = []
    def check(name, function):
        try:
            detail = function()
            results.append({'name': name, 'ready': True, 'detail': detail})
        except Exception as exc:
            results.append({'name': name, 'ready': False, 'detail': str(exc)})
    def executables():
        missing = [name for name in ('agy', 'ffmpeg', 'ffprobe') if not shutil.which(name)]
        if missing:
            raise RuntimeError('Thiếu công cụ: ' + ', '.join(missing))
        return 'Có các chương trình cần thiết; đăng nhập AGY được xác minh khi gọi tài khoản.'
    def account_provider():
        path = Path.home() / '.gemini/antigravity-cli/settings.json'
        if path.exists() and json.loads(path.read_text()).get('modelProvider') == 'gemini':
            raise RuntimeError('AGY đang dùng API provider; chỉ cho phép đăng nhập tài khoản.')
        return 'Không bật đường API trả phí.'
    def colab():
        state = _load_state(Path(sys_root))
        alias, session = state.get('profile_alias', 'alternate'), state.get('session', 'podcast-worker')
        active = _session_exists(alias, session)
        _profile_cli(alias, "sessions")  # Validate local account configuration.
        return {'profile': alias, 'session_exists': active,
                'cost_basis': 'user_assumed_free_trial', 'cost_verified': False}
    check('programs', executables)
    check('account_provider', account_provider)
    check('selected_still', lambda: str(selected_still(sys_root)[0]))
    if need_audio:
        check('colab', colab)
    return {'ready': all(row['ready'] for row in results), 'checks': results}
