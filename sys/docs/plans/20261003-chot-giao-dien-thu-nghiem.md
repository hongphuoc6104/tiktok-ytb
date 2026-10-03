# Chốt giao diện thử nghiệm Video Pilot

Ngày ghi nhận: 03/10/2026, múi giờ Việt Nam.

**Trạng thái: GIAO DIỆN THỬ NGHIỆM ĐÃ CHỐT — CHƯA TRIỂN KHAI VẬN HÀNH THẬT.**

## Quyết định của người dùng

Nguyên văn:

> “tôi chốt giao diện thử nghiệm tạm thời này sau này nâng cấp thêm sau.”

Đây là quyết định chốt bản giao diện thử nghiệm hiện tại làm mốc cho triển khai và nâng cấp sau. Không tự coi là nghiệm thu chức năng runtime, login, quota, Colab, Flow hoặc sản phẩm video.

## Mốc giao diện

- [Thiết kế 0.3](20261003-thiet-ke-colab-va-auto-thuc-hien.md): máy quản lý/lưu dữ liệu quan trọng; xử lý nặng đưa lên Colab; Flow tạo ảnh trên cloud; Auto thực hiện lập kế hoạch và đi đến đầu ra, không gọi kiểm duyệt.
- [Thiết kế tài khoản 0.4](20261003-thiet-ke-ngan-sach-tai-khoan.md): vòng ngân sách giờ, cửa sổ theo dõi, bộ đếm ảnh, auth và tài khoản active.
- Các mô phỏng được trình bày trong chat là hình thức giao diện đã chốt. Thiết kế 0.1/0.2 là lịch sử, không khôi phục auto kiểm duyệt hoặc render local từ những bản đó.

Tám tab: **Tổng quan & phiên; Tài khoản; Công việc & hàng đợi; Kịch bản & cảnh; Media; Video & thành phẩm; Colab & xử lý; Cấu hình & nhật ký.**

## Phạm vi bản thử nghiệm

Ưu tiên giao diện dễ dùng, liên kết cùng job/cảnh/revision; setup tài khoản lần đầu, chọn preset/tài khoản cho phiên sau; kế hoạch bước, trạng thái và artifact; dừng/tiếp tục; quản lý yêu cầu/prompt và lịch sử; trạng thái xử lý remote; vòng và bộ đếm tài khoản có nguồn dữ liệu rõ.

Khi nối runtime mới phải lấy dữ liệu thật, giữ request/session ownership và phân biệt số minh họa, ngân sách nội bộ, auth và khả dụng thực. Chốt giao diện không tự tạo khả năng chuyển tài khoản vượt quota/bot, không xác nhận quota Google cố định hoặc thay baseline/mode của job đang có.

## Việc tiếp theo

Giữ bố cục này cho bản đầu; các cải tiến trình bày lớn để sau trải nghiệm thực tế. Trước triển khai vẫn thực hiện phần ưu tiên ban đầu: đồng bộ Rules/Skills/quy trình/điểm vào, setup và phân quyền với kiến trúc đã chốt; rồi phát triển kết nối Colab/Flow và trang quản lý.

Lượt ghi nhận này chỉ tạo quyết định và cập nhật mục lục/tài liệu kế hoạch; không sửa runtime/Rules/Skills, chạy job, cấp GPU, kiểm auth live hoặc đổi cấu hình tài khoản.
