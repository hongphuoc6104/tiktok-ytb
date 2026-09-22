"""I01–I14: isolated fixtures, fake Flow. Never production acceptance."""
import copy
import json
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from pilot import ROOT, Pilot, Blocked, read, write, digest
import image_pipeline as ip
import prompt_templates as pt


class ImagesV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.root = Path(self.tmp.name)
        for n in ['schemas','.agents','renderer','tests','examples','scripts']:
            shutil.copytree(ROOT/n,self.root/n)
        for n in ['pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','content_contract.py','adapters.py','config.json','AGENTS.md','GEMINI.md']:
            shutil.copy(ROOT/n,self.root/n)
        cfg = read(self.root / 'config.json')
        cfg.pop('flow_batch', None)
        cfg['flow_require_ui_evidence'] = True  # Legacy strict-policy fixture; independent of deployment defaults.
        write(self.root / 'config.json', cfg)
        self.p = Pilot(self.root);self.j = 'images-test'
        self.p.new(self.j,read(ROOT/'examples/m1/brief.json'))
        self.p.approve(self.j,'control',1,'TEST FIXTURE')
        d = read(ROOT/'examples/m1/content.json');_,r,h = self.p.brief(self.j)
        d.update(brief_revision=r,brief_hash=h);write(self.p.job(self.j)/'draft/content.json',d)
        self.p.run(self.j,'content');self.p.approve(self.j,'content',1,'TEST FIXTURE')
        self.preflight()
        self.calls=[];self.mock=patch('adapters.gflow',side_effect=self.provider);self.mock.start()

    def tearDown(self):
        self.mock.stop();self.p.db.close();self.tmp.cleanup()

    def preflight(self,**changes):
        base=self.p.job(self.j)/'flow';base.mkdir(exist_ok=True)
        Image.new('RGB',(30,30)).save(base/'preflight.png')
        model_name = read(self.root / 'config.json')['flow_model']
        e=dict(observed_at=time.time(),mode='image',credits_per_generation=0,model=model_name,profile='video-pilot',project='Video Pilot',
               observer='TEST',account_confirmed=True,operations=['image','character-register'],
               screenshot='flow/preflight.png',screenshot_hash=digest(base/'preflight.png'))
        e.update(changes);write(base/'preflight.json',e)

    def provider(self,p,*args,**kwargs):
        self.calls.append(args)
        folder=Path(args[args.index('--out')+1]);registration=args[0]=='character'
        # Different prompts/ref names yield different fake images; deterministic on retry.
        import hashlib
        rgb=tuple(hashlib.sha256(' '.join(args).encode()).digest()[:3])
        Image.new('RGB',(720,1280),rgb).save(folder/'result.png')
        chars=list(args[args.index('--character')+1:]) if '--character' in args else []
        if not registration:
            write(folder/'result.json',{'jobId':args[args.index('--id')+1],'type':'image','prompt':args[args.index('--prompt')+1],
                  'ratio':'9:16','characters':chars,'source':'google-flow-browser','status':'downloaded'})
        write(folder.parent/'ui-proof.json',{'passed':True,'mode':'character-register' if registration else 'image','characters':chars})
        Image.new('RGB',(30,30)).save(folder.parent/'before-submit.png')
        return SimpleNamespace(returncode=0,stdout='TEST PROVIDER',stderr='')

    def run_stage(self):
        # Registration comparison is explicit TEST evidence, never real human approval.
        for _ in range(20):
            try:
                self.p.run(self.j,'images');return
            except Blocked as ex:
                if 'M2_REGISTRATION_REVIEW' not in str(ex):raise
                for q in (self.p.job(self.j)/'flow/attempts').glob('*/request.json'):
                    r=read(q);reg=r['identity']['registration']
                    if reg and not (q.parent/'confirmation.json').exists():
                        e={'name':reg['name'],'matches_approved_reference':True,'observer':'TEST','note':'TEST ONLY match',
                           'screenshot':str(self.p.job(self.j)/'flow/preflight.png')}
                        write(self.root/'confirm.json',e)
                        ip.flow_action(self.p,SimpleNamespace(job=self.j,command='flow-confirm-registration',request=r['key'],evidence=str(self.root/'confirm.json')))
        self.fail('too many registration checks')

    def approve(self,stage):
        self.p.approve(self.j,'images',self.p.rows(self.j)['images']['revision'],'TEST FIXTURE human approval',stage)

    def references(self):self.run_stage();self.approve('references')
    def finish(self):self.references();self.run_stage();self.approve('final')

    def test_I01_content_gate(self):
        self.p.reject(self.j,'content','TEST requested edit')
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        self.assertEqual(self.calls,[])

    def test_I02_preflight(self):
        for changes in [dict(observed_at=time.time()-601),dict(mode='video'),dict(account_confirmed=False),dict(operations=[])]:
            self.preflight(**changes)
            with self.assertRaisesRegex(Blocked,'M2_PREFLIGHT'):self.p.run(self.j,'images')
        self.assertEqual(self.calls,[])

    def _preflight_evidence_dict(self):
        model_name = read(self.root / 'config.json')['flow_model']
        return dict(observed_at=time.time(), mode='image', credits_per_generation=0, model=model_name,
                    profile='video-pilot', project='Video Pilot', observer='TEST', account_confirmed=True,
                    operations=['image', 'character-register'], screenshot='flow/preflight.png')

    def _preflight_evidence_file(self, drop=(), **overrides):
        """A --evidence JSON file plus real screenshot, for the WRITE path
        (adapters.flow_action/image_pipeline.record_preflight), as opposed to
        self.preflight() which writes flow/preflight.json directly and is
        used for the READ path (image_pipeline.preflight)."""
        shot = self.root / 'observed.png'
        Image.new('RGB', (30, 30)).save(shot)
        e = self._preflight_evidence_dict()
        e['screenshot'] = str(shot)
        e.update(overrides)
        for k in drop:
            e.pop(k, None)
        path = self.root / 'evidence.json'
        write(path, e)
        return path

    def test_flow_preflight_write_rejects_missing_project(self):
        # adapters.flow_action's flow-preflight now shares image_pipeline's
        # read-side check, so a write missing a field the reader requires
        # (project) must be refused immediately, naming the field, instead
        # of succeeding and only failing later with a bare M2_PREFLIGHT at
        # image-generation time.
        import adapters
        before = read(self.p.job(self.j) / 'flow/preflight.json')
        evidence = self._preflight_evidence_file(drop=['project'])
        with self.assertRaisesRegex(Blocked, 'project'):
            adapters.flow_action(self.p, SimpleNamespace(job=self.j, command='flow-preflight', evidence=str(evidence)))
        # The bad write must never overwrite the previously recorded evidence.
        self.assertEqual(read(self.p.job(self.j) / 'flow/preflight.json'), before)
        self.assertEqual(self.calls, [])

    def test_flow_preflight_write_rejects_missing_operations(self):
        import adapters
        before = read(self.p.job(self.j) / 'flow/preflight.json')
        evidence = self._preflight_evidence_file(drop=['operations'])
        with self.assertRaisesRegex(Blocked, 'operations'):
            adapters.flow_action(self.p, SimpleNamespace(job=self.j, command='flow-preflight', evidence=str(evidence)))
        self.assertEqual(read(self.p.job(self.j) / 'flow/preflight.json'), before)
        self.assertEqual(self.calls, [])

    def test_flow_preflight_write_full_evidence_then_produce(self):
        # Regression check: writing through the real flow-preflight command
        # (not the test fixture's direct file write) with complete evidence
        # must still succeed and image production must run exactly as before.
        import adapters
        evidence = self._preflight_evidence_file()
        result = adapters.flow_action(self.p, SimpleNamespace(job=self.j, command='flow-preflight', evidence=str(evidence)))
        self.assertIn('recorded', result['preflight'])
        self.finish()
        self.assertTrue(self.p.validate(self.j, 'images')['passed'])

    def test_preflight_default_window_600_seconds(self):
        # config.json declares no preflight_window_seconds; the default must
        # stay exactly 600s so this never silently loosens a job that hasn't
        # opted in.
        cfg = read(self.root / 'config.json')
        self.assertNotIn('preflight_window_seconds', cfg)
        fresh = dict(self._preflight_evidence_dict(), observed_at=time.time() - 599)
        ip.validate_preflight_evidence(cfg, fresh)  # must not raise
        stale = dict(self._preflight_evidence_dict(), observed_at=time.time() - 601)
        with self.assertRaisesRegex(Blocked, 'M2_PREFLIGHT_EXPIRED'):
            ip.validate_preflight_evidence(cfg, stale)

    def test_preflight_expiry_mid_run_stops_cleanly(self):
        # A dual/long production run can easily outlast one 10-minute
        # observation window. Expiry mid-run must stop cleanly between two
        # images (never resubmit, never leave a dangling 'submitted'
        # journal) and explain itself as expected, not a bug.
        self.references()
        count = {'n': 0}
        def flaky(p, *args, **kw):
            count['n'] += 1
            result = self.provider(p, *args, **kw)
            if count['n'] == 3:  # right after the first scene image (2 char registrations precede it)
                pf = self.p.job(self.j) / 'flow/preflight.json'
                e = read(pf); e['observed_at'] = time.time() - 700; write(pf, e)
            return result
        self.mock.stop()
        try:
            with patch('adapters.gflow', side_effect=flaky):
                with self.assertRaisesRegex(Blocked, 'M2_PREFLIGHT_EXPIRED') as ctx:
                    self.run_stage()
            msg = str(ctx.exception)
            self.assertIn('already downloaded and kept', msg)
            self.assertIn('1/6', msg)
        finally:
            self.mock.start()

        journals = [read(q) for q in (self.p.job(self.j) / 'flow/attempts').glob('*/request.json')]
        states = [r['state'] for r in journals]
        self.assertNotIn('submitted', states, 'no request may be left mid-flight after a clean stop')
        self.assertNotIn('ambiguous', states, 'expiry must never be recorded as an uncertain Flow outcome')
        downloaded_before = {r['identity']['target']: r['sha256'] for r in journals if r['state'] == 'downloaded'
                              and not r['identity']['target'].startswith(('ref:', 'register:'))}
        self.assertEqual(set(downloaded_before), {'SC01'})

        # Resuming with fresh evidence only submits what's left; nothing
        # already downloaded is touched or resent.
        self.preflight()
        self.run_stage()
        self.approve('final')
        for target, sha in downloaded_before.items():
            after = self._journal_for(target)
            self.assertEqual(after['sha256'], sha)
        self.assertTrue(self.p.validate(self.j, 'images')['passed'])

    def test_I03_video_and_provider(self):
        import adapters
        with self.assertRaisesRegex(Blocked,'disabled'):adapters.request_video()
        prompt = pt.batch_prompt('text-to-video',['x'])
        self.assertIn('x', prompt)
        cfg=read(self.root/'config.json');cfg['credit_budget']=-1;write(self.root/'config.json',cfg)
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        self.assertEqual(self.calls,[])

    def test_I04_reference_gate(self):
        with self.assertRaisesRegex(Blocked,'REFERENCES'):ip.request(self.p,self.j,'SC01','x')
        self.assertEqual(self.calls,[])

    def test_I05_checkpoint_gates(self):
        self.run_stage();n=len(self.calls)
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        with self.assertRaises(Blocked):self.approve('final')
        self.assertEqual(len(self.calls),n)
        self.approve('references')
        with self.assertRaises(Blocked):ip.request(self.p,self.j,'SC04','x')
        self.run_stage();n=len(self.calls)
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        # Audio no longer depends on images, so an unreviewed checkpoint is proven
        # by images staying unapproved, not by a downstream module being blocked.
        self.assertNotEqual(self.p.rows(self.j)['images']['state'],'approved')
        self.assertEqual(len(self.calls),n)

    def test_I06_bad_assets(self):
        self.references();self.run_stage();d=self.p.payload(self.j,'images')
        for change in ['missing','duplicate','escape','broken','small','ratio']:
            bad=copy.deepcopy(d)
            if change=='missing':bad['items'].pop()
            elif change=='duplicate':bad['items'][1]=bad['items'][0]
            elif change=='escape':bad['items'][0]['path']='../../outside.png'
            else:
                f=self.p.job(self.j)/'invalid.png'
                if change=='broken':f.write_text('bad')
                else:Image.new('RGB',(360,640) if change=='small' else (1280,720)).save(f)
                bad['items'][0].update(path='invalid.png',sha256=digest(f))
            with self.subTest(change=change),self.assertRaises(Exception):self.p.checks(self.j,'images',bad)

    def test_I07_prompt_and_links(self):
        self.references();self.run_stage();d=self.p.payload(self.j,'images')
        for mutate in ['prompt','hash','reference','actual']:
            bad=copy.deepcopy(d)
            if mutate=='prompt':bad['items'][0]['prompt']='different'
            elif mutate=='hash':bad['content_hash']='0'*64
            elif mutate=='actual':bad['items'][0]['actual_prompt']='not sent'
            else:bad['items'][0]['references']=[]
            with self.subTest(mutate=mutate),self.assertRaises(Blocked):self.p.checks(self.j,'images',bad)

    def test_I08_timeout_reconcile(self):
        with patch('adapters.gflow',side_effect=TimeoutError('accepted then timeout')) as call:
            for _ in range(2):
                with self.assertRaises(Blocked):self.p.run(self.j,'images')
            self.assertEqual(call.call_count,1)
        q=next((self.p.job(self.j)/'flow/attempts').glob('*/request.json'));r=read(q)
        self.assertEqual(r['state'],'ambiguous')
        # Missing visual evidence cannot reconcile an uncertain result.
        with self.assertRaises(Blocked):
            ip.flow_action(self.p,SimpleNamespace(job=self.j,command='flow-reconcile',request=r['key'],asset=None,note='TEST',evidence=None))

    def test_I08_reconcile_verified_download(self):
        def lost_after_download(p,*args,**kw):
            self.provider(p,*args,**kw)
            raise TimeoutError('lost after download')
        with patch('adapters.gflow',side_effect=lost_after_download):
            with self.assertRaises(Blocked):self.p.run(self.j,'images')
        q=next((self.p.job(self.j)/'flow/attempts').glob('*/request.json'));r=read(q)
        evidence={'request':r['key'],'mode':'image','characters':[], 'actual_prompt':r['identity']['actual_prompt'],
                  'matched_download':True,'observer':'TEST', 'screenshot':str(q.parent/'before-submit.png')}
        write(self.root/'reconcile.json',evidence)
        ip.flow_action(self.p,SimpleNamespace(job=self.j,command='flow-reconcile',request=r['key'],asset=str(q.parent/'download/result.png'),
                       note='TEST verified result',evidence=str(self.root/'reconcile.json')))
        n=len(self.calls);self.run_stage()
        self.assertEqual(len(self.calls)-n,len(self.p.payload(self.j,'content')['characters'])-1)
        self.assertTrue(self.p.validate(self.j,'images')['passed'])

    def test_registration_timeout_no_duplicate(self):
        self.references()
        with patch('adapters.gflow',side_effect=TimeoutError('registration accepted')) as call:
            for _ in range(2):
                with self.assertRaises(Blocked):self.p.run(self.j,'images')
            self.assertEqual(call.call_count,1)

    def test_first_scene_edit_reuses_other_scenes(self):
        self.finish();n=len(self.calls)
        self.p.reject(self.j,'images','TEST edit SC01',self.p.rows(self.j)['images']['revision'],'final',scene='SC01')
        self.assertEqual(ip.stage(self.p,self.j),'final')
        self.run_stage()
        self.assertEqual(len(self.calls)-n,1)
        self.assertEqual(self.p.payload(self.j,'images')['checkpoint'],'final')

    def _journal_for(self, target):
        for q in (self.p.job(self.j) / 'flow/attempts').glob('*/request.json'):
            r = read(q)
            if r['identity']['target'] == target:
                return r
        return None

    def test_content_edit_elsewhere_reuses_unaffected_journal(self):
        # A narration edit anywhere in the script used to bump every per-image
        # identity (content_hash was part of it), forcing a full re-send to Flow
        # for images that never changed. It must now be reused from cache.
        self.finish()
        n = len(self.calls)
        sc01_before = self._journal_for('SC01')
        self.assertEqual(sc01_before['state'], 'downloaded')
        old_content_hash = self.p.rows(self.j)['content']['hash']

        self.p.reject(self.j, 'content', 'TEST edit SC05 narration')
        draft = read(self.p.job(self.j) / 'draft/content.json')
        draft['scenes'][4]['narration'] += ' Cảm ơn bạn đã lắng nghe.'
        write(self.p.job(self.j) / 'draft/content.json', draft)
        self.p.run(self.j, 'content')
        self.p.approve(self.j, 'content', self.p.rows(self.j)['content']['revision'], 'TEST FIXTURE narration edit')
        self.assertNotEqual(self.p.rows(self.j)['content']['hash'], old_content_hash)
        self.assertEqual(self.p.rows(self.j)['images']['state'], 'stale')

        self.finish()
        self.assertEqual(len(self.calls), n, 'no new Flow submissions expected for unaffected scenes')
        sc01_after = self._journal_for('SC01')
        self.assertEqual(sc01_after['key'], sc01_before['key'])
        self.assertEqual(sc01_after['state'], 'downloaded')
        self.assertEqual(sc01_after['path'], sc01_before['path'])
        self.assertTrue(self.p.validate(self.j, 'images')['passed'])

    def test_ratio_major_grouping_and_based_on_order(self):
        # Synthetic dual-ratio plan: 2 scenes x 2 chained images x 2 ratios,
        # fed straight into produce() via patched content()/planned_units()
        # so this stays independent of the concurrently-evolving v3
        # content/brief schemas. Proves: (1) gflow_guard's global aspect
        # ratio/model toggle is only flipped once per ratio -- every 9:16
        # image submits before any 16:9 image -- and (2) a based_on chain
        # inside one scene stays strictly sequential within each ratio.
        units = [
            {'id': 'SC01_I1_9x16', 'scene_id': 'SC01', 'ratio': '9:16', 'based_on': None,
             'prompt': 'SC01 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC01_I1_16x9', 'scene_id': 'SC01', 'ratio': '16:9', 'based_on': None,
             'prompt': 'SC01 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC01_I2_9x16', 'scene_id': 'SC01', 'ratio': '9:16', 'based_on': 'SC01_I1_9x16',
             'prompt': 'SC01 image 2', 'character_ids': [], 'visible_text': []},
            {'id': 'SC01_I2_16x9', 'scene_id': 'SC01', 'ratio': '16:9', 'based_on': 'SC01_I1_16x9',
             'prompt': 'SC01 image 2', 'character_ids': [], 'visible_text': []},
            {'id': 'SC02_I1_9x16', 'scene_id': 'SC02', 'ratio': '9:16', 'based_on': None,
             'prompt': 'SC02 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC02_I1_16x9', 'scene_id': 'SC02', 'ratio': '16:9', 'based_on': None,
             'prompt': 'SC02 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC02_I2_9x16', 'scene_id': 'SC02', 'ratio': '9:16', 'based_on': 'SC02_I1_9x16',
             'prompt': 'SC02 image 2', 'character_ids': [], 'visible_text': []},
            {'id': 'SC02_I2_16x9', 'scene_id': 'SC02', 'ratio': '16:9', 'based_on': 'SC02_I1_16x9',
             'prompt': 'SC02 image 2', 'character_ids': [], 'visible_text': []},
        ]
        synthetic_content = {'schema_version': '2.0', 'characters': [], 'scenes': [{'id': 'SC01'}, {'id': 'SC02'}]}
        # Keep the real revision/hash (content's own staleness check compares
        # against it) and only widen aspect_ratio to dual for image_check().
        real_brief, real_rev, real_hash = self.p.brief(self.j)
        dual_brief = (dict(real_brief, aspect_ratio='dual', scene_count=2), real_rev, real_hash)

        def ratio_provider(p, *args, **kw):
            self.calls.append(args)
            folder = Path(args[args.index('--out') + 1])
            ratio = args[args.index('--ratio') + 1]
            size = (1280, 720) if ratio == '16:9' else (720, 1280)
            import hashlib
            rgb = tuple(hashlib.sha256(' '.join(args).encode()).digest()[:3])
            Image.new('RGB', size, rgb).save(folder / 'result.png')
            write(folder / 'result.json', {'jobId': args[args.index('--id') + 1], 'type': 'image',
                  'prompt': args[args.index('--prompt') + 1], 'ratio': ratio, 'characters': [],
                  'source': 'google-flow-browser', 'status': 'downloaded'})
            proof = {'passed': True, 'mode': 'image', 'characters': []}
            if '--base-image' in args:
                proof['base_image'] = args[args.index('--base-image') + 1]
            write(folder.parent / 'ui-proof.json', proof)
            Image.new('RGB', (30, 30)).save(folder.parent / 'before-submit.png')
            return SimpleNamespace(returncode=0, stdout='TEST PROVIDER', stderr='')

        with patch('image_pipeline.content', return_value=synthetic_content), \
             patch('image_pipeline.planned_units', return_value=units), \
             patch.object(self.p, 'brief', return_value=dual_brief), \
             patch('adapters.gflow', side_effect=ratio_provider):
            self.p.run(self.j, 'images')  # references stage: no characters declared, no calls
            self.assertEqual(self.calls, [])
            self.approve('references')

            out_dir = self.p.job(self.j) / 'manual-final-out'; out_dir.mkdir()
            payload = ip.produce(self.p, self.j, out_dir)

        self.assertEqual(len(self.calls), 8)
        ratios_seen = [a[a.index('--ratio') + 1] for a in self.calls]
        self.assertEqual(ratios_seen, ['9:16'] * 4 + ['16:9'] * 4,
                          'every 9:16 image must submit before any 16:9 image')

        prompts_seen = [a[a.index('--prompt') + 1] for a in self.calls]
        expected_scene_order = ['SC01 image 1', 'SC01 image 2', 'SC02 image 1', 'SC02 image 2'] * 2
        self.assertEqual([p.rsplit('Scene prompt: ', 1)[-1] for p in prompts_seen], expected_scene_order,
                          'a based_on chain inside one scene must stay in order within each ratio')

        base_image_calls = [a for a in self.calls if '--base-image' in a]
        self.assertEqual(len(base_image_calls), 4, 'the four chained variations must attach their predecessor')

        # Final payload keeps the original scene-major/ratio-minor plan order
        # even though submission itself was ratio-major.
        self.assertEqual([x['scene_id'] for x in payload['items']], [u['id'] for u in units])

    def test_user_policy_allows_preflight_without_screenshot(self):
        import image_pipeline
        from unittest.mock import patch
        with patch.object(image_pipeline, 'read', return_value={
            'flow_require_ui_evidence': False, 'video_generation': False, 'credit_budget': 0
        }):
            evidence = image_pipeline.preflight(self, 'unused', 'image')
        self.assertFalse(evidence['cost_verified'])
        self.assertEqual(evidence['cost_policy'], 'user_assumed_zero')
        self.assertNotIn('screenshot', evidence)

    def test_flow_batch_default_off(self):
        # No flow_batch key in config.json -> cfg.get('flow_batch', False) is
        # False, so produce() must never even attempt a 'batch' invocation.
        cfg = read(self.root / 'config.json')
        self.assertNotIn('flow_batch', cfg)
        self.finish()
        self.assertTrue(all(a[0] != 'batch' for a in self.calls))

    def test_flow_batch_path_isolates_a_failed_job(self):
        # gflow batch is gated behind config flow_batch (default off; this
        # test turns it on via a scoped read() patch so config.json itself
        # is never touched). Three independent (no based_on) images share
        # one ratio group and go through a single simulated `gflow batch`
        # call; SC02's job is made to fail. Proves: one batch call is made,
        # SC02 ends up 'ambiguous' (never auto-resent), and SC01/SC03 still
        # get complete, independent 'downloaded' journals with their own
        # per-job evidence (preflight.json/.png, ui-proof.json,
        # before-submit.png) -- one job's failure cannot corrupt another's.
        from pilot import read as real_read
        units = [
            {'id': 'SC01_I1', 'scene_id': 'SC01', 'ratio': '9:16', 'based_on': None,
             'prompt': 'SC01 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC02_I1', 'scene_id': 'SC02', 'ratio': '9:16', 'based_on': None,
             'prompt': 'SC02 image 1', 'character_ids': [], 'visible_text': []},
            {'id': 'SC03_I1', 'scene_id': 'SC03', 'ratio': '9:16', 'based_on': None,
             'prompt': 'SC03 image 1', 'character_ids': [], 'visible_text': []},
        ]
        synthetic_content = {'schema_version': '2.0', 'characters': [],
                              'scenes': [{'id': 'SC01'}, {'id': 'SC02'}, {'id': 'SC03'}]}
        real_brief, real_rev, real_hash = self.p.brief(self.j)
        dual_brief = (dict(real_brief, aspect_ratio='dual', scene_count=3), real_rev, real_hash)

        def read_with_batch_flag(path):
            d = real_read(path)
            if isinstance(d, dict) and str(path).endswith('config.json') and 'flow_model' in d:
                d = dict(d, flow_batch=True)
            return d

        batch_calls = []
        def fake_batch_gflow(p, *args, **kw):
            batch_calls.append(args)
            self.assertEqual(args[0], 'batch')
            jobs_file = Path(args[1])
            out_dir = Path(args[args.index('--out') + 1])
            jobs = read(jobs_file)['jobs']
            self.assertEqual(len(jobs), 3, 'all three independent images go in one batch call')
            records = []
            for job in jobs:
                evidence_dir = out_dir / '.evidence' / job['id']; evidence_dir.mkdir(parents=True, exist_ok=True)
                if 'SC02' in job['prompt']:
                    records.append({'id': job['id'], 'type': 'image', 'status': 'failed',
                                     'artifacts': [], 'error': 'TEST induced failure'})
                    continue
                write(evidence_dir / 'ui-proof.json', {'passed': True, 'mode': 'image', 'characters': job.get('character', [])})
                Image.new('RGB', (30, 30)).save(evidence_dir / 'before-submit.png')
                asset = out_dir / (job['id'] + '-1.png')
                Image.new('RGB', (720, 1280) if job['ratio'] == '9:16' else (1280, 720)).save(asset)
                write(asset.with_suffix('.json'), {'jobId': job['id'], 'type': 'image', 'prompt': job['prompt'],
                      'ratio': job['ratio'], 'characters': job.get('character', []),
                      'source': 'google-flow-browser', 'status': 'downloaded'})
                records.append({'id': job['id'], 'type': 'image', 'status': 'completed', 'artifacts': [str(asset)]})
            write(out_dir / 'gflow-run.json', {'source': 'google-flow-browser', 'jobs': records})
            return SimpleNamespace(returncode=0, stdout='BATCH TEST', stderr='')

        with patch('image_pipeline.content', return_value=synthetic_content), \
             patch('image_pipeline.planned_units', return_value=units), \
             patch.object(self.p, 'brief', return_value=dual_brief), \
             patch('image_pipeline.read', side_effect=read_with_batch_flag), \
             patch('adapters.gflow', side_effect=fake_batch_gflow):
            self.p.run(self.j, 'images')  # references stage: no characters, no calls
            self.approve('references')

            out_dir = self.p.job(self.j) / 'manual-batch-out'; out_dir.mkdir()
            with self.assertRaisesRegex(Blocked, 'M2_AMBIGUOUS'):
                ip.produce(self.p, self.j, out_dir)

        self.assertEqual(len(batch_calls), 1, 'exactly one gflow batch call for the whole ratio group')

        sc01 = self._journal_for('SC01_I1'); sc02 = self._journal_for('SC02_I1'); sc03 = self._journal_for('SC03_I1')
        self.assertEqual(sc01['state'], 'downloaded')
        self.assertEqual(sc03['state'], 'downloaded')
        self.assertEqual(sc02['state'], 'ambiguous')
        self.assertIn('error', sc02)

        for record in (sc01, sc03):
            folder = self.p.job(self.j) / Path(record['journal']).parent
            for name in ['preflight.json', 'preflight.png', 'ui-proof.json', 'before-submit.png']:
                self.assertTrue((folder / name).is_file(), f'{name} missing for {record["key"]}')
            self.assertTrue((self.p.job(self.j) / record['path']).is_file())
        # SC02's failure left no downloaded artifact behind for it to steal.
        self.assertNotIn('path', sc02)

    def test_wrapper_rejects_video_without_browser(self):
        # Assert the policy code, not the prose: the allowed-command list grows
        # (auth login joined it) while M2_POLICY is the stable contract.
        for argv in (['unknown'],['video'],['auth'],['auth','logout']):
            result=subprocess.run(['node',str(ROOT/'scripts/gflow_guard.mjs'),*argv,'--out','./out'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0,argv)
            self.assertIn('M2_POLICY',result.stderr,argv)

    def test_I09_resume_new_process(self):
        self.references()
        other=Pilot(self.root)
        # Ask the image stage directly: next() now reports audio first, and this
        # test is about the checkpoint surviving a new process, not module order.
        self.assertEqual(ip.describe(other,self.j)['checkpoint'],'final')
        other.db.close()
        n=len(self.calls);self.run_stage()
        self.assertEqual(sum(a[0]=='image' and '--character' not in a for a in self.calls),n)

    def test_I10_tampered_approval(self):
        self.finish();d=self.p.payload(self.j,'images')
        Image.new('RGB',(720,1280),'black').save(self.p.path(self.j,d['items'][0]['path']))
        self.p.refresh(self.j)
        self.assertEqual(self.p.rows(self.j)['images']['state'],'stale')

    def test_I10_reference_replacement(self):
        self.finish();d=self.p.payload(self.j,'images');cid=d['references'][0]['character_id']
        self.p.reject(self.j,'images','TEST change appearance',self.p.rows(self.j)['images']['revision'],'final',character=cid)
        self.assertEqual(ip.stage(self.p,self.j),'references')
        n=len(self.calls);self.run_stage()
        self.assertEqual(len(self.calls)-n,1)
        self.assertIsNone(ip.approved(self.p,self.j,'final'))

    def test_I11_single_scene_replacement(self):
        self.finish();old=self.p.rows(self.j)['images']['envelope'];n=len(self.calls)
        # Simulate an already-created audio module to test invalidation independently.
        self.p.db.execute("UPDATE modules SET state='approved' WHERE job=? AND module='audio'",(self.j,));self.p.db.commit()
        self.p.reject(self.j,'images','TEST revise scene six',self.p.rows(self.j)['images']['revision'],'final',scene='SC06')
        self.assertEqual(ip.stage(self.p,self.j),'final');self.run_stage()
        self.assertEqual(len(self.calls)-n,1)
        self.assertIn('TEST revise scene six',self.calls[-1][self.calls[-1].index('--prompt')+1])
        self.assertTrue(self.p.path(self.j,old).exists());self.assertEqual(self.p.rows(self.j)['audio']['state'],'approved')
        self.assertEqual(self.p.rows(self.j)['images']['state'],'awaiting_review')

    def provider_failure(self,error):
        with patch('adapters.gflow',return_value=SimpleNamespace(returncode=2,stdout='',stderr=error)) as call:
            with self.assertRaisesRegex(Blocked,error):self.p.run(self.j,'images')
            self.assertEqual(call.call_count,1)
            with self.assertRaises(Blocked):self.p.run(self.j,'images')
            self.assertEqual(call.call_count,1)
        self.assertEqual(self.p.rows(self.j)['images']['state'],'blocked')

    def test_I12_login(self):self.provider_failure('Login required')
    def test_I12_captcha(self):self.provider_failure('CAPTCHA')
    def test_I12_limit(self):self.provider_failure('Rate limit')

    def test_I13_protected_code(self):
        for f in ['image_pipeline.py','prompt_templates.py','AGENTS.md','tests/test_images_v2.py','scripts/gflow_guard.mjs']:
            q=self.root/f;original=q.read_text();q.write_text(original+'\n# tamper')
            with self.subTest(file=f),self.assertRaises(Blocked):self.p.status(self.j)
            q.write_text(original)

    def test_I14_renderer_handoff(self):
        self.finish();self.assertTrue(self.p.validate(self.j,'images')['passed'])
        self.assertEqual(self.p.next(self.j)['module'],'audio')
        d=self.p.payload(self.j,'images');c=self.p.payload(self.j,'content')
        self.assertEqual([i['scene_id'] for i in d['items']],[s['id'] for s in c['scenes']])
        self.assertEqual(len(d['items']),6)
        for i in d['items']:self.assertTrue(self.p.path(self.j,i['path']).is_file())
        self.assertEqual(self.p.db.execute('SELECT count(*) FROM image_reviews WHERE job=?',(self.j,)).fetchone()[0],2)
        # Exercise the actual renderer input consumer, stopping before media rendering.
        import adapters
        (self.p.job(self.j)/'handoff.wav').write_bytes(b'TEST ONLY; renderer never executes')
        audio={'wav':'handoff.wav','duration':48,'segments':[{'scene_id':x['id'],'start':i*8,'end':(i+1)*8,'text':x['narration']} for i,x in enumerate(c['scenes'])]}
        payload=self.p.payload
        out=self.p.job(self.j)/'render-handoff';out.mkdir()
        with patch.object(self.p,'payload',side_effect=lambda j,m: audio if m=='audio' else payload(j,m)), patch('adapters.subprocess.run',side_effect=RuntimeError('STOP_BEFORE_RENDER')):
            with self.assertRaisesRegex(RuntimeError,'STOP_BEFORE_RENDER'):adapters.render(self.p,self.j,out)
        props=read(out/'props.json')
        self.assertEqual([x['id'] for x in props['scenes']],[x['id'] for x in c['scenes']])
        for x in props['scenes']:self.assertTrue((out/'public'/x['image']).exists())

    def test_user_prompt_templates(self):
        for ratio in ['9:16','16:9']:
            self.assertIn(ratio,pt.image_prompt('scene',ratio))
            self.assertIn(ratio,pt.batch_prompt('image',['scene'],ratio))
        self.assertIn('single batch',pt.TEMPLATES['image'])
        self.assertIn('attached alongwith',pt.TEMPLATES['image-to-video'])

    def test_image_prompt_16x9_extends_without_adding_text(self):
        vertical = pt.image_prompt('scene', '9:16')
        horizontal = pt.image_prompt('scene', '16:9')
        self.assertNotIn('extend', vertical.lower())
        for keyword in ['wider', 'extend', 'central composition', 'text placement']:
            self.assertIn(keyword, horizontal.lower())
        self.assertIn('do not add any text, numbers, labels, or logos', horizontal.lower())
        # The approved visible-text list is untouched by the widening rule.
        self.assertTrue(horizontal.endswith('Scene prompt: scene'))

    def test_registration_requires_separate_cost_evidence(self):
        self.references();self.preflight(operations=['image'])
        with self.assertRaisesRegex(Blocked,'character-register'):self.p.run(self.j,'images')

    def test_missing_attachment_ui_proof_fails(self):
        def no_proof(p,*args,**kw):
            r=self.provider(p,*args,**kw);Path(args[args.index('--out')+1]).parent.joinpath('ui-proof.json').unlink();return r
        with patch('adapters.gflow',side_effect=no_proof):
            with self.assertRaises(Blocked):self.p.run(self.j,'images')
        self.assertEqual(self.p.rows(self.j)['images']['state'],'blocked')

if __name__=='__main__':unittest.main(verbosity=2)
