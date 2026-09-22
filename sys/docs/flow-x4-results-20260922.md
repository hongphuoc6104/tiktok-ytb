# Kết quả thử Flow x4 trên local

Ngày 22/09/2026; nhánh video-vocabulary; Chrome Profile 10; VP Stickman Lab. Chỉ thử nghiệm độc lập, không phải media đã duyệt của job borrow.

## Kế hoạch và kết quả ban đầu

Mục tiêu: hàng đợi 1–4 yêu cầu ảnh độc lập; giữ đầu ra mỗi SDK call là 1. Không coi đây là x4 ảnh native trong một call. Mức 3 đã bị Tool Builder bỏ khỏi UI bản sửa và chưa thử; cần khôi phục.

| Mức đồng thời | Ảnh trả về | Thời gian nhóm | Giây/ảnh trả về | Số dư sau |
|---|---:|---:|---:|---:|
| 1 (tool cũ) | 1 | 25,632 | 25,632 | 1.050 |
| 2 (tool mới) | 2 | 31,172 | 15,586 | 1.050 |
| 4 (tool mới) | 4 | 29,298 | 7,325 | 1.050 |

Số dư ban đầu 1.050; chưa thấy giảm sau 7 ảnh thử. Chưa kiểm chứng lịch sử billing hoặc độ trễ cập nhật, không kết luận miễn phí tuyệt đối. Ngân sách thử nghiệm được cấp: tối đa 1.000 credit.

Đây là smoke test một lần mỗi mức, prompt và số lượng chưa hoàn toàn tương đương; không dùng tỷ số trên để tuyên bố tăng tốc 4 lần hay đủ nghiệm thu >=15% trên ảnh đạt. Chưa lặp baseline/best ba lần.

## Chất lượng và giới hạn

Hai ảnh nhóm 2 đúng bối cảnh và có mascot áo xanh, đã xem trực tiếp. Nhóm 4 trả đúng bốn mediaId khác nhau, đúng các vật sách/ô/bút/bình tưới. Cảnh ô REQ-JACTC lệch phong cách mặt/nét mascot; cảnh bút REQ-DQGGT thiếu miệng cười có lưỡi san hô. Chưa tính bốn ảnh là bốn ảnh đạt. Chưa đổi mặc định concurrency=1.

Đã sửa source trên Flow qua Tool Builder và rà soát từng bản. Bản đầu có lỗi mất controls, ghi mediaId trễ, xử lý UNKNOWN sai. Bản hiện tại đã khôi phục controls, lưu intent trước call, lưu mediaId trước decode và dừng khi lỗi sau submit. Vẫn chưa nghiệm thu migration/reload, phụ thuộc based_on, mức3, thời gian download và lỗi giả lập. Không bật flow_batch hoặc đồng bộ production lúc này.

## Bằng chứng local

- `sys/maintenance/flow-performance-20260922/`: snapshot nguồn trước/sau, credit-before/after, baseline-summary, repaired-02-app.js.
- `sys/experiments/b2_illustrator/results/controller/parallel-smoke-2-result.json` và `parallel-smoke-4-result.json`: request, prompt, mediaId, timestamp, ảnh raw.
- Ảnh nhóm4: REQ-25HQP.jpg, REQ-JACTC.jpg, REQ-DQGGT.jpg, REQ-UBMYD.jpg cùng thư mục controller.

## Tiếp theo

Khôi phục mức3 và kiểm tra persistence/reload, sửa prompt mascot rồi chạy so sánh cùng bộ bốn prompt ở mức1 và4 ba lượt. Tính thời gian/ảnh đạt và chi phí; chỉ sau nghiệm thu mới đồng bộ mã chung ba nhánh và tiếp tục pipeline review borrow.

## Nghiệm thu thực tế bổ sung — không đạt điều kiện tích hợp

Đã chạy phép thử không tiêu credit: nhập prompt thử, bấm Initialize Generation để enqueue nhưng **không bấm Start Queue**, lưu bản sao trạng thái rồi tải lại trang. Trước tải lại có request REQ-UQLZP ở QUEUED; sau tải lại state đọc được là `{}`. Kết luận: hàng đợi không tồn tại bền vững qua reload trong môi trường Flow thực tế này. Không suy ra nguyên nhân chính xác từ riêng phép thử.

Bằng chứng: `sys/experiments/b2_illustrator/results/controller/acceptance-reload-1790038235242.json`. Không có generation được gửi trong phép thử.

Đã chuẩn bị đưa vào vocab theo hướng an toàn:

- Dịch vụ B-2 chạy bằng systemd user transient unit, tránh phụ thuộc vòng đời terminal tác vụ; chưa cài tự chạy khi đăng nhập.
- Cầu nối Python kiểm tra kết nối thành công và giữ file spec để đối chiếu sau timeout.
- Controller cũ bị chặn khi gặp giao diện hàng đợi mới; không để nhầm nút enqueue thành nút tạo ảnh.
- Hồ sơ nghiệm thu máy đọc tại `sys/experiments/b2_illustrator/acceptance.json`, production_ready=false. Đây là hồ sơ trạng thái, chưa phải cấu hình bật batch.

Còn phải làm: dùng AttemptStore phía máy local làm nguồn trạng thái có thẩm quyền, ghi submitting trước từng call và generated/mediaId ngay khi trả về, giữ unresolved qua restart, đối chiếu Flow trước retry. Kiểm thử lại reload/timeout/download và based_on, sau đó mới chạy đủ so sánh chất lượng/thời gian ba lượt. Không đưa bản tool hiện tại vào sản xuất hoặc đồng bộ ba nhánh dưới danh nghĩa đã nghiệm thu.

## Đợt vocab-4-v2 — đã chạy x4 với nhật ký local

Bốn yêu cầu độc lập hoàn tất trong **30,307 giây**, khoảng 7,577 giây/ảnh trả về. Tất cả JPEG 768×1376, bốn mediaId riêng và kiểm tra kỹ thuật đạt. Số dư hiển thị trước/sau đều 1.050. Bằng chứng: vocab-4-v2-intent.json, vocab-4-v2-events.ndjson (fsync từng sự kiện), vocab-4-v2-result.json trong results/controller; credit ở maintenance/flow-performance-20260922/batch-v2-credit-before.json và batch-v2-credit-after.json.

Đã xem từng ảnh: miệng cười/lưỡi san hô mascot xuất hiện trên cả bốn ảnh; không lẫn vật giữa prompt. REQ-9JA8I (sách) và REQ-0K5HV (bình tưới) cắt người phụ ở mép khung, không đạt yêu cầu mới toàn bộ hai người trong khung; REQ-XZKV9 (bút) chỉ có nửa người trên bàn, chưa đạt yêu cầu toàn thân. REQ-9CGSH (ô) đạt kiểm tra sơ bộ về bố cục và mascot. Không tuyên bố 4/4 chất lượng đạt.

Nhật ký local chặn chạy lại cùng batch, giữ submitting trước Start Queue, lưu mediaId và raw output khi polling quan sát được. Nếu queue biến mất thì dừng unknown. Đây là bảo vệ bổ sung, chưa thay cho nghiệm thu crash/reload end-to-end và chưa có tính nguyên tử với Flow. Chưa tích hợp sản xuất, chưa đổi mặc định.

## Đợt vocab-4-v3

Chạy 4 yêu cầu đồng thời ở mức cao nhất UI hiện có, Nano Banana Pro: đủ bốn ảnh trong 29,239 giây (7,310 giây/ảnh trả về). Timestamp submit chênh nhau 0,4 ms trong tool, xác nhận dispatch đồng thời chứ không chạy tuần tự. Đã lưu 4 JPEG và mediaId riêng, nhật ký local vocab-4-v3-events.ndjson. Đã xem cả bốn: mascot có miệng/lưỡi đúng hơn; cảnh bút vẫn cắt người phụ, cảnh ô chưa thể hiện rõ hành động nhận ô. Không tính toàn bộ ảnh đạt nội dung. Không khẳng định đây là tốc độ cao nhất có thể của dịch vụ, chỉ là concurrency cao nhất hiện cấu hình (4).
