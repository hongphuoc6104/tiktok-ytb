---
name: vp-images
description: Hình ảnh trong media cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Hình ảnh trong media

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Đọc docs/M2-FLOW.md. Dùng run JOB media; ảnh chuẩn và đăng ký là nội bộ, không xin duyệt riêng. Không còn checkpoint ba cảnh đầu. Bàn giao mọi cảnh và ảnh đăng ký cùng WAV ở media. Flow cần bằng chứng giao diện thật 0 credit; timeout dùng flow-reconcile, không gửi trùng. Sửa từng cảnh/nhân vật bằng reject media --scene/--character. Không gọi CLI trực tiếp.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
