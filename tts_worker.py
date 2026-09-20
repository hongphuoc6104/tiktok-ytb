"""Dedicated local-only environment; downloads public model weights on first use."""
import json,sys
from pathlib import Path
from vieneu import Vieneu
source,out=Path(sys.argv[1]),Path(sys.argv[2]);items=json.loads(source.read_text())
tts=Vieneu(mode='v3turbo',backend='onnx',precision='fp32')
voices=list(tts.list_preset_voices())
if not voices:raise RuntimeError('No local preset voices')
voice_id=tts._default_voice
if voice_id not in {v for _,v in voices}:raise RuntimeError('Default local voice unavailable')
label=next(label for label,v in voices if v==voice_id)
results=[]
for i,item in enumerate(items):
 path=f'segment-{i:03}.wav'
 target=out/path
 if not (target.exists() and target.stat().st_size>1000):
  audio=tts.infer(item['text'],voice=voice_id,temperature=0.35,silence_p=0.08)
  tts.save(audio,str(target))
 results.append({**item,'path':path})
(out/'tts-result.json').write_text(json.dumps({'voice':str(voice_id),'label':label,'segments':results},ensure_ascii=False,indent=2))
