# Trang quản lý local

Chạy từ `sys/`. Bootstrap dùng Python stdlib, chưa cần import Pilot:

```sh
python3 scripts/bootstrap.py plan
python3 scripts/bootstrap.py check
python3 scripts/bootstrap.py apply --install
.venv-management/bin/python -m dashboard.server --port 8765
```

Mở `http://127.0.0.1:8765`. Server chỉ bind loopback. Nếu đã có Python quản lý khác, dùng `python3 -m dashboard.server --python /đường/dẫn/python`. `resume --install` tiếp tục setup; không chạy sản xuất, OAuth, cấp GPU hoặc generation. Bootstrap tạo venv riêng không cần ensurepip; cài hai dependencies quản lý đã ghim bằng uv/pip có sẵn hoặc ensurepip của Python. Không cài model/renderer local.

Tám tab đọc job, checkpoint, revision, artifact và events thật. CLI chính thức xử lý stop/run/resume/mode/approve/reject; engine giữ quyền và ownership. API không ghi SQLite hay giả quyết định. Artifact phải nằm trong manifest và trong thư mục job; không phục vụ symlink thoát job hoặc đường dẫn tùy ý. WAV/ảnh/MP4 dùng file đã thu, video hỗ trợ byte range. JSON/text được lọc dữ liệu xác thực; GET không có quyền ghi. Mọi POST cần Host loopback, Origin cùng server, CSRF token và JSON.

Tab Tài khoản inventory metadata browser Linux và hồ sơ Colab; chưa có probe thì auth/capability là `not_tested`. Chọn pool/default không chuyển owner của request đang dở. “Gắn danh tính Google” ghi ánh xạ email băm theo xác nhận nguyên văn của người dùng, nguồn `user_confirmed`, không coi là auth live. “Kiểm auth chỉ đọc” dùng runtime CLI Colab đã cài, token hợp lệ hiện có, Google userinfo và `Client.list_assignments`; không refresh token, khởi OAuth, đồng bộ/xóa sessions hoặc cấp GPU. Token hết hạn chuyển giao người dùng OAuth qua terminal. Không đưa token/code/cookie lên trang.

Kho ngân sách mặc định dùng chung qua chat/checkout: `~/.config/video-pilot/management`. Runtime T4 còn cấp tính cả idle, 5 giờ dùng và 1 giờ dự phòng; 24 giờ là cửa sổ nội bộ, không bảo đảm quota Google. Ledger alias theo danh tính Google tránh tạo counter mới khi đổi profile. Request Flow đã gửi/unknown vẫn giữ slots. Ambiguous GPU allocation hiển thị riêng, chưa giả là T4 đã xác nhận; đối chiếu đúng account/session trước thao tác mới. Tài nguyên, auth, ngân sách và chất lượng sản phẩm là các trạng thái riêng.

Kiểm cô lập: `tests.test_dashboard`, `tests.test_dashboard_engine`, `tests.test_account_management`, `tests.test_account_probe`. `tests.test_dashboard_browser` chạy Chromium khi có Node/Playwright; đặt `VP_PLAYWRIGHT_MODULE` tới bản đã cài, không tự tải browser. Browser test dùng WAV/PNG và engine fixtures, không chứng minh giọng, Flow, T4 hay MP4 sản xuất thật.

## Setup trong trang

Tab Tài khoản có trường chọn grant setup/development hiện hữu và chỉ dẫn nguyên văn. Flow có lập kế hoạch, áp dụng cấu hình và mở đúng runtime profile đã cấu hình qua `profile_setup`; profile nguồn Chrome thường cần profile riêng/CDP, không sao chép cookie. Tab Tài khoản và Colab có chọn tên runtime chính xác, cấp T4 theo yêu cầu, chuẩn bị môi trường remote, đối chiếu runtime gốc, thu request gốc và giải phóng runtime riêng. Đây là thao tác dịch vụ thật khi người dùng bấm; inventory/check không tự chạy các thao tác này.

Setup API kiểm role và path scope trước giao việc. Các tác vụ dài chạy riêng, giữ khóa theo canonical Google identity xuyên các controller. Colab account/session phải khớp adapter và allocation/request journal gốc; collect chỉ nhận job/request ID để tìm journal đã lưu, không nhận đường dẫn tùy ý. Raw provider stdout và CDP endpoint không đưa lên frontend. Flow dùng bộ đếm ảnh theo phiên; chỉ Colab có vòng giờ T4.

`Sessions.bind_runtime(service, account, runtime_session, grant=..., source=..., evidence=..., job=None)` là thao tác binding chính thức. `snapshot(job=...)` đóng băng binding theo job; binding mặc định đổi vẫn giữ snapshot/request pins cũ. Binding ghi người chọn, grant và bằng chứng/chỉ dẫn, không thay kiểm auth hoặc allocation thật. Khi chọn job trên trang, “Gắn runtime cho job / phiên” gọi `bind-session` chính thức của engine sau khi lưu binding setup.
