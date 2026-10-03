# Kế hoạch nền tảng vận hành trước nâng cấp Video Pilot

Ngày: 03/10/2026. Bản thảo thảo luận 0.1.

**Yêu cầu hiện hành sau đính chính:** [bản thiết kế 0.3](20261003-thiet-ke-colab-va-auto-thuc-hien.md): máy chủ yếu quản lý/lưu dữ liệu quan trọng, xử lý nặng trên Colab; Auto thực hiện tự lập kế hoạch và chạy đến đầu ra, không gọi kiểm duyệt. Các phần auto review và phân chia xử lý cũ dưới đây không phải thiết kế đích mới. Runtime chưa sửa; job cũ chưa thay mode/baseline.

**Cập nhật yêu cầu sau bản 0.1:** người dùng đã chấp nhận trang quản lý trực quan tại máy, yêu cầu quản lý account Flow/Colab, nhiều lựa chọn theo phiên, tiết kiệm tài nguyên và auto review có cập nhật. Xem [thiết kế nghiệp vụ 0.2](20261003-thiet-ke-quan-ly-tai-khoan-phien-va-auto.md). Các mục bên dưới ghi “chưa chốt giao diện” là trạng thái tại lúc lập bản 0.1; quyết định mới ở dòng này có hiệu lực cho kế hoạch. Chưa triển khai runtime.

Ví dụ bổ sung theo câu hỏi tiếp theo của người dùng: [giao diện từng bước, dừng/tiếp tục và quản lý prompt](20261003-mo-phong-giao-dien-va-quan-ly-prompt.md). Đây vẫn là thiết kế để thảo luận, chưa chốt lựa chọn giao diện hay triển khai.

**Trạng thái: đề xuất để thảo luận; chưa sửa Rules/Skills/runtime, chưa cài đặt hoặc thử sản xuất.**

Yêu cầu hiện tại: ưu tiên sửa skill, Rules, quy trình, setup sau tải/clone hoặc mở chat mới, kiểm soát trực quan, tổ chức thư mục và phân quyền agent trước nâng cấp hướng video và thử nghiệm.

## 1. Quan hệ với kế hoạch trước

- [Khởi tạo dự án](20261003-ke-hoach-khoi-tao-du-an.md): chi tiết inventory, cài đặt, login và capability B0–B6.
- [Phân quyền và kiểm soát](20261003-ke-hoach-sua-phan-quyen-kiem-soat.md): chi tiết runtime, recovery, ownership và gói K0–K7.
- [Hướng video](20261003-ke-hoach-dieu-chinh-video-va-kiem-soat.md): giữ riêng để thực hiện sau nền tảng.

Tài liệu này gom phụ thuộc và bổ sung vòng đời chat, cấu trúc đích, giao diện quan sát và tiêu chí nghiệm thu. Không thay các quyết định lịch sử. Thứ tự dưới đây là đề xuất mới, chưa sửa thứ tự có hiệu lực trong INDEX: chốt thiết kế chính sách tối thiểu trước; khởi tạo vẫn là phần triển khai đầu tiên; hoàn thiện vận hành trước mở rộng sản xuất.

## 2. Phạm vi kiểm tra thực tế trong lượt này

Đã đọc INDEX, kế hoạch người dùng gửi, hai kế hoạch nền đã lưu, workflow, director-system, Rules, GEMINI, các SKILL.md vp-*, skill-creator và các phần CLI liên quan. Checkout đang đọc: nhánh `video-vocabulary` tại gốc dự án. Có thay đổi chưa commit từ trước ở AGENTS/INDEX và tài liệu; giữ nguyên.

Đây là rà soát tài liệu và mã tĩnh tại checkout này. Không xác nhận trạng thái live của job predator, các worktree khác, login, Flow/T4 hoặc capability nghe/xem. Những dữ kiện live trong báo cáo cũ chỉ là lịch sử. Không chạy status/next/run/resume của job trong lượt lập kế hoạch.

### Các lệch đã thấy tại checkout hiện tại

| Nguồn | Vấn đề | Ưu tiên xử lý |
|---|---|---|
| vp-content, vp-script-director | Ép Micro-Drama 4 hồi; director chỉ định Edge-TTS Christopher, khác giọng/provider trong quy trình | Loại yêu cầu format/provider khỏi skill dùng chung; format nào còn dùng phải thành lựa chọn riêng của hồ sơ/brief |
| vp-audio-director | Chỉ định Adam bựa và Foley bắt buộc, đồng thời ghi mixing chưa là tính năng runtime và giữ giọng Minh Quân Pro/Alba | Chỉ dẫn nghề phải bám giọng/backend thật; không hứa khả năng chưa có |
| vp-visual-director | Áp highlight màu cố định và screen shake hài trong skill dùng chung | Chuyển lựa chọn thiết kế vào hồ sơ phù hợp; chỉ dùng hiệu ứng runtime hỗ trợ |
| workflow, vp-video | Gắn 9:16 với Việt, 16:9 với Anh | Ngôn ngữ, tỷ lệ, phụ đề lấy từ hợp đồng; rà runtime trước khi cam kết hỗ trợ |
| AGENTS và pilot.py | Chính sách cho agent adopt sau xác nhận; CLI vẫn human-only/TTY và actor=user | Đồng bộ quyền và ghi rõ người duyệt/người thực thi; không dùng TTY làm bằng chứng con người |
| pilot.py | Doctor import phụ thuộc và khởi tạo Pilot trước khi báo cáo; CLI dùng khóa độc quyền | Bootstrap phải kiểm được máy chưa có deps; bảng điều khiển cần đường quan sát không ghi |
| vp-clean | Xóa rộng runs/scratch/results/video, cache toàn máy; pkill theo chuỗi chung; commit/push mặc định | Thu hẹp về tài nguyên sở hữu của dự án, xem trước danh sách, bảo toàn evidence và tách quyền xóa/đẩy Git |
| logs/issues/INDEX | Có giải pháp lịch sử như sửa journal/state hoặc chuyển profile, không phù hợp giới hạn hiện tại | Đánh dấu tính lịch sử; log là bằng chứng, không tự là chỉ dẫn vận hành hiện hành |

Mâu thuẫn được ghi ở `sys/logs/issues/ISSUE-20261003-governance-skill-conflicts.md`; chưa được sửa hay đóng lỗi.

## 3. Một nguồn cho mỗi quyết định

| Nhóm | Nguồn đích | Nội dung |
|---|---|---|
| Điểm vào | INDEX/README ngắn | Clone mới, tiếp quản chat, tiếp tục job, phát triển, bảo trì đi đâu |
| Quyền chung | AGENTS | Phạm vi hành động, ba gate, integrity, giao việc, dừng, lịch sử |
| Quy tắc chuyên biệt | .agents/rules | Nhận diện mascot và những ràng buộc dùng chung có nguồn rõ |
| Quy trình | sys/docs/workflow.md | Chuyển bước, revision, reject, recovery, nghĩa của dừng/tiếp tục |
| Cách thực hiện | .agents/skills/vp-* | Đầu vào, đầu ra, thao tác nghề, công cụ hợp lệ và điểm dừng |
| Hướng kênh | Hồ sơ kênh hiện có | Ngôn ngữ, đối tượng, phong cách, giọng, mặc định; mới áp dụng cho brief mới |
| Hợp đồng video | Brief hiện tại và content được duyệt | Lựa chọn thật cho job; thay đổi qua workflow |
| Trạng thái và quyết định | Kho trạng thái, revisions, reviews, journal hiện có | Đọc qua công cụ hợp lệ; dashboard/bàn giao không có quyền ghi thay |
| Tài liệu lịch sử | reports, plans, logs/issues | Có ngày và trạng thái; không tự trở thành quyền hoặc quy tắc |

GEMINI và điểm vào của công cụ khác trỏ cùng chính sách, tránh sao chép cả bộ. Phải kiểm cơ chế nạp của từng công cụ thật; frontmatter always_on hay file tồn tại không chứng minh phiên khác đã đọc. Không tạo lệnh/cấu hình cho nhiều công cụ trước khi có phạm vi hỗ trợ cụ thể.

Không chỉ dựa vào lời nhắc để bảo vệ thao tác dễ sai. Gate, revision/hash, ownership, dừng submit và integrity cần được runtime kiểm tương ứng. Đây là kiểm soát thao tác và truy vết; với agent có toàn quyền filesystem/shell hiện tại, chưa phải ranh giới bảo mật.

## 4. Hai luồng bắt đầu khác nhau

### 4.1 Tải/clone lần đầu

1. Nhận diện repo/branch/commit và chọn preset được hỗ trợ.
2. Kiểm máy bằng công cụ không cần import Pilot hoặc tạo DB job.
3. Lập danh sách phần có/thiếu, nơi cài, kích thước tải và phần người dùng làm.
4. Cài phụ thuộc của preset theo manifest/lock trong phạm vi setup đã yêu cầu.
5. Kiểm mascot, giọng và tài nguyên; thiếu thì báo thiếu, không đổi giọng.
6. Tạo cấu hình máy local; chọn executable/profile/project/session đúng máy.
7. Người dùng hoàn tất OAuth/login/OTP/CAPTCHA; không đưa secret vào chat hoặc report.
8. Kiểm từng capability. Cấp T4/generation/live smoke là bước riêng theo phạm vi được yêu cầu.
9. Bàn giao mức sẵn sàng và việc cần làm tiếp. Setup không tự bắt đầu video.

Git chứa mã, Rules/Skills, schemas, lock, config mẫu và asset được phép. Token/profile/DB/runs/cache/machine.local không đồng bộ mặc định. Tải ZIP cần báo provenance/version khả dụng, không giả có Git HEAD. Chuyển job từ máy cũ là thao tác riêng.

Preset khởi đầu đề xuất: Linux, review, English + Colab + Flow theo hướng đang lưu. Đây là đề xuất phạm vi; chưa cam kết đa hệ điều hành hoặc nghiệm thu backend.

### 4.2 Mở chat mới hoặc quay lại

1. Đọc INDEX và AGENTS hiện hành tại đúng checkout; xác định nhánh, commit và thay đổi chưa commit.
2. Xác định ý định lượt mới: thảo luận, setup, sản xuất, phát triển hay bảo trì.
3. Đọc bản bàn giao gần nhất để tìm job/tệp/quyết định; đối chiếu nguồn thật trước hành động.
4. Kiểm phiên bản chính sách, cấu hình máy và capability cần cho nhiệm vụ; không cài/login lại nếu chưa có lý do.
5. Khi tiếp tục sản xuất, kiểm status/next qua CLI; sau khi có observe, dùng đường quan sát trước nếu runner đang bận. Không dùng bản bàn giao để bỏ qua gate.
6. Liệt kê revision, quyết định còn hiệu lực, request đang gửi/unknown và session/account sở hữu; không resend hoặc đổi account ngầm.
7. Nạp skill và references cần cho đúng phần; không nạp mọi khuôn sáng tạo.
8. Báo ngắn: đang ở đâu, việc được phép, đầu ra kế tiếp, điều gì cần người dùng. Chỉ tiếp tục khi đúng phạm vi yêu cầu.

Nếu có nhiều job/checkouts phù hợp, hỏi chọn đối tượng trước hành động phụ thuộc. Bàn giao không tự cấp quyền mới. Những quyền đã có bằng chứng hợp lệ vẫn được giữ, không hỏi lại vô cớ.

### 4.3 Bản bàn giao cần có

- Checkout/branch/commit; policy version và thay đổi local liên quan.
- Mục tiêu hiện tại, phạm vi đã được yêu cầu và tham chiếu quyết định thật.
- Job/mode/phần/revision; link review và artifact mới nhất.
- Request/target/account/session đang dở, việc đã gửi/chưa gửi và lỗi cần đối chiếu.
- Việc tiếp theo được phép, việc phụ thuộc quyết định và người/tài nguyên sở hữu.
- Timestamp và giới hạn kiểm chứng.

Đề xuất lưu bàn giao có cấu trúc trong `sys/.state/sessions/` và sinh bản tóm tắt dễ đọc. Khi triển khai mới chốt schema. Nó là bản dẫn đường có thể lỗi thời; không có trường tự set approved hoặc quyền override workflow.

## 5. Phân quyền theo hành động và tài nguyên

| Vai trò | Được làm trong nhiệm vụ được cấp | Đầu ra | Giới hạn |
|---|---|---|---|
| Điều phối chat | Chọn đúng ngữ cảnh, viết/kiểm trực tiếp, gọi CLI hợp lệ, gửi artifact và tổng hợp | Kế hoạch/phiếu điều hành/bàn giao | Không tự duyệt review hoặc mở rộng ngoại lệ |
| Khởi tạo | Kiểm/cài/cấu hình local đúng preset | Setup report/capability/missing list | Không sinh nội dung, mua compute hay đổi hợp đồng |
| Nội dung | Outline/narration/images/beats theo brief | Draft rồi revision qua workflow | Chốt lời trước neo; không sửa lịch sử |
| Hình và âm | Làm/thu/sửa target theo content hợp lệ | WAV/ảnh/prompt/ref/session metadata | Không sửa narration hoặc retry unknown |
| Biên tập và kiểm tra | Timeline/cue, kiểm thực tế theo khả năng | Findings/evidence/unsupported | Không tự ghi quyết định chất lượng thay nguồn hợp lệ |
| Worker | Thực hiện target cụ thể trên session đã giao | Request ID/trạng thái/artifact/lỗi | Không tự đổi profile/model/brief hoặc quyết định job |
| Phát triển | Sửa phạm vi hệ thống được yêu cầu | Diff/ảnh hưởng/validation/rollback | Không đổi code để vượt gate; nhận code theo xác nhận đúng job |
| Bảo trì | Kiểm kê/dọn phạm vi được yêu cầu | Danh sách trước/sau, bằng chứng sao lưu | Không xóa journal/review, kill browser khác hoặc push Git mặc định |

Vai trò không đồng nghĩa với thêm agent. Một agent có thể đảm nhiệm nhiều vai trò theo nhiệm vụ; tạo subagent chỉ khi có quyền phù hợp. Lượt này không tạo subagent.

Khi có giao việc: ghi job/revision/target, snapshot đầu vào, tệp được ghi, session sở hữu, đầu ra, retry cap, điểm dừng và nơi bàn giao. Mỗi target/tệp chỉ có một người ghi tại một thời điểm. Worker gửi kết quả; đầu mối duy nhất điều khiển workflow qua công cụ. Gate quyết định vẫn theo review/auto, không thuộc quyền worker.

## 6. Quy tắc thiết kế lại skill

Mỗi skill giữ: khi dùng, dữ liệu đầu vào, việc được làm, đầu ra, cách bàn giao và điều kiện dừng. References chứa chi tiết chỉ cần cho trường hợp tương ứng. Skill trỏ tới chính sách thay vì sao chép quyền và ngoại lệ nhiều lần.

- Giữ vp-vocab/content/media/video/clean và bốn skill đạo diễn vì trách nhiệm đã rõ; sửa nội dung trước khi thêm tên mới.
- Đề xuất thêm `vp-bootstrap` cho setup và tiếp quản; chia hướng dẫn clone/return vào references nếu cần. Không thêm skill điều phối chỉ để lặp AGENTS.
- Format hài, màu highlight, số nhịp, thời lượng và giọng cụ thể chỉ tồn tại như lựa chọn của kênh/brief tương ứng, không là chuẩn mọi video.
- Thông tin backend phải khớp capability thật. Nội suy không thành alignment; prompt không chứng minh cảm xúc; kế hoạch âm thanh không chứng minh renderer có SFX.
- vp-clean ưu tiên sửa sớm: bỏ thao tác mặc định vượt phạm vi và tách kiểm kê, cache dự án, đóng phiên sở hữu, archive, xóa có danh sách cụ thể.
- Validate cấu trúc skill và kiểm hành vi theo tình huống sau khi có yêu cầu triển khai. Không coi validator frontmatter là nghiệm thu quy trình.

## 7. Cấu trúc đích: giữ sys/video, tổ chức bên trong từng bước

```text
pipelineFlow/
  INDEX.md, README.md, AGENTS.md, GEMINI.md, pilot.py
  .agents/
    rules/                 Chính sách chuyên biệt
    skills/                Hướng dẫn theo trách nhiệm
  sys/
    docs/
      getting-started.md    Đề xuất: setup và dẫn đường
      session-start.md      Đề xuất: tiếp quản chat
      workflow.md           Quy trình hiện hành
      plans/                Kế hoạch có trạng thái
    config/                 Đề xuất: mẫu máy, presets, manifests
    dashboard/              Đề xuất: giao diện tại máy
    scripts/, schemas/, renderer/, tests/
    assets/, vocab/, research/
    runs/, exports/         Giữ dữ liệu hiện tại
    .state/                 DB, control/setup/session local
    .gflow/                 Profile local
    logs/issues/            Bằng chứng và giải pháp sự cố
    reports/, experiments/, scratch/
  video/<job>/              Thành phẩm đã đủ quyết định
```

Những nơi ghi “đề xuất” chưa được tạo. Không di chuyển module đang chạy trong gói đầu. Trước mỗi chuyển tệp cần inventory caller/path, kế hoạch old→new, kiểm clone và rollback. Config hiện có chỉ di chuyển khi loader/integrity đã được xử lý; không tạo song song hai cấu hình hiệu lực. experiments/b2 vẫn là phụ thuộc đang dùng, không xóa vì tên experiments.

## 8. Kiểm soát trực quan

Đề xuất bản đầu là trang local xem trạng thái và mở artifact; câu hỏi lựa chọn giao diện đã gửi người dùng, chưa ghi lựa chọn này là được chốt. Chưa xây website hoặc dùng dịch vụ hosting.

### Nội dung cần thấy

1. **Thiết lập máy:** có/thiếu/đã cấu hình/đã kiểm/không hỗ trợ/chưa thử cho content, images, audio, render và auto review; timestamp và lý do.
2. **Công việc:** job, mode, revision và đúng ba cột content → media → video; “chờ duyệt” khác “đang chạy”.
3. **Sản phẩm:** nghe WAV, xem toàn bộ ảnh và MP4, mở SRT/review; nhãn revision và số đo thật.
4. **Việc đang gửi:** target, session, request ID, đã gửi/đã có/chưa thu/unknown; không biến ước lượng thành phần trăm chắc chắn.
5. **Cần người dùng:** đăng nhập, duyệt revision cụ thể, đối chiếu unknown, lựa chọn diff; link bằng chứng và hành động phù hợp.
6. **Lịch sử:** quyết định, thay đổi, lỗi và giải pháp; không hiển thị token/cookie/OAuth code.

Trạng thái sản phẩm, trạng thái vận hành và readiness của máy là ba nhóm riêng. Snapshot có timestamp; mất kết nối hiển thị cũ/mất kết nối, không giả đang cập nhật. Không gộp thành một đèn xanh “hệ thống ổn”.

### Thao tác bổ sung sau khi nền runtime đủ

- Duyệt/từ chối gắn chính xác phần, revision, hash và phản hồi thật; artifact thay đổi phải chặn quyết định cũ.
- Dừng nghĩa là chặn gửi mới và theo dõi phần đã gửi; không hứa hủy provider hoặc tự đóng browser còn evidence.
- Tiếp tục kiểm lại quyền, gate, integrity, cap và unknown; không chỉ bật cờ “running”.
- Thu kết quả cũ khác tạo lại. Unknown chỉ hiện đường đối chiếu; không có nút gửi lại mù.
- API thao tác gọi cùng application/CLI chính thức, không ghi trực tiếp SQLite/reviews/journal. Giao diện xem không khởi tạo Pilot có side effect để poll.

Các bước setup không thêm gate sản xuất. Review vẫn duyệt content/media/video; auto vẫn cần máy xem/nghe thật.

## 9. Thứ tự ưu tiên đề xuất

| Gói | Phạm vi | Kết quả xem được | Điều kiện chuyển tiếp |
|---|---|---|---|
| N0 – chốt nền thiết kế | Một nguồn quy tắc, vai trò/quyền, checkout chuẩn, thư mục đích, UX đầu tiên | Ma trận quyền, map nguồn, inventory mâu thuẫn và danh sách tệp sửa | Phạm vi rõ; không coi kế hoạch là quyền sản xuất |
| N1 – điểm vào và chỉ dẫn | INDEX/AGENTS/Rules/workflow/skill sửa phần xung đột; hướng dẫn clone và chat mới | Diff tài liệu/skill, luồng bắt đầu, checklist bàn giao | Tài liệu khớp khả năng hiện tại; lệnh chưa có ghi là đề xuất |
| N2 – khởi tạo thực thi | Gói B0–B5: bootstrap stdlib, local config, assets/login, readiness | Plan/check/report chạy được ở máy sạch | Không phụ thuộc home/profile/cache máy cũ; setup chạy lại được |
| N3 – kiểm soát runtime | Gói K1–K5: đúng quyền nhận diff, observe, dừng, recovery, ownership, artifact event | Snapshot/control và dấu vết thao tác | Unknown không bị resend; không vượt cap/gate; không giả actor |
| N4 – giao diện quan sát | Setup/job/artifacts/requests/issues từ nguồn thật | Trang local dùng để theo dõi và mở sản phẩm | Poll không ghi job, đọc được khi runner bận, hiển thị độ mới |
| N5 – điều khiển và nghiệm thu nền | Nút hợp lệ + kiểm clone/chat mới/ngắt quãng/stop/recovery | Báo cáo tình huống và demo giới hạn rõ | Đạt invariants; thử thật chỉ trong phạm vi đã được yêu cầu |
| N6 – nâng cấp hướng video | Áp kế hoạch hình/kể/job sau nền | Brief/content/media/video theo workflow | Có yêu cầu sản xuất riêng và quyết định đúng mode |

N0 là thảo luận trước triển khai. N1 tài liệu và N2 setup triển khai trước các mở rộng vận hành; N1 mô tả capability đang có, cập nhật tiếp sau N3. Có thể thiết kế giao diện cùng N0 nhưng nối dữ liệu sau N3. Chưa mở rộng số worker/profile trong gói nền.

## 10. Nghiệm thu khi được yêu cầu triển khai

- Clone sạch hoặc gói ZIP thiếu deps vẫn đọc được plan; không dùng tài nguyên máy cũ để giả đạt.
- Setup lần hai không cài/login lại vô cớ, không ghi đè cấu hình hay tạo job.
- Chat mới nắm đúng checkout/job/revision/quyền và không resend request dở.
- Đổi yêu cầu mới vào brief đúng workflow; skill không kéo lại format/giọng/tỷ lệ cũ.
- Runner đang bận vẫn quan sát được; mở dashboard không đổi trạng thái job.
- Sau khi đã tiếp nhận lệnh dừng, submit mới bằng 0; inflight và evidence giữ đầy đủ.
- Hai worker cùng target chỉ một owner/submit; session/account thu khớp request cũ.
- Duyệt revision cũ hoặc artifact đã thay bị chặn; content/media chưa duyệt không vượt phần phụ thuộc.
- Không nghe/xem được phải unsupported; metadata/tests không thay nghiệm thu thật.
- Dọn dẹp không chạm evidence/session/tệp ngoài phạm vi; archive kiểm bản sao trước xóa theo quyền.
- Diff nhận cho job phải đúng tập tệp/hash được xác nhận; người duyệt và thực thi ghi riêng.
- Live smoke có budget lượt/target/session và điểm dừng; quota/503/CAPTCHA/cap vẫn là chặn cứng.

## 11. Việc cần chốt trong thảo luận

1. Giao diện đầu: local xem trước rồi thêm nút, local có nút ngay, hoặc Markdown/chat trước.
2. Phạm vi đầu: Linux hiện tại; các công cụ agent nào cần adapter điểm vào thật.
3. Cách giao việc: một điều phối đảm nhiệm nhiều vai trò mặc định; khi nào cho phép thêm agent/worker.
4. Checkout/release chuẩn: lập inventory khác biệt trước chọn, giữ các thay đổi local và dữ liệu job riêng.

Không hỏi lại quyền adopt đã thể hiện trong AGENTS người dùng cung cấp: sau xác nhận đúng job/diff, agent được nhận phần đã duyệt. Việc cần phát triển là đồng bộ CLI và provenance với quyền đó; lượt này không adopt hoặc sửa baseline. Những lựa chọn ở trên chưa được coi là đã chốt.

## 12. Tiến độ và bước thảo luận kế tiếp

Đã hoàn tất: đối chiếu nguồn hiện tại, ghi mâu thuẫn, lập kế hoạch chung và phân định thiết kế/triển khai/nghiệm thu/sản xuất.

Chưa làm: sửa Rules/Skills/code/config, di chuyển thư mục, setup/login, tests, generation/render, adopt, tạo agent phụ hoặc thay trạng thái job.

Bước kế tiếp đề xuất: thảo luận N0 bằng ba tài liệu cụ thể — bản đồ nguồn chỉ dẫn, ma trận quyền và sơ đồ màn hình/cấu trúc đích — rồi mới triển khai N1–N2 theo yêu cầu.
