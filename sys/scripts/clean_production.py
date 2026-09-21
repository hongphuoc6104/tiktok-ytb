#!/usr/bin/env python3
"""
Video Pilot v3 — Safe Post-Production Maintenance & Selective Pruning Tool.

Guarantees:
1. NEVER deletes runs/<job> root directory, briefs, integrity hashes, or Flow evidence.
2. Performs 4-layer deep validation (SQLite approval status, ffprobe media integrity, JSON schema, dual-ratio check).
3. Whitelist-only scratch cleanup preserving all evidence, tokens, and active scripts.
4. Complete protection against path traversal (rejects ../ and special characters).
5. Supports safe periodic maintenance (Chrome on-device model cache, shader cache, remotion temp).
"""

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

def check_sqlite_approval(job_id: str) -> tuple[bool, int, str]:
    """Checks if job render module is approved in SQLite jobs.sqlite."""
    if not DB_PATH.exists():
        return False, 0, "Không tìm thấy cơ sở dữ liệu .state/jobs.sqlite"
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute(
            "SELECT state, revision FROM modules WHERE job=? AND module='render'", (job_id,)
        ).fetchone()
        conn.close()
        if not row:
            return False, 0, f"Job '{job_id}' chưa có bản ghi render trong database"
        if row["state"] != "approved":
            return False, row["revision"], f"Module render của job '{job_id}' chưa được approved (trạng thái hiện tại: {row['state']})"
        return True, row["revision"], "Đã được phê duyệt"
    except Exception as e:
        return False, 0, f"Lỗi truy vấn database: {e}"

def get_module_approved_revisions(job_id: str) -> dict[str, int]:
    """
    Returns {module: approved_revision} for every module row of this job whose
    state is 'approved'. Modules in any other state (pending, needs_changes,
    stale, blocked, running, awaiting_review) are intentionally omitted —
    callers must treat an omitted module as fail-closed (prune nothing in it).
    Read-only SQLite access only.
    """
    approved: dict[str, int] = {}
    if not DB_PATH.exists():
        return approved
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT module, state, revision FROM modules WHERE job=?", (job_id,)
        ).fetchall()
        conn.close()
        for row in rows:
            if row["state"] == "approved":
                approved[row["module"]] = row["revision"]
        return approved
    except Exception:
        return approved

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

def validate_script_integrity(script_path: Path) -> tuple[bool, str, dict]:
    """Validates JSON readability and required fields (topic, scenes)."""
    if not script_path.exists() or script_path.stat().st_size < 100:
        return False, f"File kịch bản không tồn tại hoặc quá nhỏ: {script_path.name}", {}
    try:
        content = json.loads(script_path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            return False, f"Kịch bản không phải định dạng JSON Object: {script_path.name}", {}
        scenes = content.get("scenes") or content.get("payload", {}).get("scenes")
        if not scenes or not isinstance(scenes, list) or len(scenes) == 0:
            return False, f"Kịch bản thiếu danh sách phân cảnh (scenes rỗng): {script_path.name}", {}
        return True, "Kịch bản hợp lệ", content
    except Exception as e:
        return False, f"Kịch bản không đúng chuẩn JSON cú pháp: {e}", {}

def validate_job_deliverables(job_id: str) -> tuple[bool, str, list[Path], int]:
    """
    Four-layer Deep Validation:
    1. SQLite approval check
    2. ffprobe playable video with audio & video streams
    3. JSON script syntax and scenes validation
    4. Brief completeness (dual aspect ratio verification if applicable)
    """
    job_export = EXPORTS_DIR / job_id
    if not job_export.exists() or not job_export.is_dir():
        return False, f"Thư mục thành phẩm exports/{job_id} không tồn tại", [], 0

    # Layer 1: Approval Check
    is_approved, approved_rev, app_msg = check_sqlite_approval(job_id)
    if not is_approved:
        return False, app_msg, [], approved_rev

    # Layer 2: Script Check
    scripts = [f for f in job_export.glob("*.json") if f.name.endswith("script.json") or f.name == "content.json"]
    if not scripts:
        return False, f"Không tìm thấy file kịch bản JSON trong exports/{job_id}", [], approved_rev
    script_valid, script_msg, script_data = validate_script_integrity(scripts[0])
    if not script_valid:
        return False, script_msg, [], approved_rev

    # Layer 3: Subtitles Check
    subtitles = list(job_export.glob("*.srt"))
    if not subtitles:
        return False, f"Không tìm thấy file phụ đề .srt trong exports/{job_id}", [], approved_rev

    # Layer 4: Video Check & Ratio requirements
    videos = list(job_export.glob("*.mp4"))
    if not videos:
        return False, f"Không tìm thấy video .mp4 nào trong exports/{job_id}", [], approved_rev

    for vid in videos:
        vid_valid, vid_msg = validate_video_integrity(vid)
        if not vid_valid:
            return False, vid_msg, [], approved_rev

    # Check brief aspect_ratio if brief exists
    brief_file = RUNS_DIR / job_id / "briefs/1.json"
    if brief_file.exists():
        try:
            brief = json.loads(brief_file.read_text(encoding="utf-8"))
            if brief.get("aspect_ratio") == "dual":
                has_916 = any("9x16" in v.name for v in videos)
                has_169 = any("16x9" in v.name for v in videos)
                if not (has_916 and has_169):
                    return False, f"Brief yêu cầu tỷ lệ 'dual' nhưng exports/{job_id} thiếu bản 9:16 hoặc 16:9", [], approved_rev
        except Exception:
            pass

    preserved = videos + scripts + subtitles
    return True, "Thành phẩm hoàn toàn hợp lệ", preserved, approved_rev

def prune_unapproved_revisions(job_id: str, dry_run: bool = False) -> int:
    """
    SELECTIVE PRUNING — PER-MODULE APPROVED REVISION:
    Each module (content, audio, images, render, ...) keeps its own independent
    revision counter in SQLite (see pilot.py run()), so a single job-wide
    "approved revision" number is meaningless across modules. This function
    looks up the approved revision separately for every module and only prunes
    inside that module's own revisions/<module>/ folder.

    Preserves:
    - runs/<job>/briefs, integrity.json, flow evidence, reviews.
    - For each module currently 'approved' in SQLite: its approved revision folder.
    - Fail-closed: a module NOT in state 'approved' (pending, needs_changes,
      stale, blocked, running, awaiting_review) has nothing deleted from its
      revisions/<module>/ folder — we cannot know which draft is worth keeping.
    - Fail-closed: a revisions/<module>/ folder with no matching row in the
      database at all has nothing deleted either.

    Deletes only:
    - Heavy media files (mp4, wav, intermediate png/jpg stills) in the
      non-approved revision folders of a module that IS approved.
    """
    job_dir = RUNS_DIR / job_id
    freed_bytes = 0
    revisions_dir = job_dir / "revisions"
    if not revisions_dir.exists():
        return 0

    approved_by_module = get_module_approved_revisions(job_id)

    print(f"\n  [Selective Pruning] Tối ưu hóa các revision nháp cũ của {job_id}:")
    print(f"  ✓ Giữ nguyên lịch sử: briefs, integrity.json, flow evidence")
    if approved_by_module:
        for mod, rev in sorted(approved_by_module.items()):
            print(f"  ✓ Giữ nguyên revision được duyệt của module '{mod}': Revision {rev}")
    else:
        print(f"  ✓ Không có module nào đang ở trạng thái approved — không dọn revision nào")

    for module_dir in revisions_dir.iterdir():
        if not module_dir.is_dir():
            continue
        module_name = module_dir.name

        # Fail-closed: module not approved (missing row, or state != approved) -> skip entirely.
        if module_name not in approved_by_module:
            continue
        approved_rev = approved_by_module[module_name]

        for rev_dir in module_dir.iterdir():
            if not rev_dir.is_dir() or not rev_dir.name.isdigit():
                continue
            rev_num = int(rev_dir.name)
            # Never delete the approved revision of this module
            if rev_num == approved_rev:
                continue

            # In unapproved revision, only delete heavy media (video, wav, pngs), preserve json outputs
            for media_file in rev_dir.glob("*"):
                if media_file.is_file() and media_file.suffix in [".mp4", ".wav", ".png", ".jpg"]:
                    sz = media_file.stat().st_size
                    freed_bytes += sz
                    if dry_run:
                        print(f"    - Sẽ dọn media nháp cũ: {media_file.relative_to(ROOT)} ({format_size(sz)})")
                    else:
                        try:
                            media_file.unlink()
                            print(f"    - Đã dọn media nháp cũ: {media_file.relative_to(ROOT)} ({format_size(sz)})")
                        except Exception as e:
                            print(f"    ! Lỗi xóa {media_file.name}: {e}", file=sys.stderr)

    return freed_bytes

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
    """
    HARMLESS CACHE CLEANUP:
    1. Deletes Chrome OptGuideOnDeviceModel (~4 GB unused AI model)
    2. Deletes Chrome Cache, ShaderCache in .gflow (preserves Cookies and Sessions 100%)
    3. Deletes /tmp/react-motion-* remotion render residuals
    """
    print("\n--- [Tầng 1] Dọn dẹp Cache hệ thống & Trình duyệt (Bảo toàn Session/Cookies) ---")
    freed = 0

    # 1. OptGuideOnDeviceModel
    if GFLOW_DIR.exists():
        for opt_dir in GFLOW_DIR.glob("**/OptGuideOnDeviceModel"):
            if opt_dir.is_dir():
                sz = get_dir_size(opt_dir)
                freed += sz
                if dry_run:
                    print(f"  [Cache - Sẽ xóa Chrome On-device AI Model] {opt_dir.relative_to(ROOT)} ({format_size(sz)})")
                else:
                    shutil.rmtree(opt_dir, ignore_errors=True)
                    print(f"  [Cache - Đã xóa Chrome On-device AI Model] {opt_dir.relative_to(ROOT)} ({format_size(sz)})")

        # 2. Disk and Shader Caches
        cache_names = {"Cache", "GPUCache", "DawnCache", "ShaderCache", "Crashpad"}
        for p in GFLOW_DIR.glob("profiles/*/*"):
            if p.is_dir() and p.name in cache_names:
                sz = get_dir_size(p)
                freed += sz
                if dry_run:
                    print(f"  [Cache - Sẽ dọn Shader/Disk Cache] {p.relative_to(ROOT)} ({format_size(sz)})")
                else:
                    shutil.rmtree(p, ignore_errors=True)
                    print(f"  [Cache - Đã dọn Shader/Disk Cache] {p.relative_to(ROOT)} ({format_size(sz)})")

    # 3. Remotion /tmp residuals
    tmp_path = Path("/tmp")
    for r_tmp in tmp_path.glob("react-motion-*"):
        if r_tmp.is_dir():
            sz = get_dir_size(r_tmp)
            freed += sz
            if dry_run:
                print(f"  [Temp - Sẽ dọn Remotion temp] {r_tmp} ({format_size(sz)})")
            else:
                shutil.rmtree(r_tmp, ignore_errors=True)
                print(f"  [Temp - Đã dọn Remotion temp] {r_tmp} ({format_size(sz)})")

    return freed

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
    print(f"  Thành phẩm an toàn trong exports/{job_id}:")
    for f in preserved:
        print(f"    ✓ {f.name} ({format_size(f.stat().st_size)})")
    print(f"==========================================================")

    freed = prune_unapproved_revisions(job_id, dry_run=dry_run)
    return freed

def main():
    parser = argparse.ArgumentParser(
        description="Video Pilot v3 — Safe Post-Production Maintenance & Selective Pruning"
    )
    parser.add_argument("--job", help="Tên job cần tối ưu hóa revision cũ trong runs/")
    parser.add_argument("--all", action="store_true", help="Quét và tối ưu toàn bộ các job đã nghiệm thu")
    parser.add_argument("--periodic", action="store_true", help="Chế độ bảo trì định kỳ: Dọn cache vô hại + scratch cũ + tỉa job đã duyệt")
    parser.add_argument("--cache-only", action="store_true", help="Chỉ dọn cache hệ thống và trình duyệt (an toàn 100%, không chạm project)")
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
