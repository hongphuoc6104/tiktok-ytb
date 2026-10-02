from pathlib import Path
import json
P=Path(__file__).parent/'420-429';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def patch(num,lines=None,title=None,plot=None):
 e=E[str(num)]
 if lines:
  for s,n in zip(e['scenes'],lines):s['narration']=n
 if title:e['title']=title
 if plot:e['plot_vi']=plot
 return e
patch(662,[
'Nam cứ bước nhanh hơn tôi. Hai đứa cùng mang thùng quà qua cửa. "Watch your step." Cẩn thận bước chân nhé. Tôi nhắc bạn nhìn chỗ chân đang đặt.',
'Nam muốn đem quà vào ngay để mở, còn tôi chưa qua được bậc cửa. Tôi giữ đầu thùng, nhờ cậu dừng một chút. Bạn nhìn xuống, chờ chân tôi tới gần.',
'Thùng che khuất phần chân trước mặt. Tôi đổi chỗ cầm để nhìn rõ, Nam vẫn giữ đầu kia. Hai người không kéo mạnh, cùng thử dịch thêm một bước.',
'"Take one step." Bước một bước thôi. Tôi nói với Nam khi đã cùng tới sát ngưỡng cửa. Một bước chân nữa đủ đưa đầu thùng qua, rồi mình mới đặt xuống.',
'Nam đang đợi tôi ra hiệu nhấc chân tiếp. Bạn nói giúp tôi câu bước một bước thôi bằng tiếng Anh nhé.',
'"Take one step." Bước một bước thôi. Nam bước qua cùng tôi, hai đứa đặt thùng trên sàn. Tôi ngồi ngay bậc cửa, chờ bạn lấy kéo để mở quà chung.'
],title='Chờ chân tôi qua cửa',plot='Nam muốn mang quà vào nhanh, nhưng phải chờ bạn cùng nhịp bước qua bậc cửa để mở quà chung.')
vs=['Two minimal figures carry a small plain gift box toward a dry indoor threshold, green-shirt figure ahead of mascot. No wet floor or heavy crate.',
'Both pause carrying same small box, mascot points down toward his foot still behind doorway threshold.',
'Mascot shifts one grip to see own feet while green-shirt companion holds opposite end of the same box. No strained fingers or injury.',
'Side angle of both figures stopped at dry threshold, each foot just before the raised sill, same small box shared.',
'Green-shirt companion waits beside threshold with box, mascot prepares short instruction. Top safe area for stem.',
'Box now rests indoors, mascot sits on threshold while green-shirt companion takes plain scissors from nearby table to open gift together.']
for s,v in zip(E['662']['scenes'],vs):s['visual_en']=v
E['662']['extra_visual_states']=[{'quote':'Nam bước qua cùng tôi,','visual_en':'Same doorway camera as preceding practice: both figures now have their leading feet on the indoor side of the dry sill while holding the same shared box.','purpose_en':'Demonstrate one actual step changing foot position across threshold before the box is lowered.'}]
patch(663,[
'An chèn hộp nhỏ xuống dưới cùng. Tôi giữ lại vì thiệp sẽ bị che. "Put it on top." Đặt nó lên trên cùng nhé. Đây là hộp quà em làm cho bà.',
'An ngại hộp mình nhỏ và gói còn lệch, muốn giấu dưới những hộp khác. Tôi bảo bà cần thấy phần em đã làm. Em giữ hộp, chưa dám xếp lên ngay.',
'Tôi đặt những hộp lớn thấp xuống bàn cho em dễ với. An nhìn chỗ cao nhất của chồng hộp, không còn bị hộp nào che. Em đưa món nhỏ lên đó.',
'"It is at the top." Nó ở phần trên cùng. Tôi chỉ hộp em vừa đặt. An nhìn lại, lấy tấm thiệp để gắn cùng, nhưng chưa biết đặt ở đâu.',
'Em đang cầm thiệp, chờ tôi chỉ chỗ trên cùng của hộp quà. Bạn nói giúp tôi câu đặt nó lên trên cùng nhé bằng tiếng Anh.',
'"Put it on top." Đặt nó lên trên cùng nhé. An đặt thiệp lên hộp mình. Tôi lùi lại cho em xem; lần này em giữ món quà ở chỗ dễ thấy, không giấu nữa.'
],title='Không giấu hộp nhỏ',plot='An ngại quà tự gói nên muốn giấu dưới chồng hộp; tôi giúp em đặt lên phần trên cùng và giữ thiệp của mình ở đó.')
E['663']['scenes'][4]['stem']='Put it on ___. '
vs=['Yellow-shirt cousin slips small unevenly wrapped gift beneath three larger boxes on low table, mascot gently stops the action. No tall cabinet or cake.',
'Cousin holds small crookedly wrapped box uncertainly, mascot indicates free place above larger boxes on the same low table.',
'Mascot lowers larger boxes into a stable short stack below cousin\'s chest height; cousin lifts small gift toward uppermost surface.',
'Small handmade box now rests uppermost on low short gift stack, both figures look at it. No wobbling or raised platform.',
'Cousin holds a plain blank card beside the topmost small gift, looking at mascot to ask placement. Top safe region for stem.',
'Blank card lies on top of cousin\'s small unevenly wrapped gift; both figures step back to inspect the modest low stack. No letters.']
for s,v in zip(E['663']['scenes'],vs):s['visual_en']=v
patch(664,[
'Lâm kéo máy thu âm vào túi. Bạn ngại giọng mình nhỏ quá. "I hear your voice." Tôi nghe thấy giọng cậu. Tôi xin Lâm đừng cất máy ngay.',
'Hai đứa phải gửi đoạn đọc để xin thử vai. Lâm cứ muốn nói lớn như tôi, nhưng càng cố càng mất nhịp. Tôi để bản kịch trước bạn, nghe một câu bình thường.',
'"You have a soft voice." Cậu có giọng nói nhẹ nhàng. Tôi nói về giọng của chính Lâm, không bảo cậu đổi thành người khác. Bạn ngồi lại, thử câu mình thích.',
'Tôi ngồi xa hơn để Lâm biết âm giọng ấy vẫn nghe được ở chỗ này. Bạn thôi che mặt máy, đọc như lúc nói với tôi. Tôi không đọc hộ, chờ bạn xong câu.',
'Lâm hỏi từ góc phòng tôi còn nghe giọng cậu không. Bạn nói giúp tôi câu tôi nghe thấy giọng cậu bằng tiếng Anh nhé.',
'"I hear your voice." Tôi nghe thấy giọng cậu. Lâm lấy máy khỏi túi, giữ lại đoạn vừa đọc. Cậu hỏi tôi có muốn ghi phần của mình ngay bên cạnh không.'
],title='Máy thu âm chưa cất',plot='Lâm ngại giọng nhỏ nên định bỏ ghi thử vai; tôi nghe và chấp nhận giọng riêng của bạn, cậu giữ lại đoạn vừa đọc.')
E['664']['scenes'][0]['visual_en']='Orange-shirt learner begins placing small recorder into bag beside a script with abstract non-legible lines; mascot gestures to keep it out. No throat pain or illness.'
E['664']['scenes'][2]['visual_en']='Orange-shirt learner sits relaxed at table and speaks toward small recorder, mascot listens; no mug, medication or physical trembling.'
E['664']['scenes'][5]['visual_en']='Orange-shirt learner takes recorder out of bag and places it between both friends next to script, inviting mascot to record too. No audio waveform or success certificate.'
patch(665,[
'Linh bỏ trống ô tuổi của mèo. Tôi mới nhận nuôi nên chẳng có giấy ghi. "What is its age?" Tuổi của nó là bao nhiêu? Bạn hỏi khi làm thẻ cho tôi.',
'Tôi ôm chú mèo, nhớ chỉ biết ngày mình đón nó. Linh bảo ô này hỏi nó bao nhiêu tuổi, không hỏi đã ở nhà tôi bao lâu. Tôi gật, nhìn lại chỗ trống.',
'Bạn định ghi số mình đoán. Tôi giữ bút lại, không muốn thẻ mang một con số sai. Mèo vẫn nằm trong giỏ, hai đứa chưa có thông tin để điền chắc.',
'"I do not know its age." Tôi không biết tuổi của nó. Tôi nói rõ với Linh, xin để trống và hỏi người đã chăm mèo trước. Bạn đặt bút sang bên.',
'Linh cần nghe lại phần tôi chưa biết để khỏi tự điền số. Bạn nói giúp tôi câu tôi không biết tuổi của nó bằng tiếng Anh nhé.',
'"I do not know its age." Tôi không biết tuổi của nó. Linh để ô ấy trống, ghi phần còn biết. Tôi mang thẻ về cạnh giỏ mèo, nhớ việc cần hỏi thêm.'
],title='Ô tuổi còn trống',plot='Tôi chưa biết tuổi mèo mới nhận nuôi và ngăn bạn ghi số đoán trên thẻ; hai người giữ ô tuổi trống để hỏi lại nguồn biết rõ.')
E['665']['scenes'][4]['stem']='I do not know its ___. '
vs=['Mascot and purple-shirt friend sit at a home table with a simple kitten in basket and blank pet information card. No clinic or medical chart.',
'Friend points to one empty box on blank pet card, mascot holds basket edge looking uncertain. Cat stays inside basket.',
'Mascot stops friend\'s pencil above blank box before an invented number is entered. Kitten remains in basket, no teeth check.',
'Mascot explains uncertainty while friend puts pencil aside. Same blank card, no age diagnosis.',
'Friend pauses beside blank card listening to mascot; top safe area for age-gap practice.',
'Mascot places partly completed card with non-letter marks and one still-empty box beside kitten basket. No age number or medical care scene.']
for s,v in zip(E['665']['scenes'],vs):s['visual_en']=v
E['665']['characters'].append({'id':'CH03','name_vi':'Mèo con','appearance_en':'Small minimal ink kitten with round simple head, two solid dark oval eyes, simple triangular ears, tiny tail and minimal line paws; no clothing or human torso.','outfit_en':'No clothing, plain soft grey coat.'})
for s in E['665']['scenes']:s['character_ids'].append('CH03')
patch(666,[
'Mai giữ cuốn sách tôi định mượn. Gáy đã sờn, cô không muốn mang ra ngoài nữa. "This is a good book." Đây là một quyển sách hay, cô nhắc trước khi cất.',
'Tôi tìm tập thơ Mai giới thiệu từ tuần trước. Cô cho tôi xem nhưng lo những trang cũ bị gập trong túi. Tôi đặt túi xuống, kéo ghế cạnh giá sách nhà cô.',
'Mai mở vài trang, giữ mép nhẹ bằng tay. Tôi thấy cô còn ghi dấu những đoạn mình thích. Cuốn sách này mang cả việc đọc của bạn, không chỉ phần tôi đang tìm.',
'"Can I read this book?" Tôi đọc quyển sách này được không? Tôi xin ngồi đọc ngay đây, không mượn về. Mai nhìn chiếc túi đã đặt xuống, đưa sách sang.',
'Mai hỏi tôi muốn làm gì với quyển sách khi không mang đi. Bạn nói giúp tôi câu tôi đọc quyển sách này được không bằng tiếng Anh nhé.',
'"Can I read this book?" Tôi đọc quyển sách này được không? Mai gật đầu. Tôi mở đoạn cô đánh dấu, đọc cùng bạn; chiếc túi vẫn ở dưới ghế, chưa cần mang sách đi.'
],title='Đọc ngay cạnh Mai',plot='Mai không muốn cho mượn sách cũ dễ gập trang; tôi chọn ngồi đọc ở nhà bạn để giữ cuốn sách và buổi đọc chung.')
E['666']['scenes'][4]['stem']='Can I read this ___?'
E['666']['scenes'][0]['visual_en']='Pink-shirt friend holds back one worn cloth-bound book beside a home bookshelf, mascot pauses with bag over shoulder. No bookstore labels.'
E['666']['scenes'][2]['visual_en']='Close view of open book with non-legible printed strokes and small pencil marks, friend holds fragile page corners with simple stick hands. No readable verses.'
E['666']['scenes'][5]['visual_en']='Two friends sit reading same worn book at home table; mascot\'s bag remains closed under stool. No book wrapping or leaving store.'
patch(667,[
'David đẩy album sang, tôi giữ mép lại. Bạn định cất ảnh quê Mỹ. "I love the fall." Tôi yêu mùa thu. Tôi nói, muốn xem mùa ấy thêm một chút.',
'David từng rủ tôi về thăm vào mùa thu, tôi cứ tưởng bạn thích mùa nóng. Cậu chỉ hàng cây đổi lá trong ảnh, kể lúc chụp đúng mùa thu ở quê nhà.',
'Người Mỹ gọi mùa thu bằng fall như câu tôi vừa nói. Tôi nhìn lại ảnh hai đứa đứng dưới hàng cây, nhận ra lần đầu đến đó mình còn mượn khăn của David.',
'"We met in the fall." Chúng tôi gặp nhau vào mùa thu. Tôi nhắc thời điểm hai đứa quen nhau, David dừng tay cất album. Bạn cũng giữ tấm ảnh ấy lâu nhất.',
'David hỏi tôi có còn thích mùa trong ảnh không. Bạn nói giúp tôi câu tôi yêu mùa thu bằng tiếng Anh nhé.',
'"I love the fall." Tôi yêu mùa thu. David kẹp chiếc lá khô vào đúng trang ảnh hai đứa. Tôi giữ album mở, nhờ bạn kể nốt chuyện của buổi ấy.'
],title='Trang thu chưa cất',plot='Tôi muốn xem thêm trang thu ở quê Mỹ của David, nhớ hai người gặp nhau vào mùa ấy và giữ buổi chuyện bên album.')
E['667']['scenes'][1]['visual_en']='Mascot points to an unlabeled photograph of orange-leaf trees in album while grey-shirt friend rests hand near page, no extra people.'
E['667']['scenes'][2]['visual_en']='Album photograph contains the same pale-blue mascot and grey-shirt friend under orange-leaf trees; these are same two registered figures, no family group or third person.'
E['667']['scenes'][5]['visual_en']='Grey-shirt friend places pressed maple leaf inside the same album page while mascot keeps album open to continue listening. No leaf transfer as gift or extra people.'
# Take photograph: the requesting speaker is Tuấn, not the photographer.
E['669']['scenes'][4]['narration']='Tuấn đứng cạnh bức vẽ, muốn nhờ tôi chụp cả mình trong ảnh. Bạn nói giúp cậu câu chụp cho tôi một bức ảnh bằng tiếng Anh nhé.'
E['669']['scenes'][3]['visual_en']='Olive-shirt friend asks mascot to include him in photo beside mural; one simple wave, no realistic victory-sign fingers.'
E['669']['scenes'][0]['narration']='Tuấn tránh khỏi góc tôi đang chụp. Bức tranh đầu hẻm vừa xong. "Can I take a photo?" Tôi chụp một tấm ảnh được không? Tôi hỏi trước khi giơ máy.'
E['669']['scenes'][1]['narration']='Cậu tưởng tôi chỉ muốn chụp bức tường, không muốn áo dính sơn của mình lọt vào. Tôi bảo đó cũng là phần buổi vẽ của hai đứa, cậu đứng cùng mới đủ.'
E['669']['scenes'][2]['narration']='Tuấn nhìn áo rồi bước lại, nhưng vẫn nép một bên. Tôi hạ máy chờ, không giục cậu tạo dáng. Cậu tự chọn chỗ cạnh phần tranh mình đã vẽ.'
E['669']['scenes'][5]['narration']='"Take a photo of me." Chụp cho tôi một bức ảnh. Tôi bấm máy. Tuấn xin giữ cả vệt sơn trên áo trong ảnh, rồi kéo tôi đứng cùng để chụp thêm.'
# Need: preserve actual speaker role and retrieve the first request while action is unresolved.
E['670']['scenes'][4]['narration']='Dũng đang giữ giấy giúp, hỏi tôi còn cần đồ gì. Bạn nói giúp tôi câu tôi cần vài cái ghim bằng tiếng Anh nhé.'
E['670']['scenes'][4]['stem']='I ___ some pins.'
E['670']['scenes'][5]['narration']='"I need some pins." Tôi cần vài cái ghim. Dũng đưa vỉ ghim, tiếp tục giữ góc giấy. Tôi ghim xong, quay lại hỏi bạn có muốn cùng sửa nốt tấm còn lại không.'
E['670']['scenes'][5]['visual_en']='Poster now fixed at its two upper corners; mascot holds remaining pins while brown-shirt friend still steadies lower edge. A second plain poster waits on table, no readable announcement text.'
# Avoid instructional operating hazards or unlisted hands in see story.
E['671']['scenes'][2]['visual_en']='Mascot kneels beside the grass patch under phone light; one minimal stick hand parts a few tall blades, no exposed ditch or risky river edge.'
E['671']['scenes'][0]['visual_en']='Both figures stand beside parked bicycle on an ordinary park path with grass along edge at dusk. No river, ditch or dangerous waterside.'
E['671']['scenes'][5]['visual_en']='Mascot gives retrieved key ring to lavender-shirt sibling beside stationary bicycle on ordinary park path. Minimal hands, no riverside hazard.'
E['671']['scenes'][2]['narration']='Hà lắc đầu, định bỏ cuộc để ngày mai tìm tiếp. Tôi xin em chờ một chút, rọi đèn thấp vào cỏ. Em ngồi cạnh, giữ xe giúp tôi thay vì cứ lục túi.'
# Standardize quoted practice stems to one gap without spurious punctuation/spaces.
for e in E.values():
 s=e['scenes'][4];s['stem']=s['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
for num in ['668','669']:E[num]['selected_gloss_vi']='lấy, cầm' if num=='668' else 'chụp ảnh'
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
