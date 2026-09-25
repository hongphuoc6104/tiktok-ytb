Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Kịch bản dài 16:9 cho kênh giải thích tiền sử (tiensu)

Dùng khi `brief.channel == "tiensu"` (adapter tự nạp file này ở lượt outline/content, xem
`scripts/director_context.py`). Khuôn kể chuyện mô phỏng kênh mẫu Ink Explainer — xem
`docs/tien-su-plan.md` mục 1 — nhưng KHÔNG dịch kịch bản, không dùng lại hình/nhân vật/thumbnail
của kênh mẫu. Đọc `tiensu/channel.json` (domain_requirements) và brief hiện tại trước khi viết;
brief đã lưu là hợp đồng, sửa qua đúng workflow nếu muốn đổi yêu cầu.

## Cấu trúc 5 phần bắt buộc

Ánh xạ vào `required_points` R1-R5 do `tiensu/bank.py` sinh sẵn trong brief; `coverage` phải phủ
đủ cả 5. Không ép mọi chương dài bằng nhau — nhịp theo lượng bằng chứng thật của từng chương.

1. **Hook 2 ngôi "bạn"** (30-45 giây đầu): đối lập trực tiếp một hành động đời thường của người
   xem hôm nay với cùng hành động đó khoảng 50.000 năm trước. Không mở bằng lời chào chung chung
   hay giới thiệu kênh. Kết hook bằng câu hỏi bí ẩn của video.
2. **Phá niềm tin phổ biến**: nêu một hiểu lầm/định kiến thường gặp về chủ đề, rồi chỉ ra vì sao
   nó sai hoặc chưa đủ — dựa trên bằng chứng thật trong `sources`, không phải khẳng định suông.
3. **Nhắc lại câu hỏi bí ẩn** rõ ràng, thành một câu độc lập người xem nhớ được, trước khi vào
   chương bằng chứng đầu tiên.
4. **6-8 chương bằng chứng**: mỗi chương dựng trên đúng MỘT nghiên cứu/di chỉ/số liệu cụ thể có
   trong `sources` của brief. Đặt tên chương ngắn gọn vào `scenes[].chapter` (dùng cho mô tả
   YouTube ở bước đóng gói, xem `packaging`). Mỗi tuyên bố có số liệu/tên riêng/niên đại phải có
   một `claims[]` trỏ đúng `source_id`; không suy diễn quá xa dữ liệu khảo cổ/nhân học thật, nói
   rõ mức độ chắc chắn khi nguồn còn tranh cãi (xem ví dụ Toba trong `tiensu/topics.jsonl`).
5. **Kết callback**: quay lại đúng hình ảnh đã dùng ở hook (dùng lại `image_id` hoặc ảnh cùng bối
   cảnh), chốt bằng một cặp câu đối chiếu dạng "Bạn thì… còn họ thì…" giữa đời sống hiện đại của
   người xem và điều vừa học được. Không thêm CTA sub/theo dõi vào giữa nội dung.

## Giọng kể "bạn" — văn nói tiếng Việt tự nhiên

Đây là lời đọc lên (VieNeu), không phải văn viết để đọc bằng mắt; áp dụng cùng lúc với
[văn phong chung](narration-style.md) — đọc file đó trước khi viết narration, các ràng buộc bắt
buộc ở đó (giữ đủ ý, không bịa, viết narration xong mới đặt neo, câu ngắn cho TTS ≤256 ký tự) áp
dụng nguyên vẹn ở đây, cộng thêm:

- Xưng "bạn" xuyên suốt khi nói với người xem (thì hiện tại), xưng "họ"/tên nhóm người khi kể về
  người tiền sử (thì quá khứ) — giữ ranh giới hai ngôi rõ ràng, không lẫn lộn giữa các câu.
- Văn nói tự nhiên của người kể chuyện YouTube tiếng Việt: câu hỏi tu từ, câu cụt có chủ đích,
  nhấn bằng nhịp câu chứ không phải viết hoa toàn từ. Tránh giọng học thuật/báo cáo khoa học.
  Tránh sáo ngữ AI — xem [ai-tells.md](ai-tells.md) khi câu nghe "trơn" bất thường.
  Không dịch máy từ tiếng Anh; viết thẳng bằng tiếng Việt.
- Thuật ngữ khảo cổ/nhân học (ví dụ: "Cựu Thạch khí", "hominin", tên di chỉ nước ngoài) phải được
  giải thích ngay bằng lời dẫn thường khi xuất hiện lần đầu, không giả định người xem đã biết.
  Tên riêng/địa danh nước ngoài đọc được bằng tiếng Việt tự nhiên; không phiên âm gượng ép.
  Năm/số liệu đọc thành lời tự nhiên ("khoảng ba mươi tư nghìn năm trước"), không đọc dạng số viết.

## Bằng chứng và nguồn — facts_required luôn true

- Không thêm số liệu, tên nghiên cứu, hoặc kết quả khảo cổ không có trong `sources` của brief.
  Cần thêm bằng chứng ngoài brief thì phải nghiên cứu và bổ sung vào `sources` qua revise-brief
  trước, không tự bịa rồi viết `claims` khớp theo.
  `planning.domain_requirements` có dòng "Gợi ý nghiên cứu thêm" lấy từ `seed_facts` của kho chủ
  đề (`tiensu/topics.jsonl`) — đây là hướng tìm thêm, KHÔNG phải bằng chứng đã duyệt; chỉ dùng sau
  khi tự tìm được nguồn thật và đưa vào `sources`.
- Mỗi chương bằng chứng (R4) cần ít nhất một `claims[]` với `source_id` trỏ đúng mục trong
  `sources`, `fact` khớp với một fact đã liệt kê ở source đó, và `quote` trích nguyên văn từ
  narration của đúng cảnh đang neo — không diễn giải khác đi khi trích.
  Máy duyệt content chặn claim không nguồn hoặc lệch mức độ chắc chắn của nguồn gốc.
- Khi một giả thuyết còn tranh cãi trong giới nghiên cứu (ví dụ có nguồn ủng hộ và nguồn phản
  bác), nói rõ điều đó trong lời dẫn thay vì chọn một phía rồi trình bày như sự thật đã chốt.

## Hình ảnh — không chữ trong ảnh, chữ do Remotion vẽ

- Mọi `images[]` giữ `visible_text: []`; không yêu cầu model sinh chữ/số/nhãn trong ảnh (tiếng
  Việt có dấu thường bị model vẽ sai). Phong cách theo `channel.json.style`: doodle người que mực
  đen trên nền kem/be, không màu sắc rực rỡ, không chi tiết ảnh thật.
- Nhãn, tên chương, mốc thời gian, mũi tên chỉ vị trí, số liệu chạy số… đặt vào `beats[].overlays`
  (không phải `visible_text`): `type` một trong `label|chapter_title|map_pin|counter|arrow`, `text`
  tiếng Việt có dấu, toạ độ `x,y` trong khung 0-1, `at` là giây tính từ đầu beat. Dùng `counter`
  khi cần chạy số (ví dụ tuổi di chỉ) kèm `to`; dùng `arrow` kèm `angle` khi chỉ vào chi tiết ảnh.
- `images[].kind` mặc định `still`. Ảnh loại `clip` (dùng cho hook, mở mỗi chương, cao trào/kết
  — xem `docs/tien-su-plan.md` mục 3b) phải có `from_image` trỏ tới id một ảnh `still` cùng cảnh
  làm khung hình đầu, và `motion` mô tả chuyển động bằng tiếng Anh (prompt nội bộ); không vượt
  `brief.clips.max`. Không tự đặt `kind: clip` khi brief không có trường `clips` (kênh/job đó
  chưa bật Veo).

## Ngân sách độ dài/nhịp và lỗi chặn thường gặp (bắt buộc)

Brief dài (`duration.max_seconds > 300` hoặc `channel == "tiensu"`) được adapter viết theo từng
cảnh (`scripts/agy_longform.py`): sau dàn ý, mỗi cảnh một lượt gọi kèm ngân sách riêng, lời dẫn các
cảnh trước và schema một cảnh; rồi một lượt đóng gói; lỗi hợp đồng được sửa có giới hạn (tối đa 2
vòng, chỉ cảnh lỗi). Ngân sách tính từ điểm giữa `duration` và `planning.speech_rates` (8-12 phút,
3,6 âm tiết/giây ≈ 1.800-2.400 âm tiết cả video) và là mục tiêu cứng ±15% cho từng cảnh:

- Lời dẫn: đủ số âm tiết (đếm theo từ cách nhau bởi dấu cách) của cảnh; thiếu hoặc thừa quá 15% bị
  chặn `BUDGET_UNITS`. Viết lời dẫn đủ dài trước, rồi mới đặt neo/coverage/claims lên trên.
- Nhịp: một beat mỗi 4-6 giây lời dẫn (cả video khoảng 80-150 beat); sai khoảng bị chặn
  `BUDGET_BEATS`. Không cần ảnh mới cho mỗi beat: dùng lại một ảnh `still` qua nhiều beat liên
  tiếp và đổi overlay/effect/focus (cả video khoảng 40-70 ảnh riêng, kể cả clip trong `clips.max`).
- Mô tả hình (`description`, `preserve`, `change`, `motion`), lời dẫn và chữ overlay KHÔNG được chứa
  mã quản lý (mã nhân vật như CH01, mã cảnh SC…, mã ảnh/beat như IMG_…/B…). Gọi nhân vật bằng tên và
  ngoại hình ("người tiền sử tóc bù mặc áo da thú"), không viết "CH01 ngồi dậy". Lỗi này bị chặn
  `INTERNAL_LABEL`.
- Chữ overlay ngắn: `label`/`map_pin` ≤ 40 ký tự, `chapter_title` ≤ 60, `counter`/`arrow` ≤ 30;
  vượt bị chặn `OVERLAY`. Tên chương dài đặt ở `scenes[].chapter`, overlay chỉ ghi bản rút gọn.
- Mã ảnh/beat đặt theo cảnh (`SC03_I01`, `SC03_C01`, `SC03_B01`) để không trùng giữa các cảnh.

## Đóng gói (`packaging`)

Viết cùng lúc với kịch bản, không phải bước riêng: điền `packaging` ở top-level content-v3.
- `titles`: đúng 3 phương án theo khuôn "Người tiền sử làm gì/ra sao khi ___?" hoặc biến thể câu
  hỏi 2 ngôi, không phóng đại/giật tít sai bằng chứng đã viết.
- `thumbnail.text`: 2-4 từ tiếng Việt in hoa, thường kết bằng dấu hỏi; `thumbnail.image_id` trỏ
  một ảnh `still` đã có trong `images[]` (không tạo ảnh thumbnail riêng ở bước content).
  `thumbnail.emotion`: cảm xúc nhân vật cần thấy rõ trong ảnh đó (ví dụ "hoảng sợ", "tò mò").
- `hook`: đúng 2 câu tóm tắt lời hứa mở đầu, dùng cho mô tả video, không trùng nguyên văn narration.
- `tags`: từ khoá liên quan tiền sử/khảo cổ/sinh tồn, tiếng Việt, không nhồi từ khoá không liên quan.
- `scenes[].chapter` của mỗi chương bằng chứng (R4) ghép với thời điểm bắt đầu thật của cảnh trong
  WAV (đo ở bước media) để `packaging.py` (GĐ5) dựng danh sách chapters cho mô tả YouTube.

## Không sao chép kênh mẫu

Chỉ lấy khuôn kể chuyện (hook 2 ngôi, phá niềm tin, 6-8 chương, callback) và công thức thumbnail;
không dịch bất kỳ câu nào từ video của kênh mẫu, không mô tả lại hình ảnh/nhân vật của họ. Xem
`tiensu/channel.json.avoid` và `assets/characters/tiensu-mascot/` cho nhân vật riêng của kênh này.

Đọc thêm [director-contract.md](director-contract.md) và [vp-script-director](../../vp-script-director/SKILL.md).
