# Đề xuất sửa FlowPool sau kiểm tra Chrome thật

Đây là bản thiết kế ghi trước khi sửa. Mã tương ứng đã được hợp nhất trong các commit `c5151c9`, `a544e2c`, `7829a3d` và `45a3ee0`; [lỗi nhận diện/số dư](../logs/issues/FLOW-004.md) đã qua `doctor` thật trên bốn profile. [Lỗi chọn cài đặt](../logs/issues/FLOW-005.md) có bản sửa nhưng đang chờ kiểm tra live sau khi Chrome Allow. Chưa có ảnh/clip tạo thành công, chưa đổi `flowpool_enabled` hoặc baseline của job.

## Bằng chứng hiện có

- Daemon FlowPool đã nối vào Chrome; hai tab profile được kiểm tra đang ở trang dự án Flow và hiện thông tin tài khoản. Trình soạn prompt thật là `<div contenteditable="true" translate="no" class="ProseMirror">`, **không có** `role="textbox"`.
- Bản `@swissmarley/gflow-cli` đang cài định vị prompt bằng `[role="textbox"][contenteditable="true"]`. `FlowPage.assertReady()` vì vậy báo `LoginRequiredError` trên trang dự án đã đăng nhập. `flow-ops.mjs` hiện đổi mọi lỗi từ lời gọi đó thành `NEEDS_LOGIN`; doctor hướng người dùng đăng nhập lại dù lỗi là thiếu selector.
- `flowpool.pipeline.gflow()` chỉ đưa ảnh có `--character` hoặc `--base-image` vào FlowPool. Ảnh tham chiếu CH02/CH03 và mọi lệnh `character create` rơi về `adapters.gflow()` → `b2_bridge.ensure_connected()` → kết nối CDP khác. Điều này phá hợp đồng một kết nối của daemon và có thể làm Chrome hỏi Allow lần hai.
- `sys/assets/characters/tiensu-mascot/character.json` hiện có `reference: null`, `flow.media_id: null`; chưa có bitmap mascot tiền sử ở thư mục này. `image_pipeline.request()` gọi `characters.mascot_for()` cho `ref:CH01` trước khi tới FlowPool, nên media sẽ dừng với `MASCOT_REFERENCE_MISSING` kể cả sau khi sửa selector.
- `sys/config.json` còn `flowpool_enabled: false`. Với cấu hình đó các lệnh ảnh đi đường B-2 cũ, còn clip Veo bị `clip_policy()` chặn.

## Bản sửa mã tối thiểu

### 1. Dùng selector prompt riêng trong FlowPool

**`sys/flowpool/flow-ops.mjs`**, gần `loadGflow()`, thêm `promptEditor(page)` chọn **một editor đang hiển thị** trong thanh soạn thảo: ưu tiên `.prompt-input .ProseMirror[contenteditable="true"]`, rồi `.ProseMirror[contenteditable="true"]`, rồi selector cũ `[role="textbox"][contenteditable="true"]`. Nếu không tìm thấy hoặc có nhiều editor không phân biệt được, ném `FLOW_EDITOR_NOT_FOUND`; không chọn phần tử ẩn hay đoán editor đầu tiên. Dùng cùng locator này trong các hàm sau:

- `assertProjectEditor(page, g)`: chạy `assertUsable(page)` **trước** khi nhìn editor để giữ chặn CAPTCHA/đăng xuất. Xác nhận URL là dự án Flow và editor đang hiển thị. Nếu marker yêu cầu xác minh/đồng ý của Flow hiện lên thì trả `MANUAL_ACTION_REQUIRED`; nếu chỉ thiếu editor thì trả `FLOW_EDITOR_NOT_FOUND`, không trả `NEEDS_LOGIN`.
- `fillPrompt(page, prompt, g)`: sao chép chuỗi thao tác tin cậy của `FlowPage.fillPrompt()` (đóng layer, click/focus, `ControlOrMeta+a`, `Backspace`, `pressSequentially`), nhưng dùng `promptEditor(page)`. Đọc lại `innerText` để chắc prompt đúng trước khi chuẩn bị commit. Không dùng `page.evaluate()` để gán `textContent`, vì ứng dụng có thể không nhận sự kiện nhập.
- `composerImageCount(page)`: bắt đầu từ chính `promptEditor(page)` rồi tìm ancestor chứa nút gửi `arrow_forward`; thiếu composer thì lỗi trước gửi. `attachReference()` chỉ thành công khi số ảnh nguyên liệu ở composer tăng sau chọn file. Hiện tại hàm có thể trả `-1` và bỏ qua kiểm tra đó.

Trong `flowPrepare()` và `probe()`, thay `fp.assertReady()` bằng `assertProjectEditor()` và thay `fp.fillPrompt()` bằng `fillPrompt()`. Tiếp tục dùng `FlowPage` của thư viện cho `applySettings`, tải start frame, tìm kết quả, `submit` và tải xuống; không sửa `node_modules`. Khi `assertProjectEditor()` thất bại, `session.pending` phải vẫn rỗng và chưa có `submit`.

**`ensureProject()` trong cùng file:** sau khi kiểm tra `assertUsable()`, trường hợp không thấy thẻ dự án/nút New project nên báo `PROJECT_NOT_FOUND` hoặc `FLOW_NOT_READY`. Chỉ trả `NEEDS_LOGIN` khi URL/nội dung thực sự cho thấy đăng xuất. Giữ `CAPTCHA` và `PROFILE_MISMATCH` nguyên mã. Việc doctor có thể báo UI thay đổi là chính xác hơn việc yêu cầu đăng nhập lại.

### 2. Mọi lượt tạo media từ xa đi qua daemon duy nhất

**`sys/flowpool/pipeline.py`, `gflow()`**: phân luồng theo lệnh, không theo sự hiện diện của `--character`/`--base-image`:

| Lệnh khi `flowpool_enabled=true` | Đường xử lý đề xuất |
| --- | --- |
| `image` (ảnh tham chiếu, cảnh, biến thể) | `_run()` → `FlowPool` → socket daemon, kể cả khi danh sách `--character` rỗng |
| `character create` (ảnh đăng ký CH01/CH02/CH03) | Hàm `_register()` mới: yêu cầu `--image`, tạo request `kind='image'`, `refs=[ảnh tham chiếu cần đăng ký]`, `variants=1`, cùng prompt/model/ratio/job; `_run()` qua daemon. Ghi đúng một ảnh trong `--out`, metadata và `ui-proof.json` với `mode='character-register'` để `image_pipeline.request()` kiểm tra như hiện nay |
| `batch` | Giữ `_batch()` qua `_run()`; tất cả ảnh cần có tham chiếu đúng theo cảnh |
| `auth/login` | Không phải lượt tạo media; xử lý riêng, không dùng để tự mở kết nối CDP mới trong lúc daemon chạy |

Giữ thao tác ghép/copy mascot chuẩn ở local **chỉ** nếu đầu vào là yêu cầu mascot đã có ảnh chuẩn và helper local riêng xác nhận không hề gọi B-2/CDP. Các nhánh khác không được fallback sang `adapters.gflow()` khi FlowPool bật; thiếu reference phải trả lỗi trước submit. Việc `character create` hiện thực chất tạo một ảnh có tham chiếu để so sánh ở media gate; không ghi là đã đăng ký nhân vật trong thư viện Flow khi chưa có bằng chứng UI đó.

**`sys/image_pipeline.py`, `request()` và `batch_submit()`**: truyền đường dẫn tham chiếu của từng nhân vật đã duyệt và base scene theo `registration_journal`/`base_image`, không suy từ tên nhân vật hoặc quét `runs/*` của job khác. `flowpool.pipeline.gflow()` hiện luôn gắn mascot cho ảnh cảnh và `_batch()` cũng chỉ gắn mascot; điều đó sẽ bỏ mất nhận diện CH02/CH03 dù request metadata liệt kê tên. Khi một cảnh có nhiều nhân vật, dùng một **bảng ảnh tham chiếu local** kết hợp đúng các ảnh đã duyệt (hash của bảng là một thành phần request identity), rồi gắn thêm base scene như nguyên liệu thứ hai. Hình ghép chỉ là đầu vào tham chiếu, không phải ảnh thành phẩm. Không gửi nếu không tạo/kiểm tra được bảng ảnh hoặc nếu UI không hiển thị đủ nguyên liệu. Đây là thay đổi cần thiết cho các cảnh có đồng thời CH01–CH03 trong `tiensu-001`; giới hạn hiện tại của `FlowPool.normalize_request()` là tối đa hai tệp `refs`.

`flowpool.pipeline._register()` và ảnh tham chiếu CH02/CH03 phải giữ `job`, `target`, `out_dir` ổn định để journal FlowPool có cùng identity khi `resume`. Giữ trình tự `intent → submitted → collected → validated`; timeout sau commit là `unknown` và phải reconcile theo bằng chứng thật, không tự gửi lại.

### 3. Tạo ảnh gốc mascot trước media

Đây là ngoại lệ bootstrap duy nhất cho quy tắc luôn gắn mascot: chưa có ảnh gốc thì không thể gắn chính nó. Thêm một đường FlowPool rõ ràng cho **một ảnh gốc** `purpose='mascot_bootstrap'`, `refs=[]`, `variants=1`; `normalize_request()` chỉ cho phép thiếu `refs` ở purpose này, không nới yêu cầu tham chiếu cho ảnh cảnh/nhân vật thông thường. Dùng prompt tiếng Anh từ `character.json` để đòi đúng đầu trắng viền mực, tóc nâu bù, áo da thú một vai, vòng hạt xương và tay chân người que. Request đi qua daemon, journal và kiểm tra ảnh như mọi ảnh FlowPool; lưu ở `sys/scratch/` để xem thật.

Sau khi ảnh thật được xem và chấp nhận là chuẩn, dùng lệnh hiện có `python3 pilot.py mascot-reference tiensu --from <ảnh-thật>`; lệnh đó copy ảnh và ghi `reference`/`sha256`. Không tự ghi `character.json`, không cài ảnh placeholder và không gọi ảnh chưa xem là đã duyệt. Sau đó mới cho `ref:CH01` và các ảnh tiếp theo chạy. CH01 có thể dùng copy local của ảnh chuẩn; mọi lượt tạo từ xa CH02/CH03/cảnh/clip vẫn đi daemon.

### 4. Cấu hình và tính toàn vẹn job

Chỉ sau kiểm thử selector và doctor trên tab thật, đổi `flowpool_enabled` sang `true` một lần trong cấu hình. Điều đó đổi file được khóa của `tiensu-001`: chạy `integrity-diff tiensu-001` và để **người dùng** quyết định/chạy `adopt-code` theo AGENTS.md; agent không tự chạy lệnh này. Tiếp tục cùng job và revision đang có sau gate content hợp lệ. Không tạo job mới để tránh khóa.

## Kiểm thử có ý nghĩa trước khi gửi media

1. **`sys/flowpool/test-flow-ops.mjs`**: fixture DOM có ProseMirror không role và tài khoản đã đăng nhập phải `probe`/`flowPrepare` thành công; selector role cũ vẫn hoạt động. Trang `accounts.google.com`, text đăng nhập, CAPTCHA và marker xác minh vẫn trả đúng lỗi. Trang dự án thiếu editor trả `FLOW_EDITOR_NOT_FOUND`, không `NEEDS_LOGIN`; không có lần `submit`. Kiểm tra nhập đúng prompt và tăng số nguyên liệu sau upload.
2. **`sys/tests/test_flowpool_pipeline.py`**: thay test đang kỳ vọng registration rơi về adapters. CH02 reference không `--character`, CH02/CH03 registration, ảnh cảnh một/nhiều nhân vật và batch đều gọi `_run()`; mock `adapters.gflow`/`b2_bridge.ensure_connected` phải không được gọi khi FlowPool bật. Kiểm tra `ui-proof.mode`, metadata, đúng source ref và base, cùng `not_submitted` khi thiếu nguồn; đường bootstrap không refs là ngoại lệ duy nhất.
3. **Kiểm tra live chỉ đọc**: daemon giữ một CDP connection, `open-profile` và `doctor` trên từng profile phải báo project/editor thật, tài khoản đúng, model thấy được, credit đọc được hoặc `unreadable` rõ ràng. Không dùng doctor thành công làm bằng chứng rằng upload, generation hay clip đã nghiệm thu.
4. **Kiểm tra sau khi được phép sản xuất**: gửi một ảnh bootstrap/cảnh thật qua chính daemon, xem ảnh và bằng chứng tham chiếu; đối chiếu journal/credit trước sau. Nếu timeout sau submit, reconcile; không gửi thử cùng identity lần nữa. Clip đầu tiên kiểm tra start frame, model, đầu ra, âm thanh/phụ đề ở video cuối và chi phí thực tế trước khi chạy hàng loạt.

## Điểm dừng rõ ràng

- `CAPTCHA`, đăng xuất hoặc sai tài khoản: người dùng xử lý trong Chrome; selector mới không được bỏ qua.
- Không thấy editor, nút upload, model hoặc nguyên liệu sau thao tác: lỗi trước submit, sửa UI adapter rồi chạy lại cùng job.
- Outcome sau submit không rõ: giữ journal `unknown`, lấy bằng chứng Flow thật và reconcile; không gửi trùng.
- Mascot chuẩn chưa có ảnh thật; content chưa có quyết định duyệt hợp lệ; hoặc integrity job lệch: chưa chạy media phụ thuộc.
