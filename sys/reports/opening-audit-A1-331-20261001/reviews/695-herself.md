# Kịch bản — vocab-herself-script-695 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-herself-script-695/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "chính cô ấy" của từ HERSELF, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "chính cô ấy" của HERSELF mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng HERSELF trong ít nhất một câu
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
- Từ khoá duy nhất của video: HERSELF (pron), chỉ dạy nghĩa "chính cô ấy"
- Mức độ người học: CEFR A1; chủ đề: Từ chức năng và liên kết
- Mã mục trong kho từ vựng: herself.pron (dùng để đánh dấu đã làm)
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

VI: 56.26–93.75 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.54–15.9 |
| SC02 | 9.33–15.55 |
| SC03 | 10.37–17.28 |
| SC04 | 9.75–16.24 |
| SC05 | 8.15–13.58 |
| SC06 | 9.12–15.2 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Chị Lan làm phần bánh cho nhóm — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Chị Lan tự làm món này mang tới! Herself trong mẫu này nhấn chính cô ấy. "The same female person did the task here." Bạn và người bạn dự buổi gặp hư cấu, nghe người làm món kể về phần của mình.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Female Lan presents self-made food box to mascot and companion, no health claims or real personal data. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Female Lan presents self-made food box to mascot and companion, no health claims or real personal data.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “herself” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Chị Lan tự làm món này mang tới! Herself trong mẫu này nhấn chính cô ấy. "The same female person did the task here." Bạn và người bạn dự buổi gặp hư cấu, nghe người làm món kể về phần của mình.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Chị Lan làm phần bánh cho nhóm — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nhắc lại: "She made it herself." Cô ấy tự làm nó. "She is Lan in this story." Người bạn nghe đã được giới thiệu với chị Lan, nên biết mình đang hỏi về đúng người và món đã được nhắc.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot identifies fictional Lan as stated maker, box kept closed for presentation. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot identifies fictional Lan as stated maker, box kept closed for presentation.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “She made it herself.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhắc lại: "She made it herself." Cô ấy tự làm nó. "She is Lan in this story." Người bạn nghe đã được giới thiệu với chị Lan, nên biết mình đang hỏi về đúng người và món đã được nhắc.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Chị Lan làm phần bánh cho nhóm — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Herself quay về she trong lời nhấn này. "It is about that person's own action." Hai người nghe việc chị Lan kể, không suy ai đã làm từ kiểu hộp hoặc màu khăn trên bàn; những chi tiết ấy không thay cho lời của người làm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Lan explains stated contribution while mascot and companion listen, no inference solely from decoration. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Lan explains stated contribution while mascot and companion listen, no inference solely from decoration.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “herself” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Herself quay về she trong lời nhấn này. "It is about that person's own action." Hai người nghe việc chị Lan kể, không suy ai đã làm từ kiểu hộp hoặc màu khăn trên bàn; những chi tiết ấy không thay cho lời của người làm.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Chị Lan làm phần bánh cho nhóm — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn kể thêm: "She packed it herself." Cô ấy tự gói nó. "The box was part of her preparation too." Chị Lan đặt món vào chỗ của buổi gặp hư cấu, để nhóm chia phần sau khi đã biết điều mình muốn hỏi.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Fictional Lan places self-packed cake box at shared gathering table. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Fictional Lan places self-packed cake box at shared gathering table.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “She packed it herself.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn kể thêm: "She packed it herself." Cô ấy tự gói nó. "The box was part of her preparation too." Chị Lan đặt món vào chỗ của buổi gặp hư cấu, để nhóm chia phần sau khi đã biết điều mình muốn hỏi.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Chị Lan làm phần bánh cho nhóm — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn đóng vai người kể chị Lan tự chuẩn bị món. "Say who did this work." Hãy nói: "She made it herself."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold fictional female maker and full learner sentence. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional female maker and full learner sentence.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “She made it herself.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn đóng vai người kể chị Lan tự chuẩn bị món. "Say who did this work." Hãy nói: "She made it herself."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Chị Lan làm phần bánh cho nhóm — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"She made it herself." Cô ấy tự làm nó. "The people have heard the maker's story." Buổi gặp hư cấu đã có phần chị Lan mang tới và lời kể rõ về người thực hiện, nhóm tiếp tục trò chuyện.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Mascot and companion thank fictional Lan and prepare shared gathering table. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion thank fictional Lan and prepare shared gathering table.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “She made it herself.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"She made it herself." Cô ấy tự làm nó. "The people have heard the maker's story." Buổi gặp hư cấu đã có phần chị Lan mang tới và lời kể rõ về người thực hiện, nhóm tiếp tục trò chuyện.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult companion who listens or helps with the current task. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.
- Người tham gia hoặc nhân vật bổ trợ: Fictional adult female Lan, identified participant or recipient, keep her identity throughout. Minimal flat ink style and ordinary adult proportions.; Single plain lavender top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Chị Lan tự làm món này mang tới! Herself trong mẫu này nhấn chính cô ấy. "The same female person did the task here." Bạn và người bạn dự buổi gặp hư cấu, nghe người làm món kể về phần của mình.
- R2 → SC01: Chị Lan tự làm món này mang tới! Herself trong mẫu này nhấn chính cô ấy. "The same female person did the task here." Bạn và người bạn dự buổi gặp hư cấu, nghe người làm món kể về phần của mình.
- R2 → SC02: Bạn nhắc lại: "She made it herself." Cô ấy tự làm nó. "She is Lan in this story." Người bạn nghe đã được giới thiệu với chị Lan, nên biết mình đang hỏi về đúng người và món đã được nhắc.
- R3 → SC02: Bạn nhắc lại: "She made it herself." Cô ấy tự làm nó. "She is Lan in this story." Người bạn nghe đã được giới thiệu với chị Lan, nên biết mình đang hỏi về đúng người và món đã được nhắc.
- R2 → SC03: Herself quay về she trong lời nhấn này. "It is about that person's own action." Hai người nghe việc chị Lan kể, không suy ai đã làm từ kiểu hộp hoặc màu khăn trên bàn; những chi tiết ấy không thay cho lời của người làm.
- R3 → SC04: Bạn kể thêm: "She packed it herself." Cô ấy tự gói nó. "The box was part of her preparation too." Chị Lan đặt món vào chỗ của buổi gặp hư cấu, để nhóm chia phần sau khi đã biết điều mình muốn hỏi.
- R4 → SC05: Bạn đóng vai người kể chị Lan tự chuẩn bị món. "Say who did this work." Hãy nói: "She made it herself."
- R4 → SC06: "She made it herself." Cô ấy tự làm nó. "The people have heard the maker's story." Buổi gặp hư cấu đã có phần chị Lan mang tới và lời kể rõ về người thực hiện, nhóm tiếp tục trò chuyện.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 18469: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 695: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 18469 — addressed: Đã rà 3 giây đầu: mở bằng “Chị Lan tự làm món này mang tới!”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response