#!/usr/bin/env python3
"""Durable topic reservations. Production always enters through pilot.py CLI."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
TAG='research-topic:'

def read(path): return json.loads(Path(path).read_text())
def atomic(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def topics(root=ROOT):return [json.loads(x) for file in sorted((Path(root)/'research/topics').glob('*.jsonl')) for x in file.read_text().splitlines() if x.strip()]
def topic(topic_id,root=ROOT):
    for t in topics(root):
        if t['id']==topic_id:return t
    raise ValueError('Không có mã đề tài: '+topic_id)
def job_id(job):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',job):raise ValueError('Mã job không hợp lệ')
    return job
@contextlib.contextmanager
def locked(root=ROOT):
    base=Path(root)/'research'
    with (base/'.ledger.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        yield

def ledger(root=ROOT):return read(Path(root)/'research/ledger.json')
def save(data,root=ROOT):atomic(Path(root)/'research/ledger.json',data)
def event(data,action,job,topic_id,note=''):
    data['events'].append(dict(at=dt.datetime.now(dt.timezone.utc).isoformat(),action=action,job=job,topic_id=topic_id,note=note))
def available(root=ROOT,category=None):
    state=ledger(root)
    return sorted([t for t in topics(root) if t['id'] not in state['entries'] and (not category or t['category']==category)],key=lambda t:t['editorial_order'])
def reserve(job,topic_id=None,category=None,root=ROOT):
    job_id(job)
    with locked(root):
        data=ledger(root)
        existing=[(i,r) for i,r in data['entries'].items() if r['job']==job]
        if existing:
            i,r=existing[0]
            if topic_id and i!=topic_id:raise ValueError('Job đã giữ đề tài khác')
            if r['status']=='done':raise ValueError('Job đã hoàn tất')
            return topic(i,root)
        if (Path(root)/'runs'/job).exists():raise ValueError('Job đã tồn tại, không tự gán lại đề tài')
        choices=available(root,category)
        t=topic(topic_id,root) if topic_id else (choices[0] if choices else None)
        if not t:raise ValueError('Không còn đề tài phù hợp')
        if t['id'] in data['entries']:raise ValueError('Đề tài đã được giữ chỗ hoặc hoàn tất')
        data['entries'][t['id']]=dict(job=job,status='reserved',title=t['title'])
        event(data,'reserve',job,t['id']);save(data,root)
        return t

def owned(job,root=ROOT):
    job_id(job)
    pairs=[(i,r) for i,r in ledger(root)['entries'].items() if r['job']==job]
    if len(pairs)!=1:raise ValueError('Job chưa giữ đúng một đề tài')
    return pairs[0]

def release(job,note,root=ROOT):
    if not note.strip():raise ValueError('Cần lý do giải phóng')
    with locked(root):
        i,r=owned(job,root)
        if r['status']!='reserved' or (Path(root)/'runs'/job).exists():
            raise ValueError('Không giải phóng đề tài đã tạo job; giữ chỗ để tránh video trùng')
        data=ledger(root);del data['entries'][i];event(data,'release',job,i,note);save(data,root)

def validate_evidence(t,e,today=None):
    today=today or dt.date.today()
    if e.get('topic_id')!=t['id']:raise ValueError('Nguồn không thuộc đề tài')
    date=dt.date.fromisoformat(e['checked_on'])
    age=(today-date).days
    if age<0 or age>t['refresh_after_days']:raise ValueError('Nguồn đã quá hạn hoặc có ngày trong tương lai; kiểm tra lại')
    if not e.get('checked_by','').strip() or not e.get('verification_note','').strip():raise ValueError('Thiếu người/công cụ kiểm tra và ghi chú kiểm chứng')
    sources=e.get('sources',[])
    if not sources:raise ValueError('Cần nguồn với dữ kiện thực đã kiểm tra')
    ids=set()
    for s in sources:
        if s.get('id') in ids:raise ValueError('Trùng mã nguồn')
        ids.add(s.get('id'))
        for k in ('id','title','reference'):
            if not isinstance(s.get(k),str) or not s[k].strip():raise ValueError('Nguồn thiếu '+k)
        if not s['reference'].startswith('https://'):raise ValueError('Nguồn phải có liên kết HTTPS kiểm tra được')
        if not s.get('facts') or any(not isinstance(x,str) or not x.strip() for x in s['facts']):raise ValueError('Thiếu dữ kiện cụ thể; liên kết không thay cho fact-check')
    points=e.get('required_points',[])
    if not 3<=len(points)<=5 or any(not isinstance(x,str) or not x.strip() for x in points):raise ValueError('Cần 3–5 ý biên tập riêng cho đề tài')
    if not e.get('goal','').strip():raise ValueError('Thiếu mục tiêu cụ thể')
    return e

def brief(job,e,root=ROOT):
    i,r=owned(job,root);t=topic(i,root);validate_evidence(t,e)
    c=read(Path(root)/'research/channel.json')
    b=dict(schema_version='3.0',topic=t['title'],audience=c['audience'],goal=e['goal'],video_type='research-'+t['format'],duration=c['duration'],scene_count=c['scene_count'],language='vi',tone='Rõ ràng, gần gũi, chính xác; giải thích thuật ngữ bằng ví dụ, không thổi phồng',style=c['style'],aspect_ratio=c['aspect_ratio'],facts_required=True,sources=e['sources'],planning=dict(
        success_criteria=[e['goal'],'Người xem hiểu một vấn đề và biết một việc có thể làm tiếp'],
        avoid=['Không chuyển thành bài học từ vựng','Không bịa nguồn, số liệu, giao diện phần mềm hoặc trải nghiệm sử dụng','Không coi chỉ số tạp chí là bảo đảm chất lượng từng bài','Không mở rộng thành cả khóa học'],
        prior_knowledge='Người mới nghiên cứu; giải thích thuật ngữ cần dùng',
        pacing='90–180 giây. Mỗi hình có mục đích; 18–24 hình, 24–36 nhịp là mục tiêu biên tập. Đo lại bằng WAV, không cắt ý để ép thời lượng.',
        domain_requirements=[TAG+i,'research-evidence:'+hashlib.sha256(json.dumps(e,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'research-visuals:'+json.dumps(c['visuals'],sort_keys=True),'Kiểm chứng nguồn ngày '+e['checked_on']+'; '+e['verification_note'],'Phân biệt dữ kiện, suy luận và giới hạn; một ví dụ minh họa không phải dữ liệu thực nghiệm.'],
        assumptions=['Mặc định 9:16 tiếng Việt; 16:9/dual vẫn theo ngôn ngữ của pipeline hiện hành','Số hình và thời lượng dự kiến chưa phải bằng chứng chất lượng'],text_style=c['text_style'],speech_rates={'vi':dict(units_per_second=3.6,uncertainty=.25,source='initial estimate; verify actual WAV'),'en':dict(units_per_second=2.5,uncertainty=.25,source='initial estimate; verify actual WAV')}))
    b['required_points']=[dict(id=f'R{n:02}',text=x) for n,x in enumerate(e['required_points'],1)]
    from content_contract import validate_brief
    validate_brief(root,b)
    return b

def prepare(job,evidence,root=ROOT):
    # Lock covers record + generated input. Never holds it over child CLI invocation.
    with locked(root):
        i,r=owned(job,root)
        if (Path(root)/'runs'/job).exists():raise ValueError('Job đã tồn tại; sửa qua revise-brief/reject, không ghi đè')
        e=read(evidence);b=brief(job,e,root)
        folder=Path(root)/'research/prepared'/job
        if folder.exists():raise ValueError('Đã prepare; dùng start với bản đã lưu, hoặc reserve job mới')
        atomic(folder/'evidence.json',e);atomic(folder/'brief.json',b)
        return folder/'brief.json'

def start(job,mode='review',root=ROOT):
    owned(job,root)
    file=Path(root)/'research/prepared'/job/'brief.json'
    from research.policy import check
    check(root,job,read(file))
    if (Path(root)/'runs'/job).exists():
        raise ValueError('Job đã tồn tại: dùng pilot.py status/next/resume; không gửi tạo trùng')
    result=subprocess.run([sys.executable,str(Path(root)/'pilot.py'),'new',job,'--brief',str(file),'--mode',mode],cwd=root)
    if result.returncode:raise ValueError('Tạo job chưa thành công; giữ chỗ để kiểm tra trước khi thử lại')
    return {'job':job,'next':'pilot.py status / next / run','topic_id':owned(job,root)[0]}

def completion(job,root=ROOT):
    # Existing public decision verification; never manufacture approvals or write SQL.
    from pilot import Pilot
    import workflow
    if not (Path(root)/'runs'/job/'workflow.json').is_file():raise ValueError('Chưa có job v3')
    p=Pilot(root)
    try:
        p.integrity(job)
        if not workflow.status(p,job)['complete']:raise ValueError('Video chưa có quyết định hợp lệ cho cả ba phần')
        b=p.brief(job)[0]
        from research.policy import topic_id_from
        i=topic_id_from(b)
        p.validate(job,'render')
        return i,workflow.current(p,job,'video')['revision']
    finally:p.db.close()

def mark(job,root=ROOT):
    i,revision=completion(job,root)
    with locked(root):
        own,r=owned(job,root)
        if i!=own:raise ValueError('Đề tài của job không khớp kho')
        data=ledger(root)
        if r['status']=='done':return r
        data['entries'][i].update(status='done',video_revision=revision)
        event(data,'done',job,i);save(data,root);return data['entries'][i]

def status(root=ROOT):
    data=ledger(root); counts={x:0 for x in ['reserved','done']}
    for r in data['entries'].values():counts[r['status']]+=1
    return dict(total=len(topics(root)),available=len(available(root)),**counts)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    for name in ['status','audit']:sub.add_parser(name)
    n=sub.add_parser('next');n.add_argument('--count',type=int,default=10);n.add_argument('--category')
    s=sub.add_parser('show');s.add_argument('topic_id')
    r=sub.add_parser('reserve');r.add_argument('job');r.add_argument('--topic');r.add_argument('--category')
    e=sub.add_parser('prepare');e.add_argument('job');e.add_argument('--evidence',required=True)
    s=sub.add_parser('start');s.add_argument('job');s.add_argument('--mode',choices=['review','auto'],default='review')
    for name in ['mark','release']:
        a=sub.add_parser(name);a.add_argument('job')
        if name=='release':a.add_argument('--note',required=True)
    a=p.parse_args()
    try:
        if a.cmd=='status':out=status()
        elif a.cmd=='next':out=[{k:t[k] for k in ('id','title','category','priority')} for t in available(category=a.category)[:max(0,min(a.count,50))]]
        elif a.cmd=='show':
            out=topic(a.topic_id)
            registry=read(ROOT/'research/catalog/sources.json')['sources']
            out['source_leads']=[s for s in registry if s['id'] in out['source_ids']]
        elif a.cmd=='reserve':out=reserve(a.job,a.topic,a.category)
        elif a.cmd=='prepare':out={'brief':str(prepare(a.job,a.evidence))}
        elif a.cmd=='start':out=start(a.job,a.mode)
        elif a.cmd=='mark':out=mark(a.job)
        elif a.cmd=='release':out=release(a.job,a.note)
        else:
            rows=[]
            for i,r in ledger()['entries'].items():
                try:actual,rev=completion(r['job']);state='approved_ready_to_mark' if r['status']!='done' else 'done'
                except Exception as ex:state=str(ex)
                rows.append(dict(topic_id=i,job=r['job'],ledger_status=r['status'],check=state))
            out=rows
        print(json.dumps(out,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError) as ex:p.exit(1,str(ex)+'\n')
if __name__=='__main__':main()
