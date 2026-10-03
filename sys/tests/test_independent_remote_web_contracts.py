"""Independent QA; all identities, GPU and provider responses are synthetic."""
import copy
import json
import sys
import subprocess
import tempfile
import threading
import types
import os
import shutil
import wave
import base64
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

from account_budget import Budgets, HOUR, WINDOW
from dashboard.data import Dashboard
from dashboard.server import make_server
from session_store import Sessions
from colab_bridge.job_protocol import validate_render_result
from colab_bridge.protocol import file_hash
from dashboard.colab_probe import probe


class IndependentRemoteWebContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def ledger(self):
        ledger = Budgets(self.root / 'budget')
        ledger.bind_identity('profile-a', 'synthetic-google-identity', 'QA synthetic identity')
        ledger.bind_identity('profile-alias', 'synthetic-google-identity', 'QA synthetic alias')
        return ledger

    def test_flow_cap_is_shared_between_operations(self):
        ledger = self.ledger()
        ledger.flow_submit('profile-a', 'job-1:images', 'request-1', 100, evidence='QA synthetic send')
        ledger.flow_state('profile-a', 'job-1:images', 'request-1', 'unknown', 'QA synthetic timeout')
        with self.assertRaises(ValueError):
            Budgets(self.root / 'budget').flow_submit('profile-alias', 'job-2:images', 'request-2', 1, evidence='QA synthetic send')

    def test_same_flow_operating_session_does_not_reset_after_24h(self):
        ledger=self.ledger()
        with patch('account_budget.time.time',return_value=100):
            ledger.flow_submit('profile-a','same-operating-session','request-1',100,evidence='QA synthetic submitted slots')
            ledger.flow_state('profile-a','same-operating-session','request-1','collected','QA synthetic collected result')
        with patch('account_budget.time.time',return_value=100+WINDOW+1):
            with self.assertRaises(ValueError):
                Budgets(self.root/'budget').flow_submit('profile-alias','same-operating-session','request-2',1,evidence='QA same session after day boundary')

    def test_idle_cross_window_and_recheck_are_internal_only(self):
        ledger = self.ledger()
        ledger.allocated('profile-a', 'synthetic-session', device='T4', at=100, evidence='QA synthetic allocation')
        old = ledger.snapshot('profile-alias', 100 + 5*HOUR)
        self.assertEqual(old['available_seconds'], 0)
        with self.assertRaises(ValueError): ledger.reserve('profile-a', 'new', 1, now=100+5*HOUR)
        later = ledger.snapshot('profile-a', 100 + WINDOW + HOUR)
        self.assertEqual(later['used_seconds'], HOUR)
        self.assertTrue(later['needs_service_recheck'])
        self.assertFalse(later['provider_quota_verified'])

    def test_confirmed_release_and_new_allocation_do_not_keep_old_uncertainty_active(self):
        ledger=self.ledger()
        ledger.allocated('profile-a','old-session',device='T4',at=100,evidence='QA synthetic confirmed allocation')
        ledger.uncertain('profile-a','old-session','QA synthetic temporary disconnect')
        ledger.released('profile-a','old-session',at=300,evidence='QA synthetic confirmed termination')
        ledger.allocated('profile-alias','new-session',device='T4',at=400,evidence='QA synthetic new confirmed allocation')
        self.assertFalse(ledger.snapshot('profile-a',500)['uncertain'])

    def test_day_rollover_requires_service_recheck_before_new_work(self):
        from pilot import ROOT
        from colab_bridge.client import Client, ColabError
        ledger=self.ledger()
        ledger.bind_identity('colab:qa-account','synthetic-google-identity','QA synthetic identity')
        ledger.allocated('colab:qa-account','qa-session',device='T4',at=100,evidence='QA synthetic old-day allocation')
        cfg=json.loads((ROOT/'config.json').read_text());cfg['colab_tts']['management_store']=str(self.root/'budget')
        with patch('colab_bridge.client.cli',return_value='/bin/true'),patch('colab_bridge.accounts.STORE',self.root/'fake-store'):
            client=Client(self.root,cfg);client.account='qa-account';client.session='qa-session'
            with patch('account_budget.time.time',return_value=100+WINDOW+HOUR):
                self.assertTrue(ledger.snapshot('colab:qa-account')['needs_service_recheck'])
                with self.assertRaises(ColabError):client._reserve('new-day-request','audio')

    def test_default_changes_preserve_request_ownership(self):
        selected = Sessions(self.root)
        selected.select(['colab:a'], {'colab':'colab:a'})
        selected.pin('synthetic-request', job='job', service='colab', account='colab:a', session='original')
        selected.select(['colab:b'], {'colab':'colab:b'})
        self.assertEqual(Sessions(self.root).read()['pins']['synthetic-request']['session'], 'original')
        with self.assertRaises(ValueError): selected.pin('synthetic-request', job='job', service='colab', account='colab:b', session='new')

    def test_concurrent_unknown_render_is_collected_on_original_owner(self):
        from pilot import ROOT
        from colab_bridge.client import Client, ColabError
        from colab_bridge.job_protocol import build_render_request
        import re
        cfg=json.loads((ROOT/'config.json').read_text())
        (self.root/'image.png').write_bytes(b'QA-synthetic-image');(self.root/'en.wav').write_bytes(b'QA-synthetic-audio')
        brief={'aspect_ratio':'9:16','outputs':[{'aspect_ratio':'9:16','language':'en','subtitles':True,'voice':'alba','speed':.87}]}
        images={'items':[{'path':'image.png','scene_id':'SC01','image_id':'IM01','ratio':'9:16'}]}
        audio={'wav':'en.wav','tracks':{'en':{'wav':'en.wav','duration':1.}}}
        req=build_render_request(ROOT,brief,{'scenes':[]},images,audio,lambda x:self.root/x)
        entered=threading.Event();release=threading.Event();calls=[];errors=[]
        def call(self,*args,**kw):
            calls.append((self.account,self.session,args[0]))
            if args[0]=='exec' and 'm.run(' in kw.get('code',''):
                entered.set();release.wait(5);raise ColabError('QA synthetic timeout after send')
            if args[0]=='download':raise ColabError('QA synthetic pending result')
            found=re.search('VP_EXEC_OK_[a-f0-9]+',kw.get('code',''));return found.group() if found else ''
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch('colab_bridge.client.cli',return_value='/bin/true'))
            stack.enter_context(patch('colab_bridge.accounts.STORE',self.root/'fake-store'))
            stack.enter_context(patch('pathlib.Path.home',return_value=self.root/'fake-home'))
            for name in ('ensure_authenticated','_ready','_reserve','_settle'):stack.enter_context(patch.object(Client,name,return_value=None))
            stack.enter_context(patch.object(Client,'call',call))
            first=Client(self.root,cfg);first.account='qa-original';first.session='qa-session'
            def execute():
                try:first.render(req,self.root/'out',self.root/'cache')
                except Exception as error:errors.append(str(error))
            thread=threading.Thread(target=execute);thread.start();self.assertTrue(entered.wait(5))
            second=Client(self.root,cfg);second.account='qa-new-default';second.session='qa-new-session'
            try:
                with self.assertRaisesRegex(ColabError,'REQUEST_BUSY'):second.render(req,self.root/'out2',self.root/'cache')
            finally:release.set();thread.join(5)
            self.assertEqual(len(errors),1);calls.clear()
            different=copy.deepcopy(req);different['request_id']='a'*64
            with self.assertRaisesRegex(ColabError,'PENDING_OTHER_REQUEST'):second.render(different,self.root/'out2',self.root/'cache')
            with self.assertRaisesRegex(ColabError,'pending result'):second.render(req,self.root/'out2',self.root/'cache')
            self.assertEqual(calls,[('qa-original','qa-session','download')])

    def test_bootstrap_before_dependencies_actual_cli_apply_and_resume(self):
        script=Path(__file__).resolve().parents[1]/'scripts/bootstrap.py'
        command=[sys.executable,'-I','-S',str(script)]
        checked=subprocess.run(command+['check','--root',str(self.root),'--home',str(self.root)],capture_output=True,text=True,check=True)
        report=json.loads(checked.stdout)
        self.assertEqual(list(self.root.iterdir()),[])
        self.assertTrue(report['no_provider_calls'])
        self.assertEqual(report['capabilities']['jsonschema']['state'],'missing')
        self.assertEqual(report['capabilities']['colab_T4']['state'],'not_tested')
        first=subprocess.run(command+['apply','--root',str(self.root)],capture_output=True,text=True,check=True)
        self.assertFalse(json.loads(first.stdout)['management_dependencies_installed'])
        before=(self.root/'.venv-management/pyvenv.cfg').stat().st_mtime_ns
        second=subprocess.run(command+['resume','--root',str(self.root)],capture_output=True,text=True,check=True)
        self.assertEqual((self.root/'.venv-management/pyvenv.cfg').stat().st_mtime_ns,before)
        self.assertTrue(json.loads(second.stdout)['resume_safe'])
        self.assertFalse(any(x in str(p) for p in self.root.rglob('*') for x in ('torch','transformers','node_modules','token.json')))

    def test_expired_refreshable_credential_is_not_relogin(self):
        credentials = types.SimpleNamespace(valid=False, expired=True, refresh_token='synthetic-refresh-token')
        modules = {
            'google': types.ModuleType('google'), 'google.oauth2': types.ModuleType('google.oauth2'),
            'google.oauth2.credentials': types.SimpleNamespace(Credentials=types.SimpleNamespace(from_authorized_user_file=lambda _: credentials)),
            'google.auth': types.ModuleType('google.auth'), 'google.auth.transport': types.ModuleType('google.auth.transport'),
            'google.auth.transport.requests': types.SimpleNamespace(AuthorizedSession=lambda *_args, **_kwargs: self.fail('Must not refresh on auth inspection')),
            'colab_cli': types.ModuleType('colab_cli'), 'colab_cli.common': types.SimpleNamespace(Client=object, Prod=object),
        }
        with patch.dict(sys.modules, modules): result = probe(self.root / 'synthetic-token.json')
        self.assertNotEqual(result['auth'], 'login_required', result)

    def test_identity_probe_429_and_503_keep_correct_service_reason(self):
        for status,reason in ((429,'quota'),(503,'capacity'),(403,'permission_unknown')):
            credentials=types.SimpleNamespace(valid=True)
            class FakeSession:
                def __init__(self,*_a,**_k):pass
                def get(self,*_a,**_k):return types.SimpleNamespace(status_code=status)
            modules={
                'google':types.ModuleType('google'),'google.oauth2':types.ModuleType('google.oauth2'),
                'google.oauth2.credentials':types.SimpleNamespace(Credentials=types.SimpleNamespace(from_authorized_user_file=lambda _:credentials)),
                'google.auth':types.ModuleType('google.auth'),'google.auth.transport':types.ModuleType('google.auth.transport'),
                'google.auth.transport.requests':types.SimpleNamespace(AuthorizedSession=FakeSession),
                'colab_cli':types.ModuleType('colab_cli'),'colab_cli.common':types.SimpleNamespace(Client=object,Prod=object)}
            with patch.dict(sys.modules,modules):result=probe(self.root/'fake-token.json')
            with self.subTest(status=status):
                self.assertNotEqual(result['auth'],'login_required')
                self.assertEqual(result['reason'],reason)

    def test_render_acceptance_rejects_wrong_props_language(self):
        request = {'request_id':'synthetic-request', 'brief':{'aspect_ratio':'9:16','outputs':[{'aspect_ratio':'9:16','language':'en','subtitles':True}]},
                   'audio':{'tracks':{'en':{'duration':1.}}}}
        files = {'video.mp4':b'\0\0\0\x18ftypisomSYNTHETIC-NOT-MEDIA', 'layout.json':b'{"passed":true}',
                 'editorial-audit.json':b'{"quality_approval":false}',
                 'props.json':json.dumps({'aspect_ratio':'9:16','outputs':request['brief']['outputs'], 'primary_language':'vi',
                                          'tracks':{'vi':{'audioSrc':'vi.wav','cues':[{'text':'Sai track'}]}}}).encode()}
        for name, data in files.items(): (self.root / name).write_bytes(data)
        report = {'request_id':'synthetic-request','operation':'render','processing_location':'colab','device':'QA SYNTHETIC Tesla T4',
                  'outputs':[dict(request['brief']['outputs'][0], file='video.mp4', width=1080,height=1920,duration=1.,video_codec='h264',audio_codec='aac')],
                  'files':{name:{'size':(self.root/name).stat().st_size,'sha256':file_hash(self.root/name)} for name in files}}
        (self.root/'render-result.json').write_text(json.dumps(report))
        with self.assertRaises(ValueError): validate_render_result(self.root, request)

    def server(self):
        job = self.root/'runs/isolated-job'; (job/'checkpoints/audio/1').mkdir(parents=True)
        (job/'brief-current.json').write_text('{}')
        (job/'checkpoint.txt').write_text('QA artifact data')
        (job/'checkpoints/audio/1/manifest.json').write_text(json.dumps({'revision':1,'payload':{'bearer':'Bearer synthetic-secret'},'assets':['checkpoint.txt'],'review':None}))
        app = Dashboard(self.root, home=self.root/'empty-home', cli=lambda _: {'mode':'review','checkpoints':[]})
        server = make_server(self.root, dashboard=app)
        thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown); self.addCleanup(thread.join,2)
        return server, app

    def http(self, server, method, path, body=None, headers=None):
        conn = HTTPConnection('127.0.0.1',server.server_port)
        conn.request(method,path,body,headers or {})
        response = conn.getresponse(); data = response.read(); conn.close()
        return response.status, data

    def test_live_http_host_csrf_traversal_and_redaction(self):
        server, app = self.server()
        status, raw = self.http(server,'GET','/api/state'); self.assertEqual(status,200)
        state = json.loads(raw); self.assertNotIn(b'synthetic-secret',raw)
        csrf = state['csrf']; origin=f'http://127.0.0.1:{server.server_port}'
        good={'Origin':origin,'Content-Type':'application/json','X-VP-CSRF':csrf}
        body=json.dumps({'pool':[],'defaults':{}})
        self.assertEqual(self.http(server,'POST','/api/actions/session',body,{**good,'Origin':'https://evil.invalid'})[0],403)
        self.assertEqual(self.http(server,'POST','/api/actions/session',body,{**good,'X-VP-CSRF':'bad'})[0],403)
        self.assertEqual(self.http(server,'GET','/api/state',headers={'Host':'evil.invalid'})[0],403)
        self.assertEqual(self.http(server,'GET','/api/jobs/%2e%2e%2fescape')[0],404)
        self.assertEqual(self.http(server,'GET','/media/isolated-job/'+'f'*24)[0],404)
        self.assertEqual(self.http(server,'POST','/api/actions/session',body,good)[0],200)
        before=copy.deepcopy(app.sessions.read())
        self.assertEqual(self.http(server,'POST','/api/actions/session',json.dumps({'pool':['unknown'],'defaults':{}}),good)[0],400)
        self.assertEqual(app.sessions.read(),before)

    def test_actual_flow_request_hook_freezes_account_model_project_and_enforces_cap(self):
        from pilot import ROOT,Pilot,read,write,Blocked
        from permissions import Grants
        from account_catalog import discover
        import execution as ex
        import image_pipeline
        import b2_bridge
        from PIL import Image
        for name in ('schemas','scripts','assets/characters/channel-mascot'):shutil.copytree(ROOT/name,self.root/name)
        cfg=read(ROOT/'config.json');cfg['brief_policies']=[];cfg['flow_require_ui_evidence']=False
        cfg['flow_management_store']=str(self.root/'budgets');cfg['flow_tool_url']='https://flow.google.com/project/QA-FIXTURE/tool/QA-FIXTURE';write(self.root/'config.json',cfg)
        (self.root/'.gflow/Default').mkdir(parents=True)
        p=Pilot(self.root);self.addCleanup(p.db.close)
        job='qa-flow-job';sent=[]
        with patch('pathlib.Path.home',return_value=self.root/'fake-home'):
            accounts=discover(system_root=self.root)['accounts'];account=next(x for x in accounts if x['service']=='flow')
            profile=(Path(account['metadata_root'])/account['profile']).resolve()
            chosen=Sessions(self.root).select([account['id']],{'flow':account['id']},known=accounts)
            grant=Grants(self.root).grant('production',source='QA synthetic instruction',jobs=[job])
            ex.new(p,job,read(ROOT/'examples/m1/brief.json'),'auto',grant['id'],session_id=chosen['session_id'])
            content=read(ROOT/'examples/story-v3/content.json')
            ex.author(p,job,'outline',{'outline':content['outline']},'QA synthetic author');ex.advance(p,job)
            ex.author(p,job,'dialogue',content,'QA synthetic author');ex.advance(p,job,'dialogue')
            ledger=Budgets(self.root/'budgets');ledger.bind_identity(account['id'],'qa-google-identity','QA synthetic identity')
            connection={'status':'connected','identity':{'observedProfile':str(profile),'executable':'QA synthetic browser','verifiedAt':'QA','toolUrl':cfg['flow_tool_url']}}
            def fake_backend(command,**kwargs):
                self.assertTrue(command.startswith('tool-snapshot:queue:'))
                specs=json.loads(Path(command[len('tool-snapshot:queue:'):]).read_text());sent.extend(specs);items=[]
                if any('QA synthetic timeout' in spec['prompt'] for spec in specs):raise Blocked('QA synthetic timeout after queue send')
                if any('QA synthetic quota' in spec['prompt'] for spec in specs):return {'status':'blocked','reason':'Quota exceeded: QA synthetic provider capacity','generationSubmitted':False}
                for spec in specs:
                    folder=Path(spec['outDir']);folder.mkdir(parents=True,exist_ok=True);image=folder/'qa-synthetic.png'
                    Image.new('RGB',(360,640),(140,200,220)).save(image)
                    items.append({'request_id':spec['testCase'],'path':str(image),'media_id':'QA-SYNTHETIC-MEDIA','screenshot':None})
                return {'status':'completed','items':items}
            with patch.object(b2_bridge,'ROOT',self.root),patch.object(b2_bridge,'require_queue_acceptance'),patch.object(b2_bridge,'ensure_connected',return_value=connection),patch.object(b2_bridge,'send_raw_command',side_effect=fake_backend):
                frozen_model=cfg['flow_model'];frozen_project=cfg['flow_project']
                live=copy.deepcopy(cfg);live['flow_model']='QA WRONG GLOBAL MODEL';live['flow_project']='QA-WRONG-GLOBAL-PROJECT';write(self.root/'config.json',live)
                with ex.lease(p,job):first=image_pipeline.request(p,job,'ref:QA-ISOLATED','QA synthetic first reference prompt')
                self.assertEqual(first['state'],'downloaded');self.assertEqual(len(sent),1)
                self.assertEqual(sent[0]['model'],frozen_model);self.assertEqual(sent[0]['project'],frozen_project)
                pinned=Sessions(self.root).read()['pins'][first['key']]
                self.assertEqual(pinned['account'],account['id']);self.assertEqual(pinned['session'],chosen['session_id'])
                counted=ledger.snapshot(account['id'])['flow'];self.assertEqual(sum(v['slots'] for v in counted.values()),1)
                connection['identity']['observedProfile']=str(self.root/'wrong-profile')
                with ex.lease(p,job):
                    with self.assertRaisesRegex(Blocked,'PROFILE_MISMATCH'):image_pipeline.request(p,job,'ref:QA-WRONG-PROFILE','QA synthetic wrong profile')
                connection['identity']['observedProfile']=str(profile);connection['identity']['toolUrl']='https://flow.google.com/project/WRONG/tool/WRONG'
                with ex.lease(p,job):
                    with self.assertRaisesRegex(Blocked,'PROJECT_MISMATCH'):image_pipeline.request(p,job,'ref:QA-WRONG-PROJECT','QA synthetic wrong project')
                connection['identity']['toolUrl']=cfg['flow_tool_url']
                self.assertEqual(len(sent),1)
                with ex.lease(p,job):
                    with self.assertRaisesRegex(Blocked,'timeout'):image_pipeline.request(p,job,'ref:QA-TIMEOUT','QA synthetic timeout')
                with ex.lease(p,job):
                    with self.assertRaisesRegex(Blocked,'AMBIGUOUS'):image_pipeline.request(p,job,'ref:QA-TIMEOUT','QA synthetic changed timeout prompt')
                self.assertEqual(len(sent),2)
                counted=ledger.snapshot(account['id'])['flow'];self.assertEqual(sum(v['slots'] for v in counted.values()),2)
                self.assertTrue(any(r['state'] in ('unknown','ambiguous') for op in counted.values() for r in op['requests'].values()))
                ledger.flow_submit(account['id'],chosen['session_id'],'qa-other-slots',98,budget_session=chosen['session_id'],evidence='QA synthetic additional sent slots')
                with ex.lease(p,job):
                    with self.assertRaises(Blocked):image_pipeline.request(p,job,'ref:QA-ISOLATED','QA synthetic changed reference prompt')
                self.assertEqual(len(sent),2)
                ledger.flow_state(account['id'],chosen['session_id'],'qa-other-slots','not_submitted','QA synthetic confirmed not sent')
                with ex.lease(p,job):
                    with self.assertRaisesRegex(Blocked,'[Qq]uota'):image_pipeline.request(p,job,'ref:QA-QUOTA','QA synthetic quota before send')
                self.assertEqual(len(sent),3)
                with ex.lease(p,job):
                    with self.assertRaises(Blocked):image_pipeline.request(p,job,'ref:QA-AFTER-QUOTA','QA synthetic another request after quota')
                self.assertEqual(len(sent),3)
                self.assertIn('flow',ledger.snapshot(account['id'])['blocks'])

    def test_english_portrait_adapter_audio_cues_timeline_and_remote_render(self):
        """Run DSP/worker logic with fake model/GPU/encoder; no remote quality claim."""
        from pilot import ROOT, read, write
        import adapters
        import numpy as np
        from colab_bridge import worker
        from colab_bridge.job_worker import run
        from colab_bridge.job_protocol import bundle
        from colab_bridge.protocol import validate_result
        import jsonschema
        for name in ('assets/voices','renderer','scripts'): shutil.copytree(ROOT/name,self.root/name)
        for name in ('config.json','audio_processing.py','media_packaging.py','output_contract.py','package.json','package-lock.json'):shutil.copy2(ROOT/name,self.root/name)
        cfg=read(self.root/'config.json');cfg['colab_tts']['enabled']=True;write(self.root/'config.json',cfg)
        job=self.root/'runs/synthetic-english';job.mkdir(parents=True)
        (job/'image.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl6AAAAAASUVORK5CYII='))
        brief={'aspect_ratio':'9:16','language':'en','outputs':[{'aspect_ratio':'9:16','language':'en','subtitles':True,'voice':'alba','speed':.87}]}
        text='I see a predator.'
        content={'schema_version':'3.0','scenes':[{'id':'SC01','title':'Synthetic scene','narration':'WRONG VI TRACK MUST NOT WIN',
                 'narration_en':text,'audio_direction':{'en':{'learner_pause_seconds':.75}},
                 'beats':[{'id':'BT01','image_id':'IM01','anchor':{'en':{'quote':'I','occurrence':1}},'effect':'hold','focus':{'x':.5,'y':.5}}]}]}
        data={'content':content,'images':{'items':[{'scene_id':'SC01','image_id':'IM01','ratio':'9:16','path':'image.png'}]}}
        p=types.SimpleNamespace(root=self.root,job=lambda _:job,brief=lambda _:(brief,1,'synthetic-hash'),payload=lambda _,m:data[m],path=lambda _,name:job/name)
        generated=[]
        def generate(**kw):generated.append(kw);return [(.2*np.sin(np.arange(12000)*.03)).astype(np.float32) for _ in kw['text']]
        class OOM(Exception):pass
        fake_torch=types.SimpleNamespace(Tensor=type('Tensor',(),{}),float16='synthetic-float16',manual_seed=lambda _:None,
            cuda=types.SimpleNamespace(is_available=lambda:True,get_device_name=lambda _:'QA SYNTHETIC Tesla T4',empty_cache=lambda:None,OutOfMemoryError=OOM))
        model=types.SimpleNamespace(from_pretrained=lambda *_a,**_k:types.SimpleNamespace(create_voice_clone_prompt=lambda **kw:kw,generate=generate))
        modules={'torch':fake_torch,'omnivoice':types.SimpleNamespace(OmniVoice=model),'huggingface_hub':types.SimpleNamespace(snapshot_download=lambda model,revision:model)}
        seen={}
        def synthesize(client,request,out,cache,**kwargs):
            seen['audio']=request
            remote=copy.deepcopy(request)
            for profile in remote['profiles'].values():profile['remote_wav']=profile.pop('local_wav')
            for support in remote['support_files']:
                shutil.copy2(support.pop('local_path'),out.parent/support['name']);support['remote_path']=str(out.parent/support['name'])
            path=out.parent/'request.json';write(path,remote)
            worker._MODEL=None;worker._MODEL_KEY=None;worker._PROMPTS={}
            with patch.dict(sys.modules,modules):worker.run(path,out)
            validate_result(out,request)
        def render(client,request,out,cache,**kwargs):
            seen['render']=request;archive=out.parent/'render-input.zip';bundle(request,archive)
            def invoke(argv,**kw):
                if argv[0]=='node':
                    dest=Path(argv[-1]);(dest/'video.mp4').write_bytes(b'\0\0\0\x18ftypisomQA-SYNTHETIC-ENCODER')
                    write(dest/'layout.json',{'passed':True})
            def probe_fake(argv,**kw):
                if argv[0]=='nvidia-smi':return 'QA SYNTHETIC Tesla T4\n'
                if argv[0]=='node':return '/usr/bin/true\n'
                return json.dumps({'format':{'duration':str(data['audio']['duration'])},'streams':[{'codec_type':'video','codec_name':'h264','width':1080,'height':1920},{'codec_type':'audio','codec_name':'aac'}]})
            with patch('colab_bridge.job_worker.subprocess.run',side_effect=invoke),patch('colab_bridge.job_worker.subprocess.check_output',side_effect=probe_fake):
                run(archive,out,request['request_id'],request['worker_sha256'])
            validate_render_result(out,request)
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch('adapters.retakes',return_value={}))
            stack.enter_context(patch('adapters.master',side_effect=AssertionError('Desktop master forbidden')))
            stack.enter_context(patch('colab_bridge.client.cli',return_value='/bin/true'))
            stack.enter_context(patch('colab_bridge.accounts.STORE',self.root/'synthetic-empty-auth'))
            stack.enter_context(patch('colab_bridge.client.Client.synthesize',synthesize))
            stack.enter_context(patch('colab_bridge.client.Client.render',render))
            audio_out=job/'audio';audio_out.mkdir();data['audio']=adapters.audio(p,'synthetic-english',audio_out)
            jsonschema.validate(data['audio'],read(ROOT/'schemas/audio.json'))
            video_out=job/'render';video_out.mkdir();result=adapters.render(p,'synthetic-english',video_out)
        self.assertEqual(set(data['audio']['tracks']),{'en'})
        self.assertEqual(seen['audio']['items'][0]['text'],text);self.assertEqual(seen['audio']['items'][0]['speed'],.87)
        self.assertEqual(generated[0]['speed'],[.87]);self.assertEqual(result['language'],'en')
        props=read(video_out/'props.json');track=props['tracks']['en']
        self.assertEqual(track['audioSrc'],'en.wav');self.assertEqual(track['cues'][0]['text'],text)
        self.assertEqual(track['scenesByAspect']['9:16'][0]['end'],data['audio']['duration'])
        self.assertNotIn('vi',props['tracks']);self.assertEqual(seen['render']['brief']['outputs'],brief['outputs'])
        write(ROOT/'reports/normalization/qa-remote-web-chain.json',{'fixture':True,'live_provider':False,'actual_remote':False,
            'text':text,'language':'en','aspect_ratio':'9:16','speed':.87,'waveform_seconds':data['audio']['duration'],
            'cues':track['cues'],'timeline_end':track['scenesByAspect']['9:16'][0]['end'],'audio_schema_passed':True,'fake_encoder':True})


@unittest.skipUnless(os.environ.get('VP_PLAYWRIGHT_MODULE'), 'Explicit installed browser dependencies required')
class IndependentBrowserEngine(unittest.TestCase):
    def test_actual_node_frozen_send_contract_and_unknown_replay(self):
        from pilot import ROOT,write
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);experiment=root/'sys/experiments/b2_illustrator';experiment.mkdir(parents=True)
            (experiment/'results').mkdir()
            for name in ('queue-runner.mjs','controller.mjs','attempt-store.mjs'):shutil.copy2(ROOT/'experiments/b2_illustrator'/name,experiment/name)
            (root/'node_modules').symlink_to(Path(os.environ['VP_PLAYWRIGHT_MODULE']).parent)
            write(root/'sys/config.json',{'flow_model':'QA WRONG GLOBAL MODEL','flow_tool_url':'https://flow.google.com/project/QA-FIXTURE/tool/QA-FIXTURE'})
            result=subprocess.run(['node',str(ROOT/'tests/qa-remote-web-node-contract.mjs'),str(root)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(result.stdout);self.assertTrue(report['frozen_model_selected']);self.assertTrue(report['unknown_no_duplicate_start'])
            write(ROOT/'reports/normalization/qa-remote-web-node-contract.json',report)

    def test_eight_tabs_modes_revision_change_and_actual_media(self):
        from pilot import ROOT, Pilot, observe_job, read, write
        import execution as ex
        from permissions import Grants
        from contextlib import ExitStack
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ('schemas','scripts','assets/characters/channel-mascot'): shutil.copytree(ROOT/name,root/name)
            cfg=read(ROOT/'config.json');cfg['brief_policies']=[];write(root/'config.json',cfg)
            p=Pilot(root)
            try:
                job='qa-browser-job';grant=Grants(root).grant('production',source='QA synthetic isolated instruction',jobs=[job])
                ex.new(p,job,read(ROOT/'examples/m1/brief.json'),'auto',grant['id'])
                content=read(ROOT/'examples/story-v3/content.json')
                ex.author(p,job,'outline',{'outline':content['outline']},'QA synthetic author');ex.advance(p,job)
                ex.author(p,job,'dialogue',content,'QA synthetic author')
                movie=root/'qa-synthetic.mp4'
                subprocess.run(['ffmpeg','-y','-f','lavfi','-i','color=c=gray:s=64x96:r=10:d=1','-f','lavfi','-i','anullsrc=r=8000:cl=mono','-t','1','-c:v','libx264','-c:a','aac','-shortest',str(movie)],capture_output=True,check=True)
                def audio(pilot,j,out):
                    f=out/'qa-synthetic.wav'
                    with wave.open(str(f),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*8000)
                    return {'wav':str(f.relative_to(pilot.job(j))),'language':'vi','fixture':True}
                def images(pilot,j,out):
                    f=out/'qa-synthetic.png';f.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl6AAAAAASUVORK5CYII='))
                    gallery=out/'gallery.json';write(gallery,{'items':[{'file':str(f.relative_to(pilot.job(j)))}],'fixture':True})
                    return {'checkpoint':'final','references':[],'items':[{'scene_id':'SC01','image_id':'IM01','ratio':'9:16','path':str(f.relative_to(pilot.job(j))),'actual_prompt':'QA synthetic image prompt; no provider generation'}],'proofs':[],'contact_sheet':None,'gallery':str(gallery.relative_to(pilot.job(j)))}
                def render(pilot,j,out):
                    f=out/'qa-synthetic.mp4';shutil.copy2(movie,f);return {'video':str(f.relative_to(pilot.job(j))),'fixture':True}
                with ExitStack() as st:
                    st.enter_context(patch('execution.runtime_ready',return_value={'fixture':True}))
                    st.enter_context(patch('adapters.audio',side_effect=audio));st.enter_context(patch('image_pipeline.produce',side_effect=images));st.enter_context(patch('adapters.render',side_effect=render))
                    st.enter_context(patch('image_pipeline.check',side_effect=lambda pilot,j,data:[data['gallery']]))
                    st.enter_context(patch.object(p,'remote_checks',side_effect=lambda j,m,data:[data['wav' if m=='audio' else 'video']]))
                    ex.advance(p,job)
                    def public_cli(argv):
                        code='import sys,json;sys.path.insert(0,sys.argv[1]);import pilot;from pathlib import Path;pilot.ROOT=Path(sys.argv[2]);sys.argv=["pilot.py",*json.loads(sys.argv[3])];raise SystemExit(pilot.main())'
                        response=subprocess.run([sys.executable,'-c',code,str(ROOT),str(root),json.dumps(argv)],capture_output=True,text=True,timeout=30)
                        return json.loads(response.stdout)
                    app=Dashboard(root,home=root/'empty-home',cli=public_cli);server=make_server(root,dashboard=app)
                    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                    try:
                        results=[]
                        for mode,revisions in (('auto',(1,2)),('review',(2,3))):
                            if ex.settings(p,job)['mode']!=mode: ex.change_mode(p,job,mode,'QA synthetic explicit mode instruction')
                            for revision in revisions:
                                if mode=='auto' and revision==2:
                                    ex.reject(p,job,'audio',1,'QA synthetic version update');ex.advance(p,job)
                                if mode=='review' and revision==3:
                                    for earlier in ('outline','dialogue'):
                                        ex.approve(p,job,earlier,ex.current(p,job,earlier)['revision'],'QA synthetic prior-output review after explicit mode change')
                                    ex.reject(p,job,'audio',2,'QA synthetic second version update')
                                    for phase in ('audio','images','video'):
                                        step=ex.advance(p,job);self.assertEqual(step['phase'],phase)
                                        if phase!='video':ex.approve(p,job,phase,ex.current(p,job,phase)['revision'],'QA synthetic approval for independent browser update')
                                run=subprocess.run(['node',str(ROOT/'tests/qa-remote-web-browser.mjs'),f'http://127.0.0.1:{server.server_port}',mode,str(revision)],capture_output=True,text=True,timeout=55)
                                self.assertEqual(run.returncode,0,run.stderr);results.append(json.loads(run.stdout))
                        write(ROOT/'reports/normalization/qa-remote-web-browser.json',{'live_provider':False,'fixtures':True,'runs':results})
                    finally:server.shutdown();server.server_close();thread.join(2)
            finally:p.db.close()


if __name__ == '__main__': unittest.main()
