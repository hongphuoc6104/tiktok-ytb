# Podcast ngủ — âm thanh và ảnh cố định

Trên nhánh này, yêu cầu **“Tạo video podcast”** hoặc **“Tạo video”** dùng skill `vp-podcast`: chọn chủ đề → viết và duyệt lời văn/chỉ dẫn giọng → tạo âm thanh → ghép ảnh cố định thành MP4.

## Mặc định

- Podcast tiếng Việt, xưng mình–bạn, khoảng 25 phút (cho phép 20–30 phút).
- Giọng `podcas` đã chọn, speed 0.90/pitch 1.0; TTS chỉ trên Colab CLI, không fallback local/API trả phí.
- Ảnh người dùng đã chọn tại `sys/assets/podcast/sleep-default.png`, cấu hình/hash tại `still.json` cùng thư mục. Giữ nhân vật và chữ “Podcast Sleep” đúng ảnh gốc.
- Video YouTube 16:9: H.264/AAC, 1920×1080, 24 fps. Ảnh vuông được đặt nguyên vẹn ở giữa, hai bên nền xanh đậm `#202840`; không cắt, không sinh/chỉnh ảnh bằng AI, không nhạc nền/phụ đề.
- Không còn bước tạo ảnh, prompt ảnh, duyệt ảnh hoặc phụ thuộc Flow trong pipeline podcast. Sau audio là sao chép ảnh đã chọn và ghép video. Bước `image` trong manifest chỉ là bản ghi ảnh cố định để tương thích dữ liệu cũ.
- Không tự đăng YouTube.

## Nội dung và giọng

Kịch bản gồm bốn phần nội bộ nối liền, không đọc tên phần/chào lại. Mỗi đoạn cần có quan sát, chi tiết hoặc chuyển ý hữu ích; tránh sáo rỗng, ẩn dụ gượng, lên lớp và kéo dài bằng lời an ủi lặp lại. Nhịp kể ít tải suy nghĩ, mở đầu êm và lắng dần về cuối.

Chỉ dẫn giọng được lưu riêng, neo vào câu trích duy nhất trong lời đã viết. Nhịp, cách kết câu và nhấn nhẹ là mục tiêu biên tập thể hiện qua lời/dấu câu; không giả định TTS nhận SSML hoặc điều khiển nhấn/nghỉ chính xác. Không đưa tag/chỉ dẫn vào text đọc.

Duyệt lời văn và chỉ dẫn cùng nhau trước TTS. Sau bản đầu, tối đa **ba vòng sửa tổng cho cả tập**, gom cả lỗi độ dài và trùng lặp; đạt sớm thì dừng. Hết vòng vẫn lỗi thì giữ báo cáo, chưa tạo TTS. Bộ đếm không đặt lại khi resume.

Khóa hash lời văn, chỉ dẫn và cấu hình giọng đã duyệt trước TTS. Dùng lại hiệu chỉnh tốc độ nếu cấu hình khớp. Checkpoint từng WAV, tiếp tục phần thiếu. **Không nghe duyệt/ASR lại audio và không tạo lại vì phong cách.** Chỉ kiểm tra kỹ thuật phục vụ ghép/xuất. Master lệch thời lượng được giữ thành `.out-of-range.wav`, không kéo/cắt/đọc lại để ép phút.

## Vận hành

AI tự tạo một request ID ổn định cho yêu cầu của người dùng; không bắt người dùng biết lệnh. Từ thư mục `sys/`:

```bash
python3 -m podcast.cli create --auto --request-id <mã-yêu-cầu>
python3 -m podcast.cli create --auto --request-id <mã-yêu-cầu> --topic "Một căn phòng yên tĩnh" --minutes 25
python3 -m podcast.cli status <episode-id>
python3 -m podcast.cli resume <episode-id>
```

Không có đề tài thì chọn từ tối đa năm ứng viên catalog podcast. Giữ cùng request ID khi tiếp tục; yêu cầu tạo tập mới dùng ID mới. `--prepare-only` chỉ tạo hồ sơ. `run`/`resume` có backend mặc định. `doctor` kiểm tra công cụ, ảnh đã chọn và Colab khi chuẩn bị sản xuất.

```bash
python3 -m podcast.cli read <episode-id> script
python3 -m podcast.cli read <episode-id> manifest
python3 -m podcast.cli read <episode-id> events
```

`resume --retry-failed` dành cho lỗi kỹ thuật đã xử lý nguyên nhân; không cấp thêm vòng sửa kịch bản. Lời gọi đang mơ hồ phải đối chiếu kết quả cũ, không gửi lại với ID mới. Nếu phản hồi đã lưu, pipeline dùng lại nó. Nếu chưa có phản hồi, báo lỗi để xử lý phiên tài khoản; không giả thành công.

## File và hoàn tất

`sys/runs/<episode-id>/` lưu brief, revision, phản hồi duyệt, khóa nội dung, WAV, bản sao ảnh và log. `sys/podcast/requests/` ánh xạ yêu cầu sang episode; ledger và khóa ngăn tạo trùng/chạy chồng. Episode mới đòi bằng chứng duyệt nội dung trước TTS và đúng hash ảnh người dùng chọn. Không tự chuyển phiên bản hoặc sửa lịch sử job cũ.

Ghép ảnh với master bằng FFmpeg; kiểm tra codec, stream, kích thước, giải mã và độ dài MP4 khớp WAV trong 0,1 giây. Xuất vào `video/<episode-id>/<episode-id>.mp4`, sau đó đánh dấu hoàn tất/catalog done. Chạy tiếp tập đã hoàn tất không tạo lại media. Trả liên kết MP4, tên tập và thời lượng thật.

## Phạm vi nâng cấp

Theo yêu cầu, nâng cấp chỉ dùng kiểm thử cục bộ, không gọi thử Colab, không tạo video sản xuất. Giả định Colab có lượt/thời gian dùng thử miễn phí (`user_assumed_free_trial`, `cost_verified=false`); không kiểm tra số dư compute units để suy ra khả năng miễn phí. Khi sản xuất về sau, lỗi dịch vụ thật vẫn dừng và giữ tiến độ, không đổi tài khoản để né hạn mức.
