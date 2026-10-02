# 73. ear — Tai nghe một bên, chỉ đúng một tai

Nghĩa chọn: **tai**.
Job: `vocab-ear-55s-001` · content **r2** · brief **r3** · **chờ duyệt**.
Mục tiêu 60 giây; ước tính trung tâm 63.3 giây. Khoảng bất định 47.51–79.17 giây, chưa đo WAV.
5 cảnh · 8 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-ear-55s-001/reviews/content/2/review.md)

## SC01 — Bản nhạc thiếu một nửa

Bạn đeo tai nghe rồi phát hiện âm thanh chỉ ở một bên. Ear là tai. Trong tình huống này, người bạn tháo tai nghe ra để xem bên nào đang có tiếng, chứ không vội tăng âm lượng lên thật to.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/73-ear.json).

## SC02 — Gọi tên một tai

Nhìn hình, bạn nói: "This is my ear." Đây là tai tôi. Ear chỉ một tai. Khi muốn nói hai tai, mình dùng ears, thêm s. Bạn có thể nhìn hai bên đầu để hiểu vì sao có hai cách dùng.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/73-ear.json).

## SC03 — Chỉ đúng bên được yêu cầu

Người hướng dẫn nói: "Touch your left ear." Chạm vào tai trái của bạn. Left cho biết bên trái, còn ear gọi bộ phận. Câu này giúp bạn hiểu người nói muốn chỉ đúng bên nào, không chỉ gọi chung cả đầu.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/73-ear.json).

## SC04 — Điền đúng bộ phận

Câu "Touch your left..." cần từ nào để chỉ tai trái? Hãy nói hết câu rồi chỉ nhẹ tai bên trái của chính mình.

Khoảng yên lặng cuối cảnh: **4 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/73-ear.json).

## SC05 — Dây cắm đã vào hết

"Touch your left ear." Từ còn thiếu là ear. Hóa ra dây cắm lúc nãy chưa vào hết, nên tai nghe chỉ có tiếng một bên. Lỗi nhỏ đã tìm được, còn bạn nhớ thêm một bộ phận cùng cách nói bên trái.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/73-ear.json).

