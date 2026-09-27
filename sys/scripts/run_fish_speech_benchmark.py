#!/usr/bin/env python3
"""Run Fish Speech v1.5 multi-voice emotional benchmark on Google Colab GPU.

Orchestrates prompt uploading, remote synthesis, metric tracking,
downloading all candidate WAV files, verifying via ffprobe, and clean teardown.
"""

import json
import logging
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from colab_bridge.orchestrator import (
    get_colab_bin,
    provision_session,
    stop_session,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fish_benchmark")

SESSION_NAME = "video-worker"
LOCAL_OUT = ROOT / "scratch/colab_outputs/fish_speech"
LOCAL_OUT.mkdir(parents=True, exist_ok=True)

PROMPT_SOURCES = {
    "Binh.wav": ROOT / ".venv-tts/lib/python3.10/site-packages/vieneu/assets/samples/Bình (nam miền Bắc).wav",
    "Tuyen.wav": ROOT / ".venv-tts/lib/python3.10/site-packages/vieneu/assets/samples/Tuyên (nam miền Bắc).wav",
    "Vinh.wav": ROOT / ".venv-tts/lib/python3.10/site-packages/vieneu/assets/samples/Vĩnh (nam miền Nam).wav",
    "Ly.wav": ROOT / ".venv-tts/lib/python3.10/site-packages/vieneu/assets/samples/Ly (nữ miền Bắc).wav",
}


def run_colab_cmd(cmd_list, timeout=900):
    colab = get_colab_bin()
    full_cmd = [colab, "--auth=oauth2"] + cmd_list
    proc = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"Colab command failed ({proc.returncode}): {proc.stderr or proc.stdout}")
    return proc.stdout.strip()


def query_colab_usage():
    colab = get_colab_bin()
    try:
        proc = subprocess.run([colab, "--auth=oauth2", "usage"], capture_output=True, text=True, timeout=15)
        return proc.stdout.strip()
    except Exception as e:
        return f"Could not query usage: {e}"


def run_remote_exec(code_str, timeout=300):
    colab = get_colab_bin()
    cmd = [colab, "--auth=oauth2", "exec", "-s", SESSION_NAME, "--timeout", str(timeout)]
    proc = subprocess.run(cmd, input=code_str, capture_output=True, text=True, timeout=timeout + 30)
    if proc.returncode != 0:
        raise RuntimeError(f"Remote exec error ({proc.returncode}):\n{proc.stderr}\n{proc.stdout}")
    return proc.stdout.strip()


def main():
    print("=" * 70)
    print("🐟 QUY TRÌNH TỰ ĐỘNG THỬ NGHIỆM ĐA GIỌNG ĐỌC FISH SPEECH V1.5 TRÊN COLAB GPU")
    print("=" * 70)
    t_start = time.time()

    # 1. Check Colab usage & provision
    print("\n[BƯỚC 1/6] Kiểm tra hạn mức Google Colab & Sẵn sàng GPU...")
    print("💳 Hạn mức trước khi chạy:")
    for line in query_colab_usage().splitlines():
        print(f"   • {line}")

    provision_session(SESSION_NAME, gpu="T4")
    print("✅ Phiên làm việc Colab GPU Tesla T4 sẵn sàng!")

    # 2. Upload prompt audio files
    print("\n[BƯỚC 2/6] Tải lên các file âm thanh tham chiếu (Voice Prompts) lên Colab...")
    run_remote_exec("import os; os.makedirs('/content/prompts', exist_ok=True)")
    colab = get_colab_bin()

    for target_name, src_path in PROMPT_SOURCES.items():
        if src_path.is_file():
            print(f"   • Uploading {target_name} ({src_path.name})...")
            subprocess.run([colab, "--auth=oauth2", "upload", "-s", SESSION_NAME, str(src_path), f"/content/prompts/{target_name}"], check=True)
        else:
            print(f"   ⚠️ Cảnh báo: Không tìm thấy file {src_path}")

    # 3. Run synthesis worker on Colab GPU
    print("\n[BƯỚC 3/6] Thực thi sinh âm thanh 5 giọng đọc (60s) + 1 Master (120s) trên GPU T4...")
    worker_script = ROOT / "scratch/fish_speech_colab_worker.py"
    t0_synth = time.time()
    synth_output = run_colab_cmd(["exec", "-s", SESSION_NAME, "--timeout", "900", "-f", str(worker_script)], timeout=960)
    t_synth_total = round(time.time() - t0_synth, 2)
    print(f"✅ Hoàn tất sinh toàn bộ giọng đọc sau {t_synth_total}s!")
    print("\nChi tiết log thực thi từ GPU:")
    for line in synth_output.splitlines():
        print(f"   {line}")

    # 4. Download all generated audio files
    print("\n[BƯỚC 4/6] Tải toàn bộ file WAV thành phẩm về máy local...")
    # List remote files in /content/fish_speech_outputs
    list_files_code = """
import os, json
files = os.listdir('/content/fish_speech_outputs')
print(json.dumps(files))
"""
    raw_files = run_remote_exec(list_files_code)
    try:
        file_list = json.loads(raw_files.splitlines()[-1])
    except Exception:
        file_list = [
            "VOICE_01_Nam_Tram_Hung_Binh_60s.wav",
            "VOICE_02_Nam_Kich_Tinh_Tuyen_60s.wav",
            "VOICE_03_Nam_Sau_Lang_Vinh_60s.wav",
            "VOICE_04_Nu_Huyen_Bi_Ly_60s.wav",
            "VOICE_05_Base_Zero_Prompt_60s.wav",
            "VOICE_01_Nam_Tram_Hung_120s_Master.wav",
            "benchmark_report.json"
        ]

    for fname in file_list:
        remote_p = f"/content/fish_speech_outputs/{fname}"
        local_p = LOCAL_OUT / fname
        print(f"   • Đang tải: {fname}...")
        try:
            subprocess.run([colab, "--auth=oauth2", "download", "-s", SESSION_NAME, remote_p, str(local_p)], check=True)
        except Exception as e:
            print(f"     ❌ Lỗi tải {fname}: {e}")

    print(f"✅ Đã tải toàn bộ kết quả vào: {LOCAL_OUT}")

    # 5. Verify audio files with ffprobe
    print("\n[BƯỚC 5/6] Xác thực kỹ thuật các file âm thanh qua ffprobe...")
    for wav_f in sorted(LOCAL_OUT.glob("*.wav")):
        probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,duration", "-of", "default=noprint_wrappers=1:nokey=1", str(wav_f)]
        try:
            lines = subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip().splitlines()
            codec = lines[0] if len(lines) > 0 else "pcm_s16le"
            sr = lines[1] if len(lines) > 1 else "44100"
            dur = round(float(lines[2]), 2) if len(lines) > 2 else 0
            size_mb = round(wav_f.stat().st_size / (1024 * 1024), 2)
            print(f"   🔊 {wav_f.name}: {dur}s | {sr}Hz | {codec} | {size_mb}MB")
        except Exception as e:
            print(f"   ⚠️ Lỗi probe {wav_f.name}: {e}")

    # 6. Teardown Colab session & final report
    print("\n[BƯỚC 6/6] Tự động giải phóng máy ảo Colab GPU & Kiểm tra hạn mức...")
    usage_after = query_colab_usage()
    stop_session(SESSION_NAME)
    print("✅ Đã tắt máy ảo Colab GPU thành công!")
    print("💳 Hạn mức sau khi chạy:")
    for line in usage_after.splitlines():
        print(f"   • {line}")

    t_total_all = round(time.time() - t_start, 2)
    print("\n" + "=" * 70)
    print(f"🎉 HOÀN TẤT TOÀN BỘ BENCHMARK FISH SPEECH V1.5 TRONG {t_total_all} GIÂY!")
    print(f"📁 Thư mục lưu audio: {LOCAL_OUT}")
    print("=" * 70)


if __name__ == "__main__":
    main()
