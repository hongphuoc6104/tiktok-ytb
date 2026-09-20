"""Dedicated local-only environment; downloads public model weights on first use."""
import json,sys
from pathlib import Path
import numpy as np,soundfile as sf
from vieneu import Vieneu
from vieneu_utils.core_utils import pause_pad_samples

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

source,out=Path(sys.argv[1]),Path(sys.argv[2]);req=json.loads(source.read_text())
cfg=req['settings']
tts=Vieneu(mode='v3turbo',backend=cfg.get('tts_backend','onnx'),precision=cfg.get('tts_precision','fp32'))
voices={v:label for label,v in tts.list_preset_voices()}
if not voices:raise RuntimeError('No local preset voices')
voice_id=tts.resolve_voice_name(cfg.get('tts_voice')) or tts._default_voice
if voice_id not in voices:raise RuntimeError('Requested local voice unavailable')
sr=tts.sample_rate;raw=out/'raw';raw.mkdir(exist_ok=True)
def synth(text,name):
 """Synthesize once, cached raw so a crashed revision resumes without re-paying."""
 f=raw/(name+'.wav')
 if not (f.exists() and f.stat().st_size>1000):
  tts.save(tts.infer(text,voice=voice_id,temperature=cfg['tts_temperature'],top_p=cfg['tts_top_p']),str(f))
 return sf.read(str(f),dtype='float32')[0]

# Scene-level synthesis keeps the intonation arc across sentences: vieneu infers
# each chunk independently, so one call per sentence resets the prosody every
# time. Split the waveform afterwards to keep one subtitle cue per sentence.
flat=[];modes=[]
for sc in req['scenes']:
 texts=sc['texts'];pieces=None
 if cfg.get('tts_scene_synthesis',True) and len(sc['narration'])<=cfg.get('tts_max_chars',256):
  pieces=split_at(synth(sc['narration'],sc['scene_id']),sr,texts)
 if pieces is None:
  pieces=[synth(t,f"{sc['scene_id']}-{i:02}") for i,t in enumerate(texts)]
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
 if 'pause' in x:
  nxt=flat[i+1]['wav'] if i+1<len(flat) else np.zeros(1,dtype=np.float32)
  w=np.concatenate([w,np.zeros(pause_pad_samples(w,nxt,sr,x['pause']),dtype=np.float32)])
 path=f'segment-{i:03}.wav'
 sf.write(str(out/path),w,sr,subtype='PCM_16')
 results.append({'scene_id':x['scene_id'],'text':x['text'],'path':path})
(out/'tts-result.json').write_text(json.dumps({'voice':str(voice_id),'label':voices[voice_id],'settings':cfg,'scenes':modes,'segments':results},ensure_ascii=False,indent=2))
