# Kịch bản — vocab-pull-script-536 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-pull-script-536/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "kéo" của từ PULL, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "kéo" của PULL mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng PULL trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt

Yêu cầu chuyên biệt:
- Nhân vật chính CH01 dùng đúng mascot chuẩn assets/characters/channel-mascot/reference-v1.png; giữ cấu trúc mặt, một thân, áo và độ dày nét qua mọi hình
- Một video phục vụ một kết quả học quan sát được: nhận ra nghĩa đã chọn và dùng được từ trong câu đơn giản phù hợp mức học
- Các ví dụ thuộc một micro-story có nguyên nhân, hành động và hậu quả hoặc một đối chiếu có mục đích; số cảnh trong brief là kế hoạch sản xuất, không phải năm mục giảng cố định
- Hook cho thấy một tình huống hoặc câu hỏi cụ thể; từ khóa/cách dùng xuất hiện đủ sớm để người xem hiểu lợi ích, kết thúc trả lời được lời hứa mở đầu
- Có một lượt luyện nói hoặc nhớ lại với mẫu đúng, khoảng chờ thật và phản hồi; khai báo audio_direction cho cảnh luyện tập khi cần khoảng chờ cuối cảnh
- Phát âm, IPA, nối âm, đối chiếu từ dễ nhầm và gốc từ chỉ dùng khi hữu ích và có căn cứ; không bắt buộc nhồi đủ mọi mục
- Từ khóa/câu học hiển thị rõ gần hành động, ưu tiên 1/3 phía trên và tránh vùng phụ đề/UI; giữ đúng chính tả tiếng Anh, I không biến thành Ai
- Mỗi hình/beat có chức năng học hoặc kể chuyện; đủ ảnh cho thay đổi cần thấy, giữ liên tục trạng thái trước khi tối ưu hàng đợi
- Không hứa xem khẩu hình với ảnh tĩnh; phân biệt shadowing với nghe-dừng-nhắc lại; không dùng nhãn chuẩn Tây làm tiêu chí phát âm
- Phụ đề chia theo cụm nghĩa, tối đa hai dòng, không dấu câu đứng riêng; nhận xét đồng bộ phải căn cứ âm thanh/video thật
- Từ khoá duy nhất của video: PULL (v), chỉ dạy nghĩa "kéo"
- Mức độ người học: CEFR A1; chủ đề: Động từ thông dụng
- Mã mục trong kho từ vựng: pull.v.drag (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm short; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 39.33–65.54 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.03–15.04 |
| SC02 | 7.45–12.42 |
| SC03 | 7.25–12.08 |
| SC04 | 8.56–14.27 |
| SC05 | 7.04–11.73 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Ngăn kéo cần kéo về phía mình — Nhịp 1

Mục đích: Introduce a concrete need and the selected sense.

Giấy ở trong ngăn, tay nắm lại đang bị bỏ quên! Pull nghĩa là kéo. "Bring it towards you here." Bạn muốn lấy giấy trong ngăn bàn, người bạn chỉ tay nắm để bạn mở bằng đúng hành động.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot reaches toward closed desk drawer, companion indicates handle. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot reaches toward closed desk drawer, companion indicates handle.

Lý do: Introduce a concrete need and the selected sense.

Chữ được phép: “pull” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Giấy ở trong ngăn, tay nắm lại đang bị bỏ quên! Pull nghĩa là kéo. "Bring it towards you here." Bạn muốn lấy giấy trong ngăn bàn, người bạn chỉ tay nắm để bạn mở bằng đúng hành động.” (lần 1) · Introduce a concrete need and the selected sense.

## SC02 — Ngăn kéo cần kéo về phía mình — Nhịp 2

Mục đích: Make the first model an action in the situation.

Người bạn nhắc: "Pull the handle." Kéo tay nắm nhé. "Move it towards your body." Bạn giữ tay nắm và kéo ngăn ra, thay vì chỉ chạm rồi chờ nó tự mở.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Closed drawer with hand on handle Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Closed drawer with hand on handle

Lý do: Make the first model an action in the situation.

Chữ được phép: Không có chữ/số

**Hình SC02_I2** — Same drawer pulled outward toward mascot, papers visible inside. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Same drawer pulled outward toward mascot, papers visible inside.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “Pull the handle.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Người bạn nhắc: "Pull the handle." Kéo tay nắm nhé. "Move it towards your body." Bạn giữ tay nắm và kéo ngăn ra, thay vì chỉ chạm rồi chờ nó tự mở.” (lần 1) · Make the first model an action in the situation.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “Pull the handle.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC03 — Ngăn kéo cần kéo về phía mình — Nhịp 3

Mục đích: Advance the same story with the second model.

Người ấy nhắc thêm: "Pull it slowly." Kéo chậm nhé. "Keep the papers in place." Bạn kéo tiếp vừa đủ để lấy giấy, các tờ còn lại vẫn nằm trong ngăn.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Mascot gently extends drawer enough to retrieve paper while friend watches. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot gently extends drawer enough to retrieve paper while friend watches.

Lý do: Advance the same story with the second model.

Chữ được phép: “Pull it slowly.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người ấy nhắc thêm: "Pull it slowly." Kéo chậm nhé. "Keep the papers in place." Bạn kéo tiếp vừa đủ để lấy giấy, các tờ còn lại vẫn nằm trong ngăn.” (lần 1) · Advance the same story with the second model.

## SC04 — Ngăn kéo cần kéo về phía mình — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn nhờ kéo tay nắm của ngăn bàn. "Say the action clearly." Nói như lúc cần lấy một tờ giấy: "Pull the handle."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold drawer handle and full instruction, no push motion shown as correct action. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold drawer handle and full instruction, no push motion shown as correct action.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Pull the handle.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nhờ kéo tay nắm của ngăn bàn. "Say the action clearly." Nói như lúc cần lấy một tờ giấy: "Pull the handle."” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Ngăn kéo cần kéo về phía mình — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"Pull the handle." Kéo tay nắm nhé. "The paper is within reach now." Ngăn đã được kéo ra, bạn lấy phần giấy cần dùng rồi cùng người bạn làm tiếp.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot retrieves sheet from open drawer and places it on shared work table. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot retrieves sheet from open drawer and places it on shared work table.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “Pull the handle.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Pull the handle." Kéo tay nắm nhé. "The paper is within reach now." Ngăn đã được kéo ra, bạn lấy phần giấy cần dùng rồi cùng người bạn làm tiếp.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Giấy ở trong ngăn, tay nắm lại đang bị bỏ quên! Pull nghĩa là kéo. "Bring it towards you here." Bạn muốn lấy giấy trong ngăn bàn, người bạn chỉ tay nắm để bạn mở bằng đúng hành động.
- R2 → SC01: Giấy ở trong ngăn, tay nắm lại đang bị bỏ quên! Pull nghĩa là kéo. "Bring it towards you here." Bạn muốn lấy giấy trong ngăn bàn, người bạn chỉ tay nắm để bạn mở bằng đúng hành động.
- R2 → SC02: Người bạn nhắc: "Pull the handle." Kéo tay nắm nhé. "Move it towards your body." Bạn giữ tay nắm và kéo ngăn ra, thay vì chỉ chạm rồi chờ nó tự mở.
- R3 → SC02: Người bạn nhắc: "Pull the handle." Kéo tay nắm nhé. "Move it towards your body." Bạn giữ tay nắm và kéo ngăn ra, thay vì chỉ chạm rồi chờ nó tự mở.
- R3 → SC03: Người ấy nhắc thêm: "Pull it slowly." Kéo chậm nhé. "Keep the papers in place." Bạn kéo tiếp vừa đủ để lấy giấy, các tờ còn lại vẫn nằm trong ngăn.
- R4 → SC04: Bạn muốn nhờ kéo tay nắm của ngăn bàn. "Say the action clearly." Nói như lúc cần lấy một tờ giấy: "Pull the handle."
- R4 → SC05: "Pull the handle." Kéo tay nắm nhé. "The paper is within reach now." Ngăn đã được kéo ra, bạn lấy phần giấy cần dùng rồi cùng người bạn làm tiếp.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

Không có.

## Kết quả sửa

Không có.

## Vấn đề còn lại

Không có.