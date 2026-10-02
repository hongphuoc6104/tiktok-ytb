# Kịch bản — vocab-look-script-673 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-look-script-673/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "trông có vẻ" của từ LOOK, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "trông có vẻ" của LOOK mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng LOOK trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn LOOK với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "look" còn nghĩa khác: cái nhìn, ánh mắt [n, look.n.glance-noun]. Video này KHÔNG dạy nghĩa đó.
- Từ "look" còn nghĩa khác: vẻ ngoài, phong cách (a new look) [n, look.n.appearance]. Video này KHÔNG dạy nghĩa đó.
- Từ "look" còn nghĩa khác: nhìn [v, look.v.glance]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: LOOK (v), chỉ dạy nghĩa "trông có vẻ"
- Mức độ người học: CEFR A1; chủ đề: Động từ thông dụng
- Mã mục trong kho từ vựng: look.v.appear-look (dùng để đánh dấu đã làm)
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

VI: 59.2–98.66 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.69–17.82 |
| SC02 | 8.91–14.85 |
| SC03 | 10.79–17.98 |
| SC04 | 9.54–15.9 |
| SC05 | 8.9–14.83 |
| SC06 | 10.37–17.28 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Chiếc túi trông có vẻ nặng — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Trông nặng thôi, mình chưa thử nhấc túi. Look trong bài này là trông có vẻ. "An impression from what we see." Bạn chuẩn bị đồ hư cấu với người bạn, muốn nói cảm nhận ban đầu mà chưa nhận nó là một kết quả đã kiểm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Full-looking bag on table, mascot observes without lifting, companion prepares to inspect actual contents. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Full-looking bag on table, mascot observes without lifting, companion prepares to inspect actual contents.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “look” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Trông nặng thôi, mình chưa thử nhấc túi. Look trong bài này là trông có vẻ. "An impression from what we see." Bạn chuẩn bị đồ hư cấu với người bạn, muốn nói cảm nhận ban đầu mà chưa nhận nó là một kết quả đã kiểm.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Chiếc túi trông có vẻ nặng — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nói: "The bag looks heavy." Túi trông có vẻ nặng. "That is my first impression here." Người bạn nghe rồi mở phần đồ của câu chuyện, để hai người xem bên trong trước khi quyết định ai mang.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Companion opens bag and reveals fictional contents after mascot states visual impression. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion opens bag and reveals fictional contents after mascot states visual impression.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “The bag looks heavy.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "The bag looks heavy." Túi trông có vẻ nặng. "That is my first impression here." Người bạn nghe rồi mở phần đồ của câu chuyện, để hai người xem bên trong trước khi quyết định ai mang.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Chiếc túi trông có vẻ nặng — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Looks ở mẫu này đi với điều được nhận xét, không phải lời nhờ nhìn vào một món. "We are describing how it appears." Bạn vẫn có thể hỏi hoặc kiểm thực tế; nhìn một cái túi không tự cho biết khối lượng đúng trong mọi tình huống.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both distinguish visual impression from checking bag contents, no fabricated measurement. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both distinguish visual impression from checking bag contents, no fabricated measurement.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “look” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Looks ở mẫu này đi với điều được nhận xét, không phải lời nhờ nhìn vào một món. "We are describing how it appears." Bạn vẫn có thể hỏi hoặc kiểm thực tế; nhìn một cái túi không tự cho biết khối lượng đúng trong mọi tình huống.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Chiếc túi trông có vẻ nặng — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn hỏi: "Does it look heavy to you?" Với bạn nó có trông nặng không? "What is your impression of this bag?" Người bạn kể điều họ thấy, hai người so với phần đồ rồi chia lại để mang trong câu chuyện.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Both compare impressions with open bag contents and divide carrying roles. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both compare impressions with open bag contents and divide carrying roles.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “Does it look heavy to you?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn hỏi: "Does it look heavy to you?" Với bạn nó có trông nặng không? "What is your impression of this bag?" Người bạn kể điều họ thấy, hai người so với phần đồ rồi chia lại để mang trong câu chuyện.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Chiếc túi trông có vẻ nặng — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn nói chiếc túi có vẻ nặng theo vai. "Keep the impression in the sentence." Hãy nói: "The bag looks heavy."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold packed bag and full learner sentence, no actual weight certified. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold packed bag and full learner sentence, no actual weight certified.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Keep the impression in the sentence.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “The bag looks heavy.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn nói chiếc túi có vẻ nặng theo vai. "Keep the impression in the sentence." Hãy nói: "The bag looks heavy."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Chiếc túi trông có vẻ nặng — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"The bag looks heavy." Túi trông có vẻ nặng. "We can still check what we are going to carry." Hai người đã nói rõ mức nhận xét ban đầu rồi chuẩn bị phần đồ, không đổi một chữ looks thành lời chắc chắn về khối lượng.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both pack checked fictional portions into separate bags. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both pack checked fictional portions into separate bags.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “The bag looks heavy.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"The bag looks heavy." Túi trông có vẻ nặng. "We can still check what we are going to carry." Hai người đã nói rõ mức nhận xét ban đầu rồi chuẩn bị phần đồ, không đổi một chữ looks thành lời chắc chắn về khối lượng.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Trông nặng thôi, mình chưa thử nhấc túi. Look trong bài này là trông có vẻ. "An impression from what we see." Bạn chuẩn bị đồ hư cấu với người bạn, muốn nói cảm nhận ban đầu mà chưa nhận nó là một kết quả đã kiểm.
- R2 → SC01: Trông nặng thôi, mình chưa thử nhấc túi. Look trong bài này là trông có vẻ. "An impression from what we see." Bạn chuẩn bị đồ hư cấu với người bạn, muốn nói cảm nhận ban đầu mà chưa nhận nó là một kết quả đã kiểm.
- R2 → SC02: Bạn nói: "The bag looks heavy." Túi trông có vẻ nặng. "That is my first impression here." Người bạn nghe rồi mở phần đồ của câu chuyện, để hai người xem bên trong trước khi quyết định ai mang.
- R3 → SC02: Bạn nói: "The bag looks heavy." Túi trông có vẻ nặng. "That is my first impression here." Người bạn nghe rồi mở phần đồ của câu chuyện, để hai người xem bên trong trước khi quyết định ai mang.
- R2 → SC03: Looks ở mẫu này đi với điều được nhận xét, không phải lời nhờ nhìn vào một món. "We are describing how it appears." Bạn vẫn có thể hỏi hoặc kiểm thực tế; nhìn một cái túi không tự cho biết khối lượng đúng trong mọi tình huống.
- R3 → SC04: Bạn hỏi: "Does it look heavy to you?" Với bạn nó có trông nặng không? "What is your impression of this bag?" Người bạn kể điều họ thấy, hai người so với phần đồ rồi chia lại để mang trong câu chuyện.
- R4 → SC05: Bạn muốn nói chiếc túi có vẻ nặng theo vai. "Keep the impression in the sentence." Hãy nói: "The bag looks heavy."
- R4 → SC06: "The bag looks heavy." Túi trông có vẻ nặng. "We can still check what we are going to carry." Hai người đã nói rõ mức nhận xét ban đầu rồi chuẩn bị phần đồ, không đổi một chữ looks thành lời chắc chắn về khối lượng.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 18349: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 673: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 18349 — addressed: Đã rà 3 giây đầu: mở bằng “Trông nặng thôi, mình chưa thử nhấc túi.”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response