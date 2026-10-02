from pathlib import Path
import json,subprocess,hashlib
p=Path(__file__).resolve().parents[3];o=p/'reports/scripts-100-20260930';m=json.loads((o/'manifest.json').read_text());result=[]
for e in m:
 r=subprocess.run([str(p/'.venv/bin/python'),'pilot.py','status',e['job']],cwd=p,capture_output=True,text=True);assert r.returncode==0,r.stdout;d=json.loads(r.stdout)
 states={s['stage']:s for s in d['stages']} if 'stage' in d['stages'][0] else {s['name']:s for s in d['stages']}
 assert states['content']['state']=='awaiting_review',d
 assert states['media']['state']=='pending' and states['video']['state']=='pending',d
 original=p/'runs'/e['job']/'revisions/content/1/content.json';copy=o/e['content_path'];assert original.read_bytes()==copy.read_bytes();h=hashlib.sha256(original.read_bytes()).hexdigest();assert h==e['content_sha256']
 c=json.loads(original.read_text());reader=(o/e['reader_path']).read_text();assert all(s['narration'] in reader for s in c['scenes'])
 result.append({'job':e['job'],'content':'awaiting_review','revision':1,'media':'pending','video':'pending','sha256':h,'reader_matches':True})
(o/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Verified saved content and state for',len(result),'jobs')
