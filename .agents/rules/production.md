---
trigger: always_on
---

Thư mục hệ thống là `sys/`; các đường dẫn bên dưới tính từ thư mục này. Video xuất cho người dùng ở `../video/<tên-video>/`.

Đọc AGENTS.md và docs/workflow.md. Chỉ ba phần content → media → video; review hoặc auto theo job. Không tự tạo bằng chứng hoặc bỏ kiểm tra.
Mọi video của dự án luôn sử dụng nhân vật đại diện kênh cố định tại assets/characters/channel-mascot/reference-v1.png (CH01, áo xanh biển nhạt #8CCFE8, Media ID: de94a39b-155f-4afe-acbb-d9d4b59ad532).
Giải phẫu CH01 chuẩn: 1 thân duy nhất, áo thun cộc tay xanh biển nhạt #8CCFE8, 2 tay & 2 chân que navy tối giản, đầu tròn trắng viền navy đậm, 2 mắt oval đen đặc tối giản, miệng cười tươi lưỡi san hô. Tuyệt đối cấm: vẽ răng, lông mày, mắt hoạt hình có lòng trắng/đồng tử hay vẽ 2 thân áo đè lên nhau. Luôn đính kèm ảnh tham chiếu và dùng dual-reference (Base + Character).
Lời dẫn & Vieneu TTS: Không viết in hoa toàn bộ từ khóa tiếng Anh trong narration (tránh TTS đánh vần từng ký tự). Đại từ I đơn lẻ trong câu ví dụ cần ghi âm 'Ai' để phát âm tự nhiên.
Nhịp thị giác (Visual Beats): N bối cảnh/ví dụ phải có đủ N ảnh và N visual beats. Điểm neo (anchor quote) của từ khóa/công thức phải đặt sớm trong câu để thời gian hiển thị tối thiểu đạt 2.5 - 3.5 giây.
B-2 Illustrator: Chạy qua persistent session socket. Nếu gặp sự cố timeout (state: ambiguous), phải dùng `python3 pilot.py flow-reconcile` kèm bằng chứng UI thật, tuyệt đối không gửi request trùng lặp.
Video dạy từ vựng lấy từ kho vocab/: `python3 vocab/bank.py start JOB` sinh brief và giữ chỗ; duyệt xong video mới `mark`. Không tự chọn từ ngoài kho, không viết brief từ vựng bằng tay.

