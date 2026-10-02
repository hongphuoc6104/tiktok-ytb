from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260929';fixes={201:'wear.v.wear-clothes',203:'take off.phr.remove-clothes',238:'learn.v.acquire-knowledge'};changes=[]
for e in json.loads((out/'selection.json').read_text()):
 if e['number'] not in fixes:continue
 j=p/'runs'/e['job'];meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text());removed=[x for x in b['planning']['avoid'] if fixes[e['number']] in x]
 if not removed:continue
 b['planning']['avoid']=[x for x in b['planning']['avoid'] if x not in removed];b['planning'].setdefault('assumptions',[]).append('Mục khác trong kho trùng hoặc chồng nghĩa đã chọn; bỏ riêng chỉ dẫn tránh mâu thuẫn, giữ nguyên mã mục và một nghĩa.')
 f=out/f"brief-clarification-{e['number']}.json";f.write_text(json.dumps(b,ensure_ascii=False,indent=2))
 for a in range(60):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py','revise-brief',e['job'],'--brief',str(f),'--note','Loại riêng chỉ dẫn tránh nghĩa trùng mâu thuẫn; giữ nguyên mục từ, nghĩa và mọi nghĩa khác cần tránh.'],cwd=p,capture_output=True,text=True)
  if 'Another operation is running' in r.stdout:time.sleep(5);continue
  break
 (out/'operations-local'/f"{e['number']}-revise-brief.json").write_text(r.stdout)
 if r.returncode:raise RuntimeError(r.stdout)
 changes.append({'job':e['job'],'removed':removed,'resolved':True});print('CLARIFIED',e['number'],flush=True)
(out/'brief-clarifications.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
