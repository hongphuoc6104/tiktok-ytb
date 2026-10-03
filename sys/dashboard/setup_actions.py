"""Explicit setup operations using shared profile/Colab APIs and persistent grants.

HTTP handlers never accept arbitrary commands, credentials, URLs for fetching,
request cache paths, or out directories. Long operations hold identity locks.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re

from profile_setup import _authorize
from session_store import Sessions

RUNTIME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z')


class SetupActions:
    def __init__(self, root, *, home=None, budgets=None, client_factory=None):
        self.root = Path(root).resolve()
        self.home = Path(home or Path.home())
        self.sessions = Sessions(self.root)
        self.budgets = budgets
        self.client_factory = client_factory

    def authorize(self, data, target=None):
        return _authorize(self.root, data.get('grant'), data.get('source'), target or self.sessions.path)

    @contextmanager
    def account_lock(self, service, account):
        identity = self.budgets.read()['aliases'].get(account, account)
        key = hashlib.sha256((service + ':' + identity).encode()).hexdigest()
        path = self.budgets.path.parent / ('setup-operation-' + key + '.lock')
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open('a') as handle:
            os.chmod(path, 0o600)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ValueError('Tài khoản đang có thao tác setup; không gửi trùng') from error
            yield

    def flow(self, action, data):
        import profile_setup
        self.authorize(data, self.root / 'experiments/b2_illustrator/machine.local.json')
        if action == 'start':
            configured = json.loads((self.root / 'experiments/b2_illustrator/machine.local.json').read_text())
            if data.get('account') != configured.get('runtime_account'):
                raise ValueError('Khởi động phải dùng đúng runtime profile đã cấu hình')
            with self.account_lock('flow', data['account']):
                result = profile_setup.start(self.root, grant=data['grant'], source=data['source'])
            # Do not publish raw CDP endpoint to the frontend.
            return {key: value for key, value in result.items() if key != 'endpoint'}
        value = profile_setup.plan(self.root, data['account'], data.get('tool_url'), home=self.home,
                                  executable=data.get('executable'), reuse_account=data.get('reuse_account'))
        if action == 'configure':
            return profile_setup.configure(self.root, value, grant=data['grant'], source=data['source'])
        if action != 'plan':
            raise ValueError('Thao tác Flow không hợp lệ')
        return value

    def colab(self, action, data):
        self.authorize(data)
        account = data.get('account')
        runtime = data.get('runtime_session')
        if not isinstance(account, str) or not re.fullmatch(r'colab:[a-z0-9][a-z0-9_-]{0,47}', account) or not isinstance(runtime, str) or not RUNTIME.fullmatch(runtime):
            raise ValueError('Cần account Colab và runtime session chính xác')
        if action not in ('start', 'setup', 'reconcile', 'collect', 'stop'):
            raise ValueError('Thao tác Colab không hợp lệ')
        raw = json.loads((self.root / 'config.json').read_text())
        cfg = {**raw, 'colab_tts': {**raw.get('colab_tts', {}), 'account': account[6:], 'session': runtime,
                'management_store': str(self.budgets.path.parent), '_session_explicit': True, 'management_session': self.sessions.snapshot(data.get('job'))}}
        from colab_bridge.client import Client
        with self.account_lock('colab', account):
            client = (self.client_factory or Client)(self.root, cfg)
            if client.account != account[6:] or client.session != runtime:
                raise ValueError('Runtime adapter không khớp account/session đã chọn')
            if action == 'collect':
                result = self._collect(client, data, account, runtime)
            else:
                # Setup/stop must target an observed original session. Reconcile
                # resolves its own original allocation journal, then verifies it.
                if action in ('setup', 'stop'):
                    self._original_session(account, runtime, require_allocated=action == 'setup')
                if action == 'reconcile':
                    saved = self._original_session(account, runtime, require_allocated=False)
                    if saved['session'] != runtime:
                        raise ValueError('Đối chiếu phải dùng runtime gốc')
                getattr(client, action)()
                result = {'operation': action, 'account': account, 'runtime_session': client.session}
            return {**result, 'budget': self.budgets.snapshot(account)}

    def _original_session(self, account, runtime, require_allocated=True):
        identity = self.budgets.read()['aliases'].get(account)
        if not identity:
            raise ValueError('Chưa gắn danh tính Google cho account')
        key = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        path = self.budgets.path.parent / ('allocation-' + key + '.json')
        saved = json.loads(path.read_text()) if path.is_file() else None
        if not saved or saved.get('account') != account[6:] or saved.get('session') != runtime or saved.get('phase') == 'released':
            raise ValueError('Thao tác phải dùng allocation journal account/session gốc')
        if require_allocated and saved.get('phase') != 'allocated':
            raise ValueError('Runtime chưa được xác nhận; đối chiếu trước thao tác này')
        return saved

    def _collect(self, client, data, account, runtime):
        job, request = data.get('job'), data.get('request')
        if not isinstance(job, str) or not RUNTIME.fullmatch(job) or not isinstance(request, str) or not re.fullmatch(r'[a-f0-9]{64}', request):
            raise ValueError('Cần job và mã request gốc đã lưu')
        folder = (self.root / 'runs' / job).resolve()
        if folder.parent != (self.root / 'runs').resolve() or not folder.is_dir():
            raise ValueError('Job không hợp lệ')
        matches = []
        for path in folder.rglob('state.json'):
            if not path.resolve().is_relative_to(folder) or path.parent.name != request:
                continue
            saved = json.loads(path.read_text())
            if saved.get('account') != account[6:] or saved.get('session') != runtime:
                continue
            request_path = path.parent / 'request.json'
            payloads = []
            if request_path.is_file() and request_path.resolve().is_relative_to(folder):
                payloads = [json.loads(request_path.read_text())]
            elif path.parent.parent.name == 'colab-render':
                # The official render adapter saves the immutable request at
                # its output revision, while Client keeps owner state in cache.
                payloads = [json.loads(candidate.read_text()) for candidate in folder.rglob('request-colab-render.json')
                            if candidate.resolve().is_relative_to(folder)]
            exact = {json.dumps(payload, sort_keys=True): payload for payload in payloads
                     if payload.get('request_id') == request}
            if len(exact) == 1:
                matches.append((path, saved, next(iter(exact.values()))))
        if len(matches) != 1:
            raise ValueError('Không có đúng một request journal khớp owner account/session')
        path, saved, payload = matches[0]
        # Output stays job-scoped; adapter imports through its official collect path.
        out = folder / 'colab-collected' / request
        cache = path.parent.parent
        self.authorize(data, out)
        method = client.render if payload.get('operation') == 'render' else client.synthesize
        method(payload, out, cache, collect_only=True)
        return {'operation': 'collect', 'account': account, 'runtime_session': runtime,
                'job': job, 'request': request, 'output': str(out.relative_to(folder))}
