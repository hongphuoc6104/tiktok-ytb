"""Colab Remote Worker Server.

Runs inside the Google Colab environment and handles incoming requests from
the local Video Pilot pipeline. Works with pure Python stdlib (ThreadingHTTPServer)
and requires zero extra dependencies to start.
"""

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import os
from pathlib import Path
import socketserver
import sys
from typing import Optional
from urllib.parse import unquote, urlsplit

from .remotion_engine import ColabRemotionWorker
from .tts_engine import ColabTTSWorker, PodcastTTSTaskStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("colab_worker")


def get_gpu_info():
    """Detect available GPU and VRAM."""
    info = {"available": False, "device": "CPU", "vram_total_mb": 0, "vram_free_mb": 0}
    try:
        import torch
        if torch.cuda.is_available():
            info["available"] = True
            info["device"] = torch.cuda.get_device_name(0)
            free, total = torch.cuda.mem_get_info()
            info["vram_total_mb"] = round(total / (1024 * 1024))
            info["vram_free_mb"] = round(free / (1024 * 1024))
    except Exception:
        pass
    return info


class ColabRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Colab Worker API."""

    auth_token: Optional[str] = None
    remotion_worker: Optional[ColabRemotionWorker] = None
    tts_worker: Optional[ColabTTSWorker] = None
    podcast_tts_tasks: Optional[PodcastTTSTaskStore] = None

    def _send_json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _check_podcast_auth(self) -> bool:
        # The podcast API returns user audio and carries a cloned voice profile.
        # Unlike legacy routes, it is deliberately unavailable on an open worker.
        if not self.auth_token:
            self._send_json(503, {"error": "Podcast TTS requires COLAB_AUTH_TOKEN on the worker."})
            return False
        if self.headers.get("Authorization", "") != f"Bearer {self.auth_token}":
            self._send_json(401, {"error": "Unauthorized"})
            return False
        return True

    def _podcast_store(self) -> PodcastTTSTaskStore:
        if self.podcast_tts_tasks is None:
            self.podcast_tts_tasks = PodcastTTSTaskStore()
        return self.podcast_tts_tasks

    def _check_auth(self) -> bool:
        if not self.auth_token:
            return True
        auth_hdr = self.headers.get("Authorization", "")
        if auth_hdr == f"Bearer {self.auth_token}":
            return True
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
        return False

    def do_GET(self):
        if self.path == "/health" or self.path == "/api/v1/health":
            gpu = get_gpu_info()
            data = {
                "status": "ok",
                "service": "video-pilot-colab-worker",
                "gpu": gpu,
                "capabilities": ["remotion_render", "expressive_tts"],
            }
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        route = urlsplit(self.path)
        if route.path.startswith("/api/v1/podcast/tts/"):
            if not self._check_podcast_auth():
                return
            try:
                store = self._podcast_store()
                if route.path == "/api/v1/podcast/tts/runtime":
                    self._send_json(200, store.runtime_status())
                    return
                prefix = "/api/v1/podcast/tts/jobs/"
                if route.path.startswith(prefix):
                    tail = route.path[len(prefix):]
                    if tail.endswith("/result"):
                        request_id = unquote(tail[:-len("/result")].rstrip("/"))
                        result_path = store.result_path(request_id)
                        task = store.status(request_id)
                        if not task:
                            self._send_json(404, {"error": "Podcast TTS request_id not found", "request_id": request_id})
                        elif not result_path:
                            code = 409 if task.get("state") in ("failed", "ambiguous") else 202
                            self._send_json(code, {"error": "Podcast TTS result is not ready", **task})
                        else:
                            result = result_path.read_bytes()
                            self.send_response(200)
                            self.send_header("Content-Type", "application/gzip")
                            self.send_header("Content-Length", str(len(result)))
                            self.send_header("X-Podcast-TTS-Request-Id", request_id)
                            self.send_header("X-Podcast-TTS-SHA256", task.get("result_sha256", ""))
                            self.end_headers()
                            self.wfile.write(result)
                        return
                    request_id = unquote(tail.rstrip("/"))
                    task = store.status(request_id)
                    if task:
                        self._send_json(200, task)
                    else:
                        self._send_json(404, {"error": "Podcast TTS request_id not found", "request_id": request_id})
                    return
                self._send_json(404, {"error": "Not found"})
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
            except Exception as exc:
                logger.exception("Podcast TTS status route failed")
                self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/v1/podcast/tts/jobs":
            if not self._check_podcast_auth():
                return
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                if content_len <= 0 or content_len > 25_000_000:
                    self._send_json(413, {"error": "Podcast TTS request body size is invalid"})
                    return
                data = json.loads(self.rfile.read(content_len).decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("Request body must be a JSON object")
                request_id = data.get("request_id")
                request_hash = data.get("request_hash")
                payload = data.get("payload")
                resume = data.get("resume", False)
                if not isinstance(request_id, str) or not isinstance(request_hash, str) or not isinstance(payload, dict):
                    raise ValueError("request_id, request_hash, and payload are required")
                if not isinstance(resume, bool):
                    raise ValueError("resume must be a boolean")
                status = self._podcast_store().submit(request_id, request_hash, payload, resume=resume)
                code = 202 if status.get("state") in ("queued", "running") else 200
                self._send_json(code, status)
            except FileExistsError as exc:
                self._send_json(409, {"error": str(exc)})
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
            except Exception as exc:
                logger.exception("Podcast TTS submit route failed")
                self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
            return

        if not self._check_auth():
            return

        content_len = int(self.headers.get("Content-Length", 0))

        if self.path == "/api/v1/render/remotion":
            logger.info("Received Remotion render request (%d bytes)...", content_len)
            payload = self.rfile.read(content_len)
            try:
                if not self.remotion_worker:
                    self.remotion_worker = ColabRemotionWorker()
                out_bytes = self.remotion_worker.render_tarball(payload)
                self.send_response(200)
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Length", str(len(out_bytes)))
                self.end_headers()
                self.wfile.write(out_bytes)
                logger.info("Successfully completed Remotion render (%d bytes output)", len(out_bytes))
            except Exception as e:
                logger.exception("Error in Remotion render: %s", e)
                err_body = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            return

        if self.path == "/api/v1/tts/synthesize":
            logger.info("Received TTS synthesis request (%d bytes)...", content_len)
            payload_str = self.rfile.read(content_len).decode("utf-8")
            try:
                req_json = json.loads(payload_str)
                if not self.tts_worker:
                    self.tts_worker = ColabTTSWorker()
                out_bytes = self.tts_worker.synthesize_to_tarball(req_json)
                self.send_response(200)
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Length", str(len(out_bytes)))
                self.end_headers()
                self.wfile.write(out_bytes)
                logger.info("Successfully completed TTS synthesis (%d bytes output)", len(out_bytes))
            except Exception as e:
                logger.exception("Error in TTS synthesis: %s", e)
                err_body = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            return

        self.send_response(404)
        self.end_headers()


class ThreadingServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(port: int = 8088, auth_token: str = ""):
    ColabRequestHandler.auth_token = auth_token or os.environ.get("COLAB_AUTH_TOKEN", "")
    ColabRequestHandler.podcast_tts_tasks = None
    server_address = ("0.0.0.0", port)
    httpd = ThreadingServer(server_address, ColabRequestHandler)
    gpu = get_gpu_info()
    logger.info("==================================================")
    logger.info("🚀 Video Pilot Colab Worker Server started on port %d", port)
    logger.info("🖥️  GPU: %s (VRAM: %d MB)", gpu["device"], gpu["vram_total_mb"])
    logger.info("🔒 Auth token: %s", "ENABLED" if ColabRequestHandler.auth_token else "DISABLED (Open)")
    logger.info("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        httpd.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Video Pilot Colab Worker Server")
    parser.add_argument("--port", type=int, default=8088, help="Port to listen on (default 8088)")
    parser.add_argument("--token", type=str, default="", help="Optional bearer auth token")
    args = parser.parse_args()
    run_server(port=args.port, auth_token=args.token)
