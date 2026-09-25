---
name: vp-tiensu
description: Tạo hoặc tiếp tục video giải thích đời sống tiền sử/sinh tồn dài 16:9 tiếng Việt từ kho tiensu của Video Pilot; dùng cho yêu cầu video kênh tiensu, không áp dụng cho video từ vựng hay video 9:16.
---

# Điều phối video kênh giải thích tiền sử (tiensu)

Lệnh tính từ `sys/`. Đọc `AGENTS.md`, `docs/workflow.md` và `docs/tien-su-plan.md` (đặc biệt mục
1, 4 GĐ1/GĐ4, 5, 8 — hợp đồng dữ liệu mục 8 ràng buộc mọi trường mới). Một video trả lời đúng một
câu hỏi trong kho; giữ chỗ và cập nhật kho qua `tiensu/bank.py`, không viết brief hay ledger bằng
tay, không tự chọn chủ đề ngoài kho.

## Bắt đầu

Dùng `python3 tiensu/bank.py start JOB --mode review` cho job mới. Chỉ dùng `--mode auto` khi
người dùng yêu cầu tự động; mode của job đã có giữ nguyên. Tỷ lệ/ngôn ngữ/phụ đề lấy từ
`tiensu/channel.json` (16:9, giọng Việt, phụ đề bật) — không cần cờ tỷ lệ như kênh từ vựng.
Muốn chọn đúng một chủ đề, thêm `--id TOPIC_ID` (xem `python3 tiensu/bank.py next --count 10`
để tra id). Chủ đề phải đã có `sources` thật trong `tiensu/topics.jsonl`; `reserve`/`start` chặn
chủ đề chưa có nguồn (facts_required=true không cho sources rỗng).

Khi tiếp tục job, không start lại. Chạy `python3 pilot.py status JOB` và `python3 pilot.py next JOB`.

## Thứ tự

1. Đọc `vp-content/SKILL.md` và `vp-content/references/explainer-longform.md` (adapter tự nạp
   file này vào lượt outline/content vì `brief.channel == "tiensu"`, xem
   `scripts/director_context.py`); chạy `python3 pilot.py run JOB content`. Dùng các vai trò đạo
   diễn theo `docs/director-system.md`. Giữ đúng cấu trúc 5 phần trong `required_points` (R1-R5)
   của brief: hook 2 ngôi "bạn", phá niềm tin phổ biến, nhắc lại câu hỏi bí ẩn, 6-8 chương bằng
   chứng (mỗi chương một nghiên cứu/di chỉ có nguồn, đặt tên vào `scenes[].chapter`), kết callback
   "Bạn thì… còn họ thì…". Viết `packaging` (titles/thumbnail/hook/tags) cùng lúc với kịch bản.
   Ảnh giữ `visible_text: []`; chữ/nhãn/số hiển thị đặt vào `beats[].overlays`. Chốt lời dẫn trước
   khi đặt neo/coverage/claims, không sửa sau khi đã neo.
2. Sau quyết định content hợp lệ, đọc `vp-media/SKILL.md`; chạy `python3 pilot.py run JOB media`.
   Âm thanh tiếng Việt trước, đo WAV thật, sau đó ảnh và nhịp. Video dài (8-12 phút) nên số cảnh
   và lượt tổng hợp TTS nhiều hơn video 9:16 thường gặp; theo dõi log lỗi nếu một cảnh vượt
   `tts_max_chars` (chia câu tự động theo cấu hình hiện có, không tự sửa cấu hình TTS).
   Ảnh loại `clip` (nếu brief có `clips`) dùng `from_image`/`motion` đã viết ở content; đây vẫn là
   nghiệm thu GĐ3b/GĐ6, không tự bật khi chưa được yêu cầu.
3. Sau quyết định media hợp lệ, đọc `vp-video/SKILL.md`; chạy `python3 pilot.py run JOB video`.
4. Khi video đã có quyết định hợp lệ và xuất thành công, chạy `python3 tiensu/bank.py mark JOB`.
   Trả đường dẫn MP4 thật trong `video/<job>/`, không gán revision 1. Đóng gói (thumbnail/mô
   tả/chapters/nguồn, `sys/packaging.py`) là GĐ5, chạy sau khi có sẵn — không tự chạy nếu module
   đó chưa được triển khai trên nhánh.

Review dừng đúng ba điểm content/media/video, đưa review.md và revision. Auto dùng báo cáo
xem/nghe artifact thật; unsupported hoặc lỗi đăng nhập/CAPTCHA/hạn mức thì dừng, không tự pass.
Skill hướng dẫn agent điều phối CLI, không gọi lớp Pilot để vượt gate.

Lỗi hoặc yêu cầu sửa: dùng reject đúng stage/phạm vi rồi resume; giữ journal ambiguous và đối
chiếu trước gửi lại. Không mark chỉ vì render thành công. Không dùng --force để hoàn tất job
pipeline bị chặn.

Nhiều video: chỉ dùng `tiensu/bank.py queue` khi được yêu cầu, mark từng job đạt. Không sản xuất
hàng loạt/lặp nội dung (chính sách kiếm tiền YouTube, xem mục 6 kế hoạch) — mỗi video tự nghiên
cứu, nguồn thật, không dịch/sao chép kênh mẫu Ink Explainer. Sau hoàn tất có thể dùng `vp-clean`
để kiểm kê dữ liệu tạm; dọn dẹp không là điều kiện hoàn tất và không tự xóa media/bằng chứng.

## Bổ sung chủ đề vào kho

Thêm dòng mới vào `tiensu/topics.jsonl` (JSONL, mỗi dòng một chủ đề: `id`, `question`, `angle`,
`seed_facts`, `sources`). `sources` bắt buộc phải là tài liệu/di chỉ/nghiên cứu THẬT có thể tra
cứu lại được (tên tác giả, năm, nơi công bố hoặc tên di chỉ khảo cổ) — không bịa nguồn; thiếu
`sources` thì `tiensu/bank.py start` chặn ngay ở bước sinh brief. `seed_facts` chỉ là gợi ý hướng
nghiên cứu thêm cho người viết kịch bản, không thay thế `sources` đã kiểm chứng.
