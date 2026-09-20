---
name: vp-clean
description: Dọn dẹp cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Dọn dẹp

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Không dùng script dọn cũ: nó xóa bằng chứng Flow và chọn revision mới nhất thay vì bản được duyệt. Chưa có thao tác dọn sản xuất tự động trong v3. Chỉ dọn file tạm được chỉ định rõ sau khi kiểm tra không thuộc revisions/reviews/flow evidence. Giữ thành phẩm, kịch bản, báo cáo máy, SQLite, model đang dùng và phiên đăng nhập. Không xóa lịch sử để vượt hash.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
