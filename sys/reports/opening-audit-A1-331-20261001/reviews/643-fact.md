# Kịch bản — vocab-fact-script-643 — revision 2



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-fact-script-643/revisions/content/2/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "sự thật, sự việc có thật" của từ FACT, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "sự thật, sự việc có thật" của FACT mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng FACT trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn FACT với các nghĩa khác của chính từ này

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
- Từ khoá duy nhất của video: FACT (n), chỉ dạy nghĩa "sự thật, sự việc có thật"
- Mức độ người học: CEFR A1; chủ đề: Danh từ thông dụng
- Mã mục trong kho từ vựng: fact.n.truth (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.
- Fact có cùng nghĩa lõi sự thật/dữ kiện có căn cứ trong ngữ cảnh khoa học và thường ngày. Hai mã kho tách ngữ cảnh, không phải hai nghĩa từ vựng loại trừ nhau. Bài này giữ ngữ cảnh kiểm thông tin cuộc hẹn hư cấu; không phủ nhận fact trong khoa học.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm medium; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.
- Làm rõ phạm vi trước chốt lời dẫn/neo ngày 01/10/2026.

6 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 62.44–104.05 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.6–17.66 |
| SC02 | 10.79–17.98 |
| SC03 | 11.41–19.02 |
| SC04 | 9.12–15.2 |
| SC05 | 9.94–16.56 |
| SC06 | 10.58–17.63 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Điều đã xảy ra trong lời mời được giữ rõ — Nhịp 1

Mục đích: Open on the immediate visible need or surprising detail, then establish the selected meaning; do not start with an introductory title.

Mỗi người nhớ một giờ, kiểm lời mời thôi! Fact ở đây là sự thật, sự việc có thật. "Something known to be true in our story." Hai người kiểm cuộc hẹn hư cấu, không muốn lấy ký ức chưa đối chiếu làm thông tin cuối.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion compare fictional invitation with conflicting recollections, known source stays between them. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion compare fictional invitation with conflicting recollections, known source stays between them.

Lý do: Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

Chữ được phép: “fact” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Mỗi người nhớ một giờ, kiểm lời mời thôi! Fact ở đây là sự thật, sự việc có thật. "Something known to be true in our story." Hai người kiểm cuộc hẹn hư cấu, không muốn lấy ký ức chưa đối chiếu làm thông tin cuối.” (lần 1) · Make the first-frame problem or contrast intelligible immediately, linked to the selected sense and later resolution.

## SC02 — Điều đã xảy ra trong lời mời được giữ rõ — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Bạn nói: "Let's check the facts." Cùng kiểm các sự việc đã xác định nhé. "Look at what the invitation actually says." Người bạn đặt bản đã chốt trước mặt, hai người đọc phần của cuộc hẹn trong câu chuyện thay vì tranh luận ai nhớ mạnh hơn.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Both inspect agreed fictional invitation as source for event details. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both inspect agreed fictional invitation as source for event details.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “Let's check the facts.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "Let's check the facts." Cùng kiểm các sự việc đã xác định nhé. "Look at what the invitation actually says." Người bạn đặt bản đã chốt trước mặt, hai người đọc phần của cuộc hẹn trong câu chuyện thay vì tranh luận ai nhớ mạnh hơn.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Điều đã xảy ra trong lời mời được giữ rõ — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Thông tin đúng cần căn cứ để phân biệt với một lời mình còn đoán. "Our check has a place to look." Ở tình huống này, hai người dùng bản lời mời hư cấu; đây không phải một thí nghiệm hay một dữ kiện khoa học mới được đo trong video.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both separate confirmed fictional invitation details from unresolved thought cards. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both separate confirmed fictional invitation details from unresolved thought cards.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “fact” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Thông tin đúng cần căn cứ để phân biệt với một lời mình còn đoán. "Our check has a place to look." Ở tình huống này, hai người dùng bản lời mời hư cấu; đây không phải một thí nghiệm hay một dữ kiện khoa học mới được đo trong video.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Điều đã xảy ra trong lời mời được giữ rõ — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Bạn nói: "That's a fact." Đó là một sự thật đã được xác định. "It matches the information we checked." Người bạn ghi lại phần đã đối chiếu, để hai người mang cùng thông tin tới buổi gặp hư cấu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Companion records matched fictional invitation detail while mascot confirms. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion records matched fictional invitation detail while mascot confirms.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “That's a fact.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn nói: "That's a fact." Đó là một sự thật đã được xác định. "It matches the information we checked." Người bạn ghi lại phần đã đối chiếu, để hai người mang cùng thông tin tới buổi gặp hư cấu.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Điều đã xảy ra trong lời mời được giữ rõ — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn muốn rủ kiểm điều đã được xác định trước khi chọn thông tin theo vai. "Ask for a careful check." Hãy nói: "Let's check the facts."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold fictional invitation and full model sentence, no invented real-world evidence. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional invitation and full model sentence, no invented real-world evidence.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Ask for a careful check.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.; “Let's check the facts.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn muốn rủ kiểm điều đã được xác định trước khi chọn thông tin theo vai. "Ask for a careful check." Hãy nói: "Let's check the facts."” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Điều đã xảy ra trong lời mời được giữ rõ — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Let's check the facts." Cùng kiểm các sự việc nhé. "The plan now uses the information we found in the story." Hai người đã ghi phần khớp lời mời hư cấu, giữ lại các câu hỏi chưa rõ để hỏi thêm chứ không biến chúng thành fact.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both keep confirmed fictional plan and separate unresolved question note. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both keep confirmed fictional plan and separate unresolved question note.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Let's check the facts.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Let's check the facts." Cùng kiểm các sự việc nhé. "The plan now uses the information we found in the story." Hai người đã ghi phần khớp lời mời hư cấu, giữ lại các câu hỏi chưa rõ để hỏi thêm chứ không biến chúng thành fact.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Mỗi người nhớ một giờ, kiểm lời mời thôi! Fact ở đây là sự thật, sự việc có thật. "Something known to be true in our story." Hai người kiểm cuộc hẹn hư cấu, không muốn lấy ký ức chưa đối chiếu làm thông tin cuối.
- R2 → SC01: Mỗi người nhớ một giờ, kiểm lời mời thôi! Fact ở đây là sự thật, sự việc có thật. "Something known to be true in our story." Hai người kiểm cuộc hẹn hư cấu, không muốn lấy ký ức chưa đối chiếu làm thông tin cuối.
- R2 → SC02: Bạn nói: "Let's check the facts." Cùng kiểm các sự việc đã xác định nhé. "Look at what the invitation actually says." Người bạn đặt bản đã chốt trước mặt, hai người đọc phần của cuộc hẹn trong câu chuyện thay vì tranh luận ai nhớ mạnh hơn.
- R3 → SC02: Bạn nói: "Let's check the facts." Cùng kiểm các sự việc đã xác định nhé. "Look at what the invitation actually says." Người bạn đặt bản đã chốt trước mặt, hai người đọc phần của cuộc hẹn trong câu chuyện thay vì tranh luận ai nhớ mạnh hơn.
- R2 → SC03: Thông tin đúng cần căn cứ để phân biệt với một lời mình còn đoán. "Our check has a place to look." Ở tình huống này, hai người dùng bản lời mời hư cấu; đây không phải một thí nghiệm hay một dữ kiện khoa học mới được đo trong video.
- R3 → SC04: Bạn nói: "That's a fact." Đó là một sự thật đã được xác định. "It matches the information we checked." Người bạn ghi lại phần đã đối chiếu, để hai người mang cùng thông tin tới buổi gặp hư cấu.
- R4 → SC05: Bạn muốn rủ kiểm điều đã được xác định trước khi chọn thông tin theo vai. "Ask for a careful check." Hãy nói: "Let's check the facts."
- R4 → SC06: "Let's check the facts." Cùng kiểm các sự việc nhé. "The plan now uses the information we found in the story." Hai người đã ghi phần khớp lời mời hư cấu, giữ lại các câu hỏi chưa rõ để hỏi thêm chứ không biến chúng thành fact.

## Phát biểu và nguồn

Không có.

## Nguồn

Không có.

## Phản hồi cần xử lý

- 18199: duyệt kịch bản lại, và viết lại nếu chưa đạt: kiểm tra mở đầu bài 3s đầu template mở đầu tránh trùng lặp tạo cảm giác đã xem, ưu tiên đưa phần hay lên đầu và giữ chân người xem nhất có thể.

Bài 643: sửa SC01 bằng câu mở đã chốt và hình vào thẳng chi tiết; giữ nghĩa chọn, mẫu, thực hành và phản hồi. Không duyệt content thay người dùng.

## Kết quả sửa

- 18199 — addressed: Đã rà 3 giây đầu: mở bằng “Mỗi người nhớ một giờ, kiểm lời mời thôi!”; đưa chi tiết có ích lên trước, đổi hình/camera mở để thấy đúng vấn đề. Giữ nguyên các cảnh sau, câu mẫu, khoảng chờ và payoff. Thời gian là ước tính, chưa đo khả năng giữ chân.; cảnh: SC01

## Vấn đề còn lại

Không có.

## Thay đổi so với bản trước

Cảnh thay đổi: SC01

Trường thay đổi: scenes, coverage, outline, revision_response