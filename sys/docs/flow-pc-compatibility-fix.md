# Sửa tương thích Flow trên PC — 22/09/2026

## Thay đổi cần giữ khi cập nhật

Bản PC 493cdd7 gán preflight.png vào before_submit của mascot. Khi cấu hình mới không tạo preflight.png, adapter sao chép file không tồn tại và chặn media. Bản sửa này bỏ phép gán đó: ảnh tài khoản/preflight không phải ảnh trước gửi của yêu cầu.

Hàm copy_optional_flow_screenshot chỉ sao chép nguồn có thật. Khi flow_require_ui_evidence=false, nguồn trống hoặc đã mất được bỏ qua; không tạo ảnh trắng, không báo đã chụp. Khi bật lại chế độ bắt buộc, thiếu nguồn thật vẫn dừng. Không dùng file before-submit cũ để giả đáp ứng yêu cầu mới. Nguồn trùng đích không sao chép lên chính nó.

Giữ sửa shutil.move của PC để thư mục đầu ra đơn chỉ có một ảnh cho pipeline nhận diện. Queue vẫn giữ raw output trong journal; nếu file nguồn bị di chuyển, mã collectResults có thể ghi lại từ raw mà không gọi Flow. Không đổi move thành copy đơn thuần vì sẽ tái tạo lỗi hai file ảnh trong thư mục.

## Cách cập nhật cho agent PC

- Giữ thay đổi local và cấu hình machine.local.json; fetch rồi merge/pull nhánh video-vocabulary, không reset --hard.
- Kiểm tra config: flow_batch=true, flow_queue_trial_enabled=true, flow_require_ui_evidence=false.
- Không đưa lại before_submit trỏ đến preflight.png trong adapters.py khi xử lý conflict.
- Đây là sửa adapter Python, không cần remix/share lại tool Flow hoặc khởi động lại Chrome. Lượt pipeline Python mới nạp bản sửa; tác vụ Python đang chạy dùng mã cũ phải kết thúc trước khi chạy lại.
- Không xóa journal hay tự mở khóa ambiguous cũ. Kiểm tra đã gửi hay chưa trước khi tiếp tục.
- Giữ nguyên dữ liệu từ vựng và các commit riêng PC. Phần chụp nhanh CDP của PC vẫn được giữ cho thao tác inspect tùy chọn.

Thay đổi này sửa lỗi tương thích file screenshot; không xác nhận nghiệm thu toàn pipeline hay xác minh chi phí Google.
