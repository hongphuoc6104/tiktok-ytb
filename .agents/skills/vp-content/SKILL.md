---
name: vp-content
description: Viết, kiểm tra và sửa kịch bản đa nhịp cho Video Pilot; dùng trong phần content.
---

Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Kịch bản đa nhịp

Đọc AGENTS.md, docs/workflow.md và docs/story-planning.md. Trước sản xuất chạy status JOB và next JOB. Giữ đúng ba điểm duyệt content/media/video, mode review hoặc auto cố định.

Job mới dùng schemas/brief-v3.json và schemas/content-v3.json. Đọc brief-current.json và brief hiện tại. Không gán cứng chủ đề, đối tượng, thể loại, mục đích học ngoại ngữ hay số cảnh. Tiêu chí, nội dung tránh, kiến thức sẵn có, nhịp kể và yêu cầu chuyên biệt lấy từ planning. Mặc định/suy đoán phải hiển thị trong bản duyệt; hỏi thông tin thiếu nếu quyết định đó ảnh hưởng lớn đến mục tiêu. Mọi kịch bản bắt buộc sử dụng nhân vật đại diện kênh cố định (canonical mascot) làm nhân vật chính CH01: "Người que áo xanh biển nhạt" (tham chiếu tại assets/characters/channel-mascot/reference-v1.png, ngoại hình đầu tròn trắng viền xanh đen, mắt oval, miệng cười, áo thun cộc tay xanh biển nhạt #8CCFE8).

Job dạy từ vựng: brief do `python3 vocab/bank.py start JOB` sinh ra, mang sẵn mã mục kho, một video dạy đúng một nghĩa. Đọc kỹ planning.avoid — các nghĩa khác của cùng từ nằm ở đó, kể cả nghĩa đã có video riêng; tuyệt đối không dạy lấn sang nghĩa đó, kể cả khi ví dụ nghe tự nhiên hơn. Không tự đổi từ khoá, không thêm từ khoá thứ hai. Cần từ khác thì release job và draw lại, không sửa mã mục trong brief.
Đạo diễn nội dung: đọc [vp-script-director](../vp-script-director/SKILL.md) và [vp-visual-director](../vp-visual-director/SKILL.md) trước khi lập outline; [vp-edit-director](../vp-edit-director/SKILL.md) và [vp-audio-director](../vp-audio-director/SKILL.md) khi đặt nhịp/lượt thực hành. Video từ vựng đọc [sư phạm từ vựng](references/vocab-pedagogy.md). Đây là vai trò nội bộ, không thêm gate hoặc tự tạo agent.

Lập outline trước, kiểm tra đủ ý và trình tự, rồi viết lời dẫn, images và beats. Mỗi hình/nhịp phải có chức năng học hoặc kể chuyện; số lượng theo brief và lượng thông tin, không lấy tốc độ hàng đợi làm tiêu chí sáng tạo. Giữ liên tục nhân vật, bối cảnh và trạng thái; sinh độc lập khi bố cục thật sự độc lập.

**Công thức Chuẩn Micro-Drama 4 Hồi (Thời lượng chuẩn: 15.0 – 20.0s)**:
- **Hồi 1 (SC01: 0 - 4s) — Hook Rắc Rối Đời Thường**: Mở màn bằng một tình huống oái oăm, đời thường thực tế mà người học dễ gặp phải (báo thức reo, tắc đường, vỡ đồ, muộn giờ...), tuyệt đối tránh mở bài kiểu giảng bài trên lớp hay định nghĩa từ điển.
- **Hồi 2 (SC02: 4 - 8s) — Chìa Khóa Từ Vựng**: Cụm từ tiếng Anh xuất hiện như giải pháp gỡ rối hoặc phản ứng tự nhiên; hình ảnh có chữ nổi bật (Literal Text Overlay) trên bối cảnh.
- **Hồi 3 (SC03: 8 - 13s) — Luyện Nói Phản Xạ 2 Chiều**: Mascot CH01 tương tác trực tiếp với người xem (ghé tai nghe, giơ tay khích lệ, bong bóng thoại to rõ), có khoảng dừng luyện nói `learner_pause_seconds` (1.0 - 1.5s) để người học hô to từ vựng.
- **Hồi 4 (SC04: 13 - 18s) — Cú Twist Meme Hài Hước**: Kết thúc bằng một cú bẻ lái bất ngờ, dở khóc dở cười gắn liền với đời sống (ví dụ: phát hiện chủ nhật ngủ tiếp, làm nhầm việc, người yêu cũ ghé thăm...), tạo ấn tượng vui nhộn và nhớ lâu.

Một cảnh có nhiều hình; một hình có thể dùng qua nhiều nhịp. Ảnh biến thể dùng based_on tới ảnh trước cùng cảnh, mô tả preserve/change và lý do cần ảnh. Chốt narration/narration_en trước, rồi mới đặt coverage/claims/anchor lên trên — không sửa lời dẫn sau khi đã đặt neo. Nhịp neo nguyên văn narration theo quote/occurrence, riêng vi/en; nhịp đầu bắt đầu lời dẫn. Đủ bối cảnh phải có đủ ảnh và visual beats (ví dụ nêu 3 tình huống phải có đủ 3 ảnh và 3 nhịp tương ứng); điểm neo (anchor quote) của từ khóa/công thức phải đặt sớm trong câu để thời gian hiển thị đủ để đọc; 2.5–3.5 giây chỉ là gợi ý cho nhãn ngắn, câu dài phải đo và thử đọc riêng. Lời dẫn tiếng Việt chứa từ tiếng Anh không viết in hoa toàn bộ (tránh TTS đọc đánh vần từng chữ); giữ đại từ I đúng chính tả; thay phát âm chỉ ở đầu vào TTS, không sửa narration/phụ đề/anchor. narration_en bắt buộc dual/16:9. Không đặt mốc giây giả như đã đo. Khi viết lời dẫn, đọc [văn phong](references/narration-style.md); chỉ tra [dấu hiệu văn phong máy](references/ai-tells.md) khi cần. Adapter nạp văn phong vào lượt viết chi tiết, không vào lượt outline.


Chữ minh họa tạo cùng ảnh: visible_text liệt kê chính xác chữ, đối tượng và vị trí. Danh sách rỗng nghĩa là không chữ/số. Kiểu/màu/cỡ/vùng an toàn lấy từ planning.text_style. Mã nhân vật/cảnh/ảnh chỉ là metadata, không viết vào description/preserve/change hoặc chữ nhìn thấy. Phụ đề lời đọc vẫn dựng riêng. Không thay mẫu prompt_templates.py.

coverage liên kết ý với câu trích; job dual/16:9 cần cả quote và quote_en trong cùng một cảnh. Trích đúng nguyên văn không chứng minh đủ nghĩa — bản tiếng Anh phải tự nó truyền đạt được ý bắt buộc, vì bản 16:9 phát hoàn toàn bằng tiếng Anh và không có phụ đề. claims liên kết phát biểu với dữ kiện/nguồn thật; không bịa. Kiểm tra đúng mục tiêu, tự nhiên, đủ nghĩa, không lặp, tương đương Việt/Anh và có thể minh họa. Thời lượng do WAV ở bước media quyết định. Khoảng ước tính trong bản duyệt chỉ để tham khảo, không dùng nó để cắt bớt nội dung.

Sửa qua reject content; đọc phản hồi thật và bản trước, ghi revision_response đúng request_id, giải thích cảnh/trường thay đổi hoặc unresolved. Không sửa revisions/reviews/SQLite. check-draft rồi run JOB content; review bàn giao đúng revision và review.md. Auto dùng bộ đánh giá qua điều phối, không tự tạo báo cáo pass.
