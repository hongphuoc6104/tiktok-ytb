# Video Pilot — quy trình chính v3

Dự án này dùng đúng ba phần công khai: **content → media → video**.
- content: kịch bản Việt/Anh, số cảnh, nhân vật, prompt, thời lượng dự kiến.
- media: toàn bộ ảnh cảnh, ảnh nhân vật/đăng ký nhân vật, âm thanh Việt/Anh, phụ đề và thời lượng thật.
- video: toàn bộ bản video được yêu cầu.

## Hai chế độ
- `review` (mặc định): người dùng duyệt đúng ba phần và revision hiện tại. Ghi nguyên văn phản hồi bằng `approve`; không tự suy ra đồng ý.
- `auto`: bộ đánh giá máy xem/nghe artifact thật, lưu báo cáo rồi quyết định. Không cần người dùng duyệt từng phần. Không dùng lệnh approve của người dùng trong auto.
- Chế độ cố định khi `new --mode review|auto`; không sửa workflow.json để đổi giữa chừng.
- Kiểm tra kỹ thuật nội bộ không phải duyệt chất lượng. Không tạo ảnh bằng chứng giả, không ghi phản hồi người dùng giả. Thiếu khả năng nghe/xem phải báo unsupported và giữ job chưa hoàn tất.

## Thực hiện
Đọc `docs/workflow.md`. Chạy `python3 pilot.py status JOB` và `next JOB` trước lượt sản xuất.
Dùng `run JOB` hoặc `resume JOB` để tiến đến điểm duyệt tiếp theo; không gọi lớp Pilot trực tiếp để vượt gate.
Đọc skill vp-* tương ứng. Không dùng explainer-pipeline hoặc template VideoShotCut.
Chỉ phát triển mã nguồn khi người dùng yêu cầu phát triển; không sửa bộ điều phối, cấu hình, schema, renderer, tests hay Rules để vượt kiểm tra của một job sản xuất.
Không ghi SQLite trực tiếp. Không sửa revisions/, reviews/ hoặc báo cáo máy đã lưu. Sửa qua reject rồi tạo revision mới.
Sửa ảnh: reject media với --scene/--character; sửa giọng: --part audio; sửa lời dẫn: reject content.
Không bỏ ý, bỏ cảnh, rút thời lượng hoặc tự thay công cụ. Không dùng API trả phí. Tạo video AI bị khóa; chỉ dựng video từ ảnh và âm thanh.
Flow cần bằng chứng giao diện thật, còn hạn, đúng tài khoản/model và 0 credit. Timeout sau gửi phải flow-reconcile; không gửi trùng.
Trong review, chỉ dừng xin duyệt ở content/media/video. Bước chuẩn bị ảnh nhân vật là nội bộ; so sánh nhân vật được gộp vào media. Không tuyên bố đã khớp trước khi kiểm tra.
Trong auto, job không đạt cần được sửa có kiểm soát hoặc đưa vào needs_attention; lỗi đăng nhập/CAPTCHA/hạn mức dừng hàng đợi. Không lặp vô hạn.
Khi chờ duyệt: đưa link review.md, revision và lỗi còn lại. Không chạy phần phụ thuộc trước duyệt.
Không coi dữ liệu test là sản phẩm thật. Chỉ hoàn tất khi video có quyết định hợp lệ của người hoặc máy theo chế độ job.
Job cũ không có workflow v3 là lịch sử chỉ đọc; không sửa integrity baseline để chạy tiếp. Tạo job mới với brief đã kiểm tra.
Giữ nguyên mẫu prompt trong prompt_templates.py. Tỷ lệ lấy từ brief; không tự bật video AI.

Antigravity handshake: VP-RULES-1. Đọc Rules, chạy doctor và status; chỉ ghi integration-check sau xác nhận thực tế của người dùng. Không khẳng định Rules đã nạp trong phiên khác.
