# Kịch bản — vocab-turn-on-script-733 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-turn-on-script-733/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "bật (thiết bị)" của từ TURN ON, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "bật (thiết bị)" của TURN ON mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng TURN ON trong ít nhất một câu
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
- Từ khoá duy nhất của video: TURN ON (phr), chỉ dạy nghĩa "bật (thiết bị)"
- Mức độ người học: CEFR A1; chủ đề: Cụm động từ
- Mã mục trong kho từ vựng: turn on.phr.switch-on (dùng để đánh dấu đã làm)
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

VI: 54.55–90.89 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.65–16.08 |
| SC02 | 8.82–14.69 |
| SC03 | 10.39–17.31 |
| SC04 | 8.5–14.16 |
| SC05 | 7.31–12.19 |
| SC06 | 9.88–16.46 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Bấm màn hình mãi, đèn vẫn chưa sáng — Nhịp 1

Mục đích: Make the selected sense useful in a concrete situation.

Sách mở rồi mà góc bàn tối quá! Turn on là bật thiết bị. "Make the lamp start working." Đèn bàn đã cắm sẵn trong tình huống; bạn cần nhờ bật nó để đọc, không phải xoay thân đèn cho đổi hướng.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot peers at book in dim room; ready desk lamp visible beside companion. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot peers at book in dim room; ready desk lamp visible beside companion.

Lý do: Make the selected sense useful in a concrete situation.

Chữ được phép: “turn on” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Sách mở rồi mà góc bàn tối quá! Turn on là bật thiết bị. "Make the lamp start working." Đèn bàn đã cắm sẵn trong tình huống; bạn cần nhờ bật nó để đọc, không phải xoay thân đèn cho đổi hướng.” (lần 1) · Make the selected sense useful in a concrete situation.

## SC02 — Bấm màn hình mãi, đèn vẫn chưa sáng — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nhờ: "Turn on the lamp, please." Làm ơn bật đèn nhé. "The lamp is the device we need." Người bạn đặt tay gần công tắc của chính chiếc đèn trên bàn, không chọn món khác trong phòng.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Companion beside unlit desk lamp Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion beside unlit desk lamp

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: Không có chữ/số

**Hình SC02_I2** — Same lamp lit, book page becomes readable. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Same lamp lit, book page becomes readable.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “Turn on the lamp, please.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhờ: "Turn on the lamp, please." Làm ơn bật đèn nhé. "The lamp is the device we need." Người bạn đặt tay gần công tắc của chính chiếc đèn trên bàn, không chọn món khác trong phòng.” (lần 1) · Use the first English model with its immediate purpose.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “Turn on the lamp, please.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC03 — Bấm màn hình mãi, đèn vẫn chưa sáng — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Tên đồ vật giúp lời nhờ rõ ngay. "We know which lamp you mean." Khi đã xác định đèn, it có thể nhắc lại nó. Trong mẫu này, it nằm giữa turn và on; bạn vẫn đang nói cùng một thao tác bật thiết bị.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Mascot indicates same lamp and then refers back to it, single device unchanged. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot indicates same lamp and then refers back to it, single device unchanged.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “turn on” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Tên đồ vật giúp lời nhờ rõ ngay. "We know which lamp you mean." Khi đã xác định đèn, it có thể nhắc lại nó. Trong mẫu này, it nằm giữa turn và on; bạn vẫn đang nói cùng một thao tác bật thiết bị.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Bấm màn hình mãi, đèn vẫn chưa sáng — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn nhắc ngắn hơn: "Please turn it on." Làm ơn bật nó lên. "It means the lamp we just named." Lời nhờ không cần lặp tên đèn, người bạn vẫn hiểu và bật đúng món đang cần.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Both focus on established lamp and illuminated book. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both focus on established lamp and illuminated book.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “Please turn it on.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn nhắc ngắn hơn: "Please turn it on." Làm ơn bật nó lên. "It means the lamp we just named." Lời nhờ không cần lặp tên đèn, người bạn vẫn hiểu và bật đúng món đang cần.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Bấm màn hình mãi, đèn vẫn chưa sáng — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Chiếc đèn đã được nhắc tới. "Use it for the same lamp." Hãy nói: "Please turn it on."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold lamp and pronoun model through learner interval. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold lamp and pronoun model through learner interval.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Please turn it on.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Chiếc đèn đã được nhắc tới. "Use it for the same lamp." Hãy nói: "Please turn it on."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Bấm màn hình mãi, đèn vẫn chưa sáng — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Please turn it on." Làm ơn bật nó lên. "Now the page is clear." Trong mẫu vừa luyện, it đứng giữa turn và on. Đèn sáng, bạn trở lại đọc sách; lời nhờ đã giải quyết đúng vấn đề ở góc bàn.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Mascot comfortably reads under same lit desk lamp, companion sits nearby. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot comfortably reads under same lit desk lamp, companion sits nearby.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Please turn it on.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Please turn it on." Làm ơn bật nó lên. "Now the page is clear." Trong mẫu vừa luyện, it đứng giữa turn và on. Đèn sáng, bạn trở lại đọc sách; lời nhờ đã giải quyết đúng vấn đề ở góc bàn.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Sách mở rồi mà góc bàn tối quá! Turn on là bật thiết bị. "Make the lamp start working." Đèn bàn đã cắm sẵn trong tình huống; bạn cần nhờ bật nó để đọc, không phải xoay thân đèn cho đổi hướng.
- R2 → SC01: Sách mở rồi mà góc bàn tối quá! Turn on là bật thiết bị. "Make the lamp start working." Đèn bàn đã cắm sẵn trong tình huống; bạn cần nhờ bật nó để đọc, không phải xoay thân đèn cho đổi hướng.
- R2 → SC02: Bạn nhờ: "Turn on the lamp, please." Làm ơn bật đèn nhé. "The lamp is the device we need." Người bạn đặt tay gần công tắc của chính chiếc đèn trên bàn, không chọn món khác trong phòng.
- R3 → SC02: Bạn nhờ: "Turn on the lamp, please." Làm ơn bật đèn nhé. "The lamp is the device we need." Người bạn đặt tay gần công tắc của chính chiếc đèn trên bàn, không chọn món khác trong phòng.
- R2 → SC03: Tên đồ vật giúp lời nhờ rõ ngay. "We know which lamp you mean." Khi đã xác định đèn, it có thể nhắc lại nó. Trong mẫu này, it nằm giữa turn và on; bạn vẫn đang nói cùng một thao tác bật thiết bị.
- R3 → SC04: Bạn nhắc ngắn hơn: "Please turn it on." Làm ơn bật nó lên. "It means the lamp we just named." Lời nhờ không cần lặp tên đèn, người bạn vẫn hiểu và bật đúng món đang cần.
- R4 → SC05: Chiếc đèn đã được nhắc tới. "Use it for the same lamp." Hãy nói: "Please turn it on."
- R4 → SC06: "Please turn it on." Làm ơn bật nó lên. "Now the page is clear." Trong mẫu vừa luyện, it đứng giữa turn và on. Đèn sáng, bạn trở lại đọc sách; lời nhờ đã giải quyết đúng vấn đề ở góc bàn.

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