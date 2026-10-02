# 33. free — Chiều nay có thời gian đi chơi

Nghĩa chọn: **rảnh, có thời gian**.
Job: `vocab-free-55s-001` · content **r2** · brief **r3** · **chờ duyệt**.
Mục tiêu 80 giây; ước tính trung tâm 75.7 giây. Khoảng bất định 56.8–94.66 giây, chưa đo WAV.
5 cảnh · 9 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-free-55s-001/reviews/content/2/review.md)

## SC01 — Cuộc hẹn tìm chỗ trống

Bạn làm xong việc và thấy buổi chiều còn trống. Free trong bài này nghĩa là rảnh, có thời gian. Bạn nghĩ tới chiếc vợt nằm ở góc phòng: hôm nay có lẽ nó được ra sân rồi. Buổi sáng còn việc, buổi chiều mới trống. Bạn có thể rảnh ở một thời điểm và bận ở thời điểm khác. Vì vậy, hỏi kèm buổi hoặc giờ giúp hẹn dễ hơn.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/33-free.json).

## SC02 — Rủ đúng thời gian

Bạn hỏi: "Are you free this afternoon?" Chiều nay bạn có rảnh không? Trong câu này, free nói về thời gian của người nghe. Bạn đang hỏi họ có thể dành buổi chiều cho một cuộc hẹn không. Câu trả lời sau ba giờ không có nghĩa cả ngày đều rảnh. Hai người chỉ cần chọn khoảng thời gian mà cả hai có thể dành cho việc chơi cầu lông.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/33-free.json).

## SC03 — Một câu trả lời có ích

Nếu rảnh, người kia có thể đáp: "I'm free after three." Tôi rảnh sau ba giờ. Câu trả lời vừa cho biết có thời gian, vừa giúp hai bạn chọn được lúc gặp cụ thể.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/33-free.json).

## SC04 — Bạn gửi lời rủ

Bạn muốn rủ mình chơi cầu lông chiều nay. Hãy hoàn thành "Are you... this afternoon?" bằng từ chỉ trạng thái có thời gian.

Khoảng yên lặng cuối cảnh: **4 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/33-free.json).

## SC05 — Vợt được ra sân

"Are you free this afternoon?" Từ còn thiếu là free. Bạn có lịch trống, người kia cũng rảnh, cuộc hẹn thành hình. Chiếc vợt được mang ra cửa nhờ một câu hỏi rất ngắn ấy.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/33-free.json).

