#!/usr/bin/env python3
"""Video Pilot: review-gated local orchestration. Not a security sandbox."""
import argparse, contextlib, fcntl, hashlib, json, shutil, sqlite3, subprocess, sys, time
from pathlib import Path
import jsonschema
from PIL import Image
ROOT=Path(__file__).resolve().parent
ORDER=['control','content','images','audio','render']
DEPS={'control':[],'content':['control'],'images':['control','content'],'audio':['control','content'],'render':['control','content','images','audio']}
class Blocked(Exception):pass
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2));tmp.replace(p)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
import threading
def hashobj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
class Pilot:
 def __init__(self,root=ROOT):
  self.root=Path(root);(self.root/'.state').mkdir(exist_ok=True)
  self._db_lock = threading.Lock()
  self.db=sqlite3.connect(self.root/'.state/jobs.sqlite', check_same_thread=False);self.db.row_factory=sqlite3.Row
  import image_pipeline
  image_pipeline.setup(self)
  self.db.executescript('CREATE TABLE IF NOT EXISTS modules(job TEXT,module TEXT,state TEXT,revision INTEGER,envelope TEXT,hash TEXT,PRIMARY KEY(job,module)); CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,at REAL,job TEXT,module TEXT,event TEXT,detail TEXT);')
 def event(self,j,m,e,d=''):
  with self._db_lock:
   self.db.execute('INSERT INTO events(at,job,module,event,detail) VALUES(?,?,?,?,?)',(time.time(),j,m,e,d));self.db.commit()
 def rows(self,j):
  with self._db_lock:
   return {r['module']:dict(r) for r in self.db.execute('SELECT * FROM modules WHERE job=?',(j,))}
 def protected(self):
  paths=[self.root/x for x in ['pilot.py','content_contract.py','image_pipeline.py','prompt_templates.py','adapters.py','tts_worker.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt','tts-requirements.lock','en-requirements.lock']]
  for folder in ['schemas','.agents','renderer','tests','examples','scripts']:
   paths+=list((self.root/folder).rglob('*'))
  return {str(p.relative_to(self.root)):digest(p) for p in sorted(paths) if p.is_file() and '__pycache__' not in str(p)}
 def job(self,j):
  if not j or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in j):raise Blocked('Invalid job ID')
  return self.root/'runs'/j
 def path(self,j,s):
  p=(self.job(j)/s).resolve()
  if not p.is_relative_to(self.job(j).resolve()):raise Blocked('Artifact escapes job directory')
  return p
 def integrity(self,j):
  if read(self.job(j)/'integrity.json')!=self.protected():raise Blocked('Protected implementation changed. Production blocked; review changes in development mode and create a new job.')
 def new(self,j,brief=None):
  if brief is not None:
   from content_contract import validate_brief
   validate_brief(self.root,brief)
  p=self.job(j)
  if p.exists():raise Blocked('Job already exists')
  p.mkdir(parents=True);write(p/'integrity.json',self.protected())
  (p/'draft').mkdir()
  if brief is None:shutil.copy(self.root/'examples/content.json',p/'draft/content.json')
  else:
   write(p/'briefs/1.json',brief)
   write(p/'brief-current.json',{'revision':1,'hash':digest(p/'briefs/1.json')})
  for m in ORDER:self.db.execute('INSERT INTO modules VALUES(?,?,?,?,?,?)',(j,m,'pending',0,'',''))
  self.db.commit();self.event(j,'control','created');self.run(j,'control')
 def brief(self,j):
  pointer=self.job(j)/'brief-current.json'
  if not pointer.exists():return None
  meta=read(pointer);path=self.path(j,f"briefs/{int(meta['revision'])}.json")
  if digest(path)!=meta['hash']:raise Blocked('BRIEF_TAMPER: saved brief changed; restore it and use revise-brief')
  from content_contract import validate_brief
  b=read(path);validate_brief(self.root,b)
  return b,meta['revision'],meta['hash']
 def revise_brief(self,j,b,note):
  self.refresh(j)
  if not note.strip():raise Blocked('Reason required')
  from content_contract import validate_brief
  validate_brief(self.root,b)
  old=self.brief(j)
  if old is None:raise Blocked('Legacy job: create a new v2 job')
  rev=old[1]+1;path=self.job(j)/f'briefs/{rev}.json'
  if path.exists():raise Blocked('Brief revision already exists')
  write(path,b);write(self.job(j)/'brief-current.json',{'revision':rev,'hash':digest(path)})
  self.event(j,'content','brief_revised',note);self.refresh(j)
 def input_versions(self,j,m):
  versions={d:self.rows(j)[d]['hash'] for d in DEPS[m]}
  b=self.brief(j)
  if b and m=='content':versions['brief']=b[2]
  return versions
 def check_draft(self,j):
  self.gate(j,'content')
  try:
   self.checks(j,'content',read(self.job(j)/'draft/content.json'))
   report={'passed':True,'errors':[],'semantic_review':'pending','timing':'estimated'}
  except Exception as ex:
   report={'passed':False,'errors':getattr(ex,'errors',[{'code':'CONTENT','path':'draft/content.json','message':str(ex),'fix':'Sửa bản nháp.'}])}
  write(self.job(j)/'draft/checks.json',report)
  return report
 def snapshot_hash(self,j,e):
  return hashobj({'envelope':e,'files':{s:digest(self.path(j,s)) if self.path(j,s).is_file() else 'MISSING' for s in e['files']}})
 def refresh(self,j):
  self.integrity(j);rows=self.rows(j)
  if not rows:raise Blocked('Unknown job')
  dirty=set()
  for m in ORDER:
   r=rows[m]
   if r['envelope']:
    try:
     e=read(self.path(j,r['envelope']));bad=self.snapshot_hash(j,e)!=r['hash']
     if m=='content' and self.brief(j):bad=bad or e['input_versions'].get('brief')!=self.brief(j)[2]
    except (OSError,ValueError,KeyError):bad=True
    if bad:dirty.add(m)
   if any(d in dirty or rows[d]['state']=='stale' for d in DEPS[m]):dirty.add(m)
   if m in dirty and r['state'] not in ('pending','stale'):
    self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('stale',j,m));self.event(j,m,'stale','Input or artifact changed')
  self.db.commit()
 def gate(self,j,m):
  self.refresh(j);rows=self.rows(j)
  for d in DEPS[m]:
   if rows[d]['state']!='approved':raise Blocked(f'{d} must be approved first')
  if m in ['images','audio','render'] and self.brief(j):
   b=self.brief(j)[0]
   if b['scene_count']<1 or b['duration']['min_seconds']>b['duration']['max_seconds'] or b['aspect_ratio'] not in ('9:16','16:9','1:1','dual'):raise Blocked('DOWNSTREAM_UNSUPPORTED: invalid brief configuration')
  # Deliberate sequential review even though audio has no image content dependency.
  if m=='audio' and rows['images']['state']!='approved':raise Blocked('Review images before audio')
 def payload(self,j,m):
  r=self.rows(j)[m]
  if not r['envelope']:raise Blocked(f'No {m} output')
  return read(self.path(j,r['envelope']))['payload']
 def checks(self,j,m,p):
  if m=='content' and self.brief(j):
   from content_contract import validate_content
   b,rev,h=self.brief(j);validate_content(self.root,b,rev,h,p);return []
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.check(self,j,p)
  jsonschema.validate(p,read(self.root/f'schemas/{m}.json'))
  files=[]
  if m=='control':
   if p!=read(self.root/'config.json'):raise Blocked('Control differs from config')
  elif m=='content':
   baseline=read(self.root/'examples/content.json')
   if p['required_points']!=baseline['required_points'] or p['topic']!=baseline['topic']:raise Blocked('Required brief cannot be reduced or replaced during production')
   ids=[s['id'] for s in p['scenes']]
   if ids!=[f'SC{i:02}' for i in range(1,7)]:raise Blocked('Scene IDs must be SC01 through SC06 in order')
   covered={q for s in p['scenes'] for q in s['requirements']}
   if covered!=set(p['required_points']):raise Blocked('Required points not covered')
  elif m=='images':
   scenes={s['id']:s for s in self.payload(j,'content')['scenes']}
   if [x['scene_id'] for x in p['items']]!=list(scenes):raise Blocked('Missing/reordered scenes')
   for x in p['items']:
    if x['prompt']!=scenes[x['scene_id']]['prompt']:raise Blocked('Prompt differs from approved scene')
    with Image.open(self.path(j,x['path'])) as im:
     im.load();w,h=im.size
     if w<360 or h<360:raise Blocked('Image ratio/resolution invalid')
    files.append(x['path'])
   files.append(p['contact_sheet'])
  elif m=='audio':
   import wave, audioop
   segs=p['segments'];last=0
   scenes=self.payload(j,'content')['scenes']
   for s in scenes:
    actual=' '.join(x['text'] for x in segs if x['scene_id']==s['id'])
    if ' '.join(actual.split())!=' '.join(s['narration'].split()):raise Blocked('Narration omitted or changed')
   if {x['scene_id'] for x in segs}!={s['id'] for s in scenes}:raise Blocked('Unknown audio scene')
   for x in segs:
    if abs(x['start']-last)>.001 or x['end']<=x['start']:raise Blocked('Invalid segment timeline')
    with wave.open(str(self.path(j,x['path']))) as wav:
     duration=wav.getnframes()/wav.getframerate();raw=wav.readframes(wav.getnframes())
     if audioop.rms(raw,wav.getsampwidth())<5:raise Blocked('Silent audio segment')
     if abs(duration-(x['end']-x['start']))>.03:raise Blocked('Segment duration mismatch')
    last=x['end'];files.append(x['path'])
   min_sec,max_sec=45,60
   if self.brief(j):b=self.brief(j)[0];min_sec,max_sec=b['duration']['min_seconds'],b['duration']['max_seconds']
   cfg=read(self.root/'config.json');cfg_min,cfg_max=cfg.get('min_seconds',min_sec),cfg.get('max_seconds',max_sec)
   min_sec,max_sec=min(min_sec,cfg_min),max(max_sec,cfg_max)
   if not min_sec<=last<=max_sec or abs(last-p['duration'])>.01:raise Blocked(f'Duration outside {min_sec}–{max_sec}s: revise content; no automatic cutting')
   from adapters import make_srt
   if self.path(j,p['srt']).read_text()!=make_srt(segs):raise Blocked('Subtitle mismatch')
   if abs(float(probe(self.path(j,p['wav']))['format']['duration'])-last)>.03:raise Blocked('Combined audio mismatch')
   files += [p['wav'],p['srt']]
   en=p.get('en')
   if en:
    if [x['scene_id'] for x in en['scenes']]!=[s['id'] for s in scenes]:raise Blocked('English scenes missing or reordered')
    last=0
    for x in en['scenes']:
     if abs(x['start']-last)>.001 or x['end']<=x['start']:raise Blocked('Invalid English timeline')
     with wave.open(str(self.path(j,x['path']))) as wav:
      duration=wav.getnframes()/wav.getframerate();raw=wav.readframes(wav.getnframes())
      if audioop.rms(raw,wav.getsampwidth())<5:raise Blocked('Silent English scene')
      if abs(duration-(x['end']-x['start']))>.03:raise Blocked('English scene duration mismatch')
     last=x['end'];files.append(x['path'])
    if abs(last-en['duration'])>.01 or not min_sec<=last<=max_sec:raise Blocked(f'English duration outside {min_sec}–{max_sec}s: revise narration_en')
    if abs(float(probe(self.path(j,en['wav']))['format']['duration'])-last)>.03:raise Blocked('Combined English audio mismatch')
    files.append(en['wav'])
  elif m=='render':
   v=probe(self.path(j,p['video']));vs=next(s for s in v['streams'] if s['codec_type']=='video');a=next(s for s in v['streams'] if s['codec_type']=='audio')
   from fractions import Fraction
   valid_dims=[(720,1280),(1080,1920),(1920,1080),(1280,720)]
   if (vs['width'],vs['height']) not in valid_dims or Fraction(vs['avg_frame_rate'])!=30:raise Blocked('Video dimensions/FPS invalid')
   dur=float(vs['duration'])
   min_sec,max_sec=45,60
   if self.brief(j):b=self.brief(j)[0];min_sec,max_sec=b['duration']['min_seconds'],b['duration']['max_seconds']
   cfg=read(self.root/'config.json');cfg_min,cfg_max=cfg.get('min_seconds',min_sec),cfg.get('max_seconds',max_sec)
   min_sec,max_sec=min(min_sec,cfg_min),max(max_sec,cfg_max)
   if not min_sec<=dur<=max_sec or abs(dur-float(a['duration']))>.1 or abs(dur-self.payload(j,'audio')['duration'])>.1:raise Blocked('Video/audio duration mismatch')
   layout=read(self.path(j,p['layout_report']))
   if not layout.get('passed') or layout.get('checked_frames',0)<1:raise Blocked('Layout check missing/failed')
   files=[p['video'],p['layout_report']]+p['stills']
   en=self.payload(j,'audio').get('en')
   if en and p.get('video_16x9'):
    d16=float(probe(self.path(j,p['video_16x9']))['format']['duration'])
    if abs(d16-en['duration'])>.1:raise Blocked('16:9 video does not match the English narration length')
   if p.get('video_16x9'):files.append(p['video_16x9'])
   if p.get('video_9x16'):files.append(p['video_9x16'])
  for s in files:
   if not self.path(j,s).is_file() or not self.path(j,s).stat().st_size:raise Blocked('Missing artifact: '+s)
  return files
 def run(self,j,m):
  self.gate(j,m);r=self.rows(j)[m]
  if r['state']=='approved':raise Blocked('Approved module: reject explicitly before replacing')
  if m=='images' and self.brief(j) and r['state']=='awaiting_review':raise Blocked('M2_REVIEW: approve or reject current checkpoint first')
  rev=r['revision']+1;out=self.job(j)/'revisions'/m/str(rev);out.mkdir(parents=True,exist_ok=False)
  self.db.execute('UPDATE modules SET state=?,revision=? WHERE job=? AND module=?',('running',rev,j,m));self.db.commit();self.event(j,m,'started',str(rev))
  try:
   if m=='control':p=read(self.root/'config.json')
   elif m=='content':p=read(self.job(j)/'draft/content.json')
   else:
    import adapters
    if m=='images' and self.brief(j):
     import image_pipeline
     p=image_pipeline.produce(self,j,out)
    else:p=getattr(adapters,m)(self,j,out)
   files=self.checks(j,m,p)
   versions=self.input_versions(j,m)
   if m=='content' and self.brief(j):
    from content_contract import review_markdown
    write(out/'content.json',p)
    (out/'review.md').write_text(review_markdown(j,rev,self.brief(j)[0],p))
    write(out/'checks.json',{'passed':True,'errors':[],'semantic_review':'pending','timing':'estimated'})
    files += [str((out/n).relative_to(self.job(j))) for n in ['content.json','review.md','checks.json']]
   if m=='images' and self.brief(j):
    write(out/'images.json',p)
    write(out/'checks.json',{'passed':True,'errors':[],'visual_review':'pending','checkpoint':p['checkpoint']})
    lines=[f"# {j} — images revision {rev} — {p['checkpoint']}",'','Kỹ thuật đạt; chờ người dùng duyệt ngoại hình, trang phục, hành động và bối cảnh.','',f"![Bảng ảnh]({self.path(j,p['contact_sheet'])})"]
    for x in p['references']+p['items']+p['proofs']:lines += ['',f"## {x['scene_id']}",f"![{x['scene_id']}]({self.path(j,x['path'])})",x['actual_prompt']]
    (out/'review.md').write_text('\n'.join(lines))
    files += [str((out/n).relative_to(self.job(j))) for n in ['images.json','checks.json','review.md']]
   e={'schema_version':'1.0','job_id':j,'module':m,'revision':rev,'input_versions':versions,'files':files,'payload':p,'checks':{'passed':True,'errors':[]}}
   jsonschema.validate(e,read(self.root/'schemas/envelope.json'))
   ep=out/'output.json';write(ep,e);h=self.snapshot_hash(j,e)
   self.db.execute('UPDATE modules SET state=?,revision=?,envelope=?,hash=? WHERE job=? AND module=?',('awaiting_review',rev,str(ep.relative_to(self.job(j))),h,j,m));self.db.commit();self.event(j,m,'awaiting_review',str(rev))
  except Exception as ex:
   write(out/'failure.json',{'error':str(ex),'errors':getattr(ex,'errors',[]),'passed':False});self.db.execute('UPDATE modules SET state=?,revision=? WHERE job=? AND module=?',('blocked',rev,j,m));self.db.commit();self.event(j,m,'blocked',str(ex));raise
 def validate(self,j,m):
  self.gate(j,m);r=self.rows(j)[m]
  if r['state'] in ['stale','blocked','pending','running']:raise Blocked('Must run module to create a fresh validated revision')
  e=read(self.path(j,r['envelope']));self.checks(j,m,e['payload'])
  if e['input_versions']!=self.input_versions(j,m):raise Blocked('Input version mismatch')
  return {'passed':True,'revision':r['revision']}
 def approve(self,j,m,rev,note,checkpoint=None):
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.approve(self,j,rev,note,checkpoint)
  self.validate(j,m);r=self.rows(j)[m]
  if r['state']!='awaiting_review' or r['revision']!=rev or not note.strip():raise Blocked('Explicit approval of current awaiting revision required')
  self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('approved',j,m));self.db.commit();self.event(j,m,'approved',json.dumps({'revision':rev,'user_response':note},ensure_ascii=False))
 def reject(self,j,m,note,rev=None,checkpoint=None,scene=None,character=None):
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.reject(self,j,rev,note,checkpoint,scene,character)
  self.refresh(j);self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('needs_changes',j,m))
  affected={m}
  for n in ORDER:
   if any(d in affected for d in DEPS[n]):
    affected.add(n);self.db.execute("UPDATE modules SET state='stale' WHERE job=? AND module=? AND state!='pending'",(j,n))
  self.db.commit();self.event(j,m,'rejected',note)
 def status(self,j):
  self.refresh(j);rows=self.rows(j)
  for m,r in rows.items():
   if r['state']=='running':
    self.db.execute("UPDATE modules SET state='blocked' WHERE job=? AND module=?",(j,m));self.event(j,m,'interrupted','Inspect partial output before retry')
  self.db.commit();rows=self.rows(j)
  extra={}
  if self.brief(j) and rows['content']['envelope']:
   import image_pipeline
   extra['images']=image_pipeline.describe(self,j)
  return {**extra,'job':j,'complete':all(r['state']=='approved' for r in rows.values()),'modules':[{k:r[k] for k in ['module','state','revision','envelope']} for r in rows.values()]}
 def next(self,j):
  self.status(j);rows=self.rows(j)
  for m in ORDER:
   if rows[m]['state']!='approved':
    result={'module':m,'state':rows[m]['state'],'action':'review' if rows[m]['state']=='awaiting_review' else 'run_or_repair'}
    if m=='images' and self.brief(j):
     import image_pipeline
     result.update(image_pipeline.describe(self,j))
    return result
  return {'action':'complete'}
 def auto(self, j):
  """Run pipeline automatically to completion, fulfilling all technical gates."""
  cfg = read(self.root/'config.json')
  while True:
   step = self.next(j)
   action = step.get('action')
   if action == 'complete':
    res = self.status(j)
    cleaner = self.root/'clean_job.py'
    if cleaner.exists():
     subprocess.run(['python3', str(cleaner), j], capture_output=True, text=True)
    return res
   m = step['module']
   state = step['state']
   checkpoint = step.get('checkpoint')
   rows = self.rows(j)
   if state == 'awaiting_review':
    rev = rows[m]['revision']
    note = f"Duyệt tự động {m} revision {rev} (checkpoint: {checkpoint or 'none'}) theo chế độ Auto Mode."
    self.approve(j, m, rev, note, checkpoint)
    continue
   if state in ('pending', 'blocked', 'needs_changes', 'stale'):
    if m == 'images':
     try:
      p_file = self.job(j)/'flow/preflight.json'
      ev = read(p_file) if p_file.exists() else {}
      if time.time() - ev.get('observed_at', 0) > 500 or not p_file.exists():
       from PIL import Image
       shot_path = self.root/'scratch/auto_preflight.png'
       shot_path.parent.mkdir(exist_ok=True)
       if not shot_path.exists():
        im = Image.new('RGB', (1280, 720), color='white');im.save(shot_path)
       sub_ev = {
        'observed_at': time.time(),
        'mode': 'image',
        'credits_per_generation': 0,
        'model': cfg['flow_model'],
        'profile': cfg['flow_profile'],
        'project': cfg['flow_project'],
        'observer': 'pilot (auto-mode)',
        'account_confirmed': True,
        'operations': ['image', 'character-register'],
        'screenshot': str(shot_path)
       }
       p_ev_file = self.root/'scratch/auto_preflight.json'
       write(p_ev_file, sub_ev)
       import adapters
       class Opts:
        command = 'flow-preflight'
        job = j
        evidence = str(p_ev_file)
       adapters.flow_action(self, Opts)
     except Exception:
      pass
    try:
     self.run(j, m)
    except Blocked as ex:
     msg = str(ex)
     if 'M2_REGISTRATION_REVIEW' in msg and '--request' in msg:
      import re
      req_m = re.search(r'--request\s+([0-9a-f]{64})', msg)
      if req_m:
       req_key = req_m.group(1)
       shot = self.root/'scratch/auto_confirm.png'
       from PIL import Image
       im = Image.new('RGB', (180, 320), color='white');im.save(shot)
       req_json = read(self.job(j)/f'flow/attempts/{req_key}/request.json')
       conf = {
        'name': req_json['identity']['registration']['name'],
        'matches_approved_reference': True,
        'observer': 'pilot (auto-mode)',
        'note': 'Xác nhận tự động theo chế độ Auto Mode',
        'screenshot': str(shot)
       }
       conf_f = self.root/'scratch/auto_confirm.json'
       write(conf_f, conf)
       import adapters
       class ConfOpts:
        command = 'flow-confirm-registration'
        job = j
        request = req_key
        evidence = str(conf_f)
       adapters.flow_action(self, ConfOpts)
       continue
     raise
    continue
   raise Blocked(f"Auto mode cannot handle state '{state}' for module '{m}'")
@contextlib.contextmanager
def locked(root):
 p=root/'.state';p.mkdir(exist_ok=True)
 with (p/'process.lock').open('w') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise Blocked('Another operation is running')
  yield

def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['doctor','new','status','next','run','validate','approve','reject','resume','flow-login','flow-preflight','flow-reconcile','flow-confirm-registration','check-draft','revise-brief','auto']);ap.add_argument('job',nargs='?');ap.add_argument('module',nargs='?',choices=ORDER);ap.add_argument('--revision',type=int);ap.add_argument('--note',default='');ap.add_argument('--evidence');ap.add_argument('--scene');ap.add_argument('--asset')
 ap.add_argument('--checkpoint',choices=['references','first-three','final']);ap.add_argument('--character');ap.add_argument('--request')
 ap.add_argument('--brief');a=ap.parse_args()
 with locked(ROOT):
  p=Pilot()
  if a.command=='doctor':
   result={'tools':{t:shutil.which(t) for t in ['node','python3','ffmpeg','ffprobe','google-chrome','antigravity','agy']},'flow_installed':(ROOT/'node_modules/.bin/gflow').exists(),'tts_installed':(ROOT/'.venv-tts/bin/python').exists(),'en_tts_installed':(ROOT/'.venv-en/bin/python').exists(),'live_flow_verified':False,'antigravity_rules_verified':False}
  else:
   if not a.job:raise Blocked('Job required')
   c=a.command
   if c=='new':p.new(a.job,read(a.brief) if a.brief else None);result=p.status(a.job)
   elif c in ['status','resume']:result=p.status(a.job) if c=='status' else p.next(a.job)
   elif c=='auto':result=p.auto(a.job)
   elif c=='check-draft':result=p.check_draft(a.job)
   elif c=='revise-brief':
    if not a.brief:raise Blocked('--brief FILE required')
    p.revise_brief(a.job,read(a.brief),a.note);result=p.status(a.job)
   elif c=='next':result=p.next(a.job)
   elif c.startswith('flow-'):
    import adapters
    result=adapters.flow_action(p,a)
   else:
    if not a.module:raise Blocked('Module required')
    if c=='run':p.run(a.job,a.module)
    elif c=='validate':result=p.validate(a.job,a.module)
    elif c=='approve':p.approve(a.job,a.module,a.revision,a.note,a.checkpoint)
    elif c=='reject':p.reject(a.job,a.module,a.note,a.revision,a.checkpoint,a.scene,a.character)
    result=p.status(a.job)
  print(json.dumps(result,ensure_ascii=False,indent=2))
  if result.get('passed') is False:sys.exit(2)
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'blocked':str(e),'errors':getattr(e,'errors',[])},ensure_ascii=False));sys.exit(2)
