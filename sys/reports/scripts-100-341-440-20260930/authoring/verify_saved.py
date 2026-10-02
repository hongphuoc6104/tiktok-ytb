from pathlib import Path
import json,subprocess,hashlib,time
p=Path(__file__).resolve().parents[3];o=p/'reports/scripts-100-341-440-20260930';m=json.loads((o/'manifest.json').read_text());result=[]
for e in m:
 for attempt in range(6000):
  r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py','status',e['job']],cwd=p,capture_output=True,text=True);d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':
   if attempt%400==0:print('WAIT VERIFY',e['number'],flush=True)
   time.sleep(0.05);continue
  assert r.returncode==0 and not d.get('blocked'),r.stdout
  break
 else:raise RuntimeError('Bounded wait exhausted while verifying '+e['job'])
 states={s['stage']:s for s in d['stages']} if 'stage' in d['stages'][0] else {s['name']:s for s in d['stages']}
 assert states['content']['state']=='awaiting_review',d
 assert states['media']['state']=='pending' and states['video']['state']=='pending',d
 original=p/'runs'/e['job']/'revisions/content/1/content.json';copy=o/e['content_path'];assert original.read_bytes()==copy.read_bytes();h=hashlib.sha256(original.read_bytes()).hexdigest();assert h==e['content_sha256']
 c=json.loads(original.read_text());reader=(o/e['reader_path']).read_text();assert all(s['narration'] in reader for s in c['scenes'])
 result.append({'job':e['job'],'content':'awaiting_review','revision':1,'media':'pending','video':'pending','sha256':h,'reader_matches':True})
(o/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Verified saved content and state for',len(result),'jobs')
