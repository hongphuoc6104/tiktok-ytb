from pathlib import Path
import json
P=Path(__file__).parent/'440-449';d=json.loads((P/'episodes.json').read_text());E={e['job'].rsplit('-',1)[1]:e for e in d['episodes']}
def line(num,i,n):E[str(num)]['scenes'][i-1]['narration']=n
def visual(num,i,v):E[str(num)]['scenes'][i-1]['visual_en']=v
# Remove all code identifiers from visual prose before individual semantic review.
for e in E.values():
 for s in e['scenes']:
  s['visual_en']=s['visual_en'].replace('CH01','the pale-blue mascot').replace('CH02','the companion')
 for c in e['characters']:c['appearance_en']=c['appearance_en'].replace(', no mouth','')
line(682,1,'Tôi giữ tách, chưa dám đưa anh. Lọ đường trống từ hôm qua. Anh Huy nhận lấy: "I drink tea without sugar." Anh uống trà không có đường. Tôi mới đặt tách mình xuống.')
line(682,2,'Anh muốn ngồi cùng tôi hết tách trà trước khi đi xưởng. Tôi định tìm món khác để mời vì ngại hết đường. Anh lắc đầu, kéo ghế cho tôi, chẳng cần đi tìm gì nữa.')
line(682,3,'Mưa bắt đầu ngoài cửa. Anh Huy nhìn giờ, định đi ngay, để chiếc ô lại cho tôi. Tôi đứng lên, giữ tay nắm cửa một chút, không muốn anh ra đường tay không.')
line(682,6,'"Do not go without an umbrella." Đừng đi mà không có chiếc ô. Anh Huy nhận ô, mở ra ngoài cửa. Tôi đứng dưới hiên chào; anh vẫn giữ tách trà vừa uống vào đúng chỗ trước khi đi.')
visual(682,1,'Mascot hesitates offering a plain tea mug while navy-shirt brother reaches to accept it; empty sugar jar on shelf, second mug on table. Two figures only.')
visual(682,2,'Brother pulls a chair closer for mascot beside two tea mugs, empty sugar jar still on shelf. No new sweets or written menu.')
line(683,1,'Tôi giữ hộp, Linh chưa cho mở. Bạn muốn nhắc ai gửi trước. "This gift is from my sister." Món quà này từ chị gái tôi. Tôi đặt hộp xuống, nghe bạn kể.')
line(683,2,'Chị gửi một ít táo quê lên. Linh đã dành hộp này để hai đứa ăn cùng, nhưng tôi tưởng bạn mua ở quán. Tôi nhìn lại lớp giấy chị đã gói, không bóc vội nữa.')
line(683,3,'Tôi muốn gửi lời cảm ơn, Linh bảo gọi một câu được rồi. Tôi lấy giấy, chọn làm tấm thiệp nhỏ. Bạn ngại mất công, tôi xin giữ phần việc này cho mình.')
line(683,4,'"This card is from me." Tấm thiệp này là tôi gửi. Tôi nói với Linh, đưa thiệp để bạn mang giúp. Hai món đến từ hai người khác nhau, tôi muốn chị biết phần của mình.')
line(683,5,'Linh hỏi có cần ghi thiệp là cả hai người gửi không. Bạn nói giúp tôi câu tấm thiệp này là tôi gửi bằng tiếng Anh nhé.')
line(683,6,'"This card is from me." Tấm thiệp này là tôi gửi. Linh nhận, cất riêng vào túi. Tôi mở hộp táo; lần này biết người ở xa đã gói món ấy cho hai đứa.')
E['683']['scenes'][4]['stem']='This card is ___ me.'
E['683']['plot_vi']='Linh muốn tôi biết quà đến từ chị trước khi mở; tôi giữ phần làm thiệp cảm ơn của mình và nhờ bạn mang giúp.'
visual(683,4,'Mascot offers a small handmade blank card to orange-shirt friend beside open box of apples, making its sender clear. No written signature or English sentence.')
visual(683,6,'Friend places handmade blank card into a separate bag pocket while mascot opens apple box at shared table. No visible message text or shipping address.')
line(684,1,'An giữ sách, tôi định lật sang cuối. Bạn chưa muốn bỏ trang này. "This book is about the sea." Cuốn sách này viết về biển. Tôi quay về trang bạn đang giữ.')
line(684,3,'An nói bố từng kể chuyện đi biển theo những hình trong sách. Tôi chỉ muốn xem hết nhanh, nhưng bạn muốn nói về một chuyến mình còn nhớ. Tôi buông mép trang, nghe bạn.')
line(684,4,'"We can talk about the sea." Chúng ta có thể trò chuyện về biển. Tôi đề nghị gấp sách lại một chút, để An kể thay vì cứ phải đuổi theo trang tôi lật.')
line(684,6,'"We can talk about the sea." Chúng ta có thể trò chuyện về biển. An đặt sách sang bên, kể chuyện mình nhớ. Tôi kéo ghế gần hơn, lần này không nhìn xem còn bao nhiêu trang nữa.')
E['684']['plot_vi']='Tôi muốn lật sách nhanh, An muốn kể chuyện biển gắn với bố; tôi chọn gấp sách lại và nghe bạn kể về đúng chủ đề ấy.'
visual(684,4,'Mascot closes sea-illustrated book halfway to invite friend\'s story, brown-shirt friend gestures toward simple sailboat illustration. No printed passages or third person.')
visual(684,6,'Closed illustrated sea book rests aside on table, mascot pulls stool close to brown-shirt friend speaking. No memory vignette of absent father.')
line(685,1,'Mai giữ bút, chưa đưa tôi viết. Tôi đã chuẩn bị giấy, muốn làm biển một mình. Bạn đặt bút xuống: "I have paper and a pen." Tôi có giấy và một cây bút, tôi nói.')
line(685,2,'Giấy của tôi, bút bạn mang tới, cả hai món đều đã có. Mai muốn nhận một phần biển sách mới, nhưng tôi sợ hai nét vẽ không giống nhau nên cứ định tự làm hết.')
line(685,3,'Mai thử một bông hoa ở góc giấy thừa, đưa tôi xem. Tôi nhìn tấm biển còn trống, nhận ra mình chưa cần giành cả chỗ. Tôi đẩy giấy về giữa bàn.')
line(685,4,'"You and I can finish it." Bạn và tôi có thể làm xong. Tôi nói, mời Mai nhận phần viền. Bạn lấy bút, chừa một khoảng trong để tôi viết dòng cần treo.')
line(685,5,'Mai hỏi có thật tôi muốn cùng làm hay chỉ mượn bút thôi. Bạn nói giúp tôi câu bạn và tôi có thể làm xong bằng tiếng Anh nhé.')
line(685,6,'"You and I can finish it." Bạn và tôi có thể làm xong. Mai vẽ viền, tôi viết phần giữa. Treo biển lên, tôi nhường bạn giữ một góc để cả hai cùng chỉnh ngay ngắn.')
E['685']['custom_visible_text']=[{'text':'Sách mới','placement':'center of shared shop sign inside floral border','object':'cardboard shop sign'}]
E['685']['plot_vi']='Tôi chỉ muốn mượn bút và làm biển một mình; Mai cho xem nét vẽ, tôi chia phần để hai người cùng hoàn thành.'
visual(685,1,'Green-shirt friend holds marker back beside mascot and blank cardboard sign. Mascot has supplied paper, friend offers pen for shared work; no labels.')
visual(685,3,'Friend shows simple flower drawing on a separate scrap while mascot moves blank main sign to table center. No ruler or measurement lines.')
visual(685,4,'Mascot indicates blank center region while friend begins floral border. Only the permitted later sign text Sách mới will appear, no hours or inventory list.')
visual(685,6,'Both figures hold opposite lower corners of finished sign bearing permitted Sách mới inside flower border to straighten it at shop door. No opening-hours or extra lettering.')
# Or: two linked drink options, no undeclared cashier or medical issue, complete A1 sentences.
lines=[
'Khoa đẩy tách, định đứng lên đi. Bạn nghĩ tôi chỉ có trà. "Do you want tea or water?" Bạn muốn trà hay nước lọc? Tôi chỉ hai chiếc cốc trống.',
'Tôi muốn mời bạn ngồi sau buổi cùng dọn nhà. Khoa không thích trà, ngại bảo tôi pha lại. Tôi đặt bình nước bên tách, nói bạn có thể chọn một món hợp mình.',
'Bạn còn nhìn tôi như chờ phải uống giống nhau. Tôi tự lấy trà, chừa cốc để Khoa chọn nước. Hai người ngồi cùng không cần giữ cùng một thức uống.',
'"We can drink tea or water." Chúng ta có thể uống trà hoặc nước. Tôi nhắc hai lựa chọn đang có, Khoa với cốc còn trống rồi chỉ bình nước.',
'Khoa vẫn ngại nói lựa chọn của mình. Bạn giúp tôi hỏi câu bạn muốn trà hay nước lọc bằng tiếng Anh nhé.',
'"Do you want tea or water?" Bạn muốn trà hay nước lọc? Khoa nhận nước, ngồi xuống. Tôi kéo ghế lại, giữ tách trà của mình; lần này bạn không phải uống thứ không thích.'
]
for s,n in zip(E['686']['scenes'],lines):s['narration']=n
E['686']['scenes'][4]['stem']='Do you want tea ___ water?'
E['686']['plot_vi']='Khoa ngại uống trà nên định về; tôi cho bạn lựa chọn nước để giữ buổi ngồi chung mà không ép cùng sở thích.'
vs=['Grey-shirt friend begins rising from home table beside tea mug, mascot indicates two empty cups and one water jug. No cafe owner or menu.',
'Mascot places plain water jug beside his tea pot, grey-shirt friend hesitates at same table. No medication or payment signs.',
'Mascot pours own tea while leaving second empty glass for friend beside water jug. No words on cups.',
'Grey-shirt friend reaches toward empty glass and water jug as mascot offers both options. No money or cards.',
'Friend pauses choosing drink while mascot asks him, top safe region for stem.',
'Both figures sit together with different drinks: mascot holds tea mug, friend holds clear water glass; moved-out cartons in background show shared work.']
for s,v in zip(E['686']['scenes'],vs):s['visual_en']=v
# But: honest contrast in words, no limping/pain or implied weather immunity.
line(687,3,'Tôi đề nghị chờ cho tạnh, Bình muốn đưa tôi về cùng. Cậu để ô giữa hai đứa, hỏi tôi có thể đi chậm không. Tôi nhận cầm một bên túi để bạn đỡ phải giữ cả ô lẫn đồ.')
line(687,4,'Đến ngã rẽ, Bình dừng lại nhìn quãng đường còn lại: "I am tired, but I will walk." Tôi mệt nhưng tôi vẫn sẽ đi bộ. Cậu muốn đi cùng, không bỏ tôi ở lại.')
line(687,6,'"I am tired, but I will walk." Tôi mệt nhưng tôi vẫn sẽ đi bộ. Tôi nhận túi giúp Bình, cậu giữ ô. Tới cửa, tôi mời bạn ngồi lại; lần này chẳng cần vội bước tiếp.')
visual(687,3,'Both friends stand beneath small umbrella at ordinary dry-side pavement with only shallow puddles, mascot offers to hold part of friend\'s bag. No flooded alley or injuries.')
visual(687,6,'Two friends arrive beneath home porch; mascot holds friend\'s bag and offers a plain stool, yellow-shirt friend closes umbrella. No miraculous rain ending.')
# So: keep canonical shirt unobscured; use two present causes producing a shared action and decision.
lines=[
'Xe buýt rời trạm, tôi vẫn đứng đợi. Long nhìn tôi: "The bus left, so we will walk." Xe đi rồi nên chúng ta sẽ đi bộ. Tôi cất vé, bước cạnh bạn.',
'Tôi muốn chờ chuyến nữa vì sợ tới xưởng đã hết phần của hai đứa. Long rủ đi ngay, còn hơn chỉ đứng lo ở trạm. Bạn nhận cầm giúp tệp giấy tôi mang.',
'Hai đứa đi được một đoạn, mưa bắt đầu. Long nhìn tệp giấy, tôi cũng không muốn nó ướt. Có hiên ngay bên cạnh, hai người cùng dừng trước khi bước qua chỗ không có mái.',
'"It is raining, so we will wait." Trời đang mưa nên chúng ta sẽ chờ. Tôi nói với Long, chọn giữ trang giấy hai đứa đã làm thay vì cứ chạy tiếp cho nhanh.',
'Long hỏi sao lúc nãy rủ đi mà giờ tôi muốn dừng. Bạn nói giúp tôi câu trời đang mưa nên chúng ta sẽ chờ bằng tiếng Anh nhé.',
'"It is raining, so we will wait." Trời đang mưa nên chúng ta sẽ chờ. Long gật, để giấy giữa hai đứa dưới hiên. Tôi gọi báo tới muộn, rồi ngồi chờ cùng bạn.'
]
for s,n in zip(E['688']['scenes'],lines):s['narration']=n
E['688']['scenes'][4]['stem']='It is raining, ___ we will wait.'
E['688']['plot_vi']='Lỡ xe, Long rủ tôi đi bộ; khi mưa tới, tôi quyết định chờ dưới hiên để giữ bản chung và báo muộn, Long ở lại cùng.'
vs=['Both figures stand at quiet stop with bus departing in distance, red-shirt friend points along path while mascot keeps plain ticket. No readable timetable.',
'Red-shirt friend offers to hold mascot\'s plain paper folder as both prepare to walk. No price or vehicle schedule claim.',
'Light rain starts on ordinary walkway; both figures pause by nearby porch holding paper folder. Mascot retains visible single pale-blue short-sleeve torso.',
'Mascot and red-shirt friend shelter under porch with folder held fully dry between them, no raincoat or jacket.',
'Friend asks mascot while both stay under porch, light rain visible beyond roof; top safe area for stem.',
'Both figures sit under porch with folder between them, mascot holds plain phone screen away to report delay. No cold injury or workshop arrival yet.']
for s,v in zip(E['688']['scenes'],vs):s['visual_en']=v
line(689,3,'Tôi muốn chạy tiếp vì còn hẹn, nhưng Thảo kéo ghế ở hiên ra. Cậu biết tôi chưa ăn, không muốn vừa đi vừa cầm đồ. Tôi dừng lại, nghe xem bạn đã chuẩn bị gì.')
line(689,6,'"I bought food because you were hungry." Tôi mua đồ ăn bởi vì bạn đói. Tôi nhận bánh, kéo ghế bên cạnh cho Thảo. Cuộc hẹn có thể chờ chút; bữa ăn bạn chuẩn bị được hai đứa ngồi ăn chung.')
# Before: first model explicitly matches a door, not a window.
line(690,1,'Quân kéo cửa, tôi còn ở bàn. Bạn định để cửa mở và đi trước. "Close the door before you leave." Đóng cửa trước khi rời đi nhé. Tôi muốn giữ phòng khi dọn nốt.')
line(690,2,'Quân quay lại, chưa khép cửa vì tưởng tôi cũng đi ngay. Tôi nhặt phần giấy còn dưới ghế, xin bạn chờ một chút. Cậu đặt túi xuống, không đứng thúc ở lối ra nữa.')
line(690,3,'Tôi dọn gần xong, Quân giữ cửa cho cả hai cùng ra. Việc khép cửa sẽ phải xong trước lúc rời phòng, đúng điều tôi nhờ. Cậu nhìn đèn còn sáng, gọi tôi lại.')
line(690,6,'"Turn off the light before you go." Tắt đèn trước khi đi nhé. Tôi tắt đèn, Quân đợi bên cửa. Hai đứa khép cửa rồi mới cùng xuống cầu thang, không còn người phải dọn ở lại.')
visual(690,1,'Teal-shirt friend pulls entrance door open to leave while mascot still gathers loose paper at study table; no open window in focus.')
visual(690,2,'Friend sets bag down beside door and waits for mascot to gather last sheets near chair. Entrance door still open, no window latch.')
visual(690,3,'Friend holds entrance door open for both figures and points toward desk lamp still lit; mascot finishes putting papers into bag.')
E['690']['plot_vi']='Quân định đi trước nhưng tôi còn dọn; bạn ở lại đợi, nhắc tắt đèn và cả hai khép cửa trước khi cùng rời phòng.'
# After: support sequential timing by actual states without moralizing that rest must be earned.
line(691,1,'Lâm đặt bút xuống, muốn nghỉ ngay. Tôi chỉ phần cuối hai đứa định nộp hôm nay: "We can rest after we finish." Mình nghỉ sau khi làm xong nhé, tôi đề nghị.')
line(691,2,'Bạn bảo vẫn còn nhiều chi tiết, không muốn cố cả trang nữa. Tôi rủ hoàn thành phần cần trước, giữ phần thêm cho hôm khác. Lâm nhìn lại, chọn một góc muốn sửa.')
line(691,3,'Tôi làm phần mình, chờ Lâm kết thúc góc đã chọn. Bản vẽ xong, hai người đặt bút xuống rồi mới ngồi nghỉ. Bạn ngả ghế, tôi không đưa thêm việc vào ngay.')
line(691,4,'Một lúc sau, Lâm nhìn giấy vụn: "We can play after we clean the room." Mình có thể chơi sau khi dọn phòng. Bạn muốn cất đồ trước rồi mới ra sân, để mai đỡ phải tìm.')
line(691,6,'"We can play after we clean the room." Mình có thể chơi sau khi dọn phòng. Tôi gom giấy, Lâm cất bút. Xong phần dọn, bạn kéo cửa ra sân, giữ cho tôi bước cùng.')
visual(691,3,'Both figures sit resting with pens laid down beside completed unlabelled drawing; no active sketching or instant cure from drink.')
for e in E.values():
 e['scenes'][4]['stem']=e['scenes'][4]['stem'].strip().strip('"').replace('___ .','___.').replace('___ ?','___?')
(P/'edited.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
