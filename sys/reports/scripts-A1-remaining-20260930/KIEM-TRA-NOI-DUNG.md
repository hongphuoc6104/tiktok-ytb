# Kiểm tra lô A1 còn lại

Phạm vi: 331 bài mới số 441–771, cộng chín mục cùng nghĩa dẫn về bài đã có. Không sửa các kịch bản hoặc file hệ thống được bảo vệ.

## Lời dẫn và hoạt động học

- Mỗi bài giữ cách dùng được chọn trong brief từ kho, với mục tiêu ứng dụng và tình huống cụ thể.
- Hai câu mẫu chính được kiểm tra có từ/cụm hoặc dạng biến đổi đúng mục; giữ đúng I trong tiếng Anh.
- Năm, sáu hoặc bảy cảnh theo kế hoạch từng mục. Không rút bài về cùng năm mục để đủ khuôn.
- Lượt thực hành ở cảnh áp chót, có mẫu/gợi ý, khoảng chờ cuối cảnh và phản hồi ở cảnh sau.
- Lời dẫn viết trước neo; coverage và anchor đều trích chuỗi thật có trong lời dẫn. Không sửa lời dẫn sau khi nộp revision.
- Chữ minh họa đối chiếu với phần được nói hoặc từ mục tiêu; phần tiếng Anh được giữ nguyên chính tả.

## Kế hoạch hình

CH01 dùng mascot chuẩn. Mỗi cảnh có hành động/vật/quan hệ cần thấy. Những cặp hình trước/sau giữ góc và bối cảnh bằng based_on; hình là kế hoạch, chưa phải ảnh đã sinh. Những vai giới tính như Minh/Lan được ghi trong hồ sơ; bài enough có bốn người để chứng minh một người thiếu ghế rồi tất cả có chỗ.

## Thời lượng và giới hạn lời dẫn

Điểm ước tính: 170 bài ngắn 51,2–63,5 giây; 132 bài trung bình 70,6–87,6 giây; 29 bài dài 90,4–101,5 giây. Tổng gồm khoảng chờ thực hành. Đây chưa phải thời lượng WAV, và khoảng bất định trong bản duyệt có thể rộng hơn brief.

Có 12 cảnh vượt 256 ký tự. Theo hướng dẫn lời dẫn hiện tại, 256 ký tự là ngưỡng xử lý tổng hợp, không phải giới hạn sáng tác; không cắt ý chỉ để nằm dưới số này. Khi sản xuất vẫn phải nghe WAV thật, đo thời gian và kiểm phụ đề.

## Căn cứ và giới hạn kết luận

- `content-audit.json`: đối chiếu nguồn/bản nháp, brief hiện hành, mã nghĩa giữ chỗ, neo, coverage, chữ và lượt thực hành.
- `operations-local/*check-draft.json`: kết quả CLI kiểm cấu trúc từng bài.
- `export-verification.json`: đối chiếu bản đọc với revision lưu và checksum bản sao.
- `final-verification.json`: trạng thái cuối từ CLI; chỉ có sau khi đủ lô được nộp và kiểm.
- Kiểm tra kỹ thuật không thay cho người dùng duyệt chất lượng. Không ghi duyệt hộ hoặc suy ra hiệu quả giữ chân/học khi chưa có người xem thật.

## Kết quả cuối

Đã kiểm trạng thái hiện tại đủ 331 hồ sơ qua CLI: review mode, content revision 1 awaiting_review, media/video pending. Cả 331 check-draft đều passed; integrity-diff không đổi file được bảo vệ. Bản đọc giữ nguyên mọi lời dẫn trong revision; JSON xuất giữ nguyên byte/checksum revision gốc. Không còn lỗi kỹ thuật ngăn duyệt content; chất lượng vẫn chờ phản hồi thật của người dùng.
