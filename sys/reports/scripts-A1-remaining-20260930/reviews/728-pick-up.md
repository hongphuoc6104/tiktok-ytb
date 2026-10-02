# Kịch bản — vocab-pick-up-script-728 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-pick-up-script-728/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "nhặt lên, cầm lên" của từ PICK UP, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "nhặt lên, cầm lên" của PICK UP mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng PICK UP trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn PICK UP với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "pick up" còn nghĩa khác: đón ai đó [phr, pick up.phr.collect-person]. Video này KHÔNG dạy nghĩa đó.
- Từ "pick up" còn nghĩa khác: học được (kỹ năng, ngôn ngữ) một cách tự nhiên [phr, pick up.phr.learn-naturally]. Video này KHÔNG dạy nghĩa đó.
- Từ "pick up" còn nghĩa khác: khởi sắc, cải thiện (kinh doanh, sức khoẻ) [phr, pick up.phr.improve]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: PICK UP (phr), chỉ dạy nghĩa "nhặt lên, cầm lên"
- Mức độ người học: CEFR A1; chủ đề: Cụm động từ
- Mã mục trong kho từ vựng: pick up.phr.lift-object (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm medium; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

6 cảnh · 7 hình logic · 7 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 54.4–90.65 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.43–19.05 |
| SC02 | 8.91–14.85 |
| SC03 | 9.75–16.24 |
| SC04 | 8.5–14.16 |
| SC05 | 7.94–13.23 |
| SC06 | 7.87–13.12 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Nhặt thẻ đang nằm dưới bàn — Nhịp 1

Mục đích: Make the selected sense useful in a concrete situation.

Thẻ trên bàn đã đếm rồi, một tấm còn nằm dưới chân ghế! Pick up trong bài này là nhặt lên, cầm lên từ chỗ thấp. "Lift the item from where it is lying here." Bạn dọn trò chơi hư cấu, cần lấy lại món trước khi cất đủ bộ.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion notice one game card on floor below table, no person injury. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion notice one game card on floor below table, no person injury.

Lý do: Make the selected sense useful in a concrete situation.

Chữ được phép: “pick up” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Thẻ trên bàn đã đếm rồi, một tấm còn nằm dưới chân ghế! Pick up trong bài này là nhặt lên, cầm lên từ chỗ thấp. "Lift the item from where it is lying here." Bạn dọn trò chơi hư cấu, cần lấy lại món trước khi cất đủ bộ.” (lần 1) · Make the selected sense useful in a concrete situation.

## SC02 — Nhặt thẻ đang nằm dưới bàn — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nhờ: "Pick up the card." Nhặt thẻ lên nhé. "The one below the chair in our scene." Người bạn nhìn đúng tấm được nhắc, cúi lấy trong cảnh minh họa rồi đưa về chỗ các thẻ đã kiểm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Card on floor beneath chair Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Card on floor beneath chair

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: Không có chữ/số

**Hình SC02_I2** — Companion holds same card above table level, ordinary adult pose. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Companion holds same card above table level, ordinary adult pose.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “Pick up the card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhờ: "Pick up the card." Nhặt thẻ lên nhé. "The one below the chair in our scene." Người bạn nhìn đúng tấm được nhắc, cúi lấy trong cảnh minh họa rồi đưa về chỗ các thẻ đã kiểm.” (lần 1) · Use the first English model with its immediate purpose.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “Pick up the card.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC03 — Nhặt thẻ đang nằm dưới bàn — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Với it nhắc lại món, câu mẫu sẽ giữ đại từ giữa pick và up. "The card remains the same item." Bài này không nói tới đón một người bằng xe; hai người đang gọi hành động nhặt một vật của trò chơi.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both compare noun-card model with pronoun reference, no passenger pickup target. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both compare noun-card model with pronoun reference, no passenger pickup target.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “pick up” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Với it nhắc lại món, câu mẫu sẽ giữ đại từ giữa pick và up. "The card remains the same item." Bài này không nói tới đón một người bằng xe; hai người đang gọi hành động nhặt một vật của trò chơi.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Nhặt thẻ đang nằm dưới bàn — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn đề nghị: "Let's pick it up." Cùng nhặt nó lên nhé. "Then it can return to the game box." Hai người kiểm lại tấm vừa lấy, đặt vào bộ của câu chuyện trước khi khép nắp.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Both return recovered card to defined fictional game set. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both return recovered card to defined fictional game set.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “Let's pick it up.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn đề nghị: "Let's pick it up." Cùng nhặt nó lên nhé. "Then it can return to the game box." Hai người kiểm lại tấm vừa lấy, đặt vào bộ của câu chuyện trước khi khép nắp.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Nhặt thẻ đang nằm dưới bàn — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn nhờ nhặt tấm thẻ đang ở dưới ghế. "Name the object to lift." Hãy nói: "Pick up the card."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold floor-card relation and full learner instruction. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold floor-card relation and full learner instruction.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Pick up the card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn nhờ nhặt tấm thẻ đang ở dưới ghế. "Name the object to lift." Hãy nói: "Pick up the card."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Nhặt thẻ đang nằm dưới bàn — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Pick up the card." Nhặt thẻ lên nhé. "The last item is no longer under the chair." Hai người đã có lại phần còn thiếu trong câu chuyện, kiểm bàn rồi cất trò chơi.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both store complete fictional card set after recovery. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both store complete fictional card set after recovery.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Pick up the card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Pick up the card." Nhặt thẻ lên nhé. "The last item is no longer under the chair." Hai người đã có lại phần còn thiếu trong câu chuyện, kiểm bàn rồi cất trò chơi.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Thẻ trên bàn đã đếm rồi, một tấm còn nằm dưới chân ghế! Pick up trong bài này là nhặt lên, cầm lên từ chỗ thấp. "Lift the item from where it is lying here." Bạn dọn trò chơi hư cấu, cần lấy lại món trước khi cất đủ bộ.
- R2 → SC01: Thẻ trên bàn đã đếm rồi, một tấm còn nằm dưới chân ghế! Pick up trong bài này là nhặt lên, cầm lên từ chỗ thấp. "Lift the item from where it is lying here." Bạn dọn trò chơi hư cấu, cần lấy lại món trước khi cất đủ bộ.
- R2 → SC02: Bạn nhờ: "Pick up the card." Nhặt thẻ lên nhé. "The one below the chair in our scene." Người bạn nhìn đúng tấm được nhắc, cúi lấy trong cảnh minh họa rồi đưa về chỗ các thẻ đã kiểm.
- R3 → SC02: Bạn nhờ: "Pick up the card." Nhặt thẻ lên nhé. "The one below the chair in our scene." Người bạn nhìn đúng tấm được nhắc, cúi lấy trong cảnh minh họa rồi đưa về chỗ các thẻ đã kiểm.
- R2 → SC03: Với it nhắc lại món, câu mẫu sẽ giữ đại từ giữa pick và up. "The card remains the same item." Bài này không nói tới đón một người bằng xe; hai người đang gọi hành động nhặt một vật của trò chơi.
- R3 → SC04: Bạn đề nghị: "Let's pick it up." Cùng nhặt nó lên nhé. "Then it can return to the game box." Hai người kiểm lại tấm vừa lấy, đặt vào bộ của câu chuyện trước khi khép nắp.
- R4 → SC05: Bạn muốn nhờ nhặt tấm thẻ đang ở dưới ghế. "Name the object to lift." Hãy nói: "Pick up the card."
- R4 → SC06: "Pick up the card." Nhặt thẻ lên nhé. "The last item is no longer under the chair." Hai người đã có lại phần còn thiếu trong câu chuyện, kiểm bàn rồi cất trò chơi.

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