# Kết quả triển khai tinh gọn nhánh vocabulary

Thực hiện trên worktree `/tmp/vp-shotfix-vocab`, nhánh `video-vocabulary`, từ commit 2326f79. Thay đổi đang ở working tree, chưa commit/push. Checkout nghiên cứu tại `/home/hongphuoc/Desktop/pipelineFlow` không đổi nhánh và không nhận các sửa mã này.

## Đã triển khai

- Đúng năm skills: vp-vocab → vp-content → vp-media → vp-video; vp-vocab mark sau hoàn tất, vp-clean tùy chọn. Hợp nhất audio/images thành references trong media; humanizer thành references của content. Adapter nạp văn phong một lần vào lượt chi tiết, không vào outline. Cập nhật Rules, AGENTS, GEMINI, INDEX và tài liệu vận hành.
- vp-vocab giữ review mặc định, dùng auto khi được yêu cầu, tỷ lệ/số cảnh theo brief; không ghi cứng render revision 1, không dùng render thành công thay cho quyết định duyệt. Giữ tốc độ TTS 0.92 và cấu hình batch thử nghiệm hiện có.
- Adapter ảnh đơn giữ đường dẫn artifact do queue journal ghi, không di chuyển mất bản tải và không tạo ảnh thứ hai trong thư mục nhận. Metadata media ID nằm cạnh đúng ảnh; không gọi Flow trong kiểm thử.
- Integrity bổ sung bridge, engine B-2, các cấu hình engine dùng chung và mã Python vocab. Ledger/catalog/machine.local không được đưa vào baseline; channel được chuyển thành brief cho job mới. Không sửa baseline lịch sử.
- Controller cho phép truyền cấu hình local tường minh để kiểm thử độc lập; runtime vẫn giữ ưu tiên machine.local. Kiểm tra executable sử dụng cùng cấu hình đã hợp nhất. Có test ưu tiên local và chặn traversal.
- Khóa script rerender_16x9 cũ ngay trước thực thi để tránh ghi đè thành phẩm; giữ code lịch sử để tra cứu. gflow_guard và đường adapter không brief được ghi rõ legacy, không loại bỏ phụ thuộc kiểm thử còn dùng.
- `mark` xác minh đủ ba quyết định hiện tại và hash các bản video đã xuất khớp artifact. Video xuất thiếu/thay đổi thì chưa mark; cần resume/kiểm tra xuất.
- Sandbox có mã engine và chính sách vocab; không sao chép production ledger, machine.local hoặc phiên Flow. Chỉ tạo reservation test trong sandbox cho mục được yêu cầu.
- Dọn dẹp xác minh thư viện video v3 qua SQLite chỉ đọc. Giữ mọi revision/media/bằng chứng/cache/model/profile và /tmp dùng chung; chỉ dọn scratch rỗng quá hạn không symlink. Không tạo lệnh /vp-end chưa có implementation.

## Kiểm tra

- Bộ Python chính: 183/183 đạt trong lượt toàn bộ.
- Các sửa cuối được kiểm tra lại theo phạm vi: 7/7 hợp đồng redesign; 26/26 story-v3; 9/9 adapter nội dung; 5/5 bảo toàn revision. Các nhóm có phần giao nhau với lượt toàn bộ, không cộng thành tổng duy nhất.
- Kho vocab: 28/28 đạt.
- Node B-2: 38/38 đạt.
- Năm skills đều qua quick_validate; git diff --check không có lỗi.
- Test sandbox chạy policy trong tiến trình riêng, xác nhận ledger thật không đổi. Test dọn thử ghi vào kết nối SQLite và bị chặn ở chế độ chỉ đọc. Test video phát hiện bản xuất thiếu/đổi hash hoặc thiếu quyết định media.
- Không thay config.json, vocab/ledger.json, bank.jsonl hoặc prompt_templates.py. Không tạo job/media/video sản xuất, không dọn dữ liệu thật.

Log: thư mục `vocab-redesign-checks/` cạnh báo cáo.

## Giới hạn vận hành

Worktree dùng liên kết local tới Python/Node dependencies sẵn có để kiểm thử; không cài thêm gói. Doctor nhận các công cụ nền nhưng chưa nhận hai môi trường TTS trong worktree này, và machine_review_media_verified vẫn false. Chưa kết nối/sửa phiên B-2, chưa reload service, chưa tạo ảnh hoặc nghe/xem video thật. Acceptance Flow giữ nguyên chưa đạt sản xuất; test kỹ thuật không thay thế nghiệm thu đó.

Skills mới chỉ nằm trong worktree vocabulary này. Muốn dùng cho sản xuất phải mở đúng checkout và chuẩn bị môi trường local của nó; không chạy đồng thời hai checkout với hai ledger độc lập. Mã thay đổi integrity: job lịch sử giữ nguyên, không sửa baseline để chạy tiếp.
