import json,pathlib,re
P=pathlib.Path('/home/hongphuoc6104/Desktop/pipelineFlow/sys/reports/drama-A1-all-20261001');O=P/'shards/nhom-1';old=O/'style-612-631-originals';old.mkdir(exist_ok=True)
m={int(x['job'].split('-script-')[-1]):x for x in json.loads((P/'manifest.json').read_text())}
E={}
for n in range(612,632):
 j=m[n]['job'];f=P/'narration-frozen'/f'{j}.json';e=json.loads(f.read_text());snap=old/f.name
 if not snap.exists():snap.write_text(json.dumps(e,ensure_ascii=False,indent=2))
 E[n]=e
# Explicit human editorial changes; originals above remain intact.
changes={
612:{3:'Mặt bàn vẫn còn một vết xước nhỏ ở góc. Huy cúi nhìn, hỏi có cần sơn lại không. Minh lắc đầu, bảo chỗ ấy cứ để, nhìn là nhớ hai đứa đã loay hoay cả buổi.',4:'\"I like this feeling.\" Tôi thích cảm giác này. Minh trả lời khi Huy hỏi có tiếc cả buổi chiều không. Cậu kéo ghế lại, mời bạn ngồi, lần này không phải kéo tới để sửa bàn nữa.'},
613:{3:'Minh nhìn cặp lồng, hỏi Bình đã phải đi vòng xa không. Anh gật đầu, bảo mẹ vẫn sợ cậu bỏ bữa. Minh kéo ghế, giữ quai túi của anh lại một chút, xin ngồi ăn cùng mình.',6:'\"Thank you for your love.\" Cảm ơn sự yêu thương của anh. Bình đặt túi xuống, giữ bát để Minh múc cháo. Minh gọi mẹ, kể hai người đang ăn đúng món mẹ đã gửi.'},
614:{3:'Dũng bảo đã dọn cả hai hôm liền. Minh ngồi nghe hết, thôi nhìn điện thoại. Cậu đề nghị nhận phần cuối tuần, nhưng Dũng bảo tối nay cũng muốn được nghỉ. Minh nhìn chồng bát, gật đầu.',5:'Dũng hỏi Minh có muốn nghe phần việc nào còn thiếu không. Bạn nói giúp Minh câu mình nói chuyện được không bằng tiếng Anh nhé.'},
615:{2:'Khách gật đầu rồi đưa vé. Minh định chỉ xe ngay, nhưng lại đứng ngập ngừng, sợ nói sai. Khách đặt vé lên quầy, nói chậm hơn, đợi cậu nhìn kỹ rồi mới hỏi tiếp.',6:'\"I speak a little English.\" Tôi nói được một chút tiếng Anh. Khách chỉ vào vé, hỏi từng ý ngắn. Minh tìm đúng xe, giữ cửa cho khách bước tới. Khách quay lại vẫy tay, Minh mới về quầy.'},
616:{2:'Hà ngẩng lên mà tay vẫn lướt. Minh đặt bình tưới xuống, đứng đợi. Em hỏi anh chưa nói à. Minh nhìn chiếc máy, Hà mới úp màn hình lại, kéo ghế để anh ngồi cạnh.',4:'\"Listen to the story.\" Nghe câu chuyện này nhé. Minh kể ông đã mang chậu lan về lúc hai anh em còn nhỏ. Hà thôi nhìn điện thoại, hỏi hôm ấy ông đặt chậu ở đâu.'},
617:{3:'Minh mở phong bì, thấy lá thư gấp làm đôi. Bạn vẫn viết nghiêng như hồi ngồi cạnh ở lớp. Cậu giữ giấy phẳng, đọc chậm từng dòng, Chú Tám đứng đợi vì thấy cậu chưa nói được ngay.',6:'\"I got a letter from my friend.\" Tôi nhận được thư từ bạn mình. Chú Tám đi tiếp. Minh mang giấy ra hiên, đặt thư cạnh tờ giấy mới. Cậu chưa biết mở đầu thế nào, nhưng không muốn để bạn chờ như lần trước.'},
618:{2:'Lan bảo nhìn cả đoạn là muốn bỏ, sợ mình đọc sai trước Minh. Cậu lấy mảnh giấy che các dòng dưới, chừa câu ngắn đang báo người viết ở đây. Cậu nói chỉ đọc chỗ này trước thôi.',3:'Lan chỉ từng từ, chưa nối lại được ý. Minh đợi cô nhìn hết dòng, nhắc câu này đã nói trọn một điều. Lan ngừng đếm chữ, thử đọc cả câu, rồi nhìn Minh xem cậu có đang nghe không.',6:'\"Read this sentence.\" Đọc câu này nhé. Lan đọc xong rồi tự kéo giấy xuống tiếp. Minh định đưa tay giúp, cô giữ mép giấy lại. Cậu rút tay, ngồi đợi cô tìm câu tiếp theo.'},
619:{2:'Minh nhìn chỗ An chỉ. Em bảo thấy hình bánh nhưng vẫn chưa biết nắp mở bên nào. Minh đặt hộp sát lại, chỉ đúng từ em chưa hiểu, không nhấc nắp hộ em ngay.',3:'Minh đọc phần chữ rồi chỉ chiếc tai mở ngay cạnh đó. An cầm thử, hỏi có phải chữ ấy chỉ việc cần làm ở đây không. Minh gật đầu, để em tự kéo, vẫn giữ đáy hộp giúp.',6:'\"What does this word mean?\" Từ này nghĩa là gì? Minh ngồi xuống xem chữ dưới đáy cùng An. Mở được hộp, em giữ riêng nắp, hỏi lần sau gặp chữ khác có được đem tới hỏi nữa không.'},
620:{2:'Mai chuẩn bị thẻ để bạn đoán hành động. Cô đã biết câu trên thẻ là tôi chạy, nhưng không muốn ghi nhầm loại từ. Minh chỉ vào run, hỏi cô thấy người nói đang làm gì.',3:'Minh chạy vài bước rồi dừng lại. Mai nhìn thẻ, bảo từ chạy nói đúng việc cậu vừa làm. Cô giữ thẻ lâu hơn, hỏi nếu đổi người diễn thì vẫn dùng câu này được chứ. Minh nhắc phải đọc cả câu, không chỉ nhìn hình.',6:'\"Is this a verb?\" Đây có phải động từ không? Minh gật đầu, Mai cất lại thẻ đang có câu. Cô đưa hộp cho cậu, bảo vào chơi cùng nhé, để cậu chạy lại động tác vừa làm cho mọi người đoán.'},
621:{2:'Nam cần nhãn cho góc đồ dùng mà cứ khoanh chữ miêu tả. Minh kéo chiếc ghế lại gần, hỏi bạn muốn gọi tên món nào. Nam chạm tay vào lưng ghế, nhìn câu bên cạnh thêm một lần.',3:'Minh chỉ chair, từ gọi tên chiếc ghế trong câu này. Nam bảo lúc nãy mình nhìn phần chữ mà không nhìn đồ thật. Cậu giữ chiếc ghế cho ngay, nhờ Minh để thẻ cạnh đó để tự chọn lại.',6:'\"Find the noun in this sentence.\" Tìm danh từ trong câu này nhé. Nam gạch dưới chair rồi đặt thẻ cạnh chiếc ghế. Cậu kéo ghế cho Minh ngồi, bảo phần nhãn tiếp theo mình muốn thử trước.'},
622:{2:'Minh nhìn nhãn rồi nhìn túi xanh. Mai sợ chỉ ghi túi thì lát nữa vẫn trao nhầm. Cậu chỉ blue, chữ đang tả màu xanh, giữ hai túi cách nhau để cô so lại.',3:'Mai đặt nhãn cạnh túi xanh, hỏi có cần thêm hình nữa không. Minh bảo cứ nhìn chữ tả màu trên nhãn trước. Cô đọc lại cả cụm, rồi nhận ra mình đang cầm nhãn cho đúng chiếc muốn tìm.',6:'\"Find the adjective here.\" Tìm tính từ ở đây nhé. Minh chỉ blue, Mai dán nhãn lên túi xanh. Cô nhấc túi nâu đặt sang ngăn khác, bảo lần sau cậu cứ hỏi lại, để cô tự kiểm trước.'},
623:{3:'Bình hỏi vì sao không để kéo trên bàn mình cho tiện. Minh chỉ ngăn trống, bảo người tới sau sẽ tìm ở đó. Bình nhìn chiếc thiệp còn dở, nói mình làm xong rồi sẽ đem trả, không mang về.'},
624:{2:'Minh chưa biết vì sao cây héo, cũng không muốn đoán thay Hải. Cậu mở vở môn khoa học, bảo mang câu hỏi tới lớp cùng hai ảnh nhé. Hải nhìn phần mình vừa định xóa, để bút xuống.',3:'Hải hỏi Minh có đi học cùng để hỏi chuyện cây không. Minh gật đầu, lấy ảnh ra khỏi túi. Hai chậu nhìn khác nhau, nhưng cậu chưa bảo thêm nước hay làm gì khác; câu hỏi vẫn nằm giữa bàn.'},
625:{2:'Khoa bảo chắc thuyền sẽ nổi thôi. Minh hỏi mình đã thả chưa. Khoa nhìn khay còn khô, bảo chưa. Cậu hạ bút xuống, nhấc thuyền lên nhưng đợi Minh mang nước tới rồi mới đặt vào.'},
626:{2:'Lan lắc đầu, bảo nhìn trang đầy số là ngại. Minh xin ngồi kiểm cùng từng phần, hỏi cô còn giữ giấy ghi từ sáng không. Lan đẩy chồng sách sang bên, tìm thêm dưới mép bàn.',3:'Hai bạn cộng lại những khoản đã ghi. Lan thấy một mẩu giấy còn kẹp trong cuốn sách, hỏi có phải mình quên nhập chỗ này không. Minh ngồi đợi cô tự thêm, không lấy bút ghi hộ.'},
627:{3:'Bác Thành xoay mẩu giấy hẹn, sợ mình đã nhớ muộn. Minh chỉ hai kim: chín giờ đúng, chưa có phút lẻ. Bác nhìn lại lời hẹn, hỏi có nên gọi trước khi đóng cổng không.'},
628:{2:'Huy gật đầu, bảo hay tới đọc sau buổi học, có hôm lại ở nhà. Minh lật mấy ảnh cùng một góc bàn, thấy cuốn sách mỗi lần khác nhau. Huy giữ một tấm lại, muốn cho cậu xem chỗ mình thích.',6:'\"Do you often go there?\" Bạn có thường tới đó không? Huy gật đầu. Chiều ấy Minh đặt sách xuống bàn cạnh cửa sổ, hỏi có thể ngồi lại lâu một chút không. Huy kéo ghế của mình sang bên, chừa chỗ cho bạn.'},
629:{2:'Minh bảo lần nào đi buổi học này cũng mở sổ kiểm trước. Nam hỏi kể cả đã nhớ giờ rồi à. Minh gật đầu, đưa trang mình vừa ghi cho bạn xem, rồi mới cất sổ vào ngăn quen.',6:'\"I always check my notebook.\" Tôi luôn kiểm sổ. Nam mở lại trang vừa ghi, tự đặt sổ vào túi. Minh giữ cửa, đợi bạn kéo khóa xong. Nam hỏi có phiền vì phải đợi không, Minh bảo vẫn còn kịp.'},
630:{2:'Hai đứa cùng thuê căn hộ này. Minh bảo từ khi đi lớp ấy, lần nào cũng để khóa trong túi, chưa quên lần nào. An nhìn chìa cậu đưa, xin quay vào lấy chiếc của mình trước khi đi.',3:'Minh mở cửa, đứng đợi ở bậc thềm. An tìm được khóa dưới cuốn vở, hỏi sao Minh vẫn chưa đi trước. Cậu chỉ chiếc túi còn ở trong nhà của An, bảo cứ kiểm cho xong, mình đi cùng.',6:'\"I never forget my key.\" Tôi không bao giờ quên chìa khóa. An mang khóa ra, cất riêng rồi tự kiểm lại. Minh khép cửa, đứng cạnh chờ, tới khi bạn gật đầu hai đứa mới cùng bước đi.'},
631:{2:'Linh tưởng cuối tuần nào Minh cũng đi chơi. Cậu bảo có hôm ở nhà, có hôm ra ngoài, chiều nay muốn ăn cùng cô. Linh ngừng viết thêm tên, hỏi ở nhà thật cũng tính là một buổi hẹn à.',4:'\"We sometimes cook together.\" Chúng tôi thỉnh thoảng nấu cùng nhau. Minh nhắc những buổi đã làm chung, Linh nhìn lại tấm ảnh rồi chừa trống một chiều. Cô hỏi lần này có được tự chọn món không.'}
}
visual={
612:{3:'Same evening camera: dry painted table has one small remaining scratch at corner. Grey friend points to it, mascot smiles and leaves it unchanged; both relax.'},
613:{3:'Mascot pulls empty stool beside opened porridge container while brown cousin still holds bag strap, they look at each other; no third person.'},
614:{1:'Kitchen, olive-green single-shirt roommate washes dishes with back stiff, mascot hesitates at doorway; no extra apron layer.',2:'Same sink, olive-green single-shirt roommate shuts tap and turns slightly toward mascot who waits; one torso each.',5:'Both already seated at kitchen table beside blank chore grid; olive friend points toward remaining dishes, mascot invites more conversation. No roommate suddenly standing or unlisted person.'},
615:{2:'Same terminal counter, beige traveler places unprinted ticket down and waits while mascot hesitates, blue and grey buses beyond shelter.',6:'Traveler at open stationary blue bus door waves to mascot who has held the doorway open, no driver/passengers or destination print.'},
616:{2:'Same veranda, younger cream-shirt sister still holds phone faceup while mascot waits beside watering can, no legible UI.',4:'Two siblings now seated side by side by orchid, younger sister phone remains facedown and she asks questions about plant history.'},
617:{3:'Mascot slowly reads unfolded paper letter with non-readable ink strokes, dark-green mailman waits at gate, same envelope in mascot hand.'},
618:{2:'Mascot covers lower text with blank paper strip, leaving only permitted We are here now. visible, yellow friend looks carefully.',3:'Close stable shot of permitted We are here now. as one complete sentence with initial W and final period, learner reads entire line instead of counting.',4:'Yellow learner slides covering strip slightly to expose second copy of same permitted We are here now., mascot waits without reading for her.',6:'Yellow learner controls covering strip herself while mascot withdraws helping hand and waits. Only permitted We are here now. appears on page, no thumbs-up lecture pose.'},
619:{2:'Orange younger figure points to exact permitted OPEN beside opening tab on tin lid, mascot holds base without opening it for learner.',3:'Same tin and OPEN next to opening tab, learner tries tab while mascot steadies tin; no separate new word or label.'},
620:{2:'Lavender learner points to run within exact I run. flashcard, mascot prepares to demonstrate, sorting trays remain blank.',3:'Mascot demonstrates short running stride beside table while lavender learner holds same I run. card. No new sentence or unrelated state illustration.',6:'Learner puts same I run. card back in single running-symbol tray and offers it to mascot, no magically sorted second stack or extra group on screen.'},
621:{1:'Capped single-white-shirt learner at desk erases choice on card I need a chair., mascot indicates chair beside him; no unrelated words visible.',3:'Same card I need a chair. with chair circled by mascot, learner steadies real chair beside table; no generic definition text.'},
622:{2:'Dark-grey learner and mascot compare exact blue bag label to one blue and one brown bag, no separate blue-only note replacing label.',4:'Same lost-property shelf and label blue bag, learner hands label toward mascot for checking; no list at unrelated desk.'},
623:{2:'Mascot points to blank storage slot with scissors silhouette while brown learner pauses with scissors, no written wall rules.'},
624:{2:'Same table, mascot opens science notebook with plant diagrams and blank labels, olive learner lowers eraser; two plant photos beside question page.',3:'Both look at plant photographs and question page, water can and treatments absent, pencil set down while they choose to bring question to class.'},
625:{2:'Dry paper boat held by beige learner beside still-empty shallow tray, mascot brings water jug, observation report unmarked and no claim already confirmed.'},
627:{1:'Two figures beside station clock with only9 and12 numerals, other positions tick marks, hour hand9 and minute hand12.',2:'Same clock showing9:00 using hour hand9 and minute hand12; mascot holds plain note9:00 beside elderly figure, no full numeral ring.',3:'Same clock and9:00 note, mascot indicates both hands while elderly figure considers calling; no printed grammar rule.',4:'Elderly figure holds note9:00 and own phone, same clock behind.',5:'Elderly figure on phone holds note9:00 to confirm agreement, mascot beside station gate.'},
628:{2:'Two friends compare several photos of same library table by window with different books on each visit, no readable dates or unlisted readers.'},
629:{4:'Mascot gives extra pen to plain forest-green short-sleeve friend, each has own notebook and mascot retains own second pen. No hoodie or extra layer.'},
630:{2:'Mascot holds own key beside plain-purple short-sleeve friend and closed apartment door; no key copying or lock instructions.'},
631:{3:'Mascot shows photo of just these same two listed figures sharing home meal, yellow-shirt friend considers own planner with non-readable marks.',4:'Both figures at same planning table with photo of shared meal and planner, friend chooses a blank space. No arbitrary jump to cooking scene.'}
}
for n,z in changes.items():
 for i,t in z.items():E[n]['scenes'][i-1]['narration']=t
for n,z in visual.items():
 for i,t in z.items():E[n]['scenes'][i-1]['visual_en']=t
# Explicit allowed data for pedagogical grammar/time examples, with unchanged target meaning.
for n,text,place,obj in [(618,'We are here now.','Exposed line on worksheet','Reading worksheet'),(619,'OPEN','Beside tin opening tab','Cookie tin lid'),(620,'I run.','Only sentence on held flashcard','Grammar flashcard'),(621,'I need a chair.','Only sentence on held card','Grammar card'),(622,'blue bag','On held label next to blue bag','Lost-property label')]:
 for sc in E[n]['scenes']:
  sc['custom_visible_text']=[{'text':text,'placement':place,'object':obj}]
for i,sc in enumerate(E[627]['scenes'],1):
 if i<=5:
  sc['custom_visible_text']=[{'text':'9','placement':'Left clock-face hour position','object':'Station clock'},{'text':'12','placement':'Top clock-face minute position','object':'Station clock'}]
  if i>=2:sc['custom_visible_text'].append({'text':'9:00','placement':'Large single time on held note','object':'Appointment note'})
# Keep two English models exactly, six scenes, same gate-independent frozen schema.
for n,e in E.items():
 sc=e['scenes'];e['editorial_review']='Reviewed and rewritten by an authorized writing agent; narration frozen before anchors.';e['visual_review_ready']=True
 e['opening_function_vi']='Mở bằng chi tiết cụ thể: '+re.split(r'(?<=[.!?])\s+',sc[0]['narration'])[0]
 e['learner_outcome_vi']='Dùng đúng '+e.get('teaching_form',m[n]['word'])+' với nghĩa '+e.get('selected_gloss_vi',m[n].get('selected_gloss_vi',m[n]['gloss_vi']))+' trong một câu đầy đủ cần cho câu chuyện.'
 for i,s in enumerate(sc):
  s['title_vi']=['Vướng mắc trước mắt','Điều người kia cần','Một thay đổi nhỏ','Câu nói làm rõ','Lời cần nói','Kết quả gần'][i]
  s['purpose_en']=['Establish concrete personal want and early usable model.','Advance resistance through dialogue and a concrete shared object.','Show the relevant meaning through a small action or specific truthful explanation.','Use second related English model to advance the same story.','Retrieve a full story-linked sentence, hold before feedback.','Give correct response and earned local consequence.'][i]
  if 'extra_visual_states' in s:
   s['extra_visual_states']=[a for a in s['extra_visual_states'] if a.get('quote','') in s['narration']]
 assert len(sc)==m[n]['scene_count']==6
 assert sc[4]['practice_pause_seconds']==4 and '___' in sc[4]['stem']
 assert len(re.split(r'[.!?]',sc[0]['narration'])[0].split())<=9
 assert '...' not in ' '.join(s['narration'] for s in sc)
 olde=json.loads((old/(e['job']+'.json')).read_text())
 oldmodels=set(re.findall(r'"([A-Za-z][^"]*[.!?])"',' '.join(s['narration'] for s in olde['scenes'])))
 newmodels=set(re.findall(r'"([A-Za-z][^"]*[.!?])"',' '.join(s['narration'] for s in sc)))
 assert oldmodels==newmodels and len(newmodels)==2,(n,oldmodels,newmodels)
# Full episodes staged, no edits to frozen or current revisions.
f=O/'staged-style-612-631.json';t=f.with_suffix('.tmp');t.write_text(json.dumps({e['job']:e for e in E.values()},ensure_ascii=False,indent=2));t.replace(f)
print('STAGED',len(E),f)
