from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/drama-A1-all-20261001';raw=json.loads((OUT/'narration-attempts/016-027/episodes.json').read_text())['episodes']
updates=[
('Chuyến xe chờ bánh','Một đơn bánh chưa có người chở; tài xế quay lại giúp người thợ già bưng khay và cả hai thôi vội.','He is a careful ___.',[
'Bánh nguội dần, xe vẫn chưa tới. "I need a driver." Tôi cần một tài xế. Bác Năm nhìn khay bánh, hỏi tôi có nên gọi thêm lần nữa không.',
'Bác nhận đơn này vì các em nhỏ ở lớp tối đã hẹn đợi. Mưa từ sáng, người chở hàng quen lại xin nghỉ. Tôi kéo khay bánh vào trong hiên, gọi một người khác.',
'Xe đỗ trước cửa. Bác tài kê lại từng khay, không chồng lên nhau. "He is a careful driver." Bác ấy là tài xế cẩn thận. Bác Năm cuối cùng cũng ngồi xuống.',
'Nếu muốn nói bác ấy là một tài xế cẩn thận, bạn nói giúp tôi cả câu bằng tiếng Anh nhé.',
'"He is a careful driver." Đúng rồi. Bác tài giữ cửa để bác Năm đưa khay cuối lên. Xe đi rồi, bác hỏi tôi ăn bánh chưa. Bác vẫn chừa lại hai chiếc.']),
('Túi đỏ bên ghế đá','Bo mất túi đồ chơi ở công viên; nhân vật giúp cháu tìm cảnh sát và lấy lại túi mà không phải cố tỏ ra không sợ.','She is a kind ___.',[
'Bo nắm tay tôi, chiếc túi không còn. "Look for a police officer." Tìm một cảnh sát nhé. Tôi đưa Bo quay lại ghế đá, chậm hơn lúc đi vào.',
'Trong túi chỉ có món đồ chơi Bo mang từ nhà. Thằng bé cứ nói không sao, rồi lại nhìn xuống tay mình. Tôi bảo mình cùng hỏi người ở cổng, chưa cần bỏ cuộc.',
'Cô cảnh sát cúi xuống nghe Bo nói. "She is a kind police officer." Cô ấy là cảnh sát tốt bụng. Cô chỉ chiếc túi đỏ có người vừa mang tới bàn trực.',
'Nếu muốn giới thiệu cô ấy là một cảnh sát tốt bụng, bạn sẽ nói câu nào bằng tiếng Anh?',
'"She is a kind police officer." Đúng rồi. Bo nhận túi, lấy món đồ chơi ra kiểm tra rồi cất lại. Trước khi đi, cháu tự quay lại cảm ơn cô, không kéo tôi nói hộ nữa.']),
('Hộp màu chưa bị cất','Một người vẽ biển tay định cất hộp màu vì ít đơn; bạn giúp giữ một phần bản vẽ và để khách chọn chính nét chưa hoàn hảo ấy.','He is an ___.',[
'Huy đóng hộp màu, tấm biển còn dở. "You are an artist." Cậu là một nghệ sĩ. Tôi giữ góc tấm gỗ, hỏi bông hoa này đã vẽ xong chưa.',
'Bạn bảo dạo này khách thích biển in sẵn hơn. Tôi chỉ xin giữ lại tấm đang vẽ, chưa bàn chuyện bán được hay không. Huy mở hộp màu, ngồi xuống thêm một chút.',
'Bác chủ quán ghé hỏi ai vẽ tấm biển. "He is an artist." Cậu ấy là một nghệ sĩ. Huy nhìn bông hoa còn lệch, rồi tự kể vì sao mình chọn màu đó.',
'Bạn nói giúp tôi câu cậu ấy là một nghệ sĩ bằng tiếng Anh nhé.',
'"He is an artist." Đúng rồi. Bác chọn giữ bông hoa đang vẽ dở ấy. Huy hỏi tôi mai có rảnh ngồi đây không. Tôi kéo chiếc ghế lại, trước khi trả lời.']),
('Một câu hát còn nhớ','Ca sĩ trẻ lo quên lời trước tiết mục nhỏ; người bạn nhắc một câu quen thuộc, để em đủ bình tĩnh bước ra và hoàn thành.','She is our ___.',[
'Mai đứng sau rèm, quên câu đầu. "She is our singer." Em ấy là ca sĩ của nhóm. Tôi đưa ly nước, ngồi xuống để em không phải đứng chờ một mình.',
'Tiết mục này em đã tập cùng cả nhóm nhiều ngày. Đến giờ lên sân khấu nhỏ, em lại nhìn xuống tờ lời bài hát. Tôi hỏi em nhớ nhất đoạn nào, để em bắt đầu từ đó.',
'Em hát thử câu quen thuộc, giọng còn nhỏ. "You are a good singer." Em là một ca sĩ tốt. Tôi gấp tờ lời lại, hỏi em có muốn tự cầm mic không.',
'Người dẫn đang hỏi ai là ca sĩ của nhóm mình. Bạn giúp tôi nói cả câu bằng tiếng Anh nhé.',
'"She is our singer." Đúng rồi. Mai bước ra, vẫn cầm tờ giấy gấp trong tay. Hát xong, em quay vào tìm tôi: Có một câu em tự nhớ được đấy.']),
('Tên mình sau buổi thử vai','Phong muốn làm diễn viên nhưng ngại thử vai; người bạn tập cùng, Phong bước vào và nhận lời hẹn cho một buổi đọc tiếp.','He is an ___.',[
'Phong tập lại câu đầu, rồi lại quên. "I want to be an actor." Tớ muốn thành diễn viên. Bạn nói vậy, nhưng vẫn chưa mở cửa phòng thử vai.',
'Tôi đứng ngoài tập cùng bạn. Phong cứ nhìn gương, hỏi mặt mình có hợp không. Tôi lật trang kịch bản: Mình thử nghe câu này trước đã. Bạn thôi nhìn gương một lúc.',
'Phong kể đoạn nhân vật trở về nhà, giọng chậm hơn. "You are a good actor." Cậu là diễn viên tốt. Bạn cười một chút, rồi tự cất gương vào túi.',
'Đến lượt giới thiệu bạn với người phụ trách. Bạn nói giúp tôi câu cậu ấy là một diễn viên bằng tiếng Anh nhé.',
'"He is an actor." Đúng rồi. Phong bước vào, đọc hết đoạn đã tập. Ra cửa, bạn đưa tôi tờ hẹn đọc tiếp ngày mai. Lần này, bạn không hỏi về gương mặt mình nữa.']),
('Ngăn kéo của ông','Ông định cất bản thảo vì nghĩ không ai muốn đọc; cháu đọc lại một đoạn và xin giữ câu chuyện ông chưa kể hết.','He is a ___.',[
'Ông đóng ngăn kéo, tôi giữ lại quyển sổ. "My grandfather is a writer." Ông tôi là người viết. Tôi chưa đọc hết đoạn ông kể hôm qua.',
'Ông bảo chuyện cũ chắc chẳng ai cần nữa. Tôi mở lại trang về cây trước sân, hỏi hồi bé ông có trèo lên đó không. Ông kéo ghế ngồi, rồi kể thêm một chi tiết.',
'Tôi ghi tên ông lên bìa mới của tập bản thảo. "He is a writer." Ông ấy là người viết. Ông sửa cho tôi một chữ, rồi lấy thêm tờ giấy trắng.',
'Nếu muốn giới thiệu ông ấy là một người viết, bạn nói câu nào bằng tiếng Anh?',
'"He is a writer." Đúng rồi. Ông viết thêm đoạn vừa kể. Tôi xin mượn tập bản thảo mang về đọc. Ông không đóng ngăn kéo nữa, chỉ dặn hôm sau kể ông nghe tôi thích đoạn nào.']),
('Người nấu bát cơm trưa','Một người mới phải nhận phần nấu trong ca thiếu người; đồng nghiệp giúp chia việc, để cậu đứng ra nhận đúng công mình đã làm.','He is the ___.',[
'Nồi còn trên bếp, người nấu lại vắng. "We need a cook." Mình cần một người nấu bếp. An nhìn tôi, hỏi hôm nay có thể bắt đầu với ít món hơn không.',
'Tôi ra ngoài nhận món, để An có chỗ tập trung. Khách quen hỏi sao chờ lâu hơn mọi hôm. Tôi nói người nấu đang làm từng phần, không giục An qua cửa bếp nữa.',
'An bưng phần ăn đầu tiên ra. "He is the cook." Cậu ấy là người nấu bếp. Tôi nhường chỗ để cậu tự đặt bát xuống trước vị khách đang đợi.',
'Khách muốn biết ai là người nấu bếp hôm nay. Bạn giúp tôi nói câu cậu ấy là người nấu bếp bằng tiếng Anh nhé.',
'"He is the cook." Đúng rồi. Khách hỏi An lần sau có nấu món này nữa không. Hết ca, cậu ngồi ăn bát đã để lại cho mình, lần đầu không phải chờ tôi nhắc.']),
('Bó hoa còn một chiếc nơ','Hai bạn bắt đầu bán hoa, một ngày ít khách khiến một người muốn dọn; họ chia lại việc, tiếp tục buổi bán còn đang dang dở.','Business is slow ___.',[
'Linh tháo chiếc nơ, định dọn xe hoa. "Business is slow today." Hôm nay việc kinh doanh chậm. Tôi giữ bó cuối, hỏi em muốn đi về thật chưa.',
'Hai đứa mới bắt đầu bán ở góc phố này. Linh cứ đếm lại tiền lẻ, tôi cứ sửa chiếc nơ. Có người hỏi giá rồi đi, em nhìn theo rất lâu mà không gọi lại.',
'"I do business here." Tôi kinh doanh ở đây. Tôi nói khi một cô hỏi xe hoa có trở lại ngày mai không. Linh ngẩng lên, chỉ cho cô xem bó còn đang gói.',
'Nếu muốn nói hôm nay việc kinh doanh chậm, bạn nói giúp tôi cả câu bằng tiếng Anh nhé.',
'"Business is slow today." Đúng rồi. Cô mua một bó, còn nhiều bó chưa bán. Linh buộc lại chiếc nơ ban đầu. Hai đứa thống nhất dọn khi trời tối, không dọn ngay lúc này.']),
('Tấm ảnh của công ty nhỏ','Nhân vật chụp ảnh kỷ niệm cho công ty nhỏ, định cất máy khi mọi người chưa về; đồng nghiệp giữ chỗ cho một người luôn đứng sau ảnh.','I work for this ___.',[
'Ảnh chụp xong, vẫn thiếu một người. "I work for this company." Tôi làm cho công ty này. Tôi đứng sau máy, nhìn mọi người đang chuẩn bị ra về.',
'Công ty của tôi chỉ có năm người. Tấm ảnh nào tôi cũng chụp giúp rồi lưu lại. Anh Khoa nhìn ảnh mới, hỏi sao lần nào cũng thiếu tôi. Tôi bảo vậy cũng được mà.',
'"Our company has five people." Công ty chúng tôi có năm người. Anh đếm lại bốn gương mặt trong ảnh, kéo tôi đứng vào khoảng trống rồi đặt máy lên bàn.',
'Có người hỏi bạn làm cho nơi nào. Bạn giúp tôi nói câu tôi làm cho công ty này bằng tiếng Anh nhé.',
'"I work for this company." Đúng rồi. Cả nhóm chụp lại. Tôi lưu tấm có đủ người, không xóa tấm cũ. Lần này, tôi biết mình sẽ muốn mở lại ảnh nào.']),
('Chiếc máy bà muốn tự bật','Bà ngại chạm máy tính để xem ảnh cháu; nhân vật chờ bà tự làm một bước nhỏ thay vì bấm hộ hết.','Turn on the ___.',[
'Bà giấu tay sau lưng, chưa dám bấm. "Turn on the computer." Bật máy tính lên nhé bà. Tôi kéo ghế gần, để bà tự chạm vào nút nguồn.',
'Em gửi ảnh trường mới về từ hôm qua. Bà muốn xem nhưng cứ gọi tôi tới mở giúp. Hôm nay, tôi chỉ ngồi cạnh. Bà bấm được rồi, vẫn quay sang hỏi có sao không.',
'"This computer is old." Máy tính này cũ rồi. Tôi nói khi bà sợ mình vừa làm nó chậm. Bà nhìn màn hình sáng lên, tay vẫn giữ trên mép bàn.',
'Bà muốn nhớ câu bật máy tính lên để lần sau nhờ cháu. Bạn nói giúp bà bằng tiếng Anh nhé.',
'"Turn on the computer." Đúng rồi. Ảnh em hiện ra. Bà nhìn một lúc, rồi hỏi muốn xem ảnh tiếp thì bấm chỗ nào. Tôi chưa kịp trả lời, bà đã kéo ghế lại gần hơn.']),
('Máy tính dưới mái hiên','Giữa mưa, người bạn lo chiếc máy chứa bài trình bày; nhờ nhân vật cầm giúp để buộc lại túi, rồi tới lớp và bắt đầu dù vẫn run.','Can you hold my ___?',[
'Mưa vào túi, Dung ôm chặt chiếc máy. "Can you hold my laptop?" Bạn cầm giúp máy tính xách tay của mình nhé. Tôi đứng sát mái hiên, nhận máy bằng hai tay.',
'Dung đã chuẩn bị bài trình bày nhiều ngày. Hôm nay, bạn cứ kiểm tra túi rồi kiểm tra giờ. Tôi giữ chiếc máy, để bạn có thể buộc lại quai túi đang tuột.',
'"My laptop is in my bag." Máy tính xách tay của mình ở trong túi. Dung nói sau khi cất máy lại, lần đầu buông tay khỏi miệng túi. Tôi gọi bạn lên chiếc xe vừa tới.',
'Nếu cần nhờ người khác cầm giúp máy tính xách tay của mình, bạn sẽ nói câu nào bằng tiếng Anh?',
'"Can you hold my laptop?" Đúng rồi. Đến lớp, Dung mở máy và nhìn tôi trước khi bắt đầu. Bạn vẫn nói chậm, nhưng không còn ôm chiếc túi trên ngực nữa.']),
('Cuộc gọi bố chưa dám nhấc','Bố chờ tin ở hành lang bệnh viện, tìm điện thoại đúng lúc người nhà gọi; cùng con nghe một lời nhắn bình thường để bớt lo.','Answer the ___.',[
'Bố đứng dậy rồi lại ngồi xuống. "Where is my phone?" Điện thoại bố đâu rồi? Tôi mở chiếc túi đang cầm, đặt máy vào tay bố.',
'Mẹ vào phòng khám đã lâu. Bố cứ hỏi giờ, dù đồng hồ ở ngay trước mặt. Tôi ngồi xuống cạnh bố, giữ lại chiếc ghế trống để lát mẹ ra còn ngồi.',
'"The phone is ringing." Điện thoại đang reo. Người nhà gọi hỏi hai bố con đã ăn gì chưa. Bố nhìn màn hình, ngập ngừng như thể vẫn đang đợi một cuộc gọi khác.',
'Bạn nhắc giúp bố câu nhấc điện thoại bằng tiếng Anh nhé.',
'"Answer the phone." Đúng rồi. Bố nghe máy, nói hai bố con vẫn đang đợi. Tôi lấy hộp bánh trong túi ra. Bố chia lại cho tôi một chiếc, rồi thôi đứng lên nhìn đồng hồ.'])]
for ep,(title,plot,stem,narrs) in zip(raw,updates):
 ep.update(title=title,plot_vi=plot,learner_outcome_vi='Nhận ra nghĩa chọn và dùng câu ngắn phù hợp tình huống.',editorial_review='Reviewed and rewritten by primary agent; narration frozen before anchors.')
 for i,(s,narr) in enumerate(zip(ep['scenes'],narrs)):
  s.update(narration=narr,practice_pause_seconds=4 if i==3 else 0,title_vi=['Chi tiết đầu chuyện','Điều cần hiểu','Hành động làm đổi chuyện','Lời người xem giúp nói','Kết quả'][i],purpose_en=['Open with a consequential detail, then provide an early English model.','Show a believable personal reason and resistance in the same situation.','Use another English model as a useful utterance, not a general technical/moral claim.','Ask for one supported sentence for the same need; wait before feedback.','Give the answer and show a modest concrete consequence, without miraculous success or a generic CTA.'][i])
 ep['scenes'][3]['stem']=stem
 (OUT/'narration-frozen'/f"{ep['job']}.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
print('Frozen twelve rewritten professions/device narrations, awaiting aligned visual plan')
