"""Replaceable providers; no provider can approve a module."""
import json, re, shutil, subprocess, time, wave
from pathlib import Path
from PIL import Image, ImageDraw
from pilot import Blocked,read,write,digest

def rel(p,j,path):return str(Path(path).relative_to(p.job(j)))
def config(p):return read(p.root/'config.json')
def gflow(p,*args,timeout=960):
 exe=p.root/'node_modules/.bin/gflow'
 if not exe.exists():raise Blocked('Install npm dependencies first')
 if args and args[0]=='video':raise Blocked('Video AI disabled')
 if args and (args[0]=='image' or args[:2]==('character','create')):
  return subprocess.run(['node',str(p.root/'scripts/gflow_guard.mjs'),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
 return subprocess.run([str(exe),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
def request_video(*a,**k):
 raise Blocked('Video AI disabled; image-only production')

def flow_action(p,a):
 j=a.job;p.gate(j,'images');cfg=config(p)
 if p.brief(j) and a.command in ['flow-reconcile','flow-confirm-registration']:
  import image_pipeline
  return image_pipeline.flow_action(p,a)
 if a.command=='flow-login':
  r=gflow(p,'auth','login','--profile',cfg['flow_profile'])
  if r.returncode:raise Blocked(r.stderr[-1500:])
  return {'login':'opened; user must sign in directly','output':r.stdout[-2000:]}
 if a.command=='flow-preflight':
  if not a.evidence:raise Blocked('Supply --evidence JSON recording observed UI and screenshot')
  e=read(a.evidence)
  if e.get('credits_per_generation')!=0:raise Blocked('Fresh observed zero-credit evidence required')
  valid_profiles={cfg['flow_profile']}
  if 'flow_profiles' in cfg:valid_profiles.update(cfg['flow_profiles'])
  valid_profiles.add('video-pilot')
  if e.get('mode')!='image' or e.get('model')!=cfg['flow_model'] or e.get('profile') not in valid_profiles or not e.get('observer') or not e.get('account_confirmed'):raise Blocked('Need observed image mode, exact model and confirmed account')
  if abs(time.time()-e.get('observed_at',0))>600:raise Blocked('Observation must be from last 10 minutes')
  shot=Path(e['screenshot']).resolve()
  with Image.open(shot) as im:im.verify()
  dest=p.job(j)/'flow/preflight.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(shot,dest)
  e['screenshot']=rel(p,j,dest);e['screenshot_hash']=digest(dest);write(p.job(j)/'flow/preflight.json',e)
  p.event(j,'images','ui_preflight_recorded',json.dumps(e,ensure_ascii=False));return {'preflight':'recorded, expires in 10 minutes; visual observation is not machine proof'}
 if a.command=='flow-reconcile':
  if not a.scene or not a.asset or not a.note:raise Blocked('Need scene, verified downloaded asset, and verification note')
  if a.scene not in {s['id'] for s in p.payload(j,'content')['scenes']}:raise Blocked('Unknown scene')
  q=p.job(j)/'flow'/f'{a.scene}.json'
  if not q.exists():raise Blocked('No submitted attempt')
  s=read(q)
  if s['state']!='ambiguous' and s['state']!='submitted':raise Blocked('Only reconcile ambiguous/submitted attempts')
  source=Path(a.asset).resolve()
  with Image.open(source) as im:
   im.load()
   if abs(im.width/im.height-9/16)>.03:raise Blocked('Wrong image ratio')
  dest=p.job(j)/'flow/assets'/f'{a.scene}-{int(time.time())}{source.suffix}';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(source,dest)
  s.update(state='downloaded',path=rel(p,j,dest),sha256=digest(dest),verification=a.note);write(q,s);p.event(j,'images','reconciled',a.note);return s

def generate_image(p,j,scene):
 cfg=config(p);base=p.job(j)/'flow';base.mkdir(exist_ok=True)
 attempt=base/(scene['id']+'.json');key=digest(p.root/'config.json')+scene['prompt']
 if attempt.exists():
  s=read(attempt)
  if s['key']==key:
   if s['state']=='downloaded':
    path=p.path(j,s['path'])
    if path.exists() and digest(path)==s['sha256']:return path
    raise Blocked('Downloaded original changed; reconcile manually')
   raise Blocked('Uncertain Flow request; inspect Flow and use flow-reconcile. No resubmission.')
  if s['state']!='downloaded':raise Blocked('Previous unresolved request must be reconciled first')
  shutil.copy(attempt,base/(scene['id']+f'-history-{time.time_ns()}.json'))
 pre=read(base/'preflight.json') if (base/'preflight.json').exists() else {}
 if time.time()-pre.get('observed_at',0)>600 or pre.get('mode')!='image' or pre.get('model')!=cfg['flow_model']:raise Blocked('Fresh Flow UI preflight required')
 if digest(p.path(j,pre['screenshot']))!=pre['screenshot_hash']:raise Blocked('Preflight screenshot changed')
 folder=base/'downloads'/f"{scene['id']}-{time.time_ns()}";folder.mkdir(parents=True)
 s={'state':'submitted','key':key,'scene_id':scene['id'],'prompt':scene['prompt'],'submitted_at':time.time(),'output_dir':rel(p,j,folder)};write(attempt,s)
 try:
  model_arg = 'nano-banana-pro' if 'pro' in cfg['flow_model'].lower() else ('nano-banana-2' if '2' in cfg['flow_model'] else cfg['flow_model'])
  r=gflow(p,'image','--id',scene['id'],'--prompt',scene['prompt'],'--model',model_arg,'--ratio','9:16','--outputs','1','--profile',cfg['flow_profile'],'--project',cfg['flow_project'],'--out',str(folder))
  (folder/'command.log').write_text(r.stdout+'\n'+r.stderr)
  if r.returncode:raise Blocked('Flow command failed; inspect command.log')
  candidates=[]
  for f in folder.rglob('*'):
   if f.is_file():
    try:
     with Image.open(f) as im:im.verify()
     candidates.append(f)
    except Exception:pass
  if len(candidates)!=1:raise Blocked('Cannot uniquely identify downloaded image')
  f=candidates[0];s.update(state='downloaded',path=rel(p,j,f),sha256=digest(f));write(attempt,s);return f
 except Exception as ex:
  s.update(state='ambiguous',error=str(ex));write(attempt,s);raise Blocked('Flow outcome ambiguous; no automatic resubmission: '+str(ex))

def images(p,j,out):
 if p.brief(j):
  import image_pipeline
  return image_pipeline.produce(p,j,out)
 items=[];thumbs=[]
 for s in p.payload(j,'content')['scenes']:
  source=generate_image(p,j,s);dest=out/(s['id']+source.suffix);shutil.copy(source,dest)
  items.append({'scene_id':s['id'],'path':rel(p,j,dest),'prompt':s['prompt'],'source':'google-flow'})
  with Image.open(dest) as im:thumbs.append(im.convert('RGB').resize((180,320)))
 sheet=Image.new('RGB',(540,700),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(thumbs):x=(i%3)*180;y=(i//3)*350;sheet.paste(im,(x,y));draw.text((x+8,y+325),items[i]['scene_id'],fill='black')
 f=out/'contact-sheet.jpg';sheet.save(f);return {'items':items,'contact_sheet':rel(p,j,f)}
def timestamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def make_srt(segs):return '\n'.join(f"{i}\n{timestamp(s['start'])} --> {timestamp(s['end'])}\n{s['text']}\n" for i,s in enumerate(segs,1))
def chunks(text):
 import re
 raw=re.split(r'(?<=[.!?])\s+', text.strip())
 parts=[]
 for s in raw:
  s=s.strip()
  if not s:continue
  if len(s)>180:
   sub=re.split(r'(?<=[,;:\-])\s+', s)
   parts.extend([x.strip() for x in sub if x.strip()])
  else:
   parts.append(s)
 return parts if parts else [text.strip()]

DEFAULT_PAUSE={'para':.70,'sentence':.50,'minor':.30,'tail':.35}

def gap_after(text,g):
 """Pause following a chunk inside a scene; mirrors vieneu's own gap table.

 Only used on the per-sentence fallback path -- scene-level synthesis gets
 these gaps from the model itself.
 """
 return g.get('sentence',DEFAULT_PAUSE['sentence']) if text.rstrip()[-1:] in '.!?…' else g.get('minor',DEFAULT_PAUSE['minor'])

def frames_of(path):
 with wave.open(str(path)) as wav:return wav.getnframes()

def master(src,dst,cfg):
 """EQ, then a static gain to target loudness with a true-peak limiter.

 loudnorm is used for ANALYSIS only: its dynamic mode pads and resamples to
 192 kHz, which would break the +/-30 ms duration gates in pilot.checks.
 No compressor: a limiter only touches the few samples above the ceiling, so
 it reaches the loudness target without flattening the prosody we just gained.
 alimiter needs level=disabled or it auto-normalises straight back to 0 dBFS.
 Every filter here is sample-preserving; the frame count is asserted anyway.
 """
 eq='equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=7000:t=q:w=2:g=-2.5'
 subprocess.run(['ffmpeg','-y','-i',str(src),'-af',eq,'-ar','48000','-c:a','pcm_s16le',str(dst)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if not (dst.exists() and dst.stat().st_size>1000):return
 r=subprocess.run(['ffmpeg','-v','info','-i',str(dst),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True)
 try:m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
 except ValueError:dst.unlink(missing_ok=True);return
 peak=float(cfg.get('audio_peak_db',-1.5));gain=float(cfg.get('audio_lufs',-14.))-float(m['input_i'])
 final=dst.with_name('narration_lv.wav')
 subprocess.run(['ffmpeg','-y','-i',str(dst),'-af',f'volume={gain:.2f}dB,alimiter=limit={10**(peak/20):.4f}:level=disabled','-ar','48000','-c:a','pcm_s16le',str(final)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 dst.unlink(missing_ok=True)
 if final.exists() and final.stat().st_size>1000 and frames_of(final)==frames_of(src):shutil.move(str(final),str(src))
 else:final.unlink(missing_ok=True)

def needs_en(p,j):
 """16:9 exports carry the English track; 9:16 carries Vietnamese."""
 b=p.brief(j)
 return bool(b) and b[0].get('aspect_ratio') in ('dual','16:9')

def english(p,j,out,cfg,scenes):
 py=p.root/'.venv-en/bin/python'
 if not py.exists():raise Blocked('Install the English TTS environment (.venv-en)')
 missing=[s['id'] for s in scenes if not s.get('narration_en')]
 if missing:raise Blocked('Missing narration_en for '+', '.join(missing))
 g=cfg.get('tts_pause',DEFAULT_PAUSE)
 items=[{'scene_id':s['id'],'narration_en':s['narration_en'],
         'tail':g.get('tail',DEFAULT_PAUSE['tail']) if k==len(scenes)-1 else g.get('para',DEFAULT_PAUSE['para'])}
        for k,s in enumerate(scenes)]
 keys=('en_voice','en_device','en_quantize','en_temperature','en_threads','en_seed')
 request=out/'request-en.json';write(request,{'settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'scenes':items})
 r=subprocess.run([str(py),str(p.root/'scripts/en_worker.py'),str(request),str(out)],capture_output=True,text=True,timeout=7200)
 (out/'tts-en.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('English TTS failed; see tts-en.log')
 meta=read(out/'en-result.json');cursor=0.;frames=[];params=None;done=[]
 for x in meta['scenes']:
  f=out/x['path']
  with wave.open(str(f)) as wav:
   fmt=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
   if params and fmt!=params:raise Blocked('Inconsistent English audio formats')
   params=fmt;d=wav.getnframes()/wav.getframerate();frames.append(wav.readframes(wav.getnframes()))
  done.append({'scene_id':x['scene_id'],'start':cursor,'end':cursor+d,'path':rel(p,j,f)});cursor+=d
 combined=out/'narration_en.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_en_eq.wav',cfg)
 return {'engine':meta['engine'],'voice':meta['voice'],'wav':rel(p,j,combined),'duration':cursor,'scenes':done}

def audio(p,j,out):
 py=p.root/'.venv-tts/bin/python'
 if not py.exists():raise Blocked('Install local TTS environment')
 content=p.payload(j,'content');cfg=config(p);g=cfg.get('tts_pause',DEFAULT_PAUSE)
 scenes=[{'scene_id':s['id'],'narration':s['narration'],'texts':chunks(s['narration'])} for s in content['scenes']]
 for k,sc in enumerate(scenes):
  sc['gaps']=[gap_after(t,g) for t in sc['texts'][:-1]]
  sc['tail']=g.get('tail',DEFAULT_PAUSE['tail']) if k==len(scenes)-1 else g.get('para',DEFAULT_PAUSE['para'])
 keys=('tts_voice','tts_temperature','tts_top_p','tts_max_chars','tts_scene_synthesis','tts_backend','tts_precision')
 request=out/'request.json';write(request,{'settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'scenes':scenes})
 result=subprocess.run([str(py),str(p.root/'tts_worker.py'),str(request),str(out)],capture_output=True,text=True,timeout=1800)
 (out/'tts.log').write_text(result.stdout+'\n'+result.stderr)
 if result.returncode:raise Blocked('Local TTS failed; see tts.log; no cloud fallback')
 meta=read(out/'tts-result.json');segments=[];cursor=0.;frames=[];params=None
 for x in meta['segments']:
  file=out/x['path']
  with wave.open(str(file)) as wav:
   fmt=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
   if params and fmt!=params:raise Blocked('Inconsistent TTS audio formats')
   params=fmt;duration=wav.getnframes()/wav.getframerate();frames.append(wav.readframes(wav.getnframes()))
  segments.append({'scene_id':x['scene_id'],'text':x['text'],'start':cursor,'end':cursor+duration,'path':rel(p,j,file)});cursor+=duration
 combined=out/'narration.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_eq.wav',cfg)
 srt=out/'subtitles.srt';srt.write_text(make_srt(segments))
 payload={'voice':meta['voice'],'backend':cfg.get('tts_backend','onnx'),'wav':rel(p,j,combined),'srt':rel(p,j,srt),'duration':cursor,'segments':segments}
 if needs_en(p,j):payload['en']=english(p,j,out,cfg,content['scenes'])
 return payload

def render(p,j,out):
 content=p.payload(j,'content');imgs=p.payload(j,'images');snd=p.payload(j,'audio')
 public=out/'public';public.mkdir(exist_ok=True);shutil.copy(p.path(j,snd['wav']),public/'narration.wav')
 en=snd.get('en')
 if en:shutil.copy(p.path(j,en['wav']),public/'narration_en.wav')
 scenes=[]
 image_by_id={x['scene_id']:x for x in imgs['items']}
 b=p.brief(j)[0] if p.brief(j) else None
 ratio=b.get('aspect_ratio','9:16') if b else '9:16'
 for scene in content['scenes']:
  img=image_by_id[scene['id']]
  src_file=p.path(j,img['path'])
  dst=public/(scene['id']+src_file.suffix);shutil.copy(src_file,dst)
  for sub_img in src_file.parent.glob(scene['id']+'_*.png'):shutil.copy(sub_img,public/sub_img.name)
  segs=[x for x in snd['segments'] if x['scene_id']==scene['id']]
  sc_dict={'id':scene['id'],'title':scene['title'],'image':dst.name,'start':segs[0]['start'],'end':segs[-1]['end']}
  sub_b=public/(scene['id']+'_b.png')
  sub_a=public/(scene['id']+'_a.png')
  if sub_b.exists():
   first_src=sub_a.name if sub_a.exists() else dst.name
   sc_dict['images']=[{'src':first_src,'at':0},{'src':sub_b.name,'at':3.5}]
  scenes.append(sc_dict)
 props={'duration':snd['duration'],'scenes':scenes,'segments':snd['segments'],'aspect_ratio':ratio,'render_concurrency':config(p).get('render_concurrency',2)}
 if en:
  # 16:9 follows the English timeline; reusing the Vietnamese one leaves the
  # tail silent and drifts every image cut against the narration.
  span={x['scene_id']:x for x in en['scenes']}
  props['en_duration']=en['duration']
  props['en_scenes']=[{**sc,'start':span[sc['id']]['start'],'end':span[sc['id']]['end']} for sc in scenes]
 write(out/'props.json',props)
 r=subprocess.run(['node',str(p.root/'renderer/render.mjs'),str(out.resolve())],cwd=p.root,capture_output=True,text=True,timeout=3600);(out/'render.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('Render or layout check failed; see render.log: '+r.stderr[-500:])
 result={'video':rel(p,j,out/'video.mp4'),'stills':[rel(p,j,out/(s['id']+'.png')) for s in scenes],'layout_report':rel(p,j,out/'layout.json'),'duration':en['duration'] if ratio=='16:9' else snd['duration']}
 if (out/'video_16x9.mp4').exists():result['video_16x9']=rel(p,j,out/'video_16x9.mp4')
 if (out/'video_9x16.mp4').exists():result['video_9x16']=rel(p,j,out/'video_9x16.mp4')
 return result
