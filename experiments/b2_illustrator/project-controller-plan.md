# Nghiệm thu VP Stickman Lab qua bộ điều khiển dự án

Trạng thái: kế hoạch, chưa phải kết quả kiểm thử. Tool đã được tạo trên Flow;
chưa chứng minh Antigravity vận hành được hoặc chuỗi ảnh đạt chất lượng.

## Điều kiện đầu tiên

- Dùng cơ chế Chrome/session của dự án và Google Chrome đã cài, không dùng
  extension Codex, IAB, Brave, profile mới hoặc tự đoán Profile 10.
- Đối chiếu flow_profile, flow_user_data_dir, flow_profile_directory với phiên
  Chrome thật. Guard hiện mặc định Default, experiment cũ ghi Profile 10,
  trong khi phiên UI hoạt động hiển thị tên 1.1. Chưa chứng minh chúng là một.
- Đọc thông tin profile từ giao diện Chrome và xác nhận tài khoản/project trên
  Flow; không suy đăng nhập từ Preferences, không đọc/copy cookie.

## Phát triển cô lập

Guard hiện chỉ nhận image/character create/batch/auth login. ToolPage của gflow
1.1.1 chỉ có create/list/open; các selector còn cần đối chiếu UI hiện tại.
Không sửa node_modules hoặc mở rộng production guard chỉ để vượt giới hạn.

Luna high chuẩn bị adapter thử nghiệm dưới experiments/b2_illustrator, dùng lại
cơ chế browser/session dự án. Nếu cần tách helper chung, làm thành thay đổi riêng
có kiểm tra hồi quy, giữ nguyên hành vi production. Tool ID phải cấu hình được.
Các thao tác dự kiến: inspect, prepare, submit, collect, reconcile, status.
Đây là giao diện đề xuất, chưa có lệnh chạy tương ứng.

Input: topic/style, ratio, character/base references, preserve/change, allowed
text/style. Output: file thật, MIME/kích thước/hash thật, request/tool identity,
ảnh bằng chứng tham chiếu và nhật ký trạng thái trước gửi. Không tạo lại yêu cầu
có kết quả chưa xác định. Cache phải phân biệt phiên bản tool và prompt mở rộng.

## Vòng thử

1. Inspect không tốn credit: đúng browser/profile/project/tool, iframe, input,
   khả năng upload/download và tài khoản/chi phí quan sát được.
2. Kiểm thử phần mềm: ánh xạ input/output, phụ thuộc ảnh, resume, timeout,
   lỗi upload/download, output containment. Mô phỏng không tính là bằng chứng live.
3. Smoke live một ảnh: đúng tỷ lệ, tải file thật, khớp request, ghi chi phí.
4. Chuỗi bốn hình: một người → thêm hai người → thêm vật → thêm chữ; dùng ảnh
   trước thật và kiểm tra chi tiết phải giữ nguyên ở từng bước.
5. Bộ 16 output theo trial-plan.json: hai tỷ lệ, chữ Việt/Anh/rỗng, nhiều chủ đề.
6. Hàng đợi hữu hạn và khôi phục: không gửi trùng khi ngắt; ảnh phụ thuộc chạy
   đúng thứ tự; xác minh phần lỗi trước retry. Không bật flow_batch production.
7. Antigravity chạy cùng entry point mà không có extension Codex. Thiếu phiên
   Antigravity thật thì ghi chưa kiểm chứng, không giả handshake/integration-check.
8. Chỉ sau các vòng đạt mới dựng video thử và đề xuất tích hợp ba bước hiện tại.

Luna high thực thi adapter/tests và thu evidence; root review mã, ảnh thật,
chi phí và quyết định đạt/chưa đạt. Trần thử nghiệm 1050 credit gồm lượt cũ;
chi phí cũ vẫn chưa rõ. Production tiếp tục yêu cầu 0 credit.

## Nghiệm thu

Mọi ảnh chọn cuối phải đạt nội dung/chữ/tính liên tục. Báo cáo tỷ lệ đạt lần đầu,
thời gian và credit trên ảnh đạt; tối đa hai lần sửa mỗi ảnh. 90% là mục tiêu
mẫu thử, không chứng minh độ tin cậy dài hạn. Nếu browser/profile, reference,
chi phí hoặc trạng thái yêu cầu chưa xác minh, giữ vòng phụ thuộc chưa chạy.
