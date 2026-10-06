# Khả năng trình render (Renderer Capabilities)

Tài liệu này ghi nhận hiện trạng kỹ thuật thực tế của trình render Remotion (`sys/renderer/index.tsx`, `render.mjs`) trong hệ thống Video Pilot.

Khác với bảng thuật ngữ điện ảnh ổn định lâu dài trong `.agents/skills/vp-production/references/cinematography.md`, tài liệu này thay đổi theo từng phiên bản nâng cấp của engine và renderer.

---

## 1. Khả năng đã hỗ trợ trực tiếp trong mã nguồn trình render (Remotion Engine)

Các hiệu ứng này đã được lập trình sẵn trong `sys/renderer/index.tsx`, được kích hoạt qua trường `effect` và `focus` của từng beat trong `scene.images`:

| Hiệu ứng / Kỹ thuật | Trạng thái trong Code | Cơ chế hoạt động & Tham số | Lưu ý khi áp dụng |
|---|---|---|---|
| **Cắt gắt (`cut` / `hold`)** | Đã hỗ trợ | Chuyển thẳng sang ảnh mới tại mốc `at`. Nếu `hold`, camera đứng yên không kích hoạt chuyển động Ken Burns. | Thích hợp cho nhịp kể nhanh, giải thích logic, hoặc giữ nguyên biểu đồ số liệu. |
| **Hòa tan (`fade` / Dissolve)** | Đã hỗ trợ | Lớp ảnh mới tăng dần độ mờ đục `opacity` từ 0 lên 1 trong tối đa 0.3s (hoặc nửa thời lượng beat), đè lên ảnh trước. | Phù hợp biến đổi thời gian, hồi tưởng hoặc làm mềm chuyển cảnh. |
| **Trượt ngang / Whip Pan (`slide_left`)** | Đã hỗ trợ | Dịch chuyển tọa độ `translateX` từ 100% về 0% có gia tốc mượt, kết hợp Dynamic Motion Blur (`blur(Xpx, 0px)`) theo vận tốc trượt trong tối đa 0.3s. | Lật trang, sang chủ đề mới, tạo cú lia máy chuyển cảnh điện ảnh. |
| **Phóng to êm (`zoom_in`)** | Đã hỗ trợ | Tăng tỷ lệ `scale` từ 1.0 lên 1.08 theo đường cong gia tốc phi tuyến (Bezier Easing). | Tập trung thị giác vào từ khóa hoặc chi tiết trọng tâm một cách mượt mà. |
| **Thu nhỏ êm (`zoom_out`)** | Đã hỗ trợ | Giảm tỷ lệ `scale` từ 1.08 về 1.0 theo đường cong gia tốc phi tuyến (Bezier Easing). | Hé lộ bối cảnh rộng hơn (Pull-out) êm ái, tự nhiên. |
| **Zoom dồn giật (`punch_in`)** | Đã hỗ trợ | Phóng to giật 1.25x trong 0.35s đầu với Spring dynamic rồi dịu về 1.08x, kèm rung nhẹ. | Nhấn mạnh khoảnh khắc ngạc nhiên, sốc, phát hiện bất ngờ. |
| **Lia máy ngang (`pan_left` / `pan_right`)** | Đã hỗ trợ | Cố định `scale = 1.06`, dịch chuyển `translateX` qua lại có gia tốc êm ái. | Khảo sát tranh phong cảnh hoặc quét qua nhiều việc nhà. |
| **Auto Ken Burns** | Đã hỗ trợ | Khi `effect` không đặt và không phải `hold`: tự động luân chuyển chu kỳ 4 pha với đường cong Easing êm ái: (1) zoom in $\to$ (2) pan right $\to$ (3) zoom out $\to$ (4) pan left. | Đảm bảo video không bao giờ có khung hình chết (Never static frame). |
| **Tâm điểm tiêu cự (`focus`)** | Đã hỗ trợ | Nhận tọa độ `focus: {x, y}` (từ 0 đến 1) để gán cho `transformOrigin: x% y%`. Mặc định tâm là `{x: 0.5, y: 0.42}` (chuẩn 9:16). | Hướng chuyển động zoom/pan nhắm chính xác vào mặt nhân vật hoặc vật thể trọng tâm. |
| **Rung chấn màn hình (`shake`)** | Đã hỗ trợ | Rung máy ngẫu nhiên theo thuật toán Perlin/Simplex noise mô phỏng tay cầm máy quay thật (Handheld Camera Shake) tắt dần trong 0.28s. | Thể hiện cú va chạm, giật mình, tiếng nổ hoặc gõ mạnh một cách tự nhiên. |
| **Nét rung sống động (`line_boil`)** | **Đã hỗ trợ** | Bộ lọc nhiễu hữu cơ Procedural SVG Displacement Map (`<feTurbulence>` + `<feDisplacementMap>`) với 4 seed xoay vòng ở tần số 10 fps. Tự động kích hoạt qua `line_boil: true` hoặc `effect: 'line_boil'`. | Biến nét đen người que tĩnh thành hoạt họa sống động như *MinutePhysics*, người que "thở" tự nhiên, 0 chi phí AI. |
| **Nét vẽ tự chạy (`draw_on`)** | **Đã hỗ trợ** | Mặt nạ chuyển tiếp mềm `maskImage: linear-gradient(135deg, ...)` quét chéo từ góc trên-trái xuống dưới-phải trong `draw_duration` (mặc định 1.3s), tích hợp icon bút chì `✏️` dẫn đường. Kích hoạt qua `draw_on: true` hoặc `effect: 'draw_on'`. | Mở đầu cảnh ấn tượng, nét vẽ phác họa trực tiếp theo câu thoại mở màn của người dẫn truyện. |
| **Lớp phủ điện ảnh (Cinematic Overlays)** | Đã hỗ trợ | Lớp phủ Vignette tối 4 góc nhẹ nhàng và hạt Film Grain tinh tế trên toàn khung hình. | Hòa quyện nét vẽ 2D vào không gian thị giác, loại bỏ cảm giác ảnh thô. |
| **Kinetic Keyword Typography** | Đã hỗ trợ | Tách từ trong phụ đề, tự động highlight từ vựng mục tiêu (`target_word`) hoặc từ in hoa tiếng Anh bằng màu vàng phát sáng `#FACC15` kèm đổ bóng viền đen. | Không cần vẽ thêm text tĩnh trong ảnh, phụ đề tự làm nổi bật từ khóa. |
| **Interactive Practice Counter** | Đã hỗ trợ | Tự động đếm nhịp "3... 2... 1... 🎙️" dạng bóng thoại nổi khi cue có cờ `practice` hoặc chứa cụm "Cùng nhắc lại nhé". | Tương tác người học mà không cần dựng thủ công từng frame. |
| **Hoạt hình phân lớp (`scene.layers`)** | **Đã hỗ trợ** | Kết xuất đa lớp động (1 Background + N Sticker độc lập). Tự động kích hoạt Spring dynamics (`pop`, `pop_wobble`, `bounce`, `drop`, `slide_left`, `spin_grow`), nét rung hữu cơ `line_boil`, hiệu ứng xoáy hút `suck`, chớp sáng `bg_flash` và rung giật `shakeAt`. | Biến cảnh tĩnh thành hoạt họa 2.5D sống động, người que và đạo cụ nảy tự nhiên theo mốc thời gian từng từ. Content khai báo qua `scenes[].layers` + `images[].kind` (schema content-v3), prompt registry 1.2.0, sticker được tách nền trên Colab bằng `tools/matte_sticker.py`. Hướng dẫn: skill `vp-layered-motion`. |

---

## 2. Kỹ thuật thuộc cấp Kịch bản, Storyboard và Timeline (Không cần shader riêng)

Những kỹ thuật này không đòi hỏi mã nguồn renderer riêng biệt mà phụ thuộc hoàn toàn vào cách người dựng sắp xếp nội dung và mốc thời gian:

- **Match cut, Jump cut, Smash cut**: Tạo sự tương đồng hoặc tương phản bằng nội dung ảnh và đặt thời lượng beat (`at`) phù hợp.
- **L-cut / J-cut**: File âm thanh `narration.wav` chạy liên tục trên một rãnh audio riêng; các mốc chuyển ảnh `scene.start` và `beat.at` được cố tình căn lệch trước hoặc sau lời thoại 0.2s - 0.5s để tạo dòng chảy thị giác liền mạch.
- **Visual beats & Pacing**: Phân bổ mảng `images` trong mỗi scene với các giá trị `at` tương ứng với từng trọng âm câu thoại.
- **B-roll**: Chèn beat hình phụ hoặc đoạn clip ngắn (hỗ trợ cả `.mp4` / `.webm` qua `RemotionVideo`).

---

## 3. Kỹ thuật thuộc cấp Prompt và Tạo ảnh (Flow Image Generation)

Các góc máy và cỡ cảnh được quyết định khi lập prompt tạo ảnh tĩnh cho Flow, không phải xử lý biến dạng 3D trong renderer:

- **Cỡ cảnh**: `Establishing shot`, `Close-up`, `Extreme close-up`, `Over-the-shoulder`, `POV shot`.
- **Góc máy**: `High angle`, `Low angle`, `Dutch angle` (yêu cầu nghiêng đường chân trời trong prompt).
- **Call-out / Annotation vẽ tay**: Yêu cầu vẽ "red hand-drawn circle / arrow pointing at the focal object" trực tiếp trong prompt theo brand tolerance (tránh dùng element đồ họa máy móc đè lên).

---

## 4. Kỹ thuật chưa hỗ trợ (Unsupported)

| Kỹ thuật | Hiện trạng | Giải pháp thay thế khả dĩ hiện tại |
|---|---|---|
| **Parallax 3D không gian / Mesh biến dạng 3D** | **Chưa hỗ trợ**. Renderer hiện đã hỗ trợ hoạt hình phân lớp 2.5D qua `scene.layers`, nhưng chưa hỗ trợ mô phỏng camera 3D không gian thực hoặc biến dạng lưới 3D (Mesh warping). | Sử dụng hoạt hình phân lớp qua `scene.layers` (skill `vp-layered-motion`) hoặc vẽ bố cục phối cảnh 2D có chiều sâu. |
