"""Join and normalize a completed podcast's ordered Colab WAV chunks."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


class AudioFinalizeError(RuntimeError):
    """Raised when chunk audio cannot form a valid podcast master."""


@dataclass(frozen=True)
class AudioResult:
    path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    sample_width_bytes: int
    peak_dbfs: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _probe_wav(path: Path) -> tuple[int, int, int, int]:
    try:
        with wave.open(str(path), "rb") as wav:
            if wav.getcomptype() != "NONE":
                raise AudioFinalizeError(f"WAV không phải PCM không nén: {path}")
            return wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
    except (wave.Error, EOFError, OSError) as exc:
        raise AudioFinalizeError(f"Không đọc được WAV: {path}") from exc


def _peak_dbfs(path: Path) -> float:
    peak = 0
    with wave.open(str(path), "rb") as wav:
        width = wav.getsampwidth()
        if width not in (1, 2, 3, 4):
            raise AudioFinalizeError(f"PCM sample width không hỗ trợ: {width}")
        while frames := wav.readframes(wav.getframerate() * 5):
            if width == 1:
                peak = max(peak, max(abs(sample - 128) for sample in frames))
                maximum = 128
            elif width == 2:
                import array
                values = array.array("h")
                values.frombytes(frames)
                if os.sys.byteorder != "little":
                    values.byteswap()
                peak = max(peak, max((abs(value) for value in values), default=0))
                maximum = 32768
            else:
                signed = (int.from_bytes(frames[i:i + width], "little", signed=True)
                          for i in range(0, len(frames), width))
                peak = max(peak, max((abs(value) for value in signed), default=0))
                maximum = (1 << (width * 8 - 1))
    if peak <= 0:
        return float("-inf")
    import math
    return 20 * math.log10(peak / maximum)


def _run(command: list[str], *, timeout: float, label: str) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise AudioFinalizeError(f"{label} chạy quá {timeout:g} giây.") from exc
    except OSError as exc:
        raise AudioFinalizeError(f"Không chạy được {label}: {exc}") from exc
    if result.returncode:
        details = (result.stderr or result.stdout).strip()[-3000:]
        raise AudioFinalizeError(f"{label} lỗi ({result.returncode}): {details}")
    return result.stdout


def finalize_audio(
    chunk_paths: Iterable[str | os.PathLike[str]],
    output_path: str | os.PathLike[str],
    *,
    minimum_seconds: float = 1200,
    maximum_seconds: float = 1800,
    target_lufs: float = -18.0,
    true_peak_dbfs: float = -1.5,
    ffmpeg: str = "ffmpeg",
    timeout: float = 7200,
) -> AudioResult:
    """Concatenate WAVs in manifest order, normalize once, and verify duration.

    The caller must supply chunk paths in the manifest's stable order. Every
    source stays intact. The master is replaced atomically only after a complete
    encode and duration/format check succeeds.
    """
    chunks = [Path(item).expanduser().resolve(strict=True) for item in chunk_paths]
    if not chunks:
        raise AudioFinalizeError("Không có WAV đoạn đọc để ghép.")
    if len(set(chunks)) != len(chunks):
        raise AudioFinalizeError("Danh sách WAV có đoạn bị lặp.")
    if minimum_seconds <= 0 or maximum_seconds <= minimum_seconds:
        raise ValueError("Invalid duration bounds")
    ffmpeg_path = shutil.which(ffmpeg)
    if not ffmpeg_path:
        raise AudioFinalizeError(f"Không tìm thấy ffmpeg: {ffmpeg}")

    params = [_probe_wav(path) for path in chunks]
    channels, width, sample_rate, _ = params[0]
    if channels not in (1, 2) or width != 2 or sample_rate != 24000:
        raise AudioFinalizeError(
            f"Đoạn đầu có định dạng {channels} kênh, {width * 8}-bit, {sample_rate} Hz; "
            "podcast cần PCM16 24 kHz, mono hoặc stereo."
        )
    if any((ch, sample_width, rate) != (channels, width, sample_rate)
           for ch, sample_width, rate, _ in params):
        raise AudioFinalizeError("Các đoạn WAV chưa cùng định dạng PCM; không tự đổi tốc độ/pitch.")

    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target in chunks:
        raise AudioFinalizeError("File master không được ghi đè lên WAV đoạn đọc.")
    descriptor, joined_name = tempfile.mkstemp(prefix=".podcast-joined-", suffix=".wav", dir=target.parent)
    os.close(descriptor)
    descriptor, normalized_name = tempfile.mkstemp(prefix=".podcast-master-", suffix=".wav", dir=target.parent)
    os.close(descriptor)
    joined = Path(joined_name)
    normalized = Path(normalized_name)
    try:
        with wave.open(str(joined), "wb") as master:
            master.setnchannels(channels)
            master.setsampwidth(width)
            master.setframerate(sample_rate)
            for chunk_path in chunks:
                with wave.open(str(chunk_path), "rb") as source:
                    master.writeframes(source.readframes(source.getnframes()))

        # Single full-program loudness pass keeps volume consistent across
        # chunk boundaries. No music, extra silence, or speed changes are added.
        _run([
            ffmpeg_path, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(joined),
            "-af", f"loudnorm=I={target_lufs}:TP={true_peak_dbfs}:LRA=7:linear=true",
            "-ar", str(sample_rate), "-ac", str(channels), "-c:a", "pcm_s16le",
            str(normalized),
        ], timeout=timeout, label="chuẩn hóa âm lượng podcast")

        out_channels, out_width, out_rate, frames = _probe_wav(normalized)
        duration = frames / out_rate
        if (out_channels, out_width, out_rate) != (channels, 2, sample_rate):
            raise AudioFinalizeError("Master WAV đầu ra không giữ định dạng PCM16 đã yêu cầu.")
        if not minimum_seconds <= duration <= maximum_seconds:
            retained = target.with_name(target.stem + ".out-of-range.wav")
            os.replace(normalized, retained)
            raise AudioFinalizeError(
                f"Thời lượng WAV thực đo {duration:.2f}s nằm ngoài "
                f"{minimum_seconds:.0f}–{maximum_seconds:.0f}s; đã giữ file tại {retained}."
            )
        peak = _peak_dbfs(normalized)
        os.replace(normalized, target)
        return AudioResult(str(target), duration, sample_rate, channels, out_width, peak)
    finally:
        joined.unlink(missing_ok=True)
        normalized.unlink(missing_ok=True)


__all__ = ["AudioFinalizeError", "AudioResult", "finalize_audio"]
