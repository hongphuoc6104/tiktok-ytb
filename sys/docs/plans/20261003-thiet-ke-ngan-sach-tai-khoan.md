# Thiết kế 0.4 — ngân sách giờ/ảnh và tình trạng đăng nhập

Ngày 03/10/2026. Bổ sung cho [bản 0.3](20261003-thiet-ke-colab-va-auto-thuc-hien.md). **Chỉ thiết kế; chưa thêm chức năng runtime hoặc kiểm live tài khoản.**

**Giao diện thử nghiệm đã chốt:** [quyết định ngày 03/10/2026](20261003-chot-giao-dien-thu-nghiem.md). Phần tài khoản là mốc giao diện bản đầu; các dữ liệu/khả năng thực vẫn cần triển khai và kiểm chứng.

## 1. Yêu cầu và phần được điều chỉnh

Người dùng yêu cầu T4 mặc định; vòng năng lượng 6 giờ, trần sử dụng 5 giờ; đếm 24 giờ từ kết nối đầu; chỉ định hoặc tự chọn account; đếm 100–200 ảnh Flow/account/phiên; tối đa ba lần phục hồi; kiểm auth Colab và Flow, thông báo cần login.

Giữ các chức năng đo/hiển thị, tự chọn trong phạm vi sử dụng hợp lệ và ngân sách. **Không thiết kế xoay tài khoản để kéo dài quota miễn phí hoặc né giới hạn/bot/abuse**. Đạt ngân sách thì dừng phát việc mới và giữ kết quả; quota/bot/auth là trạng thái riêng. Account selection cho công việc hợp lệ khác vẫn giữ như bản 0.3; không lấy account pool làm tổng quota miễn phí của một người.

## 2. Đối chiếu nguồn chính thức

Kiểm ngày 03/10/2026:

- [Colab FAQ](https://research.google.com/colaboratory/faq.html): limits/idle/VM/GPU dynamic và không bảo đảm tài nguyên; không công bố quota GPU cố định. Mốc notebook tối đa 12 giờ không phải cam kết CPU 12 giờ mỗi ngày. Không bảo đảm phục hồi sau 24 giờ hoặc được T4. FAQ cấm dùng nhiều account để vượt giới hạn truy cập/tài nguyên.
- [Google Flow Help](https://support.google.com/flow/answer/16353333?hl=en): rate-limit generation để cân bằng tài nguyên; giới hạn có thể thay đổi, số lượt mỗi phút có thể giảm khi tạo nhiều trong ngày. Hướng dẫn unusual activity là chờ rồi thử lại và tắt VPN/proxy nếu đang dùng; không đề xuất xoay account. Runtime hiện hành vẫn giữ điểm dừng bot/quota/503/CAPTCHA.

6 giờ GPU, 5 giờ thực dùng, 12 giờ CPU, 24 giờ cửa sổ và 100–200 ảnh là **ngân sách/giả định người dùng đặt**, không ghi là quyền tài nguyên đã được Google xác nhận. Chưa cấp VM, đọc số dư live hoặc login account trong lượt này.

FAQ Colab cũng có giới hạn cho free managed runtimes về remote-control/web UI/worker. Trước triển khai phần offload, cần xác định đường thực hiện được hỗ trợ và điều kiện account thực tế; không tự dùng account rotation để giải quyết, không mua compute units hoặc đưa xử lý nặng về máy ngầm. Không kết luận chỉ có Colab CLI là đủ chứng minh mọi kiểu workload được hỗ trợ.

## 3. Hai chế độ lựa chọn account

- **Theo chỉ định:** chỉ dùng account/service được người dùng chọn. Không tự chọn khác khi account này lỗi/hết ngân sách; hiển thị lý do và giữ pending/inflight.
- **Tự chọn:** chọn trong pool của phiên cho workload được phép, dựa vào auth live, service capability, session sở hữu và ngân sách nội bộ. Không chọn account khác để vượt quota/abuse hoặc cộng quota miễn phí.

Hiển thị active riêng cho Colab và Flow, cùng job/step/request/session. Có thể active Colab A cho audio và Flow B cho ảnh. Active nghĩa đang phục vụ request/VM thật, không phải chỉ tick chọn/default. Request dở có ownership riêng dù default đã đổi.

## 4. Mô hình giờ Colab

### Khởi điểm

Không bắt đầu đếm khi chỉ mở trang Colab, có file token, OAuth thành công hoặc liệt kê sessions. Mốc bắt đầu là lần xác nhận runtime GPU gắn đúng account/session và kết nối thành công; kiểm GPU thực là T4 theo preset. Nếu quan sát được thời điểm allocation sớm hơn, tính cả khoảng đã cấp để không bỏ sót.

Lưu UTC; giao diện hiển thị Asia/Ho_Chi_Minh. Cửa sổ nội bộ bắt đầu tại mốc này và dài 24 giờ. Chạy lại chat/browser không reset cửa sổ. Danh tính account ổn định; profile/email alias không mở ngân sách mới.

### Thời gian phải tính

Đếm thời gian runtime GPU còn được cấp, kể cả idle nếu VM chưa được giải phóng; không chỉ đếm model đang suy luận. Đóng tab Colab không đồng nghĩa VM đã dừng. Giữ các khoảng start/stop cùng session ID; cuối khoảng phải có xác nhận stop/release/termination. Mất kết nối hoặc telemetry thiếu: đánh dấu ước lượng/không chắc chắn, không tự trừ usage về 0.

Nhiều session cùng account: hiển thị từng khoảng và tổng runtime-hours để tránh ẩn sử dụng đồng thời. Preset đầu chỉ một session GPU riêng/account; ngân sách dùng chung giữa jobs/chats/checkouts. Runtime ngoài sự quản lý của dự án có thể không đo được; ghi rõ phạm vi, không gọi tổng dự án là quota còn lại trên Google.

### Vòng năng lượng

- Thang hiển thị: 6 giờ theo giả định người dùng.
- Phần dự phòng: 1 giờ được khoá ngay từ đầu.
- Ngân sách chạy: 5 giờ cho cửa sổ nội bộ.
- Khả dụng nội bộ: `max(0, 5 giờ - usage đã tính - phần đã giữ chỗ)`.

Vòng hiển thị riêng đã dùng/còn trong ngân sách/dự phòng, có chữ và số, không chỉ màu. Tài nguyên thực hiển thị bên cạnh: chưa kiểm/T4 được cấp/không được cấp/bị giới hạn. Nếu vòng còn 4 giờ nhưng Google không cấp GPU, account vẫn không chạy được.

Ví dụ kết nối được xác nhận 03/10 lúc 10:00: “cửa sổ nội bộ tới 04/10 10:00”. Sau dùng 2 giờ: vòng 6 giờ gồm 2 đã dùng, 3 còn dùng được, 1 dự phòng. Không ghi “Google chắc chắn hồi phục lúc 10:00”.

### Hết ngân sách và qua 24 giờ

Không gửi tác vụ mới khi đã đạt trần 5 giờ. Trước task dài, giữ chỗ theo ước lượng và biên dự phòng; nếu thiếu thông tin, chia task/checkpoint thay vì giả task sẽ kết thúc trong giờ còn lại. Task đang gửi phải thu/đối chiếu; không chuyển account rồi chạy lại nó.

Qua cửa sổ 24 giờ có thể mở ngân sách nội bộ mới nhưng trạng thái dịch vụ chuyển cần kiểm lại. Runtime đang tồn tại qua ranh giới phải phân bổ interval sang hai cửa sổ; không đếm lại hoặc miễn phí khoảng sau ranh giới. Không tự thông báo quota Google đã hồi phục.

CPU có ledger riêng với 12 giờ là mốc nội bộ nếu preset CPU được chọn; không tự fallback CPU khi T4 không được cấp. Render sử dụng CPU trong runtime T4 vẫn tính thời gian GPU runtime còn cấp; không chuyển loại đồng hồ chỉ vì task không dùng CUDA.

## 5. Bộ đếm ảnh Flow

- Mặc định đề xuất 100 ảnh/account/phiên vận hành; người dùng có thể đặt 100–200, tối đa nội bộ 200. Đây là trần dừng, không phải mức chắc chắn tránh bot.
- Profile khác dùng cùng Google identity không mở bộ đếm mới. Tổng phiên không reset khi chuyển tab/chat, mở lại browser hoặc đổi profile. Lưu thêm lịch sử theo ngày để quan sát mức dùng.
- Theo dõi riêng output slots đã gửi, số ảnh tạo được, đã tải, lỗi, unknown và pending. Request đã gửi/unknown vẫn giữ slot; không chỉ đếm JPEG đã tải để bỏ sót các lần gửi.
- Không sinh thêm để đo khả dụng/quota; không dùng screenshot giả. Chi phí giữ nhãn giả định theo người dùng nếu chưa có nguồn thật.
- Đạt trần: dừng submit, thu phần inflight, hiện “Đạt ngân sách ảnh nội bộ”. Không tự chuyển account để né giới hạn hoặc tín hiệu bot.
- Tần suất và giới hạn thật của provider vẫn có hiệu lực; trần 100–200 không bảo đảm tránh unusual activity.
- Chuỗi based_on và Character/Base references giữ đúng project/session. Thay account cho workload hợp lệ mới cần kiểm mapping, không mang media ID sang account khác như asset sẵn có.

## 6. Ba lần phục hồi có điều kiện

Lưu recovery_attempt_count theo operation/request/error episode, không reset khi thay chat hoặc đổi tên target. Đề xuất tối đa ba hành động phục hồi tổng cộng sau lỗi ban đầu; config/cap hiện hành nếu chặt hơn vẫn áp dụng.

| Loại sự cố | Hành động |
|---|---|
| Lỗi mạng/load trước gửi, chắc chắn not_submitted | Có thể reconnect/reload có chờ, tối đa ba lần trong phạm vi operation; không tăng submit |
| Đã có media ID nhưng tải lỗi | Retry download/collect cùng kết quả, tối đa ba lần; không tạo ảnh lại |
| Timeout sau submit, ambiguous/unknown | Chỉ đối chiếu request cũ. Không “retry tạo lại” ba lần |
| Login hết hiệu lực được xác nhận | Dừng operation, thông báo cần đăng nhập lại đúng service/account; không thử login giả hoặc xoay account |
| Quota/429, 503 theo chặn hiện hành, CAPTCHA, bot/unusual activity | Dừng phát mới trong phạm vi liên quan; giữ bằng chứng. Không lặp đủ ba rồi chuyển account |
| Lỗi nội dung hoặc output kỹ thuật có thể sửa | Sửa đúng phạm vi/revision và caps; không dùng đổi account như biện pháp sửa |
| Ba lần phục hồi tạm thời không thành công | needs_attention với lỗi/thao tác đã thử; không thử vô hạn hoặc tự đổi provider/account |

Bot warning là tín hiệu dừng ngay, không phải loại lỗi phải tiêu đủ ba lượt. Những thử lại theo hướng dẫn provider chỉ sau điều kiện chờ được đáp ứng, xác minh trạng thái request và quyền thực hiện; không tự vòng vô hạn.

## 7. Auth cho Colab và Chrome/Flow

Ba lớp status độc lập: hồ sơ phát hiện; login; service/runtime khả dụng.

### Colab

- File token tồn tại → “Có thông tin đăng nhập; chưa kiểm”.
- Read-only authenticated call thành công → “Đăng nhập hợp lệ”, timestamp.
- OAuth hết hạn/revoked/login-required được xác nhận → “Cần đăng nhập lại”.
- GPU quota/T4 unavailable/VM capacity → “Tài nguyên chưa khả dụng”, không “đã đăng xuất”.
- Không đọc được vì network/timeout → “Không xác minh được”, không suy token sai.
- Units=0 không tự suy login hỏng hay không dùng được free runtime; kiểm capability thực theo điều kiện provider. Không hứa free GPU được cấp.

Không cấp T4 hoặc upload chỉ để kiểm auth. User tự OAuth; không in URL/code/token vào report/frontend.

### Chrome/Flow

- Directory/cache metadata → “Phát hiện profile”, chưa là login.
- Kiểm trang Flow đúng profile và identity, project/model/refs → status riêng.
- Trang login/sign-in_required xác nhận → “Cần đăng nhập lại Flow”. Chỉ dùng chữ “Đã đăng xuất” khi có bằng chứng rõ.
- Permission/project thiếu, quota, bot hoặc 403 không rõ → status đúng nguyên nhân/không xác định; không gộp thành auth expired.
- Google account login không tự chứng minh Flow access; Colab và Flow auth độc lập.

Kiểm tuần tự theo nhu cầu, không mở toàn bộ profile cùng lúc và không chạy probe liên tục. Không xoá cookie/cache/session để thử sửa auth khi request còn cần evidence.

## 8. Dữ liệu và giao diện

Ledger thiết kế (schema chưa chốt): account identity/service, ownership workload, window start/end, runtime/session/device, intervals/usage/held budget, source/evidence/uncertainty, active operation, Flow submitted/generated/collected/unknown, auth status/check time, resource status, recovery episode/attempts và block reason.

Ghi bằng công cụ chính thức, event append-only và khóa thống nhất across chats; không sửa journal/revision/SQLite tay. Secret giữ kho auth hiện có, không copy vào ledger/Colab/frontend/Git.

Tab Tài khoản mỗi account có vòng/giờ/cửa sổ, auth, runtime T4, số ảnh/trần, active, pending/inflight và lý do chưa dùng được. Tab Colab & xử lý có session intervals/checkpoints. Tổng quan chỉ tóm tắt active Colab/Flow và vấn đề cần người dùng.

Hết 24 giờ đổi nhãn “Đến mốc kiểm lại”, không tự xanh “GPU đã hồi phục”. Chỉ định account và pool auto có nguồn lựa chọn rõ; không bất ngờ đổi default global khi chỉ thay phiên.

## 9. Tiêu chí nghiệm thu

- Không kết nối runtime: đồng hồ chưa bắt đầu; token không làm ring thành live quota.
- Hai chat cùng account dùng chung usage; mở lại không reset clock/counters.
- Idle VM còn cấp vẫn tính; mất kết nối hiển thị uncertain; interval qua ranh giới chia đúng.
- 5 giờ trần/1 giờ dự phòng đúng; tasks mới không phát khi ngân sách thiếu.
- Window 24 giờ hết không giả quota reset; T4/units0 được phân biệt với auth.
- Flow counters không giảm do unknown/download fail hoặc đổi profile cùng account.
- Ba lần recovery không tạo duplicate; bot/quota/auth dừng đúng, không rotate bypass.
- Đổi default không đổi owner inflight; pin user được giữ.
- Không gọi reviewer; nặng vẫn ở Colab; chỉ ledger/control nhẹ local.

## 10. Tiến độ

Đã đọc nguồn chính thức, đối chiếu account/auth/request code và bổ sung thiết kế. Chưa live auth probe, allocate GPU, chạy Flow, đổi accounts/preferred/config, tạo ledger hoặc sửa runtime/Rules/Skills. Không tuyên bố quota/mốc hồi phục thật đã xác minh.
