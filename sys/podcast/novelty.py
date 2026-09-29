"""Bounded cross-episode references and deterministic script overlap checks.

Prior script revisions are scanned incrementally. This module retains only
short excerpts and word-shingle fingerprints, never a complete prior script.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Callable, Mapping, Sequence


DEFAULT_SYS_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST_NAME = "podcast_manifest.json"
_SHINGLE_WORDS = 8
_MAX_SHINGLES_PER_PART = 12_000


class _JsonCursor:
    """Small streaming JSON reader used to skip embedded long narration fields."""

    def __init__(self, path: Path):
        self._stream = path.open("r", encoding="utf-8")
        self._buffer = ""
        self._offset = 0

    def close(self) -> None:
        self._stream.close()

    def peek(self) -> str:
        if self._offset >= len(self._buffer):
            self._buffer = self._stream.read(8192)
            self._offset = 0
        return self._buffer[self._offset:self._offset + 1]

    def take(self) -> str:
        value = self.peek()
        if value:
            self._offset += 1
        return value

    def skip_space(self) -> None:
        while self.peek() and self.peek().isspace():
            self.take()

    def expect(self, expected: str) -> None:
        self.skip_space()
        actual = self.take()
        if actual != expected:
            raise ValueError(f"Malformed JSON: expected {expected!r}, got {actual!r}")

    def read_string(self, consumer: Callable[[str], None] | None = None) -> str | None:
        self.skip_space()
        if self.take() != '"':
            raise ValueError("Malformed JSON string")
        output: list[str] | None = [] if consumer is None else None

        def emit(char: str) -> None:
            if consumer is not None:
                consumer(char)
            else:
                output.append(char)  # type: ignore[union-attr]

        while True:
            char = self.take()
            if not char:
                raise ValueError("Unterminated JSON string")
            if char == '"':
                break
            if char != "\\":
                emit(char)
                continue
            escape = self.take()
            simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                      "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
            if escape in simple:
                emit(simple[escape])
                continue
            if escape != "u":
                raise ValueError("Malformed JSON escape")
            digits = "".join(self.take() for _ in range(4))
            if len(digits) != 4:
                raise ValueError("Malformed JSON unicode escape")
            codepoint = int(digits, 16)
            if 0xD800 <= codepoint <= 0xDBFF:
                if self.take() != "\\" or self.take() != "u":
                    raise ValueError("Malformed JSON surrogate pair")
                low_digits = "".join(self.take() for _ in range(4))
                if len(low_digits) != 4:
                    raise ValueError("Malformed JSON unicode escape")
                low = int(low_digits, 16)
                if not 0xDC00 <= low <= 0xDFFF:
                    raise ValueError("Invalid JSON surrogate pair")
                codepoint = 0x10000 + ((codepoint - 0xD800) << 10) + low - 0xDC00
            elif 0xDC00 <= codepoint <= 0xDFFF:
                raise ValueError("Unexpected JSON low surrogate")
            emit(chr(codepoint))
        return "".join(output) if output is not None else None

    def skip_value(self) -> None:
        self.skip_space()
        char = self.peek()
        if char == '"':
            self.read_string(lambda _chunk: None)
            return
        if char == "{":
            self.take()
            self.skip_space()
            if self.peek() == "}":
                self.take()
                return
            while True:
                self.read_string()
                self.expect(":")
                self.skip_value()
                self.skip_space()
                separator = self.take()
                if separator == "}":
                    return
                if separator != ",":
                    raise ValueError("Malformed JSON object")
        if char == "[":
            self.take()
            self.skip_space()
            if self.peek() == "]":
                self.take()
                return
            while True:
                self.skip_value()
                self.skip_space()
                separator = self.take()
                if separator == "]":
                    return
                if separator != ",":
                    raise ValueError("Malformed JSON array")
        if not char:
            raise ValueError("Unexpected end of JSON")
        token: list[str] = []
        while self.peek() and self.peek() not in ",]} \t\r\n":
            token.append(self.take())
        if not token:
            raise ValueError("Malformed JSON value")

    def read_scalar(self) -> Any:
        self.skip_space()
        if self.peek() == '"':
            return self.read_string()
        if self.peek() in ("{", "["):
            self.skip_value()
            return None
        token: list[str] = []
        while self.peek() and self.peek() not in ",]} \t\r\n":
            token.append(self.take())
        if not token:
            raise ValueError("Malformed JSON scalar")
        return json.loads("".join(token))


@dataclass
class _TextSummary:
    excerpt_limit: int = 220
    max_shingles: int = _MAX_SHINGLES_PER_PART
    normalized_hash: str = ""
    word_count: int = 0
    shingles: set[int] = field(default_factory=set)
    excerpt: str = ""
    _digest: Any = field(default_factory=hashlib.sha256, repr=False)
    _word: list[str] = field(default_factory=list, repr=False)
    _window: deque[str] = field(default_factory=lambda: deque(maxlen=_SHINGLE_WORDS), repr=False)
    _first: list[str] = field(default_factory=list, repr=False)
    _samples: list[tuple[int, str]] = field(default_factory=list, repr=False)
    _active_sample: tuple[int, list[str]] | None = field(default=None, repr=False)
    _next_sample_at: int = field(default=0, repr=False)
    _char_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        self._sample_chars = max(96, min(160, self.excerpt_limit // 2))
        self._sample_interval = max(384, self._sample_chars * 3)

    def feed(self, text: str) -> None:
        for char in text:
            self._sample_char(char)
            if unicodedata.category(char)[0] in {"L", "N", "M"} or char == "_":
                self._word.append(char)
            else:
                self._flush_word()

    def _sample_char(self, char: str) -> None:
        if len(self._first) < max(1, self.excerpt_limit // 3):
            self._first.append(char)
        if self._char_count >= self._next_sample_at and len(self._samples) < 40:
            if self._active_sample is None:
                self._active_sample = (self._char_count, [])
                self._next_sample_at = self._char_count + self._sample_interval
        if self._active_sample is not None:
            start, chars = self._active_sample
            chars.append(char)
            if len(chars) >= self._sample_chars:
                self._samples.append((start, "".join(chars)))
                self._active_sample = None
        self._char_count += 1

    def _flush_word(self) -> None:
        if not self._word:
            return
        word = unicodedata.normalize("NFKC", "".join(self._word)).casefold()
        self._word.clear()
        if not word:
            return
        self._digest.update(word.encode("utf-8"))
        self._digest.update(b" ")
        self.word_count += 1
        self._window.append(word)
        if (len(self._window) == _SHINGLE_WORDS and
                len(self.shingles) < self.max_shingles):
            phrase = "\x1f".join(self._window).encode("utf-8")
            self.shingles.add(int.from_bytes(hashlib.blake2b(phrase, digest_size=8).digest(), "big"))

    def finish(self) -> "_TextSummary":
        self._flush_word()
        self.normalized_hash = self._digest.hexdigest()
        if self._active_sample is not None:
            start, chars = self._active_sample
            if chars:
                self._samples.append((start, "".join(chars)))
            self._active_sample = None
        first_len = max(1, self.excerpt_limit // 3)
        first = "".join(self._first[:first_len]).strip()
        if self._samples:
            target = int(self._char_count * 0.45)
            middle = min(self._samples, key=lambda item: abs(item[0] - target))[1]
        else:
            middle = ""
        middle_len = max(0, self.excerpt_limit - len(first) - 3)
        middle = middle[:middle_len].strip()
        excerpt = " ".join(first.split())
        if middle and middle not in excerpt:
            excerpt += (" … " if excerpt else "") + " ".join(middle.split())
        self.excerpt = excerpt[:self.excerpt_limit]
        return self


def _parse_manifest(path: Path) -> dict[str, Any]:
    cursor = _JsonCursor(path)
    result: dict[str, Any] = {}
    root_keys = {"episode_id", "kind", "topic", "title", "created_at", "updated_at", "state"}
    try:
        cursor.expect("{")
        cursor.skip_space()
        if cursor.peek() == "}":
            cursor.take()
            return result
        while True:
            key = cursor.read_string()
            cursor.expect(":")
            if key in root_keys:
                result[key] = cursor.read_scalar()
            elif key == "script":
                result["script"] = _parse_manifest_script_record(cursor)
            else:
                cursor.skip_value()
            cursor.skip_space()
            separator = cursor.take()
            if separator == "}":
                break
            if separator != ",":
                raise ValueError("Malformed episode manifest")
    finally:
        cursor.close()
    return result


def _parse_manifest_script_record(cursor: _JsonCursor) -> dict[str, Any]:
    fields = {"revision", "path", "sha256", "title"}
    result: dict[str, Any] = {}
    cursor.expect("{")
    cursor.skip_space()
    if cursor.peek() == "}":
        cursor.take()
        return result
    while True:
        key = cursor.read_string()
        cursor.expect(":")
        if key in fields:
            result[key] = cursor.read_scalar()
        else:
            cursor.skip_value()
        cursor.skip_space()
        separator = cursor.take()
        if separator == "}":
            return result
        if separator != ",":
            raise ValueError("Malformed script record in episode manifest")


def _parse_script_revision(path: Path, excerpt_chars: int) -> dict[str, Any]:
    cursor = _JsonCursor(path)
    result: dict[str, Any] = {"parts": []}
    try:
        cursor.expect("{")
        cursor.skip_space()
        if cursor.peek() == "}":
            cursor.take()
            return result
        while True:
            key = cursor.read_string()
            cursor.expect(":")
            if key in {"title", "topic"}:
                result[key] = cursor.read_scalar()
            elif key == "parts":
                result["parts"] = _parse_script_parts(cursor, excerpt_chars)
            else:
                cursor.skip_value()
            cursor.skip_space()
            separator = cursor.take()
            if separator == "}":
                break
            if separator != ",":
                raise ValueError("Malformed script revision")
    finally:
        cursor.close()
    return result


def _parse_script_parts(cursor: _JsonCursor, excerpt_chars: int) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    index = 0
    cursor.expect("[")
    cursor.skip_space()
    if cursor.peek() == "]":
        cursor.take()
        return parts
    while True:
        if index < 4:
            part = _parse_script_part(cursor, excerpt_chars)
            if part.get("id") or part.get("title") or part.get("summary"):
                parts.append(part)
        else:
            cursor.skip_value()
        index += 1
        cursor.skip_space()
        separator = cursor.take()
        if separator == "]":
            return parts
        if separator != ",":
            raise ValueError("Malformed script part list")


def _parse_script_part(cursor: _JsonCursor, excerpt_chars: int) -> dict[str, Any]:
    part: dict[str, Any] = {}
    cursor.expect("{")
    cursor.skip_space()
    if cursor.peek() == "}":
        cursor.take()
        return part
    while True:
        key = cursor.read_string()
        cursor.expect(":")
        if key in {"id", "title"}:
            part[key] = cursor.read_scalar()
        elif key == "script":
            summary = _TextSummary(excerpt_limit=excerpt_chars)
            cursor.read_string(summary.feed)
            part["summary"] = summary.finish()
        else:
            cursor.skip_value()
        cursor.skip_space()
        separator = cursor.take()
        if separator == "}":
            return part
        if separator != ",":
            raise ValueError("Malformed script part")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class _EpisodeFingerprint:
    episode_id: str
    parts: tuple[dict[str, Any], ...]
    shingles: frozenset[int]


@dataclass
class NoveltyContext:
    """Short prompt references plus private fingerprints for local comparison."""

    references: list[dict[str, Any]]
    _episodes: tuple[_EpisodeFingerprint, ...] = field(default=(), repr=False)

    def check_draft(self, draft: str | Mapping[str, Any]) -> dict[str, Any]:
        """Return exact and conservative near-verbatim overlap signals.

        Exact comparison ignores case, punctuation, and whitespace but keeps
        diacritics. Near-verbatim comparison uses unique contiguous 8-word
        shingles; it is a deterministic signal, not a semantic similarity test.
        """
        current_parts = _draft_parts(draft)
        if not self._episodes:
            return {
                "status": "empty_history",
                "history_episode_count": 0,
                "exact_matches": [],
                "near_verbatim_matches": [],
                "possible_overlap_matches": [],
                "method": _overlap_method(),
            }
        summaries = []
        for raw in current_parts:
            summary = _TextSummary(excerpt_limit=0)
            summary.feed(raw["script"])
            summary.finish()
            summaries.append({**raw, "summary": summary})

        exact_matches: list[dict[str, str]] = []
        possible: list[dict[str, Any]] = []
        likely: list[dict[str, Any]] = []
        for current in summaries:
            summary: _TextSummary = current["summary"]
            if summary.word_count < _SHINGLE_WORDS:
                continue
            for episode in self._episodes:
                best_shared = 0
                best_part: dict[str, Any] | None = None
                for previous in episode.parts:
                    prior_summary: _TextSummary = previous["summary"]
                    if (summary.word_count == prior_summary.word_count and
                            summary.normalized_hash == prior_summary.normalized_hash):
                        exact_matches.append({
                            "draft_part_id": current["id"],
                            "episode_id": episode.episode_id,
                            "episode_part_id": str(previous.get("id", "")),
                            "episode_part_title": str(previous.get("title", "")),
                        })
                    shared = len(summary.shingles.intersection(prior_summary.shingles))
                    if shared > best_shared:
                        best_shared = shared
                        best_part = previous
                if not best_shared or not summary.shingles:
                    continue
                coverage = best_shared / len(summary.shingles)
                record = {
                    "draft_part_id": current["id"],
                    "episode_id": episode.episode_id,
                    "episode_part_id": str((best_part or {}).get("id", "")),
                    "episode_part_title": str((best_part or {}).get("title", "")),
                    "shared_8_word_shingles": best_shared,
                    "draft_shingle_coverage": round(coverage, 4),
                }
                if best_shared >= 8 and coverage >= 0.05:
                    likely.append(record)
                elif best_shared >= 3 and coverage >= 0.015:
                    possible.append(record)

                # Also compare against the episode-wide set to catch text moved
                # to a different structural part in a revision.
                episode_shared = len(summary.shingles.intersection(episode.shingles))
                episode_coverage = episode_shared / len(summary.shingles)
                if (episode_shared >= 8 and episode_coverage >= 0.05 and
                        episode_shared > best_shared):
                    likely.append({
                        "draft_part_id": current["id"],
                        "episode_id": episode.episode_id,
                        "episode_part_id": None,
                        "episode_part_title": "Nhiều phần trong tập",
                        "shared_8_word_shingles": episode_shared,
                        "draft_shingle_coverage": round(episode_coverage, 4),
                    })

        likely.sort(key=lambda item: (-item["draft_shingle_coverage"], item["episode_id"], item["draft_part_id"]))
        possible.sort(key=lambda item: (-item["draft_shingle_coverage"], item["episode_id"], item["draft_part_id"]))
        return {
            "status": "compared",
            "history_episode_count": len(self._episodes),
            "exact_matches": _dedupe_records(exact_matches),
            "near_verbatim_matches": _dedupe_records(likely),
            "possible_overlap_matches": _dedupe_records(possible),
            "method": _overlap_method(),
        }


def _overlap_method() -> dict[str, Any]:
    return {
        "normalization": "NFKC, casefold, punctuation/whitespace ignored; Vietnamese diacritics preserved",
        "shingle_words": _SHINGLE_WORDS,
        "near_verbatim_threshold": "at least 8 shared unique shingles and 5% of draft-part shingles",
        "possible_overlap_threshold": "at least 3 shared unique shingles and 1.5% of draft-part shingles",
    }


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    result = []
    for record in records:
        key = (record.get("draft_part_id"), record.get("episode_id"),
               record.get("episode_part_id"))
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def _draft_parts(draft: str | Mapping[str, Any]) -> list[dict[str, str]]:
    if isinstance(draft, str):
        return [{"id": "DRAFT", "title": "Bản nháp", "script": draft}]
    raw_parts = draft.get("parts")
    if isinstance(raw_parts, Sequence) and not isinstance(raw_parts, (str, bytes)):
        result = []
        for index, part in enumerate(raw_parts, 1):
            if not isinstance(part, Mapping):
                continue
            script = part.get("script", part.get("text", ""))
            if isinstance(script, str) and script.strip():
                result.append({
                    "id": str(part.get("id", f"P{index:02}")),
                    "title": str(part.get("title", f"Phần {index}")),
                    "script": script,
                })
        return result
    script = draft.get("script", draft.get("text", ""))
    if isinstance(script, str) and script.strip():
        return [{"id": "DRAFT", "title": str(draft.get("title", "Bản nháp")), "script": script}]
    return []


def load_recent_episode_context(
    sys_root: Path | str = DEFAULT_SYS_ROOT,
    current_episode_id: str | None = None,
    *,
    limit: int = 5,
    excerpt_chars_per_part: int = 220,
    max_total_excerpt_chars: int = 6000,
) -> NoveltyContext:
    """Load recent real podcast revisions as short references and fingerprints.

    The ledger decides which episodes are candidates. Only an existing,
    identity-matching manifest and its checksum-matching script revision are
    used. Long script strings and chunk arrays are streamed and skipped or
    reduced to excerpts/fingerprints while parsing.
    """
    root = Path(sys_root).expanduser().resolve()
    limit = max(0, min(int(limit), 10))
    excerpt_chars_per_part = max(80, min(int(excerpt_chars_per_part), 500))
    max_total_excerpt_chars = max(0, int(max_total_excerpt_chars))
    ledger_path = root / "podcast" / "ledger.json"
    if limit == 0 or not ledger_path.is_file():
        return NoveltyContext(references=[])
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if ledger.get("schema_version") != 1 or not isinstance(ledger.get("episodes"), dict):
            return NoveltyContext(references=[])
        rows = list(ledger["episodes"].values())
    except (OSError, json.JSONDecodeError, AttributeError):
        return NoveltyContext(references=[])

    rows = [row for row in rows if isinstance(row, Mapping) and
            str(row.get("episode_id", "")) != str(current_episode_id or "")]
    rows.sort(key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""), reverse=True)
    references: list[dict[str, Any]] = []
    fingerprints: list[_EpisodeFingerprint] = []
    excerpt_budget = max_total_excerpt_chars

    for row in rows:
        if len(references) >= limit:
            break
        episode_id = str(row.get("episode_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", episode_id):
            continue
        episode_dir = (root / "runs" / episode_id).resolve()
        try:
            episode_dir.relative_to(root.resolve())
        except ValueError:
            continue
        raw_manifest = row.get("manifest") or (Path("runs") / episode_id / _MANIFEST_NAME).as_posix()
        manifest_path = (root / str(raw_manifest)).resolve()
        try:
            if not manifest_path.is_relative_to(root) or manifest_path.parent != episode_dir:
                continue
            if not manifest_path.is_file():
                continue
            manifest = _parse_manifest(manifest_path)
            if manifest.get("kind") != "podcast_episode" or manifest.get("episode_id") != episode_id:
                continue
            script_record = manifest.get("script")
            if not isinstance(script_record, Mapping):
                continue
            script_relative = script_record.get("path")
            expected_hash = str(script_record.get("sha256", ""))
            if not isinstance(script_relative, str) or not script_relative or not re.fullmatch(r"[a-fA-F0-9]{64}", expected_hash):
                continue
            script_path = (episode_dir / script_relative).resolve()
            if not script_path.is_relative_to(episode_dir) or not script_path.is_file():
                continue
            if _sha256_file(script_path).lower() != expected_hash.lower():
                continue
            script_data = _parse_script_revision(script_path, excerpt_chars_per_part)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, RecursionError):
            continue

        script_parts = script_data.get("parts")
        if not isinstance(script_parts, list) or not script_parts:
            continue
        part_refs: list[dict[str, str]] = []
        part_fingerprints: list[dict[str, Any]] = []
        for index, part in enumerate(script_parts, 1):
            summary = part.get("summary") if isinstance(part, Mapping) else None
            if not isinstance(summary, _TextSummary):
                continue
            part_id = str(part.get("id", f"P{index:02}"))
            part_title = str(part.get("title", f"Phần {index}"))[:160]
            excerpt = summary.excerpt[:max(0, excerpt_budget)]
            excerpt_budget -= len(excerpt)
            part_refs.append({"id": part_id, "title": part_title, "excerpt": excerpt})
            part_fingerprints.append({"id": part_id, "title": part_title, "summary": summary})
        if not part_refs:
            continue
        topic = str(manifest.get("topic") or script_data.get("topic") or row.get("topic") or "")[:240]
        title = str(manifest.get("title") or script_data.get("title") or row.get("title") or topic)[:240]
        references.append({
            "episode_id": episode_id,
            "topic": topic,
            "title": title,
            "state": str(manifest.get("state") or row.get("state") or "unknown"),
            "parts": part_refs,
        })
        episode_shingles: set[int] = set()
        for item in part_fingerprints:
            episode_shingles.update(item["summary"].shingles)
        fingerprints.append(_EpisodeFingerprint(
            episode_id=episode_id,
            parts=tuple(part_fingerprints),
            shingles=frozenset(episode_shingles),
        ))
    return NoveltyContext(references=references, _episodes=tuple(fingerprints))


def check_draft_overlap(
    draft: str | Mapping[str, Any],
    context: NoveltyContext,
) -> dict[str, Any]:
    """Convenience wrapper for deterministic comparison against loaded history."""
    return context.check_draft(draft)


__all__ = ["NoveltyContext", "load_recent_episode_context", "check_draft_overlap"]
