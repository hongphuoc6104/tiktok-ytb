# Mốc duyệt triển khai và bước tiếp theo

Người dùng xác nhận: “tôi duyệt bước đầu tiê rồi bước tiếp theo là module nào. khởi tọa git commit dự án đi.”

Ghi nhận duyệt phần triển khai module ① Nội dung và chuyển sang chuẩn bị module ② Hình ảnh. Đây không phải bản ghi approve cho một nội dung sản xuất chưa tồn tại. Tại thời điểm ghi nhận, m1-agy-001 có control revision 1 awaiting_review và content pending; hồ sơ cùng nhật ký vẫn giữ nguyên.

## Module tiếp theo: ② Hình ảnh Google Flow

Mục tiêu: từ nội dung đã duyệt, tạo ảnh thật cho từng cảnh, dùng ảnh tham chiếu cho nhân vật, tải đúng file và bàn giao bảng ảnh để người dùng duyệt.

Đầu vào: phiên bản nội dung được duyệt, danh sách cảnh, hồ sơ nhân vật, phong cách, prompt và ngân sách.
Đầu ra: ảnh theo mã cảnh, bảng xem ảnh, lịch sử tạo và liên kết ảnh tham chiếu.

Các kiểm chứng bắt buộc trước khi nghiệm thu:
- Xác nhận chế độ tạo ảnh và chi phí trên tài khoản thật; chưa xác minh thì dừng.
- Tạo ảnh thật, tải xuống và đối chiếu đúng cảnh.
- Thử một nhân vật qua ba cảnh dùng cùng ảnh tham chiếu; người dùng đánh giá nhất quán.
- Timeout sau gửi không tạo yêu cầu trùng.
- Thiếu ảnh, file lỗi hoặc sai tỷ lệ bị phát hiện.
- Không gọi tạo video AI.

Chưa bắt đầu lượt Flow thật trong yêu cầu tạo commit này. Goal M1 còn các điều kiện nghiệm thu sản xuất; việc duyệt triển khai không tự thay thế những bằng chứng đó.
