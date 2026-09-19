import copy,json,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,ROOT,Blocked,read
from scripts.agy_pipeline import generate,invoke

class AgyAdapterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for n in ['schemas','.agents','renderer','tests','examples','scripts']:shutil.copytree(ROOT/n,self.root/n)
  for n in ['pilot.py','content_contract.py','config.json','AGENTS.md','GEMINI.md']:shutil.copy(ROOT/n,self.root/n)
  self.p=Pilot(self.root);self.p.new('agy',read(ROOT/'examples/m1/brief.json'))
 def tearDown(self):self.p.db.close();self.tmp.cleanup()
 def approve_control(self):self.p.approve('agy','control',1,'TEST ONLY')
 def response(self):
  d=read(ROOT/'examples/m1/content.json');_,rev,h=self.p.brief('agy');d.update(brief_revision=rev,brief_hash=h)
  return {'status':'SUCCESS','conversation_id':'TEST-ID','structured_output':d}
 def test_gate_before_external_request(self):
  with patch('scripts.agy_pipeline.invoke') as call:
   with self.assertRaises(Blocked):generate(self.p,'agy')
   call.assert_not_called()
 def test_valid_generation_stops_for_review(self):
  self.approve_control()
  with patch('scripts.agy_pipeline.invoke',return_value=self.response()):self.assertEqual(generate(self.p,'agy')['action'],'review')
  self.assertEqual(self.p.rows('agy')['content']['state'],'awaiting_review')
  with patch('scripts.agy_pipeline.invoke') as call:
   with self.assertRaises(Blocked):generate(self.p,'agy')
   call.assert_not_called()
 def test_invalid_response_no_submission(self):
  self.approve_control();data=self.response();data['structured_output']['coverage']=[]
  with patch('scripts.agy_pipeline.invoke',return_value=data):
   with self.assertRaises(ValueError):generate(self.p,'agy')
  self.assertEqual(self.p.rows('agy')['content']['revision'],0)
  self.assertFalse((self.p.job('agy')/'draft/content.json').exists())
 def test_timeout_no_retry(self):
  self.approve_control()
  with patch('scripts.agy_pipeline.invoke',side_effect=Blocked('AGY_TIMEOUT')) as call:
   with self.assertRaises(Blocked):generate(self.p,'agy')
   self.assertEqual(call.call_count,1)
  attempts=list((self.p.job('agy')/'agent-attempts').glob('*/attempt.json'))
  self.assertEqual(read(attempts[0])['state'],'blocked')
 def test_protocol_rejects_success_without_structured_output(self):
  from types import SimpleNamespace
  with patch('scripts.agy_pipeline.shutil.which',return_value='/fake/agy'),patch('scripts.agy_pipeline.Path.home',return_value=self.root),patch('scripts.agy_pipeline.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='{"status":"SUCCESS"}')):
   with self.assertRaisesRegex(Blocked,'missing structured_output'):invoke('x',{},self.root)
 def test_api_provider_blocked(self):
  from pilot import write
  write(self.root/'.gemini/antigravity-cli/settings.json',{'modelProvider':'gemini'})
  with patch('scripts.agy_pipeline.Path.home',return_value=self.root),patch('scripts.agy_pipeline.shutil.which',return_value='/fake/agy'),patch('scripts.agy_pipeline.subprocess.run') as call:
   with self.assertRaisesRegex(Blocked,'AGY_API_PROVIDER'):invoke('x',{},self.root)
   call.assert_not_called()
