from pathlib import Path
import json
P=Path(__file__).parent/'390-399';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def put(num,lines,plot=None,visuals=None,title=None):
 e=E[str(num)];assert len(lines)==6
 for s,n in zip(e['scenes'],lines):s['narration']=n
 if plot:e['plot_vi']=plot
 if title:e['title']=title
 if visuals:
  for s,v in zip(e['scenes'],visuals):s['visual_en']=v
 return e
put(632,[
'Huy giục tôi lên xe máy. Bạn sợ tôi đi bộ sẽ tới xưởng muộn. Tôi lắc đầu: "I usually walk to work." Tôi thường đi bộ đi làm.',
'Tôi thích đi qua công viên sáng sớm. Thường thì tôi chọn đi bộ, dù có hôm đi xe khi cần. Usually trong lời kể ấy vẫn để chỗ cho ngày khác thói quen.',
'Huy tắt máy, hỏi: "Do you usually arrive early?" Bạn thường đến sớm không? Tôi gật đầu, kể mình thường đi trước giờ hẹn một chút để không phải vội.',
'Tôi chỉ chiếc ghế đá hai đứa hay ngồi hồi mới vào xưởng. Huy chưa ghé lại lâu rồi. Bạn tháo mũ, bảo hôm nay cũng muốn đi qua chỗ đó.',
'Huy hỏi tôi có đi xe cùng bạn lần này không. Bạn nói giúp tôi câu tôi thường đi bộ đi làm bằng tiếng Anh nhé.',
'"I usually walk to work." Tôi thường đi bộ đi làm. Huy gửi xe lại nhà, đi cạnh tôi. Tới ghế đá, hai đứa dừng một chút rồi mới vào xưởng.'
],title='Qua chiếc ghế cũ',plot='Huy muốn chở bạn đi làm, nhưng nghe về thói quen đi bộ qua công viên nên cùng bạn ghé lại ghế đá quen.')
E['632']['scenes'][0]['visual_en']='Mascot stands beside a stationary motorbike outside a home gate in dry morning weather. Grey-shirt coworker offers a spare helmet; no traffic or rain.'
E['632']['scenes'][3]['visual_en']='Mascot points toward a nearby park bench; grey-shirt friend removes his helmet beside the stationary bike outside the home gate.'
E['632']['scenes'][5]['visual_en']='Both minimal figures stand together by the old park bench; bike and helmets absent because left safely at home. Workshop visible beyond path, no crowd.'
put(633,[
'Lâm giữ nắp hũ, chờ tôi gật. Món mứt mẹ gửi vừa tới. Tôi bảo: "I tried it once." Tôi đã thử nó một lần, hồi tết năm ngoái.',
'Lâm hỏi có ngon không mà tôi nhớ lâu thế. Tôi kể chỉ được nếm một lần ấy khi còn ở nhà. Once gọi đúng một lần thử, không phải nhiều buổi ăn.',
'Lâm định để dành tới tết. Tôi rủ mở một chút hôm nay; hai anh em đâu thường có dịp ngồi ăn cùng. Bạn đặt hũ xuống bàn, lấy thêm đĩa.',
'"We meet once a week." Chúng mình gặp nhau một lần mỗi tuần. Tôi nhắc lịch gặp hiện tại, nói lần này muốn cùng ăn món mẹ gửi thay vì lại để nguyên.',
'Lâm hỏi tôi đã ăn món này nhiều lần chưa. Bạn nói giúp tôi câu tôi đã thử nó một lần bằng tiếng Anh nhé.',
'"I tried it once." Tôi đã thử nó một lần. Lâm chia một ít ra hai đĩa, đậy hũ lại. Tôi nhắn mẹ món đã đến, hai anh em đang ăn cùng.'
],title='Mở một chút hôm nay',plot='Hai anh em gặp mỗi tuần một lần. Lâm muốn để dành mứt, còn Nam nhắc lần duy nhất từng nếm và rủ chia món mẹ gửi ngay buổi này.')
E['633']['scenes'][2]['visual_en']='Green-shirt younger brother places closed ceramic jar on table and takes a second plain small plate while mascot brings the first one.'
E['633']['scenes'][3]['visual_en']='The two brothers sit at the table with the jar and two empty plates, discussing their regular meeting. No printed calendar or attendance count.'
E['633']['scenes'][5]['visual_en']='Two small servings of candied ginger sit on two plates, jar closed beside them; mascot holds a plain phone turned away from viewer to message family. No additional person.'
put(634,[
'Tấm thiệp cứ lệch khỏi phong bì. Tôi định cắt lại, bác Bảy giữ thước: "Please check it twice." Kiểm tra hai lần nhé. Giấy đẹp chỉ còn một tờ.',
'Tôi muốn làm thiệp mời bác dự buổi trưng tranh. Bác chưa biết mình là người được mời, vẫn ngồi giúp tôi sửa. Hai lần kiểm nghĩa là làm việc kiểm đúng hai lượt.',
'Tôi đặt lại thước trên tờ giấy, xem cả mép dài và mép ngắn. Lần kiểm thứ hai, tôi mới thấy mình giữ thước nghiêng. Bác chờ tôi tự sửa vạch.',
'"I measured it twice." Tôi đã đo nó hai lần. Tôi nói với bác sau hai lượt, rồi mới gấp thiệp. Bác hỏi sao hôm nay tôi làm kỹ vậy.',
'Bác đang chờ tôi xác nhận đã đo bao nhiêu lần. Bạn nói giúp tôi câu tôi đã đo nó hai lần bằng tiếng Anh nhé.',
'"I measured it twice." Tôi đã đo nó hai lần. Tôi đặt thiệp vào phong bì rồi đưa luôn cho bác. Bác nhìn tôi, cất thước xuống, kéo ghế ngồi lại.'
],title='Thiệp mời người đang giúp',plot='Nam làm thiệp cho bác Bảy nhưng chưa nói. Bác giúp kiểm kích thước hai lần; Nam đưa thiệp mời cho chính người đang giúp mình.',visuals=[
'Mascot holds a folded card partly outside a plain envelope at a table; older brown-shirt figure stops his trimming gesture and offers a ruler. No saw or workshop tools.',
'Older figure sits helping mascot at the same stationery table, one sheet of decorative paper and blank card nearby, no readable invitation.',
'Close view of ruler aligned to the same card edge; one slanted non-legible pencil mark is visible. Minimal stick hand rests against ruler, no exact measurements.',
'Mascot sets ruler down and folds the card again while older figure watches, envelope remains open beside him.',
'Mascot holds card and ruler separately, older figure waits for his confirmation. Keep top safe region for stem.',
'Mascot hands the closed plain envelope directly to the older helper, who puts his ruler down and pulls his chair closer.'
])
E['634']['scenes'][4]['stem']='I measured it ___.'
E['634']['extra_visual_states']=[{'quote':'Lần kiểm thứ hai, tôi mới thấy mình giữ thước nghiêng.','visual_en':'Same close camera at the card edge: mascot notices ruler angled across the card rather than aligned, prior to straightening it. Preserve card and pencil mark. No numbers.','purpose_en':'Show the second check revealing a visible alignment mistake before correction.'}]
put(635,[
'Bác Tư giữ tôi ngoài cửa lớp. Bác chưa nhận ra người vừa tới. Tôi nhắc: "I left school two years ago." Tôi rời trường cách đây hai năm.',
'Bác nhìn kỹ rồi cười, nhớ tôi hay ngồi bàn cuối. Cách đây hai năm tính lùi từ hôm nói chuyện này. Khoảng thời gian đứng trước ago trong câu vừa nghe.',
'Tôi đưa điện thoại ra: "You called an hour ago." Bác đã gọi cách đây một giờ. Cuộc gọi mời tôi nhận cuốn sổ cũ tìm thấy lúc dọn phòng.',
'Bác quên mình đã gọi ai, giờ lấy sổ trong ngăn kéo. Tôi nhận ra hình mình vẽ ngoài bìa. Bác hỏi hồi ấy tôi rời lớp bao lâu rồi.',
'Bạn nói giúp tôi câu tôi rời trường cách đây hai năm bằng tiếng Anh nhé. Bác vẫn đang chờ để xếp sổ vào đúng phần của lớp cũ.',
'"I left school two years ago." Tôi rời trường cách đây hai năm. Bác giao sổ cho tôi. Tôi mở ngay trang cuối, vẫn còn bức vẽ mình chưa tô xong.'
],title='Cuốn sổ bác giữ',plot='Bác Tư gọi Nam nhận cuốn sổ cũ rồi không nhận ra người tới cửa. Nam nhắc mình rời trường cách đây hai năm và cuộc gọi cách đây một giờ.')
E['635']['scenes'][0]['visual_en']='Older dark-blue-shirt school caretaker stands at classroom threshold, mascot waits outside, both facing each other. No noticeboard photo or group of children.'
E['635']['scenes'][1]['visual_en']='Mascot explains his past attendance to caretaker beside the same door; a small drawer cabinet visible inside. No photograph, classmates or labels.'
E['635']['scenes'][2]['visual_en']='Mascot holds a plain phone toward the caretaker to remind him of their recent call, no legible screen interface or additional caller.'
E['635']['scenes'][3]['visual_en']='Caretaker opens the drawer and retrieves a closed notebook with one simple unfinished drawing on its cover; mascot recognizes it.'
E['635']['scenes'][5]['visual_en']='Caretaker has handed notebook to mascot, who opens its final page showing an unfinished unlabelled sketch. Same classroom doorway, no key exchange.'
put(636,[
'Chị Hà định cất gói hàng lại. Xe còn chưa thấy, trời đã tối. Tôi báo: "The bus will arrive soon." Xe buýt sẽ đến sớm thôi.',
'Tôi vừa nhận tin báo xe đang gần bưu cục. Soon nói xe sẽ đến trong thời gian gần, không cho đúng số phút. Chị vẫn đứng chờ, giữ hộp trước mặt.',
'Chị thường hẹn tôi ăn sau ca, hôm nay sợ về muộn. Chị nhắn: "See you soon." Hẹn gặp em sớm nhé. Tôi bảo mình có thể chờ cùng.',
'Hai người dán nốt mép hộp. Chị nhìn ghế trống, mời tôi ngồi. Tôi cất điện thoại, chờ bên cạnh thay vì cứ nhắc chị đừng lo rồi bỏ về.',
'Chị hỏi xe có còn lâu không, khi ngoài cửa vẫn vắng. Bạn nói giúp tôi câu xe buýt sẽ đến sớm thôi bằng tiếng Anh nhé.',
'"The bus will arrive soon." Xe buýt sẽ đến sớm thôi. Đèn xe xuất hiện ngoài cửa. Chị Hà đứng lên ôm hộp, nhắc tôi giữ chỗ ăn cho hai người lát nữa.'
],title='Chờ cùng chị một chút')
E['636']['scenes'][1]['visual_en']='Mascot holds a plain phone with screen away from viewer and gives a recent update to yellow-shirt colleague, who holds the parcel at counter. No legible timetable.'
E['636']['scenes'][2]['visual_en']='Yellow-shirt colleague talks to mascot at postal counter with the same unopened parcel and tape; no other participant visible.'
E['636']['scenes'][3]['visual_en']='Both minimal figures sit beside the parcel counter, one empty stool now occupied by mascot. Outside window remains dark and empty.'
E['636']['scenes'][4]['visual_en']='Yellow-shirt colleague asks mascot beside the counter, dark doorway still empty. No arriving bus or driver yet; top safe area for target-gap stem.'
E['636']['scenes'][5]['visual_en']='Lights of stationary bus appear outside doorway; yellow-shirt colleague stands holding closed parcel, mascot rises from stool. Driver not visible, no transfer labels.'
put(637,[
'Cuộn chỉ rơi giữa hai chiếc ghế. Tôi định lấy chổi, cô Lan giữ tấm áo đang sửa. "I will do it later." Tôi sẽ làm việc đó sau.',
'Cô muốn xong phần áo trước vì đó là món tôi tặng chị mình tối nay. Tôi đặt chổi sang góc. Việc dọn vẫn phải làm, chỉ chuyển tới sau bước đang cần.',
'Cô hỏi chuyện buổi sinh nhật, nhưng tôi cứ nhìn vạt áo. "We can talk later." Chúng ta có thể nói chuyện sau. Tôi muốn làm xong rồi ngồi nghe cô kể.',
'Hai người cùng kiểm lại chiếc áo. Tôi treo lên cạnh cửa, cuộn chỉ vẫn dưới ghế. Later trong lời hẹn là sau phần sửa này, chưa phải một giờ cụ thể.',
'Cô Lan định đứng dậy dọn giúp. Bạn nói giúp tôi câu tôi sẽ làm việc đó sau bằng tiếng Anh nhé. Tôi muốn tự làm phần mình đã hẹn.',
'"I will do it later." Tôi sẽ làm việc đó sau. Áo treo xong, tôi cầm chổi gom chỉ. Cô Lan ngồi lại, kể chuyện; lần này tôi nghe, chẳng còn nhìn vạt áo.'
],title='Áo xong rồi mới kể',plot='Nam muốn sửa xong áo tặng chị rồi dọn và trò chuyện. Cô Lan giúp, Nam thực hiện việc đã để tới sau rồi ngồi nghe cô.')
E['637']['scenes'][3]['visual_en']='Finished blue tunic hangs beside doorway; both figures inspect it together, loose spools still on floor between two stools. No machinery close-up or exact stitch claims.'
E['637']['scenes'][4]['visual_en']='Purple-shirt seamstress reaches toward broom, mascot offers to do the postponed clearing. Tunic remains hung, thread spools still on floor.'
E['637']['scenes'][5]['visual_en']='Mascot sweeps the loose spools gently into a small collection area while purple-shirt seamstress sits talking on stool beside him. Same hung tunic, no customer.'
put(638,[
'Tuấn kéo chồng sách về góc bỏ. Tôi giữ lại: "We have a lot of books." Chúng ta có nhiều sách. Trong đó còn bộ truyện hai đứa đọc chung.',
'Phòng mới ít chỗ, Tuấn chỉ muốn mang đồ gọn. Tôi mở cuốn từng gập mép, đưa cho bạn. Cậu nhớ trang mình dừng, đặt sách trở lại thùng.',
'"There is a lot of work today." Hôm nay có nhiều việc. Tuấn nhìn các thùng còn trống, nhờ tôi cùng xếp. Cụm a lot of nói lượng nhiều đang nhắc tới.',
'Sách nhiều, việc cũng nhiều, hai mẫu dùng cùng cụm ấy. Tôi đề nghị mang bộ truyện trước, những cuốn khác lựa lại. Tuấn ngồi xuống cùng tôi thay vì bỏ cả chồng.',
'Bạn hỏi vì sao tôi giữ góc thùng rộng như vậy. Bạn nói giúp tôi câu chúng ta có nhiều sách bằng tiếng Anh nhé.',
'"We have a lot of books." Chúng ta có nhiều sách. Hai đứa đặt bộ truyện lên trên, để mở lại không phải lục cả thùng. Tuấn lấy một cuốn đọc nốt trang cũ.'
],title='Cuốn truyện gập mép',plot='Tuấn muốn bỏ cả chồng sách khi chuyển phòng; Nam giữ bộ truyện hai đứa từng đọc, hai bạn lựa sách và dành chỗ cho kỷ niệm nhỏ.')
E['638']['scenes'][4]['visual_en']='Both roommates face each other beside an open broad book box, red-shirt friend points to its available space. No driver, horn or extra person.'
E['638']['scenes'][5]['visual_en']='Red-shirt roommate opens one familiar comic book while mascot places the rest of its series on top inside their moving carton. Two people only, no vehicle or driver.'
put(639,[
'Bác Ba bày bàn, thiếu hai bát. Tôi nhìn chỗ ngồi mới thêm: "We need more bowls." Chúng ta cần thêm bát. Hôm nay bác muốn mời cả hàng xóm.',
'Bát đang có chỉ đủ phần ban đầu. More trong lời tôi là thêm so với số đó. Bác định cất bớt ghế, tôi xin lấy bát trong bếp để giữ lời mời.',
'Tôi mang bát ra, thấy bình nước cạnh bác vơi. "Can I have more water?" Cháu xin thêm nước được không? Cốc đã có một ít, tôi muốn thêm để mang ra bàn.',
'Bác rót tiếp rồi nhìn những ghế đã đủ bát. Tôi bảo mình sẽ dọn sau bữa, bác không cần ngại có người tới. Bác lấy khăn trải ngay chỗ vừa định bỏ.',
'Bác hỏi tôi lúc nãy còn thiếu đồ gì cho bàn. Bạn nói giúp tôi câu chúng ta cần thêm bát bằng tiếng Anh nhé.',
'"We need more bowls." Chúng ta cần thêm bát. Tôi đặt hai chiếc vừa lấy lên bàn. Bác Ba kéo thẳng các ghế, giữ cả những chỗ bác định cất đi.'
],title='Giữ hai chiếc ghế',plot='Bác Ba muốn bày bữa mời hàng xóm nhưng thiếu bát nên định bớt ghế. Nam lấy thêm bát và nước, giúp bác giữ trọn lời mời.',visuals=[
'Mascot and older white-shirt host stand at a home dining table with four chairs but only two plain bowls. No guests or crowd visible.',
'Older host starts to pull one unserved chair away while mascot points toward bowl shelf inside kitchen. Same four chairs and two bowls.',
'Mascot holds a partly filled glass toward host beside a partly empty water jug, two extra bowls rest on tray near him.',
'Host lays a plain cloth across table while mascot holds two clean bowls ready to add, all four chairs remain.',
'Two figures remain beside the incomplete dining setting, host asks mascot; extra bowls still on tray. No answer word printed on props.',
'Mascot sets the two extra bowls on the two previously empty places while host aligns all four chairs. No dinner guests shown.'
])
put(640,[
'Bác Năm giữ tay nắm cửa. Bác sợ chờ tôi gấp thiệp sẽ muộn. "It takes about ten minutes." Việc đó mất khoảng mười phút. Tôi xin bác đợi một chút.',
'Tôi muốn đem thiệp tới buổi gặp cùng bác. Khoảng mười phút là ước lượng, có thể hơn hoặc kém một chút. About trước lượng cho biết tôi chưa hứa đúng từng phút.',
'Bác nhìn chồng thiệp còn trống: "We have about twenty cards." Chúng ta có khoảng hai mươi tấm. Bác chỉ ước lượng chồng giấy, chưa đếm riêng từng chiếc.',
'Tôi chọn gấp số đang cần, giữ phần còn lại cho lần sau. Bác ngồi xuống thử gấp cùng. Hai người không còn nghĩ phải làm xong cả chồng mới ra cửa.',
'Bác hỏi phần tôi chọn sẽ mất chừng bao lâu. Bạn nói giúp tôi câu việc đó mất khoảng mười phút bằng tiếng Anh nhé.',
'"It takes about ten minutes." Việc đó mất khoảng mười phút. Gấp xong, tôi đưa bác một tấm để mang cùng. Bác cất thiệp vào túi, gọi tôi đi bên cạnh.'
],title='Bác ngồi đợi thiệp',plot='Nam xin bác Năm chờ gấp ít thiệp mang cùng. Hai người nói lượng ước chừng, không cố hoàn thành cả chồng rồi cùng rời nhà.',visuals=[
'Older orange-shirt figure holds a home door handle ready to leave while mascot sits folding a card at nearby table. No boat, river or crowd.',
'Mascot asks older figure to wait, showing one half-folded blank card and a small stack. No visible clock or exact time label.',
'Older figure gestures toward a roughly sized stack of plain cards without count marks or numbers, still beside home table.',
'Both figures sit folding a few cards, larger unused pile left aside; no complete count, measurements or labels.',
'Older figure pauses folding and asks mascot about remaining effort, top safe region left for practice stem.',
'Mascot hands older figure one finished blank card; older figure tucks it into his bag at the open door while mascot rises to join.'
])
put(641,[
'Miệng bình đất cứ nghiêng sang bên. Tôi định vò lại, chú Hùng giữ bàn xoay: "This is the right way." Đây là cách làm đúng, chú chỉ cách mình đang dùng.',
'Tôi muốn tự làm chiếc bình nhỏ để cắm hoa ở bàn học. Chú đặt mẫu bên cạnh, chỉ một động tác. Ở đây way nói cách làm việc ấy, không phải đường đi.',
'"Show me the way to do it." Chỉ cháu cách làm nhé. Tôi nhờ chú làm chậm để nhìn rõ. Chú giữ chiếc bình, tôi ngồi cạnh theo dõi thay vì cứ ấn thêm.',
'Tôi thử lại phần vừa nhìn. Miệng bình vẫn hơi nghiêng, nhưng không muốn vò bỏ nữa. Chú hỏi tôi đã hiểu cách mình hướng dẫn chưa; tôi gật, giữ tay lại để xem.',
'Bạn nói giúp tôi câu đây là cách làm đúng bằng tiếng Anh nhé. Tôi muốn xác nhận cách vừa được chỉ, trước khi thử thêm lần nữa.',
'"This is the right way." Đây là cách làm đúng. Tôi đặt bình lên ván, xin giữ cả chiếc hơi nghiêng. Chú đưa tôi một nhành hoa nhỏ để thử đặt vào.'
],title='Giữ chiếc bình hơi nghiêng',plot='Nam định vò bỏ chiếc bình đất bị nghiêng. Chú Hùng cho xem cách làm; Nam thử lại và giữ kết quả chưa hoàn hảo của mình.')
E['641']['scenes'][2]['visual_en']='Grey-shirt mentor demonstrates one gentle clay-shaping gesture at a stopped wheel, mascot watches from adjacent stool. One simple vase, minimal stick hands, no anatomical fingers.'
E['641']['scenes'][3]['visual_en']='Mascot has both minimal stick hands near the slightly tilted clay rim, mentor waits patiently beside him. Rim remains imperfect, no guaranteed technical success.'
E['641']['scenes'][5]['visual_en']='Slightly tilted small clay vase sits on a board; mentor offers mascot one simple flower sprig beside it. No firing, fresh water or material durability claim.'
for e in E.values():
 e['selected_gloss_vi']={'632':'thường thì','633':'một lần','634':'hai lần','635':'cách đây','636':'sớm thôi','637':'sau đó','638':'nhiều','639':'thêm, nhiều hơn lượng đang có','640':'khoảng chừng','641':'cách, phương pháp làm gì'}[e['job'].rsplit('-',1)[1]]
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
