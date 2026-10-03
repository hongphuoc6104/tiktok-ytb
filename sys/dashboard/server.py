"""Stdlib HTTP management UI, restricted to loopback and explicit artifacts."""
import argparse
import hmac
import json
import mimetypes
from pathlib import Path
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from dashboard.data import Dashboard, safe
from permissions import PermissionDenied

STATIC = Path(__file__).with_name('static')


def make_server(root, *, port=0, dashboard=None, python=None):
    app = dashboard or Dashboard(root, python=python)
    csrf = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not log request bodies, source instructions, OAuth or paths.

        def origin(self):
            return 'http://' + self.headers.get('Host', '')

        def trusted_host(self):
            allowed = {'127.0.0.1:' + str(self.server.server_port), 'localhost:' + str(self.server.server_port)}
            return self.headers.get('Host') in allowed

        def send(self, status, value, mime='application/json; charset=utf-8'):
            if not isinstance(value, bytes):
                value = json.dumps(safe(value), ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(value)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(value)

        def do_GET(self):
            if not self.trusted_host():
                return self.send(403, {'blocked': 'Host không hợp lệ'})
            path = unquote(urlsplit(self.path).path)
            try:
                if path == '/api/state':
                    return self.send(200, {**app.snapshot(), 'csrf': csrf})
                if path.startswith('/api/jobs/'):
                    return self.send(200, app.job(path[len('/api/jobs/'):]))
                if path in ('/', '/app.js', '/style.css'):
                    name = 'index.html' if path == '/' else path[1:]
                    file = STATIC / name
                    return self.send(200, file.read_bytes(), (mimetypes.guess_type(name)[0] or 'text/plain') + '; charset=utf-8')
                if path.startswith('/media/'):
                    parts = path.split('/')
                    if len(parts) != 4 or not re.fullmatch('[0-9a-f]{24}', parts[3]):
                        raise ValueError('Artifact ID không hợp lệ')
                    file = app.artifact_path(parts[2], parts[3])
                    if file.suffix == '.json':
                        return self.send(200, json.loads(file.read_text()))
                    if file.suffix in ('.md', '.txt', '.srt', '.vtt'):
                        return self.send(200, str(safe(file.read_text())).encode(), 'text/plain; charset=utf-8')
                    # Byte-range media playback; never buffer a whole final video.
                    size = file.stat().st_size
                    start, end, status = 0, size - 1, 200
                    value = self.headers.get('Range')
                    if value:
                        match = re.fullmatch(r'bytes=(\d*)-(\d*)', value)
                        if not match or not any(match.groups()):
                            return self.send(416, {'blocked': 'Range không hợp lệ'})
                        if match[1]:
                            start = int(match[1]); end = min(int(match[2]) if match[2] else end, end)
                        else:
                            start = max(0, size - int(match[2]))
                        if start > end or start >= size:
                            return self.send(416, {'blocked': 'Range ngoài artifact'})
                        status = 206
                    self.send_response(status)
                    self.send_header('Content-Type', mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
                    self.send_header('Content-Length', str(end - start + 1))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Cache-Control', 'no-store')
                    if status == 206:
                        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                    self.end_headers()
                    with file.open('rb') as handle:
                        handle.seek(start)
                        left = end - start + 1
                        while left:
                            chunk = handle.read(min(left, 128 * 1024))
                            if not chunk:
                                break
                            self.wfile.write(chunk); left -= len(chunk)
                    return
                self.send(404, {'blocked': 'Không có route'})
            except (BrokenPipeError, ConnectionResetError):
                # Browser navigation can cancel media streaming after headers.
                # The closed connection cannot receive a second response.
                return
            except (ValueError, OSError) as error:
                self.send(404, {'blocked': str(error) if isinstance(error, ValueError) else 'File không khả dụng'})
            except Exception:
                self.send(503, {'blocked': 'Không đọc được metadata; kiểm môi trường quản lý.'})

        def do_POST(self):
            if (not self.trusted_host() or self.headers.get('Origin') != self.origin() or
                self.headers.get('Sec-Fetch-Site') not in (None, 'same-origin') or
                not hmac.compare_digest(self.headers.get('X-VP-CSRF', ''), csrf)):
                return self.send(403, {'blocked': 'Origin/CSRF không hợp lệ'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.send(415, {'blocked': 'JSON required'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1024 * 1024:
                    return self.send(413, {'blocked': 'Request quá lớn hoặc rỗng'})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('JSON object required')
                path = urlsplit(self.path).path
                if not path.startswith('/api/actions/') or '/' in path[len('/api/actions/'):]:
                    return self.send(404, {'blocked': 'Không có thao tác'})
                result = app.mutate(path[len('/api/actions/'):], data)
                self.send(200, result)
            except PermissionDenied:
                self.send(403, {'blocked': 'Quyền đã chọn không cho phép thao tác trong phạm vi này.'})
            except (ValueError, TypeError) as error:
                self.send(400, {'blocked': str(error)})
            except Exception:
                self.send(409, {'blocked': 'CLI từ chối thao tác; kiểm quyền, revision và ownership.'})

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.dashboard = app
    server.daemon_threads = True
    return server


def main():
    parser = argparse.ArgumentParser(description='Trang quản lý Video Pilot chỉ trên loopback')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--python', help='Python môi trường quản lý dùng cho CLI')
    args = parser.parse_args()
    server = make_server(args.root, port=args.port, python=args.python)
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}', 'scope': 'loopback', 'provider_calls': False}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
