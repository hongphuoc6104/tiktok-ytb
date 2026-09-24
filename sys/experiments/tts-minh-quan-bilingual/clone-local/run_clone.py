"""Local reference-clone experiment; never writes production presets."""
import os,json,hashlib,html,subprocess,sys
from pathlib import Path
from importlib.metadata import version
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parent
source=P/'reference-original.wav'
texts=[('vi','Ví dụ này rất rõ ràng. Bạn tỉnh chưa? Mẹ bảo bé mở cửa rồi nghỉ một lát.'),('en','Wake. I wake at six every morning. Think about these three things before you leave.'),('mixed','Trong tiếng Anh, <en>wake</en> có nghĩa là thức giấc. Ví dụ: <en>I wake at six every morning.</en>')]
from vieneu import Vieneu
print('Đang nạp v3 Turbo local...',flush=True)
tts=Vieneu(mode='v3turbo',backend='onnx',precision='fp32')
name='MQ tham chiếu V4 — thử nghiệm'
print('Đang trích hồ sơ từ mẫu 5,09 giây...',flush=True)
profile=P/'voice-profile.npz'
if profile.exists():
 z=np.load(profile,allow_pickle=False)
 voice={'speaker_emb':z['speaker_emb'],'codes':z['codes']}
else:
 emb,codes=tts.encode_reference(source,denoise=True)
 np.savez_compressed(profile,speaker_emb=emb,codes=codes)
 voice={'speaker_emb':emb,'codes':codes}
meta={'name':name,'engine':'v3turbo','backend':'onnx','precision':'fp32','vieneu':version('vieneu'),'sea_g2p':version('sea-g2p'),'reference_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'profile_sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'temperature':0.8,'top_p':0.95,'speed':1.0,'denoise_reference':True,'note':'Local synthesis conditioned on V4 demo audio; NOT the V4 model. Listening quality not evaluated.','clips':[]}
for key,text in texts:
 for kind,v in [('clone',voice),('preset','Minh Quân Pro')]:
  stem=f'{key}-{kind}';raw=P/(stem+'-raw.wav');dest=P/(stem+'.wav')
  if not raw.exists():
   np.random.seed(20260922)
   print('Tạo',stem,flush=True)
   wav=np.asarray(tts.infer(text,voice=v,temperature=.8,top_p=.95),dtype=np.float32)
   assert wav.size>4800 and np.isfinite(wav).all()
   sf.write(raw,wav,48000,subtype='FLOAT')
  if not dest.exists():
   r=subprocess.run(['ffmpeg','-v','info','-i',str(raw),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
   m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1]);gain=min(-23-float(m['input_i']),-1.5-float(m['input_tp']))
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',f'volume={gain}dB','-c:a','pcm_s16le',str(dest)],check=True)
  w,sr=sf.read(dest);assert sr==48000 and len(w)>4800 and np.isfinite(w).all()
  meta['clips'].append({'file':dest.name,'kind':kind,'text':text,'duration':len(w)/sr,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(P/'result.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
page='<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Clone local từ mẫu Minh Quân Pro V4</title><body style="font:18px system-ui;background:#f5f6f0;color:#173d30;max-width:950px;margin:40px auto;padding:20px"><h1>Clone local từ mẫu Minh Quân Pro V4</h1><p>Âm thanh AI thử nghiệm bằng v3 Turbo trên máy. Không phải model V4. Chưa đánh giá chất lượng, chưa đặt mặc định.</p><h2>Mẫu gốc từ VieNeu V4</h2><audio controls src="reference-original.wav"></audio><p>Mẫu gốc giữ nguyên âm lượng; các bản thử bên dưới đã cân âm lượng để đối chiếu.</p>'
for key,text in texts:
 page+=f'<h2>{dict(vi="Tiếng Việt",en="Tiếng Anh",mixed="Việt–Anh xen kẽ")[key]}</h2><p>{html.escape(text.replace("<en>","").replace("</en>",""))}</p>'
 for kind,label in [('clone','Bản clone local từ mẫu V4'),('preset','Minh Quân Pro có sẵn — đối chứng')]:page+=f'<p><b>{label}</b></p><audio controls preload="metadata" src="{key}-{kind}.wav" style="width:100%"></audio>'
page+='<p>Nghe riêng wake, âm R, ví dụ, thanh điệu và độ giống mẫu. Chưa khẳng định clone sửa được lỗi phát âm.</p></body></html>'
(P/'index.html').write_text(page)
print('Hoàn thành:',P/'index.html',flush=True)
