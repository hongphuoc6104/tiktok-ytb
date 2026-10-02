# 563. safe — Mô hình cần một chỗ không bị va

**Nghĩa/cách dùng trong bài:** an toàn.

**Mục tiêu:** Dùng safe để nói một món được đặt an toàn trong tình huống.

**Diễn tiến:** Mô hình dễ bị va → hỏi chỗ → đặt trong hộp → kiểm.

**Dự kiến:** 60.5 giây · 5 cảnh · Chọn hoặc nhận diện rồi nhận phản hồi.

**Hai câu mẫu chính:**

- Is it safe here?
- The model is safe in this box.

**Trạng thái:** chờ duyệt content revision 1. Mã hồ sơ: `vocab-safe-script-563`.

[Bản duyệt gốc](/home/hongphuoc6104/Desktop/pipelineFlow/sys/runs/vocab-safe-script-563/reviews/content/1/review.md) · [Bản sao hồ sơ](../reviews/563-safe.md)

## SC01 — Nhịp 1

Mô hình vừa làm xong mà mép bàn đã có người đi qua! Safe nghĩa là an toàn. "It is in a good place here." Bạn muốn đặt món giấy ở chỗ được giữ riêng trước khi mang đi.

**Chữ minh họa được phép:** “safe”

**Hình dự kiến:** 1; tập trung quan hệ, vật hoặc hành động của cảnh.

## SC02 — Nhịp 2

Bạn hỏi: "Is it safe here?" Để nó ở đây có an toàn không? "Is this a good place for it?" Người bạn nhìn chỗ đang chọn trong câu chuyện, rồi cùng bạn đưa mô hình vào hộp có phần lót.

**Chữ minh họa được phép:** “Is it safe here?”

**Hình dự kiến:** 1; tập trung quan hệ, vật hoặc hành động của cảnh.

## SC03 — Nhịp 3

Bạn nói: "The model is safe in this box." Mô hình được giữ an toàn trong hộp này. "The sides keep other things away." Hai người kiểm phần lót và chỗ riêng đã chừa cho món giấy trong tình huống.

**Chữ minh họa được phép:** “The model is safe in this box.”

**Hình dự kiến:** 2; cặp hình giữ góc cho thay đổi trước/sau.

## SC04 — Lượt thực hành

Bạn muốn hỏi chỗ đặt mô hình có an toàn theo vai. "Ask about the place." Nói như khi đang chọn chỗ cho một món đồ: "Is it safe here?"

**Chữ minh họa được phép:** “Is it safe here?”

**Hình dự kiến:** 1; tập trung quan hệ, vật hoặc hành động của cảnh.

**Chờ 4 giây cuối cảnh** để người xem trả lời; phản hồi ở cảnh kế tiếp.

## SC05 — Phản hồi và kết quả

"Is it safe here?" Để ở đây an toàn không? "The model now has its own space." Trong câu chuyện, mô hình đã có chỗ giữ riêng, bạn khép hộp sau khi hai người kiểm xong.

**Chữ minh họa được phép:** “Is it safe here?”

**Hình dự kiến:** 1; tập trung quan hệ, vật hoặc hành động của cảnh.

