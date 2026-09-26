"""Submit a step batch to the flowctl runner and wait for its result.

CLI (from sys/):  python3 -m flowctl.client LANE steps.json   (or '-' for stdin)
"""
import itertools
import json
import sys
import time
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / 'scratch' / 'flowctl'
_n = itertools.count()


def run(lane, steps, timeout=900):
    name = f'{lane}__{int(time.time() * 1000)}_{next(_n)}'
    tmp = DIR / 'in' / (name + '.tmp')
    tmp.write_text(json.dumps(steps, ensure_ascii=False))
    tmp.rename(tmp.with_suffix('.json'))
    out = DIR / 'out' / (name + '.json')
    end = time.time() + timeout
    while time.time() < end:
        if out.exists():
            time.sleep(0.05)
            return json.loads(out.read_text())
        if not (DIR / 'ready').exists():
            raise RuntimeError('flowctl runner is not running')
        time.sleep(0.3)
    raise TimeoutError(name)


if __name__ == '__main__':
    src = sys.stdin.read() if sys.argv[2] == '-' else Path(sys.argv[2]).read_text()
    print(json.dumps(run(sys.argv[1], json.loads(src)), ensure_ascii=False, indent=1))
