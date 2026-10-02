from pathlib import Path
import json,re,hashlib
root=Path.cwd();p=root/'reports/scripts-50-20260929';a=p/'authoring'
manifest=json.loads((p/'manifest.json').read_text());records={}
visual=dict((r.split('|')[0],r.split('|')[1:]) for r in (a/'hinh-du-kien.txt').read_text().splitlines())
for f in sorted(a.glob('[0-9]*.txt')):
 for block in f.read_text().split('@')[1:]:
  lines=block.strip().splitlines();w,title,objective,setting=lines[0].split('|');rows=[r.split('|') for r in lines[1:]]
  assert len(rows)==5 and all(len(r)==4 and len(r[3])<=256 for r in rows)
  records[w]=dict(title=title,objective=objective,setting=setting,rows=rows)
assert len(records)==50
roles={
 'mother':('Mẹ','Adult woman, simple flat illustration, gentle expression, minimal limbs.','Plain peach short-sleeve top.'),
 'father':('Bố','Adult man, simple flat illustration, minimal limbs.','Plain sage-green short-sleeve top.'),
 'daughter':('Người con gái','Adult woman, simple flat illustration, minimal limbs; distinct from mother.','Plain lavender top.'),
 'child':('Đứa trẻ','Young child, clearly smaller than adult mascot, simple round head, minimal limbs.','Plain yellow top.'),
 'baby':('Em bé','Infant lying in a clear cot, simple flat illustration, small rounded body.','Plain cream onesie.'),
 'brother':('Anh trai','Adult male sibling, simple flat illustration, slightly taller than mascot; relation established in narration.','Plain sage top.'),
 'sister':('Em gái','Female sibling younger than mascot in story, simple flat illustration, minimal limbs.','Plain lavender top.'),
 'grandmother':('Bà','Older adult woman, short gray hair, simple flat illustration, minimal limbs.','Plain peach top.'),
 'grandfather':('Ông','Older adult man, short gray hair, simple flat illustration, minimal limbs.','Plain sage top.'),
 'uncle':('Cậu','Adult man, mother’s younger brother in this story, simple flat illustration.','Plain sage top.'),
 'aunt':('Dì','Adult woman, mother’s younger sister in this story, simple flat illustration.','Plain lavender top and loose simple scarf.'),
 'cousin':('Người anh chị em họ','Same-generation relative of mascot, mother’s sister’s child in this story; flat illustration.','Plain yellow top.'),
 'woman':('Người phụ nữ','Adult woman, simple flat illustration, dark short hair, minimal limbs.','Plain peach top.'),
 'man':('Người đàn ông','Adult man, simple flat illustration, dark short hair, minimal limbs.','Plain sage top.'),
 'friend':('Người bạn','Adult friend, simple flat illustration, minimal limbs, distinct from mascot.','Plain lavender top.'),
 'classmate':('Bạn cùng lớp','Learner of similar age to mascot, simple flat illustration.','Plain yellow top.'),
 'human':('Người minh họa phụ','Adult human teaching figure, simple flat 2D illustration, short black hair, small clearly visible nose and ears, two ordinary eyes; one torso and two arms, no realistic muscles. Hands can be shown in separate flat teaching diagrams with clearly separated digits.','Plain yellow short-sleeve top and dark simple trousers.')}
casts={'family':['mother','father'],'parent':['mother','father'],'mother':['mother'],'father':['father'],'mum':['mother'],'dad':['father'],'son':['father'],'daughter':['mother','daughter'],'child':['child'],'kid':['child'],'baby':['baby'],'brother':['brother'],'sister':['sister'],'grandparent':['grandmother','grandfather'],'grandmother':['grandmother'],'grandfather':['grandfather'],'uncle':['mother','uncle'],'aunt':['mother','aunt'],'cousin':['cousin'],'husband':['woman','man'],'wife':['man','woman'],'friend':['friend'],'best friend':['friend'],'classmate':['classmate'],'boyfriend':['woman','man'],'girlfriend':['man','woman'],'love':['mother'],'visit':['grandmother'],'body':['human'],'hair':['human'],'nose':['human'],'ear':['human'],'neck':['human']}
mc={'parent':'a parent / parents','grandparent':'a grandparent / grandparents','eye':'an eye / eyes','tooth':'tooth / teeth','leg':'leg / legs','foot':'foot / feet'}
reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
for e in manifest:
 w=e['word'];rec=records[w];j=e['job'];d=root/'runs'/j/'draft';d.mkdir(exist_ok=True)
 meta=json.loads((d.parent/'brief-current.json').read_text());b=json.loads((d.parent/'briefs'/f"{meta['revision']}.json").read_text())
 outline=[{'scene_id':f'SC{i:02}','purpose':r[1],'requirements':reqs[i-1],'transition':(f"Use the established situation ({r[0]}) to motivate the next learning action: {rec['rows'][i][1]}" if i<5 else 'After explicit learner feedback, resolve the concrete situation introduced in the opening.')} for i,r in enumerate(rec['rows'],1)]
 (d/'outline.json').write_text(json.dumps(outline,ensure_ascii=False,indent=2))
 chars=[{'id':'CH01','name':'Người que áo xanh biển nhạt','appearance':'Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso, two minimal stick arms and two stick legs. Small expressive eyebrows and changing mouth curves are allowed. Do not add hair, realistic muscles, detailed fingers, a realistic nose or ears to this mascot.','outfit':'Exactly one pale-blue short-sleeve T-shirt (#8CCFE8); simple lower clothing where needed. No stacked shirts.'}]
 for k,role in enumerate(casts.get(w,[]),2):
  name,look,outfit=roles[role];chars.append(dict(id=f'CH{k:02}',name=name,appearance=look,outfit=outfit))
 char_ids=[x['id'] for x in chars]
 c=dict(schema_version='3.0',brief_revision=meta['revision'],brief_hash=meta['hash'],topic=b['topic'],duration=b['duration'],style=b['style'],required_points=[x['text'] for x in b['required_points']],characters=chars,scenes=[],outline=outline,coverage=[],claims=[],revision_response=[],open_questions=[])
 for i,row in enumerate(rec['rows'],1):
  title,purpose,desc,n=row;sid=f'SC{i:02}';im=f'{sid}_I1';bid=f'{sid}_B1'
  quotes=re.findall(r'"([^"]+)"',n)
  screen=w if i==1 else (mc[w] if i==4 and w in mc else quotes[0] if quotes else '')
  text=[dict(text=screen,placement='Upper third; clear of faces, gesture target and bottom caption area.',object='Flat teaching text.')] if screen else []
  pause=(5 if w in ['best friend','get dressed','get ready','brother','sister','grandparent','parent','tooth','foot','ear'] else 4) if i==4 else 0
  # Teaching diagrams are separate objects, never anatomical changes to the canonical mascot.
  direction=desc+' '+rec['setting']+' Show only the people explicitly described in this frame. Keep family relations and distinct clothing consistent across the story. For mascot, attach canonical Character reference; never replace the mascot with the secondary human teaching figure. Diagrams on cards are separate flat educational objects. No extra text, labels or numbers outside visible_text. Leave bottom 22% clear for captions and 10% outer margins.'
  sc=dict(id=sid,title=title,purpose=purpose,action=visual[w][i-1],setting=rec['setting'],camera='Eye-level medium shot; use a closer view when the named body part or small prop is the learning focus. Keep that referent large and unambiguous on a portrait phone frame.',narration=n,requirements=reqs[i-1],character_ids=char_ids,source_ids=[],vocabulary=[dict(word=w,meaning=e['gloss_vi'])],images=[dict(id=im,description=direction,character_ids=char_ids,based_on=None,preserve='',change=desc,reason=purpose,visible_text=text)],beats=[dict(id=bid,image_id=im,purpose=purpose,anchor={'vi':dict(quote=n,occurrence=1)},effect='hold' if i==4 else 'cut',focus=dict(x=.5,y=.4))],audio_direction={'vi':dict(intent='Ask the concrete retrieval question; leave the full quiet hold before the next scene gives feedback.' if i==4 else 'Confirm the answer, then resolve the opening situation warmly.' if i==5 else 'Speak conversationally, clarify the relation or action, and give the English example room to be heard as a full sentence.',pronunciation_notes='Keep standard spelling and read I normally in English. Embedded English and plural endings must be checked by listening only if media is later authorized. No pronunciation claim has been verified from audio.',learner_pause_seconds=pause)})
  c['scenes'].append(sc)
  for rid in reqs[i-1]:c['coverage'].append(dict(requirement_id=rid,scene_id=sid,quote=n))
 (d/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
 e.update(title=rec['title'],objective=rec['objective'],pause_seconds=c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds'],draft_path=str(d/'content.json'),source_sha256=hashlib.sha256('\n'.join(r[3] for r in rec['rows']).encode()).hexdigest())
(p/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Đã tạo 50 bản nháp content-v3, 250 cảnh; lời dẫn chốt trước khi đặt neo.')
