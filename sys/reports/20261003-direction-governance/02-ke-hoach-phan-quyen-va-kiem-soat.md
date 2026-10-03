# Kế hoạch phân quyền và kiểm soát Video Pilot

Ngày: 03/10/2026. Phiên bản đề xuất: 1.0.

**Trạng thái: CHỈ LẬP KẾ HOẠCH - CHƯA ÁP DỤNG.** Người dùng yêu cầu xuất báo cáo, tạm thời chưa thực hiện, tiếp theo lập kế hoạch về phân quyền, kiểm soát, quá trình chạy, rules và skill. Tài liệu này không cấp quyền mới, không thay rules đang có và không cho phép tiếp tục sản xuất.

## 1. Mục tiêu và phạm vi

Ngăn dự án tự lệch mục tiêu khi chuyển từ yêu cầu trong chat sang brief, lời dẫn, prompt ảnh và video. Thiết lập quyền rõ cho từng hành động, bàn giao đủ bằng chứng, giới hạn sửa và bảo toàn lịch sử. Người đang xử lý cuộc trò chuyện chịu trách nhiệm tổng hợp; các vai trò không gắn với tên một hệ thống hay một agent cố định.

Hướng sáng tạo đề xuất được lấy từ báo cáo rà soát đi kèm: Short 9:16 hoàn toàn tiếng Anh, học một nghĩa từ B1 trở lên bằng tiếng Anh dễ hiểu; kể và minh họa giải thích 2D theo mẫu Ink Explainer; mascot chuẩn nhỏ làm người dẫn; giọng đã duyệt ở tốc độ nói 0.92; ảnh Flow, dựng từ ảnh và âm thanh.

Job đang dừng: vocab-predator-english-9x16-65s-001, review, content revision 5 approved, media pending, video pending. Đây là trạng thái đã kiểm tra trong lượt rà soát trước; lượt xuất tài liệu không chạy lại sản xuất. Những request Flow unknown còn phải đối chiếu. Mọi quyết định tiếp tục phải dựa vào trạng thái thật lúc đó.

## 2. Phân biệt ba loại chỉ dẫn

| Loại | Nguồn đề xuất | Chức năng |
|---|---|---|
| Quyền và giới hạn vận hành | AGENTS.md và rules dùng chung | Ai được làm gì, khi nào dừng, bảo vệ lịch sử và công cụ |
| Hợp đồng của từng video | Brief hiện tại và quyết định theo revision | Từ/nghĩa, mục tiêu, ngôn ngữ, tỷ lệ, giọng, hình, ý bắt buộc |
| Cách thực hiện | Skill và tài liệu thao tác | Viết, tạo, đối chiếu, sửa, dựng và bàn giao |

Ưu tiên chỉ dẫn hệ thống và yêu cầu trực tiếp hiện hành của người dùng. Khi yêu cầu mới đổi hợp đồng đã lưu, ghi nhận yêu cầu rồi sửa bằng workflow trước sản xuất. Skill không được tự cấp quyền, thay công cụ, đổi hướng kênh hoặc đổi brief. Kết quả kỹ thuật đạt không phải quyết định duyệt chất lượng.

Nếu hai tài liệu dự án mâu thuẫn, người điều phối ghi rõ nguồn, phạm vi, hệ quả và đề xuất thống nhất. Chỉ dừng hành động phụ thuộc vào mâu thuẫn đó; công việc đọc và chuẩn bị độc lập vẫn có thể tiếp tục nếu người dùng chưa yêu cầu dừng toàn bộ.

## 3. Ma trận quyền đề xuất

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

## 4. Phân cấp thay đổi và quyền xác nhận

| Mức | Ví dụ | Đường xử lý đề xuất |
|---|---|---|
| A - đọc/chuẩn bị | Xem trạng thái, đối chiếu mẫu, báo cáo, kế hoạch | Thực hiện trong phạm vi yêu cầu; không tác động sản xuất |
| B - sản xuất đã được phép | Tạo media theo content đã duyệt, thu kết quả cũ, dựng sau media approval | Dùng CLI; giữ revision và journal; gửi artifact ngay khi có |
| C - đổi sản phẩm | Đổi nét hình, narration, số cảnh, ngôn ngữ hoặc yêu cầu mascot | Sửa brief/reject đúng phần; revision mới; duyệt lại phần bị ảnh hưởng |
| D - đổi hệ thống | Sửa bộ điều phối, renderer, config, Rules, skills, cách retry | Trình phạm vi và diff, xử lý integrity theo quyền hiện hành; không trộn vào lượt sản xuất |
| E - cần quyết định riêng | Mua compute, đổi provider, publish, xóa dữ liệu đáng kể | Chỉ thực hiện khi có yêu cầu/xác nhận rõ cho chính hành động |

Không hỏi lại quyền đã được cấp đúng phạm vi. Việc phát sinh lỗi không tự mở rộng phạm vi. Khi đổi yêu cầu, ghi phần bị ảnh hưởng và phần còn hợp lệ; dùng lịch sử workflow thay vì chỉnh revision cũ.

**Mâu thuẫn cần chốt trước phát triển:** AGENTS.md ở worktree đang có ngoại lệ cho người điều phối chạy adopt-code sau xác nhận cụ thể; hướng dẫn người dùng vừa cung cấp lại ghi lệnh này chỉ người dùng chạy. Kế hoạch không tự giải quyết bằng cách chọn bản thuận tiện. Trong thời gian chưa thống nhất, không chạy adopt-code hoặc sửa baseline. Đề xuất tương lai: nếu muốn cho phép agents nhận code sau duyệt, phải ghi rõ quyền đó trong chính sách có hiệu lực, kèm job, danh sách tệp, diff và lưu baseline cũ.

## 5. Quy trình chạy có kiểm soát

### 5.1 Trước chạy

1. Xác định đúng checkout, job, mode, revision và yêu cầu mới nhất.
2. Đọc INDEX, AGENTS, workflow và skills cần cho phần đang làm; không nạp cả bộ khuôn sáng tạo không liên quan.
3. Đọc status/next; kiểm tra khác biệt implementation nếu có. Ghi các request dở và session sở hữu.
4. Lập phiếu điều hành ngắn: việc đã được phép, đầu ra cần có, giới hạn worker, điểm dừng, phần đang chờ duyệt. Phiếu chỉ tóm tắt và trỏ tới nguồn quyết định; không tạo kịch bản phụ hoặc quyền mới.
5. Tách công việc có thể song song khỏi công việc phụ thuộc. Quyết định sáng tạo và chất lượng phải có trước lựa chọn tốc độ worker.

### 5.2 Content

Người điều phối viết trực tiếp theo brief. Kiểm câu chuyện, cách dùng từ, chức năng mỗi hình, mascot và chữ. Chốt narration trước coverage/anchor. Kiểm draft, tạo revision, gửi review cho người dùng. Duyệt hợp lệ cho revision hiện tại mới cho phép media. Không ép số nhịp, khoảng nghỉ, giọng hài hay chủ đề tiền sử từ skill cũ.

### 5.3 Media

Chạy theo cấu hình đã duyệt; chỉ audio và ảnh song song nếu ngoại lệ Colab tương ứng đang hợp lệ. Bộ ảnh kiểm phong cách là bước nội bộ của media, không thêm cổng duyệt công khai. Gửi WAV/ảnh thật ngay khi hoàn tất; tiếp tục phần độc lập. Timeline và phụ đề cuối chờ WAV thật và đủ ảnh. Kiểm mọi ảnh, phát âm, chức năng hình, chữ và vùng an toàn. Review media tập hợp đủ đầu ra và lỗi; chờ quyết định hợp lệ trước video.

### 5.4 Video và kết thúc

Dựng qua workflow sau media approval. Xem/nghe bản MP4 thật và kiểm nhịp, phụ đề, hình, mở/kết. Gửi video để duyệt. Chỉ xuất thành phẩm và mark nghĩa từ sau quyết định hợp lệ và xác minh file thật. Bản render để review được gọi đúng là bản chờ duyệt, không tuyên bố job hoàn tất.

### 5.5 Review và auto

- Review: ba cổng content/media/video gắn revision. Lệnh “tiếp tục” chỉ tiếp tục phần đã được phép, không tự tạo quyết định cho artifact chưa hoàn tất.
- Auto: chỉ dùng cho job được tạo đúng mode; máy phải thực sự xem/nghe, có báo cáo và giới hạn vòng sửa. Unsupported giữ needs_attention.
- Mode của job hiện tại giữ nguyên. Kế hoạch này không chuyển job đang chạy sang auto, không tạo job khác để né gate.
- Yêu cầu dừng của người dùng được ưu tiên: ngừng gửi việc mới, giữ kết quả/journal và ghi việc đang chạy để thu hoặc dừng theo khả năng công cụ. Không đóng trình duyệt có request đang gửi chỉ để làm giao diện trống.

## 6. Kiểm soát đồng thời, retry và lỗi

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

## 7. Tổ chức lại Rules

Đề xuất một nguồn cho mỗi nhóm quy tắc và các tài liệu khác trỏ tới nguồn đó:

| Nơi | Nội dung nên giữ | Nội dung cần tách/loại khỏi phần dùng chung |
|---|---|---|
| AGENTS.md | Quyền, ưu tiên yêu cầu, ba gate, integrity, dừng, bằng chứng, bàn giao | Chi tiết format sáng tạo từng kênh hoặc từng job |
| .agents/rules/production.md | Quy tắc vận hành ngắn, dùng chung và trỏ workflow | Khuôn kể, quota ảnh, yêu cầu tương tác cố định |
| .agents/rules/brand_tolerance.md | Nhận diện mascot và dung sai có thể quan sát | Diễn giải 80/20 thành xác suất/điểm số hoặc miễn kiểm nghĩa |
| docs/workflow.md | Trình tự, revision, reject/resume và ngữ nghĩa mode | Mặc định cũ gắn 9:16 với tiếng Việt |
| Hồ sơ kênh/brief | Hướng tiếng Anh, phong cách 2D, giọng và yêu cầu riêng | Mô tả sai rằng mọi video mẫu có đúng sáu nhịp |

Quy tắc watermark ghi theo quyết định hiện hành và khả năng nguồn thật: Flow có thể bắt buộc watermark nhìn thấy; prompt không bảo đảm tắt. Nếu người dùng yêu cầu ảnh sạch, báo giới hạn trước tạo. Nếu đã chấp nhận Flow với dấu bắt buộc cho một job, lưu đúng phạm vi đó. Không dùng crop/che để tuyên bố ảnh gốc sạch.

## 8. Tổ chức lại Skills

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

## 9. Bàn giao và bằng chứng

Mỗi artifact bàn giao có: job, phần, revision hoặc nhãn tạm, đường dẫn, nguồn tạo, trạng thái kiểm, lỗi còn lại và việc tiếp theo được phép. WAV có duration/rate/định dạng; ảnh có scene/image ID, reference, prompt và trạng thái; SRT có nguồn cue; MP4 có ratio và revision.

Mỗi quyết định có: người/máy quyết định, phần/revision, nguyên văn phản hồi hoặc báo cáo thật, phạm vi còn hiệu lực. Mỗi lỗi có: triệu chứng, evidence, ảnh hưởng, hành động đã thử, nguyên nhân đã xác định hoặc chưa biết, cách xử lý dứt điểm khi có. Không ghi đã nghe/xem nếu công cụ chỉ kiểm metadata.

Thông báo theo sự kiện: kế hoạch bắt đầu; artifact mới; thay đổi hướng; lỗi cần can thiệp; điểm duyệt; hoàn tất. Khi đang làm, cập nhật ngắn trong tối đa khoảng 60 giây nếu có tiến triển. Không lặp các status giống nhau thay cho giải pháp.

## 10. Các giai đoạn triển khai sau này

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

## 11. Tiêu chí kiểm chứng khi được yêu cầu triển khai

Đề xuất các tình huống kiểm tra sau này: yêu cầu dừng không gửi mới; content chưa duyệt không tạo media; media chưa duyệt không render; unknown không generation lại; collected chỉ thu kết quả cũ; đổi narration làm mất hiệu lực audio liên quan đúng workflow; code lệch baseline bị chặn; artifact thật được gửi đúng revision; skill cũ không áp khuôn hài; hai worker không ghi cùng mục.

Kiểm kỹ thuật, thử tình huống và nghiệm thu sáng tạo là ba việc khác nhau. Chỉ chạy tests/diễn tập khi được yêu cầu kiểm thử trong giai đoạn triển khai; lượt xuất này không chạy tests và không gửi request sản xuất.

## 12. Những quyết định cần chốt trước áp dụng

1. Phạm vi quyền phát triển và quyền nhận baseline sau khi người dùng duyệt diff.
2. Hướng kể/hình mới và mức giữ nguyên narration/WAV đã duyệt.
3. Ngữ nghĩa “chạy đến kết quả” trong review so với auto cho job tương lai.
4. Phạm vi thử hai profile/bốn worker và điểm dừng từng lỗi.
5. Nguồn thống nhất cho ngôn ngữ/tỷ lệ/giọng/mascot/watermark để các skill không giữ mặc định cũ.

Không có mục nào trong danh sách này được coi là đã duyệt chỉ vì tài liệu được xuất. Bước kế tiếp là người dùng rà kế hoạch; sản xuất và thay đổi hệ thống vẫn dừng.
