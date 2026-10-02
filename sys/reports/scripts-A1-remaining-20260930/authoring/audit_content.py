import json,hashlib,re,collections
from source_utils import ROOT,OUT,ENTRIES,records,model_indices,quotes,contains_target,practice_quotes
recs=records();assert len(recs)==331
ledger=json.loads((ROOT/'vocab/ledger.json').read_text())['entries'];checks=[]
for n,rec in sorted(recs.items()):
 e=ENTRIES[n];j=ROOT/'runs'/e['job'];c=json.loads((j/'draft/content.json').read_text());meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text())
 assert ledger[e['id']]['job']==e['job'],n
 assert c['brief_revision']==meta['revision'] and c['brief_hash']==meta['hash'],n
 assert c['duration']==b['duration'] and len(c['scenes'])==e['scene_count'],n
 assert [s['narration'] for s in c['scenes']]==[r[0] for r in rec['rows']],n
 chars={ch['id'] for ch in c['characters']};assert 'CH01' in chars,n
 for i,s in enumerate(c['scenes']):
  assert 'CH01' in s['character_ids'] and set(s['character_ids'])<=chars,n
  assert len(s['beats'])==len(s['images']) and len(s['images']) in [1,2],n
  assert s['audio_direction']['vi']['learner_pause_seconds']>0 if i==len(c['scenes'])-2 else s['audio_direction']['vi']['learner_pause_seconds']==0,n
  for beat in s['beats']:assert beat['anchor']['vi']['quote'] in s['narration'],(n,s['id'])
  for im in s['images']:
   assert 'reference-v1.png' in c['characters'][0]['appearance'],n
   if im['based_on']:assert im['based_on']==s['images'][0]['id'],n
   for v in im['visible_text']:
    assert v['text'].casefold() in s['narration'].casefold() or v['text'].lower()==e['teaching_form'].lower(),(n,s['id'],v['text'])
  assert not re.search(r'\b(?:WAV|TTS|render|CH01)\b',s['narration']),n
 for cv in c['coverage']:
  sc=next(s for s in c['scenes'] if s['id']==cv['scene_id']);assert cv['quote'] in sc['narration'],n
 assert {x['requirement_id'] for x in c['coverage']}=={r['id'] for r in b['required_points']},n
 models=[quotes(c['scenes'][i]['narration'])[0] for i in model_indices(e['scene_count'])];assert all(contains_target(x,e) for x in models),n
 pract=practice_quotes(c['scenes'][-2]['narration']);assert pract,n
 # Blank-completion and choices are retained; the last scene provides literal response or model.
 assert quotes(c['scenes'][-1]['narration']),n
 checks.append({'number':n,'job':e['job'],'source_matches_draft':True,'brief_matches_current':True,'ledger_matches_bank_id':True,'literal_anchors_valid':True,'coverage_complete':True,'practice_and_feedback_present':True,'draft_sha256':hashlib.sha256((j/'draft/content.json').read_bytes()).hexdigest()})
(OUT/'content-audit.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(checks),'drafts: source, brief, bank reservation, literal anchors, coverage, permitted text, practice and feedback')
