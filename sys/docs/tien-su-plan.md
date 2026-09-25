# Kế hoạch kênh giải thích đời sống tiền sử (nhánh `video-tien-su`)

Ngày lập: 25/09/2026. Nhánh tách từ `video-vocabulary` (e6080b1), kế thừa toàn bộ
pipeline content → media → video, Flow, VieNeu, Remotion, auto mode và giới hạn vòng sửa.

## 1. Mục tiêu

Pipeline tự động sinh video dài 16:9 tiếng Việt theo khuôn kênh mẫu Ink Explainer
(96,1 nghìn sub, 15 video, trung vị 315 nghìn view ở 9 video đã hơn 3 tháng):

| Lớp | Khuôn mẫu gốc (đo từ 15 video) | Bản Việt |
|---|---|---|
| Chủ đề | Câu hỏi đời thường về người tiền sử; lệch ngách thì view giảm mạnh | Kho chủ đề riêng, chỉ ngách tiền sử/sinh tồn |
| Tiêu đề | `What/When/Why/How Did Ancient Humans ___?` | "Người tiền sử làm gì khi ___?", góc nhập vai "bạn" |
| Thumbnail | Người que mặt cường điệu + cảnh màu tươi + 2–3 chữ in hoa vàng/trắng viền đen, thường có "?" | Giữ công thức, nhân vật riêng của kênh |
| Kịch bản | Hook "bạn" hiện đại ↔ 50.000 năm trước → phá niềm tin cũ → câu hỏi bí ẩn → 6–8 chương bằng chứng → kết quay lại hình mở đầu | Như gốc, tự nghiên cứu, nguồn thật |
| Hình trong video | Doodle người que trên nền kem, vật có nhãn, bản đồ, sơ đồ khối; đổi hình ~4–6 giây | Như gốc; nhãn chữ do Remotion vẽ |
| Nhịp | 190–245 từ/phút tiếng Anh, 6–15 phút, ~10 ngày/video | 8–12 phút, ~2.000 tiếng Việt |
| Mô tả | Chapters + danh sách nguồn + sponsor | Chapters từ WAV thật + nguồn |

Không sao chép: không dịch kịch bản, không dùng lại hình, nhân vật hay thumbnail của kênh
mẫu. Chỉ lấy khuôn. Đây cũng là điều kiện kiếm tiền (chính sách nội dung lặp lại/hàng loạt).

## 2. Khoảng cách giữa repo hiện tại và mục tiêu

| Hiện có | Thiếu / phải đổi |
|---|---|
| Short 9:16 30–55 s, 5–6 cảnh | Long-form 480–720 s, 7–9 chương, 80–150 beat |
| 16:9 = tiếng Anh, ẩn phụ đề | Tỷ lệ 16:9 tiếng Việt (giọng Việt, phụ đề tùy chọn) |
| `config.max_seconds` 450 | Cho phép 780 s theo kênh |
| Kho `vocab/` + `vocab.policy` | Kho `tiensu/` (chủ đề, ledger, policy) cùng cơ chế |
| Mascot áo xanh | Mascot người tiền sử riêng (tóc bù, áo da thú) |
| Chữ tạo trong ảnh (`visible_text`) | Nhãn/bản đồ/số do Remotion vẽ để khỏi tạo lại ảnh vì sai chữ |
| Mỗi beat = 1 ảnh Flow | Thư viện ảnh tái sử dụng + ghép lớp để giảm số ảnh mới |
| Không có đóng gói | Thumbnail, tiêu đề, mô tả, chapters, nguồn, tags |
| Máy duyệt xem toàn bộ artifact | Duyệt video dài bằng contact sheet + đoạn audio lấy mẫu |

## 3. Nguyên tắc tiết kiệm quota

Ba nguồn quota: lượt Antigravity (viết/duyệt), ảnh Flow, thời gian máy (TTS/render).

1. **Rẻ trước, đắt sau.** Giữ thứ tự content → audio (local, miễn phí) → ảnh. Thời lượng
   WAV lệch khoảng brief thì dừng trước khi tạo ảnh.
2. **Ngân sách cứng mỗi video:** tối đa 1 outline + 1 draft + 2 lượt sửa content;
   3 lượt máy duyệt; tối đa 40 ảnh Flow mới/video; vượt thì `needs_attention`, không tự nới.
3. **Tái sử dụng ảnh.** Thư viện `assets/library/` gắn tag (tư thế, cảm xúc, bối cảnh, vật);
   planner chọn ảnh có sẵn trước khi xin ảnh mới. Video sau càng rẻ hơn video trước.
4. **Chữ không nằm trong ảnh.** Nhãn, bản đồ, con số, tiêu đề chương do Remotion vẽ lên
   ảnh sạch. Sửa chữ = sửa JSON, không tốn ảnh.
5. **Chuyển động bằng Remotion.** Pan/zoom/tách lớp/nhãn bật lên tạo nhịp 4–6 s từ một ảnh
   gốc; mỗi ảnh Flow dùng cho 2–4 beat.
6. **Duyệt máy lấy mẫu.** Content: duyệt văn bản. Media: contact sheet mỗi chương + 3 đoạn
   audio 20 s. Video: contact sheet 1 khung/10 s + loudness/overflow báo cáo máy.
7. **Cache mọi thứ.** Giữ khóa cache TTS theo cảnh và identity ảnh theo yêu cầu; sửa một
   chương không làm lại chương khác.

## 4. Các giai đoạn

Mỗi giai đoạn kết thúc bằng tests đạt + commit riêng. Không chạy Flow thật trước giai đoạn 6.

### GĐ1 — Khung kênh (`tiensu/`)
- `tiensu/channel.json`: 16:9, vi, 480–720 s, 7–9 cảnh, style doodle, tone, avoid,
  domain_requirements theo bảng mục 1, speech_rates vi 3,6 đơn vị/s (hiệu chỉnh sau pilot).
- `tiensu/topics.jsonl` + `ledger.json` + `bank.py` (tái dùng mẫu `vocab/bank.py`):
  `status | next | start | mark | queue | audit`. Nạp sẵn 3 chủ đề thử (mục 5) và ~30 chủ đề.
- `tiensu/policy.py`; `config.brief_policies` trỏ sang `tiensu.policy:check`.
- Gỡ các brief/sources từ vựng khỏi nhánh (giữ ở `video-vocabulary`).

### GĐ2 — Video dài 16:9 tiếng Việt
- Thêm lựa chọn ngôn ngữ cho 16:9 (`brief.voice_language`, mặc định giữ hành vi cũ):
  16:9 dùng WAV Việt, phụ đề bật/tắt theo kênh; không yêu cầu `narration_en`.
- Nâng `max_seconds` theo kênh; kiểm tra TTS theo cảnh dài (chia câu ≤256 ký tự đã có).
- Đo render 10 phút 1920×1080 trên máy đích; nếu > 2× thời lượng thì thêm đường render
  ffmpeg cho cảnh tĩnh + Remotion chỉ cho overlay.

### GĐ3 — Hệ hình ảnh
- Mascot mới `assets/characters/tiensu-mascot/` (tham chiếu + character.json).
- Remotion: lớp nền + lớp nhân vật + overlay (`label`, `map_pin`, `counter`, `chapter_title`,
  `arrow`) khai báo trong beat; hiệu ứng thêm `pan_left/right`, `pop`.
- `assets/library/index.jsonl` + bước planner "reuse-first"; ảnh mới được đăng ký vào thư
  viện sau khi media đạt duyệt.
- Prompt template doodle nền kem, không chữ trong ảnh.

### GĐ4 — Kịch bản
- Skill `vp-explainer` (hoặc references mới trong `vp-content`): cấu trúc 5 phần, giọng
  "bạn", phá niềm tin cũ, mỗi chương một bằng chứng, câu hỏi tương tác, kết callback.
- Bắt buộc `facts_required: true`: mỗi claim có số liệu gắn nguồn trong `sources`;
  máy duyệt chặn claim không nguồn.
- Chống văn AI: dùng `references/ai-tells.md` hiện có + bổ sung văn nói Việt.

### GĐ5 — Đóng gói
- Thumbnail: 1 ảnh Flow 16:9 (nhân vật cảm xúc mạnh) + chữ 2–3 từ vẽ bằng Remotion still;
  3 phương án.
- `metadata.json`: 3 tiêu đề, mô tả (hook 2 câu + chapters từ ranh giới cảnh WAV thật +
  nguồn), tags. Xuất vào `video/<job>/` cùng MP4.
- Ghi chú khai báo: hoạt hình cách điệu, không cần nhãn nội dung tổng hợp chân thực.

### GĐ6 — Pilot có người duyệt
- 3 video thử ở chế độ `review` (người duyệt đủ 3 mốc). Đo: số lượt Antigravity, số ảnh
  Flow mới, thời gian TTS/render, lỗi phải sửa.
- Hiệu chỉnh speech_rates bằng `scripts/calibrate_speech_rates.py`.

### GĐ7 — Tự động
- `tiensu/bank.py queue` → `pilot.py batch` ở chế độ `auto` với các cap ở mục 3.
- Chỉ bật sau khi 3 video pilot đạt và số liệu nằm trong ngân sách.
- Tùy chọn: cắt 2–3 Shorts 9:16 từ mỗi video dài, dùng lại ảnh (không tốn Flow).

## 5. Ba chủ đề thử

1. Một ngày sống như người săn bắt hái lượm: kiếm ăn, ngủ và giữ ấm ra sao?
2. Mưa cả tuần khi chưa có nhà: người tiền sử trú ẩn và kiếm ăn thế nào?
3. Mùa đông khắc nghiệt: tổ tiên sống sót khi chưa có nhà hay áo ấm ra sao?

## 6. Rủi ro

- Nhu cầu tiếng Việt chưa đạt phép thử 10/20 → chỉ mở rộng sau số liệu Analytics của pilot.
- Chính sách YouTube về nội dung lặp/hàng loạt → giữ người duyệt ở mốc content cho tới khi
  kênh ổn định; mỗi video tự nghiên cứu, nguồn thật.
- Máy đích 16 GB / P620 2 GB: render và TTS 10 phút chưa đo.
- Flow: chi phí credit chưa kiểm chứng tuyệt đối (flow-x4-results-20260922.md).
