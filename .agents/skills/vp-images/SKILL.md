---
name: vp-images
description: Hình ảnh trong media cho Video Pilot v3; dùng khi chạy hoặc sửa phần này.
---

Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Hình ảnh trong media

Đọc AGENTS.md và docs/workflow.md. Trước sản xuất chạy status JOB và next JOB. Hai chế độ review/auto; chỉ ba phần content/media/video. Không áp dụng hướng dẫn duyệt từng module cũ.

Đọc docs/M2-FLOW.md. Dùng run JOB media; ảnh chuẩn và đăng ký là nội bộ, không xin duyệt riêng. Không còn checkpoint ba cảnh đầu. Bàn giao mọi cảnh và ảnh đăng ký cùng WAV ở media. Flow cần bằng chứng giao diện thật 0 credit; timeout dùng flow-reconcile, không gửi trùng. Sửa từng cảnh/nhân vật bằng reject media --scene/--character. Không gọi CLI trực tiếp.

Quyết định người dùng cần đúng phần/revision và phản hồi nguyên văn. Quyết định máy chỉ qua báo cáo kiểm tra thật. Không tự tạo bằng chứng, không sửa file đã lưu hoặc ghi SQLite trực tiếp.

Job content 3.0: đọc docs/story-planning.md. Tạo đầy đủ scenes[].images cho từng tỷ lệ yêu cầu, không mặc định một ảnh/cảnh. based_on cần đính kèm ảnh trước thật, tạo theo thứ tự; thiếu bằng chứng đính kèm thì dừng. Chữ tạo cùng hình theo visible_text và planning.text_style; không tự thêm nhãn, mã nội bộ, logo. Ở media phải kiểm tra từng ảnh về đúng chữ, không chữ thừa, kiểu/màu/vị trí và tính liên tục. Đối chiếu visual-timing.json với âm thanh thật; thời điểm nội suy chưa phải căn chỉnh từ đã đo. Sửa --scene sẽ áp dụng cho các hình thuộc cảnh đó.

Quy trình B-2 Illustrator mới: Tích hợp trực tiếp qua Persistent Session (`b2_bridge.py` kết nối `session.sock`). Bỏ CLI `gflow` và `gflow_guard.mjs` cũ. Hỗ trợ tự động điều hòa tham chiếu qua 2 slot: Base Scene (`base-scene-selector` cho cảnh kế thừa `based_on`) và Character (`character-selector` cho nhân vật), truyền trực tiếp `mediaId` và `base64` vào React Fiber state, hỗ trợ giữ liên tục visual beats; vẫn phải kiểm tra ảnh thật ở từng tỷ lệ. Mọi hình ảnh sinh ra có nhân vật bắt buộc gắn kết nhân vật đại diện kênh cố định (`assets/characters/channel-mascot/reference-v1.png`, Media ID: `de94a39b-155f-4afe-acbb-d9d4b59ad532`, áo thun xanh biển nhạt `#8CCFE8`); adapters và b2_bridge tự động áp dụng avatar này làm tham chiếu mặc định cho mọi tác vụ sinh ảnh. Ràng buộc giải phẫu CH01 nghiêm ngặt: đúng 1 thân duy nhất, 2 tay & 2 chân que navy tối giản, đầu tròn trắng viền navy đậm, 2 mắt oval đen đặc tối giản, miệng cười tươi lưỡi san hô; tuyệt đối cấm vẽ răng, lông mày, lòng trắng hoạt hình hay vẽ hai thân áo đè lên nhau. Khi Applet gặp UNKNOWN, STABILITY ALERT hoặc timeout, giữ nguyên nhật ký và dùng flow-reconcile với UI proof thật; không xóa localStorage, không tự gửi lại. Đọc docs/flow-queue-operations.md cho hàng đợi mới, link share, cấu hình riêng theo máy và điều kiện bật sản xuất.


Job nghiên cứu: kiểm tra research-visual-review.json tại mốc media; nghe/xem nhịp chữ thực trước duyệt. Nhiều hình không có nghĩa tăng FPS hay tự bật song song.


Cập nhật theo yêu cầu người dùng: mặc định flow_require_ui_evidence=false; không yêu cầu screenshot trước gửi hoặc chứng minh 0 credit cho tạo ảnh. Ghi chi phí là giả định do người dùng chỉ định, không ghi đã xác minh. Giữ kiểm tra model/tham chiếu, nhật ký và đối chiếu timeout sau gửi; không tự mở khóa yêu cầu cũ chưa rõ kết quả.
