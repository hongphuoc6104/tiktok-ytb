"""Authorized setup controls and exact runtime bindings, no live providers."""
import copy
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from account_catalog import discover
from dashboard.data import Dashboard
from dashboard.server import make_server
from permissions import Grants, PermissionDenied
from session_store import Sessions

URL='https://flow.google.com/project/test-project/tool/test-tool'

class DashboardSetupTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.home=Path(self.tmp.name);self.root=self.home/'sys';self.root.mkdir()
  store=self.home/'.config/video-pilot/colab';(store/'profiles/account-02').mkdir(parents=True);(store/'accounts.json').write_text('{"preferred":"account-02","accounts":[{"id":"account-02"}]}')
  browser=self.home/'.config/google-chrome-cdp-profile4';(browser/'Profile 4').mkdir(parents=True);(browser/'Local State').write_text('{"profile":{"info_cache":{"Profile 4":{"name":"Work Profile"}}}}')
  self.binary=self.home/'chrome';self.binary.write_text('#!/bin/sh\nexit 0\n');self.binary.chmod(0o700)
  (self.root/'config.json').write_text('{"colab_tts":{"account":"auto","session":"wrong-global-session"},"flow_session_image_cap":150}')
  self.calls=[]
  def cli(argv):
   self.calls.append(argv);return {'job':argv[1],'version':4,'mode':'auto','grant_id':self.production,'checkpoints':[]}
  self.app=Dashboard(self.root,home=self.home,cli=cli,client_factory=self.client)
  self.grant=Grants(self.root).grant('setup',source='TEST authorized setup',paths=['.state/**','experiments/b2_illustrator/machine.local.json','runs/test-job/**'])['id']
  self.other=Grants(self.root).grant('setup',source='TEST wrong scope',paths=['unrelated/**'])['id']
  self.production=Grants(self.root).grant('production',source='TEST production',jobs=['test-job'],paths=['runs/test-job/**'])['id']
  self.flow=next(x['id'] for x in discover(self.home,self.root)['accounts'] if x['service']=='flow')
  self.app.sessions.select(['colab:account-02',self.flow],{'colab':'colab:account-02','flow':self.flow})
  self.app.budgets.bind_identity('colab:account-02','google:real-identity-fixture','TEST identity')
  self.app.budgets.bind_identity(self.flow,'google:flow-identity-fixture','TEST identity')
  self.provider=[];self.release=threading.Event();self.entered=threading.Event()
 def tearDown(self):self.release.set();self.tmp.cleanup()
 def data(self,**extra):return {'grant':self.grant,'source':'TEST actual setup instruction','account':'colab:account-02','runtime_session':'vp-normalization-20261003',**extra}
 def client(self,root,cfg):
  testcase=self
  class Client:
   account=cfg['colab_tts']['account'];session=cfg['colab_tts']['session']
   def start(self):testcase.provider.append(('start',self.account,self.session));testcase.entered.set();testcase.release.wait(2)
   def setup(self):testcase.provider.append(('setup',self.account,self.session));return 'secret token provider output must not escape'
   def stop(self):testcase.provider.append(('stop',self.account,self.session))
   def reconcile(self):testcase.provider.append(('reconcile',self.account,self.session))
   def synthesize(self,request,out,cache,collect_only):testcase.provider.append(('collect',self.account,self.session,collect_only))
   def render(self,request,out,cache,collect_only):testcase.provider.append(('collect-render',self.account,self.session,collect_only))
  return Client()
 def allocation(self,phase='allocated'):
  identity=self.app.budgets.read()['aliases']['colab:account-02'];key=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True).encode()).hexdigest();(self.app.budgets.path.parent/('allocation-'+key+'.json')).write_text(json.dumps({'account':'account-02','session':'vp-normalization-20261003','phase':phase,'allocation_started_at':100}))
 def finish(self,key):
  for _ in range(100):
   item=self.app.operations[key]
   if item['state']=='finished':return item['result']
   time.sleep(.01)
  self.fail('Operation did not finish')
 def test_http_setup_requires_grant_source_and_csrf(self):
  server=make_server(self.root,dashboard=self.app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   conn=HTTPConnection('127.0.0.1',server.server_port);conn.request('GET','/api/state');response=conn.getresponse();state=json.loads(response.read());conn.close()
   headers={'Origin':f'http://127.0.0.1:{server.server_port}','Content-Type':'application/json','X-VP-CSRF':state['csrf']}
   for data,expected in ((self.data(grant=self.production),403),(self.data(grant=self.other),403),(self.data(source=''),403)):
    conn=HTTPConnection('127.0.0.1',server.server_port);conn.request('POST','/api/actions/colab-start',json.dumps(data),headers);response=conn.getresponse();self.assertEqual(response.status,expected);response.read();conn.close()
   self.assertEqual(self.provider,[])
  finally:server.shutdown();server.server_close();thread.join()
 def test_permission_denies_setup_and_wrong_scope_before_provider(self):
  for grant in (self.production,self.other,None):
   with self.assertRaises(PermissionDenied):self.app.mutate('colab-start',self.data(grant=grant))
  self.assertEqual(self.provider,[])
 def test_exact_account_runtime_and_duplicate_async_operation(self):
  result=self.app.mutate('colab-start',self.data());self.assertTrue(self.entered.wait(1))
  with self.assertRaises(ValueError):self.app.mutate('colab-start',self.data())
  self.release.set();done=self.finish(result['operation']);self.assertEqual(done['runtime_session'],'vp-normalization-20261003');self.assertEqual(self.provider,[('start','account-02','vp-normalization-20261003')])
 def test_setup_original_runtime_and_no_raw_provider_output(self):
  self.allocation();result=self.app.mutate('colab-setup',self.data());done=self.finish(result['operation']);self.assertNotIn('secret',json.dumps(done));self.assertEqual(self.provider,[('setup','account-02','vp-normalization-20261003')])
  result=self.app.mutate('colab-stop',self.data(runtime_session='wrong'));done=self.finish(result['operation']);self.assertIn('blocked',done);self.assertEqual(len(self.provider),1)
 def test_reconcile_ambiguous_uses_original_owner(self):
  self.allocation('ambiguous');result=self.app.mutate('colab-reconcile',self.data());self.finish(result['operation']);self.assertEqual(self.provider,[('reconcile','account-02','vp-normalization-20261003')])
 def test_flow_plan_configure_and_start_use_shared_api_and_grant(self):
  data=self.data(account=self.flow,tool_url=URL,executable=str(self.binary))
  plan=self.app.mutate('flow-plan',data);self.assertEqual(plan['runtime_account'],self.flow);self.assertEqual(plan['tool_url'],URL)
  configured=self.app.mutate('flow-configure',data);self.assertEqual(configured['grant'],self.grant)
  with patch('profile_setup.start',return_value={'owned':True,'auth':'not_tested','endpoint':'DO-NOT-EXPOSE'}) as starter:
   operation=self.app.mutate('flow-start',data);result=self.finish(operation['operation']);self.assertNotIn('endpoint',result);starter.assert_called_once()
  with self.assertRaises(PermissionDenied):self.app.mutate('flow-configure',{**data,'grant':self.other})
 def test_readonly_flow_probe_has_scope_and_no_fake_provider_fallback(self):
  with patch('account_catalog.probe_flow',create=True,return_value={'auth':'verified','capability':'TEST fixture'} ) as probe:
   result=self.app.mutate('probe-flow',self.data(account=self.flow));done=self.finish(result['operation']);self.assertEqual(done['auth'],'verified');probe.assert_called_once_with(self.flow,system_root=self.root,home=self.home,budget_store=self.app.budgets.path.parent)
   with self.assertRaises(PermissionDenied):self.app.mutate('probe-flow',self.data(account=self.flow,grant=self.other))
  self.assertEqual(self.provider,[])
 def test_runtime_binding_frozen_per_job_and_request_pins_immutable(self):
  sessions=self.app.sessions;sessions.pin('request',job='test-job',service='colab',account='colab:account-02',session='old-original')
  sessions.bind_runtime('colab','colab:account-02','default-runtime',grant=self.grant,source='TEST binding',evidence='TEST request target')
  sessions.bind_runtime('colab','colab:account-02','job-runtime',grant=self.grant,source='TEST job binding',evidence='TEST allocated observed',job='test-job')
  frozen=copy.deepcopy(sessions.snapshot('test-job'));self.assertEqual(frozen['runtime_bindings']['colab']['runtime_session'],'job-runtime')
  sessions.bind_runtime('colab','colab:account-02','new-default',grant=self.grant,source='TEST changed target',evidence='TEST target')
  self.assertEqual(frozen['runtime_bindings']['colab']['runtime_session'],'job-runtime');self.assertEqual(sessions.snapshot('test-job')['runtime_bindings']['colab']['runtime_session'],'job-runtime');self.assertEqual(sessions.read()['pins']['request']['session'],'old-original')
  with self.assertRaises(PermissionDenied):sessions.bind_runtime('colab','colab:account-02','x',grant=self.other,source='TEST',evidence='TEST')
 def test_flow_target_frozen_and_rejects_credentials_tokens_wrong_profile(self):
  sessions=self.app.sessions;profile=str(self.home/'.config/google-chrome-cdp-profile4/Profile 4');target={'tool_url':URL,'profile_path':profile}
  binding=sessions.bind_runtime('flow',self.flow,'daemon-project-hash',grant=self.grant,source='TEST actual Flow target',evidence='TEST exact connected profile',job='test-job',target=target);frozen=sessions.snapshot('test-job');target['tool_url']='https://flow.google.com/project/other/tool/other';self.assertEqual(frozen['runtime_bindings']['flow']['target']['tool_url'],URL)
  before=copy.deepcopy(sessions.read())
  for invalid in ({'tool_url':'https://user:password@flow.google.com/project/test/tool/test','profile_path':profile},{'tool_url':URL+'?access_token=private','profile_path':profile},{'tool_url':URL,'profile_path':profile,'token':'private'},{'tool_url':URL,'profile_path':str(self.home/'other/Default')},{'tool_url':'https://external.example/project/test/tool/test','profile_path':profile}):
   with self.assertRaises(ValueError):sessions.bind_runtime('flow',self.flow,'new-daemon',grant=self.grant,source='TEST',evidence='TEST',target=invalid)
  self.assertEqual(sessions.read(),before)
 def test_job_binding_uses_official_bind_session(self):
  (self.root/'runs/test-job').mkdir(parents=True);result=self.app.mutate('bind-runtime',self.data(service='colab',job='test-job',evidence='TEST actual runtime observation'))
  self.assertIn(['bind-session','test-job','--session',self.app.sessions.read()['session_id'],'--source','TEST actual setup instruction'],self.calls)
  self.assertEqual(result['binding']['runtime_session'],'vp-normalization-20261003')
 def test_flow_image_count_separate_and_unresolved_other_session_stays_charged(self):
  session=self.app.sessions.read()['session_id'];b=self.app.budgets;b.flow_submit(self.flow,'job1','r1',3,cap=150,budget_session=session,evidence='TEST sent');b.flow_state(self.flow,'job1','r1','collected','TEST downloaded');b.flow_submit(self.flow,'oldjob','old',2,cap=150,budget_session='old-session',evidence='TEST sent');b.flow_state(self.flow,'oldjob','old','unknown','TEST timeout')
  account=next(x for x in self.app.snapshot()['inventory']['accounts'] if x['id']==self.flow);self.assertEqual(account['flow_usage']['charged'],5);self.assertEqual(account['flow_usage']['cap'],150);self.assertEqual(account['flow_usage']['states']['collected'],3);self.assertEqual(account['flow_usage']['states']['unknown'],2)
  js=(Path(__file__).parents[1]/'dashboard/static/app.js').read_text();self.assertIn("if(a.service==='colab')",js);self.assertIn('Ngân sách ảnh Flow',js);self.assertIn('colabControls',js);self.assertIn('flowControls',js)
 def test_render_collect_uses_exact_saved_revision_and_original_owner(self):
  request='b'*64;job=self.root/'runs/test-job';cache=job/'cache/colab-render'/request;cache.mkdir(parents=True);(cache/'state.json').write_text(json.dumps({'account':'account-02','session':'vp-normalization-20261003','phase':'ambiguous','request_id':request}));revision=job/'revisions/render/1';revision.mkdir(parents=True);(revision/'request-colab-render.json').write_text(json.dumps({'request_id':request,'operation':'render','worker_sha256':'TEST old saved worker'}))
  result=self.app.mutate('colab-collect',self.data(job='test-job',request=request));done=self.finish(result['operation']);self.assertEqual(done['operation'],'collect');self.assertEqual(self.provider,[('collect-render','account-02','vp-normalization-20261003',True)])
 def test_collect_is_exact_journal_only_and_job_scope(self):
  request='a'*64;path=self.root/'runs/test-job/remote-cache'/request;path.mkdir(parents=True);(path/'state.json').write_text(json.dumps({'account':'account-02','session':'vp-normalization-20261003','phase':'ambiguous'}));(path/'request.json').write_text(json.dumps({'request_id':request,'operation':'synthesize'}))
  result=self.app.mutate('colab-collect',self.data(job='test-job',request=request));done=self.finish(result['operation']);self.assertEqual(done['operation'],'collect');self.assertEqual(self.provider,[('collect','account-02','vp-normalization-20261003',True)])
  result=self.app.mutate('colab-collect',self.data(job='test-job',request='../bad'));self.assertIn('blocked',self.finish(result['operation']));self.assertEqual(len(self.provider),1)

if __name__=='__main__':unittest.main()
