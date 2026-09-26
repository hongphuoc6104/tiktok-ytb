"""Bản AI của "Người tiền sử làm gì cả ngày?" với nhân vật chính Mơ (cô bé tiền sử).

Lời dẫn giữ theo ngay_tien_su.py, chỉ đổi nhân vật trung tâm thành Mơ. Mỗi câu có 1–2 shot
(ảnh AI qua tool VP Stickman Lab, Nano Banana Pro, tham chiếu nhân vật Mơ). Bản clip dùng
chính các shot này làm khung đầu cho Omni Flash.
Shot: (id, prompt, effect, overlays[, clip_motion]).
"""
from doodle.scripts.ngay_tien_su import TAGS, L, CH  # noqa: F401

TITLE = 'Người tiền sử làm gì cả ngày?'
TITLES = ['Người tiền sử làm gì cả ngày?', 'Một ngày của cô bé tiền sử: nhàn hơn bạn nghĩ?',
          'Không báo thức, không deadline: tổ tiên sống thế nào?']
HOOK = ('Tám giờ sáng, bạn kẹt giữa biển xe máy. Năm mươi nghìn năm trước, cô bé Mơ thức dậy '
        'không chuông báo thức, không deadline. Vậy cả nhà Mơ làm gì suốt một ngày?')
THUMB = {'shot': 's06_rest_1', 'text': 'NHÀN HƠN BẠN?'}

CAST = {
    'MO': 'Mo (the girl from the character reference: round white head, orange-red hair bun tied with a white bone, leopard-spot yellow tunic, turquoise pendant)',
    'DAD': "Mo's father (tall stick figure, round white head, messy black hair and short black beard, dark-brown fur tunic)",
    'MOM': "Mo's mother (stick figure, round white head, long dark-brown braid, grey-green fur dress, small bead necklace)",
    'GRAN': "Mo's grandmother (small stick figure, round white head, white hair bun, walking stick, beige tunic)",
    'BI': "Mo's little brother Bi (tiny stick figure, round white head, spiky black hair, small brown fur loincloth)",
    'YOU': 'a modern Vietnamese office worker (stick figure, round white head, black hair, glasses, white shirt, blue tie)',
    'NOMO': 'The girl from the character reference does NOT appear in this image.',
}
STYLE = ('Hand-drawn doodle explainer illustration like a popular YouTube history explainer: thick slightly uneven black marker '
         'outlines, flat muted colors, simple shapes, off-white paper texture, stick-figure characters with round white heads and '
         'very expressive faces. Keep Mo exactly as in the character reference. No text, no letters, no numbers, no watermark, no captions.')


def P(text):
    for k, v in CAST.items():
        text = text.replace('{' + k + '}', v)
    return text


# (id, prompt, effect, overlays, clip motion)
SCENES = [
    {'id': 'SC01', 'chapter': 'Mở đầu', 'lines': [
        ('Tám giờ sáng. Bạn đang kẹt giữa một biển xe máy.', [
            ('s01_traffic_1', 'A huge traffic jam of motorbikes on a crowded Vietnamese city street at 8 a.m., {YOU} stuck in the middle on a scooter looking exhausted, exhaust smoke, a big wall clock showing eight. {NOMO}', 'zoom_in', [L('8:00 SÁNG')],
             'the motorbikes inch forward, smoke puffs, the worker sighs')]),
        ('Còi xe inh ỏi, khói bụi mù mịt, và điện thoại trong túi thì rung liên tục.', [
            ('s01_traffic_2', 'Close-up of {YOU} on a scooter covering his ears, horns honking drawn as jagged lines, grey smoke clouds, his phone vibrating in his shirt pocket with shake lines. {NOMO}', 'pop', [],
             'horn lines pulse, smoke drifts, the phone buzzes and shakes')]),
        ('Đó là tin nhắn nhắc bạn về cuộc họp lúc chín giờ, và cái deadline chiều nay.', [
            ('s01_phone', '{YOU} staring at a smartphone with wide worried eyes, a thought bubble above him full of a calendar and a clock and stacks of papers. {NOMO}', 'zoom_in', [L('Cuộc họp 9h • Deadline 17h', y=.1)],
             'he sweats and his eyes widen as the thought bubble grows')]),
        ('Rồi bạn sẽ ngồi tám tiếng trước màn hình, về nhà khi trời đã tối.', [
            ('s01_office', '{YOU} slumped at an office desk in front of a computer screen, tall stacks of paper, a window showing night sky, a tired face with bags under his eyes. {NOMO}', 'pan_right', [],
             'he slowly slumps forward onto the desk, the window darkens')]),
        ('Sáng mai, mọi thứ lặp lại, từ tiếng chuông báo thức đầu tiên.', [
            ('s01_alarm', 'An alarm clock ringing loudly next to a bed, {YOU} buried under the blanket with only a grumpy face showing, early morning light. {NOMO}', 'zoom_out', [],
             'the alarm clock shakes and rings, the worker pulls the blanket over his head')]),
        ('Bây giờ, hãy tua ngược thời gian.', [
            ('s01_rewind', 'A big swirling spiral time tunnel on paper, clocks and calendars flying backwards into it, {YOU} being pulled in with a surprised face. {NOMO}', 'fade', [{'type': 'counter', 'text': 'năm trước', 'to': 50000, 'x': .5, 'y': .2, 'at': .2}],
             'the spiral spins fast and the clocks fly into it')]),
        ('Không phải một trăm năm, không phải một nghìn năm, mà là năm mươi nghìn năm.', [
            ('s01_timeline', 'A long winding path drawn on paper going back through history: a city, then castles, then pyramids, then a small prehistoric camp with huts and a campfire far in the distance. {NOMO}', 'pan_left', [],
             'the camera glides along the path back to the tiny prehistoric camp')]),
        ('Một cô bé tên Mơ mở mắt khi ánh nắng đầu tiên chạm vào mặt.', [
            ('s01_wake_1', '{MO} lying on a fur blanket inside a small hide hut, a warm beam of sunrise light touching her face, eyes just opening, sleepy smile.', 'zoom_in', [],
             'sunlight moves across her face, she opens her eyes and yawns')]),
        ('Không ai đánh thức cô. Không ai chờ cô ở văn phòng. Cũng không có cuộc họp nào cả.', [
            ('s01_wake_2', '{MO} sitting up and stretching both arms high with a huge happy yawn outside a hide hut at dawn, birds in the pink sky.', 'pop', [],
             'she stretches her arms and yawns, birds fly by')]),
        ('Mơ chỉ có gia đình nhỏ của mình, một bếp lửa đã tàn, và cả một ngày dài phía trước.', [
            ('s01_family_sleep', 'A prehistoric camp at dawn: {DAD}, {MOM} and {BI} still asleep on furs around a campfire with only a thin curl of smoke, {MO} tiptoeing past them with a finger on her lips.', 'pan_right', [],
             'the smoke curls up, Mo tiptoes carefully past her sleeping family')]),
        ('Câu hỏi là: cả nhà Mơ sẽ làm gì với ngày đó?', [
            ('s01_question', '{MO} standing on a small hill at sunrise with hands on hips, looking at a wide open savanna with trees and a river, curious raised eyebrows.', 'zoom_out', [L('Họ làm gì cả ngày?', y=.12)],
             'the wind moves the grass, Mo looks around curiously')]),
        ('Và vì sao câu trả lời có thể khiến bạn nhìn lại chính một ngày của mình?', [
            ('s01_mirror', 'Split picture: on the left {YOU} stuck in traffic looking stressed, on the right {MO} relaxing under a tree; they look at each other with surprise across the middle line.', 'zoom_in', [],
             'both characters turn their heads and look at each other')]),
    ]},
    {'id': 'SC02', 'chapter': 'Chúng ta đã nghĩ sai?', 'lines': [
        ('Nếu hỏi một người bất kỳ, bạn sẽ nghe một câu trả lời quen thuộc.', [
            ('s02_ask', 'Several modern people with speech bubbles showing scary images of cavemen with clubs, a dark cave and a hungry stomach. {NOMO}', 'fade', [CH('Chúng ta đã nghĩ sai?')],
             'the speech bubbles pop up one after another')]),
        ('Người tiền sử sống khổ sở, lúc nào cũng đói, lúc nào cũng sợ.', [
            ('s02_myth_1', 'A cliché scene: {MO} and {DAD} shivering in a dark rainy cave, thin and hungry, stomachs rumbling, frightened eyes.', 'zoom_in', [],
             'rain falls outside the cave, they shiver')]),
        ('Họ chạy trốn thú dữ từ sáng đến tối, và chết trẻ vì bệnh tật.', [
            ('s02_myth_2', '{MO} and {DAD} running away in panic from a huge roaring sabre-tooth tiger, dust clouds behind them, comic motion lines.', 'slide_left', [],
             'they run in panic, the tiger chases them')]),
        ('Trong hình dung đó, mỗi phút của họ đều là cuộc chiến sinh tồn.', [
            ('s02_myth_3', '{MO} with a tiny spear and a determined but scared face surrounded by many dangers drawn around her: a snake, a storm cloud, a wolf, a mammoth.', 'zoom_out', [],
             'the dangers close in around Mo, she turns nervously')]),
        ('Nhưng khi các nhà khảo cổ đào lên những bộ xương cổ, câu chuyện bắt đầu khác đi.', [
            ('s02_dig', 'Two archaeologists with hats and brushes carefully uncovering an ancient skeleton in a dig site, one lifting a magnifying glass, surprised faces. {NOMO}', 'zoom_in', [],
             'the brush sweeps away sand revealing the bones')]),
        ('Hãy thử so sánh hai người.', [
            ('s02_compare', 'A museum table with two skeletons lying side by side under labels-free cards, a big magnifying glass hovering between them. {NOMO}', 'pan_right', [],
             'the magnifying glass moves from one skeleton to the other')]),
        ('Một người sống bằng săn bắt và hái lượm. Người kia là một trong những nông dân đầu tiên.', [
            ('s02_two_1', 'Left: {DAD} as a hunter-gatherer holding a spear and a basket of fruit, standing tall. Right: an early farmer stick figure holding a stone sickle next to a wheat field. A big question mark between them.', 'zoom_in', [L('Ai khỏe hơn?', x=.5, y=.12)],
             'both characters flex, the question mark wobbles')]),
        ('Nhiều người sẽ đoán người nông dân khỏe hơn, vì có nhà, có kho lúa, có bữa ăn ổn định.', [
            ('s02_farmer', 'An early farmer stick figure proudly standing in front of a mud-brick house and a big granary full of grain, holding a bowl of porridge. {NOMO}', 'pan_left', [],
             'the farmer smiles proudly and pats the granary')]),
        ('Thế nhưng ở nhiều nơi trên thế giới, kết quả lại ngược lại.', [
            ('s02_twist', '{MO} popping into the frame with a huge surprised face and both hands on her cheeks, a big exclamation mark shape above her.', 'pop', [],
             'Mo pops in with a gasp and her eyes grow huge')]),
        ('Những người nông dân đầu tiên thường thấp hơn, răng sâu nhiều hơn, xương khớp mòn hơn.', [
            ('s02_farmer_sick', 'The early farmer stick figure looking tired and bent, holding his aching back, a cracked tooth drawn next to him, short and thin, bags under his eyes. {NOMO}', 'zoom_in', [L('Sâu răng • Mòn khớp • Thấp hơn', y=.12)],
             'the farmer groans and rubs his back')]),
        ('Trong khi người săn bắt hái lượm trước họ lại có bộ xương chắc khỏe đáng ngạc nhiên.', [
            ('s02_hunter_fit', '{DAD} standing tall and strong with a big confident smile, flexing an arm, {MO} beside him pointing at him proudly.', 'pop', [],
             'Dad flexes his arm, Mo claps and cheers')]),
        ('Vậy một ngày của Mơ và gia đình cô thật sự trông như thế nào?', [
            ('s02_family', 'The whole family portrait in front of their hide hut: {DAD}, {MOM}, {GRAN}, {BI} and {MO} in the middle waving at the viewer, sunny savanna.', 'zoom_out', [],
             'the family waves at the camera together')]),
    ]},
    {'id': 'SC03', 'chapter': 'Bình minh không có chuông báo thức', 'lines': [
        ('Ngày của họ bắt đầu theo mặt trời, chứ không theo đồng hồ.', [
            ('s03_sun', 'A big smiling sun rising over the savanna hills, {MO} beside a tree pointing at the sun, a broken modern alarm clock lying ignored in the grass.', 'fade', [CH('Bình minh không có chuông báo thức')],
             'the sun rises slowly and Mo points at it happily')]),
        ('Việc đầu tiên thường là khơi lại bếp lửa từ đống than còn ấm.', [
            ('s03_fire_1', 'Close-up of {GRAN} and {MO} kneeling by a campfire of glowing embers, Mo blowing gently with puffed cheeks, tiny sparks rising.', 'zoom_in', [],
             'Mo blows on the embers and small flames flicker up')]),
        ('Giữ được lửa qua đêm là cả một kỹ năng, vì nhóm lửa lại từ đầu tốn công hơn nhiều.', [
            ('s03_fire_2', '{MO} happily holding her hands near a campfire that has flared up bright, {GRAN} nodding with approval, morning light.', 'pan_right', [],
             'the fire flares up, Grandma nods')]),
        ('Còn giấc ngủ của họ thì sao?', [
            ('s03_sleep_q', '{MO} with a thoughtful face tapping her chin, a big thought bubble with a crescent moon and stars above her.', 'pop', [],
             'Mo taps her chin, the moon in the bubble twinkles')]),
        ('Khi các nhà nghiên cứu theo dõi những nhóm săn bắt hái lượm ngày nay, họ thấy mọi người thường ngủ khoảng sáu đến bảy tiếng.', [
            ('s03_research', 'A modern researcher stick figure with a notebook sitting at the edge of a hunter-gatherer camp at night, watching people sleep around a fire. {NOMO}', 'zoom_in', [L('~6–7 tiếng mỗi đêm', y=.12)],
             'the researcher writes notes, the fire crackles'),
            ('s03_sleep', '{MO} sleeping peacefully on a fur blanket under the stars next to a small fire, a gentle smile, a sleeping cat-like hyrax nearby.', 'zoom_out', [],
             'Mo breathes slowly in her sleep, stars twinkle')]),
        ('Không nhiều hơn chúng ta là mấy.', [
            ('s03_same', 'Split image: {YOU} asleep in a modern bed on the left, {MO} asleep on furs on the right, both with the same peaceful face.', 'fade', [],
             'both sleepers breathe and turn in their sleep')]),
        ('Điều khác biệt là họ ngủ theo nhịp của bóng tối, và thức dậy theo ánh sáng.', [
            ('s03_rhythm', 'A day-and-night circle drawn on paper: one half with a sun and {MO} awake and playing, the other half with a moon and Mo sleeping.', 'zoom_in', [],
             'the circle slowly turns from day to night')]),
        ('Một số nhà sử học còn cho rằng ở nhiều nơi, người xưa từng ngủ thành hai giấc, thức dậy một lúc giữa đêm.', [
            ('s03_night_wake', 'Middle of the night by a small fire: {MO} and {GRAN} sitting up awake, quietly chatting and looking at the moon, others asleep around.', 'pan_left', [],
             'Grandma whispers a story, Mo listens sleepily')]),
        ('Sau bếp lửa là nước.', [
            ('s03_water_1', '{MO} carrying a large gourd water container on her shoulder, walking toward a sparkling stream with a cheerful face.', 'fade', [L('Việc đầu ngày: lửa và nước', y=.12)],
             'Mo walks toward the stream swinging the gourd')]),
        ('Cả nhóm thường chọn nơi dựng trại gần một con suối hay một dòng sông.', [
            ('s03_camp', 'Wide view of a small prehistoric camp with hide huts on a grassy bank next to a winding river, smoke rising, trees around. {NOMO}', 'pan_right', [],
             'the river flows and smoke rises from the camp')]),
        ('Trẻ con đi theo người lớn, vừa chơi vừa học đường đi.', [
            ('s03_kids_follow', '{MOM} walking ahead with a basket, {MO} and {BI} following behind splashing and hopping over stepping stones in the stream, laughing.', 'zoom_in', [],
             'the children hop across the stones and splash water')]),
        ('Rồi mọi người ngồi lại, bàn xem hôm nay ai đi đâu, làm gì.', [
            ('s03_meeting', 'The family and a few neighbors sitting in a circle on the grass, {DAD} drawing a map in the dirt with a stick, {MO} leaning in curiously.', 'pan_left', [],
             'Dad draws lines in the dirt, everyone leans in')]),
        ('Không có ông chủ nào giao việc. Quyết định được đưa ra cùng nhau.', [
            ('s03_vote', 'Everyone in the circle raising their hands and nodding in agreement, {MO} raising both hands excitedly, happy faces.', 'pop', [],
             'hands go up one by one, Mo bounces excitedly')]),
    ]},
    {'id': 'SC04', 'chapter': 'Làm việc bao nhiêu giờ một ngày?', 'lines': [
        ('Và đây là phần bất ngờ nhất.', [
            ('s04_drumroll', '{MO} holding a big leaf like a curtain about to reveal a secret, a mischievous grin, sparkles around.', 'pop', [CH('Làm việc bao nhiêu giờ?')],
             'Mo slowly pulls the leaf aside with a grin')]),
        ('Vào những năm sáu mươi, nhà nhân học Richard Lee đã sống cùng người San ở sa mạc Kalahari và ghi lại họ dành bao nhiêu thời gian để kiếm ăn.', [
            ('s04_lee_1', 'A 1960s anthropologist stick figure with a hat and notebook in the Kalahari desert, sitting with a group of San foragers under a tree, sand dunes. {NOMO}', 'zoom_in', [],
             'the anthropologist writes in his notebook and nods'),
            ('s04_lee_2', 'Close-up of an old notebook page with sketches of footprints, a sun and small tally marks, a pencil, desert sand around. {NOMO}', 'pan_right', [],
             'the pencil adds tally marks to the notebook')]),
        ('Câu trả lời khiến nhiều người sửng sốt: chỉ khoảng hai đến ba ngày mỗi tuần.', [
            ('s04_week', 'A week drawn as seven stone tablets in a row, only two or three have a small spear and basket icon, the rest have a hammock icon, {MO} pointing at them amazed.', 'zoom_in', [L('2–3 ngày kiếm ăn mỗi tuần', y=.1)],
             'Mo jumps with surprise pointing at the tablets')]),
        ('Tính ra, thời gian săn bắt và hái lượm có khi chỉ vào khoảng mười lăm đến hai mươi giờ một tuần.', [
            ('s04_bars', 'Two simple hand-drawn bars: a short brown bar with a spear icon next to a very tall grey bar with a laptop icon, {MO} standing on top of the short bar laughing, {YOU} hanging from the tall bar looking tired.', 'pop', [L('Kiếm ăn', x=.37, y=.12), L('Bạn', x=.62, y=.12)],
             'the tall bar grows taller, the worker slides down')]),
        ('Tất nhiên, con số này còn nhiều tranh luận.', [
            ('s04_debate', 'Several scholars stick figures arguing around a table covered with papers, speech bubbles with question marks, one scratching his head. {NOMO}', 'zoom_in', [],
             'the scholars wave their hands and argue')]),
        ('Nếu cộng thêm chế tạo công cụ, nấu nướng, lấy nước và kiếm củi, tổng thời gian làm việc sẽ dài hơn.', [
            ('s04_chores_1', '{DAD} chipping a stone tool, {MOM} cooking roots on the fire, {MO} carrying a bundle of firewood on her back, busy camp.', 'pan_left', [],
             'Dad chips the stone, Mom stirs, Mo staggers with the firewood'),
            ('s04_chores_2', '{MO} carrying water with {BI}, both sweating a little but smiling, gourds on their shoulders.', 'zoom_in', [],
             'the kids walk carrying gourds, water splashes')]),
        ('Và cuộc sống ở vùng giàu tài nguyên chắc chắn dễ thở hơn ở vùng khắc nghiệt.', [
            ('s04_regions', 'Split image: left a lush green valley full of fruit trees and fish, right a harsh dry desert with a few cacti and cracked ground. {NOMO}', 'pan_right', [],
             'leaves sway on the left, heat shimmers on the right')]),
        ('Nhưng ngay cả khi tính đủ, bức tranh vẫn rất khác với tám tiếng ngồi văn phòng, cộng thêm hai tiếng kẹt xe.', [
            ('s04_contrast', 'Split image: {YOU} trapped at a desk and then in traffic on the left, {MO} lying in a hammock between two trees on the right sipping from a coconut shell.', 'zoom_out', [],
             'Mo swings in the hammock while the worker types frantically')]),
        ('Vậy công việc buổi sáng của họ là gì?', [
            ('s04_morning_q', '{MO} with a basket on her arm peeking out from behind a big bush with a curious face.', 'fade', [],
             'Mo peeks out from behind the bush')]),
        ('Phần lớn thức ăn thường đến từ hái lượm: quả mọng, hạt, rau dại, củ và mật ong.', [
            ('s04_gather_1', '{MOM} and {MO} picking red berries from bushes into a woven basket, Mo eating one with delight.', 'zoom_in', [L('Quả • Hạt • Củ • Mật ong', y=.12)],
             'Mo picks a berry and pops it into her mouth'),
            ('s04_honey', '{DAD} reaching into a tree hollow for a honeycomb while {MO} watches with a thrilled face, a few bees buzzing around.', 'pop', [],
             'Dad pulls out dripping honeycomb, bees buzz, Mo licks her lips')]),
        ('Công việc này đòi hỏi trí nhớ đáng kinh ngạc.', [
            ('s04_memory', '{MO} with a big thought bubble above her head filled with many plants, mushrooms, fruits and roots arranged like a map.', 'zoom_in', [],
             'plants pop up one by one inside the thought bubble')]),
        ('Họ phải biết cây nào ăn được, cây nào có độc, mùa nào quả chín, và chỗ nào có củ nằm sâu dưới đất.', [
            ('s04_poison', '{GRAN} stopping {MO} from picking a bright red spotted mushroom, wagging her finger, Mo with a surprised face.', 'pan_right', [],
             'Grandma wags her finger and Mo pulls her hand back'),
            ('s04_roots', '{MO} and {MOM} digging with a stick and pulling a big root tuber out of the ground, dirt flying, Mo cheering.', 'zoom_in', [],
             'they pull hard and the big root pops out of the ground')]),
        ('Mỗi chuyến đi là một bài học, và người lớn tuổi chính là cuốn sách sống của cả nhóm.', [
            ('s04_gran_teach', '{GRAN} sitting on a rock teaching {MO} and {BI} about plants, holding up a leaf, the children listening with sparkling eyes.', 'zoom_out', [],
             'Grandma holds up the leaf, the kids nod eagerly')]),
    ]},
    {'id': 'SC05', 'chapter': 'Cuộc săn và luật chia phần', 'lines': [
        ('Săn bắn thì khác. Nó hiếm hơn, nguy hiểm hơn, và thường thất bại.', [
            ('s05_hunters', '{DAD} and two other hunters with spears crouching in tall grass, tense faces, {MO} watching from behind a rock.', 'fade', [CH('Cuộc săn và luật chia phần')],
             'the hunters creep forward through the grass')]),
        ('Một nhóm nhỏ đi theo dấu chân thú, đọc từng vết cỏ gãy, từng dấu phân còn mới.', [
            ('s05_tracks', 'Close-up of {DAD} kneeling and studying animal footprints in the mud and broken grass stems, pointing with a finger, focused face.', 'pan_left', [],
             'Dad traces the footprints with his finger')]),
        ('Con người không nhanh bằng linh dương, cũng không khỏe bằng sư tử.', [
            ('s05_antelope', 'A fast antelope leaping away easily from a panting hunter, and a proud lion watching from a rock. {NOMO}', 'zoom_in', [],
             'the antelope bounds away, the lion yawns')]),
        ('Nhưng chúng ta có một vũ khí đặc biệt: khả năng chạy bền.', [
            ('s05_run', '{DAD} running steadily across the hot savanna under a blazing sun with a determined face, long shadow, dust puffs.', 'slide_left', [L('Vũ khí bí mật: chạy bền', y=.12)],
             'Dad jogs steadily across the savanna')]),
        ('Cơ thể con người đổ mồ hôi để làm mát, nên có thể đi và chạy hàng giờ dưới nắng.', [
            ('s05_sweat', 'Simple explainer drawing of {DAD} jogging with sweat drops flying off, small cooling breeze lines around his body, a sun above.', 'zoom_in', [],
             'sweat drops fly and the breeze lines swirl')]),
        ('Có giả thuyết cho rằng tổ tiên ta từng bám theo con mồi cho đến khi nó kiệt sức vì nóng.', [
            ('s05_tired_kudu', 'A kudu antelope lying down exhausted in the heat, tongue out, while {DAD} walks up calmly behind it at a distance.', 'pan_right', [],
             'the tired antelope pants, Dad approaches slowly')]),
        ('Dù vậy, nhiều buổi săn kết thúc tay trắng.', [
            ('s05_fail', '{DAD} returning to camp at sunset empty-handed with a sad face and a drooping spear, {MO} patting his arm to comfort him.', 'zoom_in', [],
             'Dad sighs, Mo pats his arm')]),
        ('Có ngày, bữa tối là cá bắt được ở sông, chứ không phải thịt thú lớn.', [
            ('s05_fish', '{MO} standing in the shallow river proudly lifting a big wriggling fish above her head, water splashing, {BI} cheering on the bank.', 'pop', [],
             'the fish wriggles, Mo laughs, water splashes')]),
        ('Và khi có thịt, điều quan trọng nhất không phải là ai săn được, mà là chia thế nào.', [
            ('s05_meat', 'Around a campfire a roasted leg of meat on a stick, everyone looking at it hungrily, {DAD} holding a stone knife ready to cut.', 'fade', [],
             'the meat sizzles over the fire, everyone watches')]),
        ('Ở nhiều nhóm săn bắt hái lượm ngày nay, thịt được chia cho cả nhóm, kể cả người không đi săn.', [
            ('s05_share', '{DAD} handing out pieces of meat to everyone in a circle, {GRAN} and {BI} and neighbors receiving portions, {MO} receiving hers with a big smile.', 'zoom_in', [L('Thịt chia cho cả nhóm', y=.12)],
             'pieces of meat are passed from hand to hand')]),
        ('Người khoe khoang chiến công thường bị trêu chọc để giữ cho không ai tự cho mình là hơn người.', [
            ('s05_brag', 'A boastful hunter puffing out his chest and pointing at himself, while everyone around including {MO} laughs and teases him, he blushes.', 'pop', [],
             'the braggart puffs his chest, then deflates as everyone laughs')]),
        ('Hôm nay bạn chia cho tôi, mai tôi chia lại cho bạn. Đó chính là tấm bảo hiểm của họ.', [
            ('s05_insurance', 'Two neighboring families exchanging food across a campfire, a fish going one way and berries going the other way, {MO} in the middle holding hands with both sides.', 'zoom_out', [],
             'food passes back and forth, everyone smiles')]),
    ]},
    {'id': 'SC06', 'chapter': 'Buổi chiều của những người rảnh rỗi', 'lines': [
        ('Khi mặt trời lên cao và trời nóng nhất, nhiều nhóm đơn giản là nghỉ ngơi.', [
            ('s06_rest_1', '{MO} lying in the shade of a big acacia tree with hands behind her head, eyes closed, super relaxed smile, a blazing sun outside the shade.', 'fade', [CH('Buổi chiều rảnh rỗi')],
             'leaves sway, Mo sighs happily')]),
        ('Họ ngồi dưới bóng cây, ngủ trưa, trò chuyện, chải tóc cho nhau.', [
            ('s06_rest_2', 'Under a big tree: {MOM} braiding {MO}\'s hair, {DAD} napping and snoring, {GRAN} chatting with a neighbor, peaceful afternoon.', 'zoom_in', [],
             'Mom braids Mo\'s hair, Dad snores')]),
        ('Người già dạy trẻ con cách ghè đá để làm dao và mũi giáo.', [
            ('s06_knap_1', '{GRAN} showing {MO} how to strike a flint stone with a hammerstone, small stone flakes flying, Mo watching closely.', 'pan_right', [],
             'Grandma strikes the stone, flakes fly off')]),
        ('Một con dao đá tốt cần nhiều giờ luyện tay, và kinh nghiệm được truyền qua từng thế hệ.', [
            ('s06_knap_2', '{MO} proudly holding up her first slightly wonky stone knife, {GRAN} giving a thumbs up and laughing.', 'pop', [],
             'Mo holds up her stone knife proudly')]),
        ('Trẻ con thì có rất nhiều thời gian để chơi.', [
            ('s06_play_1', '{MO} and {BI} and other children playing tag around the huts, running and laughing, dust clouds and motion lines.', 'slide_left', [],
             'the kids chase each other around the huts')]),
        ('Chúng chạy nhảy, bắt chước người lớn đi săn, và tự tìm quả ăn gần trại.', [
            ('s06_play_2', '{BI} pretending to be a hunter with a small stick spear sneaking up on {MO} who wears a leaf mask pretending to be an antelope, both giggling.', 'zoom_in', [],
             'Bi sneaks up, Mo jumps away laughing')]),
        ('Còn người lớn thì làm một việc mà chúng ta hay xem nhẹ: nói chuyện.', [
            ('s06_talk_1', 'The adults sitting in a relaxed circle chatting with lively speech bubbles, {MO} sitting among them listening.', 'fade', [],
             'speech bubbles pop up, everyone gestures')]),
        ('Họ kể về ai đang giận ai, chỗ nào có nhiều quả, đàn thú đang di chuyển về đâu.', [
            ('s06_talk_2', 'Close-up of {MOM} gossiping with a neighbor, speech bubbles showing an angry face, a bush of berries, and a herd of zebras walking.', 'zoom_in', [],
             'the pictures in the speech bubbles change one by one')]),
        ('Những câu chuyện đó giữ cho cả nhóm gắn bó, và giúp họ sống sót.', [
            ('s06_bond', 'The whole group laughing together in a tight circle, arms around each other\'s shoulders, {MO} in the middle, warm afternoon light.', 'zoom_out', [],
             'everyone sways and laughs together')]),
        ('Một số người còn dùng thời gian rảnh để làm một thứ hoàn toàn không cần cho sinh tồn: nghệ thuật.', [
            ('s06_art_1', 'Inside a cave, {MO} painting a red ochre animal on the rock wall with her fingers, a small torch lighting the wall, focused tongue-out face.', 'fade', [],
             'Mo paints, the torchlight flickers')]),
        ('Trên vách hang ở nhiều nơi, người xưa để lại dấu bàn tay và hình vẽ động vật, có những bức đã hơn bốn mươi nghìn năm tuổi.', [
            ('s06_art_2', 'A cave wall covered with red hand stencils and paintings of bulls, horses and deer in ochre, lit by torchlight. {NOMO}', 'pan_left', [L('Hơn 40.000 năm tuổi', y=.12)],
             'the torchlight flickers across the paintings'),
            ('s06_hand', '{MO} pressing her small hand against the cave wall next to ancient hand stencils, amazed face.', 'zoom_in', [],
             'Mo places her hand on the wall and gasps')]),
        ('Hãy tưởng tượng xem: một người không có deadline, không có tin nhắn, và dành cả buổi chiều để vẽ.', [
            ('s06_imagine', '{MO} lying on her belly drawing in the sand with a stick, happily humming, butterflies around, no worries at all.', 'pop', [],
             'Mo draws in the sand, butterflies flutter')]),
    ]},
    {'id': 'SC07', 'chapter': 'Đêm bên ngọn lửa', 'lines': [
        ('Khi trời tối, cả nhóm lại quây quần bên bếp lửa.', [
            ('s07_fire_1', 'Night: the family sitting around a big warm campfire, orange glow on their faces, dark blue sky with stars, {MO} holding her knees.', 'fade', [CH('Đêm bên ngọn lửa')],
             'the fire crackles and sparks rise into the night')]),
        ('Lửa giữ ấm, xua thú dữ, nấu chín thức ăn, và kéo dài thêm vài giờ cho một ngày.', [
            ('s07_fire_2', 'Campfire scene: roots roasting on sticks, glowing eyes of a hyena in the dark bushes turning away, {MO} warming her hands.', 'zoom_in', [L('Ấm • An toàn • Nấu chín', y=.12)],
             'the hyena eyes blink and retreat, food roasts')]),
        ('Nghiên cứu ở một số nhóm săn bắt hái lượm cho thấy câu chuyện ban đêm khác hẳn ban ngày.', [
            ('s07_day_night', 'Split image: daytime people talking about work with tool and basket speech bubbles on the left, night-time people telling stories by a fire with star and spirit bubbles on the right. {NOMO}', 'fade', [],
             'the left side fades from day into night')]),
        ('Ban ngày người ta nói về công việc. Ban đêm, người ta kể chuyện.', [
            ('s07_storyteller', '{GRAN} telling a dramatic story by the fire with raised hands, her shadow huge on the rocks behind, {MO} and {BI} listening with wide eyes.', 'zoom_in', [],
             'Grandma raises her hands, the shadow looms, kids gasp')]),
        ('Chuyện về những cuộc săn xa xưa, về tổ tiên, về các vì sao và những con vật khổng lồ.', [
            ('s07_story_bubble', 'A big smoky story bubble rising from the campfire showing ancient hunters, a giant mammoth and constellations, {MO} gazing up at it in wonder.', 'zoom_out', [],
             'the smoky pictures swirl upward from the fire')]),
        ('Và có cả âm nhạc.', [
            ('s07_music', '{DAD} playing a small bone flute by the fire while {MO} dances happily, musical notes floating in the air.', 'pop', [],
             'Dad plays the flute, Mo twirls, notes float')]),
        ('Các nhà khảo cổ đã tìm thấy những chiếc sáo làm từ xương chim, có tuổi khoảng bốn mươi nghìn năm.', [
            ('s07_flute', 'Museum-style drawing of an ancient bone flute with finger holes lying on a cloth, a small brush beside it, soft spotlight. {NOMO}', 'zoom_in', [L('Sáo xương ~40.000 năm', y=.12)],
             'the spotlight slowly brightens on the flute')]),
        ('Nghĩa là từ rất lâu, con người đã ngồi bên lửa và thổi những giai điệu đầu tiên.', [
            ('s07_song', 'Everyone around the fire clapping and swaying to the music, {MO} singing with eyes closed, sparks and notes rising together.', 'pan_right', [],
             'everyone claps and sways')]),
        ('Trẻ con nằm ngửa nhìn trời sao, nơi người lớn chỉ cho chúng những hình thù quen thuộc.', [
            ('s07_stars', '{MO} and {BI} lying on their backs on the grass looking up at a sky full of stars, {DAD} pointing at a constellation shaped like an antelope drawn with dotted lines.', 'pan_left', [],
             'the stars twinkle and the constellation lines appear')]),
        ('Rồi mọi người ngủ gần nhau, quanh bếp lửa.', [
            ('s07_sleep', 'The family sleeping close together on furs around the glowing embers, {MO} curled up next to {MOM}, peaceful night.', 'fade', [],
             'the embers glow, everyone breathes slowly')]),
        ('Luôn có người ngủ chập chờn hoặc thức giấc giữa chừng, như những người canh gác tự nhiên.', [
            ('s07_guard', '{GRAN} awake sitting by the embers with a stick, watchful eyes scanning the dark, others asleep, a sliver of moon.', 'zoom_in', [],
             'Grandma looks around and pokes the embers')]),
        ('Không ai phải cô đơn trong bóng tối.', [
            ('s07_safe', 'Close-up of {MO} sleeping with a gentle smile, snuggled between {MOM} and {BI}, warm orange glow.', 'zoom_out', [],
             'Mo smiles in her sleep')]),
    ]},
    {'id': 'SC08', 'chapter': 'Cái giá của sự tiến bộ', 'lines': [
        ('Vậy tại sao chúng ta lại từ bỏ lối sống đó?', [
            ('s08_why', '{MO} standing at a crossroads with a signpost-like tree, one path to the wild savanna, the other to plowed fields and mud houses, confused face.', 'fade', [CH('Cái giá của sự tiến bộ')],
             'Mo looks left and right between the two paths')]),
        ('Khoảng mười hai nghìn năm trước, ở một số nơi, con người bắt đầu trồng trọt.', [
            ('s08_farm', 'Early farmers planting seeds in rows in a freshly plowed field with digging sticks, a small wheat sprout, sunny. {NOMO}', 'zoom_in', [{'type': 'counter', 'text': 'năm trước', 'to': 12000, 'x': .5, 'y': .2, 'at': 0}],
             'seeds drop and the sprouts grow')]),
        ('Nông nghiệp nuôi được nhiều người hơn trên cùng một mảnh đất, và cho phép tích trữ lương thực.', [
            ('s08_granary', 'A village with mud houses and a big granary overflowing with sacks of grain, people carrying baskets of wheat. {NOMO}', 'pan_right', [],
             'people carry baskets into the granary')]),
        ('Dân số tăng lên. Làng mạc mọc lên. Rồi thành phố, chữ viết, và mọi thứ chúng ta có hôm nay.', [
            ('s08_growth_1', 'A village growing into a walled ancient city with temples and a scribe writing on a clay tablet, crowds of people. {NOMO}', 'zoom_in', [],
             'buildings rise and the crowd grows'),
            ('s08_growth_2', 'The ancient city transforming into a modern Vietnamese city skyline with skyscrapers, cars and motorbikes. {NOMO}', 'zoom_out', [],
             'the skyline rises, traffic starts moving')]),
        ('Nhưng cái giá phải trả là thời gian.', [
            ('s08_scale', 'A big balance scale: on one side a pile of grain sacks and a house, on the other side a big hourglass, the hourglass side rising up. {NOMO}', 'fade', [L('Đổi thời gian lấy sự ổn định', y=.12)],
             'the scale tips and sand runs through the hourglass')]),
        ('Ruộng đồng cần người chăm từ sáng đến tối. Kho lúa cần người canh. Và một khi dân số đã tăng, không thể quay lại được nữa.', [
            ('s08_toil', 'An early farmer stick figure bent over in a field from sunrise to sunset, sweating, the sun moving across the sky behind him. {NOMO}', 'pan_left', [],
             'the sun moves across the sky while the farmer toils'),
            ('s08_guard', 'A tired farmer guarding a granary at night with a torch, yawning, a crowd of houses behind. {NOMO}', 'zoom_in', [],
             'the farmer yawns, the torch flickers')]),
        ('Chúng ta đổi sự tự do lấy sự ổn định.', [
            ('s08_trade', '{MO} sadly waving goodbye to a hammock and a sunny tree while holding a heavy sack of grain, bittersweet face.', 'zoom_in', [],
             'Mo waves goodbye, the hammock swings empty')]),
        ('Tất nhiên, không ai nên lãng mạn hóa quá khứ.', [
            ('s08_not_romantic', '{MO} shaking her finger at the viewer with a serious but kind face, a stormy cloud and a snake drawn behind her.', 'fade', [],
             'Mo wags her finger at the camera')]),
        ('Người tiền sử không có thuốc men, không có bệnh viện, và trẻ em chết yểu rất nhiều.', [
            ('s08_sick', '{MOM} worriedly caring for a feverish {BI} lying on furs, a wet leaf on his forehead, {MO} holding his hand with a worried face, dim light.', 'zoom_in', [],
             'Mom dabs Bi\'s forehead, Mo squeezes his hand')]),
        ('Nhưng có một điều họ có nhiều hơn chúng ta: thời gian dành cho nhau.', [
            ('s08_together', 'The whole family hugging together under a big tree at golden sunset, {MO} in the middle with a big happy smile.', 'zoom_in', [],
             'the family hugs, leaves drift in the golden light')]),
        ('Vậy nên lần tới, khi bạn kẹt giữa biển xe máy lúc tám giờ sáng, hãy thử nghĩ về cô bé Mơ của năm mươi nghìn năm trước.', [
            ('s08_back_traffic', 'Back in the motorbike traffic jam, {YOU} on his scooter with a small thought bubble showing a prehistoric girl with an orange hair bun waving from under a tree. {NOMO}', 'fade', [],
             'the thought bubble appears above the worker in the traffic')]),
        ('Bạn thì có tất cả mọi thứ, trừ thời gian. Còn Mơ thì chẳng có gì, trừ thời gian.', [
            ('s08_contrast', 'Split image: left {YOU} surrounded by gadgets, car keys and money but staring at a clock with stress; right {MO} with nothing but a stick, sitting happily watching a sunset.', 'zoom_in', [L('Bạn thì… còn Mơ thì…', y=.12)],
             'the clock ticks on the left, the sun sets on the right')]),
        ('Và có lẽ, câu hỏi đáng giá nhất không phải là họ làm gì cả ngày, mà là chúng ta muốn dành ngày của mình cho điều gì.', [
            ('s08_end', '{MO} turning toward the viewer and smiling warmly, waving goodbye, sunset savanna behind her.', 'zoom_out', [],
             'Mo turns and waves goodbye to the camera')]),
    ]},
]


def shots():
    for sc in SCENES:
        for _, ss in sc['lines']:
            for s in ss:
                yield s


# Flow gắn cờ "unusual activity" 27/09 trước khi kịp tạo 17 shot chương 7–8: dùng lại hình đã có
# làm cảnh gợi nhắc (callback) thay vì tạo mới.
REUSE = {
    's07_guard': 's03_night_wake', 's07_safe': 's07_sleep',
    's08_why': 's01_question', 's08_farm': 's02_two_1', 's08_granary': 's02_farmer',
    's08_growth_1': 's01_timeline', 's08_growth_2': 's01_traffic_1', 's08_scale': 's04_contrast',
    's08_toil': 's02_farmer_sick', 's08_guard': 's01_office', 's08_trade': 's06_rest_1',
    's08_not_romantic': 's02_myth_3', 's08_sick': 's02_myth_1', 's08_together': 's06_bond',
    's08_back_traffic': 's01_traffic_2', 's08_contrast': 's01_mirror', 's08_end': 'x_wave',
}
# Ảnh cận biểu cảm của Mơ chen vào 40% cuối của shot (chỉ bản ảnh, khi shot dài hơn 3,2 s).
REACT = {
    's01_question': 'x_idea', 's02_hunter_fit': 'x_proud', 's02_family': 'x_wave', 's03_vote': 'x_jump',
    's04_week': 'x_jump', 's04_bars': 'x_proud', 's04_memory': 'x_idea', 's05_fish': 'x_jump',
    's06_knap_2': 'x_proud', 's07_music': 'x_jump', 's03_sleep_q': 'x_idea', 's06_imagine': 'x_wave',
}
