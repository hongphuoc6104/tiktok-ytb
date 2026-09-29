"""Generate, review, and narrowly repair a complete podcast script."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .content_review import ContentReviewError, repair_part, review_script
from .writer import ScriptGenerationError, generate_script, validate_script


class PodcastContentError(RuntimeError):
    """The podcast script could not pass bounded content review."""


@dataclass(frozen=True)
class ReviewedScript:
    script: dict[str, Any]
    reviews: list[dict[str, Any]]
    repairs: list[dict[str, Any]]
    novelty_reports: list[dict[str, Any]]


def _save_json(path: Path, value: Any) -> None:
    from .coordinator import _atomic_json
    _atomic_json(path, value)


def generate_reviewed_script(
    topic: str,
    *,
    brief: Mapping[str, Any],
    estimated_wpm: float,
    output_dir: Path | str,
    novelty_context: Any = None,
    max_repair_rounds: int = 3,
    timeout: int = 480,
) -> ReviewedScript:
    """Review the full episode, with a durable shared budget of three repairs.

    A pending remote call is never silently replayed after a crash. Its result
    must be reconciled before continuing; completed local work is reused.
    """
    import hashlib
    import fcntl

    if not 0 <= max_repair_rounds <= 3:
        raise ValueError("Podcast cho phép tối đa ba vòng sửa toàn tập.")
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    with (root / "pipeline.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PodcastContentError("Nội dung đang được xử lý bởi tiến trình khác.") from exc
        prompt_brief = copy.deepcopy(dict(brief))
        references = getattr(novelty_context, "references", None)
        if isinstance(references, list) and references:
            prompt_brief["recent_episode_references"] = references
        target_minutes = float(brief.get("target_minutes", 25))
        input_identity = hashlib.sha256(json.dumps(
            [topic, dict(brief), estimated_wpm, max_repair_rounds],
            ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        identity = hashlib.sha256(json.dumps(
            [topic, prompt_brief, estimated_wpm, max_repair_rounds],
            ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        checkpoint = root / "pipeline-state.json"
        if checkpoint.exists():
            state = json.loads(checkpoint.read_text())
            if (state.get("input_identity", input_identity) != input_identity or
                    ("input_identity" not in state and state["identity"] != identity)):
                raise PodcastContentError("Đầu vào khác checkpoint; không tự đặt lại ngân sách sửa.")
            prompt_brief = state.get("prompt_brief", prompt_brief)
            if state.get("exhausted"):
                raise PodcastContentError("Đã hết ngân sách sửa nội dung; cần xử lý lỗi còn lại.")
            if state.get("pending") and not ((root / (state["pending"] + "-result.json")).is_file() or
                    (root / state["pending"] / "account-response.json").is_file()):
                raise PodcastContentError("Lời gọi nội dung chưa rõ kết quả; cần đối chiếu trước khi tiếp tục: " + state["pending"])
        else:
            if (root / "write-1").exists() or (root / "reports").exists():
                raise PodcastContentError("Có lịch sử nội dung cũ chưa nhập checkpoint; không tự viết lại.")
            state = {"identity": identity, "input_identity": input_identity, "prompt_brief": prompt_brief,
                     "round": 0, "script": None,
                     "reviews": [], "repairs": [], "novelty_reports": [],
                     "queue": [], "feedback": {}, "pending": None, "complete": False}
            _save_json(checkpoint, state)

        def call(label, function, *args, **kwargs):
            state["pending"] = label
            _save_json(checkpoint, state)
            result_path = root / (label + "-result.json")
            if result_path.is_file():
                result = json.loads(result_path.read_text())
            else:
                result = function(*args, **kwargs)
                _save_json(result_path, result)
            # Caller commits both result and cleared pending flag atomically.
            return result

        if state["script"] is None:
            state["script"] = call("write-1", generate_script, topic,
                target_minutes=target_minutes, estimated_wpm=estimated_wpm,
                brief=prompt_brief, output_dir=root / "write-1", timeout=timeout)
            state["pending"] = None
            _save_json(checkpoint, state)

        while not state["complete"]:
            while state["queue"]:
                part_id = state["queue"][0]
                label = f"repair-round-{state['round']}-{part_id}"
                result = call(label, repair_part, state["script"], part_id,
                    state["feedback"][part_id], brief=prompt_brief,
                    target_minutes=target_minutes, estimated_wpm=estimated_wpm,
                    output_dir=root / label, timeout=timeout)
                state["script"] = validate_script(result["repaired_script"],
                    target_minutes=target_minutes, estimated_wpm=estimated_wpm, enforce_duration=False)
                state["repairs"].append({"part_id": part_id, "round": state["round"],
                    "feedback": state["feedback"][part_id], "generation": result.get("generation", {})})
                state["queue"].pop(0)
                state["pending"] = None
                _save_json(checkpoint, state)

            feedback = {}
            if novelty_context is not None:
                novelty = novelty_context.check_draft(state["script"])
                state["novelty_reports"].append(novelty)
                for match in [*novelty.get("exact_matches", []), *novelty.get("near_verbatim_matches", [])]:
                    part_id = str(match.get("draft_part_id", ""))
                    if part_id not in {p["id"] for p in state["script"]["parts"]}:
                        raise PodcastContentError("Báo cáo trùng lặp có mã phần không hợp lệ.")
                    feedback.setdefault(part_id, []).append(
                        "Replace reused wording/story while preserving topic and sleep-friendly flow: "
                        + json.dumps(match, ensure_ascii=False))
            # Duration errors belong to the same repair budget, before costly TTS.
            parts = state["script"]["parts"]
            if all(isinstance(p.get("script"), str) for p in parts):
                from .writer import word_count
                counts = {p["id"]: word_count(p["script"]) for p in parts}
                total = sum(counts.values())
                limits = brief.get("duration_seconds", {"min": 1200, "max": 1800})
                seconds = total / estimated_wpm * 60
                if not float(limits["min"]) <= seconds <= float(limits["max"]):
                    for p in parts:
                        feedback.setdefault(p["id"], []).append(
                            f"Total estimated duration {seconds:.1f}s is outside {limits}. "
                            f"Target {target_minutes * estimated_wpm:.0f} spoken words across the whole episode; "
                            "revise length with concrete meaningful content, no filler or abrupt cuts.")
                for p in parts:
                    if total and not .12 <= counts[p["id"]] / total <= .38:
                        feedback.setdefault(p["id"], []).append(
                            "This part must carry 12–38% of total speech; preserve smooth transitions and avoid filler.")
            label = f"review-round-{state['round']}"
            report = call(label, review_script, state["script"], brief=prompt_brief,
                target_minutes=target_minutes, estimated_wpm=estimated_wpm,
                output_dir=root / label, timeout=timeout)
            state["reviews"].append(report)
            for part in report["parts"]:
                if part.get("findings"):
                    feedback.setdefault(part["id"], []).extend(part["findings"])
            state["pending"] = None
            if report["verdict"] == "pass" and not feedback:
                state["complete"] = True
            elif not feedback or state["round"] >= max_repair_rounds:
                state["exhausted"] = True
                _save_json(checkpoint, state)
                raise PodcastContentError("Kịch bản chưa đạt sau ngân sách sửa cho phép: " + report["summary"])
            else:
                state["round"] += 1
                state["feedback"] = feedback
                state["queue"] = sorted(feedback)
            _save_json(checkpoint, state)
        return ReviewedScript(script=state["script"], reviews=state["reviews"],
                              repairs=state["repairs"], novelty_reports=state["novelty_reports"])


__all__ = ["PodcastContentError", "ReviewedScript", "generate_reviewed_script"]
