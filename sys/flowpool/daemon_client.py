"""Client for the FlowPool daemon (sys/flowpool/daemon.mjs).

The daemon owns the ONLY CDP connection to the user's Chrome (every new CDP
client makes Chrome ask the user to click "Allow"). All CLI and pipeline calls
go through its unix socket: one JSON request line, one JSON reply line.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from .config import HOME, SYS


class DaemonError(Exception):
    def __init__(self, code, message='', reply=None):
        super().__init__(f'{code}: {message}' if message else code)
        self.code = code
        self.reply = reply or {}


def socket_path(cfg):
    return Path(cfg.get('flowpool_daemon_socket') or HOME / 'daemon.sock')


class DaemonClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.path = socket_path(cfg)

    def call(self, op, timeout=60, **params):
        """Send one request. Raises DaemonError(NO_DAEMON) when nothing listens and
        DaemonError(TIMEOUT) when the reply does not arrive in time."""
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            try:
                s.connect(str(self.path))
            except OSError as ex:
                raise DaemonError('NO_DAEMON', f'FlowPool daemon is not running ({ex}); start it: python3 -m flowpool daemon start')
            s.sendall((json.dumps(dict(params, op=op), ensure_ascii=False) + '\n').encode('utf-8'))
            chunks = []
            while True:
                try:
                    chunk = s.recv(65536)
                except socket.timeout:
                    raise DaemonError('TIMEOUT', f'daemon did not answer {op} within {timeout}s')
                if not chunk:
                    break
                chunks.append(chunk)
                if chunk.endswith(b'\n'):
                    break
        finally:
            s.close()
        text = b''.join(chunks).decode('utf-8').strip()
        if not text:
            raise DaemonError('WORKER_DIED', f'daemon closed the connection during {op}')
        try:
            return json.loads(text)
        except ValueError:
            raise DaemonError('PROTOCOL', text[:200])

    def status(self):
        try:
            return self.call('status', timeout=10)
        except DaemonError as ex:
            return {'ok': False, 'code': ex.code, 'error': str(ex), 'connected': False}


def start(cfg, wait_connect=150, popen=subprocess.Popen, client=None):
    """Start the daemon (idempotent) and let it open its single CDP connection.
    Chrome then shows one "Allow" prompt that the user must approve."""
    client = client or DaemonClient(cfg)
    st = client.status()
    if st.get('ok'):
        if st.get('connected'):
            return {'status': 'already_running', **st}
    else:
        log = open(HOME / 'daemon.log', 'a')
        env = dict(os.environ, FLOWPOOL_PYTHON=sys.executable)
        popen([cfg.get('flowpool_node', 'node'), str(HOME / 'daemon.mjs'), 'serve'], cwd=str(SYS), stdin=subprocess.DEVNULL,
              stdout=log, stderr=log, start_new_session=True, env=env)
        deadline = time.time() + 15
        while time.time() < deadline and not client.status().get('ok'):
            time.sleep(0.3)
        if not client.status().get('ok'):
            raise DaemonError('DAEMON_START_FAILED', f'see {HOME / "daemon.log"}')
    print('Chrome sẽ hỏi cho phép gỡ lỗi từ xa: bấm "Allow" trong cửa sổ Chrome.', file=sys.stderr, flush=True)
    reply = client.call('reconnect', timeout=wait_connect)
    return {'status': 'connected' if reply.get('ok') else 'needs_allow', **reply}
