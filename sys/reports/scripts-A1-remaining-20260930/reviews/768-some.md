# Kịch bản — vocab-some-script-768 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-some-script-768/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "một số" của từ SOME, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "một số" của SOME mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng SOME trong ít nhất một câu
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
- Từ khoá duy nhất của video: SOME (det), chỉ dạy nghĩa "một số"
- Mức độ người học: CEFR A1; chủ đề: Từ chức năng và liên kết
- Mã mục trong kho từ vựng: some.det (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm long; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

7 cảnh · 7 hình logic · 7 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 74.8–124.66 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.11–18.51 |
| SC02 | 10.6–17.66 |
| SC03 | 10.69–17.82 |
| SC04 | 10.07–16.78 |
| SC05 | 11.09–18.49 |
| SC06 | 8.77–14.62 |
| SC07 | 12.47–20.78 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Có đồ để dùng, nhưng chưa cần nêu con số — Nhịp 1

Mục đích: Establish the need and one selected meaning promptly.

Muốn làm thiệp mà chưa biết trong hộp có vật liệu gì! Some là một số, một lượng chưa nêu con số chính xác. "There is an unspecified amount or number." Bạn cần biết có đồ để bắt đầu, rồi mới kiểm lượng đủ cho công việc của nhóm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion inspect closed craft supply box beside empty work surface. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion inspect closed craft supply box beside empty work surface.

Lý do: Establish the need and one selected meaning promptly.

Chữ được phép: “some” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Muốn làm thiệp mà chưa biết trong hộp có vật liệu gì! Some là một số, một lượng chưa nêu con số chính xác. "There is an unspecified amount or number." Bạn cần biết có đồ để bắt đầu, rồi mới kiểm lượng đủ cho công việc của nhóm.” (lần 1) · Establish the need and one selected meaning promptly.

## SC02 — Có đồ để dùng, nhưng chưa cần nêu con số — Nhịp 2

Mục đích: Use the first model at the point where the speaker needs it.

Bạn mở hộp và nói: "We have some paper." Chúng ta có một ít giấy. "There is paper available to use." Người bạn lấy phần giấy ra, trải ở bàn; câu báo có vật liệu, chưa khẳng định số tờ hoặc đã đủ cho mọi người.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot opens box revealing paper supply, companion lays some sheets on table. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot opens box revealing paper supply, companion lays some sheets on table.

Lý do: Use the first model at the point where the speaker needs it.

Chữ được phép: “We have some paper.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn mở hộp và nói: "We have some paper." Chúng ta có một ít giấy. "There is paper available to use." Người bạn lấy phần giấy ra, trải ở bàn; câu báo có vật liệu, chưa khẳng định số tờ hoặc đã đủ cho mọi người.” (lần 1) · Use the first model at the point where the speaker needs it.

## SC03 — Có đồ để dùng, nhưng chưa cần nêu con số — Nhịp 3

Mục đích: Show the condition or contrast that makes this usage matter.

Paper trong mẫu đang nói vật liệu, không nêu con số tờ. "Some does not give an exact amount." Nếu cần biết số cụ thể, nhóm còn phải kiểm. Bài không đánh đồng có một ít với chắc chắn đủ cho mọi nhu cầu ở cả lớp.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both inspect paper supply relative to current small activity, no invented measurement labels. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both inspect paper supply relative to current small activity, no invented measurement labels.

Lý do: Show the condition or contrast that makes this usage matter.

Chữ được phép: “some” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Paper trong mẫu đang nói vật liệu, không nêu con số tờ. "Some does not give an exact amount." Nếu cần biết số cụ thể, nhóm còn phải kiểm. Bài không đánh đồng có một ít với chắc chắn đủ cho mọi nhu cầu ở cả lớp.” (lần 1) · Show the condition or contrast that makes this usage matter.

## SC04 — Có đồ để dùng, nhưng chưa cần nêu con số — Nhịp 4

Mục đích: Use the second model to advance or compare within the same story.

Bạn tìm thêm và báo: "There are some pens in the box." Có một số bút trong hộp. "These are separate items, so pens is plural." Người bạn nhìn các chiếc bút còn dùng được, chọn những màu cần cho tấm thiệp đang làm.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Companion finds several capped pens in same supply box and selects useful colors. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Companion finds several capped pens in same supply box and selects useful colors.

Lý do: Use the second model to advance or compare within the same story.

Chữ được phép: “There are some pens in the box.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Bạn tìm thêm và báo: "There are some pens in the box." Có một số bút trong hộp. "These are separate items, so pens is plural." Người bạn nhìn các chiếc bút còn dùng được, chọn những màu cần cho tấm thiệp đang làm.” (lần 1) · Use the second model to advance or compare within the same story.

## SC05 — Có đồ để dùng, nhưng chưa cần nêu con số — Nhịp 5

Mục đích: Clarify a common trap through this example without expanding to another meaning.

Some đi được với paper trong mẫu vật liệu và pens số nhiều trong mẫu vật riêng. "The noun form still matters." Ta chỉ luyện câu khẳng định báo có đồ; chưa mở cách dùng some trong lời mời hay câu hỏi đặc biệt để tránh làm rối hoạt động.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot separates paper material from distinct pen items at same desk. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot separates paper material from distinct pen items at same desk.

Lý do: Clarify a common trap through this example without expanding to another meaning.

Chữ được phép: “some” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “Some đi được với paper trong mẫu vật liệu và pens số nhiều trong mẫu vật riêng. "The noun form still matters." Ta chỉ luyện câu khẳng định báo có đồ; chưa mở cách dùng some trong lời mời hay câu hỏi đặc biệt để tránh làm rối hoạt động.” (lần 1) · Clarify a common trap through this example without expanding to another meaning.

## SC06 — Có đồ để dùng, nhưng chưa cần nêu con số — Lượt thực hành

Mục đích: Invite a supported learner response; hold before the feedback.

Bạn đã tìm thấy giấy và muốn báo cho người bạn biết. "Say that an unspecified amount is available." Hãy nói: "We have some paper."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Hold found paper and complete model through learner interval. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold found paper and complete model through learner interval.

Lý do: Invite a supported learner response; hold before the feedback.

Chữ được phép: “We have some paper.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · hold · vi: “Bạn đã tìm thấy giấy và muốn báo cho người bạn biết. "Say that an unspecified amount is available." Hãy nói: "We have some paper."” (lần 1) · Invite a supported learner response; hold before the feedback.

## SC07 — Có đồ để dùng, nhưng chưa cần nêu con số — Phản hồi và kết quả

Mục đích: Provide the response and complete the opening promise.

"We have some paper." Chúng ta có một ít giấy. "Now the group knows what is available." Giấy và bút đã ra bàn, hai người kiểm lượng cho tấm thiệp rồi bắt đầu. Some giúp báo có vật liệu hoặc một số đồ, còn lượng chính xác được xem xét khi hoạt động cần tới.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC07_I1** — Both begin card with found materials, remaining supply visible in box. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both begin card with found materials, remaining supply visible in box.

Lý do: Provide the response and complete the opening promise.

Chữ được phép: “We have some paper.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC07_B1 → SC07_I1 · cut · vi: “"We have some paper." Chúng ta có một ít giấy. "Now the group knows what is available." Giấy và bút đã ra bàn, hai người kiểm lượng cho tấm thiệp rồi bắt đầu. Some giúp báo có vật liệu hoặc một số đồ, còn lượng chính xác được xem xét khi hoạt động cần tới.” (lần 1) · Provide the response and complete the opening promise.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Muốn làm thiệp mà chưa biết trong hộp có vật liệu gì! Some là một số, một lượng chưa nêu con số chính xác. "There is an unspecified amount or number." Bạn cần biết có đồ để bắt đầu, rồi mới kiểm lượng đủ cho công việc của nhóm.
- R2 → SC01: Muốn làm thiệp mà chưa biết trong hộp có vật liệu gì! Some là một số, một lượng chưa nêu con số chính xác. "There is an unspecified amount or number." Bạn cần biết có đồ để bắt đầu, rồi mới kiểm lượng đủ cho công việc của nhóm.
- R2 → SC02: Bạn mở hộp và nói: "We have some paper." Chúng ta có một ít giấy. "There is paper available to use." Người bạn lấy phần giấy ra, trải ở bàn; câu báo có vật liệu, chưa khẳng định số tờ hoặc đã đủ cho mọi người.
- R3 → SC02: Bạn mở hộp và nói: "We have some paper." Chúng ta có một ít giấy. "There is paper available to use." Người bạn lấy phần giấy ra, trải ở bàn; câu báo có vật liệu, chưa khẳng định số tờ hoặc đã đủ cho mọi người.
- R2 → SC03: Paper trong mẫu đang nói vật liệu, không nêu con số tờ. "Some does not give an exact amount." Nếu cần biết số cụ thể, nhóm còn phải kiểm. Bài không đánh đồng có một ít với chắc chắn đủ cho mọi nhu cầu ở cả lớp.
- R3 → SC04: Bạn tìm thêm và báo: "There are some pens in the box." Có một số bút trong hộp. "These are separate items, so pens is plural." Người bạn nhìn các chiếc bút còn dùng được, chọn những màu cần cho tấm thiệp đang làm.
- R2 → SC05: Some đi được với paper trong mẫu vật liệu và pens số nhiều trong mẫu vật riêng. "The noun form still matters." Ta chỉ luyện câu khẳng định báo có đồ; chưa mở cách dùng some trong lời mời hay câu hỏi đặc biệt để tránh làm rối hoạt động.
- R4 → SC06: Bạn đã tìm thấy giấy và muốn báo cho người bạn biết. "Say that an unspecified amount is available." Hãy nói: "We have some paper."
- R4 → SC07: "We have some paper." Chúng ta có một ít giấy. "Now the group knows what is available." Giấy và bút đã ra bàn, hai người kiểm lượng cho tấm thiệp rồi bắt đầu. Some giúp báo có vật liệu hoặc một số đồ, còn lượng chính xác được xem xét khi hoạt động cần tới.

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