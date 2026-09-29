"""Configuration management for Colab Bridge."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ColabConfig:
    """Settings controlling Google Colab offloading."""

    def __init__(
        self,
        enabled: bool = False,
        endpoint: str = "http://localhost:8088",
        auth_token: str = "",
        timeout_render: int = 1800,
        timeout_tts: int = 600,
        timeout_health: float = 3.0,
        fallback_to_local: bool = False,
        tasks: Optional[Dict[str, bool]] = None,
    ):
        self.enabled = enabled
        self.endpoint = endpoint.rstrip("/")
        self.auth_token = auth_token
        self.timeout_render = timeout_render
        self.timeout_tts = timeout_tts
        self.timeout_health = timeout_health
        self.fallback_to_local = fallback_to_local
        self.tasks = tasks or {
            "remotion_render": True,
            "expressive_tts": True,
        }

    def is_task_enabled(self, task_name: str) -> bool:
        if not self.enabled:
            return False
        return bool(self.tasks.get(task_name, False))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "auth_token": self.auth_token,
            "timeout_render": self.timeout_render,
            "timeout_tts": self.timeout_tts,
            "timeout_health": self.timeout_health,
            "fallback_to_local": self.fallback_to_local,
            "tasks": self.tasks,
        }


def get_colab_config(root_dir: Optional[Path] = None) -> ColabConfig:
    """Load ColabConfig from root_dir/config.json, state file, or env vars."""
    root = root_dir or Path(__file__).resolve().parents[1]
    cfg_file = root / "config.json"

    data: Dict[str, Any] = {}
    if cfg_file.is_file():
        try:
            full_cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
            data = full_cfg.get("colab_offload", {})
        except Exception:
            data = {}

    # Check state file (e.g. written when Colab notebook boots up)
    state_file = root / ".state" / "colab_endpoint.json"
    if state_file.is_file():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            if "endpoint" in state_data:
                data["endpoint"] = state_data["endpoint"]
            if "auth_token" in state_data:
                data["auth_token"] = state_data["auth_token"]
        except Exception:
            pass

    # Environment overrides
    env_enabled = os.environ.get("COLAB_OFFLOAD_ENABLED")
    if env_enabled is not None:
        data["enabled"] = env_enabled.strip().lower() in ("1", "true", "yes")

    env_endpoint = os.environ.get("COLAB_ENDPOINT")
    if env_endpoint:
        data["endpoint"] = env_endpoint.strip()

    env_token = os.environ.get("COLAB_AUTH_TOKEN")
    if env_token:
        data["auth_token"] = env_token.strip()

    return ColabConfig(
        enabled=data.get("enabled", False),
        endpoint=data.get("endpoint", "http://localhost:8088"),
        auth_token=data.get("auth_token", ""),
        timeout_render=int(data.get("timeout_render", 1800)),
        timeout_tts=int(data.get("timeout_tts", 600)),
        timeout_health=float(data.get("timeout_health", 3.0)),
        fallback_to_local=bool(data.get("fallback_to_local", False)),
        tasks=data.get("tasks"),
    )
