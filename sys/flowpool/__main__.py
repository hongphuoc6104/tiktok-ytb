"""python3 -m flowpool status|doctor|run|init|mark|reconcile|open-profile (run from sys/)."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import config as config_mod
from .pool import FlowPool
from .profiles import STATES, derive
from .store import write_json_atomic


def _table(status):
    lines = [f"veo_model={status['veo_model']}  credits/clip={status['credits_per_clip']} ({status['cost_basis']})  "
             f"month_spent={status['month_spent']:.0f}{'*' if status['month_spent_includes_estimates'] else ''}"
             f"/{status['credit_budget']}  video_generation={status['video_generation']}",
             f"{'profile':<14}{'state':<13}{'credits':>9}{'clips_left':>12}  tool  reason"]
    for r in status['profiles']:
        lines.append(f"{r['profile']:<14}{r['state']:<13}{'-' if r['credits'] is None else r['credits']:>9}"
                     f"{'-' if r['clips_left_estimate'] is None else r['clips_left_estimate']:>12}  "
                     f"{'yes ' if r['tool_url'] else 'no  '}  {r['reason'] or ''}")
    lines.append('journal: ' + json.dumps(status['journal']))
    for a in status['attention']:
        lines.append(f"  needs attention: {a['id']} [{a['key']}] {a['state']} on {a['profile']} {a['code'] or ''}")
    if status['month_spent_includes_estimates']:
        lines.append('* includes estimated costs where the UI balance was unreadable')
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='flowpool', description='Google Flow across signed-in Chrome profiles')
    sub = ap.add_subparsers(dest='cmd', required=True)
    st = sub.add_parser('status'); st.add_argument('--json', action='store_true')
    dr = sub.add_parser('doctor'); dr.add_argument('--profile', action='append')
    rn = sub.add_parser('run'); rn.add_argument('--queue', required=True)
    it = sub.add_parser('init'); it.add_argument('--force', action='store_true')
    mk = sub.add_parser('mark'); mk.add_argument('profile'); mk.add_argument('state', choices=[s for s in STATES if s != 'busy'])
    mk.add_argument('--note', required=True)
    rc = sub.add_parser('reconcile'); rc.add_argument('ref', help='request id or journal key prefix')
    rc.add_argument('--note', required=True); rc.add_argument('--release', action='store_true')
    rc.add_argument('--files', nargs='+'); rc.add_argument('--media-ids', nargs='+')
    op = sub.add_parser('open-profile', help='open a window of the real profile (copy-free) with a binding marker')
    op.add_argument('profile'); op.add_argument('--tool', action='store_true', help='open the B-2 tool URL instead of Flow')
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
                print(f'{path} exists; use --force to re-derive (states and bindings are reset)')
                return 2
            write_json_atomic(path, derive(cfg=fp.cfg))
            print(f'wrote {path}')
        elif a.cmd == 'mark':
            print(json.dumps(fp.mark(a.profile, a.state, a.note), ensure_ascii=False, indent=2))
        elif a.cmd == 'reconcile':
            snap = fp.reconcile(a.ref, a.note, a.release, a.files, a.media_ids)
            print(json.dumps({k: snap[k] for k in ('key', 'state')}, indent=2))
        elif a.cmd == 'open-profile':
            return open_profile(fp, a.profile, a.tool)
    except (RuntimeError, ValueError, KeyError) as ex:
        print(json.dumps({'blocked': str(ex)}, ensure_ascii=False))
        return 2
    return 0


def open_profile(fp, name, tool=False):
    """Ask the running Chrome to open a window for `name`. Chrome forwards the
    command line to the existing process for that user-data-dir, so this uses
    the real profile without copying it, adds no automation flag and never
    signs in. The URL fragment lets the worker bind this tab to the profile."""
    pool = fp.pool()
    p = pool.get(name)
    base = p.get('tool_url') if tool else (p.get('project_url') or 'https://labs.google/fx/tools/flow')
    if not base:
        raise ValueError(f'{name} has no tool_url; remix the B-2 tool in that account and set it in profiles.json')
    url = f"{base.split('#')[0]}#flowpool={p['slug']}"
    exe = pool.data.get('executable_path') or '/opt/google/chrome/google-chrome'
    args = [exe, f"--profile-directory={p['profile_directory']}"]
    if Path(p['user_data_dir']).resolve() != (Path.home() / '.config/google-chrome').resolve():
        args.append(f"--user-data-dir={p['user_data_dir']}")
    subprocess.Popen(args + [url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print(json.dumps({'opened': url, 'profile': name, 'note': 'sign in / solve any check yourself in that window'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
