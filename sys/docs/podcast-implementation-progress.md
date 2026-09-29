# Kết quả nâng cấp pipeline podcast

## Phạm vi đã chốt

Viết và duyệt lời văn/chỉ dẫn giọng trước TTS, tối đa ba vòng sửa tổng. Tạo giọng Colab có checkpoint, không nghe duyệt lại. Dùng ảnh cố định người dùng cung cấp rồi ghép video 16:9. Xóa tuyến tạo/duyệt ảnh podcast. Không chạy thử dịch vụ hoặc tạo tập thật trong lượt nâng cấp.

## Các thay đổi

- Skill vp-podcast nhận yêu cầu tự nhiên; CLI create có request ID ổn định, topic/minutes tùy chọn và backend mặc định.
- Writer/reviewer chuyên podcast ngủ, chống sáo rỗng, ẩn dụ gượng, lặp ý và nội dung gây tải suy nghĩ. Chỉ dẫn giọng tách riêng, có neo nguyên văn và giới hạn khả năng TTS rõ ràng.
- Ba vòng sửa chung; checkpoint bền vững, phản hồi tài khoản được lưu/dùng lại; không gửi trùng khi chưa rõ kết quả. Khóa nội dung/giọng đã duyệt trước TTS.
- Hiệu chỉnh giọng dùng cache đúng cấu hình; transport CLI; checkpoint tiếp tục phần thiếu; không kiểm tra số dư trả phí để suy ra khả năng dùng thử miễn phí.
- Ảnh `assets/podcast/sleep-default.png` 2048×2048, hash khớp cấu hình, đã xem đối chiếu đúng ảnh người dùng. Không phụ thuộc đường dẫn Downloads. Giữ nguyên ảnh trong 1920×1080 bằng contain/pad nền #202840.
- Xóa `podcast/image.py`, `podcast/image_review.py`, bài test tạo ảnh và thay đổi queue B-2 chỉ phục vụ podcast. Bỏ Flow khỏi preflight/backend; mã B-2 chung của các tuyến khác được giữ nguyên.
- Kiểm tra checksum trước ghép/xuất, giữ master lệch thời lượng, khóa toàn episode, không tái tạo phần hoàn tất. Xuất MP4 theo codec/thời lượng đã định rồi đánh dấu hoàn tất.
- Đồng bộ AGENTS, Rules, skill, README và kế hoạch theo phạm vi cuối cùng; giữ dữ liệu sản xuất/revisions/WAV cũ.

## Kiểm chứng

- 28 bài kiểm thử Python podcast đạt, gồm điều phối toàn tuyến bằng backend/artifact giả và chạy tiếp không lặp stage.
- Compileall, kiểm tra diff và kiểm tra skill đạt.
- Ảnh lưu trong dự án có hash khớp still.json; bộ ghép dùng scale giảm để giữ trọn ảnh và pad, không crop.
- Không chạy thử Colab/Flow hoặc tạo MP4 sản xuất trong phần nâng cấp đã chốt offline. Các bài kiểm thử không phải sản phẩm thật và không chứng minh chất lượng TTS thực tế.

Luồng cho người dùng: **“Tạo video podcast” → kịch bản → giọng đọc → ảnh cố định + âm thanh → MP4 YouTube 16:9**. Hướng dẫn tại [README](../podcast/README.md).
