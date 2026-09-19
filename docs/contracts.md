# Hợp đồng v1

control → content → images → audio → render; mỗi mốc cần validate và duyệt.
Payload JSON theo schemas/. Envelope chứa job_id, revision, input_versions,
files (đường dẫn tương đối trong job), checks. Bộ điều phối tạo envelope và hash.
Content nằm ở draft/content.json. Artifact và báo cáo ở revisions/<module>/<revision>/.
Audio dùng nhiều đoạn ngắn cho mỗi cảnh; thời gian từ độ dài WAV, không đoán word timestamps.
Các module chỉ giao tiếp qua payload; adapter không được cấp quyền approve.
Nếu content thay đổi, downstream bị stale. Chỉ ảnh thay đổi thì audio giữ hiệu lực, render stale.
Giới hạn: ánh xạ đủ ý là kiểm tra cấu trúc, không chứng minh lời dẫn đúng ý; người dùng duyệt nội dung.
