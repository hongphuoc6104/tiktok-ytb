from pathlib import Path
import json,subprocess,time,hashlib
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-341-440-20260930';m=json.loads((out/'manifest.json').read_text());note='tôi đã đọc và duyệt qua, cập nhật đi';results=[]
def cli(j,cmd,*args):
 for attempt in range(6000):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py',cmd,j,*args],cwd=p,capture_output=True,text=True);d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':
   if attempt%400==0:print('WAIT',e['number'],cmd,flush=True)
   time.sleep(0.05);continue
  (out/'operations-local'/f'{j}-{cmd}-approval.json').write_text(r.stdout)
  if r.returncode or d.get('blocked'):
   if 'Protected implementation changed' in r.stdout:
    evidence=subprocess.run([str(p/'.venv/bin/python'),'pilot.py','integrity-diff',j],cwd=p,capture_output=True,text=True)
    (out/'operations-local'/f'{j}-integrity-diff-approval.json').write_text(evidence.stdout)
   raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Another operation is running: bounded wait exhausted')
for e in m:
 j=e['job'];src=p/'runs'/j/'revisions/content/1/content.json';assert hashlib.sha256(src.read_bytes()).hexdigest()==e['content_sha256'];assert src.read_bytes()==(out/e['content_path']).read_bytes()
 d=cli(j,'status');s=d['stages'][0];assert s['revision']==1 and s['state'] in {'awaiting_review','approved'},d
 # Both status and approve check integrity through the standard CLI.
 if s['state']=='awaiting_review':d=cli(j,'approve','content','--revision','1','--note',note)
 else:
  prior=json.loads((p/'runs'/j/'reviews/content/1/decision.json').read_text());assert prior['approved'] and prior['note']==note,prior
 # approve returns the updated workflow status.
 assert d['stages'][0]['state']=='approved' and all(x['state']=='pending' for x in d['stages'][1:]),d
 decision=json.loads((p/'runs'/j/'reviews/content/1/decision.json').read_text());assert decision['approved'] and decision['note']==note and decision['actor']=='user'
 e['state']='approved';results.append({'job':j,'number':e['number'],'revision':1,'state':'approved','note':note,'content_sha256':e['content_sha256'],'media':'pending','video':'pending'})
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(out/'approval-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('APPROVED',e['number'],e['word'],flush=True)
print('COMPLETE: 100 approved; no media',flush=True)
