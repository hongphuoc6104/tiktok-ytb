"""Per-machine Flow profile setup. Metadata inventory; no credential copying.

Browser start is an explicitly authorized, bounded operation. Reusing a browser
does not establish Google identity or Flow authentication; the controller must
verify chrome://version before dispatch. This module never terminates browsers,
removes their locks, refreshes tokens, or sends generation requests.
"""
import argparse
import errno
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
from urllib.parse import urlparse
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

from account_catalog import discover
from permissions import Grants, PermissionDenied
from session_store import locked_json


class SetupBlocked(RuntimeError):
    pass


def inventory(system_root, home=None):
    """Include every discovered profile, preserving unsupported entries."""
    home = Path(home or Path.home())
    items = [dict(x) for x in discover(home, system_root)['accounts'] if x['service'] == 'flow']
    defaults = {str((home / folder).resolve()) for folder in
                ('.config/google-chrome', '.config/google-chrome-beta', '.config/google-chrome-unstable')}
    for item in items:
        root = Path(item['metadata_root']).resolve()
        supported = item['browser'] in ('Chrome', 'Chrome Beta', 'Chrome Dev', 'Chrome managed',
                                        'Chrome Flatpak', 'Configured Flow', 'Project Flow', 'Project Flow profiles')
        item.update(provider_supported=supported,
                    setup_state=('fresh_managed_profile_login_required' if str(root) in defaults else
                                 'existing_root_auth_not_tested') if supported else 'provider_unsupported',
                    launch_requires_nondefault_root=str(root) in defaults,
                    source_mapping='metadata_only_no_google_identity')
        item['source_account_candidates'] = []
        if item['browser'] == 'Chrome managed':
            # These are suggestions for operator selection. Root suffixes and
            # display names cannot prove which Google account is logged in.
            suffix = re.fullmatch(r'google-chrome-cdp-(?:profile|p)(\d+)', root.name)
            hinted = 'Profile ' + suffix[1] if suffix else ('Default' if root.name.endswith('-default') else item['profile'])
            item['source_account_candidates'] = [source['id'] for source in items
                if source['metadata_root'] == str(home / '.config/google-chrome') and source['profile'] == hinted]
    return items


def _url(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname != 'flow.google.com' or parsed.username or parsed.password or parsed.port:
        raise ValueError('An exact HTTPS Flow tool URL is required')
    if not re.fullmatch(r'/project/[a-zA-Z0-9-]+/tool/[a-zA-Z0-9-]+', parsed.path) or parsed.query or parsed.fragment:
        raise ValueError('Select the exact project/tool URL; a landing page is insufficient')
    return url


def _profile(name):
    if not isinstance(name, str) or name in ('.', '..') or Path(name).name != name or '\\' in name:
        raise ValueError('Invalid profile directory')
    return name


def _validate(value, home=None):
    home = Path(home or Path.home()).resolve()
    root = Path(value['flow_user_data_dir']).resolve()
    defaults = {home / '.config/google-chrome', home / '.config/google-chrome-beta',
                home / '.config/google-chrome-unstable'}
    if root in defaults or root == home:
        raise SetupBlocked('DEFAULT_CHROME_CDP_FORBIDDEN')
    _url(value['tool_url']); _profile(value['flow_profile_directory'])
    if value.get('remote_debugging_port') != 0 or value.get('remote_debugging_address') != '127.0.0.1':
        raise SetupBlocked('UNSAFE_CDP_CONFIGURATION')
    executable = Path(value['executable_path'])
    if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
        raise SetupBlocked('CHROME_EXECUTABLE_UNAVAILABLE')
    if value.get('credential_copy_permitted') is not False:
        raise SetupBlocked('CREDENTIAL_COPY_FORBIDDEN')


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except (PermissionError, ValueError, TypeError):
        return True  # An uncertain owner is never permission to start another.


def plan(system_root, account_id, tool_url, *, home=None, executable=None, managed_root=None, reuse_account=None):
    home = Path(home or Path.home())
    accounts = {x['id']: x for x in inventory(system_root, home)}
    item = accounts.get(account_id)
    if not item:
        raise SetupBlocked('PROFILE_NOT_DISCOVERED')
    if not item['provider_supported']:
        raise SetupBlocked('PROVIDER_BROWSER_UNSUPPORTED: profile retained in inventory')
    source_root = Path(item['metadata_root']).resolve()
    profile = _profile(item['profile'])
    target = source_root
    fresh = item['launch_requires_nondefault_root']
    if reuse_account:
        reuse = accounts.get(reuse_account)
        if not reuse or reuse['launch_requires_nondefault_root'] or not reuse['provider_supported']:
            raise SetupBlocked('MANAGED_PROFILE_NOT_REUSABLE')
        if account_id not in reuse.get('source_account_candidates', []):
            raise SetupBlocked('SOURCE_METADATA_NOT_MATCHED: choose the managed profile directly instead')
        target = Path(reuse['metadata_root']).resolve()
        profile = _profile(reuse['profile'])
        fresh = False
    elif fresh:
        policy_path = Path(system_root) / 'config.json'
        policy = json.loads(policy_path.read_text()) if policy_path.is_file() else {}
        if policy.get('flow_profile_policy') == 'existing_only':
            raise SetupBlocked('EXISTING_PROFILE_EXTENSION_REQUIRED: open the selected existing Chrome profile normally and use browser extension control; do not create a replacement profile')
        target = Path(managed_root or home / '.config/video-pilot/flow-browser' / account_id).resolve()
        # Reusing ordinary Chrome credentials through filesystem copies is never
        # an option. A fresh directory requires a human Google/Flow login.
        profile = 'Default'
    elif managed_root is not None and Path(managed_root).resolve() != source_root:
        raise SetupBlocked('EXISTING_PROFILE_ROOT_MUST_MATCH')
    default_roots = {str((home / p).resolve()) for p in ('.config/google-chrome', '.config/google-chrome-beta', '.config/google-chrome-unstable')}
    if str(target) in default_roots or target == home.resolve():
        raise SetupBlocked('DEFAULT_CHROME_CDP_FORBIDDEN')
    binary = str(Path(executable or shutil.which('google-chrome') or '/opt/google/chrome/google-chrome').resolve())
    if not Path(binary).is_file() or not os.access(binary, os.X_OK):
        raise SetupBlocked('CHROME_EXECUTABLE_UNAVAILABLE')
    alias = 'browser-' + hashlib.sha256((str(target) + '/' + profile).encode()).hexdigest()[:20]
    return {'version': 1, 'source_account': account_id, 'runtime_account': alias, 'source_root': str(source_root),
            'source_profile': item['profile'], 'flow_user_data_dir': str(target),
            'flow_profile_directory': profile, 'executable_path': binary, 'tool_url': _url(tool_url),
            'remote_debugging_address': '127.0.0.1', 'remote_debugging_port': 0,
            'fresh_login_required': fresh, 'authentication_verified': False,
            'identity_verified': False, 'source_mapping': 'metadata_only_no_google_identity',
            'credential_copy_permitted': False, 'selected_existing_alias': reuse_account}


def _authorize(root, grant_id, source, target):
    if not isinstance(source, str) or not source.strip():
        raise PermissionDenied('Actual setup authorization source is required')
    grants = Grants(root)
    entry = next((x for x in grants.read()['grants'] if x['id'] == grant_id), None)
    if not entry or entry['role'] not in ('setup', 'development'):
        raise PermissionDenied('Setup/development grant required')
    checked = grants.require(grant_id, entry['role'], 'setup')
    relative = Path(target).resolve().relative_to(grants.project_root).as_posix()
    if not any(fnmatch.fnmatchcase(relative, x) for x in checked['paths']):
        raise PermissionDenied('Profile setup is outside granted project paths')
    return checked


def configure(system_root, value, *, grant, source):
    root = Path(system_root).resolve()
    target = root / 'experiments/b2_illustrator/machine.local.json'
    _authorize(root, grant, source, target)
    policy_path = root / 'config.json'
    policy = json.loads(policy_path.read_text()) if policy_path.is_file() else {}
    if policy.get('flow_profile_policy') == 'existing_only' and value.get('fresh_login_required'):
        raise SetupBlocked('EXISTING_PROFILE_EXTENSION_REQUIRED: fresh browser profiles are outside the selected setup policy')
    # Re-validate caller-owned data; do not allow command switches through fields.
    _validate(value)
    stored = {**value, 'setup_source': source, 'grant': grant, 'configured_at': time.time()}
    with locked_json(root / '.state/flow-profile-setup.json', dict) as state:
        if state.get('active') and state['active'].get('root') != value['flow_user_data_dir']:
            previous = state['active']
            if processes(previous['root']) or _pid_alive(previous.get('pid')) or (
                    endpoint_status(previous['root'])['state'] not in ('missing', 'refused') or
                    lock_status(previous['root'])['state'] not in ('absent', 'local_dead')):
                raise SetupBlocked('ANOTHER_BROWSER_SESSION_OWNED: finish the prior session first')
            state.setdefault('history', []).append(state.pop('active'))
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix('.tmp')
        temp.write_text(json.dumps(stored, indent=2) + '\n')
        temp.replace(target)
        state['configuration'] = stored
    return stored


def processes(data_root, proc_root='/proc'):
    """Return only PIDs whose exact user-data-dir equals this selected root."""
    selected = str(Path(data_root).resolve())
    found = []
    for item in Path(proc_root).iterdir():
        if not item.name.isdigit():
            continue
        try:
            argv = (item / 'cmdline').read_bytes().decode(errors='replace').split('\0')
            argv = [value for value in argv if value]
            # Chromium can rewrite its process title into a single argv[0].
            # Split at option boundaries, preserving spaces inside root/profile
            # values; shlex would lose those spaces in an unquoted title.
            if len(argv) == 1 and ' --user-data-dir=' in argv[0]:
                argv = [value.strip() for value in re.split(r' (?=--[A-Za-z][A-Za-z0-9-]*(?:=|\s|$))', argv[0])]
            if '--type=renderer' in argv or any(x.startswith('--type=') for x in argv):
                continue
            options = [x.split('=', 1)[1] for x in argv if x.startswith('--user-data-dir=')]
            if any(str(Path(value).resolve()) == selected for value in options):
                found.append({'pid': int(item.name), 'cdp_ephemeral': len(options) == 1 and '--remote-debugging-port=0' in argv,
                              'localhost': len(options) == 1 and '--remote-debugging-address=127.0.0.1' in argv})
        except (OSError, ValueError):
            continue
    return found


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def endpoint_status(data_root, *, fetch=None):
    """Distinguish a refused departed endpoint from timeout/unknown ownership.

    A connection refusal is only evidence that this exact localhost port is
    closed. Restart also requires a complete root-process check and safe lock
    ownership; no network failure by itself proves a browser has stopped.
    """
    marker = Path(data_root) / 'DevToolsActivePort'
    try:
        lines = marker.read_text().strip().splitlines()
        port = int(lines[0])
        if not 1 <= port <= 65535 or not re.fullmatch(r'/devtools/browser/[a-zA-Z0-9-]+', lines[1]):
            raise ValueError('Invalid endpoint')
        url = f'http://127.0.0.1:{port}/json/version'
        if fetch is None:
            with build_opener(ProxyHandler({}), _NoRedirect()).open(url, timeout=2) as response:
                raw = response.read(65537)
                if len(raw) > 65536:
                    raise ValueError('Oversized endpoint response')
                data = json.loads(raw)
        else:
            data = fetch(url)
        ws = f'ws://127.0.0.1:{port}' + lines[1]
        if data.get('webSocketDebuggerUrl') != ws:
            raise ValueError('Endpoint ownership mismatch')
        return {'state': 'connected', 'endpoint': ws}
    except FileNotFoundError:
        return {'state': 'missing', 'endpoint': None}
    except (ValueError, IndexError):
        return {'state': 'invalid', 'endpoint': None}
    except (OSError, URLError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        if isinstance(reason, ConnectionRefusedError) or getattr(reason, 'errno', None) == errno.ECONNREFUSED:
            return {'state': 'refused', 'endpoint': None}
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return {'state': 'timeout', 'endpoint': None}
        return {'state': 'unknown', 'endpoint': None}


def endpoint(data_root, *, fetch=None):
    return endpoint_status(data_root, fetch=fetch)['endpoint']


def lock_status(data_root, *, hostname=None, pid_alive=None):
    """Inspect Chromium's lock symlink only; preserve every lock file."""
    lock = Path(data_root) / 'SingletonLock'
    if not lock.is_symlink():
        return {'state': 'unknown'} if lock.exists() else {'state': 'absent'}
    try:
        owner = os.readlink(lock)
        match = re.fullmatch(r'([a-zA-Z0-9_.-]+)-(\d+)', owner)
        if not match or int(match[2]) <= 0:
            return {'state': 'unknown'}
        host, pid = match[1], int(match[2])
        if host != (hostname or socket.gethostname()):
            return {'state': 'foreign', 'hostname': host, 'pid': pid}
        return {'state': 'local_live_or_unknown' if (pid_alive or _pid_alive)(pid) else 'local_dead',
                'hostname': host, 'pid': pid}
    except OSError:
        return {'state': 'unknown'}


def start(system_root, *, grant, source, timeout=15, runner=None, inspect_processes=None, inspect_endpoint=None,
          inspect_endpoint_status=None):
    root = Path(system_root).resolve()
    config_path = root / 'experiments/b2_illustrator/machine.local.json'
    _authorize(root, grant, source, config_path)
    value = json.loads(config_path.read_text())
    data_root = Path(value['flow_user_data_dir']).resolve()
    _validate(value)
    probe = inspect_processes or processes
    resolve_endpoint = inspect_endpoint or endpoint
    def transport(root):
        if inspect_endpoint_status is not None:
            return inspect_endpoint_status(root)
        if inspect_endpoint is not None:
            value = inspect_endpoint(root)
            # Legacy test doubles returning None cannot certify refusal.
            return {'state': 'connected' if value else ('unknown' if (Path(root)/'DevToolsActivePort').exists() else 'missing'),
                    'endpoint': value}
        return endpoint_status(root)
    with locked_json(root / '.state/flow-profile-setup.json', dict) as state:
        active = state.get('active')
        if active and active['root'] != str(data_root):
            if (probe(active['root']) or _pid_alive(active.get('pid')) or
                    transport(active['root'])['state'] not in ('missing', 'refused') or
                    lock_status(active['root'])['state'] not in ('absent', 'local_dead')):
                raise SetupBlocked('ANOTHER_BROWSER_SESSION_OWNED')
        live = probe(data_root)
        observed = transport(data_root)
        ws = observed.get('endpoint')
        if active and active['root'] == str(data_root) and active.get('pid') is not None and not live:
            # Launch ownership is persisted before returning from the OS call.
            # A concurrent caller cannot interpret an observation lag as death.
            if _pid_alive(active['pid']):
                raise SetupBlocked('BROWSER_START_STILL_OWNED')
        if live:
            if len(live) != 1 or not live[0]['localhost'] or not live[0]['cdp_ephemeral'] or not ws:
                raise SetupBlocked('LIVE_BROWSER_NOT_REUSABLE: user must close/reconfigure it directly')
            owned = bool(active and active.get('owned') and active.get('pid') == live[0]['pid'] and active['root'] == str(data_root))
            state['active'] = {'root': str(data_root), 'pid': live[0]['pid'], 'owned': owned,
                               'reused': True, 'endpoint': ws, 'source': source, 'started_at': time.time()}
            return {**state['active'], 'auth': 'not_tested'}
        lock = lock_status(data_root)
        if observed['state'] not in ('missing', 'refused') or lock['state'] not in ('absent', 'local_dead'):
            raise SetupBlocked('STALE_OR_UNKNOWN_BROWSER_OWNER: ' + observed['state'] + '/' + lock['state'] + '; no lock/endpoint files removed')
        restart_evidence = {'endpoint_state': observed['state'], 'exact_root_processes': [], 'lock': lock,
                            'prior_owned_pid_dead': active.get('pid') if active and active.get('owned') else None,
                            'checked_at': time.time(), 'files_removed': False}
        data_root.mkdir(parents=True, exist_ok=True)
        command = [value['executable_path'], '--user-data-dir=' + str(data_root),
                   '--profile-directory=' + value['flow_profile_directory'], '--remote-debugging-address=127.0.0.1',
                   '--remote-debugging-port=0', '--no-first-run', value['tool_url']]
        # No no-sandbox, remote-allow-origins, credentials or copied browser data.
        process = (runner or subprocess.Popen)(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                               start_new_session=True)
        state['active'] = {'root': str(data_root), 'pid': process.pid, 'owned': True, 'reused': False,
                           'source': source, 'started_at': time.time(), 'state': 'starting',
                           'restart_evidence': restart_evidence}
    deadline = time.monotonic() + min(max(timeout, 0), 30)
    while True:
        live = probe(data_root)
        ws = resolve_endpoint(data_root)
        ready = any(x['pid'] == process.pid and x['localhost'] and x['cdp_ephemeral'] for x in live) and ws
        if ready:
            break
        if process.poll() is not None or time.monotonic() >= deadline:
            raise SetupBlocked('BROWSER_START_NOT_CONFIRMED: owner preserved; do not retry blindly')
        time.sleep(.2)
    with locked_json(root / '.state/flow-profile-setup.json', dict) as state:
        active = state['active']
        if active['pid'] != process.pid or active['root'] != str(data_root):
            raise SetupBlocked('BROWSER_OWNER_CHANGED')
        active.update(endpoint=ws, state='connected_transport')
        result = dict(active)
    return {**result, 'auth': 'not_tested', 'user_login_required': value['fresh_login_required']}


def main():
    parser = argparse.ArgumentParser(description='Metadata inventory and authorized Flow profile setup')
    parser.add_argument('action', choices=('inventory', 'plan', 'configure', 'start'))
    parser.add_argument('--root', default=str(Path(__file__).parent))
    parser.add_argument('--account'); parser.add_argument('--tool-url'); parser.add_argument('--executable')
    parser.add_argument('--reuse-account')
    parser.add_argument('--grant'); parser.add_argument('--source')
    args = parser.parse_args()
    if args.action == 'inventory':
        result = inventory(args.root)
    elif args.action == 'start':
        result = start(args.root, grant=args.grant, source=args.source)
    else:
        result = plan(args.root, args.account, args.tool_url, executable=args.executable, reuse_account=args.reuse_account)
        if args.action == 'configure':
            result = configure(args.root, result, grant=args.grant, source=args.source)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
