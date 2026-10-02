from pathlib import Path
import json,subprocess,time,sqlite3,hashlib
p=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
manifest=json.loads((out/'manifest.json').read_text())
NOTE='những bài nào không được bảo vệ thì bạn hãy thay đổi theo cách mới đi để tôi sẽ render và đăng lên nền tảng ngay để kiểm tra số liệu.'
def cli(job,command,*args):
 for attempt in range(90):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py',command,job,*args],cwd=p,capture_output=True,text=True)
  try:d=json.loads(r.stdout)
  except ValueError:raise RuntimeError(r.stdout+r.stderr)
  if d.get('blocked')=='Another operation is running':
   if attempt%6==0:print('Waiting for existing production operation:',job,command,flush=True)
   time.sleep(5);continue
  (out/'operations'/f'{job}-{command}-{int(time.time()*1000)}.json').write_text(r.stdout)
  if r.returncode or d.get('blocked') or d.get('passed') is False:raise RuntimeError(json.dumps(d,ensure_ascii=False))
  return d
 raise RuntimeError('Existing production lock did not become available; leave proposals unchanged.')
for x in manifest:
 j=x['job'];n=x['number'];job=p/'runs'/j
 status=cli(j,'status');cli(j,'next');diff=cli(j,'integrity-diff')
 if diff['changed']:raise RuntimeError('Integrity changed: '+j)
 cs=status['stages'][0]
 if cs['state']!='awaiting_review' or cs['revision']!=1 or any(s['state']!='pending' for s in status['stages'][1:]):raise RuntimeError('Unexpected state: '+j)
 if hashlib.sha256((job/'revisions/content/1/content.json').read_bytes()).hexdigest()!=x['source_sha256']:raise RuntimeError('Source changed: '+j)
 cli(j,'reject','content','--revision','1','--note',NOTE)
 # Read-only lookup of generated feedback IDs; all state mutations use the supported CLI.
 with sqlite3.connect('file:'+str(p/'.state/jobs.sqlite')+'?mode=ro',uri=True) as db:
  requests=db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id",(j,)).fetchall()
 c=json.loads((out/'proposals'/f'{n}.json').read_text())
 c['revision_response']=[{'request_id':str(r[0]),'status':'addressed','explanation':'Đã sửa lời dẫn SC01–SC02: mở bằng tình huống/câu tiếng Anh ngay, bỏ dẫn nhập vòng và nối trực tiếp vào câu mẫu. Đã cập nhật hình mở đầu, biến thể cùng góc máy, outline, coverage và neo theo lời chốt. Giữ nguyên SC03–SC05, nghĩa từ, ví dụ bắt buộc và khoảng chờ thực hành. Chưa có số liệu hiệu quả sau đăng.','scene_ids':['SC01','SC02']} for r in requests]
 (job/'draft/content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 # Keep editable outline consistent; immutable revisions/reviews are never edited.
 outline=job/'draft/outline.json'
 if outline.exists():
  od=json.loads(outline.read_text())
  if isinstance(od,dict) and 'outline' in od:od['outline']=c['outline'];outline.write_text(json.dumps(od,ensure_ascii=False,indent=2)+'\n')
 cli(j,'check-draft');result=cli(j,'run','content')
 if result.get('revision')!=2 or result.get('state')!='awaiting_review':raise RuntimeError('Unexpected submission result: '+str(result))
 x.update(state='awaiting_review',revision=2,review=result['review'],content=str(job/'revisions/content/2/content.json'))
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print('DONE',n,x['word'],'revision 2',flush=True)
print('COMPLETE',len(manifest),flush=True)
