# Kịch bản — vocab-gram-script-463 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-gram-script-463/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "gam" của từ GRAM, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "gam" của GRAM mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng GRAM trong ít nhất một câu
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
- Từ khoá duy nhất của video: GRAM (n), chỉ dạy nghĩa "gam"
- Mức độ người học: CEFR A1; chủ đề: Thời gian, số lượng, đo lường
- Mã mục trong kho từ vựng: gram.n (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm short; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 43.95–73.23 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.65–16.08 |
| SC02 | 8.08–13.47 |
| SC03 | 8.29–13.81 |
| SC04 | 10.68–17.79 |
| SC05 | 7.25–12.08 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Đừng đổ hết túi bột vào cân — Nhịp 1

Mục đích: Introduce a concrete need and the selected sense.

Cả túi lớn thế này, mình chỉ cần một phần nhỏ! Gram là gam. "A unit of weight." Bạn pha hỗn hợp cho mô hình trong bài thủ công, người bạn đặt cân lên bàn để lấy lượng bột của kế hoạch.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot holds large craft-powder bag above bowl on scale, friend has fictional recipe card. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot holds large craft-powder bag above bowl on scale, friend has fictional recipe card.

Lý do: Introduce a concrete need and the selected sense.

Chữ được phép: “gram” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Cả túi lớn thế này, mình chỉ cần một phần nhỏ! Gram là gam. "A unit of weight." Bạn pha hỗn hợp cho mô hình trong bài thủ công, người bạn đặt cân lên bàn để lấy lượng bột của kế hoạch.” (lần 1) · Introduce a concrete need and the selected sense.

## SC02 — Đừng đổ hết túi bột vào cân — Nhịp 2

Mục đích: Make the first model an action in the situation.

Người bạn nói: "We need a hundred grams." Chúng ta cần một trăm gam. "Only the amount for this task." Bạn đổ từng phần vào bát, chưa dùng hết túi chỉ vì túi đã mở.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot gradually pours craft powder into bowl on scale, unapproved numerals absent. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot gradually pours craft powder into bowl on scale, unapproved numerals absent.

Lý do: Make the first model an action in the situation.

Chữ được phép: “We need a hundred grams.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Người bạn nói: "We need a hundred grams." Chúng ta cần một trăm gam. "Only the amount for this task." Bạn đổ từng phần vào bát, chưa dùng hết túi chỉ vì túi đã mở.” (lần 1) · Make the first model an action in the situation.

## SC03 — Đừng đổ hết túi bột vào cân — Nhịp 3

Mục đích: Advance the same story with the second model.

Bạn hỏi: "How many grams are left?" Còn bao nhiêu gam nữa? "Check before adding more." Người bạn nhìn cân và phần kế hoạch, rồi nhắc bạn dừng khi lượng dành cho mô hình đã đủ.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend compares scale and craft plan as mascot holds powder bag still. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend compares scale and craft plan as mascot holds powder bag still.

Lý do: Advance the same story with the second model.

Chữ được phép: “How many grams are left?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn hỏi: "How many grams are left?" Còn bao nhiêu gam nữa? "Check before adding more." Người bạn nhìn cân và phần kế hoạch, rồi nhắc bạn dừng khi lượng dành cho mô hình đã đủ.” (lần 1) · Advance the same story with the second model.

## SC04 — Đừng đổ hết túi bột vào cân — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn nói lượng cần theo vai trong bài. "Name the amount." Hundred grams là một trăm gam. Nói như lúc chuẩn bị vật liệu: "We need a hundred grams."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold craft materials and full sentence, no food or medical measurement guidance. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold craft materials and full sentence, no food or medical measurement guidance.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Name the amount.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “We need a hundred grams.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nói lượng cần theo vai trong bài. "Name the amount." Hundred grams là một trăm gam. Nói như lúc chuẩn bị vật liệu: "We need a hundred grams."” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Đừng đổ hết túi bột vào cân — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"We need a hundred grams." Cần một trăm gam. "The rest stays in the bag." Phần bột cho mô hình đã được lấy riêng, bạn đóng túi lại để dùng sau.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot seals remaining craft powder and places measured bowl beside model supplies. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot seals remaining craft powder and places measured bowl beside model supplies.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “We need a hundred grams.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"We need a hundred grams." Cần một trăm gam. "The rest stays in the bag." Phần bột cho mô hình đã được lấy riêng, bạn đóng túi lại để dùng sau.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Cả túi lớn thế này, mình chỉ cần một phần nhỏ! Gram là gam. "A unit of weight." Bạn pha hỗn hợp cho mô hình trong bài thủ công, người bạn đặt cân lên bàn để lấy lượng bột của kế hoạch.
- R2 → SC01: Cả túi lớn thế này, mình chỉ cần một phần nhỏ! Gram là gam. "A unit of weight." Bạn pha hỗn hợp cho mô hình trong bài thủ công, người bạn đặt cân lên bàn để lấy lượng bột của kế hoạch.
- R2 → SC02: Người bạn nói: "We need a hundred grams." Chúng ta cần một trăm gam. "Only the amount for this task." Bạn đổ từng phần vào bát, chưa dùng hết túi chỉ vì túi đã mở.
- R3 → SC02: Người bạn nói: "We need a hundred grams." Chúng ta cần một trăm gam. "Only the amount for this task." Bạn đổ từng phần vào bát, chưa dùng hết túi chỉ vì túi đã mở.
- R3 → SC03: Bạn hỏi: "How many grams are left?" Còn bao nhiêu gam nữa? "Check before adding more." Người bạn nhìn cân và phần kế hoạch, rồi nhắc bạn dừng khi lượng dành cho mô hình đã đủ.
- R4 → SC04: Bạn muốn nói lượng cần theo vai trong bài. "Name the amount." Hundred grams là một trăm gam. Nói như lúc chuẩn bị vật liệu: "We need a hundred grams."
- R4 → SC05: "We need a hundred grams." Cần một trăm gam. "The rest stays in the bag." Phần bột cho mô hình đã được lấy riêng, bạn đóng túi lại để dùng sau.

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