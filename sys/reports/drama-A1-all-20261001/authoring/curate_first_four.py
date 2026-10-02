from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/drama-A1-all-20261001';raw=json.loads((OUT/'narration-attempts/000-003/episodes.json').read_text());episodes=raw['episodes']
texts=[
['Quà đã gói xong, địa chỉ còn trống. "I have a pen." Tôi đưa cây bút mực cho bà cụ đang lục túi.',
'Bà bảo món quà gửi cho đứa cháu sắp nhập học. Tay bà run, tôi giữ tờ giấy cho bà viết. Tên cháu viết xong rồi, bà vẫn nhìn cây bút rất lâu.',
'Bà xin giữ cây bút để cháu dùng vào buổi học đầu. Tôi vừa mua nó sáng nay. Nghĩ một lúc, tôi nói: "Please take this pen." Bà cứ cầm cây bút này nhé.',
'Bà tưởng tôi chỉ cho mượn. Bạn nói giúp tôi câu bà cứ cầm cây bút này bằng tiếng Anh nhé.',
'"Please take this pen." Đúng rồi. Bà đặt bút vào hộp quà, gói lại thật chậm. Tôi bước ra cửa bưu điện, mới nhớ mình cũng chưa viết xong tấm thiệp cho mẹ.'],
['Em muốn vẽ bố, mà sợ vẽ sai. "I use a pencil." Tôi đưa em cây bút chì, rồi kéo ghế ngồi cạnh.',
'Bố vừa chuyển đi làm xa. Em chỉ nhớ mái tóc và đôi mắt hay cười. Vẽ được nửa khuôn mặt, đầu bút gãy. Em úp tay lên tờ giấy: Thôi, em không vẽ nữa.',
'Tôi gọt lại đầu bút: "This pencil is sharp." Bút chì nhọn rồi này. Em nhấc tay lên, vẽ lại đường tóc. Lần này, em để nét đầu nhẹ hơn.',
'Em muốn tự vẽ nốt. Nếu định nói tôi dùng một cây bút chì, bạn sẽ nói câu nào bằng tiếng Anh?',
'"I use a pencil." Đúng rồi. Em vẽ thêm một bàn tay đang nắm tay em. Bức chân dung chưa giống lắm. Em vẫn bỏ nó vào phong bì gửi bố.'],
['Linh đẩy bản vẽ ra xa: bỏ đi. "I need an eraser." Tôi cần cục tẩy. Tôi giữ mép giấy, trước khi cô vò nó lại.',
'Cả tháng, Linh đều mang bản vẽ này đi sửa. Đêm cuối trước ngày nộp, cô kéo nhầm một nét dài qua cửa sổ. Tôi thử tẩy một đoạn nhỏ ở góc.',
'"This eraser is soft." Cục tẩy này mềm. Linh cầm lấy, xóa từng chút. Nét thừa nhạt dần. Cô kéo ghế lại gần: Vậy mình sửa cửa sổ trước nhé.',
'Linh muốn lấy lại cục tẩy. Bạn nói giúp cô câu tôi cần một cục tẩy bằng tiếng Anh nhé.',
'"I need an eraser." Đúng rồi. Bản vẽ còn phải sửa, nhưng Linh đã thôi định xé nó. Khi cô mở rèm, trời sáng. Hai đứa rủ nhau ăn sáng trước khi đi nộp.'],
['Ông treo bức ảnh, nó cứ nghiêng. "I have a ruler." Cháu có thước kẻ đây. Tôi đặt ảnh xuống, ngồi cạnh ông ở mép bàn.',
'Đó là ảnh bà chụp ở căn nhà cũ. Ông muốn tự làm một chiếc khung mới. Cây thước ngắn quá; cứ nhấc lên đặt xuống, đường đánh dấu lại lệch.',
'Tôi lấy cây thước dài hơn: "Use this long ruler." Ông dùng chiếc thước kẻ dài này nhé. Ông giữ thước, tôi đánh dấu mép bìa. Hai tay ông đã thôi vội.',
'Giờ ông tìm cây thước để đo nốt. Nếu muốn nói cháu có một chiếc thước kẻ, bạn nói câu nào bằng tiếng Anh?',
'"I have a ruler." Đúng rồi. Khung ảnh ngay ngắn trên tường. Ông nhìn một lúc, rồi kéo ghế ra: Ngồi ăn cơm với ông nhé. Tôi cất thước, để điện thoại sang một bên.']]
titles=['Cây bút trong hộp quà','Bức chân dung chưa giống','Bản vẽ chưa bị xé','Chiếc ghế cạnh ông']
plots=['Thiếu đồ viết địa chỉ trong một lần gửi quà; nhân vật giúp bà viết, chấp nhận tặng cây bút còn cần dùng cho cháu bà.','Em ngập ngừng khi vẽ người bố đi làm xa; ngòi gãy khiến em muốn bỏ, người anh giúp em tiếp tục và giữ cả nét vẽ chưa hoàn hảo.','Một nét sai khiến Linh muốn vò đồ án; người bạn giúp cô thử tẩy, giữ lại bản vẽ và tiếp tục sửa đến sáng.','Ông muốn làm lại khung ảnh từ nhà cũ; cháu giúp đo bằng thước dài rồi ở lại ăn cơm, thay vì mải điện thoại.']
frames=[
['At a quiet postal counter, the elderly woman holds a plain wrapped parcel with a blank address label and searches her bag. The pale-blue mascot offers one navy ink pen. No crowd, no printed addresses or incidental text.',
'The mascot steadies the blank card on the counter while the elderly woman writes a few non-letter ink strokes with the pen. Her parcel stays beside her, with no readable address. They focus on the same small task.',
'The elderly woman starts returning the pen; the mascot gently gestures that she can keep it. Parcel remains at the same counter, exactly one pen. Show the decision to give away his own useful object.',
'Hold the same two people at the counter, woman holding the pen uncertainly and mascot inviting her to keep it. Preserve the parcel and single pen, leave the upper safe region available for the sentence stem.',
'The elderly woman places the navy pen inside the plain gift parcel while mascot looks at his own still-unwritten plain card. Show the two purposes clearly with no extra stationery or readable postal writing.'],
['At a simple home drawing table, the small yellow-shirted boy hesitates over a blank sheet while the pale-blue mascot offers a wooden graphite pencil and brings a chair near him. No sailor uniform or military details.',
'At the same table, the boy covers a half-finished simple face sketch with one hand. The pencil has a visibly broken tip; his free hand is moving away from the drawing. The mascot remains beside him.',
'The mascot holds the newly sharpened graphite pencil near the page; the boy raises his hand off the sketch and starts adding a soft hair outline. Keep the same sheet, chair positions and identities. No photorealistic fingers.',
'Hold the boy reaching to take the graphite pencil for himself and mascot letting him continue. The simple face sketch is still unfinished; no answer text beyond the approved sentence stem.',
'The boy puts his modest pencil drawing of a father and a small linked hand into a plain envelope; mascot sits beside him without correcting the unfinished-looking lines. No writing or address on the envelope.'],
['In a minimal night workspace, lavender-shirted Linh pushes a drawing sheet away, about to crumple it. Mascot holds one edge to prevent the sheet being discarded while reaching for one white eraser.',
'At the same desk, the mascot tests a small corner with the eraser; a stray dark pencil line across a simple window shape remains visible on the main drawing. Linh watches rather than tearing the page.',
'Linh carefully uses the soft white eraser on a portion of the unwanted graphite line, with a few eraser crumbs nearby. Some unwanted line remains faintly visible; no claim of a magically perfect white restoration.',
'Hold Linh reaching for the white eraser and mascot ready to hand it over beside the same still-imperfect drawing. Keep the meaningful target object in view, with clear top space for the stem.',
'Morning light at the same desk: Linh opens a plain curtain, the saved drawing lies flat with a few imperfect marks, and the mascot gestures toward the exit for breakfast. Both are relieved, not triumphantly perfect.'],
['In a simple family room, a crooked plain photo frame rests partly against the wall after grandfather tries hanging it. The pale-blue mascot places it safely on a table and shows a short ruler. The grandfather has one plain green top.',
'At the table, grandfather and mascot try aligning a short ruler with a longer cardboard photo backing. The ruler does not span the required edge, so the newly marked guide lines are inconsistent. No cutting glass or sharp blades.',
'Grandfather holds a long metal straight ruler across the cardboard photo backing while the mascot marks one guide line along its edge. Keep their roles and positions stable, with an old photo beside the backing. Tick marks have no numerals.',
'Hold grandfather looking for the long ruler and mascot holding it ready beside the unfinished frame. One plain photo and cardboard backing remain on the table; leave safe space for the sentence stem.',
'The finished simple family photo hangs straight on the wall. Grandfather pulls out the neighboring chair by a small dining table; mascot sets a blank-screen phone aside and moves to sit with him. No writing, logos or extra people.']]
outfits=[('Bà cụ','An elderly minimal ink stick figure with a small silver hair bun, round white face and solid dark oval eyes, ordinary simple proportions.','Exactly one plain brown short-sleeve top and minimal stick limbs; no layered costume or realistic fingers.'),('Em trai','Small minimal ink stick figure, round white head, solid black oval eyes and a short simple dark hair silhouette.','Exactly one plain yellow short-sleeve top, minimal stick limbs.'),('Linh','Adult female minimal ink stick figure, round white face, solid black oval eyes and simple tied-back hair; modest tired expression.','Exactly one plain lavender short-sleeve top, minimal stick limbs.'),('Ông nội','Elderly male minimal ink stick figure, round white face with solid black oval eyes and a small white hair silhouette, modest head tilt.','Exactly one plain green short-sleeve top, minimal stick limbs.')]
for ep,narrs,title,plot,visual,char in zip(episodes,texts,titles,plots,frames,outfits):
 ep.update(title=title,plot_vi=plot,learner_outcome_vi='Nhận ra đúng nghĩa và nói được câu mẫu cần cho tình huống.',editorial_review='Reviewed and rewritten by primary agent; narration frozen before anchors.')
 ep['characters']=[ep['characters'][0],dict(id='CH02',name_vi=char[0],appearance_en=char[1],outfit_en=char[2])]
 for i,(s,n,v) in enumerate(zip(ep['scenes'],narrs,visual)):
  s.update(narration=n,visual_en=v,practice_pause_seconds=4 if i==3 else 0,character_ids=['CH01','CH02'],title_vi=['Chi tiết đầu chuyện','Điều cần hiểu','Hành động làm đổi chuyện','Lời người xem giúp nói','Kết quả'][i],purpose_en=['Open with a concrete situation and an early usable English line.','Establish why this small action matters to these people and support the selected meaning.','Use the second English model as a decision or action with a consequence.','Invite one manageable full-sentence retrieval tied to the same need; hold before the answer.','Give the correct response and close the local story with a visible relationship or consequence.'][i])
 ep['scenes'][3]['stem']={'vocab-pen-script-242':'Please take this ___.','vocab-pencil-script-243':'I use a ___.','vocab-eraser-script-244':'I need an ___.','vocab-ruler-script-245':'I have a ___.'}[ep['job']]
(OUT/'narration-frozen').mkdir(exist_ok=True)
for ep in episodes:
 (OUT/'narration-frozen'/f"{ep['job']}.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
print('Frozen four editorially rewritten episodes before building anchors')
