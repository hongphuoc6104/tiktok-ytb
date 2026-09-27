"""Unit and integration tests for Colab Bridge module."""

import io
import json
import os
from pathlib import Path
import socketserver
import tarfile
import threading
import time
from typing import Dict, Any
import unittest
from unittest.mock import patch

from colab_bridge.config import ColabConfig, get_colab_config
from colab_bridge.client import (
    ColabClient,
    ColabCommunicationError,
    ColabExecutionError,
    is_colab_available,
    get_colab_status,
)
from colab_bridge.server import ColabRequestHandler, ThreadingServer


class TestColabConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = ColabConfig()
        self.assertFalse(cfg.enabled)
        self.assertEqual(cfg.endpoint, "http://localhost:8088")
        self.assertFalse(cfg.fallback_to_local)
        self.assertTrue(cfg.tasks.get("remotion_render"))
        cfg.enabled = True
        self.assertTrue(cfg.is_task_enabled("remotion_render"))

    def test_env_override(self):
        with patch.dict(os.environ, {
            "COLAB_OFFLOAD_ENABLED": "1",
            "COLAB_ENDPOINT": "http://100.99.1.2:8000",
            "COLAB_AUTH_TOKEN": "secret123"
        }):
            cfg = get_colab_config()
            self.assertTrue(cfg.enabled)
            self.assertEqual(cfg.endpoint, "http://100.99.1.2:8000")
            self.assertEqual(cfg.auth_token, "secret123")


class TestColabBridgeClientServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start a test server on an ephemeral port (port 0)
        ColabRequestHandler.auth_token = ""
        cls.server = ThreadingServer(("127.0.0.1", 0), ColabRequestHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.endpoint = f"http://127.0.0.1:{cls.port}"
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_check(self):
        self.assertTrue(is_colab_available(self.endpoint, timeout=2.0))
        status = get_colab_status(self.endpoint, timeout=2.0)
        self.assertEqual(status["status"], "ok")
        self.assertIn("gpu", status)
        self.assertIn("capabilities", status)

    def test_offline_detection(self):
        # A dead port should return False without raising an unhandled exception
        dead_endpoint = "http://127.0.0.1:59998"
        self.assertFalse(is_colab_available(dead_endpoint, timeout=0.5))

    def test_mock_render_pipeline(self):
        # Mock the server's remotion worker to return a fake video tarball
        class FakeRemotionWorker:
            def render_tarball(self, incoming_bytes):
                # Verify that incoming_bytes is a valid tar containing props.json
                with tarfile.open(fileobj=io.BytesIO(incoming_bytes), mode="r:gz") as tar:
                    names = tar.getnames()
                    assert "props.json" in names
                    assert any(n.startswith("public/") for n in names)

                # Return a valid response tarball
                out = io.BytesIO()
                with tarfile.open(fileobj=out, mode="w:gz") as tar:
                    fake_video = b"FAKEMP4DATA" * 200
                    ti = tarfile.TarInfo(name="video.mp4")
                    ti.size = len(fake_video)
                    tar.addfile(ti, io.BytesIO(fake_video))

                    timing_json = json.dumps([{"file": "video.mp4", "render_seconds": 1.2}]).encode("utf-8")
                    ti_timing = tarfile.TarInfo(name="render-timing.json")
                    ti_timing.size = len(timing_json)
                    tar.addfile(ti_timing, io.BytesIO(timing_json))

                return out.getvalue()

        ColabRequestHandler.remotion_worker = FakeRemotionWorker()

        # Prepare test files
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
            in_p = Path(tmp_in)
            out_p = Path(tmp_out)

            props_p = in_p / "props.json"
            props_p.write_text(json.dumps({"title": "test"}), encoding="utf-8")

            public_p = in_p / "public"
            public_p.mkdir()
            (public_p / "test.png").write_bytes(b"FAKEPNG")

            cfg = ColabConfig(enabled=True, endpoint=self.endpoint)
            client = ColabClient(cfg)
            res = client.render_remotion(props_p, public_p, out_p, timeout=5)

            self.assertEqual(res["status"], "success")
            self.assertTrue((out_p / "video.mp4").is_file())
            self.assertTrue((out_p / "render-timing.json").is_file())
            self.assertEqual(len(res["timings"]), 1)

    def test_mock_tts_pipeline(self):
        # Mock the server's TTS worker
        class FakeTTSWorker:
            def synthesize_to_tarball(self, req_json):
                assert "scenes" in req_json
                out = io.BytesIO()
                with tarfile.open(fileobj=out, mode="w:gz") as tar:
                    fake_wav = b"RIFFfakeWAVE" * 100
                    ti = tarfile.TarInfo(name="scene-1.wav")
                    ti.size = len(fake_wav)
                    tar.addfile(ti, io.BytesIO(fake_wav))

                    meta_json = json.dumps({
                        "segments": [{"id": "scene-1", "path": "scene-1.wav", "duration": 3.5}]
                    }).encode("utf-8")
                    ti_meta = tarfile.TarInfo(name="tts-result.json")
                    ti_meta.size = len(meta_json)
                    tar.addfile(ti_meta, io.BytesIO(meta_json))

                return out.getvalue()

        ColabRequestHandler.tts_worker = FakeTTSWorker()

        import tempfile
        with tempfile.TemporaryDirectory() as tmp_out:
            out_p = Path(tmp_out)
            cfg = ColabConfig(enabled=True, endpoint=self.endpoint)
            client = ColabClient(cfg)

            res = client.synthesize_tts(
                request_payload={"scenes": [{"id": "scene-1", "text": "Hang đá tiền sử"}]},
                output_dir=out_p,
                timeout=5,
            )
            self.assertEqual(res["status"], "success")
            self.assertTrue((out_p / "tts-result.json").is_file())
            self.assertTrue((out_p / "scene-1.wav").is_file())
            self.assertEqual(res["metadata"]["segments"][0]["duration"], 3.5)


if __name__ == "__main__":
    unittest.main()
