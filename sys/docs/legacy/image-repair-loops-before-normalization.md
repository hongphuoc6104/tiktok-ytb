# Sửa ảnh có tiến bộ, không lặp vô ích

Thay đổi này áp dụng cho job mới tạo với mã hiện tại. Không sửa integrity baseline, revision, quyết định hoặc bằng chứng của job cũ để chạy tiếp.

## Phạm vi và lịch sử

- `--image IMAGE_ID` sửa đúng hình; thêm `--ratio 9:16` hoặc `16:9` để giới hạn tỷ lệ. Bỏ tỷ lệ có nghĩa áp dụng cho cả hai bản của hình.
- `--scene SCENE_ID` chủ động sửa toàn cảnh. Phản hồi nhắc đích danh một hình trong cảnh nhiều hình bị chặn và yêu cầu dùng `--image`.
- Lịch sử phản hồi nguyên văn được giữ trong `image_edits`. Mỗi bản kế hoạch sửa mới được thêm vào `image_repair_details`, không ghi đè lịch sử.
- Prompt chỉ dùng snapshot yêu cầu hiện tại: lỗi còn tồn tại và lỗi mới. Lỗi đã giải quyết không được nối tiếp vào prompt; yêu cầu còn hiệu lực phải được ghi lại đầy đủ.
- Mô tả nhân vật không bị chèn lại mỗi lần nhắc mã. Chính sách chữ chỉ xuất hiện một lần. Bridge Flow không tự thêm một prompt giải phẫu khác với prompt đã lưu.

## Cách sử dụng

Chạy từ `sys/`; các mã dưới đây chỉ minh họa, không phải quyết định duyệt.

```bash
.venv/bin/python pilot.py repair-status JOB --image IMG_SC03_02 --ratio 9:16
.venv/bin/python pilot.py reject JOB media --revision N --image IMG_SC03_02 --ratio 9:16 --repair-plan scratch/repair.json --note 'Phản hồi thực tế, nguyên văn'
.venv/bin/python pilot.py resume JOB
```

`repair-status` cung cấp đường dẫn ảnh, hash hiện tại, hash ảnh bị từ chối ở lượt trước và kế hoạch trước. Phải xem ảnh thật trước khi viết bằng chứng. Lượt đầu có thể chỉ dùng `--note`; khi đó lỗi mang mã `visual`. Từ lượt thứ hai phải cung cấp kế hoạch có cấu trúc. Nên dùng kế hoạch ngay từ đầu để có mã lỗi cụ thể.

Ví dụ cấu trúc `repair.json` cho lỗi còn tồn tại:

```json
{
  "current_sha256": "HASH_ẢNH_HIỆN_TẠI",
  "previous_sha256": "HASH_ẢNH_BỊ_TỪ_CHỐI_LƯỢT_TRƯỚC",
  "strategy": {"pose": "Show regret through lowered head and hands; preserve the reference face."},
  "issues": [
    {
      "id": "eyebrows",
      "status": "remaining",
      "evidence": "Mô tả chi tiết thực sự quan sát thấy khi so sánh hai ảnh.",
      "instruction": "Preserve the plain forehead and solid oval eyes from the character reference."
    }
  ]
}
```

Lượt đầu dùng `previous_sha256: null`, trạng thái `new`. Các lượt sau giữ mã lỗi và phân loại `remaining` hoặc `resolved`; lỗi mới dùng mã mới và `new`. Mọi lỗi đang mở ở lượt trước phải được phân loại, không được bỏ qua hoặc đổi tên để né giới hạn. Lỗi `resolved` có thể để `instruction` rỗng. Kế hoạch chỉ có lỗi đã hết không được sinh ảnh lại: chuyển sang đánh giá media.

`strategy` chỉ nhận `pose` và/hoặc `composition`, được đưa vào prompt thật. Không nhận một câu khai báo chung rằng đã đổi chiến lược. Thay tham chiếu hoặc nội dung vẫn phải qua workflow tương ứng, không dùng trường này để gắn đường dẫn ảnh tùy ý.

## Giới hạn và quyết định chất lượng

- Cùng yêu cầu sửa và cùng chiến lược bị chặn ngay; đổi khoảng trắng không tạo lượt mới.
- Sau hai lượt sửa cùng lỗi, chỉ tiếp tục khi có thay đổi cụ thể về tư thế/bố cục. Thêm một câu cấm tương tự không đủ.
- Tối đa sáu kế hoạch sửa trên mỗi ảnh/tỷ lệ hoặc nhân vật; đổi tên lỗi không làm mới giới hạn. Chạm giới hạn phải dừng để chẩn đoán, không tự tạo job mới nhằm né giới hạn.
- Trạng thái `needs_attention` và báo cáo trong `repair-stops/` xuất hiện ở `status`/`next`; `resume` không tự chạy tiếp. Một kế hoạch hợp lệ cho đúng đích bị chặn có thể giải quyết điểm dừng trước khi chạm giới hạn tuyệt đối.
- Media review kèm ảnh trước/sau. Auto bắt buộc báo `resolved`, `remaining`, `new` theo từng ảnh và bằng chứng thị giác. Thiếu khả năng xem/nghe vẫn là `unsupported`; metadata/hash không thay thế đánh giá cảm nhận.
- Hash giống nhau chỉ chứng minh byte không đổi. Không cho báo lỗi đã được sửa trên hai file giống hệt nhau. Mức độ tiến bộ về nghĩa/hình vẫn do người hoặc bộ đánh giá xem ảnh thật quyết định.
- Giữ nguyên ba gate content → media → video; không tự thông qua media vì đã sửa đủ số lần.
- Auto không gọi lại bộ đánh giá media/video nếu artifact giữ nguyên và đã có kết quả chưa đạt. Sau khi sửa khả năng xem/nghe hoặc nguyên nhân đánh giá, có thể yêu cầu đánh giá lại rõ ràng bằng `resume JOB --retry-review`; cờ này không mở khóa gửi ảnh hoặc bỏ giới hạn sửa.

## Tái sử dụng và phục hồi

Ảnh không bị tác động và audio hợp lệ được giữ lại. Khóa cache của ảnh kế thừa dùng mã và hash ảnh nền, không dùng đường dẫn thư mục revision; nền cùng byte không buộc tạo lại ảnh con. Nền thay đổi byte sẽ làm mới các ảnh phụ thuộc theo `based_on`.

Trước batch, lưu mọi yêu cầu có khả năng được gửi. Thiếu nhật ký sau gián đoạn là kết quả chưa rõ, không được tự chuyển sang gửi từng ảnh. Chỉ bằng chứng từ adapter rằng chưa gửi mới được ghi `not_submitted`.

Kết quả đã sinh nhưng lỗi thu hồi giữ trạng thái `generated`. Tiếp tục đúng yêu cầu sẽ dùng chế độ chỉ thu hồi, giữ định danh Flow và không mở quyền tạo mới nếu mất kết quả đã biết. Trường hợp một phần batch đã sinh được phân loại từng yêu cầu. `submitted`/`ambiguous` vẫn cần `flow-reconcile` với bằng chứng thật; đổi prompt không vượt khóa.

Kiểm thử dùng job tạm và provider giả. Việc các kiểm thử đạt không đồng nghĩa Flow thật, phát âm hoặc chất lượng video đã được nghiệm thu.
