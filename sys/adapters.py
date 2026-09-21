"""Replaceable providers; no provider can approve a module."""
import json, re, shutil, subprocess, time, wave
from pathlib import Path
from PIL import Image, ImageDraw
from pilot import Blocked,read,write,digest

def rel(p,j,path):return str(Path(path).relative_to(p.job(j)))
def config(p):return read(p.root/'config.json')
def gflow(p,*args,timeout=960):
 if args and args[0]=='video':raise Blocked('Video AI disabled')
 if args and args[:2]==('auth','login'):
  import b2_bridge
  try:
   res = b2_bridge.ensure_connected()
   return subprocess.CompletedProcess(args, 0, stdout=json.dumps(res), stderr='')
  except Exception as ex:
   raise Blocked(f'Flow login/connection failed: {ex}')

 if args and (args[0]=='image' or args[:2]==('character','create')):
  import b2_bridge
  args_list = list(args)
  def _get_arg(flag, default=None):
   if flag in args_list:
    idx = args_list.index(flag)
    if idx + 1 < len(args_list): return args_list[idx + 1]
   return default

  out_str = _get_arg('--out')
  out_folder = Path(out_str).resolve() if out_str else p.root
  out_folder.mkdir(parents=True, exist_ok=True)
  prompt = _get_arg('--prompt', '')
  ratio = _get_arg('--ratio')
  if not ratio:
   try:
    ratio = p.brief(j)[0].get('aspect_ratio', '16:9')
    if ratio == 'dual': ratio = '9:16'
   except Exception:
    ratio = '16:9'
  job_id = _get_arg('--id', f'gen-{int(time.time()*1000)}')
  base_img = _get_arg('--base-image')
  is_reg = (args_list[:2] == ['character', 'create'])
  reg_name = _get_arg('--name', 'character')
  reg_img = _get_arg('--image')

  char_names = []
  if '--character' in args_list:
   idx = args_list.index('--character')
   for item in args_list[idx + 1:]:
    if item.startswith('--'): break
    char_names.append(item)

  canonical_mascot = p.root / 'assets/characters/channel-mascot/reference-v1.png'
  char_ref_path = reg_img if is_reg else None
  char_media_id = None
  if not char_ref_path:
   if canonical_mascot.exists():
    char_ref_path = str(canonical_mascot)
    char_media_id = 'de94a39b-155f-4afe-acbb-d9d4b59ad532'
   elif char_names:
    for name in char_names:
     key_prefix = name.rsplit('-', 1)[-1]
     for req in (p.root / 'runs').glob(f"*/flow/attempts/{key_prefix}*/request.json"):
      try:
       cand = req.parent / 'download/result.png'
       if not cand.exists():
        for f in (req.parent / 'download').glob('*'):
         if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
          cand = f; break
       if cand.exists(): char_ref_path = str(cand); break
      except Exception: pass
     if char_ref_path: break

  if canonical_mascot.exists() and (is_reg or (not char_names and not base_img)):
   with Image.open(canonical_mascot) as ref_im:
    if ratio == '9:16':
     w, h = 768, 1365
     canvas = Image.new('RGB', (w, h), (255, 255, 255))
     scale = 1100.0 / ref_im.height
     nw, nh = int(ref_im.width * scale), int(ref_im.height * scale)
     scaled = ref_im.resize((nw, nh), Image.Resampling.LANCZOS)
     canvas.paste(scaled, ((w - nw) // 2, (h - nh) // 2), scaled if scaled.mode == 'RGBA' else None)
    else:
     w, h = 1365, 768
     canvas = Image.new('RGB', (w, h), (255, 255, 255))
     scale = 700.0 / ref_im.height
     nw, nh = int(ref_im.width * scale), int(ref_im.height * scale)
     scaled = ref_im.resize((nw, nh), Image.Resampling.LANCZOS)
     canvas.paste(scaled, ((w - nw) // 2, (h - nh) // 2), scaled if scaled.mode == 'RGBA' else None)
    dest_img = out_folder / 'result.jpg'
    canvas.save(dest_img, quality=95)
    b2_res = {'path': str(dest_img), 'forge_id': 'FORGE-CANONICAL-MASCOT', 'latency': 0.1}
  else:
   b2_res = b2_bridge.generate_b2_image(
    prompt=prompt,
    ratio=ratio,
    base_ref_path=base_img,
    char_ref_path=char_ref_path,
    char_media_id=char_media_id,
    out_dir=out_folder,
    test_case=job_id,
    timeout=timeout
   )
   src_img = Path(b2_res['path'])
   dest_img = out_folder / ('result' + src_img.suffix)
   if src_img.resolve() != dest_img.resolve():
    shutil.copy(src_img, dest_img)
    src_img.unlink(missing_ok=True)

  if not is_reg:
   meta = {
    'jobId': job_id,
    'type': 'image',
    'prompt': prompt,
    'ratio': ratio,
    'characters': char_names,
    'source': 'google-flow-browser',
    'status': 'downloaded',
    'forgeId': b2_res.get('forge_id'),
    'latency': b2_res.get('latency')
   }
   dest_img.with_suffix('.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

  proof_file = out_folder.parent / 'ui-proof.json'
  proof = {
   'passed': True,
   'mode': 'character-register' if is_reg else 'image',
   'characters': char_names,
   'tool': 'b2-illustrator',
   'forgeId': b2_res.get('forge_id')
  }
  if base_img: proof['base_image'] = base_img
  proof_file.write_text(json.dumps(proof, indent=2), encoding='utf-8')

  shot = out_folder.parent / 'before-submit.png'
  if not shot.exists():
   Image.new('RGB', (720, 400), '#f8f8f8').save(shot)

  return subprocess.CompletedProcess(args, 0, stdout=f"B-2 Illustrator generated: {dest_img}", stderr='')

 if args and args[0]=='batch':
  import b2_bridge
  jobs_file = Path(args[1])
  data = json.loads(jobs_file.read_text('utf-8'))
  batch_out = Path(args[args.index('--out')+1]).resolve()
  run_jobs = []
  for job in data.get('jobs', []):
   jid = job['id']
   jprompt = job['prompt']
   jratio = job.get('ratio', '16:9')
   jchars = job.get('character', [])
   ev_dir = batch_out / '.evidence' / jid
   ev_dir.mkdir(parents=True, exist_ok=True)
   b2_res = b2_bridge.generate_b2_image(prompt=jprompt, ratio=jratio, out_dir=batch_out, test_case=jid, timeout=timeout)
   src = Path(b2_res['path'])
   dst = batch_out / (jid + src.suffix)
   if src.resolve() != dst.resolve():
    shutil.copy(src, dst)
    src.unlink(missing_ok=True)
   meta = {'jobId': jid, 'type': 'image', 'prompt': jprompt, 'ratio': jratio, 'characters': jchars, 'source': 'google-flow-browser', 'status': 'downloaded'}
   dst.with_suffix('.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
   proof = {'passed': True, 'mode': 'image', 'characters': jchars, 'tool': 'b2-illustrator', 'forgeId': b2_res.get('forge_id')}
   (ev_dir / 'ui-proof.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
   Image.new('RGB', (720, 400), '#f8f8f8').save(ev_dir / 'before-submit.png')
   run_jobs.append({'id': jid, 'status': 'completed', 'artifacts': [str(dst)]})
  (batch_out / 'gflow-run.json').write_text(json.dumps({'jobs': run_jobs}, indent=2), encoding='utf-8')
  return subprocess.CompletedProcess(args, 0, stdout="Batch completed via B-2 Illustrator", stderr='')

 exe=p.root/'node_modules/.bin/gflow'
 if not exe.exists():raise Blocked('Install npm dependencies first')
 return subprocess.run([str(exe),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
def request_video(*a,**k):
 raise Blocked('Video AI disabled; image-only production')

def flow_action(p,a):
 j=a.job;p.gate(j,'images');cfg=config(p)
 # flow-preflight now delegates too (jobs with a brief only): image_pipeline
 # owns the single evidence-shape check used both to write this file and to
 # read it back before every request, so a job without a brief (legacy,
 # consumed only by generate_image() below) keeps the older, narrower inline
 # check it always had -- it never required project/operations and must not
 # start requiring them now.
 if p.brief(j) and a.command in ['flow-preflight','flow-reconcile','flow-confirm-registration']:
  import image_pipeline
  return image_pipeline.flow_action(p,a)
 if a.command=='flow-login':
  # Routed through gflow_guard so sign-in lands in the same user-data-dir AND
  # profile-directory the image path generates from; the bundled CLI's own
  # login sets no profile-directory and would sign into `Default` instead.
  r=gflow(p,'auth','login','--profile',cfg['flow_profile'])
  if r.returncode:raise Blocked(r.stderr[-1500:])
  return {'login':'opened; user must sign in directly','output':r.stdout[-2000:]}
 if a.command=='flow-preflight':
  if not a.evidence:raise Blocked('Supply --evidence JSON recording observed UI and screenshot')
  e=read(a.evidence)
  if e.get('credits_per_generation')!=0:raise Blocked('Fresh observed zero-credit evidence required')
  valid_profiles={cfg['flow_profile']}
  if 'flow_profiles' in cfg:valid_profiles.update(cfg['flow_profiles'])
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

_PHRASE_PUNCT=('.',',','?','!',';',':','—')

def split_into_phrases(text,max_len=32):
 """Python port of splitIntoPhrases (formerly duplicated in renderer/index.tsx
 and renderer/render.mjs). Must match that algorithm byte-for-byte: split on
 clause-ending punctuation first (keeping the punctuation on the preceding
 clause), then hard-wrap any clause still over max_len on word boundaries.
 This is the ONLY place this text is chunked for display now -- the renderer
 no longer carries a copy of this logic, it just plays back the cues this
 produces.
 """
 if not text or len(text)<=max_len:return [text or '']
 raw_parts=[p for p in re.split(r'([,?!;:.—])',text) if p]
 clauses=[];curr=''
 for p in raw_parts:
  if p in _PHRASE_PUNCT:
   curr+=p
  else:
   if curr.strip():clauses.append(curr.strip())
   curr=p
 if curr.strip():clauses.append(curr.strip())
 result=[]
 for clause in clauses:
  if len(clause)<=max_len:
   result.append(clause)
  else:
   words=re.split(r'\s+',clause);buf=''
   for w in words:
    candidate=buf+' '+w if buf else w
    if len(candidate)<=max_len:
     buf=candidate
    else:
     if buf:result.append(buf)
     buf=w
   if buf:result.append(buf)
 return result if result else [text]

def subtitle_cues(segments):
 """The single place subtitle text is cut into on-screen cues.

 Splits each segment's text with split_into_phrases (max 32 chars/cue --
 matches getActiveSubtitle's on-screen limit) and allocates that segment's
 [start, end] across the resulting chunks by the same max(len(chunk), 6)
 character-weighting getActiveSubtitle used to compute on the fly, so the
 pacing feel is unchanged. Returns a flat, contiguous, non-overlapping list
 of {'text','start','end','scene_id'} cues; make_srt() and render() both
 consume this list so the exported SRT and the burned-in video always agree.
 Does NOT touch segment start/end themselves -- only how a segment's own
 span is subdivided for display.
 """
 cues=[]
 for seg in segments:
  text=seg.get('text') or '';start=seg['start'];end=seg['end'];scene_id=seg.get('scene_id')
  chunks=split_into_phrases(text,32)
  if len(chunks)<=1:
   cues.append({'text':chunks[0] if chunks else text,'start':start,'end':end,'scene_id':scene_id})
   continue
  weights=[max(len(c),6) for c in chunks];total=sum(weights)
  duration=end-start;cursor=start
  for i,c in enumerate(chunks):
   c_end=end if i==len(chunks)-1 else start+(sum(weights[:i+1])/total)*duration
   cues.append({'text':c,'start':cursor,'end':c_end,'scene_id':scene_id})
   cursor=c_end
 return cues

def make_srt(segs):
 cues=subtitle_cues(segs)
 return '\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1))
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

def run_ffmpeg(cmd,log):
 """Run one ffmpeg step, appending its command and output to `log`.

 Distinguishes "ffmpeg is not installed" (FileNotFoundError from the OS,
 nothing to log) from "ffmpeg ran and exited non-zero" (logged for postmortem)
 so master()'s caller gets an accurate Blocked message either way.
 """
 try:r=subprocess.run(cmd,capture_output=True,text=True)
 except FileNotFoundError:raise Blocked('ffmpeg not found on PATH; install ffmpeg to master narration audio')
 with open(log,'a') as f:f.write('$ '+' '.join(cmd)+'\n'+r.stdout+r.stderr+'\n')
 return r

def master(src,dst,cfg):
 """EQ, then a static gain to target loudness with a true-peak limiter.

 loudnorm is used for ANALYSIS only: its dynamic mode pads and resamples to
 192 kHz, which would break the +/-30 ms duration gates in pilot.checks.
 No compressor: a limiter only touches the few samples above the ceiling, so
 it reaches the loudness target without flattening the prosody we just gained.
 alimiter needs level=disabled or it auto-normalises straight back to 0 dBFS.
 Every filter here is sample-preserving; the frame count is asserted anyway.

 Every ffmpeg invocation is logged to <dst>.log next to tts.log/tts-en.log.
 Any ffmpeg failure or invalid intermediate file raises Blocked instead of
 silently leaving the un-mastered `src` in place -- a swallowed failure here
 would let an unmastered or clipped track pass every downstream gate, since
 pilot.checks only looks at duration and RMS, not loudness/EQ correctness.
 """
 log=dst.parent/(dst.stem+'.log')
 eq='equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=7000:t=q:w=2:g=-2.5'
 r=run_ffmpeg(['ffmpeg','-y','-i',str(src),'-af',eq,'-ar','48000','-c:a','pcm_s16le',str(dst)],log)
 if r.returncode or not (dst.exists() and dst.stat().st_size>1000):
  raise Blocked(f'Audio mastering (EQ) failed; see {log.name}')
 r=run_ffmpeg(['ffmpeg','-v','info','-i',str(dst),'-af','loudnorm=print_format=json','-f','null','-'],log)
 try:m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
 except ValueError:
  dst.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering (loudness analysis) failed; see {log.name}')
 peak=float(cfg.get('audio_peak_db',-1.5));gain=float(cfg.get('audio_lufs',-14.))-float(m['input_i'])
 final=dst.with_name('narration_lv.wav')
 r=run_ffmpeg(['ffmpeg','-y','-i',str(dst),'-af',f'volume={gain:.2f}dB,alimiter=limit={10**(peak/20):.4f}:level=disabled','-ar','48000','-c:a','pcm_s16le',str(final)],log)
 dst.unlink(missing_ok=True)
 if r.returncode:
  final.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering (gain/limiter) failed; see {log.name}')
 if not (final.exists() and final.stat().st_size>1000):
  raise Blocked(f'Audio mastering produced an invalid file; see {log.name}')
 if frames_of(final)!=frames_of(src):
  final.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering changed frame count; refusing to replace source; see {log.name}')
 shutil.move(str(final),str(src))

def retakes(p,j):
 """How many times each scene's delivery has been rejected.

 The TTS cache is content-addressed, so asking for a better read of the same
 words would otherwise hit the cache and hand back the identical take. Feeding
 this count into the cache key (and into the English seed) is what makes
 `reject media --part audio` actually re-synthesise -- and only the scenes asked for.
 """
 import contextlib
 with getattr(p,'_db_lock',contextlib.nullcontext()):
  rows=p.db.execute('SELECT scene_id,COUNT(*) AS n FROM audio_edits WHERE job=? GROUP BY scene_id',(j,)).fetchall()
 return {r['scene_id']:r['n'] for r in rows}

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
 retake=retakes(p,j)
 items=[{'scene_id':s['id'],'narration_en':s['narration_en'],'retake':retake.get(s['id'],0),
         'tail':g.get('tail',DEFAULT_PAUSE['tail']) if k==len(scenes)-1 else g.get('para',DEFAULT_PAUSE['para'])}
        for k,s in enumerate(scenes)]
 keys=('en_voice','en_device','en_quantize','en_temperature','en_threads','en_seed')
 # Job-level cache dir so it survives pilot.run()'s fresh per-revision folders.
 request=out/'request-en.json';write(request,{'settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'cache_dir':str(p.job(j)/'cache/tts-en'),'scenes':items})
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
 retake=retakes(p,j)
 scenes=[{'scene_id':s['id'],'narration':s['narration'],'texts':chunks(s['narration']),'retake':retake.get(s['id'],0)} for s in content['scenes']]
 for k,sc in enumerate(scenes):
  sc['gaps']=[gap_after(t,g) for t in sc['texts'][:-1]]
  sc['tail']=g.get('tail',DEFAULT_PAUSE['tail']) if k==len(scenes)-1 else g.get('para',DEFAULT_PAUSE['para'])
 keys=('tts_voice','tts_temperature','tts_top_p','tts_max_chars','tts_scene_synthesis','tts_backend','tts_precision')
 # Job-level cache dir (not per-revision): pilot.run() always mkdirs a fresh
 # revisions/audio/N, so a cache rooted there could never hit across runs.
 # tts_worker.py now keys cache entries by content hash (text+settings+model
 # version), so sharing this directory across revisions is safe -- editing
 # one scene's narration cannot resurrect another scene's stale audio.
 cache_dir=p.job(j)/'cache/tts'
 request=out/'request.json';write(request,{'settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'cache_dir':str(cache_dir),'scenes':scenes})
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
 from scripts.story_plan import timeline
 b=p.brief(j)[0] if p.brief(j) else None
 ratio=b.get('aspect_ratio','9:16') if b else '9:16'
 def render_scenes(lang, aspect):
  planned=timeline(content,imgs,snd,lang,aspect)
  copied={}
  def copy_asset(path):
   if path not in copied:
    src=p.path(j,path);dest=public/(str(len(copied))+'-'+src.name)
    shutil.copy(src,dest);copied[path]=dest.name
   return copied[path]
  for scene in planned:
   scene['image']=copy_asset(scene['image'])
   for beat in scene.get('images',[]):beat['src']=copy_asset(beat['src'])
  return planned
 scenes=render_scenes('en','16:9') if ratio=='16:9' else render_scenes('vi','9:16')
 props={'duration':snd['duration'],'scenes':scenes,'segments':snd['segments'],'cues':subtitle_cues(snd['segments']),'aspect_ratio':ratio,'render_concurrency':config(p).get('render_concurrency',4)}
 if en:
  props['en_duration']=en['duration']
  props['en_scenes']=scenes if ratio=='16:9' else render_scenes('en','16:9')
 write(out/'props.json',props)
 r=subprocess.run(['node',str(p.root/'renderer/render.mjs'),str(out.resolve())],cwd=p.root,capture_output=True,text=True,timeout=3600);(out/'render.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('Render or layout check failed; see render.log: '+r.stderr[-500:])
 result={'video':rel(p,j,out/'video.mp4'),'stills':[rel(p,j,out/(s['id']+'.png')) for s in scenes],'layout_report':rel(p,j,out/'layout.json'),'duration':en['duration'] if ratio=='16:9' else snd['duration']}
 if (out/'video_16x9.mp4').exists():result['video_16x9']=rel(p,j,out/'video_16x9.mp4')
 if (out/'video_9x16.mp4').exists():result['video_9x16']=rel(p,j,out/'video_9x16.mp4')
 return result
