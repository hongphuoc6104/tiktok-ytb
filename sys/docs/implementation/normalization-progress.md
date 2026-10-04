# Bàn giao triển khai chuẩn hóa Video Pilot

Ngày 03/10/2026. Trạng thái: **đang triển khai, chưa hoàn tất**.

## Latest verified state after the user's voice and prompt-template changes

- The original full run passed 469/469 with 127 source hashes stable; later changes have their own targeted evidence. Do not apply that older result to the newest tree without the final combined run.
- Active entry points, five Rules, operational definitions and four Skills now use English instructions. User chat/UI stay Vietnamese. Plans, historical reports, user feedback and saved media evidence remain unchanged. Thirty-six active Markdown files passed link/language checks.
- Twenty local Colab aliases represent fifteen provider-verified Google identities. Duplicate aliases share counters; fifteen distinct identities were selected. Secrets and account maps stay outside tracked documentation.
- Real account-02 T4 setup and assembly produced an Alba trial (51.29 seconds). After the user selected the main English voice, exact reference-narrator assets were copied to the development tree and the missing main-project asset directory; SHA-256 `97d5aee4bc5bbb4a5951a180c04954f5f33b36e901f9a99084ec9f2ebb1817e9`, 3.24 seconds, mono PCM16/48 kHz.
- Default English voice is now reference-narrator at 0.92. Ninety targeted voice/routing/legacy checks passed. Saved Alba jobs retain their references; no old audio was overwritten.
- Real reference-narrator WAV exists at `runs/normalization-oversleep-english-9x16-001/revisions/audio/5/narration.wav`: 43.02 seconds, exact reference identity/hash. It is **not technically complete** because the saved trial window is 45–90 seconds. A same-sense narration repair is pending; do not silently shorten the brief window or change the requested speed.
- Narrator3 timed-out preparation was reconciled before replay: remote request, worker and output were absent, so no generation had been sent. A single same-owner retry collected the WAV; the dedicated T4 was then released. Actual allocation disappearance is confirmed by authenticated provider assignment evidence, never inferred from a missing local session name.
- Profile4 has a real downloaded Flow character reference. The subsequent registration was known not-submitted because the copied reference lacked its real media ID; the adapter now resolves provider IDs from verified downloaded journal/sidecar bytes, with targeted tests. Final story/action/diagram/continuity images and other-profile one-image tests are still incomplete.
- Setup/UI runtime QA passed 14/14; per-model Flow compiler passed 10/10, but compiler-to-runtime pin integration is still in progress. The existing trial has downloaded legacy prompts and must not acquire a new template pin retroactively.
- Remaining completion evidence: technically valid new-voice WAV, final Flow set and per-profile finite tests, real remote MP4, both-mode/recovery demonstration, final combined regression and safe integration into the main checkout. Goal remains active.

## Cập nhật 16:16 ngày 03/10 — thay thế các nhận định tiến độ cũ bên dưới

- Đã triển khai engine v4, grant, checkpoint, mode/lease/migration; QA độc lập 15/15 đạt sau sửa bốn lỗi thực. Báo cáo `../../reports/normalization/qa-engine.md`.
- Đã có dashboard 8 tab, setup, kho tài khoản/budget, đường xử lý audio/render remote và hồ sơ English9:16/2D/character. Các kiểm chứng hiện tại dùng fixture; chưa có Colab T4/Flow/video thật.
- Root vừa sửa cap Flow dùng chung các operation/alias, credential refreshable hết hạn không báo logout, phân loại 429/503 và chặn reserve ở cửa sổ mới tới khi kiểm dịch vụ thật. 17 kiểm tập trung đạt. Root sở hữu account_budget.py và dashboard/colab_probe.py ở đợt này.
- Worker remote đang sửa kiểm props/track ngôn ngữ, rollover Client và manifest audio đủ file; QA remote sẽ chạy lại độc lập. Root còn nối budget/đúng profile vào ranh giới gửi Flow thật và đóng băng config Flow theo job.
- Bảo trì/Git an toàn, audit mọi tài liệu/link và thử artifact thật còn thiếu. Chưa nhập thay đổi vào checkout chính, chưa commit/push và chưa đánh dấu goal complete.
- Ghi giải pháp hiện tại ở `../../logs/issues/ISSUE-20261003-normalization-qa.md`.

## Cập nhật sau đăng nhập — 17:00 ngày 03/10

- Người dùng đã cho phép mở Colab CLI và thử một ảnh Flow mỗi profile. Terminal thật kiểm 5 hồ sơ cũ rồi mở thêm OAuth. Sau 20 hồ sơ, đã xác minh trực tiếp Google userinfo và Colab list_assignments: **15 tài khoản Google riêng biệt**, không còn thiếu; 5 hồ sơ trùng được giữ, dùng chung identity/bộ đếm. Báo cáo có định danh nằm trong `.state/colab-account-verification.json`, không đưa email/token vào tài liệu Git.
- Pool phiên chọn 15 Colab identity duy nhất; vẫn giữ các credential alias và request pins cũ. Inventory hiện có 15 Chrome thường, 10 alias CDP và Brave/Firefox (27 mục Flow), không coi alias CDP là thêm tài khoản Google.
- QA remote/web độc lập đã kiểm **16/16 mới + 57/57 hiện có**, gồm actual Python caller→B2 send boundary với socket giả và Node queue thật/UI giả; browser thật hiển thị/giải mã WAV/PNG/MP4 fixture. Chưa có ảnh Flow/T4/WAV/video provider thật.
- Profile setup **22/22** kiểm đạt, phân biệt endpoint bị từ chối với timeout, giữ lock/marker và chỉ cho khởi động lại khi đã xác minh chủ sở hữu chết. Chưa mở profile hay tạo ảnh thật ở mục này.
- Bảo trì đang sửa các phát hiện QA độc lập về scope owner thật, archive/lease, outgoing Git history, secrets, hooks và refs/tags. Chưa nghiệm thu cleanup/Git trên dự án thật; không chạy commit/push trong checkout người dùng.
- Full suite handle **83546** đã kết thúc: **457 kiểm, 2 failures và 1 error, 316,334 giây**; log `../../reports/normalization/full-suite.log`. Hai failures thuộc maintenance lúc worker đang sửa; error còn phải đối chiếu. Chưa phải lần nghiệm thu cuối; chạy lại sau các sửa cần thiết trên trạng thái ghép ổn định.
- Dashboard do root sở hữu chạy tại `127.0.0.1:8765`, handle **37601**. Handle cũ **70245** đã dừng đúng PID sau xác minh không có operation đang chạy. Trang tài khoản hiển thị email Google đã xác minh, profile metadata tương ứng và duplicate; phần hiển thị counter Flow riêng với Colab vẫn cần hoàn thiện.
- Còn năm gói để nghiệm thu toàn mục tiêu: Flow một ảnh/profile; T4→WAV/ảnh/timeline→MP4 thật theo hướng mới; auto/review + stop/resume/repair cuối trên cùng web; đóng lỗi maintenance/full suite/setup; audit/đưa bản đã kiểm vào checkout chính và bàn giao. Goal vẫn active, chưa hoàn tất.

## Cập nhật 17:05 ngày 03/10

- QA maintenance cuối **28/28 đạt**, hash runtime/docs/test ổn định trong lượt kiểm; worker bổ sung **20/20**. Các lỗi owner/đường dẫn, scope archive/lease, cache_dir xuyên job, outgoing history/secret, hooks và tags đã có kiểm độc lập. Chưa commit/push/dọn dữ liệu thật.
- Error full suite còn lại là fixture CLI fresh-process chỉ sao chép runtime v3, thiếu execution.py. Đã sửa fixture sao chép Python runtime thực và dùng sys.executable, giữ nguyên kiểm resume đúng job/review. Cần chạy lại bộ phù hợp rồi full suite cuối, không lấy kết quả 457 cũ làm kết quả bản đã sửa.

## Ngữ cảnh đã rút gọn

Mục tiêu đầy đủ: sửa dự án theo `../plans/20261003-ke-hoach-chuan-hoa-quyen-mode-va-tai-lieu.md`, bao gồm mục 15 về hướng video mới. Không thu hẹp thành chỉ sửa tài liệu hoặc chỉ giữ test cũ xanh.

Checkout phát triển: `/home/hongphuoc6104/.codex/worktrees/normalize-video-workflow/pipelineFlow`, nhánh `codex/normalize-video-workflow`, bắt đầu từ `80e61cd7`. Checkout gốc `/home/hongphuoc6104/Desktop/pipelineFlow` giữ job, profile, token và những sửa local của người dùng. Kế hoạch và AGENTS/INDEX hiện tại đã được sao chép vào checkout phát triển; không sao chép state/job/auth.

Người dùng đã yêu cầu triển khai toàn kế hoạch. Quyền hoạt động: development trong phạm vi chuẩn hóa này. Không cần hỏi lại quyền đọc/sửa/test tương ứng; không giả quyền sản xuất/live generation hoặc nhận baseline của một job cụ thể chưa được kiểm trạng thái/diff.

Không tạo subagent khi chưa có yêu cầu phù hợp. Dùng skill-creator cho skill. Nếu tạo/cập nhật mô phỏng, đọc đầy đủ visualize skill trước thực hiện; hiện không có tác vụ mô phỏng mới.

## Yêu cầu phải chứng minh hoàn tất

- [ ] INDEX/README/AGENTS/GEMINI ngắn, không lặp chính sách hoặc mô tả sai khả năng.
- [ ] Rules có nguồn duy nhất cho permissions/execution/accounts/brand; phân loại file theo chức năng.
- [ ] Bốn skill setup/production/development/maintenance thay discovery cũ; references nghề giữ đủ nội dung và mọi caller/link được cập nhật.
- [ ] Grant bền vững theo phạm vi; một quyền hoạt động/quy trình; production sửa nội dung/job cũ không hỏi lại quyền đã cấp.
- [ ] Compatibility/version thay hash blanket cho engine mới; provenance/migration đúng công cụ; legacy giữ lịch sử.
- [ ] Observe không ghi, ownership/stop/resume/takeover không double submit giữa chat.
- [ ] Auto thực hiện tổng plan/micro-plan, không reviewer hoặc cap tổng sửa; no-progress chặn lặp không có evidence mới.
- [ ] Review chờ outline, lời thoại, WAV, bộ ảnh, MP4 đúng phiên bản; mode transition có sự kiện chính thức.
- [ ] Web thật 8 tab, cùng dữ liệu/event/artifact với CLI, không lấy stdout hoặc mock làm evidence hiển thị.
- [ ] Setup clone/chat mới và account selection không mang home/profile/model cũ; auth khác capability/budget, không lộ secret.
- [ ] Xử lý nặng audio/media/timeline/subtitles/render trên Colab, Flow tạo ảnh; không fallback local âm thầm.
- [ ] Profile English B1+ một nghĩa từ kho, 2D nền sáng viền đậm, hình vẽ 2D rõ ràng mọi khung; giọng/rate theo brief, không hài/SFX/hình-count mặc định.
- [ ] English9:16 đúng narration/coverage/anchors/audio/cues/timeline/render, ngôn ngữ độc lập tỷ lệ.
- [ ] Bảo trì chỉ xóa tái tạo được; Git allowlist/branch/secret check, không force-push hoặc tự tạo lịch chưa có tần suất.
- [ ] Test meaningful từng hợp đồng và luồng cô lập; live proof từng bước chỉ khi phạm vi thực sự được phép/capability có.

## Bằng chứng khởi đầu

- Goal đang active, không có token budget.
- Rà process checkout gốc không thấy pilot run/resume/batch hoặc colab synthesize/start/setup đang chạy.
- Đã sửa bốn điểm vào/Rules/workflow/setup/session docs và tạo bốn skill/references; chuyển skill cũ vào docs/legacy, cập nhật director_context/agy_pipeline bindings. Chưa sửa job hoặc coreengine.
- Baseline hoàn tất trước implementation:295 tests,5failures/16errors/231.869s. Config remote/Adam/rate1.08 khác fixtures; thiếu scipy và pathsvenv/node_moduleshardcoded. Summary tại sys/reports/normalization/baseline.json.

## Gói đang làm

P1 đã có code/tài liệu:4skill structurevalid; testcaller paths đang cập nhật; cần audit active docslinks. Tiếp theo: ngôn ngữ/tỷ lệ và profile, rồi enginequyền/mode/remote/web. Chưa coi P1 hoàn tất nghiệm thu toàn phạm vi.

Đã đọc skill-creator toàn bộ và openai_yaml reference. Kế hoạch đầy đủ nằm trong `sys/docs/plans/`; các bản 0.1/0.2 là lịch sử, không nhập auto reviewer/render local vào hướng đích.

## Quy tắc nghiệm thu

Mỗi mục trên cần file/command/test/artifact hiện tại chứng minh đúng phạm vi. Fixture chứng minh logic, không chứng minh Flow/T4/giọng/video thật. Không đánh dấu goal complete nếu remote/web/kiểm từng bước còn thiếu. Ghi phần thiếu và tiếp tục các việc có thể làm; không đổi mục tiêu để khớp phần đã làm.

## Bàn giao sau gói đầu

- Đã sửa bốn tệp gốc; Rules permissions/execution/accounts; production chỉ là adapter; brand_tolerance giữ nguồn identity.
- Bốn skill mới đã validate cấu trúc. Các loader thực (director_context/agy_pipeline) dùng đường dẫn mới; oldskills ở sys/docs/legacy/skills-v3 ngoài discovery.
- Đã có output_contract.py, schema outputs, anchors EN-only, validators/estimates theo languages, renderer outputs chọn track/timeline/cue độc lập aspect. Đây mới là hợp đồng/routing unit, chưa đủ toàn audio/Colab/render chain.
- Kiểm hiện tại: test_agy_adapter9/9, test_direction13/13, test_output_contract7/7, test_story_v3 26/26. Tổng55 targeted checks pass; baseline295 trước thay đổi có5failures/16errors.
- Chưa đổi channel/config/voice/profile; chưa có enginev4 grants/checkpoint/ownership/stop/migration; chưa bootstrap/web thật/remote-render. Goal vẫn active, không hoàn tất.
- Tác vụ tiếp theo: profile EnglishB1+ và bank dynamic scene planning/outputs; đồng bộ audio/payload/request và renderer props; engine mới giữ v3 history, rồi web/remote/bootstrap và audit đầy đủ.
- Không còn testprocess đang chạy ở cuối gói này. Các handles40637/7185/26577/73604/96148/93078 đã terminal; không poll hoặc restart chúng từ bàn giao.

## Current verified continuation — 2026-10-03

This section supersedes earlier incomplete implementation snapshots without rewriting history.

- Actual Colab T4 render collected: `normalization-oversleep-english-9x16-001/revisions/render/1/video.mp4`, English 1080x1920, 49.024 seconds, reference-narrator/.92, source audio6 retained. Report `reports/normalization/live-colab-render5-20261003.json` records exact request/input/output hashes and released dedicated runtime. No full viewing/listening claim.
- Actual SC04 render still displays unapproved instruction text. Official targeted images rejection recorded for IM04 only; dialogue/audio remain accepted. Replacement image/MP4 are pending.
- Modern duration ranges are estimates; 7/7 duration-contract tests pass after fixing a missing test import. Positive finite PCM/header/timeline/hash and exact-current-WAV checks remain required. No audio retake to fit seconds.
- Serial Flow profile trial default bridge precharge bug reproduced and repaired; 6 controlled transport checks pass. Inventory includes 15 source Chrome profiles, 8 with existing managed candidates and 7 requiring login. Metadata correlation does not prove Flow authentication. Live all-profile image trials remain pending.
- Browser Profile4 still lives, but the worktree control socket is connection-refused and no session daemon is running. Safe official stale-daemon recovery is being developed; no generation restarted from a timeout.
- Final suite for current changes is running, result not yet claimed. Main-checkout integration, actual targeted image repair/rerender, all-profile trials and final requirement audit remain open. Goal active.

## Session closure implementation authorized

User authorized remaining live tests and main integration. Actual IM04 replacement images5 collected; six other hashes unchanged, audio6 retained. Flow template1.0.0 actual Nano Banana Pro sample downloaded (live-flow-template-v1.json), brightflatstyle/no unwantedtext but character edge cropped, so composition acceptance pending. Colab render6 allocated/setup, official bind-session refresh performed; render pending. Current suite v2 running. Main integration exact195-path allowlist prepared; two root conflicts preserve user discipline and plan references. No goal completion claimed.
