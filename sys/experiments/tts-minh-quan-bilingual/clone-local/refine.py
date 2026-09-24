from pathlib import Path
import json, hashlib, subprocess
import numpy as np
import soundfile as sf
from vieneu import Vieneu
P=Path(__file__).resolve().parent
O=P/'refinement'; O.mkdir(exist_ok=True)
tts=Vieneu(mode='v3turbo',backend='onnx',precision='fp32')
emb,codes=tts.encode_reference(P/'reference-original.wav',denoise=False)
np.savez_compressed(O/'profile-original.npz',speaker_emb=emb,codes=codes)
original={'speaker_emb':emb,'codes':codes}
z=np.load(P/'voice-profile.npz',allow_pickle=False)
clean={'speaker_emb':z['speaker_emb'],'codes':z['codes']}
texts={'same':'Xin chào, hôm nay chúng ta sẽ tìm hiểu cách deploy một ứng dụng lên server bằng docker và nginx.','mixed':'Trong tiếng Anh, <en>wake</en> có nghĩa là thức giấc. Ví dụ: <en>I wake at six every morning.</en>'}
rows=[]
for label,voice,temp in [('A',clean,.8),('B',original,.8),('C',original,.65)]:
 for key,text in texts.items():
  print(label,key,flush=True)
  np.random.seed(20260922)
  wav=np.asarray(tts.infer(text,voice=voice,temperature=temp,top_p=.95),dtype=np.float32)
  assert wav.size>4800 and np.isfinite(wav).all()
  raw=O/f'{label}-{key}-raw.wav'; out=O/f'{label}-{key}.wav'
  sf.write(raw,wav,48000,subtype='FLOAT')
  r=subprocess.run(['ffmpeg','-v','info','-i',str(raw),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
  m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
  gain=min(-23-float(m['input_i']),-1.5-float(m['input_tp']))
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',f'volume={gain}dB','-c:a','pcm_s16le',str(out)],check=True)
  rows.append(dict(file=out.name,text=text,denoise=label=='A',temperature=temp,top_p=.95,seconds=len(wav)/48000,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
(O/'result.json').write_text(json.dumps({'engine':'v3turbo-onnx-fp32','listening':'not_evaluated','clips':rows},ensure_ascii=False,indent=2))
print('DONE',flush=True)
