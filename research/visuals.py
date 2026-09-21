"""Explicit image budget carried by each brief; no topic assumptions in the renderer."""
import json
PREFIX='research-visuals:'
def settings(b):
    tags=[x[len(PREFIX):] for x in b.get('planning',{}).get('domain_requirements',[]) if x.startswith(PREFIX)]
    if not tags:return None
    if len(tags)!=1:raise ValueError('Duplicate research visual settings')
    d=json.loads(tags[0])
    for lo,target,hi in [('min_images','target_images','max_images'),('min_beats','target_beats','max_beats')]:
        if not all(type(d.get(k)) is int for k in (lo,target,hi)) or not 1<=d[lo]<=d[target]<=d[hi]<=100:raise ValueError('Invalid visual budget')
    if type(d.get('min_images_per_scene')) is not int or not 1<=d['min_images_per_scene']<=10:raise ValueError('Invalid per-scene minimum')
    if not isinstance(d.get('readable_text_seconds'),(int,float)) or not 2.5<=d['readable_text_seconds']<=10:raise ValueError('Invalid text hold')
    return d

def validate(b,c):
    v=settings(b)
    if not v:return
    n=sum(len(s['images']) for s in c['scenes']);beats=sum(len(s['beats']) for s in c['scenes'])
    if not v['min_images']<=n<=v['max_images']:raise ValueError(f'Research needs {v["min_images"]}–{v["max_images"]} images; got {n}')
    if not v['min_beats']<=beats<=v['max_beats']:raise ValueError(f'Research needs {v["min_beats"]}–{v["max_beats"]} beats; got {beats}')
    if any(len(s['images'])<v['min_images_per_scene'] for s in c['scenes']):raise ValueError('Too few images in a research scene')

def timing_report(b,c,timings):
    v=settings(b)
    if not v:return None
    by_image={i['id']:i for s in c['scenes'] for i in s['images']}
    by_beat={bt['id']:bt for s in c['scenes'] for bt in s['beats']}
    warnings=[]
    for lang,scenes in timings.items():
        for s in scenes:
            beats=s.get('images',[])
            for n,bt in enumerate(beats):
                span=(beats[n+1]['at'] if n+1<len(beats) else s['end']-s['start'])-bt['at']
                im=by_image[by_beat[bt['id']]['image_id']]
                if im['visible_text'] and span<v['readable_text_seconds']:
                    warnings.append(dict(language=lang,beat=bt['id'],seconds=round(span,2),issue='Chữ có thể hiển thị quá nhanh; kiểm tra nghe/xem và sửa neo nếu cần'))
    return dict(status='needs_visual_review' if warnings else 'technical_timing_only',warnings=warnings,note='Nội suy theo WAV, không phải căn chỉnh từ chính xác; không tự duyệt chất lượng.')
