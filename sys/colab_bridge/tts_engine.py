"""TTS execution worker for Google Colab environment.

Runs heavy neural TTS models with full GPU acceleration (16GB Tesla T4 VRAM)
and supports expressive acting directions (breaths, dramatic pauses, pacing)
and neural voice cloning (OmniVoice-8400h).
"""

import io
import base64
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import shutil
import tarfile
import threading
import tempfile
import time
import uuid
import wave
from typing import Any, Dict, List, Optional

logger = logging.getLogger("colab_bridge.tts")


class ColabTTSWorker:
    """Executes high-VRAM TTS and expressive audio direction on Colab."""

    def __init__(self, sys_dir: Optional[Path] = None):
        self.sys_dir = sys_dir or Path(__file__).resolve().parents[1]
        self.tts_worker_script = self.sys_dir / "tts_worker.py"
        self.omnivoice_script = self.sys_dir / "colab_bridge" / "omnivoice_worker.py"

    def synthesize_to_tarball(self, request_payload: Dict[str, Any]) -> bytes:
        """Run TTS synthesis with GPU acceleration, returning a tar.gz with all WAVs and metadata."""
        with tempfile.TemporaryDirectory(prefix="colab_tts_") as tmp_dir:
            out_dir = Path(tmp_dir)

            # 1. Prepare request file
            settings = request_payload.setdefault("settings", {})
            voice = settings.get("tts_voice", "Minh Quân Pro")

            # Check if requested voice is a cloned voice or OmniVoice engine
            is_omnivoice = (
                settings.get("tts_engine") == "omnivoice"
                or (self.sys_dir / "assets" / "voices" / voice).is_dir()
                or voice in ("van_vo", "vui_ve")
                or Path(f"/content/BetterBox-TTS/wavs/{voice}.wav").is_file()
            )

            request_file = out_dir / "request.json"
            request_file.write_text(json.dumps(request_payload, indent=2, ensure_ascii=False), encoding="utf-8")

            if is_omnivoice:
                # Use OmniVoice execution worker
                cmd = ["python3", str(self.omnivoice_script), str(request_file), str(out_dir)]
                logger.info("Executing OmniVoice TTS on Colab GPU: %s", " ".join(cmd))
            else:
                # Default settings for VieNeu on GPU
                settings.setdefault("tts_voice", "Minh Quân Pro")
                settings.setdefault("tts_temperature", 0.65)
                settings.setdefault("tts_top_p", 0.95)
                settings.setdefault("tts_device", "auto")
                settings.setdefault("tts_backend", "pytorch")
                settings.setdefault("tts_batch_size", 6)
                settings.setdefault("tts_gpu_dtype", "float32")

                # Rewrite request file with defaulted settings
                request_file.write_text(json.dumps(request_payload, indent=2, ensure_ascii=False), encoding="utf-8")

                # Find python executable with PyTorch & Vieneu
                py_candidates = [
                    self.sys_dir / ".venv-tts-gpu/bin/python",
                    self.sys_dir / ".venv-tts/bin/python",
                    self.sys_dir / ".venv/bin/python",
                    Path(os.sys.executable),
                ]
                python_bin = None
                for cand in py_candidates:
                    if cand.is_file():
                        python_bin = str(cand)
                        break
                if not python_bin:
                    python_bin = "python3"

                cmd = [python_bin, str(self.tts_worker_script), str(request_file), str(out_dir)]
                logger.info("Executing VieNeu TTS on Colab GPU: %s", " ".join(cmd))

            proc = subprocess.run(
                cmd,
                cwd=str(self.sys_dir),
                capture_output=True,
                text=True,
                timeout=1800,
            )
            log_file = out_dir / "tts.log"
            log_file.write_text(f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}", encoding="utf-8")

            if proc.returncode != 0:
                raise RuntimeError(f"TTS synthesis failed with code {proc.returncode}:\n{proc.stderr[-1000:]}")

            # 4. Pack output files into response tar.gz
            out_buf = io.BytesIO()
            with tarfile.open(fileobj=out_buf, mode="w:gz") as out_tar:
                for item in out_dir.iterdir():
                    if item.is_file() and item.name != "request.json":
                        out_tar.add(str(item), arcname=item.name)

            return out_buf.getvalue()


class PodcastTTSTaskStore:
    """Idempotent podcast TTS task store for a single live Colab runtime."""

    REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,159}$")
    CHUNK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
    SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
    PODCAST_ALIASES = {"podcas", "podcast"}
    CANONICAL_PODCAST_PROFILE = "wynn_podcast_ea9b0og4_21s_20260928"
    REQUIRED_MODEL = "kjanh/KhanhTTS-OmniVoice"
    REQUIRED_ENGINE = "OmniVoice-8400h"
    RUNNER_VERSION = "podcast-omnivoice-v1"
    MAX_ATTEMPTS = 3

    def __init__(self, root: Optional[Path] = None):
        configured = os.environ.get("PODCAST_TTS_TASK_DIR")
        self.root = Path(root or configured or "/content/video-pilot-podcast-tts").resolve()
        self.tasks_dir = self.root / "tasks"
        self.chunk_cache_dir = self.root / "chunk-cache"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._gpu_lock = threading.Lock()
        self._active_runs = set()
        self._worker = ColabTTSWorker()
        self.runtime_id = self._load_or_create_runtime_id()
        self._recover_tasks()

    @staticmethod
    def canonical_json(value: Any) -> bytes:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _load_or_create_runtime_id(self) -> str:
        path = self.root / "runtime.json"
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                value = data.get("runtime_id")
                if isinstance(value, str) and value:
                    return value
            except Exception:
                pass
        value = uuid.uuid4().hex
        self._atomic_json(path, {"runtime_id": value, "created_at": time.time()})
        return value

    @staticmethod
    def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
        temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp, path)

    @staticmethod
    def _atomic_bytes(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
        temp.write_bytes(content)
        os.replace(temp, path)

    def _task_dir(self, request_id: str) -> Path:
        if not self.REQUEST_ID_RE.fullmatch(request_id):
            raise ValueError("Invalid podcast TTS request_id")
        return self.tasks_dir / request_id

    def _read_record(self, request_id: str) -> Optional[Dict[str, Any]]:
        path = self._task_dir(request_id) / "task.json"
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Podcast TTS task record is unreadable: {request_id}") from exc

    def _write_record(self, request_id: str, record: Dict[str, Any]) -> None:
        self._atomic_json(self._task_dir(request_id) / "task.json", record)

    def _runner_alive(self, record: Dict[str, Any]) -> bool:
        pid = record.get("runner_pid")
        request_id = record.get("request_id", "")
        if not isinstance(pid, int) or pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        try:
            proc_root = Path(f"/proc/{pid}")
            command = (proc_root / "cmdline").read_bytes()
            environment = (proc_root / "environ").read_bytes()
            return b"remote_tts_runner.py" in command and f"PODCAST_TTS_REQUEST_ID={request_id}".encode() in environment
        except OSError:
            # If identity cannot be checked, do not risk a duplicate worker.
            return True

    def _recover_tasks(self) -> None:
        queued: List[str] = []
        with self._lock:
            for folder in self.tasks_dir.iterdir():
                if not folder.is_dir() or not self.REQUEST_ID_RE.fullmatch(folder.name):
                    continue
                record = self._read_record(folder.name)
                if not record:
                    continue
                if record.get("state") in ("running", "starting"):
                    if self._runner_alive(record):
                        continue
                    if self._all_chunks_complete(folder, record):
                        result_path = self._archive_result(folder)
                        record.update({"state": "succeeded", "result_sha256": self._sha256(result_path.read_bytes()),
                                       "result_bytes": result_path.stat().st_size, "updated_at": time.time()})
                    elif record.get("runner_pid"):
                        record.update({"state": "interrupted", "error": "Colab worker stopped; saved chunks are retained and missing chunks can resume.",
                                       "updated_at": time.time()})
                    else:
                        record.update({"state": "ambiguous", "error": "Worker start outcome is unknown; refusing a duplicate submission.",
                                       "updated_at": time.time()})
                    self._write_record(folder.name, record)
                elif record.get("state") == "queued":
                    queued.append(folder.name)
        for request_id in queued:
            self._launch(request_id)

    def runtime_status(self) -> Dict[str, Any]:
        return {"runtime_id": self.runtime_id, "task_storage": "runtime_local"}

    def validate_request(self, request_id: str, request_hash: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.REQUEST_ID_RE.fullmatch(request_id):
            raise ValueError("Invalid podcast TTS request_id")
        if not self.SHA256_RE.fullmatch(request_hash):
            raise ValueError("Invalid podcast TTS request_hash")
        if self._sha256(self.canonical_json(payload)) != request_hash:
            raise ValueError("Podcast TTS request_hash does not match payload")
        settings, scenes, profile = payload.get("settings"), payload.get("scenes"), payload.get("podcast_profile")
        if not isinstance(settings, dict) or settings.get("tts_engine") != "omnivoice":
            raise ValueError("Podcast TTS requires the OmniVoice Colab engine")
        if not isinstance(scenes, list) or not 1 <= len(scenes) <= 64:
            raise ValueError("A podcast part must contain between 1 and 64 chunks")
        info = self._validate_profile_bundle(profile, settings.get("tts_voice"))
        try:
            speed, pitch = float(settings.get("tts_speed", 1.0)), float(settings.get("pitch_shift", 1.0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Podcast TTS speed and pitch settings must be numeric") from exc
        if not (0.5 <= speed <= 2.0 and 0.5 <= pitch <= 2.0):
            raise ValueError("Podcast TTS speed or pitch setting is outside the supported range")
        seen = set()
        for scene in scenes:
            if not isinstance(scene, dict):
                raise ValueError("Podcast TTS scene must be an object")
            scene_id, text = scene.get("id"), scene.get("narration")
            if not isinstance(scene_id, str) or not self.CHUNK_ID_RE.fullmatch(scene_id) or scene_id in seen:
                raise ValueError("Podcast TTS chunk ids must be unique safe identifiers")
            if not isinstance(text, str) or not text.strip() or len(text) > 100_000:
                raise ValueError("Podcast TTS chunk text is empty or too large")
            seen.add(scene_id)
            expected = self._sha256(self.canonical_json({
                "text": text.strip(), "profile_fingerprint": info["profile_fingerprint"],
                "model": self.REQUIRED_MODEL, "speed": speed, "pitch_shift": pitch,
                "runner_version": self.RUNNER_VERSION,
            }))
            if scene.get("chunk_hash") != expected:
                raise ValueError(f"Podcast TTS chunk hash mismatch for {scene_id}")
        return info

    def _validate_profile_bundle(self, profile: Any, requested_voice_id: Any) -> Dict[str, Any]:
        if not isinstance(profile, dict):
            raise ValueError("Podcast TTS requires a verified podcast profile bundle")
        voice_id = profile.get("voice_id")
        if (not isinstance(voice_id, str) or not self.REQUEST_ID_RE.fullmatch(voice_id) or
                requested_voice_id != voice_id or voice_id != self.CANONICAL_PODCAST_PROFILE):
            raise ValueError("Invalid or mismatched podcast voice profile id")
        config = profile.get("voice_config")
        if not isinstance(config, dict):
            raise ValueError("Podcast voice_config is missing")
        aliases = {x.casefold() for x in config.get("aliases", []) if isinstance(x, str)}
        approval = config.get("user_approval")
        name = config.get("name")
        if not aliases.intersection(self.PODCAST_ALIASES) or not isinstance(approval, dict) or approval.get("approved") is not True:
            raise ValueError("Voice profile is not approved and podcast-labelled")
        if config.get("voice_id") != voice_id or not isinstance(name, str) or name.casefold() != "podcast":
            raise ValueError("Voice profile identity does not match podcast configuration")
        if config.get("engine") != self.REQUIRED_ENGINE or config.get("model") != self.REQUIRED_MODEL:
            raise ValueError("Podcast voice profile uses an unsupported model or engine")
        files = config.get("files")
        if not isinstance(files, dict):
            raise ValueError("Podcast profile file manifest is missing")
        wav_name, text_name = files.get("reference_wav"), files.get("transcript_txt")
        if not all(isinstance(x, str) and x == Path(x).name and "\\" not in x for x in (wav_name, text_name)):
            raise ValueError("Podcast profile filenames must be plain filenames")
        wav_b64, transcript = profile.get("reference_wav_base64"), profile.get("transcript")
        if not isinstance(wav_b64, str) or not isinstance(transcript, str) or not transcript.strip():
            raise ValueError("Podcast profile reference audio or transcript is missing")
        try:
            wav_bytes = base64.b64decode(wav_b64, validate=True)
        except Exception as exc:
            raise ValueError("Podcast profile audio is not valid base64") from exc
        if not wav_bytes or len(wav_bytes) > 20_000_000:
            raise ValueError("Podcast profile audio size is invalid")
        wav_hash, text_hash = profile.get("reference_wav_sha256"), profile.get("transcript_sha256")
        if self._sha256(wav_bytes) != wav_hash or self._sha256(transcript.encode("utf-8")) != text_hash:
            raise ValueError("Podcast profile reference checksum mismatch")
        fingerprint = self._sha256(self.canonical_json({"voice_config": config, "reference_wav_sha256": wav_hash,
                                                        "transcript_sha256": text_hash}))
        if profile.get("profile_fingerprint") != fingerprint:
            raise ValueError("Podcast profile fingerprint mismatch")
        return {"voice_id": voice_id, "config": config, "wav_name": wav_name, "text_name": text_name,
                "wav_bytes": wav_bytes, "transcript": transcript, "profile_fingerprint": fingerprint}

    def submit(self, request_id: str, request_hash: str, payload: Dict[str, Any], resume: bool = False) -> Dict[str, Any]:
        self.validate_request(request_id, request_hash, payload)
        task_dir = self._task_dir(request_id)
        launch = False
        with self._lock:
            record = self._read_record(request_id)
            if record:
                if record.get("request_hash") != request_hash:
                    raise FileExistsError("request_id already belongs to a different request_hash")
                if record.get("runtime_id") != self.runtime_id:
                    raise RuntimeError("Podcast TTS request belongs to another Colab runtime")
                state = record.get("state")
                if state in ("partial_failed", "interrupted") and resume:
                    if self._runner_alive(record):
                        return self._public_status(record, task_dir)
                    if int(record.get("attempts", 1)) >= self.MAX_ATTEMPTS:
                        record.update({"state": "failed", "error": "Podcast part exhausted initial generation plus two retries.",
                                       "updated_at": time.time()})
                        self._write_record(request_id, record)
                        return self._public_status(record, task_dir)
                    record["attempts"] = int(record.get("attempts", 1)) + 1
                    record.update({"state": "queued", "error": None, "updated_at": time.time()})
                    self._write_record(request_id, record)
                    launch = True
                else:
                    return self._public_status(record, task_dir)
            else:
                task_dir.mkdir(parents=True, exist_ok=False)
                self._atomic_json(task_dir / "request.json", payload)
                now = time.time()
                record = {"request_id": request_id, "request_hash": request_hash, "runtime_id": self.runtime_id,
                          "state": "queued", "attempts": 1, "created_at": now, "updated_at": now,
                          "expected_chunks": [scene["id"] for scene in payload["scenes"]]}
                self._write_record(request_id, record)
                launch = True
        if launch:
            self._launch(request_id)
        return self.status(request_id) or {}

    def _launch(self, request_id: str) -> None:
        threading.Thread(target=self._run_task, args=(request_id,), name=f"podcast-tts-{request_id[:24]}", daemon=True).start()

    def _run_task(self, request_id: str) -> None:
        with self._gpu_lock:
            task_dir = self._task_dir(request_id)
            with self._lock:
                record = self._read_record(request_id)
                if not record or record.get("state") != "queued":
                    return
                self._active_runs.add(request_id)
                record.update({"state": "starting", "updated_at": time.time()})
                self._write_record(request_id, record)
            try:
                payload = json.loads((task_dir / "request.json").read_text(encoding="utf-8"))
                profile = self._validate_profile_bundle(payload.get("podcast_profile"), payload.get("settings", {}).get("tts_voice"))
                self._stage_profile(profile)
                runner_request = {key: value for key, value in payload.items() if key != "podcast_profile"}
                runner_request["profile_fingerprint"] = profile["profile_fingerprint"]
                runner_request["request_id"] = request_id
                runner_request["request_hash"] = record["request_hash"]
                request_path = task_dir / "worker-request.json"
                self._atomic_json(request_path, runner_request)
                output_dir = task_dir / "output"
                output_dir.mkdir(parents=True, exist_ok=True)
                runner = self._worker.sys_dir / "podcast" / "remote_tts_runner.py"
                if not runner.is_file():
                    raise FileNotFoundError(f"Podcast Colab runner not installed: {runner}")
                env = os.environ.copy()
                env.pop("COLAB_AUTH_TOKEN", None)
                env.update({"PODCAST_TTS_REQUEST": str(request_path), "PODCAST_TTS_OUTPUT": str(output_dir),
                            "PODCAST_TTS_REQUEST_ID": request_id, "PODCAST_TTS_REQUEST_HASH": record["request_hash"],
                            "PODCAST_TTS_CHUNK_CACHE": str(self.chunk_cache_dir)})
                process = subprocess.Popen([os.sys.executable, str(runner)], cwd=str(self._worker.sys_dir), env=env,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                with self._lock:
                    record = self._read_record(request_id) or record
                    record.update({"state": "running", "runner_pid": process.pid, "updated_at": time.time()})
                    self._write_record(request_id, record)
                log_path = task_dir / "runner.log"
                with log_path.open("a", encoding="utf-8") as log:
                    for line in process.stdout or ():
                        log.write(line)
                        log.flush()
                return_code = process.wait()
                if log_path.is_file():
                    output_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(log_path, output_dir / "tts.log")
                if return_code == 0 and self._all_chunks_complete(task_dir, record):
                    result_path = self._archive_result(task_dir)
                    final = {"state": "succeeded", "result_sha256": self._sha256(result_path.read_bytes()),
                             "result_bytes": result_path.stat().st_size, "updated_at": time.time(), "error": None}
                else:
                    detail = ""
                    if log_path.is_file():
                        detail = "\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-30:])
                    final = {"state": "partial_failed", "error": (detail or f"Podcast runner exited with code {return_code}")[-4000:],
                             "updated_at": time.time()}
            except Exception as exc:
                logger.exception("Podcast TTS task %s failed", request_id)
                final = {"state": "partial_failed", "error": f"{type(exc).__name__}: {exc}"[:4000], "updated_at": time.time()}
            with self._lock:
                record = self._read_record(request_id) or {"request_id": request_id}
                record.update(final)
                self._write_record(request_id, record)
                self._active_runs.discard(request_id)
                if final.get("state") == "succeeded":
                    try:
                        (task_dir / "request.json").unlink()
                    except FileNotFoundError:
                        pass

    def _stage_profile(self, profile: Dict[str, Any]) -> None:
        voice_dir = self._worker.sys_dir / "assets" / "voices" / profile["voice_id"]
        voice_dir.mkdir(parents=True, exist_ok=True)
        entries = {profile["wav_name"]: profile["wav_bytes"], profile["text_name"]: profile["transcript"].encode("utf-8"),
                   "voice_config.json": json.dumps(profile["config"], indent=2, ensure_ascii=False).encode("utf-8")}
        for filename, content in entries.items():
            self._atomic_bytes(voice_dir / filename, content)

    def _chunk_progress(self, task_dir: Path, record: Dict[str, Any]) -> Dict[str, Any]:
        progress_path = task_dir / "output" / "tts-progress.json"
        try:
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
        except Exception:
            progress = {"chunks": []}
        chunks = progress.get("chunks", []) if isinstance(progress, dict) else []
        by_id = {item.get("id"): item for item in chunks if isinstance(item, dict)}
        expected = record.get("expected_chunks", [])
        normalized = []
        for chunk_id in expected:
            item = by_id.get(chunk_id, {"id": chunk_id, "state": "pending"})
            normalized.append(item)
        complete = sum(item.get("state") == "succeeded" for item in normalized)
        return {"chunks": normalized, "completed_chunks": complete, "total_chunks": len(normalized),
                "progress_percent": round(100 * complete / len(normalized)) if normalized else 0}

    def _all_chunks_complete(self, task_dir: Path, record: Dict[str, Any]) -> bool:
        progress = self._chunk_progress(task_dir, record)
        if not progress["total_chunks"] or progress["completed_chunks"] != progress["total_chunks"]:
            return False
        for item in progress["chunks"]:
            wav = task_dir / "output" / item.get("path", "")
            meta = task_dir / "output" / "chunk_meta" / f"{item['id']}.json"
            if not wav.is_file() or not meta.is_file():
                return False
            try:
                meta_json = json.loads(meta.read_text(encoding="utf-8"))
                if self._sha256(wav.read_bytes()) != meta_json.get("wav_sha256"):
                    return False
            except Exception:
                return False
        return True

    def _archive_result(self, task_dir: Path) -> Path:
        output_dir = task_dir / "output"
        result = output_dir / "tts-result.json"
        if not result.is_file():
            request_path = task_dir / "worker-request.json"
            if not request_path.is_file():
                raise RuntimeError("Podcast runner did not create tts-result.json")
            request = json.loads(request_path.read_text(encoding="utf-8"))
            segments = []
            for scene in request.get("scenes", []):
                scene_id = scene["id"]
                meta_path = output_dir / "chunk_meta" / f"{scene_id}.json"
                if not meta_path.is_file():
                    raise RuntimeError(f"Podcast chunk metadata is missing: {scene_id}")
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                segments.append({"scene_id": scene_id, "text": scene["narration"],
                                 "path": f"chunks/{scene_id}.wav", "chunk_hash": scene["chunk_hash"],
                                 "duration_seconds": metadata["duration_seconds"]})
            self._atomic_json(result, {"request_id": request.get("request_id"),
                                       "request_hash": request.get("request_hash"),
                                       "voice": request.get("settings", {}).get("tts_voice"),
                                       "profile_fingerprint": request.get("profile_fingerprint"),
                                       "segments": segments})
        destination = task_dir / "result.tar.gz"
        temp = task_dir / f"result.{uuid.uuid4().hex}.tmp"
        with tarfile.open(temp, mode="w:gz") as tar:
            for path in output_dir.rglob("*"):
                if path.is_file():
                    tar.add(path, arcname=path.relative_to(output_dir).as_posix())
        os.replace(temp, destination)
        return destination

    def status(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._read_record(request_id)
            if not record:
                return None
            if (record.get("state") in ("running", "starting") and request_id not in self._active_runs
                    and not self._runner_alive(record)):
                if record.get("state") == "starting" and not record.get("runner_pid") and time.time() - record.get("updated_at", 0) < 30:
                    return self._public_status(record, self._task_dir(request_id))
                task_dir = self._task_dir(request_id)
                if self._all_chunks_complete(task_dir, record):
                    result_path = self._archive_result(task_dir)
                    record.update({"state": "succeeded", "result_sha256": self._sha256(result_path.read_bytes()),
                                   "result_bytes": result_path.stat().st_size, "updated_at": time.time(), "error": None})
                elif record.get("runner_pid"):
                    record.update({"state": "interrupted", "error": "Colab worker stopped; saved chunks are retained and missing chunks can resume.",
                                   "updated_at": time.time()})
                else:
                    record.update({"state": "ambiguous", "error": "Worker start outcome is unknown; refusing a duplicate submission.",
                                   "updated_at": time.time()})
                self._write_record(request_id, record)
            return self._public_status(record, self._task_dir(request_id))

    def _public_status(self, record: Dict[str, Any], task_dir: Path) -> Dict[str, Any]:
        keys = ("request_id", "request_hash", "runtime_id", "state", "attempts", "created_at", "updated_at", "result_sha256",
                "result_bytes", "error")
        result = {key: record[key] for key in keys if key in record}
        result.update(self._chunk_progress(task_dir, record))
        return result

    def result_path(self, request_id: str) -> Optional[Path]:
        state = self.status(request_id)
        if not state or state.get("state") != "succeeded":
            return None
        result = self._task_dir(request_id) / "result.tar.gz"
        if not result.is_file() or not result.stat().st_size:
            return None
        expected = state.get("result_sha256")
        if expected and self._sha256(result.read_bytes()) != expected:
            raise RuntimeError("Persisted podcast TTS result failed checksum verification")
        return result
