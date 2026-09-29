# ISSUE-030 — Kiểm tra integrity chặn nộp bộ 30 kịch bản

Trạng thái: OPEN / chờ người dùng quyết định. Ngày: 2026-09-29.

Job đầu tiên: `vocab-bath-55s-001`. Lệnh `status` trước lượt content báo `Protected implementation changed`. Dừng ngay vòng xử lý; chưa ghi draft/content.json và chưa chạy content. Không có audio, ảnh hoặc video được tạo.

`integrity-diff vocab-bath-55s-001` xác nhận 2 file được thêm so với baseline: `.agents/ORIGINAL_REQUEST.md`, `.agents/sentinel_1/BRIEFING.md`. Không có file modified/removed trong kết quả đối chiếu đó. Agent thực hiện kịch bản không tạo hai file này và không tự xóa hay chỉnh chúng.

Đã tạo 30 job review, giữ chỗ 30 mục kho, cập nhật brief bằng revise-brief theo yêu cầu 35–75 giây. Lời dẫn và ghi chú cảnh đã được soạn tại reports/scripts-30-20260929/authoring trước khi lỗi xuất hiện. Sau lỗi chỉ đóng gói văn bản đã có để bàn giao, không tiếp tục job, không gọi adopt-code, không tạo job thay thế. Chưa đối chiếu integrity riêng từng job còn lại.

## Làm gì cho hết lỗi

Chưa có giải pháp đã được thực hiện/kiểm chứng. Người dùng cần quyết định khôi phục hai file mới về trạng thái baseline hoặc tự xem integrity-diff rồi tự chạy adopt-code cho job cần tiếp tục. Agent không được tự chạy adopt-code. Sau quyết định của người dùng, kiểm tra lại status/next từng job; chỉ nộp content, không chạy media/video nếu chưa được yêu cầu.

## Bản kịch bản đã bảo toàn

`reports/scripts-30-20260929/KICH-BAN-30.md` và các bản đọc riêng được xuất từ lời dẫn đã viết. Chúng là bản thảo biên tập, chưa phải revision content đã được tiếp nhận/duyệt.
