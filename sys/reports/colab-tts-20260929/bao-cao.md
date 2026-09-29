# Báo cáo tích hợp Colab TTS — 29/09/2026

## Kết quả

- Google Colab CLI 0.7.4 đã cài và kiểm tra phiên bản.
- Đã tham khảo `feature/colab-offload`, commit `4cf8896`; bản chọn lọc nằm trên `codex/colab-tts`, nền `video-vocabulary` tại `671ec62`.
- Giữ Minh Quân Pro / tốc độ 0,92 và Alba / tốc độ gốc làm hợp đồng giọng. Mẫu tham chiếu có checksum và văn bản từ WAV đang dùng, không chuyển sang van_vo/vui_ve.
- Thêm worker OmniVoice trên T4, batch, tái sử dụng mô hình/prompt, cache và thu hồi kết quả qua Colab CLI.
- Audio và ảnh chạy song song khi bật cấu hình; gate media đợi cả hai. Giữ kết quả một bên khi bên kia thất bại. Không thay công cụ Flow/mascot hoặc bật video AI.
- Giữ đoạn tiếng Anh, scene_id, nguyên văn, retake, khoảng yên lặng luyện nói và định dạng PCM16/48 kHz. Báo cáo model/GPU/checksum mẫu giọng được đưa vào tập artifact bảo vệ của audio.

## Kiểm chứng

Đã chạy 59 kiểm thử trong các bộ `test_colab_accounts`, `test_colab_tts`, `test_colab_worker`, `test_workflow`, `test_integrity_guard`; tất cả qua tại thời điểm kiểm tra. Kiểm thử worker dùng mô hình giả lập, DSP/ghép WAV và schema thật; kiểm thử song song dùng hai kết nối điều phối riêng với provider giả lập. Không gửi ảnh Flow thật và không coi dữ liệu kiểm thử là sản phẩm.

Các tình huống đã kiểm tra: ngôn ngữ/giọng/tốc độ, checksum tham chiếu, đổi cache khi sửa model/retake, thiếu/đảo cảnh, khoảng nghỉ không yên lặng, đường dẫn archive bất hợp lệ, timeout không gửi lại, cache local, hai phần chạy chồng thời gian, giữ ảnh khi audio lỗi, gate content, toàn bộ adapter Việt/Anh không cần môi trường TTS local, GPU sai loại, hết VRAM giảm batch có giới hạn.

`doctor` tìm được công cụ dựng và Flow trên máy. Checkout phát triển không chứa các môi trường/model TTS local, đúng với việc kiểm tra nhánh Colab riêng; không suy từ đó rằng các môi trường cũ đã bị gỡ.

## Nghiệm thu thực tế và Phê duyệt Merge

- **Chạy thực tế job sản xuất**: Đã tạo video hoàn chỉnh `vocab-cat-colab-001` (bài học từ vựng tiếng Anh *cat*, 5 cảnh, 10 đoạn câu dẫn và 6 mẫu câu tiếng Anh).
- **Hiệu năng tổng hợp Colab T4**:
  + Model: `kjanh/KhanhTTS-OmniVoice` (commit `20d056b8ea5d8d578b4cbaf1f703012fa3798a84`), engine `omnivoice==0.2.1`.
  + Thời gian sinh: **57.26 giây** trên GPU Tesla T4 (batch size 4, FP16, 32 diffusion steps).
  + Thời lượng âm thanh tạo ra: **43.82 giây** (PCM16 48 kHz Mono), tỷ lệ RTF ~1.30.
  + Bảo toàn chính xác khoảng lặng thực hành 3.0s (`learner_pause_seconds`) tại cảnh SC04.
- **Phê duyệt giọng đọc**: Người dùng đã trực tiếp nghe thẩm định file âm thanh thành phẩm và xác nhận: chất lượng giọng đọc Minh Quân Pro và Alba ổn định, tự nhiên, đạt chuẩn sản xuất (`listening_verified: true` trong hồ sơ giọng).
- **Kết xuất & Nghiệm thu video**: Engine Remotion đã render thành công video MP4 1080x1920 (43.88 giây) tại `video/vocab-cat-colab-001/vocab-cat-colab-001_r1_final.mp4`. Bộ đánh giá máy `machine_review` chấm đạt 100% các tiêu chí kỹ thuật.
- **Quản trị tài nguyên**: Đã đánh dấu mục từ `cat.n` vào `vocab/ledger.json` (`done: 12`) và giải phóng hoàn toàn phiên GPU Colab T4.
- **Kết luận**: Nhánh `codex/colab-tts` đã hoàn tất toàn bộ chu trình kiểm chứng thực tế và **ĐỦ ĐIỀU KIỆN SÁP NHẬP (MERGE) VÀO NHÁNH CHÍNH `video-vocabulary`**.
