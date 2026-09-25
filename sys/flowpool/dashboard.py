"""Data behind the FlowPool dashboard (served by daemon.mjs): profiles, queue,
gallery, and the user's pick/regenerate decisions. Labels are Vietnamese."""
from pathlib import Path

from .decisions import Decisions
from .journal import UNRESOLVED

# What the user must do, per profile state / error code.
ACTIONS = {
    'captcha': 'Giải CAPTCHA trong {name} (tool không tự giải), rồi chạy: python3 -m flowpool doctor',
    'needs_login': '{name} bị đăng xuất hoặc sai tài khoản: người dùng tự đăng nhập lại trong Chrome, rồi chạy doctor',
    'low_credit': '{name} đã dùng hết credit tháng này; clip sẽ chuyển sang profile khác',
    'cooldown': '{name} đang tạm nghỉ; nếu lý do là RECONCILE_REQUIRED thì kiểm tra Flow rồi chạy flowpool reconcile/mark',
    'NEEDS_ALLOW': 'Bấm "Allow" trong Chrome rồi chạy: python3 -m flowpool daemon reconnect',
    'NOT_CONNECTED': 'Bấm "Allow" trong Chrome rồi chạy: python3 -m flowpool daemon reconnect',
    'NO_DAEMON': 'Chạy: python3 -m flowpool daemon start',
    'PROFILE_TAB_NOT_FOUND': 'Mở tab của profile: python3 -m flowpool open-profile "{name}"',
    'PROFILE_MISMATCH': 'Tab của {name} đang hiện tài khoản khác: kiểm tra lại cửa sổ Chrome của profile này',
    'CAPTCHA': 'Giải CAPTCHA trong {name} (tool không tự giải), rồi chạy: python3 -m flowpool doctor',
    'NEEDS_LOGIN': '{name} bị đăng xuất: người dùng tự đăng nhập lại trong Chrome',
}
STATE_LABELS = {'intent': 'chờ gửi', 'not_submitted': 'chưa gửi', 'submitted': 'đang tạo', 'unknown': 'chưa rõ kết quả',
                'collected': 'đã tải về', 'validated': 'đã kiểm tra', 'failed': 'lỗi', 'released': 'đã giải phóng'}


def action_for(name, state=None, code=None):
    for k in (code, state):
        if k and k in ACTIONS:
            return ACTIONS[k].format(name=name)
    return None


def _decisions(fp):
    return Decisions(fp.dir / 'decisions.ndjson')


def ui_state(fp, limit=200):
    status = fp.status(locate=False)
    pool = fp.pool()
    for row in status['profiles']:
        p = pool.get(row['profile'])
        row['action'] = action_for(row['profile'], row['state'], (row.get('reason') or '').split(':')[0])
        row['project_url'] = p.get('project_url')
    decisions = _decisions(fp)
    queue, gallery = [], []
    snaps = sorted(fp.journal.all(), key=lambda s: s['events'][-1]['at'], reverse=True)[:limit]
    for s in snaps:
        req = s.get('request') or {}
        times = {}
        for e in s['events']:
            times.setdefault(e['state'], e['at'])
        queue.append({'key': s['key'], 'id': req.get('id'), 'kind': req.get('kind'), 'job': req.get('job'),
                      'scene': req.get('scene'), 'state': s['state'], 'label': STATE_LABELS.get(s['state'], s['state']),
                      'profile': s.get('profile'), 'times': times, 'code': s.get('code'), 'error': s.get('error'),
                      'needs_attention': s['state'] in UNRESOLVED + ('failed',)})
        if s['state'] not in ('collected', 'validated'):
            continue
        ranking = next((e.get('ranking') for e in reversed(s['events']) if e.get('ranking')), None) or []
        scores = {r['path']: r for r in ranking}
        best = ranking[0]['path'] if ranking else None
        pick = decisions.latest('pick', request_id=req.get('id'), key=s['key'])
        profile = s.get('profile')
        project = pool.get(profile).get('project_url') if profile and any(p['name'] == profile for p in pool.data['profiles']) else None
        gallery.append({
            'key': s['key'], 'id': req.get('id'), 'kind': req.get('kind'), 'job': req.get('job'), 'scene': req.get('scene'),
            'prompt': req.get('prompt'), 'profile': profile, 'open_in_flow': project,
            'variants': [{'index': i, 'path': o['path'], 'media_id': o.get('media_id'), 'score': scores.get(o['path'], {}).get('score'),
                          'checks': scores.get(o['path'], {}).get('checks'), 'best': o['path'] == best,
                          'picked': bool(pick and pick.get('file') == o['path'])}
                         for i, o in enumerate(s.get('outputs') or [])],
            'regenerate_requested': bool(decisions.latest('regenerate', request_id=req.get('id'), key=s['key'])),
        })
    return {'status': status, 'queue': queue, 'gallery': gallery,
            'decisions': decisions.all()[-50:]}


def decide(fp, kind, key, index=None, note=None):
    snaps = [s for s in fp.journal.all() if s['key'].startswith(key)]
    if len(snaps) != 1:
        raise ValueError(f'DECISION_TARGET: {len(snaps)} requests match {key!r}')
    s = snaps[0]
    req = s.get('request') or {}
    file = None
    if kind == 'pick':
        outputs = s.get('outputs') or []
        if index is None or not 0 <= index < len(outputs):
            raise ValueError(f'DECISION_INDEX: {req.get("id")} has {len(outputs)} variants')
        file = outputs[index]['path']
    entry = _decisions(fp).record(kind, s['key'], req.get('id'), req.get('job'), req.get('scene'), index, file, note)
    out = {'ok': True, 'decision': entry}
    if kind == 'regenerate' and req.get('job'):
        # Pipeline images are regenerated through the review workflow, never behind its back.
        target = req.get('target') or '<IMAGE_ID>'
        image, ratio = target, None
        for sfx, r in (('_16x9', '16:9'), ('_9x16', '9:16')):
            if target.endswith(sfx):
                image, ratio = target[:-len(sfx)], r
        out['next'] = (f'python3 pilot.py reject {req["job"]} media --image {image}' + (f' --ratio {ratio}' if ratio else '')
                       + f' --note "{(note or "tạo lại").replace(chr(34), "")}"')
    elif kind == 'pick' and req.get('job'):
        out['next'] = 'Bản chọn được dùng khi media chạy lại; duyệt media vẫn qua pilot.py.'
    return out
