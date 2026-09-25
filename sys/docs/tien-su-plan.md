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
| Máy duyệt short 1 phút | Duyệt video dài 10 phút + mọi clip Veo (mục 3b.6) |

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

Mỗi giai đoạn kết thúc bằng tests đạt + commit riêng. Flow thật chỉ dùng ở bước nghiệm thu GĐ3b và từ GĐ6.

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

- **Pool tài khoản** (`flowpool/profiles.json`; mỗi tài khoản một Chrome riêng do FlowPool quản lý,
  user-data-dir `sys/.gflow/pool/<tên>/` + cổng debug riêng — xem nhật ký 25/09 bản 2): mỗi profile
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
- 25/09/2026 (GĐ1): thêm `tiensu/` (channel.json, topics.jsonl 30 chủ đề — 3 chủ đề thử đúng mục 5,
  mỗi chủ đề có `sources` thật để qua cổng facts_required — ledger.json, bank.py CLI
  status/next/start/mark/queue/audit tái dùng tiện ích từ `vocab/bank.py`, policy.py). Sửa
  `config.json` (brief_policies → tiensu.policy:check, max_seconds 780) và `pilot.py` (thêm
  `tiensu/*.py` vào protected()/git_state() cho song song với vocab). Thêm 4 trường brief-v3
  (channel/voice_language/subtitles/clips) và content-v3 (scenes.chapter, images.kind/from_image/
  motion, beats.overlays, effect pan_left/pan_right/pop, packaging) — tất cả optional, đã xác minh
  30 brief sinh từ kho qua được validate_brief. Xoá dữ liệu vocab-only (briefs/*.json,
  sources/*.txt, bank.jsonl); ledger.json rỗng lại ({"entries":{}}). vocab/test_bank.py::
  RealBankTests tự skip khi thiếu bank.jsonl (cơ chế skip có sẵn). Sửa 2 chỗ trong
  tests/test_redesign.py phụ thuộc bank.jsonl thật khác rỗng (so is_file() với bản gốc thay vì
  assertTrue cứng; skip test dùng bank.bank()[0] khi kho thật đã gỡ) — đây là test chung của cơ
  chế sandbox, không riêng vocab/tiensu.
  Test: `sys/.venv/bin/python -m unittest discover -s tests` + `tiensu.test_bank` + `vocab.test_bank`.
  Việc còn lại: GĐ2 (voice_language chưa được content_contract.py/adapters.py thật sự dùng để bỏ
  yêu cầu narration_en trên 16:9 — cờ needs_en vẫn theo aspect_ratio), GĐ3/GĐ3b (renderer overlay/
  clip, FlowPool), GĐ5 (packaging.py chưa tồn tại), GĐ6 pilot 3 video thật.
- 25/09/2026 (GĐ4): thêm `.agents/skills/vp-content/references/explainer-longform.md` (cấu trúc
  5 phần, giọng "bạn", ràng buộc facts/sources, quy tắc overlays/clip/packaging) và
  `.agents/skills/vp-tiensu/SKILL.md`. Sửa `scripts/director_context.py`: thêm `tiensu_brief()` +
  nạp `explainer-longform.md` ở stage outline/content khi `brief.channel=="tiensu"` (đã kiểm bằng
  script tay: nạp đúng cho brief tiensu, không nạp cho brief từ vựng). Không sửa
  `prompt_templates.py` (giữ đúng AGENTS.md "giữ nguyên mẫu prompt"; phong cách no-text/cream
  doodle đã đủ qua `style` + `visible_text: []`, không cần sửa template chung).
  Việc còn lại: viết thật một kịch bản tiensu qua `pilot.py run JOB content` để kiểm references
  trong tình huống thật (chưa làm vì không tạo job sản xuất theo yêu cầu phạm vi).
- 25/09/2026 GĐ3b (offline, chưa nghiệm thu thật): `sys/flowpool/` (pool/scheduler/journal/ledger/profiles,
  worker.mjs + flow-ops.mjs). Ảnh qua hàng đợi B-2 (queue-runner tách hàm dùng chung), clip qua Flow
  frames-to-video (gflow FlowPage). Worker chỉ gắn CDP vào Chrome đang chạy; mọi profile của một
  user-data-dir chạy trong một Chrome, mỗi profile một cửa sổ mở bằng `flowpool open-profile`.
  `image_pipeline` dùng FlowPool khi `flowpool_enabled`; `kind: clip` + `brief.clips` mở khóa video/credit.
  Test: `python -m unittest tests.test_flowpool tests.test_flowpool_pipeline`, `node --test flowpool/test-flow-ops.mjs`.
  Còn lại: nghiệm thu thật (gắn tab theo profile, đọc credit, selector Veo), tool_url/media ID từng tài khoản.
- 25/09/2026 GĐ3b bản 2 (sau nghiệm thu thật lần 1): Chrome 152 chỉ cho CDP thấy một profile của
  user-data-dir mặc định (bật qua chrome://inspect), gắn tab theo dấu URL chập chờn; labs.google/fx/tools/flow
  chuyển sang flow.google.com; tài khoản mới chưa có project "Video Pilot". Đổi sang **mỗi tài khoản một Chrome
  riêng**: `add NAME` (thư mục `sys/.gflow/pool/NAME/`, cổng 9301+), `login NAME` (mở không có cổng debug để
  người dùng tự đăng nhập), `launch NAME|--all`, `stop NAME|--all`. Bỏ chế độ profile dùng chung và
  `open-profile`. Worker nối đúng cổng của instance; chỉ instance đang chạy mới nhận việc (tối đa
  `flowpool_max_browsers`). Project tự mở theo URL đã ghi, không có thì tìm theo tên, không có nữa thì bấm
  "New project" và ghi `project_url` (không đổi tên project). Ảnh mặc định đi đường Flow UI (đính kèm ảnh tham
  chiếu bằng Upload, 1 ảnh/lượt); đường B-2 x4 chỉ khi instance có `tool_url` + media ID của tài khoản đó.
  Selector chỉ kiểm bằng đọc mã (gflow-cli 1.1.1), chưa chạy thật.
- 25/09/2026 GĐ2 + GĐ3 (phần renderer): brief `voice_language`/`subtitles`/`channel`/`clips`;
  16:9 + `vi` dùng narration.wav, không cần narration_en/quote_en/neo en (story_plan.needs_english
  là nguồn duy nhất cho content_contract, estimates, review_plan, pilot gate audio/render, workflow
  visual-timing, editorial_audit, machine_review). Phụ đề Việt đốt vào 16:9, kiểm hình học ở 1920×1080.
  Content-v3: clip (`kind/from_image/motion`), hiệu ứng pan_left/pan_right/pop, `overlays[]`,
  `chapter`, `packaging` (chỉ kiểm hình dạng). Renderer: overlay Noto Sans Bold nhúng (`renderer/fonts`),
  counter đếm lên, chapter_title 3,5 s, clip MP4 qua OffthreadVideo + Loop (tắt tiếng), render-timing.json.
  TTS: đoạn không dấu câu bị cắt ≤240 ký tự. Test: `tests/test_longform_16x9.py`; toàn bộ 295 test đạt.
- Đo render (Ryzen 5 6600H, RTX 3050; `scripts/render_benchmark.py`, 600 s 1920×1080, 8 cảnh, 120 beat,
  2 clip, overlay mọi loại, phụ đề): 30 fps, concurrency 6 → 1340 s (**2,23×**); encode đã là h264_nvenc
  qua `hardwareAcceleration`. Đường rẻ: `config.render_fps: 15` (chỉ 16:9) + `render_concurrency: 8` →
  Remotion chụp 15 fps rồi ffmpeg lặp khung lên 30 fps (nvenc, fallback libx264) → 719 s (**1,20×**).
  Việc còn lại: đặt `render_fps: 15`, `render_concurrency: 8` trong config.json kênh (agent GĐ1 giữ file
  này); đường ffmpeg-tĩnh + Remotion-overlay chưa cần. Chưa đo trên máy 16 GB/P620 và chưa xem clip Veo thật.

## 8. Hợp đồng dữ liệu chung (khóa trước khi phát triển song song)

Mọi trường mới đều **tùy chọn**; thiếu trường thì hành vi cũ giữ nguyên (job từ vựng, job lịch sử).

### Brief (brief-v3, thêm)
- `channel`: `"tiensu"` | … — tên kênh sinh brief.
- `voice_language`: `"vi"` | `"en"`. Mặc định: 16:9 → `en`, 9:16 → `vi` (như cũ). 16:9 + `vi` =
  WAV Việt, không cần `narration_en`, không cần `quote_en`.
- `subtitles`: bool. Mặc định: true khi giọng Việt, false khi 16:9 tiếng Anh.
- `clips`: `{ "max": int, "model": "veo-fast" | "veo-quality", "variants": int }` — thiếu = không clip.

### Content-v3 (thêm)
- `images[].kind`: `"still"` (mặc định) | `"clip"`. Clip có `from_image` (id ảnh still cùng cảnh
  làm khung đầu), `motion` (mô tả chuyển động, tiếng Anh), không có `visible_text`.
  Tệp clip là MP4 do FlowPool trả về; beat trỏ `image_id` tới clip như ảnh thường.
- `beats[].effect` thêm: `pan_left`, `pan_right`, `pop`.
- `beats[].overlays[]`: `{ "type": "label"|"chapter_title"|"map_pin"|"counter"|"arrow",
  "text": str, "x": 0–1, "y": 0–1, "at": giây tính từ đầu beat (mặc định 0),
  "to": số đích (chỉ counter), "angle": độ (chỉ arrow) }`. Chữ do Remotion vẽ, tiếng Việt có dấu.
- `packaging`: `{ "titles": [3 chuỗi], "thumbnail": { "image_id": id ảnh still có sẵn,
  "text": 2–4 từ in hoa, "emotion": str }, "hook": 2 câu mô tả, "tags": [..] }`.
- `scenes[].chapter`: tên chương hiển thị trong mô tả YouTube.

### FlowPool (`sys/flowpool/`)
- Yêu cầu: `{ "id", "kind": "image"|"clip", "prompt", "ratio": "16:9"|"9:16",
  "refs": [đường dẫn ảnh tham chiếu], "start_frame": đường dẫn (clip), "variants": n,
  "model": str, "job", "scene" }`.
- Kết quả: `{ "id", "status": "ok"|"failed"|"unknown", "files": [..], "profile",
  "credits_before", "credits_after", "error" }`.
- API Python: `flowpool.run(requests, cfg) -> list[result]`; CLI
  `python3 -m flowpool status|doctor|run --queue FILE`.

### Đóng gói (`sys/packaging.py`)
- Chạy sau render đạt duyệt video; ghi `thumbnail.jpg` (1280×720), `metadata.json`
  (titles, description, chapters, tags, sources), `description.txt` vào `video/<job>/`.
- Chapters lấy từ thời điểm bắt đầu thật của từng cảnh trong WAV; chương đầu 0:00.
