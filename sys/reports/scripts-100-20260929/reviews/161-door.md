# Kịch bản — vocab-door-script-161 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-door-script-161/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "cửa ra vào" của từ DOOR, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "cửa ra vào" của DOOR mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng DOOR trong ít nhất một câu
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
- Từ khoá duy nhất của video: DOOR (n), chỉ dạy nghĩa "cửa ra vào"
- Mức độ người học: CEFR A1; chủ đề: Nhà cửa và nội thất
- Mã mục trong kho từ vựng: door.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 41.77–69.63 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.44–15.74 |
| SC02 | 8.7–14.51 |
| SC03 | 8.4–14.0 |
| SC04 | 8.72–14.53 |
| SC05 | 6.51–10.85 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Hai tay đều bận — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

"Can you open the door?" Bạn mở cửa giúp tôi được không? Door là cửa ra vào. Bạn ôm chiếc hộp bằng cả hai tay, tới nơi mới biết cửa đang đóng. Người bạn ở bên trong có thể giúp ngay.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot carries a large box with both hands at a closed door; friend is visible through a small clear side panel. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot carries a large box with both hands at a closed door; friend is visible through a small clear side panel.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “Can you open the door?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “"Can you open the door?" Bạn mở cửa giúp tôi được không? Door là cửa ra vào. Bạn ôm chiếc hộp bằng cả hai tay, tới nơi mới biết cửa đang đóng. Người bạn ở bên trong có thể giúp ngay.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Hai tay đều bận — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn nhờ: "Can you open the door?" Open the door là mở cửa. Câu bắt đầu bằng Can you để nhờ người đối diện làm giúp. Bạn đứng lùi một chút, chừa chỗ cho cánh cửa mở ra.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — The door is closed and mascot waits with the box outside its swing. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: The door is closed and mascot waits with the box outside its swing.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Can you open the door?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

**Hình SC02_I2** — Friend has opened the door; mascot still holds the box and now has a clear path. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base scene camera, background, character identities, single mascot torso and exact clothing, prop positions and visible text; change only the specified state.; đổi: Friend has opened the door; mascot still holds the box and now has a clear path.

Lý do: Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

Chữ được phép: “Can you open the door?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nhờ: "Can you open the door?" Open the door là mở cửa. Câu bắt đầu bằng Can you để nhờ người đối diện làm giúp. Bạn đứng lùi một chút, chừa chỗ cho cánh cửa mở ra.” (lần 1) · Use the first English model as an action within the situation.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “Bạn đứng lùi một chút” (lần 1) · Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

## SC03 — Hai tay đều bận — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Qua cửa rồi, bạn nhắc: "Please close the door." Làm ơn đóng cửa lại. Close là đóng. Chiếc hộp đã ở trong nhà, người bạn có thể khép cửa mà không vướng hai tay bạn nữa.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Mascot has set the box inside; friend reaches to close the doorway behind them. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot has set the box inside; friend reaches to close the doorway behind them.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “Please close the door.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Qua cửa rồi, bạn nhắc: "Please close the door." Làm ơn đóng cửa lại. Close là đóng. Chiếc hộp đã ở trong nhà, người bạn có thể khép cửa mà không vướng hai tay bạn nữa.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Hai tay đều bận — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Hai tay đang bận, bạn muốn nhờ mở cửa. Điền vào "Can you open the...?" rồi nói cả câu.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold mascot carrying the box at a closed door with the unfinished request. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold mascot carrying the box at a closed door with the unfinished request.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “Can you open the...?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Hai tay đang bận, bạn muốn nhờ mở cửa. Điền vào "Can you open the...?" rồi nói cả câu.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Hai tay đều bận — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"Can you open the door?" Đáp án là door. Chỉ cần nhờ đúng việc, hộp vào được nhà và bạn không phải đặt nó xuống ngoài lối đi.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Box rests inside the home and the door is closed; mascot relaxes empty hands. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Box rests inside the home and the door is closed; mascot relaxes empty hands.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “Can you open the door?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Can you open the door?" Đáp án là door. Chỉ cần nhờ đúng việc, hộp vào được nhà và bạn không phải đặt nó xuống ngoài lối đi.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người bạn hoặc người hỗ trợ trong tình huống: Adult supporting person in minimal flat ink style. Maintain the role and identity specified by the scene across the whole story. Plain mustard top; may wear the explicitly described extra garment for clothing lessons.; Plain mustard-yellow top, with only scenario-required accessories.
- Người phụ khi tình huống yêu cầu: Adult supporting person, distinct from the main mascot and first companion, minimal flat ink style; appears only when explicitly specified.; Plain lavender top; scenario-required accessories only.

## Đối chiếu ý bắt buộc

- R1 → SC01: "Can you open the door?" Bạn mở cửa giúp tôi được không? Door là cửa ra vào. Bạn ôm chiếc hộp bằng cả hai tay, tới nơi mới biết cửa đang đóng. Người bạn ở bên trong có thể giúp ngay.
- R2 → SC01: "Can you open the door?" Bạn mở cửa giúp tôi được không? Door là cửa ra vào. Bạn ôm chiếc hộp bằng cả hai tay, tới nơi mới biết cửa đang đóng. Người bạn ở bên trong có thể giúp ngay.
- R2 → SC02: Bạn nhờ: "Can you open the door?" Open the door là mở cửa. Câu bắt đầu bằng Can you để nhờ người đối diện làm giúp. Bạn đứng lùi một chút, chừa chỗ cho cánh cửa mở ra.
- R3 → SC02: Bạn nhờ: "Can you open the door?" Open the door là mở cửa. Câu bắt đầu bằng Can you để nhờ người đối diện làm giúp. Bạn đứng lùi một chút, chừa chỗ cho cánh cửa mở ra.
- R3 → SC03: Qua cửa rồi, bạn nhắc: "Please close the door." Làm ơn đóng cửa lại. Close là đóng. Chiếc hộp đã ở trong nhà, người bạn có thể khép cửa mà không vướng hai tay bạn nữa.
- R4 → SC04: Hai tay đang bận, bạn muốn nhờ mở cửa. Điền vào "Can you open the...?" rồi nói cả câu.
- R4 → SC05: "Can you open the door?" Đáp án là door. Chỉ cần nhờ đúng việc, hộp vào được nhà và bạn không phải đặt nó xuống ngoài lối đi.

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