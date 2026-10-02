# Kịch bản — vocab-login-script-469 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-login-script-469/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "đăng nhập" của từ LOG IN, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "đăng nhập" của LOG IN mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng LOG IN trong ít nhất một câu
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
- Từ khoá duy nhất của video: LOG IN (v), chỉ dạy nghĩa "đăng nhập"
- Mức độ người học: CEFR A1; chủ đề: Công nghệ và Internet
- Mã mục trong kho từ vựng: login.v (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm short; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.
- Mã kho login.v được giữ nguyên; dạng động từ chuẩn là log in (Cambridge Dictionary: https://dictionary.cambridge.org/dictionary/english/log-in). Không dạy login như động từ, không thay mục bằng mục A2.

5 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 44.67–74.44 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.18–16.97 |
| SC02 | 8.5–14.16 |
| SC03 | 8.82–14.69 |
| SC04 | 9.09–15.15 |
| SC05 | 8.08–13.47 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Tài liệu còn sau màn hình đăng nhập — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Tài liệu đây rồi, sao chưa mở được? Log in nghĩa là đăng nhập; động từ này viết thành hai từ. "Enter your account." Bạn đang vào ứng dụng lớp học hư cấu, màn hình yêu cầu đăng nhập trước khi xem tài liệu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot sees class document tile behind a generic login gate on phone, companion indicates account-entry step; no personal data. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot sees class document tile behind a generic login gate on phone, companion indicates account-entry step; no personal data.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “log in” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Tài liệu đây rồi, sao chưa mở được? Log in nghĩa là đăng nhập; động từ này viết thành hai từ. "Enter your account." Bạn đang vào ứng dụng lớp học hư cấu, màn hình yêu cầu đăng nhập trước khi xem tài liệu.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Tài liệu còn sau màn hình đăng nhập — Nhịp 2

Mục đích: Make the first model an action in the situation.

Bạn nói: "I can't log in." Tôi chưa đăng nhập được. "The account is not open yet." Người bạn nhìn màn hình cùng bạn để hiểu bước còn thiếu, không hỏi bạn đọc mật khẩu thành tiếng.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend and mascot examine generic sign-in fields, no credentials shown or requested. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend and mascot examine generic sign-in fields, no credentials shown or requested.

Lý do: Make the first model an action in the situation.

Chữ được phép: “I can't log in.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "I can't log in." Tôi chưa đăng nhập được. "The account is not open yet." Người bạn nhìn màn hình cùng bạn để hiểu bước còn thiếu, không hỏi bạn đọc mật khẩu thành tiếng.” (lần 1) · Make the first model an action in the situation.

## SC03 — Tài liệu còn sau màn hình đăng nhập — Nhịp 3

Mục đích: Advance the same story with the second model.

Trên hướng dẫn có câu: "Please log in first." Hãy đăng nhập trước. "First, enter your account." Bạn hoàn tất bước đăng nhập bằng tài khoản của mình trong câu chuyện, rồi màn hình chuyển tới tài liệu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Generic sign-in screen without personal data Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Generic sign-in screen without personal data

Lý do: Advance the same story with the second model.

Chữ được phép: Không có chữ/số

**Hình SC03_I2** — Fictional course materials screen appears after character's authorized sign-in. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: SC03_I1; giữ: Preserve base camera, background, identities, clothing and all unchanged props; only the specified state and permitted teaching text may change.; đổi: Fictional course materials screen appears after character's authorized sign-in.

Lý do: Show the explicitly described before/after state with the same camera and identities.

Chữ được phép: “Please log in first.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Trên hướng dẫn có câu: "Please log in first." Hãy đăng nhập trước. "First, enter your account." Bạn hoàn tất bước đăng nhập bằng tài khoản của mình trong câu chuyện, rồi màn hình chuyển tới tài liệu.” (lần 1) · Advance the same story with the second model.

Nhịp SC03_B2 → SC03_I2 · cut · vi: “Please log in first.” (lần 1) · Show the explicitly described before/after state with the same camera and identities.

## SC04 — Tài liệu còn sau màn hình đăng nhập — Lượt thực hành

Mục đích: Invite a supported learner response and leave time before feedback.

Bạn muốn nhắc đăng nhập trước. "Give the short instruction." Log in là hai từ trong câu mình đang dùng. Nói lại: "Please log in first."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold fictional app and full instruction, no personal information. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional app and full instruction, no personal information.

Lý do: Invite a supported learner response and leave time before feedback.

Chữ được phép: “Please log in first.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nhắc đăng nhập trước. "Give the short instruction." Log in là hai từ trong câu mình đang dùng. Nói lại: "Please log in first."” (lần 1) · Invite a supported learner response and leave time before feedback.

## SC05 — Tài liệu còn sau màn hình đăng nhập — Phản hồi và kết quả

Mục đích: Provide the correct response and resolve the opening need.

"Please log in first." Hãy đăng nhập trước. "Now the page can open." Bạn đã hiểu bước cần làm trước lúc xem tài liệu, và dùng đúng dạng động từ log in trong lời nhắc.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot views generic course document on phone, friend points to opened material. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot views generic course document on phone, friend points to opened material.

Lý do: Provide the correct response and resolve the opening need.

Chữ được phép: “Please log in first.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"Please log in first." Hãy đăng nhập trước. "Now the page can open." Bạn đã hiểu bước cần làm trước lúc xem tài liệu, và dùng đúng dạng động từ log in trong lời nhắc.” (lần 1) · Provide the correct response and resolve the opening need.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Tài liệu đây rồi, sao chưa mở được? Log in nghĩa là đăng nhập; động từ này viết thành hai từ. "Enter your account." Bạn đang vào ứng dụng lớp học hư cấu, màn hình yêu cầu đăng nhập trước khi xem tài liệu.
- R2 → SC01: Tài liệu đây rồi, sao chưa mở được? Log in nghĩa là đăng nhập; động từ này viết thành hai từ. "Enter your account." Bạn đang vào ứng dụng lớp học hư cấu, màn hình yêu cầu đăng nhập trước khi xem tài liệu.
- R2 → SC02: Bạn nói: "I can't log in." Tôi chưa đăng nhập được. "The account is not open yet." Người bạn nhìn màn hình cùng bạn để hiểu bước còn thiếu, không hỏi bạn đọc mật khẩu thành tiếng.
- R3 → SC02: Bạn nói: "I can't log in." Tôi chưa đăng nhập được. "The account is not open yet." Người bạn nhìn màn hình cùng bạn để hiểu bước còn thiếu, không hỏi bạn đọc mật khẩu thành tiếng.
- R3 → SC03: Trên hướng dẫn có câu: "Please log in first." Hãy đăng nhập trước. "First, enter your account." Bạn hoàn tất bước đăng nhập bằng tài khoản của mình trong câu chuyện, rồi màn hình chuyển tới tài liệu.
- R4 → SC04: Bạn muốn nhắc đăng nhập trước. "Give the short instruction." Log in là hai từ trong câu mình đang dùng. Nói lại: "Please log in first."
- R4 → SC05: "Please log in first." Hãy đăng nhập trước. "Now the page can open." Bạn đã hiểu bước cần làm trước lúc xem tài liệu, và dùng đúng dạng động từ log in trong lời nhắc.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 17081: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 469: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 17081 — addressed: Đã rà 3 giây đầu: mở bằng “Tài liệu đây rồi, sao chưa mở được?”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response