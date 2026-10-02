# Kịch bản — vocab-actress-script-450 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-actress-script-450/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "diễn viên nữ" của từ ACTRESS, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "diễn viên nữ" của ACTRESS mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng ACTRESS trong ít nhất một câu
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
- Từ khoá duy nhất của video: ACTRESS (n), chỉ dạy nghĩa "diễn viên nữ"
- Mức độ người học: CEFR A1; chủ đề: Âm nhạc và nghệ thuật
- Mã mục trong kho từ vựng: actress.n (dùng để đánh dấu đã làm)
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

VI: 41.3–68.83 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.12–15.2 |
| SC02 | 7.98–13.31 |
| SC03 | 8.5–14.16 |
| SC04 | 8.98–14.97 |
| SC05 | 6.72–11.19 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Tên vai nghề nghiệp của người trên áp phích — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Mình từng xem cô ấy đóng phim rồi! Actress là diễn viên nữ. "A woman who acts." Bạn chọn phim cùng người bạn, thấy người trên áp phích hư cấu từng xuất hiện trong bộ phim hai người đã xem.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot recognizes the fictional female actress on the movie poster, companion holds the same film selection; no real celebrity. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot recognizes the fictional female actress on the movie poster, companion holds the same film selection; no real celebrity.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “actress” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Mình từng xem cô ấy đóng phim rồi! Actress là diễn viên nữ. "A woman who acts." Bạn chọn phim cùng người bạn, thấy người trên áp phích hư cấu từng xuất hiện trong bộ phim hai người đã xem.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Tên vai nghề nghiệp của người trên áp phích — Nhịp 2

Mục đích: Make the first model an action in the situation.

Bạn hỏi: "Who's that actress?" Diễn viên nữ kia là ai? "That woman, in the film." Người bạn mở phần giới thiệu để tìm đúng người, không đoán tên từ một tấm ảnh nhỏ.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend checks generic cast profile of same adult female performer while mascot points to poster. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend checks generic cast profile of same adult female performer while mascot points to poster.

Lý do: Make the first model an action in the situation.

Chữ được phép: “Who's that actress?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn hỏi: "Who's that actress?" Diễn viên nữ kia là ai? "That woman, in the film." Người bạn mở phần giới thiệu để tìm đúng người, không đoán tên từ một tấm ảnh nhỏ.” (lần 1) · Make the first model an action in the situation.

## SC03 — Tên vai nghề nghiệp của người trên áp phích — Nhịp 3

Mục đích: Advance the same story with the second model.

Người bạn kể: "She's my favorite actress." Cô ấy là diễn viên nữ tôi thích nhất. "My favorite performer." Bạn hiểu vì sao người ấy muốn chọn bộ phim này, rồi xem tiếp nội dung giới thiệu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend indicates favorite fictional performer, mascot reviews plain plot card without printed title. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend indicates favorite fictional performer, mascot reviews plain plot card without printed title.

Lý do: Advance the same story with the second model.

Chữ được phép: “She's my favorite actress.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn kể: "She's my favorite actress." Cô ấy là diễn viên nữ tôi thích nhất. "My favorite performer." Bạn hiểu vì sao người ấy muốn chọn bộ phim này, rồi xem tiếp nội dung giới thiệu.” (lần 1) · Advance the same story with the second model.

## SC04 — Tên vai nghề nghiệp của người trên áp phích — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn hỏi về diễn viên nữ trên áp phích. "Ask who she is." Nói như trong cuộc trò chuyện khi chọn phim: "Who's that actress?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold fictional female performer poster and full question. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional female performer poster and full question.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Who's that actress?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn hỏi về diễn viên nữ trên áp phích. "Ask who she is." Nói như trong cuộc trò chuyện khi chọn phim: "Who's that actress?"” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Tên vai nghề nghiệp của người trên áp phích — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"Who's that actress?" Diễn viên nữ ấy là ai? "Now you can ask." Hai người đã tìm đúng phần giới thiệu và chọn được phim muốn xem cùng nhau.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot and friend confirm fictional movie choice with same performer thumbnail. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and friend confirm fictional movie choice with same performer thumbnail.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “Who's that actress?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Who's that actress?" Diễn viên nữ ấy là ai? "Now you can ask." Hai người đã tìm đúng phần giới thiệu và chọn được phim muốn xem cùng nhau.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.
- Người tham gia hoặc nhân vật bổ trợ: Fictional adult female actress, appears only on the poster or screen within the scene; same identity throughout. Minimal flat ink style and ordinary adult proportions.; Single plain lavender top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Mình từng xem cô ấy đóng phim rồi! Actress là diễn viên nữ. "A woman who acts." Bạn chọn phim cùng người bạn, thấy người trên áp phích hư cấu từng xuất hiện trong bộ phim hai người đã xem.
- R2 → SC01: Mình từng xem cô ấy đóng phim rồi! Actress là diễn viên nữ. "A woman who acts." Bạn chọn phim cùng người bạn, thấy người trên áp phích hư cấu từng xuất hiện trong bộ phim hai người đã xem.
- R2 → SC02: Bạn hỏi: "Who's that actress?" Diễn viên nữ kia là ai? "That woman, in the film." Người bạn mở phần giới thiệu để tìm đúng người, không đoán tên từ một tấm ảnh nhỏ.
- R3 → SC02: Bạn hỏi: "Who's that actress?" Diễn viên nữ kia là ai? "That woman, in the film." Người bạn mở phần giới thiệu để tìm đúng người, không đoán tên từ một tấm ảnh nhỏ.
- R3 → SC03: Người bạn kể: "She's my favorite actress." Cô ấy là diễn viên nữ tôi thích nhất. "My favorite performer." Bạn hiểu vì sao người ấy muốn chọn bộ phim này, rồi xem tiếp nội dung giới thiệu.
- R4 → SC04: Bạn muốn hỏi về diễn viên nữ trên áp phích. "Ask who she is." Nói như trong cuộc trò chuyện khi chọn phim: "Who's that actress?"
- R4 → SC05: "Who's that actress?" Diễn viên nữ ấy là ai? "Now you can ask." Hai người đã tìm đúng phần giới thiệu và chọn được phim muốn xem cùng nhau.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 16946: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 450: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 16946 — addressed: Đã rà 3 giây đầu: mở bằng “Mình từng xem cô ấy đóng phim rồi!”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response