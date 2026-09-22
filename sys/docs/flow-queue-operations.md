# Vận hành tool Flow tạo ảnh đồng thời

Cập nhật 22/09/2026. Đọc INDEX.md, AGENTS.md và docs/M2-FLOW.md trước khi sản xuất.

## Link và cập nhật tool

- Link share lấy từ nút Share → Copy link trên Flow: https://flow.google.com/shared/tool/f9458f79-f068-476c-848d-c407cfa9fbc1
- Bản local đã thử: https://flow.google.com/project/7c815425-4625-4afb-ba84-4290d3fa9ea4/tool/bc72cb6a-c68c-49a3-b089-d94fc27eb8dd
- Bản PC trước đó: https://flow.google.com/project/41d3d574-907c-4bb0-90a7-c98f85f5e22b/tool/2791e8ba-9ae0-4ca9-9368-b7efe600c53d

Pull Git không tự cập nhật bản tool đã remix trong tài khoản Flow khác. Mở link share bằng đúng profile dự án, kiểm tra bản có Initialize Generation (thêm vào hàng đợi), Start Queue, Nano Banana Pro và Workers 1/2/4. Nếu remix tạo URL mới, cập nhật tool_url trong machine.local.json trên máy đó. Không tự đổi tài khoản hoặc profile. Chưa kiểm chứng bản remix cũ tự nhận thay đổi; không mặc định có tự cập nhật.

Link share có thể cho người có link xem/remix tài nguyên trong tool; không đặt thông tin đăng nhập vào tài liệu hoặc tool.

## Cấu hình riêng theo máy

Tạo `sys/experiments/b2_illustrator/machine.local.json` (được Git bỏ qua), gồm `tool_url`, `flow_user_data_dir`, `flow_profile_directory`, `executable_path`. Dùng giá trị thực đã xác minh của máy; không sao chép đường dẫn home/profile từ PC sang laptop. File này được controller ưu tiên hơn browser-profiles.json. Không mở IAB hoặc kết nối bằng extension khác.

Giữ dịch vụ Persistent Session đang chạy; kiểm tra `node experiments/b2_illustrator/session.mjs status` từ sys. Không khởi động lại chỉ để pull mã. Controller/session thay đổi chỉ có hiệu lực đầy đủ trong phiên mới được xác minh; không ép đóng phiên đang có tác vụ. Browser operations được nạp động, queue-runner được cache trong phiên: sau chỉnh queue-runner cần nghiệm thu trong phiên mới trước sản xuất.

## Tích hợp và trạng thái

`queue-runner.mjs` điều khiển biểu mẫu tuần tự để chụp từng đầu vào riêng, sau đó Start Queue cho tối đa bốn yêu cầu. Mỗi yêu cầu sinh một ảnh. Ba ảnh dùng hai workers vì UI hiện không có mức ba. Đây không phải native x4 hoặc cam kết tăng tốc bốn lần.

`b2_bridge.generate_b2_batch` và adapter batch đã nối hàng đợi. Chỉ ảnh độc lập được đưa vào batch; based_on vẫn đi theo đường đơn và cần base media ID thật. Metadata forgeId đi theo ảnh để truy lại tham chiếu. Không coi hoàn tất kỹ thuật là đã duyệt ảnh cha.

**Mặc định bật thử nghiệm trên PC theo yêu cầu người dùng:** config.json đặt flow_batch=true và flow_queue_trial_enabled=true. Pipeline gom tối đa 4 ảnh độc lập mỗi nhóm. Bridge cho phép chạy theo ngoại lệ thử nghiệm này; acceptance.json vẫn production_ready=false vì chưa nghiệm thu đầy đủ. Không sửa hồ sơ nghiệm thu thành đạt. Còn phải nghiệm thu chuỗi phụ thuộc/đăng ký mascot, chữ hiển thị, lỗi thực tế và so sánh chất lượng ba lượt. Adapter cũ tạo ảnh trắng làm screenshot đã được bỏ; thiếu screenshot thật sẽ dừng. Nhánh đăng ký mascot cũ dùng ảnh local chưa có bằng chứng Flow phù hợp nên sẽ dừng, cần sửa hợp đồng đăng ký trước nghiệm thu toàn pipeline.

Job borrow local hiện bị integrity gate chặn sau thay đổi mã. Giữ lịch sử; tạo job mới qua vocab/bank.py theo đúng chính sách giữ chỗ khi tiếp tục, không sửa baseline để chạy tiếp.

## Nhật ký và phục hồi

Nguồn trạng thái nằm ở `experiments/b2_illustrator/results/controller/production-attempts/*.ndjson`, không phụ thuộc localStorage của Flow. Nhật ký ghi submitting trước Start Queue; media ID và raw output được fsync khi controller quan sát kết quả. Có khoảng trễ polling; mất phiên trong khoảng này vẫn là unknown cần đối chiếu.

- Collected: dùng lại ảnh đã lưu, không gửi lại.
- Generated: mã mới có đường ghi lại file từ raw output, không tạo ảnh lại; cần nghiệm thu tải lỗi thực tế.
- Submitting/unknown hoặc nhóm chỉ hoàn tất một phần: dừng, đối chiếu UI và media ID. Không đổi ID/prompt để né trạng thái cũ.
- Không xóa nhật ký, không xóa localStorage, không tự reset UNKNOWN.
- Dùng flow-reconcile cho journal pipeline kèm bằng chứng thật; journal controller còn cần đối chiếu có kiểm soát qua AttemptStore. Chưa có lệnh tự động giải quyết đồng thời hai journal, không chỉnh JSON để giả đã hoàn tất.

Các ảnh, snapshot và dữ liệu raw chỉ lưu local; không commit. Không nhận dữ liệu test là media sản xuất.

## Bằng chứng đợt tích hợp

4 yêu cầu chạy thật qua adapter mới trả 4 JPEG 768×1376, khoảng 29,13 giây đến tải/kiểm tra đủ ảnh. Chạy lại cùng manifest trả cùng 4 media ID từ nhật ký, không gửi thêm. Ảnh đã xem: cảnh ô chưa rõ hành động nhận; nền và bố cục chưa đồng nhất. Không công bố 4/4 chất lượng đạt, không suy chi phí 0.

Bằng chứng local: `sys/maintenance/production-sync-20260922/queue-live/`. Kiểm thử session/AttemptStore/đầu vào queue: 21 đạt; kiểm thử audio sau đồng bộ PC: 29 đạt. Đây chưa phải nghiệm thu reload giữa lúc chạy hoặc đo ba lượt baseline/best.


## Bàn giao cho agent PC — mặc định đã bật thử nghiệm

1. Giữ thay đổi chưa commit trên PC trước khi cập nhật nhánh video-vocabulary; không reset --hard. Pull/merge mã mới và giữ cấu hình/profile riêng của PC.
2. Mở link share ở trên bằng profile PC đã xác minh; dùng bản queue mới hoặc remix vào project PC. Cập nhật tool_url trong machine.local.json theo URL tool thực tế; pull Git không thay bản Flow cũ.
3. Kiểm tra status dịch vụ. Nếu đang có tác vụ, chờ đối chiếu xong trước khi khởi động phiên mới để nạp queue-runner mới. Không xóa nhật ký hay đổi profile để né lỗi.
4. Tạo job thử mới qua kho vocab; không sửa integrity baseline của job cũ. Chạy theo content → media → video, giữ các mốc duyệt. Bật batch không tự duyệt content/media/video hay bỏ kiểm tra chi phí.
5. Ảnh độc lập chạy tối đa 4 cùng lúc; based_on vẫn chạy theo phụ thuộc. Những lỗi chữ/đăng ký mascot/thiếu media ID hoặc bằng chứng thật còn lại phải sửa và báo rõ, không giả bằng chứng để vượt.
6. Tắt thử nghiệm: đặt flow_batch=false và flow_queue_trial_enabled=false. Giữ toàn bộ nhật ký để đối chiếu.

Đây là cho phép thử tích hợp trên PC, không phải xác nhận đã nghiệm thu hoặc cho phép chi tiêu sản xuất không giới hạn.
