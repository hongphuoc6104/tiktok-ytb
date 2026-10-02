from pathlib import Path
import json,subprocess,time,sqlite3,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/opening-audit-A1-331-20261001'
BASE={x['number']:x for x in json.loads((OUT/'baseline.json').read_text())}
M=json.loads((OUT/'manifest.json').read_text());USER=(OUT/'authoring/user-request.txt').read_text().strip()
(OUT/'operations-local').mkdir(exist_ok=True)
def save():
 (OUT/'manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n')
def log_error(j,cmd,data):
 p=ROOT/'logs/issues/ISSUE-OPENING-A1-331-20261001.md'
 with p.open('a') as f:f.write(f'\n## Lỗi {j} — {cmd}\n\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```\n\nGiữ job hiện tại; không sửa code, không tạo job khác hoặc thay baseline.\n')
def call(j,cmd,*args):
 for a in range(6000):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py',cmd,j,*args],cwd=ROOT,capture_output=True,text=True)
  try:d=json.loads(r.stdout)
  except Exception:
   log_error(j,cmd,{'output':r.stdout,'stderr':r.stderr});raise
  if d.get('blocked')=='Another operation is running':
   if a%800==0:print('WAIT',j,cmd,flush=True)
   time.sleep(.05);continue
  (OUT/'operations-local'/f'{j}-{cmd}.json').write_text(r.stdout)
  if r.returncode or d.get('blocked') or d.get('passed') is False:
   log_error(j,cmd,d);raise RuntimeError(r.stdout)
  return d
 log_error(j,cmd,{'error':'Bounded lock wait exhausted'})
 raise RuntimeError('Bounded lock wait exhausted')
def feedback(j):
 with sqlite3.connect(f'file:{ROOT}/.state/jobs.sqlite?mode=ro',uri=True) as db:
  return db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id",(j,)).fetchall()
for e in M:
 if len(__import__('sys').argv)>1 and e['number']!=int(__import__('sys').argv[1]):continue
 n=e['number'];j=e['job'];base=BASE[n]['content'];r1=ROOT/'runs'/j/'revisions/content/1/content.json'
 assert hashlib.sha256(r1.read_bytes()).hexdigest()==BASE[n]['saved_r1_sha256'],j
 if e['state']=='awaiting_review' and e.get('content_revision') in [1,2]:
  rev=e['content_revision'];saved=json.loads((ROOT/'runs'/j/f'revisions/content/{rev}/content.json').read_text());planned=json.loads((OUT/'candidates'/f'{n}.json').read_text())
  assert {k:v for k,v in saved.items() if k!='revision_response'}=={k:v for k,v in planned.items() if k!='revision_response'},j
  assert json.loads((ROOT/'runs'/j/'draft/content.json').read_text())==saved,j
  continue # already checked and submitted through CLI in this finite operation
 s=call(j,'status');nx=call(j,'next');diff=call(j,'integrity-diff')
 if diff['changed']:
  log_error(j,'integrity-diff',diff);raise RuntimeError('Protected implementation changed '+j)
 st=s['stages'][0];candidate=json.loads((OUT/'candidates'/f'{n}.json').read_text())
 if s.get('complete') or s['mode']!='review' or any(x.get('revision') for x in s['stages'][1:]):
  e.update(state='skipped_protected',skip_reason='Job has progressed beyond untouched content; no mutation',status_snapshot=s);save();print('SKIP',n,j,flush=True);continue
 if not e['changed']:
  assert st['state']=='awaiting_review' and st['revision']==1,s
  assert json.loads(r1.read_text())==candidate,j
  check=call(j,'check-draft')
  e.update(state='awaiting_review',content_revision=1,checks_passed=check['passed'],review=str(ROOT/'runs'/j/'reviews/content/1/review.md'));save();print('KEEP',n,j,flush=True);continue
 if st['state']=='awaiting_review' and st['revision']==2:
  saved=json.loads((ROOT/'runs'/j/'revisions/content/2/content.json').read_text())
  assert {k:v for k,v in saved.items() if k!='revision_response'}=={k:v for k,v in candidate.items() if k!='revision_response'},j
  e.update(state='awaiting_review',content_revision=2,review=str(ROOT/'runs'/j/'reviews/content/2/review.md'));save();print('EXISTING R2',n,j,flush=True);continue
 note=USER+'\n\nBài '+str(n)+': sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.'
 existing_requests=feedback(j)
 owned_pending=st['state']=='pending' and st['revision'] is None and bool(existing_requests) and existing_requests[-1][1]==note
 if owned_pending:
  draft=json.loads((ROOT/'runs'/j/'draft/content.json').read_text())
  assert {k:v for k,v in draft.items() if k!='revision_response'}=={k:v for k,v in candidate.items() if k!='revision_response'},j
 if not owned_pending and (st['revision']!=1 or st['state'] not in ['awaiting_review','needs_changes']):
  e.update(state='skipped_protected',skip_reason='Current revision or state changed outside this edit',status_snapshot=s);save();print('SKIP',n,j,flush=True);continue
 if st['state']=='awaiting_review':call(j,'reject','content','--revision','1','--note',note)
 requests=feedback(j)
 assert requests and requests[-1][1]==note,(j,requests)
 candidate['revision_response']=[{'request_id':str(rid),'status':'addressed','explanation':'Đã rà 3 giây đầu: mở bằng “'+e['opening']+'”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.','scene_ids':['SC01']} for rid,text in requests]
 path=ROOT/'runs'/j/'draft'
 (path/'content.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
 (path/'outline.json').write_text(json.dumps({'outline':candidate['outline']},ensure_ascii=False,indent=2)+'\n')
 check=call(j,'check-draft');out=call(j,'run','content')
 assert out.get('state')=='awaiting_review' and out.get('revision')==2,out
 assert hashlib.sha256(r1.read_bytes()).hexdigest()==BASE[n]['saved_r1_sha256'],j
 saved=ROOT/'runs'/j/'revisions/content/2/content.json';assert json.loads(saved.read_text())==candidate,j
 assert candidate['scenes'][1:]==base['scenes'][1:],j
 e.update(state='awaiting_review',content_revision=2,checks_passed=check['passed'],review=out['review'],request_ids=[str(r[0]) for r in requests],content_sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
 save();print('UPDATED',n,j,'r2',flush=True)
print('APPLY COMPLETE',sum(e.get('content_revision')==2 for e in M),'r2',sum(e.get('content_revision')==1 for e in M),'r1',sum(e['state']=='skipped_protected' for e in M),'skips',flush=True)
