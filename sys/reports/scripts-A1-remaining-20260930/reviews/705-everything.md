# Kịch bản — vocab-everything-script-705 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-everything-script-705/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "mọi thứ" của từ EVERYTHING, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "mọi thứ" của EVERYTHING mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng EVERYTHING trong ít nhất một câu
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
- Từ khoá duy nhất của video: EVERYTHING (pron), chỉ dạy nghĩa "mọi thứ"
- Mức độ người học: CEFR A1; chủ đề: Từ chức năng và liên kết
- Mã mục trong kho từ vựng: everything.pron (dùng để đánh dấu đã làm)
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

VI: 59.94–99.89 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.64–19.4 |
| SC02 | 9.95–16.59 |
| SC03 | 10.79–17.98 |
| SC04 | 9.75–16.24 |
| SC05 | 8.69–14.48 |
| SC06 | 9.12–15.2 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Mọi món trong phần đã chọn đều có chỗ — Nhịp 1

Mục đích: Make the selected sense useful in a concrete situation.

Ba món của bộ đã bày, bạn muốn kiểm cả phần chứ không riêng một cây bút! Everything nghĩa là mọi thứ. "All the things in the group we are talking about." Bạn chuẩn bị bộ dụng cụ hư cấu, đã chọn giấy, bút và thước cho công việc trên bàn.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion inspect fictional set of paper pen ruler and storage box. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion inspect fictional set of paper pen ruler and storage box.

Lý do: Make the selected sense useful in a concrete situation.

Chữ được phép: “everything” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Ba món của bộ đã bày, bạn muốn kiểm cả phần chứ không riêng một cây bút! Everything nghĩa là mọi thứ. "All the things in the group we are talking about." Bạn chuẩn bị bộ dụng cụ hư cấu, đã chọn giấy, bút và thước cho công việc trên bàn.” (lần 1) · Make the selected sense useful in a concrete situation.

## SC02 — Mọi món trong phần đã chọn đều có chỗ — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn hỏi: "Is everything here?" Mọi thứ có ở đây chưa? "Have we got all the items on this list?" Người bạn kiểm từng món của bộ, giữ phạm vi theo phần cần chuẩn bị chứ không theo tất cả đồ trong căn phòng.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Companion checks defined three-item fictional supply list against visible objects. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion checks defined three-item fictional supply list against visible objects.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “Is everything here?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Is everything here?" Mọi thứ có ở đây chưa? "Have we got all the items on this list?" Người bạn kiểm từng món của bộ, giữ phạm vi theo phần cần chuẩn bị chứ không theo tất cả đồ trong căn phòng.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Mọi món trong phần đã chọn đều có chỗ — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Everything dùng như một chủ ngữ số ít trong mẫu này, nên đi với is. "The sentence covers the whole set we named." Hai người vẫn cần biết set gồm gì trước khi trả lời, không dùng một chữ everything để bỏ qua phần chưa được liệt kê.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both keep defined set separate from unrelated room props. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both keep defined set separate from unrelated room props.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “everything” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Everything dùng như một chủ ngữ số ít trong mẫu này, nên đi với is. "The sentence covers the whole set we named." Hai người vẫn cần biết set gồm gì trước khi trả lời, không dùng một chữ everything để bỏ qua phần chưa được liệt kê.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Mọi món trong phần đã chọn đều có chỗ — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn nói: "Everything is in the box." Mọi thứ đều ở trong hộp. "All the items of this set are inside now." Người bạn nhìn lại bộ vừa cất, hai người khép nắp sau khi xác nhận phần của câu chuyện đã đủ.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — All defined paper pen ruler items packed inside fictional box, unrelated props outside. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: All defined paper pen ruler items packed inside fictional box, unrelated props outside.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “Everything is in the box.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn nói: "Everything is in the box." Mọi thứ đều ở trong hộp. "All the items of this set are inside now." Người bạn nhìn lại bộ vừa cất, hai người khép nắp sau khi xác nhận phần của câu chuyện đã đủ.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Mọi món trong phần đã chọn đều có chỗ — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn hỏi cả bộ đồ đã chọn có mặt chưa. "Ask about the whole set." Hãy nói: "Is everything here?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold defined supply set and full learner question. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold defined supply set and full learner question.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Ask about the whole set.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “Is everything here?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn hỏi cả bộ đồ đã chọn có mặt chưa. "Ask about the whole set." Hãy nói: "Is everything here?"” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Mọi món trong phần đã chọn đều có chỗ — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Is everything here?" Mọi thứ có ở đây chưa? "The set is ready for the task we chose." Hai người đã kiểm đúng phạm vi và cất bộ dụng cụ hư cấu, mang hộp tới phần hoạt động kế tiếp.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both carry checked fictional supply box to task area. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both carry checked fictional supply box to task area.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Is everything here?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Is everything here?" Mọi thứ có ở đây chưa? "The set is ready for the task we chose." Hai người đã kiểm đúng phạm vi và cất bộ dụng cụ hư cấu, mang hộp tới phần hoạt động kế tiếp.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Ba món của bộ đã bày, bạn muốn kiểm cả phần chứ không riêng một cây bút! Everything nghĩa là mọi thứ. "All the things in the group we are talking about." Bạn chuẩn bị bộ dụng cụ hư cấu, đã chọn giấy, bút và thước cho công việc trên bàn.
- R2 → SC01: Ba món của bộ đã bày, bạn muốn kiểm cả phần chứ không riêng một cây bút! Everything nghĩa là mọi thứ. "All the things in the group we are talking about." Bạn chuẩn bị bộ dụng cụ hư cấu, đã chọn giấy, bút và thước cho công việc trên bàn.
- R2 → SC02: Bạn hỏi: "Is everything here?" Mọi thứ có ở đây chưa? "Have we got all the items on this list?" Người bạn kiểm từng món của bộ, giữ phạm vi theo phần cần chuẩn bị chứ không theo tất cả đồ trong căn phòng.
- R3 → SC02: Bạn hỏi: "Is everything here?" Mọi thứ có ở đây chưa? "Have we got all the items on this list?" Người bạn kiểm từng món của bộ, giữ phạm vi theo phần cần chuẩn bị chứ không theo tất cả đồ trong căn phòng.
- R2 → SC03: Everything dùng như một chủ ngữ số ít trong mẫu này, nên đi với is. "The sentence covers the whole set we named." Hai người vẫn cần biết set gồm gì trước khi trả lời, không dùng một chữ everything để bỏ qua phần chưa được liệt kê.
- R3 → SC04: Bạn nói: "Everything is in the box." Mọi thứ đều ở trong hộp. "All the items of this set are inside now." Người bạn nhìn lại bộ vừa cất, hai người khép nắp sau khi xác nhận phần của câu chuyện đã đủ.
- R4 → SC05: Bạn muốn hỏi cả bộ đồ đã chọn có mặt chưa. "Ask about the whole set." Hãy nói: "Is everything here?"
- R4 → SC06: "Is everything here?" Mọi thứ có ở đây chưa? "The set is ready for the task we chose." Hai người đã kiểm đúng phạm vi và cất bộ dụng cụ hư cấu, mang hộp tới phần hoạt động kế tiếp.

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