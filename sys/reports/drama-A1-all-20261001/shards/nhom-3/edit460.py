from pathlib import Path
import json
P=Path(__file__).parent/'460-469';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def line(n,i,t):E[str(n)]['scenes'][i-1]['narration']=t
def vis(n,i,t):E[str(n)]['scenes'][i-1]['visual_en']=t
line(702,1,'An đứng ở cửa, định về trước. Tôi vẫn giữ khóa cần trả: "No one is at the desk." Không ai ở quầy trực. Ghế trống, tôi chưa biết giao cho ai.')
line(702,2,'Phòng đã mở nhưng không có người nhận. An rủ mai quay lại, tôi ngại mình mang khóa về khiến người trực không biết. Tôi rủ bạn thử gọi số đã lưu trước khi đi.')
line(702,3,'"No one answered the phone." Không ai nghe máy. Tôi đặt điện thoại xuống, nhìn chìa khóa. An đợi thêm, dù lúc nãy đã muốn đi; cậu đưa tôi mẩu giấy để ghi lại.')
line(702,6,'"No one is at the desk." Không ai ở quầy trực. Tôi để giấy nhắn sẽ quay lại, giữ khóa trong túi mình. An lấy túi giúp, bảo mai mình tới cùng nhau để trả tận tay.')
E['702']['custom_visible_text']=[{'text':'Tôi sẽ quay lại.','placement':'center of one small paper note on office glass door','object':'paper note'}]
E['702']['plot_vi']='Không có người nhận khóa, tôi thử gọi rồi ghi lời sẽ quay lại; An thôi về trước và hẹn cùng trả tận tay hôm sau.'
vis(702,3,'Mascot holds plain mobile phone with screen turned away after unanswered call; cream-shirt companion offers blank yellow note. Empty desk remains visible, no wall phone number or clipboard.')
vis(702,6,'Mascot attaches small note bearing permitted Tôi sẽ quay lại. to glass door and keeps key in own pocket; cream-shirt companion holds his bag to leave together. No security drop-box or implied approval to deposit keys.')
# Something: explicit mystery, register actual kitten only after reveal; no milk-care claim.
e=E['703'];e['characters'].append({'id':'CH03','name_vi':'Mèo con trong hộp','appearance_en':'Small minimal grey ink kitten with round simple face, two solid dark oval eyes, triangular ears, minimal line paws and tail.','outfit_en':'No clothes or human torso, plain grey coat.'})
line(703,1,'Bình xếp hộp, tôi giữ chiếc cuối. Trong hộp có tiếng sột soạt. "There\'s something in the box." Có thứ gì đó trong hộp. Tôi chưa biết đó là gì, chỉ nhờ bạn dừng lại.')
line(703,2,'Bạn muốn dọn hết góc kho trước khi về. Tôi đặt hộp xuống, không chồng thùng khác lên. Bình vẫn chưa chắc bên trong có đồ, cậu đưa đèn để tôi xem trước.')
line(703,3,'Tôi soi qua khe nắp, thấy một chú mèo con nằm trên khăn. "I found something." Tôi tìm thấy một thứ rồi. Bình hạ chồng hộp đang mang, cúi xuống nhìn cùng tôi.')
line(703,4,'Bạn định dán kín nắp cho gọn, tôi giữ lại. Chúng tôi để hộp ở góc riêng, không lẫn với các thùng rỗng. Bình lấy một mảnh giấy nhắc đừng chuyển hộp này đi.')
line(703,6,'"There\'s something in the box." Có thứ gì đó trong hộp. Bình đặt hộp ở góc riêng, không chuyển cùng thùng rỗng. Tôi ngồi xuống cạnh, chờ con mèo bước ra thay vì vội kết thúc việc dọn.')
e['custom_visible_text']=[{'text':'Đừng chuyển hộp','placement':'small note beside box on floor, separate from opening','object':'paper note'}];e['plot_vi']='Bình định xếp nốt hộp rỗng, tôi nhờ dừng khi nghe có thứ bên trong; tìm thấy mèo, hai người dành góc riêng để hộp không bị chuyển đi.'
for i,s in enumerate(e['scenes']):s['character_ids']=['CH01','CH02'] if i<2 else ['CH01','CH02','CH03']
vis(703,4,'Two figures place open kitten box in separate floor corner, friend holds blank note beside it. Kitten stays on plain towel, no milk, feeding procedure or anatomical fingers.')
vis(703,6,'Open kitten box rests separately beside note bearing permitted Đừng chuyển hộp; empty cartons stacked elsewhere. Mascot sits nearby while friend leaves box untouched. No unseen janitor or adoption claim.')
# Anything: bag question not contradicted by notebooks, no jacket covering mascot identity.
lines=[
'Linh giữ túi, định bỏ buổi đi chơi. Bạn chưa chuẩn bị đồ gì. "Is there anything in the bag?" Trong túi có thứ gì không? Tôi hỏi trước khi mở túi cùng bạn.',
'Linh cho xem túi trống, ngại mình lại phải mượn. Tôi đặt túi đồ của mình bên cạnh, nói đã mang để dùng chung. Bạn vẫn giữ quai túi, chưa muốn nhận lời đi.',
'"Do you need anything?" Bạn có cần thứ gì không? Tôi hỏi rộng, chưa chọn hộ bạn phải lấy món nào. Linh nhìn túi tôi rồi nói cần một tấm khăn để ngồi.',
'Tôi lấy khăn, đưa bạn tự xếp vào túi. Linh bảo chỉ cần thế, không muốn tôi mang hộ tất cả. Tôi giữ phần đồ còn lại của mình, để bạn được tự chuẩn bị phần ấy.',
'Linh sợ còn thiếu món nào tôi muốn bạn mang. Bạn nói giúp tôi câu bạn có cần thứ gì không bằng tiếng Anh nhé.',
'"Do you need anything?" Bạn có cần thứ gì không? Linh lắc đầu, kéo khóa túi đã có khăn. Tôi ra cửa chờ, lần này bạn khoác túi của mình lên để cùng đi.'
]
for s,n in zip(E['704']['scenes'],lines):s['narration']=n
E['704']['plot_vi']='Linh ngại chưa chuẩn bị gì nên định không đi chơi; tôi hỏi nhu cầu không chọn thay, bạn nhận một tấm khăn và tự mang phần ấy.';E['704']['title']='Khăn trong chiếc túi trống'
vs=['Yellow-shirt friend hesitates holding empty plain tote at home doorway, mascot asks beside his own picnic bag. No rain or wet clothes.',
'Friend shows fully empty tote while mascot places own closed shared-supplies bag beside it. No notebooks contradict empty-bag question.',
'Mascot asks openly with empty hands, friend points toward folded plain cloth partly visible in supply bag.',
'Friend folds plain cloth into own tote while mascot keeps remaining supplies in his own bag. Both registered shirt colors visible, no raincoat.',
'Friend pauses beside partly filled tote asking about missing need, mascot listens. Top safe space for stem.',
'Friend closes tote containing cloth and joins mascot at open home doorway with each carrying own bag. No weather exposure or health claim.']
for s,v in zip(E['704']['scenes'],vs):s['visual_en']=v
# Everything refers to the finite supplies named by the group, all remain together.
line(705,1,'Khoa tìm hộp, tôi còn giữ ba món. "Is everything here?" Mọi thứ có ở đây chưa? Bạn hỏi về thẻ, bút và kẹp cần cho góc sách của hai người.')
line(705,2,'Tôi đã xếp thẻ nhưng còn một chiếc kẹp dưới sổ. Khoa muốn đóng hộp cho nhanh, tôi nhờ đợi. Thiếu món nhỏ ấy, phần tôi làm sẽ chưa treo được.')
line(705,3,'Tôi lấy kẹp, đặt cả ba món vào các ngăn. "Everything is in the box." Mọi thứ đều trong hộp. Khoa nhìn lại, không phải đi tìm thêm thứ đã có trên bàn nữa.')
line(705,4,'Bạn định thêm một món trang trí lớn, tôi xin giữ bộ nhỏ này để hai đứa mang được. Khoa cất món định thêm, nhận cầm hộp thay tôi. Tôi lấy phần thẻ đã chuẩn bị.')
line(705,6,'"Is everything here?" Mọi thứ có ở đây chưa? Khoa chỉ ba ngăn đầy, gật đầu. Tôi khép hộp, bạn nhận cầm một bên để cả hai cùng mang tới chỗ bày đã chọn.')
E['705']['plot_vi']='Khoa muốn đóng hộp nhanh nhưng thiếu chiếc kẹp tôi cần; hai bạn giữ đủ bộ ba món nhỏ rồi cùng mang thay vì thêm trang trí cồng kềnh.'
vis(705,1,'Green-shirt friend holds open organizer box while mascot has plain cards, one pen and a clip at table. Only these three supply types, no readable checklist.')
vis(705,2,'Mascot lifts closed notebook to retrieve one clip while friend waits with organizer box open; plain cards and pen already beside box.')
vis(705,3,'Close view of open organizer box containing plain cards, pen and clip in three visible compartments, both figures inspect. No books distributed elsewhere.')
vis(705,4,'Friend sets bulky unlabelled decoration aside and reaches to carry small supply box with mascot. No arriving customers or hall opening.')
vis(705,6,'Both figures hold opposite sides of small organizer box containing their three supplies, ready to carry together. No hidden fourth item or claim about all objects in world.')
# Nothing: keep collected tools in fabric roll, tin genuinely empty before practice.
line(706,1,'Tôi chạm bàn, hộp của Mai rơi xuống. Cọ và bút nằm rải quanh ghế. "There\'s nothing in the box." Không có gì trong hộp. Tôi nhấc lên, xin bạn để mình gom lại.')
line(706,2,'Mai muốn tìm ngay chiếc cọ nhỏ đang dùng, nhưng tôi cứ cầm hộp rỗng đứng nhìn. Tôi đặt hộp xuống, quỳ cạnh bạn. Hai đứa chia hai bên ghế để tìm hết đồ mình vừa làm rơi.')
line(706,4,'Tôi lau nắp hộp rỗng, chưa cất cọ trở lại vì Mai đã xếp đủ vào cuộn vải. Bạn muốn giữ cuộn đó cho gọn, tôi hỏi còn cần chiếc hộp này không.')
line(706,6,'"There\'s nothing in the box." Không có gì trong hộp. Mai nhận cuộn cọ đã đủ, đưa hộp rỗng cho tôi giữ giấy vụn. Tôi đặt nó ở bàn, lần này để xa mép ghế vừa va vào.')
E['706']['plot_vi']='Tôi làm rơi bộ cọ của Mai; cả hai tìm đủ rồi bạn dùng cuộn vải, dành chiếc hộp thật sự rỗng cho tôi giữ giấy vụn.'
vis(706,4,'Mascot wipes lid of empty tin beside friend\'s full fabric brush roll; open tin remains bare. No brushes returned inside tin.')
vis(706,6,'Friend holds full fabric brush roll while mascot places still-empty tin safely toward center of table for later paper scraps. No lights-out action or second tin.')
# Somewhere: no plant physiology or technical positioning claim; place still undecided until answer.
line(707,1,'Nam giữ kệ, chậu cây vẫn trên tay tôi. Bệ cửa đã đầy sách. "We need somewhere to put it." Mình cần một nơi đặt nó. Tôi muốn món cây đem tới có chỗ đứng cùng đồ hai bạn.')
line(707,2,'Nam đã dành góc kệ cho bộ sách mới, không muốn dời ngay. Tôi đứng đợi giữa hai bàn, chưa chọn chỗ nào. Bạn nhìn quanh, thử kê một mặt bàn đang dùng để xếp giấy.')
line(707,3,'Chậu cây che phần giấy Nam cần lấy. "Can we put it somewhere else?" Mình đặt ở nơi khác được không? Tôi hỏi, không muốn đồ của mình khiến bạn phải bỏ chỗ đang làm.')
line(707,4,'Nam kéo ghế ra, nhìn góc kệ dưới. Tôi nâng chậu lên lại, để bạn lấy giấy trước. Hai đứa vẫn cần dọn một chỗ khác, chưa phải cố giữ vị trí vừa đặt thử.')
line(707,6,'"We need somewhere to put it." Mình cần một nơi đặt nó. Nam dời một chồng sách nhỏ, tôi đặt cây vào góc vừa chừa. Bạn để lại một cuốn bên cạnh, giờ góc ấy có phần của cả hai.')
E['707']['plot_vi']='Tôi mang cây tới góc làm chung nhưng Nam chưa muốn dời sách; hai người thử một chỗ rồi chọn nhường góc nhỏ để giữ đồ của cả hai.'
vis(707,1,'Mascot holds small potted plant while purple-shirt friend keeps bookshelf corner filled with books. Shared room with two tables, no plant care labels.')
vis(707,3,'Potted plant on temporary paper table blocks access to a plain folder; friend reaches toward folder, mascot asks to move plant. No fan, leaf damage or light claim.')
vis(707,4,'Mascot lifts plant back into own hands while friend retrieves papers and surveys lower shelf; no cleared final platform yet.')
vis(707,6,'Friend has moved one small book stack aside to make room on lower shelf; mascot puts plant in new gap, one of friend\'s books remains beside it. No watering or sunlight guarantees.')
# Anywhere: permission within an identified area, no unregistered new reader.
line(708,1,'Dũng cất sách, tôi vẫn đứng ở cửa. Nhiều bàn trống nhưng tôi chưa biết chỗ dành cho ai. "Can I sit anywhere?" Tôi ngồi chỗ nào cũng được không? Tôi hỏi bạn.')
line(708,2,'Bạn đã rủ tôi tới đọc cùng, nhưng tôi quên mang thẻ người đọc. Tôi sợ ngồi nhầm phần đặt riêng, cứ giữ túi trên vai. Dũng đặt sách xuống để chỉ khu mình đang ở.')
line(708,3,'"You can sit anywhere here." Bạn ngồi bất cứ chỗ nào ở đây được. Dũng chỉ dãy bàn này, nơi bạn đã hỏi phép dùng trước; những phần khác của thư viện chưa thuộc lời mời.')
line(708,4,'Tôi chọn ghế cuối dãy, vẫn chưa đặt đồ vì bạn đang đứng. Dũng mang sách tới cạnh, hỏi sao tôi cứ sợ phải chọn đúng một chiếc ghế nhất định.')
line(708,5,'Tôi muốn xác nhận chỗ ngồi trong dãy này trước khi mở sách. Bạn nói giúp tôi câu tôi ngồi chỗ nào cũng được không bằng tiếng Anh nhé.')
line(708,6,'"Can I sit anywhere?" Tôi ngồi chỗ nào cũng được không? Dũng gật, kéo ghế bên cạnh tôi. Tôi để túi xuống, mở sách; buổi đọc cùng bạn cuối cùng đã có chỗ cho cả hai.')
E['708']['plot_vi']='Tôi ngại chọn sai chỗ khi quên thẻ, Dũng chỉ quyền chọn bất cứ ghế trong dãy đã được dùng; bạn ngồi cạnh để tôi thôi đứng chờ.'
vis(708,4,'Mascot pauses behind chosen empty chair with bag still over shoulder, beige-shirt friend brings closed book toward adjacent seat in identified reading row.')
vis(708,5,'Mascot asks same friend beside chosen two chairs, no new reader at door. Top safe region for stem.')
vis(708,6,'Both friends sit side by side in identified reading row with books open and mascot\'s bag beneath chair. No other library guests or global access sign.')
# Everywhere: exhaustive-room statement comes after completing local search.
line(709,1,'Hà giữ cửa, giấy đã bay đầy phòng. "There\'s paper everywhere." Giấy ở khắp nơi. Tôi nhìn dưới bàn, trên ghế, cả sàn đều có những tờ hai người đang làm.')
line(709,3,'Hà chỉ lo bức mình đã vẽ, muốn tìm ngay rồi bỏ phần giấy vụn. Tôi nhặt từng chỗ giúp bạn, kiểm cả sau rèm. Bạn cùng cúi xuống, không đứng riêng ở bàn nữa.')
line(709,4,'Sau rèm có bức vẽ. "We looked everywhere in this room." Chúng tôi đã tìm khắp phòng này. Tôi nói khi cả hai đã kiểm những chỗ cần tìm, đưa tranh để Hà tự nhìn lại.')
line(709,6,'"There\'s paper everywhere." Giấy ở khắp nơi. Hà giữ tranh lên kệ, quay lại gom giấy với tôi. Tờ cuối nằm dưới ghế bạn, lần này Hà kéo ghế ra giúp chứ không chỉ giữ phần của mình.')
vis(709,3,'Companion searches under table while mascot checks behind curtain, sheets still scattered on desks, chairs and floor. No final claim before search complete.')
vis(709,6,'Friend has placed retrieved unlabelled drawing on shelf and helps mascot by pulling chair out to reach last loose sheet; most paper organized nearby. No awards or completed-room jump.')
# Both: two referents and actual English pronoun use stays as previous bank contract.
line(710,1,'Tuấn giữ khung, chỉ chừa một ô trống. Tôi cầm hai ảnh: "I like both." Tôi thích cả hai. Một ảnh có trại nhỏ, ảnh kia có sân bóng hai đứa từng đi qua.')
line(710,3,'"Both are mine." Cả hai đều của tôi. Tôi nói, không muốn bỏ một tấm chỉ vì khung nhỏ. Tuấn hỏi tấm nào gắn với mình, tôi chỉ cả hai chỗ bạn từng ngồi cạnh.')
line(710,4,'Bạn xem lại khoảng trống, thử đặt hai ảnh sát nhau. Không cần chọn một rồi cất một, chỉ cần bớt giấy nền. Tôi giữ một tấm, Tuấn giữ tấm còn lại để thử cùng.')
line(710,6,'"I like both." Tôi thích cả hai. Tuấn dán ảnh cạnh nhau, để tôi chỉnh phần của mình. Hôm sau nhìn khung, hai đứa không cần nhớ bức nào đã phải cất đi.')
E['710']['plot_vi']='Khung chỉ chừa một ô, tôi muốn giữ cả hai ảnh gắn với hai bạn; Tuấn thử bỏ nền để hai tấm cùng vừa.'
vis(710,2,'Mascot holds two photos side by side showing only unoccupied campsite and empty court, no friends or class crowd pictured.')
vis(710,3,'Mascot shows both unlabelled photo fronts to teal-shirt companion, pointing to empty bench in each; no handwritten signatures or class list.')
# This: choice near speaker, reluctant recipient learns friend deliberately chose for him.
line(711,1,'Lan giữ cuốn xanh, tôi chưa dám nhận. "This book is new." Quyển sách này mới. Tôi chạm mép sách bạn vừa được thưởng, ngại lấy thứ bạn còn chưa đọc xong.')
line(711,2,'Lan muốn tặng tôi trước khi chuyển trường. Bạn nhớ tôi đã giúp chọn cuốn này ở hội sách, nên giữ riêng. Tôi đề nghị lấy cuốn khác cũ hơn, đỡ khiến bạn tiếc.')
line(711,3,'"I want this book." Tôi muốn quyển sách này. Tôi nói thật khi Lan hỏi mình muốn cuốn nào, chỉ đúng cuốn trong tay. Bạn vẫn có thể giữ đọc xong rồi mới đưa tôi.')
line(711,4,'Lan đặt kẹp vào trang đầu, bảo mình mua vì nghĩ tôi sẽ thích. Tôi thôi đẩy về kệ, nhận cuốn gần tay mình. Bạn còn chỉ một trang muốn tôi đọc đầu tiên.')
line(711,6,'"I want this book." Tôi muốn quyển sách này. Lan đưa lại đúng cuốn xanh. Tôi mở trang bạn chỉ, hẹn đọc xong sẽ kể bạn nghe, không chỉ cất sách vào túi rồi chào đi ngay.')
E['711']['plot_vi']='Tôi ngại lấy cuốn mới của Lan, bạn cho biết đã chọn vì tôi; tôi nói rõ muốn cuốn gần tay và giữ lời sẽ kể lại phần đọc.'
vis(711,1,'Pink-shirt friend holds one new blue book close to mascot beside home bookshelf, mascot touches its corner hesitantly. No written reward label.')
vis(711,6,'Mascot opens received blue book to an unlabelled illustrated page while friend points to that same page; both stay beside shelf talking. No departure or printed excerpts.')
for e in E.values():e['scenes'][4]['stem']=e['scenes'][4]['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
