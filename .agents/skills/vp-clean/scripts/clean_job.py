#!/usr/bin/env python3
"""
clean_job.py — Dọn dẹp an toàn bộ nhớ đệm và file trung gian của Video Pilot.
Tự động sao lưu video thành phẩm sang exports/<job_id>/ trước khi dọn dẹp.
"""
import os
import sys
import shutil
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # pipelineFlow root

def get_dir_size(path: Path) -> int:
    """Tính tổng dung lượng (bytes) của thư mục hoặc file."""
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for p in path.rglob('*'):
        if p.is_file() and not p.is_symlink():
            try:
                total += p.stat().st_size
            except (OSError, FileNotFoundError):
                pass
    return total

def format_size(size_bytes: int) -> str:
    """Định dạng kích thước theo đơn vị đọc được (B, KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:3.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def find_latest_revision(module_dir: Path) -> int:
    """Tìm số revision lớn nhất trong thư mục revisions/<module>."""
    if not module_dir.exists():
        return 0
    revs = []
    for d in module_dir.iterdir():
        if d.is_dir() and d.name.isdigit():
            revs.append(int(d.name))
    return max(revs) if revs else 0

def export_deliverables(job_id: str, dry_run: bool = False) -> Path:
    """Sao lưu video hoàn chỉnh, phụ đề và kịch bản vào exports/<job_id>/."""
    job_dir = ROOT / 'runs' / job_id
    if not job_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục job: {job_dir}")

    render_rev_dir = job_dir / 'revisions' / 'render'
    latest_render_rev = find_latest_revision(render_rev_dir)
    if latest_render_rev == 0:
        raise FileNotFoundError(f"Chưa có bản render nào trong {render_rev_dir}")

    video_src = render_rev_dir / str(latest_render_rev) / 'video.mp4'
    if not video_src.exists() or video_src.stat().st_size < 1024 * 1024:
        raise ValueError(f"File video thành phẩm không hợp lệ: {video_src}")

    # Tìm file phụ đề SRT
    audio_rev_dir = job_dir / 'revisions' / 'audio'
    latest_audio_rev = find_latest_revision(audio_rev_dir)
    srt_src = audio_rev_dir / str(latest_audio_rev) / 'subtitles.srt'

    # Tìm file kịch bản JSON
    content_rev_dir = job_dir / 'revisions' / 'content'
    latest_content_rev = find_latest_revision(content_rev_dir)
    content_src = content_rev_dir / str(latest_content_rev) / 'content.json'
    if not content_src.exists():
        content_src = job_dir / 'draft' / 'content.json'

    # Thư mục đích
    export_dir = ROOT / 'exports' / job_id
    stills_dir = export_dir / 'stills'

    print(f"\n📦 [1/4] Xuất bản thành phẩm sang: {export_dir.relative_to(ROOT)}/")
    if not dry_run:
        export_dir.mkdir(parents=True, exist_ok=True)
        stills_dir.mkdir(exist_ok=True)

        # Copy video
        video_dst = export_dir / f"{job_id}_final.mp4"
        shutil.copy2(video_src, video_dst)
        print(f"  ✅ Video: {video_dst.name} ({format_size(video_dst.stat().st_size)})")

        # Copy SRT
        if srt_src.exists():
            srt_dst = export_dir / f"{job_id}_subtitles.srt"
            shutil.copy2(srt_src, srt_dst)
            print(f"  ✅ Phụ đề: {srt_dst.name}")

        # Copy Script JSON
        if content_src.exists():
            content_dst = export_dir / f"{job_id}_script.json"
            shutil.copy2(content_src, content_dst)
            print(f"  ✅ Kịch bản: {content_dst.name}")

        # Copy Stills
        render_dir = render_rev_dir / str(latest_render_rev)
        for still in render_dir.glob('SC*.png'):
            shutil.copy2(still, stills_dir / still.name)
        print(f"  ✅ Ảnh chụp đại diện: {len(list(stills_dir.glob('SC*.png')))} ảnh trong stills/")
    else:
        print(f"  [DRY-RUN] Sẽ copy video: {video_src.name} -> {job_id}_final.mp4")
        if srt_src.exists():
            print(f"  [DRY-RUN] Sẽ copy phụ đề: {srt_src.name}")
        if content_src.exists():
            print(f"  [DRY-RUN] Sẽ copy kịch bản: {content_src.name}")

    return export_dir

def clean_job_revisions(job_id: str, deep: bool = False, dry_run: bool = False) -> int:
    """Xóa các bản revisions cũ và ảnh chụp attempt trung gian."""
    job_dir = ROOT / 'runs' / job_id
    freed_bytes = 0

    print(f"\n🧹 [2/4] Dọn dẹp các revisions trung gian trong {job_dir.relative_to(ROOT)}/...")

    # Xóa các revisions images cũ (giữ lại revision mới nhất)
    img_dir = job_dir / 'revisions' / 'images'
    latest_img_rev = find_latest_revision(img_dir)
    for r in img_dir.iterdir():
        if r.is_dir() and r.name.isdigit():
            rev_num = int(r.name)
            if deep or rev_num < latest_img_rev:
                size = get_dir_size(r)
                freed_bytes += size
                if not dry_run:
                    shutil.rmtree(r, ignore_errors=True)
                print(f"  🗑️ Xóa images/rev {rev_num} ({format_size(size)})")

    # Xóa các revisions audio cũ
    aud_dir = job_dir / 'revisions' / 'audio'
    latest_aud_rev = find_latest_revision(aud_dir)
    for r in aud_dir.iterdir():
        if r.is_dir() and r.name.isdigit():
            rev_num = int(r.name)
            if rev_num < latest_aud_rev:
                size = get_dir_size(r)
                freed_bytes += size
                if not dry_run:
                    shutil.rmtree(r, ignore_errors=True)
                print(f"  🗑️ Xóa audio/rev {rev_num} ({format_size(size)})")

    # Xóa các revisions render cũ
    rnd_dir = job_dir / 'revisions' / 'render'
    latest_rnd_rev = find_latest_revision(rnd_dir)
    for r in rnd_dir.iterdir():
        if r.is_dir() and r.name.isdigit():
            rev_num = int(r.name)
            if rev_num < latest_rnd_rev:
                size = get_dir_size(r)
                freed_bytes += size
                if not dry_run:
                    shutil.rmtree(r, ignore_errors=True)
                print(f"  🗑️ Xóa render/rev {rev_num} ({format_size(size)})")

    # Xóa thư mục flow/attempts (ảnh chụp màn hình trước khi submit và preflight)
    attempts_dir = job_dir / 'flow' / 'attempts'
    if attempts_dir.exists():
        size = get_dir_size(attempts_dir)
        freed_bytes += size
        if not dry_run:
            shutil.rmtree(attempts_dir, ignore_errors=True)
        print(f"  🗑️ Xóa flow/attempts/ ({format_size(size)})")

    return freed_bytes

def clean_scratch(dry_run: bool = False) -> int:
    """Xóa file tạm trong thư mục scratch/."""
    scratch_dir = ROOT / 'scratch'
    freed_bytes = 0
    if not scratch_dir.exists():
        return 0

    print(f"\n🧹 [3/4] Dọn dẹp file kiểm thử tạm trong scratch/...")
    # Xóa các file ảnh crop, inpaint, wav test
    for f in scratch_dir.glob('*'):
        if f.is_file() and f.suffix in ['.png', '.jpg', '.jpeg', '.wav', '.log']:
            size = f.stat().st_size
            freed_bytes += size
            if not dry_run:
                try:
                    f.unlink()
                except OSError:
                    pass
    print(f"  🗑️ Đã dọn file media tạm trong scratch/ ({format_size(freed_bytes)})")
    return freed_bytes

def clean_browser_and_model_cache(dry_run: bool = False) -> int:
    """Xóa cache mô hình nặng và profile rác, bảo vệ Cookies/Session."""
    gflow_dir = ROOT / '.gflow'
    freed_bytes = 0
    if not gflow_dir.exists():
        return 0

    print(f"\n🚀 [4/4] Dọn dẹp bộ nhớ đệm trình duyệt & mô hình AI ngầm (.gflow)...")

    # 1. Xóa thư mục OptGuideOnDeviceModel (Model On-device ~4.0 GB mà Chrome tải ngầm)
    opt_model_dir = gflow_dir / 'profiles' / 'video-pilot' / 'OptGuideOnDeviceModel'
    if opt_model_dir.exists():
        size = get_dir_size(opt_model_dir)
        freed_bytes += size
        if not dry_run:
            shutil.rmtree(opt_model_dir, ignore_errors=True)
        print(f"  ⚡ Xóa OptGuideOnDeviceModel (Chrome AI Cache): {format_size(size)}")

    # 2. Xóa profile test cũ test-p10 (~840 MB)
    test_profile = gflow_dir / 'profiles' / 'test-p10'
    if test_profile.exists():
        size = get_dir_size(test_profile)
        freed_bytes += size
        if not dry_run:
            shutil.rmtree(test_profile, ignore_errors=True)
        print(f"  ⚡ Xóa profile thử nghiệm test-p10: {format_size(size)}")

    # 3. Xóa cache thư mục Cache, GPUCache, Code Cache trong video-pilot (BẢO TOÀN Cookies, Login Data)
    vp_dir = gflow_dir / 'profiles' / 'video-pilot'
    if vp_dir.exists():
        cache_names = ['Cache', 'Code Cache', 'DawnCache', 'GPUCache', 'ShaderCache', 'Crashpad']
        for p in vp_dir.rglob('*'):
            if p.is_dir() and p.name in cache_names:
                size = get_dir_size(p)
                freed_bytes += size
                if not dry_run:
                    shutil.rmtree(p, ignore_errors=True)
        print(f"  ⚡ Đã dọn dẹp Shader & Disk Cache (Bảo toàn 100% Cookies/Login Data)")

    return freed_bytes

def main():
    parser = argparse.ArgumentParser(description="Dọn dẹp bộ nhớ đệm và lưu trữ video thành phẩm.")
    parser.add_argument('job_id', nargs='?', default='stickman-001', help="Mã job cần dọn dẹp (mặc định: stickman-001)")
    parser.add_argument('--dry-run', action='store_true', help="Mô phỏng dọn dẹp, không xóa file thật")
    parser.add_argument('--deep', action='store_true', help="Dọn dẹp sâu cả các ảnh đã render để tiết kiệm tối đa")
    args = parser.parse_args()

    print("=" * 65)
    print(f"✨ BẮT ĐẦU QUY TRÌNH DỌN DẸP & XUẤT THÀNH PHẨM (Job: {args.job_id})")
    print("=" * 65)

    initial_job_size = get_dir_size(ROOT / 'runs' / args.job_id)
    initial_gflow_size = get_dir_size(ROOT / '.gflow')
    initial_scratch_size = get_dir_size(ROOT / 'scratch')
    total_before = initial_job_size + initial_gflow_size + initial_scratch_size

    try:
        # Bước 1: Xuất video thành phẩm an toàn
        export_dir = export_deliverables(args.job_id, dry_run=args.dry_run)

        # Bước 2: Dọn dẹp revisions cũ của job
        freed_revisions = clean_job_revisions(args.job_id, deep=args.deep, dry_run=args.dry_run)

        # Bước 3: Dọn dẹp scratch
        freed_scratch = clean_scratch(dry_run=args.dry_run)

        # Bước 4: Dọn dẹp cache trình duyệt và model ngầm
        freed_browser = clean_browser_and_model_cache(dry_run=args.dry_run)

        total_freed = freed_revisions + freed_scratch + freed_browser

        print("\n" + "=" * 65)
        print("🎉 KẾT QUẢ DỌN DẸP:")
        print(f"  • Dung lượng trước dọn dẹp: {format_size(total_before)}")
        print(f"  • Tổng dung lượng GIẢI PHÓNG: {format_size(total_freed)}")
        print(f"  • Thư mục xuất video: {export_dir.resolve()}/")
        print("=" * 65)

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình dọn dẹp: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
