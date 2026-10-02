from pathlib import Path
import json
P=Path(__file__).parent/'470-479';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def line(n,i,t):E[str(n)]['scenes'][i-1]['narration']=t
def vis(n,i,t):E[str(n)]['scenes'][i-1]['visual_en']=t
# That: far umbrella stays away from narrator until after response.
line(712,1,'Nam lấy ô đen ngay gần cửa. Tôi chỉ chiếc vàng ở đầu dãy xa: "That umbrella is mine." Chiếc ô đó là của tôi. Bạn dừng lại, nhìn theo tay tôi.')
line(712,2,'Chiếc vàng là món Nam tặng tôi hồi mới cùng đi học. Bạn tưởng tôi đã thay chiếc khác, cứ đưa ô đen cho tiện. Tôi lắc đầu, muốn giữ món mình vẫn đang dùng.')
line(712,3,'"Can you get that umbrella?" Bạn lấy giúp chiếc ô đó được không? Tôi nhờ Nam khi chiếc vàng còn ở xa mình. Bạn đi tới đầu dãy, không lấy món gần nhất nữa.')
line(712,4,'Nam lấy ô vàng xuống nhưng vẫn đứng bên giá. Bạn nhìn quai cũ, nhớ chiếc mình đã chọn. Tôi chờ ở cửa, muốn bạn thấy mình còn giữ món ấy, không phải chỉ dùng vì trời mưa.')
line(712,5,'Nam cầm ô ở đầu dãy, hỏi có đúng chiếc tôi muốn không. Bạn nói giúp tôi câu chiếc ô đó là của tôi bằng tiếng Anh nhé.')
line(712,6,'"That umbrella is mine." Chiếc ô đó là của tôi. Nam mang chiếc vàng tới, hai đứa mở cùng. Ra cửa, bạn giữ một bên quai túi cho tôi, vẫn đi cạnh chiếc ô mình từng tặng.')
E['712']['plot_vi']='Nam định lấy ô gần nhất, tôi muốn chiếc ở xa bạn từng tặng; bạn nhớ món cũ và cùng dùng nó ra về.'
vis(712,3,'Mascot remains at hallway door while grey-shirt friend walks toward yellow umbrella at far end of a low accessible rack. Black umbrella remains near door, no climbing.')
vis(712,4,'Friend holds yellow umbrella beside far rack and examines old handle, mascot stays by door several steps away. Umbrella not yet handed to narrator.')
vis(712,5,'Grey-shirt friend asks while holding yellow umbrella at far rack, mascot points from doorway. Clear distance remains for that; upper safe region for stem.')
# These: two close books, actual transfer after answer only.
line(713,1,'Linh giữ sách, chưa chịu đem ra kệ. Tôi chạm hai cuốn gần tay: "These books are new." Những cuốn sách này mới. Bạn định cất riêng vì chưa ai đọc.')
line(713,2,'Hai cuốn ấy do nhóm cũ để lại cho góc đọc chung. Linh sợ mở ra sẽ nhanh cũ, muốn dùng chồng cũ trước. Tôi giữ sách ở ngay trước mặt mình, xin bạn nghe lý do chọn.')
line(713,3,'"I need these books." Tôi cần những cuốn sách này. Tôi muốn người tới góc đọc được xem cả phần mới, không phải tìm mãi ở ngăn khóa. Linh nhìn chỗ trống mình đã chừa.')
line(713,4,'Bạn lấy thêm một chiếc kê sách để đỡ hai cuốn, chưa mang đi. Tôi nhận giữ một cuốn, Linh giữ cuốn còn lại bên cạnh. Lần này không ai đẩy cả chồng vào tủ trước.')
line(713,6,'"I need these books." Tôi cần những cuốn sách này. Linh giúp tôi đặt hai cuốn lên kệ. Bạn mở một trang ở cuốn mình giữ, chọn chỗ để người tới sau thấy ngay.')
E['713']['plot_vi']='Linh muốn giữ riêng sách mới, tôi xin hai cuốn gần tay cho góc đọc chung; bạn cùng đặt lên kệ và chọn trang để người tới thấy.'
vis(713,1,'Mascot touches exactly two crisp books close to his hands, yellow-shirt friend hesitates holding cupboard key. Old books farther across table.')
vis(713,4,'Each friend holds one of same two new books close together above table, small plain bookend waiting nearby. Neither book shelved yet.')
vis(713,5,'Friend asks mascot about the two books still held close between them, shelf remains waiting behind. Top safe region for stem.')
# Those: distant pair persists until post-answer move; no inference of reserved status from bags.
line(714,1,'Huy giữ bàn, chưa muốn lấy ghế cũ. Tôi chỉ hai chiếc phía xa: "Those chairs are empty." Những chiếc ghế đó đang trống. Bàn hai người vẫn chưa có chỗ ngồi.')
line(714,2,'Đó là ghế Huy giữ ở phòng này, nhưng cậu ngại mình đã kê chúng vào góc. Tôi xin kéo lại để ngồi học cùng, không cần ngồi bệt hoặc mua thêm chiếc khác.')
line(714,3,'"Can we use those chairs?" Mình dùng những chiếc ghế đó được không? Tôi hỏi Huy từ cạnh bàn, chỉ đúng hai chiếc ở xa. Bạn nhìn lại góc từng dùng để đọc một mình.')
line(714,4,'Huy định bảo tôi chọn ghế mới ở phòng ngoài. Tôi rủ dùng chỗ cậu quen, rồi sẽ kê lại nếu cần. Bạn đặt vở ở giữa bàn, vẫn chưa nhấc ghế khỏi góc.')
line(714,5,'Huy hỏi tôi muốn dùng đúng cặp ghế nào. Bạn nói giúp tôi câu mình dùng những chiếc ghế đó được không bằng tiếng Anh nhé.')
line(714,6,'"Can we use those chairs?" Mình dùng những chiếc ghế đó được không? Huy gật. Mỗi người mang một chiếc về bàn, cậu nhận chiếc thường ngồi; tôi mở vở ở chỗ mới cạnh bạn.')
E['714']['plot_vi']='Huy ngại dùng cặp ghế cũ của mình ở xa, tôi xin kéo lại để giữ buổi học chung trong góc bạn quen.'
vis(714,2,'Both figures remain at study table without chairs, two owned wooden chairs visible at far wall; no bags or reservation tags on seats.')
vis(714,3,'Mascot points from same table toward exactly two far chairs while navy-shirt owner considers request; neither person approaches chairs yet.')
vis(714,4,'Navy-shirt friend places closed notebook at table center, far chair pair still untouched. No carrying or status inferred from lack of bags.')
vis(714,5,'Both stay beside table asking about distant pair, top safe area for target-gap stem. No chair held near narrator before those response.')
vis(714,6,'Each friend carries one of the same two chairs from far corner toward table, notebooks ready. No extra student or third chair.')
# All: complete finite set of FOUR distinct picture cards, no undeclared letter tiles.
line(715,1,'Phong gập hộp, tôi còn nhìn gầm bàn. "Are all the cards here?" Tất cả thẻ có ở đây không? Bộ của hai đứa có bốn hình, tôi chưa thấy chiếc thuyền.')
line(715,2,'Bạn muốn về ngay, bảo hôm sau tìm cũng được. Tôi nhớ bộ này Phong mang cho mình mượn, không muốn trả thiếu. Tôi mở khăn bàn, Phong đợi với hộp còn mở.')
line(715,3,'Tôi nhặt thẻ thuyền, đặt cạnh hình tròn, hoa và lá. "I checked all the cards." Tôi kiểm tra tất cả thẻ rồi. Cả bốn đều đã có, không chỉ một phần của bộ.')
line(715,4,'Phong đẩy hộp sang cho tôi tự xếp, nhưng vẫn giữ nắp giúp. Tôi đặt bốn hình vào cùng ngăn, không để lại chiếc mình vừa tìm dưới khăn bàn nữa.')
line(715,6,'"Are all the cards here?" Tất cả thẻ có ở đây không? Phong chỉ từng hình rồi gật. Tôi đóng hộp, trả bạn; Phong để lại trên bàn, bảo buổi sau hai đứa chơi tiếp.')
E['715']['plot_vi']='Phong muốn về, tôi giữ lại tìm thẻ cuối vì không muốn trả thiếu bộ mượn; bạn đợi, rồi để bộ đủ bốn hình lại cho buổi chơi sau.'
vs=['Green-shirt friend starts closing plain storage box while mascot looks beneath table; three picture cards show circle, flower, leaf; fourth boat card missing.',
'Mascot lifts cloth edge while friend keeps empty box open, three known picture cards remain on table. No letters or fifty-card claim.',
'Mascot places recovered boat card beside circle, flower and leaf cards, all four visible distinctly. No words or numbers on cards.',
'Mascot packs same four picture cards into one open box while friend holds lid aside.',
'Friend holds open box showing four picture cards, asks mascot to verify complete set; top safe area for stem.',
'Mascot closes complete box and returns it to friend, who puts it back at table center for another meeting. No trophy or handwriting.']
for s,v in zip(E['715']['scenes'],vs):s['visual_en']=v
# No: local paper absence remains true while old paper is available elsewhere.
line(716,1,'Mai mở hộp, tôi lục ngăn kéo. "There is no paper in the drawer." Không có giấy trong ngăn kéo. Chỉ có hai chiếc kẹp, chưa thứ gì để hai người vẽ.')
line(716,3,'"There are no cards in this box." Không có thẻ trong hộp này. Mai cho tôi xem đáy trống. Tôi định thôi buổi vẽ, bạn vẫn giữ bút chưa muốn cất.')
line(716,4,'Mai lấy tờ lịch đã dùng xong, xoay mặt trắng ra. Bạn hỏi thử vẽ ở đây được không. Tôi nhìn ngăn kéo vẫn chưa có giấy, rồi kéo ghế lại thay vì đóng hết đồ.')
line(716,5,'Mai hỏi trong ngăn kéo có còn giấy nào không trước khi dùng lịch cũ. Bạn nói giúp tôi câu không có giấy trong ngăn kéo bằng tiếng Anh nhé.')
line(716,6,'"There is no paper in the drawer." Không có giấy trong ngăn kéo. Tôi đặt tờ lịch lên bàn, mặt trắng quay lên. Mai nhận một bên, tôi nhận bên kia; buổi vẽ vẫn bắt đầu bằng thứ hai người tìm được.')
E['716']['scenes'][4]['stem']='There is ___ paper in the drawer.';E['716']['plot_vi']='Không có giấy trong ngăn kéo hay thẻ trong hộp, tôi muốn thôi vẽ; Mai giữ bút và rủ dùng mặt trắng lịch cũ để hai người tiếp tục.'
vis(716,4,'Orange-shirt friend unfolds used calendar with entirely blank reverse facing viewer, mascot draws stool closer. No legible dates or thickness/material guarantee.')
# Very: mutual help is offered, no guaranteed mechanical safety or straining body detail.
line(717,1,'Đức ôm thùng, không muốn tôi phải giúp. "This box is very big." Chiếc hộp này rất to. Tôi đứng cạnh, thấy nó chiếm gần hết khoảng trước bàn hai người.')
line(717,3,'Đức nhấc thử rồi đặt xuống: "It is very heavy." Nó rất nặng. Bạn mới nhận sách của mình, ngại nhờ tôi mang vì tôi đã dọn góc phòng từ sáng.')
line(717,4,'Tôi chỉ chỗ cả hai đang muốn ngồi, đề nghị chuyển cùng một đoạn. Đức đưa tôi một quai, không giữ cả việc về mình nữa. Chúng tôi dừng ở đây để chọn chỗ đặt trước.')
line(717,6,'"This box is very big." Chiếc hộp này rất to. Hai người cùng chuyển sang góc bên, rồi Đức kéo ghế cho tôi. Tôi chọn một cuốn sách mới tới, không còn đứng giữ cả thùng chắn trước bàn.')
vis(717,3,'Olive-shirt friend sets large book-filled cardboard box down after trying to lift; mascot offers help nearby. No slipping, injury, muscles or anatomical fingers.')
vis(717,4,'Both figures hold opposite handles of a cardboard box still resting on floor while deciding corner position. No airborne heavy crate before practice.')
vis(717,6,'Large cardboard box now rests at side corner, olive-shirt friend pulls chair for mascot, who selects one plain book from open box. No safety certification or wood machinery.')
# Just: recent arrival and request to restart current shared reading, paired question-answer timing.
lines=[
'Vy giữ vở, tưởng tôi đã học từ trước. Tôi mới bước tới bàn. "Did you just get here?" Bạn vừa mới tới đây à? Vy hỏi khi thấy tôi chưa cất túi.',
'Bạn đã đọc tới giữa bài, muốn tôi tiếp ngay phần đang dở. Tôi ngồi xuống, nhìn trang đó mà chưa hiểu đầu chuyện. Tôi giữ túi, xin Vy chờ nghe mình nói trước.',
'"I just arrived." Tôi vừa mới tới. Tôi báo sự việc mới xảy ra ngay trước lúc hai người nói, để bạn biết tôi chưa nghe phần đã đọc lúc mình còn chưa ở đây.',
'Vy đặt bút xuống, lật lại trang đầu. Tôi thôi giữ túi, cùng xem chỗ bắt đầu. Bạn không phải bỏ bài, chỉ dành một chút để cả hai theo cùng phần.',
'Vy hỏi vì sao tôi chưa theo được đoạn giữa bạn vừa đọc. Bạn nói giúp tôi câu tôi vừa mới tới bằng tiếng Anh nhé.',
'"I just arrived." Tôi vừa mới tới. Vy trượt vở về giữa bàn, chỉ trang đầu. Tôi mở túi lấy bút; bạn chờ tôi xong rồi hai người mới đọc tiếp cùng nhau.'
]
for s,n in zip(E['718']['scenes'],lines):s['narration']=n
E['718']['selected_gloss_vi']='vừa mới xảy ra';E['718']['plot_vi']='Vy muốn tôi đọc tiếp ngay đoạn giữa, tôi nói mình vừa mới tới; bạn quay về đầu để cả hai theo cùng phần.';E['718']['title']='Quay lại trang đầu'
vis(718,1,'Mascot arrives beside lavender-shirt friend at study table with bag still over shoulder; friend holds open notebook mid-page and asks about recent arrival.')
vis(718,3,'Mascot sits with bag still on shoulder beside friend explaining arrival, no mug or cold-cure gesture.')
vis(718,4,'Friend turns notebook back toward beginning while mascot lowers bag to floor, both preparing to read together. No warm drink needed.')
# Only: original thick stack vs two remaining contradiction removed, exactly THREE initial cards.
line(719,1,'Hoàng đưa cả ba thẻ qua bàn. Tôi chỉ muốn giữ phần lượt mình. "I need only one card." Tôi chỉ cần một thẻ. Tôi lấy một chiếc, để hai chiếc còn lại gần bạn.')
line(719,2,'Hoàng tưởng tôi cần cả bộ để viết dài hơn. Tôi chỉ có một câu muốn thử, chưa muốn nhận phần của lượt sau. Bạn giữ lại hai thẻ, không đưa thêm khi tôi vừa ngồi xuống.')
line(719,3,'"We have only two cards left." Chúng ta chỉ còn hai thẻ. Hoàng nói khi kiểm phần còn lại; tôi cũng nhìn rõ hai chiếc trên tay bạn, chưa nhận có nhiều hơn.')
line(719,6,'"I need only one card." Tôi chỉ cần một thẻ. Hoàng giữ hai chiếc còn lại trong hộp, để tôi dùng một chiếc trước. Viết xong, tôi đưa bạn xem, không xin thêm chỉ vì chỗ giấy còn rộng.')
E['719']['selected_gloss_vi']='chỉ, giới hạn lượng được nhắc';E['719']['plot_vi']='Hoàng muốn đưa cả bộ ba thẻ, tôi chỉ nhận một cho lượt của mình; hai thẻ còn lại được giữ cho phần sau.'
vis(719,1,'Cream-shirt friend offers exactly three plain cards across table, mascot takes one while two remain together near friend. No thick stack.')
vis(719,2,'Mascot keeps one card by own hand, friend holds exactly two remaining blank cards; no duplicate card pile or written answers.')
vis(719,3,'Friend fans exactly two remaining cards beside open small box, mascot\'s one card stays separate. No third chair needed.')
vis(719,4,'Mascot writes non-legible strokes on own single card while friend puts exactly two blank cards beside pencil case. No readable model sentence on props.')
vis(719,6,'Mascot shows his single card with non-legible strokes to friend, who keeps remaining two cards together inside open box. No extra study card given to friend yet.')
# Really: specific personal motive replaces generic determination/inspirational resolution.
line(720,1,'Thảo gập tờ rơi, định thôi rủ tôi. "Do you really want to go?" Bạn thực sự muốn đi không? Bạn sợ tôi chỉ nhận lời cho bạn đỡ buồn, không thích xem tranh.')
line(720,3,'"I really want to go." Tôi thực sự muốn đi. Tôi nói, chỉ bức tranh mình muốn xem từ lúc bạn gửi. Đây là điều tôi muốn, không phải chỉ theo để chiều bạn.')
line(720,4,'Thảo mở tờ rơi lại, tìm phần tranh tôi vừa chỉ. Bạn đã định bỏ buổi đi vì ngại tôi không thích. Tôi đề nghị mỗi người chọn một phần muốn xem, rồi đi cùng.')
line(720,6,'"I really want to go." Tôi thực sự muốn đi. Thảo để tờ rơi giữa hai người, không gập cất nữa. Tôi đánh dấu phần mình chọn, bạn đánh dấu bên cạnh; buổi đi có cả lý do của hai đứa.')
E['720']['plot_vi']='Thảo tưởng tôi chỉ nhận lời vì bạn, tôi nêu điều mình thật sự muốn xem; hai người giữ buổi đi và mỗi người chọn một phần.'
vis(720,3,'Mascot points to one plain illustrated painting on brochure while pink-shirt friend listens. No hand-over-heart performance or promise of energy.')
vis(720,4,'Both figures open brochure flat on shared table and select separate illustrated sections, no printed titles or hat supplies.')
vis(720,5,'Friend pauses over open brochure to ask mascot about sincere choice, top safe region for stem. No hats or departure yet.')
vis(720,6,'Both friends mark their separate preferred illustrations with small unlettered dots on same brochure. No sun hats, timeline or exact exhibition data.')
# Get on: stationary open-door bus until the actual post-answer boarding.
line(721,1,'Bình giữ vé, chưa chịu bước lên. Xe vừa dừng, cửa đã mở. "Do we get on this bus?" Mình lên xe buýt này à? Bạn hỏi tôi, sợ mình nhớ sai.')
line(721,3,'Tôi kiểm số trên vé và đầu xe, đúng số đã chọn. "Get on the bus." Lên xe buýt nhé. Tôi bước lên bậc thấp, quay lại đợi Bình, chưa vào ngồi trước.')
line(721,4,'Bạn vẫn ở ngoài, ngại mình cầm vé chưa sẵn. Tôi đứng giữ vị trí gần cửa để bạn thấy mình. Xe còn dừng, cửa mở, Bình lấy vé ra đúng tay rồi mới bước tới.')
line(721,6,'"Get on the bus." Lên xe buýt nhé. Bình bước từ đường lên bậc cửa, vào cùng tôi. Tôi giữ chiếc ghế cạnh cửa sổ cho bạn, không để bạn phải đi tìm chỗ một mình.')
E['721']['custom_visible_text']=[{'text':'7','placement':'large route numeral on bus front placard','object':'bus route placard'},{'text':'7','placement':'small route numeral on plain monthly pass','object':'monthly pass'}]
E['721']['plot_vi']='Bình ngại nhớ sai xe và chưa chuẩn bị vé; tôi kiểm số, đứng trên bậc đợi bạn thật sự bước lên rồi cùng chọn chỗ.'
vis(721,1,'Stationary bus with front door fully open and permitted route numeral 7, grey-shirt friend holds pass near curb while mascot waits beside him. No driver or passengers.')
vis(721,4,'Mascot stands on lower open bus step looking back, friend remains at curb taking permitted 7 pass from bag. Bus stationary, door fully open, no closing motion.')
vis(721,5,'Same camera: mascot waits on lower step, friend paused just before boarding with pass ready. No seat view or departure yet; upper safe region for stem.')
vis(721,6,'Grey-shirt friend takes one foot from curb onto lower bus step while mascot stands just inside, door fully open and bus stationary. No driver, crowd or duplicate body.')
E['721']['extra_visual_states']=[{'quote':'Tôi giữ chiếc ghế cạnh cửa sổ cho bạn,','visual_en':'After both have boarded, the same two registered figures sit on two adjacent empty bus seats by window. No driver or other passenger visible.','purpose_en':'Show boarded state after the actual step-through action and close their choice to sit together.'}]
for e in E.values():e['scenes'][4]['stem']=e['scenes'][4]['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
