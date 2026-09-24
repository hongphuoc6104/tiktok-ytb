---
name: vp-media
description: Tạo, kiểm tra hoặc sửa âm thanh, ảnh và nhịp thị giác trong giai đoạn media của Video Pilot.
---

# Media

Read [visual direction](../vp-visual-director/SKILL.md), [audio direction](../vp-audio-director/SKILL.md) and [editing direction](../vp-edit-director/SKILL.md) for the corresponding planning and actual-media review. These are internal responsibilities, not additional gates.

Chạy lệnh từ `sys/`. Theo `AGENTS.md` và `docs/workflow.md`; kiểm tra `status JOB` và `next JOB` trước sản xuất.

Sau quyết định content hợp lệ, dùng `python3 pilot.py run JOB media` hoặc `resume JOB`. Đọc [âm thanh](references/audio.md) khi tạo/sửa giọng, [hình ảnh](references/images.md) khi tạo/sửa ảnh. Lượt tạo media mới cần cả hai.

Thứ tự bắt buộc: tạo âm thanh → đo WAV → tạo ảnh theo kế hoạch → đối chiếu nhịp và phụ đề. Audio/images là bước nội bộ; chỉ duyệt chung tại media. Giữ CH01 và hai tham chiếu Character/Base cho ảnh kế thừa; không gửi lại yêu cầu chưa rõ kết quả.
Áp dụng quy tắc dung sai 80/20: kiểm tra 80% nhận diện thương hiệu cốt lõi (áo xanh #8CCFE8, người que 1 thân, đầu tròn trắng mắt đen); chấp nhận 20% dung sai sai lệch nhỏ (nét lông mày biểu cảm nhẹ, mồ hôi, nếp trán lo lắng, biến thiên tư thế tứ chi). Không đánh rớt media vì các chi tiết biểu cảm 20% này. Mọi sự cố phát sinh phải ghi vào `logs/issues/` và cập nhật `INDEX.md`.

Bàn giao toàn bộ WAV, ảnh/nhân vật, SRT, thời lượng thật và review.md đúng revision. Không coi thời điểm nội suy là căn chỉnh từ đã đo. Review chờ người dùng; auto đi qua bộ đánh giá thật, unsupported thì dừng.

Sửa giọng: `reject JOB media --revision N --part audio --note 'phản hồi thật'`, có thể thêm `--scene`. Sửa ảnh thêm `--scene` hoặc `--character`; sửa lời dẫn phải reject content. Khi media được duyệt, tiếp tục với `vp-video`.

For a single faulty image, prefer `--image IMAGE_ID --ratio 9:16` over a scene-wide rejection. Read `docs/image-repair-loops.md`: subsequent repairs require `--repair-plan` with actual before/after hashes, stable issue IDs, evidence and active corrections. Keep the user's verbatim note separately. Never repeat an unchanged repair or evade a `needs_attention` stop by renaming an issue. Repeated defects require a concrete pose/composition change, with at most six repairs per target. `repair-status JOB --image IMAGE_ID` shows the current repair context. A generated Flow result may be collected again without generation; unknown submissions still require reconciliation.
