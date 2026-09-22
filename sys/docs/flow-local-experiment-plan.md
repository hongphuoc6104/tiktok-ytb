# Kế hoạch thử Flow trên máy local — cập nhật 22/09/2026

## Phạm vi mới

Theo yêu cầu mới, ưu tiên thử và tối ưu tool Flow trên máy local, nhánh video-vocabulary. Chưa chạy phép đo đầu-cuối trên PC SATA trong đợt này. Không dùng số đo local để kết luận về PC. Giữ nguyên dữ liệu và thay đổi riêng trên PC.

Từ mới: **borrow (mượn)**, mã borrow.v; kho local báo todo trước khi giữ chỗ. Job: vocab-borrow-local-001, chế độ review, 9:16, bốn cảnh, ba ví dụ và mascot CH01 chuẩn. Không tạo lại wake.

## Thứ tự thực hiện

1. Xác minh tài khoản/project/tool trên phiên Flow local; sao lưu nguồn và cấu hình đúng bản đang chạy. Bản sao từ PC chỉ là tài liệu tham khảo.
2. Ghi ảnh bằng chứng model, số đầu ra và giá hiện hành từng mức x1/x2/x3/x4. Chỉ gửi trường hợp được xác nhận 0 credit; giá chưa rõ ghi chưa xác định. Không có x3 ghi không hỗ trợ.
3. Đo bản hiện tại trước sửa: chuẩn bị prompt, gắn tham chiếu, gửi, ảnh đầu tiên, đủ ảnh, tải và kiểm tra. Ghi riêng thời gian Flow với thời gian controller phát hiện kết quả.
4. Tách số ảnh mỗi yêu cầu và số yêu cầu đồng thời; mặc định 1/1. Mỗi yêu cầu có mã và ánh xạ cảnh/nhịp/prompt/tham chiếu/media ID. Không dùng chung biểu mẫu đang sửa giữa các tác vụ. Ảnh based_on chờ ảnh cha đạt kiểm tra.
5. Thử số đầu ra từng mức; sau đó thử đồng thời 1→2→3→4 trên các prompt độc lập. Dừng tăng khi lỗi hoặc không cải thiện. Timeout sau gửi phải đối chiếu, không gửi lại; lỗi tải chỉ tải lại đầu ra đã có. Đăng nhập/CAPTCHA/hạn mức dừng hàng đợi.
6. Lặp mức cơ sở và mức tốt nhất ba lần. Chỉ đổi mặc định nếu thời gian trên mỗi ảnh đạt giảm ít nhất 15%, không tăng lỗi. Chưa bật flow_batch sản xuất.
7. Sau nghiệm thu tool, tiếp tục job borrow qua content → media → video, duyệt thật từng phần. Đo công đoạn và tài nguyên trên local; tách tổng xử lý khỏi tổng gồm chờ duyệt. Phép đo PC SATA là lượt riêng sau đó.
8. Đồng bộ mã dùng chung lên ba nhánh sau nghiệm thu; giữ dữ liệu, cấu hình riêng và các file độc hữu của từng nhánh.

## Trạng thái hiện tại

- Đã chuyển local sang video-vocabulary, kiểm tra môi trường và tạo job review từ kho.
- Phiên trình duyệt local có thể điều khiển đang yêu cầu đăng nhập Google; đang chờ người dùng kết nối phiên Flow.
- Chưa gửi yêu cầu tạo ảnh; giá Nano Banana Pro x1/x2/x3/x4 chưa xác định trên local.
- Chưa có số đo tốc độ Flow hoặc bằng chứng cải thiện; chưa thay mặc định song song.

## Kết quả chuẩn bị local

- Đã bỏ cơ chế xóa localStorage/tải lại khi tool UNKNOWN hoặc STABILITY ALERT; controller dừng với FLOW_RECONCILIATION_REQUIRED để giữ lịch sử và tránh gửi trùng.
- Kiểm tra cú pháp và 14 kiểm thử attempt-store/contract đạt. Đây là kiểm tra nội bộ, không phải nghiệm thu tốc độ hoặc Flow thật.
- Lượt chạy content đầu tiên của borrow bị chặn: OUTLINE: wrong scene count/order. Chưa có revision nội dung để duyệt; cần sửa dàn ý trước khi chạy lại.

## Kiểm tra giao diện local sau kết nối

Đã xác minh Chrome Profile 10 thật và mở VP Stickman Lab bằng Persistent Session. Đã lưu nguồn tool trước sửa trong experiments/b2_illustrator/results/controller/source-before-*.json. Giao diện Agent settings có x1/x2/x3/x4 và menu Nano Banana Pro/2/2 Lite, nhưng không hiện giá. Chi phí các mức vẫn chưa xác định; chưa gửi tạo ảnh, chưa có phép đo tốc độ. Không suy miễn phí từ tài khoản PRO hoặc số dư. 17 kiểm thử session/attempt-store đạt sau sửa kết nối và bảo toàn trạng thái. Chưa sửa tool trên Flow, chưa bật song song sản xuất.

## Nâng cấp x4 — kế hoạch thực thi

Ngân sách thử nghiệm được người dùng cấp riêng: tối đa 1.000 credit, theo dõi số dư trước/sau từng nhóm; không áp dụng ngoại lệ này cho job sản xuất.

1. Sửa bản Flow 2.1.0 bị mất control và sai cơ chế lưu trạng thái; sao lưu nguồn từng revision. Không chạy bản lỗi.
2. Tách output native (SDK hiện trả một ảnh/call) và concurrency 1–4; không gọi bốn request là native x4.
3. Mỗi nhóm dùng bốn prompt độc lập cố định, mascot CH01, 9:16. Đo concurrency 1/2/3/4; dừng tăng nếu lỗi hoặc throughput giảm.
4. Lặp baseline/best ba lần; tải từng ảnh, đối chiếu mediaId/request, chữ và tham chiếu. Báo thời gian/ảnh đạt và số dư; chỉ đổi mặc định khi cải thiện >=15% và không tăng lỗi. Tăng tốc 4 lần là mục tiêu, không phải cam kết.
5. Thử lỗi bằng mô phỏng không tốn credit; timeout sau submit không resubmit. Chỉ đồng bộ ba nhánh sau nghiệm thu.

Baseline live đầu tiên: Nano Banana Pro 1 ảnh, 25,632 giây từ gửi tới controller phát hiện; JPEG 768×1376 đạt kỹ thuật. Số dư hiển thị 1.050 trước và sau, chưa xác nhận độ trễ cập nhật billing. Ảnh test không phải media đã duyệt cho job borrow.

## Đợt x4 tiếp theo: vocab-4-v2

Dùng lại phiên Profile 10; bốn cảnh độc lập mượn sách/ô/bút/bình tưới. Tăng ràng buộc miệng cười, lưỡi san hô, nét vẽ và khung hình đầy đủ. Trước Start Queue ghi submitting vào nhật ký local có fsync; khi controller quan sát mediaId ghi ngay vào nhật ký local, không đợi cả nhóm hoàn tất. Mất queue sau reload hoặc timeout là unknown, không tự gửi lại. Mỗi batch có tên duy nhất và file intent độc quyền để chặn gửi lại cùng batch. Khoảng trễ quan sát khoảng 1 giây vẫn tồn tại; chưa được coi là transaction nguyên tử với Flow. Không tạo lại tab/kết nối trong khi chạy nhóm.
