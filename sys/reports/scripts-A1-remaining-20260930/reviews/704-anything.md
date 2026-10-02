# Kịch bản — vocab-anything-script-704 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-anything-script-704/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "bất cứ thứ gì" của từ ANYTHING, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "bất cứ thứ gì" của ANYTHING mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng ANYTHING trong ít nhất một câu
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
- Từ khoá duy nhất của video: ANYTHING (pron), chỉ dạy nghĩa "bất cứ thứ gì"
- Mức độ người học: CEFR A1; chủ đề: Từ chức năng và liên kết
- Mã mục trong kho từ vựng: anything.pron (dùng để đánh dấu đã làm)
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

VI: 60.21–100.34 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.2–18.67 |
| SC02 | 11.32–18.86 |
| SC03 | 10.26–17.1 |
| SC04 | 8.91–14.85 |
| SC05 | 8.77–14.62 |
| SC06 | 9.75–16.24 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Hỏi có bất cứ thứ gì còn trong túi — Nhịp 1

Mục đích: Make the selected sense useful in a concrete situation.

Đồ trên bàn đã cất, trong túi còn bất cứ món nào của lớp không? Anything nghĩa là bất cứ thứ gì trong mẫu hỏi này. "We have not selected a particular object." Bạn cùng người bạn kiểm phần còn lại của hoạt động hư cấu trước khi rời bàn.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion inspect bag after fictional craft-class packing. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion inspect bag after fictional craft-class packing.

Lý do: Make the selected sense useful in a concrete situation.

Chữ được phép: “anything” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Đồ trên bàn đã cất, trong túi còn bất cứ món nào của lớp không? Anything nghĩa là bất cứ thứ gì trong mẫu hỏi này. "We have not selected a particular object." Bạn cùng người bạn kiểm phần còn lại của hoạt động hư cấu trước khi rời bàn.” (lần 1) · Make the selected sense useful in a concrete situation.

## SC02 — Hỏi có bất cứ thứ gì còn trong túi — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn hỏi: "Is there anything in the bag?" Trong túi có thứ gì không? "We are checking for any item, not one named thing." Người bạn mở túi để xem, câu hỏi cho họ biết bạn muốn kiểm phần bên trong chứ không chỉ một cây bút đã nói trước.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Companion checks bag interior for remaining class items. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion checks bag interior for remaining class items.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “Is there anything in the bag?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Is there anything in the bag?" Trong túi có thứ gì không? "We are checking for any item, not one named thing." Người bạn mở túi để xem, câu hỏi cho họ biết bạn muốn kiểm phần bên trong chứ không chỉ một cây bút đã nói trước.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Hỏi có bất cứ thứ gì còn trong túi — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Anything giúp giữ câu hỏi mở về đồ vật trong tình huống. "The answer can name an item or say there is none." Bạn chưa lấy việc túi nhẹ làm chắc nó rỗng; hai người nhìn phần của câu chuyện rồi mới kể điều còn lại.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both examine interior rather than infer from bag shape or weight. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both examine interior rather than infer from bag shape or weight.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “anything” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Anything giúp giữ câu hỏi mở về đồ vật trong tình huống. "The answer can name an item or say there is none." Bạn chưa lấy việc túi nhẹ làm chắc nó rỗng; hai người nhìn phần của câu chuyện rồi mới kể điều còn lại.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Hỏi có bất cứ thứ gì còn trong túi — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn hỏi thêm: "Do you need anything?" Bạn có cần gì không? "Is there an item for your next task?" Người bạn nhìn phần chuẩn bị của mình, nói món cần lấy trong buổi hư cấu nếu còn thiếu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Companion checks own next-task plan and answers item-needed question. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion checks own next-task plan and answers item-needed question.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “Do you need anything?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn hỏi thêm: "Do you need anything?" Bạn có cần gì không? "Is there an item for your next task?" Người bạn nhìn phần chuẩn bị của mình, nói món cần lấy trong buổi hư cấu nếu còn thiếu.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Hỏi có bất cứ thứ gì còn trong túi — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn hỏi người bạn còn cần món nào mà chưa chọn tên cụ thể. "Leave the question open." Hãy nói: "Do you need anything?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold fictional supplies and full learner question, no item preselected during pause. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional supplies and full learner question, no item preselected during pause.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Leave the question open.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “Do you need anything?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn hỏi người bạn còn cần món nào mà chưa chọn tên cụ thể. "Leave the question open." Hãy nói: "Do you need anything?"” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Hỏi có bất cứ thứ gì còn trong túi — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Do you need anything?" Bạn có cần gì không? "The reply can tell us the item to look for." Hai người đã kiểm túi và phần cần chuẩn bị trong câu chuyện, cất đồ khi cả hai đã nói điều mình còn cần.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both finish fictional packing after checking remaining and needed items. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both finish fictional packing after checking remaining and needed items.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Do you need anything?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Do you need anything?" Bạn có cần gì không? "The reply can tell us the item to look for." Hai người đã kiểm túi và phần cần chuẩn bị trong câu chuyện, cất đồ khi cả hai đã nói điều mình còn cần.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Đồ trên bàn đã cất, trong túi còn bất cứ món nào của lớp không? Anything nghĩa là bất cứ thứ gì trong mẫu hỏi này. "We have not selected a particular object." Bạn cùng người bạn kiểm phần còn lại của hoạt động hư cấu trước khi rời bàn.
- R2 → SC01: Đồ trên bàn đã cất, trong túi còn bất cứ món nào của lớp không? Anything nghĩa là bất cứ thứ gì trong mẫu hỏi này. "We have not selected a particular object." Bạn cùng người bạn kiểm phần còn lại của hoạt động hư cấu trước khi rời bàn.
- R2 → SC02: Bạn hỏi: "Is there anything in the bag?" Trong túi có thứ gì không? "We are checking for any item, not one named thing." Người bạn mở túi để xem, câu hỏi cho họ biết bạn muốn kiểm phần bên trong chứ không chỉ một cây bút đã nói trước.
- R3 → SC02: Bạn hỏi: "Is there anything in the bag?" Trong túi có thứ gì không? "We are checking for any item, not one named thing." Người bạn mở túi để xem, câu hỏi cho họ biết bạn muốn kiểm phần bên trong chứ không chỉ một cây bút đã nói trước.
- R2 → SC03: Anything giúp giữ câu hỏi mở về đồ vật trong tình huống. "The answer can name an item or say there is none." Bạn chưa lấy việc túi nhẹ làm chắc nó rỗng; hai người nhìn phần của câu chuyện rồi mới kể điều còn lại.
- R3 → SC04: Bạn hỏi thêm: "Do you need anything?" Bạn có cần gì không? "Is there an item for your next task?" Người bạn nhìn phần chuẩn bị của mình, nói món cần lấy trong buổi hư cấu nếu còn thiếu.
- R4 → SC05: Bạn muốn hỏi người bạn còn cần món nào mà chưa chọn tên cụ thể. "Leave the question open." Hãy nói: "Do you need anything?"
- R4 → SC06: "Do you need anything?" Bạn có cần gì không? "The reply can tell us the item to look for." Hai người đã kiểm túi và phần cần chuẩn bị trong câu chuyện, cất đồ khi cả hai đã nói điều mình còn cần.

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