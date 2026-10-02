from pathlib import Path
import json
p=Path(__file__).parent
# Editorial decisions before packaging frozen narration and anchors.
f=p/'321-330.txt';s=f.read_text().replace('Bạn nói: "Let\'s go to the cinema tonight."','Nhớ lời rủ lúc chiều: "Let\'s go to the cinema tonight."');f.write_text(s)
openings={
262:('Vừa giận dữ, quay đi đã cười? Actor là diễn viên.','"He\'s an actor." Anh ấy là diễn viên. Vừa giận dữ, quay đi đã cười?'),
268:('Đi họp mà mang cả màn hình à? Laptop là máy tính xách tay.','"I\'ll bring my laptop." Tôi sẽ mang máy tính xách tay của mình. Đi họp đâu cần mang cả bàn!'),
273:('Bạn mở đúng thứ để học chưa? App là ứng dụng.','"Open the app." Mở ứng dụng nhé. App là ứng dụng; bạn đã chọn đúng thứ để học chưa?'),
275:('Khoan đóng, bức vẽ chưa lưu! Save trong bài này là lưu tệp.','"Save the file!" Lưu tập tin đã! Save trong bài này là lưu tệp.'),
280:('Trang cứ quay vòng, có phải mình bấm sai? Internet là mạng Internet.','"Is the internet working?" Mạng Internet có hoạt động không? Trang cứ quay vòng, có phải mình bấm sai?'),
283:('Mang giày rồi mới nhớ lớp ở trên mạng! Online nghĩa là trực tuyến.','"The class is online." Lớp học diễn ra trực tuyến. Mang giày rồi mới nhớ lớp ở trên mạng!'),
284:('Đừng đọc mật khẩu cho cả phòng nghe! Password là mật khẩu.','"I forgot my password." Tôi quên mật khẩu rồi. Password là mật khẩu; đừng đọc nó cho cả phòng nghe!'),
289:('Bản đồ mở to, người nhìn vẫn ngơ ngác! Tourist là khách du lịch.','"I\'m a tourist." Tôi là khách du lịch. Bản đồ mở to, người nhìn vẫn ngơ ngác!'),
294:('Vali nặng, mưa còn nặng hơn! Taxi là xe taxi.','"Let\'s take a taxi." Cùng đi taxi nhé. Vali nặng, mưa còn nặng hơn!'),
299:('Vẫn ở ghế cũ vì chuyến bay chưa tới giờ mới! Flight là chuyến bay.','"Our flight is late." Chuyến bay của chúng ta bị trễ. Flight là chuyến bay; thế là phải chờ thêm!'),
302:('Bạn đứng lên rồi, người bạn vẫn lắc đầu! Stop ở đây là điểm dừng xe.','"This isn\'t our stop." Đây chưa phải điểm dừng của chúng ta. Stop ở đây là điểm dừng xe.'),
307:('Có xe rồi, ai lái đây? Drive là lái xe.','"Can you drive?" Bạn có biết lái xe không? Drive là lái xe. Có xe rồi, ai lái đây?'),
309:('Đỗ đây có chắn lối không? Park trong bài này là đỗ xe.','"Can I park here?" Tôi đỗ xe ở đây được không? Park trong bài này là đỗ xe.'),
315:('Vali chưa đóng vì mình muốn ở thêm! Stay ở đây là ở lại, lưu trú.','"Let\'s stay one more night." Cùng ở thêm một đêm nhé. Stay ở đây là ở lại, lưu trú.'),
324:('Ngồi trong nhà mãi, đổi sang chiếc ghế dưới cây nhé? Park ở đây là công viên.','"Let\'s go to the park." Cùng tới công viên nhé. Park ở đây là công viên; đổi sang chiếc ghế dưới cây nào!'),
334:('Trước ghế không có, dưới ghế cũng không! Behind nghĩa là phía sau.','"Your bag is behind the chair." Túi ở phía sau chiếc ghế. Behind nghĩa là phía sau; mình tìm dưới gầm làm gì!'),
340:('Biết tên bảo tàng rồi, tới đó bằng cách nào? Get to nghĩa là đi tới.','"How do I get to the museum?" Tôi tới bảo tàng bằng cách nào? Get to nghĩa là đi tới.')}
for f in p.glob('[0-9]*.txt'):
 s=f.read_text()
 for n,(a,b) in openings.items():
  if a in s:s=s.replace(a,b,1)
 f.write_text(s)
