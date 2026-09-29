"""Explicit lifecycle/benchmark tools; never modify workflow approvals."""
import argparse
import json
from pathlib import Path
from .client import Client, ColabError, issue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['status', 'start', 'setup', 'stop', 'synthesize', 'collect'])
    parser.add_argument('--request', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / 'config.json').read_text())
    client = Client(root, cfg)
    if args.action == 'status':
        client.ensure_authenticated()
        print(client.call('status', '-s', client.session))
    elif args.action in ('start', 'setup', 'stop'):
        print(getattr(client, args.action)())
    else:
        if not all((args.request, args.out, args.cache)):
            parser.error('--request, --out and --cache are required')
        print(client.synthesize(json.loads(args.request.read_text()), args.out, args.cache,
                                collect_only=args.action == 'collect'))


if __name__ == '__main__':
    try:
        main()
    except ColabError as ex:
        root = Path(__file__).resolve().parents[1]
        issue(root, str(ex))
        print(json.dumps({'ok': False, 'error': str(ex)}, ensure_ascii=False))
        raise SystemExit(2)
