from pathlib import Path
import json
P=Path(__file__).parent/'400-409';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def put(num,lines,title,plot,visuals,stem):
 e=E[str(num)]
 for s,n,v in zip(e['scenes'],lines,visuals):s['narration']=n;s['visual_en']=v
 e['title']=title;e['plot_vi']=plot;e['scenes'][4]['stem']=stem;e.pop('extra_visual_states',None)
 return e
put(642,[
'Bác Dũng cất cọ, định nghỉ luôn. Hàng rào còn một đoạn chưa sơn. Tôi kéo ghế lại: "I will do this part." Cháu sẽ làm phần này.',
'Bác đã giúp tôi cả chiều, dù hàng rào của nhà tôi. Tôi chỉ phần thấp gần chân rào, muốn bác ngồi nghỉ. Bác giữ thùng sơn, hỏi tôi có cần giúp không.',
'"Which part is next?" Phần tiếp theo là phần nào ạ? Tôi hỏi vì thanh gỗ góc bên vẫn chưa quét. Bác chỉ đúng đoạn nhỏ còn lại trên hàng rào.',
'Tôi sơn một bên, bác ngồi giữ thùng bên cạnh. Bác định đứng lên, tôi lắc đầu. Đoạn còn lại ít thôi; lần này tôi muốn làm để bác được nghỉ.',
'Bác hỏi có nên để phần này đến mai không. Bạn giúp tôi nói câu cháu sẽ làm phần này bằng tiếng Anh nhé.',
'"I will do this part." Cháu sẽ làm phần này. Xong đoạn cuối, tôi đặt cọ xuống. Bác vẫn ngồi trên ghế; tôi mang thêm cốc nước ra ngồi cạnh bác.'
],'Đoạn rào cho bác nghỉ','An nhận phần rào còn lại để bác hàng xóm được nghỉ sau buổi giúp mình.',[
'Older grey-shirt neighbor sets down paintbrush beside partly painted fence; mascot pulls a chair toward him. Dry afternoon, no rain or storm.',
'Older neighbor sits beside fence holding closed paint bucket; mascot gestures to a small unpainted lower section.',
'Mascot points to corner section of same fence while older neighbor indicates that specific unpainted section; no numbers or labels.',
'Mascot paints lower section while older neighbor remains seated holding bucket beside him. Single learning focus, no urgent weather.',
'Older neighbor points to small remaining section, mascot replies beside chair. Upper safe space for target-gap stem.',
'Finished fence behind both figures sitting together; paintbrush set away on ground, mascot offers a plain glass of water to neighbor.'
],'I will do this ___.')
put(643,[
'Chị Lan gọi, tôi đã ở ngoài cửa. Chị tưởng thùng quà vừa mất. Tôi quay lại: "Let\'s check the facts." Cùng kiểm tra những việc có thật nhé chị.',
'Chị nghe nói xe đã mang hết đồ đi. Tôi nhớ mình vừa để một thùng dưới bàn, chưa giao ai. Chị vẫn muốn gọi khắp nơi, tôi rủ tìm chỗ ấy trước.',
'Tôi kéo khăn bàn lên, chiếc thùng vẫn nằm đó. Chị ngồi xuống nhìn dấu băng dính mình đã dán. Không cần đoán nữa: đồ còn ở đúng chỗ tôi nhớ.',
'"That is a fact." Đó là một sự thật. Tôi nhắc việc hai người vừa thấy: thùng còn ở đây. Chị đặt điện thoại xuống, nhận ra mình đã nghe nhầm.',
'Chị vẫn hỏi tôi có chắc chuyện ấy không. Bạn nói giúp tôi câu đó là một sự thật bằng tiếng Anh nhé.',
'"That is a fact." Đó là một sự thật. Chị Lan kéo thùng ra, nhờ tôi đứng đợi cùng một chút. Tôi đặt túi xuống; lần này chị không cần gọi tìm nữa.'
],'Thùng dưới khăn bàn','Minh quay lại giúp chị Lan kiểm lời đồn mất quà; hai người tìm thấy thùng dưới bàn, chị giữ cậu ở lại đợi cùng.',[
'Mascot stands at office doorway with bag, orange-shirt colleague holds phone worriedly near a cloth-covered table. Two figures only.',
'Mascot gestures toward space beneath the cloth-covered table while colleague lowers phone reluctantly. Plain boxes nearby, no signed delivery documents.',
'Mascot lifts tablecloth to reveal one sealed parcel beneath, orange-shirt colleague bends to look directly at it.',
'Both figures look at the same parcel with its distinctive diagonal tape; colleague puts phone down. No count, tally or signatures.',
'Colleague asks mascot beside revealed parcel; same table, upper safe region for practice stem.',
'Colleague slides parcel out beside her stool; mascot places his bag on floor and pulls a second stool closer to wait with her.'
],'That is a ___.')
put(644,[
'Ông giữ lại giỏ hoa của tôi. Tôi đã chọn toàn hoa tròn, ông muốn loại cánh dài. Tôi hỏi: "What kind of flower is this?" Đây là loại hoa gì ạ?',
'Ông chỉ bó đang cầm, nói tên bằng tiếng Việt. Cùng là hoa nhưng có loại khác nhau. Ông muốn giỏ giống giỏ mình từng làm cho bà, không chỉ giống màu.',
'Tôi định giữ loại mình thích cho nhanh. Ông lấy ảnh giỏ cũ ra, đặt cạnh hai bó. Tôi nhìn cánh hoa, nhận ra bó của ông hợp điều ông đang nhớ.',
'"We need this kind of flower." Chúng ta cần loại hoa này. Tôi nói, đổi bó trong giỏ. Ông cười, để tôi tự chọn số còn lại.',
'Ông đưa hai bó lần nữa, chờ tôi nói muốn lấy loại nào. Bạn nói giúp tôi câu chúng ta cần loại hoa này bằng tiếng Anh nhé.',
'"We need this kind of flower." Chúng ta cần loại hoa này. Tôi xếp bó cánh dài vào giỏ, giữ một bông tròn cạnh đó. Ông nhìn, bảo bông ấy là phần của cháu.'
],'Hai loại trong giỏ','Bình muốn làm nhanh bằng loại hoa mình thích; nghe kỷ niệm của ông, cậu đổi loại để giỏ mang cả ý của hai người.',[
'Older brown-shirt figure holds back a flower basket filled with round blossoms while mascot offers a contrasting long-petal bunch. No nursery treatments.',
'Older figure shows long-petal bouquet beside round blossom bouquet, mascot looks closely at the two shapes.',
'One simple photograph of a flower basket lies beside both bouquets, containing flowers only with no people or text. Both figures compare shapes.',
'Mascot swaps the main round blossom bouquet for long-petal flowers in basket, older figure watches appreciatively.',
'Older figure offers both bunches again, mascot indicates long-petal flowers. Upper safe region for stem, no botanical labels.',
'Finished basket holds long-petal flowers with one round bloom on edge. Both figures look at the shared arrangement.'
],'We need this ___ of flower.')
put(645,[
'Cô Mai giữ ảnh, chẳng nhớ ngày chụp. Tôi đề nghị: "Look at the back." Nhìn mặt sau nhé cô. Mặt trước có ảnh, chỗ cần tìm có thể ở phía đối diện.',
'Cô sợ lật mạnh sẽ làm rơi ảnh. Tôi đặt khung lên khăn mềm, đỡ cả hai mép rồi cùng cô xoay. Mặt sau vẫn nguyên, có một mẩu giấy ông đã dán.',
'"The date is on the back." Ngày tháng ở mặt sau. Tôi chỉ dòng ông viết, cô cúi xuống đọc. Lâu rồi cô chỉ xem mặt ảnh, chưa nhìn phía này.',
'Cô muốn chụp lại ngày ấy để nhớ, nhưng tôi đã quay khung về phía ảnh. Cô đặt điện thoại sang bên, xin tôi xoay lại. Tôi giữ khung, đợi cô chuẩn bị.',
'Cô cần nhờ tôi nhìn mặt sau thêm một lần nữa. Bạn nói giúp cô câu nhìn mặt sau bằng tiếng Anh nhé.',
'"Look at the back." Nhìn mặt sau nhé. Tôi xoay khung lại. Cô chụp xong, đặt ảnh lên bàn; lần này còn giữ cả mẩu giấy ghi ngày trong tập ảnh của mình.'
],'Ngày ở mặt sau','Nam cùng cô Mai lật khung ảnh cẩn thận và tìm ngày chụp ở mặt sau; cô giữ thêm bản chụp mẩu ghi chú cũ.',[
'Mascot and yellow-shirt aunt hold framed abstract landscape photograph front-facing under a lamp. No family faces or third person.',
'Frame rests on plain cloth, both figures gently support opposite edges while turning it toward reverse side.',
'Close view of frame reverse with one attached note bearing permitted date; yellow-shirt aunt looks at it beside mascot.',
'Mascot holds frame front-facing while aunt places plain phone on table ready to photograph its reverse again.',
'Aunt asks mascot to turn frame, phone waiting on table. Upper safe region for stem.',
'Aunt photographs reverse of frame with phone screen facing away; beside it open album contains a blank pocket for copy. No repair tools or nails.'
],'Look at the ___.')
E['645']['custom_visible_text']=[{'text':'1990','placement':'small handwritten date centered on attached note','object':'note on reverse of frame'}]
put(646,[
'Chú Hùng lục bàn lần thứ ba. Kéo lại nằm dưới vải. Tôi đưa khay trống: "This is the right place." Đây là chỗ phù hợp, mình để kéo ở đây nhé.',
'Chú hay đặt đồ xuống bất cứ góc nào còn trống. Tôi cũng vậy nên hai người cứ tìm. Khay ở ngay cạnh bàn, không cần mở ngăn hoặc với lên kệ.',
'"Let\'s find a safe place." Hãy tìm chỗ an toàn. Chú đề nghị đưa khay vào phía trong, khỏi vướng lối đi. Tôi nhìn chỗ mới, gật đầu cùng chú.',
'Chúng tôi làm nốt áo đã nhận sửa. Chú đưa tay tìm kéo dưới vải theo thói quen; tôi đặt khay sát lại, để chú nhìn thấy ngay. Chú bật cười, nhận kéo.',
'Chú hỏi để xong thì cất đâu, sợ lát nữa lại quên. Bạn nói giúp tôi câu đây là chỗ phù hợp bằng tiếng Anh nhé.',
'"This is the right place." Đây là chỗ phù hợp. Chú đặt kéo vào khay rồi đưa luôn thước cạnh nó. Tôi cất phần của mình cùng chỗ, khỏi phải hỏi tìm lần nữa.'
],'Khay sát cạnh bàn','Tuấn và chú Hùng thống nhất chỗ cất đồ ở khay trong góc bàn; sau khi quên một lần, cả hai cùng thực hiện.',[
'Green-shirt tailor searches fabric scraps on table; mascot holds plain empty tray beside newly found scissors.',
'Mascot places tray at table corner near both workers; scissors lie separately on fabric, no wall hooks.',
'Older figure moves the empty tray farther inside the table edge away from walkway, mascot agrees. No mounting or tool safety instructions.',
'Older tailor searches fabric with one hand while mascot slides scissors tray into his sight. Same unfinished garment on table.',
'Older tailor holds scissors after work, looking at mascot for where to put them. Upper safe region for stem.',
'Scissors and ruler rest together in the shared tray at inner table corner; mascot adds his pencil, older figure lowers empty hand.'
],'This is the right ___.')
put(647,[
'Tôi giữ món đồng, bà định bỏ đi. Nó chẳng giống đồ nào tôi biết. Tôi hỏi: "What is this thing?" Đồ vật này là gì thế bà?',
'Bà Năm nhìn kỹ, nhận ra hộp nhạc mình giữ từ lâu. Bà bảo nó cũ quá, chắc không còn dùng được. Tôi đặt lại xuống bàn thay vì bỏ vào túi dọn đồ.',
'Bà xoay núm bên cạnh, một đoạn nhạc nhỏ vang lên. "This thing makes music." Đồ vật này phát ra nhạc. Tôi nói với bà, mời bà thử nghe thêm.',
'Nhạc ngừng, tôi định xoay tiếp. Bà giữ tay tôi, cười bảo đoạn ngắn ấy mình vẫn nhớ. Bà không cần nó mới như xưa; chỉ muốn giữ lại món đồ đã tìm thấy.',
'Tôi muốn hỏi tên đồ vật trên tay bà, trước khi xếp vào rương. Bạn nói giúp tôi câu đồ vật này là gì bằng tiếng Anh nhé.',
'"What is this thing?" Đồ vật này là gì? Bà nhắc lại tên hộp nhạc. Tôi đặt nó lên góc bàn riêng, bà kéo ghế tới để hôm sau vẫn nhìn thấy.'
],'Món đồng chưa bỏ','Khoa hỏi về vật bà định bỏ khi dọn rương, hai người nghe đoạn nhạc ngắn và quyết định giữ hộp nhạc cũ.',[
'Mascot holds simple round brass music box above an open sorting chest while purple-shirt grandmother reaches toward a discard bag.',
'Grandmother recognizes simple brass cylinder on table, mascot has put discard bag aside. No exposed gear or oil.',
'Grandmother turns one small winding key on intact brass box while mascot listens. No written music notes.',
'Grandmother stops mascot from winding again and smiles toward the old box on tabletop. No broken machinery or repair procedure.',
'Mascot asks grandmother about intact brass box she holds. Upper safe region for target-gap practice.',
'Brass music box rests alone on a separate table corner; grandmother pulls her stool close while mascot leaves discard bag by chest.'
],'What is this ___?')
put(648,[
'Thảo xoay quả cầu, tìm mãi chưa thấy. Em muốn biết dì ở đâu. Tôi chỉ phần bên kia: "The world is very big." Thế giới rất rộng lớn.',
'Quả cầu nhỏ này gợi Trái Đất, thế giới hai chị em đang sống. Dì đã chuyển tới nước khác. Thảo chỉ biết tên, chưa hình dung nơi ấy cách nhà mình thế nào.',
'"Where in the world is she?" Dì ở đâu trên thế giới? Em hỏi. Tôi chỉ vị trí dì từng gửi, để em nhìn cùng nơi thay vì xoay đoán mãi.',
'Thảo muốn bỏ quả cầu vì thấy xa quá. Tôi lấy hai miếng giấy đánh dấu nhà mình và chỗ dì. Em giữ một bên, tôi xoay để hai dấu cùng hiện ra.',
'Em hỏi vì sao phải xoay qua nhiều chỗ mới tìm được dì. Bạn nói giúp tôi câu thế giới rất rộng lớn bằng tiếng Anh nhé.',
'"The world is very big." Thế giới rất rộng lớn. Thảo dán thêm dấu nhỏ ở nhà. Tới giờ gọi dì, em giữ quả cầu cạnh mình để lần này kể đã tìm được chỗ ấy.'
],'Hai dấu trên quả cầu','Huy giúp Thảo tìm nơi dì sống trên địa cầu, em đánh dấu hai nơi rồi giữ quả cầu cạnh mình trong cuộc gọi.',[
'Smaller pink-shirt sibling turns a simple globe on desk while mascot points toward opposite hemisphere. No legible place names.',
'Both figures look at the unlabeled globe and one plain travel envelope closed beside it. No aunt image or video-call screen.',
'Pink-shirt sibling asks while mascot indicates one unlabeled coastline on globe. No location facts, coordinates or invented names.',
'Mascot and sibling attach two plain colored stickers to globe, one near each indicated place, keeping same desk setup.',
'Sibling holds globe still while mascot explains its scale. Upper safe area for stem, no printed answer on globe.',
'Sibling keeps marked globe beside plain phone during call; mascot sits beside her. Screen turned away, no third person visible.'
],'The ___ is very big.')
put(649,[
'Chú Lâm giữ chiếc điều khiển lại. Tôi đã định tắt phim. "Wait for the end." Chờ phần kết nhé. Hai người mới xem tới đoạn gần xong.',
'Tôi tưởng câu chuyện đã khép lại, muốn đứng dậy dọn bàn. Chú bảo còn một đoạn mình chưa xem. Tôi ngồi xuống, để chiếc điều khiển giữa hai người.',
'Chú đã chờ cả tuần để xem cùng tôi. Tôi cứ hỏi khi nào hết vì còn việc khác. Lần này tôi cất điện thoại, không giục nữa, nhìn vào màn hình cùng chú.',
'"This is the end." Đây là phần kết. Chú nói khi đoạn cuối tới. Tôi thấy câu chuyện trả lời điều hai người đoán từ đầu, nên vẫn ngồi xem cho trọn.',
'Chú hỏi giờ mình đã đến phần nào của phim. Bạn nói giúp tôi câu đây là phần kết bằng tiếng Anh nhé.',
'"This is the end." Đây là phần kết. Tôi tắt máy sau khi phim xong, rồi hỏi chú thích đoạn nào. Chú đặt điều khiển xuống, kéo ghế lại để kể.'
],'Chờ đoạn chú muốn xem','Phong muốn tắt phim sớm nhưng nhận ra chú đã chờ xem cùng. Cậu ở lại tới phần kết rồi ngồi nghe chú nói.',[
'At home, navy-shirt older figure keeps remote between himself and mascot seated beside him. Screen shows abstract non-human shapes only.',
'Mascot sits back on sofa, remote now on small table between both figures. Same abstract screen, no credits or theater crowd.',
'Mascot sets phone face down beside remote and turns attention toward screen with older relative. No visible people on screen.',
'Both figures watch a simple abstract closing image on screen, older relative gestures toward it. No readable titles or credits.',
'Older relative asks mascot while both remain seated, remote still on table. Upper safe space for practice stem.',
'Television off, mascot turns his chair toward older relative to listen. Remote left on table, phone face down.'
],'This is the ___.')
put(650,[
'Bố xoay hộp quà sang bên. Tôi đã dán đẹp mặt trước, còn một vách trống. "Look at this side." Nhìn mặt bên này nhé. Bố chỉ chỗ vừa lộ ra.',
'Tôi định đưa đi luôn vì ai cũng nhìn mặt trước. Bố bảo đặt hộp lên bàn sẽ thấy cả mặt bên. Tôi kéo ghế, lấy phần giấy còn lại ra xem.',
'"Which side needs paper?" Mặt bên nào cần giấy ạ? Tôi hỏi. Bố chỉ vách bên trái, khác với nắp và mặt trước đã dán. Tôi giữ hộp ở đúng góc đó.',
'Bố đưa mảnh giấy mình thích nhưng tôi định chọn màu khác. Tôi thử đặt cả hai lên vách, rồi giữ mảnh của bố. Món quà này là hai bố con cùng chuẩn bị.',
'Tôi muốn mời bố nhìn mặt bên đã chọn giấy. Bạn nói giúp tôi câu nhìn mặt bên này bằng tiếng Anh nhé.',
'"Look at this side." Nhìn mặt bên này nhé. Bố nhìn giấy mình chọn trên hộp, cười. Tôi dán nốt, đưa bố giữ một đầu dây để cả hai cùng buộc quà.'
],'Mảnh giấy bố chọn','Đức định để mặt bên hộp quà trống; bố giúp chọn giấy, hai người hoàn thành món quà chung.',[
'Older grey-shirt father rotates one gift box with decorated front toward blank left side, mascot watches holding paper scraps.',
'Mascot pulls stool to table and looks at blank side panel with father; top and front already decorated.',
'Mascot points to blank left side while father confirms that panel. Same camera angle distinguishes side from front and lid.',
'Two different decorative paper pieces held against side by father and mascot, no printed patterns or words.',
'Mascot shows chosen paper applied to left side, father looks. Keep upper safe region for stem.',
'Gift box now decorated on same left side; father and mascot hold opposite ends of one ribbon, ready to tie it together.'
],'Look at this ___.')
put(651,[
'Chị Nga kéo rèm, định thôi bày sách. Hộp trưng không vừa chỗ cửa. Tôi giữ lại: "I have an idea." Em có một ý tưởng, mình thử xoay hộp nhé.',
'Tôi muốn dành góc ấy cho những cuốn chị từng đọc cho tôi. Chị nghĩ phải mua kệ mới, không muốn làm thêm hôm nay. Tôi đề nghị chỉ thử bằng hai hộp sẵn có.',
'Chị nhìn cách tôi xoay: "That is a good idea." Đó là một ý tưởng hay. Hộp giờ vừa khoảng trống, còn chỗ đặt những cuốn bìa nhỏ cạnh nhau.',
'Hai người xếp thử sách lên, chưa chắc ai đi ngang sẽ nhìn. Chị vẫn mở rèm lại vì muốn thử cùng tôi. Tôi lấy cuốn cũ của chị đặt vào giữa.',
'Chị hỏi sao lúc nãy tôi giữ rèm lại. Bạn nói giúp tôi câu em có một ý tưởng bằng tiếng Anh nhé.',
'"I have an idea." Em có một ý tưởng. Chị Nga nhận ra cuốn mình đọc cho tôi hồi nhỏ. Chị ngồi xuống lật một trang; tôi kéo ghế tới, để góc bày sách đợi chút.'
],'Cuốn sách giữa hai hộp','Kiên đề nghị thử góc bày sách bằng hộp sẵn có thay vì mua kệ, rồi cùng chị Nga đọc lại cuốn gắn với hai người.',[
'Teal-shirt shopkeeper reaches toward window curtain, mascot holds one plain display crate beside a narrow gap. No passersby or customers.',
'Mascot offers two empty crates already in shop, shopkeeper looks hesitant beside covered display gap. No construction tools.',
'Mascot rotates one crate to fit gap, shopkeeper nods toward it. Two existing crates only.',
'Both figures set a few plain illustrated books on crates, no claims about sales or visibility, curtain partly open.',
'Teal-shirt shopkeeper asks mascot near the same window display, upper safe space for target-gap stem.',
'Shopkeeper sits reading one familiar illustrated book while mascot pulls a stool closer; display remains waiting behind them. No new customer.'
],'I have an ___.')
# Record a narrow label for the selected back/side spatial senses.
E['645']['selected_gloss_vi']='mặt sau của đồ vật';E['650']['selected_gloss_vi']='mặt bên của đồ vật'
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
