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
 if args and (args[0]=='image' or args[0]=='video' or args[:2]==('character','create')):
  return subprocess.run(['node',str(p.root/'scripts/gflow_guard.mjs'),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
 return subprocess.run([str(exe),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
def request_video(*a,**k):
 cfg=config(a[0]) if a and hasattr(a[0],'root') else read(Path(__file__).resolve().parent/'config.json')
 if not cfg.get('video_generation') or cfg.get('credit_budget',0)<=0:
  raise Blocked('Video AI disabled or credit budget is zero')
 if len(a)>=3:
  p,j,scene=a[0],a[1],a[2]
  out=p.job(j)/'flow/videos';out.mkdir(parents=True,exist_ok=True)
  args=['video','--prompt',scene['prompt'],'--ratio','9:16','--out',str(out),'--profile',cfg['flow_profile']]
  return gflow(p,*args)
 return {'status':'video enabled'}

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

def audio(p,j,out):
 py=p.root/'.venv-tts/bin/python'
 if not py.exists():raise Blocked('Install local TTS environment')
 content=p.payload(j,'content');inputs=[{'scene_id':s['id'],'text':t} for s in content['scenes'] for t in chunks(s['narration'])]
 request=out/'request.json';write(request,inputs)
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
 mastered=out/'narration_eq.wav'
 subprocess.run(['ffmpeg','-y','-i',str(combined),'-af','equalizer=f=3500:t=q:w=1.5:g=-3.5,equalizer=f=220:t=q:w=1:g=2,lowpass=f=9500',str(mastered)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if mastered.exists() and mastered.stat().st_size>1000:shutil.move(str(mastered),str(combined))
 srt=out/'subtitles.srt';srt.write_text(make_srt(segments))
 return {'voice':meta['voice'],'backend':'onnx','wav':rel(p,j,combined),'srt':rel(p,j,srt),'duration':cursor,'segments':segments}

def render(p,j,out):
 content=p.payload(j,'content');imgs=p.payload(j,'images');snd=p.payload(j,'audio')
 public=out/'public';public.mkdir(exist_ok=True);shutil.copy(p.path(j,snd['wav']),public/'narration.wav')
 if (p.root/'scratch/narration_en.wav').exists():shutil.copy(p.root/'scratch/narration_en.wav',public/'narration_en.wav')
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
 props={'duration':snd['duration'],'scenes':scenes,'segments':snd['segments'],'aspect_ratio':ratio}
 write(out/'props.json',props)
 r=subprocess.run(['node',str(p.root/'renderer/render.mjs'),str(out.resolve())],cwd=p.root,capture_output=True,text=True,timeout=3600);(out/'render.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('Render or layout check failed; see render.log: '+r.stderr[-500:])
 result={'video':rel(p,j,out/'video.mp4'),'stills':[rel(p,j,out/(s['id']+'.png')) for s in scenes],'layout_report':rel(p,j,out/'layout.json'),'duration':snd['duration']}
 if (out/'video_16x9.mp4').exists():result['video_16x9']=rel(p,j,out/'video_16x9.mp4')
 if (out/'video_9x16.mp4').exists():result['video_9x16']=rel(p,j,out/'video_9x16.mp4')
 return result
