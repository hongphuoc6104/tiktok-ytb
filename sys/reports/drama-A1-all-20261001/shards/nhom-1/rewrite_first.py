import json,pathlib
P=pathlib.Path('/home/hongphuoc6104/Desktop/pipelineFlow/sys/reports/drama-A1-all-20261001');O=P/'shards/nhom-1'
A='Minimal ink stick figure, round white head outlined dark navy, solid black oval eyes, minimal stick limbs, exactly one torso.'
data=[
('taxi','Chỗ khô cho hộp bánh','Mẹ','brown', 'Tôi đón mẹ dưới mưa nhưng bà tiếc tiền taxi; chiếc hộp bánh bà mang cho tôi quyết định chuyến đi.', 'Let’s take a taxi.','Let’s take a ___.',[
'Áo mẹ ướt hết một bên vai. Tôi vừa tới ga đón mẹ, đã thấy bà ôm hộp bánh vào ngực. "Let’s take a taxi." Tôi rủ mẹ đi taxi, nhưng bà lắc đầu, bảo nhà đâu có xa.',
'Tôi nhìn đôi dép mẹ đang đi. Quai dép đã sắp đứt, bà vẫn bảo đi bộ được. Mẹ nghiêng hộp bánh về phía tôi, hỏi ở nhà còn thích ăn loại này không. Tôi gật đầu.',
'Tôi gọi xe rồi cất điện thoại. "The taxi is here." Xe taxi tới rồi. Mẹ chưa chịu bước ra khỏi mái che. Tôi bảo hộp bánh mà ướt thì con tiếc lắm. Bà mới chịu đứng lên.',
'Mẹ vẫn hỏi có cần đi xe thật không. Bạn nói giúp tôi lời rủ cùng đi taxi bằng tiếng Anh nhé.',
'"Let’s take a taxi." Mẹ ngồi vào xe, đặt hộp bánh giữa hai người. Bà mở hé nắp cho tôi nhìn. Tôi lấy một chiếc bánh, còn mẹ cuối cùng cũng thả lỏng đôi vai.'],[
'Mascot meets his mother under station awning in rain. Mother wears one brown shirt, hugs one closed cake box. Her left shoulder is wet.',
'Same awning and box. Close view of mother’s worn sandal strap and mascot noticing it; mother gently offers the box.',
'Same awning, a taxi stopped at curb. Mascot points to the car; mother remains seated holding the single box.',
'Hold both under awning, stationary taxi beside curb, mother unsure and mascot gesturing toward its open rear door.',
'Two people seated in stationary taxi back seat, cake box between them. Mascot takes one small cake as mother relaxes.']),
('motorbike','Chiếc xe bố vẫn giữ','Bố','gray','Tôi ngại chiếc xe máy cũ của bố nhưng nhận ra bố vẫn dùng nó để đưa mình đi học.', 'This motorbike is old.','This ___ is old.',[
'Bố lau yên xe bằng khăn cũ. "This motorbike is old." Chiếc xe máy này cũ rồi. Tôi nói vậy rồi nhìn sang chiếc xe mới nhà bên, chẳng muốn ngồi lên yên sau của bố.',
'Bố không nói gì, chỉ buộc lại túi áo mưa. Trên tay lái vẫn treo chiếc móc tôi tặng hồi nhỏ. Tôi tưởng bố đã bỏ nó từ lâu. Bố kéo túi xuống để tôi nhìn rõ hơn.',
'Bố hỏi hôm nay tôi có cần bố đưa tới lớp không. Tôi cầm mũ bảo hiểm rồi đáp: "I like this motorbike." Tôi thích chiếc xe máy này. Bố quay lại nhìn, tưởng mình nghe nhầm.',
'Bố còn đợi câu trả lời. Bạn nói giúp tôi rằng tôi thích chiếc xe máy này bằng tiếng Anh nhé.',
'"I like this motorbike." Bố đưa tôi chiếc mũ. Tôi ngồi lên yên sau, giữ túi giúp bố. Trước khi đi, bố lau lại chỗ tôi ngồi thêm một lần nữa.'],[
'Father wipes old parked motorbike seat in home courtyard. Mascot stands beside it looking hesitant. Both single shirts.',
'Close view of father tying raincoat pouch to parked bike; a small plain charm hangs on handlebar, mascot notices it.',
'Same parked bike, mascot holding helmet with slight smile while father turns his head toward him.',
'Hold father and mascot beside stationary motorbike and helmet, invite spoken response without riding action.',
'Mascot seated behind father on parked motorbike, both helmets secured, mascot holds small bag as father finishes wiping rear seat.']),
('bicycle','Hai tay bố buông ra','Bố','gray','Tôi tập xe đạp, sợ bố buông tay rồi nhận ra mình đã tự đi được một đoạn.', 'This is my bicycle.','I ride my ___.',[
'Bố đang giữ yên xe sau lưng. "This is my bicycle." Đây là xe đạp của tôi. Tôi mới có nó hôm qua, còn hôm nay cứ đạp được vài vòng là lại chống chân xuống.',
'Tôi dặn bố đừng buông tay. Bố đáp biết rồi, cứ nhìn phía trước. Tôi đạp chậm trên sân phẳng, nghe bố nói sau lưng. Lần này tôi chưa dừng lại ở vạch gạch quen thuộc.',
'Tôi ngoái lại, bố đã đứng cách mấy bước. Hai tay bố không chạm vào xe nữa. "I ride my bicycle." Tôi tự đi xe đạp rồi. Bố vẫy tay, còn tôi vội nhìn lại phía trước.',
'Bố hỏi con đang tự đi bằng gì đấy. Bạn nói giúp tôi câu tôi đi xe đạp của mình bằng tiếng Anh nhé.',
'"I ride my bicycle." Tôi dừng xe rồi quay lại chỗ bố. Bố hỏi có sợ không. Tôi bảo có, nhưng vẫn muốn thử thêm một vòng, lần này bố chỉ đứng nhìn.'],[
'Closed flat courtyard, father holds seat of small pedal bicycle as mascot sits with both feet down; both wear helmets.',
'Same courtyard side view, mascot pedaling slowly while father keeps one hand on rear saddle.',
'Same camera, mascot pedaling ahead, father visibly several steps behind with both hands released. Clear pedals and two wheels.',
'Hold side view of mascot controlling bicycle and father behind, stable empty courtyard with no traffic.',
'Mascot stopped with feet planted and turns toward father. Father hands held clear of bike, ready to watch another attempt.']),
('boat','Chuyến qua sông của bà','Bà','brown','Bà sợ thuyền chòng chành; tôi đi cùng và giữ giỏ cho bà sang thăm bạn.', 'The boat is here.','The ___ is here.',[
'Bà đứng lùi khỏi mép bến. "The boat is here." Thuyền tới rồi. Tôi gọi bà, nhưng bà vẫn giữ chặt giỏ cam. Bà muốn sang thăm bạn bên kia sông, lại sợ bước xuống chiếc thuyền nhỏ.',
'Tôi đi xuống trước, ngồi yên rồi đưa tay đón giỏ. Bà hỏi nó có chòng chành không. Tôi bảo bà cứ đợi thuyền buộc xong. Bà nhìn tôi, rồi nhìn chiếc giỏ đang nằm cạnh chân tôi.',
'Bà bước xuống, vẫn nắm tay tôi. "We are on the boat." Hai bà cháu đã ở trên thuyền. Bà ngồi xuống cạnh giỏ cam và bảo tôi đừng cười vì bà sợ nhé.',
'Bà còn ngó về phía bến. Bạn báo giúp bà câu thuyền tới rồi bằng tiếng Anh nhé.',
'"The boat is here." Tôi nói lại câu lúc nãy, lần này bà bật cười. Qua tới bờ bên kia, bà đứng dậy lấy giỏ. Bà bảo lượt về cũng nhờ tôi giữ hộ.'],[
'Docked wooden boat tied at sheltered river landing, grandmother in brown holds orange basket away from edge; mascot points to boat.',
'Mascot seated inside securely moored boat wearing life jacket, grandmother waits on landing, basket placed next to his feet.',
'Both seated in moored wooden boat with life jackets, grandmother holds mascot hand, orange basket at feet; no other people.',
'Hold both seated, boat secured to landing, grandmother looks toward shore and mascot reassures with open palm.',
'Same two people at opposite dock beside stationary moored boat, grandmother lifts orange basket and smiles at mascot.']),
('plane','Chiếc máy bay của em','Em','yellow','Em vẽ máy bay không được; tôi đưa em đi nhìn một chiếc thật để sửa bức vẽ.', 'I see a plane.','I see a ___.',[
'Em gạch bỏ đôi cánh lần nữa. Em đang vẽ máy bay cho bài ở lớp, nhưng cứ bảo hình mình giống con cá. Tôi rủ em ra chỗ ngắm máy bay ngoài sân bay, mang theo tờ giấy ấy.',
'Em chỉ lên trước cả tôi. "I see a plane." Em nhìn thấy một chiếc máy bay. Nó đi chậm ở xa phía sau hàng rào. Em cúi xuống tờ giấy, cuối cùng cũng biết cánh nằm ở đâu.',
'Một chiếc khác đỗ gần hơn, em đứng nhìn rất lâu. "The plane is big." Chiếc máy bay to thật. Em vẽ thêm hai cánh rộng, lần này không gạch đi. Tôi giữ mép giấy khỏi bị gió lật.',
'Em muốn kể mình nhìn thấy một chiếc máy bay. Bạn nói giúp em cả câu tiếng Anh nhé.',
'"I see a plane." Em viết câu ấy dưới hình. Trên đường về, em ôm tờ giấy trước ngực. Tôi hỏi còn giống cá không. Em bảo có một chút, nhưng cá của em có cánh rồi.'],[
'Mascot and child in yellow beside drawing table, child erases wing on rough non-readable aircraft sketch.',
'Both outside airport perimeter viewing fence, small real aircraft taxiing beyond fence, child points while holding sketch.',
'Same public viewing area, larger stationary aircraft beyond fence. Child adds wide wings to sketch as mascot holds paper edge.',
'Hold pair looking through public viewing fence toward aircraft, child holds corrected sketch, no runway access.',
'Child hugs paper showing plane drawing and exact authorized sentence while mascot walks beside child outside viewing area.']),
('flight','Chuyến bay còn phải đợi','Bạn','green','Chuyến bay trễ làm tôi lỡ bữa cơm với bạn; tôi gọi báo thay vì giấu sự thất vọng.', 'Our flight is late.','Our ___ is late.',[
'Bạn đã hâm cơm lần thứ hai. Tôi nhìn tin nhắn rồi nhìn bảng báo giờ ở sân bay. "Our flight is late." Chuyến bay của chúng tôi bị trễ. Bữa cơm bạn nấu chắc phải chờ thêm một lúc.',
'Tôi nhắn bảo bạn cứ ăn trước. Bạn gửi lại ảnh hai cái bát, nói không sao, món canh còn nóng. Người đi cùng hỏi tôi sao cứ nhìn điện thoại mãi. Tôi đưa ảnh cho bạn ấy xem.',
'Bạn ấy kéo ghế sát lại: "What time is our flight?" Chuyến bay của chúng ta lúc mấy giờ? Tôi kiểm tra giờ mới rồi gọi cho người đang chờ, lần này nói rõ còn phải đợi bao lâu.',
'Bạn ở nhà chưa nghe rõ lý do. Bạn nói giúp tôi rằng chuyến bay của chúng tôi bị trễ bằng tiếng Anh nhé.',
'"Our flight is late." Tôi nói lại, đầu dây bên kia bảo cứ tới đã rồi tính. Tôi cất điện thoại. Người đi cùng đưa tôi phần bánh còn lại, bảo ăn một chút cho đỡ đói.'],[
'Mascot seated with green-shirt travel companion in airport waiting area, phone shows simple image of two bowls; departure status datum authorized separately.',
'Same airport chairs, mascot shows phone image of two bowls to companion. No remote person depicted.',
'Same chairs, companion leans closer as mascot checks updated departure time and holds phone to ear; essential delay data only.',
'Hold seated mascot on phone beside companion, departure display with exact allowed datum, no aircraft need be visible.',
'Companion offers part of small bread roll to mascot in same airport seats, phone put away; they continue waiting together.']),
('airport','Ai cũng từng đi lần đầu','Bạn','green','Tôi lần đầu tới sân bay, giấu việc chưa biết lối; bạn quay lại đi cùng.', 'This is the airport.','This is the ___.',[
'Tôi kéo vali nhầm về phía cửa ra. "This is the airport." Đây là sân bay. Bạn nói khi chúng tôi vừa xuống xe, nhưng tôi chỉ gật đầu, không thú nhận đây là lần đầu mình tới đây.',
'Bạn đi được mấy bước rồi quay lại. Tôi vẫn đứng ở cửa, tay giữ chặt quai túi. Bạn hỏi tìm gì. Tôi bảo tìm quầy làm thủ tục, rồi thú nhận mình chẳng biết bắt đầu từ đâu.',
'Bạn chỉ về phía sảnh đón các chuyến bay: "The airport is big." Sân bay rộng thật. Bạn cầm giúp chiếc túi nhỏ và bảo cứ đi cùng nhau. Tôi thôi giả vờ biết lối, mở vé ra hỏi tiếp.',
'Tôi muốn gọi đúng nơi hai người đang đứng. Bạn nói giúp tôi câu đây là sân bay bằng tiếng Anh nhé.',
'"This is the airport." Tôi nhắc lại, lần này nhìn quanh được lâu hơn. Tới quầy, bạn đặt túi xuống cạnh tôi. Tôi tự đưa giấy tờ ra, còn bạn đứng bên chờ.'],[
'Public airport entrance, mascot pulling small suitcase hesitates at exit-side door while green-shirt friend points toward glass terminal; distant parked aircraft.',
'Same doorway, friend returns to mascot who clutches bag strap, both face one another, suitcase stationary.',
'Wide airport check-in hall, both enter together, friend carries mascot small bag, mascot looks at ticket.',
'Hold two friends in terminal with check-in desks and aircraft visible through glass, no extra people.',
'Mascot at check-in desk places document folder forward, friend beside him sets small bag down; no clerk depicted.']),
('station','Ga tàu trong bức ảnh cũ','Bố','gray','Tôi đưa bố quay lại ga cũ, ông nhận ra chiếc ghế chờ từng tiễn con đi xa.', 'This is the station.','This is the ___.',[
'Bố dừng trước chiếc ghế gỗ cũ. "This is the station." Đây là nhà ga. Tôi vừa đưa bố tới ga tàu trong bức ảnh ông giữ, nhưng bố nhìn quanh mãi, chưa nhận ra chỗ mình từng đứng.',
'Tôi mở bức ảnh trên điện thoại cho bố xem. Trong ảnh chỉ có mái che và chiếc ghế ấy. Bố bảo hồi tiễn tôi đi học, bố ngồi đây đợi tàu khuất rồi mới chịu về.',
'Tôi ngồi xuống cạnh bố: "We wait at the station." Hai bố con chờ ở nhà ga. Lần này chẳng ai phải đi đâu. Bố đặt túi xuống, nghe tiếng tàu tới rồi kể tiếp chuyện hồi đó.',
'Bố muốn gửi cho mẹ lời báo đây là nhà ga. Bạn nói giúp bố cả câu tiếng Anh nhé.',
'"This is the station." Tôi quay điện thoại về phía ghế gỗ, chụp thêm một tấm. Bố bảo nhớ chụp cả tôi. Trong bức ảnh mới, chỗ ngồi bên cạnh bố không còn trống.'],[
'Mascot and gray-shirt father at old train station wooden bench under roof, passenger train tracks visible beyond safe platform.',
'Mascot shows phone photo of same empty bench and awning to father; no person in old photo.',
'Both seated at same bench with bag on ground, passenger train in background, father gestures while telling story.',
'Hold two people beside same station bench and tracks, mascot holds phone ready for place message.',
'Both seated close at bench, mascot extends phone to frame them together; same roof and track background.']),
('stop','Một điểm dừng sớm hơn','Bạn','green','Tôi quên xuống điểm hẹn; bạn đi bộ sang đón, biến lời trách thành chuyện ngồi nghỉ cùng nhau.', 'This is my stop.','This is my ___.',[
'Tôi nhìn thấy bạn qua cửa kính. "This is my stop." Đây là điểm dừng tôi cần xuống. Tôi đứng dậy muộn quá, cửa xe buýt đã đóng. Bạn ở ngoài vẫn vẫy tay, chưa biết tôi còn trên xe.',
'Tôi xuống ở điểm tiếp theo rồi gọi lại. Tôi tưởng bạn sẽ bực vì phải chờ. Bạn chỉ hỏi tôi đang đứng dưới mái che nào. Tôi gửi ảnh chiếc ghế trống, ngồi xuống với túi quà trên đùi.',
'Mấy phút sau, bạn đi tới: "The stop is near my house." Điểm dừng này gần nhà bạn. Bạn bảo đáng ra hẹn tôi ở đây cho tiện, rồi ngồi xuống chỗ trống bên cạnh.',
'Lần sau tôi phải báo sớm cho người đi cùng. Bạn nói giúp tôi câu đây là điểm dừng tôi cần xuống bằng tiếng Anh nhé.',
'"This is my stop." Tôi nói lại rồi đưa túi quà cho bạn. Bạn mở ra ngay trên ghế, hỏi sao tôi ôm kỹ thế. Tôi bảo quà tới trễ một điểm dừng thôi.'],[
'Mascot inside stationary closed-door blue bus sees green-shirt friend waving outside designated stop, gift bag on lap.',
'Mascot seated alone under next bus stop shelter holding gift bag and phone, empty adjacent seat, blue bus absent.',
'Same next stop shelter, friend arrives on foot and sits next to mascot, small houses behind shelter.',
'Hold same pair seated at stop, mascot gestures toward stop pole; same gift bag and simple shelter.',
'Same bench, mascot hands gift bag to friend who opens top while both smile modestly.']),
('ticket','Tấm vé bố không mua','Bố','gray','Tôi tưởng bố không muốn xem buổi diễn của mình; bố chỉ tiếc mua vé cho bản thân, tôi đã giữ cho ông một tấm.', 'I have a ticket.','I have a ___.',[
'Bố đứng chờ ngoài cửa khán phòng. "I have a ticket." Tôi có một tấm vé. Tôi đưa vé cho bố, nhưng bố bảo cứ để người khác xem, bố đứng ngoài nghe cũng được.',
'Tôi tưởng bố không thích buổi diễn đầu tiên của mình. Bố nhìn đôi giày sân khấu tôi đang cầm, hỏi có đau chân không. Tôi lắc đầu. Bố bảo vé chắc đắt, con giữ lại mà dùng.',
'Tôi đặt tấm vé vào tay bố. "This ticket is for you." Vé này dành cho bố. Tôi đã giữ nó từ hôm đăng ký buổi diễn. Bố nhìn lại tôi rồi cất vé vào túi áo.',
'Bố ngập ngừng trước cửa soát vé. Bạn nói giúp bố câu tôi có một tấm vé bằng tiếng Anh nhé.',
'"I have a ticket." Bố đưa vé ra rồi bước vào. Tôi chờ ở cánh gà, nhìn bố chọn ghế phía trước. Bố đặt hai tay lên đầu gối, ngồi thẳng hơn lúc ở nhà.'],[
'Mascot outside small auditorium entrance holding stage shoes and one admission ticket, gray-shirt father hesitates at doorway.',
'Same entrance, father glances at mascot shoes while mascot lowers gaze; ticket remains in mascot hand.',
'Close view of mascot placing single ticket into father hand, both figures visible in same doorway.',
'Hold father presenting ticket toward empty entrance counter, mascot beside him; no unlisted clerk.',
'Father seated in front row of small auditorium, mascot visible waiting beside stage curtain holding stage shoes.'])]
for stem,title,person,color,plot,answer,gap,n,v in data:
 job=f'vocab-{stem}-script-'+str(294+[d[0] for d in data].index(stem))
 e={'job':job,'title':title,'plot_vi':plot,'opening_function_vi':'Một chi tiết cụ thể làm lộ điều nhân vật muốn và vướng mắc nhỏ.','learner_outcome_vi':'Nói một câu đúng nghĩa từ trong tình huống của câu chuyện.','characters':[{'id':'CH01','name_vi':'Tôi','appearance_en':A,'outfit_en':'Exactly one pale-blue short-sleeve shirt (#8CCFE8).'}, {'id':'CH02','name_vi':person,'appearance_en':A,'outfit_en':f'Exactly one plain {color} short-sleeve shirt.'}],'scenes':[],'editorial_review':'Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.','visual_review_ready':True}
 for i,(narr,vis) in enumerate(zip(n,v),1):
  s={'scene_id':f'SC{i:02}','title_vi':['Điều chưa nói','Vướng mắc','Quyết định','Lời cần nói','Chuyện tiếp tục'][i-1],'narration':narr,'purpose_en':['Show immediate personal need.','Make resistance and selected sense concrete.','Use second English model for a consequential small action.','Retrieve one full story-linked model before answer.','Give answer and earned physical payoff.'][i-1],'visual_en':vis,'character_ids':['CH01','CH02'],'practice_pause_seconds':4 if i==4 else 0}
  if i==4:s['stem']=gap
  if stem=='stop' and i==2:s['character_ids']=['CH01']
  if stem=='flight' and i in [1,3,4]:s['custom_visible_text']=[{'text':'Delayed','placement':'Departure information area above seats','object':'Airport departure display'}]
  if stem=='plane' and i==5:s['custom_visible_text']=[{'text':'I see a plane.','placement':'Below aircraft drawing on held sheet','object':'Child drawing paper'}]
  e['scenes'].append(s)
 # standard apostrophes ensure plain exact retrieval
 for s in e['scenes']:
  s['narration']=s['narration'].replace('Let’s',"Let's")
  if 'stem' in s:s['stem']=s['stem'].replace('Let’s',"Let's")
 f=P/'narration-frozen'/f'{job}.json';t=f.with_suffix('.tmp');t.write_text(json.dumps(e,ensure_ascii=False,indent=2));t.replace(f)
 print(job,sum(len(s['narration'].split()) for s in e['scenes']))
