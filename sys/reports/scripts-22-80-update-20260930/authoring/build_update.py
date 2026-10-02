"""Content authoring for this request only; no protected implementation edits."""
import copy
import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SYS = ROOT / 'sys'
OUT = Path(__file__).resolve().parents[1]
PYTHON = SYS / '.venv/bin/python'
SCOPE = json.loads((OUT / 'update-scope.json').read_text())
RECORDS = json.loads((OUT / 'authoring/original-records.json').read_text())
EDITS = json.loads((OUT / 'authoring/edits.json').read_text())
PREFLIGHT = {x['job']: x for x in json.loads((OUT / 'preflight-after-adopt.json').read_text())}
NOTE = 'Cập nhật theo yêu cầu người dùng: mỗi bài một nghĩa, thời lượng hướng đến 60/80/100 giây; sửa lời dẫn, tình huống, hình chứng minh nghĩa, khoảng chờ thực hành và neo. Người dùng đã chấp nhận hướng chỉnh trong cuộc trò chuyện; bản lời dẫn đầy đủ mới cần được đối chiếu theo revision.'

MASCOT = dict(id='CH01', name='Người que áo xanh biển nhạt',
 appearance='Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso, two minimal stick arms and two stick legs. Subtle expressive eyebrows, small worry lines, sweat drops and changing mouth curves are acceptable. No realistic muscles, detailed fingers, added hair, realistic nose or ears, duplicate torso or anime eyes.',
 outfit='Exactly one pale-blue short-sleeve T-shirt (#8CCFE8). Keep this shirt throughout; simple trousers or shorts can change for the story. No stacked shirts.')

SUPPORT = {
 'remember': 'A small independent comparison card shows a birthday cake and the same blue cup, linking an already-known birthday and favorite color to the chosen gift. No new person or calendar date.',
 'carry': 'Show the same bag at a shop counter, then supported in a minimal hand while walking along the sidewalk. Use two separate small panels so moving the object is explicit. A resting bag stays on a bench, never floats.',
 'late': 'Use two separate time cards for this class: scheduled 8:00 and arrival 8:10. A further unlabeled pictogram compares arrival before a later scheduled start; do not suggest the clock time alone means late.',
 'early': 'Show the same classroom schedule 8:00 and arrival 7:50. A neutral afternoon appointment pictogram shows an earlier arrival than its start without extra digits. Both comparisons establish earlier than the appointment, not morning.',
 'done': 'Show the same paper-house task list: cutting and folding checked, gluing unchecked before completion; final finished state has all three check marks. No letters except permitted teaching text.',
 'free': 'Show a planner with a filled morning block and an empty afternoon block. A small separate card marks availability only after the agreed afternoon time by a blank-to-open interval. No prices or currency.',
 'get dressed': 'Compare lower-body clothing before and after: pajama-pattern trousers on the seated mascot, then daytime shorts. Preserve the one canonical blue shirt in both. A separate still-visible key on the hook shows dressing does not complete all preparation. No undressing or duplicate torso.',
 'get ready': 'Show the dressed mascot beside a bag that still lacks the bottle and keys; then the bottle packed and keys held in a separate panel. Preparation proceeds before readiness. No unsupported animated action.',
 'parent': 'Show exactly one parent signing the single line. A separate simple comparison card presents either declared mother or declared father as one signer, then both parents together for plural. Never duplicate a person in the actual room.',
 'mum': 'Keep the declared mother identifiable in a homecoming shot and a separate telling-a-friend shot. Make speaker direction clear. No claim that this is a different person from mother.',
 'dad': 'Show the declared father addressed by the mascot with the closed lunchbox, then the same father releasing the side latch. A separate explanatory card links direct address to talking about the same father.',
 'son': 'Show the declared father as speaker and adult mascot as his son. A separate relation card links the same father to the mascot; make adult status explicit. No age inferred from height alone.',
 'daughter': 'Show the declared mother as speaker and the declared adult daughter beside the drawing; the mascot is the listener. Use a distinct relation card from mother to daughter, not an age-only portrait.',
 'child': 'Keep the declared young child and appropriately low chair visible. A small neutral age-comparison card distinguishes a young child from an adult without adding a second real child or teaching the parent-child sense.',
 'kid': 'Show the same declared child running for the ball and then standing still after returning it. Both panels depict a child; speed does not determine the noun. Keep friendly expression, no mocking label.',
 'brother': 'Show an explicit sibling relation card between mascot and declared male sibling. Use an unlabeled age-order arrow, distinct from a height comparison. An illustrative height reversal does not change the declared older sibling relation.',
 'sister': 'Show an explicit sibling relation card between mascot and declared younger female sibling. Use an age-order arrow, not height or craft skill, to establish younger.',
 'grandparent': 'Show a card containing only the declared grandmother, then a card containing only the declared grandfather, then a separate group card containing both. A two-generation link through a generic parent silhouette establishes the family relation.',
 'grandmother': 'Show the declared grandmother and mascot by the baking table. An independent relation card uses a generic parent silhouette between mascot and grandmother; her family position, not baking or gray hair, establishes the relation.',
 'grandfather': 'Show the declared grandfather and mascot with the album. An independent relation card uses a generic parent silhouette between mascot and grandfather. The old album portrait is the same grandfather when younger, not another relative.',
 'uncle': 'Build a relation card using declared mascot, mother and her younger brother. Highlight mascot-to-mother first, then mother-to-brother. In a separate neutral comparison card, a father silhouette links to his brother. Keep the actual visitor the same maternal uncle. No other real visitor.',
 'aunt': 'Build a relation card using declared mascot, mother and her younger sister. Highlight mascot-to-mother first, then mother-to-sister. A separate neutral comparison card links a father silhouette to his sister. Keep the actual visitor the maternal aunt; scarves do not define relations.',
 'cousin': 'Use four declared people on a flat relation card: mascot and mother in the left branch; mother’s sister and her child in the right branch. A sibling link joins the two mothers. Highlight each mother-to-child branch before connecting the two cousins. Real scene remains the same family gathering.',
 'husband': 'Show the declared married woman speaking to mascot and indicating her declared husband. A simple separate relationship card identifies the woman as speaker; two cups alone are not marriage evidence. No assumption from rings or gestures alone.',
 'wife': 'Show the declared married man speaking to mascot and indicating his declared wife. A separate relationship card marks the speaking man and the indicated woman, distinct from the mascot attendant.',
 'best friend': 'Keep the same close friend and completed creative project. A neutral friendship card distinguishes the selected close friend from a generic group of friends without ranking human worth or requiring daily calls.',
 'classmate': 'Show a school-courtyard context with one anonymous distant learner, then an independent classroom composition with mascot and declared classmate at desks facing the same board. This supports same school versus same class, not friendship intensity.',
 'boyfriend': 'Show the declared woman as speaker and her declared male romantic partner as referent, with mascot hosting. A simple relationship card establishes the stated romantic relation; never use gender, seating or a photo alone as proof.',
 'girlfriend': 'Show the declared man as speaker and his declared female romantic partner as referent, with mascot hosting. A simple relationship card establishes the stated romantic relation independently of the saved chair.',
 'hate': 'Show the same alarm and rest-day icon, with strongly displeased but restrained mascot expression. Keep the alarm intact. The second panel shows switching its rest-day setting off rather than damaging it.',
 'tooth': 'Use separate flat educational diagrams with one tooth highlighted, then several teeth highlighted. Do not add detailed teeth to the mascot. The plural card must preserve a clear one-versus-many comparison.',
 'arm': 'Use a flat diagram highlighting the complete arm from shoulder through elbow to wrist; hand is a different muted color. Compare raised arm with opening only the hand on a separate diagram, not extra mascot anatomy.',
 'hand': 'Use a flat human hand diagram with coin in closed palm, then opened palm revealing it. Keep palm and fingers readable, distinguish the long arm region. Mascot minimal hands remain unchanged.',
 'leg': 'Use a flat lower-body diagram highlighting hip-to-ankle legs and a muted foot below each ankle. A separate pair of trousers is clearly an object beside the body diagram, not the referent of the noun.',
 'foot': 'Use flat diagrams of one foot below the ankle, then two feet resting on the floor in a seated pose. Keep the long leg region muted. A shoe fits the foot, never the whole leg.'
}

def load(p): return json.loads(p.read_text())
def save(p, x):
 p.parent.mkdir(parents=True, exist_ok=True)
 p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')

def cli(action, job, *args):
 result = subprocess.run([str(PYTHON), str(SYS/'pilot.py'), action, job, *args], cwd=SYS, capture_output=True, text=True)
 try: value = json.loads(result.stdout)
 except ValueError: value = {'stdout':result.stdout,'stderr':result.stderr}
 save(OUT/'operations'/f'{job}-{action}.json', value)
 if result.returncode or value.get('blocked') or (action=='check-draft' and not value.get('passed')):
  raise RuntimeError(f'{action} {job}: {result.stdout} {result.stderr}')
 return value

def records_for(word):
 rec = copy.deepcopy(RECORDS[word])
 rec['title'] = EDITS['titles'][word]
 if word == 'get dressed':
  rec['rows'][0][3] = rec['rows'][0][3].replace('mặc quần áo để sẵn sàng','mặc quần áo')
 if word == 'early':
  rec['setting'] = 'Classroom entrance with schedule 8:00 and mascot arrival 7:50; canonical mascot carries a schoolbag; closed door opens at class time.'
  replacements = [('phòng chiếu','lớp học'),('suất phim','buổi học'),('phim','buổi học'),('Phim','Buổi học'),('rạp','lớp'),('vé','lịch học'),('mười lăm giờ','tám giờ'),('mười bốn giờ bốn mươi','bảy giờ năm mươi'),('hai mươi phút','mười phút'),('15:00','8:00'),('14:40','7:50'),('cinema','classroom'),('movie','class'),('screening','class'),('ticket','schoolbag'),('tickets','schoolbags')]
  for row in rec['rows']:
   for old,new in replacements:
    row[2]=row[2].replace(old,new); row[3]=row[3].replace(old,new)
  rec['rows'][0][3] = 'Buổi học bắt đầu lúc tám giờ, bạn tới lúc bảy giờ năm mươi. Cửa còn đóng vì chưa tới giờ. Early nghĩa là sớm hơn giờ dự kiến. Bạn có mặt trước mười phút, nên còn thời gian ngồi chờ.'
  rec['rows'][1][3] = 'Bạn nhìn lại lịch và nói: "I’m early." Tôi đến sớm rồi. Trong câu này, early nói thời điểm bạn tới so với giờ hẹn. Nó không chỉ có nghĩa là trời còn sớm.'
  rec['rows'][2][3] = 'Bạn kể rõ hơn: "I’m early for class." Tôi đến lớp sớm. For class cho biết buổi học mà bạn tới trước giờ. Bạn ngồi chờ bên cửa, chưa cần vội mở một cánh cửa còn khóa.'
  rec['rows'][3][3] = 'Lớp bắt đầu tám giờ, bạn tới bảy giờ năm mươi. Hãy điền tính từ vừa học vào câu "I’m..." rồi nói cả câu. Nghĩ tới hai mốc giờ trước khi trả lời nhé.'
  rec['rows'][4][3] = '"I’m early." Từ cần điền là early. Bạn tới trước giờ hẹn nên đến sớm. Tới tám giờ, cửa mở và bạn vào lớp. Khoảng chờ lúc nãy giúp bạn xem lại đồ dùng trước khi buổi học bắt đầu.'
 if word=='classmate':
  rec['rows'][0][3] = 'Ở sân trường bạn gặp một người học lớp khác. Vào lớp mình, bạn mở hộp bút thấy trống trơn; người ngồi cạnh đưa sang một chiếc. Classmate là bạn cùng lớp. Hai bạn học chung lớp nên có từ này để giới thiệu.'
 if word=='aunt':
  rec['rows'][0][3] = 'Mẹ giới thiệu người vừa tới là em gái của mẹ. Với bạn, người ấy là aunt; trong câu chuyện này tiếng Việt gọi là dì. Hai người có chiếc khăn giống nhau, nhưng lời giới thiệu cho biết rõ quan hệ.'
  rec['rows'][0][2] = 'Mascot welcomes mother in peach top and her younger sister in lavender top; mother explicitly introduces her sister using a clear relation card. Similar scarves are incidental props.'
 if word=='boyfriend':
  rec['rows'][2][3] = rec['rows'][2][3].replace('My boyfriend likes photos.','My boyfriend likes taking photos.').replace('Bạn trai tôi thích ảnh.','Bạn trai tôi thích chụp ảnh.')
 if word=='cook':
  rec['rows'][2][3] = rec['rows'][2][3].replace('Cook nói hành động làm món ăn chín và sẵn sàng','Trong món mì này, cook nói hành động nấu nguyên liệu thành món ăn')
 return rec

def provisional_brief(item, rec):
 jobdir=SYS/'runs'/item['job']; meta=load(jobdir/'brief-current.json'); b=load(jobdir/'briefs'/f"{meta['revision']}.json")
 old=b['topic']; word=item['word']; gloss=EDITS['glosses'].get(word,item.get('gloss_vi',''))
 if not gloss:
  bank=[loadline for line in (SYS/'vocab/bank.jsonl').read_text().splitlines() if (loadline:=json.loads(line))['word']==word]
  gloss=bank[0]['gloss_vi']
 b['topic']=f'Học từ vựng tiếng Anh {word} — {gloss} qua câu chuyện “{rec["title"]}”'
 b['goal']=f'Người xem nhận ra nghĩa “{gloss}” của {word} trong tình huống, dùng đúng từ trong câu mẫu và hoàn thành lượt nhớ lại có phản hồi.'
 b['duration']={k:v for k,v in item['requested_duration'].items() if k!='target_seconds'}
 b['required_points']=[{'id':'R1','text':f'Mở bằng tình huống cụ thể dẫn tới {word}; payoff giải quyết tình huống ấy.'}, {'id':'R2','text':f'Chỉ dạy nghĩa “{gloss}” của {word}; hình và lời giải thích làm rõ hành động, bộ phận hoặc quan hệ, gỡ điểm dễ nhầm khi cần.'}, {'id':'R3','text':f'Hai câu ví dụ dùng {word} chính xác, nối trong cùng câu chuyện hoặc một đối chiếu có mục đích.'}, {'id':'R4','text':f'Một lượt nhớ lại hoặc dùng {word}, có khoảng yên lặng thật và phản hồi; giữ đáp án sau lượt trả lời.'}]
 p=b['planning']; p['success_criteria']=[f'Nhận ra {word} với nghĩa “{gloss}” qua hình và câu chuyện.', 'Dùng từ hoặc cụm từ trong một câu mẫu đúng người nói và ngữ cảnh.', 'Thử trả lời trong khoảng chờ, rồi đối chiếu đáp án; hiệu quả học chưa đo với học viên thật.']
 p['avoid']=list(dict.fromkeys(p['avoid']+['Không dạy các nghĩa khác như mục tiêu bổ sung.','Không thêm lời lặp hoặc khoảng yên lặng vô cớ để kéo dài video.','Không hiển thị đáp án đầy đủ trong lượt nhớ lại.']))
 p['domain_requirements']=[x for x in p['domain_requirements'] if not x.startswith('Từ khoá duy nhất của video:')]
 p['domain_requirements'] += [f'Từ khoá duy nhất của video: {word}; nghĩa chọn: “{gloss}”.',f'Thời lượng hướng đến {item["requested_duration"]["target_seconds"]} giây, gồm khoảng chờ; đo lại bằng WAV thật, không đổi tốc độ giọng để ép thời lượng.']
 p['assumptions']=list(dict.fromkeys(p['assumptions']+['Bản dọc 9:16 lời dẫn Việt và câu mẫu Anh; không tự thêm narration_en độc lập.', 'Người dùng đã chấp nhận hướng chỉnh ý tưởng; lời dẫn và revision mới được bàn giao để đối chiếu, chưa tự suy ra quyết định duyệt.']))
 return b,gloss

def skeleton(item,rec,b,gloss,meta):
 word=item['word']; source=SYS/'runs'/item['job']/'draft/content.json'
 if source.exists(): c=load(source)
 elif item['number']>=31: c=load(SYS/'reports/scripts-50-20260929/content'/f'{item["number"]:02}-{word.replace(" ","-")}.json')
 else: c={'schema_version':'3.0','characters':[copy.deepcopy(MASCOT)],'claims':[],'revision_response':[],'open_questions':[]}
 c['characters'][0]=copy.deepcopy(MASCOT)
 if word=='cousin':
  c['characters'] += [dict(id='CH03',name='Mẹ',appearance='Adult woman, plain flat style, dark short hair, mother of mascot and elder sister of the declared aunt.',outfit='Plain peach top.'),dict(id='CH04',name='Dì',appearance='Adult woman, plain flat style, dark short hair, mother of declared cousin and younger sister of mascot’s mother.',outfit='Plain lavender top.')]
 c.update(brief_revision=meta['revision'],brief_hash=meta['hash'],topic=b['topic'],duration=b['duration'],style=b['style'],required_points=[x['text'] for x in b['required_points']],scenes=[],outline=[],coverage=[],claims=[],revision_response=[],open_questions=[])
 allids=[x['id'] for x in c['characters']]
 reqs=[['R1','R2'],['R2','R3'],['R3'],['R4'],['R4']]
 for i,row in enumerate(rec['rows'],1):
  title,purpose,desc,n=row; sid=f'SC{i:02}'; addition=EDITS['additions'].get(word,['','',''])[i-1] if i<=3 else ''
  narration=n+(' '+addition if addition else '')
  pause=5 if i==4 and word in ['carry','late','early','parent','grandparent','uncle','aunt','cousin','son','daughter','husband','wife','boyfriend','girlfriend','get dressed','get ready','best friend','tooth','foot'] else 4 if i==4 else 0
  camera='Eye-level medium shot with a single semantic focus; separate flat close-up diagrams for anatomy and family links; portrait phone readability. Keep frame stable through the learner response.'
  sc=dict(id=sid,title=title,purpose=purpose,action=desc,setting=rec['setting'],camera=camera,narration=narration,requirements=reqs[i-1],character_ids=allids,source_ids=[],vocabulary=[dict(word=word,meaning=gloss)],images=[],beats=[],audio_direction={'vi':dict(intent='Ask the retrieval question calmly, then leave the complete quiet hold; the answer belongs to the next scene.' if i==4 else 'Confirm the response and resolve the initial situation.' if i==5 else 'Explain this concrete action or relationship conversationally; give the English model a clear natural pause.',pronunciation_notes=f'Read the English model as a complete sentence. Check the actual pronunciation of {word} and any plural ending on the WAV later; spelling including I stays unchanged. This direction is not a verified voice control.',learner_pause_seconds=pause)})
  c['scenes'].append(sc)
  transition=f'Continue the same situation: {rec["rows"][i][1]}' if i<5 else 'After the learner response, confirm the correct answer and resolve the opening goal.'
  c['outline'].append(dict(scene_id=sid,purpose=purpose,requirements=reqs[i-1],transition=transition))
 return c

def attach(c, rec, item):
 """Narration is final before creating any anchors or coverage."""
 word=item['word']; keep='Preserve the canonical round white head, solid oval eyes, exactly one pale-blue short-sleeve shirt, minimal limbs, all declared characters, camera angle and stable prop layout. Keep minor expressions within permitted 80/20 tolerance.'
 instruction='Attach the canonical mascot Character reference. Keep each declared person distinct and only show those specified for this frame. All diagrams are separate flat educational objects; never alter mascot anatomy. Reserve bottom 22% for subtitles and outer 10% margins. No unlisted labels, numbers, logos or text.'
 for i,sc in enumerate(c['scenes'],1):
  n=sc['narration']; original=rec['rows'][i-1][3]; desc=rec['rows'][i-1][2]; segments=[(0,desc,None)]
  models=list(re.finditer(r'"([^"\n]+)"|“([^”\n]+)”',original))
  if models and models[0].start()>=12:
   model=models[0].group(1) or models[0].group(2)
   segments.append((models[0].start(),desc+' Focus on the same referent with the permitted English model placed above it. Preserve the ongoing action state.',model))
  if len(n)>len(original):
   segments.append((len(original)+1,SUPPORT[word],word))
  elif not models and i<=3 and len(n)>125:
   sentences=list(re.finditer(r'(?<=[.!?])\s+',n)); pos=sentences[len(sentences)//2].end() if sentences else 0
   if pos>0:segments.append((pos,desc+' Focus more closely on the semantic referent already shown; keep the action consistent with this line.',word))
  # Independent semantic cards use independent composition; inherited shots retain the base camera.
  for k,(pos,d,label) in enumerate(segments,1):
   iid=f'{sc["id"]}_I{k}'; inherited=k>1 and not (len(n)>len(original) and pos==len(original)+1)
   text=[]
   if k==1 and i==1:text=[dict(text=word,placement='Upper third, close to the semantic referent, clear of face and captions.',object='Flat teaching text.')]
   if label:text=[dict(text=label,placement='Upper third, above the referent; readable on phone, clear of face and subtitles.',object='Flat teaching text.')]
   if word in ['late','early'] and i in [1,3,4]:
    text += [dict(text='Lớp: 8:00',placement='Upper left comparison card, clear of main learning sentence.',object='Schedule card.'),dict(text='Đến: '+('8:10' if word=='late' else '7:50'),placement='Upper right comparison card, clear of main learning sentence.',object='Arrival-time card.')]
   if i==4:
    # The learner sees only a stem/options if these are in the spoken prompt.
    text=[t for t in text if word.lower() not in t['text'].lower() or '...' in t['text']]
    if word in ['parent','grandparent','tooth','foot','leg']:
     candidates={'parent':'a parent / parents','grandparent':'a grandparent / grandparents','tooth':'tooth / teeth','foot':'foot / feet','leg':'leg / legs'}
     text.append(dict(text=candidates[word],placement='Upper third: two equally emphasized choices; neither marked correct.',object='Practice options.'))
   im=dict(id=iid,description=d+' '+rec['setting']+' '+instruction,character_ids=sc['character_ids'],based_on=sc['images'][0]['id'] if inherited else None,preserve=keep if inherited else '',change=d,reason='Present the model at the spoken quote.' if label and '"' in n[pos:pos+1] else 'Make the meaning or relevant contrast visible at this line.',visible_text=text)
   sc['images'].append(im)
   quote=' '.join(n[pos:].split()[:7])
   if quote not in n[pos:]: quote=n[pos:pos+min(65,len(n)-pos)]
   occurrence=n[:pos].count(quote)+1
   sc['beats'].append(dict(id=f'{sc["id"]}_B{k}',image_id=iid,purpose='Hold the retrieval cue through the quiet response interval.' if i==4 else 'Connect this line to its concrete referent or semantic contrast.',anchor={'vi':dict(quote=quote,occurrence=occurrence)},effect='hold' if i==4 else 'cut',focus=dict(x=.5,y=.4)))
  for rid in sc['requirements']:c['coverage'].append(dict(requirement_id=rid,scene_id=sc['id'],quote=n))

def prepare_proposals():
 # Preview all scripts before changing any job.
 from content_contract import validate_brief,validate_content
 from scripts.story_plan import estimates
 manifest=[]
 for item in SCOPE:
  rec=records_for(item['word']); b,gloss=provisional_brief(item,rec)
  meta=load(SYS/'runs'/item['job']/'brief-current.json'); c=skeleton(item,rec,b,gloss,meta);attach(c,rec,item)
  validate_brief(SYS,b); validate_content(SYS,b,meta['revision'],meta['hash'],c)
  timing=estimates(b,c); central=sum(s['seconds'] for s in timing['languages']['vi']['scenes'])
  entry={**item,'title':rec['title'],'selected_gloss':gloss,'estimated_seconds':round(central,2),'estimate_range':[timing['languages']['vi']['min'],timing['languages']['vi']['max']],'images':sum(len(s['images']) for s in c['scenes']),'record':rec}
  save(OUT/'proposals/briefs'/f'{item["number"]:02}.json',b);save(OUT/'proposals/content'/f'{item["number"]:02}.json',c)
  manifest.append(entry)
 save(OUT/'proposal-manifest.json',manifest)
 print(json.dumps([{'number':x['number'],'word':x['word'],'target':x['requested_duration']['target_seconds'],'estimate':x['estimated_seconds'],'images':x['images']} for x in manifest],ensure_ascii=False,indent=2))

def update_jobs():
 results=[]
 for item in load(OUT/'proposal-manifest.json'):
  job=item['job']; old=PREFLIGHT[job]['status']['stages'][0]
  # Refresh status/next immediately before each production mutation.
  cli('status',job);cli('next',job)
  if old['revision'] is not None:
   cli('reject',job,'content','--revision',str(old['revision']),'--note',NOTE)
  brief=OUT/'proposals/briefs'/f'{item["number"]:02}.json'
  cli('revise-brief',job,'--brief',str(brief),'--note',NOTE)
  folder=SYS/'runs'/job; meta=load(folder/'brief-current.json');b=load(folder/'briefs'/f'{meta["revision"]}.json')
  c=load(OUT/'proposals/content'/f'{item["number"]:02}.json');c.update(brief_revision=meta['revision'],brief_hash=meta['hash'],topic=b['topic'],duration=b['duration'],style=b['style'],required_points=[x['text'] for x in b['required_points']])
  # Read existing feedback only, never mutate SQLite directly.
  with sqlite3.connect(f'file:{SYS}/.state/jobs.sqlite?mode=ro',uri=True) as db:
   feedback=db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id",(job,)).fetchall()
  c['revision_response']=[dict(request_id=str(rid),status='addressed',explanation='Đã cập nhật nghĩa chọn, thời lượng, lời dẫn và hình làm rõ điểm dễ nhầm; giữ hai câu ví dụ, lượt nhớ lại có phản hồi. Tạo lại coverage và anchor sau khi chốt lời; giữ mascot và các gate.',scene_ids=[s['id'] for s in c['scenes']]) for rid,note in feedback]
  save(folder/'draft/outline.json',c['outline']);save(folder/'draft/content.json',c)
  check=cli('check-draft',job)
  state=cli('run',job,'content')
  if state.get('state')!='awaiting_review':raise RuntimeError(f'Unexpected state: {state}')
  results.append({**{k:v for k,v in item.items() if k!='record'},'brief_revision':meta['revision'],'content_revision':state['revision'],'content_state':state['state'],'review_path':state['review'],'checks_passed':check['passed']})
  save(OUT/'updated-manifest.json',results)
  print(f'{item["number"]} {item["word"]}: content r{state["revision"]}, chờ duyệt',flush=True)

if __name__=='__main__':
 import sys
 sys.path.insert(0,str(SYS))
 if sys.argv[1:]==['apply']:update_jobs()
 else:prepare_proposals()
