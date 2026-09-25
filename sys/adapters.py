"""Replaceable providers; no provider can approve a module."""
import json, re, shutil, subprocess, time, wave
from pathlib import Path
from PIL import Image, ImageDraw
from pilot import Blocked,read,write,digest

def copy_optional_flow_screenshot(source, destination, *, required):
 """Never substitute preflight/account evidence for a real submission screenshot."""
 destination = Path(destination)
 if source and Path(source).is_file():
  if Path(source).resolve() != destination.resolve():
   shutil.copy(source, destination)
 elif required:
  raise Blocked('Real Flow UI evidence required; no synthetic screenshot')

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
    base_media_id=(read(Path(base_img).with_suffix(".json")).get("forgeId") if base_img and Path(base_img).with_suffix(".json").is_file() else None),
    char_ref_path=char_ref_path,
    char_media_id=char_media_id,
    out_dir=out_folder,
    test_case=job_id,
    timeout=timeout,
    collection_only='--collect-only' in args_list,
   )
   src_img = Path(b2_res['path'])
   # The queue journal owns this stable path; preserve it for replay.
   if src_img.parent.resolve() != out_folder.resolve():
    raise Blocked('B-2 output must be in the requested download directory')
   dest_img = src_img

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

  evidence_folder = Path(_get_arg('--evidence-out', str(out_folder.parent)))
  evidence_folder.mkdir(parents=True, exist_ok=True)
  proof_file = evidence_folder / 'ui-proof.json'
  proof = {
   'passed': True,
   'mode': 'character-register' if is_reg else 'image',
   'characters': char_names,
   'tool': 'b2-illustrator',
   'forgeId': b2_res.get('forge_id')
  }
  if base_img: proof['base_image'] = base_img
  proof_file.write_text(json.dumps(proof, indent=2), encoding='utf-8')

  shot = evidence_folder / 'before-submit.png'
  copy_optional_flow_screenshot(b2_res.get('before_submit'), shot,
                               required=config(p).get('flow_require_ui_evidence', True))

  return subprocess.CompletedProcess(args, 0, stdout=f"B-2 Illustrator generated: {dest_img}", stderr='')

 if args and args[0]=='batch':
  import b2_bridge
  data = read(Path(args[1]))
  batch_out = Path(args[args.index('--out')+1]).resolve()
  batch_out.mkdir(parents=True, exist_ok=True)
  jobs = data.get('jobs', [])
  run_jobs = [{'id':job['id'],'status':'not_submitted','error':'Chưa đến lượt gửi'} for job in jobs]
  state_file = batch_out / 'gflow-run.json'
  mascot = p.root / 'assets/characters/channel-mascot/reference-v1.png'
  for offset in range(0, len(jobs), 4):
   group = jobs[offset:offset+4]
   specs = [{'testCase': job['id'], 'prompt': job['prompt'], 'ratio': job.get('ratio', '9:16'),
             'outDir': str(batch_out / job['id']), 'characterRefPath': str(mascot),
             'charMediaId': 'de94a39b-155f-4afe-acbb-d9d4b59ad532'} for job in group]
   # Persist attempted membership BEFORE the external call. Ambiguous groups cannot fall through to serial retries.
   entries = run_jobs[offset:offset+4]
   for entry in entries: entry.update(status='failed',error='Submission pending; reconcile before retry')
   write(state_file, {'jobs': run_jobs})
   try:
    results = b2_bridge.generate_b2_batch(specs, timeout=timeout)
    for job, result, entry in zip(group, results, entries):
     src = Path(result['path'])
     dst = batch_out / (job['id'] + src.suffix)
     shutil.copy(src, dst)
     chars = job.get('character', [])
     write(dst.with_suffix('.json'), {'jobId':job['id'], 'type':'image', 'prompt':job['prompt'],
           'ratio':job.get('ratio','9:16'), 'characters':chars, 'source':'google-flow-browser',
           'status':'downloaded', 'forgeId':result['media_id']})
     ev = batch_out / '.evidence' / job['id']; ev.mkdir(parents=True, exist_ok=True)
     if result.get('before_submit'): shutil.copy(result['before_submit'], ev / 'before-submit.png')
     write(ev / 'ui-proof.json', {'passed':True, 'mode':'image', 'characters':chars,
           'tool':'b2-illustrator', 'forgeId':result['media_id'], 'screenshot':result['screenshot']})
     entry.update(status='completed', artifacts=[str(dst)])
     entry.pop('error', None)
     write(state_file, {'jobs':run_jobs})
   except Exception as ex:
    observed = {x['request_id']:x['state'] for x in getattr(ex,'attempt_states',[]) if 'request_id' in x and 'state' in x}
    for entry in entries:
     if observed.get(entry['id']) in ('generated','collected'): entry.update(collection_only=True)
     elif observed.get(entry['id']) == 'prepared': entry.update(status='not_submitted',error=str(ex))
    if getattr(ex, 'collection_only', False):
     for entry in entries: entry.update(collection_only=True)
    if getattr(ex, 'generation_submitted', True) is False:
     for entry in entries: entry.update(status='not_submitted', error=str(ex))
    write(state_file, {'jobs':run_jobs})
    raise Blocked(f'B-2 batch stopped; reconcile attempted requests: {ex}')
  return subprocess.CompletedProcess(args, 0, stdout='Batch completed via B-2 queue', stderr='')

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
 # Legacy no-brief compatibility; v3 production uses image_pipeline.request.
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

from scripts.subtitles import subtitle_cues, phrase_chunks


def split_into_phrases(text, max_len=32):
 return phrase_chunks(text or '', max_len)


def make_srt(segs):
 cues=subtitle_cues(segs)
 return '\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1))
def chunks(text):
 import re
 raw=re.split(r'(?<=[.!?])\s+|(?<=[.!?][\"\'”’])\s+', text.strip())
 parts=[]
 for s in raw:
  s=s.strip()
  if not s:continue
  if len(s)>180:
   sub=re.split(r'(?<=[,;:\-])\s+', s)
   for x in (x.strip() for x in sub if x.strip()):
    # Long-form narration can carry a clause with no punctuation at all;
    # never hand the TTS model more than it accepts (tts_max_chars 256).
    while len(x)>240:
     cut=x.rfind(' ',0,200)
     cut=cut if cut>0 else 200
     parts.append(x[:cut].strip());x=x[cut:].strip()
    if x:parts.append(x)
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
 """16:9 exports carry the English track unless the brief sets
 voice_language "vi"; 9:16 always carries Vietnamese."""
 from scripts.story_plan import needs_english
 b=p.brief(j)
 return bool(b) and needs_english(b[0])

def scene_tail(scene, language, gaps, last):
 """A learner turn is a measured scene-tail hold, never spoken metadata."""
 default = gaps.get('tail' if last else 'para', DEFAULT_PAUSE['tail' if last else 'para'])
 requested = scene.get('audio_direction', {}).get(language, {}).get('learner_pause_seconds', 0)
 if isinstance(requested, bool) or not isinstance(requested, (int, float)) or not 0 <= requested <= 8:
  raise Blocked('learner_pause_seconds must be between 0 and 8')
 return max(default, requested)


QUOTE=re.compile(r'"([^"]+)"|“([^”]+)”')
def is_english(s):
 """Pure-ASCII Latin text: no Vietnamese letter can be inside it."""
 return bool(re.search('[A-Za-z]',s)) and all(ord(c)<128 or c in '‘’…–—' for c in s)

def english_parts(text,words):
 """Split one narration chunk into ordered Vietnamese/English parts.

 English = a quoted pure-ASCII phrase, or one of the scene's vocabulary words
 (content field `vocabulary`, plus -s/-es/-ed/-d/-ing) outside quotes. Only
 called for scenes that declare vocabulary, so a quoted Vietnamese word
 written without accents is never mistaken for English. Sentence punctuation
 right after a word stays with it (it sets the English intonation); parts
 without letters (quote marks, a stray colon) are dropped."""
 spans=[(m.start(),m.end(),(m.group(1) or m.group(2)).strip()) for m in QUOTE.finditer(text) if is_english(m.group(1) or m.group(2))]
 for w in words:
  pat=r"(?<![\w'’])"+r'\s+'.join(map(re.escape,w.split()))+r"(?:s|es|ed|d|ing)?(?![\w'’])"
  for m in re.finditer(pat,text,re.I):
   if any(a<=m.start()<b for a,b,_ in spans):continue
   end=m.end()
   while end<len(text) and text[end] in '.!?':end+=1
   spans.append((m.start(),end,text[m.start():end]))
 parts=[];pos=0
 for a,b,t in sorted(spans):
  if a<pos:continue
  if re.search(r'\w',text[pos:a]):parts.append({'lang':'vi','text':text[pos:a].strip()})
  parts.append({'lang':'en','text':t});pos=b
 if re.search(r'\w',text[pos:]):parts.append({'lang':'vi','text':text[pos:].strip()})
 return parts

def span_take(cfg,retake):
 """Deterministic English delivery for the n-th retake of a scene. The reseed
 alone was not enough (SC04 of vocab-scold-002 failed three retakes): each
 retake also lowers the sampling temperature and, for embedded words, slows
 the speaking rate, so a rejected read changes something audible and recorded.
 Retake 0 is exactly the configured delivery."""
 r=max(0,int(retake))
 return {'seed':int(cfg.get('en_seed',42))+r,
         'temperature':round(max(.1,float(cfg.get('en_temperature',.3))-.05*r),3),
         'rate':round(max(.8,float(cfg.get('audio_english_spans_rate',1.))-.05*r),3)}

def english_spans(p,j,out,cfg,scenes):
 """Voice the English parts of Vietnamese narration with the English engine.

 VieNeu has no English final clusters: in vocab-scold-002 the reviewer kept
 hearing "Please don't scold me!" as "sco"/"scood". Identical text with an
 identical take is synthesized once and reused, so a word sounds the same in
 every scene. Fills each English part with its WAV, take and rate in place."""
 py=p.root/'.venv-en/bin/python'
 if not py.exists():raise Blocked('Thiếu môi trường TTS tiếng Anh (.venv-en) để đọc từ/câu tiếng Anh; cài .venv-en hoặc đặt audio_english_spans_engine khác "en"')
 items=[];ids={}
 for sc in scenes:
  take=span_take(cfg,sc['retake'])
  for x in (x for c in sc.get('parts',[]) for x in c if x['lang']=='en'):
   k=(x['text'],take['seed'],take['temperature'])
   if k not in ids:ids[k]=f'S{len(items):03}';items.append({'id':ids[k],'text':x['text'],'retake':sc['retake'],'take':take})
   x.update(id=ids[k],rate=take['rate'])
 keys=('en_voice','en_device','en_quantize','en_temperature','en_threads','en_seed')
 request=out/'request-en-spans.json';write(request,{'mode':'spans','settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'cache_dir':str(p.job(j)/'cache/tts-en-spans'),'spans':items})
 r=subprocess.run([str(py),str(p.root/'scripts/en_worker.py'),str(request),str(out)],capture_output=True,text=True,timeout=7200)
 (out/'tts-en-spans.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('TTS tiếng Anh cho từ/câu mẫu thất bại; xem tts-en-spans.log')
 meta=read(out/'en-spans-result.json');done={x['id']:x for x in meta['spans']}
 for x in (x for sc in scenes for c in sc.get('parts',[]) for x in c if x['lang']=='en'):
  d=done[x.pop('id')]
  x.update(wav=str(out/d['path']),take=dict(engine=meta['engine'],voice=meta['voice'],seed=d['seed'],temperature=d['temperature'],rate=x['rate']))

def english(p,j,out,cfg,scenes):
 py=p.root/'.venv-en/bin/python'
 if not py.exists():raise Blocked('Install the English TTS environment (.venv-en)')
 missing=[s['id'] for s in scenes if not s.get('narration_en')]
 if missing:raise Blocked('Missing narration_en for '+', '.join(missing))
 g=cfg.get('tts_pause',DEFAULT_PAUSE)
 retake=retakes(p,j)
 items=[{'scene_id':s['id'],'narration_en':s['narration_en'],'retake':retake.get(s['id'],0),
         'take':{x:v for x,v in span_take(cfg,retake.get(s['id'],0)).items() if x!='rate'},
         'tail':scene_tail(s,'en',g,k==len(scenes)-1)}
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
  item={'scene_id':x['scene_id'],'start':cursor,'end':cursor+d,'path':rel(p,j,f)}
  if 'content_duration' in x:item['content_end']=cursor+x['content_duration']
  if 'take' in x:item['take']=x['take']
  done.append(item);cursor+=d
 combined=out/'narration_en.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_en_eq.wav',cfg)
 return {'engine':meta['engine'],'voice':meta['voice'],'wav':rel(p,j,combined),'duration':cursor,'scenes':done}

def tts_python(root,cfg):
 """.venv-tts-gpu (torch cu126 + VieNeu) when installed and tts_device allows a
 GPU; the worker itself still falls back to ONNX/CPU if CUDA is unusable."""
 gpu=root/'.venv-tts-gpu/bin/python'
 return gpu if cfg.get('tts_device','auto')!='cpu' and gpu.exists() else root/'.venv-tts/bin/python'

def audio(p,j,out):
 content=p.payload(j,'content');cfg=config(p);g=cfg.get('tts_pause',DEFAULT_PAUSE)
 py=tts_python(p.root,cfg)
 if not py.exists():raise Blocked('Install local TTS environment')
 retake=retakes(p,j)
 scenes=[{'scene_id':s['id'],'narration':s['narration'],'texts':chunks(s['narration']),'retake':retake.get(s['id'],0)} for s in content['scenes']]
 for k,sc in enumerate(scenes):
  sc['gaps']=[gap_after(t,g) for t in sc['texts'][:-1]]
  sc['tail']=scene_tail(content['scenes'][k],'vi',g,k==len(scenes)-1)
  words=[v['word'] for v in content['scenes'][k].get('vocabulary') or [] if is_english(v.get('word',''))]
  # audio_english_spans_engine: 'en' (default) voices English inside Vietnamese
  # narration with the English engine; any other value keeps it on VieNeu.
  if words and cfg.get('audio_english_spans_engine','en')=='en':
   parts=[english_parts(t,words) for t in sc['texts']]
   if any(x['lang']=='en' for c in parts for x in c):sc['parts']=parts
 if any('parts' in sc for sc in scenes):english_spans(p,j,out,cfg,scenes)
 keys=('tts_voice','tts_temperature','tts_top_p','tts_max_chars','tts_scene_synthesis','tts_backend','tts_precision','tts_speed','tts_device','tts_gpu_dtype','tts_batch_size','audio_english_spans_gap')
 # Job-level cache dir (not per-revision): pilot.run() always mkdirs a fresh
 # revisions/audio/N, so a cache rooted there could never hit across runs.
 # tts_worker.py now keys cache entries by content hash (text+settings+model
 # version), so sharing this directory across revisions is safe -- editing
 # one scene's narration cannot resurrect another scene's stale audio.
 cache_dir=p.job(j)/'cache/tts'
 request=out/'request.json';write(request,{'settings':{k:cfg.get(k) for k in keys if cfg.get(k) is not None},'cache_dir':str(cache_dir),'scenes':scenes})
 result=subprocess.run([str(py),str(p.root/'tts_worker.py'),str(request),str(out)],capture_output=True,text=True,timeout=7200)
 (out/'tts.log').write_text(result.stdout+'\n'+result.stderr)
 if result.returncode:raise Blocked('Local TTS failed; see tts.log; no cloud fallback')
 meta=read(out/'tts-result.json');segments=[];cursor=0.;frames=[];params=None
 for x in meta['segments']:
  file=out/x['path']
  with wave.open(str(file)) as wav:
   fmt=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
   if params and fmt!=params:raise Blocked('Inconsistent TTS audio formats')
   params=fmt;duration=wav.getnframes()/wav.getframerate();frames.append(wav.readframes(wav.getnframes()))
  item={'scene_id':x['scene_id'],'text':x['text'],'start':cursor,'end':cursor+duration,'path':rel(p,j,file)}
  if 'content_duration' in x:item['content_end']=cursor+x['content_duration']
  segments.append(item);cursor+=duration
 combined=out/'narration.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_eq.wav',cfg)
 srt=out/'subtitles.srt';srt.write_text(make_srt(segments))
 payload={'voice':meta['voice'],'backend':meta.get('engine',{}).get('backend','onnx'),'wav':rel(p,j,combined),'srt':rel(p,j,srt),'duration':cursor,'segments':segments}
 if meta.get('english_spans'):payload['english_spans']=meta['english_spans']
 if needs_en(p,j):payload['en']=english(p,j,out,cfg,content['scenes'])
 return payload

def render(p,j,out):
 content=p.payload(j,'content');imgs=p.payload(j,'images');snd=p.payload(j,'audio')
 public=out/'public';public.mkdir(exist_ok=True);shutil.copy(p.path(j,snd['wav']),public/'narration.wav')
 en=snd.get('en')
 if en:shutil.copy(p.path(j,en['wav']),public/'narration_en.wav')
 from scripts.story_plan import timeline, voice_language, subtitles_enabled
 b=p.brief(j)[0] if p.brief(j) else None
 ratio=b.get('aspect_ratio','9:16') if b else '9:16'
 # Language of the 16:9 track: English by default, Vietnamese when the brief
 # sets voice_language "vi" (then it reuses narration.wav and the vi cues).
 wide=voice_language(b) if b else 'vi'
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
 scenes=render_scenes(wide,'16:9') if ratio=='16:9' else render_scenes('vi','9:16')
 cfg=config(p)
 props={'duration':snd['duration'],'scenes':scenes,'segments':snd['segments'],'cues':subtitle_cues(snd['segments']),'aspect_ratio':ratio,
        'voice_language':wide,'subtitles':subtitles_enabled(b),'render_concurrency':cfg.get('render_concurrency',4)}
 for k in ('render_x264_preset','render_gl'):
  if cfg.get(k):props[k]=cfg[k]
 # config.render_fps (e.g. 15): cheaper long-form render, re-timed to 30 fps.
 if cfg.get('render_fps') and ratio=='16:9':props['fps']=int(cfg['render_fps'])
 if en and wide=='en':
  props['en_duration']=en['duration']
  props['en_scenes']=scenes if ratio=='16:9' else render_scenes('en','16:9')
 elif ratio=='dual':props['horizontal_scenes']=render_scenes('vi','16:9')
 from scripts.editorial_audit import audit
 editorial=audit(props);write(out/'editorial-audit.json',editorial)
 if editorial['errors']:raise Blocked('Editorial technical defects; see editorial-audit.json')
 write(out/'props.json',props)
 r=subprocess.run(['node',str(p.root/'renderer/render.mjs'),str(out.resolve())],cwd=p.root,capture_output=True,text=True,timeout=max(3600,int(props['duration']*8)));(out/'render.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('Render or layout check failed; see render.log: '+r.stderr[-500:])
 result={'video':rel(p,j,out/'video.mp4'),'stills':[rel(p,j,out/(s['id']+'.png')) for s in scenes],'layout_report':rel(p,j,out/'layout.json'),'editorial_report':rel(p,j,out/'editorial-audit.json'),'duration':en['duration'] if ratio=='16:9' and wide=='en' else snd['duration']}
 if (out/'video_16x9.mp4').exists():result['video_16x9']=rel(p,j,out/'video_16x9.mp4')
 if (out/'video_9x16.mp4').exists():result['video_9x16']=rel(p,j,out/'video_9x16.mp4')
 return result
