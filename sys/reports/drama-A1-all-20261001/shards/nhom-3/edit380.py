from pathlib import Path
import json
P=Path(__file__).parent/'380-389';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def put(num,lines,title=None,plot=None,visuals=None):
 e=E[str(num)]
 for s,n in zip(e['scenes'],lines):s['narration']=n
 if title:e['title']=title
 if plot:e['plot_vi']=plot
 if visuals:
  for s,v in zip(e['scenes'],visuals):s['visual_en']=v
 e.pop('extra_visual_states',None)
 return e
put(622,[
'Mai giữ tấm nhãn chưa dán. Hai chiếc túi bị để lẫn ở kho đồ thất lạc. Cô chỉ chữ tả màu: "Is this an adjective?" Đây có phải tính từ không?',
'Minh nhìn nhãn rồi nhìn túi xanh. Trong cụm trên giấy, blue tả màu của chiếc túi. Mai muốn biết đúng loại từ để ghi thêm đặc điểm dễ nhận.',
'Tính từ giúp tả đặc điểm ở đây. Một nhãn chỉ ghi túi chưa phân biệt được hai chiếc. Mai giữ chữ tả màu xanh, đặt nhãn cạnh đúng túi ấy.',
'Cô nhờ Minh kiểm trước khi dán: "Find the adjective here." Tìm tính từ ở đây nhé. Minh nhìn cả cụm, chưa chỉ ngay; Mai cũng tự tìm thử.',
'Mai muốn nhờ bạn kiểm từ tả màu trên nhãn của mình. Bạn nói giúp cô câu tìm tính từ ở đây bằng tiếng Anh nhé.',
'"Find the adjective here." Tìm tính từ ở đây nhé. Minh chỉ blue. Mai dán nhãn lên túi xanh, giữ túi nâu bên cạnh riêng ra để khỏi trao nhầm.'
],title='Nhãn cho chiếc túi xanh')
E['622']['custom_visible_text']=[{'text':'blue bag','placement':'center of one paper label','object':'paper bag label'}]
E['622']['scenes'][0]['visual_en']='Mascot and dark-shirt companion stand at a lost-property shelf with one blue bag and one brown bag. Companion holds the permitted label blue bag, still unattached.'
E['622']['scenes'][2]['visual_en']='Close shot of label blue bag beside blue bag; brown bag remains visibly separate behind it. No answer highlight or extra printed words.'
E['622']['scenes'][5]['visual_en']='Companion attaches permitted blue bag label to the blue bag while mascot points to blue. Brown bag stays separate on shelf; no new owner or crowd.'
put(623,[
'Bình đưa kéo, rồi giữ lại. Cậu mới tới phòng thủ công, chưa biết cất đâu. Cậu hỏi Minh: "What\'s the class rule?" Quy định của lớp là gì?',
'Minh chỉ ngăn có hình chiếc kéo. Lớp này yêu cầu dùng xong trả về đó. Bình định mang kéo sang bàn mình, giờ nhìn lại chỗ cất chung.',
'Quy định ấy dành cho người dùng đồ trong lớp. Bạn đến sau tìm ở đúng ngăn sẽ thấy. Bình bảo mình làm nốt tấm thiệp rồi trả, không mang về.',
'"We must follow the rule." Chúng ta cần làm theo quy định. Bình nói với Minh khi thấy kệ còn trống. Cậu thu giấy vụn rồi cầm kéo tới kệ.',
'Bình muốn nhớ cách hỏi khi tới một lớp mới, trước khi dùng đồ chung. Bạn nói giúp cậu câu quy định của lớp là gì bằng tiếng Anh nhé.',
'"What\'s the class rule?" Quy định của lớp là gì? Minh nhắc lại chỗ cất. Bình tự đặt kéo về ngăn, rồi lấy tấm thiệp vừa làm ra khoe bạn.'
],title='Ngăn chiếc kéo')
E['623']['scenes'][2]['visual_en']='One scissors silhouette on a blank storage slot, currently empty. Mascot indicates that same slot while brown-shirt learner holds scissors at his own table. No knives or written labels.'
E['623']['scenes'][3]['visual_en']='Brown-shirt learner collects plain paper scraps after finishing a card, scissors held lowered beside him; mascot watches beside storage shelf.'
E['623']['scenes'][4]['visual_en']='Same brown-shirt learner pauses with scissors beside the storage shelf and looks toward mascot. No third person enters; upper safe region for target-gap stem.'
E['623']['scenes'][5]['visual_en']='Brown-shirt learner places the scissors into their silhouette slot; finished blank handmade card remains on the worktable and mascot looks at it.'
put(624,[
'Hải định xóa câu hỏi về cây. Bạn bảo đoán chắc do thiếu nước rồi. Minh giữ trang vở: "We study science at school." Chúng mình học khoa học ở trường.',
'Cậu muốn mang câu hỏi tới tiết học thay vì xóa. Môn khoa học giúp hai bạn tìm hiểu tự nhiên và kiểm thông tin. Hai chậu cây nhìn khác nhau chưa đủ biết nguyên nhân.',
'Hải đặt bút xuống. Minh lấy ảnh chậu cây cả hai đã chụp, giữ câu hỏi bên cạnh. Họ chưa bón gì hoặc nhận suy đoán ấy là kết quả.',
'"Do you like science?" Bạn có thích khoa học không? Hải hỏi khi Minh đề nghị cùng tìm tài liệu của lớp. Minh gật đầu, đưa vở về giữa bàn.',
'Hải muốn rủ Minh học cùng nhưng cần hỏi cậu thích môn này không. Bạn nói giúp Hải câu bạn có thích khoa học không bằng tiếng Anh nhé.',
'"Do you like science?" Bạn có thích khoa học không? Minh nhận lời. Hải viết lại câu hỏi vừa định xóa, kẹp ảnh vào vở để mai mang tới lớp.'
],title='Câu hỏi chưa xóa',plot='Hải định bỏ câu hỏi vì đã đoán nguyên nhân cây héo. Minh giữ câu hỏi và cùng bạn chuẩn bị tìm hiểu trong môn khoa học.',visuals=[
'At a study table, olive-shirt learner holds an eraser above an illustrated question page; mascot keeps the page flat with one stick hand. Two plant photographs nearby, no readable text.',
'Mascot opens a school science notebook with simple tree and leaf diagrams, olive-shirt learner listens. No readable labels.',
'Both plant photographs rest beside the preserved question page; the eraser is set aside, pencil lies between the two learners.',
'Olive-shirt learner asks mascot across the same study table; mascot offers the notebook toward the shared center.',
'Both learners remain at the same table with notebook and two photos, no findings or treatment instructions. Hold upper safe space for practice.',
'Olive-shirt learner places the two photographs inside the notebook while mascot closes his own school bag beside him.'
])
put(625,[
'Khoa định khoanh luôn câu đoán. Buổi thử thuyền giấy còn chưa bắt đầu. Minh chặn đầu bút: "Is this a fact?" Đây có phải dữ kiện thật không?',
'Khoa bảo chiếc thuyền chắc sẽ nổi. Minh hỏi hai đứa đã quan sát chưa. Trong bài khoa học này, dữ kiện cần có căn cứ; lời đoán chưa cho hai bạn căn cứ đó.',
'Hai bạn đặt chiếc thuyền vào khay nước. Nó nổi ngay trước mắt ở lần thử này. Khoa nhìn kỹ rồi mới ghi lại điều vừa quan sát, giữ câu đoán riêng.',
'"We need facts for our project." Chúng ta cần dữ kiện cho dự án. Minh nhắc khi Khoa chuẩn bị trang báo cáo. Hai bạn dùng ghi chép lần thử của mình.',
'Khoa còn một câu muốn đưa vào bài nhưng chưa kiểm. Bạn nói giúp Minh câu đây có phải dữ kiện thật không bằng tiếng Anh nhé.',
'"Is this a fact?" Đây có phải dữ kiện thật không? Khoa dừng bút, giữ câu ấy ở phần cần hỏi. Báo cáo còn một chỗ trống, nhưng không chép lời đoán vào.'
],title='Câu đoán để riêng',plot='Khoa muốn dùng lời đoán làm dữ kiện cho dự án. Hai bạn quan sát một lần thử thuyền giấy rồi giữ kết quả có căn cứ riêng với câu chưa kiểm.',visuals=[
'At a classroom table, beige-shirt learner holds pencil above an unmarked report page. Mascot stops the pencil gesture; a dry paper boat and shallow empty tray stand nearby.',
'Both figures look at the dry paper boat beside the report, still outside the shallow tray. Page carries abstract non-letter lines only.',
'Close view of one paper boat floating on shallow tray water during this observed trial; both learners watch from behind the table. No laboratory labels or scientific diagrams.',
'Mascot indicates an observation note with abstract non-letter strokes beside the same floating boat, beige-shirt learner prepares the report.',
'Beige-shirt learner pauses over a separate abstract note while mascot asks him to check. Keep upper safe space for practice stem.',
'Beige-shirt learner puts the separate unchecked note aside; report page still has a blank space. Same boat and tray remain on table, no certification.'
])
put(626,[
'Lan lật sổ, vẫn thiếu một khoản. Hội chợ sách sắp dọn bàn mà tiền ghi chưa khớp. Minh ngồi xuống: "Do you like mathematics?" Bạn có thích toán học không?',
'Lan lắc đầu, ngại những trang đầy số. Minh bảo mình thích, xin cùng kiểm từng phần nhỏ. Hai đứa giữ sách đã bán một bên, giấy ghi tiền một bên.',
'Họ dùng phép cộng của môn toán để kiểm lại số đã ghi. Lan tìm dưới chồng sách, thấy một mẩu giấy mình chưa nhập vào sổ. Minh chờ bạn tự thêm.',
'"Mathematics is my favorite subject." Toán là môn tôi thích nhất. Minh trả lời khi Lan hỏi sao cậu chịu ngồi giúp. Cô đẩy sổ ra giữa để kiểm cùng.',
'Lan muốn hỏi lại sở thích của Minh trước khi rủ bạn chuẩn bị hội chợ sau. Bạn nói giúp cô câu bạn có thích toán học không nhé.',
'"Do you like mathematics?" Bạn có thích toán học không? Minh gật đầu. Lan kẹp mẩu giấy vào sổ, hẹn lần sau giữ mọi ghi chép cùng chỗ ngay từ đầu.'
],title='Mẩu giấy dưới chồng sách')
for s in E['626']['scenes']:s['visual_en']=s['visual_en'].replace('number columns','abstract non-legible number columns').replace('figures in the notebook','non-legible marks in the notebook')
E['626']['scenes'][5]['visual_en']='Both figures close the ledger with the loose receipt securely tucked inside; books remain stacked on the same fair table. No readable prices, sums or receipt writing.'
put(627,[
'Bác Thành nhìn lại đồng hồ trạm. Kim phút vừa lên đỉnh, kim giờ ở số chín. Minh báo: "It\'s nine o\'clock." Bây giờ là chín giờ đúng.',
'Xe giao sách chưa đến. Bác Thành sợ mình nhớ sai giờ, định đóng cổng đi chợ. Minh giữ bác lại, mở mẩu giấy hẹn bác để trong túi.',
'Giờ đúng trên đồng hồ không có phút lẻ. Bài này dùng o\'clock sau số giờ. Minh chỉ cả hai kim, rồi đưa giấy để bác so với lời hẹn.',
'"Let\'s meet at nine o\'clock." Mình gặp lúc chín giờ đúng nhé. Đó là lời tài xế đã nhắn. Bác Thành đọc lại, quyết định gọi trước khi đi.',
'Tài xế chưa nhớ giờ hai người đã hẹn. Bạn nói giúp bác câu mình gặp lúc chín giờ đúng nhé bằng tiếng Anh.',
'"Let\'s meet at nine o\'clock." Mình gặp lúc chín giờ đúng nhé. Tài xế báo đang ở ngoài cổng. Bác Thành cất giỏ đi chợ, ra mở cổng nhận sách.'
],title='Chưa đóng cổng',plot='Bác Thành tưởng nhớ sai giờ giao sách và định đi chợ. Minh đọc đồng hồ chín giờ đúng và kiểm lời hẹn để bác gọi tài xế ngay.')
E['627']['custom_visible_text']=[{'text':'9:00','placement':'center of one yellow appointment note','object':'appointment note'}]
E['627']['scenes'][5]['visual_en']='Elderly dark-shirt figure opens the gate for a stationary delivery van with plain book boxes, his market basket set aside indoors. Mascot remains at the open gate.'
put(628,[
'Huy giữ ảnh, chưa chịu chọn quán. Minh muốn hẹn nơi khác lần này. Cậu chỉ ảnh thư viện: "Do you often go there?" Bạn có thường tới đó không?',
'Huy gật đầu, kể mình hay đọc ở đó sau buổi học. Thường xuyên tức là việc lặp lại nhiều lần trong thói quen ấy; một ảnh chưa kể được hết các lần.',
'Minh ngại thư viện quá yên, không biết có chỗ ngồi cùng nhau không. Huy mở thêm ảnh góc đọc mình thích. Cậu muốn Minh thử trước khi chọn quán đông.',
'"I often read at the library." Tôi thường đọc ở thư viện. Huy nói về thói quen của mình, rồi rủ Minh xem chỗ ấy. Minh đồng ý một buổi thử.',
'Minh muốn hỏi lại việc Huy thường tới nơi ấy trước khi cùng đi. Bạn nói giúp cậu câu bạn có thường tới đó không bằng tiếng Anh nhé.',
'"Do you often go there?" Bạn có thường tới đó không? Huy gật đầu. Chiều ấy, hai bạn tìm được bàn cạnh cửa sổ; Minh đặt sách xuống chỗ vừa được giới thiệu.'
],title='Thử góc bàn của Huy')
E['628']['scenes'][2]['visual_en']='Friend offers a photograph of a quiet library table by a window to mascot, who hesitates with a cafe photograph face down beside him. No calendar or frequency tally.'
E['628']['scenes'][3]['visual_en']='Friend holds his closed book and the library-table photo, inviting mascot to visit. No stamped card, readable dates or new membership.'
E['628']['scenes'][5]['visual_en']='Both friends sit at one library table by a window, mascot sets his book on his chosen place. No other readers or readable signs.'
put(629,[
'Nam lục túi, bỏ sót cuốn sổ. Minh đã đứng ở cửa, vẫn mở sổ kiểm: "I always check my notebook." Tôi luôn kiểm sổ. Nam hỏi sao cậu chưa đi.',
'Minh bảo mỗi lần đến buổi học này, mình đều xem lại việc đã ghi. Always nói mọi lần trong thói quen cậu đang kể, không chỉ vài lần thuận tiện.',
'Nam định mượn luôn sổ của bạn. Minh giữ lại, giúp Nam tìm cuốn của mình dưới tập giấy. Hai đứa cùng kiểm việc hẹn, không cần chép thay cả trang.',
'Minh đưa thêm chiếc bút: "I always bring a pen." Tôi luôn mang bút. Cậu giữ một chiếc khác cho mình. Nam ghi giờ hẹn vào sổ vừa tìm thấy.',
'Nam hỏi thói quen gì khiến Minh vẫn kiểm trước khi ra cửa. Bạn nói giúp Minh câu tôi luôn kiểm sổ bằng tiếng Anh nhé.',
'"I always check my notebook." Tôi luôn kiểm sổ. Nam xem lại trang mình vừa ghi, đặt sổ vào túi. Minh chờ bạn kéo khóa xong rồi hai đứa mới đi.'
],title='Kiểm rồi mới đi')
E['629']['scenes'][2]['visual_en']='Mascot helps green-shirt friend uncover his own notebook beneath plain loose sheets on desk; mascot keeps his own notebook in the other stick hand.'
E['629']['scenes'][4]['visual_en']='Mascot holds his own notebook, green-shirt friend has his separately and asks about the routine. Keep upper safe region for target-gap practice stem.'
put(630,[
'An kéo cửa, rồi đứng sững. Khóa vẫn ở trong nhà. Minh đưa chìa của mình: "I never forget my key." Tôi không bao giờ quên chìa khóa.',
'Hai bạn cùng thuê căn hộ này. Minh kể mỗi buổi đến lớp mình đều mang khóa, chưa có lần quên trong thói quen ấy. Never diễn tả việc không xảy ra lần nào.',
'An xin quay vào lấy đồ. Minh mở cửa, đợi bạn kiểm túi. Câu có never đã mang ý phủ định; mẫu này không thêm not trước từ forget nữa.',
'"I\'m never late for class." Tôi không bao giờ đến lớp muộn. Minh nói về những buổi học của mình, rồi nhìn An. Cậu vẫn chờ bạn, không đi bỏ trước.',
'An hỏi vì sao Minh có khóa ngay khi cần. Bạn nói giúp Minh câu tôi không bao giờ quên chìa khóa bằng tiếng Anh nhé.',
'"I never forget my key." Tôi không bao giờ quên chìa khóa. An mang khóa ra, để riêng trong túi. Minh khóa cửa, cả hai cùng đi; lần này An tự kiểm lại.'
],title='Chờ bạn lấy khóa')
E['630']['scenes'][2]['visual_en']='Door now open, purple-shirt friend returns inside for his key while mascot waits on the threshold holding his own key. No key pouch, lock procedure or safety label.'
E['630']['scenes'][3]['visual_en']='Mascot waits beside the open door with a patient posture and closed school bag, friend visible inside retrieving key. No rushing gesture or readable time.'
E['630']['scenes'][5]['visual_en']='Both friends stand outside the closed apartment door, purple-shirt friend checks his own key in his pocket and mascot holds his own separately before leaving.'
put(631,[
'Linh cứ thêm tên vào lịch hẹn. Minh rủ cô ở lại nhà một chiều: "I sometimes stay at home." Tôi thỉnh thoảng ở nhà. Linh ngạc nhiên, ngừng viết.',
'Cô tưởng cuối tuần nào Minh cũng đi chơi. Cậu kể có hôm ra ngoài, có hôm ở nhà. Sometimes nói thỉnh thoảng trong những dịp ấy, không phải mọi lần.',
'Linh ngại mình từ chối thì bạn sẽ buồn. Minh bảo cuộc hẹn có thể là một bữa ăn ở nhà. Cậu đưa cô xem món hai người từng làm cùng.',
'"We sometimes cook together." Chúng tôi thỉnh thoảng nấu cùng nhau. Minh nhắc những buổi như vậy, không hẹn tuần nào cũng nấu. Linh chọn để trống chiều chủ nhật này.',
'Linh muốn nói mình cũng có lúc chọn ở nhà, không phải cuối tuần nào cũng đi. Bạn nói giúp cô câu tôi thỉnh thoảng ở nhà nhé.',
'"I sometimes stay at home." Tôi thỉnh thoảng ở nhà. Linh cất lịch, nhận lời ăn cùng Minh chủ nhật. Cô tự chọn món, còn Minh nhận phần dọn bàn.'
],title='Chừa lại chiều chủ nhật')
E['631']['scenes'][1]['visual_en']='Mascot and yellow-shirt companion talk across the table, closed notebook and a plain glass of water between them. No tea serving or implied therapy.'
E['631']['scenes'][2]['visual_en']='Mascot shows one photograph of a previous shared home meal, companion looks from photo to her open planner. Planner has abstract non-legible marks only.'
E['631']['scenes'][5]['visual_en']='Yellow-shirt companion closes her planner and points to a simple meal photograph, mascot carries two plates toward a cleared table. No cooking instructions or chopping tools.'
stems={622:'Find the ___ here.',623:"What's the class ___?",624:'Do you like ___?',625:'Is this a ___?',626:'Do you like ___?',627:'Let\'s meet at nine ___.',628:'Do you ___ go there?',629:'I ___ check my notebook.',630:'I ___ forget my key.',631:'I ___ stay at home.'}
colors={622:'dark grey',623:'brown',624:'olive green',625:'beige',626:'dark grey',627:'dark grey',628:'dark green',629:'forest green',630:'purple',631:'yellow'}
for num,e in E.items():
 e['scenes'][4]['stem']=stems[int(num)]
 e['characters'][0]['outfit_en']='Exactly one pale-blue short-sleeve torso (#8CCFE8) and minimal navy stick limbs.'
 for c in e['characters'][1:]:c['outfit_en']=f'Exactly one plain {colors[int(num)]} short-sleeve shirt and minimal navy stick limbs.'
 # Remove outfits repeated in visual prose that would request prohibited extra torso layers.
 for s in e['scenes']:
  for a,b in [('in a craft apron','in a brown shirt'),('in apron','in a brown shirt'),('in an apron','in a dark shirt'),('in an olive vest','in an olive shirt'),('in a beige vest','in a beige shirt'),('in a green hoodie','in a green shirt'),('in purple jacket','in purple shirt'),('in a purple jacket','in a purple shirt'),('in yellow apron','in yellow shirt'),('in a yellow apron','in a yellow shirt')]:s['visual_en']=s['visual_en'].replace(a,b)
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
