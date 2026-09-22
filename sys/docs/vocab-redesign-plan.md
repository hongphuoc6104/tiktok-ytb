# Kế hoạch tinh gọn Video Pilot — nhánh vocabulary

Ngày 22/09/2026. Phạm vi: nhánh video-vocabulary, đối chiếu commit 2326f79. Đã triển khai thay đổi mã và skills trong worktree này; xem báo cáo tại ../reports/vocab-redesign-result.md. Nghiệm thu Flow/media thật còn riêng. Worktree đang dùng: /tmp/vp-shotfix-vocab; giữ nguyên checkout nghiên cứu và dữ liệu chưa commit tại đó.

## Kiến trúc đích

Năm skills: vp-vocab, vp-content, vp-media, vp-video, vp-clean.

- vp-vocab: chọn một nghĩa trong kho, start qua bank.py, điều phối CLI theo status/next, mark sau quyết định video hợp lệ và xác nhận xuất thành công. Giữ review mặc định; auto khi người dùng yêu cầu. Tỷ lệ theo brief/channel và yêu cầu, 9:16 là mặc định của luồng từ vựng.
- vp-content: kịch bản đa nhịp và coverage; hợp nhất vp-humanizer thành references/narration-style.md và ai-tells.md. Adapter phải nạp narration-style đúng lượt viết chi tiết, trước khi đặt anchor/coverage/claims; không nạp tài liệu dài vào mọi lượt.
- vp-media: gộp vp-audio/vp-images; âm thanh trước, đo WAV, sau đó ảnh và nhịp. Chi tiết ở references/audio.md và images.md. Giữ CH01, Base/Character reference, nhật ký và đối chiếu timeout.
- vp-video: đổi từ vp-render; dựng, duyệt và xuất video theo brief; trả đường dẫn thực từ thư viện video, không đoán revision.
- vp-clean: kiểm kê và dọn dữ liệu tạm xác định rõ; chưa tự động xóa media/revisions/profile/model.

Bỏ vp-control sau khi đã chuyển mọi nội dung có giá trị và cập nhật chỗ tham chiếu. AGENTS giữ quy tắc chung, workflow.md giữ quy trình; skills chỉ giữ kiến thức và thao tác riêng. Mã audio/images/render nội bộ vẫn tách theo trách nhiệm kỹ thuật.

## Đợt 1 — Sửa các điểm nền trước hợp nhất

1. Chuẩn hóa hợp đồng artifact B-2: kết quả có đường dẫn ổn định, metadata và media ID; retry/replay không tạo ảnh mới. Nhánh này dùng shutil.move trong adapters.py, khác nhánh nghiên cứu dùng copy: kiểm thử đường journal collected sau di chuyển và khả năng tải lại từ raw output; không bê nguyên kết luận “hai ảnh” sang vocab.
2. Bổ sung integrity cho bridge, session/controller/queue và các dependency sản xuất. Phân định mã/chính sách vocab với bank/ledger là dữ liệu; ghi rõ chính sách snapshot channel cho job. Không thêm ledger động vào baseline, không viết lại baseline lịch sử.
3. Cách ly rerender_16x9.py khỏi vận hành sản xuất; chặn ghi đè video qua exports/symlink nếu vẫn giữ công cụ thủ công.
4. Đồng bộ hợp đồng chọn profile và fixture test-controller, giữ cấu hình riêng theo máy. Kiểm thử lại trên vocab, không lấy số test của nghiên cứu làm nghiệm thu nhánh này.

## Đợt 2 — Hợp nhất skills và sửa hướng dẫn vocab

1. Giữ vp-vocab là điểm vào dành riêng video từ vựng; bỏ trigger “tạo video 9:16” quá rộng và lời hứa tự động 100%.
2. Dùng start/draw/queue hiện có trong vocab/bank.py; một video một nghĩa, không tạo brief tay, không sửa ledger tay. Không dùng luồng reserve/prepare của research.
3. Bỏ ép auto; tôn trọng review/auto đã chọn và mode bất biến của job. Mark chỉ sau quyết định hợp lệ, không sau render đơn thuần; xác nhận xuất video trước báo hoàn tất.
4. Bỏ đường dẫn cứng runs/JOB/revisions/render/1/video.mp4. Lấy đường dẫn thật từ kết quả xuất video/<job>/.
5. Giữ tts_speed=0.92 và xử lý câu ví dụ đang có trên nhánh này; nguyên tắc phát âm áp dụng đúng narration Việt, không thay máy móc tiếng Anh chuẩn trong narration_en. Bố cục cảnh lấy từ brief/channel thay vì áp bốn cảnh cho mọi job.
6. Di chuyển humanizer và cập nhật agy_pipeline.py trong cùng thay đổi; cập nhật AGENTS/GEMINI/Rules/skill links/tests. Không sửa prompt_templates.py chỉ để đổi ngôn ngữ.
7. Đồng bộ ngoại lệ batch thử nghiệm và flow_require_ui_evidence=false; giữ cost_verified=false và trạng thái acceptance chưa đạt. Không tự tắt/bật hoặc đổi mode sản xuất trong đợt tinh gọn.

## Đợt 3 — Công cụ phụ và mã cũ

- Sandbox phải có dependency vocab.policy và dữ liệu thử độc lập phù hợp; không sao chép hoặc dùng ledger sản xuất để giữ chỗ thử.
- Công cụ dọn nhận diện video/ và đủ quyết định v3, brief hiện tại; bảo vệ toàn bộ bằng chứng/lịch sử được giữ. Ban đầu chỉ dry-run, danh sách ứng viên và lý do rõ ràng.
- Đánh dấu legacy cho gflow_guard và các nhánh adapter không brief; chỉ loại bỏ sau kiểm tra toàn bộ nơi gọi và test.
- Giữ experiments/b2_illustrator vì engine chính còn dùng. Đổi vị trí engine, nếu cần, là đợt riêng có cập nhật socket/service/import; không di chuyển cùng đợt gộp skills.
- Chưa tạo /vp-end như lệnh đã có. Nếu bổ sung sau này, xác định hành vi, triển khai và kiểm thử trước; không mặc định xóa cache trình duyệt/model hoặc đóng phiên còn tác vụ.

## Điều kiện nghiệm thu

- Chính xác năm skill đích, không còn tham chiếu đường dẫn cũ trong hướng dẫn đang hoạt động và mã gọi; lịch sử giữ nguyên.
- Nội dung văn phong được nạp đúng một lần vào lượt viết chi tiết; không mất dữ kiện, narration_en hoặc coverage.
- Test hợp đồng ảnh đơn/batch/based_on, replay, timeout và ảnh đã tải nhưng lỗi xử lý không gây gửi trùng.
- Test mode review/auto, chỉ mark sau duyệt, xuất đúng revision/tỷ lệ, không ghi đè video khác.
- Test kho: giữ chỗ một nghĩa, chống trùng, lỗi start, mark; sandbox không đụng ledger thật.
- Dọn thử không chọn revision/bằng chứng/profile/model cần giữ; nhận đúng đầu ra video mới.
- Chạy Python/Node tests của chính nhánh vocab. Nghiệm thu Flow và chất lượng media thật là bước riêng với job mới; kiểm thử không thay thế xem/nghe.

## Giữ nguyên trong đợt này

Kho từ, ledger, job cũ, reviews, revisions, profile và video hiện có. Không đổi baseline để tiếp tục job cũ. Không chạy sản xuất hoặc dọn dữ liệu khi đang chỉ lập kế hoạch.
