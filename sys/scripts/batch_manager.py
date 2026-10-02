#!/home/hongphuoc6104/Desktop/pipelineFlow/sys/.venv-tts-gpu/bin/python3
"""
Bộ Quản Lý Lô Sản Xuất Video Micro-Drama (Hybrid Batch Manager) v3.0
Mô hình Phân Tầng Bất Đối Xứng (Two-Tier Asymmetric Hybrid Batching):
- Máy Local (Zero Heavy Lift): Tạo kịch bản nhanh, kiểm định chất lượng (audit), gom lỗi, lắp ráp & render.
- Colab CLI (Cloud Workhorse): GPU T4 16GB VRAM xử lý 100% TTS Vieneu Adam bựa và sửa chữa hàng loạt tập trung (Batch Retake).
"""

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
BATCH_DIR = ROOT / 'batches'
VIDEO_EXPORT_DIR = ROOT.parent / 'video'
SFX_DIR = ROOT / 'assets/audio/sfx'
BGM_DIR = ROOT / 'assets/audio/bgm'
VENV_TTS_PYTHON = ROOT / '.venv-tts-gpu/bin/python3'
BRAIN = Path("/home/hongphuoc6104/.gemini/antigravity-ide/brain/83a11ada-95e4-4701-a588-0e916a012623")
COLAB_ACCOUNT = "account-04"
COLAB_SESSION = "video-pilot-tts"

# ==========================================
# 1. TẠO GÓI LÔ KỊCH BẢN TẠI MÁY LOCAL
# ==========================================

def load_bank_items(start_idx=32, count=50):
    scenarios_file = ROOT / 'scripts/drama_scenarios_50.json'
    if scenarios_file.exists():
        data = json.loads(scenarios_file.read_text(encoding='utf-8'))
        return data[:count]
        
    bank_file = ROOT / 'vocab/bank.jsonl'
    lines = [json.loads(line) for line in bank_file.read_text().splitlines() if line.strip()]
    selected = lines[start_idx - 1 : start_idx - 1 + count]
    
    items = []
    for offset, it in enumerate(selected):
        idx = start_idx + offset
        word = it.get('word')
        gloss = it.get('gloss_vi')
        eid = it.get('id')
        w_upper = word.upper()
        
        sc01 = f"Tình thế cấp bách ngay trước mắt rồi, phải hành động nhanh kẻo trễ!"
        sc02 = f"Hành động này trong tiếng Anh dùng ngay từ: {w_upper}!"
        sc03 = f"Cùng thực hiện liền nha: \"Let's {word}!\" Đọc to theo tui nè: {w_upper}!"
        sc04 = f"Vừa làm xong hớn hở quay lại thì thấy mình làm nhầm việc của sếp!"
            
        cues = [
            {"text": sc01[:23], "start": 0.0, "end": 1.7},
            {"text": "Nhanh lên nào!", "start": 1.7, "end": 3.4},
            {"text": "Tiếng Anh gọi là:", "start": 3.6, "end": 5.0},
            {"text": f"{w_upper}!", "start": 5.0, "end": 7.2},
            {"text": f"Nhớ từ này nha: {word}", "start": 7.4, "end": 9.2},
            {"text": f"(Cùng đọc to: {w_upper}!)", "start": 9.2, "end": 13.6},
            {"text": "Vừa xong quay lại...", "start": 13.8, "end": 15.0},
            {"text": sc04[:23], "start": 15.0, "end": 18.5}
        ]
        
        items.append({
            "index": idx,
            "id": eid,
            "word": word,
            "title": gloss,
            "scenes": [
                (sc01, 0.20),
                (sc02, 0.20),
                (sc03, 1.20),
                (sc04, 0.40)
            ],
            "cues": cues
        })
    return items

def prepare_batch(batch_name="batch-02-words-32-81", start_idx=32, count=50):
    out_dir = BATCH_DIR / batch_name
    out_dir.mkdir(parents=True, exist_ok=True)
    items = load_bank_items(start_idx, count)
    req_file = out_dir / 'request.json'
    with open(req_file, 'w', encoding='utf-8') as f:
        json.dump({"batch_name": batch_name, "count": len(items), "items": items}, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã chuẩn bị gói Lô {batch_name}: {req_file} ({len(items)} từ vựng, từ #{start_idx} đến #{start_idx+count-1})")
    return req_file

def sanitize_cues(raw_cues):
    """
    Tự động chuẩn hóa và tách nhỏ phụ đề thành các cue 1 dòng (dưới 24 ký tự),
    loại bỏ dấu \n gây lỗi Text overflow trong Playwright.
    """
    clean = []
    for cue in raw_cues:
        text = cue['text'].replace('\n', ' ').strip()
        start = cue['start']
        end = cue['end']
        dur = max(0.5, end - start)
        
        if len(text) > 24:
            # Cắt ngắn đảm bảo an toàn
            p1 = text[:23].strip()
            p2 = text[23:46].strip()
            if p2:
                mid = round(start + dur * 0.5, 2)
                clean.append({"text": p1, "start": start, "end": mid})
                clean.append({"text": p2, "start": mid, "end": end})
            else:
                clean.append({"text": p1, "start": start, "end": end})
        else:
            clean.append({"text": text, "start": start, "end": end})
    return clean

# ==========================================
# 2. XỬ LÝ NẶNG TRÊN COLAB CLI (ROUND 1)
# ==========================================

def run_colab_batch_tts(batch_name="batch-02-words-32-81"):
    """
    Đẩy toàn bộ 50 từ (200 câu thoại) lên Colab GPU T4 xử lý TTS Vieneu Adam bựa + time-stretch 1.12x.
    """
    batch_path = BATCH_DIR / batch_name
    req_file = batch_path / 'request.json'
    if not req_file.exists():
        raise FileNotFoundError(f"Không tìm thấy {req_file}")
        
    print(f"\n=== [BƯỚC 1] KHỞI CHẠY COLAB CLI BATCH TTS CHO LÔ: {batch_name} ===")
    
    # 1. Kiểm tra / Start Colab session
    check_sess = subprocess.run(["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "sessions"], cwd=str(ROOT), capture_output=True, text=True)
    if COLAB_SESSION not in check_sess.stdout:
        print("1. Khởi động phiên Colab T4 mới...")
        subprocess.run(["python3", "-m", "colab_bridge", "start"], cwd=str(ROOT))
    else:
        print(f"1. Phiên Colab T4 '{COLAB_SESSION}' đã sẵn sàng và đang hoạt động!")
    
    # 2. Upload request
    print("2. Upload gói request lên Colab VM...")
    cmd_upload = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "upload", "-s", COLAB_SESSION, str(req_file), "/content/batch_request.json"]
    subprocess.run(cmd_upload, cwd=str(ROOT), check=True)
    
    # 3. Exec worker
    print("3. Tổng hợp 200 câu thoại giọng Adam bựa & time-stretch 1.12x trên Tesla T4...")
    worker_file = ROOT / "scratch/remote_batch_tts_worker.py"
    cmd_exec = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "exec", "-s", COLAB_SESSION, "--timeout", "600", "-f", str(worker_file)]
    subprocess.run(cmd_exec, cwd=str(ROOT), check=True)
    
    # 4. Download zip
    print("4. Tải file âm thanh thành phẩm về máy local...")
    out_zip = batch_path / "batch_output.zip"
    cmd_dl = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "download", "-s", COLAB_SESSION, "/content/batch_output.zip", str(out_zip)]
    subprocess.run(cmd_dl, cwd=str(ROOT), check=True)
    
    # 5. Extract zip
    print("5. Giải nén âm thanh vào thư mục lô...")
    audio_dir = batch_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, 'r') as zf:
        zf.extractall(audio_dir)
    print(f"✓ Đã hoàn tất xử lý âm thanh trên Colab và tải về {audio_dir}!")
    print("ℹ Phiên Colab vẫn được giữ mở để sẵn sàng cho bước Retake tập trung (nếu cần).")

# ==========================================
# 3. KIỂM ĐỊNH CHẤT LƯỢNG TỰ ĐỘNG TẠI MÁY LOCAL (AUDIT)
# ==========================================

def audit_batch(batch_name="batch-02-words-32-81"):
    """
    Kiểm định toàn diện chất lượng của 50 từ trong lô:
    - Đo thời lượng từng cảnh
    - Tính tổng thời lượng (chuẩn vàng: 16.5s - 20.5s)
    - Kiểm tra clipping âm thanh
    - Kiểm tra an toàn phụ đề
    - Xuất file retake_manifest.json nếu có câu cần sửa chữa
    """
    batch_path = BATCH_DIR / batch_name
    req = json.loads((batch_path / 'request.json').read_text())
    items = req['items']
    audio_dir = batch_path / 'audio'
    
    print(f"\n=== [BƯỚC 2] KIỂM ĐỊNH TỰ ĐỘNG CHẤT LƯỢNG LÔ (LOCAL AUDIT): {batch_name} ===")
    
    results = []
    retakes = []
    
    for it in items:
        word = it['word']
        entry_id = it['id']
        word_audio = audio_dir / entry_id
        
        part_durs = []
        is_clipped = False
        
        for idx in range(4):
            wav_path = word_audio / f"part_{idx}.wav"
            if not wav_path.exists():
                part_durs.append(0.0)
                continue
            data, sr = sf.read(str(wav_path))
            dur = len(data) / sr
            part_durs.append(dur)
            if np.max(np.abs(data)) > 0.98:
                is_clipped = True
                
        # Tổng thời lượng kèm pause: 0.2 + 0.2 + 1.2 + 0.4 = 2.0s
        pause_total = sum(p for _, p in it['scenes'])
        total_dur = round(sum(part_durs) + pause_total, 2)
        
        # Đánh giá tiêu chuẩn
        status = "PASS"
        action = None
        
        if total_dur > 20.8:
            status = "WARN_LONG"
            # Cần nén thêm tốc độ cảnh 4 hoặc cảnh 1
            excess = total_dur - 19.5
            needed_rate = round(1.0 + (excess / part_durs[3]), 2)
            action = f"Stretch part_3 rate={needed_rate}"
            retakes.append({
                "id": entry_id,
                "word": word,
                "part_idx": 3,
                "rate": needed_rate,
                "reason": f"Thời lượng dài ({total_dur}s > 20.8s)"
            })
        elif total_dur < 15.5:
            status = "WARN_SHORT"
            retakes.append({
                "id": entry_id,
                "word": word,
                "part_idx": 3,
                "rate": 0.92,
                "reason": f"Thời lượng ngắn ({total_dur}s < 15.5s)"
            })
            
        results.append({
            "index": it['index'],
            "word": word,
            "total_dur": total_dur,
            "parts": [round(d, 2) for d in part_durs],
            "clipped": is_clipped,
            "status": status,
            "action": action
        })

    # In kết quả
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    warn_count = len(results) - pass_count
    
    print(f"Tổng số từ kiểm tra: {len(results)}")
    print(f"✓ Đạt chuẩn vàng (16.0s - 20.5s): {pass_count}/{len(results)} ({pass_count/len(results)*100:.1f}%)")
    if warn_count > 0:
        print(f"⚠ Cần tinh chỉnh nhẹ: {warn_count} từ")
        for r in results:
            if r['status'] != 'PASS':
                print(f"  - [{r['word']}]: {r['total_dur']}s -> {r['action']} ({r['status']})")
    else:
        print("🎉 100% CÁC TỪ TRONG LÔ ĐỀU ĐẠT CHUẨN HOÀN HẢO!")
        
    # Ghi manifest
    manifest_file = batch_path / 'retake_manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump({"batch_name": batch_name, "retakes": retakes}, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã lưu danh sách sửa chữa: {manifest_file} ({len(retakes)} mục)")
    return len(retakes)

# ==========================================
# 4. GOM LÔ SỬA CHỮA HÀNG LOẠT TRÊN COLAB (ROUND 2)
# ==========================================

def run_colab_retake(batch_name="batch-02-words-32-81"):
    """
    Gom toàn bộ các câu cần sửa chữa đẩy lên Colab GPU T4 xử lý 1 mẻ duy nhất,
    tải về ghi đè và ngắt phiên Colab dứt điểm.
    """
    batch_path = BATCH_DIR / batch_name
    manifest_file = batch_path / 'retake_manifest.json'
    if not manifest_file.exists():
        print("Không có file retake_manifest.json, bỏ qua bước retake.")
        return
        
    manifest = json.loads(manifest_file.read_text())
    retakes = manifest.get('retakes', [])
    if not retakes:
        print("✓ Không có mục nào cần sửa chữa! Đạt chuẩn 100%.")
        # Đóng session Colab giải phóng GPU
        subprocess.run(["python3", "-m", "colab_bridge", "stop"], cwd=str(ROOT))
        return
        
    print(f"\n=== [BƯỚC 3] GOM LÔ SỬA CHỮA HÀNG LOẠT TRÊN COLAB (SINGLE-PASS RETAKE) ===")
    print(f"Gom {len(retakes)} cảnh cần tinh chỉnh lên Colab VM...")
    
    # 1. Upload retake request
    cmd_upload = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "upload", "-s", COLAB_SESSION, str(manifest_file), "/content/retake_request.json"]
    subprocess.run(cmd_upload, cwd=str(ROOT), check=True)
    
    # 2. Exec retake worker
    retake_file = ROOT / "scratch/remote_retake_worker.py"
    cmd_exec = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "exec", "-s", COLAB_SESSION, "--timeout", "300", "-f", str(retake_file)]
    subprocess.run(cmd_exec, cwd=str(ROOT), check=True)
    
    # 3. Download retake zip
    out_zip = batch_path / "retake_output.zip"
    cmd_dl = ["python3", "-m", "colab_bridge.accounts", "run", COLAB_ACCOUNT, "download", "-s", COLAB_SESSION, "/content/retake_output.zip", str(out_zip)]
    subprocess.run(cmd_dl, cwd=str(ROOT), check=True)
    
    # 4. Extract ghi đè
    audio_dir = batch_path / "audio"
    with zipfile.ZipFile(out_zip, 'r') as zf:
        zf.extractall(audio_dir)
    print(f"✓ Đã cập nhật ghi đè các file âm thanh đã sửa vào {audio_dir}!")
    
    # 5. Đóng session Colab dứt điểm
    print("5. Đóng phiên Colab dứt điểm để bảo toàn quota GPU...")
    subprocess.run(["python3", "-m", "colab_bridge", "stop"], cwd=str(ROOT))

# ==========================================
# 5. LẮP RÁP TIMELINE, SFX & RENDER XUẤT XƯỞNG
# ==========================================

def assemble_and_export_batch(batch_name="batch-02-words-32-81"):
    """
    Lắp ráp timeline, gắn SFX Foley và render video Remotion cho toàn bộ lô 50 video
    """
    sr = 48000
    batch_path = BATCH_DIR / batch_name
    req = json.loads((batch_path / 'request.json').read_text())
    items = req['items']

    image_files = {
        'sc01.jpg': BRAIN / 'dad_micro_sc01_1790905129698.jpg',
        'sc02.jpg': BRAIN / 'dad_micro_sc02_1790905209678.jpg',
        'sc03.jpg': BRAIN / 'dad_micro_sc03_1790905257999.jpg',
        'sc04.jpg': BRAIN / 'dad_micro_sc04_1790905276710.jpg',
    }

    render_script = ROOT / 'renderer/render.mjs'
    exported_videos = []

    for it in items:
        word = it['word']
        entry_id = it['id']
        print(f"\n=== ĐANG LẮP RÁP & RENDER VIDEO [{it['index']}/81]: {word.upper()} ===")

        job_run_dir = ROOT / 'runs' / f"vocab-{word}-micro"
        job_run_dir.mkdir(parents=True, exist_ok=True)
        public_dir = job_run_dir / 'public'
        public_dir.mkdir(parents=True, exist_ok=True)

        # Chép 4 ảnh vào public
        for target_name, src_path in image_files.items():
            shutil.copy(src_path, public_dir / target_name)

        # Chép BGM
        bgm_path = BGM_DIR / 'upbeat-chill.wav'
        if bgm_path.exists():
            shutil.copy(bgm_path, public_dir / 'bgm.wav')

        # Ghép âm thanh & SFX
        audio_dir = batch_path / 'audio' / entry_id
        combined_samples = []
        timeline = []
        cur_time = 0.0

        for idx, (text, pause_after) in enumerate(it['scenes']):
            part_wav = audio_dir / f"part_{idx}.wav"
            data, seg_sr = sf.read(str(part_wav))
            if seg_sr != sr:
                new_len = int(len(data) * sr / seg_sr)
                data = np.interp(np.linspace(0, len(data), new_len, endpoint=False), np.arange(len(data)), data)
            if len(data.shape) > 1:
                data = data.mean(axis=1)

            dur = len(data) / sr
            timeline.append({
                'start': cur_time,
                'end': cur_time + dur,
                'dur': dur,
                'total_end': cur_time + dur + pause_after
            })
            combined_samples.append(data)
            cur_time += dur

            if pause_after > 0:
                silence = np.zeros(int(pause_after * sr))
                combined_samples.append(silence)
                cur_time += pause_after

        full_audio = np.concatenate(combined_samples)

        # Chèn 6 Foley SFX
        def overlay_sfx(base, sfx_name, start_sec, vol=0.5):
            sfx_path = SFX_DIR / sfx_name
            if not sfx_path.exists():
                return
            sfx_data, sfx_sr = sf.read(str(sfx_path))
            if sfx_sr != sr:
                new_len = int(len(sfx_data) * sr / sfx_sr)
                sfx_data = np.interp(np.linspace(0, len(sfx_data), new_len, endpoint=False), np.arange(len(sfx_data)), sfx_data)
            if len(sfx_data.shape) > 1:
                sfx_data = sfx_data.mean(axis=1)
            idx_start = int(start_sec * sr)
            idx_end = min(len(base), idx_start + len(sfx_data))
            if idx_end > idx_start:
                base[idx_start:idx_end] += sfx_data[:idx_end - idx_start] * vol

        t1 = timeline[1]['start']
        t2 = timeline[2]['start']
        t2_end = timeline[2]['end']
        t3 = timeline[3]['start']

        overlay_sfx(full_audio, 'click.wav', 0.40, vol=0.50)
        overlay_sfx(full_audio, 'whoosh.wav', t1, vol=0.35)
        overlay_sfx(full_audio, 'ding.wav', t1 + 1.20, vol=0.40)
        overlay_sfx(full_audio, 'tick.wav', t2_end + 0.25, vol=0.45)
        overlay_sfx(full_audio, 'tick.wav', t2_end + 0.70, vol=0.45)
        overlay_sfx(full_audio, 'tick.wav', t2_end + 1.15, vol=0.45)
        overlay_sfx(full_audio, 'click.wav', t3 + 0.15, vol=0.55)
        overlay_sfx(full_audio, 'pop.wav', t3 + 0.28, vol=0.65)
        overlay_sfx(full_audio, 'crunch.wav', t3 + 1.80, vol=0.70)

        max_val = np.max(np.abs(full_audio))
        if max_val > 0.95:
            full_audio = (full_audio / max_val) * 0.95

        total_dur = round(len(full_audio) / sr, 2)
        sf.write(str(public_dir / 'narration.wav'), full_audio, sr)

        scenes = [
            {
                "id": "SC01",
                "title": "Tình huống khẩn cấp",
                "start": 0.0,
                "end": round(timeline[0]['total_end'], 2),
                "image": "sc01.jpg",
                "images": [{"id": "SC01_B1", "src": "sc01.jpg", "at": 0, "effect": "punch_in", "focus": {"x": 0.5, "y": 0.35}}]
            },
            {
                "id": "SC02",
                "title": "Chìa khóa từ vựng",
                "start": round(timeline[0]['total_end'], 2),
                "end": round(timeline[1]['total_end'], 2),
                "image": "sc02.jpg",
                "images": [{"id": "SC02_B1", "src": "sc02.jpg", "at": 0, "effect": "pan_right", "focus": {"x": 0.5, "y": 0.40}}]
            },
            {
                "id": "SC03",
                "title": "Luyện nói phản xạ",
                "start": round(timeline[1]['total_end'], 2),
                "end": round(timeline[2]['total_end'], 2),
                "image": "sc03.jpg",
                "images": [{"id": "SC03_B1", "src": "sc03.jpg", "at": 0, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.45}}]
            },
            {
                "id": "SC04",
                "title": "Cú twist meme",
                "start": round(timeline[2]['total_end'], 2),
                "end": total_dur,
                "image": "sc04.jpg",
                "images": [{"id": "SC04_B1", "src": "sc04.jpg", "at": 0, "effect": "shake", "focus": {"x": 0.5, "y": 0.45}}]
            }
        ]

        # Căn chỉnh cues chính xác theo timeline
        raw_cues = it['cues']
        adjusted_cues = []
        
        t0 = timeline[0]['start']
        t1 = timeline[1]['start']
        t2 = timeline[2]['start']
        t3 = timeline[3]['start']
        
        adjusted_cues.append({"text": raw_cues[0]['text'], "start": 0.0, "end": round(t0 + (timeline[0]['dur'] * 0.5), 2)})
        adjusted_cues.append({"text": raw_cues[1]['text'], "start": round(t0 + (timeline[0]['dur'] * 0.5), 2), "end": round(timeline[0]['end'], 2)})
        
        adjusted_cues.append({"text": raw_cues[2]['text'], "start": round(t1, 2), "end": round(t1 + (timeline[1]['dur'] * 0.45), 2)})
        adjusted_cues.append({"text": raw_cues[3]['text'], "start": round(t1 + (timeline[1]['dur'] * 0.45), 2), "end": round(timeline[1]['end'], 2)})
        
        adjusted_cues.append({"text": raw_cues[4]['text'], "start": round(t2, 2), "end": round(t2 + (timeline[2]['dur'] * 0.40), 2)})
        adjusted_cues.append({"text": raw_cues[5]['text'], "start": round(t2 + (timeline[2]['dur'] * 0.40), 2), "end": round(timeline[2]['total_end'], 2)})
        
        adjusted_cues.append({"text": raw_cues[6]['text'], "start": round(t3, 2), "end": round(t3 + (timeline[3]['dur'] * 0.45), 2)})
        adjusted_cues.append({"text": raw_cues[7]['text'], "start": round(t3 + (timeline[3]['dur'] * 0.45), 2), "end": total_dur})

        props = {
            "duration": total_dur,
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "9:16",
            "target_word": word.capitalize(),
            "audioSrc": "narration.wav",
            "bgmSrc": "bgm.wav",
            "bgmVolume": 0.12,
            "scenes": scenes,
            "cues": sanitize_cues(adjusted_cues)
        }

        with open(job_run_dir / 'props.json', 'w', encoding='utf-8') as f:
            json.dump(props, f, ensure_ascii=False, indent=2)

        # Render Remotion
        res = subprocess.run(['node', str(render_script), str(job_run_dir)], cwd=str(ROOT), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Lỗi render {word}:\n{res.stderr}")
            continue

        out_video_dir = VIDEO_EXPORT_DIR / f"vocab-{word}-micro"
        out_video_dir.mkdir(parents=True, exist_ok=True)
        final_mp4 = out_video_dir / f"vocab-{word}-micro.mp4"
        shutil.copy(job_run_dir / 'video.mp4', final_mp4)
        size_mb = final_mp4.stat().st_size / (1024 * 1024)
        print(f"✓ XUẤT XƯỞNG THÀNH CÔNG: {final_mp4} ({total_dur}s, {size_mb:.2f} MB)")
        exported_videos.append((word, total_dur, size_mb, final_mp4))

    print(f"\n==========================================")
    print(f"HOÀN THÀNH XUẤT XƯỞNG {len(exported_videos)}/{len(items)} VIDEO TRONG LÔ!")
    for w, dur, sz, path in exported_videos:
        print(f"  - [{w}]: {dur}s | {sz:.2f}MB -> {path}")

def mark_batch_in_ledger(batch_name="batch-02-words-32-81"):
    from datetime import datetime
    batch_path = BATCH_DIR / batch_name
    req = json.loads((batch_path / 'request.json').read_text())
    ledger_file = ROOT / 'vocab/ledger.json'
    led = json.loads(ledger_file.read_text())
    entries = led.setdefault('entries', {})
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    count = 0
    for it in req['items']:
        eid = it['id']
        base_word = it['word']
        entries[eid] = {
            'status': 'done',
            'job': f"vocab-{base_word}-micro",
            'at': now_str,
            'format': 'micro-drama-4-acts',
            'voice': 'Adam bựa'
        }
        count += 1
    ledger_file.write_text(json.dumps(led, ensure_ascii=False, indent=2))
    print(f"✓ Đã cập nhật thành công {count} từ vựng vào vocab/ledger.json!")

def main():
    parser = argparse.ArgumentParser(description="Hybrid Batch Manager v3.0")
    parser.add_argument("action", choices=["prepare", "colab-tts", "audit", "colab-retake", "assemble", "mark", "stop-colab"])
    parser.add_argument("--batch", default="batch-02-words-32-81")
    parser.add_argument("--start", type=int, default=32)
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()

    if args.action == "prepare":
        prepare_batch(args.batch, args.start, args.count)
    elif args.action == "colab-tts":
        run_colab_batch_tts(args.batch)
    elif args.action == "audit":
        audit_batch(args.batch)
    elif args.action == "colab-retake":
        run_colab_retake(args.batch)
    elif args.action == "assemble":
        assemble_and_export_batch(args.batch)
    elif args.action == "mark":
        mark_batch_in_ledger(args.batch)
    elif args.action == "stop-colab":
        subprocess.run(["python3", "-m", "colab_bridge", "stop"], cwd=str(ROOT))

if __name__ == '__main__':
    main()
