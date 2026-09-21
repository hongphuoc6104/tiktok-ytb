---
name: vp-clean
description: Dọn dẹp cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---

Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Dọn dẹp

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Không dùng script dọn cũ tự động xóa mất bằng chứng Flow hoặc xóa trọn thư mục job. Tuyệt đối giữ nguyên lịch sử kiểm chứng: briefs, integrity.json, SQLite, phiên đăng nhập và revision đã được duyệt. Chưa có thao tác tự xóa job đang làm dở.

## Bảo trì sau chuyển đổi thư mục

Đọc `../INDEX.md` từ sys để tra đường dẫn mới. Chỉ xem trước bằng:
`python3 scripts/clean_production.py --periodic --dry-run`.

Phần scratch chỉ tự dọn thư mục `tmp_*` hoặc `render_output` rỗng và quá hạn; không theo symlink, không xóa media theo tuổi hoặc tên. File và thư mục không rỗng cần danh mục xét riêng vì có thể chứa bằng chứng.

Phần cache trình duyệt và tỉa revision của script vẫn cần rà soát trước khi thực thi: không coi trạng thái module render là đủ chứng minh quyết định video v3 hoặc toàn bộ lịch sử revision đã duyệt. Không chạy --periodic, --all hoặc --job ở chế độ xóa thật trong khi các điều kiện này chưa được kiểm chứng. Không xóa trọn job, phiên đăng nhập, model hoặc bằng chứng.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
