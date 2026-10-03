# QA độc lập bảo trì và tài liệu — 03/10/2026

Kết quả hiện tại: **28/28 tình huống độc lập đạt, 1,765 giây**, không failures/errors. Hash các nguồn maintenance/permissions/test/docs giữ nguyên từ đầu đến cuối lượt chạy. Mười phát hiện đều có reproduction được giữ trong bộ test và đã xác nhận sửa. Ban đầu 23 tình huống có bảy lỗi; QA phát hiện thêm directory reference, silent hook bypass và implicit tag push, rồi chạy lại độc lập sau sửa. Bộ mới: `tests/test_independent_maintenance_contracts.py`; lệnh từ sys: `.venv/bin/python -m unittest discover -s tests -p test_independent_maintenance_contracts.py -v`.

QA đọc đầy đủ kế hoạch chuẩn hóa, AGENTS/INDEX/Rules, skill maintenance, maintenance.py và tài liệu hiện hành. Chỉ viết test mới và báo cáo theo phạm vi giao; runtime/test cũ do worker khác sở hữu.

## Bằng chứng và phạm vi

Tất cả cleanup/archive/commit/push chạy trong dự án/repository/bare remote tạm riêng. Đây là các thao tác API/CLI và Git thực; không fake Git hoặc khóa. Các artifact chỉ chứa dữ liệu fixture và credential giả có tiền tố QA. Không cleanup, archive, commit/push hoặc chỉnh job/auth của dự án thật; không gọi provider/GPU/OAuth. Tên, hash, số file và trạng thái có ý nghĩa trong fixture, không chứng minh sao lưu GitHub/HDD hoặc quality media.

Help CLI chạy chỉ `--help`; không đăng nhập hoặc gửi yêu cầu. Audit link chỉ kiểm file mục tiêu tồn tại; đối chiếu policy/profile/skill có test riêng. Không lấy help/link pass làm bằng chứng capability dịch vụ đã chạy.

## Mười phát hiện đã gửi root/maintenance_docs_worker

| Mã | Cách tái hiện và thực tế | Yêu cầu sửa |
|---|---|---|
| QA-M01 | Grant chỉ job A, đường dẫn `sys/runs/**`; manifest ghi owner A nhưng candidate thật nằm `sys/runs/B/scratch/B-only.bin`. Job B có request unknown. Cleanup vẫn xóa candidate B. | Xác định owner từ đường dẫn thật, không cho manifest đổi nhãn; giữ unknown/request và job scope thực. |
| QA-M02 | Grant jobs A + path `video/**`; archive `video/B/final.mp4` thành công. | Archive phải kiểm job source thuộc grant, cùng path scope. |
| QA-M03 | Giữ lease `runs/A/execution-lease.lock`; archive artifact A vẫn copy. | Acquire lease các owner source trước copy; không dựa riêng process.lock của v3. |
| QA-M04 | Remote ở baseline; local đã có commit khác chưa push chứa `other-user-secret.md`. Chỉ cấp allowed.md; checkpoint tạo commit allowed.md rồi normal HEAD push đưa cả commit cũ ra remote. | Kiểm toàn outgoing commits/blobs/paths/secrets so với remote thật, trước commit/push; không chỉ working file mới. |
| QA-M05 | allowed.md chứa `refresh_token=QA_SYNTHETIC_SECRET_123456789` không có dấu nháy. git_plan chấp nhận. | Scanner phải bắt giá trị secret rõ ràng dạng unquoted, không in giá trị thật. |
| QA-M06 | Pre-commit hook chạy `git add -- other-user.md` sau allowlist check. Thành phẩm commit gồm allowed.md và other-user.md. | Bảo vệ tree thực sự commit và quyền staging; không cho hook kéo sửa local khác vào commit. Không bypass hook/check ngầm. |
| QA-M07 | Archive dry-run nhận `.env` chứa password fixture; private.pem cũng chưa có chặn extension. | Credential/environment/private key không là artifact archive, dù grant path rộng. |
| QA-M08 | Shared candidate `sys/.cache/shared-tts/repro.bin` khai owner A; request unknown job B có cache_dir trỏ directory chứa candidate. Audit chỉ dò từng file/basename nên cleanup xóa thành viên directory đang dùng. | Giữ phụ thuộc directory/cache_dir, không chỉ file đầy đủ; shared cache phải audit các owner/request liên quan. |
| QA-M09 | Fix M06 tắt mọi commit/push hook qua core.hooksPath=/dev/null. Hook exit1 vẫn cho commit/push thành công, trái với giữ required checks và docs nói hook failure dừng. | Không bypass kiểm tra có sẵn; nếu không chạy hook an toàn theo scope thì chặn trước mutation và nêu nguyên nhân. |
| QA-M10 | Git cấu hình push.followTags=true; explicit HEAD:branch push vẫn gửi thêm annotated user tag chưa được cấp. | Chặn followTags/mirror settings hoặc override rõ để chỉ gửi đúng ref đã cấp. |

Tên các test lỗi:

- `test_owner_field_cannot_relabel_other_job_cache_and_skip_its_unknown_request`
- `test_archive_cannot_expand_job_scope_with_broad_path_allowlist`
- `test_archive_does_not_copy_owned_artifact_while_writer_has_lease`
- `test_unreviewed_outgoing_history_cannot_be_pushed_with_allowed_checkpoint`
- `test_symlink_and_secret_plaintext_are_never_checkpointed`
- `test_commit_hook_cannot_include_other_user_files_in_allowlist_commit`
- `test_archive_does_not_copy_credential_files_under_broad_grant`
- `test_crossjob_pending_directory_reference_preserves_shared_cache_members`
- `test_failing_existing_hook_is_not_silently_bypassed`
- `test_push_followtags_config_cannot_transfer_ungranted_tag`

Worker đã sửa M01–M10; QA chạy lại độc lập xác nhận toàn bộ reproduction đạt. M09 hiện chặn hook thực thi đang có trước mutation để giữ required checks; không tắt hook ngầm. M10 dùng explicit no-follow-tags, không gửi tag của người dùng. Cần issue log + “Làm gì cho hết lỗi” cùng bằng chứng theo quy định dự án; worker sở hữu phần lưu log. QA không tự sửa runtime hoặc logs ngoài phần sở hữu.

## Hành vi đã chứng minh đạt trong lượt đầu

| Nhóm | Bằng chứng cụ thể |
|---|---|
| Cleanup qua CLI thật | Dry-run giữ candidate; execute đúng review hash xóa chính xác một file, giữ inputs/output hashes; intent và result đủ. |
| References | Metadata job khác trỏ absolute, project-relative hoặc basename đều giữ cache. Shared cache được request unknown tham chiếu cũng giữ; hardlink bị chặn. |
| Unknown | Nested submit_state unknown/ambiguous/submitted/running/inflight/generating/generated/not_collected ở owner đều chặn dọn và giữ nguyên journal hash. |
| Auth/lịch sử | Revisions, flow request history, profiles, token filenames, key/sqlite và symlink không được dọn. |
| Leases | Owner A, job B và v3 process lock còn writer đều chặn cleanup. |
| Review/grant | Proof đổi, review hash sai hoặc grant thu hồi đều không xóa file. |
| Archive đã cấp | Destination ngoài phải có scope riêng; copy kiểm hash và giữ nguồn; không ghi đè directory đã tồn tại. |
| Git đúng phạm vi | Commit và normal push của allowed.md giữ sửa local other-user.md; HEAD remote bằng commit mới; index rỗng sau thao tác. |
| Staging/remote | Staging người dùng có sẵn được giữ nguyên; path ngoài grant, branch/remote đổi, review hash đổi đều bị chặn. |
| Conflict | Divergence đã biết chặn trước tạo commit mới; race remote sau commit giữ local commit/journal và remote không bị force overwrite. |
| Runtime/ignored | Broad grant vẫn không cho stage ignored, runtime histories, profiles, model/binary. |
| Git history và refs | Toàn outgoing history bị kiểm phạm vi/secret, kể cả commit-message secret; push.followTags=true không gửi thêm annotated tag ngoài branch. |
| Hooks | Hook có thể stage file khác hoặc hook exit1 đều chặn trước mutation; HEAD/remote giữ nguyên, không bypass kiểm tra. |
| Owner/archive | Candidate B không thể tự khai owner A; archive source ngoài jobs grant bị chặn; archive A cần writer lease rảnh và không nhận .env/private.pem. |

## Đối chiếu tài liệu hiện hành

Ba kiểm độc lập đạt:

1. CLI `--help` có các command/option đã hướng dẫn trong workflow/maintenance/setup/session/vocabulary/Colab/dashboard; không thấy lệnh mới bị quảng cáo nhưng parser chưa có.
2. Discovery thực có đúng bốn SKILL.md: setup, production, development, maintenance. Channel profile thực là English9:16, B1/B2/C1, Alba0.92 và scene_count=null; director_context tải references vp-production cho toàn bộ stage, không còn caller tới skill active cũ.
3. Link file từ bốn điểm vào, nhóm docs active được docs/INDEX khai báo và toàn bộ skill/references đều tồn tại. Các nguồn legacy/reference/plans đã được phân loại, không nhập mode/gate cũ vào policy hiện hành. Hướng dẫn workflow ghi auto cần connected author khi thiếu draft và không machine reviewer; review đúng năm output.

Các command/profile/links hiện hành đã kiểm không có mâu thuẫn mới. Docs/runtime ban đầu chưa khớp các giới hạn cleanup/archive/Git do QA-M01–M08; đã sửa và kiểm lại. M09 phát hiện cách xử lý hooks chưa khớp câu “Hook/check thất bại dừng”; đã đổi sang hook blocker trước mutation, không bypass. Tài liệu nên nêu chính xác blocker này để người vận hành biết hook cần review riêng, không hiểu công cụ đã chạy hook. Report worker cũ 26/26 không bao phủ các reproduction độc lập này; bằng chứng hiện tại là bộ 28 test và JSON mới.

## Giới hạn còn lại của toàn kế hoạch

Không chứng minh recipe có thể tái chạy trên service thật hoặc dữ liệu ngoại vi không được journal tham chiếu. Không chứng minh GitHub/HDD thật, lịch đồng bộ hoặc đóng Colab runtime; kế hoạch không tự cho phép tạo lịch khi chưa có cadence/branch/paths. Scope/source do công cụ ghi vẫn không là xác thực transport người dùng hay OS sandbox. Không có evidence nghe/xem giọng/ảnh/video, T4/Flow/web của toàn mục tiêu trong báo cáo bảo trì này.

QA đã giữ nguyên các reproduction và chạy lại bộ độc lập sau sửa. JSON ghi output đầy đủ, hash mã trước/sau ổn định và lịch sử kết quả. Nếu runtime còn thay đổi liên quan thì chạy lại đúng phạm vi; không lấy lượt kiểm này thay nghiệm thu dịch vụ/media thật.
