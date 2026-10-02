# Kịch bản — vocab-ride-script-308 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-ride-script-308/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "cưỡi, đi (xe đạp, xe máy)" của từ RIDE, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "cưỡi, đi (xe đạp, xe máy)" của RIDE mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng RIDE trong ít nhất một câu
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
- Từ khoá duy nhất của video: RIDE (v), chỉ dạy nghĩa "cưỡi, đi (xe đạp, xe máy)"
- Mức độ người học: CEFR A1; chủ đề: Du lịch và đi lại
- Mã mục trong kho từ vựng: ride.v (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 42.72–71.2 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 8.29–13.81 |
| SC02 | 8.08–13.47 |
| SC03 | 8.08–13.47 |
| SC04 | 10.82–18.03 |
| SC05 | 7.45–12.42 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Đạp được một vòng rồi — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Đi được một vòng mà vui như xa lắm! Ride ở đây là đi xe đạp. Bạn đang tập trong sân trống, chiếc xe đã vừa người; người bạn đứng gần để hỗ trợ khi cần.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Helmeted mascot balances on correctly sized bicycle in empty practice courtyard, friend nearby. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Helmeted mascot balances on correctly sized bicycle in empty practice courtyard, friend nearby.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “ride” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Đi được một vòng mà vui như xa lắm! Ride ở đây là đi xe đạp. Bạn đang tập trong sân trống, chiếc xe đã vừa người; người bạn đứng gần để hỗ trợ khi cần.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Đạp được một vòng rồi — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Người bạn hỏi: "Can you ride a bicycle?" Bạn có biết đi xe đạp không? Bạn chỉ mới tập, nên bắt đầu chậm trên đoạn đường thẳng, không lao ra nơi có xe qua lại.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Friend addresses stationary helmeted mascot astride bicycle at start of clear practice lane. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend addresses stationary helmeted mascot astride bicycle at start of clear practice lane.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “Can you ride a bicycle?” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Người bạn hỏi: "Can you ride a bicycle?" Bạn có biết đi xe đạp không? Bạn chỉ mới tập, nên bắt đầu chậm trên đoạn đường thẳng, không lao ra nơi có xe qua lại.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Đạp được một vòng rồi — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Sau khi tập, bạn nói: "I can ride a bicycle." Tôi biết đi xe đạp. Câu này nói khả năng làm được; bạn đạp một đoạn ngắn rồi dừng có kiểm soát bên người bạn.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Mascot cycles slowly along empty lane then approaches friend, helmet secure. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot cycles slowly along empty lane then approaches friend, helmet secure.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “I can ride a bicycle.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Sau khi tập, bạn nói: "I can ride a bicycle." Tôi biết đi xe đạp. Câu này nói khả năng làm được; bạn đạp một đoạn ngắn rồi dừng có kiểm soát bên người bạn.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Đạp được một vòng rồi — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn muốn nói mình biết đi xe đạp. Hãy trả lời "Can you ride a bicycle?" bằng câu bắt đầu "I can..." và nói hết ý.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 6 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold question on steady view of bicycle and helmeted mascot, no full response. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold question on steady view of bicycle and helmeted mascot, no full response.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “Can you ride a bicycle?” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.; “I can...” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn nói mình biết đi xe đạp. Hãy trả lời "Can you ride a bicycle?" bằng câu bắt đầu "I can..." và nói hết ý.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Đạp được một vòng rồi — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"I can ride a bicycle." Tôi biết đi xe đạp. Một đoạn ngắn đã đủ để bạn tự tin hơn; hai người tiếp tục tập ở sân, chưa cần vội đi xa.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Mascot stops beside supportive friend on empty courtyard practice lane. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot stops beside supportive friend on empty courtyard practice lane.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “I can ride a bicycle.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"I can ride a bicycle." Tôi biết đi xe đạp. Một đoạn ngắn đã đủ để bạn tự tin hơn; hai người tiếp tục tập ở sân, chưa cần vội đi xa.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Nhân vật đồng hành chính: Adult friend or companion. Minimal flat ink style; consistent adult face, age, gender and identity across all scenes. Distinct from canonical mascot. Plain mustard top; only explicitly required work outerwear, helmet or life jacket.; Plain mustard-yellow top, with only scenario-required accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Đi được một vòng mà vui như xa lắm! Ride ở đây là đi xe đạp. Bạn đang tập trong sân trống, chiếc xe đã vừa người; người bạn đứng gần để hỗ trợ khi cần.
- R2 → SC01: Đi được một vòng mà vui như xa lắm! Ride ở đây là đi xe đạp. Bạn đang tập trong sân trống, chiếc xe đã vừa người; người bạn đứng gần để hỗ trợ khi cần.
- R2 → SC02: Người bạn hỏi: "Can you ride a bicycle?" Bạn có biết đi xe đạp không? Bạn chỉ mới tập, nên bắt đầu chậm trên đoạn đường thẳng, không lao ra nơi có xe qua lại.
- R3 → SC02: Người bạn hỏi: "Can you ride a bicycle?" Bạn có biết đi xe đạp không? Bạn chỉ mới tập, nên bắt đầu chậm trên đoạn đường thẳng, không lao ra nơi có xe qua lại.
- R3 → SC03: Sau khi tập, bạn nói: "I can ride a bicycle." Tôi biết đi xe đạp. Câu này nói khả năng làm được; bạn đạp một đoạn ngắn rồi dừng có kiểm soát bên người bạn.
- R4 → SC04: Bạn muốn nói mình biết đi xe đạp. Hãy trả lời "Can you ride a bicycle?" bằng câu bắt đầu "I can..." và nói hết ý.
- R4 → SC05: "I can ride a bicycle." Tôi biết đi xe đạp. Một đoạn ngắn đã đủ để bạn tự tin hơn; hai người tiếp tục tập ở sân, chưa cần vội đi xa.

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