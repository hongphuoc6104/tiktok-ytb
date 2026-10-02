import sys,json,re,collections
from source_utils import ROOT,OUT,ENTRIES,records,quotes,contains_target,model_indices,pause_for
sys.path.insert(0,str(ROOT))
from scripts.story_plan import estimates

recs=records();checks=[]
for n,rec in sorted(recs.items()):
    e=ENTRIES[n]
    models=[quotes(rec['rows'][i][0])[0] for i in model_indices(e['scene_count'])]
    assert models[0]!=models[1],(n,models)
    assert all(contains_target(x,e) for x in models),(n,e['teaching_form'],models)
    assert not re.search(r'\bi\b',' '.join(models)),n
    root=ROOT/'runs'/e['job'];meta=json.loads((root/'brief-current.json').read_text());b=json.loads((root/f"briefs/{meta['revision']}.json").read_text())
    pause=pause_for(rec)
    # Counts represent planned images only; this object is used for arithmetic,
    # never as a product or as evidence of audio, images or word alignment.
    c={'scenes':[{'id':f'SC{i+1:02}','narration':r[0], 'beats':[{}]*(2 if ' => ' in r[1] else 1),
                 'audio_direction':{'vi':{'learner_pause_seconds':pause if i==len(rec['rows'])-2 else 0}}}
                 for i,r in enumerate(rec['rows'])]}
    est=estimates(b,c);seconds=round(sum(x['seconds'] for x in est['languages']['vi']['scenes']),1)
    checks.append({'number':n,'job':e['job'],'models':models,'scene_count':len(rec['rows']),'planned_images':sum(len(s['beats']) for s in c['scenes']),
                   'practice_pause_seconds':pause,'estimated_seconds':seconds,'duration':b['duration'],
                   'point_estimate_outside_brief':not b['duration']['min_seconds']<=seconds<=b['duration']['max_seconds']})
(OUT/'source-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
(OUT/'authored-scripts.json').write_text(json.dumps(list(recs.values()),ensure_ascii=False,indent=2)+'\n')
print('Checked',len(checks),'authored scripts;',sum(x['scene_count'] for x in checks),'scenes;',sum(x['planned_images'] for x in checks),'planned images')
print('Estimate range',min(x['estimated_seconds'] for x in checks),max(x['estimated_seconds'] for x in checks))
print('Outside point estimate:',[(x['number'],x['estimated_seconds']) for x in checks if x['point_estimate_outside_brief']])
