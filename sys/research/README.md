# Kho đề tài nghiên cứu — đọc theo nhu cầu

Không nạp toàn bộ kho vào prompt. Rules/skills chỉ trỏ đến tài liệu này.
- `topics/`: 40 file, mỗi file 25 đề tài; dữ liệu máy đọc.
- `catalog/topics.txt`: bản biên tập gốc cho người bảo trì, không phải context sản xuất.
- `TOPICS.md`, `index.html`: danh sách đầy đủ cho người dùng, không bắt buộc agent đọc.
- `FIRST-80.md`: thứ tự khởi động gợi ý, chưa phải lịch đăng.
- `ledger.json`: giữ chỗ/hoàn tất; không sửa tay.
- `catalog/sources.json`: 32 nguồn định hướng đã tra ngày 22/09/2026, không phải fact-check cho từng đề tài.

## Mỗi lượt chỉ đọc một đề tài

```bash
python3 research/bank.py status
python3 research/bank.py next --count 5 --category journals
python3 research/bank.py show TOPIC_ID
python3 research/bank.py reserve research-001 --topic TOPIC_ID
```

`next` chỉ in mã, tiêu đề, nhóm và ưu tiên. `show` trả một đề tài. Chương trình có
thể đọc file local để lọc; nội dung 1.000 mục không đưa vào context của agent.

Tra cứu nguồn cụ thể hỗ trợ đúng đề tài trước khi chuẩn bị brief. Tạo tệp evidence
của riêng job theo cấu trúc dưới đây; các chuỗi mô tả là chỗ phải điền, không phải
bằng chứng thật và không được đưa nguyên mẫu vào sản xuất:

```json
{
  "topic_id": "MÃ ĐỀ TÀI ĐÃ GIỮ CHỖ",
  "checked_on": "YYYY-MM-DD",
  "checked_by": "người/công cụ đã thực sự kiểm tra",
  "verification_note": "đã đọc phần nào, phiên bản nào, giới hạn kiểm chứng",
  "goal": "kết quả cụ thể người xem có được",
  "required_points": ["ý 1", "ý 2", "ý 3"],
  "sources": [{"id":"S01","title":"tên tài liệu thật","reference":"https://đường-dẫn-thật","facts":["dữ kiện thực sự được nguồn hỗ trợ"]}]
}
```

```bash
python3 research/bank.py prepare research-001 --evidence PATH_TO_EVIDENCE
python3 research/bank.py start research-001 --mode review
python3 pilot.py status research-001
python3 pilot.py next research-001
python3 pilot.py run research-001
```

`start` dùng CLI chính, không vượt cổng duyệt. Chính sách kiểm tra mã/giữ chỗ/nguồn
và thời lượng với job `video_type=research-*` hoặc có thẻ research-topic.
Generic job không bị đổi thành nghiên cứu bằng kiểm tra từ khóa. Quy tắc vận hành
nhánh này yêu cầu mọi video mới lấy đề tài qua kho; không đổi video_type để lách kho.

Nguồn hết hạn: AI/tạp chí/chỉ số 14 ngày, phần mềm/truy cập 30 ngày, nhóm khác
180 hoặc 365 ngày. Đây là cửa sổ kiểm tra biên tập, không chứng nhận nội dung còn đúng.
Trước công bố vẫn đối chiếu nguồn hiện hành, nhất là giá, hạn mức, chỉ mục và chính sách.
Không khẳng định cả 1.000 video đã có dữ kiện mới nhất. Không tạo rating uy tín tùy tiện.

## Tránh trùng và hoàn tất

`reserve` dùng khóa file và ghi nguyên tử; cùng job gọi lại trả cùng đề tài.
Job khác không thể chiếm mục reserved/done. Không tự giải phóng khi lỗi tạo job.
`release JOB --note ...` chỉ giải phóng khi chưa tạo job thực.
Sau khi video có đủ quyết định hợp lệ:

```bash
python3 research/bank.py mark research-001
python3 research/bank.py audit
```

`mark` kiểm tra decision hiện tại và video qua pipeline, không tin một file tự ghi
approved=true. Đánh dấu hoàn tất sản xuất không có nghĩa đã đăng YouTube.
Không tự đăng video. `audit` tìm mục đã duyệt nhưng chưa mark; reserved vẫn chặn trùng.
Khóa chỉ bảo vệ các tiến trình trên cùng checkout; không chạy hai máy/checkout sản xuất
cùng một ledger độc lập. Git merge ledger không phải hệ thống đặt chỗ phân tán.

Trùng tiêu đề/ID được chặn khi build; trùng ngữ nghĩa phải rà bằng mục tiêu và phạm vi.
Đổi tên đề tài tạo ID mới: không dùng cách này để làm lại mục đã có; giữ ID và lịch sử
khi xây công cụ biên tập tiếp theo. Không có lệnh redo tự động.

## Hình và thời lượng

Mặc định 6 cảnh lớn, mục tiêu 18–24 hình và 24–36 nhịp; giới hạn cấu trúc 18–36 hình,
24–60 nhịp, ít nhất 2 hình/cảnh. Mỗi hình mới phải mang thay đổi có ý nghĩa.
Có thể chỉnh `channel.json` cho job mới; bản đã tạo giữ ngân sách trong brief.
Không tăng FPS hoặc tự bật sinh song song. Dual cần tạo hình cho cả hai tỷ lệ nên chi phí
và thời gian tăng. Mỗi cảnh giữ nền/người que qua based_on và ảnh tham chiếu chuẩn.

Báo cáo media nêu nhịp chữ ngắn hơn 3 giây dựa trên thời gian nội suy từ WAV;
người/máy phải xem thực, không coi báo cáo là duyệt. Phần mềm được giới thiệu chỉ dùng
hình minh họa khái niệm nếu chưa có ảnh giao diện thật, không bịa vị trí nút để dạy thao tác.

## Bảo trì

`python3 research/build_catalog.py` tạo lại 40 file dữ liệu và các trang tra cứu.
Không sửa trực tiếp file sinh. Nguồn định hướng không tự trở thành dữ kiện kịch bản.
Không đụng job lịch sử/reviews/integrity để thích nghi code mới; tạo job mới.
