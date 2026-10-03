"""Execution/grants/ownership contracts with isolated fixture providers, never live media."""
import copy
import json
import io
import sys
from contextlib import redirect_stdout
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from pilot import ROOT, Pilot, PilotView, Blocked, read, write, digest, hashobj, observe_job
from permissions import Grants, PermissionDenied
import execution as ex
import workflow


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('schemas', 'examples', 'scripts', 'assets/characters/channel-mascot'):
            if (ROOT / name).exists(): shutil.copytree(ROOT / name, self.root / name)
        shutil.copy(ROOT / 'config.json', self.root / 'config.json')
        cfg = read(self.root / 'config.json'); cfg['brief_policies'] = []
        write(self.root / 'config.json', cfg)
        self.p = Pilot(self.root)
        self.addCleanup(self.p.db.close)
        self.job = 'fixture-v4'
        self.brief = read(ROOT / 'examples/m1/brief.json')
        self.content = read(ROOT / 'examples/story-v3/content.json')
        self.grant = Grants(self.root).grant('production', source='TEST actual job instruction', jobs=[self.job], paths=['runs/'+self.job+'/**'])

    def new(self, mode='review', dynamic=False):
        brief = copy.deepcopy(self.brief)
        if dynamic: brief.update(schema_version='3.0', scene_count=None)
        return ex.new(self.p, self.job, brief, mode, self.grant['id'])

    def outline(self):
        return {'outline': self.content['outline']}

    def author_inputs(self):
        ex.author(self.p, self.job, 'outline', self.outline(), 'TEST connected author')
        step = ex.advance(self.p, self.job)
        if step['action'] == 'review': self.approve('outline')
        ex.author(self.p, self.job, 'dialogue', self.content, 'TEST connected author')

    def approve(self, phase):
        return ex.approve(self.p, self.job, phase, ex.current(self.p, self.job, phase)['revision'], 'TEST actual decision '+phase)

    def fixture_provider(self, p, job, out):
        file = out/'fixture.bin'; file.write_bytes(b'isolated technical fixture')
        return {'wav': str(file.relative_to(p.job(job))), 'language': 'vi'}

    def fixture_images(self, p, job, out):
        gallery=out/'gallery.json';write(gallery,{'fixture':True})
        return {'checkpoint':'final','references':[],'items':[],'proofs':[],
                'contact_sheet':None,'gallery':str(gallery.relative_to(p.job(job)))}

    def fixture_render(self, p, job, out):
        file=out/'fixture.mp4';file.write_bytes(b'isolated render fixture')
        return {'video':str(file.relative_to(p.job(job)))}

    def providers(self):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch('execution.runtime_ready', return_value={'fixture':True}))
        stack.enter_context(patch('adapters.audio',side_effect=self.fixture_provider))
        stack.enter_context(patch('adapters.render',side_effect=self.fixture_render))
        stack.enter_context(patch('image_pipeline.produce',side_effect=self.fixture_images))
        stack.enter_context(patch('image_pipeline.check',side_effect=lambda p,j,payload:[payload['gallery']]))
        stack.enter_context(patch.object(self.p,'remote_checks',side_effect=lambda j,m,payload:[payload['wav' if m=='audio' else 'video']]))
        return stack

    def test_review_stops_at_every_exact_output_and_rejects_stale_decision(self):
        self.new();ex.author(self.p,self.job,'outline',self.outline(),'TEST author')
        step=ex.advance(self.p,self.job)
        self.assertEqual((step['phase'],step['action']),('outline','review'))
        with self.assertRaises(Blocked):ex.approve(self.p,self.job,'outline',99,'TEST')
        self.approve('outline');ex.author(self.p,self.job,'dialogue',self.content,'TEST author')
        with self.providers(), patch('machine_review.review', side_effect=AssertionError('reviewer forbidden')):
            for phase in ('dialogue','audio','images','video'):
                step=workflow.advance(self.p,self.job)
                self.assertEqual((step['phase'],step['action']),(phase,'review'))
                self.assertEqual(workflow.next_step(self.p,self.job)['phase'],phase)
                with self.assertRaises(Blocked):ex.approve(self.p,self.job,phase,step['checkpoints'][0]['revision']+99,'TEST')
                self.approve(phase)
            self.assertTrue(ex.advance(self.p,self.job)['complete'])
        rows=self.p.db.execute("SELECT count(*) FROM events WHERE job=? AND event='checkpoint_approved'",(self.job,)).fetchone()[0]
        self.assertEqual(rows,5)

    def test_auto_has_no_quality_decisions_or_reviewer_and_requests_connected_author(self):
        self.new('auto')
        step=ex.advance(self.p,self.job)
        self.assertEqual(step['action'],'author_outline')
        self.assertEqual(step['checkpoints'][0]['state'],'pending')
        count=self.p.db.execute("SELECT count(*) FROM events WHERE event='author_action_requested'").fetchone()[0]
        ex.advance(self.p,self.job)
        self.assertEqual(self.p.db.execute("SELECT count(*) FROM events WHERE event='author_action_requested'").fetchone()[0],count)
        self.author_inputs()
        with self.providers(),patch('machine_review.review',side_effect=AssertionError('reviewer forbidden')):
            self.assertEqual(ex.advance(self.p,self.job)['action'],'complete')
        self.assertEqual(list(self.p.job(self.job).glob('checkpoints/*/*/decision.json')),[])
        with self.assertRaises(Blocked):self.approve('video')

    def test_dynamic_scene_count_freezes_from_this_outline(self):
        self.new(dynamic=True)
        self.assertIsNone(self.p.brief(self.job)[0]['scene_count'])
        ex.author(self.p,self.job,'outline',self.outline(),'TEST author')
        ex.advance(self.p,self.job)
        self.assertEqual(self.p.brief(self.job)[0]['scene_count'],len(self.outline()['outline']))
        self.assertEqual(self.p.brief(self.job)[1],2)

    def test_observation_never_initializes_or_refreshes_and_keeps_running_owner(self):
        self.new()
        with ex.lease(self.p,self.job):
            before={str(p.relative_to(self.root)):digest(p) for p in self.root.rglob('*') if p.is_file()}
            with patch.object(Pilot,'__init__',side_effect=AssertionError('read must not initialize')),patch.object(Pilot,'refresh',side_effect=AssertionError('read must not refresh')):
                result=observe_job(self.root,self.job)
                self.assertEqual(result['control']['pid'],os.getpid())
            after={str(p.relative_to(self.root)):digest(p) for p in self.root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)

    def test_live_owner_denies_second_runner_mode_change_and_takeover(self):
        self.new()
        with ex.lease(self.p,self.job):
            for action in (lambda:ex.advance(self.p,self.job),lambda:ex.change_mode(self.p,self.job,'auto','TEST source'),lambda:ex.takeover(self.p,self.job,'TEST takeover')):
                with self.assertRaisesRegex(Blocked,'JOB_RUNNING'):action()

    def test_stop_blocks_submits_but_is_cleared_by_authorized_resume(self):
        self.new('auto')
        with self.assertRaisesRegex(Blocked,'LEASE_REQUIRED'):ex.before_submit(self.p,self.job)
        with ex.lease(self.p,self.job):
            ex.stop(self.p,self.job,'TEST stop from human')
            with self.assertRaisesRegex(Blocked,'STOP_REQUESTED'):ex.before_submit(self.p,self.job)
        self.assertEqual(ex.advance(self.p,self.job)['action'],'stopped')
        self.assertEqual(ex.resume(self.p,self.job)['action'],'author_outline')
        self.assertFalse(ex.control(self.p,self.job)['stop_requested'])

    def test_mode_change_is_official_and_previous_user_decision_stays_immutable(self):
        self.new();ex.author(self.p,self.job,'outline',self.outline(),'TEST author');ex.advance(self.p,self.job);self.approve('outline')
        decision=self.p.path(self.job,ex.current(self.p,self.job,'outline')['decision']);stamp=digest(decision)
        ex.change_mode(self.p,self.job,'auto','TEST explicit mode change')
        self.assertTrue(ex.accepted(self.p,self.job,'outline'))
        self.assertEqual(digest(decision),stamp)
        ex.change_mode(self.p,self.job,'review','TEST explicit mode change back')
        self.assertTrue(ex.accepted(self.p,self.job,'outline'))
        cfg=read(self.p.job(self.job)/'workflow.json');cfg['mode']='auto';write(self.p.job(self.job)/'workflow.json',cfg)
        with self.assertRaisesRegex(Blocked,'EXECUTION_SETTINGS'):ex.observe(self.p,self.job)

    def test_manifest_cannot_be_forged_or_changed_and_original_outline_is_preserved(self):
        self.new('auto');ex.author(self.p,self.job,'outline',self.outline(),'TEST author');ex.advance(self.p,self.job)
        manifest=ex.latest(self.p,self.job,'outline');original=self.p.path(self.job,manifest['assets'][0]);stamp=digest(original)
        ex.reject(self.p,self.job,'outline',1,'TEST adjust outline')
        self.assertEqual(digest(original),stamp)
        self.assertIsNone(ex.current(self.p,self.job,'outline'))
        path=self.p.job(self.job)/'checkpoints/outline/1/manifest.json';manifest['snapshot']={};write(path,manifest)
        self.assertFalse(ex.accepted(self.p,self.job,'outline'))

    def test_compatible_system_changes_do_not_lock_v4_but_contract_changes_do(self):
        self.new('auto');(self.root/'README.md').write_text('Changed operational guidance')
        self.p.integrity(self.job)
        path=self.p.job(self.job)/'integrity-meta.json';meta=read(path);meta['engine_contract']['delivery']=999;write(path,meta)
        with self.assertRaisesRegex(Blocked,'MIGRATION_REQUIRED'):self.p.integrity(self.job)

    def test_repairs_have_no_total_cap_but_unchanged_evidence_and_strategy_stops(self):
        self.new('auto')
        plan=dict(symptom='TEST failure',evidence='artifact-v1',error_class='visual',target='SC01',input_hash='fixture',strategy='composition 1',success_criteria='Visible action',rollback='Original preserved',submit_state='not_submitted')
        for index in range(15):
            ex.micro_plan(self.p,self.job,{**plan,'input_hash':str(index),'evidence':'artifact-'+str(index)})
        with self.assertRaisesRegex(Blocked,'NO_PROGRESS'):ex.micro_plan(self.p,self.job,{**plan,'input_hash':'14','evidence':'artifact-14'})
        with self.assertRaisesRegex(Blocked,'AMBIGUOUS_REQUEST'):ex.micro_plan(self.p,self.job,{**plan,'submit_state':'ambiguous'})
        ex.micro_plan(self.p,self.job,{**plan,'submit_state':'ambiguous','strategy':'collect'})

    def test_fresh_controller_reuses_grant_and_revocation_blocks_mutations(self):
        self.new('auto');another=Pilot(self.root)
        try:self.assertEqual(ex.advance(another,self.job)['action'],'author_outline')
        finally:another.db.close()
        Grants(self.root).revoke(self.grant['id'],source='TEST revoke')
        self.assertEqual(ex.observe(self.p,self.job)['job'],self.job)
        with self.assertRaises(PermissionDenied):ex.advance(self.p,self.job)

    def test_migration_retains_existing_audio_and_freezes_legacy_voice_without_rewriting(self):
        from tests import test_workflow as helpers
        workflow.new(self.p,self.job,self.brief,'review')
        data=copy.deepcopy(self.content);_,revision,stamp=self.p.brief(self.job);data.update(brief_revision=revision,brief_hash=stamp)
        write(self.p.job(self.job)/'draft/content.json',data)
        review=workflow.advance(self.p,self.job,'content')
        workflow.approve(self.p,self.job,'content',review['revision'],'TEST actual legacy decision')
        with patch('adapters.audio', side_effect=lambda p,j,out: helpers.WorkflowTests.audio(self,p,j,out)):
            self.p.run(self.job,'audio');self.p.approve(self.job,'audio',self.p.rows(self.job)['audio']['revision'],'TEST technical',actor='technical')
        before=self.p.rows(self.job)['audio'];raw=read(self.p.path(self.job,before['envelope']))
        hashes={name:digest(self.p.path(self.job,name)) for name in raw['files']}
        legacy_voice=self.p.payload(self.job,'control')['tts_voice']
        dev=Grants(self.root).grant('development',source='TEST migrate with valid WAV',jobs=[self.job])
        ex.migrate(self.p,self.job,dev['id'],self.grant['id'],'TEST authorized migration','auto')
        self.assertEqual(self.p.brief(self.job)[0]['outputs'][0]['voice'],legacy_voice)
        effective=self.p.payload(self.job,'audio')
        self.assertEqual(effective['tracks']['vi']['wav'],raw['payload']['wav'])
        self.assertEqual(read(self.p.path(self.job,before['envelope'])),raw)
        with patch('adapters.audio',side_effect=AssertionError('Valid retained WAV must not be synthesized')):
            step=ex.advance(self.p,self.job,'outline')
            ex.advance(self.p,self.job,'dialogue');ex.advance(self.p,self.job,'audio')
        self.assertTrue(ex.accepted(self.p,self.job,'audio'))
        self.assertEqual(self.p.rows(self.job)['audio'],before)
        self.assertEqual({name:digest(self.p.path(self.job,name)) for name in raw['files']},hashes)

    def test_cli_defaults_to_v4_reuses_grant_and_records_dirty_provenance(self):
        import pilot
        authority=Grants(self.root).grant('production',source='TEST actual multi-job task',jobs=['fixture-*'],paths=['runs/fixture-*/**'])
        brief=self.root/'input-brief.json';write(brief,self.brief)
        dirty={'head':'fixture-commit','dirty':True,'changes':[' M README.md']}
        for job in ('fixture-first','fixture-next-chat'):
            output=io.StringIO()
            with patch.object(pilot,'ROOT',self.root),patch('sys.argv',['pilot.py','new',job,'--brief',str(brief),'--mode','auto']),patch.object(Pilot,'git_state',return_value=dirty),redirect_stdout(output):
                self.assertEqual(pilot.main(),0)
            result=json.loads(output.getvalue())
            self.assertEqual(result['version'],4);self.assertEqual(result['grant_id'],authority['id'])
            self.assertEqual(result['checkpoints'][0]['state'],'pending')
            metadata=read(self.root/'runs'/job/'integrity-meta.json')
            self.assertTrue(metadata['protected_dirty']);self.assertEqual(metadata['git_head'],'fixture-commit')
        self.assertEqual(len(Grants(self.root).read()['grants']),2)

    def test_low_level_v4_writes_require_lease_and_cannot_forge_user_decisions(self):
        self.new('auto')
        with self.assertRaisesRegex(Blocked,'LEASE_REQUIRED'):self.p.refresh(self.job)
        with self.assertRaisesRegex(Blocked,'LEASE_REQUIRED'):self.p.approve(self.job,'control',1,'TEST user',actor='user')
        with ex.lease(self.p,self.job):
            with self.assertRaisesRegex(Blocked,'exact output checkpoint'):self.p.approve(self.job,'control',1,'TEST user',actor='user')
        Grants(self.root).revoke(self.grant['id'],source='TEST revoke')
        with ex.lease(self.p,self.job):
            with self.assertRaises(PermissionDenied):self.p.refresh(self.job)

    def test_custom_root_cannot_submit_media_without_bound_account_session(self):
        from session_store import Sessions
        self.new('auto')
        with ex.lease(self.p,self.job):
            for service in ('colab','flow'):
                with self.assertRaisesRegex(Blocked,'MANAGEMENT_SETUP_REQUIRED'):ex.before_submit(self.p,self.job,service)
        selected=Sessions(self.root).select(['colab:fixture','browser-fixture'],{'colab':'colab:fixture','flow':'browser-fixture'})
        ex.bind_session(self.p,self.job,selected['session_id'],'TEST actual setup selection')
        with ex.lease(self.p,self.job):
            ex.before_submit(self.p,self.job,'colab');ex.before_submit(self.p,self.job,'flow')
        frozen=ex.settings(self.p,self.job)['management_session']
        Sessions(self.root).select(['other-fixture'],{'colab':'other-fixture'})
        self.assertEqual(ex.settings(self.p,self.job)['management_session'],frozen)
        self.assertNotIn('pins',frozen)

    def test_migration_and_rollback_preserve_legacy_baseline_snapshots_and_request_owner(self):
        workflow.new(self.p,self.job,self.brief,'review')
        baseline=digest(self.p.job(self.job)/'integrity.json')
        legacy=read(self.p.job(self.job)/'workflow.json')
        request=self.p.job(self.job)/'flow/attempts/unknown/request.json';write(request,{'state':'unknown','account':'fixture-account','session':'fixture-session'})
        stamp=digest(request)
        dev=Grants(self.root).grant('development',source='TEST migrate existing job',jobs=[self.job])
        ex.migrate(self.p,self.job,dev['id'],self.grant['id'],'TEST authorized migration')
        self.assertEqual(digest(request),stamp)
        self.assertEqual(digest(self.p.job(self.job)/'integrity.json'),baseline)
        cfg=ex.settings(self.p,self.job);self.assertTrue((self.p.path(self.job,cfg['migration'])/'provenance.json').is_file())
        ex.rollback_migration(self.p,self.job,dev['id'],'TEST rollback')
        self.assertEqual(read(self.p.job(self.job)/'workflow.json'),legacy)
        self.assertEqual(digest(request),stamp)


if __name__=='__main__': unittest.main()
