---
trigger: always_on
---

# Quy Tắc Dung Sai Nhận Diện Thương Hiệu 80/20 (Brand Tolerance Policy)

Quy định này áp dụng cho toàn bộ quá trình lập kịch bản, tạo hình ảnh (Flow / B-2 Illustrator) và đánh giá chất lượng (Machine Review / Human Review) của Video Pilot.

## 1. Nguyên lý Cốt lõi: Tỷ lệ 80/20
Hệ thống cho phép sai số, **không bắt buộc hình ảnh phải giống 100% kịch bản tuyệt đối hay đồng nhất đến từng milimet pixel**.
- **80% là Nhận diện thương hiệu cốt lõi (Brand Identity)**: Cố định và bắt buộc tuân thủ.
- **20% là Dung sai cho phép (Acceptable Tolerance)**: Cho phép sai lệch ở các chi tiết nhỏ và nét biểu cảm tình huống.

---

## 2. 80% Nhận diện Thương hiệu Cốt lõi (Bắt buộc tuân thủ)
Mọi hình ảnh có sự xuất hiện của nhân vật đại diện kênh (CH01 - Canonical Mascot tại `sys/assets/characters/channel-mascot/reference-v1.png`) phải đảm bảo nhận diện:
1. **Dáng hình cơ bản**: Người que (stickman), đúng **một thân duy nhất**.
2. **Trang phục**: Áo thun cộc tay màu xanh biển nhạt (Light Sky Blue `#8CCFE8`).
3. **Đầu & Khuôn mặt**: Đầu tròn màu trắng với đường viền ngoài màu navy/xanh đen đậm; hai mắt hình oval màu đen đặc tối giản.
4. **Tứ chi**: Hai tay và hai chân dạng đường thẳng que màu navy tối giản.
5. **Phong cách thị giác**: Flat illustration tối giản 2D, màu sắc hài hòa, không gian rõ ràng, chừa khoảng trống cho phụ đề điện thoại.

> **Các lỗi vi phạm 80% thương hiệu (Bắt buộc từ chối):**
> - Mặc áo sai màu (đỏ, vàng, xanh lá, tím...).
> - Vẽ 2 thân áo đè lên nhau hoặc nhiều lớp áo phức tạp.
> - Biến thành người thật, vẽ cơ bắp, ngón tay ngón chân chi tiết như người thật.
> - Mắt hoạt hình kiểu anime/pixar (có tròng trắng to, đồng tử lấp lánh, mí mắt phức tạp).

---

## 3. 20% Dung sai Cho phép (Được chấp nhận — Không được đánh rớt)
Bộ đánh giá chất lượng (Machine Reviewer) và các đạo diễn **tuyệt đối KHÔNG được đánh rớt (`verdict: fail`)** đối với các chi tiết sau:
1. **Nét biểu cảm tình huống**:
   - Lông mày biểu cảm nhẹ (nét cong rũ xuống khi buồn bã, nhíu mày khi tập trung/lo lắng, nét cong cao khi giật mình/ngạc nhiên).
   - Nếp nhăn nhỏ trên trán thể hiện suy nghĩ hoặc hối lỗi.
   - Giọt mồ hôi biểu cảm lo âu, bối rối.
   - Khuôn miệng linh hoạt (cười tươi, mếu máo, hé mở khi nói hoặc nghe).
2. **Biến thiên nét vẽ tứ chi**:
   - Bàn chân hơi bo tròn hoặc bẹt nhẹ khi tiếp đất bước đi.
   - Bàn tay có nét bo tròn nhỏ khi cầm nắm đồ vật (cầm sách, chỉ tay vào bảng, cầm bút).
   - Bàn tay dạng găng/bàn tay hoạt hình màu trắng, giơ ngón cái; bàn chân chỉ có viền (rỗng) thay vì tô đặc.
3. **Chi tiết bối cảnh & Đạo cụ phụ**:
   - Cho phép sai lệch nhẹ về góc kê bàn ghế, kích thước bảng chữ, hoa văn nền so với kịch bản mô tả, miễn là đúng chức năng sư phạm (thể hiện được hành động/nghĩa của từ vựng).

---

## 4. Hướng dẫn Dành cho Bộ Đánh Giá (Review Directives)
- Khi kiểm tra tiêu chí `character_consistency`: Nếu nhân vật thể hiện rõ 80% đặc trưng nhận diện (áo xanh biển nhạt, người que 1 thân, đầu trắng mắt đen), **phải chấm `PASS`**.
- Chi tiết thuộc 20% dung sai được phép khác nhau giữa các khung hình; khác biệt đó không phải lỗi `visual_continuity`.
- Nụ cười lưỡi san hô trong ảnh tham chiếu không bắt buộc; khuôn miệng theo tình huống.
- Ghi chú sửa ảnh (repair note/reject) không được biến chi tiết thuộc 20% dung sai thành điều cấm (ví dụ "tuyệt đối không lông mày").
- Không lặp lại vòng lặp sửa ảnh (`image-repair-loops`) vì các nét biểu cảm tình huống thuộc phạm vi 20% dung sai.
