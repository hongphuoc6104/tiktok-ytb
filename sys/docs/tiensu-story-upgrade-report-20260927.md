# Nâng cấp vp-tiensu — kết quả kiểm tra ngày 27/09/2026

## Đã triển khai trong worktree riêng

- Nâng skill `vp-tiensu`, hướng dẫn viết kịch bản dài và hướng dẫn hình/nhân vật để video mới kể một câu chuyện riêng, không bắt mascot xuyên kênh hay số chương cố định. Bảng đối chiếu 5 video nhiều lượt xem và 2 đối chứng ở `ink-explainer-story-patterns-20260927.md` nêu rõ giới hạn suy luận từ lượt xem.
- Kho tiensu tạo brief **360–900 giây**, `character_mode: story_cast`, 16:9 giọng Việt, không `clips`, khoảng 9 cảnh theo mục tiêu giữa 630 giây. Brief cũ thiếu `character_mode` giữ đường canonical; không sửa revision hay integrity của job đã lưu.
- Bộ chia nội dung ước lượng nhiều ảnh still hơn cho `story_cast` (khoảng 75% số visual beats); mỗi ảnh/beat vẫn phải có chức năng, không biến tỷ lệ này thành số lượng cứng. Đường FlowPool và B-2 không gắn mascot mặc định vào cảnh mới không người; ảnh có một nhân vật riêng dùng reference và media ID của chính job. Ảnh dựa trên ảnh trước vẫn giữ Base reference; journal unknown không được gửi lại.
- `doodle.build_ai` nhận thư mục ảnh và thư mục xuất tùy chọn, bỏ câu mô tả gắn cứng với Mơ. Đây là bộ dựng dùng cho phép thử và bản đã có; sản phẩm mới đi qua cổng Pilot content → media → video.
- Bộ dựng ảnh tĩnh giờ đọc `BURN_SUBTITLES` từ script; mẫu 15 giây bật phụ đề trong khung hình để kiểm khả năng đọc, bên cạnh file SRT.
- FlowPool nhận `reference_mode: none` cho ảnh `story_cast` độc lập và `base_only` cho ảnh kế thừa bối cảnh mà không có nhân vật. Khi tài khoản có bản VP Stickman Lab đã mở trong dự án, các ảnh này dùng B-2; `base_only` gắn ảnh cảnh trước vào ô Base. Giao diện Agent của Flow được đóng trước khi chọn Image/model; đường B-2 không gửi lại journal `unknown`.

## Kiểm chứng

| Kiểm tra | Kết quả |
|---|---|
| Skill validator, `git diff --check` | Đạt |
| Bộ kiểm tra Python | 410 đạt, 2 skip ở lượt nền; sau thay đổi FlowPool, 75/75 kiểm tra liên quan đạt |
| Kiểm tra FlowPool/B-2 | 24/24 kiểm tra Flow Node và 10/10 kiểm tra queue B-2 đạt, gồm cảnh không tham chiếu, Base scene và giữ chặn gửi lại unknown |
| Brief mới qua schema/contract | Đạt: 360–900 s, 9 cảnh, `story_cast`, không clips |
| Render tổng hợp 900 s, 16:9, 12 cảnh/180 beat, 15 fps nguồn | MP4 dài 900,053 s; render 1071,572 s (1,191× thời lượng), tổng gồm chuẩn bị 1082,3 s |
| WAV cuối cho mẫu 15 s | PCM 48 kHz, dài 15,390 s, giải mã sạch; người dùng đã nghe và xác nhận đạt |
| Kiểm tra sau sửa tùy chọn phụ đề | Skill valid; 9/9 kiểm tra đóng gói đạt; mã Python biên dịch được |
| 5 ảnh Flow mới | 3 ảnh từ Flow thường và 2 ảnh cùng một lô VP Stickman Lab trên Profile 14; đã xem từng ảnh, không có mascot. Lô B-2 trả media ID `72e9da54-f495-43cc-9341-47b2f4c36e09` và `f9af67d1-600d-4cfc-8063-900050f5bba5`. Đường Flow thường tải được file nhưng chưa trả media ID. |
| MP4 thử | 15,445 s, 1920×1080, H.264/AAC, 5 nhịp ảnh, phụ đề trong hình và SRT; dài hơn WAV 0,055 s. Kiểm tra 2 khung hình/giây và `blackdetect` không thấy khung đen; phụ đề đọc được trong bản xem 360 px. Người dùng xác nhận nghe/xem đạt. |

Video tổng hợp 900 giây vẫn chỉ là dữ liệu kiểm tra renderer. Video thử cuối nằm ở `sys/scratch/story-smoke-15/deliverables/story-smoke-15/story-smoke-15.mp4`; WAV, SRT, contact sheet, manifest ảnh và nhật ký yêu cầu nằm cùng thư mục scratch. Dự án Flow riêng cho hàng đợi B-2 có ID `0fb6366e-83b8-4a4c-9a30-6f39bc550c30`. Dữ kiện Mezhyrich được viết ở mức giả thuyết nơi trú theo nguồn `https://pmc.ncbi.nlm.nih.gov/articles/PMC12639289/`. Mẫu này không phải quyết định duyệt content/media/video của một job Pilot.

## Giới hạn vận hành

Phép thử xác nhận đường ảnh `story_cast` không nhân vật và batch B-2 trên Flow thật, nhưng chưa thay thế nghiệm thu một job Pilot dài với ba gate. Nhánh `base_only` đã qua kiểm thử giao diện giả lập, chưa có lượt Flow thật dùng ảnh Base kế thừa. Profile 10 vẫn báo `usage limit` dù còn 1.026 credit (`FLOW-013`); một yêu cầu khác trên Profile 102 còn `unknown` sau timeout và UI báo hoạt động bất thường (`FLOW-015`), nên không gửi lại. Profile 13 dừng trước submit vì nút settings; Profile 14 hoạt động sau khi đóng Agent mode (`FLOW-005`). Ba job `tiensu-001/002/003` vẫn giữ nguyên revision và integrity; không dùng mẫu này để hợp thức hóa quyết định duyệt của chúng. Media ID của ba ảnh Flow thường vẫn là `null` (`FLOW-016`), cần kiểm tra trước khi dùng chúng làm tham chiếu tài khoản trong sản xuất.
