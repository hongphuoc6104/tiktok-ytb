# Kịch bản — vocab-game-script-435 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-game-script-435/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "trò chơi" của từ GAME, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "trò chơi" của GAME mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng GAME trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn GAME với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "game" còn nghĩa khác: trận đấu [n, game.n]. Video này KHÔNG dạy nghĩa đó.
- Từ "game" còn nghĩa khác: thú rừng (để săn bắn) [n, game.n.wild-animals]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: GAME (n), chỉ dạy nghĩa "trò chơi"
- Mức độ người học: CEFR A1; chủ đề: Giải trí và truyền thông
- Mã mục trong kho từ vựng: game.n.game (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 46.76–77.91 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.22–15.36 |
| SC02 | 8.29–13.81 |
| SC03 | 8.91–14.85 |
| SC04 | 11.31–18.85 |
| SC05 | 9.03–15.04 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Trò chơi trên bàn chưa có người thứ ba — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Bàn đã bày đủ mà vẫn chừa một chỗ cho bạn! Game trong bài này là trò chơi. Hai người bạn đang chuẩn bị thẻ hình và quân trên bàn, bạn vừa tới cửa thì được kéo ghế mời tham gia.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot arrives at table where two adults set picture cards and tokens, third seat empty. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot arrives at table where two adults set picture cards and tokens, third seat empty.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “game” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Bàn đã bày đủ mà vẫn chừa một chỗ cho bạn! Game trong bài này là trò chơi. Hai người bạn đang chuẩn bị thẻ hình và quân trên bàn, bạn vừa tới cửa thì được kéo ghế mời tham gia.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Trò chơi trên bàn chưa có người thứ ba — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Người bạn rủ: "Let's play a game." Cùng chơi một trò nhé. A game gọi trò đang đề xuất; bạn ngồi xuống, nghe cách lấy thẻ và mục tiêu trước khi chạm vào quân của mình.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend explains tabletop card game to seated mascot, tokens kept in starting positions. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend explains tabletop card game to seated mascot, tokens kept in starting positions.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Let's play a game.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Người bạn rủ: "Let's play a game." Cùng chơi một trò nhé. A game gọi trò đang đề xuất; bạn ngồi xuống, nghe cách lấy thẻ và mục tiêu trước khi chạm vào quân của mình.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Trò chơi trên bàn chưa có người thứ ba — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Bạn hỏi: "How do we play this game?" Trò này chơi thế nào? This game chỉ bộ đang bày trên bàn; một câu hỏi giúp bạn biết cần làm gì trong lượt đầu, thay vì đoán theo người khác.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Mascot asks while pointing to picture cards, friend demonstrates one simple turn. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot asks while pointing to picture cards, friend demonstrates one simple turn.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “How do we play this game?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn hỏi: "How do we play this game?" Trò này chơi thế nào? This game chỉ bộ đang bày trên bàn; một câu hỏi giúp bạn biết cần làm gì trong lượt đầu, thay vì đoán theo người khác.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Trò chơi trên bàn chưa có người thứ ba — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn mới gặp một trò trên bàn và chưa biết chơi. Nói lại "How do we play this game?" rồi hình dung mình đang hỏi điều gì trước lượt đầu.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 6 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold tabletop game and full question, no specific rule answer shown. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold tabletop game and full question, no specific rule answer shown.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “How do we play this game?” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn mới gặp một trò trên bàn và chưa biết chơi. Nói lại "How do we play this game?" rồi hình dung mình đang hỏi điều gì trước lượt đầu.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Trò chơi trên bàn chưa có người thứ ba — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"How do we play this game?" Trò này chơi thế nào? Bạn đã được hướng dẫn, chiếc ghế trống có người và ván mới bắt đầu. Game ở đây gọi trò chơi, không phải trận thi đấu trên sân.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Three adults begin picture-card game together, mascot takes first guided turn. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Three adults begin picture-card game together, mascot takes first guided turn.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “How do we play this game?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"How do we play this game?" Trò này chơi thế nào? Bạn đã được hướng dẫn, chiếc ghế trống có người và ván mới bắt đầu. Game ở đây gọi trò chơi, không phải trận thi đấu trên sân.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người đồng hành trong tình huống: Adult friend explaining tabletop game. Minimal flat ink style. Maintain age, gender, clothing and identity across all scenes; use mustard top and only explicitly needed accessory. Distinct from canonical mascot.; Plain mustard-yellow top, with only scenario-required accessories.
- Người phụ khi tình huống yêu cầu: Adult third participant. Minimal flat ink style; consistent role, adult identity and lavender clothing with only scenario-required outerwear. Distinct from mascot and companion.; Plain lavender top; scenario-required accessories only.

## Đối chiếu ý bắt buộc

- R1 → SC01: Bàn đã bày đủ mà vẫn chừa một chỗ cho bạn! Game trong bài này là trò chơi. Hai người bạn đang chuẩn bị thẻ hình và quân trên bàn, bạn vừa tới cửa thì được kéo ghế mời tham gia.
- R2 → SC01: Bàn đã bày đủ mà vẫn chừa một chỗ cho bạn! Game trong bài này là trò chơi. Hai người bạn đang chuẩn bị thẻ hình và quân trên bàn, bạn vừa tới cửa thì được kéo ghế mời tham gia.
- R2 → SC02: Người bạn rủ: "Let's play a game." Cùng chơi một trò nhé. A game gọi trò đang đề xuất; bạn ngồi xuống, nghe cách lấy thẻ và mục tiêu trước khi chạm vào quân của mình.
- R3 → SC02: Người bạn rủ: "Let's play a game." Cùng chơi một trò nhé. A game gọi trò đang đề xuất; bạn ngồi xuống, nghe cách lấy thẻ và mục tiêu trước khi chạm vào quân của mình.
- R3 → SC03: Bạn hỏi: "How do we play this game?" Trò này chơi thế nào? This game chỉ bộ đang bày trên bàn; một câu hỏi giúp bạn biết cần làm gì trong lượt đầu, thay vì đoán theo người khác.
- R4 → SC04: Bạn mới gặp một trò trên bàn và chưa biết chơi. Nói lại "How do we play this game?" rồi hình dung mình đang hỏi điều gì trước lượt đầu.
- R4 → SC05: "How do we play this game?" Trò này chơi thế nào? Bạn đã được hướng dẫn, chiếc ghế trống có người và ván mới bắt đầu. Game ở đây gọi trò chơi, không phải trận thi đấu trên sân.

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