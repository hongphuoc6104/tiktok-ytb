from pathlib import Path
import json,hashlib,subprocess,time,re
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/opening-audit-A1-331-20261001'
m=json.loads((OUT/'manifest.json').read_text());base={x['number']:x for x in json.loads((OUT/'baseline.json').read_text())};rows=[]
for e in m:
 n=e['number'];j=e['job'];rev=e['content_revision'];assert rev in [1,2]
 for attempt in range(1200):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py','status',j],cwd=ROOT,capture_output=True,text=True);s=json.loads(r.stdout)
  if s.get('blocked')=='Another operation is running':
   if attempt%120==0:print('WAIT STATUS',n,flush=True)
   time.sleep(.5);continue
  assert r.returncode==0 and not s.get('blocked'),s;break
 else:raise RuntimeError('Bounded status wait exhausted '+j)
 assert s['mode']=='review' and s['stages'][0]['state']=='awaiting_review' and s['stages'][0]['revision']==rev,s
 assert all(x['state']=='pending' and x['revision'] is None for x in s['stages'][1:]),s
 folder=ROOT/'runs'/j;p=folder/f'revisions/content/{rev}/content.json';c=json.loads(p.read_text());draft=json.loads((folder/'draft/content.json').read_text());assert c==draft,n
 assert json.loads((folder/'draft/checks.json').read_text())['passed'] is True,n
 assert c['scenes'][1:]==base[n]['content']['scenes'][1:],n
 assert hashlib.sha256((folder/'revisions/content/1/content.json').read_bytes()).hexdigest()==base[n]['saved_r1_sha256'],n
 assert (OUT/e['content_path']).read_bytes()==p.read_bytes(),n
 assert (OUT/e['review_copy']).read_bytes()==Path(e['review']).read_bytes(),n
 reader=(OUT/e['reader_path']).read_text();assert all(sc['narration'] in reader for sc in c['scenes']),n
 for sc in c['scenes']:
  for beat in sc['beats']:assert beat['anchor']['vi']['quote'] in sc['narration'],n
 for cv in c['coverage']:assert cv['quote'] in next(sc['narration'] for sc in c['scenes'] if sc['id']==cv['scene_id']),n
 rows.append({'number':n,'job':j,'current_revision':rev,'review_state':'awaiting_review','mode':'review','media_video':'pending','draft_and_export_match_saved_content':True,'reader_literal':True,'r1_preserved':True,'downstream_scenes_unchanged':True,'anchors_coverage_literal':True,'content_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (OUT/'final-verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 if len(rows)%50==0:print('VERIFIED',len(rows),flush=True)
print('FINAL VERIFIED',len(rows),'scripts; saved revisions and readers literal, r1 unchanged, review mode, no media/video revisions',flush=True)
