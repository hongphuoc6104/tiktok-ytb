# Video Pilot

Bắt đầu tại [INDEX.md](INDEX.md): bản đồ thư mục mới và hướng dẫn cho agent quay lại dự án.

Pipeline chính: **kịch bản → âm thanh và hình ảnh → video hoàn chỉnh**.
Hai chế độ: **review** (bạn duyệt ba mốc) và **auto** (máy đánh giá rồi chuyển bước).
Hướng dẫn duy nhất cho quy trình: [docs/workflow.md](sys/docs/workflow.md). Rules: [AGENTS.md](AGENTS.md).

```bash
python3 pilot.py doctor
python3 pilot.py new video-001 --brief sys/examples/story-v3/brief.json --mode review
python3 pilot.py status video-001
python3 pilot.py next video-001
python3 pilot.py run video-001
```

Không còn duyệt riêng control/images/audio hoặc ba cảnh đầu. run/resume tự tiến đến mốc theo mode. Auto không cần người dùng duyệt từng video, nhưng phải có kiểm tra thật; không đánh giá được thì báo cần xử lý. Hàng đợi dùng `pilot.py batch --queue queue.json`, danh sách job auto đã tạo.

## Nền dùng chung cho nhiều kênh

Nhánh `master` không áp đặt chủ đề hoặc mục tiêu học ngoại ngữ. Mỗi job xác định
chủ đề, đối tượng, mục tiêu, nguồn và yêu cầu riêng trong brief v3.
Giữ nhân vật người que áo xanh chuẩn và cả hai giọng Việt/Anh.
Ngôn ngữ lời đọc không quyết định chủ đề video.

- `master`: nền dùng chung; chỉ nhận cải tiến pipeline áp dụng cho nhiều kênh.
- `video-nghien-cuu`: nội dung giải thích và hướng dẫn nghiên cứu.
- `video-vocabulary`: bản lưu phát triển kênh học tiếng Anh/từ vựng.

Không merge ngược toàn bộ nội dung riêng của kênh vào master; chuyển riêng các
commit cải tiến dùng chung. Xem [docs/channels.md](sys/docs/channels.md).

## Sắp xếp thư mục

- `video/<tên-video>/`: chỉ chứa file MP4 để xem và sử dụng. Video mới được sao chép ra đây sau khi duyệt video hợp lệ; các bản đã xuất từ trước được chuyển nguyên trạng, không suy ra đã được duyệt theo v3.
- `sys/`: mã nguồn, cấu hình, tài liệu, môi trường Python/Node, dữ liệu job, hồ sơ trình duyệt và hồ sơ xuất cũ. `sys/exports/` giữ metadata và liên kết tới các video đã chuyển.
- `.git/`, `.agents/`, `.claude/`: giữ ở gốc để Git, phát hiện skill/Rules và các worktree của trợ lý hoạt động.
- `pilot.py`: điểm chạy tại gốc, chuyển vào bộ điều phối trong `sys/`.

Lệnh vận hành ở trên chạy từ gốc. Các hướng dẫn kỹ thuật trong `sys/docs/` dùng đường dẫn tương đối với `sys/`; hãy `cd sys` trước khi chạy. Cài Node bằng `npm --prefix sys ci` nếu đang ở gốc.

Các job cũ vẫn giữ baseline và lịch sử gốc; không sửa integrity để tiếp tục chạy sau thay đổi mã. Chi tiết chuyển đổi: [báo cáo sắp xếp](sys/docs/layout-migration.md).

## Môi trường

Chạy các lệnh cài môi trường sau khi `cd sys`.

Python điều phối: `uv venv --python 3.12 .venv`, cài requirements.txt; Node: `npm ci`.
Tiếng Việt: `.venv-tts` Python 3.10, tts-requirements.lock; VieNeu v3 Turbo ONNX FP32, Minh Quân Pro.
Tiếng Việt trên GPU (tùy chọn): `.venv-tts-gpu` Python 3.10, tts-gpu-requirements.lock (torch 2.8.0 cu126, chạy được Pascal như Quadro P620). Có môi trường này thì `tts_device: auto` dùng GPU PyTorch FP32, gom `tts_batch_size` cảnh mỗi lượt; thiếu CUDA hoặc hết VRAM thì tự lùi về ONNX/CPU và ghi vào `fallbacks` của tts-result.json. Đo ngày 23/09/2026 (Phạm Tuyên, 98 giây giọng): P620 21,5 giây gồm nạp model, Xeon E3-1240 v3 ONNX 51 giây. Đặt `tts_device: cpu` để giữ ONNX.

```bash
uv venv --python 3.10 .venv-tts-gpu
uv pip sync --python .venv-tts-gpu/bin/python --index-strategy unsafe-best-match tts-gpu-requirements.lock
```

Tiếng Anh: `.venv-en` Python 3.11; Pocket TTS Alba, CPU INT8 attention/FFN, decoder FP32, tốc độ gốc.

```bash
uv venv --python 3.11 .venv-en
uv pip sync --python .venv-en/bin/python --index-strategy unsafe-best-match en-requirements.lock
```

Model tải lần đầu, lần sau dùng cache; không API trả phí. Alba cần ghi công theo [voice-attribution.md](sys/docs/voice-attribution.md).
Máy đích Xeon E3-1241 v3 / 16 GB / P620 2 GB: chưa nghiệm thu hiệu năng thực tế. Render mặc định hai tác vụ, Flow một tác vụ. flow_batch (config.json) mặc định tắt, chưa nghiệm thu với Flow thật. Không tạo video AI.

## Kiểm chứng

`sys/.venv/bin/python -m unittest discover -s sys/tests -v` kiểm tra logic bằng fixture cô lập; không phải nghiệm thu Flow/video thật.
Auto dùng Antigravity đăng nhập tài khoản; chưa mặc định khẳng định công cụ hỗ trợ nghe/xem mọi loại media. Nếu thiếu hỗ trợ, job không được thông qua.
Job cũ và báo cáo reports/ giữ làm lịch sử; không sửa integrity baseline để chạy job cũ theo mã mới.
