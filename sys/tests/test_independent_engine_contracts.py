"""Independent operational QA. All roots/accounts/artifacts are disposable fixtures.

Real CLI parser, grants, database, revision snapshots, leases and decision journals
are exercised. Provider callbacks/remote artifact checks alone are replaced; these
tests make no claim about provider output quality, live login, GPU or real media.
"""
import copy
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import execution as ex
from permissions import Grants, PermissionDenied
from pilot import ROOT, Pilot, Blocked, digest, read, write, observe_job
from session_store import Sessions
import workflow


class IndependentEngineContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='independent-engine-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'custom-project'
        self.root = self.project / 'sys'
        self.root.mkdir(parents=True)
        (self.project / 'pilot.py').write_text('# isolated launcher marker\n')
        for folder in ('schemas', 'examples', 'scripts', 'assets/characters/channel-mascot'):
            if (ROOT / folder).exists(): shutil.copytree(ROOT / folder, self.root / folder)
        cfg = read(ROOT / 'config.json')
        cfg['brief_policies'] = []
        write(self.root / 'config.json', cfg)
        self.p = Pilot(self.root)
        self.addCleanup(self.p.db.close)
        self.job = 'authorized-old-video'
        self.brief = read(ROOT / 'examples/m1/brief.json')
        self.content = read(ROOT / 'examples/story-v3/content.json')
        self.grant = Grants(self.root).grant('production', source='TEST: create or repair this existing video', jobs=[self.job], paths=['sys/runs/' + self.job + '/**'])
        self.calls = []

    def cli(self, *args):
        code = ('import sys,json\nfrom pathlib import Path\nsys.path.insert(0,sys.argv.pop(1))\nimport pilot\npilot.ROOT=Path(sys.argv.pop(1))\n'
                'try:sys.exit(pilot.main())\nexcept Exception as error:print(json.dumps({"blocked":str(error),"errors":getattr(error,"errors",[])}));sys.exit(2)\n')
        result = subprocess.run([sys.executable, '-c', code, str(ROOT), str(self.root), *args], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout) if result.stdout.strip().startswith('{') else result.stderr

    def new(self, mode='auto'):
        session = Sessions(self.root).select(['colab:QA', 'flow:QA'], {'colab': 'colab:QA', 'flow': 'flow:QA'})
        return ex.new(self.p, self.job, self.brief, mode, self.grant['id'], session['session_id'])

    def draft(self, phase):
        return {'outline': copy.deepcopy(self.content['outline'])} if phase == 'outline' else copy.deepcopy(self.content)

    def author(self, phase):
        ex.author(self.p, self.job, phase, self.draft(phase), 'TEST: connected author submits the requested script')

    def accept(self, phase):
        return ex.approve(self.p, self.job, phase, ex.current(self.p, self.job, phase)['revision'], 'TEST: actual user feedback on ' + phase)

    def provider(self, p, job, out, phase):
        ex.before_submit(p, job, 'flow' if phase == 'images' else 'colab')
        self.calls.append((phase, p.rows(job)[ex.MODULES[phase]]['revision']))
        if phase == 'images':
            gallery = out / 'gallery.json'
            write(gallery, {'QA_fixture': True})
            return dict(checkpoint='final', references=[], items=[], proofs=[], contact_sheet=None, gallery=str(gallery.relative_to(p.job(job))))
        path = out / ('qa-fixture.wav' if phase == 'audio' else 'qa-fixture.mp4')
        path.write_bytes(b'QA fixture, not genuine provider media')
        return {('wav' if phase == 'audio' else 'video'): str(path.relative_to(p.job(job))), 'language': 'vi'}

    def providers(self, audio=None):
        stack = ExitStack()
        stack.enter_context(patch('adapters.audio', side_effect=audio or (lambda p,j,o: self.provider(p,j,o,'audio'))))
        stack.enter_context(patch('adapters.render', side_effect=lambda p,j,o: self.provider(p,j,o,'video')))
        stack.enter_context(patch('image_pipeline.produce', side_effect=lambda p,j,o: self.provider(p,j,o,'images')))
        stack.enter_context(patch('image_pipeline.check', side_effect=lambda p,j,x: [x['gallery']]))
        stack.enter_context(patch.object(Pilot, 'remote_checks', side_effect=lambda j,m,x: [x['wav' if m == 'audio' else 'video']]))
        stack.enter_context(patch('machine_review.review', side_effect=AssertionError('A reviewer must never execute in v4 auto')))
        return stack

    def ready_dialogue(self):
        self.author('outline')
        ex.advance(self.p, self.job, 'outline')
        if ex.settings(self.p,self.job)['mode'] == 'review': self.accept('outline')
        self.author('dialogue')

    def test_real_cli_fresh_controller_reuses_scope_and_total_plan(self):
        path = self.project / 'request.json'; write(path, self.brief)
        rc, data = self.cli('new', self.job, '--brief', str(path), '--mode', 'auto')
        self.assertEqual(rc, 0, data)
        plan = read(self.p.job(self.job) / 'plans/1/plan.json')
        self.assertEqual(plan['scope']['grant_id'], self.grant['id'])
        self.assertEqual([x['output'] for x in plan['steps']], list(ex.CHECKPOINTS))
        self.assertEqual(plan['locations']['video'], 'colab')
        rc, data = self.cli('resume', self.job)
        self.assertEqual((rc, data['action']), (0, 'author_outline'))
        self.assertEqual(data['grant_id'], self.grant['id'])
        rc, data = self.cli('status', self.job)
        self.assertEqual((rc, data['version']), (0, 4))

    def test_auto_repairs_existing_video_keeps_job_voice_history_and_grant(self):
        self.new(); self.ready_dialogue()
        with self.providers():
            self.assertTrue(ex.advance(self.p, self.job)['complete'])
            audio = copy.deepcopy(self.p.rows(self.job)['audio'])
            old = ex.current(self.p,self.job,'video')
            old_files = {name: digest(self.p.path(self.job,name)) for name in old['assets']}
            ex.reject(self.p,self.job,'video',old['revision'],'TEST: repair only the final video framing')
            fresh = Pilot(self.root)
            try: self.assertTrue(ex.resume(fresh,self.job)['complete'])
            finally: fresh.db.close()
            self.assertEqual(self.p.rows(self.job)['audio'], audio)
            self.assertEqual(ex.current(self.p,self.job,'video')['revision'], 2)
            self.assertEqual({name:digest(self.p.path(self.job,name)) for name in old_files},old_files)
        self.assertEqual(self.calls, [('audio',1),('images',1),('video',1),('video',2)])
        self.assertFalse(list(self.p.job(self.job).glob('checkpoints/*/*/decision.json')))
        self.assertTrue(list((self.p.job(self.job)/'micro-plans').glob('*/plan.json')))

    def test_review_waits_at_all_five_outputs_and_preserves_stale_decisions(self):
        self.new('review'); self.author('outline')
        with self.providers():
            for phase in ex.CHECKPOINTS:
                step = ex.advance(self.p,self.job)
                self.assertEqual((step['action'],step['phase']),('review',phase))
                with self.assertRaises(Blocked):ex.approve(self.p,self.job,phase,100,'TEST wrong revision')
                prior_calls = list(self.calls)
                self.assertEqual(ex.advance(self.p,self.job)['phase'],phase)
                self.assertEqual(prior_calls,self.calls)
                self.accept(phase)
                if phase == 'outline':self.author('dialogue')
            self.assertTrue(ex.advance(self.p,self.job)['complete'])
            decision = self.p.path(self.job, ex.current(self.p,self.job,'video')['decision'])
            stamp = digest(decision)
            ex.reject(self.p,self.job,'video',1,'TEST: adjust ending framing')
            ex.advance(self.p,self.job)
            with self.assertRaises(Blocked):ex.approve(self.p,self.job,'video',1,'TEST stale approval')
            self.assertEqual(digest(decision),stamp)

    def test_two_concurrent_cli_decision_writers_save_exactly_one_decision(self):
        self.new('review');self.author('outline');ex.advance(self.p,self.job)
        barrier=threading.Barrier(2);results=[]
        def run():
            barrier.wait();results.append(self.cli('approve',self.job,'outline','--revision','1','--note','TEST actual feedback'))
        threads=[threading.Thread(target=run) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(20)
        self.assertEqual(sorted(x[0] for x in results),[0,2],results)
        events=self.p.db.execute("SELECT count(*) FROM events WHERE job=? AND event='checkpoint_approved'",(self.job,)).fetchone()[0]
        self.assertEqual(events,1)
        self.assertEqual(len(list(self.p.job(self.job).glob('checkpoints/*/*/decision.json'))),1)

    def test_cli_stop_during_owned_submit_then_resume_without_duplicate(self):
        self.new();self.ready_dialogue()
        entered=threading.Event();released=threading.Event();errors=[];results=[]
        def audio(p,j,out):
            result=self.provider(p,j,out,'audio');entered.set()
            if not released.wait(15):raise AssertionError('QA stop synchronization timed out')
            return result
        def runner():
            try:results.append(ex.advance(self.p,self.job))
            except Exception as err:errors.append(str(err))
        with self.providers(audio):
            thread=threading.Thread(target=runner);thread.start()
            self.assertTrue(entered.wait(15))
            rc,data=self.cli('stop',self.job,'--source','TEST user stops this running video')
            self.assertEqual(rc,0,data)
            rc,data=self.cli('takeover',self.job,'--source','TEST try takeover live runner')
            self.assertNotEqual(rc,0)
            released.set();thread.join(20)
            self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
            self.assertEqual(results[0]['action'],'stopped')
            self.assertEqual(self.calls,[('audio',1)])
            self.assertTrue(ex.resume(self.p,self.job)['complete'])
            self.assertEqual(self.calls,[('audio',1),('images',1),('video',1)])

    def test_guidance_change_allowed_but_incompatible_schema_requires_migration(self):
        self.new();(self.project/'AGENTS.md').write_text('Updated authorized operational guidance')
        self.p.integrity(self.job)
        schema=read(self.root/'schemas/outline-v3.json')
        schema['required'].append('new_required_incompatible_key')
        write(self.root/'schemas/outline-v3.json',schema)
        with self.assertRaisesRegex(Blocked,'MIGRATION_REQUIRED'):self.p.integrity(self.job)

    def test_removing_allowed_property_under_closed_schema_requires_migration(self):
        self.new()
        schema=read(self.root/'schemas/outline-v3.json')
        self.assertIs(schema.get('additionalProperties'),False)
        del schema['properties']['outline']
        write(self.root/'schemas/outline-v3.json',schema)
        with self.assertRaisesRegex(Blocked,'MIGRATION_REQUIRED'):self.p.integrity(self.job)

    def test_production_grant_denies_all_protected_definitions_and_other_jobs(self):
        store=Grants(self.root)
        broad=store.grant('production',source='TEST content scope wildcard must not grant system edits',jobs=[self.job],paths=['**'])
        for path in ('AGENTS.md','.agents/rules/permissions.md','sys/config.json','sys/vocab/bank.py','sys/renderer/outputs.mjs','sys/schemas/brief.json','sys/runs/'+self.job+'/workflow.json'):
            with self.assertRaises(PermissionDenied,msg=path):store.require(broad['id'],'production','content',path=path)
        with self.assertRaises(PermissionDenied):store.require(self.grant['id'],'production','execute',job='other-video')

    def test_no_total_repair_cap_and_identical_plan_stops_across_controller(self):
        self.new()
        base=dict(symptom='TEST repeated layout defect',evidence='frame 1',error_class='visual',target='SC01',input_hash='input 1',strategy='TEST move prop',success_criteria='Prop visibly illustrates the meaning',rollback='Retain old frame',submit_state='not_submitted')
        for i in range(30):
            ex.micro_plan(self.p,self.job,{**base,'input_hash':str(i),'evidence':'TEST frame '+str(i)})
        fresh=Pilot(self.root)
        try:
            with self.assertRaisesRegex(Blocked,'NO_PROGRESS'):ex.micro_plan(fresh,self.job,{**base,'input_hash':'29','evidence':'TEST frame 29'})
            with self.assertRaisesRegex(Blocked,'AMBIGUOUS_REQUEST'):ex.micro_plan(fresh,self.job,{**base,'submit_state':'unknown'})
            ex.micro_plan(fresh,self.job,{**base,'submit_state':'unknown','strategy':'collect'})
        finally:fresh.db.close()

    def test_actual_audio_retake_revisions_exceed_legacy_total_and_scene_caps(self):
        self.new();self.ready_dialogue()
        with self.providers():
            self.assertTrue(ex.advance(self.p,self.job)['complete'])
            images=copy.deepcopy(self.p.rows(self.job)['images'])
            for index in range(8):
                revision=ex.current(self.p,self.job,'audio')['revision']
                ex.reject(self.p,self.job,'audio',revision,'TEST measured pronunciation correction '+str(index),scene='SC01')
                self.assertTrue(ex.resume(self.p,self.job)['complete'])
                self.assertEqual(self.p.rows(self.job)['images'],images)
        self.assertEqual(ex.current(self.p,self.job,'audio')['revision'],9)
        self.assertEqual(len([x for x in self.calls if x[0]=='audio']),9)
        self.assertEqual(len([x for x in self.calls if x[0]=='images']),1)
        edits=self.p.db.execute('SELECT count(*) FROM audio_edits WHERE job=? AND scene_id=?',(self.job,'SC01')).fetchone()[0]
        self.assertEqual(edits,8)

    def test_observe_does_not_modify_files_even_when_runner_owns_job(self):
        self.new()
        with ex.lease(self.p,self.job):
            before={str(x.relative_to(self.root)):digest(x) for x in self.root.rglob('*') if x.is_file()}
            state=observe_job(self.root,self.job)
            self.assertEqual(state['control']['pid'],os.getpid())
            after={str(x.relative_to(self.root)):digest(x) for x in self.root.rglob('*') if x.is_file()}
            self.assertEqual(before,after)

    def test_parallel_api_micro_plans_cannot_duplicate_identical_recovery(self):
        self.new()
        plan=dict(symptom='TEST unchanged image',evidence='same current frame',error_class='visual',target='SC01',input_hash='same input',strategy='same composition',success_criteria='Show changed action',rollback='Keep old frame',submit_state='not_submitted')
        rendezvous=threading.Barrier(2);outcomes=[]
        original_settings=ex.settings
        # Deterministically schedules the natural check/append race. It changes
        # no result, DB read or write; both callers reach settings after checking
        # that no recovery exists, before either writes its first event.
        def scheduled_settings(p,j):
            if threading.current_thread().name.startswith('qa-micro-'):
                try:rendezvous.wait(1)
                except threading.BrokenBarrierError:pass
            return original_settings(p,j)
        def writer():
            fresh=Pilot(self.root)
            try:
                try:ex.micro_plan(fresh,self.job,plan);outcomes.append('accepted')
                except Blocked:outcomes.append('blocked')
            finally:fresh.db.close()
        with patch('execution.settings',side_effect=scheduled_settings):
            threads=[threading.Thread(target=writer,name='qa-micro-'+str(i)) for i in range(2)]
            for thread in threads:thread.start()
            for thread in threads:thread.join(20)
        self.assertEqual(sorted(outcomes),['accepted','blocked'])
        count=self.p.db.execute("SELECT count(*) FROM events WHERE job=? AND event='micro_plan'",(self.job,)).fetchone()[0]
        self.assertEqual(count,1)

    def test_wrong_management_session_does_not_leave_unresumable_partial_job(self):
        Sessions(self.root).select(['colab:QA','flow:QA'],{'colab':'colab:QA','flow':'flow:QA'})
        with self.assertRaises(ValueError):ex.new(self.p,self.job,self.brief,'auto',self.grant['id'],'incorrect-session')
        self.assertFalse(self.p.job(self.job).exists(),'Rejected session validation must run before durable job creation')
        self.assertEqual(self.p.rows(self.job),{})

    def test_crashed_owner_takeover_preserves_checkpoint_and_request_identity(self):
        self.new();self.ready_dialogue()
        manifest=copy.deepcopy(ex.current(self.p,self.job,'outline'))
        sessions=Sessions(self.root)
        sessions.pin('QA-original-request',job=self.job,service='flow',account='flow:QA',session='QA-exact-session')
        pins=copy.deepcopy(sessions.read()['pins'])
        code=('import sys,time\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom pilot import Pilot\nimport execution\n'
              'p=Pilot(Path(sys.argv[2]))\nwith execution.lease(p,sys.argv[3]):\n print("owner-ready",flush=True)\n time.sleep(60)\n')
        child=subprocess.Popen([sys.executable,'-c',code,str(ROOT),str(self.root),self.job],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(),'owner-ready')
            with self.assertRaisesRegex(Blocked,'JOB_RUNNING'):ex.takeover(self.p,self.job,'TEST live owner cannot be replaced')
            child.kill();child.wait(timeout=5)
            ex.takeover(self.p,self.job,'TEST previous controller crashed; continue the same job')
            self.assertEqual(ex.current(self.p,self.job,'outline'),manifest)
            self.assertEqual(sessions.read()['pins'],pins)
            with self.providers():self.assertTrue(ex.resume(self.p,self.job)['complete'])
            self.assertEqual(self.calls,[('audio',1),('images',1),('video',1)])
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=5)
            child.stdout.close();child.stderr.close()

    def test_authorized_legacy_migration_rollback_preserve_decisions_artifacts_requests(self):
        workflow.new(self.p,self.job,self.brief,'review')
        content=copy.deepcopy(self.content);_,revision,stamp=self.p.brief(self.job)
        content.update(brief_revision=revision,brief_hash=stamp)
        write(self.p.job(self.job)/'draft/content.json',content)
        report=workflow.advance(self.p,self.job,'content')
        workflow.approve(self.p,self.job,'content',report['revision'],'TEST actual legacy dialogue approval')
        request=self.p.job(self.job)/'flow/attempts/unknown/request.json'
        write(request,{'state':'unknown','request_id':'QA-inflight','account':'QA-account','session':'QA-original-session'})
        pins=Sessions(self.root);pins.pin('QA-inflight',job=self.job,service='flow',account='QA-account',session='QA-original-session')
        preserved={str(x.relative_to(self.p.job(self.job))):digest(x) for x in self.p.job(self.job).rglob('*') if x.is_file()}
        pins_before=copy.deepcopy(pins.read()['pins'])
        dev=Grants(self.root).grant('development',source='TEST authorized migration and rollback of this old video',jobs=[self.job],operations=['migrate'])
        ex.migrate(self.p,self.job,dev['id'],self.grant['id'],'TEST migrate old job to current auto','auto')
        for name,old_hash in preserved.items():
            if name not in ('workflow.json','integrity-meta.json'):self.assertEqual(digest(self.p.path(self.job,name)),old_hash,name)
        self.assertEqual(pins.read()['pins'],pins_before)
        ex.rollback_migration(self.p,self.job,dev['id'],'TEST roll back without running v4 outputs')
        for name,old_hash in preserved.items():self.assertEqual(digest(self.p.path(self.job,name)),old_hash,name)
        self.assertEqual(pins.read()['pins'],pins_before)


if __name__ == '__main__':unittest.main()
