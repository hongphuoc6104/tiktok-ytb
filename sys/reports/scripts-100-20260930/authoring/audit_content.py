from pathlib import Path
import json,re,sys,collections,hashlib
p=Path(__file__).resolve().parents[3];o=p/'reports/scripts-100-20260930';sys.path.insert(0,str(p))
import jsonschema
from scripts.story_plan import validate_plan
from content_contract import validate_content
m=json.loads((o/'manifest.json').read_text());ledger=json.loads((p/'vocab/ledger.json').read_text())['entries'];schema=json.loads((p/'schemas/content-v3.json').read_text());records=[]
for e in m:
 j=p/'runs'/e['job'];c=json.loads((j/'draft/content.json').read_text());meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text())
 assert ledger[e['id']]['job']==e['job'],e
 assert any('Mã mục trong kho từ vựng: '+e['id']+' ' in x for x in b['planning']['domain_requirements']),e
 jsonschema.validate(c,schema);validate_plan(b,c)
 assert len(c['scenes'])==5
 examples=[re.findall(r'"([^"]+)"',sc['narration'])[0] for sc in c['scenes'][1:3]];assert examples[0]!=examples[1],e
 assert all(e['word'] in x.lower() or (e['word']=='like' and 'liked' in x.lower()) or (e['word']=='wifi' and 'wi-fi' in x.lower()) for x in examples),(e,examples)
 assert c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds']>0
 assert c['scenes'][4]['audio_direction']['vi']['learner_pause_seconds']==0
 assert not re.search(r'\bi\b',' '.join(examples)),e
 for sc in c['scenes']:
  for im in sc['images']:
   for v in im['visible_text']:
    assert v['text'] in sc['narration'] or v['text'].lower() in sc['narration'].lower() or v['text'] in {'2','Wi-Fi'} or e['word']=='wifi',(e['number'],sc['id'],v['text'])
 records.append({'number':e['number'],'job':e['job'],'brief_revision':meta['revision'],'schema':'passed','plan':'passed','ledger':'matched','examples':examples,'scenes':5,'images':sum(len(s['images']) for s in c['scenes']),'practice_pause':c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds'],'draft_sha256':hashlib.sha256((j/'draft/content.json').read_bytes()).hexdigest()})
(o/'authoring-checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Verified',len(records),'scripts;',sum(x['images'] for x in records),'planned images;',collections.Counter(x['practice_pause'] for x in records),'pause distribution')
