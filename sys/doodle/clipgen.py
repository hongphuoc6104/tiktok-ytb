"""Frames-to-video clips in Google Flow (direct mode, Omni 1.1 Flash) through the flowctl runner.

Each job: upload the shot still as Start frame, pick duration, type the motion prompt, submit.
Up to IN_FLIGHT generations run at once; a new result tile is matched to its job by comparing the
clip's first frame with each pending still (no reliance on tile order). Credits are booked in
<out>/ledger.json at submit time and a hard cap (default 1050, including earlier spend) is never passed.

Usage (from sys/): python3 -m doodle.clipgen JOBS.json OUT_DIR [--cap 1050] [--tab p10v]
JOBS: [{"id", "image", "seconds": 4|6|8|10, "prompt"}]
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYS))
from flowctl.client import run as fc  # noqa: E402

COST = {4: 7, 6: 10, 8: 12, 10: 15}  # Omni 1.1 Flash, 720p, read from the Flow UI 27/09/2026
IN_FLIGHT = 3
TIMEOUT = 600
STYLE = 'Gentle hand-drawn doodle animation. Keep the exact drawing style, line art, colors and characters of the start frame. '
TAIL = ' Subtle camera motion. No text, no captions.'


def ok(res):
    bad = [r for r in res if not r['ok']]
    if bad:
        raise RuntimeError(json.dumps(bad, ensure_ascii=False)[:800])
    return res


def tiles(tab):
    """Media ids of generated-video tiles currently in the grid, newest first, plus visible failure texts."""
    r = ok(fc(tab, [{'op': 'eval', 'tab': tab, 'js':
        "const ids=[...document.querySelectorAll('img[alt=\"Generated video thumbnail\"]')].map(i=>(i.src.match(/image\\/([0-9a-f-]{36})/)||[])[1]).filter(Boolean);"
        "const t=document.body.innerText; return {ids, failed:(t.match(/(Failed|failed to generate|Generation failed|couldn.t generate)[^\\n]{0,80}/gi)||[])};"}]))
    return r[0]['r']


def fetch(tab, mid, dest):
    steps = [{'op': 'hover', 'tab': tab, 'sel': f'img[src*="{mid}"]'}, {'op': 'wait', 'tab': tab, 'ms': 1500},
             {'op': 'eval', 'tab': tab, 'js': f"const v=[...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src).find(s=>s&&s.includes('{mid}')); return v||null;"}]
    src = ok(fc(tab, steps))[-1]['r']
    if not src:
        return None
    ok(fc(tab, [{'op': 'save', 'tab': tab, 'src': src, 'path': str(dest)}]))
    return dest


def first_frame_diff(clip, image):
    """Mean abs difference (0..255) between the clip's first frame and the still, both 64x36 grey."""
    def grab(args):
        r = subprocess.run(['ffmpeg', '-v', 'error'] + args + ['-vf', 'scale=64:36,format=gray', '-frames:v', '1', '-f', 'rawvideo', '-'],
                           capture_output=True)
        return r.stdout
    a, b = grab(['-i', str(clip)]), grab(['-i', str(image)])
    if len(a) != len(b) or not a:
        return 255.0
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def submit(tab, job, up_dir):
    up = up_dir / f"{job['id']}{Path(job['image']).suffix}"
    shutil.copy(job['image'], up)
    prompt = STYLE + job['prompt'][0].upper() + job['prompt'][1:] + '.' + TAIL
    fc(tab, [  # best-effort cleanup of a composer left over from an earlier failed attempt
        {'op': 'press', 'tab': tab, 'key': 'Escape'},
        {'op': 'wait', 'tab': tab, 'ms': 500},
        {'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Clear prompt', 'timeout': 1500, 'optional': True},
        {'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Image ingredient', 'timeout': 1500, 'optional': True},
        {'op': 'wait', 'tab': tab, 'ms': 500}])
    ok(fc(tab, [
        {'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Start', 'exact': True},
        {'op': 'waitFor', 'tab': tab, 'text': 'Select a frame image'},
        {'op': 'upload', 'tab': tab, 'trigger': {'role': 'button', 'name': 'Upload media'}, 'files': [str(up)]},
        {'op': 'waitFor', 'tab': tab, 'role': 'option', 'name': job['id'], 'timeout': 60000},
        {'op': 'wait', 'tab': tab, 'ms': 3000}]))
    probe = [{'op': 'eval', 'tab': tab, 'js': f"const o=[...document.querySelectorAll('[role=option]')].find(o=>o.innerText.includes('{job['id']}')); return o?{{sel:o.getAttribute('aria-selected'),txt:o.innerText}}:null;"}]
    for _ in range(45):
        sel = ok(fc(tab, probe))[0]['r']
        if sel and 'Uploading' not in sel.get('txt', ''):
            break
        time.sleep(2)
    if not sel or 'Uploading' in sel.get('txt', ''):
        raise RuntimeError(f'upload not ready: {sel}')
    if sel.get('sel') != 'true':
        ok(fc(tab, [{'op': 'click', 'tab': tab, 'role': 'option', 'name': job['id']}, {'op': 'wait', 'tab': tab, 'ms': 800}]))
    fc(tab, [{'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Add to prompt', 'timeout': 4000, 'optional': True}])
    ok(fc(tab, [{'op': 'waitFor', 'tab': tab, 'text': 'Select a frame image', 'state': 'hidden'}]))
    res = ok(fc(tab, [
        {'op': 'wait', 'tab': tab, 'ms': 1200},
        {'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Settings trigger'},
        {'op': 'waitFor', 'tab': tab, 'role': 'radio', 'name': '720p', 'timeout': 8000},
        {'op': 'click', 'tab': tab, 'role': 'radio', 'name': f"{job['seconds']}s"},
        {'op': 'wait', 'tab': tab, 'ms': 400},
        {'op': 'eval', 'tab': tab, 'js': "const B=[...document.querySelectorAll('button')]; const b=B.find(b=>b.getAttribute('aria-label')==='Select model family'); const c=[...document.querySelectorAll('a')].map(a=>a.innerText).find(t=>/credits/.test(t)); return {model:b&&b.innerText, cost:c||null, emptyStart:!!B.find(b=>b.innerText.trim()==='Start')};"},
        {'op': 'press', 'tab': tab, 'key': 'Escape'},
        {'op': 'wait', 'tab': tab, 'ms': 400},
        {'op': 'type', 'tab': tab, 'sel': 'div.ProseMirror[contenteditable=true]', 'value': prompt},
        {'op': 'wait', 'tab': tab, 'ms': 600},
        {'op': 'shot', 'tab': tab, 'name': f"pre-{job['id']}"}]))
    info = res[5]['r']
    want = f"{COST[job['seconds']]} credits"
    if 'Omni' not in (info.get('model') or '') or info.get('cost') != want or info.get('emptyStart'):
        raise RuntimeError(f"settings mismatch before submit: {info}, want Omni / {want} / start frame attached")
    ok(fc(tab, [{'op': 'click', 'tab': tab, 'role': 'button', 'name': 'Start generation'}, {'op': 'wait', 'tab': tab, 'ms': 3000}]))


def main(jobs_file, out, cap=1050, tab='p10v'):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    up_dir = out / 'upload'
    up_dir.mkdir(exist_ok=True)
    lf = out / 'ledger.json'
    L = json.loads(lf.read_text()) if lf.exists() else {'spent': 0, 'jobs': {}}
    save = lambda: lf.write_text(json.dumps(L, ensure_ascii=False, indent=1))
    jobs = [j for j in json.loads(Path(jobs_file).read_text()) if not (out / f"{j['id']}.mp4").exists()
            and L['jobs'].get(j['id'], {}).get('state') not in ('submitted', 'unknown')]
    print(f'{len(jobs)} clips to make; spent so far {L["spent"]}/{cap}', flush=True)
    known = set(tiles(tab)['ids']) | {v['media_id'] for v in L['jobs'].values() if v.get('media_id')}
    pending = {}  # id -> job
    while jobs or pending:
        while jobs and len(pending) < IN_FLIGHT:
            job = jobs[0]
            cost = COST[job['seconds']]
            if L['spent'] + cost > cap:
                print(f'cap reached: {L["spent"]}+{cost} > {cap}; stop submitting', flush=True)
                jobs = []
                break
            jobs.pop(0)
            try:
                submit(tab, job, up_dir)
            except Exception as ex:  # failed before the submit click: nothing spent
                print(f'prepare failed {job["id"]}: {str(ex)[:300]}', flush=True)
                L['jobs'][job['id']] = {'state': 'prepare_failed', 'error': str(ex)[:300]}
                save()
                continue
            L['spent'] += cost
            L['jobs'][job['id']] = {'state': 'submitted', 'cost': cost, 't': time.time()}
            save()
            pending[job['id']] = job
            print(f'submitted {job["id"]} ({job["seconds"]}s, {cost} cr) spent={L["spent"]}', flush=True)
        time.sleep(8)
        now = tiles(tab)
        new = [m for m in now['ids'] if m not in known]
        for mid in new:
            tmp = out / f'_{mid}.mp4'
            try:
                if not fetch(tab, mid, tmp):
                    continue  # still rendering: no video src yet
            except Exception as ex:
                print(f'fetch {mid} failed: {str(ex)[:200]}', flush=True)
                continue
            known.add(mid)
            scores = sorted((first_frame_diff(tmp, j['image']), jid) for jid, j in pending.items())
            if not scores or scores[0][0] > 40:
                print(f'unmatched result {mid} scores={scores[:3]}', flush=True)
                tmp.rename(out / f'unmatched_{mid}.mp4')
                continue
            jid = scores[0][1]
            tmp.rename(out / f'{jid}.mp4')
            L['jobs'][jid].update(state='done', media_id=mid, diff=round(scores[0][0], 1), took=round(time.time() - L['jobs'][jid]['t']))
            save()
            pending.pop(jid)
            print(f'done {jid} <- {mid} diff={scores[0][0]:.1f}', flush=True)
        for jid in list(pending):
            if time.time() - L['jobs'][jid]['t'] > TIMEOUT:
                L['jobs'][jid]['state'] = 'unknown'
                save()
                pending.pop(jid)
                print(f'timeout {jid}: marked unknown (not resubmitted); failures on page: {now["failed"][:3]}', flush=True)
    print(json.dumps({'spent': L['spent'], 'done': sum(1 for v in L['jobs'].values() if v.get('state') == 'done')}), flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    cap = int(a[a.index('--cap') + 1]) if '--cap' in a else 1050
    tab = a[a.index('--tab') + 1] if '--tab' in a else 'p10v'
    main(a[0], a[1], cap, tab)
