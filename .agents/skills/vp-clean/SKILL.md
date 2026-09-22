---
name: vp-clean
description: Kiểm kê thành phẩm và dọn thư mục tạm rỗng của Video Pilot; dùng khi người dùng yêu cầu bảo trì hoặc dọn sau video.
---

# Bảo trì

Chạy từ `sys/`, đọc `AGENTS.md` và `docs/workflow.md`. Xem trước bằng `python3 scripts/clean_production.py --periodic --dry-run` hoặc `--job JOB --dry-run`.

Công cụ kiểm tra quyết định v3 và MP4 hiện tại trong `video/<job>/`. Chỉ thư mục scratch `tmp_*`/`render_output` rỗng, quá hạn, không symlink được phép dọn. Giữ mọi revision/review, media, Flow journal, SQLite, ledger, session/profile và model. Không suy file thừa từ tuổi hoặc tên.

Công cụ không xóa cache trình duyệt hoặc /tmp dùng chung; không có lệnh /vp-end. Chỉ kiểm kê phần cần xem xét riêng. Dọn không thay đổi quyết định duyệt và không là bước bắt buộc trước video tiếp theo.
