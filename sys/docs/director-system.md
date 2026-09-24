# Hệ thống đạo diễn của Video Pilot

Các vai trò dưới đây làm việc bên trong **content → media → video**. Mỗi vai trò chịu trách nhiệm cho quyết định sáng tạo và tiêu chí kiểm chứng, không thêm gate và không tự cho phép chạy nhiều agent.

| Vai trò | Lúc áp dụng | Quyết định cần đưa vào sản phẩm |
|---|---|---|
| vp-script-director | Outline, viết và sửa content | Mục tiêu học, hook/payoff, nguyên nhân–hành động–hậu quả, lời thoại và thực hành |
| vp-visual-director | Content và media | Hành động chứng minh nghĩa, bố cục, nhận diện mascot, trạng thái liên tục |
| vp-edit-director | Beats, media và bản video | Điểm cắt, thời gian đọc/đáp lại, phụ đề, nhịp phối hợp lời–hình |
| vp-audio-director | Kế hoạch lời, WAV và MP4 | Ý đồ câu nói, phát âm, khoảng chờ, kiểm tra giọng và ưu tiên lời |

## Tích hợp thật trong hệ thống

Adapter sinh nội dung nạp trực tiếp các tài liệu cần dùng; không trông chờ lượt chỉ-trả-JSON tự mở đường dẫn trong skill. Outline nhận kịch bản/hình và tài liệu sư phạm nếu là brief từ vựng; lượt chi tiết nhận thêm biên tập/âm thanh và văn phong. Bộ duyệt máy nhận tiêu chí theo phần, bốn skill tương ứng và kịch bản đã chốt khi đánh giá media/video. Bản review dành cho người dùng có tiêu chí đạo diễn tương ứng.

Không chỉnh mẫu cố định prompt_templates.py. Những hướng dẫn mới chỉ bổ sung tại adapter sinh/duyệt và skill nội bộ. Nguồn nghề nghiệp được ghi tại `.agents/skills/vp-content/references/director-sources.md` ở gốc dự án.

## Hợp đồng nội dung

Giữ dữ liệu đạo diễn trong outline, purpose, transition, action, camera, images và beats hiện có. Không tạo một kịch bản phụ làm nguồn sự thật thứ hai.

Content-v3 có trường tùy chọn ở từng cảnh:

```json
"audio_direction": {
  "vi": {
    "intent": "Invite the learner to repeat the model sentence calmly.",
    "pronunciation_notes": "Check the target word and sentence stress against the chosen reference.",
    "learner_pause_seconds": 2.0
  }
}
```

Có thể khai báo `en` riêng cho bản tiếng Anh. Khoảng chờ là số từ 0 đến 8 giây, được thực hiện **cuối cảnh**, sau lời đọc; thời lượng WAV/video bao gồm nó. Chọn độ dài theo câu cần nhại và thử nghe, không mặc định mọi bài đều hai giây. Nếu cần một lượt thực hành giữa đoạn, thiết kế ranh giới cảnh trước khi chốt lời/neo. Khoảng chờ không phải cue lời mới và không làm thay đổi văn bản narration. Audio mới ghi content_end (ranh giới chunk trước phần yên lặng thêm), để khoảng chờ không kéo trễ các cue/neo trước đó; đây chưa phải mốc âm vị hoặc word alignment.

`intent` và `pronunciation_notes` hướng dẫn kiểm tra và retake. Runtime không có tham số để thực thi chính xác một cảm xúc; không khẳng định các trường này tự làm giọng có cảm xúc. Không hỗ trợ âm nhạc/SFX hay lip-sync chỉ vì có skill đạo diễn âm thanh.

Giữ I đúng trong dữ liệu tiếng Anh. VieNeu chỉ nhận cách đọc Ai ở bước chuẩn hóa tổng hợp; bản tiếng Anh Pocket TTS giữ I. Thay đổi cách chuẩn hóa làm thay phiên bản cache, tránh dùng lại take cũ cho thuật toán mới.

## Phụ đề và bằng chứng

Cue giữ nguyên chữ, chọn ranh giới từ/cụm và chia tối đa hai dòng. Cùng danh sách cue tạo SRT và MP4. Bố cục caption được dùng chung bởi composition và phép kiểm tra hình học để tránh kiểm tra một cỡ chữ nhưng render cỡ khác.

`scripts/editorial_audit.py --props PATH` chỉ đọc props, trả lỗi/warning có mốc thời gian. Các ngưỡng thời gian đọc là gợi ý biên tập, không phải tiêu chuẩn mọi người học. Các mốc cue vẫn nội suy theo segment; muốn khẳng định đồng bộ phải nghe video thật.

Khi render, lưu `editorial-audit.json` cạnh props. Đây là report kỹ thuật mới, không phải quyết định duyệt. Các lỗi timeline/dấu câu được chặn; warning mật độ chữ phải được xem trong bối cảnh. Khả năng đọc, phát âm, mascot và học tập vẫn cần ảnh/WAV/MP4 thật.

## Brief mới và lịch sử

Mặc định kênh chuyển từ khuôn năm phần sang chức năng học. `scene_count` vẫn là số cảnh sản xuất của brief; `example_count` điều khiển số câu ví dụ (mặc định 2, từ 1 đến 4). Video mới có mẫu nghe/lượt nhớ lại và phản hồi; phát âm, gốc từ, IPA chỉ dùng khi hữu ích. Không sửa brief của job đang có, không sửa ledger hoặc integrity baseline.

Các job bị chặn vì implementation thay đổi giữ nguyên lịch sử. Khi triển khai bộ mã mới, tạo job mới theo kho từ và mode hợp lệ. Test/render phát triển không phải sản phẩm đã được duyệt và phải nằm trong `sys/`, không trộn vào `video/`.

## Kiểm chứng trước khi tuyên bố chất lượng

1. Kỹ thuật: schema, đầy đủ ý, timeline/cue, thời lượng, không tràn chữ và đúng tỉ lệ.
2. Cảm nhận: xem từng ảnh, nghe toàn bộ WAV, xem/nghe đầy đủ MP4; báo unsupported nếu không có khả năng.
3. Học tập và phân phối: người học dùng đúng từ, nhớ lại; dữ liệu giữ chân/lưu/chia sẻ theo nền tảng. Chưa có dữ liệu thì ghi chưa đo.

Không lấy kết quả mức 1 thay cho mức 2 hoặc 3. Không tự ghi integration-check cho Antigravity từ kết quả kiểm thử ở phiên này.
