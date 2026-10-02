# Kịch bản — vocab-flower-script-391 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-flower-script-391/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "bông hoa" của từ FLOWER, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "bông hoa" của FLOWER mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng FLOWER trong ít nhất một câu
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
- Từ khoá duy nhất của video: FLOWER (n), chỉ dạy nghĩa "bông hoa"
- Mức độ người học: CEFR A1; chủ đề: Cây cối và nông nghiệp
- Mã mục trong kho từ vựng: flower.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 43.12–71.88 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 8.7–14.51 |
| SC02 | 8.08–13.47 |
| SC03 | 7.87–13.12 |
| SC04 | 10.18–16.97 |
| SC05 | 8.29–13.81 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Một bông hoa đủ làm quà — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Một bông thôi cũng có người chờ nhận! Flower là bông hoa. Bạn chọn quà nhỏ cho người bạn, nhìn một cành riêng bên cạnh bó lớn; hôm nay chỉ muốn gửi một lời cảm ơn giản dị.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot chooses one flower stem beside small bouquet at wrapping table, friend assists. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot chooses one flower stem beside small bouquet at wrapping table, friend assists.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “flower” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Một bông thôi cũng có người chờ nhận! Flower là bông hoa. Bạn chọn quà nhỏ cho người bạn, nhìn một cành riêng bên cạnh bó lớn; hôm nay chỉ muốn gửi một lời cảm ơn giản dị.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Một bông hoa đủ làm quà — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn nói: "This flower is for you." Bông hoa này dành cho bạn. This flower chỉ đúng bông đang cầm; bạn đưa bằng phần thân đã được gói, để người nhận thấy món quà nhỏ.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot offers one wrapped flower to adult friend, bloom clearly visible. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot offers one wrapped flower to adult friend, bloom clearly visible.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “This flower is for you.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "This flower is for you." Bông hoa này dành cho bạn. This flower chỉ đúng bông đang cầm; bạn đưa bằng phần thân đã được gói, để người nhận thấy món quà nhỏ.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Một bông hoa đủ làm quà — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Người bạn nhìn bó trên bàn: "Those flowers are beautiful." Những bông hoa kia đẹp. Flowers thêm s vì nói nhiều; hai người đang chỉ hai lượng khác nhau, một bông và cả bó.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Friend gestures toward multiple flowers in bouquet while holding single gifted stem separately. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend gestures toward multiple flowers in bouquet while holding single gifted stem separately.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “Those flowers are beautiful.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn nhìn bó trên bàn: "Those flowers are beautiful." Những bông hoa kia đẹp. Flowers thêm s vì nói nhiều; hai người đang chỉ hai lượng khác nhau, một bông và cả bó.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Một bông hoa đủ làm quà — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn tặng đúng một bông. Chọn flower hay flowers trong "This... is for you." rồi nói cả câu tặng quà. Nhớ nhìn số lượng đang cầm.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 5 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — One flower held forward with two word-form choices and sentence stem. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: One flower held forward with two word-form choices and sentence stem.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “This... is for you.” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn tặng đúng một bông. Chọn flower hay flowers trong "This... is for you." rồi nói cả câu tặng quà. Nhớ nhìn số lượng đang cầm.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Một bông hoa đủ làm quà — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"This flower is for you." Bông hoa này dành cho bạn. Người bạn nhận và tìm một chiếc lọ nhỏ. Bó lớn vẫn ở bàn, còn một bông đã hoàn thành lời cảm ơn của mình.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Friend places single flower into small vase, bouquet stays separate on table. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Friend places single flower into small vase, bouquet stays separate on table.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “This flower is for you.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"This flower is for you." Bông hoa này dành cho bạn. Người bạn nhận và tìm một chiếc lọ nhỏ. Bó lớn vẫn ở bàn, còn một bông đã hoàn thành lời cảm ơn của mình.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người đồng hành trong tình huống: Adult friend or companion. Minimal flat ink style. Maintain age, gender, clothing and identity across all scenes; use mustard top and only explicitly needed accessory. Distinct from canonical mascot.; Plain mustard-yellow top, with only scenario-required accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Một bông thôi cũng có người chờ nhận! Flower là bông hoa. Bạn chọn quà nhỏ cho người bạn, nhìn một cành riêng bên cạnh bó lớn; hôm nay chỉ muốn gửi một lời cảm ơn giản dị.
- R2 → SC01: Một bông thôi cũng có người chờ nhận! Flower là bông hoa. Bạn chọn quà nhỏ cho người bạn, nhìn một cành riêng bên cạnh bó lớn; hôm nay chỉ muốn gửi một lời cảm ơn giản dị.
- R2 → SC02: Bạn nói: "This flower is for you." Bông hoa này dành cho bạn. This flower chỉ đúng bông đang cầm; bạn đưa bằng phần thân đã được gói, để người nhận thấy món quà nhỏ.
- R3 → SC02: Bạn nói: "This flower is for you." Bông hoa này dành cho bạn. This flower chỉ đúng bông đang cầm; bạn đưa bằng phần thân đã được gói, để người nhận thấy món quà nhỏ.
- R3 → SC03: Người bạn nhìn bó trên bàn: "Those flowers are beautiful." Những bông hoa kia đẹp. Flowers thêm s vì nói nhiều; hai người đang chỉ hai lượng khác nhau, một bông và cả bó.
- R4 → SC04: Bạn tặng đúng một bông. Chọn flower hay flowers trong "This... is for you." rồi nói cả câu tặng quà. Nhớ nhìn số lượng đang cầm.
- R4 → SC05: "This flower is for you." Bông hoa này dành cho bạn. Người bạn nhận và tìm một chiếc lọ nhỏ. Bó lớn vẫn ở bàn, còn một bông đã hoàn thành lời cảm ơn của mình.

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