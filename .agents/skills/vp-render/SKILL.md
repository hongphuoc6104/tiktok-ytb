---
name: vp-render
description: Video hoàn chỉnh cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---

Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Video hoàn chỉnh

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Chỉ run JOB video sau media được duyệt hợp lệ. 9:16 Việt có phụ đề; 16:9 Anh timeline riêng, ẩn phụ đề. Review: đưa tất cả MP4 và revision để người dùng xem. Auto: máy xem/nghe bản dựng thật; không hỗ trợ thì blocked. Chỉ quyết định video hợp lệ mới là hoàn tất.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.

Job content 3.0: dựng theo danh sách beats/images đã duyệt và timeline riêng Việt/Anh; không tự phát hiện ảnh phụ theo tên hoặc gán mốc giây cố định. Hỗ trợ hold/cut/fade/slide_left/zoom_in/zoom_out. Chữ minh họa đã nằm trong ảnh; không dựng thêm lớp từ vựng. Giữ phụ đề Việt theo quy trình. Chuyển động phóng gần phải được kiểm tra không cắt mất chữ; không tự thêm hiệu ứng ngoài kế hoạch.
