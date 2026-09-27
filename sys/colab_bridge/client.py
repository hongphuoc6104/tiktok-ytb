"""Local Python client for communicating with Google Colab Remote Worker."""

import io
import json
import logging
import os
from pathlib import Path
import tarfile
from typing import Any, Dict, Optional, Tuple
import urllib.error
import urllib.request

from .config import ColabConfig, get_colab_config

logger = logging.getLogger("colab_bridge")


class ColabCommunicationError(Exception):
    """Raised when communication with Colab server fails."""
    pass


class ColabExecutionError(Exception):
    """Raised when remote execution on Colab returns an error."""
    pass


def _create_request(
    url: str,
    data: Optional[bytes] = None,
    content_type: str = "application/json",
    auth_token: str = "",
    method: Optional[str] = None,
) -> urllib.request.Request:
    headers = {"Content-Type": content_type}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    return req


def _safe_extractall(tar: tarfile.TarFile, path: Path):
    if hasattr(tarfile, "data_filter"):
        tar.extractall(path=path, filter="data")
    else:
        tar.extractall(path=path)


def is_colab_available(
    endpoint: Optional[str] = None,
    auth_token: str = "",
    timeout: float = 3.0,
) -> bool:
    """Quick non-blocking check whether the Colab worker is reachable and healthy."""
    cfg = get_colab_config()
    target_endpoint = (endpoint or cfg.endpoint).rstrip("/")
    token = auth_token or cfg.auth_token

    url = f"{target_endpoint}/health"
    try:
        req = _create_request(url, auth_token=token, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload.get("status") == "ok"
    except Exception:
        return False
    return False


def get_colab_status(
    endpoint: Optional[str] = None,
    auth_token: str = "",
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Fetch complete health & capability status from Colab server."""
    cfg = get_colab_config()
    target_endpoint = (endpoint or cfg.endpoint).rstrip("/")
    token = auth_token or cfg.auth_token

    url = f"{target_endpoint}/health"
    try:
        req = _create_request(url, auth_token=token, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            raise ColabCommunicationError(f"HTTP {resp.status}: {resp.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        raise ColabCommunicationError(f"Failed to connect to Colab worker at {target_endpoint}: {e}") from e


class ColabClient:
    """High-level client for executing heavy pipeline operations on Colab."""

    def __init__(self, config: Optional[ColabConfig] = None):
        self.config = config or get_colab_config()

    def health(self) -> Dict[str, Any]:
        return get_colab_status(self.config.endpoint, self.config.auth_token, self.config.timeout_health)

    def is_alive(self) -> bool:
        return is_colab_available(self.config.endpoint, self.config.auth_token, self.config.timeout_health)

    def render_remotion(
        self,
        props_path: Path,
        public_dir: Path,
        output_dir: Path,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Pack props.json and public/ directory into tarball, send to Colab,
        and unpack rendered video and stills into output_dir.
        """
        props_path = Path(props_path)
        public_dir = Path(public_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not props_path.is_file():
            raise FileNotFoundError(f"props.json not found at {props_path}")
        if not public_dir.is_dir():
            raise FileNotFoundError(f"public directory not found at {public_dir}")

        # 1. Package props.json and public/ into an in-memory tar.gz
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            tar.add(str(props_path), arcname="props.json")
            for root, _, files in os.walk(public_dir):
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(public_dir)
                    tar.add(str(full_p), arcname=f"public/{rel_p.as_posix()}")

        payload_bytes = buf.getvalue()
        url = f"{self.config.endpoint}/api/v1/render/remotion"
        req_timeout = timeout or self.config.timeout_render

        logger.info("Sending Remotion render job to Colab (%d bytes)...", len(payload_bytes))
        req = _create_request(
            url,
            data=payload_bytes,
            content_type="application/gzip",
            auth_token=self.config.auth_token,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=req_timeout) as resp:
                if resp.status != 200:
                    err_msg = resp.read().decode("utf-8", errors="ignore")
                    raise ColabExecutionError(f"Colab render failed (HTTP {resp.status}): {err_msg}")
                result_tar_bytes = resp.read()
        except urllib.error.HTTPError as e:
            err_text = e.read().decode("utf-8", errors="ignore")
            raise ColabExecutionError(f"Colab render HTTP {e.code}: {err_text}") from e
        except Exception as e:
            raise ColabCommunicationError(f"Colab render connection error: {e}") from e

        # 2. Extract returned tarball into output_dir
        with tarfile.open(fileobj=io.BytesIO(result_tar_bytes), mode="r:gz") as tar:
            _safe_extractall(tar, output_dir)

        # 3. Verify outputs
        video_file = output_dir / "video.mp4"
        if not video_file.is_file() or video_file.stat().st_size < 1000:
            raise ColabExecutionError("Colab worker finished but did not return a valid video.mp4")

        timing_file = output_dir / "render-timing.json"
        timings = []
        if timing_file.is_file():
            try:
                timings = json.loads(timing_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        return {
            "status": "success",
            "video_path": str(video_file),
            "timings": timings,
            "bytes_received": len(result_tar_bytes),
        }

    def synthesize_tts(
        self,
        request_payload: Dict[str, Any],
        output_dir: Path,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send TTS synthesis request payload to Colab, receiving WAVs and metadata."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        payload_bytes = json.dumps(request_payload).encode("utf-8")
        url = f"{self.config.endpoint}/api/v1/tts/synthesize"
        req_timeout = timeout or self.config.timeout_tts

        logger.info("Sending TTS synthesis job to Colab...")
        req = _create_request(
            url,
            data=payload_bytes,
            content_type="application/json",
            auth_token=self.config.auth_token,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=req_timeout) as resp:
                if resp.status != 200:
                    err_msg = resp.read().decode("utf-8", errors="ignore")
                    raise ColabExecutionError(f"Colab TTS failed (HTTP {resp.status}): {err_msg}")
                result_tar_bytes = resp.read()
        except urllib.error.HTTPError as e:
            err_text = e.read().decode("utf-8", errors="ignore")
            raise ColabExecutionError(f"Colab TTS HTTP {e.code}: {err_text}") from e
        except Exception as e:
            raise ColabCommunicationError(f"Colab TTS connection error: {e}") from e

        # Extract returned tarball into output_dir
        with tarfile.open(fileobj=io.BytesIO(result_tar_bytes), mode="r:gz") as tar:
            _safe_extractall(tar, output_dir)

        result_json_path = output_dir / "tts-result.json"
        if not result_json_path.is_file():
            raise ColabExecutionError("Colab TTS finished but did not return tts-result.json")

        meta = json.loads(result_json_path.read_text(encoding="utf-8"))
        return {
            "status": "success",
            "metadata": meta,
            "bytes_received": len(result_tar_bytes),
        }
