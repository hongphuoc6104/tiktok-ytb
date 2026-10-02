from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-341-440-20260930';m=json.loads((out/'selection.json').read_text())
def call(args):
 for a in range(1500):
  r=subprocess.run([str(p/'.venv/bin/python'),*args],cwd=p,capture_output=True,text=True)
  d=json.loads(r.stdout)
  if 'Another operation is running' in r.stdout:
   if a%100==0:print('Waiting for current operation',args[-1],flush=True)
   time.sleep(0.4);continue
  if r.returncode or d.get('blocked'):raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Operation lock timeout')
for e in m:
 j=e['job'];r=p/'runs'/j
 if r.exists():
  import hashlib
  ledger=json.loads((p/'vocab/ledger.json').read_text())['entries'];assert ledger[e['id']]['job']==j
  print('EXISTING',e['number'],e['word'],flush=True);continue
 d=call(['vocab/bank.py','start',j,'--mode','review','--level','A1']+(['--topic','entertainment-media'] if e['word']=='TV' else ['--word',e['word']]));(out/'operations-local'/f"{e['number']}-start.json").write_text(json.dumps(d,ensure_ascii=False,indent=2))
 # status and next are executed before content submission by submit_content.py.
 print('STARTED',e['number'],e['word'],flush=True)
