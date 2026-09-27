"""Remote Bootstrap Script for Google Colab VM.

Executed on the remote Colab kernel (via `colab exec` or notebook) to prepare
the environment, launch the worker daemon, and establish the tunnel.
"""

import os
from pathlib import Path
import re
import subprocess
import sys
import time

REPO_URL = "https://github.com/hongphuoc6104/tiktok-ytb.git"
BRANCH = "feature/colab-offload"
LOCAL_DIR = Path("/content/tiktok-ytb")
SYS_DIR = LOCAL_DIR / "sys"
PORT = 8088


def run(cmd, shell=True, check=True):
    print(f"[BOOT] Executing: {cmd}")
    return subprocess.run(cmd, shell=shell, check=check)


def setup_environment():
    print("=" * 60)
    print("🚀 Initializing Video Pilot Worker on Google Colab GPU...")
    print("=" * 60)

    # 1. Clone or update codebase
    if not LOCAL_DIR.exists():
        run(f"git clone -b {BRANCH} {REPO_URL} {LOCAL_DIR}")
    else:
        run(f"cd {LOCAL_DIR} && git fetch && git checkout {BRANCH} && git pull")

    # 2. System packages (ffmpeg, nodejs, cloudflared)
    run("apt-get update -qq && apt-get install -y -qq ffmpeg curl")
    node_check = subprocess.run("which node", shell=True, capture_output=True)
    if node_check.returncode != 0:
        run("curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null")
        run("apt-get install -y -qq nodejs")

    # 3. Node modules for Remotion
    run(f"cd {SYS_DIR} && npm install --silent")

    # 4. Python dependencies
    run("pip install -q soundfile numpy scipy vieneu")

    # 5. Cloudflared tunnel binary
    cf_check = subprocess.run("which cloudflared", shell=True, capture_output=True)
    if cf_check.returncode != 0:
        run("wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
        run("dpkg -i cloudflared-linux-amd64.deb > /dev/null 2>&1 || true")

    print("✅ Environment ready!")


def start_worker_and_tunnel():
    os.chdir(str(SYS_DIR))
    sys.path.insert(0, str(SYS_DIR))

    # 1. Kill any existing instances on port
    subprocess.run(f"fuser -k {PORT}/tcp 2>/dev/null || true", shell=True)

    # 2. Start Worker Server in background
    server_cmd = f"python3 -m colab_bridge.server --port {PORT}"
    server_proc = subprocess.Popen(
        server_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(2)

    # 3. Start Cloudflare Tunnel
    tunnel_cmd = f"cloudflared tunnel --url http://localhost:{PORT}"
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    tunnel_url = None
    for _ in range(40):
        line = tunnel_proc.stdout.readline()
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            break
        time.sleep(0.5)

    if not tunnel_url:
        raise RuntimeError("Failed to obtain Cloudflare Tunnel URL within 20s")

    print("\n" + "=" * 60)
    print(f"COLAB_WORKER_ONLINE: {tunnel_url}")
    print("=" * 60 + "\n")
    return tunnel_url


if __name__ == "__main__":
    setup_environment()
    url = start_worker_and_tunnel()
    # Keep script alive so Colab doesn't shut down the tunnel
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping worker...")
