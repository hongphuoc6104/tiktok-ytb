"""Read metadata and invoke the public CLI; never write job state/SQLite."""
import hashlib
import json
import mimetypes
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import threading
import time
from urllib.parse import quote

from account_catalog import discover, login_handoff, confirm_identity, probe_colab
from account_budget import Budgets
from session_store import Sessions
from dashboard.setup_actions import SetupActions

JOB = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z')
SECRET = re.compile(r'token|cookie|credential|password|secret|oauth|authorization|code_verifier|^code$', re.I)
MEDIA = {'.wav', '.mp3', '.ogg', '.m4a', '.flac', '.png', '.jpg', '.jpeg', '.webp', '.mp4', '.srt', '.vtt', '.json', '.md', '.txt'}


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items() if not SECRET.search(str(k))}
    if isinstance(value, list):
        return [safe(x) for x in value]
    if isinstance(value, str):
        # Never send URLs carrying OAuth codes/query secrets or bearer literals.
        if re.search(r'(?i)(bearer\s+\S+|https?://[^\s]*(?:oauth|[?&](?:code|token|key|access_token)=))', value):
            return '[Dữ liệu xác thực đã ẩn]'
        return value
    return value


def read_json(path):
    try:
        if path.stat().st_size > 8 * 1024 * 1024:
            return {'error': 'metadata_too_large'}
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


class Dashboard:
    def __init__(self, root, *, python=None, cli=None, home=None, budget_store=None, client_factory=None):
        self.root = Path(root).resolve()
        managed = self.root / '.venv-management/bin/python'
        self.python = python or (str(managed) if managed.is_file() else sys.executable)
        self._cli = cli
        self.home = Path(home or Path.home())
        self.sessions = Sessions(self.root)
        self.budgets = Budgets(budget_store or self.home / '.config/video-pilot/management')
        self.setup = SetupActions(self.root, home=self.home, budgets=self.budgets, client_factory=client_factory)
        self.operations = {}
        self.operation_lock = threading.Lock()

    def job_path(self, job):
        if not isinstance(job, str) or not JOB.fullmatch(job) or job in ('.', '..'):
            raise ValueError('Mã job không hợp lệ')
        path = (self.root / 'runs' / job).resolve()
        if path.parent != (self.root / 'runs').resolve() or not path.is_dir():
            raise ValueError('Không tìm thấy job')
        return path

    def cli(self, argv):
        if self._cli:
            return safe(self._cli(argv))
        proc = subprocess.run([self.python, str(self.root / 'pilot.py'), *argv], cwd=self.root,
                              capture_output=True, text=True, timeout=600)
        try:
            result = json.loads(proc.stdout)
        except ValueError:
            result = {'blocked': 'CLI chưa trả metadata JSON; kiểm bootstrap/environment.', 'exit_code': proc.returncode}
        return safe(result)

    def jobs(self):
        folder = self.root / 'runs'
        return [self.job(p.name) for p in sorted(folder.iterdir()) if p.is_dir() and JOB.fullmatch(p.name) and ((p / 'workflow.json').is_file() or (p / 'brief-current.json').is_file())] if folder.is_dir() else []

    def job(self, job):
        folder = self.job_path(job)
        state = self.cli(['status', job])
        next_step = self.cli(['next', job])
        # Manifests are immutable engine output; expose exact revision, no synthesized approval.
        checkpoints = []
        artifacts = {}
        for phase in ('outline', 'dialogue', 'audio', 'images', 'video'):
            candidates = [x for x in (folder / 'checkpoints' / phase).glob('*/manifest.json') if x.parent.name.isdigit()]
            if not candidates:
                continue
            path = max(candidates, key=lambda x: int(x.parent.name))
            manifest = self._metadata(folder, path)
            if not isinstance(manifest, dict):
                continue
            revision = manifest.get('revision')
            checkpoint = {'phase': phase, 'revision': revision, 'payload': safe(manifest.get('payload')),
                          'review': manifest.get('review'), 'assets': []}
            for name in [*manifest.get('assets', []), manifest.get('review')]:
                if not isinstance(name, str):
                    continue
                metadata = self._asset(job, name, phase, revision)
                if metadata:
                    checkpoint['assets'].append(metadata)
                    self._register(artifacts, metadata)
            # Gallery JSON contains explicit raw scene/reference paths. No local resizing.
            for name in manifest.get('assets', []):
                if isinstance(name, str) and name.endswith('.json'):
                    path = self._resolve(job, name)
                    payload = read_json(path) if path else None
                    self._gallery(job, payload, phase, revision, checkpoint, artifacts)
            checkpoints.append(checkpoint)
        # Legacy envelopes are products too, but no v4 quality decision is invented.
        for envelope in folder.glob('revisions/*/*/envelope.json'):
            value = self._metadata(folder, envelope)
            if isinstance(value, dict):
                for name in value.get('files', []):
                    if isinstance(name, str):
                        metadata = self._asset(job, name, value.get('module', 'legacy'), value.get('revision'))
                        if metadata:
                            self._register(artifacts, metadata)
        # Product tabs show the outputs of current owning checkpoints. Shared
        # render inputs remain downloadable details with original provenance.
        products = {}
        for checkpoint in checkpoints:
            phase = checkpoint['phase']
            payload = checkpoint.get('payload') or {}
            for name in self._products(payload, phase):
                products.setdefault(name, (phase, checkpoint['revision']))
        current = {item['phase']: item['revision'] for item in checkpoints}
        for metadata in artifacts.values():
            owner = metadata['phase']
            metadata['current_checkpoint'] = current.get(owner) == metadata['revision']
            metadata['display_group'] = 'details'
            if metadata['name'] in products and products[metadata['name']] == (owner, metadata['revision']):
                metadata['display_group'] = 'media' if owner in ('audio', 'images') else 'video' if owner == 'video' else 'details'
        return {'job': job, 'state': state, 'next': next_step, 'brief': safe(self._metadata(folder, folder / 'brief-current.json')),
                'outline': safe(self._metadata(folder, folder / 'draft/outline.json')),
                'dialogue': safe(self._metadata(folder, folder / 'draft/content.json')),
                'checkpoints': checkpoints, 'artifacts': list(artifacts.values()), 'events': self.events(job)}

    def _metadata(self, folder, path):
        resolved = path.resolve()
        return read_json(resolved) if resolved.is_relative_to(folder) else None

    def _gallery(self, job, value, phase, revision, checkpoint, artifacts):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ('path', 'file', 'image', 'source', 'reference') and isinstance(item, str):
                    metadata = self._asset(job, item, phase, revision)
                    if metadata:
                        self._register(artifacts, metadata)
                        if metadata not in checkpoint['assets']:
                            checkpoint['assets'].append(metadata)
                elif isinstance(item, (list, dict)):
                    self._gallery(job, item, phase, revision, checkpoint, artifacts)
        elif isinstance(value, list):
            for item in value:
                self._gallery(job, item, phase, revision, checkpoint, artifacts)

    def _resolve(self, job, name):
        folder = self.job_path(job)
        if Path(name).is_absolute() or '..' in Path(name).parts or SECRET.search(name):
            return None
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or path.suffix.lower() not in MEDIA or not path.is_file():
            return None
        return path

    def _asset(self, job, name, phase, revision):
        path = self._resolve(job, name)
        if path is None:
            return None
        key = hashlib.sha256(name.encode()).hexdigest()[:24]
        prefix = re.match(r'^revisions/([^/]+)/(\d+)/', name)
        source_phase = {'render': 'video', 'content': 'dialogue'}.get(prefix[1], prefix[1]) if prefix else None
        manifest_phase = phase
        if source_phase and source_phase != phase:
            phase, revision = source_phase, int(prefix[2])
        return {'id': key, 'name': name, 'phase': phase, 'revision': revision, 'owner_manifest_phase': manifest_phase,
                'source_phase': source_phase, 'source_revision': int(prefix[2]) if prefix else None,
                'bytes': path.stat().st_size, 'mime': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
                'url': '/media/' + quote(job, safe='') + '/' + key}

    @staticmethod
    def _register(artifacts, metadata):
        """Prefer the actual artifact owner; dependency manifests cannot win."""
        existing = artifacts.get(metadata['id'])
        if existing is None or (metadata.get('source_phase') == metadata['owner_manifest_phase'] and
                                existing.get('source_phase') != existing['owner_manifest_phase']):
            artifacts[metadata['id']] = metadata

    @staticmethod
    def _products(payload, phase):
        names = []
        if not isinstance(payload, dict):
            return names
        if phase == 'audio':
            for track in [payload, *payload.get('tracks', {}).values(), payload.get('en', {})]:
                if isinstance(track, dict):
                    names.extend(track.get(key) for key in ('wav', 'srt'))
        elif phase == 'images':
            names.extend(item.get('path', item.get('file')) for item in payload.get('items', []) if isinstance(item, dict))
            names.extend(payload.get(key) for key in ('contact_sheet', 'gallery'))
        elif phase == 'video':
            names.extend(payload.get(key) for key in ('video', 'video_9x16', 'video_16x9'))
            names.extend(payload.get('stills', []))
        return [name for name in names if isinstance(name, str)]

    def artifact_path(self, job, key):
        item = next((x for x in self.job(job)['artifacts'] if x['id'] == key), None)
        if not item:
            raise ValueError('Artifact không có trong manifest job')
        path = self._resolve(job, item['name'])
        if not path:
            raise ValueError('Artifact không còn khả dụng')
        return path

    def events(self, job):
        db = self.root / '.state/jobs.sqlite'
        if not db.is_file():
            return []
        try:
            with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute('SELECT id,at,module,event,detail FROM events WHERE job=? ORDER BY id DESC LIMIT 100', (job,)).fetchall()
                result = []
                for row in rows:
                    item = dict(row)
                    try:
                        item['detail'] = json.loads(item['detail'])
                    except (ValueError, TypeError):
                        pass
                    result.append(safe(item))
                return result
        except sqlite3.Error:
            return []

    def snapshot(self):
        inventory = discover(self.home, self.root)
        from profile_setup import inventory as flow_inventory
        flow_details = {x['id']: x for x in flow_inventory(self.root, self.home)}
        budget_data = self.budgets.read()
        for item in inventory['accounts']:
            item.update({key: value for key, value in flow_details.get(item['id'], {}).items() if key not in ('auth', 'capability')})
            item['display_label'] = item.get('label', item['id']) + (' · ' + item.get('browser', '') + ' / ' + item.get('profile', '') if item['service'] == 'flow' else ' · Colab')
            item['profile_path'] = str(Path(item['metadata_root']) / item['profile']) if item['service'] == 'flow' else None
            same = budget_data['aliases'].get(item['id'])
            item['same_identity_profiles'] = [alias for alias, identity in budget_data['aliases'].items() if same and identity == same and alias != item['id']]
        for account in inventory['accounts']:
            account['budget'] = self.budgets.snapshot(account['id'])
            if account['service'] == 'flow':
                account['flow_usage'] = self.flow_usage(account['budget'], account=account['id'])
            service_block = account['budget']['blocks'].get(account['service'])
            if service_block:
                account['capability'] = {'state': 'blocked_' + service_block['error'], 'source': 'provider_response_journal'}
                if service_block['error'] in ('auth', 'login_required'):
                    account['auth'] = {'state': 'login_required', 'source': 'provider_response_journal'}
            if account['service'] == 'colab' and account['budget']['allocated_sessions'] and not service_block:
                account['capability'] = {'state': 'allocated_uncertain' if account['budget']['uncertain'] else 'T4_allocated',
                    'device': 'T4', 'source': 'recorded_runtime_allocation_evidence'}
            identity = self.budgets.read()['aliases'].get(account['id'])
            if account['service'] == 'colab' and identity:
                stamp = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                allocation = read_json(self.budgets.path.parent / ('allocation-' + stamp + '.json'))
                if allocation:
                    account['allocation'] = safe(allocation)
                    if allocation.get('phase') in ('submitted', 'ambiguous'):
                        provisional = max(0, time.time() - allocation.get('allocation_started_at', time.time()))
                        account['budget'].update(uncertain=True, provisional_runtime_seconds=provisional)
                        account['runtime_state'] = {'state': 'allocation_' + allocation['phase'], 'device': 'not_confirmed', 'source': 'allocation_request_journal'}
                        if not service_block:
                            account['capability'] = account['runtime_state']
            account['login_handoff'] = login_handoff(account)
        with self.operation_lock:
            operations = safe(list(self.operations.values()))
        issues = self.root / 'logs/issues/INDEX.md'
        return {'jobs': self.jobs(), 'inventory': safe(inventory), 'session': safe(self.sessions.read()), 'setup': self.setup_status(),
                'operations': operations, 'issues': safe(issues.read_text()) if issues.is_file() else '',
                'settings': {'execution': 'CLI chính thức', 'processing': 'Colab', 'images': 'Flow',
                             'auth_probe': 'not_tested', 'provider_quota': 'not_verified'}, 'observed_at': time.time()}

    def flow_usage(self, budget, account=None):
        config = read_json(self.root / 'config.json') or {}
        cap = config.get('flow_session_image_cap', 100)
        if type(cap) is not int or not 100 <= cap <= 200:
            cap = 100
        selected = self.sessions.read().get('session_id')
        if account:
            ledger = self.budgets.read()
            identity = ledger['aliases'].get(account)
            cap = min(cap, ledger['accounts'].get(identity, {}).get('flow_limits', {}).get(selected, cap))
        totals = {key: 0 for key in ('submitted', 'generated', 'collected', 'unknown', 'failed', 'not_submitted')}
        current = 0
        for operation in budget['flow'].values():
            for request in operation['requests'].values():
                if request.get('budget_session', 'legacy-shared-session') != selected and request['state'] not in ('submitted', 'unknown', 'ambiguous'):
                    continue
                slots = request['slots']
                phase = request['state']
                key = 'unknown' if phase in ('unknown', 'ambiguous') else phase
                if key in totals:
                    totals[key] += slots
                if phase != 'not_submitted':
                    current += slots
        return {'cap': cap, 'charged': current, 'remaining': max(0, cap-current),
                'states': totals, 'session_id': selected, 'source': 'internal_project_ledger', 'provider_quota_verified': False}

    def setup_status(self):
        from permissions import Grants
        grants = [entry for entry in Grants(self.root).read()['grants']
                  if entry['role'] in ('setup', 'development') and not entry.get('revoked') and
                  (entry.get('expires_at') is None or entry['expires_at'] > time.time())]
        flow = read_json(self.root / '.state/flow-profile-setup.json') or {}
        public_flow = {key: value for key, value in flow.items() if key != 'history'}
        if isinstance(public_flow.get('active'), dict):
            public_flow['active'] = {key: value for key, value in public_flow['active'].items() if key != 'endpoint'}
        bridge = {'state': 'not_tested'}
        try:
            import b2_bridge
            socket = b2_bridge.get_socket_path() if self.root == b2_bridge.ROOT else b2_bridge.session_socket_path(self.root)
            bridge = {'state': 'present' if socket.exists() else 'missing', 'source': 'socket_file_presence_only', 'live_verified': False}
        except ImportError:
            bridge = {'state': 'unsupported', 'source': 'management_dependencies_missing'}
        return safe({'grants': grants, 'flow': public_flow, 'flow_bridge': bridge})

    def start_operation(self, scope, action, task, *, job=None, account=None):
        key = hashlib.sha256((scope + str(time.time_ns())).encode()).hexdigest()[:20]
        with self.operation_lock:
            if any(value.get('scope', value.get('job')) == scope and value['state'] == 'running' for value in self.operations.values()):
                raise ValueError('Phạm vi này đã có thao tác đang chạy; không gửi trùng')
            self.operations[key] = {'id': key, 'scope': scope, 'job': job, 'account': account,
                                    'action': action, 'state': 'running', 'at': time.time()}
        def execute():
            try:
                result = task()
            except Exception as error:
                result = {'blocked': str(error)}
            with self.operation_lock:
                self.operations[key].update(state='finished', result=safe(result))
        threading.Thread(target=execute, daemon=True).start()
        return {'operation': key, 'state': 'running'}

    def mutate(self, action, data):
        if action.startswith('flow-') or action.startswith('colab-'):
            service, operation = action.split('-', 1)
            if service == 'flow' and operation not in ('plan', 'configure', 'start') or service == 'colab' and operation not in ('start', 'setup', 'reconcile', 'collect', 'stop'):
                raise ValueError('Thao tác setup không hợp lệ')
            account = data.get('account')
            known = {item['id']: item for item in discover(self.home, self.root)['accounts']}
            configured = (read_json(self.root / 'experiments/b2_illustrator/machine.local.json') or {}).get('runtime_account')
            if account not in known and not (service == 'flow' and operation == 'start' and account == configured):
                raise ValueError('Tài khoản không có trong inventory/cấu hình runtime')
            if account in known and known[account]['service'] != service:
                raise ValueError('Service không khớp tài khoản')
            self.setup.authorize(data, self.root / 'experiments/b2_illustrator/machine.local.json' if service == 'flow' else None)
            task = lambda: getattr(self.setup, service)(operation, data)
            if service == 'flow' and operation in ('plan', 'configure'):
                return task()
            identity = self.budgets.read()['aliases'].get(account, account)
            return self.start_operation(service + ':' + identity, action, task, job=data.get('job'), account=account)
        if action == 'bind-runtime':
            job = data.get('job')
            if job:
                self.job_path(job)
                state = self.cli(['status', job])
                from permissions import Grants
                Grants(self.root).require(state.get('grant_id'), 'production', 'execute', job=job)
            binding = self.sessions.bind_runtime(data.get('service'), data.get('account'), data.get('runtime_session'),
                grant=data.get('grant'), source=data.get('source'), evidence=data.get('evidence'), job=job, target=data.get('target'))
            if job:
                result = self.cli(['bind-session', job, '--session', self.sessions.read()['session_id'], '--source', data['source']])
                return {'binding': binding, 'job': result}
            return {'binding': binding}

        if action == 'probe-flow':
            account = data.get('account')
            if account not in {item['id'] for item in discover(self.home, self.root)['accounts'] if item['service'] == 'flow'}:
                raise ValueError('Chọn đúng hồ sơ Flow đã phát hiện')
            self.setup.authorize(data, self.root / 'experiments/b2_illustrator/machine.local.json')
            import account_catalog
            probe = getattr(account_catalog, 'probe_flow', None)
            if probe is None:
                raise ValueError('Kiểm Flow chỉ đọc chưa khả dụng trong runtime này')
            identity = self.budgets.read()['aliases'].get(account, account)
            return self.start_operation('flow:' + identity, action,
                lambda: probe(account, system_root=self.root, home=self.home, budget_store=self.budgets.path.parent), account=account)
        if action in ('confirm-identity', 'probe-colab'):
            account = data.get('account')
            if account not in {x['id'] for x in discover(self.home, self.root)['accounts']}:
                raise ValueError('Tài khoản không có trong inventory')
            if action == 'confirm-identity':
                return confirm_identity(account, data.get('email'), data.get('source', ''), home=self.home, budget_store=self.budgets.path.parent)
            return probe_colab(account, home=self.home, budget_store=self.budgets.path.parent)
        if action == 'session':
            return self.sessions.select(data.get('pool'), data.get('defaults'), selection=data.get('selection', 'specified'), known=discover(self.home, self.root)['accounts'])
        job = data.get('job')
        self.job_path(job)
        if action in ('stop', 'takeover', 'mode'):
            source = data.get('source')
            if not isinstance(source, str) or not source.strip():
                raise ValueError('Cần chỉ dẫn nguyên văn của người dùng')
            argv = [action, job, '--source', source]
            if action == 'mode':
                if data.get('mode') not in ('auto', 'review'):
                    raise ValueError('Mode không hợp lệ')
                argv += ['--mode', data['mode']]
        elif action in ('approve', 'reject'):
            phase, revision, note = data.get('phase'), data.get('revision'), data.get('note')
            if phase not in ('outline', 'dialogue', 'audio', 'images', 'video') or type(revision) is not int or revision < 1 or not isinstance(note, str) or not note.strip():
                raise ValueError('Cần đầu ra, revision chính xác và phản hồi nguyên văn')
            argv = [action, job, phase, '--revision', str(revision), '--note', note]
            if action == 'reject':
                for key in ('scene', 'character', 'image', 'ratio'):
                    if data.get(key):
                        if not isinstance(data[key], str) or len(data[key]) > 200:
                            raise ValueError('Phạm vi sửa không hợp lệ')
                        argv += ['--' + key, data[key]]
        elif action in ('run', 'resume'):
            argv = [action, job]
        else:
            raise ValueError('Thao tác không được hỗ trợ')
        if action not in ('run', 'resume'):
            return self.cli(argv)
        # Long-running CLI keeps the official job lease while HTTP stays responsive.
        return self.start_operation(job, action, lambda: self.cli(argv), job=job)
