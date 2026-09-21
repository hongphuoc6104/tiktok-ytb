# Định dạng file nguồn từ vựng

Mỗi file là một chủ đề, tên file trùng `id` trong `vocab/topics.json`.
Mỗi dòng là MỘT NGHĨA của một từ:

```
word|pos|nghĩa tiếng Việt|cefr[|khoá nghĩa]
```

- `word`: viết thường (`take`, `look after`, `ice cream`); chỉ viết hoa khi là từ viết tắt (`ATM`, `GDP`).
- `pos`: n, v, adj, adv, prep, conj, pron, det, phr, num, int.
- `nghĩa tiếng Việt`: ngắn gọn, đúng một nghĩa, không kèm ví dụ, không kèm dấu `|`.
- `cefr`: A1, A2, B1, B2, C1.
- `khoá nghĩa` (cột 5, tuỳ chọn): chữ thường/gạch nối, bắt buộc khi cùng một `word|pos`
  xuất hiện nhiều lần với nghĩa khác nhau — mỗi nghĩa thành một mục riêng, một video riêng.

Ví dụ tách nghĩa:

```
bank|n|ngân hàng|A2|finance
bank|n|bờ sông|B1|river
```

Dòng bắt đầu bằng `#` là chú thích. `python3 vocab/bank.py build` sẽ chặn nếu sai định dạng,
sai mức CEFR, hoặc trùng `word|pos` mà không có khoá nghĩa.
