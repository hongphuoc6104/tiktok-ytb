# Video Pilot — bản thử 5 module

Mở **thư mục này** thành một project riêng trong Antigravity 2.0. Không mở chung với VideoShotCut.

## Bắt đầu

```bash
source .venv/bin/activate
python3 pilot.py doctor
python3 pilot.py status pilot-001
python3 pilot.py next pilot-001
```

Dự án đã có môi trường Python, TTS riêng và dependencies Node khóa bằng package-lock.json.
Nếu chuyển sang máy khác: `uv venv --python 3.12 .venv`, cài requirements.txt vào .venv;
`npm ci`; tạo .venv-tts với Python 3.10 rồi cài tts-requirements.lock vào đó;
tạo .venv-en với Python 3.11 rồi cài en-requirements.lock vào đó (Alba tiếng Anh).
Mô hình TTS tải về lần đầu qua Hugging Face; không cần API trả phí.

## Giao việc cho Antigravity

> Đọc AGENTS.md của Video Pilot, báo mã handshake trong file, chạy doctor và status pilot-001. Tiếp tục đúng next. Không dùng explainer-pipeline cũ; không tự duyệt module. Mỗi lần chờ duyệt, trình bày artifact, revision và câu lệnh duyệt tương ứng.

Agent báo đúng mã và trạng thái mới là bằng chứng ban đầu Rules được đọc.
Chưa coi integration Antigravity là đã kiểm chứng chỉ vì file có mặt trên đĩa.
Có thể ghi xác nhận thực tế vào runs/pilot-001/integration-check.json sau khi bạn chứng kiến handshake.

## Duyệt module

Đọc artifact được status chỉ ra, rồi phản hồi rõ **module và revision**. Ví dụ:

> Tôi duyệt module control revision 1 của pilot-001.

Sau phản hồi đó, agent mới được ghi nhận:

```bash
python3 pilot.py approve pilot-001 control --revision 1 --note 'Tôi duyệt module control revision 1 của pilot-001.'
python3 pilot.py run pilot-001 content
```

Lệnh approve ghi quyết định đã có, không tạo ra quyền tự duyệt cho agent.
Đây là guardrail trong một tài khoản máy, không phải xác thực người duyệt độc lập.

## Nối Flow thật sau khi content được duyệt

```bash
python3 pilot.py flow-login pilot-001
```

Bạn đăng nhập Chrome profile video-pilot trực tiếp. Agent xem giao diện Flow,
chọn tạo **ảnh**, Nano Banana 2, dọc 9:16, một đầu ra và xác minh **0 credit**.
Ghi quan sát mới vào JSON (observed_at là Unix timestamp hiện tại):

```json
{
  "mode": "image",
  "model": "Nano Banana 2",
  "credits_per_generation": 0,
  "profile": "video-pilot",
  "account_confirmed": true,
  "observer": "Tên người/agent thực sự kiểm tra giao diện",
  "observed_at": 0,
  "screenshot": "/absolute/path/to/actual-flow-screenshot.png"
}
```

Không dùng giá trị mẫu 0 cho observed_at. Quan sát quá 10 phút phải làm mới.
Ảnh chụp là bằng chứng cho kiểm tra trực quan, không phải OCR tự chứng minh giá credit.
Nếu không xác minh được, giữ blocked.

```bash
python3 pilot.py flow-preflight pilot-001 --evidence /absolute/path/to/observation.json
python3 pilot.py run pilot-001 images
```

Nếu timeout sau gửi: kiểm tra project Flow. Tải đúng kết quả đã có rồi dùng:

```bash
python3 pilot.py flow-reconcile pilot-001 --scene SC01 --asset /path/to/verified-image.png --note 'Đã đối chiếu ảnh với prompt và lần tạo trong Flow.'
python3 pilot.py run pilot-001 images
```

Nếu không tìm được kết quả cũ, dừng và điều tra; không xóa journal để gửi lại.
CLI bên thứ ba vẫn có lệnh video, nhưng adapter sản xuất chỉ xuất chức năng image.
Rules cấm gọi trực tiếp công cụ bên ngoài để đi vòng qua gate.

## Âm thanh và dựng

Sau duyệt images: `python3 pilot.py run pilot-001 audio`.
Bản 9:16 đọc tiếng Việt kèm phụ đề (VieNeu-TTS, giọng preset trong `config.json`).
Bản 16:9 đọc tiếng Anh, ẩn phụ đề (Pocket TTS, giọng Alba ở tốc độ gốc) và chạy theo timeline
tiếng Anh riêng, nên điểm cắt ảnh bám lời tiếng Anh chứ không bám tiếng Việt.
Brief có `aspect_ratio` là `dual` hoặc `16:9` thì mỗi cảnh phải có `narration_en`.
Môi trường tiếng Anh nằm riêng ở `.venv-en`; tạo lại bằng
`uv venv --python 3.11 .venv-en` rồi
`uv pip sync --python .venv-en/bin/python --index-strategy unsafe-best-match en-requirements.lock`.
Runtime dùng PyTorch CPU-only và lượng tử hóa dynamic INT8 cho attention/FFN;
bộ giải mã âm thanh vẫn FP32. Không cần GPU hoặc tài khoản Hugging Face cho giọng có sẵn.
`en_threads=4`, `en_temperature=0.3`, `en_seed=42`; không giảm tốc hoặc đổi cao độ.
Model và embedding Alba tải lần đầu, các lần sau dùng cache (có thể đặt `HF_HUB_OFFLINE=1`).
Giọng Alba MacKenna (casual), CC BY 4.0; xem [ghi công giọng](docs/voice-attribution.md).
Đo mẫu ngắn trên Ryzen 5 6600H: RAM đỉnh khoảng 1,1 GiB, RTF 0,26–0,28;
chưa xác nhận hiệu năng trên Xeon E3-1241 v3. Mô hình nạp FP32 trước khi lượng tử hóa.
Các revision âm thanh cũ giữ nguyên; muốn thay âm thanh của job cũ cần revision mới và duyệt lại.
Nghe WAV, xem SRT và thời lượng rồi duyệt revision audio.
Sau đó: `python3 pilot.py run pilot-001 render`.
Nếu TTS ngoài 45–60 giây, reject content và sửa draft rồi duyệt lại; không cắt tự động.
Bản thử không thêm nhạc hoặc dịch vụ cloud thay thế.

## Kiểm tra, sửa và tiếp tục

```bash
python3 -m unittest discover -s tests -v
python3 pilot.py validate pilot-001 content
python3 pilot.py reject pilot-001 content --note 'Nêu rõ đoạn cần sửa'
python3 pilot.py resume pilot-001
```

Sửa kịch bản ở runs/pilot-001/draft/content.json. Mỗi lần run tạo revision mới.
Không sửa output.json để tự đổi checks hoặc đánh dấu hoàn tất.
Thay Rules/công cụ/schema/tests sau khi tạo job sẽ chặn job vì integrity khác.
Muốn phát triển phiên bản mới: kết thúc sản xuất, kiểm tra thay đổi rồi tạo job mới;
không cập nhật integrity baseline của job cũ để vượt gate.

## Những gì chưa được bảo đảm

Kiểm tra đủ ý xác minh ánh xạ, không chấm chất lượng ngữ nghĩa tự động.
Phụ đề căn theo đoạn WAV, chưa có word-level alignment.
Flow phụ thuộc giao diện bên thứ ba; credit và tài khoản phải được kiểm tra thật.
Người có toàn quyền filesystem vẫn có thể sửa cả code và dữ liệu; đây không phải sandbox.
Tốc độ 10–30 video/ngày chưa nằm trong nghiệm thu bản thử.

## Module Nội dung v2

Đã bổ sung yêu cầu riêng theo công việc, nhân vật, ánh xạ lời dẫn, kiểm tra nháp và review có phiên bản. Xem [goal M1](docs/M1-GOAL.md) và [hướng dẫn nghiệm thu Antigravity](docs/M1-ANTIGRAVITY.md). Trạng thái nghiệm thu thật chưa đạt; không dùng kết quả test thay cho duyệt của người dùng.

## Kết nối Antigravity CLI

Đã có adapter M1 qua agy. Xem [cài đặt và sử dụng](docs/AGY-SETUP.md), [kết nối thật](reports/agy-connection.json) và [kiểm thử](reports/agy-tests.txt). Adapter chỉ sinh nội dung, kiểm tra rồi dừng chờ duyệt.

## Module ② — hình ảnh v2

[Hướng dẫn M2](docs/M2-FLOW.md): ảnh chuẩn → ba cảnh → sáu cảnh, tham chiếu nhân vật, sửa từng cảnh và khôi phục timeout. [Báo cáo triển khai](reports/M2-RESULT.md). Mẫu prompt của người dùng hỗ trợ 9:16/16:9; lượt thử hiện tại dùng 9:16, không tạo video AI.
