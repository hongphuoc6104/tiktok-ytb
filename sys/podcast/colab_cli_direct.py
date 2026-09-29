"""Foreground Colab CLI transport for resumable podcast TTS.

This path runs the podcast runner in the selected notebook kernel itself. It
does not start a remote HTTP server, tunnel, or background worker.
"""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any, Callable, Mapping, Sequence
import uuid

from .colab_deploy import (
    ColabProvisioningError,
    _exec_remote,
    _load_state,
    _profile_cli,
    _run,
    _upload,
)
from .tts import (
    MAX_PART_ATTEMPTS,
    PodcastChunk,
    PodcastColabTTS,
    PodcastTTSAmbiguous,
    PodcastTTSRemoteFailure,
    _atomic_json,
    canonical_json,
    sha256,
)


REMOTE_SYS = Path("/content/tiktok-ytb/sys")
REMOTE_STATE = Path("/content/video-pilot-podcast-tts")
REMOTE_RUNNER = REMOTE_SYS / "podcast" / "remote_tts_runner.py"
REMOTE_ARCHIVE_NAME = "podcast-result.tar.gz"
TORCH_STACK = {"torch": "2.8.0+cu128", "torchvision": "0.23.0+cu128",
               "torchaudio": "2.8.0+cu128"}


class PodcastColabCLIRunner:
    """Synthesize one stable quarter-part through a Colab CLI notebook cell."""

    def __init__(self, tts: PodcastColabTTS, *, profile_alias: str = "alternate",
                 session: str = "podcast-worker"):
        self.tts = tts
        self.sys_root = tts.sys_root
        self.profile_alias = profile_alias
        self.session = session
        self.runtime_id: str | None = None

    def _cell(self, source: str, *, timeout: float = 120,
              env: Mapping[str, str] | None = None, stream: bool = False) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as handle:
            handle.write(source)
            script = Path(handle.name)
        try:
            command = _profile_cli(self.profile_alias, "exec", "--session", self.session,
                                   "--file", str(script), "--timeout", str(timeout))
            for key, value in (env or {}).items():
                command.extend(["--env", f"{key}={value}"])
            if not stream:
                return _run(command, timeout=timeout + 60, check=False)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, bufsize=1)
            captured: list[str] = []
            for line in process.stdout or ():
                captured.append(line)
                print(line, end="", flush=True)
            code = process.wait(timeout=timeout + 60)
            return subprocess.CompletedProcess(command, code, "".join(captured), "")
        finally:
            script.unlink(missing_ok=True)

    def ensure_runtime(self) -> dict[str, Any]:
        """Prepare the T4 kernel once, then identify its persistent runtime ID."""
        probe = r'''from importlib import metadata
from pathlib import Path
import json
root = Path("/content/video-pilot-podcast-tts")
target = Path("/content/torchvision-0.23.0-target")
try:
    versions = {name: metadata.version(name) for name in ("torch", "torchvision", "torchaudio")}
except metadata.PackageNotFoundError:
    versions = {}
target_ok = any(target.glob("torchvision-0.23.0+cu128.dist-info/METADATA"))
ready = (versions == {"torch": "2.8.0+cu128", "torchvision": "0.23.0+cu128",
                     "torchaudio": "2.8.0+cu128"}
         and target_ok
         and Path("/content/BetterBox-TTS/OmniVoice/modelOmniLocal/config.json").is_file())
print("PODCAST_CLI_ENV=" + json.dumps({"ready": ready, "versions": versions}))
'''
        env_probe = self._cell(probe, timeout=120)
        if env_probe.returncode != 0:
            raise ColabProvisioningError("Không đọc được trạng thái môi trường Colab qua CLI.")
        env_line = next((line.partition("=")[2].strip() for line in env_probe.stdout.splitlines()
                         if line.startswith("PODCAST_CLI_ENV=")), None)
        if not env_line:
            raise ColabProvisioningError("Colab CLI không trả trạng thái thư viện TTS.")
        env_info = json.loads(env_line)
        if not env_info.get("ready"):
            bootstrap = r'''from pathlib import Path
import importlib.metadata as metadata
import json, shutil, subprocess, sys

def run(label, args):
    print("[PODCAST_BOOT] " + label, flush=True)
    subprocess.run(list(map(str, args)), check=True)

betterbox = Path("/content/BetterBox-TTS")
if not betterbox.is_dir():
    run("clone TTS source", ["git", "clone", "--depth", "1",
        "https://github.com/nowtranminh1-TTS/BetterBox-TTS.git", betterbox])
run("install audio dependencies", [sys.executable, "-m", "pip", "install", "-q",
    "soundfile", "numpy", "scipy", "vieneu"])
run("install model requirements", [sys.executable, "-m", "pip", "install", "-q",
    "-r", betterbox / "general" / "requirements.txt"])
run("pin matching T4 CUDA stack", [sys.executable, "-m", "pip", "install", "-q",
    "--force-reinstall", "--no-deps", "--index-url", "https://download.pytorch.org/whl/cu128",
    "torch==2.8.0+cu128", "torchvision==0.23.0+cu128", "torchaudio==2.8.0+cu128"])
model_dir = betterbox / "OmniVoice" / "modelOmniLocal"
if not (model_dir / "config.json").is_file():
    run("download pretrained OmniVoice model", [sys.executable, "-c",
        "from huggingface_hub import snapshot_download; "
        "snapshot_download(repo_id='kjanh/KhanhTTS-OmniVoice', "
        "local_dir='/content/BetterBox-TTS/OmniVoice/modelOmniLocal')"])
tv_target = Path("/content/torchvision-0.23.0-target")
shutil.rmtree(tv_target, ignore_errors=True)
run("prepare torchvision runtime path", [sys.executable, "-m", "pip", "install", "-q",
    "--no-deps", "--ignore-installed", "--target", tv_target,
    "--index-url", "https://download.pytorch.org/whl/cu128", "torchvision==0.23.0+cu128"])
for path in (Path("/content/tiktok-ytb/sys/podcast"),
             Path("/content/tiktok-ytb/sys/assets/voices"),
             Path("/content/video-pilot-podcast-tts/chunk-cache")):
    path.mkdir(parents=True, exist_ok=True)
Path("/content/video-pilot-podcast-tts/environment.json").write_text(json.dumps({
    "torch": "2.8.0+cu128", "torchvision": "0.23.0+cu128",
    "torchaudio": "2.8.0+cu128", "model": "kjanh/KhanhTTS-OmniVoice"
}, indent=2), encoding="utf-8")
print("[PODCAST_BOOT] ready; kernel restart needed to load the pinned stack", flush=True)
'''
            boot_result = self._cell(bootstrap, timeout=7200, stream=True)
            if boot_result.returncode != 0:
                raise ColabProvisioningError(
                    "Bootstrap Colab chưa hoàn tất; giữ nguyên checkpoint và không gửi TTS. "
                    + (boot_result.stderr or boot_result.stdout or "Colab bootstrap failed")[-2000:])
            restarted = _run(_profile_cli(self.profile_alias, "restart-kernel", "--session", self.session),
                             timeout=120, check=False)
            if restarted.returncode != 0:
                raise ColabProvisioningError("Không khởi động lại được kernel sau khi ghim thư viện TTS.")

        source = r'''from pathlib import Path
import json, uuid
import torch
import sys
sys.path.insert(0, "/content/torchvision-0.23.0-target")
import torchvision, torchaudio
root = Path("/content/video-pilot-podcast-tts")
root.mkdir(parents=True, exist_ok=True)
runtime_file = root / "cli-runtime.json"
try:
    data = json.loads(runtime_file.read_text(encoding="utf-8"))
    runtime_id = data.get("runtime_id")
except Exception:
    runtime_id = None
if not isinstance(runtime_id, str) or not runtime_id:
    runtime_id = uuid.uuid4().hex
    runtime_file.write_text(json.dumps({"runtime_id": runtime_id}), encoding="utf-8")
gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else ""
free, total = torch.cuda.mem_get_info() if torch.cuda.is_available() else (0, 0)
versions = {"torch": torch.__version__, "torchvision": torchvision.__version__,
            "torchaudio": torchaudio.__version__}
print("PODCAST_CLI_RUNTIME=" + json.dumps({"runtime_id": runtime_id, "gpu": gpu, "versions": versions,
      "vram_total_bytes": total, "vram_free_bytes": free}))
'''
        result = self._cell(source, timeout=120)
        if result.returncode != 0:
            raise ColabProvisioningError(
                "Không thể thực thi notebook Colab hiện tại qua CLI. "
                + (result.stderr or result.stdout or "Colab exec failed")[-1000:])
        marker = next((line.partition("=")[2].strip() for line in result.stdout.splitlines()
                       if line.startswith("PODCAST_CLI_RUNTIME=")), None)
        if not marker:
            raise ColabProvisioningError("Colab CLI không trả thông tin runtime TTS.")
        info = json.loads(marker)
        if not str(info.get("gpu", "")).startswith("Tesla T4"):
            raise ColabProvisioningError(f"Phiên Colab hiện tại không phải T4: {info.get('gpu') or 'không có GPU'}")
        if info.get("versions") != TORCH_STACK:
            raise ColabProvisioningError(f"Môi trường TTS Colab chưa đúng bộ đã ghim: {info.get('versions')}")
        runtime_id = info.get("runtime_id")
        if not isinstance(runtime_id, str) or not runtime_id:
            raise ColabProvisioningError("Colab CLI không trả runtime ID hợp lệ.")
        self.runtime_id = runtime_id
        return info

    def _ensure_remote_layout(self) -> None:
        voice_id = self.tts.profile.voice_id
        source = f'''from pathlib import Path
for p in ({str(REMOTE_SYS / "podcast")!r},
          {str(REMOTE_SYS / "assets" / "voices" / voice_id)!r},
          {str(REMOTE_STATE / "chunk-cache")!r}):
    Path(p).mkdir(parents=True, exist_ok=True)
'''
        result = self._cell(source)
        if result.returncode != 0:
            raise ColabProvisioningError("Không tạo được thư mục làm việc trong phiên Colab.")

    def _upload_source_and_profile(self) -> None:
        profile = self.tts.profile
        voice_dir = self.tts.sys_root / "assets" / "voices" / profile.voice_id
        files = {
            self.tts.sys_root / "podcast" / "remote_tts_runner.py": REMOTE_RUNNER,
            voice_dir / "voice_config.json": REMOTE_SYS / "assets" / "voices" / profile.voice_id / "voice_config.json",
        }
        voice_files = profile.voice_config.get("files") or {}
        reference_name = voice_files.get("reference_wav")
        transcript_name = voice_files.get("transcript_txt")
        for filename in (reference_name, transcript_name):
            if not isinstance(filename, str) or Path(filename).name != filename:
                raise ColabProvisioningError("Voice profile contains an unsafe reference filename.")
        files[voice_dir / reference_name] = REMOTE_SYS / "assets" / "voices" / profile.voice_id / reference_name
        for local_path, remote_path in files.items():
            if not local_path.is_file():
                raise ColabProvisioningError(f"Thiếu file runtime podcast: {local_path.name}")
            _upload(self.profile_alias, self.session, local_path, str(remote_path))
        # The profile fingerprint is based on the trimmed transcript, so upload
        # exactly those verified bytes rather than a source file's trailing newline.
        remote_transcript = REMOTE_SYS / "assets" / "voices" / profile.voice_id / transcript_name
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
            handle.write(profile.transcript)
            transcript_path = Path(handle.name)
        try:
            _upload(self.profile_alias, self.session, transcript_path, str(remote_transcript))
        finally:
            transcript_path.unlink(missing_ok=True)

    def _prepare_request(self, part_id: str, chunks: Sequence[PodcastChunk], *,
                         speed: float, pitch_shift: float, retry_failed: bool) -> tuple[str, str, dict, list, dict]:
        tts = self.tts
        profile = tts.profile
        payload, normalized = tts._make_payload(chunks, speed, pitch_shift, profile)
        request_hash = sha256(canonical_json(payload))
        episode_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", tts.episode_id)[:48]
        part_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", part_id)[:40]
        base_id = f"podcast-{episode_safe}-{part_safe}-{request_hash[:20]}"
        manifest = tts._read_manifest()
        old_id = manifest.get("parts", {}).get(part_id)
        old = manifest.get("requests", {}).get(old_id, {}) if old_id else {}
        recovered_result_loss = bool(
            old and old.get("request_hash") == request_hash
            and "Colab synthesis finished but the result archive could not be downloaded." in str(old.get("error", ""))
            and old.get("state") in ("ambiguous", "failed")
            and not tts._local_chunks_valid(old)
        )

        if old and old.get("request_hash") == request_hash and old.get("runtime_id") == self.runtime_id:
            if old.get("state") == "succeeded" and tts._local_chunks_valid(old):
                return old_id, request_hash, payload, normalized, old
            if old.get("state") in ("running", "submitting", "ambiguous", "interrupted", "partial_failed"):
                request_id = old_id
                attempt = int(old.get("attempt", 0))
            elif old.get("state") == "failed" and not retry_failed:
                raise PodcastTTSRemoteFailure(old.get("error", "Colab TTS part failed; pass retry_failed to retry."))
            else:
                request_id = ""
                attempt = 0
        else:
            request_id = ""
            attempt = 0
            if old and old.get("request_hash") == request_hash and old.get("state") not in ("succeeded", "failed"):
                tts._set_request_state(old_id, "failed",
                                       error="Colab runtime was replaced; any unsaved remote output is unavailable.")

        if not request_id:
            prior = [row for row in manifest.get("requests", {}).values()
                     if row.get("part_id") == part_id and row.get("base_request_id") == base_id]
            used = sum(max(1, int(row.get("remote_attempts", 1))) for row in prior)
            # One bounded recovery is permitted when TTS finished on Colab but
            # its archive was lost with the previous runtime. Verified local
            # checkpoints still suppress every already-saved chunk.
            attempt_limit = MAX_PART_ATTEMPTS + int(recovered_result_loss)
            latest = max(prior, key=lambda row: int(row.get("attempt", 0)), default=None)
            if latest and latest.get("state") == "failed":
                if not retry_failed:
                    raise PodcastTTSRemoteFailure(latest.get("error", "Colab TTS part failed; retry is required."))
                if used >= attempt_limit:
                    raise PodcastTTSRemoteFailure("Podcast part exhausted its initial attempt and two retries.")
                attempt = used
                request_id = f"{base_id}-r{attempt}"
            else:
                request_id = latest.get("request_id", base_id) if latest else base_id
                attempt = int(latest.get("attempt", 0)) if latest else 0

        profile_path = tts._store_profile_bundle(profile)
        spec_path = f"requests/{request_id}.json"
        _atomic_json(tts.tts_dir / spec_path,
                     {"settings": payload["settings"], "scenes": normalized})
        entry = {"request_id": request_id, "base_request_id": base_id, "request_hash": request_hash,
                 "part_id": part_id, "runtime_id": self.runtime_id,
                 "profile_fingerprint": profile.fingerprint, "profile_bundle_path": profile_path,
                 "spec_path": spec_path, "state": "running", "attempt": attempt,
                 "remote_attempts": 1, "transport": "colab_cli_foreground",
                 "recovered_from_lost_result": recovered_result_loss,
                 "recovered_request_id": old_id if recovered_result_loss else None,
                 "chunk_ids": [item["id"] for item in normalized],
                 "created_at": old.get("created_at", time.time()), "updated_at": time.time()}

        def save(data):
            existing = data.setdefault("requests", {}).get(request_id)
            if existing and existing.get("request_hash") != request_hash:
                raise ValueError("Colab CLI request id already belongs to different content.")
            if existing:
                entry["created_at"] = existing.get("created_at", entry["created_at"])
            data["requests"][request_id] = {**(existing or {}), **entry}
            data.setdefault("parts", {})[part_id] = request_id
            data.setdefault("expected_chunks", {})[part_id] = entry["chunk_ids"]
            for scene in normalized:
                previous = data.setdefault("chunks", {}).get(scene["id"], {})
                if previous.get("chunk_hash") != scene["chunk_hash"]:
                    data["chunks"][scene["id"]] = {"chunk_id": scene["id"], "part_id": part_id,
                                                     "chunk_hash": scene["chunk_hash"], "state": "pending"}
        tts._update(save)
        record = tts._read_manifest()["requests"][request_id]
        runner_request = {"settings": payload["settings"], "scenes": normalized,
                          "profile_fingerprint": profile.fingerprint,
                          "request_id": request_id, "request_hash": request_hash}
        runner_path = tts.tts_dir / "requests" / f"{request_id}-runner.json"
        _atomic_json(runner_path, runner_request)
        return request_id, request_hash, runner_request, normalized, record

    @staticmethod
    def _remote_exec_cell() -> str:
        return r'''import os, runpy, tarfile
from pathlib import Path
runner = Path("/content/tiktok-ytb/sys/podcast/remote_tts_runner.py")
runpy.run_path(str(runner), run_name="__main__")
output = Path(os.environ["PODCAST_TTS_OUTPUT"])
archive = output.parent / "podcast-result.tar.gz"
with tarfile.open(archive, "w:gz") as tar:
    for relative in ("tts-result.json", "tts-progress.json"):
        path = output / relative
        if path.is_file(): tar.add(path, arcname=relative)
    for folder in ("chunks", "chunk_meta"):
        path = output / folder
        if path.is_dir():
            for item in sorted(path.iterdir()):
                if item.is_file(): tar.add(item, arcname=f"{folder}/{item.name}")
print("PODCAST_CLI_ARCHIVE=" + str(archive), flush=True)
'''

    def _import_archive(self, archive_path: Path, request_id: str, request_hash: str,
                        normalized: Sequence[Mapping[str, Any]], part_id: str) -> list[dict[str, Any]]:
        checkpoint = self.tts.tts_dir / "checkpoints" / request_id
        expected_names = {"tts-result.json", "tts-progress.json"}
        expected_ids = {str(item["id"]) for item in normalized}
        expected_names |= {f"chunks/{chunk_id}.wav" for chunk_id in expected_ids}
        expected_names |= {f"chunk_meta/{chunk_id}.json" for chunk_id in expected_ids}
        checkpoint.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(archive_path, "r:gz") as archive:
                members = archive.getmembers()
                names = set()
                for member in members:
                    rel = PurePosixPath(member.name)
                    if (member.name not in expected_names or rel.is_absolute() or ".." in rel.parts
                            or not member.isfile() or member.issym() or member.islnk()):
                        raise ValueError("Colab result archive contains an unexpected path.")
                    names.add(member.name)
                    destination = checkpoint.joinpath(*rel.parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError("Colab result archive has an unreadable entry.")
                    temp = destination.with_name(destination.name + f".{uuid.uuid4().hex}.tmp")
                    with source, temp.open("wb") as target:
                        target.write(source.read())
                    os.replace(temp, destination)
        except (OSError, tarfile.TarError) as exc:
            raise ValueError("Colab CLI returned an invalid podcast result archive.") from exc

        if not expected_names.issubset(names):
            missing = sorted(expected_names - names)
            raise ValueError("Colab result archive is incomplete: " + ", ".join(missing[:4]))
        result = json.loads((checkpoint / "tts-result.json").read_text(encoding="utf-8"))
        if result.get("request_id") != request_id or result.get("request_hash") != request_hash:
            raise ValueError("Colab TTS result identity does not match the active request.")
        segments = {item.get("scene_id"): item for item in result.get("segments", [])
                    if isinstance(item, dict)}
        if set(segments) != expected_ids:
            raise ValueError("Colab TTS result has missing or duplicate chunk records.")
        for scene in normalized:
            segment = segments[scene["id"]]
            if segment.get("chunk_hash") != scene.get("chunk_hash"):
                raise ValueError(f"Colab TTS result chunk hash mismatch for {scene['id']}.")
        imported = self.tts.import_local_checkpoints(part_id)
        if {item.get("chunk_id") for item in imported} != expected_ids:
            raise ValueError("Not all verified Colab WAVs were imported into local checkpoints.")
        return imported

    def synthesize_part(self, part_id: str, chunks: Sequence[PodcastChunk], *,
                        speed: float, pitch_shift: float, retry_failed: bool = False,
                        progress_callback: Callable[[dict], None] | None = None) -> dict[str, Any]:
        runtime = self.ensure_runtime()
        self._ensure_remote_layout()
        self._upload_source_and_profile()
        request_id, request_hash, runner_request, normalized, record = self._prepare_request(
            part_id, chunks, speed=speed, pitch_shift=pitch_shift, retry_failed=retry_failed)
        if record.get("state") == "succeeded" and self.tts._local_chunks_valid(record):
            return {"status": "success", "request_id": request_id, "part_id": part_id,
                    "chunks": self.tts._local_chunk_outputs(record), "reused": True}

        runner_path = self.tts.tts_dir / "requests" / f"{request_id}-runner.json"
        remote_request = REMOTE_STATE / "tasks" / request_id / "worker-request.json"
        remote_output = REMOTE_STATE / "tasks" / request_id / "output"
        remote_cache = REMOTE_STATE / "chunk-cache"
        remote_archive = remote_output.parent / REMOTE_ARCHIVE_NAME
        make_task_dirs = f'''from pathlib import Path
Path({str(remote_request.parent)!r}).mkdir(parents=True, exist_ok=True)
Path({str(remote_output)!r}).mkdir(parents=True, exist_ok=True)
'''
        layout_result = self._cell(make_task_dirs)
        if layout_result.returncode != 0:
            raise ColabProvisioningError("Không tạo được thư mục request podcast trong Colab.")
        _upload(self.profile_alias, self.session, runner_path, str(remote_request))
        env = {
            "PODCAST_TTS_REQUEST": str(remote_request),
            "PODCAST_TTS_OUTPUT": str(remote_output),
            "PODCAST_TTS_REQUEST_ID": request_id,
            "PODCAST_TTS_REQUEST_HASH": request_hash,
            "PODCAST_TTS_CHUNK_CACHE": str(remote_cache),
        }
        result = self._cell(self._remote_exec_cell(), timeout=5400, env=env, stream=True)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "Colab TTS cell failed")[-3000:]
            self.tts._set_request_state(request_id, "ambiguous",
                                        error="CLI execution ended without a verified result archive. " + detail)
            raise PodcastTTSAmbiguous(f"Colab CLI TTS part {part_id} chưa có kết quả được xác minh; không gửi yêu cầu mới.")

        with tempfile.TemporaryDirectory(prefix="podcast_colab_cli_") as temp:
            local_archive = Path(temp) / REMOTE_ARCHIVE_NAME
            downloaded = _run(_profile_cli(self.profile_alias, "download", str(remote_archive),
                                           str(local_archive), "--session", self.session),
                              timeout=600, check=False)
            if downloaded.returncode != 0 or not local_archive.is_file():
                self.tts._set_request_state(request_id, "ambiguous",
                                            error=("Colab synthesis finished but the result archive could not be downloaded. "
                                                   + (downloaded.stderr or downloaded.stdout or "")))
                raise PodcastTTSAmbiguous("Colab đã chạy TTS nhưng chưa tải được kết quả; giữ nguyên request để đối chiếu.")
            try:
                self._import_archive(local_archive, request_id, request_hash, normalized, part_id)
            except Exception as exc:
                self.tts._set_request_state(request_id, "needs_attention", error=str(exc))
                raise

        chunks_out = self.tts._local_chunk_outputs(self.tts._read_manifest()["requests"][request_id])
        remote_summary = {"state": "succeeded", "runtime_id": runtime["runtime_id"],
                          "completed_chunks": len(chunks_out), "total_chunks": len(chunks_out),
                          "progress_percent": 100,
                          "chunks": [{"id": item.get("chunk_id"), "state": "succeeded",
                                      "wav_sha256": item.get("wav_sha256"),
                                      "duration_seconds": item.get("duration_seconds")}
                                     for item in chunks_out]}
        self.tts._set_request_state(request_id, "succeeded", remote=remote_summary)
        if progress_callback:
            progress_callback(self.tts.progress())
        return {"status": "success", "request_id": request_id, "part_id": part_id,
                "chunks": chunks_out, "runtime_id": runtime["runtime_id"]}


__all__ = ["PodcastColabCLIRunner"]
