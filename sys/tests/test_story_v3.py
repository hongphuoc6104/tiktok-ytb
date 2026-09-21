"""Isolated contract and integration tests; no external generation or approvals."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pilot import ROOT, Blocked, read, write
from content_contract import validate_brief, validate_content, ContractError
from scripts.story_plan import normalize_brief, image_units, estimates, timeline, feedback, calibrate_rates
import test_workflow as workflow_tests
import workflow as wf
import image_pipeline


def fixture():
    b=read(ROOT/'examples/story-v3/brief.json');c=read(ROOT/'examples/story-v3/content.json')
    c['brief_hash']='TEST';return b,c


def add_variation(c):
    sc=c['scenes'][0];base=sc['images'][0]
    sc['images'].append(dict(copy.deepcopy(base),id='IMAGE_EXTRA',based_on=base['id'],
        preserve='Giữ nền và người đang có',change='Thêm một chiếc cốc',reason='Minh họa vật được nhắc đến',
        visible_text=[{'text':'cup','placement':'cạnh cốc','object':'chiếc cốc'}]))
    sc['beats'].append(dict(copy.deepcopy(sc['beats'][0]),id='BEAT_EXTRA',image_id='IMAGE_EXTRA',
        anchor={'vi':{'quote':'Hãy thử','occurrence':1}},effect='fade'))
    sc['beats'].append(dict(copy.deepcopy(sc['beats'][0]),id='BEAT_REUSE',image_id='IMAGE_EXTRA',
        anchor={'vi':{'quote':'tôn trọng','occurrence':1}},effect='zoom_in'))
    return c


class StoryContractTests(unittest.TestCase):
    def check(self,b,c):validate_brief(ROOT,b);validate_content(ROOT,b,1,'TEST',c)
    def test_six_scenes_seven_images_eight_beats(self):
        b,c=fixture();add_variation(c);self.check(b,c)
        self.assertEqual(len(image_units(c)),7)
        self.assertEqual(sum(len(x['beats']) for x in c['scenes']),8)
    def test_topic_and_type_are_not_hardcoded(self):
        for topic,kind in [('Bảo dưỡng xe','technical'),('Kể chuyện lịch sử','documentary'),('Giới thiệu sản phẩm','advertisement')]:
            b,c=fixture();b.update(topic=topic,video_type=kind);c['topic']=topic;self.check(b,c)
    def test_no_internal_label_in_visible_prompt(self):
        b,c=fixture();c['scenes'][0]['images'][0]['description']+=' ch01'
        with self.assertRaisesRegex(ContractError,'INTERNAL_LABEL'):self.check(b,c)
    def test_character_description_cannot_leak_id(self):
        b,c=fixture();c['characters'][0]['appearance']+=' CH01'
        with self.assertRaisesRegex(ContractError,'INTERNAL_LABEL'):self.check(b,c)
    def test_forward_image_reference_rejected(self):
        b,c=fixture();add_variation(c);c['scenes'][0]['images'][0]['based_on']='IMAGE_EXTRA'
        with self.assertRaisesRegex(ContractError,'IMAGE_BASE'):self.check(b,c)
    def test_unused_images_rejected(self):
        b,c=fixture();add_variation(c);c['scenes'][0]['beats']=c['scenes'][0]['beats'][:1]
        with self.assertRaisesRegex(ContractError,'IMAGE_USAGE'):self.check(b,c)
    def test_unknown_or_reversed_anchors_rejected(self):
        b,c=fixture();add_variation(c);c['scenes'][0]['beats'][1]['anchor']['vi']['quote']='not in narration'
        with self.assertRaisesRegex(ContractError,'ANCHOR'):self.check(b,c)
    def test_bilingual_requires_both_anchor_languages(self):
        b,c=fixture();b['aspect_ratio']='dual'
        for sc in c['scenes']:sc['narration_en']='First we look. Then we act.'
        for cov in c['coverage']:cov['quote_en']='First we look.'
        with self.assertRaisesRegex(ContractError,'ANCHOR'):self.check(b,c)
    def test_dual_coverage_missing_quote_en(self):
        b,c=fixture();b['aspect_ratio']='dual'
        for sc in c['scenes']:sc['narration_en']='English narration for '+sc['id']+'.'
        with self.assertRaisesRegex(ContractError,'COVERAGE_EN'):self.check(b,c)
    def test_dual_quote_en_not_in_narration_en(self):
        b,c=fixture();b['aspect_ratio']='dual'
        for sc in c['scenes']:sc['narration_en']='English narration for '+sc['id']+'.'
        for cov in c['coverage']:cov['quote_en']='This sentence appears nowhere.'
        with self.assertRaisesRegex(ContractError,'QUOTE_EN'):self.check(b,c)
    def test_dual_quote_en_from_other_scene_rejected(self):
        b,c=fixture();b['aspect_ratio']='dual'
        for sc in c['scenes']:sc['narration_en']='English narration unique to '+sc['id']+'.'
        by_id={sc['id']:sc for sc in c['scenes']}
        for cov in c['coverage']:
            cov['quote_en']=by_id[cov['scene_id']]['narration_en']
        # SC01's coverage now quotes SC02's English narration instead of its own scene's.
        sc01=next(cov for cov in c['coverage'] if cov['scene_id']=='SC01')
        sc01['quote_en']=by_id['SC02']['narration_en']
        with self.assertRaisesRegex(ContractError,'QUOTE_EN'):self.check(b,c)
    def test_916_job_does_not_require_quote_en(self):
        b,c=fixture()
        self.check(b,c)
    def test_source_fact_must_exist(self):
        b,c=fixture();b.update(facts_required=True,sources=[dict(id='SRC',title='test',reference='provided test data',facts=['fact'])])
        c['claims']=[dict(scene_id='SC01',quote='Đồng nghiệp',language='vi',source_id='SRC',fact='invented')]
        with self.assertRaisesRegex(ContractError,'CLAIM_SOURCE'):self.check(b,c)
    def test_timing_depends_on_words_not_declared_estimate(self):
        b,c=fixture();first=estimates(b,c);c['scenes'][0]['narration']+=' thêm lời '*100
        self.assertGreater(estimates(b,c)['languages']['vi']['max'],first['languages']['vi']['max'])
    def test_v3_not_gated_by_estimate_mismatch(self):
        b,c=fixture();tiny={'min_seconds':1,'max_seconds':2};b['duration']=tiny;c['duration']=tiny
        self.check(b,c)
    def test_english_only_render_does_not_build_vietnamese_timeline(self):
        from types import SimpleNamespace
        import adapters
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'render';out.mkdir()
            (root/'voice.wav').write_bytes(b'TEST')
            (root/'image.png').write_bytes(b'TEST')
            write(root/'config.json',{})
            audio={'wav':'voice.wav','duration':5,'en':{'wav':'voice.wav','duration':8},'segments':[]}
            payloads={'content':{},'images':{},'audio':audio}
            p=SimpleNamespace(root=root,path=lambda job,path:root/path,
                              payload=lambda job,module:payloads[module],brief=lambda job:({'aspect_ratio':'16:9'},1,'TEST'))
            planned=[{'id':'SC01','title':'TEST','image':'image.png','start':0,'end':8}]
            with patch('scripts.story_plan.timeline',return_value=planned) as build, patch('adapters.subprocess.run',side_effect=RuntimeError('STOP')):
                with self.assertRaisesRegex(RuntimeError,'STOP'):adapters.render(p,'TEST',out)
            self.assertEqual(build.call_count,1)
            self.assertEqual(build.call_args.args[-2:],('en','16:9'))
            props=read(out/'props.json')
            self.assertEqual(props['scenes'],props['en_scenes'])

    def test_measured_rates_are_not_rtf(self):
        b,c=fixture();audio={'duration':50};rates=calibrate_rates(c,audio,'TEST')
        self.assertAlmostEqual(rates['vi']['units_per_second'],sum(len(x['narration'].split()) for x in c['scenes'])/50,places=4)
    def test_separate_language_timelines_and_image_reuse(self):
        b,c=fixture();add_variation(c);sc=c['scenes'][0];c['scenes']=[sc]
        sc['narration_en']='First we wait. Then we look at the cup. Finally we stop.'
        for bt,quote in zip(sc['beats'],['First','Then','Finally']):bt['anchor']['en']={'quote':quote,'occurrence':1}
        images={'items':[{'scene_id':'SC01','image_id':im['id'],'ratio':r,'path':im['id']+r} for im in sc['images'] for r in ['9:16','16:9']]}
        audio={'segments':[{'scene_id':'SC01','start':0,'end':10,'text':sc['narration']}], 'en':{'scenes':[{'scene_id':'SC01','start':0,'end':20}]}}
        vi=timeline(c,images,audio,'vi','9:16')[0];en=timeline(c,images,audio,'en','16:9')[0]
        self.assertNotEqual(vi['images'][1]['at'],en['images'][1]['at'])
        self.assertEqual(en['images'][1]['src'],en['images'][2]['src'])
        self.assertEqual(en['end'],20)
        self.assertEqual(en['images'][0]['at'],0)


class StoryIntegrationTests(unittest.TestCase):
    setUp=workflow_tests.WorkflowTests.setUp
    new=workflow_tests.WorkflowTests.new
    approve=workflow_tests.WorkflowTests.approve
    audio=workflow_tests.WorkflowTests.audio
    media=workflow_tests.WorkflowTests.media
    def provider(self,p,*args,**kwargs):
        result=workflow_tests.WorkflowTests.provider(self,p,*args,**kwargs)
        if '--base-image' in args:
            folder=Path(args[args.index('--out')+1]);proof=read(folder.parent/'ui-proof.json')
            proof['base_image']=args[args.index('--base-image')+1];write(folder.parent/'ui-proof.json',proof)
        return result
    def variant_job(self):
        wf.new(self.p,self.job,read(ROOT/'examples/story-v3/brief.json'))
        _,rev,h=self.p.brief(self.job);_,c=fixture();add_variation(c);c.update(brief_revision=rev,brief_hash=h)
        write(self.p.job(self.job)/'draft/content.json',c);wf.advance(self.p,self.job,'content');self.approve('content');return c
    def test_variations_reach_media_with_real_dependency_journal(self):
        self.variant_job();self.media();data=self.p.payload(self.job,'images')
        self.assertEqual(len(data['items']),7)
        extra=next(x for x in data['items'] if x['image_id']=='IMAGE_EXTRA')
        req=read(self.p.path(self.job,extra['request']))
        self.assertEqual(req['identity']['base_image']['target'],'SC01_I1_9x16')
        self.assertIn('--base-image',req['args'])
        self.assertNotIn('CH01',extra['actual_prompt'])
        self.assertIn('cup',extra['actual_prompt'])
        manifest=wf.current(self.p,self.job,'media')
        self.assertTrue(any(x.endswith('visual-timing.json') for x in manifest['assets']))
        self.approve('media')
        timing=next(x for x in manifest['assets'] if x.endswith('visual-timing.json'))
        write(self.p.path(self.job,timing),{})
        self.assertFalse(wf.approved(self.p,self.job,'media'))
    def test_media_reviewer_receives_image_and_audio_mapping(self):
        self.variant_job();self.media()
        manifest=wf.current(self.p,self.job,'media')
        for module in ['images','audio']:
            self.assertIn(self.p.rows(self.job)[module]['envelope'],manifest['assets'])

    def test_scene_edit_invalidates_all_its_variations_only(self):
        self.variant_job();self.media();before={x['image_id']:x['request'] for x in self.p.payload(self.job,'images')['items']}
        wf.reject(self.p,self.job,'media',1,'TEST fix SC01 CH01',scene='SC01');self.media()
        after={x['image_id']:x['request'] for x in self.p.payload(self.job,'images')['items']}
        self.assertNotEqual(before['SC01_I1'],after['SC01_I1'])
        self.assertNotEqual(before['IMAGE_EXTRA'],after['IMAGE_EXTRA'])
        self.assertEqual(before['SC02_I1'],after['SC02_I1'])
        item=next(x for x in self.p.payload(self.job,'images')['items'] if x['image_id']=='IMAGE_EXTRA')
        self.assertNotIn('CH01',item['actual_prompt']);self.assertNotIn('SC01',item['actual_prompt'])
    def test_rejected_content_unchanged_payload_blocked(self):
        self.new();wf.reject(self.p,self.job,'content',1,'TEST change narration')
        with self.assertRaisesRegex(Blocked,'REVISION_RESPONSE|UNCHANGED_DRAFT'):self.p.run(self.job,'content')
    def test_feedback_keeps_all_prior_requests(self):
        self.new()
        self.p.event(self.job,'content','rejected','TEST first change')
        self.p.event(self.job,'content','rejected','TEST second change')
        self.assertEqual([x['note'] for x in feedback(self.p,self.job)],['TEST first change','TEST second change'])
    def test_resume_rewrites_using_feedback_and_preserves_old_revision(self):
        self.new();old=self.p.payload(self.job,'content');wf.reject(self.p,self.job,'content',1,'TEST update title')
        request=feedback(self.p,self.job)[0]
        new=copy.deepcopy(old);new['scenes'][0]['title']='Updated title'
        new['revision_response']=[dict(request_id=request['request_id'],status='addressed',explanation='Changed first title',scene_ids=['SC01'])]
        calls=[]
        def invoke(prompt,schema,out,**kwargs):
            calls.append(prompt)
            return {'structured_output':{'outline':new['outline']} if len(calls)==1 else new}
        with patch('scripts.agy_pipeline.invoke',side_effect=invoke):wf.advance(self.p,self.job,'content')
        self.assertEqual(len(calls),2);self.assertIn('TEST update title',calls[0])
        self.assertEqual(read(self.p.job(self.job)/'revisions/content/1/content.json'),old)
        manifest=wf.current(self.p,self.job,'content');text=self.p.path(self.job,manifest['review']).read_text()
        self.assertIn('Updated title',text);self.assertIn('Thay đổi so với',text)
    def test_dual_units_have_both_ratios(self):
        self.new()
        with patch.object(self.p,'brief',return_value=({'aspect_ratio':'dual','planning':read(ROOT/'examples/story-v3/brief.json')['planning']},1,'TEST')):
            units=image_pipeline.planned_units(self.p,self.job)
        self.assertEqual(len(units),12);self.assertEqual({x['ratio'] for x in units},{'9:16','16:9'})
    def test_missing_base_attachment_evidence_blocks_media(self):
        self.variant_job()
        with patch.object(self,'provider',side_effect=lambda p,*a,**k:workflow_tests.WorkflowTests.provider(self,p,*a,**k)):
            with self.assertRaisesRegex(Blocked,'attachment evidence'):self.media()

if __name__=='__main__':unittest.main()
