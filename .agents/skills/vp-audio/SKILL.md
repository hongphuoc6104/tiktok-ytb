---
name: vp-audio
description: Âm thanh trong media cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---
# Âm thanh trong media

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Dùng run JOB media. Việt Minh Quân Pro / VieNeu ONNX; Anh Alba / Pocket TTS CPU INT8 tốc độ gốc. Dual/16:9 bắt buộc narration_en và .venv-en. Bàn giao WAV Việt/Anh, SRT, thời lượng thật cùng ảnh tại media; không xin duyệt audio riêng. Sửa giọng bằng reject media --part audio; sửa lời dẫn bằng reject content.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.
