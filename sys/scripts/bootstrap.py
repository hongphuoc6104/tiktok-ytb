#!/usr/bin/env python3
"""Dependency-free setup inspector. No Pilot import, login, GPU or generation."""
import argparse
import errno
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import time

MANAGEMENT = ('jsonschema==4.26.0', 'Pillow==12.1.1')
CONTROL_VERSION = '1.58.2'


def _definition(root):
    folder = Path(root) / 'control'
    if not (folder / 'package.json').is_file() or not (folder / 'package-lock.json').is_file():
        return None
    value = json.loads((folder / 'package.json').read_text())
    if value.get('dependencies') != {'playwright': CONTROL_VERSION}:
        raise ValueError('Control manifest must contain only pinned Playwright')
    return folder


def control_directory(home=None):
    return Path(home or Path.home()) / '.local/share/video-pilot/control' / ('playwright-' + CONTROL_VERSION)


def node_runtime(*, node=None, npm=None, runner=subprocess.run):
    binary = str(Path(node).expanduser().resolve()) if node else shutil.which('node')
    installer = str(Path(npm).expanduser().resolve()) if npm else shutil.which('npm')
    result = {'state': 'missing', 'node': binary, 'npm': installer, 'minimum': '18.18.0',
              'installation_source': 'existing_local_runtime', 'official_install': 'https://nodejs.org/en/download'}
    if not binary:
        return result
    try:
        response = runner([binary, '--version'], capture_output=True, text=True, timeout=5, check=True)
        match = __import__('re').fullmatch(r'v(\d+)\.(\d+)\.(\d+)\s*', response.stdout)
        version = tuple(map(int, match.groups())) if match else ()
        result.update(state='verified' if version >= (18,18,0) else 'unsupported',
                      version=response.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        result['state'] = 'unavailable'
    return result


def control_env(runtime, node):
    env = dict(os.environ)
    env.update(VP_CONTROL_RUNTIME=str(Path(runtime).resolve()), PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1',
               PATH=str(Path(node).parent) + os.pathsep + env.get('PATH', ''))
    # The pinned package does not need user's Node hooks or their npm lifecycle
    # configuration. Browser controller gets only our explicit module loader.
    env.pop('NODE_OPTIONS', None)
    return env


def control_dependencies(root, *, home=None, node=None, npm=None, runner=subprocess.run):
    root = Path(root).resolve()
    runtime = control_directory(home)
    info = {'state': 'missing', 'runtime': str(runtime), 'scope': 'browser_control_only',
            'version': CONTROL_VERSION, 'browser_download': False, 'provider_called': False}
    definition = _definition(root)
    if definition is None:
        return {**info, 'reason': 'control_definition_missing'}
    if not (runtime / 'node_modules/playwright/package.json').is_file():
        return info
    executable = node_runtime(node=node, npm=npm, runner=runner)
    if executable['state'] != 'verified':
        return {**info, 'reason': 'node_' + executable['state']}
    try:
        response = runner([executable['node'], '--experimental-loader', str(definition/'loader.mjs'),
                           str(definition/'import-check.mjs')], env=control_env(runtime, executable['node']),
                          capture_output=True, text=True, timeout=15, check=True)
        proof = json.loads(response.stdout)
        if proof != {'playwright':CONTROL_VERSION, 'connect_api':True, 'browser_started':False, 'provider_called':False}:
            raise ValueError('Unexpected control import evidence')
        return {**info, 'state':'verified', 'proof':proof, 'node':executable['node']}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {**info, 'state':'unavailable', 'reason':'isolated_control_import_failed'}


def install_control(root, *, home=None, node=None, npm=None, runner=subprocess.run):
    root = Path(root).resolve()
    definition = _definition(root)
    if definition is None:
        return {'state':'missing', 'reason':'control_definition_missing', 'installed':False}
    executable = node_runtime(node=node, npm=npm, runner=runner)
    if executable['state'] != 'verified' or not executable['npm']:
        raise RuntimeError('Install a supported Node/npm from https://nodejs.org/en/download or pass --node/--npm')
    runtime = control_directory(home)
    runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    if runtime.is_symlink() or runtime.stat().st_uid != os.getuid():
        raise RuntimeError('Unsafe control-runtime owner')
    with (runtime/'.install.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        for name in ('package.json', 'package-lock.json'):
            target = runtime/name
            source = definition/name
            if target.is_symlink():
                raise RuntimeError('Unsafe runtime manifest symlink')
            if target.is_file() and target.read_bytes() != source.read_bytes():
                raise RuntimeError('Different control manifest already owns this runtime; do not replace it')
            if not target.is_file():
                shutil.copyfile(source, target)
        ready = control_dependencies(root,home=home,node=executable['node'],npm=executable['npm'],runner=runner)
        if ready['state'] != 'verified':
            runner([executable['npm'], 'ci', '--ignore-scripts', '--omit=optional', '--no-audit', '--no-fund',
                    '--registry=https://registry.npmjs.org'], cwd=runtime, env=control_env(runtime,executable['node']),
                   check=True, capture_output=True, text=True, timeout=180)
            ready = control_dependencies(root,home=home,node=executable['node'],npm=executable['npm'],runner=runner)
            if ready['state'] != 'verified':
                raise RuntimeError('Control package install did not pass isolated import')
        return {**ready, 'installed':True, 'local_renderer_installed':False, 'model_installed':False,
                'manifest_sha256':hashlib.sha256((definition/'package-lock.json').read_bytes()).hexdigest()}


def session_socket_path(root):
    """Same short socket contract as b2_bridge/session.mjs, without Pilot import."""
    key = hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:16]
    return Path(__import__('tempfile').gettempdir()) / ('video-pilot-' + str(os.getuid())) / ('flow-' + key + '.sock')


def control_status(root):
    path = session_socket_path(root)
    result = {'state':'missing', 'socket':str(path), 'provider_called':False, 'browser_connected':False}
    try:
        meta = path.lstat()
        parent = path.parent.lstat()
        if not stat.S_ISSOCK(meta.st_mode) or meta.st_uid != os.getuid() or parent.st_uid != os.getuid() or stat.S_ISLNK(parent.st_mode):
            return {**result, 'state':'unsafe_owner'}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(1)
            client.connect(str(path))
            client.sendall(b'status\n')
            raw = client.recv(8193)
        if len(raw) > 8192:
            raise ValueError('Oversized status')
        value = json.loads(raw)
        if value.get('status') not in ('connected', 'not_connected', 'disconnected'):
            raise ValueError('Unknown daemon status')
        return {**result, 'state':'verified', 'daemon_status':value['status'],
                'browser_connected':value['status']=='connected',
                'profile_verification_present':bool((value.get('identity') or {}).get('observedProfile'))}
    except FileNotFoundError:
        return result
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            return {**result, 'state':'connection_refused', 'terminal_transport':True,
                    'instruction':'Use authorized control-recover-stale after ownership evidence; no automatic deletion.'}
        return {**result, 'state':'unresponsive_or_invalid', 'terminal_transport':False,
                'reason':'timeout' if isinstance(error, TimeoutError) else 'transport_unknown',
                'instruction':'Inspect the existing owner; do not delete socket or start a duplicate.'}
    except (ValueError, TypeError):
        return {**result, 'state':'unresponsive_or_invalid', 'terminal_transport':False,
                'reason':'invalid_status', 'instruction':'Inspect the existing owner; do not delete socket or start a duplicate.'}


def _process_identity(pid, proc_root='/proc'):
    """PID + kernel start ticks identify a process; reuse is never dead-owner evidence."""
    folder = Path(proc_root) / str(pid)
    try:
        metadata = folder.stat()
        fields = (folder / 'stat').read_text().rsplit(')', 1)[1].split()
        argv = (folder / 'cmdline').read_bytes().decode(errors='strict').split('\0')
        try:
            cwd = os.readlink(folder / 'cwd')
        except OSError:
            cwd = None
        return {'pid':int(pid), 'uid':metadata.st_uid, 'process_state':fields[0], 'start_ticks':fields[19],
                'argv':[value for value in argv if value], 'cwd':cwd}
    except FileNotFoundError:
        if not folder.exists():
            return {'pid':int(pid), 'state':'dead'}
        return {'pid':int(pid), 'state':'unknown'}
    except (OSError, ValueError, IndexError, UnicodeError):
        return {'pid':int(pid), 'state':'unknown'}


def _exact_daemon(process, root):
    if process.get('state') or process.get('uid') != os.getuid():
        return False
    script = (Path(root) / 'experiments/b2_illustrator/session.mjs').resolve()
    argv = process['argv']
    for index, argument in enumerate(argv):
        if index + 1 < len(argv) and argv[index + 1] == 'serve':
            candidate = Path(argument)
            if not candidate.is_absolute():
                if not process.get('cwd'):
                    return None if candidate.name == 'session.mjs' else False
                candidate = Path(process['cwd']) / candidate
            if candidate.resolve() == script:
                return True
    return False


def socket_ownership(root, *, proc_root='/proc'):
    """Read-only kernel inode + same-UID process audit, including missing journals."""
    root = Path(root).resolve()
    socket_path = session_socket_path(root)
    proc = Path(proc_root)
    evidence = {'state':'verified', 'socket':str(socket_path), 'kernel_inodes':[],
                'inode_owners':[], 'matching_daemons':[], 'unknown_processes':[],
                'recorded_owner':None, 'provider_called':False, 'browser_started':False}
    try:
        lines = (proc / 'net/unix').read_text().splitlines()[1:]
        evidence['kernel_inodes'] = [line.split()[6] for line in lines
            if len(line.split()) >= 8 and line.split()[7] == str(socket_path)]
        for folder in proc.iterdir():
            if not folder.name.isdigit():
                continue
            try:
                if folder.stat().st_uid != os.getuid():
                    continue
                process = _process_identity(int(folder.name), proc_root)
                if process.get('state') == 'dead':
                    continue
                if process.get('state') == 'unknown':
                    evidence['unknown_processes'].append(int(folder.name)); continue
                if process.get('process_state') != 'Z':
                    # Unix socket visibility is network-namespace scoped.
                    # Sandboxed same-UID processes may have another table;
                    # absence only in this controller's namespace is unsafe.
                    process_lines = (folder / 'net/unix').read_text().splitlines()[1:]
                    evidence['kernel_inodes'].extend(line.split()[6] for line in process_lines
                        if len(line.split()) >= 8 and line.split()[7] == str(socket_path))
                exact = _exact_daemon(process, root)
                if exact is None:
                    evidence['unknown_processes'].append(int(folder.name)); continue
                if exact:
                    evidence['matching_daemons'].append({'pid':process['pid'], 'start_ticks':process['start_ticks']})
                if not evidence['kernel_inodes'] or process.get('process_state') == 'Z':
                    continue
                for descriptor in (folder / 'fd').iterdir():
                    try:
                        target = os.readlink(descriptor)
                    except FileNotFoundError:
                        continue
                    if target.startswith('socket:[') and target[8:-1] in evidence['kernel_inodes']:
                        evidence['inode_owners'].append({'pid':process['pid'], 'fd':descriptor.name, 'inode':target[8:-1]})
            except FileNotFoundError:
                if folder.exists():
                    evidence['unknown_processes'].append(int(folder.name))
            except OSError:
                evidence['unknown_processes'].append(int(folder.name))
        owner_path = root / '.state/flow-control.json'
        if owner_path.exists():
            if owner_path.is_symlink() or owner_path.stat().st_uid != os.getuid():
                raise ValueError('Unsafe daemon owner journal')
            owner = json.loads(owner_path.read_text())
            if owner.get('root') != str(root) or owner.get('socket') != str(socket_path) or type(owner.get('pid')) is not int or owner['pid'] <= 0:
                raise ValueError('Daemon owner journal does not identify this checkout/socket')
            process = _process_identity(owner['pid'], proc_root)
            evidence['recorded_owner'] = {'pid':owner['pid'], 'state':process.get('state', 'live'),
                'start_ticks_match': bool(owner.get('start_ticks') and owner['start_ticks'] == process.get('start_ticks')),
                'exact_daemon':_exact_daemon(process, root)}
            # Even a reused/unrelated PID remains unknown ownership, not a
            # reason to terminate or remove anything.
            if process.get('state') != 'dead':
                evidence['state'] = 'owner_live_or_unknown'
        evidence['kernel_inodes'] = sorted(set(evidence['kernel_inodes']))
        evidence['unknown_processes'] = sorted(set(evidence['unknown_processes']))
        if evidence['kernel_inodes'] or evidence['inode_owners'] or evidence['matching_daemons']:
            evidence['state'] = 'live_or_shared_owner'
        elif evidence['unknown_processes']:
            evidence['state'] = 'process_audit_incomplete'
    except (OSError, ValueError, IndexError):
        evidence['state'] = 'ownership_unknown'
    return evidence


def _private_socket(root):
    path = session_socket_path(root)
    parent = path.parent.lstat()
    metadata = path.lstat()
    if (path.is_symlink() or not stat.S_ISSOCK(metadata.st_mode) or metadata.st_uid != os.getuid()
            or stat.S_ISLNK(parent.st_mode) or not stat.S_ISDIR(parent.st_mode)
            or parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) & 0o077
            or stat.S_IMODE(metadata.st_mode) & 0o077):
        raise RuntimeError('Unsafe/shared socket ownership or permissions; nothing removed')
    return path, metadata, parent


def control_recover_stale(root, *, grant, source, proc_root='/proc'):
    """Explicit authorized cleanup of one proven departed listener socket only."""
    root = Path(root).resolve()
    sys.path.insert(0, str(root))
    from profile_setup import _authorize
    _authorize(root, grant, source, root / 'experiments/b2_illustrator/session.mjs')
    state = root / '.state'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'flow-control.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        status = control_status(root)
        if status['state'] == 'missing':
            return {**status, 'recovered':False, 'reason':'already_missing'}
        if status['state'] != 'connection_refused':
            raise RuntimeError('Recovery requires connection-refused; timeout/live/invalid endpoint retained')
        path, original, original_parent = _private_socket(root)
        ownership = socket_ownership(root, proc_root=proc_root)
        if ownership['state'] != 'verified':
            raise RuntimeError('Socket ownership unresolved: ' + ownership['state'] + '; nothing removed')
        # Repeat terminal transport and kernel/owner checks immediately before
        # unlink. Our official startup uses the same lock; unknown manual
        # restarts are rejected whenever the observation differs.
        if control_status(root)['state'] != 'connection_refused':
            raise RuntimeError('Socket transport changed during recovery; nothing removed')
        final_ownership = socket_ownership(root, proc_root=proc_root)
        current = path.lstat()
        if final_ownership != ownership or (current.st_dev,current.st_ino,current.st_uid,current.st_mode,current.st_ctime_ns) != (original.st_dev,original.st_ino,original.st_uid,original.st_mode,original.st_ctime_ns):
            raise RuntimeError('Socket identity/ownership changed during recovery; nothing removed')
        parent_handle = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            actual_parent = os.fstat(parent_handle)
            if (actual_parent.st_dev, actual_parent.st_ino, actual_parent.st_uid, actual_parent.st_mode) != (original_parent.st_dev, original_parent.st_ino, original_parent.st_uid, original_parent.st_mode):
                raise RuntimeError('Private socket directory changed; nothing removed')
            final = os.stat(path.name, dir_fd=parent_handle, follow_symlinks=False)
            if (final.st_dev,final.st_ino,final.st_uid,final.st_mode,final.st_ctime_ns) != (original.st_dev,original.st_ino,original.st_uid,original.st_mode,original.st_ctime_ns):
                raise RuntimeError('Socket inode changed; nothing removed')
            evidence = {'version':1, 'root':str(root), 'socket':str(path), 'inode':original.st_ino,
                'device':original.st_dev, 'transport':'connection_refused', 'ownership':ownership,
                'source':source, 'grant':grant, 'at':time.time(), 'provider_called':False,
                'browser_started':False, 'manual_owner_record_missing':ownership['recorded_owner'] is None}
            folder = state / 'flow-control-recoveries';folder.mkdir(exist_ok=True,mode=0o700)
            target = folder / (str(time.time_ns()) + '.json')
            target.write_text(json.dumps({**evidence,'result':'verified_before_unlink'},indent=2)+'\n');os.chmod(target,0o600)
            os.unlink(path.name, dir_fd=parent_handle)
        finally:
            os.close(parent_handle)
        done = folder / (target.stem + '-result.json')
        done.write_text(json.dumps({'evidence':str(target),'result':'exact_stale_socket_removed','at':time.time()},indent=2)+'\n');os.chmod(done,0o600)
        return {'state':'missing','socket':str(path),'recovered':True,'evidence':str(target),
                'manual_owner_record_missing':ownership['recorded_owner'] is None,
                'provider_called':False,'browser_started':False,'next_action':'control-start with the same setup authority'}


def control_start(root, *, grant, source, home=None, node=None, npm=None, runner=None):
    """Start the fixed daemon listener only. No connect/login/generation."""
    root = Path(root).resolve()
    sys.path.insert(0,str(root))
    from profile_setup import _authorize
    _authorize(root,grant,source,root/'experiments/b2_illustrator/session.mjs')
    dependency = control_dependencies(root,home=home,node=node,npm=npm)
    if dependency['state'] != 'verified':
        raise RuntimeError('Control dependencies missing; bootstrap apply --install')
    state = root/'.state'
    state.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (state/'flow-control.lock').open('a') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        existing = control_status(root)
        if existing['state'] == 'verified':
            return {**existing, 'reused':True, 'browser_started':False}
        if existing['state'] != 'missing':
            raise RuntimeError('Existing daemon owner is unresolved; no socket deleted')
        owner_path=state/'flow-control.json'
        if owner_path.is_file():
            owner=json.loads(owner_path.read_text())
            from profile_setup import _pid_alive
            if _pid_alive(owner.get('pid')):
                raise RuntimeError('Prior daemon process still owns startup; no duplicate started')
        command=[dependency['node'],'--experimental-loader',str(root/'control/loader.mjs'),
                 str(root/'experiments/b2_illustrator/session.mjs'),'serve']
        (root/'experiments/b2_illustrator/results').mkdir(parents=True,exist_ok=True)
        process=(runner or subprocess.Popen)(command,cwd=root,env=control_env(dependency['runtime'],dependency['node']),
                                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        observed_process = _process_identity(process.pid)
        owner={'pid':process.pid,'start_ticks':observed_process.get('start_ticks'),'root':str(root),'socket':str(session_socket_path(root)),
               'source':source,'grant':grant,'started_at':time.time(),'browser_started':False,'provider_called':False}
        temp=owner_path.with_suffix('.tmp');temp.write_text(json.dumps(owner,indent=2)+'\n');os.chmod(temp,0o600);temp.replace(owner_path)
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            result=control_status(root)
            if result['state']=='verified':
                return {**result,'pid':process.pid,'reused':False,'browser_started':False}
            if process.poll() is not None:
                break
            time.sleep(.1)
        raise RuntimeError('Daemon listener not confirmed; owner preserved for investigation')


def check(root, *, home=None, node=None, npm=None):
    root = Path(root).resolve()
    result = {'version': 1, 'checked_at': time.time(), 'root': str(root),
              'capabilities': {}, 'no_provider_calls': True, 'heavy_processing': 'remote_only'}
    caps = result['capabilities']
    caps['python'] = {'state': 'verified', 'version': sys.version.split()[0], 'executable': sys.executable}
    for name in ('git', 'google-chrome', 'chromium', 'colab', 'uv'):
        path = shutil.which(name)
        caps[name] = {'state': 'present' if path else 'missing', 'path': path, 'live_verified': False}
    for name in ('jsonschema', 'PIL'):
        caps[name] = {'state': 'present' if importlib.util.find_spec(name) else 'missing', 'scope': 'management'}
    for name in ('reference-v1.png', 'character.json'):
        path = root / 'assets/characters/channel-mascot' / name
        caps['mascot/' + name] = {'state': 'present' if path.is_file() else 'missing'}
    caps['colab_auth'] = {'state': 'not_tested', 'instruction': 'Người dùng OAuth; tồn tại token không chứng minh auth live.'}
    caps['flow_auth'] = {'state': 'not_tested'}
    caps['colab_T4'] = {'state': 'not_tested', 'local_fallback': False}
    caps['remote_render'] = {'state': 'not_tested', 'local_fallback': False}
    caps['node_control'] = node_runtime(node=node,npm=npm)
    caps['playwright_control'] = control_dependencies(root,home=home,node=node,npm=npm)
    caps['flow_daemon'] = control_status(root)
    caps['disk'] = {'state': 'verified', 'free_bytes': shutil.disk_usage(root).free}
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from account_catalog import discover
    inventory = discover(home=home, system_root=root)
    result['account_inventory'] = inventory
    result['next'] = 'apply --install: môi trường quản lý; đăng nhập/probe do người dùng yêu cầu riêng'
    return result


def plan(root):
    root = Path(root).resolve()
    return {'version': 1, 'root': str(root), 'steps': [
        {'id': 'state', 'action': 'create_local_state', 'path': str(root / '.state')},
        {'id': 'management_venv', 'action': 'create_venv', 'path': str(root / '.venv-management')},
        {'id': 'management_deps', 'action': 'install_pinned_management_dependencies', 'requirements': list(MANAGEMENT)},
        {'id':'control_deps','action':'install_pinned_browser_control_only','requirements':['playwright=='+CONTROL_VERSION],
         'path':str(control_directory()),'browser_download':False},
        {'id':'flow_daemon','action':'explicit_control_start_after_setup_grant','automatic':False}],
        'excluded': ['OAuth/login', 'GPU allocation', 'generation', 'local model', 'local renderer', 'secret/profile copying']}


def apply(root, *, install=False, home=None, node=None, npm=None, runner=subprocess.run):
    root = Path(root).resolve()
    state = root / '.state'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    env = root / '.venv-management'
    if not (env / 'bin/python').is_file():
        runner([sys.executable, '-m', 'venv', '--without-pip', str(env)], check=True, capture_output=True, text=True)
    if install:
        uv = shutil.which('uv')
        if uv:
            command = [uv, 'pip', 'install', '--python', str(env / 'bin/python'), *MANAGEMENT]
        elif importlib.util.find_spec('pip'):
            command = [sys.executable, '-m', 'pip', '--python', str(env / 'bin/python'), 'install', '--disable-pip-version-check', *MANAGEMENT]
        else:
            runner([str(env / 'bin/python'), '-m', 'ensurepip', '--upgrade'], check=True, capture_output=True, text=True)
            command = [str(env / 'bin/python'), '-m', 'pip', 'install', '--disable-pip-version-check', *MANAGEMENT]
        runner(command, check=True, capture_output=True, text=True)
    control = install_control(root,home=home,node=node,npm=npm,runner=runner) if install else control_dependencies(root,home=home,node=node,npm=npm,runner=runner)
    previous = json.loads((state / 'bootstrap.json').read_text()) if (state / 'bootstrap.json').is_file() else {}
    result = {'version': 1, 'applied_at': time.time(), 'environment': str(env),
              'management_dependencies_installed': bool(install or previous.get('management_dependencies_installed')), 'resume_safe': True,
              'control_dependencies':control,
              'no_provider_calls': True, 'heavy_processing': 'remote_only'}
    target = state / 'bootstrap.json'
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2) + '\n')
    os.chmod(tmp, 0o600)
    tmp.replace(target)
    return result


def main():
    parser = argparse.ArgumentParser(description='Khởi tạo phần quản lý local; xử lý nặng ở Colab.')
    parser.add_argument('action', choices=('plan', 'check', 'apply', 'resume', 'control-status', 'control-start', 'control-ownership', 'control-recover-stale'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--home', type=Path, help='Root inventory metadata riêng cho phép kiểm cô lập')
    parser.add_argument('--install', action='store_true', help='Cài dependencies quản lý đã ghim vào venv riêng')
    parser.add_argument('--node',help='Đường dẫn Node runtime đã cài');parser.add_argument('--npm',help='Đường dẫn npm đã cài')
    parser.add_argument('--grant');parser.add_argument('--source')
    args = parser.parse_args()
    if args.action in ('plan', 'check'):
        result = plan(args.root) if args.action == 'plan' else check(args.root, home=args.home,node=args.node,npm=args.npm)
    elif args.action=='control-status':
        result=control_status(args.root)
    elif args.action=='control-ownership':
        result=socket_ownership(args.root)
    elif args.action=='control-recover-stale':
        result=control_recover_stale(args.root,grant=args.grant,source=args.source)
    elif args.action=='control-start':
        result=control_start(args.root,grant=args.grant,source=args.source,home=args.home,node=args.node,npm=args.npm)
    else:
        result = apply(args.root, install=args.install,home=args.home,node=args.node,npm=args.npm)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        # Dependency subprocess output may contain environment data; do not echo it.
        print(json.dumps({'blocked': type(error).__name__, 'reason':str(error) if isinstance(error, (RuntimeError, ValueError)) else 'Environment operation failed; external output hidden', 'instruction': 'Inspect control-status and control-ownership for listener recovery; otherwise verify management installer and resume. No provider operation performed.'}, ensure_ascii=False))
        raise SystemExit(2)
