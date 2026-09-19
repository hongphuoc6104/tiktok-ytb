# Chạy nghiệm thu M1 trong Antigravity

Mở thư mục `outputs/video-pilot` làm workspace, không mở dự án VideoShotCut. Đã cài agy và xác minh kết nối tài khoản cùng khả năng tiếp tục hội thoại qua CLI. Có thể dùng adapter trong AGY-SETUP.md; các bước dưới đây dành cho nghiệm thu trực tiếp bằng IDE. Không cần cài thêm dịch vụ trả phí.

## Lượt thứ nhất

Dùng yêu cầu sau trong Antigravity (các tên file tính từ workspace video-pilot):

> Thực hiện goal M1 trong docs/M1-GOAL.md, dùng skill .agents/skills/vp-content/SKILL.md. Đọc Rules và báo VP-RULES-1. Chạy doctor, status và next cho m1-acceptance-001 bằng .venv/bin/python pilot.py. Nếu control chờ duyệt, hiển thị config và revision rồi dừng để tôi duyệt. Khi control đã duyệt, đọc brief hiện tại và tự viết draft/content.json từ yêu cầu, không lấy examples/m1/content.json làm kết quả của bạn. Kiểm tra nháp, sửa lỗi rồi run và validate content. Bàn giao review.md và revision để tôi duyệt. Chỉ làm M1, không tạo ảnh, âm thanh hoặc video; không sửa Rules, hợp đồng hoặc kiểm tra. Lưu nhận xét về nội dung còn cần tôi xác nhận, không tự duyệt.

## Lượt thứ hai — cuộc trò chuyện mới

> Đọc Rules và skill vp-content. Tiếp tục công việc m1-acceptance-001 bằng status và next. Cho tôi biết module, trạng thái, revision và bước được phép làm; không tạo lại công việc, không tự ghi duyệt. Nếu nội dung đang chờ duyệt, mở đúng review.md để tôi xem.

## Bằng chứng nghiệm thu

Giữ bản xuất cuộc trò chuyện hoặc ảnh chụp cho cả hai lượt vào `runs/m1-acceptance-001/evidence/`, ghi thời điểm và phiên bản ứng dụng. Đối chiếu với nhật ký events trong bộ điều phối. Sau khi người dùng duyệt rõ module/revision, ghi phản hồi nguyên văn qua approve. Chỉ cập nhật checklist goal khi có bằng chứng tương ứng.

Kết quả mẫu do Codex chuẩn bị nằm trong examples/m1; đó là mẫu hợp đồng và dữ liệu test, không phải kết quả Antigravity đã tạo.
