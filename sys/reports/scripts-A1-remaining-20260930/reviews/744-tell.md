# Kịch bản — vocab-tell-script-744 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-tell-script-744/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "kể, nói cho biết" của từ TELL, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "kể, nói cho biết" của TELL mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng TELL trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn TELL với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "tell" còn nghĩa khác: phân biệt được (tell the difference) [v, tell.v.distinguish]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: TELL (v), chỉ dạy nghĩa "kể, nói cho biết"
- Mức độ người học: CEFR A1; chủ đề: Giao tiếp và ngôn ngữ
- Mã mục trong kho từ vựng: tell.v (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm long; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

7 cảnh · 7 hình logic · 7 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 70.22–117.03 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.8–18.01 |
| SC02 | 9.75–16.24 |
| SC03 | 10.07–16.78 |
| SC04 | 10.8–18.01 |
| SC05 | 9.43–15.71 |
| SC06 | 7.94–13.23 |
| SC07 | 11.43–19.05 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Nói rõ cho tôi chuyện vừa xảy ra — Nhịp 1

Mục đích: Establish the need and one selected meaning promptly.

Ảnh có chiếc bàn trống, nhưng sao mọi người trong nhóm đều cười? Tell là kể, nói cho ai biết. "Give someone information." Bạn muốn nghe câu chuyện phía sau ảnh, cần chỉ rõ người sẽ nhận thông tin thay vì chỉ nhắc rằng có lời nói.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion examine fictional photo of empty craft table after group cleanup. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion examine fictional photo of empty craft table after group cleanup.

Lý do: Establish the need and one selected meaning promptly.

Chữ được phép: “tell” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Ảnh có chiếc bàn trống, nhưng sao mọi người trong nhóm đều cười? Tell là kể, nói cho ai biết. "Give someone information." Bạn muốn nghe câu chuyện phía sau ảnh, cần chỉ rõ người sẽ nhận thông tin thay vì chỉ nhắc rằng có lời nói.” (lần 1) · Establish the need and one selected meaning promptly.

## SC02 — Nói rõ cho tôi chuyện vừa xảy ra — Nhịp 2

Mục đích: Use the first model at the point where the speaker needs it.

Bạn nhờ: "Tell me the story." Kể cho tôi câu chuyện nhé. "Me is the person who wants to know." Người bạn chỉ vào bức ảnh và bắt đầu giải thích: cả nhóm vừa dọn xong, nên chiếc bàn mới trống như vậy.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Companion describes fictional photo while mascot listens, image matches cleanup result. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion describes fictional photo while mascot listens, image matches cleanup result.

Lý do: Use the first model at the point where the speaker needs it.

Chữ được phép: “Tell me the story.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhờ: "Tell me the story." Kể cho tôi câu chuyện nhé. "Me is the person who wants to know." Người bạn chỉ vào bức ảnh và bắt đầu giải thích: cả nhóm vừa dọn xong, nên chiếc bàn mới trống như vậy.” (lần 1) · Use the first model at the point where the speaker needs it.

## SC03 — Nói rõ cho tôi chuyện vừa xảy ra — Nhịp 3

Mục đích: Show the condition or contrast that makes this usage matter.

Trong mẫu này, tell đi với người nghe ngay sau nó. "Someone receives the information." Me không phải nội dung chuyện; the story mới là điều được kể. Ta giữ hai vai rõ để người học biết đang nhờ ai kể cho ai nghe.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Show companion as speaker, mascot as listener, photo between them. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Show companion as speaker, mascot as listener, photo between them.

Lý do: Show the condition or contrast that makes this usage matter.

Chữ được phép: “tell” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Trong mẫu này, tell đi với người nghe ngay sau nó. "Someone receives the information." Me không phải nội dung chuyện; the story mới là điều được kể. Ta giữ hai vai rõ để người học biết đang nhờ ai kể cho ai nghe.” (lần 1) · Show the condition or contrast that makes this usage matter.

## SC04 — Nói rõ cho tôi chuyện vừa xảy ra — Nhịp 4

Mục đích: Use the second model to advance or compare within the same story.

Lan cũng chưa hiểu ảnh, bạn đề nghị: "Tell Lan about the photo." Hãy kể cho Lan về bức ảnh. "Lan needs the same explanation." Người bạn quay sang Lan, vẫn nhắc câu chuyện dọn bàn đã nói; không tự bịa một sự kiện khác cho ảnh.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Companion turns toward female Lan, explaining same fictional photo; mascot stays nearby. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion turns toward female Lan, explaining same fictional photo; mascot stays nearby.

Lý do: Use the second model to advance or compare within the same story.

Chữ được phép: “Tell Lan about the photo.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Lan cũng chưa hiểu ảnh, bạn đề nghị: "Tell Lan about the photo." Hãy kể cho Lan về bức ảnh. "Lan needs the same explanation." Người bạn quay sang Lan, vẫn nhắc câu chuyện dọn bàn đã nói; không tự bịa một sự kiện khác cho ảnh.” (lần 1) · Use the second model to advance or compare within the same story.

## SC05 — Nói rõ cho tôi chuyện vừa xảy ra — Nhịp 5

Mục đích: Clarify a common trap through this example without expanding to another meaning.

Đừng thêm to trước me trong câu Tell me the story đang luyện. "The listener follows tell directly here." Ta đang dùng tell để kể thông tin cho người khác; không mở thêm nghĩa bảo ai làm việc gì trong bài này.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Three adults maintain speaker and listener roles, no new command activity introduced. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Three adults maintain speaker and listener roles, no new command activity introduced.

Lý do: Clarify a common trap through this example without expanding to another meaning.

Chữ được phép: “tell” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “Đừng thêm to trước me trong câu Tell me the story đang luyện. "The listener follows tell directly here." Ta đang dùng tell để kể thông tin cho người khác; không mở thêm nghĩa bảo ai làm việc gì trong bài này.” (lần 1) · Clarify a common trap through this example without expanding to another meaning.

## SC06 — Nói rõ cho tôi chuyện vừa xảy ra — Lượt thực hành

Mục đích: Invite a supported learner response; hold before the feedback.

Bạn muốn nhờ người bạn kể chuyện cho mình. "Name the listener and the information." Hãy nói: "Tell me the story."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Hold storyteller, listener and exact request. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold storyteller, listener and exact request.

Lý do: Invite a supported learner response; hold before the feedback.

Chữ được phép: “Tell me the story.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · hold · vi: “Bạn muốn nhờ người bạn kể chuyện cho mình. "Name the listener and the information." Hãy nói: "Tell me the story."” (lần 1) · Invite a supported learner response; hold before the feedback.

## SC07 — Nói rõ cho tôi chuyện vừa xảy ra — Phản hồi và kết quả

Mục đích: Provide the response and complete the opening promise.

"Tell me the story." Kể cho tôi câu chuyện nhé. "Now the empty table makes sense." Bức ảnh ghi kết quả sau khi dọn, nên mọi người vui. Bạn đã nhận được thông tin còn thiếu, và câu vừa luyện đặt me đúng chỗ để nói người cần nghe chuyện.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC07_I1** — Mascot and Lan understand photo, companion displays same cleared table in room. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and Lan understand photo, companion displays same cleared table in room.

Lý do: Provide the response and complete the opening promise.

Chữ được phép: “Tell me the story.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC07_B1 → SC07_I1 · cut · vi: “"Tell me the story." Kể cho tôi câu chuyện nhé. "Now the empty table makes sense." Bức ảnh ghi kết quả sau khi dọn, nên mọi người vui. Bạn đã nhận được thông tin còn thiếu, và câu vừa luyện đặt me đúng chỗ để nói người cần nghe chuyện.” (lần 1) · Provide the response and complete the opening promise.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Fictional adult male Minh, participating companion; maintain the named identity. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.
- Người tham gia hoặc nhân vật bổ trợ: Fictional adult female Lan, participating listener or recipient; maintain the named identity. Minimal flat ink style and ordinary adult proportions.; Single plain lavender top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Ảnh có chiếc bàn trống, nhưng sao mọi người trong nhóm đều cười? Tell là kể, nói cho ai biết. "Give someone information." Bạn muốn nghe câu chuyện phía sau ảnh, cần chỉ rõ người sẽ nhận thông tin thay vì chỉ nhắc rằng có lời nói.
- R2 → SC01: Ảnh có chiếc bàn trống, nhưng sao mọi người trong nhóm đều cười? Tell là kể, nói cho ai biết. "Give someone information." Bạn muốn nghe câu chuyện phía sau ảnh, cần chỉ rõ người sẽ nhận thông tin thay vì chỉ nhắc rằng có lời nói.
- R2 → SC02: Bạn nhờ: "Tell me the story." Kể cho tôi câu chuyện nhé. "Me is the person who wants to know." Người bạn chỉ vào bức ảnh và bắt đầu giải thích: cả nhóm vừa dọn xong, nên chiếc bàn mới trống như vậy.
- R3 → SC02: Bạn nhờ: "Tell me the story." Kể cho tôi câu chuyện nhé. "Me is the person who wants to know." Người bạn chỉ vào bức ảnh và bắt đầu giải thích: cả nhóm vừa dọn xong, nên chiếc bàn mới trống như vậy.
- R2 → SC03: Trong mẫu này, tell đi với người nghe ngay sau nó. "Someone receives the information." Me không phải nội dung chuyện; the story mới là điều được kể. Ta giữ hai vai rõ để người học biết đang nhờ ai kể cho ai nghe.
- R3 → SC04: Lan cũng chưa hiểu ảnh, bạn đề nghị: "Tell Lan about the photo." Hãy kể cho Lan về bức ảnh. "Lan needs the same explanation." Người bạn quay sang Lan, vẫn nhắc câu chuyện dọn bàn đã nói; không tự bịa một sự kiện khác cho ảnh.
- R2 → SC05: Đừng thêm to trước me trong câu Tell me the story đang luyện. "The listener follows tell directly here." Ta đang dùng tell để kể thông tin cho người khác; không mở thêm nghĩa bảo ai làm việc gì trong bài này.
- R4 → SC06: Bạn muốn nhờ người bạn kể chuyện cho mình. "Name the listener and the information." Hãy nói: "Tell me the story."
- R4 → SC07: "Tell me the story." Kể cho tôi câu chuyện nhé. "Now the empty table makes sense." Bức ảnh ghi kết quả sau khi dọn, nên mọi người vui. Bạn đã nhận được thông tin còn thiếu, và câu vừa luyện đặt me đúng chỗ để nói người cần nghe chuyện.

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