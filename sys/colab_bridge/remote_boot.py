"""Bootstrap the Colab worker without storing credentials in source files."""

import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time


REPO_URL = "https://github.com/hongphuoc6104/tiktok-ytb.git"
BRANCH = os.environ.get("VIDEO_PILOT_COLAB_BRANCH", "feature/colab-offload")
LOCAL_DIR = Path("/content/tiktok-ytb")
SYS_DIR = LOCAL_DIR / "sys"
PORT = 8088
STATE_DIR = Path("/content/video-pilot-podcast-tts")
SERVER_PID_FILE = STATE_DIR / "server.pid"
TUNNEL_PID_FILE = STATE_DIR / "tunnel.pid"
TUNNEL_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


def run(cmd, check=True):
    """Run setup commands without echoing environment values or tokens."""
    print("[BOOT] Running:", Path(str(cmd[0])).name if cmd else "command")
    return subprocess.run(list(map(str, cmd)), check=check)


def setup_environment():
    print("[BOOT] Preparing the Colab worker environment")
    if not LOCAL_DIR.exists():
        run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, LOCAL_DIR])
    if not SYS_DIR.is_dir():
        raise FileNotFoundError(f"Worker source tree is missing at {SYS_DIR}")
    run(["apt-get", "update", "-qq"])
    run(["apt-get", "install", "-y", "-qq", "ffmpeg", "curl", "psmisc"])
    if subprocess.run(["which", "cloudflared"], capture_output=True).returncode != 0:
        package = Path("/tmp/cloudflared-linux-amd64.deb")
        url = ("https://github.com/cloudflare/cloudflared/releases/latest/download/"
               "cloudflared-linux-amd64.deb")
        run(["curl", "-fsSL", url, "-o", package])
        run(["dpkg", "-i", package])
        package.unlink(missing_ok=True)
        subprocess.run(["cloudflared", "--version"], check=True, capture_output=True, text=True)
    if subprocess.run(["which", "node"], capture_output=True).returncode != 0:
        run(["bash", "-lc", "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -"])
        run(["apt-get", "install", "-y", "-qq", "nodejs"])
    run([sys.executable, "-m", "pip", "install", "-q", "soundfile", "numpy", "scipy", "vieneu"])
    betterbox = Path("/content/BetterBox-TTS")
    if not betterbox.exists():
        run(["git", "clone", "--depth", "1", "https://github.com/nowtranminh1-TTS/BetterBox-TTS.git", betterbox])
    run([sys.executable, "-m", "pip", "install", "-q", "-r", betterbox / "general" / "requirements.txt"])
    # Colab's image may provide a newer torch than BetterBox's supported
    # torchvision/torchaudio wheels. Keep the CUDA trio on one tested release.
    run([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps",
         "--index-url", "https://download.pytorch.org/whl/cu128",
         "torch==2.8.0+cu128", "torchvision==0.23.0+cu128", "torchaudio==2.8.0+cu128"])
    model_dir = betterbox / "OmniVoice" / "modelOmniLocal"
    if not (model_dir / "config.json").is_file():
        run([sys.executable, "-c",
             "from huggingface_hub import snapshot_download; "
             f"snapshot_download(repo_id='kjanh/KhanhTTS-OmniVoice', local_dir={str(model_dir)!r})"])
    tv_target = Path("/content/torchvision-0.23.0-target")
    if not (tv_target / "torchvision").is_dir():
        run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", tv_target,
             "--index-url", "https://download.pytorch.org/whl/cu128", "torchvision==0.23.0+cu128"])
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tv_target) + os.pathsep + env.get("PYTHONPATH", "")
    check = "import torch,torchvision; assert torch.cuda.is_available(); " \
            "print({'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'torchvision':torchvision.__version__})"
    subprocess.run([sys.executable, "-c", check], env=env, check=True)
    (SYS_DIR / "podcast").mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    print("[BOOT] Colab environment is ready")


def _stop_pid_file(path: Path):
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.25)
    except (OSError, ValueError):
        pass
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _read_secret_once(token_file: Path) -> str:
    if not token_file.is_file():
        raise RuntimeError("A one-time podcast worker token file was not uploaded")
    token = token_file.read_text(encoding="utf-8").strip()
    try:
        token_file.unlink()
    except OSError:
        pass
    if len(token) < 32:
        raise RuntimeError("Podcast worker token is missing or too short")
    return token


def start_worker_and_tunnel(auth_token: str):
    if not auth_token:
        raise RuntimeError("Podcast worker authentication is required")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _stop_pid_file(TUNNEL_PID_FILE)
    _stop_pid_file(SERVER_PID_FILE)
    os.chdir(str(SYS_DIR))
    tv_target = Path("/content/torchvision-0.23.0-target")
    worker_env = os.environ.copy()
    worker_env["COLAB_AUTH_TOKEN"] = auth_token
    worker_env["PODCAST_TTS_TASK_DIR"] = str(STATE_DIR)
    worker_env["PYTHONPATH"] = str(tv_target) + os.pathsep + worker_env.get("PYTHONPATH", "")
    worker_log = (STATE_DIR / "worker.log").open("a", encoding="utf-8")
    server = subprocess.Popen([sys.executable, "-m", "colab_bridge.server", "--port", str(PORT)],
                              cwd=str(SYS_DIR), env=worker_env, stdin=subprocess.DEVNULL,
                              stdout=worker_log, stderr=subprocess.STDOUT, start_new_session=True)
    SERVER_PID_FILE.write_text(str(server.pid), encoding="utf-8")
    time.sleep(2)
    if server.poll() is not None:
        raise RuntimeError(f"Colab worker server exited during startup; inspect {STATE_DIR / 'worker.log'}")

    tunnel_log_path = STATE_DIR / "tunnel.log"
    tunnel_log = tunnel_log_path.open("a", encoding="utf-8")
    tunnel = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
                              cwd=str(STATE_DIR), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, bufsize=1, start_new_session=True)
    TUNNEL_PID_FILE.write_text(str(tunnel.pid), encoding="utf-8")
    found = queue.Queue(maxsize=1)

    def collect_tunnel_output():
        for line in tunnel.stdout or ():
            tunnel_log.write(line)
            tunnel_log.flush()
            match = TUNNEL_PATTERN.search(line)
            if match:
                try:
                    found.put_nowait(match.group(0))
                except queue.Full:
                    pass

    threading.Thread(target=collect_tunnel_output, name="podcast-tunnel-log", daemon=True).start()
    try:
        tunnel_url = found.get(timeout=40)
    except queue.Empty as exc:
        raise RuntimeError(f"Cloudflare Tunnel did not provide an endpoint; inspect {tunnel_log_path}") from exc
    print(f"COLAB_WORKER_ONLINE: {tunnel_url}", flush=True)
    return tunnel_url


def main():
    bootstrap_only = os.environ.get("PODCAST_BOOTSTRAP_ONLY") == "1"
    start_only = os.environ.get("PODCAST_START_WORKER") == "1"
    # `colab exec --env` variables persist in the remote notebook kernel.
    # A retry bootstrap must therefore take priority over a stale start flag.
    if bootstrap_only:
        setup_environment()
        for key in ("PODCAST_BOOTSTRAP_ONLY", "PODCAST_START_WORKER", "PODCAST_COLAB_TOKEN_FILE"):
            os.environ.pop(key, None)
        return
    if not start_only:
        setup_environment()
    token_path = Path(os.environ.get("PODCAST_COLAB_TOKEN_FILE", "/content/.podcast-colab-token-once"))
    try:
        token = _read_secret_once(token_path)
        start_worker_and_tunnel(token)
    finally:
        for key in ("PODCAST_BOOTSTRAP_ONLY", "PODCAST_START_WORKER", "PODCAST_COLAB_TOKEN_FILE"):
            os.environ.pop(key, None)


if __name__ == "__main__":
    main()
