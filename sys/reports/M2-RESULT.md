# Kết quả triển khai M2

**Phần triển khai và kiểm thử tự động đã đạt; nghiệm thu Flow thật chưa hoàn tất.**

## Đã triển khai

- Hợp đồng hình ảnh v2, giữ giao diện `items`/`scene_id`/`path` để bộ dựng đọc theo mã cảnh.
- Điểm duyệt `references` → `first-three` → `final` lưu trong SQLite theo revision/hash; chỉ điểm cuối mở audio.
- Ảnh chuẩn, đăng ký nhân vật, đối chiếu riêng vì CLI có thể sinh ngoại hình mới; các cảnh gắn đúng tên tham chiếu đã xác nhận.
- Tạo tuần tự, nhật ký trước gửi, xác minh metadata tải xuống và bằng chứng giao diện; timeout không tự gửi lại.
- Sửa từng cảnh/nhân vật có lý do, giữ lịch sử, không tạo lại ảnh không liên quan; ảnh thay đổi không vô hiệu hóa audio.
- Kiểm tra file/hash, 6 cảnh, tỷ lệ 9:16, tối thiểu 720×1280; bảng ảnh và bản xem dễ đọc.
- Lớp bảo vệ CLI phiên bản 1.1.1 dừng khi không xác nhận Image/model/tỷ lệ hoặc đính kèm nhân vật; không sửa node_modules.
- Lưu nguyên văn ba prompt người dùng cung cấp. Biến thể ảnh có tham số 9:16/16:9; bản thử dùng 9:16 từng ảnh để giữ điểm duyệt. Mẫu video không được phép thực thi.

## Kiểm chứng

65/65 kiểm thử đạt, bao gồm 41 kiểm thử trước và 24 kiểm thử M2/bổ sung. [Nhật ký đầy đủ](m2-tests.txt).

I01–I14 bao phủ: chặn đầu vào chưa duyệt; chế độ/chi phí; từ chối video; tham chiếu nhân vật; ba điểm duyệt; ảnh lỗi/thiếu/sai; phiên bản prompt; timeout/đối chiếu; resume bằng tiến trình mới; sửa sau duyệt; sửa riêng cảnh; login/CAPTCHA/giới hạn; sửa bộ kiểm tra; bàn giao vào hàm dựng thật và dừng trước xuất media.

Tất cả ảnh và dấu duyệt trong bộ test đều là **fixture tạm**, không phải ảnh Flow hay duyệt của người dùng. Kiểm thử đường cấm video chạy lớp wrapper thật nhưng không mở trình duyệt. Chưa có kiểm chứng selector trên tài khoản Flow thật, chưa xác minh giá trên tài khoản, chưa có sáu ảnh thật được duyệt.

Skill `vp-images` đã qua quick_validate; kiểm tra cú pháp Python/JavaScript và git diff whitespace đạt.

## Điểm tiếp tục

Hồ sơ `m2-flow-001`: control revision 1 đang chờ duyệt; content/images/audio/render chưa chạy. Phiên tiến trình mới trả về đúng bước chờ này. Xem [bản duyệt cấu hình](M2-START.md).

Sau control: tạo nội dung bằng Antigravity thật → người dùng duyệt nội dung → đăng nhập và xác minh Flow → duyệt A/B/C. Chưa đóng goal M2. Không có yêu cầu tạo ảnh/video trên Flow được gửi trong lượt triển khai này.

Lịch sử pilot-001 và các công việc trước được giữ nguyên. Mã triển khai thay đổi nên chúng không được tự đặt lại integrity; hồ sơ mới được tạo sau khi mã nguồn và kiểm thử ổn định.
