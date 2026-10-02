# Kịch bản — vocab-draw-script-472 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-draw-script-472/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "vẽ (bằng bút)" của từ DRAW, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "vẽ (bằng bút)" của DRAW mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng DRAW trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn DRAW với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "draw" còn nghĩa khác: trận hoà [n, draw.n]. Video này KHÔNG dạy nghĩa đó.
- Từ "draw" còn nghĩa khác: hoà (trong thi đấu) [v, draw.v.sport]. Video này KHÔNG dạy nghĩa đó.
- Từ "draw" còn nghĩa khác: rút ra (kết luận) [v, draw.v.draw-conclude]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: DRAW (v), chỉ dạy nghĩa "vẽ (bằng bút)"
- Mức độ người học: CEFR A1; chủ đề: Âm nhạc và nghệ thuật
- Mã mục trong kho từ vựng: draw.v.art (dùng để đánh dấu đã làm)
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

VI: 44.03–73.37 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 8.82–14.69 |
| SC02 | 8.59–14.32 |
| SC03 | 8.08–13.47 |
| SC04 | 10.04–16.73 |
| SC05 | 8.5–14.16 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Bản đồ chưa có công viên — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Nói khó hình dung, mình vẽ luôn nhé! Draw nghĩa là vẽ bằng bút trong bài này. "Put lines on paper." Bạn muốn chỉ chỗ hẹn cho người bạn, lấy giấy để tạo một sơ đồ đơn giản.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot starts a simple meeting-route sketch as companion watches the pencil tip, map referents remain simple. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot starts a simple meeting-route sketch as companion watches the pencil tip, map referents remain simple.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “draw” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Nói khó hình dung, mình vẽ luôn nhé! Draw nghĩa là vẽ bằng bút trong bài này. "Put lines on paper." Bạn muốn chỉ chỗ hẹn cho người bạn, lấy giấy để tạo một sơ đồ đơn giản.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Bản đồ chưa có công viên — Nhịp 2

Mục đích: Make the first model an action in the situation.

Bạn nói: "I can draw a map." Tôi có thể vẽ một sơ đồ. "A map for our meeting." Bạn vẽ đường chính và điểm bắt đầu để người bạn biết mình đang nói về khu vực nào.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot holds pencil above blank paper Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot holds pencil above blank paper

Lý do: Make the first model an action in the situation.

Chữ được phép: Không có chữ/số

**Hình SC02_I2** — Simple route lines and starting-place icon now drawn by mascot. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Simple route lines and starting-place icon now drawn by mascot.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “I can draw a map.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "I can draw a map." Tôi có thể vẽ một sơ đồ. "A map for our meeting." Bạn vẽ đường chính và điểm bắt đầu để người bạn biết mình đang nói về khu vực nào.” (lần 1) · Make the first model an action in the situation.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “I can draw a map.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC03 — Bản đồ chưa có công viên — Nhịp 3

Mục đích: Advance the same story with the second model.

Người bạn nhờ: "Draw the park here." Vẽ công viên ở đây nhé. "Add the meeting place." Bạn thêm hình cây ở vị trí đã chọn; sơ đồ giờ có cả đường và điểm hẹn.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend points to empty meeting position as mascot draws tree icon on same map. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend points to empty meeting position as mascot draws tree icon on same map.

Lý do: Advance the same story with the second model.

Chữ được phép: “Draw the park here.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn nhờ: "Draw the park here." Vẽ công viên ở đây nhé. "Add the meeting place." Bạn thêm hình cây ở vị trí đã chọn; sơ đồ giờ có cả đường và điểm hẹn.” (lần 1) · Advance the same story with the second model.

## SC04 — Bản đồ chưa có công viên — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn đề nghị mình có thể vẽ sơ đồ. "Offer to draw it." Hoàn thành câu bằng map rồi nói cả câu theo tình huống: "I can draw a..."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold drawn route and incomplete sentence, no complete answer printed. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold drawn route and incomplete sentence, no complete answer printed.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “I can draw a...” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn đề nghị mình có thể vẽ sơ đồ. "Offer to draw it." Hoàn thành câu bằng map rồi nói cả câu theo tình huống: "I can draw a..."” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Bản đồ chưa có công viên — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"I can draw a map." Tôi có thể vẽ một sơ đồ. "Now the place is visible." Người bạn đã hiểu đường qua những nét bút, hai người giữ tờ giấy để dùng lúc tới điểm hẹn.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Friend takes completed hand-drawn map while mascot indicates agreed park icon. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend takes completed hand-drawn map while mascot indicates agreed park icon.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “I can draw a map.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"I can draw a map." Tôi có thể vẽ một sơ đồ. "Now the place is visible." Người bạn đã hiểu đường qua những nét bút, hai người giữ tờ giấy để dùng lúc tới điểm hẹn.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Nói khó hình dung, mình vẽ luôn nhé! Draw nghĩa là vẽ bằng bút trong bài này. "Put lines on paper." Bạn muốn chỉ chỗ hẹn cho người bạn, lấy giấy để tạo một sơ đồ đơn giản.
- R2 → SC01: Nói khó hình dung, mình vẽ luôn nhé! Draw nghĩa là vẽ bằng bút trong bài này. "Put lines on paper." Bạn muốn chỉ chỗ hẹn cho người bạn, lấy giấy để tạo một sơ đồ đơn giản.
- R2 → SC02: Bạn nói: "I can draw a map." Tôi có thể vẽ một sơ đồ. "A map for our meeting." Bạn vẽ đường chính và điểm bắt đầu để người bạn biết mình đang nói về khu vực nào.
- R3 → SC02: Bạn nói: "I can draw a map." Tôi có thể vẽ một sơ đồ. "A map for our meeting." Bạn vẽ đường chính và điểm bắt đầu để người bạn biết mình đang nói về khu vực nào.
- R3 → SC03: Người bạn nhờ: "Draw the park here." Vẽ công viên ở đây nhé. "Add the meeting place." Bạn thêm hình cây ở vị trí đã chọn; sơ đồ giờ có cả đường và điểm hẹn.
- R4 → SC04: Bạn muốn đề nghị mình có thể vẽ sơ đồ. "Offer to draw it." Hoàn thành câu bằng map rồi nói cả câu theo tình huống: "I can draw a..."
- R4 → SC05: "I can draw a map." Tôi có thể vẽ một sơ đồ. "Now the place is visible." Người bạn đã hiểu đường qua những nét bút, hai người giữ tờ giấy để dùng lúc tới điểm hẹn.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 17099: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 472: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 17099 — addressed: Đã rà 3 giây đầu: mở bằng “Nói khó hình dung, mình vẽ luôn nhé!”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response