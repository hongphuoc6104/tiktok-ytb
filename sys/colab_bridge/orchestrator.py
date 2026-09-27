"""Colab Orchestrator: High-level automated lifecycle controller for AI Agents."""

import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("colab_orchestrator")

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".state"
ENDPOINT_FILE = STATE_DIR / "colab_endpoint.json"
REMOTE_BOOT_SCRIPT = Path(__file__).resolve().parent / "remote_boot.py"


def get_colab_bin() -> str:
    """Locate colab executable."""
    bin_path = shutil.which("colab")
    if bin_path:
        return bin_path
    home_bin = Path.home() / ".local/bin/colab"
    if home_bin.is_file():
        return str(home_bin)
    raise FileNotFoundError("colab CLI executable not found in PATH or ~/.local/bin")


def is_authenticated() -> bool:
    """Check if colab CLI has an active auth token."""
    token_file = Path.home() / ".config/colab-cli/token.json"
    return token_file.is_file() and token_file.stat().st_size > 10


def list_sessions() -> Dict[str, Any]:
    """Query active Colab sessions."""
    colab = get_colab_bin()
    try:
        proc = subprocess.run([colab, "--auth=oauth2", "sessions"], capture_output=True, text=True, timeout=10)
        return {"returncode": proc.returncode, "output": proc.stdout + proc.stderr}
    except Exception as e:
        return {"returncode": -1, "error": str(e)}


def has_active_session(session_name: str = "video-worker") -> bool:
    res = list_sessions()
    if res.get("returncode") == 0:
        return session_name in res.get("output", "")
    return False


def provision_session(session_name: str = "video-worker", gpu: str = "T4") -> str:
    """Create a new Colab VM session with GPU acceleration."""
    colab = get_colab_bin()
    if has_active_session(session_name):
        logger.info("Reusing existing Colab session '%s'", session_name)
        return session_name

    logger.info("Provisioning fresh Colab VM '%s' (GPU %s)...", session_name, gpu)
    cmd = [colab, "--auth=oauth2", "new", "-s", session_name, "--gpu", gpu]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        # Fallback to CPU if GPU quota unavailable
        logger.warning("GPU %s allocation failed; retrying with CPU...", gpu)
        cmd_cpu = [colab, "--auth=oauth2", "new", "-s", session_name]
        proc = subprocess.run(cmd_cpu, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            raise RuntimeError(f"Colab VM provisioning failed: {proc.stderr or proc.stdout}")

    logger.info("Colab session '%s' created successfully!", session_name)
    return session_name


def stop_session(session_name: str = "video-worker") -> bool:
    """Tear down Colab VM to release GPU resources and stop billing."""
    colab = get_colab_bin()
    logger.info("Stopping Colab session '%s'...", session_name)
    proc = subprocess.run([colab, "--auth=oauth2", "stop", "-s", session_name], capture_output=True, text=True, timeout=30)
    if ENDPOINT_FILE.is_file():
        try:
            ENDPOINT_FILE.unlink()
        except Exception:
            pass
    return proc.returncode == 0


def get_status(session_name: str = "video-worker") -> Dict[str, Any]:
    """Retrieve session telemetry."""
    colab = get_colab_bin()
    proc = subprocess.run([colab, "--auth=oauth2", "status", "-s", session_name], capture_output=True, text=True, timeout=10)
    return {
        "session": session_name,
        "active": proc.returncode == 0,
        "raw_status": proc.stdout or proc.stderr,
    }


def save_endpoint(endpoint: str, auth_token: str = ""):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"endpoint": endpoint.rstrip("/"), "auth_token": auth_token, "updated_at": time.time()}
    ENDPOINT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_saved_endpoint() -> Optional[str]:
    if ENDPOINT_FILE.is_file():
        try:
            data = json.loads(ENDPOINT_FILE.read_text(encoding="utf-8"))
            return data.get("endpoint")
        except Exception:
            pass
    return None
