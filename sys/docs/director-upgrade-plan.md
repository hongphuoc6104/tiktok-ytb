# Kế hoạch nâng cấp đạo diễn Video Pilot

Ngày bắt đầu: 24/09/2026. Người dùng cho phép phát triển, tái thiết skill, Rules và những phần hệ thống cần thiết. Căn cứ: [khảo sát sản phẩm và nguồn skill](../reports/director-research-20260924/bao-cao.md).

## Mục tiêu nghiệm thu

Video mới phải được thiết kế như một bài học có câu chuyện: đúng một nghĩa, người học hiểu hành động, có mẫu câu và lượt thực hành, hình–lời–chữ hỗ trợ nhau. Kiểm tra kỹ thuật không được tự coi là đã nghe/xem hoặc đã chứng minh người học nhớ bài.

## Các hạng mục triển khai

| Hạng mục | Thực hiện | Cách xác minh |
|---|---|---|
| Bảo toàn dữ liệu | Chụp bản sao mã/skill đang có; ghi trạng thái thay đổi của người dùng | Không sửa revisions, reviews, ledger, MP4 hoặc baseline job |
| Bốn vai trò đạo diễn | Viết skill kịch bản, hình, dựng, âm thanh; liên kết với vp-* | Kiểm tra cấu trúc skill, tình huống đánh giá và đường dẫn |
| Tiêu chuẩn sáng tạo | Tách ràng buộc khỏi gợi ý; cấu trúc theo mục tiêu học, không bắt mọi tập theo cùng khuôn | Rules, channel brief và tài liệu không mâu thuẫn; brief cũ vẫn giữ nguyên |
| Nạp chỉ dẫn thật | Đưa tài liệu cần thiết vào prompt tại đúng lượt outline/detailed/review | Kiểm thử adapter bảo đảm nội dung nhận được và không gọi công cụ ngoài phạm vi |
| Biên tập phụ đề | Giữ dấu câu với cụm, tránh cue mồ côi, hỗ trợ tối đa hai dòng dễ đọc | Kiểm thử bảo toàn chữ/thời gian và render thử lỗi thật |
| Đạo diễn âm thanh | Giữ I đúng ở nội dung, xử lý phát âm ở TTS; cho phép khoảng chờ luyện nói có khai báo | Kiểm thử request, cache, WAV thử và timeline; nghe thật vẫn là gate |
| Kiểm tra chất lượng | Thêm tiêu chí hook/payoff, nhân quả, học tập, mascot, phụ đề và lượt thực hành | Unsupported vẫn chặn, không có auto-pass từ số đo |
| Chạy thử và bàn giao | Render bản kỹ thuật riêng bằng asset có sẵn; lưu kết quả và giới hạn | Xem khung thật, kiểm thử Python/renderer; không gọi là video sản xuất đã duyệt |

## Phạm vi thiết kế

- Giữ ba phần công khai content → media → video, review/auto, ảnh mascot chuẩn và công cụ đang được cho phép.
- Giữ mẫu cố định trong prompt_templates.py; bổ sung ngữ cảnh đạo diễn tại điểm adapter phù hợp.
- Chỉ dẫn nội bộ mới dùng tiếng Anh; tài liệu và giao tiếp cho người dùng bằng tiếng Việt. Nội dung tiếng Anh hiển thị/đọc giữ đúng ngôn ngữ.
- Thêm trường kế hoạch tùy chọn có kiểm tra, không làm mất khả năng đọc cấu trúc v3 cũ. Không sửa baseline để tiếp tục job cũ.
- Không cài hàng loạt skill bên ngoài; viết skill gọn theo dự án và lưu nguồn tham khảo.
- Không thêm nhà cung cấp, API trả phí, tạo video AI, quyền gửi trùng Flow hoặc tự chứng nhận khả năng nghe/xem.

## Thứ tự và điều kiện hoàn tất

1. Đọc mã, lưu hiện trạng, chạy kiểm thử gốc.
2. Xây hợp đồng đạo diễn, skill và Rules đồng bộ với brief mới.
3. Sửa các lỗi kỹ thuật đã có bằng chứng; nối chỉ dẫn vào bước sinh/duyệt thật.
4. Kiểm thử hồi quy, thử tình huống lỗi và render minh họa riêng.
5. Báo cáo rõ phần đã triển khai, phần đã kiểm chứng và phần phải nghe/xem ở job sản xuất mới.

Không hứa “chuyên nghiệp” chỉ vì thêm skill. Tiêu chí cuối vẫn là artifact thật và phản ứng của người học; chất lượng giọng/diễn xuất và hiệu quả giữ chân không thể suy ra từ tests.

## Trạng thái bàn giao

Đã triển khai các hạng mục phát triển ở trên, 275 kiểm thử đạt và bản MP4 thử render thành công. Xem [báo cáo bàn giao](../reports/director-upgrade-20260924.md) để biết bằng chứng và giới hạn. Nghiệm thu cảm nhận/hiệu quả học của video sản xuất mới vẫn là bước riêng trong các gate hiện hành; chưa được thay bằng kết quả thử kỹ thuật.
