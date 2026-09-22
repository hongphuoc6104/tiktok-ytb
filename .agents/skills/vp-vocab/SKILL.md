---
name: vp-vocab
description: Tạo hoặc tiếp tục video dạy một nghĩa từ vựng tiếng Anh từ kho vocab của Video Pilot; dùng cho yêu cầu video từ vựng, không áp dụng chỉ vì video có tỷ lệ 9:16.
---

# Điều phối video từ vựng

Lệnh tính từ `sys/`. Đọc `AGENTS.md`, `docs/workflow.md` và `docs/vocabulary.md`. Một video dạy đúng một nghĩa; giữ chỗ và cập nhật kho qua `vocab/bank.py`, không viết brief hay ledger bằng tay.

## Bắt đầu

Dùng `python3 vocab/bank.py start JOB --mode review` cho job mới. Chỉ dùng `--mode auto` khi người dùng yêu cầu tự động; mode của job đã có giữ nguyên. Tỷ lệ lấy từ yêu cầu và cấu hình kênh; dùng `--aspect-ratio 9:16` khi yêu cầu bản dọc. Muốn chọn từ cụ thể, thêm `--word WORD`, đối chiếu nghĩa được rút trước sản xuất; không thay từ ngoài kho.

Khi tiếp tục job, không start/draw lại. Chạy `python3 pilot.py status JOB` và `python3 pilot.py next JOB`.

## Thứ tự

1. Đọc `vp-content/SKILL.md` ở thư mục skills bên cạnh; chạy `python3 pilot.py run JOB content`. Bố cục và số cảnh lấy từ brief/channel. Chốt lời dẫn trước coverage/anchor.
2. Sau quyết định content hợp lệ, đọc `vp-media/SKILL.md`; chạy `python3 pilot.py run JOB media`. Âm thanh trước, đo WAV, sau đó ảnh và nhịp. Giữ tốc độ TTS cấu hình kênh (hiện 0.92), không tự đổi. Câu ví dụ tiếng Anh trong narration Việt cần dấu câu rõ; giữ narration_en là tiếng Anh chuẩn khi brief yêu cầu.
3. Sau quyết định media hợp lệ, đọc `vp-video/SKILL.md`; chạy `python3 pilot.py run JOB video`.
4. Khi video đã có quyết định hợp lệ và xuất thành công, chạy `python3 vocab/bank.py mark JOB`. Trả đường dẫn MP4 thật trong `video/<job>/`, không gán revision 1.

Review dừng đúng ba điểm content/media/video, đưa review.md và revision. Auto dùng báo cáo xem/nghe artifact thật; unsupported hoặc lỗi đăng nhập/CAPTCHA/hạn mức thì dừng, không tự pass. Skill hướng dẫn agent điều phối CLI, không gọi lớp Pilot để vượt gate.

Lỗi hoặc yêu cầu sửa: dùng reject đúng stage/phạm vi rồi resume; giữ journal ambiguous và đối chiếu trước gửi lại. Không mark chỉ vì render thành công. Không dùng --force để hoàn tất job pipeline bị chặn.

Nhiều video: chỉ dùng queue/batch hữu hạn khi được yêu cầu, mark từng job đạt. Sau hoàn tất có thể dùng `vp-clean` để kiểm kê dữ liệu tạm; dọn dẹp không là điều kiện hoàn tất và không tự xóa media/bằng chứng.
