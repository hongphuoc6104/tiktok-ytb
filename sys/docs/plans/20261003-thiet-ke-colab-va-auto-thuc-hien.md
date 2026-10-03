# Thiết kế 0.3 — Colab xử lý, máy quản lý, auto thực hiện

Ngày: 03/10/2026. **Bản thiết kế hiện hành cho phần đang thảo luận. Chưa triển khai runtime.**

**Giao diện thử nghiệm đã được người dùng chốt:** xem [quyết định nguyên văn](20261003-chot-giao-dien-thu-nghiem.md). Giữ bố cục bản đầu để triển khai; nâng cấp sau. Chưa nghiệm thu chức năng runtime.

Bổ sung phần tài khoản: [ngân sách giờ/ảnh và auth — bản 0.4](20261003-thiet-ke-ngan-sach-tai-khoan.md). Mốc 6/5/12/24 giờ và 100–200 ảnh là ngân sách nội bộ, không là quota Google bảo đảm. Không triển khai rotation để vượt quota hoặc né bot.

## 1. Đính chính yêu cầu

Người dùng đã sửa rõ hai điểm:

> “tiết kiệm tài nguyên cho máy là phần xử lý, tránh xử lý nặng ở máy đưa toàn bộ lên colab. máy chỉ lưu trữ một số phần quan trọng và các phần cần quản lý thôi. không cần máy kiểm duyệt gì cả auto là tự lên kế hoạch thực hiện từng bước cho đến khi ra kết quả không gọi kiểm duyệt.”

Theo yêu cầu này, phần tiết kiệm không còn được thiết kế chủ yếu bằng giảm số worker/concurrency local. Mục tiêu là **đưa các công việc xử lý nặng sang Colab**. Auto không gọi máy kiểm duyệt, ở máy hay Colab; auto lập kế hoạch và thực hiện các bước đến sản phẩm cuối.

Bản này thay phần phân chia xử lý và định nghĩa auto trong [thiết kế 0.2](20261003-thiet-ke-quan-ly-tai-khoan-phien-va-auto.md). Giữ các yêu cầu đã chốt về trang local, account/profile, lựa chọn nhiều theo phiên, revision, request/session ownership và dừng/thu kết quả. Không biến bản thiết kế thành sửa mode/baseline của job cũ.

## 2. Phân chia công việc

| Việc | Nơi thực hiện theo thiết kế | Máy giữ gì |
|---|---|---|
| Giao diện quản lý | Máy | Trang local, lựa chọn phiên và thông báo |
| Đăng nhập/chọn tài khoản | Máy, qua cơ chế browser/CLI tương ứng | Profile/token tại kho local hiện có, không đưa secret lên giao diện hay gói job |
| Agent nhận yêu cầu và lập kế hoạch | Phiên chat/điều phối hiện có; không chạy model nặng local | Yêu cầu, brief/content, kế hoạch và phạm vi được giao |
| TTS và xử lý audio | Colab | WAV cần nghe/lưu và metadata; model/cache nặng ở Colab |
| Đo/ghép/chuẩn hoá audio | Colab | Kết quả và số đo cần quản lý |
| Xử lý ảnh cho video, thumbnail, resize/crop theo kế hoạch | Colab | Bản xem nhỏ và ảnh quan trọng; không render xử lý hàng loạt local |
| Tạo ảnh | Google Flow trên dịch vụ cloud | Profile/session liên kết, request ID, reference và kết quả cần lưu |
| Chuẩn bị timeline/phụ đề/props/gói dựng | Colab | Bản kế hoạch và SRT/metadata cần quản lý |
| Render/encode/ghép MP4 và bản xem | Colab | MP4 thành phẩm và manifest |
| Kiểm tra kỹ thuật thực thi | Chủ yếu Colab | File đủ, duration/streams/hash và lỗi; không có quality reviewer |
| Machine review chất lượng | Không gọi trong auto thực hiện | Không đòi report quality pass để chạy tiếp |

Tạo ảnh Flow vốn chạy ở dịch vụ Google; không thay provider tạo ảnh thành mô hình khác trên Colab. Phần điều khiển Flow qua profile local hiện có chỉ phục vụ đăng nhập/gửi/thu; phải tối giản, không kéo render/TTS về máy. Nếu yêu cầu chuyển cả browser automation Flow sang Colab sau này, đó là hạng mục riêng cần thiết kế đăng nhập/session; không tự chuyển cookie/token browser lên VM.

Colab có CPU/GPU và môi trường dựng riêng; chuyển sang Colab không đồng nghĩa mọi xử lý đều tự tăng tốc bằng T4. Cần kiểm cài Chrome/FFmpeg/Node/Remotion và chạy thử render thật trước khi cam kết thời gian hoặc khả năng tương thích.

## 3. Auto thực hiện

Tên hiển thị đề xuất: **Auto thực hiện**. Không dùng “Auto kiểm duyệt”.

1. Nhận yêu cầu và chọn preset/tài khoản của phiên.
2. Lập kế hoạch đầu ra, các bước/phụ thuộc và ngân sách đợt chạy.
3. Soạn brief/content đúng nguồn kho và hợp đồng; chốt lời rồi neo như quy tắc nghề nghiệp.
4. Chạy audio Colab và ảnh Flow trong phạm vi độc lập được thiết kế.
5. Thu hoặc liên kết kết quả, xử lý media/timeline/phụ đề trên Colab.
6. Render/encode trên Colab.
7. Thu sản phẩm cuối và dữ liệu quan trọng về máy, báo hoàn tất thực hiện.

Trong luồng này không gọi bộ đánh giá chất lượng và không tự tạo quyết định machine approved. Không dừng chờ duyệt content/media/video trong chế độ auto thực hiện mới nếu nhiệm vụ và hợp đồng đã đủ phạm vi; ba phần vẫn là tổ chức sản phẩm. Nếu cần quyết định làm thay đổi mục tiêu, thiếu tài khoản/tài nguyên hoặc có chặn thực thi thật thì báo đúng lý do.

Mọi bước có artifact cập nhật ngay: content, WAV, ảnh, SRT, video. Người dùng có thể xem/nghe và yêu cầu sửa; đây không phải điểm chờ quality gate tự động. Khi sửa, xác định impact và tạo phiên bản mới có lịch sử, không ghi đè artifact đã lưu.

“Hoàn tất thực hiện” dựa vào kế hoạch đã chạy xong và đủ file đầu ra hợp lệ kỹ thuật, không được diễn đạt như đã được người/máy nghiệm thu chất lượng. Người dùng có thể kiểm sản phẩm sau, nhưng không bắt thêm một quyết định duyệt chỉ để luồng auto xuất kết quả.

## 4. Kiểm tra kỹ thuật khác gọi kiểm duyệt

Các kiểm tra cần cho thực thi vẫn có: dữ liệu đầu vào hợp lệ, đúng request/account/session, kết quả đúng job, có đủ file, đọc được WAV/MP4, đủ audio/video streams, thời lượng từ file thật, không missing assets, upload/download hoàn tất, không gửi trùng. Xử lý nặng cho các kiểm tra này đưa lên Colab; máy chỉ kiểm metadata/hash cần để nhận/lưu.

Không đánh giá câu chuyện, giọng tự nhiên, hiệu quả học, mascot giống hay hình đẹp bằng reviewer trong auto. Không thêm quality pass vào điều kiện chuyển bước. Không ghi chất lượng đã đạt khi chỉ kiểm file.

## 5. Tám tab sau điều chỉnh

| Tab | Nội dung |
|---|---|
| Tổng quan & phiên | Preset, account được chọn/ưu tiên, Auto thực hiện, mục tiêu phiên và bàn giao |
| Tài khoản | Toàn bộ profile/hồ sơ phát hiện; Flow/Colab login và khả dụng, chọn nhiều/chuyển nhanh |
| Công việc & hàng đợi | Kế hoạch, bước hiện tại, dependencies, requests, dừng/tiếp tục và kết quả |
| Kịch bản & cảnh | Brief/lời thoại/cảnh/ảnh/beat/chữ và lịch sử sửa; liên kết sản phẩm |
| Media | WAV, ảnh, phụ đề và trạng thái xử lý remote; nghe/xem theo nhu cầu |
| Video & thành phẩm | Render remote, MP4/bản xuất/tỷ lệ/phiên bản và tải về |
| Colab & xử lý | Account/VM/session, môi trường, tác vụ audio/media/render, chuyển dữ liệu, lỗi, thu/giải phóng phiên riêng |
| Cấu hình & nhật ký | Nguồn prompt/Rules/Skills, vai trò, preset, dữ liệu giữ local, issues và lịch sử |

Bỏ tab “Kiểm duyệt” khỏi thiết kế hiện hành. Trong giai đoạn chuyển đổi, lịch sử duyệt của job cũ vẫn được xem như hồ sơ lịch sử ở chi tiết job; không xoá hay diễn giải lại.

## 6. Tài khoản và dữ liệu

Giữ inventory đã kiểm của bản 0.2: 15 profile Chrome chính; 5 account Colab lưu thông tin đăng nhập, preferred account-02. Tổng 34 thư mục profile tại 12 root được phát hiện không tương đương 34 tài khoản duy nhất. Live login/Flow/T4 chưa được kiểm.

Chọn nhiều tạo pool cho phiên. Request đang chạy/unknown giữ account/session gốc; chuyển nhanh chỉ đổi việc mới chưa gửi sau kiểm nguồn/reference. Lỗi quota/503/CAPTCHA/login không tự xoay tài khoản. Colab worker không nhận toàn bộ browser profiles hay account store local.

Máy giữ mặc định: cấu hình máy/preset, thông tin auth trong kho local, brief/content/kế hoạch, revision/index, request journal, references quan trọng, logs/bằng chứng, bản xem cần thiết và MP4 cuối. Model weights, dependencies xử lý nặng, cache render và file trung gian tái tạo đặt ở Colab. Những file đang là evidence, request dở hoặc cần phục hồi vẫn bảo toàn; không xóa hàng loạt nhân danh offload.

Cần bảng chính sách lưu trữ phân loại required/local-preview/remote-intermediate/evidence, thời điểm thu về và điều kiện dọn. Kết quả quan trọng phải được thu bền vững trước giải phóng phiên Colab chuyên dụng. Không chỉ lưu đường dẫn VM rồi gọi là đã lưu thành phẩm trên máy.

## 7. Nền code hiện có và phần phải phát triển

Rà soát tĩnh trong lượt đính chính:

- `sys/colab_bridge` hiện là đường TTS, đã có account/session/request ID, upload/collect và output.zip. Chưa là worker toàn pipeline.
- `sys/renderer/render.mjs` hiện bundle/openBrowser/renderStill/renderMedia bằng Node/Chrome local; chuyển render remote là thay đổi thật, không chỉ đổi nhãn trên dashboard.
- Timeline/subtitles và xử lý media cần lập inventory caller để chuyển nơi thực hiện; giữ schema và anchor dữ liệu hợp lệ.
- `workflow.py` hiện định nghĩa auto là machine review và mode immutable. Không thể dùng thẳng `--mode auto` hiện tại để thực hiện yêu cầu mới mà vẫn gọi đó là không review.

Cần thiết kế execution strategy mới và đồng bộ AGENTS/Rules/Skills/runtime/CLI trước áp dụng. Có thể giữ engine review cũ để đọc/chạy job lịch sử theo hợp đồng cũ, nhưng không gọi reviewer trong auto thực hiện mới. Tên/schema/CLI đích sẽ chốt khi triển khai; không tự sửa workflow.json, baseline hay tạo job thay cùng nội dung để né trạng thái cũ.

## 8. Thứ tự ưu tiên đã sửa

1. Chốt ma trận local/Colab/Flow và định nghĩa Auto thực hiện; cập nhật chính sách/skills đúng nghiệp vụ sau khi bắt đầu triển khai.
2. Setup account/profile + chọn preset phiên + Colab environment readiness.
3. Worker Colab nhận gói job, chạy audio/media/render, lưu manifest và checkpoint kết quả; thu theo request/session, không submit trùng.
4. Điều phối Auto thực hiện: kế hoạch bước/phụ thuộc, chạy/thu/tiếp tục, không gọi quality reviewer.
5. Trang trực quan nối account/job/cảnh/media/video/Colab, artifact updates và dừng/tiếp tục thật.
6. Nghiệm thu chuyển xử lý: chứng minh không chạy TTS/render/media processing nặng local, đủ file cuối, phục hồi gián đoạn và bảo toàn dữ liệu.
7. Sau đó mới thử hướng video mới.

## 9. Tiêu chí nghiệm thu mới

- Chạy một job Auto thực hiện không gọi reviewer service/module; không giả machine approval.
- TTS, media processing, timeline/subtitles/render/encode chạy ở Colab theo manifest.
- Local không cài/chạy model xử lý nặng trong preset remote, không chạy Remotion/FFmpeg render như fallback ngầm.
- File sản phẩm và từng trạng thái được cập nhật; không chờ quality pass hay click duyệt từng phần trong auto mới.
- Dừng có hiệu lực trước submit mới, giữ inflight/checkpoint; resume thu phần đã chạy, không tạo lại.
- Account/session và reference khớp request; quota/503/CAPTCHA/unknown vẫn xử lý đúng giới hạn.
- Máy có đủ metadata, evidence và sản phẩm quan trọng sau thu; không phụ thuộc file Colab chưa tải về để tuyên bố đã lưu.
- Job cũ giữ lịch sử/mode/baseline, có kế hoạch chuyển đổi được yêu cầu và xác nhận nếu cần.

## 10. Tiến độ

Đã sửa bản thiết kế, hướng tab và định nghĩa auto sau phản hồi người dùng. Chưa sửa code/Rules/Skills, đổi mode job, cấp Colab, upload/auth hoặc chạy sản xuất. Bản mô phỏng là thiết kế, không là kết quả remote đã kiểm.
