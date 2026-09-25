"""python3 -m flowpool (run from sys/)

One-time per account:  add NAME -> login NAME (sign in by hand, close window) -> launch NAME -> doctor
Daily:                 launch --all -> status -> run --queue FILE -> stop --all
Also: init, mark, reconcile.
"""
import argparse
import json
import sys
import time
from pathlib import Path

from . import instances
from .pool import FlowPool
from .profiles import STATES, empty_pool
from .store import file_lock, write_json_atomic


def _table(status):
    lines = [f"veo_model={status['veo_model']}  credits/clip={status['credits_per_clip']} ({status['cost_basis']})  "
             f"month_spent={status['month_spent']:.0f}{'*' if status['month_spent_includes_estimates'] else ''}"
             f"/{status['credit_budget']}  video_generation={status['video_generation']}",
             f"{'instance':<12}{'port':>6}  {'chrome':<8}{'state':<13}{'credits':>9}{'clips_left':>12}  project  reason"]
    for r in status['profiles']:
        lines.append(f"{r['profile']:<12}{r['port'] or '-':>6}  {'running' if r['running'] else 'stopped':<8}"
                     f"{r['state']:<13}{'-' if r['credits'] is None else r['credits']:>9}"
                     f"{'-' if r['clips_left_estimate'] is None else r['clips_left_estimate']:>12}  "
                     f"{'yes' if r['project_url'] else 'no ':<7}  {r['reason'] or ''}")
    if not status['profiles']:
        lines.append('(no instances: python3 -m flowpool add acc1)')
    lines.append('journal: ' + json.dumps(status['journal']))
    for a in status['attention']:
        lines.append(f"  needs attention: {a['id']} [{a['key']}] {a['state']} on {a['profile']} {a['code'] or ''}")
    if status['month_spent_includes_estimates']:
        lines.append('* includes estimated costs where the UI balance was unreadable')
    return '\n'.join(lines)


def _targets(pool, name, all_):
    if all_:
        return [p['name'] for p in pool.profiles]
    if not name:
        raise ValueError('give an instance NAME or --all')
    return [name]


def main(argv=None):
    ap = argparse.ArgumentParser(prog='flowpool', description='Google Flow across FlowPool-managed Chrome instances')
    sub = ap.add_subparsers(dest='cmd', required=True)
    st = sub.add_parser('status'); st.add_argument('--json', action='store_true')
    dr = sub.add_parser('doctor'); dr.add_argument('--profile', action='append')
    rn = sub.add_parser('run'); rn.add_argument('--queue', required=True)
    it = sub.add_parser('init', help='start an empty instance pool'); it.add_argument('--force', action='store_true')
    ad = sub.add_parser('add', help='create an instance (own Chrome data dir + port)'); ad.add_argument('name')
    lg = sub.add_parser('login', help='open the instance WITHOUT remote debugging so you can sign in by hand')
    lg.add_argument('name')
    for cmd in ('launch', 'stop'):
        c = sub.add_parser(cmd); c.add_argument('name', nargs='?'); c.add_argument('--all', action='store_true')
    mk = sub.add_parser('mark'); mk.add_argument('profile'); mk.add_argument('state', choices=[s for s in STATES if s != 'busy'])
    mk.add_argument('--note', required=True)
    rc = sub.add_parser('reconcile'); rc.add_argument('ref', help='request id or journal key prefix')
    rc.add_argument('--note', required=True); rc.add_argument('--release', action='store_true')
    rc.add_argument('--files', nargs='+'); rc.add_argument('--media-ids', nargs='+')
    a = ap.parse_args(argv)
    fp = FlowPool()
    try:
        if a.cmd == 'status':
            s = fp.status()
            print(json.dumps(s, ensure_ascii=False, indent=2) if a.json else _table(s))
        elif a.cmd == 'doctor':
            report = fp.doctor(a.profile)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if all(r['state_after'] in ('ready', 'low_credit') and not r.get('error') for r in report) else 2
        elif a.cmd == 'run':
            requests = json.loads(Path(a.queue).read_text(encoding='utf-8'))
            if isinstance(requests, dict):
                requests = requests.get('requests', [])
            results = fp.run(requests)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return 0 if all(r['status'] == 'ok' for r in results) else 2
        elif a.cmd == 'init':
            path = fp.dir / 'profiles.json'
            if path.exists() and not a.force:
                print(f'{path} exists; use --force to start an empty pool (the old file is kept as .bak)')
                return 2
            with file_lock(fp.lock_path, blocking=False):
                if path.exists():
                    path.rename(path.with_name(f'profiles.json.bak-{int(time.time())}'))
                write_json_atomic(path, empty_pool(fp.cfg))
            print(f'wrote {path}')
        elif a.cmd == 'add':
            with file_lock(fp.lock_path, blocking=False):
                entry = fp.pool().add(a.name)
            print(json.dumps({k: entry[k] for k in ('name', 'user_data_dir', 'port')}, ensure_ascii=False, indent=2))
            print(f'next: python3 -m flowpool login {a.name}   (sign in by hand, then close that window)')
        elif a.cmd == 'login':
            print(json.dumps(instances.launch(fp.pool(), a.name, fp.cfg, login=True), ensure_ascii=False, indent=2))
        elif a.cmd in ('launch', 'stop'):
            pool = fp.pool()
            fn = instances.launch if a.cmd == 'launch' else instances.stop
            out, failed = [], False
            for name in _targets(pool, a.name, a.all):
                try:
                    out.append(fn(pool, name, fp.cfg) if a.cmd == 'launch' else fn(pool, name))
                except RuntimeError as ex:
                    out.append({'instance': name, 'blocked': str(ex)})
                    failed = True
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return 2 if failed else 0
        elif a.cmd == 'mark':
            print(json.dumps(fp.mark(a.profile, a.state, a.note), ensure_ascii=False, indent=2))
        elif a.cmd == 'reconcile':
            snap = fp.reconcile(a.ref, a.note, a.release, a.files, a.media_ids)
            print(json.dumps({k: snap[k] for k in ('key', 'state')}, indent=2))
    except (RuntimeError, ValueError, KeyError) as ex:
        print(json.dumps({'blocked': str(ex).strip('"')}, ensure_ascii=False))
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
