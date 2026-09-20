"""Review-gated Flow image stages. Production approvals are never inferred."""
import contextlib
import json
import shutil
import time
from pathlib import Path
import jsonschema
from PIL import Image, ImageDraw
from pilot import Blocked, digest, hashobj, read, write

STAGES = ('references', 'final')


def setup(p):
    p.db.executescript('''
    CREATE TABLE IF NOT EXISTS image_reviews(
      job TEXT, checkpoint TEXT, revision INTEGER, envelope TEXT, hash TEXT,
      signature TEXT, note TEXT, at REAL, PRIMARY KEY(job, checkpoint, revision));
    CREATE TABLE IF NOT EXISTS image_edits(
      id INTEGER PRIMARY KEY, job TEXT, target TEXT, note TEXT, at REAL);
    ''')


def content(p, j):
    c = p.payload(j, 'content')
    if c.get('schema_version') != '2.0':
        raise Blocked('M2_CONTENT: create a v2 content job; legacy history is read-only')
    import re
    if any(not re.fullmatch(r'[A-Za-z0-9_-]+', x['id']) for x in c['characters']):
        raise Blocked('M2_CHARACTER_ID: use safe alphanumeric character IDs')
    return c


def edits(p, j, target):
    with getattr(p, '_db_lock', contextlib.nullcontext()):
        return [dict(r) for r in p.db.execute(
            'SELECT id,note FROM image_edits WHERE job=? AND target=? ORDER BY id', (j, target)).fetchall()]


def signature(p, j, stage):
    c = content(p, j)
    targets = ['ref:' + x['id'] for x in c['characters']]
    if stage != 'references':
        targets += [x['id'] for x in c['scenes']]
        targets += ['proof:' + x['id'] for x in c['characters']]
    return hashobj({'content': p.rows(j)['content']['hash'],
                    'edits': {t: edits(p, j, t) for t in targets}})


def approved(p, j, stage):
    with getattr(p, '_db_lock', contextlib.nullcontext()):
        row = p.db.execute('SELECT * FROM image_reviews WHERE job=? AND checkpoint=? ORDER BY revision DESC LIMIT 1',
                           (j, stage)).fetchone()
    if not row or row['signature'] != signature(p, j, stage):
        return None
    try:
        e = read(p.path(j, row['envelope']))
        if p.snapshot_hash(j, e) != row['hash']:
            return None
        return e
    except (OSError, ValueError, KeyError):
        return None


def stage(p, j):
    for s in STAGES:
        if not approved(p, j, s):
            return s
    return 'complete'


def describe(p, j):
    s = stage(p, j)
    c = content(p, j)
    return {'checkpoint': s, 'approved_checkpoints': [x for x in STAGES if approved(p, j, x)],
            'next_step': {'references': 'Create/review character references',
                          'final': f"Create/review remaining scenes and all {len(c['scenes'])} images",
                          'complete': 'Images approved; audio may proceed'}[s]}


def preflight(p, j, operation):
    cfg = read(p.root / 'config.json')
    if cfg.get('video_generation') or cfg.get('credit_budget', 0) != 0:
        raise Blocked('M2_POLICY: credit budget must be non-negative')
    path = p.job(j) / 'flow/preflight.json'
    e = read(path) if path.exists() else {}
    valid_profiles = {cfg['flow_profile']}
    if 'flow_profiles' in cfg: valid_profiles.update(cfg['flow_profiles'])
    valid_profiles.add('video-pilot')
    if (e.get('credits_per_generation') != 0 or not 0 <= time.time() - e.get('observed_at', 0) <= 600 or e.get('mode') != 'image'
        or e.get('model') != cfg['flow_model']
        or e.get('project') != cfg['flow_project'] or e.get('profile') not in valid_profiles or not e.get('account_confirmed')
        or not e.get('observer') or operation not in e.get('operations', [])):
        raise Blocked('M2_PREFLIGHT: fresh observed evidence required for ' + operation)
    if digest(p.path(j, e['screenshot'])) != e['screenshot_hash']:
        raise Blocked('M2_PREFLIGHT: screenshot changed')
    return e


def image_check(p, j, path, expected_hash=None, full=True):
    f = p.path(j, path)
    if expected_hash and digest(f) != expected_hash:
        raise Blocked('M2_HASH: image changed: ' + path)
    with Image.open(f) as im:
        im.load()
        if full:
            b = p.brief(j)[0] if p.brief(j) else None
            ratio = b.get('aspect_ratio', '9:16') if b else '9:16'
            if ratio == '16:9':
                if abs(im.width / im.height - 16 / 9) > .04 or im.width < 720 or im.height < 400:
                    raise Blocked('M2_IMAGE: require 16:9: ' + path)
            elif ratio == 'dual':
                v9 = abs(im.width / im.height - 9 / 16) <= .05 and (im.width >= 360 and im.height >= 640)
                v16 = abs(im.width / im.height - 16 / 9) <= .05 and (im.width >= 640 and im.height >= 360)
                if not (v9 or v16):
                    raise Blocked('M2_IMAGE: require 9:16 or 16:9 resolution: ' + path)
            else:
                if abs(im.width / im.height - 9 / 16) > .04 or im.width < 360 or im.height < 640:
                    raise Blocked('M2_IMAGE: require 9:16 and at least 720x1280: ' + path)
    return path


def request(p, j, target, prompt, refs=(), registration=None):
    """One durable journal per identity; unknown outcomes are never retried."""
    import adapters
    p.gate(j, 'images')
    c = content(p, j)
    if not target.startswith('ref:') and not approved(p, j, 'references'):
        raise Blocked('M2_REFERENCES: approve references first')
    scene = next((x for x in c['scenes'] if x['id'] == target), None)
    if scene:
        approved_refs = approved(p, j, 'references')['payload']['references']
        linked = [register_existing(p, j, next(x for x in approved_refs if x['character_id'] == cid)) for cid in scene['character_ids']]
        if list(refs) != linked or prompt != scene['prompt']:
            raise Blocked('M2_REFERENCE_LINK: scene request must use approved prompt and registered characters')
    cfg = read(p.root / 'config.json')
    from prompt_templates import image_prompt
    corrections = '\n'.join(x['note'] for x in edits(p, j, target))
    revised_prompt = prompt + ('\nRequested corrections: ' + corrections if corrections else '')
    ratio = '16:9' if p.brief(j)[0]['aspect_ratio']=='16:9' else '9:16'
    actual_prompt = revised_prompt if registration else image_prompt(revised_prompt, ratio)
    identity = {'content_hash': p.rows(j)['content']['hash'], 'target': target,
                'prompt': prompt, 'actual_prompt': actual_prompt, 'model': cfg['flow_model'], 'ratio': ratio,
                'references': list(refs), 'edits': edits(p, j, target),
                'registration': registration, 'config_hash': digest(p.root / 'config.json')}
    key = hashobj(identity)
    base = p.job(j) / 'flow/attempts'
    base.mkdir(parents=True, exist_ok=True)
    # Even changed prompts/edits cannot hide an unresolved submission.
    for q in base.glob('*/request.json'):
        old = read(q)
        same_target = old['identity']['target'] == target
        if target.startswith('register:'):
            same_target = old['identity']['target'].rsplit(':', 1)[0] == target.rsplit(':', 1)[0]
        if same_target and old['state'] in ('submitted', 'ambiguous'):
            raise Blocked('M2_AMBIGUOUS: reconcile request ' + old['key'] + ' before another submission')
    folder = base / key
    record = folder / 'request.json'
    if record.exists():
        result = read(record)
        if result['state'] == 'downloaded':
            image_check(p, j, result['path'], result['sha256'], full=registration is None)
            return result
        raise Blocked('M2_ATTEMPT: request needs explicit reconciliation')
    evidence = preflight(p, j, 'character-register' if registration else 'image')
    folder.mkdir()
    write(folder / 'preflight.json', evidence)
    shutil.copy(p.path(j, evidence['screenshot']), folder / 'preflight.png')
    out = folder / 'download'
    out.mkdir()
    common = ['--profile', cfg['flow_profile'], '--project', cfg['flow_project'], '--out', str(out)]
    model_arg = 'nano-banana-pro' if 'pro' in cfg['flow_model'].lower() else ('nano-banana-2' if '2' in cfg['flow_model'] else cfg['flow_model'])
    if registration:
        args = ['character', 'create', '--name', registration['name'], '--prompt', actual_prompt,
                '--model', model_arg,
                '--image', str(p.path(j, registration['path']))] + common
    else:
        args = ['image', '--id', key[:16], '--prompt', actual_prompt, '--model', model_arg,
                '--ratio', ratio, '--outputs', '1'] + common
        if refs:
            args += ['--character'] + [x['name'] for x in refs]
    result = {'key': key, 'identity': identity, 'state': 'submitted', 'submitted_at': time.time(),
              'args': args, 'journal': str(record.relative_to(p.job(j)))}
    write(record, result)
    p.event(j, 'images', 'flow_submitted', key)
    try:
        r = adapters.gflow(p, *args)
        (folder / 'command.log').write_text(r.stdout + '\n' + r.stderr)
        if r.returncode:
            raise Blocked('Flow failed (login/CAPTCHA/limit or provider error); see command.log: ' + r.stderr[-500:])
        candidates = []
        for f in out.rglob('*'):
            if f.is_file():
                try:
                    with Image.open(f) as im:
                        im.verify()
                    candidates.append(f)
                except Exception:
                    pass
        if len(candidates) != 1:
            raise Blocked('Cannot identify exactly one downloaded result')
        proof = read(folder / 'ui-proof.json')
        if proof.get('passed') is not True or proof.get('characters') != [x['name'] for x in refs]:
            raise Blocked('Flow UI attachment/mode evidence missing')
        if proof.get('mode') != ('character-register' if registration else 'image'):
            raise Blocked('Flow UI mode evidence differs')
        with Image.open(folder / 'before-submit.png') as im: im.verify()
        f = candidates[0]
        if not registration:
            metadata = read(f.with_suffix('.json'))
            if (metadata.get('jobId') != key[:16] or metadata.get('type') != 'image'
                or metadata.get('prompt') != actual_prompt or metadata.get('ratio') != ratio
                or metadata.get('characters', []) != [x['name'] for x in refs]
                or metadata.get('source') != 'google-flow-browser' or metadata.get('status') != 'downloaded'):
                raise Blocked('Downloaded metadata does not match request')
        result.update(state='downloaded', path=str(f.relative_to(p.job(j))), sha256=digest(f))
        write(record, result)
        image_check(p, j, result['path'], result['sha256'], full=registration is None)
        p.event(j, 'images', 'flow_downloaded', key)
        return result
    except Exception as ex:
        # A known downloaded but invalid image is not an unknown submission.
        if result['state'] != 'downloaded':
            result.update(state='ambiguous', error=str(ex))
            write(record, result)
        raise Blocked('M2_FLOW: ' + str(ex)) from ex


def reference_prompt(c, char):
    return f"{c['style']}. Một nhân vật toàn thân, nền đơn giản, không chữ. {char['name']}. {char['appearance']}. Trang phục: {char['outfit']}."


def register(p, j, ref):
    r = request(p, j, 'register:' + ref['character_id'] + ':' + ref['sha256'], ref['prompt'],
                registration={'name': ref['name'], 'path': ref['path'], 'sha256': ref['sha256']})
    confirmation = p.path(j, r['journal']).parent / 'confirmation.json'
    if not confirmation.exists() and (p.job(j) / 'workflow.json').exists():
        import workflow
        mode = workflow.settings(p, j)['mode']
        report = None
        if mode == 'auto':
            from machine_review import review
            report = review(p, j, 'registration', [ref['path'], r['path']],
                            {'reference_hash': ref['sha256'], 'result_hash': r['sha256']})
        # In review mode the user compares these images at the combined media gate.
        # A pending comparison must never be described as a verified identity match.
        shot = p.path(j, r['journal']).parent / 'before-submit.png'
        write(confirmation, {'reference_hash': ref['sha256'], 'result_hash': r['sha256'],
                            'name': ref['name'], 'matches_approved_reference': mode == 'auto',
                            'pending_media_review': mode == 'review', 'observer': 'machine' if report else 'technical',
                            'note': 'Machine identity review' if report else 'Compare at media gate',
                            'report': report, 'screenshot': str(shot.relative_to(p.job(j))),
                            'screenshot_hash': digest(shot)})
    if not confirmation.exists():
        raise Blocked('M2_REGISTRATION_REVIEW: character create can generate a new appearance. Compare ' + r['path'] +
                      ' with approved reference; record flow-confirm-registration --request ' + r['key'] + ' --evidence FILE')
    e = read(confirmation)
    if (e.get('reference_hash') != ref['sha256'] or e.get('result_hash') != r['sha256']
        or not registration_accepted(p, j, e) or not e.get('observer') or not e.get('note')
        or e.get('name') != ref['name'] or digest(p.path(j, e['screenshot'])) != e['screenshot_hash']):
        raise Blocked('M2_REGISTRATION_REVIEW: confirmation invalid')
    return {'name': ref['name'], 'character_id': ref['character_id'], 'sha256': ref['sha256'],
            'registration_hash': r['sha256'], 'registration_journal': r['journal'],
            'confirmation': str(confirmation.relative_to(p.job(j)))}


def registration_accepted(p, j, evidence):
    if evidence.get('matches_approved_reference') is True:
        return True
    if evidence.get('pending_media_review') and (p.job(j) / 'workflow.json').exists():
        import workflow
        return workflow.settings(p, j)['mode'] == 'review'
    return False


def attach(p, j, result, target, prompt, refs, out):
    src = p.path(j, result['path'])
    dst = out / (target + src.suffix)
    shutil.copy(src, dst)
    return {'scene_id': target, 'path': str(dst.relative_to(p.job(j))), 'prompt': prompt,
            'source': 'google-flow', 'actual_prompt': result['identity']['actual_prompt'], 'sha256': digest(dst), 'references': list(refs),
            'request': result['journal']}


def produce(p, j, out):
    c = content(p, j)
    s = stage(p, j)
    if s == 'complete':
        raise Blocked('M2_APPROVED: reject a specific scene or character before replacement')
    if p.rows(j)['images']['state'] == 'awaiting_review':
        raise Blocked('M2_REVIEW: approve or reject current checkpoint first')
    refs, items, proofs = [], [], []
    if s == 'references':
        for char in c['characters']:
            prompt = reference_prompt(c, char)
            r = request(p, j, 'ref:' + char['id'], prompt)
            name = j + '-' + char['id'] + '-' + r['key'][:12]
            asset = attach(p, j, r, 'REF-' + char['id'], prompt, [], out)
            refs.append(dict(asset, character_id=char['id'], name=name))
    else:
        refs = approved(p, j, 'references')['payload']['references']
        registrations = {r['character_id']: register(p, j, r) for r in refs}
        scenes = c['scenes']
        import concurrent.futures
        cfg = read(p.root / 'config.json')
        concurrency = cfg.get('concurrency', 3)

        def process_scene(scene):
            linked = [registrations[x] for x in scene['character_ids']]
            r = request(p, j, scene['id'], scene['prompt'], linked)
            return (scene['id'], scene['prompt'], linked, r)

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            for scene_id, prompt, linked, r in executor.map(process_scene, scenes):
                items.append(attach(p, j, r, scene_id, prompt, linked, out))

    entries = refs + items + proofs
    sheet = Image.new('RGB', (540, max(1, (len(entries) + 2) // 3) * 350), '#eeeeee')
    draw = ImageDraw.Draw(sheet)
    for i, entry in enumerate(entries):
        with Image.open(p.path(j, entry['path'])) as im:
            im = im.convert('RGB');im.thumbnail((180, 320));sheet.paste(im, ((i % 3) * 180, (i // 3) * 350))
        draw.text(((i % 3) * 180 + 5, (i // 3) * 350 + 325), entry['scene_id'], fill='black')
    sheet.save(out / 'contact-sheet.jpg')
    payload = {'schema_version': '2.0', 'checkpoint': s, 'content_hash': p.rows(j)['content']['hash'],
               'signature': signature(p, j, s), 'items': items, 'references': refs, 'proofs': proofs,
               'contact_sheet': str((out / 'contact-sheet.jpg').relative_to(p.job(j)))}
    return payload


def check(p, j, data):
    jsonschema.validate(data, read(p.root / 'schemas/images-v2.json'))
    c = content(p, j);s = data['checkpoint']
    if data['content_hash'] != p.rows(j)['content']['hash'] or data['signature'] != signature(p, j, s):
        raise Blocked('M2_VERSION: content or requested edits changed')
    chars = {x['id']: x for x in c['characters']}
    for ref in data['references']:
        if ref['character_id'] not in chars or ref['prompt'] != reference_prompt(c, chars[ref['character_id']]):
            raise Blocked('M2_REFERENCES: reference differs from approved character profile')
    if [x['character_id'] for x in data['references']] != list(chars):
        raise Blocked('M2_REFERENCES: missing/duplicate character')
    expected = [] if s == 'references' else c['scenes']
    if [x['scene_id'] for x in data['items']] != [x['id'] for x in expected]:
        raise Blocked('M2_SCENES: missing/duplicate/reordered scenes')
    if s != 'references':
        a = approved(p, j, 'references')
        if not a or data['references'] != a['payload']['references']:
            raise Blocked('M2_REFERENCES: references not approved')
    for item, scene in zip(data['items'], expected):
        if item['prompt'] != scene['prompt'] or [x['character_id'] for x in item['references']] != scene['character_ids']:
            raise Blocked('M2_PROMPT: approved prompt or character links changed')
    if data['proofs']:
        raise Blocked('Separate proof images removed; review actual scene images')
    files = [data['contact_sheet']]
    image_check(p, j, data['contact_sheet'], full=False)
    for item in data['references'] + data['items'] + data['proofs']:
        files.append(image_check(p, j, item['path'], item['sha256']))
        req = read(p.path(j, item['request']))
        from prompt_templates import image_prompt
        changes = '\n'.join(x['note'] for x in req['identity']['edits'])
        expected_prompt = image_prompt(item['prompt'] + ('\nRequested corrections: ' + changes if changes else ''), req['identity']['ratio'])
        if item['actual_prompt'] != expected_prompt:
            raise Blocked('M2_PROMPT: actual prompt differs from configured template')
        if (req['state'] != 'downloaded' or req['identity']['content_hash'] != data['content_hash']
            or req['identity']['prompt'] != item['prompt'] or req['identity']['actual_prompt'] != item['actual_prompt'] or req['sha256'] != item['sha256']
            or req['identity']['references'] != item['references']):
            raise Blocked('M2_EVIDENCE: request does not match downloaded asset')
        files.extend([item['request'], req['path']])
        if not req.get('reconciliation_evidence'): files.append(str(p.path(j, req['path']).with_suffix('.json').relative_to(p.job(j))))
        if req.get('reconciliation_evidence'): files.append(req['reconciliation_evidence'])
        base = p.path(j, item['request']).parent
        files.extend(str((base / n).relative_to(p.job(j))) for n in ['preflight.json', 'preflight.png', 'ui-proof.json', 'before-submit.png'])
        ui = read(base / 'ui-proof.json')
        if ui.get('passed') is not True or ui.get('mode') != 'image' or ui.get('characters') != [x['name'] for x in item['references']]:
            raise Blocked('M2_UI_EVIDENCE: image mode/reference attachment not verified')
        for ref in item['references']:
            original = next((x for x in data['references'] if x['character_id'] == ref['character_id']), None)
            if not original or ref != register_existing(p, j, original):
                raise Blocked('M2_REFERENCE_LINK: registration evidence mismatch')
            reg = read(p.path(j, ref['registration_journal']))
            conf = read(p.path(j, ref['confirmation']))
            files.extend([ref['registration_journal'], reg['path'], ref['confirmation'], conf['screenshot']])
            if reg.get('reconciliation_evidence'): files.append(reg['reconciliation_evidence'])
            regbase = p.path(j, ref['registration_journal']).parent
            files.extend(str((regbase / n).relative_to(p.job(j))) for n in ['preflight.json', 'preflight.png', 'ui-proof.json', 'before-submit.png'])
    for f in files:
        if not p.path(j, f).is_file():
            raise Blocked('M2_FILE: missing ' + f)
    return list(dict.fromkeys(files))


def register_existing(p, j, original):
    # Validation must never issue a provider request.
    target = 'register:' + original['character_id'] + ':' + original['sha256']
    candidates = []
    for q in (p.job(j) / 'flow/attempts').glob('*/request.json'):
        r = read(q)
        if r['identity']['target'] == target and r['state'] == 'downloaded':
            conf = q.parent / 'confirmation.json'
            if not conf.exists():
                continue
            e = read(conf)
            if (registration_accepted(p, j, e) and e.get('reference_hash') == original['sha256']
                and e.get('result_hash') == r['sha256'] and e.get('name') == original['name']
                and e.get('observer') and e.get('note')
                and digest(p.path(j, e['screenshot'])) == e['screenshot_hash']):
                image_check(p, j, r['path'], r['sha256'], full=False)
                candidates.append((r.get('submitted_at', 0), {
                    'name': original['name'], 'character_id': original['character_id'], 'sha256': original['sha256'],
                    'registration_hash': r['sha256'], 'registration_journal': r['journal'],
                    'confirmation': str(conf.relative_to(p.job(j)))
                }))
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    raise Blocked('M2_REGISTRATION: verified registration missing')


def approve(p, j, rev, note, checkpoint, actor='user'):
    p.validate(j, 'images');row = p.rows(j)['images'];e = read(p.path(j, row['envelope']))
    s = e['payload']['checkpoint']
    if checkpoint != s or row['revision'] != rev or row['state'] != 'awaiting_review' or not note.strip():
        raise Blocked('M2_APPROVAL: exact checkpoint, revision and user feedback required')
    p.db.execute('INSERT INTO image_reviews VALUES(?,?,?,?,?,?,?,?)',
                 (j, s, rev, row['envelope'], row['hash'], signature(p, j, s), note, time.time()))
    p.db.execute('UPDATE modules SET state=? WHERE job=? AND module=?',
                 ('approved' if s == 'final' else 'pending', j, 'images'))
    p.db.commit();p.event(j, 'images', 'technical_accepted' if actor=='technical' else 'checkpoint_approved', json.dumps({'checkpoint': s, 'revision': rev, 'actor': actor, 'note': note}, ensure_ascii=False))


def reject(p, j, rev, note, checkpoint, scene=None, character=None):
    p.gate(j, 'images');row = p.rows(j)['images']
    if not note.strip() or row['revision'] != rev or checkpoint not in STAGES:
        raise Blocked('M2_REJECT: exact revision, checkpoint and reason required')
    current = stage(p, j) if row['state'] in ('blocked', 'running') else p.payload(j, 'images')['checkpoint']
    if current != checkpoint:
        raise Blocked('M2_REJECT: checkpoint differs from current output')
    c = content(p, j)
    if bool(scene) == bool(character):
        raise Blocked('M2_REJECT: select exactly one --scene or --character')
    if scene and scene not in [x['id'] for x in c['scenes'][:0 if checkpoint=='references' else len(c['scenes'])]]:
        raise Blocked('M2_REJECT: scene is not in this checkpoint')
    if character and character not in [x['id'] for x in c['characters']]:
        raise Blocked('M2_REJECT: unknown character')
    target = scene or 'ref:' + character
    p.db.execute('INSERT INTO image_edits(job,target,note,at) VALUES(?,?,?,?)', (j, target, note, time.time()))
    p.db.execute("UPDATE modules SET state='needs_changes' WHERE job=? AND module='images'", (j,))
    p.db.execute("UPDATE modules SET state='stale' WHERE job=? AND module='render' AND state!='pending'", (j,))
    p.db.commit();p.event(j, 'images', 'image_revision_requested', json.dumps({'target': target, 'note': note}, ensure_ascii=False))


def flow_action(p, a):
    p.gate(a.job, 'images')
    if not a.request or len(a.request) != 64 or any(x not in '0123456789abcdef' for x in a.request):
        raise Blocked('M2_REQUEST: --request SHA256 required')
    q = p.job(a.job) / 'flow/attempts' / a.request / 'request.json'
    r = read(q)
    if a.command == 'flow-confirm-registration':
        e = read(a.evidence) if a.evidence else {}
        reg = r['identity']['registration']
        if not reg or r['state'] != 'downloaded':
            raise Blocked('M2_REGISTRATION: no downloaded registration')
        if (e.get('matches_approved_reference') is not True or e.get('name') != reg['name']
            or not e.get('observer') or not e.get('note')):
            raise Blocked('M2_REGISTRATION: observed identity match, exact name and feedback required')
        dest = q.parent / 'confirmation.png'
        if (q.parent / 'confirmation.json').exists():
            raise Blocked('Confirmation already exists; do not overwrite evidence')
        with Image.open(e['screenshot']) as im: im.verify()
        shutil.copy(e['screenshot'], dest)
        e.update(reference_hash=reg['sha256'], result_hash=r['sha256'], screenshot=str(dest.relative_to(p.job(a.job))), screenshot_hash=digest(dest))
        write(q.parent / 'confirmation.json', e)
        p.event(a.job, 'images', 'registration_confirmed', a.request)
        return {'confirmed': a.request}
    if r['state'] not in ('submitted', 'ambiguous') or not a.asset or not a.note or not a.evidence:
        raise Blocked('M2_RECONCILE: unresolved request, downloaded asset, UI screenshot and verification note required')
    source = Path(a.asset)
    with Image.open(source) as im: im.verify()
    dest = q.parent / ('reconciled' + source.suffix)
    shutil.copy(source, dest)
    image_check(p, a.job, str(dest.relative_to(p.job(a.job))), full=r['identity']['registration'] is None)
    evidence = q.parent / 'reconcile.png'
    observed = read(a.evidence)
    expected_names = [x['name'] for x in r['identity']['references']]
    expected_mode = 'character-register' if r['identity']['registration'] else 'image'
    if (observed.get('request') != r['key'] or observed.get('mode') != expected_mode
        or observed.get('characters') != expected_names or observed.get('matched_download') is not True
        or not observed.get('observer') or observed.get('actual_prompt') != r['identity']['actual_prompt']):
        raise Blocked('M2_RECONCILE: observed request, prompt, mode, references and downloaded result must match')
    with Image.open(observed['screenshot']) as im: im.verify()
    shutil.copy(observed['screenshot'], evidence)
    observed['passed'] = True
    write(q.parent / 'ui-proof.json', observed)
    shutil.copy(evidence, q.parent / 'before-submit.png')
    r.update(state='downloaded', path=str(dest.relative_to(p.job(a.job))), sha256=digest(dest),
             verification=a.note, reconciliation_evidence=str(evidence.relative_to(p.job(a.job))))
    write(q, r);p.event(a.job, 'images', 'flow_reconciled', json.dumps({'request': a.request, 'note': a.note}))
    return r
