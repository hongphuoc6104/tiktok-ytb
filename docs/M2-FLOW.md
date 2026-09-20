# Google Flow trong phần media

Dùng pilot.py, không gọi CLI tạo ảnh trực tiếp. Xem workflow.md cho ba điểm duyệt chính.
Sau content được duyệt, kết nối qua `python3 pilot.py flow-login JOB`.
Agent kiểm tra giao diện thật: chế độ ảnh, model đúng config.json, đúng tài khoản/profile/project, 0 credit cho image và character-register. Không suy chi phí từ số dư. Không tạo ảnh trắng làm bằng chứng.
Ghi JSON gồm observed_at (Unix timestamp thực), mode=image, model, profile, project, credits_per_generation=0, account_confirmed=true, observer, operations=["image","character-register"], screenshot (đường dẫn ảnh chụp thật).
Gọi `python3 pilot.py flow-preflight JOB --evidence FILE`, sau đó `python3 pilot.py run JOB media`.
Bằng chứng hết hạn sau 10 phút: kiểm tra giao diện mới. Không tự thay timestamp.

Ảnh nhân vật và đăng ký là bước nội bộ. Trong review, ảnh chuẩn và ảnh đăng ký đều được đưa vào media để người dùng đối chiếu; không xin duyệt riêng. Trong auto, máy so sánh ảnh đăng ký trước khi dùng; thiếu khả năng đánh giá thì blocked.

Timeout sau gửi: không retry. Dùng `flow-reconcile JOB --request SHA256 --asset FILE --evidence FILE --note 'Kết quả đã đối chiếu'`. Evidence gồm request, mode, characters, actual_prompt, matched_download=true, observer, screenshot thật. Chỉ xác nhận sau đối chiếu kết quả với yêu cầu cũ.
Sửa ảnh bằng `reject JOB media --revision N --scene SCxx --note ...`; thay nhân vật dùng --character. Không sửa revisions hoặc xóa journal để tạo lại.
