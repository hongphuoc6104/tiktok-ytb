# Nâng cấp vp-tiensu — kết quả kiểm tra ngày 27/09/2026

## Đã triển khai trong worktree riêng

- Nâng skill `vp-tiensu`, hướng dẫn viết kịch bản dài và hướng dẫn hình/nhân vật để video mới kể một câu chuyện riêng, không bắt mascot xuyên kênh hay số chương cố định. Bảng đối chiếu 5 video nhiều lượt xem và 2 đối chứng ở `ink-explainer-story-patterns-20260927.md` nêu rõ giới hạn suy luận từ lượt xem.
- Kho tiensu tạo brief **360–900 giây**, `character_mode: story_cast`, 16:9 giọng Việt, không `clips`, khoảng 9 cảnh theo mục tiêu giữa 630 giây. Brief cũ thiếu `character_mode` giữ đường canonical; không sửa revision hay integrity của job đã lưu.
- Bộ chia nội dung ước lượng nhiều ảnh still hơn cho `story_cast` (khoảng 75% số visual beats); mỗi ảnh/beat vẫn phải có chức năng, không biến tỷ lệ này thành số lượng cứng. Đường FlowPool và B-2 không gắn mascot mặc định vào cảnh mới không người; ảnh có một nhân vật riêng dùng reference và media ID của chính job. Ảnh dựa trên ảnh trước vẫn giữ Base reference; journal unknown không được gửi lại.
- `doodle.build_ai` nhận thư mục ảnh và thư mục xuất tùy chọn, bỏ câu mô tả gắn cứng với Mơ. Đây là bộ dựng dùng cho phép thử và bản đã có; sản phẩm mới đi qua cổng Pilot content → media → video.

## Kiểm chứng

| Kiểm tra | Kết quả |
|---|---|
| Skill validator, `git diff --check` | Đạt |
| Bộ kiểm tra Python | 410 đạt, 2 skip (lượt trước chỉnh sửa cuối cùng); các kiểm tra liên quan sau chỉnh sửa đều đạt |
| Kiểm tra queue B-2 | 9/9 đạt, gồm cảnh không tham chiếu nhân vật và giữ chặn gửi lại unknown |
| Brief mới qua schema/contract | Đạt: 360–900 s, 9 cảnh, `story_cast`, không clips |
| Render tổng hợp 900 s, 16:9, 12 cảnh/180 beat, 15 fps nguồn | MP4 dài 900,053 s; render 1071,572 s (1,191× thời lượng), tổng gồm chuẩn bị 1082,3 s |
| WAV mới cho mẫu 15 s | PCM 48 kHz, dài 14,020 s, giải mã sạch |
| 3–5 ảnh Flow mới và MP4 mẫu | **Chưa đạt**: Flow từ chối ảnh đầu tiên vì `usage limit`, xác nhận không tính phí; không gửi ảnh tiếp hoặc thay nguồn ảnh |

Video tổng hợp 900 giây là dữ liệu kiểm tra renderer, không phải sản phẩm. WAV 14 giây nằm ở `sys/scratch/story-smoke-15/audio/narration.wav`; chưa có MP4 mẫu. Yêu cầu đầu tiên và lỗi hạn mức nằm trong dự án Flow `6ab8f469-4d15-41a7-9182-b82d15080bd9`. Xem `sys/logs/issues/FLOW-013.md` trong checkout chính để biết điều kiện thử lại. Không coi bài kiểm tra này là quyết định duyệt media/video.

## Giới hạn vận hành

Ảnh `story_cast` chưa được nghiệm thu trực tiếp qua B-2/FlowPool trên một job Pilot thật vì Flow đang báo hạn mức. Các kiểm tra offline xác nhận dữ liệu đi đúng đường, nhưng UI thật có thể thay đổi. Ba job `tiensu-001/002/003` giữ nguyên trạng thái trong checkout chính; bản mã worktree này chưa được hợp nhất vào đó. Khi Flow khả dụng, tạo 3–5 ảnh mới cho mẫu đã chuẩn bị, xem từng ảnh, dựng MP4 14–16 s và xem/nghe toàn bộ trước khi coi phép thử đạt. Không dùng ảnh cũ để giả bài thử mới.
