# Cinematography and Shot Grammar for Explainer Videos (9:16)

Quy chuẩn thị giác, ngữ pháp cỡ cảnh và nhịp cắt cho video giải thích 9:16. Đọc trước khi lập beat và viết prompt tạo ảnh.

## 1. Quy trình 3 bước bắt buộc
1. **Phân tích nhịp câu thoại**: Xác định từ khóa cần neo (vocabulary anchor), trọng âm và cảm xúc truyền tải.
2. **Chọn ngữ pháp khung hình & hiệu ứng**: Quyết định cỡ cảnh, góc máy, tiêu điểm mắt và hiệu ứng chuyển cảnh tương thích với renderer.
3. **Viết prompt cho Flow**: Tạo ảnh tĩnh bám sát cỡ cảnh đã chọn, đúng chuẩn người que vô danh (nền sáng, nét đậm, chừa vùng phụ đề).

---

## 2. Bố cục khung dọc 9:16 (1080x1920)
- **Top 30% (Tầng trên)**: Đầu nhân vật, biểu cảm khuôn mặt, bóng thoại, icon cảm xúc/câu hỏi.
- **Middle 40% (Vùng vàng)**: Hành động chính, đạo cụ quan trọng, tương tác. Mắt người xem dừng tại đây nhiều nhất.
- **Bottom 30% (Tầng dưới - Vùng an toàn)**: Dành riêng cho phụ đề động và giao diện ứng dụng. **Cấm** đặt chi tiết trọng tâm hoặc chữ bài học vào vùng này.
- **Lề an toàn**: Giữ lề ngang tối thiểu 80px hai bên mép. Giữ sự liên tục vị trí mắt (eye-trace continuity) giữa 2 cảnh kế tiếp.

---

## 3. Bảng cỡ cảnh chuẩn cho khung dọc 9:16
| Cỡ cảnh / Góc máy | Ý nghĩa & Vị trí trong 9:16 | Ứng dụng thực tế |
|---|---|---|
| **Establishing shot** | Cảnh toàn rộng; xếp lớp bối cảnh theo chiều dọc (đất ở 1/3 dưới, núi/nhà ở giữa, trời ở trên). | Mở đầu cảnh mới, đặt nhân vật vào môi trường. |
| **Medium / OTS** | Trung cảnh hoặc nhìn qua vai đối thoại; nhân vật phía trước ở góc dưới, đối tượng ở 1/2 trên. | Hội thoại, giải thích, tương tác giữa hai nhân vật. |
| **Close-up / Extreme close-up** | Cận cảnh/cực cận; đặt gương mặt/miệng ở tâm 1/3 trên màn hình. | Biểu cảm sốc/vui/buồn, phát âm từ vựng bài học. |
| **POV shot** | Góc nhìn ngôi thứ nhất; vẽ đạo cụ hoặc tay que ở cạnh dưới vươn vào giữa. | Tăng tính nhập vai, hành động cầm nắm trực tiếp. |
| **High / Low / Dutch angle** | Góc cao (nhìn xuống), góc thấp (nhìn lên), hoặc nghiêng đường chân trời 15-25°. | Thể hiện sự nhỏ bé/áp lực (high), khổng lồ (low), hoặc bối rối/kỳ lạ (Dutch). |

---

## 4. Chuyển cảnh & Hiệu ứng tương thích Renderer
Tham khảo chi tiết tham số tại [render-capabilities](../../../../sys/docs/render-capabilities.md).

| Hiệu ứng trong Scene | Cơ chế hoạt động | Áp dụng phù hợp |
|---|---|---|
| `cut` / `hold` | Cắt gắt chuyển ảnh ngay. `hold` cố định không chuyển động. | Match cut, Jump cut, Smash cut, nhịp nhanh hoặc giữ biểu đồ. |
| `fade` | Hòa tan mờ đục (Dissolve) tối đa 0.3s đè lên ảnh trước. | Biến đổi thời gian, hồi tưởng, làm mềm chuyển cảnh. |
| `slide_left` | Trượt ngang ảnh mới từ phải sang trái trong 0.3s. | Lật trang, chuyển ý mới, sang phân đoạn mới. |
| `zoom_in` / `zoom_out` | Tăng dần tỷ lệ scale (1.0 $\to$ 1.08) hoặc thu nhỏ (1.08 $\to$ 1.0). | Push-in (tập trung từ khóa) hoặc Pull-out (hé lộ bối cảnh). |
| `punch_in` | Phóng to giật 1.25x trong 0.35s kèm rung nhẹ. | Nhấn mạnh khoảnh khắc phát hiện bất ngờ, ngạc nhiên. |
| `pan_left` / `pan_right` | Dịch chuyển nhẹ ngang 3% ở scale 1.06. | Quét qua phong cảnh rộng hoặc nhiều chi tiết ngang. |
| Auto Ken Burns | Tự động luân chuyển zoom in $\to$ pan $\to$ zoom out khi không đặt effect. | Chống khung hình chết (Never static frame). |
| `focus: {x, y}` | Tọa độ tâm tiêu cự (mặc định `{x: 0.5, y: 0.42}`). | Hướng chuyển động zoom/pan trúng mặt hoặc đạo cụ chính. |
| `shake` | Rung chấn màn hình 55Hz tắt dần trong 0.28s. | Cú va chạm, giật mình, tiếng nổ hoặc gõ mạnh. |

- **L-cut / J-cut**: Lời thoại chạy liền mạch; đặt mốc beat ảnh (`at`) lệch 0.2s - 0.5s so với đầu câu thoại.
- **Call-out vẽ tay**: Yêu cầu "red hand-drawn circle/arrow" trực tiếp trong prompt theo brand tolerance.
- **Từ vựng nổi bật**: Phụ đề tự highlight màu vàng sáng `#FACC15` cho từ mục tiêu (`target_word`); không vẽ chữ tĩnh đè lên ảnh.
- **Ranh giới renderer**: **Không chọn Parallax 3D đa lớp** vì renderer hiện tại nhận một ảnh bitmap phẳng 2D duy nhất cho mỗi beat (chưa tách lớp). Whip pan được hỗ trợ tự động qua chuyển cảnh `slide_left` có motion blur và gia tốc quán tính.
