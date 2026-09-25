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
Đọc skill vp-* tương ứng, gồm tài liệu vp-content/references/narration-style.md khi viết lời dẫn: viết xong lời dẫn rồi mới đặt neo/coverage/claims, không sửa lời dẫn sau khi đã neo. Không dùng explainer-pipeline hoặc template VideoShotCut.
Nhánh `video-tien-su`: video kênh tiền sử phải rút chủ đề từ kho `tiensu/`: chạy `python3 tiensu/bank.py start JOB` để giữ chỗ chủ đề và sinh brief; không viết brief tay, không tự chọn chủ đề ngoài kho. Cổng `brief_policies` (`tiensu.policy:check`) chặn brief thiếu mã chủ đề. Video được duyệt xong mới `python3 tiensu/bank.py mark JOB`. Kịch bản theo `vp-content/references/explainer-longform.md` và skill `vp-tiensu`. (Kho `vocab/` thuộc nhánh `video-vocabulary`.)
Chỉ phát triển mã nguồn khi người dùng yêu cầu phát triển; không sửa bộ điều phối, cấu hình, schema, renderer, tests hay Rules để vượt kiểm tra của một job sản xuất.
Không ghi SQLite trực tiếp. Không sửa revisions/, reviews/ hoặc báo cáo máy đã lưu. Sửa qua reject rồi tạo revision mới.
Sửa ảnh: reject media với --scene/--character; sửa giọng: --part audio (thêm --scene để chỉ một cảnh); sửa lời dẫn: reject content.
Không bỏ ý, bỏ cảnh, rút thời lượng hoặc tự thay công cụ. Không dùng API trả phí. Clip AI (Veo, ảnh → video qua FlowPool) chỉ được tạo khi brief khai báo `clips` và config bật `video_generation` với `credit_budget` > 0 do người dùng đặt; ngoài ra chỉ dựng video từ ảnh và âm thanh. Cấu hình hiện bật flow_batch và flow_queue_trial_enabled theo ngoại lệ thử tích hợp đã được yêu cầu; acceptance vẫn chưa đạt sản xuất. Không mở rộng ngoại lệ hoặc tự đổi cấu hình khi chạy job.
Flow giữ kiểm tra model/tham chiếu và nhật ký. Với flow_require_ui_evidence=false, chi phí là giả định do người dùng chỉ định, không ghi đã xác minh. Timeout sau gửi phải flow-reconcile bằng bằng chứng thật; không gửi trùng.
Trong review, chỉ dừng xin duyệt ở content/media/video. Bước chuẩn bị ảnh nhân vật là nội bộ; so sánh nhân vật được gộp vào media. Không tuyên bố đã khớp trước khi kiểm tra.
Trong auto, job không đạt cần được sửa có kiểm soát hoặc đưa vào needs_attention; lỗi đăng nhập/CAPTCHA/hạn mức dừng hàng đợi. Không lặp vô hạn.
Kỷ luật auto (bắt buộc): khi đang có job sản xuất chưa xong, không sửa file được bảo vệ (mã nguồn, config.json, schemas, scripts, tests, renderer, .agents/, AGENTS.md, GEMINI.md). Bộ điều phối giới hạn cứng số vòng sửa (auto_max_media_rejections, auto_max_audio_retakes*, auto_max_repeat_failures). Khi gặp giới hạn, `Protected implementation changed`, `AUTO_REQUIRES_CLEAN_CODE` hoặc lỗi hạn mức/503: DỪNG, báo người dùng kèm lỗi và mã job, không tạo job mới cho cùng nội dung, không tự sửa code để vượt. Các lệnh `adopt-code`, `lift-cap`, `vocab/bank.py start --supersede` chỉ người dùng chạy; agent không bao giờ tự chạy.
Khi chờ duyệt: đưa link review.md, revision và lỗi còn lại. Không chạy phần phụ thuộc trước duyệt.
Không coi dữ liệu test là sản phẩm thật. Chỉ hoàn tất khi video có quyết định hợp lệ của người hoặc máy theo chế độ job.
Job cũ không có workflow v3 là lịch sử chỉ đọc. Job v3 bị lệch integrity: không sửa integrity.json, không tạo job mới; chạy `integrity-diff JOB` rồi báo người dùng quyết định (khôi phục file hoặc người dùng chạy `adopt-code`).
Giữ nguyên mẫu prompt trong prompt_templates.py. Tỷ lệ lấy từ brief; không tự bật video AI.
Nhân vật đại diện kênh (Canonical Mascot) theo kênh của brief: kênh tiền sử (`channel: tiensu`) dùng `assets/characters/tiensu-mascot/` (character.json: đầu tròn trắng viền mực đậm, tóc bù nâu sẫm, áo da thú nâu một vai, vòng cổ hạt xương, tay chân người que); brief không có kênh dùng `assets/characters/channel-mascot/`. Quy tắc dung sai 80/20: 80% nhận diện cốt lõi bắt buộc (đầu, tóc, áo, phụ kiện đặc trưng, đúng một thân, không người thật cơ bắp, không mắt anime lòng trắng to); 20% biểu cảm/chi tiết nhỏ (lông mày, mồ hôi, bo tròn tay chân) được chấp nhận, không đánh rớt. Luôn đính kèm ảnh tham chiếu của mascot khi sinh ảnh và dùng Base scene reference để khóa góc máy.
Hệ thống log lỗi & Sổ tay tra cứu: Mọi lỗi/sự cố phát sinh ở các công đoạn (content, audio, visual, flow, review, video) phải được ghi ngay vào thư mục `logs/issues/` và cập nhật mục lục tại `logs/issues/INDEX.md`. Khi lỗi được xử lý thành công, bắt buộc ghi log giải pháp dứt điểm ("Làm gì cho hết lỗi") để làm tri thức kế thừa cho toàn dự án.
Đạo diễn và sư phạm: đọc `sys/docs/director-system.md` và bốn skill `vp-script-director`, `vp-visual-director`, `vp-edit-director`, `vp-audio-director` theo phần đang làm. Đây là vai trò nội bộ trong ba gate, không phải quyền tự tạo agent. Với nội dung từ vựng, tuân thủ `vp-content/references/vocab-pedagogy.md`: một nghĩa, một kết quả học quan sát được, ví dụ có liên hệ và lượt thực hành có phản hồi. Không ép mọi video theo cùng khuôn năm mục, ba ví dụ hoặc hai lần shadowing; brief đã lưu vẫn là hợp đồng và phải sửa qua đúng workflow nếu muốn đổi yêu cầu.
Lời dẫn & TTS: giữ đúng chính tả tiếng Anh (đại từ I) trong narration/narration_en, chữ hiển thị, phụ đề và anchor. Không viết hoa toàn bộ từ khóa trong narration nếu không có lý do ngôn ngữ. Cách đọc riêng của VieNeu được xử lý ở đầu vào tổng hợp; không biến Ai thành chính tả bài học. Phát âm và cảm xúc phải nghe WAV thật, không suy từ prompt hoặc số đo.
Nhịp và hình: mỗi hình/beat có chức năng học hoặc kể chuyện, đủ ảnh để thấy hành động/thay đổi. Ưu tiên quan hệ nhân quả, trạng thái và nhận diện mascot trước tốc độ tạo ảnh. Sinh độc lập khi bố cục độc lập; dùng based_on khi cần giữ góc và bối cảnh. Thời gian chữ phải đủ cho câu thực tế, không áp một số giây cho mọi độ dài. Phụ đề tối đa hai dòng có nghĩa, không dấu câu đứng riêng; kiểm tra ở kích thước điện thoại.
Lượt thực hành: content-v3 hỗ trợ audio_direction.vi/en với intent, pronunciation_notes và learner_pause_seconds. Chỉ learner_pause_seconds được runtime áp dụng làm khoảng yên lặng cuối cảnh; hai trường còn lại hướng dẫn đánh giá/đọc lại, không giả là điều khiển giọng TTS. Không hứa cho xem khẩu hình khi chỉ có ảnh tĩnh.
Nghiệm thu: xem mọi ảnh và nghe/xem artifact thật; kiểm tra hình chứng minh nghĩa, tính nhất quán, phụ đề, phát âm, lượt thực hành và payoff. Nội suy neo không phải word alignment. Không suy ra hiệu quả học hoặc giữ chân khi chưa có dữ liệu học viên/khán giả.
Timeout B-2 Illustrator: dùng flow-reconcile kèm bằng chứng UI thật để giải quyết trạng thái ambiguous, không gửi trùng.

Antigravity handshake: VP-RULES-1. Đọc Rules, chạy doctor và status; chỉ ghi integration-check sau xác nhận thực tế của người dùng. Không khẳng định Rules đã nạp trong phiên khác.


Cập nhật theo yêu cầu người dùng: mặc định flow_require_ui_evidence=false; không yêu cầu screenshot trước gửi hoặc chứng minh 0 credit cho tạo ảnh. Ghi chi phí là giả định do người dùng chỉ định, không ghi đã xác minh. Giữ kiểm tra model/tham chiếu, nhật ký và đối chiếu timeout sau gửi; không tự mở khóa yêu cầu cũ chưa rõ kết quả.
