# Kiểm tra dựng video và SSD — 22/09/2026

## Ý nghĩa cấu hình

`render_concurrency` là số tác vụ dựng khung hình song song trong một video, không phải số GPU hay số phiên mã hóa NVENC. Mặc định mới là 4; có thể đặt lại 2 trong config.json. Các bản đầu ra dual vẫn dựng lần lượt. Tăng mức này không bảo đảm tăng tốc.

## Cách đo và giới hạn

Chạy renderer thật với ảnh gradient kiểm tra 1080×1920, hiệu ứng zoom, âm thanh im lặng, video 8 giây/30 fps. Thứ tự 2 → 4 → 4 → 2, mỗi lượt gồm bundle, ảnh kiểm tra và xuất MP4. Đây là thử nghiệm kỹ thuật, không phải sản phẩm hay nghiệm thu chất lượng. Mẫu nhỏ, ảnh dễ nén, có cache; chưa đại diện video dài nhiều ảnh lớn. Thống kê ổ đĩa là toàn máy, có thể gồm ứng dụng khác. Không xóa cache hệ thống.

| Máy | Mức 2 (giây) | Mức 4 (giây) |
| --- | --- | --- |
| Laptop Ryzen 5 6600H, RTX 3050 4 GB, NVMe | 20.03 / 20.03 | 21.03 / 21.03 |
| PC Xeon E3-1240 v3, Quadro P620 2 GB, SATA | 24.03 / 24.03 | 25.03 / 24.03 |

Cả 8 lượt thành công. Mức 4 chạy được nhưng chưa chứng minh nhanh hơn; không suy ra GPU có thể chạy 4 video đồng thời.

## PC SATA

Kết nối SSH qua alias remote-pc-ts. Dự án nằm trên /dev/sda2, ổ WDC WDS250G2B0A-00SM50, link SATA 6.0 Gbps. Ổ phụ SanDisk SDSSDA120G cũng SATA. Máy có khoảng 16 GB RAM, GPU P620 2 GB; ổ dự án còn khoảng 98 GB trống.

Trong bốn lượt render, đo /proc/diskstats mỗi giây: đọc cao nhất 2.16 MB/s; ghi cao nhất 69.55 MB/s; tỷ lệ thời gian ổ bận cao nhất 30.76%; CPU iowait cao nhất 3.16%. Không thấy bão hòa SSD trong mẫu thử.

Sau render, thử đọc/ghi tuần tự trực tiếp bằng file tạm riêng 256 MiB: ghi 247 MB/s, đọc 310 MB/s. File thử đã xóa. Đây là phép đo ngắn, không phải tốc độ duy trì toàn ổ hoặc benchmark ngẫu nhiên; không mặc định ổ thực tế đạt 500 MB/s.

Hai render.log lịch sử ở fluency-habit-04 và vocab-wake-002 chỉ có một byte xuống dòng, không có số đo hiệu năng để so sánh. Không tìm thấy báo cáo benchmark trong các thư mục dự án đã kiểm tra.

## GPU và đường đọc ghi

Quan sát tiến trình thực tế: FFmpeg dùng h264_nvenc và image2pipe, nhận khung hình qua stdin rồi ghi MP4 tạm. Trên laptop, Chrome render có --use-angle=swiftshader-webgl: không thể gọi toàn bộ pipeline là render GPU. Khai báo chromiumOptions.args trong mã không được openBrowser của thư viện hiện cài đọc như một tùy chọn cờ tùy ý; muốn thay backend đồ họa cần kiểm tra riêng.

Remotion có thể truyền buffer trực tiếp sang encoder khi đủ RAM; khi thiếu RAM có thể chuyển đường dựng qua file khung hình. Pipeline còn sao chép ảnh/âm thanh vào public, bundle tài nguyên và sao chép MP4 đầu ra. Bản dual hiện có thể sao chép lại ảnh chung cho từng ngôn ngữ. Các thao tác này có I/O nhưng phép đo hiện tại chưa chứng minh chúng gây nghẽn.

Không có cơ sở chuyển dữ liệu sang RAM disk hoặc thay SSD chỉ từ kết quả này. Nếu video nhiều ảnh lớn vẫn chậm, cần đo mẫu đó với thời gian riêng cho bundle/dựng/mã hóa, RAM/swap và I/O; ưu tiên xác minh backend dựng hình trước khi tăng concurrency thêm.

## Phạm vi thay đổi

Đổi mặc định concurrency từ 2 lên 4 trong config, adapter và renderer; không thay backend GPU hay chất lượng mã hóa. 26 kiểm thử story-v3, 1 kiểm thử chọn đầu ra và kiểm tra cú pháp renderer đạt.

PC đang ở bản cũ 782fa40 trên video-vocabulary, có thay đổi chưa commit. Không pull, checkout hay ghi đè bản làm việc đó; các thử nghiệm PC nằm /tmp/vp-render-check-20260922. Cấu hình PC vẫn là 2. Log đo lưu local tại sys/maintenance/render-check-20260922, không đưa video kiểm tra lên GitHub.
