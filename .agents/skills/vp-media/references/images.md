Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Hình ảnh trong media

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Đọc docs/M2-FLOW.md. Dùng run JOB media; ảnh chuẩn và đăng ký là nội bộ, không xin duyệt riêng. Không còn checkpoint ba cảnh đầu. Bàn giao mọi cảnh và ảnh đăng ký cùng WAV ở media. Mặc định không yêu cầu screenshot trước gửi; chi phí là giả định của người dùng, không phải đã xác minh. Timeout sau gửi dùng flow-reconcile với bằng chứng thật, không gửi trùng. Sửa từng cảnh/nhân vật bằng reject media --scene/--character. Không gọi CLI trực tiếp.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.

Job content 3.0: đọc docs/story-planning.md. Tạo đầy đủ scenes[].images cho từng tỷ lệ yêu cầu, không mặc định một ảnh/cảnh. based_on cần đính kèm ảnh trước thật, tạo theo thứ tự; thiếu bằng chứng đính kèm thì dừng. Chữ tạo cùng hình theo visible_text và planning.text_style; không tự thêm nhãn, mã nội bộ, logo. Ở media phải kiểm tra từng ảnh về đúng chữ, không chữ thừa, kiểu/màu/vị trí và tính liên tục. Đối chiếu visual-timing.json với âm thanh thật; thời điểm nội suy chưa phải căn chỉnh từ đã đo. Sửa --scene sẽ áp dụng cho các hình thuộc cảnh đó.

Quy trình B-2 Illustrator dùng Persistent Session (`b2_bridge.py` kết nối `session.sock`) với Base Scene cho cảnh `based_on` và Character cho nhân vật thực sự có trong ảnh. Brief canonical giữ mascot theo kênh; brief `character_mode: story_cast` không tự gắn mascot và có thể để trống Character cho cảnh độc lập không người. Nhân vật riêng của video cần ảnh tham chiếu/media ID đúng tài khoản Flow và phải được xem thật để xác nhận. Không suy ra chất lượng từ prompt hoặc ID; chỉ dẫn 80/20 áp dụng cho nhận diện cốt lõi của nhân vật đã khai báo. Khi Applet gặp UNKNOWN, STABILITY ALERT hoặc timeout, giữ nguyên nhật ký và đối chiếu UI thật; không xóa localStorage, không tự gửi lại. Đọc docs/flow-queue-operations.md cho điều kiện vận hành.



Cập nhật theo yêu cầu người dùng: mặc định flow_require_ui_evidence=false; không yêu cầu screenshot trước gửi hoặc chứng minh 0 credit cho tạo ảnh. Ghi chi phí là giả định do người dùng chỉ định, không ghi đã xác minh. Giữ kiểm tra model/tham chiếu, nhật ký và đối chiếu timeout sau gửi; không tự mở khóa yêu cầu cũ chưa rõ kết quả.
