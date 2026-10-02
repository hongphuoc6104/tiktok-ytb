from pathlib import Path
import json,re,copy,hashlib,sys
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260930';a=out/'authoring';sys.path.insert(0,str(p));from scripts.story_plan import estimates
selection=json.loads((out/'selection.json').read_text());records={}
for f in sorted(a.glob('[0-9]*.txt')):
 for block in f.read_text().split('@')[1:]:
  lines=block.strip().splitlines();assert len(lines)==6,(f,lines[0],len(lines));n,title,objective,setting,plot=lines[0].split('|');rows=[r.split('|') for r in lines[1:]];assert all(len(r)==2 for r in rows)
  records[int(n)]={'title':title,'objective':objective,'setting':setting,'plot':plot,'rows':rows}
assert len(records)==100
reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
purposes=['Show an immediate concrete need and establish the selected sense.','Use the first English model as an action within the situation.','Use the second model to clarify the same sense and advance the outcome.','Invite one manageable learner response; withhold the answer until the next scene.','Give the correct response and resolve the concrete situation.']
from visual_changes import variants
from cast_plan import apply_cast
manifest=[]
for e in selection:
 n=e['number'];rec=records[n];j=p/'runs'/e['job'];meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text());assert b['scene_count']==5
 chars=[{'id':'CH01','name':'Người que áo xanh biển nhạt','appearance':'Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.','outfit':'Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.'},{'id':'CH02','name':'Nhân vật phụ chính của tình huống','appearance':'Adult supporting person in minimal flat ink style. Use the principal companion or professional role in this script consistently across scenes. Plain mustard top with only role-required outerwear. Keep age, gender and identity consistent; never substitute for mascot.','outfit':'Plain mustard-yellow top, with only scenario-required accessories.'},{'id':'CH03','name':'Người phụ khi tình huống yêu cầu','appearance':'Adult additional person in minimal flat ink style, distinct from mascot and main companion. Only for an explicitly described attendant, professional or third guest when the companion is also present; preserve role and identity.','outfit':'Plain lavender top; scenario-required accessories only.'}]
 c={'schema_version':'3.0','brief_revision':meta['revision'],'brief_hash':meta['hash'],'topic':b['topic'],'duration':b['duration'],'style':b['style'],'required_points':[v['text'] for v in b['required_points']],'characters':chars,'scenes':[],'coverage':[],'outline':[],'claims':[],'revision_response':[],'open_questions':[]}
 for i,(narration,visual) in enumerate(rec['rows'],1):
  sid=f'SC{i:02}';iid=sid+'_I1';purpose=purposes[i-1]
  quotes=re.findall(r'"([^"]+)"',narration)
  label=(quotes[0] if narration.startswith('"') and quotes else e['word']) if i==1 else (quotes[0] if quotes else '')
  if e['word']=='wifi' and i==1:label='Wi-Fi'
  if e['word']=='t-shirt' and i==1 and not narration.startswith('"'):label='T-shirt'
  visible=[{'text':label,'placement':'Upper third, readable at phone size; separate from faces, main object and bottom subtitles.','object':'Flat teaching text.'}] if label else []
  if i==4 and quotes:
   visible=[{'text':q,'placement':'Upper third; balanced options, no answer highlight; clear of bottom subtitles.','object':'Flat teaching text.'} for q in quotes]
  if n==311 and i==3:visible.append({'text':'2','placement':'Elevator button panel, readable but secondary to lesson sentence.','object':'Floor button numeral.'})
  prompt=visual+' Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.'
  im={'id':iid,'description':prompt,'character_ids':['CH01','CH02','CH03'],'based_on':None,'preserve':'','change':visual,'reason':purpose,'visible_text':visible}
  beat={'id':sid+'_B1','image_id':iid,'purpose':purpose,'anchor':{'vi':{'quote':narration,'occurrence':1}},'effect':'hold' if i==4 else 'cut','focus':{'x':0.5,'y':0.4}}
  pause=(6 if n in {257,259,266,273,278,283,288,292,294,296,299,307,308,311,316,319,321,329,330,336,338,340} else 4 if n in {248,262,264,267,276,277,279,285,287,291,300,302,304,313,324} else 5) if i==4 else 0
  sc={'id':sid,'title':rec['title']+' — '+['Mở tình huống','Câu dùng thứ nhất','Diễn biến tiếp theo','Bạn thử nói','Đáp án và kết thúc'][i-1],'purpose':purpose,'action':visual,'setting':rec['setting'],'camera':'Medium close view with one dominant semantic action. Match the shot to the referent; lock camera and prop placement for based-on changes. Hold steady during learner response.','narration':narration,'requirements':reqs[i-1],'character_ids':['CH01','CH02','CH03'],'source_ids':[],'vocabulary':[{'word':e['word'],'meaning':e['gloss_vi']}],'images':[im],'beats':[beat],'audio_direction':{'vi':{'intent':'Ask the learner, then wait before the answer.' if i==4 else 'Confirm the response and resolve the situation.' if i==5 else 'Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible.','pronunciation_notes':'Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality.','learner_pause_seconds':pause}}}
  if n in variants and variants[n][0]==i:
   _,quote,before,after=variants[n];assert quote in narration,(n,quote)
   im['description']=prompt.replace(visual,before,1);im['change']=before
   im2=copy.deepcopy(im);im2.update(id=sid+'_I2',description=prompt.replace(visual,after,1),based_on=iid,preserve='Preserve base scene camera, background, character identities, single mascot torso and exact clothing, prop positions and visible text; change only the specified state.',change=after,reason='Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.')
   sc['images'].append(im2);be=copy.deepcopy(beat);be.update(id=sid+'_B2',image_id=im2['id'],purpose=im2['reason']);be['anchor']['vi']={'quote':quote,'occurrence':1};sc['beats'].append(be)
  # Include only described supporting roles, keeping distinct staff as the third role when the friend is also present.
  support=any(w in visual.lower() for w in ['friend','teacher','instructor','sister','farmer','driver','officer','painter','singer','performer','actor','writer','cook','worker','woman','engineer','attendant','staff','receptionist','pedestrian','local','reader','grandmother','guide','organizer','supervisor','clerk','acquaintance','companion','both','two people','travelers'])
  people=['CH01']+(['CH02'] if support else [])
  third=('friend' in visual.lower() or 'both' in visual.lower()) and any(w in visual.lower() for w in ['attendant','staff','receptionist','local adult','grandmother','arriving adult','guide','driver','clerk'])
  if third:people.append('CH03')
  sc['character_ids']=people
  for imx in sc['images']:imx['character_ids']=people
  c['scenes'].append(sc)
  c['outline'].append({'scene_id':sid,'purpose':purpose,'requirements':reqs[i-1],'transition':'Story continuity: '+rec['plot']+'. Next visible event: '+(rec['rows'][i][1] if i<5 else 'Hold the resolved result after feedback.')})
  for rid in reqs[i-1]:c['coverage'].append({'requirement_id':rid,'scene_id':sid,'quote':narration})
 apply_cast(n,c)
 d=j/'draft';d.mkdir(exist_ok=True);(d/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');(d/'outline.json').write_text(json.dumps({'outline':c['outline']},ensure_ascii=False,indent=2)+'\n')
 est=estimates(b,c);sec=round(sum(z['seconds'] for z in est['languages']['vi']['scenes']),1)
 manifest.append({**e,'title':rec['title'],'objective':rec['objective'],'plot':rec['plot'],'opening_type':'B-cau-dung-ngay' if rec['rows'][0][0].startswith('"') else 'A-tinh-huong','estimated_seconds':sec,'estimate_range_seconds':[est['languages']['vi']['min'],est['languages']['vi']['max']],'warnings':est['warnings'],'state':'draft','content_revision':None})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Packaged',len(manifest),'scripts;',len(manifest)*5,'scenes; seconds min/max/mean:',min(x['estimated_seconds'] for x in manifest),max(x['estimated_seconds'] for x in manifest),round(sum(x['estimated_seconds'] for x in manifest)/100,1))
print('warnings',[(x['number'],x['warnings']) for x in manifest if x['warnings']])
