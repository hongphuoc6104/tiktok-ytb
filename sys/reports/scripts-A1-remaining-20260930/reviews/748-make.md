# Kịch bản — vocab-make-script-748 — revision 1



Chế độ: review. Kiểm tra kỹ thuật đã đạt; chưa duyệt chất lượng.



Đạo diễn: hook có lời giải; ví dụ có quan hệ; đủ ý brief; lượt thực hành và phản hồi; hình chứng minh nghĩa; không hứa khả năng chưa có. Không xem/nghe được phải ghi chưa hỗ trợ, không suy pass từ metadata.

[output.json](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-make-script-748/revisions/content/1/output.json)

## Mục tiêu và người xem

Người xem hiểu đúng nghĩa "làm ra, chế tạo" của từ MAKE, nhớ lâu và biết đặt câu tự nhiên

Người xem: Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.

Kiến thức đầu vào: Tiếng Anh cơ bản, đã quen bảng chữ cái và câu đơn giản

Tiêu chí đạt:
- Người xem nói lại được nghĩa "làm ra, chế tạo" của MAKE mà không cần tra từ điển
- Người xem nghe và nhại được cách dùng MAKE trong ít nhất một câu
- Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật
- Người xem không lẫn MAKE với các nghĩa khác của chính từ này

Cần tránh:
- Dịch nghĩa sáo rỗng kiểu từ điển
- Nhồi quá nhiều từ mới ngoài từ khoá chính
- Nhân vật quá phức tạp gây rối mắt
- Từ "make" còn nghĩa khác: khiến, làm cho ai đó thế nào [v, make.v.cause]. Video này KHÔNG dạy nghĩa đó.
- Từ "make" còn nghĩa khác: kiếm được (tiền) [v, make.v.earn]. Video này KHÔNG dạy nghĩa đó.
- Từ "make" còn nghĩa khác: kịp, bắt kịp (chuyến xe) [v, make.v.catch-in-time]. Video này KHÔNG dạy nghĩa đó.

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
- Từ khoá duy nhất của video: MAKE (v), chỉ dạy nghĩa "làm ra, chế tạo"
- Mức độ người học: CEFR A1; chủ đề: Động từ thông dụng
- Mã mục trong kho từ vựng: make.v.create (dùng để đánh dấu đã làm)
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

VI: 71.85–119.77 giây. Cơ sở: initial estimate; replace with measured voice rate

| Cảnh | Khoảng giây dự kiến |
|---|---|
| SC01 | 11.12–18.54 |
| SC02 | 10.69–17.82 |
| SC03 | 10.26–17.1 |
| SC04 | 9.95–16.59 |
| SC05 | 9.75–16.24 |
| SC06 | 8.56–14.27 |
| SC07 | 11.52–19.21 |

Cảnh báo thời lượng/nhịp:
Không có.

## Chữ tạo cùng hình

Kiểu: Inter, sans-serif. Màu: #172033. Viền/nền: Nền sáng tương phản. Cỡ: Lớn, dễ đọc trên màn hình điện thoại. Vị trí: Trung tâm hoặc 1/3 phía trên, tránh vùng viền mép.

Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.

## SC01 — Tờ giấy phẳng biến thành món quà nhỏ — Nhịp 1

Mục đích: Establish the need and one selected meaning promptly.

Bạn muốn tặng một món nhỏ, trên bàn chỉ có giấy và bút! Make là làm ra, tạo ra. "Create something that was not there before." Trong chuyện, bạn sẽ biến vật liệu thành một tấm thiệp; món quà chưa có sẵn để chỉ lấy từ ngăn kéo.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC01_I1** — Mascot and companion examine paper, capped pens and empty gift spot on desk. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot and companion examine paper, capped pens and empty gift spot on desk.

Lý do: Establish the need and one selected meaning promptly.

Chữ được phép: “make” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC01_B1 → SC01_I1 · cut · vi: “Bạn muốn tặng một món nhỏ, trên bàn chỉ có giấy và bút! Make là làm ra, tạo ra. "Create something that was not there before." Trong chuyện, bạn sẽ biến vật liệu thành một tấm thiệp; món quà chưa có sẵn để chỉ lấy từ ngăn kéo.” (lần 1) · Establish the need and one selected meaning promptly.

## SC02 — Tờ giấy phẳng biến thành món quà nhỏ — Nhịp 2

Mục đích: Use the first model at the point where the speaker needs it.

Bạn nói: "Let's make a card." Cùng làm một tấm thiệp nhé. "We can create it from this paper." Hai người chọn tờ giấy, gấp thành bìa rồi thêm hình trang trí. Kết quả đang dần có hình dạng cụ thể từ những vật liệu ban đầu.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC02_I1** — Both fold paper into a card and add simple non-text decoration. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both fold paper into a card and add simple non-text decoration.

Lý do: Use the first model at the point where the speaker needs it.

Chữ được phép: “Let's make a card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC02_B1 → SC02_I1 · cut · vi: “Bạn nói: "Let's make a card." Cùng làm một tấm thiệp nhé. "We can create it from this paper." Hai người chọn tờ giấy, gấp thành bìa rồi thêm hình trang trí. Kết quả đang dần có hình dạng cụ thể từ những vật liệu ban đầu.” (lần 1) · Use the first model at the point where the speaker needs it.

## SC03 — Tờ giấy phẳng biến thành món quà nhỏ — Nhịp 3

Mục đích: Show the condition or contrast that makes this usage matter.

Make tập trung vào việc tạo ra món trong hai mẫu này. "A new object is the result." Ta không dùng một quy tắc tuyệt đối rằng mọi hành động bằng tay đều phải là make; riêng chuyện này có tấm thiệp mới được làm ra.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC03_I1** — Compare original flat sheet with partially completed card, same material color. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Compare original flat sheet with partially completed card, same material color.

Lý do: Show the condition or contrast that makes this usage matter.

Chữ được phép: “make” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC03_B1 → SC03_I1 · cut · vi: “Make tập trung vào việc tạo ra món trong hai mẫu này. "A new object is the result." Ta không dùng một quy tắc tuyệt đối rằng mọi hành động bằng tay đều phải là make; riêng chuyện này có tấm thiệp mới được làm ra.” (lần 1) · Show the condition or contrast that makes this usage matter.

## SC04 — Tờ giấy phẳng biến thành món quà nhỏ — Nhịp 4

Mục đích: Use the second model to advance or compare within the same story.

Người bạn hỏi: "Can you make a paper flower?" Bạn có thể làm một bông hoa giấy không? "It can go with our card." Bạn dùng phần giấy còn lại tạo một bông hoa đơn giản, đặt cạnh thiệp để cùng thành món quà.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC04_I1** — Mascot makes simple folded paper flower from spare sheet beside existing card. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Mascot makes simple folded paper flower from spare sheet beside existing card.

Lý do: Use the second model to advance or compare within the same story.

Chữ được phép: “Can you make a paper flower?” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC04_B1 → SC04_I1 · cut · vi: “Người bạn hỏi: "Can you make a paper flower?" Bạn có thể làm một bông hoa giấy không? "It can go with our card." Bạn dùng phần giấy còn lại tạo một bông hoa đơn giản, đặt cạnh thiệp để cùng thành món quà.” (lần 1) · Use the second model to advance or compare within the same story.

## SC05 — Tờ giấy phẳng biến thành món quà nhỏ — Nhịp 5

Mục đích: Clarify a common trap through this example without expanding to another meaning.

Hai mẫu có card và paper flower là sản phẩm. "Name what you want to create." Làm một món rồi vẫn cần kiểm và chỉnh; câu tiếng Anh nêu mục đích tạo ra, không khẳng định sản phẩm đầu tiên luôn hoàn hảo.

Chỉ đạo âm thanh vi: Address a Vietnamese beginner, make the immediate purpose clear and keep English phrases intelligible. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC05_I1** — Both adjust flower petals and card fold, concrete small improvements visible. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both adjust flower petals and card fold, concrete small improvements visible.

Lý do: Clarify a common trap through this example without expanding to another meaning.

Chữ được phép: “make” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC05_B1 → SC05_I1 · cut · vi: “Hai mẫu có card và paper flower là sản phẩm. "Name what you want to create." Làm một món rồi vẫn cần kiểm và chỉnh; câu tiếng Anh nêu mục đích tạo ra, không khẳng định sản phẩm đầu tiên luôn hoàn hảo.” (lần 1) · Clarify a common trap through this example without expanding to another meaning.

## SC06 — Tờ giấy phẳng biến thành món quà nhỏ — Lượt thực hành

Mục đích: Invite a supported learner response; hold before the feedback.

Bạn muốn rủ người bạn làm một tấm thiệp cùng nhau. "Choose the verb for creating this item." Hãy nói: "Let's make a card."

Chỉ đạo âm thanh vi: Invite the response, then wait quietly at the scene end. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 4 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC06_I1** — Hold paper materials and invitation model. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Hold paper materials and invitation model.

Lý do: Invite a supported learner response; hold before the feedback.

Chữ được phép: “Let's make a card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC06_B1 → SC06_I1 · hold · vi: “Bạn muốn rủ người bạn làm một tấm thiệp cùng nhau. "Choose the verb for creating this item." Hãy nói: "Let's make a card."” (lần 1) · Invite a supported learner response; hold before the feedback.

## SC07 — Tờ giấy phẳng biến thành món quà nhỏ — Phản hồi và kết quả

Mục đích: Provide the response and complete the opening promise.

"Let's make a card." Cùng làm một tấm thiệp nhé. "The paper has become a small gift." Trên bàn có thiệp và hoa giấy do hai người làm. Make trong chuyện dẫn tới sản phẩm nhìn thấy được; món quà đã sẵn để trao cho người được nhắc trong buổi gặp.

Chỉ đạo âm thanh vi: Give the response and finish the story clearly. · Lưu ý phát âm: Preserve English spelling, I and inflected forms. Check actual WAV for the target word, sentence stress, language switches and learner interval; text instructions do not prove voice quality. · Khoảng chờ học viên cuối cảnh: 0 giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.

**Hình SC07_I1** — Both present finished card and paper flower to arriving adult friend. Attach canonical Character reference for the mascot. Preserve the single pale-blue short-sleeve torso, round white navy-outlined head, solid black oval eyes and stick limbs. Keep all characters and props continuous within the story. Show only the people explicitly needed here. Outer 10% safe and bottom 22% clear for subtitles. Only visible_text may appear as writing; no incidental logos, numerals, dates, account data or watermarks.

Ảnh gốc: Tạo mới; giữ: Không áp dụng; đổi: Both present finished card and paper flower to arriving adult friend.

Lý do: Provide the response and complete the opening promise.

Chữ được phép: “Let's make a card.” — Upper third, readable at phone size, separate from faces and main referent; keep bottom 22% clear for subtitles.; đối tượng: Flat teaching text.

Nhịp SC07_B1 → SC07_I1 · cut · vi: “"Let's make a card." Cùng làm một tấm thiệp nhé. "The paper has become a small gift." Trên bàn có thiệp và hoa giấy do hai người làm. Make trong chuyện dẫn tới sản phẩm nhìn thấy được; món quà đã sẵn để trao cho người được nhắc trong buổi gặp.” (lần 1) · Provide the response and complete the opening promise.

## Nhân vật

- Người que áo xanh biển nhạt: Canonical mascot: round white head with dark navy outline, two solid black oval eyes, exactly one torso and minimal stick limbs. Small expressive eyebrows, sweat, mouth changes and limb curvature are allowed. No doubled torso, realistic muscles or large anime eye whites. Use canonical reference assets/characters/channel-mascot/reference-v1.png.; Exactly one pale-blue (#8CCFE8) short-sleeve T-shirt, unchanged throughout; minimal stick limbs.
- Người đồng hành chính: Adult principal companion in minimal ink style; maintain the same adult identity and role within this story. Keep minimal flat ink appearance and ordinary proportions, no realistic muscular bodies.; Single plain mustard-yellow top; only specifically needed role accessories.

## Đối chiếu ý bắt buộc

- R1 → SC01: Bạn muốn tặng một món nhỏ, trên bàn chỉ có giấy và bút! Make là làm ra, tạo ra. "Create something that was not there before." Trong chuyện, bạn sẽ biến vật liệu thành một tấm thiệp; món quà chưa có sẵn để chỉ lấy từ ngăn kéo.
- R2 → SC01: Bạn muốn tặng một món nhỏ, trên bàn chỉ có giấy và bút! Make là làm ra, tạo ra. "Create something that was not there before." Trong chuyện, bạn sẽ biến vật liệu thành một tấm thiệp; món quà chưa có sẵn để chỉ lấy từ ngăn kéo.
- R2 → SC02: Bạn nói: "Let's make a card." Cùng làm một tấm thiệp nhé. "We can create it from this paper." Hai người chọn tờ giấy, gấp thành bìa rồi thêm hình trang trí. Kết quả đang dần có hình dạng cụ thể từ những vật liệu ban đầu.
- R3 → SC02: Bạn nói: "Let's make a card." Cùng làm một tấm thiệp nhé. "We can create it from this paper." Hai người chọn tờ giấy, gấp thành bìa rồi thêm hình trang trí. Kết quả đang dần có hình dạng cụ thể từ những vật liệu ban đầu.
- R2 → SC03: Make tập trung vào việc tạo ra món trong hai mẫu này. "A new object is the result." Ta không dùng một quy tắc tuyệt đối rằng mọi hành động bằng tay đều phải là make; riêng chuyện này có tấm thiệp mới được làm ra.
- R3 → SC04: Người bạn hỏi: "Can you make a paper flower?" Bạn có thể làm một bông hoa giấy không? "It can go with our card." Bạn dùng phần giấy còn lại tạo một bông hoa đơn giản, đặt cạnh thiệp để cùng thành món quà.
- R2 → SC05: Hai mẫu có card và paper flower là sản phẩm. "Name what you want to create." Làm một món rồi vẫn cần kiểm và chỉnh; câu tiếng Anh nêu mục đích tạo ra, không khẳng định sản phẩm đầu tiên luôn hoàn hảo.
- R4 → SC06: Bạn muốn rủ người bạn làm một tấm thiệp cùng nhau. "Choose the verb for creating this item." Hãy nói: "Let's make a card."
- R4 → SC07: "Let's make a card." Cùng làm một tấm thiệp nhé. "The paper has become a small gift." Trên bàn có thiệp và hoa giấy do hai người làm. Make trong chuyện dẫn tới sản phẩm nhìn thấy được; món quà đã sẵn để trao cho người được nhắc trong buổi gặp.

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