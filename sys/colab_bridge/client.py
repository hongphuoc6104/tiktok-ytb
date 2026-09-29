"""Authenticated CLI transport with durable request identity and collection-only recovery."""
import copy
import fcntl
import json
import os
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
        self.binary = cli()
        from .accounts import STORE, select
        self.account = select(self.cfg.get('account', 'auto')) if (STORE / 'accounts.json').exists() else None

    def call(self, *args, timeout=60, code=None):
        try:
            from .accounts import command
            argv = command(self.binary, self.account, args) if self.account else [self.binary, '--auth', 'oauth2', *args]
            p = subprocess.run(argv, input=code or '',
                               capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as ex:
            raise ColabError('COLAB_TIMEOUT: operation outcome must be reconciled') from ex
        if p.returncode:
            # OAuth URLs/codes belong in an interactive terminal, not artifact logs.
            raise ColabError(f'COLAB_COMMAND_FAILED: {args[0]} (exit {p.returncode}); '
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

    def start(self):
        self.ensure_authenticated()
        # Explicit lifecycle command only: synthesis never allocates/falls back silently.
        return self.call('new', '-s', self.session, '--gpu', 'T4', timeout=120)

    def setup(self):
        self.ensure_authenticated()
        self.exec("import subprocess\ngpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True)\nassert 'T4' in gpu, 'T4 required'\nprint(gpu)")
        return self.exec("import sys, subprocess\nsubprocess.check_call([sys.executable, '-m', 'pip', 'install', 'omnivoice==0.2.1', 'soundfile==0.13.1'])", timeout=900)

    def stop(self):
        return self.call('stop', '-s', self.session)

    def synthesize(self, request, out, cache, collect_only=False):
        out, cache = Path(out), Path(cache)
        cache.mkdir(parents=True, exist_ok=True)
        out.mkdir(parents=True, exist_ok=True)
        worker = Path(__file__).with_name('worker.py')
        req = copy.deepcopy(request)
        req['worker_sha256'] = file_hash(worker)
        req['request_id'] = stamp(dict(request=req['request_id'], worker=req['worker_sha256']))
        folder = cache / req['request_id']
        folder.mkdir(exist_ok=True)
        state_path = folder / 'state.json'
        # Serialize access across jobs/checkouts to this Colab session, not just one job.
        lock_dir = Path.home() / '.cache/video-pilot-colab'
        lock_dir.mkdir(parents=True, exist_ok=True)
        saved = json.loads(state_path.read_text()) if state_path.exists() else {}
        if saved.get('account'):
            from .accounts import select
            self.account = select(saved['account'])
            self.session = saved.get('session', self.session)
        lock = lock_dir / (stamp([self.account, self.session]) + '.lock')
        with lock.open('a') as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as ex:
                raise ColabError('COLAB_SESSION_BUSY: another request owns this session') from ex
            try:
                if (folder / 'result/tts-result.json').exists():
                    return self._import(folder / 'result', out, req)
                self.ensure_authenticated()
                remote = '/content/video-pilot-tts/' + req['request_id']
                state = json.loads(state_path.read_text()) if state_path.exists() else {}
                if state.get('phase') in ('submitted', 'ambiguous', 'complete') or collect_only:
                    # Never automatically repeat execution after an uncertain send.
                    self._download(remote, folder, req)
                else:
                    self.exec(f'from pathlib import Path\nPath({remote!r}).mkdir(parents=True, exist_ok=True)')
                    for lang, profile in req['profiles'].items():
                        dest = remote + '/' + lang + '.wav'
                        self.call('upload', '-s', self.session, profile.pop('local_wav'), dest, timeout=120)
                        profile['remote_wav'] = dest
                    request_file = folder / 'request.json'
                    request_file.write_text(json.dumps(req, ensure_ascii=False, indent=2))
                    remote_worker = remote + '/worker.py'
                    self.call('upload', '-s', self.session, str(worker), remote_worker, timeout=120)
                    self.call('upload', '-s', self.session, str(request_file), remote + '/request.json', timeout=120)
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
                return self._import(folder / 'result', out, req)
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
                    if Path(entry.filename).suffix not in ('.wav', '.json'):
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
