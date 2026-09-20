# Hợp đồng v3

Quy trình công khai: content → media → video, xem [workflow.md](workflow.md).
Mode review/auto cố định tại lúc tạo job. Mỗi mốc có manifest, revision, snapshot hash các module đầu vào và quyết định riêng actor=user/machine. Máy kiểm tra kỹ thuật nội bộ không tạo phản hồi người dùng.

Nội bộ giữ control/content/images/audio/render và envelope theo schemas/. Đây là định dạng dữ liệu, không phải năm điểm duyệt. images chỉ có references/final nội bộ; không còn first-three hay ảnh proof riêng. Media gồm ảnh cuối và audio cùng snapshot, không thể duyệt một nửa để mở render.

Đổi content làm mất hiệu lực media/video. Đổi ảnh giữ audio nhưng buộc duyệt lại media/video. Không sửa revisions. Hash file được kiểm tra lại trước chuyển bước; báo cáo máy phải khớp artifact đã xem.

Việt VieNeu ONNX Minh Quân Pro; Anh Pocket TTS CPU INT8 Alba tốc độ gốc. Tiếng Anh có timeline riêng. Phụ đề Việt căn theo đoạn WAV, chưa phải word-level alignment. Structural validation không chứng minh đúng ngữ nghĩa; review mode dùng người dùng, auto dùng báo cáo đánh giá thật và chặn unsupported.
