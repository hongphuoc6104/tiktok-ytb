# Sắp xếp hệ thống và video — 22/09/2026

Đã thực hiện trên `master` theo yêu cầu: video ở gốc dự án, mọi thư mục vận hành ở `sys/`, ngoại trừ thư mục bắt buộc cho công cụ.

## Cấu trúc hiện tại

```text
pipelineFlow/
├── video/
│   ├── stickman-001/
│   │   └── stickman-001_final.mp4
│   └── stickman-long-001/
│       ├── stickman-long-001_9x16.mp4
│       └── stickman-long-001_16x9.mp4
├── sys/
│   ├── pilot.py, workflow.py, adapters.py, ...
│   ├── assets/, docs/, examples/, schemas/, scripts/, tests/, renderer/
│   ├── experiments/, reports/, research/, vocab/
│   ├── runs/, exports/, scratch/, .state/, .gflow/
│   ├── .venv/, .venv-tts/, .venv-en/, node_modules/
│   └── maintenance/layout-20260922/
├── .git/       # Git và đăng ký worktree
├── .agents/    # Công cụ tự tìm Rules và skills tại đây
├── .claude/    # Bốn worktree đã đăng ký; không xóa hoặc di chuyển tùy tiện
├── .gitignore
├── AGENTS.md
├── GEMINI.md
├── README.md
└── pilot.py    # Launcher giữ lệnh chạy từ gốc
```

`sys/.agents`, `sys/AGENTS.md` và `sys/GEMINI.md` là liên kết về bản gốc, không phải các bản sao cần đồng bộ. Tài liệu vận hành và skill quy ước các đường dẫn nội bộ tính từ `sys/`.

## Video và dữ liệu

- Chuyển 5 file MP4 trong exports cũ thành 3 video riêng biệt. Hai bản trùng được xác định bằng SHA-256; giảm **181.858.682 byte (~173,43 MiB)**.
- `sys/exports/` giữ nguyên hồ sơ xuất, metadata và ảnh. Các đường dẫn MP4 cũ bên trong thư mục này là liên kết đến `video/`, nên không lưu trùng dung lượng.
- Các video này là bản đã xuất từ trước, không tạo hoặc suy ra quyết định duyệt v3 mới.
- Video mới chỉ được sao chép ra `video/<job>/` sau khi cả ba phần có quyết định duyệt hợp lệ. Tên file gồm revision và tỷ lệ; không xuất thêm bản trùng `video.mp4` khi đã có bản theo tỷ lệ.
- Không ghi đè file khác nội dung tại đích. Nếu xuất bị gián đoạn sau khi duyệt, chạy `resume JOB` để thử lại việc xuất; không cần ghi lại quyết định duyệt.
- Dữ liệu job, revision, reviews, báo cáo máy, SQLite, bằng chứng và hồ sơ trình duyệt được di chuyển nguyên trạng. Đối chiếu **2.747 file** trong danh mục: không có thay đổi nội dung.
- Không cập nhật integrity baseline của job cũ. Các đường dẫn tuyệt đối trong hồ sơ lịch sử được giữ nguyên văn; khi tra cứu thủ công, thay tiền tố gốc cũ bằng `<gốc>/sys/`. Job lịch sử vẫn ở chế độ chỉ đọc.

## Phần đã dọn

- Hai bản MP4 xuất trùng nội dung.
- Cache Python và pytest ở các thư mục mã/công cụ đã kiểm tra, gồm cache cũ trong vocab; thư mục tạm rỗng. Giữ file khóa của kho nội dung trong sys/vocab.
- Đầu ra đóng gói thử và bản giải nén mã để đối chiếu do lượt kiểm tra này tạo ra.
- Không chạy chế độ xóa của `clean_production.py`: các vấn đề bảo vệ bằng chứng đã nêu trong kế hoạch cũ chưa được sửa trong đợt sắp xếp này. Không xóa media nháp, job, bằng chứng hoặc cache trình duyệt.

## Kiểm tra

- **164 kiểm thử Python đạt**, dùng môi trường `sys/.venv` có đủ phụ thuộc âm thanh. Python hệ thống trong lần kiểm tra trước thiếu `soundfile`; không cài thêm hoặc thay đổi thư viện để xử lý.
- 33 kiểm thử Node của B-2: 30 đạt, 3 lỗi về kết nối lại phiên. Chạy trên bản mã trước di chuyển cho cùng 3 lỗi, nên đây là lỗi tồn tại trước đợt sắp xếp; không sửa hành vi Flow trong thay đổi này.
- Remotion bundle thành công từ `sys/renderer/index.tsx`; các phụ thuộc Node được tìm thấy ở `sys/node_modules`.
- Ba MP4 đều được ffprobe đọc thành công, có stream video và audio; không coi kiểm tra kỹ thuật này là duyệt chất lượng.
- Cả ba môi trường Python đã được cập nhật đường dẫn activation/entrypoint; hai gói TTS vẫn được nhận diện. Không tải hoặc tái tạo model.
- `python3 pilot.py doctor` chạy được từ gốc; TTS Việt/Anh đều được tìm thấy. Không kiểm tra tạo ảnh Flow hoặc khẳng định đã nghiệm thu khả năng nghe/xem của máy.
- Các worktree Git giữ nguyên vị trí và đăng ký.

Lệnh kiểm tra từ gốc:

```bash
python3 pilot.py doctor
sys/.venv/bin/python -m unittest discover -s sys/tests -v
npm --prefix sys ls --depth=0
```

Lệnh công cụ chuyên biệt: thêm `sys/` trước đường dẫn script, hoặc `cd sys` rồi dùng lệnh cũ. Ví dụ `python3 sys/scripts/clean_production.py --periodic --dry-run` chỉ xem trước.

## Bản ghi và hoàn tác

`sys/maintenance/layout-20260922/` chứa bản sao mã nguồn trước thay đổi, danh mục checksum, ánh xạ di chuyển, danh sách cache đã xóa và log kiểm tra. Thư mục này không được đưa vào Git. Bản sao mã không phải bản sao toàn bộ video hoặc dữ liệu tài khoản.

Nếu cần hoàn tác, phải dừng các tiến trình đang dùng dự án, lưu thay đổi phát sinh sau đợt chuyển đổi, rồi dùng `migration.json` để đảo việc di chuyển. Với MP4, phục hồi từng tên cũ từ video đích trước khi gỡ liên kết; cập nhật lại đường dẫn môi trường Python. Không chỉ checkout mã cũ rồi chạy vì dữ liệu local vẫn ở `sys/`.

Cập nhật: cả ba nhánh đã được chuyển sang cấu trúc mới, giữ nguyên nội dung riêng từng nhánh. Xem branch-sync.md.


## Bổ sung sau rà soát

- Thêm `INDEX.md` tại gốc, liên kết từ README, AGENTS và GEMINI; `sys/INDEX.md` trỏ về cùng file để tra cứu từ thư mục hệ thống.
- Sửa dọn scratch: chỉ xóa thư mục tạm rỗng quá hạn, không đi qua symlink, giữ toàn bộ file kể cả ảnh cũ và bằng chứng lồng trong tmp. Ba kiểm thử hồi quy mới đạt; bộ kiểm thử clean_production hiện có cũng đạt.
- Launcher chuyển cache bytecode vào `sys/.cache/pycache`; không để module hệ thống sinh cache ở gốc khi chạy CLI.
- Không thực hiện thêm xóa media hoặc cache trình duyệt; không có ứng viên dữ liệu mới được xác minh là thừa.
