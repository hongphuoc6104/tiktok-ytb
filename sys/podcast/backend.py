"""Default end-to-end handlers for the podcast episode coordinator."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import uuid
from typing import Any, Mapping

from .direction import locked_content
from .audio import finalize_audio
from .content_pipeline import generate_reviewed_script
from .coordinator import Coordinator, EpisodeContext, EpisodeError
from .colab_cli_direct import PodcastColabCLIRunner
from .exporter import export_video
from .novelty import load_recent_episode_context
from .tts import (
    DEFAULT_PODCAST_SPEED,
    CalibrationCacheMiss,
    PodcastChunk,
    PodcastColabTTS,
    PodcastTTSAmbiguous,
    PodcastTTSRemoteFailure,
    load_podcast_colab_config,
)


PITCH_SHIFT = 1.0


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _verified_artifact(project_root: Path, record: Mapping[str, Any]) -> Path:
    path = (project_root / str(record.get("path", ""))).resolve()
    if not path.is_relative_to(project_root.resolve()) or not path.is_file():
        raise EpisodeError("Artifact đã lưu bị thiếu hoặc vượt thư mục dự án.")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != record.get("sha256"):
        raise EpisodeError("Artifact đã thay đổi sau khi ghi nhận; dừng ghép/xuất.")
    return path


def _chunks(part: Mapping[str, Any]) -> list[PodcastChunk]:
    return [PodcastChunk(str(item.get("id", item.get("chunk_id"))), str(item["text"]))
            for item in part.get("chunks", [])]


def _colab_progress(progress: Mapping[str, Any]) -> None:
    part_progress = progress.get("part_progress_percent")
    completed_parts = progress.get("completed_parts")
    total_parts = progress.get("total_parts")
    if part_progress is not None:
        print(f"Podcast TTS: phần {part_progress}% — {completed_parts or 0}/{total_parts or 4} phần",
              flush=True)


def handlers(coordinator: Coordinator, episode_id: str) -> dict[str, Any]:
    """Factory consumed by `python3 -m podcast.cli run/resume --backend`."""
    episode_dir = coordinator.episode_dir(episode_id)
    tts = PodcastColabTTS(
        episode_id=episode_id,
        run_dir=episode_dir,
        sys_root=coordinator.sys_root,
        profile_alias="podcas",
    )
    calibration_tts = PodcastColabTTS(
        episode_id=episode_id,
        run_dir=episode_dir / "calibration",
        sys_root=coordinator.sys_root,
        profile_alias="podcas",
    )
    deployment: dict[str, str] | None = None
    cli_runner: PodcastColabCLIRunner | None = None
    cli_restored_runtime: str | None = None

    def ensure_colab() -> dict[str, str]:
        nonlocal deployment, cli_runner, cli_restored_runtime
        if deployment is None:
            from .colab_deploy import deploy_podcast_worker, restore_local_tts_checkpoints
            from .colab_deploy import _load_state

            state = _load_state(coordinator.sys_root)
            transport = os.environ.get("PODCAST_COLAB_TRANSPORT") or state.get("transport", "cli_foreground")
            if transport == "cli_foreground":
                from .colab_deploy import _session_exists, _provision
                alias = str(state.get("profile_alias", "alternate"))
                session = str(state.get("session", "podcast-worker"))
                if not _session_exists(alias, session):
                    _provision(alias, session)
                cli_runner = PodcastColabCLIRunner(
                    tts, profile_alias=str(state.get("profile_alias", "alternate")),
                    session=str(state.get("session", "podcast-worker")))
                runtime = cli_runner.ensure_runtime()
                runtime_id = str(runtime["runtime_id"])
                if cli_restored_runtime != runtime_id:
                    restored = restore_local_tts_checkpoints(coordinator.sys_root, episode_id)
                    cli_restored_runtime = runtime_id
                    if restored.get("restored_chunks"):
                        print(f"Podcast TTS: đã phục hồi {restored['restored_chunks']} chunk WAV đã lưu lên Colab.",
                              flush=True)
                deployment = {"session": cli_runner.session, "transport": "cli_foreground",
                              "runtime_id": runtime_id}
            else:
                deployment = deploy_podcast_worker(session="podcast-worker", sys_root=coordinator.sys_root)
                restored = restore_local_tts_checkpoints(coordinator.sys_root, episode_id)
                if restored.get("restored_chunks"):
                    print(f"Podcast TTS: đã phục hồi {restored['restored_chunks']} chunk WAV đã lưu.", flush=True)
                refreshed_config = load_podcast_colab_config(coordinator.sys_root)
                tts.config = refreshed_config
                calibration_tts.config = refreshed_config
        return deployment

    def preflight_environment(ctx: EpisodeContext) -> dict[str, Any]:
        from .preflight import check_environment
        manifest = ctx.manifest
        if manifest["stages"]["video"]["state"] == "complete":
            return {"ready": True, "checks": []}
        # Once media exists, exporting it must not depend on remote availability.
        if (manifest["stages"]["audio"]["state"] == "complete" and
                manifest["stages"]["image"]["state"] == "complete"):
            return {"ready": True, "checks": []}
        chunks = [c for part in manifest["parts"] for c in part["chunks"]]
        result = check_environment(coordinator.sys_root,
            need_audio=not chunks or any(c["state"] != "complete" for c in chunks))
        _atomic_json(ctx.artifact_path("preflight/latest.json"), result)
        return result

    def generation_signature() -> dict[str, Any]:
        return tts.generation_signature(speed=DEFAULT_PODCAST_SPEED, pitch_shift=PITCH_SHIFT)

    def content(ctx: EpisodeContext) -> dict[str, Any]:
        try:
            calibration = calibration_tts.calibrate(speed=DEFAULT_PODCAST_SPEED, cache_only=True)
        except CalibrationCacheMiss:
            ensure_colab()
            synthesize = None
            if cli_runner is not None:
                calibration_runner = PodcastColabCLIRunner(calibration_tts,
                    profile_alias=cli_runner.profile_alias, session=cli_runner.session)
                synthesize = calibration_runner.synthesize_part
            calibration = calibration_tts.calibrate(speed=DEFAULT_PODCAST_SPEED,
                synthesizer=synthesize, progress_callback=_colab_progress)
        calibration_record = {
            "estimated_wpm": calibration.estimated_wpm,
            "token_count": calibration.token_count,
            "duration_seconds": calibration.duration_seconds,
            "wav_path": str(Path(calibration.wav_path).resolve().relative_to(coordinator.project_root)),
            "cache_hit": calibration.cache_hit,
            "profile_fingerprint": calibration.profile_fingerprint,
            "model": calibration.model,
            "speed": calibration.speed,
            "sample_sha256": calibration.sample_sha256,
            "sample_text": calibration.sample_text,
            "cache_key": calibration.cache_key,
        }
        _atomic_json(ctx.artifact_path("content/voice-calibration.json"), calibration_record)

        novelty_context = load_recent_episode_context(
            coordinator.sys_root,
            current_episode_id=episode_id,
            limit=5,
            excerpt_chars_per_part=220,
            max_total_excerpt_chars=6000,
        )
        result = generate_reviewed_script(
            ctx.brief["topic"],
            brief=ctx.brief,
            estimated_wpm=calibration.estimated_wpm,
            output_dir=ctx.artifact_path("content/quality"),
            novelty_context=novelty_context,
        )
        _atomic_json(ctx.artifact_path("content/locked-input.json"),
                     locked_content(result.script, generation_signature()))
        _atomic_json(ctx.artifact_path("content/script.json"), result.script)
        _atomic_json(ctx.artifact_path("content/summary.json"), {
            "review_count": len(result.reviews),
            "repair_count": len(result.repairs),
            "verdict": result.reviews[-1]["verdict"] if result.reviews else "unsupported",
            "total_word_count": result.script["word_count"],
            "estimated_wpm": calibration.estimated_wpm,
            "estimated_minutes": round(result.script["word_count"] / calibration.estimated_wpm, 2),
            "novelty_status": result.novelty_reports[-1]["status"] if result.novelty_reports else "unsupported",
            "novelty_history_episodes": (result.novelty_reports[-1].get("history_episode_count", 0)
                                         if result.novelty_reports else 0),
        })
        return result.script

    def reconcile_content(ctx: EpisodeContext, manifest: Mapping[str, Any]) -> dict[str, Any]:
        checkpoint = ctx.artifact_path("content/quality/pipeline-state.json")
        if not checkpoint.exists():
            return {"state": "needs_attention", "detail": "Chưa có checkpoint nội dung để đối chiếu."}
        state = json.loads(checkpoint.read_text())
        pending = state.get("pending")
        if state.get("exhausted"):
            return {"state": "needs_attention", "detail": "Đã dùng hết ba vòng sửa; giữ nguyên báo cáo lỗi."}
        if pending and not ((checkpoint.parent / (pending + "-result.json")).exists() or
                            (checkpoint.parent / pending / "account-response.json").exists()):
            return {"state": "ambiguous", "detail": "Chưa có kết quả lời gọi cũ; cần đối chiếu phiên tài khoản, không gửi lại."}
        script = content(ctx)
        script["generation_signature"] = generation_signature()
        return {"state": "complete", "script": script}

    def register_plan(ctx: EpisodeContext) -> None:
        lock_path = ctx.artifact_path("content/locked-input.json")
        if lock_path.exists():
            expected = json.loads(lock_path.read_text())
            actual = locked_content(coordinator.read(episode_id, "script"), generation_signature())
            if actual != expected:
                raise EpisodeError("Đầu vào TTS khác lời văn/giọng đã khóa; không tạo audio.")
        manifest = ctx.manifest
        parts = {part["id"]: _chunks(part) for part in manifest["parts"]}
        tts.register_plan(
            parts,
            speed=DEFAULT_PODCAST_SPEED,
            pitch_shift=PITCH_SHIFT,
            script_revision=int(manifest["script"]["revision"]),
        )

    def audio_part(ctx: EpisodeContext, part: Mapping[str, Any], chunks: list[dict[str, Any]],
                   progress_callback, retry_failed: bool = False) -> dict[str, Any]:
        ensure_colab()
        register_plan(ctx)
        try:
            part_chunks = [PodcastChunk(str(item.get("id", item.get("chunk_id"))), str(item["text"]))
                           for item in chunks]
            if cli_runner is not None:
                result = cli_runner.synthesize_part(
                    str(part["id"]), part_chunks, speed=DEFAULT_PODCAST_SPEED,
                    pitch_shift=PITCH_SHIFT, retry_failed=retry_failed,
                    progress_callback=progress_callback)
            else:
                result = tts.synthesize_part(
                    str(part["id"]), part_chunks,
                    speed=DEFAULT_PODCAST_SPEED,
                    pitch_shift=PITCH_SHIFT,
                    retry_failed=retry_failed,
                    progress_callback=progress_callback,
                )
            return {"status": "success", "chunks": result.get("chunks", []),
                    "request_id": result.get("request_id"), "part_id": part["id"]}
        except PodcastTTSAmbiguous as exc:
            return {"status": "ambiguous", "error": str(exc), "chunks": tts.progress().get("chunks", [])}
        except PodcastTTSRemoteFailure as exc:
            return {"status": "failed", "error": str(exc), "chunks": tts.progress().get("chunks", [])}

    def reconcile_audio_part(ctx: EpisodeContext, part: Mapping[str, Any], chunks: list[dict[str, Any]],
                             progress_callback, retry_failed: bool = False) -> dict[str, Any]:
        ensure_colab()
        register_plan(ctx)
        try:
            if cli_runner is not None:
                result = cli_runner.synthesize_part(
                    str(part["id"]), _chunks(part), speed=DEFAULT_PODCAST_SPEED,
                    pitch_shift=PITCH_SHIFT, retry_failed=retry_failed,
                    progress_callback=progress_callback)
            else:
                result = tts.resume_part(str(part["id"]), progress_callback=progress_callback)
            return {"status": "success", "chunks": result.get("chunks", []),
                    "request_id": result.get("request_id"), "part_id": part["id"]}
        except PodcastTTSAmbiguous as exc:
            if cli_runner is not None:
                return {"status": "ambiguous", "error": str(exc),
                        "chunks": tts.progress().get("chunks", [])}
            try:
                resolution = tts.mark_part_failed_if_runtime_changed(str(part["id"]))
            except Exception as verify_error:
                return {"status": "ambiguous", "error": str(verify_error or exc),
                        "chunks": tts.progress().get("chunks", [])}
            try:
                tts.import_local_checkpoints(str(part["id"]))
            except Exception as checkpoint_error:
                return {"status": "needs_attention", "error": str(checkpoint_error),
                        "chunks": tts.progress().get("chunks", [])}
            if retry_failed:
                try:
                    result = tts.synthesize_part(
                        str(part["id"]),
                        [PodcastChunk(str(item.get("id", item.get("chunk_id"))), str(item["text"]))
                         for item in chunks],
                        speed=DEFAULT_PODCAST_SPEED,
                        pitch_shift=PITCH_SHIFT,
                        retry_failed=True,
                        progress_callback=progress_callback,
                    )
                    return {"status": "success", "chunks": result.get("chunks", []),
                            "request_id": result.get("request_id"), "part_id": part["id"]}
                except PodcastTTSAmbiguous as retry_error:
                    return {"status": "ambiguous", "error": str(retry_error),
                            "chunks": tts.progress().get("chunks", [])}
                except PodcastTTSRemoteFailure as retry_error:
                    return {"status": "failed", "error": str(retry_error),
                            "chunks": tts.progress().get("chunks", [])}
            return {"status": "failed", "error": (
                f"Request Colab cũ đã được đối chiếu là mất cùng runtime; giữ checkpoint để chạy lại phần lỗi. {exc}"),
                "request_id": resolution.get("request_id"), "part_id": part["id"],
                "chunks": tts.progress().get("chunks", [])}
        except PodcastTTSRemoteFailure as exc:
            return {"status": "failed", "error": str(exc), "chunks": tts.progress().get("chunks", [])}

    def audio_finalize(ctx: EpisodeContext, manifest: Mapping[str, Any]) -> dict[str, Any]:
        ordered_paths: list[Path] = []
        for part in manifest["parts"]:
            for chunk in part["chunks"]:
                artifact = chunk.get("artifact") or {}
                relative = artifact.get("path")
                if not relative:
                    raise EpisodeError(f"Thiếu WAV đã đạt cho {part['id']}/{chunk['id']}.")
                ordered_paths.append(_verified_artifact(coordinator.project_root, artifact))
        brief = ctx.brief
        result = finalize_audio(
            ordered_paths,
            ctx.artifact_path("audio/master.wav"),
            minimum_seconds=float(brief["duration_seconds"]["min"]),
            maximum_seconds=float(brief["duration_seconds"]["max"]),
        )
        return {"path": result.path, "duration_seconds": result.duration_seconds,
                "sample_rate": result.sample_rate, "channels": result.channels,
                "peak_dbfs": result.peak_dbfs}

    def image(ctx: EpisodeContext, manifest: Mapping[str, Any]) -> dict[str, Any]:
        from .still import copy_selected_still
        return copy_selected_still(ctx, manifest)

    reconcile_image = image

    def _export(ctx: EpisodeContext, manifest: Mapping[str, Any], *, overwrite: bool) -> dict[str, Any]:
        audio_record = manifest["stages"]["audio"]["master"]
        image_record = manifest["stages"]["image"]["artifact"]
        if not audio_record or not image_record:
            raise EpisodeError("Thiếu WAV master hoặc ảnh tĩnh đã đạt để xuất video.")
        audio_path = _verified_artifact(coordinator.project_root, audio_record)
        image_path = _verified_artifact(coordinator.project_root, image_record)
        output_path = coordinator.project_root / manifest["output_dir"] / f"{episode_id}.mp4"
        result = export_video(audio_path, image_path, output_path, overwrite=overwrite)
        return {"path": str(result.output_path),
                "duration_seconds": result.output_duration_seconds,
                "video_codec": result.video_codec, "audio_codec": result.audio_codec,
                "width": result.width, "height": result.height}

    def video(ctx: EpisodeContext, manifest: Mapping[str, Any]) -> dict[str, Any]:
        return _export(ctx, manifest, overwrite=False)

    def reconcile_video(ctx: EpisodeContext, manifest: Mapping[str, Any]) -> dict[str, Any]:
        # Export is a local deterministic operation over already accepted media;
        # it is safe to rebuild an output whose write outcome was interrupted.
        return _export(ctx, manifest, overwrite=True)

    return {
        "preflight": preflight_environment,
        "generation_signature": generation_signature,
        "content": content,
        "reconcile_content": reconcile_content,
        "audio_part": audio_part,
        "reconcile_audio_part": reconcile_audio_part,
        "audio_finalize": audio_finalize,
        "reconcile_audio_finalize": audio_finalize,
        "image": image,
        "reconcile_image": reconcile_image,
        "video": video,
        "reconcile_video": reconcile_video,
    }


__all__ = ["handlers"]
