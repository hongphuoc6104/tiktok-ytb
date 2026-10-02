from pathlib import Path
import subprocess,json,time,hashlib,sqlite3
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'reports/drama-A1-all-20261001';j='vocab-let-script-512';r=ROOT/'runs'/j

def call(cmd,*args):
 for i in range(100):
  z=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py',cmd,j,*args],cwd=ROOT,capture_output=True,text=True);d=json.loads(z.stdout)
  if d.get('blocked')=='Another operation is running':time.sleep(.1);continue
  assert z.returncode==0 and not d.get('blocked') and d.get('passed') is not False,d
  return d
 raise RuntimeError('Bounded lock wait exhausted')
s=call('status');print(s);print(call('next'));assert not call('integrity-diff')['changed']
m=json.loads((P/'manifest.json').read_text());e=next(x for x in m if x['job']==j);epath=P/'narration-frozen'/f'{j}.json';ep=json.loads(epath.read_text());c=json.loads((r/'draft/content.json').read_text());saved=json.loads((r/f"revisions/content/{e['new_content_revision']}/content.json").read_text());assert {k:v for k,v in c.items() if k!='revision_response'}=={k:v for k,v in saved.items() if k!='revision_response'}
assert s['stages'][0]['state']=='pending'
with sqlite3.connect(f'file:{ROOT}/.state/jobs.sqlite?mode=ro',uri=True) as db:last=db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id DESC LIMIT1".replace('LIMIT1','LIMIT 1'),(j,)).fetchone()
assert str(last[0])==c['revision_response'][-1]['request_id'] and last[1].startswith('bắt đầu áp dụng cho toàn bộ kịch bản A1 còn lại')
# Only accurate scene metadata changes; words and anchors remain frozen.
c['scenes'][0]['title']='Giữ mép phông giấy';ep['scenes'][0]['title_vi']='Giữ mép phông giấy';epath.write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n');(r/'draft/content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
check=call('check-draft');result=call('run','content');assert result['state']=='awaiting_review';new=result['revision'];assert json.loads((r/f'revisions/content/{new}/content.json').read_text())==c
reader=Path(e['reader']);text=reader.read_text().replace('Căng bạt sân khấu','Giữ mép phông giấy').replace('Content r'+str(e['new_content_revision']),'Content r'+str(new)).replace(e['review'],result['review']);reader.write_text(text)
e.update(new_content_revision=new,review=result['review'],narration_frozen_sha256=hashlib.sha256(epath.read_bytes()).hexdigest(),checks_passed=check['passed']);(P/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'logs/issues/ISSUE-DRAMA-A1-ALL-20261001.md').open('a') as f:f.write('\n**Làm gì cho hết lỗi let512:** xác nhận draft trùng bản trước sau reject của mình; đổi title SC01 đúng phông giấy (không sửa lời/neo). check-draft passed, run content lưu r'+str(new)+', reader/hash đồng bộ. Lịch sử nguyên vẹn, không đổi mã nguồn/gate.\n')
print('RECOVERED',j,new)
