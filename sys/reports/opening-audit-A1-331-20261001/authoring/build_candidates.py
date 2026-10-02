from pathlib import Path
import json,copy,re,sys,hashlib,collections
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/opening-audit-A1-331-20261001'
sys.path.insert(0,str(ROOT));from scripts.story_plan import estimates
b=json.loads((OUT/'baseline.json').read_text());hooks={}
for f in sorted((OUT/'authoring').glob('hooks-*.txt')):
 for l in f.read_text().splitlines():
  n,family,hook,frame=l.split('|');n=int(n);assert n not in hooks
  hooks[n]={'family':family,'hook':hook,'frame':frame}
assert set(hooks)=={x['number'] for x in b};audit=[];manifest=[]
(OUT/'candidates').mkdir(exist_ok=True)
for x in b:
 e=x['entry'];n=x['number'];h=hooks[n];old=x['content'];sc=old['scenes'][0]
 first,rest=re.split(r'(?<=[.!?])\s+',sc['narration'],maxsplit=1)
 changed=h['hook']!='KEEP'
 c=copy.deepcopy(old)
 if changed:
  # Freeze complete new narration before any anchors or coverage are constructed.
  new_narration=h['hook']+' '+rest
  assert len(h['hook'].split())<=9,(n,h['hook'])
  old_quotes=[t for t in re.findall(r'"([^"]+)"',sc['narration'])]
  assert all(t in new_narration for t in old_quotes),n
  first_scene=c['scenes'][0];assert len(first_scene['images'])==1,n
  first_scene['narration']=new_narration
  first_scene['purpose']='Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.'
  first_scene['action']=h['frame']
  first_scene['camera']='Begin directly on the described revealing prop or consequential action with the mascot visible. Use one dominant referent, contextual close or medium shot as needed. No introductory card. Keep existing subtitle safe area and readable target label; actual opening timing requires WAV and video verification.'
  first_scene['images'][0]['description']=h['frame']+sc['images'][0]['description'][sc['images'][0]['description'].index(' Attach canonical Character reference'):]
  first_scene['images'][0]['change']=h['frame']
  first_scene['images'][0]['reason']='Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.'
  first_scene['beats'][0]['purpose']=first_scene['images'][0]['reason']
  first_scene['beats'][0]['anchor']['vi']={'quote':new_narration,'occurrence':1}
  c['outline'][0]['purpose']=first_scene['purpose']
  c['outline'][0]['transition']='The opening makes this need explicit: '+h['frame']+' Continue with the existing connected model: '+c['scenes'][1]['action']
  for cv in c['coverage']:
   if cv['scene_id']==first_scene['id']:cv['quote']=new_narration
  # All downstream narrative models, practice, pause and resolution remain literal.
  assert c['scenes'][1:]==old['scenes'][1:],n
  c['revision_response']=[] # populated only after real CLI rejection feedback exists
 else:new_narration=sc['narration']
 j=ROOT/'runs'/e['job'];meta=json.loads((j/'brief-current.json').read_text());brief=json.loads((j/f"briefs/{meta['revision']}.json").read_text())
 assert old['brief_revision']==meta['revision'] and old['brief_hash']==meta['hash'],n
 est=estimates(brief,c);seconds=round(sum(s['seconds'] for s in est['languages']['vi']['scenes']),1)
 chosen=h['hook'] if changed else first
 units=len(chosen.split());opening_est=round(units/brief['planning']['speech_rates']['vi']['units_per_second']+.15*len(re.findall(r'[.!?;,]',chosen)),2)
 for cv in c['coverage']:
  scene=next(s for s in c['scenes'] if s['id']==cv['scene_id']);assert cv['quote'] in scene['narration'],n
 for s in c['scenes']:
  for beat in s['beats']:assert beat['anchor']['vi']['quote'] in s['narration'],n
  for image in s['images']:
   for vt in image['visible_text']:assert vt['text'].casefold() in s['narration'].casefold() or vt['text'].casefold()==e['teaching_form'].casefold(),(n,vt['text'])
 (OUT/'candidates'/f'{n}.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 audit.append({'number':n,'word':e['teaching_form'],'job':e['job'],'decision':'rewrite' if changed else 'keep','old_opening':first,'new_opening':chosen,'opening_type':h['family'] if changed else 'Mở đầu cũ đã rõ tình huống và có điểm chú ý','first_frame':first_scene['action'] if changed else sc['action'],'payoff_scene':old['scenes'][-1]['id'],'payoff_narration':old['scenes'][-1]['narration'],'why':'Rút câu dẫn vào một điểm cụ thể; đưa trở ngại, chi tiết hay hoặc lời cần nói lên đầu, đổi bố cục cho thấy ngay điều đó; giảm nhịp hỏi dài rồi kể lại bối cảnh.' if changed else 'Đã có vấn đề hoặc đối chiếu cụ thể từ đầu; hình kế hoạch làm rõ và câu chuyện có phản hồi/kết quả. Không sửa chỉ để đổi chữ.','estimated_opening_seconds':opening_est,'opening_units':units,'estimated_total_seconds':seconds,'original_estimated_total_seconds':e['estimated_seconds'],'timing_evidence':'Ước tính theo tốc độ brief, chưa đo WAV','first_three_seconds_goal':'Point of interest is introduced at the start; full retained opening may exceed 3s. New hooks fit approximately 3s under brief estimate, no measured guarantee.','downstream_scenes_literal':True,'anchors_and_coverage_literal':True,'user_approval':False})
 manifest.append({**e,'changed':changed,'opening':chosen,'opening_type':audit[-1]['opening_type'],'estimated_seconds':seconds,'estimate_range_seconds':[est['languages']['vi']['min'],est['languages']['vi']['max']],'state':'candidate','content_revision':None,'candidate_sha256':hashlib.sha256((OUT/'candidates'/f'{n}.json').read_bytes()).hexdigest()})
assert len({x['new_opening'].casefold() for x in audit})==331
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(OUT/'frozen-hooks.json').write_text(json.dumps(hooks,ensure_ascii=False,indent=2)+'\n')
print('Reviewed',len(audit),'rewrite',sum(x['decision']=='rewrite' for x in audit),'keep',sum(x['decision']=='keep' for x in audit))
print('New opening estimate min/max',min(x['estimated_opening_seconds'] for x in audit if x['decision']=='rewrite'),max(x['estimated_opening_seconds'] for x in audit if x['decision']=='rewrite'))
print('Below/above brief point estimates',[(x['number'],x['estimated_total_seconds']) for x in audit if not next(y['content']['duration']['min_seconds']<=x['estimated_total_seconds']<=y['content']['duration']['max_seconds'] for y in b if y['number']==x['number'])])
print('Opening types',dict(collections.Counter(x['opening_type'] for x in audit)))
