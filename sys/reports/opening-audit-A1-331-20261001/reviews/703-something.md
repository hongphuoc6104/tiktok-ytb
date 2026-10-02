# Kịch bản — vocab-something-script-703 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-something-script-703/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "thứ gì đó" của từ SOMETHING, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "thứ gì đó" của SOMETHING mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng SOMETHING trong ít nhất một câu
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
- Từ khoá duy nhất của video: SOMETHING (pron), chỉ dạy nghĩa "thứ gì đó"
- Mức độ người học: CEFR A1; chủ đề: Từ chức năng và liên kết
- Mã mục trong kho từ vựng: something.pron (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm medium; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

6 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 56.8–94.66 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.65–16.08 |
| SC02 | 9.75–16.24 |
| SC03 | 9.63–16.06 |
| SC04 | 8.5–14.16 |
| SC05 | 9.73–16.22 |
| SC06 | 9.54–15.9 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Trong hộp còn một món chưa biết tên — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Hộp tưởng rỗng, còn một món kìa! Something nghĩa là thứ gì đó. "A thing whose name we have not given yet." Bạn dọn trò chơi hư cấu với người bạn, muốn nhắc có một món cần kiểm trước khi cất hộp.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot tilts open game box to reveal last harmless piece tucked in corner, companion notices it. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot tilts open game box to reveal last harmless piece tucked in corner, companion notices it.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “something” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Hộp tưởng rỗng, còn một món kìa! Something nghĩa là thứ gì đó. "A thing whose name we have not given yet." Bạn dọn trò chơi hư cấu với người bạn, muốn nhắc có một món cần kiểm trước khi cất hộp.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Trong hộp còn một món chưa biết tên — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nói: "There's something in the box." Có thứ gì đó trong hộp. "An item is still inside here." Người bạn mở phần nắp trong câu chuyện, để hai người nhìn món còn lại thay vì tự nhận hộp đã không có gì.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Both look inside defined box for remaining partly hidden token. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both look inside defined box for remaining partly hidden token.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “There's something in the box.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "There's something in the box." Có thứ gì đó trong hộp. "An item is still inside here." Người bạn mở phần nắp trong câu chuyện, để hai người nhìn món còn lại thay vì tự nhận hộp đã không có gì.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Trong hộp còn một món chưa biết tên — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Something chưa gọi tên chính xác đối tượng. "We can find out what it is next." Bạn vẫn giữ rõ vật chứa và điều đã thấy, không lấy chữ something để báo chắc món gì khi chưa nhìn đủ phần của câu chuyện.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both examine hidden corner without guessing specific token identity prematurely. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both examine hidden corner without guessing specific token identity prematurely.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “something” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Something chưa gọi tên chính xác đối tượng. "We can find out what it is next." Bạn vẫn giữ rõ vật chứa và điều đã thấy, không lấy chữ something để báo chắc món gì khi chưa nhìn đủ phần của câu chuyện.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Trong hộp còn một món chưa biết tên — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn nói: "I found something." Tôi tìm thấy một thứ. "The item is now in view." Bạn lấy món của trò hư cấu ra cho người bạn xem, rồi nhận được tên và chỗ nó thuộc về.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Mascot reveals remaining fictional game token to companion. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot reveals remaining fictional game token to companion.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “I found something.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn nói: "I found something." Tôi tìm thấy một thứ. "The item is now in view." Bạn lấy món của trò hư cấu ra cho người bạn xem, rồi nhận được tên và chỗ nó thuộc về.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Trong hộp còn một món chưa biết tên — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn nói có một thứ trong hộp khi chưa gọi tên. "Keep the object unnamed for this moment." Hãy nói: "There's something in the box."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold box with partly visible object and full learner sentence. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold box with partly visible object and full learner sentence.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Keep the object unnamed for this moment.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “There's something in the box.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn nói có một thứ trong hộp khi chưa gọi tên. "Keep the object unnamed for this moment." Hãy nói: "There's something in the box."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Trong hộp còn một món chưa biết tên — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"There's something in the box." Có thứ gì đó trong hộp. "The last item has not been packed away by mistake." Hai người đã nhận ra món còn lại và trả về đúng phần trò chơi, khép hộp sau khi kiểm xong.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both return revealed token to appropriate game set and close checked box. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both return revealed token to appropriate game set and close checked box.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “There's something in the box.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"There's something in the box." Có thứ gì đó trong hộp. "The last item has not been packed away by mistake." Hai người đã nhận ra món còn lại và trả về đúng phần trò chơi, khép hộp sau khi kiểm xong.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Hộp tưởng rỗng, còn một món kìa! Something nghĩa là thứ gì đó. "A thing whose name we have not given yet." Bạn dọn trò chơi hư cấu với người bạn, muốn nhắc có một món cần kiểm trước khi cất hộp.
- R2 → SC01: Hộp tưởng rỗng, còn một món kìa! Something nghĩa là thứ gì đó. "A thing whose name we have not given yet." Bạn dọn trò chơi hư cấu với người bạn, muốn nhắc có một món cần kiểm trước khi cất hộp.
- R2 → SC02: Bạn nói: "There's something in the box." Có thứ gì đó trong hộp. "An item is still inside here." Người bạn mở phần nắp trong câu chuyện, để hai người nhìn món còn lại thay vì tự nhận hộp đã không có gì.
- R3 → SC02: Bạn nói: "There's something in the box." Có thứ gì đó trong hộp. "An item is still inside here." Người bạn mở phần nắp trong câu chuyện, để hai người nhìn món còn lại thay vì tự nhận hộp đã không có gì.
- R2 → SC03: Something chưa gọi tên chính xác đối tượng. "We can find out what it is next." Bạn vẫn giữ rõ vật chứa và điều đã thấy, không lấy chữ something để báo chắc món gì khi chưa nhìn đủ phần của câu chuyện.
- R3 → SC04: Bạn nói: "I found something." Tôi tìm thấy một thứ. "The item is now in view." Bạn lấy món của trò hư cấu ra cho người bạn xem, rồi nhận được tên và chỗ nó thuộc về.
- R4 → SC05: Bạn muốn nói có một thứ trong hộp khi chưa gọi tên. "Keep the object unnamed for this moment." Hãy nói: "There's something in the box."
- R4 → SC06: "There's something in the box." Có thứ gì đó trong hộp. "The last item has not been packed away by mistake." Hai người đã nhận ra món còn lại và trả về đúng phần trò chơi, khép hộp sau khi kiểm xong.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 18509: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 703: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 18509 — addressed: Đã rà 3 giây đầu: mở bằng “Hộp tưởng rỗng, còn một món kìa!”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response