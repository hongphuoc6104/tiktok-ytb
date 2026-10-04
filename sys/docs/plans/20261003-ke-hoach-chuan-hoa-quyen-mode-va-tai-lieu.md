# Kế hoạch chuẩn hóa quyền, mode, hướng dẫn và kỹ năng

Ngày 03/10/2026. **Bản kế hoạch để rà trước cập nhật; chưa sửa tệp vận hành, chưa đổi trạng thái job.**

**Phạm vi bổ sung theo yêu cầu mới nhất:** đồng bộ hướng video từ vựng tiếng Anh minh họa giải thích 2D trong cùng đợt sửa này. Không chỉ sửa quyền rồi để hồ sơ kênh/brief/giọng/render kéo về hướng cũ. Chi tiết tại mục 15; đây vẫn là cập nhật kế hoạch, chưa sửa hệ thống hoặc chạy job.

Yêu cầu hiện hành: viết gọn INDEX/AGENTS/GEMINI/README; phân quyền theo quy trình; cho tự sửa nội dung/video trong quyền; tiếp tục job giữa chat không bị khóa vô lý; auto lập kế hoạch và tự thực hiện, dùng micro-plan sửa lỗi, không cap tổng lượt sửa; review chờ lệnh sau từng đầu ra chính; cả hai cập nhật web; giảm số skill, dọn chỉ dẫn cũ và thử từng bước thật.

Tên mode chuẩn đề xuất là `auto` theo ý nghĩa “audo” người dùng mô tả. Đây là thay đổi định nghĩa so với `auto` trong mã hiện tại, không phải chỉ đổi tên giao diện.

## 1. Phát hiện hiện tại

Rà soát tĩnh checkout gốc `video-vocabulary`; giữ thay đổi chưa commit từ trước. Không chạy status/run/resume hoặc thay baseline của job.

| Nơi | Vấn đề đã xác nhận | Sửa cần thiết |
|---|---|---|
| INDEX | Nhiều kế hoạch/lịch sử/mốc tests/đường dẫn chuyển đổi chen vào điểm vào; ưu tiên không phản ánh đầy đủ yêu cầu mới | Giữ điều hướng hiện hành, bản đồ ngắn, điểm tiếp quản; đưa lịch sử về đúng tài liệu |
| AGENTS/Rules/GEMINI/README | Lặp ba gate, mascot, auto kiểm duyệt; README hướng cài local TTS/render; thiếu quyền theo quy trình | Một nguồn quyền/mode, điểm vào ngắn; mô tả trạng thái code thật trong thời gian chuyển đổi |
| pilot.py protected/integrity | Hash cả .agents/tests/examples/scripts cùng các tệp hệ thống; đổi chỉ dẫn có thể khóa job | Phân nhóm file và tương thích phiên bản thay khóa chung toàn bộ |
| pilot.py adopt-code | Human-only/TTY trong CLI; khác quyền mô tả cho agent sau xác nhận | Ghi người cấp quyền và người thực thi riêng, nhận phiên bản trong đúng quyền |
| pilot.py clean_code | AUTO_REQUIRES_CLEAN_CODE dừng job vì thay đổi protected chưa commit | Provenance rõ cho release/development; không coi dirty bất kỳ là lỗi sản phẩm |
| pilot.py process.lock | CLI quan sát cũng qua khóa độc quyền | Đường đọc trạng thái không ghi và cơ chế ownership tác vụ |
| workflow.py / config | Auto là machine review; trần media=3, audio tổng=4/cảnh=2, repeat failures=3 | Engine auto thực hiện không reviewer; sửa theo tiến bộ thay cap tổng lượt |
| image_repairs.py | MAX_REPAIRS=6 và machine-review streak | Giữ chống duplicate/không tiến bộ, bỏ dừng do tổng lượt sửa trong engine mới |
| Skills | 9 skill và references có khuôn hài, giọng/provider, effect hoặc ngôn ngữ cố định; clean có xóa rộng/pkill/push mặc định | Hợp nhất theo quy trình, craft thành references, bảo trì và Git theo phạm vi cụ thể |

Các giới hạn hiện có không bị gỡ bằng config hay lift-cap trong lượt lập kế hoạch. Muốn thay hành vi phải triển khai chính sách/runtime đồng bộ và xử lý tương thích job.

## 2. Một quyền tương ứng một quy trình

| Quyền | Quy trình | Phạm vi tự thực hiện | Ngoài quyền |
|---|---|---|---|
| production | Tạo, tiếp tục hoặc sửa video/nội dung được giao | Thêm/sửa/thay/xóa nội dung và artifact trong phạm vi job; micro-plan; chạy/thu/render remote; cập nhật web | Không sửa AGENTS/Rules/Skills/README/engine/schema/config hệ thống để chữa job |
| development | Nâng cấp/phát triển được giao | Sửa mọi tệp dự án liên quan phạm vi nâng cấp, gồm hướng dẫn, code, config, schema, tests; migration job và validation | Không thay mục tiêu sản phẩm hoặc thao tác tài khoản/secret ngoài nhiệm vụ; không tự mua dịch vụ |
| setup | Khởi tạo hoặc tiếp quản môi trường | Inventory, cấu hình máy/account theo preset, cài phần cần quản lý và môi trường Colab; bàn giao người dùng login | Không sản xuất hoặc tự đổi quy định/engine khi setup lỗi |
| maintenance | Kiểm kê, dọn/lưu trữ/đồng bộ | Dọn file phát sinh tái tạo được; thu/lưu trước dọn; commit/push phạm vi đã được cấp | Không xóa lịch sử, secret, request dở hoặc sửa logic/Rules để chữa lỗi |

Agent có đúng một quyền hoạt động cho mỗi nhiệm vụ/quy trình. Đổi quyền là bàn giao hoặc chuyển nhiệm vụ có bằng chứng cấp quyền; không tự coi production là developer vì gặp lỗi. Worker thực thi trong quyền của nhiệm vụ giao, không tự tạo quyền mới. Một agent có thể được cấp nhiều phạm vi nhưng chỉ kích hoạt đúng quyền khi thực hiện từng quy trình.

production bao gồm sửa video cũ được giao, không chỉ tạo video mới. Phạm vi phải đủ để sửa các phần phụ thuộc hợp lý của yêu cầu; không xin thêm quyền riêng cho từng WAV/ảnh khi đã thuộc nhiệm vụ. Không suy quyền sửa toàn bộ video khác trong kho từ một yêu cầu sửa một job.

Khởi tạo được tách rõ để clone mới không bị coi là nhiệm vụ nâng cấp hoặc sản xuất. Tên quyền/CLI/schema đích cần chốt khi triển khai, không giả các lệnh này đã có.

## 3. Phân nhóm file và dữ liệu

| Nhóm | Ví dụ | Cách quản lý quyền |
|---|---|---|
| Định nghĩa hệ thống | AGENTS, Rules, Skills, INDEX, README, GEMINI, docs vận hành, engine, renderer, scripts, schemas, lockfiles, config hệ thống | development được sửa trong nhiệm vụ; production/setup/maintenance không sửa ngoài phạm vi rõ |
| Nội dung đang làm | Brief/draft/narration/scenes/images/beats/prompts sửa, dữ liệu kho từ được giao, WAV/ảnh/SRT/MP4 và props của job | production được thêm/sửa/thay/xóa qua workflow công cụ; có impact/version history |
| Trạng thái và lịch sử | Quyết định, revision snapshots, request journal, usage ledger, quyền đã cấp, DB | Công cụ chính thức ghi/cập nhật; không biến quyền sửa nội dung thành quyền giả quyết định hoặc xóa owner/request |
| File tạm tái tạo | Cache/bundle/render temporary, intermediary đã thu đủ đầu ra và không còn dùng làm evidence | maintenance dọn theo manifest/owner và danh sách cụ thể, không wildcard quét sạch |
| Tài khoản/secret | Token, cookies, browser profiles, account store | Kho local hiện có; setup thao tác theo quyền; không push/đưa vào gói Colab/frontend |

Phân loại theo nội dung/chức năng, không chỉ tên thư mục: `sys/vocab/*.py` là code hệ thống; dữ liệu từ vựng là nội dung; metadata/quyết định trong `runs` không phải tất cả đều xóa được. Canonical mascot/profile giọng chuẩn là tài nguyên thương hiệu có nhận diện; production dùng và tạo biến thể, không thay chuẩn thương hiệu ngầm.

Quyền xóa sản phẩm cho phép thay bản làm việc hoặc bỏ đầu ra lỗi theo job đã giao, nhưng lịch sử tối thiểu/ảnh hưởng tới references cần giữ. Đề xuất xóa có tombstone/manifest và lưu phiên bản cần đối chiếu; không biến snapshots bất biến thành toàn bộ job bị khóa. Không buộc duyệt riêng mọi thao tác xóa artifact tái tạo đã thuộc quyền.

## 4. Quyền bền vững và cơ chế xin quyền

Lưu quyền có scope repo/checkout, quyền, job hoặc tập job, hành động và nguồn xác nhận thật; trạng thái còn hiệu lực/đã thu hồi. Thời hạn chỉ đặt nếu người dùng đặt, không hết hạn vì đổi chat. Mode thực hiện và quyền là hai trường độc lập.

Chat mới đối chiếu grant và ownership, tiếp tục phạm vi đang được phép; không hỏi lại “có được sửa không” chỉ vì phiên mới. Một câu cấp quyền rộng được ánh xạ thành phạm vi cụ thể và hiển thị, không thành toàn quyền mơ hồ cho mọi tài khoản/máy.

Nếu micro-plan production cần sửa engine/Rules: chuẩn bị chẩn đoán, diff dự kiến/phạm vi/ảnh hưởng/khôi phục để xin development scope. Không sửa trước rồi xin hợp thức hóa. Nếu đúng development scope đã được cấp còn hiệu lực, thực hiện và ghi lại, không yêu cầu duyệt lại mỗi tệp. Những quyết định thay đổi mục tiêu/chi phí/xuất bản ngoài nhiệm vụ vẫn cần quyền tương ứng.

Quyền trên CLI/application nhằm giảm sai thao tác và truy vết. Với agent có toàn quyền filesystem/shell, chưa được gọi đây là sandbox bảo mật; muốn ranh giới cứng cần cơ chế hệ điều hành/công cụ riêng.

## 5. Sửa cơ chế khóa và tiếp tục job

Tách ba việc khác nhau:

1. **Quyền ghi:** ai được sửa nhóm file nào trong nhiệm vụ.
2. **Tương thích thực thi:** job/checkpoint có đọc/chạy tiếp được với phiên bản engine không.
3. **Toàn vẹn lịch sử:** request/snapshot/quyết định không bị sửa giả hoặc gửi trùng.

Chuyển từ hash toàn bộ repo gây khóa job sang phiên bản engine/schema/policy và kiểm tương thích đúng phần ảnh hưởng. Tệp chỉ dẫn đổi không tự làm WAV/ảnh mất hiệu lực. Production sửa nội dung tạo phiên bản và làm mới đúng phần phụ thuộc, không chạy rebaseline cho mỗi lần sửa.

Thay đổi engine tương thích, đã thuộc development scope: kiểm rồi tiếp nhận/migrate qua công cụ, lưu bản cũ và provenance, không xin người dùng chạy terminal hoặc xác nhận từng job nếu đã nằm trong phạm vi cấp. Thay đổi chưa có quyền/không tương thích chưa có migration: dừng đúng phần, không giả tương thích.

Job ownership có lease/heartbeat, nhận diện runner còn sống và thao tác takeover khi runner cũ không còn. Dừng rồi resume hoặc sang chat mới dùng checkpoint cũ; không nhân đôi runner/submit. Snapshot quan sát không refresh/ghi trạng thái job. Không tự mở khóa writer của runner còn sống.

## 6. Hai mode sản xuất mới

### auto

Lập một kế hoạch tổng thể gồm mục tiêu, phạm vi, tài khoản, bước/phụ thuộc, nơi xử lý và đầu ra. Tự thực hiện content → media → video tới kết quả. Không gọi machine reviewer, không chờ click duyệt từng đầu ra; cập nhật web và chat khi có artifact.

Có lỗi: tạo micro-plan, tra issue log dự án và tài liệu internet khi cần, thực thi trong quyền rồi tiếp tục. Lỗi được xử lý phải lưu giải pháp và bằng chứng; không chỉ log “đã thử lại”. Thay đổi mục tiêu/đi ra ngoài quyền là lý do xin quyết định, không hỏi lại công việc đã giao.

Không cap tổng số lượt sửa nội dung/audio/ảnh. Cơ chế tránh vô hạn là kiểm tiến bộ, nguyên nhân và các thao tác còn khả thi, không đạt N lượt rồi xin lift-cap.

### review

Sau mỗi đầu ra chính, cập nhật web/chat và chờ phản hồi/lệnh mới của người dùng cho bước phụ thuộc:

1. Kịch bản ngắn/outline và kế hoạch cảnh.
2. Lời thoại đầy đủ và liên kết cảnh/hình/chữ.
3. Audio thật.
4. Bộ ảnh thật, xem được từng ảnh.
5. Video thật.

Ba nhóm sản phẩm content/media/video vẫn giữ để tổ chức dữ liệu, nhưng điểm chờ review được tách theo đầu ra như người dùng vừa yêu cầu; không giữ quy định cũ “chỉ ba điểm duyệt” để bỏ điểm chờ audio/ảnh. Với bộ ảnh nhiều mục, quyết định gắn bộ/ảnh/phạm vi cụ thể; việc chia nhóm giao sản phẩm phải hiện trong plan, không tự buộc người dùng click từng prompt.

Phản hồi sửa tạo phiên bản mới cho phần ảnh hưởng. Quyết định gắn đúng đầu ra/phiên bản và nguyên văn phản hồi thật. Không suy “được rồi” cho đầu ra chưa tạo. Chuyển mode khi được yêu cầu dùng thao tác ghi sự kiện/checkpoint đúng quyền; không edit workflow.json tay. Cách chuyển job v3 hiện có sang định nghĩa mới cần migration riêng.

## 7. Micro-plan và chống vòng lặp

Micro-plan ngắn có: triệu chứng/evidence; fingerprint lỗi; nguyên nhân đã biết/giả thuyết; đầu ra/tệp ảnh hưởng; quyền cần; hành động khác lần trước; tiêu chí thành công; checkpoint/khôi phục; kết quả.

Giữ lịch sử fingerprint gồm error class + target + input/artifact + strategy + trạng thái submit. Không chạy lại bộ tổ hợp giống nhau khi chưa có evidence/điều kiện mới. Fingerprint chữ không thay thế giải thích vì sao chiến lược mới có thể hữu ích.

Nếu không tiến bộ: chẩn đoán thêm, đọc giải pháp trước đó, tìm nguồn chính thức, đổi chiến lược trong quyền. Nếu không còn hành động có cơ sở và được phép, dừng ở `needs_attention` với nguyên nhân/đề xuất cụ thể. Không hỏi xin “thêm lượt” và không đổi tên issue/job để reset lịch sử.

Timeout sau submit chỉ collect/reconcile request cũ. Quota/CAPTCHA/bot/auth/capacity/503 vẫn cần xử lý đúng giới hạn dịch vụ, không lặp generation để thử may mắn hoặc xoay account né chặn. Giới hạn số hành động phục hồi mạng có thể giữ riêng theo loại thao tác; không biến nó thành cap tổng số sửa video. Không unlimited requests trả phí, không tự mua compute.

## 8. Web là kênh quản lý bắt buộc của cả hai mode

Cùng một nguồn job/version cho web/chat. Sự kiện: kế hoạch, bước chạy, artifact ready, micro-plan/lỗi, đang chờ review/quyền/login, dừng/tiếp tục, kết quả cuối.

Web phải xem được kịch bản ngắn, lời thoại theo cảnh, WAV, từng ảnh, SRT/timeline và MP4. Nguồn prompt/ref/request đi theo target. Generated chưa download không hiển thị như file đã sẵn sàng. Không giả đã gửi web khi chỉ ghi stdout.

Bản đồ 8 tab đã chốt giữ nguyên; review hiển thị điểm chờ theo đầu ra, auto hiển thị thực hiện/khắc phục liên tục không reviewer. Không dựa vào mockup để tuyên bố event/web runtime đã tồn tại.

## 9. Phân bố bốn tệp gốc và Rules

| Tệp | Giữ | Đưa ra ngoài |
|---|---|---|
| INDEX | Đường vào setup/chat mới/sản xuất/phát triển/bảo trì; map ngắn; phiên bản tài liệu hiện hành | Lịch sử chuyển đường dẫn, tests cũ, dài danh sách kế hoạch |
| README | Dự án làm gì, kiến trúc máy/Colab/Flow, cách bắt đầu và trạng thái hỗ trợ | Lệnh cài model local, hướng dẫn reviewer cũ và số đo máy cũ |
| AGENTS | Cách xác định quyền đang dùng, ngôn ngữ, nguồn chính sách/workflow, bàn giao và ưu tiên yêu cầu | Chi tiết hình ảnh, thao tác CLI/retry, khuôn sáng tạo và tài liệu setup dài |
| GEMINI | Adapter điểm vào ngắn, trỏ đúng INDEX/AGENTS và workflow | Sao chép lại toàn bộ quyền/sản xuất/brand |

Rules đề xuất: `permissions.md` (ma trận quyền/nhóm file/grant); `execution.md` (mode/stop/recovery/no duplicate và trỏ workflow); `brand_tolerance.md` (nhận diện); `accounts.md` (auth/session/budget, trỏ spec). `production.md` hiện tại được phân tách rồi bỏ/đổi thành adapter ngắn nếu công cụ cần; không để hai nguồn cùng định nghĩa một quyền.

Workflow giữ thứ tự/checkpoint/version/impact chi tiết. Getting-started và session-start giữ setup/tiếp quản. Tài liệu chuyên môn giữ cách viết/lập hình/âm/biên tập, không cấp quyền.

## 10. Bộ skill tối thiểu đề xuất: bốn skill

| Skill | Một quy trình | Tài liệu đọc theo nhu cầu |
|---|---|---|
| vp-setup | Clone/setup hoặc tiếp quản môi trường | Getting-started/session-start, account/Colab/Flow setup |
| vp-production | Tạo/tiếp tục/sửa video auto hoặc review | Content, vocabulary, visual/audio/editing references theo bước |
| vp-development | Nâng cấp hệ thống trong scope được cấp | Diff, schema/engine compatibility, tests, migration/rollback |
| vp-maintenance | Kiểm kê/dọn/archive/Git theo quyền | Retention/reproducibility/owner, commit/push allowlist |

Hợp nhất vp-vocab/content/media/video vào vp-production; bốn director chuyển phần nghề hữu ích vào references; vp-clean thay bằng maintenance. Không xóa trước inventory callers ở adapter/director_context/reviewer/docs/tests/tool metadata. Giữ nội dung hữu ích và lịch sử trong Git hoặc snapshot được kiểm, cập nhật mọi tham chiếu rồi mới bỏ skill cũ khỏi thư mục discovery. Không giữ bản skill cũ active gây nạp lại khuôn hài/giọng.

Skill cấu trúc validate và tình huống thực mới là hai phép kiểm khác nhau. Không chỉ kiểm frontmatter rồi tuyên bố đã test workflow.

## 11. Bảo trì và Git

Maintenance có quyền dọn file sinh ra tái tạo được, với điều kiện không còn target đang dùng/evidence duy nhất và kết quả quan trọng đã thu. Ghi danh sách trước/sau; không xóa runs/video/browser cache toàn máy bằng wildcard. Đóng session chỉ thuộc dự án, đã thu và không còn unknown.

Quyền commit/push định kỳ thuộc maintenance scope đã cấp. Đề xuất thực hiện tại cuối đợt bảo trì hoặc checkpoint đã chọn; lịch chạy theo giờ chỉ tạo sau khi chốt tần suất, repo/branch và paths. Lượt lập kế hoạch không tạo automation/commit/push.

Stage allowlist, kiểm diff/secrets/remote/branch; giữ sửa local ngoài phạm vi và không `git add .` mù. Chỉ push lịch sử bình thường, không force-push; conflict/auth failure dừng đúng nguyên nhân. Video/model/profile/token/DB không đưa Git. Bản thay đổi developer chỉ vào commit khi đã bàn giao đúng scope.

## 12. Gói triển khai và nghiệm thu

| Gói | Việc làm | Tiêu chí xong |
|---|---|---|
| P0 – chốt hợp đồng | Nhóm file, 4 quyền, 2 mode, review outputs, nguồn duy nhất và hướng kênh tiếng Anh/2D | Tài liệu định nghĩa ngắn, không mâu thuẫn; scope cụ thể và hồ sơ hướng sản phẩm |
| P1 – điểm vào/Rules | Viết gọn INDEX/README/AGENTS/GEMINI; rules split; setup/return docs; contract kênh và map nguồn | Clone/chat mới tìm đúng việc/hướng kênh; không quảng cáo lệnh chưa có |
| P2 – runtime quyền/resume | Grant bền vững; compatibility thay integrity blanket; ownership/takeover; observe | Sửa job cũ/đổi chat/dừng rồi chạy không xin lại quyền hợp lệ; không double submit |
| P3 – mode/micro-plan | Auto không reviewer, review checkpoint theo đầu ra; chống no-progress | Không fixed cap tổng sửa; lặp không evidence bị chặn; out-of-scope xin đúng quyền |
| P4 – skill và dọn docs | 4 skill; references nghề cụ thể theo hướng mới; profile/brief generator; cập nhật callers và archive nội dung cũ | Không skill/link mồ côi, không khuôn/giọng lạc đề; nguồn profile đi vào brief/content/request thật |
| P5 – web và remote | Artifact/events/review controls, account/session, xử lý Colab; tách ngôn ngữ/tỷ lệ/track/subtitles | Hai mode cập nhật web thật; bản dọc tiếng Anh đúng track/timeline; nặng không fallback local |
| P6 – thử từng bước | Tình huống cô lập rồi thử outline/narration/WAV/3 dạng hình/continuity/MP4 thật hữu hạn | Đúng hướng mới từ brief đến MP4; có evidence; không lấy fixture làm sản phẩm |

Thiết kế P0 bao gồm chính sách đích và migration; chỉnh P1 không tự làm engine v3 hỗ trợ quyền/mode mới. Trong thời gian chuyển đổi, banner capability chỉ rõ trạng thái để agent không gọi `--mode auto` cũ cho nhiệm vụ auto không reviewer.

Tình huống bắt buộc khi triển khai: production sửa narration/ảnh đúng scope không hỏi; production không sửa Rules khi chữa lỗi; development đã cấp sửa/tiếp nhận đúng scope không bắt người dùng tự TTY; đổi chat nhận grant/checkpoint; runner cũ còn sống không takeover; review dừng sau script/dialogue/audio/images/video; auto không gọi reviewer; sau nhiều sửa có tiến bộ vẫn chạy; fingerprint không đổi chặn lặp; unknown không submit lại; cache cleanup giữ evidence; commit/push chỉ paths/branch đã cấp.

## 13. Job cũ và tài liệu cũ

Giữ chính job khi sửa nội dung cũ. Inventory engine/schema/mode/requests/decisions trước migration; kiểm trên bản sao cô lập, tạo event chuyển đổi và có rollback dữ liệu phù hợp. Job chưa migrate dùng contract cũ; không chữa bằng sửa DB/integrity/workflow tay hay tạo job mới cùng nội dung để né lỗi.

Tài liệu lỗi thời được phân loại active/legacy/reference/plan; active có một mục lục và đường dẫn mới. Lịch sử reviews/revisions/evidence không xóa. README/INDEX bỏ claim test/khả năng đã cũ hoặc chuyển sang report có ngày và scope. Không dọn mã B-2 chỉ vì nằm experiments, không xóa .gflow/token để làm repo nhẹ.

## 14. Phạm vi lượt này

Chỉ đọc và lưu kế hoạch. Chưa sửa INDEX/AGENTS/GEMINI/README/Rules/Skills/engine/config; chưa migrate/adopt/lift-cap, cài đặt, login, test/generation/render, xóa file hoặc commit/push. Yêu cầu cuối của người dùng là bắt đầu lập plan nên không tự triển khai trong lượt này.

## 15. Đồng bộ hướng video mới trong cùng đợt sửa

### 15.1 Hướng sản phẩm phải đi vào dữ liệu và cách làm

Căn cứ báo cáo/kế hoạch người dùng vừa cung cấp, không phải khảo sát lại kênh mẫu trong lượt này:

- Short 9:16 hoàn toàn bằng tiếng Anh; từ/ý học B1 trở lên lấy từ kho, một nghĩa mỗi video; lời giải thích dễ hiểu, dùng đúng ngữ cảnh.
- Một câu hỏi hoặc tình huống dẫn chuyện, kết có payoff; giải thích nghĩa/cách dùng/phát âm/ngữ pháp theo hợp đồng, nối vào tình huống thay vì đọc lần lượt các mục giáo án.
- Minh họa giải thích 2D vẽ tay, viền đậm, màu phẳng, nền sáng, đạo cụ/sơ đồ rõ. Không dùng tranh tư liệu gần hiện thực nhiều chất liệu/ánh sáng tối; không nhập chủ đề tiền sử từ kênh mẫu thành ngách bắt buộc.
- Nhân vật vẽ tay nét rõ ràng trong các khung, dùng pose/cử chỉ dẫn mắt; giữ đúng core identity/80–20. Không để nhân vật che trọng tâm hoặc thay hành động bằng nhân vật chỉ đứng cạnh.
- Số cảnh/hình/beat được chọn cho từng kịch bản; không 4 hồi hài/6 nhịp/16–22 tranh/15–20 giây mặc định bắt buộc. Khi đã chọn thì lưu số cảnh cụ thể vào hợp đồng job để tạo/validate nhất quán.
- Giữ Flow, giọng và tốc độ đã chọn của job; rate 0.92 trong báo cáo là quyết định cần bảo toàn/đối chiếu cho job liên quan, không suy từ config khác. Không lấy giọng Adam/rate1.08 của checkout hiện tại thay quyết định đó.

Các checkpoint và quyền trong phần B của kế hoạch cũ đã được yêu cầu mới hơn thay thế: auto thực hiện không reviewer; review theo đầu ra chính; quyền theo quy trình và chống lặp không cap tổng sửa. Giữ phần A về hướng hình/kể, không tái nhập auto kiểm duyệt/ba gate cố định/TTY human-only vào thiết kế mới.

### 15.2 Kết luận về skill

Bốn skill vp-setup/production/development/maintenance phù hợp để phân quy trình và quyền. **Chưa đủ nếu vp-production chỉ là danh sách lệnh**, hoặc nếu xóa skill đạo diễn đồng nghĩa xóa toàn bộ chuyên môn. Phải giữ craft thành references được vp-production nạp đúng bước, có đầu vào/đầu ra và tiêu chí cụ thể:

| Reference đề xuất trong vp-production | Chức năng | Đầu ra đưa vào job |
|---|---|---|
| vocabulary | Một nghĩa, chọn B1+ đúng kho, mục tiêu học và ví dụ/phản hồi phù hợp | Bank entry/sense, coverage yêu cầu, lưu ý nghĩa khác |
| script | Câu hỏi dẫn, English dễ hiểu, causality, payoff, chốt narration trước neo | Outline, narration, purpose/transition, chữ và anchors |
| storyboard | Hành động/trạng thái, cảnh kể/cận hành động/sơ đồ, continuity | Images/beats, based_on, preserve/change, function từng hình |
| visuals | Nét 2D/nền sáng/màu phẳng, bố cục, nhân vật và references | Description/ref/allowed text theo profile, kết quả ảnh liên kết target |
| audio | Voice/rate theo brief, synthesis Colab, pronunciation/holds khi cần | Request thật có voice/rate, WAV đo được; không chứng nhận cảm xúc từ prompt |
| editing | WAV thật, cut/hold, cue đủ đọc, không tràn hai dòng, kết quay lại câu hỏi | Timeline/SRT/render props và MP4 theo track/ngôn ngữ |

Hồ sơ kênh là nguồn lựa chọn style/ngôn ngữ/giọng; references hướng dẫn cách thực hiện lựa chọn đó, không giữ bản cấu hình sáng tạo thứ hai. Reference storyboard/visual có thể gộp nếu đủ ngắn; không tạo nhiều tệp chỉ để chia tên vai trò. Không bắt mở mọi reference trong mọi lượt.

### 15.3 Phạm vi tệp và mã cần đồng bộ

| Nhóm | Điều cần đổi trong đợt này |
|---|---|
| AGENTS/Rules | Quyền/mode/nhận diện chung; trỏ profile, không nhét toàn bộ format kênh vào quyền |
| INDEX/README/GEMINI | Dẫn tới hướng đang dùng, nhận diện tài liệu lịch sử; nói đúng trạng thái hỗ trợ English portrait/Colab |
| sys/vocab/channel.json | Profile hiện tại thực tế là tiếng Việt, micro_drama, 4 cảnh/15–20s, Adam,1.08 và Foley/screen-shake; phải thay hướng mặc định hoặc dùng preset kênh mới có lựa chọn rõ |
| sys/vocab/bank.py và dữ liệu kho | Chọn phạm vi B1+ (đã có bộ lọc --level, cần nối profile/selection), một nghĩa; chuyển profile thành brief đúng hướng; số cảnh/độ dài không lấy template cố định; không viết brief vocab ngoài bank |
| Brief/content schemas và validators | Ngôn ngữ, tỷ lệ, subtitles/track độc lập; scene_count cụ thể sau planning; narration/coverage/anchors theo ngôn ngữ yêu cầu. Chưa được coi bỏ key scene_count là code sẽ tự hỗ trợ |
| vp-production và references | Giữ chuyên môn hữu ích, bỏ hài/shadowing/SFX/timing/hình-count bắt buộc; chuyển narration-style khỏi giả định 16:9=English và hạn256 ký tự làm lý do ép câu |
| scripts/director_context.py và nơi gọi | Hiện đọc trực tiếp tên/path của bốn director và vp-content refs; chuyển bindings trước xóa skill, test không FileNotFound và context đúng profile. Không sử dụng phần reviewer của loader trong auto mới |
| scripts/agy_pipeline.py và adapter content | Nội dung do điều phối viết trong workflow mới; tránh fallback tự gọi generator/reviewer cũ kéo hướng. Lưu draft/plan/nguồn hướng trong dữ liệu |
| adapters.py / colab_bridge / renderer/outputs.mjs | Hiện needs_en và English coverage nhiều nơi phụ thuộc16:9/dual; vertical dùng narration.wav/vi cues. Phải hỗ trợ English9:16 với đúng text/voice/track/timeline/cue ở toàn chuỗi, không chỉ sửa chú thích |
| config/voice profiles | Ngăn defaults Adam1.08 hoặc rate khác override voice/rate hợp đồng; log request thực. Không đổi nhân vật/provider/mẫu prompt cố định để làm nhanh |
| Web | Kịch bản/cảnh cho thấy chức năng hình, narration tiếng Anh, nhân vật/ref, ảnh và thời điểm audio/video, nguồn profile/revision; cùng dữ liệu của job |
| Docs active/historical | Loại/tách chỉ dẫn kéo về A1–A2/hài/local/bilingual nếu không đúng preset; giữ báo cáo lịch sử, request và phản hồi, không viết lại bằng chứng |

### 15.4 Thử từng bước theo hướng mới

1. Brief thử từ kho: đúng entry/sense B1+, English9:16, profile mới, voice/rate và constraints. Không có yêu cầu hài4hồi/tiền sử/quota tranh mặc định.
2. Outline/narration: một câu hỏi, các ví dụ phục vụ câu hỏi, giải thích đủ ý và payoff; không đọc mục giáo án; anchors giữ nguyên văn lời đã chốt.
3. WAV Colab: có track English thực, đúng voice/rate đã chọn, duration thật; kết quả phát âm/nghe chỉ ghi khi thực sự nghe. Không gọi reviewer tự động.
4. Bộ hình thử hữu hạn: cảnh kể, hành động, sơ đồ/giải thích; mỗi ảnh có nhân vật chuẩn và đúng hướng. Xem hình thật để chốt phát triển hướng, không suy từ prompt hoặc hash. Trong auto production mới không biến thử phong cách thành quality gate bắt buộc.
5. Chuỗi continuity: cùng bối cảnh khóa góc và base ref, thấy state change; hình độc lập mới dùng generation độc lập. Không nới identity20% để chấp nhận sai hành động.
6. MP4 English9:16: English audio, English cue nếu brief yêu cầu phụ đề, timeline theo WAV, không track Việt/ngang bị kéo nhầm, không crop mất chữ/nhân vật. Render trên Colab; file thật và kiểm kỹ thuật kết quả.
7. Cùng profile được thử cho auto và review: auto không reviewer/chờ duyệt; review dừng đúng các output; cả hai đưa artifact lên web. Mock/fixture xác minh logic không thay bộ ảnh/WAV/video thực.

Với job predator đang được nhắc: các revision/approval/request trong báo cáo là lịch sử, chưa xác minh live ở lượt này. Khi triển khai phải tiếp tục chính job, kiểm trạng thái hiện tại, giữ sense đang reserved; không tự thay narration/WAV nếu yêu cầu chỉ đổi hình. Chỉ phần bị tác động được tạo phiên bản mới; unknown cũ đối chiếu trước, không tạo job mới để bỏ qua.
