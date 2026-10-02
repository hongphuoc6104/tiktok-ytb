from pathlib import Path
import json
P=Path(__file__).parent/'450-459';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def line(num,i,n):E[str(num)]['scenes'][i-1]['narration']=n
def visual(num,i,v):E[str(num)]['scenes'][i-1]['visual_en']=v
def extra(num,name,color):
 e=E[str(num)];e['characters'].append({'id':'CH03','name_vi':name,'appearance_en':'Minimal ink figure with round white head, navy outline, solid black oval eyes and simple stick limbs.','outfit_en':f'Exactly one plain {color} short-sleeve torso and minimal navy stick limbs.'});return e
line(692,1,'Duy giữ bút, muốn vẽ hộ tôi. Tôi đã làm gần xong kẹp sách: "I made it myself." Tôi tự làm nó. Bạn nhìn đường hơi lệch, hỏi sao tôi không dùng mẫu in sẵn.')
line(692,2,'Tôi muốn tặng Duy thứ mình tự vẽ, nên giữ tấm giấy lại. Bạn vẫn ở bên, đẩy lọ màu giúp tôi, nhưng đường vẽ này do tôi làm. Tôi chỉ nắn thêm góc còn thiếu.')
line(692,3,'Duy ngồi xuống, không vẽ thay nữa. Cậu chọn chỗ muốn kẹp vào sổ. Tôi nhìn cuốn sổ bạn dùng hằng ngày, đổi độ dài dây để món nhỏ dễ đặt vào đó.')
line(692,4,'"I wrote the note myself." Tôi tự viết lời nhắn. Tôi ghi tên Duy ở góc giấy, không nhờ bạn viết hộ. Duy nhận ra tên mình, thôi hỏi tặng cho ai.')
line(692,6,'"I made it myself." Tôi tự làm nó. Duy kẹp tấm thẻ vào sổ, chừa đường vẽ hơi lệch ra ngoài. Tôi định chỉnh nốt, cậu giữ lại, bảo để thế cũng nhận ra là của tôi.')
E['692']['custom_visible_text']=[{'text':'Duy','placement':'small handwritten recipient name near lower bookmark corner','object':'bookmark'}]
E['692']['plot_vi']='Duy định vẽ hộ cho nhanh nhưng tôi muốn tự làm kẹp sách tặng cậu; bạn ngồi cạnh hỗ trợ đồ dùng và giữ cả nét vẽ hơi lệch.'
# Yourself: same doer, not necessarily alone; simple paper box, no screw or wood guarantees.
line(693,1,'Mai để hộp giấy chưa gấp kín lại. Em muốn tôi làm hộ cho nhanh. "Did you make it yourself?" Em tự làm nó à? Tôi hỏi về phần em đã gấp xong.')
line(693,2,'Mai gật, chỉ hai mép mình đã làm. Em muốn có hộp để giữ dây buộc tóc nhưng ngại góc cuối sẽ lệch. Tôi nhìn phần em đã thử, kéo ghế ngồi bên cạnh.')
line(693,3,'Tôi đưa lại tờ mẫu, để Mai nhìn góc cần gấp. Anh vẫn ngồi đây, phần này em làm nhé. Mai giữ giấy, không đẩy cả hộp sang tôi nữa.')
line(693,4,'"You can do it yourself." Em có thể tự làm được. Tôi nhắc đúng phần Mai đã thử trên tờ mẫu, không nhận làm thay. Em xoay hộp lại để tìm nếp đã gấp.')
line(693,6,'"Did you make it yourself?" Em tự làm nó à? Mai gật, đặt dây buộc tóc vào hộp. Tôi đưa cuộn dây còn lại cho em cất, giữ chiếc ghế cạnh em thêm một chút.')
vs=['Yellow-shirt sister places partly folded paper box on table asking mascot to complete it; one already folded side visible.',
'Sister shows two completed folds in paper box to mascot beside simple pictorial paper template. No lettering or screw tools.',
'Mascot slides non-text folding diagram toward sister while remaining seated beside her; she keeps actual box in own hands.',
'Sister turns paper box to inspect final corner, mascot waits beside her holding no tools. No guaranteed universal skill claim.',
'Sister has folded final corner herself while mascot looks at the resulting small box, top safe space for stem.',
'Sister puts one plain hair tie into folded box, mascot offers remaining hair ties while seated beside her.']
for s,v in zip(E['693']['scenes'],vs):s['visual_en']=v
E['693']['plot_vi']='Mai muốn tôi gấp hộ góc cuối của hộp; tôi ở cạnh cho em xem lại phần đã thử, em tự làm rồi cất dây buộc tóc.'
E['693']['title']='Góc cuối của hộp giấy'
# Himself: explicit male referent and listener registered; no repair safety promises.
e=extra(694,'Bác Tư','brown');e['characters'][1]['name_vi']='Huy'
lines=[
'Bác Tư tưởng mô hình do tôi làm. Tôi giữ hộp của Huy: "He made it himself." Anh ấy tự làm nó. Tôi chỉ bạn đứng cạnh, chưa nhận phần ấy về mình.',
'Huy làm chiếc thuyền giấy để tặng bác, nhưng ngại nó còn méo. Tôi chỉ mang hộp đựng giúp. Bác nhìn từ tôi sang Huy, mời cậu kể mình đã thử thế nào.',
'Huy nói gấp đi gấp lại mới giữ được dáng. Tôi vẫn ở cạnh lúc bạn làm, nhưng không gấp hộ. Bác lấy hộp, đợi Huy đặt chiếc thuyền vào chính tay mình.',
'"He packed the box himself." Anh ấy tự xếp hộp. Tôi nói khi bác hỏi ai đã chuẩn bị cả phần bên ngoài. Huy kéo mép hộp cho ngay, không giấu sau lưng tôi nữa.',
'Bác Tư hỏi lại ai đã làm chiếc thuyền giấy. Bạn nói giúp tôi câu anh ấy tự làm nó bằng tiếng Anh nhé.',
'"He made it himself." Anh ấy tự làm nó. Bác Tư nhận hộp từ Huy. Bạn chỉ chỗ hơi méo, bác đặt luôn lên bàn mình, để Huy nhìn thấy quà đã được giữ lại.'
]
for s,n in zip(e['scenes'],lines):s['narration']=n;s['character_ids']=['CH01','CH02','CH03']
e['scenes'][4]['stem']='He made it ___.';e['plot_vi']='Bác Tư nhầm người làm quà, tôi nói rõ phần Huy tự gấp và tự chuẩn bị; Huy trao hộp và không giấu kết quả hơi méo.';e['title']='Chiếc thuyền là của Huy'
vs=['Mascot holds small gift box while brown-shirt older figure looks at him; olive-shirt Huy stands beside holding a slightly uneven paper boat.',
'Older figure gestures inviting Huy to explain his uneven paper boat, mascot holds only empty gift box.',
'Huy puts paper boat into box held by mascot while older figure watches. No bike, machinery or implied solitude.',
'Huy adjusts folds of outer plain box himself, mascot tells older figure about Huy\'s preparation.',
'Older figure asks mascot who made the boat, Huy holds completed box nearby. Top safe space for stem.',
'Older figure receives box directly from Huy and places it on his own table with paper boat visible; mascot stands beside them.']
for s,v in zip(e['scenes'],vs):s['visual_en']=v
# Herself: explicit female referent, one cake, no homemade-only moral or sleep deprivation.
e=extra(695,'Mai','light yellow')
lines=[
'Mai nhận hộp, tưởng bánh tôi mua sẵn. Tôi lắc đầu: "She made it herself." Cô ấy tự làm nó. Chị Lan ở bên cạnh, vẫn chưa muốn đưa hộp vào bàn.',
'Chị đã làm một chiếc bánh nhỏ tặng Mai, nhưng mặt bánh còn lệch. Tôi chỉ nhận phần mang hộp. Mai nhìn sang chị, hỏi món có phải chị chuẩn bị từ sáng không.',
'Chị Lan gật, định tháo dây để xem lại. Mai giữ nắp, muốn nghe chị kể trước, không cần sửa cho đẹp hơn. Tôi đặt hộp xuống giữa hai người, thôi cầm hộ nữa.',
'"She packed the box herself." Cô ấy tự xếp hộp. Tôi nói khi Mai khen chiếc nơ. Chị Lan chỉ nếp giấy mình gấp, bảo nó vẫn lệch nhưng ôm vừa bánh.',
'Mai hỏi lại ai làm chiếc bánh trong hộp. Bạn giúp tôi nói câu cô ấy tự làm nó bằng tiếng Anh nhé.',
'"She made it herself." Cô ấy tự làm nó. Mai nhận hộp từ tay chị, mời cả hai ngồi xuống. Chị Lan cắt phần bánh đầu, lần này giữ nguyên chiếc nơ mình định tháo.'
]
for s,n in zip(e['scenes'],lines):s['narration']=n;s['character_ids']=['CH01','CH02','CH03']
e['plot_vi']='Mai tưởng bánh mua sẵn; tôi nói rõ chị Lan tự làm và tự gói. Mai giữ món quà hơi lệch, mời chị cùng ăn.';e['title']='Giữ nguyên chiếc nơ'
vs=['Yellow-shirt Mai pauses with one tied cake box beside table, mascot points toward pink-shirt Lan standing close. One cake, three registered figures.',
'Lan hesitates holding unevenly wrapped cake box while Mai asks her about making it; mascot stands aside holding no baking tool.',
'Mai holds box lid closed to stop Lan reopening it, mascot sets box down between the two women. No apron, sleep deprivation or moral text.',
'Lan points to her own imperfect paper fold and twine bow on single cake box while mascot explains its maker to Mai.',
'Mai asks mascot about the single cake, Lan holds box beside them. Top safe space for stem.',
'All three sit at a small table, Lan cuts first slice from one slightly uneven cake; original twine bow remains beside open box.']
for s,v in zip(e['scenes'],vs):s['visual_en']=v
# Itself: visible reflexive action on SAME registered animal, present action consistent with narration.
e=E['696'];e['characters'].append({'id':'CH03','name_vi':'Mèo nhà tôi','appearance_en':'Small minimal ink kitten, round white and grey head, two solid black oval eyes, simple triangular ears, minimal line paws and tail.','outfit_en':'No clothing or human torso; plain white-grey coat.'})
line(696,1,'Bình đưa tay, mèo nép sau cửa. Tôi rủ bạn ngồi xuống, đừng đuổi theo. "The cat is cleaning itself." Mèo đang tự làm sạch mình. Nó liếm bàn chân của chính nó.')
line(696,2,'Bình định lấy khăn lau hộ, tôi giữ khăn lại. Con mèo nhà tôi vừa ra thảm, tự liếm lông. Người làm sạch và con vật được làm sạch ở đây cùng là một con mèo.')
line(696,3,'Bạn đặt khăn xuống, ngồi bên tôi để xem thêm. Mèo bước tới chiếc gương thấp. Bình tưởng có con khác ở trong đó, tôi chỉ hình giống hệt con đang đứng trước gương.')
line(696,4,'"It is looking at itself in the mirror." Nó đang nhìn hình mình trong gương. Tôi kể điều nhìn thấy, không bảo mèo biết đó là gì. Bình ngồi yên, để nó tự đi tiếp.')
line(696,5,'Bình hỏi hành động lúc mèo ngồi trên thảm. Bạn nói giúp tôi câu mèo đang tự làm sạch mình bằng tiếng Anh nhé.')
line(696,6,'"The cat is cleaning itself." Mèo đang tự làm sạch mình. Bình cất khăn, đặt tay lên sàn. Mèo đi lại gần chiếc dép bạn, tôi kéo ghế thấp để cả hai cùng ngồi xem tiếp.')
e['scenes'][4]['stem']='The cat is cleaning ___.'
for s in e['scenes']:s['character_ids']=['CH01','CH02','CH03']
e['selected_gloss_vi']='chính nó, hành động quay lại cùng con vật';e['plot_vi']='Bình định vuốt rồi lau mèo, tôi rủ ngồi xem hành động mèo tự làm sạch và nhìn hình mình; bạn đặt khăn xuống, để mèo tự tới gần.'
visual(696,2,'Kitten licks its own forepaw on round rug, friend holds cleaning cloth but mascot gently keeps it aside. Two registered people and one registered cat only.')
visual(696,5,'Mascot and friend gesture back toward rug where kitten is grooming its own paw again; mirror remains beside wall, no second physical cat.')
visual(696,6,'Friend has put cloth aside and rests one minimal stick hand on floor near his slipper; kitten walks toward slipper, mascot brings a low stool closer. No adoption claim or duplicate cat.')
# Ourselves: completed act stays past and we includes narrator; mutual choice, no universal moral.
line(697,1,'Tuấn định che chiếc kệ bằng vải. Tôi giữ mép lại: "We made it ourselves." Chúng tôi tự làm nó. Hai đứa dựng xong từ tối qua, vẫn còn chỗ dán hơi lệch.')
line(697,2,'Bạn sợ người tới gian hàng tưởng kệ mua sẵn bị hỏng. Tôi muốn giữ phần mình đã làm, chỉ thêm vải ở đáy. Tuấn nhìn lại, hỏi có cần thay toàn bộ kệ không.')
line(697,3,'Tôi và Tuấn tự dán từng ngăn tối qua, không thuê người làm. Hôm nay hai đứa chỉ sửa một góc, vẫn đứng cạnh giúp nhau giữ. Tôi không muốn nhận thành quả về riêng mình.')
line(697,4,'"We packed the bag ourselves." Chúng tôi tự xếp túi. Tôi nhắc cả phần hai đứa cùng chuẩn bị sáng nay, rồi lấy sách từ túi đã đóng sẵn ra kệ.')
line(697,6,'"We made it ourselves." Chúng tôi tự làm nó. Tuấn gấp vải xuống đáy kệ, giữ ngăn phía trên ra ngoài. Tôi đưa bạn cuốn đầu để xếp; lần này kệ không cần che hết.')
visual(697,1,'Orange-shirt friend begins covering completed cardboard shelf with cloth, mascot holds cloth edge to keep upper shelf visible. Empty booth behind them, no outside workers.')
visual(697,2,'Both inspect finished cardboard shelf with one visibly crooked tape corner, cloth folded at bottom. No ongoing full construction or extra figure.')
visual(697,3,'Both figures adjust only one taped corner of existing shelf: friend holds panel and mascot presses tape. Shows collaborative doers rather than solitude.')
visual(697,6,'Friend folds cloth beneath shelf while mascot offers him first book to place on visible upper tier. No boastful sign or universal self-reliance text.')
E['697']['plot_vi']='Tuấn ngại kệ hai người tự dựng còn lệch, tôi giữ phần tự làm và rủ chỉ sửa một góc; cả hai không che hết công chung.'
# Themselves: three total people; main narrator explicitly EXCLUDED from the two makers.
e=E['698'];e['characters'][1]['name_vi']='Mai';extra(698,'Nam','dark green')
lines=[
'Tôi đưa biển, Mai giữ lại phần tên. Tôi định ghi cả tên mình cho nhóm. "They made it themselves." Họ tự làm nó. Tôi nhìn Mai và Nam với tấm áp phích vừa xong.',
'Tối qua tôi chỉ giúp mang giấy tới, còn hai bạn tự vẽ. Mai muốn ghi đúng người làm, nhưng ngại nói vì vẫn cần tôi dựng chân trưng. Tôi đặt bút xuống, nghe bạn.',
'Nam kéo áp phích lại gần, chỉ phần mình tô. Mai chỉ phần viền mình vẽ. Tôi đứng xem, không nằm trong hai người làm bức này, dù hôm nay cùng ở buổi trưng.',
'"They prepared the display themselves." Họ tự chuẩn bị góc trưng. Tôi nhìn hai bạn xếp tác phẩm của mình, chừa chỗ cho tấm biển tôi đang cầm. Phần việc của tôi khác với của họ.',
'Mai hỏi tôi sẽ nói ai làm áp phích khi người xem hỏi. Bạn giúp tôi nói câu họ tự làm nó bằng tiếng Anh nhé.',
'"They made it themselves." Họ tự làm nó. Tôi ghi hai tên đúng chỗ, đưa biển cho Mai kiểm. Nam giữ chân trưng để tôi gắn biển; mỗi người có phần của mình, không nhận lẫn.'
]
for s,n in zip(e['scenes'],lines):s['narration']=n;s['character_ids']=['CH01','CH02','CH03']
e['custom_visible_text']=[{'text':'Mai, Nam','placement':'small maker credit on separate exhibit card','object':'exhibit credit card'}]
e['plot_vi']='Tôi định ghi chung tên nhóm nhưng chỉ mang giấy giúp; Mai và Nam muốn phần tự vẽ được ghi đúng, tôi phân biệt công của mình và ghi hai tên lên biển.';e['selected_gloss_vi']='chính họ, nhấn hai người được nhắc là người làm'
vs=['Mascot holds blank credit card and pen beside exhibit, beige-shirt Mai stops writing gesture while dark-green-shirt Nam holds handmade poster.',
'Mai and Nam show handmade poster to mascot, who has lowered pen to listen. Three registered people only.',
'Nam points to colored central illustration while Mai points to handmade border; mascot watches without touching artwork.',
'Mai and Nam arrange poster on display stand themselves while mascot holds separate blank credit card, no printed information cards.',
'Mai asks mascot beside poster and Nam, credit card still blank. Top safe region for stem.',
'Mascot offers permitted Mai, Nam credit card to Mai to check, Nam holds stand base ready for card attachment. No third maker or extra audience.']
for s,v in zip(e['scenes'],vs):s['visual_en']=v
# Someone: an unknown person is actual cast, identity not exposed before answer.
e=extra(699,'Người mang trả sổ','grey')
line(699,1,'An giữ tôi lại bên máy tính. Tiếng gõ cửa vừa tới. "Someone is at the door." Có ai đó ở cửa. Tôi nhìn bóng mờ, chưa biết người ấy là ai.')
line(699,3,'An tưởng người ta gõ nhầm phòng, rủ tôi làm nốt dòng đang viết. Tôi thấy bóng vẫn chờ nên đứng dậy. Bạn đặt tay khỏi bàn phím, hỏi xem tôi có cần đi cùng không.')
line(699,4,'"Is someone waiting outside?" Có ai đang đợi ngoài đó à? An hỏi. Tôi gật, đặt tay vào nắm cửa, nhưng vẫn nghe bạn trước khi mở.')
line(699,6,'"Someone is at the door." Có ai đó ở cửa. Tôi mở, người đó đưa cuốn sổ tôi bỏ quên dưới sảnh. An giữ cửa cùng tôi; người mang sổ không phải chờ thêm nữa.')
for s in e['scenes']:s['character_ids']=['CH01','CH02','CH03']
visual(699,6,'Mascot opens office door; grey-shirt visitor hands back one plain blue notebook while lavender-shirt colleague holds door from inside. Only three registered figures, no readable names.')
e['plot_vi']='An tưởng gõ nhầm nên muốn làm nốt; tôi chọn ra xem ai đang chờ, nhận sổ người lạ mang trả và cùng bạn giữ cửa cảm ơn.'
# Anyone: permission for an open invitation, no claims anyone can safely move heavy equipment.
lines=[
'Huy đặt bảng, định tự làm hết. Tôi còn đang giữ dây: "Can anyone help?" Có ai giúp được không? Tôi hỏi về chỗ buộc nơ còn trống, chưa chọn riêng một người.',
'Bạn bảo việc nhỏ thôi, mình làm luôn cũng được. Tôi muốn những người ghé bàn được thử cùng, chứ không chỉ nhìn thành quả xong sẵn. Huy đặt dây còn lại ra giữa.',
'Tôi nhận phần giữ bảng, mời Huy buộc nơ thử trước. Cậu ngại mình chưa làm đẹp, định trả dây lại. Tôi để mẫu bên cạnh, không giành lấy làm thay.',
'"Anyone can try." Bất kỳ ai cũng được thử. Tôi nói về lượt ở bàn này, không cần người đã từng làm. Huy nhận một đoạn dây, chọn màu mình thích.',
'Huy hỏi có thật lượt thử mở cho cả người mới không. Bạn giúp tôi nói câu bất kỳ ai cũng được thử bằng tiếng Anh nhé.',
'"Anyone can try." Bất kỳ ai cũng được thử. Huy buộc một chiếc hơi lệch, để lại làm mẫu của mình. Tôi giữ bảng cho bạn thêm một lượt, thay vì cất hết dây đi.'
]
for s,n in zip(E['700']['scenes'],lines):s['narration']=n
E['700']['scenes'][4]['stem']='___ can try.';E['700']['plot_vi']='Huy muốn làm sẵn hết các nơ, tôi mở lượt thử cho bất kỳ người mới nào; Huy nhận lượt và giữ chiếc mình thử đầu.';E['700']['title']='Dây để giữa bàn';E['700']['selected_gloss_vi']='bất kỳ ai, lời mời không giới hạn riêng người nào'
vs=['Mascot holds small craft display board while dusty-blue-shirt friend sets ribbon lengths aside to finish alone. No heavy box or cart.',
'Friend lays remaining ribbon lengths in table center for open practice while mascot keeps board upright. No participant list or extra guest.',
'Mascot holds board while friend hesitates with one ribbon beside a simple bow sample. No readable instructions.',
'Friend selects a ribbon color while mascot offers the practice place, no exact claim about ability or equipment.',
'Friend asks about invitation while holding own ribbon length, board ready at table. Top safe region for target gap.',
'Friend attaches one imperfect bow to board and takes another ribbon to try; mascot continues holding board steady. No packed machinery or guarantee.']
for s,v in zip(E['700']['scenes'],vs):s['visual_en']=v
# Everyone: three registered group members, exact reference to this small group.
e=extra(701,'Mai','pale pink')
lines=[
'Khoa cầm ba vé, tôi vẫn đứng đợi. Chưa thấy Mai tới. "Is everyone here?" Mọi người có mặt chưa? Tôi hỏi về nhóm ba người mình đã hẹn.',
'Khoa muốn tôi vào chọn chỗ trước. Tôi bảo đợi ở cửa để Mai khỏi phải tìm một mình. Bạn giữ vé, nhìn đường tới bến cùng tôi thay vì đi ngay.',
'Mai vừa tới, kéo túi chưa kín. Tôi giúp giữ quai, Khoa đưa vé cho bạn. Ba người đều đã có mặt, nhưng tôi vẫn chờ Mai kiểm nốt đồ mình.',
'"Everyone is ready." Mọi người sẵn sàng rồi. Khoa nói khi Mai đóng túi, mỗi người đã cầm vé của mình. Tôi thôi nhìn về đường, nhận phần túi đã giữ giúp.',
'Khoa hỏi có thể vào chưa khi cả nhóm đã chuẩn bị xong. Bạn nói giúp tôi câu mọi người sẵn sàng rồi bằng tiếng Anh nhé.',
'"Everyone is ready." Mọi người sẵn sàng rồi. Tôi đưa lại túi cho Mai, để bạn đi cạnh mình. Khoa giữ cửa, chờ cả hai bước qua rồi mới vào cùng nhóm.'
]
for s,n in zip(e['scenes'],lines):s['narration']=n
for i,s in enumerate(e['scenes']):s['character_ids']=['CH01','CH02'] if i<2 else ['CH01','CH02','CH03']
e['scenes'][4]['stem']='___ is ready.';e['plot_vi']='Khoa muốn tôi vào trước, tôi chọn đợi Mai để ba người cùng vào; cả nhóm kiểm xong đồ, từng người đợi nhau qua cửa.';e['selected_gloss_vi']='mọi người trong nhóm đang nhắc'
vs=['Mascot and mint-shirt Khoa wait beside station gate with three plain tickets; third group member not yet present. No crowded station or readout.',
'Khoa points toward gate while mascot indicates waiting area, both keep tickets together and watch path.',
'Pink-shirt Mai joins two companions, mascot holds her bag strap while Khoa offers one plain ticket. Exactly three registered figures.',
'All three stand prepared with closed bags and one plain ticket each, Khoa announces readiness. No fourth group member.',
'Khoa asks mascot beside prepared Mai, all three remain ready at gate. Top safe space for stem.',
'Khoa holds gate as mascot and Mai enter beside each other, three-person group complete. No driver or additional crowd.']
for s,v in zip(e['scenes'],vs):s['visual_en']=v
for num,e in E.items():
 if num in {'692','693','694','695','697'}:e['selected_gloss_vi']={'692':'chính tôi, nhấn tôi là người làm','693':'chính bạn, nhấn người nghe là người làm','694':'chính anh ấy, nhấn anh ấy là người làm','695':'chính cô ấy, nhấn cô ấy là người làm','697':'chính chúng tôi, nhóm có người nói là người làm'}[num]
 e['scenes'][4]['stem']=e['scenes'][4]['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
