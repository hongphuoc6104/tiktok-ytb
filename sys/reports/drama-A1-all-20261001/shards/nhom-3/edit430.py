from pathlib import Path
import json
P=Path(__file__).parent/'430-439';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def line(num,i,n):E[str(num)]['scenes'][i-1]['narration']=n
def visual(num,i,v):E[str(num)]['scenes'][i-1]['visual_en']=v
line(672,1,'Huy quay mặt khỏi bản vẽ. Cậu muốn bỏ phần mình đã vẽ lệch. Tôi giữ giấy: "Look at this drawing." Nhìn bản vẽ này nhé. Mình chưa cần làm lại hết đâu.')
line(672,2,'Tôi xin Huy nhìn lại cả trang, không chỉ chỗ cậu đang ngại. Cậu quay xuống bàn, thấy phần gian hàng hai đứa đã chọn vẫn còn nguyên. Tôi đưa bút cho bạn.')
line(672,3,'Huy chỉ khung cửa hơi nghiêng, bảo chỗ đó không giống ý ban đầu. Tôi kéo ghế lại, giữ trang giấy để cậu thấy có thể sửa riêng phần ấy.')
line(672,4,'"Let\'s look at it together." Cùng nhìn nó nhé. Tôi đề nghị xem chung, không muốn bạn bỏ cả buổi mình làm. Huy ngồi xuống, chỉ cho tôi đường muốn sửa.')
line(672,6,'"Look at this drawing." Nhìn bản vẽ này nhé. Huy nhìn lại, sửa đường khung cửa một chút. Tôi giữ nguyên phần tên hai đứa trong hồ sơ, để bạn cầm bản chung đem đi.')
visual(672,1,'Orange-shirt friend turns away from imperfect booth drawing at table; mascot keeps sheet flat and invites him to inspect. No readable labels or names.')
visual(672,3,'Mascot draws stool closer while orange-shirt friend points to one slightly slanted doorway line in their unlabelled booth sketch. No measurements or paper tearing.')
visual(672,6,'Friend folds revised drawing into a blank shared folder and holds it ready to carry, mascot stays beside him. No visible written names, measurements or perfect-straight certification.')
E['672']['plot_vi']='Huy định bỏ phần vẽ lệch; tôi rủ nhìn lại cả bản chung và sửa riêng khung cửa, để bạn vẫn mang thành quả hai đứa đi nộp.'
line(673,1,'Anh Tuấn giữ túi, không cho tôi giúp. Quai phồng, sách còn thò ra. "The bag looks heavy." Túi trông có vẻ nặng. Tôi nói điều mình thấy từ dáng túi.')
line(673,2,'Anh bảo xách một mình được, nhưng cứ nhìn con dốc ngoài cửa. Tôi chưa biết túi nặng bao nhiêu, chỉ thấy nó căng. Tôi kéo ba lô mình lại gần để hỏi thêm.')
line(673,3,'"You look worried." Anh trông có vẻ lo. Tôi nói khi anh dừng tay trước cửa, không bảo mình đọc được suy nghĩ anh. Anh thừa nhận ngại nhờ tôi mang cùng.')
line(673,4,'Tôi xin cầm một ít sách, vì hai anh em cũng đi chung. Anh lấy ra cuốn tôi từng mượn, đặt vào ba lô đã mở. Tôi chờ anh chọn nốt, không giành cả túi.')
line(673,6,'"The bag looks heavy." Túi trông có vẻ nặng. Anh Tuấn đưa tôi phần sách vừa chọn. Ra cửa, anh chờ tôi mang ba lô, hai anh em bước cùng thay vì anh đi trước.')
E['673']['teaching_form']='looks';E['673']['selected_gloss_vi']='trông có vẻ'
visual(673,3,'Dark-green-shirt brother hesitates looking toward doorway beside full bag, mascot addresses his worried posture. No actual weighing or broken strap.')
visual(673,4,'Older brother places one familiar plain book into mascot\'s open backpack, keeping main bag himself. They share the load voluntarily.')
line(674,1,'Linh úp chiếc túi rỗng xuống bàn. Cậu không tìm được chìa khóa phòng. "I believe you." Tôi tin bạn. Tôi đáp khi Linh bảo đã gửi lại chỗ mình học.')
line(674,2,'Linh cứ xin lỗi vì sợ tôi tưởng bạn làm mất. Tôi xin nghe lại chỗ cậu nhớ, không bắt bạn mở túi thêm lần nữa. Linh chỉ bàn thư viện ở cuối đường.')
line(674,3,'Tôi còn hẹn việc khác, nhưng nếu bỏ bạn đi thì Linh phải quay lại một mình. Tôi cất điện thoại, rủ bạn đi cùng xem chỗ đã gửi.')
line(674,4,'"Do you believe me?" Bạn có tin tôi không? Linh hỏi ở cửa, vẫn ngại kéo tôi quay lại. Tôi gật, cầm túi giúp bạn để cả hai đi được ngay.')
line(674,6,'"I believe you." Tôi tin bạn. Hai đứa quay lại bàn thư viện, tìm thấy khóa ở góc. Linh đưa tôi cầm mở cửa khi về, rồi kéo ghế cho tôi nghỉ cùng.')
visual(674,3,'Mascot puts plain phone into pocket and picks up bag to accompany yellow-shirt friend, both at home table with empty tote. No manager or penalty notice.')
visual(674,6,'At their home door, mascot holds retrieved key while yellow-shirt friend opens doorway to pull two chairs close inside. No third library attendant visible.')
E['674']['extra_visual_states']=[{'quote':'Hai đứa quay lại bàn thư viện, tìm thấy khóa ở góc.','visual_en':'Both registered figures inspect a quiet empty library desk; one small key lies at a corner, no attendant, extra reader or readable label.','purpose_en':'Show the check finding the object before the home-door ending.'}]
E['674']['plot_vi']='Linh sợ bạn không tin lời mình về chìa khóa; tôi bỏ việc đang định đi để cùng quay lại tìm, rồi bạn mời tôi nghỉ chung.'
line(675,1,'An gạt tờ giấy hỏng vào góc. Em muốn thôi làm lồng đèn. Tôi đặt máy lên bàn: "Let\'s watch the video." Cùng xem video nhé. Mình thử nhìn lại một lần.')
line(675,3,'Đoạn mẫu chỉ hiện giấy và bàn tay gấp, không có người nói trước máy. An nhìn theo chưa kịp, giấy trên tay vẫn chưa biết đổi chỗ. Tôi dừng chờ em hỏi.')
line(675,6,'"Let\'s watch the video." Cùng xem video nhé. Tôi phát lại phần em cần, không cầm giấy làm hộ. An gấp được một cánh, kéo tờ hỏng về để thử lại chỗ mình đã bỏ.')
visual(675,2,'Mascot props plain phone on stand showing only a colored paper diagram; younger learner leans toward it with a fresh sheet. No human presenter or interface text.')
visual(675,3,'Younger learner hesitates with folded paper while phone displays paper-only diagram on neutral background; no extra person or anatomical hands on screen.')
visual(675,6,'Younger learner has completed one simple paper fold and pulls old crumpled sheet back onto table, mascot watches beside plain phone showing paper-only diagram. No instant finished lantern.')
E['675']['plot_vi']='An muốn bỏ sau nếp gấp hỏng; tôi rủ xem lại mẫu và để em tự hỏi, tự thử một cánh thay vì làm hộ cả chiếc lồng đèn.'
line(676,1,'Tôi che máy, vẫn không nghe rõ. Bác Nam đang gọi hẹn lấy khóa. "Can you hear me?" Cháu có nghe thấy bác không? Bác hỏi, nhưng gió lấn nửa câu.')
line(676,2,'Bác còn việc phải đi, muốn giao khóa ngay chiều nay. Tôi chỉ nghe từng tiếng, không dám gật thay câu trả lời. Tôi chỉ cho bác chờ một chút rồi tìm chỗ yên hơn.')
line(676,3,'Tôi vào góc cầu thang, tránh tiếng gió ở cửa. Bác vẫn giữ máy, không cúp đi để gọi người khác. Tôi áp máy vừa tầm tai, thử nghe lại lời bác.')
line(676,4,'"I can hear you now." Bây giờ cháu nghe thấy bác. Tôi báo khi giọng bác đã tới rõ. Bác nói giờ hẹn, tôi nhắc lại để chắc mình không nghe nhầm.')
line(676,5,'Bác lại hỏi cháu có nghe được không trước khi kết thúc cuộc gọi. Bạn nói giúp tôi câu bây giờ cháu nghe thấy bác bằng tiếng Anh nhé.')
line(676,6,'"I can hear you now." Bây giờ cháu nghe thấy bác. Bác đợi tôi nói xong mới cất máy. Chiều ấy tôi tới nhận khóa, nhắc đúng lời hẹn bác đã nói, cả hai không cần chờ nữa.')
E['676']['scenes'][4]['stem']='I can ___ you now.'
visual(676,2,'Grey-shirt older neighbor waits alone with phone beside quiet entrance and key ring; no busy street, crowd or split-screen text.')
visual(676,3,'Mascot moves inside quiet stairwell corner while holding phone, no ear pain or forced tight pressure.')
visual(676,6,'Both registered figures meet at quiet lobby entrance in afternoon, older neighbor hands mascot the key ring. No additional resident or schedule label.')
E['676']['plot_vi']='Tôi chưa nghe rõ cuộc gọi hẹn giao khóa nên chuyển vào chỗ yên; bác đợi, hai người xác nhận giờ và gặp đúng hẹn.'
line(677,1,'Trang báo mình chỉ vừa đổi tàu. Tôi giữ cuốn sách định gửi bạn: "I hope you can come." Tôi hy vọng bạn tới được. Quán tôi ngồi ở gần ga thôi.')
line(677,3,'Trang sợ quay qua quán sẽ phải vội ra tàu, chưa dám nhận lời. Tôi nhìn cuốn sách, quyết định có thể mang ra gần ga gặp bạn, đâu cần bạn tới đúng chỗ mình.')
line(677,4,'"I hope we can meet soon." Tôi hy vọng mình gặp nhau sớm. Tôi nhắn rồi mang sách ra cửa. Trang còn phải xem giờ, tôi chưa biết cuộc gặp có được không.')
line(677,5,'Trước khi có lời đáp, tôi muốn nhắc mình mong Trang tới được. Bạn nói giúp tôi câu tôi hy vọng bạn tới được bằng tiếng Anh nhé.')
line(677,6,'"I hope you can come." Tôi hy vọng bạn tới được. Trang báo đứng ở cổng ga. Tôi đem sách ra đó, chỉ kịp nói chuyện vài câu nhưng lần này đã đưa tận tay bạn.')
visual(677,3,'Pink-shirt traveler waits alone beside station gate holding bag and plain phone, no crowd, ticket line or grand family occasion.')
visual(677,4,'Mascot closes a plain book and takes it toward still-closed cafe doorway, phone in pocket; no second waiting teacup.')
visual(677,5,'Mascot pauses at closed cafe doorway with book waiting for reply, pink-shirt friend not yet visible. Upper safe area for target-gap stem.')
visual(677,6,'Both figures meet just outside quiet station gate, mascot hands plain closed book to pink-shirt friend carrying travel bag. No train driver or crowd.')
E['677']['plot_vi']='Trang không chắc tới quán được giữa hai chuyến tàu; tôi hy vọng gặp và chọn mang sách tới gần ga thay vì chỉ chờ bạn đến mình.'
# right: visually check an illustration against same depicted object, no archival/history claims.
line(678,1,'Đức đưa hình, vẫn chờ tôi kiểm. Hai đứa làm tấm thẻ cho hộp đồ dùng. "You\'re right." Bạn đúng. Hình chiếc kéo là hình mình cần dán vào hộp này.')
line(678,2,'Tôi mở hộp cho Đức xem: đồ thật đúng là kéo. Bạn mới làm nhãn lần đầu, sợ dán lẫn như hôm trước. Tôi để bạn tự dán phần vừa chọn, không cầm thay.')
line(678,3,'Bên cạnh còn hai hình cọ vẽ rất giống nhau. Tôi muốn chọn đúng hình cho chiếc cọ nhỏ, cũng không chắc. Đức kéo cọ thật ra đặt cạnh hai tấm để cùng xem.')
line(678,4,'"Is this the right picture?" Đây có phải hình đúng không? Tôi đưa hình cọ nhỏ cho Đức. Cậu so với món trước mặt, chưa trả lời chỉ vì tôi đã chọn.')
line(678,6,'"Is this the right picture?" Đây có phải hình đúng không? Đức gật, chỉ chiếc cọ giống hình. Tôi nhận nhãn bạn dán, giữ phần đó để hôm sau chính mình tìm đồ dễ hơn.')
vs=['Brown-shirt friend holds scissors illustration above box of actual scissors, mascot confirms. Two figures, no archival code or readable label.',
'Mascot opens plain scissors box while friend attaches matching scissors picture to its side, no printed word.',
'Two brush illustrations with different sizes lie beside actual small brush on table, both figures compare them.',
'Mascot holds small-brush picture beside actual small brush for friend to check, no history map or symbols.',
'Brown-shirt friend compares actual brush to small-brush picture, top safe region for target-gap stem.',
'Two boxes bear matching unlabelled scissors and small-brush pictures; mascot accepts friend\'s labelled box, no answer word or certification.']
for s,v in zip(E['678']['scenes'],vs):s['visual_en']=v
E['678']['plot_vi']='Đức ngại dán nhãn sai; tôi xác nhận hình kéo bằng đồ thật, rồi cũng nhờ bạn kiểm hình cọ trước khi nhận hộp đã dán.'
# to: destination relationship remains literal; characters make a choice about walking together.
line(679,1,'Mai chắn ngay lối tôi định rẽ. Bạn tưởng tôi tới chợ như mọi lần. "I\'m going to the park." Tôi đang đi tới công viên. Tôi đưa túi vở cho bạn xem.')
line(679,3,'Mai nhìn hai lối, nói con đường mình đang chọn đi sang chợ. Tôi dừng lại, chưa rẽ, mở mảnh giấy vẽ tuyến. Công viên là điểm tôi muốn tới, không phải chỗ đang đứng.')
line(679,5,'Mai còn tưởng tôi đã đổi nơi hẹn sang chợ. Bạn nói giúp tôi câu tôi đang đi tới công viên bằng tiếng Anh nhé.')
line(679,6,'"I\'m going to the park." Tôi đang đi tới công viên. Mai chỉ lại lối, rồi cất túi giúp để cùng đi một đoạn. Tới cổng, tôi giữ cửa cho bạn vào ngồi học chung.')
visual(679,3,'Two plain paths divide at a fork, one toward tree-lined park gate, the other toward distant low buildings; no signs or readable arrows.')
visual(679,6,'Mascot holds quiet park gate for yellow-shirt friend who carries his shoulder bag; both enter together, no study group or market crowd.')
# in: paper must remain inside the container until the retrieval answer.
line(680,1,'Phong dẹp hộp, cứ tìm trên bàn. Tôi kéo hộp lại: "The paper is in the box." Giấy ở trong hộp. Phong nhìn xuống, chưa mở vì tưởng tôi đã lấy ra rồi.')
line(680,3,'Cậu cần cả bút trước khi mở giấy để khỏi làm bẩn trang. Tôi giữ nguyên hộp, nhờ bạn tìm nốt dụng cụ. Phong nhìn chiếc túi đang treo cạnh chỗ mình cất màu.')
line(680,5,'Phong chưa mở hộp, hỏi giấy đang ở đâu để khỏi lục cả bàn nữa. Bạn nói giúp tôi câu giấy ở trong hộp bằng tiếng Anh nhé.')
line(680,6,'"The paper is in the box." Giấy ở trong hộp. Phong mở hộp lấy giấy, tôi đưa bút vừa thấy trong túi. Cậu đẩy một trang sang cho tôi, rủ cùng vẽ thay vì đứng chờ.')
visual(680,2,'Mascot keeps translucent box on table with paper visible fully inside, grey-shirt friend points toward it. Lid not removed, no paper on easel yet.')
visual(680,3,'Closed translucent box with paper still inside rests on table, friend searches for missing fine brush near plain tote bag. No paper moved out.')
visual(680,6,'Friend opens box and takes blank sheet out while mascot offers brush from tote bag; friend slides second blank sheet toward mascot. Same art table, no ready-made painted result.')
# with: protagonist calls Khoa a friend consistently; keep companion action with no extra bicycle costume.
line(681,1,'Khoa giữ thiệp, chưa cho tôi mang đi. Bạn đã dán từng cánh hoa cùng tôi. "I made it with my friend." Tôi làm nó cùng người bạn, tôi nói khi định ký tên mình.')
line(681,2,'Bạn hỏi sao tôi chỉ ghi một tên nếu hai người cùng làm. Tôi đặt bút xuống, xin thêm tên Khoa bên cạnh. Tấm thiệp dành cho bà tôi, nhưng công của bạn cũng ở đó.')
line(681,3,'Tôi chuẩn bị đem thiệp sang nhà bà, Khoa vẫn đứng ở cửa. Bạn muốn đi để tự đưa phần mình làm, nhưng ngại đây là người nhà của tôi. Tôi chờ bạn nói trước.')
line(681,4,'"Can I go with you?" Tôi đi cùng bạn được không? Khoa hỏi. Tôi gật đầu, đưa thiệp cho bạn giữ. Hai người cùng đi như đã cùng làm, bạn đâu phải ở lại chờ.')
line(681,6,'"Can I go with you?" Tôi đi cùng bạn được không? Tôi mở cổng, nhường Khoa bước cùng. Bạn giữ thiệp, tôi giữ phong bì; không ai phải cầm phần quà ấy một mình.')
E['681']['custom_visible_text']=[{'text':'Tôi và Khoa','placement':'small signature line inside handmade card','object':'handmade card'}]
visual(681,1,'Orange-shirt friend holds decorated dried-flower card back from mascot, who has pen ready at blank signature line. No readable text yet.')
visual(681,2,'Mascot writes permitted Tôi và Khoa on inside signature line of handmade card while friend watches. No other written greeting or name.')
visual(681,3,'Mascot waits at open home doorway holding blank envelope, friend stands uncertainly with dried-flower card. No extra cap or bicycle outfit.')
visual(681,6,'Both figures walk out through garden gate together, friend holds decorated card and mascot holds blank envelope. Two people only; no grandmother shown.')
E['681']['plot_vi']='Khoa muốn việc cùng làm thiệp được ghi nhận; tôi thêm phần bạn, đồng ý cùng đem thiệp tới nhà bà thay vì tự đi.'
for e in E.values():
 s=e['scenes'][4];s['stem']=s['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Local publisher must substitute the actual teaching inflection where specified.
p=Path(__file__).parent/'review.py';s=p.read_text().replace("answer=s['stem'].replace('___',m['word'])","answer=s['stem'].replace('___',e.get('teaching_form',m['word']))");p.write_text(s)
