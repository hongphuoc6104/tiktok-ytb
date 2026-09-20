---
name: vp-control
description: Điều phối cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Điều phối

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Dùng new --brief FILE --mode review|auto; run/resume chạy đến mốc tiếp theo. Control chỉ là cấu hình nội bộ, không xin duyệt. Chỉ ba tên phần CLI: content, media, video.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
