# 48. sister — Là chị hay em? Phải hỏi thêm

Nghĩa chọn: **chị hoặc em gái**.
Job: `vocab-sister-55s-001` · content **r2** · brief **r3** · **chờ duyệt**.
Mục tiêu 80 giây; ước tính trung tâm 79.3 giây. Khoảng bất định 59.5–99.17 giây, chưa đo WAV.
5 cảnh · 9 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-sister-55s-001/reviews/content/2/review.md)

## SC01 — Chiếc thiệp của ai?

Bạn khoe một chiếc thiệp do người cùng nhà làm, rồi giới thiệu cô ấy là sister. Sister có thể là chị gái hoặc em gái. Chỉ nghe một từ này, người khác chưa biết ai trong hai bạn lớn tuổi hơn. Trong lời giới thiệu đầu, bạn chưa nói tuổi nên người nghe chỉ biết quan hệ chị em gái. Họ cần thêm một thông tin nữa để dịch chính xác thành chị hay em.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/48-sister.json).

## SC02 — Giới thiệu người làm thiệp

Bạn nói: "This is my sister." Đây là chị hoặc em gái tôi. Câu ấy cho biết quan hệ giữa hai người. Để biết cô ấy là chị hay em, người nghe cần thêm thông tin về tuổi. Younger nói nhỏ tuổi hơn, không nói thấp hơn. Một người em gái có thể cao hơn chị hoặc anh mình. Không dùng dáng người để quyết định thứ tự tuổi.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/48-sister.json).

## SC03 — Nói rõ là em gái

Ở câu chuyện này, cô ấy nhỏ tuổi hơn bạn. "She is my younger sister." Cô ấy là em gái tôi. Younger thêm ý ít tuổi hơn. Bạn nhớ cả cụm younger sister để giới thiệu đúng quan hệ này.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/48-sister.json).

## SC04 — Người nhỏ tuổi hơn

Bạn muốn giới thiệu em gái mình. Hãy hoàn thành "She is my younger..." Younger cho biết người ấy nhỏ tuổi hơn bạn.

Khoảng yên lặng cuối cảnh: **4 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/48-sister.json).

## SC05 — Thiệp đẹp chẳng cần lớn tuổi

"She is my younger sister." Từ cần điền là sister. Em nhỏ tuổi hơn nhưng gấp thiệp rất khéo. Bạn vừa giới thiệu được người làm món quà, vừa nói rõ vì sao mình gọi cô ấy là em gái.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/48-sister.json).

