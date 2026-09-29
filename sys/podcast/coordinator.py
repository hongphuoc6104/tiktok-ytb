"""Durable episode state and pluggable orchestration for long-form podcasts.

The coordinator owns episode metadata, immutable brief/script revisions, stable
chunk IDs, and resumable stage state. It deliberately does not implement TTS,
image generation, or video encoding; those are injected as handlers.
"""
from __future__ import annotations

import contextlib
import copy
import datetime as dt
import fcntl
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import unicodedata
import uuid
import wave
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence


SYS_ROOT = Path(__file__).resolve().parents[1]
EPISODE_MANIFEST = "podcast_manifest.json"
PART_IDS = tuple(f"P{i:02}" for i in range(1, 5))
MAX_ATTEMPTS = 3  # Technical attempts; image creation has its own stricter cap.
CHUNK_TARGET_SECONDS = 60
CHUNK_MAX_SECONDS = 80


class EpisodeError(ValueError):
    """A recoverable, user-facing episode workflow error."""


def _utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_digest(value: Any) -> str:
    return _digest(json.dumps(value, sort_keys=True, ensure_ascii=False,
                              separators=(",", ":")).encode("utf-8"))


def _validate_generation_signature(value: Mapping[str, Any]) -> dict[str, Any]:
    required = ("profile_id", "profile_fingerprint", "profile_wav_sha256",
                "profile_transcript_sha256", "model", "runner_version",
                "speed", "pitch_shift", "settings")
    if not isinstance(value, Mapping) or any(key not in value for key in required):
        raise EpisodeError("TTS signature cần profile ID/fingerprint/WAV/transcript, model, "
                           "runner version, speed, pitch và settings.")
    signature = copy.deepcopy(dict(value))
    for key in ("profile_id", "model", "runner_version"):
        if not isinstance(signature[key], str) or not signature[key].strip():
            raise EpisodeError(f"TTS signature thiếu {key}.")
    for key in ("profile_fingerprint", "profile_wav_sha256", "profile_transcript_sha256"):
        if not isinstance(signature[key], str) or not re.fullmatch(r"[a-fA-F0-9]{64}", signature[key]):
            raise EpisodeError(f"TTS signature {key} phải là SHA-256.")
    try:
        signature["speed"] = float(signature["speed"])
        signature["pitch_shift"] = float(signature["pitch_shift"])
    except (TypeError, ValueError) as exc:
        raise EpisodeError("TTS signature speed/pitch không hợp lệ.") from exc
    if (not math.isfinite(signature["speed"]) or not math.isfinite(signature["pitch_shift"]) or
            not 0.5 <= signature["speed"] <= 2.0 or not 0.5 <= signature["pitch_shift"] <= 2.0 or
            not isinstance(signature["settings"], Mapping)):
        raise EpisodeError("TTS signature speed/pitch/settings không hợp lệ.")
    signature["settings"] = copy.deepcopy(dict(signature["settings"]))
    if (signature["settings"].get("tts_voice") != signature["profile_id"] or
            float(signature["settings"].get("tts_speed", signature["speed"])) != signature["speed"] or
            float(signature["settings"].get("pitch_shift", signature["pitch_shift"])) != signature["pitch_shift"]):
        raise EpisodeError("TTS signature profile/speed/pitch không khớp settings.")
    return signature


def _process_identity(pid: int) -> str | None:
    """Linux process start token, preventing accidental PID-reuse ownership."""
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
        after_name = raw[raw.rfind(")") + 2:].split()
        return after_name[19]  # proc stat field 22 (starttime), after field 2.
    except (OSError, IndexError):
        return None


def _owner() -> dict[str, Any]:
    pid = os.getpid()
    return {"host": socket.gethostname(), "pid": pid,
            "process_identity": _process_identity(pid)}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp",
                                dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _valid_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", value):
        raise EpisodeError("Mã tập chỉ được gồm chữ, số, gạch ngang và gạch dưới.")
    return value


def _slug(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return (slug or "episode")[:42].rstrip("-")


def _default_brief(topic: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "podcast_policy_version": 2,
        "topic": topic,
        "audience": "Người trưởng thành muốn thư giãn và dễ đi vào giấc ngủ",
        "goal": "Một cuộc trò chuyện nhẹ nhàng, giúp người nghe thả lỏng trước khi ngủ",
        "target_minutes": 25,
        "duration_seconds": {"min": 1200, "target": 1500, "max": 1800},
        "voice_profile": "podcas",
        "video": {"aspect_ratio": "16:9", "still_image_count": 1,
                  "subtitles": False, "background_music": False},
    }


def _normalize_brief(topic: str | None, brief: Mapping[str, Any] | None) -> dict[str, Any]:
    supplied = copy.deepcopy(dict(brief or {}))
    resolved_topic = (topic or supplied.get("topic") or supplied.get("title") or "").strip()
    if not resolved_topic:
        raise EpisodeError("Cần chủ đề hoặc brief có trường topic/title.")
    base = _default_brief(resolved_topic)
    base.update(supplied)
    base["topic"] = resolved_topic
    duration = base.get("duration_seconds")
    if isinstance(duration, Mapping):
        duration = dict(duration)
        duration.setdefault("min", 1200)
        duration.setdefault("target", 1500)
        duration.setdefault("max", 1800)
        base["duration_seconds"] = duration
    else:
        base["duration_seconds"] = {"min": 1200, "target": 1500, "max": 1800}
    try:
        target = float(base.get("target_minutes", 25))
        minimum = float(base["duration_seconds"]["min"])
        maximum = float(base["duration_seconds"]["max"])
    except (TypeError, ValueError, KeyError) as exc:
        raise EpisodeError("Brief cần target_minutes và duration_seconds hợp lệ.") from exc
    if not 20 <= target <= 30 or minimum < 1200 or maximum > 1800 or minimum >= maximum:
        raise EpisodeError("Podcast cần mục tiêu 20–30 phút và giới hạn nằm trong 1200–1800 giây.")
    video = base.setdefault("video", {})
    if not isinstance(video, dict):
        raise EpisodeError("Trường video trong brief phải là object.")
    video.setdefault("aspect_ratio", "16:9")
    video.setdefault("still_image_count", 1)
    video.setdefault("subtitles", False)
    video.setdefault("background_music", False)
    if (video["aspect_ratio"] != "16:9" or int(video["still_image_count"]) != 1 or
            bool(video["subtitles"]) or bool(video["background_music"])):
        raise EpisodeError("Video podcast cần 16:9, đúng một ảnh tĩnh, không phụ đề và không nhạc nền.")
    return base


def _words(text: str) -> int:
    return len(re.findall(r"\S+", text.strip()))


def _sentence_units(text: str) -> list[str]:
    """Split Vietnamese narration without discarding its punctuation."""
    pieces = re.split(r"(?<=[.!?…])\s+", text.strip())
    out: list[str] = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        # Very long sentences still need independently retryable TTS units.
        tokens = piece.split()
        if len(tokens) > CHUNK_MAX_SECONDS * 4:
            for start in range(0, len(tokens), CHUNK_MAX_SECONDS * 4):
                out.append(" ".join(tokens[start:start + CHUNK_MAX_SECONDS * 4]))
        else:
            out.append(piece)
    return out


def _split_chunks(script: str, estimated_wpm: float) -> list[str]:
    if not math.isfinite(estimated_wpm) or estimated_wpm <= 0:
        raise EpisodeError("estimated_wpm phải là tốc độ đọc dương do writer cung cấp.")
    target_words = max(35, int(round(estimated_wpm * CHUNK_TARGET_SECONDS / 60)))
    max_words = max(target_words + 1,
                    int(round(estimated_wpm * CHUNK_MAX_SECONDS / 60)))
    chunks: list[str] = []
    current: list[str] = []
    count = 0

    def flush() -> None:
        nonlocal current, count
        if current:
            chunks.append(" ".join(current).strip())
            current = []
            count = 0

    for paragraph in re.split(r"\n\s*\n", script.strip()):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _sentence_units(paragraph):
            size = _words(sentence)
            if size > max_words:
                flush()
                tokens = sentence.split()
                for start in range(0, len(tokens), max_words):
                    chunks.append(" ".join(tokens[start:start + max_words]))
                continue
            if current and count + size > max_words:
                flush()
            current.append(sentence)
            count += size
            if count >= target_words:
                flush()
    flush()
    return chunks


def _validate_script_payload(payload: Mapping[str, Any], brief: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise EpisodeError("Writer phải trả về object có title, topic và bốn parts.")
    parts = payload.get("parts")
    if not isinstance(parts, Sequence) or isinstance(parts, (str, bytes)) or len(parts) != 4:
        raise EpisodeError("Kịch bản phải có đúng bốn phần P01–P04.")
    target = float(payload.get("target_minutes", brief.get("target_minutes", 25)))
    if not 20 <= target <= 30:
        raise EpisodeError("target_minutes phải nằm trong khoảng 20–30.")
    try:
        wpm = float(payload["estimated_wpm"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EpisodeError("Writer cần trả về estimated_wpm đã hiệu chỉnh theo mẫu giọng.") from exc
    if not math.isfinite(wpm) or wpm <= 0:
        raise EpisodeError("estimated_wpm phải là số dương.")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(parts, 1):
        if not isinstance(raw, Mapping):
            raise EpisodeError(f"Phần P{index:02} phải là object.")
        part_id = str(raw.get("id", f"P{index:02}"))
        script = str(raw.get("script", raw.get("text", ""))).strip()
        if part_id != f"P{index:02}" or not script:
            raise EpisodeError(f"Phần {index} cần id P{index:02} và lời dẫn không rỗng.")
        title = str(raw.get("title", f"Phần {index}" )).strip()
        chunks = raw.get("chunks")
        if chunks is None:
            chunk_texts = _split_chunks(script, wpm)
        else:
            if not isinstance(chunks, Sequence) or isinstance(chunks, (str, bytes)):
                raise EpisodeError(f"chunks của {part_id} phải là danh sách văn bản.")
            chunk_texts = [str(x).strip() for x in chunks]
            if not chunk_texts or any(not x for x in chunk_texts):
                raise EpisodeError(f"chunks của {part_id} không được rỗng.")
            if " ".join(" ".join(chunk_texts).split()) != " ".join(script.split()):
                raise EpisodeError(f"Các chunks của {part_id} phải giữ đủ và đúng thứ tự lời dẫn.")
        from .direction import validate_direction
        direction = ({"voice_direction": validate_direction(raw)}
                     if "voice_direction" in raw else {})
        normalized.append({
            "id": part_id,
            "title": title,
            "script": script,
            "word_count": int(raw.get("word_count", _words(script))),
            "chunks": chunk_texts,
            **direction,
        })
    total_words = sum(_words(part["script"]) for part in normalized)
    estimated_seconds = total_words / wpm * 60
    limits = brief["duration_seconds"]
    if not float(limits["min"]) <= estimated_seconds <= float(limits["max"]):
        raise EpisodeError(
            f"Kịch bản ước tính {estimated_seconds / 60:.1f} phút theo {wpm:g} từ/phút; "
            f"brief yêu cầu {float(limits['min']) / 60:g}–{float(limits['max']) / 60:g} phút.")
    for part in normalized:
        share = _words(part["script"]) / total_words
        if not 0.12 <= share <= 0.38:
            raise EpisodeError(
                f"{part['id']} chiếm {share:.0%} tổng lời; mỗi phần cần trong khoảng 12–38% để giữ mạch kể cân đối.")
    return {
        "title": str(payload.get("title", brief.get("title", payload.get("topic", brief["topic"])))).strip(),
        "topic": str(payload.get("topic", brief["topic"])).strip(),
        "target_minutes": target,
        "estimated_wpm": wpm,
        "parts": normalized,
    }


def _file_record(project_root: Path, value: Mapping[str, Any], *, must_exist: bool = True) -> dict[str, Any]:
    raw = value.get("path") or value.get("file")
    if not isinstance(raw, str) or not raw.strip():
        raise EpisodeError("Artifact hoàn tất cần có đường dẫn path.")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = project_root / path
    path = path.resolve()
    try:
        relative = path.relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise EpisodeError("Artifact phải nằm trong thư mục dự án.") from exc
    if must_exist and not path.is_file():
        raise EpisodeError(f"Không tìm thấy artifact: {relative}")
    record = {k: copy.deepcopy(v) for k, v in value.items() if k not in ("path", "file")}
    record["path"] = relative
    if path.is_file():
        actual_hash = _digest_file(path)
        expected_hash = record.get("sha256") or record.get("wav_sha256")
        if expected_hash and expected_hash != actual_hash:
            raise EpisodeError(f"Checksum artifact không khớp: {relative}")
        record["sha256"] = actual_hash
        record["size_bytes"] = path.stat().st_size
    return record


def _wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as stream:
            rate = stream.getframerate()
            if rate <= 0:
                raise EpisodeError("Audio master WAV có sample rate không hợp lệ.")
            return stream.getnframes() / rate
    except (wave.Error, EOFError, OSError) as exc:
        raise EpisodeError(f"Không đọc được master audio WAV: {path.name}") from exc


def _mp4_probe(path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise EpisodeError("Không có ffprobe để đo thời lượng MP4 thật.")
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        kinds = {str(stream.get("codec_type")) for stream in data.get("streams", [])}
    except (subprocess.SubprocessError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise EpisodeError(f"ffprobe không đo được MP4: {path.name}") from exc
    if not math.isfinite(duration) or duration <= 0 or not {"audio", "video"}.issubset(kinds):
        raise EpisodeError("MP4 cần stream audio/video hợp lệ và thời lượng dương.")
    return duration


@dataclass(frozen=True)
class EpisodeContext:
    """Read-only handler context; mutations go through the coordinator."""

    coordinator: "Coordinator"
    episode_id: str

    @property
    def episode_dir(self) -> Path:
        return self.coordinator.episode_dir(self.episode_id)

    @property
    def project_root(self) -> Path:
        return self.coordinator.project_root

    @property
    def manifest(self) -> dict[str, Any]:
        return self.coordinator.get_manifest(self.episode_id)

    @property
    def brief(self) -> dict[str, Any]:
        return self.coordinator.read(self.episode_id, "brief")

    def artifact_path(self, relative: str) -> Path:
        path = (self.episode_dir / relative).resolve()
        if not path.is_relative_to(self.episode_dir.resolve()):
            raise EpisodeError("Đường dẫn artifact vượt khỏi thư mục tập.")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class Coordinator:
    """Process-safe episode ledger and four-part run coordinator."""

    def __init__(self, sys_root: Path | str = SYS_ROOT):
        self.sys_root = Path(sys_root).resolve()
        self.project_root = self.sys_root.parent
        self.podcast_dir = self.sys_root / "podcast"
        self.runs_dir = self.sys_root / "runs"
        self.ledger_path = self.podcast_dir / "ledger.json"
        self.lock_dir = self.podcast_dir / ".locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def episode_dir(self, episode_id: str) -> Path:
        return self.runs_dir / _valid_id(episode_id)

    @contextlib.contextmanager
    def _lock(self, episode_id: str | None = None):
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        name = "ledger" if episode_id is None else _valid_id(episode_id)
        with (self.lock_dir / f"{name}.lock").open("a+") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @contextlib.contextmanager
    def _write_lock(self, episode_id: str | None = None):
        # Lock ordering is always ledger then episode, avoiding deadlocks.
        with self._lock():
            if episode_id is None:
                yield
            else:
                with self._lock(episode_id):
                    yield

    def _manifest_path(self, episode_id: str) -> Path:
        return self.episode_dir(episode_id) / EPISODE_MANIFEST

    def _load_manifest(self, episode_id: str) -> dict[str, Any]:
        path = self._manifest_path(episode_id)
        if not path.is_file():
            raise EpisodeError(f"Không tìm thấy podcast episode: {episode_id}")
        data = _read_json(path)
        if data.get("kind") != "podcast_episode" or data.get("episode_id") != episode_id:
            raise EpisodeError(f"Thư mục {episode_id} không phải podcast episode hợp lệ.")
        return data

    def _ledger(self) -> dict[str, Any]:
        if not self.ledger_path.exists():
            return {"schema_version": 1, "episodes": {}, "reservations": {}, "events": []}
        data = _read_json(self.ledger_path)
        if data.get("schema_version") != 1 or not isinstance(data.get("episodes"), dict):
            raise EpisodeError("Ledger podcast không đúng schema; giữ nguyên file để kiểm tra.")
        data.setdefault("events", [])
        data.setdefault("reservations", {})
        return data

    def _event(self, episode_id: str, action: str, detail: Mapping[str, Any] | None = None) -> None:
        ledger = self._ledger()
        event = {"at": _utcnow(), "episode_id": episode_id,
                 "action": action, "detail": copy.deepcopy(dict(detail or {}))}
        ledger["events"].append(event)
        if len(ledger["events"]) > 5000:
            ledger["events"] = ledger["events"][-5000:]
        manifest_path = self._manifest_path(episode_id)
        if manifest_path.exists():
            manifest = _read_json(manifest_path)
            ledger["episodes"][episode_id] = {
                "episode_id": episode_id,
                "topic": manifest.get("topic"),
                "topic_id": manifest.get("topic_id"),
                "title": manifest.get("title"),
                "state": manifest.get("state"),
                "created_at": manifest.get("created_at"),
                "updated_at": manifest.get("updated_at"),
                "manifest": manifest_path.relative_to(self.sys_root).as_posix(),
            }
            event_path = self.episode_dir(episode_id) / "events.jsonl"
            with event_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        _atomic_json(self.ledger_path, ledger)

    def _save(self, manifest: dict[str, Any], action: str,
              detail: Mapping[str, Any] | None = None) -> None:
        manifest["updated_at"] = _utcnow()
        manifest["state"] = self._overall_state(manifest)
        _atomic_json(self._manifest_path(manifest["episode_id"]), manifest)
        self._event(manifest["episode_id"], action, detail)

    @staticmethod
    def _overall_state(manifest: Mapping[str, Any]) -> str:
        stages = manifest["stages"]
        if stages["video"]["state"] == "complete":
            return "complete"
        content_state = stages["content"]["state"]
        if content_state in ("failed", "ambiguous", "unsupported", "needs_attention"):
            return "needs_attention"
        if content_state != "complete":
            return "content_pending"
        audio = stages["audio"]["state"]
        if audio in ("failed", "ambiguous", "unsupported", "needs_attention"):
            return "needs_attention"
        if audio != "complete":
            return "audio_in_progress" if audio == "running" else "audio_pending"
        image = stages["image"]["state"]
        video = stages["video"]["state"]
        if image in ("failed", "ambiguous", "unsupported", "needs_attention") or video in (
                "failed", "ambiguous", "unsupported", "needs_attention"):
            return "needs_attention"
        if image != "complete":
            return "image_pending"
        return "video_pending"

    def _refresh_audio_state(self, manifest: dict[str, Any]) -> None:
        chunks = [chunk for part in manifest["parts"] for chunk in part["chunks"]]
        states = [chunk["state"] for chunk in chunks]
        audio = manifest["stages"]["audio"]
        if not chunks:
            audio["state"] = "pending"
        elif any(s in ("failed", "ambiguous", "unsupported", "needs_attention") for s in states):
            audio["state"] = next(s for s in states if s in ("ambiguous", "unsupported", "needs_attention", "failed"))
        elif any(s == "running" for s in states):
            audio["state"] = "running"
        elif not all(s == "complete" for s in states):
            audio["state"] = "pending"
        elif not audio.get("master"):
            audio["state"] = "finalize_pending"
        else:
            audio["state"] = "complete"
        for part in manifest["parts"]:
            part_states = [chunk["state"] for chunk in part["chunks"]]
            if not part_states:
                part["state"] = "pending"
            elif all(s == "complete" for s in part_states):
                part["state"] = "complete"
            elif any(s in ("failed", "ambiguous", "unsupported", "needs_attention") for s in part_states):
                part["state"] = "needs_attention"
            elif any(s == "running" for s in part_states):
                part["state"] = "running"
            else:
                part["state"] = "pending"

    def create_episode(self, topic: str | None = None,
                       brief: Mapping[str, Any] | None = None,
                       episode_id: str | None = None,
                       topic_id: str | None = None) -> dict[str, Any]:
        normalized = _normalize_brief(topic, brief)
        if episode_id is None:
            stem = f"podcast-{dt.date.today():%Y%m%d}-{_slug(normalized['topic'])}"
            episode_id = f"{stem}-{uuid.uuid4().hex[:6]}"
        episode_id = _valid_id(episode_id)
        episode_dir = self.episode_dir(episode_id)
        with self._write_lock(episode_id):
            if episode_dir.exists() or self._manifest_path(episode_id).exists():
                raise EpisodeError(f"Episode đã tồn tại: {episode_id}")
            episode_dir.mkdir(parents=True, exist_ok=False)
            (episode_dir / "briefs").mkdir()
            (episode_dir / "scripts").mkdir()
            (episode_dir / "audio" / "chunks").mkdir(parents=True)
            brief_path = episode_dir / "briefs" / "1.json"
            _atomic_json(brief_path, normalized)
            now = _utcnow()
            manifest = {
                "schema_version": 1,
                "kind": "podcast_episode",
                "episode_id": episode_id,
                "topic_id": topic_id,
                "topic": normalized["topic"],
                "title": normalized.get("title", normalized["topic"]),
                "created_at": now,
                "updated_at": now,
                "state": "content_pending",
                "target_minutes": normalized["target_minutes"],
                "brief": {"revision": 1, "path": "briefs/1.json",
                          "sha256": _digest(brief_path.read_bytes())},
                "script": {"revision": 0, "path": None, "sha256": None,
                           "estimated_wpm": None, "part_count": 4},
                "tts_generation": {"signature": None, "sha256": None},
                "parts": [{"id": part_id, "title": f"Phần {index}",
                           "state": "pending", "script_hash": None,
                           "estimated_seconds": None, "chunks": []}
                          for index, part_id in enumerate(PART_IDS, 1)],
                "stages": {
                    "content": {"state": "pending", "attempts": 0},
                    "audio": {"state": "pending", "attempts": 0, "master": None},
                    "image": {"state": "pending", "attempts": 0, "artifact": None},
                    "video": {"state": "pending", "attempts": 0, "artifact": None},
                },
                "output_dir": (Path("video") / episode_id).as_posix(),
            }
            _atomic_json(self._manifest_path(episode_id), manifest)
            self._event(episode_id, "created", {"topic": normalized["topic"]})
            return copy.deepcopy(manifest)

    def get_manifest(self, episode_id: str) -> dict[str, Any]:
        with self._lock(episode_id):
            return copy.deepcopy(self._load_manifest(episode_id))

    def _checked_brief(self, episode_id: str, manifest: Mapping[str, Any]) -> dict[str, Any]:
        record = manifest["brief"]
        path = (self.episode_dir(episode_id) / record["path"]).resolve()
        if not path.is_relative_to(self.episode_dir(episode_id).resolve()) or not path.is_file():
            raise EpisodeError("Không tìm thấy revision brief hiện tại.")
        if _digest(path.read_bytes()) != record["sha256"]:
            raise EpisodeError("BRIEF_TAMPER: brief đã lưu thay đổi ngoài coordinator.")
        return _read_json(path)

    def read(self, episode_id: str, kind: str = "manifest") -> Any:
        with self._lock(episode_id):
            manifest = self._load_manifest(episode_id)
            if kind == "manifest":
                return copy.deepcopy(manifest)
            if kind == "brief":
                return self._checked_brief(episode_id, manifest)
            if kind == "script":
                record = manifest["script"]
                if not record["path"]:
                    raise EpisodeError("Tập chưa có kịch bản.")
                path = (self.episode_dir(episode_id) / record["path"]).resolve()
                if not path.is_relative_to(self.episode_dir(episode_id).resolve()) or not path.is_file():
                    raise EpisodeError("Không tìm thấy revision kịch bản hiện tại.")
                if _digest(path.read_bytes()) != record["sha256"]:
                    raise EpisodeError("SCRIPT_TAMPER: kịch bản đã lưu thay đổi ngoài coordinator.")
                return _read_json(path)
            if kind == "events":
                path = self.episode_dir(episode_id) / "events.jsonl"
                if not path.is_file():
                    return []
                return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            raise EpisodeError("Chỉ đọc được manifest, brief, script hoặc events.")

    def set_script(self, episode_id: str, payload: Mapping[str, Any],
                   generation_signature: Mapping[str, Any] | None = None) -> dict[str, Any]:
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            brief = self._checked_brief(episode_id, manifest)
            script = _validate_script_payload(payload, brief)
            supplied_signature = generation_signature or payload.get("generation_signature")
            if supplied_signature is None:
                supplied_signature = manifest.get("tts_generation", {}).get("signature")
            signature = (_validate_generation_signature(supplied_signature)
                         if supplied_signature is not None else None)
            if int(brief.get("podcast_policy_version", 1)) >= 2:
                from .direction import locked_content
                lock_path = self.episode_dir(episode_id) / "content/locked-input.json"
                quality_path = self.episode_dir(episode_id) / "content/quality/pipeline-state.json"
                if not signature or not lock_path.is_file() or not quality_path.is_file():
                    raise EpisodeError("Cần cặp kịch bản đã duyệt và khóa trước khi tạo audio.")
                quality = _read_json(quality_path)
                if not quality.get("complete") or quality.get("pending") or quality.get("exhausted"):
                    raise EpisodeError("Nội dung chưa có quyết định đạt cuối cùng.")
                expected = _read_json(lock_path)
                if (locked_content(script, signature) != expected or
                        locked_content(quality["script"], signature) != expected):
                    raise EpisodeError("Kịch bản/giọng không khớp bản đã duyệt.")
            signature_hash = _json_digest(signature) if signature else None
            generation_key = signature_hash or f"unbound:{uuid.uuid4().hex}"
            episode_dir = self.episode_dir(episode_id)
            old_manifest = copy.deepcopy(manifest)
            previous_generation = old_manifest.get("tts_generation", {})
            generation_history = list(previous_generation.get("history", []))
            if (previous_generation.get("signature") and
                    previous_generation.get("sha256") != signature_hash):
                generation_history.append({"sha256": previous_generation.get("sha256"),
                                           "signature": copy.deepcopy(previous_generation["signature"]),
                                           "replaced_at": _utcnow()})
            old_script_record = old_manifest["script"]
            same_script = False
            if old_script_record.get("path"):
                old_script_path = episode_dir / old_script_record["path"]
                if old_script_path.is_file() and _digest_file(old_script_path) == old_script_record.get("sha256"):
                    same_script = _json_digest(_read_json(old_script_path)) == _json_digest(script)
            old_chunks = [chunk for part in manifest["parts"] for chunk in part["chunks"]]
            cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for chunk in old_chunks:
                cache.setdefault((chunk["text_hash"], chunk.get("generation_key", "")), []).append(chunk)
            revision = int(manifest["script"]["revision"]) + 1
            script_rel = f"scripts/{revision}.json"
            script_path = episode_dir / script_rel
            _atomic_json(script_path, script)
            used_ids: set[str] = set()
            new_parts: list[dict[str, Any]] = []
            for part in script["parts"]:
                part_id = part["id"]
                chunks: list[dict[str, Any]] = []
                for index, text in enumerate(part["chunks"], 1):
                    text_hash = _digest(text.encode("utf-8"))
                    candidates = cache.get((text_hash, generation_key), [])
                    reusable = candidates.pop(0) if candidates else None
                    if reusable is not None and self._chunk_artifact_valid(reusable):
                        chunk = copy.deepcopy(reusable)
                        chunk["reused_from_revision"] = manifest["script"]["revision"]
                    else:
                        chunk_id = f"{part_id}-C{index:03}"
                        suffix = 2
                        while chunk_id in used_ids:
                            chunk_id = f"{part_id}-C{index:03}-{suffix}"
                            suffix += 1
                        chunk = {
                            "id": chunk_id,
                            "sequence": index,
                            "text": text,
                            "text_hash": text_hash,
                            "generation_key": generation_key,
                            "estimated_seconds": round(_words(text) / script["estimated_wpm"] * 60, 2),
                            "state": "pending",
                            "attempts": 0,
                            "attempt_history": [],
                            "artifact": None,
                        }
                    if chunk["id"] in used_ids:
                        # A repeated identical chunk may share a cache entry; keep IDs unique.
                        chunk["id"] = f"{part_id}-C{index:03}-{text_hash[:6]}"
                    used_ids.add(chunk["id"])
                    chunk["sequence"] = index
                    chunk["text"] = text
                    chunk["text_hash"] = text_hash
                    chunk["generation_key"] = generation_key
                    chunk["estimated_seconds"] = round(_words(text) / script["estimated_wpm"] * 60, 2)
                    chunks.append(chunk)
                part_seconds = sum(chunk["estimated_seconds"] for chunk in chunks)
                new_parts.append({
                    "id": part_id,
                    "title": part["title"],
                    "state": "pending",
                    "script_hash": _digest(part["script"].encode("utf-8")),
                    "estimated_seconds": round(part_seconds, 2),
                    "chunks": chunks,
                    "script": part["script"],
                })
            manifest["parts"] = new_parts
            manifest["script"] = {"revision": revision, "path": script_rel,
                                   "sha256": _digest(script_path.read_bytes()),
                                   "estimated_wpm": script["estimated_wpm"],
                                   "part_count": 4, "title": script["title"]}
            manifest["title"] = script["title"] or manifest["title"]
            manifest["topic"] = script["topic"] or manifest["topic"]
            manifest["target_minutes"] = script["target_minutes"]
            manifest["tts_generation"] = {"signature": signature,
                                           "sha256": signature_hash,
                                           "bound_at": _utcnow() if signature else None,
                                           "history": generation_history}
            manifest["stages"]["content"].update(state="complete", attempts=manifest["stages"]["content"].get("attempts", 0))
            manifest["stages"]["content"].pop("owner", None)
            manifest["stages"]["content"].pop("error", None)
            self._refresh_audio_state(manifest)
            if manifest["stages"]["audio"]["state"] != "complete":
                manifest["stages"]["audio"]["master"] = None
            if (not same_script or
                    manifest["stages"]["audio"]["state"] != "complete"):
                manifest["stages"]["video"]["state"] = "pending"
                manifest["stages"]["video"]["artifact"] = None
            self._save(manifest, "script_saved", {"revision": revision,
                                                    "reused_chunks": sum(c["state"] == "complete" for p in new_parts for c in p["chunks"])})
            return copy.deepcopy(manifest)

    def bind_generation_signature(self, episode_id: str,
                                  generation_signature: Mapping[str, Any]) -> dict[str, Any]:
        signature = _validate_generation_signature(generation_signature)
        signature_hash = _json_digest(signature)
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            current = manifest.setdefault("tts_generation", {"signature": None, "sha256": None})
            if current.get("sha256") == signature_hash:
                return copy.deepcopy(manifest)
            history = list(current.get("history", []))
            if current.get("signature"):
                history.append({"sha256": current.get("sha256"),
                                "signature": copy.deepcopy(current["signature"]),
                                "replaced_at": _utcnow()})
            for part in manifest["parts"]:
                part["state"] = "pending"
                for chunk in part["chunks"]:
                    chunk.update(state="pending", generation_key=signature_hash,
                                 attempts=0, artifact=None, error=None)
                    chunk.pop("owner", None)
                    chunk.pop("remote_request", None)
            manifest["tts_generation"] = {"signature": signature,
                                           "sha256": signature_hash,
                                           "bound_at": _utcnow(), "history": history}
            manifest["stages"]["audio"].update(state="pending", attempts=0, master=None)
            manifest["stages"]["video"].update(state="pending", artifact=None)
            self._save(manifest, "tts_generation_changed",
                       {"signature_sha256": signature_hash})
            return copy.deepcopy(manifest)

    def _chunk_artifact_valid(self, chunk: Mapping[str, Any]) -> bool:
        artifact = chunk.get("artifact")
        if chunk.get("state") != "complete" or not isinstance(artifact, Mapping):
            return False
        path = (self.project_root / str(artifact.get("path", ""))).resolve()
        try:
            path.relative_to(self.project_root)
        except ValueError:
            return False
        if not path.is_file():
            return False
        expected = artifact.get("sha256")
        return not expected or _digest_file(path) == expected

    def set_chunk_state(self, episode_id: str, chunk_id: str, state: str,
                        detail: str = "", artifact: Mapping[str, Any] | None = None,
                        retry_failed: bool = False) -> dict[str, Any]:
        allowed = {"pending", "running", "complete", "failed", "ambiguous",
                   "unsupported", "needs_attention"}
        if state not in allowed:
            raise EpisodeError(f"Trạng thái chunk không hợp lệ: {state}")
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            chunk = next((c for p in manifest["parts"] for c in p["chunks"] if c["id"] == chunk_id), None)
            if chunk is None:
                raise EpisodeError(f"Không có subchunk {chunk_id}.")
            if state == "running":
                if chunk["state"] == "running":
                    raise EpisodeError(f"Subchunk {chunk_id} đã được một tiến trình nhận.")
                if chunk["state"] == "ambiguous":
                    raise EpisodeError(f"Subchunk {chunk_id} đang mơ hồ; cần đối chiếu yêu cầu Colab trước.")
                if chunk["state"] == "complete" and self._chunk_artifact_valid(chunk):
                    return copy.deepcopy(manifest)
                if chunk["state"] == "failed" and not retry_failed:
                    raise EpisodeError(f"Subchunk {chunk_id} lỗi; cần yêu cầu retry_failed.")
                if int(chunk.get("attempts", 0)) >= MAX_ATTEMPTS:
                    raise EpisodeError(f"Subchunk {chunk_id} đã hết {MAX_ATTEMPTS} lần thử.")
                chunk["attempts"] = int(chunk.get("attempts", 0)) + 1
                chunk["state"] = "running"
                chunk["owner"] = _owner()
                chunk["attempt_history"].append({"attempt": chunk["attempts"], "started_at": _utcnow()})
            elif state == "complete":
                if artifact is None:
                    raise EpisodeError("Chunk hoàn tất cần metadata artifact.")
                chunk["artifact"] = _file_record(self.project_root, artifact)
                chunk.pop("owner", None)
                history = chunk.setdefault("attempt_history", [])
                if history and history[-1].get("state") is None:
                    history[-1].update(state="complete", finished_at=_utcnow(), detail=detail)
                chunk["state"] = "complete"
                chunk["error"] = None
            else:
                chunk["state"] = state
                chunk.pop("owner", None)
                chunk["error"] = detail
                history = chunk.setdefault("attempt_history", [])
                if history and history[-1].get("state") is None:
                    history[-1].update(state=state, finished_at=_utcnow(), detail=detail)
            self._refresh_audio_state(manifest)
            # Any new/missing chunk invalidates the concatenated master and final video.
            manifest["stages"]["audio"]["master"] = None if manifest["stages"]["audio"]["state"] != "complete" else manifest["stages"]["audio"].get("master")
            if manifest["stages"]["audio"]["state"] != "complete":
                manifest["stages"]["audio"]["state"] = "pending" if state == "complete" else manifest["stages"]["audio"]["state"]
                manifest["stages"]["video"]["state"] = "pending"
                manifest["stages"]["video"]["artifact"] = None
            self._save(manifest, "chunk_" + state, {"chunk_id": chunk_id, "detail": detail})
            return copy.deepcopy(manifest)

    def set_chunk_remote_request(self, episode_id: str, chunk_id: str,
                                 request_id: str, detail: Mapping[str, Any] | None = None) -> None:
        """Persist a Colab request identity before waiting on its result."""
        if not request_id.strip():
            raise EpisodeError("Cần request_id để đối chiếu yêu cầu TTS từ xa.")
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            chunk = next((c for p in manifest["parts"] for c in p["chunks"] if c["id"] == chunk_id), None)
            if chunk is None:
                raise EpisodeError(f"Không có subchunk {chunk_id}.")
            if chunk["state"] != "running":
                raise EpisodeError("Chỉ ghi request_id khi subchunk đang chạy.")
            chunk["remote_request"] = {"request_id": request_id,
                                       "detail": copy.deepcopy(dict(detail or {})),
                                       "recorded_at": _utcnow()}
            self._save(manifest, "chunk_remote_request", {"chunk_id": chunk_id,
                                                           "request_id": request_id})

    def refund_unsubmitted_chunk_attempt(self, episode_id: str, chunk_id: str,
                                         expected_detail: str) -> dict[str, Any]:
        """Return a retry slot only when a local preflight failed before Colab submit.

        The exact failure detail is required, and the chunk must have no remote
        request or artifact. The history remains as an audit record.
        """
        if not expected_detail.strip():
            raise EpisodeError("Cần lỗi preflight chính xác để hoàn lại lượt chưa gửi.")
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            chunk = next((c for p in manifest["parts"] for c in p["chunks"]
                          if c["id"] == chunk_id), None)
            if chunk is None:
                raise EpisodeError(f"Không có subchunk {chunk_id}.")
            history = chunk.setdefault("attempt_history", [])
            last = history[-1] if history else None
            remote_request = chunk.get("remote_request")
            request_is_from_prior_attempt = False
            if isinstance(remote_request, Mapping) and isinstance(last, Mapping):
                try:
                    request_time = dt.datetime.fromisoformat(str(remote_request.get("recorded_at", "")))
                    attempt_time = dt.datetime.fromisoformat(str(last.get("started_at", "")))
                    request_is_from_prior_attempt = request_time < attempt_time
                except ValueError:
                    request_is_from_prior_attempt = False
            if (chunk.get("state") != "failed" or chunk.get("artifact")
                    or (remote_request and not request_is_from_prior_attempt)
                    or not isinstance(last, dict) or last.get("state") != "failed"
                    or last.get("detail") != expected_detail):
                raise EpisodeError("Chỉ hoàn lại lượt thất bại đúng lỗi preflight, chưa có request hoặc WAV.")
            attempts = int(chunk.get("attempts", 0))
            if attempts <= 0 or int(last.get("attempt", -1)) != attempts:
                raise EpisodeError("Bộ đếm lượt thử không khớp lịch sử; không thể hoàn lại an toàn.")
            now = _utcnow()
            last.update(state="not_submitted", refunded_at=now,
                        detail="Đã hoàn lượt: lỗi cục bộ trước khi gửi TTS Colab. " + expected_detail)
            chunk["attempts"] = attempts - 1
            chunk["state"] = "pending"
            chunk.pop("error", None)
            chunk.pop("owner", None)
            self._refresh_audio_state(manifest)
            self._save(manifest, "unsubmitted_attempt_refunded",
                       {"chunk_id": chunk_id, "preflight_error": expected_detail})
            return copy.deepcopy(manifest)

    def update_part_progress(self, episode_id: str, part_id: str,
                             progress: Mapping[str, Any]) -> None:
        request_id = progress.get("request_id")
        summary = {key: copy.deepcopy(progress[key]) for key in
                   ("state", "part_progress_percent", "completed_chunks", "total_chunks")
                   if key in progress}
        if request_id:
            summary["request_id"] = str(request_id)
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            part = next((p for p in manifest["parts"] if p["id"] == part_id), None)
            if part is None:
                raise EpisodeError(f"Không có part {part_id}.")
            if part.get("progress") == summary:
                return
            part["progress"] = summary
            if request_id:
                for chunk in part["chunks"]:
                    if chunk["state"] == "running" and chunk.get("remote_request", {}).get("request_id") != request_id:
                        chunk["remote_request"] = {"request_id": str(request_id),
                                                   "recorded_at": _utcnow()}
            self._save(manifest, "part_progress", {"part_id": part_id, **summary})

    def record_stage(self, episode_id: str, stage: str, result: Mapping[str, Any]) -> dict[str, Any]:
        if stage not in {"audio_finalize", "image", "video"}:
            raise EpisodeError("Stage phải là audio_finalize, image hoặc video.")
        result = dict(result)
        state = str(result.get("state", "complete"))
        allowed = {"complete", "failed", "ambiguous", "unsupported", "needs_attention"}
        if state not in allowed:
            raise EpisodeError(f"Trạng thái stage không hợp lệ: {state}")
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            self._refresh_audio_state(manifest)
            if stage == "audio_finalize":
                chunks = [c for p in manifest["parts"] for c in p["chunks"]]
                if not chunks or not all(c["state"] == "complete" for c in chunks):
                    raise EpisodeError("Chỉ được ghép master khi đủ mọi subchunk.")
                target = manifest["stages"]["audio"]
                key = "master"
            elif stage == "image":
                if manifest["stages"]["audio"]["state"] != "complete":
                    raise EpisodeError("Cần audio master trước khi ghép ảnh mặc định.")
                target = manifest["stages"]["image"]
                key = "artifact"
            else:
                if (manifest["stages"]["audio"]["state"] != "complete" or
                        manifest["stages"]["image"]["state"] != "complete"):
                    raise EpisodeError("Cần audio master và ảnh đạt trước khi xuất video.")
                target = manifest["stages"]["video"]
                key = "artifact"
            was_claimed = bool(target.get("owner"))
            target["state"] = state
            if not was_claimed:
                target["attempts"] = int(target.get("attempts", 0)) + 1
            target["error"] = result.get("detail") if state != "complete" else None
            target.pop("owner", None)
            if state == "complete":
                artifact_value = result.get("artifact") or result
                duration_value = result.get("duration_seconds")
                artifact_record = _file_record(self.project_root, artifact_value)
                artifact_path = (self.project_root / artifact_record["path"]).resolve()
                if stage in {"audio_finalize", "video"}:
                    if duration_value is None:
                        raise EpisodeError(f"{stage} cần duration_seconds đo từ artifact thật.")
                    try:
                        reported_duration = float(duration_value)
                    except (TypeError, ValueError) as exc:
                        raise EpisodeError(f"{stage} trả duration_seconds không hợp lệ.") from exc
                    if not math.isfinite(reported_duration) or reported_duration <= 0:
                        raise EpisodeError(f"{stage} trả duration_seconds không hợp lệ.")
                    brief = self._checked_brief(episode_id, manifest)
                    limits = brief["duration_seconds"]
                    if stage == "audio_finalize":
                        if artifact_path.suffix.lower() != ".wav":
                            raise EpisodeError("Audio master podcast phải là file WAV.")
                        measured_duration = _wav_duration(artifact_path)
                        if abs(measured_duration - reported_duration) > 0.1:
                            raise EpisodeError("duration_seconds không khớp thời lượng WAV đo bằng wave.")
                    else:
                        if artifact_path.suffix.lower() != ".mp4":
                            raise EpisodeError("Video podcast phải là file MP4.")
                        expected_video_dir = (self.project_root / "video" / episode_id).resolve()
                        if not artifact_path.is_relative_to(expected_video_dir):
                            raise EpisodeError(f"MP4 cần nằm trong {expected_video_dir.relative_to(self.project_root)}.")
                        measured_duration = _mp4_probe(artifact_path)
                        if abs(measured_duration - reported_duration) > 0.1:
                            raise EpisodeError("duration_seconds không khớp thời lượng MP4 đo bằng ffprobe.")
                        audio_duration = manifest["stages"]["audio"].get("master", {}).get("duration_seconds")
                        if audio_duration is None or abs(float(audio_duration) - measured_duration) > 0.1:
                            raise EpisodeError("Thời lượng MP4 phải khớp WAV master trong 0,1 giây.")
                    if not float(limits["min"]) <= measured_duration <= float(limits["max"]):
                        raise EpisodeError(f"Thời lượng {measured_duration:.2f}s nằm ngoài brief "
                                           f"({limits['min']}–{limits['max']}s).")
                    artifact_record["duration_seconds"] = measured_duration
                    artifact_record["reported_duration_seconds"] = reported_duration
                if stage == "image" and int(self._checked_brief(episode_id, manifest).get("podcast_policy_version", 1)) >= 2:
                    from .still import selected_still
                    _, selected = selected_still(self.sys_root)
                    if result.get("source") != "user_selected" or artifact_record["sha256"] != selected["sha256"]:
                        raise EpisodeError("Video phải dùng đúng ảnh mặc định người dùng đã chọn.")
                target[key] = artifact_record
            elif stage == "audio_finalize":
                target[key] = None
            elif key in target:
                target[key] = None
            self._save(manifest, stage + "_" + state,
                       {"detail": result.get("detail", "")})
            return copy.deepcopy(manifest)

    def resolve_stage(self, episode_id: str, stage: str, state: str,
                      detail: str = "", result: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Apply an explicit reconciliation result without silently resubmitting work."""
        if stage not in {"content", "audio_finalize", "image", "video"}:
            raise EpisodeError("Stage đối chiếu không hợp lệ.")
        if state == "complete":
            if result is None:
                raise EpisodeError("Kết quả complete cần payload hoặc artifact.")
            if stage == "content":
                return self.set_script(episode_id, result)
            return self.record_stage(episode_id, stage, result)
        if state not in {"pending", "failed", "ambiguous", "unsupported", "needs_attention"}:
            raise EpisodeError("Trạng thái đối chiếu không hợp lệ.")
        stage_key = "audio" if stage == "audio_finalize" else stage
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            target = manifest["stages"][stage_key]
            target["state"] = state
            target["error"] = detail or None
            target.pop("owner", None)
            if stage == "audio_finalize":
                target["master"] = None
            elif stage in {"image", "video"}:
                target["artifact"] = None
            self._save(manifest, stage + "_reconciled_" + state,
                       {"detail": detail})
            return copy.deepcopy(manifest)

    def next_action(self, episode_id: str) -> dict[str, Any]:
        return self._next_action_from_manifest(self.get_manifest(episode_id))

    def _next_action_from_manifest(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        episode_id = str(manifest["episode_id"])
        if manifest["stages"]["content"]["state"] != "complete":
            if manifest["stages"]["content"]["state"] == "running":
                return {"stage": "content", "action": "wait_for_content",
                        "episode_id": episode_id}
            if manifest["stages"]["content"]["state"] == "ambiguous":
                return {"stage": "content", "action": "reconcile_content",
                        "episode_id": episode_id}
            if manifest["stages"]["content"]["state"] == "failed":
                if int(manifest["stages"]["content"].get("attempts", 0)) >= MAX_ATTEMPTS:
                    return {"stage": "content", "action": "needs_attention",
                            "episode_id": episode_id, "reason": "maximum attempts reached"}
                return {"stage": "content", "action": "retry_content",
                        "episode_id": episode_id}
            if manifest["stages"]["content"]["state"] in ("unsupported", "needs_attention"):
                return {"stage": "content", "action": "resolve_content",
                        "episode_id": episode_id}
            return {"stage": "content", "action": "write_script", "episode_id": episode_id}
        if not manifest.get("tts_generation", {}).get("sha256"):
            return {"stage": "audio", "action": "verify_tts_generation_signature",
                    "episode_id": episode_id}
        for part in manifest["parts"]:
            for chunk in part["chunks"]:
                if chunk["state"] == "complete" and not self._chunk_artifact_valid(chunk):
                    if int(chunk.get("attempts", 0)) >= MAX_ATTEMPTS:
                        return {"stage": "audio", "action": "needs_attention",
                                "episode_id": episode_id, "part_id": part["id"],
                                "chunk_id": chunk["id"], "reason": "maximum attempts reached"}
                    return {"stage": "audio", "action": "restore_chunk",
                            "episode_id": episode_id, "part_id": part["id"],
                            "chunk_id": chunk["id"], "text_hash": chunk["text_hash"]}
                if chunk["state"] in ("pending", "failed"):
                    if int(chunk.get("attempts", 0)) >= MAX_ATTEMPTS:
                        return {"stage": "audio", "action": "needs_attention",
                                "episode_id": episode_id, "part_id": part["id"],
                                "chunk_id": chunk["id"], "reason": "maximum attempts reached"}
                    return {"stage": "audio", "action": "synthesize_chunk",
                            "episode_id": episode_id, "part_id": part["id"],
                            "chunk_id": chunk["id"], "chunk_state": chunk["state"],
                            "text_hash": chunk["text_hash"]}
                if chunk["state"] in ("ambiguous", "unsupported", "needs_attention"):
                    return {"stage": "audio", "action": "resolve_chunk",
                            "episode_id": episode_id, "part_id": part["id"],
                            "chunk_id": chunk["id"], "chunk_state": chunk["state"]}
                if chunk["state"] == "running":
                    return {"stage": "audio", "action": "wait_for_chunk",
                            "episode_id": episode_id, "part_id": part["id"],
                            "chunk_id": chunk["id"]}
        audio = manifest["stages"]["audio"]
        if audio["state"] != "complete":
            if audio["state"] == "running":
                return {"stage": "audio", "action": "wait_for_finalize",
                        "episode_id": episode_id}
            if audio["state"] == "ambiguous":
                return {"stage": "audio", "action": "reconcile_audio",
                        "episode_id": episode_id}
            if audio["state"] in ("unsupported", "needs_attention") or int(audio.get("attempts", 0)) >= MAX_ATTEMPTS:
                return {"stage": "audio", "action": "resolve_audio",
                        "episode_id": episode_id}
            return {"stage": "audio", "action": "finalize_audio", "episode_id": episode_id}
        if manifest["stages"]["image"]["state"] != "complete":
            if manifest["stages"]["image"]["state"] == "running":
                return {"stage": "image", "action": "wait_for_image", "episode_id": episode_id}
            if manifest["stages"]["image"]["state"] == "ambiguous":
                return {"stage": "image", "action": "reconcile_image", "episode_id": episode_id}
            if (manifest["stages"]["image"]["state"] in ("unsupported", "needs_attention") or
                    int(manifest["stages"]["image"].get("attempts", 0)) >= MAX_ATTEMPTS):
                return {"stage": "image", "action": "resolve_image", "episode_id": episode_id}
            return {"stage": "image", "action": "use_selected_still", "episode_id": episode_id}
        if manifest["stages"]["video"]["state"] != "complete":
            if manifest["stages"]["video"]["state"] == "running":
                return {"stage": "video", "action": "wait_for_export", "episode_id": episode_id}
            if manifest["stages"]["video"]["state"] == "ambiguous":
                return {"stage": "video", "action": "reconcile_export", "episode_id": episode_id}
            if (manifest["stages"]["video"]["state"] in ("unsupported", "needs_attention") or
                    int(manifest["stages"]["video"].get("attempts", 0)) >= MAX_ATTEMPTS):
                return {"stage": "video", "action": "resolve_export", "episode_id": episode_id}
            return {"stage": "video", "action": "export_mp4", "episode_id": episode_id}
        return {"stage": "complete", "action": "none", "episode_id": episode_id}

    def status(self, episode_id: str) -> dict[str, Any]:
        manifest = self.get_manifest(episode_id)
        return self._status_from_manifest(manifest)

    def _status_from_manifest(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        episode_id = str(manifest["episode_id"])
        chunks = [c for p in manifest["parts"] for c in p["chunks"]]
        counts: dict[str, int] = {}
        for chunk in chunks:
            counts[chunk["state"]] = counts.get(chunk["state"], 0) + 1
        return {
            "episode_id": episode_id,
            "topic": manifest["topic"],
            "state": self._overall_state(manifest),
            "target_minutes": manifest["target_minutes"],
            "script_revision": manifest["script"]["revision"],
            "parts": [{"id": p["id"], "title": p["title"], "state": p["state"],
                       "chunks": len(p["chunks"]),
                       "complete_chunks": sum(c["state"] == "complete" for c in p["chunks"]),
                       "estimated_seconds": p.get("estimated_seconds"),
                       "progress": copy.deepcopy(p.get("progress"))}
                      for p in manifest["parts"]],
            "chunk_counts": counts,
            "stages": copy.deepcopy(manifest["stages"]),
            "next": self._next_action_from_manifest(manifest),
        }

    def list_episodes(self) -> list[dict[str, Any]]:
        with self._lock():
            ledger = self._ledger()
            rows = list(ledger["episodes"].values())
        return sorted(rows, key=lambda row: row.get("created_at", ""), reverse=True)

    def _catalog(self) -> list[dict[str, Any]]:
        path = self.podcast_dir / "catalog.json"
        if not path.is_file():
            return []
        data = _read_json(path)
        topics = data.get("topics") if isinstance(data, Mapping) else None
        if data.get("schema_version") != 1 or not isinstance(topics, list):
            raise EpisodeError("Catalog podcast sai schema.")
        ids: set[str] = set()
        for topic in topics:
            if not isinstance(topic, dict) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", str(topic.get("id", ""))):
                raise EpisodeError("Catalog có topic thiếu id hợp lệ.")
            if topic["id"] in ids or not str(topic.get("title", "")).strip():
                raise EpisodeError("Catalog có id trùng hoặc topic thiếu title.")
            ids.add(topic["id"])
        return topics

    def next_topics(self, count: int = 10) -> list[dict[str, Any]]:
        count = max(0, min(int(count), 50))
        with self._lock():
            ledger = self._ledger()
            reservations = ledger["reservations"]
            candidates = []
            for topic in self._catalog():
                record = reservations.get(topic["id"], {})
                if record.get("status") in {"reserved", "starting", "started", "done"}:
                    continue
                candidates.append(copy.deepcopy(topic))
        candidates.sort(key=lambda item: (item.get("editorial_order", 999999), item["id"]))
        return candidates[:count]

    def show_topic(self, topic_id: str) -> dict[str, Any]:
        with self._lock():
            catalog = self._catalog()
            topic = next((item for item in catalog if item["id"] == topic_id), None)
            if topic is None:
                raise EpisodeError(f"Không có mã chủ đề: {topic_id}")
            ledger = self._ledger()
            episodes = [copy.deepcopy(item) for item in ledger["episodes"].values()
                        if item.get("topic_id") == topic_id]
            return {"topic": copy.deepcopy(topic),
                    "reservation": copy.deepcopy(ledger["reservations"].get(topic_id)),
                    "episodes": episodes}

    def reserve_topic(self, topic_id: str, episode_id: str) -> dict[str, Any]:
        episode_id = _valid_id(episode_id)
        with self._write_lock():
            topic = next((item for item in self._catalog() if item["id"] == topic_id), None)
            if topic is None:
                raise EpisodeError(f"Không có mã chủ đề: {topic_id}")
            ledger = self._ledger()
            existing = ledger["reservations"].get(topic_id, {})
            if existing.get("status") in {"reserved", "starting", "started", "done"}:
                raise EpisodeError(f"Chủ đề {topic_id} đang được giữ hoặc đã hoàn tất.")
            if episode_id in ledger["episodes"] or self.episode_dir(episode_id).exists():
                raise EpisodeError(f"Episode đã tồn tại: {episode_id}")
            if any(r.get("episode_id") == episode_id and r.get("status") in {"reserved", "starting", "started"}
                   for r in ledger["reservations"].values()):
                raise EpisodeError(f"Episode {episode_id} đã được giữ cho chủ đề khác.")
            reservation = {"topic_id": topic_id, "title": topic["title"],
                           "episode_id": episode_id, "status": "reserved",
                           "reserved_at": _utcnow()}
            ledger["reservations"][topic_id] = reservation
            ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                     "action": "topic_reserved", "topic_id": topic_id})
            _atomic_json(self.ledger_path, ledger)
            return copy.deepcopy(reservation)

    def start_reserved(self, episode_id: str, brief_overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
        episode_id = _valid_id(episode_id)
        reservation: dict[str, Any] | None = None
        with self._write_lock():
            ledger = self._ledger()
            pair = next(((topic_id, value) for topic_id, value in ledger["reservations"].items()
                         if value.get("episode_id") == episode_id), None)
            if pair is None:
                raise EpisodeError(f"Episode {episode_id} chưa giữ chủ đề trong catalog.")
            topic_id, reservation = pair
            if reservation.get("status") == "done":
                raise EpisodeError(f"Episode {episode_id} đã hoàn tất.")
            if reservation.get("status") == "released":
                raise EpisodeError(f"Giữ chỗ cho episode {episode_id} đã được giải phóng.")
            if reservation.get("status") == "started":
                if self._manifest_path(episode_id).is_file():
                    return self.get_manifest(episode_id)
                raise EpisodeError("Reservation đã start nhưng thiếu manifest episode.")
            if reservation.get("status") == "starting" and not self._manifest_path(episode_id).is_file():
                if self._owner_is_alive(reservation.get("owner")):
                    raise EpisodeError("Episode đang được start ở một tiến trình khác.")
                reservation["status"] = "reserved"
            reservation = copy.deepcopy(reservation)
            reservation["status"] = "starting"
            reservation["starting_at"] = _utcnow()
            reservation["owner"] = _owner()
            ledger["reservations"][topic_id] = reservation
            ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                     "action": "topic_starting", "topic_id": topic_id})
            _atomic_json(self.ledger_path, ledger)
        existing_manifest = self._manifest_path(episode_id)
        try:
            if existing_manifest.is_file():
                manifest = self.get_manifest(episode_id)
                if manifest.get("topic_id") != reservation["topic_id"]:
                    raise EpisodeError("Episode đã tồn tại nhưng không khớp topic reservation.")
            else:
                topic = next(item for item in self._catalog() if item["id"] == reservation["topic_id"])
                manifest = self.create_episode(topic=topic["title"], episode_id=episode_id,
                                               topic_id=reservation["topic_id"], brief=brief_overrides)
        except Exception:
            with self._write_lock():
                ledger = self._ledger()
                row = ledger["reservations"].get(reservation["topic_id"])
                if row and row.get("episode_id") == episode_id and row.get("status") == "starting":
                    row["status"] = "reserved"
                    row.pop("starting_at", None)
                    row.pop("owner", None)
                    ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                             "action": "topic_start_failed", "topic_id": reservation["topic_id"]})
                    _atomic_json(self.ledger_path, ledger)
            raise
        with self._write_lock():
            ledger = self._ledger()
            row = ledger["reservations"].get(reservation["topic_id"])
            if row and row.get("episode_id") == episode_id:
                row["status"] = "started"
                row["started_at"] = _utcnow()
                row.pop("owner", None)
                ledger["episodes"][episode_id]["state"] = manifest["state"]
                ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                         "action": "topic_started", "topic_id": reservation["topic_id"]})
                _atomic_json(self.ledger_path, ledger)
        return manifest

    def mark_done(self, episode_id: str) -> dict[str, Any]:
        episode_id = _valid_id(episode_id)
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            if self._status_from_manifest(manifest)["state"] != "complete":
                raise EpisodeError("Chỉ được mark khi Coordinator.status() là complete.")
            ledger = self._ledger()
            row = ledger["episodes"].setdefault(episode_id, {
                "episode_id": episode_id,
                "manifest": self._manifest_path(episode_id).relative_to(self.sys_root).as_posix()})
            topic_id = manifest.get("topic_id")
            reservation = ledger["reservations"].get(topic_id) if topic_id else None
            if row.get("state") == "complete" and (not reservation or reservation.get("status") == "done"):
                return copy.deepcopy(row)
            row.update(state="complete", completed_at=_utcnow(), topic=manifest["topic"],
                       title=manifest["title"], topic_id=topic_id,
                       updated_at=manifest["updated_at"])
            if reservation and reservation.get("episode_id") == episode_id:
                reservation["status"] = "done"
                reservation["completed_at"] = _utcnow()
            ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                     "action": "episode_done", "topic_id": topic_id})
            _atomic_json(self.ledger_path, ledger)
            return copy.deepcopy(row)

    def release_reservation(self, episode_id: str, note: str) -> dict[str, Any]:
        episode_id = _valid_id(episode_id)
        if not note.strip():
            raise EpisodeError("Cần ghi chú khi giải phóng chủ đề.")
        with self._write_lock(episode_id):
            ledger = self._ledger()
            pair = next(((topic_id, value) for topic_id, value in ledger["reservations"].items()
                         if value.get("episode_id") == episode_id), None)
            if pair is None:
                raise EpisodeError(f"Episode {episode_id} không có reservation.")
            topic_id, reservation = pair
            if reservation.get("status") == "done":
                raise EpisodeError("Không thể giải phóng chủ đề đã mark done.")
            if reservation.get("status") == "starting":
                raise EpisodeError("Không thể release khi start đang tạo episode.")
            manifest_path = self._manifest_path(episode_id)
            if manifest_path.is_file() and self._overall_state(self._load_manifest(episode_id)) == "complete":
                raise EpisodeError("Episode đã hoàn tất; dùng mark thay vì release.")
            reservation["status"] = "released"
            reservation["released_at"] = _utcnow()
            reservation["release_note"] = note.strip()
            ledger["events"].append({"at": _utcnow(), "episode_id": episode_id,
                                     "action": "topic_released", "topic_id": topic_id,
                                     "note": note.strip()})
            _atomic_json(self.ledger_path, ledger)
            return copy.deepcopy(reservation)

    def _claim_stage(self, episode_id: str, stage: str, retry_failed: bool = False) -> bool:
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            target = manifest["stages"][stage]
            if target["state"] == "complete":
                return False
            if target["state"] in ("running", "ambiguous", "unsupported", "needs_attention"):
                return False
            if target["state"] == "failed" and not retry_failed:
                return False
            limit = MAX_ATTEMPTS
            if int(target.get("attempts", 0)) >= limit:
                return False
            target["state"] = "running"
            target["attempts"] = int(target.get("attempts", 0)) + 1
            target["started_at"] = _utcnow()
            target["owner"] = _owner()
            self._save(manifest, stage + "_running")
            return True

    @staticmethod
    def _owner_is_alive(owner: Mapping[str, Any] | None) -> bool:
        if not isinstance(owner, Mapping) or owner.get("host") != socket.gethostname():
            return True
        try:
            pid = int(owner["pid"])
        except (KeyError, TypeError, ValueError):
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        expected = owner.get("process_identity")
        actual = _process_identity(pid)
        return not (expected and actual and expected != actual)

    def recover_abandoned(self, episode_id: str) -> list[str]:
        """Mark dead local workers ambiguous; never resubmit their remote work."""
        changed: list[str] = []
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            for part in manifest["parts"]:
                for chunk in part["chunks"]:
                    if chunk["state"] == "running" and not self._owner_is_alive(chunk.get("owner")):
                        chunk["state"] = "ambiguous"
                        chunk["error"] = "Local worker ended; reconcile the Colab request before retrying."
                        chunk.pop("owner", None)
                        history = chunk.setdefault("attempt_history", [])
                        if history and history[-1].get("state") is None:
                            history[-1].update(state="ambiguous", finished_at=_utcnow(),
                                               detail=chunk["error"])
                        changed.append(chunk["id"])
            for stage_name in ("content", "audio", "image", "video"):
                stage = manifest["stages"][stage_name]
                if stage["state"] == "running" and not self._owner_is_alive(stage.get("owner")):
                    stage["state"] = "ambiguous"
                    stage["error"] = "Local worker ended; inspect the remote result before retrying."
                    stage.pop("owner", None)
                    changed.append(stage_name)
            if changed:
                self._refresh_audio_state(manifest)
                self._save(manifest, "abandoned_work_reconciled", {"units": changed})
        return changed

    def _reconcile_stage(self, episode_id: str, stage: str,
                         handler: Callable[..., Any], context: EpisodeContext) -> dict[str, Any]:
        result = dict(handler(context, self.get_manifest(episode_id)) or {})
        state = str(result.get("state", "ambiguous"))
        payload = result.get("script", result) if stage == "content" else result
        return self.resolve_stage(episode_id, stage, state,
                                  str(result.get("detail", "")), payload)

    @staticmethod
    def _handler_generation_signature(handlers: Mapping[str, Any],
                                      context: EpisodeContext) -> dict[str, Any] | None:
        provider = handlers.get("generation_signature")
        if provider is None:
            for key in ("audio_part", "audio_chunk", "reconcile_audio_part"):
                owner = getattr(handlers.get(key), "__self__", None)
                candidate = getattr(owner, "generation_signature", None)
                if candidate is not None:
                    provider = candidate
                    break
        if provider is None:
            return None
        if isinstance(provider, Mapping):
            return _validate_generation_signature(provider)
        if not callable(provider):
            raise EpisodeError("generation_signature cần object hoặc callable.")
        try:
            signature = inspect.signature(provider)
            required = [p for p in signature.parameters.values()
                        if p.default is inspect.Parameter.empty and
                        p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                   inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        except (TypeError, ValueError):
            required = []
        value = provider(context) if required else provider()
        return _validate_generation_signature(value)

    def _apply_tts_progress(self, episode_id: str, part_id: str,
                            progress: Mapping[str, Any]) -> None:
        for chunk_info in progress.get("chunks", []):
            if not isinstance(chunk_info, Mapping):
                continue
            chunk_id = chunk_info.get("chunk_id", chunk_info.get("id"))
            state = str(chunk_info.get("state", ""))
            path = chunk_info.get("path")
            if (chunk_id and str(chunk_id).startswith(part_id + "-") and path and
                    state in {"succeeded", "success", "complete"}):
                try:
                    self.set_chunk_state(episode_id, str(chunk_id), "complete",
                                         "WAV xác thực từ tiến độ Colab.", chunk_info)
                except EpisodeError:
                    # The final response is checked again before the part is accepted.
                    pass
        for part_info in progress.get("parts", []):
            if not isinstance(part_info, Mapping) or part_info.get("part_id") != part_id:
                continue
            remote = part_info.get("remote_progress") or {}
            summary = {
                "state": part_info.get("state"),
                "part_progress_percent": remote.get("progress_percent",
                                                       progress.get("part_progress_percent", 0)),
                "completed_chunks": remote.get("completed_chunks", 0),
                "total_chunks": remote.get("total_chunks", 0),
            }
            if part_info.get("request_id"):
                summary["request_id"] = part_info["request_id"]
            self.update_part_progress(episode_id, part_id, summary)

    @staticmethod
    def _invoke_audio_part(handler: Callable[..., Any], context: EpisodeContext,
                           part: Mapping[str, Any], chunks: list[dict[str, Any]],
                           progress_callback: Callable[[Mapping[str, Any]], None],
                           retry_failed: bool) -> Any:
        try:
            parameters = inspect.signature(handler).parameters.values()
            accepts_retry = any(p.name == "retry_failed" or p.kind == inspect.Parameter.VAR_KEYWORD
                                for p in parameters)
        except (TypeError, ValueError):
            accepts_retry = False
        kwargs = {"retry_failed": retry_failed} if accepts_retry else {}
        return handler(context, dict(part), chunks, progress_callback, **kwargs)

    def run_episode(self, episode_id: str,
                    handlers: Mapping[str, Callable[..., Any]] | None = None,
                    *, retry_failed: bool = False) -> dict[str, Any]:
        episode_id = _valid_id(episode_id)
        self.get_manifest(episode_id)
        with (self.episode_dir(episode_id) / "run.lock").open("a+") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {"status": "waiting", "error": "Episode đang chạy ở tiến trình khác.",
                        "next": self.next_action(episode_id)}
            return self._run_episode(episode_id, handlers, retry_failed=retry_failed)

    def _run_episode(self, episode_id: str,
                    handlers: Mapping[str, Callable[..., Any]] | None = None,
                    *, retry_failed: bool = False) -> dict[str, Any]:
        """Run available handlers in order; completed units are always reused.

        Handler signatures are `content(ctx) -> writer payload`,
        `audio_part(ctx, part, full_ordered_chunks, progress_callback, retry_failed=False)`,
        optional `reconcile_audio_part` with the same signature, or the per-chunk
        fallback `audio_chunk(ctx, part, chunk)`. Part handlers always receive the
        full ordered chunk list so Colab request hashes remain stable on resume.
        Supply `generation_signature` as a mapping or callable; it must include
        the approved profile ID/fingerprint/reference hashes, model and runner
        version, speed, pitch, and settings. `audio_finalize` and `video` results
        must include `duration_seconds` measured from their real files (WAV via
        `wave`, MP4 via `ffprobe`). Results may set state to failed, ambiguous,
        unsupported, or needs_attention; complete results must point to existing files.
        """
        handlers = dict(handlers or {})
        self.recover_abandoned(episode_id)
        context = EpisodeContext(self, episode_id)
        if handlers.get("preflight"):
            try:
                readiness = handlers["preflight"](context)
            except Exception as exc:
                return {"status": "needs_attention", "error": str(exc), "next": self.next_action(episode_id)}
            if not readiness.get("ready"):
                return {"status": "needs_attention", "preflight": readiness,
                        "next": self.next_action(episode_id)}
        try:
            generation_signature = self._handler_generation_signature(handlers, context)
        except Exception as exc:
            return {"status": "failed", "error": str(exc),
                    "next": self.next_action(episode_id)}
        manifest = self.get_manifest(episode_id)
        if (manifest["stages"]["content"]["state"] == "ambiguous" and
                handlers.get("reconcile_content")):
            try:
                self._reconcile_stage(episode_id, "content", handlers["reconcile_content"], context)
            except Exception as exc:
                return {"status": "needs_attention", "error": str(exc),
                        "next": self.next_action(episode_id)}
            manifest = self.get_manifest(episode_id)
        if manifest["stages"]["content"]["state"] != "complete":
            if manifest["stages"]["content"]["state"] in ("ambiguous", "unsupported", "needs_attention", "running"):
                return {"status": "waiting", "next": self.next_action(episode_id)}
            handler = handlers.get("content")
            if handler is None:
                return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
            if not self._claim_stage(episode_id, "content", retry_failed):
                return {"status": "waiting", "next": self.next_action(episode_id)}
            try:
                result = handler(context)
                if isinstance(result, Mapping) and result.get("state") in {
                        "failed", "ambiguous", "unsupported", "needs_attention"}:
                    self.resolve_stage(episode_id, "content", str(result["state"]),
                                       str(result.get("detail", "")))
                    return {"status": result["state"], "next": self.next_action(episode_id)}
                payload = result.get("script", result) if isinstance(result, Mapping) else result
                self.set_script(episode_id, payload, generation_signature=generation_signature)
            except Exception as exc:
                self._finish_stage_error(episode_id, "content", exc)
                return {"status": "failed", "error": str(exc), "next": self.next_action(episode_id)}
        manifest = self.get_manifest(episode_id)
        has_audio_handler = bool(handlers.get("audio_part") or handlers.get("audio_chunk") or
                                 handlers.get("reconcile_audio_part"))
        if has_audio_handler and generation_signature is None:
            return {"status": "waiting_for_signature",
                    "next": self.next_action(episode_id)}
        if generation_signature is not None:
            try:
                self.bind_generation_signature(episode_id, generation_signature)
            except Exception as exc:
                return {"status": "failed", "error": str(exc),
                        "next": self.next_action(episode_id)}
            manifest = self.get_manifest(episode_id)
        audio_part_handler = handlers.get("audio_part")
        audio_chunk_handler = handlers.get("audio_chunk")
        if (audio_part_handler is None and audio_chunk_handler is None and
                handlers.get("reconcile_audio_part") is None and any(
                c["state"] != "complete" or not self._chunk_artifact_valid(c)
                for p in manifest["parts"] for c in p["chunks"])):
            return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
        for part_snapshot in manifest["parts"]:
            current = self.get_manifest(episode_id)
            part_snapshot = next(p for p in current["parts"] if p["id"] == part_snapshot["id"])
            part_reconcile = (any(c["state"] == "ambiguous" for c in part_snapshot["chunks"])
                              and handlers.get("reconcile_audio_part"))
            if not part_reconcile:
                for chunk_snapshot in part_snapshot["chunks"]:
                    if chunk_snapshot["state"] != "ambiguous" or not handlers.get("reconcile_chunk"):
                        continue
                    try:
                        result = dict(handlers["reconcile_chunk"](
                            context, copy.deepcopy(part_snapshot), copy.deepcopy(chunk_snapshot)) or {})
                        resolved = str(result.get("state", "ambiguous"))
                        if resolved == "complete":
                            self.set_chunk_state(episode_id, chunk_snapshot["id"], "complete",
                                                 str(result.get("detail", "")),
                                                 result.get("artifact") or result)
                        elif resolved in ("pending", "failed", "unsupported", "needs_attention"):
                            self.set_chunk_state(episode_id, chunk_snapshot["id"], resolved,
                                                 str(result.get("detail", "")))
                        else:
                            return {"status": "ambiguous", "next": self.next_action(episode_id)}
                    except Exception as exc:
                        return {"status": "needs_attention", "error": str(exc),
                                "next": self.next_action(episode_id)}
            current = self.get_manifest(episode_id)
            live_part = next(p for p in current["parts"] if p["id"] == part_snapshot["id"])
            blocked = next((c for c in live_part["chunks"]
                            if c["state"] in ("unsupported", "needs_attention", "running") or
                            (c["state"] == "ambiguous" and not part_reconcile)), None)
            if blocked:
                return {"status": "waiting", "next": self.next_action(episode_id)}
            work = [c for c in live_part["chunks"]
                    if c["state"] != "complete" or not self._chunk_artifact_valid(c)]
            if not work:
                continue
            if any(c["state"] == "failed" for c in work) and not retry_failed and not part_reconcile:
                return {"status": "waiting", "next": self.next_action(episode_id)}
            handler = (handlers.get("reconcile_audio_part") if part_reconcile
                       else (audio_part_handler or audio_chunk_handler))
            if handler is None:
                return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
            claimed: list[str] = []
            try:
                for chunk in work:
                    if chunk["state"] == "ambiguous" and part_reconcile:
                        claimed.append(chunk["id"])
                        continue
                    self.set_chunk_state(episode_id, chunk["id"], "running",
                                         retry_failed=retry_failed)
                    claimed.append(chunk["id"])
            except EpisodeError as exc:
                return {"status": "waiting", "error": str(exc),
                        "next": self.next_action(episode_id)}
            current = self.get_manifest(episode_id)
            live_part = next(p for p in current["parts"] if p["id"] == part_snapshot["id"])
            live_chunks = [c for c in live_part["chunks"] if c["id"] in claimed]
            try:
                if audio_part_handler or part_reconcile:
                    # Keep the full ordered part list so the remote request hash stays
                    # stable on resume; only unfinished chunks are claimed locally.
                    requested = [{"id": c["id"], "chunk_id": c["id"],
                                  "text": c["text"], "text_hash": c["text_hash"],
                                  "estimated_seconds": c["estimated_seconds"]}
                                 for c in live_part["chunks"]]
                    def progress_callback(progress: Mapping[str, Any]) -> None:
                        self._apply_tts_progress(episode_id, live_part["id"], progress)
                    result = self._invoke_audio_part(
                        handler, context, live_part, requested,
                        progress_callback, retry_failed)
                    result = dict(result or {})
                    response_state = str(result.get("status", result.get("state", "success")))
                    returned = result.get("chunks", [])
                    by_id = {str(item.get("chunk_id", item.get("id"))): item
                             for item in returned if isinstance(item, Mapping)}
                    for chunk_id in claimed:
                        now = self.get_manifest(episode_id)
                        saved = next(c for p in now["parts"] for c in p["chunks"] if c["id"] == chunk_id)
                        if saved["state"] == "complete" and self._chunk_artifact_valid(saved):
                            continue
                        item = by_id.get(chunk_id)
                        if item and item.get("path") and item.get("state", "succeeded") in {
                                "succeeded", "success", "complete"}:
                            self.set_chunk_state(episode_id, chunk_id, "complete",
                                                 "Colab WAV đã tải và kiểm tra.", item)
                        elif response_state in {"ambiguous", "interrupted", "queued", "running"}:
                            self.set_chunk_state(episode_id, chunk_id, "ambiguous",
                                                 str(result.get("error", "Colab request chưa được đối chiếu.")))
                        else:
                            self.set_chunk_state(episode_id, chunk_id, "failed",
                                                 str(result.get("error", "Không nhận được WAV hợp lệ cho subchunk.")))
                    if response_state not in {"success", "succeeded", "complete"}:
                        return {"status": "ambiguous" if response_state in {"ambiguous", "interrupted", "queued", "running"} else "failed",
                                "next": self.next_action(episode_id)}
                else:
                    for chunk in live_chunks:
                        result = dict(audio_chunk_handler(
                            context, copy.deepcopy(live_part), copy.deepcopy(chunk)) or {})
                        state = str(result.get("state", "complete"))
                        if state == "complete":
                            self.set_chunk_state(episode_id, chunk["id"], "complete",
                                                 str(result.get("detail", "")),
                                                 result.get("artifact") or result)
                        else:
                            self.set_chunk_state(episode_id, chunk["id"], state,
                                                 str(result.get("detail", "")))
                            if state != "complete":
                                return {"status": state, "next": self.next_action(episode_id)}
            except Exception as exc:
                failure_state = "ambiguous" if "Ambiguous" in type(exc).__name__ else "failed"
                for chunk_id in claimed:
                    try:
                        current = self.get_manifest(episode_id)
                        saved = next(c for p in current["parts"] for c in p["chunks"] if c["id"] == chunk_id)
                        if saved["state"] == "running":
                            self.set_chunk_state(episode_id, chunk_id, failure_state, str(exc))
                    except EpisodeError:
                        pass
                return {"status": failure_state, "error": str(exc),
                        "next": self.next_action(episode_id)}
        manifest = self.get_manifest(episode_id)
        if manifest["stages"]["audio"]["state"] != "complete":
            if (manifest["stages"]["audio"]["state"] == "ambiguous" and
                    handlers.get("reconcile_audio_finalize")):
                try:
                    self._reconcile_stage(episode_id, "audio_finalize",
                                          handlers["reconcile_audio_finalize"], context)
                except Exception as exc:
                    return {"status": "needs_attention", "error": str(exc),
                            "next": self.next_action(episode_id)}
                manifest = self.get_manifest(episode_id)
            if manifest["stages"]["audio"]["state"] in ("ambiguous", "unsupported", "needs_attention", "running"):
                return {"status": "waiting", "next": self.next_action(episode_id)}
        if self.get_manifest(episode_id)["stages"]["audio"]["state"] != "complete":
            handler = handlers.get("audio_finalize")
            if handler is None:
                return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
            if not self._claim_stage(episode_id, "audio", retry_failed):
                return {"status": "waiting", "next": self.next_action(episode_id)}
            try:
                result = handler(context, self.get_manifest(episode_id))
                self.record_stage(episode_id, "audio_finalize", dict(result or {}))
            except Exception as exc:
                self._finish_stage_error(episode_id, "audio_finalize", exc)
                return {"status": "failed", "error": str(exc), "next": self.next_action(episode_id)}
        manifest = self.get_manifest(episode_id)
        if manifest["stages"]["image"]["state"] != "complete":
            if ((manifest["stages"]["image"]["state"] == "ambiguous" or
                 (retry_failed and manifest["stages"]["image"]["state"] in ("unsupported", "needs_attention"))) and
                    handlers.get("reconcile_image")):
                try:
                    self._reconcile_stage(episode_id, "image", handlers["reconcile_image"], context)
                except Exception as exc:
                    return {"status": "needs_attention", "error": str(exc),
                            "next": self.next_action(episode_id)}
                manifest = self.get_manifest(episode_id)
            if manifest["stages"]["image"]["state"] in ("ambiguous", "unsupported", "needs_attention", "running"):
                return {"status": "waiting", "next": self.next_action(episode_id)}
        if self.get_manifest(episode_id)["stages"]["image"]["state"] != "complete":
            handler = handlers.get("image")
            if handler is None:
                return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
            if not self._claim_stage(episode_id, "image", retry_failed):
                return {"status": "waiting", "next": self.next_action(episode_id)}
            try:
                self.record_stage(episode_id, "image", dict(handler(context, self.get_manifest(episode_id)) or {}))
            except Exception as exc:
                self._finish_stage_error(episode_id, "image", exc)
                return {"status": "failed", "error": str(exc), "next": self.next_action(episode_id)}
        manifest = self.get_manifest(episode_id)
        if manifest["stages"]["video"]["state"] != "complete":
            if (manifest["stages"]["video"]["state"] == "ambiguous" and
                    handlers.get("reconcile_video")):
                try:
                    self._reconcile_stage(episode_id, "video", handlers["reconcile_video"], context)
                except Exception as exc:
                    return {"status": "needs_attention", "error": str(exc),
                            "next": self.next_action(episode_id)}
                manifest = self.get_manifest(episode_id)
            if manifest["stages"]["video"]["state"] in ("ambiguous", "unsupported", "needs_attention", "running"):
                return {"status": "waiting", "next": self.next_action(episode_id)}
        if self.get_manifest(episode_id)["stages"]["video"]["state"] != "complete":
            handler = handlers.get("video")
            if handler is None:
                return {"status": "waiting_for_handler", "next": self.next_action(episode_id)}
            if not self._claim_stage(episode_id, "video", retry_failed):
                return {"status": "waiting", "next": self.next_action(episode_id)}
            try:
                self.record_stage(episode_id, "video", dict(handler(context, self.get_manifest(episode_id)) or {}))
            except Exception as exc:
                self._finish_stage_error(episode_id, "video", exc)
                return {"status": "failed", "error": str(exc), "next": self.next_action(episode_id)}
        final = self.status(episode_id)
        if final["state"] == "complete":
            self.mark_done(episode_id)
        return {"status": "complete" if final["state"] == "complete" else "waiting",
                "episode": final, "next": final["next"]}

    def _finish_stage_error(self, episode_id: str, stage: str, exc: Exception) -> None:
        with self._write_lock(episode_id):
            manifest = self._load_manifest(episode_id)
            stage_key = "audio" if stage == "audio_finalize" else stage
            target = manifest["stages"][stage_key]
            target["state"] = "failed"
            if stage == "content":
                checkpoint = self.episode_dir(episode_id) / "content/quality/pipeline-state.json"
                if checkpoint.is_file():
                    saved = _read_json(checkpoint)
                    if saved.get("exhausted"):
                        target["state"] = "needs_attention"
                    elif saved.get("pending"):
                        target["state"] = "ambiguous"
            target["error"] = str(exc)
            target.pop("owner", None)
            if stage == "audio_finalize":
                target["master"] = None
            self._save(manifest, stage + "_failed", {"error": str(exc)})

    def resume(self, episode_id: str,
               handlers: Mapping[str, Callable[..., Any]] | None = None,
               *, retry_failed: bool = False) -> dict[str, Any]:
        if handlers is None:
            return {"status": "paused", "episode": self.status(episode_id),
                    "next": self.next_action(episode_id)}
        return self.run_episode(episode_id, handlers, retry_failed=retry_failed)


__all__ = ["Coordinator", "EpisodeContext", "EpisodeError", "PART_IDS"]
