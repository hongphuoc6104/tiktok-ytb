from pathlib import Path
import json,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/opening-audit-A1-331-20261001'
baseline=json.loads((OUT/'baseline.json').read_text());(OUT/'operations-local').mkdir(exist_ok=True)
def call(job,cmd,*args):
 for a in range(1200):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py',cmd,job,*args],cwd=ROOT,capture_output=True,text=True)
  try:d=json.loads(r.stdout)
  except Exception:raise RuntimeError(r.stdout+r.stderr)
  if d.get('blocked')=='Another operation is running':
   if a%120==0:print('WAIT',job,cmd,flush=True)
   time.sleep(.5);continue
  (OUT/'operations-local'/f'{job}-{cmd}-before.json').write_text(r.stdout)
  if r.returncode or d.get('blocked'):raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Bounded wait exhausted; no lock deletion or code changes')
if __name__=='__main__':
 eligible=[];skipped=[]
 for x in baseline:
  e=x['entry'];j=e['job'];d=call(j,'status');nx=call(j,'next');integ=call(j,'integrity-diff')
  if integ['changed']:raise RuntimeError('Protected implementation changed '+j+' '+str(integ))
  st=d['stages'][0]
  if d.get('complete') or d['mode']!='review' or st['state']!='awaiting_review' or st['revision']!=1 or any(s.get('revision') for s in d['stages'][1:]):
   skipped.append({'number':x['number'],'job':j,'reason':'Current state differs from untouched content-r1 awaiting review','status':d})
  else:eligible.append(x['number'])
  (OUT/'eligibility.json').write_text(json.dumps({'eligible':eligible,'skipped':skipped,'scanned':len(eligible)+len(skipped)},ensure_ascii=False,indent=2)+'\n')
  if len(eligible)%25==0:print('SCANNED',len(eligible)+len(skipped),flush=True)
 print('PREFLIGHT COMPLETE',len(eligible),'eligible',len(skipped),'skip',flush=True)
