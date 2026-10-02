from pathlib import Path
import json,sys,re,os
P=Path(__file__).resolve().parent
OUT=P.parents[1]
M={e['job']:e for e in json.loads((OUT/'manifest.json').read_text())}
batch=P/sys.argv[1]
source=batch/'edited.json'
if not source.exists():source=batch/'episodes.json'
episodes=json.loads(source.read_text())['episodes']
for e in episodes:
 m=M[e['job']];n=' '.join(s['narration'] for s in e['scenes']);pr=[s for s in e['scenes'] if s['practice_pause_seconds']]
 if sys.argv[2]=='preview':
  print('\n',e['job'],m.get('selected_gloss_vi',m['gloss_vi']),len(n.split()),e['title'])
  print('PLOT',e['plot_vi']);print('CAST',json.dumps(e['characters'],ensure_ascii=False))
  for s in e['scenes']:print(s['scene_id'],s['narration'],'\nV:',s['visual_en'],'\nSTEM:',s.get('stem',''))
  print('EXTRA',json.dumps(e.get('extra_visual_states',[]),ensure_ascii=False))
 else:
  assert e['job'] in json.loads((OUT/'shard-assignments/nhom-3.json').read_text())['jobs']
  assert [s['scene_id'] for s in e['scenes']]==[f'SC{i:02}' for i in range(1,m['scene_count']+1)]
  assert len(pr)==1 and 3<=pr[0]['practice_pause_seconds']<=5
  s=pr[0];i=e['scenes'].index(s);assert i<len(e['scenes'])-1
  assert '___' in s.get('stem','')
  answer=s['stem'].replace('___',e.get('teaching_form',m['word']))
  assert answer.lower() in e['scenes'][i+1]['narration'].lower(),(e['job'],answer)
  assert not any('...' in x['narration'] or '…' in x['narration'] for x in e['scenes'])
  assert len(re.split(r'[.!?]',e['scenes'][0]['narration'])[0].split())<=9
  for x in e.get('extra_visual_states',[]):assert x['quote'] in n
  e['editorial_review']='Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.'
  e['visual_review_ready']=True
  target=OUT/'narration-frozen'/f"{e['job']}.json";assert not target.exists(),target
  tmp=target.with_suffix('.nhom-3.tmp');tmp.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,target)
  print('FROZEN',e['job'],len(n.split()))
if sys.argv[2]!='preview':(batch/'review-completed.json').write_text(json.dumps({'jobs':[e['job'] for e in episodes],'review':'Actual line-by-line review and repairs by authorized writing agent. Language, exact selected sense, causal story, full-sentence recall, next-scene answer, framing, cast continuity and brand core checked. No media evaluation performed.'},ensure_ascii=False,indent=2)+'\n')
