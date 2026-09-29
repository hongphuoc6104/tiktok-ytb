"""Export a podcast master audio file and one still image as an MP4 video.

This module is intentionally independent of the general multi-scene renderer.
It has no TTS, subtitle, music, or animation behavior.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence


WIDTH = 1920
HEIGHT = 1080
FPS = 24


class ExportError(RuntimeError):
    """Raised when the input, render, or rendered MP4 fails validation."""


@dataclass(frozen=True)
class ExportResult:
    output_path: Path
    source_duration_seconds: float
    output_duration_seconds: float
    video_codec: str
    audio_codec: str
    width: int
    height: int


def _executable(value: str, label: str) -> str:
    resolved = shutil.which(value)
    if not resolved:
        raise ExportError(f"{label} executable not found: {value}")
    return resolved


def _run_json(command: Sequence[str], *, timeout: float, label: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            list(command), capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise ExportError(f"{label} timed out after {timeout:g} seconds") from exc
    except OSError as exc:
        raise ExportError(f"Could not start {label}: {exc}") from exc
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-4000:]
        raise ExportError(f"{label} failed (exit {result.returncode}): {detail}")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ExportError(f"{label} returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise ExportError(f"{label} returned an unexpected response")
    return data


def _probe(path: Path, ffprobe: str, *, timeout: float = 60) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ExportError(f"Input file is missing or empty: {path}")
    return _run_json(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        timeout=timeout,
        label=f"ffprobe on {path.name}",
    )


def _decimal(value: Any) -> Decimal | None:
    if value in (None, "", "N/A"):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() else None


def _stream_duration(stream: dict[str, Any]) -> Decimal | None:
    """Prefer exact ticks (common for WAV); otherwise use ffprobe's duration."""
    ticks = stream.get("duration_ts")
    time_base = stream.get("time_base")
    if ticks not in (None, "N/A") and time_base not in (None, "N/A"):
        try:
            value = Fraction(str(ticks)) * Fraction(str(time_base))
            return Decimal(value.numerator) / Decimal(value.denominator)
        except (ValueError, ZeroDivisionError, InvalidOperation):
            pass
    return _decimal(stream.get("duration"))


def _input_duration(probe: dict[str, Any], audio_path: Path) -> Decimal:
    streams = probe.get("streams")
    if not isinstance(streams, list):
        raise ExportError(f"ffprobe found no streams in master audio: {audio_path}")
    audio_streams = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"]
    if not audio_streams:
        raise ExportError(f"Master audio has no audio stream: {audio_path}")
    duration = _stream_duration(audio_streams[0])
    if duration is None:
        fmt = probe.get("format")
        duration = _decimal(fmt.get("duration")) if isinstance(fmt, dict) else None
    if duration is None or duration <= 0:
        raise ExportError(f"Could not determine a positive master audio duration: {audio_path}")
    return duration


def _check_image(probe: dict[str, Any], image_path: Path) -> None:
    streams = probe.get("streams")
    if not isinstance(streams, list) or not any(
        isinstance(s, dict)
        and s.get("codec_type") == "video"
        and int(s.get("width") or 0) > 0
        and int(s.get("height") or 0) > 0
        for s in streams
    ):
        raise ExportError(f"Input is not a readable image: {image_path}")


def _output_probe(
    path: Path,
    *,
    ffprobe: str,
    expected_duration: Decimal,
) -> tuple[dict[str, Any], Decimal]:
    data = _probe(path, ffprobe)
    streams = data.get("streams")
    if not isinstance(streams, list):
        raise ExportError("Rendered MP4 has no readable streams")
    videos = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "video"]
    audios = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1 or len(streams) != 2:
        raise ExportError("Rendered MP4 must contain exactly one video stream and one audio stream")
    video, audio = videos[0], audios[0]
    if video.get("codec_name") != "h264":
        raise ExportError(f"Rendered video codec is {video.get('codec_name')}, expected h264")
    if (int(video.get("width") or 0), int(video.get("height") or 0)) != (WIDTH, HEIGHT):
        raise ExportError(
            f"Rendered dimensions are {video.get('width')}x{video.get('height')}, expected {WIDTH}x{HEIGHT}"
        )
    if audio.get("codec_name") != "aac":
        raise ExportError(f"Rendered audio codec is {audio.get('codec_name')}, expected aac")
    fmt = data.get("format")
    if not isinstance(fmt, dict) or "mp4" not in str(fmt.get("format_name", "")).split(","):
        raise ExportError("Rendered file is not an MP4 container")

    actual = _decimal(fmt.get("duration"))
    if actual is None:
        actual = max(filter(None, (_stream_duration(video), _stream_duration(audio))), default=None)
    if actual is None:
        raise ExportError("Could not determine rendered MP4 duration")

    # H.264's final frame is quantized to 1/FPS and AAC uses 1024-sample
    # packets. MP4 edit lists normally preserve the source duration; allow a
    # small muxer/codec rounding margin while rejecting materially wrong output.
    tolerance = max(Decimal("0.10"), Decimal(1) / Decimal(FPS) + Decimal("0.03"))
    if abs(actual - expected_duration) > tolerance:
        raise ExportError(
            f"Rendered duration {actual:.6f}s differs from master audio "
            f"{expected_duration:.6f}s by more than {tolerance:.3f}s"
        )
    audio_duration = _stream_duration(audio)
    if audio_duration is not None and abs(audio_duration - expected_duration) > tolerance:
        raise ExportError(
            f"Rendered AAC duration {audio_duration:.6f}s differs from master audio "
            f"{expected_duration:.6f}s by more than {tolerance:.3f}s"
        )
    return data, actual


def _decode_check(path: Path, ffmpeg: str, *, timeout: float) -> None:
    try:
        result = subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(path), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ExportError(f"Full-file decode validation timed out after {timeout:g} seconds") from exc
    except OSError as exc:
        raise ExportError(f"Could not start ffmpeg decode validation: {exc}") from exc
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-4000:]
        raise ExportError(f"Rendered MP4 failed full-file decode validation: {detail}")


def export_video(
    audio_path: str | os.PathLike[str],
    image_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    overwrite: bool = False,
    timeout: float = 7200,
    preset: str = "medium",
    crf: int = 18,
) -> ExportResult:
    """Create a static 1920x1080 H.264/AAC MP4 whose duration follows the audio.

    The complete image is fitted inside 16:9 with dark blue side padding. Only
    the supplied still and master audio are mapped into the output; no subtitles,
    music, effects, or transitions are added. Output is rendered beside its
    destination, validated, and atomically moved into place on success.

    Args:
        audio_path: Final audio master (WAV or another ffprobe-readable format).
        image_path: The single still image for the podcast video.
        output_path: Destination ending in ``.mp4``.
        overwrite: Atomically replace an existing destination when true.
        timeout: Timeout in seconds for render and full-file decode validation.
        preset: FFmpeg libx264 preset.
        crf: FFmpeg libx264 quality value (lower is higher quality).
    """
    audio = Path(audio_path).expanduser().resolve(strict=True)
    image = Path(image_path).expanduser().resolve(strict=True)
    target_arg = Path(output_path).expanduser()
    target_arg.parent.mkdir(parents=True, exist_ok=True)
    target = target_arg.parent.resolve() / target_arg.name
    if target.suffix.lower() != ".mp4":
        raise ExportError(f"Output path must end with .mp4: {target}")
    if target in (audio, image):
        raise ExportError("Output path must be different from both input paths")
    if target.exists() and not overwrite:
        raise ExportError(f"Output already exists; pass overwrite=True to replace it: {target}")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if not 0 <= crf <= 51:
        raise ValueError("crf must be between 0 and 51")
    if preset not in {"ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow", "placebo"}:
        raise ValueError("preset must be a supported libx264 preset")

    ffmpeg_path = _executable(ffmpeg, "ffmpeg")
    ffprobe_path = _executable(ffprobe, "ffprobe")
    audio_probe = _probe(audio, ffprobe_path)
    image_probe = _probe(image, ffprobe_path)
    duration = _input_duration(audio_probe, audio)
    _check_image(image_probe, image)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.stem}.", suffix=".tmp.mp4", dir=target.parent
    )
    os.close(fd)
    temporary = Path(temp_name)
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-nostdin",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(FPS),
        "-i",
        str(image),
        "-i",
        str(audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x202840,setsar=1,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        str(crf),
        "-tune",
        "stillimage",
        "-r",
        str(FPS),
        "-fps_mode",
        "cfr",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-t",
        format(duration, "f"),
        "-shortest",
        "-movflags",
        "+faststart",
        "-f",
        "mp4",
        str(temporary),
    ]
    try:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise ExportError(f"ffmpeg render timed out after {timeout:g} seconds") from exc
        except OSError as exc:
            raise ExportError(f"Could not start ffmpeg render: {exc}") from exc
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()[-5000:]
            raise ExportError(f"ffmpeg render failed (exit {result.returncode}): {detail}")
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise ExportError("ffmpeg completed without producing a non-empty MP4")

        _, output_duration = _output_probe(
            temporary, ffprobe=ffprobe_path, expected_duration=duration
        )
        _decode_check(temporary, ffmpeg_path, timeout=timeout)

        # Do not overwrite a file that appeared while a non-overwriting render
        # was in progress. For overwrite=True, replace is atomic on this volume.
        if overwrite:
            os.replace(temporary, target)
        else:
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise ExportError(f"Output appeared while rendering; left it untouched: {target}") from exc
            temporary.unlink()
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return ExportResult(
        output_path=target,
        source_duration_seconds=float(duration),
        output_duration_seconds=float(output_duration),
        video_codec="h264",
        audio_codec="aac",
        width=WIDTH,
        height=HEIGHT,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, help="Master audio file")
    parser.add_argument("--image", required=True, help="Single still image")
    parser.add_argument("--output", required=True, help="Destination .mp4 path")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing destination")
    parser.add_argument("--timeout", type=float, default=7200, help="Render/decode timeout in seconds")
    parser.add_argument("--preset", default="medium", help="libx264 preset")
    parser.add_argument("--crf", type=int, default=18, help="libx264 quality value, 0-51")
    args = parser.parse_args(argv)
    try:
        result = export_video(
            args.audio,
            args.image,
            args.output,
            overwrite=args.overwrite,
            timeout=args.timeout,
            preset=args.preset,
            crf=args.crf,
        )
    except (ExportError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(result) | {"output_path": str(result.output_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
