# Độ dài lời dẫn: ưu tiên nội dung, hiểu đúng mốc 256 ký tự

Ngày cập nhật: 29/09/2026. Người dùng đã đồng ý lưu hướng dẫn này trong `sys/docs/` trước khi đồng bộ vào các skill được bảo vệ.

## Phạm vi và trạng thái

Áp dụng như hướng dẫn biên tập khi viết mới hoặc sửa nội dung theo workflow hiện hành. Đây là tài liệu bổ sung đã được yêu cầu, không phải thay đổi cách chạy TTS. Chưa sửa `.agents/`, cấu hình, mã nguồn, schema hoặc prompt cố định. Adapter chưa tự nạp tài liệu này; người biên tập cần đọc trực tiếp. Hướng dẫn trong skill sẽ được đồng bộ ở một đợt chuyển phiên bản có kiểm soát.

Brief hiện tại vẫn là hợp đồng: giữ đủ ý, số cảnh, ngôn ngữ và khoảng thời lượng đã lưu. Mốc khoảng 55 giây, linh hoạt 35–75 giây, là yêu cầu của các đợt kịch bản trong cuộc trao đổi này, không phải mặc định mới cho mọi dự án.

## Quyết định biên tập

- 256 ký tự là ngưỡng lựa chọn cách tổng hợp giọng trong cấu hình hiện tại, không phải trần sáng tạo hay tiêu chí tự động đánh rớt chất lượng kịch bản.
- Ưu tiên nghĩa chính xác, lời nói tự nhiên, diễn biến có liên hệ, kết thúc giải quyết tình huống mở đầu và lượt thực hành có phản hồi.
- Giữ lời gọn bằng cách bỏ câu đệm hoặc lặp không có tác dụng. Cho phép một cảnh vượt 256 ký tự khi cần để giữ đủ ý hoặc mạch kể. Không bỏ ví dụ, ý bắt buộc hay phản hồi chỉ để xuống dưới ngưỡng.
- Chia cảnh tại thay đổi hành động, ý nghĩa, điểm nhìn hoặc lượt thực hành; không chia cơ học ở ký tự thứ 256. Nếu cần đổi số cảnh đã lưu, dùng revise-brief theo workflow trước khi lập nội dung mới.
- Một cảnh có thể có nhiều hình và nhiều nhịp. Độ dài đoạn không quyết định số hình; bố trí hình theo thông tin cần nhìn thấy.
- Chốt lời dẫn trước khi đặt coverage, claims và anchor. Khi sửa nội dung đã nộp, dùng reject content và tạo revision mới; không sửa revision/review đã lưu.
- Câu hỏi luyện tập kết thúc trước khoảng chờ; đáp án ở cảnh kế tiếp nếu dùng learner_pause_seconds, vì runtime đặt khoảng chờ ở cuối cảnh.

## Cách chạy local hiện tại đã đối chiếu mã nguồn

Trong [tts_worker.py](../tts_worker.py), nhánh xử lý ở cấp cảnh được chọn theo thứ tự:

| Điều kiện | Cách xử lý | Ý nghĩa đối với biên tập |
|---|---|---|
| Yêu cầu cảnh có `parts` | `mixed`: tổng hợp các phần tiếng Việt và ghép phần tiếng Anh đã tải | Ưu tiên trước kiểm tra độ dài; dưới 256 không bảo đảm tổng hợp cả cảnh trong một lượt. Không mặc định mọi câu có tiếng Anh đều đã được tách `parts`; cần xem yêu cầu thực tế. |
| Không có `parts`, `tts_scene_synthesis=true`, `len(narration) <= tts_max_chars` | `scene`: tổng hợp cả lời cảnh rồi chia waveform để phục vụ các đoạn phụ đề | Có cơ hội giữ mạch ngữ điệu giữa các câu; chưa chứng minh giọng thực tế tự nhiên. |
| Không thuộc hai trường hợp trên | `per-sentence`: tổng hợp từng phần tử trong danh sách câu `texts`, sau đó ghép | Vượt ngưỡng không tự động làm cảnh bị từ chối; cần chú ý ngữ điệu và khoảng nối khi nghe kết quả. |

[config.json](../config.json) hiện đặt `tts_max_chars=256` và `tts_scene_synthesis=true`. Phép so sánh dùng `len()` của chuỗi narration, tính cả khoảng trắng và dấu câu; không phải số từ, số giây hoặc số byte. Bảng trên mô tả nhánh của worker Việt hiện tại, không khẳng định worker tiếng Anh độc lập có cùng cơ chế.

Tổng hợp liền cả cảnh có thể giúp giữ ngữ điệu qua nhiều câu. Tổng hợp rời có thể làm các câu kém liền mạch, nhưng đây là rủi ro cần nghe kiểm tra, không phải kết luận mọi đoạn dài đều kém. Tăng ngưỡng cũng chưa được chứng minh là tốt hơn trên giọng hiện tại.

## Phân biệt với đường Colab TTS

Đối chiếu [colab_bridge/protocol.py](../colab_bridge/protocol.py): phần lời Việt được đóng gói theo `texts`; nếu có `parts`, mỗi đoạn được tách thành các phần theo ngôn ngữ. Phần tiếng Anh độc lập được đóng gói từ `narration_en` theo cảnh. Hàm đóng gói này không dùng `tts_max_chars` để chọn giữa scene và per-sentence như worker Việt local.

Vì vậy, không áp bảng lựa chọn của local cho Colab, không suy rằng đoạn dưới 256 ký tự được tổng hợp liền cảnh trên Colab, và cũng không suy rằng Colab nhận đoạn dài tùy ý. Giới hạn thực tế của mô hình và chất lượng đoạn dài cần được xác minh riêng. Kết quả nghe hoặc benchmark của một mẫu không chứng minh mọi độ dài đều đạt.

Theo [hướng dẫn Colab TTS](colab-tts.md), khi bật Colab cùng `parallel_images`, audio và ảnh có thể chạy đồng thời sau duyệt content; review media, timeline và render vẫn chờ WAV thật và đủ ảnh. Ngoại lệ về thứ tự chạy không thay đổi nguyên tắc biên tập lời dẫn, duyệt content hoặc kiểm tra integrity.

## Ví dụ quyết định khi biên tập

- Cảnh 220 ký tự vẫn có câu đệm hoặc nhắc lại đáp án nhiều lần: sửa cho tự nhiên dù đã dưới ngưỡng.
- Cảnh 280 ký tự cần giữ đủ tình huống, câu mẫu và giải thích đúng nghĩa: có thể giữ nguyên; ghi nhận cách tổng hợp thực tế và nghe lại khi làm media.
- Cảnh có câu hỏi rồi trả lời ngay trong cùng đoạn: tách lượt thực hành ở ranh giới có ý nghĩa, dành khoảng chờ trước đáp án. Nếu thay số cảnh, sửa brief theo workflow trước.
- Một cảnh có hai trạng thái cần thấy: lập đủ hình/beat; không tăng số cảnh chỉ để đạt số ký tự và không kéo dài thời gian giữ một hình để thay cho hành động còn thiếu.

## Kiểm tra theo từng phần

**Content:** kiểm tra nghĩa, câu mẫu, quan hệ nhân vật, nguyên nhân–kết quả, thời lượng ước tính và lượt trả lời. Số ký tự là thông tin chẩn đoán; không dùng “dưới 256” để thay cho đánh giá nội dung.

**Media khi được yêu cầu:** nghe toàn bộ WAV để kiểm tra độ liền mạch, chuyển ngôn ngữ, trọng âm, âm cuối và khoảng chờ. Đo thời lượng thật theo brief. Không suy chất lượng từ độ dài, transcript hoặc tên chế độ tổng hợp. Nếu không nghe được, ghi unsupported theo workflow.

**Video khi được yêu cầu:** kiểm tra nhịp hình, chữ và phụ đề trên artifact thật. Không dùng mốc thời gian ước tính từ content như mốc đồng bộ đã đo.

## Đồng bộ skill ở đợt chuyển phiên bản sau

Các file dự kiến cập nhật:

1. [narration-style.md](../../.agents/skills/vp-content/references/narration-style.md): thay phần giải thích giới hạn độ dài bằng nguyên tắc ưu tiên nội dung và bảng điều kiện ngắn gọn về scene/mixed/per-sentence.
2. [vp-audio-director/SKILL.md](../../.agents/skills/vp-audio-director/SKILL.md): bổ sung rằng độ dài không xác nhận chất lượng âm thanh; xác định chế độ tổng hợp thực tế và nghe WAV trước khi nhận xét.

Nội dung chỉ dẫn nội bộ đề xuất cho hai file:

> Treat 256 characters as the current local Vietnamese synthesis-routing threshold, not a creative ceiling. Preserve required meaning, natural speech, connected examples, and learner feedback. Split at a meaningful action, idea, or practice boundary, not at a character count. Honor the saved brief and revise it through the workflow if the scene count must change. Freeze narration before adding coverage and anchors.

> In the local Vietnamese worker, when a scene request contains parts, mixed-language synthesis takes precedence over the scene-length check. Otherwise, scene-level synthesis requires tts_scene_synthesis and a narration length within tts_max_chars; longer narration uses per-sentence synthesis. Short narration does not prove fluent prosody, correct pronunciation, or seamless language switching. Judge those properties by listening to the actual WAV. Do not apply this local routing rule to Colab; inspect its request segmentation and actual output separately.

Trước khi sửa file được bảo vệ, kiểm kê job đang dùng chúng và xử lý việc chuyển phiên bản theo AGENTS.md. Không sửa mốc integrity, không tự chạy adopt-code hoặc tạo job thay thế để tránh chặn. Chưa áp dụng hai đoạn đề xuất vào skill trong đợt tài liệu này.

Không thay đổi `tts_max_chars`, engine, tốc độ hoặc công cụ tạo giọng trong cập nhật này. Muốn thử ngưỡng mới cần yêu cầu phát triển riêng và so sánh âm thanh thật có kiểm soát.
