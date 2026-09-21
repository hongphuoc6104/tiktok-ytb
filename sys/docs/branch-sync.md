# Đồng bộ bố cục ba nhánh — 22/09/2026

Giữ ba lịch sử nhánh riêng, không merge nội dung kênh vào master. Mỗi nhánh nhận cấu trúc sys/ và launcher, chỉ mục, xuất video sau duyệt và bảo vệ scratch giống nhau. File riêng được chuyển vào sys/ nguyên nội dung; cấu hình, mascot và kho dữ liệu riêng không bị thay bằng bản master.

Mốc trước chuyển đổi:
- master: 086161058c4f537fedd45cae8d452c5f3f1b342c
- video-nghien-cuu: 1af7096
- video-vocabulary: 782fa40

Bản dự phòng lịch sử Git nằm local tại sys/maintenance/branch-sync-20260922/before.bundle. Các commit cũ vẫn nằm trong lịch sử nhánh. Muốn tra cứu bản cũ, tạo worktree riêng tại mốc tương ứng; không reset cứng workspace chứa dữ liệu đang chạy.

Video, môi trường, phiên đăng nhập và dữ liệu runtime bị ignore vẫn chỉ ở local. GitHub lưu mã, tài liệu và dữ liệu đã được theo dõi trước đó; không tự đưa runtime lên mạng. Các kiểm tra di chuyển file không thay thế nghiệm thu video hoặc Flow thật.

## Đối chiếu và kiểm thử

Không thiếu file được theo dõi nào sau ánh xạ đường dẫn. Giữ nguyên nội dung và mode của 57 file chỉ có ở nhánh nghiên cứu và 53 file chỉ có ở nhánh từ vựng so với master trước chuyển đổi. Các khác biệt cấu hình và mã kênh được giữ lại.

Master: 167 kiểm thử đạt. Nghiên cứu: bộ 179 kiểm thử có 2 ca thiếu phụ thuộc trong worktree; cả 2 đạt sau nối môi trường Python/Node local. Từ vựng: bộ 167 có cùng 2 ca thiếu phụ thuộc; cả 2 đạt khi kiểm tra lại, thêm 28 kiểm thử kho từ vựng đạt. Không coi đây là nghiệm thu sản xuất media.
