# Antigravity CLI cho Video Pilot

Đã cài agy 1.2.7 từ bộ cài chính thức, xác minh SHA-512; nằm trong ~/.local/bin và PATH. CLI dùng được phiên tài khoản hiện có. Không cấu hình Gemini API key hoặc tự bật bỏ qua quyền.

## Cách dùng trong thư mục video-pilot

Kiểm tra kết nối tài khoản, JSON và tiếp tục phiên bằng tiến trình mới:

```bash
.venv/bin/python scripts/agy_pipeline.py smoke
```

Công việc `m1-agy-001` đã được tạo. Với công việc mới khác, thay mã công việc trong ví dụ sau (không tạo lại mã đã có):

```bash
.venv/bin/python pilot.py new m1-agy-001 --brief examples/m1/brief.json
.venv/bin/python pilot.py status m1-agy-001
```

Hiển thị control revision 1 để người dùng duyệt. Sau phản hồi rõ, ghi approve bằng lệnh hiện có cùng nguyên văn phản hồi. Không dùng hướng dẫn này làm bằng chứng người dùng đã duyệt.

Khi control đã approved:

```bash
.venv/bin/python scripts/agy_pipeline.py content m1-agy-001
```

Adapter gửi brief và skill nội dung tới agy, nhận structured_output, kiểm tra hợp đồng rồi tạo content revision chờ duyệt. Không tự ghi duyệt hoặc gọi Flow/TTS/render. Quyết định duyệt vẫn do pilot.py quản lý.

## Lỗi và tiếp tục

- Lỗi tài khoản: chạy `agy` để đăng nhập trực tiếp rồi kiểm tra lại.
- Lỗi JSON hoặc hợp đồng: xem agent-attempts/ATTEMPT/response.json và attempt.json; không coi exit code 0 là đủ.
- Timeout: không tự gửi lại; đọc attempt.json trước khi quyết định chạy lại.
- Mỗi lần thử giữ response, mã hội thoại và bản nháp trước đó. Agent chỉ được yêu cầu trả nội dung; Python ghi file và chuyển trạng thái.
- Bản yêu cầu thay đổi hoặc file bảo vệ thay đổi: chặn nhận kết quả.
- Hồ sơ tạo trước khi bổ sung adapter bị chốt integrity chặn; giữ nguyên để đối chiếu, dùng công việc mới. Không cập nhật baseline cũ.

## Giới hạn

Lượt smoke chứng minh kết nối và tiếp tục ngữ cảnh qua CLI, không thay thế nghiệm thu nội dung. Phép thử hợp đồng thật nằm riêng trong reports/agy-contract-probe: đó là công việc thử có duyệt giả lập, không phải duyệt sản xuất. CLI có thể tự cập nhật; khi phiên bản đổi cần chạy lại smoke và kiểm tra hợp đồng.
