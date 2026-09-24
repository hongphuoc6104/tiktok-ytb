---
name: vp-clean
description: Kiểm kê thành phẩm, dọn dẹp bộ nhớ đệm, lưu trữ video sang HDD và đưa dự án về trạng thái tinh gọn sẵn sàng cho video mới; dùng khi người dùng yêu cầu bảo trì, dọn dẹp hoặc kết thúc phiên làm việc.
---

# Quy Trình Bảo Trì & Dọn Dẹp Video Pilot (vp-clean)

Tài liệu này định nghĩa toàn diện các cấp độ dọn dẹp, giải phóng dung lượng đĩa và lưu trữ sau khi sản xuất video. Chạy từ thư mục gốc hoặc `sys/`.

---

## 1. Kiểm kê Thành Phẩm & Bảo Trì Định Kỳ (Standard Maintenance)
- **Lệnh thực thi:**
  ```bash
  python3 scripts/clean_production.py --periodic --dry-run  # Xem trước
  python3 scripts/clean_production.py --periodic            # Thực thi
  ```
- **Chức năng:** Kiểm tra tính toàn vẹn của các video đã nghiệm thu (ffprobe, container, streams audio/video), bảo vệ dữ liệu v3 và dọn các thư mục tạm rỗng `tmp_*`/`render_output` quá hạn trong `scratch/`.

---

## 2. Kết Thúc Phiên Làm Việc (End Session Protocol)
Khi một hoặc nhiều video đã hoàn thành và không cần tạo ảnh tiếp ngay lập tức, tiến hành đóng phiên để giải phóng RAM & CPU:
1. **Dừng daemon socket Flow / B-2 Illustrator:**
   ```bash
   pkill -f "experiments/b2_illustrator/session.mjs serve"
   rm -f sys/experiments/b2_illustrator/results/controller/session.sock
   ```
2. **Dừng phiên Chrome remote debugging (nếu cần):**
   ```bash
   pkill -f "remote-debugging-port"
   ```

---

## 3. Dọn Dẹp Bộ Nhớ Đệm & File Tạm (Deep Cache Flush)
Khi dung lượng ổ đĩa bị đầy hoặc sau nhiều đợt render:
1. **Dọn dẹp cache package tải về (uv / pip):**
   ```bash
   uv cache clean
   pip cache purge
   ```
2. **Dọn dẹp cache web tĩnh của trình duyệt & hệ thống:**
   - Xóa cache HTTP và Code Cache của Chrome/Brave:
     ```bash
     rm -rf ~/.cache/google-chrome/* ~/.cache/BraveSoftware/* ~/.cache/thumbnails/* ~/.local/share/Trash/*
     rm -rf sys/.gflow/profiles/video-pilot/Default/Cache/* sys/.gflow/profiles/video-pilot/Default/"Code Cache"/*
     ```
   - Xóa model Chrome On-Device tự tải (`weights.bin` ~2.7GB nếu có):
     ```bash
     rm -rf sys/.gflow/profiles/video-pilot/OptGuideOnDeviceModel
     ```
   *(Lưu ý: Luôn bảo toàn `Cookies`, `Local Storage`, `IndexedDB` của Chrome để không làm mất phiên đăng nhập Flow).*

3. **Dọn dẹp ảnh nháp & inspect tạm thời trong dự án:**
   - Xóa ảnh test nháp, crop, snapshot trong `sys/scratch/`:
     ```bash
     find sys/scratch/ -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) -delete
     ```
   - Xóa các ảnh chụp màn hình inspect queue/UI tạm trong `sys/experiments/b2_illustrator/results/controller/`:
     ```bash
     find sys/experiments/b2_illustrator/results/controller/ -type f \( -name "inspect-*.png" -o -name "session-inspect-*.json" -o -name "profile9_*.png" -o -name "queue-*.png" -o -name "current-tab*.png" -o -name "ui-*.png" \) -delete
     ```

---

## 4. Nén & Sao Lưu Video Sang Ổ Cứng Ngoài HDD (Video Archive)
Sau khi video được duyệt hoàn tất, chuyển thành phẩm sang ổ HDD ngoài (ví dụ `/media/hongphuoc6104/DATA_HDD`):
1. **Tạo thư mục đích trên HDD:**
   ```bash
   mkdir -p /media/hongphuoc6104/DATA_HDD/PipelineFlow_Videos/exported_mp4
   ```
2. **Sao chép các file `.mp4` thành phẩm để xem/sử dụng ngay:**
   ```bash
   cp -v video/*/*.mp4 /media/hongphuoc6104/DATA_HDD/PipelineFlow_Videos/exported_mp4/
   ```
3. **Nén toàn bộ thư mục `video/` làm bản lưu trữ dự phòng:**
   ```bash
   tar -czvf /media/hongphuoc6104/DATA_HDD/PipelineFlow_Videos/pipelineflow_videos_archive_$(date +%Y%m%d).tar.gz video/
   ```

---

## 5. Đưa Dự Án Về Trạng Thái Tinh Gọn (Post-Production Reset)
Khi người dùng yêu cầu xóa toàn bộ các thành phần phát sinh tự động để chuẩn bị chạy video mới tinh:
1. **Xóa dữ liệu sinh ra tự động trong các lượt chạy:**
   ```bash
   rm -rf sys/runs/* sys/scratch/* sys/experiments/b2_illustrator/results/* video/* sys/.cache/*
   mkdir -p sys/runs sys/scratch sys/experiments/b2_illustrator/results/controller video sys/.cache
   ```
2. **Nguyên tắc bảo toàn tuyệt đối:**
   - Giữ nguyên 100% mã nguồn dự án (`sys/*.py`, `sys/renderer/`, `sys/schemas/`, `sys/vocab/`).
   - Giữ nguyên sổ cái từ vựng (`sys/vocab/ledger.json`, `sys/vocab/bank.json`).
   - Giữ nguyên nhân vật đại diện kênh cố định (`sys/assets/characters/channel-mascot/reference-v1.png`).
   - Giữ nguyên môi trường Python virtualenvs (`.venv`, `.venv-en`, `.venv-tts`, `.venv-tts-gpu`).

---

## 6. Kiểm Tra & Đồng Bộ Git (Git Commit & Push)
Trước khi kết thúc lượt làm việc, luôn kiểm tra và đồng bộ trạng thái sổ cái lên GitHub:
```bash
git status
git add sys/vocab/ledger.json
git commit -m "chore(vocab): update ledger status"
git push origin video-vocabulary
```
