"""image_pipeline <-> FlowPool integration with fakes: routing, clip lock, clip journal."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import image_pipeline as ip
from pilot import Blocked, ROOT, read, write
from flowpool import pipeline as fpp
from scripts.story_plan import image_units


class FakeP:
    def __init__(self, root, brief):
        self.root, self._brief, self.events = root, brief, []

    def brief(self, j):
        return (self._brief, 1, 'h') if self._brief is not None else None

    def job(self, j):
        return self.root / 'runs' / j

    def path(self, j, rel):
        return self.job(j) / rel

    def gate(self, j, m):
        pass

    def event(self, *a):
        self.events.append(a)


class PipelineCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'assets/characters/channel-mascot').mkdir(parents=True)
        Image.new('RGB', (64, 64)).save(self.root / fpp.MASCOT)
        self.cfg = dict(read(ROOT / 'config.json'), flowpool_enabled=True, video_generation=True, credit_budget=500,
                        flow_require_ui_evidence=False)
        write(self.root / 'config.json', self.cfg)
        self.p = FakeP(self.root, {'aspect_ratio': '16:9', 'clips': {'max': 2, 'model': 'veo-fast', 'variants': 2}})
        self.p.job('j').mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def set_cfg(self, **kw):
        write(self.root / 'config.json', dict(self.cfg, **kw))


class RoutingTests(PipelineCase):
    def test_flow_call_follows_flowpool_enabled(self):
        import adapters
        self.assertIs(ip.flow_call(self.p), fpp.gflow)
        self.set_cfg(flowpool_enabled=False)
        self.assertIs(ip.flow_call(self.p), adapters.gflow)

    def fake_run(self, status='ok', state='validated'):
        def run(p, requests):
            out = []
            for r in requests:
                Path(r['out_dir']).mkdir(parents=True, exist_ok=True)
                f = Path(r['out_dir']) / f"{r['id']}-1.jpg"
                Image.new('RGB', (1376, 768)).save(f)
                out.append({'id': r['id'], 'status': status, 'state': state, 'files': [str(f)] if status == 'ok' else [],
                            'media_ids': ['MID'], 'profile': 'Profile 13', 'error': None, 'code': None})
            self.requests = requests
            return out
        return run

    def test_image_request_writes_pipeline_evidence(self):
        out = self.p.job('j') / 'flow/attempts/k/download'
        with patch('flowpool.pipeline._run', side_effect=self.fake_run()):
            r = fpp.gflow(self.p, 'image', '--id', 'abc', '--prompt', 'P', '--ratio', '16:9', '--out', str(out),
                          '--character', 'j-CH01-x')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.requests[0]['refs'], [str(self.root / fpp.MASCOT)])
        self.assertEqual(self.requests[0]['job'], 'j')
        meta = read(out / 'abc-1.json')
        self.assertEqual((meta['jobId'], meta['characters'], meta['forgeId'], meta['source']),
                         ('abc', ['j-CH01-x'], 'MID', 'google-flow-browser'))
        proof = read(out.parent / 'ui-proof.json')
        self.assertEqual((proof['passed'], proof['mode'], proof['tool'], proof['profile']), (True, 'image', 'flowpool', 'Profile 13'))

    def test_outcomes_map_to_submission_flags(self):
        out = self.p.job('j') / 'o'
        args = ('image', '--id', 'abc', '--prompt', 'P', '--ratio', '16:9', '--out', str(out), '--character', 'n')
        with patch('flowpool.pipeline._run', side_effect=self.fake_run('unknown', 'unknown')):
            with self.assertRaises(Blocked) as cm:
                fpp.gflow(self.p, *args)
        self.assertTrue(cm.exception.generation_submitted)
        with patch('flowpool.pipeline._run', side_effect=self.fake_run('failed', 'not_submitted')):
            with self.assertRaises(Blocked) as cm:
                fpp.gflow(self.p, *args)
        self.assertFalse(cm.exception.generation_submitted)

    def test_local_mascot_and_registration_stay_on_adapters(self):
        with patch('adapters.gflow', return_value=subprocess.CompletedProcess([], 0, '', '')) as g, \
             patch('flowpool.pipeline._run') as run:
            fpp.gflow(self.p, 'image', '--id', 'x', '--prompt', 'p', '--out', str(self.root / 'o'))
            fpp.gflow(self.p, 'character', 'create', '--name', 'n', '--out', str(self.root / 'o'))
        self.assertEqual(g.call_count, 2)
        run.assert_not_called()

    def test_batch_writes_gflow_run_state(self):
        batch = self.p.job('j') / 'flow/batches/b'
        batch.mkdir(parents=True)
        write(batch / 'jobs.json', {'jobs': [{'id': 'a1', 'prompt': 'x', 'ratio': '16:9', 'character': ['n']},
                                             {'id': 'a2', 'prompt': 'y', 'ratio': '16:9', 'character': ['n']}]})
        def run(p, requests):
            ok = self.fake_run()(p, requests[:1])
            return ok + [{'id': 'a2', 'status': 'failed', 'state': 'not_submitted', 'files': [], 'error': 'NO_READY_PROFILE'}]
        with patch('flowpool.pipeline._run', side_effect=run):
            fpp.gflow(self.p, 'batch', str(batch / 'jobs.json'), '--out', str(batch))
        state = {e['id']: e for e in read(batch / 'gflow-run.json')['jobs']}
        self.assertEqual((state['a1']['status'], state['a2']['status']), ('completed', 'not_submitted'))
        self.assertTrue((batch / 'a1.jpg').is_file() and (batch / '.evidence/a1/ui-proof.json').is_file())
        self.assertEqual(read(batch / 'a1.json')['jobId'], 'a1')


class ClipLockTests(PipelineCase):
    def test_lock_lifted_only_for_briefs_with_clips(self):
        self.assertEqual(ip.preflight(self.p, 'j', 'image')['ui_evidence_required'], False)
        self.p._brief = {'aspect_ratio': '16:9'}
        with self.assertRaisesRegex(Blocked, 'M2_POLICY'):
            ip.preflight(self.p, 'j', 'image')
        self.set_cfg(video_generation=False, credit_budget=0)
        self.assertEqual(ip.preflight(self.p, 'j', 'image')['ui_evidence_required'], False)

    def test_clip_policy_needs_config_and_flowpool(self):
        self.assertEqual(ip.clip_policy(self.p, 'j')['max'], 2)
        self.set_cfg(credit_budget=0)
        with self.assertRaisesRegex(Blocked, 'credit_budget'):
            ip.clip_policy(self.p, 'j')
        self.set_cfg(flowpool_enabled=False)
        with self.assertRaisesRegex(Blocked, 'FlowPool'):
            ip.clip_policy(self.p, 'j')
        self.p._brief = {'aspect_ratio': '16:9'}
        with self.assertRaisesRegex(Blocked, 'declares no clips'):
            ip.clip_policy(self.p, 'j')


class ClipPlanTests(PipelineCase):
    content = {'schema_version': '3.0', 'style': 'doodle', 'characters': [{'id': 'CH01', 'appearance': 'a', 'outfit': 'o'}],
               'scenes': [{'id': 'SC01', 'images': [
                   {'id': 'SC01_I1', 'description': 'd', 'character_ids': ['CH01'], 'preserve': 'p', 'change': 'c',
                    'based_on': None, 'visible_text': []},
                   {'id': 'SC01_C1', 'kind': 'clip', 'from_image': 'SC01_I1', 'motion': 'slow push in'}]}]}

    def units(self):
        return [dict(u, id=u['id'] + '_16x9', image_id=u['id'], ratio='16:9',
                     **({'from_image': u['from_image'] + '_16x9'} if u.get('kind') == 'clip' else {}))
                for u in image_units(self.content)]

    def test_image_units_carry_clip_fields(self):
        units = image_units(self.content)
        clip = units[1]
        self.assertEqual((clip['kind'], clip['from_image'], clip['character_ids'], clip['visible_text']),
                         ('clip', 'SC01_I1', [], []))
        self.assertIn('Motion: slow push in', clip['prompt'])
        self.assertNotIn('kind', units[0])

    def test_clip_plan_enforces_max_and_source(self):
        self.assertEqual(ip.check_clip_plan(self.p, 'j', self.units())['max'], 2)
        self.p._brief['clips']['max'] = 0
        with self.assertRaisesRegex(Blocked, 'clips.max'):
            ip.check_clip_plan(self.p, 'j', self.units())
        self.p._brief['clips']['max'] = 2
        bad = self.units()
        bad[1]['from_image'] = 'SC09_I1_16x9'
        with self.assertRaisesRegex(Blocked, 'M2_CLIP_SOURCE'):
            ip.check_clip_plan(self.p, 'j', bad)
        self.assertIsNone(ip.check_clip_plan(self.p, 'j', self.units()[:1]))


class ClipRequestTests(PipelineCase):
    def setUp(self):
        super().setUp()
        still = self.p.job('j') / 'images/SC01_I1_16x9.png'
        still.parent.mkdir(parents=True)
        Image.new('RGB', (1376, 768)).save(still)
        from pilot import digest
        self.base = {'target': 'SC01_I1_16x9', 'path': 'images/SC01_I1_16x9.png', 'sha256': digest(still)}
        self.unit = {'id': 'SC01_C1_16x9', 'scene_id': 'SC01', 'kind': 'clip', 'prompt': 'push in', 'ratio': '16:9',
                     'from_image': 'SC01_I1_16x9', 'image_id': 'SC01_C1'}
        self.calls = []

    def fake_clip(self, status='ok'):
        def clip(p, request):
            self.calls.append(request)
            if status != 'ok':
                ex = Blocked('FlowPool unknown')
                ex.generation_submitted = True
                raise ex
            files = []
            for n in range(request['variants']):
                f = Path(request['out_dir']) / f"{request['id']}-{n + 1}.mp4"
                f.write_bytes(b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 32)
                files.append(str(f))
            return {'id': request['id'], 'status': 'ok', 'files': files, 'media_ids': ['A', 'B'], 'profile': 'Profile 13',
                    'credits_before': 500, 'credits_after': 460}
        return clip

    def test_clip_request_journals_and_reuses_download(self):
        with patch('scripts.image_repairs.active', return_value=''), \
             patch('flowpool.pipeline.clip', side_effect=self.fake_clip()):
            r = ip.clip_request(self.p, 'j', self.unit, self.base)
            again = ip.clip_request(self.p, 'j', self.unit, self.base)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(again['path'], r['path'])
        self.assertEqual((r['state'], len(r['variants']), r['profile']), ('downloaded', 2, 'Profile 13'))
        self.assertEqual(self.calls[0]['start_frame'], str(self.p.path('j', self.base['path'])))
        self.assertEqual((self.calls[0]['variants'], self.calls[0]['model']), (2, 'veo-fast'))
        folder = self.p.path('j', r['journal']).parent
        proof = read(folder / 'ui-proof.json')
        self.assertEqual((proof['mode'], proof['base_image']), ('clip', str(self.p.path('j', self.base['path']))))
        self.assertEqual(read(self.p.path('j', r['path']).with_suffix('.json'))['type'], 'video')
        self.assertEqual(ip.clip_check(self.p, 'j', r['path'], r['sha256']), r['path'])

    def test_unknown_clip_is_ambiguous_and_other_prompts_are_blocked(self):
        with patch('scripts.image_repairs.active', return_value=''), \
             patch('flowpool.pipeline.clip', side_effect=self.fake_clip('unknown')):
            with self.assertRaises(Blocked):
                ip.clip_request(self.p, 'j', self.unit, self.base)
            # Same identity goes back to FlowPool, whose journal refuses to resubmit.
            with self.assertRaises(Blocked):
                ip.clip_request(self.p, 'j', self.unit, self.base)
            with self.assertRaisesRegex(Blocked, 'M2_AMBIGUOUS'):
                ip.clip_request(self.p, 'j', dict(self.unit, prompt='other motion'), self.base)
        records = list((self.p.job('j') / 'flow/attempts').glob('*/request.json'))
        self.assertEqual([read(r)['state'] for r in records], ['ambiguous'])


class ProduceWithClipsTests(unittest.TestCase):
    """produce() + check() with a still and its clip, reusing the ImagesV2 fixture helpers."""

    def setUp(self):
        import test_images_v2 as iv
        self.iv = iv.ImagesV2Tests
        self.iv.setUp(self)
        cfg = read(self.root / 'config.json')
        cfg.update(flowpool_enabled=True, video_generation=True, credit_budget=500)
        write(self.root / 'config.json', cfg)
        # The fixture job's integrity baseline predates this config edit (test-only bypass).
        self.integrity = patch.object(type(self.p), 'integrity', lambda *a, **k: None)
        self.integrity.start()
        self.clip_calls = []

    def tearDown(self):
        self.integrity.stop()
        self.iv.tearDown(self)

    def preflight(self, **changes):
        return self.iv.preflight(self, **changes)

    def provider(self, p, *args, **kwargs):
        return self.iv.provider(self, p, *args, **kwargs)

    def approve(self, stage):
        return self.iv.approve(self, stage)

    def fake_clip(self, p, request):
        self.clip_calls.append(request)
        f = Path(request['out_dir']) / f"{request['id']}-1.mp4"
        f.write_bytes(b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 32)
        return {'id': request['id'], 'status': 'ok', 'files': [str(f)], 'media_ids': ['V1'], 'profile': 'Profile 13',
                'credits_before': 500, 'credits_after': 480}

    def test_clip_follows_its_still_and_passes_check(self):
        units = [{'id': 'SC01_I1_9x16', 'image_id': 'SC01_I1', 'scene_id': 'SC01', 'ratio': '9:16', 'based_on': None,
                  'prompt': 'still one', 'character_ids': [], 'visible_text': []},
                 {'id': 'SC01_C1_9x16', 'image_id': 'SC01_C1', 'scene_id': 'SC01', 'ratio': '9:16', 'kind': 'clip',
                  'from_image': 'SC01_I1_9x16', 'based_on': None, 'prompt': 'slow push in', 'character_ids': [],
                  'visible_text': []}]
        synthetic = {'schema_version': '3.0', 'characters': [], 'scenes': [{'id': 'SC01', 'images': [], 'beats': []}]}
        brief, rev, h = self.p.brief(self.j)
        clip_brief = (dict(brief, clips={'max': 1, 'model': 'veo-fast', 'variants': 1}), rev, h)
        with patch('image_pipeline.content', return_value=synthetic), \
             patch('image_pipeline.planned_units', return_value=units), \
             patch.object(self.p, 'brief', return_value=clip_brief), \
             patch('scripts.image_repairs.active', return_value=''), \
             patch('flowpool.pipeline.clip', side_effect=self.fake_clip):
            self.p.run(self.j, 'images')
            self.approve('references')
            out = self.p.job(self.j) / 'manual-final-out'
            out.mkdir()
            payload = ip.produce(self.p, self.j, out)
            # check() compares items against the plan: stills stay images, the clip is an MP4.
            files = ip.check(self.p, self.j, payload)
            broken = json.loads(json.dumps(payload))
            broken['items'][1]['path'] = payload['items'][0]['path']
            with self.assertRaisesRegex(Blocked, 'M2_CLIP'):
                ip.check(self.p, self.j, broken)
        self.assertEqual(len(self.clip_calls), 1)
        self.assertTrue(payload['items'][1]['path'].endswith('.mp4'))
        still = read(self.p.path(self.j, payload['items'][0]['request']))
        self.assertEqual(self.clip_calls[0]['start_frame'], str(self.p.path(self.j, still['path'])))
        self.assertIn(payload['items'][1]['path'], files)
        self.assertEqual(len(self.calls), 1)  # one still through the (patched) provider


if __name__ == '__main__':
    unittest.main()
