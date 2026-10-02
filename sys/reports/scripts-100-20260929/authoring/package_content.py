from pathlib import Path
import json,re,copy,hashlib,sys
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260929';a=out/'authoring';sys.path.insert(0,str(p));from scripts.story_plan import estimates
selection=json.loads((out/'selection.json').read_text());records={}
for f in sorted(a.glob('[0-9]*.txt')):
 for block in f.read_text().split('@')[1:]:
  lines=block.strip().splitlines();assert len(lines)==6,(f,lines[0],len(lines));n,title,objective,setting,plot=lines[0].split('|');rows=[r.split('|') for r in lines[1:]];assert all(len(r)==2 for r in rows)
  records[int(n)]={'title':title,'objective':objective,'setting':setting,'plot':plot,'rows':rows}
assert len(records)==100
reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
purposes=['Show an immediate concrete need and establish the selected sense.','Use the first English model as an action within the situation.','Use the second model to clarify the same sense and advance the outcome.','Invite one manageable learner response; withhold the answer until the next scene.','Give the correct response and resolve the concrete situation.']
# Explicit before/after plans for state changes. Quotes are attached after prose is frozen.
variants={
143:(3,'Lần này chiếc nắp vừa miệng nồi','The lid is just above the deep pot; keep pan separate.','The matching lid now rests squarely on the deep pot.'),
148:(2,'Người bạn kéo chiếc còn lại khỏi bao','The second chopstick remains partly inside its plain sleeve beside the first.','The friend has pulled the second chopstick free and laid it beside the first.'),
149:(3,'Bạn đặt bát xuống rồi mới đổ ngũ cốc','The deep bowl is empty on the table, cereal box held upright.','Cereal is being poured into the same bowl on the table.'),
150:(2,'Người bạn nhìn theo tay bạn rồi đặt bánh xuống','The friend holds the cake just above the empty plate.','The cake now rests on the plate; the friend has released it.'),
153:(3,'Nhận đúng màu rồi, bạn mới cho vào túi','The mascot holds the green bottle outside their open bag.','The green bottle is inside the mascot bag; the friend retains the blue one.'),
156:(2,'Người bạn gật đầu và mở rộng cửa','The friend stands at a slightly open apartment door.','The same door is open wider and the friend invites the mascot inside.'),
161:(2,'Người bạn kéo','', ''),
162:(2,'Người bạn kéo cánh cửa khép lại','The window is open; the friend reaches for its handle and paper lies on floor.','The window is closed; the mascot has retrieved the same paper.'),
163:(3,'Bạn đặt sách vào góc bàn vừa trống','The picture is mounted on the wall, table corner still empty and books held by mascot.','The books now sit on the cleared table corner below the picture.'),
164:(3,'Cả hai lấy cây lau và khăn','The spill remains visible; both people have cleaning tools ready.','The mascot mops the small spill while the friend holds the cloth clear of the wet area.'),
171:(2,'Người bạn bật công tắc','The desk lamp is off with the open book beneath it.','The same lamp is on and its light falls on the open book, not the face.'),
173:(3,'rồi bật lại khi đã đặt vững','The repositioned fan is off, standing stably facing the mascot.','The same fan is on, facing the reading chair; all hands are clear of the grille.'),
175:(2,'Người bạn giữ hai mép khung, chỉnh một chút','The framed landscape is tilted on the wall; friend holds both frame edges.','The picture is straight on the same mount; friend releases hands.'),
176:(3,'người kia đặt mái lên','The paper house walls stand with the roof held just above them.','The roof is seated on the model walls while the friend steadies the base.'),
179:(2,'Bạn lấy đồ từ giỏ được chỉ','Clean folded clothes sit in a basket beside the separate rumpled laundry.','The mascot folds a clean spare garment from the indicated basket; own shirt unchanged.'),
183:(2,'Người bạn quay lại, nhấc áo khỏi móc','The jacket is still on the hook; friend reaches for it.','The friend carries the jacket over an arm and the hook is empty.'),
191:(3,'Bạn xếp chúng chồng lên nhau','Two matching socks lie side by side on the table.','The same two socks are neatly stacked as a pair.'),
192:(2,'Người bạn kéo ghế ra nhẹ','One shoe is partly hidden beneath the entry bench.','The bench has shifted slightly and the missing shoe is fully visible.'),
195:(2,'bạn liền để chiếc ấy lại','Mascot is reaching toward the long-handled bag as friend points to it.','Mascot withdraws hand and leaves the long-handled bag in front of the friend.'),
196:(2,'Người bạn quay lại, nhấc túi lên','The backpack hangs on the chair back.','Friend holds the backpack and checks its zipper; chair back is empty.'),
198:(2,'người ấy chạm tay vào rồi bật cười','Friend wears glasses on top of head, searching around the desk.','Friend touches the glasses on top of head with a surprised smile; mascot unchanged.'),
202:(2,'Người bạn nhấc mũ lên','Friend holds the hat in hand, ready to put it on.','Friend has placed the same hat on head and adjusts its brim.'),
203:(3,'Cởi xong, người ấy xếp giày thành đôi','Friend sits at the door after removing shoes; both shoes lie separately nearby.','The removed shoes are neatly placed as a matching pair beside the door.'),
204:(5,'Thay xong trong phòng riêng','Friend is behind the closed private-room door; mascot waits fully clothed outside.','Friend has returned fully dressed in dry mustard top, holding wet top folded.'),
205:(2,'Người bán từ trong quay ra','The shop door is partly open, clerk is farther behind the counter.','Clerk has opened the shop door wider and invites both visitors inside.'),
217:(2,'Người bán xoay thẻ ra ngoài','Selected bottle tag shows its blank reverse.','Tag is turned outward by clerk; do not invent readable prices or extra text.'),
225:(3,'Người bạn quay lại','An adult learner group leaves one clear empty place in the photo arrangement.','Friend joins the empty place so all adult learners are in the group.'),
233:(2,'Bạn cất bút vào hộp','Mascot holds a pen above the open case at the classroom desk.','Pen is in the closed case; mascot begins to stand for break.'),
239:(3,'Bạn tự gấp lại một lần','Mascot holds an unfolded sheet while friend keeps hands away.','Mascot has independently made the demonstrated first fold, friend watching.'),
240:(2,'Bạn làm theo trên tờ của mình','Friend demonstrates the first fold, mascot sheet remains flat.','Mascot reproduces the fold on a separate sheet; friend keeps the sample.'),
}
variants[161]=(2,'Người bạn mở cửa','The door is closed and mascot waits with the box outside its swing.','Friend has opened the door; mascot still holds the box and now has a clear path.')
# Use a quote present in the already-finalized narration.
variants[161]=(2,'Bạn đứng lùi một chút',variants[161][2],variants[161][3])
manifest=[]
for e in selection:
 n=e['number'];rec=records[n];j=p/'runs'/e['job'];meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text());assert b['scene_count']==5
 chars=[{'id':'CH01','name':'Người que áo xanh biển nhạt','appearance':'Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.','outfit':'Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.'},{'id':'CH02','name':'Người bạn hoặc người hỗ trợ trong tình huống','appearance':'Adult supporting person in minimal flat ink style. Maintain the role and identity specified by the scene across the whole story. Plain mustard top; may wear the explicitly described extra garment for clothing lessons.','outfit':'Plain mustard-yellow top, with only scenario-required accessories.'},{'id':'CH03','name':'Người phụ khi tình huống yêu cầu','appearance':'Adult supporting person, distinct from the main mascot and first companion, minimal flat ink style; appears only when explicitly specified.','outfit':'Plain lavender top; scenario-required accessories only.'}]
 c={'schema_version':'3.0','brief_revision':meta['revision'],'brief_hash':meta['hash'],'topic':b['topic'],'duration':b['duration'],'style':b['style'],'required_points':[v['text'] for v in b['required_points']],'characters':chars,'scenes':[],'coverage':[],'outline':[],'claims':[],'revision_response':[],'open_questions':[]}
 for i,(narration,visual) in enumerate(rec['rows'],1):
  sid=f'SC{i:02}';iid=sid+'_I1';purpose=purposes[i-1]
  quotes=re.findall(r'"([^"]+)"',narration)
  label=(quotes[0] if narration.startswith('"') and quotes else e['word']) if i==1 else (quotes[0] if quotes else '')
  if e['word']=='t-shirt' and i==1 and not narration.startswith('"'):label='T-shirt'
  visible=[{'text':label,'placement':'Upper third, readable at phone size; separate from faces, main object and bottom subtitles.','object':'Flat teaching text.'}] if label else []
  prompt=visual+' Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.'
  im={'id':iid,'description':prompt,'character_ids':['CH01','CH02','CH03'],'based_on':None,'preserve':'','change':visual,'reason':purpose,'visible_text':visible}
  beat={'id':sid+'_B1','image_id':iid,'purpose':purpose,'anchor':{'vi':{'quote':narration,'occurrence':1}},'effect':'hold' if i==4 else 'cut','focus':{'x':0.5,'y':0.4}}
  pause=5 if i==4 else 0
  sc={'id':sid,'title':rec['title']+' — '+['Mở tình huống','Câu dùng thứ nhất','Diễn biến tiếp theo','Bạn thử nói','Đáp án và kết thúc'][i-1],'purpose':purpose,'action':visual,'setting':rec['setting'],'camera':'Medium close view with one dominant semantic action. Match the shot to the referent; lock camera and prop placement for based-on changes. Hold steady during learner response.','narration':narration,'requirements':reqs[i-1],'character_ids':['CH01','CH02','CH03'],'source_ids':[],'vocabulary':[{'word':e['word'],'meaning':e['gloss_vi']}],'images':[im],'beats':[beat],'audio_direction':{'vi':{'intent':'Ask the learner, then wait before the answer.' if i==4 else 'Confirm the response and resolve the situation.' if i==5 else 'Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible.','pronunciation_notes':'Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality.','learner_pause_seconds':pause}}}
  if n in variants and variants[n][0]==i:
   _,quote,before,after=variants[n];assert quote in narration,(n,quote)
   im['description']=prompt.replace(visual,before,1);im['change']=before
   im2=copy.deepcopy(im);im2.update(id=sid+'_I2',description=prompt.replace(visual,after,1),based_on=iid,preserve='Preserve base scene camera, background, character identities, single mascot torso and exact clothing, prop positions and visible text; change only the specified state.',change=after,reason='Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.')
   sc['images'].append(im2);be=copy.deepcopy(beat);be.update(id=sid+'_B2',image_id=im2['id'],purpose=im2['reason']);be['anchor']['vi']={'quote':quote,'occurrence':1};sc['beats'].append(be)
  c['scenes'].append(sc)
  c['outline'].append({'scene_id':sid,'purpose':purpose,'requirements':reqs[i-1],'transition':'Story continuity: '+rec['plot']+'. Next visible event: '+(rec['rows'][i][1] if i<5 else 'Hold the resolved result after feedback.')})
  for rid in reqs[i-1]:c['coverage'].append({'requirement_id':rid,'scene_id':sid,'quote':narration})
 d=j/'draft';d.mkdir(exist_ok=True);(d/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');(d/'outline.json').write_text(json.dumps({'outline':c['outline']},ensure_ascii=False,indent=2)+'\n')
 est=estimates(b,c);sec=round(sum(z['seconds'] for z in est['languages']['vi']['scenes']),1)
 manifest.append({**e,'title':rec['title'],'objective':rec['objective'],'plot':rec['plot'],'opening_type':'B-cau-dung-ngay' if rec['rows'][0][0].startswith('"') else 'A-tinh-huong','estimated_seconds':sec,'estimate_range_seconds':[est['languages']['vi']['min'],est['languages']['vi']['max']],'warnings':est['warnings'],'state':'draft','content_revision':None})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Packaged',len(manifest),'scripts;',len(manifest)*5,'scenes; seconds min/max/mean:',min(x['estimated_seconds'] for x in manifest),max(x['estimated_seconds'] for x in manifest),round(sum(x['estimated_seconds'] for x in manifest)/100,1))
print('warnings',[(x['number'],x['warnings']) for x in manifest if x['warnings']])
