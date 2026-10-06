"""Internal budgets, not provider quota: count allocated runtime and sent slots.

All writes are locked across controllers. Provider adapters supply real evidence;
profile presence and page opening never start a runtime interval.
"""
import json
from pathlib import Path
import time
from session_store import locked_json

HOUR = 3600
WINDOW = 24 * HOUR
HARD_STOPS = {'quota', '429', '503', 'captcha', 'bot', 'auth', 'login_required'}


class Budgets:
    def __init__(self, store=None):
        self.path = Path(store or Path.home() / '.config/video-pilot/management') / 'budgets.json'

    def read(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {'version': 1, 'aliases': {}, 'accounts': {}, 'events': []}

    def bind_identity(self, alias, identity, evidence):
        if not alias or not identity or not evidence:
            raise ValueError('Verified identity mapping evidence required')
        with locked_json(self.path, self.read) as data:
            old = data['aliases'].get(alias)
            if old and old != identity:
                raise ValueError('Identity alias is already pinned')
            data['aliases'][alias] = identity
            data['events'].append({'event': 'identity_bound', 'alias': alias, 'identity': identity, 'evidence': evidence, 'at': time.time()})

    def _identity(self, data, account):
        # Never initialize independent counters for unverified browser aliases.
        if account not in data['aliases']:
            raise ValueError('Stable account identity is required before budget allocation')
        return data['aliases'][account]

    def _account(self, data, account):
        identity = self._identity(data, account)
        return data['accounts'].setdefault(identity, {'anchor': None, 'intervals': [], 'holds': {}, 'flow': {}, 'recovery': {}, 'blocks': {}})

    def allocated(self, account, session, *, device, at=None, evidence):
        if device != 'T4' or not evidence:
            raise ValueError('Confirmed T4 allocation evidence required; no CPU fallback')
        at = time.time() if at is None else at
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            if any(x['end'] is None for x in state['intervals']):
                raise ValueError('Dedicated preset permits one allocated GPU runtime per identity')
            state['anchor'] = at if state['anchor'] is None else state['anchor']
            state['intervals'].append({'session': session, 'device': device, 'start': at, 'end': None, 'uncertain': False, 'evidence': evidence})
            data['events'].append({'event': 'allocated', 'account': account, 'session': session, 'at': at, 'evidence': evidence})

    def released(self, account, session, *, at=None, evidence):
        if not evidence:
            raise ValueError('Confirmed release/termination evidence required')
        at = time.time() if at is None else at
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            interval = next((x for x in state['intervals'] if x['session'] == session and x['end'] is None), None)
            if not interval or at < interval['start']:
                raise ValueError('Allocated session and valid release time required')
            interval.update(end=at, release_evidence=evidence)
            data['events'].append({'event': 'released', 'account': account, 'session': session, 'at': at, 'evidence': evidence})

    def uncertain(self, account, session, evidence):
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            interval = next(x for x in state['intervals'] if x['session'] == session and x['end'] is None)
            interval.update(uncertain=True, telemetry_evidence=evidence)

    def service_rechecked(self, account, session, *, device, evidence, at=None):
        """Record actual service/runtime evidence for the current budget window."""
        if device != 'T4' or not evidence:
            raise ValueError('Confirmed T4 service recheck evidence required')
        at = time.time() if at is None else at
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            interval = next((x for x in state['intervals'] if x['session'] == session and x['end'] is None), None)
            if interval is None or at < interval['start']:
                raise ValueError('Recheck must belong to the active allocated session')
            state['service_recheck'] = {'session': session, 'at': at, 'device': device, 'evidence': evidence}
            interval.update(uncertain=False, telemetry_evidence=evidence)

    def snapshot(self, account, now=None, data=None):
        now = time.time() if now is None else now
        data = self.read() if data is None else data
        identity = data['aliases'].get(account)
        state = data['accounts'].get(identity, {})
        anchor = state.get('anchor')
        start = anchor + max(0, int((now - anchor) // WINDOW)) * WINDOW if anchor is not None else None
        used = 0
        if start is not None:
            used = sum(max(0, min(x['end'] if x['end'] is not None else now, start + WINDOW) - max(x['start'], start)) for x in state['intervals'])
        held = sum(x['seconds'] for x in state.get('holds', {}).values())
        flow = state.get('flow', {})
        return {'identity_configured': identity is not None, 'window_start': start,
                'window_end': start + WINDOW if start is not None else None,
                'needs_service_recheck': anchor is not None and now >= anchor + WINDOW and not (
                    state.get('service_recheck', {}).get('at', -1) >= start and
                    any(x['session'] == state.get('service_recheck', {}).get('session') and x['end'] is None for x in state.get('intervals', []))),
                'display_seconds': 6 * HOUR, 'usable_seconds': 5 * HOUR, 'reserve_seconds': HOUR,
                'used_seconds': used, 'held_seconds': held, 'available_seconds': max(0, 5 * HOUR - used - held),
                'uncertain': any(x.get('uncertain') and x['end'] is None for x in state.get('intervals', [])),
                'historical_uncertainty': any(x.get('uncertain') for x in state.get('intervals', [])),
                'allocated_sessions': [x for x in state.get('intervals', []) if x['end'] is None],
                'flow': {operation: {'slots': sum(x['slots'] for x in requests.values()), 'requests': requests} for operation, requests in flow.items()},
                'blocks': state.get('blocks', {}), 'source': 'internal_project_ledger', 'provider_quota_verified': False}

    def reserve(self, account, request, seconds, *, now=None):
        if not isinstance(seconds, (int, float)) or seconds <= 0:
            raise ValueError('Positive task estimate required')
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            if request in state['holds']:
                if state['holds'][request]['seconds'] != seconds:
                    raise ValueError('Reservation already exists')
                return
            status = self.snapshot(account, now, data)
            if status['needs_service_recheck']:
                raise ValueError('New budget window requires actual service recheck before submission')
            if state['blocks'].get('colab') or status['available_seconds'] < seconds:
                raise ValueError('Internal budget insufficient or service blocked; do not rotate account')
            state['holds'][request] = {'seconds': seconds, 'at': time.time()}

    def settle(self, account, request):
        with locked_json(self.path, self.read) as data:
            self._account(data, account)['holds'].pop(request, None)

    def flow_submit(self, account, operation, request, slots, *, cap=100, evidence, budget_session=None):
        return self.flow_submit_many(account, operation, [(request, slots)], cap=cap, evidence=evidence, budget_session=budget_session)

    def allow_flow_repair(self, account, budget_session, *, extra_slots, system_root, grant, job, source, evidence):
        """Append a small, authorized repair allowance without resetting usage.

        This is an internal project limit. Provider/service blocks remain hard
        stops and all original request ownership and slot counts are retained.
        """
        from permissions import Grants
        if (type(extra_slots) is not int or not 1 <= extra_slots <= 4 or not budget_session
                or not isinstance(source, str) or not source.strip() or not evidence):
            raise ValueError('Bounded repair slots, actual source and evidence required')
        authority = Grants(system_root).require(grant, 'development', 'system', job=job,
                                                path=Path(system_root).resolve() / 'account_budget.py')
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            if state.get('blocks', {}).get('flow'):
                raise ValueError('Provider/service blocked; repair allowance cannot bypass it')
            limit = state.get('flow_limits', {}).get(budget_session)
            if not isinstance(limit, int) or limit < 100 or limit + extra_slots > 200:
                raise ValueError('Existing session limit and maximum 200 required')
            state.setdefault('flow_repair_allowances', {})
            if any(x.get('event') == 'flow_repair_allowance' and x.get('job') == job
                   and x.get('budget_session') == budget_session and x.get('evidence') == evidence
                   for x in data['events']):
                raise ValueError('Identical repair evidence already has an allowance')
            record = {'job': job, 'account': account, 'budget_session': budget_session,
                      'previous_limit': limit, 'limit': limit + extra_slots, 'extra_slots': extra_slots,
                      'source': source, 'evidence': evidence, 'grant': authority['id'], 'at': time.time()}
            state['flow_repair_allowances'][budget_session] = record
            state['flow_limits'][budget_session] = record['limit']
            data['events'].append({'event': 'flow_repair_allowance', **record})
        return record

    def flow_submit_many(self, account, operation, entries, *, cap=100, evidence, budget_session=None):
        budget_session = budget_session or 'legacy-shared-session'
        if (not isinstance(cap, int) or isinstance(cap, bool) or cap < 100 or cap > 200 or not entries or not evidence
                or any(not isinstance(key, str) or not key or not isinstance(slots, int) or isinstance(slots, bool) or slots < 1 for key, slots in entries)
                or len({key for key, _ in entries}) != len(entries)):
            raise ValueError('Flow cap 100–200, positive slots and submission evidence required')
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            requests = state['flow'].setdefault(operation, {})
            if any(key in items and items[key]['state'] != 'not_submitted' for key, _ in entries for items in state['flow'].values()):
                raise ValueError('Existing request: collect/reconcile, never resubmit')
            # Flow uses an explicit management session, not a 24-hour reset.
            # Operation/job names are trace labels, never independent budgets.
            # Unresolved sends remain charged even when the session changes.
            now = time.time()
            limits = state.setdefault('flow_limits', {})
            limit_key = budget_session
            allowance = state.get('flow_repair_allowances', {}).get(limit_key)
            if allowance and allowance.get('limit') == limits.get(limit_key):
                cap = max(cap, allowance['limit'])
            limits[limit_key] = min(limits.get(limit_key, cap), cap)
            used = sum(x['slots'] for items in state['flow'].values() for x in items.values()
                       if x.get('state') != 'not_submitted' and (x.get('budget_session', 'legacy-shared-session') == budget_session or x.get('state') in ('submitted', 'unknown', 'ambiguous')))
            if state['blocks'].get('flow') or used + sum(slots for _, slots in entries) > limits[limit_key]:
                raise ValueError('Flow internal budget/service blocked; do not rotate account')
            for key, slots in entries:
                requests[key] = {'slots': slots, 'state': 'submitted', 'at': now, 'budget_session': budget_session, 'evidence': evidence}

    def flow_state(self, account, operation, request, state, evidence):
        if state not in ('generated', 'collected', 'failed', 'unknown', 'ambiguous', 'not_submitted') or not evidence:
            raise ValueError('Observed state/evidence required')
        with locked_json(self.path, self.read) as data:
            self._account(data, account)['flow'][operation][request].update(state=state, evidence=evidence)

    def recover(self, account, service, episode, *, action, error, submit_state, evidence):
        if service not in ('flow', 'colab') or not evidence or not episode:
            raise ValueError('Exact service/episode and evidence required')
        with locked_json(self.path, self.read) as data:
            state = self._account(data, account)
            if error in HARD_STOPS:
                state['blocks'][service] = {'error': error, 'evidence': evidence, 'at': time.time()}
                allowed = False
            elif state['blocks'].get(service):
                allowed = False
            else:
                records = state['recovery'].setdefault(service + ':' + episode, [])
                allowed = len(records) < 3 and (submit_state not in ('unknown', 'ambiguous', 'submitted') or action in ('collect', 'reconcile'))
                if allowed:
                    records.append({'action': action, 'error': error, 'submit_state': submit_state, 'evidence': evidence, 'at': time.time()})
        if not allowed:
            raise ValueError('Recovery blocked: preserve request, no generation retry or account rotation')
        return len(self.read()['accounts'][self.read()['aliases'][account]]['recovery'][service + ':' + episode])
