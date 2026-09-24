"""Dedicated local-only environment; downloads public model weights on first use."""
import hashlib,json,sys
from pathlib import Path
import numpy as np,soundfile as sf

CACHE_VERSION=2  # bump to invalidate every cached WAV (e.g. after a model/package upgrade)

def troughs(w,sr,thresh_db=-40.,win_s=0.01,min_s=0.10):
 """Silence runs strictly inside w, as (start,end) sample pairs."""
 win=max(1,int(win_s*sr));n=w.size//win
 if n==0:return []
 quiet=np.abs(w[:n*win]).reshape(n,win).mean(1)<=10**(thresh_db/20)
 runs=[];i=0
 while i<n:
  if not quiet[i]:i+=1;continue
  j=i
  while j<n and quiet[j]:j+=1
  if (j-i)*win>=min_s*sr:runs.append((i*win,j*win))
  i=j
 return [r for r in runs if r[0]>0 and r[1]<n*win]

def split_at(w,sr,texts):
 """Cut one scene waveform back into len(texts) sentence pieces, choosing the
 silence trough nearest each sentence's expected position and preferring long
 troughs. None when the audio cannot be split confidently."""
 k=len(texts)
 if k<2:return [w]
 runs=troughs(w,sr)
 if len(runs)<k-1:return None
 chars=np.cumsum([len(t) for t in texts],dtype=float)
 used=set();cuts=[]
 for b in range(k-1):
  want=w.size*chars[b]/chars[-1];best=score=None
  for idx,(s,e) in enumerate(runs):
   if idx in used:continue
   sc=abs((s+e)/2-want)/sr-0.5*min((e-s)/sr,0.8)
   if score is None or sc<score:best,score=idx,sc
  used.add(best);cuts.append(best)
 pieces=[];prev=0
 for idx in sorted(cuts):
  s,e=runs[idx];mid=int((s+e)//2)
  if mid<=prev:return None
  pieces.append(w[prev:mid]);prev=mid
 pieces.append(w[prev:])
 return pieces if all(p.size>int(.15*sr) for p in pieces) else None

def cache_key(text,settings,package_version,sample_rate,cache_version=CACHE_VERSION):
 """Content-addressed cache name: text + every setting that changes the audio +
 the installed model package version. Mirrors scripts/en_worker.py's cache_key,
 which is the correct pattern -- a cache keyed by scene/file NAME instead of by
 content will silently keep stale audio after a narration edit. Pure function
 (no vieneu import) so it stays importable/testable without the TTS runtime.
 """
 data=dict(engine='vieneu',package=package_version,language='vietnamese',
           sample_rate=sample_rate,text=text,settings=settings,cache_version=cache_version)
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

ACRONYM_WHITELIST={'AI','VIP','TP','TP.HCM','UBND','CSGT','VTV','HTV','CEO','IELTS','TOEIC','ID','DNA','RNA','FBI','CIA'}

def normalize_text_for_tts(text):
 """Sanitize text for VieNeu/sea_g2p TTS:
 1. Normalize curly quotes/apostrophes to standard quotes/apostrophes.
 2. Lowercase all-caps English words (>= 2 letters) that are not recognized acronyms,
    preventing sea_g2p normalizer from spelling them out letter-by-letter as Vietnamese acronyms.
 """
 if not text:return text
 import re
 text=text.replace('“','"').replace('”','"').replace('’',"'").replace('‘',"'")
 def _repl(m):
  w=m.group(0)
  return w if w in ACRONYM_WHITELIST else w.lower()
 text=re.sub(r'\b[A-Z]{2,}\b',_repl,text)
 # Pronunciation workaround stays in VieNeu input; original script/captions stay I.
 return re.sub(r'\bI\b', 'Ai', text)

def change_tempo(w,sr,speed):
 """Adjust audio tempo without changing pitch using ffmpeg atempo filter."""
 if abs(speed-1.0)<0.01:return w
 import io,subprocess
 buf_in=io.BytesIO()
 sf.write(buf_in,w,sr,format='WAV',subtype='PCM_16')
 cmd=['ffmpeg','-v','error','-f','wav','-i','pipe:0','-filter:a',f'atempo={speed}','-f','wav','pipe:1']
 proc=subprocess.run(cmd,input=buf_in.getvalue(),capture_output=True,check=True)
 buf_out=io.BytesIO(proc.stdout)
 out_w,_=sf.read(buf_out,dtype='float32')
 return out_w

def load_engine(cfg):
 """(Vieneu instance, engine description). tts_device: auto = CUDA when this
 interpreter has torch with a visible GPU, else ONNX/CPU; cuda = require GPU;
 cpu = always ONNX. The GPU path is PyTorch and batches chunks from many
 scenes into one forward (measured 6-7x real time on a Quadro P620 at batch 6,
 vs ~1x for ONNX/CPU on its Xeon E3-1240 v3). Below compute capability 8
 (Pascal/Turing) bf16 is emulated and fp16 crawls, so dtype is forced to fp32."""
 from vieneu import Vieneu
 device=cfg.get('tts_device','auto')
 if device not in ('auto','cuda','cpu'):raise ValueError('tts_device must be auto, cuda or cpu')
 if device!='cpu':
  try:
   import torch;cuda=torch.cuda.is_available()
  except ImportError:cuda=False
  if cuda:
   dtype=cfg.get('tts_gpu_dtype','float32')
   if torch.cuda.get_device_capability(0)[0]<8:dtype='float32'
   batch=max(1,int(cfg.get('tts_batch_size',6)))
   tts=Vieneu(mode='v3turbo',backend='pytorch',device='cuda',dtype=dtype,max_batch_size=batch)
   return tts,dict(backend='pytorch',precision=dtype,device=torch.cuda.get_device_name(0),batch_size=batch)
  if device=='cuda':raise RuntimeError('tts_device=cuda but this environment has no usable CUDA GPU')
 precision=cfg.get('tts_precision','fp32')
 return Vieneu(mode='v3turbo',backend='onnx',precision=precision),dict(backend='onnx',precision=precision,device='cpu',batch_size=1)

def is_oom(ex):
 return 'out of memory' in str(ex).lower()

def run(source,out):
 from vieneu_utils.core_utils import pause_pad_samples
 from importlib.metadata import version
 source,out=Path(source),Path(out)
 req=json.loads(source.read_text())
 cfg=req['settings']
 st={}
 def use(tts,engine):
  voices={v:label for label,v in tts.list_preset_voices()}
  if not voices:raise RuntimeError('No local preset voices')
  voice_id=tts.resolve_voice_name(cfg.get('tts_voice')) or tts._default_voice
  if voice_id not in voices:raise RuntimeError('Requested local voice unavailable')
  st.update(tts=tts,engine=engine,voice=voice_id,label=voices[voice_id],sr=tts.sample_rate)
 use(*load_engine(cfg))
 fallbacks=[]

 # Step 1 (this change): cache filenames are content hashes instead of scene
 # names, so an edited narration or changed voice/settings can never reuse a
 # stale WAV. Step 2 (separate change): the cache directory itself moves to
 # runs/JOB/cache/tts so it survives across pilot.py's per-run revision dirs
 # -- until then it still lives under the revision (out/'raw') and buys
 # nothing across runs, but the keys are now safe to relocate.
 raw=Path(req['cache_dir']) if req.get('cache_dir') else out/'raw'
 raw.mkdir(parents=True,exist_ok=True)
 package_version=version('vieneu')
 speed=float(cfg.get('tts_speed',1.0))

 def cached(text,retake):
  """Cache file for text under the ACTIVE engine. backend/precision are part of
  the key: GPU and CPU takes differ, and a mid-run fallback must not mislabel
  audio. Batch size is not -- it only groups work, the take stays equivalent."""
  e=st['engine']
  key_settings=dict(voice=str(st['voice']),temperature=cfg['tts_temperature'],top_p=cfg['tts_top_p'],
                    backend=e['backend'],precision=e['precision'],mode='v3turbo',speed=speed,retake=retake)
  return raw/(cache_key(text,key_settings,package_version,st['sr'])+'.wav')

 def generate(texts):
  """One waveform per text. GPU: all texts share batched forwards; on CUDA OOM
  the batch is halved, and at batch 1 the run falls back to ONNX/CPU."""
  while True:
   tts,e=st['tts'],st['engine']
   kw=dict(voice=st['voice'],temperature=cfg['tts_temperature'],top_p=cfg['tts_top_p'])
   if e['backend']!='pytorch':return [tts.infer(t,**kw) for t in texts]
   try:return tts.infer_batch(texts,batch_size=e['batch_size'],**kw)
   except Exception as ex:
    if not is_oom(ex):raise
    import gc,torch;gc.collect();torch.cuda.empty_cache()
    if e['batch_size']>1:
     fallbacks.append(f"CUDA OOM at batch {e['batch_size']}; retrying at {e['batch_size']//2}")
     e['batch_size']//=2;continue
    fallbacks.append('CUDA OOM at batch 1; switching to ONNX/CPU')
    st['tts']=tts=None;gc.collect();torch.cuda.empty_cache()
    use(*load_engine(dict(cfg,tts_device='cpu')))

 def prefetch(items):
  """Synthesize every (text, retake) not yet cached in one batched call, so the
  GPU sees many scenes at once instead of one scene per forward."""
  todo=[];seen=set()
  for text,retake in items:
   f=cached(text,retake)
   if (text,retake) in seen or (f.exists() and f.stat().st_size>1000):continue
   seen.add((text,retake));todo.append((text,retake))
  if not todo:return
  wavs=generate([normalize_text_for_tts(t) for t,_ in todo])
  for (text,retake),w in zip(todo,wavs):
   if isinstance(w,np.ndarray) and abs(speed-1.0)>=0.01:w=change_tempo(w,st['sr'],speed)
   st['tts'].save(w,str(cached(text,retake)))

 def synth(text,retake=0):
  """Synthesize once, cached by content hash so a crashed/rerun revision
  resumes without re-paying, and an edited scene never plays back old audio.

  `retake` is how many times this scene's delivery was rejected. Same words,
  same settings, so without it the cache would return the identical take and
  "read this one better" would be a no-op."""
  prefetch([(text,retake)])
  return sf.read(str(cached(text,retake)),dtype='float32')[0]

 def scene_level(sc):
  return cfg.get('tts_scene_synthesis',True) and len(sc['narration'])<=cfg.get('tts_max_chars',256)
 first=[]
 for sc in req['scenes']:
  r=int(sc.get('retake',0))
  first+=[(sc['narration'],r)] if scene_level(sc) else [(t,r) for t in sc['texts']]
 prefetch(first)

 # Scene-level synthesis keeps the intonation arc across sentences: vieneu infers
 # each chunk independently, so one call per sentence resets the prosody every
 # time. Split the waveform afterwards to keep one subtitle cue per sentence.
 sr=st['sr'];flat=[];modes=[]
 for sc in req['scenes']:
  texts=sc['texts'];pieces=None;retake=int(sc.get('retake',0))
  if scene_level(sc):
   pieces=split_at(synth(sc['narration'],retake),sr,texts)
  if pieces is None:
   prefetch([(t,retake) for t in texts])
   pieces=[synth(t,retake) for t in texts]
   for i in range(len(pieces)-1):
    pad=pause_pad_samples(pieces[i],pieces[i+1],sr,float(sc['gaps'][i]))
    pieces[i]=np.concatenate([pieces[i],np.zeros(pad,dtype=np.float32)])
   modes.append({'scene_id':sc['scene_id'],'mode':'per-sentence'})
  else:modes.append({'scene_id':sc['scene_id'],'mode':'scene'})
  flat.extend([{'scene_id':sc['scene_id'],'text':t,'wav':w} for t,w in zip(texts,pieces)])
  flat[-1]['pause']=float(sc['tail'])

 # The pause belongs to the chunk that is ending, so the timeline stays contiguous
 # (pilot.py:161) and the subtitle cue holds through the breath.
 results=[]
 for i,x in enumerate(flat):
  w=x['wav']
  content_duration=len(w)/sr  # Chunk boundary, not detected phoneme timing.
  if 'pause' in x:
   nxt=flat[i+1]['wav'] if i+1<len(flat) else np.zeros(1,dtype=np.float32)
   w=np.concatenate([w,np.zeros(pause_pad_samples(w,nxt,sr,x['pause']),dtype=np.float32)])
  path=f'segment-{i:03}.wav'
  sf.write(str(out/path),w,sr,subtype='PCM_16')
  results.append({'scene_id':x['scene_id'],'text':x['text'],'path':path,'content_duration':content_duration})
 (out/'tts-result.json').write_text(json.dumps({'voice':str(st['voice']),'label':st['label'],'engine':st['engine'],'fallbacks':fallbacks,'settings':cfg,'scenes':modes,'segments':results},ensure_ascii=False,indent=2))

if __name__=='__main__':
 run(Path(sys.argv[1]),Path(sys.argv[2]))
