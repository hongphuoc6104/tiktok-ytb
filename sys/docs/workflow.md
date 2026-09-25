# Quy trình v3: ba phần, hai chế độ

Đây là nguồn hướng dẫn sản xuất hiện hành. Các báo cáo trong reports/ là lịch sử kiểm thử, không phải quy trình hoặc dấu duyệt hiện tại.

| Phần | Đầu ra cần xem | Chuyển bước |
|---|---|---|
| content | Kịch bản Việt/Anh, số cảnh, nhân vật, ý bắt buộc, thời lượng ước tính (tham khảo, không rào duyệt) | Người hoặc máy duyệt nội dung |
| media | WAV Việt/Anh (chạy trước), toàn bộ cảnh/ảnh, ảnh nhân vật đã đăng ký, phụ đề, thời lượng thật | Người hoặc máy duyệt chung |
| video | Video hoàn chỉnh cho các tỷ lệ đã yêu cầu | Người hoặc máy duyệt thành phẩm |

Các module control/images/audio/render vẫn là bước kỹ thuật nội bộ. Không còn lệnh duyệt công khai cho control/images/audio/render, không còn điểm duyệt ba cảnh đầu. Ảnh chuẩn được kiểm tra kỹ thuật trước khi làm toàn bộ cảnh; trong review, việc so sánh nhân vật chờ mốc media và được ghi rõ là pending, không giả là đã khớp.

`workflow.STAGES['media']` chạy audio trước images: giọng đọc chạy local, miễn phí, đo được thời lượng thật, nên kịch bản lệch khoảng thời lượng hỏng ở bước audio trước khi tốn credit Flow cho ảnh. Trong `Pilot.gate`, hai module audio và images vẫn độc lập để `flow-login`/`flow-preflight` dùng được bất cứ lúc nào; chỉ thứ tự trên đường sản xuất do STAGES quyết định.

## Chế độ Kiểm tra

```bash
python3 pilot.py new video-001 --brief examples/story-v3/brief.json --mode review
python3 pilot.py status video-001
python3 pilot.py next video-001
python3 pilot.py run video-001
```

Nếu draft/content.json chưa có, adapter Antigravity tài khoản tạo bản nháp. Nếu đã có thì dùng bản nháp đó. Máy kiểm tra kỹ thuật và dừng ở content revision N. Xem đường dẫn review do lệnh trả về. Chỉ sau phản hồi thực tế của người dùng mới gọi:

```bash
python3 pilot.py approve video-001 content --revision 1 --note 'NGUYÊN VĂN PHẢN HỒI THẬT'
python3 pilot.py run video-001
```

Thay số revision bằng giá trị hiện tại; văn bản ví dụ không phải bằng chứng đồng ý. Mốc kế tiếp là media, sau đó video; dùng cùng cú pháp approve với đúng tên phần. Không xin thêm duyệt control, ảnh chuẩn hoặc ba cảnh đầu.

Flow cần phiên đăng nhập và đúng model/tham chiếu. Mặc định flow_require_ui_evidence=false không yêu cầu screenshot trước gửi; chi phí chưa được xác minh. Sau timeout vẫn phải đối chiếu bằng chứng thật; xem M2-FLOW.md. Đây không phải mốc duyệt nội dung bổ sung.

## Chế độ Tự động

```bash
python3 pilot.py new auto-001 --brief examples/story-v3/brief.json --mode auto
python3 pilot.py run auto-001
```

Máy dùng Antigravity qua tài khoản để đánh giá nội dung và artifact, không dùng API key trả phí. Báo cáo được lưu trong machine-reviews/; quyết định ghi actor=machine. Chỉ pass khi mọi tiêu chí bắt buộc đạt và đầy đủ file được xem/nghe. Công cụ không hỗ trợ nghe WAV/xem video phải trả unsupported; không lấy metadata thay thế chất lượng.

Khả năng đánh giá đa phương thức phụ thuộc công cụ của phiên Antigravity; chưa được coi là nghiệm thu hàng loạt chỉ vì các bài test đạt. Không tự hạ tiêu chí khi thiếu khả năng đánh giá. Job thất bại giữ artifact để sửa qua reject; không tự tạo lại ảnh sau timeout.

Chạy hàng đợi hữu hạn chứa mã các job auto đã tạo:

```json
["auto-001", "auto-002"]
```

```bash
python3 pilot.py batch --queue queue.json
```

Các job chạy lần lượt để tránh tranh RAM trên máy 16 GB. Lỗi riêng một job được ghi needs_attention, chuyển job tiếp theo. Lỗi chung đăng nhập/CAPTCHA/hạn mức/preflight dừng hàng đợi. Chạy lại hàng đợi bỏ qua job đã hoàn tất; báo cáo từng lượt nằm trong .state/batch-results/. Không tự chạy nền vô hạn hoặc tự tạo lịch.

## Sửa và tiếp tục

```bash
python3 pilot.py reject video-001 media --revision 1 --scene SC03 --note 'Lý do sửa ảnh'
python3 pilot.py reject video-001 media --revision 1 --character C01 --note 'Lý do sửa nhân vật'
python3 pilot.py reject video-001 media --revision 1 --part audio --note 'Lý do tạo lại âm thanh'
python3 pilot.py reject video-001 media --revision 1 --part audio --scene SC03 --note 'Lý do đọc lại cảnh SC03'
python3 pilot.py reject video-001 content --revision 1 --note 'Lý do sửa lời dẫn'
python3 pilot.py reject video-001 video --revision 1 --note 'Lý do dựng lại'
python3 pilot.py resume video-001
```

Mỗi ví dụ là một lựa chọn riêng, không chạy nối tiếp trên cùng revision. `--part audio` không kèm `--scene` đánh dấu đọc lại toàn bộ; kèm `--scene` chỉ đánh dấu cảnh đó — số lần bị từ chối của từng cảnh nằm trong khoá cache TTS (và seed giọng Anh) để tránh trả lại đúng bản vừa bị chê. Sửa nội dung ở draft/content.json. Thay brief qua revise-brief, không sửa brief đã lưu. Thay ảnh giữ audio hợp lệ; mọi thay đổi media buộc duyệt lại media trước dựng. Không sửa file đã duyệt.

Mode được giữ cố định trong job. Job trước v3 chỉ đọc lịch sử; không tự đổi baseline hoặc biến duyệt cũ thành duyệt v3. Chưa có công cụ chuyển job cũ tự động.

## Kho từ vựng cho kênh học từ

Quy trình sửa đúng từng ảnh, đối chiếu tiến bộ và giới hạn vòng sửa nằm tại [Chống vòng lặp sửa ảnh](image-repair-loops.md). Ưu tiên `--image IMAGE_ID --ratio 9:16`; `--scene` có nghĩa sửa tất cả ảnh trong cảnh. Từ lượt sửa thứ hai của mỗi ảnh cần `--repair-plan`; xem hash và lịch sử bằng `repair-status JOB --image IMAGE_ID`.

Job dạy từ vựng lấy brief từ `vocab/bank.py` thay vì viết tay: mỗi video một nghĩa, ledger
giữ dấu từ đã làm, từ nhiều nghĩa tách thành nhiều mục. Dữ liệu kho (sources, bank.jsonl,
ledger) không nằm trong integrity baseline nên thêm từ không chặn job đang chạy.

Đây không còn là quy ước: `config.brief_policies` trỏ tới `vocab.policy:check`, chạy trong
`Pilot.new` và `revise_brief`. Brief có dấu hiệu dạy từ vựng mà thiếu mã mục kho, mang mã
không có thật, hoặc mang mục đang giữ chỗ cho job khác đều bị từ chối trước khi job ra đời.
Brief không dạy từ vựng không bị ảnh hưởng — bộ điều phối vẫn không gán cứng chủ đề nào,
toàn bộ hiểu biết về từ vựng nằm trong `vocab/policy.py`. Xem [vocabulary.md](vocabulary.md).

## Kịch bản đa nhịp

Job mới dùng brief/content 3.0: cảnh → hình → nhịp, chữ tạo cùng hình theo danh sách cho phép, ước tính riêng Việt/Anh, đối chiếu ý bắt buộc hai ngôn ngữ (quote/quote_en) và phản hồi sửa có đối chiếu. Không gán cứng chủ đề. Xem [story-planning.md](story-planning.md) cho cấu trúc và giới hạn thời điểm nội suy.

## Giọng đọc và đầu ra

Việt: Minh Quân Pro / VieNeu v3 Turbo ONNX FP32. Anh: Alba / Pocket TTS CPU INT8, tốc độ gốc. Bản 9:16 có tiếng Việt/phụ đề; 16:9 có tiếng Anh, timeline riêng và ẩn phụ đề. Dual tạo cả hai. Phụ đề cắt một lần ở Python (adapters.subtitle_cues); .srt và khung hình dùng chung danh sách cue nên luôn khớp nhau. Thời lượng kiểm tra theo brief, không nới bằng config. Tạo video AI bị khóa.

## Dọn dẹp

Không xóa lịch sử, bằng chứng Flow hoặc model đang dùng để làm sạch mã cũ. Script dọn cũ xóa toàn bộ attempts đã được bỏ. Xuất thành phẩm chỉ sau video được duyệt; chưa tự dọn artifact của job.

## Đạo diễn và kiểm tra biên tập

Đọc [director-system.md](director-system.md). Bốn vai trò đạo diễn hỗ trợ ba gate hiện có. Brief mới dùng mục tiêu học và câu chuyện; brief đã lưu không thay đổi. Lượt thực hành có thể khai báo khoảng chờ cuối cảnh qua audio_direction của content-v3. Phụ đề dùng một bộ cue chung cho SRT/MP4, tối đa hai dòng; report kỹ thuật biên tập không thay thế nghe/xem thật. Khi Python mặc định thiếu phụ thuộc, dùng `.venv/bin/python pilot.py ...`.

## Chuyển job đang làm sang auto theo yêu cầu rõ ràng

`set-mode JOB --mode auto --confirm JOB --reason "Yêu cầu thật của người dùng"` chỉ chuyển review → auto trước khi có lượt audio/images/render. Lệnh giữ nguyên workflow.json gốc, brief, nội dung và lịch sử duyệt; lưu biên bản chuyển chế độ và sự kiện đối chiếu. Bản duyệt cũ không còn hiệu lực dưới chế độ mới; resume tạo bản duyệt mới từ artifact content đã có và gọi bộ đánh giá máy. Không ghi quyết định duyệt thay người dùng.

Mã phải được commit và khớp integrity của job. Nếu cần nhận bản mã mới, chỉ người dùng chạy adopt-code như quy trình hiện hành. Không dùng set-mode để giải quyết hạn mức, lỗi model, phiên đăng nhập hay thiếu khả năng xem/nghe. Lệnh không tự tạo media; tiếp tục bằng resume. Đây là đường chuyển được bổ sung theo yêu cầu người dùng ngày 26/09/2026, thay cho việc sửa trực tiếp chế độ cố định trong workflow.json hoặc tạo job trùng nội dung.
