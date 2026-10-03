"""Durable management selections and request pinning, with process-safe writes."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import time
import uuid


@contextmanager
def locked_json(path, default):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.with_suffix('.lock').open('a') as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        value = json.loads(path.read_text()) if path.exists() else default()
        yield value
        tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        os.chmod(tmp, 0o600)
        tmp.replace(path)


class Sessions:
    def __init__(self, system_root):
        self.path = Path(system_root) / '.state/management-session.json'

    def read(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {
            'version': 1, 'session_id': None, 'pool': [], 'defaults': {}, 'pins': {}, 'selection': 'specified', 'preset': 'remote-t4'}

    def select(self, pool, defaults, *, selection='specified', preset='remote-t4', known=None):
        if selection not in ('specified', 'auto') or preset != 'remote-t4':
            raise ValueError('Supported selection/preset required')
        if not isinstance(pool, list) or any(not isinstance(x, str) for x in pool) or len(pool) != len(set(pool)):
            raise ValueError('Unique account IDs required')
        if not isinstance(defaults, dict) or set(defaults) - {'colab', 'flow'} or any(x not in pool for x in defaults.values()):
            raise ValueError('Defaults must belong to selected pool')
        if known is not None:
            by_id = {x['id']: x for x in known}
            if any(x not in by_id for x in pool) or any(by_id[x]['service'] != service for service, x in defaults.items()):
                raise ValueError('Unknown account or wrong service')
        with locked_json(self.path, self.read) as state:
            state.setdefault('session_id', None)
            if state['session_id'] is None:
                state['session_id'] = uuid.uuid4().hex
            state.update(pool=pool, defaults=defaults, selection=selection, preset=preset, updated_at=time.time())
        return self.read()

    def snapshot(self, job=None):
        state = self.read()
        snapshot = {key: state.get(key) for key in ('version', 'session_id', 'pool', 'defaults', 'selection', 'preset')}
        snapshot['runtime_bindings'] = {**state.get('runtime_bindings', {}), **state.get('job_runtime_bindings', {}).get(job, {})}
        return snapshot

    def pin(self, request, *, job, service, account, session, identity=None):
        if not all(isinstance(x, str) and x for x in (request, job, service, account, session)) or service not in ('colab', 'flow'):
            raise ValueError('Exact request ownership required')
        record = {'job': job, 'service': service, 'account': account, 'session': session, 'identity': identity}
        with locked_json(self.path, self.read) as state:
            existing = state.setdefault('pins', {}).get(request)
            if existing and existing != record:
                raise ValueError('Pinned request ownership cannot be changed')
            state['pins'][request] = record
        return record

    def bind_runtime(self, service, account, runtime_session, *, grant, source, evidence, job=None, target=None):
        """Official setup binding; never moves submitted request pins or claims auth.

        A binding records the user's exact runtime target. Actual allocation and
        account authentication are independently checked by provider adapters.
        Frozen snapshots retain old bindings when the current selection changes.
        """
        import re
        from profile_setup import _authorize
        if service not in ('colab', 'flow') or not isinstance(account, str):
            raise ValueError('Exact service/account required')
        if not isinstance(runtime_session, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', runtime_session):
            raise ValueError('Exact runtime session ID required')
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError('Runtime binding needs actual instruction/observation evidence')
        if job is not None and (not isinstance(job, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', job)):
            raise ValueError('Exact job required')
        if target is not None:
            from profile_setup import _url
            import hashlib
            if service != 'flow' or not isinstance(target, dict) or set(target) != {'tool_url', 'profile_path'}:
                raise ValueError('Flow target permits only exact tool_url and profile_path')
            _url(target['tool_url'])
            path = Path(target['profile_path']) if isinstance(target['profile_path'], str) else None
            if path is None or not path.is_absolute() or '..' in path.parts or path.name in ('', '.', '..'):
                raise ValueError('Flow target needs the exact absolute runtime profile path')
            canonical = str(path.parent.resolve()) + '/' + path.name
            expected = 'browser-' + hashlib.sha256(canonical.encode()).hexdigest()[:20]
            if account != expected:
                raise ValueError('Flow target profile path must match the selected runtime account alias')
            target = {'tool_url': target['tool_url'], 'profile_path': str(path.parent.resolve() / path.name)}
        _authorize(self.path.parent.parent, grant, source, self.path)
        with locked_json(self.path, self.read) as state:
            if account not in state.get('pool', []):
                raise ValueError('Runtime account must be selected in this management session')
            if service == 'colab' and not account.startswith('colab:') or service == 'flow' and not account.startswith('browser-'):
                raise ValueError('Runtime account service mismatch')
            binding = {'service': service, 'account': account, 'runtime_session': runtime_session,
                       'source': source, 'evidence': evidence, 'grant': grant, 'bound_at': time.time()}
            if target is not None:
                binding['target'] = target
            bindings = state.setdefault('job_runtime_bindings', {}).setdefault(job, {}) if job else state.setdefault('runtime_bindings', {})
            old = bindings.get(service)
            if old:
                state.setdefault('runtime_binding_history', []).append({'job': job, 'binding': old})
            bindings[service] = binding
        return binding
