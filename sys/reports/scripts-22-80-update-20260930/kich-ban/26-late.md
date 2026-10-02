# 26. late — Hẹn tám giờ, tám giờ mười mới tới

Nghĩa chọn: **trễ hơn giờ cần có mặt**.
Job: `vocab-late-55s-001` · content **r1** · brief **r3** · **chờ duyệt**.
Mục tiêu 80 giây; ước tính trung tâm 79.8 giây. Khoảng bất định 59.85–99.72 giây, chưa đo WAV.
5 cảnh · 9 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-late-55s-001/reviews/content/1/review.md)

## SC01 — Chạy nhanh mà vẫn chậm

Buổi học bắt đầu lúc tám giờ. Bạn đến lúc tám giờ mười. Late nghĩa là muộn, trễ hơn giờ cần có mặt. Chạy rất nhanh ở đoạn cuối cũng không đổi được mười phút đã qua. Cần so hai mốc: giờ bắt đầu và giờ bạn tới. Nếu buổi học bắt đầu chín giờ, đến tám giờ mười chưa phải muộn; con số tám giờ mười tự nó không quyết định.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/26-late.json).

## SC02 — Nói đúng tình trạng

Bạn nói: "I'm late." Tôi đến muộn rồi. I'm là I am nói gọn. Khi báo mình đang bị muộn, nhớ cả câu này để không bỏ mất am trước tính từ late. Ở đây lớp bắt đầu tám giờ, nên bạn đến sau giờ cần có mặt. Đồng hồ và lịch học phải cùng xuất hiện để người xem hiểu lời báo muộn.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/26-late.json).

## SC03 — Nói muộn việc gì

Muốn nói rõ hơn: "I'm late for class." Tôi đi học muộn. For class cho biết việc bạn đã bị trễ. Câu dài hơn một chút nhưng vẫn gắn đúng với cánh cửa lớp trước mặt.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/26-late.json).

## SC04 — Chọn theo tình huống

Thử kiểm tra nhé: lớp bắt đầu tám giờ, bạn đến tám giờ mười. Bạn có thể nói "I'm late" không? Hãy trả lời có hoặc không, rồi tự nói câu phù hợp với tình huống.

Khoảng yên lặng cuối cảnh: **5 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/26-late.json).

## SC05 — Nhận ra rồi điều chỉnh

Có. "I'm late for class." Bạn đến sau giờ bắt đầu nên late là đúng. Ngày mai, nhân vật sẽ chuẩn bị sớm hơn. Còn hôm nay, ít nhất bạn đã nói rõ được điều vừa xảy ra.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/26-late.json).

