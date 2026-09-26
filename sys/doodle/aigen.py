"""Batch image generation through the B-2 "VP Stickman Lab" Flow tool (same path as video-vocabulary).

Input: a JSON list of specs {id, prompt, ratio, ref: [path, media_id], base: [path, media_id]|null, model?, style?}.
Output: <out>/<id>.<ext> and <out>/manifest.json {id: {path, media_id}}. Ids already in the manifest are skipped.
An unknown (ambiguous) outcome is never resubmitted; it is reported and the batch moves on.

Usage (from sys/): python3 -m doodle.aigen SPECS.json OUT_DIR [--model "Nano Banana Pro"]
"""
import json
import sys
import time
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYS))
import b2_bridge  # noqa: E402
from pilot import Blocked  # noqa: E402


def run(specs, out, model='Nano Banana Pro', style=''):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mf = out / 'manifest.json'
    manifest = json.loads(mf.read_text()) if mf.exists() else {}
    todo = [s for s in specs if s['id'] not in manifest]
    failed = {}
    print(f'{len(todo)} to generate, {len(manifest)} done', flush=True)
    for i in range(0, len(todo), 4):
        group = todo[i:i + 4]
        batch = []
        for s in group:
            ref, base = s['ref'], s.get('base')
            batch.append({'testCase': s['id'], 'testName': s['id'], 'prompt': s['prompt'], 'ratio': s.get('ratio', '16:9'),
                          'preserve': s.get('preserve', ''), 'change': s.get('change', ''), 'literalText': '',
                          'outDir': str(out), 'characterRefPath': str(Path(ref[0]).resolve()), 'charMediaId': ref[1],
                          'baseRefPath': str(Path(base[0]).resolve()) if base else None, 'baseMediaId': base[1] if base else None,
                          'model': s.get('model', model), 'style': s.get('style', style), 'collectionOnly': False})
        t = time.time()
        try:
            items = b2_bridge.generate_b2_batch(batch, timeout=600)
        except Blocked as ex:
            msg = str(ex)
            print(f'batch {[s["id"] for s in group]} blocked: {msg[:300]}', flush=True)
            # Settle one by one: a 'generated' attempt is collected from the local store without
            # resubmitting; an 'unknown' one keeps its id retired and is regenerated under a new id
            # (stills are free), at most twice.
            for s, spec in zip(group, batch):
                for k in range(3):
                    sid = spec['testCase'] if k == 0 else f"{s['id']}_r{k}"
                    try:
                        alt = dict(spec, testCase=sid, testName=sid, model='Nano Banana 2') if k == 2 else dict(spec, testCase=sid, testName=sid)
                        it = b2_bridge.generate_b2_batch([alt], timeout=600)[0]
                        manifest[s['id']] = {'path': it['path'], 'media_id': it.get('media_id')}
                        mf.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
                        print(f'  settled {s["id"]} as {sid}', flush=True)
                        break
                    except Blocked as e2:
                        print(f'  {sid}: {str(e2)[:160]}', flush=True)
                else:
                    failed[s['id']] = msg[:300]
            continue
        for s, it in zip(group, items):
            manifest[s['id']] = {'path': it['path'], 'media_id': it.get('media_id')}
        mf.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
        print(f'ok {[s["id"] for s in group]} in {time.time() - t:.0f}s ({len(manifest)}/{len(specs)})', flush=True)
    return manifest, failed


if __name__ == '__main__':
    args = sys.argv[1:]
    model = args[args.index('--model') + 1] if '--model' in args else 'Nano Banana Pro'
    m, f = run(json.loads(Path(args[0]).read_text()), args[1], model)
    print(json.dumps({'done': len(m), 'failed': f}, ensure_ascii=False))
