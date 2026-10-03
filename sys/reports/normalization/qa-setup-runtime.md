# QA độc lập setup/UI/runtime — 03/10/2026

Kết quả hiện tại: **14/14 tình huống độc lập đạt, 4,574 giây**, không failures/errors. Hash toàn bộ 16 nguồn liên quan giữ nguyên trước/sau lượt chạy. Lệnh: `.venv/bin/python -m unittest discover -s tests -p test_independent_setup_runtime.py -v` từ sys. Đây là kiểm mục tiêu trên mã hiện tại, không dùng tổng test cũ hoặc fixture để chứng nhận dịch vụ thật.

QA chỉ thêm `tests/test_independent_setup_runtime.py`, browser fixture `tests/test_independent_setup_browser.mjs` và các `reports/normalization/qa-setup-runtime*`; không sửa runtime, tài khoản, job hoặc daemon thật. Root tiếp tục sở hữu thử T4/Flow/OAuth và sự cố đợt audio thật.

## Phạm vi bằng chứng

- HTTP server thật chỉ bind loopback/ephemeral port cho sys/home tạm. Browser Chrome headless dùng profile tạm riêng, chỉ truy cập HTTP fixture; không dùng profile Google của người dùng hoặc trang Flow.
- Async/setup/permission/lock/session/pin/file containment chạy code thật. Callback Colab giả được ghi số lần gọi để chứng minh không gửi trùng hoặc generation lại; không có T4/provider thật.
- `probe_flow` chạy code thật nhưng response status/account UI được mock; chứng minh exact-profile gate và đúng lệnh account-inspect, không chứng minh auth thật.
- UNIX server dùng official session.mjs/controller/attempt-store sao chép vào sys tạm. Chỉ status/inspect trước connect; Node listener thật không mở browser hoặc gọi provider. Python/Node hash path được đối chiếu trên thư mục rất dài; socket vẫn dưới108 byte.
- Fresh control_start chạy official bootstrap helper với package Playwright1.58.2 và core đã cài được sao chép vào runtime tạm; ESM loader thực, không repo node_modules. Chứng minh import/start/reuse; không lấy đây làm thử tải package qua mạng. Bằng chứng npm install riêng do profile_setup_worker lưu tại bootstrap-control-proof.json.
- Peer UID sai được tiêm vào SO_PEERCRED của kết nối UNIX thật để kiểm nhánh từ chối; không tác động tiến trình của user khác. Mode/symlink và socket hợp lệ kiểm bằng filesystem/kernel thật.

## Phát hiện và xác nhận sửa

| Mã | Reproduction trước sửa | Sau sửa đã kiểm |
|---|---|---|
| QA-S01 | Python bridge nhận socket symlink và đi tới endpoint khác. | Chặn trước gửi; generation_submitted=false. |
| QA-S02 | Python bridge nhận socket mode0666. | Chỉ private owner/socket mode0600, parent0700; mode sai bị chặn trước gửi. |
| QA-S03 | Client không kiểm peer UID. | SO_PEERCRED UID khác bị chặn, không gửi byte lệnh; generation_submitted=false. Nhánh UID sai dùng injection như mô tả scope. |
| QA-S04 | Browser thật trên fixture chưa allocation chỉ ghi Ngân sách Colab, chưa đánh dấu ngân sách nội bộ. | Card ghi Ngân sách Colab nội bộ trước allocation; Flow chỉ đếm3/150 và unknown3, không time ring. |
| QA-S05 | getting-started còn chỉ jsonschema/Pillow, bỏ Node/Playwright/control-start nên clone không tìm được đường bật Flow daemon. | Guide mô tả Node, pinned control dependency, shared runtime, không repo node_modules/browser download, control-start/status và quyền. |

Trong lúc worker đang thêm bootstrap path, QA rà được command thiếu `serve` và parse identity:null của listener not_connected. Worker đã sửa trước lượt helper chính thức của QA; helper/listener thực hiện nay khởi động và reuse được. Đây là phát hiện khi review mã đang phát triển, không báo là reproduction live.

Nguy cơ collect output symlink đã được kiểm và **không tái hiện**: resolve/authorize containment chặn trước callback provider, thư mục ngoài giữ rỗng. Không đưa nghi ngờ này thành lỗi còn mở.

## Hành vi và đối chiếu yêu cầu

| Yêu cầu | Bằng chứng hiện tại | Giới hạn |
|---|---|---|
| Setup có quyền đúng scope/source | HTTP production grant, source rỗng và CSRF sai đều403 trước callback; thao tác đúng được nhận async. | Nguồn grant do operator ghi, không transport authentication/sandbox. |
| Không duplicate giữa controller/account alias | Hai alias cùng verified fixture identity; controller hiện tại chặn request lặp; Dashboard mới vẫn bị persistent account lock chặn. | Callback provider giả, không allocation T4. |
| HTTP vẫn quan sát khi setup chạy | GET state trả200 và thấy running operation trong khi callback bị giữ; kết thúc dùng đúng runtime đã chỉ định. | Server/home fixture, không server của root. |
| Collect-only đúng owner/request | Render journal ambiguous và immutable revision request được thu bằng account/runtime gốc, collect_only=true; default mới không đổi pin; account sai không gọi provider. | Không thu ZIP/provider file thật. |
| Binding theo job bền | Job runtime override giữ qua default mới và fresh Sessions; request pin cũ không đổi. | Bằng chứng logic; không chứng nhận allocation/auth. |
| Flow probe chỉ đọc | Profile sai không gọi account-inspect; profile đúng chỉ gọi tool-snapshot:account-inspect và không connect/start/generate. | UI account response mock. Root sở hữu live exact-profile Google identity proof. |
| Counter khác nhau | Browser thực: Flow không có ring giờ, counter3/150/unknown3/internal cap; Colab có ring và chữ nội bộ. | Dữ liệu ledger giả; không quota nhà cung cấp. |
| Clone không phụ thuộc repo node_modules | Official loader/control_start từ sys tạm không repo dependency link; listener status not_connected, browser_started=false/provider_called=false; startup lần2 reuse đúng tiến trình. | Dùng copy package pinned đã cài, không phép install mạng của QA. |
| Socket dài/chủ thể | Python và Node cùng UID/root hash, byte path<108; daemon có parent0700/socket0600; client mode/symlink/peer mismatch bị chặn. | Không thử peer user khác thật. |
| Tài liệu đúng đường setup | Guide mới có Node/Playwright/control-start; helper thực đã chạy. | Toàn provider/browser connection/auth vẫn kiểm riêng. |

Các mục trong audit toàn kế hoạch được bổ sung bằng chứng: Q01 quyền thao tác web/setup; Q08 ownership/controller; Q17 bootstrap clone; Q18 account/profile/pin/binding; Q19 counters ngân sách nội bộ; Q20 collect-only journal. Các test này **không hoàn tất Q21/Q22/Q28 về audio/T4/render/ảnh/video thật**, không chứng minh câu chuyện/mascot/phát âm/payoff hoặc khả năng nghe/xem dịch vụ của runtime thật.

## Artifact fixture

Screenshot đã được QA mở xem: `qa-setup-runtime-browser.png` hiển thị ba account fixture, selector grant/source, controls runtime và Flow counter khác Colab ring. JSON browser ghi `fixture=true`, `live_provider=false`, lỗi JS rỗng. Đây là ảnh giao diện chạy thật trên metadata giả, không evidence tài khoản người dùng.

`qa-setup-runtime.json` lưu output14 test đầy đủ, hash trước/sau ổn định, scope và phát hiện. Giữ test để ngăn tái phát. Nếu root tiếp tục đổi code liên quan, kiểm lại đúng phạm vi; không chạy lại cả tổng469 chỉ để tăng count. Thiếu media/provider thật vẫn do root kiểm và báo đúng limitation.
