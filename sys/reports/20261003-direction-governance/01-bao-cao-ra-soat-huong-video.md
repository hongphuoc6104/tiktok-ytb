# Rà soát và lập lại hướng sản xuất — 03/10/2026

## Trạng thái

Người dùng yêu cầu: “hiện tại dự án đang bị lệch khỏi mong muốn của tôi, dừng lại kiểm tra lập plan lại. video gốc và kênh gốc đang hướng đến là gì. liệt kê lại, hình ảnh phong cách tạo ra hiện tại cũng chưa đúng.”

Đã dừng sản xuất. Khi kiểm tra không có tiến trình run/resume hoặc hàng đợi tạo ảnh đang chạy; chỉ có hai dịch vụ kết nối trình duyệt đang chờ. Không gửi thêm yêu cầu Flow, không tổng hợp âm thanh mới, không render. Đây là báo cáo đối chiếu và kế hoạch đề xuất, chưa phải brief mới hay quyết định duyệt.

Job: vocab-predator-english-9x16-65s-001. CLI xác nhận content revision 5 approved, media pending, video pending. Các request Flow unknown giữ nguyên để đối chiếu; không xóa hoặc gửi lại. Lời dẫn và WAV đã duyệt được giữ làm tài liệu đối chiếu.

## Nguồn tham khảo chính xác

- Kênh của người dùng: https://www.youtube.com/@stickervocabulary/shorts — mục tiêu đã yêu cầu là Short học tiếng Anh hoàn toàn bằng tiếng Anh, từ B1 trở lên, lời nói dễ hiểu, có ngữ cảnh, giải thích nghĩa/cách dùng/phát âm/ngữ pháp.
- Kênh mẫu: Ink Explainer, @Inkexplainer96, https://www.youtube.com/@Inkexplainer96/videos.
- Video mẫu chính: How Did Ancient Humans Survive the Deadliest Predators on Earth?, https://www.youtube.com/watch?v=19Fi4_5ptrc. UI kiểm tra ngày 03/10 ghi 10:26 trên player; thẻ kênh làm tròn 10:27.
- Phạm vi kênh mẫu theo mô tả hiển thị: lịch sử loài người, hành vi và khoa học liên quan đời sống. Trang có 16 video và phần lớn chủ đề đang thấy là đời sống/sinh tồn của người cổ đại. Đây là chủ đề của nguồn tham khảo, không phải yêu cầu chuyển kênh học tiếng Anh thành ngách tiền sử.

Năm video đầu trong tab Popular đã kiểm tra trực tiếp ngày 03/10 (view là số làm tròn trên UI, không phải số chính xác):

| Video | View hiển thị | URL |
|---|---:|---|
| What Did Ancient Humans Actually Do All Day? | 10M | https://www.youtube.com/watch?v=49_Ph2q6uIM |
| What Did Ancient Humans Do When It Rained All Week? | 1.5M | https://www.youtube.com/watch?v=SD7XyG2wd1k |
| Why Are We the Only Human Species Left? What happened to others... | 1.2M | https://www.youtube.com/watch?v=OCr6NteWSQ8 |
| When Did Ancient Humans Start Drinking Alcohol? | 888K | https://www.youtube.com/watch?v=9AFO6MHy8y4 |
| How Did Ancient Humans Travel the World? | 809K | https://www.youtube.com/watch?v=QP1maS6hYn4 |

Khảo sát trước: research/ink-explainer-top-five-analysis-20261002.md. Lượt này xác nhận lại kênh, danh sách Popular, đọc caption video mẫu và xem hai khung đại diện 1:22 và 5:13; không tuyên bố đã xem lại toàn bộ năm video.

## Phong cách của mẫu và phần đã lệch

Quan sát trực tiếp video gốc:

- 1:22: bản đồ Nam Phi, màu phẳng, nét đen vẽ tay, nhãn ngắn, một địa điểm làm trọng tâm. Nền trắng và khoảng trống rõ.
- 5:13: hình lửa, đạo cụ và mũi tên thể hiện quan hệ phát triển; ít chữ, hình dễ nhận ra. Có biểu tượng người dẫn nhỏ ở góc dưới phải trong hai khung đã xem.
- Caption đoạn mở đầu dẫn người xem từ cảm giác an toàn ban đêm hiện tại sang nguy hiểm trong quá khứ, rồi đưa manh mối/bằng chứng và câu hỏi trung tâm. Các câu nối bằng nguyên nhân và hệ quả. Caption tự động không chứng minh vị trí ngắt thở, nhịp im lặng hay số ảnh độc lập.

Đối chiếu dự án:

| Hạng mục | Hiện tại | Hướng sửa đề xuất |
|---|---|---|
| Nét vẽ | Tranh thiên nhiên vẽ tay gần hiện thực, nhiều chất liệu, ánh sáng tối | Minh họa giải thích 2D vẽ tay, viền đậm, màu phẳng, nền sáng, đạo cụ rõ |
| Mức đầu tư | Đang thể hiện qua chi tiết tranh | Thể hiện qua storyboard, hành động, sơ đồ và thay đổi có ý nghĩa theo lời |
| Cách kể | Hook nhỏ về gợn nước, sau đó các đoạn định nghĩa/phát âm/chủ ngữ/động từ/số nhiều | Giữ một câu hỏi dẫn chuyện; gắn phần học vào tình huống đang diễn ra, tránh cảm giác lần lượt đọc mục giáo án |
| Template | Đóng cứng đúng sáu nhịp và 16–22 tranh | Số cảnh/ảnh là quyết định cho từng kịch bản, không phải đặc điểm đã chứng minh của mẫu |
| Mascot | Thêm mô tả vào prompt mới; 10 ảnh cũ chưa có mascot | Mascot chuẩn nhỏ trong mọi khung theo yêu cầu mới; cử chỉ dẫn mắt, đứng cạnh phần minh họa khi giải thích |
| Liên tục hình | Nhiều ảnh based_on=null dù mô tả muốn quay lại đúng ao mở đầu | Khóa nền/bố cục khi là cùng tình huống; đổi độc lập khi đổi nội dung hoặc góc thực sự |

Ảnh thật SC02_I1 tại flow/attempts/e0e1cc4ab35fd85b732fe374a5d37b3f1bdd227983dafdaa2e4389987f0fe33a/result.jpg cho thấy cá sấu chìm trong nước tối với nhiều chất liệu và cây cỏ; không có mascot. Cú lao hụt như mô tả kịch bản cũng chưa được thể hiện rõ trong ảnh này. Ảnh chứng minh phong cách hiện tại khác mẫu, không dùng như một ảnh đạt chất lượng.

Báo cáo khảo sát trước đã nhận ra mẫu là hoạt họa 2D viền đậm, nền phẳng/pastel; phần đề xuất lại chủ động đổi thành tranh tư liệu cao cấp. Đó là chỗ diễn giải sai yêu cầu “có đầu tư”.

## Những chỉ dẫn dễ kéo lệch cần xử lý khi triển khai

- vocab/channel.json đang ghi hand-painted natural-history editorial art và exactly six narrative beats; mặc định speed=1.0 khác lựa chọn giọng 0.92 đã duyệt cho job. Không dùng các giá trị này làm mô tả đúng của mẫu.
- Skill vp-script-director hiện chứa khuôn Micro-Drama 4 hồi, mệnh lệnh nhại và khoảng chờ; vp-visual-director chứa hiệu ứng hài. Chúng không phù hợp yêu cầu hiện tại. Yêu cầu trực tiếp của người dùng được ưu tiên; việc chỉnh tệp skill sẽ phải theo phạm vi phát triển và integrity hợp lệ, không tự sửa trong lượt rà soát.
- docs/channel-mascot-host-template.md còn trỏ brief 5/content 4 và yêu cầu dừng vì watermark; job mới nhất là brief 6/content 5 và đã có lựa chọn tiếp tục Flow. Cần đồng bộ tài liệu tương lai với quyết định thật; không sửa lịch sử.
- Ước lượng 55–90 nhịp hình trong video dài ở khảo sát cũ là ngoại suy từ mẫu frame. Không coi đó là số file ảnh đã đếm hoặc bằng chứng mẫu luôn cắt mỗi 2–4 giây.

## Kế hoạch làm lại

1. Chốt hướng bằng báo cáo này: Short tiếng Anh học một nghĩa từ, trình bày minh họa giải thích theo mẫu; chủ đề có thể là đời sống, tự nhiên hoặc khoa học tùy từ. Giữ Flow và giọng đã duyệt, mascot nhỏ.
2. Lập bảng tham chiếu thị giác từ video mẫu: cảnh kể, cận hành động, bản đồ/sơ đồ, cảnh giải thích; ghi timestamp, nét vẽ, nền, lượng chữ và chức năng hình. Muốn đo khoảng nghỉ phải nghe audio thật; muốn đếm hình phải kiểm toàn timeline.
3. Đề xuất brief sửa phong cách cho chính job này bằng workflow. Giữ predator.n đang được kho giữ chỗ; chưa chọn thêm từ hoặc đổi sang một nhóm từ. Chỉ sửa lời dẫn nếu phản hồi mới yêu cầu; khi sửa phải reject content và nộp revision mới, không ghi đè narration/anchor đã duyệt.
4. Thiết kế storyboard theo các cụm lời thật. Hướng thử gồm: ao/đàn cá đơn giản; cá sấu chuẩn bị lao; cá tránh được; sơ đồ động vật săn → con mồi → thức ăn; cùng câu ví dụ được nhấn phần đang nói; đối chiếu cá sấu/chim săn mồi; kết quay lại dấu hiệu ban đầu. Không đóng cứng số tranh ở bước này.
5. Sau khi sửa content hợp lệ và giải quyết các request cũ bằng bằng chứng thật, tạo bộ ảnh kiểm phong cách nội bộ trong phần media: một cảnh kể, một cảnh hành động, một cảnh sơ đồ/giải thích. Gửi artifact thật ngay khi có; đánh giá toàn bộ trước khi mở rộng. Đây không phải gate công khai mới.
6. Khi nét hình đúng, làm đầy đủ ảnh, giữ nhân vật/ao ở các trạng thái liên quan; canh hình và phụ đề theo WAV 0.92 thực. Nhiều ảnh có chức năng, không chỉ nhiều ảnh độc lập.
7. Review media đầy đủ rồi dựng video theo gate hiện có. Không lấy phê duyệt nội dung cũ làm phê duyệt cho revision đã sửa hoặc cho bộ ảnh mới.

Hiện chỉ hoàn tất rà soát và lập kế hoạch. Chưa thay cấu hình, skill, brief hoặc nội dung đã duyệt; chưa tạo ảnh thử mới. Không cam kết lên xu hướng từ việc bám phong cách, vì chưa có dữ liệu người xem của format mới.
