---
name: vp-clean
description: Dọn dẹp cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Dọn dẹp

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Không dùng script dọn cũ tự động xóa mất bằng chứng Flow hoặc xóa trọn thư mục job. Tuyệt đối giữ nguyên lịch sử kiểm chứng: briefs, integrity.json, SQLite, phiên đăng nhập và revision đã được duyệt. Chưa có thao tác tự xóa job đang làm dở.

## Quy Trình Bảo Trì & Dọn Dẹp An Toàn (Safe Maintenance & Selective Pruning)
Chỉ thực hiện dọn dẹp khi sản phẩm đã được nghiệm thu hoàn tất trong `exports/`:
- **Chỉ dọn cache vô hại (100% an toàn):** `python3 scripts/clean_production.py --cache-only` (Dọn cache Chrome on-device AI ~4GB, shader/disk cache mà không mất Cookies hay Session).
- **Xem trước tối ưu hóa job & scratch:** `python3 scripts/clean_production.py --periodic --dry-run`
- **Thực thi bảo trì định kỳ:** `python3 scripts/clean_production.py --periodic`
- **Tối ưu hóa một job cụ thể:** `python3 scripts/clean_production.py --job <JOB_ID>`

Cơ chế an toàn tự động:
1. Xác thực 4 lớp: SQLite approval status, ffprobe video integrity, JSON schema, dual-aspect ratio.
2. Selective Pruning: Bảo toàn 100% thư mục job, briefs, bằng chứng Flow và revision được duyệt. Chỉ tỉa bỏ media (.mp4, .wav) của các revision nháp cũ không được duyệt.
3. Whitelist Scratch: Bảo vệ tuyệt đối các file bằng chứng Flow (*evidence*.json), token và script. Chống Path Traversal.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
