# Kế hoạch sắp xếp và dọn dẹp dự án

> Kế hoạch ban đầu đã được thay thế bởi yêu cầu gom hệ thống vào `sys/` và video vào `video/`. Xem [kết quả thực hiện](layout-migration.md). Nội dung bên dưới được giữ để tra cứu quyết định ban đầu, không phải cấu trúc đang áp dụng.

Ngày khảo sát: 22/09/2026. Nhánh thực hiện: `master`, mốc `51208e9`.
Không có nhánh `main` trong danh sách nhánh local hoặc remote hiện có.
Đây là kế hoạch; chưa xóa dữ liệu, di chuyển mã nguồn hoặc thay đổi luồng sản xuất.

## 1. Kết quả khảo sát

Dung lượng xấp xỉ trong workspace dùng chung giữa các nhánh, không phải dung lượng mã nguồn riêng của master:

| Nhóm | Dung lượng | Kết luận ban đầu |
| --- | ---: | --- |
| `.gflow/` | 3,2 GB | Hồ sơ trình duyệt và cache; không xóa toàn thư mục |
| `runs/` | 1,8 GB | Lịch sử và dữ liệu job; giữ nguyên |
| `.venv-en/`, `.venv-tts/`, `.venv/` | 1,9 GB | Ba môi trường có nhiệm vụ riêng, không phải bản trùng |
| `node_modules/` | 437 MB | Phụ thuộc dựng video và Flow đang dùng |
| `exports/` | 365 MB | Thành phẩm; giữ nguyên |
| `scratch/` | 190 MB | Lẫn dữ liệu dựng lại, kiểm thử và bằng chứng thật |
| `experiments/` | 120 MB | Có B-2 đang được pipeline sử dụng |
| `.claude/` | 4,8 MB | Có bốn Git worktree đã đăng ký; không xóa trực tiếp |
| `reports/` | 604 KB | Báo cáo lịch sử; không coi là rác |

Tổng workspace lúc khảo sát khoảng 7,9 GB. Không lấy con số này làm mục tiêu dung lượng cần xóa.

Các phụ thuộc đã xác nhận:

- `adapters.py` gọi `b2_bridge.py`; bridge sử dụng socket và đầu ra dưới `experiments/b2_illustrator/results/controller/`.
- `examples/content.json`, `examples/m1/` và `examples/story-v3/` còn được mã nguồn hoặc tests tham chiếu. Schema v2 vẫn được adapter chọn theo phiên bản.
- `docs/b2-illustrator-assessment.md` tham chiếu ảnh trong `scratch/` và `experiments/`; tên thư mục tạm không chứng minh file vô dụng.
- Sau khi chuyển nhánh, `research/` còn cache và `evidence/`, `vocab/` còn cache. Đây là dữ liệu local tồn tại qua các nhánh; không xóa chỉ vì master không theo dõi.
- Các đường dẫn trong scripts được tính từ vị trí file; việc chuyển thư mục phải cập nhật đồng bộ cách xác định gốc dự án, import và lệnh gọi.

## 2. Cấu trúc đích đề xuất

```text
pipelineFlow/
  pilot.py                    # Giữ lệnh vào hiện tại
  video_pilot/                # Mã Python dùng chung, chuyển từng bước
  renderer/                  # Dựng video
  integrations/b2_illustrator/ # Mã B-2 đang dùng, tách khỏi nhãn experiments
  scripts/
    maintenance/             # Dọn dữ liệu, hiệu chỉnh, công cụ dựng lại
    rehearsal/               # Bộ chạy thử cô lập
  docs/
    workflow.md              # Giữ đường dẫn hướng dẫn chính
    ...                      # Tài liệu vận hành hiện tại
    architecture/            # Sơ đồ mã, phụ thuộc và vòng đời dữ liệu
  reports/                   # Lịch sử, có mục lục
  experiments/               # Chỉ phần thử nghiệm thật sự độc lập
  assets/                    # Giữ nguyên mascot chuẩn và tài nguyên
  schemas/
  examples/
  tests/
  runs/                      # Giữ nguyên vị trí dữ liệu job
  exports/                   # Giữ nguyên vị trí thành phẩm
  scratch/                   # Đầu ra tạm mới phải có chủ sở hữu/mục đích
  .state/                    # Giữ nguyên SQLite và trạng thái
  .gflow/                    # Giữ nguyên hồ sơ đăng nhập
```

Giữ `AGENTS.md`, `GEMINI.md`, `.agents/`, cấu hình và manifest/lockfile ở vị trí hiện hành. Không chuyển `prompt_templates.py` trong đợt đầu, không sửa nội dung mẫu prompt. Không gom ba môi trường Python vì khác phiên bản và phụ thuộc TTS.

## 3. Thứ tự thực hiện

### Đợt 1 — Lập danh mục và chuẩn bị hoàn tác

1. Ghi mốc Git, trạng thái các worktree và các tiến trình đang dùng Flow/TTS/render.
2. Lập danh sách từng ứng viên với đường dẫn, dung lượng, nguồn tạo, nơi tham chiếu, job liên quan và lý do giữ/xóa. File không có tham chiếu tìm thấy chưa đủ để kết luận không dùng.
3. Tách danh sách thành: cache tái tạo được; mã/tài liệu cần chuyển; dữ liệu cần giữ; chưa đủ bằng chứng.
4. Sao lưu dữ liệu local trước mọi xóa thật. Git không khôi phục được file bị ignore. Bản sao hoặc vùng cách ly phải nằm ngoài phạm vi script dọn và có danh mục checksum.

### Đợt 2 — Dọn cache có phạm vi rõ

- Ứng viên ưu tiên: `__pycache__`, `.pytest_cache`, thư mục tạm rỗng đã xác định không có tiến trình dùng.
- Cache trình duyệt: chỉ lập whitelist theo đường dẫn thực tế sau khi kiểm tra profile đang hoạt động; không chạm cookies, sessions, credentials, dữ liệu tài khoản hoặc model TTS.
- `.claude/worktrees`: kiểm tra thay đổi chưa commit và công việc liên quan từng worktree; chỉ gỡ bằng thao tác Git khi đã kết thúc, không xóa trọn `.claude/`.
- Chưa có cơ sở đưa bất kỳ job hoặc cả profile trình duyệt nào vào danh sách xóa.

### Đợt 3 — Sắp xếp tài liệu và công cụ

- Thêm mục lục tài liệu theo vận hành, kiến trúc, thử nghiệm và lịch sử; giữ các báo cáo đã lưu.
- Chuyển `rehearse_content.py`, `rehearse_flow.py`, `rehearse_report.py` vào `scripts/rehearsal/`, cập nhật import/lệnh/tài liệu và giữ điểm gọi tương thích nếu còn người dùng.
- Chuyển công cụ bảo trì vào `scripts/maintenance/` sau khi kiểm tra cách tính ROOT và các nơi gọi. Đánh giá riêng `rerender_16x9.py` vì có đường dẫn scratch mặc định phục vụ trường hợp cụ thể.
- Không xóa examples/schema v2 hoặc tests chỉ vì tên cũ; cần kế hoạch bỏ hỗ trợ riêng nếu muốn loại bỏ.

### Đợt 4 — Gom mã dùng chung

- Đưa dần `workflow.py`, `content_contract.py`, `machine_review.py`, `adapters.py`, `image_pipeline.py`, `tts_worker.py` vào package `video_pilot/` theo phụ thuộc; giữ CLI `python3 pilot.py`.
- Mỗi nhóm chuyển phải cập nhật imports, subprocess, ROOT, test fixtures và tài liệu, rồi kiểm tra trước khi chuyển nhóm tiếp theo.
- Chuyển mã B-2 đang hoạt động sang `integrations/b2_illustrator/`. Không di chuyển journal, ảnh bằng chứng và session socket đang dùng cùng lúc; giữ đường dẫn dữ liệu cũ qua cấu hình tương thích cho đến khi có kế hoạch chuyển riêng.
- `master` chỉ nhận thay đổi nền chung. Không đưa toàn bộ nội dung riêng của nhánh nghiên cứu hoặc từ vựng vào master.

### Đợt 5 — Chỉ xóa phần thừa đã chứng minh

- Chốt danh sách file cụ thể từ danh mục, kiểm tra không còn phụ thuộc hoặc tác vụ sử dụng.
- Mã thừa được xóa bằng thay đổi Git riêng có thể hoàn tác. Dữ liệu local qua vùng cách ly và kiểm tra khôi phục trước khi xóa vĩnh viễn.
- Không sửa hoặc xóa revisions, reviews, báo cáo máy, integrity baseline hay lịch sử job trong đợt tái cấu trúc này.
- Đo dung lượng thực tế sau dọn, không cam kết trước số GB chưa xác minh.

## 4. Công cụ dọn hiện tại cần rà soát trước khi dùng thật

Đã chạy `python3 scripts/clean_production.py --periodic --dry-run`: kết quả **0 B**. Tất cả 15 thư mục job đều bị bỏ qua vì không có exports hoặc trạng thái render chưa approved. Đây không phải bằng chứng mọi job đã được kiểm tra chất lượng.

Các vấn đề thấy trực tiếp trong mã:

1. Nhánh scratch xóa cả thư mục có tên bắt đầu bằng `tmp` hoặc `render_output`, không kiểm tra đệ quy nội dung bảo vệ hoặc tuổi thư mục trước khi xóa.
2. PNG/JPG cũ có thể bị chọn theo tuổi và tên; bằng chứng giao diện thật không nhất thiết có chữ `evidence` trong tên.
3. Quyết định dọn job dựa vào module `render`, cần đối chiếu thêm quyết định phần `video` của workflow v3 và toàn bộ lịch sử revision đã duyệt trước khi cho phép tỉa.
4. Phạm vi tìm cache chỉ bao phủ một số cấp thư mục dưới `.gflow/profiles`; chưa thể suy ra phần lớn 3,2 GB là cache có thể xóa.

Sửa và kiểm thử công cụ này là một thay đổi riêng khi triển khai, không dùng nhãn “an toàn 100%” trong phần mô tả script để thay thế kiểm chứng thực tế.

## 5. Tiêu chí hoàn tất khi triển khai

- CLI và ba phần `content → media → video` giữ nguyên hành vi, không đổi gate hoặc chế độ job.
- Chạy bộ tests hiện có sau thay đổi mã; bổ sung tests có ý nghĩa cho whitelist, symlink, bằng chứng nằm trong thư mục tmp và lịch sử duyệt nếu sửa công cụ dọn.
- Kiểm tra import, lệnh công cụ, liên kết tài liệu và dựng thử bằng fixture cô lập; không tạo ảnh Flow hoặc gọi API trả phí để kiểm tra sắp xếp thư mục.
- Danh mục trước/sau chứng minh không mất dữ liệu được bảo vệ; có đường khôi phục mã và dữ liệu local.
- Chuyển cải tiến dùng chung sang các nhánh kênh theo commit riêng, kiểm tra tương thích trước khi tiếp tục sản xuất.

## 6. Kiểm tra đã thực hiện trong lượt lập kế hoạch

- Đã đọc AGENTS, Rules, workflow và skill vp-clean; không ghi integration-check.
- `doctor` tìm thấy các công cụ nền và hai môi trường TTS; khả năng máy đánh giá media vẫn chưa được xác minh.
- `status` yêu cầu mã job; thử `status stickman-001` trả `LEGACY_JOB`, lịch sử chỉ đọc. Không chạy sản xuất hoặc sửa job để vượt kiểm tra này.
- Chưa chạy tests vì chưa đổi mã nguồn; chỉ thêm tài liệu kế hoạch này.
