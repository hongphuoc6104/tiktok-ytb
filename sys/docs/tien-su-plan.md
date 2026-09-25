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
| Mỗi beat = 1 ảnh Flow | Thư viện ảnh tái sử dụng + ghép lớp giữ nhận diện |
| `video_generation: false`, `credit_budget: 0` | Bật clip Veo (ảnh → video) cho hook, mở chương, cao trào |
| B-2 chạy 1 profile, `automatic_account_switching: false` | FlowPool: hàng đợi bền trên nhiều profile AI Pro, sổ credit từng profile |
| Không có đóng gói | Thumbnail, tiêu đề, mô tả, chapters, nguồn, tags |
| Máy duyệt xem toàn bộ artifact | Duyệt video dài bằng contact sheet + đoạn audio lấy mẫu |

## 3. Hai loại quota

### 3a. Phát triển — tiết kiệm tối đa
Quota của agent lập trình (token/lượt) là thứ cần giữ.

1. **Sửa, không viết lại.** Mở rộng `vocab/bank.py`, `image_pipeline.py`, `renderer/`,
   B-2 queue runner hiện có; module mới chỉ khi không có chỗ cắm.
2. **Đọc có mục tiêu.** Agent đọc `INDEX.md` + file của giai đoạn đang làm, dùng `grep`/`sed -n`
   thay vì đọc cả file lớn; không mở lại `reports/` lịch sử.
3. **Test offline bằng fixture** (`sys/tests`, `node --test`) trước; chạm Flow thật chỉ ở
   bước nghiệm thu từng giai đoạn, mỗi lần một lệnh ngắn.
4. **Một giai đoạn = một commit + ghi chú 5–10 dòng** trong mục 7 bên dưới để phiên sau
   không phải dò lại.

### 3b. Vận hành — dùng hết tài nguyên được cấp
Khi sản xuất video, được phép dùng tối đa lượt Antigravity, credit Flow và máy.

1. **Chất lượng trước.** Không cap cứng số ảnh; tạo 2–4 phương án mỗi ảnh/clip rồi chọn.
   Cap chỉ để chống vòng lặp vô hạn (giữ `auto_max_*` hiện có), không để tiết kiệm.
2. **Rẻ trước để hỏng sớm**, không phải để tiết kiệm: content → audio (local) → ảnh → clip.
   WAV lệch thời lượng thì dừng trước khi tốn Veo.
3. **Tận dụng mọi profile Google AI Pro** qua FlowPool (GĐ3b): ảnh chạy song song trên mọi
   profile; clip Veo phân bổ theo số credit còn lại của từng profile.
4. **Chữ không nằm trong ảnh/clip.** Nhãn, bản đồ, số, tiêu đề chương do Remotion vẽ — lý do
   là độ chính xác tiếng Việt (model sinh chữ Việt sai dấu), không phải tiết kiệm.
5. **Thư viện tái sử dụng** vẫn giữ để giữ nhận diện nhân vật/bối cảnh xuyên video.
6. **Máy duyệt đầy đủ**: content toàn văn; media xem từng ảnh/clip; video xem toàn bộ nếu
   phiên Antigravity hỗ trợ, nếu không thì contact sheet 1 khung/5 s + mọi clip Veo.

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
- Beat loại `clip`: phát clip Veo bằng `OffthreadVideo` (tắt tiếng, cắt/lặp theo neo lời
  đọc), overlay chữ vẫn chồng được lên clip.
- `assets/library/index.jsonl` + bước planner "reuse-first"; ảnh mới được đăng ký vào thư
  viện sau khi media đạt duyệt.
- Prompt template doodle nền kem, không chữ trong ảnh.

### GĐ3b — FlowPool: tool Flow tự động nhiều profile
Mở rộng `experiments/b2_illustrator` (queue-runner, attempt-store, session) thành
`sys/flowpool/`, dùng chung cho ảnh và clip.

- **Pool profile** (`flowpool/profiles.json`, sinh từ `browser-profiles.json`): mỗi profile
  có trạng thái `ready | busy | low_credit | needs_login | captcha | cooldown`, số credit đọc
  từ UI trước/sau mỗi lượt, giới hạn song song riêng.
- **Bộ lập lịch**: ảnh (Nano Banana, không tốn credit theo đo 22/09) chia vòng tròn cho mọi
  profile `ready`; clip Veo giao cho profile còn nhiều credit nhất. Profile gặp
  CAPTCHA/đăng xuất bị loại khỏi vòng và báo người dùng — tool **không** tự giải CAPTCHA,
  không tự đăng nhập.
- **Song song theo RAM**: mặc định 2 Chrome cùng lúc trên máy 16 GB (đo lại), mỗi Chrome
  gửi hàng đợi 4 yêu cầu như B-2 x4 đã nghiệm thu.
- **Hàng đợi bền**: mỗi yêu cầu có intent → submitted → collected → validated, ghi
  ndjson fsync; khởi động lại không gửi trùng yêu cầu chưa rõ kết quả (giữ quy tắc timeout
  hiện có).
- **Clip Veo**: chế độ ảnh → video (frames to video) từ ảnh đã duyệt để giữ nhân vật; 8 s,
  tắt tiếng clip, lời đọc vẫn là VieNeu; 2 phương án/clip, máy duyệt chọn.
- **Sổ credit** `flowpool/ledger.ndjson`: profile, loại, model, credit trước/sau, job, scene.
  `pilot.py flowpool status` in số dư, clip còn tạo được trong tháng theo từng profile.
- **Cấu hình**: `config.video_generation: true`, `credit_budget` = tổng trần theo tháng người
  dùng đặt, `veo_model` (Fast/Quality), `veo_clips_per_video` (mặc định 8–12).
- Bỏ khóa trong `image_pipeline.py:169` chỉ cho job có brief khai báo `clips`.

Phân bổ clip mỗi video (mặc định, chỉnh theo credit thật): hook 0–45 s (2–3 clip),
mở mỗi chương (1 clip), cao trào + kết (2 clip). Phần còn lại ảnh tĩnh + chuyển động
Remotion, đúng phong cách doodle của kênh mẫu.

Ràng buộc: chỉ dùng profile của chính người dùng, mỗi tài khoản có gói AI Pro hợp lệ;
người dùng tự chịu trách nhiệm tuân thủ điều khoản Google về nhiều tài khoản.

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
- 3 video thử ở chế độ `review` (người duyệt đủ 3 mốc). Đo: credit Veo thật/clip và
  /video theo sổ FlowPool, số ảnh, thời gian mỗi profile, TTS/render, lỗi phải sửa.
- Từ số đo, đặt `veo_clips_per_video` và số video/tháng mà tổng credit các profile nuôi được.
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
- Flow: chi phí ảnh chưa kiểm chứng tuyệt đối (flow-x4-results-20260922.md); credit Veo
  mỗi clip phải đo từ UI trước/sau, không lấy từ tài liệu.
- Giao diện Flow thay đổi làm hỏng selector → FlowPool có `doctor` kiểm tra từng profile
  trước mỗi batch và dừng sạch khi lệch.
- Nhiều Chrome song song trên 16 GB RAM → bắt đầu 2 profile, tăng khi đo được.

## 7. Thứ tự thực hiện và nhật ký

Thứ tự: GĐ1 → GĐ3b (FlowPool, cần máy có profile) → GĐ2 → GĐ3 → GĐ4 → GĐ5 → GĐ6 → GĐ7.
FlowPool làm sớm vì là phần rủi ro cao nhất và các giai đoạn sau phụ thuộc số đo credit.

Nhật ký (mỗi giai đoạn thêm 5–10 dòng: đã làm, file chính, lệnh test, việc còn lại):

- 25/09/2026: lập kế hoạch; bổ sung FlowPool + Veo theo yêu cầu người dùng.
