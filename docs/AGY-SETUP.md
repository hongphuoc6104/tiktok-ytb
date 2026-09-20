# Antigravity tài khoản

CLI agy dùng đăng nhập tài khoản, không tự chuyển sang API trả phí. Kiểm tra kết nối bằng `.venv/bin/python scripts/agy_pipeline.py smoke`; đây chỉ là kiểm thử kết nối.

Tạo job và chạy qua `pilot.py new JOB --brief FILE --mode review|auto`, rồi `pilot.py run JOB` như docs/workflow.md. Không còn bước duyệt control.
Adapter nội dung nhận brief, sinh JSON, validate và lưu draft/revision. Bộ điều phối quyết định điểm duyệt.
Máy đánh giá ở chế độ auto phải đọc artifact thật; phiên không hỗ trợ nghe/xem media phải báo unsupported. Không coi kết quả smoke là nghiệm thu đánh giá đa phương thức.
Nhật ký ở agent-attempts/ và machine-reviews/. Timeout hoặc lỗi tài khoản giữ job chưa hoàn tất; sửa điều kiện rồi resume, không giả lập kết quả.
