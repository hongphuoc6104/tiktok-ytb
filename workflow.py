"""Three public review gates; technical modules remain private implementation steps."""
import json
import time
from pathlib import Path

from pilot import Blocked, read, write, hashobj, digest

STAGES = {'content': ('content',), 'media': ('images', 'audio'), 'video': ('render',)}
LABELS = {'content': 'Kịch bản', 'media': 'Cảnh, hình ảnh và âm thanh', 'video': 'Video hoàn chỉnh'}


def settings(p, job):
    path = p.job(job) / 'workflow.json'
    if not path.exists():
        raise Blocked('LEGACY_JOB: lịch sử chỉ đọc; tạo job mới với --brief và --mode review hoặc auto')
    data = read(path)
    if data.get('version') != 3 or data.get('mode') not in ('review', 'auto'):
        raise Blocked('Invalid workflow settings')
    with p._db_lock:
        row = p.db.execute("SELECT detail FROM events WHERE job=? AND event='workflow_created' ORDER BY id LIMIT 1", (job,)).fetchone()
    if not row or row['detail'] != hashobj(data):
        raise Blocked('Workflow settings changed; job mode is immutable')
    return data


def new(p, job, brief, mode='review'):
    if brief is None or mode not in ('review', 'auto'):
        raise Blocked('New jobs require --brief and mode review/auto')
    p.new(job, brief)
    data = {'version': 3, 'mode': mode, 'created_at': time.time()}
    write(p.job(job) / 'workflow.json', data)
    p.event(job, 'control', 'workflow_created', hashobj(data))
    accept_module(p, job, 'control')
    return status(p, job)


def accept_module(p, job, module):
    """Technical acceptance is never represented as a human quality decision."""
    row = p.rows(job)[module]
    checkpoint = p.payload(job, module).get('checkpoint') if module == 'images' else None
    p.approve(job, module, row['revision'], 'Validated internal step', checkpoint, actor='technical')


def snapshot(p, job, stage):
    rows = p.rows(job)
    modules = ('content',) if stage == 'content' else ('content', 'images', 'audio')
    if stage == 'video':
        modules += ('render',)
    return {'settings': hashobj(settings(p, job)), 'modules': {
        m: {'revision': rows[m]['revision'], 'hash': rows[m]['hash']} for m in modules}}


def latest(p, job, stage):
    folder = p.job(job) / 'reviews' / stage
    files = list(folder.glob('*/manifest.json'))
    return read(max(files, key=lambda x: int(x.parent.name))) if files else None


def current(p, job, stage):
    data = latest(p, job, stage)
    if not data or data['snapshot'] != snapshot(p, job, stage):
        return None
    rows = p.rows(job)
    if any(rows[m]['state'] not in ('awaiting_review', 'approved') for m in data['snapshot']['modules']):
        return None
    return data


def approved(p, job, stage):
    data = current(p, job, stage)
    if not data:
        return False
    decision = p.path(job, data['decision'])
    if not decision.exists():
        return False
    result = read(decision)
    if result.get('approved') is not True or result.get('manifest_hash') != hashobj(data):
        return False
    if result.get('actor') == 'machine':
        report = p.path(job, result['report'])
        return report.is_file() and digest(report) == result.get('report_hash')
    return result.get('actor') == 'user'


def gate(p, job, module):
    # Low-level helpers cannot bypass the public gates on a v3 job.
    if not (p.job(job) / 'workflow.json').exists():
        return
    if module in ('images', 'audio', 'render') and not approved(p, job, 'content'):
        raise Blocked('Kịch bản chưa được duyệt theo chế độ của job')
    if module == 'render' and not approved(p, job, 'media'):
        raise Blocked('Hình ảnh và âm thanh chưa được duyệt cùng phiên bản')


def status(p, job):
    cfg = settings(p, job)
    try:
        p.status(job)
    except Blocked as ex:
        return {'job': job, 'mode': cfg['mode'], 'complete': False, 'blocked': str(ex)}
    stages = []
    for stage in STAGES:
        item = current(p, job, stage)
        stages.append({'stage': stage, 'label': LABELS[stage],
                       'state': 'approved' if approved(p, job, stage) else ('awaiting_review' if item else 'pending'),
                       'revision': item['revision'] if item else None,
                       'review': str(p.path(job, item['review'])) if item else None})
    return {'job': job, 'mode': cfg['mode'], 'complete': all(x['state'] == 'approved' for x in stages), 'stages': stages}


def next_step(p, job):
    state = status(p, job)
    if 'blocked' in state:
        return state
    for item in state['stages']:
        if item['state'] != 'approved':
            return {**item, 'mode': state['mode'], 'action':
                    ('machine_review' if state['mode'] == 'auto' else 'review')
                    if item['state'] == 'awaiting_review' else 'run_or_repair'}
    return {'action': 'complete', 'mode': state['mode']}


def assets(p, job, stage):
    """Files a semantic reviewer must actually inspect, not just existence-check."""
    files = []
    content_row = p.rows(job)['content']
    files.append(content_row['envelope'])
    if stage in ('media', 'video'):
        images = p.payload(job, 'images')
        files += [x['path'] for x in images['references'] + images['items']]
        for item in images['items']:
            for ref in item['references']:
                files.append(read(p.path(job, ref['registration_journal']))['path'])
        audio = p.payload(job, 'audio')
        files += [audio['wav'], audio['srt']]
        if audio.get('en'):
            files.append(audio['en']['wav'])
    if stage == 'video':
        video = p.payload(job, 'render')
        files += [video[k] for k in ('video', 'video_9x16', 'video_16x9') if video.get(k)]
    return list(dict.fromkeys(files))


def prepare(p, job, stage):
    p.refresh(job)
    if stage not in STAGES:
        raise Blocked('Chỉ có ba phần: content, media, video')
    for previous in STAGES:
        if previous == stage:
            break
        if not approved(p, job, previous):
            raise Blocked(f'{previous} chưa được duyệt')
    existing = current(p, job, stage)
    if existing:
        return existing
    for module in STAGES[stage]:
        while p.rows(job)[module]['state'] != 'approved':
            row = p.rows(job)[module]
            if row['state'] != 'awaiting_review':
                if module == 'content' and not (p.job(job) / 'draft/content.json').exists():
                    from scripts.agy_pipeline import generate
                    generate(p, job)
                else:
                    p.run(job, module)
            if module in ('images', 'audio'):
                accept_module(p, job, module)
            else:
                break
    for module in STAGES[stage]:
        p.validate(job, module)
    old = latest(p, job, stage)
    revision = old['revision'] + 1 if old else 1
    folder = p.job(job) / 'reviews' / stage / str(revision)
    folder.mkdir(parents=True, exist_ok=False)
    relative = lambda f: str(f.relative_to(p.job(job)))
    data = {'stage': stage, 'revision': revision, 'snapshot': snapshot(p, job, stage),
            'assets': assets(p, job, stage), 'review': relative(folder / 'review.md'),
            'decision': relative(folder / 'decision.json')}
    write(folder / 'manifest.json', data)
    lines = [f'# {LABELS[stage]} — {job} — revision {revision}', '',
             f"Chế độ: {settings(p, job)['mode']}. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.", '']
    for name in data['assets']:
        path = p.path(job, name)
        lines.append(f'[{path.name}]({path})')
    if stage == 'content':
        for scene in p.payload(job, 'content')['scenes']:
            lines += ['', f"## {scene['id']} — {scene['title']}", scene['narration']]
            if scene.get('narration_en'):
                lines.append(scene['narration_en'])
            lines.append(scene['prompt'])
    if stage == 'media':
        lines += ['', f"Số cảnh: {len(p.payload(job, 'images')['items'])}",
                  f"![Bảng ảnh]({p.path(job, p.payload(job, 'images')['contact_sheet'])})"]
        audio = p.payload(job, 'audio')
        lines += [f"Tiếng Việt: {audio['duration']:.2f} giây", f"![Nghe tiếng Việt]({p.path(job, audio['wav'])})"]
        if audio.get('en'):
            lines += [f"Tiếng Anh: {audio['en']['duration']:.2f} giây", f"![Nghe Alba]({p.path(job, audio['en']['wav'])})"]
        for item in p.payload(job, 'images')['items']:
            lines += [f"## {item['scene_id']}", f"![{item['scene_id']}]({p.path(job, item['path'])})", item['prompt']]
    (folder / 'review.md').write_text('\n\n'.join(lines))
    p.event(job, stage, 'review_ready', json.dumps({'revision': revision}))
    return data


def approve(p, job, stage, revision, note, machine=False):
    p.refresh(job)
    cfg = settings(p, job)
    if machine != (cfg['mode'] == 'auto'):
        raise Blocked('Actor differs from immutable job mode')
    data = current(p, job, stage)
    if not data or data['revision'] != revision or not note.strip() or approved(p, job, stage):
        raise Blocked('Cần đúng phần, revision hiện tại và phản hồi duyệt')
    if p.path(job, data['decision']).exists():
        raise Blocked('Decision/report changed; reject and create a new revision, never overwrite a saved decision')
    for module in STAGES[stage]:
        p.validate(job, module)
    report = None
    if machine:
        from machine_review import review
        report = review(p, job, stage, data['assets'], data['snapshot'])
        p.refresh(job)
        if current(p, job, stage) != data:
            raise Blocked('Artifacts changed during machine review')
    # Low-level acceptance cannot release another public gate by itself.
    for module in STAGES[stage]:
        if p.rows(job)[module]['state'] == 'awaiting_review':
            accept_module(p, job, module)
    result = {'approved': True, 'actor': 'machine' if machine else 'user',
              'note': note, 'manifest_hash': hashobj(data), 'at': time.time(), 'report': report}
    if report:
        result['report_hash'] = digest(p.path(job, report))
    write(p.path(job, data['decision']), result)
    p.event(job, stage, 'machine_approved' if machine else 'user_approved', json.dumps(result, ensure_ascii=False))
    return status(p, job)


def reject(p, job, stage, revision, note, part=None, scene=None, character=None):
    p.refresh(job)
    data = current(p, job, stage)
    if not data or data['revision'] != revision or not note.strip():
        raise Blocked('Cần đúng phần, revision và lý do sửa')
    if stage == 'media':
        if scene or character:
            p.reject(job, 'images', note, p.rows(job)['images']['revision'], 'final', scene, character)
        elif part == 'audio':
            p.reject(job, 'audio', note)
        else:
            raise Blocked('Sửa media: chọn --scene, --character hoặc --part audio')
    else:
        p.reject(job, STAGES[stage][0], note)
    # State changes above invalidate this manifest and every dependent gate.
    p.event(job, stage, 'review_rejected', json.dumps({'revision': revision, 'note': note}))
    return status(p, job)


def advance(p, job, target=None):
    cfg = settings(p, job)
    for _ in range(3):
        step = next_step(p, job)
        if 'blocked' in step:
            raise Blocked(step['blocked'])
        if step.get('action') == 'complete':
            return status(p, job)
        stage = step['stage']
        if target and stage != target:
            raise Blocked(f'Phần được phép hiện tại: {stage}')
        data = prepare(p, job, stage)
        if cfg['mode'] == 'review':
            return next_step(p, job)
        approve(p, job, stage, data['revision'], 'Automated quality review', machine=True)
        if target:
            return next_step(p, job)
    return status(p, job)


def batch(p, jobs):
    """One durable result per job, sequential to fit the target 16 GB machine."""
    result = []
    for job in jobs:
        try:
            if settings(p, job)['mode'] != 'auto':
                raise Blocked('Batch only accepts auto jobs')
            outcome = advance(p, job)
            result.append({'job': job, 'result': outcome})
        except Exception as ex:
            entry = {'job': job, 'needs_attention': True, 'error': str(ex)}
            result.append(entry)
            # These failures concern the shared provider, not just one script.
            if any(word in str(ex).lower() for word in ('login', 'captcha', 'rate limit', 'preflight', 'agy_not_installed', 'agy_api_provider')):
                entry['queue_paused'] = True
                break
    path = p.root / '.state' / 'batch-results' / f'{time.time_ns()}.json'
    write(path, result)
    return {'results': result, 'report': str(path)}
