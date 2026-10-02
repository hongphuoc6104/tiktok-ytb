from pathlib import Path
import json,hashlib,re,collections
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];m=json.loads((P/'manifest.json').read_text());report={'updated':0,'errors':[],'warnings':[],'openings':{},'scope':len(m)}
for e in m:
 if e.get('state')!='awaiting_review_new':continue
 j=e['job'];report['updated']+=1
 p=ROOT/'runs'/j;c=json.loads((p/f"revisions/content/{e['new_content_revision']}/content.json").read_text());ep=json.loads((P/'narration-frozen'/f'{j}.json').read_text());ids={x['id'] for x in c['characters']}
 def err(v):report['errors'].append({'job':j,'error':v})
 def warn(v):report['warnings'].append({'job':j,'warning':v})
 if c!=json.loads((p/'draft/content.json').read_text()):err('Draft differs from current saved revision')
 if len(c['scenes'])!=e['scene_count']:err('Scene count changed')
 if hashlib.sha256((p/f"revisions/content/{e['content_revision']}/content.json").read_bytes()).hexdigest()!=e['source_content_sha256']:err('Original history changed')
 if e.get('narration_frozen_sha256')!=hashlib.sha256((P/'narration-frozen'/f'{j}.json').read_bytes()).hexdigest():warn('Frozen authoring changed; new revision required')
 pauses=[i for i,s in enumerate(c['scenes']) if s['audio_direction']['vi']['learner_pause_seconds']>0]
 if len(pauses)!=1 or pauses[0]==len(c['scenes'])-1:err('Invalid practice position')
 if [s['narration'] for s in c['scenes']]!=[s['narration'] for s in ep['scenes']]:warn('Latest frozen narration not yet applied')
 reader=Path(e['reader']).read_text()
 models=[]
 for i,s in enumerate(c['scenes']):
  if s['narration'] not in reader:err('Reader lost literal narration')
  if not set(s['character_ids'])<=ids:err('Unknown cast')
  for b in s['beats']:
   if b['anchor']['vi']['quote'] not in s['narration']:err('Nonliteral anchor')
  for im in s['images']:
   if not set(im['character_ids'])<=ids:err('Unknown image cast')
   if re.search(r'\b(?:CH\d\d|SC\d\d)\b',im['description']):err('Internal ID in visual prose')
  models += [q for q in re.findall(r'"([^"]+)"',s['narration']) if re.search(r'[A-Za-z]',q) and not re.search(r'[À-ỹ]',q)]
 if len(set(models))!=2:warn('Distinct quoted English models: '+str(len(set(models))))
 if pauses:
  stem=ep['scenes'][pauses[0]].get('stem','');reply=c['scenes'][pauses[0]+1]['narration']
  if not reply.startswith('"'):err('Answer not at start of next scene')
  if stem:
   pat=re.sub(r'_+', '(.+?)', re.escape(stem.replace('’',"'")));matches=[re.fullmatch(pat,q.replace('’',"'")) for q in models];gaps=[x.group(1) for x in matches if x]
   if not gaps:warn('Practice stem not matching a model')
   teaching=e.get('teaching_form',e['word']).lower()
   if gaps and not any(g.lower().replace('’',"'").rstrip('s') in teaching.rstrip('s') or teaching.rstrip('s') in g.lower().rstrip('s') for g in gaps):warn('Practice gap may target another word: '+str(gaps))
 opening=re.split(r'[.!?]',c['scenes'][0]['narration'])[0].strip();report['openings'].setdefault(opening,[]).append(j)
 if len(opening.split())>9:warn('Opening exceeds9 units')
 report['last_checked_job']=j
report['duplicate_openings']={k:v for k,v in report['openings'].items() if len(v)>1};report.pop('openings');(P/'verification-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
ready=[e for e in m if e.get('state')=='awaiting_review_new'];lines=['# Kịch bản A1 theo dạng phim ngắn','',f'Đã cập nhật {len(ready)}/{len(m)} bài trong phạm vi. Tất cả bản mới chờ duyệt content; chưa tạo media.','', 'Thời lượng và 3 giây mở đầu là kế hoạch tham khảo; chưa đo WAV hoặc hiệu quả giữ chân.','']
for e in ready:lines.append(f"- [{e.get('teaching_form',e['word'])} — {e['opening']}]({e['reader']}) · content r{e['new_content_revision']}")
for e in ready:lines+=['','---','',Path(e['reader']).read_text()]
(P/'KICH-BAN-HIEN-CO.md').write_text('\n'.join(lines)+'\n');progress={'total_in_scope':len(m),'updated_current_scripts':len(ready),'not_yet_updated':len(m)-len(ready),'media_created_this_batch':False,'protected_untouched_groups':{'already_media_video':140,'done_entries':116,'covered_aliases_without_job':9},'reader':'KICH-BAN-HIEN-CO.md','user_approval_new_scripts_recorded':False};(P/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
