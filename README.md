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

## Kho từ vựng

Kênh học từ vựng lấy từ ra từ `vocab/`: mỗi video là một nghĩa của một từ, từ đã làm được
đánh dấu để không lặp lại, từ nhiều nghĩa tách thành nhiều mục riêng. Đây là đường bắt
buộc, không phải quy ước: `config.brief_policies` chặn brief từ vựng không sinh từ kho ngay
trong `pilot.py new`. Hướng dẫn: [docs/vocabulary.md](sys/docs/vocabulary.md).

```bash
cd sys
python3 vocab/bank.py status
python3 vocab/bank.py next --count 10 --topic food-drink
python3 vocab/bank.py start vocab-010 --mode review
python3 vocab/bank.py mark vocab-010 --note 'Đã xuất bản'
python3 vocab/bank.py queue --count 5 --mode auto   # rồi pilot.py batch --queue vocab/queue.json
python3 vocab/bank.py audit                        # job nào làm ngoài kho, job nào quên mark
```
- `master`: nền dùng chung; chỉ nhận cải tiến pipeline áp dụng cho nhiều kênh.
- `video-nghien-cuu`: nội dung giải thích và hướng dẫn nghiên cứu.
- `video-vocabulary`: bản lưu phát triển kênh học tiếng Anh/từ vựng.

Không merge ngược toàn bộ nội dung riêng của kênh vào master; chuyển riêng các
commit cải tiến dùng chung. Xem [hướng dẫn từ vựng](sys/docs/vocabulary.md).

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
Tiếng Anh: `.venv-en` Python 3.11; Pocket TTS Alba, CPU INT8 attention/FFN, decoder FP32, tốc độ gốc.

```bash
uv venv --python 3.11 .venv-en
uv pip sync --python .venv-en/bin/python --index-strategy unsafe-best-match en-requirements.lock
```

Model tải lần đầu, lần sau dùng cache; không API trả phí. Alba cần ghi công theo [voice-attribution.md](sys/docs/voice-attribution.md).
Máy đích Xeon E3-1241 v3 / 16 GB / P620 2 GB: chưa nghiệm thu hiệu năng thực tế. Render hiện cấu hình bốn tác vụ. Flow cho phép thử queue tối đa bốn ảnh độc lập qua flow_batch/flow_queue_trial_enabled; acceptance chưa đạt sản xuất. Không tạo video AI.

## Kiểm chứng

`sys/.venv/bin/python -m unittest discover -s sys/tests -v` kiểm tra logic bằng fixture cô lập; không phải nghiệm thu Flow/video thật.
Auto dùng Antigravity đăng nhập tài khoản; chưa mặc định khẳng định công cụ hỗ trợ nghe/xem mọi loại media. Nếu thiếu hỗ trợ, job không được thông qua.
Job cũ và báo cáo reports/ giữ làm lịch sử; không sửa integrity baseline để chạy job cũ theo mã mới.
