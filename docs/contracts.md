# Hợp đồng v1

control → content → images → audio → render; mỗi mốc cần validate và duyệt.
Payload JSON theo schemas/. Envelope chứa job_id, revision, input_versions,
files (đường dẫn tương đối trong job), checks. Bộ điều phối tạo envelope và hash.
Content nằm ở draft/content.json. Artifact và báo cáo ở revisions/<module>/<revision>/.
Audio dùng nhiều đoạn ngắn cho mỗi cảnh; thời gian từ độ dài WAV, không đoán word timestamps.
TTS dựng nguyên một cảnh trong một lượt để giữ ngữ điệu liên câu, rồi cắt lại theo câu ở
chỗ im lặng để mỗi câu vẫn là một cue phụ đề; cảnh dài quá tts_max_chars hoặc không cắt
được thì tự lùi về dựng từng câu. Khoảng nghỉ nằm trong chính file WAV của đoạn, nên
timeline vẫn liền mạch. Giọng, temperature, độ dài nghỉ và độ to đọc từ config.json.
Brief aspect_ratio dual hoặc 16:9 bắt buộc mỗi cảnh có narration_en; stage audio dựng thêm
track tiếng Anh với timeline riêng theo cảnh, và bản 16:9 chạy theo timeline đó chứ không
theo tiếng Việt. Bản 9:16 luôn dùng tiếng Việt kèm phụ đề; bản 16:9 dùng tiếng Anh, ẩn phụ đề.
Các module chỉ giao tiếp qua payload; adapter không được cấp quyền approve.
Nếu content thay đổi, downstream bị stale. Chỉ ảnh thay đổi thì audio giữ hiệu lực, render stale.
Giới hạn: ánh xạ đủ ý là kiểm tra cấu trúc, không chứng minh lời dẫn đúng ý; người dùng duyệt nội dung.
