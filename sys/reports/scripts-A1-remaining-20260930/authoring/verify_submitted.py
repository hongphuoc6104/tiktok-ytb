import json,subprocess,time,hashlib
from source_utils import ROOT,OUT,records
m=json.loads((OUT/'manifest.json').read_text());recs=records();result=[]
for e in m:
 for attempt in range(600):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py','status',e['job']],cwd=ROOT,capture_output=True,text=True);d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':time.sleep(.5);continue
  assert r.returncode==0 and not d.get('blocked'),r.stdout;break
 else:raise RuntimeError('Bounded status wait exhausted')
 stages={s['stage']:s for s in d['stages']}
 assert d['mode']=='review' and not d['complete'],e['job']
 assert stages['content']['state']=='awaiting_review' and stages['content']['revision']==1,e['job']
 assert all(stages[x]['state']=='pending' and stages[x]['revision'] is None for x in ['media','video']),e['job']
 j=ROOT/'runs'/e['job'];saved=j/'revisions/content/1/content.json';c=json.loads(saved.read_text())
 assert [s['narration'] for s in c['scenes']]==[r[0] for r in recs[e['number']]['rows']],e['job']
 assert saved.read_bytes()==(OUT/e['content_path']).read_bytes(),e['job']
 assert c==json.loads((j/'draft/content.json').read_text()),e['job']
 assert all(s['narration'] in (OUT/e['reader_path']).read_text() for s in c['scenes']),e['job']
 result.append({'number':e['number'],'job':e['job'],'mode':'review','content_revision':1,'content_state':'awaiting_review','media_state':'pending','video_state':'pending','source_and_reader_match':True,'content_sha256':hashlib.sha256(saved.read_bytes()).hexdigest()})
 if len(result)%50==0:print('Verified',len(result),flush=True)
(OUT/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS 331 current content r1 waiting for real user review; media/video untouched',flush=True)
