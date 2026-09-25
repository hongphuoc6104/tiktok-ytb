"""Start/stop FlowPool-managed Chrome instances (one per account).

`launch` starts Chrome with the instance's own --user-data-dir and
--remote-debugging-port (allowed for non-default data dirs) at Flow. `login`
starts the same data dir WITHOUT remote debugging, so the user signs in by
hand in a plain browser window; FlowPool never automates sign-in. No
automation or anti-detection flags are added.
"""
import json
import os
import shutil
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

DEFAULT_URL = 'https://flow.google.com/'


def chrome_exe(pool_data, cfg):
    for exe in (cfg.get('flowpool_chrome'), pool_data.get('executable_path'), '/opt/google/chrome/google-chrome',
                shutil.which('google-chrome'), shutil.which('google-chrome-stable')):
        if exe and Path(exe).exists():
            return exe
    raise RuntimeError('CHROME_NOT_FOUND: set config flowpool_chrome to the Google Chrome executable')


def cdp_alive(port, timeout=1.5):
    """True when a Chrome DevTools endpoint answers on 127.0.0.1:port."""
    if not port:
        return False
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{int(port)}/json/version', timeout=timeout) as r:
            return 'Browser' in json.loads(r.read().decode('utf-8'))
    except (OSError, ValueError):
        return False


def chrome_pids(user_data_dir, proc_root='/proc'):
    """Main (non-helper) Chrome processes using exactly this user-data-dir."""
    want = f'--user-data-dir={Path(user_data_dir).resolve()}'
    found = []
    for d in Path(proc_root).iterdir():
        if not d.name.isdigit():
            continue
        try:
            args = (d / 'cmdline').read_bytes().decode('utf-8', 'replace').split('\0')
        except OSError:
            continue
        if want in args and not any(a.startswith('--type=') for a in args):
            found.append(int(d.name))
    return sorted(found)


def instance_status(p, alive=cdp_alive, pids=chrome_pids):
    running = pids(p['user_data_dir'])
    return {'running': bool(running), 'pids': running, 'cdp': alive(p.get('port'))}


def launch(pool, name, cfg, login=False, popen=subprocess.Popen, alive=cdp_alive, pids=chrome_pids,
           sleep=time.sleep, wait_seconds=20):
    p = pool.get(name)
    Path(p['user_data_dir']).mkdir(parents=True, exist_ok=True)
    running = pids(p['user_data_dir'])
    if running:
        if not login and alive(p['port']):
            return {'instance': name, 'status': 'already_running', 'port': p['port'], 'pid': running[0]}
        raise RuntimeError(f'INSTANCE_ALREADY_OPEN: {name} is open (pid {running[0]})'
                           + ('' if login else ' without remote debugging; close that window first'))
    if not login and alive(p['port']):
        raise RuntimeError(f'PORT_IN_USE: port {p["port"]} answers but is not {name}; change its port in profiles.json')
    args = [chrome_exe(pool.data, cfg), f'--user-data-dir={Path(p["user_data_dir"]).resolve()}',
            '--no-first-run', '--no-default-browser-check']
    if not login:
        args.append(f'--remote-debugging-port={int(p["port"])}')
    args.append(p.get('project_url') if (p.get('project_url') and not login) else cfg.get('flowpool_flow_url') or DEFAULT_URL)
    proc = popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 start_new_session=True)
    pool.update(name, pid=proc.pid, launched_at=time.time())
    if login:
        return {'instance': name, 'status': 'sign_in_window_opened', 'pid': proc.pid,
                'next': f'sign in by hand, close the window, then: python3 -m flowpool launch {name}'}
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if alive(p['port']):
            return {'instance': name, 'status': 'launched', 'port': p['port'], 'pid': proc.pid}
        sleep(0.5)
    raise RuntimeError(f'LAUNCH_TIMEOUT: Chrome for {name} did not open port {p["port"]}')


def stop(pool, name, pids=chrome_pids, kill=os.kill, sleep=time.sleep, wait_seconds=10):
    """SIGTERM only the Chrome whose command line names this instance's data dir."""
    p = pool.get(name)
    running = pids(p['user_data_dir'])
    for pid in running:
        try:
            kill(pid, signal.SIGTERM)
        except OSError:
            pass
    deadline = time.time() + wait_seconds
    while running and time.time() < deadline and pids(p['user_data_dir']):
        sleep(0.3)
    pool.update(name, pid=None)
    return {'instance': name, 'status': 'stopped' if running else 'not_running', 'pids': running}
