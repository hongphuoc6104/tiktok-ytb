from pathlib import Path
import json,copy,re,hashlib,sys
p=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent
sys.path.insert(0,str(p));from scripts.story_plan import estimates
m=json.loads((p/'reports/scripts-60-20260929/manifest.json').read_text())[:20]
rows={}
for block in (out/'openings.txt').read_text().split('@')[1:]:
 lines=block.strip().splitlines();n,g=lines[0].split('|');assert len(lines)==4;rows[int(n)]={'group':g,'narration':lines[1:3],'visual':lines[3]}
assert len(rows)==20
second={
81:('Có tiếng gõ vui tai rồi','The mascot turns the anatomical heart flashcard toward the friend while the toy stethoscope remains on the table.'),
82:('Một cuộc gọi về nhà','The mascot settles the tablet securely on its stand and leans in to listen to the elderly relative.'),
83:('Tấm ảnh chỉ cho thấy','The mascot lowers the walking photograph slightly and makes eye contact with the friend, inviting a reply.'),
84:('Người bạn bước tới giúp.','The mustard-shirt friend moves beside the heavy box, ready to help; the box is still on the floor.'),
85:('Người bạn không tới được','The mascot glances from the phone toward the empty chair, holding the same phone without changing its message.'),
86:('Chỉ cần câu ấy','The mascot lowers the tissue packet onto the table while continuing to address the friend.'),
87:('Mô hình có thể chờ','The mascot places the unfinished paper roof flat on the table beside the open storage box.'),
88:('Bạn quay sang người bên cạnh','The mascot turns toward the nearby passerby and gestures toward the two buildings, still holding the visiting bag.'),
89:('Nhân viên nghe xong','The receptionist responds with a welcoming hand gesture while the mascot holds the folded question paper ready.'),
90:('Chưa đọc được thẻ','The nurse gestures toward himself while addressing the mascot; keep the same badge reversed and blank.'),
91:('Bạn cần đúng thuốc của mình','The mascot turns to the family member and gestures toward the high shelf; leave both containers in place.'),
92:('Bạn cầm chiếc vé lên','The mascot holds the offered ticket with one hand and keeps the wallet open with the other, looking toward the attendant.'),
93:('Bình nước ở ngay bên cạnh','The mascot makes an inviting open-hand gesture toward the empty cups and jug; the guest has not chosen yet.'),
94:('Trên bàn có bình nước chung','The mascot holds the same empty bottle upright with the lid open and turns toward the friend near the shared jug.'),
95:('Bạn cầm bát trống','The mascot extends the empty bowl toward the friend holding the rice paddle; do not fill the bowl yet.'),
96:('Câu vừa rồi nói rõ','The mascot indicates a single-slice-sized portion with a simple stick-hand gesture; the large loaf is still intact on the board.'),
97:('Cả món có nhiều sợi','The spoon is lowered slightly over the bowl so the single noodle joins the other strands; the chopsticks stay beside the bowl.'),
98:('Đổi sang bát sâu thôi','The mascot places the flat plate on the counter and reaches for the deep bowl; keep the pot and soup unchanged.'),
99:('Cầm đúng một quả trên tay','The mascot brings the same single intact egg slightly forward for a clear view, with the other eggs still in the open carton.'),
100:('Bạn chỉ đúng món','The mascot points more clearly to one dish on the same menu while making eye contact with the server; do not reveal ingredients yet.')}
for name in ['proposals','readers','before']:(out/name).mkdir(exist_ok=True)
manifest=[]
for x in m:
 n=x['number'];rec=rows[n]; job=p/'runs'/x['job'];src=job/'revisions/content/1/content.json';old=json.loads(src.read_text());c=copy.deepcopy(old)
 (out/'before'/f'{n}.json').write_bytes(src.read_bytes())
 for i in range(2):c['scenes'][i]['narration']=rec['narration'][i]
 # Prose is finalized above. Rebuild dependent anchors only afterwards.
 for i in range(2):
  sc=c['scenes'][i];sc['purpose']='Present an immediate everyday need and the selected vocabulary meaning.' if i==0 else 'Connect the opening to a usable English model without a new introduction.'
  sc['camera']='Medium close view with one dominant referent, readable mascot reaction, stable camera and subtitle clearance.'
  sc['beats'][0]['anchor']['vi']={'quote':sc['narration'],'occurrence':1};sc['beats'][0]['purpose']=sc['purpose'];sc['audio_direction']['vi']['intent']='Begin the first spoken phrase immediately and address the situation naturally. Keep the English model intelligible; verify actual onset and rhythm on WAV during media.'
  c['outline'][i]['purpose']=sc['purpose']
  for cov in c['coverage']:
   if cov['scene_id']==sc['id']:cov['quote']=sc['narration']
 sc=c['scenes'][0];im=sc['images'][0];im['description']=rec['visual']+' Attach canonical mascot Character reference. Exactly one pale-blue short-sleeve torso, round white navy-outlined head, black oval eyes and minimal stick limbs. Keep bottom 22% free for subtitles and outer 10% safe. Render only listed visible_text; no incidental lettering or logos.'
 sc['action']=rec['visual'];sc['title']='Câu dùng ngay' if rec['group']=='B' else 'Tình huống xảy ra ngay'
 im['change']=rec['visual'];im['reason']=sc['purpose'];im['character_ids']=['CH01','CH03'] if n==82 else ['CH01','CH02'];sc['character_ids']=im['character_ids']
 text=re.findall(r'"([^"]+)"',sc['narration'])[0] if rec['group']=='B' else x['word']
 im['visible_text']=[{'text':text,'placement':'Upper third, large readable text; clear of faces, main action and subtitles.','object':'Phone message.' if n==85 else 'Flat teaching text.'}]
 quote,action=second[n];assert quote in sc['narration'];variant=copy.deepcopy(im);variant.update(id='SC01_I2',based_on='SC01_I1',preserve='Preserve the base camera, background, character identities, single pale-blue mascot torso, props, lighting and exact visible text.',change=action,reason='Show the causal next action while the opening phrase leads into the lesson.',description=action+' Same shot and layout as the base image; attach Base scene reference and canonical Character reference. Only listed text; preserve subtitle safe space.')
 sc['images'].append(variant);beat=copy.deepcopy(sc['beats'][0]);beat.update(id='SC01_B2',image_id='SC01_I2',purpose=variant['reason']);beat['anchor']['vi']={'quote':quote,'occurrence':1};sc['beats'].append(beat)
 c['outline'][0]['transition']='Resolve the immediate question or need through the next English model. Next visual event: '+c['scenes'][1]['action']
 c['outline'][1]['transition']='Continue the same interaction into the second model. Next visual event: '+c['scenes'][2]['action']
 # No changes to learner practice, feedback, senses, briefs or downstream scenes.
 assert c['scenes'][2:]==old['scenes'][2:]
 pointer=json.loads((job/'brief-current.json').read_text());brief=json.loads((job/f"briefs/{pointer['revision']}.json").read_text());e=estimates(brief,c);secs=sum(s['seconds'] for s in e['languages']['vi']['scenes'])
 (out/'proposals'/f'{n}.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 manifest.append({'number':n,'word':x['word'],'job':x['job'],'group':rec['group'],'source_revision':1,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'state':'proposal_not_submitted','estimated_seconds':round(secs,1),'duration_estimate':e,'opening_before':old['scenes'][0]['narration'],'opening_after':sc['narration']})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(manifest),'proposals, estimated seconds',min(x['estimated_seconds'] for x in manifest),max(x['estimated_seconds'] for x in manifest))
