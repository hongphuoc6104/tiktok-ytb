# Kế hoạch kịch bản đa nhịp

Áp dụng cho job mới, không thay đổi lịch sử hoặc integrity của job đã tồn tại. Ba cổng công khai vẫn là content → media → video. Schema nội dung 3.0 độc lập với phiên bản workflow 3.

## Yêu cầu đầu vào

Brief 3.0 giữ topic/audience/goal/required_points/sources và thêm planning: success_criteria, avoid, prior_knowledge, pacing, domain_requirements, assumptions, text_style, speech_rates. video_type là chuỗi tự do, không khóa chủ đề. Yêu cầu chuyên biệt là dữ liệu của job, không mặc định video dạy tiếng Anh.

Lệnh new tiếp nhận brief 2.0 và chuẩn hóa thành brief 3.0 trước khi lưu; không tự chuyển nội dung lịch sử. Các mặc định được lưu và hiện trong bản duyệt. Tiêu chí ban đầu lấy từ goal; agent cần cụ thể hóa theo yêu cầu người dùng. Sửa brief bằng revise-brief, không sửa file lưu. Đầu ra hỗ trợ 9:16, 16:9, dual; tỷ lệ khác bị từ chối trước sản xuất.

## Luồng content

1. Đọc yêu cầu, làm rõ thiếu sót ảnh hưởng mục tiêu.
2. Lập outline theo cảnh, mục đích, ý bắt buộc và chuyển ý; kiểm tra thứ tự/số cảnh/đủ mã ý.
3. Viết chi tiết theo outline: lời dẫn trước — áp dụng skill vp-humanizer cho văn phong tự nhiên — rồi mới đặt neo/ánh xạ: nhân vật, images, beats, coverage, claims. Không sửa lời dẫn sau khi đã đặt neo (lệch quote/occurrence, hỏng validate_content/validate_plan); nguyên tắc văn phong không bao giờ là cớ bỏ ý bắt buộc hay rút ngắn nội dung.
4. Kiểm tra cấu trúc, nghĩa, nguồn, hai ngôn ngữ, khả năng minh họa và khoảng thời lượng ước tính (tham khảo, không rào duyệt).
5. Xuất một review.md đầy đủ để người duyệt hoặc máy đánh giá. Không thêm cổng duyệt dàn ý.

Adapter lưu outline trước khi viết chi tiết. Nội dung tạo thủ công phải có outline cùng bản nháp. Kiểm tra cấu trúc không thay thế đánh giá nghĩa. Máy kiểm tra tiêu chí mục tiêu/người xem, nguồn, lời dẫn, tương đương Việt/Anh, nhịp hình/chữ, thời lượng và xử lý phản hồi.

## Cảnh, hình và nhịp

- Mỗi cảnh giữ mục đích, lời dẫn, nhân vật; images là danh sách hình, beats là trình tự sử dụng.
- Mỗi hình có id quản lý, description, character_ids, based_on (null hoặc ảnh trước cùng cảnh), preserve, change, reason, visible_text.
- based_on được đính kèm bằng ảnh thật trong cùng tỷ lệ; không coi việc lặp prompt là giữ nền. Bằng chứng UI phải xác nhận ảnh đã được đính kèm; không xác nhận được thì dừng trước gửi.
- Mỗi beat chỉ định image_id, purpose, anchor.vi/en (quote và occurrence), effect và focus.x/y trong khoảng 0–1. Nhịp đầu neo đầu lời dẫn; các nhịp sau tăng dần. Có thể dùng lại một hình nhiều lần.
- Hiệu ứng hỗ trợ: hold, cut, fade, slide_left, zoom_in, zoom_out. Không tự thêm hiệu ứng ngoài danh sách.
- Dual tạo riêng bộ hình 9:16 và 16:9 để giữ bố cục/chữ đúng khung. Số hình thực tế vì vậy có thể gấp đôi số hình logic.
- Vân tay (identity) của một yêu cầu ảnh (image_pipeline.request()) gắn theo target/prompt/edits/tham chiếu của chính ảnh đó, không theo hash toàn bộ kịch bản; sửa một cảnh không làm mất hiệu lực ảnh của cảnh khác.
- Khi tạo hàng loạt, ảnh được gom theo tỷ lệ trước rồi mới theo cảnh (produce() hoàn tất một tỷ lệ mới sang tỷ lệ kế) để không đảo toggle tỷ lệ trên giao diện Flow từng tấm.
- Bản 16:9 được phép mở rộng bối cảnh hai bên khung so với bản 9:16 cùng cảnh nhưng tuyệt đối không được thêm chữ/số/nhãn (prompt_templates.image_prompt).

## Ý bắt buộc và tiếng Anh (coverage)

coverage ánh xạ mỗi ý bắt buộc tới một cảnh và trích dẫn nguyên văn `quote` (Việt) từ narration của đúng cảnh đó. Khi bản có tiếng Anh (16:9 hoặc dual), mỗi mục coverage còn phải có `quote_en` trích nguyên văn từ narration_en của CHÍNH cảnh đó; validate_content (content_contract.py) chặn nếu thiếu quote_en hoặc trích sai cảnh. Bản duyệt (review_plan) hiện bảng hai cột Việt/Anh khi có ít nhất một quote_en.

## Sinh ảnh hàng loạt (flow_batch)

Cờ `flow_batch` trong config.json (mặc định không có, tức tắt) cho phép gom các ảnh gốc độc lập của một nhóm tỷ lệ vào một lệnh `gflow batch` duy nhất trước khi rơi về đường từng ảnh (batch_submit() trong image_pipeline.py); ảnh biến thể (`based_on` khác null) luôn đi đường đơn lẻ vì cần đính kèm ảnh nền và bằng chứng UI riêng. Đây là tính năng chưa được kiểm chứng với Flow thật — chỉ bật sau khi tự kiểm tay, không dùng mặc định cho job sản xuất.

## Chữ trong hình

visible_text là danh sách cho phép chính xác, mỗi mục gồm text, placement, object. Rỗng nghĩa là không có chữ/số. planning.text_style quy định font tham chiếu, color, outline, size, placement chung. Prompt hình chỉ lấy nội dung nhìn thấy, không tuần tự hóa mã quản lý. Mẫu prompt_templates.py giữ nguyên.

Ở media kiểm tra đúng chữ, không chữ thừa/mã nhân vật/logo, tính dễ đọc, màu/kiểu/vị trí, vùng phụ đề và mép hình. Tên font trong prompt là yêu cầu thẩm mỹ, không chứng minh font kết quả đúng. Phụ đề lời đọc cắt một lần ở Python (adapters.subtitle_cues); make_srt và renderer dùng chung danh sách cue đó nên .srt xuất ra luôn khớp đúng chữ trên màn hình — renderer không tự cắt chữ nữa. Bản 16:9 ẩn phụ đề nên layout.json ghi applies:false thay vì kiểm một thứ không tồn tại. Chữ thay đổi phải tạo ảnh biến thể và duyệt cùng media.

## Thời lượng và nhịp

content-v3 không còn trường estimated_seconds trên từng cảnh; content_contract.validate_content chỉ còn gate tổng ước tính (mã ESTIMATE) cho content-v2 lịch sử. Với content-v3, hàm estimates() (scripts/story_plan.py) vẫn in khoảng ước tính vào bản duyệt nhưng chỉ để tham khảo — thời lượng thật do WAV ở bước media quyết định.

speech_rates gồm units_per_second, uncertainty và source riêng vi/en. Đơn vị là nhóm phân cách bởi khoảng trắng (không coi từ tiếng Việt và tiếng Anh có cùng tốc độ). Mặc định là ước lượng ban đầu với sai số, không gắn nhãn số đo. Có thể hiệu chỉnh bằng dữ liệu narration và thời lượng WAV đã kiểm tra, ghi nguồn số đo trong brief mới. Không dùng RTF làm tốc độ lời đọc: RTF là tốc độ tính toán.

Báo cáo dự kiến cộng độ dài lời đọc và khoảng nghỉ dấu câu; cảnh quá nhiều nhịp có cảnh báo. WAV thật vẫn phải đạt khoảng duration của brief. visual-timing.json tại media ánh xạ điểm neo vào các đoạn âm thanh thật, nội suy trong đoạn; tiếng Anh dùng biên cảnh. Đây không phải forced alignment từng từ. Duyệt media cần nghe để đánh giá nhịp trước khi dựng; video còn kiểm tra đồng bộ thực tế.

## Phản hồi và lịch sử

reject content lưu nguyên văn phản hồi. revision_response liên kết request_id, addressed/unresolved, giải thích và scene_ids. Bản nháp không đổi bị chặn. Khi resume gặp bản nháp y nguyên bản bị từ chối, adapter viết lại từ phản hồi và bản trước; bản nháp đã được sửa được kiểm tra và dùng trực tiếp. Không retry vô hạn. Bản duyệt hiển thị cảnh/trường thay đổi, phản hồi và câu hỏi còn lại.

Ví dụ cấu trúc ở examples/story-v3; chỉ là dữ liệu minh họa, không phải chủ đề mặc định hoặc sản phẩm đã duyệt.

Hiệu chỉnh từ job mới đã duyệt media: `python3 scripts/calibrate_speech_rates.py JOB --output /duong-dan-moi/rates.json`. Công cụ chỉ xuất số đo; đưa kết quả vào planning.speech_rates của brief mới hoặc revise-brief. Không sửa brief/revision đã lưu và không giả số đo khi chưa có mẫu thật.
