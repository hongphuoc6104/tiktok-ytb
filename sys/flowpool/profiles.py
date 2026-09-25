"""Profile pool (profiles.json): the user's existing signed-in Chrome profiles.

Only the profiles declared in experiments/b2_illustrator/browser-profiles.json
(`priority`) are used -- no new sign-ins, no separate user-data-dirs, no copies
of profile data. Only the profile-picker metadata in `Local State` (display
name, account e-mail hint) is read; cookies and login databases are never
opened. All profiles live in the user's one Chrome process and are driven
through the FlowPool daemon's single CDP connection.
"""
import json
import os
import re
import threading
import time
from pathlib import Path

from .config import SYS
from .store import write_json_atomic
import characters

STATES = ('ready', 'busy', 'low_credit', 'needs_login', 'captcha', 'cooldown')
# States that only a clean doctor observation or a human `mark` can clear.
STICKY = ('needs_login', 'captcha')
B2 = SYS / 'experiments/b2_illustrator'
# Which Chrome/Flow account profile already has a channel's mascot registered
# as a character -- account-specific bookkeeping, not part of which mascot
# design a channel uses (that's characters.py). Only the default/vocab
# mascot has a known profile assignment so far; a channel with no entry here
# simply seeds no media_ids (derive() below resolves the path/media id
# through characters.py rather than a literal string).
MASCOT_PROFILE_BY_CHANNEL = {None: 'Profile 10'}
PROFILE_DIR = re.compile(r'^(Default|Profile \d+)$')


def _registered_mascots():
    """{sha256_of_reference_image: (media_id, profile_name)} for every channel
    mascot that currently has both an approved reference image and a known
    Flow media id -- never a hard-coded single (path, media_id) pair."""
    from .journal import sha256_file
    out = {}
    for channel, profile in MASCOT_PROFILE_BY_CHANNEL.items():
        mascot = characters.try_resolve(SYS, channel)
        if mascot and mascot['media_id']:
            out[sha256_file(mascot['reference_path'])] = (mascot['media_id'], profile)
    return out


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
    """Build the pool definition from the declared (`priority`) profiles only."""
    cfg = cfg or {}
    src = json.loads(Path(browser_profiles).read_text(encoding='utf-8'))
    local = json.loads(Path(machine_local).read_text(encoding='utf-8')) if Path(machine_local).exists() else {}
    udd = local.get('flow_user_data_dir') or src['flow_user_data_dir']
    priority = list(src.get('priority') or [src['flow_profile_directory']])
    hints = _local_state_hints(udd)
    names = [n for n in priority if PROFILE_DIR.match(n)]
    registered = _registered_mascots()  # {sha256: (media_id, profile)}, never a single hard-coded pair
    profiles = []
    for i, name in enumerate(names):
        primary = name == (local.get('flow_profile_directory') or src['flow_profile_directory'])
        media = {sha: media_id for sha, (media_id, profile) in registered.items() if profile == name}
        profiles.append({
            'name': name, 'slug': slug(name), 'user_data_dir': udd, 'profile_directory': name,
            'enabled': True, 'priority': i, 'max_parallel': cfg.get('flowpool_per_browser_queue', 4),
            'display_name': hints.get(name, {}).get('display_name'),
            'account_hint': hints.get(name, {}).get('account_hint'),
            # Each account needs its own remix of the B-2 queue tool and its own project.
            'tool_url': local.get('tool_url') if primary else None,
            'project': cfg.get('flow_project', 'Video Pilot'), 'project_url': None,
            'media_ids': media,
            'state': 'ready', 'state_reason': None, 'state_since': time.time(), 'cooldown_until': None,
            'credits': None, 'credits_at': None,
            # Tab of this profile inside the shared Chrome (CDP target id; valid until Chrome restarts)
            # and the account e-mail Flow showed there, recorded once observed and verified afterwards.
            'binding': None, 'account_email': None,
        })
    return {'schema_version': 1, 'source': str(Path(browser_profiles).relative_to(SYS)) if str(browser_profiles).startswith(str(SYS)) else str(browser_profiles),
            'executable_path': local.get('executable_path') or src.get('executable_path'),
            'automatic_account_switching': False, 'profiles': profiles}


class Pool:
    def __init__(self, path, cfg=None, derive_fn=derive, declared=None):
        """`declared`: browser-profiles.json to sync from. A profile added there
        (priority list) is appended here automatically; nothing else is needed."""
        self.path = Path(path)
        self.cfg = cfg or {}
        self.lock = threading.RLock()
        if not self.path.exists():
            write_json_atomic(self.path, derive_fn(declared, cfg=self.cfg) if declared else derive_fn(cfg=self.cfg))
        self.data = json.loads(self.path.read_text(encoding='utf-8'))
        if self.data.get('schema_version') != 1 or self.data.get('mode') == 'instances':
            raise RuntimeError('OLD_POOL_FORMAT: profiles.json is from the separate-instance build; run '
                               '`python3 -m flowpool init --force` (keeps a .bak)')
        if declared and Path(declared).exists():
            self._sync(derive_fn(declared, cfg=self.cfg))
        self._normalize(time.time())

    def _sync(self, fresh):
        have = {p['name'] for p in self.data['profiles']}
        new = [p for p in fresh['profiles'] if p['name'] not in have]
        if new:
            top = max((p.get('priority', 0) for p in self.data['profiles']), default=-1)
            for i, p in enumerate(new):
                p['priority'] = top + 1 + i
            self.data['profiles'].extend(new)
            write_json_atomic(self.path, self.data)

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

    def update(self, name, **fields):
        with self.lock:
            p = self.get(name)
            p.update(fields)
            self.save()
            return p

    def record_binding(self, name, binding):
        if binding and binding != self.get(name).get('binding'):
            self.update(name, binding=binding)

    def record_email(self, name, email):
        if email and not self.get(name).get('account_email'):
            self.update(name, account_email=email.lower())

    def record_project(self, name, url):
        if url and self.get(name).get('project_url') != url:
            self.update(name, project_url=url)

    def refresh(self, now=None):
        with self.lock:
            self._normalize(now or time.time())
            self.save()
