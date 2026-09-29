"""Single-sample FP16 autocast test with FP32 weights on the Colab T4."""

from __future__ import annotations

import gc
import hashlib
import importlib
import json
import random
import time
from pathlib import Path
import sys


TEXT = (
    "Bây giờ, khi những việc trong ngày đã tạm khép lại, bạn có thể cho mình một khoảng nghỉ thật nhỏ. "
    "Không cần vội nghĩ xem ngày mai ra sao, cũng không cần tự nhắc mình phải hoàn thành thêm điều gì. "
    "Hãy cảm nhận nơi cơ thể đang được nâng đỡ, để đôi vai hạ xuống, hai bàn tay thôi nắm chặt."
)
VOICE_ID = "wynn_podcast_ea9b0og4_21s_20260928"
SPEED = 0.90
SEED = 20260928
OUTPUT = Path("/content/podcast-precision-benchmark-20260928")


def main() -> None:
    # The previous benchmark may have left its converted test model in the
    # notebook namespace. Release it before loading fresh FP32 weights.
    namespace = globals()
    for name in ("omni", "model"):
        namespace.pop(name, None)
    gc.collect()

    sys_dir = Path("/content/tiktok-ytb/sys").resolve()
    betterbox = Path("/content/BetterBox-TTS").resolve()
    tv_target = Path("/content/torchvision-0.23.0-target")
    if tv_target.is_dir():
        sys.path.insert(0, str(tv_target))
    sys.path.insert(0, str(betterbox))
    sys.path.insert(0, str(sys_dir))

    import torch
    import numpy as np
    import scipy.io.wavfile as wavfile
    import types
    gc.collect()
    torch.cuda.empty_cache()

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

    voice_dir = sys_dir / "assets" / "voices" / VOICE_ID
    voice_config = json.loads((voice_dir / "voice_config.json").read_text(encoding="utf-8"))
    files = voice_config["files"]
    reference_wav = voice_dir / files["reference_wav"]
    reference_text = (voice_dir / files["transcript_txt"]).read_text(encoding="utf-8").strip()
    if not reference_wav.is_file():
        raise FileNotFoundError("The approved podcast voice reference is missing")

    module = importlib.import_module("OmniVoice.omnivoice_inference.ttsOmni")
    generate_speech_omni = module.generate_speech_omni
    original_vad_trim = module.vad_trim

    def vad_trim_float32(audio, sample_rate, *args, **kwargs):
        # VAD requires float32; autocast may return a finite float16 waveform.
        audio = np.asarray(audio)
        if audio.dtype == np.float16:
            audio = audio.astype(np.float32)
        result = original_vad_trim(audio, sample_rate, *args, **kwargs)
        return np.asarray(result, dtype=np.float32)

    module.vad_trim = vad_trim_float32
    model_path = betterbox / "OmniVoice" / "modelOmniLocal"
    if not (model_path / "config.json").is_file():
        model_path = Path("kjanh/KhanhTTS-OmniVoice")

    # Match the same local reference model and seed as the FP32/FP16 tests.
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.cuda.init()
    torch.cuda.synchronize()
    load_started = time.perf_counter()
    omni = module.Omni(model_path=str(model_path), device="cuda")
    model = omni.loadModelOmni()
    torch.cuda.synchronize()
    load_seconds = time.perf_counter() - load_started
    if str(next(model.parameters()).dtype) != "torch.float32":
        raise RuntimeError("AMP test requires the original FP32 model weights")

    torch.use_deterministic_algorithms(False, warn_only=True)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.enable_flash_sdp(False)
    torch.backends.cuda.enable_math_sdp(False)
    torch.backends.cuda.enable_mem_efficient_sdp(True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    torch.cuda.reset_peak_memory_stats()

    def synthesize_current_backend():
        random.seed(SEED)
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        torch.cuda.manual_seed_all(SEED)
        torch.cuda.synchronize()
        started = time.perf_counter()
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            result = generate_speech_omni(
                omni=omni, text=TEXT, language="vi", reference_audio=str(reference_wav),
                ref_text=reference_text, speed=SPEED, pitch_shift=1.0,
            )
        torch.cuda.synchronize()
        (sample_rate, audio), status, subtitle = result
        return sample_rate, audio, status, subtitle, time.perf_counter() - started

    attention_backend = "memory_efficient_sdp"
    try:
        sample_rate, audio, status, _srt, inference_seconds = synthesize_current_backend()
        audio = np.asarray(audio)
        if audio.size == 0 or not np.isfinite(audio).all():
            raise FloatingPointError("FP16 autocast with memory-efficient SDP produced non-finite audio")
    except Exception as first_error:
        # Keep the mixed-precision test useful on T4 builds where the
        # memory-efficient kernel is unavailable for this model's shapes.
        torch.backends.cuda.enable_math_sdp(True)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        attention_backend = "math_sdp_fallback"
        try:
            sample_rate, audio, status, _srt, inference_seconds = synthesize_current_backend()
            audio = np.asarray(audio)
            if audio.size == 0 or not np.isfinite(audio).all():
                raise FloatingPointError("FP16 autocast with math SDP produced non-finite audio")
        except Exception as fallback_error:
            failure = {
                "variant": "FP16 autocast with FP32 weights",
                "voice_id": VOICE_ID,
                "model": voice_config.get("model"),
                "sample_text": TEXT,
                "sample_word_count": len(TEXT.split()),
                "speed": SPEED,
                "pitch_shift": 1.0,
                "gpu": torch.cuda.get_device_name(0),
                "attention_backend_attempted": "memory_efficient_sdp",
                "first_error_type": type(first_error).__name__,
                "first_error": str(first_error)[-800:],
                "fallback_error_type": type(fallback_error).__name__,
                "fallback_error": str(fallback_error)[-800:],
            }
            report_path = OUTPUT / "fp16_autocast.json"
            report_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False), encoding="utf-8")
            print("PODCAST_AMP_BENCH_RESULT=" + json.dumps(failure, ensure_ascii=False), flush=True)
            return
    peak = float(np.max(np.abs(audio)))
    normalized = (audio / peak) * 0.89 if peak > 0 else audio
    pcm = (normalized * 32767).clip(-32768, 32767).astype(np.int16)
    wav_path = OUTPUT / "fp16_autocast.wav"
    wavfile.write(str(wav_path), int(sample_rate), pcm)
    duration = len(pcm) / float(sample_rate)
    result = {
        "variant": "FP16 autocast with FP32 weights",
        "voice_id": VOICE_ID,
        "voice_alias": "podcas",
        "model": voice_config.get("model"),
        "weights_dtype": str(next(model.parameters()).dtype),
        "autocast_dtype": "torch.float16",
        "vad_input_cast": "float32",
        "sample_text": TEXT,
        "sample_word_count": len(TEXT.split()),
        "speed": SPEED,
        "pitch_shift": 1.0,
        "seed": SEED,
        "gpu": torch.cuda.get_device_name(0),
        "attention_backend": attention_backend,
        "attention_backends": {"flash": False,
                               "math": attention_backend == "math_sdp_fallback",
                               "mem_efficient": attention_backend == "memory_efficient_sdp"},
        "deterministic_algorithms": False,
        "model_load_seconds": load_seconds,
        "synthesis_seconds": inference_seconds,
        "sample_rate": int(sample_rate),
        "duration_seconds": duration,
        "real_time_factor": inference_seconds / duration,
        "peak_vram_mib": round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1),
        "status": str(status),
        "wav_path": str(wav_path),
        "wav_sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
        "wav_bytes": wav_path.stat().st_size,
    }
    report_path = OUTPUT / "fp16_autocast.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("PODCAST_AMP_BENCH_RESULT=" + json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
