"""Repair regressions with isolated jobs and fake providers; no production media."""
import copy
import unittest
from unittest.mock import patch

from pilot import Blocked, digest, read, write
import image_pipeline as ip
import workflow as wf
from scripts import image_repairs as repairs
from scripts.story_plan import safe_corrections
import test_story_v3 as story_tests


class RepairIntegrationTests(unittest.TestCase):
    setUp = story_tests.StoryIntegrationTests.setUp
    approve = story_tests.StoryIntegrationTests.approve
    audio = story_tests.StoryIntegrationTests.audio
    media = story_tests.StoryIntegrationTests.media
    provider = story_tests.StoryIntegrationTests.provider
    variant_job = story_tests.StoryIntegrationTests.variant_job

    def start(self):
        self.variant_job()
        self.media()

    def items(self):
        return {x['image_id']: x for x in self.p.payload(self.job,'images')['items']}

    def reject(self, note='Keep the face free of eyebrows.', plan=None, image='IMAGE_EXTRA'):
        return wf.reject(self.p,self.job,'media',wf.current(self.p,self.job,'media')['revision'],
                         note,image=image,ratio='9:16',repair_plan=plan)

    def plan(self, instruction='Remove eyebrows.', status='new', strategy=None):
        item = self.items()['IMAGE_EXTRA']
        h = repairs.history(self.p,self.job,'IMAGE_EXTRA_9x16')
        return {'current_sha256':digest(self.p.path(self.job,item['path'])),
                'previous_sha256':h[-1]['plan']['current_sha256'] if h else None,
                'strategy':strategy or {},'issues':[{'id':'eyebrows','status':status,
                'evidence':'TEST ONLY: two visible marks above the eyes.', 'instruction':instruction}]}

    def test_single_image_repair_preserves_sibling_and_audio(self):
        self.start(); before=self.items(); audio=self.p.rows(self.job)['audio']['envelope']
        self.reject(); self.media(); after=self.items()
        for key in before:
            self.assertEqual(before[key]['request']==after[key]['request'], key!='IMAGE_EXTRA')
        self.assertEqual(audio,self.p.rows(self.job)['audio']['envelope'])
        self.assertEqual(after['IMAGE_EXTRA']['actual_prompt'].count('Phong cách chữ chung:'),1)

    def test_unchanged_base_pixels_do_not_regenerate_child(self):
        self.start(); before=self.items()
        self.reject(image='SC01_I1'); self.media(); after=self.items()
        self.assertNotEqual(before['SC01_I1']['request'],after['SC01_I1']['request'])
        # Fake provider always returns the same pixels; descendant key must stay stable.
        self.assertEqual(before['IMAGE_EXTRA']['request'],after['IMAGE_EXTRA']['request'])

    def test_duplicate_strategy_stops_without_new_edit_or_provider_call(self):
        self.start(); self.reject(plan=self.plan()); self.media()
        with self.assertRaisesRegex(Blocked,'không thay đổi'):
            self.reject(plan=self.plan(status='remaining'))
        self.assertEqual(len(repairs.history(self.p,self.job,'IMAGE_EXTRA_9x16')),1)
        self.assertEqual(wf.next_step(self.p,self.job)['state'],'needs_attention')
        with patch('adapters.gflow') as provider:
            with self.assertRaisesRegex(Blocked,'NEEDS_ATTENTION'):wf.advance(self.p,self.job)
        provider.assert_not_called()

    def test_third_attempt_requires_concrete_strategy_change(self):
        self.start(); self.reject(plan=self.plan()); self.media()
        self.reject(plan=self.plan('Use a plain forehead.', 'remaining')); self.media()
        with self.assertRaisesRegex(Blocked,'Lỗi lặp hai lần'):
            self.reject(plan=self.plan('Absolutely no eyebrows.', 'remaining'))
        self.reject(plan=self.plan('Preserve the reference face.', 'remaining', {'pose':'Show regret through lowered head and hands.'}))
        self.assertIsNone(repairs.attention(self.p,self.job))

    def test_missing_comparison_and_stale_hash_block(self):
        self.start(); plan=self.plan(); plan['current_sha256']='0'*64
        with self.assertRaisesRegex(Blocked,'hash'):self.reject(plan=plan)
        self.reject(); self.media()
        with self.assertRaisesRegex(Blocked,'repair-plan'):self.reject('A differently worded ban.')

    def test_conflicting_issue_states_are_rejected(self):
        self.start(); plan=self.plan(); plan['issues'].append(dict(plan['issues'][0],status='resolved'))
        with self.assertRaisesRegex(Blocked,'duy nhất'):self.reject(plan=plan)

    def test_scene_note_cannot_target_only_one_sibling(self):
        self.start()
        with self.assertRaisesRegex(Blocked,'SCOPE'):
            wf.reject(self.p,self.job,'media',1,'Fix IMAGE_EXTRA only.',scene='SC01')

    def test_prompt_never_expands_character_or_image_descriptions(self):
        self.start(); c=self.p.payload(self.job,'content')
        prompt=safe_corrections(c,'CH01 CH01 IMAGE_EXTRA')
        self.assertNotIn(c['characters'][0]['appearance'],prompt)
        self.assertNotIn(c['scenes'][0]['images'][-1]['description'],prompt)

    def test_changed_prompt_cannot_bypass_ambiguous_attempt(self):
        self.start(); item=self.items()['IMAGE_EXTRA']; record=self.p.path(self.job,item['request'])
        # Isolated test journal, never a production artifact.
        data=read(record); data['state']='ambiguous'; write(record,data)
        cfg=read(self.root/'config.json')
        with patch.object(self.p,'gate'), patch('image_pipeline._plan_request',return_value=(cfg,'9:16','changed',{},'f'*64)), patch('adapters.gflow') as provider:
            with self.assertRaisesRegex(Blocked,'M2_AMBIGUOUS'):
                ip.request(self.p,self.job,'IMAGE_EXTRA_9x16','changed')
        provider.assert_not_called()

    def test_absolute_budget_cannot_be_reset_by_changing_issue_name(self):
        self.start();plan=self.plan()
        with patch('scripts.image_repairs.history',return_value=[{'id':i,'note':'TEST','plan':None} for i in range(6)]):
            with self.assertRaisesRegex(Blocked,'giới hạn 6'):
                self.reject(plan=plan)

    def test_machine_review_requires_actual_comparison_and_rejects_false_progress(self):
        import machine_review
        self.start(); self.reject(plan=self.plan()); self.media()
        manifest=wf.current(self.p,self.job,'media')
        def invoke(prompt,schema,out,**kwargs):
            request=read(out/'request.json');pair=request['repair_comparisons'][0]
            self.assertIn(str(self.p.path(self.job,pair['before']['path'])),request['files'])
            return {'structured_output':{'identity':request['identity'],'inspected_files':list(request['files']),
                'checks':{k:{'verdict':'pass','evidence':'TEST fixture only, not production.'} for k in machine_review.CRITERIA['media']},
                'repair_progress':{pair['target']:{'verdict':'pass','evidence':'TEST false progress on same pixels.',
                    'resolved':['eyebrows'],'remaining':[],'new':[]}}}}
        with patch('scripts.agy_pipeline.invoke',side_effect=invoke) as reviewer:
            with self.assertRaisesRegex(Blocked,'ảnh không đổi'):
                machine_review.review(self.p,self.job,'media',manifest['assets'],manifest['snapshot'])
            with self.assertRaisesRegex(Blocked,'REVIEW_UNCHANGED'):
                machine_review.review(self.p,self.job,'media',manifest['assets'],manifest['snapshot'])
            self.assertEqual(reviewer.call_count,1)
            with self.assertRaisesRegex(Blocked,'ảnh không đổi'):
                machine_review.review(self.p,self.job,'media',manifest['assets'],manifest['snapshot'],retry=True)
            self.assertEqual(reviewer.call_count,2)

    def test_collection_failure_retries_same_request_and_reuses_result(self):
        self.start(); self.reject()
        original=self.provider; calls=[]
        def provider(p,*args,**kwargs):
            calls.append(args)
            if len(calls)==1:
                error=Blocked('TEST collection failed');error.collection_only=True;raise error
            return original(p,*args,**kwargs)
        with self.assertRaisesRegex(Blocked,'collection failed'):self.media(provider)
        self.media(provider)
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[0],tuple(x for x in calls[1] if x!='--collect-only'))
        self.assertIn('--collect-only',calls[1])
        events=self.p.db.execute("SELECT event FROM events WHERE job=? AND event='flow_collection_resumed'",(self.job,)).fetchall()
        self.assertEqual(len(events),1)

    def test_batch_crash_without_adapter_log_never_falls_back_to_serial(self):
        self.start(); self.reject(image='SC02_I1')
        units=[u for u in ip.planned_units(self.p,self.job) if u['image_id']=='SC02_I1']
        refs=ip.approved(self.p,self.job,'references')['payload']['references']
        registrations={r['character_id']:ip.register_existing(self.p,self.job,r) for r in refs}
        with patch('adapters.gflow',side_effect=RuntimeError('TEST crash')) as provider:
            with self.assertRaisesRegex(Blocked,'M2_AMBIGUOUS'):ip.batch_submit(self.p,self.job,units,registrations)
        self.assertEqual(provider.call_count,1)
        self.assertIsNotNone(ip._unresolved_conflict(self.p,self.job,units[0]['id']))


if __name__=='__main__':unittest.main()
