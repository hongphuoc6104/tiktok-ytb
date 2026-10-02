# Kịch bản — vocab-build-script-176 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-build-script-176/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "xây" của từ BUILD, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "xây" của BUILD mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng BUILD trong ít nhất một câu
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
- Từ khoá duy nhất của video: BUILD (v), chỉ dạy nghĩa "xây"
- Mức độ người học: CEFR A1; chủ đề: Nhà cửa và nội thất
- Mã mục trong kho từ vựng: build.v (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 42.2–70.35 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.44–15.74 |
| SC02 | 9.23–15.39 |
| SC03 | 8.3–13.84 |
| SC04 | 8.61–14.35 |
| SC05 | 6.62–11.03 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Nhà giấy chưa có mái — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Nhà chưa có mái! Build là xây. Bạn đang ghép một căn nhà mô hình, bốn bức tường đã đứng mà mảnh mái còn nằm trên bàn. Người bạn giữ tường giúp; hai người cùng làm cho căn nhà hoàn chỉnh.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and friend assemble a small model house on a craft table, with four walls upright and a roof piece beside them. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and friend assemble a small model house on a craft table, with four walls upright and a roof piece beside them.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “build” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Nhà chưa có mái! Build là xây. Bạn đang ghép một căn nhà mô hình, bốn bức tường đã đứng mà mảnh mái còn nằm trên bàn. Người bạn giữ tường giúp; hai người cùng làm cho căn nhà hoàn chỉnh.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Nhà giấy chưa có mái — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn rủ: "Let's build a house." Mình xây một căn nhà nhé. Build nói hành động tạo nên căn nhà từng phần. Trong trò chơi này, vật liệu là những mảnh giấy cứng, nên cả căn nhà vừa trên bàn.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend stabilizes model walls while mascot positions another small panel; roof still separate. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend stabilizes model walls while mascot positions another small panel; roof still separate.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Let's build a house.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn rủ: "Let's build a house." Mình xây một căn nhà nhé. Build nói hành động tạo nên căn nhà từng phần. Trong trò chơi này, vật liệu là những mảnh giấy cứng, nên cả căn nhà vừa trên bàn.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Nhà giấy chưa có mái — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Bạn kể: "We build it together." Chúng tôi cùng xây nó. Together là cùng nhau. Một người giữ tường, người kia đặt mái lên; nhờ phối hợp, mô hình không nghiêng khi thêm phần cuối.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — The paper house walls stand with the roof held just above them. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: The paper house walls stand with the roof held just above them.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “We build it together.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

**Hình SC03_I2** — The roof is seated on the model walls while the friend steadies the base. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: SC03_I1; giữ: Preserve base scene camera, background, character identities, single mascot torso and exact clothing, prop positions and visible text; change only the specified state.; đổi: The roof is seated on the model walls while the friend steadies the base.

Lý do: Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

Chữ được phép: “We build it together.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn kể: "We build it together." Chúng tôi cùng xây nó. Together là cùng nhau. Một người giữ tường, người kia đặt mái lên; nhờ phối hợp, mô hình không nghiêng khi thêm phần cuối.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

Nhịp SC03_B2 → SC03_I2 · cut · vi: “người kia đặt mái lên” (lần 1) · Show the visible state change caused by the previous action; attach Base scene reference and canonical Character reference.

## SC04 — Nhà giấy chưa có mái — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Muốn rủ bạn cùng xây một căn nhà mô hình, hoàn thành "Let's... a house." và nói trọn câu.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold model walls and separate roof with the unfinished invitation. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold model walls and separate roof with the unfinished invitation.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “Let's... a house.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Muốn rủ bạn cùng xây một căn nhà mô hình, hoàn thành "Let's... a house." và nói trọn câu.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Nhà giấy chưa có mái — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"Let's build a house." Từ đó là build. Mái đã ở trên tường, cả mô hình đứng vững. Hai người buông tay mà căn nhà vẫn không đổ.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Both adults show open hands beside the completed stable model house on the table. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both adults show open hands beside the completed stable model house on the table.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “Let's build a house.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Let's build a house." Từ đó là build. Mái đã ở trên tường, cả mô hình đứng vững. Hai người buông tay mà căn nhà vẫn không đổ.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người bạn hoặc người hỗ trợ trong tình huống: Adult supporting person in minimal flat ink style. Maintain the role and identity specified by the scene across the whole story. Plain mustard top; may wear the explicitly described extra garment for clothing lessons.; Plain mustard-yellow top, with only scenario-required accessories.
- Người phụ khi tình huống yêu cầu: Adult supporting person, distinct from the main mascot and first companion, minimal flat ink style; appears only when explicitly specified.; Plain lavender top; scenario-required accessories only.

## Đối chiếu ý bắt buộc

- R1 → SC01: Nhà chưa có mái! Build là xây. Bạn đang ghép một căn nhà mô hình, bốn bức tường đã đứng mà mảnh mái còn nằm trên bàn. Người bạn giữ tường giúp; hai người cùng làm cho căn nhà hoàn chỉnh.
- R2 → SC01: Nhà chưa có mái! Build là xây. Bạn đang ghép một căn nhà mô hình, bốn bức tường đã đứng mà mảnh mái còn nằm trên bàn. Người bạn giữ tường giúp; hai người cùng làm cho căn nhà hoàn chỉnh.
- R2 → SC02: Bạn rủ: "Let's build a house." Mình xây một căn nhà nhé. Build nói hành động tạo nên căn nhà từng phần. Trong trò chơi này, vật liệu là những mảnh giấy cứng, nên cả căn nhà vừa trên bàn.
- R3 → SC02: Bạn rủ: "Let's build a house." Mình xây một căn nhà nhé. Build nói hành động tạo nên căn nhà từng phần. Trong trò chơi này, vật liệu là những mảnh giấy cứng, nên cả căn nhà vừa trên bàn.
- R3 → SC03: Bạn kể: "We build it together." Chúng tôi cùng xây nó. Together là cùng nhau. Một người giữ tường, người kia đặt mái lên; nhờ phối hợp, mô hình không nghiêng khi thêm phần cuối.
- R4 → SC04: Muốn rủ bạn cùng xây một căn nhà mô hình, hoàn thành "Let's... a house." và nói trọn câu.
- R4 → SC05: "Let's build a house." Từ đó là build. Mái đã ở trên tường, cả mô hình đứng vững. Hai người buông tay mà căn nhà vẫn không đổ.

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