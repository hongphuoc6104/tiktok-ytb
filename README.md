# Video Pilot

Pipeline chính: **kịch bản → hình ảnh và âm thanh → video hoàn chỉnh**.
Hai chế độ: **review** (bạn duyệt ba mốc) và **auto** (máy đánh giá rồi chuyển bước).
Hướng dẫn duy nhất cho quy trình: [docs/workflow.md](docs/workflow.md). Rules: [AGENTS.md](AGENTS.md).

```bash
python3 pilot.py doctor
python3 pilot.py new video-001 --brief examples/m1/brief.json --mode review
python3 pilot.py status video-001
python3 pilot.py next video-001
python3 pilot.py run video-001
```

Không còn duyệt riêng control/images/audio hoặc ba cảnh đầu. run/resume tự tiến đến mốc theo mode. Auto không cần người dùng duyệt từng video, nhưng phải có kiểm tra thật; không đánh giá được thì báo cần xử lý. Hàng đợi dùng `pilot.py batch --queue queue.json`, danh sách job auto đã tạo.

## Môi trường

Python điều phối: `uv venv --python 3.12 .venv`, cài requirements.txt; Node: `npm ci`.
Tiếng Việt: `.venv-tts` Python 3.10, tts-requirements.lock; VieNeu v3 Turbo ONNX FP32, Minh Quân Pro.
Tiếng Anh: `.venv-en` Python 3.11; Pocket TTS Alba, CPU INT8 attention/FFN, decoder FP32, tốc độ gốc.

```bash
uv venv --python 3.11 .venv-en
uv pip sync --python .venv-en/bin/python --index-strategy unsafe-best-match en-requirements.lock
```

Model tải lần đầu, lần sau dùng cache; không API trả phí. Alba cần ghi công theo [voice-attribution.md](docs/voice-attribution.md).
Máy đích Xeon E3-1241 v3 / 16 GB / P620 2 GB: chưa nghiệm thu hiệu năng thực tế. Render mặc định hai tác vụ, Flow một tác vụ. Không tạo video AI.

## Kiểm chứng

`python3 -m unittest discover -s tests -v` kiểm tra logic bằng fixture cô lập; không phải nghiệm thu Flow/video thật.
Auto dùng Antigravity đăng nhập tài khoản; chưa mặc định khẳng định công cụ hỗ trợ nghe/xem mọi loại media. Nếu thiếu hỗ trợ, job không được thông qua.
Job cũ và báo cáo reports/ giữ làm lịch sử; không sửa integrity baseline để chạy job cũ theo mã mới.
