# QA độc lập engine — 03/10/2026

Kết quả hiện tại: **15/15 kiểm thử độc lập đạt, 12,633 giây**. Ban đầu 14 kiểm thử có ba lỗi; sau sửa đã đạt 14/14, kiểm thêm biến thể schema tìm được QA-E04, sau sửa QA chạy lại đủ 15/15. Lệnh bộ đầy đủ: `.venv/bin/python -m unittest discover -s tests -p test_independent_engine_contracts.py -v` từ `sys/`. Cả bốn reproduction đã được xác nhận sửa. Chưa nghiệm thu toàn kế hoạch.

Nguồn kiểm: toàn bộ kế hoạch `20261003-ke-hoach-chuan-hoa-quyen-mode-va-tai-lieu.md`, gồm mục 15; AGENTS/INDEX/Rules/skill development; code hiện tại. QA chỉ thêm `tests/test_independent_engine_contracts.py` và báo cáo này/JSON; không sửa runtime hay test cũ.

## Phạm vi bằng chứng

Mỗi tình huống tạo một dự án tạm `custom-project/sys` có launcher marker, schema/config và dữ liệu riêng. Thực thi thật: CLI parser/main trong tiến trình mới, grant, SQLite, lease, control, checkpoint, snapshot, quyết định, migration, rollback và issue journal. CLI dùng đúng code hiện tại, chỉ chuyển ROOT sang dự án tạm trước gọi main. Hai writer quyết định chạy đồng thời trong hai tiến trình. Cách viết lỗi/exit mô phỏng đúng entry point chính.

Chỉ thay callback nhà cung cấp audio/images/render và kiểm artifact remote để tránh tài khoản, GPU, Flow/Colab thật. Session/account có tên QA là metadata giả. File WAV/MP4 fixture là bytes giả; không dùng làm sản phẩm, bằng chứng phát âm/hình/chất lượng hoặc thông số media. Không gọi reviewer, live accounts, generation, push. Fixture nội dung dùng ví dụ sẵn có; không chứng minh hướng English B1+/2D9:16. Việc đọc/ghi SQLite do Pilot thực hiện, không sửa tay DB.

## Lỗi hành động được

### QA-E01 — schema không tương thích vẫn qua compatibility

- Tái hiện: tạo v4 job; thay operational AGENTS (được phép tiếp tục); sau đó thêm `new_required_incompatible_key` vào `required` của schema `schemas/outline-v3.json`; gọi `p.integrity(job)`.
- Thực tế: không có lỗi/migration yêu cầu. `verify_compatibility` chỉ so sánh `integrity-meta.engine_contract` với hằng CONTRACT; không so với schema hiện hành. Khác biệt thực tế chỉ xuất hiện khi bước validation sử dụng schema mới.
- Yêu cầu: phân biệt tài liệu vận hành đổi với schema/engine không tương thích; kiểm provenance/tương thích trước chạy tiếp, dừng đúng phần khi chưa có migration. Không quay về hash blanket toàn repo hoặc khóa audio/ảnh chỉ do sửa hướng dẫn.
- Test: `test_guidance_change_allowed_but_incompatible_schema_requires_migration`.
- Đã sửa: metadata lưu schema snapshot; compatibility chặn required bị thu hẹp. QA độc lập xác nhận test gốc và biến thể QA-E04 đều đạt.

### QA-E02 — micro-plan API có tranh chấp check/append

- Tái hiện: hai Pilot trên cùng root cùng gọi `execution.micro_plan` với đúng một fingerprint/evidence. Test đồng bộ điểm gọi settings sau đọc lịch sử và trước append; không đổi kết quả đọc/ghi DB.
- Thực tế: cả hai trả accepted và lưu cùng chiến lược thất bại; CLI có lease nhưng API không tự bảo vệ hoặc bắt buộc owner.
- Yêu cầu: đúng một writer/target và no-progress phải bền xuyên controller, không chỉ áp dụng cho đường CLI. Cần lease/check và append nguyên tử; nếu gọi dưới lease hiện hữu thì không tự khóa lồng gây hỏng reject/image repair.
- Test: `test_parallel_api_micro_plans_cannot_duplicate_identical_recovery`.
- Đã sửa: micro-plan.lock tuần tự hóa history-check/append cho API. QA độc lập xác nhận chỉ một caller lưu recovery.

### QA-E03 — session sai để lại job chưa hoàn chỉnh không thể tiếp tục

- Tái hiện: session đã chọn; gọi `execution.new` cùng brief/grant hợp lệ và `session_id='incorrect-session'`.
- Thực tế: trả ValueError sau khi `p.new` đã tạo runs/job, DB rows, control revision và integrity; workflow v4 chưa ghi. Thử lại cùng job sẽ gặp Job already exists; không có settings v4 để resume bình thường.
- Yêu cầu: kiểm session/đầu vào trước durable creation hoặc rollback bằng công cụ có provenance. Không yêu cầu người dùng tạo job thay để né trạng thái dở.
- Test: `test_wrong_management_session_does_not_leave_unresumable_partial_job`.
- Đã sửa: session snapshot và validation diễn ra trước p.new. QA độc lập xác nhận session sai không để lại job/DB rows.

### QA-E04 — bỏ property dưới schema đóng vẫn bị coi tương thích

- Tái hiện sau sửa QA-E01: v4 job lưu schema snapshot; xóa `properties.outline` trong `outline-v3.json`, giữ `additionalProperties=false` và `required=['outline']`; gọi `p.integrity(job)`.
- Thực tế: không lỗi. Schema mới từ chối mọi outline đã hợp lệ vì trường bắt buộc đồng thời bị coi trường dư. `_schema_compatible` chỉ duyệt properties của schema mới nên không xét properties đã bị xóa.
- Yêu cầu: xét cả properties cũ bị bỏ so với additionalProperties mới; không chỉ xét property tồn tại trong schema mới.
- Test: `test_removing_allowed_property_under_closed_schema_requires_migration`; lệnh targeted thêm `-k removing_allowed_property`.
- Đã sửa: so sánh mọi property cũ bị bỏ với additionalProperties mới. QA chạy lại đầy đủ 15/15 đạt, bao gồm reproduction này. Các giải pháp QA-E01–E04 cần được engine_worker lưu vào issue log của dự án theo phạm vi sở hữu.

## Hành vi đã được chứng minh

| Yêu cầu | Bằng chứng cụ thể | Giới hạn |
|---|---|---|
| Quyền production bền qua chat/controller | CLI new tìm grant đã lưu, resume/status ở tiến trình mới giữ đúng grant; plan ghi scope/source/dependencies/accounts/location | Không chứng minh xác thực nguồn cấp quyền từ chat; code khai báo transport_verified=false |
| Auto chạy tới kết quả, sửa cùng video, không reviewer | Các callback reviewer bị chặn AssertionError; auto hoàn tất; reject video rồi fresh Pilot resume tạo video revision2, giữ audio rows và hash checkpoint cũ | Fixture chỉ chứng minh điều phối/không gọi reviewer |
| Tổng plan và micro-plan | Plan có năm đầu ra, scope và Colab/Flow locations; repair tạo micro-plan đúng job | Chưa chứng minh agent tự chẩn đoán nguyên nhân/tra issue hoặc internet và thi hành toàn kế hoạch |
| Review đủ năm đầu ra đúng revision | Outline/dialogue/audio/images/video đều chờ; chạy tiếp khi chưa duyệt không gọi provider thêm; revision sai và quyết định cũ bị từ chối; quyết định cũ giữ hash | WAV/ảnh/video là fixture |
| Writer quyết định đồng thời | Hai CLI approve cùng outline revision1 chỉ có một thành công và đúng một decision/event | Một job/một checkpoint trong fixture |
| Dừng khi owner đang chạy | Audio callback đã submit rồi chờ; CLI stop ở tiến trình khác thành công; takeover live runner bị chặn; kết quả đã gửi được giữ; chưa tạo ảnh/video; resume chỉ tạo phần chưa gửi | Không có timeout/unknown provider thật |
| Tiếp quản runner chết | Tiến trình giữ lease bị kill riêng; takeover sau reaping thành công, outline checkpoint và request pin account/session giữ nguyên; resume không đổi checkpoint cũ | Request pin giả; chưa chứng minh reconcile unknown provider thật |
| Quan sát chỉ đọc | Trong khi có owner, observe_job không thay hash bất kỳ file trong root | SQLite đơn giản của fixture |
| Production không sửa hệ thống/lịch sử | Grant wildcard vẫn bị require chặn AGENTS/Rules/config/vocab code/renderer/schema/workflow; job khác ngoài scope bị chặn | Kiểm thao tác API; không là OS sandbox |
| Không cap tổng lượt sửa | 30 micro-plan khác input/evidence qua được; tám retake thật qua workflow cho SC01 tạo audio revision9, giữ image rows, vượt cap legacy tổng và từng cảnh | Adapter/check media được thay; chưa chứng minh chất lượng các take |
| No-progress xuyên controller | Fresh Pilot không nhận lại cùng input+strategy+evidence; unknown chỉ cho collect/reconcile; race API QA-E02 đã được sửa và QA xác nhận | Chưa đo tiến bộ chất lượng thật |
| Development migrate/rollback job cũ | Legacy content đã có quyết định thật trong fixture; migration giữ hash revisions/reviews/request/account/session pin/integrity baseline; rollback khôi phục toàn bộ hash file cũ | Rollback trước v4 execution; reverse migration sau phát sinh output cần phạm vi riêng |

## Phần còn thiếu cho toàn kế hoạch

Đây là kiểm engine và quyền, không thay P5/P6/live acceptance. Chưa có bằng chứng trong báo cáo này cho web 8 tab thật, event/artifact hiển thị trên web, login/quota/service restrictions, Colab T4 tổng hợp/thu WAV và render thật, Flow identity/base-reference/model thật, subtitle/timeline English9:16 đúng track, mascot nhỏ đúng core trong mỗi ảnh, chất lượng giọng/ảnh/câu chuyện/payoff. Cần QA riêng hoặc artifact thật có nguồn và revision.

Auto nhận `author_outline`/`author_dialogue` là handoff cho connected author; kiểm này không chứng minh ứng dụng tự chạy author đến cuối khi người dùng chỉ giao một yêu cầu mới. Micro-plan được tạo khi gọi reject/micro-plan; cần bằng chứng owner xử lý lỗi provider có kiểm soát, ghi kết quả/giải pháp và needs_attention khi hết hành động khả thi. Không dùng số test xanh để tuyên bố đã hoàn thành các phần còn thiếu này.

## Bàn giao

Đã chạy lại độc lập sau sửa runtime và giữ các reproduction trong bộ 15 test để chặn tái phát. JSON ghi output đầy đủ, hash mã và kết quả trước/sau sửa. Nếu runtime còn thay đổi liên quan thì chạy lại đúng phạm vi. Không tự sửa job/auth tại checkout gốc.
