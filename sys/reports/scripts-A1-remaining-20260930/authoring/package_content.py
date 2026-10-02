import json,re,copy,sys,hashlib
from source_utils import ROOT,OUT,ENTRIES,records,quotes,model_indices,practice_quotes,pause_for
sys.path.insert(0,str(ROOT))
from scripts.story_plan import estimates

recs=records()
assert len(recs)==331,('All scripts must be finished before freezing anchors',len(recs))
manifest=[]
core='Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.'

def cast(n,visual):
    lower=visual.lower()
    people=['CH01']
    if any(w in lower for w in ['friend','companion','both','guide','clerk','instructor','host','group','minh','lan','grandfather','artist','adult','participant','reader']):
        people.append('CH02')
    if any(w in lower for w in ['third','three adults','group','instructor','clerk','host','photographer','minh and','male minh and female lan']):
        people.append('CH03')
    if n in {450,566,568,606,607,610,694,695,698,738,743,744,760}:
        people=['CH01','CH02','CH03']
    if n==756:
        people=['CH01','CH02','CH03','CH04']
    return list(dict.fromkeys(people))

def characters(n):
    second='Adult principal companion in minimal ink style; maintain the same adult identity and role within this story.'
    third='Adult additional participant or professional explicitly named in the scene. Preserve the same role and identity; do not add a person when the scene does not call for one.'
    if n==450:
        third='Fictional adult female actress, appears only on the poster or screen within the scene; same identity throughout.'
    if n==566:
        second='Fictional older adult grandfather who is active at the craft table.'
        third='Adult visiting companion listening to the grandfather.'
    if n==568:
        second='Adult visitor companion at community art class.'
        third='Fictional young adult female artist introducing her own work.'
    if n==606:
        second='Fictional adult male Minh, the explicitly stated owner of the bag.'
        third='Adult companion listening to mascot describe Minh and his item.'
    if n==607:
        second='Fictional adult female Lan, the explicitly stated owner of the notebook.'
        third='Adult companion listening to mascot describe Lan and her item.'
    if n==610:
        second='Fictional adult male Minh, co-owner of the poster with Lan.'
        third='Fictional adult female Lan, co-owner of the poster with Minh; mascot is not an owner of this project.'
    if n in {694,743,744}:
        second='Fictional adult male Minh, participating companion; maintain the named identity.'
        third='Fictional adult female Lan, participating listener or recipient; maintain the named identity.'
    if n in {695,738,760}:
        second='Adult companion who listens or helps with the current task.'
        third='Fictional adult female Lan, identified participant or recipient, keep her identity throughout.'
    if n==698:
        second='Fictional adult male Minh, co-maker of the poster with Lan.'
        third='Fictional adult female Lan, co-maker of the poster with Minh; mascot observes their work.'
    result = [
        {'id':'CH01','name':'Người que áo xanh biển nhạt','appearance':core,'outfit':'Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.'},
        {'id':'CH02','name':'Người đồng hành chính','appearance':second+' Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.','outfit':'Single plain mustard-yellow top; only specifically needed role accessories.'},
        {'id':'CH03','name':'Người tham gia hoặc nhân vật bổ trợ','appearance':third+' Minimal flat ink style and ordinary adult proportions.','outfit':'Single plain lavender top; only specifically needed role accessories.'}
    ]
    if n==756:
        result.append({'id':'CH04','name':'Người thứ tư cần ghế','appearance':'Fourth ordinary adult participant at the meeting, consistent identity throughout. Minimal flat ink style.','outfit':'Single plain coral top, no realistic muscles.'})
    return result

def purposes(count):
    if count==5:
        return ['Introduce a concrete need and the selected sense.','Make the first model an action in the situation.','Advance the same story with the second model.','Invite a supported learner response and leave time before feedback.','Provide the correct response and resolve the opening need.']
    if count==6:
        return ['Make the selected sense useful in a concrete situation.','Use the first English model with its immediate purpose.','Clarify the specific usage or condition and change the story state.','Use the second model to move the same situation forward.','Ask for one manageable response, without moving on during the learner interval.','Give feedback and show the result of the shared action.']
    return ['Establish the need and one selected meaning promptly.','Use the first model at the point where the speaker needs it.','Show the condition or contrast that makes this usage matter.','Use the second model to advance or compare within the same story.','Clarify a common trap through this example without expanding to another meaning.','Invite a supported learner response; hold before the feedback.','Provide the response and complete the opening promise.']

for n,rec in sorted(recs.items()):
    e=ENTRIES[n];job=ROOT/'runs'/e['job']
    assert not (job/'revisions/content/1/content.json').exists(),'Never overwrite submitted content: '+e['job']
    meta=json.loads((job/'brief-current.json').read_text());b=json.loads((job/f"briefs/{meta['revision']}.json").read_text())
    assert b['scene_count']==len(rec['rows']),n
    assert any('Mã mục trong kho từ vựng: '+e['id']+' ' in s for s in b['planning']['domain_requirements']),n
    count=len(rec['rows']);mi=model_indices(count);practice=count-2;roles=purposes(count);pause=pause_for(rec)
    models=[quotes(rec['rows'][i][0])[0] for i in mi]
    c={'schema_version':'3.0','brief_revision':meta['revision'],'brief_hash':meta['hash'],
       'topic':b['topic'],'duration':b['duration'],'style':b['style'],
       'required_points':[x['text'] for x in b['required_points']], 'characters':characters(n),
       'scenes':[],'coverage':[],'outline':[],'claims':[],'revision_response':[],'open_questions':[]}
    for i,(narration,visual) in enumerate(rec['rows']):
        sid=f'SC{i+1:02}';ids=cast(n,visual)
        required=['R1','R2'] if i==0 else ['R2','R3'] if i==mi[0] else ['R3'] if i==mi[1] else ['R4'] if i>=practice else ['R2']
        chosen=[e['teaching_form']] if i==0 else [models[mi.index(i)]] if i in mi else practice_quotes(narration) if i==practice else [quotes(narration)[0]] if i==count-1 and quotes(narration) else [e['teaching_form']]
        allowed=[{'text':q,'placement':'Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.','object':'Flat teaching text.'} for q in dict.fromkeys(chosen)]
        # Small literal data needed on the object, all present in the spoken story.
        for literal in ['hello','cat','five','one hundred','two hundred','one thousand','two thousand','I am here','I write','I need a chair','The bag is blue']:
            if literal.lower() in narration.lower() and literal.lower() in visual.lower():
                allowed.append({'text':literal,'placement':'On the explicitly described card, object or display; readable and clear of teaching sentence.','object':'The literal teaching example named in narration.'})
        suffix=' Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.'
        pieces=visual.split(' => ')
        assert len(pieces)<=2,(n,sid)
        images=[];beats=[]
        for k,piece in enumerate(pieces):
            iid=f'{sid}_I{k+1}'
            im={'id':iid,'description':piece+suffix,'character_ids':ids,
                'based_on':f'{sid}_I1' if k else None,
                'preserve':'Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.' if k else '',
                'change':piece,'reason':roles[i] if not k else 'Show the explicitly described before/after state with the same camera and identities.',
                'visible_text':allowed if k or len(pieces)==1 else []}
            images.append(im)
            anchor=narration
            if k:
                candidates=[q for q in quotes(narration) if narration.find(q)>0]
                assert candidates,(n,sid,'A later literal anchor is needed for the changed image')
                anchor=candidates[0]
            beats.append({'id':f'{sid}_B{k+1}','image_id':iid,'purpose':im['reason'],
                          'anchor':{'vi':{'quote':anchor,'occurrence':1}},'effect':'hold' if i==practice else 'cut','focus':{'x':0.5,'y':0.4}})
        sc={'id':sid,'title':rec['title']+' — '+('Lượt thực hành' if i==practice else 'Phản hồi và kết quả' if i==count-1 else 'Nhịp '+str(i+1)),
            'purpose':roles[i],'action':visual,'setting':rec['setting'],
            'camera':'Frame the word referent and one meaningful action; adjust shot scale to the object or relation. Lock view for based_on changes and hold during the learner response.',
            'narration':narration,'requirements':required,'character_ids':ids,'source_ids':[],
            'vocabulary':[{'word':e['teaching_form'],'meaning':e.get('selected_gloss_vi',e['gloss_vi'])}],
            'images':images,'beats':beats,
            'audio_direction':{'vi':{'intent':'Invite the response, then wait quietly at the scene end.' if i==practice else 'Give the response and finish the story clearly.' if i==count-1 else 'Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible.',
                                      'pronunciation_notes':'Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality.',
                                      'learner_pause_seconds':pause if i==practice else 0}}}
        if n==602:
            sc['audio_direction']['vi']['pronunciation_notes']+=' Check the adjective close with its final /s/, distinct from the verb close; verify in the actual WAV.'
        c['scenes'].append(sc)
        c['outline'].append({'scene_id':sid,'purpose':roles[i],'requirements':required,
                             'transition':'Story continuity: '+rec['plot']+'. Next event: '+(rec['rows'][i+1][1] if i+1<count else 'Hold the completed result after feedback.')})
        for rid in required:
            c['coverage'].append({'requirement_id':rid,'scene_id':sid,'quote':narration})
    used={cid for s in c['scenes'] for cid in s['character_ids']}
    c['characters']=[ch for ch in c['characters'] if ch['id'] in used]
    draft=job/'draft';draft.mkdir(exist_ok=True)
    (draft/'content.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    (draft/'outline.json').write_text(json.dumps({'outline':c['outline']},ensure_ascii=False,indent=2)+'\n')
    est=estimates(b,c);sec=round(sum(x['seconds'] for x in est['languages']['vi']['scenes']),1)
    manifest.append({**e,'title':rec['title'],'objective':rec['objective'],'plot':rec['plot'],
                     'brief_revision':meta['revision'],'models':models,'practice_pause_seconds':pause,
                     'estimated_seconds':sec,'estimate_range_seconds':[est['languages']['vi']['min'],est['languages']['vi']['max']],
                     'planned_images':sum(len(s['images']) for s in c['scenes']),'warnings':est['warnings'],
                     'state':'draft','content_revision':None})
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Packaged',len(manifest),'scripts;',sum(e['scene_count'] for e in manifest),'scenes;',sum(e['planned_images'] for e in manifest),'planned images')
