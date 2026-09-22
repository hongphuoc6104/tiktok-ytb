#!/usr/bin/env python3
"""V3 maintenance: verify published videos, retain history/cache, clean empty scratch only."""

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = ROOT / "exports"
RUNS_DIR = ROOT / "runs"
SCRATCH_DIR = ROOT / "scratch"
GFLOW_DIR = ROOT / ".gflow"
STATE_DIR = ROOT / ".state"
DB_PATH = STATE_DIR / "jobs.sqlite"
LOG_PATH = STATE_DIR / "cleanup.log"

JOB_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

def log_event(message: str) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    for entry in path.rglob("*"):
        if entry.is_file() and not entry.is_symlink():
            try:
                total += entry.stat().st_size
            except OSError:
                pass
    return total

def validate_job_id(job_id: str) -> Path:
    """Validates job_id against regex and ensures path does not escape runs directory."""
    if not job_id or not JOB_ID_REGEX.match(job_id):
        raise ValueError(f"Tên job không hợp lệ (chỉ chấp nhận a-z, A-Z, 0-9, _, -): {job_id}")
    run_dir = (RUNS_DIR / job_id).resolve()
    if not run_dir.is_relative_to(RUNS_DIR.resolve()):
        raise ValueError(f"Đường dẫn job vi phạm an toàn (Path Traversal detected): {job_id}")
    return run_dir

def validate_video_integrity(video_path: Path) -> tuple[bool, str]:
    """Uses ffprobe to verify video streams, duration, and container integrity."""
    if not video_path.exists() or video_path.stat().st_size < 100 * 1024:
        return False, f"File video không tồn tại hoặc quá nhỏ (<100KB): {video_path.name}"
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=codec_type,codec_name",
            "-of", "json", str(video_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            return False, f"ffprobe không thể đọc video (hỏng container hoặc thiếu moov atom): {video_path.name}"
        data = json.loads(res.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        if duration <= 0:
            return False, f"Thời lượng video không hợp lệ (duration={duration}): {video_path.name}"
        streams = data.get("streams", [])
        has_video = any(s.get("codec_type") == "video" for s in streams)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        if not has_video:
            return False, f"Video thiếu stream hình ảnh: {video_path.name}"
        if not has_audio:
            return False, f"Video thiếu stream âm thanh: {video_path.name}"
        return True, "Video hợp lệ"
    except Exception as e:
        return False, f"Lỗi kiểm tra ffprobe: {e}"

def validate_job_deliverables(job_id: str) -> tuple[bool, str, list[Path], int]:
    """Verify v3 decisions and current video library without changing job state."""
    import threading
    sys.path.insert(0, str(ROOT))
    from pilot import Pilot
    import workflow
    p = None
    try:
        validate_job_id(job_id)
        p = object.__new__(Pilot)
        p.root = ROOT
        p._db_lock = threading.Lock()
        p.db = sqlite3.connect(DB_PATH.resolve().as_uri() + '?mode=ro', uri=True)
        p.db.row_factory = sqlite3.Row
        paths = [Path(x) for x in workflow.published_videos(p, job_id)]
        for path in paths:
            valid, reason = validate_video_integrity(path)
            if not valid:
                return False, reason, [], 0
        return True, 'Đủ quyết định v3 và video xuất khớp artifact', paths, workflow.current(p, job_id, 'video')['revision']
    except Exception as exc:
        return False, str(exc), [], 0
    finally:
        if p is not None and hasattr(p, 'db'):
            p.db.close()


def prune_unapproved_revisions(job_id: str, dry_run: bool = False) -> int:
    """Revision history and evidence are retained, including rejected artifacts."""
    validate_job_id(job_id)
    print(f'  Giữ toàn bộ revision và bằng chứng của {job_id}; không có ứng viên xóa.')
    return 0

def clean_scratch_whitelist(retention_days: int = 3, dry_run: bool = False) -> int:
    """Remove only old, empty scratch directories; filenames are not evidence of disposal.

    Media and nonempty directories require a separately reviewed inventory.
    Never follow symlinks, including a symlink replacing the scratch root.
    """
    if SCRATCH_DIR.is_symlink() or not SCRATCH_DIR.is_dir():
        return 0
    cutoff = time.time() - max(0, retention_days) * 86400
    for item in SCRATCH_DIR.iterdir():
        if item.is_symlink() or not item.is_dir():
            continue
        if not (item.name.startswith('tmp_') or item.name == 'render_output'):
            continue
        try:
            if item.stat().st_mtime >= cutoff or any(item.iterdir()):
                continue
            if dry_run:
                print(f"  [Scratch - Thư mục rỗng có thể dọn] {item}")
            else:
                # rmdir fails safely if another process has added a file.
                item.rmdir()
                print(f"  [Scratch - Đã dọn thư mục rỗng] {item}")
        except OSError:
            continue
    return 0

def clean_system_and_browser_cache(dry_run: bool = False) -> int:
    """No ownership proof for shared caches: never select them for deletion."""
    print('  Giữ profile, cache trình duyệt, model và /tmp dùng chung; chưa có ứng viên xóa được xác minh.')
    return 0

def clean_completed_job(job_id: str, dry_run: bool = False) -> int:
    """Safely validates and prunes unapproved revisions of a completed job."""
    try:
        run_dir = validate_job_id(job_id)
    except ValueError as e:
        print(f"❌ [LỖI BẢO MẬT] {e}", file=sys.stderr)
        return 0

    if not run_dir.exists():
        print(f"Bỏ qua: Không tìm thấy thư mục runs/{job_id}")
        return 0

    valid, reason, preserved, approved_rev = validate_job_deliverables(job_id)
    if not valid:
        print(f"🛡️  [BẢO VỆ DỮ LIỆU] Không dọn dẹp job '{job_id}': {reason}")
        print(f"   Dữ liệu {job_id} trong runs/ được giữ nguyên 100%.")
        return 0

    print(f"\n==========================================================")
    print(f"  Job Hợp Lệ Đã Nghiệm Thu: {job_id}")
    print(f"  Thành phẩm đã xác minh trong thư viện video của {job_id}:")
    for f in preserved:
        print(f"    ✓ {f.name} ({format_size(f.stat().st_size)})")
    print(f"==========================================================")

    freed = prune_unapproved_revisions(job_id, dry_run=dry_run)
    return freed

def main():
    parser = argparse.ArgumentParser(
        description="Video Pilot v3 — Safe Post-Production Maintenance & Selective Pruning"
    )
    parser.add_argument("--job", help="Tên job cần kiểm tra thành phẩm v3")
    parser.add_argument("--all", action="store_true", help="Kiểm kê các job và dọn scratch rỗng quá hạn")
    parser.add_argument("--periodic", action="store_true", help="Chế độ bảo trì định kỳ: Kiểm kê job và dọn scratch rỗng quá hạn")
    parser.add_argument("--cache-only", action="store_true", help="Báo trạng thái bảo toàn cache; không xóa")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước các mục sẽ dọn mà không xóa thật")
    args = parser.parse_args()

    if not any([args.job, args.all, args.periodic, args.cache_only]):
        parser.print_help()
        sys.exit(1)

    print("==========================================================")
    print(" Video Pilot v3 — Safe Post-Production Maintenance Protocol")
    print(f" Chế độ: {'XEM TRƯỚC (--dry-run)' if args.dry_run else 'THỰC THI (Execution)'}")
    print("==========================================================")

    total_freed = 0

    if args.cache_only:
        total_freed += clean_system_and_browser_cache(dry_run=args.dry_run)

    elif args.job:
        total_freed += clean_completed_job(args.job, dry_run=args.dry_run)

    elif args.all or args.periodic:
        # Step 1: System & Browser Cache
        total_freed += clean_system_and_browser_cache(dry_run=args.dry_run)

        # Step 2: Scratch Whitelist
        total_freed += clean_scratch_whitelist(retention_days=3, dry_run=args.dry_run)

        # Step 3: Scan all runs/ for completed, approved jobs
        print("\n--- [Tầng 3] Tối ưu hóa các Job đã nghiệm thu hoàn tất ---")
        if RUNS_DIR.exists():
            for j in sorted(RUNS_DIR.iterdir()):
                if j.is_dir() and JOB_ID_REGEX.match(j.name):
                    total_freed += clean_completed_job(j.name, dry_run=args.dry_run)

    print("\n==========================================================")
    action_text = "Dung lượng ước tính sẽ giải phóng" if args.dry_run else "Tổng dung lượng đã giải phóng"
    print(f" 🎉 {action_text}: {format_size(total_freed)}")
    print(" 🛡️  Lịch sử briefs, integrity hashes, bằng chứng Flow và kịch bản/video kết quả BẢO TOÀN 100%.")
    print("==========================================================")

    if not args.dry_run and total_freed > 0:
        log_event(f"Cleaned {format_size(total_freed)} (mode: {'job=' + args.job if args.job else 'all/periodic'})")

if __name__ == "__main__":
    main()
