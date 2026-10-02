from pathlib import Path
import json
P=Path(__file__).parent/'410-419';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def patch(num,lines=None,plot=None,title=None):
 e=E[str(num)]
 if lines:
  for s,n in zip(e['scenes'],lines):s['narration']=n
 if plot:e['plot_vi']=plot
 if title:e['title']=title
 return e
patch(652,[
'Tôi giấu chiếc hộp sau lưng. Linh chuyển nhóm hôm nay, đang dọn nốt bàn. "I have a present for you." Tôi có một món quà cho bạn.',
'Linh bảo đừng tốn tiền vì mình, định đẩy hộp lại. Tôi mở nắp, cho cô thấy cây bút cô từng nhắc. Tôi đã chọn nó khi biết bạn sắp chuyển chỗ.',
'"Do you like the present?" Bạn có thích món quà không? Tôi hỏi, hơi ngập ngừng. Linh cầm bút, thử đặt vào gáy sổ đang mang theo.',
'Cô bảo sợ nhận rồi không còn dịp giúp tôi việc chung. Tôi nói món quà chỉ để cô nhớ mình từng làm cùng, đâu phải lời hẹn trả lại thứ gì.',
'Linh hỏi tôi chắc muốn tặng cô chứ. Bạn giúp tôi nói câu tôi có một món quà cho bạn bằng tiếng Anh nhé.',
'"I have a present for you." Tôi có một món quà cho bạn. Linh cất bút vào sổ. Ra đến cửa, cô mở lại sổ, ghi chỗ mới để tuần sau tôi ghé chơi.'
],plot='Linh ngại nhận quà trước khi chuyển nhóm; tôi giải thích món quà là kỷ niệm, cô nhận và ghi chỗ mới để tôi ghé.')
E['652']['scenes'][0]['visual_en']='Mascot stands holding small tied gift box behind back near nearly empty office desk, orange-shirt coworker packs a closed notebook.'
E['652']['scenes'][1]['visual_en']='Coworker gently pushes gift box back with a hesitant gesture while mascot opens it to reveal one plain wooden pen.'
E['652']['scenes'][3]['visual_en']='Coworker holds pen by closed notebook hesitantly, mascot speaks with an open reassuring gesture; no shirt pocket or printed labels.'
E['652']['scenes'][5]['visual_en']='At office doorway, coworker opens notebook and writes non-letter strokes with gifted pen to share her new location; mascot stands beside her. No readable address or extra person.'
patch(653,[
'Tôi chỉ đủ tiền mua một tệp giấy. Bình lại muốn tôi chọn cùng cậu. "What type of paper do you need?" Bạn cần loại giấy nào? Tôi đưa hai tệp ra.',
'Một tệp mặt nhám, một tệp mặt láng. Bình muốn vẽ chung ngoài trời cuối tuần. Tôi thích giấy láng, nhưng cậu đưa tay giữ tệp nhám lâu hơn.',
'"I need this type of paper." Tôi cần loại giấy này. Bình chỉ tệp nhám, kể mình đã quen dùng nó trong buổi học. Cậu chưa yêu cầu tôi phải mua theo.',
'Tôi nhớ đã hẹn mang giấy để cả hai cùng vẽ. Tôi đặt tệp láng trở lại, nhưng vẫn chờ Bình nói rõ trước khi chọn. Cậu nhìn tôi, hỏi có muốn đổi ý không.',
'Tôi muốn nghe loại giấy Bình cần thêm một lần cho chắc. Bạn nói giúp tôi câu bạn cần loại giấy nào bằng tiếng Anh nhé.',
'"What type of paper do you need?" Bạn cần loại giấy nào? Bình chỉ lại tệp nhám. Tôi đặt nó vào giỏ, bảo cuối tuần cậu phải ngồi vẽ cùng tôi đấy.'
],plot='Tôi chỉ mua được một tệp giấy để hai bạn vẽ chung; hỏi loại Bình cần, tôi chọn theo bạn và giữ lời hẹn cùng vẽ.')
E['653']['scenes'][0]['visual_en']='Mascot holds two unlabelled paper pads at art shelf, green-shirt friend watches. Closed small coin purse beside mascot, no prices.'
E['653']['scenes'][2]['visual_en']='Green-shirt friend touches rough surface of one unlabelled paper pad, mascot holds the smooth pad separately. No claims printed on labels.'
E['653']['scenes'][3]['visual_en']='Mascot puts smooth pad back on shelf while rough pad remains held between both friends, shopping basket empty.'
E['653']['scenes'][4]['visual_en']='Both friends remain at paper shelf choosing between the same unlabelled pads, no brush aisle; upper safe region for practice stem.'
E['653']['scenes'][5]['visual_en']='Mascot places rough pad inside basket while green-shirt friend smiles and keeps one plain pencil ready for their shared drawing plan. No cashier.'
patch(654,[
'An đưa miệng sát nến, định thổi luôn. Tôi giữ điện thoại: "Look at the fire." Nhìn ngọn lửa nhé. Tôi còn chưa chụp bánh sinh nhật cho em.',
'Tôi làm chiếc bánh nhỏ, viết tên em không được đẹp nên cứ chậm chụp. An đã chờ từ chiều, chỉ muốn ăn cùng tôi. Em nhìn nến, đợi tôi đặt máy xuống.',
'"The fire is small." Ngọn lửa nhỏ. Tôi nhìn đốm sáng trên cây nến duy nhất, nghe em bảo chụp bây giờ được rồi. Lửa ở đó là ngọn đang cháy, không phải hình trang trí.',
'Tôi thôi chỉnh bánh, đưa máy cho An xem góc hình. Em gật, ngồi lại cạnh tôi. Bức ảnh sẽ có cả chiếc bánh hơi lệch mà tôi đã tự làm.',
'An chưa chú ý vào cây nến trong lúc tôi chuẩn bị chụp. Bạn nói giúp tôi câu nhìn ngọn lửa bằng tiếng Anh nhé.',
'"Look at the fire." Nhìn ngọn lửa nhé. Tôi chụp xong, An mới thổi nến. Em đưa tôi miếng bánh đầu tiên, giữ lại tấm ảnh tôi cứ ngại chụp.'
],plot='Tôi ngại chụp bánh tự làm chưa đẹp; An chờ bên ngọn nến nhỏ, giúp tôi giữ cả kết quả chưa hoàn hảo trong ảnh.',title='Đốm lửa trên chiếc bánh')
vs=['Mascot holds plain phone beside brown-shirt sibling seated at birthday table with one small uneven cake and one lit candle. No stove, fuel or printed name.',
'Sibling waits beside same uneven cake, mascot holds phone low hesitating; only one small candle flame.',
'Close view of single small candle flame on plain uneven cake, both figures look at it from seated distance. No match lighting or hands near flame.',
'Mascot shows phone framing to sibling, screen away from viewer, cake and candle unchanged.',
'Mascot asks sibling to look toward single candle, phone prepared at side, top safe area for stem.',
'Candle extinguished after photo, sibling offers mascot first cake slice beside whole uneven cake. Phone lies face down, no written music or labels.']
for s,v in zip(E['654']['scenes'],vs):s['visual_en']=v
E['654']['scenes'][4]['stem']='Look at the ___.'
patch(655,[
'Huy đưa thêm chậu, tôi vẫn giữ tay. Chúng tôi đã dọn gần xong sân. "I need a rest." Tôi cần nghỉ một chút. Cậu ngạc nhiên vì tôi ít khi dừng trước.',
'Tôi muốn giúp Huy xếp vườn trước khi mẹ cậu về. Nhưng tay đã mỏi, tôi cần ngồi xuống. Một quãng nghỉ ở đây là lúc dừng làm để nghỉ ngơi, chưa bỏ việc chung.',
'Huy định làm nốt một mình. Tôi giữ hai chiếc ghế: "Let\'s have a rest." Chúng ta nghỉ một chút nhé. Cậu nhìn chậu cuối, rồi đặt nó xuống cạnh sân.',
'Hai đứa ngồi dưới hiên, uống nước. Huy bảo mình sợ tôi chờ lâu sẽ bực. Tôi lắc đầu, rủ cậu ngắm hàng cây vừa xếp, chưa cần đi đâu.',
'Huy đưa bình tưới, hỏi tôi có muốn làm tiếp ngay không. Bạn nói giúp tôi câu tôi cần nghỉ một chút bằng tiếng Anh nhé.',
'"I need a rest." Tôi cần nghỉ một chút. Huy để bình xuống, ngồi lại cạnh tôi. Chậu cuối vẫn đợi, còn chiếc ghế tôi kéo cho cậu đã có người ngồi.'
],plot='Huy muốn hoàn thành vườn ngay, còn tôi cần một quãng nghỉ và rủ cậu dừng cùng thay vì làm nốt một mình.')
E['655']['scenes'][1]['visual_en']='Mascot puts down watering can and indicates the stool under porch, yellow-shirt friend holds one remaining pot with puzzled posture.'
E['655']['scenes'][3]['visual_en']='Both figures sit on stools under porch with glasses of water; one final unplaced pot waits on courtyard edge, no claim all work done.'
E['655']['scenes'][5]['visual_en']='Yellow-shirt friend has put watering can aside and sits again beside mascot; remaining pot still waits on ground. No fan needed.'
patch(656,[
'Mai giữ rèm, không dám kéo lên. Tiếng cọ cứ vang ngoài kính. "What is that sound?" Âm thanh đó là gì? Tôi hỏi, dừng bút nhìn theo bạn.',
'Mai nghĩ có người gõ cửa. Tôi nghe tiếng lặp lại ở mép kính, chưa chắc. Mai không muốn một mình lại gần, tôi đứng lên cùng để xem.',
'"I hear a strange sound." Tôi nghe một âm thanh lạ. Mai nói với tôi, chỉ rèm cửa. Hai đứa nghe thêm rồi mới kéo rèm, không phải đoán từ bức hình bên ngoài.',
'Một cành hoa giấy đang chạm kính khi gió lay. Mai cười, buông vai xuống. Tôi định quay về học, nhưng bạn muốn giữ cửa mở để căn phòng có gió.',
'Tiếng cọ lại vang khi Mai kéo rèm xuống. Bạn giúp tôi nhắc câu hỏi âm thanh đó là gì bằng tiếng Anh nhé.',
'"What is that sound?" Âm thanh đó là gì? Mai chỉ cành cây, gài nó sang bên. Tôi giữ rèm cho bạn mở cửa; hai đứa về bàn, vẫn có gió mà không còn tiếng cọ.'
],plot='Mai ngại tiếng lạ ngoài kính nên tôi cùng xem; tìm ra cành hoa, chúng tôi giữ cửa mở mà loại bỏ tiếng cọ.')
E['656']['scenes'][0]['visual_en']='Purple-shirt friend hesitates holding closed curtain edge at study-room window, mascot looks up from desk. No intruder or sound lettering.'
E['656']['scenes'][1]['visual_en']='Mascot stands beside hesitant friend at window so they can inspect together, curtain still closed.'
E['656']['scenes'][5]['visual_en']='Mascot holds curtain aside while friend secures flower branch beside railing away from window; window open, branch no longer touches glass. No realistic fingers.'
E['656']['extra_visual_states']=[{'quote':'hai đứa về bàn, vẫn có gió mà không còn tiếng cọ.','visual_en':'Same room after branch has been moved: both figures sit back at study table, window remains open and branch visible safely to one side.','purpose_en':'Show the local consequence after stopping the rubbing sound without closing the window.'}]
patch(657,[
'Nam tìm túi, tôi thấy khóa dưới ghế. "It is on the ground." Nó ở trên mặt đất. Chùm khóa nằm cạnh chân ghế, không còn ở trong túi bạn.',
'Nam định ngồi hẳn xuống cỏ để lấy. Tôi thấy chỗ ấy còn ướt, nhắc: "Do not sit on the ground." Đừng ngồi xuống mặt đất. Tôi đưa tay để bạn tựa.',
'Cậu không muốn làm bẩn quần nhưng cũng sợ khóa rơi lẫn trong cỏ. Tôi giữ túi giúp, để cậu cúi xuống tìm. Khóa vẫn ở nguyên chỗ vừa thấy.',
'Nam đưa mắt nhìn chân ghế bên kia, chưa nhận ra nó. Tôi chỉ lại miếng cỏ sát lối đi. Cậu nhìn theo tay tôi, không tiếp tục lục túi nữa.',
'Nam hỏi chùm khóa nằm ở đâu trước khi nhặt. Bạn nói giúp tôi câu nó ở trên mặt đất bằng tiếng Anh nhé.',
'"It is on the ground." Nó ở trên mặt đất. Nam lấy được khóa, tôi đưa túi lại. Cậu rủ tôi ngồi cùng trên ghế; lần này móc khóa nằm riêng trong lòng bàn tay.'
],plot='Nam tìm chìa khóa và muốn ngồi xuống cỏ ướt; tôi giúp bạn nhận vị trí trên mặt đất và lấy được khóa trước khi hai người nghỉ cùng.')
E['657']['scenes'][2]['visual_en']='Mascot holds friend\'s bag while red-shirt friend bends toward key ring still on grass beside bench. Key not yet picked up.'
E['657']['scenes'][3]['visual_en']='Red-shirt friend looks under wrong bench leg, mascot points to key at grass edge beside path. Stone bench remains same; no dry wooden bench swap.'
E['657']['scenes'][4]['visual_en']='Red-shirt friend pauses crouching before retrieving key, mascot points down. Key remains visible on ground for accurate practice statement.'
patch(658,[
'Hà đẩy tờ rơi lại cho tôi. Bạn tưởng lớp chỉ học ban ngày. "This course starts in June." Khóa học này bắt đầu tháng Sáu. Tôi giữ giấy để cùng đọc lại.',
'Tôi muốn học làm gốm với bạn, nhưng Hà còn đi làm. Khóa học có nhiều buổi để học dần, chưa phải buổi đến thử một lần. Tôi chỉ phần lịch tối Hà vừa bỏ qua.',
'Hà đọc lại, nói: "I like this course." Tôi thích khóa học này. Bạn thích những buổi làm bát rồi tách, nhưng vẫn ngại mình không theo kịp.',
'Tôi cũng chưa từng làm. Tôi đề nghị ngồi cùng bàn buổi đầu, để hai đứa thử thay vì chờ biết rồi mới đăng ký. Hà lấy bút, vẫn hỏi tháng bắt đầu lần nữa.',
'Bạn nói giúp tôi câu khóa học này bắt đầu tháng Sáu bằng tiếng Anh nhé. Hà muốn chắc phần thời gian trước khi điền tên.',
'"This course starts in June." Khóa học này bắt đầu tháng Sáu. Hà nhận một phiếu, đưa tôi phiếu còn lại. Chúng tôi cất hai tờ cùng chỗ để tới buổi đầu cùng nhau.'
],plot='Hà ngại khóa học không hợp giờ làm và chưa có kinh nghiệm. Tôi chỉ lịch tối, rủ ngồi cùng buổi đầu để cả hai cùng thử.')
E['658']['custom_visible_text']=[{'text':'June','placement':'small schedule box on brochure','object':'course brochure'}]
E['658']['scenes'][1]['visual_en']='Mascot points to permitted June schedule label beside simple moon icon on course brochure, teal-shirt friend examines it. No invented dates or class counts.'
E['658']['scenes'][2]['visual_en']='Teal-shirt friend reads brochure containing permitted June label and simple bowl-and-cup icons only. No printed syllabus paragraphs.'
E['658']['scenes'][3]['visual_en']='Two figures each take a blank application sheet and plain pencil at table, looking at each other uncertainly; brochure remains between them.'
E['658']['scenes'][4]['visual_en']='Teal-shirt friend pauses with pen above blank application, looking toward mascot beside same brochure. Top safe region for target-gap stem.'
patch(659,[
'Đức giữ hộp bánh, không bước vào. Bạn tưởng mình đến sớm quá. "Welcome to the party." Chào mừng bạn đến bữa tiệc. Tôi mở cửa rộng hơn, mời bạn vào.',
'Nhà mới của tôi còn nhiều thùng chưa dọn. Tôi chỉ mời một người, sợ phòng trống sẽ buồn. Đức nhìn hai chiếc đĩa, hỏi có cần chờ ai nữa không.',
'"The party is ready." Bữa tiệc đã sẵn sàng. Tôi nói, kéo ghế cho bạn. Đây là buổi nhỏ mừng tôi chuyển nhà, có bánh và hai người cùng ngồi, vậy là đủ với tôi.',
'Đức đặt hộp bánh xuống, vẫn định đứng giúp dọn thùng. Tôi giữ chiếc ghế: hôm nay cậu là khách. Bạn nhìn tôi rồi ngồi, để hộp gần mép bàn cho tôi mở.',
'Đức hỏi thật sự bữa tiệc nhỏ này dành để đón mình à. Bạn nói giúp tôi câu chào mừng bạn đến bữa tiệc bằng tiếng Anh nhé.',
'"Welcome to the party." Chào mừng bạn đến bữa tiệc. Đức cười, chia bánh vào hai đĩa. Thùng vẫn ở góc phòng; lần đầu bàn nhà tôi có người ngồi phía đối diện.'
],plot='Đức tưởng bữa tiệc còn phải chờ khách khác, tôi mời bạn ngồi ngay giữa nhà chưa dọn xong và giữ một buổi nhỏ dành cho hai người.')
E['659']['scenes'][0]['visual_en']='Grey-shirt friend stands hesitant at apartment doorway holding a plain cake box, mascot opens the door toward him. Stacked moving cartons in corner.'
E['659']['scenes'][2]['visual_en']='Mascot pulls one of two chairs from a small table with two empty plates, friend holds cake box just inside doorway. No additional guest or labels.'
E['659']['scenes'][3]['visual_en']='Friend reaches toward a moving carton to help, mascot indicates the waiting chair instead. Cake box stays on table unopened.'
E['659']['scenes'][4]['visual_en']='Grey-shirt friend pauses beside waiting chair asking mascot, no tea pouring or completed meal yet; upper safe area for practice stem.'
E['659']['scenes'][5]['visual_en']='Both figures sit opposite each other at small table as friend divides plain cake onto two plates; moving cartons remain unfinished in corner.'
patch(660,[
'Thảo gạch lịch, tôi giữ trang lại. Bạn đã xếp cả ngày kín việc. "What is our plan?" Kế hoạch của chúng ta là gì? Tôi muốn nghe trước khi nhận lời.',
'Thảo kể muốn trả sách rồi cùng đi bảo tàng. Tôi nhắc đã hẹn giúp bác dọn một góc nhà. Nếu giữ tất cả, hai đứa chẳng còn buổi ngồi chơi như đã hứa.',
'Thảo đặt bút xuống, hỏi tôi muốn giữ việc nào. Tôi rủ trả sách trước, giúp bác rồi để bảo tàng sang dịp khác. Bạn khoanh lại ít việc hơn.',
'"This is a good plan." Đây là một kế hoạch tốt. Tôi nhìn thứ tự vừa chọn. Thảo cũng giữ một khoảng trống để hai đứa ăn cùng, không thêm giờ xe vào ngay.',
'Bạn gấp sổ rồi hỏi tôi có nhớ phần hai người vừa thống nhất không. Bạn nói giúp tôi câu kế hoạch của chúng ta là gì bằng tiếng Anh nhé.',
'"What is our plan?" Kế hoạch của chúng ta là gì? Thảo nhắc những việc đã giữ lại. Tôi cất sổ cùng sách phải trả, để hôm sau không tự thêm một cuộc hẹn khác.'
],plot='Thảo muốn làm quá nhiều việc trong ngày cùng tôi. Hai người nói rõ nhu cầu, bỏ bớt một nơi để giữ lời giúp bác và buổi ăn chung.')
E['660']['scenes'][2]['visual_en']='Pink-shirt friend puts pen down and asks mascot over a planner with abstract non-legible marks, no numbers or bullet list of three claimed actions.'
E['660']['scenes'][3]['visual_en']='Both figures look at planner with fewer abstract marks and one visible blank region, mascot nods to the shared choice. No timetable text.'
patch(661,[
'Phong cất vé, định kéo tôi về. Cậu tưởng tới sai buổi vì sân khấu còn đóng. "When does the show start?" Chương trình biểu diễn bắt đầu khi nào? Tôi hỏi.',
'Phong mua vé để tôi nghe cùng, nhưng giờ ngại mình nhớ nhầm. Tôi xin xem lại vé. Chương trình biểu diễn có giờ bắt đầu, chưa thấy diễn không có nghĩa đã lỡ mất.',
'"The show starts at seven." Chương trình bắt đầu lúc bảy giờ. Tôi đọc cho bạn nghe. Hai người tới sớm một chút; Phong nhìn sân khấu, chưa yên tâm ngồi.',
'Tôi kéo ghế cạnh bạn, đưa vé lại. Tôi muốn ở lại nghe cùng, đâu cần hôm nay mọi thứ đúng như cậu đoán. Phong ngồi xuống, giữ cho tôi chiếc ghế sát bên.',
'Phong hỏi liệu giờ mình vừa đọc có đúng không. Bạn nói giúp tôi câu chương trình bắt đầu lúc bảy giờ bằng tiếng Anh nhé.',
'"The show starts at seven." Chương trình bắt đầu lúc bảy giờ. Đèn sân khấu bật, Phong cất vé. Tôi ngồi ngay chỗ bạn giữ, cùng chờ phần mở màn sau tấm rèm.'
],plot='Phong ngại mua nhầm buổi và muốn về khi sân khấu đóng; tôi kiểm giờ bảy giờ, chọn ngồi lại bên bạn để cùng chờ mở màn.')
E['661']['custom_visible_text']=[{'text':'7:00','placement':'small start-time field at lower ticket corner','object':'show ticket'}]
E['661']['scenes'][0]['visual_en']='Slate-shirt friend closes ticket wallet and starts to turn away from a curtained small stage; mascot stops beside him with an asking gesture. Two people only.'
E['661']['scenes'][2]['visual_en']='Mascot points to permitted 7:00 printed in ticket corner, slate-shirt friend reads alongside; blank stage curtain behind them.'
E['661']['scenes'][5]['visual_en']='Two friends sit next to each other facing closed red stage curtain as stage lights turn on; no performers or audience extras visible.'
E['661']['scenes'][4]['stem']='The ___ starts at seven.'
for e in E.values():
 s=e['scenes'][4];s['stem']=s['stem'].replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
