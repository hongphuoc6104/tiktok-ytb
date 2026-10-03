# Ví dụ giao diện, dừng/tiếp tục và quản lý prompt

Ngày 03/10/2026. Bổ sung cho [kế hoạch nền vận hành](20261003-ke-hoach-nen-tang-van-hanh.md).

**Bản thiết kế để thảo luận. Chưa là giao diện vận hành thật.** Người dùng yêu cầu mô tả rõ từng bước, trang giới thiệu, dừng/tiếp tục và bổ sung/quản lý prompt. Chưa chốt lựa chọn giao diện từ câu hỏi trước.

## 1. Trang giới thiệu và luồng vào

Trang giới thiệu có mô tả ngắn: dự án tạo video từ ảnh và âm thanh; ba phần content/media/video; ai quyết định trong review/auto. Có ba lối vào:

- **Thiết lập máy:** tải/clone mới; kiểm đúng môi trường, tài nguyên và login.
- **Tiếp tục công việc:** chọn job/checkout, thấy bản bàn giao và đối chiếu trạng thái thật.
- **Chuẩn bị video:** chỉ khi nền đủ cho phần cần làm và nhiệm vụ đã được yêu cầu; không tự submit.

Trang giới thiệu không tự run/resume. Với chat mới, agent dùng cùng thông tin tiếp quản ở trang công việc, không chỉ dựa vào tóm tắt của phiên trước.

## 2. Ví dụ từng bước

Video giả định dạy nghĩa động vật săn mồi của “predator”, tiếng Anh, 9:16. Mọi revision/trạng thái trong ví dụ là minh họa, không phải trạng thái job predator thật.

| Bước | Người dùng thấy | Agent làm | Điểm dừng/tiếp tục |
|---|---|---|---|
| Giới thiệu | Chọn setup hay tiếp quản | Đọc điểm vào/quyền/checkout | Không sinh nội dung tự động |
| Kiểm máy | Từng thành phần có/thiếu/chưa thử | Lập plan theo preset, cài phạm vi được yêu cầu | Thiếu quyền/tài nguyên thì báo đúng phần |
| Login | Flow/Colab cần người dùng | Chuẩn bị thao tác; kiểm sau login thật | Người dùng tự OAuth/OTP/CAPTCHA; login không chứng minh có T4 |
| Yêu cầu video | Nghĩa từ kho, ngôn ngữ, tỷ lệ, giọng, hướng hình | Tổng hợp hợp đồng qua workflow | Đổi yêu cầu phải có revision hợp lệ; không thêm gate sản xuất |
| Nội dung | Kịch bản, storyboard, chữ, review và revision | Viết/kiểm/nộp content | Review dừng ở content; “tiếp tục” chung không thành duyệt |
| Media | WAV xuất sớm, ảnh lần lượt, request đang chờ, phụ đề | Tạo/thu đúng revision/session; kiểm artifact thật | Có thể dừng submit; cuối media chờ duyệt chung |
| Video | Bản MP4 chờ duyệt, issue theo timestamp | Dựng sau media hợp lệ; xem/nghe thật | Chờ duyệt video; sau đó kiểm xuất/mark |

Trang sản phẩm phải mở đúng file thật; chưa có file thì ghi chưa có. Demo không tạo placeholder có hình/tiếng để giả thành sản phẩm đã kiểm.

## 3. Nút dừng và tiếp tục

### Đang làm media

Ví dụ có một ảnh đã gửi và một ảnh chưa gửi:

1. Người dùng bấm **Dừng gửi mới**.
2. Runtime tiếp nhận yêu cầu; scheduler và worker kiểm trước submit. Từ thời điểm stop có hiệu lực không gửi mục mới.
3. Ảnh đã gửi giữ request/session, hiển thị chờ thu. Có thể tiếp tục thu nếu yêu cầu người dùng cho phép; không hứa hủy provider.
4. Khi thu xong và không còn thao tác đang làm, hiển thị **Đã dừng**.
5. **Tiếp tục phần chưa gửi** chỉ có hiệu lực nếu không còn unknown, gate/integrity/cap đủ và phạm vi nhiệm vụ còn hợp lệ.

Nếu chỉ muốn dừng hẳn cả thao tác thu, cần thể hiện đúng yêu cầu đó và giữ request để đối chiếu sau. Không đóng browser cần làm evidence cho request còn dở. Hành vi hủy tức thì phụ thuộc công cụ, không quảng cáo khi chưa có.

### Đang chờ người dùng duyệt

Hiển thị **Chờ duyệt content/media/video revision N**. Nút cần cụ thể: “Duyệt bản N”, “Yêu cầu sửa”. Tiếp tục qua bước kế tiếp chỉ sau quyết định hợp lệ; không dùng một nút Continue để vừa chạy vừa giả approve.

### Timeout sau gửi

Hiển thị **Cần đối chiếu**, request/session/target và bằng chứng. Khóa tạo lại mục đó. Nếu tìm được ảnh đã tạo, thu ảnh cũ. Không có đủ bằng chứng thì giữ cần can thiệp; không biến “không thấy tile” thành chưa gửi.

## 4. Bổ sung prompt: trước hết chọn loại yêu cầu

| Phạm vi | Ví dụ | Quản lý |
|---|---|---|
| Hệ thống | Đổi quyền worker, retry hoặc cách renderer hoạt động | Phạm vi phát triển; diff, validation, ảnh hưởng integrity. Không nhập rồi áp trực tiếp cho sản xuất |
| Kênh | Mặc định video mới nền sáng, nét viền đậm | Hồ sơ kênh có phiên bản; không sửa brief job cũ ngầm |
| Video | “Video này hoàn toàn tiếng Anh; thêm giải thích cách dùng” | Brief/content revision qua workflow; giữ nguyên phản hồi và hiển thị ảnh hưởng |
| Ảnh | “SC02 ảnh 1 cần thấy rõ động tác săn mồi, giữ ao/góc máy” | Reject đúng target media, bản sửa mới và reference thật; giữ audio nếu narration không đổi |
| Âm thanh | “Cảnh 2 đọc sai trọng âm” | Reject audio đúng cảnh, hướng dẫn retake; giữ narration nếu chỉ lỗi phát âm |
| Bản dựng | “Phụ đề cuối hiện quá nhanh” | Xác định lỗi timeline/render hay lời dẫn; sửa đúng phần, không cắt ý ngầm |

Những loại này là trường/luồng tương tác, không tạo sáu kho prompt độc lập. Nguồn nội dung vẫn là brief/content và nguồn vận hành vẫn là chính sách/skill hiện hành.

## 5. Ví dụ quản lý yêu cầu thêm cho một ảnh

Người dùng nhập: “Giữ góc máy và ao. Cá sấu phải đang lao về con mồi, mascot nhỏ ở góc. Không đổi lời dẫn.”

1. Chọn **Một ảnh → SC02 / ảnh 1**.
2. Lưu nguyên văn yêu cầu; agent chuẩn bị bản sửa có chỉ dẫn nội bộ tiếng Anh nhưng giữ nguyên dữ liệu chữ được phép/narration/anchor.
3. Xem trước ảnh hưởng: content/giọng còn hợp lệ nếu không đổi hợp đồng; ảnh target sửa; media và video phụ thuộc cần revision/quyết định tương ứng.
4. Nếu request cũ đang chạy/unknown, chặn gửi thay; thu/đối chiếu trước.
5. Reject đúng revision/target; tạo lần sửa qua công cụ hợp lệ và repair plan khi runtime yêu cầu.
6. Xem ảnh trước/sau, prompt/reference/request từng lần, lỗi còn lại. Không chỉnh attempt cũ.
7. Review media hiện tại được duyệt mới cho dựng video tiếp.

Không yêu cầu người dùng duyệt riêng từng prompt hoặc từng ảnh mặc định. Nội dung đã được phép và sửa mục đã reject tiếp tục trong phạm vi đó; chỉ hỏi khi yêu cầu mới mở rộng hợp đồng/quyền hoặc điểm chặn thật. Ba gate vẫn giữ nguyên.

## 6. Mỗi lần gửi cần hồ sơ truy vết

Trang prompt hiển thị từ nguồn thật:

- Job, phần, revision, scene/image/target.
- Mẫu cố định và phiên bản/hash; nguồn brief/content; yêu cầu sửa liên quan.
- Prompt hoàn chỉnh đã gửi, danh sách chữ được phép, Character/Base reference.
- Provider/model/ratio/session/account profile không chứa secret.
- Request/attempt ID, thời điểm submit, trạng thái, kết quả tải về/hash.
- Kiểm kỹ thuật và kiểm chất lượng thực sự đã làm, lỗi còn lại.

Đề xuất thay đổi có nhãn **Bản nháp yêu cầu**; preview có nhãn **Prompt dự kiến**; journal thật hiển thị **Prompt đã gửi**. Không thay nhãn dự kiến thành đã gửi nếu chưa submit. Chi phí Flow ghi giả định theo người dùng, không ghi đã xác minh khi thiếu bằng chứng.

Giữ nguyên mẫu cố định `prompt_templates.py` theo chính sách hiện tại. Bổ sung vào trường dữ liệu/hướng dẫn sửa được hỗ trợ; không chỉnh template để né gate. Thay template nếu có yêu cầu phát triển riêng phải rà phạm vi/quy tắc tương ứng trước làm.

## 7. Phạm vi bản đầu đề xuất

Giữ một giao diện thống nhất: giới thiệu/setup, công việc ba phần, sản phẩm thật, yêu cầu bổ sung và lịch sử. Bản xem chỉ đọc ra mắt trước; nút thao tác nối runtime sau khi observe/stop/revision/ownership đủ. Có thể thiết kế toàn bộ màn hình ngay để người dùng hiểu đích, nhưng demo không là nghiệm thu.

Chưa quyết định bắt buộc chuyển chat thành nguồn phụ: người dùng có thể yêu cầu trong chat; điều phối ghi đúng workflow và giao diện phản ánh cùng trạng thái. Không giữ hai quyết định duyệt hoặc hai brief khác nhau giữa chat và trang quản lý.
