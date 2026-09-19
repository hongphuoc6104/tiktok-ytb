# M2 — Ảnh Google Flow

## Trạng thái và giới hạn

M2 v2 có ba điểm duyệt: A `references`, B `first-three`, C `final`. Chỉ C được duyệt mới mở module âm thanh. CLI chọn bước từ SQLite, không dựa vào lời agent. Phiên bản cũ được giữ nguyên; không đặt lại integrity của công việc cũ sau khi sửa mã nguồn.

Bản thử dùng 6 cảnh, 45–60 giây và ảnh 9:16 ≥720×1280. Bộ prompt hỗ trợ tham số 9:16/16:9, nhưng đường sản xuất hiện tại chỉ nhận 9:16; thay tỷ lệ cho công việc sau cần đồng bộ hợp đồng media/bộ dựng. Không bật video AI, API trả phí, batch đồng thời hoặc UI web.

Flow CLI 1.1.1 có một số thao tác giao diện bỏ qua lỗi. `scripts/gflow_guard.mjs` bọc phiên bản này, yêu cầu xác nhận chế độ Image, model/tỷ lệ và gắn nhân vật. Selector chưa nghiệm thu trên tài khoản thật: nếu giao diện khác, dừng trước gửi, sửa ở lượt phát triển và tạo công việc mới. Không bỏ lớp bảo vệ để “chạy cho được”.

## Lượt sản xuất

Chạy lệnh tại thư mục dự án, dùng `.venv/bin/python pilot.py` làm tiền tố:

1. `status JOB`, `next JOB`. Control và nội dung v2 phải được người dùng duyệt.
2. `flow-login JOB`: người dùng tự đăng nhập Chrome profile `video-pilot`.
3. Quan sát màn hình đúng tài khoản/project/model và giá cho thao tác sắp làm. Ghi JSON rồi `flow-preflight JOB --evidence FILE`.
4. `run JOB images`, `validate JOB images`; gửi `revisions/images/N/review.md` để xem.
5. Sau phản hồi rõ: `approve JOB images --checkpoint references --revision N --note 'nguyên văn phản hồi'`.
6. `run JOB images` đăng ký từng nhân vật; nếu yêu cầu đối chiếu, xem ảnh chuẩn và ảnh đăng ký. Sau người dùng xác nhận, ghi bằng chứng như dưới rồi tiếp tục. Tạo SC01–SC03; thêm ảnh kiểm chứng riêng nếu một nhân vật chưa có ba ví dụ trong ba cảnh đầu.
7. Duyệt `first-three` bằng đúng revision; chạy tiếp, duyệt `final` sau xem toàn bộ sáu cảnh.

`resume JOB` hoạt động ở phiên agent mới. Không tạo lại ảnh đã tải và hash còn đúng. Dữ liệu giả lập không được chuyển vào công việc sản xuất.

## Bằng chứng trước tạo

Ví dụ JSON quan sát (thời gian là Unix seconds thực tế; screenshot là file thật):

```json
{
  "observed_at": 0,
  "mode": "image",
  "credits_per_generation": 0,
  "model": "Nano Banana 2",
  "profile": "video-pilot",
  "project": "Video Pilot",
  "observer": "người quan sát thực tế",
  "account_confirmed": true,
  "operations": ["image"],
  "screenshot": "/absolute/path/observed.png"
}
```

Chỉ ghi `character-register` trong operations khi đã quan sát riêng chi phí thao tác đó. Screenshot và lời khai quan sát không phải chứng minh máy đọc tự động về giá. Không xác minh được thì dừng. Mỗi request lưu bản sao bằng chứng riêng; chứng cứ có hạn 10 phút và không chấp nhận thời gian tương lai.

## Đối chiếu đăng ký nhân vật

Lệnh `character create` của CLI có thể sinh ảnh mới từ ảnh chuẩn. Vì vậy cần người dùng đối chiếu và xác nhận tên nhân vật đã lưu trên Flow trước khi tạo cảnh. Không dùng thumbnail mới làm ảnh chuẩn tự động.

```json
{
  "name": "tên riêng do hệ thống tạo",
  "matches_approved_reference": true,
  "observer": "người kiểm tra",
  "note": "phản hồi xác nhận của người dùng",
  "screenshot": "/absolute/path/registration.png"
}
```

`flow-confirm-registration JOB --request HASH --evidence FILE`. Hash ảnh chuẩn/kết quả được chương trình bổ sung. Nếu khác ngoại hình, yêu cầu sửa nhân vật bằng lệnh reject và duyệt lại A; không xác nhận giả.

## Sửa và khôi phục

`reject JOB images --checkpoint final --revision N --scene SC06 --note 'lý do sửa'` chỉ yêu cầu tạo lại SC06; ghi lý do vào prompt thực tế. Dùng `--character ID` thay `--scene` để sửa ảnh chuẩn và duyệt lại các cảnh liên quan. Bản cũ và nhật ký không bị xóa. Bị lỗi ở bước chưa có output cũng có thể reject đúng revision/checkpoint để yêu cầu sửa nhân vật/cảnh đã thất bại. Audio không bị vô hiệu hóa do thay ảnh; bản dựng bị vô hiệu hóa.

Timeout/không rõ kết quả: `flow-reconcile JOB --request HASH --asset FILE --evidence JSON --note 'đối chiếu kết quả trên Flow'`. JSON cần request, mode (`image`/`character-register`), characters (tên đã gắn, có thứ tự), actual_prompt (nguyên văn prompt thực tế), matched_download=true, observer và screenshot. Không có bằng chứng rõ thì giữ blocked. Không tự xác nhận kết quả không tồn tại để gửi lại.

## Nguồn prompt

Người dùng cung cấp ba mẫu IMAGE AUTOMATION / TEXT TO VIDEO / IMAGE TO VIDEO và cho biết đã kiểm tra. Giữ nguyên văn trong `prompt_templates.py`, chưa coi đó là bằng chứng tích hợp Flow tại máy này đã thành công. Mẫu ảnh có tham số tỷ lệ; bản thử dùng biến thể từng ảnh 9:16 để tôn trọng A/B/C. Mẫu video được lưu nhưng hàm sử dụng từ chối trong M2.

## Nghiệm thu

Chạy `.venv/bin/python -m unittest discover -s tests -v`. I01–I14 nằm trong `tests/test_images_v2.py`, sử dụng provider giả lập và duyệt TEST trong thư mục tạm. Nghiệm thu thật cần ảnh chuẩn, ba cảnh, sáu cảnh, bằng chứng Flow, duyệt người dùng và kiểm tra resume. M2 chưa hoàn thành chỉ vì test đạt.
