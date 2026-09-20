---
name: vp-content
description: Kịch bản cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Kịch bản

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Đọc brief-current.json và brief hiện tại. Ghi draft/content.json theo schemas/content-v2.json: đủ ý, đúng số cảnh, nhân vật, coverage và nguồn; narration_en bắt buộc cho dual/16:9. Không bịa dữ kiện. Dùng check-draft, rồi run JOB content. Review: bàn giao review.md và chờ phản hồi đúng revision. Auto: máy đánh giá ngữ nghĩa qua bộ điều phối. Sửa lời dẫn bằng reject content, không sửa revisions.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
