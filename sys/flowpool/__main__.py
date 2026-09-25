"""python3 -m flowpool (run from sys/)

Uses ONLY the user's existing signed-in Chrome profiles (browser-profiles.json),
through one daemon that holds the single CDP connection to that Chrome.

Daily:  daemon start (click "Allow" once in Chrome) -> open-profile "Profile N" (each)
        -> doctor -> ui (dashboard) / run --queue FILE -> daemon stop
Also:   status, init, mark, reconcile, decide, ui-state.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from . import daemon_client
from .dashboard import decide, ui_state
from .pool import FlowPool
from .profiles import STATES, derive
from .store import file_lock, write_json_atomic


def _table(status):
    lines = [f"{status['month']}: pool budget {status['credit_budget']:.0f}, used {status['month_spent']:.0f}"
             f"{'*' if status['month_spent_includes_estimates'] else ''}, left {status['budget_left']:.0f}, "
             f"~{status['clips_left_total']} clips ({status['veo_model']} ~{status['credits_per_clip']:.0f} cr/clip, "
             f"{status['cost_basis']}); video_generation={status['video_generation']}",
             f"{'profile':<12}{'tab':<5}{'state':<12}{'used':>7}{'cap':>7}{'left':>7}{'clips':>7}  email / reason"]
    for r in status['profiles']:
        lines.append(f"{r['profile']:<12}{'yes' if r['tab_open'] else 'no':<5}{r['state']:<12}{r['month_used']:>7.0f}"
                     f"{r['monthly_cap']:>7.0f}{r['month_remaining']:>7.0f}{r['clips_left_estimate'] or 0:>7}  "
                     f"{r['account_email'] or r['account_hint'] or '-'} {r['reason'] or ''}")
    if status.get('daemon_error') and status['daemon_error'] != 'NOT_ASKED':
        lines.append(f"daemon: {status['daemon_error']} -> python3 -m flowpool daemon start")
    lines.append('journal: ' + json.dumps(status['journal']))
    for a in status['attention']:
        lines.append(f"  needs attention: {a['id']} [{a['key']}] {a['state']} on {a['profile']} {a['code'] or ''}")
    if status['month_spent_includes_estimates']:
        lines.append('* includes estimated costs where the UI balance was unreadable')
    return '\n'.join(lines)


def open_profile(fp, name, wait=30, popen=subprocess.Popen, sleep=time.sleep):
    """Open a window of the user's existing profile (same Chrome, same user-data-dir,
    no copies, no sign-in) at Flow with a binding marker, then let the daemon find
    that tab (polling up to `wait` s) and close duplicate marker tabs."""
    pool = fp.pool()
    p = pool.get(name)
    base = (p.get('project_url') or fp.cfg.get('flowpool_flow_url') or 'https://flow.google.com/').split('#')[0]
    url = f"{base}#flowpool={p['slug']}"
    exe = fp.cfg.get('flowpool_chrome') or pool.data.get('executable_path') or '/opt/google/chrome/google-chrome'
    args = [exe, f"--profile-directory={p['profile_directory']}"]
    if Path(p['user_data_dir']).resolve() != (Path.home() / '.config/google-chrome').resolve():
        args.append(f"--user-data-dir={p['user_data_dir']}")
    popen(args + [url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    deadline = time.time() + wait
    error = None
    while time.time() < deadline:
        found, error = fp.locate_fn([p], True)
        if found.get(name):
            pool.record_binding(name, {'target_id': found[name]['target_id']})
            return {'profile': name, 'status': 'bound', **found[name]}
        if error in ('NO_DAEMON', 'NEEDS_ALLOW', 'NOT_CONNECTED'):
            break
        sleep(1)
    raise RuntimeError(f'PROFILE_TAB_NOT_FOUND: {name} tab did not appear' + (f' (daemon {error})' if error else ''))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='flowpool', description="Google Flow across the user's signed-in Chrome profiles")
    sub = ap.add_subparsers(dest='cmd', required=True)
    st = sub.add_parser('status'); st.add_argument('--json', action='store_true')
    dr = sub.add_parser('doctor'); dr.add_argument('--profile', action='append')
    rn = sub.add_parser('run'); rn.add_argument('--queue', required=True)
    it = sub.add_parser('init', help='re-derive profiles.json from browser-profiles.json'); it.add_argument('--force', action='store_true')
    dm = sub.add_parser('daemon'); dm.add_argument('action', choices=['start', 'stop', 'status', 'reconnect'])
    op = sub.add_parser('open-profile', help='open a window of an existing profile and bind its tab'); op.add_argument('profile')
    sub.add_parser('ui', help='print the dashboard URL (starts the daemon if needed)')
    sub.add_parser('ui-state', help='dashboard data as JSON')
    dc = sub.add_parser('decide'); dc.add_argument('kind', choices=['pick', 'regenerate']); dc.add_argument('key')
    dc.add_argument('--index', type=int); dc.add_argument('--note')
    mk = sub.add_parser('mark'); mk.add_argument('profile'); mk.add_argument('state', choices=[s for s in STATES if s != 'busy'])
    mk.add_argument('--note', required=True)
    rc = sub.add_parser('reconcile'); rc.add_argument('ref', help='request id or journal key prefix')
    rc.add_argument('--note', required=True); rc.add_argument('--release', action='store_true')
    rc.add_argument('--files', nargs='+'); rc.add_argument('--media-ids', nargs='+')
    a = ap.parse_args(argv)
    fp = FlowPool()
    out = lambda x: print(json.dumps(x, ensure_ascii=False, indent=2))
    try:
        if a.cmd == 'status':
            s = fp.status()
            print(json.dumps(s, ensure_ascii=False, indent=2) if a.json else _table(s))
        elif a.cmd == 'doctor':
            report = fp.doctor(a.profile)
            out(report)
            return 0 if all(r['state_after'] in ('ready', 'low_credit') and not r.get('error') for r in report) else 2
        elif a.cmd == 'run':
            requests = json.loads(Path(a.queue).read_text(encoding='utf-8'))
            if isinstance(requests, dict):
                requests = requests.get('requests', [])
            results = fp.run(requests)
            out(results)
            return 0 if all(r['status'] == 'ok' for r in results) else 2
        elif a.cmd == 'init':
            path = fp.dir / 'profiles.json'
            if path.exists() and not a.force:
                print(f'{path} exists; use --force to re-derive (the old file is kept as .bak)')
                return 2
            with file_lock(fp.lock_path, blocking=False):
                if path.exists():
                    path.rename(path.with_name(f'profiles.json.bak-{int(time.time())}'))
                write_json_atomic(path, derive(cfg=fp.cfg))
            print(f'wrote {path}')
        elif a.cmd == 'daemon':
            client = daemon_client.DaemonClient(fp.cfg)
            if a.action == 'start':
                out(daemon_client.start(fp.cfg, client=client))
            elif a.action == 'status':
                out(client.status())
            elif a.action == 'reconnect':
                out(client.call('reconnect', timeout=150))
            else:
                out(client.call('shutdown', timeout=30))
        elif a.cmd == 'open-profile':
            out(open_profile(fp, a.profile))
        elif a.cmd == 'ui':
            client = daemon_client.DaemonClient(fp.cfg)
            if not client.status().get('ok'):
                out(daemon_client.start(fp.cfg, client=client))
            print(f"http://127.0.0.1:{fp.cfg.get('flowpool_ui_port', 8765)}")
        elif a.cmd == 'ui-state':
            print(json.dumps(ui_state(fp), ensure_ascii=False))
        elif a.cmd == 'decide':
            print(json.dumps(decide(fp, a.kind, a.key, a.index, a.note), ensure_ascii=False))
        elif a.cmd == 'mark':
            out(fp.mark(a.profile, a.state, a.note))
        elif a.cmd == 'reconcile':
            snap = fp.reconcile(a.ref, a.note, a.release, a.files, a.media_ids)
            out({k: snap[k] for k in ('key', 'state')})
    except (RuntimeError, ValueError, KeyError, daemon_client.DaemonError) as ex:
        print(json.dumps({'ok': False, 'blocked': str(ex).strip('"')}, ensure_ascii=False))
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
