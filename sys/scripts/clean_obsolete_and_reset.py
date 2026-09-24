#!/usr/bin/env python3
"""
clean_obsolete_and_reset.py

Dọn dẹp an toàn các thành phần lỗi thời, tệp test tạm, cache và 2 video vừa tạo:
1. Xóa bỏ 2 video mới vừa tạo (vocab-wake-002, vocab-wake-up-001) và dữ liệu run.
2. Giải phóng 2 đề tài (wake.v và wake up.phr) trong sys/vocab/ledger.json về kho sẵn sàng tạo lại từ đầu.
3. Dọn dẹp 10 file .wav test rác và __pycache__ ở gốc.
4. Dọn dẹp các thư mục tàn dư layout cũ ở gốc (tests, scripts, vocab, experiments, .state).
5. Di chuyển và bảo toàn tuyệt đối .gflow sang sys/.gflow kèm symlink.
6. Sao lưu các script tiện ích scratch sang sys/scratch/, dọn sạch media rác và tạo symlink scratch.
7. Xóa các run attempt hỏng (vocab-get-up-001 đến 005) và exports cũ.
"""

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"

def log(msg: str):
    print(f"[CLEANUP] {msg}")

def safe_remove_file(path: Path):
    if path.exists() or path.is_symlink():
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
                log(f"Đã xóa file: {path.relative_to(ROOT)}")
        except Exception as e:
            log(f"Lỗi khi xóa file {path}: {e}")

def safe_remove_dir(path: Path):
    if path.exists() and not path.is_symlink():
        try:
            shutil.rmtree(path)
            log(f"Đã xóa thư mục: {path.relative_to(ROOT)}")
        except Exception as e:
            log(f"Lỗi khi xóa thư mục {path}: {e}")
    elif path.is_symlink():
        try:
            path.unlink()
            log(f"Đã gỡ bỏ symlink: {path.relative_to(ROOT)}")
        except Exception as e:
            log(f"Lỗi khi gỡ symlink {path}: {e}")

def step_1_reset_two_videos_and_topics():
    log("=== BƯỚC 1: Xóa 2 video mới tạo & Giải phóng 2 đề tài về kho ===")
    
    # 1.1 Xóa video output trong video/
    video_dir = ROOT / "video" / "vocab-wake-up-001"
    safe_remove_dir(video_dir)
    
    # 1.2 Xóa các runs tương ứng trong sys/runs
    runs_to_remove = [
        SYS_DIR / "runs" / "vocab-wake-001",
        SYS_DIR / "runs" / "vocab-wake-002",
        SYS_DIR / "runs" / "vocab-wake-up-001",
    ]
    for r in runs_to_remove:
        safe_remove_dir(r)
        
    # 1.3 Cập nhật ledger.json để giải phóng wake.v và wake up.phr
    ledger_path = SYS_DIR / "vocab" / "ledger.json"
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)
            
        entries = ledger_data.get("entries", {})
        freed = []
        for word_id in ["wake.v", "wake up.phr"]:
            if word_id in entries:
                del entries[word_id]
                freed.append(word_id)
                
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            
        log(f"Đã giải phóng {freed} trong sys/vocab/ledger.json. Đề tài hiện đã sẵn sàng để tạo mới từ đầu!")

def step_2_clean_root_loose_files():
    log("=== BƯỚC 2: Xóa 10 file audio wav rác và bytecode ở gốc ===")
    
    wav_files = [
        ROOT / "test_piece_0.wav",
        ROOT / "test_piece_1.wav",
        ROOT / "test_piece_2.wav",
        ROOT / "test_piece_3.wav",
        ROOT / "test_piece_4.wav",
        ROOT / "test_piece_5.wav",
        ROOT / "test_piece_6.wav",
        ROOT / "test_sc03_take_0.wav",
        ROOT / "test_sc03_take_1.wav",
        ROOT / "test_what_time.wav",
    ]
    for w in wav_files:
        safe_remove_file(w)
        
    safe_remove_dir(ROOT / "__pycache__")

def step_3_clean_root_legacy_dirs():
    log("=== BƯỚC 3: Dọn dẹp các thư mục tàn dư trước chuyển đổi ở gốc ===")
    
    dirs_to_clean = [
        ROOT / "tests",
        ROOT / "scripts",
        ROOT / "vocab",
        ROOT / "experiments",
        ROOT / ".state",
    ]
    for d in dirs_to_clean:
        safe_remove_dir(d)

def step_4_preserve_gflow():
    log("=== BƯỚC 4: Bảo toàn tuyệt đối .gflow (di chuyển sang sys/.gflow và tạo symlink) ===")
    root_gflow = ROOT / ".gflow"
    sys_gflow = SYS_DIR / ".gflow"
    
    if root_gflow.exists() and not root_gflow.is_symlink():
        if not sys_gflow.exists():
            log("Di chuyển .gflow từ gốc sang sys/.gflow...")
            shutil.move(str(root_gflow), str(sys_gflow))
            log("Tạo symlink .gflow -> sys/.gflow tại gốc...")
            os.symlink("sys/.gflow", str(root_gflow))
            log("Đã bảo toàn hoàn hảo hồ sơ và cookie Google Flow!")
        else:
            log("sys/.gflow đã tồn tại, kiểm tra và dọn dẹp liên kết...")
    elif not root_gflow.exists() and sys_gflow.exists():
        log("Tạo lại symlink .gflow -> sys/.gflow tại gốc...")
        os.symlink("sys/.gflow", str(root_gflow))

def step_5_clean_scratch():
    log("=== BƯỚC 5: Sao lưu scripts scratch sang sys/scratch/ và dọn rác ===")
    root_scratch = ROOT / "scratch"
    sys_scratch = SYS_DIR / "scratch"
    sys_scratch.mkdir(parents=True, exist_ok=True)
    
    useful_scripts = [
        "inspect_flow_ui.cjs",
        "check_other_projects.cjs",
        "download_all_flow_images.cjs",
        "prepare_render_data.py",
        "launch_chrome.sh",
    ]
    
    if root_scratch.exists() and not root_scratch.is_symlink():
        for script_name in useful_scripts:
            src = root_scratch / script_name
            dst = sys_scratch / script_name
            if src.exists():
                shutil.copy2(src, dst)
                log(f"Đã sao lưu tiện ích sang sys/scratch/: {script_name}")
                
        log("Xóa toàn bộ thư mục scratch cũ ở gốc chứa media và video rác...")
        safe_remove_dir(root_scratch)
        
        log("Tạo symlink scratch -> sys/scratch tại gốc...")
        os.symlink("sys/scratch", str(root_scratch))
    elif not root_scratch.exists():
        log("Tạo symlink scratch -> sys/scratch tại gốc...")
        os.symlink("sys/scratch", str(root_scratch))

def step_6_clean_stale_runs_and_exports():
    log("=== BƯỚC 6: Xóa các run attempt hỏng và thư mục xuất cũ ===")
    
    # Xóa các attempt get-up cũ bị hỏng (giữ vocab-get-up-006)
    for i in range(1, 6):
        stale_run = SYS_DIR / "runs" / f"vocab-get-up-{i:03d}"
        safe_remove_dir(stale_run)
        
    # Xóa thư mục exports ở gốc
    root_exports = ROOT / "exports"
    if root_exports.exists() and not root_exports.is_symlink():
        safe_remove_dir(root_exports)

def main():
    log("BẮT ĐẦU QUY TRÌNH DỌN DẸP AN TOÀN VÀ RESET ĐỀ TÀI")
    step_1_reset_two_videos_and_topics()
    step_2_clean_root_loose_files()
    step_3_clean_root_legacy_dirs()
    step_4_preserve_gflow()
    step_5_clean_scratch()
    step_6_clean_stale_runs_and_exports()
    log("HOÀN TẤT DỌN DẸP TOÀN DIỆN THÀNH CÔNG!")

if __name__ == "__main__":
    main()
