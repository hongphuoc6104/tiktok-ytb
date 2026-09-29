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

## Phần chưa hoàn thành

Đã lưu 5 hồ sơ tài khoản riêng trên máy và xác nhận cả 5 kết nối Colab thành công. Token nằm ngoài repository, không được đưa vào commit.

Đã chạy mẫu Việt/Anh trên Tesla T4 thật qua CLI và thu WAV thành công. Lượt đầu mất 45,61 giây trong worker, gồm nạp mô hình và tổng hợp; chưa phải thông lượng steady-state. Mẫu Việt: câu cũ 3,98 giây, câu mới 3,77 giây (ngắn hơn khoảng 5,3%). Mẫu Anh: cũ 3,40 giây, mới 3,60 giây (dài hơn khoảng 5,9%). Cả hai giữ đủ 2 giây khoảng yên lặng. Chưa nghe đánh giá nhận diện giọng/phát âm, chưa xác nhận hay hơn và chưa so sánh tốc độ sinh với local trên cùng đầu vào.

Mẫu A/B nằm trong `sys/scratch/colab-tts-benchmark/result/`; số đo đã lưu vào `benchmark-summary.json` cạnh báo cáo này. Cần nghe đối chiếu và đo thêm batch đủ lớn trước khi bật sản xuất.

`colab_tts.enabled` vẫn false. Chuẩn bị commit/push theo yêu cầu người dùng; chưa merge vào nhánh sản xuất. Thư mục dự án gốc vẫn giữ nguyên nhánh `video-vocabulary` và các thay đổi vocab đã có; không sửa job, SQLite, ledger hoặc integrity baseline trong thư mục đó.
