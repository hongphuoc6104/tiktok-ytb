"""Metadata-only Linux browser/Colab inventory. Never read credential contents."""
import configparser
import hashlib
import json
from pathlib import Path
import re

BROWSER_ROOTS = (
 ('Chrome', '.config/google-chrome'), ('Chrome Beta', '.config/google-chrome-beta'),
 ('Chrome Dev', '.config/google-chrome-unstable'), ('Chromium', '.config/chromium'),
 ('Brave', '.config/BraveSoftware/Brave-Browser'), ('Brave Beta', '.config/BraveSoftware/Brave-Browser-Beta'),
 ('Brave Nightly', '.config/BraveSoftware/Brave-Browser-Nightly'), ('Edge', '.config/microsoft-edge'),
 ('Edge Beta', '.config/microsoft-edge-beta'), ('Edge Dev', '.config/microsoft-edge-dev'),
 ('Vivaldi', '.config/vivaldi'), ('Opera', '.config/opera'), ('Opera Developer', '.config/opera-developer'),
 ('Chromium Snap', 'snap/chromium/common/chromium'),
 ('Chrome Flatpak', '.var/app/com.google.Chrome/config/google-chrome'),
 ('Chromium Flatpak', '.var/app/org.chromium.Chromium/config/chromium'),
 ('Brave Flatpak', '.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser'),
 ('Edge Flatpak', '.var/app/com.microsoft.Edge/config/microsoft-edge'),
 ('Vivaldi Flatpak', '.var/app/com.vivaldi.Vivaldi/config/vivaldi'),
 ('Opera Flatpak', '.var/app/com.opera.Opera/config/opera'))
FIREFOX_ROOTS = ('.mozilla/firefox', 'snap/firefox/common/.mozilla/firefox',
                 '.var/app/org.mozilla.firefox/.mozilla/firefox')


def load_metadata(path):
    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return {}
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _browser(label, root, name, display=None):
    stable = hashlib.sha256((str(root.resolve()) + '/' + name).encode()).hexdigest()[:20]
    return {'id': 'browser-' + stable, 'service': 'flow', 'browser': label,
            'profile': name, 'label': display or name, 'metadata_root': str(root),
            'configured': True, 'auth': {'state': 'not_tested', 'source': 'profile_metadata'},
            'capability': {'state': 'not_tested'}, 'identity': None,
            'identity_note': 'Profile không chứng minh danh tính Google hoặc đăng nhập Flow.'}


def discover(home=None, system_root=None):
    home = Path(home or Path.home())
    roots = [(label, home / folder) for label, folder in BROWSER_ROOTS]
    # Existing operator-managed Chrome roots are metadata aliases, never a
    # credential copy or proof that the corresponding ordinary profile is in use.
    roots.extend(('Chrome managed', root) for root in sorted((home / '.config').glob('google-chrome-cdp*'))
                 if root.is_dir())
    if system_root:
        roots.extend([('Project Flow', Path(system_root) / '.gflow'),
                      ('Project Flow profiles', Path(system_root) / '.gflow/profiles')])
        project = Path(system_root)
        for group in (project / '.gflow', project / '.gflow/profiles'):
            if group.is_dir():
                for candidate in group.iterdir():
                    if candidate.is_dir() and ((candidate / 'Local State').is_file() or (candidate / 'Default').is_dir()):
                        roots.append(('Project Flow', candidate))
        cfg = load_metadata(project / 'experiments/b2_illustrator/browser-profiles.json')
        for metadata in (cfg, load_metadata(project / 'experiments/b2_illustrator/machine.local.json'), load_metadata(project / 'experiments/b2_illustrator/config.json')):
            for key in ('flow_user_data_dir', 'user_data_dir'):
                value = metadata.get(key)
                if isinstance(value, str) and value:
                    roots.append(('Configured Flow', Path(value).expanduser()))
        for item in cfg.get('profiles', []) if isinstance(cfg.get('profiles'), list) else []:
            if isinstance(item, dict) and isinstance(item.get('user_data_dir'), str):
                roots.append(('Configured Flow', Path(item['user_data_dir']).expanduser()))
    found, inspected, seen = [], [], set()
    for label, root in roots:
        key = str(root.resolve())
        if key in seen:
            continue
        seen.add(key)
        inspected.append({'browser': label, 'root': str(root), 'present': root.is_dir()})
        if not root.is_dir():
            continue
        metadata = load_metadata(root / 'Local State')
        profiles = metadata.get('profile', {}).get('info_cache', {})
        if not isinstance(profiles, dict):
            profiles = {}
        names = set(profiles)
        names.update(p.name for p in root.iterdir() if p.is_dir() and
                     (p.name == 'Default' or re.fullmatch(r'Profile \d+', p.name)))
        if not names and ((root / 'Preferences').is_file() or (root / 'Local State').is_file()):
            names.add('.')
        for name in sorted(names):
            if name != '.' and (Path(name).name != name or name in ('.', '..')):
                continue
            if not (root / name).is_dir():
                continue
            display = profiles.get(name, {}).get('name') if isinstance(profiles.get(name), dict) else None
            found.append(_browser(label, root, name, display))
    for relative in FIREFOX_ROOTS:
        root = home / relative
        inspected.append({'browser': 'Firefox', 'root': str(root), 'present': root.is_dir()})
        ini = root / 'profiles.ini'
        if not ini.is_file():
            continue
        parser = configparser.ConfigParser()
        try:
            parser.read(ini)
            for section in parser.sections():
                if section.startswith('Profile'):
                    name = parser.get(section, 'Path', fallback='')
                    if not name or Path(name).is_absolute() or '..' in Path(name).parts:
                        continue
                    if (root / name).is_dir():
                        found.append(_browser('Firefox', root, name, parser.get(section, 'Name', fallback=name)))
        except (OSError, configparser.Error):
            pass
    colab_root = home / '.config/video-pilot/colab'
    registry = load_metadata(colab_root / 'accounts.json')
    colab = []
    for item in registry.get('accounts', []):
        if not isinstance(item, dict) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}', str(item.get('id', ''))):
            continue
        name = item['id']
        configured = (colab_root / 'profiles' / name / 'token.json').is_file()
        colab.append({'id': 'colab:' + name, 'account': name, 'service': 'colab', 'label': name,
                      'configured': configured, 'enabled': bool(item.get('enabled', True)),
                      'preferred': name == registry.get('preferred'), 'identity': None,
                      'auth': {'state': 'not_tested' if configured else 'login_required',
                               'source': 'credential_file_presence_only'},
                      'capability': {'state': 'not_tested', 'device': 'T4'}})
    observed = observations(home)
    for item in colab + found:
        result = observed.get(item['id'], {})
        if result.get('auth'):
            item['auth'] = {'state': result['auth'], 'source': result.get('auth_source', result.get('source')), 'checked_at': result.get('auth_checked_at', result.get('checked_at'))}
        if result.get('capability'):
            item['capability'] = {'state': result['capability'], 'gpu': result.get('gpu', 'not_tested'), 'source': result.get('capability_source', result.get('source')), 'checked_at': result.get('capability_checked_at', result.get('checked_at'))}
        item['identity_source'] = result.get('identity_source')
        item['identity'] = result.get('identity')
        item['account_label'] = result.get('account_label')
        if item['service'] == 'colab' and item['account_label']:
            item['label'] = item['account'] + ' · ' + item['account_label']
    # Correlate local Chrome metadata with a provider-verified Colab identity.
    # This identifies a likely profile, never verifies its Flow login.
    root_metadata = {item['metadata_root']: load_metadata(Path(item['metadata_root']) / 'Local State') for item in found}
    for item in colab:
        item['matching_browser_profiles'] = []
        item['same_google_account_as'] = [other['id'] for other in colab
            if other['id'] != item['id'] and item.get('identity') and other.get('identity') == item['identity']]
        for browser in found:
            metadata = root_metadata[browser['metadata_root']].get('profile', {}).get('info_cache', {}).get(browser['profile'], {})
            email = metadata.get('user_name', '').strip().lower() if isinstance(metadata, dict) else ''
            candidate = 'google:' + hashlib.sha256(email.encode()).hexdigest() if email else None
            if item.get('identity') and item['identity'] == candidate:
                item['matching_browser_profiles'].append({k: browser[k] for k in ('id', 'profile', 'label', 'browser')})
    return {'accounts': colab + found, 'roots': inspected, 'colab_store_present': colab_root.is_dir(),
            'no_live_probe': True, 'note': 'Inventory metadata; chưa kiểm auth, Flow hoặc T4 thật.'}


def login_handoff(account):
    if account.get('service') == 'colab':
        name = account.get('account', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}', name):
            raise ValueError('Invalid account')
        return {'state': 'user_action_required', 'instruction': 'Người dùng tự OAuth trong terminal riêng; không dán mã/token vào trang quản lý.',
                'command': 'python3 -m colab_bridge.accounts login ' + name}
    return {'state': 'user_action_required', 'instruction': 'Mở đúng profile browser đã chọn và đăng nhập Flow bằng thao tác của người dùng. Inventory chưa xác minh trạng thái đăng nhập.'}


def observation_store(home=None):
    return Path(home or Path.home()) / '.config/video-pilot/management/accounts.json'


def observations(home=None):
    return load_metadata(observation_store(home))


def record_observation(account_id, record, home=None):
    import time
    from session_store import locked_json
    allowed = {'auth', 'capability', 'source', 'identity', 'identity_source', 'reason', 'gpu', 'session_count', 'account_label'}
    value = {key: record[key] for key in allowed if key in record}
    if record.get('auth') == 'verified' and 'reason' not in record:
        value['reason'] = None
    value['checked_at'] = time.time()
    if 'auth' in value:
        value.update(auth_source=value.get('source'), auth_checked_at=value['checked_at'])
    if 'capability' in value:
        value.update(capability_source=value.get('source'), capability_checked_at=value['checked_at'])
    with locked_json(observation_store(home), dict) as data:
        data[account_id] = {**data.get(account_id, {}), **value}
        saved = dict(data[account_id])
    return saved


def confirm_identity(account_id, email, source, *, home=None, budget_store=None):
    """Explicit human identity mapping, not a live authentication claim."""
    from account_budget import Budgets
    if not isinstance(email, str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or not source.strip():
        raise ValueError('Google email và xác nhận nguyên văn là bắt buộc')
    identity = 'google:' + hashlib.sha256(email.strip().lower().encode()).hexdigest()
    store = budget_store or Path(home or Path.home()) / '.config/video-pilot/management'
    Budgets(store).bind_identity(account_id, identity, 'user_confirmed: ' + source)
    return record_observation(account_id, {'identity': identity, 'identity_source': 'user_confirmed',
        'source': 'explicit_user_identity_confirmation'}, home)


def probe_colab(account_id, *, home=None, budget_store=None, runner=None, binary=None):
    """On-demand authenticated read only; never called during inventory/check."""
    import shutil
    import subprocess
    if not re.fullmatch(r'colab:[a-z0-9][a-z0-9_-]{0,47}', account_id):
        raise ValueError('Chọn đúng hồ sơ Colab')
    home = Path(home or Path.home())
    name = account_id.split(':', 1)[1]
    token = home / '.config/video-pilot/colab/profiles' / name / 'token.json'
    if not token.is_file():
        return record_observation(account_id, {'auth': 'login_required', 'capability': 'not_tested', 'source': 'credential_missing'}, home)
    launcher = Path(binary or shutil.which('colab') or home / '.local/bin/colab')
    try:
        first = launcher.read_text().splitlines()[0]
        if not first.startswith('#!/') or ' ' in first[2:]:
            raise ValueError('Unsupported launcher')
        result = (runner or subprocess.run)([first[2:], str(Path(__file__).parent / 'dashboard/colab_probe.py'), str(token)],
            capture_output=True, text=True, timeout=40)
        value = json.loads(result.stdout) if result.returncode == 0 else {'auth': 'unknown', 'capability': 'unsupported', 'source': 'installed_cli_runtime'}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        value = {'auth': 'unknown', 'capability': 'not_tested', 'reason': 'network_or_runtime_unknown', 'source': 'read_only_probe'}
    if value.get('identity') and value.get('auth') == 'verified':
        from account_budget import Budgets
        Budgets(budget_store or home / '.config/video-pilot/management').bind_identity(account_id, value['identity'], value['identity_source'])
    return record_observation(account_id, value, home)


def probe_flow(account_id, *, system_root, home=None, budget_store=None):
    """Read the connected Flow account UI; never open/connect/submit a profile."""
    import b2_bridge
    from account_budget import Budgets
    by_id = {item['id']: item for item in discover(home, system_root)['accounts'] if item['service'] == 'flow'}
    item = by_id.get(account_id)
    if not item:
        raise ValueError('Chọn đúng profile Flow đã phát hiện')
    expected = (Path(item['metadata_root']) / item['profile']).resolve()
    try:
        connection = b2_bridge.query_status()
        observed = (connection.get('identity') or {}).get('observedProfile')
        if connection.get('status') != 'connected' or not observed or Path(observed).resolve() != expected:
            value = {'auth': 'unknown', 'capability': 'not_tested', 'reason': 'selected_profile_not_connected',
                     'source': 'flow_connected_profile_check'}
        else:
            value = b2_bridge.send_raw_command('tool-snapshot:account-inspect', timeout=45)
            if value.get('auth') == 'verified' and (not value.get('identity') or
                    Path(value.get('observedProfile', '')).resolve() != expected):
                value = {'auth': 'unknown', 'capability': 'not_tested', 'reason': 'account_observation_mismatch',
                         'source': 'flow_connected_profile_check'}
    except Exception:
        value = {'auth': 'unknown', 'capability': 'not_tested', 'reason': 'network_or_runtime_unknown',
                 'source': 'read_only_flow_probe'}
    if value.get('auth') == 'verified':
        Budgets(budget_store or Path(home or Path.home()) / '.config/video-pilot/management').bind_identity(
            account_id, value['identity'], value['identity_source'])
    return record_observation(account_id, value, home)
