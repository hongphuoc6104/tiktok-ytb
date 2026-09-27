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

from .remotion_engine import ColabRemotionWorker
from .tts_engine import ColabTTSWorker

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

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
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
