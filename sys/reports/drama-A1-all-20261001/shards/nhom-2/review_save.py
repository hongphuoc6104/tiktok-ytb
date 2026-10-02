import json,pathlib,sys,re,os
base=pathlib.Path('/home/hongphuoc6104/Desktop/pipelineFlow/sys/reports/drama-A1-all-20261001');own=base/'shards/nhom-2'
p=pathlib.Path(sys.argv[1]);d=json.loads(p.read_text());es=d.get('structured_output',d)['episodes'];jobs=set(json.load(open(base/'shard-assignments/nhom-2.json'))['jobs']);m={x['job']:x for x in json.load(open(base/'manifest.json'))}
for e in es:
 assert e['job'] in jobs
 assert len(e['scenes'])==m[e['job']]['scene_count']
 assert [s['scene_id'] for s in e['scenes']]==[f'SC{i+1:02}' for i in range(len(e['scenes']))]
 assert e['characters'][0]['id']=='CH01'
 narration=' '.join(s['narration'] for s in e['scenes'])
 assert len(e['scenes'][0]['narration'].split('.')[0].split())<=9, e['job']
 ps=[i for i,s in enumerate(e['scenes']) if s.get('practice_pause_seconds',0)>0]
 assert len(ps)==1 and ps[0]<len(e['scenes'])-1
 s=e['scenes'][ps[0]];assert 3<=s['practice_pause_seconds']<=5 and '___' in s.get('stem','')
 for s in e['scenes']:
  assert s.get('visual_en') and s.get('purpose_en')
  for q in s.get('extra_visual_states',[]):assert q['quote'] in s['narration']
 e['editorial_review']='Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.'
 e['visual_review_ready']=True
 dst=base/'narration-frozen'/f"{e['job']}.json";tmp=dst.with_suffix('.json.tmp.nhom2');tmp.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,dst)
progress={'finished':[j for j in json.load(open(base/'shard-assignments/nhom-2.json'))['jobs'] if (base/'narration-frozen'/f'{j}.json').exists()]};progress['count']=len(progress['finished']);(own/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
print(progress['count'])
