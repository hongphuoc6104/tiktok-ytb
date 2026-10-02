# Kịch bản — vocab-stand-script-546 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-stand-script-546/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "đứng" của từ STAND, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "đứng" của STAND mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng STAND trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn STAND với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "stand" còn nghĩa khác: quầy hàng, gian hàng [n, stand.n.booth]. Video này KHÔNG dạy nghĩa đó.
- Từ "stand" còn nghĩa khác: khán đài (sân vận động) [n, stand.n.grandstand]. Video này KHÔNG dạy nghĩa đó.
- Từ "stand" còn nghĩa khác: chịu đựng (can't stand) [v, stand.v.tolerate]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: STAND (v), chỉ dạy nghĩa "đứng"
- Mức độ người học: CEFR A1; chủ đề: Động từ thông dụng
- Mã mục trong kho từ vựng: stand.v.stand-basic (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm short; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 39.54–65.89 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.03–15.04 |
| SC02 | 7.66–12.77 |
| SC03 | 7.25–12.08 |
| SC04 | 8.77–14.62 |
| SC05 | 6.83–11.38 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Đứng vào chỗ để cả hai có trong ảnh — Nhịp 1

Mục đích: Introduce a concrete need and the selected sense.

Ảnh chỉ có người ngồi, người bạn muốn thêm cả hai vào khung! Stand nghĩa là đứng. "Be on your feet here." Bạn chuẩn bị chụp ảnh hư cấu, người bạn chỉ chỗ giúp hai người cùng xuất hiện.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot sits on simple chair as friend indicates clear photo position nearby. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot sits on simple chair as friend indicates clear photo position nearby.

Lý do: Introduce a concrete need and the selected sense.

Chữ được phép: “stand” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Ảnh chỉ có người ngồi, người bạn muốn thêm cả hai vào khung! Stand nghĩa là đứng. "Be on your feet here." Bạn chuẩn bị chụp ảnh hư cấu, người bạn chỉ chỗ giúp hai người cùng xuất hiện.” (lần 1) · Introduce a concrete need and the selected sense.

## SC02 — Đứng vào chỗ để cả hai có trong ảnh — Nhịp 2

Mục đích: Make the first model an action in the situation.

Người bạn nhắc: "Stand here." Đứng ở đây nhé. "This is the spot for the picture." Bạn đứng dậy rồi vào chỗ đã chỉ, để chiếc ghế không che phần người trong ảnh.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot seated on chair Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot seated on chair

Lý do: Make the first model an action in the situation.

Chữ được phép: Không có chữ/số

**Hình SC02_I2** — Mascot standing at indicated photo position, same blue shirt and single torso. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC02_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Mascot standing at indicated photo position, same blue shirt and single torso.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “Stand here.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Người bạn nhắc: "Stand here." Đứng ở đây nhé. "This is the spot for the picture." Bạn đứng dậy rồi vào chỗ đã chỉ, để chiếc ghế không che phần người trong ảnh.” (lần 1) · Make the first model an action in the situation.

Nhịp SC02_B2 → SC02_I2 · cut · vi: “Stand here.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC03 — Đứng vào chỗ để cả hai có trong ảnh — Nhịp 3

Mục đích: Advance the same story with the second model.

Bạn hỏi: "Can we stand together?" Mình đứng cùng nhau được không? "Both of us in one picture." Người bạn bước cạnh bạn, hai người kiểm lại khung trước khi chụp.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both stand together in photo position beside chair, generic camera on stable support. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both stand together in photo position beside chair, generic camera on stable support.

Lý do: Advance the same story with the second model.

Chữ được phép: “Can we stand together?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Bạn hỏi: "Can we stand together?" Mình đứng cùng nhau được không? "Both of us in one picture." Người bạn bước cạnh bạn, hai người kiểm lại khung trước khi chụp.” (lần 1) · Advance the same story with the second model.

## SC04 — Đứng vào chỗ để cả hai có trong ảnh — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn nhờ người bạn đứng ở chỗ mình chỉ. "Name the place to stand." Nói như lúc đang chuẩn bị tấm ảnh: "Stand here."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold photo position and short instruction. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold photo position and short instruction.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Stand here.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nhờ người bạn đứng ở chỗ mình chỉ. "Name the place to stand." Nói như lúc đang chuẩn bị tấm ảnh: "Stand here."” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Đứng vào chỗ để cả hai có trong ảnh — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"Stand here." Đứng ở đây nhé. "The frame now has both people." Hai người đã vào đúng chỗ trong câu chuyện, rồi chụp ảnh khi cả hai sẵn sàng.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot and companion pose together for fictional photo, chair remains to side. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion pose together for fictional photo, chair remains to side.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “Stand here.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Stand here." Đứng ở đây nhé. "The frame now has both people." Hai người đã vào đúng chỗ trong câu chuyện, rồi chụp ảnh khi cả hai sẵn sàng.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Ảnh chỉ có người ngồi, người bạn muốn thêm cả hai vào khung! Stand nghĩa là đứng. "Be on your feet here." Bạn chuẩn bị chụp ảnh hư cấu, người bạn chỉ chỗ giúp hai người cùng xuất hiện.
- R2 → SC01: Ảnh chỉ có người ngồi, người bạn muốn thêm cả hai vào khung! Stand nghĩa là đứng. "Be on your feet here." Bạn chuẩn bị chụp ảnh hư cấu, người bạn chỉ chỗ giúp hai người cùng xuất hiện.
- R2 → SC02: Người bạn nhắc: "Stand here." Đứng ở đây nhé. "This is the spot for the picture." Bạn đứng dậy rồi vào chỗ đã chỉ, để chiếc ghế không che phần người trong ảnh.
- R3 → SC02: Người bạn nhắc: "Stand here." Đứng ở đây nhé. "This is the spot for the picture." Bạn đứng dậy rồi vào chỗ đã chỉ, để chiếc ghế không che phần người trong ảnh.
- R3 → SC03: Bạn hỏi: "Can we stand together?" Mình đứng cùng nhau được không? "Both of us in one picture." Người bạn bước cạnh bạn, hai người kiểm lại khung trước khi chụp.
- R4 → SC04: Bạn muốn nhờ người bạn đứng ở chỗ mình chỉ. "Name the place to stand." Nói như lúc đang chuẩn bị tấm ảnh: "Stand here."
- R4 → SC05: "Stand here." Đứng ở đây nhé. "The frame now has both people." Hai người đã vào đúng chỗ trong câu chuyện, rồi chụp ảnh khi cả hai sẵn sàng.

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