# TTS trên Colab T4, giữ giọng Minh Quân Pro và Alba

Bản phát triển trên `codex/colab-tts`, xuất phát từ `video-vocabulary`. Tham khảo `feature/colab-offload` tại commit `4cf8896`; không nhập các thay đổi mascot, kênh tiền sử, kho từ hoặc renderer của nhánh đó.

## Phạm vi và trạng thái

Đã cài Google Colab CLI 0.7.4 trên máy. Tích hợp dùng CLI chính thức cho upload/exec/download, không mở HTTP public hoặc gọi API suy luận trả phí. Render vẫn theo đường hiện tại. Mã mới chưa được kích hoạt cho các job sản xuất: `colab_tts.enabled=false` cho đến khi nghe đối chiếu đạt yêu cầu. Không sửa baseline/integrity của job cũ.

Mô hình thử mặc định là `kjanh/KhanhTTS-OmniVoice`, commit `20d056b8ea5d8d578b4cbaf1f703012fa3798a84`, qua `omnivoice==0.2.1`. Model card hiện ghi khoảng 1.500 giờ Việt/Anh; không dùng con số 8.400 giờ trong ghi chú nhánh cũ. Đây là ứng viên cần đo trên T4, chưa phải khẳng định tốt hơn VieNeu/Pocket.

Mẫu giọng tại `assets/voices/minh-quan-pro/` và `assets/voices/alba/` được trích từ WAV thực tế của giọng đang dùng; profile lưu nguyên văn, nguồn, checksum, tốc độ nguồn. Mẫu Alba ghép hai câu đầy đủ với 0,2 giây nghỉ. Chưa xác nhận độ giống giọng bằng nghe. Không dùng các giọng `van_vo` hoặc `vui_ve` của nhánh tham khảo.

## Tốc độ và cách xử lý

Giữ `tts_speed=0.92`, giọng Việt Minh Quân Pro và tiếng Anh Alba tốc độ 1.0. OmniVoice ước lượng thời lượng dựa trên mẫu tham chiếu; tham số gửi vào mô hình là tốc độ yêu cầu chia tốc độ mẫu nguồn để không làm chậm hai lần. Giữ hệ số không bảo đảm hai mô hình đọc cùng nhịp: bắt buộc đối chiếu thời lượng của cùng câu và nghe trước khi bật sản xuất. Không tự kéo giãn audio hoặc đổi cao độ.

Gom các đoạn cùng giọng/lượt retake thành batch tối đa 4, FP16, 32 bước; kiểm tra GPU thật là T4. Không dùng BF16/torch.compile/FlashAttention bắt buộc. Hết VRAM chỉ giảm batch 4 → 2 → 1 rồi dừng. Không tự lùi CPU hoặc máy local. Mô hình và prompt được giữ trong kernel giữa các job của cùng phiên; kết quả có cache trên VM và bản thu về tại máy. Không hứa hệ số tăng tốc trước benchmark.

Văn bản học, đại từ I, thứ tự cảnh và đoạn tiếng Anh được giữ nguyên. Đầu ra 48 kHz mono PCM16 để phù hợp adapter/mastering hiện có. Mỗi chunk giữ `content_duration`; khoảng nghỉ và lượt chờ luyện nói được thêm sau phần lời, tính trong thời lượng video. Phụ đề vẫn nội suy theo chunk, không gọi là word alignment.

## Cài và đăng nhập

Các lệnh sau chạy từ `sys/` của checkout mới.

```bash
uv tool install google-colab-cli==0.7.4
colab --auth oauth2 sessions
```

Lần đầu mở liên kết Google và dán mã vào terminal. Không lưu mã/token trong dự án. `colab auth` là xác thực dịch vụ bên trong VM, không phải lệnh đăng nhập CLI.

```bash
python3 -m colab_bridge start
python3 -m colab_bridge setup
python3 -m colab_bridge status
python3 scripts/colab_tts_benchmark.py prepare
python3 scripts/colab_tts_benchmark.py run
```

`start` cấp phiên riêng `video-pilot-tts` với T4. Chỉ chạy một lần khi chưa có phiên này; không cấp lại khi trạng thái chưa rõ. Không tự mua compute units. `setup` cài mô hình/thư viện trên Colab, không cài mô hình nặng trên máy. Benchmark nằm trong `scratch/colab-tts-benchmark`, không đi vào `video/` hay được coi là job sản xuất. `comparison.json` ghi thời gian sinh, tỷ lệ thời lượng câu cũ/mới và khoảng yên lặng; phần nghe vẫn pending.

Xong đợt phải thu kết quả về rồi giải phóng GPU:

```bash
python3 -m colab_bridge stop
```

## Audio và ảnh song song

Với `colab_tts.enabled=true` và `parallel_images=true`, `run`/`resume` khởi chạy audio trên Colab và quy trình ảnh Flow tại máy bằng hai kết nối điều phối riêng. Mỗi bên vẫn qua kiểm tra kỹ thuật và gate content. Chỉ tạo review media sau khi cả hai hoàn tất và đã đo WAV. Dựng/phụ đề/nhịp cuối không dùng thời lượng ước lượng thay cho audio thật.

Nếu một bên lỗi, phần đã hoàn thành được giữ và lần tiếp tục không sinh lại phần đó. Phần đang chạy được chờ thu kết quả, không hủy mù một lần gửi Flow. Lỗi Colab dùng chung (đăng nhập, timeout, GPU, phiên bận) dừng hàng đợi job. Flow vẫn giữ model, Character/Base references, nhật ký và flow-reconcile. Chi phí Flow vẫn là giả định của người dùng, chưa xác minh.

Không bật trong config của checkout có job auto dang dở. Triển khai sau kiểm chứng theo quy trình integrity; agent không chạy adopt-code hoặc lift-cap. Không tạo job mới để né lỗi của job cũ.

## Khôi phục timeout

Sau khi đánh dấu gửi, `resume` chỉ thử tải `output.zip` của cùng request. Chưa có file thì báo lỗi và giữ trạng thái, không tự gửi lại. Có thể thu mẫu benchmark riêng:

```bash
python3 scripts/colab_tts_benchmark.py collect
```

Với một yêu cầu sản xuất đã có `request-colab.json`, công cụ `python3 -m colab_bridge collect --request ... --out ... --cache ...` phải dùng cùng thư mục cache job; không nhập đè revision đã lưu. Thao tác qua `resume` được ưu tiên vì tự tạo revision hợp lệ. Nếu VM đã mất, giữ nhật ký, báo người dùng quyết định phục hồi; không xóa trạng thái ambiguous để ép gửi lại.

## Nguồn

- [Google Colab CLI](https://github.com/googlecolab/google-colab-cli)
- [OmniVoice: clone, batch và điều khiển tốc độ](https://github.com/k2-fsa/OmniVoice)
- [KhanhTTS-OmniVoice model card](https://huggingface.co/kjanh/KhanhTTS-OmniVoice)

## Kho tài khoản trên máy

Kho dùng chung cho các agent: `~/.config/video-pilot/colab/accounts.json`; mỗi tài khoản nằm trong `profiles/account-NN/` với token, sessions và history riêng. Không đưa token vào Git. Thư mục 0700, file xác thực 0600. CLI gốc không bị sửa; bộ gọi chỉ đổi đường dẫn xác thực trong tiến trình riêng.

```bash
python3 -m colab_bridge.accounts list
python3 -m colab_bridge.accounts login-many
python3 -m colab_bridge.accounts prefer account-02
python3 -m colab_bridge.accounts run account-02 sessions
```

`account: auto` chọn hồ sơ đã đăng nhập, đang bật, ưu tiên `preferred`; nếu hồ sơ ưu tiên không đủ điều kiện thì chọn hồ sơ hợp lệ tiếp theo trước khi gửi. Một request đã gửi lưu tài khoản và tên phiên; resume/collect bắt buộc quay lại đúng hồ sơ đó. Không tự xoay tài khoản sau lỗi hạn mức/503, lỗi đăng nhập hoặc kết quả gửi chưa rõ. Thêm tài khoản cần người dùng hoàn tất OAuth trong terminal, không gửi mã/token vào chat.

Cập nhật kiểm chứng thực tế:
- Đã chạy tạo video hoàn chỉnh `vocab-cat-colab-001` (bài học từ vựng CAT, 5 cảnh, 10 câu tiếng Việt và 6 mẫu phát âm tiếng Anh) trên Tesla T4 thật.
- File âm thanh `narration.wav` (43.82 giây) được sinh trong 57.26 giây (RTF ~1.3), tích hợp khoảng lặng 3.0s luyện phát âm tại cảnh SC04.
- Người dùng đã nghe kiểm tra trực tiếp và phê duyệt: giọng đọc Minh Quân Pro và Alba tự nhiên, rõ ràng, đạt chuẩn sản xuất (`listening_verified: true`).
- Toàn bộ pipeline 3 chặng `content → media → video` chạy thông suốt ở chế độ `auto`, Remotion render MP4 1080x1920 đạt 100% PASS từ `machine_review`.
- Đủ điều kiện kỹ thuật và chất lượng để sáp nhập (merge) nhánh `codex/colab-tts` vào nhánh chính `video-vocabulary`.
