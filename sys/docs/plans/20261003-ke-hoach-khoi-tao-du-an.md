# Kế hoạch phát triển phần khởi tạo dự án

Ngày: 03/10/2026. Phiên bản đề xuất: 1.0.

**Trạng thái: đã phân tích và lập kế hoạch; chưa cài đặt, đăng nhập, sửa mã hoặc chạy sản xuất.** Theo yêu cầu mới nhất, ưu tiên phần khởi tạo trước kế hoạch sửa phân quyền và kiểm soát. Kế hoạch điều chỉnh hướng video vẫn giữ riêng.

## 1. Kết luận: hiện có gì và thiếu gì?

Không phải hoàn toàn chưa có hướng dẫn. README có mục môi trường; INDEX có bản đồ và điểm vào; docs/colab-tts.md có cài CLI/OAuth; docs/flow-queue-operations.md có cấu hình máy; các skill có quy trình sản xuất. Tuy nhiên chưa có một luồng clone mới, từng bước, phân rõ việc agents làm và việc người dùng làm, có khả năng kiểm tra/resume và kết luận sẵn sàng theo từng chức năng.

Doctor hiện cần import các phụ thuộc của Pilot trước khi chạy, nên không giúp được bước đầu trên máy thiếu jsonschema/Pillow. Nó chủ yếu kiểm tool trên PATH và sự tồn tại của môi trường; chưa xác nhận đầy đủ login, profile, project, references, asset, render và hỗ trợ review media. Trên máy mới, một kết quả doctor không đủ để tuyên bố sẵn sàng tạo video.

### Bằng chứng đã kiểm tra

| ID | Nguồn | Phát hiện |
|---|---|---|
| I01 | README.md, INDEX.md | Có hướng dẫn môi trường rời rạc, chưa có checklist khởi tạo thống nhất; một số lệnh được đưa trước phần cài phụ thuộc |
| I02 | sys/requirements.txt, package.json/package-lock.json, TTS lockfiles | Core có jsonschema/Pillow; Node có lockfile; local TTS dùng môi trường riêng. Node chưa có pin dự án rõ; các Python được README mô tả riêng theo backend |
| I03 | sys/pilot.py | Doctor import Pilot trước; check công cụ/file chưa phải kiểm vận hành hoặc chất lượng thật |
| I04 | git ls-files và git status tại worktree | Mã đang phát triển còn thay đổi chưa commit. reference-narrator và một số tệp hỗ trợ review hiện có local nhưng chưa được Git theo dõi. Clone commit hiện tại không nhận toàn bộ khả năng của working tree này |
| I05 | .gitignore | Venv, node_modules, runs, SQLite, profile, token và machine.local bị bỏ qua đúng mục đích; cần phân biệt tài nguyên bắt buộc với dữ liệu chỉ thuộc máy cũ |
| I06 | browser-profiles.json, renderer/render.mjs | Cấu hình browser chứa home/profile của máy khác; renderer có đường dẫn Chrome cố định. Clone về máy mới chưa portable |
| I07 | machine.local và b2_bridge/controller/session | Có cơ chế cấu hình riêng theo máy/session, nhưng chưa có mẫu và luồng thiết lập thống nhất cho người mới |
| I08 | README của B-2; flow-queue-operations.md | README B-2 còn mô tả harness chưa tích hợp, trong khi tài liệu vận hành mô tả hàng đợi đã tích hợp. Cần phân loại lịch sử và nguồn hiện hành |
| I09 | config canonical_character; mascot reference đã tracked | Ảnh mascot portable; media ID/project registration là tài nguyên tài khoản, chưa chứng minh dùng được tại project mới |
| I10 | docs/colab-tts.md, colab_bridge | Có account store, login, start/setup/collect và journal; login phải do người dùng OAuth. Các bước login và cấp T4 cần tách, không cấp phiên GPU để kiểm login |
| I11 | README, docs/workflow, docs/machine-review-setup | Review và auto cần capability khác nhau; mô tả reviewer giữa các tài liệu còn cũ/khác nhau. Clone mới không được tự yêu cầu một dịch vụ viết hoặc review ngoài phạm vi đã chọn |

Phạm vi: phân tích từ các tệp repo/worktree hiện có. Chưa thử một fresh clone hoặc xác minh remote chứa các thay đổi local. Không đọc/in token, không sao chép browser credentials và không kiểm live generation trong lượt này.

## 2. Mục tiêu của phần khởi tạo

Một người clone đúng bản dự án có thể biết chính xác:

1. Máy cần công cụ nào, phiên bản nào và tài nguyên nào.
2. Những gì lấy từ Git, những gì cần cài/tải/import riêng.
3. Người dùng cần đăng nhập dịch vụ nào, bằng profile nào.
4. Agents phải đọc gì và được tự thiết lập tới đâu.
5. Bước nào đã đạt, bước nào thiếu và cách tiếp tục sau khi gián đoạn.
6. Có thể làm content, audio, images, render hay auto review đến mức nào.
7. Setup hoàn tất chưa đồng nghĩa job hoặc công cụ Flow được nghiệm thu sản xuất.

Phạm vi đầu tiên đề xuất: Linux đúng kiến trúc đã kiểm chứng; ưu tiên chế độ review và preset tiếng Anh/Colab/Flow phù hợp yêu cầu hiện tại. OS khác trả unsupported hoặc chỉ dẫn thủ công rõ; chưa tuyên bố hỗ trợ đầy đủ Windows/macOS.

## 3. Những gì cần cài và ai thực hiện

| Thành phần | Bắt buộc khi nào | Việc agents có thể thực hiện sau khi được yêu cầu setup | Việc người dùng cần làm |
|---|---|---|---|
| Git | Clone/cập nhật | Xác minh checkout/commit, giữ thay đổi local, đọc repo | Cấp quyền repository nếu repo riêng; không gửi token trong chat |
| Python/uv | Core và quản lý môi trường | Kiểm phiên bản; tạo sys/.venv và cài theo manifest/lock đã chọn | Cấp quyền cài công cụ hệ thống nếu cần |
| Core Python | Điều phối | Cài đúng requirements; kiểm import thật trong venv | Không cần login |
| Node.js/npm | Flow bridge và renderer | Dùng phiên bản đã pin; npm ci theo package-lock; kiểm import/binary | Quyền cài công cụ hệ thống nếu thiếu |
| FFmpeg/ffprobe | Xử lý/đo âm thanh và video | Phát hiện path/version/codec cần thiết; cấu hình máy đúng | Quyền cài nếu thiếu |
| Google Chrome | Flow và renderer hiện tại | Phát hiện executable; tạo/chọn data dir chuyên dụng theo quyền; cấu hình CDP loopback/session | Chọn profile/account phù hợp và tự login Google |
| Colab CLI | TTS remote | Cài CLI theo phiên bản ghim, kiểm account/session không in secret | OAuth/OTP/CAPTCHA nếu có; cho phép cấp T4 riêng khi cần |
| Local TTS environments/models | Chỉ preset local TTS | Tạo .venv-tts/.venv-en theo lock riêng khi được chọn | Quyền tải model/asset cần thiết; quyền nguồn giọng |
| Mascot/voice package | Backend/brief yêu cầu | Kiểm file, hash, profile metadata; import gói đã được phép | Cung cấp gói giọng/reference thiếu hoặc quyết định cách lấy |
| Reviewer | Chỉ auto mode | Kiểm cấu hình và capability của reviewer được chọn | Login reviewer nếu backend đó yêu cầu; review mode không bắt buộc bước này |

Với preset English + Colab, không cài local model TTS nặng chỉ vì README cũ liệt kê. GPU local không bắt buộc. Core Python 3.12 lấy từ README hiện hành; bootstrap cần chạy bằng stdlib trên Python nền trước khi tạo core venv. Phiên bản Node sẽ được ghim sau kiểm tương thích với lockfile, không tự dùng bản mới nhất. Các phiên bản chưa kiểm là hạng mục phát triển, không phải cam kết hoạt động.

## 4. Người dùng cần đăng nhập gì?

### 4.1 Google Flow

- Dùng account có quyền truy cập Flow và project/tool cần dùng.
- Người dùng thực hiện login/OTP/CAPTCHA trong browser. Agents chuẩn bị và kiểm trang sau login, không nhận password/token/cookie trong chat.
- Clone Git không tạo project/tool trong tài khoản. Cần mở tool được phép, remix vào project nếu cần, rồi lưu URL thật của máy vào cấu hình local.
- Xác minh executable/profile thực tế, tool UI/model/ratio/reference và quyền project. Có cookie hoặc tên profile chưa chứng minh login Flow đang hợp lệ.
- Kiểm khả năng watermark từ tài khoản thật và ghi giới hạn; không hứa prompt có thể tắt dấu bắt buộc.

### 4.2 Google Colab

- Login CLI qua OAuth do người dùng hoàn tất; tận dụng account store có sẵn nếu hợp lệ.
- Login thành công không có nghĩa có T4. Tách bước cấp phiên GPU/setup model và chỉ chạy khi đã được phép.
- Giữ account/session của request đã gửi; không xoay account để vượt quota hoặc timeout.
- Không mua compute units. Nếu không được cấp T4, báo đúng thiếu năng lực audio remote, không âm thầm chuyển giọng/backend.

### 4.3 Các login khác

Git hosting chỉ cần khi repo/access yêu cầu. Reviewer chỉ cần khi chọn auto và backend đã được xác định. Review bằng người dùng không tự yêu cầu login reviewer. Không yêu cầu login dịch vụ viết kịch bản: người đang chat viết trực tiếp. Không đăng nhập hoặc publish YouTube/TikTok trong onboarding tạo video; publishing là phạm vi riêng.

## 5. Những gì clone phải mang theo

### 5.1 Gói repo portable

Mã nguồn đã được phép đưa vào Git; schemas; rules/skills hiện hành; README/INDEX; lockfiles; config mẫu trung lập; ảnh mascot; dữ liệu kho từ theo chính sách; manifest tài nguyên và mẫu cấu hình máy không chứa secret.

Cần kiểm release commit thực sự chứa toàn bộ module đang tham chiếu. Working tree chạy được không chứng minh clone sẽ chạy. Chuẩn bị bản diff/package được duyệt trước khi commit/push; không tự commit hoặc xuất asset giọng chỉ từ kế hoạch này.

### 5.2 Tài nguyên import hoặc tải riêng

- Gói giọng đã được phép phân phối/import, có profile và checksum. reference-narrator hiện local chưa tracked; không tự đổi giọng khi thiếu.
- Model weights theo backend được chọn; ghi model revision/license/source và nơi cache. Remote weights cài trong Colab cho preset remote.
- Local browser/session/project mappings. Media ID từ tài khoản máy cũ không portable; phải đối chiếu/đăng ký tại project đích.
- Dữ liệu job cần tiếp tục phải được người dùng chuyển riêng có kiểm soát. Fresh clone không tự có runs/SQLite. Ledger theo Git có thể giữ chỗ cho job không có trên máy mới: báo mismatch, không tự xóa/release/supersede.

### 5.3 Dữ liệu không clone/sync qua Git

Token/OAuth codes/password/cookies; browser data dirs; SQLite/runs/output cá nhân; account store; machine.local; cache model và venv. Không lấy profile/token từ máy khác làm shortcut. Gói chuyển dữ liệu nếu sau này cần là thao tác riêng, không mặc định của setup.

## 6. Agents phải đọc gì và thứ tự nào?

Thứ tự đề xuất cho lần đầu:

1. INDEX.md: chọn entry point, checkout và bản đồ.
2. AGENTS.md: quyền, giới hạn, yêu cầu mới nhất và điểm dừng.
3. sys/docs/getting-started.md: luồng người mới và phân công từng bước.
4. .agents/skills/vp-bootstrap/SKILL.md: chỉ dẫn setup cho người đang chat.
5. Manifest phụ thuộc và mẫu cấu hình của preset được chọn.
6. Tài liệu Flow/Colab tương ứng khi đến bước đó.
7. docs/workflow.md và vp-vocab/vp-content khi bắt đầu sản xuất sau setup.

Các tệp getting-started/vp-bootstrap/manifest mới ở đây là đề xuất cần phát triển, chưa tồn tại. Không giả đã nạp Rules hoặc setup trong phiên khác. Skill bootstrap không viết kịch bản, không tạo job, không gửi generation hoặc cấp quyền sửa code.

Agents tự làm việc trong phạm vi setup đã được yêu cầu: kiểm hệ thống, lập plan cài, tạo venv/phụ thuộc, ghi cấu hình local, kiểm asset và connectivity. Phần thiếu login cần người dùng thì chuẩn bị màn hình/lệnh đúng và báo cụ thể việc người dùng phải làm; không yêu cầu lại thông tin đã xác định và được phép dùng.

## 7. Luồng khởi tạo từng bước

| Bước | Việc phải làm | Đầu ra/bằng chứng | Điểm dừng |
|---|---|---|---|
| S0 - chọn bản | Đúng repository/branch/commit; phân biệt clone mới với checkout có job | Danh tính checkout; thay đổi local; inventory job/request | Nếu là checkout đang có job: không overwrite code/config hoặc reset dữ liệu |
| S1 - đọc và chọn phạm vi | Đọc INDEX/AGENTS; chọn preset và review/auto theo yêu cầu | Phiếu setup: preset, backend, login cần, downloads, phần người dùng làm | Thiếu quyết định quan trọng thì hỏi gọn; chưa gửi production |
| S2 - kiểm máy trước cài | OS/architecture, Python nền, Node, FFmpeg, Chrome, disk/network/perms | Plan missing/present/incompatible; lệnh dự kiến và đích cài | OS/architecture không hỗ trợ hoặc thiếu quyền hệ thống |
| S3 - cài phụ thuộc cục bộ | Core venv; Node theo lock; CLI Colab nếu preset chọn | Phiên bản thật, import thật, binary paths, install log đã che secret | Lỗi cài dừng đúng bước; không tự nâng lockfile/package versions |
| S4 - kiểm/import tài nguyên | Mascot, voice, model manifest, bank/ledger | File/hash checks; missing package; trạng thái dữ liệu job | Thiếu voice/reference bắt buộc hoặc ledger/job mismatch |
| S5 - cấu hình máy | Chrome executable/profile/CDP; Flow tool/session; runtime paths | Cấu hình local schema-valid, chmod phù hợp, Git ignored | Không lấy home/profile/media ID cũ làm bằng chứng đúng máy |
| S6 - login người dùng | Flow browser; Colab OAuth; reviewer nếu auto chọn | Kết quả login/connectivity thật, không lưu secret trong report | User login, CAPTCHA, access denied, quota |
| S7 - kiểm tích hợp không sinh nội dung | Session/profile/tool UI; Colab CLI account/session inventory; imports và assets | Capability report theo từng phần | Không cấp T4, upload/generation hoặc gọi reviewer live nếu chưa được phép |
| S8 - thử hữu hạn khi được yêu cầu | Cấp T4 thật/setup remote, WAV thử; render fixture; Flow smoke riêng nếu được phép | Bằng chứng thật, số lượt submit, output đo được, cleanup phạm vi riêng | Không dùng fixtures thay nghiệm thu; unknown dừng đối chiếu |
| S9 - bàn giao | Tóm tắt ready/missing, login cần, lệnh tiếp theo và phạm vi đã kiểm | setup-report + checklist người dùng/agents | Không tự new/start/run job sản xuất sau setup |

Bootstrap phải chạy lại được: bước đã đạt không cài lại hoặc login lại vô cớ; bước lỗi tiếp tục đúng chỗ. Dùng checksum/version/path để phát hiện cần kiểm lại. Lệnh check/plan không phát generation, không đổi config hay trạng thái job.

## 8. Thiết kế công cụ bootstrap tối thiểu

Đề xuất một entry point stdlib, không import Pilot, phục vụ cả máy chưa có venv. Giao diện dự kiến, chưa có hiệu lực:

```text
python3 sys/scripts/bootstrap.py plan --preset english-colab-flow --mode review
python3 sys/scripts/bootstrap.py apply --preset english-colab-flow --mode review
python3 sys/scripts/bootstrap.py check --preset english-colab-flow --mode review
```

plan: chỉ đọc và in kế hoạch. apply: chỉ thực hiện việc cài/cấu hình đã được phép, không production, không tự login/cấp GPU. check: chỉ kiểm trạng thái và capability. Live smoke là tùy chọn riêng sau này, không tự chạy trong apply/check.

Các nguyên tắc:

- Dùng sys/.venv cho core và khóa riêng đúng backend; không trộn dependencies TTS khác Python vào core.
- Không phụ thuộc venv/node_modules của đường dẫn home máy cũ. Worktree có thể dùng runtime chia sẻ nếu được cấu hình và kiểm version/hash rõ; không tạo symlink sang một máy giả định.
- Không sửa config.json theo máy nếu có thể dùng lớp cấu hình local được runtime hỗ trợ. Máy mới có cấu hình mẫu, field validation và merge chỉ các trường máy cho phép. Không override giọng/format/gate qua một lớp local không kiểm.
- Không ghi secrets vào manifest/report/stdout; chỉ ghi đã có/chưa có và lỗi được làm sạch. Không coi tồn tại token là login thành công.
- Không nâng package để làm hết lỗi cài; báo đúng incompatible và đề xuất thay đổi lockfile trong phạm vi phát triển riêng.
- Install system tools/sudo, tải model lớn, mở OAuth và cấp VM có phân công/quyền rõ; không gom vào một bước chạy mù.
- Ghi report local dưới sys/.state/bootstrap/; không tạo/edit SQLite, revisions, reviews hoặc approval sản xuất.

## 9. Mức sẵn sàng cần hiển thị

| Capability | Điều kiện được báo đạt | Điều chưa được suy ra |
|---|---|---|
| content_ready | Core import + schema/bank + entry point + hướng dẫn nhất quán | Media đã hoạt động hoặc kịch bản có chất lượng |
| flow_connected | Profile/executable/tool/account thật đã đối chiếu, refs cần thiết khả dụng | Generation thành công/chi phí đã xác minh/queue production_ready |
| audio_configured | Backend/voice/model manifest đủ; CLI/account đúng | T4 được cấp hoặc chất lượng giọng đạt |
| audio_verified | Đợt thử được phép trên backend thật, WAV/engine/format đúng và kiểm nghe theo khả năng | Những request/job khác được duyệt |
| render_verified | Imports/binary/paths đúng và render thử được phép có artifact | Video sản xuất đã được duyệt |
| auto_review_ready | Reviewer backend được chọn, login/capability thực và kiểm media có bằng chứng | Metadata hoặc smoke text chứng minh nghe/xem được |
| production_ready | Tổng hợp capabilities yêu cầu của preset và nghiệm thu nguồn/queue theo chính sách | Không ép mọi preset phải đủ mọi backend; không tự set acceptance=true |

Report phải ghi verified/configured/missing/unsupported/not_tested và timestamp riêng. Setup tổng thể có thể đủ cho content nhưng chưa đủ cho images/audio; người dùng nhận được danh sách hành động cụ thể thay một chữ PASS chung.

## 10. Các gói phát triển theo thứ tự

| Gói | Tệp dự kiến | Việc thực hiện | Tiêu chí xong |
|---|---|---|---|
| B0 - inventory và bản portable | README/INDEX; manifest asset/dependency dự kiến | Chốt commit/phạm vi được phân phối; phân loại tracked/local/secret; pin phiên bản; xác định Linux/preset đầu tiên | Clone không tham chiếu module/voice vắng mặt mà không báo missing |
| B1 - hướng dẫn người dùng/agents | sys/docs/getting-started.md; vp-bootstrap/SKILL.md; INDEX/AGENTS entry | Viết S0-S9, trách nhiệm, lệnh và điểm dừng; trỏ tài liệu chuyên biệt | Người mới và người đang chat cùng tìm được một luồng setup |
| B2 - preflight/install/check | sys/scripts/bootstrap.py; manifest/schema setup | Entry point stdlib; plan/apply/check; report; idempotent install | Máy chưa có venv đọc được plan; check không gửi production |
| B3 - runtime và cấu hình máy | mẫu machine.local; config loader/helper nếu cần; renderer/Flow bridge đọc cùng paths | Bỏ giả định home/profile/Chrome cũ; schema local; chọn session/ref đúng project | Chạy từ vị trí clone khác không yêu cầu home máy cũ |
| B4 - tài nguyên và login | asset manifest; bootstrap connectors; Flow/Colab docs | Missing asset import; user OAuth/browser handoff; kết quả login thật; T4 bước riêng | Không lộ secret, không tự đổi account/voice hoặc mua compute |
| B5 - doctor và readiness | sys/pilot.py doctor hoặc doctor module; setup report schema; docs | Doctor trả capability và đúng command next; loại check cũ không còn liên quan | Không báo ready từ which/file-exists hoặc chỉ text smoke |
| B6 - nghiệm thu fresh clone | tests/bootstrap tương ứng; báo cáo riêng; docs cập nhật | Kiểm clone sạch, máy thiếu deps, run lại, quyền/login thiếu và interrupted setup | Có evidence của clone sạch; không dùng cache/profile máy cũ để giả đạt |

Đợt B0-B2 là nền tối thiểu. B3-B5 làm máy mới thực sự portable. B6 chỉ chạy tests/live smoke khi người dùng yêu cầu kiểm thử và cho phép phạm vi tương ứng. Không commit/push từ kế hoạch; khi triển khai cần diff được phép và integrity của job đang dở.

## 11. Những tình huống phải kiểm khi được yêu cầu

- Fresh clone không có venv/node_modules/token/machine.local: plan vẫn chạy và chỉ rõ thiếu gì.
- Máy có Python nền khác core version: bootstrap không import Pilot, đề xuất đúng core venv.
- English-Colab preset không cài local TTS/model nặng.
- Chạy apply lần hai không cài lại vô cớ, không ghi đè profile hoặc login store.
- Node/core lock không tương thích: dừng, không tự upgrade/regen lock.
- Clone commit thiếu voice/module default: báo missing; không dùng asset local ngoài manifest.
- Browser executable khác path cũ; profile chưa login; tool URL project khác; media ID không có tại project mới: kết luận đúng và handoff cụ thể.
- OAuth chưa hoàn tất: báo bước cần người dùng, không lưu URL/code/token vào report.
- Colab quota/T4 unavailable: không mua units hoặc xoay tài khoản.
- Interrupted request/session đã có: kiểm/collect đúng account/session, không cấp trùng hoặc gửi lại.
- Review preset không yêu cầu reviewer login; auto preset thiếu nghe/xem trả unsupported.
- Checkout có job locked/ledger reservation cũ: không sửa baseline/ledger, không tạo job thay để hoàn tất setup.
- plan/check không ghi vào state sản xuất và không submit request.
- Setup xong không tự chạy video.

## 12. Quan hệ với các kế hoạch đang lưu

Thứ tự ưu tiên hiện tại:

1. Kế hoạch khởi tạo này: làm entry point/setup/capability rõ trước.
2. Kế hoạch sửa phân quyền và kiểm soát: dùng nền setup và phạm vi checkout đã rõ; phát triển quyền/dừng/recovery/worker.
3. Kế hoạch điều chỉnh hướng video: sửa hợp đồng sáng tạo và tiếp tục đúng job khi được yêu cầu.

Các quy tắc an toàn hiện hành vẫn áp dụng trong khởi tạo. Không dùng ưu tiên bootstrap để sửa code job đang khóa hoặc cấp quyền mới ngầm. B1 sẽ tham chiếu chính sách hiện hành; khi kế hoạch phân quyền được áp dụng, cập nhật phần quyền bootstrap tương ứng.

## 13. Bước tiếp theo và tiến độ

Đã làm: phân tích README/INDEX, manifest phụ thuộc, Git tracking, local paths, Flow/Colab/login, assets và doctor; lập kế hoạch B0-B6.

Chưa làm: tạo skill/bootstrap thật, cài/tải bất kỳ dependency, OAuth, cấp T4, import/upload reference, sửa runtime, tests, smoke generation hoặc sản xuất video.

Khi người dùng yêu cầu triển khai: bắt đầu B0-B1, trình inventory/thiết kế và diff đầu tiên; rồi phát triển B2-B5 theo quyền đã cấp. Cụm nhắc riêng: **“Thực hiện kế hoạch khởi tạo dự án ngày 03/10.”**
