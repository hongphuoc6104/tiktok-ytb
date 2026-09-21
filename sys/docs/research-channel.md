# Kênh nghiên cứu

## Phạm vi
Video giải thích nghiên cứu và hướng dẫn phương pháp, công cụ, quy trình nghiên cứu.
Không gán cứng ngành, đề tài, độ dài hoặc số cảnh. Xác định trong brief theo nhu cầu.
Hai giọng Việt/Anh là phương tiện truyền đạt, không phải mục tiêu học ngoại ngữ.
Giữ người que chuẩn CH01 áo xanh biển nhạt làm người dẫn chuyện.
Avatar kênh: assets/channel-avatars/nghien-cuu-v1.png; avatar không thay ảnh tham chiếu nhân vật.

## Hai loại nội dung
- Giải thích nghiên cứu: câu hỏi, bối cảnh, phương pháp, kết quả, ý nghĩa và giới hạn.
  Không biến tương quan thành nhân quả; phân biệt kết quả của tác giả với diễn giải.
- Hướng dẫn nghiên cứu: mục tiêu, điều kiện đầu vào, các bước thực hiện, ví dụ,
  đầu ra mong đợi, cách kiểm tra và lỗi thường gặp. Không giả đã thực hiện thí nghiệm.

## Brief và duyệt
Chủ đề, đối tượng, kiến thức sẵn có và thành công mong muốn phải rõ trong brief.
Khi giải thích nghiên cứu hoặc nêu dữ kiện, đặt facts_required=true, cung cấp
sources với dữ kiện đã đối chiếu tài liệu gốc trước khi viết lời dẫn. Liên kết claims
với nguồn và câu trích. Không bịa nghiên cứu, số liệu, trích dẫn hoặc DOI.
Nếu thiếu tài liệu để hỗ trợ phát biểu, ghi rõ thiếu và giữ nội dung chưa đạt.

Content: người/máy kiểm tra đúng nghĩa nguồn, đủ bối cảnh và giới hạn, không thổi phồng.
Media: kiểm tra người que nhất quán; chữ, sơ đồ và số liệu đúng với kịch bản;
minh họa tổng hợp không được trình bày như ảnh hoặc kết quả thực nghiệm thật.
Video: kiểm tra mạch giải thích, nhịp xem, độ rõ và cách trình bày nguồn.
Đây là tiêu chí đánh giá nội dung; schema chỉ kiểm tra cấu trúc, không tự chứng minh
độ tin cậy khoa học. Giữ nguyên review/auto và các gate hiện hành.

## Sản xuất
Tạo job mới bằng brief v3, không sửa integrity hoặc dữ liệu đã duyệt của job cũ.
Theo docs/workflow.md và các skill vp-*. Không tạo nội dung nghiên cứu mẫu bằng
nguồn giả. Chưa có video nghiên cứu thật được nghiệm thu cho nhánh này.

Giới hạn kế thừa: 9:16 đọc Việt, 16:9 đọc Anh; dual tạo hai bản. Muốn bản ngang
tiếng Việt phải phát triển lựa chọn ngôn ngữ độc lập trước, không chỉ sửa brief.
Cải tiến pipeline dùng chung tách thành commit riêng để đưa về master; tài liệu
và avatar của kênh này không merge ngược vào nền chung.

## Kho nội dung và ngân sách hình

Dùng research/bank.py cho job mới; xem ../research/README.md. Kho 1.000 ý tưởng chia 40 nhóm, không phải 1.000 kịch bản đã kiểm chứng. Mặc định 90–180 giây; 18–24 hình và 24–36 nhịp mục tiêu. Chỉ đọc mục đã chọn; không nạp toàn kho vào context.
