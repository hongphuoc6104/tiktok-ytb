# Manifest tích hợp chuẩn hóa — chỉ đọc

Snapshot ngày03/10/2026. **Chưa triển khai, sao chép, commit/push, migrate/adopt hoặc khởi chạy job**. Nguồn là worktree `codex/normalize-video-workflow`; đích là checkout `video-vocabulary`. Cả hai HEAD tại `80e61cd7a93721f3aaa9c6797fae6458aeb8d01e`. JSON cạnh báo cáo ghi chính xác từng đường dẫn, operation, category, ba hash base/main/proposed và diff ba chiều. Root/worker còn sửa Flow prompt/UI/runtime; snapshot này **không tuyên bố nguồn đã ổn định**.

## Danh sách bàn giao cụ thể

Snapshot có265 đường dẫn đổi/thêm/xóa:215 candidate add/replace,17 tệp skill cũ cần xóa khỏi discovery sau khi archive được kiểm,2 conflict ba chiều và2 dữ liệu production bị loại riêng. Các tệp còn lại đã giống byte ở đích, chủ yếu plan/reference assets do root đã đưa vào trước.

Kiểm lại ngay sau viết đã thấy drift ở `sys/docs/flow-prompts.md`, `sys/flow_management.py`, `sys/image_pipeline.py`, `sys/tests/test_flow_prompt_integration.py`, report narrator4 và screenshot browser fixture. JSON giữ hash snapshot và hash mới riêng; **không copy theo snapshot cũ trước khi refresh**. Điều này là bằng chứng worker còn làm, không phải lỗi toàn vẹn job hoặc lý do tự nhận baseline.

| Nhóm | Số đường dẫn snapshot | Cách tích hợp |
|---|---:|---|
| Runtime |46| Các Python/Colab bridge/Flow adapter/dashboard scripts liên quan, kiểm hash trước nhận |
| Tests |38| Test runtime/independent/bank mới và cập nhật; giữ failing reproduction/history |
| Skills |34| Bốn skill mới/references;17 deletion active cũ chỉ sau archive match |
| Rules |5| Nguồn quyền/mode/accounts/brand và adapter |
| Root entrypoints |5| AGENTS/INDEX conflict cần merge; README/GEMINI/gitignore theo manifest |
| Schemas |5| Tương thích/migration đúng tool; không nhận baseline job ngầm |
| Config |1| Review diff config riêng, giữ per-machine identity/session/account của đích |
| Renderer remote source |3| Package source cho remote; không cài renderer local |
| Documentation |27| Active setup/workflow/voice/prompt/implementation/plans, không dùng status cũ làm capability hiện tại |
| Legacy archive |27| Giữ provenance/byte lịch sử; không discovery skill cũ |
| Control dependencies |4| Pinned manifest/lock/loader/import-check; không node_modules |
| Versioned Flow prompts |3| Compiler/package/registry1.0.0; pin trước submit; job/reference đã có request giữ legacy prompt |
| Assets |3| reference-narrator README/profile/WAV; main đã có cùng bytes, giữ đúng hash |
| Vocabulary |5| bank.py/test/profile/bank có rank policy; ledger/trial brief loại |
| Evidence reports |59| Optional developer handoff artifacts, xét scope thật/fixture; không coi report là sản phẩm hoặc publish |

JSON là allowlist thực tế; bảng không cho phép copy nguyên directory. Các số là snapshot, phải tái tạo khi worker còn thêm/đổi.

## Hai conflict cần hợp nhất với sửa của người dùng

**AGENTS.md**: main thay từ base gồm kỷ luật end-to-end, tái hiện bug theo flow người dùng, issue solutions; mở scope development khi thay đổi cần thiết rõ cho job; gửi artifact ngay; quyền agent nhận code sau xác nhận đúng job; bảo toàn job v3. Proposed viết gọn nguồn quyền/mode và thay ba gate/caps bằng contract mới. Phải giữ tinh thần các yêu cầu thật về hoàn tất/tái hiện/log/artifact/provenance, đồng thời reconcile nội dung ba gate/caps theo yêu cầu mới hơn. Không overwrite AGENTS người dùng bằng file worktree chỉ vì mới hơn.

**INDEX.md**: main thêm16 dòng liên kết các plan0.2/0.3/0.4, quyết định8tab và thứ tự setup. Proposed rút gọn navigation và trỏ implementation progress. Lưu nguyên bản main và chuyển các liên kết/kết luận đã chốt vào docs/plans hoặc mục lục phù hợp; phân loại trạng thái “chưa triển khai” của plan là lịch sử. Không xóa nguồn quyết định khi rút gọn điểm vào.

JSON lưu đầy đủ main-vs-base và proposed-vs-main cho hai file, cùng hash. Các plan/report/research main-only không nằm allowlist thay thế được giữ nguyên. Main chưa có runtime đổi khác so base ở lượt đọc này.

## Dữ liệu tuyệt đối không chuyển từ worktree

- `sys/vocab/ledger.json`: worktree đang reserved `oversleep.v` cho `normalization-oversleep-english-9x16-001`; **main không có entry này, chưa reserved**, đã kiểm bytes/JSON thật. Không copy ledger để giả trạng thái production.
- `sys/vocab/briefs/normalization-oversleep-english-9x16-001.json`: brief thử riêng. Nếu cần bàn giao job/artifact, root lập storage/official bank reservation/job migration plan đúng cùng request/account/session, không copy raw brief/ledger hoặc tạo job thay để né unknown.
- `.state`, runs, video sản xuất, token/cookie/profiles, `.gflow`, browser results, machine.local/browser-profiles, scratch/cache, node_modules/.venv/model: preserve tại main, không đồng bộ từ worktree. Shared per-user Colab/management/control stores không là source deploy.
- Evidence reports có thể lưu riêng nhưng không phát hành WAV/MP4 hoặc raw provider cache như thành phẩm. Không publish content-releaseartifact tự động.

## Chứng minh thay đổi kho từ

Base và proposed đều5541 mục/5541 ID, cùng ID; **mọi field ngoài rank bằng nhau**. Canonical JSON theo ID, bỏ riêng rank, hash hai bên cùng:

`e2efaebf946bdb52060b87bd32a944779d8487bf8a5f676d6ab332db1a2c1a85`.

Chỉ1554 rank đổi. Điều này bảo toàn nghĩa/word/CEFR/source/siblings/topics và nội dung học; rank vẫn làm đổi thứ tự chọn mặc định nên cần review chính sách xếp hạng trước nhận. Không rebuild hoặc chỉnh main ledger trong audit; sourcebank changes là deployable code/data candidate có chứng minh, chưa áp dụng.

`prompt_templates.py` hiện byte bằng base; không bị thay để hợp thức hóa job.17 file skill active bị xóa đều có archive `sys/docs/legacy/skills-v3/...` bằng đúng byte base, hash ghi trong JSON.

## Job main và baseline

Kiểm metadata thấy5 thư mục job:2workflowv3 và3không workflow. JSON ghi workflow/integrity hashes theo job, không sửa history. Không autorun/resume/adopt job sau nhận source. V3 giữ contract lịch sử đến khi root inventory requests/decisions/artifacts/owner/account/session và kiểm compatibility trên bản sao. Adoption/migration chỉ official command, đúng development scope; rollback có provenance, giữ baseline cũ và immutable snapshots.

Thay đổi docs/tests không tự lock v4 blanket; v3 baseline rộng có thể khác sau integration, phải báo diff thật. Không edit integrity.json/DB/journal hoặc tạo job cùng nội dung để né.

## Giọng, prompt và docs hiện hành

New English profile hiện là **reference-narrator0.92**, theo steering mới nhất. Reference WAV hash `97d5aee4bc5bbb4a5951a180c04954f5f33b36e901f9a99084ec9f2ebb1817e9`; đo file3,24s. Main đã có cùng asset, không cần overwrite. Job cũ Alba/Minh Quân giữ lựa chọn đã lưu. Các profile `listening_verified`/notes là claim lịch sử, không chứng minh QA đã nghe synthesis T4 hiện tại; JSON ghi từng profile/hash/scope. Không tái nhập Alba default từ report QA cũ vào config/brief mới.

Audit34 active doc/skill files không link file hỏng. **Gap cụ thể:** docs/flow-prompts.md và registry `flow_prompts/versions/1.0.0/registry.json` tồn tại nhưng docs/INDEX chưa dẫn prompt registry guide. Root thêm link trước bàn giao để clone/chat mới tìm đúng contract, không dùng prompt generic cũ cho job mới có pin. Legacy reference/Alpha requests vẫn giữ generic prompt đã gửi; compiler pass không chứng minh UI attachment/model/cost/image quality.

## Kiểm cuối trước tích hợp

Report469 pass chỉ cho source snapshot cũ. Hiện **27 tệp trong127 hash của report ấy đã đổi**; JSON ghi danh sách cụ thể. Không viện469 như nghiệm thu source hiện tại. Latest selected-voice verified suite returncode0/40,342s, fixture-only; report trước có returncode1 vẫn giữ lịch sử. Cần chạy trên source đã freeze, không đổi test expectation chỉ để xanh:

1. `tests.test_selected_voice`, `tests.test_channel_profile`, `tests.test_output_contract`, `tests.test_colab_tts`, `tests.test_colab_worker`, `tests.test_audio`, `tests.test_audio_english_spans` cho defaultreference/rate và legacy explicitAlba.
2. `tests.test_flow_prompts`, `tests.test_flow_prompt_integration`, `tests.test_flow_reference_binding`, `tests.test_modern_images`, `tests.test_flow_status`, `tests.test_live_setup_edges` cho registry/pin/actualtemplate/reference/shortsocket.
3. `tests.test_independent_engine_contracts`, `tests.test_execution_v4`, `tests.test_permissions` cho quyền/review/auto/compatibility/migration/stop/owner.
4. `tests.test_independent_setup_runtime`, `tests.test_dashboard_setup`, `tests.test_colab_runtime_binding`, `tests.test_bootstrap_control`, `tests.test_profile_setup` cho setup/UI/session/control/runtime. Browser fixture có riêng proof scope; không gọi live account.
5. `tests.test_independent_maintenance_contracts`, `tests.test_maintenance`, `tests.test_independent_remote_web_contracts`, `tests.test_remote_render`, `tests.test_dashboard_browser` cho maintenance/web/remote routing.
6. Cuối freeze chạy bộ phù hợp/full suite với hash trước/sau ổn định; kiểm link active/4skill/registry/documentation và bank canonical proof. Bất kỳ source đổi giữa kiểm phải đánh dấu phạm vi chưa ổn định và kiểm lại phần ảnh hưởng.

Không có MP4/live end-to-end acceptance trong audit này. Root đang sửa narration/audio/reference43,02s và Flow/template; chưa thể nghiệm thu production/learning/payoff hoặc bàn giao thành phẩm. QA deployment manifest không thay kết quả live.

## Backup và thứ tự tích hợp cho root

Trước mutation, root tạo backup manifest đúng allowlist của main bytes/permissions/symlink metadata, gồm AGENTS/INDEX user edits, config, vocabulary bank/channel, oldactive skills và any destination collision. Dữ liệu job/auth không copy vào backup source package công khai; nếu cần backup trạng thái thì giữ private location theo official maintenance/archive policy. Record SHA/byte/source provenance và restore manifest trước thay.

Reconcile hai conflicts, freeze nguồn rồi refresh integration JSON/hash. Thêm source/schema/control/assets/docs/tests theo exact allowlist; giữ main-only untracked/history/auth/per-machine files. Chỉ bỏ active oldskills khi archive hash đã match và caller tests đạt. Review config diff riêng. Giữ main ledger/trialbrief state nguyên. Sau nhận, run doctor/observe chỉ đọc và targeted/full checks phù hợp; chưa autorun v3 job. Job acceptance/migration là bước riêng có scope/provenance/request inventory.

Rollback cần khôi phục đúng byte main trước integration và loại riêng các tệp newlyadded trong manifest, không wildcard dọn dự án; không hoàn nguyên journal/provider work mới hoặc xóa evidence. Nếu source checksum/target collision thay so snapshot, dừng phần copy và làm lại ba chiều. Manifest hiện là kết quả cụ thể sẵn review; không tự cấp quyền deployment/publish/Git hoặc nhận baseline.
