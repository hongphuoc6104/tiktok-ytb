---
name: vp-clean
description: Dọn dẹp bộ nhớ đệm và file trung gian của dự án Video Pilot; lưu trữ video thành phẩm tách biệt ra thư mục gốc exports/<job_id>/ và bảo toàn kịch bản cùng phiên đăng nhập.
---

# vp-clean — Dọn Dẹp & Xuất Video Tách Biệt

Áp dụng cho dự án Video Pilot khi người dùng yêu cầu `clear`, `clean`, "dọn dẹp", "xóa rác", hoặc "giải phóng bộ nhớ".

## Nguyên tắc An toàn Cốt lõi
1. **Bảo vệ thành phẩm trước khi xóa:** Luôn sao lưu video hoàn chỉnh MP4, phụ đề SRT, và kịch bản vào `exports/<job_id>/` tại thư mục gốc trước khi xóa bất kỳ file nào.
2. **Bảo toàn kịch bản & metadata nhẹ:** Tuyệt đối không xóa kịch bản gốc (`content.json`, `brief.json`, `draft/content.json`), database `pilot.db`, và file kiểm định.
3. **Bảo toàn phiên đăng nhập:** Giữ nguyên các file `Cookies`, `Login Data` trong thư mục profile Chrome để người dùng không bị đăng xuất khỏi Google Flow.
4. **Chỉ xóa những gì có thể tái tạo lại được:**
   - Các bản revisions ảnh/audio trung gian cũ (giữ lại bản approved cuối cùng).
   - Ảnh chụp màn hình UI preflight / before-submit trong `flow/attempts/`.
   - File cache tạm trong `scratch/`.
   - Bộ nhớ đệm mô hình ngầm của Chrome (`OptGuideOnDeviceModel`, giải phóng ~4.0 GB).
   - Profile thử nghiệm thừa (`test-p10`, giải phóng ~840 MB).

## Cách Sử Dụng
Chạy script dọn dẹp tự động:
```bash
# Xem trước các file sẽ được dọn dẹp (an toàn, không xóa)
python3 .agents/skills/vp-clean/scripts/clean_job.py <job_id> --dry-run

# Thực thi xuất video ra exports/<job_id>/ và dọn dẹp cache
python3 .agents/skills/vp-clean/scripts/clean_job.py <job_id>

# Dọn dẹp sâu (giải phóng tối đa, chỉ giữ lại kịch bản và video xuất bản)
python3 .agents/skills/vp-clean/scripts/clean_job.py <job_id> --deep
```

## Cấu trúc Thư mục Sau khi Dọn Dẹp
Video thành phẩm được lưu riêng biệt tại thư mục gốc của dự án:
```
pipelineFlow/
└── exports/
    └── <job_id>/
        ├── <job_id>_final.mp4      (Video dọc 9:16 hoàn thiện)
        ├── <job_id>_subtitles.srt  (Phụ đề khớp từng câu)
        ├── <job_id>_script.json    (Kịch bản nội dung chi tiết)
        └── stills/                 (Ảnh chụp đại diện kèm phụ đề)
```
