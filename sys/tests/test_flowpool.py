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
        self.engines = []
        self.daemon_error = None
        self.stopped = set()   # profiles without an open tab in the shared Chrome


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
        return {'account_verified': None, 'email': f"{self.profile['slug']}@example.com"}

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
        self.project_url = f'https://flow.test/project/{self.profile["slug"]}-0001'
        self.w.log.append(('prepare', self.name, [i['id'] for i in items]))
        self.w.engines.append((self.name, [i['engine'] for i in items]))
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
                    for n in range(it.get('variants') or 1):
                        f = Path(it['out_dir']) / f'{it["id"]}-{n + 1}.jpg'
                        Image.new('RGB', size, (10 + 40 * n, 20, 30)).save(f)
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


def profile(name, prio, tool=True, media=None, state='ready', credits=None, **extra):
    return dict({'name': name, 'slug': name.lower().replace(' ', '-'), 'user_data_dir': '/fake/google-chrome',
            'profile_directory': name, 'enabled': True, 'priority': prio, 'max_parallel': 4,
            'tool_url': f'https://flow.test/{prio}' if tool else None,
            'project': 'Video Pilot', 'project_url': None, 'media_ids': media or {}, 'state': state,
            'state_reason': None, 'state_since': 0, 'cooldown_until': None, 'credits': credits,
            'credits_at': time.time() if credits is not None else None,
            'binding': None, 'account_email': None, 'account_hint': None}, **extra)


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
        self.cfg = {'flowpool_state_dir': str(self.state), 'flowpool_max_parallel': 2, 'video_generation': True,
                    'flowpool_browser_profiles': None,
                    'credit_budget': 1000, 'flow_model': 'Nano Banana 2', 'veo_model': 'veo-fast'}
        self.which = patch('flowpool.validate.shutil.which', return_value=None)
        self.which.start()

    def tearDown(self):
        self.which.stop()
        self.tmp.cleanup()

    def write_profiles(self, *profiles):
        (self.state / 'profiles.json').write_text(json.dumps({'schema_version': 1, 'profiles': list(profiles)}))

    def pool(self, **cfg):
        return FlowPool(dict(self.cfg, **cfg), lambda p, c: FakeDriver(self.world, p, c), locate=self.locate)

    def locate(self, profiles, dedupe=False):
        if self.world.daemon_error:
            return {}, self.world.daemon_error
        return {p['name']: {'target_id': 'T-' + p['slug'], 'via': 'target'} for p in profiles
                if p['name'] not in self.world.stopped}, None

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
        self.pool(flowpool_max_parallel=3).run([self.image(i) for i in range(5)])
        self.assertEqual(sorted(len(c[2]) for c in self.commits()), [1, 2, 2])
        self.world.log.clear()
        self.pool(flowpool_max_parallel=1).run([self.image(i) for i in range(10, 20)])
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

    def test_new_accounts_without_remix_use_plain_flow_one_per_submission(self):
        self.write_profiles(profile('acc1', 0, tool=False), profile('acc2', 1, tool=False))
        results = self.pool().run([self.image(i) for i in range(4)])
        self.assertEqual({r['status'] for r in results}, {'ok'})
        self.assertEqual({r['profile'] for r in results}, {'acc1', 'acc2'})
        self.assertTrue(all(len(c[2]) == 1 for c in self.commits()))
        self.assertEqual({e for _, es in self.world.engines for e in es}, {'flow'})

    def test_engine_choice(self):
        ctx = scheduler.Context({})
        req = {'kind': 'image', '_ref_shas': [self.ref_sha]}
        self.assertEqual(scheduler.engine(profile('a', 0, media={self.ref_sha: 'M'}), req, ctx), 'b2')
        self.assertEqual(scheduler.engine(profile('a', 0), req, ctx), 'flow')       # remix but no media id
        self.assertEqual(scheduler.engine(profile('a', 0, tool=False), req, ctx), 'flow')
        self.assertEqual(scheduler.engine(profile('a', 0), {'kind': 'clip'}, ctx), 'clip')

    def test_only_profiles_with_an_open_tab_take_work(self):
        self.two_image_profiles()
        self.world.stopped = {'Profile 10', 'Profile 13', 'Profile 14'}
        [r] = self.pool().run([self.image(1)])
        self.assertEqual((r['status'], r['code'], r['state']), ('failed', 'NO_ELIGIBLE_PROFILE', 'not_submitted'))
        self.assertIn('no_tab', r['error'])
        self.assertEqual(self.commits(), [])
        self.world.stopped = {'Profile 10'}
        self.assertEqual(self.pool().run([self.image(2)])[0]['profile'], 'Profile 13')

    def test_project_url_and_binding_are_recorded_per_profile(self):
        self.write_profiles(profile('acc1', 0, tool=False))
        self.pool().run([self.image(1)])
        rec = Pool(self.state / 'profiles.json').get('acc1')
        self.assertEqual(rec['project_url'], 'https://flow.test/project/acc1-0001')
        self.assertEqual(rec['binding'], {'target_id': 'T-acc1'})
        self.assertEqual(rec['account_email'], 'acc1@example.com')

    def test_concurrency_limited_by_max_browsers(self):
        media = {self.ref_sha: 'M'}
        self.write_profiles(*[profile(f'Profile {n}', i, media=media) for i, n in enumerate((10, 13, 14))])
        self.world.delay = 0.05
        self.pool(flowpool_max_parallel=2).run([self.image(i) for i in range(12)])
        self.assertEqual(self.world.max_active, 2)

    def test_dependent_image_follows_profile_that_owns_base_media(self):
        self.two_image_profiles()
        [base] = self.pool().run([self.image(1)])
        owner = base['profile']
        dep = self.image(2, refs=[str(self.ref), base['files'][0]])
        [r] = self.pool(flowpool_max_parallel=1).run([dep])
        self.assertEqual(r['status'], 'ok')
        # Only the owner knows the base image's media ID, so only there can the B-2 queue take it.
        self.assertEqual(self.world.engines[-1][1], ['b2' if r['profile'] == owner else 'flow'])


class SafetyTests(FlowPoolCase):
    def test_captcha_profile_leaves_rotation_and_work_moves(self):
        self.two_image_profiles()
        self.world.fail[('Profile 10', 'open')] = DriverError('CAPTCHA', 'challenge shown')
        results = self.pool().run([self.image(i) for i in range(4)])
        self.assertEqual({r['status'] for r in results}, {'ok'})
        self.assertNotIn('Profile 10', {r['profile'] for r in results})
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
        results = self.pool(flowpool_max_parallel=1).run([self.image(i) for i in range(2)])
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

    def test_derive_uses_only_declared_profiles_and_syncs_new_ones(self):
        udd = self.dir / 'chrome'
        for d in ('Default', 'Profile 10', 'Profile 13', 'Profile 99'):
            (udd / d).mkdir(parents=True)
        (udd / 'Local State').write_text(json.dumps({'profile': {'info_cache': {
            'Profile 13': {'name': 'Kênh 2', 'user_name': 'second@example.com'}}}}))
        src = self.dir / 'browser-profiles.json'
        declared = {'executable_path': '/opt/google/chrome/google-chrome', 'flow_user_data_dir': str(udd),
                    'flow_profile_directory': 'Profile 10', 'priority': ['Profile 10', 'Profile 13']}
        src.write_text(json.dumps(declared))
        data = derive(src, self.dir / 'missing.json', {'flow_project': 'Video Pilot'})
        self.assertEqual([p['name'] for p in data['profiles']], ['Profile 10', 'Profile 13'])
        self.assertEqual(data['profiles'][1]['account_hint'], 'second@example.com')
        self.assertTrue(all(p['user_data_dir'] == str(udd) and p['enabled'] for p in data['profiles']))
        pool = Pool(self.state / 'profiles.json', declared=src)
        pool.set_state('Profile 13', 'captcha', 'x')
        declared['priority'].append('Profile 99')          # the user declares one more profile
        src.write_text(json.dumps(declared))
        pool = Pool(self.state / 'profiles.json', declared=src)
        self.assertEqual([p['name'] for p in pool.profiles], ['Profile 10', 'Profile 13', 'Profile 99'])
        self.assertEqual(pool.get('Profile 13')['state'], 'captcha')      # existing state kept
        self.assertEqual(pool.get('Profile 99')['priority'], 2)

    def test_separate_instance_pool_format_is_refused(self):
        (self.state / 'profiles.json').write_text(json.dumps({'schema_version': 2, 'mode': 'instances', 'profiles': []}))
        with self.assertRaisesRegex(RuntimeError, 'OLD_POOL_FORMAT'):
            Pool(self.state / 'profiles.json')

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
        bad = [{'id': 'x y', 'kind': 'image'}, self.image(1, variants=5), self.image(2, refs=[]),
               self.image(3, ratio='1:1'), {'id': 'dup', 'kind': 'video'}]
        results = self.pool().run(bad)
        self.assertEqual({r['status'] for r in results}, {'failed'})
        self.assertEqual(self.world.log, [])






class CreditTests(FlowPoolCase):
    """Per-profile monthly caps (1050 each by default) and the pool budget."""

    def spend(self, profile, delta, at=None):
        Ledger(self.state / 'ledger.ndjson').submission(
            profile=profile, kind='image', model='veo-fast', request_id='x', key='k', job='j', scene='s', variants=1,
            credits_before=1000, credits_after=1000 - delta, batch_size=1, status='ok', at=at)

    def test_remaining_is_cap_minus_month_spend_lowered_by_ui_balance(self):
        self.write_profiles(profile('A', 0), profile('B', 1, credits=100), profile('C', 2, monthly_credits=300))
        self.spend('A', 50)
        self.spend('A', 400, at=time.time() - 40 * 86400)   # last month: does not count
        fp = self.pool(flowpool_profile_monthly_credits=1050)
        pool = fp.pool()
        self.assertEqual(fp.remaining(pool.get('A')), 1000)
        self.assertEqual(fp.remaining(pool.get('B')), 100)          # UI balance read this month is lower
        self.assertEqual(fp.remaining(pool.get('C')), 300)          # per-profile override
        stale = dict(pool.get('B'), credits_at=time.time() - 40 * 86400)
        self.assertEqual(fp.remaining(stale), 1050)                 # last month's balance is ignored
        self.assertEqual(fp.effective_budget(pool), 1000)           # credit_budget (1000) < 1050+1050+300
        self.assertEqual(self.pool(credit_budget=99999).effective_budget(pool), 2400)

    def test_clip_never_goes_to_a_profile_below_clip_cost(self):
        self.write_profiles(profile('A', 0, monthly_credits=30), profile('B', 1, monthly_credits=500))
        self.world.credits = {'A': 1000, 'B': 1000}
        results = self.pool().run([self.clip(1), self.clip(2)])
        self.assertEqual({r['profile'] for r in results}, {'B'})    # A: 30 left < 40 per clip (2 variants)
        self.write_profiles(profile('A', 0, monthly_credits=30))
        [r] = self.pool().run([self.clip(3)])
        self.assertEqual((r['status'], r['code']), ('failed', 'NO_ELIGIBLE_PROFILE'))
        self.assertIn('insufficient_credits', r['error'])

    def test_status_shows_month_usage_and_total_clips(self):
        self.write_profiles(profile('A', 0), profile('B', 1))
        self.spend('A', 200)
        s = self.pool(credit_budget=4200).status()
        rows = {r['profile']: r for r in s['profiles']}
        self.assertEqual((rows['A']['month_used'], rows['A']['month_remaining'], rows['A']['clips_left_estimate']), (200, 850, 42))
        self.assertEqual((rows['B']['monthly_cap'], rows['B']['clips_left_estimate']), (1050, 52))
        self.assertEqual((s['credit_budget'], s['budget_left'], s['clips_left_total']), (2100, 1900, 94))


class DaemonTests(FlowPoolCase):
    """The single-connection daemon seen from Python: socket client, driver, open-profile."""

    def serve(self, replies):
        import socket as so
        path = str(self.dir / 'd.sock')
        srv = so.socket(so.AF_UNIX, so.SOCK_STREAM)
        srv.bind(path)
        srv.listen(8)
        self.seen = []

        def loop():
            while True:
                try:
                    c, _ = srv.accept()
                except OSError:
                    return
                data = b''
                while not data.endswith(b'\n'):
                    chunk = c.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                msg = json.loads(data)
                self.seen.append(msg)
                reply = replies(msg) if callable(replies) else replies
                if reply is not None:
                    c.sendall((json.dumps(reply) + '\n').encode())
                c.close()
        threading.Thread(target=loop, daemon=True).start()
        self.addCleanup(srv.close)
        return path

    def test_client_reports_missing_daemon_and_timeouts(self):
        from flowpool.daemon_client import DaemonClient, DaemonError
        c = DaemonClient({'flowpool_daemon_socket': str(self.dir / 'none.sock')})
        with self.assertRaises(DaemonError) as cm:
            c.call('status')
        self.assertEqual(cm.exception.code, 'NO_DAEMON')
        self.assertEqual(c.status()['code'], 'NO_DAEMON')
        path = self.serve(lambda m: None if m['op'] == 'commit' else {'ok': True, 'connected': True})
        c = DaemonClient({'flowpool_daemon_socket': path})
        self.assertTrue(c.status()['connected'])
        with self.assertRaises(DaemonError) as cm:
            c.call('commit', timeout=0.3)
        self.assertEqual(cm.exception.code, 'WORKER_DIED')

    def test_driver_maps_replies_and_marks_lost_commit_as_submitted(self):
        from flowpool.driver import DaemonDriver
        from flowpool.daemon_client import DaemonClient
        def reply(m):
            if m['op'] == 'open':
                return {'ok': True, 'email': 'a@x.com', 'project_url': 'https://flow.google.com/project/abcd1234'}
            if m['op'] == 'prepare':
                return {'ok': False, 'code': 'CAPTCHA', 'error': 'challenge', 'submitted': False}
            if m['op'] == 'commit':
                return None   # connection dropped mid-commit
            return {'ok': True}
        path = self.serve(reply)
        d = DaemonDriver(profile('Profile 10', 0, _secret='x'), {'flowpool_daemon_socket': path},
                         DaemonClient({'flowpool_daemon_socket': path}))
        self.assertEqual(d.open()['email'], 'a@x.com')
        self.assertEqual(d.project_url, 'https://flow.google.com/project/abcd1234')
        self.assertNotIn('_secret', self.seen[0]['profile'])
        with self.assertRaises(DriverError) as cm:
            d.prepare('image', [])
        self.assertEqual((cm.exception.code, cm.exception.submitted), ('CAPTCHA', False))
        with self.assertRaises(DriverError) as cm:
            d.commit(1)
        self.assertTrue(cm.exception.submitted)

    def test_lost_daemon_stops_the_run_without_parking_profiles(self):
        self.two_image_profiles()
        self.world.fail[('Profile 10', 'open')] = DriverError('NEEDS_ALLOW', 'connection lost')
        self.world.fail[('Profile 13', 'open')] = DriverError('NEEDS_ALLOW', 'connection lost')
        self.world.fail[('Profile 14', 'open')] = DriverError('NEEDS_ALLOW', 'connection lost')
        results = self.pool(flowpool_max_parallel=1).run([self.image(i) for i in range(3)])
        self.assertEqual({r['code'] for r in results}, {'NEEDS_ALLOW'})
        self.assertEqual({r['state'] for r in results}, {'not_submitted'})
        self.assertEqual({p['state'] for p in Pool(self.state / 'profiles.json').profiles}, {'ready'})
        self.world.daemon_error = 'NO_DAEMON'
        [r] = self.pool().run([self.image(9)])
        self.assertIn('daemon NO_DAEMON', r['error'])

    def test_doctor_reports_profiles_without_tab(self):
        self.two_image_profiles()
        self.world.stopped = {'Profile 13'}
        report = {r['profile']: r for r in self.pool().doctor()}
        self.assertIn('open-profile', report['Profile 13']['error'])
        self.assertNotIn(('open', 'Profile 13'), self.world.log)
        self.assertEqual(report['Profile 10']['state_after'], 'ready')

    def test_open_profile_uses_existing_profile_and_waits_for_the_tab(self):
        from flowpool.__main__ import open_profile
        self.write_profiles(profile('Profile 13', 0))
        calls, polls = [], []
        def locate(profiles, dedupe=False):
            polls.append(dedupe)
            return ({'Profile 13': {'target_id': 'T9', 'url': 'https://flow.google.com/#flowpool=profile-13', 'via': 'marker',
                                    'closed': 1}} if len(polls) >= 3 else {}), None
        fp = FlowPool(dict(self.cfg, flowpool_chrome='/opt/google/chrome/google-chrome'), locate=locate)
        r = open_profile(fp, 'Profile 13', wait=5, popen=lambda a, **k: calls.append(a), sleep=lambda s: None)
        self.assertEqual((r['status'], r['closed']), ('bound', 1))
        args = calls[0]
        self.assertIn('--profile-directory=Profile 13', args)
        self.assertEqual(args[-1], 'https://flow.google.com/#flowpool=profile-13')
        self.assertFalse([a for a in args if a.startswith('--remote-debugging') or 'automation' in a])
        self.assertEqual(polls, [True, True, True])
        self.assertEqual(Pool(self.state / 'profiles.json').get('Profile 13')['binding'], {'target_id': 'T9'})
        fp2 = FlowPool(dict(self.cfg), locate=lambda ps, d=False: ({}, 'NEEDS_ALLOW'))
        with self.assertRaisesRegex(RuntimeError, 'NEEDS_ALLOW'):
            open_profile(fp2, 'Profile 13', wait=5, popen=lambda a, **k: None, sleep=lambda s: None)


class RankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def doodle(self, name, size=(1376, 768), text=False, blank=False):
        from PIL import ImageDraw
        img = Image.new('RGB', size, (245, 238, 220))
        d = ImageDraw.Draw(img)
        if not blank:
            d.ellipse((600, 200, 760, 360), outline=(20, 20, 20), width=6)
            d.line((680, 360, 680, 560), fill=(20, 20, 20), width=6)
            d.line((680, 420, 600, 500), fill=(20, 20, 20), width=6)
            d.rectangle((150, 520, 420, 700), fill=(140, 110, 80))
        if text:
            for row in range(3):
                for col in range(60):
                    x, y = 100 + col * 20, 60 + row * 30
                    d.rectangle((x, y, x + 3, y + 16), fill=(0, 0, 0))
                    d.rectangle((x + 8, y, x + 11, y + 16), fill=(0, 0, 0))
                    d.line((x, y, x + 11, y + 16), fill=(0, 0, 0), width=2)
        p = self.dir / name
        img.save(p)
        return p

    def test_defects_rank_below_a_clean_doodle(self):
        from flowpool.rank import rank
        clean = self.doodle('clean.png')
        texty = self.doodle('text.png', text=True)
        blank = self.doodle('blank.png', blank=True)
        wrong = self.doodle('portrait.png', size=(768, 1376))
        order = [Path(r['path']).name for r in rank([texty, blank, wrong, clean], '16:9')]
        self.assertEqual(order[0], 'clean.png')
        scores = {Path(r['path']).name: r for r in rank([texty, blank, wrong, clean], '16:9')}
        self.assertGreater(scores['text.png']['checks']['text_likeness'], scores['clean.png']['checks']['text_likeness'])
        self.assertLess(scores['blank.png']['score'], 0)
        self.assertLess(scores['portrait.png']['score'], scores['clean.png']['score'])

    def test_reference_similarity_breaks_ties(self):
        from flowpool.rank import rank
        ref = self.doodle('ref.png')
        same = self.doodle('same.png')
        other = self.dir / 'other.png'
        from PIL import ImageDraw
        img = Image.new('RGB', (1376, 768), (245, 238, 220))
        ImageDraw.Draw(img).rectangle((900, 50, 1300, 700), fill=(60, 60, 60))
        img.save(other)
        ranked = rank([other, same], '16:9', [ref])
        self.assertEqual(Path(ranked[0]['path']).name, 'same.png')
        self.assertEqual(ranked[0]['checks']['reference_similarity'], [1.0])

    def test_pool_records_ranking_and_best(self):
        case = FlowPoolCase('run')
        case.setUp()
        try:
            case.write_profiles(profile('acc1', 0, tool=False))
            [r] = case.pool().run([case.image(1, variants=2)])
            self.assertEqual((r['status'], len(r['files'])), ('ok', 2))
            self.assertEqual(r['best'], r['files'][0])
            self.assertEqual(r['ranking'][0]['path'], r['best'])
        finally:
            case.tearDown()


class DecisionsDashboardTests(FlowPoolCase):
    def produce(self):
        self.write_profiles(profile('acc1', 0, tool=False, project_url='https://flow.google.com/project/abcd1234'))
        [r] = self.pool().run([self.clip(1, target='SC01_C1_16x9')])
        return r

    def test_ui_state_lists_profiles_queue_and_gallery(self):
        from flowpool.dashboard import ui_state
        r = self.produce()
        self.world.fail[('acc1', 'commit')] = DriverError('TIMEOUT', 'x', submitted=True)
        self.pool().run([self.clip(2)])
        state = ui_state(self.pool())
        self.assertEqual(state['status']['profiles'][0]['profile'], 'acc1')
        self.assertIn('RECONCILE_REQUIRED', state['status']['profiles'][0]['reason'])
        self.assertIn('reconcile', state['status']['profiles'][0]['action'])
        labels = {q['id']: q['label'] for q in state['queue']}
        self.assertEqual((labels['clip1'], labels['clip2']), ('đã kiểm tra', 'chưa rõ kết quả'))
        [g] = state['gallery']
        self.assertEqual((g['id'], g['kind'], g['open_in_flow'], len(g['variants'])), ('clip1', 'clip', 'https://flow.test/project/acc1-0001', 2))
        self.assertEqual(sum(v['best'] for v in g['variants']), 1)
        self.assertEqual(g['variants'][0]['path'], r['files'][0])

    def test_pick_and_regenerate_decisions(self):
        from flowpool.dashboard import decide, ui_state
        from flowpool.decisions import Decisions
        r = self.produce()
        with self.assertRaisesRegex(ValueError, 'DECISION_INDEX'):
            decide(self.pool(), 'pick', r['key'][:12], 7)
        out = decide(self.pool(), 'pick', r['key'][:12], 1)
        self.assertEqual(out['decision']['file'], r['files'][1])
        d = Decisions(self.state / 'decisions.ndjson')
        self.assertEqual(d.choose(r), (r['files'][1], 'user_pick'))
        self.assertEqual(d.choose(dict(r, id='other', key='other')), (r['best'], 'ranked'))
        out = decide(self.pool(), 'regenerate', r['key'], note='mặt nhân vật rõ hơn')
        self.assertEqual(out['next'], 'python3 pilot.py reject job1 media --image SC01_C1 --ratio 16:9 --note "mặt nhân vật rõ hơn"')
        [g] = ui_state(self.pool())['gallery']
        self.assertTrue(g['variants'][1]['picked'] and g['regenerate_requested'])
        with self.assertRaises(ValueError):
            d.record('approve', 'k', 'id')


class PromptTests(unittest.TestCase):
    def test_image_prompt_has_style_identity_scene_and_negatives(self):
        from flowpool import prompts
        from pilot import ROOT
        style = prompts.channel_style(ROOT, 'tiensu')
        self.assertIn('stick-figure doodle', style)
        mascot = {'appearance': {'hair': 'messy dark-brown hair', 'accent': 'bone necklace'}}
        text = prompts.image_prompt('A hunter waits by the river.', '16:9', style, mascot, has_base=True)
        for part in ('stick-figure doodle', 'Bold clean outlines', 'Wide 16:9', 'bone necklace', 'base scene',
                     'A hunter waits by the river.', 'Do not draw any text'):
            self.assertIn(part, text)
        self.assertIsNone(prompts.channel_style(ROOT, None))
        self.assertNotIn('Style:', prompts.image_prompt('x', '9:16'))

    def test_clip_prompt_is_short_motion_with_locked_style(self):
        from flowpool import prompts
        text = prompts.clip_prompt('slow push-in,  character blinks and turns head, embers drift', 8)
        self.assertTrue(text.startswith('8-second shot'))
        self.assertIn('Motion: slow push-in, character blinks and turns head, embers drift', text)
        self.assertIn('no new characters, no text', text)


if __name__ == '__main__':
    unittest.main()
