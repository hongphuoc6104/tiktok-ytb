"""image_pipeline <-> FlowPool bridge. Used only when config `flowpool_enabled` is true.

`gflow()` is a drop-in for adapters.gflow('image' | 'batch'): it writes the same
files image_pipeline already verifies (one image + metadata JSON in --out,
ui-proof.json in the evidence folder, gflow-run.json for batches). Commands that
never reach Flow (registration, auth, local mascot composition) stay on adapters.
"""
import json
import shutil
import subprocess
from pathlib import Path

from pilot import Blocked, digest, read, write
import characters
from . import prompts
from .decisions import Decisions

MASCOT = 'assets/characters/channel-mascot/reference-v1.png'  # default/vocab mascot; see characters.resolve()


def config(p):
    cfg = read(p.root / 'config.json')
    cfg.setdefault('flowpool_state_dir', str(p.root / 'flowpool'))
    return cfg


def _decisions(p):
    return Decisions(Path(config(p)['flowpool_state_dir']) / 'decisions.ndjson')


def _channel(p, job):
    try:
        found = p.brief(job) if job else None
    except Exception:
        found = None
    return (found[0] if found else {}).get('channel')


def _target_of(out_folder):
    """image_pipeline's target id (e.g. SC01_I1_16x9) from the attempt's request.json, if any."""
    try:
        return read(Path(out_folder).parent / 'request.json')['identity']['target']
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _run(p, requests):
    import flowpool
    return flowpool.run(requests, config(p))


def _arg(args, flag, default=None):
    if flag in args and args.index(flag) + 1 < len(args):
        return args[args.index(flag) + 1]
    return default


def _characters(args):
    if '--character' not in args:
        return []
    out = []
    for item in args[args.index('--character') + 1:]:
        if item.startswith('--'):
            break
        out.append(item)
    return out


def _job_of(path):
    parts = Path(path).resolve().parts
    return parts[parts.index('runs') + 1] if 'runs' in parts and parts.index('runs') + 1 < len(parts) else None


def blocked_from(result):
    """Translate a FlowPool result into the Blocked flags image_pipeline understands."""
    ex = Blocked(f"FlowPool {result['status']}: {result.get('code') or ''} {result.get('error') or ''}".strip())
    ex.generation_submitted = not (result['status'] == 'failed' and result.get('state') == 'not_submitted')
    ex.collection_only = False
    return ex


def _place_choice(p, result, dest_stem):
    """Copy the chosen variant (user pick > ranked best > first) to `<dest_stem><ext>`."""
    chosen, why = _decisions(p).choose(result)
    if not chosen:
        raise Blocked('FlowPool returned no file')
    dest = Path(str(dest_stem) + Path(chosen).suffix)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(chosen, dest)
    return dest, chosen, why


def _write_image_evidence(p, out_folder, evidence_folder, result, job_id, prompt, ratio, chars, base_img, flow_prompt=None):
    src, chosen, why = _place_choice(p, result, out_folder / f'{job_id}-1')
    files = result.get('files') or []
    media = (result.get('media_ids') or [None] * len(files))[files.index(chosen)] if chosen in files else None
    write(src.with_suffix('.json'), {'jobId': job_id, 'type': 'image', 'prompt': prompt, 'ratio': ratio,
                                     'characters': chars, 'source': 'google-flow-browser', 'status': 'downloaded',
                                     'forgeId': media, 'profile': result.get('profile'), 'flow_prompt': flow_prompt,
                                     'variants': files, 'chosen': chosen, 'choice': why})
    evidence_folder.mkdir(parents=True, exist_ok=True)
    proof = {'passed': True, 'mode': 'image', 'characters': chars, 'tool': 'flowpool', 'forgeId': media,
             'profile': result.get('profile')}
    if base_img:
        proof['base_image'] = base_img
    write(evidence_folder / 'ui-proof.json', proof)
    return src


def gflow(p, *args, timeout=960):
    import adapters
    args = list(args)
    if args[:1] == ['batch']:
        return _batch(p, args)
    chars, base_img = _characters(args), _arg(args, '--base-image')
    if args[:1] != ['image'] or not (chars or base_img):
        return adapters.gflow(p, *args, timeout=timeout)
    out_folder = Path(_arg(args, '--out')).resolve()
    # The channel-resolved mascot (never a hard-coded vocab path); same
    # local-composition rule as adapters.gflow applies when it can't be
    # resolved here (e.g. no job context) -- delegate rather than guess.
    mascot = characters.try_mascot_for(p, _job_of(out_folder))
    if not mascot:
        return adapters.gflow(p, *args, timeout=timeout)
    out_folder.mkdir(parents=True, exist_ok=True)
    job_id, prompt, ratio = _arg(args, '--id'), _arg(args, '--prompt', ''), _arg(args, '--ratio', '16:9')
    job = _job_of(out_folder)
    refs = [str(mascot['reference_path'])] + ([str(Path(base_img).resolve())] if base_img else [])
    flow_prompt = prompts.image_prompt(prompt, ratio, prompts.channel_style(p.root, _channel(p, job)), mascot, bool(base_img))
    # Variants live next to --out, not inside it: request() expects exactly one image in --out.
    [result] = _run(p, [{'id': job_id, 'kind': 'image', 'prompt': flow_prompt, 'ratio': ratio, 'refs': refs,
                         'variants': int(config(p).get('flowpool_image_variants') or 1), 'job': job,
                         'scene': _target_of(out_folder), 'target': _target_of(out_folder),
                         'out_dir': str(out_folder.parent / 'variants')}])
    if result['status'] != 'ok':
        raise blocked_from(result)
    evidence = Path(_arg(args, '--evidence-out', str(out_folder.parent)))
    dest = _write_image_evidence(p, out_folder, evidence, result, job_id, prompt, ratio, chars, base_img, flow_prompt)
    return subprocess.CompletedProcess(args, 0, stdout=f'FlowPool generated: {dest}', stderr='')


def _batch(p, args):
    data = read(Path(args[1]))
    batch_out = Path(_arg(args, '--out')).resolve()
    batch_out.mkdir(parents=True, exist_ok=True)
    jobs = data.get('jobs', [])
    # Every job in a FlowPool batch gets the same raw reference image (no
    # per-character lookup here), so this resolves the *channel's* mascot --
    # never a hard-coded vocab path -- and fails loudly and early rather
    # than silently sending a different channel's mascot.
    mascot = str(characters.mascot_for(p, characters.job_of(batch_out))['reference_path'])
    state_file = batch_out / 'gflow-run.json'
    run_jobs = [{'id': job['id'], 'status': 'failed', 'error': 'Submission pending; reconcile before retry'} for job in jobs]
    # Persist attempted membership before the external call.
    write(state_file, {'jobs': run_jobs})
    style = prompts.channel_style(p.root, _channel(p, _job_of(batch_out)))
    resolved = characters.try_mascot_for(p, characters.job_of(batch_out))
    variants = int(config(p).get('flowpool_image_variants') or 1)
    requests = [{'id': job['id'], 'kind': 'image', 'ratio': job.get('ratio', '9:16'),
                 'prompt': prompts.image_prompt(job['prompt'], job.get('ratio', '9:16'), style, resolved),
                 'refs': [mascot], 'variants': variants, 'job': _job_of(batch_out), 'out_dir': str(batch_out / job['id'])}
                for job in jobs]
    try:
        results = {r['id']: r for r in _run(p, requests)}
    except Exception as ex:
        raise Blocked(f'FlowPool batch stopped; reconcile attempted requests: {ex}')
    for job, entry in zip(jobs, run_jobs):
        r = results.get(job['id'])
        if not r:
            continue
        if r['status'] == 'ok':
            dst, chosen, why = _place_choice(p, r, batch_out / job['id'])
            chars = job.get('character', [])
            write(dst.with_suffix('.json'), {'jobId': job['id'], 'type': 'image', 'prompt': job['prompt'],
                                             'ratio': job.get('ratio', '9:16'), 'characters': chars,
                                             'source': 'google-flow-browser', 'status': 'downloaded',
                                             'forgeId': (r.get('media_ids') or [None])[0], 'profile': r.get('profile')})
            ev = batch_out / '.evidence' / job['id']
            ev.mkdir(parents=True, exist_ok=True)
            write(ev / 'ui-proof.json', {'passed': True, 'mode': 'image', 'characters': chars, 'tool': 'flowpool',
                                         'forgeId': (r.get('media_ids') or [None])[0], 'profile': r.get('profile')})
            entry.update(status='completed', artifacts=[str(dst)])
            entry.pop('error', None)
        elif r['status'] == 'failed' and r.get('state') == 'not_submitted':
            entry.update(status='not_submitted', error=r.get('error') or '')
        else:
            entry.update(status='failed', error=f"{r['status']}: {r.get('error') or ''}")
    write(state_file, {'jobs': run_jobs})
    return subprocess.CompletedProcess(args, 0, stdout='Batch completed via FlowPool', stderr=json.dumps(
        {k: v['status'] for k, v in results.items()}))


def clip(p, request):
    """One Veo frames-to-video request; returns the FlowPool result (with `chosen`)
    or raises Blocked. The motion prompt is wrapped with the channel's clip rules."""
    cfg = config(p)
    style = prompts.channel_style(p.root, _channel(p, request.get('job')))
    flow_prompt = prompts.clip_prompt(request['prompt'], int(cfg.get('flowpool_clip_seconds') or 8), style)
    [result] = _run(p, [dict(request, kind='clip', prompt=flow_prompt)])
    if result['status'] != 'ok':
        raise blocked_from(result)
    result['chosen'], result['choice'] = _decisions(p).choose(result)
    result['flow_prompt'] = flow_prompt
    return result


def apply_pick(p, j, result):
    """Swap a downloaded image for the variant the user picked in the dashboard.

    Only a file that FlowPool itself produced (validated) for this very request
    can be picked. The swap changes the candidate's hash, so any earlier media
    approval no longer matches and the normal review gate applies again."""
    args = result.get('args') if isinstance(result.get('args'), list) else []
    job_id = _arg(args, '--id')
    if not job_id or result.get('state') != 'downloaded':
        return result
    pick = _decisions(p).latest('pick', request_id=job_id)
    if not pick or not Path(pick.get('file') or '').is_file():
        return result
    import flowpool
    journal = flowpool.FlowPool(config(p)).journal
    produced = {o['path'] for s in journal.by_request_id(job_id) if s['state'] == 'validated' for o in s.get('outputs') or []}
    if pick['file'] not in produced or digest(Path(pick['file'])) == result.get('sha256'):
        return result
    current = p.path(j, result['path'])
    dest = current.with_suffix(Path(pick['file']).suffix)
    meta = read(current.with_suffix('.json')) if current.with_suffix('.json').is_file() else {}
    shutil.copy(pick['file'], dest)
    if dest != current:
        current.unlink(missing_ok=True)
        current.with_suffix('.json').unlink(missing_ok=True)
    meta.update(chosen=pick['file'], choice='user_pick')
    write(dest.with_suffix('.json'), meta)
    result.update(path=str(dest.relative_to(p.job(j))), sha256=digest(dest), picked_at=pick['at'])
    record = p.path(j, result['journal'])
    write(record, result)
    p.event(j, 'images', 'flowpool_variant_picked', job_id)
    return result
