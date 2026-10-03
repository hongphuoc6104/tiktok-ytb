"""Bind real Flow dispatch to the job's frozen management session.

Browser profile verification is not a claim of Google authentication. Stable
identity comes from the recorded provider/user mapping; provider failures keep
the exact owner and are never retried on a different account.
"""
from pathlib import Path
import json
import re

from account_budget import Budgets
from account_catalog import discover
from session_store import Sessions
from pilot import Blocked, read, write


def config(p, job):
    from execution import is_job
    live = read(p.root / 'config.json')
    if not is_job(p, job):
        return live
    frozen = p.payload(job, 'control')
    # Control revision is immutable provenance. New jobs may choose a new
    # default; an existing request/job must retain its selected provider.
    # A new global key is still a policy change. Existing jobs must not inherit
    # it implicitly and regenerate cached requests after a config upgrade.
    effective = dict(frozen)
    from execution import settings
    binding = settings(p, job).get('management_session', {}).get('runtime_bindings', {}).get('flow', {})
    target = binding.get('target', {})
    if target.get('tool_url'):
        effective['flow_tool_url'] = target['tool_url']
        effective['flow_profile'] = binding['account']
    return effective


def prompt_pin(p, job):
    """Read/validate an official immutable pin; legacy jobs stay legacy."""
    from execution import is_job, settings
    if not is_job(p, job):
        return None
    frozen = p.payload(job, 'control')
    if frozen.get('flow_prompt_version') is None:
        return None
    from flow_prompts import validate_pin, freeze
    cfg = settings(p, job)
    pin = cfg.get('flow_prompt_pin')
    if pin is None:
        raise Blocked('FLOW_TEMPLATE_PIN_REQUIRED: this new contract must freeze before first send')
    pin = freeze(frozen['flow_model'], frozen['flow_prompt_version'], existing_pin=pin)
    path = p.job(job) / 'flow/prompts/pin.json'
    if not path.is_file() or read(path) != pin:
        raise Blocked('FLOW_TEMPLATE_PIN_CHANGED: official pin artifact is missing or changed')
    from pilot import hashobj
    with p._db_lock:
        event = p.db.execute("SELECT 1 FROM events WHERE job=? AND event='flow_prompt_frozen' AND detail=?", (job, hashobj(pin))).fetchone()
    if not event:
        raise Blocked('FLOW_TEMPLATE_PIN_CHANGED: pin has no official freeze event')
    return validate_pin(pin)


def freeze_prompt_pin(p, job):
    """Official new-job pre-send persistence; authority and live lease required."""
    from execution import require, control, settings
    from flow_prompts import freeze
    from pilot import hashobj
    require(p, job, 'execute')
    state = control(p, job)
    if getattr(p, '_execution_job', None) != job or state.get('owner') != getattr(p, '_execution_owner', None):
        raise Blocked('JOB_LEASE_REQUIRED: prompt freeze belongs to the official controller')
    frozen = p.payload(job, 'control')
    if frozen.get('flow_prompt_version') is None:
        return None
    path = p.job(job) / 'flow/prompts/pin.json'
    existing = read(path) if path.is_file() else None
    records = [read(path) for path in (p.job(job) / 'flow/attempts').glob('*/request.json')]
    pin = freeze(frozen['flow_model'], frozen['flow_prompt_version'], existing_pin=existing,
                 request_states=[record['state'] for record in records])
    if settings(p, job).get('flow_prompt_pin') != pin:
        raise Blocked('FLOW_TEMPLATE_PIN_CHANGED: workflow pin differs from saved control')
    if existing is None:
        write(path, pin)
        p.event(job, 'control', 'flow_prompt_frozen', hashobj(pin))
    return pin


def budgets(p, job):
    cfg = config(p, job)
    return Budgets(cfg.get('flow_management_store') or cfg.get('colab_tts', {}).get('management_store'))


def before_send(p, job, folders, connection):
    from execution import before_submit, runtime_ready
    folders = [Path(folder) for folder in folders]
    records = [read(folder / 'request.json') for folder in folders]
    if all(record['state'] == 'generated' for record in records):
        for folder in folders:
            owner = read(folder / 'owner.json')
            if (connection.get('status') != 'connected' or
                    Path((connection.get('identity') or {}).get('observedProfile', '')).resolve() != Path(owner['profile_path'])):
                raise Blocked('FLOW_OWNER_MISMATCH: collection must use the original verified profile')
        return
    before_submit(p, job)
    session = runtime_ready(p, job, 'flow')
    identity = connection.get('identity') or {}
    observed = identity.get('observedProfile')
    if connection.get('status') != 'connected' or not observed:
        raise Blocked('FLOW_PROFILE_UNVERIFIED: reconnect and verify the selected browser profile')
    cfg = config(p, job)
    if cfg.get('flow_prompt_version') is not None:
        pinned = prompt_pin(p, job)
        from image_pipeline import _saved_template_prompt
        for record in records:
            identity_record = record['identity']
            if identity_record.get('prompt_template', {}).get('pin') != pinned or _saved_template_prompt(p, job, identity_record) != identity_record['actual_prompt']:
                raise Blocked('FLOW_TEMPLATE_RECORD_CHANGED: submit must use the exact pinned compiled prompt')
    if not cfg.get('flow_tool_url') or identity.get('toolUrl') != cfg['flow_tool_url']:
        raise Blocked('FLOW_PROJECT_MISMATCH: configure and connect the exact Flow tool URL frozen for this job')
    by_id = {x['id']: x for x in discover(system_root=p.root)['accounts'] if x['service'] == 'flow'}
    matching = [x for x in session['pool'] if x in by_id and
                (Path(by_id[x]['metadata_root']) / by_id[x]['profile']).resolve() == Path(observed).resolve()]
    binding = session.get('runtime_bindings', {}).get('flow', {})
    selected = binding.get('account') or session.get('defaults', {}).get('flow')
    if binding.get('target', {}).get('profile_path') and Path(binding['target']['profile_path']).resolve() != Path(observed).resolve():
        raise Blocked('FLOW_PROFILE_MISMATCH: connected profile differs from the frozen runtime binding')
    if session.get('selection') == 'specified':
        if selected not in matching:
            raise Blocked('FLOW_PROFILE_MISMATCH: connected browser differs from this job account selection')
        account = selected
    elif len(matching) == 1:
        account = matching[0]
    else:
        raise Blocked('FLOW_PROFILE_MISMATCH: connected browser must match one account in the selected pool')
    ledger = budgets(p, job)
    stable = ledger.read()['aliases'].get(account)
    if not stable:
        raise Blocked('FLOW_IDENTITY_REQUIRED: confirm or probe the stable Google identity before dispatch')
    records = []
    for folder in folders:
        folder = Path(folder)
        record = read(folder / 'request.json')
        owner = {'job': job, 'account': account, 'session': session['session_id'], 'identity': stable,
                 'profile_path': str(Path(observed).resolve()), 'operation': session['session_id'],
                 'model': cfg['flow_model'], 'project': cfg['flow_project'], 'tool_url': cfg['flow_tool_url']}
        old = read(folder / 'owner.json') if (folder / 'owner.json').exists() else None
        if old and old != owner:
            raise Blocked('FLOW_OWNER_MISMATCH: collect/reconcile on the original account and session')
        Sessions(p.root).pin(record['key'], job=job, service='flow', account=account,
                             session=session['session_id'], identity=stable)
        write(folder / 'owner.json', owner)
        records.append((record['key'], 1))
    try:
        ledger.flow_submit_many(account, session['session_id'], records,
                                cap=config(p, job).get('flow_session_image_cap', 100),
                                budget_session=session['session_id'],
                                evidence='verified browser profile; send boundary for ' + job)
    except ValueError as error:
        raise Blocked('FLOW_BUDGET: ' + str(error)) from error
    p.event(job, 'images', 'flow_account_active', json.dumps({'account': account, 'session': session['session_id'],
                                                           'requests': [key for key, _ in records]}))


def sync(p, job, folder, record):
    """Reflect real journal outcomes; an unknown outcome remains charged."""
    owner_path = Path(folder) / 'owner.json'
    if not owner_path.exists():
        return
    owner = read(owner_path)
    ledger = budgets(p, job)
    state = {'downloaded': 'collected', 'submitted': 'unknown', 'ambiguous': 'ambiguous',
             'generated': 'generated', 'not_submitted': 'not_submitted'}.get(record['state'])
    if state:
        existing = ledger.read()['accounts'].get(owner['identity'], {}).get('flow', {}).get(owner['operation'], {})
        if record['key'] in existing:
            ledger.flow_state(owner['account'], owner['operation'], record['key'], state,
                              'journal:' + str(Path(folder) / 'request.json'))
    # A known not-submitted response may still be a service-wide stop.
    # Preserve it across controllers rather than allowing the next target.
    text = record.get('error', '').lower()
    patterns = [('captcha', r'captcha'), ('bot', r'unusual activity|automated requests|abuse detected|bot detected'),
                ('429', r'\b429\b|rate.?limit'), ('503', r'\b503\b'),
                ('quota', r'quota|resource_exhausted|limit exceeded'),
                ('auth', r'invalid_grant|unauthenticated|login.required|sign.?in.required|token.{0,24}(expired|revoked)')]
    kind = next((kind for kind, pattern in patterns if re.search(pattern, text)), None)
    if kind:
        try:
            ledger.recover(owner['account'], 'flow', record['key'], action='reconcile', error=kind,
                           submit_state=state or 'unknown', evidence='journal:' + str(Path(folder) / 'request.json'))
        except ValueError:
            pass  # recover persisted the service block before raising.
        p.event(job, 'images', 'flow_account_blocked', json.dumps({'account': owner['account'], 'reason': kind}))
