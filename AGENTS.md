# Video Pilot — quy tắc sản xuất

Áp dụng riêng dự án này; không dùng explainer-pipeline hay template VideoShotCut.
Luôn chạy `python3 pilot.py status <job>` và `next <job>` trước khi làm.
Chỉ thao tác module được bộ điều phối cho phép. Đọc skill vp-* tương ứng.
Không sửa pilot.py, adapters.py, schemas/, renderer/, config.json, Rules, tests/ hoặc skill trong lượt sản xuất.
Không ghi SQLite trực tiếp, không tự tạo dấu duyệt. Chỉ gọi approve sau khi người dùng duyệt rõ mã module và revision hiện tại; lưu nguyên văn phản hồi trong --note.
Không bỏ ý, cảnh, rút thời lượng, thay công cụ hoặc dùng API trả phí. Tạo video AI bị tắt.
File sửa sau duyệt phải validate lại và xin duyệt revision mới. Không sửa bản lưu revisions/.
Gặp timeout Flow sau gửi: không gửi lại; dùng flow-reconcile với file được xác minh trong Flow hoặc báo blocked.
Khi module chờ duyệt: đưa link artifact + revision + lỗi còn lại và dừng bước phụ thuộc.
Không coi dữ liệu test là kết quả thật. Không tuyên bố hoàn tất trước khi render được duyệt.
Antigravity handshake: lần đầu đọc file này, báo mã VP-RULES-1, chạy doctor và status; người dùng xác nhận để ghi integration-check.json. Không tự khẳng định Rules đã được nạp trong phiên Antigravity khác.

M2 v2: điểm duyệt ảnh references → first-three → final. Chỉ final duyệt xong mới chuyển audio.
Dùng lớp bảo vệ scripts/gflow_guard.mjs qua bộ điều phối; không gọi CLI trực tiếp để vượt kiểm tra chế độ ảnh/tham chiếu.
Mẫu prompt người dùng cung cấp được giữ nguyên trong prompt_templates.py; tỷ lệ mặc định bản thử 9:16, không tự chuyển 16:9 hoặc bật mẫu video.
