#!/usr/bin/env python3
"""Video Pilot: review-gated local orchestration. Not a security sandbox."""
import argparse, contextlib, fcntl, hashlib, json, shutil, sqlite3, subprocess, sys, time
from pathlib import Path
import jsonschema
from PIL import Image
ROOT=Path(__file__).resolve().parent
ORDER=['control','content','audio','images','render']
DEPS={'control':[],'content':['control'],'images':['control','content'],'audio':['control','content'],'render':['control','content','images','audio']}
PROTECTED_FILES=['pilot.py','workflow.py','machine_review.py','content_contract.py','image_pipeline.py','prompt_templates.py','adapters.py','tts_worker.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt','tts-requirements.lock','tts-gpu-requirements.lock','en-requirements.lock','b2_bridge.py']
PROTECTED_DIRS=['assets/voices','colab_bridge','schemas','.agents','renderer','tests','examples','scripts']
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
 def issue(self,j,module,error,evidence=None):
  folder=self.root/'logs/issues';folder.mkdir(parents=True,exist_ok=True)
  name=f"{time.time_ns()}-{j}-{module}.md";path=folder/name
  text=f"# Sự cố {j} — {module}\n\nMã job: {j}.\n\nTriệu chứng: {error}\n\nBằng chứng: {evidence or 'xem revision/failure.json và sự kiện của job'}\n\nTrạng thái: đang xử lý.\n"
  path.write_text(text)
  with (folder/'.index.lock').open('a') as handle:
   fcntl.flock(handle,fcntl.LOCK_EX)
   index=folder/'INDEX.md'
   prior=index.read_text() if index.exists() else '# Mục lục sự cố\n\n'
   index.write_text(prior+f"- [{j} — {module}]({name})\n")
  self.event(j,module,'issue_recorded',str(path.relative_to(self.root)))
  return str(path.relative_to(self.root))
 def resolve_issues(self,j,module,revision,action=None,evidence=None):
  with self._db_lock:
   recorded=self.db.execute("SELECT detail FROM events WHERE job=? AND module=? AND event='issue_recorded'",(j,module)).fetchall()
   resolved={r['detail'] for r in self.db.execute("SELECT detail FROM events WHERE job=? AND module=? AND event='issue_resolved'",(j,module))}
  with self._db_lock:
   recovery=self.db.execute("SELECT event,detail FROM events WHERE job=? AND event IN ('micro_plan','author_input_received','rejected','image_revision_requested','audio_retake_requested','code_adopted') ORDER BY id DESC LIMIT 1",(j,)).fetchone()
  action=action or ((recovery['event']+': '+recovery['detail']) if recovery else 'Lần thực thi đã lưu input_versions và artifact đầy đủ; nguyên nhân gốc chưa được xác nhận')
  evidence=evidence or f'runs/{j}/revisions/{module}/{revision}/output.json'
  for row in recorded:
   name=row['detail']
   if name in resolved:continue
   path=(self.root/name).resolve()
   if not path.is_relative_to((self.root/'logs/issues').resolve()) or not path.is_file():continue
   with path.open('a') as handle:handle.write(f"\n## Làm gì cho hết lỗi\n\nHành động phục hồi đã ghi: {action}. Phần {module} kiểm tra kỹ thuật thành công tại revision {revision}. Bằng chứng: {evidence}. Chưa suy ra chất lượng hình/giọng từ kết quả kỹ thuật.\n")
   self.event(j,module,'issue_resolved',name)
 def rows(self,j):
  with self._db_lock:
   return {r['module']:dict(r) for r in self.db.execute('SELECT * FROM modules WHERE job=?',(j,))}
 def protected(self):
  paths=[self.root/x for x in PROTECTED_FILES]
  paths += list((self.root/'vocab').glob('*.py'))
  engine = self.root/'experiments/b2_illustrator'
  paths += [x for x in engine.glob('*') if x.suffix in ('.py','.mjs') and not x.name.startswith('test')]
  paths += [engine/x for x in ('config.json','acceptance.json','browser-profiles.json')]
  for folder in PROTECTED_DIRS:
   paths+=list((self.root/folder).rglob('*'))
  return {str(p.relative_to(self.root)):digest(p) for p in sorted(paths) if p.is_file() and '__pycache__' not in str(p)}
 def git_state(self):
  """HEAD and uncommitted protected changes for provenance; None fields when git is unavailable."""
  specs=PROTECTED_FILES+PROTECTED_DIRS+[':(glob)vocab/*.py',':(glob)experiments/b2_illustrator/*.py',':(glob)experiments/b2_illustrator/*.mjs',':(exclude,glob)experiments/b2_illustrator/test*']+[f'experiments/b2_illustrator/{x}' for x in ('config.json','acceptance.json','browser-profiles.json')]
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
  meta=self.job(j)/'integrity-meta.json'
  if meta.is_file() and read(meta).get('engine_version')==4:
   from execution import verify_compatibility
   verify_compatibility(self,j)
   return
  d=self.integrity_diff(j)
  if d['changed']:
   lines=[f'{k}: {x}' for k in ('modified','added','removed') for x in d[k]]
   raise Blocked(f"Protected implementation changed. Production blocked: {d['changed']} file bảo vệ khác baseline của job {j}:\n  "+'\n  '.join(lines[:15])+(f'\n  … và {len(lines)-15} file khác' if len(lines)>15 else '')
    +f'\nKHÔNG tạo job mới cho cùng nội dung (sẽ làm lại từ đầu, tốn quota). Dừng lại và báo người dùng. Cách xử lý: khôi phục các file trên về đúng bản cũ, '
    +f'hoặc người dùng (không phải agent) xem `python3 pilot.py integrity-diff {j}` rồi tự chạy `python3 pilot.py adopt-code {j} --confirm {j} --reason "..."` để job chạy tiếp với code mới.')
 def adopt_code(self,j,confirm,reason,grant_id=None):
  """Human-only rebaseline: keep all recorded revisions/reviews/approvals, continue under the new code.
  Stale needs_attention machine reviews are superseded so the next resume re-reviews under the new code."""
  if confirm!=j:raise Blocked(f'adopt-code cần --confirm {j} (đúng mã job)')
  if not (reason or '').strip():raise Blocked('adopt-code cần --reason nêu lý do nhận code mới')
  authority=None
  if grant_id:
   from execution import _migration_authority
   authority=_migration_authority(self,j,grant_id)
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
  write(hist,{'job':j,'at':at,'actor':'assistant' if authority else 'user','grant_id':grant_id,'authorization_source':authority['source'] if authority else reason.strip(),'granted_by':authority['granted_by'] if authority else 'user','reason':reason.strip(),'git_head':g['head'],'git_dirty':g['dirty'],'git_changes':g['changes'],'diff':d,
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
 def new(self,j,brief=None,mode=None,engine_version=3,grant_id=None):
  if engine_version==4:
   from permissions import Grants
   Grants(self.root).require(grant_id,'production','execute',job=j)
   if brief is None or not brief.get('outputs'):raise Blocked('Engine v4 requires a frozen explicit output contract')
  if brief is not None:
   from content_contract import validate_brief
   validate_brief(self.root,brief);self.brief_policies(j,brief)
  p=self.job(j)
  if p.exists():raise Blocked('Job already exists')
  if engine_version not in (3,4):raise Blocked('Unsupported execution engine')
  g=self.clean_code(mode if engine_version==3 else 'review')
  p.mkdir(parents=True);write(p/'integrity.json',self.protected())
  metadata={'created_at':time.time(),'mode':mode,'git_head':g['head'],'protected_dirty':g['dirty'],'protected_changes':g['changes'],'engine_version':engine_version}
  if engine_version==4:
   from execution import CONTRACT,schema_snapshot
   metadata['engine_contract']=CONTRACT
   metadata['schema_contracts']=schema_snapshot(self)
  write(p/'integrity-meta.json',metadata)
  (p/'draft').mkdir()
  if brief is None:shutil.copy(self.root/'examples/content.json',p/'draft/content.json')
  else:
   write(p/'briefs/1.json',brief)
   write(p/'brief-current.json',{'revision':1,'hash':digest(p/'briefs/1.json')})
  for m in ORDER:self.db.execute('INSERT INTO modules VALUES(?,?,?,?,?,?)',(j,m,'pending',0,'',''))
  self.db.commit();self.event(j,'control','created')
  self._creating_v4_job=j if engine_version==4 else None
  try:self.run(j,'control')
  finally:self._creating_v4_job=None
 def brief(self,j):
  pointer=self.job(j)/'brief-current.json'
  if not pointer.exists():return None
  meta=read(pointer);path=self.path(j,f"briefs/{int(meta['revision'])}.json")
  if digest(path)!=meta['hash']:raise Blocked('BRIEF_TAMPER: saved brief changed; restore it and use revise-brief')
  from content_contract import validate_brief
  b=read(path);validate_brief(self.root,b)
  from execution import is_job,settings
  if is_job(self,j):
   cfg=settings(self,j)
   if cfg.get('outputs') and not b.get('outputs'):
    # Migration freezes a checked projection; immutable legacy brief/hash stay original.
    b={**b,'outputs':cfg['outputs']}
    validate_brief(self.root,b)
  return b,meta['revision'],meta['hash']
 def revise_brief(self,j,b,note):
  from execution import is_job, require
  if is_job(self,j):require(self,j,'content')
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
  from execution import is_job,require
  if is_job(self,j):
   require(self,j,'execute')
   if getattr(self,'_execution_job',None)!=j:raise Blocked('JOB_LEASE_REQUIRED: mutable refresh requires this job controller')
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
  payload=read(self.path(j,r['envelope']))['payload']
  from execution import is_job,settings
  if m=='audio' and is_job(self,j) and settings(self,j).get('migration') and 'tracks' not in payload:
   # Read-compatible projection of accepted legacy WAVs. No historical envelope is rewritten.
   from output_contract import languages,primary_language,voice_settings,narration
   brief=self.brief(j)[0];content=self.payload(j,'content');tracks={}
   for language in languages(brief):
    base=payload if language==payload.get('language','vi') else payload.get('en')
    if base is None:raise Blocked('MIGRATION_AUDIO: requested legacy language is unavailable')
    chosen=voice_settings(brief,language,self.payload(j,'control'))
    track=json.loads(json.dumps(base));track.update(language=language,voice=base.get('voice',chosen['voice']),speed=chosen['speed'])
    if not track.get('segments'):
     scenes={scene['id']:scene for scene in content['scenes']}
     track['segments']=[dict(item,text=narration(scenes[item['scene_id']],language)) for item in track.get('scenes',[])]
    tracks[language]=track
   primary=primary_language(brief)
   payload={**payload,**tracks[primary],'tracks':tracks,'migration_projection':True}
   if primary!='en' and 'en' in tracks:payload['en']=tracks['en']
  return payload
 def checks(self,j,m,p):
  if m=='content' and self.brief(j):
   from content_contract import validate_content
   b,rev,h=self.brief(j);validate_content(self.root,b,rev,h,p);return []
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.check(self,j,p)
  if m in ('audio','render') and self.brief(j) and self.brief(j)[0].get('outputs'):
   return self.remote_checks(j,m,p)
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
    expected_text=s.get('narration_en' if p.get('language')=='en' else 'narration','')
    if ' '.join(actual.split())!=' '.join(expected_text.split()):raise Blocked('Narration omitted or changed')
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
   if p.get('generation_report'):files.append(p['generation_report'])
   en=p.get('en')
   if self.brief(j):
    from output_contract import languages,primary_language
    if 'en' in languages(self.brief(j)[0]) and primary_language(self.brief(j)[0])!='en' and not en:raise Blocked('English audio required')
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
   from output_contract import outputs
   language=outputs(self.brief(j)[0])[0]['language'] if self.brief(j) else 'vi'
   expected=audio.get('tracks',{}).get(language, audio.get('en') if language=='en' and audio.get('language','vi')!='en' else audio)['duration']
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
 def duration_requirement(self,j,duration,brief):
  """Modern ranges plan the story; only explicit source-backed requirements bind seconds."""
  import math
  if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0:
   raise Blocked('REMOTE_DURATION: measured duration must be positive and finite')
  from execution import is_job,settings
  if not is_job(self,j):
   required=brief['duration']
  else:
   policy=settings(self,j).get('duration_requirement',{'policy':'estimated'})
   if not isinstance(policy,dict) or policy.get('policy') not in ('estimated','required'):
    raise Blocked('DURATION_REQUIREMENT: invalid saved requirement; use the official contract operation')
   if policy['policy']=='estimated':return
   if not isinstance(policy.get('source'),str) or not policy['source'].strip():
    raise Blocked('DURATION_REQUIREMENT: a hard duration needs the actual user requirement source')
   required=policy
  minimum=required.get('min_seconds');maximum=required.get('max_seconds')
  if (type(minimum) not in (int,float) or type(maximum) not in (int,float)
      or not math.isfinite(minimum) or not math.isfinite(maximum) or not 0<minimum<=maximum):
   raise Blocked('DURATION_REQUIREMENT: invalid required window')
  if not minimum<=duration<=maximum:
   raise Blocked(f'DURATION_REQUIRED: measured {duration}s differs from explicitly required {minimum}–{maximum}s; keep audio/content/voice and report the requirement')
 def measured_wav_duration(self,j,name):
  """Read collected PCM headers; no local synthesis, decoding, DSP or waveform scanning."""
  import wave,math
  try:
   path=self.path(j,name)
   with wave.open(str(path)) as handle:
    if handle.getcomptype()!='NONE' or handle.getframerate()<=0 or handle.getnchannels()<=0 or handle.getsampwidth()<=0:
     raise Blocked('REMOTE_DURATION: unsupported collected WAV header')
    duration=handle.getnframes()/handle.getframerate()
    if path.stat().st_size<handle.getnframes()*handle.getnchannels()*handle.getsampwidth():
     raise Blocked('REMOTE_DURATION: collected WAV frame bytes are incomplete')
  except (OSError,EOFError,wave.Error) as ex:
   raise Blocked('REMOTE_DURATION: unreadable collected PCM WAV') from ex
  if not math.isfinite(duration) or duration<=0:raise Blocked('REMOTE_DURATION: collected WAV is empty or invalid')
  return duration
 def remote_checks(self,j,m,payload):
  """Control-side hashes/contracts only; the Colab worker measured the media."""
  from output_contract import languages,primary_language,narration,outputs,voice_settings
  import math
  brief=self.brief(j)[0];content=self.payload(j,'content');files=[]
  if m=='audio':
   folder=self.path(j,payload['wav']).parent
   report_path=folder/'audio-result.json';report=read(report_path)
   effective=folder/'request-colab-effective.json'
   if not effective.is_file():raise Blocked('REMOTE_PROVENANCE: effective immutable audio request missing')
   request=read(effective)
   if report.get('request_id')!=request['request_id'] or report.get('processing_location')!='colab' or report.get('language')!=primary_language(brief):raise Blocked('REMOTE_PROVENANCE: audio request/language/location mismatch')
   files=[str(report_path.relative_to(self.job(j))),str(effective.relative_to(self.job(j)))]
   for name,stamp in report.get('files',{}).items():
    path=folder/name
    if Path(name).name!=name or path.is_symlink() or not path.is_file() or path.stat().st_size==0 or digest(path)!=stamp:raise Blocked('REMOTE_ARTIFACT: changed or missing audio '+name)
    files.append(str(path.relative_to(self.job(j))))
   tracks=payload.get('tracks',{})
   if set(tracks)!=set(languages(brief)):raise Blocked('REMOTE_TRACKS: requested audio languages missing or extra')
   primary=tracks[primary_language(brief)]
   imported_duration=payload.get('duration')
   if type(imported_duration) not in (int,float) or not math.isfinite(imported_duration) or imported_duration<=0 or imported_duration!=primary.get('duration') or payload.get('wav')!=primary.get('wav'):raise Blocked('REMOTE_DURATION: primary imported duration/WAV differs from the selected track')
   for language,track in tracks.items():
    expected_voice=voice_settings(brief,language,read(self.root/'config.json'))
    if track.get('language')!=language or track.get('voice')!=expected_voice['voice'] or abs(track.get('speed',0)-expected_voice['speed'])>1e-8:raise Blocked('REMOTE_VOICE: track identity/rate differs from contract')
    if request.get('profiles',{}).get(language,{}).get('voice')!=expected_voice['voice']:raise Blocked('REMOTE_VOICE: effective request identity differs from contract')
    if any(abs(item['speed']-expected_voice['speed'])>1e-8 for item in request.get('items',[]) if item['language']==language):raise Blocked('REMOTE_VOICE: effective request rate differs from contract')
    duration=track.get('duration',0)
    self.duration_requirement(j,duration,brief)
    measured=self.measured_wav_duration(j,track['wav'])
    if abs(measured-duration)>2/48000:raise Blocked('REMOTE_DURATION: collected WAV and imported track duration differ')
    last=0
    segments=track.get('segments',[])
    for segment in segments:
     boundaries=[segment.get('start'),segment.get('end'),segment.get('content_end',segment.get('end'))]
     if any(type(value) not in (int,float) or not math.isfinite(value) for value in boundaries):raise Blocked('REMOTE_TIMELINE: segment boundaries must be finite numbers')
     if segment['start']<0 or abs(segment['start']-last)>2/48000 or segment['end']<=segment['start'] or not segment['start']<segment.get('content_end',segment['end'])<=segment['end']:raise Blocked('REMOTE_TIMELINE: invalid segment boundaries')
     if segment['path'] not in files:raise Blocked('REMOTE_ARTIFACT: segment missing from hashed manifest')
     actual_segment=self.measured_wav_duration(j,segment['path'])
     if abs(actual_segment-(segment['end']-segment['start']))>2/48000:raise Blocked('REMOTE_DURATION: segment PCM header differs from timeline')
     last=segment['end']
    if abs(last-duration)>.01:raise Blocked('REMOTE_TIMELINE: track duration mismatch')
    if {x['scene_id'] for x in segments}!={s['id'] for s in content['scenes']}:raise Blocked('REMOTE_NARRATION: scene mismatch')
    for scene in content['scenes']:
     actual=' '.join(x['text'] for x in segments if x['scene_id']==scene['id'])
     if ' '.join(actual.split())!=' '.join(narration(scene,language).split()):raise Blocked('REMOTE_NARRATION: omitted or changed words')
    for name in ('wav','srt'):
     if track[name] not in files:raise Blocked('REMOTE_ARTIFACT: track missing from manifest')
   raw=report['payload']
   def localize(value):
    value=json.loads(json.dumps(value))
    for key in ('wav','srt','generation_report'):
     if key in value:value[key]=str((folder/value[key]).relative_to(self.job(j)))
    for field in ('segments','scenes'):
     for item in value.get(field,[]):item['path']=str((folder/item['path']).relative_to(self.job(j)))
    return value
   wanted=localize(raw)
   wanted['tracks']={lang:localize(track) for lang,track in raw.get('tracks',{}).items()}
   if raw.get('en'):wanted['en']=localize(raw['en'])
   if payload!=wanted:raise Blocked('REMOTE_PAYLOAD: imported audio differs from immutable result')
  else:
   folder=self.path(j,payload['remote_report']).parent
   request=read(folder/'request-colab-render.json')
   from colab_bridge.job_protocol import validate_render_result
   audio=self.payload(j,'audio')
   for language in languages(brief):
    source=audio.get('tracks',{}).get(language)
    requested=request.get('audio',{}).get('tracks',{}).get(language)
    if not source or not requested:raise Blocked('REMOTE_DURATION: requested/current audio track is missing')
    duration=source.get('duration')
    self.duration_requirement(j,duration,brief)
    if abs(self.measured_wav_duration(j,source['wav'])-duration)>2/48000:raise Blocked('REMOTE_DURATION: current audio WAV and track duration differ')
    if {k:v for k,v in source.items() if k!='wav'}!={k:v for k,v in requested.items() if k!='wav'}:raise Blocked('REMOTE_PROVENANCE: render audio differs from current track')
    record=next((entry for entry in request.get('files',[]) if entry.get('name')==requested['wav']),None)
    path=self.path(j,source['wav'])
    if not record or record.get('sha256')!=digest(path) or record.get('size')!=path.stat().st_size:raise Blocked('REMOTE_ARTIFACT: render audio input differs from current collected WAV')
   files=[str((folder/name).relative_to(self.job(j))) for name in validate_render_result(folder,request)]
   if request['brief']!=brief:raise Blocked('REMOTE_PROVENANCE: render brief differs from current contract')
   if request['content']!=content:raise Blocked('REMOTE_PROVENANCE: render dialogue differs from current content')
   report=read(self.path(j,payload['remote_report']))
   delivered=report['outputs'][0]['duration']
   if type(payload.get('duration')) not in (int,float) or not math.isfinite(payload['duration']) or delivered<=0 or abs(payload['duration']-delivered)>1e-8:raise Blocked('REMOTE_DURATION: imported video differs from measured remote result')
   for name in ('video','layout_report','editorial_report'):
    if payload[name] not in files:raise Blocked('REMOTE_ARTIFACT: output missing from hashed manifest')
   layout=read(self.path(j,payload['layout_report']))
   if layout.get('passed') is not True:raise Blocked('REMOTE_LAYOUT: layout check failed')
   audit=read(self.path(j,payload['editorial_report']))
   if audit.get('errors') or any(v.get('errors') for v in audit.get('tracks',{}).values()):raise Blocked('REMOTE_CAPTIONS: subtitle technical defects')
   files.append(str((folder/'request-colab-render.json').relative_to(self.job(j))))
  if not files:raise Blocked('REMOTE_ARTIFACT: missing remote manifest')
  return list(dict.fromkeys(files))
 def run(self,j,m):
  from execution import is_job, before_submit
  if is_job(self,j):before_submit(self,j,'flow' if m=='images' else 'colab' if m in ('audio','render') else None)
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
    lines=[f"# {j} — images revision {rev} — {p['checkpoint']}",'','Bước ảnh nội bộ đã kiểm tra kỹ thuật; cần đối chiếu từng ảnh thật.','']
    if p.get('contact_sheet'):lines.append(f"![Bảng ảnh]({self.path(j,p['contact_sheet'])})")
    if p.get('gallery'):lines.append(f"[Danh sách ảnh]({self.path(j,p['gallery'])})")
    for x in p['references']+p['items']+p['proofs']:lines += ['',f"## {x['scene_id']}",f"![{x['scene_id']}]({self.path(j,x['path'])})",x['actual_prompt']]
    (out/'review.md').write_text('\n'.join(lines))
    files += [str((out/n).relative_to(self.job(j))) for n in ['images.json','checks.json','review.md']]
   e={'schema_version':'1.0','job_id':j,'module':m,'revision':rev,'input_versions':versions,'files':files,'payload':p,'checks':{'passed':True,'errors':[]}}
   jsonschema.validate(e,read(self.root/'schemas/envelope.json'))
   ep=out/'output.json';write(ep,e);h=self.snapshot_hash(j,e)
   self.db.execute('UPDATE modules SET state=?,revision=?,envelope=?,hash=? WHERE job=? AND module=?',('awaiting_review',rev,str(ep.relative_to(self.job(j))),h,j,m));self.db.commit();self.event(j,m,'awaiting_review',str(rev));self.resolve_issues(j,m,rev)
  except Exception as ex:
   self.issue(j,m,str(ex),evidence=str((out/'failure.json').relative_to(self.job(j))))
   write(out/'failure.json',{'error':str(ex),'errors':getattr(ex,'errors',[]),'passed':False});self.db.execute('UPDATE modules SET state=?,revision=? WHERE job=? AND module=?',('blocked',rev,j,m));self.db.commit();self.event(j,m,'blocked',str(ex));raise
 def validate(self,j,m):
  self.gate(j,m);r=self.rows(j)[m]
  if r['state'] in ['stale','blocked','pending','running']:raise Blocked('Must run module to create a fresh validated revision')
  e=read(self.path(j,r['envelope']));self.checks(j,m,e['payload'])
  if e['input_versions']!=self.input_versions(j,m):raise Blocked('Input version mismatch')
  return {'passed':True,'revision':r['revision']}
 def approve(self,j,m,rev,note,checkpoint=None,actor='user'):
  from execution import is_job,require
  if is_job(self,j):
   require(self,j,'execute')
   if getattr(self,'_execution_job',None)!=j:raise Blocked('JOB_LEASE_REQUIRED: technical acceptance requires this job controller')
   if actor!='technical':raise Blocked('Use exact output checkpoint approval for a user decision')
  if m=='images' and self.brief(j):
   import image_pipeline
   return image_pipeline.approve(self,j,rev,note,checkpoint,actor)
  self.validate(j,m);r=self.rows(j)[m]
  if r['state']!='awaiting_review' or r['revision']!=rev or not note.strip():raise Blocked('Explicit approval of current awaiting revision required')
  self.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',('approved',j,m));self.db.commit();self.event(j,m,'technical_accepted' if actor=='technical' else 'approved',json.dumps({'revision':rev,'actor':actor,'note':note},ensure_ascii=False))
 def reject(self,j,m,note,rev=None,checkpoint=None,scene=None,character=None,image=None,ratio=None,repair_plan=None):
  from execution import is_job, require
  if is_job(self,j):require(self,j,'repair')
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
  from execution import is_job,observe
  if is_job(self,j):return observe(self,j)
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
  from execution import is_job,next_step
  if is_job(self,j):return next_step(self,j)
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

class PilotView(Pilot):
 """Read-only observations: no schema setup, mkdir, state refresh or lock files."""
 def __init__(self,root=ROOT):
  self.root=Path(root)
  self._db_lock=threading.Lock()
  path=self.root/'.state/jobs.sqlite'
  if not path.is_file():raise Blocked('No local job database exists')
  self.db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,check_same_thread=False)
  self.db.row_factory=sqlite3.Row
  self.db.execute('PRAGMA query_only=ON')
  self._read_only=True
 def event(self,*args,**kwargs):raise Blocked('Observation cannot append events')
 def refresh(self,*args,**kwargs):raise Blocked('Observation cannot refresh mutable job state')
 def status(self,j):
  from execution import is_job,observe
  if is_job(self,j):return observe(self,j)
  rows=self.rows(j)
  if not rows:raise Blocked('Unknown job')
  modules=[]
  for m,row in rows.items():
   state=row['state']
   if row['envelope']:
    try:
     envelope=read(self.path(j,row['envelope']))
     if self.snapshot_hash(j,envelope)!=row['hash'] or envelope['input_versions']!=self.input_versions(j,m):state='stale'
    except (OSError,ValueError,KeyError):state='stale'
   modules.append({**row,'observed_state':state})
  return {'job':j,'version':3,'read_only':True,'modules':modules,'complete':all(x['observed_state']=='approved' for x in modules)}


def observe_job(root,job,next_only=False):
 import execution,workflow
 p=PilotView(root)
 try:
  if execution.is_job(p,job):return execution.next_step(p,job) if next_only else execution.observe(p,job)
  state=p.status(job)
  cfg=read(p.job(job)/'workflow.json') if (p.job(job)/'workflow.json').exists() else {}
  state['mode']=cfg.get('mode');state['legacy']=True
  if next_only:
   for row in state['modules']:
    if row['observed_state']!='approved':return {**state,'action':'legacy_run_or_review','module':row['module']}
   state['action']='complete'
  return state
 finally:p.db.close()


def main():
 import workflow,execution
 from permissions import Grants
 ap=argparse.ArgumentParser(description='Video Pilot: quyền bền vững, auto/review theo đầu ra')
 commands=['lift-cap','doctor','new','observe','status','next','repair-status','run','validate','approve','reject','resume','stop','takeover','mode','bind-session','author','micro-plan','micro-result','grant','grants','revoke-grant','migrate','rollback-migration','flow-login','flow-preflight','flow-reconcile','flow-confirm-registration','check-draft','revise-brief','batch','integrity-diff','adopt-code']
 ap.add_argument('command',choices=commands)
 ap.add_argument('job',nargs='?');ap.add_argument('stage',nargs='?',choices=list(workflow.STAGES)+list(execution.CHECKPOINTS))
 ap.add_argument('--mode',choices=['review','auto'])
 ap.add_argument('--engine',type=int,choices=[3,4],default=4)
 ap.add_argument('--revision',type=int);ap.add_argument('--note',default='')
 for name in ['evidence','scene','asset','character','request','brief','queue','image','repair-plan','grant','production-grant','source','data','session','fingerprint']:
  ap.add_argument('--'+name)
 ap.add_argument('--role',choices=['setup','production','development','maintenance'])
 ap.add_argument('--operations',nargs='+');ap.add_argument('--jobs',nargs='+',default=[]);ap.add_argument('--paths',nargs='+',default=[])
 ap.add_argument('--part',choices=['audio']);ap.add_argument('--ratio',choices=['9:16','16:9'])
 ap.add_argument('--retry-review',action='store_true')
 ap.add_argument('--confirm');ap.add_argument('--reason',default='')
 a=ap.parse_args();c=a.command
 if c=='doctor':
  result={'tools':{t:shutil.which(t) for t in ['node','python3','ffprobe','google-chrome','agy']},'workflow_version':4,'legacy_versions':[3],'checkpoints':list(execution.CHECKPOINTS),'modes':['review','auto'],'auto_reviewer':False,'permission_transport_verified':False}
 elif c in ('grants','grant','revoke-grant'):
  store=Grants(ROOT)
  if c=='grants':result=store.read()
  elif c=='grant':result=store.grant(a.role,source=a.source,jobs=a.jobs,paths=a.paths,operations=a.operations)
  else:result=store.revoke(a.grant,source=a.source or '')
 elif c in ('observe','status','next','integrity-diff','repair-status'):
  if not a.job:raise Blocked('Job required')
  if c in ('integrity-diff','repair-status'):
   p=PilotView(ROOT)
   try:
    if c=='integrity-diff':result=p.integrity_diff(a.job)
    else:
     from scripts.image_repairs import status as repair_status
     result=repair_status(p,a.job,a.image,a.ratio)
   finally:p.db.close()
  else:result=observe_job(ROOT,a.job,c=='next')
 else:
  if not a.job and c!='batch':raise Blocked('Job required')
  store=Grants(ROOT)
  if c=='new' and a.engine==4:
   authority=store.require(a.grant,'production','execute',job=a.job) if a.grant else store.find('production','execute',job=a.job)
   if authority is None:
    if not a.source:raise Blocked('New execution requires an existing --grant or the actual --source authorization')
    authority=store.grant('production',source=a.source,jobs=[a.job],paths=['sys/runs/'+a.job+'/**' if store.project_root!=store.system_root else 'runs/'+a.job+'/**'])
   a.grant=authority['id']
  p=Pilot(ROOT)
  try:
   modern=(p.job(a.job)/'workflow.json').is_file() and execution.is_job(p,a.job) if a.job else False
   # v4 controllers own an individual job; legacy writers retain their old global lock.
   scope=contextlib.nullcontext() if modern or c in ('new','migrate','rollback-migration') else locked(ROOT)
   with scope:
    if c=='new':result=execution.new(p,a.job,read(a.brief) if a.brief else None,a.mode or 'review',a.grant,a.session) if a.engine==4 else workflow.new(p,a.job,read(a.brief) if a.brief else None,a.mode or 'review')
    elif c=='batch':
     if not a.queue:raise Blocked('batch requires --queue JSON list of existing auto job IDs')
     jobs=read(a.queue)
     if not isinstance(jobs,list) or not jobs or any(not isinstance(j,str) for j in jobs) or len(set(jobs))!=len(jobs):raise Blocked('Queue must contain unique job IDs')
     result=workflow.batch(p,jobs)
    elif c=='adopt-code':
     if not a.grant:raise Blocked('adopt-code requires a scoped development --grant and actual --reason')
     with execution.lease(p,a.job):result=p.adopt_code(a.job,a.confirm,a.reason,a.grant)
    elif c=='migrate':result=execution.migrate(p,a.job,a.grant,a.production_grant,a.source or '',a.mode)
    elif c=='rollback-migration':result=execution.rollback_migration(p,a.job,a.grant,a.source or '')
    elif c in ('stop','takeover','mode','bind-session','author','micro-plan','micro-result'):
     if not modern:raise Blocked('Explicit v3 migration is required for this operation')
     if c=='mode':result=execution.change_mode(p,a.job,a.mode,a.source or '')
     elif c=='bind-session':result=execution.bind_session(p,a.job,a.session,a.source or '')
     elif c=='author':
      if not a.data:raise Blocked('author requires --data JSON file')
      result=execution.author(p,a.job,a.stage,read(a.data),a.source or '')
     elif c=='micro-result':
      if not a.data:raise Blocked('micro-result requires --data JSON file')
      result=execution.micro_result(p,a.job,a.fingerprint,read(a.data))
     elif c=='micro-plan':
      if not a.data:raise Blocked('micro-plan requires --data JSON file')
      with execution.lease(p,a.job):result=execution.micro_plan(p,a.job,read(a.data))
     else:result=getattr(execution,c)(p,a.job,a.source or '')
    elif c=='repair-status':
     from scripts.image_repairs import status as repair_status
     result=repair_status(p,a.job,a.image,a.ratio)
    else:
     workflow.settings(p,a.job)
     if c=='lift-cap':
      if modern:raise Blocked('Engine v4 uses evidence/progress recovery, not total repair caps')
      if not sys.stdin.isatty() or input(f'Gõ lại mã job {a.job} để xác nhận mở khóa: ').strip()!=a.job:raise Blocked('lift-cap chỉ dành cho người dùng, chạy trực tiếp trong terminal')
      result=workflow.lift_cap(p,a.job,a.note)
     elif c=='resume' and modern:result=execution.resume(p,a.job)
     elif c in ('run','resume'):result=workflow.advance(p,a.job,a.stage,retry_review=a.retry_review)
     elif c=='check-draft':
      with execution.lease(p,a.job) if modern else contextlib.nullcontext():result=p.check_draft(a.job)
     elif c=='revise-brief':
      if not a.brief:raise Blocked('--brief FILE required')
      with execution.lease(p,a.job) if modern else contextlib.nullcontext():p.revise_brief(a.job,read(a.brief),a.note)
      result=workflow.status(p,a.job)
     elif c.startswith('flow-'):
      import adapters
      with execution.lease(p,a.job) if modern else contextlib.nullcontext():
       if modern:execution.require(p,a.job,'execute')
       result=adapters.flow_action(p,a)
     else:
      if not a.stage:raise Blocked('Output checkpoint required')
      if c=='approve':result=workflow.approve(p,a.job,a.stage,a.revision,a.note)
      elif c=='reject':result=workflow.reject(p,a.job,a.stage,a.revision,a.note,a.part,a.scene,a.character,a.image,a.ratio,read(a.repair_plan) if a.repair_plan else None)
      elif c=='validate':
       modules=[execution.MODULES[a.stage]] if modern and a.stage in execution.MODULES else workflow.STAGES.get(a.stage,())
       if not modules:raise Blocked('Select an output with a technical module')
       with execution.lease(p,a.job) if modern else contextlib.nullcontext():
        for module in modules:p.validate(a.job,module)
       result={'passed':True,'stage':a.stage}
   print(json.dumps(result,ensure_ascii=False,indent=2))
   if result.get('passed') is False or result.get('blocked'):return 2
   return 0
  finally:p.db.close()
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'blocked':str(e),'errors':getattr(e,'errors',[])},ensure_ascii=False));sys.exit(2)
