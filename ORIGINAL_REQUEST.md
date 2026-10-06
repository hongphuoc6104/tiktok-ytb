# Original User Request

## 2026-10-05T23:31:28Z

This is a single self-contained fix; keep it small and focused.
Sửa chữa dứt điểm 3 lỗi thị giác trong video phân lớp 9:16 (dải trắng 1/5 đáy khung hình, mất phụ đề, và hiện tượng giật giật viền trắng của nhân vật), bổ sung unit tests tự động phòng ngừa hồi quy, và xuất lại video hoàn chỉnh end-to-end cho job `vocab-loyal-emperor-9x16-002`.

Working directory: /home/hongphuoc6104/Desktop/codex-normalize
Integrity mode: development

## Requirements

### R1. Khắc phục dải trắng đáy 1/5 trên khung hình dọc 9:16
Hình ảnh nền (background plate) phải hiển thị tràn viền (full-bleed) toàn bộ khung hình 1080x1920, loại bỏ hoàn toàn dải băng trắng 18-20% ở phía đáy màn hình mà không làm biến dạng tỷ lệ hình ảnh.

### R2. Hiển thị phụ đề đầy đủ và nổi trên các lớp đồ họa
Phụ đề (caption/cues) phải luôn hiển thị rõ ràng trên mọi phân cảnh (SC01–SC06), nằm trên lớp nền và các sticker nhân vật/đạo cụ, đồng bộ chính xác với audio và nổi bật trên nền video.

### R3. Triệt tiêu hiện tượng chớp giật viền trắng của nhân vật/sticker
Loại bỏ hoàn toàn hiện tượng nhấp nháy, giật cục quang học (flickering/jitter) quanh viền trắng của các sticker nhân vật; đảm bảo chuyển động camera và sticker diễn ra mượt mà, tự nhiên và liên tục.

### R4. Bộ kiểm thử tự động (Automated Unit Tests)
Viết các bài kiểm thử tự động độc lập để xác minh hồi quy:
- Kiểm tra thứ tự hiển thị (z-index / layering) đảm bảo phụ đề không bị che khuất bởi các lớp đồ họa khác.
- Kiểm tra layout hình nền lấp đầy khung hình dọc 9:16 mà không để hở dải trắng ở đáy.
- Kiểm tra tính liên tục của chuyển động/góc xoay (không có bước nhảy góc/tọa độ rời rạc gây nhấp nháy).

### R5. Tái tạo và nghiệm thu video End-to-End
Chạy lại pipeline kết xuất video cho job `vocab-loyal-emperor-9x16-002`, kiểm tra trực quan như người xem thực tế bằng cách phân tích các frame xuất ra để nghiệm thu việc giải quyết triệt để 3 lỗi trên.

## Acceptance Criteria

### Subtitles & Visibility
- [ ] Phụ đề xuất hiện đầy đủ trong tất cả các phân cảnh có thoại của SC01–SC06.
- [ ] Phụ đề nổi hoàn toàn trên các lớp nền và sticker, có độ tương phản cao, dễ đọc trên thiết bị di động.

### Full-bleed Layout
- [ ] Khung hình 9:16 (1080x1920) không còn dải trắng 18-20% ở đáy màn hình trong toàn bộ thời lượng video.
- [ ] Hình nền phủ kín toàn bộ 1920px chiều dọc mà không làm méo tỷ lệ (aspect ratio).

### Visual Smoothness
- [ ] Không còn hiện tượng giật góc, chớp nháy viền trắng ở các sticker nhân vật qua từng khung hình liên tiếp.
- [ ] Chuyển động sticker êm ái, hòa hợp tự nhiên với bối cảnh hoạt hình.

### Verification & Testing
- [ ] Toàn bộ bộ unit tests tự động mới và test suite hiện có của hệ thống đều chạy PASS (100%).
- [ ] File video kết quả MP4 được tạo mới tại `video/vocab-loyal-emperor-9x16-002/` với đầy đủ thông số kỹ thuật (1080x1920 @ 30fps, H.264/AAC).
- [ ] Trích xuất ảnh frame thực tế từ video kết quả xác nhận không còn bất kỳ lỗi nào trong 3 lỗi thị giác ban đầu.
