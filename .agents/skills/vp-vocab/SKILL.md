---
name: vp-vocab
description: Tự động sản xuất video học từ vựng tiếng Anh dọc 9:16 trọn gói từ kho vocab/ theo quy trình chuẩn Video Pilot v3 (Content -> Media -> Video); kích hoạt khi người dùng gõ /vp-vocab, "tạo video từ vựng", "tạo video 9:16", hoặc yêu cầu làm video học tiếng Anh.
---

Đường dẫn vận hành trong skill tính từ `sys/` của dự án; chạy `cd sys` trước các lệnh. Video cho người dùng nằm ở `../video/<tên-video>/`.

# Video Pilot: Sản Xuất Video Từ Vựng Tiếng Anh 9:16 (vp-vocab)

Skill này tự động hóa 100% quy trình sản xuất video dạy từ vựng tiếng Anh dọc 9:16 chất lượng cao từ kho `vocab/` qua đúng 3 giai đoạn chuẩn của Video Pilot v3: **Content ➔ Media ➔ Video**.

---

## 1. Khởi Tạo Job Từ Vựng
Rút từ vựng kế tiếp từ ngân hàng từ vựng:
```bash
python3 vocab/bank.py start <job_name> --mode auto --aspect-ratio 9:16
```
*(Nếu muốn chọn đích danh 1 từ vựng cụ thể: `python3 vocab/bank.py draw <job_name> --word <từ_vựng>` rồi `python3 pilot.py new <job_name> --brief vocab/briefs/<job_name>.json --mode auto`)*.

---

## 2. Giai Đoạn 1: Content (Kịch bản & Ngữ âm)
Lệnh thực thi:
```bash
python3 pilot.py run <job_name> content
```
**Quy tắc bắt buộc khi viết kịch bản:**
1. **Văn phong:** Lời dẫn tự nhiên, gần gũi, mở đầu bằng tình huống đồng cảm (SC01), giải nghĩa từ vựng (SC02), 3 ví dụ đời thường (SC03), và mẫu câu hành động (SC04).
2. **Vieneu TTS & Phiên âm tiếng Anh:**
   - Tuyệt đối KHÔNG viết hoa toàn bộ từ khóa tiếng Anh trong lời dẫn (narration) để tránh TTS đọc đánh vần từng chữ cái. Luôn viết chữ thường hoặc viết hoa chữ cái đầu (ví dụ: `procrastinate` hoặc `Procrastinate`).
   - Đại từ nhân xưng tiếng Anh `I` đứng đơn lẻ trong câu ví dụ PHẢI ghi âm dạng ngữ âm `"Ai"` để giọng đọc phát âm chuẩn bản xứ `/aɪ/`.
3. **Visual Beats (Nhịp thị giác):**
   - $N$ bối cảnh/ví dụ phải có đủ $N$ hình ảnh và $N$ visual beats tương ứng.
   - Điểm neo (anchor quote) của từ khóa/công thức phải đặt thật sớm trong câu để chữ hiển thị trên màn hình tối thiểu từ 2.5 đến 3.5 giây.

---

## 3. Giai Đoạn 2: Media (Giọng Đọc, Mascot Chuẩn & Hình Ảnh 9:16)
Lệnh thực thi:
```bash
python3 pilot.py run <job_name> media
```
**Quy tắc bắt buộc:**
1. **Âm thanh:** Tự động tạo `narration.wav` và phụ đề đồng bộ `subtitles.srt`.
2. **Nhân vật đại diện kênh cố định (Canonical Mascot CH01):**
   - File tham chiếu: `assets/characters/channel-mascot/reference-v1.png` (Media ID: `de94a39b-155f-4afe-acbb-d9d4b59ad532`).
   - Giải phẫu CH01 chuẩn: Đúng 1 thân duy nhất, áo thun cộc tay màu xanh biển nhạt `#8CCFE8`, 2 tay và 2 chân que navy tối giản, đầu tròn trắng viền navy đậm, 2 mắt oval đen đặc, miệng cười tươi lưỡi san hô.
   - Tuyệt đối cấm: vẽ răng, lông mày, lòng trắng hoạt hình, hoặc vẽ 2 thân áo đè lên nhau.
3. **Sinh ảnh qua B-2 Persistent Session Socket:**
   - Kết nối `experiments/b2_illustrator/results/controller/session.sock`.
   - Sinh đầy đủ ảnh 9:16 cho các phân cảnh và visual beats.

---

## 4. Giai Đoạn 3: Video (Dựng Hình Remotion & Thẩm Định Máy)
Lệnh thực thi:
```bash
python3 pilot.py run <job_name> video
```
- Tự động dựng video MP4 độ phân giải dọc 1080×1920 (9:16) bằng Remotion.
- Chạy hệ thống đánh giá máy (Machine Review QA) kiểm tra âm thanh, hình ảnh và tỷ lệ khung hình. Đảm bảo đạt quyết định duyệt hợp lệ.

---

## 5. Đánh Dấu Hoàn Tất
Sau khi render video thành công:
```bash
python3 vocab/bank.py mark <job_name>
```
Báo cáo lại cho người dùng:
1. Đường dẫn video MP4 cuối cùng (nằm tại `runs/<job_name>/revisions/render/1/video.mp4`).
2. Gợi ý Tiêu đề (Title), Caption, Hashtags và Bình luận ghim mẫu để đăng TikTok / YouTube Shorts / Facebook Reels.
