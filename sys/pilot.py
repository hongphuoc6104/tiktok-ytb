#!/usr/bin/env python3
"""Video Pilot: review-gated local orchestration. Not a security sandbox."""
import argparse, contextlib, fcntl, hashlib, json, shutil, sqlite3, subprocess, sys, time
from pathlib import Path
import jsonschema
from PIL import Image
ROOT=Path(__file__).resolve().parent
ORDER=['control','content','audio','images','render']
DEPS={'control':[],'content':['control'],'images':['control','content'],'audio':['control','content'],'render':['control','content','images','audio']}
PROTECTED_FILES=['pilot.py','workflow.py','machine_review.py','content_contract.py','image_pipeline.py','prompt_templates.py','adapters.py','characters.py','tts_worker.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt','tts-requirements.lock','tts-gpu-requirements.lock','en-requirements.lock','b2_bridge.py']
PROTECTED_DIRS=['schemas','.agents','renderer','tests','examples','scripts']
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
  self.db.executescript('CREATE TABLE IF NOT EXISTS modules(job TEXT,module TEXT,state TEXT,revision INTEGER,envelope TEXT,hash TEXT,PRIMARY KEY(job,module)); CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,at REAL,job TEXT,module TEXT,event TEXT,detail TEXT); CREATE TABLE IF NOT EXISTS audio_edits(id INTEGER PRIMARY KEY,job TEXT,scene_id TEXT,note TEXT,at REAL);')
 def event(self,j,m,e,d=''):
  with self._db_lock:
   self.db.execute('INSERT INTO events(at,job,module,event,detail) VALUES(?,?,?,?,?)',(time.time(),j,m,e,d));self.db.commit()
 def rows(self,j):
  with self._db_lock:
   return {r['module']:dict(r) for r in self.db.execute('SELECT * FROM modules WHERE job=?',(j,))}
 def protected(self):
  paths=[self.root/x for x in PROTECTED_FILES]
  paths += list((self.root/'vocab').glob('*.py'))
  paths += list((self.root/'tiensu').glob('*.py'))
  engine = self.root/'experiments/b2_illustrator'
  paths += [x for x in engine.glob('*') if x.suffix in ('.py','.mjs') and not x.name.startswith('test')]
  paths += [engine/x for x in ('config.json','acceptance.json','browser-profiles.json')]
  for folder in PROTECTED_DIRS:
   paths+=list((self.root/folder).rglob('*'))
  return {str(p.relative_to(self.root)):digest(p) for p in sorted(paths) if p.is_file() and '__pycache__' not in str(p)}
 def git_state(self):
  """HEAD and uncommitted protected changes for provenance; None fields when git is unavailable."""
  specs=PROTECTED_FILES+PROTECTED_DIRS+[':(glob)vocab/*.py',':(glob)tiensu/*.py',':(glob)experiments/b2_illustrator/*.py',':(glob)experiments/b2_illustrator/*.mjs',':(exclude,glob)experiments/b2_illustrator/test*']+[f'experiments/b2_illustrator/{x}' for x in ('config.json','acceptance.json','browser-profiles.json')]
  git=lambda *a:subprocess.run(['git','-C',str(self.root),*a],capture_output=True,text=True,timeout=60)
  try:
   head=git('rev-parse','HEAD')
   if head.returncode:return {'head':None,'dirty':None,'changes':None}
   st=git('status','--porcelain','--',*specs)
   changes=[x for x in st.stdout.splitlines() if x.strip() and '__pycache__' not in x]
   return {'head':head.stdout.strip(),'dirty':bool(changes) if not st.returncode else None,'changes':changes if not st.returncode else None}
  except (OSError,subprocess.SubprocessError):return {'head':None,'dirty':None,'changes':None}
 def clean_code(self,mode):
  """Auto jobs run unattended, so they must start from committed protected code (traceable, restorable)."""
  g=self.git_state()
  if mode=='auto' and g['dirty'] and read(self.root/'config.json').get('auto_require_clean_code',True):
   raise Blocked(f"AUTO_REQUIRES_CLEAN_CODE: code được bảo vệ có {len(g['changes'])} thay đổi chưa commit ("+', '.join(x[3:] for x in g['changes'][:10])+(' …' if len(g['changes'])>10 else '')+'). Job auto chỉ được tạo trên code đã commit. Dừng lại và báo người dùng commit hoặc khôi phục các thay đổi này; agent không tự sửa/commit code bảo vệ.')
  return g
 def job(self,j):
  if not j or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in j):raise Blocked('Invalid job ID')
  return self.root/'runs'/j
 def path(self,j,s):
  p=(self.job(j)/s).resolve()
  if not p.is_relative_to(self.job(j).resolve()):raise Blocked('Artifact escapes job directory')
  return p
 def integrity_diff(self,j,now=None):
  old=read(self.job(j)/'integrity.json');now=self.protected() if now is None else now
  d={'modified':sorted(k for k in old.keys()&now.keys() if old[k]!=now[k]),'added':sorted(now.keys()-old.keys()),'removed':sorted(old.keys()-now.keys())}
  return {'job':j,'changed':sum(map(len,d.values())),**d}
 def integrity(self,j):
  d=self.integrity_diff(j)
  if d['changed']:
   lines=[f'{k}: {x}' for k in ('modified','added','removed') for x in d[k]]
   raise Blocked(f"Protected implementation changed. Production blocked: {d['changed']} file bảo vệ khác baseline của job {j}:\n  "+'\n  '.join(lines[:15])+(f'\n  … và {len(lines)-15} file khác' if len(lines)>15 else '')
    +f'\nKHÔNG tạo job mới cho cùng nội dung (sẽ làm lại từ đầu, tốn quota). Dừng lại và báo người dùng. Cách xử lý: khôi phục các file trên về đúng bản cũ, '
    +f'hoặc người dùng (không phải agent) xem `python3 pilot.py integrity-diff {j}` rồi tự chạy `python3 pilot.py adopt-code {j} --confirm {j} --reason "..."` để job chạy tiếp với code mới.')
 def adopt_code(self,j,confirm,reason):
  """Human-only rebaseline: keep all recorded revisions/reviews/approvals, continue under the new code.
  Stale needs_attention machine reviews are superseded so the next resume re-reviews under the new code."""
  if confirm!=j:raise Blocked(f'adopt-code cần --confirm {j} (đúng mã job)')
  if not (reason or '').strip():raise Blocked('adopt-code cần --reason nêu lý do nhận code mới')
  base=self.job(j)/'integrity.json'
  if not base.is_file() or not self.rows(j):raise Blocked('Unknown job')
  now=self.protected();d=self.integrity_diff(j,now)
  if not d['changed']:raise Blocked('Code bảo vệ trùng baseline của job; không có gì để nhận')
  at=time.time();ts=time.strftime('%Y%m%dT%H%M%S',time.localtime(at))+f'-{time.time_ns()%10**9:09d}'
  hist=self.job(j)/'integrity-history'/f'{ts}.json';rel=str(hist.relative_to(self.job(j)))
  if hist.exists():raise Blocked('Integrity history entry already exists; retry')
  stale=[]
  for f in sorted((self.job(j)/'machine-reviews').glob('*/attempt.json')):
   x=read(f)
   if x.get('state')=='needs_attention':stale.append((f,x))
  g=self.git_state()
  write(hist,{'job':j,'at':at,'actor':'user','reason':reason.strip(),'git_head':g['head'],'git_dirty':g['dirty'],'git_changes':g['changes'],'diff':d,
   'old_baseline':read(base),'old_baseline_sha256':digest(base),'new_baseline_sha256':hashobj(now),
   'superseded_machine_reviews':{str(f.relative_to(self.job(j))):x for f,x in stale}})
  for f,x in stale:write(f,{**x,'state':'superseded','superseded_state':x['state'],'superseded_by':'code_adopted','history':rel})
  write(base,now)
  self.event(j,'control','code_adopted',json.dumps({'history':rel,'reason':reason.strip(),'changed':d['changed'],'git_head':g['head'],'superseded_machine_reviews':len(stale)},ensure_ascii=False))
  return {'job':j,'adopted':True,'history':str(hist),'changed':d['changed'],'superseded_machine_reviews':len(stale),'next':f'python3 pilot.py resume {j}'}
 def brief_policies(self,j,brief):
  # Chính sách riêng của kênh do config chỉ định; bộ điều phối không biết chủ đề nào cả.
  for ref in read(self.root/'config.json').get('brief_policies',[]):
   module,_,func=ref.partition(':')
   import importlib
   getattr(importlib.import_module(module),func or 'check')(self.root,j,brief)
 def new(self,j,brief=None,mode=None):
  if brief is not None:
   from content_contract import validate_brief
   validate_brief(self.root,brief);self.brief_policies(j,brief)
  p=self.job(j)
  if p.exists():raise Blocked('Job already exists')
  g=self.clean_code(mode)
  p.mkdir(parents=True);write(p/'integrity.json',self.protected())
  write(p/'integrity-meta.json',{'created_at':time.time(),'mode':mode,'git_head':g['head'],'protected_dirty':g['dirty'],'protected_changes':g['changes']})
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
  validate_brief(self.root,b);self.brief_policies(j,b)
  old=self.brief(j)
  if old is None:raise Blocked('Legacy job: create a new job')
  if old[0].get('schema_version')=='3.0':
   from scripts.story_plan import normalize_brief
   b=normalize_brief(b);validate_brief(self.root,b)
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
   draft=read(self.job(j)/'draft/content.json')
   self.checks(j,'content',draft)
   from scripts.story_plan import check_revision
   check_revision(self,j,draft)
   report={'passed':True,'errors':[],'semantic_review':'pending','timing':'estimated'}
   if draft.get('schema_version')=='3.0':
    from scripts.story_plan import estimates
    report['duration_estimate']=estimates(self.brief(j)[0],draft)
    report['open_questions']=draft['open_questions']
    report['revision_response']=draft['revision_response']
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
  import workflow
  workflow.gate(self,j,m)
  for d in DEPS[m]:
   if rows[d]['state']!='approved':raise Blocked(f'{d} must be approved first')
  if m in ['images','audio','render'] and self.brief(j):
   b=self.brief(j)[0]
   if b['scene_count']<1 or b['duration']['min_seconds']>b['duration']['max_seconds'] or b['aspect_ratio'] not in ('9:16','16:9','dual'):raise Blocked('DOWNSTREAM_UNSUPPORTED: invalid brief configuration')
  # Audio and images stay independent here so flow-login/flow-preflight remain
  # usable at any time; workflow.STAGES['media'] is what orders the media stage,
  # running the free local TTS first so a narration that misses the brief window
  # fails before any Flow credit is spent on images.
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
    if not x['start']<x.get('content_end',x['end'])<=x['end']:raise Blocked('Invalid content boundary before silence')
    with wave.open(str(self.path(j,x['path']))) as wav:
     duration=wav.getnframes()/wav.getframerate();raw=wav.readframes(wav.getnframes())
     if audioop.rms(raw,wav.getsampwidth())<5:raise Blocked('Silent audio segment')
     if abs(duration-(x['end']-x['start']))>.03:raise Blocked('Segment duration mismatch')
    last=x['end'];files.append(x['path'])
   min_sec,max_sec=45,60
   if self.brief(j):b=self.brief(j)[0];min_sec,max_sec=b['duration']['min_seconds'],b['duration']['max_seconds']
   if not min_sec<=last<=max_sec or abs(last-p['duration'])>.01:raise Blocked(f'Duration outside {min_sec}–{max_sec}s: revise content; no automatic cutting')
   from adapters import make_srt
   if self.path(j,p['srt']).read_text()!=make_srt(segs):raise Blocked('Subtitle mismatch')
   if abs(float(probe(self.path(j,p['wav']))['format']['duration'])-last)>.03:raise Blocked('Combined audio mismatch')
   files += [p['wav'],p['srt']]
   en=p.get('en')
   from scripts.story_plan import needs_english
   if self.brief(j) and needs_english(self.brief(j)[0]) and not en:raise Blocked('English audio required')
   if en:
    if [x['scene_id'] for x in en['scenes']]!=[s['id'] for s in scenes]:raise Blocked('English scenes missing or reordered')
    last=0
    for x in en['scenes']:
     if abs(x['start']-last)>.001 or x['end']<=x['start']:raise Blocked('Invalid English timeline')
     if not x['start']<x.get('content_end',x['end'])<=x['end']:raise Blocked('Invalid English content boundary before silence')
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
   audio=self.payload(j,'audio');ratio=self.brief(j)[0]['aspect_ratio'] if self.brief(j) else '9:16'
   from scripts.story_plan import voice_language
   expected=audio['en']['duration'] if ratio=='16:9' and voice_language(self.brief(j)[0])=='en' else audio['duration']
   if not min_sec<=dur<=max_sec or abs(dur-float(a['duration']))>.1 or abs(dur-expected)>.1:raise Blocked('Video/audio duration mismatch')
   layout=read(self.path(j,p['layout_report']))
   checked=layout.get('checked_cues',layout.get('checked_frames',0))
   if not layout.get('passed') or (layout.get('applies') is not False and checked<1):raise Blocked('Layout check missing/failed')
   files=[p['video'],p['layout_report']]+p['stills']
   if p.get('editorial_report'):
    editorial=read(self.path(j,p['editorial_report']))
    if editorial.get('errors'):raise Blocked('Editorial technical defects in render')
    files.append(p['editorial_report'])
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
   elif m=='content':
    p=read(self.job(j)/'draft/content.json')
    from scripts.story_plan import check_revision
    check_revision(self,j,p)
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
    lines=[f"# {j} — images revision {rev} — {p['checkpoint']}",'','Bước ảnh nội bộ đã kiểm tra kỹ thuật; duyệt chất lượng tại phần media cùng âm thanh.','',f"![Bảng ảnh]({self.path(j,p['contact_sheet'])})"]
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
 def approve(self,j,m,rev,note,checkpoint=None,actor='user'):
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.approve(self,j,rev,note,checkpoint,actor)
  self.validate(j,m);r=self.rows(j)[m]
  if r['state']!='awaiting_review' or r['revision']!=rev or not note.strip():raise Blocked('Explicit approval of current awaiting revision required')
  self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('approved',j,m));self.db.commit();self.event(j,m,'technical_accepted' if actor=='technical' else 'approved',json.dumps({'revision':rev,'actor':actor,'note':note},ensure_ascii=False))
 def reject(self,j,m,note,rev=None,checkpoint=None,scene=None,character=None,image=None,ratio=None,repair_plan=None):
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.reject(self,j,rev,note,checkpoint,scene,character,image,ratio,repair_plan)
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
@contextlib.contextmanager
def locked(root):
 p=root/'.state';p.mkdir(exist_ok=True)
 with (p/'process.lock').open('w') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise Blocked('Another operation is running')
  yield

def main():
 import workflow
 ap=argparse.ArgumentParser(description='Video Pilot: content → media → video; review hoặc auto')
 ap.add_argument('command',choices=['lift-cap','doctor','new','status','next','repair-status','run','validate','approve','reject','resume','flow-login','flow-preflight','flow-reconcile','flow-confirm-registration','check-draft','revise-brief','batch','integrity-diff','adopt-code','mascot-reference'])
 ap.add_argument('job',nargs='?');ap.add_argument('stage',nargs='?',choices=workflow.STAGES)
 ap.add_argument('--mode',choices=['review','auto'],default='review')
 ap.add_argument('--revision',type=int);ap.add_argument('--note',default='')
 for name in ['evidence','scene','asset','character','request','brief','queue','image','repair-plan']:
  ap.add_argument('--'+name)
 ap.add_argument('--from',dest='mascot_from',help='mascot-reference: approved image file to install as the reference')
 ap.add_argument('--part',choices=['audio'])
 ap.add_argument('--ratio',choices=['9:16','16:9'])
 ap.add_argument('--retry-review',action='store_true')
 ap.add_argument('--confirm',help='adopt-code: nhập lại đúng mã job');ap.add_argument('--reason',default='')
 a=ap.parse_args()
 with locked(ROOT):
  p=Pilot()
  try:
   c=a.command
   if c=='doctor':
    result={'tools':{t:shutil.which(t) for t in ['node','python3','ffmpeg','ffprobe','google-chrome','agy']},'workflow_version':3,'stages':list(workflow.STAGES),'modes':['review','auto'],'tts_installed':(ROOT/'.venv-tts/bin/python').exists(),'tts_gpu_installed':(ROOT/'.venv-tts-gpu/bin/python').exists(),'en_tts_installed':(ROOT/'.venv-en/bin/python').exists(),'machine_review_media_verified':False}
   elif c=='batch':
    if not a.queue:raise Blocked('batch requires --queue JSON list of existing auto job IDs')
    jobs=read(a.queue)
    if not isinstance(jobs,list) or not jobs or any(not isinstance(j,str) for j in jobs) or len(set(jobs))!=len(jobs):raise Blocked('Queue must be a nonempty list of unique job IDs')
    result=workflow.batch(p,jobs)
   else:
    if not a.job:raise Blocked('Job required')
    if c=='new':p.clean_code(a.mode);result=workflow.new(p,a.job,read(a.brief) if a.brief else None,a.mode)
    elif c=='integrity-diff':result=p.integrity_diff(a.job)
    elif c=='adopt-code':
     if not sys.stdin.isatty():raise Blocked('adopt-code chỉ dành cho người dùng, chạy trực tiếp trong terminal')
     # Human-only: agents must never run this; they report the integrity block to the user instead.
     print(f'CẢNH BÁO: adopt-code chỉ dành cho NGƯỜI DÙNG. Job {a.job} sẽ chạy tiếp với code bảo vệ hiện tại; baseline cũ được lưu trong integrity-history. Agent không bao giờ tự chạy lệnh này.',file=sys.stderr)
     result=p.adopt_code(a.job,a.confirm,a.reason)
    elif c=='status':result=workflow.status(p,a.job)
    elif c=='next':result=workflow.next_step(p,a.job)
    elif c=='repair-status':
     from scripts.image_repairs import status as repair_status
     result=repair_status(p,a.job,a.image,a.ratio)
    elif c=='mascot-reference':
     # a.job is the channel/mascot name here (e.g. "tiensu" or "default"), not a job id.
     if not a.mascot_from:raise Blocked('mascot-reference requires --from FILE')
     import characters
     result=characters.set_reference(p.root,a.job,a.mascot_from)
    else:
     workflow.settings(p,a.job)
     if c=='lift-cap':
      if not sys.stdin.isatty() or input(f'Gõ lại mã job {a.job} để xác nhận mở khóa: ').strip()!=a.job:raise Blocked('lift-cap chỉ dành cho người dùng, chạy trực tiếp trong terminal')
      result=workflow.lift_cap(p,a.job,a.note)
     elif c in ('run','resume'):result=workflow.advance(p,a.job,a.stage,retry_review=a.retry_review)
     elif c=='check-draft':result=p.check_draft(a.job)
     elif c=='revise-brief':
      if not a.brief:raise Blocked('--brief FILE required')
      p.revise_brief(a.job,read(a.brief),a.note);result=workflow.status(p,a.job)
     elif c.startswith('flow-'):
      import adapters
      result=adapters.flow_action(p,a)
     else:
      if not a.stage:raise Blocked('Stage required: content, media or video')
      if c=='approve':result=workflow.approve(p,a.job,a.stage,a.revision,a.note)
      elif c=='reject':result=workflow.reject(p,a.job,a.stage,a.revision,a.note,a.part,a.scene,a.character,a.image,a.ratio,read(a.repair_plan) if a.repair_plan else None)
      elif c=='validate':
       for m in workflow.STAGES[a.stage]:p.validate(a.job,m)
       result={'passed':True,'stage':a.stage}
   print(json.dumps(result,ensure_ascii=False,indent=2))
   if result.get('passed') is False or result.get('blocked'):sys.exit(2)
  finally:p.db.close()
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'blocked':str(e),'errors':getattr(e,'errors',[])},ensure_ascii=False));sys.exit(2)
