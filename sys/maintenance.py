"""Exact-file maintenance plans; dry-run by default, no timers or force pushes.

This enforces workflow provenance and conservative retention, not an OS sandbox.
"""
import argparse
from contextlib import ExitStack, contextmanager
import fcntl
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

from permissions import Grants, PermissionDenied, classify


class MaintenanceBlocked(RuntimeError):
    pass


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Maintenance:
    def __init__(self, system_root):
        self.system = Path(system_root).resolve()
        self.grants = Grants(self.system)
        self.project = self.grants.project_root

    def _file(self, relative):
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts or any(ord(c) < 32 for c in relative):
            raise MaintenanceBlocked('Use exact project-relative file paths')
        path = self.project / relative
        if any(p.is_symlink() for p in [path, *path.parents] if p != self.project.parent):
            raise MaintenanceBlocked('Symlinks are outside maintenance scope')
        if not path.is_file() or not path.resolve().is_relative_to(self.project):
            raise MaintenanceBlocked('Candidate must be an existing regular project file')
        if path.stat().st_nlink != 1:
            raise MaintenanceBlocked('Hard-linked files are outside maintenance scope')
        return path

    def _grant(self, grant, operation, paths=(), jobs=()):
        authority = self.grants.require(grant, 'maintenance', operation)
        for relative in paths:
            if not any(fnmatch.fnmatchcase(relative, x) for x in authority['paths']):
                raise PermissionDenied('File is outside the maintenance path allowlist')
        for job in jobs:
            if not any(fnmatch.fnmatchcase(job, x) for x in authority['jobs']):
                raise PermissionDenied('Job is outside the maintenance scope')
        return authority

    def _job(self, job):
        if not isinstance(job, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', job):
            raise MaintenanceBlocked('Exact owner job is required')
        root = self.system / 'runs' / job
        if root.is_symlink() or root.parent.is_symlink():
            raise MaintenanceBlocked('Owner job directories must not be symlinks')
        return root

    def _path_job(self, relative):
        path = self.project / relative
        for base in (self.system / 'runs', self.project / 'video'):
            try:
                parts = path.relative_to(base).parts
            except ValueError:
                continue
            if len(parts) < 2:
                raise MaintenanceBlocked('Job artifact paths need an explicit job and file')
            self._job(parts[0])
            return parts[0]
        return None

    @staticmethod
    def _credential_path(relative):
        path = Path(relative)
        return bool(re.search(r'(^\.env(?:\.|$)|token|cookie|credential|client_secret|service_account)', path.name, re.I)
                    or path.suffix.lower() in ('.pem', '.key', '.token')
                    or classify(relative) in ('auth', 'git-state'))

    @staticmethod
    def _secret_content(data):
        # Reject actual-looking assignments in quoted or plaintext credential formats.
        # Values are never included in the diagnostic or journal.
        return bool(re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ya29\.|gh[pousr]_)[A-Za-z0-9_-]{15,}|AKIA[A-Z0-9]{16}|(?i:refresh_token|access_token|client_secret|password)\s*["\']?\s*[:=]\s*(?:["\'][^"\'\n]{8,}["\']|[A-Za-z0-9_+/=-]{8,}(?=\s*(?:$|[#,;])))', data, re.M))

    @contextmanager
    def _locks(self, jobs):
        state = self.system / '.state'
        state.mkdir(parents=True, exist_ok=True)
        with ExitStack() as stack:
            handles = [stack.enter_context((state / 'maintenance.lock').open('a'))]
            for job in sorted(set(jobs)):
                root = self._job(job)
                if not root.is_dir():
                    raise MaintenanceBlocked('Owner job must still exist')
                handles.extend([stack.enter_context((root / name).open('a')) for name in ('execution-lease.lock',)])
            # v3 writers use the shared process lock. Acquiring it does not change job state.
            handles.append(stack.enter_context((state / 'process.lock').open('a')))
            for handle in handles:
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as ex:
                    raise MaintenanceBlocked('A live writer owns a maintenance target') from ex
            yield

    def _retention(self, candidates, jobs):
        for job in jobs:
            root = self._job(job)
            if not root.is_dir():
                raise MaintenanceBlocked('Owner job is missing')
            control = root / 'execution-control.json'
            if control.is_file():
                value = json.loads(control.read_text())
                if value.get('pid'):
                    try:
                        os.kill(int(value['pid']), 0)
                    except ProcessLookupError:
                        pass
                    else:
                        raise MaintenanceBlocked('Owner runner is still alive')
            for meta in root.rglob('*.json'):
                if meta.is_symlink():
                    raise MaintenanceBlocked('Symlink metadata requires separate inventory')
                try:
                    value = json.loads(meta.read_text())
                except (ValueError, OSError):
                    raise MaintenanceBlocked('Unreadable owner metadata prevents safe retention audit')
                def pending(v):
                    if isinstance(v, dict):
                        if any(str(v.get(k, '')).lower() in ('unknown', 'ambiguous', 'submitted', 'running', 'inflight', 'generating', 'not_collected', 'generated') for k in ('status', 'state', 'submit_state')):
                            return True
                        return any(pending(x) for x in v.values())
                    return isinstance(v, list) and any(pending(x) for x in v)
                if pending(value):
                    raise MaintenanceBlocked('Collect/reconcile pending owner work before maintenance')
        # A different job can reference an asset from this job: inspect all durable metadata.
        roots = [self.system / 'runs', self.project / 'video']
        for root in roots:
            if not root.is_dir():
                continue
            for meta in root.rglob('*'):
                if not meta.is_file() or meta.suffix not in ('.json', '.jsonl', '.md', '.srt') or meta in candidates:
                    continue
                if meta.is_symlink():
                    raise MaintenanceBlocked('Symlink durable metadata prevents safe retention audit')
                text = meta.read_text(errors='strict')
                directory_refs = []
                if meta.suffix in ('.json', '.jsonl'):
                    try:
                        values = [json.loads(line) for line in text.splitlines() if line.strip()] if meta.suffix == '.jsonl' else [json.loads(text)]
                    except ValueError as ex:
                        raise MaintenanceBlocked('Unreadable durable metadata prevents dependency audit') from ex
                    def strings(value):
                        if isinstance(value, str):
                            yield value
                        elif isinstance(value, dict):
                            for child in value.values():
                                yield from strings(child)
                        elif isinstance(value, list):
                            for child in value:
                                yield from strings(child)
                    for value in values:
                        for raw in strings(value):
                            if not raw or '\n' in raw or '://' in raw:
                                continue
                            ref = Path(raw)
                            options = [ref] if ref.is_absolute() else [base / ref for base in (self.project, self.system, meta.parent)]
                            directory_refs.extend(x.resolve() for x in options if x.is_dir())
                for candidate in candidates:
                    if any(candidate.is_relative_to(directory) for directory in directory_refs):
                        raise MaintenanceBlocked('Candidate directory is referenced by durable job/video evidence')
                    # File names are conservative: preserving an unneeded cache is safer than
                    # deleting the only reference when older relative paths have inconsistent bases.
                    needles = [str(candidate), candidate.relative_to(self.project).as_posix(), candidate.name]
                    if any(x in text for x in needles):
                        raise MaintenanceBlocked('Candidate is referenced by durable job/video evidence')

    def cleanup_plan(self, manifest):
        if not isinstance(manifest, dict) or manifest.get('version') != 1:
            raise MaintenanceBlocked('Versioned reproducibility manifest is required')
        items = manifest.get('files')
        if not isinstance(items, list) or not items:
            raise MaintenanceBlocked('Manifest must name exact generated files')
        paths, jobs, results = [], [], []
        for item in items:
            if not isinstance(item, dict) or not str(item.get('recipe', '')).strip():
                raise MaintenanceBlocked('Each file needs its reproducible recipe')
            path = self._file(item.get('path'))
            if classify(path.relative_to(self.project).as_posix()) != 'temporary':
                raise MaintenanceBlocked('Only generated temporary files may be deleted')
            if path in paths or path.suffix in ('.db', '.sqlite', '.sqlite3', '.token', '.pem', '.key') or re.search(r'token|cookie|credential|ledger', path.name, re.I):
                raise MaintenanceBlocked('Duplicate, secret, state or ledger candidate')
            job = item.get('owner_job')
            self._job(job)
            actual_job = self._path_job(item['path'])
            if actual_job is not None and actual_job != job:
                raise MaintenanceBlocked('Manifest owner must match the actual job artifact path')
            if not item.get('inputs') or not item.get('collected_outputs'):
                raise MaintenanceBlocked('Recipe inputs and durable collected outputs are required')
            proofs = {}
            for field in ('inputs', 'collected_outputs'):
                proofs[field] = []
                for proof in item[field]:
                    proof_path = self._file(proof.get('path'))
                    if field == 'collected_outputs' and classify(proof['path']) == 'temporary':
                        raise MaintenanceBlocked('Collected outputs must live in durable storage, not a temporary folder')
                    if proof_path == path or digest(proof_path) != proof.get('sha256'):
                        raise MaintenanceBlocked('Input/output evidence must exist and match its saved hash')
                    proofs[field].append({'path': proof['path'], 'sha256': digest(proof_path)})
            if digest(path) != item.get('sha256'):
                raise MaintenanceBlocked('Generated candidate changed since manifest was recorded')
            paths.append(path); jobs.append(job)
            results.append({'path': item['path'], 'sha256': digest(path), 'bytes': path.stat().st_size,
                            'owner_job': job, 'recipe': item['recipe'], **proofs})
        if any((self.project / proof['path']) in paths for item in results for field in ('inputs', 'collected_outputs') for proof in item[field]):
            raise MaintenanceBlocked('Recipe/output proof cannot itself be a cleanup candidate')
        self._retention(paths, jobs)
        body = {'version': 1, 'kind': 'cleanup', 'project': str(self.project), 'files': results,
                'bytes': sum(x['bytes'] for x in results)}
        return {**body, 'review_hash': fingerprint(body), 'dry_run': True}

    def _record(self, value):
        root = self.system / '.state' / 'maintenance'
        root.mkdir(parents=True, exist_ok=True)
        target = root / (str(time.time_ns()) + '-' + uuid.uuid4().hex + '.json')
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        return str(target)

    def cleanup(self, manifest, *, execute=False, grant=None, review_hash=None):
        plan = self.cleanup_plan(manifest)
        if not execute:
            return plan
        self._grant(grant, 'cleanup', [x['path'] for x in plan['files']], [x['owner_job'] for x in plan['files']])
        all_jobs = [x.name for x in (self.system / 'runs').iterdir() if x.is_dir()]
        with self._locks(all_jobs):
            fresh = self.cleanup_plan(manifest)
            if not review_hash or fresh['review_hash'] != review_hash:
                raise MaintenanceBlocked('Re-review the exact changed cleanup plan')
            # Audit intent before deletion; append a second immutable outcome afterward.
            intent = self._record({'kind': 'cleanup_intent', 'grant': grant, 'plan': fresh})
            deleted = []
            try:
                for item in fresh['files']:
                    self._file(item['path']).unlink()
                    deleted.append(item['path'])
            finally:
                result = {'kind': 'cleanup_result', 'intent': intent, 'deleted': deleted,
                          'bytes': sum(x['bytes'] for x in fresh['files'] if x['path'] in deleted), 'complete': len(deleted) == len(fresh['files'])}
                result['record'] = self._record(result)
            return result

    def authorize_archive(self, *, grant, destination, source):
        self._grant(grant, 'archive')
        if not source or not source.strip() or not isinstance(destination, str) or not Path(destination).is_absolute():
            raise MaintenanceBlocked('External archive scope requires actual authorization and an absolute destination')
        target = Path(destination)
        if '..' in target.parts or target.exists() or any(x.is_symlink() for x in target.parents):
            raise MaintenanceBlocked('Choose a new archive directory without symlink ancestors')
        entry = {'kind': 'archive_scope', 'grant': grant, 'destination': str(target), 'source': source,
                 'created_at': time.time(), 'source_transport_verified': False}
        with self._locks([]):
            entry['record'] = self._record(entry)
        return entry

    def _archive_scope(self, grant, destination):
        root = self.system / '.state' / 'maintenance'
        for path in root.glob('*.json') if root.exists() else []:
            value = json.loads(path.read_text())
            if value.get('kind') == 'archive_scope' and value.get('grant') == grant and value.get('destination') == destination:
                return value
        raise MaintenanceBlocked('External archive destination needs its recorded archive-scope authorization')

    def archive(self, *, paths, destination, grant=None, execute=False, review_hash=None):
        if not isinstance(destination, str) or not destination or '..' in Path(destination).parts:
            raise MaintenanceBlocked('Archive destination must be an explicit new directory')
        external = Path(destination).is_absolute()
        target = Path(destination) if external else self.project / destination
        if target.exists() or any(x.is_symlink() for x in target.parents):
            raise MaintenanceBlocked('Archive uses a new directory and never overwrites existing data')
        sources = [self._file(x) for x in paths]
        if not sources or len(set(paths)) != len(paths):
            raise MaintenanceBlocked('Choose exact archive source files')
        for relative in paths:
            if self._credential_path(relative):
                raise MaintenanceBlocked('Credentials/profiles are not archive artifacts')
            source = self._file(relative)
            if source.stat().st_size <= 2 * 1024 * 1024:
                try:
                    text = source.read_text()
                except UnicodeDecodeError:
                    text = ''
                if self._secret_content(text):
                    raise MaintenanceBlocked('Possible secret in archive source')
        source_jobs = sorted({job for relative in paths if (job := self._path_job(relative)) is not None})
        body = {'version': 1, 'kind': 'archive', 'project': str(self.project), 'destination': destination,
                'files': [{'path': x, 'sha256': digest(p), 'bytes': p.stat().st_size} for x, p in zip(paths, sources)]}
        plan = {**body, 'review_hash': fingerprint(body), 'dry_run': True, 'source_deletion': False}
        if not execute:
            return plan
        self._grant(grant, 'archive', paths if external else [*paths, destination + '/manifest.json', *[destination + '/' + x for x in paths]], source_jobs)
        if external:
            self._archive_scope(grant, str(target))
        if not review_hash or review_hash != plan['review_hash']:
            raise MaintenanceBlocked('Re-review this exact archive plan')
        with self._locks(source_jobs):
            self._retention([], source_jobs)
            import shutil
            target.mkdir(parents=True, exist_ok=False)
            try:
                for item in body['files']:
                    source = self._file(item['path'])
                    if digest(source) != item['sha256']:
                        raise MaintenanceBlocked('Archive source changed during copy')
                    copy = target / item['path']
                    copy.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, copy)
                    if digest(copy) != item['sha256'] or digest(source) != item['sha256']:
                        raise MaintenanceBlocked('Archive verification failed; preserve original source')
                (target / 'manifest.json').write_text(json.dumps(body, indent=2) + '\n')
            except Exception:
                self._record({'kind': 'archive_incomplete', 'destination': destination, 'source_deletion': False})
                raise
            result = {**plan, 'dry_run': False, 'verified': True}
            result['record'] = self._record(result)
            return result

    def authorize_git(self, *, grant, branch, remote='origin', allow_push=False, source):
        self._grant(grant, 'git')
        if not source or not source.strip() or not branch or branch.startswith('-') or not remote or remote.startswith('-'):
            raise MaintenanceBlocked('Git scope needs actual authorization, exact branch and remote')
        self._git('check-ref-format', 'refs/heads/' + branch)
        url = self._remote_url(remote)
        if re.search(r'https?://[^/]*@', url):
            raise MaintenanceBlocked('Remote URL contains embedded credentials')
        entry = {'kind': 'git_scope', 'grant': grant, 'branch': branch, 'remote': remote,
                 'remote_url': url, 'allow_push': bool(allow_push), 'source': source,
                 'created_at': time.time(), 'source_transport_verified': False}
        with self._locks([]):
            entry['record'] = self._record(entry)
        return entry

    def _git_scope(self, grant, branch, remote, url, push=False):
        root = self.system / '.state' / 'maintenance'
        entries = []
        for path in root.glob('*.json') if root.exists() else []:
            value = json.loads(path.read_text())
            if value.get('kind') == 'git_scope' and value.get('grant') == grant:
                entries.append(value)
        scope = max(entries, key=lambda x: x['created_at'], default={})
        if scope.get('branch') != branch or scope.get('remote') != remote or scope.get('remote_url') != url:
            raise MaintenanceBlocked('Record the actual authorized branch/remote with git-scope before checkpoint')
        if push and not scope.get('allow_push'):
            raise MaintenanceBlocked('This Git scope authorizes commit only; push needs explicit scope')
        return scope

    def _check_hooks(self, *, push=False):
        names = ['pre-commit', 'prepare-commit-msg', 'commit-msg', 'post-commit']
        if push:
            names.append('pre-push')
        configured = subprocess.run(['git', '-C', str(self.project), 'config', '--get', 'core.hooksPath'], capture_output=True, text=True)
        if configured.returncode not in (0, 1):
            raise MaintenanceBlocked('Cannot inspect effective Git hook policy')
        raw = configured.stdout.strip() if configured.returncode == 0 else self._git('rev-parse', '--git-path', 'hooks')
        root = Path(raw).expanduser()
        if not root.is_absolute():
            root = self.project / root
        active = [name for name in names if (root / name).is_file() and os.access(root / name, os.X_OK)]
        if active:
            raise MaintenanceBlocked('Git hook review required before checkpoint: ' + ', '.join(active) + '; checks are not silently bypassed')

    def _remote_url(self, remote):
        urls = self._git('remote', 'get-url', '--push', '--all', remote).splitlines()
        if len(urls) != 1:
            raise MaintenanceBlocked('A checkpoint requires exactly one authorized push URL')
        if re.search(r'https?://[^/]*@', urls[0]):
            raise MaintenanceBlocked('Remote URL contains embedded credentials')
        return urls[0]

    def _git(self, *args):
        env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        if args and args[0] in ('commit', 'push'):
            self._check_hooks(push=args[0] == 'push')
        # Existing validation hooks block above. Disable only a late hook race from
        # introducing unreviewed side effects after that exact preflight check.
        hook_policy = ['-c', 'core.hooksPath=/dev/null'] if args and args[0] in ('commit', 'push') else []
        p = subprocess.run(['git', *hook_policy, '-C', str(self.project), *args], env=env, capture_output=True, text=True)
        if p.returncode:
            raise MaintenanceBlocked('Git operation failed: ' + args[0] + '; inspect auth/conflict locally')
        return p.stdout.strip()

    def _git_bytes(self, *args):
        result = subprocess.run(['git', '-C', str(self.project), *args],
                                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}, capture_output=True)
        if result.returncode:
            raise MaintenanceBlocked('Git object audit failed; inspect auth/conflict locally')
        return result.stdout

    def _audit_git_path(self, relative, grant, reviewed_paths):
        self._grant(grant, 'git', [relative])
        if relative not in reviewed_paths:
            raise PermissionDenied('Outgoing history contains a path outside the reviewed checkpoint allowlist')
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or any(ord(c) < 32 for c in relative):
            raise MaintenanceBlocked('Invalid path in outgoing Git history')
        kind = classify(relative)
        if (kind in ('temporary', 'auth', 'git-state') or (kind == 'history' and not relative.startswith('sys/docs/'))
                or self._credential_path(relative)
                or path.suffix in ('.db', '.sqlite', '.sqlite3', '.wav', '.mp3', '.mp4', '.ogg', '.flac', '.safetensors', '.pt', '.onnx')
                or any(x in path.parts for x in ('node_modules', 'models', 'video', 'runs', '.venv'))):
            raise MaintenanceBlocked('Runtime/credential/history data in outgoing Git history')

    def _audit_git_blob(self, oid):
        size = int(self._git('cat-file', '-s', oid))
        if size > 2 * 1024 * 1024:
            raise MaintenanceBlocked('Large historical/index blob needs separate reviewed asset workflow')
        data = self._git_bytes('cat-file', 'blob', oid)
        if b'\x00' in data:
            raise MaintenanceBlocked('Binary historical/index blob needs separate reviewed asset workflow')
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError as ex:
            raise MaintenanceBlocked('Non-text historical/index blob needs separate reviewed asset workflow') from ex
        if self._secret_content(text):
            raise MaintenanceBlocked('Possible secret in historical/index blob; value withheld')

    def _outgoing(self, *, branch, url, grant, paths):
        # Inspect the *push* URL/target directly; a stale remote tracking ref is not proof.
        found = self._git('ls-remote', '--heads', '--', url, 'refs/heads/' + branch)
        rows = [x.split() for x in found.splitlines() if x.strip()]
        if len(rows) > 1 or any(len(x) != 2 or not re.fullmatch(r'[a-f0-9]{40,64}', x[0]) for x in rows):
            raise MaintenanceBlocked('Ambiguous remote target prevents outgoing audit')
        tip = rows[0][0] if rows else None
        head = self._git('rev-parse', 'HEAD')
        if tip:
            has_tip = subprocess.run(['git', '-C', str(self.project), 'cat-file', '-e', tip + '^{commit}'], capture_output=True).returncode == 0
            ancestor = subprocess.run(['git', '-C', str(self.project), 'merge-base', '--is-ancestor', tip, head], capture_output=True).returncode == 0 if has_tip else False
            if not has_tip or not ancestor:
                raise MaintenanceBlocked('Git push preflight auth/conflict: remote tip must be fetched and reconciled within scope')
        revisions = self._git('rev-list', '--reverse', head, *(['--not', tip] if tip else [])).splitlines()
        commits = []
        for commit in revisions:
            if self._secret_content(self._git('show', '-s', '--format=%B', commit)):
                raise MaintenanceBlocked('Possible secret in outgoing commit message; value withheld')
            changed = self._git_bytes('diff-tree', '--root', '-m', '--no-commit-id', '--name-only', '--no-renames', '-r', '-z', commit)
            relatives = sorted({x.decode('utf-8') for x in changed.split(b'\x00') if x})
            audited = []
            for relative in relatives:
                self._audit_git_path(relative, grant, paths)
                entry = self._git_bytes('ls-tree', '-z', commit, '--', relative)
                oid = None
                if entry:
                    mode, kind, oid = entry.split(b'\t', 1)[0].decode().split()
                    if kind != 'blob' or mode not in ('100644', '100755'):
                        raise MaintenanceBlocked('Symlink/submodule/non-file in outgoing history')
                    self._audit_git_blob(oid)
                audited.append({'path': relative, 'blob': oid})
            commits.append({'commit': commit, 'files': audited})
        return {'remote_tip': tip, 'head': head, 'commits': commits}

    def _audit_index(self, *, grant, paths):
        entries = self._git_bytes('ls-files', '--stage', '-z', '--', *paths)
        for entry in entries.split(b'\x00'):
            if not entry:
                continue
            info, relative = entry.split(b'\t', 1)
            mode, oid, stage = info.decode().split()
            relative = relative.decode('utf-8')
            self._audit_git_path(relative, grant, paths)
            if mode not in ('100644', '100755') or stage != '0':
                raise MaintenanceBlocked('Symlink/submodule/conflicted index entry')
            self._audit_git_blob(oid)

    def git_plan(self, *, branch, paths, remote='origin', grant):
        self._grant(grant, 'git', paths)
        if not branch or not remote or branch.startswith('-') or remote.startswith('-'):
            raise MaintenanceBlocked('Exact branch and configured remote are required')
        current = self._git('symbolic-ref', '--short', 'HEAD')
        if current != branch:
            raise MaintenanceBlocked('Current branch differs from the authorized checkpoint branch')
        if self._git('diff', '--cached', '--name-only'):
            raise MaintenanceBlocked('Preserve preexisting staging; complete or unstage it separately')
        if self._git('diff', '--name-only', '--diff-filter=U'):
            raise MaintenanceBlocked('Resolve existing Git conflicts within an authorized task')
        if not paths or len(set(paths)) != len(paths):
            raise MaintenanceBlocked('Choose a nonempty exact file allowlist')
        url = self._remote_url(remote)
        if re.search(r'https?://[^/]*@', url):
            raise MaintenanceBlocked('Remote URL contains embedded credentials')
        scope = self._git_scope(grant, branch, remote, url)
        outgoing = self._outgoing(branch=branch, url=url, grant=grant, paths=paths) if scope.get('allow_push') else None
        changes = []
        for relative in paths:
            if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts or any(ord(c) < 32 for c in relative):
                raise MaintenanceBlocked('Git allowlist must use exact project-relative paths')
            path = self.project / relative
            removed = not path.exists()
            if any(x.is_symlink() for x in [path, *path.parents]):
                raise MaintenanceBlocked('Symlinks are outside this Git checkpoint')
            if not removed:
                path = self._file(relative)
            else:
                self._git('ls-files', '--error-unmatch', '--', relative)
            kind = classify(relative)
            if (kind in ('temporary', 'auth', 'git-state') or (kind == 'history' and not relative.startswith('sys/docs/'))) or self._credential_path(relative) or path.suffix in ('.db', '.sqlite', '.sqlite3', '.wav', '.mp3', '.mp4', '.ogg', '.flac', '.safetensors', '.pt', '.onnx') or any(x in Path(relative).parts for x in ('node_modules', 'models', 'video', 'runs', '.venv')):
                raise MaintenanceBlocked('Runtime/history/media/model/account data cannot enter this checkpoint')
            ignored = subprocess.run(['git', '-C', str(self.project), 'check-ignore', '--quiet', '--', relative], capture_output=True).returncode
            if ignored == 0:
                raise MaintenanceBlocked('Ignored files cannot enter this checkpoint')
            if not removed:
                if path.stat().st_size > 2 * 1024 * 1024 or b'\x00' in path.read_bytes():
                    raise MaintenanceBlocked('Large/binary data requires a separate reviewed asset workflow')
                data = path.read_text(errors='strict')
                if self._secret_content(data):
                    raise MaintenanceBlocked('Possible secret in checkpoint file; inspect it without printing values')
            status = self._git('status', '--porcelain', '--untracked-files=all', '--', relative)
            if not status:
                raise MaintenanceBlocked('Allowlist includes an unchanged file')
            changes.append({'path': relative, 'sha256': None if removed else digest(path), 'status': status, 'deleted': removed})
        # Branch/remote are explicit reviewed inputs bound into the plan, not inferred later.
        body = {'version': 1, 'kind': 'git_checkpoint', 'project': str(self.project), 'grant': grant,
                'branch': branch, 'remote': remote, 'remote_url': url, 'head': self._git('rev-parse', 'HEAD'), 'files': changes, 'outgoing': outgoing}
        return {**body, 'review_hash': fingerprint(body), 'dry_run': True}

    def git_checkpoint(self, *, branch, paths, grant, remote='origin', execute=False,
                       review_hash=None, message=None, push=False):
        plan = self.git_plan(branch=branch, paths=paths, remote=remote, grant=grant)
        if not execute:
            return plan
        self._git_scope(grant, branch, remote, plan['remote_url'], push=push)
        self._check_hooks(push=push)
        if not message or not message.strip() or message.startswith('-') or self._secret_content(message):
            raise MaintenanceBlocked('Concrete commit message is required')
        with self._locks([]):
            fresh = self.git_plan(branch=branch, paths=paths, remote=remote, grant=grant)
            if not review_hash or fresh['review_hash'] != review_hash:
                raise MaintenanceBlocked('Re-review the exact changed Git checkpoint')
            intent = self._record({'kind': 'git_intent', 'plan': fresh, 'message': message, 'push': push})
            self._git('add', '--', *paths)
            staged = set(self._git('diff', '--cached', '--name-only').splitlines())
            if staged != set(paths):
                raise MaintenanceBlocked('Staged paths differ from the reviewed allowlist')
            self._git('diff', '--cached', '--check')
            self._audit_index(grant=grant, paths=paths)
            # Existing hooks require an explicit reviewed integration before any mutation.
            self._git('commit', '-m', message)
            commit = self._git('rev-parse', 'HEAD')
            result = {'kind': 'git_result', 'intent': intent, 'commit': commit, 'pushed': False, 'paths': paths}
            result['record'] = self._record(result)
            if push:
                self._outgoing(branch=branch, url=plan['remote_url'], grant=grant, paths=paths)
                self._git('push', '--no-follow-tags', '--recurse-submodules=no', '--', remote, 'HEAD:refs/heads/' + branch)
                result['pushed'] = True
                result['push_record'] = self._record(result)
            return result


def main():
    p = argparse.ArgumentParser(description='Bảo trì exact-file; mặc định chỉ xem trước')
    p.add_argument('action', choices=('cleanup', 'archive', 'archive-scope', 'git-scope', 'git'))
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    p.add_argument('--manifest', type=Path)
    p.add_argument('--grant'); p.add_argument('--review-hash'); p.add_argument('--execute', action='store_true')
    p.add_argument('--paths', nargs='+'); p.add_argument('--branch'); p.add_argument('--remote', default='origin')
    p.add_argument('--message'); p.add_argument('--push', action='store_true')
    p.add_argument('--destination'); p.add_argument('--source')
    a = p.parse_args(); m = Maintenance(a.root)
    if a.action == 'cleanup':
        if a.manifest is None:
            p.error('cleanup requires --manifest')
        result = m.cleanup(json.loads(a.manifest.read_text()), execute=a.execute, grant=a.grant, review_hash=a.review_hash)
    elif a.action == 'archive-scope':
        result = m.authorize_archive(grant=a.grant, destination=a.destination, source=a.source)
    elif a.action == 'archive':
        result = m.archive(paths=a.paths, destination=a.destination, grant=a.grant, execute=a.execute, review_hash=a.review_hash)
    elif a.action == 'git-scope':
        result = m.authorize_git(grant=a.grant, branch=a.branch, remote=a.remote, allow_push=a.push, source=a.source)
    else:
        result = m.git_checkpoint(branch=a.branch, paths=a.paths, grant=a.grant, remote=a.remote, execute=a.execute,
                                  review_hash=a.review_hash, message=a.message, push=a.push)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (MaintenanceBlocked, PermissionDenied, ValueError, OSError) as error:
        print(json.dumps({'blocked': str(error)}, ensure_ascii=False)); raise SystemExit(2)
