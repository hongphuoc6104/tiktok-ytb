# Kho từ vựng và vòng làm video theo từ

Kho nằm trong `vocab/`, tách khỏi bộ điều phối. Mã Python của kho nằm trong integrity baseline. Dữ liệu bank/ledger và cấu hình channel không nằm trong baseline: channel được chuyển thành brief khi tạo job, thay channel chỉ áp dụng job mới. Thêm hoặc sửa mục kho không thay mã bảo vệ của job đang chạy.

| File | Vai trò |
|---|---|
| `vocab/topics.json` | Danh mục chủ đề; `id` trùng tên file nguồn |
| `vocab/sources/*.txt` | Nguồn do người viết, mỗi dòng một nghĩa (xem `vocab/sources/FORMAT.md`) |
| `vocab/bank.jsonl` | Bản biên dịch của nguồn, một mục JSON mỗi dòng, id ổn định |
| `vocab/ledger.json` | Trạng thái từng mục: `reserved` (đang làm) hoặc `done` (đã có video) |
| `vocab/channel.json` | Mặc định của kênh khi sinh brief: tỷ lệ, thời lượng, phong cách, text_style |
| `vocab/briefs/JOB.json` | Brief 3.0 sinh ra cho từng job |

## Một video là một nghĩa

Mỗi dòng nguồn là MỘT nghĩa. Từ nhiều nghĩa được tách thành nhiều mục, mỗi mục có id
riêng (`bank.n.finance`, `bank.n.river`) và được đánh dấu riêng trong ledger. Khi rút một
nghĩa ra làm kịch bản, brief tự động mang theo lời nhắc về các nghĩa anh em, kèm dấu
"ĐÃ CÓ VIDEO RIÊNG" nếu nghĩa đó đã làm rồi, nên kịch bản không dạy trùng.

`build` chặn khi cùng `word|pos` có hai nghĩa khác nhau mà thiếu khoá nghĩa ở cột 5 —
đó là cách kho buộc người viết tách nghĩa thay vì gộp bừa. Cùng một nghĩa xuất hiện ở hai
chủ đề thì được gộp thành một mục có hai chủ đề, không nhân bản.

## Cổng bắt buộc

`config.brief_policies` trỏ tới `vocab.policy:check`. `Pilot.new` và `revise_brief` chạy
chính sách này trước khi job ra đời, nên brief dạy từ vựng KHÔNG thể vào pipeline nếu:

- thiếu dòng `Mã mục trong kho từ vựng: <id>` trong `planning.domain_requirements`;
- mang mã mục không có thật trong `bank.jsonl`;
- mang mục đang giữ chỗ cho job khác, hoặc mục đã có video ở job khác.

Brief không dạy từ vựng đi qua bình thường: bộ điều phối vẫn không gán cứng chủ đề nào,
toàn bộ hiểu biết về từ vựng nằm trong `vocab/policy.py` (`SIGNALS` quyết định brief nào
bị coi là dạy từ vựng — sửa ở đó, không sửa `pilot.py`).

Kiểm tra định kỳ bằng `python3 vocab/bank.py audit`: liệt kê job nào làm ngoài kho, job nào
mang mã mục lạ, và job nào video đã duyệt mà quên `mark`.

## Vòng làm việc

```bash
python3 vocab/bank.py build                       # sau mỗi lần sửa sources/
python3 vocab/bank.py status                      # còn bao nhiêu từ, đã làm bao nhiêu
python3 vocab/bank.py next --count 10             # xem trước 10 từ kế tiếp, chưa giữ chỗ
python3 vocab/bank.py next --topic food-drink --level A2 --count 10
```

Bắt đầu một video:

```bash
python3 vocab/bank.py start vocab-010 --mode review
```

`start` giữ chỗ từ kế tiếp, ghi `vocab/briefs/vocab-010.json` rồi gọi `pilot.py new`. Nếu
`pilot new` lỗi, từ được trả lại kho ngay. Muốn xem brief trước khi tạo job thì dùng `draw`:

```bash
python3 vocab/bank.py draw vocab-010 --topic emotions-feelings
python3 pilot.py new vocab-010 --brief vocab/briefs/vocab-010.json --mode review
```

Sau đó chạy đúng quy trình ba phần trong [workflow.md](workflow.md). Khi phần video đã
được duyệt:

```bash
python3 vocab/bank.py mark vocab-010 --note 'Đã xuất bản 9:16'
```

`mark` xác minh đủ ba quyết định hiện tại và bản xuất trong video/ khớp artifact trước khi ghi. Nếu xuất bị gián đoạn, resume trước khi mark. Job chưa có quyết định duyệt
hợp lệ sẽ bị chặn, nên ledger không thể đánh dấu xong một video chưa làm xong. Video làm
ngoài pipeline thì đánh dấu thủ công, bắt buộc kèm lý do:

```bash
python3 vocab/bank.py mark vocab-9x16 --entry procrastinate.v --force \
    --note 'Video cũ, đã đăng' --video 'link'
```

Job bị huỷ thì trả từ về kho: `python3 vocab/bank.py release vocab-010`.

Làm lại một từ đã có video là việc có ý thức, phải nói rõ:

```bash
python3 vocab/bank.py draw vocab-020 --word procrastinate --redo --note 'Làm bản mới, hình cũ mờ'
```

Không có `--redo` thì từ đã `done` không bao giờ được rút ra nữa. Có `--redo`, bản ghi cũ
được đẩy vào `previous` trong ledger chứ không bị xoá.

Các lệnh ghi (`draw`, `start`, `queue`, `mark`, `release`) chạy trong một khoá file
(`vocab/.ledger.lock`), vì hai phiên làm việc song song từng ghi đè mất bản ghi của nhau.

## Làm nhiều video một lượt

```bash
python3 vocab/bank.py queue --count 5 --mode auto --prefix vocab-
python3 pilot.py batch --queue vocab/queue.json
```

`queue` rút 5 từ khác nhau, tạo 5 job liên tiếp (mã tự tăng, bỏ qua mã đã có trong `runs/`
và mã đang giữ chỗ) rồi ghi danh sách vào `vocab/queue.json` đúng định dạng `pilot.py
batch` cần. Hết từ hợp bộ lọc giữa chừng thì dừng lại, các job đã tạo vẫn giữ nguyên và
hàng đợi chỉ chứa những job tạo được. Sau khi batch chạy xong, đánh dấu từng job bằng
`mark` — ledger vẫn đòi phần video đã được duyệt.

## Chọn từ theo thứ tự nào

Mặc định `--order level`: A1 trước, trong cùng mức thì theo thứ tự chủ đề rồi thứ tự dòng
trong file nguồn. `--order topic` đi hết chủ đề này mới sang chủ đề khác. Lọc thêm bằng
`--topic`, `--level`, `--pos`, hoặc ép đúng một từ bằng `--word`.

Một job chỉ giữ chỗ một mục. `draw` từ chối nếu job đó đã giữ chỗ, để không có chuyện hai
từ cùng gắn vào một video.

## Tra cứu một từ

```bash
python3 vocab/bank.py show --word bank
python3 vocab/bank.py topics
```

`show` liệt kê mọi nghĩa của từ kèm trạng thái và job đã dùng. `topics` cho biết từng chủ
đề còn bao nhiêu từ chưa làm.

## Rà trùng nghĩa

```bash
python3 vocab/bank.py lint
```

`lint` tìm hai mục cùng từ và cùng từ loại mà lời giải nghĩa thật ra nói về một nghĩa —
tức hai video sẽ dạy trùng nhau. Đây là lỗi mà `build` không bắt được: hai mục đó có khoá
nghĩa khác nhau nên id vẫn hợp lệ. Sửa bằng cách xoá một dòng trong `vocab/sources/`, hoặc
nếu đọc kỹ thấy đúng là hai nghĩa riêng thì thêm cặp id vào `vocab/lint-allow.json` kèm
một dòng `why` giải thích. Chạy `lint` sau mỗi lần thêm từ mới.

## Sửa và mở rộng kho

Thêm từ bằng cách sửa file trong `vocab/sources/`, rồi `build` lại. `build` chỉ ghi đè
`bank.jsonl`; `ledger.json` không bị đụng tới nên các từ đã làm vẫn giữ dấu. Xoá một dòng
nguồn không xoá dấu trong ledger — dấu cũ nằm lại vô hại và trở lại có hiệu lực nếu từ
được thêm lại.

Kiểm tra kho: `.venv/bin/python -m pytest vocab/test_bank.py -q`.
