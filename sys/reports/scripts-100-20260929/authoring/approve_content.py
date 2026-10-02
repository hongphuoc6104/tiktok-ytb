from pathlib import Path
import json,subprocess,time,hashlib
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260929';m=json.loads((out/'manifest.json').read_text());note='tôi duyệt 100 kịch bản trên.';results=[]
def cli(j,cmd,*args):
 for attempt in range(36):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py',cmd,j,*args],cwd=p,capture_output=True,text=True);d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':time.sleep(5);continue
  (out/'operations-local'/f'{j}-{cmd}-approval.json').write_text(r.stdout)
  if r.returncode or d.get('blocked'):raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Another operation is running: bounded wait exhausted')
for e in m:
 j=e['job'];src=p/'runs'/j/'revisions/content/1/content.json';assert hashlib.sha256(src.read_bytes()).hexdigest()==e['content_sha256'];assert src.read_bytes()==(out/e['content_path']).read_bytes()
 d=cli(j,'status');cli(j,'next');s=d['stages'][0];assert s['revision']==1 and s['state']=='awaiting_review',d
 cli(j,'approve','content','--revision','1','--note',note)
 d=cli(j,'status');assert d['stages'][0]['state']=='approved' and all(x['state']=='pending' for x in d['stages'][1:]),d
 decision=json.loads((p/'runs'/j/'reviews/content/1/decision.json').read_text());assert decision['approved'] and decision['note']==note
 e['state']='approved';results.append({'job':j,'number':e['number'],'revision':1,'state':'approved','note':note,'content_sha256':e['content_sha256'],'media':'pending','video':'pending'})
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(out/'approval-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('APPROVED',e['number'],e['word'],flush=True)
print('COMPLETE: 100 approved; no media',flush=True)
