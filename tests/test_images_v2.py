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
        for n in ['pilot.py','image_pipeline.py','prompt_templates.py','content_contract.py','adapters.py','config.json','AGENTS.md','GEMINI.md']:
            shutil.copy(ROOT/n,self.root/n)
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
        e=dict(observed_at=time.time(),mode='image',credits_per_generation=0,model='Nano Banana 2',profile='video-pilot',project='Video Pilot',
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
    def first_three(self):self.references();self.run_stage();self.approve('first-three')
    def finish(self):self.first_three();self.run_stage();self.approve('final')

    def test_I01_content_gate(self):
        self.p.reject(self.j,'content','TEST requested edit')
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        self.assertEqual(self.calls,[])

    def test_I02_preflight(self):
        for changes in [dict(observed_at=time.time()-601),dict(mode='video'),dict(credits_per_generation=1),dict(account_confirmed=False),dict(operations=[])]:
            self.preflight(**changes)
            with self.assertRaisesRegex(Blocked,'M2_PREFLIGHT'):self.p.run(self.j,'images')
        self.assertEqual(self.calls,[])

    def test_I03_video_and_provider(self):
        import adapters
        with self.assertRaises(Blocked):adapters.request_video()
        with self.assertRaises(Blocked):pt.batch_prompt('text-to-video',['x'])
        cfg=read(self.root/'config.json');cfg['credit_budget']=1;write(self.root/'config.json',cfg)
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
        with self.assertRaisesRegex(Blocked,'CHECKPOINT'):ip.request(self.p,self.j,'SC04','x')
        self.run_stage();n=len(self.calls)
        with self.assertRaises(Blocked):self.p.run(self.j,'images')
        with self.assertRaises(Blocked):self.p.gate(self.j,'audio')
        self.assertEqual(len(self.calls),n)

    def test_I06_bad_assets(self):
        self.first_three();self.run_stage();d=self.p.payload(self.j,'images')
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
        self.first_three();self.run_stage();d=self.p.payload(self.j,'images')
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

    def test_first_three_edit_reuses_other_scenes(self):
        self.finish();n=len(self.calls)
        self.p.reject(self.j,'images','TEST edit SC01',self.p.rows(self.j)['images']['revision'],'final',scene='SC01')
        self.assertEqual(ip.stage(self.p,self.j),'first-three')
        self.run_stage();self.approve('first-three');self.run_stage()
        self.assertEqual(len(self.calls)-n,1)
        self.assertEqual(self.p.payload(self.j,'images')['checkpoint'],'final')

    def test_wrapper_rejects_video_without_browser(self):
        result=subprocess.run(['node',str(ROOT/'scripts/gflow_guard.mjs'),'video'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('only image or character create allowed',result.stderr)

    def test_I09_resume_new_process(self):
        self.references()
        output=subprocess.check_output([str(ROOT/'.venv/bin/python'),str(self.root/'pilot.py'),'resume',self.j],text=True)
        self.assertEqual(json.loads(output)['checkpoint'],'first-three')
        n=len(self.calls);self.run_stage()
        self.assertEqual(sum(a[0]=='image' and '--character' not in a for a in self.calls),n)

    def test_I10_tampered_approval(self):
        self.finish();d=self.p.payload(self.j,'images')
        Image.new('RGB',(720,1280),'black').save(self.p.path(self.j,d['items'][0]['path']))
        with self.assertRaises(Blocked):self.p.gate(self.j,'audio')
        self.assertEqual(self.p.rows(self.j)['images']['state'],'stale')

    def test_I10_reference_replacement(self):
        self.finish();d=self.p.payload(self.j,'images');cid=d['references'][0]['character_id']
        self.p.reject(self.j,'images','TEST change appearance',self.p.rows(self.j)['images']['revision'],'final',character=cid)
        self.assertEqual(ip.stage(self.p,self.j),'references')
        n=len(self.calls);self.run_stage()
        self.assertEqual(len(self.calls)-n,1)
        self.assertIsNone(ip.approved(self.p,self.j,'first-three'))

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
        self.assertEqual(self.p.db.execute('SELECT count(*) FROM image_reviews WHERE job=?',(self.j,)).fetchone()[0],3)
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
