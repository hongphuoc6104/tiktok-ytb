"""Colab-only, resumable TTS primitives for long-form Vietnamese podcasts."""

from __future__ import annotations

import base64
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import uuid
import wave
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence

from colab_bridge.config import ColabConfig


CANONICAL_PROFILE_ID = "wynn_podcast_ea9b0og4_21s_20260928"
PODCAST_ALIASES = {"podcas", "podcast"}
REQUIRED_MODEL = "kjanh/KhanhTTS-OmniVoice"
REQUIRED_ENGINE = "OmniVoice-8400h"
RUNNER_VERSION = "podcast-omnivoice-v1"
DEFAULT_PODCAST_SPEED = 0.90
MAX_PART_ATTEMPTS = 3  # Initial generation plus at most two retakes.
CHUNK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
EPISODE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# A fixed 100+ token Vietnamese passage gives a more stable pacing estimate.
CALIBRATION_TEXT = (
    "Bây giờ, khi những việc trong ngày đã tạm khép lại, bạn có thể cho mình một khoảng nghỉ thật nhỏ. "
    "Không cần vội nghĩ xem ngày mai ra sao, cũng không cần tự nhắc mình phải hoàn thành thêm điều gì. "
    "Hãy cảm nhận nơi cơ thể đang được nâng đỡ, để đôi vai hạ xuống, hai bàn tay thôi nắm chặt, "
    "và hơi thở trở về nhịp bình thường. Nếu trong đầu còn vài suy nghĩ, hãy để chúng đi ngang qua "
    "như những đám mây ngoài khung cửa. Mỗi lần thở ra, thử buông bớt một chút căng thẳng; "
    "không cần cố làm mọi thứ biến mất. Bạn đang có mặt ở đây, trong một khoảnh khắc yên. "
    "Chỉ cần lắng nghe giọng nói nhẹ nhàng và nghỉ ngơi theo cách riêng của mình."
)


class CalibrationCacheMiss(RuntimeError):
    """No verified calibration for the current voice/engine signature."""


class PodcastTTSError(RuntimeError):
    """Base error for podcast Colab TTS operations."""


class PodcastTTSUnavailable(PodcastTTSError):
    """Colab is disabled, unhealthy, unauthenticated, or lacks its GPU."""


class PodcastTTSAmbiguous(PodcastTTSError):
    """The remote request may be running; never resubmit on a new runtime."""


class PodcastTTSRemoteFailure(PodcastTTSError):
    """Colab explicitly reported a terminal synthesis failure."""


class PodcastTTSProtocolError(PodcastTTSError):
    """The remote worker returned an invalid or inconsistent response."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + f".{uuid.uuid4().hex}.tmp")
    shutil.copyfile(source, temp)
    os.replace(temp, destination)


@dataclass(frozen=True)
class PodcastChunk:
    """One independently reusable TTS segment inside a podcast part."""

    chunk_id: str
    text: str


@dataclass(frozen=True)
class VerifiedVoiceProfile:
    voice_id: str
    alias: str
    voice_config: Dict[str, Any]
    reference_wav: bytes
    transcript: str
    reference_wav_sha256: str
    transcript_sha256: str
    fingerprint: str

    def bundle(self) -> Dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "voice_config": self.voice_config,
            "reference_wav_base64": base64.b64encode(self.reference_wav).decode("ascii"),
            "transcript": self.transcript,
            "reference_wav_sha256": self.reference_wav_sha256,
            "transcript_sha256": self.transcript_sha256,
            "profile_fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class CalibrationResult:
    estimated_wpm: float
    token_count: int
    duration_seconds: float
    wav_path: str
    cache_hit: bool
    profile_fingerprint: str
    model: str
    speed: float
    sample_sha256: str
    sample_text: str
    cache_key: str


def resolve_podcast_profile(sys_root: Path, alias: str = "podcas") -> VerifiedVoiceProfile:
    """Resolve only approved podcast-labelled profiles and reject ambiguity."""
    normalized_alias = alias.casefold().strip()
    if normalized_alias not in PODCAST_ALIASES and alias != CANONICAL_PROFILE_ID:
        raise PodcastTTSError(f"Unsupported podcast voice alias: {alias}")
    voices_dir = Path(sys_root) / "assets" / "voices"
    candidates: List[tuple[Path, Dict[str, Any]]] = []
    if normalized_alias == CANONICAL_PROFILE_ID.casefold() or alias == CANONICAL_PROFILE_ID:
        profile_dirs = [voices_dir / CANONICAL_PROFILE_ID]
    else:
        # Scan configs so future approved podcast-labelled profiles can be
        # recognized, but never guess when two satisfy the same alias.
        profile_dirs = sorted(path.parent for path in voices_dir.glob("*/voice_config.json"))
    for profile_dir in profile_dirs:
        config_path = profile_dir / "voice_config.json"
        if not config_path.is_file():
            continue
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise PodcastTTSError(f"Voice profile config is unreadable: {profile_dir.name}") from exc
        profile_aliases = {item.casefold() for item in config.get("aliases", []) if isinstance(item, str)}
        approval = config.get("user_approval")
        alias_match = normalized_alias in profile_aliases or (profile_dir.name == CANONICAL_PROFILE_ID and
                                                               normalized_alias == CANONICAL_PROFILE_ID.casefold())
        profile_name = config.get("name")
        if (alias_match and isinstance(approval, dict) and approval.get("approved") is True
                and isinstance(profile_name, str) and profile_name.casefold() == "podcast" and config.get("engine") == REQUIRED_ENGINE
                and config.get("model") == REQUIRED_MODEL and config.get("voice_id") == profile_dir.name):
            candidates.append((profile_dir, config))
    if len(candidates) != 1:
        raise PodcastTTSError(f"Expected one approved podcast profile for alias '{alias}', found {len(candidates)}")
    profile_dir, config = candidates[0]
    if profile_dir.name != CANONICAL_PROFILE_ID:
        raise PodcastTTSError(f"Only the verified canonical podcast profile is enabled: {CANONICAL_PROFILE_ID}")
    files = config.get("files") or {}
    wav_name, transcript_name = files.get("reference_wav"), files.get("transcript_txt")
    for filename in (wav_name, transcript_name):
        if not isinstance(filename, str) or filename != Path(filename).name or "\\" in filename:
            raise PodcastTTSError("Podcast profile contains an unsafe reference filename")
    wav_path, transcript_path = profile_dir / wav_name, profile_dir / transcript_name
    if not wav_path.is_file() or not transcript_path.is_file():
        raise PodcastTTSError("Approved podcast profile is missing its reference WAV or transcript")
    wav_bytes, transcript_bytes = wav_path.read_bytes(), transcript_path.read_bytes()
    transcript = transcript_bytes.decode("utf-8").strip()
    if not transcript or not wav_bytes:
        raise PodcastTTSError("Approved podcast profile reference is empty")
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
            if (wav.getnchannels() != int(config.get("channels", 1)) or
                    wav.getframerate() != int(config.get("sample_rate", 24000)) or
                    wav.getsampwidth() != 2 or wav.getnframes() <= 0):
                raise PodcastTTSError("Podcast reference WAV does not match the declared 24 kHz mono PCM16 format")
    except wave.Error as exc:
        raise PodcastTTSError("Podcast reference WAV is invalid") from exc
    audio_hash, transcript_hash = sha256(wav_bytes), sha256(transcript.encode("utf-8"))
    fingerprint = sha256(canonical_json({"voice_config": config, "reference_wav_sha256": audio_hash,
                                         "transcript_sha256": transcript_hash}))
    return VerifiedVoiceProfile(config["voice_id"], normalized_alias, config, wav_bytes, transcript,
                                audio_hash, transcript_hash, fingerprint)


def load_podcast_colab_config(sys_root: Path) -> ColabConfig:
    """Load only the podcast worker endpoint/token, never global bridge flags."""
    state_path = Path(sys_root) / ".state" / "podcast-colab.json"
    if not state_path.is_file():
        return ColabConfig(enabled=False, tasks={"expressive_tts": True})
    try:
        mode = state_path.stat().st_mode & 0o777
        if mode & 0o077:
            raise PodcastTTSUnavailable("Podcast Colab state must be private (mode 0600)")
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except PodcastTTSUnavailable:
        raise
    except Exception as exc:
        raise PodcastTTSUnavailable("Podcast Colab endpoint state is unreadable") from exc
    endpoint, token = state.get("endpoint"), state.get("auth_token")
    if not isinstance(endpoint, str) or not endpoint.startswith("https://") or not isinstance(token, str) or len(token) < 32:
        return ColabConfig(enabled=False, endpoint=endpoint or "http://localhost:8088",
                           auth_token=token or "", tasks={"expressive_tts": True})
    return ColabConfig(enabled=True, endpoint=endpoint, auth_token=token, timeout_tts=2400,
                       timeout_health=5.0, fallback_to_local=False, tasks={"expressive_tts": True})


class PodcastColabTTS:
    """Callable Colab-only TTS interface for podcast coordinators.

    A part is submitted as one model process containing multiple stable chunk
    IDs. The Colab runner saves each completed chunk immediately, so a part
    retry reloads the model once and generates only missing chunks.
    """

    def __init__(
        self,
        episode_id: str,
        run_dir: Path,
        sys_root: Optional[Path] = None,
        profile_alias: str = "podcas",
        config: Optional[ColabConfig] = None,
        status_poll_seconds: float = 5.0,
        wait_timeout_seconds: float = 14400.0,
        keepalive_interval_seconds: float = 60.0,
        calibration_cache_dir: Optional[Path] = None,
    ):
        if not EPISODE_ID_RE.fullmatch(episode_id):
            raise ValueError("episode_id must be a safe stable identifier")
        self.episode_id = episode_id
        self.sys_root = Path(sys_root or Path(__file__).resolve().parents[1]).resolve()
        self.run_dir = Path(run_dir).resolve()
        self.tts_dir = self.run_dir / "tts"
        self.manifest_path = self.tts_dir / "manifest.json"
        self.lock_path = self.tts_dir / ".manifest.lock"
        self.config = config or load_podcast_colab_config(self.sys_root)
        self.profile_alias = profile_alias
        self._profile: Optional[VerifiedVoiceProfile] = None
        self.status_poll_seconds = max(0.25, float(status_poll_seconds))
        self.wait_timeout_seconds = max(1.0, float(wait_timeout_seconds))
        self.keepalive_interval_seconds = max(15.0, float(keepalive_interval_seconds))
        self.calibration_cache_dir = Path(calibration_cache_dir or (self.sys_root / ".cache" / "podcast-tts-calibration"))

    @property
    def profile(self) -> VerifiedVoiceProfile:
        if self._profile is None:
            self._profile = resolve_podcast_profile(self.sys_root, self.profile_alias)
        return self._profile

    def _ensure_config(self) -> None:
        if not self.config.enabled or not self.config.is_task_enabled("expressive_tts"):
            raise PodcastTTSUnavailable("Colab expressive_tts is disabled; podcast TTS has no local fallback")
        if not self.config.auth_token:
            raise PodcastTTSUnavailable("COLAB_AUTH_TOKEN is required for the podcast TTS task API")
        endpoint = self.config.endpoint.rstrip("/")
        if not endpoint.startswith("https://") and not endpoint.startswith(("http://localhost", "http://127.0.0.1")):
            raise PodcastTTSUnavailable("Podcast TTS requires HTTPS unless the worker is on loopback")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.config.auth_token}", "Content-Type": "application/json"}

    def _http(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None,
              timeout: Optional[float] = None) -> tuple[int, bytes, Mapping[str, str]]:
        self._ensure_config()
        body = canonical_json(payload) if payload is not None else None
        headers = self._headers()
        if body is not None:
            headers["Content-Length"] = str(len(body))
        request = urllib.request.Request(self.config.endpoint.rstrip("/") + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout or self.config.timeout_health) as response:
                return response.status, response.read(), response.headers
        except urllib.error.HTTPError as exc:
            detail = exc.read()
            try:
                message = json.loads(detail.decode("utf-8"))
            except Exception:
                message = detail[:1000].decode("utf-8", errors="replace")
            if exc.code in (408, 429) or exc.code >= 500:
                raise PodcastTTSAmbiguous(
                    f"Colab returned HTTP {exc.code}; the task outcome must be reconciled before any retry") from exc
            raise _RemoteHTTPError(exc.code, message) from exc
        except Exception as exc:
            raise PodcastTTSAmbiguous(f"Colab connection outcome is unknown: {type(exc).__name__}: {exc}") from exc

    def _runtime(self) -> str:
        self._ensure_config()
        endpoint = self.config.endpoint.rstrip("/")
        request = urllib.request.Request(endpoint + "/health", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_health) as response:
                health = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise PodcastTTSUnavailable(f"Colab health check failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(health, dict):
            raise PodcastTTSUnavailable("Colab returned an invalid health response")
        gpu = health.get("gpu")
        if health.get("status") != "ok" or not isinstance(gpu, dict) or gpu.get("available") is not True:
            raise PodcastTTSUnavailable("Colab worker is not healthy with a CUDA GPU; no local fallback is available")
        try:
            _status, raw, _headers = self._http("GET", "/api/v1/podcast/tts/runtime")
            data = json.loads(raw.decode("utf-8"))
        except _RemoteHTTPError as exc:
            raise PodcastTTSUnavailable(f"Podcast Colab task API is unavailable: {exc.message}") from exc
        runtime_id = data.get("runtime_id") if isinstance(data, dict) else None
        if not isinstance(runtime_id, str) or not runtime_id:
            raise PodcastTTSProtocolError("Colab did not identify the current runtime")
        with self._manifest_lock():
            manifest = self._read_manifest_unlocked()
            previous = manifest.get("last_runtime_id")
            if previous and previous != runtime_id:
                manifest.setdefault("runtime_changes", []).append({"from": previous, "to": runtime_id, "at": time.time()})
            manifest["last_runtime_id"] = runtime_id
            self._write_manifest_unlocked(manifest)
        return runtime_id

    @contextmanager
    def _manifest_lock(self):
        self.tts_dir.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _read_manifest_unlocked(self) -> Dict[str, Any]:
        if not self.manifest_path.is_file():
            return {"schema_version": 1, "episode_id": self.episode_id, "parts": {}, "requests": {}, "chunks": {}}
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise PodcastTTSError("Podcast TTS manifest is unreadable; refusing to overwrite it") from exc
        if manifest.get("episode_id") != self.episode_id or manifest.get("schema_version") != 1:
            raise PodcastTTSError("Podcast TTS manifest belongs to another episode or schema")
        return manifest

    def _write_manifest_unlocked(self, manifest: Dict[str, Any]) -> None:
        _atomic_json(self.manifest_path, manifest)

    def _update(self, mutator: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
        with self._manifest_lock():
            manifest = self._read_manifest_unlocked()
            mutator(manifest)
            manifest["updated_at"] = time.time()
            self._write_manifest_unlocked(manifest)
            return manifest

    def _store_profile_bundle(self, profile: VerifiedVoiceProfile) -> str:
        relative = f"profiles/{profile.fingerprint}.json"
        path = self.tts_dir / relative
        if not path.is_file():
            _atomic_json(path, profile.bundle())
        else:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("profile_fingerprint") != profile.fingerprint:
                raise PodcastTTSError("Cached podcast voice profile bundle does not match its fingerprint")
        return relative

    def _chunk_hash(self, text: str, speed: float, pitch_shift: float, profile: VerifiedVoiceProfile) -> str:
        return sha256(canonical_json({"text": text.strip(), "profile_fingerprint": profile.fingerprint,
                                      "model": profile.voice_config["model"], "speed": speed,
                                      "pitch_shift": pitch_shift, "runner_version": RUNNER_VERSION}))

    def generation_signature(self, speed: Optional[float] = None,
                             pitch_shift: Optional[float] = None) -> Dict[str, Any]:
        """Return the frozen settings/profile fields shared by all chunks."""
        profile = self.profile
        params = profile.voice_config.get("recommended_params", {})
        resolved_speed = float(speed if speed is not None else DEFAULT_PODCAST_SPEED)
        resolved_pitch = float(pitch_shift if pitch_shift is not None else params.get("pitch_shift", 1.0))
        return {"profile_id": profile.voice_id, "profile_fingerprint": profile.fingerprint,
                "profile_wav_sha256": profile.reference_wav_sha256,
                "profile_transcript_sha256": profile.transcript_sha256,
                "model": profile.voice_config["model"], "runner_version": RUNNER_VERSION,
                "speed": resolved_speed, "pitch_shift": resolved_pitch,
                "settings": {"tts_engine": "omnivoice", "tts_voice": profile.voice_id,
                             "tts_speed": resolved_speed, "pitch_shift": resolved_pitch}}

    def chunk_signature(self, text: str, speed: Optional[float] = None,
                        pitch_shift: Optional[float] = None) -> Dict[str, Any]:
        """Return the exact content-dependent cache signature sent to Colab."""
        generation = self.generation_signature(speed, pitch_shift)
        fields = {"text": text.strip(), "profile_fingerprint": generation["profile_fingerprint"],
                  "model": generation["model"], "speed": generation["speed"],
                  "pitch_shift": generation["pitch_shift"], "runner_version": RUNNER_VERSION}
        return {**generation, "text": text.strip(), "chunk_hash": sha256(canonical_json(fields))}

    def _make_payload(self, chunks: Sequence[PodcastChunk], speed: float, pitch_shift: float,
                      profile: VerifiedVoiceProfile) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        normalized: List[Dict[str, Any]] = []
        seen = set()
        for chunk in chunks:
            chunk_id = chunk.chunk_id.strip()
            text = chunk.text.strip()
            if not CHUNK_ID_RE.fullmatch(chunk_id) or chunk_id in seen:
                raise ValueError(f"Chunk id is invalid or repeated: {chunk_id}")
            if not text:
                raise ValueError(f"Chunk text is empty: {chunk_id}")
            seen.add(chunk_id)
            normalized.append({"id": chunk_id, "narration": text,
                               "chunk_hash": self._chunk_hash(text, speed, pitch_shift, profile)})
        if not normalized or len(normalized) > 64:
            raise ValueError("Each Colab part must contain 1–64 podcast chunks")
        payload = {"settings": {"tts_engine": "omnivoice", "tts_voice": profile.voice_id,
                                "tts_speed": speed, "pitch_shift": pitch_shift},
                   "scenes": normalized, "podcast_profile": profile.bundle()}
        return payload, normalized

    def _request_payload(self, request_record: Mapping[str, Any]) -> Dict[str, Any]:
        spec = json.loads((self.tts_dir / request_record["spec_path"]).read_text(encoding="utf-8"))
        bundle = json.loads((self.tts_dir / request_record["profile_bundle_path"]).read_text(encoding="utf-8"))
        payload = dict(spec)
        payload["podcast_profile"] = bundle
        return payload

    def _safe_episode_part_id(self, part_id: str) -> str:
        if not CHUNK_ID_RE.fullmatch(part_id):
            raise ValueError("part_id must be a safe stable identifier")
        return part_id

    def register_plan(self, parts: Mapping[str, Sequence[PodcastChunk]], *, speed: Optional[float] = None,
                      pitch_shift: Optional[float] = None,
                      script_revision: Optional[int | str] = None) -> Dict[str, Any]:
        """Freeze the episode plan, rejecting edits without a new script revision."""
        profile = self.profile
        params = profile.voice_config.get("recommended_params", {})
        resolved_speed = float(speed if speed is not None else DEFAULT_PODCAST_SPEED)
        resolved_pitch = float(pitch_shift if pitch_shift is not None else params.get("pitch_shift", 1.0))
        if len(parts) != 4:
            raise ValueError("A 20–30 minute podcast plan must register exactly four parts")
        plan: Dict[str, List[Dict[str, str]]] = {}
        for part_id, part_chunks in parts.items():
            self._safe_episode_part_id(part_id)
            normalized = []
            seen = set()
            for chunk in part_chunks:
                chunk_id = chunk.chunk_id.strip()
                text = chunk.text.strip()
                if not CHUNK_ID_RE.fullmatch(chunk_id) or chunk_id in seen or not text:
                    raise ValueError(f"Invalid or duplicate chunk in part {part_id}: {chunk_id}")
                seen.add(chunk_id)
                normalized.append({"chunk_id": chunk_id,
                                   "text_hash": sha256(text.encode("utf-8")),
                                   "chunk_hash": self._chunk_hash(text, resolved_speed, resolved_pitch, profile)})
            if not normalized:
                raise ValueError(f"Podcast part {part_id} is empty")
            plan[part_id] = normalized
        all_ids = [chunk["chunk_id"] for rows in plan.values() for chunk in rows]
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("Chunk IDs must be unique across all parts")
        generation = self.generation_signature(resolved_speed, resolved_pitch)
        generation_hash = sha256(canonical_json(generation))
        content_hash = sha256(canonical_json({part_id: [{"chunk_id": item["chunk_id"],
                                                         "text_hash": item["text_hash"]} for item in rows]
                                             for part_id, rows in plan.items()}))
        def save(data):
            previous = data.get("plan")
            effective_revision = script_revision
            if previous:
                if effective_revision is None:
                    effective_revision = previous.get("script_revision")
                same_revision = effective_revision == previous.get("script_revision")
                if same_revision and content_hash != previous.get("content_sha256"):
                    raise PodcastTTSError("Podcast chunk plan changed under the same script revision; create a new coordinator script revision")
                if (isinstance(effective_revision, int) and isinstance(previous.get("script_revision"), int)
                        and effective_revision < previous["script_revision"]):
                    raise PodcastTTSError("script_revision cannot move backwards")
                if previous.get("signature_sha256") != generation_hash or previous.get("plan_sha256") != sha256(canonical_json(plan)):
                    history = list(data.get("plan_history", []))
                    history.append({**previous, "replaced_at": time.time()})
                    data["plan_history"] = history
            data["plan"] = {"script_revision": effective_revision, "content_sha256": content_hash,
                            "signature": generation, "signature_sha256": generation_hash,
                            "plan_sha256": sha256(canonical_json(plan)), "registered_at": time.time()}
            data["planned_parts"] = list(plan)
            old_chunks = data.get("planned_chunks", {})
            data["planned_chunks"] = {
                chunk["chunk_id"]: {
                    **chunk, "part_id": part_id,
                    "state": old_chunks.get(chunk["chunk_id"], {}).get("state", "pending")
                    if old_chunks.get(chunk["chunk_id"], {}).get("chunk_hash") == chunk["chunk_hash"] else "pending",
                }
                for part_id, rows in plan.items() for chunk in rows
            }
        return self._update(save)

    def synthesize_part(
        self,
        part_id: str,
        chunks: Sequence[PodcastChunk],
        *,
        speed: Optional[float] = None,
        pitch_shift: Optional[float] = None,
        retry_failed: bool = False,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Synthesize one quarter-part and retain all completed chunk WAVs."""
        part_id = self._safe_episode_part_id(part_id)
        profile = self.profile
        rec_params = profile.voice_config.get("recommended_params", {})
        speed = float(speed if speed is not None else DEFAULT_PODCAST_SPEED)
        pitch_shift = float(pitch_shift if pitch_shift is not None else rec_params.get("pitch_shift", 1.0))
        if not (math.isfinite(speed) and 0.5 <= speed <= 2.0 and math.isfinite(pitch_shift) and 0.5 <= pitch_shift <= 2.0):
            raise ValueError("Podcast TTS speed and pitch must be finite values from 0.5 to 2.0")
        payload, normalized = self._make_payload(chunks, speed, pitch_shift, profile)
        request_hash = sha256(canonical_json(payload))
        episode_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", self.episode_id)[:48]
        part_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", part_id)[:40]
        base_id = f"podcast-{episode_safe}-{part_safe}-{request_hash[:20]}"
        runtime_id = self._runtime()
        self._store_profile_bundle(profile)
        manifest = self._read_manifest()
        old_id = manifest.get("parts", {}).get(part_id)
        if old_id and old_id in manifest.get("requests", {}):
            old_request = manifest["requests"][old_id]
            if old_request.get("request_hash") != request_hash and old_request.get("state") in (
                    "submitting", "queued", "starting", "running", "ambiguous", "interrupted", "partial_failed"):
                if old_request.get("runtime_id") != runtime_id:
                    self._set_request_state(old_id, "ambiguous", error="Colab runtime changed before the previous part could be reconciled")
                    raise PodcastTTSAmbiguous(f"Part {part_id} has an unresolved request from a previous Colab runtime")
                self._finish_request(old_id, old_request, old_request["part_id"], wait=True,
                                     resume_failed=old_request.get("state") in ("partial_failed", "interrupted"),
                                     progress_callback=progress_callback)

        prior_tries = [item for item in manifest.get("requests", {}).values()
                       if item.get("part_id") == part_id and item.get("base_request_id") == base_id]
        attempts_used = sum(max(1, int(item.get("remote_attempts", 1))) for item in prior_tries)
        attempt_index = 0
        request_id = base_id
        current_matches = (old_id and old_id in manifest.get("requests", {}) and
                           manifest["requests"][old_id].get("request_hash") == request_hash)
        if current_matches:
            current = manifest["requests"][old_id]
            if current.get("state") == "failed":
                if not retry_failed:
                    raise PodcastTTSRemoteFailure(current.get("error", "Colab reported a failed TTS task"))
                if attempts_used >= MAX_PART_ATTEMPTS:
                    raise PodcastTTSRemoteFailure("Podcast part exhausted initial generation plus two retries")
                attempt_index = attempts_used
                request_id = f"{base_id}-r{attempt_index}"
            else:
                request_id = old_id
                attempt_index = int(current.get("attempt", 0))
        elif prior_tries:
            latest = max(prior_tries, key=lambda item: int(item.get("attempt", 0)))
            if latest.get("state") == "failed" and not retry_failed:
                raise PodcastTTSRemoteFailure(latest.get("error", "Colab reported a failed TTS task"))
            if latest.get("state") == "failed":
                if attempts_used >= MAX_PART_ATTEMPTS:
                    raise PodcastTTSRemoteFailure("Podcast part exhausted initial generation plus two retries")
                attempt_index = attempts_used
                request_id = f"{base_id}-r{attempt_index}"
            else:
                request_id = latest["request_id"]
                attempt_index = int(latest.get("attempt", 0))

        if request_id in manifest.get("requests", {}):
            rec = manifest["requests"][request_id]
            if rec.get("runtime_id") != runtime_id and rec.get("state") == "succeeded":
                if self._local_chunks_valid(rec):
                    return {"status": "success", "request_id": request_id, "part_id": part_id,
                            "progress": self.progress(), "chunks": self._local_chunk_outputs(rec), "reused": True}
                raise PodcastTTSAmbiguous("The old Colab runtime completed this part, but its local WAVs are missing; refusing to synthesize again")
            if rec.get("runtime_id") != runtime_id and rec.get("state") not in ("succeeded", "failed"):
                raise PodcastTTSAmbiguous(f"Request {request_id} belongs to a previous Colab runtime; refusing to resend")
            if rec.get("state") == "failed" and not retry_failed:
                raise PodcastTTSRemoteFailure(rec.get("error", "Colab reported a failed TTS task"))
            if rec.get("state") == "partial_failed" and not retry_failed:
                raise PodcastTTSRemoteFailure("Part stopped after a partial result; call resume_part() to continue missing chunks")
            if rec.get("state") == "ambiguous":
                raise PodcastTTSAmbiguous(rec.get("error", "Remote task outcome is unknown"))
            if rec.get("state") == "succeeded" and self._local_chunks_valid(rec):
                return {"status": "success", "request_id": request_id, "part_id": part_id,
                        "progress": self.progress(), "chunks": self._local_chunk_outputs(rec), "reused": True}
        else:
            profile_path = self._store_profile_bundle(profile)
            spec_path = f"requests/{request_id}.json"
            _atomic_json(self.tts_dir / spec_path, {"settings": payload["settings"], "scenes": normalized})
            entry = {"request_id": request_id, "base_request_id": base_id, "request_hash": request_hash,
                     "part_id": part_id, "runtime_id": runtime_id, "profile_fingerprint": profile.fingerprint,
                     "profile_bundle_path": profile_path, "spec_path": spec_path,
                     "state": "submitting", "attempt": attempt_index, "remote_attempts": 0,
                     "chunk_ids": [scene["id"] for scene in normalized],
                     "created_at": time.time(), "updated_at": time.time()}
            def add_entry(data):
                requests = data.setdefault("requests", {})
                existing = requests.get(request_id)
                if existing and existing.get("request_hash") != request_hash:
                    raise PodcastTTSError("Local request_id collision with a different request hash")
                if not existing:
                    requests[request_id] = entry
                data.setdefault("parts", {})[part_id] = request_id
                data.setdefault("expected_chunks", {})[part_id] = entry["chunk_ids"]
                for scene in normalized:
                    previous = data.setdefault("chunks", {}).get(scene["id"], {})
                    if previous.get("chunk_hash") != scene["chunk_hash"]:
                        data["chunks"][scene["id"]] = {
                            "chunk_id": scene["id"], "part_id": part_id,
                            "chunk_hash": scene["chunk_hash"], "state": "pending"}
            self._update(add_entry)
            manifest = self._read_manifest()
            rec = manifest["requests"][request_id]

        result = self._finish_request(request_id, rec, part_id, wait=True,
                                      resume_failed=retry_failed or rec.get("state") in ("partial_failed", "interrupted"),
                                      progress_callback=progress_callback)
        return result

    def _read_manifest(self) -> Dict[str, Any]:
        with self._manifest_lock():
            return self._read_manifest_unlocked()

    def resume_part(self, part_id: str, *, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """Reconcile or continue a known part without changing its request hash."""
        manifest = self._read_manifest()
        request_id = manifest.get("parts", {}).get(part_id)
        if not request_id:
            raise PodcastTTSError(f"No saved TTS request for part {part_id}")
        record = manifest["requests"][request_id]
        try:
            runtime_id = self._runtime()
        except PodcastTTSUnavailable as exc:
            self._set_request_state(request_id, "ambiguous", error="Colab runtime is unavailable; request outcome cannot be queried safely")
            raise PodcastTTSAmbiguous("Colab runtime is unavailable; refusing to resubmit this part") from exc
        if record.get("runtime_id") != runtime_id and record.get("state") == "succeeded":
            if self._local_chunks_valid(record):
                return {"status": "success", "request_id": request_id, "part_id": part_id,
                        "progress": self.progress(), "chunks": self._local_chunk_outputs(record), "reused": True}
            raise PodcastTTSAmbiguous("The prior runtime completed this part, but its local result is missing; refusing to resubmit")
        if record.get("runtime_id") != runtime_id and record.get("state") != "failed":
            self._set_request_state(request_id, "ambiguous", error="Colab runtime changed; refusing to resend an unresolved request")
            raise PodcastTTSAmbiguous(f"Colab runtime changed; request {request_id} cannot be queried or resent safely")
        return self._finish_request(request_id, record, part_id, wait=True, resume_failed=True,
                                    progress_callback=progress_callback)

    def _finish_request(self, request_id: str, rec: Mapping[str, Any], part_id: str, *, wait: bool,
                        resume_failed: bool, progress_callback: Optional[Callable[[Dict[str, Any]], None]]) -> Dict[str, Any]:
        try:
            runtime_id = self._runtime()
        except PodcastTTSUnavailable as exc:
            self._set_request_state(request_id, "ambiguous", error="Colab runtime is unavailable; request outcome cannot be queried safely")
            raise PodcastTTSAmbiguous(f"Colab runtime is unavailable while reconciling {request_id}") from exc
        if rec.get("runtime_id") and rec.get("runtime_id") != runtime_id:
            if rec.get("state") == "succeeded" and self._local_chunks_valid(rec):
                return {"status": "success", "request_id": request_id, "part_id": part_id,
                        "progress": self.progress(), "chunks": self._local_chunk_outputs(rec), "reused": True}
            self._set_request_state(request_id, "ambiguous", error="Colab runtime changed while the part was unresolved")
            raise PodcastTTSAmbiguous(f"Colab runtime changed while request {request_id} was unresolved; refusing to resend")
        payload = self._request_payload(rec)
        task_state = None
        try:
            task_state = self._get_task(request_id)
        except _RemoteHTTPError as exc:
            if exc.status != 404:
                self._set_request_state(request_id, "ambiguous", error="Colab task status could not be queried safely")
                raise PodcastTTSAmbiguous(f"Cannot query Colab task {request_id}; refusing to resend") from exc
        except PodcastTTSAmbiguous:
            self._set_request_state(request_id, "ambiguous", error="Colab task status could not be queried safely")
            raise
        if task_state is None:
            task_state = self._submit(request_id, rec["request_hash"], payload, resume=False)
        elif task_state.get("state") in ("interrupted", "partial_failed") and resume_failed:
            task_state = self._submit(request_id, rec["request_hash"], payload, resume=True)
        self._apply_remote_status(request_id, task_state)
        deadline = time.monotonic() + self.wait_timeout_seconds
        last_keepalive_at = time.monotonic()
        while task_state.get("state") in ("queued", "starting", "running"):
            if progress_callback:
                progress_callback(self.progress())
            if not wait or time.monotonic() >= deadline:
                self._set_request_state(request_id, "ambiguous", error="Task is still running; resume will query the same idempotency key.")
                raise PodcastTTSAmbiguous(f"Colab task {request_id} is still running; no new submission was made")
            time.sleep(self.status_poll_seconds)
            if time.monotonic() - last_keepalive_at >= self.keepalive_interval_seconds:
                self._send_keepalive(request_id)
                last_keepalive_at = time.monotonic()
            try:
                task_state = self._refresh_task(request_id, rec)
            except PodcastTTSAmbiguous:
                self._set_request_state(request_id, "ambiguous", error="Colab status could not be reached; request may still be running.")
                raise
            self._apply_remote_status(request_id, task_state)
        if task_state.get("state") == "succeeded":
            self._download_and_store(request_id, rec, task_state)
            return {"status": "success", "request_id": request_id, "part_id": part_id,
                    "progress": self.progress(), "chunks": self._local_chunk_outputs(rec)}
        if task_state.get("state") in ("partial_failed", "interrupted"):
            self._set_request_state(request_id, task_state["state"], error=task_state.get("error"))
            raise PodcastTTSRemoteFailure(task_state.get("error") or f"Colab task {request_id} stopped with partial chunks")
        if task_state.get("state") in ("failed", "ambiguous"):
            self._set_request_state(request_id, task_state["state"], error=task_state.get("error"))
            if task_state["state"] == "ambiguous":
                raise PodcastTTSAmbiguous(task_state.get("error", "Colab task outcome is ambiguous"))
            raise PodcastTTSRemoteFailure(task_state.get("error", "Colab task failed"))
        raise PodcastTTSProtocolError(f"Unexpected Colab task state: {task_state.get('state')}")

    def _submit(self, request_id: str, request_hash: str, payload: Dict[str, Any], resume: bool) -> Dict[str, Any]:
        def mark_submitting(data):
            item = data["requests"][request_id]
            if item.get("state") not in ("succeeded", "failed"):
                item.update({"state": "submitting", "updated_at": time.time()})
        self._update(mark_submitting)
        try:
            _status, raw, _headers = self._http("POST", "/api/v1/podcast/tts/jobs",
                                                {"request_id": request_id, "request_hash": request_hash,
                                                 "payload": payload, "resume": resume}, timeout=30)
            state = json.loads(raw.decode("utf-8"))
            self._set_request_state(request_id, state.get("state", "queued"), remote=state)
            return state
        except _RemoteHTTPError as exc:
            self._set_request_state(request_id, "failed", error=f"Colab rejected the TTS request with HTTP {exc.status}")
            raise PodcastTTSRemoteFailure(f"Colab rejected the TTS request with HTTP {exc.status}") from exc
        except PodcastTTSAmbiguous:
            # The POST may have reached the worker. Query its stable key, and
            # only repeat POST when the same runtime confirms it has no record.
            try:
                runtime = self._runtime()
                rec = self._read_manifest()["requests"][request_id]
                if runtime != rec.get("runtime_id"):
                    self._set_request_state(request_id, "ambiguous", error="Colab runtime changed during submission")
                    raise PodcastTTSAmbiguous("Colab runtime changed during submission; refusing to resend")
                status = self._get_task(request_id)
                self._apply_remote_status(request_id, status)
                return status
            except _RemoteHTTPError as exc:
                if exc.status == 404:
                    # The server's POST handler registers the id before work;
                    # replaying this exact key/hash is atomic and idempotent.
                    _status, raw, _headers = self._http("POST", "/api/v1/podcast/tts/jobs",
                                                        {"request_id": request_id, "request_hash": request_hash,
                                                         "payload": payload, "resume": resume}, timeout=30)
                    state = json.loads(raw.decode("utf-8"))
                    self._set_request_state(request_id, state.get("state", "queued"), remote=state)
                    return state
                self._set_request_state(request_id, "ambiguous", error="Submission was sent but task state could not be reconciled")
                raise PodcastTTSAmbiguous("Colab submission outcome is unknown; resume will reconcile this same request") from exc
            except PodcastTTSAmbiguous:
                raise
            except Exception as exc:
                self._set_request_state(request_id, "ambiguous", error=f"Submission may be running: {type(exc).__name__}: {exc}")
                raise PodcastTTSAmbiguous("Colab submission outcome is unknown; resume will reconcile this same request") from exc

    def _get_task(self, request_id: str) -> Dict[str, Any]:
        try:
            _status, raw, _headers = self._http("GET", f"/api/v1/podcast/tts/jobs/{request_id}", timeout=20)
        except _RemoteHTTPError:
            raise
        return json.loads(raw.decode("utf-8"))

    def _apply_remote_status(self, request_id: str, state: Mapping[str, Any]) -> None:
        remote_runtime = state.get("runtime_id")
        def apply(manifest):
            item = manifest["requests"][request_id]
            if remote_runtime and remote_runtime != item.get("runtime_id"):
                item.update({"state": "ambiguous", "error": "Remote task belongs to another Colab runtime"})
                return
            remote_state = state.get("state", item.get("state"))
            item.update({"state": "downloading" if remote_state == "succeeded" else remote_state,
                "remote_state": remote_state, "remote_progress": {
                "completed_chunks": state.get("completed_chunks", 0),
                "total_chunks": state.get("total_chunks", len(item.get("chunk_ids", []))),
                "progress_percent": state.get("progress_percent", 0),
                "chunks": state.get("chunks", []),
            }, "remote_attempts": int(state.get("attempts", item.get("remote_attempts", 0))),
                "updated_at": time.time()})
            if state.get("error"):
                item["error"] = state["error"]
            for chunk in state.get("chunks", []):
                chunk_id = chunk.get("id")
                for chunk_map in (manifest.get("chunks", {}), manifest.get("planned_chunks", {})):
                    if chunk_id in chunk_map:
                        chunk_map[chunk_id].update({"state": chunk.get("state", "pending"),
                                                    "remote_request_id": request_id,
                                                    "wav_sha256": chunk.get("wav_sha256"),
                                                    "duration_seconds": chunk.get("duration_seconds")})
        self._update(apply)

    def _set_request_state(self, request_id: str, state: str, *, error: Optional[str] = None,
                           remote: Optional[Mapping[str, Any]] = None) -> None:
        def apply(manifest):
            item = manifest.get("requests", {}).get(request_id)
            if not item:
                return
            item.update({"state": state, "updated_at": time.time()})
            if error is not None:
                item["error"] = error
            if remote:
                item["remote_progress"] = {"completed_chunks": remote.get("completed_chunks", 0),
                                            "total_chunks": remote.get("total_chunks", len(item.get("chunk_ids", []))),
                                            "progress_percent": remote.get("progress_percent", 0),
                                            "chunks": remote.get("chunks", [])}
                item["remote_attempts"] = int(remote.get("attempts", item.get("remote_attempts", 0)))
        self._update(apply)

    def import_local_checkpoints(self, part_id: str) -> List[Dict[str, Any]]:
        """Validate and adopt WAV chunks saved before a Colab runtime was paused."""
        manifest = self._read_manifest()
        request_id = manifest.get("parts", {}).get(part_id)
        if not request_id or request_id not in manifest.get("requests", {}):
            raise PodcastTTSError(f"No saved TTS request for part {part_id}")
        record = manifest["requests"][request_id]
        checkpoint_dir = self.tts_dir / "checkpoints" / request_id
        metadata_dir = checkpoint_dir / "chunk_meta"
        if not metadata_dir.is_dir():
            return []
        payload = self._request_payload(record)
        expected = {item["id"]: item for item in payload.get("scenes", [])}
        staged: List[Dict[str, Any]] = []
        for meta_path in sorted(metadata_dir.glob("*.json")):
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise PodcastTTSProtocolError(f"Checkpoint metadata is unreadable: {meta_path.name}") from exc
            chunk_id = metadata.get("scene_id")
            if not isinstance(chunk_id, str) or chunk_id not in expected:
                raise PodcastTTSProtocolError(f"Checkpoint belongs to an unknown chunk: {meta_path.name}")
            if not chunk_id.startswith(part_id + "-"):
                raise PodcastTTSProtocolError(f"Checkpoint chunk {chunk_id} does not belong to part {part_id}")
            scene = expected[chunk_id]
            if (metadata.get("chunk_hash") != scene.get("chunk_hash") or
                    metadata.get("profile_fingerprint") != record.get("profile_fingerprint") or
                    metadata.get("text_sha256") != sha256(scene["narration"].encode("utf-8"))):
                raise PodcastTTSProtocolError(f"Checkpoint identity does not match saved request for {chunk_id}")
            wav_path = checkpoint_dir / "chunks" / f"{chunk_id}.wav"
            if not wav_path.is_file():
                raise PodcastTTSProtocolError(f"Checkpoint WAV is missing for {chunk_id}")
            raw = wav_path.read_bytes()
            digest = sha256(raw)
            if digest != metadata.get("wav_sha256"):
                raise PodcastTTSProtocolError(f"Checkpoint WAV checksum mismatch for {chunk_id}")
            try:
                with wave.open(str(wav_path), "rb") as wav:
                    channels, width, rate, frames = (wav.getnchannels(), wav.getsampwidth(),
                                                      wav.getframerate(), wav.getnframes())
                    if channels != 1 or width != 2 or rate != 24000 or frames <= 0:
                        raise PodcastTTSProtocolError(f"Checkpoint WAV format is invalid for {chunk_id}")
                    if len(wav.readframes(frames)) != frames * channels * width:
                        raise PodcastTTSProtocolError(f"Checkpoint WAV is truncated for {chunk_id}")
            except wave.Error as exc:
                raise PodcastTTSProtocolError(f"Checkpoint WAV is unreadable for {chunk_id}") from exc
            wav_dest = self.tts_dir / "chunks" / f"{chunk_id}.wav"
            meta_dest = self.tts_dir / "chunk_meta" / f"{chunk_id}.json"
            _atomic_copy(wav_path, wav_dest)
            imported = dict(metadata)
            imported.update({"chunk_id": chunk_id, "part_id": part_id, "episode_id": self.episode_id,
                             "path": str(wav_dest.resolve()), "state": "succeeded",
                             "source": "colab_checkpoint", "source_request_id": request_id,
                             "checkpoint_imported_at": time.time()})
            _atomic_json(meta_dest, imported)
            imported["wav_sha256"] = digest
            staged.append(imported)
        if not staged:
            return []

        def adopt(data):
            chunks = data.setdefault("chunks", {})
            planned = data.setdefault("planned_chunks", {})
            request = data.get("requests", {}).get(request_id)
            progress = request.get("remote_progress", {}).get("chunks", []) if request else []
            progress_by_id = {item.get("id"): item for item in progress if isinstance(item, dict)}
            for item in staged:
                chunk_id = item["chunk_id"]
                chunks[chunk_id] = dict(item)
                if chunk_id in planned:
                    planned[chunk_id].update(item)
                if chunk_id in progress_by_id:
                    progress_by_id[chunk_id].update({"state": "succeeded", "path": f"chunks/{chunk_id}.wav",
                                                     "wav_sha256": item["wav_sha256"],
                                                     "duration_seconds": item["duration_seconds"],
                                                     "reused_from_local_checkpoint": True})
            if request:
                remote = request.setdefault("remote_progress", {})
                remote["chunks"] = list(progress_by_id.values())
                remote["completed_chunks"] = sum(item.get("state") == "succeeded" for item in remote["chunks"])
                remote["total_chunks"] = len(remote["chunks"])
                remote["progress_percent"] = round(100 * remote["completed_chunks"] / max(1, remote["total_chunks"]))
        self._update(adopt)
        return staged

    def mark_part_failed_if_runtime_changed(self, part_id: str) -> Dict[str, Any]:
        """Retire an unresolved request only after the current Colab runtime proves it is gone."""
        manifest = self._read_manifest()
        request_id = manifest.get("parts", {}).get(part_id)
        if not request_id or request_id not in manifest.get("requests", {}):
            raise PodcastTTSError(f"No saved TTS request for part {part_id}")
        record = manifest["requests"][request_id]
        if record.get("state") == "failed":
            return {"status": "already_failed", "request_id": request_id, "part_id": part_id}
        if record.get("state") == "succeeded" and self._local_chunks_valid(record):
            return {"status": "already_succeeded", "request_id": request_id, "part_id": part_id}
        try:
            from podcast.colab_deploy import _load_state, _session_exists
            state = _load_state(self.sys_root)
            session, profile_alias = state.get("session"), state.get("profile_alias")
            if not isinstance(session, str) or not isinstance(profile_alias, str):
                raise PodcastTTSUnavailable("Podcast Colab session profile is missing")
            if not _session_exists(profile_alias, session):
                return self.mark_part_failed_if_session_missing(part_id)
            current_runtime_id = self._runtime()
            if current_runtime_id == record.get("runtime_id"):
                raise PodcastTTSAmbiguous(
                    f"The original Colab runtime is still active; refusing to retire {request_id}")
            try:
                self._get_task(request_id)
            except _RemoteHTTPError as exc:
                if exc.status != 404:
                    raise PodcastTTSAmbiguous("The new Colab runtime did not conclusively reject the old task id") from exc
            else:
                raise PodcastTTSAmbiguous("The old request id exists in the current runtime; refusing to retire it")
        except (PodcastTTSAmbiguous, PodcastTTSUnavailable):
            raise
        except Exception as exc:
            raise PodcastTTSUnavailable("Could not verify that the previous Colab runtime was replaced") from exc

        now = time.time()
        error = "Previous Colab runtime was replaced; its request id is absent from the current runtime task store."
        def retire(data):
            current = data.get("requests", {}).get(request_id)
            if not current or current.get("state") == "succeeded":
                raise PodcastTTSError("TTS request changed while confirming runtime replacement")
            current.update({"state": "failed", "error": error, "updated_at": now,
                            "runtime_loss_verified": {"session": session, "profile_alias": profile_alias,
                                                       "from_runtime_id": record.get("runtime_id"),
                                                       "to_runtime_id": current_runtime_id,
                                                       "verified_at": now}})
        self._update(retire)
        return {"status": "failed_runtime_replaced", "request_id": request_id, "part_id": part_id}

    def mark_part_failed_if_session_missing(self, part_id: str) -> Dict[str, Any]:
        """Retire a remote request only after Colab confirms its session is gone.

        This makes the normal bounded retry path available after a runtime is
        conclusively absent. A running or unqueryable session remains
        ambiguous and is never resent.
        """
        manifest = self._read_manifest()
        request_id = manifest.get("parts", {}).get(part_id)
        if not request_id or request_id not in manifest.get("requests", {}):
            raise PodcastTTSError(f"No saved TTS request for part {part_id}")
        record = manifest["requests"][request_id]
        if record.get("state") == "failed":
            return {"status": "already_failed", "request_id": request_id, "part_id": part_id}
        if record.get("state") == "succeeded":
            raise PodcastTTSError(f"Part {part_id} already succeeded; refusing to retire it")
        if record.get("state") not in ("submitting", "queued", "starting", "running", "downloading", "ambiguous",
                                        "interrupted", "partial_failed"):
            raise PodcastTTSError(f"Part {part_id} is not an unresolved Colab request")
        try:
            from podcast.colab_deploy import _load_state, _session_exists
            state = _load_state(self.sys_root)
            session, profile_alias = state.get("session"), state.get("profile_alias")
            if not isinstance(session, str) or not isinstance(profile_alias, str):
                raise PodcastTTSUnavailable("Podcast Colab session profile is missing")
            if _session_exists(profile_alias, session):
                raise PodcastTTSAmbiguous(
                    f"Colab session {session} is still active; refusing to retire request {request_id}")
        except PodcastTTSAmbiguous:
            raise
        except Exception as exc:
            raise PodcastTTSUnavailable("Could not verify that the prior Colab session is gone") from exc

        now = time.time()
        error = f"Colab session {session} is absent from the active-session list; remote runtime task was lost."
        def apply(data):
            current = data.get("requests", {}).get(request_id)
            if not current or current.get("state") == "succeeded":
                raise PodcastTTSError("TTS request changed while confirming runtime loss")
            current.update({"state": "failed", "error": error, "updated_at": now,
                            "runtime_loss_verified": {"session": session,
                                                       "profile_alias": profile_alias,
                                                       "verified_at": now}})
        self._update(apply)
        return {"status": "failed_runtime_lost", "request_id": request_id, "part_id": part_id}

    def _send_keepalive(self, request_id: str) -> None:
        """Send a lightweight notebook cell while the server-side TTS runs."""
        success = False
        error_type = None
        try:
            from podcast.colab_deploy import keepalive_podcast_worker
            keepalive_podcast_worker(self.sys_root)
            success = True
        except Exception as exc:
            error_type = type(exc).__name__

        def apply(manifest):
            request = manifest.get("requests", {}).get(request_id)
            if not request:
                return
            status = request.setdefault("keepalive", {"attempts": 0, "successes": 0, "failures": 0})
            status["attempts"] = int(status.get("attempts", 0)) + 1
            status["successes" if success else "failures"] = int(status.get("successes" if success else "failures", 0)) + 1
            status["last_attempt_at"] = time.time()
            status["last_result"] = "ok" if success else "failed"
            if error_type:
                status["last_error_type"] = error_type
            else:
                status.pop("last_error_type", None)
        self._update(apply)

    def _download_and_store(self, request_id: str, rec: Mapping[str, Any], remote: Mapping[str, Any]) -> None:
        _status, archive_bytes, headers = self._http("GET", f"/api/v1/podcast/tts/jobs/{request_id}/result",
                                                      timeout=max(60, self.config.timeout_tts))
        if headers.get("X-Podcast-TTS-Request-Id") != request_id:
            raise PodcastTTSProtocolError("Colab returned an archive for a different request id")
        expected_archive_hash = remote.get("result_sha256")
        if expected_archive_hash and sha256(archive_bytes) != expected_archive_hash:
            raise PodcastTTSProtocolError("Colab task archive checksum does not match task status")
        if remote.get("result_bytes") and len(archive_bytes) != remote["result_bytes"]:
            raise PodcastTTSProtocolError("Colab task archive size does not match task status")
        with tempfile.TemporaryDirectory(prefix="podcast_tts_result_") as temp:
            extract_dir = Path(temp)
            try:
                with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tar:
                    total_unpacked = 0
                    for member in tar.getmembers():
                        member_path = PurePosixPath(member.name)
                        if (member_path.is_absolute() or ".." in member_path.parts or "\\" in member.name
                                or member.issym() or member.islnk() or member.isdev() or member.isfifo()):
                            raise PodcastTTSProtocolError("Colab archive contains an unsafe path")
                        destination = extract_dir.joinpath(*member_path.parts)
                        if member.isdir():
                            destination.mkdir(parents=True, exist_ok=True)
                            continue
                        if not member.isfile():
                            raise PodcastTTSProtocolError("Colab archive contains an unsupported entry")
                        total_unpacked += member.size
                        if member.size < 0 or total_unpacked > 1_000_000_000:
                            raise PodcastTTSProtocolError("Colab archive exceeds the allowed expanded size")
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        source = tar.extractfile(member)
                        if source is None:
                            raise PodcastTTSProtocolError("Colab archive contains an unreadable file")
                        with source, destination.open("wb") as target:
                            shutil.copyfileobj(source, target)
            except (tarfile.TarError, OSError) as exc:
                raise PodcastTTSProtocolError("Colab returned an invalid TTS archive") from exc
            result_path = extract_dir / "tts-result.json"
            if not result_path.is_file():
                raise PodcastTTSProtocolError("Colab archive is missing tts-result.json")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("request_id") != request_id or result.get("request_hash") != rec.get("request_hash"):
                raise PodcastTTSProtocolError("Colab result metadata does not match the submitted request")
            expected_scenes = {item["id"]: item for item in self._request_payload(rec)["scenes"]}
            returned = {item.get("scene_id"): item for item in result.get("segments", []) if isinstance(item, dict)}
            if set(returned) != set(expected_scenes):
                raise PodcastTTSProtocolError("Colab result is missing or duplicating podcast chunks")
            for chunk_id, scene in expected_scenes.items():
                segment = returned[chunk_id]
                if segment.get("chunk_hash") != scene["chunk_hash"] or segment.get("text") != scene["narration"]:
                    raise PodcastTTSProtocolError(f"Colab result metadata mismatch for {chunk_id}")
                archive_rel = PurePosixPath(segment.get("path", ""))
                if archive_rel.is_absolute() or ".." in archive_rel.parts:
                    raise PodcastTTSProtocolError(f"Unsafe Colab WAV path for {chunk_id}")
                source = extract_dir.joinpath(*archive_rel.parts)
                if not source.is_file():
                    raise PodcastTTSProtocolError(f"Colab WAV is missing for {chunk_id}")
                wav_bytes = source.read_bytes()
                try:
                    with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
                        channels, sample_width, sample_rate, frames = (wav.getnchannels(), wav.getsampwidth(),
                                                                      wav.getframerate(), wav.getnframes())
                except wave.Error as exc:
                    raise PodcastTTSProtocolError(f"Colab returned an invalid WAV for {chunk_id}") from exc
                if channels != 1 or sample_width != 2 or sample_rate <= 0 or frames <= 0:
                    raise PodcastTTSProtocolError(f"Colab WAV format is invalid for {chunk_id}")
                digest = sha256(wav_bytes)
                chunk_path = self.tts_dir / "chunks" / f"{chunk_id}.wav"
                chunk_meta_path = self.tts_dir / "chunk_meta" / f"{chunk_id}.json"
                chunk_path.parent.mkdir(parents=True, exist_ok=True)
                temp_wav = chunk_path.with_name(chunk_path.name + f".{uuid.uuid4().hex}.tmp")
                temp_wav.write_bytes(wav_bytes)
                os.replace(temp_wav, chunk_path)
                metadata = {"chunk_id": chunk_id, "part_id": rec["part_id"], "episode_id": self.episode_id,
                            "request_id": request_id, "request_hash": rec["request_hash"],
                            "chunk_hash": scene["chunk_hash"], "profile_fingerprint": rec["profile_fingerprint"],
                            "voice_id": result.get("voice"), "model": self.profile.voice_config.get("model"),
                            "text_sha256": sha256(scene["narration"].encode("utf-8")),
                            "sample_rate": sample_rate, "channels": channels, "duration_seconds": frames / sample_rate,
                            "wav_sha256": digest, "path": str(chunk_path), "source": "colab",
                            "saved_at": time.time()}
                for key in ("inference_precision", "weights_dtype", "autocast_dtype", "attention_backend",
                            "vad_input_dtype", "inference_started_at", "inference_seconds",
                            "real_time_factor", "slow_chunk_warning"):
                    if segment.get(key) is not None:
                        metadata[key] = segment[key]
                _atomic_json(chunk_meta_path, metadata)
                def set_chunk(manifest):
                    entry = {**metadata, "state": "succeeded"}
                    manifest.setdefault("chunks", {})[chunk_id] = entry
                    if chunk_id in manifest.get("planned_chunks", {}):
                        manifest["planned_chunks"][chunk_id].update(entry)
                self._update(set_chunk)
        self._set_request_state(request_id, "succeeded", remote=remote)

    def _local_chunk_outputs(self, rec: Mapping[str, Any]) -> List[Dict[str, Any]]:
        manifest = self._read_manifest()
        return [manifest.get("chunks", {}).get(chunk_id, {"chunk_id": chunk_id, "state": "pending"})
                for chunk_id in rec.get("chunk_ids", [])]

    def _local_chunks_valid(self, rec: Mapping[str, Any]) -> bool:
        manifest = self._read_manifest()
        for chunk_id in rec.get("chunk_ids", []):
            chunk = manifest.get("chunks", {}).get(chunk_id, {})
            path = Path(chunk.get("path", ""))
            if not path.is_file() or not chunk.get("wav_sha256"):
                return False
            if sha256(path.read_bytes()) != chunk.get("wav_sha256"):
                return False
        return bool(rec.get("chunk_ids"))

    def progress(self) -> Dict[str, Any]:
        manifest = self._read_manifest()
        planned_chunks = manifest.get("planned_chunks") or manifest.get("chunks", {})
        chunks = list(planned_chunks.values())
        completed = sum(item.get("state") == "succeeded" for item in chunks)
        current_parts = manifest.get("parts", {})
        planned_parts = manifest.get("planned_parts") or list(current_parts)
        requests = [manifest.get("requests", {}).get(current_parts.get(part_id, ""), {"part_id": part_id, "state": "pending"})
                    for part_id in planned_parts]
        done_parts = sum(item.get("state") == "succeeded" for item in requests)
        expected_parts = len(planned_parts)
        return {"episode_id": self.episode_id, "completed_chunks": completed, "total_chunks": len(chunks),
                "chunk_progress_percent": round(100 * completed / len(chunks)) if chunks else 0,
                "completed_parts": done_parts, "total_parts": expected_parts,
                "part_progress_percent": round(100 * done_parts / expected_parts) if expected_parts else 0,
                "chunks": chunks,
                "parts": [{"part_id": item.get("part_id"), "state": item.get("state"),
                           "request_id": item.get("request_id"), "remote_progress": item.get("remote_progress")}
                          for item in requests]}

    def _refresh_task(self, request_id: str, rec: Mapping[str, Any]) -> Dict[str, Any]:
        try:
            state = self._get_task(request_id)
        except _RemoteHTTPError as exc:
            if exc.status != 404:
                raise PodcastTTSAmbiguous(f"Cannot query Colab task {request_id}; it may still be running") from exc
            current_runtime = self._runtime()
            if current_runtime != rec.get("runtime_id"):
                raise PodcastTTSAmbiguous(f"Colab runtime changed; task {request_id} no longer has queryable state") from exc
            payload = self._request_payload(rec)
            state = self._submit(request_id, rec["request_hash"], payload, resume=False)
        if state.get("runtime_id") != rec.get("runtime_id"):
            self._set_request_state(request_id, "ambiguous", error="Colab task response came from another runtime")
            raise PodcastTTSAmbiguous(f"Colab task {request_id} is associated with a different runtime")
        return state

    def _read_cached_wav(self, path: Path) -> tuple[float, int]:
        try:
            with wave.open(str(path), "rb") as wav:
                if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() <= 0 or wav.getnframes() <= 0:
                    raise PodcastTTSError("Cached calibration WAV has an invalid format")
                sample_rate = wav.getframerate()
                duration = wav.getnframes() / float(sample_rate)
        except wave.Error as exc:
            raise PodcastTTSError("Cached calibration WAV is unreadable") from exc
        return duration, sample_rate

    def calibrate(self, speed: Optional[float] = None, *, cache_only: bool = False, synthesizer=None, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> CalibrationResult:
        """Measure the approved profile's Vietnamese speaking pace on Colab."""
        profile = self.profile
        default_speed = DEFAULT_PODCAST_SPEED
        speed = float(speed if speed is not None else default_speed)
        pitch = float(profile.voice_config.get("recommended_params", {}).get("pitch_shift", 1.0))
        sample_hash = sha256(CALIBRATION_TEXT.encode("utf-8"))
        model = profile.voice_config["model"]
        cache_key = sha256(canonical_json({"profile_fingerprint": profile.fingerprint, "model": model,
                                           "speed": speed, "pitch_shift": pitch, "runner_version": RUNNER_VERSION,
                                           "sample_sha256": sample_hash}))
        cache_dir = self.calibration_cache_dir / cache_key
        wav_path, meta_path = cache_dir / "calibration.wav", cache_dir / "calibration.json"
        if wav_path.is_file() and meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                duration, _sample_rate = self._read_cached_wav(wav_path)
                if (meta.get("cache_key") == cache_key and meta.get("wav_sha256") == sha256(wav_path.read_bytes())
                        and meta.get("sample_sha256") == sample_hash and meta.get("sample_text") == CALIBRATION_TEXT
                        and meta.get("token_count") == len(CALIBRATION_TEXT.split()) and duration > 0):
                    tokens = len(CALIBRATION_TEXT.split())
                    return CalibrationResult(tokens / duration * 60.0, tokens, duration, str(wav_path), True,
                                             profile.fingerprint, model, speed, sample_hash,
                                             CALIBRATION_TEXT, cache_key)
            except Exception:
                pass
        if cache_only:
            raise CalibrationCacheMiss("Chưa có hiệu chỉnh đã xác minh cho cấu hình giọng hiện tại.")
        calibration_part = f"calibration-{cache_key[:12]}"
        calibration_chunk = f"CAL-{cache_key[:12]}"
        synthesize = synthesizer or self.synthesize_part
        synthesize(calibration_part, [PodcastChunk(calibration_chunk, CALIBRATION_TEXT)], speed=speed,
                             pitch_shift=pitch, retry_failed=True,
                             progress_callback=progress_callback)
        generated = self.tts_dir / "chunks" / f"{calibration_chunk}.wav"
        duration, _sample_rate = self._read_cached_wav(generated)
        cache_dir.mkdir(parents=True, exist_ok=True)
        _atomic_copy(generated, wav_path)
        token_count = len(CALIBRATION_TEXT.split())
        _atomic_json(meta_path, {"cache_key": cache_key, "profile_fingerprint": profile.fingerprint,
                                 "model": model, "speed": speed, "pitch_shift": pitch,
                                 "settings": self.generation_signature(speed=speed, pitch_shift=pitch)["settings"],
                                 "sample_sha256": sample_hash,
                                 "sample_text": CALIBRATION_TEXT,
                                 "token_count": token_count, "duration_seconds": duration,
                                 "estimated_wpm": token_count / duration * 60.0,
                                 "wav_sha256": sha256(wav_path.read_bytes()), "created_at": time.time()})
        tokens = len(CALIBRATION_TEXT.split())
        return CalibrationResult(tokens / duration * 60.0, tokens, duration, str(wav_path), False,
                                 profile.fingerprint, model, speed, sample_hash,
                                 CALIBRATION_TEXT, cache_key)


class _RemoteHTTPError(PodcastTTSError):
    def __init__(self, status: int, message: Any):
        self.status = status
        self.message = message
        super().__init__(f"Colab HTTP {status}: {message}")
