# Pipeline podcast — phạm vi cuối cùng

Cập nhật theo yêu cầu cuối của người dùng: bỏ và xóa tạo/duyệt ảnh; dùng ảnh đã chọn, xong âm thanh thì ghép video. Không chạy thử dịch vụ hoặc tạo tập sản xuất trong lượt nâng cấp.

## Luồng hiện hành

Yêu cầu “tạo video podcast” → request ID ổn định → đề tài tự chọn hoặc người dùng cung cấp → brief → lời văn và chỉ dẫn giọng → duyệt/sửa tối đa ba vòng tổng → khóa nội dung → Colab CLI tạo WAV có checkpoint → ghép master → dùng `assets/podcast/sleep-default.png` → MP4 16:9 → hoàn tất.

Ảnh nguồn vuông 2048×2048 được giữ nguyên cả nhân vật và chữ, đặt giữa 1920×1080 với nền xanh đậm hai bên. Không dùng Flow, không tạo thêm ảnh, không có cổng duyệt ảnh. Không nghe/ASR hậu kiểm audio; chỉ kiểm tra file và ghép/xuất kỹ thuật. Không tự đăng YouTube.

## Đối chiếu triển khai

| Yêu cầu | Mã/hồ sơ thực hiện | Kiểm chứng cục bộ |
|---|---|---|
| Một yêu cầu, mặc định/chủ đề/thời lượng | skill vp-podcast, cli.py, request.py | Request ID lặp không tạo tập trùng; chủ đề được reserve một lần |
| Viết tự nhiên, có nghĩa, nghe ngủ | writer.py, content_review.py | Schema bắt buộc giọng; reviewer trích bằng chứng thật |
| Chỉ dẫn giọng tách khỏi lời | direction.py | Neo khớp duy nhất; đổi direction/engine đổi hash |
| Tối đa ba vòng sửa toàn tập | content_pipeline.py | Nhiều phần lỗi vẫn ba vòng; resume không reset; đạt sớm dùng lại |
| Lưu phản hồi, chống gửi trùng | account.py | Dùng lại kết quả; timeout không gửi lần hai; đầu vào thay đổi bị chặn |
| Duyệt trước TTS | coordinator.py, backend.py | set-script chưa duyệt bị từ chối; kiểm tra hash trước TTS |
| Colab có checkpoint, không fallback | tts.py, colab_cli_direct.py, remote_tts_runner.py | Kiểm thử runtime đang sống/mất/thay thế, hash WAV, retry giới hạn |
| Dùng lại hiệu chỉnh | tts.py, backend.py | Cache không gọi transport, thay pitch mất hiệu lực; CLI được truyền đúng |
| Ảnh người dùng chọn | assets/podcast/still.json, still.py | Copy nguyên bytes; giữ hash; thiếu/đổi ảnh báo lỗi, không sinh thay |
| Audio xong ghép MP4 | audio.py, exporter.py | Điều phối offline đến complete; resume không gọi lại stage thành công; đọc mã encode/decode và giới hạn thời lượng |
| Không cắt ảnh vuông | exporter.py | Filter contain + pad, không crop; bản nguồn đã đối chiếu trực quan |
| Không còn tuyến tạo ảnh | backend.py, preflight.py, coordinator.py | Xóa image.py/image_review.py và test cũ; không import Flow/B-2 trong podcast |
| Giao kết quả và tiếp tục lỗi | coordinator.py, skill, README | Manifest lưu artifact; khóa toàn episode; request ổn định |

## Giới hạn kiểm chứng

Nâng cấp được kiểm tra bằng unit/integration tests offline, không gọi TTS/Flow, không tạo MP4 sản xuất. Không chứng nhận trạng thái đăng nhập, hạn mức, chất lượng giọng thực hoặc thời gian chạy dịch vụ. Colab dùng giả định miễn phí do người dùng chỉ định (`user_assumed_free_trial`, `cost_verified=false`). Các lỗi dịch vụ khi sản xuất về sau vẫn phải giữ checkpoint và báo đúng.

Hướng dẫn vận hành: [README podcast](../podcast/README.md). Không dùng các yêu cầu tạo ảnh hoặc chạy thử thật trong kế hoạch cũ nữa.
