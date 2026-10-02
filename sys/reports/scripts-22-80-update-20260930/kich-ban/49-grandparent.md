# 49. grandparent — Một người là grandparent, nhiều người là grandparents

Nghĩa chọn: **ông hoặc bà**.
Job: `vocab-grandparent-55s-001` · content **r2** · brief **r3** · **chờ duyệt**.
Mục tiêu 80 giây; ước tính trung tâm 79.9 giây. Khoảng bất định 59.92–99.86 giây, chưa đo WAV.
5 cảnh · 8 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-grandparent-55s-001/reviews/content/2/review.md)

## SC01 — Đếm người trước khi chọn từ

Bạn có một ảnh chụp riêng bà và một ảnh chụp cả ông bà. Grandparent ở số ít là một người ông hoặc bà. Khi nói grandparents, có s, mình đang nhắc đến nhiều người thuộc vai ông bà. Nếu ảnh chỉ có ông, ông cũng là một grandparent. Nếu ảnh chỉ có bà, bà cũng vậy. Không cần cả hai xuất hiện thì từ số ít mới được dùng.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/49-grandparent.json).

## SC02 — Chỉ một người trong ảnh

Bạn nói: "A grandparent is in the photo." Một người ông hoặc bà có trong ảnh. Câu này chưa nói cụ thể là ông hay bà, nhưng đã cho biết chỉ một người đang được nhắc đến. Quan hệ được tính từ bạn qua bố hoặc mẹ tới thế hệ trước. Một người lớn tuổi bất kỳ trong ảnh chưa chắc là ông hay bà của bạn; cần biết liên hệ gia đình.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/49-grandparent.json).

## SC03 — Cả hai cùng tới chơi

Hôm nay cả ông và bà tới nhà. "My grandparents are here." Ông bà tôi ở đây. Grandparents là nhiều người nên câu dùng are. Nhìn hai người trước cửa, bạn hiểu ngay vì sao từ có thêm s.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/49-grandparent.json).

## SC04 — Một ảnh, một người

Trong ảnh chỉ có một người bà. Bạn chọn a grandparent hay grandparents để nói riêng người ấy? Hãy chọn theo số người được nhắc đến.

Khoảng yên lặng cuối cảnh: **5 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/49-grandparent.json).

## SC05 — Hai chiếc ghế đều có khách

A grandparent là đúng khi nói một người. Còn cả ông bà là grandparents. Hai chiếc ghế trong phòng hôm nay đều có khách, nhưng bạn đã biết cách đổi từ khi chỉ muốn nói riêng một người trong hai.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/49-grandparent.json).

