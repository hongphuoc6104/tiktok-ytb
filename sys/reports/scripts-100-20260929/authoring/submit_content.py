from pathlib import Path
import json,subprocess,time,hashlib
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260929';m=json.loads((out/'manifest.json').read_text())
def call(j,cmd,*args):
 for attempt in range(120):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py',cmd,j,*args],cwd=p,capture_output=True,text=True)
  d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':
   if attempt%6==0:print('WAIT',j,cmd,flush=True)
   time.sleep(5);continue
  (out/'operations-local'/f'{j}-{cmd}.json').write_text(r.stdout)
  if r.returncode or d.get('blocked') or d.get('passed') is False:raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Bounded wait for current production lock exhausted')
for e in m:
 j=e['job'];d=call(j,'status');call(j,'next');diff=call(j,'integrity-diff')
 if diff['changed']:raise RuntimeError('Protected implementation changed '+j)
 if d['stages'][0]['state']!='pending':raise RuntimeError('Unexpected existing content '+j)
 call(j,'check-draft');result=call(j,'run','content')
 assert result.get('state')=='awaiting_review' and result.get('revision')==1,result
 e.update(state='awaiting_review',content_revision=1,review=result['review']);(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 print('DONE',e['number'],e['word'],flush=True)
print('COMPLETE 100 content revisions; no media run',flush=True)
