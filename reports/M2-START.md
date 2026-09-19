# Hồ sơ chạy thật — m2-flow-001

Điểm chờ: **control revision 1**, kiểm tra cấu hình đã đạt. Chưa duyệt, chưa tạo nội dung, chưa gọi Flow.

- Chủ đề: Góp ý với đồng nghiệp mà không gây căng thẳng.
- Người xem: người đi làm; mục tiêu biết cách nói riêng, nêu việc cụ thể, lắng nghe và thống nhất cách sửa.
- Video dự kiến: tiếng Việt, 6 cảnh, 45–60 giây, dọc 720×1280, 30 fps.
- Ảnh: Google Flow, Nano Banana 2, tỷ lệ 9:16, tối thiểu 720×1280. Giá phải xác minh bằng 0 credit trước tạo.
- Phong cách: minh họa biên tập 2D ấm áp, văn phòng Việt Nam hiện đại, xanh teal/cam nhạt, nhân vật trưởng thành, không chữ trong ảnh.
- Duyệt ảnh: ảnh chuẩn → ba cảnh → sáu cảnh; chỉ chạy tiếp sau phản hồi người dùng cho đúng phiên bản.
- Không tạo video AI, không dịch vụ trả phí, không đăng lên mạng. Audio/render chưa chạy trong M2.

Hồ sơ chi tiết: [yêu cầu](../runs/m2-flow-001/briefs/1.json), [control revision 1](../runs/m2-flow-001/revisions/control/1/output.json).

Phản hồi cần ghi nhận: **“Duyệt control revision 1 của m2-flow-001.”** Nếu cần đổi yêu cầu, nêu thay đổi trước khi chạy.

Sau duyệt cấu hình: dùng adapter Antigravity `scripts/agy_pipeline.py content m2-flow-001`, kiểm tra và gửi bản nội dung cho người dùng duyệt. Sau nội dung mới đến đăng nhập/preflight Flow và điểm A. Không lấy nội dung integration-test làm bản sản xuất đã duyệt.

Lý do cần điểm duyệt này: AGENTS.md yêu cầu “Chỉ gọi approve sau khi người dùng duyệt rõ mã module và revision hiện tại”. Các lời duyệt trước đã thuộc hồ sơ/mốc cũ; không chuyển dấu duyệt sang revision mới. Các công việc cũ giữ nguyên; không đặt lại integrity để vượt kiểm tra.
