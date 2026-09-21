"""Three public review gates; technical modules remain private implementation steps."""
import itertools
import json
import shutil
import tempfile
import time
from pathlib import Path

from pilot import Blocked, read, write, hashobj, digest

STAGES = {'content': ('content',), 'media': ('audio', 'images'), 'video': ('render',)}
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
    from scripts.story_plan import normalize_brief
    p.new(job, normalize_brief(brief))
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
    try:
        if any(digest(p.path(job,name)) != stamp for name,stamp in data.get('asset_hashes',{}).items()): return None
    except OSError:
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
    actor = result.get('actor')
    if actor == 'machine':
        report = p.path(job, result['report'])
        if not (report.is_file() and digest(report) == result.get('report_hash')):
            return False
    elif actor != 'user':
        return False
    # decision.json is a plain file anyone can write; only a matching row that
    # approve() already appended to the events table proves it was not hand-crafted.
    event = 'machine_approved' if actor == 'machine' else 'user_approved'
    with p._db_lock:
        row = p.db.execute("SELECT 1 FROM events WHERE job=? AND module=? AND event=? AND detail=? LIMIT 1",
                            (job, stage, event, hashobj(result))).fetchone()
    return row is not None


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
        files.append(p.rows(job)['audio']['envelope'])
        files.append(p.rows(job)['images']['envelope'])
        files += [x['path'] for x in images['references'] + images['items']]
        for item in images['items']:
            for ref in item['references']:
                files.append(read(p.path(job, ref['registration_journal']))['path'])
        audio = p.payload(job, 'audio')
        files += [audio['wav'], audio['srt']]
        if audio.get('en'):
            files.append(audio['en']['wav'])
    if stage == 'video':
        media = current(p,job,'media')
        if media:
            files += [x for x in media['assets'] if x.endswith('visual-timing.json')]
        video = p.payload(job, 'render')
        files += [video[k] for k in ('video', 'video_9x16', 'video_16x9') if video.get(k)]
    return list(dict.fromkeys(files))


def character_comparisons(p, job, images):
    """The identity check docs/workflow.md folds into the media gate: the
    approved character reference next to what Flow actually registered.
    image_pipeline.register() never marks a review-mode registration as a
    verified match (it writes pending_media_review=True instead) — this must
    say the same thing in the same words, never a softer "looks fine"."""
    lines = ['## Cần so sánh trước khi duyệt', '',
             'Với mỗi nhân vật: ảnh tham chiếu đã duyệt (trái) và ảnh do Flow đăng ký (phải). '
             'Mở cả hai và xác nhận đúng là cùng một nhân vật trước khi duyệt phần media.']
    for ref in images['references']:
        reg = next((r for item in images['items'] for r in item['references']
                     if r['character_id'] == ref['character_id']), None)
        lines += ['', f"### {ref['name']} ({ref['character_id']})"]
        if not reg:
            lines.append('Nhân vật này không được dùng trong hình nào đã lên kế hoạch; không có ảnh đăng ký để so sánh.')
            continue
        registered_path = read(p.path(job, reg['registration_journal']))['path']
        confirmation = read(p.path(job, reg['confirmation']))
        lines += ['| Ảnh tham chiếu đã duyệt | Ảnh do Flow đăng ký |', '|---|---|',
                  f"| ![{ref['name']} — tham chiếu]({p.path(job, ref['path'])}) "
                  f"| ![{ref['name']} — đăng ký]({p.path(job, registered_path)}) |"]
        if confirmation.get('pending_media_review'):
            lines.append('**CHƯA SO SÁNH — cần bạn đối chiếu ngay bây giờ.** '
                          'Hệ thống chưa tự nhận hai ảnh là cùng một nhân vật.')
        if confirmation.get('matches_approved_reference') is True and confirmation.get('observer') == 'machine':
            report = confirmation.get('report')
            lines.append('Máy đã đánh giá và cho là khớp với tham chiếu. Báo cáo: '
                          + (str(p.path(job, report)) if report else 'không có'))
        if confirmation.get('observer') == 'technical':
            lines.append('Lưu ý: xác nhận này chỉ là kiểm tra kỹ thuật (đã ghi nhận đúng file), '
                          'KHÔNG phải xác nhận hai ảnh là cùng một nhân vật.')
    return lines


def scene_image_lines(p, job, items):
    """Dual jobs render every logical image twice (9:16 and 16:9, see
    docs/story-planning.md); a reviewer can only confirm the 16:9 crop kept
    the same characters/action/text by seeing both ratios together, so pair
    them under one heading. A single-ratio job keeps the prior one-item-per-
    heading layout unchanged (regression-sensitive)."""
    image_ids = [it.get('image_id') for it in items if it.get('image_id')]
    if len(image_ids) == len(set(image_ids)):
        lines = []
        for item in items:
            lines += [f"## {item['scene_id']} — {item.get('image_id','')} {item.get('ratio','')}",
                      f"![{item['scene_id']}]({p.path(job, item['path'])})", item['prompt']]
        return lines
    lines = []
    for scene_id, scene_items in itertools.groupby(items, key=lambda it: it['scene_id']):
        scene_items = list(scene_items)
        lines.append(f'## {scene_id}')
        for image_id, image_items in itertools.groupby(scene_items, key=lambda it: it.get('image_id')):
            image_items = list(image_items)
            lines.append(f'### {image_id}')
            lines.append('| ' + ' | '.join(it.get('ratio', '') for it in image_items) + ' |')
            lines.append('|' + '---|' * len(image_items))
            lines.append('| ' + ' | '.join(
                f"![{image_id} {it.get('ratio','')}]({p.path(job, it['path'])})" for it in image_items) + ' |')
            prompts = list(dict.fromkeys(it['prompt'] for it in image_items))
            if len(prompts) == 1:
                lines.append(prompts[0])
            else:
                for it in image_items:
                    lines.append(f"Prompt ({it.get('ratio','')}): {it['prompt']}")
    return lines


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
                draft_path = p.job(job) / 'draft/content.json'
                unchanged_rejected = module == 'content' and row['state'] == 'needs_changes' and row['envelope'] and draft_path.exists() and read(draft_path) == read(p.path(job,row['envelope']))['payload']
                if module == 'content' and (not draft_path.exists() or unchanged_rejected):
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
    revision = 1 + max([int(x.name) for x in (p.job(job) / 'reviews' / stage).glob('*') if x.is_dir() and x.name.isdigit()], default=0)
    folder = p.job(job) / 'reviews' / stage / str(revision)
    folder.mkdir(parents=True, exist_ok=False)
    relative = lambda f: str(f.relative_to(p.job(job)))
    data = {'stage': stage, 'revision': revision, 'snapshot': snapshot(p, job, stage),
            'assets': assets(p, job, stage), 'review': relative(folder / 'review.md'),
            'decision': relative(folder / 'decision.json')}
    lines = [f'# {LABELS[stage]} — {job} — revision {revision}', '',
             f"Chế độ: {settings(p, job)['mode']}. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.", '']
    for name in data['assets']:
        path = p.path(job, name)
        lines.append(f'[{path.name}]({path})')
    if stage == 'content':
        payload = p.payload(job, 'content')
        if payload.get('schema_version') == '3.0':
            from scripts.story_plan import review_plan, feedback
            previous = sorted((p.job(job) / 'revisions/content').glob('*/content.json'), key=lambda x: int(x.parent.name))
            lines.append(review_plan(p.brief(job)[0], payload, read(previous[-2]) if len(previous)>1 else None, feedback(p,job)))
        else:
            from content_contract import review_markdown
            lines.append(review_markdown(job, revision, p.brief(job)[0], payload))
    if stage == 'media':
        images = p.payload(job, 'images')
        lines += character_comparisons(p, job, images)
        lines += ['', f"Số cảnh: {len(p.payload(job, 'content')['scenes'])}; số hình: {len(images['items'])}",
                  f"![Bảng ảnh]({p.path(job, images['contact_sheet'])})"]
        audio = p.payload(job, 'audio')
        lines += [f"Tiếng Việt: {audio['duration']:.2f} giây", f"![Nghe tiếng Việt]({p.path(job, audio['wav'])})"]
        if audio.get('en'):
            lines += [f"Tiếng Anh: {audio['en']['duration']:.2f} giây", f"![Nghe Alba]({p.path(job, audio['en']['wav'])})"]
        from scripts.story_plan import timeline
        payload = p.payload(job, 'content')
        if payload.get('schema_version') == '3.0':
            ratio = p.brief(job)[0]['aspect_ratio']
            timing = {lang: timeline(payload, images, audio, lang, r) for lang,r in ([('vi','9:16'),('en','16:9')] if ratio=='dual' else [('en','16:9')] if ratio=='16:9' else [('vi','9:16')])}
            if any(x.startswith('research-visuals:') for x in p.brief(job)[0].get('planning',{}).get('domain_requirements',[])):
                from research.visuals import timing_report
                report = timing_report(p.brief(job)[0], payload, timing)
                write(folder / 'research-visual-review.json', report)
                data['assets'].append(relative(folder / 'research-visual-review.json'))
                lines += ['## Kiểm tra nhịp hình nghiên cứu', json.dumps(report,ensure_ascii=False,indent=2)]
            write(folder / 'visual-timing.json', timing)
            data['assets'].append(relative(folder / 'visual-timing.json'))
            lines += ['Nhịp theo âm thanh (nội suy, cần nghe kiểm tra):', json.dumps(timing,ensure_ascii=False,indent=2), 'Kiểm tra từng hình: chữ đúng danh sách, không mã nội bộ/chữ thừa; đúng kiểu chữ, vị trí và tính liên tục.']
        lines += scene_image_lines(p, job, images['items'])
    data['asset_hashes'] = {name:digest(p.path(job,name)) for name in data['assets']}
    (folder / 'review.md').write_text('\n\n'.join(lines))
    data['asset_hashes'][relative(folder / 'review.md')] = digest(folder / 'review.md')
    write(folder / 'manifest.json', data)
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
    # Verified against a hash, matching workflow_created; a raw JSON detail would let anyone forge a matching row.
    p.event(job, stage, 'machine_approved' if machine else 'user_approved', hashobj(result))
    p.event(job, stage, 'approval_detail', json.dumps(result, ensure_ascii=False))
    result = status(p, job)
    if stage == 'video' and result.get('complete'):
        result['videos'] = publish_videos(p, job)
    return result


def publish_videos(p, job):
    """Copy only approved video deliverables into the visible video library.

    Sandboxes always export beneath their own root. The installed sys/ layout
    exports beside sys/. Historical revisions and decisions remain untouched.
    """
    from pilot import ROOT
    p.refresh(job)
    settings(p, job)
    if not all(approved(p, job, stage) for stage in STAGES):
        raise Blocked('Video publication requires all three current approvals')
    root = p.root.resolve()
    library = (root.parent if root == ROOT.resolve() and root.name == 'sys' else root) / 'video'
    if library.is_symlink():
        raise Blocked('Video library must not be a symbolic link')
    folder = library / p.job(job).name
    if folder.is_symlink():
        raise Blocked('Video output folder must not be a symbolic link')
    payload = p.payload(job, 'render')
    keys = [key for key in ('video_9x16', 'video_16x9') if payload.get(key)] or ['video']
    revision = current(p, job, 'video')['revision']
    plans = []
    for key in keys:
        source = p.path(job, payload[key])
        if source.suffix.lower() != '.mp4' or not source.is_file():
            raise Blocked('Missing approved MP4 deliverable')
        suffix = key.removeprefix('video_') if key != 'video' else 'final'
        target = folder / f'{job}_r{revision}_{suffix}.mp4'
        stamp = digest(source)
        if target.is_symlink() or (target.exists() and (not target.is_file() or digest(target) != stamp)):
            raise Blocked(f'Refusing to overwrite a different video: {target}')
        plans.append((source, target, stamp))
    folder.mkdir(parents=True, exist_ok=True)
    for source, target, stamp in plans:
        if target.exists():
            continue
        with tempfile.NamedTemporaryFile(dir=folder, prefix='.publishing-', delete=False) as handle:
            temporary = Path(handle.name)
        try:
            shutil.copyfile(source, temporary)
            if digest(temporary) != stamp:
                raise Blocked('Video copy did not match the approved source')
            # Link atomically without replacing a file created by another writer.
            target.hardlink_to(temporary)
        finally:
            temporary.unlink(missing_ok=True)
    return [str(target) for _, target, _ in plans]


def retake_audio(p, job, note, scene=None):
    """Ask for a new read of the narration, optionally of one scene only.

    The TTS cache is content-addressed, so rejecting a delivery without bumping
    this count would re-synthesise the same words with the same settings and
    hand back the identical take. Without --scene every scene is bumped, which
    is what rejecting the whole track has always meant.
    """
    ids = [s['id'] for s in p.payload(job, 'content')['scenes']]
    if scene and scene not in ids:
        raise Blocked('Sửa giọng: cảnh không có trong kịch bản')
    targets = [scene] if scene else ids
    with p._db_lock:
        for scene_id in targets:
            p.db.execute('INSERT INTO audio_edits(job,scene_id,note,at) VALUES(?,?,?,?)',
                         (job, scene_id, note, time.time()))
        p.db.commit()
    p.event(job, 'audio', 'audio_retake_requested', json.dumps({'scenes': targets, 'note': note}, ensure_ascii=False))
    p.reject(job, 'audio', note)


def reject(p, job, stage, revision, note, part=None, scene=None, character=None):
    p.refresh(job)
    data = current(p, job, stage)
    if not data or data['revision'] != revision or not note.strip():
        raise Blocked('Cần đúng phần, revision và lý do sửa')
    if stage == 'media':
        # --part audio is checked first: with a --scene it means "read this scene
        # again", not "redraw this scene's image".
        if part == 'audio':
            retake_audio(p, job, note, scene)
        elif scene or character:
            p.reject(job, 'images', note, p.rows(job)['images']['revision'], 'final', scene, character)
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
            result = status(p, job)
            result['videos'] = publish_videos(p, job)
            return result
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
