"""Instance pool (profiles.json): one FlowPool-managed Chrome per Google account.

Each instance has its own user-data-dir under sys/.gflow/pool/<slug>/ and its
own remote-debugging port, so every account is a separate Chrome process that
FlowPool can drive in parallel. The user signs in once per instance by hand
(`python3 -m flowpool login NAME`); FlowPool never types credentials and never
reads or copies cookies.
"""
import json
import os
import re
import threading
import time
from pathlib import Path

from .config import SYS
from .store import write_json_atomic

STATES = ('ready', 'busy', 'low_credit', 'needs_login', 'captcha', 'cooldown')
# States that only a clean doctor observation or a human `mark` can clear.
STICKY = ('needs_login', 'captcha')
SCHEMA = 2
NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$')


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def _pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def empty_pool(cfg=None):
    cfg = cfg or {}
    return {'schema_version': SCHEMA, 'mode': 'instances',
            'executable_path': cfg.get('flowpool_chrome') or '/opt/google/chrome/google-chrome',
            'automatic_account_switching': False, 'profiles': []}


def new_instance(name, data, cfg=None):
    """Pool entry for a new account instance: own user-data-dir, next free port."""
    cfg = cfg or {}
    if not NAME.match(name or ''):
        raise ValueError('INVALID_NAME: use 1-40 letters, digits, _ or - (e.g. acc1)')
    if any(p['name'] == name for p in data['profiles']):
        raise ValueError(f'INSTANCE_EXISTS: {name}')
    used = {p.get('port') for p in data['profiles']}
    port = int(cfg.get('flowpool_base_port', 9301))
    while port in used:
        port += 1
    root = Path(cfg.get('flowpool_instances_dir') or SYS / '.gflow/pool')
    return {
        'name': name, 'slug': slug(name), 'user_data_dir': str((root / slug(name)).resolve()), 'port': port,
        'enabled': True, 'priority': len(data['profiles']), 'max_parallel': cfg.get('flowpool_per_browser_queue', 4),
        'account_hint': None,  # optional e-mail the user may fill in; checked when Flow shows it
        # Optional B-2 queue tool remixed into this account (x4 image queue). Empty =
        # images go through the plain Flow UI like clips, which needs no remix.
        'tool_url': None, 'media_ids': {},
        'project': cfg.get('flow_project', 'Video Pilot'), 'project_url': None,
        'state': 'ready', 'state_reason': None, 'state_since': time.time(), 'cooldown_until': None,
        'credits': None, 'credits_at': None, 'pid': None, 'launched_at': None,
    }


class Pool:
    def __init__(self, path, cfg=None):
        self.path = Path(path)
        self.cfg = cfg or {}
        self.lock = threading.RLock()
        if not self.path.exists():
            write_json_atomic(self.path, empty_pool(self.cfg))
        self.data = json.loads(self.path.read_text(encoding='utf-8'))
        if self.data.get('schema_version') != SCHEMA:
            raise RuntimeError('OLD_POOL_FORMAT: profiles.json is the shared-profile pool; run '
                               '`python3 -m flowpool init --force` (keeps a .bak) and add instances')
        self._normalize(time.time())

    def _normalize(self, now):
        for p in self.data['profiles']:
            if p.get('state') == 'busy' and not _pid_alive(p.get('busy_pid')):
                p.update(state=p.get('busy_from') or 'ready', busy_pid=None)
            if p.get('state') == 'cooldown' and p.get('cooldown_until') and now >= p['cooldown_until']:
                p.update(state='ready', state_reason=None, cooldown_until=None)

    def save(self):
        with self.lock:
            write_json_atomic(self.path, self.data)

    @property
    def profiles(self):
        return [p for p in self.data['profiles'] if p.get('enabled')]

    def get(self, name):
        for p in self.data['profiles']:
            if p['name'] == name:
                return p
        raise KeyError(f'unknown instance {name}; add it with `python3 -m flowpool add {name}`')

    def add(self, name):
        with self.lock:
            entry = new_instance(name, self.data, self.cfg)
            Path(entry['user_data_dir']).mkdir(parents=True, exist_ok=True)
            self.data['profiles'].append(entry)
            self.save()
            return entry

    def update(self, name, **fields):
        with self.lock:
            p = self.get(name)
            p.update(fields)
            self.save()
            return p

    def set_state(self, name, state, reason=None, until=None, now=None):
        if state not in STATES:
            raise ValueError(state)
        with self.lock:
            p = self.get(name)
            p.update(state=state, state_reason=reason, state_since=now or time.time(),
                     cooldown_until=until if state == 'cooldown' else None)
            if state != 'busy':
                p.pop('busy_pid', None)
                p.pop('busy_from', None)
            self.save()
            return p

    def acquire(self, name):
        with self.lock:
            p = self.get(name)
            if p['state'] not in ('ready', 'low_credit'):
                raise RuntimeError(f'PROFILE_NOT_READY: {name} is {p["state"]}')
            p.update(busy_from=p['state'], state='busy', busy_pid=os.getpid())
            self.save()
            return p

    def release(self, name, state=None, reason=None, until=None):
        with self.lock:
            p = self.get(name)
            target = state or p.get('busy_from') or 'ready'
            p.pop('busy_from', None)
            return self.set_state(name, target, reason, until)

    def record_credits(self, name, credits, at=None):
        if credits is not None:
            self.update(name, credits=credits, credits_at=at or time.time())

    def record_project(self, name, url):
        if url and self.get(name).get('project_url') != url:
            self.update(name, project_url=url)

    def refresh(self, now=None):
        with self.lock:
            self._normalize(now or time.time())
            self.save()
