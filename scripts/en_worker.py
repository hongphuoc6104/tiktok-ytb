"""English narration worker. Runs in .venv-en; Chatterbox base, built-in voice.

One render per scene so the 16:9 cut points follow the English delivery rather
than the Vietnamese timeline. No per-sentence split: the 16:9 export hides
subtitles, so scene granularity is all the renderer needs.
"""
import json,re,sys,warnings
from pathlib import Path
warnings.filterwarnings('ignore')
import numpy as np,soundfile as sf,torch,torchaudio
from chatterbox.tts import ChatterboxTTS

SR=48000

def sentences(text,limit):
 """Whole scene in one pass when it fits; else split on sentence ends."""
 text=text.strip()
 if len(text)<=limit:return [text]
 out=[]
 for s in re.split(r'(?<=[.!?])\s+',text):
  s=s.strip()
  if s:out.append(s)
 return out or [text]

def tail_silence(w,sr,thresh_db=-40.,win_s=0.01):
 win=max(1,int(win_s*sr));n=w.size//win
 if n==0:return 0
 env=np.abs(w[:n*win]).reshape(n,win).mean(1)
 loud=np.flatnonzero(env>10**(thresh_db/20))
 return w.size if not loud.size else w.size-(int(loud[-1])+1)*win

source,out=Path(sys.argv[1]),Path(sys.argv[2]);req=json.loads(source.read_text())
cfg=req['settings']
model=ChatterboxTTS.from_pretrained(device=cfg.get('en_device','cpu'))
resample=torchaudio.transforms.Resample(model.sr,SR) if model.sr!=SR else None
gen=dict(exaggeration=cfg.get('en_exaggeration',.5),cfg_weight=cfg.get('en_cfg_weight',.5),temperature=cfg.get('en_temperature',.8))
limit=cfg.get('en_max_chars',300);gap=float(cfg.get('en_sentence_pause',.35))
raw=out/'raw-en';raw.mkdir(exist_ok=True);scenes=[]
for sc in req['scenes']:
 f=raw/(sc['scene_id']+'.wav')
 if not (f.exists() and f.stat().st_size>1000):
  parts=[]
  for k,piece in enumerate(sentences(sc['narration_en'],limit)):
   w=model.generate(piece,**gen)
   if resample is not None:w=resample(w)
   parts.append(w.squeeze(0).numpy().astype(np.float32))
   if k:parts.insert(-1,np.zeros(int(gap*SR),dtype=np.float32))
  sf.write(str(f),np.concatenate(parts),SR,subtype='PCM_16')
 scenes.append({'scene_id':sc['scene_id'],'wav':sf.read(str(f),dtype='float32')[0],'tail':float(sc['tail'])})
# Pause baked into the scene file so the timeline stays contiguous, as on the VN path.
results=[]
for i,sc in enumerate(scenes):
 w=sc['wav'];pad=max(0,int(sc['tail']*SR)-tail_silence(w,SR))
 path=f"en-{sc['scene_id']}.wav"
 sf.write(str(out/path),np.concatenate([w,np.zeros(pad,dtype=np.float32)]),SR,subtype='PCM_16')
 results.append({'scene_id':sc['scene_id'],'path':path})
(out/'en-result.json').write_text(json.dumps({'engine':'chatterbox','voice':'default','settings':cfg,'scenes':results},ensure_ascii=False,indent=2))
