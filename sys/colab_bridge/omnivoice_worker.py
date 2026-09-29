#!/usr/bin/env python3
"""OmniVoice Execution Worker for Colab GPU.

Processes a Video Pilot request.json and generates scene-by-scene audio WAVs
and a tts-result.json conforming 100% to schemas/audio.json.
"""

import json
import logging
import os
from pathlib import Path
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omnivoice_worker")


def main():
    if len(sys.argv) < 3:
        print("Usage: python omnivoice_worker.py <request.json> <out_dir>")
        sys.exit(1)

    req_file = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(req_file, "r", encoding="utf-8") as f:
        req = json.load(f)

    settings = req.get("settings", {})
    scenes = req.get("scenes", [])
    voice_id = settings.get("tts_voice", "van_vo")
    speed = float(settings.get("tts_speed", 1.0))
    pitch_shift = float(settings.get("pitch_shift", 1.0))

    # BetterBox-TTS environment setup on Colab
    betterbox_dir = Path("/content/BetterBox-TTS")
    if not betterbox_dir.is_dir():
        # Fallback to local search if running in local sandbox/test
        alt_betterbox = Path(__file__).resolve().parents[1] / "BetterBox-TTS"
        if alt_betterbox.is_dir():
            betterbox_dir = alt_betterbox

    if str(betterbox_dir) not in sys.path:
        sys.path.insert(0, str(betterbox_dir))

    try:
        os.chdir(str(betterbox_dir))
    except Exception as e:
        logger.warning("Could not change working directory to %s: %s", betterbox_dir, e)

    import numpy as np
    import scipy.io.wavfile as wavfile
    from OmniVoice.omnivoice_inference.ttsOmni import Omni, generate_speech_omni

    # 1. Resolve Voice Profile
    # Check assets/voices first
    root_sys = Path(__file__).resolve().parents[1]
    voice_dir = root_sys / "assets" / "voices" / voice_id
    ref_audio = None
    ref_text = None

    if voice_dir.is_dir():
        cfg_path = voice_dir / "voice_config.json"
        if cfg_path.is_file():
            try:
                vcfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                ref_wav_name = vcfg.get("files", {}).get("reference_wav", f"{voice_id}.wav")
                ref_txt_name = vcfg.get("files", {}).get("transcript_txt", f"{voice_id}.txt")
                ref_audio = str(voice_dir / ref_wav_name)
                ref_text = (voice_dir / ref_txt_name).read_text(encoding="utf-8").strip()
            except Exception as e:
                logger.warning("Failed to load voice_config.json from %s: %s", voice_dir, e)

    # Fallback to /content/BetterBox-TTS/wavs/
    if not ref_audio or not os.path.exists(ref_audio):
        candidate_wav = betterbox_dir / "wavs" / f"{voice_id}.wav"
        candidate_txt = betterbox_dir / "wavs" / f"{voice_id}.txt"
        if candidate_wav.is_file() and candidate_txt.is_file():
            ref_audio = str(candidate_wav)
            ref_text = candidate_txt.read_text(encoding="utf-8").strip()

    if not ref_audio or not os.path.exists(ref_audio) or not ref_text:
        raise FileNotFoundError(
            f"Voice profile for '{voice_id}' not found in assets/voices/ or {betterbox_dir}/wavs/"
        )

    logger.info("Loaded voice profile: %s", voice_id)
    logger.info("  Reference Audio: %s", ref_audio)
    logger.info("  Reference Text: %s", ref_text[:80] + "..." if len(ref_text) > 80 else ref_text)

    # 2. Load OmniVoice Model
    model_path = "/content/BetterBox-TTS/OmniVoice/modelOmniLocal"
    if not os.path.exists(model_path):
        model_path = "kjanh/KhanhTTS-OmniVoice"

    logger.info("Initializing OmniVoice model from: %s", model_path)
    t0 = time.time()
    omni = Omni(model_path=model_path, device="cuda")
    omni.loadModelOmni()
    logger.info("OmniVoice model loaded in %.2fs", time.time() - t0)

    # 3. Synthesize Each Scene
    segments = []
    total_audio_samples = 0
    sample_rate = 24000

    for idx, sc in enumerate(scenes):
        sc_id = sc.get("id", f"S{idx+1}")
        # Extract text for the scene
        if "texts" in sc and isinstance(sc["texts"], list):
            scene_text = " ".join(t.strip() for t in sc["texts"] if t.strip())
        elif "narration" in sc:
            scene_text = str(sc["narration"]).strip()
        else:
            scene_text = ""

        if not scene_text:
            logger.warning("Scene %s has no text! Skipping.", sc_id)
            continue

        logger.info("Synthesizing Scene %s (%d chars): '%s'...", sc_id, len(scene_text), scene_text[:60])
        t_start = time.time()

        (sr, audio_np), status, srt_path = generate_speech_omni(
            omni=omni,
            text=scene_text,
            language="vi",
            reference_audio=ref_audio,
            ref_text=ref_text,
            speed=speed,
            pitch_shift=pitch_shift,
        )
        sample_rate = sr
        duration_s = len(audio_np) / sr
        logger.info("Scene %s generated in %.2fs (duration: %.2fs)", sc_id, time.time() - t_start, duration_s)

        # Apply -1.01 dBFS Headroom Normalization (prevents digital clipping)
        max_val = np.max(np.abs(audio_np))
        if max_val > 0:
            audio_norm = (audio_np / max_val) * 0.89
        else:
            audio_norm = audio_np

        audio_int16 = (audio_norm * 32767).clip(-32768, 32767).astype(np.int16)
        out_wav_name = f"{sc_id}.wav"
        out_wav_path = out_dir / out_wav_name
        wavfile.write(str(out_wav_path), sr, audio_int16)

        total_audio_samples += len(audio_int16)
        segments.append({
            "scene_id": sc_id,
            "text": scene_text,
            "path": out_wav_name,
        })

    # 4. Generate tts-result.json
    result_meta = {
        "voice": voice_id,
        "engine": {
            "backend": "pytorch",
            "precision": "float32",
            "device": "Tesla T4",
            "sample_rate": sample_rate,
        },
        "segments": segments,
    }
    result_json_path = out_dir / "tts-result.json"
    result_json_path.write_text(json.dumps(result_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("TTS Synthesis successfully finished. Saved results to %s", result_json_path)


if __name__ == "__main__":
    main()
