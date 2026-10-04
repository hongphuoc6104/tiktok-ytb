# Đối chiếu yêu cầu và bằng chứng chuẩn hóa

Ngày 03/10/2026. Rà trực tiếp checkout phát triển `codex/normalize-video-workflow`; đây là ảnh chụp trạng thái mã khi audit, không phải nghiệm thu toàn hệ thống. Các agent khác đang sửa cùng checkout nên phải chạy lại tiêu chí sau khi ghép thay đổi.

Nguồn hợp đồng đã đọc đầy đủ: [kế hoạch chuẩn hóa, gồm mục 15](../plans/20261003-ke-hoach-chuan-hoa-quyen-mode-va-tai-lieu.md), [thiết kế 0.3](../plans/20261003-thiet-ke-colab-va-auto-thuc-hien.md), [thiết kế 0.4](../plans/20261003-thiet-ke-ngan-sach-tai-khoan.md), [giao diện đã chốt](../plans/20261003-chot-giao-dien-thu-nghiem.md), INDEX/AGENTS, Rules và skill vp-development. Ghi chú tiến độ cũ chỉ dùng tìm phạm vi, không dùng thay chứng cứ hiện tại.

## Cách đọc trạng thái

- **Có logic đã kiểm**: phép kiểm cô lập đã chạy trong lượt audit này; chưa chứng minh dịch vụ hay chất lượng artifact thật.
- **Có mã, chưa nối đủ**: có implementation nhưng caller, CLI, phụ thuộc hoặc kiểm nghiệm còn thiếu.
- **Chưa có bằng chứng**: chưa tìm thấy đường chạy thực hoặc artifact/evidence hợp lệ ở checkout này.
- **Xung đột đang có**: caller hiện tại vẫn thực hiện hành vi trái hợp đồng đích.

## Ma trận yêu cầu

| ID | Yêu cầu cần đạt | Bằng chứng trong mã hiện tại | Trạng thái và tiêu chí còn phải chạy |
|---|---|---|---|
| Q01 | Bốn quyền setup/production/development/maintenance, mỗi nhiệm vụ một quyền hoạt động | `permissions.py:ROLES/OPERATIONS`; Rules permissions | Có logic đã kiểm: role khác và operation ngoài quyền bị từ chối. Cần nối mọi thao tác CLI/web với cùng grant, không chỉ kiểm tại `execution.require`. |
| Q02 | Grant sống qua chat, có scope, nguồn thật, thu hồi/thời hạn do người dùng đặt | `Grants.grant/read/revoke/require`; trường source, project, jobs, paths, expiry | Có logic đã kiểm: store mới đọc grant cũ; job khác, revoke, path escape bị chặn. `source_transport_verified=false` được ghi rõ; chuỗi source tự khai không chứng minh người dùng thật đã cấp. Cần caller có provenance và một thao tác tiếp quản thực. |
| Q03 | Production tự sửa video cũ trong quyền; không sửa hệ thống để chữa job | `classify`, operation content/repair; `Pilot.reject/revise_brief` lịch sử cũ | Có logic scope đã kiểm, nhưng chưa có `execution.reject/repair` nối checkpoint mới và invalidation. Cần sửa đúng job qua công cụ, giữ sense/request/decision, không hỏi lại từng artifact. |
| Q04 | Lịch sử/request/quyết định bất biến không thành nội dung được sửa trực tiếp | `classify` nhận biết revisions/reviews/integrity/workflow/ledger | Có mã, chưa đủ: request journal, checkpoints/decision.json, execution-control và các manifest trong runs chưa được phân loại history; mặc định runs là content. Kiểm âm: production có paths rộng vẫn không được sửa trực tiếp những tệp này. |
| Q05 | Engine mới không khóa blanket do đổi Rules/test/docs/dirty | `Pilot.integrity` dispatch `verify_compatibility`; CONTRACT phiên bản 4; new v4 dùng provenance | Có mã, chưa nối đủ CLI. Cần chứng minh đổi doc/test không khóa v4; đổi contract không tương thích buộc migration đúng phần. Legacy vẫn giữ baseline/lịch sử. |
| Q06 | Development đúng scope được migrate/adopt không cần giả human TTY | Legacy `adopt_code` và CLI vẫn human-only; chưa tìm thấy migration v3→v4 | Xung đột đang có ở CLI: xác nhận scope phát triển chưa nối vào công cụ migration. Cần backup/provenance/compatibility/rollback, giữ chính job và quyết định cũ, không sửa state tay. |
| Q07 | Quan sát chỉ đọc, không writer lock hoặc refresh | `execution.observe/current` đọc metadata/DB; legacy CLI vẫn `with locked(ROOT)`; `Pilot.status` refresh/interrupted writes | Có mã observe, chưa nối đủ. `Pilot()` tự tạo .state/schema nên kiểm cả đường mở kết nối. Chụp hash/mtime trước–sau observer, thử trong lúc runner giữ lease; không đổi job hoặc lấy lock writer. |
| Q08 | Runner ownership/heartbeat, stop/resume/takeover không double submit | `execution.lease` dùng per-job flock; control owner/pid/heartbeat; resume không clear stop khi lease đang giữ | Có mã, chưa có takeover chính thức hoặc kiểm crash đa process. `approve` chưa dùng lease. Cần runner sống không bị takeover; runner chết giải phóng ownership có sự kiện; hai reviewer không ghi đè quyết định. |
| Q09 | Stop chặn từng request mới, thu inflight giữ nguyên owner | `before_submit` được gọi quanh `p.run` và checkpoint images | Có mã, chưa đủ: một `p.run(images)` có thể gửi nhiều request/batch; chưa thấy hook tại mỗi real submit. Phải kiểm stop giữa hai ảnh, collect request trước vẫn chạy, ảnh tiếp theo không gửi. |
| Q10 | Auto tổng plan→thực hiện, không machine reviewer hoặc quality approval | `execution.advance` technical p.approve, không import reviewer trực tiếp | Có mã, chưa đủ: thiếu tổng plan đã lưu. `image_pipeline.register` vẫn gọi settings v3 và reviewer khi auto. Kiểm spy trên mọi reviewer entry, kể cả character registration; không chỉ kiểm execution.py không import module. |
| Q11 | Micro-plan có evidence, nguyên nhân/chiến lược/tiêu chí/khôi phục/kết quả | Chưa tìm thấy kho hoặc thao tác micro-plan cho engine mới | Chưa có bằng chứng. Cần lưu input/target/error/strategy/submit state, tra issue, action/result; no-progress chặn tổ hợp lặp không có evidence mới, không chặn sửa có tiến bộ. |
| Q12 | Không cap tổng sửa; recovery mạng có episode riêng | `image_repairs.validate_plan` vẫn MAX_REPAIRS=6; workflow v3 có tổng media/audio/repeat caps | Xung đột đang có nếu v4 dùng caller repair cũ. Bypass phải theo engine mới, giữ v3 nguyên nghĩa. Thử hơn sáu sửa có tiến bộ và một lặp không đổi bị chặn; không gọi lift-cap. |
| Q13 | Review chờ outline, dialogue, audio, images, video đúng revision | CHECKPOINTS, manifest hash, event-backed `execution.approve`, `gate` | Có mã, chưa có kiểm toàn luồng/CLI. Cần dừng đúng năm điểm, reject tạo version mới, stale feedback bị chặn; review bộ ảnh gắn tập/ảnh cụ thể theo plan. |
| Q14 | Mode transition chính thức, event/checkpoint, không edit workflow tay | `change_mode` ghi hash event và chi tiết nguồn | Có mã, chưa nối CLI/web. Cần đổi auto↔review và stale/current decisions có nghĩa đúng; không tự công nhận đầu ra chưa tạo, không diễn giải machine approval v3 thành approval mới. |
| Q15 | Web thật tám tab, dữ liệu chung CLI và hai mode | Chưa tìm thấy server/frontend/dashboard runtime ở checkout audit | Chưa có bằng chứng. Phải chạy server, mở browser thật, tạo/update artifact fixture qua official engine, thấy đúng job/revision/WAV/ảnh/SRT/video ở tám tab; stdout hoặc mockup không chứng minh hiển thị. |
| Q16 | Web mutations quyền/owner, loopback/origin, media path an toàn | Chưa có implementation web để kiểm | Chưa có bằng chứng. Kiểm mutation ngoài origin, path traversal, stale revision và runner sống; không đưa secret/OAuth URL/code/token vào response/frontend/log. |
| Q17 | Clone/setup/chat mới không mang home/profile/model cũ | getting-started/session-start viết đúng hướng; chưa có bootstrap callable | Có tài liệu, chưa có workflow đã thử. Clone sạch trong thư mục tạm: đọc capability present/configured/verified/missing/not_tested/unsupported, không cài model/render local, không auth thay người dùng. |
| Q18 | Auth khác capability/budget; pin/pool/active độc lập Colab/Flow | `colab_bridge.accounts` và client lưu account/session; token-only ensure_authenticated | Có nền account, chưa chứng minh live auth/capability và pool phiên. Token tồn tại chỉ là có hồ sơ; active phải gắn request/VM thật. Pin không đổi khi lỗi; không rotate né chặn. |
| Q19 | Ledger 0.4 bền qua chats: GPU idle/uncertain/window/reserve; Flow submitted/unknown | Chưa tìm thấy ngân sách thời gian/ảnh và reservation ledger triển khai | Chưa có bằng chứng. Cần 6h display/5h usable/1h reserve, window 24h từ connected T4, idle vẫn tính, interval crossing chia đúng; output unknown giữ slot và profile alias không mở counter mới. Đây là ngân sách người dùng, không quota Google. |
| Q20 | Recovery tối đa ba theo operation/request/episode; quota/bot/auth/503 dừng | client giữ ambiguous→download-only; queue guards cũ | Có nền collection-only, chưa có ledger recovery episode và test thay chat. Timeout sau submit chỉ collect/reconcile request cũ, không ba lần generation; chặn quota ngay, không rotate. |
| Q21 | Audio/assembly/mastering/subtitles chạy Colab, WAV có voice/rate contract | `remote_audio.produce`, protocol assemble/support hashes, worker và `media_packaging.assemble` | Có mã, chưa chứng minh T4/WAV thật trong lượt audit. Cần remote manifest đúng account/session/request/language/voice/speed/hash, lượng audio; không local synthesis fallback. |
| Q22 | Image processing/timeline/props/render/encode chuyển Colab | `adapters.render` vẫn chuẩn bị timeline/cues/copies và gọi local node renderer | Xung đột đang có. Cần gói remote versioned, submit/collect journal, asset manifest, safe imports; local chỉ quản lý/lưu. Không đổi nhãn processing_location để tuyên bố remote. |
| Q23 | Profile English B1+, một sense kho, 2D sáng, hình minh họa rõ ràng mọi khung, count theo job | channel v4 English 9:16 Alba .92, allowed_levels; bank profile→brief; scene_count null trước plan | Có logic đã kiểm: B1+ default, explicit override, brief snapshot/profile/output, scene_count theo job. Chưa có hình thật hoặc proof mọi frame có hình minh họa/hành động nghĩa. Existing job giữ contract cũ/voice/rate riêng. |
| Q24 | 80/20 giữ core và cho phép eyebrows nhẹ | Rules brand cho tolerance; `image_pipeline.requested_prompt` vẫn thêm “do not add eyebrows” | Xung đột đang có trong prompt thực. Sửa instruction động đúng tolerance, giữ nguyên mẫu prompt_templates nếu không được yêu cầu đổi mẫu. Kiểm prompt cuối và ảnh thật, không suy từ hash. |
| Q25 | English9:16 đi đúng narration/coverage/anchors/WAV/cues/timeline/render | output_contract, content validation, outputs.mjs; audio remote primary en | Có logic đã kiểm ở schema/routing helper. `adapters.render` vẫn chọn vi cho portrait; Pilot checks vẫn có 16:9→en. Cần kiểm full adapter→remote payload→render props, không chỉ đầu ra outputPlans với props giả. |
| Q26 | Bảo trì chỉ tái tạo, manifest/owner/evidence; Git allowlist/secret/branch | skill maintenance + classify cleanup | Có tài liệu và scope check, chưa có cleanup/archive/Git công cụ đã thử. Kiểm evidence/inflight không bị xóa; chỉ stage/push paths/branch được cấp, không force-push hoặc automation chưa có tần suất. |
| Q27 | Log mọi issue và giải pháp thực; fixture không thành sản phẩm | client issue có ghi logs/INDEX nhưng mẫu gợi ý chưa phải giải pháp đã xử lý | Chưa có nghiệm thu toàn tuyến. Log mới phải phân biệt chẩn đoán/gợi ý với “Làm gì cho hết lỗi” đã chứng minh; không rewrite evidence/history cũ. |
| Q28 | Thử từng bước thật hữu hạn: brief/outline/WAV/ba loại hình/continuity/MP4; cả modes web | Chưa tạo provider artifact trong lượt audit | Chưa có bằng chứng. Live chỉ theo scope cho phép/capability; lưu lineage/hash/location/account/request, nghe/xem thật. Thiếu login/T4/Flow ghi đúng phần chưa kiểm, không dùng fixture thay proof. |

## Các điểm cần sửa trước nghiệm thu luồng

1. **Nối engine và ownership vào public caller.** CLI tại thời điểm rà còn chỉ lựa chọn ba stage của workflow v3 và giữ lock toàn `.state/process.lock`. Không thể dùng tài liệu mới hoặc gọi `execution.advance` trực tiếp làm chứng minh người dùng dùng được engine mới.
2. **Tách hoàn toàn reviewer/caps tại caller ảnh.** Character registration gọi settings v3 và machine reviewer; repair helper cap sáu lần áp vô điều kiện. Cần engine-aware route và test negative dependency, giữ nghĩa v3 cho lịch sử.
3. **Hoàn thiện sửa/impact/migration.** Năm checkpoint hiện có đường tạo/approve nhưng thiếu official reject/migration; một bộ checkpoint mới chưa đồng nghĩa production đã sửa video cũ an toàn. Approval phải serialize cùng writer và giữ nguyên phản hồi thật.
4. **Chặn submit ở granularity request.** Stop ở vòng phase không đủ khi batch/scene loop tiếp tục gửi bên trong adapter. Đường collect không được bị stop chặn vì vẫn cần thu phần đã gửi.
5. **Chuyển renderer thật.** Helpers chọn English portrait không sửa việc adapter hiện còn chọn VI timeline và chạy Node local. Xác minh nơi thực thi bằng runner/manifest/probe artifact, không bằng nhãn dashboard.
6. **Hoàn thiện nguồn dữ liệu web/account.** Tám tab phải lấy events, request owner, checkpoint và assets cùng job. Bộ đếm/usage/auth cần dữ liệu độc lập rõ source/uncertainty; chưa kết nối không khởi tạo clock live.
7. **Kho history cần phân loại theo chức năng.** Đường request, checkpoint và control trong runs chưa được `classify` bảo vệ như lịch sử. Job paths rộng không được cho sửa quyết định/journal trực tiếp.

## Kiểm đã chạy trong lượt audit

Dùng interpreter core sẵn có của checkout gốc, chỉ import mã checkout phát triển; không đọc/copy state, job, profile, auth hay tạo provider request. Các test dùng temp directory và fixtures.

| Bộ kiểm | Kết quả quan sát | Phạm vi chứng minh |
|---|---|---|
| `tests.test_permissions` | 5/5 đạt | Store quyền bền, scope/revoke/path escape, system/history/auth protection đã được liệt kê trong test |
| `tests.test_channel_profile` | 3/3 đạt | Profile mới→bank→brief, B1+ default, scene_count theo job, brief đã lưu không bị profile mới viết lại |
| `tests.test_output_contract` | 7/7 đạt | English portrait schema/anchors/coverage/voice-rate và Node outputPlans chọn track/cues/portrait props đã cấp |

Tổng **15/15**, 0,065 giây theo unittest. System Python mặc định thiếu jsonschema nên lần đầu chỉ 5 permissions chạy được; đây là giới hạn môi trường clone cần bootstrap phân biệt, không là lỗi provider hoặc chất lượng sản phẩm. Dùng interpreter có dependencies đã giải quyết phép kiểm import; chưa cài hay đổi môi trường người dùng.

Những phép kiểm trên **không** chứng minh execution v4 toàn tuyến, không-review registration, more-than-six repairs, đồng bộ web browser, T4 thật, âm thanh/phát âm, hình/continuity hoặc render Colab/MP4 thật.

## Kịch bản nghiệm thu ưu tiên khi code đã ghép

| Tình huống | Phép kiểm cần quan sát |
|---|---|
| Hai controller cùng job | Lease thứ hai bị chặn khi process thứ nhất sống; observer vẫn đọc; stop drain inflight; crash/resume không nhân đôi request |
| Auto đầy đủ | Plan lưu trước chạy; author action→outline/dialogue không human gate; WAV/ảnh/MP4 cập nhật; mọi reviewer spy đều không bị gọi, kể cả registration |
| Review đầy đủ | Chỉ bước hiện tại chạy; stale revision/feedback bị từ chối; exact outline/dialogue/audio/images/video approvals cho bước phụ thuộc tiếp tục |
| Sửa nhiều có tiến bộ | Hơn sáu repair đủ evidence vẫn được thực hiện; cùng fingerprint/input/strategy không evidence mới bị needs_attention; recovery mạng giữ episode riêng |
| Chỉ sửa ảnh một job cũ | Sense/narration/WAV không đổi; chỉ images/render phiên bản mới, snapshots cũ còn nguyên; unknown request cũ được collect trước |
| English portrait từ bank đến MP4 | B1+ một sense, English coverage/anchors thật; request giọng/rate brief; en WAV/cues; portrait timeline; remote renderer thu MP4 đúng streams/duration/assets |
| Web hai mode | Mở browser/server thật; tám tab dùng cùng event/job/revision; audio/ảnh/video nghe/xem/tải được; control stop/review tác động thật, không state mock |
| Clone và trở lại | Clone không home/profile/token/model; setup report chỉ phần đã kiểm; new controller thấy grant/checkpoint/inflight và tiếp tục account/session gốc |
| Ngân sách 0.4 | Token không chạy clock; connected T4 bắt đầu; idle/uncertain/cross-window; thiếu 5h usable chặn submit; Flow unknown giữ slot; pin và alias identity giữ đúng |
| Thu và dọn | Artifact final local durable trước release; evidence/journal/unknown giữ; generated cache chỉ xóa theo manifest không owner; Git allowlist không secret |

Chỉ đánh dấu hoàn tất từng hàng khi có bằng chứng đúng phạm vi. Mã fixture đạt và dịch vụ thật đã kiểm là hai loại bằng chứng riêng, cần ghi riêng trong báo cáo cuối.
