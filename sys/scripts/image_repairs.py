"""Bounded, artifact-bound image repairs. History is append-only; prompts are snapshots."""
import json
import re
import uuid

from pilot import Blocked, digest, read, write

MAX_REPAIRS = 6
SAME_ISSUE_LIMIT = 2


def history(p, job, target):
    with p._db_lock:
        rows = p.db.execute('SELECT e.id,e.note,d.plan FROM image_edits e LEFT JOIN image_repair_details d '
                            'ON d.edit_id=e.id WHERE e.job=? AND e.target=? ORDER BY e.id', (job, target)).fetchall()
    return [dict(id=r['id'], note=r['note'], plan=json.loads(r['plan']) if r['plan'] else None) for r in rows]


def active(p, job, unit, target):
    """New repairs are expanded to exact units; old scene journals stay read-only."""
    records = history(p, job, target)
    if unit:
        records += history(p, job, unit.get('scene_id', target)) if unit.get('scene_id') != target else []
    if not records:
        return ''
    latest = max(records, key=lambda x: x['id'])
    if not latest['plan']:
        return latest['note'].strip()
    plan = latest['plan']
    instructions = list(dict.fromkeys(i['instruction'].strip() for i in plan['issues'] if i['status'] != 'resolved'))
    strategy = plan['strategy']
    if strategy:
        instructions.append('Visual direction: ' + json.dumps(strategy, ensure_ascii=False, sort_keys=True))
    return '\n'.join(instructions)


def stop(p, job, target, reason, detail=None, code='M2_REPAIR_NEEDS_ATTENTION'):
    report = p.job(job) / 'repair-stops' / (uuid.uuid4().hex + '.json')
    write(report, {'state': 'needs_attention', 'target': target, 'reason': reason,
                   'history': history(p, job, target) if detail is None else detail})
    p.event(job, 'images', 'repair_needs_attention', str(report.relative_to(p.job(job))))
    raise Blocked(f'{code}: {reason}; {report}')


def attention(p, job):
    # A human lift (workflow.lift_cap) clears every older stop; per-target limits re-check on the next reject.
    with p._db_lock:
        rows = p.db.execute("SELECT event,detail FROM events WHERE job=? AND ((module='images' AND "
                            "event IN ('repair_needs_attention','image_revision_requested')) OR event='loop_cap_lifted') "
                            "ORDER BY id DESC", (job,)).fetchall()
    cleared = set()
    for row in rows:
        if row['event'] == 'loop_cap_lifted':
            return None
        if row['event'] == 'image_revision_requested':
            data=json.loads(row['detail']);cleared.update(data.get('targets', [data.get('target')]))
        elif read(p.path(job,row['detail']))['target'] not in cleared:
            return row['detail']
    return None


def repeat_failures(p, job, n, after=0):
    """Machine-review criteria that failed in each of the last n completed media reviews.

    Ordered by when response.json was written; reviews without a parseable
    response (crashed/running) are skipped, and anything before `after` (the
    last human lift) is ignored. A passing review breaks every streak.
    """
    done = []
    for response in (p.job(job) / 'machine-reviews').glob('*/response.json'):
        try:
            when = response.stat().st_mtime
            if when <= after or read(response.parent / 'request.json').get('stage') != 'media':
                continue
            checks = read(response)['structured_output']['checks']
            done.append((when, response.parent.name, {k for k, v in checks.items() if v.get('verdict') != 'pass'}))
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
    last = sorted(done, key=lambda x: x[:2])[-n:] if n > 0 else []
    if len(last) < n or not last:
        return [], []
    common = sorted(set.intersection(*(x[2] for x in last)))
    return (common, [x[1] for x in last]) if common else ([], [])


def validate_plan(p, job, target, item, note, supplied):
    records = history(p, job, target)
    if len(records) >= MAX_REPAIRS:
        stop(p, job, target, 'Đã đạt giới hạn 6 lượt sửa ảnh; cần chẩn đoán, không tự tạo tiếp')
    current_hash = digest(p.path(job, item['path']))
    prior = records[-1]['plan'] if records else None
    if supplied is None:
        if records:
            stop(p, job, target, 'Lượt sửa tiếp theo cần --repair-plan với đối chiếu ảnh và lỗi cụ thể')
        supplied = {'current_sha256': current_hash, 'previous_sha256': None, 'strategy': {},
                    'issues': [{'id': 'visual', 'status': 'new', 'evidence': note, 'instruction': note}]}
    plan = json.loads(json.dumps(supplied))
    if not isinstance(plan,dict) or set(plan) != {'current_sha256', 'previous_sha256', 'strategy', 'issues'}:
        raise Blocked('M2_REPAIR_PLAN: cần current_sha256, previous_sha256, strategy, issues')
    expected_previous = prior['current_sha256'] if prior else None
    if plan['current_sha256'] != current_hash or plan['previous_sha256'] != expected_previous:
        raise Blocked('M2_REPAIR_PLAN: hash ảnh đối chiếu không khớp lịch sử và artifact hiện tại')
    strategy = plan['strategy']
    if (not isinstance(strategy, dict) or set(strategy) - {'pose', 'composition'} or
            any(not isinstance(v, str) or not v.strip() for v in strategy.values())):
        raise Blocked('M2_REPAIR_PLAN: strategy chỉ chứa pose/composition cụ thể, không rỗng')
    if not isinstance(plan['issues'], list) or not plan['issues']:
        raise Blocked('M2_REPAIR_PLAN: cần danh sách lỗi cụ thể')
    seen = set()
    prior_open = {i['id'] for i in prior['issues'] if i['status'] != 'resolved'} if prior else set()
    for issue in plan['issues']:
        if (not isinstance(issue, dict) or set(issue) != {'id', 'status', 'evidence', 'instruction'} or
                not isinstance(issue['id'], str) or not re.fullmatch(r'[a-z0-9_-]+', issue['id']) or
                issue['id'] in seen or issue['status'] not in ('new', 'remaining', 'resolved') or
                not isinstance(issue['evidence'], str) or not issue['evidence'].strip() or
                not isinstance(issue['instruction'], str) or
                (issue['status'] != 'resolved' and not issue['instruction'].strip())):
            raise Blocked('M2_REPAIR_PLAN: mỗi lỗi cần id duy nhất, status, evidence và instruction')
        seen.add(issue['id'])
        issue['instruction'] = ' '.join(issue['instruction'].split())
        if issue['status'] == 'new' and issue['id'] in prior_open:
            raise Blocked('M2_REPAIR_PLAN: lỗi còn tồn tại phải giữ id và status remaining')
        if issue['status'] in ('remaining', 'resolved') and issue['id'] not in prior_open:
            raise Blocked('M2_REPAIR_PLAN: lỗi remaining/resolved phải có trong lượt trước')
        count = sum(any(i['id'] == issue['id'] and i['status'] != 'resolved' for i in r['plan']['issues'])
                    for r in records if r['plan'])
        if issue['status'] != 'resolved' and count >= SAME_ISSUE_LIMIT:
            if not strategy or strategy == (prior or {}).get('strategy', {}):
                stop(p, job, target, 'Lỗi lặp hai lần: cần thay đổi tư thế/bố cục cụ thể; thêm câu cấm không đủ')
    if not prior_open <= seen:
        raise Blocked('M2_REPAIR_PLAN: phải ghi rõ resolved/remaining cho mọi lỗi đang mở')
    if all(i['status'] == 'resolved' for i in plan['issues']):
        raise Blocked('M2_REPAIR_NO_CHANGE: mọi lỗi đã hết; hãy đánh giá media, không sinh lại')
    if prior and current_hash == prior['current_sha256'] and any(i['status'] == 'resolved' for i in plan['issues']):
        raise Blocked('M2_REPAIR_PLAN: ảnh không đổi; không thể ghi lỗi đã được sửa')
    if prior:
        effective = lambda x: {'strategy': x['strategy'], 'instructions': sorted(set(
            i['instruction'].strip() for i in x['issues'] if i['status'] != 'resolved'))}
        if effective(plan) == effective(prior):
            stop(p, job, target, 'Yêu cầu sửa không thay đổi; không gửi lại cùng cách làm')
    plan['artifact'] = {'path': item['path'], 'sha256': current_hash, 'request': item.get('request')}
    plan['progress'] = {'resolved': [i['id'] for i in plan['issues'] if i['status'] == 'resolved'],
                        'remaining': [i['id'] for i in plan['issues'] if i['status'] == 'remaining'],
                        'new': [i['id'] for i in plan['issues'] if i['status'] == 'new'],
                        'same_pixels': bool(prior and current_hash == prior['current_sha256'])}
    return plan


def comparisons(p, job):
    """Actual before/after files for the existing media review, never a new gate."""
    result = []
    payload = p.payload(job, 'images')
    for item in payload['items'] + payload['references']:
        target = 'ref:'+item['character_id'] if item.get('character_id') else item.get('image_id', item['scene_id'])
        if item.get('image_id'):
            target += '_' + item['ratio'].replace(':', 'x')
        records = history(p, job, target)
        if not records or not records[-1]['plan']:
            continue
        plan = records[-1]['plan']
        before = plan['artifact']
        if digest(p.path(job,before['path'])) != before['sha256']:
            raise Blocked('M2_REPAIR_EVIDENCE: ảnh trước đã thay đổi, không thể đối chiếu')
        result.append({'target': target, 'before': before,
                       'after': {'path': item['path'], 'sha256': digest(p.path(job, item['path']))},
                       'issues': plan['issues'], 'strategy': plan['strategy']})
    return result


def status(p, job, image=None, ratio=None):
    p.validate(job,'images')
    result=[]
    for item in p.payload(job,'images')['items']:
        image_id=item.get('image_id',item['scene_id'])
        if (image and image_id != image) or (ratio and item.get('ratio') != ratio):
            continue
        target=image_id + ('_'+item['ratio'].replace(':','x') if item.get('image_id') else '')
        records=history(p,job,target)
        prior=records[-1]['plan'] if records else None
        result.append({'image':image_id,'ratio':item.get('ratio'),'target':target,
                       'current_path':str(p.path(job,item['path'])), 'current_sha256':digest(p.path(job,item['path'])),
                       'previous_sha256':prior['current_sha256'] if prior else None,
                       'repairs_used':len(records),'repair_limit':MAX_REPAIRS,
                       'previous_plan':prior})
    if not result:
        raise Blocked('M2_REPAIR_SCOPE: không tìm thấy ảnh/tỷ lệ')
    return {'job':job,'images':result,'needs_attention':attention(p,job)}
