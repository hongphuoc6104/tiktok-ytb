# Thử Minh Quân Pro — tiếng Việt và Anh–Mỹ

Bộ thử độc lập, giữ **VieNeu v3 Turbo / ONNX FP32 / Minh Quân Pro**. Không sửa
cấu hình sản xuất, thư viện cài sẵn, kịch bản đã duyệt hay dữ liệu job. Các biến thể
`I` và `<en>…</en>` chỉ áp dụng vào phần tiếng Anh được đánh dấu trong bộ thử.

## Nghe và đánh giá

Mở `artifacts/index.html` trực tiếp hoặc trang local được phục vụ bởi lệnh `serve`.
Chọn câu, nghe các bản A/B/C, chấm điểm, ghi lỗi kèm thời điểm và tải phiếu JSON.
Các chữ A/B/C được đảo riêng cho từng câu; chúng không đại diện cố định cho một
cấu hình. Trang nghe không tự điền điểm hoặc xác nhận đã nghe.

Người đánh giá tiếng Anh cần phân biệt được âm, trọng âm và nhịp Anh–Mỹ. Nếu không
có người/công cụ nghe phù hợp, trạng thái là **chưa đánh giá**, không phải đạt hoặc
không đạt. Phiếu thử nghiệm không phải quyết định duyệt media/video của Pilot.

## Chạy từ gốc dự án

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py prepare
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py run A
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py serve --port 8768
```

Máy chủ chỉ nghe ở `127.0.0.1`. Không tải/cập nhật model hoặc dùng API trả phí.
Nếu model chưa có trong cache, dừng để báo thiếu môi trường.

Sau khi nhận phiếu nghe thật:

```bash
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py review A --file /duong-dan/danh-gia-minh-quan-A.json
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/lab.py run B
```

Tiếp tục tương tự theo thứ tự `A → B → C-speed → C-split → D → E → final`.
Mỗi vòng chỉ chạy khi có phiếu hợp lệ của vòng trước. Không tự chọn bằng âm vị hoặc
thời lượng. Chạy lại cùng lệnh để tiếp tục nếu bị gián đoạn; có thể dùng `--limit 1`
để kiểm tra một bản trước. Phiếu đã nhập không bị ghi đè.

| Vòng | Các biến thể | Phạm vi |
|---|---|---|
| A | Hiện tại / chính tả Anh chuẩn / thẻ tiếng Anh | 13 mục có tiếng Anh × 3, cộng 8 câu Việt đối chứng: 47 WAV |
| B | Hiện tại / giữ dấu câu | 21 mục + 2 mẫu câu hỏi ngắn, mỗi mục 2 bản |
| C-speed | 0,92 / 0,96 / 1,00 | 21 mục, các tốc độ dùng chung WAV nguồn |
| C-split | Cả cảnh / từng câu / chuyển ngôn ngữ | 21 mục + từ đơn `wake`, cụm `get up` |
| D | Temperature 0,65 / 0,50 / 0,80 | 8 mục khó nhất theo phiếu C-split, 3 lần độc lập mỗi cấu hình |
| E | Cân âm lượng / EQ và limiter sản xuất | 8 mục khó, dùng chung WAV nguồn cho mỗi cặp |
| final | Cấu hình được chọn | 8 mục giữ lại + 5 cảnh thực tế |

Ưu tiên ít bản có lỗi nghiêm trọng hơn, sau đó điểm trung bình cao hơn. Nếu tỉ lệ
lỗi bằng nhau và điểm chênh không quá 0,1/5, giữ phương án ít thay đổi hơn (hiện tại,
0,92, cả cảnh, temperature 0,65, hoặc chỉ cân âm lượng). Cấu hình thắng một vòng
không có nghĩa đã đạt yêu cầu cuối cùng.

## Dữ liệu và kiểm soát phép thử

- `corpus.json`: 16 mục chính, 5 cảnh từ `vocab-wake-004`, 8 mục giữ lại từ
  `vocab-wake-up-003`, 4 mục chẩn đoán. Lưu câu nguyên văn, vị trí đoạn tiếng Anh,
  đường dẫn revision, scene và dấu kiểm tra nội dung. Tám mục giữ lại không được
  tổng hợp trước vòng cuối; chúng gần chủ đề đang học, chưa đại diện cho mọi từ vựng.
- `frozen.json`: dấu kiểm tra bộ câu và các file đối chứng cần giữ nguyên.
- `environment.json`: phiên bản gói, hash model/codec đã nạp, mã thử và hồ sơ giọng.
- `history/`: bản sao nguyên WAV sản xuất revision 2 cùng yêu cầu và metadata cũ.
- `cache/<hash>/`: WAV nguồn dạng float, từng đơn vị đọc và nhật ký đầu vào,
  câu sau chuẩn hóa, âm vị, seed, khoảng nghỉ. Không cắt đầu/cuối WAV nguồn.
- `rounds/<vòng>/`: kế hoạch khóa, WAV để nghe, kết quả đo, nhật ký xử lý và trang nghe.
- `reviews/`, `decisions/`: phiếu nghe nguyên bản và quyết định chọn cấu hình thử.

WAV mới là clip thử độc lập, không giả là tái tạo bit-for-bit toàn bộ khâu ghép
của bản sản xuất. WAV lịch sử là đối chứng thật. Các seed được ghép theo câu và lần
tạo; seed khác nhau giữa ba lần ở D, cố định khi so sánh yếu tố khác. Không bảo đảm
bit-identical giữa phần cứng hoặc phiên bản runtime khác nhau.

Nhánh giữ dấu câu dùng thay thế hàm chỉ trong tiến trình thử, luôn khôi phục sau
lượt gọi. Không sửa `site-packages`. Vẫn chuẩn hóa số và từ viết tắt. Không dùng
thẻ cảm xúc trong phép thử này. Các khoảng nghỉ đã có được đo trước khi bù; không
cộng thêm nguyên khoảng nghỉ vào WAV đã có im lặng.

Âm lượng nghe đối chiếu là **−23 LUFS**, sai số không quá 0,5 LUFS. Nhánh hậu kỳ E
thực hiện EQ, mức −14 LUFS và limiter −1,5 dB của sản xuất trước, rồi hạ mức phát
về −23 LUFS để so sánh công bằng. Không nén động riêng bản đối chứng để làm nó to
hơn. Tốc độ được đổi sau khi tạo nguồn, giống cách triển khai hiện tại.

## Kiểm tra và kết luận

```bash
sys/.venv-tts/bin/python -B -m unittest discover -s sys/experiments/tts-minh-quan-bilingual -p 'test_*.py' -v
sys/.venv-tts/bin/python -B sys/experiments/tts-minh-quan-bilingual/audit.py
```

Điều kiện đạt: không bỏ/thêm/lặp từ, không sai nghĩa do thanh điệu, không sai âm
hay trọng âm từ đang dạy; từng tiêu chí trung bình ≥ 4/5, không điểm nào < 3/5;
đồng thời đạt trên ba lần tạo của cấu hình D và bộ kiểm tra cuối. Nhận diện vẫn là
Minh Quân Pro được chấm riêng. Phép đo không chứng minh âm đầu/cuối không bị nuốt.

Không có vòng sửa tự động vô hạn. Công cụ chạy một lượt theo trình tự trên. Nếu
còn lỗi cụ thể sau vòng cuối, bàn giao bằng chứng và chỉ cân nhắc tối đa một đợt
sửa riêng có lưu dấu, không sửa đè báo cáo cũ. Không tự tích hợp sản xuất.
