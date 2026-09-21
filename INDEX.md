# Bắt đầu tại đây — Video Pilot

Dự án đã chuyển sang cấu trúc `sys/` + `video/` trên nhánh `master` ngày 22/09/2026. Agent quen cấu trúc cũ hãy đọc file này, rồi đọc [AGENTS.md](AGENTS.md) trước khi làm việc.

## Bản đồ thư mục

| Vị trí từ gốc dự án | Nội dung |
| --- | --- |
| `video/<tên-video>/` | Các file MP4 dành cho người dùng; không đặt mã nguồn hoặc metadata ở đây |
| `sys/` | Toàn bộ mã nguồn, cấu hình, phụ thuộc và dữ liệu vận hành |
| `sys/docs/workflow.md` | Quy trình hiện hành: content → media → video |
| `sys/docs/layout-migration.md` | Báo cáo chuyển đổi, kiểm tra và cách hoàn tác |
| `sys/runs/<job>/` | Brief, bản nháp, revision, review, bằng chứng và cache của job |
| `sys/exports/<job>/` | Hồ sơ xuất cũ; MP4 là liên kết tới thư viện video |
| `sys/.state/` | SQLite và trạng thái; không chỉnh trực tiếp |
| `sys/.gflow/` | Hồ sơ trình duyệt; giữ cookies và phiên đăng nhập |
| `sys/assets/characters/channel-mascot/` | Ảnh và cấu hình nhân vật chuẩn |
| `sys/scripts/`, `sys/renderer/` | Công cụ Python/Node và bộ dựng video |
| `sys/tests/`, `sys/examples/`, `sys/schemas/` | Kiểm thử, ví dụ và hợp đồng dữ liệu |
| `sys/experiments/b2_illustrator/` | B-2 vẫn đang được pipeline sử dụng; không phải thư mục rác |
| `sys/reports/` | Báo cáo lịch sử, không phải quyết định duyệt hiện tại |
| `sys/scratch/` | Dữ liệu tạm có thể chứa bằng chứng thật; không xóa hàng loạt |
| `sys/.venv/`, `sys/.venv-tts/`, `sys/.venv-en/` | Môi trường điều phối, giọng Việt và giọng Anh |
| `sys/node_modules/` | Phụ thuộc Node, Remotion và trình duyệt |
| `sys/maintenance/layout-20260922/` | Bản sao mã trước chuyển đổi, checksum, ánh xạ và log; chỉ có local |
| `.agents/`, `AGENTS.md`, `GEMINI.md` | Hướng dẫn agent tại gốc; các tên tương ứng trong sys là liên kết về đây |
| `.git/`, `.claude/` | Git và worktree của công cụ; giữ nguyên vị trí |
| `pilot.py` | Launcher ở gốc; mã điều phối thực ở `sys/pilot.py` |

## Đổi đường dẫn cũ sang mới

| Cũ | Mới |
| --- | --- |
| `docs/...`, `scripts/...`, `tests/...` | `sys/docs/...`, `sys/scripts/...`, `sys/tests/...` |
| `assets/...`, `examples/...`, `schemas/...` | Thêm tiền tố `sys/` |
| `runs/...`, `scratch/...`, `.state/...`, `.gflow/...` | Thêm tiền tố `sys/` |
| `config.json`, `workflow.py`, `adapters.py`, các module khác | `sys/<tên-file>` |
| `package.json`, lockfile và requirements | `sys/<tên-file>` |
| `.venv*/bin/python`, `node_modules/...` | `sys/.venv*/bin/python`, `sys/node_modules/...` |
| `exports/<job>/*.mp4` | Video tại `video/<job>/`; hồ sơ/liên kết cũ tại `sys/exports/<job>/` |

Không sửa các đường dẫn tuyệt đối bên trong báo cáo lịch sử, revision hoặc bằng chứng đã lưu. Khi tra cứu thủ công, ánh xạ `<gốc-cũ>/runs/...` sang `<gốc>/sys/runs/...`. Không tạo lại hàng loạt thư mục cũ tại gốc để chữa lỗi đường dẫn.

## Lệnh chạy

Từ gốc dự án:

```bash
python3 pilot.py doctor
python3 pilot.py status JOB
python3 pilot.py next JOB
python3 pilot.py run JOB
python3 pilot.py resume JOB
sys/.venv/bin/python -m unittest discover -s sys/tests -v
npm --prefix sys ls --depth=0
```

`JOB` là mã job thực tế, không phải tên thư mục video tùy ý. `run`/`resume` tuân thủ gate, chỉ dùng khi nhiệm vụ sản xuất đã được yêu cầu.

Hoặc vào thư mục hệ thống, rồi dùng các lệnh và đường dẫn tương đối trong skill/tài liệu vận hành:

```bash
cd sys
python3 pilot.py doctor
python3 scripts/clean_production.py --periodic --dry-run
```

Các đối số `--brief`, `--evidence`, `--queue` được tính từ thư mục đang chạy. Ví dụ từ gốc dùng `--brief sys/examples/story-v3/brief.json`; từ sys dùng `--brief examples/story-v3/brief.json`.

## Các điểm agent cần nhớ

1. Kiểm tra nhánh và thay đổi chưa commit trước khi làm việc. Các nhánh nội dung khác chưa được chuyển bố cục; không tự checkout nhánh cũ trên dữ liệu local đã chuyển. Dùng checkout riêng khi cần.
2. Đọc [quy trình](sys/docs/workflow.md) và skill phù hợp; trước sản xuất chạy status và next. Không suy ra quyết định duyệt từ file video có sẵn.
3. Job lịch sử giữ nguyên integrity baseline; không sửa để tiếp tục chạy bằng mã mới. Nếu báo LEGACY_JOB, giữ lịch sử chỉ đọc và tạo job mới theo quy trình.
4. Video mới được sao chép ra `video/<job>/` sau đủ ba quyết định duyệt hợp lệ; tên gồm revision và tỷ lệ. Nếu xuất bị gián đoạn sau duyệt, resume có thể thử lại việc xuất mà không ghi lại quyết định.
5. Không xóa runs, reviews, bằng chứng, SQLite, phiên đăng nhập hoặc model chỉ để giảm dung lượng. Công cụ dọn scratch chỉ tự xóa thư mục tạm rỗng đã quá hạn; phần dọn cache trình duyệt và tỉa revision vẫn cần rà soát riêng trước khi chạy thật.
6. Kiểm tra chuyển đổi trước đó: 164 tests Python đạt; 3 lỗi kiểm thử kết nối lại B-2 tồn tại từ trước. Không coi kết quả tests hoặc doctor là nghiệm thu Flow/media thật.

Thư mục gốc chỉ dành cho `video/`, `sys/`, các ngoại lệ công cụ và file hướng dẫn/launcher. Lưu báo cáo kỹ thuật mới vào `sys/`, không để dữ liệu phát sinh rải ở gốc.
