# Kế hoạch merge Colab đã được người dùng duyệt

## Đích và phạm vi

Đích đề xuất là `video-vocabulary`, nhánh sản xuất hiện tại. GitHub mặc định là `master`, nhưng tài liệu nghiệm thu tại checkout `/home/hongphuoc6104/colab-tts` chỉ định `video-vocabulary`. Không nhập toàn bộ lịch sử kênh từ vựng vào master; `docs/branch-sync.md` yêu cầu giữ riêng nội dung kênh.

Người dùng xác nhận đã chạy kiểm tra, tạo âm thanh Colab thành công và duyệt. Kiểm tra file tại job `vocab-cat-colab-001` thấy quyết định approved=true, actor=machine cho cả content/media/video. Đây là kiểm tra file quyết định, chưa phải kiểm chứng lại sự kiện SQLite hoặc nghe lại toàn bộ artifact trong lượt lập kế hoạch.

## Mốc đối chiếu

- origin/master: 0ed7cd2, lịch sử có 14 commit riêng so với Colab local; Colab có 34 commit riêng. Không suy ra 14 commit đều là tính năng thiếu vì có lịch sử đồng bộ/cherry-pick riêng.
- origin/video-vocabulary và checkout gốc: 9f331d4, thêm 30 kịch bản A1 nhắm 55 giây.
- origin/codex/colab-tts: 7831471.
- codex/colab-tts local: 93d8124, thêm commit bật colab_tts.enabled=true, chưa push.
- Colab local còn thay đổi chưa commit trong hai profile giọng, tài liệu hướng dẫn, báo cáo nghiệm thu và ledger; brief vocab-cat-colab-001 chưa theo dõi.
- Checkout gốc có ledger đã sửa, nhiều brief và báo cáo/agent files chưa theo dõi; có 91 thư mục chứa workflow.json. Chưa kết luận tất cả là job đang chạy.

## Khả năng hợp nhất

Mô phỏng bằng git merge-tree ba cây (Git 2.34.1), không chạm index/working tree:
- video-vocabulary + Colab local: không có dấu xung đột văn bản. Cần xác nhận lại bằng merge thật trong checkout cô lập; mô phỏng không chứng minh đúng ngữ nghĩa/runtime.
- master + Colab local: nhiều vùng xung đột; cùng sửa adapters, workflow, pilot, config, schemas, renderer và Flow.

Master giữ flow_model=Nano Banana Pro, concurrency=1, brief_policies=[]; nhánh từ vựng dùng Nano Banana 2 Lite, concurrency=4, vocab.policy:check cùng các nâng cấp đạo diễn/âm thanh và kho vocab. Không ghi đè master bằng cấu hình kênh từ vựng.

## Các bước thực hiện

1. Chốt phạm vi video-vocabulary theo ngữ cảnh và tài liệu nghiệm thu; nếu người dùng muốn master, lập nhánh port riêng chỉ mang tích hợp Colab cùng phụ thuộc cần thiết.
2. Kiểm kê tiến trình/job đang hoạt động ở cả hai checkout. Sao lưu Git refs và manifest/checksum thay đổi local; không reset, clean, stash hàng loạt hoặc ghi đè ledger. Bảo toàn runtime/DB/phiên trình duyệt và token ngoài Git.
3. Đóng gói thay đổi nghiệm thu có liên quan từ Colab, dựa trên phản hồi thật. Không sửa revision/review/machine report đã lưu. Commit bật Colab 93d8124 phải được mang theo; chỉ merge origin hiện tại sẽ giữ enabled=false.
4. Không chép ledger thử nghiệm đè ledger sản xuất. Đối chiếu mục cat.n, job xuất video và quyết định hợp lệ qua CLI trước khi quyết định chuyển trạng thái kho. Giữ brief thử nghiệm cùng bằng chứng trong checkout nguồn để tra cứu.
5. Tạo checkout merge riêng trên origin/video-vocabulary mới nhất, merge --no-ff Colab đã chốt. Giữ toàn bộ commit 9f331d4 và 30 kịch bản; không chép thư mục nguồn đè đích. Rà soát diff cuối chỉ còn phạm vi Colab/nghiệm thu và cập nhật có chủ đích.
6. Chạy kiểm thử tài khoản, TTS, worker, workflow, integrity; kiểm tra cấu hình enabled, song song, giọng/tốc độ, bảo vệ token, CLI doctor và hồ sơ tài khoản thực tế. Kiểm thử đầy đủ thêm các phần bị ảnh hưởng; không yêu cầu tái sinh video đã duyệt nếu không có thay đổi chức năng liên quan.
7. Kiểm kê integrity của job sản xuất trước rollout. Code mới thay baseline của job cũ, kể cả thay nội dung profile giọng đã được bảo vệ. Không tự adopt-code/lift-cap, không tạo job thay thế để né. Có thể merge mã vào remote trước, giữ checkout sản xuất cũ cho job dang dở tới khi người dùng quyết định chuyển.
8. Sau kiểm tra đạt: push commit nguồn cần thiết và merge commit lên video-vocabulary, xác nhận SHA remote. Chỉ cập nhật checkout gốc khi đã xử lý công việc đang chạy và dữ liệu chưa commit. Không force-push.

## Hoàn tác

Giữ SHA đích trước merge và merge commit. Nếu đã push, dùng revert merge trên nhánh đích rồi kiểm tra; không reset --hard hoặc force-push. Revert mã không hoàn tác quyết định/job/artifact/ledger. Giữ nguyên lịch sử runtime và áp dụng quy trình integrity cho từng job.

## Trạng thái lượt này

Đã khảo sát và lập kế hoạch. Chưa commit thay đổi nghiệm thu, chưa merge, chưa push, chưa sửa cấu hình hoặc dữ liệu sản xuất.
