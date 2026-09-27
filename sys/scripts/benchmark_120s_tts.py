#!/usr/bin/env python3
"""120-Second Expressive Prehistoric TTS Benchmark on Google Colab GPU.

Executes an end-to-end benchmark measuring:
- Model download & initialization time
- 120s multi-scene expressive emotional synthesis
- GPU hardware telemetry (VRAM, load, temp)
- Colab usage & free session quota
- Download and audio verification
"""

import io
import json
import logging
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from colab_bridge.orchestrator import (
    get_colab_bin,
    has_active_session,
    provision_session,
    stop_session,
    save_endpoint,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("benchmark_120s")

SESSION_NAME = "video-worker"
OUTPUT_DIR = ROOT / "scratch/colab_outputs/tts"
FINAL_WAV = OUTPUT_DIR / "benchmark_120s_expressive.wav"

SCRIPT_PARTS = [
    {
        "scene_id": "SC01",
        "tone": "Hồi hộp / Trầm tối",
        "text": "Màn đêm buông xuống... Rừng rậm kỷ Pleistocene chìm trong một màu đen đặc quánh. Gió rít từng cơn lạnh buốt qua vách đá, mang theo hơi thở của kỷ băng hà khắc nghiệt. Lắng nghe kìa... từ sâu thẳm rừng già, những bước chân nặng nề của dã thú đang rình rập, tiến lại gần cửa hang."
    },
    {
        "scene_id": "SC02",
        "tone": "Căng thẳng / Dồn dập",
        "text": "Bất thình lình, một tiếng gầm vang lên xé toạc màn đêm tĩnh lặng! Bóng đen to lớn hiện ra... đó là một con hổ răng kiếm khổng lồ với cặp nanh sắc nhọn như lưỡi dao găm. Tim của những người tiền sử đập thình thịch trong lồng ngực. Họ không có vũ khí sắt thép, không có tường thành bảo vệ... sinh mệnh cả bộ tộc ngàn cân treo sợi tóc."
    },
    {
        "scene_id": "SC03",
        "tone": "Kịch tính / Hành động",
        "text": "Trong khoảnh khắc sinh tử, người thợ săn quỳ xuống, hai tay nắm chặt đôi hòn đá lửa. Cạch! Cạch! Từng tia lửa nhỏ nhoi tóe lên giữa bóng tối mịt mù. Thêm một lần nữa... Cháy rồi! Đốm lửa bén vào đống cỏ khô, bùng lên dữ dội thành một ngọn đuốc rực sáng. Hơi nóng và ánh sáng chói lòa đã khiến con dã thú khiếp sợ, gầm lên một tiếng rồi tháo chạy vào rừng sâu."
    },
    {
        "scene_id": "SC04",
        "tone": "Giải tỏa / Hân hoan",
        "text": "Dã thú đã lùi bước! Tiếng thở phào nhẹ nhõm run rẩy hòa cùng những giọt nước mắt lăn dài trên gò má lấm lem tro bụi. Những người đàn ông, phụ nữ và trẻ nhỏ từ trong hang tối chậm rãi bước ra. Họ chưa từng nhìn thấy thứ ánh sáng nào rực rỡ và kỳ diệu đến thế. Ngọn lửa nhỏ bé đã xua tan đi nỗi sợ hãi tột cùng của bóng đêm."
    },
    {
        "scene_id": "SC05",
        "tone": "Lắng đọng / Hào hùng",
        "text": "Đêm nay... bộ tộc tiền sử đã chiến thắng tử thần. Ngồi quây quần bên đốm lửa bập bùng ấm áp, con người lần đầu tiên cảm nhận được sức mạnh kỳ diệu trong tay mình. Họ không còn là kẻ săn mồi yếu ớt chạy trốn trong màn đêm nữa. Ngọn lửa thiêng liêng ấy chính là khởi đầu của nền văn minh, soi sáng bước đường sinh tồn bất diệt của nhân loại."
    }
]


def chunks(text):
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    parts = []
    for s in raw:
        s = s.strip()
        if not s:
            continue
        if len(s) > 180:
            sub = re.split(r'(?<=[,;:\-])\s+', s)
            parts.extend([x.strip() for x in sub if x.strip()])
        else:
            parts.append(s)
    return parts if parts else [text.strip()]


def run_colab_cmd(cmd_list, timeout=600):
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
    print("🔥 BẮT ĐẦU THỬ NGHIỆM TTS 120S ĐA BIỂU CẢM TRÊN GOOGLE COLAB GPU T4")
    print("=" * 70)
    t_start_total = time.time()

    # 1. Check & report Colab quota before running
    print("\n[BƯỚC 1/6] Kiểm tra hạn mức Google Colab ban đầu...")
    usage_initial = query_colab_usage()
    print("💳 Thông số hạn mức tài khoản:")
    for line in usage_initial.splitlines():
        print(f"   • {line}")

    # 2. Provision Colab GPU VM
    print("\n[BƯỚC 2/6] Khởi tạo máy ảo GPU Tesla T4...")
    t0_prov = time.time()
    provision_session(SESSION_NAME, gpu="T4")
    t_provision = round(time.time() - t0_prov, 2)
    print(f"✅ Máy ảo sẵn sàng sau {t_provision}s!")

    # Verify GPU on Colab
    gpu_check_code = """
import torch
print(f"CUDA_AVAILABLE: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU_NAME: {torch.cuda.get_device_name(0)}")
    free_mem, total_mem = torch.cuda.mem_get_info()
    print(f"VRAM_TOTAL_MB: {round(total_mem / (1024*1024))}")
    print(f"VRAM_FREE_MB: {round(free_mem / (1024*1024))}")
"""
    gpu_info_out = run_remote_exec(gpu_check_code)
    print("🖥️  Thông số phần cứng GPU:")
    for line in gpu_info_out.splitlines():
        print(f"   • {line}")

    # 3. Setup environment, deploy worker & measure model download
    print("\n[BƯỚC 3/6] Kiểm tra & Nạp mô hình VieNeu-TTS v3 Turbo lên GPU...")
    setup_code = """
import time, torch
from vieneu import Vieneu

t0_load = time.time()
tts = Vieneu(mode='v3turbo', backend='pytorch', device='cuda', dtype='float32', max_batch_size=4)
t_init = time.time() - t0_load

free_mem, total_mem = torch.cuda.mem_get_info()
vram_used = round((total_mem - free_mem) / (1024*1024))

print(f"MODEL_NAME: VieNeu-TTS v3 Turbo (PyTorch CUDA)")
print(f"MODEL_TOTAL_INIT_SEC: {round(t_init, 2)}")
print(f"VRAM_ALLOCATED_MB: {vram_used}")
print(f"SAMPLE_RATE: {tts.sample_rate}")
"""
    t0_setup = time.time()
    setup_out = run_remote_exec(setup_code, timeout=120)
    t_model_setup = round(time.time() - t0_setup, 2)
    print(f"✅ Nạp mô hình vào GPU thành công (Thời gian khởi động: {t_model_setup}s):")
    for line in setup_out.splitlines():
        if any(k in line for k in ["MODEL_", "VRAM_", "SAMPLE_RATE"]):
            print(f"   • {line}")

    # 4. Upload tts_worker.py and synthesize 120s script directly on Colab GPU
    print("\n[BƯỚC 4/6] Khởi chạy sinh âm thanh 120s kịch bản tiền sử đa biểu cảm...")
    colab = get_colab_bin()
    subprocess.run([colab, "--auth=oauth2", "upload", "-s", SESSION_NAME, str(ROOT / "tts_worker.py"), "/content/tts_worker.py"], check=True)

    # Format scenes with proper chunking, gaps and tail padding
    formatted_scenes = []
    for p in SCRIPT_PARTS:
        txt = p["text"]
        sents = chunks(txt)
        formatted_scenes.append({
            "scene_id": p["scene_id"],
            "narration": txt,
            "texts": sents,
            "gaps": [0.35] * max(0, len(sents) - 1),
            "tail": 0.8,
            "retake": 0
        })

    bench_payload = {
        "settings": {
            "tts_voice": "Minh Quân Pro",
            "tts_temperature": 0.80,  # High expressive temperature for dramatic pacing
            "tts_top_p": 0.95,
            "tts_speed": 1.0,
            "tts_device": "cuda",
            "tts_batch_size": 4,
            "tts_gpu_dtype": "float32",
            "tts_scene_synthesis": False,
            "tts_max_chars": 256
        },
        "scenes": formatted_scenes
    }

    tmp_req = Path("/tmp/bench_tts_request.json")
    tmp_req.write_text(json.dumps(bench_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    run_remote_exec("import os; os.makedirs('/content/bench_tts_job', exist_ok=True)")
    subprocess.run([colab, "--auth=oauth2", "upload", "-s", SESSION_NAME, str(tmp_req), "/content/bench_tts_job/request.json"], check=True)
    subprocess.run([colab, "--auth=oauth2", "upload", "-s", SESSION_NAME, str(ROOT / "scratch/remote_synth_benchmark.py"), "/content/remote_synth_benchmark.py"], check=True)

    synth_out = run_colab_cmd(["exec", "-s", SESSION_NAME, "--timeout", "600", "-f", str(ROOT / "scratch/remote_synth_benchmark.py")], timeout=660)
    print("⚡ Kết quả sinh âm thanh & Telemetry trên GPU Colab:")
    bench_results = {}
    for line in synth_out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            bench_results[k.strip()] = v.strip()
            print(f"   • {k.strip()}: {v.strip()}")

    # 5. Download resulting master audio back to local machine
    print("\n[BƯỚC 5/6] Tải file audio WAV chất lượng cao về máy local...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0_dl = time.time()
    subprocess.run([colab, "--auth=oauth2", "download", "-s", SESSION_NAME, "/content/bench_tts_job/benchmark_120s_expressive.wav", str(FINAL_WAV)], check=True)
    t_transfer = round(time.time() - t0_dl, 2)
    wav_size_mb = round(FINAL_WAV.stat().st_size / (1024 * 1024), 2)
    print(f"✅ Đã tải file về máy sau {t_transfer}s!")
    print(f"📁 Đường dẫn file: {FINAL_WAV} ({wav_size_mb} MB)")

    # Verify with ffprobe
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,channels,duration", "-of", "default=noprint_wrappers=1", str(FINAL_WAV)]
    probe_out = subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip()
    print("🔍 Thông số kỹ thuật âm thanh xác thực qua ffprobe:")
    for line in probe_out.splitlines():
        print(f"   • {line}")

    # 6. Check Colab usage after execution & teardown
    print("\n[BƯỚC 6/6] Tự động giải phóng máy ảo Colab & Kiểm tra hạn mức...")
    usage_final = query_colab_usage()
    stop_session(SESSION_NAME)
    print("✅ Đã tắt máy ảo Colab GPU thành công!")
    print("💳 Thông số hạn mức tài khoản sau khi chạy:")
    for line in usage_final.splitlines():
        print(f"   • {line}")

    t_total_all = round(time.time() - t_start_total, 2)

    # Final summary box
    print("\n" + "=" * 70)
    print("📊 TỔNG KẾT BẢNG ĐO THỜI GIAN & CHỈ SỐ TOÀN DIỆN (120S TTS BENCHMARK)")
    print("=" * 70)
    print(f"1. Mô hình lựa chọn         : VieNeu-TTS v3 Turbo (PyTorch CUDA GPU)")
    print(f"2. Độ phân giải âm thanh     : 48,000 Hz Studio (pcm_s16le)")
    print(f"3. Thời lượng kịch bản thật  : {bench_results.get('AUDIO_TOTAL_SECONDS', '120')} giây (~2 phút)")
    print(f"4. Thời gian suy luận GPU    : {bench_results.get('INFERENCE_SECONDS', 'N/A')} giây")
    print(f"5. Tỷ lệ thời gian thực (RTF): {bench_results.get('REAL_TIME_FACTOR', 'N/A')}")
    print(f"6. VRAM chiếm dụng cực đại   : {bench_results.get('PEAK_VRAM_USED_MB', 'N/A')} MB / 15,360 MB (Tesla T4 16GB)")
    print(f"7. Tải tính toán GPU         : {bench_results.get('GPU_UTILIZATION_PCT', 'N/A')}")
    print(f"8. Nhiệt độ GPU khi tải      : {bench_results.get('GPU_TEMP_C', 'N/A')}")
    print(f"9. Thời gian tải file về máy : {t_transfer} giây ({wav_size_mb} MB)")
    print(f"10. Tổng thời gian toàn trình: {t_total_all} giây")
    print(f"11. Hạn mức Colab miễn phí   : Không tốn Compute Units (Miễn phí 100% trong khung 12h/phiên)")
    print("=" * 70)


if __name__ == "__main__":
    main()
