# Phân tách nền chung và nội dung kênh

`master` là nền dùng chung, không phải chứng nhận mọi chức năng đã nghiệm thu.
Giữ content → media → video, review/auto, hai giọng và người que chuẩn.
Không gán cứng chủ đề. Brief v3 chứa mục tiêu, người xem, nguồn, ý bắt buộc và
planning của từng job. Ví dụ trong examples chỉ là dữ liệu minh họa.

Nội dung kênh học tiếng Anh/từ vựng được lưu trên `thu-nghiem-quy-trinh` tại
commit da10286. Kho từ vựng, ledger và brief cũ vẫn có trong lịch sử Git.
Không dùng chính sách của kênh đó làm mặc định trên nền chung.

`video-nghien-cuu` kế thừa nền chung và giữ hướng dẫn riêng trong docs/research-channel.md.
Chỉ đưa cải tiến dùng chung về master bằng commit riêng; không nhập lại tài liệu,
kho nội dung hoặc cấu hình theo kênh. Không gộp dữ liệu job giữa các kênh.

Thư mục runs, exports, .state và phiên Chrome là dữ liệu local dùng chung khi
chuyển nhánh trong cùng checkout. Đổi nhánh không cô lập các dữ liệu này.
Dùng thư mục làm việc riêng khi sản xuất nhiều kênh đồng thời; không để nhiều
bộ điều khiển tranh cùng phiên Flow. Job cũ giữ lịch sử; không sửa integrity để chạy lại.

Giới hạn hiện tại: 9:16 dùng lời Việt, 16:9 dùng lời Anh; dual tạo cả hai.
Đây là quy tắc đầu ra hiện hành, không phải quy tắc chủ đề. Video nghiên cứu
ngang tiếng Việt cần phát triển tách ngôn ngữ khỏi tỷ lệ trước khi sản xuất.
Chưa nghiệm thu Flow song song hoặc tự động hàng loạt trên máy đích.
