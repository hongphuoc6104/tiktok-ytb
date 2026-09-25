"""FlowPool offline tests: fake browser drivers only; nothing reaches Chrome or Flow."""
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from flowpool import FlowPool
from flowpool import scheduler
from flowpool.driver import Driver, DriverError
from flowpool.journal import Journal, JournalError, identity, key_for
from flowpool.ledger import Ledger
from flowpool.profiles import Pool, derive
from flowpool.store import read_ndjson

W, H = 1376, 768


class World:
    """Shared fake Flow: per-profile credits, scripted failures and a call log."""

    def __init__(self, journal_dir):
        self.credits = {}
        self.fail = {}          # (profile, op) -> DriverError
        self.log = []
        self.lock = threading.Lock()
        self.active = 0
        self.max_active = 0
        self.journal_dir = journal_dir
        self.probe = {}
        self.clip_cost = 20
        self.delay = 0.0


class FakeDriver(Driver):
    def __init__(self, world, profile, cfg):
        self.w, self.profile, self.cfg = world, profile, cfg
        self.name = profile['name']
        self.items = None
        self.kind = None

    def _maybe_fail(self, op):
        err = self.w.fail.get((self.name, op))
        if err:
            raise err

    def open(self):
        self.w.log.append(('open', self.name))
        self._maybe_fail('open')
        return {'binding': {'target_id': 'T-' + self.profile['slug'], 'browser_context_id': 'C-' + self.profile['slug']},
                'account_verified': True}

    def probe(self, kinds):
        self._maybe_fail('probe')
        return self.w.probe.get(self.name, {'logged_in': True, 'flow_reachable': True, 'image_tool': True,
                                            'image_model_selectable': True, 'clip_model_selectable': True,
                                            'credits': {'value': self.w.credits.get(self.name), 'method': 'fake'}})

    def read_credits(self):
        return {'value': self.w.credits.get(self.name), 'method': 'fake'}

    def prepare(self, kind, items):
        self._maybe_fail('prepare')
        self.kind, self.items = kind, items
        self.w.log.append(('prepare', self.name, [i['id'] for i in items]))
        return [f'Q-{i["id"]}' for i in items]

    def commit(self, timeout):
        # Invariant under test: every request is durably `submitted` before commit.
        j = Journal(self.w.journal_dir)
        for it in self.items:
            snaps = j.by_request_id(it['id'])
            assert any(s['state'] == 'submitted' for s in snaps), f'{it["id"]} committed before journal submitted'
        with self.w.lock:
            self.w.active += 1
            self.w.max_active = max(self.w.max_active, self.w.active)
        try:
            self.w.log.append(('commit', self.name, [i['id'] for i in self.items]))
            if self.w.delay:
                time.sleep(self.w.delay)
            self._maybe_fail('commit')
            out = []
            for it in self.items:
                Path(it['out_dir']).mkdir(parents=True, exist_ok=True)
                files = []
                if self.kind == 'image':
                    size = (W, H) if it['ratio'] == '16:9' else (H, W)
                    f = Path(it['out_dir']) / f'{it["id"]}-1.jpg'
                    Image.new('RGB', size, (10, 20, 30)).save(f)
                    files.append(str(f))
                else:
                    for n in range(it['variants']):
                        f = Path(it['out_dir']) / f'{it["id"]}-{n + 1}.mp4'
                        f.write_bytes(b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 64)
                        files.append(str(f))
                    if self.w.credits.get(self.name) is not None:
                        self.w.credits[self.name] -= self.w.clip_cost * it['variants']
                out.append({'id': it['id'], 'files': files, 'media_ids': [f'M-{it["id"]}-{k}' for k in range(len(files))]})
            return out
        finally:
            with self.w.lock:
                self.w.active -= 1


def profile(name, prio, tool=True, media=None, udd='/fake/udd', state='ready', credits=None):
    return {'name': name, 'slug': name.lower().replace(' ', '-'), 'user_data_dir': udd, 'profile_directory': name,
            'enabled': True, 'priority': prio, 'max_parallel': 4, 'tool_url': f'https://flow.test/{prio}' if tool else None,
            'project': 'Video Pilot', 'project_url': None, 'media_ids': media or {}, 'state': state,
            'state_reason': None, 'state_since': 0, 'cooldown_until': None, 'credits': credits, 'credits_at': None,
            'binding': None, 'account_hint': None}


class FlowPoolCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ref = self.dir / 'mascot.png'
        Image.new('RGB', (64, 64), 'white').save(self.ref)
        self.still = self.dir / 'still.png'
        Image.new('RGB', (W, H), 'blue').save(self.still)
        from flowpool.journal import sha256_file
        self.ref_sha = sha256_file(self.ref)
        self.state = self.dir / 'state'
        self.state.mkdir()
        self.world = World(self.state / 'journal')
        self.cfg = {'flowpool_state_dir': str(self.state), 'flowpool_max_browsers': 2, 'video_generation': True,
                    'credit_budget': 1000, 'flow_model': 'Nano Banana 2', 'veo_model': 'veo-fast'}
        self.which = patch('flowpool.validate.shutil.which', return_value=None)
        self.which.start()

    def tearDown(self):
        self.which.stop()
        self.tmp.cleanup()

    def write_profiles(self, *profiles):
        (self.state / 'profiles.json').write_text(json.dumps({'schema_version': 1, 'profiles': list(profiles)}))

    def pool(self, **cfg):
        return FlowPool(dict(self.cfg, **cfg), lambda p, c: FakeDriver(self.world, p, c))

    def image(self, i, **kw):
        return dict({'id': f'img{i}', 'kind': 'image', 'prompt': f'scene {i}', 'ratio': '16:9',
                     'refs': [str(self.ref)], 'job': 'job1', 'scene': f'S{i}'}, **kw)

    def clip(self, i, **kw):
        return dict({'id': f'clip{i}', 'kind': 'clip', 'prompt': f'camera push {i}', 'ratio': '16:9',
                     'start_frame': str(self.still), 'variants': 2, 'model': 'veo-fast', 'job': 'job1',
                     'scene': f'S{i}'}, **kw)

    def two_image_profiles(self, **kw):
        media = {self.ref_sha: 'MASCOT'}
        self.write_profiles(profile('Profile 10', 0, media=media, **kw), profile('Profile 13', 1, media=media, **kw),
                            profile('Profile 14', 2, tool=False))

    def commits(self):
        return [e for e in self.world.log if e[0] == 'commit']


class SchedulerTests(FlowPoolCase):
    def test_images_round_robin_across_ready_profiles(self):
        self.two_image_profiles()
        results = self.pool().run([self.image(i) for i in range(8)])
        self.assertEqual([r['status'] for r in results], ['ok'] * 8)
        by_profile = {c[1]: c[2] for c in self.commits()}
        self.assertEqual(set(by_profile), {'Profile 10', 'Profile 13'})
        self.assertEqual(sorted(len(v) for v in by_profile.values()), [4, 4])
        self.assertTrue(all(Path(r['files'][0]).is_file() for r in results))

    def test_batches_spread_evenly_and_respect_queue_cap(self):
        media = {self.ref_sha: 'M'}
        self.write_profiles(*[profile(f'Profile {n}', i, media=media) for i, n in enumerate((10, 13, 14))])
        self.pool(flowpool_max_browsers=3).run([self.image(i) for i in range(5)])
        self.assertEqual(sorted(len(c[2]) for c in self.commits()), [1, 2, 2])
        self.world.log.clear()
        self.pool(flowpool_max_browsers=1).run([self.image(i) for i in range(10, 20)])
        self.assertTrue(all(len(c[2]) <= 4 for c in self.commits()))

    def test_clip_goes_to_profile_with_most_credits(self):
        self.write_profiles(profile('Profile 10', 0, credits=100), profile('Profile 13', 1, credits=500),
                            profile('Profile 14', 2, credits=300))
        self.world.credits = {'Profile 10': 100, 'Profile 13': 500, 'Profile 14': 300}
        [r] = self.pool().run([self.clip(1)])
        self.assertEqual((r['status'], r['profile']), ('ok', 'Profile 13'))
        self.assertEqual((r['credits_before'], r['credits_after']), (500, 460))
        self.assertEqual(len(r['files']), 2)
        entry = [e for e in read_ndjson(self.state / 'ledger.ndjson') if e['type'] == 'submission'][0]
        self.assertEqual((entry['profile'], entry['kind'], entry['model'], entry['job'], entry['scene'], entry['delta']),
                         ('Profile 13', 'clip', 'veo-fast', 'job1', 'S1', 40))

    def test_unknown_balance_ranks_last_for_clips(self):
        ctx = scheduler.Context({'flowpool_clip_credit_estimate': {'veo-fast': 20}})
        ps = [profile('A', 0, credits=None), profile('B', 1, credits=50)]
        req = {'id': 'c', 'kind': 'clip', 'model': 'veo-fast', 'variants': 1}
        self.assertEqual(scheduler.next_batch([req], ps, ctx)[0]['name'], 'B')
        ps[1]['credits'] = 10  # below one clip: ineligible, unknown balance is still tried
        self.assertEqual(scheduler.next_batch([req], ps, ctx)[0]['name'], 'A')

    def test_image_without_media_id_on_profile_is_not_routed_there(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}), profile('Profile 13', 1))
        results = self.pool().run([self.image(i) for i in range(3)])
        self.assertEqual({r['profile'] for r in results}, {'Profile 10'})

    def test_no_eligible_profile_fails_without_submission(self):
        self.write_profiles(profile('Profile 13', 1))
        [r] = self.pool().run([self.image(1)])
        self.assertEqual((r['status'], r['code'], r['state']), ('failed', 'NO_ELIGIBLE_PROFILE', 'not_submitted'))
        self.assertEqual(self.commits(), [])

    def test_concurrency_limited_by_max_browsers(self):
        media = {self.ref_sha: 'M'}
        self.write_profiles(*[profile(f'Profile {n}', i, media=media) for i, n in enumerate((10, 13, 14))])
        self.world.delay = 0.05
        self.pool(flowpool_max_browsers=2).run([self.image(i) for i in range(12)])
        self.assertEqual(self.world.max_active, 2)
        self.world.max_active = 0
        self.pool(flowpool_max_browsers=3, flowpool_serialize_user_data_dir=True).run([self.image(i) for i in range(20, 32)])
        self.assertEqual(self.world.max_active, 1)

    def test_dependent_image_follows_profile_that_owns_base_media(self):
        self.two_image_profiles()
        [base] = self.pool().run([self.image(1)])
        owner = base['profile']
        dep = self.image(2, refs=[str(self.ref), base['files'][0]])
        [r] = self.pool().run([dep])
        self.assertEqual((r['status'], r['profile']), ('ok', owner))


class SafetyTests(FlowPoolCase):
    def test_captcha_profile_leaves_rotation_and_work_moves(self):
        self.two_image_profiles()
        self.world.fail[('Profile 10', 'open')] = DriverError('CAPTCHA', 'challenge shown')
        results = self.pool().run([self.image(i) for i in range(4)])
        self.assertEqual({r['status'] for r in results}, {'ok'})
        self.assertEqual({r['profile'] for r in results}, {'Profile 13'})
        pool = Pool(self.state / 'profiles.json')
        self.assertEqual(pool.get('Profile 10')['state'], 'captcha')
        # Sticky: the next run never opens it again.
        self.world.log.clear()
        self.pool().run([self.image(9)])
        self.assertNotIn(('open', 'Profile 10'), self.world.log)

    def test_needs_login_is_sticky_until_doctor_sees_clean_page(self):
        self.two_image_profiles()
        self.world.fail[('Profile 13', 'prepare')] = DriverError('NEEDS_LOGIN', 'signed out')
        self.pool().run([self.image(i) for i in range(8)])
        self.assertEqual(Pool(self.state / 'profiles.json').get('Profile 13')['state'], 'needs_login')
        del self.world.fail[('Profile 13', 'prepare')]
        report = self.pool().doctor(['Profile 13'])
        self.assertEqual(report[0]['state_after'], 'ready')

    def test_doctor_is_read_only_and_marks_captcha(self):
        self.two_image_profiles()
        self.world.credits = {'Profile 10': 900}
        self.world.fail[('Profile 13', 'open')] = DriverError('CAPTCHA', 'x')
        report = {r['profile']: r for r in self.pool().doctor()}
        self.assertEqual(report['Profile 10']['checks']['credits']['value'], 900)
        self.assertEqual(report['Profile 13']['state_after'], 'captcha')
        self.assertFalse([e for e in self.world.log if e[0] in ('prepare', 'commit')])

    def test_restart_never_resubmits_interrupted_submission(self):
        self.two_image_profiles()
        req = self.image(1)
        from flowpool.pool import normalize_request
        norm = normalize_request(req, self.cfg, self.state / 'out')
        ident = identity(norm)
        j = Journal(self.state / 'journal')
        j.intent(norm, ident)
        j.transition(key_for(ident), 'submitted', profile='Profile 10')   # crash right after this line
        for _ in range(2):
            [r] = self.pool().run([req])
            self.assertEqual((r['status'], r['code']), ('unknown', 'RECONCILE_REQUIRED'))
        self.assertEqual(self.commits(), [])
        self.assertEqual(j.load(key_for(ident))['events'][-1].get('reason'), 'interrupted-submission')

    def test_timeout_after_commit_is_unknown_and_parks_profile(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.fail[('Profile 10', 'commit')] = DriverError('TIMEOUT', 'no result', submitted=True)
        [r] = self.pool().run([self.image(1)])
        self.assertEqual(r['status'], 'unknown')
        p = Pool(self.state / 'profiles.json').get('Profile 10')
        self.assertEqual((p['state'], p['cooldown_until']), ('cooldown', None))
        self.assertIn('RECONCILE_REQUIRED', p['state_reason'])
        del self.world.fail[('Profile 10', 'commit')]
        self.pool().mark('Profile 10', 'ready', 'checked Flow UI')
        n = len(self.commits())
        [r] = self.pool().run([self.image(1)])
        self.assertEqual(r['status'], 'unknown')
        self.assertEqual(len(self.commits()), n)

    def test_changed_request_cannot_hide_unknown_attempt(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.fail[('Profile 10', 'commit')] = DriverError('RECONCILE_REQUIRED', 'queue vanished', submitted=True)
        self.pool().run([self.image(1)])
        del self.world.fail[('Profile 10', 'commit')]
        self.pool().mark('Profile 10', 'ready', 'checked')
        [r] = self.pool().run([self.image(1, prompt='a different prompt')])
        self.assertEqual((r['status'], r['code']), ('unknown', 'RECONCILE_REQUIRED'))

    def test_partial_results_before_failure_are_kept(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        out = self.state / 'partial'
        out.mkdir()
        f = out / 'img1-1.jpg'
        Image.new('RGB', (W, H)).save(f)
        self.world.fail[('Profile 10', 'commit')] = DriverError(
            'CAPTCHA', 'challenge mid-queue', submitted=True,
            partial=[{'id': 'img1', 'files': [str(f)], 'media_ids': ['M1']}, {'id': 'img2', 'files': []}])
        res = {r['id']: r for r in self.pool().run([self.image(1), self.image(2)])}
        self.assertEqual((res['img1']['status'], res['img2']['status']), ('ok', 'unknown'))
        self.assertEqual(Pool(self.state / 'profiles.json').get('Profile 10')['state'], 'captcha')

    def test_prepare_failure_retries_on_another_profile(self):
        self.two_image_profiles()
        self.world.fail[('Profile 10', 'prepare')] = DriverError('UNRESOLVED_FLOW_QUEUE', 'queued items left')
        results = self.pool(flowpool_max_browsers=1).run([self.image(i) for i in range(2)])
        self.assertEqual({(r['status'], r['profile']) for r in results}, {('ok', 'Profile 13')})
        p = Pool(self.state / 'profiles.json').get('Profile 10')
        self.assertEqual((p['state'], p['cooldown_until']), ('cooldown', None))

    def test_explicit_refusal_is_terminal_until_released(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.fail[('Profile 10', 'commit')] = DriverError('POLICY_BLOCKED', 'blocked', submitted=True)
        [r] = self.pool().run([self.image(1)])
        self.assertEqual((r['status'], r['code']), ('failed', 'POLICY_BLOCKED'))
        self.assertEqual(Pool(self.state / 'profiles.json').get('Profile 10')['state'], 'ready')
        del self.world.fail[('Profile 10', 'commit')]
        n = len(self.commits())
        self.assertEqual(self.pool().run([self.image(1)])[0]['status'], 'failed')
        self.assertEqual(len(self.commits()), n)
        self.pool().reconcile('img1', 'rewrote nothing; user accepts a retry', release=True)
        self.assertEqual(self.pool().run([self.image(1)])[0]['status'], 'ok')

    def test_reconcile_unknown_with_files_then_validate(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.fail[('Profile 10', 'commit')] = DriverError('TIMEOUT', 'x', submitted=True)
        self.pool().run([self.image(1)])
        f = self.dir / 'found.jpg'
        Image.new('RGB', (W, H)).save(f)
        with self.assertRaises(ValueError):
            self.pool().reconcile('img1', 'no evidence given')
        self.pool().reconcile('img1', 'matched mediaId in Flow UI', files=[str(f)], media_ids=['M9'])
        [r] = self.pool().run([self.image(1)])
        self.assertEqual((r['status'], r['files']), ('ok', [str(f.resolve())]))

    def test_validated_results_are_reused_without_browser(self):
        self.two_image_profiles()
        self.pool().run([self.image(1)])
        self.world.log.clear()
        [r] = self.pool().run([self.image(1)])
        self.assertEqual(r['status'], 'ok')
        self.assertEqual(self.world.log, [])

    def test_bad_output_is_failed_not_regenerated(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.fail[('Profile 10', 'commit')] = DriverError('TIMEOUT', 'x', submitted=True)
        self.pool().run([self.image(1)])
        bad = self.dir / 'bad.jpg'
        bad.write_bytes(b'garbage')
        self.pool().reconcile('img1', 'file found in Flow UI', files=[str(bad)])
        del self.world.fail[('Profile 10', 'commit')]
        self.pool().mark('Profile 10', 'ready', 'checked')
        n = len(self.commits())
        [r] = self.pool().run([self.image(1)])
        self.assertEqual((r['status'], r['code']), ('failed', 'VALIDATION_FAILED'))
        self.assertEqual(len(self.commits()), n)

    def test_parallel_runs_are_excluded(self):
        self.two_image_profiles()
        from flowpool.store import file_lock
        with file_lock(self.state / 'run.lock'):
            with self.assertRaises(RuntimeError):
                self.pool().run([self.image(1)])


class ClipPolicyTests(FlowPoolCase):
    def setUp(self):
        super().setUp()
        self.write_profiles(profile('Profile 10', 0, credits=1000))
        self.world.credits = {'Profile 10': 1000}

    def test_clips_disabled_or_zero_budget(self):
        [r] = self.pool(video_generation=False).run([self.clip(1)])
        self.assertEqual((r['code'], r['state']), ('CLIP_DISABLED', 'not_submitted'))
        [r] = self.pool(credit_budget=0).run([self.clip(1)])
        self.assertEqual(r['code'], 'CREDIT_BUDGET_ZERO')
        self.assertEqual(self.commits(), [])

    def test_monthly_budget_counts_ledger_spend(self):
        results = self.pool(credit_budget=100).run([self.clip(i) for i in range(4)])
        # each clip = 2 variants x 20 credits; 100 allows two
        self.assertEqual([r['status'] for r in results], ['ok', 'ok', 'failed', 'failed'])
        self.assertEqual(results[2]['code'], 'CREDIT_BUDGET_EXCEEDED')
        self.assertEqual(len(self.commits()), 2)

    def test_low_credit_profile_skips_clips_keeps_images(self):
        self.write_profiles(profile('Profile 10', 0, credits=1000, media={self.ref_sha: 'M'}))
        self.world.credits = {'Profile 10': 30}
        [r] = self.pool().run([self.clip(1)])
        self.assertEqual(r['status'], 'failed')
        self.assertEqual(Pool(self.state / 'profiles.json').get('Profile 10')['state'], 'low_credit')
        self.assertEqual(self.pool().run([self.image(1)])[0]['status'], 'ok')

    def test_clip_requires_start_frame_and_measured_cost_updates_estimate(self):
        [r] = self.pool().run([self.clip(1, start_frame=None)])
        self.assertEqual(r['code'], 'START_FRAME_REQUIRED')
        self.world.clip_cost = 30
        self.pool().run([self.clip(2)])
        s = self.pool().status()
        self.assertEqual((s['credits_per_clip'], s['cost_basis']), (30, 'measured'))
        row = s['profiles'][0]
        self.assertEqual((row['credits'], row['clips_left_estimate']), (940, 31))
        self.assertEqual(s['month_spent'], 60)


class JournalLedgerProfileTests(FlowPoolCase):
    def test_journal_transitions(self):
        j = Journal(self.state / 'j')
        req = {'id': 'a', 'kind': 'image', 'prompt': 'p', 'ratio': '16:9', 'refs': [str(self.ref)], 'variants': 1}
        snap = j.intent(req)
        key = snap['key']
        with self.assertRaises(JournalError):
            j.transition(key, 'collected')
        j.transition(key, 'submitted')
        j.transition(key, 'unknown')
        with self.assertRaises(JournalError) as cm:
            j.transition(key, 'collected', outputs=[])
        self.assertEqual(cm.exception.code, 'EVIDENCE_REQUIRED')
        with self.assertRaises(JournalError):
            j.intent(req)
        # A torn trailing line from a crash is ignored, earlier lines are kept.
        with open(self.state / 'j' / f'{key}.ndjson', 'a') as f:
            f.write('{"state": "valid')
        self.assertEqual(j.load(key)['state'], 'unknown')

    def test_ledger_balances_and_month_spend(self):
        led = Ledger(self.state / 'l.ndjson')
        led.reading('A', 1000)
        led.submission(profile='A', kind='clip', model='veo-fast', request_id='c', key='k', job='j', scene='s',
                       variants=2, credits_before=1000, credits_after=960, batch_size=1, status='ok')
        led.submission(profile='B', kind='clip', model='veo-fast', request_id='d', key='k2', job='j', scene='s',
                       variants=1, credits_before=None, credits_after=None, batch_size=1, status='ok', estimate=20)
        self.assertEqual(led.balances()['A'][0], 960)
        self.assertEqual(led.month_spend(), (60.0, True))
        self.assertEqual(led.cost_per_clip('veo-fast', 99), (20.0, 'measured'))

    def test_derive_profiles_from_b2_config(self):
        udd = self.dir / 'chrome'
        for d in ('Default', 'Profile 10', 'Profile 13', 'Profile 99', 'Crashpad'):
            (udd / d).mkdir(parents=True)
        (udd / 'Local State').write_text(json.dumps({'profile': {'info_cache': {
            'Profile 13': {'name': 'Kênh 2', 'user_name': 'second@example.com'}}}}))
        src = self.dir / 'browser-profiles.json'
        src.write_text(json.dumps({'executable_path': '/opt/google/chrome/google-chrome', 'flow_user_data_dir': str(udd),
                                   'flow_profile_directory': 'Profile 10', 'priority': ['Profile 10', 'Profile 13']}))
        data = derive(src, self.dir / 'missing.json', {'flow_project': 'Video Pilot'})
        names = [p['name'] for p in data['profiles']]
        self.assertEqual(names, ['Profile 10', 'Profile 13', 'Default', 'Profile 99'])
        self.assertEqual([p['enabled'] for p in data['profiles']], [True, True, False, False])
        self.assertEqual(data['profiles'][1]['account_hint'], 'second@example.com')
        self.assertTrue(all(p['state'] == 'ready' and p['user_data_dir'] == str(udd) for p in data['profiles']))
        self.assertFalse(data['automatic_account_switching'])

    def test_profile_state_machine(self):
        self.write_profiles(profile('P', 0), profile('Q', 1, state='cooldown'))
        pool = Pool(self.state / 'profiles.json')
        pool.acquire('P')
        self.assertEqual(pool.get('P')['state'], 'busy')
        with self.assertRaises(RuntimeError):
            pool.acquire('P')
        pool.release('P', 'captcha', 'challenge')
        with self.assertRaises(RuntimeError):
            pool.acquire('P')
        pool.set_state('Q', 'cooldown', 'rate', until=time.time() - 1)
        pool.refresh()
        self.assertEqual(pool.get('Q')['state'], 'ready')
        # A busy marker left by a dead process is recovered on load.
        pool.acquire('Q')
        pool.get('Q')['busy_pid'] = 999999999
        pool.save()
        self.assertEqual(Pool(self.state / 'profiles.json').get('Q')['state'], 'ready')

    def test_status_reports_balances_and_attention(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        self.world.credits = {'Profile 10': 1000}
        self.world.fail[('Profile 10', 'commit')] = DriverError('TIMEOUT', 'x', submitted=True)
        self.pool().run([self.image(1)])
        s = self.pool().status()
        self.assertEqual(s['profiles'][0]['credits'], 1000)
        self.assertEqual(s['profiles'][0]['clips_left_estimate'], 50)
        self.assertEqual(s['attention'][0]['state'], 'unknown')

    def test_invalid_requests_fail_without_touching_the_pool(self):
        self.write_profiles(profile('Profile 10', 0, media={self.ref_sha: 'M'}))
        bad = [{'id': 'x y', 'kind': 'image'}, self.image(1, variants=2), self.image(2, refs=[]),
               self.image(3, ratio='1:1'), {'id': 'dup', 'kind': 'video'}]
        results = self.pool().run(bad)
        self.assertEqual({r['status'] for r in results}, {'failed'})
        self.assertEqual(self.world.log, [])


if __name__ == '__main__':
    unittest.main()
