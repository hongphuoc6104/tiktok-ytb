# Bản đồ thực hiện `tiensu-001`

Cập nhật: 26/09/2026. Phạm vi: tiếp tục **cùng job** qua content → media → video, sau đó xuất thành phẩm và đánh dấu chủ đề đã làm. Đây là bản đồ điều phối; trạng thái sống phải đọc lại bằng `pilot.py status`, `next`, `integrity-diff` và FlowPool trước mỗi lượt sản xuất. Mọi lệnh bên dưới chạy từ `sys/`.

## Cập nhật tiếp tục: bản duyệt content revision 2

Khóa integrity đã hết ở lượt kiểm tra status/next mới. Đã reject content 1, lưu brief 2 qua revise-brief, viết lại draft và resume thành bản duyệt content revision 2 đang awaiting_review (module content revision 3 theo manifest). Bản mới có tám cảnh, sáu chương SC02–SC07, bảy claims theo sáu nguồn, 65 hình gồm năm clip và 120 beat. Ước tính trung tâm khoảng 620 giây; chưa có WAV để xác nhận. Xem [review content 2](../runs/tiensu-001/reviews/content/2/review.md). Các dòng content 1 và khóa mã bên dưới là bằng chứng lịch sử, đã được cập nhật bởi đoạn này.

Bước kế tiếp: người dùng duyệt hoặc phản hồi content 2; sau duyệt mới chạy media. FlowPool chưa được mở lại, vấn đề cooldown/ảnh mascot và cấu hình vẫn chưa nghiệm thu. Đường agy E2BIG và lỗi token_revoked đã ghi CONTENT-002; không sửa mã được bảo vệ hoặc thử gọi lại.

## Trạng thái có bằng chứng

| Yêu cầu/cổng | Bằng chứng hiện tại | Kết luận |
|---|---|---|
| Job đúng quy trình | [`workflow.json`](../runs/tiensu-001/workflow.json): v3, mode `review`; `tiensu/bank.py status tiensu-001`: một chủ đề đã giữ chỗ cho job | Dùng ba cổng duyệt của người dùng; không tạo job thay thế, không đổi mode. |
| Hợp đồng kênh | [`briefs/1.json`](../runs/tiensu-001/briefs/1.json): `channel=tiensu`, 16:9, tiếng Việt, phụ đề bật, 480–720 giây, 8 cảnh, `clips.max=10`, Veo Fast, 2 biến thể | Thời lượng cuối phải đo trên WAV/MP4; clip chỉ qua FlowPool khi mọi điều kiện được phép. |
| Content kỹ thuật | [`checks.json`](../runs/tiensu-001/revisions/content/1/checks.json): `passed=true`, `semantic_review=pending`, `timing=estimated`; [`review.md`](../runs/tiensu-001/reviews/content/1/review.md): revision 1, 8 cảnh, 64 hình logic, 120 beat | Chưa có duyệt chất lượng. Chưa có quyết định `reviews/content/1/decision.json`. |
| Content theo brief | Brief R4 yêu cầu **6 chương bằng chứng** có nguồn. [`content.json`](../runs/tiensu-001/revisions/content/1/content.json) chỉ đặt `chapter` tại SC04–SC08 (5 cảnh); brief chỉ có nguồn S1; content có 2 claim, đều trỏ S1 tại SC05–SC06 | **Chưa chứng minh đạt R4.** Cần sửa theo quy trình revision trước media; xem [`CONTENT-002`](../logs/issues/CONTENT-002.md) và [đề cương nguồn/sáu chương](tiensu-001-content-revision-proposal.md). Kiểm tra kỹ thuật hiện tại không thay thế phản biện nguồn. |
| Khóa mã | `pilot.py integrity-diff tiensu-001` đã ghi nhận mã/cấu hình khác baseline; phạm vi hiện gồm cả `.agents/` và nguồn FlowPool theo bản sửa [INTEGRITY-001](../logs/issues/INTEGRITY-001.md) | Lệnh sản xuất vẫn bị chặn. Chạy lại `integrity-diff` **một lần sau khi chốt mã**, giữ job/lịch sử; chỉ người dùng chạy `adopt-code` sau khi xem diff, hoặc khôi phục đúng baseline. |
| FlowPool thật | [FLOW-004](../logs/issues/FLOW-004.md) qua `doctor` thật: bốn profile đăng nhập và đọc số dư 1050/331/1050/1050. Yêu cầu mascot cùng ID có bốn lượt `MODEL_NOT_SELECTABLE` trước submit; sau bản sửa mới, bộ lập lịch chặn `NO_READY_PROFILE` vì cả bốn profile `cooldown_until=null`; xem [FLOW-005](../logs/issues/FLOW-005.md) | Chưa có ảnh/clip thật hoặc chi phí khấu trừ. Bản sửa panel chưa được chạy trên Flow thật; không tự mở cooldown hay gửi tiếp. Cần người dùng quyết định phục hồi profile. |
| Ảnh tham chiếu và nhân vật phụ | Bản sửa trong [`flowpool/pipeline.py`](../flowpool/pipeline.py) và [`image_pipeline.py`](../image_pipeline.py) đã đưa ảnh ref/đăng ký CH02–CH03, ảnh cảnh và batch qua cùng daemon; kiểm thử đường liên quan đạt, xem [FLOW-003](../logs/issues/FLOW-003.md) | Không còn nhánh fallback B-2 khi FlowPool bật trong mã hiện tại, nhưng phải nghiệm thu ảnh/ref/media ID thật trước sản xuất hàng loạt. |
| Mascot tiền sử | [`character.json`](../assets/characters/tiensu-mascot/character.json): `reference=null`; chưa có ảnh tham chiếu; xem [MASCOT-001](../logs/issues/MASCOT-001.md). Request bootstrap đầu tiên vẫn `not_submitted` | Xem ảnh thật sau lượt tạo thành công và cài qua CLI `mascot-reference`; không dùng mascot từ vựng hoặc ảnh test giả. |
| Cấu hình và chi phí | [`config.json`](../config.json): `video_generation=true`, `credit_budget=4200`, `flowpool_enabled=false`; Flow thật hiển thị 0 credit cho chế độ ảnh và 20 credit cho Veo Fast 8 giây ở Profile 10, nhưng chưa gửi generation | Clip job còn bị `clip_policy` chặn cho tới khi bật FlowPool hợp lệ. Số dư UI là quan sát thật; chi phí thực tế mỗi lượt phải đo trước/sau, không suy từ giá trên menu. |
| Media, video và xuất | Chưa có revision media/video, WAV/ảnh sản xuất/SRT/MP4 trong job hoặc thư mục `video/tiensu-001` | Chưa có dữ liệu nghe/xem thật, chưa có duyệt media/video, chưa thể `mark`. |
| Đóng gói | [`packaging.py`](../packaging.py) đã được gọi bởi `workflow.publish_videos` sau khi MP4 được duyệt và xuất; chưa có thumbnail/metadata thật | Kiểm tra `thumbnail*.jpg`, `metadata.json`, `description.txt` sau khi xuất; không coi mã nguồn hay test là thành phẩm. |

## Kế hoạch tổng quát, lặp ở mỗi cổng

1. **Đọc trạng thái sống.** Chạy `python3 pilot.py doctor`, `status tiensu-001`, `next tiensu-001`; khi báo integrity, chạy `integrity-diff tiensu-001`. Ghi lỗi mới ngay vào `logs/issues/` và mục lục. Không sửa SQLite, `integrity.json`, revision, review hay báo cáo đã lưu.
2. **Chốt các phụ thuộc trước sản xuất.** Kiểm tra và sửa thiếu hụt nguồn/chương ở content theo quy trình revision; nghiệm thu FlowPool bằng Chrome thật, model, ảnh tham chiếu và clip thử có đối chiếu nhật ký; chốt cấu hình được phép dùng trước khi người dùng nhận baseline mới. Không dùng credit cho media khi content chưa có quyết định hợp lệ.
3. **Content.** Giữ chủ đề `hunter-gatherer-daily-life`, đủ R1–R5, đặc biệt 6 chương R4 có claim truy nguồn; giữ 8 cảnh, 480–720 giây dự kiến, giọng “bạn”, mascot tiền sử, ảnh không chữ và overlay tiếng Việt. Nếu sửa, dùng `reject tiensu-001 content --revision N --note ...`, cập nhật `draft/content.json` và brief bằng `revise-brief` nếu hợp đồng nguồn phải đổi, rồi `check-draft` và `resume`. Không sửa lời dẫn sau khi đặt coverage/claims/anchor. Người dùng xem [`review.md`](../runs/tiensu-001/reviews/content/1/review.md) của revision **hiện tại** và quyết định content bằng phản hồi nguyên văn.
4. **Media.** Chỉ sau quyết định content hợp lệ: tạo WAV tiếng Việt trước, nghe toàn bộ và đo thời lượng thật; nếu lệch 480–720 giây thì sửa đúng nguồn lỗi trước khi chi credit. Tiếp đó tạo ảnh still và clip đã khai báo, gắn ảnh mascot chuẩn và Base scene reference khi kế thừa, kiểm từng ảnh/clip thật, nhịp, phụ đề và overlay ở kích thước xem. Media được duyệt **một lần chung** cho audio, hình, nhân vật và nhịp. Khi lỗi, `reject media` đúng `--scene`, `--character` hoặc `--part audio` rồi `resume` cùng job. Trạng thái gửi Flow chưa rõ kết quả phải `flow-reconcile` bằng bằng chứng UI thật trước khi gửi lại.
5. **Video.** Chỉ sau quyết định media hợp lệ: `run tiensu-001 video` qua điều phối, xem/nghe toàn bộ MP4 16:9 tiếng Việt với phụ đề; kiểm lời–hình, clip Veo tắt tiếng, overlay, nhịp 8–12 phút, mascot, đoạn kết và thumbnail. Cần sửa thì `reject video` đúng revision rồi `resume`; lời dẫn phải quay về content, WAV/ảnh phải quay về media. Người dùng duyệt revision video thực tế. Sau khi xuất, xác nhận MP4 trong `video/tiensu-001/` cùng các tệp đóng gói rồi mới chạy `python3 tiensu/bank.py mark tiensu-001`.
6. **Đối chiếu sau mỗi lần sửa.** Chạy lại `status`/`next`, kiểm revision và đường dẫn review mới, xác nhận quyết định cũ còn hợp lệ hoặc cần duyệt lại. Mỗi lỗi có micro-plan, số lượt hữu hạn và bằng chứng kết thúc. Chỉ tuyên bố hoàn thành khi quyết định video hợp lệ, MP4 xem/nghe được, hồ sơ xuất đủ và chủ đề được `mark`.

## Micro-plan cho các lỗi đang mở

### A. Khóa integrity của `tiensu-001`

- Xem `integrity-diff` sau khi chốt mã/cấu hình, gồm nguồn FlowPool mới được khóa; không dùng số lượng file cũ vì đã có thêm thay đổi theo yêu cầu người dùng. Không đổi config trong lúc chạy job để né cổng.
- Người dùng tự chọn khôi phục bản cũ hoặc chạy trong terminal: `python3 pilot.py adopt-code tiensu-001 --confirm tiensu-001 --reason "<lý do thật>"`. Agent không chạy lệnh này, không tạo job mới, không sửa integrity bằng tay.
- Kiểm chứng kết thúc: `status` và `next` không còn `Protected implementation changed`; sau đó mới dùng `resume` ở đúng cổng.

### B. Content revision 1 chưa đáp ứng bằng chứng R4

- Kiểm tra R1–R5 trên lời dẫn và claims thật; hiện có 5 `chapter`, một nguồn S1, 2 claim. Nghiên cứu nguồn thật cho các chương còn thiếu; không lấy `seed_facts` hay ảnh minh họa làm bằng chứng, không bịa di chỉ/số liệu.
- Sau khi khóa integrity được xử lý, `reject content` revision hiện tại **trước** khi tạo brief revision (đổi brief trước có thể làm manifest cũ stale). Nếu hợp đồng nguồn cần bổ sung, cập nhật kho chủ đề rồi dùng `revise-brief` hợp lệ với [bản nháp đã kiểm schema](../scratch/tiensu-001-revision-prep/proposed-brief-v2.json); không sửa brief đã lưu hay làm lại job. Sửa draft, tạo content revision mới, kiểm tra kỹ thuật và phản biện từng chương.
- Kiểm chứng kết thúc: 6 chương có nhãn riêng, mỗi chương có phát biểu then chốt và claim trỏ nguồn tương ứng trong brief; lời dẫn không khẳng định quá mức. Chỉ phản hồi thực tế của người dùng mới tạo quyết định content trong mode `review`.

### C. FlowPool và clip chưa được nghiệm thu sống

- Bốn profile đã qua `doctor` thật sau bản sửa nhận diện/số dư [FLOW-004](../logs/issues/FLOW-004.md). Daemon đã kết nối, nhưng hiện tất cả profile đang `cooldown` không có hạn tự hết; không mở client CDP khác hay `mark ready` để né cổng.
- Bản sửa chọn Image/model/9:16 đã hợp nhất và kiểm thử mục tiêu đạt, song lượt sau bản sửa dừng ở `NO_READY_PROFILE` trước UI. [FLOW-005](../logs/issues/FLOW-005.md) giữ micro-plan; chỉ tiếp tục đúng request/journal khi trạng thái profile được giải quyết bằng quyết định hợp lệ, không đổi ID/prompt.
- Nghiệm thu lần lượt: ảnh độc lập; ảnh `based_on` có Character/Base reference thật; chọn/đọc lại media ID; một clip ảnh→video từ still đạt yêu cầu; journal và credit trước/sau; gián đoạn/timeout được đối chiếu mà không gửi trùng. Kiểm chất lượng output thật, không chỉ selector hay metadata. Hàng đợi B-2 đang `production_ready=false`; ngoại lệ thử nghiệm hiện có không tự thành acceptance sản xuất.
- Kiểm riêng ảnh tham chiếu và đăng ký CH02/CH03 sau sửa [FLOW-003](../logs/issues/FLOW-003.md): mã đi cùng daemon và kiểm SHA nguồn, nhưng ảnh `based_on`/bảng tham chiếu nhiều nhân vật/media ID vẫn cần bằng chứng output thật; không suy kết quả của một đường từ đường khác.
- Chỉ khi khả năng chạy thật và đường chi phí rõ ràng mới chốt config FlowPool theo quyết định người dùng. `flowpool_enabled=false` hiện chặn năm clip đã lên kế hoạch; `video_generation=true` và budget dương riêng lẻ chưa đủ. Không sửa config hoặc nhật ký để qua gate.

### D. Lỗi có thể gặp tại media/video

- WAV dài/ngắn, sai phát âm: xác định cảnh, nghe take thật, `reject media --part audio` theo cảnh nếu có thể; sau revision nghe lại và đo toàn bộ timeline.
- Mascot, chữ thừa, ảnh sai ý hoặc clip sai khung: ghi scene/image ID và bằng chứng nhìn thấy; sửa phạm vi nhỏ nhất qua `reject media`, giữ ảnh tham chiếu, kiểm lại trước/sau. Flow ambiguous cần đối chiếu UI và journal trước mọi retry.
- Phụ đề, overlay, thời điểm neo, crop hoặc render: dùng báo cáo kỹ thuật để định vị rồi xem MP4 ở kích thước sử dụng. Sửa đúng phần và duyệt lại theo gate; không lấy `editorial-audit.json` hay kiểm thử làm quyết định chất lượng.
- Xuất hoặc đóng gói lỗi sau duyệt video: `resume` cùng job để thử lại xuất; không ghi quyết định duyệt giả. Chỉ `mark` khi MP4 và hồ sơ xuất đã kiểm chứng.

## Việc chỉ người dùng làm và mốc hoàn thành lớn hơn

- Người dùng trực tiếp quyết định `adopt-code`; bấm **Allow**/xử lý đăng nhập hoặc CAPTCHA của Chrome; đưa phản hồi duyệt thật cho content, media và video của đúng revision. `approve` chỉ ghi nguyên văn phản hồi đó. Không có xác nhận thì không chạy phần phụ thuộc.
- Kênh theo [`tien-su-plan.md`](tien-su-plan.md) còn mốc GĐ6 gồm **ba video pilot review** với số đo credit, TTS và render; GĐ7 auto chỉ sau mốc đó. `tiensu-001` là video đầu, không được tạo job khác cho cùng nội dung để né khóa. Khi lên video tiếp theo, rút chủ đề mới từ `tiensu/bank.py` và lặp cùng ba cổng.
