# Kịch bản — vocab-fact-script-625 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-fact-script-625/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "sự thật (khoa học)" của từ FACT, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "sự thật (khoa học)" của FACT mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng FACT trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn FACT với các nghĩa khác của chính từ này

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
- Từ khoá duy nhất của video: FACT (n), chỉ dạy nghĩa "sự thật (khoa học)"
- Mức độ người học: CEFR A1; chủ đề: Khoa học và nghiên cứu
- Mã mục trong kho từ vựng: fact.n (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.
- Fact có cùng nghĩa lõi sự thật/dữ kiện có căn cứ trong ngữ cảnh khoa học và thường ngày. Hai mã kho tách ngữ cảnh, không phải hai nghĩa từ vựng loại trừ nhau. Bài này giữ ngữ cảnh dự án khoa học; không bịa số đo hoặc kết quả.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm medium; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.
- Làm rõ phạm vi trước chốt lời dẫn/neo ngày 01/10/2026.

6 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 64.6–107.66 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.01–18.35 |
| SC02 | 9.75–16.24 |
| SC03 | 11.2–18.67 |
| SC04 | 11.62–19.37 |
| SC05 | 9.4–15.66 |
| SC06 | 11.62–19.37 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Tài liệu cho một câu hỏi khoa học — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Đoán được rồi, có dữ kiện để kiểm chưa? Fact trong ngữ cảnh khoa học là sự thật, dữ kiện đã có căn cứ. "Something to check against evidence." Hai người chuẩn bị dự án hư cấu, phân biệt điều đang nghĩ với thông tin mình cần tìm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot compares hypothesis thought card with reference-book evidence question, companion keeps unresolved information separate. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot compares hypothesis thought card with reference-book evidence question, companion keeps unresolved information separate.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “fact” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Đoán được rồi, có dữ kiện để kiểm chưa? Fact trong ngữ cảnh khoa học là sự thật, dữ kiện đã có căn cứ. "Something to check against evidence." Hai người chuẩn bị dự án hư cấu, phân biệt điều đang nghĩ với thông tin mình cần tìm.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Tài liệu cho một câu hỏi khoa học — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn hỏi: "Is this a fact?" Đây có phải dữ kiện thật không? "What information supports it?" Người bạn nhìn câu vừa ghi rồi mở tài liệu của lớp, để hai người biết phần nào cần đối chiếu trước khi đưa vào bài.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Both compare fictional claim card with class reference material, no unsupported claim certified. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both compare fictional claim card with class reference material, no unsupported claim certified.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “Is this a fact?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Is this a fact?" Đây có phải dữ kiện thật không? "What information supports it?" Người bạn nhìn câu vừa ghi rồi mở tài liệu của lớp, để hai người biết phần nào cần đối chiếu trước khi đưa vào bài.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Tài liệu cho một câu hỏi khoa học — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Mẫu này dùng fact trong việc học khoa học, không coi mọi ý được viết trên giấy đều thành sự thật. "The question is part of checking." Hai người ghi chỗ cần hỏi người hướng dẫn, giữ những phần chưa có căn cứ ở nhóm câu hỏi của dự án.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both mark unresolved question icon separately from checked-material section, no real dataset or verification simulated. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both mark unresolved question icon separately from checked-material section, no real dataset or verification simulated.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “fact” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Mẫu này dùng fact trong việc học khoa học, không coi mọi ý được viết trên giấy đều thành sự thật. "The question is part of checking." Hai người ghi chỗ cần hỏi người hướng dẫn, giữ những phần chưa có căn cứ ở nhóm câu hỏi của dự án.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Tài liệu cho một câu hỏi khoa học — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn nói: "We need facts for our project." Chúng ta cần dữ kiện cho dự án. "We need more than our first guess." Bạn và người bạn chuẩn bị câu hỏi cùng tài liệu để mang tới buổi học hư cấu, chưa ghi một phép đo hay kết quả mình chưa làm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Mascot and companion gather project question cards and reference book for instructor discussion. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion gather project question cards and reference book for instructor discussion.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “We need facts for our project.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn nói: "We need facts for our project." Chúng ta cần dữ kiện cho dự án. "We need more than our first guess." Bạn và người bạn chuẩn bị câu hỏi cùng tài liệu để mang tới buổi học hư cấu, chưa ghi một phép đo hay kết quả mình chưa làm.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Tài liệu cho một câu hỏi khoa học — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn hỏi một điều đã ghi có phải dữ kiện thật trong ngữ cảnh khoa học. "Ask before using the statement." Hãy nói: "Is this a fact?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold fictional claim question and full learner prompt, no fake proof supplied. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional claim question and full learner prompt, no fake proof supplied.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Is this a fact?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn hỏi một điều đã ghi có phải dữ kiện thật trong ngữ cảnh khoa học. "Ask before using the statement." Hãy nói: "Is this a fact?"” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Tài liệu cho một câu hỏi khoa học — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Is this a fact?" Đây có phải dữ kiện thật không? "The question helps us keep track of what is known." Hai người mang phần chưa rõ tới người hướng dẫn của câu chuyện, có cách gọi thông tin cần căn cứ bằng fact mà chưa nhận suy đoán là kết quả.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both discuss unresolved fictional project question with adult instructor, evidence status remains honest. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both discuss unresolved fictional project question with adult instructor, evidence status remains honest.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Is this a fact?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Is this a fact?" Đây có phải dữ kiện thật không? "The question helps us keep track of what is known." Hai người mang phần chưa rõ tới người hướng dẫn của câu chuyện, có cách gọi thông tin cần căn cứ bằng fact mà chưa nhận suy đoán là kết quả.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.
- Người tham gia hoặc nhân vật bổ trợ: Adult additional participant or professional explicitly named in the scene. Preserve the same role and identity; do not add a person when the scene does not call for one. Minimal flat ink style and ordinary adult proportions.; Single plain lavender top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Đoán được rồi, có dữ kiện để kiểm chưa? Fact trong ngữ cảnh khoa học là sự thật, dữ kiện đã có căn cứ. "Something to check against evidence." Hai người chuẩn bị dự án hư cấu, phân biệt điều đang nghĩ với thông tin mình cần tìm.
- R2 → SC01: Đoán được rồi, có dữ kiện để kiểm chưa? Fact trong ngữ cảnh khoa học là sự thật, dữ kiện đã có căn cứ. "Something to check against evidence." Hai người chuẩn bị dự án hư cấu, phân biệt điều đang nghĩ với thông tin mình cần tìm.
- R2 → SC02: Bạn hỏi: "Is this a fact?" Đây có phải dữ kiện thật không? "What information supports it?" Người bạn nhìn câu vừa ghi rồi mở tài liệu của lớp, để hai người biết phần nào cần đối chiếu trước khi đưa vào bài.
- R3 → SC02: Bạn hỏi: "Is this a fact?" Đây có phải dữ kiện thật không? "What information supports it?" Người bạn nhìn câu vừa ghi rồi mở tài liệu của lớp, để hai người biết phần nào cần đối chiếu trước khi đưa vào bài.
- R2 → SC03: Mẫu này dùng fact trong việc học khoa học, không coi mọi ý được viết trên giấy đều thành sự thật. "The question is part of checking." Hai người ghi chỗ cần hỏi người hướng dẫn, giữ những phần chưa có căn cứ ở nhóm câu hỏi của dự án.
- R3 → SC04: Bạn nói: "We need facts for our project." Chúng ta cần dữ kiện cho dự án. "We need more than our first guess." Bạn và người bạn chuẩn bị câu hỏi cùng tài liệu để mang tới buổi học hư cấu, chưa ghi một phép đo hay kết quả mình chưa làm.
- R4 → SC05: Bạn muốn hỏi một điều đã ghi có phải dữ kiện thật trong ngữ cảnh khoa học. "Ask before using the statement." Hãy nói: "Is this a fact?"
- R4 → SC06: "Is this a fact?" Đây có phải dữ kiện thật không? "The question helps us keep track of what is known." Hai người mang phần chưa rõ tới người hướng dẫn của câu chuyện, có cách gọi thông tin cần căn cứ bằng fact mà chưa nhận suy đoán là kết quả.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 18099: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 625: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 18099 — addressed: Đã rà 3 giây đầu: mở bằng “Đoán được rồi, có dữ kiện để kiểm chưa?”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response