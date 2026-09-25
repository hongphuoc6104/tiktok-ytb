"""Profile pool (profiles.json): one entry per signed-in Chrome profile.

Derived from experiments/b2_illustrator/browser-profiles.json. Only directory
names and the profile-picker metadata in `Local State` (display name, account
e-mail hint) are read; cookies and login databases are never opened or copied.
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
B2 = SYS / 'experiments/b2_illustrator'
CANONICAL_MASCOT_MEDIA = {
    # Profile 10's registered channel mascot (see adapters.gflow); valid for that account only.
    'path': SYS / 'assets/characters/channel-mascot/reference-v1.png',
    'media_id': 'de94a39b-155f-4afe-acbb-d9d4b59ad532',
    'profile': 'Profile 10',
}
PROFILE_DIR = re.compile(r'^(Default|Profile \d+)$')


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


def _local_state_hints(user_data_dir):
    try:
        data = json.loads((Path(user_data_dir) / 'Local State').read_text(encoding='utf-8'))
        cache = data.get('profile', {}).get('info_cache', {})
        return {k: {'display_name': v.get('name'), 'account_hint': v.get('user_name') or None}
                for k, v in cache.items()}
    except (OSError, ValueError):
        return {}


def derive(browser_profiles=B2 / 'browser-profiles.json', machine_local=B2 / 'machine.local.json', cfg=None):
    """Build the pool definition. Priority profiles are enabled; every other
    `Profile N` directory found in the same user-data-dir is listed disabled."""
    cfg = cfg or {}
    src = json.loads(Path(browser_profiles).read_text(encoding='utf-8'))
    local = json.loads(Path(machine_local).read_text(encoding='utf-8')) if Path(machine_local).exists() else {}
    udd = local.get('flow_user_data_dir') or src['flow_user_data_dir']
    priority = list(src.get('priority') or [src['flow_profile_directory']])
    found = []
    try:
        found = sorted((d.name for d in Path(udd).iterdir() if d.is_dir() and PROFILE_DIR.match(d.name)),
                       key=lambda n: (0, 0) if n == 'Default' else (1, int(n.split()[-1])))
    except OSError:
        pass
    hints = _local_state_hints(udd)
    names = priority + [n for n in found if n not in priority]
    mascot_sha = None
    if CANONICAL_MASCOT_MEDIA['path'].exists():
        from .journal import sha256_file
        mascot_sha = sha256_file(CANONICAL_MASCOT_MEDIA['path'])
    profiles = []
    for i, name in enumerate(names):
        primary = name == (local.get('flow_profile_directory') or src['flow_profile_directory'])
        media = {}
        if mascot_sha and name == CANONICAL_MASCOT_MEDIA['profile']:
            media[mascot_sha] = CANONICAL_MASCOT_MEDIA['media_id']
        profiles.append({
            'name': name, 'slug': slug(name), 'user_data_dir': udd, 'profile_directory': name,
            'enabled': name in priority, 'priority': i, 'max_parallel': cfg.get('flowpool_per_browser_queue', 4),
            'display_name': hints.get(name, {}).get('display_name'),
            'account_hint': hints.get(name, {}).get('account_hint'),
            # Each account needs its own remix of the B-2 queue tool and its own project.
            'tool_url': local.get('tool_url') if primary else None,
            'project': cfg.get('flow_project', 'Video Pilot'), 'project_url': None,
            'media_ids': media,
            'state': 'ready', 'state_reason': None, 'state_since': time.time(), 'cooldown_until': None,
            'credits': None, 'credits_at': None, 'binding': None,
        })
    return {'schema_version': 1, 'source': str(Path(browser_profiles).relative_to(SYS)) if str(browser_profiles).startswith(str(SYS)) else str(browser_profiles),
            'executable_path': local.get('executable_path') or src.get('executable_path'),
            'automatic_account_switching': False, 'profiles': profiles}


class Pool:
    def __init__(self, path, cfg=None, derive_fn=derive):
        self.path = Path(path)
        self.cfg = cfg or {}
        self.lock = threading.RLock()
        if not self.path.exists():
            write_json_atomic(self.path, derive_fn(cfg=self.cfg))
        self.data = json.loads(self.path.read_text(encoding='utf-8'))
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
        raise KeyError(f'unknown profile {name}')

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
        if credits is None:
            return
        with self.lock:
            p = self.get(name)
            p.update(credits=credits, credits_at=at or time.time())
            self.save()

    def record_binding(self, name, binding):
        with self.lock:
            self.get(name)['binding'] = binding
            self.save()

    def refresh(self, now=None):
        with self.lock:
            self._normalize(now or time.time())
            self.save()
