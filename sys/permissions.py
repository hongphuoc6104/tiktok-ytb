"""Persistent workflow grants; operational checks, not an OS security sandbox."""
from contextlib import contextmanager
import fcntl
import fnmatch
import json
import math
from pathlib import Path
import time
import uuid

ROLES = ('setup', 'production', 'development', 'maintenance')
OPERATIONS = {
    'setup': {'observe', 'setup', 'login'},
    'production': {'observe', 'content', 'execute', 'repair', 'stop', 'resume', 'mode', 'takeover'},
    'development': {'observe', 'system', 'tests', 'migrate', 'setup'},
    'maintenance': {'observe', 'cleanup', 'archive', 'git'},
}


class PermissionDenied(RuntimeError):
    pass


class Grants:
    def __init__(self, system_root):
        self.system_root = Path(system_root).resolve()
        self.project_root = (self.system_root.parent if self.system_root.name == 'sys'
                             and (self.system_root.parent / 'pilot.py').is_file() else self.system_root)
        self.path = self.system_root / '.state' / 'grants.json'

    def read(self):
        return json.loads(self.path.read_text()) if self.path.is_file() else {'version': 1, 'grants': []}

    @contextmanager
    def _writer(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix('.lock').open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            yield

    def _save(self, data):
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        temp.replace(self.path)

    def grant(self, role, *, source, jobs=(), paths=(), expires_at=None,
              granted_by='user', executed_by='assistant', operations=None):
        if role not in ROLES or not isinstance(source, str) or not source.strip():
            raise ValueError('A known role and actual authorization source are required')
        if not jobs and not paths:
            raise ValueError('An explicit job or path scope is required')
        if any(not isinstance(x, str) or not x or '..' in Path(x).parts or Path(x).is_absolute() for x in paths):
            raise ValueError('Grant paths must be relative to this project')
        if any(not isinstance(x, str) or not x for x in jobs):
            raise ValueError('Invalid job scope')
        if expires_at is not None and (type(expires_at) not in (int, float) or not math.isfinite(expires_at) or expires_at <= time.time()):
            raise ValueError('Expiry must be explicitly chosen in the future')
        operations = sorted(OPERATIONS[role]) if operations is None else list(operations)
        if not operations or len(operations) != len(set(operations)) or not set(operations) <= OPERATIONS[role]:
            raise ValueError('Grant operations must be an explicit subset of its role')
        entry = {'id': 'grant-' + uuid.uuid4().hex, 'role': role,
                 'project': str(self.project_root), 'jobs': list(jobs), 'paths': list(paths),
                 'source': source.strip(), 'granted_by': granted_by, 'executed_by': executed_by,
                 'created_at': time.time(), 'expires_at': expires_at, 'revoked': False,
                 'source_transport_verified': False, 'operations': operations}
        with self._writer():
            data = self.read()
            data['grants'].append(entry)
            self._save(data)
        return entry

    def find(self, role, operation, *, job=None, path=None):
        """Reuse an unrevoked grant without tying authority to the chat lifetime."""
        for entry in reversed(self.read()['grants']):
            try:
                return self.require(entry['id'], role, operation, job=job, path=path)
            except PermissionDenied:
                continue
        return None

    def revoke(self, grant_id, *, source):
        if not source.strip():
            raise ValueError('Revocation requires its actual source')
        with self._writer():
            data = self.read()
            entry = next((x for x in data['grants'] if x['id'] == grant_id), None)
            if entry is None:
                raise PermissionDenied('Unknown grant')
            entry.update(revoked=True, revoked_at=time.time(), revocation_source=source)
            self._save(data)
        return entry

    def require(self, grant_id, role, operation, *, job=None, path=None):
        entry = next((x for x in self.read()['grants'] if x['id'] == grant_id), None)
        if entry is None or entry.get('revoked'):
            raise PermissionDenied('A valid existing grant is required')
        if entry['project'] != str(self.project_root) or entry['role'] != role:
            raise PermissionDenied('Grant belongs to another project or workflow role')
        if entry.get('expires_at') is not None and entry['expires_at'] <= time.time():
            raise PermissionDenied('Grant expired at its explicitly chosen deadline')
        if operation not in OPERATIONS.get(role, set()) or operation not in entry.get('operations', OPERATIONS[role]):
            raise PermissionDenied('Prepare a micro-plan to request the required workflow role')
        if job is not None and not any(fnmatch.fnmatchcase(job, pattern) for pattern in entry['jobs']):
            raise PermissionDenied('Job is outside the granted scope')
        if path is not None:
            resolved = Path(path)
            if not resolved.is_absolute():
                resolved = self.project_root / resolved
            try:
                relative = resolved.resolve().relative_to(self.project_root).as_posix()
            except ValueError as ex:
                raise PermissionDenied('Path escapes the granted project') from ex
            if not any(fnmatch.fnmatchcase(relative, pattern) for pattern in entry['paths']):
                raise PermissionDenied('Path is outside the granted scope')
            kind = classify(relative)
            if kind == 'system' and role != 'development':
                raise PermissionDenied('System files require development authority')
            if kind in ('history', 'auth', 'git-state') and not (role == 'development' and operation == 'migrate' and kind == 'history'):

                raise PermissionDenied('Use the official state/auth/Git operation instead of direct file edits')
            if role == 'maintenance' and kind != 'temporary':
                raise PermissionDenied('Cleanup requires a reproducible generated-file manifest')
        return dict(entry)


def classify(relative):
    path = Path(relative)
    parts = path.parts
    if any(x in parts for x in ('.git',)):
        return 'git-state'
    if any(x in parts for x in ('.gflow', 'profiles')) or path.name in ('token.json', 'tokens.json', 'cookies.json'):
        return 'auth'
    if any(x in parts for x in ('.state', 'reviews', 'revisions', 'checkpoints', 'migration-history', 'integrity-history', 'requests', 'attempts', 'flow', 'micro-plans', 'micro-results', 'author-submissions', 'plans')) or path.name in ('integrity.json', 'integrity-meta.json', 'workflow.json', 'ledger.json', 'execution-control.json', 'brief-current.json'):
        return 'history'
    if 'runs' in parts and (path.name.endswith('.lock') or path.name in ('request.json', 'state.json') or any(x in parts for x in ('colab-tts', 'colab-render'))):
        return 'history'
    if any(x in parts for x in ('scratch', '.cache', 'bundle', 'temporary')):
        return 'temporary'
    if 'runs' in parts or 'video' in parts:
        return 'content'
    if 'vocab' in parts and path.suffix in ('.txt', '.jsonl'):
        return 'content'
    return 'system'
