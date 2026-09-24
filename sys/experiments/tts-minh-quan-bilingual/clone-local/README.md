# Clone local từ mẫu Minh Quân Pro V4

Đây là thử nghiệm do người dùng yêu cầu, dùng âm thanh demo làm tham chiếu cho
**VieNeu v3 Turbo ONNX FP32** đang cài. Không tải model V4, không gọi API tổng hợp
trả phí. Chất giọng và độ chính xác phát âm chưa được nghe nghiệm thu.

Nguồn và checksum nằm ở `source.json`; quyền sử dụng không được xác minh độc lập.
Không đăng ký vào preset toàn cục hoặc sửa mặc định của dự án.

Chạy từ gốc dự án:

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/clone-local/run_clone.py
```

`voice-profile.npz` chứa speaker embedding và reference codes để tái sử dụng local.
Nạp bằng `numpy.load(..., allow_pickle=False)` rồi truyền dictionary gồm
`speaker_emb` và `codes` vào tham số `voice` của `tts.infer`.

Trang `index.html` gồm mẫu gốc và ba cặp clone/preset: Việt, Anh, Việt–Anh.
WAV `*-raw.wav` giữ bản tạo gốc; WAV còn lại chỉ điều chỉnh âm lượng, không đổi
cao độ hay tốc độ. Mẫu nguồn V4 giữ nguyên để đối chiếu, có thể khác âm lượng.
Các file mẫu đã tồn tại được giữ lại khi chạy tiếp, không tự tạo lại để chọn bản đẹp.

Không coi file hợp lệ hoặc model chạy thành công là bằng chứng phát âm đạt.
