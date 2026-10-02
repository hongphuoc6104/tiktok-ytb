import json,csv,collections,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]; v=root/'vocab'; out=Path(__file__).parent
bank=v/'bank.jsonl'; original=(out/'bank-before.jsonl').read_bytes() if (out/'bank-before.jsonl').exists() else bank.read_bytes(); items=[json.loads(s) for s in original.decode().splitlines()]; ledger=(v/'ledger.json').read_bytes(); states=json.loads(ledger)['entries']
(out/'bank-before.jsonl').write_bytes(original)
function_pos={'prep','conj','det','pron'}
contrast=set('say tell speak talk hear listen see look watch learn study teach make do bring take borrow lend wear'.split())|{'put on','take off','wake up','get up','a few','a little','few','little','many','much','too','enough','already','still','yet','since','until','while','as','either','neither'}
abstract_words=set('reason chance idea fact kind way course matter mind power state form interest process system cause method theory freedom right law legal illegal guilty innocent opinion agreement suggestion promise explanation tense grammar meaning experience quality service available necessary possible impossible allow avoid expect encourage include imagine decide believe hope need mean seem depend'.split())
idioms={'get back','look for','look like','agree with','worry about','look after','put off','put up','put down','go on','go out with','look forward to','look up','give up','check out','clear up','find out','hang on','hang up','hold on','run out of','set up','show up','depend on','focus on','think of','watch out for','wrap up','pay back','save up','believe in','complain about','hear from','keep in touch','instead of','because of'}
abstract_topics={'law-government','business-economy'}
plans=[]
for x in items:
 if x['cefr'] not in {'A1','A2'}: continue
 reasons=[]
 if x['pos'] in function_pos: reasons.append('Quan hệ ngữ pháp/cách dùng cần ngữ cảnh và lượt chọn câu')
 if x['word'] in contrast: reasons.append('Cần đối chiếu cách dùng dễ nhầm, chỉ dạy nghĩa đã chọn')
 if (x['word'] in abstract_words and not (x['word']=='kind' and x['pos']=='adj')) or (set(x['topics'])&abstract_topics and x['word'] not in {'company','cash','coin','stamp','prison','jail','president','identity card','document','form'}): reasons.append('Nghĩa trừu tượng hoặc quan hệ xã hội cần tình huống và hậu quả')
 if x['word'] in idioms: reasons.append('Cụm từ khó suy nghĩa từ từng thành phần')
 if x['pos']=='adv' and x['word'] in {'often','always','never','sometimes','usually','ago','just','only','almost','even','especially','actually','however','quite','completely','nearly','exactly'}: reasons.append('Phạm vi/tần suất hoặc sắc thái cần đối chiếu trong câu')
 extended=bool(reasons)
 tier=5 if x['pos'] in function_pos else 4 if extended else 3 if x['pos'] in {'phr','adv'} or (x['pos']=='n' and set(x['topics'])&{'common-nouns','communication-language','science-research','emotions-feelings','personality-character'}) else 3 if x['word'] in {'habit','schedule','housework','laundry','bedtime','art','music','news','health','business','science'} else 2 if x['pos'] in {'v','adj'} else 1
 state=states.get(x['id'],{}).get('status','todo')
 plans.append({'id':x['id'],'word':x['word'],'pos':x['pos'],'gloss_vi':x['gloss_vi'],'cefr':x['cefr'],'status':state,'eligible_for_reorder':state=='todo','difficulty_tier':tier,'original_rank':x['rank'],'extended':extended,'duration':{'min_seconds':75 if extended else 45,'target_seconds':100 if extended else 60,'max_seconds':120 if extended else 75},'english_explanation_target_percent':60 if extended and x['cefr']=='A1' else 70 if extended else 30 if x['cefr']=='A1' else 45,'reasons':reasons or ['Nghĩa có thể minh họa trực tiếp; ưu tiên bài ngắn'],'language_guidance':'Tăng tiếng Anh đơn giản từng bước; tiếng Việt giải nghĩa/chốt chỗ khó. Tỷ lệ tính trên phần giải thích, không tính câu mẫu; không dịch lặp mọi câu. Đây là mục tiêu biên tập, không tiêu chí nghiệm thu cứng.'})
byid={p['id']:p for p in plans}
for lv in ['A1','A2']:
 pool=[x for x in items if x['cefr']==lv and byid[x['id']]['eligible_for_reorder']]
 slots=sorted(x['rank'] for x in pool)
 pool.sort(key=lambda x:(byid[x['id']]['difficulty_tier'],x['rank']))
 for i,(x,rank) in enumerate(zip(pool,slots),1):
  x['rank']=rank; byid[x['id']]['pending_order_within_level']=i
for p in plans:p['rank']=next(x['rank'] for x in items if x['id']==p['id'])
bank.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in items))
(v/'learning-plan.json').write_text(json.dumps({'version':1,'date':'2026-09-30','scope':'A1–A2; áp dụng cho brief/kịch bản mới; không thay brief hiện có','classification':'Đề xuất biên tập theo quy tắc có thể rà soát, không phải đánh giá năng lực thực nghiệm','entries':plans},ensure_ascii=False,indent=2)+'\n')
with (out/'A1-A2-ke-hoach.csv').open('w') as f:
 fields=['id','word','gloss_vi','cefr','status','difficulty_tier','rank','extended','target_seconds','english_explanation_target_percent','reasons']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
 for p in sorted(plans,key=lambda p:p['rank']):w.writerow({k: p['duration']['target_seconds'] if k=='target_seconds' else '; '.join(p[k]) if k=='reasons' else p[k] for k in fields})
summary={lv:{'entries':sum(x['cefr']==lv for x in items),'distinct_words':len({x['word'] for x in items if x['cefr']==lv}),'extended':sum(p['cefr']==lv and p['extended'] for p in plans),'reordered':sum(p['cefr']==lv and p['eligible_for_reorder'] for p in plans)} for lv in ['A1','A2','B1','B2','C1','C2']}
(out/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
assert ledger==(v/'ledger.json').read_bytes()
assert len({x['rank'] for x in items})==len(items)
old={x['id']:x for x in map(json.loads,original.decode().splitlines())}
for x in items:
 y=dict(x);y['rank']=old[x['id']]['rank'];assert y==old[x['id']]
 if states.get(x['id'],{}).get('status','todo')!='todo':assert x==old[x['id']]
print('Verified: only pending A1/A2 ranks changed; all identities, meanings, other levels and ledger preserved.')
