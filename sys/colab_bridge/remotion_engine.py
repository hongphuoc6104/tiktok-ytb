"""Remotion execution worker for Google Colab environment."""

import io
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from typing import Dict, Any, Optional

logger = logging.getLogger("colab_bridge.remotion")


class ColabRemotionWorker:
    """Executes Remotion render jobs on Colab GPU."""

    def __init__(self, renderer_dir: Optional[Path] = None):
        # Default renderer directory on Colab or local repo
        self.renderer_dir = renderer_dir or Path(__file__).resolve().parents[1] / "renderer"
        self.render_script = self.renderer_dir / "render.mjs"

    def render_tarball(self, incoming_tar_bytes: bytes) -> bytes:
        """Unpack input tarball (props.json + public/), run Remotion render,
        and return output tarball (video.mp4, stills, timings, logs).
        """
        with tempfile.TemporaryDirectory(prefix="colab_render_") as tmp_dir:
            job_dir = Path(tmp_dir)

            # 1. Extract input archive
            with tarfile.open(fileobj=io.BytesIO(incoming_tar_bytes), mode="r:gz") as tar:
                if hasattr(tarfile, "data_filter"):
                    tar.extractall(path=job_dir, filter="data")
                else:
                    tar.extractall(path=job_dir)

            props_file = job_dir / "props.json"
            if not props_file.is_file():
                raise RuntimeError("Invalid render package: props.json missing")

            # 2. Adjust props for Colab environment if needed
            try:
                props = json.loads(props_file.read_text(encoding="utf-8"))
                # On Colab T4 GPU, set concurrency to match available CPU cores safely
                cpu_cores = os.cpu_count() or 2
                props["render_concurrency"] = cpu_cores
                # Ensure hardware acceleration
                props["render_gl"] = "angle"
                props_file.write_text(json.dumps(props, indent=2), encoding="utf-8")
            except Exception as e:
                logger.warning("Could not adjust props for Colab: %s", e)

            # 3. Execute Node Remotion renderer
            # Locate node binary
            node_bin = shutil.which("node") or "node"
            cmd = [node_bin, str(self.render_script), str(job_dir.resolve())]

            cwd = self.renderer_dir.parent  # sys/ directory
            log_file = job_dir / "render.log"
            logger.info("Executing Remotion: %s", " ".join(cmd))

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )
                log_file.write_text(f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}", encoding="utf-8")
                if proc.returncode != 0:
                    raise RuntimeError(f"Remotion process failed with code {proc.returncode}:\n{proc.stderr[-1000:]}")
            except subprocess.TimeoutExpired as e:
                log_file.write_text(f"TIMEOUT EXPIRED: {e}", encoding="utf-8")
                raise RuntimeError("Remotion render timed out on Colab") from e

            # 4. Collect outputs into response tarball
            out_buf = io.BytesIO()
            with tarfile.open(fileobj=out_buf, mode="w:gz") as out_tar:
                for item in job_dir.iterdir():
                    if item.name == "public":
                        continue  # Don't echo back the entire public dir to save bandwidth
                    if item.is_file():
                        out_tar.add(str(item), arcname=item.name)

            return out_buf.getvalue()
