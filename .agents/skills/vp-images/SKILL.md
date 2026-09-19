---
name: vp-images
description: Xử lý module Hình ảnh trong dự án Video Pilot dùng pilot.py; áp dụng khi chạy hoặc sửa module này.
---
# Hình ảnh
Đọc AGENTS.md. Chạy `python3 pilot.py next <job>`.
Đọc `schemas/images.json` và `docs/contracts.md` trước khi tạo đầu ra.
Chạy `python3 pilot.py run <job> images` rồi `validate <job> images`.
Riêng control: dùng new để tạo hồ sơ; run control không cấp quyền duyệt.
Riêng content: sửa runs/<job>/draft/content.json rồi run; không sửa revisions.
Riêng images: cần bằng chứng giao diện 0 credit bằng flow-preflight; nếu lỗi ambiguous dùng flow-reconcile, không retry tạo.
Đọc artifact và báo revision cho người dùng. Dừng ở awaiting_review.
Sau phản hồi rõ ràng, gọi approve kèm --revision và --note nguyên văn.
Reject ghi lý do. Resume đọc trạng thái đã lưu, không khởi tạo lại công việc.
