from pathlib import Path
import json,re,hashlib
root=Path.cwd();p=root/'reports/scripts-60-20260929';a=p/'authoring';m=json.loads((p/'manifest.json').read_text());records={}
plans={r.split('|')[0]:r.split('|')[2] for r in (a/'story-plans.txt').read_text().splitlines()}
for f in sorted(a.glob('[0-9]*.txt')):
 for b in f.read_text().split('@')[1:]:
  ls=b.strip().splitlines();assert len(ls)==6,(f,ls[0]);w,title,goal,setting=ls[0].split('|');rows=[x.split('|') for x in ls[1:]];assert all(len(r)==2 for r in rows)
  records[w]=dict(title=title,goal=goal,setting=setting,rows=rows)
assert len(records)==60
roles={'doctor':('Bác sĩ','Adult clinician, simple white coat over neutral clothing, flat illustration, no detailed anatomy.'),'nurse':('Y tá','Adult male nurse in plain green work top, small badge with no readable text, flat illustration.'),'heart':('Người bạn cùng chơi','Adult friend in plain mustard-yellow top, minimal flat illustration; toy stethoscope and tapping are a game, not clinical evidence.')}
reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
# Every selected change has an explicit old/new visible state and an exact narration cue.
variants={
 ('water',3):('Bạn nhận cốc rồi rót vào bình.','Mascot nhận cốc nước, bình còn mở và chưa được rót.','Mascot nghiêng cốc rót nước vào đúng bình đang mở, giữ bàn và vị trí người bạn.'),
 ('orange',3):('Bạn bóc vỏ, tách múi ra đĩa','Mascot cầm quả cam nguyên vừa được đưa, đĩa còn trống.','Cam đã bóc, mascot đặt các múi lên đĩa; vỏ nằm gọn ở bát phụ.'),
 ('salad',2):('Bạn dùng hai thìa đảo nhẹ','Mascot đặt bát xuống, rau và phần nước trộn vẫn tách rõ.','Mascot dùng hai thìa đảo nhẹ rau trong cùng bát, nước trộn phủ đều hơn.'),
 ('sandwich',3):('Bạn đặt bánh xuống thớt','Bánh kẹp cao còn nguyên trên thớt; mascot và bạn nhìn món.','Bánh kẹp đã chia làm hai trên cùng thớt, hai đĩa nhỏ chờ bên cạnh.'),
 ('milk',3):('Bạn rót vào phần ngũ cốc','Mascot nhận hộp sữa, bát ngũ cốc còn khô.','Mascot rót sữa vào cùng bát ngũ cốc, giữ bàn và chiếc thìa đúng vị trí.'),
 ('sugar',3):('Bạn thêm vào cốc','Mascot cầm thìa nhỏ có đường phía trên cốc, lọ đúng đặt riêng ở cạnh.','Đường đã cho vào cốc, mascot đậy nắp lọ, giữ vị trí lọ còn lại.'),
 ('ice cream',3):('Điện thoại được hạ xuống','Mascot vừa nhận ra giọt kem chảy, điện thoại vẫn gần tầm mắt.','Mascot hạ điện thoại xuống bàn và lấy khăn giấy, kem giữ cùng hình và vị trí.'),
 ('pizza',5):('Còn miếng cuối, hai bạn cắt đôi.','Hai người nhìn một miếng pizza cuối còn nguyên trên đĩa.','Cùng góc máy, miếng pizza cuối đã chia làm hai trên hai đĩa nhỏ.'),
 ('sweet',1):('Sweet nghĩa là ngọt.','Mascot nếm cốc trà trước khi thêm đường, thìa đường nằm riêng cạnh cốc.','Đã thêm một ít đường, mascot nếm lại cùng cốc trà; giữ nguyên bối cảnh và người bạn.'),
 ('strong',3):('Bạn nhìn đống sách rồi lấy thêm một hộp nhỏ.','Hộp sách lớn vừa được đặt xuống, mascot và bạn cùng nhìn hộp.','Mascot đặt thêm hộp nhỏ bên hộp lớn để chia sách; đồ vật còn lại giữ nguyên.'),
 ('apple',5):('Bạn nhặt lên đem rửa','Mascot phát hiện quả táo cạnh chân ghế, chưa nhặt lên.','Mascot nhặt quả táo khỏi sàn; hai quả trên bàn đã nằm trong bát, giữ vị trí bàn ghế.'),
 ('rice',3):('Nghe vậy, bạn xếp thêm bát','Mascot và bạn nhìn nồi còn cơm, trên bàn có các bát ban đầu.','Mascot đặt thêm một bát cho người mới tới, giữ nồi và các bát cũ tại chỗ.')}
for e in m:
 w=e['word'];rec=records[w];j=e['job'];d=root/'runs'/j/'draft';meta=json.loads((d.parent/'brief-current.json').read_text());b=json.loads((d.parent/'briefs'/f"{meta['revision']}.json").read_text());assert b['scene_count']==5 and b['duration']['max_seconds']==75
 plot=plans[w].split(' → ')
 outline=[]
 for i,(n,vis) in enumerate(rec['rows'],1):
  purpose=['Establish the concrete problem and selected sense.','Use the first English model to advance the situation.','Use the second English model for the linked action or consequence.','Elicit one achievable learner response; withhold the answer.','Give explicit feedback and resolve the opening problem.'][i-1]
  outline.append(dict(scene_id=f'SC{i:02}',purpose=purpose,requirements=reqs[i-1],transition='Story continuity: '+plans[w]+'. Next visual event: '+(rec['rows'][i][1] if i<5 else 'Hold the completed result after feedback.')))
 # Outline is saved before finalized prose is connected to anchors.
 (d/'outline.json').write_text(json.dumps(outline,ensure_ascii=False,indent=2))
 counterpart,look=roles.get(w,('Người bạn hoặc người phục vụ','Adult supporting character in a plain mustard-yellow top, minimal flat illustration, solid simple eyes; no celebrity likeness. Follow the role explicitly stated in narration: friend, host, shop assistant or waiter.'))
 chars=[dict(id='CH01',name='Người que áo xanh biển nhạt',appearance='Canonical mascot with round white head, dark navy outline, two solid black oval eyes, exactly one torso and two minimal stick arms and legs. Small eyebrows, sweat and mouth-expression changes allowed under 80/20 tolerance. No realistic muscle anatomy or large anime eye whites.',outfit='Exactly one pale-blue short-sleeve T-shirt (#8CCFE8); no doubled shirts.'),dict(id='CH02',name=counterpart,appearance=look,outfit='Plain green nursing top.' if w=='nurse' else 'White clinician coat.' if w=='doctor' else 'Plain mustard-yellow top.'),dict(id='CH03',name='Người phụ thứ hai khi cảnh yêu cầu',appearance='Supporting adult, minimal flat illustration, distinct from main mascot and first companion; appears only where explicitly required. Older relative for the family call or visit scenes.',outfit='Plain lavender top; gray hair only for an elderly relative.')]
 c=dict(schema_version='3.0',brief_revision=meta['revision'],brief_hash=meta['hash'],topic=b['topic'],duration=b['duration'],style=b['style'],required_points=[x['text'] for x in b['required_points']],characters=chars,scenes=[],coverage=[],outline=outline,claims=[],revision_response=[],open_questions=[])
 for i,(n,vis) in enumerate(rec['rows'],1):
  sid=f'SC{i:02}';iid=f'{sid}_I1';purpose=outline[i-1]['purpose'];quotes=re.findall(r'"([^"]+)"',n)
  text=w if i==1 else quotes[0] if quotes else ''
  if i==4 and w in ['noodle','egg']:text={'noodle':'I like... / noodle / noodles','egg':'This is... / a egg / an egg'}[w]
  allowed=[dict(text=text,placement='Upper third in large readable type; keep clear of faces and bottom captions.',object='Flat teaching text.')] if text else []
  prompt='Depict this single concrete story moment: '+vis+' Setting: '+rec['setting']+' Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.'
  im=dict(id=iid,description=prompt,character_ids=['CH01','CH02','CH03'],based_on=None,preserve='',change=vis,reason=purpose,visible_text=allowed)
  beat=dict(id=f'{sid}_B1',image_id=iid,purpose=purpose,anchor={'vi':dict(quote=n,occurrence=1)},effect='hold' if i==4 else 'cut',focus=dict(x=.5,y=.4))
  pause=(5 if w in ['water','bread','medicine','orange','soup','egg','chocolate','candy','ice cream','tea','coffee','juice','beer','menu','restaurant','delicious'] else 4) if i==4 else 0
  sc=dict(id=sid,title=vis.split('，')[0].split(';')[0][:80],purpose=purpose,action=vis,setting=rec['setting'],camera='Medium shot or close view of the referent; choose one clear focal action. Use stable framing for learner response and locked camera for any based-on state change.',narration=n,requirements=reqs[i-1],character_ids=['CH01','CH02','CH03'],source_ids=[],vocabulary=[dict(word=w,meaning=e['gloss_vi'])],images=[im],beats=[beat],audio_direction={'vi':dict(intent='Ask and wait for the learner before revealing the answer.' if i==4 else 'Confirm the answer and finish the concrete story.' if i==5 else 'Speak to a Vietnamese beginner in a conversational tone; give each English model clear space without spelling out its letters.',pronunciation_notes='Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion.',learner_pause_seconds=pause)})
  if (w,i) in variants:
   anchor,before,after=variants[w,i];assert anchor in n,(w,i,anchor)
   im['description']=prompt.replace(vis,before,1);im['change']=before
   im2=dict(im);im2.update(id=f'{sid}_I2',description=prompt.replace(vis,after,1),based_on=iid,preserve='Keep the base camera, room, character identities, clothes, lighting, prop positions and visible text; change only the stated action or object state.',change=after,reason='Show the visible consequence after the preceding state.')
   sc['images'].append(im2);sc['beats'].append(dict(id=f'{sid}_B2',image_id=im2['id'],purpose='Reveal the action result at the matching spoken cue.',anchor={'vi':dict(quote=anchor,occurrence=1)},effect='cut',focus=dict(x=.5,y=.4)))
  c['scenes'].append(sc)
  for rid in reqs[i-1]:c['coverage'].append(dict(requirement_id=rid,scene_id=sid,quote=n))
 (d/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
 e.update(title=rec['title'],objective=rec['goal'],pause_seconds=c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds'],narration_sha256=hashlib.sha256('\n'.join(s['narration'] for s in c['scenes']).encode()).hexdigest())
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
print('60 content drafts; 300 scenes; planned before/after variants:',len(variants))
