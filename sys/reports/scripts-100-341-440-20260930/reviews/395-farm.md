# Kịch bản — vocab-farm-script-395 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-farm-script-395/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "nông trại" của từ FARM, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt học tiếng Anh ở mức độ của mục kho, muốn dùng đúng một nghĩa từ trong tình huống đời thường

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "nông trại" của FARM mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng FARM trong ít nhất một câu
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
- Từ khoá duy nhất của video: FARM (n), chỉ dạy nghĩa "nông trại"
- Mức độ người học: CEFR A1; chủ đề: Cây cối và nông nghiệp
- Mã mục trong kho từ vựng: farm.n (dùng để đánh dấu đã làm)

Nhịp kể: Mở rõ tình huống và lợi ích học; tăng nhịp khi có biến chuyển, giữ đủ thời gian đọc câu và đáp lại mẫu nghe; số hình theo chức năng kể chuyện

Giả định cần kiểm tra:
- Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.
- Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.

5 cảnh · 5 hình logic · 5 nhịp

Tỷ lệ: 9:16

## Thời lượng dự kiến (chưa phải WAV)

VI: 46.05–76.75 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 9.23–15.39 |
| SC02 | 7.97–13.28 |
| SC03 | 8.29–13.81 |
| SC04 | 11.65–19.42 |
| SC05 | 8.91–14.85 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Một ngày ở nông trại — Mở tình huống

Mục đích: Show an immediate concrete need and establish the selected sense.

Rau ở một phía, con vật ở phía khác! Farm là nông trại. Bạn tới thăm người quen, vừa qua cổng đã thấy luống rau và khu nuôi tách riêng; nơi này rộng hơn chiếc vườn nhỏ bạn tưởng tượng.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot enters farm with vegetable plots and fenced animal area clearly separated, host greets. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot enters farm with vegetable plots and fenced animal area clearly separated, host greets.

Lý do: Show an immediate concrete need and establish the selected sense.

Chữ được phép: “farm” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Rau ở một phía, con vật ở phía khác! Farm là nông trại. Bạn tới thăm người quen, vừa qua cổng đã thấy luống rau và khu nuôi tách riêng; nơi này rộng hơn chiếc vườn nhỏ bạn tưởng tượng.” (lần 1) · Show an immediate concrete need and establish the selected sense.

## SC02 — Một ngày ở nông trại — Câu dùng thứ nhất

Mục đích: Use the first English model as an action within the situation.

Bạn nói: "My uncle has a farm." Chú tôi có một nông trại. A farm gọi nơi có các hoạt động nông nghiệp; trong chuyến thăm này chú sẽ dẫn hai người xem từng khu.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Mascot introduces adult uncle at farm gate to companion, farm buildings behind. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot introduces adult uncle at farm gate to companion, farm buildings behind.

Lý do: Use the first English model as an action within the situation.

Chữ được phép: “My uncle has a farm.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "My uncle has a farm." Chú tôi có một nông trại. A farm gọi nơi có các hoạt động nông nghiệp; trong chuyến thăm này chú sẽ dẫn hai người xem từng khu.” (lần 1) · Use the first English model as an action within the situation.

## SC03 — Một ngày ở nông trại — Diễn biến tiếp theo

Mục đích: Use the second model to clarify the same sense and advance the outcome.

Người bạn rủ: "Let's visit the farm." Cùng thăm nông trại nhé. Câu này có thể dùng khi lên kế hoạch chuyến đi; giờ đã tới, hai người theo chủ nhà đi từ khu rau trước.

Chỉ đạo âm thanh vi: Start promptly with the concrete situation or model sentence; speak naturally to a Vietnamese beginner and leave English intelligible. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Uncle leads mascot and companion along path beside vegetable beds, animals stay in separate area. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Uncle leads mascot and companion along path beside vegetable beds, animals stay in separate area.

Lý do: Use the second model to clarify the same sense and advance the outcome.

Chữ được phép: “Let's visit the farm.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Người bạn rủ: "Let's visit the farm." Cùng thăm nông trại nhé. Câu này có thể dùng khi lên kế hoạch chuyến đi; giờ đã tới, hai người theo chủ nhà đi từ khu rau trước.” (lần 1) · Use the second model to clarify the same sense and advance the outcome.

## SC04 — Một ngày ở nông trại — Bạn thử nói

Mục đích: Invite one manageable learner response; withhold the answer until the next scene.

Bạn muốn kể chú mình có một nông trại. Hoàn thành "My uncle has a..." bằng farm rồi nói cả câu. Hãy tưởng tượng đang giới thiệu nơi vừa tới.

Chỉ đạo âm thanh vi: Ask the learner, then wait before the answer. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 6 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Hold farm gate and incomplete sentence, no full answer. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold farm gate and incomplete sentence, no full answer.

Lý do: Invite one manageable learner response; withhold the answer until the next scene.

Chữ được phép: “My uncle has a...” — Upper third; balanced options, no answer highlight; clear of bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · hold · vi: “Bạn muốn kể chú mình có một nông trại. Hoàn thành "My uncle has a..." bằng farm rồi nói cả câu. Hãy tưởng tượng đang giới thiệu nơi vừa tới.” (lần 1) · Invite one manageable learner response; withhold the answer until the next scene.

## SC05 — Một ngày ở nông trại — Đáp án và kết thúc

Mục đích: Give the correct response and resolve the concrete situation.

"My uncle has a farm." Chú tôi có một nông trại. Bạn đã gọi đúng nơi cả nhóm đang thăm, rồi đi theo lối giữa các luống. Chuyến đi bắt đầu từ rau trước khi tới khu con vật.

Chỉ đạo âm thanh vi: Confirm the response and resolve the situation. · Lưu ý phát âm: Preserve standard English spelling and I. Check target word, plurals and language switches by listening to actual WAV at media stage; directions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Visitors follow uncle along farm path from vegetable beds toward distant animal pens. Attach canonical Character reference for mascot. Maintain one pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and minimal stick limbs. Show only people explicitly needed by this moment. Keep props and clothing continuous. Bottom 22% clear for subtitles, outer 10% safe. Only visible_text may appear as writing; no incidental logos, dates, numerals, ID details or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Visitors follow uncle along farm path from vegetable beds toward distant animal pens.

Lý do: Give the correct response and resolve the concrete situation.

Chữ được phép: “My uncle has a farm.” — Upper third, readable at phone size; separate from faces, main object and bottom subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “"My uncle has a farm." Chú tôi có một nông trại. Bạn đã gọi đúng nơi cả nhóm đang thăm, rồi đi theo lối giữa các luống. Chuyến đi bắt đầu từ rau trước khi tới khu con vật.” (lần 1) · Give the correct response and resolve the concrete situation.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows and mouth changes allowed. No muscles, doubled torso or anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt; keep it throughout, show other clothes as props or on supporting adults.
- Người đồng hành trong tình huống: Adult visiting companion. Minimal flat ink style. Maintain age, gender, clothing and identity across all scenes; use mustard top and only explicitly needed accessory. Distinct from canonical mascot.; Plain mustard-yellow top, with only scenario-required accessories.
- Người phụ khi tình huống yêu cầu: Adult uncle who hosts the farm visit. Minimal flat ink style; consistent role, adult identity and lavender clothing with only scenario-required outerwear. Distinct from mascot and companion.; Plain lavender top; scenario-required accessories only.

## Đối chiếu ý bắt buộc

- R1 → SC01: Rau ở một phía, con vật ở phía khác! Farm là nông trại. Bạn tới thăm người quen, vừa qua cổng đã thấy luống rau và khu nuôi tách riêng; nơi này rộng hơn chiếc vườn nhỏ bạn tưởng tượng.
- R2 → SC01: Rau ở một phía, con vật ở phía khác! Farm là nông trại. Bạn tới thăm người quen, vừa qua cổng đã thấy luống rau và khu nuôi tách riêng; nơi này rộng hơn chiếc vườn nhỏ bạn tưởng tượng.
- R2 → SC02: Bạn nói: "My uncle has a farm." Chú tôi có một nông trại. A farm gọi nơi có các hoạt động nông nghiệp; trong chuyến thăm này chú sẽ dẫn hai người xem từng khu.
- R3 → SC02: Bạn nói: "My uncle has a farm." Chú tôi có một nông trại. A farm gọi nơi có các hoạt động nông nghiệp; trong chuyến thăm này chú sẽ dẫn hai người xem từng khu.
- R3 → SC03: Người bạn rủ: "Let's visit the farm." Cùng thăm nông trại nhé. Câu này có thể dùng khi lên kế hoạch chuyến đi; giờ đã tới, hai người theo chủ nhà đi từ khu rau trước.
- R4 → SC04: Bạn muốn kể chú mình có một nông trại. Hoàn thành "My uncle has a..." bằng farm rồi nói cả câu. Hãy tưởng tượng đang giới thiệu nơi vừa tới.
- R4 → SC05: "My uncle has a farm." Chú tôi có một nông trại. Bạn đã gọi đúng nơi cả nhóm đang thăm, rồi đi theo lối giữa các luống. Chuyến đi bắt đầu từ rau trước khi tới khu con vật.

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