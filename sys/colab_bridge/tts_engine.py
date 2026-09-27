"""TTS execution worker for Google Colab environment.

Runs heavy neural TTS models with full GPU acceleration (16GB Tesla T4 VRAM)
and supports expressive acting directions (breaths, dramatic pauses, pacing)
and neural voice cloning (OmniVoice-8400h).
"""

import io
import json
import logging
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger("colab_bridge.tts")


class ColabTTSWorker:
    """Executes high-VRAM TTS and expressive audio direction on Colab."""

    def __init__(self, sys_dir: Optional[Path] = None):
        self.sys_dir = sys_dir or Path(__file__).resolve().parents[1]
        self.tts_worker_script = self.sys_dir / "tts_worker.py"
        self.omnivoice_script = self.sys_dir / "colab_bridge" / "omnivoice_worker.py"

    def synthesize_to_tarball(self, request_payload: Dict[str, Any]) -> bytes:
        """Run TTS synthesis with GPU acceleration, returning a tar.gz with all WAVs and metadata."""
        with tempfile.TemporaryDirectory(prefix="colab_tts_") as tmp_dir:
            out_dir = Path(tmp_dir)

            # 1. Prepare request file
            settings = request_payload.setdefault("settings", {})
            voice = settings.get("tts_voice", "Minh Quân Pro")

            # Check if requested voice is a cloned voice or OmniVoice engine
            is_omnivoice = (
                settings.get("tts_engine") == "omnivoice"
                or (self.sys_dir / "assets" / "voices" / voice).is_dir()
                or voice in ("van_vo", "vui_ve")
                or Path(f"/content/BetterBox-TTS/wavs/{voice}.wav").is_file()
            )

            request_file = out_dir / "request.json"
            request_file.write_text(json.dumps(request_payload, indent=2, ensure_ascii=False), encoding="utf-8")

            if is_omnivoice:
                # Use OmniVoice execution worker
                cmd = ["python3", str(self.omnivoice_script), str(request_file), str(out_dir)]
                logger.info("Executing OmniVoice TTS on Colab GPU: %s", " ".join(cmd))
            else:
                # Default settings for VieNeu on GPU
                settings.setdefault("tts_voice", "Minh Quân Pro")
                settings.setdefault("tts_temperature", 0.65)
                settings.setdefault("tts_top_p", 0.95)
                settings.setdefault("tts_device", "auto")
                settings.setdefault("tts_backend", "pytorch")
                settings.setdefault("tts_batch_size", 6)
                settings.setdefault("tts_gpu_dtype", "float32")

                # Rewrite request file with defaulted settings
                request_file.write_text(json.dumps(request_payload, indent=2, ensure_ascii=False), encoding="utf-8")

                # Find python executable with PyTorch & Vieneu
                py_candidates = [
                    self.sys_dir / ".venv-tts-gpu/bin/python",
                    self.sys_dir / ".venv-tts/bin/python",
                    self.sys_dir / ".venv/bin/python",
                    Path(os.sys.executable),
                ]
                python_bin = None
                for cand in py_candidates:
                    if cand.is_file():
                        python_bin = str(cand)
                        break
                if not python_bin:
                    python_bin = "python3"

                cmd = [python_bin, str(self.tts_worker_script), str(request_file), str(out_dir)]
                logger.info("Executing VieNeu TTS on Colab GPU: %s", " ".join(cmd))

            proc = subprocess.run(
                cmd,
                cwd=str(self.sys_dir),
                capture_output=True,
                text=True,
                timeout=1800,
            )
            log_file = out_dir / "tts.log"
            log_file.write_text(f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}", encoding="utf-8")

            if proc.returncode != 0:
                raise RuntimeError(f"TTS synthesis failed with code {proc.returncode}:\n{proc.stderr[-1000:]}")

            # 4. Pack output files into response tar.gz
            out_buf = io.BytesIO()
            with tarfile.open(fileobj=out_buf, mode="w:gz") as out_tar:
                for item in out_dir.iterdir():
                    if item.is_file() and item.name != "request.json":
                        out_tar.add(str(item), arcname=item.name)

            return out_buf.getvalue()
