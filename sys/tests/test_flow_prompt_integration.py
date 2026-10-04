"""Official CLI→engine→real adapter→fake B2 boundary, no provider/media claim."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from account_budget import Budgets
from account_catalog import discover
from pilot import ROOT, Pilot, read, write, Blocked, hashobj
from session_store import Sessions
import b2_bridge
import execution as ex
import image_pipeline
from flow_management import config, prompt_pin
from flow_prompts import compile_pinned


class FlowPromptIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for name in ('schemas','scripts'):shutil.copytree(ROOT/name,self.root/name)
  mascot_dir = self.root / 'assets/characters/channel-mascot'; mascot_dir.mkdir(parents=True, exist_ok=True)
  Image.new('RGB', (30, 30), '#8CCFE8').save(mascot_dir / 'reference-v1.png')
  write(mascot_dir / 'character.json', {'name': 'channel-mascot', 'media_id': 'de94a39b-155f-4afe-acbb-d9d4b59ad532'})
  self.cfg=read(ROOT/'config.json');self.cfg['brief_policies']=[];self.cfg['flow_require_ui_evidence']=False;self.cfg['flow_management_store']=str(self.root/'budgets');self.cfg['flow_tool_url']='https://flow.google.com/project/FIXTURE/tool/FIXTURE';self.cfg['flow_prompt_version']='1.0.0';write(self.root/'config.json',self.cfg)
  (self.root/'.gflow/Default').mkdir(parents=True)
  self.home=patch('pathlib.Path.home',return_value=self.root/'fake-home');self.home.start();self.addCleanup(self.home.stop)
  accounts=discover(system_root=self.root)['accounts'];self.account=next(item for item in accounts if item['service']=='flow');self.profile=(Path(self.account['metadata_root'])/self.account['profile']).resolve();self.session=Sessions(self.root).select([self.account['id']],{'flow':self.account['id']},known=accounts)
  self.ledger=Budgets(self.root/'budgets');self.ledger.bind_identity(self.account['id'],'fixture-google','TEST explicit identity')
  self.job='template-fixture';self.sent=[];self.connection={'status':'connected','identity':{'observedProfile':str(self.profile),'executable':'TEST browser','verifiedAt':'TEST','toolUrl':self.cfg['flow_tool_url']}}
 def cli_new(self):
  brief=self.root/'brief.json';write(brief,read(ROOT/'examples/m1/brief.json'))
  code='import sys; import pilot; from pathlib import Path; pilot.ROOT=Path(sys.argv.pop(1)); pilot.main()'
  result=subprocess.run([sys.executable,'-c',code,str(self.root),'new',self.job,'--brief',str(brief),'--mode','auto','--source','TEST authorized CLI fixture job'],cwd=ROOT,capture_output=True,text=True,timeout=20)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
  self.p=Pilot(self.root);self.addCleanup(self.p.db.close)
  content=read(ROOT/'examples/story-v3/content.json');ex.author(self.p,self.job,'outline',{'outline':content['outline']},'TEST connected author');ex.advance(self.p,self.job);ex.author(self.p,self.job,'dialogue',content,'TEST connected author');ex.advance(self.p,self.job,'dialogue')
 def backend(self,command,**kwargs):
  self.assertTrue(command.startswith('tool-snapshot:queue:'));specs=read(Path(command[len('tool-snapshot:queue:'):]));self.sent.extend(specs);items=[]
  for spec in specs:
   folder=Path(spec['outDir']);folder.mkdir(parents=True,exist_ok=True);image=folder/'fixture.png';Image.new('RGB',(360,640),(140+len(self.sent),200,220)).save(image)
   items.append({'request_id':spec['testCase'],'path':str(image),'forge_id':'00000000-0000-4000-8000-'+str(len(self.sent)).zfill(12),'media_id':'00000000-0000-4000-8000-'+str(len(self.sent)).zfill(12),'screenshot':None})
  return {'status':'completed','items':items}
 def transport(self):
  from contextlib import ExitStack
  stack=ExitStack();stack.enter_context(patch.object(b2_bridge,'ROOT',self.root));stack.enter_context(patch.object(b2_bridge,'require_queue_acceptance'));stack.enter_context(patch.object(b2_bridge,'ensure_connected',return_value=self.connection));stack.enter_context(patch.object(b2_bridge,'send_raw_command',side_effect=self.backend));return stack
 def test_cli_new_freezes_before_send_real_adapter_passes_compiled_pin_model_and_guards(self):
  self.cli_new();pin=prompt_pin(self.p,self.job);self.assertEqual(pin['version'],'1.0.0');self.assertTrue((self.p.job(self.job)/'flow/prompts/pin.json').is_file());self.assertEqual(self.p.db.execute("SELECT count(*) FROM events WHERE job=? AND event='flow_prompt_frozen'",(self.job,)).fetchone()[0],1)
  cfg=copy.deepcopy(self.cfg);cfg['flow_prompt_version']='99.0.0';cfg['flow_model']='WRONG FUTURE GLOBAL';cfg['new_policy']='must not leak';write(self.root/'config.json',cfg)
  self.assertNotIn('new_policy',config(self.p,self.job));self.assertEqual(config(self.p,self.job)['flow_prompt_version'],'1.0.0')
  import flow_management
  with self.transport(),patch('flow_management.before_send',wraps=flow_management.before_send) as guard:
   with ex.lease(self.p,self.job):result=image_pipeline.request(self.p,self.job,'ref:CH01','The canonical single mascot full-body reference on a bright plain background.')
  self.assertEqual(result['state'],'downloaded');self.assertEqual(len(self.sent),1);self.assertEqual(guard.call_count,1);record=result['identity']['prompt_template'];self.assertEqual(record['pin'],pin);self.assertEqual(record['purpose'],'character');self.assertEqual(self.sent[0]['prompt'],compile_pinned(pin,'character',record['data'])['prompt']);self.assertEqual(self.sent[0]['model'],pin['model']);self.assertEqual(self.sent[0]['charMediaId'],'de94a39b-155f-4afe-acbb-d9d4b59ad532');self.assertEqual(Sessions(self.root).read()['pins'][result['key']]['account'],self.account['id'])
  before=(self.p.path(self.job,result['journal'])).read_bytes()
  with self.transport(),ex.lease(self.p,self.job):again=image_pipeline.request(self.p,self.job,'ref:CH01','The canonical single mascot full-body reference on a bright plain background.')
  self.assertEqual(again['key'],result['key']);self.assertEqual(len(self.sent),1);self.assertEqual(self.p.path(self.job,result['journal']).read_bytes(),before)
 def test_cast_version_sends_without_mascot_or_character_slot(self):
  cfg=copy.deepcopy(self.cfg);cfg['flow_prompt_version']='1.1.0';write(self.root/'config.json',cfg);self.cli_new();pin=prompt_pin(self.p,self.job);self.assertEqual(pin['version'],'1.1.0')
  with self.transport(),ex.lease(self.p,self.job):result=image_pipeline.request(self.p,self.job,'ref:CH01','Three anonymous stick figures in different costumes on a plain background.')
  self.assertEqual(result['state'],'downloaded');self.assertEqual(len(self.sent),1);record=result['identity']['prompt_template'];self.assertNotIn('character_reference',record['data']);self.assertIsNone(record['provenance']['references']['character'])
  sent=self.sent[0];self.assertFalse(sent.get('characterRefPath'));self.assertFalse(sent.get('charMediaId'));self.assertIs(sent.get('useCharacterRef'),False);self.assertNotIn('#8CCFE8',sent['prompt']);self.assertIn('No main character, presenter or recurring protagonist',sent['prompt'])
 def test_legacy_downloaded_request_does_not_inherit_template_or_resubmit(self):
  cfg=copy.deepcopy(self.cfg);cfg.pop('flow_prompt_version',None);write(self.root/'config.json',cfg);self.cli_new();self.assertIsNone(prompt_pin(self.p,self.job))
  with self.transport(),ex.lease(self.p,self.job):first=image_pipeline.request(self.p,self.job,'ref:CH01','TEST unchanged legacy generic reference')
  path=self.p.path(self.job,first['journal']);before=path.read_bytes();actual=first['identity']['actual_prompt'];key=first['key']
  cfg['flow_prompt_version']='1.0.0';cfg['future_global_key']='new policy';write(self.root/'config.json',cfg)
  with self.transport(),ex.lease(self.p,self.job):second=image_pipeline.request(self.p,self.job,'ref:CH01','TEST unchanged legacy generic reference')
  self.assertEqual(path.read_bytes(),before);self.assertEqual(second['key'],key);self.assertEqual(second['identity']['actual_prompt'],actual);self.assertNotIn('prompt_template',second['identity']);self.assertEqual(len(self.sent),1);self.assertNotIn('flow_prompt_version',config(self.p,self.job))
 def test_scene_batch_and_variation_share_compiler_exact_text_real_reference_hashes(self):
  self.cli_new()
  with self.transport(),ex.lease(self.p,self.job):reference=image_pipeline.request(self.p,self.job,'ref:CH01','TEST canonical source reference')
  original={'character_id':'CH01','sha256':reference['sha256'],'name':'test-mascot','prompt':'TEST canonical source reference','path':reference['path']}
  approved={'payload':{'references':[original]}}
  with self.transport(),patch('image_pipeline.approved',return_value=approved),ex.lease(self.p,self.job):registered=image_pipeline.register(self.p,self.job,original)
  units=[{'id':'SC01_I1_9x16','image_id':'SC01_I1','scene_id':'SC01','ratio':'9:16','prompt':'TEST mascot points at a bird taking a seed.','character_ids':['CH01'],'based_on':None,'visible_text':[{'text':'I took one seed.','placement':'upper left','object':'speech bubble'}]}]
  with self.transport(),patch('image_pipeline.approved',return_value=approved),patch('image_pipeline.planned_units',return_value=units),ex.lease(self.p,self.job):
   plan=image_pipeline._plan_request(self.p,self.job,units[0]['id'],units[0]['prompt'],[registered],None,None)
   image_pipeline.batch_submit(self.p,self.job,units,{'CH01':registered})
   first=image_pipeline.request(self.p,self.job,units[0]['id'],units[0]['prompt'],[registered])
  self.assertEqual(first['key'],plan[-1]);self.assertEqual(first['identity'],plan[-2]);self.assertEqual(first['identity']['prompt_template']['purpose'],'scene');self.assertEqual(first['identity']['prompt_template']['data']['allowed_text'],units[0]['visible_text']);self.assertEqual(self.sent[-1]['prompt'],first['identity']['actual_prompt']);self.assertEqual(first['identity']['prompt_template']['data']['character_reference']['sha256'],registered['registration_hash']);self.assertEqual(len(self.sent),3)
  variable=copy.deepcopy(units[0]);variable.update(id='SC01_I2_9x16',image_id='SC01_I2',based_on=units[0]['id'],prompt='TEST same bowl: the bird now holds the seed.')
  current=copy.deepcopy(image_pipeline.content(self.p,self.job));current['scenes'][0]['images'].append({'id':'SC01_I2','preserve':'Keep camera and bowl fixed.','change':'Move the seed from bowl to bird.'})
  base={'target':units[0]['id'],'path':first['path'],'sha256':first['sha256']}
  with self.transport(),patch('image_pipeline.approved',return_value=approved),patch('image_pipeline.planned_units',return_value=[units[0],variable]),patch('image_pipeline.content',return_value=current),ex.lease(self.p,self.job):second=image_pipeline.request(self.p,self.job,variable['id'],variable['prompt'],[registered],base_image=base)
  compiled=second['identity']['prompt_template'];self.assertEqual(compiled['purpose'],'variation');self.assertEqual(compiled['data']['base_reference']['sha256'],first['sha256']);self.assertEqual(self.sent[-1]['baseMediaId'],compiled['data']['base_reference']['media_id']);self.assertEqual(len(self.sent),4)
 def test_callback_denies_actual_prompt_tamper_before_fake_socket_send(self):
  self.cli_new()
  import flow_management
  original_guard=flow_management.before_send
  def tamper(p,job,folders,connection):
   path=Path(folders[0])/'request.json';record=read(path);record['identity']['actual_prompt']='Injected replacement prompt';write(path,record);return original_guard(p,job,folders,connection)
  with self.transport(),patch('flow_management.before_send',side_effect=tamper),ex.lease(self.p,self.job):
   with self.assertRaisesRegex(Blocked,'FLOW_TEMPLATE_RECORD_CHANGED'):image_pipeline.request(self.p,self.job,'ref:CH01','TEST canonical reference')
  self.assertFalse(self.sent);records=list((self.p.job(self.job)/'flow/attempts').glob('*/request.json'));self.assertEqual(read(records[0])['state'],'not_submitted')
 def test_missing_or_tampered_pin_denies_before_dispatch(self):
  self.cli_new();path=self.p.job(self.job)/'flow/prompts/pin.json';pin=read(path);write(path,{**pin,'registry_sha256':'0'*64})
  with self.transport(),ex.lease(self.p,self.job):
   with self.assertRaisesRegex(Blocked,'FLOW_TEMPLATE_PIN_CHANGED'):image_pipeline.request(self.p,self.job,'ref:CH01','TEST canonical reference')
  self.assertFalse(self.sent)

if __name__=='__main__':unittest.main()
