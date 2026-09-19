# Goal M1 — Nội dung sẵn sàng bàn giao

Từ yêu cầu đã chốt, Antigravity tạo kịch bản, cảnh, hồ sơ nhân vật và prompt theo hợp đồng. Không tạo media ở goal này.

## Tiến độ nghiệm thu

- [x] Hợp đồng v2 theo từng công việc; v1 giữ nguyên để đọc hồ sơ cũ.
- [x] Bộ kiểm tra T01–T14 và các kiểm tra bổ sung chạy bằng dữ liệu thử.
- [x] Kiểm tra tiến trình Python mới đọc lại trạng thái.
- [x] Adapter hình ảnh thật đọc cấu trúc nội dung v2 trong test; chặn trước thao tác bên ngoài.
- [ ] Antigravity thật viết đầu ra; giữ bằng chứng lượt chạy.
- [ ] Một cuộc trò chuyện Antigravity mới tiếp tục đúng bước.
- [ ] Người dùng duyệt nội dung 6 cảnh đúng phiên bản.
- [ ] Bàn giao phiên bản đã được người dùng duyệt tới module hình ảnh.

Goal vẫn đang mở. Kiểm thử tiến trình không thay thế cuộc trò chuyện Antigravity thật. Gọi adapter trong test không chứng minh Google Flow đã kết nối.

## Hợp đồng và lệnh

- `schemas/brief-v2.json`: yêu cầu; lưu bất biến trong `briefs/N.json` cùng con trỏ và hash.
- `schemas/content-v2.json`: bản nháp/đầu ra; tham chiếu phiên bản brief và hash.
- `new JOB --brief FILE`: kiểm tra đầy đủ trước khi tạo công việc; tạo control chờ duyệt.
- `check-draft JOB`: kiểm tra nháp không tăng revision; mã thoát 2 khi không đạt.
- `run JOB content`: tạo phiên bản gồm output.json, content.json, review.md và checks.json.
- `revise-brief JOB --brief FILE --note TEXT`: lưu yêu cầu mới và vô hiệu hóa đầu ra phụ thuộc.
- Các lệnh status, next, resume, approve, reject, validate giữ giao diện cũ.

Lỗi hợp đồng trả danh sách code/path/message/fix. Brief chỉ được thay khi người dùng yêu cầu. Hash phát hiện thay đổi thông thường, không phải chữ ký bảo mật.

## Tiêu chí duyệt người dùng

Đủ ý về nghĩa, lời đọc tự nhiên, diễn biến hợp lý và mỗi cảnh có thể minh họa. Thời lượng dự kiến chưa thay thế WAV thật. Kiểm tra tự động không chứng minh tính đúng đắn của nguồn hay mọi phát biểu trong lời dẫn.

## Giới hạn tương thích

Hợp đồng mới hỗ trợ số cảnh và thời lượng riêng ở M1. Media hiện tại chỉ nhận 6 cảnh, 45–60 giây, 9:16; cấu hình khác bị chặn trước khi gọi adapter. Không tự thu ngắn nội dung.

`pilot-001` giữ nguyên file, trạng thái và lịch sử. Vì mã nguồn đã thay đổi, chốt integrity của hồ sơ cũ sẽ chặn chạy tiếp bằng bản triển khai mới. Không cập nhật lại baseline để vượt chốt; dùng công việc M1 mới.
