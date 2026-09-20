"""Audio module coverage. Real TTS is never invoked; the worker is faked."""
import json,math,shutil,struct,subprocess,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,Blocked,read,write,ROOT
import adapters

SR=48000

def worker(emit,voice=None):
 """Fake tts_worker.py. Only intercepts the worker call; ffmpeg still runs for real."""
 real=subprocess.run
 def run(cmd,**kw):
  if 'tts_worker.py' not in str(cmd[1]):return real(cmd,**kw)
  req=read(cmd[2]);out=Path(cmd[3]);segs=[]
  for sc in req['scenes']:
   for t in sc['texts']:
    emit(out,len(segs),sc,t)
    segs.append({'scene_id':sc['scene_id'],'text':voice(t) if voice else t,'path':f'segment-{len(segs):03}.wav'})
  write(out/'tts-result.json',{'voice':req['settings']['tts_voice'],'label':'fake','segments':segs})
  return subprocess.CompletedProcess(cmd,0,'','')
 return run

def tone(path,seconds,level=8000):
 """Mono PCM_16 48 kHz speech stand-in: a tone body plus a trailing silence."""
 body=int(SR*seconds*.8);tail=int(SR*seconds)-body
 frames=b''.join(struct.pack('<h',int(level*math.sin(2*math.pi*180*i/SR))) for i in range(body))+b'\x00\x00'*tail
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(frames)

class PureHelperTests(unittest.TestCase):
 def test_chunks_preserve_narration(self):
  """pilot.checks rejoins segment texts and compares to narration verbatim.

  Guards against anyone swapping in vieneu's chunker, whose punc_norm output
  lowercases and rewrites punctuation and would trip 'Narration omitted'.
  """
  for s in read(ROOT/'examples/content.json')['scenes']:
   self.assertEqual(' '.join(' '.join(adapters.chunks(s['narration'])).split()),' '.join(s['narration'].split()))

 def test_chunks_never_empty(self):
  for text in ['No terminal punctuation','Một câu. Hai câu!','A'*400+'. B'*5]:
   parts=adapters.chunks(text)
   self.assertTrue(parts and all(c.strip() for c in parts),text[:20])

 def test_gap_after_follows_punctuation(self):
  g=adapters.DEFAULT_PAUSE
  for text,want in [('Xin chào bạn.','sentence'),('Thật sao?','sentence'),('Tuyệt vời!','sentence'),
                    ('Dấu ba chấm…','sentence'),('Một, hai,','minor'),('Vế trước;','minor'),('Không dấu','minor')]:
   self.assertEqual(adapters.gap_after(text,g),g[want],text)

 def test_gap_after_honours_config_override(self):
  self.assertEqual(adapters.gap_after('Câu.',{'sentence':.9}),.9)
  self.assertEqual(adapters.gap_after('Câu,',{}),adapters.DEFAULT_PAUSE['minor'])

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg required')
class MasterTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()

 def test_master_preserves_frame_count(self):
  """pilot.checks matches the combined wav against segments[-1]['end'] within
  30 ms, so mastering must not pad, trim or resample."""
  src=self.d/'n.wav';tone(src,3.0);before=adapters.frames_of(src)
  adapters.master(src,self.d/'eq.wav',{'audio_lufs':-14.,'audio_peak_db':-1.5})
  self.assertEqual(adapters.frames_of(src),before)
  with wave.open(str(src)) as w:self.assertEqual(w.getframerate(),48000)

 def test_master_hits_loudness_target_without_clipping(self):
  src=self.d/'n.wav';tone(src,3.0,level=2000)
  adapters.master(src,self.d/'eq.wav',{'audio_lufs':-14.,'audio_peak_db':-1.5})
  r=subprocess.run(['ffmpeg','-v','info','-i',str(src),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True)
  m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
  self.assertLess(abs(float(m['input_i'])+14.),1.5,m)
  self.assertLessEqual(float(m['input_tp']),-1.0,m)

 def test_master_leaves_no_temp_files(self):
  src=self.d/'n.wav';tone(src,1.0)
  adapters.master(src,self.d/'eq.wav',{})
  self.assertEqual([p.name for p in self.d.iterdir()],['n.wav'])

class AudioStageTests(unittest.TestCase):
 """Drives adapters.audio() with a fake worker and asserts every pilot gate."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for name in ['schemas','.agents','renderer','tests','examples']:shutil.copytree(ROOT/name,self.root/name)
  for name in ['config.json','AGENTS.md','GEMINI.md','pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','adapters.py','tts_worker.py','package.json','package-lock.json','requirements.txt']:
   if (ROOT/name).exists():shutil.copy(ROOT/name,self.root/name)
  self.p=Pilot(self.root);self.p.new('test')
  (self.root/'.venv-tts/bin').mkdir(parents=True);(self.root/'.venv-tts/bin/python').write_text('#fake')
  self.p.approve('test','control',self.p.rows('test')['control']['revision'],'TEST FIXTURE approval, not user consent')
  self.p.run('test','content');self.p.approve('test','content',self.p.rows('test')['content']['revision'],'TEST FIXTURE approval, not user consent')
  self.p.db.execute("UPDATE modules SET state='approved' WHERE job='test' AND module='images'");self.p.db.commit()
 def tearDown(self):self.p.db.close();self.tmp.cleanup()

 def fake_worker(self,seconds=4.0):
  """Stands in for tts_worker: honours the request's scene/text structure."""
  return worker(lambda out,i,sc,t:tone(out/f'segment-{i:03}.wav',seconds))

 def test_audio_passes_every_gate(self):
  with patch.object(adapters.subprocess,'run',side_effect=self.fake_worker()):
   self.p.run('test','audio')
  r=self.p.rows('test')['audio']
  self.assertEqual(r['state'],'awaiting_review')
  self.p.validate('test','audio')
  pay=read(self.p.path('test',r['envelope']))['payload']
  self.assertEqual(len(pay['segments']),sum(len(adapters.chunks(s['narration'])) for s in self.p.payload('test','content')['scenes']))
  last=0
  for s in pay['segments']:
   self.assertAlmostEqual(s['start'],last,places=3);self.assertGreater(s['end'],s['start']);last=s['end']
  self.assertAlmostEqual(pay['duration'],last,places=3)

 def test_request_carries_pauses_and_voice(self):
  seen={};inner=self.fake_worker()
  def spy(cmd,**kw):
   if 'tts_worker.py' in str(cmd[1]):seen.update(read(cmd[2]))
   return inner(cmd,**kw)
  with patch.object(adapters.subprocess,'run',side_effect=spy):self.p.run('test','audio')
  cfg=read(self.root/'config.json')
  self.assertEqual(seen['settings']['tts_voice'],cfg['tts_voice'])
  self.assertEqual(seen['settings']['tts_temperature'],cfg['tts_temperature'])
  self.assertEqual(seen['scenes'][-1]['tail'],cfg['tts_pause']['tail'])
  for sc in seen['scenes'][:-1]:self.assertEqual(sc['tail'],cfg['tts_pause']['para'])
  for sc in seen['scenes']:self.assertEqual(len(sc['gaps']),len(sc['texts'])-1)

 def test_silent_segment_is_blocked(self):
  run=worker(lambda out,i,sc,t:tone(out/f"segment-{i:03}.wav",4.0,level=0))
  with patch.object(adapters.subprocess,'run',side_effect=run):
   with self.assertRaises(Blocked):self.p.run('test','audio')

 def test_altered_narration_is_blocked(self):
  run=worker(lambda out,i,sc,t:tone(out/f"segment-{i:03}.wav",4.0),voice=lambda t:t+' thêm chữ')
  with patch.object(adapters.subprocess,'run',side_effect=run):
   with self.assertRaises(Blocked):self.p.run('test','audio')

if __name__=='__main__':unittest.main()

class EnglishTrackTests(unittest.TestCase):
 """16:9 jobs carry an English track on its own timeline; 9:16 jobs must not."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for n in ['schemas','.agents','renderer','tests','examples']:shutil.copytree(ROOT/n,self.root/n)
  for n in ['pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','content_contract.py','adapters.py','tts_worker.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt']:
   if (ROOT/n).exists():shutil.copy(ROOT/n,self.root/n)
  (self.root/'scripts').mkdir(exist_ok=True);shutil.copy(ROOT/'scripts/en_worker.py',self.root/'scripts/en_worker.py')
  for v in ['.venv-tts','.venv-en']:
   (self.root/v/'bin').mkdir(parents=True);(self.root/v/'bin/python').write_text('#fake')
 def tearDown(self):
  if hasattr(self,'p'):self.p.db.close()
  self.tmp.cleanup()

 def start(self,ratio):
  b=read(ROOT/'examples/m1/brief.json');b['aspect_ratio']=ratio
  self.p=Pilot(self.root);self.p.new('m1',b)
  self.p.approve('m1','control',1,'TEST FIXTURE approval, not user consent')
  d=read(ROOT/'examples/m1/content.json');_,rev,h=self.p.brief('m1')
  d.update(brief_revision=rev,brief_hash=h)
  if ratio in ('dual','16:9'):
   for s in d['scenes']:s['narration_en']='English narration for '+s['id']+'. It carries the same idea in natural English.'
  write(self.p.job('m1')/'draft/content.json',d)
  self.p.run('m1','content');self.p.approve('m1','content',1,'TEST FIXTURE approval, not user consent')
  self.p.db.execute("UPDATE modules SET state='approved' WHERE job='m1' AND module='images'");self.p.db.commit()
  return d

 def fake(self,vi=4.0,en=9.0):
  """Fakes both workers; ffmpeg still runs for real inside master()."""
  real=subprocess.run
  def run(cmd,**kw):
   s=str(cmd[1])
   if 'tts_worker.py' in s:
    req=read(cmd[2]);out=Path(cmd[3]);segs=[]
    for sc in req['scenes']:
     for t in sc['texts']:
      tone(out/f'segment-{len(segs):03}.wav',vi)
      segs.append({'scene_id':sc['scene_id'],'text':t,'path':f'segment-{len(segs):03}.wav'})
    write(out/'tts-result.json',{'voice':'vi','label':'fake','segments':segs})
   elif 'en_worker.py' in s:
    req=read(cmd[2]);out=Path(cmd[3]);scs=[]
    for sc in req['scenes']:
     path=f"en-{sc['scene_id']}.wav";tone(out/path,en)
     scs.append({'scene_id':sc['scene_id'],'path':path})
    write(out/'en-result.json',{'engine':'pocket-tts','voice':'alba','settings':req['settings'],'scenes':scs})
   else:return real(cmd,**kw)
   return subprocess.CompletedProcess(cmd,0,'','')
  return run

 def test_dual_job_produces_english_track(self):
  content=self.start('dual')
  with patch.object(adapters.subprocess,'run',side_effect=self.fake()):self.p.run('m1','audio')
  self.p.validate('m1','audio')
  pay=read(self.p.path('m1',self.p.rows('m1')['audio']['envelope']))['payload']
  en=pay['en']
  self.assertEqual(en['engine'],'pocket-tts');self.assertEqual(en['voice'],'alba')
  self.assertEqual([s['scene_id'] for s in en['scenes']],[s['id'] for s in content['scenes']])
  last=0
  for s in en['scenes']:
   self.assertAlmostEqual(s['start'],last,places=3);last=s['end']
  self.assertAlmostEqual(en['duration'],last,places=3)
  # The whole point: English runs on its own clock, not the Vietnamese one.
  self.assertNotAlmostEqual(en['duration'],pay['duration'],places=1)

 def test_english_request_uses_selected_alba_settings(self):
  self.start('dual');seen={};inner=self.fake()
  def spy(cmd,**kw):
   if 'en_worker.py' in str(cmd[1]):seen.update(read(cmd[2]))
   return inner(cmd,**kw)
  with patch.object(adapters.subprocess,'run',side_effect=spy):self.p.run('m1','audio')
  self.assertEqual(seen['settings'],dict(en_voice='alba',en_device='cpu',en_quantize=True,
                                        en_temperature=0.3,en_threads=4,en_seed=42))

 def test_english_worker_failure_blocks_audio(self):
  self.start('dual');inner=self.fake()
  def fail(cmd,**kw):
   if 'en_worker.py' in str(cmd[1]):return subprocess.CompletedProcess(cmd,1,'','INT8 failed')
   return inner(cmd,**kw)
  with patch.object(adapters.subprocess,'run',side_effect=fail):
   with self.assertRaisesRegex(Blocked,'English TTS failed'):self.p.run('m1','audio')

 def test_vertical_job_has_no_english_track(self):
  self.start('9:16')
  with patch.object(adapters.subprocess,'run',side_effect=self.fake()):self.p.run('m1','audio')
  pay=read(self.p.path('m1',self.p.rows('m1')['audio']['envelope']))['payload']
  self.assertNotIn('en',pay)

 def test_dual_content_without_english_is_rejected(self):
  from content_contract import ContractError
  b=read(ROOT/'examples/m1/brief.json');b['aspect_ratio']='dual'
  self.p=Pilot(self.root);self.p.new('m1',b)
  self.p.approve('m1','control',1,'TEST FIXTURE approval, not user consent')
  d=read(ROOT/'examples/m1/content.json');_,rev,h=self.p.brief('m1')
  d.update(brief_revision=rev,brief_hash=h);write(self.p.job('m1')/'draft/content.json',d)
  with self.assertRaises(ContractError) as c:self.p.run('m1','content')
  self.assertIn('NARRATION_EN',{e['code'] for e in c.exception.errors})

 def test_render_props_carry_english_timeline(self):
  content=self.start('dual')
  with patch.object(adapters.subprocess,'run',side_effect=self.fake()):self.p.run('m1','audio')
  self.p.approve('m1','audio',1,'TEST FIXTURE approval, not user consent')
  snd=self.p.payload('m1','audio')
  imgs={'items':[{'scene_id':s['id'],'path':'x.png','prompt':'p','source':'fake'} for s in content['scenes']]}
  out=self.p.job('m1')/'revisions/render/1';out.mkdir(parents=True)
  for s in content['scenes']:
   f=self.p.job('m1')/'x.png'
   if not f.exists():f.write_bytes(b'TEST ONLY; renderer never executes')
  captured={}
  def stop(cmd,**kw):
   captured.update(read(out/'props.json'));raise RuntimeError('renderer not executed in tests')
  with patch.object(adapters,'subprocess') as sp:
   sp.run.side_effect=stop
   with patch.object(self.p,'payload',side_effect=lambda j,m:{'content':content,'images':imgs,'audio':snd}[m]):
    with self.assertRaises(RuntimeError):adapters.render(self.p,'m1',out)
  self.assertEqual(captured['en_duration'],snd['en']['duration'])
  self.assertEqual([s['start'] for s in captured['en_scenes']],[s['start'] for s in snd['en']['scenes']])
  self.assertNotEqual([s['end'] for s in captured['en_scenes']],[s['end'] for s in captured['scenes']])
