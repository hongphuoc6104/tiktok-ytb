"""Branch-local topic and evidence gate, plugged into Pilot's existing policy hook."""
from pathlib import Path
import hashlib
import json
from research import bank

def topic_id_from(brief):
    tags=[s[len(bank.TAG):] for s in brief.get('planning',{}).get('domain_requirements',[]) if s.startswith(bank.TAG)]
    if len(tags)!=1:raise ValueError('Research job cần đúng một mã kho; dùng research/bank.py reserve → prepare → start')
    return tags[0]

def check(root,job,brief):
    from pilot import Blocked
    tags=brief.get('planning',{}).get('domain_requirements',[])
    if not brief.get('video_type','').startswith('research-') and not any(x.startswith(bank.TAG) for x in tags):
        return  # Non-research fixtures and legacy generic briefs remain topic-independent.
    try:
        i=topic_id_from(brief);t=bank.topic(i,root);owner,record=bank.owned(job,root)
        if owner!=i:raise ValueError('Đề tài đang thuộc job khác')
        if record['status']=='done':raise ValueError('Đề tài đã hoàn tất; không tạo lại hoặc sửa brief lịch sử')
        if brief['topic']!=t['title']:raise ValueError('Không đổi đề tài sau khi giữ chỗ')
        e=bank.read(Path(root)/'research/prepared'/job/'evidence.json');bank.validate_evidence(t,e)
        stamp=hashlib.sha256(json.dumps(e,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        tags=brief['planning']['domain_requirements']
        if 'research-evidence:'+stamp not in tags:raise ValueError('Nguồn thay đổi sau prepare; cần chuẩn bị revision có kiểm soát')
        if brief['sources']!=e['sources'] or not brief['facts_required']:raise ValueError('Nguồn trong brief không khớp bản đã kiểm chứng')
        if not 90<=brief['duration']['min_seconds']<=brief['duration']['max_seconds']<=180:raise ValueError('Video nghiên cứu phải dài 90–180 giây')
        from research.visuals import settings
        if settings(brief) is None:raise ValueError('Thiếu kế hoạch số hình/nhịp nghiên cứu')
    except (ValueError,KeyError,OSError) as ex:raise Blocked('RESEARCH_POLICY: '+str(ex)) from ex
