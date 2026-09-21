# B-2 Illustrator — khảo sát và quyết định tích hợp

Ngày ghi nhận: 2026-09-21

## Kết luận hiện tại

Đã mở được B-2 Illustrator trong project Flow bằng Chrome profile hiện có. Không có Remix trong More options và chưa xác nhận được bản custom độc lập. Một ảnh thử nghiệm cô lập đã được root gửi theo hạn mức riêng tối đa 1050 credit; không sửa tool Community và không chạy production.

Lần mở URL Flow bằng in-app browser trước đó rơi về trang giới thiệu/`about`; điều này chỉ chứng minh phiên in-app browser đó chưa có quyền truy cập Flow, không kết luận trạng thái đăng nhập của data dir Chrome `video-pilot`.

## Bằng chứng live đã ghi nhận

Ảnh chụp [`experiments/b2_illustrator/results/b2-live.png`](../experiments/b2_illustrator/results/b2-live.png) được root chụp từ Chrome profile `Profile 10` trong project Flow. URL tool đã mở ở dạng `/project/.../tool/community-...`; đây là bằng chứng giao diện thật cho tool Community, không phải bằng chứng preflight production.

Giao diện B-2 hiển thị:

- `Scene input` gồm ô tags gợi ý `Trigger a tag: special, office, night` và ô `Describe the action...`;
- `Style configuration`: `Light mode`, `Dark mode`, `Accent color` (đang là Orange);
- `Character mode`: `Profession` và `Ancient`;
- nút `Generate B-2`;
- vùng preview yêu cầu input scene để bắt đầu minh họa;
- cảnh báo cuối trang rằng tool có thể tiêu credit.

Menu More options chỉ hiện `Pin` và `Report`; không có `Remix`. Tool Builder có một ô `Ask applet agent to make changes`, nhưng chưa có bằng chứng rằng đây là bản sao riêng có thể chỉnh sửa an toàn, và chưa gửi yêu cầu chỉnh sửa.

Các trạng thái chưa được xác nhận từ UI live: 0 credit và charge thực tế, input ảnh nhân vật, input ảnh base scene, batch, download mapping từng ảnh và prompt mở rộng thật sự gửi model. Footer của tool hiển thị `Style Locked B2 Digital Editorial`, `1920x1080`, `Nano Banana Pro`; tuy nhiên artifact thử nghiệm tải về là JPEG 1376×768, nên các giá trị footer chưa đủ làm bằng chứng output contract. Ảnh live và thử nghiệm đều không được dùng làm `flow-preflight`.

Ảnh thử nghiệm cô lập: [`experiments/b2_illustrator/results/b2-001.jpg`](../experiments/b2_illustrator/results/b2-001.jpg), screenshot [`experiments/b2_illustrator/results/b2-attempt-001.png`](../experiments/b2_illustrator/results/b2-attempt-001.png), journal [`experiments/b2_illustrator/results/attempt-001.json`](../experiments/b2_illustrator/results/attempt-001.json). Journal ghi `charged_credits: null`; không suy ra chi phí từ trần 1050.

## Điều đã xác minh từ workspace

`config.json` đặt các điều kiện Flow bắt buộc cho pipeline:

- model: `Nano Banana Pro`
- profile: `video-pilot`
- project: `Video Pilot`
- `credit_budget`: `0`
- `video_generation`: `false`

Đường bảo vệ `scripts/gflow_guard.mjs` chỉ cho phép image, character create hoặc batch; image phải là tỷ lệ `9:16`/`16:9`, một output, và phải lấy bằng chứng từ UI đang mở. `image_pipeline.py` còn yêu cầu:

- ảnh nhân vật đăng ký trước khi dùng cho cảnh;
- ảnh biến thể phải gắn ảnh nền trước thật, theo đúng thứ tự;
- prompt, nhân vật, tỷ lệ và ảnh nền phải khớp journal;
- batch đang tắt mặc định và tài liệu workspace cấm bật trên job production khi chưa kiểm tay với Flow thật.

Các điều kiện này là hợp đồng tích hợp local; chúng không chứng minh B-2 hỗ trợ các khả năng tương ứng.

## Bằng chứng giao diện lịch sử, không phải xác nhận B-2

Các ảnh dưới đây được lưu từ phiên Flow trước ngày khảo sát. Chúng chỉ cho thấy khả năng chung từng thấy trong Flow, không phải bằng chứng hiện tại của tài khoản hay của tool B-2:

- [`scratch/flow_add_ingredients_menu.png`](../scratch/flow_add_ingredients_menu.png): menu Ingredients có tìm kiếm và nhóm Images, Videos, Voices, Characters, Avatars, Uploads; có nút `Add to prompt`.
- [`scratch/flow_char_list.png`](../scratch/flow_char_list.png): khu Characters có `New character`, `Create my avatar` và một character đã đăng ký.
- [`scratch/current_flow_live.png`](../scratch/current_flow_live.png): project `Video Pilot` và pane prompt tạo ảnh người que.
- [`scratch/flow_project_screen.png`](../scratch/flow_project_screen.png): project workspace và thẻ gợi ý `Edit an image`.
- [`.gflow/profiles/video-pilot/current-flow-check.png`](../.gflow/profiles/video-pilot/current-flow-check.png): trang giới thiệu Google Flow, cho thấy profile local không cung cấp phiên Flow đang đăng nhập ở lần kiểm tra đó.

Không dùng các ảnh này để ghi `flow-preflight`, xác nhận account, xác nhận credit, hay suy ra B-2 có batch/remix.

## Ma trận khả năng

| Khả năng cần cho pipeline | Hiện trạng | Bằng chứng cần lấy từ UI thật |
|---|---|---|
| B-2 giữ phong cách minh họa | Có bằng chứng tool có cấu hình style và character mode; chất lượng đầu ra chưa kiểm tra | Tạo ảnh thử chỉ sau khi xác nhận credit và ghi artifact thật |
| Remix/custom prompt | Có input tags/action; More options không có Remix | Cần xác minh Tool Builder có tạo bản sao riêng và lưu được instruction |
| Character reference | Chưa thấy input reference trong B-2 | Cần kiểm tra UI input/asset attachment |
| Base scene / `based_on` | Chưa thấy | Cần kiểm tra attachment và chứng minh ảnh trước được giữ |
| Batch nhiều ảnh | Chưa thấy | Cần kiểm tra output count/batch và thứ tự kết quả |
| Xuất từng ảnh | Chưa thấy | Cần kiểm tra download/asset IDs và ánh xạ kết quả |
| Model/ratio/credit | Footer khai báo `Nano Banana Pro`, 1920×1080; charge và output thực tế chưa khớp/không biết | Cần bắt charge thật, kích thước artifact và mapping download |

## Quyết định và bước tiếp theo

Giữ quyết định ở trạng thái `blocked-by-capability-and-credit-evidence`. B-2 cho kết quả minh họa người que có triển vọng, nhưng artifact thử nghiệm cho thấy mismatch kích thước 1920×1080 được khai báo so với JPEG 1376×768 tải về. Tool chưa đủ hợp đồng đầu vào/đầu ra để cắm vào pipeline. Vì More options không có Remix, ưu tiên tiếp theo là kiểm tra Tool Builder bằng một bản sao riêng nếu UI xác nhận thao tác đó không sửa Community instance.

Các bước tiếp theo:

1. Kiểm tra Tool Builder có tạo bản tùy chỉnh riêng hay chỉ sửa tool Community.
2. Chỉ quan sát các trường input và luồng asset; không gửi generation khi 0 credit chưa được xác nhận.
3. Xác minh character reference, base scene, output count, batch, download và thứ tự bằng cấu hình UI; thiếu bằng chứng thì giữ blocked.
4. Nếu bản tùy chỉnh hỗ trợ các input/đầu ra cần thiết, ưu tiên custom bản riêng. Nếu không, tạo wrapper mới tối thiểu quanh hợp đồng local và ghi rõ tool identity/version cùng prompt mở rộng vào provenance.
5. Chưa bật `flow_batch`, chưa chạy `pilot.py run` và chưa ghi preflight.

## Điều kiện mở khóa production

Chỉ tạo ảnh sau khi người điều phối có bằng chứng UI tươi, trong hạn 10 phút, cho đúng tài khoản/profile/project, mode image, `Nano Banana Pro`, 0 credit và các operation image/character-register. Khi đó mới đi qua `pilot.py flow-preflight JOB --evidence FILE` và luồng production đã được duyệt.
