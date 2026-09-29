"""Sequential FP32/FP16 comparison for the approved podcast voice on Colab.

Execute this file with the saved Colab profile. It creates temporary remote WAVs
only; it does not change the production voice profile or TTS defaults.
"""

from __future__ import annotations

import gc
import hashlib
import importlib
import json
import random
import time
from pathlib import Path
import sys


REQUESTED_SAMPLE_TEXT = (
    "Bây giờ, khi những việc trong ngày đã tạm khép lại, bạn có thể cho mình một khoảng nghỉ thật nhỏ. "
    "Không cần vội nghĩ xem ngày mai ra sao, cũng không cần tự nhắc mình phải hoàn thành thêm điều gì. "
    "Hãy cảm nhận nơi cơ thể đang được nâng đỡ, để đôi vai hạ xuống, hai bàn tay thôi nắm chặt."
)
VOICE_ID = "wynn_podcast_ea9b0og4_21s_20260928"
SPEED = 0.90
SEED = 20260928
OUTPUT_DIR = Path("/content/podcast-precision-benchmark-20260928")


def _seed(torch, np) -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)


def _model_dtype(model) -> str:
    for parameter in model.parameters():
        return str(parameter.dtype)
    return "no-parameters"


def _run_sample(tag, *, omni, generate_speech_omni, reference_wav: Path,
                reference_text: str, torch, np, wavfile) -> dict:
    _seed(torch, np)
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    started = time.perf_counter()
    (sample_rate, audio), status, _srt = generate_speech_omni(
        omni=omni,
        text=REQUESTED_SAMPLE_TEXT,
        language="vi",
        reference_audio=str(reference_wav),
        ref_text=reference_text,
        speed=SPEED,
        pitch_shift=1.0,
    )
    torch.cuda.synchronize()
    synthesis_seconds = time.perf_counter() - started
    audio = np.asarray(audio)
    if audio.size == 0 or not np.isfinite(audio).all():
        raise RuntimeError(f"{tag} returned empty or invalid audio")
    original_peak = float(np.max(np.abs(audio)))
    normalized = (audio / original_peak) * 0.89 if original_peak > 0 else audio
    pcm = (normalized * 32767).clip(-32768, 32767).astype(np.int16)
    wav_path = OUTPUT_DIR / f"{tag}.wav"
    wavfile.write(str(wav_path), int(sample_rate), pcm)
    duration = len(pcm) / float(sample_rate)
    rms = float(np.sqrt(np.mean(np.square(normalized.astype(np.float64)))))
    return {
        "tag": tag,
        "dtype": _model_dtype(omni.model),
        "status": str(status),
        "sample_rate": int(sample_rate),
        "duration_seconds": duration,
        "synthesis_seconds": synthesis_seconds,
        "real_time_factor": synthesis_seconds / duration,
        "peak_before_normalization": original_peak,
        "rms_after_normalization": rms,
        "peak_vram_mib": round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1),
        "wav_path": str(wav_path),
        "wav_sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
        "wav_bytes": wav_path.stat().st_size,
    }


def main() -> None:
    output = OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    sys_dir = Path("/content/tiktok-ytb/sys").resolve()
    betterbox_dir = Path("/content/BetterBox-TTS").resolve()
    voice_dir = sys_dir / "assets" / "voices" / VOICE_ID
    voice_config = json.loads((voice_dir / "voice_config.json").read_text(encoding="utf-8"))
    files = voice_config["files"]
    reference_wav = voice_dir / files["reference_wav"]
    reference_txt = voice_dir / files["transcript_txt"]
    if not reference_wav.is_file() or not reference_txt.is_file():
        raise FileNotFoundError("The approved podcast voice reference is missing from Colab")
    reference_text = reference_txt.read_text(encoding="utf-8").strip()

    tv_target = Path("/content/torchvision-0.23.0-target")
    if tv_target.is_dir():
        sys.path.insert(0, str(tv_target))
    sys.path.insert(0, str(betterbox_dir))
    sys.path.insert(0, str(sys_dir))

    import torch
    import numpy as np
    import scipy.io.wavfile as wavfile
    import types

    # Match the production runner's compatibility shims and audio post-process.
    torch.compile = lambda model, *args, **kwargs: model
    pedalboard_stub = types.ModuleType("pedalboard")

    class PedalboardStub:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, audio, *args, **kwargs):
            return audio

    pedalboard_stub.Pedalboard = PedalboardStub
    pedalboard_stub.PitchShift = lambda *args, **kwargs: None
    sys.modules["pedalboard"] = pedalboard_stub
    from general import general_tool_audio
    general_tool_audio.fix_silent_and_speed_audio = lambda audio, *args, **kwargs: audio

    module = importlib.import_module("OmniVoice.omnivoice_inference.ttsOmni")
    from OmniVoice.omnivoice_inference.ttsOmni import generate_speech_omni
    model_path = betterbox_dir / "OmniVoice" / "modelOmniLocal"
    if not (model_path / "config.json").is_file():
        model_path = Path("kjanh/KhanhTTS-OmniVoice")

    torch.cuda.init()
    torch.cuda.synchronize()
    cuda_ready = torch.cuda.is_available()
    if not cuda_ready:
        raise RuntimeError("CUDA is unavailable; refusing a CPU benchmark")

    results = {
        "voice_id": VOICE_ID,
        "voice_alias": "podcas",
        "model": voice_config.get("model"),
        "speed": SPEED,
        "pitch_shift": 1.0,
        "seed": SEED,
        "sample_text": REQUESTED_SAMPLE_TEXT,
        "sample_word_count": len(REQUESTED_SAMPLE_TEXT.split()),
        "gpu": torch.cuda.get_device_name(0),
        "source_dtype": "FP32 (production runner's current default)",
        "fp32": None,
        "fp16": None,
    }

    load_started = time.perf_counter()
    omni = module.Omni(model_path=str(model_path), device="cuda")
    model = omni.loadModelOmni()
    torch.cuda.synchronize()
    fp32_load_seconds = time.perf_counter() - load_started
    results["fp32"] = _run_sample("fp32", omni=omni,
                                   generate_speech_omni=generate_speech_omni,
                                   reference_wav=reference_wav, reference_text=reference_text,
                                   torch=torch, np=np, wavfile=wavfile)
    results["fp32"]["model_load_seconds"] = fp32_load_seconds
    del model

    conversion_started = time.perf_counter()
    omni.model.to(dtype=torch.float16)
    torch.cuda.synchronize()
    fp16_conversion_seconds = time.perf_counter() - conversion_started
    results["fp16_conversion_seconds"] = fp16_conversion_seconds
    results["fp16_parameter_dtype"] = _model_dtype(omni.model)
    try:
        results["fp16"] = _run_sample("fp16", omni=omni,
                                       generate_speech_omni=generate_speech_omni,
                                       reference_wav=reference_wav, reference_text=reference_text,
                                       torch=torch, np=np, wavfile=wavfile)
    except Exception as exc:
        results["fp16"] = {"error_type": type(exc).__name__, "error": str(exc)[-1200:]}

    gc.collect()
    torch.cuda.empty_cache()
    if results.get("fp16") and "synthesis_seconds" in results["fp16"]:
        results["speedup_inference"] = round(
            results["fp32"]["synthesis_seconds"] / results["fp16"]["synthesis_seconds"], 3)
    report_path = output / "comparison.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("PODCAST_PRECISION_BENCH_RESULT=" + json.dumps(results, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
