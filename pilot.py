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
def hashobj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
class Pilot:
 def __init__(self,root=ROOT):
  self.root=Path(root);(self.root/'.state').mkdir(exist_ok=True)
  self.db=sqlite3.connect(self.root/'.state/jobs.sqlite');self.db.row_factory=sqlite3.Row
  self.db.executescript('CREATE TABLE IF NOT EXISTS modules(job TEXT,module TEXT,state TEXT,revision INTEGER,envelope TEXT,hash TEXT,PRIMARY KEY(job,module)); CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,at REAL,job TEXT,module TEXT,event TEXT,detail TEXT);')
 def event(self,j,m,e,d=''):
  self.db.execute('INSERT INTO events(at,job,module,event,detail) VALUES(?,?,?,?,?)',(time.time(),j,m,e,d));self.db.commit()
 def protected(self):
  paths=[self.root/x for x in ['pilot.py','content_contract.py','adapters.py','tts_worker.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt','tts-requirements.lock']]
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
 def rows(self,j):return {r['module']:dict(r) for r in self.db.execute('SELECT * FROM modules WHERE job=?',(j,))}
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
   if b['scene_count']!=6 or b['duration']!={'min_seconds':45,'max_seconds':60} or b['aspect_ratio']!='9:16':raise Blocked('DOWNSTREAM_UNSUPPORTED: current media modules require 6 scenes, 45–60 seconds, 9:16')
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
     if abs(w/h-9/16)>.03 or w<360:raise Blocked('Image ratio/resolution invalid')
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
   if not 45<=last<=60 or abs(last-p['duration'])>.01:raise Blocked('Duration outside 45–60s: revise content; no automatic cutting')
   from adapters import make_srt
   if self.path(j,p['srt']).read_text()!=make_srt(segs):raise Blocked('Subtitle mismatch')
   if abs(float(probe(self.path(j,p['wav']))['format']['duration'])-last)>.03:raise Blocked('Combined audio mismatch')
   files += [p['wav'],p['srt']]
  elif m=='render':
   v=probe(self.path(j,p['video']));vs=next(s for s in v['streams'] if s['codec_type']=='video');a=next(s for s in v['streams'] if s['codec_type']=='audio')
   from fractions import Fraction
   if (vs['width'],vs['height'])!=(720,1280) or Fraction(vs['avg_frame_rate'])!=30:raise Blocked('Video dimensions/FPS invalid')
   dur=float(vs['duration'])
   if not 45<=dur<=60 or abs(dur-float(a['duration']))>.1 or abs(dur-self.payload(j,'audio')['duration'])>.1:raise Blocked('Video/audio duration mismatch')
   layout=read(self.path(j,p['layout_report']))
   if not layout.get('passed') or layout.get('checked_frames',0)<6:raise Blocked('Layout check missing/failed')
   files=[p['video'],p['layout_report']]+p['stills']
  for s in files:
   if not self.path(j,s).is_file() or not self.path(j,s).stat().st_size:raise Blocked('Missing artifact: '+s)
  return files
 def run(self,j,m):
  self.gate(j,m);r=self.rows(j)[m]
  if r['state']=='approved':raise Blocked('Approved module: reject explicitly before replacing')
  rev=r['revision']+1;out=self.job(j)/'revisions'/m/str(rev);out.mkdir(parents=True,exist_ok=False)
  self.db.execute('UPDATE modules SET state=?,revision=? WHERE job=? AND module=?',('running',rev,j,m));self.db.commit();self.event(j,m,'started',str(rev))
  try:
   if m=='control':p=read(self.root/'config.json')
   elif m=='content':p=read(self.job(j)/'draft/content.json')
   else:
    import adapters
    p=getattr(adapters,m)(self,j,out)
   files=self.checks(j,m,p)
   versions=self.input_versions(j,m)
   if m=='content' and self.brief(j):
    from content_contract import review_markdown
    write(out/'content.json',p)
    (out/'review.md').write_text(review_markdown(j,rev,self.brief(j)[0],p))
    write(out/'checks.json',{'passed':True,'errors':[],'semantic_review':'pending','timing':'estimated'})
    files += [str((out/n).relative_to(self.job(j))) for n in ['content.json','review.md','checks.json']]
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
 def approve(self,j,m,rev,note):
  self.validate(j,m);r=self.rows(j)[m]
  if r['state']!='awaiting_review' or r['revision']!=rev or not note.strip():raise Blocked('Explicit approval of current awaiting revision required')
  self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('approved',j,m));self.db.commit();self.event(j,m,'approved',json.dumps({'revision':rev,'user_response':note},ensure_ascii=False))
 def reject(self,j,m,note):
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
  return {'job':j,'complete':all(r['state']=='approved' for r in rows.values()),'modules':[{k:r[k] for k in ['module','state','revision','envelope']} for r in rows.values()]}
 def next(self,j):
  self.status(j);rows=self.rows(j)
  for m in ORDER:
   if rows[m]['state']!='approved':return {'module':m,'state':rows[m]['state'],'action':'review' if rows[m]['state']=='awaiting_review' else 'run_or_repair'}
  return {'action':'complete'}
@contextlib.contextmanager
def locked(root):
 p=root/'.state';p.mkdir(exist_ok=True)
 with (p/'process.lock').open('w') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise Blocked('Another operation is running')
  yield

def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['doctor','new','status','next','run','validate','approve','reject','resume','flow-login','flow-preflight','flow-reconcile','check-draft','revise-brief']);ap.add_argument('job',nargs='?');ap.add_argument('module',nargs='?',choices=ORDER);ap.add_argument('--revision',type=int);ap.add_argument('--note',default='');ap.add_argument('--evidence');ap.add_argument('--scene');ap.add_argument('--asset')
 ap.add_argument('--brief');a=ap.parse_args()
 with locked(ROOT):
  p=Pilot()
  if a.command=='doctor':
   result={'tools':{t:shutil.which(t) for t in ['node','python3','ffmpeg','ffprobe','google-chrome','antigravity','agy']},'flow_installed':(ROOT/'node_modules/.bin/gflow').exists(),'tts_installed':(ROOT/'.venv-tts/bin/python').exists(),'live_flow_verified':False,'antigravity_rules_verified':False}
  else:
   if not a.job:raise Blocked('Job required')
   c=a.command
   if c=='new':p.new(a.job,read(a.brief) if a.brief else None);result=p.status(a.job)
   elif c in ['status','resume']:result=p.status(a.job) if c=='status' else p.next(a.job)
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
    elif c=='approve':p.approve(a.job,a.module,a.revision,a.note)
    elif c=='reject':p.reject(a.job,a.module,a.note)
    result=p.status(a.job)
  print(json.dumps(result,ensure_ascii=False,indent=2))
  if result.get('passed') is False:sys.exit(2)
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'blocked':str(e),'errors':getattr(e,'errors',[])},ensure_ascii=False));sys.exit(2)
