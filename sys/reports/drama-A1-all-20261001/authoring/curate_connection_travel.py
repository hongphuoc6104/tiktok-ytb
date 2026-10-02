from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
raw=json.loads((P/'narration-attempts/040-051/episodes.json').read_text())['episodes']
items=[
('Chiếc ghế chú giữ lại','Chú giữ một chỗ ngồi cho người tới học; nhân vật tìm Wi-Fi để báo mình đã tới rồi ở lại nghe chú kể về chỗ ngồi ấy.','Chú Ba','Do you have ___?',[ 
'Chú kéo ghế, tưởng tôi sắp đi. "Do you have Wi-Fi?" Chú có mạng không dây không? Tôi chưa gửi được tin báo đã tới lớp, cứ nhìn điện thoại thay vì ngồi xuống.',
'Chú chỉ chỗ ngồi cạnh cửa, bảo hôm nay lớp nghỉ. Tôi tới sớm một ngày. Chú vẫn giữ chiếc ghế, hỏi có muốn ngồi đợi cơn mưa qua không. Tôi cất túi xuống.',
'"The Wi-Fi is free here." Wi-Fi ở đây miễn phí. Tôi nối mạng của quán rồi gửi tin cho bạn. Chú đặt ly nước xuống, bảo ghế này trước kia người bạn của chú hay ngồi.',
'Tôi muốn hỏi lại chú có Wi-Fi không để lần sau khỏi đứng mãi ở cửa. Bạn nói giúp tôi cả câu tiếng Anh nhé.',
'"Do you have Wi-Fi?" Chú gật đầu rồi kể tiếp về người bạn ấy. Tin của tôi đã gửi, nhưng tôi chưa đứng lên. Ngoài cửa vẫn mưa, chú kéo chiếc ghế của mình lại gần.'
],[
'At a quiet small café, mascot stands holding phone beside a chair the older owner has pulled out. Show no cellular network icon guarantees or router repairs.',
'Owner offers the chair by window while mascot sets bag down. Rain outside, only these two people in the café.',
'Owner indicates a generic wireless connection icon on mascot phone; mascot sends one abstract message bubble. The same empty chair remains beside window.',
'Hold mascot ready to ask owner about available Wi-Fi, phone and chair in view. Only supported question stem, no full answer.',
'Mascot sits listening as owner pulls his own chair beside the window chair. Phone is face down; rain remains outside.'
]),
('Lớp học trong căn phòng mới','Em nghĩ phải đi tới trường mới gặp được bạn cũ; buổi học trực tuyến cho em một cách tham gia từ căn phòng vừa chuyển tới.','Em','The class is ___.',[
'Em mang giày, đứng đợi ngoài cửa. "The class is online." Lớp học diễn ra trực tuyến. Tôi chỉ chiếc máy trên bàn, nhưng em vẫn giữ chiếc cặp, chưa muốn ngồi xuống.',
'Hôm qua em vừa chuyển nhà. Em tưởng hôm nay được quay lại lớp cũ, ngồi cạnh người bạn vẫn chia bút cho mình. Tôi kéo chiếc ghế gần bàn, để em tự mở máy.',
'"I have an online class today." Hôm nay em có một buổi học trực tuyến. Em nói khi thấy lớp hiện lên trên mạng. Em đặt chiếc cặp bên cạnh, hỏi ở đây có tới lượt mình đọc không.',
'Em còn hỏi lớp này ở đâu. Bạn giải thích giúp tôi rằng lớp học diễn ra trực tuyến bằng một câu tiếng Anh nhé.',
'"The class is online." Em ngồi xuống, tự mở quyển vở mang từ nhà cũ. Tôi định cất giày giúp, em bảo cứ để đó. Học xong, em muốn ra ngoài xem đường quanh nhà.'
],[
'Home doorway: younger sibling wearing shoes holds schoolbag while mascot points at an open laptop on a nearby desk. No other people displayed clearly.',
'Mascot pulls a chair to the desk while sibling retains the bag. Plain moving box nearby establishes new room.',
'Sibling sits at laptop with generic online classroom tiles made of colored shapes, opens familiar notebook; no faces beyond listed cast or readable names.',
'Hold the same desk and laptop, sibling asking where class takes place. Show supported stem only.',
'Sibling opens the old notebook at laptop, shoes remain nearby and schoolbag beside chair. Mascot waits instead of taking over.'
]),
('Đừng gõ hộ em','Em muốn mở tài khoản để gửi thiệp tự làm nhưng ngại để anh biết mật khẩu; anh nhường bàn phím và chờ ngoài cửa.','Em','I forgot my ___.',[
'Em che bàn phím bằng quyển vở. "I forgot my password." Em quên mật khẩu rồi. Tôi đang định gõ hộ, thấy em né sang một bên thì kéo tay lại.',
'Em muốn vào tài khoản của mình để gửi tấm thiệp đã làm. Nhưng mỗi lần tôi ngồi cạnh, em lại sợ bị hỏi gõ gì. Tôi bảo anh ra ngoài, em tự làm cũng được.',
'"Do not share your password." Đừng chia sẻ mật khẩu của em nhé. Tôi nói rồi đứng dậy. Em tự tìm cách lấy lại quyền vào tài khoản, không đọc hay đưa chuỗi bí mật cho tôi.',
'Nếu quên chuỗi bí mật để vào tài khoản, em cần nói câu nào? Bạn nói giúp em câu em quên mật khẩu rồi bằng tiếng Anh nhé.',
'"I forgot my password." Lúc sau em gọi tôi vào xem thiệp, màn hình đã mở. Tôi chỉ nhìn tấm thiệp. Em kéo ghế cạnh mình, hỏi chữ ký đặt chỗ này có được không.'
],[
'At home desk, younger sibling shields keyboard with notebook as mascot withdraws a hand. Generic locked-account screen, no visible credentials.',
'Sibling keeps control of laptop and plain card design, mascot rises from neighboring chair. No recovery instructions or security procedure shown.',
'Mascot stands outside room doorway while sibling works privately at keyboard. Screen turned away, no password text or readable code.',
'Hold sibling looking at generic locked screen, mascot nearby but not entering credentials. Show target stem only.',
'Sibling invites mascot to view open plain card design after independently regaining account access. No password or recovery detail visible.'
]),
('Tin vẫn chưa gửi','Hai bạn đợi nhau ở hai chỗ; nhân vật nhận ra tin hẹn mình soạn chưa gửi và gọi bạn, rồi thôi giả vờ đang ở gần.','Hải','Please read my ___.',[
'Hải đứng chờ, tôi còn ở nhà. "Please read my message." Đọc tin nhắn của tôi nhé. Tôi nhờ bạn rồi mở máy, mới thấy tin vẫn nằm trong ô soạn.',
'Tôi đã đổi chỗ hẹn nhưng chưa bấm gửi. Hải vẫn ở quán cũ, tưởng tôi sắp tới. Tôi nhìn câu đang viết rằng mình gần tới rồi, xóa đi, nhắn mình còn ở nhà.',
'"You have a new message." Bạn có tin nhắn mới. Hải đọc thông báo rồi gọi lại. Bạn hỏi cần bao lâu. Tôi nói rõ, chờ nghe câu trả lời thay vì vội hứa thêm.',
'Tôi muốn nhờ Hải xem lời hẹn vừa gửi. Bạn nói giúp tôi câu đọc tin nhắn của tôi nhé bằng tiếng Anh.',
'"Please read my message." Hải bảo sẽ chờ ở quán cũ. Khi tôi tới, bạn để chiếc ghế cạnh mình trống. Tôi đặt máy xuống, xin lỗi rồi hỏi bạn đã gọi món gì chưa.'
],[
'Home medium shot: mascot examines phone with an unsent generic draft bubble. Hải is not physically present; only mascot in this shot.',
'Same phone angle: mascot erases an abstract draft block and prepares new message. No readable location, private data or wording.',
'Café shot: Hải sees one incoming message icon on phone and calls mascot, one empty neighboring chair. No other customer or staff.',
'Home shot: mascot holds phone ready to request Hải read the new message. Supported stem only.',
'At the same café table, mascot finally sits on the chair beside Hải. Two plain cups, phones set down, no other people.'
]),
('Tấm ảnh mẹ muốn gửi','Mẹ muốn gửi ảnh chiếc khăn mình đan cho người cháu ở xa; nhân vật giúp mẹ chia sẻ rồi nhường máy để bà viết lời của mình.','Mẹ','Please ___ this photo.',[
'Mẹ giữ điện thoại, chưa chịu đưa. "Please share this photo." Chia sẻ tấm ảnh này nhé. Mẹ muốn gửi ảnh chiếc khăn vừa đan cho cháu, nhưng tôi cứ hỏi bà đưa máy đây.',
'Mẹ sợ tôi gửi luôn mà chưa viết lời bà muốn nói. Tôi ngồi xuống cạnh mẹ, hỏi muốn người nhận thấy điều gì. Bà chỉ phần mép khăn mình đã tháo ra đan lại.',
'"Can I share this photo?" Con chia sẻ tấm ảnh này được không? Tôi hỏi trước khi gửi. Mẹ gật đầu rồi giữ máy, tự viết lời nhắn. Tôi chờ bà viết hết.',
'Mẹ cần nhờ tôi gửi ảnh cho cháu. Bạn nói giúp mẹ câu chia sẻ tấm ảnh này nhé bằng tiếng Anh.',
'"Please share this photo." Ảnh được gửi đi cùng lời mẹ viết. Bà đặt điện thoại xuống, vuốt lại mép khăn. Tôi hỏi mai có chụp thêm không. Bà bảo đợi đan xong phần còn lại.'
],[
'Mother holds phone displaying photo of a handmade scarf while mascot reaches then stops. Real scarf on table; no readable caption.',
'Mother points to corrected edge of real scarf, mascot listens rather than taking phone. Same scarf and table.',
'Close view of phone and mother holding it: photo selected for sharing, empty recipient-message area represented by generic lines. Mascot waits for permission.',
'Hold mother and mascot at table, selected scarf photo still on phone. Supported imperative stem only.',
'Same table: phone shows sent abstract photo thumbnail with message shape; mother smooths real scarf and mascot watches. No readable recipient or private wording.'
]),
('Một trái tim cho bài đầu','Bạn ngại bài hướng dẫn đầu tiên không ai xem; nhân vật làm thử, bấm thích bài và cho bạn thấy phần mình còn làm chưa được.','Duy','Please ___ this post.',[
'Duy định xóa bài vừa đăng. "Please like this post." Bấm thích bài này nhé. Bạn nói nhỏ rồi cất máy, ngại mình phải nhờ cả người quen xem bài đầu tiên.',
'Bài hướng dẫn gấp hộp giấy của Duy. Tôi lấy tờ giấy làm theo, gấp sai ngay mép đầu. Tôi hỏi bước đó một lần nữa. Duy kéo ghế lại, mở bài cho tôi xem chậm.',
'"I will like this post." Tôi sẽ bấm thích bài này. Tôi chạm biểu tượng trái tim dưới bài của Duy. Bạn hỏi hộp đã gấp xong chưa. Tôi đưa chiếc hộp còn lệch nắp ra.',
'Nếu muốn nhờ người khác bấm thích bài mình đăng, bạn nói giúp Duy một câu tiếng Anh nhé.',
'"Please like this post." Duy giữ chiếc hộp tôi làm, chỉ chỗ cần gấp lại. Bạn thôi định xóa bài, lấy thêm giấy để quay rõ bước đó. Tôi giữ máy giúp, lần này không gấp vội.'
],[
'At desk, Duy holds phone with own paper-box tutorial post, mascot beside him. Empty heart icon under post; no names or metrics.',
'Mascot attempts folding one paper box with visibly skewed first edge while Duy reopens same tutorial. No scissors, additional people or text.',
'Same phone close angle: mascot finger poised over empty heart icon beneath tutorial post. Duy keeps skewed paper box at side.',
'Hold Duy requesting appreciation on his tutorial post with mascot and one paper box visible. Stem only, no full answer.',
'Duy unfolds skewed edge to demonstrate correction while mascot holds phone to film this step. No published-success or popularity claim.'
]),
('Đi cùng một lần','Bố luôn khuyên con đi xa nhưng chưa đi cùng; nhân vật xin bố cùng du hành chuyến này và dành chỗ cho túi của ông.','Bố','I want to ___ with you.',[
'Bố đặt túi của tôi sát cửa. "I want to travel with you." Con muốn đi xa cùng bố. Tôi nói vậy, bố cứ tưởng mình đang đùa, bảo cứ đi đi, bố ở nhà được.',
'Bố đã xem hộ tôi đường tới thành phố mới, xếp cả áo mưa vào túi. Tôi hỏi sao bố nhớ từng chỗ mà chưa tới lần nào. Bố nói hồi trước muốn đi, rồi cứ để sau.',
'"We can travel by train." Mình có thể đi bằng tàu hỏa. Tôi mở lịch chuyến cho bố xem, hỏi lần này bố có để sau nữa không. Bố ngồi xuống, nhìn một lúc rồi hỏi cần mang gì.',
'Bố còn nghĩ tôi chỉ rủ cho vui. Bạn nói giúp tôi câu con muốn đi xa cùng bố bằng tiếng Anh nhé.',
'"I want to travel with you." Bố lấy chiếc túi nhỏ của mình ra. Tôi kéo túi tôi sang bên, để hai chiếc cạnh cửa. Bố kiểm áo mưa rồi bảo lần này để bố tự xếp.'
],[
'Home doorway: father places mascot travel bag down, mascot points to both of them inviting father along. No train yet.',
'Father sits beside packed bag with raincoat, mascot listens. No readable itinerary or invented real location.',
'At same table, mascot shows generic train journey pictogram on laptop, father looks then reaches for own plain bag. No readable timetable.',
'Hold father considering invitation, mascot and packed bag in view. Supported travel stem only.',
'Two separate travel bags now side by side near doorway; father places his own raincoat into smaller one, mascot makes space.'
]),
('Khách ở chính quê mình','Nhân vật về làng sau lâu ngày bị hỏi có phải khách du lịch; thay vì giấu chuyện chưa biết ngõ mới, nhân vật nhờ người bạn dẫn xem.','Lan','Are you a ___?',[
'Lan hỏi tôi có phải khách du lịch. "Are you a tourist?" Bạn là khách du lịch à? Tôi đang chụp chiếc cổng làng, vừa quay về sau nhiều năm, không biết ngõ mới đi đâu.',
'Tôi bảo từng sống ở đây. Lan chỉ con đường lát mới, hỏi còn nhớ chỗ giếng cũ không. Tôi định gật đầu, rồi thôi. Tôi hỏi giếng bây giờ còn ở đó không.',
'"I\'m a tourist." Hôm nay tôi là khách du lịch. Tôi nói vậy vì muốn đi tham quan lại nơi mình từng biết. Lan bật cười, bảo thế để bạn dẫn một vòng, đừng giả vờ thuộc đường.',
'Nếu muốn hỏi người đang tới tham quan có phải khách du lịch không, bạn nói giúp Lan câu hỏi bằng tiếng Anh nhé.',
'"Are you a tourist?" Tôi gật đầu. Lan đi cùng tôi tới giếng cũ, đứng chờ tôi chụp xong. Tôi hỏi bạn có chịu đứng vào ảnh không. Lan bảo nhớ gửi lại cho mình một tấm.'
],[
'Village entrance: mascot holds camera facing old gate while local Lan asks his purpose. Plain gate without inscription.',
'Lan points along a newly paved lane, mascot admits unfamiliarity. Same gate remains behind; no crowd.',
'Mascot indicates camera as sightseeing visitor, Lan offers to walk beside him. No official tourism claim or named landmark.',
'Hold visitor mascot with camera and local Lan at lane entrance. Supported tourist question stem only.',
'At a small old village well with solid low wall, mascot photographs Lan standing safely beside it. No leaning into well, other people or lettering.'
]),
('Bản đồ mẹ đã gấp','Mẹ ngại đưa tờ bản đồ mình giữ vì con quen dùng máy; nhân vật mở cùng bà rồi để mẹ chọn lối đi qua chỗ cũ.','Mẹ','Can I see the ___?',[
'Mẹ gấp tờ giấy lại quá nhanh. "Can I see the map?" Con xem bản đồ được không? Tôi đang tìm đường trên điện thoại, chưa nhận ra mẹ cũng mang một tờ bản đồ theo.',
'Mẹ bảo bản đồ này cũ rồi, chắc con chẳng cần. Tôi nhìn nếp giấy đã sờn, hỏi sao mẹ vẫn giữ. Bà chỉ góc có công viên, nói từng dẫn tôi tới đó hồi nhỏ.',
'"The park is on this map." Công viên có trên bản đồ này. Tôi đặt điện thoại xuống, mở tờ giấy cùng mẹ. Lối chúng tôi định đi đã khác, nhưng tên chỗ cũ bà nhớ vẫn còn.',
'Tôi muốn xin mẹ cho xem tờ bản đồ đang cầm. Bạn nói giúp tôi một câu tiếng Anh nhé.',
'"Can I see the map?" Mẹ đưa hẳn tờ giấy, không gấp lại nữa. Tôi hỏi có muốn ghé công viên trước không. Bà giữ một mép bản đồ, kéo tôi đi chậm về phía ấy.'
],[
'At city pedestrian square, mother folds worn paper map while mascot holds phone. No street names yet.',
'Mother unfolds map slightly and points to generic park pictogram. Mascot lowers phone to look at same paper.',
'Fixed close angle of same paper map: mother and mascot hold opposite edges, park pictogram clear. No readable place names or navigational guarantees.',
'Hold mother with same worn map, mascot ready to request a look. Question stem only.',
'Mother and mascot walk slowly along broad pedestrian path, map open between them and simple park entrance visible at distance. No roadway crossing or exact navigation.'
]),
('Chỗ bố ngồi lại','Bố muốn cùng con đi thăm người quen nhưng ngại ô tô cũ sẽ làm con xấu hổ; nhân vật xin đi cùng và giữ thói quen đặt túi của bố.','Bố','Can we take your ___?',[
'Bố cất chìa khóa khi thấy tôi. "Can we take your car?" Mình đi bằng ô tô của bố được không? Tôi hỏi, bố nhìn lớp sơn cũ rồi bảo để con gọi xe khác.',
'Tôi đã hẹn đi thăm người quen với bố. Bố vẫn sợ tôi ngại chiếc xe ông giữ lâu rồi. Tôi mở cửa bên cạnh, thấy chiếc khăn nhỏ bố luôn để chỗ tôi hay ngồi.',
'"This is my father\'s car." Đây là ô tô của bố tôi. Tôi nói khi bạn gọi hỏi mình đi bằng gì. Bố nghe được, quay lại tìm chìa khóa. Tôi cầm túi đồ giúp ông.',
'Bố còn hỏi có chắc muốn đi bằng xe ông không. Bạn nói giúp tôi câu mình đi bằng ô tô của bố được không bằng tiếng Anh nhé.',
'"Can we take your car?" Bố gật đầu, đặt túi xuống phía sau. Tôi ngồi vào chỗ có chiếc khăn, thắt dây rồi hỏi ông đã mang quà chưa. Bố chỉ chiếc túi tôi vừa cầm.'
],[
'Quiet driveway: father pockets car keys beside an older compact car, mascot asks to take it. No visible damage or repair advice.',
'Mascot opens passenger door of stationary car, a small folded cloth on passenger seat; father remains outside.',
'Mascot answers phone beside same stationary car while father retrieves keys. One small gift bag held by mascot.',
'Hold father and mascot beside older parked car, gift bag and keys visible. Supported noun stem only.',
'Stationary car interior: mascot buckles passenger belt, father at driver seat before departure, same gift bag on back seat. No moving-driver distraction.'
]),
('Bố đi tuyến của con','Bố muốn tự đi tới lớp xem con biểu diễn; nhân vật cùng bố nhận ra tuyến xe buýt rồi thôi làm hộ từng bước.','Bố','We can take this ___.',[
'Bố giấu tờ đường đi vào túi. "This bus goes to my school." Xe buýt này đi tới trường con. Tôi chỉ chiếc xe vừa dừng, bố bảo biết rồi nhưng vẫn nhìn tờ giấy.',
'Hôm nay bố muốn tới xem tôi biểu diễn. Tôi thường đón rồi dẫn ông tới tận ghế; lần này bố muốn tự nhớ đường. Tôi đứng bên cạnh, chờ ông đối chiếu tuyến với tờ giấy.',
'"We can take this bus." Mình có thể đi xe buýt này. Tôi xác nhận khi bố chỉ đúng chiếc đang dừng. Bố cất giấy, bước tới cửa. Tôi đi sau, không kéo tay ông như mọi lần.',
'Bố hỏi lại hai người có thể đi xe này không. Bạn nói giúp tôi câu mình có thể đi xe buýt này bằng tiếng Anh nhé.',
'"We can take this bus." Hai bố con ngồi cạnh nhau. Bố hỏi mai nếu tới sớm thì chờ con ở đâu. Tôi bảo chiếc ghế trước cửa lớp, rồi để ông tự ghi vào tờ giấy.'
],[
'Bus shelter: father hides folded route note while mascot points to stationary bus. Door open, driver and other passengers outside framing.',
'Father checks route-note pictogram against same bus route icon, mascot waits. No readable route numbers or real location.',
'Father steps toward stationary bus open door with mascot following. Same folded note now in father pocket, no one else visible.',
'Hold beside open bus door while father asks for confirmation; only supported bus stem visible.',
'Inside stationary bus: father and mascot sit beside each other; father writes a nonreadable note on same paper. No crowds or arrival guarantee.'
]),
('Một chỗ cạnh cửa sổ','Ông đưa cháu tới ga nhưng định về ngay; cháu muốn ông cùng đi chuyến tàu ngắn và giúp ông chọn chỗ mình thích.','Ông','Can we take this ___?',[
'Ông đưa túi rồi quay người đi. "Can we take this train?" Mình đi chuyến tàu này được không? Tôi giữ túi lại, nói lần này đã hỏi ông đi cùng chứ không chỉ nhờ đưa tới ga.',
'Ông bảo ngồi lâu sẽ mỏi, rồi hỏi tàu đi có xa không. Tôi cho ông xem chuyến ngắn đã chọn. Ông nhìn hai tấm vé tôi cầm, hỏi sao không bảo sớm để ông mang thêm áo.',
'"The train is here." Tàu hỏa tới rồi. Tôi chỉ đoàn tàu đang dừng ở ga. Ông lấy áo khoác khỏi túi mình, bảo thế đi thôi, lần này ông muốn ngồi cạnh cửa sổ.',
'Tôi muốn rủ ông cùng đi chuyến tàu trước mặt. Bạn nói giúp tôi câu mình đi chuyến tàu này được không bằng tiếng Anh nhé.',
'"Can we take this train?" Ông gật đầu. Lên toa, tôi để ông ngồi sát cửa sổ, đặt túi xuống cạnh mình. Ông nhìn ra sân ga rồi hỏi lượt về có đổi chỗ cho tôi không.'
],[
'Quiet platform away from track edge: grandfather gives mascot one travel bag and starts to turn, mascot shows two tickets and asks him to come. No readable ticket data.',
'Grandfather looks at two plain tickets while mascot points to generic short-trip diagram. Both remain behind platform safety line.',
'Stationary passenger train at platform, grandfather removes light jacket from own bag as mascot gestures toward open door. No crowd or close track-edge pose.',
'Hold both behind safety line facing stationary train, supported train question stem only.',
'Train carriage: grandfather in window seat, mascot in aisle seat, bags secured beside their feet. No readable outside place names or extra passengers.'
])]
for old,(title,plot,role,stem,narrs,visuals) in zip(raw,items):
 ep={'job':old['job'],'title':title,'plot_vi':plot,'opening_function_vi':narrs[0].split('.')[0],'learner_outcome_vi':'Nhận ra đúng nghĩa đã chọn và dùng một câu ngắn cho nhu cầu của nhân vật.','characters':[old['characters'][0],{'id':'CH02','name_vi':role,'appearance_en':'Minimal ink stick figure with round white navy-outlined head, solid black oval eyes and simple stick limbs. A small plain hair silhouette appropriate to the role.','outfit_en':'Exactly one plain mustard-yellow short-sleeve shirt, no logo or layered torso.'}],'scenes':[],'editorial_review':'Reviewed and rewritten by primary agent; narration frozen before anchors.','visual_review_ready':True}
 for i,(n,v) in enumerate(zip(narrs,visuals)):
  purpose=['Open on immediate personal tension and useful English.','Reveal the human need and resistance through ordinary action.','Make a small consequential choice using the second model.','Invite the same necessary sentence and wait for learner response.','Return the answer and resolve the initial human tension through a concrete gesture.'][i]
  s={'scene_id':f'SC{i+1:02}','title_vi':['Điều xảy ra trước mắt','Điều chưa nói','Lựa chọn','Lời cần đáp','Chuyện tiếp tục'][i],'narration':n,'visual_en':v,'purpose_en':purpose,'character_ids':['CH01','CH02'],'practice_pause_seconds':4 if i==3 else 0}
  if i==3:s['stem']=stem
  if old['job']=='vocab-message-script-285':s['character_ids']=['CH02'] if i==2 else ['CH01'] if i<4 else ['CH01','CH02']
  if old['job']=='vocab-share-script-286' and i==2:s['extra_visual_states']=[{'quote':'Mẹ gật đầu rồi giữ máy,','visual_en':'Same fixed phone close view: mother enters her own nonreadable message beside scarf photo before sharing. Mascot keeps hands back.','purpose_en':'Permission and personal message precede the digital sharing action.'}]
  if old['job']=='vocab-like-script-287' and i==2:s['extra_visual_states']=[{'quote':'Tôi chạm biểu tượng trái tim','visual_en':'Keep exact same phone close view: mascot presses heart under tutorial post; empty heart becomes filled red. No metrics or extra text.','purpose_en':'Show social like as the visible change from unselected to selected heart, not general preference.'}]
  ep['scenes'].append(s)
 if old['job']=='vocab-wifi-script-282':ep['teaching_form']='Wi-Fi'
 (P/'narration-frozen'/f"{ep['job']}.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
 print(ep['job'],sum(len(n.split()) for n in narrs))
