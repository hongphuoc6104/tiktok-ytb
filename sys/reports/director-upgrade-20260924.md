# Bàn giao nâng cấp hệ thống đạo diễn — 24/09/2026

## Kết quả triển khai

Đã xây bốn skill riêng cho Video Pilot và nối vào bộ sinh nội dung/bộ duyệt thực tế. Bốn vai trò giữ nguyên quy trình content → media → video, không tạo thêm điểm xin duyệt.

| Vai trò | File |
|---|---|
| Kịch bản và học tập | [vp-script-director](../../.agents/skills/vp-script-director/SKILL.md) |
| Hình ảnh và mascot | [vp-visual-director](../../.agents/skills/vp-visual-director/SKILL.md) |
| Biên tập và phụ đề | [vp-edit-director](../../.agents/skills/vp-edit-director/SKILL.md) |
| Giọng và âm thanh | [vp-audio-director](../../.agents/skills/vp-audio-director/SKILL.md) |

Đã đồng bộ AGENTS.md, Rules, GEMINI.md, INDEX.md, các skill điều phối và mặc định brief mới. Có [kế hoạch](../docs/director-upgrade-plan.md), [hướng dẫn vận hành](../docs/director-system.md), [khảo sát với 47 đường dẫn tham khảo](director-research-20260924/bao-cao.md). Nhiều đường dẫn thuộc cùng nhà xuất bản/repository, không xem là 47 nguồn độc lập.

## Vấn đề → thay đổi → bằng chứng

| Vấn đề khảo sát | Thay đổi đã làm | Cách kiểm chứng và giới hạn |
|---|---|---|
| Hook và bài học rập khuôn | Skill kịch bản cùng mặc định theo mục tiêu học; không ép năm mục giảng | Bộ sinh nhận hướng dẫn thật; chất lượng hook mới cần đánh giá kịch bản/khán giả |
| Ba ví dụ chưa có quan hệ | Yêu cầu nguyên nhân–hành động–hậu quả hoặc đối chiếu có mục đích | Bộ duyệt có story_and_learning_design; chưa tuyên bố video cũ đã được viết lại |
| Nhiều ảnh nhưng chưa đúng nhịp | Mỗi beat có chức năng, giữ thời gian đọc và thực hành | Audit chỉ xác minh timeline; xem/nghe vẫn bắt buộc |
| Phụ đề chỉ một dấu ngoặc kép | Thay bộ chia cue, giữ dấu câu theo token/cụm | Khung thật tại giây 31,35 của bản dựng thử không còn dấu đứng riêng |
| Chữ phụ đề nhỏ | Hai dòng, cỡ chữ lớn hơn, bố cục chung giữa renderer và preflight | 26 cue trong bản thử đạt phép kiểm tra hình học; đã xem khung render |
| Hình chỉ gợi chủ đề, chưa chứng minh nghĩa | Skill hình yêu cầu hành động/biến đổi, tách cảnh hậu quả | Tiêu chí mới phải đối chiếu ảnh thật, không suy từ prompt |
| Mascot đổi mắt/lông mày/thân | Skill và review yêu cầu so sánh từng ảnh với ảnh chuẩn và cả dãy | Không tự gắn nhãn matched; bản thử dùng ảnh cũ nên vẫn giữ các sai khác cũ |
| Hứa khẩu hình nhưng ảnh tĩnh | Quy định khả năng minh họa phải khớp lời hướng dẫn | Bộ viết/duyệt nhận tiêu chí; không mở tạo video AI |
| Thiếu thời gian người học đáp lại | Trường audio_direction có learner_pause_seconds cuối cảnh, riêng vi/en | Kiểm thử WAV xác nhận yên lặng thật; content_end tránh kéo trễ cue/neo trước khoảng chờ |
| Ai lọt vào bài học | Giữ I ở dữ liệu, thay phát âm chỉ trong đầu vào VieNeu; đổi phiên bản cache | Kiểm thử giữ nguyên văn narration/caption và đầu vào tổng hợp riêng |
| Chỉ dẫn liên kết nhưng không tới lượt chỉ-trả-JSON | Nạp trực tiếp tài liệu đạo diễn/sư phạm tại outline/detailed/review | Kiểm thử adapter và kiểm tra định tuyến; chưa chạy một phiên sinh mới qua tài khoản ngoài |
| Đánh đồng tests với chất lượng | Review tách bằng chứng kịch bản/ảnh/WAV/MP4, unsupported vẫn chặn | Kiểm thử gate và protocol; không ghi integration-check giả |

## Bản dựng kiểm tra

Bản thử dùng lại hình/âm thanh đã có của get-up-009, chỉ kiểm tra thay đổi biên tập và renderer. Thời lượng MP4 đo được: **46,656 giây**, 1080×1920, H.264/AAC. Không thay thế video đã duyệt, không đánh dấu kho từ và không gọi đây là video mới hoàn chỉnh.

- [MP4 thử kỹ thuật](/home/hongphuoc6104/Desktop/pipelineFlow/sys/scratch/director-upgrade-20260924/preview/video.mp4)
- [So sánh phụ đề trước/sau](/home/hongphuoc6104/Desktop/pipelineFlow/sys/scratch/director-upgrade-20260924/caption-comparison.jpg)
- [Audit bản thử](../maintenance/director-upgrade-20260924/editorial-audit-preview.json)

Audit không có lỗi kỹ thuật, còn hai cảnh báo thời gian ngắn ở các cue “Chuông reo,” và “Ủa khoan!”. Không tự kéo thời gian gây lệch lời; các cảnh báo này cần cân nhắc khi biên tập kịch bản mới. Đã kiểm tra khung hình, chưa nghe/xem liên tục để duyệt chất lượng video.

## Kiểm thử

**275 kiểm thử đạt:** 209 hệ thống Python, 28 kho từ và 38 JavaScript. Không có kiểm thử lỗi trong ba lượt cuối. Đây là kết quả kỹ thuật, không phải nghiệm thu giọng/ảnh/video sản xuất.

Kết quả hồi quy cuối được lưu tại [tests-final.log](../maintenance/director-upgrade-20260924/tests-final.log). Bộ kho từ tại [vocab-tests.log](../maintenance/director-upgrade-20260924/vocab-tests.log), bộ JavaScript tại [node-tests.log](../maintenance/director-upgrade-20260924/node-tests.log).

Kiểm thử gốc có hai lỗi trước nâng cấp: phép thử hết hạn preflight giả định chỉ một yêu cầu đang chạy và phép thử thứ tự ảnh đòi tổng thứ tự tuần tự. Đã làm rõ fixture tuần tự ở phép thử thứ nhất; phép thử thứ hai vẫn kiểm tra thứ tự theo tỷ lệ, chuỗi phụ thuộc và đúng ảnh tham chiếu, đồng thời cho phép các cảnh độc lập chạy xen kẽ. Không đổi cấu hình hay bỏ cổng Flow để làm tests đạt.

Skill validator đạt cho bốn skill mới và các skill điều phối được chỉnh; các liên kết tài liệu mới đã được kiểm tra. Mẫu cố định prompt_templates.py được giữ nguyên.

## Bảo toàn và giới hạn

Bản sao trước nâng cấp ở `sys/maintenance/director-upgrade-20260924/before/`, kèm checksum và trạng thái Git đầu lượt. Kho làm việc đã có thay đổi của người dùng; không reset, không commit gộp các thay đổi đó.

Không sửa revisions/reviews/MP4 cũ, ledger, baseline integrity; không gọi Flow hoặc API trả phí. Bốn skill được viết riêng, các nguồn ngoài chỉ dùng khảo sát. Các job cũ có thể bị chặn vì implementation thay đổi; tiếp tục thử sản xuất bằng job mới theo kho từ, không sửa baseline để mở lại.

Chỉ `learner_pause_seconds` là điều khiển âm thanh mới được thực thi. `intent` và `pronunciation_notes` là chỉ dẫn đánh giá/retake; chưa phải điều khiển cảm xúc TTS. Nhạc nền/SFX không tự được thêm bởi skill. Phát âm, cảm xúc, độ khớp mascot trong ảnh mới và hiệu quả học/giữ chân phải được kiểm chứng bằng artifact và người học thật.

## Bước áp dụng tiếp theo

Tạo một job mới bằng vocab/bank.py theo mode được chọn, dùng bốn vai trò trong các gate hiện có. Kiểm tra kịch bản có quan hệ nhân quả, tạo WAV và nghe lượt thực hành trước ảnh, rồi xem/nghe toàn bộ MP4. Đây là bước nghiệm thu sản phẩm mới; bộ kiểm thử phần mềm không thay được bước này.
