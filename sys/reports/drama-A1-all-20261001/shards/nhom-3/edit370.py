from pathlib import Path
import json
P=Path(__file__).parent/'370-379';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def narration(num,lines,title=None,plot=None):
 e=E[str(num)];assert len(lines)==len(e['scenes'])
 for s,n in zip(e['scenes'],lines):s['narration']=n
 if title:e['title']=title
 if plot:e['plot_vi']=plot
 e.pop('extra_visual_states',None)
 e['scenes'][4]['stem']=e['scenes'][4]['stem'].replace('...','___')
 e['characters'][0]['outfit_en']='Exactly one pale-blue short-sleeve torso (#8CCFE8) and minimal navy stick limbs.'
 for c in e['characters'][1:]:
  if num==613:c['outfit_en']='Exactly one plain brown short-sleeve shirt and minimal navy stick limbs.'
  if num==614:c['outfit_en']='Exactly one olive-green short-sleeve shirt and minimal navy stick limbs.'
  if num==615:c['outfit_en']='Exactly one plain beige short-sleeve shirt, khaki hat, small backpack and minimal navy stick limbs.'
  if num==617:c['outfit_en']='Exactly one dark-green short-sleeve shirt, mail cap, mail satchel and minimal navy stick limbs.'
  if num==620:c['outfit_en']='Exactly one lavender short-sleeve shirt and minimal navy stick limbs.'
 return e
narration(612,[
'Minh buông cọ xuống sàn. Chiếc bàn cuối cùng cũng sơn xong. Cậu thở phào với Huy: "It\'s a great feeling." Một cảm giác thật tuyệt.',
'Lúc chiều, hai đứa suýt bỏ cuộc vì mặt bàn còn xước. Huy muốn mua chiếc khác. Minh xin thử thêm một lần, rồi cả hai cùng làm đến tối.',
'Giờ hai đứa nhìn chiếc bàn ngay ngắn, thấy công sức của mình có kết quả. Minh vui và nhẹ nhõm. Cảm giác ấy vẫn còn dù tay đã mỏi.',
'"I like this feeling." Tôi thích cảm giác này. Minh nói với Huy khi bạn hỏi có tiếc cả buổi chiều không. Cậu kéo ghế lại, mời bạn ngồi.',
'Huy bảo lần sau cứ mua cho nhanh. Minh vẫn muốn tự làm cùng bạn. Bạn nói giúp Minh câu tôi thích cảm giác này bằng tiếng Anh nhé.',
'"I like this feeling." Tôi thích cảm giác này. Huy chia đôi ổ bánh, đặt lên chiếc bàn đã khô. Hai đứa ăn ngay tại chỗ vừa định bỏ cuộc.'
],title='Chiếc bàn suýt bỏ',plot='Minh và Huy suýt bỏ việc sơn bàn, cùng thử thêm rồi chia sẻ cảm giác vui nhẹ nhõm khi dùng chính thành quả của mình.')
E['612']['scenes'][1]['visual_en']='Same workshop, scratched unpainted table in the afternoon, grey-shirt friend holding a furniture catalogue face down while mascot keeps a paintbrush beside the tabletop. No readable print.'
E['612']['scenes'][2]['visual_en']='Same camera in the evening: painted table complete and dry, both minimal figures stand back admiring their own work with relaxed shoulders.'
E['612']['scenes'][3]['visual_en']='Mascot pulls one stool beside the dry painted table for his grey-shirt friend; a second stool is already beside him.'
E['612']['scenes'][4]['visual_en']='Both friends remain beside the finished table, grey-shirt friend gestures toward the unused catalogue while mascot gestures toward the table. Hold the practice stem in upper safe space.'
E['612']['scenes'][5]['visual_en']='Both friends sit at the finished dry table sharing one split bread roll. Paintbrush rests on the floor well away from their meal. No printed text.'
narration(613,[
'Bình đặt cặp lồng xuống bàn. Minh vừa tan ca, chưa kịp ăn. Anh họ mở nắp: mẹ cậu gửi món cháo Minh thích từ nhỏ.',
'Minh thường giục mẹ đừng bận vì mình. Bình nhắc câu mẹ hay nói: "Love is important in our family." Tình yêu thương rất quan trọng trong gia đình mình.',
'Mẹ nhớ món cậu thích, Bình đem qua dù phải đi vòng. Sự yêu thương của người nhà hiện ra qua việc nhỏ ấy. Minh kéo ghế mời anh ngồi.',
'Bình định về ngay, sợ làm phiền. Minh giữ anh lại: "Thank you for your love." Cảm ơn sự yêu thương của anh. Cậu lấy thêm một bát.',
'Bình bảo chỉ mang đồ ăn thôi mà. Minh muốn cảm ơn cả việc anh đã dành thời gian. Bạn nói giúp cậu câu cảm ơn sự yêu thương của anh nhé.',
'"Thank you for your love." Cảm ơn sự yêu thương của anh. Bình đặt túi xuống. Minh chia cháo cho hai bát, gọi mẹ để cả ba cùng trò chuyện.'
],title='Thêm một bát',plot='Anh họ mang món mẹ gửi tới sau ca làm; Minh giữ anh cùng ăn và nói lời cảm ơn sự yêu thương của gia đình.')
vs=['Modest room after work. Mascot sits at a table as his brown-shirt cousin sets one closed metal food container on it.','Brown-shirt cousin opens a container of porridge at the same table while mascot looks attentively at him.','Mascot pulls an empty stool toward the table for his cousin, whose shoulder bag remains on.','Cousin holds his shoulder-bag strap ready to leave while mascot offers an empty bowl and gestures toward the stool.','Cousin and mascot pause beside the empty stool and two bowls. Preserve the upper safe region for the practice stem.','Both cousins sit at the table with two filled bowls and a plain phone propped between them during a family call. No visible interface or extra person.']
for s,v in zip(E['613']['scenes'],vs):s['visual_en']=v
narration(614,[
'Dũng rửa bát, chẳng nói câu nào. Minh quên phần việc của mình tối qua. Cậu đứng cạnh bồn rửa: "Can we talk?" Mình nói chuyện được không?',
'Dũng khóa vòi nước nhưng vẫn quay lưng. Minh nhận lỗi, không viện cớ đi làm thêm. Cậu muốn nghe bạn nói thay vì đoán vì sao bạn giận.',
'Dũng bảo mình phải dọn cả hai hôm liền. Minh ngồi nghe cho hết rồi đề nghị nhận phần cuối tuần. Cuộc nói chuyện giờ có cả ý của hai người.',
'Minh mang lịch việc ra bàn: "Let\'s talk about the plan." Cùng nói chuyện về kế hoạch nhé. Dũng chỉ hôm cần đổi, Minh lấy bút ghi lại.',
'Bạn cùng phòng vẫn hơi ngại ngồi xuống. Minh muốn mời bạn nói chuyện tiếp cho rõ. Bạn nói giúp cậu câu mình nói chuyện được không bằng tiếng Anh nhé.',
'"Can we talk?" Mình nói chuyện được không? Dũng kéo ghế lại. Hai đứa sửa lịch xong; Minh đứng lên rửa nốt bát, để bạn nghỉ một tối.'
],title='Phần bát của Minh')
E['614']['scenes'][2]['visual_en']='Both minimal figures sit on plain stools at the kitchen table; olive-shirt roommate speaks while mascot listens with hands still.'
E['614']['scenes'][3]['visual_en']='Mascot points to a simple blank chore grid with non-letter marks; olive-shirt roommate points to one cell. No written weekdays or readable text.'
E['614']['scenes'][5]['visual_en']='Mascot now washes the remaining dishes at the same sink while his olive-shirt friend rests on the nearby stool; blank chore grid with non-letter marks lies on table.'
narration(615,[
'Khách cầm vé, nhìn hai chiếc xe. Minh đang trực ở bến. Cậu bước tới hỏi: "Do you speak English?" Bạn có nói tiếng Anh không?',
'Vị khách gật đầu, đưa vé cho Minh. Hai người dùng tiếng Anh để hiểu nhau. Với speak ở đây, Minh đang hỏi người khách có nói được thứ tiếng ấy không.',
'Minh chỉ đọc được vài câu đơn giản. Thấy khách chờ, cậu hơi ngập ngừng rồi lấy chiếc vé xem điểm đến. Khách kiên nhẫn đứng cạnh, không giục.',
'"I speak a little English." Tôi nói được một chút tiếng Anh. Minh báo trước với khách rồi chỉ chiếc xe xanh. Khách nhìn theo, gật đầu xác nhận.',
'Khách hỏi thêm, Minh muốn nói rõ mình chỉ biết một chút tiếng Anh. Bạn nói giúp cậu câu tôi nói được một chút tiếng Anh nhé.',
'"I speak a little English." Tôi nói được một chút tiếng Anh. Khách chậm lại khi hỏi. Minh tìm được chỗ lên xe cho khách, rồi quay về quầy trực.'
],title='Một chút cũng đủ mở lời')
E['615']['scenes'][2]['visual_en']='Mascot examines a plain bus ticket with abstract non-letter marks while beige-shirt traveler patiently waits beside him. Both blue and grey buses remain visible through shelter.'
E['615']['scenes'][3]['visual_en']='Mascot points toward the blue bus beside the grey one, traveler follows the direction. No numbers, destinations or readable bus labels.'
E['615']['scenes'][5]['visual_en']='Traveler waits at the open blue bus door, waving thanks toward mascot at the nearby counter. Bus is stationary; no crowd or readable signs.'
narration(616,[
'Hà cứ nhìn màn hình điện thoại. Minh cần nhờ em chăm chậu lan cuối tuần. Cậu gõ nhẹ mặt bàn: "Listen to me." Nghe anh nói này.',
'Hà ngẩng lên nhưng tay vẫn lướt. Minh đặt bình tưới xuống, chờ em cất điện thoại. Anh muốn em chú ý nghe lời mình, chứ chỉ nhìn anh chưa đủ.',
'Hà úp điện thoại lại. Em hỏi vì sao anh cứ nhắc chậu hoa đó. Minh kéo ghế bên cạnh, kể ông đã trồng nó từ lúc hai anh em còn nhỏ.',
'"Listen to the story." Nghe câu chuyện này nhé. Trong câu ấy, listen to hướng lời nhờ vào chuyện anh đang kể. Hà ngồi lại, hỏi thêm về ông.',
'Minh còn một điều muốn dặn, nhưng Hà định cầm điện thoại lên. Bạn nói giúp anh câu nghe anh nói này bằng tiếng Anh nhé.',
'"Listen to me." Nghe anh nói này. Hà để điện thoại xuống. Em nhắc lại việc đã nghe, rồi đặt bình tưới cạnh chậu lan để cuối tuần nhớ chăm.'
],title='Điện thoại úp xuống',plot='Minh nhờ em chăm chậu lan của ông. Hà đang dùng điện thoại, rồi cất máy để nghe câu chuyện và lời dặn của anh.')
E['616']['scenes'][5]['visual_en']='Younger ribbon-wearing figure sets the watering can beside the purple orchid and leaves her phone face down on table; mascot sits listening to her recap. No instructions or readable phone UI.'
narration(617,[
'Chú Tám giữ lại phong bì. Minh chạy ra nhưng chú chưa đưa ngay. Chú hỏi đúng tên người nhận rồi nói: "This letter is for you." Bức thư này dành cho cháu.',
'Ngõ bên cũng có một người tên Minh. Chú muốn chắc thư đến đúng nhà. Minh chỉ vào cửa của mình, nhận ra nét chữ người bạn đã chuyển đi.',
'Cậu mở phong bì, thấy tờ giấy gấp có lời bạn viết. Đó là bức thư gửi cho cậu, cả thông điệp trên giấy; hôm nay letter không chỉ một chữ cái.',
'Minh khoe với chú: "I got a letter from my friend." Cháu nhận được thư từ bạn mình. Lâu rồi không gặp, cậu cứ tưởng bạn đã quên địa chỉ.',
'Chú hỏi thư của ai gửi đến mà cháu vui vậy. Bạn nói giúp Minh câu tôi nhận được thư từ bạn mình bằng tiếng Anh nhé.',
'"I got a letter from my friend." Tôi nhận được thư từ bạn mình. Chú Tám đi tiếp. Minh mang giấy ra hiên, định viết lại ngay để bạn không phải chờ.'
],title='Đúng nhà mới đưa',plot='Người đưa thư giữ phong bì để kiểm đúng người nhận vì hàng xóm trùng tên. Minh nhận thư bạn cũ, muốn viết trả lời ngay.')
E['617']['scenes'][0]['visual_en']='At a small alley gate, elderly mailman holds back one stamped envelope and checks with mascot standing inside. Bicycle leans safely beside gate.'
E['617']['scenes'][2]['visual_en']='Mascot opens the envelope to reveal a folded letter with abstract ink strokes; no legible addresses, names, postal labels or letter contents.'
E['617']['scenes'][5]['visual_en']='Mascot sits on porch with unfolded letter showing abstract ink strokes, a fresh blank sheet and a pen, ready to answer. Mailman and bicycle recede outside gate.'
narration(618,[
'Lan đẩy trang bài đọc sang bên. Minh giữ lại, che các dòng dưới: "Read this sentence." Đọc câu này nhé. Cậu chỉ một câu ngắn trên đầu trang.',
'Lan sợ nhìn cả đoạn sẽ đọc sai. Minh để cô đọc riêng câu nói người viết đang ở đây. Những từ ấy đi cùng nhau, tạo ra một thông báo trọn ý.',
'Câu trên trang bắt đầu bằng chữ hoa, có dấu chấm cuối. Đó là câu đang đọc. Câu hỏi cũng có thể là câu; mình đừng chỉ đếm số từ để nhận ra.',
'Lan nhìn lại: "This sentence is short." Câu này ngắn. Cô thử đọc rồi kéo mảnh giấy xuống một chút. Minh chờ, không đọc hộ câu tiếp theo.',
'Lan muốn đọc thêm nhưng còn ngập ngừng. Minh chỉ đúng câu vừa để lộ. Bạn nói giúp cậu câu đọc câu này bằng tiếng Anh nhé.',
'"Read this sentence." Đọc câu này nhé. Lan đọc xong, tự kéo giấy xuống tiếp. Cả trang vẫn còn đó, nhưng hai bạn đã tìm được cách bắt đầu.'
],title='Che bớt một trang')
E['618']['custom_visible_text']=[{'text':'We are here now.','placement':'one short line on the upper exposed area of the reading sheet','object':'reading sheet'}]
E['618']['scenes'][2]['visual_en']='Close-up of the one permitted sentence We are here now. on the exposed sheet, with capital W and final period clearly visible. Blank paper covers everything below; no other readable print.'
narration(619,[
'An giữ nắp hộp trong tay. Cậu chỉ một chữ, hỏi Minh: "What does this word mean?" Từ này nghĩa là gì? Hộp bánh chưa mở được.',
'Minh nhìn chỗ em chỉ. An đã biết hình bánh trên hộp, nhưng chưa hiểu phần chữ. Cậu muốn hỏi đúng một từ ấy, chứ không hỏi tên cả hộp.',
'Minh đọc chữ trên nắp rồi thử kéo đúng mép mở. Một từ có thể mang điều cần hiểu trong tình huống; ở đây nó giúp hai anh em tìm chỗ mở hộp.',
'"I know this word." Anh biết từ này. Minh chỉ cho An mép nắp cần kéo. An thử, nhưng dưới đáy còn một từ khác cậu chưa từng đọc.',
'An muốn hỏi tiếp phần chữ vừa thấy, để lần sau tự mở hộp. Bạn nói giúp em câu từ này nghĩa là gì bằng tiếng Anh nhé.',
'"What does this word mean?" Từ này nghĩa là gì? Minh ngồi xuống xem cùng An. Hai anh em mở được hộp; An giữ lại nắp để lần sau hỏi tiếp.'
],title='Từ trên mép nắp',plot='An muốn tự mở hộp bánh nhưng chưa hiểu phần chữ. Em hỏi Minh một từ cụ thể, thử chỗ mở rồi tiếp tục hỏi khi thấy từ khác.')
E['619']['custom_visible_text']=[{'text':'OPEN','placement':'small label beside the tin opening tab','object':'tin lid'}]
E['619']['scenes'][2]['visual_en']='Close view of the tin opening tab beside the permitted word OPEN; mascot points to the tab, younger orange-shirt figure watches. No icon labels or other readable lettering.'
E['619']['scenes'][4]['visual_en']='Orange-shirt learner holds the tin turned to show its underside with abstract non-letter marks and looks toward mascot. Keep upper safe area clear for practice stem.'
narration(620,[
'Mai giữ thẻ, chưa chịu thả xuống. Cậu đọc câu rồi hỏi Minh: "Is this a verb?" Đây có phải động từ không? Hai hộp vẫn đang để trống.',
'Mai phải chia thẻ cho nhóm chơi đoán hành động. Minh chỉ từ run trong câu tôi chạy. Ở câu ấy, nó nói việc người nói làm, chứ không gọi tên người.',
'Động từ có thể diễn tả hành động hoặc trạng thái. Hôm nay hai bạn chỉ kiểm từ chạy trong câu này. Minh bước vài bước minh họa, Mai nhìn lại thẻ.',
'"Yes, it\'s a verb." Đúng, đó là động từ. Minh đáp câu hỏi của Mai. Cô đặt thẻ vào hộp có hình người chạy, rồi đưa hộp cho cậu.',
'Mai muốn kiểm lại từ vừa chọn trước khi mang cho nhóm chơi. Bạn nói giúp cô câu đây có phải động từ không bằng tiếng Anh nhé.',
'"Is this a verb?" Đây có phải động từ không? Minh gật đầu. Mai mang hộp ra; lần này cô giữ nguyên câu trên thẻ để người chơi hiểu từ được dùng thế nào.'
],title='Thẻ chưa vào hộp',plot='Mai phân loại thẻ cho trò đoán hành động, hỏi về run trong câu I run. Minh minh họa và xác nhận để cô chuẩn bị đúng thẻ.')
E['620']['custom_visible_text']=[{'text':'I run.','placement':'center of one flashcard','object':'flashcard'}]
E['620']['scenes'][0]['visual_en']='Lavender-shirt figure holds one flashcard bearing the permitted sentence I run. between two blank sorting trays while mascot watches.'
E['620']['scenes'][1]['visual_en']='Lavender-shirt figure points to run in the permitted sentence I run. on the single flashcard; mascot leans toward that same word.'
E['620']['scenes'][2]['visual_en']='Mascot takes a running stride beside the table while lavender-shirt learner looks between him and the same I run. card. Single torso and minimal stick limbs, no realistic fingers.'
E['620']['scenes'][4]['visual_en']='Lavender-shirt learner lifts the same I run. card from the running-symbol tray to check it with mascot. No new flashcard or extra word.'
narration(621,[
'Nam gạch rồi lại xóa. Minh nhìn bài chọn từ loại của bạn: "This word is a noun." Từ này là danh từ. Cậu chỉ chữ gọi chiếc ghế.',
'Nam cần chọn một từ để dán vào góc đồ dùng. Cậu đã khoanh nhầm chữ miêu tả. Minh kéo chiếc ghế gần lại: lần này hãy tìm từ gọi tên nó.',
'Danh từ có thể gọi tên người, vật, nơi hay ý niệm. Trong câu này, chair gọi tên chiếc ghế. Minh khoanh riêng từ ấy, để Nam thấy đúng chỗ cần kiểm.',
'Minh đưa lại bút: "Find the noun in this sentence." Tìm danh từ trong câu này nhé. Cậu không khoanh hộ nữa; Nam nhìn câu bên cạnh chiếc ghế.',
'Nam muốn nhờ Minh hỏi lại để tự chọn một lần. Bạn nói giúp Minh câu tìm danh từ trong câu này bằng tiếng Anh nhé.',
'"Find the noun in this sentence." Tìm danh từ trong câu này nhé. Nam gạch dưới chair. Cậu đem thẻ đặt cạnh chiếc ghế, rồi nhường bạn ngồi viết phần còn lại.'
],title='Tên chiếc ghế',plot='Nam chọn nhầm từ miêu tả khi chuẩn bị thẻ đồ dùng. Minh dùng chiếc ghế thật và câu I need a chair. để giúp Nam tự tìm danh từ.')
E['621']['custom_visible_text']=[{'text':'I need a chair.','placement':'one centered line on a study card','object':'study card'}]
E['621']['scenes'][1]['visual_en']='Mascot pulls one plain wooden chair beside the study table, capped learner compares it with the card I need a chair. No other readable notebook writing.'
E['621']['scenes'][2]['visual_en']='Close view of card bearing I need a chair. with a circle around chair only, wooden chair clearly beside it. No arrows to unrelated objects.'
E['621']['scenes'][3]['visual_en']='Mascot offers the pencil to learner over a second clean copy of the card I need a chair. with no answer marks. Wooden chair remains beside table.'
E['621']['scenes'][4]['visual_en']='Learner waits with pencil above the clean card I need a chair. while mascot gestures toward it. No underline or answer highlight; upper area for target-gap practice stem.'
E['621']['scenes'][5]['visual_en']='Learner places his card beside the wooden chair, chair underlined in the permitted sentence I need a chair. Mascot now sits on that chair, learner stands beside him.'
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
