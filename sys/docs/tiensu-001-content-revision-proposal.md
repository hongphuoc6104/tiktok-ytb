# Đề cương sửa content cho `tiensu-001`

Ngày: 26/09/2026. Đây là tài liệu nghiên cứu và phương án revision, **không phải** brief/content đã lưu hoặc quyết định duyệt. Job hiện tại vẫn là `tiensu-001`.

## Vấn đề của revision 1

Brief R4 yêu cầu sáu chương bằng chứng; content revision 1 chỉ gắn `chapter` cho SC04–SC08, trong đó SC08 kiêm đoạn kết. Chỉ có hai claim (SC05–SC06) cùng trỏ S1. Nhiều câu tả một nhóm người cách đây 50.000 năm như sự thật quan sát được, dù S1 là nghiên cứu một cộng đồng Ju/’hoansi hiện đại. Giữ hình thức nhập vai nhưng phải nói rõ đây là hành trình minh họa ghép từ nhiều loại bằng chứng, không phải nhật ký của một nhóm/địa điểm/ngày có thật.

S1 trong brief hiện ghi “trung bình 15–20 giờ mỗi tuần”. [Chương gốc của Richard B. Lee (1968)](https://faculty.washington.edu/stevehar/lee.pdf) báo khoảng **12–19 giờ mỗi tuần để lấy thức ăn** qua ba tuần mùa đông tại một trại Dobe; số này không tính nấu ăn, đập hạt, lấy nước/củi và việc khác. Không chuyển thành “chỉ làm 2–3 giờ mỗi ngày” hoặc kết luận mọi người thời tiền sử nhàn hơn người hiện đại.

Lời dẫn hiện nói có ca gác đêm. [Nghiên cứu Hadza của Samson và cộng sự (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5524507/) đo thời điểm ngủ lệch nhau; tác giả cho rằng hiện tượng này không cần người được phân làm lính gác. Đây là phép đối chiếu từ cộng đồng hiện đại, không chứng minh lịch gác của nhóm 50.000 năm trước. Cần sửa cả góc kể của brief và lời dẫn; không giữ “phân ca canh gác” như một dữ kiện.

## Sáu chương trong tám cảnh

| Cảnh | Vai trò | Nguồn chính và claim hẹp có thể kiểm tra |
|---|---|---|
| SC01 | Gộp hook “bạn”, phá định kiến và nêu câu hỏi; không gán dữ kiện khảo cổ cụ thể khi chưa có nguồn | Mở câu chuyện, chưa là chương bằng chứng. |
| SC02 | Chương 1: tuổi và việc trong trại | [Froehle và cộng sự (2019)](https://doi.org/10.1002/ajhb.23209) quan sát trẻ Hadza: loại việc trong trại thay đổi theo tuổi và có khác biệt theo giới trong mẫu nghiên cứu. Không suy thành phân vai cố định cho mọi nhóm thời đồ đá. |
| SC03 | Chương 2: di chuyển vì tài nguyên | [Wood và cộng sự (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8060163/) theo GPS 2.078 ngày-người ở 15 trại Hadza; phần lớn các chuyến đi ra khỏi trại nhằm tìm thực phẩm, nước hoặc củi. Không gán giờ giấc hay tuyến nước cụ thể cho 50.000 năm trước. |
| SC04 | Chương 3: lao động kiếm thức ăn | Lee (1968), nguồn S1 hiện có: tại một trại Dobe được quan sát trong ba tuần mùa đông, thời gian trực tiếp lấy thức ăn khoảng 12–19 giờ/tuần; phân biệt rõ với tổng lao động. |
| SC05 | Chương 4: công cụ săn | [Lombard (2005)](https://doi.org/10.1016/j.jhevol.2004.11.006): vết sử dụng/chất kết dính trên mũi đá ở Sibudu (khoảng 50–60 ka) phù hợp với công cụ săn có cán. Không suy kiểu con mồi, giới người săn hoặc một cuộc rượt đuổi cụ thể. |
| SC06 | Chương 5: lửa và thức ăn thực vật | [Larbey và cộng sự (2019)](https://doi.org/10.1016/j.jhevol.2019.03.015): các bếp lửa tại Klasies River (khoảng 120 ka và 65 ka) có mô thực vật chứa tinh bột bị cháy. Không dựng một thực đơn hay nghi lễ bếp lửa thành dữ kiện. |
| SC07 | Chương 6: bề mặt nghỉ/ngủ và giữ ấm | [Sievers và cộng sự (2022)](https://doi.org/10.1016/j.quascirev.2021.107280): lớp cỏ/lác tại Border Cave (khoảng 60–40 ka), thường nằm trên lớp tro, được diễn giải là bề mặt ngủ/làm việc có chuẩn bị. Không khẳng định mục đích lớp tro hay ca canh gác. |
| SC08 | Quay lại hình mở đầu; đối chiếu điều đã biết với điều chưa biết | Có thể nêu kết quả Samson (2017) để tránh ngộ nhận “ai đó phải được phân gác”, nhưng không tạo chương bằng chứng thứ bảy. Kết bằng “Bạn thì… còn họ thì…” với mức chắc chắn đúng nguồn. |

Các nghiên cứu Hadza/Ju/’hoansi là **đối chiếu dân tộc học hiện đại**; Sibudu, Klasies River và Border Cave là **bằng chứng khảo cổ tại những nơi và thời điểm khác nhau**. Không ghép chúng thành lịch trình thực tế của cùng một nhóm người. Từng claim của content phải trỏ đúng `sources[].facts` trong brief revision mới, đúng câu quote đã chốt và `scene.source_ids`.

## Trình tự sửa hợp lệ trên cùng job

1. Chốt bộ nguồn, mốc thời gian và câu claim ngắn; đối chiếu lại bài gốc trước khi dùng. Sau khi người dùng tự nhận baseline mã mới, chạy `reject tiensu-001 content --revision 1` **trước khi** đổi brief; đổi brief trước có thể làm content manifest hiện tại stale và mất đường reject đúng revision.
2. Bổ sung nguồn trong kho chủ đề theo quy trình của kênh, rồi tạo **brief revision qua `pilot.py revise-brief`** với [JSON đề xuất](../scratch/tiensu-001-revision-prep/proposed-brief-v2.json). Không sửa `briefs/1.json` hoặc `integrity.json`. Sửa `draft/content.json` hoặc để adapter viết revision mới qua workflow; giữ đủ 8 cảnh, R1–R5, hình/beat và thời lượng 480–720 giây, đặt sáu `chapter` ở SC02–SC07.
3. Kiểm tra lại claims, coverage, lời dẫn tiếng Việt, hình và nhịp ở revision mới. Chỉ khi đạt mới trình `review.md` mới để người dùng phản hồi duyệt content. Không chạy media trước quyết định đó.
