"""M1 behavioral acceptance tests. All approvals here are test fixtures."""
import copy,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,ROOT,Blocked,read,write
from content_contract import ContractError

class ContentV2Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for n in ['schemas','.agents','renderer','tests','examples','scripts','assets']:shutil.copytree(ROOT/n,self.root/n)
  for n in ['pilot.py','workflow.py','machine_review.py','image_pipeline.py','characters.py','prompt_templates.py','content_contract.py','adapters.py','config.json','AGENTS.md','GEMINI.md']:shutil.copy(ROOT/n,self.root/n)
  self.p=Pilot(self.root);self.b=read(ROOT/'examples/m1/brief.json');self.p.new('m1',self.b)
  self.p.approve('m1','control',1,'TEST ONLY control approval')
  self.d=self.draft('m1')
 def tearDown(self):self.p.db.close();self.tmp.cleanup()
 def draft(self,j):
  d=read(ROOT/'examples/m1/content.json');b,rev,h=self.p.brief(j)
  d.update(brief_revision=rev,brief_hash=h);write(self.p.job(j)/'draft/content.json',d);return d
 def submit(self,d=None):
  write(self.p.job('m1')/'draft/content.json',d or self.d);self.p.run('m1','content')
 def approved(self):self.submit();self.p.approve('m1','content',1,'TEST ONLY content approval')
 def invalid(self,d,code):
  with self.assertRaises(ContractError) as ctx:self.submit(d)
  self.assertIn(code,{e['code'] for e in ctx.exception.errors})
 def test_T01_valid_review(self):
  self.submit();self.assertEqual(self.p.next('m1')['action'],'review');self.assertTrue(self.p.validate('m1','content')['passed'])
  e=read(self.p.path('m1',self.p.rows('m1')['content']['envelope']));self.assertEqual(len(e['files']),3)
 def test_T02_missing_fields(self):
  for key in ['goal','duration','required_points']:
   b=copy.deepcopy(self.b);del b[key]
   with self.subTest(key=key),self.assertRaises(ContractError) as c:self.p.new('bad',b)
   self.assertIn(key,str(c.exception));self.assertFalse(self.p.job('bad').exists())
 def test_T03_scene_count_and_duplicate(self):
  for duplicate in [False,True]:
   d=copy.deepcopy(self.d)
   if duplicate:d['scenes'][1]['id']='SC01'
   else:d['scenes'].pop()
   with self.subTest(duplicate=duplicate):self.invalid(d,'SCENES')
 def test_T04_coverage_missing(self):
  d=copy.deepcopy(self.d);d['coverage'].pop();self.invalid(d,'COVERAGE')
 def test_T05_false_quote(self):
  d=copy.deepcopy(self.d);d['coverage'][0]['quote']='Không có câu này';self.invalid(d,'QUOTE')
 def test_T06_unknown_character(self):
  d=copy.deepcopy(self.d);d['scenes'][0]['character_ids']=['UNKNOWN'];self.invalid(d,'CHARACTER_REF')
 def test_T07_missing_fields_and_artifact(self):
  for key in ['narration','prompt']:
   d=copy.deepcopy(self.d);del d['scenes'][0][key];self.invalid(d,'SCHEMA')
  self.submit();r=self.p.rows('m1')['content'];e=read(self.p.path('m1',r['envelope']));self.p.path('m1',e['files'][0]).unlink()
  with self.assertRaises(Blocked):self.p.approve('m1','content',r['revision'],'TEST')
  self.assertEqual(self.p.rows('m1')['content']['state'],'stale')
 def test_T08_changed_brief_fields(self):
  for key,value in [('topic','Other'),('duration',{'min_seconds':20,'max_seconds':30}),('required_points',['Other'])]:
   d=copy.deepcopy(self.d);d[key]=value
   with self.subTest(key=key):self.invalid(d,'BRIEF_MISMATCH')
 def test_T09_old_brief_revision(self):
  self.submit();b=copy.deepcopy(self.b);b['goal']='Mục tiêu mới';self.p.revise_brief('m1',b,'TEST explicit new brief')
  with self.assertRaises(Blocked):self.p.approve('m1','content',1,'TEST old')
  self.invalid(self.d,'BRIEF_VERSION');self.assertTrue((self.p.job('m1')/'briefs/1.json').exists())
 def test_T10_changed_approved_output(self):
  self.approved();r=self.p.rows('m1')['content'];q=self.p.path('m1',r['envelope']);e=read(q);e['payload']['scenes'][0]['narration']='Changed';write(q,e)
  self.p.refresh('m1');self.assertEqual(self.p.rows('m1')['content']['state'],'stale')
 def test_T11_fresh_process_resume(self):
  self.submit()
  import workflow
  write(self.p.job('m1')/'workflow.json',{'version':3,'mode':'review','created_at':0})
  from pilot import hashobj
  self.p.event('m1','control','workflow_created',hashobj(read(self.p.job('m1')/'workflow.json')))
  workflow.prepare(self.p,'m1','content')
  out=subprocess.check_output([str(ROOT/'.venv/bin/python'),str(self.root/'pilot.py'),'resume','m1'],text=True)
  self.assertEqual(json.loads(out)['stage'],'content')
  self.assertEqual(json.loads(out)['action'],'review')
 def test_T12_images_before_approval(self):
  self.submit()
  with patch('adapters.images') as call:
   with self.assertRaises(Blocked):self.p.run('m1','images')
   call.assert_not_called()
 def test_T13_protected_changes(self):
  for name in ['content_contract.py','AGENTS.md']:
   q=self.root/name;original=q.read_text();q.write_text(original+'\n# Changed')
   with self.assertRaises(Blocked):self.p.status('m1')
   q.write_text(original)
 def test_T14_independent_profiles(self):
  for job,kind,n,lo,hi in [('product','product',3,20,30),('social','interpersonal',6,45,60),('long','explainer',12,180,240)]:
   b=copy.deepcopy(self.b);b.update(topic=job,video_type=kind,scene_count=n,duration={'min_seconds':lo,'max_seconds':hi});b['required_points']=[{'id':'R01','text':'Ý riêng '+job}]
   self.p.new(job,b);self.p.approve(job,'control',1,'TEST');_,rev,h=self.p.brief(job)
   d=copy.deepcopy(self.d);d.update(topic=job,duration=b['duration'],required_points=[b['required_points'][0]['text']],brief_revision=rev,brief_hash=h)
   d['scenes']=[dict(copy.deepcopy(self.d['scenes'][0]),id=f'SC{i:02}',requirements=['R01'],estimated_seconds=(lo+hi)/2/n) for i in range(1,n+1)]
   d['coverage']=[{'requirement_id':'R01','scene_id':'SC01','quote':d['scenes'][0]['narration']}]
   write(self.p.job(job)/'draft/content.json',d);self.p.run(job,'content');self.p.approve(job,'content',1,'TEST')
   self.p.gate(job,'images')
  self.assertEqual(self.p.payload('product','content')['topic'],'product')
 def test_sources_required(self):
  b=copy.deepcopy(self.b);b['facts_required']=True
  with self.assertRaises(ContractError):self.p.new('facts',b)
 def test_brief_tamper(self):
  write(self.p.job('m1')/'briefs/1.json',dict(self.b,topic='Changed'))
  with self.assertRaises(Blocked):self.submit()
 def test_handoff_real_adapter_read_without_generation(self):
  self.approved();self.p.gate('m1','images')
  import adapters
  # The real adapter consumes the approved payload before requesting images.
  with patch('image_pipeline.request',side_effect=RuntimeError('STOP_BEFORE_EXTERNAL')) as call:
   with self.assertRaisesRegex(RuntimeError,'STOP_BEFORE_EXTERNAL'):adapters.images(self.p,'m1',self.p.job('m1')/'handoff-test')
   self.assertEqual(call.call_args.args[2],'ref:'+self.d['characters'][0]['id'])
 def test_estimate_outside_range(self):
  d=copy.deepcopy(self.d);d['scenes'][0]['estimated_seconds']=100;self.invalid(d,'ESTIMATE')
 def test_draft_check_no_revision(self):
  self.d['coverage']=[];write(self.p.job('m1')/'draft/content.json',self.d)
  self.assertFalse(self.p.check_draft('m1')['passed']);self.assertEqual(self.p.rows('m1')['content']['revision'],0)
