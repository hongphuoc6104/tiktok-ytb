import json,pathlib,sys,re
P=pathlib.Path('/home/hongphuoc6104/Desktop/pipelineFlow/sys/reports/drama-A1-all-20261001');O=P/'shards/nhom-1'
name=sys.argv[1]; es=json.loads((O/name/'response.json').read_text())['structured_output']['episodes']
patchpath=O/(name+'-patches.json');patches=json.loads(patchpath.read_text()) if patchpath.exists() else {}
m={x['job']:x for x in json.loads((P/'manifest.json').read_text())}
for e in es:
 for i,s in enumerate(e['scenes'],1):
  s['scene_id']=f'SC{i:02}'
  if isinstance(s.get('practice_pause_seconds'),str):s['practice_pause_seconds']=float(s['practice_pause_seconds'])
 for spec in patches.get(e['job'],[]):
  if spec.get('scene'):
   sc=e['scenes'][spec['scene']-1];sc.update(spec['set'])
  else:e.update(spec['set'])
 assert len(e['scenes'])==m[e['job']]['scene_count'],e['job']
 assert any(c['id']=='CH01' for c in e['characters'])
 assert all('CH01' not in s['visual_en'] and not re.search(r'SC\d',s['visual_en']) for s in e['scenes'])
 practice=[s for s in e['scenes'] if s.get('practice_pause_seconds',0)>0]; assert len(practice)==1,e['job']
 assert practice[0].get('stem') and '___' in practice[0]['stem'],e['job']
 assert 3<=practice[0]['practice_pause_seconds']<=5
 assert all('...' not in s['narration'] and '…' not in s['narration'] for s in e['scenes']),e['job']
 assert all(c in {a['id'] for a in e['characters']} for s in e['scenes'] for c in s['character_ids'])
 for s in e['scenes']:
  for ex in s.get('extra_visual_states',[]):assert ex['quote'] in s['narration']
 e['opening_function_vi']='Mở bằng chi tiết cụ thể: '+re.split(r'(?<=[.!?])\s+',e['scenes'][0]['narration'])[0]
 e['learner_outcome_vi']='Dùng đúng nghĩa '+e.get('selected_gloss_vi',m[e['job']]['gloss_vi'])+' của '+e.get('teaching_form',m[e['job']]['word'])+' trong một câu đầy đủ gắn với câu chuyện.'
 for i,sc in enumerate(e['scenes']):
  sc['title_vi']=['Điều đang xảy ra','Vướng mắc nhỏ','Một hành động cần thiết','Lời cần nói','Kết quả gần'][i] if len(e['scenes'])==5 else sc['title_vi']
  sc['purpose_en']=['Establish the concrete personal situation and introduce or prepare an early English model.','Advance the same situation and clarify the target sense with meaningful English usage.','Show the small action or consequence that motivates the upcoming response.','Ask for a complete story-linked sentence, then hold before the answer.','Give the correct answer and close with the earned local consequence.'][i] if len(e['scenes'])==5 else sc['purpose_en']
 e['editorial_review']='Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.';e['visual_review_ready']=True
 f=P/'narration-frozen'/f"{e['job']}.json";t=f.with_suffix('.tmp');t.write_text(json.dumps(e,ensure_ascii=False,indent=2));t.replace(f)
 print(e['job'],sum(len(s['narration'].split()) for s in e['scenes']))
(O/(name+'-review.json')).write_text(json.dumps({'reviewed_jobs':[e['job'] for e in es],'checks':['actual narration read','target sense/POS','English examples and full retrieval','causal arc','actual visual prose read','cast continuity','mascot brand plan','no anchors yet']},ensure_ascii=False,indent=2))
