import contextlib,io,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,Blocked,read,write,ROOT
import adapters
from PIL import Image

class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for name in ['schemas','.agents','renderer','tests']:shutil.copytree(ROOT/name,self.root/name)
  for name in ['config.json','AGENTS.md','GEMINI.md','pilot.py','image_pipeline.py','prompt_templates.py','adapters.py','tts_worker.py','package.json','package-lock.json','requirements.txt']:
   if (ROOT/name).exists():shutil.copy(ROOT/name,self.root/name)
  shutil.copytree(ROOT/'examples',self.root/'examples');self.p=Pilot(self.root);self.p.new('test')
 def tearDown(self):self.p.db.close();self.tmp.cleanup()
 def approve(self,m):
  r=self.p.rows('test')[m];self.p.approve('test',m,r['revision'],'TEST FIXTURE approval, not user consent')
 def content(self):self.approve('control');self.p.run('test','content');self.approve('content')
 def test_render_before_approval_blocked(self):
  with self.assertRaises(Blocked):self.p.run('test','render')
 def test_stale_revision_cannot_approve(self):
  with self.assertRaises(Blocked):self.p.approve('test','control',9,'old revision')
 def test_missing_scene_fails(self):
  self.approve('control');q=self.p.job('test')/'draft/content.json';d=read(q);d['scenes'].pop();write(q,d)
  with self.assertRaises(Exception):self.p.run('test','content')
  self.assertEqual(self.p.rows('test')['content']['state'],'blocked')
 def test_missing_required_point_fails(self):
  self.approve('control');q=self.p.job('test')/'draft/content.json';d=read(q);d['required_points'].append('extra');write(q,d)
  with self.assertRaises(Blocked):self.p.run('test','content')
 def test_changed_approved_output_invalidates(self):
  self.content();r=self.p.rows('test')['content'];q=self.p.path('test',r['envelope']);e=read(q);e['payload']['scenes'][0]['narration']='changed';write(q,e)
  self.p.refresh('test');self.assertEqual(self.p.rows('test')['content']['state'],'stale')
  with self.assertRaises(Blocked):self.p.run('test','images')
 def test_resume_new_process(self):
  self.content();second=Pilot(self.root)
  self.assertEqual(second.next('test')['module'],'images');second.db.close()
 def test_modified_validator_blocks(self):
  (self.root/'pilot.py').write_text('changed')
  with self.assertRaises(Blocked):self.p.status('test')
 def test_video_status(self):
  self.assertEqual(adapters.request_video().get('status'),'video enabled')
 def test_escape_rejected(self):
  with self.assertRaises(Blocked):self.p.path('test','../../secret')
 def test_timeout_not_resubmitted(self):
  self.content();base=self.p.job('test')/'flow';base.mkdir();shot=base/'preflight.png';Image.new('RGB',(10,10)).save(shot)
  from pilot import digest
  import time
  model_name=read(self.root/'config.json')['flow_model']
  write(base/'preflight.json',{'observed_at':time.time(),'mode':'image','credits_per_generation':0,'model':model_name,'screenshot':'flow/preflight.png','screenshot_hash':digest(shot)})
  scene=self.p.payload('test','content')['scenes'][0]
  with patch('adapters.gflow',side_effect=TimeoutError('submitted but timed out')) as call:
   for _ in range(2):
    with self.assertRaises(Blocked):adapters.generate_image(self.p,'test',scene)
   self.assertEqual(call.call_count,1)
 def test_missing_image_rejected(self):
  self.content();content=self.p.payload('test','content')
  payload={'items':[{'scene_id':s['id'],'path':'missing.png','prompt':s['prompt'],'source':'google-flow'} for s in content['scenes']],'contact_sheet':'sheet.jpg'}
  with self.assertRaises(Exception):self.p.checks('test','images',payload)
 def test_rejection_invalidates_downstream(self):
  self.content();self.p.reject('test','control','change configuration');self.assertEqual(self.p.rows('test')['content']['state'],'stale')
 def test_approval_without_feedback_rejected(self):
  with self.assertRaises(Blocked):self.p.approve('test','control',1,'')
 def test_retry_failed_revision_uses_new_directory(self):
  self.approve('control');q=self.p.job('test')/'draft/content.json';original=read(q);bad=dict(original);bad['scenes']=[];write(q,bad)
  with self.assertRaises(Exception):self.p.run('test','content')
  write(q,original);self.p.run('test','content');self.assertEqual(self.p.rows('test')['content']['revision'],2)
 def test_scene_id_path_injection_rejected(self):
  self.approve('control');q=self.p.job('test')/'draft/content.json';d=read(q);d['scenes'][0]['id']='../../escape';write(q,d)
  with self.assertRaises(Blocked):self.p.run('test','content')
 def test_cannot_reduce_brief_with_script(self):
  self.approve('control');q=self.p.job('test')/'draft/content.json';d=read(q);removed=d['required_points'].pop();d['scenes'][-1]['requirements']=[d['required_points'][0]];write(q,d)
  with self.assertRaises(Blocked):self.p.run('test','content')
if __name__=='__main__':unittest.main(verbosity=2)
