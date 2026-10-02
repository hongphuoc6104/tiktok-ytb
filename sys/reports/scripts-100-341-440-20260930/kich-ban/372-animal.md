# 372. animal — Đoán con vật qua bóng

**Nghĩa:** con vật. **Mục tiêu bài:** Dùng animal để hỏi tên một con vật.

**Diễn tiến:** Thấy bóng → hỏi → lật thẻ → nhận diện.

**Lượt thực hành:** Lựa chọn hoặc nhận diện theo hình/tình huống. **Dự kiến:** 57.0 giây.

**Trạng thái:** content revision 1, đã được người dùng duyệt. Mã bài: `vocab-animal-script-372`.

[Bản duyệt gốc](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-animal-script-372/reviews/content/1/review.md) · [Bản sao trong hồ sơ](../reviews/372-animal.md)

## SC01 — Mở tình huống

Tai dài thế này, bạn đoán ra chưa? Animal là con vật. Bạn đang chơi đoán hình với người bạn, chỉ nhìn thấy bóng một con vật trên thẻ; mặt có hình đầy đủ đang bị úp xuống.

**Chữ minh họa cho phép:** “animal”

**Hình dự kiến:** 1; tập trung hành động, đồ vật hoặc quan hệ vị trí được nói tới.

## SC02 — Câu dùng thứ nhất

Bạn hỏi: "What animal is this?" Đây là con vật gì? What animal hỏi tên loại con vật; người bạn nhìn đôi tai rồi đưa ra một dự đoán trước khi lật thẻ.

**Chữ minh họa cho phép:** “What animal is this?”

**Hình dự kiến:** 1; tập trung hành động, đồ vật hoặc quan hệ vị trí được nói tới.

## SC03 — Diễn biến tiếp theo

Lật ra, bạn nói: "This animal has long ears." Con vật này có tai dài. Hình con thỏ giúp kiểm tra dự đoán; animal vẫn là cách gọi chung con vật trong câu.

**Chữ minh họa cho phép:** “This animal has long ears.”

**Hình dự kiến:** 2; cặp hình giữ góc cho thay đổi trước/sau.

## SC04 — Bạn thử nói

Đến lượt bạn hỏi người kia về một con vật trong ảnh. Nói "What animal is this?" rồi chọn con vật mình muốn đưa ra câu đố. Chưa cần trả lời thay họ nhé.

**Chữ minh họa cho phép:** “What animal is this?”

**Hình dự kiến:** 1; tập trung hành động, đồ vật hoặc quan hệ vị trí được nói tới.

**Chờ 4 giây cuối cảnh** để người xem trả lời hoặc nói lại; phản hồi ở cảnh sau.

## SC05 — Đáp án và kết thúc

"What animal is this?" Đây là con vật gì? Với tấm thẻ vừa rồi, câu trả lời là con thỏ. Bạn có thể đổi ảnh để chơi tiếp, còn mẫu hỏi vẫn dùng được.

**Chữ minh họa cho phép:** “What animal is this?”

**Hình dự kiến:** 1; tập trung hành động, đồ vật hoặc quan hệ vị trí được nói tới.

