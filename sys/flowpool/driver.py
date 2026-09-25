"""Browser drivers. The pool talks to one driver per active profile.

Protocol (all read-only except `commit`):
  open()            attach to the instance's own Chrome (its debugging port); detect CAPTCHA/login
  probe(kinds)      doctor checks: logged in, Flow reachable, model selectable, credits
  read_credits()    {'value': int|None, 'raw': ..., 'method': ...}
  prepare(kind, items)  fill the form / local queue; MUST NOT start a generation
  commit(timeout)   the only call that can start a generation; returns
                    [{'id', 'files': [...], 'media_ids': [...]}]
  close()
Errors are DriverError(code, submitted=bool). `submitted` tells the pool
whether the generation may have started.
"""
import json
import queue
import subprocess
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Codes the pool understands. Anything else is treated as a generic failure.
PROFILE_CODES = {
    'CAPTCHA': 'captcha',
    'NEEDS_LOGIN': 'needs_login',
    'PROFILE_MISMATCH': 'needs_login',  # Flow shows a different account than the instance's account_hint
    'RATE_LIMITED': 'cooldown',
    'CREDIT_LIMIT': 'low_credit',
}
# Explicit refusals shown by Flow after submit: terminal, never retried automatically.
DECLINED = ('RATE_LIMITED', 'CREDIT_LIMIT', 'POLICY_BLOCKED', 'GENERATION_FAILED')


class DriverError(Exception):
    def __init__(self, code, message='', submitted=False, partial=None):
        super().__init__(f'{code}: {message}' if message else code)
        self.code = code
        self.submitted = submitted
        self.partial = partial or []


class Driver:
    def open(self):
        raise NotImplementedError

    def probe(self, kinds):
        raise NotImplementedError

    def read_credits(self):
        raise NotImplementedError

    def prepare(self, kind, items):
        raise NotImplementedError

    def commit(self, timeout):
        raise NotImplementedError

    def close(self):
        pass


class NodeDriver(Driver):
    """Runs sys/flowpool/worker.mjs and speaks line-delimited JSON over stdio."""

    def __init__(self, profile, cfg):
        self.profile = profile
        self.cfg = cfg
        self.proc = None
        self.lines = queue.Queue()
        self.project_url = None  # reported by the worker once it opened/created the Flow project

    def _start(self):
        self.proc = subprocess.Popen([self.cfg.get('flowpool_node', 'node'), str(HERE / 'worker.mjs')],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, cwd=str(HERE.parent), bufsize=1)

        def pump(stream, sink):
            for line in stream:
                sink.put(line)
            sink.put(None)

        threading.Thread(target=pump, args=(self.proc.stdout, self.lines), daemon=True).start()
        self.stderr = queue.Queue()
        threading.Thread(target=pump, args=(self.proc.stderr, self.stderr), daemon=True).start()

    def _call(self, message, timeout, submitted_on_error=False):
        if self.proc is None:
            self._start()
        try:
            self.proc.stdin.write(json.dumps(message, ensure_ascii=False) + '\n')
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as ex:
            raise DriverError('WORKER_DIED', str(ex), submitted=submitted_on_error)
        try:
            line = self.lines.get(timeout=timeout)
        except queue.Empty:
            self.kill()
            raise DriverError('TIMEOUT', f'{message["op"]} exceeded {timeout}s', submitted=submitted_on_error)
        if line is None:
            raise DriverError('WORKER_DIED', self._stderr_tail(), submitted=submitted_on_error)
        try:
            reply = json.loads(line)
        except ValueError:
            raise DriverError('PROTOCOL', line[:200], submitted=submitted_on_error)
        if reply.get('project_url'):
            self.project_url = reply['project_url']
        if not reply.get('ok'):
            raise DriverError(reply.get('code') or 'WORKER_ERROR', reply.get('error', ''),
                              submitted=bool(reply.get('submitted', submitted_on_error)), partial=reply.get('partial'))
        return reply

    def _stderr_tail(self):
        out = []
        while True:
            try:
                item = self.stderr.get_nowait()
            except (queue.Empty, AttributeError):
                break
            if item:
                out.append(item)
        return ''.join(out)[-500:]

    def open(self):
        return self._call({'op': 'open', 'profile': self.profile, 'cfg': _worker_cfg(self.cfg)}, 120)

    def probe(self, kinds):
        return self._call({'op': 'probe', 'kinds': list(kinds)}, 180)

    def read_credits(self):
        return self._call({'op': 'credits'}, 60)['credits']

    def prepare(self, kind, items):
        return self._call({'op': 'prepare', 'kind': kind, 'items': items}, 300)['prepared']

    def commit(self, timeout):
        return self._call({'op': 'commit', 'timeout_ms': int(timeout * 1000)}, timeout + 120,
                          submitted_on_error=True)['items']

    def close(self):
        if self.proc and self.proc.poll() is None:
            try:
                self._call({'op': 'close'}, 30)
                self.proc.wait(5)
            except (DriverError, subprocess.TimeoutExpired):
                pass
            self.kill()

    def kill(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def _worker_cfg(cfg):
    keys = ('flow_model', 'flow_project', 'veo_model', 'flowpool_credit_probe', 'flowpool_model_labels',
            'flowpool_clip_seconds', 'flowpool_flow_url')
    return {k: cfg.get(k) for k in keys}
