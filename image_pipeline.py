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
    if c.get('schema_version') not in ('2.0', '3.0'):
        raise Blocked('M2_CONTENT: create a v2 content job; legacy history is read-only')
    import re
    if any(not re.fullmatch(r'[A-Za-z0-9_-]+', x['id']) for x in c['characters']):
        raise Blocked('M2_CHARACTER_ID: use safe alphanumeric character IDs')
    return c


def planned_units(p, j):
    from scripts.story_plan import image_units, text_prompt
    c = content(p,j)
    units = image_units(c)
    if c.get('schema_version') != '3.0': return units
    brief = p.brief(j)[0]
    ratios = ['9:16','16:9'] if brief['aspect_ratio']=='dual' else [brief['aspect_ratio']]
    return [dict(u, id=u['id']+'_'+ratio.replace(':','x'), image_id=u['id'], ratio=ratio,
                 based_on=(u['based_on']+'_'+ratio.replace(':','x')) if u['based_on'] else None,
                 prompt=text_prompt(u['prompt'],u['visible_text'],brief['planning']['text_style']))
            for u in units for ratio in ratios]


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


def _preflight_problems(cfg, e, operation=None):
    """The one definition of a valid Flow image-preflight envelope.

    Shared by adapters.flow_action (which calls this when WRITING
    flow/preflight.json, for jobs with a brief) and preflight() below (which
    calls it again when READING that file back before every image/
    character-register request). Before this was unified, the writer
    accepted envelopes the reader would later refuse -- an operator could
    record preflight, see success, then have production die on M2_PREFLIGHT
    without being told which field was missing. Never relax a condition here
    without relaxing it in both places at once.

    `operation`, when given, additionally requires that specific operation to
    already be declared in the envelope's `operations` list; the writer omits
    it and only requires a non-empty list of recognised operations, since at
    write time the envelope may cover more than one upcoming operation.

    Returns a list of (code, message) pairs -- empty means valid. `code` is
    'stale' for the freshness check and 'other' for everything else, so a
    caller can tell a plain expiry (normal mid-production event) apart from a
    genuinely malformed envelope.
    """
    problems = []
    # No profile name is hardcoded here: an envelope must name the profile the
    # config actually points at (or one listed in flow_profiles). 'video-pilot'
    # used to be accepted unconditionally, which meant evidence could claim a
    # profile the production run never used.
    valid_profiles = {cfg['flow_profile']}
    if 'flow_profiles' in cfg: valid_profiles.update(cfg['flow_profiles'])
    if e.get('credits_per_generation') != 0:
        problems.append(('other', 'credits_per_generation must be observed as 0'))
    window = cfg.get('preflight_window_seconds', 600)
    observed_at = e.get('observed_at')
    if not isinstance(observed_at, (int, float)) or not 0 <= time.time() - observed_at <= window:
        problems.append(('stale', f'observed_at must be a fresh UI observation within the last {window}s'))
    if e.get('mode') != 'image':
        problems.append(('other', "mode must be observed as 'image'"))
    if e.get('model') != cfg['flow_model']:
        problems.append(('other', 'model must match config flow_model'))
    if e.get('project') != cfg['flow_project']:
        problems.append(('other', 'project must match config flow_project'))
    if e.get('profile') not in valid_profiles:
        problems.append(('other', 'profile must be an allowed Flow profile'))
    if not e.get('account_confirmed'):
        problems.append(('other', 'account_confirmed must be true'))
    if not e.get('observer'):
        problems.append(('other', 'observer required'))
    ops = e.get('operations')
    if not isinstance(ops, list) or not ops or any(o not in ('image', 'character-register') for o in ops):
        problems.append(('other', "operations must be a non-empty list drawn from 'image'/'character-register'"))
    elif operation is not None and operation not in ops:
        problems.append(('other', f'operations must include {operation!r}'))
    if not e.get('screenshot'):
        problems.append(('other', 'screenshot required'))
    return problems


def validate_preflight_evidence(cfg, e, operation=None):
    """Raise Blocked naming every missing/invalid field, or return silently."""
    problems = _preflight_problems(cfg, e, operation)
    if problems:
        codes = {c for c, _ in problems}
        tag = 'M2_PREFLIGHT_EXPIRED' if codes == {'stale'} else 'M2_PREFLIGHT'
        raise Blocked(tag + ': ' + '; '.join(m for _, m in problems))


def preflight(p, j, operation):
    cfg = read(p.root / 'config.json')
    if cfg.get('video_generation') or cfg.get('credit_budget', 0) != 0:
        raise Blocked('M2_POLICY: credit budget must be non-negative')
    path = p.job(j) / 'flow/preflight.json'
    e = read(path) if path.exists() else {}
    validate_preflight_evidence(cfg, e, operation)
    if digest(p.path(j, e['screenshot'])) != e['screenshot_hash']:
        raise Blocked('M2_PREFLIGHT: screenshot changed')
    return e


def _preflight_expiry_message(done, total):
    """Friendly M2_PREFLIGHT_EXPIRED framing for a mid-run expiry.

    A dual-ratio job with dozens of scene images, each taking tens of seconds
    through the browser, will routinely outlast a single 10-minute (or
    config-configured) observation window. That is expected, not a failure:
    every image finished so far is already downloaded and kept (journals are
    per-identity and never resubmitted), so re-observing the Flow UI and
    resuming picks up exactly where this stopped.

    gflow_guard.mjs's applySettings() independently re-verifies the *live*
    model/ratio/output-count on every single job it submits and throws if it
    can't -- that is stronger, real-time proof than this stale screenshot, so
    the only thing actually lost on expiry is the human observation of
    mode/account/credits, which is what re-observing restores.
    """
    return (f'M2_PREFLIGHT_EXPIRED: Flow UI observation window elapsed mid-run '
            f'({done}/{total} images already downloaded and kept; nothing new was submitted). '
            f'This is expected for a long production run, not an error. Re-observe the Flow UI '
            f'(image mode, model, project, account, 0 credits) and record a fresh flow-preflight, '
            f'then resume the same command -- it will only submit what is left. '
            f'(gflow_guard.mjs already re-verifies the live model/ratio/output settings on every '
            f'job it runs; this window only covers what that cannot see.)')


def _reraise_if_expired(ex, done, total):
    if 'M2_PREFLIGHT_EXPIRED' in str(ex):
        raise Blocked(_preflight_expiry_message(done, total)) from ex
    raise ex


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


def requested_prompt(p, j, target, prompt, notes, ratio, registration=False):
    from scripts.story_plan import safe_corrections, text_prompt
    from prompt_templates import image_prompt
    c = content(p,j)
    corrections = safe_corrections(c, notes)
    revised = prompt + ('\nRequested corrections (keep the approved visible-text list unchanged): '+corrections if corrections else '') if c.get('schema_version')=='3.0' else prompt + ('\nRequested corrections: '+corrections if corrections else '')
    unit = next((x for x in planned_units(p,j) if x['id']==target),None)
    if unit and c.get('schema_version')=='3.0':
        revised = text_prompt(revised,unit['visible_text'],p.brief(j)[0]['planning']['text_style'])
    return revised if registration else image_prompt(revised,ratio)


def _plan_request(p, j, target, prompt, refs, registration, base_image):
    """Identity/key computation shared by request() and the batch pre-pass.

    Kept side-effect-free (besides the read-only validation content() already
    does) so the batch path can compute the exact same journal key a normal
    request() call would, without submitting anything itself.
    """
    content(p, j)  # schema/character-id validation; result unused below.
    if not target.startswith('ref:') and not approved(p, j, 'references'):
        raise Blocked('M2_REFERENCES: approve references first')
    scene = next((x for x in planned_units(p,j) if x['id'] == target), None)
    if scene:
        approved_refs = approved(p, j, 'references')['payload']['references']
        linked = [register_existing(p, j, next(x for x in approved_refs if x['character_id'] == cid)) for cid in scene['character_ids']]
        if list(refs) != linked or prompt != scene['prompt']:
            raise Blocked('M2_REFERENCE_LINK: scene request must use approved prompt and registered characters')
    cfg = read(p.root / 'config.json')
    edit_target = scene.get('scene_id',target) if scene else target
    corrections = '\n'.join(x['note'] for x in edits(p, j, edit_target))
    ratio = scene.get('ratio') if scene and scene.get('ratio') else ('16:9' if p.brief(j)[0]['aspect_ratio']=='16:9' else '9:16')
    if scene and scene.get('based_on'):
        if not base_image or base_image.get('target') != scene['based_on'] or digest(p.path(j,base_image['path'])) != base_image['sha256']:
            raise Blocked('M2_BASE_IMAGE: prior image required for variation')
    elif base_image:
        raise Blocked('M2_BASE_IMAGE: unexpected reference image')
    actual_prompt = requested_prompt(p,j,target,prompt,corrections,ratio,bool(registration))
    # Identity must track content (name/sha256), never the incidental copy path a
    # revision folder happens to use today: that path churns every produce() run
    # and must not force a real character re-registration.
    identity_registration = {'name': registration['name'], 'sha256': registration['sha256']} if registration else None
    identity = {'target': target,
                'prompt': prompt, 'actual_prompt': actual_prompt, 'model': cfg['flow_model'], 'ratio': ratio,
                'references': list(refs), 'edits': edits(p, j, edit_target), 'base_image': base_image,
                'registration': identity_registration, 'config_hash': digest(p.root / 'config.json')}
    return cfg, ratio, actual_prompt, identity, hashobj(identity)


def _unresolved_conflict(p, j, target):
    """An existing journal for the same target that is not yet resolved.

    Shared by request() (which must refuse a second submission while one is
    unresolved) and the batch pre-pass (which must not even offer such a
    target to gflow batch).
    """
    base = p.job(j) / 'flow/attempts'
    if not base.exists():
        return None
    for q in base.glob('*/request.json'):
        old = read(q)
        same_target = old['identity']['target'] == target
        if target.startswith('register:'):
            same_target = old['identity']['target'].rsplit(':', 1)[0] == target.rsplit(':', 1)[0]
        if same_target and old['state'] in ('submitted', 'ambiguous'):
            return old
    return None


def request(p, j, target, prompt, refs=(), registration=None, base_image=None):
    """One durable journal per identity; unknown outcomes are never retried."""
    import adapters
    p.gate(j, 'images')
    cfg, ratio, actual_prompt, identity, key = _plan_request(p, j, target, prompt, refs, registration, base_image)
    base = p.job(j) / 'flow/attempts'
    base.mkdir(parents=True, exist_ok=True)
    # Even changed prompts/edits cannot hide an unresolved submission.
    conflict = _unresolved_conflict(p, j, target)
    if conflict:
        raise Blocked('M2_AMBIGUOUS: reconcile request ' + conflict['key'] + ' before another submission')
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
        if base_image:
            args += ['--base-image', str(p.path(j,base_image['path']))]
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
        if base_image and proof.get('base_image') != str(p.path(j,base_image['path'])):
            raise Blocked('M2_BASE_IMAGE: UI attachment evidence missing')
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


def batch_submit(p, j, units, registrations):
    """Optional bulk path: one `gflow batch` call pre-populates journals for a
    ratio group's independent images, so the normal request() calls that
    follow just hit the cache. Gated by config flow_batch (default off, read
    via cfg.get('flow_batch', False)) -- see produce(). Never called for the
    references stage.

    Scope is deliberately narrow: only images with based_on absent (no
    variation chain) are ever offered to the batch. A chained variation
    needs its predecessor's file physically attached and UI-verified as an
    upload before submission; the single-image request() path already does
    that carefully, and this pre-pass does not attempt to reproduce it, so
    chains always fall through to request() individually.

    Failure handling mirrors the single-image path exactly: a job that
    completes but fails verification, or that gflow reports failed, becomes
    an 'ambiguous' journal (never auto-resent; needs flow-reconcile). A job
    the batch never got to (process crashed, hard-stop mid-run) is left with
    no journal at all, so it is simply retried through the normal per-image
    path next time -- nothing already completed is touched or resent.
    """
    import adapters
    cfg = read(p.root / 'config.json')
    plans = []
    for unit in units:
        if unit.get('based_on'):
            continue  # variation chains always use the single-image path
        if _unresolved_conflict(p, j, unit['id']):
            continue  # let request() raise M2_AMBIGUOUS as usual
        linked = [registrations[x] for x in unit['character_ids']]
        _, plan_ratio, actual_prompt, identity, key = _plan_request(p, j, unit['id'], unit['prompt'], linked, None, None)
        if (p.job(j) / 'flow/attempts' / key / 'request.json').exists():
            continue  # already resolved (e.g. downloaded on a prior run)
        plans.append({'unit': unit, 'ratio': plan_ratio, 'actual_prompt': actual_prompt,
                      'identity': identity, 'key': key, 'linked': linked})
    if not plans:
        return
    evidence = preflight(p, j, 'image')  # one preflight for the whole batch
    model_arg = 'nano-banana-pro' if 'pro' in cfg['flow_model'].lower() else ('nano-banana-2' if '2' in cfg['flow_model'] else cfg['flow_model'])
    batch_id = hashobj([x['key'] for x in plans])[:16]
    batch_dir = p.job(j) / 'flow/batches' / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for plan in plans:
        folder = p.job(j) / 'flow/attempts' / plan['key']
        folder.mkdir(parents=True, exist_ok=True)
        write(folder / 'preflight.json', evidence)
        shutil.copy(p.path(j, evidence['screenshot']), folder / 'preflight.png')
        jobs.append({'id': plan['key'][:16], 'type': 'image', 'project': cfg['flow_project'],
                     'prompt': plan['actual_prompt'], 'model': model_arg, 'ratio': plan['ratio'],
                     'outputs': 1, 'character': [x['name'] for x in plan['linked']], 'out': str(batch_dir)})
        plan['folder'], plan['job_id'] = folder, plan['key'][:16]
    jobs_by_id = {job['id']: (job, plan) for job, plan in zip(jobs, plans)}
    jobs_file = batch_dir / 'jobs.json'
    write(jobs_file, {'jobs': jobs})
    args = ['batch', str(jobs_file), '--out', str(batch_dir), '--profile', cfg['flow_profile'], '--continue-on-failure']
    try:
        r = adapters.gflow(p, *args, timeout=max(960, 300 * len(jobs)))
        (batch_dir / 'command.log').write_text(r.stdout + '\n' + r.stderr)
    except Exception as ex:
        (batch_dir / 'command.log').write_text('EXCEPTION: ' + str(ex))
    run_state_path = batch_dir / 'gflow-run.json'
    if not run_state_path.exists():
        return  # nothing attempted; leave every plan unjournaled for a plain retry
    run_state = read(run_state_path)
    for entry in run_state.get('jobs', []):
        found = jobs_by_id.get(entry.get('id'))
        if not found or entry.get('status') not in ('completed', 'failed'):
            continue  # never attempted (batch stopped early) -- retry normally later
        job, plan = found
        folder, key, identity = plan['folder'], plan['key'], plan['identity']
        record = folder / 'request.json'
        if record.exists():
            continue
        result = {'key': key, 'identity': identity, 'state': 'submitted', 'submitted_at': time.time(),
                  'args': job, 'journal': str(record.relative_to(p.job(j)))}
        if entry['status'] == 'failed':
            result.update(state='ambiguous', error=entry.get('error', 'batch job failed'))
            write(record, result)
            p.event(j, 'images', 'flow_batch_ambiguous', key)
            continue
        try:
            job_evidence_dir = batch_dir / '.evidence' / plan['job_id']
            ui_proof_path, before_submit_path = job_evidence_dir / 'ui-proof.json', job_evidence_dir / 'before-submit.png'
            if not ui_proof_path.is_file() or not before_submit_path.is_file():
                raise Blocked('Flow UI attachment/mode evidence missing')
            proof = read(ui_proof_path)
            expected_names = [x['name'] for x in plan['linked']]
            if proof.get('passed') is not True or proof.get('characters') != expected_names:
                raise Blocked('Flow UI attachment/mode evidence missing')
            if proof.get('mode') != 'image':
                raise Blocked('Flow UI mode evidence differs')
            with Image.open(before_submit_path) as im: im.verify()
            image_files = [Path(a) for a in entry.get('artifacts', []) if Path(a).suffix.lower() in ('.png', '.jpg', '.jpeg')]
            if len(image_files) != 1:
                raise Blocked('Cannot identify exactly one downloaded result')
            f = image_files[0]
            with Image.open(f) as im: im.verify()
            metadata = read(f.with_suffix('.json'))
            if (metadata.get('jobId') != plan['job_id'] or metadata.get('type') != 'image'
                or metadata.get('prompt') != plan['actual_prompt'] or metadata.get('ratio') != plan['ratio']
                or metadata.get('characters', []) != expected_names
                or metadata.get('source') != 'google-flow-browser' or metadata.get('status') != 'downloaded'):
                raise Blocked('Downloaded metadata does not match request')
            dest = folder / ('result' + f.suffix)
            shutil.copy(f, dest)
            shutil.copy(ui_proof_path, folder / 'ui-proof.json')
            shutil.copy(before_submit_path, folder / 'before-submit.png')
            shutil.copy(f.with_suffix('.json'), dest.with_suffix('.json'))
            result.update(state='downloaded', path=str(dest.relative_to(p.job(j))), sha256=digest(dest))
            write(record, result)
            image_check(p, j, result['path'], result['sha256'], full=True)
            p.event(j, 'images', 'flow_batch_downloaded', key)
        except Exception as ex:
            result.update(state='ambiguous', error=str(ex))
            write(record, result)
            p.event(j, 'images', 'flow_batch_ambiguous', key)


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
        chars = c['characters']
        for i, char in enumerate(chars):
            prompt = reference_prompt(c, char)
            try:
                r = request(p, j, 'ref:' + char['id'], prompt)
            except Blocked as ex:
                _reraise_if_expired(ex, i, len(chars))
            name = j + '-' + char['id'] + '-' + r['key'][:12]
            asset = attach(p, j, r, 'REF-' + char['id'], prompt, [], out)
            refs.append(dict(asset, character_id=char['id'], name=name))
    else:
        refs = approved(p, j, 'references')['payload']['references']
        registrations = {}
        for i, r0 in enumerate(refs):
            try:
                registrations[r0['character_id']] = register(p, j, r0)
            except Blocked as ex:
                _reraise_if_expired(ex, i, len(refs))
        scenes = planned_units(p,j)
        import concurrent.futures
        cfg = read(p.root / 'config.json')
        concurrency = cfg.get('concurrency', 3)

        completed = {}
        def process_scene(scene):
            linked = [registrations[x] for x in scene['character_ids']]
            base = completed.get(scene.get('based_on'))
            r = request(p, j, scene['id'], scene['prompt'], linked, **({'base_image':base} if base else {}))
            completed[scene['id']] = {'target':scene['id'],'path':r['path'],'sha256':r['sha256']}
            return (scene['id'], scene['prompt'], linked, r)

        # Flow's aspect-ratio/model/output toggles are one global UI setting;
        # flipping it per image is wasteful and unsafe under parallel workers.
        # Finish every image of one ratio before starting the next. Scenes
        # within a ratio still run in parallel; variations inside one scene
        # stay sequential because based_on chains to the immediately preceding
        # image of that same scene, and planned_units keeps the ratio suffix
        # aligned so a chain never crosses ratios.
        ratio_order, ratio_groups = [], {}
        for unit in scenes:
            rk = unit.get('ratio')
            if rk not in ratio_groups:
                ratio_groups[rk] = {}
                ratio_order.append(rk)
            ratio_groups[rk].setdefault(unit.get('scene_id',unit['id']), []).append(unit)

        def process_group(group):
            return [(unit, process_scene(unit)) for unit in group]

        # Optional bulk path (default off; see batch_submit's docstring). Pre-
        # populates journals for each ratio's independent images with a single
        # gflow batch call; the per-scene loop below is unchanged either way
        # and simply hits the cache for anything the batch already resolved.
        if cfg.get('flow_batch', False):
            for rk in ratio_order:
                units_in_ratio = [u for group in ratio_groups[rk].values() for u in group]
                batch_submit(p, j, units_in_ratio, registrations)

        outcomes = {}
        try:
            for rk in ratio_order:
                with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                    for results in executor.map(process_group, ratio_groups[rk].values()):
                        for unit, outcome in results:
                            outcomes[unit['id']] = outcome
        except Blocked as ex:
            # Any request() already in flight when the window lapsed finishes
            # to a determinate state (downloaded/ambiguous) before this is
            # raised -- ThreadPoolExecutor's context manager waits for every
            # submitted unit, it just never starts a new one. Nothing here
            # resubmits; only the message is enriched with progress.
            _reraise_if_expired(ex, len(outcomes), len(scenes))

        # Re-assemble in the original planned order (scene-major, ratio-minor)
        # regardless of the ratio-major order used to submit requests above.
        for unit in scenes:
            scene_id, prompt, linked, r = outcomes[unit['id']]
            item = attach(p, j, r, scene_id, prompt, linked, out)
            if c.get('schema_version') == '3.0':
                item.update(scene_id=unit['scene_id'],image_id=unit['image_id'],ratio=unit['ratio'])
            items.append(item)

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
    expected = [] if s == 'references' else planned_units(p,j)
    if [(x.get('image_id')+'_'+x['ratio'].replace(':','x')) if x.get('image_id') else x['scene_id'] for x in data['items']] != [x['id'] for x in expected]:
        raise Blocked('M2_SCENES: missing/duplicate/reordered scenes')
    if s != 'references':
        a = approved(p, j, 'references')
        if not a or data['references'] != a['payload']['references']:
            raise Blocked('M2_REFERENCES: references not approved')
    for item, scene in zip(data['items'], expected):
        if item['scene_id'] != scene.get('scene_id',scene['id']): raise Blocked('M2_SCENE_LINK: wrong parent scene')
        if scene.get('ratio'):
            with Image.open(p.path(j,item['path'])) as im:
                target_ratio = 16/9 if scene['ratio']=='16:9' else 9/16
                if abs(im.width/im.height-target_ratio)>.04: raise Blocked('M2_RATIO: image does not match planned output')
        item_request = read(p.path(j,item['request']))
        if item_request['identity']['target'] != scene['id']: raise Blocked('M2_SCENE_LINK: wrong image request target')
        req_base = item_request['identity'].get('base_image')
        if scene.get('based_on'):
            prior = next((x for x in data['items'] if x.get('image_id','')+'_'+x.get('ratio','').replace(':','x')==scene['based_on']),None)
            if not prior or not req_base or req_base['target']!=scene['based_on'] or req_base['sha256']!=prior['sha256']:
                raise Blocked('M2_BASE_IMAGE: wrong planned predecessor')
        elif req_base: raise Blocked('M2_BASE_IMAGE: unexpected predecessor')
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
        expected_prompt = requested_prompt(p,j,req['identity']['target'],item['prompt'],changes,req['identity']['ratio'])
        if item['actual_prompt'] != expected_prompt:
            raise Blocked('M2_PROMPT: actual prompt differs from configured template')
        if (req['state'] != 'downloaded'
            or req['identity']['prompt'] != item['prompt'] or req['identity']['actual_prompt'] != item['actual_prompt'] or req['sha256'] != item['sha256']
            or req['identity']['references'] != item['references']):
            raise Blocked('M2_EVIDENCE: request does not match downloaded asset')
        files.extend([item['request'], req['path']])
        if not req.get('reconciliation_evidence'): files.append(str(p.path(j, req['path']).with_suffix('.json').relative_to(p.job(j))))
        if req.get('reconciliation_evidence'): files.append(req['reconciliation_evidence'])
        base = p.path(j, item['request']).parent
        files.extend(str((base / n).relative_to(p.job(j))) for n in ['preflight.json', 'preflight.png', 'ui-proof.json', 'before-submit.png'])
        ui = read(base / 'ui-proof.json')
        base_image = req['identity'].get('base_image')
        if base_image:
            if digest(p.path(j,base_image['path'])) != base_image['sha256'] or ui.get('base_image') != str(p.path(j,base_image['path'])):
                raise Blocked('M2_BASE_IMAGE: reference or evidence changed')
            files.append(base_image['path'])
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


def record_preflight(p, a):
    """Write flow/preflight.json for a job with a brief (see flow_action).

    Validates with the exact same validate_preflight_evidence() that
    preflight() uses to READ this file back before every image/character-
    register request, so an envelope accepted here can never be rejected
    later for a field this writer didn't check -- that mismatch (missing
    `project`/`operations`) was the whole reason this now lives next to the
    reader instead of duplicated in adapters.flow_action.
    """
    j = a.job
    if not a.evidence:
        raise Blocked('Supply --evidence JSON recording observed UI and screenshot')
    cfg = read(p.root / 'config.json')
    e = read(a.evidence)
    validate_preflight_evidence(cfg, e)
    shot = Path(e['screenshot']).resolve()
    with Image.open(shot) as im: im.verify()
    dest = p.job(j) / 'flow/preflight.png'
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(shot, dest)
    e['screenshot'] = str(dest.relative_to(p.job(j)))
    e['screenshot_hash'] = digest(dest)
    write(p.job(j) / 'flow/preflight.json', e)
    p.event(j, 'images', 'ui_preflight_recorded', json.dumps(e, ensure_ascii=False))
    window = cfg.get('preflight_window_seconds', 600)
    return {'preflight': f'recorded, expires in {window} seconds; visual observation is not machine proof'}


def flow_action(p, a):
    p.gate(a.job, 'images')
    if a.command == 'flow-preflight':
        return record_preflight(p, a)
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
    base_image = r['identity'].get('base_image')
    if base_image and observed.get('base_image') != str(p.path(a.job,base_image['path'])):
        raise Blocked('M2_RECONCILE: base image attachment must be observed')
    observed['passed'] = True
    write(q.parent / 'ui-proof.json', observed)
    shutil.copy(evidence, q.parent / 'before-submit.png')
    r.update(state='downloaded', path=str(dest.relative_to(p.job(a.job))), sha256=digest(dest),
             verification=a.note, reconciliation_evidence=str(evidence.relative_to(p.job(a.job))))
    write(q, r);p.event(a.job, 'images', 'flow_reconciled', json.dumps({'request': a.request, 'note': a.note}))
    return r
