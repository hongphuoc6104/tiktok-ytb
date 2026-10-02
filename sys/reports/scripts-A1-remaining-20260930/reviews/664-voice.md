# Kịch bản — vocab-voice-script-664 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-voice-script-664/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "giọng nói" của từ VOICE, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "giọng nói" của VOICE mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng VOICE trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn VOICE với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "voice" còn nghĩa khác: tiếng nói, quyền phát biểu (have a voice in) [n, voice.n.say]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: VOICE (n), chỉ dạy nghĩa "giọng nói"
- Mức độ người học: CEFR A1; chủ đề: Danh từ thông dụng
- Mã mục trong kho từ vựng: voice.n.speech-voice (dùng để đánh dấu đã làm)
- Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.
- Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.
- Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.
- Thời lượng dự kiến theo nhóm medium; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.

6 cảnh · 6 hình logic · 6 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 61.7–102.82 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 10.27–17.12 |
| SC02 | 10.37–17.28 |
| SC03 | 10.58–17.63 |
| SC04 | 11.83–19.72 |
| SC05 | 8.9–14.83 |
| SC06 | 9.75–16.24 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Giọng nói của người đang ở đầu cuộc gọi — Nhịp 1

Mục đích: Make the selected sense useful in a concrete situation.

Trong câu chuyện, người bạn lên tiếng trước khi hình trên máy hiện rõ! Voice là giọng nói. "The sound of a person speaking." Bạn đang xem cảnh cuộc gọi hư cấu, muốn gọi đúng điều nhân vật nghe khi người ở đầu kia nói.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion view fictional call-scene illustration with speaker and phone, no actual recording evidence. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion view fictional call-scene illustration with speaker and phone, no actual recording evidence.

Lý do: Make the selected sense useful in a concrete situation.

Chữ được phép: “voice” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Trong câu chuyện, người bạn lên tiếng trước khi hình trên máy hiện rõ! Voice là giọng nói. "The sound of a person speaking." Bạn đang xem cảnh cuộc gọi hư cấu, muốn gọi đúng điều nhân vật nghe khi người ở đầu kia nói.” (lần 1) · Make the selected sense useful in a concrete situation.

## SC02 — Giọng nói của người đang ở đầu cuộc gọi — Nhịp 2

Mục đích: Use the first English model with its immediate purpose.

Nhân vật hỏi: "Can you hear my voice?" Bạn có nghe giọng tôi không? "Am I being heard in this talk?" Câu hỏi nói về giọng của người đang nói trong cảnh; người ở đầu kia trả lời để cả hai tiếp tục cuộc trao đổi.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Fictional speaker on phone checks being heard, mascot follows story reference. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Fictional speaker on phone checks being heard, mascot follows story reference.

Lý do: Use the first English model with its immediate purpose.

Chữ được phép: “Can you hear my voice?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Nhân vật hỏi: "Can you hear my voice?" Bạn có nghe giọng tôi không? "Am I being heard in this talk?" Câu hỏi nói về giọng của người đang nói trong cảnh; người ở đầu kia trả lời để cả hai tiếp tục cuộc trao đổi.” (lần 1) · Use the first English model with its immediate purpose.

## SC03 — Giọng nói của người đang ở đầu cuộc gọi — Nhịp 3

Mục đích: Clarify the specific usage or condition and change the story state.

Voice ở đây là giọng của người đang nói, không phải mọi tiếng xuất hiện quanh hai nhân vật. "We mean the person speaking in this call." Bạn nhìn người được nhắc trong câu chuyện, giữ câu hỏi gắn với đúng giọng mà nhân vật muốn nghe.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Both discuss fictional call illustration, no synthetic-audio quality certificate. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both discuss fictional call illustration, no synthetic-audio quality certificate.

Lý do: Clarify the specific usage or condition and change the story state.

Chữ được phép: “voice” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Voice ở đây là giọng của người đang nói, không phải mọi tiếng xuất hiện quanh hai nhân vật. "We mean the person speaking in this call." Bạn nhìn người được nhắc trong câu chuyện, giữ câu hỏi gắn với đúng giọng mà nhân vật muốn nghe.” (lần 1) · Clarify the specific usage or condition and change the story state.

## SC04 — Giọng nói của người đang ở đầu cuộc gọi — Nhịp 4

Mục đích: Use the second model to move the same situation forward.

Nhân vật đáp trong truyện: "I know your voice." Tôi nhận ra giọng bạn. "I have heard you speak before in this story." Lời ấy gắn với quan hệ của hai nhân vật đã được kể: họ từng nói chuyện trước đây, nên người nghe nhận ra người đang ở đầu cuộc gọi.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Fictional companions recognize each other in illustrated story, no real speaker-identification test. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Fictional companions recognize each other in illustrated story, no real speaker-identification test.

Lý do: Use the second model to move the same situation forward.

Chữ được phép: “I know your voice.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Nhân vật đáp trong truyện: "I know your voice." Tôi nhận ra giọng bạn. "I have heard you speak before in this story." Lời ấy gắn với quan hệ của hai nhân vật đã được kể: họ từng nói chuyện trước đây, nên người nghe nhận ra người đang ở đầu cuộc gọi.” (lần 1) · Use the second model to move the same situation forward.

## SC05 — Giọng nói của người đang ở đầu cuộc gọi — Lượt thực hành

Mục đích: Ask for one manageable response, without moving on during the learner interval.

Bạn đóng vai người hỏi có nghe giọng mình. "Ask in the situation we described." Hãy nói: "Can you hear my voice?"

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Hold fictional call scene and full learner question. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold fictional call scene and full learner question.

Lý do: Ask for one manageable response, without moving on during the learner interval.

Chữ được phép: “Can you hear my voice?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · hold · vi: “Bạn đóng vai người hỏi có nghe giọng mình. "Ask in the situation we described." Hãy nói: "Can you hear my voice?"” (lần 1) · Ask for one manageable response, without moving on during the learner interval.

## SC06 — Giọng nói của người đang ở đầu cuộc gọi — Phản hồi và kết quả

Mục đích: Give feedback and show the result of the shared action.

"Can you hear my voice?" Bạn nghe giọng tôi không? "The conversation can continue in the story." Hai nhân vật đã có cách nói về tiếng của người đang nói, còn người học có danh từ voice để dùng trong một câu ngắn.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Both continue discussing fictional call scene, no actual call or new audio artifact. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both continue discussing fictional call scene, no actual call or new audio artifact.

Lý do: Give feedback and show the result of the shared action.

Chữ được phép: “Can you hear my voice?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · cut · vi: “"Can you hear my voice?" Bạn nghe giọng tôi không? "The conversation can continue in the story." Hai nhân vật đã có cách nói về tiếng của người đang nói, còn người học có danh từ voice để dùng trong một câu ngắn.” (lần 1) · Give feedback and show the result of the shared action.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Trong câu chuyện, người bạn lên tiếng trước khi hình trên máy hiện rõ! Voice là giọng nói. "The sound of a person speaking." Bạn đang xem cảnh cuộc gọi hư cấu, muốn gọi đúng điều nhân vật nghe khi người ở đầu kia nói.
- R2 → SC01: Trong câu chuyện, người bạn lên tiếng trước khi hình trên máy hiện rõ! Voice là giọng nói. "The sound of a person speaking." Bạn đang xem cảnh cuộc gọi hư cấu, muốn gọi đúng điều nhân vật nghe khi người ở đầu kia nói.
- R2 → SC02: Nhân vật hỏi: "Can you hear my voice?" Bạn có nghe giọng tôi không? "Am I being heard in this talk?" Câu hỏi nói về giọng của người đang nói trong cảnh; người ở đầu kia trả lời để cả hai tiếp tục cuộc trao đổi.
- R3 → SC02: Nhân vật hỏi: "Can you hear my voice?" Bạn có nghe giọng tôi không? "Am I being heard in this talk?" Câu hỏi nói về giọng của người đang nói trong cảnh; người ở đầu kia trả lời để cả hai tiếp tục cuộc trao đổi.
- R2 → SC03: Voice ở đây là giọng của người đang nói, không phải mọi tiếng xuất hiện quanh hai nhân vật. "We mean the person speaking in this call." Bạn nhìn người được nhắc trong câu chuyện, giữ câu hỏi gắn với đúng giọng mà nhân vật muốn nghe.
- R3 → SC04: Nhân vật đáp trong truyện: "I know your voice." Tôi nhận ra giọng bạn. "I have heard you speak before in this story." Lời ấy gắn với quan hệ của hai nhân vật đã được kể: họ từng nói chuyện trước đây, nên người nghe nhận ra người đang ở đầu cuộc gọi.
- R4 → SC05: Bạn đóng vai người hỏi có nghe giọng mình. "Ask in the situation we described." Hãy nói: "Can you hear my voice?"
- R4 → SC06: "Can you hear my voice?" Bạn nghe giọng tôi không? "The conversation can continue in the story." Hai nhân vật đã có cách nói về tiếng của người đang nói, còn người học có danh từ voice để dùng trong một câu ngắn.

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