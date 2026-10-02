# 69. eye — Tìm một mắt, rồi cả hai mắt

Nghĩa chọn: **mắt**.
Job: `vocab-eye-55s-001` · content **r2** · brief **r3** · **chờ duyệt**.
Mục tiêu 60 giây; ước tính trung tâm 63.2 giây. Khoảng bất định 47.37–78.98 giây, chưa đo WAV.
5 cảnh · 8 hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.
[Review revision hiện tại](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-eye-55s-001/reviews/content/2/review.md)

## SC01 — Một chấm bé trên bức tranh

Bạn tìm một chi tiết rất nhỏ trong tranh và phải nhìn kỹ hơn. Eye là mắt. Khi chỉ một mắt, mình dùng eye; khi nói hai mắt, từ thường thành eyes. Cùng bộ phận ấy, số lượng làm dạng từ thay đổi.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/69-eye.json).

## SC02 — Nhận ra một mắt

Bạn nhìn sơ đồ và nói: "This is an eye." Đây là một mắt. An eye chỉ một mắt. Hình chỉ đúng một mắt để bạn nhận ra dạng số ít. Nếu chỉ sang mắt còn lại thì vẫn là một mắt riêng, vẫn dùng an eye.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/69-eye.json).

## SC03 — Chuyển sang hai mắt

Trong một trò chơi, người hướng dẫn nói: "Open your eyes." Mở mắt ra. Ở đây, eyes nhắc tới hai mắt. Chỉ cần nhận ra cách dùng số nhiều; mình không học cấu tạo chi tiết của mắt trong video này.

Hình dự kiến: 2; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/69-eye.json).

## SC04 — Chọn theo số lượng

Sơ đồ đang chỉ đúng một mắt. Bạn chọn an eye hay eyes? Hãy đếm phần được chỉ tới rồi nói đáp án.

Khoảng yên lặng cuối cảnh: **4 giây** để người học trả lời. Ghi chú này không phải lời đọc.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/69-eye.json).

## SC05 — Chi tiết đã tìm thấy

An eye là một mắt. Còn eyes là dạng số nhiều. Chi tiết nhỏ trong tranh cuối cùng đã được tìm thấy. Bạn cũng đã biết vì sao có lúc từ này có s, có lúc lại không.

Hình dự kiến: 1; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/69-eye.json).

