# Kết quả sửa vòng lặp ảnh — 24/09/2026

Đã triển khai trong mã nguồn và kiểm thử bằng job tạm/provider giả. Không gửi yêu cầu Flow thật, không sửa revision/review/integrity của `vocab-scold-001`.

## Thay đổi

1. Thêm `reject --image IMAGE_ID [--ratio ...]`. Ghi chú nhắc một hình không được áp lẫn cho các hình khác trong cảnh. `--scene` vẫn là sửa chủ động toàn cảnh.
2. Tách phản hồi nguyên văn khỏi kế hoạch sửa hiện hành; lịch sử thêm mới, không ghi đè. Prompt không nối lịch sử, không bung mã thành cả mô tả, không lặp chính sách chữ. Chỉ dẫn mascot hướng tới đúng CH01; Flow bridge giữ đúng prompt đã lưu.
3. Thêm kế hoạch sửa gắn với hash ảnh trước/sau, mã lỗi ổn định, bằng chứng, trạng thái `new/remaining/resolved`, tư thế/bố cục cụ thể. `repair-status` cung cấp thông tin để lập kế hoạch.
4. Media review có ảnh trước/sau. Auto phải phân loại tiến bộ theo từng ảnh và không được báo lỗi đã sửa nếu byte ảnh không thay đổi. Cùng bộ artifact đã có kết quả media/video chưa đạt sẽ không bị đánh giá lại tự động; `--retry-review` dành cho yêu cầu đánh giá lại rõ ràng sau khi xử lý nguyên nhân.
5. Chặn kế hoạch không thay đổi, yêu cầu đối chiếu từ lượt thứ hai, yêu cầu thay đổi tư thế/bố cục sau hai lượt cùng lỗi và giới hạn tuyệt đối sáu lượt/đích. `needs_attention` được giữ riêng từng đích; sửa đích khác không xóa điểm dừng.
6. Cache ảnh con dựa trên mã/hash ảnh nền, không dựa vào đường dẫn revision. Giữ audio và ảnh không bị tác động. Lưu nhật ký trước dispatch batch; phân loại kết quả từng yêu cầu. Kết quả `generated` có chế độ chỉ thu hồi; `ambiguous/submitted` vẫn cần đối chiếu thật, không tự gửi trùng.

## Kiểm chứng

- Bộ Python toàn dự án: **222/222 đạt**, 225,401 giây.
- Hai kiểm thử bổ sung biên adapter/bridge: **2/2 đạt** (batch một phần và giữ nguyên prompt khi thu hồi).
- Bộ nhật ký/queue Node: **18/18 đạt**.
- Sau tinh chỉnh phạm vi chỉ dẫn CH01, chạy lại nhóm ảnh: **35/35 đạt**, nhóm story-v3: **26/26 đạt**.
- Nhóm chống vòng lặp chuyên biệt: **13/13 đạt**, nằm trong bộ Python toàn dự án; không cộng lặp vào tổng.
- Kiểm tra cú pháp Python/JavaScript và `git diff --check` đạt.

Lỗi ban đầu ở kiểm thử khởi động tiến trình mới được sửa bằng cách sao chép thư mục `scripts` vào fixture. Fixture workflow dùng provider đơn ảnh được cấu hình rõ `flow_batch=false`; batch có kiểm thử riêng. Không nới quy tắc sản xuất để làm tests đạt.

## Phạm vi áp dụng

Xem [hướng dẫn vận hành](../docs/image-repair-loops.md). Những thay đổi này làm thay đổi protected implementation: dùng cho job mới theo workflow, không thay baseline job cũ để tiếp tục.

Kiểm thử xác nhận cơ chế điều phối, cache, giới hạn và phục hồi trong môi trường giả lập. Chưa nghiệm thu Flow UI thật hoặc chất lượng ảnh/video thật. Việc hiểu hai câu sửa khác chữ nhưng cùng nghĩa vẫn cần người/bộ đánh giá xem xét; giới hạn hữu hạn là chốt chặn khi phân loại ngữ nghĩa chưa đủ.
