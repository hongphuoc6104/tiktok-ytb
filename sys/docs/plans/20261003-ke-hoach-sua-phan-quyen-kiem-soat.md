# Kế hoạch sửa phân quyền và kiểm soát vận hành

Ngày phân tích: 03/10/2026. Phiên bản: 1.0.

**Thứ tự mới theo yêu cầu người dùng:** làm [phần khởi tạo dự án](20261003-ke-hoach-khoi-tao-du-an.md) trước. Các gói K0-K7 bên dưới vẫn là kế hoạch chưa triển khai.

**Trạng thái: đã phân tích và lập kế hoạch sửa; chưa sửa Rules, Skills, cấu hình hoặc mã vận hành.** Đây là kế hoạch riêng về quyền và kiểm soát. Kế hoạch điều chỉnh hướng video được lưu riêng; lượt này không tiếp tục sản xuất video.

## 1. Kết luận phân tích

Hệ thống đã có ba gate theo revision, hash artifact, chế độ job cố định, integrity baseline, khóa ghi nhật ký request và giới hạn sửa tự động. Cần giữ các cơ chế này. Phần yếu là chính sách phân tán, hướng dẫn khác nhau giữa checkout, quyền sửa job chưa khớp CLI, điều hành khi runner đang bận, khôi phục request thất bại và bàn giao song song.

Chỉ sửa văn bản hướng dẫn sẽ không xử lý hết các lỗi vận hành. Kế hoạch chia thành chuẩn hóa chính sách và phát triển các kiểm tra runtime tương ứng. Không dùng thay đổi chính sách để reset request, bỏ gate hoặc hợp thức hóa quyết định lịch sử.

## 2. Phạm vi bằng chứng

Đã đọc và đối chiếu checkout chính và worktree sản xuất. Các phát hiện mã bên dưới lấy từ worktree `english-9x16-agent-content`, không khẳng định hai checkout đang chạy cùng một phiên bản. Đây là phân tích tĩnh; chưa chạy tests, smoke generation hoặc sửa baseline.

| ID | Bằng chứng đã đọc | Phát hiện | Hệ quả |
|---|---|---|---|
| G01 | AGENTS.md hai checkout; hướng dẫn người dùng trong phiên; sys/pilot.py:71-100, 419-423 | Tài liệu trên đĩa cho phép agents adopt-code sau duyệt; hướng dẫn người dùng trong phiên và CLI còn ghi human-only. CLI kiểm TTY, lịch sử adopt ghi actor=user | Quyền được mô tả không thống nhất; lịch sử chưa tách người duyệt và người thực thi |
| G02 | Diff vp-script-director, vp-vocab và docs/director-system giữa hai checkout | Checkout chính còn khuôn hài 4 hồi/cách sinh nội dung cũ; worktree đã bỏ khuôn 4 hồi và hướng đến người đang chat viết trực tiếp | Người quay lại có thể nạp hướng dẫn khác nhau. Đính chính rà soát trước: khuôn hài nằm ở checkout chính, không còn ở vp-script-director của worktree đã kiểm |
| G03 | sys/workflow.py:48-110, 386-416 | Gate công khai đối chiếu snapshot, revision, hash và event; kỹ thuật có actor riêng | Cơ chế này đúng chức năng, cần bảo toàn; quyền vận hành không được biến thành quyền duyệt |
| G04 | sys/pilot.py:383-388, 404; sys/workflow.py:status | Mọi lệnh CLI đi qua process.lock độc quyền; khóa đang bận trả lỗi ngay, kể cả lệnh đọc. Status có refresh logic | Thiếu đường quan sát độc lập khi chạy lâu; cần giao diện đọc thực sự không ghi |
| G05 | Danh sách lệnh pilot.py; sys/experiments/b2_illustrator/session.mjs:61-106 | Chưa có lệnh dừng gửi mới ở mức job. Lệnh stop session nằm sau queue và đóng tab/browser | Dừng session không thay cho dừng lịch phát việc an toàn; có thể chờ việc dài hoặc mất UI của request đang dở |
| G06 | attempt-store.mjs:297-310; image_pipeline.py:948-999 | Unknown chỉ chuyển generated khi có evidence; flow-reconcile đòi asset tải về. Chưa có trạng thái thất bại cuối cùng được xác nhận không có asset | Một request thật sự thất bại vẫn có thể giữ job bị chặn. UI UNKNOWN/lỗi dịch vụ hiện tại chưa đủ để xác nhận thất bại |
| G07 | attempt-store.mjs:113-158; image_pipeline.py:291-332 | Đã có khóa ghi độc quyền từng attempt; target còn unresolved chặn prompt mới | Cần mở rộng liên kết attempt/session/target, không thay hoặc bỏ khóa đã có |
| G08 | image_pipeline.py:413-495; b2_bridge.py:38-52; adapters.py single-image route | Batch chia theo session cấu hình; đường ảnh đơn mặc định lấy session đầu nếu không chỉ định | Cần session sở hữu cố định, đặc biệt khi thu lại request và với asset/reference chỉ thuộc một project |
| G09 | acceptance.json; config.json:11-14; b2_bridge.py:250 | production_ready=false, max_production_concurrency=1; trial bật; kiểm chất lượng/khôi phục còn fail hoặc pending | Hai profile x bốn worker là ngoại lệ thử, chưa phải mức sản xuất đạt nghiệm thu |
| G10 | AGENTS.md mục gửi kết quả; workflow.prepare_parallel_media | Quy tắc gửi output sớm có trong văn bản; hai nhánh media được join trước review | Chưa có hợp đồng bàn giao thống nhất từ worker tới người điều phối để bảo đảm output được đưa vào chat khi vừa có |
| G11 | vp-content/vp-script-director; rules production/brand; vp-video | Nội dung viết trực tiếp, quyền giao việc và quyền đổi dữ liệu chưa được tóm tắt nhất quán. vp-video còn gắn 9:16 với tiếng Việt | Quy tắc kỹ thuật cần độc lập với format kênh; các skill không được tự đổi hợp đồng |

Giới hạn: CLI hiện tự mô tả là bộ điều phối có gate, không phải security sandbox. TTY hoặc file approval do agents có quyền ghi không xác thực được người thật. Kế hoạch dưới đây giảm sai thao tác và tăng truy vết; không được tuyên bố là ranh giới bảo mật trước agents có toàn quyền filesystem/shell.

## 3. Chính sách quyền đề xuất

### 3.1 Đầu mối và vai trò

Người đang xử lý cuộc trò chuyện là đầu mối thực thi. Vai trò có tên chức năng, không gắn với tên một hệ thống hoặc agent cố định. Người dùng quyết định mục tiêu và chất lượng trong review. Máy quyết định chất lượng trong auto qua bộ review thật. Worker chỉ thực hiện việc được giao.

| Hành động | Người điều phối được tự làm trong phạm vi đã được yêu cầu | Cần quyết định bổ sung | Tuyệt đối không tự làm |
|---|---|---|---|
| Đọc/kiểm | Đọc trạng thái, nguồn, artifact, diff; lập báo cáo | Không cần hỏi lại việc đọc liên quan | Ghi đã nghe/xem khi chỉ đọc metadata |
| Nội dung | Viết draft trực tiếp, sửa theo phản hồi, check-draft và nộp revision | Đổi mục tiêu/từ/nghĩa/format ngoài phạm vi đã duyệt | Ghi đè revision/anchor đã chốt hoặc dùng dịch vụ viết thay |
| Media | Tạo/thu đúng content revision được duyệt; sửa mục được reject | Đổi giọng, provider, model hoặc yêu cầu sản phẩm ngoài quyền hiện hành | Retry unknown, che dấu watermark rồi gọi ảnh gốc sạch |
| Vận hành | Tiếp tục bước đã được phép; thu output cũ; dừng gửi mới theo yêu cầu | Cần quyền mới khi mở rộng phạm vi/ngoại lệ | Đổi mode, đổi job để né lỗi hoặc xoay tài khoản vượt hạn mức |
| Giao việc | Giao phần chuẩn bị, kiểm tra, worker hoặc phát triển khi có phép song song | Giao thêm phạm vi chưa được cho phép | Hai agents cùng ghi một tệp/target hoặc cùng quyết định trạng thái job |
| Sửa hệ thống | Phân tích và chuẩn bị diff trong phạm vi phát triển đã được yêu cầu | Duyệt diff và tiếp nhận đúng thay đổi cho job đang khóa | Sửa code/rules/config chỉ để qua gate; nhận thêm tệp ngoài diff đã duyệt |
| Duyệt/hoàn tất | Ghi quyết định thật qua CLI và trả file thật | Đúng phần/revision hoặc report auto hợp lệ | Tự suy ra approval từ “tiếp tục”, giả actor, giả bằng chứng |

Không hỏi lại phần đã được cấp quyền; cũng không mở rộng quyền từ một câu đồng ý chung. Bản kế hoạch không tự cấp quyền triển khai.

### 3.2 Quyền sửa job đã khóa

Đề xuất giữ ý định người dùng trước đây: sau khi người dùng duyệt đúng diff, người điều phối được thực hiện việc tiếp nhận code trong chính job đó. Để làm đúng, cần sửa chính sách và CLI đồng thời, thay vì dùng TTY để làm như người dùng đã tự chạy.

Điều kiện đề xuất cho bước nhận code:

- Job cụ thể, danh sách tệp, hash nội dung từng tệp và hash diff đã trình.
- Nguyên văn xác nhận thật và tham chiếu tới xác nhận; ghi rõ người duyệt là người dùng, người thực thi là agents nếu thực thi thay.
- Tập khác biệt tại thời điểm nhận phải trùng tập/hash được duyệt; có thay đổi phát sinh thì chặn đúng phần mới.
- Ghi baseline cũ, baseline mới, reason và policy version; không sửa integrity bằng tay.
- Quyền nhận code không bao gồm lift-cap, supersede nghĩa từ, tắt gate, tự đổi mode hoặc đổi nguồn tạo.

Trong khi chưa triển khai chính sách mới, giữ quyền hiện hành chặt hơn cho thao tác đang mâu thuẫn. Không chạy adopt-code ở lượt lập kế hoạch này. Nguồn xác nhận cần trung thực: runtime chỉ ghi dấu vết xác nhận được cung cấp; nếu chưa có transport xác thực người dùng, phải ghi rõ giới hạn đó.

### 3.3 Hợp đồng giao việc

Mỗi việc giao có: job/checkout, phần/revision, target IDs, session sở hữu nếu có, tệp được ghi, đầu vào bất biến, đầu ra, giới hạn thử, điểm dừng và người nhận kết quả. Worker không được đổi brief, narration, model/profile hoặc tự phê duyệt. Người điều phối viết kịch bản trực tiếp; agent khác có thể phản biện hoặc chuẩn bị tư liệu nếu có phép.

Khóa hiện có của attempt giữ nguyên. Bổ sung quyền sở hữu target và session chỉ khi runtime kiểm được trước submit. Giao việc trong chat không thay việc cấp quyền cho CLI.

## 4. Cơ chế kiểm soát chạy đề xuất

### 4.1 Tách quyết định sản phẩm khỏi trạng thái chạy

Giữ nguyên review/auto và ba gate. Thêm trạng thái điều hành riêng, không sửa workflow mode: đang chạy, đã yêu cầu dừng gửi mới, đang thu việc đã gửi, đã dừng, cần can thiệp.

Hành vi khi người dùng yêu cầu dừng:

1. Chặn gửi mới ngay tại scheduler và trước thao tác UI submit tiếp theo.
2. Ghi danh sách đã gửi, chưa gửi, kết quả đã có và lỗi chưa rõ.
3. Thu request đã gửi nếu có thể và đúng yêu cầu; không tự generation lại.
4. Đóng session chỉ sau khi không cần UI đối chiếu hoặc người dùng yêu cầu rõ; không hứa có thể hủy công việc provider nếu công cụ không hỗ trợ.
5. Worker tiếp nhận lệnh dừng dù runner đang bận; không xếp sau batch dài như stop session hiện tại.

### 4.2 Quan sát khi runner đang bận

Đề xuất đường đọc trạng thái không đi qua khóa ghi và không refresh/write DB. Trả snapshot nhất quán: job, revision, runner/worker, mục đã gửi/đã thu/chưa gửi, request unknown, output gần nhất, thời điểm cập nhật và lỗi. Nếu snapshot đang thay đổi, trả dấu chưa ổn định; không mở khóa ghi để đọc thuận tiện.

Tên lệnh/API sẽ chốt khi triển khai; có thể mở rộng status bằng chế độ observe chỉ đọc. Không thay toàn bộ chiến lược khóa hoặc cho nhiều writer cập nhật workflow cùng lúc.

### 4.3 Khôi phục request

Giữ khác biệt ba tình huống: chưa gửi; đã tạo nhưng chưa thu; đã gửi chưa rõ kết quả. Bổ sung trạng thái cuối `failed_confirmed` chỉ khi có bằng chứng gắn chính xác request và xác nhận thất bại cuối cùng, không có asset kết quả.

| Trạng thái | Được phép |
|---|---|
| not_submitted với generation_submitted=false | Chuẩn bị/sửa lỗi trước gửi và gửi trong quyền hiện hành |
| submitted/submitting | Chờ/đối chiếu request đó, không tạo request thay |
| unknown/ambiguous | Đối chiếu. UNKNOWN, thông báo lỗi chung hoặc không thấy tile chưa đủ để coi thất bại |
| generated | Thu đúng media ID đã có, không generation |
| collected/downloaded | Kiểm/tiếp tục bằng asset đúng hash |
| failed_confirmed | Giữ attempt cũ; một attempt mới phải liên kết attempt thất bại, đúng quyền retry và giới hạn |

Đường failed_confirmed cần evidence về request ID, session/project, prompt/reference identity, trạng thái cuối từ nguồn thật, observer và timestamp. Nếu nguồn không xác nhận được thất bại cuối cùng, giữ unknown. CAPTCHA/quota/503 vẫn dừng; xác nhận thất bại không tạo quyền vượt hạn mức.

Nhật ký Python và Node phải có ánh xạ trạng thái thống nhất. Không chuyển failed_confirmed về not_submitted, không reset hash để né `_unresolved_conflict`, không sửa journal trực tiếp. Các attempt cũ chỉ được bổ sung event đối chiếu qua công cụ chính thức sau triển khai.

### 4.4 Profile, worker và phạm vi thử

Session sở hữu được ghi khi chuẩn bị và dùng lại khi thu. Không lấy session đầu danh sách làm lựa chọn ngầm cho request cũ. Character/Base media phải khả dụng trong project tương ứng trước gửi; media ID ở project khác không được coi là đã có reference tại session mới.

Concurrency hiệu lực là giao của giới hạn hệ thống, giới hạn phiên, số việc độc lập và ngoại lệ người dùng đã cấp. Ngoại lệ thử hai profile x bốn worker cần job, session IDs, số worker, phạm vi mục, hạn kết thúc thử và điều kiện dừng. Không đổi production_ready chỉ vì thử chạy được. Khi có lỗi chung của provider dừng các submit mới trong phạm vi liên quan; lỗi riêng một target không làm mất output khác.

### 4.5 Gửi kết quả theo sự kiện

Runner/worker phát sự kiện artifact_ready với đường dẫn, job/part/revision/target, hash và số đo kỹ thuật khi artifact đã ghi hoàn chỉnh. Người điều phối gửi preview/link trong chat ngay khi nhận, rồi tiếp tục phần độc lập. Trạng thái generated chưa tải về không phải artifact sẵn sàng.

Không coi stdout/manifest là bằng chứng người dùng đã thấy. Dấu đã gửi chỉ ghi sau khi bước hiển thị thật xảy ra. Quyền gửi artifact không phải quyền duyệt; vẫn dừng ở ba gate. Giới hạn công cụ nghe/xem được ghi unsupported.

## 5. Kế hoạch chỉnh Rules và Skills

### 5.1 Một nguồn cho mỗi loại chính sách

| Tệp/nhóm | Sửa dự kiến | Tiêu chí đạt |
|---|---|---|
| AGENTS.md | Quyền đọc/sản xuất/phát triển/duyệt; quyền nhận diff; thứ tự ưu tiên; hợp đồng giao việc; dừng và gửi output | Không còn mệnh lệnh trái CLI hoặc các ngoại lệ không rõ phạm vi |
| .agents/rules/production.md | Rút gọn quy tắc vận hành bắt buộc, trỏ nguồn chính | Không lặp khuôn sư phạm hoặc giọng/tỷ lệ cố định |
| .agents/rules/brand_tolerance.md | Giữ nhận diện và dung sai; làm rõ dung sai nét phụ không cho phép sai nghĩa/hành động | Người kiểm không chấp nhận ảnh sai hành động vì mascot đúng |
| sys/docs/workflow.md | Ngữ nghĩa duyệt/tiếp tục/dừng; revision; observe; recovery | Đủ ba gate, ví dụ đúng, không ép ngôn ngữ theo tỷ lệ |
| sys/docs/director-system.md và director-contract | Phạm vi trách nhiệm; nguồn dữ liệu duy nhất; quan hệ với workflow | Vai trò đạo diễn không tự cấp quyền hoặc gọi dịch vụ viết |
| vp-vocab/vp-content/vp-script-director | Người đang chat viết; cách phản biện/giao việc; brief là hợp đồng; quy trình freeze/neo | Cùng hướng dẫn ở checkout được chọn, không gọi lớp Pilot để vượt gate |
| vp-media/vp-audio-director/vp-visual-director/vp-edit-director | Sản xuất theo snapshot; phạm vi audio/ảnh độc lập; evidence và repair | Không đổi hợp đồng, tự retry unknown hoặc giả đã xem/nghe |
| vp-video | Tỷ lệ và ngôn ngữ theo brief; export sau quyết định hợp lệ | Short tiếng Anh 9:16 không bị hướng dẫn cũ đổi sang tiếng Việt |
| vp-clean | Tách quyền bảo trì khỏi sản xuất | Không tự xóa journal/evidence hoặc coi dọn sạch là hoàn tất |
| INDEX.md | Entry point, kế hoạch riêng và checkout đang dùng | Quay lại dự án tìm được đúng chính sách/plan, không tự merge checkout |

Hướng sáng tạo riêng của kênh nằm trong hồ sơ/brief và kế hoạch điều chỉnh hướng. Bộ Rules/Skills dùng chung không đóng cứng nét hình, số nhịp, số tranh, khoảng nghỉ hoặc giọng hài. Mọi thay đổi các tệp bảo vệ đều phải theo phạm vi phát triển và integrity của job đang dở.

### 5.2 Khung chỉ dẫn cần đưa vào sau khi được phép sửa

Các câu dưới đây là bản nháp chính sách, chưa có hiệu lực:

- Người đang xử lý cuộc trò chuyện thực thi và tổng hợp trong phạm vi người dùng đã yêu cầu; vai trò được gọi theo chức năng.
- Quyền chuẩn bị, chạy, sửa và duyệt là bốn quyền riêng; không suy từ quyền này ra quyền khác.
- Xác nhận cho diff cụ thể tiếp tục có hiệu lực với đúng diff/job; thay đổi ngoài phạm vi cần được trình riêng.
- Mọi request đã gửi còn chưa rõ kết quả phải được đối chiếu; chỉ evidence hợp lệ mới chuyển trạng thái.
- Yêu cầu dừng chặn submit mới và giữ lịch sử; kết quả đã có không bị xóa.
- Mỗi artifact thật được bàn giao ngay, cùng revision và giới hạn kiểm tra. Review mode vẫn chờ đúng quyết định từng phần.
- Mọi ngoại lệ worker/profile phải có phạm vi và giới hạn; tốc độ không mở rộng quyền.

## 6. Các gói sửa và thứ tự triển khai

| Gói | Ưu tiên/phụ thuộc | Tệp dự kiến | Công việc cụ thể | Điều kiện hoàn tất |
|---|---|---|---|---|
| K0 - chốt chính sách và checkout | Trước mọi sửa runtime | AGENTS, INDEX, docs và rules liên quan | Chọn checkout chuẩn cho phát triển; lập diff giữa hai bản; thống nhất quyền adopt và giao việc; không merge dữ liệu job | Một chính sách rõ, phạm vi tệp được phép và mâu thuẫn đã có quyết định |
| K1 - quyền nhận thay đổi | Sau K0 | sys/pilot.py; schema/hợp đồng xác nhận nếu cần; docs workflow | expected file/diff hashes; approved_by/executed_by; lưu evidence và baseline history; bỏ diễn giải TTY=người dùng cho quyền thực thi thay | Nhận đúng diff đã xác nhận; chặn diff thay đổi; không mở cap/gate |
| K2 - quan sát và dừng | Sau K0, có thể chuẩn bị độc lập K1 | sys/pilot.py, workflow.py, session.mjs, queue-runner.mjs; schema nếu cần | Observe chỉ đọc; control state riêng; stop-dispatch ngoài queue dài; drain kết quả đã gửi | Có thể xem tiến độ và ngăn submit mới khi runner bận, không mất journal |
| K3 - recovery thất bại có bằng chứng | Sau K0; cần K2 để thử dừng an toàn | image_pipeline.py, b2_bridge.py, attempt-store.mjs, controller.mjs, queue-runner.mjs, adapters.py | Schema evidence; failed_confirmed; ánh xạ Python/Node; linked attempt retry; đối chiếu nguồn thật | UNKNOWN chưa đủ vẫn bị chặn; asset có sẵn chỉ thu; confirmed failure giữ lịch sử |
| K4 - ownership và worker | Sau K2/K3 | image_pipeline.py, adapters.py, b2_bridge.py, session.mjs, controller.mjs | Ghi session sở hữu; kiểm project/reference; một writer/target; ngoại lệ thử scoped và ngừng phát việc | Không chọn lại session ngầm hoặc gửi một target hai lần |
| K5 - bàn giao output | Sau K2, tích hợp K4 | workflow.py, adapters.py, queue-runner.mjs; docs/skills | Event artifact_ready sau atomic write; revision/hash; người điều phối đưa output vào chat | WAV/ảnh sẵn được gửi khi phần độc lập còn chạy; không giả approval |
| K6 - thống nhất Skills | Sau K0, hoàn thiện khi K1-K5 đã chốt interface | Các vp-* liên quan, Rules, director/workflow docs | Loại hướng dẫn trái interface; chỉ dẫn đúng capability; sync có chọn lọc hai checkout | Không còn hướng dẫn cũ kéo sai quyền/tỷ lệ/luồng |
| K7 - kiểm chứng và bàn giao | Sau từng gói và đợt cuối, khi được yêu cầu kiểm thử | tests tương ứng và báo cáo kiểm | Kiểm logic, diễn tập không generation, rồi smoke thật hữu hạn nếu được phép | Có evidence; acceptance giữ false đến khi đủ tiêu chí thật |

Tên tệp mới và schema chỉ là ứng viên; khi triển khai phải đọc cấu trúc hiện tại để tránh tạo nguồn trạng thái trùng. Không mở rộng lần sửa sang renderer/nội dung nếu không cần cho cơ chế kiểm soát. Không sửa prompt_templates.py.

## 7. Tiêu chí nghiệm thu đề xuất

| Tình huống kiểm tra sau này | Kết quả yêu cầu |
|---|---|
| Có quyền chạy, chưa có content approval | Media vẫn bị chặn |
| Người dùng duyệt diff X, tệp đổi thêm sau đó | Nhận baseline bị chặn; trả phần lệch mới |
| Agents thực thi sau xác nhận thật | Lịch sử ghi user là người duyệt, agent là người thực thi |
| Status trong lúc runner giữ khóa | Đọc snapshot, không ghi/refresh hoặc mở khóa writer |
| Yêu cầu dừng giữa đợt | Submit sau điểm dừng bằng 0; inflight được liệt kê và giữ |
| Unknown kèm lỗi chung hoặc mất tile | Không retry, không đổi thành failed_confirmed |
| Có media ID nhưng download lỗi | Thu lại cùng media, generation tăng thêm bằng 0 |
| Thất bại cuối được xác nhận đúng request | Attempt cũ giữ nguyên; retry có liên kết và nằm trong quyền/giới hạn |
| Hai worker nhận cùng target | Chỉ một submit; worker còn lại nhận xung đột ownership |
| Session mất hoặc reference chỉ ở project khác | Chặn; không chọn session khác ngầm |
| Quota/503/CAPTCHA/hết cap | Dừng; không xoay account/job hoặc tự lift-cap |
| WAV xong, ảnh còn chạy | Có event và artifact thật được đưa vào chat; media approval chưa tự tạo |
| Artifact đổi sau review | Gate không dùng quyết định cũ |
| Không nghe/xem được | Ghi unsupported, không pass bằng metadata |
| Thay format/giọng trong skill | Không âm thầm thay brief hiện tại |

Chỉ chạy tests khi người dùng yêu cầu kiểm thử/verify ở bước triển khai. Live smoke cần quyền sản xuất rõ và giới hạn lượt gửi; không lấy fixtures làm evidence thật.

## 8. Áp dụng cho job đang dở và hoàn tác

Khi được yêu cầu triển khai, trước sửa ghi baseline/diff của checkout và các job bị ảnh hưởng. Không bắt đầu sản xuất song song trong lúc sửa tệp bảo vệ. Từng gói có diff review được, ảnh hưởng tương thích và bước quay lại phiên bản cũ.

Giữ vocab-predator-english-9x16-65s-001; không tạo job mới cùng nội dung để né integrity hoặc request unknown. Các trạng thái mới phải tương thích journal cũ; nếu không thể ánh xạ bằng evidence, giữ cần can thiệp. Rollback code không có nghĩa rollback nhật ký/decision đã ghi. Nếu rollback sau thay trạng thái, phải kiểm khả năng đọc trạng thái đó bằng bản cũ trước khi nhận code trở lại.

Tài liệu hướng dẫn và code chỉ được đồng bộ sang checkout chính sau khi rà diff có chọn lọc; không sao chép SQLite, runs, token, profile hoặc ledger. Những phần đã sửa từ trước cần được giữ hoặc quyết định rõ, không reset toàn bộ nhánh.

## 9. Bước triển khai đầu tiên khi được yêu cầu thực hiện

1. K0: lập bản diff chính sách quyền và danh sách checkout/tệp áp dụng, lấy quyết định về quyền adopt/giao việc đang mâu thuẫn.
2. K1 + K2: chỉnh quyền nhận diff và đường quan sát/dừng trước khi mở rộng worker.
3. K3: bổ sung recovery có evidence để giải quyết điểm kẹt request; không nhận lỗi UNKNOWN hiện tại làm thất bại đã xác nhận.
4. K4 + K5: điều phối session/worker và bàn giao output.
5. K6 + K7: cập nhật skill đúng capability và nghiệm thu theo tình huống được yêu cầu.

Đây là thứ tự phát triển hệ thống. Tiếp tục sản xuất video là quyết định riêng sau khi chính sách/runtime/job state đáp ứng yêu cầu; kế hoạch hướng video vẫn giữ riêng.

## 10. Tiến độ

- Đã hoàn tất: đọc và so sánh quyền/rules/skills/mã vận hành; ghi phát hiện và kế hoạch sửa này.
- Chưa thực hiện: mọi gói K0-K7, sửa tệp bảo vệ, nhận code, tests, live smoke và sản xuất video.
- Cụm nhắc riêng: **“Thực hiện kế hoạch sửa phân quyền và kiểm soát ngày 03/10.”**
