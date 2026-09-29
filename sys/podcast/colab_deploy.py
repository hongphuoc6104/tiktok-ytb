"""Provision and deploy the podcast-only Colab worker with ignored credentials."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import secrets
import json
import subprocess
import shutil
import time
import urllib.request
from typing import Dict, Optional


class ColabProvisioningError(RuntimeError):
    """Colab could not allocate the required GPU session; retry later."""


def _run(args, *, timeout: float, check: bool = True):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        details = (result.stderr or result.stdout or "No details returned by Colab CLI").strip()[-1200:]
        raise RuntimeError(details)
    return result


def _profile_cli(profile_alias: str, *args: str) -> list[str]:
    """Use a saved Colab account alias without exposing its token."""
    if not re.fullmatch(r"[a-z][a-z0-9_-]{1,31}", profile_alias):
        raise ColabProvisioningError("Invalid Colab profile alias")
    config_dir = Path.home() / ".config" / "colab-cli"
    wrapper = config_dir / "profile_cli.py"
    profiles_path = config_dir / "profiles.json"
    if not wrapper.is_file() or not profiles_path.is_file():
        raise ColabProvisioningError("Local Colab profile wrapper or registry is unavailable")
    try:
        profiles = json.loads(profiles_path.read_text(encoding="utf-8")).get("profiles", [])
        entry = next(item for item in profiles if item.get("alias") == profile_alias)
    except Exception as exc:
        raise ColabProvisioningError(f"Colab profile is not configured: {profile_alias}") from exc
    for key in ("token_path", "session_config"):
        if not Path(str(entry.get(key, ""))).is_file():
            raise ColabProvisioningError(f"Colab profile {profile_alias} is missing its {key}")

    colab_bin = shutil.which("colab") or str(Path.home() / ".local" / "bin" / "colab")
    try:
        first_line = Path(colab_bin).read_text(encoding="utf-8").splitlines()[0]
        interpreter = first_line[2:] if first_line.startswith("#!") else ""
    except (OSError, IndexError):
        interpreter = ""
    if not interpreter or not Path(interpreter).is_file():
        raise ColabProvisioningError("Cannot locate the Python runtime for the installed Colab CLI")
    return [interpreter, str(wrapper), profile_alias, *map(str, args)]


def _session_exists(profile_alias: str, session: str) -> bool:
    result = _run(_profile_cli(profile_alias, "sessions"), timeout=20, check=False)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Colab session listing failed").strip()[-800:]
        raise ColabProvisioningError(f"Cannot inspect Colab sessions; retry after checking Colab CLI access. {details}")
    return re.search(rf"(?<![A-Za-z0-9_.-]){re.escape(session)}(?![A-Za-z0-9_.-])", result.stdout + result.stderr) is not None


def _compute_units_balance(profile_alias: str) -> float:
    """Read the selected account's balance without switching profiles."""
    result = _run(_profile_cli(profile_alias, "usage"), timeout=30, check=False)
    if result.returncode != 0:
        raise ColabProvisioningError("Không đọc được số dư compute units của profile Colab đang chọn.")
    match = re.search(r"Current balance:\s*([0-9]+(?:\.[0-9]+)?)\s*compute units",
                      result.stdout + "\n" + result.stderr, re.IGNORECASE)
    if not match:
        raise ColabProvisioningError("Colab không trả số dư compute units; giữ checkpoint và dừng cấp GPU.")
    return float(match.group(1))


def _provision(profile_alias: str, session: str) -> None:
    result = _run(_profile_cli(profile_alias, "new", "-s", session, "--gpu", "T4"),
                  timeout=120, check=False)
    if result.returncode == 0:
        return
    details = (result.stderr or result.stdout or "Colab assignment API returned no details").strip()[-1200:]
    raise ColabProvisioningError(
        "Colab could not provision the required T4 session; this is retryable when the assignment service is available. "
        f"No CPU fallback was attempted. {details}"
    )


def _exec_remote(profile_alias: str, session: str, script: Path, *, timeout: float,
                 env: Optional[Dict[str, str]] = None):
    command = _profile_cli(profile_alias, "exec", "--session", session,
                           "--file", str(script), "--timeout", str(timeout))
    for key, value in (env or {}).items():
        command.extend(["--env", f"{key}={value}"])
    return _run(command, timeout=timeout + 30, check=False)


def keepalive_podcast_worker(sys_root: Optional[Path] = None) -> Dict[str, str]:
    """Run a tiny notebook cell while remote TTS runs outside the kernel.

    Colab can reclaim a runtime when its notebook kernel stays idle even though
    the podcast HTTP worker is still using the T4 in a child process. Call this
    only while a TTS task is active; it does not request or change an
    accelerator.
    """
    root = Path(sys_root or Path(__file__).resolve().parents[1]).resolve()
    state = _load_state(root)
    session = state.get("session")
    profile_alias = state.get("profile_alias")
    if (not isinstance(session, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", session)
            or not isinstance(profile_alias, str)):
        raise ColabProvisioningError("Podcast Colab session profile is not configured")
    script = root / "podcast" / "colab_keepalive.py"
    if not script.is_file():
        raise ColabProvisioningError("Podcast Colab keepalive cell is missing")
    result = _exec_remote(profile_alias, session, script, timeout=30)
    if result.returncode != 0:
        raise ColabProvisioningError("Could not send a lightweight activity cell to the active Colab session")
    return {"session": session, "profile_alias": profile_alias}


def _state_path(sys_root: Path) -> Path:
    return sys_root / ".state" / "podcast-colab.json"


def _load_state(sys_root: Path) -> dict:
    path = _state_path(sys_root)
    if not path.is_file():
        return {}
    try:
        if path.stat().st_mode & 0o077:
            raise RuntimeError("Podcast Colab state permissions must be 0600")
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError("Podcast Colab state is unreadable") from exc


def _write_state(sys_root: Path, state: dict) -> Path:
    state_dir = sys_root / ".state"
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_path = _state_path(sys_root)
    temp = state_path.with_name(state_path.name + ".tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        temp.chmod(0o600)
    except OSError:
        pass
    os.replace(temp, state_path)
    try:
        state_path.chmod(0o600)
    except OSError:
        pass
    return state_path


def _worker_source_hash(sys_root: Path) -> str:
    """Hash the local server/engine/runner bundle for safe idempotent upgrades."""
    digest = hashlib.sha256()
    files = (
        sys_root / "colab_bridge" / "server.py",
        sys_root / "colab_bridge" / "tts_engine.py",
        sys_root / "podcast" / "remote_tts_runner.py",
    )
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _ensure_local_token(sys_root: Path, state: dict) -> tuple[Path, str]:
    state_dir = sys_root / ".state"
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        state_dir.chmod(0o700)
    except OSError:
        pass
    # This short-lived file is uploaded once, then removed locally. Persistent
    # endpoint/token state is stored separately at .state/podcast-colab.json.
    token_path = state_dir / ".podcast-colab-token-upload"
    token = str(state.get("auth_token", ""))
    if not token and token_path.is_file():
        token = token_path.read_text(encoding="utf-8").strip()
    if len(token) < 32:
        token = secrets.token_urlsafe(48)
        temp = token_path.with_name(token_path.name + ".tmp")
        temp.write_text(token, encoding="utf-8")
        try:
            temp.chmod(0o600)
        except OSError:
            pass
        os.replace(temp, token_path)
        try:
            token_path.chmod(0o600)
        except OSError:
            pass
    token_path.write_text(token, encoding="utf-8")
    try:
        token_path.chmod(0o600)
    except OSError:
        pass
    return token_path, token


def _upload(profile_alias: str, session: str, local_path: Path, remote_path: str) -> None:
    result = _run(_profile_cli(profile_alias, "upload", str(local_path), remote_path,
                               "--session", session), timeout=90, check=False)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Colab upload failed").strip()[-1000:]
        raise RuntimeError(f"Could not upload podcast worker component {local_path.name}: {details}")


def restore_local_tts_checkpoints(sys_root: Path, episode_id: str) -> Dict[str, object]:
    """Restore verified local chunk checkpoints into the selected Colab cache.

    This runs only on the already selected profile; it never switches accounts.
    The remote runner can then reuse completed chunks after a Colab runtime is
    recreated, while generating only missing chunks.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", episode_id):
        raise ColabProvisioningError("Invalid podcast episode id for checkpoint restore")
    root = Path(sys_root).resolve()
    state = _load_state(root)
    session, profile_alias = state.get("session"), state.get("profile_alias")
    if not isinstance(session, str) or not isinstance(profile_alias, str):
        raise ColabProvisioningError("Podcast Colab session profile is not configured")
    from podcast.tts import PodcastColabTTS

    episode_dir = root / "runs" / episode_id
    client = PodcastColabTTS(episode_id, episode_dir, sys_root=root)
    tts_manifest = client._read_manifest()
    imported: list[dict] = []
    saved_parts = tts_manifest.get("parts", {})
    for part_id in tts_manifest.get("planned_parts", []):
        # A planned part has no checkpoint request until synthesis has actually
        # started. Skip untouched parts when restoring after a runtime restart.
        if str(part_id) in saved_parts:
            imported.extend(client.import_local_checkpoints(str(part_id)))
    # Also restore already-adopted local chunks even when the current part
    # request ID changed after a retry. Those verified WAVs live in the normal
    # TTS cache and remain reusable independently of the request checkpoint.
    tts_manifest = client._read_manifest()
    for item in tts_manifest.get("chunks", {}).values():
        if isinstance(item, dict) and item.get("state") == "succeeded":
            imported.append(dict(item))

    by_hash: dict[str, dict] = {}
    for item in imported:
        chunk_hash = item.get("chunk_hash")
        chunk_id = item.get("chunk_id")
        local_path = Path(str(item.get("path", ""))).resolve()
        try:
            local_path.relative_to((episode_dir / "tts").resolve())
        except ValueError as exc:
            raise ColabProvisioningError(f"Checkpoint path escapes the TTS cache for {chunk_id}") from exc
        if not isinstance(chunk_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", chunk_hash):
            raise ColabProvisioningError(f"Checkpoint chunk hash is invalid for {chunk_id}")
        if not local_path.is_file() or hashlib.sha256(local_path.read_bytes()).hexdigest() != item.get("wav_sha256"):
            raise ColabProvisioningError(f"Checkpoint WAV is missing or changed for {chunk_id}")
        previous = by_hash.get(chunk_hash)
        if previous and previous.get("wav_sha256") != item.get("wav_sha256"):
            raise ColabProvisioningError(f"Two checkpoints disagree for chunk hash {chunk_hash}")
        by_hash[chunk_hash] = item

    for chunk_hash, item in by_hash.items():
        chunk_id = str(item["chunk_id"])
        wav_path = Path(str(item["path"]))
        meta_path = episode_dir / "tts" / "chunk_meta" / f"{chunk_id}.json"
        if not meta_path.is_file():
            raise ColabProvisioningError(f"Checkpoint metadata is missing for {chunk_id}")
        cache_base = f"/content/video-pilot-podcast-tts/chunk-cache/{chunk_hash}"
        _upload(profile_alias, session, wav_path, cache_base + ".wav")
        _upload(profile_alias, session, meta_path, cache_base + ".json")

    return {"session": session, "profile_alias": profile_alias,
            "restored_chunks": len(by_hash), "chunk_ids": sorted(str(item["chunk_id"]) for item in by_hash.values())}


def _worker_ready(endpoint: str, token: str) -> Optional[Dict[str, object]]:
    try:
        request = urllib.request.Request(endpoint.rstrip("/") + "/health", method="GET")
        with urllib.request.urlopen(request, timeout=5) as response:
            health = json.loads(response.read().decode("utf-8"))
        gpu = health.get("gpu") if isinstance(health, dict) else None
        if health.get("status") != "ok" or not isinstance(gpu, dict) or gpu.get("available") is not True:
            return None
        request = urllib.request.Request(endpoint.rstrip("/") + "/api/v1/podcast/tts/runtime",
                                         headers={"Authorization": f"Bearer {token}"}, method="GET")
        with urllib.request.urlopen(request, timeout=5) as response:
            runtime = json.loads(response.read().decode("utf-8"))
        return {"health": health, "runtime": runtime} if runtime.get("runtime_id") else None
    except Exception:
        return None


def _wait_health(endpoint: str, token: str, attempts: int = 30) -> Dict[str, object]:
    last_error = "worker did not answer"
    for _ in range(attempts):
        try:
            ready = _worker_ready(endpoint, token)
            if ready:
                return ready["health"]
            last_error = "worker health/task API did not report an authenticated CUDA runtime"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(2)
    raise RuntimeError(f"Colab worker did not become healthy with a GPU: {last_error}")


def deploy_podcast_worker(session: str = "podcast-worker", sys_root: Optional[Path] = None,
                          profile_alias: str = "alternate") -> Dict[str, str]:
    """Create/reuse a T4 session, upload current files, and start its tunnel."""
    # Free-trial availability is a user-specified assumption, not verified billing.
    # Service errors still stop the existing account; never fail over to evade quota.
    root = Path(sys_root or Path(__file__).resolve().parents[1]).resolve()
    state = _load_state(root)
    source_hash = _worker_source_hash(root)
    existing_endpoint = state.get("endpoint")
    existing_token = state.get("auth_token")
    if (state.get("session") == session and state.get("profile_alias") == profile_alias and
            state.get("worker_source_hash") == source_hash and
            isinstance(existing_endpoint, str) and
            isinstance(existing_token, str) and _worker_ready(existing_endpoint, existing_token)):
        return {"session": session, "endpoint": existing_endpoint,
                "token_path": str(_state_path(root)), "reused": "true"}
    if not _session_exists(profile_alias, session):
        _provision(profile_alias, session)

    remote_boot = root / "colab_bridge" / "remote_boot.py"
    bootstrap = _exec_remote(profile_alias, session, remote_boot, timeout=3600,
                             env={"PODCAST_BOOTSTRAP_ONLY": "1"})
    if bootstrap.returncode != 0:
        details = (bootstrap.stderr or bootstrap.stdout or "Colab bootstrap failed").strip()[-1200:]
        raise RuntimeError(f"Could not prepare the Colab runtime: {details}")

    components = (
        (root / "colab_bridge" / "server.py", "/content/tiktok-ytb/sys/colab_bridge/server.py"),
        (root / "colab_bridge" / "tts_engine.py", "/content/tiktok-ytb/sys/colab_bridge/tts_engine.py"),
        (root / "podcast" / "remote_tts_runner.py", "/content/tiktok-ytb/sys/podcast/remote_tts_runner.py"),
    )
    for local_path, remote_path in components:
        if not local_path.is_file():
            raise FileNotFoundError(local_path)
        _upload(profile_alias, session, local_path, remote_path)

    token_path, token = _ensure_local_token(root, state)
    state = {"session": session, "profile_alias": profile_alias,
             "endpoint": state.get("endpoint"), "auth_token": token,
             "worker_source_hash": source_hash,
             "updated_at": time.time(), "pending_deploy": True, "task_storage": "colab_runtime_local"}
    _write_state(root, state)
    remote_token_path = "/content/.podcast-colab-token-once"
    _upload(profile_alias, session, token_path, remote_token_path)
    token_path.unlink(missing_ok=True)
    start = _exec_remote(profile_alias, session, remote_boot, timeout=90,
                         env={"PODCAST_START_WORKER": "1", "PODCAST_COLAB_TOKEN_FILE": remote_token_path})
    if start.returncode != 0:
        details = (start.stderr or start.stdout or "Colab worker start failed").strip()[-1200:]
        raise RuntimeError(f"Could not start the authenticated Colab worker: {details}")
    marker = "COLAB_WORKER_ONLINE:"
    endpoint = next((line.split(marker, 1)[1].strip() for line in (start.stdout + "\n" + start.stderr).splitlines()
                     if marker in line), None)
    if not endpoint:
        raise RuntimeError("Colab worker started without returning its tunnel endpoint")
    _write_state(root, {"session": session, "profile_alias": profile_alias,
                        "endpoint": endpoint, "auth_token": token,
                        "worker_source_hash": source_hash,
                        "updated_at": time.time(), "pending_deploy": True,
                        "task_storage": "colab_runtime_local"})
    _wait_health(endpoint, token)
    state_path = _write_state(root, {"session": session, "profile_alias": profile_alias,
                                     "endpoint": endpoint, "auth_token": token,
                                     "worker_source_hash": source_hash,
                                     "updated_at": time.time(), "pending_deploy": False,
                                     "task_storage": "colab_runtime_local"})
    return {"session": session, "endpoint": endpoint, "token_path": str(state_path), "reused": "false"}


def main():
    parser = argparse.ArgumentParser(description="Deploy the podcast TTS worker to Google Colab T4")
    parser.add_argument("--session", default="podcast-worker")
    parser.add_argument("--profile", default="alternate")
    args = parser.parse_args()
    result = deploy_podcast_worker(args.session, profile_alias=args.profile)
    print(f"Podcast Colab worker ready for session {result['session']} using profile {args.profile}.")


if __name__ == "__main__":
    main()
