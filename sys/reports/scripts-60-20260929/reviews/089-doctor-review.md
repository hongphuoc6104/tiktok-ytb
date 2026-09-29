# Kịch bản — vocab-doctor-script-089 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

output.json (artifact local; xem mã job)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "bác sĩ" của từ DOCTOR, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "bác sĩ" của DOCTOR mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng DOCTOR trong ít nhất một câu
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
- Từ khoá duy nhất của video: DOCTOR (n), chỉ dạy nghĩa "bác sĩ"
- Mức độ người học: CEFR A1; chủ đề: Y tế và bệnh viện
- Mã mục trong kho từ vựng: doctor.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 47.49–79.14 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.86–16.43 |
| SC02 | 10.58–17.63 |
| SC03 | 10.07–16.78 |
| SC04 | 9.11–15.18 |
| SC05 | 7.87–13.12 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Mascot đứng tại quầy tiếp nhận, bác sĩ ở phía cửa phòng.

Mục đích: Establish the concrete problem and selected sense.

Bạn tới phòng khám, có điều muốn hỏi nhưng chưa biết cần gặp ai. Doctor nghĩa là bác sĩ. Người ở quầy hỏi bạn cần gì; lúc này, một câu nói đúng tên người muốn gặp sẽ giúp cuộc trao đổi dễ hơn.

Chỉ đạo âm thanh vi: Speak to a Vietnamese beginner in a conversational tone; give each English model clear space without spelling out its letters. · Lưu ý phát âm: Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Depict this single concrete story moment: Mascot đứng tại quầy tiếp nhận, bác sĩ ở phía cửa phòng. Setting: Quầy tiếp nhận phòng khám, bác sĩ áo trắng và mascot áo xanh chuẩn. Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot đứng tại quầy tiếp nhận, bác sĩ ở phía cửa phòng.

Lý do: Establish the concrete problem and selected sense.

Chữ được phép: “doctor” — Upper third in large readable type; keep clear of faces and bottom captions.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Bạn tới phòng khám, có điều muốn hỏi nhưng chưa biết cần gặp ai. Doctor nghĩa là bác sĩ. Người ở quầy hỏi bạn cần gì; lúc này, một câu nói đúng tên người muốn gặp sẽ giúp cuộc trao đổi dễ hơn.” (lần 1) · Establish the concrete problem and selected sense.

## SC02 — Mascot nói với nhân viên quầy, chữ câu mẫu ở phần trên.

Mục đích: Use the first English model to advance the situation.

Bạn nói: "I need to see a doctor." Tôi cần gặp bác sĩ. See a doctor trong câu này là gặp bác sĩ để được khám hoặc trao đổi về sức khỏe. Chữ a cho biết bạn đang nói một bác sĩ, chưa gọi tên riêng ai.

Chỉ đạo âm thanh vi: Speak to a Vietnamese beginner in a conversational tone; give each English model clear space without spelling out its letters. · Lưu ý phát âm: Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Depict this single concrete story moment: Mascot nói với nhân viên quầy, chữ câu mẫu ở phần trên. Setting: Quầy tiếp nhận phòng khám, bác sĩ áo trắng và mascot áo xanh chuẩn. Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot nói với nhân viên quầy, chữ câu mẫu ở phần trên.

Lý do: Use the first English model to advance the situation.

Chữ được phép: “I need to see a doctor.” — Upper third in large readable type; keep clear of faces and bottom captions.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "I need to see a doctor." Tôi cần gặp bác sĩ. See a doctor trong câu này là gặp bác sĩ để được khám hoặc trao đổi về sức khỏe. Chữ a cho biết bạn đang nói một bác sĩ, chưa gọi tên riêng ai.” (lần 1) · Use the first English model to advance the situation.

## SC03 — Bác sĩ áo trắng giới thiệu, mascot ngồi đối diện, không diễn cảnh điều trị.

Mục đích: Use the second English model for the linked action or consequence.

Khi vào phòng, người đón bạn giới thiệu: "I'm a doctor." Tôi là bác sĩ. Câu ấy cho biết nghề của người nói. Bạn nghe lời giới thiệu rồi mới đặt câu hỏi đã chuẩn bị, không cần đoán nghề chỉ từ màu áo.

Chỉ đạo âm thanh vi: Speak to a Vietnamese beginner in a conversational tone; give each English model clear space without spelling out its letters. · Lưu ý phát âm: Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Depict this single concrete story moment: Bác sĩ áo trắng giới thiệu, mascot ngồi đối diện, không diễn cảnh điều trị. Setting: Quầy tiếp nhận phòng khám, bác sĩ áo trắng và mascot áo xanh chuẩn. Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Bác sĩ áo trắng giới thiệu, mascot ngồi đối diện, không diễn cảnh điều trị.

Lý do: Use the second English model for the linked action or consequence.

Chữ được phép: “I'm a doctor.” — Upper third in large readable type; keep clear of faces and bottom captions.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Khi vào phòng, người đón bạn giới thiệu: "I'm a doctor." Tôi là bác sĩ. Câu ấy cho biết nghề của người nói. Bạn nghe lời giới thiệu rồi mới đặt câu hỏi đã chuẩn bị, không cần đoán nghề chỉ từ màu áo.” (lần 1) · Use the second English model for the linked action or consequence.

## SC04 — Giữ quầy và câu gợi ý, không chữ đáp án trong hình.

Mục đích: Elicit one achievable learner response; withhold the answer.

Bạn đứng ở quầy và muốn gặp bác sĩ. Hoàn thành "I need to see a..." bằng từ vừa học, rồi nói câu đầy đủ.

Chỉ đạo âm thanh vi: Ask and wait for the learner before revealing the answer. · Lưu ý phát âm: Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Depict this single concrete story moment: Giữ quầy và câu gợi ý, không chữ đáp án trong hình. Setting: Quầy tiếp nhận phòng khám, bác sĩ áo trắng và mascot áo xanh chuẩn. Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Giữ quầy và câu gợi ý, không chữ đáp án trong hình.

Lý do: Elicit one achievable learner response; withhold the answer.

Chữ được phép: “I need to see a...” — Upper third in large readable type; keep clear of faces and bottom captions.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn đứng ở quầy và muốn gặp bác sĩ. Hoàn thành "I need to see a..." bằng từ vừa học, rồi nói câu đầy đủ.” (lần 1) · Elicit one achievable learner response; withhold the answer.

## SC05 — Mascot lấy tờ giấy không chữ nhìn thấy, bác sĩ lắng nghe.

Mục đích: Give explicit feedback and resolve the opening problem.

"I need to see a doctor." Từ cần dùng là doctor. Bạn lấy tờ giấy ghi câu hỏi ra. Người muốn gặp đã ở trước mặt, giờ bạn có thể bắt đầu trao đổi.

Chỉ đạo âm thanh vi: Confirm the answer and finish the concrete story. · Lưu ý phát âm: Keep English I and standard spelling. Check English examples, noun plurals, switching and sentence rhythm by listening to the actual WAV only when audio is authorized. Character count alone is not a voice-quality criterion. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Depict this single concrete story moment: Mascot lấy tờ giấy không chữ nhìn thấy, bác sĩ lắng nghe. Setting: Quầy tiếp nhận phòng khám, bác sĩ áo trắng và mascot áo xanh chuẩn. Use only the people explicitly mentioned in this moment, not every registered character. Preserve prop identities and colors across scenes. Attach canonical Character reference for the mascot. Extra symbols and labels are allowed only if explicitly listed as visible text; omit incidental package text, logos, prices, time digits and watermarks. Keep bottom 22% for subtitles and outer 10% as safe margins.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot lấy tờ giấy không chữ nhìn thấy, bác sĩ lắng nghe.

Lý do: Give explicit feedback and resolve the opening problem.

Chữ được phép: “I need to see a doctor.” — Upper third in large readable type; keep clear of faces and bottom captions.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"I need to see a doctor." Từ cần dùng là doctor. Bạn lấy tờ giấy ghi câu hỏi ra. Người muốn gặp đã ở trước mặt, giờ bạn có thể bắt đầu trao đổi.” (lần 1) · Give explicit feedback and resolve the opening problem.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot with round white head, dark navy outline, two solid black oval eyes, exactly one torso and two minimal stick arms and legs. Small eyebrows, sweat and mouth-expression changes allowed under 80/20 tolerance. No realistic muscle anatomy or large anime eye whites.; Exactly one pale-blue short-sleeve T-shirt (#8CCFE8); no doubled shirts.
- Bác sĩ: Adult clinician, simple white coat over neutral clothing, flat illustration, no detailed anatomy.; White clinician coat.
- Người phụ thứ hai khi cảnh yêu cầu: Supporting adult, minimal flat illustration, distinct from main mascot and first companion; appears only where explicitly required. Older relative for the family call or visit scenes.; Plain lavender top; gray hair only for an elderly relative.

## Đối chiếu ý bắt buộc

- R1 → SC01: Bạn tới phòng khám, có điều muốn hỏi nhưng chưa biết cần gặp ai. Doctor nghĩa là bác sĩ. Người ở quầy hỏi bạn cần gì; lúc này, một câu nói đúng tên người muốn gặp sẽ giúp cuộc trao đổi dễ hơn.
- R2 → SC01: Bạn tới phòng khám, có điều muốn hỏi nhưng chưa biết cần gặp ai. Doctor nghĩa là bác sĩ. Người ở quầy hỏi bạn cần gì; lúc này, một câu nói đúng tên người muốn gặp sẽ giúp cuộc trao đổi dễ hơn.
- R2 → SC02: Bạn nói: "I need to see a doctor." Tôi cần gặp bác sĩ. See a doctor trong câu này là gặp bác sĩ để được khám hoặc trao đổi về sức khỏe. Chữ a cho biết bạn đang nói một bác sĩ, chưa gọi tên riêng ai.
- R3 → SC02: Bạn nói: "I need to see a doctor." Tôi cần gặp bác sĩ. See a doctor trong câu này là gặp bác sĩ để được khám hoặc trao đổi về sức khỏe. Chữ a cho biết bạn đang nói một bác sĩ, chưa gọi tên riêng ai.
- R3 → SC03: Khi vào phòng, người đón bạn giới thiệu: "I'm a doctor." Tôi là bác sĩ. Câu ấy cho biết nghề của người nói. Bạn nghe lời giới thiệu rồi mới đặt câu hỏi đã chuẩn bị, không cần đoán nghề chỉ từ màu áo.
- R4 → SC04: Bạn đứng ở quầy và muốn gặp bác sĩ. Hoàn thành "I need to see a..." bằng từ vừa học, rồi nói câu đầy đủ.
- R4 → SC05: "I need to see a doctor." Từ cần dùng là doctor. Bạn lấy tờ giấy ghi câu hỏi ra. Người muốn gặp đã ở trước mặt, giờ bạn có thể bắt đầu trao đổi.

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