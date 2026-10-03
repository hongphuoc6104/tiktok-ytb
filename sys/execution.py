"""Version-four execution: technical completion, durable rights and output review.

The connected agent authors plans/content; this engine never falls back to a
legacy generator or machine reviewer. Missing author input is an agent action,
not a request for human quality approval in auto mode.
"""
from contextlib import contextmanager
import fcntl
import json
import os
import shutil
from pathlib import Path
import time
import uuid

import jsonschema
from permissions import Grants

VERSION = 4
CONTRACT = {'engine': VERSION, 'content_schema': '3.0', 'delivery': 1, 'permissions': 1}
CHECKPOINTS = ('outline', 'dialogue', 'audio', 'images', 'video')
MODULES = {'dialogue': 'content', 'audio': 'audio', 'images': 'images', 'video': 'render'}


def is_job(p, job):
    path = p.job(job) / 'workflow.json'
    return path.is_file() and json.loads(path.read_text()).get('version') == VERSION


def settings(p, job):
    from pilot import read, hashobj, Blocked
    data = read(p.job(job) / 'workflow.json')
    if data.get('version') != VERSION or data.get('mode') not in ('auto', 'review'):
        raise Blocked('EXECUTION_SETTINGS: unsupported execution contract')
    with p._db_lock:
        event = p.db.execute("SELECT detail FROM events WHERE job=? AND event IN ('workflow_created','execution_mode_changed','execution_session_changed') ORDER BY id DESC LIMIT 1", (job,)).fetchone()
    if not event or event['detail'] != hashobj(data):
        raise Blocked('EXECUTION_SETTINGS: changed outside the official operation')
    return data


def verify_compatibility(p, job):
    from pilot import read, Blocked
    metadata = read(p.job(job) / 'integrity-meta.json')
    if metadata.get('engine_contract') != CONTRACT:
        raise Blocked('ENGINE_MIGRATION_REQUIRED: incompatible execution/schema contract')
    previous = metadata.get('schema_contracts')
    actual = schema_snapshot(p)
    from pilot import hashobj
    cache = (hashobj(previous), hashobj(actual))
    if getattr(p, '_verified_schema_contract', None) != cache:
        for name, schema in actual.items():
            try:
                jsonschema.validators.validator_for(schema).check_schema(schema)
            except jsonschema.SchemaError as ex:
                raise Blocked('ENGINE_MIGRATION_REQUIRED: invalid schema ' + name) from ex
    if previous is None:
        from pilot import digest
        baseline = read(p.job(job) / 'integrity.json')
        incompatible = [name for name in actual if baseline.get('schemas/' + name) != digest(p.root / 'schemas' / name)]
    else:
        incompatible = [name for name, schema in actual.items() if name not in previous or not _schema_compatible(previous[name], schema)]
    if incompatible:
        raise Blocked('ENGINE_MIGRATION_REQUIRED: incompatible schemas: ' + ', '.join(incompatible))
    p._verified_schema_contract = cache
    if (p.job(job) / 'workflow.json').exists():
        settings(p, job)
    elif getattr(p, '_creating_v4_job', None) != job:
        raise Blocked('EXECUTION_SETTINGS: finish creation through the official v4 entry point')


def require(p, job, operation):
    cfg = settings(p, job)
    return Grants(p.root).require(cfg['grant_id'], 'production', operation, job=job)


def new(p, job, brief, mode, grant_id, session_id=None):
    from pilot import write, hashobj
    if mode not in ('auto', 'review'):
        raise ValueError('Expected auto or review')
    Grants(p.root).require(grant_id, 'production', 'execute', job=job)
    from scripts.story_plan import normalize_brief
    from output_contract import outputs
    if brief is None:
        raise ValueError('New jobs require an explicit brief')
    brief = normalize_brief(brief)
    from output_contract import voice_settings
    cfg = __import__('pilot').read(p.root / 'config.json')
    plans = outputs(brief)
    for plan in plans:
        choice = voice_settings(brief, plan['language'], cfg)
        plan.setdefault('voice', choice['voice'])
        plan.setdefault('speed', choice['speed'])
    brief = {**brief, 'outputs': plans}
    from session_store import Sessions
    manager = Sessions(p.root)
    session = manager.snapshot(job=job) if hasattr(manager, 'snapshot') else {k: v for k, v in manager.read().items() if k != 'pins'}
    if session_id is not None and session.get('session_id') != session_id:
        raise ValueError('Selected management session does not match --session')
    prompt_pin = None
    if cfg.get('flow_prompt_version') is not None:
        from flow_prompts import freeze
        prompt_pin = freeze(cfg['flow_model'], cfg['flow_prompt_version'])
    p.new(job, brief, mode, engine_version=VERSION, grant_id=grant_id)
    cfg = {'version': VERSION, 'mode': mode, 'grant_id': grant_id, 'created_at': time.time(),
           'session_id': session.get('session_id'), 'management_session': session}
    if prompt_pin is not None:
        cfg['flow_prompt_pin'] = prompt_pin
    write(p.job(job) / 'workflow.json', cfg)
    p.event(job, 'control', 'workflow_created', hashobj(cfg))
    with lease(p, job):
        p.approve(job, 'control', p.rows(job)['control']['revision'], 'Technical configuration accepted', actor='technical')
        if prompt_pin is not None:
            from flow_management import freeze_prompt_pin
            freeze_prompt_pin(p, job)
        _update_control(p, job, stop_requested=False)
    authority = Grants(p.root).require(grant_id, 'production', 'execute', job=job)
    plan = {'job': job, 'objective': brief.get('goal', brief.get('topic')), 'outputs': brief['outputs'],
            'scope': {'role': 'production', 'job': job, 'grant_id': grant_id, 'source': authority['source']},
            'steps': [{'output': name, 'depends_on': list(CHECKPOINTS[:i]),
                       'review_required': mode == 'review'} for i, name in enumerate(CHECKPOINTS)],
            'requested_accounts': {'flow_profile': __import__('pilot').read(p.root / 'config.json').get('flow_profile'),
                                   'colab_account': __import__('pilot').read(p.root / 'config.json').get('colab_tts', {}).get('account', 'auto')},
            'locations': {'audio': 'colab', 'images': 'flow', 'timeline': 'colab', 'subtitles': 'colab', 'video': 'colab'},
            'created_at': time.time(), 'contract': CONTRACT, 'session_id': cfg['session_id'],
            'management_session': session}
    write(p.job(job) / 'plans/1/plan.json', plan)
    p.event(job, 'control', 'execution_plan', json.dumps(plan, ensure_ascii=False))
    return observe(p, job)


def _update_control(p, job, **changes):
    from pilot import read, write
    path = p.job(job) / 'execution-control.json'
    with path.with_suffix('.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        value = read(path) if path.is_file() else {}
        value.update(changes, updated_at=time.time())
        write(path, value)
    return value


def control(p, job):
    from pilot import read
    path = p.job(job) / 'execution-control.json'
    return read(path) if path.is_file() else {'stop_requested': False, 'owner': None, 'pid': None}


@contextmanager
def lease(p, job):
    from pilot import Blocked
    path = p.job(job) / 'execution-lease.lock'
    with path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as ex:
            raise Blocked('JOB_RUNNING: another controller owns this job') from ex
        owner = uuid.uuid4().hex
        _update_control(p, job, owner=owner, pid=os.getpid(), heartbeat=time.time())
        p._execution_job = job
        p._execution_owner = owner
        try:
            yield owner
        finally:
            p._execution_job = None
            p._execution_owner = None
            p._execution_phase = None
            _update_control(p, job, owner=None, pid=None, heartbeat=time.time())


def before_submit(p, job, service=None):
    from pilot import Blocked
    require(p, job, 'execute')
    verify_compatibility(p, job)
    state = control(p, job)
    if getattr(p, '_execution_job', None) != job or state.get('owner') != getattr(p, '_execution_owner', None):
        raise Blocked('JOB_LEASE_REQUIRED: submit needs this job controller lease')
    if state.get('stop_requested'):
        raise Blocked('STOP_REQUESTED: no new request may be submitted')
    phase = getattr(p, '_execution_phase', None)
    service = service or ('flow' if phase == 'images' else 'colab' if phase in ('audio', 'video') else None)
    if service in ('colab', 'flow'):
        runtime_ready(p, job, service)
    _update_control(p, job, heartbeat=time.time())


def stop(p, job, source):
    require(p, job, 'stop')
    if not source.strip():
        raise ValueError('Stop needs its actual instruction')
    _update_control(p, job, stop_requested=True)
    p.event(job, 'control', 'stop_requested', source)
    return observe(p, job)


def takeover(p, job, source):
    from pilot import Blocked
    require(p, job, 'takeover')
    if not source.strip():
        raise ValueError('Takeover needs its actual instruction')
    state = control(p, job)
    pid = state.get('pid')
    if pid:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        except PermissionError as ex:
            raise Blocked('JOB_RUNNING: previous runner may still be alive') from ex
        else:
            raise Blocked('JOB_RUNNING: cannot take ownership from a live runner')
    with lease(p, job):
        p.event(job, 'control', 'ownership_taken_over', json.dumps({'previous': state, 'source': source}))
    return observe(p, job)


def resume(p, job):
    require(p, job, 'resume')
    return advance(p, job, clear_stop=True)


def change_mode(p, job, mode, source):
    from pilot import write, hashobj
    require(p, job, 'mode')
    if mode not in ('auto', 'review') or not source.strip():
        raise ValueError('Mode change needs a supported mode and actual instruction')
    with lease(p, job):
        old = settings(p, job)
        cfg = {**old, 'mode': mode, 'mode_changed_at': time.time()}
        write(p.job(job) / 'workflow.json', cfg)
        p.event(job, 'control', 'execution_mode_changed', hashobj(cfg))
        p.event(job, 'control', 'mode_change_detail', json.dumps({'old': old['mode'], 'new': mode, 'source': source}))
    return observe(p, job)


def _snapshot(p, job, phase):
    from pilot import digest, read
    files = {}
    def include(path):
        if path.is_file():
            files[str(path.relative_to(p.job(job)))] = digest(path)
    include(p.job(job) / 'brief-current.json')
    cfg = settings(p, job)
    if cfg.get('outputs'):
        from pilot import hashobj
        files['execution_output_contract'] = hashobj(cfg['outputs'])
    include(p.job(job) / 'draft/outline.json')
    if phase != 'outline':
        include(p.job(job) / 'draft/content.json')
        row = p.rows(job)[MODULES[phase]]
        if row['envelope']:
            envelope = p.path(job, row['envelope'])
            include(envelope)
            for name in read(envelope)['files']:
                include(p.path(job, name))
    return files


def latest(p, job, phase):
    from pilot import read
    folder = p.job(job) / 'checkpoints' / phase
    files = list(folder.glob('*/manifest.json'))
    return read(max(files, key=lambda path: int(path.parent.name))) if files else None


def current(p, job, phase):
    manifest = latest(p, job, phase)
    try:
        if manifest is None or manifest['snapshot'] != _snapshot(p, job, phase):
            return None
    except (OSError, ValueError, KeyError):
        return None
    from pilot import hashobj
    with p._db_lock:
        events = p.db.execute("SELECT detail FROM events WHERE job=? AND module=? AND event='artifact_ready'", (job, phase)).fetchall()
    if not any(json.loads(event['detail']).get('manifest_hash') == hashobj(manifest) for event in events):
        return None
    if phase != 'outline' and p.rows(job)[MODULES[phase]]['state'] not in ('approved', 'awaiting_review'):
        return None
    if phase != 'outline':
        from pilot import read
        module = MODULES[phase]
        row = p.rows(job)[module]
        if not row['envelope']:
            return None
        envelope = read(p.path(job, row['envelope']))
        if envelope['input_versions'] != p.input_versions(job, module) or p.snapshot_hash(job, envelope) != row['hash']:
            return None
    return manifest


def accepted(p, job, phase):
    from pilot import read, hashobj
    manifest = current(p, job, phase)
    if not manifest:
        return False
    if settings(p, job)['mode'] == 'auto':
        return manifest.get('technical_complete') is True
    decision_path = p.path(job, manifest['decision'])
    if not decision_path.is_file():
        return False
    try:
        decision = read(decision_path)
    except (OSError, ValueError):
        return False
    if decision.get('manifest_hash') != hashobj(manifest) or decision.get('actor') != 'user' or decision.get('approved') is not True:
        return False
    with p._db_lock:
        event = p.db.execute("SELECT 1 FROM events WHERE job=? AND module=? AND event='checkpoint_approved' AND detail=?", (job, phase, hashobj(decision))).fetchone()
    return event is not None


def _approve(p, job, phase, revision, note):
    from pilot import write, hashobj, Blocked
    require(p, job, 'execute')
    verify_compatibility(p, job)
    if phase not in CHECKPOINTS or settings(p, job)['mode'] != 'review':
        raise Blocked('Only review output checkpoints accept user decisions')
    manifest = current(p, job, phase)
    if not manifest or manifest['revision'] != revision or not note.strip():
        raise Blocked('Exact current output revision and actual feedback are required')
    if p.path(job, manifest['decision']).exists():
        raise Blocked('A saved decision is never overwritten')
    decision = {'actor': 'user', 'approved': True, 'note': note, 'manifest_hash': hashobj(manifest), 'at': time.time()}
    write(p.path(job, manifest['decision']), decision)
    p.event(job, phase, 'checkpoint_approved', hashobj(decision))
    p.event(job, phase, 'decision_detail', json.dumps(decision, ensure_ascii=False))
    if phase == 'video':
        from workflow import publish_videos
        return {**observe(p, job), 'videos': publish_videos(p, job)}
    return observe(p, job)


def _checkpoint(p, job, phase, assets, payload=None):
    from pilot import write, hashobj
    previous = latest(p, job, phase)
    revision = previous['revision'] + 1 if previous else 1
    folder = p.job(job) / 'checkpoints' / phase / str(revision)
    folder.mkdir(parents=True, exist_ok=False)
    data = {'phase': phase, 'revision': revision, 'technical_complete': True,
            'snapshot': _snapshot(p, job, phase), 'assets': assets,
            'decision': str((folder / 'decision.json').relative_to(p.job(job))),
            'payload': payload, 'created_at': time.time()}
    if phase == 'outline':
        write(folder / 'outline.json', payload)
        data['assets'] = [str((folder / 'outline.json').relative_to(p.job(job)))]
    lines = [f'# {job} — {phase} revision {revision}', '', 'Đầu ra đã kiểm tra kỹ thuật. Chất lượng cần đối chiếu artifact thật.', '']
    for name in data['assets']:
        path = p.path(job, name)
        lines.append(f'- [{path.name}]({path})')
    (folder / 'review.md').write_text('\n'.join(lines) + '\n')
    data['review'] = str((folder / 'review.md').relative_to(p.job(job)))
    write(folder / 'manifest.json', data)
    p.event(job, phase, 'artifact_ready', json.dumps({'revision': revision, 'assets': data['assets'], 'manifest_hash': hashobj(data)}, ensure_ascii=False))
    return data


def gate(p, job, module):
    from pilot import Blocked
    if module == 'content' and not accepted(p, job, 'outline'):
        raise Blocked('Outline checkpoint is not ready for dialogue production')
    if module in ('audio', 'images', 'render') and not accepted(p, job, 'dialogue'):
        raise Blocked('Dialogue checkpoint is not ready for the current mode')
    if module == 'images' and settings(p, job)['mode'] == 'review' and not accepted(p, job, 'audio'):
        raise Blocked('Review requires the audio decision before image generation')
    if module == 'render' and not all(accepted(p, job, phase) for phase in ('audio', 'images')):
        raise Blocked('Audio/image checkpoints are not ready for rendering')


def observe(p, job):
    from pilot import Blocked
    cfg = settings(p, job)
    blocked = None
    try:
        verify_compatibility(p, job)
    except Blocked as ex:
        blocked = str(ex)
    stages = []
    for phase in CHECKPOINTS:
        item = current(p, job, phase)
        state = 'complete' if accepted(p, job, phase) else 'awaiting_review' if item else 'pending'
        stages.append({'phase': phase, 'state': state, 'revision': item['revision'] if item else None,
                       'assets': item['assets'] if item else [],
                       'review': str(p.path(job, item['review'])) if item and item.get('review') else None})
    owner = control(p, job)
    from scripts.image_repairs import attention
    needs_attention = attention(p, job)
    with p._db_lock:
        recovery = p.db.execute("SELECT event,detail FROM events WHERE job=? AND event IN ('execution_needs_attention','micro_plan') ORDER BY id DESC LIMIT 1", (job,)).fetchone()
    if recovery and recovery['event'] == 'execution_needs_attention':
        needs_attention = json.loads(recovery['detail'])
    return {'job': job, 'version': VERSION, 'mode': cfg['mode'], 'grant_id': cfg['grant_id'],
            'complete': not blocked and all(s['state'] == 'complete' for s in stages),
            'control': owner, 'checkpoints': stages, 'observed_at': time.time(),
            'needs_attention': needs_attention, **({'blocked': blocked} if blocked else {})}


def advance(p, job, target=None, clear_stop=False):
    from pilot import read, write, Blocked
    require(p, job, 'execute')
    with lease(p, job):
        if clear_stop:
            _update_control(p, job, stop_requested=False)
            p.event(job, 'control', 'execution_resumed')
        state = observe(p, job)
        if state.get('needs_attention'):
            raise Blocked('NEEDS_ATTENTION: inspect issue and submit an evidence-backed recovery plan')
        for phase in CHECKPOINTS:
            p._execution_phase = phase
            if accepted(p, job, phase):
                continue
            if control(p, job).get('stop_requested'):
                return {**observe(p, job), 'action': 'stopped'}
            if target and phase != target:
                raise Blocked(f'Current permitted output: {phase}')
            existing = current(p, job, phase)
            if existing:
                return {**observe(p, job), 'action': 'review', 'phase': phase}
            if phase == 'outline':
                path = p.job(job) / 'draft/outline.json'
                if not path.is_file():
                    _request_author(p, job, phase, path)
                    return {**observe(p, job), 'action': 'author_outline', 'path': str(path)}
                outline = read(path)
                jsonschema.validate(outline, read(p.root / 'schemas/outline-v3.json'))
                ids = [x['scene_id'] for x in outline['outline']]
                if ids != [f'SC{i:02}' for i in range(1, len(ids) + 1)]:
                    raise Blocked('OUTLINE: scene IDs must follow the chosen order')
                brief, revision, _ = p.brief(job)
                if {r for item in outline['outline'] for r in item['requirements']} != {r['id'] for r in brief['required_points']}:
                    raise Blocked('OUTLINE: required meanings are missing or unknown')
                if brief.get('scene_count') is None:
                    p.revise_brief(job, {**brief, 'scene_count': len(ids)}, 'Scene count chosen from this job outline')
                elif brief['scene_count'] != len(ids):
                    initial = read(p.job(job) / 'briefs/1.json')
                    if initial.get('scene_count') is None:
                        p.revise_brief(job, {**brief, 'scene_count': len(ids)}, 'Scene count changed by this authorized outline revision')
                    else:
                        raise Blocked('OUTLINE: scene count differs from the saved job contract')
                _checkpoint(p, job, phase, [str(path.relative_to(p.job(job)))], outline)
            else:
                if phase == 'dialogue':
                    path = p.job(job) / 'draft/content.json'
                    if not path.is_file():
                        _request_author(p, job, phase, path)
                        return {**observe(p, job), 'action': 'author_dialogue', 'path': str(path)}
                    draft = read(path)
                    if draft.get('outline') != read(p.job(job) / 'draft/outline.json')['outline']:
                        raise Blocked('OUTLINE: dialogue changed the chosen outline')
                    _, revision, stamp = p.brief(job)
                    draft.update(brief_revision=revision, brief_hash=stamp)
                    write(path, draft)
                module = MODULES[phase]
                internal_steps = set()
                while p.rows(job)[module]['state'] != 'approved':
                    # A crash after collection must accept the saved technical output,
                    # never generate a new revision/request merely to reach its checkpoint.
                    if p.rows(job)[module]['state'] != 'awaiting_review':
                        before_submit(p, job)
                        p.run(job, module)
                    payload = p.payload(job, module)
                    checkpoint = payload.get('checkpoint') if module == 'images' else None
                    if checkpoint and checkpoint in internal_steps:
                        p.issue(job, module, 'NO_PROGRESS: internal image checkpoint did not advance', evidence=checkpoint)
                        raise Blocked('NO_PROGRESS: inspect internal checkpoint before another provider action')
                    if checkpoint:
                        internal_steps.add(checkpoint)
                    p.approve(job, module, p.rows(job)[module]['revision'],
                              'Technical output accepted, no quality approval', checkpoint, actor='technical')
                envelope = read(p.path(job, p.rows(job)[module]['envelope']))
                _checkpoint(p, job, phase, envelope['files'], envelope['payload'])
            if target and settings(p, job)['mode'] == 'auto':
                return {**observe(p, job), 'action': 'continue', 'phase': phase}
            if settings(p, job)['mode'] == 'review':
                return {**observe(p, job), 'action': 'review', 'phase': phase}
        from workflow import publish_videos
        return {**observe(p, job), 'action': 'complete', 'videos': publish_videos(p, job)}


def approve(p, job, phase, revision, note):
    with lease(p, job):
        return _approve(p, job, phase, revision, note)


def next_step(p, job):
    state = observe(p, job)
    if state.get('blocked'):
        return {**state, 'action': 'migration_required'}
    if state.get('needs_attention'):
        return {**state, 'action': 'needs_attention'}
    if state['control'].get('stop_requested'):
        return {**state, 'action': 'stopped'}
    for item in state['checkpoints']:
        if item['state'] != 'complete':
            return {**item, 'job': job, 'mode': state['mode'],
                    'action': 'review' if item['state'] == 'awaiting_review' else
                              ('author_' + item['phase'] if item['phase'] in ('outline', 'dialogue') else 'run_or_repair')}
    return {**state, 'action': 'complete'}


def _micro_plan(p, job, plan):
    """Append an evidence-bound recovery strategy, never reset by a chat change."""
    from pilot import Blocked, hashobj, write
    require(p, job, 'repair')
    required = {'symptom', 'evidence', 'error_class', 'target', 'input_hash', 'strategy',
                'success_criteria', 'rollback', 'submit_state'}
    if not isinstance(plan, dict) or not required <= plan.keys() or any(
            not isinstance(plan[k], str) or not plan[k].strip() for k in required):
        raise Blocked('MICRO_PLAN: provide symptom/evidence/cause class/target/input/strategy/success/rollback/submit state')
    if plan['submit_state'] in ('unknown', 'ambiguous') and plan['strategy'] not in ('collect', 'reconcile'):
        raise Blocked('AMBIGUOUS_REQUEST: collect/reconcile the original request before generation')
    key = hashobj({k: plan[k] for k in ('error_class', 'target', 'input_hash', 'strategy', 'submit_state')})
    with p._db_lock:
        prior = p.db.execute("SELECT detail FROM events WHERE job=? AND event='micro_plan' ORDER BY id", (job,)).fetchall()
    for row in prior:
        item = json.loads(row['detail'])
        if item['fingerprint'] == key and item['evidence'] == plan['evidence']:
            issue = p.issue(job, 'control', 'NO_PROGRESS: identical input, strategy and evidence', evidence=key)
            p.event(job, 'control', 'execution_needs_attention', json.dumps({'reason': 'no progress', 'fingerprint': key, 'target': plan['target'], 'issue': issue}))
            raise Blocked('NO_PROGRESS: identical input, strategy and evidence; diagnose before retrying')
    record = {**plan, 'fingerprint': key, 'grant_id': settings(p, job)['grant_id'], 'at': time.time()}
    folder = p.job(job) / 'micro-plans' / uuid.uuid4().hex
    write(folder / 'plan.json', record)
    p.event(job, 'control', 'micro_plan', json.dumps(record, ensure_ascii=False))
    return record


def reject(p, job, phase, revision, note, *, scene=None, character=None, image=None, ratio=None, repair_plan=None):
    from pilot import Blocked, hashobj, write
    require(p, job, 'repair')
    if phase not in CHECKPOINTS or not note.strip():
        raise Blocked('Select an exact output and supply the actual change instruction')
    with lease(p, job):
        manifest = current(p, job, phase)
        if not manifest or manifest['revision'] != revision:
            raise Blocked('Exact current output revision is required')
        if phase != 'images' and (character or image or ratio):
            raise Blocked('Image selection belongs to the images output')
        if phase != 'audio' and phase != 'images' and scene:
            raise Blocked('Targeted scene repair belongs to audio/images')
        if phase != 'images':
            plan = repair_plan or {'symptom': note, 'evidence': hashobj(manifest['snapshot']),
                'error_class': 'output_revision', 'target': phase + (':' + scene if scene else ''),
                'input_hash': hashobj(manifest['snapshot']), 'strategy': note,
                'success_criteria': note, 'rollback': f"preserved checkpoint {phase}/{revision}",
                'submit_state': 'not_submitted'}
            micro_plan(p, job, plan)
        if phase == 'outline':
            # Preserve the original output, then invalidate dialogue and its dependencies.
            if p.rows(job)['content']['state'] != 'pending':
                p.reject(job, 'content', note)
            (p.job(job) / 'draft/outline.json').unlink()
        elif phase == 'audio':
            from workflow import retake_audio
            retake_audio(p, job, note, scene)
        elif phase == 'images':
            p.reject(job, 'images', note, p.rows(job)['images']['revision'], 'final', scene, character, image, ratio, repair_plan)
        else:
            p.reject(job, MODULES[phase], note)
        event = {'phase': phase, 'revision': revision, 'note': note, 'snapshot_hash': hashobj(manifest)}
        # A later approval must target a new checkpoint. Existing decisions remain immutable.
        p.event(job, phase, 'checkpoint_rejected', json.dumps(event, ensure_ascii=False))
        return observe(p, job)


def _migration_authority(p, job, grant_id):
    from permissions import PermissionDenied
    store = Grants(p.root)
    try:
        return store.require(grant_id, 'development', 'migrate', job=job)
    except PermissionDenied:
        prefix = 'sys/' if store.project_root != store.system_root else ''
        return store.require(grant_id, 'development', 'migrate', path=prefix + 'runs/' + job + '/workflow.json')


def migrate(p, job, development_grant, production_grant, source, mode=None):
    """Official v3-to-v4 transition: original snapshots/journals stay untouched."""
    from pilot import read, write, hashobj, Blocked
    _migration_authority(p, job, development_grant)
    Grants(p.root).require(production_grant, 'production', 'execute', job=job)
    if not source.strip():
        raise Blocked('Migration needs the actual authorized instruction')
    path = p.job(job)
    old = read(path / 'workflow.json')
    if old.get('version') != 3:
        raise Blocked('Migration accepts a legacy v3 workflow only')
    mode = mode or old['mode']
    if mode not in ('review', 'auto'):
        raise Blocked('Unsupported mode')
    from pilot import locked
    with locked(p.root), lease(p, job):
        rows = p.rows(job)
        if any(row['state'] == 'running' for row in rows.values()):
            raise Blocked('MIGRATION_INTERRUPTED: reconcile running legacy module/request before migration')
        if rows['control']['state'] != 'approved':
            raise Blocked('Migration requires the existing technical control checkpoint')
        history = path / 'migration-history' / uuid.uuid4().hex
        history.mkdir(parents=True)
        for name in ('workflow.json', 'integrity-meta.json', 'integrity.json'):
            if (path / name).exists():
                shutil.copy2(path / name, history / name)
        record = {'job': job, 'from': 3, 'to': VERSION, 'source': source,
                  'development_grant': development_grant, 'production_grant': production_grant,
                  'at': time.time(), 'modules': rows, 'preserved_request_ownership': True,
                  'original_files': {name: hashobj(read(history / name)) for name in ('workflow.json', 'integrity-meta.json', 'integrity.json') if (history / name).exists()}}
        write(history / 'provenance.json', record)
        from output_contract import outputs, voice_settings
        original_brief = p.brief(job)[0]
        original_control = p.payload(job, 'control')
        plans = outputs(original_brief)
        for delivery in plans:
            chosen = voice_settings(original_brief, delivery['language'], original_control)
            delivery.setdefault('voice', chosen['voice'])
            delivery.setdefault('speed', chosen['speed'])
        cfg = {'version': VERSION, 'mode': mode, 'grant_id': production_grant,
               'created_at': old['created_at'], 'migrated_at': time.time(),
               'migration': str(history.relative_to(path)), 'outputs': plans,
               'effective_contract_source': 'legacy_saved_brief_and_control',
               'session_id': None, 'management_session': {}}
        write(path / 'integrity-meta.json', {**read(path / 'integrity-meta.json'), 'engine_version': VERSION, 'engine_contract': CONTRACT, 'schema_contracts': schema_snapshot(p)})
        write(path / 'workflow.json', cfg)
        p.event(job, 'control', 'workflow_created', hashobj(cfg))
        p.event(job, 'control', 'execution_migrated', json.dumps(record, ensure_ascii=False))
        if not (path / 'draft/outline.json').exists() and rows['content']['envelope']:
            content = p.payload(job, 'content')
            if content.get('outline'):
                write(path / 'draft/outline.json', {'outline': content['outline']})
        _update_control(p, job, stop_requested=False)
    return observe(p, job)


def rollback_migration(p, job, grant_id, source):
    from pilot import read, write, hashobj, Blocked
    _migration_authority(p, job, grant_id)
    if not source.strip():
        raise Blocked('Rollback needs the actual authorized instruction')
    with lease(p, job):
        cfg = settings(p, job)
        if not cfg.get('migration'):
            raise Blocked('No legacy migration is available')
        history = p.path(job, cfg['migration'])
        provenance = read(history / 'provenance.json')
        if p.rows(job) != provenance['modules']:
            raise Blocked('ROLLBACK_IMPACT: execution changed since migration; preserve outputs and prepare explicit reverse migration')
        for name, stamp in provenance['original_files'].items():
            if hashobj(read(history / name)) != stamp:
                raise Blocked('MIGRATION_HISTORY_TAMPER: cannot restore altered provenance')
        write(history / ('rollback-' + uuid.uuid4().hex + '.json'), {'source': source, 'grant_id': grant_id, 'at': time.time(), 'v4_settings': cfg})
        for name in provenance['original_files']:
            shutil.copy2(history / name, p.job(job) / name)
        p.event(job, 'control', 'execution_migration_rolled_back', json.dumps({'migration': cfg['migration'], 'source': source}))
    return {'job': job, 'version': 3, 'rolled_back': True, 'history': str(history)}


def _request_author(p, job, phase, path):
    from pilot import hashobj
    plan = {'phase': phase, 'path': str(path.relative_to(p.job(job))),
            'brief_hash': p.brief(job)[2], 'assignee': 'connected_author',
            'mode': settings(p, job)['mode'], 'quality_review_requested': False}
    key = hashobj(plan)
    with p._db_lock:
        known = p.db.execute("SELECT 1 FROM events WHERE job=? AND event='author_action_requested' AND detail=?", (job, key)).fetchone()
    if not known:
        p.event(job, phase, 'author_action_requested', key)
        p.event(job, phase, 'author_action_detail', json.dumps(plan, ensure_ascii=False))


def author(p, job, phase, payload, source):
    """The connected author submits inputs via a versioned, scoped operation."""
    from pilot import Blocked, write, hashobj
    require(p, job, 'content')
    if phase not in ('outline', 'dialogue') or not source.strip():
        raise Blocked('Author requires outline/dialogue and actual authorship source')
    with lease(p, job):
        if current(p, job, phase):
            raise Blocked('Reject the current output before replacing its authored input')
        if phase == 'dialogue' and not accepted(p, job, 'outline'):
            raise Blocked('Outline must be ready before dialogue authorship')
        if phase == 'outline':
            jsonschema.validate(payload, __import__('pilot').read(p.root / 'schemas/outline-v3.json'))
        folder = p.job(job) / 'author-submissions' / uuid.uuid4().hex
        write(folder / 'input.json', payload)
        record = {'phase': phase, 'source': source, 'input_hash': hashobj(payload),
                  'input': str((folder / 'input.json').relative_to(p.job(job))), 'at': time.time()}
        write(folder / 'provenance.json', record)
        write(p.job(job) / ('draft/outline.json' if phase == 'outline' else 'draft/content.json'), payload)
        p.event(job, phase, 'author_input_received', json.dumps(record, ensure_ascii=False))
    return observe(p, job)


def bind_session(p, job, session_id, source):
    from pilot import Blocked, write, hashobj
    from session_store import Sessions
    require(p, job, 'execute')
    if not source.strip():
        raise Blocked('Session binding requires the actual selection instruction')
    manager = Sessions(p.root)
    session = manager.snapshot(job=job) if hasattr(manager, 'snapshot') else {k: v for k, v in manager.read().items() if k != 'pins'}
    if not session_id or session.get('session_id') != session_id or not session.get('pool'):
        raise Blocked('Known selected management session required')
    with lease(p, job):
        previous = settings(p, job)
        cfg = {**previous, 'session_id': session_id, 'management_session': session, 'session_bound_at': time.time()}
        write(p.job(job) / 'workflow.json', cfg)
        p.event(job, 'control', 'execution_session_changed', hashobj(cfg))
        p.event(job, 'control', 'session_change_detail', json.dumps({'old': previous.get('session_id'), 'new': session_id, 'source': source, 'existing_request_ownership_preserved': True}))
    return observe(p, job)


def micro_result(p, job, fingerprint, result):
    from pilot import Blocked, write
    require(p, job, 'repair')
    if not isinstance(result, dict) or type(result.get('success')) is not bool or not isinstance(result.get('evidence'), str) or not result['evidence'].strip():
        raise Blocked('MICRO_RESULT: success and actual outcome evidence are required')
    with lease(p, job):
        with p._db_lock:
            records = p.db.execute("SELECT detail FROM events WHERE job=? AND event='micro_plan' ORDER BY id DESC", (job,)).fetchall()
        plan = next((json.loads(r['detail']) for r in records if json.loads(r['detail'])['fingerprint'] == fingerprint), None)
        if not plan:
            raise Blocked('Unknown recovery strategy fingerprint')
        record = {'fingerprint': fingerprint, 'target': plan['target'], 'result': result, 'at': time.time()}
        path = p.job(job) / 'micro-results' / (uuid.uuid4().hex + '.json')
        write(path, record)
        p.event(job, 'control', 'micro_plan_result', json.dumps(record, ensure_ascii=False))
        if result['success']:
            p.resolve_issues(job, 'control', 'recovery', action=plan['strategy'], evidence=str(path) + ': ' + result['evidence'])
        return record


def runtime_ready(p, job, service):
    """All roots require selected accounts. Provider readiness/budgets verify identity/device."""
    from pilot import Blocked
    cfg = settings(p, job)
    session = cfg.get('management_session', {})
    if (not cfg.get('session_id') or cfg['session_id'] != session.get('session_id')
            or not session.get('pool') or session.get('preset') != 'remote-t4'):
        raise Blocked('MANAGEMENT_SETUP_REQUIRED: select and bind the account session before remote production')
    default = session.get('defaults', {}).get(service)
    if session.get('selection') == 'specified' and (not default or default not in session['pool']):
        raise Blocked('MANAGEMENT_SETUP_REQUIRED: the selected service needs an account in this job pool')
    return session


def micro_plan(p, job, plan):
    """Serialize API and CLI history checks together with their append operation."""
    require(p, job, 'repair')
    path = p.job(job) / 'micro-plan.lock'
    with path.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        return _micro_plan(p, job, plan)


SCHEMA_FILES = ('outline-v3.json', 'brief-v3.json', 'content-v3.json', 'audio.json',
                'images-v2.json', 'render.json', 'envelope.json', 'control.json')


def schema_snapshot(p):
    from pilot import read
    return {name: read(p.root / 'schemas' / name) for name in SCHEMA_FILES}


def _schema_compatible(old, new):
    """Conservative schema relaxation check; unsupported semantic changes need migration."""
    if json.dumps(old, sort_keys=True) == json.dumps(new, sort_keys=True) or new is True or old is False:
        return True
    if new is False or old is True or not isinstance(old, dict) or not isinstance(new, dict):
        return False
    annotations = {'title', 'description', '$comment', 'examples', 'default'}
    managed = {'type', 'enum', 'const', 'required', 'properties', 'additionalProperties',
               'items', 'minimum', 'exclusiveMinimum', 'maximum', 'exclusiveMaximum',
               'minItems', 'maxItems', 'minLength', 'maxLength', 'minProperties', 'maxProperties'}
    for key in new.keys() - annotations - managed:
        if key not in old or new[key] != old[key]:
            return False
    if 'type' in new:
        if 'type' not in old:
            return False
        before = set(old['type'] if isinstance(old['type'], list) else [old['type']])
        after = set(new['type'] if isinstance(new['type'], list) else [new['type']])
        if 'number' in after:
            after.add('integer')
        if not before <= after:
            return False
    encode = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False)
    if 'enum' in new and ('enum' not in old or not {encode(x) for x in old['enum']} <= {encode(x) for x in new['enum']}):
        return False
    if 'const' in new and ('const' not in old or encode(new['const']) != encode(old['const'])):
        return False
    if not set(new.get('required', [])) <= set(old.get('required', [])):
        return False
    for key in ('minimum', 'exclusiveMinimum', 'minItems', 'minLength', 'minProperties'):
        if key in new and (key not in old or new[key] > old[key]):
            return False
    for key in ('maximum', 'exclusiveMaximum', 'maxItems', 'maxLength', 'maxProperties'):
        if key in new and (key not in old or new[key] < old[key]):
            return False
    old_extra, new_extra = old.get('additionalProperties', True), new.get('additionalProperties', True)
    if not _schema_compatible(old_extra, new_extra):
        return False
    for name, value in new.get('properties', {}).items():
        original = old.get('properties', {}).get(name, old_extra)
        if not _schema_compatible(original, value):
            return False
    for name, original in old.get('properties', {}).items():
        if name not in new.get('properties', {}) and not _schema_compatible(original, new_extra):
            return False
    if 'items' in new and not _schema_compatible(old.get('items', True), new['items']):
        return False
    return True
