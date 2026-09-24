---
trigger: always_on
---

Thư mục hệ thống là `sys/`; các đường dẫn bên dưới tính từ thư mục này. Video xuất cho người dùng ở `../video/<tên-video>/`.

Đọc AGENTS.md và docs/workflow.md. Chỉ ba phần content → media → video; review hoặc auto theo job. Không tự tạo bằng chứng hoặc bỏ kiểm tra.
Mọi video của dự án luôn sử dụng nhân vật đại diện kênh cố định tại assets/characters/channel-mascot/reference-v1.png (CH01, áo xanh biển nhạt #8CCFE8, Media ID: de94a39b-155f-4afe-acbb-d9d4b59ad532).
Giải phẫu CH01 chuẩn & Quy tắc dung sai nhận diện 80/20: Không đòi hỏi giống 100% kịch bản hay tuyệt đối hóa chi tiết nhỏ, cho phép sai lệch 20% ở các chi tiết biểu cảm nhỏ và nét phụ. 80% là nhận diện thương hiệu cốt lõi bắt buộc: đúng 1 thân duy nhất, áo thun cộc tay xanh biển nhạt #8CCFE8, 2 tay & 2 chân que navy tối giản, đầu tròn trắng viền navy đậm, 2 mắt oval đen đặc tối giản. Tuyệt đối cấm các lỗi vi phạm thương hiệu 80%: vẽ người thật cơ bắp, mắt hoạt hình anime có tròng trắng to/đồng tử, vẽ 2 thân áo đè lên nhau, áo sai màu. 20% dung sai cho phép: nét lông mày biểu cảm nhẹ (buồn bã, nhíu mày, lo lắng), nếp nhăn trán nhỏ, giọt mồ hôi, nét bo tròn bàn chân/bàn tay khi cử động... ĐƯỢC CHẤP NHẬN, cấm đánh rớt (verdict: fail) vì 20% chi tiết này. Luôn đính kèm ảnh tham chiếu và dùng dual-reference (Base + Character).
Creative direction: follow `docs/director-system.md` and load the relevant vp-script-director / vp-visual-director / vp-edit-director / vp-audio-director skills within the existing three stages. These are responsibilities, not permission to spawn agents. Preserve the current brief; new defaults do not rewrite existing jobs.
Vocabulary lessons: one sense, a clear learner action, causally connected examples or a meaningful contrast, and a feasible practice turn with feedback. No universal five-part lecture, three-example quota, two-repeat quota or image-count quota; honor any such requirement explicitly present in the current brief.
Keep correct English I in narration, captions, visible_text and anchors; VieNeu-only pronunciation normalization must not leak into learner text. Listen to verify pronunciation. Do not promise moving mouth demonstrations with static images.
Direct each frame/cut for meaning; continuity and mascot identity precede throughput. Keep captions in meaningful groups, at most two readable lines, with no punctuation-only cues. Check actual phone-size frames and full playback.
Optional content-v3 audio_direction.vi/en carries intent, pronunciation_notes and learner_pause_seconds. Only the scene-tail learner hold is a runtime control; other notes require actual listening/retakes. Include practice time in measured duration. No new provider or sound-mixing capability is implied.
B-2 Illustrator: Chạy qua persistent session socket. Nếu gặp sự cố timeout (state: ambiguous), phải dùng `python3 pilot.py flow-reconcile` kèm bằng chứng UI thật, tuyệt đối không gửi request trùng lặp.
Video dạy từ vựng lấy từ kho vocab/: `python3 vocab/bank.py start JOB` sinh brief và giữ chỗ; duyệt xong video mới `mark`. Không tự chọn từ ngoài kho, không viết brief từ vựng bằng tay.
Quản lý log lỗi và tra cứu sự cố: Mọi sự cố/lỗi phát sinh ở bất kỳ công đoạn xử lý nào (content, audio, visual, flow, review, video) phải được ghi ngay vào thư mục `logs/issues/` và cập nhật mục lục tại `logs/issues/INDEX.md`. Khi xử lý thành công, bắt buộc ghi log giải pháp dứt điểm ("Làm gì cho hết lỗi") để kế thừa kinh nghiệm vận hành.


Ngôn ngữ: tuân thủ mục “Ngôn ngữ giao tiếp và prompt” trong AGENTS.md. Mọi kế hoạch (plan), tiến độ và kết quả hiển thị cho người dùng dùng tiếng Việt; chỉ dẫn/prompt nội bộ mặc định dùng tiếng Anh. Giữ nguyên ngôn ngữ dữ liệu, câu trích, chữ hiển thị và các trường máy đọc bắt buộc.

Video từ vựng bắt đầu với vp-vocab; lần lượt đọc vp-content → vp-media → vp-video. vp-clean chỉ bảo trì dữ liệu tạm. Mark sau quyết định hợp lệ và xác minh video đã xuất.
