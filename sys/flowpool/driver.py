"""Browser drivers. The pool talks to one driver per active profile.

Protocol (all read-only except `commit`):
  open()            find the profile's tab in the shared Chrome (via the daemon); detect CAPTCHA/login
  probe(kinds)      doctor checks: logged in, Flow reachable, model selectable, credits
  read_credits()    {'value': int|None, 'raw': ..., 'method': ...}
  prepare(kind, items)  fill the form / local queue; MUST NOT start a generation
  commit(timeout)   the only call that can start a generation; returns
                    [{'id', 'files': [...], 'media_ids': [...]}]
  close()
Errors are DriverError(code, submitted=bool). `submitted` tells the pool
whether the generation may have started.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Codes the pool understands. Anything else is treated as a generic failure.
PROFILE_CODES = {
    'CAPTCHA': 'captcha',
    'NEEDS_LOGIN': 'needs_login',
    'PROFILE_MISMATCH': 'needs_login',  # Flow shows another account than the one recorded for this profile
    'RATE_LIMITED': 'cooldown',
    'CREDIT_LIMIT': 'low_credit',
}
# The daemon's single CDP connection is gone: nothing can run until the user acts.
DAEMON_CODES = ('NO_DAEMON', 'NEEDS_ALLOW', 'NOT_CONNECTED')
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


class DaemonDriver(Driver):
    """Per-profile driver over the FlowPool daemon's single CDP connection.
    Each call carries the profile record; the daemon serializes work per tab."""

    def __init__(self, profile, cfg, client=None):
        from .daemon_client import DaemonClient
        self.profile = {k: v for k, v in profile.items() if not k.startswith('_')}
        self.cfg = cfg
        self.client = client or DaemonClient(cfg)
        self.project_url = None
        self.email = None

    def _call(self, op, timeout, submitted_on_error=False, **params):
        from .daemon_client import DaemonError
        try:
            reply = self.client.call(op, timeout=timeout, profile=self.profile, cfg=_worker_cfg(self.cfg), **params)
        except DaemonError as ex:
            # Once commit was sent, a lost reply means the generation may have started.
            raise DriverError(ex.code, str(ex), submitted=submitted_on_error)
        if reply.get('project_url'):
            self.project_url = reply['project_url']
        if not reply.get('ok'):
            raise DriverError(reply.get('code') or 'WORKER_ERROR', reply.get('error', ''),
                              submitted=bool(reply.get('submitted', submitted_on_error)), partial=reply.get('partial'))
        return reply

    def open(self):
        reply = self._call('open', 120)
        self.email = reply.get('email')
        return reply

    def probe(self, kinds):
        return self._call('probe', 240, kinds=list(kinds))

    def read_credits(self):
        return self._call('credits', 60)['credits']

    def prepare(self, kind, items):
        return self._call('prepare', 300, kind=kind, items=items)['prepared']

    def commit(self, timeout):
        return self._call('commit', timeout + 120, submitted_on_error=True, timeout_ms=int(timeout * 1000))['items']

    def close(self):
        try:
            self._call('release', 30)
        except DriverError:
            pass


def _worker_cfg(cfg):
    keys = ('flow_model', 'flow_project', 'veo_model', 'flowpool_credit_probe', 'flowpool_model_labels',
            'flowpool_clip_seconds', 'flowpool_flow_url')
    return {k: cfg.get(k) for k in keys}
