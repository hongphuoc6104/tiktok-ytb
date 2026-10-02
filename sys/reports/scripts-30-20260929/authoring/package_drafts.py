from pathlib import Path
import json,re,subprocess
root=Path.cwd();out=root/'reports/scripts-30-20260929';a=out/'authoring'
manifest=json.loads((out/'manifest.json').read_text())
visual_vi={r.split('|')[0]:r.split('|')[1:] for r in (a/'hinh-du-kien.txt').read_text().splitlines()}
trans={r.split('|')[0]:r.split('|')[1:] for r in (a/'transitions.txt').read_text().splitlines()}
records={}
for f in sorted(a.glob('[0-9]*.txt')):
 for block in f.read_text().split('@')[1:]:
  lines=block.strip().splitlines();w,title,objective,setting=lines[0].split('|')
  records[w]={'title':title,'objective':objective,'setting':setting,'rows':[r.split('|') for r in lines[1:]]}
# Each outline is written first. Narration is finalized before any coverage or anchors are attached.
for entry in manifest:
 w=entry['word'];j=entry['job'];rec=records[w];folder=root/'runs'/j;draft=folder/'draft'
 for cmd in ['status','next']:
  r=subprocess.run(['.venv/bin/python','pilot.py',cmd,j],capture_output=True,text=True)
  (out/f"{entry['number']:02}-{cmd}-before.json").write_text(r.stdout+r.stderr)
  if r.returncode:raise SystemExit(r.stdout+r.stderr)
 meta=json.loads((folder/'brief-current.json').read_text());b=json.loads((folder/'briefs'/f"{meta['revision']}.json").read_text())
 reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
 outline=[{'scene_id':f'SC{i:02}','purpose':row[1],'requirements':reqs[i-1],'transition':trans[w][i-1] if i<5 else 'Resolve the opening situation after explicit feedback; hold the final model long enough to read.'} for i,row in enumerate(rec['rows'],1)]
 (draft/'outline.json').write_text(json.dumps(outline,ensure_ascii=False,indent=2))
 narration=[row[3] for row in rec['rows']]
 assert len(narration)==5 and all(len(n)<=256 for n in narration)
 c={'schema_version':'3.0','brief_revision':meta['revision'],'brief_hash':meta['hash'],'topic':b['topic'],'duration':b['duration'],'style':b['style'],'required_points':[r['text'] for r in b['required_points']], 'characters':[{'id':'CH01','name':'Người que áo xanh biển nhạt','appearance':'Round white head with dark navy outline; two solid black oval eyes; exactly one torso, two minimal stick arms and two stick legs. Small expressive eyebrows and mouth variations are acceptable.','outfit':'Exactly one pale-blue short-sleeve T-shirt (#8CCFE8); simple lower-body clothing only where needed; no layered shirts.'}], 'scenes':[], 'outline':outline,'coverage':[],'claims':[],'revision_response':[],'open_questions':[]}
 for i,(row,n) in enumerate(zip(rec['rows'],narration),1):
  sid=f'SC{i:02}';iid=f'{sid}_I1';bid=f'{sid}_B1'
  quotes=re.findall(r'"([^"]+)"',n)
  label=w if i==1 else (quotes[0] if quotes else '')
  allowed=[{'text':label,'placement':'Upper third, centered, above the relevant action; clear of face and bottom caption area.','object':'Flat teaching text.'}] if label else []
  if w in ('late','early') and i in (1,3,4):
   times=['Lớp: 8:00','Đến: 8:10'] if w=='late' else ['Phim: 15:00','Đến: 14:40']
   allowed += [{'text':t,'placement':'Two small cards beside the time comparison, above caption-safe area.','object':'Time card.'} for t in times]
  pause= (6.0 if w=='early' else 5.0 if w in ['arrive','morning','afternoon','weekend','bathroom','remember','late','carry'] else 4.0) if i==4 else 0
  desc=row[2]+' '+rec['setting']+' Use the canonical mascot Character reference. One clear focal action. Maintain the listed prop positions and colors across this story. No unlisted text, logos, labels or numbers. Reserve bottom 22% for captions and outer 10% as safe margins.'
  sc={'id':sid,'title':row[0],'purpose':row[1],'action':visual_vi[w][i-1],'setting':rec['setting'],'camera':'Eye-level medium shot, with the named action and referent readable on a portrait phone frame. Hold a stable composition during retrieval.','narration':n,'requirements':reqs[i-1],'character_ids':['CH01'],'source_ids':[], 'vocabulary':[{'word':w,'meaning':rec['objective']}], 'images':[{'id':iid,'description':desc,'character_ids':['CH01'],'based_on':None,'preserve':'','change':row[2],'reason':row[1],'visible_text':allowed}], 'beats':[{'id':bid,'image_id':iid,'purpose':row[1],'anchor':{'vi':{'quote':n,'occurrence':1}},'effect':'hold' if i==4 else 'cut','focus':{'x':0.5,'y':0.4}}], 'audio_direction':{'vi':{'intent':'Invite a response, then leave the specified quiet hold; do not speak the answer in this scene.' if i==4 else 'Confirm the learner response warmly, then deliver the story payoff without rushing.' if i==5 else 'Tell the concrete situation conversationally; give the quoted English model clear space.','pronunciation_notes':'Keep standard English spelling, including I. Read embedded English as a full sentence; check the actual WAV only if audio is later authorized. These notes are direction, not verified voice control.','learner_pause_seconds':pause}}}
  c['scenes'].append(sc)
  for rid in reqs[i-1]:c['coverage'].append({'requirement_id':rid,'scene_id':sid,'quote':n})
 (draft/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
 entry.update(title=rec['title'],objective=rec['objective'],script_path=str(draft/'content.json'))
 (out/f"{entry['number']:02}-editorial.json").write_text(json.dumps({'word':w,'objective':rec['objective'],'visual_vi':visual_vi[w],'narration_units':sum(len(n.split()) for n in narration),'longest_scene_chars':max(map(len,narration)),'learner_pause_seconds':c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds'],'status':'draft_not_approved'},ensure_ascii=False,indent=2))
 print(entry['number'],w,'draft written')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
