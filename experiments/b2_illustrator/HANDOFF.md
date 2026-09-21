# Bàn giao — dừng theo yêu cầu người dùng, 2026-09-21

## Một công việc đã hoàn thành

Giữ phiên điều khiển trên đúng tab Chrome đã xác minh Profile 10.

- Chrome: /opt/google/chrome/google-chrome.
- Profile: /home/hongphuoc/.config/google-chrome/Profile 10.
- Phát hiện thực tế: kết nối cũ còn sống nhưng mở tab mới trả Profile 102.
- Bản sửa: xác minh đường dẫn profile/executable, giữ nguyên tab đã xác minh,
  dùng lại tab này; dừng nếu tab bị đóng/chuyển trang thay vì tự mở tab thay thế.
- Kết nối bản sửa đã xác minh Profile 10; hai lần inspect Flow liên tiếp đạt.
- Bằng chứng: results/bound-tab-inspect.json,
  results/bound-tab-inspect-reused.json.
- Phạm vi nghiệm thu: chuỗi kết nối/kiểm tra trên tab giữ lại, chưa phải adapter
  tạo ảnh hoàn chỉnh hoặc bảo đảm mọi trường hợp chuyển profile của Chrome.

## Mã đã chuẩn bị, chưa nghiệm thu end-to-end

- attempt-store.mjs: nhật ký append-only, fsync, khóa writer, lưu submitting trước
  gửi, unknown không gửi lại, giữ mediaId để tải lại; đối chiếu cần evidence.
- controller.mjs durable-prepare: không bỏ qua legacy attempt đang chưa rõ.
- validate_asset.py: đọc định dạng/kích thước thật, kiểm MIME và tỷ lệ.
- check_contract.mjs: kiểm tra thiếu trường giao diện, không giả nghiệm thu SDK.
- browser-operations.mjs: các thao tác đọc editor/reference/snapshot đã viết;
  chưa chạy thực tế. Session đang chạy chưa nạp các command mới này.
- CONTRACT.md: đầu vào/đầu ra và trách nhiệm controller/tool.
- Kiểm thử cuối: 33 Node tests và 8 Python tests đạt. Có dữ liệu mô phỏng;
  kết quả này không phải ảnh sản xuất hay nghiệm thu chất lượng.
- Kho attempt còn hạn chế: khóa sót sau process crash chặn an toàn, chưa có luồng
  phục hồi khóa có kiểm chứng; chưa có adapter gắn toàn bộ transaction với Flow.
- Subagent Luna high soạn ledger; root đã kiểm tra/sửa bổ sung và chạy test.

## Việc tiếp theo, đúng thứ tự

1. Rà soát và nối ledger vào adapter; hoàn thiện phục hồi khóa và trạng thái không
   rõ, kiểm thử crash thật. Không đổi state để né đối chiếu.
2. Gom các lệnh browser cần thiết rồi mới restart service một lần; Chrome có thể
   yêu cầu Allow. Giữ đúng profile/tab; không dùng extension của Codex hoặc profile mới.
3. Chụp/lưu source của tool hiện tại. Sửa từng lỗi cụ thể và so sánh sau sửa:
   thiếu ô Style, topic/storyboard mặc định, mediaId bị mất nếu lưu thành công lỗi,
   fallback đuôi PNG, nhật ký pending bị bỏ khỏi success, phạm vi localStorage.
4. Xác minh chọn ảnh thật, mediaId từng vai trò base/character, model và chi phí
   thật; không coi code hay thumbnail là bằng chứng conditioning thành công.
5. Một ảnh thật: ghi intent trước gửi; ghi mediaId ngay khi trả về; tải file,
   kiểm byte/MIME/dimensions, rồi xem chất lượng thực tế.
6. Chuỗi cùng cảnh: một người -> thêm hai người -> thêm đồ vật -> chữ trên đồ vật;
   kiểm nhân vật, bố cục, chữ đúng/không chữ thừa; cả 16:9 và 9:16.
7. Kiểm timeout/reload/tải lỗi và queue hữu hạn; không retry generation khi unknown.
8. Chạy qua controller dự án từ Antigravity. Chỉ xác nhận handshake sau thực tế.
9. Chỉ đề xuất tích hợp pipeline khi các tiêu chí thực tế đạt; production chưa đổi.

## Mục tiêu cuối

Một module tạo ảnh người que độc lập, điều khiển qua dự án, có thể được Antigravity
sử dụng: nhận kịch bản đa nhịp không gán cứng chủ đề, tạo nhiều ảnh/cảnh có liên tục
nhân vật/bối cảnh, chữ tạo cùng ảnh theo quy định, quản lý hàng đợi và khôi phục lỗi
không gửi trùng hoặc tốn credit lại. Sau nghiệm thu mới tích hợp phần media của
pipeline content -> media -> video, hỗ trợ review và auto.

## Giới hạn và phiên hiện tại

- Không thay production, không commit/push trong lượt này.
- Không tạo ảnh mới hoặc tiêu credit trong lượt này.
- Ngân sách thử nghiệm đã được người dùng cho phép: 1.050 credit tổng; chi phí ảnh
  B-2 cũ chưa biết nên không khẳng định số credit còn lại.
- Custom tool vẫn chưa tạo ảnh thật. UI audit hiện thiếu Style; conditioning,
  model availability, cost và result recovery chưa nghiệm thu.
- Người dùng yêu cầu dừng ngay sau khi chốt một việc; không tiếp tục thao tác Flow.
- Giữ service/tab đã kết nối để tránh bắt Allow lại không cần thiết; không có queue
  hay tác vụ sinh ảnh chạy nền. Session PTY hiện tại: 64710 (có thể hết khi phiên đóng).
