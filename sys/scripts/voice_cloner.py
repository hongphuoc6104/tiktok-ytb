#!/usr/bin/env python3
"""Video Pilot Voice Cloner Tool.

Extracts, normalizes, transcribes (via Chunkformer ASR on Colab GPU),
and builds permanent voice profiles in sys/assets/voices/<voice_id>/
for expressive speech synthesis with OmniVoice.
"""

import argparse
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("voice_cloner")


def run_cmd(cmd, cwd=None, check=True):
    logger.info("Executing: %s", " ".join(cmd) if isinstance(cmd, list) else cmd)
    return subprocess.run(
        cmd,
        cwd=cwd,
        shell=isinstance(cmd, str),
        check=check,
        capture_output=True,
        text=True,
    )


def extract_audio_from_source(source: str, start: float, duration: float, out_wav: Path):
    """Download from YouTube URL or slice local audio into 24kHz Mono PCM16 WAV."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    if source.startswith("http://") or source.startswith("https://"):
        logger.info("Extracting %ss audio starting at %ss from %s", duration, start, source)
        # Check yt-dlp
        if not shutil.which("yt-dlp"):
            raise RuntimeError("yt-dlp is required to download audio from URLs. Please install yt-dlp.")

        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp_dl:
            tmp_dl_path = tmp_dl.name

        try:
            # Download audio stream
            dl_cmd = [
                "yt-dlp",
                "-f", "bestaudio[ext=m4a]/bestaudio",
                "--extract-audio",
                "-o", tmp_dl_path,
                source,
            ]
            run_cmd(dl_cmd)

            # Slice and resample to 24kHz Mono 16-bit
            ff_cmd = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-t", str(duration),
                "-i", tmp_dl_path,
                "-ar", "24000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                str(out_wav),
            ]
            run_cmd(ff_cmd)
        finally:
            if os.path.exists(tmp_dl_path):
                os.remove(tmp_dl_path)
    else:
        # Local audio file
        src_path = Path(source).resolve()
        if not src_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {src_path}")
        ff_cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(duration),
            "-i", str(src_path),
            "-ar", "24000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(out_wav),
        ]
        run_cmd(ff_cmd)


def transcribe_on_colab(wav_path: Path, session: str = "video-worker") -> str:
    """Upload WAV to Colab and run Chunkformer ASR to extract Vietnamese text."""
    remote_wav = f"/content/BetterBox-TTS/wavs/{wav_path.name}"
    remote_txt = f"/content/BetterBox-TTS/wavs/{wav_path.stem}.txt"

    logger.info("Uploading %s to Colab session '%s'...", wav_path.name, session)
    run_cmd(["colab", "upload", "-s", session, str(wav_path), remote_wav])

    # Run ASR script via colab exec
    asr_py = f"""
import os, sys
try:
    from asr.transcribe_chunkformer import transcribe
except ImportError:
    sys.path.append('/content/BetterBox-TTS')
    from asr.transcribe_chunkformer import transcribe

text = transcribe('{remote_wav}')
with open('{remote_txt}', 'w', encoding='utf-8') as f:
    f.write(text.strip())
print('TRANSCRIPT_RESULT:' + text.strip())
"""
    logger.info("Running Chunkformer ASR on Colab GPU...")
    res = subprocess.run(
        ["colab", "exec", "-s", session],
        input=asr_py,
        capture_output=True,
        text=True,
        check=True,
    )

    transcript = ""
    for line in res.stdout.splitlines():
        if "TRANSCRIPT_RESULT:" in line:
            transcript = line.split("TRANSCRIPT_RESULT:", 1)[1].strip()
            break

    if not transcript:
        # Try reading remote file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_txt:
            tmp_txt_path = tmp_txt.name
        try:
            run_cmd(["colab", "download", "-s", session, remote_txt, tmp_txt_path])
            transcript = Path(tmp_txt_path).read_text(encoding="utf-8").strip()
        finally:
            if os.path.exists(tmp_txt_path):
                os.remove(tmp_txt_path)

    return transcript


def create_voice_profile(
    voice_id: str,
    source: str,
    start: float,
    duration: float,
    name: str = "",
    session: str = "video-worker",
    target_dir: str = "",
):
    root_sys = Path(__file__).resolve().parents[1]
    out_dir = Path(target_dir) if target_dir else root_sys / "assets" / "voices" / voice_id
    out_dir.mkdir(parents=True, exist_ok=True)

    wav_file = out_dir / f"{voice_id}.wav"
    txt_file = out_dir / f"{voice_id}.txt"
    config_file = out_dir / "voice_config.json"

    # Step 1: Extract audio
    logger.info("Step 1: Extracting reference audio for voice '%s'...", voice_id)
    extract_audio_from_source(source, start, duration, wav_file)

    # Step 2: Transcribe via Chunkformer ASR
    logger.info("Step 2: Transcribing audio with Chunkformer on Colab...")
    transcript = transcribe_on_colab(wav_file, session=session)
    logger.info("Transcription result:\n  '%s'", transcript)
    txt_file.write_text(transcript, encoding="utf-8")

    # Step 3: Write voice_config.json
    cfg = {
        "voice_id": voice_id,
        "name": name or f"Cloned Voice ({voice_id})",
        "model": "kjanh/KhanhTTS-OmniVoice",
        "engine": "OmniVoice-8400h",
        "source": source,
        "sample_rate": 24000,
        "channels": 1,
        "recommended_params": {
            "speed": 1.0,
            "pitch_shift": 1.0,
            "guidance_scale": 3.0,
            "layer_penalty_factor": 5.0,
            "audio_chunk_duration": 0.0,
            "audio_chunk_threshold": 60.0,
            "torch_compile": False,
            "fix_silent_chopping": False,
            "peak_headroom_dbfs": -1.0,
            "crossfade_ms": 5,
        },
        "files": {
            "reference_wav": f"{voice_id}.wav",
            "transcript_txt": f"{voice_id}.txt",
        },
        "style_tags": ["storytelling", "expressive", "neural_clone"],
    }
    config_file.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("✅ Successfully created voice profile at: %s", out_dir)
    logger.info("Files created:")
    logger.info("  - %s (%d bytes)", wav_file.name, wav_file.stat().st_size)
    logger.info("  - %s (%d chars)", txt_file.name, len(transcript))
    logger.info("  - %s", config_file.name)
    return out_dir


def main():
    parser = argparse.ArgumentParser(description="Video Pilot Voice Cloner Tool")
    parser.add_argument("--voice-id", required=True, help="Unique identifier for the voice (e.g. van_vo)")
    parser.add_argument("--url", default="", help="YouTube video URL")
    parser.add_argument("--wav", default="", help="Local WAV file path")
    parser.add_argument("--name", default="", help="Human readable name for the voice")
    parser.add_argument("--start", type=float, default=0.0, help="Start offset in seconds (default 0)")
    parser.add_argument("--duration", type=float, default=15.0, help="Duration in seconds (default 15)")
    parser.add_argument("--session", default="video-worker", help="Colab session name (default 'video-worker')")
    parser.add_argument("--out-dir", default="", help="Custom output directory")

    args = parser.parse_args()
    source = args.url or args.wav
    if not source:
        parser.error("Either --url or --wav must be provided.")

    create_voice_profile(
        voice_id=args.voice_id,
        source=source,
        start=args.start,
        duration=args.duration,
        name=args.name,
        session=args.session,
        target_dir=args.out_dir,
    )


if __name__ == "__main__":
    main()
