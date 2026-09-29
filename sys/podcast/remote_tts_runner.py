"""Podcast-only Colab inference runner with per-chunk resume and cache."""

import hashlib
import fcntl
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import traceback
import types


CHUNK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUNNER_VERSION = "podcast-omnivoice-v1"
CANONICAL_PROFILE_ID = "wynn_podcast_ea9b0og4_21s_20260928"
INFERENCE_PRECISION = "fp16_autocast_fp32_weights"
ATTENTION_BACKEND = "memory_efficient_sdp"
SLOW_CHUNK_RTF_THRESHOLD = 9.4  # 2.5x the measured 3.76 RTF; warn, never cancel.


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def file_matches(path, metadata_path, chunk_hash):
    path, metadata_path = Path(path), Path(metadata_path)
    if not path.is_file() or not metadata_path.is_file():
        return None
    try:
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        raw = path.read_bytes()
        if meta.get("chunk_hash") != chunk_hash or sha256(raw) != meta.get("wav_sha256"):
            return None
        import wave
        with wave.open(str(path), "rb") as wav:
            channels, width, rate, frames = (wav.getnchannels(), wav.getsampwidth(),
                                             wav.getframerate(), wav.getnframes())
            if channels != 1 or width != 2 or rate <= 0 or frames <= 0:
                return None
            if len(wav.readframes(frames)) != frames * channels * width:
                return None
        return meta
    except Exception:
        return None


def recover_committed_wav(path, item, profile_fingerprint, voice_id, model, speed, pitch_shift):
    """Recover the tiny crash window after atomic WAV replace but before sidecar."""
    path = Path(path)
    if not path.is_file():
        return None
    try:
        import wave
        with wave.open(str(path), "rb") as wav:
            channels, width, sample_rate, frames = (wav.getnchannels(), wav.getsampwidth(),
                                                    wav.getframerate(), wav.getnframes())
            if channels != 1 or width != 2 or sample_rate <= 0 or frames <= 0:
                return None
            if len(wav.readframes(frames)) != frames * channels * width:
                return None
        raw = path.read_bytes()
        return {
            "scene_id": item["id"], "text": item["text"],
            "text_sha256": sha256(item["text"].encode("utf-8")),
            "chunk_hash": item["chunk_hash"], "profile_fingerprint": profile_fingerprint,
            "voice_id": voice_id, "model": model, "speed": speed, "pitch_shift": pitch_shift,
            "sample_rate": sample_rate, "channels": channels,
            "duration_seconds": frames / float(sample_rate), "wav_sha256": sha256(raw),
            "source": "colab", "runner_version": RUNNER_VERSION, "status": "recovered_committed_wav",
            "generated_at": path.stat().st_mtime, "recovered_after_restart": True,
            "path": f"chunks/{item['id']}.wav",
        }
    except Exception:
        return None


def run():
    request_path = Path(os.environ["PODCAST_TTS_REQUEST"]).resolve()
    output_dir = Path(os.environ["PODCAST_TTS_OUTPUT"]).resolve()
    request_id = os.environ["PODCAST_TTS_REQUEST_ID"]
    request_hash = os.environ["PODCAST_TTS_REQUEST_HASH"]
    cache_dir = Path(os.environ["PODCAST_TTS_CHUNK_CACHE"]).resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,159}", request_id) or not SHA256_RE.fullmatch(request_hash):
        raise ValueError("Invalid stable podcast task identity")

    request = json.loads(request_path.read_text(encoding="utf-8"))
    settings = request.get("settings") or {}
    scenes = request.get("scenes") or []
    voice_id = settings.get("tts_voice")
    speed = float(settings.get("tts_speed", 1.0))
    pitch_shift = float(settings.get("pitch_shift", 1.0))
    profile_fingerprint = request.get("profile_fingerprint")
    if not isinstance(profile_fingerprint, str) or not SHA256_RE.fullmatch(profile_fingerprint):
        raise ValueError("Missing verified podcast profile fingerprint")
    if not scenes or len(scenes) > 64:
        raise ValueError("Podcast part must contain 1–64 chunks")

    sys_dir = Path(__file__).resolve().parents[1]
    betterbox_dir = Path("/content/BetterBox-TTS")
    voice_dir = sys_dir / "assets" / "voices" / str(voice_id)
    config_path = voice_dir / "voice_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    aliases = {str(alias).casefold() for alias in config.get("aliases", [])}
    approval = config.get("user_approval") or {}
    if (voice_id != CANONICAL_PROFILE_ID or config.get("voice_id") != voice_id
            or config.get("name", "").casefold() != "podcast"
            or not aliases.intersection({"podcas", "podcast"}) or approval.get("approved") is not True
            or config.get("engine") != "OmniVoice-8400h" or config.get("model") != "kjanh/KhanhTTS-OmniVoice"):
        raise ValueError("Colab voice profile is not the verified approved podcast profile")
    files = config.get("files") or {}
    ref_audio = voice_dir / files["reference_wav"]
    ref_text_path = voice_dir / files["transcript_txt"]
    ref_text = ref_text_path.read_text(encoding="utf-8").strip()
    actual_profile_fingerprint = sha256(canonical_json({
        "voice_config": config,
        "reference_wav_sha256": sha256(ref_audio.read_bytes()),
        "transcript_sha256": sha256(ref_text_path.read_bytes()),
    }))
    if actual_profile_fingerprint != profile_fingerprint:
        raise ValueError("Colab podcast profile files do not match the verified profile fingerprint")

    output_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir = output_dir / "chunks"
    metadata_dir = output_dir / "chunk_meta"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    normalized_scenes = []
    seen = set()
    for scene in scenes:
        scene_id = scene.get("id")
        text = scene.get("narration")
        chunk_hash = scene.get("chunk_hash")
        if (not isinstance(scene_id, str) or not CHUNK_ID_RE.fullmatch(scene_id) or scene_id in seen
                or not isinstance(text, str) or not text.strip() or not SHA256_RE.fullmatch(str(chunk_hash))):
            raise ValueError("Podcast part contains an invalid chunk")
        seen.add(scene_id)
        expected_hash = sha256(canonical_json({
            "text": text.strip(),
            "profile_fingerprint": profile_fingerprint,
            "model": config["model"],
            "speed": speed,
            "pitch_shift": pitch_shift,
            "runner_version": RUNNER_VERSION,
        }))
        if chunk_hash != expected_hash:
            raise ValueError(f"Input chunk hash mismatch for {scene_id}")
        normalized_scenes.append({"id": scene_id, "text": text.strip(), "chunk_hash": chunk_hash})

    progress_path = output_dir / "tts-progress.json"
    progress = {"request_id": request_id, "request_hash": request_hash,
                "chunks": [{"id": item["id"], "state": "pending", "path": f"chunks/{item['id']}.wav",
                            "chunk_hash": item["chunk_hash"]} for item in normalized_scenes]}
    progress_by_id = {item["id"]: item for item in progress["chunks"]}
    write_json(progress_path, progress)

    pending = []
    for item in normalized_scenes:
        scene_id, chunk_hash = item["id"], item["chunk_hash"]
        local_wav = chunks_dir / f"{scene_id}.wav"
        local_meta = metadata_dir / f"{scene_id}.json"
        cached_wav = cache_dir / f"{chunk_hash}.wav"
        cached_meta = cache_dir / f"{chunk_hash}.json"
        meta = file_matches(local_wav, local_meta, chunk_hash)
        if meta is None and local_wav.is_file():
            meta = recover_committed_wav(local_wav, item, profile_fingerprint, voice_id,
                                         config["model"], speed, pitch_shift)
            if meta is not None:
                write_json(local_meta, meta)
        if meta is None:
            meta = file_matches(cached_wav, cached_meta, chunk_hash)
            if meta is not None:
                shutil.copy2(cached_wav, local_wav)
                meta = dict(meta)
                meta.update({"scene_id": scene_id, "path": f"chunks/{scene_id}.wav", "reused_from_cache": True})
                write_json(local_meta, meta)
        if meta is not None:
            progress_by_id[scene_id].update({"state": "succeeded", "path": f"chunks/{scene_id}.wav",
                                             "wav_sha256": meta["wav_sha256"], "reused": True})
        else:
            pending.append(item)
    write_json(progress_path, progress)

    if pending:
        # OmniVoice is loaded once for this quarter; each completed chunk is
        # committed to disk before the next chunk starts.
        tv_target = Path("/content/torchvision-0.23.0-target")
        if tv_target.is_dir():
            sys.path.insert(0, str(tv_target))
        import torch
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

        if str(betterbox_dir) not in sys.path:
            sys.path.insert(0, str(betterbox_dir))
        from general import general_tool_audio
        general_tool_audio.fix_silent_and_speed_audio = lambda audio, *args, **kwargs: audio
        import numpy as np
        import scipy.io.wavfile as wavfile
        omni_module = importlib.import_module("OmniVoice.omnivoice_inference.ttsOmni")
        Omni = omni_module.Omni
        generate_speech_omni = omni_module.generate_speech_omni

        # OmniVoice VAD accepts FP32/FP64/integer buffers, while CUDA autocast
        # can return FP16 samples. Convert only the VAD input back to FP32; the
        # model stays on CUDA under autocast and the production audio behavior
        # remains otherwise unchanged.
        original_vad_trim = omni_module.vad_trim
        def vad_trim_float32(audio, sample_rate, *args, **kwargs):
            audio = np.asarray(audio)
            if audio.dtype == np.float16:
                audio = audio.astype(np.float32)
            result = original_vad_trim(audio, sample_rate, *args, **kwargs)
            return np.asarray(result, dtype=np.float32)
        omni_module.vad_trim = vad_trim_float32

        model_path = betterbox_dir / "OmniVoice" / "modelOmniLocal"
        if not (model_path / "config.json").is_file():
            model_path = Path("kjanh/KhanhTTS-OmniVoice")
        gpu_lock = (cache_dir / ".omnivoice.lock").open("a+")
        fcntl.flock(gpu_lock.fileno(), fcntl.LOCK_EX)
        try:
            omni = Omni(model_path=str(model_path), device="cuda")
            omni.loadModelOmni()
            # Match the benchmarked T4 configuration. Keep checkpoint weights
            # in FP32, use FP16 autocast for eligible CUDA operations, and
            # select the memory-efficient attention kernel. This code runs in
            # the isolated podcast worker, not in the Colab server process.
            torch.use_deterministic_algorithms(False, warn_only=True)
            torch.backends.cudnn.deterministic = False
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.enable_flash_sdp(False)
            torch.backends.cuda.enable_math_sdp(False)
            torch.backends.cuda.enable_mem_efficient_sdp(True)
            actual_weight_dtype = str(next(omni.model.parameters()).dtype)
            if actual_weight_dtype != "torch.float32":
                raise RuntimeError(f"Podcast AMP runner expected FP32 weights, got {actual_weight_dtype}")
            for item in pending:
                scene_id, text, chunk_hash = item["id"], item["text"], item["chunk_hash"]
                chunk_started_at = time.time()
                chunk_started_clock = time.monotonic()
                progress_by_id[scene_id]["state"] = "running"
                progress_by_id[scene_id]["started_at"] = chunk_started_at
                write_json(progress_path, progress)
                print(f"CHUNK_STARTED {scene_id} {chunk_started_at:.3f}", flush=True)
                try:
                    torch.cuda.synchronize()
                    with torch.autocast(device_type="cuda", dtype=torch.float16):
                        (sample_rate, audio_np), status, _srt_path = generate_speech_omni(
                            omni=omni, text=text, language="vi", reference_audio=str(ref_audio), ref_text=ref_text,
                            speed=speed, pitch_shift=pitch_shift,
                        )
                    torch.cuda.synchronize()
                    inference_seconds = time.monotonic() - chunk_started_clock
                    audio_np = np.asarray(audio_np)
                    if audio_np.size == 0 or not np.isfinite(audio_np).all():
                        raise RuntimeError(f"OmniVoice returned empty or invalid audio for {scene_id}")
                    peak = float(np.max(np.abs(audio_np)))
                    normalized = (audio_np / peak) * 0.89 if peak > 0 else audio_np
                    audio_int16 = (normalized * 32767).clip(-32768, 32767).astype(np.int16)
                    final_wav = chunks_dir / f"{scene_id}.wav"
                    temp_wav = chunks_dir / f"{scene_id}.{os.getpid()}.tmp.wav"
                    wavfile.write(str(temp_wav), sample_rate, audio_int16)
                    os.replace(temp_wav, final_wav)
                    raw_wav = final_wav.read_bytes()
                    duration = len(audio_int16) / float(sample_rate)
                    real_time_factor = inference_seconds / duration
                    slow_chunk = real_time_factor > SLOW_CHUNK_RTF_THRESHOLD
                    metadata = {
                        "scene_id": scene_id, "text": text, "text_sha256": sha256(text.encode("utf-8")),
                        "chunk_hash": chunk_hash, "profile_fingerprint": profile_fingerprint,
                        "voice_id": voice_id, "model": config["model"], "speed": speed,
                        "pitch_shift": pitch_shift, "sample_rate": int(sample_rate), "channels": 1,
                        "duration_seconds": duration, "wav_sha256": sha256(raw_wav),
                        "source": "colab", "runner_version": RUNNER_VERSION, "status": str(status),
                        "inference_precision": INFERENCE_PRECISION,
                        "weights_dtype": actual_weight_dtype,
                        "autocast_dtype": "torch.float16",
                        "attention_backend": ATTENTION_BACKEND,
                        "vad_input_dtype": "float32",
                        "inference_started_at": chunk_started_at,
                        "inference_seconds": inference_seconds,
                        "real_time_factor": real_time_factor,
                        "slow_chunk_warning": slow_chunk,
                        "generated_at": time.time(), "path": f"chunks/{scene_id}.wav",
                    }
                    write_json(metadata_dir / f"{scene_id}.json", metadata)
                    cache_wav_tmp = cache_dir / f"{chunk_hash}.{os.getpid()}.tmp.wav"
                    shutil.copy2(final_wav, cache_wav_tmp)
                    os.replace(cache_wav_tmp, cache_dir / f"{chunk_hash}.wav")
                    write_json(cache_dir / f"{chunk_hash}.json", metadata)
                    progress_by_id[scene_id].update({"state": "succeeded", "wav_sha256": metadata["wav_sha256"],
                                                     "duration_seconds": duration, "reused": False,
                                                     "started_at": chunk_started_at,
                                                     "completed_at": metadata["generated_at"],
                                                     "inference_seconds": inference_seconds,
                                                     "real_time_factor": real_time_factor,
                                                     "slow_chunk_warning": slow_chunk})
                    write_json(progress_path, progress)
                    print(f"CHUNK_SUCCEEDED {scene_id} audio={duration:.2f}s inference={inference_seconds:.2f}s "
                          f"rtf={real_time_factor:.2f} dtype={actual_weight_dtype}+fp16_autocast "
                          f"slow_warning={slow_chunk}", flush=True)
                except Exception as exc:
                    progress_by_id[scene_id].update({"state": "failed", "error": f"{type(exc).__name__}: {exc}",
                                                     "started_at": chunk_started_at,
                                                     "failed_at": time.time(),
                                                     "elapsed_seconds": time.monotonic() - chunk_started_clock})
                    write_json(progress_path, progress)
                    raise
        finally:
            fcntl.flock(gpu_lock.fileno(), fcntl.LOCK_UN)
            gpu_lock.close()

    segments = []
    for item in normalized_scenes:
        meta = json.loads((metadata_dir / f"{item['id']}.json").read_text(encoding="utf-8"))
        segments.append({"scene_id": item["id"], "text": item["text"], "path": f"chunks/{item['id']}.wav",
                         "chunk_hash": item["chunk_hash"], "duration_seconds": meta["duration_seconds"],
                         "inference_precision": meta.get("inference_precision", "fp32_legacy"),
                         "weights_dtype": meta.get("weights_dtype", "torch.float32"),
                         "autocast_dtype": meta.get("autocast_dtype", "none"),
                         "inference_started_at": meta.get("inference_started_at"),
                         "inference_seconds": meta.get("inference_seconds"),
                         "real_time_factor": meta.get("real_time_factor"),
                         "slow_chunk_warning": meta.get("slow_chunk_warning", False)})
    write_json(output_dir / "tts-result.json", {
        "request_id": request_id, "request_hash": request_hash, "voice": voice_id,
        "profile_fingerprint": profile_fingerprint,
        "engine": {"backend": "omnivoice", "model": config["model"], "device": torch.cuda.get_device_name(0) if pending else "cache",
                   "inference_precision": INFERENCE_PRECISION if pending else "cache_reused",
                   "weights_dtype": "torch.float32", "autocast_dtype": "torch.float16",
                   "attention_backend": ATTENTION_BACKEND,
                   "segment_precision_modes": sorted({segment["inference_precision"] for segment in segments}),
                   "sample_rate": segments[0]["duration_seconds"] and json.loads((metadata_dir / f"{segments[0]['scene_id']}.json").read_text(encoding="utf-8"))["sample_rate"]},
        "segments": segments,
    })
    print(f"PODCAST_PART_COMPLETE {request_id} {len(segments)} chunks", flush=True)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        raise
