"""English words/sentences inside Vietnamese narration are voiced by the English
engine and spliced in; retakes change a recorded, controllable knob.
No model is loaded: VieNeu and Pocket TTS are faked."""
import contextlib,importlib,json,sqlite3,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import read,write,ROOT
import adapters,tts_worker,jsonschema
import numpy as np
import soundfile as sf
from tests.test_audio import fake_vieneu,SR

SC04='Tới lượt bạn nhé! Hãy nghe và lặp lại thật to nào: "Please don\'t scold me!"'
VOCAB=[{'word':'scold','phonetic':'/skoʊld/','meaning':'mắng'}]

def sine(path,seconds,amp):
 t=np.arange(int(SR*seconds))/SR;sf.write(str(path),(amp*np.sin(2*np.pi*220*t)).astype('float32'),SR,subtype='PCM_16')

class EnglishPartsTests(unittest.TestCase):
 def test_quoted_practice_sentence_goes_to_english_engine(self):
  self.assertEqual(adapters.english_parts('Hãy nghe và lặp lại thật to nào: "Please don\'t scold me!"',['scold']),
   [{'lang':'vi','text':'Hãy nghe và lặp lại thật to nào:'},{'lang':'en','text':"Please don't scold me!"}])
 def test_bare_vocabulary_word_keeps_its_punctuation(self):
  self.assertEqual(adapters.english_parts('Phát âm chuẩn là: scold.',['scold']),
   [{'lang':'vi','text':'Phát âm chuẩn là:'},{'lang':'en','text':'scold.'}])
  self.assertEqual(adapters.english_parts('Scold có nghĩa là trách mắng.',['scold'])[0],{'lang':'en','text':'Scold'})
 def test_mid_sentence_word_and_inflection(self):
  self.assertEqual([x['lang'] for x in adapters.english_parts('Đừng quên một câu với scolding để nhớ nhé!',['scold'])],['vi','en','vi'])
  self.assertEqual(adapters.english_parts('Tôi thấy scoldx ở đây.',['scold']),[{'lang':'vi','text':'Tôi thấy scoldx ở đây.'}])
 def test_quote_wins_over_word_and_curly_quotes(self):
  parts=adapters.english_parts('Mẹ mắng: “My mom scolded me.” Xong!',['scold'])
  self.assertEqual(parts,[{'lang':'vi','text':'Mẹ mắng:'},{'lang':'en','text':'My mom scolded me.'},{'lang':'vi','text':'Xong!'}])
 def test_quoted_vietnamese_stays_on_vieneu(self):
  t='Bố can: "Đừng mắng con bé nữa!"'
  self.assertEqual(adapters.english_parts(t,['scold']),[{'lang':'vi','text':t}])

class SpanTakeTests(unittest.TestCase):
 def test_retake_zero_is_configured_delivery(self):
  self.assertEqual(adapters.span_take({'en_seed':42,'en_temperature':.3},0),{'seed':42,'temperature':.3,'rate':1.})
 def test_each_retake_changes_seed_temperature_and_rate_deterministically(self):
  takes=[adapters.span_take({},r) for r in range(4)]
  self.assertEqual(takes,[adapters.span_take({},r) for r in range(4)])
  for a,b in zip(takes,takes[1:]):
   self.assertEqual(b['seed'],a['seed']+1);self.assertLess(b['temperature'],a['temperature']);self.assertLess(b['rate'],a['rate'])
 def test_floors(self):
  t=adapters.span_take({},50);self.assertEqual((t['temperature'],t['rate']),(.1,.8))

class MixedWorkerTests(unittest.TestCase):
 """tts_worker.run() with parts: VieNeu never sees the English text."""
 def test_english_part_is_spliced_not_sent_to_vieneu(self):
  with tempfile.TemporaryDirectory() as d,fake_vieneu() as fake:
   out=Path(d);en=out/'span.wav';sine(en,.5,.5)
   texts=['Tới lượt bạn nhé!','Hãy nghe và lặp lại thật to nào: "Please don\'t scold me!"']
   parts=[[{'lang':'vi','text':texts[0]}],[{'lang':'vi','text':'Hãy nghe và lặp lại thật to nào:'},
          {'lang':'en','text':"Please don't scold me!",'wav':str(en),'rate':1.,'take':{'engine':'pocket-tts','voice':'alba','seed':43,'temperature':.25,'rate':1.}}]]
   req={'settings':dict(tts_voice='Voice One',tts_temperature=.6,tts_top_p=.9,tts_device='cpu',audio_english_spans_gap=.2),
        'scenes':[{'scene_id':'SC04','narration':' '.join(texts),'texts':texts,'parts':parts,'gaps':[.5],'tail':.3,'retake':1}]}
   write(out/'request.json',req);tts_worker.run(out/'request.json',out);res=read(out/'tts-result.json')
   self.assertFalse([c for c in fake.calls if 'scold' in c])
   self.assertEqual(res['scenes'],[{'scene_id':'SC04','mode':'mixed'}])
   self.assertEqual([s['text'] for s in res['segments']],texts)
   # vi part (0.2 s fake take) + gap + en take; the fades keep length.
   self.assertAlmostEqual(res['segments'][1]['content_duration'],.2+.2+.5,places=2)
   sp=res['english_spans'][0]
   self.assertEqual((sp['scene_id'],sp['retake'],sp['seed'],sp['temperature'],sp['engine']),('SC04',1,43,.25,'pocket-tts'))
   w,_=sf.read(str(out/res['segments'][1]['path']),dtype='float32')
   body=w[int(.45*SR):int(.85*SR)]
   # Level-matched to the Vietnamese take (0.05) within the gain clamp, not left at 0.5.
   self.assertLess(np.abs(body).max(),.2);self.assertLess(sp['gain_db'],0)

 def test_slower_rate_lengthens_english_part(self):
  with tempfile.TemporaryDirectory() as d,fake_vieneu():
   out=Path(d);en=out/'span.wav';sine(en,1.,.05)
   w=tts_worker.load_span({'wav':str(en),'rate':.8},SR)
   self.assertAlmostEqual(w.size/SR,1.25,places=1)

 def test_trim_keeps_weak_final_release(self):
  w=np.zeros(SR,dtype='float32');w[int(.2*SR):int(.5*SR)]=.3;w[int(.5*SR):int(.56*SR)]=.01
  t=tts_worker.trim(w,SR)
  self.assertGreaterEqual(t.size,int(.36*SR))  # speech + weak tail kept, plus margin

class FakeP:
 """Minimal stand-in for Pilot: exactly what adapters.audio() touches."""
 def __init__(self,root,content,cfg):
  self.root=root;self.content=content;(root/'jobs/j').mkdir(parents=True)
  write(root/'config.json',cfg)
  self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
  self.db.execute('CREATE TABLE audio_edits(id INTEGER PRIMARY KEY,job TEXT,scene_id TEXT,note TEXT,at REAL)')
  for v in ['.venv-tts','.venv-en']:(root/v/'bin').mkdir(parents=True);(root/v/'bin/python').write_text('#fake')
 def payload(self,j,m):return self.content
 def job(self,j):return self.root/'jobs'/j
 def brief(self,j):return None

class AudioAdapterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.content={'scenes':[{'id':'SC03','narration':'Mẹ mắng tôi. Bố nói: "Đừng mắng con!"','vocabulary':VOCAB},
                          {'id':'SC04','narration':SC04,'vocabulary':VOCAB,'audio_direction':{'vi':{'learner_pause_seconds':3.0}}},
                          {'id':'SC05','narration':'Rất tuyệt vời, hẹn gặp lại!'}]}
  self.cfg=dict(read(ROOT/'config.json'))
  self.calls=[]
 def tearDown(self):self.tmp.cleanup()

 def run_audio(self,**cfg):
  p=FakeP(self.root,self.content,dict(self.cfg,**cfg));self.p=p
  for sid,n in getattr(self,'retakes',{}).items():
   for _ in range(n):p.db.execute("INSERT INTO audio_edits(job,scene_id,note,at) VALUES('j',?,'TEST',0)",(sid,))
  real=subprocess.run
  def run(cmd,**kw):
   s=str(cmd[1])
   if 'en_worker.py' in s:
    req=read(cmd[2]);out=Path(cmd[3]);self.calls.append(('en',req));spans=[]
    for x in req['spans']:
     sine(out/f"en-span-{x['id']}.wav",.6,.3)
     spans.append(dict(id=x['id'],text=x['text'],path=f"en-span-{x['id']}.wav",seed=x['take']['seed'],temperature=x['take']['temperature'],content_duration=.6))
    write(out/'en-spans-result.json',{'engine':'pocket-tts','voice':'alba','spans':spans})
   elif 'tts_worker.py' in s:
    self.calls.append(('vi',read(cmd[2])))
    with fake_vieneu():tts_worker.run(Path(cmd[2]),Path(cmd[3]))
   else:return real(cmd,**kw)
   return subprocess.CompletedProcess(cmd,0,'','')
  out=p.job('j')/'revisions/audio/1';out.mkdir(parents=True)
  with patch.object(adapters.subprocess,'run',side_effect=run):return adapters.audio(p,'j',out)

 def test_scold_practice_line_uses_english_engine_and_valid_timeline(self):
  pay=self.run_audio()
  jsonschema.validate(pay,read(ROOT/'schemas/audio.json'))
  en=[r for k,r in self.calls if k=='en'][0]
  self.assertEqual(en['mode'],'spans');self.assertEqual([x['text'] for x in en['spans']],["Please don't scold me!"])
  vi=[r for k,r in self.calls if k=='vi'][0]
  self.assertEqual([('parts' in s) for s in vi['scenes']],[False,True,False])
  # Subtitle/segment contract is untouched: same texts, contiguous timeline.
  for sc in self.content['scenes']:
   self.assertEqual(' '.join(x['text'] for x in pay['segments'] if x['scene_id']==sc['id']),sc['narration'])
  last=0
  for x in pay['segments']:
   self.assertAlmostEqual(x['start'],last,places=6);self.assertLess(x['start'],x['content_end']);self.assertLessEqual(x['content_end'],x['end']);last=x['end']
  self.assertAlmostEqual(pay['duration'],last,places=6)
  self.assertEqual(pay['srt'].split('/')[-1],'subtitles.srt')
  self.assertEqual([(s['scene_id'],s['retake'],s['seed'],s['rate']) for s in pay['english_spans']],[('SC04',0,42,1.)])

 def test_retake_changes_english_take_and_is_recorded(self):
  self.retakes={'SC04':2}
  pay=self.run_audio()
  en=[r for k,r in self.calls if k=='en'][0]
  self.assertEqual(en['spans'][0]['take'],{'seed':44,'temperature':.2,'rate':.9})
  sp=pay['english_spans'][0]
  self.assertEqual((sp['retake'],sp['seed'],sp['temperature'],sp['rate']),(2,44,.2,.9))

 def test_switch_off_keeps_everything_on_vieneu(self):
  pay=self.run_audio(audio_english_spans_engine='vieneu')
  self.assertEqual([k for k,_ in self.calls],['vi'])
  self.assertNotIn('english_spans',pay)
  self.assertFalse(any('parts' in s for s in self.calls[0][1]['scenes']))

 def test_scenes_without_vocabulary_are_untouched(self):
  for s in self.content['scenes']:s.pop('vocabulary',None)
  self.run_audio()
  self.assertEqual([k for k,_ in self.calls],['vi'])

@contextlib.contextmanager
def fake_pocket():
 """Fake torch/pocket_tts/scipy so scripts/en_worker.py imports without models."""
 state=types.SimpleNamespace(seeds=[],temps=[],texts=[])
 torch=types.ModuleType('torch');torch.manual_seed=state.seeds.append
 torch.set_num_threads=torch.set_num_interop_threads=lambda n:None
 Q=type('Linear',(),{'__module__':'fake.quantized'})
 class Arr:
  def __init__(self,a):self.a=a
  def detach(self):return self
  def cpu(self):return self
  def numpy(self):return self.a
 class Model:
  sample_rate=48000;temp=None
  def modules(self):return [Q()]
  def get_state_for_audio_prompt(self,name):return name
  def generate_audio(self,voice,text):
   state.texts.append(text);state.temps.append(self.temp)
   return Arr((.3*np.sin(np.arange(SR//2)/9)).astype('float32'))
 pt=types.ModuleType('pocket_tts');pt.TTSModel=types.SimpleNamespace(load_model=lambda **kw:Model())
 sig=types.ModuleType('scipy.signal');sig.resample_poly=None;sc=types.ModuleType('scipy');sc.signal=sig
 with patch.dict(sys.modules,{'torch':torch,'pocket_tts':pt,'scipy':sc,'scipy.signal':sig}):
  sys.modules.pop('scripts.en_worker',None)
  mod=importlib.import_module('scripts.en_worker')
  with patch.object(mod,'version',return_value='9.9-test'):yield mod,state
  sys.modules.pop('scripts.en_worker',None)

class EnWorkerTests(unittest.TestCase):
 cfg=dict(en_voice='alba',en_device='cpu',en_quantize=True,en_temperature=.3,en_threads=4,en_seed=42)
 def test_spans_mode_uses_take_and_caches(self):
  with tempfile.TemporaryDirectory() as d,fake_pocket() as (m,st):
   out=Path(d)/'o';req={'mode':'spans','settings':self.cfg,'cache_dir':str(Path(d)/'c'),
    'spans':[{'id':'S000','text':"Please don't scold me!",'retake':1,'take':{'seed':43,'temperature':.25,'rate':.95}}]}
   write(Path(d)/'r.json',req);m.run(Path(d)/'r.json',out)
   res=read(out/'en-spans-result.json')['spans'][0]
   self.assertEqual((res['seed'],res['temperature'],res['path']),(43,.25,'en-span-S000.wav'))
   self.assertEqual((st.seeds[-1],st.temps),(43,[.25]))
   m.run(Path(d)/'r.json',Path(d)/'o2')
   self.assertEqual(len(st.texts),1)  # second run hit the content-addressed cache

 def test_scene_retake_lowers_temperature_but_retake_zero_key_is_unchanged(self):
  with tempfile.TemporaryDirectory() as d,fake_pocket() as (m,st):
   scenes=[{'scene_id':'SC01','narration_en':'Hello there.','tail':.3,'retake':0,'take':{'seed':42,'temperature':.3}},
           {'scene_id':'SC02','narration_en':'Please do not scold me.','tail':.3,'retake':2,'take':{'seed':44,'temperature':.2}}]
   write(Path(d)/'r.json',{'settings':self.cfg,'cache_dir':str(Path(d)/'c'),'scenes':scenes});m.run(Path(d)/'r.json',Path(d)/'o')
   self.assertEqual(st.temps,[.3,.2]);self.assertEqual(st.seeds[1:],[42,44])
   self.assertEqual((Path(d)/'c/SC01.sha256').read_text(),m.cache_key('Hello there.',m.settings(self.cfg),0))
   takes=[s['take'] for s in read(Path(d)/'o/en-result.json')['scenes']]
   self.assertEqual(takes,[{'retake':0,'seed':42,'temperature':.3},{'retake':2,'seed':44,'temperature':.2}])

if __name__=='__main__':unittest.main()
