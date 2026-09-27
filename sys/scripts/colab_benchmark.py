#!/usr/bin/env python3
"""Colab Offload Benchmark & Verification Utility.

Usage:
  # Check connection and GPU specs on Colab:
  python scripts/colab_benchmark.py status [--endpoint http://...]

  # Benchmark Remotion Render on Colab:
  python scripts/colab_benchmark.py render --seconds 60 --scenes 2

  # Benchmark TTS on Colab:
  python scripts/colab_benchmark.py tts --text "Năm mươi nghìn năm trước, trong một hang đá lạnh ngắt..."
"""

import argparse
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from colab_bridge.config import ColabConfig, get_colab_config
from colab_bridge.client import ColabClient, is_colab_available, get_colab_status
from scripts.render_benchmark import build as build_synthetic_project

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("colab_benchmark")


def cmd_status(args):
    endpoint = args.endpoint or get_colab_config(ROOT).endpoint
    token = args.token or get_colab_config(ROOT).auth_token
    print(f"🔍 Testing connection to Colab Worker at: {endpoint}")
    start = time.time()
    alive = is_colab_available(endpoint, auth_token=token, timeout=args.timeout)
    latency_ms = round((time.time() - start) * 1000, 1)

    if not alive:
        print(f"❌ Worker is OFFLINE or unreachable (latency: {latency_ms} ms)")
        print("\n💡 Gợi ý:")
        print("1. Hãy mở notebook 'sys/colab_bridge/notebooks/video_pilot_colab_worker.ipynb' trên Colab và bấm 'Run All'.")
        print("2. Đảm bảo bạn đã sao chép đúng URL Cloudflare Tunnel hoặc địa chỉ IP Tailscale.")
        print("3. Cập nhật URL bằng: export COLAB_ENDPOINT=\"https://...\" hoặc truyền --endpoint.")
        sys.exit(1)

    print(f"✅ Worker is ONLINE (ping: {latency_ms} ms)!\n")
    status = get_colab_status(endpoint, auth_token=token, timeout=args.timeout)
    gpu = status.get("gpu", {})
    print(f"🖥️  GPU: {gpu.get('device', 'Unknown')}")
    print(f"💾 VRAM: {gpu.get('vram_free_mb', 0)} MB free / {gpu.get('vram_total_mb', 0)} MB total")
    print(f"⚡ Capabilities: {', '.join(status.get('capabilities', []))}")


def cmd_render(args):
    cfg = get_colab_config(ROOT)
    if args.endpoint:
        cfg.endpoint = args.endpoint
    if args.token:
        cfg.auth_token = args.token

    client = ColabClient(cfg)
    print(f"🔍 Checking Colab worker at: {cfg.endpoint}...")
    if not client.is_alive():
        print("❌ Colab worker is not reachable. Cannot run remote render benchmark.")
        sys.exit(1)

    remote_out_dir = Path(args.out).resolve() if args.out else ROOT / "scratch/colab_outputs/render"
    remote_out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="colab_bench_render_") as tmp_dir:
        fixture_dir = Path(tmp_dir) / "fixture"
        fixture_dir.mkdir(parents=True)

        print(f"\n📦 Building synthetic project ({args.seconds}s, {args.scenes} scenes)...")
        t0 = time.time()
        build_synthetic_project(
            out=fixture_dir,
            seconds=args.seconds,
            scenes=args.scenes,
            beat_seconds=5.0,
            concurrency=args.concurrency,
            preset="veryfast",
            clips=args.clips,
        )
        print(f"✅ Project built in {round(time.time() - t0, 2)}s")

        # Run remote render on Colab
        print(f"\n🚀 Sending render job to Colab GPU NVENC...")
        t_start = time.time()
        res = client.render_remotion(
            props_path=fixture_dir / "props.json",
            public_dir=fixture_dir / "public",
            output_dir=remote_out_dir,
            timeout=args.timeout,
        )
        total_remote_s = round(time.time() - t_start, 2)
        print(f"🎉 Remote render completed successfully in {total_remote_s}s!")
        print(f"📁 Video đã tải về máy tại: {res['video_path']}")
        print(f"📊 Timings from Colab: {json.dumps(res.get('timings', []), indent=2)}")

        video_size_mb = round(Path(res['video_path']).stat().st_size / (1024 * 1024), 2)
        print(f"📦 File size: {video_size_mb} MB")


def cmd_tts(args):
    cfg = get_colab_config(ROOT)
    if args.endpoint:
        cfg.endpoint = args.endpoint
    if args.token:
        cfg.auth_token = args.token

    client = ColabClient(cfg)
    print(f"🔍 Checking Colab worker at: {cfg.endpoint}...")
    if not client.is_alive():
        print("❌ Colab worker is not reachable. Cannot run remote TTS benchmark.")
        sys.exit(1)

    out_dir = Path(args.out).resolve() if args.out else ROOT / "scratch/colab_outputs/tts"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "settings": {
            "tts_voice": "Minh Quân Pro",
            "tts_speed": 1.0,
            "tts_temperature": 0.65,
            "tts_top_p": 0.95,
            "tts_device": "auto",
            "tts_batch_size": 6,
        },
        "scenes": [
            {
                "scene_id": "SC01",
                "narration": args.text,
                "texts": [args.text],
                "retake": 0,
                "gaps": [],
                "tail": 0.5,
            }
        ],
    }

    print(f"\n🎙️ Sending TTS request to Colab GPU: '{args.text}'...")
    t_start = time.time()
    res = client.synthesize_tts(request_payload=payload, output_dir=out_dir, timeout=args.timeout)
    total_s = round(time.time() - t_start, 2)
    print(f"🎉 Remote TTS completed in {total_s}s!")
    print(f"📁 Audio WAV đã tải về máy tại: {out_dir / 'segment-000.wav'}")
    print(f"📊 Metadata: {json.dumps(res.get('metadata', {}), indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="Colab Benchmark & Diagnostic Utility")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Check Colab worker status and GPU specs")
    p_status.add_argument("--endpoint", default=None, help="Colab endpoint URL")
    p_status.add_argument("--token", default=None, help="Optional bearer token")
    p_status.add_argument("--timeout", type=float, default=5.0, help="Connection timeout in seconds")

    p_render = sub.add_parser("render", help="Run Remotion render benchmark on Colab")
    p_render.add_argument("--endpoint", default=None, help="Colab endpoint URL")
    p_render.add_argument("--token", default=None, help="Optional bearer token")
    p_render.add_argument("--out", type=Path, default=None, help="Directory to save downloaded video and stills")
    p_render.add_argument("--seconds", type=float, default=30.0, help="Synthetic video duration in seconds")
    p_render.add_argument("--scenes", type=int, default=2, help="Number of scenes")
    p_render.add_argument("--clips", type=int, default=1, help="Number of MP4 clips")
    p_render.add_argument("--concurrency", type=int, default=6, help="Remotion render concurrency")
    p_render.add_argument("--timeout", type=int, default=1200, help="Render timeout in seconds")

    p_tts = sub.add_parser("tts", help="Run TTS benchmark on Colab")
    p_tts.add_argument("--endpoint", default=None, help="Colab endpoint URL")
    p_tts.add_argument("--token", default=None, help="Optional bearer token")
    p_tts.add_argument("--out", type=Path, default=None, help="Directory to save downloaded WAV files")
    p_tts.add_argument("--text", default="Năm mươi nghìn năm trước, tổ tiên chúng ta bắt đầu học cách giữ lửa.", help="Text to synthesize")
    p_tts.add_argument("--timeout", type=int, default=300, help="TTS timeout in seconds")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "tts":
        cmd_tts(args)


if __name__ == "__main__":
    main()
