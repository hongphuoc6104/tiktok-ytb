---
name: vp-media
description: Tạo, kiểm tra hoặc sửa âm thanh, ảnh và nhịp thị giác trong giai đoạn media của Video Pilot.
---

# Media

Chạy lệnh từ `sys/`. Theo `AGENTS.md` và `docs/workflow.md`; kiểm tra `status JOB` và `next JOB` trước sản xuất.

Sau quyết định content hợp lệ, dùng `python3 pilot.py run JOB media` hoặc `resume JOB`. Đọc [âm thanh](references/audio.md) khi tạo/sửa giọng, [hình ảnh](references/images.md) khi tạo/sửa ảnh. Lượt tạo media mới cần cả hai.

Thứ tự bắt buộc: tạo âm thanh → đo WAV → tạo ảnh theo kế hoạch → đối chiếu nhịp và phụ đề. Audio/images là bước nội bộ; chỉ duyệt chung tại media. Giữ CH01 và hai tham chiếu Character/Base cho ảnh kế thừa; không gửi lại yêu cầu chưa rõ kết quả.

Bàn giao toàn bộ WAV, ảnh/nhân vật, SRT, thời lượng thật và review.md đúng revision. Không coi thời điểm nội suy là căn chỉnh từ đã đo. Review chờ người dùng; auto đi qua bộ đánh giá thật, unsupported thì dừng.

Sửa giọng: `reject JOB media --revision N --part audio --note 'phản hồi thật'`, có thể thêm `--scene`. Sửa ảnh thêm `--scene` hoặc `--character`; sửa lời dẫn phải reject content. Khi media được duyệt, tiếp tục với `vp-video`.
