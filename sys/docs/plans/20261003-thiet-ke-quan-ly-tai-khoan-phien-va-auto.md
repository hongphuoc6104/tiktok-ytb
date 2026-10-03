# Thiết kế quản lý tài khoản, phiên làm việc và kiểm duyệt tự động

**ĐÃ ĐƯỢC ĐÍNH CHÍNH bởi yêu cầu mới hơn:** auto là tự lập kế hoạch/thực hiện đến kết quả, không gọi kiểm duyệt; xử lý nặng phải đưa lên Colab. Phần auto review, tab Kiểm duyệt và render local trong bản này không còn là thiết kế đích. Xem [bản 0.3 hiện hành](20261003-thiet-ke-colab-va-auto-thuc-hien.md). Giữ bản này làm lịch sử thảo luận và inventory account.

Ngày: 03/10/2026. Bản thảo nghiệp vụ 0.2.

**Đã chốt hướng:** người dùng chấp nhận làm trang quản lý trực quan tại máy. **Chưa triển khai:** bản này là thiết kế và rà soát nền hiện có; không đăng nhập, cấp T4, đổi tài khoản mặc định, chạy job hoặc sửa runtime.

Yêu cầu bổ sung: hạn chế tối đa tài nguyên local; lấy danh sách profile trên máy; quản lý login Colab CLI và account/profile dùng Flow; chuyển nhanh; setup tài khoản lần đầu; lần sau chọn mặc định nhiều tài khoản cho phiên; quản lý kịch bản/lời thoại/cảnh/audio/ảnh/video; auto review cập nhật sản phẩm và tiếp tục khi đạt.

## 1. Bằng chứng kiểm tra trong lượt này

- Đã chạy `python3 -m colab_bridge.accounts list` từ sys, đúng quy định trước thao tác Colab. Kho có account-01…05, enabled=true và authenticated=true theo phép kiểm **file token tồn tại**. Preferred hiện là account-02. Chưa kiểm token còn hiệu lực, sessions live, GPU hoặc quota.
- Đọc metadata profile, không đọc/xuất cookie, password hay token, không mở trình duyệt. Trong các thư mục browser chuẩn Linux, các thư mục google-chrome* trực tiếp dưới .config và vùng .gflow của dự án: có 12 user-data roots, 34 thư mục profile hiện tồn tại. Chrome chính có 15 profile; Brave có 1; 18 thư mục còn lại ở các root phục vụ kết nối/dự án. **34 thư mục không phải 34 tài khoản khác nhau**, chưa xác định account trùng giữa các bản profile.
- Một số Local State của các root chuyên dụng giữ metadata profile không còn thư mục. Những bản ghi này phải hiển thị không khả dụng, không tính là profile dùng được. Không sửa/xóa Local State trong lượt kiểm tra.
- Phạm vi inventory là nơi có thể phát hiện theo các root nêu trên. Root tuỳ biến ngoài đó cần người dùng thêm đường dẫn; không tuyên bố đã quét mọi vị trí trên mọi ổ đĩa.
- Flow cần đối chiếu profile thực, account đang hoạt động, project/tool, model và Character/Base references. Profile có nhãn tài khoản chưa chứng minh vào Flow được.
- Account picker Colab hiện chỉ chọn một preferred trước request; chưa có hợp đồng chọn nhiều tài khoản theo phiên dashboard. Runtime giữ account/session cho request dở.
- Mode review/auto của job hiện được hash và ghi workflow_created; không được sửa giữa chừng. Auto cần review artifact thật và caps; không chỉ chạy nối các công đoạn.

## 2. Tám tab quản lý chính

| Tab | Chức năng | Phần con |
|---|---|---|
| Tổng quan & phiên | Chọn tài khoản/preset/mode mặc định cho công việc mới; tiếp quản việc dở; tài nguyên và việc cần người dùng | Phiên hiện tại, preset phiên, bàn giao |
| Tài khoản | Danh sách toàn bộ profile/hồ sơ được phát hiện, login và kiểm khả dụng theo dịch vụ | Google Flow, Colab CLI, dịch vụ reviewer nếu được chọn |
| Công việc & hàng đợi | Job và thứ tự thực hiện, trạng thái content/media/video, request đang chạy/unknown, dừng/tiếp tục | Từng job, hàng đợi hữu hạn, request |
| Kịch bản & cảnh | Brief, lời thoại Việt/Anh theo yêu cầu, storyboard, chữ, images/beats và revision | Tổng thể, từng cảnh, yêu cầu sửa |
| Media | Tạo/thu/nghe/xem/sửa và liên hệ với cảnh | Audio, hình ảnh, phụ đề & timeline |
| Video & thành phẩm | MP4 chờ duyệt/thành phẩm, phiên bản, tỷ lệ, lỗi theo timestamp và hồ sơ xuất | Bản xem, thành phẩm |
| Kiểm duyệt | Review của người/máy, tiêu chí, evidence, quyết định và vòng sửa | Chờ duyệt, máy đang kiểm, lỗi cần can thiệp, lịch sử |
| Cấu hình & nhật ký | Presets, nguồn prompt/Rules/Skills, vai trò/quyền, tài nguyên, issue logs và setup | Prompt & hướng dẫn, cấu hình máy, phân quyền, nhật ký |

Trang giới thiệu là màn hình vào trước tab quản lý; không cần một tab riêng luôn chiếm chỗ. Setup lần đầu là luồng dẫn trong Tài khoản/Tổng quan. Giữ cùng danh tính job/scene/revision ở mọi tab; không tách audio/ảnh/lời thoại thành các tài liệu tự sống độc lập.

## 3. Tài khoản, profile và session là ba đối tượng khác nhau

- **Tài khoản:** danh tính đăng nhập vào dịch vụ, có khả năng/quyền khác nhau.
- **Profile:** môi trường browser lưu đăng nhập; một account có thể xuất hiện trong nhiều profile và một profile có thể chứa nhiều Google accounts.
- **Session:** kết nối/VM/browser đang dùng cho một đợt; account+profile+project thật tại lúc gửi phải được ghi.

ID profile dùng browser + đường dẫn root chuẩn hoá + profile_directory, không chỉ tên “Profile 1” hay nhãn “Work”. Dedupe theo đường dẫn thật để tránh symlink; có thể nhóm account trùng khi identity được kiểm, nhưng vẫn giữ mỗi profile path riêng. Không hợp nhất cookie/token giữa các root để tiết kiệm.

Colab CLI OAuth và Flow browser login độc lập dù dùng cùng email. Profile Chrome đăng nhập Google chưa tự tạo login Colab CLI; token Colab chưa tự chứng minh quyền Flow.

## 4. Quét và đăng nhập tiết kiệm tài nguyên

### Lần đầu

1. Quét metadata và registry, lấy toàn bộ profile trong root được phát hiện; không mở N browser.
2. Hiện nguồn/path/nhãn, thư mục còn hay mất, tình trạng đăng nhập theo mức đã biết.
3. Cho chọn toàn bộ hoặc nhóm account cần kiểm Flow; kiểm thực tế tuần tự bằng số browser nằm trong ngân sách, trả tài nguyên khi xong và an toàn.
4. Với profile cần login, mở đúng profile. Người dùng thực hiện OTP/CAPTCHA. Không nhận password/cookie trong chat.
5. Liên kết project/tool và references ở từng account; không dùng media ID của project khác như reference khả dụng.
6. Colab đọc account store; thêm tài khoản qua OAuth do người dùng hoàn tất. Kiểm CLI account/session không cấp GPU chỉ để kiểm login.
7. Lưu preset phiên và báo configured/verified/missing/not_tested/unsupported cho từng khả năng.

### Những lần sau

Mở trang chọn preset đã lưu: account Flow nào dùng, Colab nào dùng, account ưu tiên, mức tài nguyên, mode mặc định cho job mới. Hiển thị trạng thái đã kiểm và độ mới; kiểm lại khi thiếu evidence, hết hạn hoặc trước thao tác cần trạng thái hiện hành. Không bắt đăng nhập lại tất cả hoặc mở tất cả account chỉ để xem danh sách.

Các hành động trên trang account: quét lại danh sách, thêm root, đăng nhập, kiểm khả dụng, chọn cho phiên, đặt ưu tiên, mở đúng profile, tắt sử dụng trong phiên. “Tắt sử dụng” không xoá token/profile; đăng xuất/xóa là hành động riêng có phạm vi cụ thể và không làm mất request dở.

## 5. Chọn nhiều và chuyển nhanh

Chọn nhiều account tạo **tập account được phép dùng trong phiên**, không đồng nghĩa khởi động mọi account hoặc gửi đồng thời. Ví dụ chọn Flow A/B và Colab 02/03; ưu tiên Flow A và Colab 02; với preset tiết kiệm chỉ mở một browser phục vụ Flow và một phiên TTS chuyên dụng khi cần.

Chuyển nhanh có ba trường hợp:

- Chưa gửi: chọn account mới cho việc tiếp theo sau kiểm project/reference/login tương ứng.
- Đã gửi/đang chạy: account/session của request đó giữ nguyên; lựa chọn mới chỉ áp cho request mới chưa được gán/submit. Không chuyển inflight sang account khác.
- Unknown/ambiguous: giữ account/session và evidence để reconcile/collect. Không dùng chuyển nhanh để gửi thay hoặc chạy vòng qua quota/503/CAPTCHA.

Một chuỗi based_on cần reference khả dụng tại project đích. Mặc định giữ chuỗi trên cùng session/project; chuyển chuỗi chưa gửi chỉ sau khi xử lý đủ mapping/reference theo đường được hỗ trợ. Không giả media ID portable.

Với Colab, request đã gửi/VM đang giữ model tiếp tục đúng account/session. Chọn Colab 03 không khiến request của 02 được gửi lại. Giải phóng VM riêng sau khi thu kết quả của đợt theo chính sách, không giải phóng session người dùng khác.

Lỗi hạn mức/503/CAPTCHA/login vẫn là điểm dừng, không tự xoay account. Ngay cả account khác đã chọn trong tập phiên cũng không tự trở thành đường vượt chặn.

## 6. Preset phiên và job

Preset phiên lưu: tên, account IDs được chọn theo dịch vụ, ưu tiên, ngân sách local, preset sản xuất và mode mặc định **cho job mới**. Không lưu secret, không viết vào config sản phẩm để đổi giọng/gate.

Khi tạo job: xác định brief/mode/quyền nhiệm vụ; ghi provenance preset. Khi gửi từng request: chốt account/profile/project/session thực và request ID. Không chỉ lưu tên preset rồi tra lại giá trị mới để collect request cũ.

Chat mới thấy preset và bàn giao, nhưng kiểm đúng checkout/job/quyền trước run. Nút “Bắt đầu phiên” áp lựa chọn phiên, không tự bắt đầu queue/video. Resume job cũ giữ mode/quyết định/request mapping của job đó.

## 7. Hạn chế tài nguyên local

Preset mặc định đề xuất **Tiết kiệm**, cần đo và triển khai mới được gọi hiệu lực:

- Dashboard nhẹ, một backend tại máy và dùng service đang có nếu tương thích; không watcher quét liên tục mọi file.
- Quét metadata on demand; kiểm login theo tài khoản được chọn hoặc đợt kiểm tuần tự; không browser cho từng hàng danh sách.
- Giới hạn tổng browser **do dự án quản lý**, đề xuất 1 ở bản đầu; không tính chọn nhiều là mở nhiều. Không đóng browser cá nhân ngoài quyền.
- TTS Colab theo preset được chọn; model nặng trên T4; không cài/chạy local TTS song song nếu không cần. Đề xuất 1 phiên TTS riêng tại một thời điểm cho preset đầu.
- Render có ngân sách riêng, đề xuất 1 job và concurrency thấp trong chế độ tiết kiệm; không hứa một process bằng một CPU thread.
- Thumbnail/cache nhỏ, tải ảnh full/audio/video khi mở; không autoplay nhiều WAV/MP4; chỉ một player hoạt động.
- Snapshot/sự kiện nhẹ; giảm tần suất khi tab ẩn/rảnh; không live probe mọi account liên tục. Telemetry đo mức dùng thực, không tạo phần trăm readiness giả.
- Dịch vụ/browser idle chỉ đóng khi thuộc phiên dự án, không còn inflight/unknown/evidence cần giữ; thu xong Colab thì giải phóng VM riêng.
- Ngân sách dùng chung cho mọi job/chat của dự án, không mỗi chat tự tạo worker và tự coi mình trong cap.

RAM/CPU/disk thresholds cần kiểm máy thật rồi chốt, không đặt giả các mức cam kết. “Tiết kiệm” có thể giảm tốc độ; giao diện cần thể hiện việc đang chờ tài nguyên. Giới hạn runtime/acceptance hiện tại vẫn áp dụng; không mở concurrency từ bản thiết kế.

## 8. Kịch bản, cảnh và media nối nhau

Một cảnh hiển thị: purpose/action, narration theo ngôn ngữ, chữ được phép, images/beats, references, audio liên quan và thời điểm trong MP4. User chọn scene rồi xem/sửa đúng mục, không tìm file thủ công.

Mọi sửa có impact preview:

- Narration/ý học thay đổi → reject content, revision mới; xác định audio/media/video phụ thuộc cần tạo/duyệt lại.
- Chỉ ảnh sai → reject target media; giữ audio nếu hợp lệ; media/video cập nhật theo workflow.
- Chỉ cách đọc sai → reject audio đúng cảnh; giữ lời dẫn nếu không đổi dữ liệu.
- Chỉ timing/render sai → sửa đúng đường timeline/render, không sửa lời dẫn ngầm.

Giao diện không ghi trực tiếp narration đã chốt vào revisions; không sửa anchor sau freeze như chỉnh văn bản tự do. Đề xuất được giữ riêng, rồi chuyển thành revision qua công cụ hợp lệ. Mỗi view hiển thị rõ revision đã duyệt, bản nháp và bản sửa chờ kiểm.

## 9. Auto kiểm duyệt: tiếp tục khi đạt, vẫn cập nhật mọi bước

Nút lựa chọn nên tên **Chế độ kiểm duyệt cho video mới**: người dùng duyệt / máy kiểm duyệt tự động. Có thể lưu mặc định trong preset phiên. Mode của job đã tạo hiện không đổi được; nếu muốn toggle giữa job là yêu cầu phát triển riêng, không tự sửa workflow.json hoặc tạo job thay cùng nội dung để né gate.

Với auto:

1. Content revision hoàn tất → cập nhật trang/chat → máy kiểm content.
2. Pass có báo cáo hợp lệ → media tiếp tục; không chờ click người dùng.
3. WAV/ảnh hoàn tất lần lượt → gửi artifact; đầy đủ media → máy xem/nghe thật.
4. Media pass → render → cập nhật MP4 → máy kiểm video thật.
5. Video pass và xuất hợp lệ → complete/mark đúng workflow.

“Không dừng lại” nghĩa không chờ duyệt thủ công khi đạt. Không có nghĩa bỏ kiểm, chạy tiếp khi fail/unsupported hoặc bỏ qua các chặn vận hành. Fail được sửa đúng phạm vi và trong cap; hết cap, thiếu capability nghe/xem, unknown, integrity, login/CAPTCHA/quota/503 → cần can thiệp/dừng theo chính sách.

Tab Kiểm duyệt luôn có actor, phần/revision, tiêu chí, report/evidence, lỗi và sửa đã thử. Machine report không được thay bằng check metadata. Không cho bật auto sản xuất nếu reviewer chưa được xác định và xác minh capability tương ứng. Giao diện cần cho xem report thiếu capability thay vì chỉ disable không lý do.

Nút Dừng vẫn hoạt động trong auto. Sau khi dừng/tiếp tục, giữ mode của job và lịch sử quyết định.

## 10. Trạng thái khả dụng cần tách

Mỗi account/profile hiển thị ba lớp:

1. Phát hiện/cấu hình: thư mục và hồ sơ có tồn tại không.
2. Đăng nhập: có thông tin lưu, đã xác minh live hay cần đăng nhập lại.
3. Khả năng dịch vụ: Flow access/project/model/reference; Colab session/T4; reviewer nghe/xem.

Có thể configured nhưng login chưa kiểm; login verified nhưng chưa có T4. Không gộp những trạng thái này thành “account khả dụng” chung. Timestamp, nguồn kiểm và lỗi cần có. Quota/credits chỉ ghi số nếu nguồn thực cho biết; không suy 0-credit hoặc T4 available từ profile/token.

## 11. Những phần nghiệp vụ còn thiếu cần đưa vào triển khai

- Account registry thống nhất theo dịch vụ, adapter browser/CLI giữ nguồn token/profile tại chỗ; session selection scoped, không thay global preferred khi user chỉ chọn cho phiên.
- Discovery đọc metadata, dedupe roots, stale entry classification; root thêm tay và kiểm browser được hỗ trợ.
- Live capability check tuần tự, output được làm sạch; Colab đăng nhập có phiên chờ user, không giữ token trong dashboard state.
- Ownership request/chain/session và ngân sách tài nguyên chung giữa nhiều chat.
- Read-only observe, artifact event, stop trước submit; UI không poll status có side effect.
- Cơ chế chuyển tài khoản cho pending request và thu old request riêng; không restart browser mù.
- Auto reviewer readiness, báo cáo thật, caps; chọn mode trước new job.
- Revision/impact preview dùng contract hiện có, validation khi đồng thời sửa hoặc click trùng; request thao tác idempotent.
- Phân quyền thao tác trên trang: người dùng quyết định review, agent điều phối, worker target, developer diff; không bật quyền từ tab cấu hình đơn giản.
- Local server bind loopback, kiểm thao tác theo nguồn phiên, không cho trang khác gửi lệnh qua browser; không lưu secret trong frontend/report/Git. Đây là thiết kế khi triển khai, chưa là sandbox bảo mật với agent có toàn quyền máy.

## 12. Thứ tự triển khai sau thiết kế

1. Đồng bộ Rules/Skills/entry points với nghiệp vụ trên; inventory checkout và protected changes.
2. Bootstrap và account discovery/readiness; trang Tài khoản + chọn preset phiên. Giữ nguồn auth hiện có.
3. Observe/ownership/resource budget/stop/recovery và session routing.
4. Trang job/kịch bản/media/video, artifact preview và impact revision.
5. Kiểm duyệt review/auto, machine capability thật và auto continuation.
6. Nghiệm thu fresh clone/chat mới/đa account/stop/unknown/mode/resource trước thử hướng video mới.

Không triển khai riêng nút account switch hoặc auto toggle trước cơ chế kiểm tương ứng.

## 13. Tiêu chí nghiệm thu chính

- 15 profile chính đều hiện từ metadata, không mở 15 browser; stale entries không coi là khả dụng.
- Profile có tên trùng hoặc cùng “Profile 1” ở root khác không bị gộp nhầm.
- Token tồn tại nhưng hết hiệu lực được báo chưa kiểm/cần login đúng, không ready giả.
- Chọn nhiều account vẫn tuân ngân sách browser/VM/render; mỗi session giữ quyền sở hữu.
- Chuyển mặc định không làm request đã gửi đổi account hoặc tạo bản gửi trùng.
- Quota/CAPTCHA/503 không dẫn đến auto rotate; based_on/reference giữ đúng project.
- Auto pass đi tiếp và artifact vẫn cập nhật; fail/unsupported/cap dừng đúng nguyên nhân.
- Job review cũ không đổi mode từ preset mới; chat mới không nhân đôi runner/VM.
- Thay narration/ảnh/audio ảnh hưởng đúng phần; revision/hash cũ không được dùng duyệt bản mới.
- Không lộ token/cookie/OAuth code; đóng phiên không chạm browser/VM ngoài sở hữu.

## 14. Quyết định và tiến độ

Đã chốt: trang local trực quan; quản lý tài khoản/đa lựa chọn phiên, ưu tiên tiết kiệm local, sản phẩm theo cảnh và kiểm duyệt auto có cập nhật.

Đã làm: kiểm metadata/profile và account list, đọc cơ chế hiện tại, thiết kế 8 tab và ghi phụ thuộc cần phát triển.

Chưa làm: live account check/login, thay preferred/account config, OAuth/GPU, tests runtime, sửa code/Rules/Skills, chạy job hoặc đổi mode. Mô phỏng UI chỉ phục vụ thảo luận.
