"""FlowPool orchestration: run / doctor / status.

Safety rules enforced here (the Node worker enforces the UI half):
- never solve CAPTCHA, never sign in: such profiles leave the rotation and are reported;
- a request whose generation may have started is never submitted again
  (journal `submitted` -> `unknown` on restart, explicit Flow refusals -> `failed`);
- clips need `video_generation: true`, a positive monthly `credit_budget`, and
  enough remaining budget according to the ledger.
"""
import collections
import concurrent.futures
import copy
import math
import time
from pathlib import Path

from . import config as config_mod
from .driver import DAEMON_CODES, DECLINED, PROFILE_CODES, DaemonDriver, DriverError
from .journal import SAFE_ID, UNRESOLVED, Journal, identity, key_for
from .ledger import Ledger
from .profiles import Pool, STICKY
from .ledger import month_of
from .scheduler import Context, can_ever_run, eligible, engine, next_batch
from .store import file_lock
from .validate import ValidationError, validate_output

KINDS = ('image', 'clip')
RATIOS = ('16:9', '9:16')
# Errors raised before submit that point at the profile's tab/tool rather than
# at the request: park the profile until a human looks (doctor/mark).
MANUAL_ATTENTION = ('UNRESOLVED_FLOW_QUEUE', 'TOOL_NOT_READY', 'MODEL_NOT_SELECTABLE', 'FRAME_NOT_ATTACHED',
                    'REFERENCE_NOT_ATTACHED', 'PROJECT_NOT_FOUND')


def normalize_request(raw, cfg, out_root):
    """Validate a section-8 request and fill defaults. Raises ValueError."""
    if not isinstance(raw, dict):
        raise ValueError('INVALID_REQUEST: object required')
    r = dict(raw)
    if not SAFE_ID.match(str(r.get('id') or '')):
        raise ValueError('INVALID_REQUEST: id must match [A-Za-z0-9_-]{1,120}')
    if r.get('kind') not in KINDS:
        raise ValueError('INVALID_REQUEST: kind must be image or clip')
    if not isinstance(r.get('prompt'), str) or not r['prompt'].strip():
        raise ValueError('INVALID_REQUEST: prompt required')
    if r.get('ratio') not in RATIOS:
        raise ValueError('INVALID_REQUEST: ratio must be 16:9 or 9:16')
    refs = r.get('refs') or []
    if not isinstance(refs, list):
        raise ValueError('INVALID_REQUEST: refs must be a list of paths')
    r['refs'] = [str(Path(x).resolve()) for x in refs]
    for x in r['refs']:
        if not Path(x).is_file():
            raise ValueError(f'INVALID_REQUEST: missing reference {x}')
    variants = r.get('variants', 1)
    if not isinstance(variants, int) or not 1 <= variants <= 4:
        raise ValueError('INVALID_REQUEST: variants must be 1..4')
    r['variants'] = variants
    bootstrap = r.get('purpose') == 'mascot_bootstrap'
    if bootstrap and (r['kind'] != 'image' or r['refs'] or variants != 1):
        raise ValueError('INVALID_MASCOT_BOOTSTRAP: requires one image variant with no refs')
    if r['kind'] == 'image':
        if not r['refs'] and not bootstrap:
            raise ValueError('CHARACTER_REFERENCE_REQUIRED: refs[0] is the character reference (refs[1] optional base image)')
        if len(r['refs']) > 2:
            raise ValueError('INVALID_REQUEST: at most two refs (character, base)')
        r['start_frame'] = None
        r.setdefault('model', cfg.get('flow_model'))
    else:
        sf = r.get('start_frame')
        if not sf or not Path(sf).is_file():
            raise ValueError('START_FRAME_REQUIRED: clip needs an existing approved still as start_frame')
        r['start_frame'] = str(Path(sf).resolve())
        r.setdefault('model', cfg.get('veo_model'))
    r['model'] = r.get('model') or (cfg.get('flow_model') if r['kind'] == 'image' else cfg.get('veo_model'))
    r['out_dir'] = str(Path(r.get('out_dir') or Path(out_root) / (r.get('job') or 'adhoc') / r['id']).resolve())
    return r


def result_of(req_id, status, snap=None, error=None, code=None, files=None):
    snap = snap or {}
    outputs = snap.get('outputs') or []
    ranking = next((e.get('ranking') for e in reversed(snap.get('events') or []) if e.get('ranking')), None)
    return {'id': req_id, 'status': status,
            'files': files if files is not None else [o['path'] for o in outputs],
            # Best variant by local checks (flowpool.rank); a dashboard pick overrides it downstream.
            'best': ranking[0]['path'] if ranking else None, 'ranking': ranking,
            'media_ids': [o.get('media_id') for o in outputs],
            'profile': snap.get('profile'), 'credits_before': snap.get('credits_before'),
            'credits_after': snap.get('credits_after'), 'error': error if error is not None else snap.get('error'),
            'code': code if code is not None else snap.get('code'), 'key': snap.get('key'),
            'state': snap.get('state')}


class FlowPool:
    def __init__(self, cfg=None, driver_factory=None, clock=time.time, locate=None):
        self.cfg = config_mod.load(cfg) if cfg is None or 'flowpool_state_dir' not in cfg else dict(config_mod.DEFAULTS, **cfg)
        self.dir = config_mod.state_dir(self.cfg)
        self.driver_factory = driver_factory or (lambda profile, cfg: DaemonDriver(profile, cfg))
        self.clock = clock
        # Which declared profiles currently have a tab in the shared Chrome: asked from
        # the daemon (its single CDP connection) -> ({name: {target_id, url, via}}, error|None).
        self.locate_fn = locate or self._daemon_locate
        self.journal = Journal(self.dir / 'journal')
        self.ledger = Ledger(self.dir / 'ledger.ndjson')
        self.lock_path = self.dir / 'run.lock'

    # ------------------------------------------------------------------ helpers
    def pool(self):
        return Pool(self.dir / 'profiles.json', self.cfg, declared=self.cfg.get('flowpool_browser_profiles'))

    def clip_cost(self, model):
        fallback = (self.cfg.get('flowpool_clip_credit_estimate') or {}).get(model, 0)
        return self.ledger.cost_per_clip(model, fallback)[0]

    def context(self):
        return Context(self.cfg, self.journal.media_lookup(), self.clip_cost, self.remaining)

    # ------------------------------------------------------------------ credits
    def monthly_cap(self, profile):
        return float(profile.get('monthly_credits') or self.cfg.get('flowpool_profile_monthly_credits') or 0)

    def month_used(self, profile):
        return self.ledger.month_spend(profile=profile['name'])[0]

    def remaining(self, profile):
        """Credits this profile may still spend this month: its monthly cap minus the
        ledger's spend, lowered to the UI balance when one was read this month."""
        left = self.monthly_cap(profile) - self.month_used(profile)
        ui = profile.get('credits')
        if ui is not None and profile.get('credits_at') and month_of(profile['credits_at']) == month_of(self.clock()):
            left = min(left, ui)
        return max(0.0, left)

    def effective_budget(self, pool):
        """Monthly pool budget: sum of the active profiles' caps, unless credit_budget is lower."""
        caps = sum(self.monthly_cap(p) for p in pool.profiles)
        budget = self.cfg.get('credit_budget') or 0
        return min(caps, budget) if budget > 0 else 0

    # ------------------------------------------------------------------ daemon
    def _daemon_locate(self, profiles, dedupe=False):
        from .daemon_client import DaemonClient, DaemonError
        try:
            reply = DaemonClient(self.cfg).call('locate', timeout=60, dedupe=dedupe,
                                               profiles=[{k: v for k, v in p.items() if not k.startswith('_')} for p in profiles])
        except DaemonError as ex:
            return {}, ex.code
        if not reply.get('ok'):
            return {}, reply.get('code') or 'DAEMON_ERROR'
        return reply.get('located') or {}, None

    def located(self, pool, dedupe=False):
        found, error = self.locate_fn(pool.profiles, dedupe) if dedupe else self.locate_fn(pool.profiles)
        for name, info in (found or {}).items():
            if info and info.get('target_id'):
                pool.record_binding(name, {'target_id': info['target_id']})
        return {n for n, info in (found or {}).items() if info}, error

    def _finish(self, results, req, status, error=None, code=None, state=None, **payload):
        snap = None
        if state:
            try:
                snap = self.journal.transition(req['_key'], state, error=error, code=code, **payload)
            except Exception:
                snap = self.journal.load(req['_key'])
        results[req['id']] = result_of(req['id'], status, snap or self.journal.load(req['_key']), error, code)

    def _item(self, req, profile, ctx):
        media = [ctx.media_id(profile, sha) for sha in req['_ref_shas']]
        return {'id': req['id'], 'kind': req['kind'], 'prompt': req['prompt'], 'ratio': req['ratio'],
                'refs': req['refs'], 'ref_media_ids': media, 'start_frame': req.get('start_frame'),
                'variants': req['variants'], 'model': req['model'], 'out_dir': req['out_dir'],
                'purpose': req.get('purpose'),
                'engine': engine(profile, req, ctx),
                'seconds': self.cfg.get('flowpool_clip_seconds', 8)}

    def _validate(self, req, snap):
        infos = []
        for out in snap.get('outputs') or []:
            infos.append(validate_output(out['path'], req['kind'], req['ratio'], self.cfg.get('flowpool_clip_seconds', 8)))
        if len(infos) < req['variants']:
            raise ValidationError(f'OUTPUT_COUNT: expected {req["variants"]}, got {len(infos)}')
        return infos

    def _settle_collected(self, req, snap, results):
        try:
            infos = self._validate(req, snap)
        except (ValidationError, OSError) as ex:
            # Bytes exist; a bad file is a failed result, never a reason to regenerate.
            self._finish(results, req, 'failed', str(ex), 'VALIDATION_FAILED', 'failed')
            return
        from .rank import rank
        refs = list(req.get('refs') or []) + ([req['start_frame']] if req.get('start_frame') else [])
        ranking = rank([i['path'] for i in infos], req['ratio'], refs)
        snap = self.journal.transition(req['_key'], 'validated', validation=infos, ranking=ranking)
        results[req['id']] = result_of(req['id'], 'ok', snap)

    # ------------------------------------------------------------------ run
    def run(self, requests):
        results, order = {}, []
        with file_lock(self.lock_path, blocking=False):
            pool = self.pool()
            pool.refresh()
            recovered = self.journal.recover()
            pending = self._admit(requests, results, order)
            ctx = self.context()
            self._gate_clips(pending, results)
            self._dispatch(pool, pending, results, ctx)
        out = [results[i] for i in order if i in results]
        if recovered:
            for r in out:
                r.setdefault('recovered_unknown', r.get('key') in recovered)
        return out

    def _admit(self, requests, results, order):
        pending = []
        seen = set()
        for raw in requests:
            rid = raw.get('id') if isinstance(raw, dict) else None
            rid = rid if isinstance(rid, str) else f'#{len(order)}'
            if rid in seen:
                results[rid + '#dup'] = result_of(rid, 'failed', error='DUPLICATE_REQUEST_ID', code='DUPLICATE_REQUEST_ID')
                order.append(rid + '#dup')
                continue
            seen.add(rid)
            order.append(rid)
            try:
                req = normalize_request(raw, self.cfg, self.dir / 'out')
                ident = identity(req)
            except (ValueError, OSError) as ex:
                results[rid] = result_of(rid, 'failed', error=str(ex), code=str(ex).split(':')[0])
                continue
            req.update(_key=key_for(ident), _ref_shas=ident['refs'], _ident=ident)
            others = [s for s in self.journal.by_request_id(req['id'])
                      if s['key'] != req['_key'] and s['state'] in UNRESOLVED]
            if others:
                results[rid] = result_of(rid, 'unknown', others[0], code='RECONCILE_REQUIRED',
                                         error=f'earlier attempt {others[0]["key"][:12]} of this id is {others[0]["state"]}; '
                                               'reconcile it before changing the request')
                continue
            snap = self.journal.load(req['_key'])
            state = snap['state'] if snap else None
            if state == 'validated':
                results[rid] = result_of(rid, 'ok', snap)
            elif state == 'collected':
                self._settle_collected(req, snap, results)
            elif state in UNRESOLVED:
                results[rid] = result_of(rid, 'unknown', snap, code='RECONCILE_REQUIRED',
                                         error='outcome unknown; never resubmitted automatically (flowpool reconcile)')
            elif state == 'failed':
                results[rid] = result_of(rid, 'failed', snap)
            else:
                self.journal.intent(req, ident)
                pending.append(req)
        return pending

    def _gate_clips(self, pending, results):
        for req in [r for r in pending if r['kind'] == 'clip']:
            code = None
            if not self.cfg.get('video_generation'):
                code = 'CLIP_DISABLED: config video_generation is false'
            elif (self.cfg.get('credit_budget') or 0) <= 0:
                code = 'CREDIT_BUDGET_ZERO: set a positive monthly credit_budget'
            if code:
                pending.remove(req)
                self._finish(results, req, 'failed', code, code.split(':')[0], 'not_submitted')

    def _budget_allows(self, req, ctx, reserved, pool):
        spent, _ = self.ledger.month_spend()
        return spent + reserved + ctx.cost(req) <= self.effective_budget(pool)

    def _dispatch(self, pool, pending, results, ctx):
        max_active = max(1, int(self.cfg.get('flowpool_max_parallel') or self.cfg.get('flowpool_max_browsers') or 1))
        cap = max(1, min(4, int(self.cfg.get('flowpool_per_browser_queue') or 4)))
        max_tries = int(self.cfg.get('flowpool_max_profile_attempts') or 2)
        tries = collections.Counter()
        rr = [-1]
        active = {}
        open_names, daemon_error = self.located(pool) if pending else (set(), None)
        running = [p for p in pool.profiles if p['name'] in open_names]
        reserved = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_active) as executor:
            while True:
                while len(active) < max_active and pending:
                    busy = {name for name, _ in active.values()}
                    choice = next_batch(pending, running, ctx, busy, max_active - len(active), rr, cap)
                    if not choice:
                        break
                    profile, batch = choice
                    if batch[0]['kind'] == 'clip' and not self._budget_allows(batch[0], ctx, sum(reserved.values()), pool):
                        pending.remove(batch[0])
                        self._finish(results, batch[0], 'failed', 'CREDIT_BUDGET_EXCEEDED: monthly credit_budget reached',
                                     'CREDIT_BUDGET_EXCEEDED', 'not_submitted')
                        continue
                    for r in batch:
                        pending.remove(r)
                        tries[r['id']] += 1
                    pool.acquire(profile['name'])
                    fut = executor.submit(self._execute, pool, profile['name'], batch, ctx)
                    active[fut] = (profile['name'], batch)
                    if batch[0]['kind'] == 'clip':
                        reserved[fut] = ctx.cost(batch[0])
                for req in list(pending):
                    if not can_ever_run(req, running, ctx):
                        pending.remove(req)
                        reasons = {p['name']: eligible(p, req, ctx)[1] if p in running else 'no_tab'
                                   for p in pool.profiles}
                        if daemon_error:
                            reasons = f'daemon {daemon_error} (python3 -m flowpool daemon start)'
                        self._finish(results, req, 'failed', f'NO_ELIGIBLE_PROFILE: {reasons}', 'NO_ELIGIBLE_PROFILE', 'not_submitted')
                if not active:
                    for req in list(pending):
                        pending.remove(req)
                        self._finish(results, req, 'failed', 'NO_READY_PROFILE: every eligible profile is cooling down or blocked',
                                     'NO_READY_PROFILE', 'not_submitted')
                    break
                done, _ = concurrent.futures.wait(list(active), return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    name, batch = active.pop(fut)
                    reserved.pop(fut, None)
                    outcome = fut.result()
                    pool.release(name, outcome['state'], outcome['reason'], outcome['until'])
                    results.update(outcome['results'])
                    if outcome.get('drop_profile'):
                        running = [p for p in running if p['name'] != name]
                    if outcome.get('daemon_lost'):
                        for req in list(pending):
                            pending.remove(req)
                            self._finish(results, req, 'failed', f"{outcome['daemon_lost']}: FlowPool daemon lost its Chrome "
                                         'connection; click Allow in Chrome, then python3 -m flowpool daemon reconnect',
                                         outcome['daemon_lost'], 'not_submitted')
                    for req in outcome['retry']:
                        if tries[req['id']] < max_tries:
                            self.journal.intent(req, req['_ident'])
                            pending.append(req)
                        else:
                            snap = self.journal.load(req['_key'])
                            results[req['id']] = result_of(req['id'], 'failed', snap)

    def _execute(self, pool, name, batch, ctx):
        """Run one batch on one profile. Never raises; returns an outcome dict."""
        outcome = {'state': None, 'reason': None, 'until': None, 'results': {}, 'retry': []}
        kind = batch[0]['kind']
        submitted = False
        driver = None
        credits_before = None
        try:
            profile = copy.deepcopy(pool.get(name))
            driver = self.driver_factory(profile, self.cfg)
            opened = driver.open() or {}
            pool.record_email(name, opened.get('email'))
            reading = driver.read_credits() or {}
            credits_before = reading.get('value')
            self.ledger.reading(name, credits_before, reading.get('raw'), reading.get('method'))
            pool.record_credits(name, credits_before)
            if kind == 'clip' and self.remaining(pool.get(name)) < ctx.cost(batch[0]):
                for req in batch:
                    self.journal.transition(req['_key'], 'not_submitted', code='LOW_CREDIT', profile=name)
                outcome.update(state='low_credit', reason=f'{self.remaining(pool.get(name)):.0f} credits left < {ctx.cost(batch[0])}',
                               retry=list(batch))
                return outcome
            items = [self._item(r, profile, ctx) for r in batch]
            queue_ids = driver.prepare(kind, items) or []
            for i, req in enumerate(batch):
                self.journal.transition(req['_key'], 'submitted', profile=name, credits_before=credits_before,
                                        queue_ids=[queue_ids[i]] if i < len(queue_ids) else [])
            submitted = True
            produced = driver.commit(self.cfg.get('flowpool_clip_timeout_seconds' if kind == 'clip' else 'flowpool_image_timeout_seconds', 300))
            credits_after = self._read_after(driver, name, pool)
            self._collect(batch, produced, name, credits_before, credits_after, outcome)
            if kind == 'clip' and self.remaining(pool.get(name)) < self.clip_cost(batch[0]['model']):
                outcome.update(state='low_credit', reason=f'{self.remaining(pool.get(name)):.0f} credits left this month')
        except DriverError as ex:
            self._driver_failure(ex, batch, name, submitted, credits_before, driver, outcome, pool)
        except Exception as ex:  # programming or local I/O error
            code = 'INTERNAL'
            for req in batch:
                snap = self.journal.load(req['_key'])
                if snap and snap['state'] == 'submitted':
                    snap = self.journal.transition(req['_key'], 'unknown', code=code, error=repr(ex), profile=name)
                    outcome['results'][req['id']] = result_of(req['id'], 'unknown', snap)
                elif snap and snap['state'] == 'intent':
                    snap = self.journal.transition(req['_key'], 'not_submitted', code=code, error=repr(ex))
                    outcome['results'][req['id']] = result_of(req['id'], 'failed', snap)
                elif req['id'] not in outcome['results']:
                    outcome['results'][req['id']] = result_of(req['id'], 'unknown' if submitted else 'failed', snap, repr(ex), code)
            outcome.update(state='cooldown', reason=f'{code}: {ex!r}', until=None)
        finally:
            if driver is not None:
                # A project can be identified before a later UI check fails.
                # Keep its URL so the next probe does not create another one.
                pool.record_project(name, getattr(driver, 'project_url', None))
                try:
                    driver.close()
                except Exception:
                    pass
        return outcome

    def _read_after(self, driver, name, pool):
        try:
            reading = driver.read_credits() or {}
        except DriverError:
            return None
        value = reading.get('value')
        self.ledger.reading(name, value, reading.get('raw'), reading.get('method'))
        pool.record_credits(name, value)
        return value

    def _collect(self, batch, produced, name, credits_before, credits_after, outcome):
        by_id = {x.get('id'): x for x in produced or []}
        for req in batch:
            got = by_id.get(req['id'])
            files = (got or {}).get('files') or []
            if not files:
                snap = self.journal.transition(req['_key'], 'unknown', code='RESULT_MISSING', profile=name,
                                               error='commit returned no file for this request')
                outcome['results'][req['id']] = result_of(req['id'], 'unknown', snap)
                continue
            media = (got.get('media_ids') or []) + [None] * len(files)
            outputs = []
            for path, media_id in zip(files, media):
                entry = {'path': str(path), 'media_id': media_id}
                try:
                    from .journal import sha256_file
                    entry['sha256'] = sha256_file(path)
                except OSError:
                    entry['sha256'] = None
                outputs.append(entry)
            snap = self.journal.transition(req['_key'], 'collected', profile=name, outputs=outputs,
                                           credits_before=credits_before, credits_after=credits_after)
            self.ledger.submission(profile=name, kind=req['kind'], model=req['model'], request_id=req['id'],
                                   key=req['_key'], job=req.get('job'), scene=req.get('scene'), variants=req['variants'],
                                   credits_before=credits_before, credits_after=credits_after, batch_size=len(batch),
                                   status='ok', estimate=self.clip_cost(req['model']) * req['variants'] if req['kind'] == 'clip' else 0)
            self._settle_collected(req, snap, outcome['results'])

    def _driver_failure(self, ex, batch, name, submitted, credits_before, driver, outcome, pool):
        state = PROFILE_CODES.get(ex.code)
        if not submitted:
            for req in batch:
                self.journal.transition(req['_key'], 'not_submitted', code=ex.code, error=str(ex), profile=name)
            outcome['retry'] = list(batch)
            if ex.code in DAEMON_CODES:
                # The one CDP connection is gone: stop everything and let the user act (Allow / daemon start).
                outcome.update(state=None, reason=None, retry=[], daemon_lost=ex.code)
                for req in batch:
                    outcome['results'][req['id']] = result_of(req['id'], 'failed', self.journal.load(req['_key']))
            elif ex.code == 'PROFILE_TAB_NOT_FOUND':
                outcome.update(state=None, reason=None, drop_profile=True)   # its tab closed: others take the work
            elif state == 'cooldown':
                outcome.update(state='cooldown', reason=ex.code, until=self.clock() + self.cfg.get('flowpool_cooldown_seconds', 900))
            elif state:
                outcome.update(state=state, reason=str(ex))
            elif ex.code in MANUAL_ATTENTION:
                outcome.update(state='cooldown', reason=str(ex), until=None)
            else:
                outcome.update(state='cooldown', reason=str(ex), until=self.clock() + self.cfg.get('flowpool_cooldown_seconds', 900))
            return
        credits_after = self._read_after(driver, name, pool) if ex.code in DECLINED and driver else None
        partial = {x.get('id'): x for x in ex.partial or [] if x.get('files')}
        if partial:
            # Outputs captured before the failure are real results: keep them, never regenerate.
            done = [r for r in batch if r['id'] in partial]
            self._collect(done, list(partial.values()), name, credits_before, None, outcome)
        for req in batch:
            if req['id'] in partial:
                continue
            if ex.code in DECLINED:
                snap = self.journal.transition(req['_key'], 'failed', code=ex.code, error=str(ex), profile=name,
                                               credits_after=credits_after)
                self.ledger.submission(profile=name, kind=req['kind'], model=req['model'], request_id=req['id'],
                                       key=req['_key'], job=req.get('job'), scene=req.get('scene'), variants=req['variants'],
                                       credits_before=credits_before, credits_after=credits_after, batch_size=len(batch),
                                       status='declined', estimate=None)
                outcome['results'][req['id']] = result_of(req['id'], 'failed', snap)
            else:
                snap = self.journal.transition(req['_key'], 'unknown', code=ex.code, error=str(ex), profile=name)
                outcome['results'][req['id']] = result_of(req['id'], 'unknown', snap)
        if state == 'cooldown':
            outcome.update(state='cooldown', reason=ex.code, until=self.clock() + self.cfg.get('flowpool_cooldown_seconds', 900))
        elif state:
            outcome.update(state=state, reason=str(ex))
        elif ex.code not in DECLINED:
            # The profile's Flow queue may still hold the request: park it until reconciled.
            outcome.update(state='cooldown', reason=f'RECONCILE_REQUIRED: {ex}', until=None)

    # ------------------------------------------------------------------ doctor
    def doctor(self, names=None):
        report = []
        with file_lock(self.lock_path, blocking=False):
            pool = self.pool()
            pool.refresh()
            targets = [pool.get(n) for n in names] if names else pool.profiles
            if not targets:
                raise ValueError('NO_PROFILES: declare them in experiments/b2_illustrator/browser-profiles.json')
            open_names, daemon_error = self.located(pool)
            single_clip = self.clip_cost(self.cfg.get('veo_model'))
            for profile in targets:
                entry = {'profile': profile['name'], 'state_before': profile['state'], 'checks': {}}
                driver = None
                if profile['name'] not in open_names:
                    entry.update(error=(f'DAEMON {daemon_error}: python3 -m flowpool daemon start' if daemon_error else
                                        f'NO_TAB: python3 -m flowpool open-profile "{profile["name"]}"'),
                                 state_after=profile['state'])
                    report.append(entry)
                    continue
                try:
                    driver = self.driver_factory(copy.deepcopy(profile), self.cfg)
                    opened = driver.open() or {}
                    pool.record_email(profile['name'], opened.get('email'))
                    probe = driver.probe(['image', 'clip']) or {}
                    credits = (probe.get('credits') or {}).get('value')
                    entry['checks'] = dict(probe, account_verified=opened.get('account_verified'))
                    self.ledger.reading(profile['name'], credits, (probe.get('credits') or {}).get('raw'),
                                        (probe.get('credits') or {}).get('method'))
                    pool.record_credits(profile['name'], credits)
                    healthy = probe.get('logged_in') and probe.get('flow_reachable')
                    if healthy and profile['state'] != 'busy':
                        left = self.remaining(pool.get(profile['name']))
                        new = 'low_credit' if left < single_clip else 'ready'
                        pool.set_state(profile['name'], new, None if new == 'ready' else f'{left:.0f} credits left this month')
                except DriverError as ex:
                    entry['error'] = str(ex)
                    state = PROFILE_CODES.get(ex.code)
                    if state in STICKY:
                        pool.set_state(profile['name'], state, str(ex))
                finally:
                    if driver is not None:
                        pool.record_project(profile['name'], getattr(driver, 'project_url', None))
                        try:
                            driver.close()
                        except Exception:
                            pass
                entry['state_after'] = pool.get(profile['name'])['state']
                report.append(entry)
        return report

    # ------------------------------------------------------------------ status
    def status(self, locate=True):
        pool = self.pool()
        pool.refresh()
        model = self.cfg.get('veo_model')
        fallback = (self.cfg.get('flowpool_clip_credit_estimate') or {}).get(model, 0)
        per_clip, basis = self.ledger.cost_per_clip(model, fallback)
        open_names, daemon_error = self.located(pool) if locate else (set(), 'NOT_ASKED')
        spent, estimated = self.ledger.month_spend()
        budget = self.effective_budget(pool)
        rows = []
        for p in pool.profiles:
            left = self.remaining(p)
            rows.append({'profile': p['name'], 'account_email': p.get('account_email'), 'account_hint': p.get('account_hint'),
                         'state': p['state'], 'reason': p.get('state_reason'), 'credits': p.get('credits'),
                         'credits_at': p.get('credits_at'), 'monthly_cap': self.monthly_cap(p), 'month_used': self.month_used(p),
                         'month_remaining': left, 'clips_left_estimate': math.floor(left / per_clip) if per_clip else None,
                         'tab_open': p['name'] in open_names, 'tool_url': bool(p.get('tool_url')),
                         'project_url': p.get('project_url')})
        pool_left = max(0.0, budget - spent)
        clips_total = sum(r['clips_left_estimate'] or 0 for r in rows if r['state'] not in ('captcha', 'needs_login'))
        if per_clip:
            clips_total = min(clips_total, math.floor(pool_left / per_clip))
        counts = collections.Counter(s['state'] for s in self.journal.all())
        unresolved = [{'id': (s.get('identity') or {}).get('id'), 'key': s['key'][:12], 'state': s['state'],
                       'profile': s.get('profile'), 'code': s.get('code')}
                      for s in self.journal.all() if s['state'] in UNRESOLVED + ('failed',)]
        return {'profiles': rows, 'veo_model': model, 'credits_per_clip': per_clip, 'cost_basis': basis,
                'month': month_of(self.clock()), 'month_spent': spent, 'month_spent_includes_estimates': estimated,
                'credit_budget': budget, 'budget_left': pool_left, 'clips_left_total': clips_total,
                'video_generation': bool(self.cfg.get('video_generation')), 'daemon_error': daemon_error,
                'journal': dict(counts), 'attention': unresolved}

    # ------------------------------------------------------------------ human actions
    def reconcile(self, ref, note, release=False, files=None, media_ids=None):
        with file_lock(self.lock_path, blocking=False):
            matches = [s for s in self.journal.all() if s['key'].startswith(ref) or (s.get('identity') or {}).get('id') == ref]
            matches = [s for s in matches if s['state'] in UNRESOLVED + ('failed',)]
            if len(matches) != 1:
                raise ValueError(f'RECONCILE_TARGET: {len(matches)} unresolved/failed journals match {ref!r}')
            snap = matches[0]
            if snap['state'] == 'submitted':
                snap = self.journal.transition(snap['key'], 'unknown', reason='reconcile')
            if release:
                return self.journal.transition(snap['key'], 'released', note=note)
            if not files:
                raise ValueError('RECONCILE: pass --release or --files')
            from .journal import sha256_file
            outputs = [{'path': str(Path(f).resolve()), 'sha256': sha256_file(f),
                        'media_id': (media_ids or [None] * len(files))[i] if media_ids and i < len(media_ids) else None}
                       for i, f in enumerate(files)]
            if snap['state'] == 'failed':
                raise ValueError('RECONCILE: a failed request can only be released')
            return self.journal.transition(snap['key'], 'collected', outputs=outputs, reconciliation={'note': note},
                                           profile=snap.get('profile'))

    def mark(self, name, state, note):
        with file_lock(self.lock_path, blocking=False):
            pool = self.pool()
            return pool.set_state(name, state, f'manual: {note}')


def run(requests, cfg=None, driver_factory=None):
    """Section-8 API: flowpool.run(requests, cfg) -> list[result]."""
    return FlowPool(cfg, driver_factory).run(requests)
