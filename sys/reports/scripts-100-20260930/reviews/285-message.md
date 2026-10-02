# Kịch bản — vocab-message-script-285 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-message-script-285/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "tin nhắn" của từ MESSAGE, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "tin nhắn" của MESSAGE mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng MESSAGE trong ít nhất một câu
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
- Từ khoá duy nhất của video: MESSAGE (n), chỉ dạy nghĩa "tin nhắn"
- Mức độ người học: CEFR A1; chủ đề: Công nghệ và Internet
- Mã mục trong kho từ vựng: message.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 40.35–67.25 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 7.66–12.77 |
| SC02 | 7.76–12.93 |
| SC03 | 7.34–12.24 |
| SC04 | 9.83–16.38 |
| SC05 | 7.76–12.93 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Tin nhắn chưa gửi — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Tưởng đã báo rồi, hóa ra tin vẫn nằm trong ô soạn! Message là tin nhắn. Bạn đợi người bạn tới đón, mở điện thoại mới thấy lời hẹn chưa được gửi đi.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot views unsent draft bubble beside inactive send icon; friend waiting outside in distant view. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot views unsent draft bubble beside inactive send icon; friend waiting outside in distant view.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “message” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Tưởng đã báo rồi, hóa ra tin vẫn nằm trong ô soạn! Message là tin nhắn. Bạn đợi người bạn tới đón, mở điện thoại mới thấy lời hẹn chưa được gửi đi.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Tin nhắn chưa gửi — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn nói: "I'll send you a message." Tôi sẽ gửi cho bạn một tin nhắn. A message là một tin nhắn; bạn kiểm tra đúng người nhận rồi mới gửi lời hẹn đã soạn.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Message draft remains in input field under generic recipient avatar. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Message draft remains in input field under generic recipient avatar.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “I'll send you a message.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

**Hình SC02_I2** — Draft has moved to sent message bubble with check icon, same recipient avatar. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base scene camera, background, character identities, single mascot torso and exact clothing, prop positions and visible text; change only the specified state.; đổi: Draft has moved to sent message bubble with check icon, same recipient avatar.

Lý do: Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

Chữ được phép: “I'll send you a message.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "I'll send you a message." Tôi sẽ gửi cho bạn một tin nhắn. A message là một tin nhắn; bạn kiểm tra đúng người nhận rồi mới gửi lời hẹn đã soạn.” (lần 1) · Use the first English model as an action within the situation.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “rồi mới gửi lời hẹn đã soạn” (lần 1) · Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

## SC03 — Tin nhắn chưa gửi — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Người bạn trả lời: "I got your message." Tôi nhận được tin nhắn của bạn rồi. Your message chỉ tin vừa gửi; hai người đã biết gặp nhau ở cùng một cửa.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Phone shows delivered incoming response bubble; mascot smiles toward doorway. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Phone shows delivered incoming response bubble; mascot smiles toward doorway.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “I got your message.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn trả lời: "I got your message." Tôi nhận được tin nhắn của bạn rồi. Your message chỉ tin vừa gửi; hai người đã biết gặp nhau ở cùng một cửa.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Tin nhắn chưa gửi — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Tin đã tới người nhận. Người ấy nên nói "I got your message." hay "I'll send you a message." để xác nhận đã nhận? Chọn rồi đọc câu đó.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Two sentence choices shown beside simple delivered-message icon, neither highlighted. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Two sentence choices shown beside simple delivered-message icon, neither highlighted.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “I got your message.” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.; “I'll send you a message.” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Tin đã tới người nhận. Người ấy nên nói "I got your message." hay "I'll send you a message." để xác nhận đã nhận? Chọn rồi đọc câu đó.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Tin nhắn chưa gửi — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"I got your message." Tôi nhận được tin nhắn của bạn rồi. Giờ người bạn mới biết bạn đang ở đâu. Một lần nhìn lại ô soạn giải thích cả quãng chờ vừa rồi.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot meets friend at agreed doorway with phone lowered. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot meets friend at agreed doorway with phone lowered.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “I got your message.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"I got your message." Tôi nhận được tin nhắn của bạn rồi. Giờ người bạn mới biết bạn đang ở đâu. Một lần nhìn lại ô soạn giải thích cả quãng chờ vừa rồi.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Nhân vật đồng hành chính: Adult friend or companion. Minimal flat ink style; consistent adult face, age, gender and identity across all scenes. Distinct from canonical mascot. Plain mustard top; only explicitly required work outerwear, helmet or life jacket.; Plain mustard-yellow top, with only scenario-required accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Tưởng đã báo rồi, hóa ra tin vẫn nằm trong ô soạn! Message là tin nhắn. Bạn đợi người bạn tới đón, mở điện thoại mới thấy lời hẹn chưa được gửi đi.
- R2 → SC01: Tưởng đã báo rồi, hóa ra tin vẫn nằm trong ô soạn! Message là tin nhắn. Bạn đợi người bạn tới đón, mở điện thoại mới thấy lời hẹn chưa được gửi đi.
- R2 → SC02: Bạn nói: "I'll send you a message." Tôi sẽ gửi cho bạn một tin nhắn. A message là một tin nhắn; bạn kiểm tra đúng người nhận rồi mới gửi lời hẹn đã soạn.
- R3 → SC02: Bạn nói: "I'll send you a message." Tôi sẽ gửi cho bạn một tin nhắn. A message là một tin nhắn; bạn kiểm tra đúng người nhận rồi mới gửi lời hẹn đã soạn.
- R3 → SC03: Người bạn trả lời: "I got your message." Tôi nhận được tin nhắn của bạn rồi. Your message chỉ tin vừa gửi; hai người đã biết gặp nhau ở cùng một cửa.
- R4 → SC04: Tin đã tới người nhận. Người ấy nên nói "I got your message." hay "I'll send you a message." để xác nhận đã nhận? Chọn rồi đọc câu đó.
- R4 → SC05: "I got your message." Tôi nhận được tin nhắn của bạn rồi. Giờ người bạn mới biết bạn đang ở đâu. Một lần nhìn lại ô soạn giải thích cả quãng chờ vừa rồi.

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