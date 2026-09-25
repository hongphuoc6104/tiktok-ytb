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

from pilot import Blocked, read, write

MASCOT = 'assets/characters/channel-mascot/reference-v1.png'


def config(p):
    cfg = read(p.root / 'config.json')
    cfg.setdefault('flowpool_state_dir', str(p.root / 'flowpool'))
    return cfg


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


def _write_image_evidence(out_folder, evidence_folder, result, job_id, prompt, ratio, chars, base_img):
    src = Path(result['files'][0])
    media = (result.get('media_ids') or [None])[0]
    write(src.with_suffix('.json'), {'jobId': job_id, 'type': 'image', 'prompt': prompt, 'ratio': ratio,
                                     'characters': chars, 'source': 'google-flow-browser', 'status': 'downloaded',
                                     'forgeId': media, 'profile': result.get('profile')})
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
    mascot = p.root / MASCOT
    # Same local-composition rule as adapters.gflow: no Flow call there.
    if args[:1] != ['image'] or not mascot.exists() or not (chars or base_img):
        return adapters.gflow(p, *args, timeout=timeout)
    out_folder = Path(_arg(args, '--out')).resolve()
    out_folder.mkdir(parents=True, exist_ok=True)
    job_id, prompt, ratio = _arg(args, '--id'), _arg(args, '--prompt', ''), _arg(args, '--ratio', '16:9')
    refs = [str(mascot)] + ([str(Path(base_img).resolve())] if base_img else [])
    [result] = _run(p, [{'id': job_id, 'kind': 'image', 'prompt': prompt, 'ratio': ratio, 'refs': refs,
                         'variants': 1, 'job': _job_of(out_folder), 'out_dir': str(out_folder)}])
    if result['status'] != 'ok':
        raise blocked_from(result)
    evidence = Path(_arg(args, '--evidence-out', str(out_folder.parent)))
    dest = _write_image_evidence(out_folder, evidence, result, job_id, prompt, ratio, chars, base_img)
    return subprocess.CompletedProcess(args, 0, stdout=f'FlowPool generated: {dest}', stderr='')


def _batch(p, args):
    data = read(Path(args[1]))
    batch_out = Path(_arg(args, '--out')).resolve()
    batch_out.mkdir(parents=True, exist_ok=True)
    jobs = data.get('jobs', [])
    state_file = batch_out / 'gflow-run.json'
    run_jobs = [{'id': job['id'], 'status': 'failed', 'error': 'Submission pending; reconcile before retry'} for job in jobs]
    # Persist attempted membership before the external call.
    write(state_file, {'jobs': run_jobs})
    mascot = str(p.root / MASCOT)
    requests = [{'id': job['id'], 'kind': 'image', 'prompt': job['prompt'], 'ratio': job.get('ratio', '9:16'),
                 'refs': [mascot], 'variants': 1, 'job': _job_of(batch_out), 'out_dir': str(batch_out / job['id'])}
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
            src = Path(r['files'][0])
            dst = batch_out / (job['id'] + src.suffix)
            shutil.copy(src, dst)
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
    """One Veo frames-to-video request; returns the FlowPool result or raises Blocked."""
    [result] = _run(p, [dict(request, kind='clip')])
    if result['status'] != 'ok':
        raise blocked_from(result)
    return result
