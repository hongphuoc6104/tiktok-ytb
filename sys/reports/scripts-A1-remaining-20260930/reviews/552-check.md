# Kịch bản — vocab-check-script-552 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-check-script-552/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "kiểm tra" của từ CHECK, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "kiểm tra" của CHECK mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng CHECK trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn CHECK với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "check" còn nghĩa khác: sự kiểm tra [n, check.n.inspection]. Video này KHÔNG dạy nghĩa đó.
- Từ "check" còn nghĩa khác: tờ séc [n, check.n.cheque]. Video này KHÔNG dạy nghĩa đó.
- Từ "check" còn nghĩa khác: hoá đơn (nhà hàng, cách gọi ở Mỹ) [n, check.n.restaurant-bill]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: CHECK (v), chỉ dạy nghĩa "kiểm tra"
- Mức độ người học: CEFR A1; chủ đề: Động từ thông dụng
- Mã mục trong kho từ vựng: check.v.check-basic (dùng để đánh dấu đã làm)
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

VI: 44.45–74.09 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.07–16.78 |
| SC02 | 7.87–13.12 |
| SC03 | 8.29–13.81 |
| SC04 | 10.35–17.26 |
| SC05 | 7.87–13.12 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Kiểm tra thẻ trước khi đặt vào phong bì — Nhịp 1

Mục đích: Introduce a concrete need and the selected sense.

Phong bì đã mở, thẻ hẹn có đúng thông tin chưa? Check nghĩa là kiểm tra. "Look carefully before the next step." Bạn chuẩn bị thiệp của một cuộc hẹn hư cấu, muốn đối chiếu phần đã ghi trước khi cất vào phong bì.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot holds fictional meeting card above open envelope, companion has plain calendar plan. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot holds fictional meeting card above open envelope, companion has plain calendar plan.

Lý do: Introduce a concrete need and the selected sense.

Chữ được phép: “check” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Phong bì đã mở, thẻ hẹn có đúng thông tin chưa? Check nghĩa là kiểm tra. "Look carefully before the next step." Bạn chuẩn bị thiệp của một cuộc hẹn hư cấu, muốn đối chiếu phần đã ghi trước khi cất vào phong bì.” (lần 1) · Introduce a concrete need and the selected sense.

## SC02 — Kiểm tra thẻ trước khi đặt vào phong bì — Nhịp 2

Mục đích: Make the first model an action in the situation.

Bạn nhờ: "Check the card." Kiểm tra thẻ nhé. "See if the details match our plan." Người bạn nhìn phần hình địa điểm rồi đặt lịch cạnh thẻ, để hai người cùng đối chiếu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend compares invitation card and fictional planner fields side by side. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend compares invitation card and fictional planner fields side by side.

Lý do: Make the first model an action in the situation.

Chữ được phép: “Check the card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhờ: "Check the card." Kiểm tra thẻ nhé. "See if the details match our plan." Người bạn nhìn phần hình địa điểm rồi đặt lịch cạnh thẻ, để hai người cùng đối chiếu.” (lần 1) · Make the first model an action in the situation.

## SC03 — Kiểm tra thẻ trước khi đặt vào phong bì — Nhịp 3

Mục đích: Advance the same story with the second model.

Bạn hỏi: "Can you check this date?" Bạn kiểm ngày tháng này được không? "One detail before we send it." Người bạn xác nhận phần ngày của câu chuyện, bạn mới đặt thiệp vào phong bì.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend checks corresponding fictional date fields, no actual personal meeting information. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend checks corresponding fictional date fields, no actual personal meeting information.

Lý do: Advance the same story with the second model.

Chữ được phép: “Can you check this date?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn hỏi: "Can you check this date?" Bạn kiểm ngày tháng này được không? "One detail before we send it." Người bạn xác nhận phần ngày của câu chuyện, bạn mới đặt thiệp vào phong bì.” (lần 1) · Advance the same story with the second model.

## SC04 — Kiểm tra thẻ trước khi đặt vào phong bì — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn nhờ kiểm ngày tháng trên một thẻ hẹn. "Ask for that check." Nói như lúc còn có thể sửa trước khi gửi: "Can you check this date?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold fictional invitation and full question. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional invitation and full question.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Can you check this date?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nhờ kiểm ngày tháng trên một thẻ hẹn. "Ask for that check." Nói như lúc còn có thể sửa trước khi gửi: "Can you check this date?"” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Kiểm tra thẻ trước khi đặt vào phong bì — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"Can you check this date?" Bạn kiểm ngày này nhé? "The card has had a careful look." Hai người đã đối chiếu thẻ với kế hoạch, rồi mới khép phong bì trong câu chuyện.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot closes envelope after companion confirms matching fictional plan. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot closes envelope after companion confirms matching fictional plan.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “Can you check this date?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Can you check this date?" Bạn kiểm ngày này nhé? "The card has had a careful look." Hai người đã đối chiếu thẻ với kế hoạch, rồi mới khép phong bì trong câu chuyện.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Phong bì đã mở, thẻ hẹn có đúng thông tin chưa? Check nghĩa là kiểm tra. "Look carefully before the next step." Bạn chuẩn bị thiệp của một cuộc hẹn hư cấu, muốn đối chiếu phần đã ghi trước khi cất vào phong bì.
- R2 → SC01: Phong bì đã mở, thẻ hẹn có đúng thông tin chưa? Check nghĩa là kiểm tra. "Look carefully before the next step." Bạn chuẩn bị thiệp của một cuộc hẹn hư cấu, muốn đối chiếu phần đã ghi trước khi cất vào phong bì.
- R2 → SC02: Bạn nhờ: "Check the card." Kiểm tra thẻ nhé. "See if the details match our plan." Người bạn nhìn phần hình địa điểm rồi đặt lịch cạnh thẻ, để hai người cùng đối chiếu.
- R3 → SC02: Bạn nhờ: "Check the card." Kiểm tra thẻ nhé. "See if the details match our plan." Người bạn nhìn phần hình địa điểm rồi đặt lịch cạnh thẻ, để hai người cùng đối chiếu.
- R3 → SC03: Bạn hỏi: "Can you check this date?" Bạn kiểm ngày tháng này được không? "One detail before we send it." Người bạn xác nhận phần ngày của câu chuyện, bạn mới đặt thiệp vào phong bì.
- R4 → SC04: Bạn muốn nhờ kiểm ngày tháng trên một thẻ hẹn. "Ask for that check." Nói như lúc còn có thể sửa trước khi gửi: "Can you check this date?"
- R4 → SC05: "Can you check this date?" Bạn kiểm ngày này nhé? "The card has had a careful look." Hai người đã đối chiếu thẻ với kế hoạch, rồi mới khép phong bì trong câu chuyện.

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