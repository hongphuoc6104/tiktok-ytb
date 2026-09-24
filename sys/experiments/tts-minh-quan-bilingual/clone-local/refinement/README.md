# Đối chiếu độ giống Minh Quân Pro V4

Nguồn chính thức được tra ngày 2026-09-23:
- https://github.com/pnnbao97/VieNeu-TTS — V4 độc quyền qua VieNeu; V3 Turbo là bản mở. Chưa tìm thấy nguồn khác được xác nhận phân phối đúng giọng V4 miễn phí.
- https://docs.vieneu.io/vi/docs/sdk/voice-cloning/ — tham chiếu có thể bỏ khử nhiễu nếu đã sạch.

Đây là âm thanh AI tạo bằng V3 Turbo local, không phải V4. Giữ nguyên mẫu tham chiếu cũ; không xác nhận giấy phép mẫu qua kết quả tìm kiếm này.

A: mẫu đã khử nhiễu, temperature 0.8 (đối chứng tái tạo).
B: mẫu không khử nhiễu, temperature 0.8.
C: mẫu không khử nhiễu, temperature 0.65.

Mỗi cấu hình có câu trùng nội dung mẫu nguồn (same) và câu Việt–Anh mới (mixed). Cùng top_p 0.95, tốc độ gốc, không đổi cao độ, cân mức âm lượng -23 LUFS có giới hạn đỉnh. So sánh A/B để xét khử nhiễu, B/C để xét temperature. Chỉ một lần sinh mỗi mục, chưa kết luận độ ổn định. NumPy seed không bảo đảm mọi bộ sinh trong engine được cố định.

Chưa đánh giá bằng nghe; không tuyên bố bản nào giống hơn. Người nghe cần chấm độ giống chất giọng riêng với độ đúng phát âm. Chưa đổi mặc định sản xuất.

Tái tạo: dùng sys/.venv-tts/bin/python chạy ../refine.py từ gốc dự án với đường dẫn đầy đủ. Thông số và hash WAV trong result.json.
