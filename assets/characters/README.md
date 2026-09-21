# Nhân vật gốc của kênh

Mẫu chuẩn được người dùng chốt ngày 2026-09-21:
[channel-mascot/reference-v1.png](channel-mascot/reference-v1.png).
Thông tin, mã ảnh trên Flow và nhận diện cố định nằm trong
[channel-mascot/character.json](channel-mascot/character.json).

Khi tạo nội dung cho kênh, dùng mẫu này làm nhân vật đại diện: đầu tròn trắng,
mắt oval đen xanh, miệng cười, áo xanh biển nhạt, tay chân người que.
Không tự thiết kế lại mẫu hoặc đổi màu áo. Không gán cứng chủ đề của video.
Nhân vật phụ vẫn có thể khác mẫu này theo kịch bản.

Khi tạo ảnh, phải đính kèm ảnh chuẩn vào Character reference; mô tả bằng chữ
không thay thế ảnh tham chiếu. Nếu kế thừa một cảnh, gắn thêm ảnh cảnh trước vào
Base Scene. Không dùng ảnh cảnh trước thay cho nhân vật chuẩn.

## Trạng thái thực tế

- Đã có ảnh chuẩn trong repository và đã được người dùng chốt.
- Đã tải ảnh vào project Flow `7c815425-4625-4afb-ba84-4290d3fa9ea4`.
- Media ID: `de94a39b-155f-4afe-acbb-d9d4b59ad532`.
- Chưa hoàn thành đăng ký riêng trong mục Characters của Flow.
- Pipeline hiện chưa tự động đọc manifest này; khi thử cần truyền ảnh chuẩn và
  media ID thật vào adapter/tool. Không dùng media ID mặc định của ảnh thử cũ.
- Chưa nghiệm thu tính nhất quán qua nhiều cảnh; không bảo đảm 100% từ metadata.

Ảnh được tạo bằng image_gen tích hợp từ ảnh cảm hứng do người dùng cung cấp.
Không tự chạy pipeline hay tạo thêm ảnh trong lượt chốt mẫu.
