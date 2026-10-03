# QA độc lập — remote, web, bootstrap, tài khoản và ngân sách

Rà tại checkout `codex/normalize-video-workflow`, ngày 03/10/2026. Phạm vi quyền development đã giao; chỉ thêm bộ kiểm độc lập và các tệp báo cáo `qa-remote-web.*`. Không sửa runtime, test cũ, state sản xuất, tài khoản hoặc secret. Các hợp đồng cô lập đã đạt sau sửa; QA này chưa chứng minh toàn bộ runtime provider thật.

Đã đọc INDEX/AGENTS, kế hoạch chuẩn hóa toàn bộ gồm mục 15, thiết kế 0.3/0.4 và skill vp-development. Các phép kiểm bên dưới dùng root/home/store tạm, tài khoản/GPU/model/provider giả có ghi nhãn. Không OAuth, cấp GPU, gọi Flow, tạo request provider, push hoặc sản xuất video thật.

**Kiểm lại cuối sau sửa của writer:** **16/16 phép kiểm độc lập đạt, 25.197 giây**; **57/57 phép kiểm hiện có đạt, 14.057 giây**. Toàn bộ RW01–RW09 đã qua kiểm hồi quy tương ứng; không bỏ hoặc nới các assert để làm xanh. Tổng 73 test đạt. Browser chạy bốn lượt, decode khung MP4 của fixture. Node queue thực thi contract chọn model và chặn sai model/URL bằng UI giả; replay unknown không Start thêm.

## Kết quả quan sát

| Phép kiểm | Kết quả | Điều đã chứng minh |
|---|---|---|
| Bộ hiện có remote/audio/accounts/dashboard | **57/57 đạt** | Transport và worker giả, hashes/bounds, ordering, technical schemas, API cơ bản. Log `qa-remote-web-targeted.log`. |
| Bộ độc lập mới | **16/16 đạt** sau writer sửa chín finding | Các assert giữ nguyên; lỗi ban đầu đã gửi để writer sửa. Log `qa-remote-web-independent.log` là kết quả mới nhất. |
| Browser Chromium thật + server thật + CLI subprocess thật trên root riêng | Đạt 4 lượt: auto revision 1→2, review revision 2→3 | Cả tám tab có nội dung; Media hiện đúng revision, WAV 1 giây đọc metadata được, PNG decode được, MP4 fixture 1 giây đọc metadata và decode khung hình được; controls khác theo mode; stale feedback bị từ chối; không lỗi JavaScript. |
| Chuỗi English 9:16 độc lập | Đạt với model/GPU/encoder giả | Adapter audio→request Alba tốc độ 0.87→WAV PCM thật của mô hình giả→schema→cues tiếng Anh→timeline dọc→adapter render→worker và manifest giả. Chỉ track en; lời “I see a predator.”; WAV/timeline 1.25 giây. Không gọi local master của adapter. |
| Bootstrap trước dependency | Đạt CLI `-I -S` thật | `check` không tạo state; jsonschema missing được báo; T4/auth/render not_tested; `apply` tạo venv quản lý không dependency; `resume` không tạo lại venv; không model, login, GPU hoặc renderer. |
| Hai controller render cùng request và timeout sau gửi | Đạt độc lập | Controller thứ hai bị REQUEST_BUSY; request khác bị PENDING_OTHER_REQUEST; sau timeout chỉ download trên account/session ban đầu dù default mới khác. Không exec/upload/generate lại. |
| Flow Python caller thực với socket/provider giả | Đạt độc lập | `image_pipeline.request → adapters.gflow → B2 queue` giữ profile/account/session, model/project/tool URL frozen dù global config đổi; mismatch chặn trước gửi; unknown giữ slot và chặn prompt đổi; cap 100 và quota hard-stop durable chặn request tiếp. Đây là reference request nội bộ trên root fixture, không giả approval cảnh. |
| Node send-contract thật với UI giả | Đạt độc lập | `prepareRequests/runQueue` chọn frozen model, giữ project identity, sai tool URL hoặc thiếu model bị từ chối. UI không áp model → FROZEN_FLOW_MODEL_MISMATCH trước Start. Unknown replay không gửi lần hai. Mã và kết quả `qa-remote-web-node-contract.*`. |
| HTTP Host/Origin/CSRF/path/redaction | Đạt độc lập | Host ngoài loopback, Origin sai, CSRF sai, job traversal và media ID không thuộc manifest bị chặn. Bearer literal được ẩn; session account không tồn tại bị từ chối không thay state. |
| Ngân sách Colab/Flow | Đạt logic và caller giả đã kiểm | Idle tính đủ, trần 5 giờ/dự phòng 1 giờ, alias dùng chung ledger; Colab qua 24 giờ phải recheck trước reserve, không ghi quota provider đã kiểm. Flow dùng phiên vận hành rõ, không tự reset ngày; uncertain của interval đã release không khóa session mới. |

Tệp browser gồm `qa-remote-web-browser.json`, mã kiểm `qa-remote-web-browser.mjs`, log và ảnh chụp theo mode/revision. Chuỗi synthetic có `qa-remote-web-chain.json`/`.log`. Các tệp này là bằng chứng kỹ thuật cô lập; không chứng nhận giọng, phát âm, mascot, hình học, T4 thật hoặc render Colab thật.

## Các lỗi đã phát hiện và kiểm lại sau sửa

| ID | Ưu tiên | Tái hiện và tác động | Vị trí, hướng sửa |
|---|---|---|---|
| RW01 | P1 | `flow_submit(profile-a, job-1:images, request-1, 100)` rồi unknown; cùng Google identity qua alias gửi `job-2:images/request-2` thêm 1 slot vẫn thành công. Đổi operation không được mở counter mới trong cùng phiên. | `account_budget.py:113–123`: cap chỉ cộng requests của một operation. Cần định danh phiên vận hành bền, counter chung identity/phiên, không namespace tùy ý theo job/phase. Test `test_flow_cap_is_shared_between_operations`. |
| RW02 | P1 | Không có caller runtime của `Budgets.flow_submit/flow_state`; hiện chỉ helper/tests dùng. `image_pipeline.request/batch_submit` gửi thật mà ledger ngân sách ảnh không được giữ slot/cập nhật; dashboard có thể luôn trống. | `image_pipeline.py:339` và `:442`, cùng adapter Flow. Nối giữ slot trước gửi tại mỗi request/batch, unknown giữ slot, thu và reconcile cập nhật cùng account/session/identity. Kiểm spy trên caller thật, không chỉ helper. |
| RW03 | P2 | Credential `valid=False, expired=True, refresh_token` hiện hữu bị báo `login_required` ngay, không hề có bằng chứng refresh token revoked. | `dashboard/colab_probe.py:32–34`: dùng trạng thái refresh-required/unverified phù hợp; giữ probe chỉ đọc, không tự refresh/login. Login-required chỉ khi credential không còn khả năng dùng hoặc auth expiry/revocation được xác nhận. Test `test_expired_refreshable_credential_is_not_relogin`. |
| RW04 | P1 | Allocation ở t=100; t=100+24h+1h ledger `needs_service_recheck=True` nhưng `Client._reserve(new-day-request,audio)` vẫn thành công dựa trên allocation ngày cũ. | `account_budget.py:87`, `colab_bridge/client.py:126–141`: chưa enforce recheck, chưa lưu xác nhận riêng theo window/account/session. Chặn submit mới, cho collect request dở; recheck thật mới mở lại phần chạy. Test `test_day_rollover_requires_service_recheck_before_new_work`. |
| RW05 | P1 | Request English 9:16; report tự khai outputs=en và duration/codec/hash hợp lệ. Đổi `props.primary_language=vi`, chỉ `tracks.vi` và cue Việt; validator vẫn nhận. | `colab_bridge/job_protocol.py:94–96`: chỉ kiểm outputs/aspect, chưa kiểm primary language/tracks/audioSrc/cues/timeline theo request. Kiểm đầy đủ provenance đầu vào và schema/shape nội dung thực tế, báo sai track trước import. Test `test_render_acceptance_rejects_wrong_props_language`. |
| RW06 | P2 | Userinfo endpoint trả 429 hoặc 503; probe báo `reason=network_unknown`; 403 thì đúng permission_unknown. | `dashboard/colab_probe.py:39–40`: bảo toàn rate-limit/quota/capacity reason của đúng endpoint; không gọi đây là quota GPU đã được xác nhận. Test `test_identity_probe_429_and_503_keep_correct_service_reason`. |
| RW07 | P1 | Sau sửa RW01, Flow ledger từng tự reset counter các request đã thu sau 24 giờ, dù vẫn cùng phiên vận hành. Cap 100/account/phiên của 0.4 không có reset ngày tự động; theo ngày chỉ là thống kê bổ sung. | `account_budget.py:flow_submit_many`: đã dùng budget_session thật, giữ counter phiên bền và unknown across phiên. Test `test_same_flow_operating_session_does_not_reset_after_24h` đã qua sau sửa. |
| RW08 | P2 | Một interval được đánh dấu uncertain, sau đó có xác nhận termination và T4 session mới; snapshot vẫn uncertain=True vì tính mọi interval lịch sử. Session mới bị _ready chặn mãi; recheck current session không xóa flag cũ. | `account_budget.py:snapshot/released`: readiness chỉ xét uncertain của interval đang được cấp hoặc clear uncertainty khi termination được xác nhận, vẫn giữ audit lịch sử. Test `test_confirmed_release_and_new_allocation_do_not_keep_old_uncertainty_active`. |
| RW09 | P1 | Provider báo quota, generationSubmitted=False. Journal được giữ not_submitted; ledger chỉ sync state, không có service block. Target khác cùng account/session được gửi và tải thành công ngay sau đó. | `flow_management.py:sync`: ghi error-category block durable theo service/request/episode. Quota/CAPTCHA/bot/login/429/503 dừng ngay; unknown chỉ collect/reconcile; không rotate. Phần cuối `test_actual_flow_request_hook_freezes_account_model_project_and_enforces_cap`. |

Các lỗi đã gửi trực tiếp tới agent gốc để writer đúng phạm vi xử lý. Người kiểm QA không sửa runtime. Agent gốc ghi issue log theo quyền của writer. Giải pháp đã kiểm lại: counter chung Flow identity/phiên; actual send hook giữ owner và slot; refresh-required khác login-required; Colab window mới cần recheck; props phải có primary/tracks/cues/timeline phù hợp request; 429/503 phân loại đúng endpoint; Flow không reset ngày tự động; uncertain lịch sử được tách khỏi readiness; quota và các hard-stop được ghi durable trước gửi mới. Cả chín finding đều đã qua assert hồi quy trong bộ 16 test cuối.

## Giới hạn còn phải nghiệm thu

- Không có live Flow/T4, login provider, phát âm hoặc chất lượng video trong đợt QA này. Fixtures không thay việc nghe/xem sản phẩm thật.
- Vai trò QA này chưa chạy capability probe Flow bằng browser/profile người dùng; inventory của phép kiểm browser dùng home trống và nhãn not_tested đúng. Agent gốc đang kiểm account/profile theo phạm vi mới người dùng cấp; bằng chứng live đó là một phần báo cáo riêng, không suy từ các fixture này.
- API kiểm security hữu hạn đã đạt các ca nêu trên; không tuyên bố chứng minh tuyệt đối mọi secret/SSRF/XSS. Frontend dùng textContent, CSP tự nguồn, artifact route allowlist và Host loopback; không có public arbitrary URL fetch route được tìm thấy.
- Browser dùng home trống để không chạm profile người dùng; tab Tài khoản hiển thị trạng thái trống thật. Account alias/budget/probe kiểm riêng trên fixture store, chưa là bằng chứng UI tài khoản live.
- Setup `--install` thật không chạy trong đợt QA; đường command pinned management deps được bộ hiện có kiểm bằng fake runner. CLI apply/resume không install đã chạy thật trước deps.

## Lệnh kiểm lại

Từ `sys/` trong worktree:

```text
PYTHONPATH=.:tests ./.venv/bin/python -m unittest tests.test_independent_remote_web_contracts.IndependentRemoteWebContracts -v
VP_PLAYWRIGHT_MODULE=/home/hongphuoc6104/Desktop/pipelineFlow/sys/node_modules/playwright PYTHONPATH=.:tests ./.venv/bin/python -m unittest tests.test_independent_remote_web_contracts.IndependentBrowserEngine -v
PYTHONPATH=.:tests ./.venv/bin/python -m unittest tests.test_remote_render tests.test_colab_tts tests.test_colab_worker tests.test_account_management tests.test_account_probe tests.test_dashboard tests.test_dashboard_engine -v
```

Các hợp đồng cô lập nêu trên đã đạt; chưa dùng kết quả này để đánh dấu hoàn tất T4/Flow/giọng/render Colab thật. Thu hồi thay đổi QA chỉ cần bỏ các tệp mới theo prefix/test; không có state/job sản xuất cần khôi phục.
