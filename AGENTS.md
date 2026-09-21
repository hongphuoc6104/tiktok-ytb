# Video Pilot — quy trình chính v3

## Vị trí hệ thống

Agent bắt đầu hoặc quay lại dự án: đọc [INDEX.md](INDEX.md) ở gốc để tra bản đồ thư mục, đường dẫn cũ → mới và lệnh chạy.

Mã nguồn và dữ liệu nằm trong `sys/`; video cho người dùng nằm trong `video/<tên-video>/`. Các đường dẫn vận hành bên dưới tương đối với `sys/`: chạy `cd sys` trước khi dùng. Có thể chạy `python3 pilot.py` từ gốc qua launcher, nhưng đường dẫn --brief/--evidence phải là đường dẫn từ thư mục hiện tại. `.agents/`, `.git/`, `.claude/` ở gốc là các ngoại lệ bắt buộc cho công cụ. Không ghi dữ liệu hệ thống mới ở gốc.


Dự án này dùng đúng ba phần công khai: **content → media → video**.
- content: mục tiêu riêng của job, kịch bản Việt/Anh, cảnh/hình/nhịp, nhân vật, chữ được phép và thời lượng dự kiến riêng từng ngôn ngữ. Không gán cứng chủ đề.
- media: âm thanh Việt/Anh (chạy trước, đo thời lượng thật), ảnh cảnh/biến thể, ảnh nhân vật/đăng ký nhân vật, phụ đề và kế hoạch nhịp theo âm thanh.
- video: toàn bộ bản video được yêu cầu.

## Ngôn ngữ giao tiếp và prompt

- Mọi nội dung trình bày cho người dùng phải bằng tiếng Việt, gồm kế hoạch (plan), danh sách công việc, cập nhật tiến độ, giải thích, câu hỏi, báo cáo duyệt và kết quả cuối cùng. Giữ nguyên tên kỹ thuật, lệnh và định danh khi cần.
- Chỉ dẫn nội bộ mặc định dùng tiếng Anh: giao việc/bàn giao giữa các agent, prompt tạo hình, phân tích, đánh giá, kiểm tra và sửa lỗi. Quy tắc này không tự cho phép tạo thêm agent hoặc thay đổi công cụ/quy trình.
- Tách chỉ dẫn khỏi dữ liệu: giữ nguyên ngôn ngữ và nội dung của lời dẫn, phụ đề, chữ cần hiển thị, câu trích, nguồn, tên file, định danh và phản hồi người dùng. Không dịch dữ liệu sang tiếng Anh chỉ vì prompt chỉ dẫn dùng tiếng Anh; đặc biệt giữ nguyên quote/anchor/coverage đã chốt.
- Nội dung dành cho người Việt dùng tiếng Việt tự nhiên. Nội dung học tiếng Anh hoặc phiên bản tiếng Anh theo brief giữ đúng ngôn ngữ yêu cầu; không đổi narration_en thành tiếng Việt.
- Prompt đánh giá nội bộ dùng tiếng Anh nhưng phải xét đúng ngôn ngữ, văn hóa và đối tượng của nội dung; phần đánh giá/giải thích hiển thị cho người dùng phải bằng tiếng Việt. Giữ nguyên schema, khóa và giá trị máy đọc bắt buộc.
- Áp dụng cho chỉ dẫn mới; không sửa mẫu cố định trong prompt_templates.py, revision, bằng chứng hay báo cáo lịch sử chỉ để đổi ngôn ngữ. Nếu người dùng yêu cầu rõ ngôn ngữ khác cho một đầu ra, làm theo yêu cầu đó.

## Hai chế độ
- `review` (mặc định): người dùng duyệt đúng ba phần và revision hiện tại. Ghi nguyên văn phản hồi bằng `approve`; không tự suy ra đồng ý.
- `auto`: bộ đánh giá máy xem/nghe artifact thật, lưu báo cáo rồi quyết định. Không cần người dùng duyệt từng phần. Không dùng lệnh approve của người dùng trong auto.
- Chế độ cố định khi `new --mode review|auto`; không sửa workflow.json để đổi giữa chừng.
- Kiểm tra kỹ thuật nội bộ không phải duyệt chất lượng. Không tạo ảnh bằng chứng giả, không ghi phản hồi người dùng giả. Thiếu khả năng nghe/xem phải báo unsupported và giữ job chưa hoàn tất.

## Thực hiện
Đọc `docs/workflow.md`. Chạy `python3 pilot.py status JOB` và `next JOB` trước lượt sản xuất.
Dùng `run JOB` hoặc `resume JOB` để tiến đến điểm duyệt tiếp theo; không gọi lớp Pilot trực tiếp để vượt gate.
Đọc skill vp-* tương ứng, gồm vp-humanizer khi viết lời dẫn: viết xong lời dẫn rồi mới đặt neo/coverage/claims, không sửa lời dẫn sau khi đã neo. Không dùng explainer-pipeline hoặc template VideoShotCut.
Chỉ phát triển mã nguồn khi người dùng yêu cầu phát triển; không sửa bộ điều phối, cấu hình, schema, renderer, tests hay Rules để vượt kiểm tra của một job sản xuất.
Không ghi SQLite trực tiếp. Không sửa revisions/, reviews/ hoặc báo cáo máy đã lưu. Sửa qua reject rồi tạo revision mới.
Sửa ảnh: reject media với --scene/--character; sửa giọng: --part audio (thêm --scene để chỉ một cảnh); sửa lời dẫn: reject content.
Không bỏ ý, bỏ cảnh, rút thời lượng hoặc tự thay công cụ. Không dùng API trả phí. Tạo video AI bị khóa; chỉ dựng video từ ảnh và âm thanh. Không tự bật flow_batch trên job sản xuất; tính năng chưa nghiệm thu với Flow thật.
Flow cần bằng chứng giao diện thật, còn hạn, đúng tài khoản/model và 0 credit. Timeout sau gửi phải flow-reconcile; không gửi trùng.
Trong review, chỉ dừng xin duyệt ở content/media/video. Bước chuẩn bị ảnh nhân vật là nội bộ; so sánh nhân vật được gộp vào media. Không tuyên bố đã khớp trước khi kiểm tra.
Trong auto, job không đạt cần được sửa có kiểm soát hoặc đưa vào needs_attention; lỗi đăng nhập/CAPTCHA/hạn mức dừng hàng đợi. Không lặp vô hạn.
Khi chờ duyệt: đưa link review.md, revision và lỗi còn lại. Không chạy phần phụ thuộc trước duyệt.
Không coi dữ liệu test là sản phẩm thật. Chỉ hoàn tất khi video có quyết định hợp lệ của người hoặc máy theo chế độ job.
Job cũ không có workflow v3 là lịch sử chỉ đọc; không sửa integrity baseline để chạy tiếp. Tạo job mới với brief đã kiểm tra.
Giữ nguyên mẫu prompt trong prompt_templates.py. Tỷ lệ lấy từ brief; không tự bật video AI.
Nhân vật đại diện kênh cố định (Canonical Mascot): Mọi kịch bản và video sản xuất trong dự án bắt buộc sử dụng nhân vật đại diện chuẩn tại assets/characters/channel-mascot/reference-v1.png (cấu hình tại assets/characters/channel-mascot/character.json, Media ID: de94a39b-155f-4afe-acbb-d9d4b59ad532) làm nhân vật chính (CH01). Ngoại hình: đầu tròn trắng viền xanh đen đậm, hai mắt oval đen đặc tối giản, miệng cười tươi lưỡi san hô, áo thun cộc tay màu xanh biển nhạt (#8CCFE8), tay chân người que tối giản, đúng một thân duy nhất. Cấm vẽ răng, lông mày, lòng trắng hoạt hình hay hai thân áo. Luôn đính kèm ảnh tham chiếu này vào Character reference khi sinh ảnh và sử dụng Base scene reference để khóa góc máy.
Lời dẫn & Vieneu TTS: Không viết hoa toàn bộ từ khóa tiếng Anh trong narration (tránh TTS đọc đánh vần từng ký tự); đại từ tiếng Anh I dùng 'Ai' để phát âm tự nhiên.
Nhịp thị giác: Đủ bối cảnh phải có đủ ảnh và visual beats; neo từ khóa/công thức sớm để hiển thị tối thiểu 2.5 - 3.5 giây.
Timeout B-2 Illustrator: dùng flow-reconcile kèm bằng chứng UI thật để giải quyết trạng thái ambiguous, không gửi trùng.

Antigravity handshake: VP-RULES-1. Đọc Rules, chạy doctor và status; chỉ ghi integration-check sau xác nhận thực tế của người dùng. Không khẳng định Rules đã nạp trong phiên khác.

## Định hướng riêng của nhánh nghiên cứu
Đọc docs/research-channel.md trước khi lập brief hoặc viết kịch bản. Nội dung phục vụ giải thích nghiên cứu và hướng dẫn nghiên cứu; không tự chuyển thành bài học từ vựng. Chủ đề cụ thể vẫn lấy từ yêu cầu từng job. Giữ cả hai giọng và nhân vật chuẩn.

Video mới trên nhánh nghiên cứu lấy đề tài qua research/bank.py (reserve → prepare → start), sau duyệt video dùng mark. Đọc research/README.md khi cần vận hành kho. Không nạp TOPICS.md, index.html, catalog/topics.txt hoặc toàn bộ topics/ vào prompt; chỉ next tối đa 5 mục rồi show một mã.
