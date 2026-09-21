#!/usr/bin/env python3
"""Rehearsal stand-in for Google Flow image generation.

This module NEVER talks to Google Flow. It exists so a full end-to-end
"dress rehearsal" of the pipeline (real content, real TTS, real render) can
run in a sandbox without a logged-in Flow session or a human watching the
browser. It does this by pre-populating the exact `flow/attempts/<key>/`
journal folders that `image_pipeline.request()` would otherwise create after
a real, successful Flow submission -- so that when the real orchestrator
(`pilot.py` / `image_pipeline.produce()`) runs, every `request()` call hits
the "already downloaded" cache branch and never calls `adapters.gflow()`.

`image_pipeline.py` itself is never modified and never even imported in a
patched form: this script drives the real, unmodified module and writes
data files in exactly the shape it already expects (see
`image_pipeline._plan_request`, `.request`, `.register`, `.check`).

Ethical/self-disclosure contract (see AGENTS.md "Không tạo ảnh bằng chứng
giả" and the task that produced this file) -- every artifact this module
writes announces itself as fake, at every layer:

  1. Every generated image is stamped, in large legible text, with
     "REHEARSAL STUB" plus the scene/image/ratio (or character) identifiers.
  2. Every request folder this module creates gets a `REHEARSAL_STUB`
     marker file.
  3. Every JSON document this module writes carries a top-level
     `"provider": "rehearsal-stub"` field.
  4. This module refuses to run against the real repository or its real
     `runs/` tree -- see `_guard_root()`. This is the most important gate
     here: get this wrong and a "rehearsal" could contaminate real
     production evidence.
  5. Nothing here ever writes into the real repo's `runs/`.

Usage
-----
As a library (the intended way for a future `scripts/rehearse.py`
orchestrator to call this):

    from scripts.rehearse_flow import provide
    result = provide(sandbox_root, "job-id")               # auto-detect stage
    result = provide(sandbox_root, "job-id", ["SC03"])      # just one scene
    result = provide(sandbox_root, "job-id", force=True)    # regenerate

As a CLI (thin wrapper around the same function):

    python3 scripts/rehearse_flow.py JOB --root /path/to/sandbox
    python3 scripts/rehearse_flow.py JOB --root /path/to/sandbox --request SC03 --force
"""
import argparse
import colorsys
import hashlib
import importlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# The real repository this file ships in. Deliberately computed once, from
# this file's own on-disk location, and used only to refuse to operate on
# it -- never to decide where to read code from (see `provide()`: the real,
# unmodified `pilot`/`image_pipeline` modules are always used normally).
_REAL_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REAL_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REAL_REPO_ROOT))

STUB_MARKER_NAME = 'REHEARSAL_STUB'
STUB_MARKER_TEXT = (
    'REHEARSAL STUB\n\n'
    'Everything under this folder was produced by scripts/rehearse_flow.py.\n'
    'No Google Flow request was ever made for it. It exists only so an\n'
    'end-to-end rehearsal of the content/audio/render pipeline can run\n'
    'without a real, logged-in Flow session.\n'
)


class RehearsalSafetyError(RuntimeError):
    """Raised when an operation would touch the real repository/runs tree."""


def _guard_root(root, job):
    """The most important safety gate in this file.

    Refuses to proceed if `root` resolves to the real repository, or if the
    computed destination (`root/runs/job`) would land inside the real
    repository's `runs/` tree. Both conditions are checked independently
    per the task's explicit requirement, even though the second subsumes
    the first in every case we could construct.
    """
    if not job or any(ch not in
                       'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
                       for ch in job):
        raise RehearsalSafetyError('Invalid job ID: ' + repr(job))
    resolved_root = Path(root).expanduser().resolve()
    if resolved_root == _REAL_REPO_ROOT:
        raise RehearsalSafetyError(
            f'Refusing to run: --root resolves to the real repository '
            f'({_REAL_REPO_ROOT}). rehearse_flow.py must only ever write into '
            f'a sandbox copy, never the real repo.')
    real_runs = (_REAL_REPO_ROOT / 'runs').resolve()
    destination = (resolved_root / 'runs' / job).resolve()
    if destination == real_runs or destination.is_relative_to(real_runs):
        raise RehearsalSafetyError(
            f'Refusing to run: the destination job path ({destination}) lies '
            f'inside the real repository\'s runs/ tree ({real_runs}). '
            f'rehearse_flow.py must never write real production evidence.')
    return resolved_root


def _iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Self-disclosing image generation
# --------------------------------------------------------------------------

def _stable_color(key):
    """A stable, vivid RGB triple derived from `key` (e.g. a scene_id)."""
    digest = hashlib.sha256(str(key).encode('utf-8')).digest()
    hue = digest[0] / 255.0
    saturation = 0.55 + (digest[1] / 255.0) * 0.15
    value = 0.75 + (digest[2] / 255.0) * 0.15
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (int(r * 255), int(g * 255), int(b * 255))


def _contrast_ink(rgb):
    r, g, b = rgb
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (12, 12, 12) if luminance > 0.55 else (245, 245, 245)


def _font(size):
    for candidate in (
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
    ):
        if Path(candidate).is_file():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def _stub_image(width, height, color_key, target, label_lines):
    """A self-disclosing stub frame: colored by `color_key`, stamped with
    'REHEARSAL STUB' plus every string in `label_lines` and `target`, large
    enough to read after the frame is thumbnailed or extracted from video.
    """
    width, height = max(int(width), 64), max(int(height), 64)
    bg = _stable_color(color_key)
    ink = _contrast_ink(bg)
    img = Image.new('RGBA', (width, height), bg + (255,))
    border = max(6, min(width, height) // 45)
    ImageDraw.Draw(img).rectangle(
        [border // 2, border // 2, width - 1 - border // 2, height - 1 - border // 2],
        outline=ink, width=border)

    measurer = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    max_text_width = int(width * 0.88)

    def fit(text, initial_size, min_size=10):
        size = max(int(initial_size), min_size)
        while size > min_size:
            font = _font(size)
            w = measurer.textbbox((0, 0), text, font=font)[2]
            if w <= max_text_width:
                return font
            size = max(min_size, size - max(1, size // 10))
        return _font(min_size)

    title_size = max(26, min(width, height) // 9)
    sub_size = max(15, min(width, height) // 24)
    texts = ['REHEARSAL STUB'] + [str(x) for x in label_lines if x] + [str(target)]
    lines = [(texts[0], fit(texts[0], title_size))]
    lines += [(text, fit(text, sub_size)) for text in texts[1:]]

    sizes = [measurer.textbbox((0, 0), text, font=font)[2:] for text, font in lines]
    gap = max(6, sub_size // 2)
    total_h = sum(h for _, h in sizes) + gap * (len(lines) - 1)
    max_w = max(w for w, _ in sizes)

    pad_x, pad_y = max(20, sub_size), max(14, sub_size // 2)
    panel_color = (0, 0, 0, 160) if ink[0] > 128 else (255, 255, 255, 180)
    panel_w = min(max_w + pad_x * 2, width - 4)
    panel = Image.new('RGBA', (panel_w, total_h + pad_y * 2), panel_color)
    px, py = (width - panel.width) // 2, (height - panel.height) // 2
    img.alpha_composite(panel, (max(px, 0), max(py, 0)))

    draw = ImageDraw.Draw(img)
    ty = max(py, 0) + pad_y
    for (text, font), (tw, th) in zip(lines, sizes):
        tx = (width - tw) // 2
        draw.text((tx, ty), text, font=font, fill=ink)
        ty += th + gap

    return img.convert('RGB')


def _evidence_image(kind, target):
    """A small stub 'screenshot' standing in for a UI evidence capture."""
    return _stub_image(640, 360, 'evidence:' + kind, target,
                        [kind, 'no real Flow UI was ever observed'])


def _dims_for_ratio(cfg, ratio):
    """Pixel size for `ratio`, derived from config.json's width/height --
    never a hardcoded literal. Config stores one canonical (portrait) pair;
    the other orientation is that pair swapped.
    """
    base_w = int(cfg.get('width', 1080))
    base_h = int(cfg.get('height', 1920))
    portrait = (base_w, base_h) if base_w <= base_h else (base_h, base_w)
    landscape = (portrait[1], portrait[0])
    return landscape if ratio == '16:9' else portrait


# --------------------------------------------------------------------------
# Journal population
# --------------------------------------------------------------------------

def _write_json(path, data):
    data = dict(data)
    data.setdefault('provider', 'rehearsal-stub')
    from pilot import write  # local import: sandbox-agnostic, real repo code
    write(path, data)


def _provide_one(p, j, cfg, *, target, prompt, refs, registration, base_image, label_lines, force):
    """Pre-populate one flow/attempts/<key>/ journal as already 'downloaded'.

    Uses image_pipeline._plan_request() -- the exact same identity/key
    computation a real request() call will use -- so the folder this
    creates is found and reused (cache hit) instead of triggering a real
    Flow submission when the real pipeline later runs.
    """
    import image_pipeline as ip
    from pilot import read, write, digest

    _cfg, ratio, actual_prompt, identity, key = ip._plan_request(
        p, j, target, prompt, refs, registration, base_image)

    attempts_dir = p.job(j) / 'flow/attempts'
    attempts_dir.mkdir(parents=True, exist_ok=True)
    (attempts_dir.parent / STUB_MARKER_NAME).write_text(STUB_MARKER_TEXT)

    folder = attempts_dir / key
    record_path = folder / 'request.json'
    if record_path.exists() and not force:
        existing = read(record_path)
        return {'target': target, 'key': key, 'path': existing['path'],
                'sha256': existing['sha256'], 'folder': str(folder), 'reused': True}
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    (folder / STUB_MARKER_NAME).write_text(STUB_MARKER_TEXT)

    now = time.time()
    is_registration = registration is not None
    mode = 'character-register' if is_registration else 'image'
    ref_names = [x['name'] for x in refs]

    width, height = _dims_for_ratio(cfg, '9:16' if is_registration else ratio)
    frame = _stub_image(width, height, label_lines[0] if label_lines else target, target, label_lines)
    download_dir = folder / 'download'
    download_dir.mkdir()
    result_path = download_dir / 'result.png'
    frame.save(result_path)
    result_sha = digest(result_path)

    metadata = {
        'jobId': key[:16], 'type': mode, 'prompt': actual_prompt,
        'project': cfg.get('flow_project'), 'model': cfg.get('flow_model'), 'ratio': ratio,
        'requestedOutputs': 1, 'quality': 'original', 'characters': ref_names,
        'downloadedAt': _iso(now), 'source': 'google-flow-browser', 'status': 'downloaded',
        'rehearsal_note': 'REHEARSAL STUB metadata; no Google Flow request was made.',
    }
    _write_json(result_path.with_suffix('.json'), metadata)

    preflight_png = folder / 'preflight.png'
    before_png = folder / 'before-submit.png'
    _evidence_image('PREFLIGHT', target).save(preflight_png)
    _evidence_image('BEFORE-SUBMIT', target).save(before_png)

    preflight_doc = {
        'observed_at': now, 'mode': 'image', 'model': cfg.get('flow_model'),
        'project': cfg.get('flow_project'), 'profile': cfg.get('flow_profile'),
        'credits_per_generation': 0, 'account_confirmed': True, 'observer': 'rehearsal-stub',
        'operations': ['image', 'character-register'],
        'screenshot': str(preflight_png.relative_to(p.job(j))), 'screenshot_hash': digest(preflight_png),
        'note': 'REHEARSAL STUB preflight; the Flow UI was never observed for this envelope.',
    }
    _write_json(folder / 'preflight.json', preflight_doc)

    ui_proof = {
        'mode': mode, 'characters': ref_names, 'passed': True,
        'note': 'REHEARSAL STUB UI proof; the Flow UI was never touched for this request.',
    }
    if base_image:
        ui_proof['base_image'] = str(p.path(j, base_image['path']))
    _write_json(folder / 'ui-proof.json', ui_proof)

    result = {
        'key': key, 'identity': identity, 'state': 'downloaded', 'submitted_at': now,
        'args': ['rehearsal-stub'], 'journal': str(record_path.relative_to(p.job(j))),
        'path': str(result_path.relative_to(p.job(j))), 'sha256': result_sha,
        'rehearsal': {'target': target, 'note': 'REHEARSAL STUB -- no real Flow request was made.'},
    }
    _write_json(record_path, result)

    if is_registration:
        conf = {
            'reference_hash': registration['sha256'], 'result_hash': result_sha,
            'name': registration['name'], 'matches_approved_reference': True,
            'observer': 'rehearsal-stub',
            'note': 'REHEARSAL STUB -- synthetic character registration auto-confirmed; not a real identity match.',
            'screenshot': str(before_png.relative_to(p.job(j))), 'screenshot_hash': digest(before_png),
        }
        _write_json(folder / 'confirmation.json', conf)

    return {'target': target, 'key': key, 'path': result['path'], 'sha256': result_sha,
            'folder': str(folder), 'reused': False}


def _provide_registration(p, j, cfg, ref, force):
    """Stub one character-registration journal for an approved reference.

    Returns a dict shaped exactly like image_pipeline.register_existing()'s
    return value, so it can be fed straight into a scene request's `refs`.
    """
    target = 'register:' + ref['character_id'] + ':' + ref['sha256']
    registration_arg = {'name': ref['name'], 'path': ref['path'], 'sha256': ref['sha256']}
    info = _provide_one(p, j, cfg, target=target, prompt=ref['prompt'], refs=(),
                         registration=registration_arg, base_image=None,
                         label_lines=['CHARACTER REGISTER', ref['character_id']], force=force)
    folder = Path(info['folder'])
    registration = {
        'name': ref['name'], 'character_id': ref['character_id'], 'sha256': ref['sha256'],
        'registration_hash': info['sha256'],
        'registration_journal': str((folder / 'request.json').relative_to(p.job(j))),
        'confirmation': str((folder / 'confirmation.json').relative_to(p.job(j))),
    }
    return info, registration


def _closure_with_predecessors(units, wanted_ids):
    """`wanted_ids` plus every based_on ancestor needed to keep chains valid."""
    by_id = {u['id']: u for u in units}
    result, stack = set(), list(wanted_ids)
    while stack:
        uid = stack.pop()
        if uid in result or uid not in by_id:
            continue
        result.add(uid)
        based_on = by_id[uid].get('based_on')
        if based_on:
            stack.append(based_on)
    return result


def provide(root, job, requests=None, *, force=False):
    """Pre-populate rehearsal Flow journals for `job` under sandbox `root`.

    root:     sandbox Pilot root directory (NOT the real repo -- see
              `_guard_root`). Must already be an initialised Pilot root for
              `job` (created via `pilot.py new`) with content approved.
    job:      job id.
    requests: optional list of ids restricting which SCENE units get
              stubbed (matched against a planned unit's composite id,
              image_id or scene_id -- any based_on predecessor is pulled in
              automatically so variation chains stay valid), or which
              characters get stubbed at the 'references' checkpoint
              (matched against character id, with or without the 'ref:'
              prefix). None (default) means everything needed for the
              current checkpoint. Character *registrations* at the 'final'
              checkpoint are always fully provided regardless of this
              filter, since every requested scene needs its characters
              registered.
    force:    regenerate a journal even if a 'downloaded' one already
              exists for that target (default False: idempotent reruns
              reuse what is already there).

    Returns a summary dict: {'provider', 'job', 'root', 'stage', 'provided'}
    where 'provided' lists {'target','key','path','sha256','reused'} for
    every journal touched (existing ones included, marked reused=True).

    Raises RehearsalSafetyError if `root`/`job` would touch the real repo
    or its runs/ tree. Raises pilot.Blocked for ordinary pipeline-state
    problems (e.g. content not yet approved, references not yet approved
    when asking for the 'final' checkpoint).
    """
    resolved_root = _guard_root(root, job)

    import pilot
    import image_pipeline as ip

    with pilot.locked(resolved_root):
        p = pilot.Pilot(root=resolved_root)
        try:
            c = ip.content(p, job)
            cfg = pilot.read(p.root / 'config.json')
            current_stage = ip.stage(p, job)
            provided = []

            if current_stage == 'complete':
                return {'provider': 'rehearsal-stub', 'job': job, 'root': str(resolved_root),
                        'stage': current_stage, 'provided': provided,
                        'note': 'Both image checkpoints are already approved; nothing to stub.'}

            if current_stage == 'references':
                wanted = set(requests) if requests else None
                for char in c['characters']:
                    if wanted is not None and char['id'] not in wanted and ('ref:' + char['id']) not in wanted:
                        continue
                    prompt = ip.reference_prompt(c, char)
                    info = _provide_one(p, job, cfg, target='ref:' + char['id'], prompt=prompt,
                                         refs=(), registration=None, base_image=None,
                                         label_lines=['REFERENCE', char['id']], force=force)
                    provided.append(info)
            else:
                approved_refs_env = ip.approved(p, job, 'references')
                if not approved_refs_env:
                    raise pilot.Blocked(
                        "M2_REFERENCES: references checkpoint is not approved yet; run/approve it "
                        "for real (using the stubbed reference images) before asking rehearse_flow "
                        "to provide the 'final' checkpoint.")
                refs = approved_refs_env['payload']['references']
                registrations = {}
                for ref in refs:
                    info, registration = _provide_registration(p, job, cfg, ref, force)
                    registrations[ref['character_id']] = registration
                    provided.append(info)

                units = ip.planned_units(p, job)
                if requests:
                    wanted_ids = {u['id'] for u in units
                                  if u['id'] in requests or u.get('image_id') in requests
                                  or u.get('scene_id') in requests}
                    needed_ids = _closure_with_predecessors(units, wanted_ids)
                else:
                    needed_ids = {u['id'] for u in units}

                completed = {}
                for unit in units:
                    if unit['id'] not in needed_ids:
                        continue
                    linked = [registrations[cid] for cid in unit['character_ids']]
                    base_image = completed.get(unit.get('based_on')) if unit.get('based_on') else None
                    scene_label = unit.get('scene_id', unit['id'])
                    image_label = unit.get('image_id', unit['id'])
                    ratio_label = unit.get('ratio', '')
                    info = _provide_one(p, job, cfg, target=unit['id'], prompt=unit['prompt'],
                                         refs=linked, registration=None, base_image=base_image,
                                         label_lines=[scene_label, image_label, ratio_label],
                                         force=force)
                    completed[unit['id']] = {'target': unit['id'], 'path': info['path'], 'sha256': info['sha256']}
                    provided.append(info)

            return {'provider': 'rehearsal-stub', 'job': job, 'root': str(resolved_root),
                    'stage': current_stage, 'provided': provided}
        finally:
            p.db.close()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=('Pre-populate rehearsal (fake) Google Flow image journals so a sandbox '
                     'pipeline run can pass image_pipeline checks end-to-end without a real, '
                     'logged-in Flow session. Every artifact this writes is stamped, at every '
                     'layer, as a rehearsal stub -- see this file\'s module docstring.'))
    ap.add_argument('job', help='Job id (must already exist under --root, content approved).')
    ap.add_argument('--root', required=True,
                     help='Sandbox Pilot root directory. Must NOT be the real repository or its runs/ tree.')
    ap.add_argument('--request', action='append', default=None,
                     help='Restrict to this scene/image/character id (repeatable). '
                          'Default: everything needed for the current checkpoint.')
    ap.add_argument('--force', action='store_true',
                     help='Regenerate even if a downloaded stub already exists for a target.')
    args = ap.parse_args(argv)
    try:
        result = provide(args.root, args.job, requests=args.request, force=args.force)
    except RehearsalSafetyError as ex:
        print(json.dumps({'provider': 'rehearsal-stub', 'blocked': str(ex)}, ensure_ascii=False, indent=2))
        return 2
    except Exception as ex:  # pilot.Blocked and friends
        print(json.dumps({'provider': 'rehearsal-stub', 'blocked': str(ex)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
