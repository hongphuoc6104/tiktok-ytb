from pathlib import Path
import json,subprocess,sqlite3,hashlib,re,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from scripts.story_plan import estimates
OUT=ROOT/'reports/drama-A1-all-20261001';M=json.loads((OUT/'manifest.json').read_text());selected=set(sys.argv[1:])
def save():(OUT/'manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n')
def call(job,command,*args):
 for attempt in range(600):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py',command,job,*args],cwd=ROOT,capture_output=True,text=True)
  try:d=json.loads(r.stdout)
  except Exception:raise RuntimeError(r.stdout+'\n'+r.stderr)
  if d.get('blocked')=='Another operation is running':time.sleep(.1);continue
  (OUT/'operations'/f'{job}-{command}.json').write_text(r.stdout)
  if r.returncode or d.get('blocked') or d.get('passed') is False:
   with (ROOT/'logs/issues/ISSUE-DRAMA-A1-ALL-20261001.md').open('a') as f:f.write('\n## '+job+' — '+command+'\n\n```json\n'+json.dumps(d,ensure_ascii=False,indent=2)+'\n```\n\nGiữ hồ sơ hiện tại; không lặp tự động hoặc sửa file bảo vệ.\n')
   raise RuntimeError(r.stdout)
  return d
 raise RuntimeError('Bounded lock wait exhausted '+job)
def model_quotes(narr):
 return [q for q in re.findall(r'"([^"]+)"',narr) if re.search(r'[A-Za-z]',q) and not re.search(r'[À-ỹ]',q)]
for e in M:
 j=e['job'];p=ROOT/'runs'/j;frozen=OUT/'narration-frozen'/f'{j}.json'
 if (selected and j not in selected) or not frozen.exists() :continue
 ep=json.loads(frozen.read_text());
 if ep.get('visual_review_ready') is False:continue
 frozen_hash=hashlib.sha256(frozen.read_bytes()).hexdigest()
 if e.get('state')=='awaiting_review_new' and e.get('narration_frozen_sha256')==frozen_hash:continue
 assert len(ep['scenes'])==e['scene_count']
 practices=[i for i,s in enumerate(ep['scenes']) if s['practice_pause_seconds']>0]
 assert len(practices)==1 and practices[0]<len(ep['scenes'])-1
 assert all('...' not in s['narration'] and '…' not in s['narration'] for s in ep['scenes'])
 assert len(re.split(r'[.!?]',ep['scenes'][0]['narration'])[0].split())<=9
 teaching=ep.get('teaching_form',e.get('teaching_form',e['word']))
 gloss=ep.get('selected_gloss_vi',e.get('selected_gloss_vi',e['gloss_vi']))
 e.update(teaching_form=teaching,selected_gloss_vi=gloss)
 proposal=Path(e['new_brief_path'])
 if not proposal.is_absolute():proposal=ROOT/proposal
 proposed=json.loads(proposal.read_text())
 scope='Editorial scope for this episode: teach '+teaching+' ('+e['pos']+'), only the bank-selected sense '+gloss+'. Bank entry identifier unchanged: '+e['entry_id']+'.'
 proposed['planning']['domain_requirements']=[x for x in proposed['planning']['domain_requirements'] if not x.startswith('Editorial scope for this episode:')]
 proposed['planning']['domain_requirements'].append(scope)
 if json.loads(proposal.read_text())!=proposed:
  proposal.write_text(json.dumps(proposed,ensure_ascii=False,indent=2)+'\n')
 assert ep.get('editorial_review') in ['Reviewed and rewritten by primary agent; narration frozen before anchors.','Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.']
 status=call(j,'status');nxt=call(j,'next');diff=call(j,'integrity-diff');assert not diff['changed'],diff
 if any(s.get('revision') for s in status['stages'][1:]) or any(any((p/'revisions'/mod).glob('*')) for mod in ['audio','images','render']):
  e.update(state='skipped_protected_now',reason='Media/render began after inventory');save();continue
 assert status['mode']=='review' and status['stages'][0]['state'] in ['approved','awaiting_review'],status
 current_rev=status['stages'][0]['revision'];assert current_rev==e.get('new_content_revision',e['content_revision']),'External content revision changed '+j
 saved=p/f'revisions/content/{current_rev}/content.json';assert json.loads((p/'draft/content.json').read_text())==json.loads(saved.read_text()),'Unowned draft change '+j
 source=p/f"revisions/content/{e['content_revision']}/content.json";assert hashlib.sha256(source.read_bytes()).hexdigest()==e['source_content_sha256'],j
 note='bắt đầu áp dụng cho toàn bộ kịch bản A1 còn lại\n\nRà biên tập bài '+e['word']+': viết lại thành “'+ep['title']+'”, '+ep['plot_vi']+' Giữ nghĩa kho/mascot/ý bắt buộc, tiếng Anh dùng trong chuyện, lượt đáp câu có4 giây chờ rồi phản hồi. Chưa duyệt nội dung mới thay người dùng.'
 call(j,'reject','content','--revision',str(current_rev),'--note',note)
 ptr=json.loads((p/'brief-current.json').read_text())
 current_brief=json.loads((p/f"briefs/{ptr['revision']}.json").read_text())
 if ptr['revision']==e['brief_revision'] or scope not in current_brief['planning']['domain_requirements']:call(j,'revise-brief','--brief',e['new_brief_path'],'--note',note)
 ptr=json.loads((p/'brief-current.json').read_text());brief=json.loads((p/f"briefs/{ptr['revision']}.json").read_text())
 chars=[e['content']['characters'][0]]+[{'id':x['id'],'name':x['name_vi'],'appearance':x['appearance_en'],'outfit':x['outfit_en']} for x in ep['characters'] if x['id']!='CH01']
 all_ids={c['id'] for c in chars};scenes=[];outline=[];coverage=[]
 common=' Keep the canonical mascot identity: one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Attach canonical Character reference. Maintain outfits, prop ownership and screen direction. Show only the listed people. Clear outer ten percent and bottom twenty-two percent for captions/UI. No writing except visible_text; no logos, incidental numbers or watermarks.'
 for idx,s in enumerate(ep['scenes']):
  sid=s['scene_id'];narr=s['narration'];assert '...' not in narr and '…' not in narr
  requirements=(['R1'] if idx==0 else [])+['R2']+(['R3'] if model_quotes(narr) else [])+(['R4'] if idx in [practices[0],practices[0]+1] else [])
  # Honor any extra required point by explicit, reviewed narrative mapping; the present batch contains exactly R1–R4.
  assert {r['id'] for r in brief['required_points']}=={'R1','R2','R3','R4'}
  texts=[s['stem']] if s['practice_pause_seconds'] else model_quotes(narr)
  if idx==1:texts=[teaching+' · '+gloss]
  texts=list(dict.fromkeys(texts));im={'id':sid+'_I1','description':s['visual_en']+common,'character_ids':s['character_ids'],'based_on':None,'preserve':'','change':s['visual_en'],'reason':s['purpose_en'],'visible_text':[{'text':t,'placement':'Upper third inside safe area, separate from faces and the bottom subtitle region; readable at phone size.','object':'Quiet flat learning caption; no other wording.'} for t in texts]}
  im['visible_text'].extend(s.get('custom_visible_text',[]))
  images=[im];beats=[{'id':sid+'_B1','image_id':im['id'],'purpose':s['purpose_en'],'anchor':{'vi':{'quote':narr,'occurrence':1}},'effect':'hold' if s['practice_pause_seconds'] else 'cut','focus':{'x':.5,'y':.4}}]
  for index,state in enumerate(s.get('extra_visual_states',[]),2):
   assert state['quote'] in narr and narr.find(state['quote'])>0
   images.append(dict(im,id=f'{sid}_I{index}',description=state['visual_en']+common,based_on=images[-1]['id'],preserve='Keep camera, layout, all identities/outfits and prop ownership fixed; change only the specified action/state.',change=state['visual_en'],reason=state['purpose_en']))
   images[-1]['visible_text'].extend(state.get('custom_visible_text',[]))
   beats.append({'id':f'{sid}_B{index}','image_id':images[-1]['id'],'purpose':state['purpose_en'],'anchor':{'vi':{'quote':state['quote'],'occurrence':1}},'effect':'cut','focus':{'x':.5,'y':.4}})
  scene={'id':sid,'title':s['title_vi'],'purpose':s['purpose_en'],'action':s['visual_en'],'setting':'The established setting and props of this episode, kept continuous.','camera':'Frame the single dominant action/referent. Hold during learner response; cut only when the narrative state changes. Keep caption and upper teaching text regions separate.','narration':narr,'requirements':requirements,'character_ids':s['character_ids'],'source_ids':[],'vocabulary':[{'word':teaching,'meaning':gloss}],'images':images,'beats':beats,'audio_direction':{'vi':{'intent':s['purpose_en']+' Tell the concrete personal situation without a lecture voice. These are listening directions, not engine controls.','pronunciation_notes':'Keep English I and spelling. Listen to actual WAV for the English models, language switches, restrained emotion and learner interval; no vocal quality is claimed from text.','learner_pause_seconds':s['practice_pause_seconds']}}}
  assert set(scene['character_ids'])<=all_ids;scenes.append(scene)
  outline.append({'scene_id':sid,'purpose':scene['purpose'],'requirements':requirements,'transition':s['purpose_en']+' Next causal state: '+(ep['scenes'][idx+1]['visual_en'] if idx+1<len(ep['scenes']) else 'Hold the resolved consequence of this episode.')})
  for req in requirements:coverage.append({'requirement_id':req,'scene_id':sid,'quote':narr})
 with sqlite3.connect(f'file:{ROOT}/.state/jobs.sqlite?mode=ro',uri=True) as db:requests=db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id",(j,)).fetchall()
 assert requests[-1][1]==note
 responses=[{'request_id':str(rid),'status':'addressed','explanation':('Yêu cầu trước được giữ trong lịch sử; bản này theo hướng phim ngắn người dùng vừa duyệt. ' if i<len(requests)-1 else '')+'Đã viết lại toàn bộ diễn biến: '+ep['plot_vi']+' Mở cụ thể, hai mẫu có ngữ cảnh, lượt nói câu có khoảng chờ và đáp án. Không nói câu bỏ trống trong narration. Thời lượng/giữ chân chưa đo.','scene_ids':[s['id'] for s in scenes]} for i,(rid,note0) in enumerate(requests)]
 content={'schema_version':'3.0','brief_revision':ptr['revision'],'brief_hash':ptr['hash'],'topic':brief['topic'],'duration':brief['duration'],'style':brief['style'],'required_points':[r['text'] for r in brief['required_points']],'characters':chars,'scenes':scenes,'coverage':coverage,'outline':outline,'claims':[],'revision_response':responses,'open_questions':[]}
 assert hashlib.sha256(frozen.read_bytes()).hexdigest()==frozen_hash
 (p/'draft/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n');(p/'draft/outline.json').write_text(json.dumps({'outline':outline},ensure_ascii=False,indent=2)+'\n')
 check=call(j,'check-draft');result=call(j,'run','content');assert result['state']=='awaiting_review';new_rev=result['revision'];new_saved=p/f'revisions/content/{new_rev}/content.json';assert json.loads(new_saved.read_text())==content
 assert hashlib.sha256(source.read_bytes()).hexdigest()==e['source_content_sha256']
 timing=estimates(brief,content);units=sum(len(s['narration'].split()) for s in scenes);first=scenes[0]['narration'].split('.')[0]+'.'
 lines=[f"# {teaching} — {ep['title']}",'', '**Nghĩa chọn:** '+gloss, '', '**Chuyện:** '+ep['plot_vi'],'',f"**Content r{new_rev} · chờ người dùng duyệt.** {len(scenes)} cảnh. Chưa tạo media. Thời lượng theo brief là tham khảo, chưa đo WAV.",'',f"[Bản duyệt gốc]({result['review']})",'']
 for s in scenes:
  lines += [f"## {s['id']}",'',s['narration'],'']
  if s['audio_direction']['vi']['learner_pause_seconds']:lines += ['**Chờ '+str(s['audio_direction']['vi']['learner_pause_seconds'])+' giây cuối cảnh; đáp án ở cảnh sau.**','']
  lines += ['**Chữ trên hình:** '+' · '.join(t['text'] for im in s['images'] for t in im['visible_text']),'']
 reader=OUT/'kich-ban'/f'{j}.md';reader.write_text('\n'.join(lines)+'\n');assert all(s['narration'] in reader.read_text() for s in scenes)
 e.update(state='awaiting_review_new',new_content_revision=new_rev,new_brief_revision=ptr['revision'],review=result['review'],reader=str(reader),narration_frozen_sha256=frozen_hash,opening=first,units=units,duration_estimate=timing,checks_passed=check['passed'],source_history_preserved=True,editorial_reviewed=True)
 save();print('UPDATED',j,'r'+str(new_rev),ep['title'],'units',units,flush=True)
print('PROGRESS',sum(e.get('state')=='awaiting_review_new' for e in M),'/',len(M),flush=True)
