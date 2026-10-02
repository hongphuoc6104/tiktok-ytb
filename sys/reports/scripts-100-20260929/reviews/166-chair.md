# Kịch bản — vocab-chair-script-166 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-chair-script-166/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "cái ghế" của từ CHAIR, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "cái ghế" của CHAIR mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng CHAIR trong ít nhất một câu
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
- Từ khoá duy nhất của video: CHAIR (n), chỉ dạy nghĩa "cái ghế"
- Mức độ người học: CEFR A1; chủ đề: Nhà cửa và nội thất
- Mã mục trong kho từ vựng: chair.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 41.35–68.91 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.35–15.58 |
| SC02 | 8.18–13.62 |
| SC03 | 8.08–13.47 |
| SC04 | 9.23–15.39 |
| SC05 | 6.51–10.85 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Khách tới mà thiếu ghế — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

"Can I have a chair?" Cho tôi xin một cái ghế được không? Chair là ghế. Bạn tới bàn cuối cùng, hai chiếc ghế đã có người ngồi. Có chỗ trên bàn rồi, còn chỗ ngồi thì phải hỏi thêm.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot stands at a table where two adult friends occupy two chairs; an extra chair is visible nearby. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot stands at a table where two adult friends occupy two chairs; an extra chair is visible nearby.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “Can I have a chair?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “"Can I have a chair?" Cho tôi xin một cái ghế được không? Chair là ghế. Bạn tới bàn cuối cùng, hai chiếc ghế đã có người ngồi. Có chỗ trên bàn rồi, còn chỗ ngồi thì phải hỏi thêm.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Khách tới mà thiếu ghế — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn hỏi: "Can I have a chair?" A chair là một chiếc ghế. Người bạn đứng dậy kéo chiếc ghế ở góc phòng tới. Bạn dịch túi ra khỏi lối để người ấy mang ghế qua.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend carries an extra chair toward the table while mascot moves a bag out of the way. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend carries an extra chair toward the table while mascot moves a bag out of the way.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Can I have a chair?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Can I have a chair?" A chair là một chiếc ghế. Người bạn đứng dậy kéo chiếc ghế ở góc phòng tới. Bạn dịch túi ra khỏi lối để người ấy mang ghế qua.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Khách tới mà thiếu ghế — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Người bạn nói: "This chair is for you." Chiếc ghế này dành cho bạn. For you chỉ người nhận. Bạn cảm ơn rồi ngồi xuống; cả ba giờ có thể nhìn nhau và trò chuyện.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend presents the extra chair to mascot at the table; third adult stays seated. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend presents the extra chair to mascot at the table; third adult stays seated.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “This chair is for you.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn nói: "This chair is for you." Chiếc ghế này dành cho bạn. For you chỉ người nhận. Bạn cảm ơn rồi ngồi xuống; cả ba giờ có thể nhìn nhau và trò chuyện.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Khách tới mà thiếu ghế — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn cần xin một chiếc ghế. Hoàn thành "Can I have a...?" rồi nói như đang đứng cạnh bàn có bạn bè.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold mascot beside the occupied table and request stem without the answer word. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold mascot beside the occupied table and request stem without the answer word.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “Can I have a...?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn cần xin một chiếc ghế. Hoàn thành "Can I have a...?" rồi nói như đang đứng cạnh bàn có bạn bè.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Khách tới mà thiếu ghế — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"Can I have a chair?" Từ đó là chair. Ba người đã có ba chỗ ngồi. Cuộc trò chuyện không còn một người phải đứng ở mép bàn.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Three adults sit around the table on three separate chairs, with the bag clear of the walkway. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Three adults sit around the table on three separate chairs, with the bag clear of the walkway.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “Can I have a chair?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Can I have a chair?" Từ đó là chair. Ba người đã có ba chỗ ngồi. Cuộc trò chuyện không còn một người phải đứng ở mép bàn.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người bạn hoặc người hỗ trợ trong tình huống: Adult supporting person in minimal flat ink style. Maintain the role and identity specified by the scene across the whole story. Plain mustard top; may wear the explicitly described extra garment for clothing lessons.; Plain mustard-yellow top, with only scenario-required accessories.
- Người phụ khi tình huống yêu cầu: Adult supporting person, distinct from the main mascot and first companion, minimal flat ink style; appears only when explicitly specified.; Plain lavender top; scenario-required accessories only.

## Đối chiếu ý bắt buộc

- R1 → SC01: "Can I have a chair?" Cho tôi xin một cái ghế được không? Chair là ghế. Bạn tới bàn cuối cùng, hai chiếc ghế đã có người ngồi. Có chỗ trên bàn rồi, còn chỗ ngồi thì phải hỏi thêm.
- R2 → SC01: "Can I have a chair?" Cho tôi xin một cái ghế được không? Chair là ghế. Bạn tới bàn cuối cùng, hai chiếc ghế đã có người ngồi. Có chỗ trên bàn rồi, còn chỗ ngồi thì phải hỏi thêm.
- R2 → SC02: Bạn hỏi: "Can I have a chair?" A chair là một chiếc ghế. Người bạn đứng dậy kéo chiếc ghế ở góc phòng tới. Bạn dịch túi ra khỏi lối để người ấy mang ghế qua.
- R3 → SC02: Bạn hỏi: "Can I have a chair?" A chair là một chiếc ghế. Người bạn đứng dậy kéo chiếc ghế ở góc phòng tới. Bạn dịch túi ra khỏi lối để người ấy mang ghế qua.
- R3 → SC03: Người bạn nói: "This chair is for you." Chiếc ghế này dành cho bạn. For you chỉ người nhận. Bạn cảm ơn rồi ngồi xuống; cả ba giờ có thể nhìn nhau và trò chuyện.
- R4 → SC04: Bạn cần xin một chiếc ghế. Hoàn thành "Can I have a...?" rồi nói như đang đứng cạnh bàn có bạn bè.
- R4 → SC05: "Can I have a chair?" Từ đó là chair. Ba người đã có ba chỗ ngồi. Cuộc trò chuyện không còn một người phải đứng ở mép bàn.

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