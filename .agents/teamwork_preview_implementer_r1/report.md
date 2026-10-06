# Implementer R1 Report

> [!WARNING] **Skepticism Disclaimer**
> Tôi tự tin cao về việc triệt tiêu dải trắng, khắc phục hiển thị phụ đề và loại bỏ giật viền trên job hiện tại vì đã đo đạc trực tiếp các pixel và frame kết xuất thực tế; tuy nhiên thuật toán crop tự động phụ thuộc vào ngưỡng màu trắng biên (> 225) nên có thể hành xử khác nếu nhà tạo ảnh sinh nền có họa tiết hoặc gradient phức tạp sát đáy.

## 1. What I changed
- `sys/renderer/captions.mjs`: Bổ sung `zIndex: 30` vào thuộc tính của `captionStyle`.
- `sys/renderer/render.mjs`: Bổ sung `zIndex` vào danh sách ngoại lệ không gắn thêm đơn vị `'px'` khi Playwright evaluate style CSS (`!['fontWeight', 'lineHeight', 'zIndex'].includes(key)`).
- `sys/renderer/index.tsx`:
  - Đặt `let rot = 0;` (thay vì `let rot = boilJitter(frame, idx) * 1.2;`), loại bỏ hoàn toàn bước nhảy góc xoay rời rạc chu kỳ 4-frame gây chớp giật mép viền trắng của sticker.
  - Gắn `zIndex: 30` vào container phụ đề `<div data-check="subtitle">` đảm bảo phụ đề luôn nổi trên các lớp graphics (`scene.layers` có `zIndex: 5`).
- `sys/tools/matte_sticker.py`: Bổ sung hàm `crop_background_plate(image_input, white_thresh=225)` và `process_background(src, dst)` nhằm tự động quét và xén bỏ dải trắng caption clearance (18–20%) và viền trắng mép ảnh nền.
- `sys/colab_bridge/job_worker.py` & `sys/adapters.py`: Tích hợp `process_background` vào luồng chuẩn bị tài nguyên `public/` cho background plate (`kind: 'background'` hoặc `bg: true`).
- `sys/tests/test_visual_defects_fix.py`: Tạo mới bộ unit tests gồm 8 ca kiểm thử hồi quy bao quát z-index stacking context, CSS parsing trong render script, hàm crop background plate, và tính liên tục vi phân của chuyển động sticker.
- `video/vocab-loyal-emperor-9x16-002/vocab-loyal-emperor-9x16-002_r1_final.mp4` & `sys/runs/vocab-loyal-emperor-9x16-002/revisions/render/2/video.mp4`: Kết xuất lại video hoàn chỉnh end-to-end 1080x1920 @ 30fps.

## 2. Why
- **R1 (Dải trắng 1/5 đáy)**: Nano Banana khi sinh ảnh theo prompt `caption_clearance` đã để trống 18–20% màu trắng ở đáy ảnh. Khi dùng `objectFit: 'cover'`, dải trắng này chiếm 1/5 màn hình dọc. Xén bỏ biên trắng đưa ảnh về tỉ lệ chuẩn, giúp `cover` lấp đầy toàn bộ khung 1080x1920 không méo tỷ lệ.
- **R2 (Mất phụ đề)**: `scene.layers` có `zIndex: 5`, trong khi phụ đề thiếu thuộc tính `zIndex` (mặc định CSS `auto`/0), dẫn đến background plate đè lên phụ đề. Đặt `zIndex: 30` cho cả style và container phụ đề, đồng thời sửa lỗi render.mjs gán `zIndex: 30px` gây vô hiệu CSS.
- **R3 (Chớp giật viền trắng)**: `boilJitter` nhảy góc xoay giả ngẫu nhiên rời rạc mỗi 4 frame (`Math.floor(frame / 4)`), làm viền trắng tương phản cao của sticker bị xoay giật cục 7.5 lần/giây. Triệt tiêu bước nhảy góc này giúp chuyển động trơn tru.
- **R4 (Unit tests)**: Ngăn ngừa tái phát lỗi phân tầng layer, lỗi cú pháp style và suy thoái animation chuyển động.
- **R5 (End-to-end output)**: Tái tạo và cung cấp bản video hoàn chỉnh cuối cùng đáp ứng tiêu chuẩn nghiệm thu thị giác.

## 3. Verification Record
- **Deep Verification (ran actual tests):**
  - Chạy `pytest sys/tests/test_visual_defects_fix.py sys/tests/test_matte_sticker.py -q`: 11/11 tests PASS 100%.
  - Chạy toàn bộ test suite liên quan (`test_remote_render.py`, `test_renderer_effects.py`, `test_layered_pipeline.py`): 43/43 tests PASS 100%.
  - Trích xuất 6 frame video đại diện (t = 5s, 15s, 25s, 35s, 45s, 54s) bằng `ffmpeg` và phân tích pixel bằng `PIL`/`numpy`:
    - 0/6 frame có pixel trắng ở 20% vùng đáy (background tràn viền 100%, không còn dải trắng).
    - Cả 6 frame đều có text phụ đề tương phản cao nổi rõ ràng trên nền tối tại đáy màn hình.
  - Phân tích chuỗi 15 frame liên tiếp tại vùng sticker của SC01: Mean Absolute Difference giữa các frame liên tiếp là 2.87 với độ lệch chuẩn 0.46 (ổn định, không có xung đột biến giật hình do bước nhảy 4-frame).
- **Shallow Verification (manual run only):**
  - Kiểm tra kích thước và định dạng video: `video.mp4` đạt 17.9 MB, 1080x1920, 30fps, audio AAC stereo đồng bộ.
  - Kiểm tra file tĩnh trích xuất `SC01.png` – `SC06.png` trong thư mục render.
- **Unverified aspects:**
  - Chưa kiểm tra trường hợp background plate có nền tự nhiên là màu trắng thuần (ví dụ cảnh bão tuyết hoặc sương mù trắng xóa) xem thuật toán crop biên có xén quá tay hay không.
  - Chưa kiểm tra render trên môi trường GPU Colab từ xa (chỉ render local bằng Google Chrome headless của hệ thống).

## 4. Known Issues
- `Minor Robustness Risk` — Thuật toán `crop_background_plate` dùng ngưỡng pixel `white_thresh=225`. Nếu ảnh nền cố tình vẽ phong cảnh tuyết trắng hoặc sương mù sát viền trên/dưới, thuật toán có thể xén bớt một phần biên ảnh thật trước khi dừng lại ở vùng có chi tiết màu.

## 5. Untested Edge Cases & Next Step
- **Untested Edge Cases:** Trường hợp prompt sinh ảnh nền có dải màu gradient xám/be ở chân (không phải trắng thuần > 225) làm dải clearance không bị cắt hoàn toàn; trường hợp sticker có kích thước cực lớn đè lên vùng phụ đề ở đáy.
- **Next Step:** Reviewer kiểm tra trực tiếp file video tại `video/vocab-loyal-emperor-9x16-002/vocab-loyal-emperor-9x16-002_r1_final.mp4` bằng trình phát video để đánh giá trải nghiệm thị giác thực tế trên màn hình dọc.
