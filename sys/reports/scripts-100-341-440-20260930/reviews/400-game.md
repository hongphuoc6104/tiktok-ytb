# Kịch bản — vocab-game-script-400 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-game-script-400/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "trận đấu" của từ GAME, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "trận đấu" của GAME mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng GAME trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn GAME với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "game" còn nghĩa khác: trò chơi [n, game.n.game]. Video này KHÔNG dạy nghĩa đó.
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
- Từ khoá duy nhất của video: GAME (n), chỉ dạy nghĩa "trận đấu"
- Mức độ người học: CEFR A1; chủ đề: Thể thao và rèn luyện
- Mã mục trong kho từ vựng: game.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 46.34–77.23 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.75–16.24 |
| SC02 | 8.7–14.51 |
| SC03 | 8.7–14.51 |
| SC04 | 11.22–18.69 |
| SC05 | 7.97–13.28 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Trận đấu đã bắt đầu chưa — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Vừa tới sân đã nghe mọi người reo! Game ở đây là trận đấu. Bạn chạy lịch cho kịp xem hai đội đá bóng, nhưng lúc tới ghế vẫn chưa biết trận bắt đầu được bao lâu; người bạn giữ chỗ đang vẫy.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot arrives at small spectator stand while friend waves, football match visible beyond fence. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot arrives at small spectator stand while friend waves, football match visible beyond fence.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “game” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Vừa tới sân đã nghe mọi người reo! Game ở đây là trận đấu. Bạn chạy lịch cho kịp xem hai đội đá bóng, nhưng lúc tới ghế vẫn chưa biết trận bắt đầu được bao lâu; người bạn giữ chỗ đang vẫy.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Trận đấu đã bắt đầu chưa — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn hỏi: "Has the game started?" Trận đấu bắt đầu chưa? The game chỉ trận hai người tới xem. Người bạn gật đầu, chỉ cầu thủ đang di chuyển trên sân để bạn theo nhịp đang diễn ra.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend indicates active match while mascot sits in saved seat. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend indicates active match while mascot sits in saved seat.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Has the game started?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Has the game started?" Trận đấu bắt đầu chưa? The game chỉ trận hai người tới xem. Người bạn gật đầu, chỉ cầu thủ đang di chuyển trên sân để bạn theo nhịp đang diễn ra.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Trận đấu đã bắt đầu chưa — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Bạn hỏi tiếp: "Is the game over?" Trận đấu kết thúc chưa? Over là đã kết thúc; lúc này cầu thủ vẫn chơi, nên bạn ngồi xuống xem thay vì tưởng tiếng reo là dấu hiệu hết trận.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Players continue football on field, both spectators watch attentively. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Players continue football on field, both spectators watch attentively.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “Is the game over?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn hỏi tiếp: "Is the game over?" Trận đấu kết thúc chưa? Over là đã kết thúc; lúc này cầu thủ vẫn chơi, nên bạn ngồi xuống xem thay vì tưởng tiếng reo là dấu hiệu hết trận.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Trận đấu đã bắt đầu chưa — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn vừa tới và muốn hỏi trận đã bắt đầu chưa. Chọn "Has the game started?" hay "Is the game over?" rồi nói câu đúng với điều cần biết.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 6 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Match in progress and two question options displayed equally. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Match in progress and two question options displayed equally.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “Has the game started?” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.; “Is the game over?” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn vừa tới và muốn hỏi trận đã bắt đầu chưa. Chọn "Has the game started?" hay "Is the game over?" rồi nói câu đúng với điều cần biết.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Trận đấu đã bắt đầu chưa — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"Has the game started?" Trận đấu bắt đầu chưa? Bạn đã có chỗ ngồi và biết trận vẫn còn. Tiếng reo tiếp theo không còn đến từ một câu chuyện mình chưa kịp theo dõi.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot and friend cheer from seats as match continues, no score or real teams shown. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and friend cheer from seats as match continues, no score or real teams shown.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “Has the game started?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Has the game started?" Trận đấu bắt đầu chưa? Bạn đã có chỗ ngồi và biết trận vẫn còn. Tiếng reo tiếp theo không còn đến từ một câu chuyện mình chưa kịp theo dõi.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người đồng hành trong tình huống: Adult friend or companion. Minimal flat ink style. Maintain age, gender, clothing and identity across all scenes; use mustard top and only explicitly needed accessory. Distinct from canonical mascot.; Plain mustard-yellow top, with only scenario-required accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Vừa tới sân đã nghe mọi người reo! Game ở đây là trận đấu. Bạn chạy lịch cho kịp xem hai đội đá bóng, nhưng lúc tới ghế vẫn chưa biết trận bắt đầu được bao lâu; người bạn giữ chỗ đang vẫy.
- R2 → SC01: Vừa tới sân đã nghe mọi người reo! Game ở đây là trận đấu. Bạn chạy lịch cho kịp xem hai đội đá bóng, nhưng lúc tới ghế vẫn chưa biết trận bắt đầu được bao lâu; người bạn giữ chỗ đang vẫy.
- R2 → SC02: Bạn hỏi: "Has the game started?" Trận đấu bắt đầu chưa? The game chỉ trận hai người tới xem. Người bạn gật đầu, chỉ cầu thủ đang di chuyển trên sân để bạn theo nhịp đang diễn ra.
- R3 → SC02: Bạn hỏi: "Has the game started?" Trận đấu bắt đầu chưa? The game chỉ trận hai người tới xem. Người bạn gật đầu, chỉ cầu thủ đang di chuyển trên sân để bạn theo nhịp đang diễn ra.
- R3 → SC03: Bạn hỏi tiếp: "Is the game over?" Trận đấu kết thúc chưa? Over là đã kết thúc; lúc này cầu thủ vẫn chơi, nên bạn ngồi xuống xem thay vì tưởng tiếng reo là dấu hiệu hết trận.
- R4 → SC04: Bạn vừa tới và muốn hỏi trận đã bắt đầu chưa. Chọn "Has the game started?" hay "Is the game over?" rồi nói câu đúng với điều cần biết.
- R4 → SC05: "Has the game started?" Trận đấu bắt đầu chưa? Bạn đã có chỗ ngồi và biết trận vẫn còn. Tiếng reo tiếp theo không còn đến từ một câu chuyện mình chưa kịp theo dõi.

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