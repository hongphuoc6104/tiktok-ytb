---
name: vp-images
description: Tạo và duyệt ảnh Google Flow cho Video Pilot qua pilot.py, gồm ảnh chuẩn nhân vật, ba cảnh đầu và toàn bộ sáu cảnh. Dùng riêng module M2; không tạo video AI.
---
# Module hình ảnh

Đọc AGENTS.md, chạy `status JOB` và `next JOB` trước mọi lượt. Đọc `docs/M2-FLOW.md` khi cần cú pháp kết nối, bằng chứng hoặc khôi phục; hợp đồng ở `schemas/images-v2.json`.

- Chỉ dùng nội dung v2 đã duyệt. `run JOB images` tự chọn nhóm được phép: `references` → `first-three` → `final`.
- Khi chờ duyệt, đưa mã công việc, revision, checkpoint và link `review.md`; dừng. Phản hồi duyệt rõ của người dùng được ghi nguyên văn bằng `approve JOB images --checkpoint ... --revision ... --note ...`. Chỉ `final` duyệt xong mới bàn giao.
- Ảnh chuẩn tạo trên Flow. Đăng ký nhân vật có thể sinh ngoại hình khác: cần bằng chứng người dùng đã đối chiếu qua `flow-confirm-registration`; không tự khai khớp.
- Trước mỗi thao tác tạo, cần bằng chứng mới về 0 credit đúng loại `image` hoặc `character-register`. Không suy từ số dư tài khoản hay từ việc tài khoản từng được miễn phí.
- Timeout sau gửi: đọc mã request, dùng `flow-reconcile` với kết quả được xác minh hoặc báo blocked; không gọi CLI trực tiếp để thử lại.
- Sửa ảnh bằng `reject` với checkpoint/revision, đúng `--scene` hoặc `--character` và lý do người dùng. Không sửa file trong revisions, không tự sinh biến thể cho đẹp hơn.
- Bảng ảnh có cả ảnh kiểm chứng nhân vật riêng khi cần; chỉ sáu `items` là ảnh cảnh bàn giao.
- Prompt chuẩn do người dùng cung cấp nằm trong `prompt_templates.py`. Bản thử dùng biến thể 9:16 từng ảnh; không gửi cả batch vượt điểm duyệt. Mẫu video chỉ lưu tham khảo, bị khóa thực thi.
- Kiểm tra kỹ thuật không chứng minh nét mặt, trang phục hoặc diễn biến đúng. Luôn cần người dùng duyệt thẩm mỹ.
