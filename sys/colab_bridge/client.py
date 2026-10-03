"""Authenticated CLI transport with durable request identity and collection-only recovery."""
import copy
import fcntl
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid
import zipfile

from .protocol import file_hash, stamp, validate_result


class ColabError(RuntimeError):
    pass


def enabled(cfg):
    return cfg.get('colab_tts', {}).get('enabled') is True


def cli():
    binary = shutil.which('colab') or str(Path.home() / '.local/bin/colab')
    if not Path(binary).is_file():
        raise ColabError('COLAB_CLI_MISSING: install google-colab-cli==0.7.4 with uv tool install')
    return binary


def issue(root, message):
    folder = root / 'logs/issues'
    folder.mkdir(parents=True, exist_ok=True)
    name = f'colab-{time.time_ns()}.md'
    (folder / name).write_text('# Sự cố Colab TTS\n\n' + message + '\n\nLàm gì cho hết lỗi: '
                              'xem trạng thái phiên; đăng nhập/cấp lại T4 khi cần. '
                              'Nếu đã gửi yêu cầu, dùng collect để lấy kết quả trước khi quyết định chạy lại.\n')
    with (folder / 'INDEX.md').open('a') as f:
        f.write(f'\n- [{name}]({name}) — Colab TTS cần kiểm tra.\n')


class Client:
    def __init__(self, root, cfg):
        self.root = Path(root)
        self.cfg = cfg['colab_tts']
        self.session = self.cfg.get('session', 'video-pilot-tts')
        if self.cfg.get('_session_explicit') and (not isinstance(self.session, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', self.session)):
            raise ColabError('COLAB_SESSION_INVALID: exact lifecycle session required')
        self.binary = cli()
        from .accounts import STORE, select
        from session_store import Sessions
        self.management = Sessions(self.root)
        selection = self.cfg.get('management_session', self.management.snapshot(self.cfg.get('job_id')))
        default = selection.get('defaults', {}).get('colab')
        choice = self.cfg.get('account', 'auto')
        binding = selection.get('runtime_bindings', {}).get('colab')
        if binding and not self.cfg.get('_session_explicit', False):
            alias = binding.get('account')
            session = binding.get('runtime_session')
            if (binding.get('service') != 'colab' or not isinstance(alias, str) or not alias.startswith('colab:')
                    or not isinstance(session, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', session)
                    or ('pool' in selection and alias not in selection['pool'])):
                raise ColabError('COLAB_RUNTIME_BINDING_INVALID: exact selected account/session required')
            account = alias.removeprefix('colab:')
            from .accounts import folder
            folder(account)
            if choice not in ('auto', account):
                raise ColabError('COLAB_RUNTIME_BINDING_ACCOUNT_MISMATCH: explicit account differs from frozen runtime')
            choice = account
            self.session = session
        elif choice == 'auto' and default:
            if not default.startswith('colab:'): raise ColabError('COLAB_SELECTION_INVALID')
            choice = default.removeprefix('colab:')
        if (STORE / 'accounts.json').exists():
            try: self.account = select(choice)
            except ValueError:
                if choice == 'auto':
                    from .accounts import registry
                    self.account = registry().get('preferred')
                else:
                    from .accounts import folder
                    folder(choice)  # Validate the explicit ID; no account rotation.
                    self.account = choice
        else: self.account = None

    def call(self, *args, timeout=60, code=None):
        try:
            from .accounts import command
            argv = command(self.binary, self.account, args) if self.account else [self.binary, '--auth', 'oauth2', *args]
            p = subprocess.run(argv, input=code or '',
                               capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as ex:
            raise ColabError('COLAB_TIMEOUT: operation outcome must be reconciled') from ex
        if p.returncode:
            observed = (p.stdout + '\n' + p.stderr).lower()
            rules = [('captcha', r'captcha'), ('bot', r'unusual activity|automated requests|abuse detected'),
                     ('429', r'\b429\b|rate limit'), ('503', r'\b503\b'),
                     ('quota', r'quota.{0,24}(exceed|exhaust)|resource.{0,24}limit'),
                     ('login_required', r'invalid_grant|token.{0,24}(expired|revoked)|login required|sign.?in required')]
            kind = next((kind for kind, pattern in rules if re.search(pattern, observed)), None)
            if kind:
                evidence = self._observation('provider-blocked', operation=args[0], error_category=kind)
                alias = 'colab:' + self.account if self.account else None
                budgets = self._budgets()
                if alias and budgets.snapshot(alias)['identity_configured']:
                    try: budgets.recover(alias, 'colab', 'command:' + args[0], action='reconcile', error=kind, submit_state='unknown', evidence=evidence)
                    except ValueError: pass  # The service block was durably recorded; no recovery loop.
                raise ColabError('COLAB_PROVIDER_BLOCKED: ' + kind + '; preserve owner and request; do not rotate account')
            if re.search(r"session\s+['\"]?[^\n]+?['\"]?\s+not found|no active sessions found|unknown session", observed):
                raise ColabError(f'COLAB_SESSION_NOT_FOUND: {self.session}; reconcile authenticated server assignments; local mapping alone does not prove termination')
            error_type = next((name for name in ('TimeoutError', 'ConnectionError', 'RuntimeError', 'ValueError', 'KeyError') if name.lower() in observed), 'CommandExit')
            # OAuth URLs/codes belong in an interactive terminal, not artifact logs.
            raise ColabError(f'COLAB_COMMAND_FAILED: {args[0]} (exit {p.returncode}, type={error_type}); '
                             'check colab --auth oauth2 sessions in your terminal')
        return p.stdout

    def exec(self, code, timeout=60):
        marker = 'VP_EXEC_OK_' + uuid.uuid4().hex
        output = self.call('exec', '-s', self.session, '--timeout', str(max(1, timeout - 5)), code=code + f'\nprint({marker!r}, flush=True)\n', timeout=timeout)
        if marker not in [line.strip() for line in output.splitlines()]:
            raise ColabError('COLAB_EXEC_UNCONFIRMED: remote code did not finish successfully')
        return output

    def ensure_authenticated(self):
        from .accounts import folder
        token = folder(self.account) / 'token.json' if self.account else Path.home() / '.config/colab-cli/token.json'
        if not token.is_file():
            raise ColabError('COLAB_LOGIN_REQUIRED: run colab --auth oauth2 sessions in a terminal')

    def _budgets(self):
        from account_budget import Budgets
        return Budgets(self.cfg.get('management_store'))

    def _alias(self):
        if not self.account: raise ColabError('COLAB_VERIFIED_SETUP_REQUIRED: select a named account')
        return 'colab:' + self.account

    def _observation(self, kind, **values):
        folder = self.root / '.state/colab-observations';folder.mkdir(parents=True, exist_ok=True)
        path = folder / (kind + '-' + str(time.time_ns()) + '.json')
        self._state(path, kind=kind, account=self.account, session=self.session, **values)
        return str(path.resolve())

    def _ready(self):
        budgets = self._budgets(); alias = self._alias()
        status = budgets.snapshot(alias)
        intervals = [item for item in status['allocated_sessions'] if item['session'] == self.session and item.get('device') == 'T4']
        if not status['identity_configured'] or not intervals or status['uncertain'] or status['blocks'].get('colab'):
            raise ColabError('COLAB_VERIFIED_SETUP_REQUIRED: confirmed identity and allocated T4 session required')
        if status['needs_service_recheck']:
            raise ColabError('COLAB_SERVICE_RECHECK_REQUIRED: verify current account/session T4 before new-window work')
        return budgets, alias

    def _reserve(self, request, operation):
        budgets, alias = self._ready()
        seconds = int(self.cfg.get('render_estimate_seconds', 1800) if operation == 'render' else self.cfg.get('audio_estimate_seconds', 600))
        try:
            budgets.reserve(alias, request, seconds)
            self.management.pin(request, job=self.cfg.get('job_id', request), service='colab', account=alias,
                                session=self.session, identity=budgets.read()['aliases'][alias])
        except ValueError as ex: raise ColabError('COLAB_BUDGET_BLOCKED: ' + str(ex)) from ex

    def _settle(self, request):
        # Collection remains possible even when setup/budget is no longer available.
        budgets = self._budgets()
        alias = 'colab:' + self.account if self.account else None
        if alias and budgets.snapshot(alias)['identity_configured']: budgets.settle(alias, request)

    def start(self):
        self.ensure_authenticated()
        budgets = self._budgets();alias = self._alias()
        identity = budgets.read().get('aliases', {}).get(alias)
        if not identity: raise ColabError('COLAB_VERIFIED_SETUP_REQUIRED: verified provider identity required')
        journal = budgets.path.parent / ('allocation-' + stamp(identity) + '.json')
        journal.parent.mkdir(parents=True, exist_ok=True)
        with journal.with_suffix('.lock').open('a') as lock:
            try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as ex: raise ColabError('COLAB_ACCOUNT_BUSY') from ex
            previous = json.loads(journal.read_text()) if journal.exists() else {}
            if previous.get('phase') in ('submitted', 'ambiguous', 'allocated'):
                raise ColabError('COLAB_ALLOCATION_PENDING: inspect/collect/release the existing exact session; never allocate twice')
            status = budgets.snapshot(alias)
            if not status['identity_configured'] or status['allocated_sessions'] or status['blocks'].get('colab') or status['available_seconds'] <= 0:
                raise ColabError('COLAB_VERIFIED_SETUP_REQUIRED: verify identity and available internal budget before allocation')
            start = time.time()
            self._state(journal, phase='submitted', account=self.account, session=self.session, allocation_started_at=start)
            try:
                result = self.call('new', '-s', self.session, '--gpu', 'T4', timeout=120)
                output = self.exec("import subprocess, json\ngpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True).strip()\nprint('VP_GPU=' + json.dumps(gpu))")
                matches = [line for line in output.splitlines() if line.startswith('VP_GPU=')]
                device = json.loads(matches[-1][7:]) if matches else ''
                if 'T4' not in device: raise ColabError('COLAB_T4_NOT_CONFIRMED: preserve allocated session; no CPU fallback')
                evidence = self._observation('allocated', device=device, allocation_started_at=start)
                budgets.allocated(alias, self.session, device='T4', at=start, evidence=evidence)
                budgets.service_rechecked(alias, self.session, device='T4', evidence=evidence)
                self._state(journal, phase='allocated', account=self.account, session=self.session, evidence=evidence, allocation_started_at=start)
            except Exception as ex:
                evidence = self._observation('allocation-unknown', error=str(ex), allocation_started_at=start)
                self._state(journal, phase='ambiguous', account=self.account, session=self.session, evidence=evidence, allocation_started_at=start)
                issue(self.root, str(ex)); raise
            return result

    def _assignment_state(self):
        from .accounts import assignment_state
        return assignment_state(self.binary, self.account, self.session)

    def reconcile(self):
        """Explicit read-only reconciliation of an allocation whose send was uncertain."""
        budgets = self._budgets();alias = self._alias()
        identity = budgets.read().get('aliases', {}).get(alias)
        if not identity: raise ColabError('COLAB_VERIFIED_SETUP_REQUIRED: verified provider identity required')
        journal = budgets.path.parent / ('allocation-' + stamp(identity) + '.json')
        if not journal.exists(): raise ColabError('COLAB_ALLOCATION_JOURNAL_REQUIRED')
        with journal.with_suffix('.lock').open('a') as lock:
            try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as ex: raise ColabError('COLAB_ACCOUNT_BUSY') from ex
            saved = json.loads(journal.read_text())
            if saved.get('account') != self.account: raise ColabError('COLAB_ALLOCATION_OWNER_MISMATCH')
            self.session = saved['session']
            self.ensure_authenticated()
            observed = self._assignment_state()
            if observed.get('verified') is not True:
                evidence = self._observation('allocation-unverified', observation=observed)
                if any(item['session'] == self.session for item in budgets.snapshot(alias)['allocated_sessions']):
                    budgets.uncertain(alias, self.session, evidence)
                raise ColabError('COLAB_ASSIGNMENT_UNVERIFIED: ' + observed.get('reason', 'unknown') + '; preserve allocation')
            if observed.get('identity') != identity:
                raise ColabError('COLAB_ALLOCATION_OWNER_MISMATCH: authenticated provider identity differs')
            if observed.get('assignment_count') == 0:
                evidence = self._observation('server-runtime-absent', observation=observed)
                if any(item['session'] == self.session for item in budgets.snapshot(alias)['allocated_sessions']):
                    budgets.released(alias, self.session, evidence=evidence)
                self._state(journal, **dict(saved, phase='released', release_evidence=evidence, release_reason='authenticated_server_no_assignments'))
                return {'account': self.account, 'session': self.session, 'state': 'released', 'source': observed['source'], 'evidence': evidence}
            if observed.get('named_assignment_active') is not True:
                evidence = self._observation('local-session-mapping-uncertain', observation=observed)
                if any(item['session'] == self.session for item in budgets.snapshot(alias)['allocated_sessions']):
                    budgets.uncertain(alias, self.session, evidence)
                raise ColabError('COLAB_LOCAL_SESSION_MAPPING_MISSING: server assignment exists; preserve allocation and reconcile the account mapping')
            output = self.exec("import subprocess, json\ngpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True).strip()\nprint('VP_GPU=' + json.dumps(gpu))")
            values = [line for line in output.splitlines() if line.startswith('VP_GPU=')]
            device = json.loads(values[-1][7:]) if values else ''
            if 'T4' not in device: raise ColabError('COLAB_T4_NOT_CONFIRMED')
            evidence = self._observation('allocation-reconciled', device=device, allocation_started_at=saved['allocation_started_at'])
            if not any(item['session'] == self.session for item in budgets.snapshot(alias)['allocated_sessions']):
                budgets.allocated(alias, self.session, device='T4', at=saved['allocation_started_at'], evidence=evidence)
            budgets.service_rechecked(alias, self.session, device='T4', evidence=evidence)
            self._state(journal, **dict(saved, phase='allocated', evidence=evidence))
            return {'account': self.account, 'session': self.session, 'device': device, 'evidence': evidence}

    def setup(self):
        self.ensure_authenticated()
        self.exec("import subprocess\ngpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True)\nassert 'T4' in gpu, 'T4 required'\nprint(gpu)")
        return self.exec("import sys, subprocess\nsubprocess.check_call([sys.executable, '-m', 'pip', 'install', 'omnivoice==0.2.1', 'soundfile==0.13.1'])", timeout=900)

    def stop(self):
        result = self.call('stop', '-s', self.session)
        budgets = self._budgets();alias = 'colab:' + self.account if self.account else None
        evidence = self._observation('released', command_confirmed=True)
        if alias and any(item['session'] == self.session for item in budgets.snapshot(alias)['allocated_sessions']):
            budgets.released(alias, self.session, evidence=evidence)
        identity = budgets.read().get('aliases', {}).get(alias) if alias else None
        if identity:
            journal = budgets.path.parent / ('allocation-' + stamp(identity) + '.json')
            if journal.exists():
                old = json.loads(journal.read_text())
                if old.get('session') == self.session:
                    self._state(journal, **dict(old, phase='released', release_evidence=evidence))
        return result

    def synthesize(self, request, out, cache, collect_only=False, before_submit=None):
        out, cache = Path(out), Path(cache)
        cache.mkdir(parents=True, exist_ok=True)
        out.mkdir(parents=True, exist_ok=True)
        with (cache / 'intent.lock').open('a') as intent_lock:
            try: fcntl.flock(intent_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as ex: raise ColabError('COLAB_REQUEST_BUSY') from ex
            worker = Path(__file__).with_name('worker.py')
            req = copy.deepcopy(request)
            if not (collect_only and req.get('worker_sha256')):
                req['source_request_id'] = request['request_id']
                req['worker_sha256'] = file_hash(worker)
                req['request_id'] = stamp(dict(request=req['request_id'], worker=req['worker_sha256']))
            for pending in cache.glob('*/state.json'):
                state = json.loads(pending.read_text())
                if state.get('phase') not in ('submitted', 'ambiguous'): continue
                saved_request = pending.parent / 'request.json'
                if not saved_request.exists(): raise ColabError('COLAB_PENDING_REQUEST_MISSING: preserve journal')
                old = json.loads(saved_request.read_text())
                # A code update may change worker identity; it cannot make an old send disappear.
                if old.get('source_request_id') != request.get('source_request_id', request['request_id']) and old.get('request_id') != request['request_id']:
                    raise ColabError('COLAB_PENDING_OTHER_REQUEST: collect the existing pinned request before new work')
                req = old
                break
            (out / 'request-colab-effective.json').write_text(json.dumps(req, ensure_ascii=False, indent=2))
            folder = cache / req['request_id']
            folder.mkdir(exist_ok=True)
            state_path = folder / 'state.json'
            # Serialize access across jobs/checkouts to this Colab session, not just one job.
            lock_dir = Path.home() / '.cache/video-pilot-colab'
            lock_dir.mkdir(parents=True, exist_ok=True)
            with (folder / 'request.lock').open('a') as request_lock:
                try: fcntl.flock(request_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as ex: raise ColabError('COLAB_REQUEST_BUSY') from ex
                saved = json.loads(state_path.read_text()) if state_path.exists() else {}
                if saved:
                    self.account = saved.get('account')
                    if self.account:
                        from .accounts import folder as account_folder
                        account_folder(self.account)
                    self.session = saved.get('session', self.session)
                lock = lock_dir / (stamp([self.account, self.session]) + '.lock')
                with lock.open('a') as handle:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError as ex:
                        raise ColabError('COLAB_SESSION_BUSY: another request owns this session') from ex
                    try:
                        if (folder / 'result/tts-result.json').exists():
                            imported = self._import(folder / 'result', out, req)
                            if req.get('assemble'): self._settle(req['request_id'])
                            return imported
                        if collect_only and not state_path.exists(): raise ColabError('COLAB_REQUEST_NOT_SUBMITTED: saved request journal required')
                        self.ensure_authenticated()
                        remote = '/content/video-pilot-tts/' + req['request_id']
                        state = json.loads(state_path.read_text()) if state_path.exists() else {}
                        if state.get('phase') in ('submitted', 'ambiguous', 'complete') or collect_only:
                            # Never automatically repeat execution after an uncertain send.
                            attempts = int(state.get('collection_attempts', 0))
                            if attempts >= 3: raise ColabError('COLAB_RECOVERY_LIMIT: needs attention; preserve pinned request')
                            self._state(state_path, **dict(state, phase=state.get('phase', 'ambiguous'), collection_attempts=attempts + 1))
                            self._download(remote, folder, req)
                        else:
                            if before_submit is not None: before_submit()
                            if req.get('assemble'): self._ready()
                            self.exec(f'from pathlib import Path\nPath({remote!r}).mkdir(parents=True, exist_ok=True)')
                            for lang, profile in req['profiles'].items():
                                dest = remote + '/' + lang + '.wav'
                                self.call('upload', '-s', self.session, profile.pop('local_wav'), dest, timeout=120)
                                profile['remote_wav'] = dest
                            for support in req.get('support_files', []):
                                local = Path(support.pop('local_path'))
                                if Path(support['name']).name != support['name'] or file_hash(local) != support['sha256']:
                                    raise ColabError('COLAB_SUPPORT_CHANGED: remote processing source changed')
                                support['remote_path'] = remote + '/' + support['name']
                                self.call('upload', '-s', self.session, str(local), support['remote_path'], timeout=120)
                            request_file = folder / 'request.json'
                            request_file.write_text(json.dumps(req, ensure_ascii=False, indent=2))
                            remote_worker = remote + '/worker.py'
                            self.call('upload', '-s', self.session, str(worker), remote_worker, timeout=120)
                            self.call('upload', '-s', self.session, str(request_file), remote + '/request.json', timeout=120)
                            if before_submit is not None: before_submit()
                            if req.get('assemble'): self._reserve(req['request_id'], 'audio')
                            self._state(state_path, phase='submitted', remote=remote, request_id=req['request_id'], account=self.account, session=self.session)
                            module = 'vp_tts_' + req['worker_sha256'][:16]
                            code = ("import importlib.util, sys\n"
                                    f"if {module!r} not in sys.modules:\n"
                                    f"    spec = importlib.util.spec_from_file_location({module!r}, {remote_worker!r})\n"
                                    "    m = importlib.util.module_from_spec(spec)\n"
                                    f"    sys.modules[{module!r}] = m\n"
                                    "    spec.loader.exec_module(m)\n"
                                    f"sys.modules[{module!r}].run({(remote + '/request.json')!r}, {(remote + '/output')!r})\n")
                            self.exec(code, timeout=int(self.cfg.get('timeout_seconds', 1800)))
                            self._download(remote, folder, req)
                        self._state(state_path, phase='complete', remote=remote, request_id=req['request_id'], account=self.account, session=self.session)
                        imported = self._import(folder / 'result', out, req)
                        if req.get('assemble'): self._settle(req['request_id'])
                        return imported
                    except Exception as ex:
                        if state_path.exists():
                            state = json.loads(state_path.read_text())
                            self._state(state_path, **dict(state, phase='ambiguous', error=str(ex)))
                        issue(self.root, str(ex))
                        raise

    @staticmethod
    def _state(path, **data):
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(data, updated_at=time.time()), indent=2))
        tmp.replace(path)

    def _download(self, remote, folder, req):
        archive = folder / 'download.zip'
        self.call('download', '-s', self.session, remote + '/output.zip', str(archive), timeout=180)
        with tempfile.TemporaryDirectory(dir=folder) as temp:
            staging = Path(temp)
            with zipfile.ZipFile(archive) as z:
                infos = z.infolist()
                if sum(x.file_size for x in infos) > 2_000_000_000:
                    raise ColabError('COLAB_RESULT_TOO_LARGE')
                names = [x.filename for x in infos]
                if len(names) != len(set(names)):
                    raise ColabError('COLAB_DUPLICATE_ARTIFACT')
                for entry in infos:
                    if Path(entry.filename).name != entry.filename or entry.is_dir() or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ColabError('COLAB_UNSAFE_ARTIFACT_PATH')
                    if Path(entry.filename).suffix not in (('.wav','.json','.srt') if req.get('assemble') else ('.wav','.json')):
                        raise ColabError('COLAB_UNEXPECTED_ARTIFACT')
                    z.extract(entry, staging)
            validate_result(staging, req)
            shutil.copytree(staging, folder / 'result', dirs_exist_ok=True)

    @staticmethod
    def _import(source, out, req):
        names = validate_result(source, req)
        for name in names:
            shutil.copy2(source / name, out / name)
        (out / 'tts.log').write_text('Colab result validated; request_id=' + req['request_id'] + '\n')
        return req['request_id']

    def render(self, request, out, cache, collect_only=False, before_submit=None):
        """Generic remote work. Unknown execution is always collected on its pinned owner."""
        from .job_protocol import bundle, extract, validate_render_result
        out, cache = Path(out), Path(cache)
        out.mkdir(parents=True, exist_ok=True)
        cache.mkdir(parents=True, exist_ok=True)
        with (cache / 'intent.lock').open('a') as intent_lock:
            try: fcntl.flock(intent_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as ex: raise ColabError('COLAB_REQUEST_BUSY') from ex
            for pending in cache.glob('*/state.json'):
                saved = json.loads(pending.read_text())
                if saved.get('phase') in ('submitted', 'ambiguous') and saved.get('request_id') != request['request_id']:
                    raise ColabError('COLAB_PENDING_OTHER_REQUEST: collect the existing pinned request before new work')
            folder = cache / request['request_id']; folder.mkdir(parents=True, exist_ok=True)
            state_path = folder / 'state.json'
            with (folder / 'request.lock').open('a') as request_lock:
                try: fcntl.flock(request_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as ex: raise ColabError('COLAB_REQUEST_BUSY') from ex
                saved = json.loads(state_path.read_text()) if state_path.exists() else {}
                if saved:
                    self.account = saved.get('account')
                    if self.account:
                        from .accounts import folder as account_folder
                        account_folder(self.account)
                    self.session = saved['session']
                locks = Path.home() / '.cache/video-pilot-colab'; locks.mkdir(parents=True, exist_ok=True)
                with (locks / (stamp([self.account, self.session]) + '.lock')).open('a') as lock:
                    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError as ex: raise ColabError('COLAB_SESSION_BUSY') from ex
                    remote = saved.get('remote', '/content/video-pilot-jobs/' + request['request_id'])
                    try:
                        result = folder / 'result'
                        if not (result / 'render-result.json').exists():
                            self.ensure_authenticated()
                            if not saved or saved.get('phase') == 'prepared':
                                if collect_only: raise ColabError('COLAB_REQUEST_NOT_SUBMITTED')
                                archive = folder / 'input.zip'; bundle(request, archive)
                                worker = Path(__file__).with_name('job_worker.py')
                                if file_hash(worker) != request['worker_sha256']: raise ColabError('COLAB_WORKER_CHANGED')
                                if before_submit is not None: before_submit()
                                self._ready()
                                self.exec(f'from pathlib import Path\nPath({remote!r}).mkdir(parents=True, exist_ok=True)')
                                self.call('upload', '-s', self.session, str(archive), remote + '/input.zip', timeout=180)
                                self.call('upload', '-s', self.session, str(worker), remote + '/job_worker.py', timeout=120)
                                if before_submit is not None: before_submit()
                                self._reserve(request['request_id'], 'render')
                                self._state(state_path, phase='submitted', account=self.account, session=self.session, remote=remote, request_id=request['request_id'])
                                module = 'vp_render_' + request['worker_sha256'][:16]
                                code = ("import importlib.util\n"
                                        f"spec = importlib.util.spec_from_file_location({module!r}, {(remote + '/job_worker.py')!r})\n"
                                        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                                        f"m.run({(remote + '/input.zip')!r}, {(remote + '/output')!r}, {request['request_id']!r}, {request['worker_sha256']!r})\n")
                                self.exec(code, timeout=int(self.cfg.get('render_timeout_seconds', 5400)))
                            if saved and saved.get('phase') != 'prepared':
                                attempts = int(saved.get('collection_attempts', 0))
                                if attempts >= 3: raise ColabError('COLAB_RECOVERY_LIMIT: needs attention; preserve pinned request')
                                self._state(state_path, **dict(saved, collection_attempts=attempts + 1))
                            archive = folder / 'output.zip'
                            self.call('download', '-s', self.session, remote + '/output.zip', str(archive), timeout=300)
                            with tempfile.TemporaryDirectory(dir=folder) as tmp:
                                staging = Path(tmp); extract(archive, staging, flat=True)
                                validate_render_result(staging, request)
                                shutil.copytree(staging, result, dirs_exist_ok=True)
                        names = validate_render_result(result, request)
                        for name in names: shutil.copy2(result / name, out / name)
                        self._state(state_path, phase='complete', account=self.account, session=self.session, remote=remote, request_id=request['request_id'])
                        self._settle(request['request_id'])
                        return request['request_id']
                    except Exception as ex:
                        if state_path.exists():
                            state = json.loads(state_path.read_text())
                            self._state(state_path, **dict(state, phase='ambiguous', error=str(ex)))
                        issue(self.root, str(ex))
                        raise
