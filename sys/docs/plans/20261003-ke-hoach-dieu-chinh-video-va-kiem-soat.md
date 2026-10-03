# Kế hoạch điều chỉnh hướng video, phân quyền và kiểm soát

- Ngày lưu: 03/10/2026.
- Trạng thái: **ĐÃ LƯU - CHƯA TRIỂN KHAI**.
- Phạm vi: báo cáo hướng video và kế hoạch phân quyền, kiểm soát quá trình chạy, Rules, Skills.
- Job liên quan: `vocab-predator-english-9x16-65s-001`.
- Yêu cầu mới nhất: chỉ lưu Markdown nội bộ để người dùng nhắc lại sau; không sản xuất hoặc sửa hệ thống ngay.

## Hướng dẫn khi người dùng nhắc lại

1. Đọc toàn bộ tài liệu này và yêu cầu mới nhất của người dùng.
2. Nếu người dùng chỉ yêu cầu nhắc lại/xem kế hoạch, tóm tắt hoặc mở tài liệu; giữ trạng thái chưa triển khai.
3. Khi người dùng yêu cầu thực hiện kế hoạch, tiếp tục từ P1 trong phần kế hoạch; đối chiếu quyền hiện hành, đúng checkout, job, revision và request đang dở trước hành động.
4. Dùng người đang xử lý cuộc trò chuyện làm đầu mối. Vai trò dùng tên chức năng; không gắn với tên hệ thống hoặc agent cụ thể. Chỉ giao thêm agents khi có quyền phù hợp.
5. Mọi quyền mới hoặc thay đổi Rules/Skills/mã nguồn trong tài liệu dưới đây là đề xuất. Chỉ áp dụng phần đã được yêu cầu và xác nhận theo quy định có hiệu lực lúc thực hiện.
6. Giữ lịch sử brief/revision/review/journal; không gửi lại request unknown, không tự đổi mode hoặc tạo job mới để né chặn.
7. Mỗi bước có artifact thật phải gửi người dùng xem/nghe; tiếp tục phần độc lập được phép và giữ ba gate content/media/video.
8. Khi triển khai sau này, cập nhật tiến độ trong một mục mới của tài liệu này; giữ nguyên báo cáo nguồn và quyết định lịch sử.

Cụm nhắc gợi ý: **“Thực hiện kế hoạch điều chỉnh video và phân quyền đã lưu ngày 03/10.”** Đây là cách tìm tài liệu, không phải một lệnh tự chạy hoặc quyết định duyệt hiện tại.

## Nội dung lưu để thực hiện sau

## PHẦN A - BÁO CÁO ĐỐI CHIẾU

## Rà soát và lập lại hướng sản xuất — 03/10/2026

### Trạng thái

Người dùng yêu cầu: “hiện tại dự án đang bị lệch khỏi mong muốn của tôi, dừng lại kiểm tra lập plan lại. video gốc và kênh gốc đang hướng đến là gì. liệt kê lại, hình ảnh phong cách tạo ra hiện tại cũng chưa đúng.”

Đã dừng sản xuất. Khi kiểm tra không có tiến trình run/resume hoặc hàng đợi tạo ảnh đang chạy; chỉ có hai dịch vụ kết nối trình duyệt đang chờ. Không gửi thêm yêu cầu Flow, không tổng hợp âm thanh mới, không render. Đây là báo cáo đối chiếu và kế hoạch đề xuất, chưa phải brief mới hay quyết định duyệt.

Job: vocab-predator-english-9x16-65s-001. CLI xác nhận content revision 5 approved, media pending, video pending. Các request Flow unknown giữ nguyên để đối chiếu; không xóa hoặc gửi lại. Lời dẫn và WAV đã duyệt được giữ làm tài liệu đối chiếu.

### Nguồn tham khảo chính xác

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

### Phong cách của mẫu và phần đã lệch

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

### Những chỉ dẫn dễ kéo lệch cần xử lý khi triển khai

- vocab/channel.json đang ghi hand-painted natural-history editorial art và exactly six narrative beats; mặc định speed=1.0 khác lựa chọn giọng 0.92 đã duyệt cho job. Không dùng các giá trị này làm mô tả đúng của mẫu.
- Skill vp-script-director hiện chứa khuôn Micro-Drama 4 hồi, mệnh lệnh nhại và khoảng chờ; vp-visual-director chứa hiệu ứng hài. Chúng không phù hợp yêu cầu hiện tại. Yêu cầu trực tiếp của người dùng được ưu tiên; việc chỉnh tệp skill sẽ phải theo phạm vi phát triển và integrity hợp lệ, không tự sửa trong lượt rà soát.
- docs/channel-mascot-host-template.md còn trỏ brief 5/content 4 và yêu cầu dừng vì watermark; job mới nhất là brief 6/content 5 và đã có lựa chọn tiếp tục Flow. Cần đồng bộ tài liệu tương lai với quyết định thật; không sửa lịch sử.
- Ước lượng 55–90 nhịp hình trong video dài ở khảo sát cũ là ngoại suy từ mẫu frame. Không coi đó là số file ảnh đã đếm hoặc bằng chứng mẫu luôn cắt mỗi 2–4 giây.

### Kế hoạch làm lại

1. Chốt hướng bằng báo cáo này: Short tiếng Anh học một nghĩa từ, trình bày minh họa giải thích theo mẫu; chủ đề có thể là đời sống, tự nhiên hoặc khoa học tùy từ. Giữ Flow và giọng đã duyệt, mascot nhỏ.
2. Lập bảng tham chiếu thị giác từ video mẫu: cảnh kể, cận hành động, bản đồ/sơ đồ, cảnh giải thích; ghi timestamp, nét vẽ, nền, lượng chữ và chức năng hình. Muốn đo khoảng nghỉ phải nghe audio thật; muốn đếm hình phải kiểm toàn timeline.
3. Đề xuất brief sửa phong cách cho chính job này bằng workflow. Giữ predator.n đang được kho giữ chỗ; chưa chọn thêm từ hoặc đổi sang một nhóm từ. Chỉ sửa lời dẫn nếu phản hồi mới yêu cầu; khi sửa phải reject content và nộp revision mới, không ghi đè narration/anchor đã duyệt.
4. Thiết kế storyboard theo các cụm lời thật. Hướng thử gồm: ao/đàn cá đơn giản; cá sấu chuẩn bị lao; cá tránh được; sơ đồ động vật săn → con mồi → thức ăn; cùng câu ví dụ được nhấn phần đang nói; đối chiếu cá sấu/chim săn mồi; kết quay lại dấu hiệu ban đầu. Không đóng cứng số tranh ở bước này.
5. Sau khi sửa content hợp lệ và giải quyết các request cũ bằng bằng chứng thật, tạo bộ ảnh kiểm phong cách nội bộ trong phần media: một cảnh kể, một cảnh hành động, một cảnh sơ đồ/giải thích. Gửi artifact thật ngay khi có; đánh giá toàn bộ trước khi mở rộng. Đây không phải gate công khai mới.
6. Khi nét hình đúng, làm đầy đủ ảnh, giữ nhân vật/ao ở các trạng thái liên quan; canh hình và phụ đề theo WAV 0.92 thực. Nhiều ảnh có chức năng, không chỉ nhiều ảnh độc lập.
7. Review media đầy đủ rồi dựng video theo gate hiện có. Không lấy phê duyệt nội dung cũ làm phê duyệt cho revision đã sửa hoặc cho bộ ảnh mới.

Hiện chỉ hoàn tất rà soát và lập kế hoạch. Chưa thay cấu hình, skill, brief hoặc nội dung đã duyệt; chưa tạo ảnh thử mới. Không cam kết lên xu hướng từ việc bám phong cách, vì chưa có dữ liệu người xem của format mới.

## PHẦN B - KẾ HOẠCH PHÂN QUYỀN VÀ KIỂM SOÁT

## Kế hoạch phân quyền và kiểm soát Video Pilot

Ngày: 03/10/2026. Phiên bản đề xuất: 1.0.

**Trạng thái: CHỈ LẬP KẾ HOẠCH - CHƯA ÁP DỤNG.** Người dùng yêu cầu xuất báo cáo, tạm thời chưa thực hiện, tiếp theo lập kế hoạch về phân quyền, kiểm soát, quá trình chạy, rules và skill. Tài liệu này không cấp quyền mới, không thay rules đang có và không cho phép tiếp tục sản xuất.

### 1. Mục tiêu và phạm vi

Ngăn dự án tự lệch mục tiêu khi chuyển từ yêu cầu trong chat sang brief, lời dẫn, prompt ảnh và video. Thiết lập quyền rõ cho từng hành động, bàn giao đủ bằng chứng, giới hạn sửa và bảo toàn lịch sử. Người đang xử lý cuộc trò chuyện chịu trách nhiệm tổng hợp; các vai trò không gắn với tên một hệ thống hay một agent cố định.

Hướng sáng tạo đề xuất được lấy từ báo cáo rà soát đi kèm: Short 9:16 hoàn toàn tiếng Anh, học một nghĩa từ B1 trở lên bằng tiếng Anh dễ hiểu; kể và minh họa giải thích 2D theo mẫu Ink Explainer; mascot chuẩn nhỏ làm người dẫn; giọng đã duyệt ở tốc độ nói 0.92; ảnh Flow, dựng từ ảnh và âm thanh.

Job đang dừng: vocab-predator-english-9x16-65s-001, review, content revision 5 approved, media pending, video pending. Đây là trạng thái đã kiểm tra trong lượt rà soát trước; lượt xuất tài liệu không chạy lại sản xuất. Những request Flow unknown còn phải đối chiếu. Mọi quyết định tiếp tục phải dựa vào trạng thái thật lúc đó.

### 2. Phân biệt ba loại chỉ dẫn

| Loại | Nguồn đề xuất | Chức năng |
|---|---|---|
| Quyền và giới hạn vận hành | AGENTS.md và rules dùng chung | Ai được làm gì, khi nào dừng, bảo vệ lịch sử và công cụ |
| Hợp đồng của từng video | Brief hiện tại và quyết định theo revision | Từ/nghĩa, mục tiêu, ngôn ngữ, tỷ lệ, giọng, hình, ý bắt buộc |
| Cách thực hiện | Skill và tài liệu thao tác | Viết, tạo, đối chiếu, sửa, dựng và bàn giao |

Ưu tiên chỉ dẫn hệ thống và yêu cầu trực tiếp hiện hành của người dùng. Khi yêu cầu mới đổi hợp đồng đã lưu, ghi nhận yêu cầu rồi sửa bằng workflow trước sản xuất. Skill không được tự cấp quyền, thay công cụ, đổi hướng kênh hoặc đổi brief. Kết quả kỹ thuật đạt không phải quyết định duyệt chất lượng.

Nếu hai tài liệu dự án mâu thuẫn, người điều phối ghi rõ nguồn, phạm vi, hệ quả và đề xuất thống nhất. Chỉ dừng hành động phụ thuộc vào mâu thuẫn đó; công việc đọc và chuẩn bị độc lập vẫn có thể tiếp tục nếu người dùng chưa yêu cầu dừng toàn bộ.

### 3. Ma trận quyền đề xuất

| Vai trò | Được thực hiện | Quyết định/bàn giao bắt buộc | Giới hạn |
|---|---|---|---|
| Người dùng | Chọn hướng, đổi yêu cầu, duyệt/từ chối, yêu cầu dừng | Quyết định thật gắn phần và revision hoặc phạm vi phát triển | Không biến phản hồi chung thành duyệt cho revision chưa tồn tại |
| Người điều phối cuộc trò chuyện | Đọc trạng thái, lập kế hoạch, viết nội dung trực tiếp, chạy CLI hợp lệ, tổng hợp đầu ra | Chọn đúng job/checkout; báo artifact và điểm chặn | Không tự duyệt thay người dùng; không đổi mode hoặc provider |
| Vai trò nội dung | Outline, lời dẫn, cảnh/hình/nhịp, chữ được phép và neo | Draft theo schema; đối chiếu hợp đồng và phản hồi | Chốt lời rồi đặt neo; không tự đổi nghĩa/từ |
| Vai trò hình/âm/biên tập | Chuẩn bị trong phạm vi content đã duyệt; kiểm artifact thật | WAV, ảnh, SRT, nhịp, lỗi cụ thể và evidence | Không sửa narration đã duyệt; không lấy prompt thay kiểm ảnh/âm |
| Vai trò vận hành worker | Thực hiện các mục đã phân công trên session được xác định | Request ID, trạng thái, output, lỗi và danh sách chưa gửi | Không tự chọn profile khác, tự sửa prompt, hoặc retry unknown |
| Vai trò kiểm tra | Kiểm kỹ thuật và xem/nghe theo khả năng thật | Pass/fail/unsupported kèm mục đã kiểm và bằng chứng | Không tự sửa báo cáo lịch sử; tự kiểm không tạo quyền duyệt |
| Vai trò phát triển | Đề xuất/sửa đúng phạm vi người dùng yêu cầu sau khi được phép | Diff cụ thể, ảnh hưởng job, phương án khôi phục | Không sửa mã/config/skill để vượt kiểm tra của job |

Các vai trò trên có thể do cùng người điều phối thực hiện; không mặc định tạo thêm agents. Khi người dùng cho phép giao việc song song, giao theo vai trò và đầu ra. Chỉ một người điều phối ghi quyết định và điều khiển trạng thái job. Mỗi tệp có một người phụ trách tại một thời điểm để tránh ghi đè.

### 4. Phân cấp thay đổi và quyền xác nhận

| Mức | Ví dụ | Đường xử lý đề xuất |
|---|---|---|
| A - đọc/chuẩn bị | Xem trạng thái, đối chiếu mẫu, báo cáo, kế hoạch | Thực hiện trong phạm vi yêu cầu; không tác động sản xuất |
| B - sản xuất đã được phép | Tạo media theo content đã duyệt, thu kết quả cũ, dựng sau media approval | Dùng CLI; giữ revision và journal; gửi artifact ngay khi có |
| C - đổi sản phẩm | Đổi nét hình, narration, số cảnh, ngôn ngữ hoặc yêu cầu mascot | Sửa brief/reject đúng phần; revision mới; duyệt lại phần bị ảnh hưởng |
| D - đổi hệ thống | Sửa bộ điều phối, renderer, config, Rules, skills, cách retry | Trình phạm vi và diff, xử lý integrity theo quyền hiện hành; không trộn vào lượt sản xuất |
| E - cần quyết định riêng | Mua compute, đổi provider, publish, xóa dữ liệu đáng kể | Chỉ thực hiện khi có yêu cầu/xác nhận rõ cho chính hành động |

Không hỏi lại quyền đã được cấp đúng phạm vi. Việc phát sinh lỗi không tự mở rộng phạm vi. Khi đổi yêu cầu, ghi phần bị ảnh hưởng và phần còn hợp lệ; dùng lịch sử workflow thay vì chỉnh revision cũ.

**Mâu thuẫn cần chốt trước phát triển:** AGENTS.md ở worktree đang có ngoại lệ cho người điều phối chạy adopt-code sau xác nhận cụ thể; hướng dẫn người dùng vừa cung cấp lại ghi lệnh này chỉ người dùng chạy. Kế hoạch không tự giải quyết bằng cách chọn bản thuận tiện. Trong thời gian chưa thống nhất, không chạy adopt-code hoặc sửa baseline. Đề xuất tương lai: nếu muốn cho phép agents nhận code sau duyệt, phải ghi rõ quyền đó trong chính sách có hiệu lực, kèm job, danh sách tệp, diff và lưu baseline cũ.

### 5. Quy trình chạy có kiểm soát

#### 5.1 Trước chạy

1. Xác định đúng checkout, job, mode, revision và yêu cầu mới nhất.
2. Đọc INDEX, AGENTS, workflow và skills cần cho phần đang làm; không nạp cả bộ khuôn sáng tạo không liên quan.
3. Đọc status/next; kiểm tra khác biệt implementation nếu có. Ghi các request dở và session sở hữu.
4. Lập phiếu điều hành ngắn: việc đã được phép, đầu ra cần có, giới hạn worker, điểm dừng, phần đang chờ duyệt. Phiếu chỉ tóm tắt và trỏ tới nguồn quyết định; không tạo kịch bản phụ hoặc quyền mới.
5. Tách công việc có thể song song khỏi công việc phụ thuộc. Quyết định sáng tạo và chất lượng phải có trước lựa chọn tốc độ worker.

#### 5.2 Content

Người điều phối viết trực tiếp theo brief. Kiểm câu chuyện, cách dùng từ, chức năng mỗi hình, mascot và chữ. Chốt narration trước coverage/anchor. Kiểm draft, tạo revision, gửi review cho người dùng. Duyệt hợp lệ cho revision hiện tại mới cho phép media. Không ép số nhịp, khoảng nghỉ, giọng hài hay chủ đề tiền sử từ skill cũ.

#### 5.3 Media

Chạy theo cấu hình đã duyệt; chỉ audio và ảnh song song nếu ngoại lệ Colab tương ứng đang hợp lệ. Bộ ảnh kiểm phong cách là bước nội bộ của media, không thêm cổng duyệt công khai. Gửi WAV/ảnh thật ngay khi hoàn tất; tiếp tục phần độc lập. Timeline và phụ đề cuối chờ WAV thật và đủ ảnh. Kiểm mọi ảnh, phát âm, chức năng hình, chữ và vùng an toàn. Review media tập hợp đủ đầu ra và lỗi; chờ quyết định hợp lệ trước video.

#### 5.4 Video và kết thúc

Dựng qua workflow sau media approval. Xem/nghe bản MP4 thật và kiểm nhịp, phụ đề, hình, mở/kết. Gửi video để duyệt. Chỉ xuất thành phẩm và mark nghĩa từ sau quyết định hợp lệ và xác minh file thật. Bản render để review được gọi đúng là bản chờ duyệt, không tuyên bố job hoàn tất.

#### 5.5 Review và auto

- Review: ba cổng content/media/video gắn revision. Lệnh “tiếp tục” chỉ tiếp tục phần đã được phép, không tự tạo quyết định cho artifact chưa hoàn tất.
- Auto: chỉ dùng cho job được tạo đúng mode; máy phải thực sự xem/nghe, có báo cáo và giới hạn vòng sửa. Unsupported giữ needs_attention.
- Mode của job hiện tại giữ nguyên. Kế hoạch này không chuyển job đang chạy sang auto, không tạo job khác để né gate.
- Yêu cầu dừng của người dùng được ưu tiên: ngừng gửi việc mới, giữ kết quả/journal và ghi việc đang chạy để thu hoặc dừng theo khả năng công cụ. Không đóng trình duyệt có request đang gửi chỉ để làm giao diện trống.

### 6. Kiểm soát đồng thời, retry và lỗi

| Tình huống | Hành động được đề xuất | Bằng chứng trước khi tiếp tục |
|---|---|---|
| Chưa gửi, lỗi chuẩn bị | Sửa đúng phạm vi rồi tiếp tục mục chưa gửi | generation_submitted=false và trạng thái not_submitted thực |
| Đã gửi nhưng timeout/unknown | Dừng gửi lại mục đó; đối chiếu request cũ | UI thật, prompt, session/request ID và asset nếu có |
| Đã tạo nhưng chưa thu | Thu lại kết quả cũ; không generation mới | Media ID và đối chiếu đúng mục |
| Tạo lỗi, chưa rõ có output | Ghi lỗi, giữ journal; cần xác minh kết quả | Không dùng giả định để chuyển thành not_submitted |
| Login/CAPTCHA/hạn mức/503 hoặc hết cap | Dừng phạm vi bị chặn và báo nhu cầu can thiệp | Không xoay tài khoản, đổi job hoặc lift-cap để vượt |
| Ảnh sai phong cách/nghĩa | Sửa media có mục tiêu và kế hoạch khác rõ | Artifact trước/sau, image ID, hash, lỗi còn lại |
| Code lệch baseline | integrity-diff, quyết định đúng phạm vi | Quyền hiện hành và diff đã xác nhận |

Hai profile x bốn worker là thử nghiệm đã yêu cầu trước đây, chưa phải mặc định sản xuất đã nghiệm thu. Kế hoạch đề xuất: mỗi profile có hàng đợi và người vận hành duy nhất; mỗi mục có khóa tránh gửi trùng, session sở hữu và trạng thái. Chỉ chạy các worker độc lập khi có quyền hợp lệ. Không tự tăng concurrency, thay model hoặc quay vòng profile khi lỗi. Đợt thử tiếp theo cần đo số request, số output, duplicate=0 và lỗi thực, không chỉ đo tốc độ.

### 7. Tổ chức lại Rules

Đề xuất một nguồn cho mỗi nhóm quy tắc và các tài liệu khác trỏ tới nguồn đó:

| Nơi | Nội dung nên giữ | Nội dung cần tách/loại khỏi phần dùng chung |
|---|---|---|
| AGENTS.md | Quyền, ưu tiên yêu cầu, ba gate, integrity, dừng, bằng chứng, bàn giao | Chi tiết format sáng tạo từng kênh hoặc từng job |
| .agents/rules/production.md | Quy tắc vận hành ngắn, dùng chung và trỏ workflow | Khuôn kể, quota ảnh, yêu cầu tương tác cố định |
| .agents/rules/brand_tolerance.md | Nhận diện mascot và dung sai có thể quan sát | Diễn giải 80/20 thành xác suất/điểm số hoặc miễn kiểm nghĩa |
| docs/workflow.md | Trình tự, revision, reject/resume và ngữ nghĩa mode | Mặc định cũ gắn 9:16 với tiếng Việt |
| Hồ sơ kênh/brief | Hướng tiếng Anh, phong cách 2D, giọng và yêu cầu riêng | Mô tả sai rằng mọi video mẫu có đúng sáu nhịp |

Quy tắc watermark ghi theo quyết định hiện hành và khả năng nguồn thật: Flow có thể bắt buộc watermark nhìn thấy; prompt không bảo đảm tắt. Nếu người dùng yêu cầu ảnh sạch, báo giới hạn trước tạo. Nếu đã chấp nhận Flow với dấu bắt buộc cho một job, lưu đúng phạm vi đó. Không dùng crop/che để tuyên bố ảnh gốc sạch.

### 8. Tổ chức lại Skills

| Skill | Trách nhiệm dự kiến | Điều cần sửa/kiểm |
|---|---|---|
| vp-vocab | Kho từ, nghĩa, lifecycle job | Một nghĩa; không tự đổi từ; mark sau hoàn tất |
| vp-content | Người điều phối viết draft và tạo revision | Quyền trực tiếp viết; dữ liệu theo brief; không cố định chủ đề |
| vp-script-director | Logic lời kể, hook/payoff và cách giải thích | Tách khuôn hài 4 hồi và nhại bắt buộc khỏi format hiện tại |
| vp-visual-director | Hành động, sơ đồ, bố cục, continuity và mascot | Hướng hình theo hồ sơ kênh; hiệu ứng theo khả năng renderer |
| vp-audio-director | Cách đọc và kiểm WAV thật | Giọng/rate theo brief; khoảng luyện chỉ khi brief yêu cầu |
| vp-edit-director | Nhịp hình, cue, đọc chữ và playback | Caption không đồng nghĩa ngắt thở; nội suy không là alignment |
| vp-media | Chạy/thu/sửa media và review chung | Ngoại lệ audio/ảnh song song rõ; unknown không gửi lại |
| vp-video | Dựng, review, xuất | Hỗ trợ ngôn ngữ/tỷ lệ theo brief; loại mặc định 9:16 chỉ Việt |
| vp-clean | Kiểm kê/bảo trì theo yêu cầu | Không xóa bằng chứng hay coi cleanup là hoàn tất |

Không cần tạo thêm skill điều phối chỉ để lặp quy tắc. Các skill giữ hướng dẫn nghề và thao tác, có đầu vào/đầu ra/phạm vi/điểm dừng rõ. Tên vai trò trung lập; người đang chat thực thi trong quyền hiện hành. Tệp hướng dẫn không tự kích hoạt lời gọi dịch vụ viết kịch bản.

### 9. Bàn giao và bằng chứng

Mỗi artifact bàn giao có: job, phần, revision hoặc nhãn tạm, đường dẫn, nguồn tạo, trạng thái kiểm, lỗi còn lại và việc tiếp theo được phép. WAV có duration/rate/định dạng; ảnh có scene/image ID, reference, prompt và trạng thái; SRT có nguồn cue; MP4 có ratio và revision.

Mỗi quyết định có: người/máy quyết định, phần/revision, nguyên văn phản hồi hoặc báo cáo thật, phạm vi còn hiệu lực. Mỗi lỗi có: triệu chứng, evidence, ảnh hưởng, hành động đã thử, nguyên nhân đã xác định hoặc chưa biết, cách xử lý dứt điểm khi có. Không ghi đã nghe/xem nếu công cụ chỉ kiểm metadata.

Thông báo theo sự kiện: kế hoạch bắt đầu; artifact mới; thay đổi hướng; lỗi cần can thiệp; điểm duyệt; hoàn tất. Khi đang làm, cập nhật ngắn trong tối đa khoảng 60 giây nếu có tiến triển. Không lặp các status giống nhau thay cho giải pháp.

### 10. Các giai đoạn triển khai sau này

| Giai đoạn | Đầu ra review được | Điều kiện kết thúc |
|---|---|---|
| P0 - hiện tại | Báo cáo rà soát + kế hoạch này | Đã xuất; sản xuất giữ dừng |
| P1 - thống nhất chính sách | Bản đề xuất quyền/ưu tiên/gate và danh sách mâu thuẫn | Người dùng xác nhận chính sách cần áp dụng |
| P2 - chuẩn hóa tài liệu | Diff AGENTS/rules/workflow/skills trong phạm vi đã yêu cầu | Không còn chỉ dẫn kéo sai hướng; quyền adopt rõ |
| P3 - cập nhật hướng job | Brief/content sửa hợp lệ và hồ sơ mẫu hình | Revision đúng và quyết định duyệt thật |
| P4 - xử lý vận hành | Đối chiếu request cũ; kế hoạch worker hữu hạn | Không còn yêu cầu chưa rõ bị gửi lại |
| P5 - thử media có kiểm soát | WAV/ảnh thật, lỗi và kiểm định hướng | Đúng phong cách/nghĩa/mascot, đủ bằng chứng |
| P6 - tiếp tục sản xuất | Media review, video review, thành phẩm | Đủ ba quyết định hợp lệ và file thật |

Các giai đoạn trên là hạng mục công việc, không phải thêm cổng duyệt sản phẩm. Gate công khai vẫn content/media/video. Phát triển chính sách là phạm vi riêng và cần quyết định cụ thể trước sửa tệp bảo vệ.

### 11. Tiêu chí kiểm chứng khi được yêu cầu triển khai

Đề xuất các tình huống kiểm tra sau này: yêu cầu dừng không gửi mới; content chưa duyệt không tạo media; media chưa duyệt không render; unknown không generation lại; collected chỉ thu kết quả cũ; đổi narration làm mất hiệu lực audio liên quan đúng workflow; code lệch baseline bị chặn; artifact thật được gửi đúng revision; skill cũ không áp khuôn hài; hai worker không ghi cùng mục.

Kiểm kỹ thuật, thử tình huống và nghiệm thu sáng tạo là ba việc khác nhau. Chỉ chạy tests/diễn tập khi được yêu cầu kiểm thử trong giai đoạn triển khai; lượt xuất này không chạy tests và không gửi request sản xuất.

### 12. Những quyết định cần chốt trước áp dụng

1. Phạm vi quyền phát triển và quyền nhận baseline sau khi người dùng duyệt diff.
2. Hướng kể/hình mới và mức giữ nguyên narration/WAV đã duyệt.
3. Ngữ nghĩa “chạy đến kết quả” trong review so với auto cho job tương lai.
4. Phạm vi thử hai profile/bốn worker và điểm dừng từng lỗi.
5. Nguồn thống nhất cho ngôn ngữ/tỷ lệ/giọng/mascot/watermark để các skill không giữ mặc định cũ.

Không có mục nào trong danh sách này được coi là đã duyệt chỉ vì tài liệu được xuất. Bước kế tiếp là người dùng rà kế hoạch; sản xuất và thay đổi hệ thống vẫn dừng.

## Tiến độ triển khai sau khi được yêu cầu

Chưa bắt đầu. Sản xuất giữ dừng theo yêu cầu người dùng.
