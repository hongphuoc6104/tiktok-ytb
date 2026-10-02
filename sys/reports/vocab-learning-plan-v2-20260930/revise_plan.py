import json,csv,collections,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];v=root/'vocab';out=Path(__file__).parent
raw=(v/'learning-plan.json').read_bytes();
if not (out/'learning-plan-before.json').exists(): (out/'learning-plan-before.json').write_bytes(raw)
plan=json.loads(raw);bankpath=v/'bank.jsonl';bankraw=bankpath.read_bytes();items=[json.loads(s) for s in bankraw.decode().splitlines()];old={x['id']:dict(x) for x in items};ledgerraw=(v/'ledger.json').read_bytes();states=json.loads(ledgerraw)['entries']
short_ids={'watch.n','right.adj.direction','right.n.direction','little.adj.size-cute','power.n.electricity','way.n.route','form.n.shape','look.n.glance-noun','wrap up.phr.wrap-gift'}
possessive={'my','your','his','her','its','our','their'}
spatial={'behind','between','near','opposite','along','across','past','around','to','in','into','with','without','from','over','under'}
simple_conj={'and','or','but','because','before','after'}
frequency={'often','always','never','sometimes','usually','ago'}
long_contrast={'say','tell','borrow','lend','make','do','bring','take','many','much','few','a few','little','a little','too','enough','already','still','yet','either','neither'}
long_abstract={'reason','chance','mind','matter','freedom','law','theory','method','cause','process','system','grammar','tense','agreement','interest','expect','allow','avoid','encourage','seem'}
long_idioms={'put off','put up','put down','go on','go out with','look forward to','look up','give up','find out','hang on','hang up','hold on','run out of','set up','depend on','hear from','believe in'}
changes=[]
for p in plan['entries']:
 before=p['duration']['target_seconds'];word=p['word'];pos=p['pos'];lv=p['cefr'];id=p['id']
 band='short';reason='Nghĩa có thể minh họa trực tiếp; một câu mẫu và lượt thực hành ngắn đủ cho mục tiêu ban đầu.'
 if p['difficulty_tier']>=3:
  band='medium';reason='Cần thêm ngữ cảnh hoặc làm rõ cách dùng trong câu; ưu tiên một tình huống và phản hồi.'
 if p['extended']:
  band='medium';reason='Cần đối chiếu hoặc làm rõ quan hệ trong câu; không mặc định kéo tới 100 giây.'
 if (word in long_contrast and pos not in {'n','adj'}) or (word in long_abstract and pos not in {'adj'}) or (word in long_idioms and pos=='phr') or (pos in {'prep','conj'} and word in {'of','on','at','for','by','against','if','while','as','since','until','as soon as'}) or (pos=='pron' and id in {'that.pron.relative','which.pron','who.pron','either.pron','neither.pron'}) or (pos=='det' and word in {'a','an','the','any','some','other','another','each','every','many','much','few','a few','little','a little','enough'}) or id in {'right.n','power.n.authority','state.n.condition','idea.n.notion','make.v.cause'}:
  band='long';reason='Cần một đối chiếu/ngữ cảnh có mục đích và lượt vận dụng có phản hồi; dành thời gian tăng thêm cho người học.'
 if id in {'take.v.grab','take.v.photo','take.v.medicine','put down.phr.place','put up.phr.hang'}:
  band='medium';reason='Nghĩa hành động cụ thể; thêm câu dùng tự nhiên và luyện ngắn, không kéo dài theo các nghĩa khác của cùng từ.'
 if id in short_ids or (pos=='det' and word in possessive):
  band='short';reason='Nghĩa cụ thể hoặc quan hệ sở hữu đơn giản; không kéo dài vì từ đồng dạng có cách dùng khác.'
 if (pos=='prep' and word in spatial) or (pos=='conj' and word in simple_conj) or (pos=='adv' and word in frequency) or (pos=='det' and word in {'this','that','these','those','all','no','several','a lot of','a couple of','more'}):
  band='medium';reason='Dùng hình hoặc đối chiếu ngắn để làm rõ vị trí, quan hệ, tần suất hay lượng; không cần bài 100 giây mặc định.'
 durations={'A1':{'short':(45,60,65),'medium':(65,80,90),'long':(80,100,110)},'A2':{'short':(50,60,75),'medium':(75,90,100),'long':(90,100,120)}}
 lo,target,hi=durations[lv][band]
 p.update(duration_band=band,extended=band=='long',needs_more_context=band!='short',duration={'min_seconds':lo,'target_seconds':target,'max_seconds':hi},reasons=[reason],status=states.get(id,{}).get('status','todo'))
 p['eligible_for_reorder']=p['status']=='todo'
 p['difficulty_tier']=1 if band=='short' and pos=='n' else 2 if band=='short' else 3 if band=='medium' else 5 if pos in {'prep','conj','det','pron'} else 4
 p['english_explanation_target_percent']=30 if lv=='A1' else 55
 p['english_explanation_profiles']=({'early':{'min_percent':20,'target_percent':30,'max_percent':35},'late':{'min_percent':35,'target_percent':45,'max_percent':50}} if lv=='A1' else {'early':{'min_percent':50,'target_percent':55,'max_percent':65},'late':{'min_percent':60,'target_percent':70,'max_percent':75}})
 p['language_guidance']='Mặc định hồ sơ đầu cấp nếu brief chưa xác định năng lực; chuyển dần sang hồ sơ cuối cấp khi người học hiểu chỉ dẫn và câu mẫu. Tỷ lệ chỉ tính phần giải thích, không tính câu mẫu; bài dài không tự tăng tiếng Anh. Dùng tiếng Việt chốt điểm khó, không dịch lặp tất cả câu; tỷ lệ là định hướng biên tập, không ngưỡng máy chấm.'
 p['authoring_guidance']='Một nghĩa, một kết quả học quan sát được. Thời lượng gồm khoảng chờ thật; phần tăng thêm dành cho ngữ cảnh, luyện và phản hồi. Không thêm nghĩa khác hay lời lặp để đủ giây; rà lại nhu cầu từng nghĩa trước khi chốt brief.'
 if before!=target:changes.append({'id':id,'old_target':before,'new_target':target,'reason':reason})
byid={p['id']:p for p in plan['entries']}
for lv in ['A1','A2']:
 pool=[x for x in items if x['cefr']==lv and byid[x['id']]['eligible_for_reorder']];slots=sorted(x['rank'] for x in pool)
 pool.sort(key=lambda x:(byid[x['id']]['difficulty_tier'],byid[x['id']]['original_rank']))
 for i,(x,rank) in enumerate(zip(pool,slots),1):x['rank']=rank;byid[x['id']]['pending_order_within_level']=i
for p in plan['entries']:p['rank']=next(x['rank'] for x in items if x['id']==p['id'])
plan.update(version=2,classification='Đề xuất biên tập đã rà lại theo mã nghĩa, ba nhóm thời lượng; chưa kiểm nghiệm với người học.',language_policy='Độc lập với độ dài và độ khó; mặc định đầu cấp, tăng dần theo khả năng hiểu.',scope='A1–A2; áp dụng cho brief/kịch bản mới. Mục reserved/done chỉ lưu gợi ý tham khảo, không thay hợp đồng job hiện có.')
assert len({x['rank'] for x in items})==len(items)
for x in items:
 y=dict(x);y['rank']=old[x['id']]['rank'];assert y==old[x['id']]
 if states.get(x['id'],{}).get('status','todo')!='todo' or x['cefr'] not in {'A1','A2'}:assert x==old[x['id']]
assert ledgerraw==(v/'ledger.json').read_bytes()
(v/'learning-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');bankpath.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in items))
fields=['id','word','gloss_vi','cefr','status','rank','difficulty_tier','duration_band','min_seconds','target_seconds','max_seconds','english_early_range','english_late_range','reasons']
with (out/'A1-A2-ke-hoach.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for p in sorted(plan['entries'],key=lambda p:p['rank']):
  row={k:p[k] for k in fields if k in p};row.update(p['duration']);row['reasons']='; '.join(p['reasons'])
  for key in ['early','late']:
   q=p['english_explanation_profiles'][key];row['english_'+key+'_range']=f"{q['min_percent']}–{q['max_percent']}%"
  w.writerow(row)
summary={lv:{'total':sum(p['cefr']==lv for p in plan['entries']),'duration_bands':dict(collections.Counter(p['duration_band'] for p in plan['entries'] if p['cefr']==lv)),'todo_bands':dict(collections.Counter(p['duration_band'] for p in plan['entries'] if p['cefr']==lv and p['status']=='todo'))} for lv in ['A1','A2']}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');(out/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2));print('Changed duration targets:',len(changes));print('Verification passed: IDs, meanings, CEFR, protected ranks and ledger preserved; rank permutation valid.')
