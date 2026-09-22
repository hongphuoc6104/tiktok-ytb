Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Lời dẫn tự nhiên

Đây là lời **đọc lên**, không phải văn viết để đọc bằng mắt. Áp dụng khi soạn `narration`/`narration_en` trong content-v3, cùng lượt sinh nội dung — không có bước viết lại sau, vì `coverage.quote`, `coverage.quote_en`, `claims.quote` và `beats[].anchor` neo nguyên văn vào lời dẫn.

## Ràng buộc bắt buộc

- **Không bỏ ý, không rút ngắn.** Nguyên tắc dưới đây chỉ sửa CÁCH DIỄN ĐẠT, không bao giờ là cớ để bỏ `required_points`, gộp cảnh hay cắt nội dung. Mọi ý bắt buộc vẫn phải được `coverage` ánh xạ đủ.
- **Không bịa để đỡ mơ hồ.** Không thêm số liệu, tên, nguồn không có trong brief/sources. `claims` phải khớp `facts` thật.
- **Thứ tự bắt buộc: viết lời dẫn xong, chốt, rồi mới đặt neo.** Đặt `coverage.quote`/`quote_en`, `claims.quote`, `beats[].anchor.vi/en` lên trên lời dẫn đã chốt. Không sửa lời dẫn sau khi đã đặt neo — sửa là lệch quote/occurrence, hỏng validate_content và validate_plan.
- Đầu ra là JSON theo schema (content-v3), không dùng định dạng trả lời 4 phần (bản viết lại/đã sửa/đã xóa/cần xác nhận) của skill humanizer gốc.

## Vì sao câu phải ngắn — không chỉ để "hay hơn"

`tts_worker.py` chỉ tổng hợp trọn một cảnh trong một lượt (giữ ngữ điệu liên tục) khi `narration` của cảnh đó ≤ `tts_max_chars` (mặc định 256 ký tự, config.json). Dài hơn thì rơi về tổng hợp từng câu rời rạc, mất đường lên xuống của cả cảnh. Câu ngắn, chủ ngữ rõ, ít mệnh đề lồng vừa dễ nghe vừa giữ chất lượng giọng đọc thật — đây là lý do kỹ thuật, không chỉ gu văn phong.

Nhịp câu dài ngắn xen kẽ nghe tự nhiên khi đọc lên, không chỉ khi đọc bằng mắt — đừng viết mọi câu cùng một độ dài.

## Dấu hiệu cần tránh — Nội dung

| Dấu hiệu | Cách sửa |
|---|---|
| Sáo ngữ tôn vinh không mang dữ kiện: "đóng vai trò quan trọng", "minh chứng cho", "để lại dấu ấn sâu đậm", "phản ánh xu hướng rộng lớn hơn" | Bỏ nếu không có dữ kiện đi kèm; nếu có dữ kiện, giữ dữ kiện, bỏ lời khen. |
| Mệnh đề đuôi phân tích hời hợt: "…, góp phần nâng cao…", "…, thể hiện cam kết…", "…, qua đó khẳng định…" | Cắt mệnh đề đuôi. Có dữ kiện thật thì tách thành câu riêng nói thẳng. |
| Quy chiếu mơ hồ không nguồn: "các chuyên gia cho rằng", "nhiều nguồn tin", "giới quan sát nhận định" khi chỉ có một nguồn hoặc không nguồn | Nêu đúng chủ thể nếu brief/sources có; không có thì hạ đúng quy mô hoặc bỏ mệnh đề quy chiếu. Không bịa tên nguồn. |
| Ngôn ngữ quảng cáo: "sôi động", "phong phú", "đa dạng", "đột phá", "toàn diện" | Thay bằng mô tả trung tính có dữ kiện, hoặc bỏ nếu không có gì cụ thể. |
| Đoạn tổng kết lặp ý: "Tóm lại", "Nhìn chung", "Có thể thấy rằng" | Bỏ nếu chỉ lặp lại điều đã nói. |
| Rào đón giới hạn dữ liệu: "thông tin chi tiết không được công bố rộng rãi", "tính đến thời điểm hiện tại" | Bỏ — giọng chatbot, không phải nội dung kịch bản. |

## Dấu hiệu cần tránh — Câu chữ

| Dấu hiệu | Cách sửa |
|---|---|
| "Không chỉ X mà còn Y", "Đây không phải là…, mà là…" | Tách hai câu khẳng định, hoặc bỏ vế phủ định nếu không mang dữ kiện. |
| Quy tắc bộ ba: ba tính từ/cụm song song đều đặn | Giữ từ mang nghĩa thật, bỏ từ đệm — thường chỉ còn một hai từ. |
| Né động từ "là/có": "đóng vai trò là", "được xem như", "sở hữu", "mang đến" | Trả về "là", "có", "gồm". |
| Nối kết mơ hồ: "gắn liền với", "có liên quan đến" | Nói thẳng quan hệ nếu brief cho biết; nếu brief cũng mơ hồ, giữ mơ hồ nhưng đơn giản. |
| Từ vựng AI dày đặc (một hai từ lẻ là bình thường, dày mới là vấn đề) — VI: "nhấn mạnh", "làm nổi bật", "thúc đẩy", "bức tranh", "bối cảnh", "then chốt", "tỉ mỉ", "hơn nữa", "đáng chú ý là"; EN: *delve, underscore, showcase, foster, robust, tapestry, landscape, crucial, intricate, meticulous, additionally* | Thay bằng từ thường ngày. |
| Trang trọng hóa thừa: "tiến hành thực hiện", "sử dụng" thay "dùng"; EN *utilize, authored, relocated* | Dùng từ ngắn, đúng khẩu ngữ khi đọc lên. |
| Câu nào cũng cùng độ dài, cùng cấu trúc | Xen câu ngắn với câu dài hơn. |

## narration_en

Áp dụng đúng các nguyên tắc trên với danh sách dấu hiệu tiếng Anh ở bảng trên. Bản 16:9 phát **hoàn toàn** bằng tiếng Anh, không phụ đề — đây là bản độc lập, không phải bản dịch phụ của tiếng Việt. Cùng giới hạn `tts_max_chars` áp dụng cho `narration_en` khi tổng hợp giọng Anh theo cảnh.

## Từ khoá và câu tiếng Anh trong lời dẫn

Khi kịch bản chứa từ khoá hoặc câu ví dụ tiếng Anh (video học ngoại ngữ):
- **Không viết hoa toàn bộ từ tiếng Anh** (tránh TTS đánh vần từng ký tự). Dùng chữ thường hoặc viết hoa chữ đầu (`wake`, `get up`).
- **Tách riêng câu ví dụ tiếng Anh bằng dấu chấm và ngoặc kép**: Không dùng dấu phẩy nối liền câu tiếng Anh với câu dịch tiếng Việt. Viết: `Thứ nhất: "We wake up early every day." Chúng tôi thức giấc sớm mỗi ngày.` để audio có khoảng ngắt nghỉ tự nhiên và phụ đề tách thẻ riêng biệt.
- **Tốc độ đọc**: Giọng đọc đã được cấu hình chậm hơn ~8% (`tts_speed: 0.92`), phát âm rõ từng âm tiết.

## Đừng sửa quá tay

Sửa quá tay tạo ra văn bản không giống người mà cũng không giống nội dung kịch bản.

- Không cấm từ "quan trọng" hay các từ trên một cách máy móc — vấn đề là mật độ và công thức, không phải bản thân từ.
- Không cố tình viết sai ngữ pháp hay chêm khẩu ngữ suồng sã để "cho giống người nói".
- Không hạ giọng văn xuống mức xuề xòa nếu chủ đề vốn cần trang trọng.
- Giữ nguyên thuật ngữ, tên riêng, số liệu, trích dẫn nguồn.

## Tra cứu đầy đủ

`ai-tells.md` là danh mục đầy đủ (từ vựng theo giai đoạn, cụm quảng cáo, vấn đề trích dẫn, danh sách "không phải dấu hiệu AI"). File này **không** được nạp vào prompt sinh nội dung — quá nặng cho mỗi lượt. Đọc trực tiếp khi làm việc tương tác và cần tra một dấu hiệu cụ thể.
