from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260930';m=json.loads((out/'selection.json').read_text())
def call(args):
 for a in range(90):
  r=subprocess.run([str(p/'.venv/bin/python'),*args],cwd=p,capture_output=True,text=True)
  d=json.loads(r.stdout)
  if 'Another operation is running' in r.stdout:
   if a%6==0:print('Waiting for current operation',args[-1],flush=True)
   time.sleep(5);continue
  if r.returncode or d.get('blocked'):raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Operation lock timeout')
for e in m:
 j=e['job'];r=p/'runs'/j
 if r.exists():raise RuntimeError('Unexpected existing job '+j)
 d=call(['vocab/bank.py','start',j,'--mode','review','--word',e['word'],'--level','A1']);(out/'operations-local'/f"{e['number']}-start.json").write_text(json.dumps(d,ensure_ascii=False,indent=2))
 for cmd in ['status','next']:
  d=call(['pilot.py',cmd,j]);(out/'operations-local'/f"{e['number']}-{cmd}.json").write_text(json.dumps(d,ensure_ascii=False,indent=2))
 print('STARTED',e['number'],e['word'],flush=True)
