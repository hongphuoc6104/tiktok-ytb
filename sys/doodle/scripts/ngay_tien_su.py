"""Kịch bản tự biên soạn: "Người tiền sử làm gì cả ngày?" (kênh tiền sử, 16:9, ~9–10 phút).

Mỗi cảnh: câu lời dẫn + beat (hình, hiệu ứng, overlay) gắn vào câu. Câu không có beat
giữ hình trước đó. Hình là cảnh doodle tự vẽ bằng doodle/draw.py (không dùng AI tạo ảnh).
Số liệu ghi theo cách nói thận trọng; không gắn trích dẫn giả.
"""

TITLE = 'Người tiền sử làm gì cả ngày?'
TITLES = ['Người tiền sử làm gì cả ngày?', 'Một ngày 50.000 năm trước: nhàn hơn bạn nghĩ?',
          'Không báo thức, không deadline: tổ tiên sống thế nào?']
THUMB = {'image': 'rest_tree', 'text': 'NHÀN HƠN BẠN?'}
HOOK = ('Tám giờ sáng, bạn kẹt giữa biển xe máy. Năm mươi nghìn năm trước, tổ tiên bạn thức dậy '
        'không chuông báo thức, không deadline. Vậy họ làm gì suốt cả ngày?')
TAGS = ['người tiền sử', 'săn bắt hái lượm', 'lịch sử loài người', 'thời đồ đá', 'tiền sử', 'khảo cổ học',
        'cuộc sống tiền sử', 'giải thích']

M = 'mascot'
IMAGES = {
    # --- hiện đại
    'traffic': {'bg': 'city', 'items': [['moto', 380, 1010, 1.25], ['you', 400, 950, .95, {'pose': 'ride', 'face': 'tired'}],
                                          ['moto', 960, 1020, 1.25, {'color': (80, 120, 200)}], ['worker', 980, 960, .95, {'pose': 'ride', 'face': 'sad'}],
                                          ['moto', 1540, 1010, 1.25, {'color': (90, 160, 90)}], ['you', 1560, 950, .95, {'pose': 'ride', 'face': 'neutral'}],
                                          ['clock', 1700, 230, .8, {'h': 8}]]},
    'you_phone': {'bg': 'city', 'items': [['moto', 900, 1010, 1.5], ['you', 920, 935, 1.15, {'pose': 'ride', 'face': 'tired'}],
                                            ['bubble', 1420, 330, 1.2, {'inner': ['calendar', 0, 50, .6, {'filled': 6}]}]]},
    'office': {'bg': 'paper', 'items': [['desk', 900, 980, 1.4], ['you', 1350, 990, 1.2, {'pose': 'think', 'face': 'tired', 'flip': True}],
                                          ['clock', 400, 300, .9, {'h': 5, 'm': 30}]]},
    'wake_modern': {'bg': 'paper', 'items': [['bed', 900, 980, 1.5], ['clock', 1500, 420, 1.0, {'h': 6, 'm': 30}], ['question', 450, 420, 1.2]]},
    # --- mở đầu tiền sử
    'dawn_wake': {'bg': 'dawn', 'items': [['hut', 420, 820, 1.0], ['mascot', 1020, 960, 1.35, {'pose': 'arms_up', 'face': 'smile'}],
                                            ['tree', 1600, 780, .9]]},
    'dawn_sleepers': {'bg': 'dawn', 'items': [['fire', 960, 900, .8, {'lit': False}], ['mascot', 620, 990, .9, {'pose': 'sleep'}],
                                                ['woman', 1350, 990, .9, {'pose': 'sleep'}], ['kid', 1600, 1000, 1.0, {'pose': 'sleep'}]]},
    'counter_bg': {'bg': 'paper', 'items': [['mascot', 1450, 980, 1.3, {'pose': 'point', 'face': 'smile', 'flip': True}], ['feet', 250, 950, 1.0, {'n': 8}]]},
    'what_do': {'bg': 'day', 'items': [['mascot', 960, 980, 1.5, {'pose': 'think', 'face': 'neutral'}], ['question', 1400, 420, 1.4], ['question', 520, 380, .9]]},
    # --- niềm tin cũ
    'myth_scary': {'bg': 'rain', 'items': [['cave', 600, 800, 1.0], ['mascot', 1200, 980, 1.3, {'pose': 'spear', 'face': 'sad'}],
                                              ['bones', 1600, 960, .8]]},
    'myth_chase': {'bg': 'day', 'items': [['mammoth', 1350, 960, 1.1], ['mascot', 500, 980, 1.2, {'pose': 'walk', 'face': 'wow', 'flip': True}]]},
    'skeletons': {'bg': 'paper', 'items': [['skeletons', 960, 950, 1.3]]},
    'skel_q': {'bg': 'paper', 'items': [['skeletons', 800, 950, 1.1], ['question', 1500, 520, 1.3]]},
    'farmer_tired': {'bg': 'day', 'items': [['wheat', 600, 900, 1.3], ['man', 1150, 980, 1.2, {'pose': 'carry', 'face': 'tired'}],
                                               ['wheat', 1550, 900, 1.0]]},
    'hunter_fit': {'bg': 'day', 'items': [['tree', 400, 780, 1.0], ['mascot', 1000, 980, 1.35, {'pose': 'spear', 'face': 'smile'}], ['bush', 1500, 820, 1.0]]},
    'bars_health': {'bg': 'paper', 'items': [['bars', 900, 900, 1.3, {'a': .55, 'b': 1.0}], ['mascot', 1550, 980, 1.0, {'pose': 'point', 'face': 'wow', 'flip': True}]]},
    # --- bình minh
    'fire_relight': {'bg': 'dawn', 'items': [['fire', 960, 920, 1.1], ['mascot', 700, 990, 1.1, {'pose': 'sit', 'face': 'smile'}],
                                                ['elder', 1250, 990, 1.1, {'pose': 'sit', 'face': 'smile', 'flip': True}]]},
    'sleep_split': {'bg': 'night', 'items': [['fire', 700, 930, .8], ['mascot', 1150, 990, 1.1, {'pose': 'sit', 'face': 'smile'}],
                                                ['woman', 1500, 1000, .9, {'pose': 'sleep'}]]},
    'sleep_hours': {'bg': 'paper', 'items': [['clock', 700, 520, 1.3, {'h': 7}], ['mascot', 1350, 1000, 1.2, {'pose': 'sleep'}]]},
    'water_trip': {'bg': 'day', 'items': [['river', 0, 930], ['mascot', 700, 900, 1.2, {'pose': 'carry', 'face': 'smile'}],
                                             ['kid', 1100, 900, 1.3, {'pose': 'walk'}], ['tree', 1650, 760, .8]]},
    'morning_talk': {'bg': 'dawn', 'items': [['mascot', 600, 980, 1.2, {'pose': 'point', 'face': 'smile'}], ['man', 1000, 980, 1.2, {'pose': 'think', 'face': 'neutral'}],
                                                ['woman', 1380, 980, 1.2, {'pose': 'stand', 'face': 'smile', 'flip': True}]]},
    # --- làm việc
    'gather': {'bg': 'day', 'items': [['bush', 500, 900, 1.3], ['woman', 950, 990, 1.2, {'pose': 'carry', 'prop': 'basket', 'face': 'smile'}],
                                         ['kid', 1250, 990, 1.3, {'pose': 'point'}], ['bush', 1600, 880, 1.0]]},
    'gather_roots': {'bg': 'day', 'items': [['woman', 700, 990, 1.2, {'pose': 'sit', 'face': 'smile'}], ['basket', 1000, 980, 1.1, {'full': True}],
                                               ['elder', 1400, 990, 1.1, {'pose': 'point', 'face': 'smile', 'flip': True}]]},
    'calendar_work': {'bg': 'paper', 'items': [['calendar', 960, 560, 1.3, {'filled': 2}], ['mascot', 960, 1030, .9, {'pose': 'arms_up', 'face': 'smile'}]]},
    'bars_work': {'bg': 'paper', 'items': [['bars', 900, 900, 1.3, {'a': .45, 'b': 1.0}], ['you', 1560, 990, 1.0, {'pose': 'think', 'face': 'tired', 'flip': True}]]},
    'map_trip': {'bg': 'paper', 'items': [['map', 960, 520, 1.3], ['mascot', 1600, 1000, .9, {'pose': 'point', 'face': 'smile', 'flip': True}]]},
    'chores': {'bg': 'day', 'items': [['fire', 500, 930, .8], ['stone', 900, 880, .7], ['man', 1150, 990, 1.1, {'pose': 'sit', 'face': 'neutral', 'prop': 'stone'}],
                                         ['basket', 1550, 960, .9, {'full': True}]]},
    # --- săn
    'hunt_track': {'bg': 'day', 'items': [['feet', 300, 960, 1.2, {'n': 7}], ['mascot', 1150, 980, 1.3, {'pose': 'walk', 'prop': 'spear', 'face': 'neutral'}],
                                             ['man', 1500, 980, 1.2, {'pose': 'spear', 'face': 'neutral'}]]},
    'hunt_deer': {'bg': 'day', 'items': [['deer', 1350, 960, 1.3], ['mascot', 500, 980, 1.2, {'pose': 'spear', 'face': 'neutral'}], ['bush', 900, 880, .9, {'berries': False}]]},
    'hunt_run': {'bg': 'day', 'items': [['deer', 1450, 960, 1.1], ['mascot', 700, 980, 1.3, {'pose': 'walk', 'face': 'tired'}]]},
    'hunt_fail': {'bg': 'dusk', 'items': [['mascot', 800, 980, 1.3, {'pose': 'stand', 'face': 'sad'}], ['man', 1200, 980, 1.2, {'pose': 'think', 'face': 'sad', 'flip': True}]]},
    'fish': {'bg': 'day', 'items': [['river', 0, 930], ['mascot', 900, 900, 1.3, {'pose': 'arms_up', 'prop': 'fish', 'face': 'wow'}]]},
    'share_meat': {'bg': 'dusk', 'items': [['fire', 960, 930, 1.0], ['mascot', 600, 990, 1.0, {'pose': 'carry', 'face': 'smile'}], ['woman', 1300, 990, 1.0, {'pose': 'stand', 'face': 'smile', 'flip': True}],
                                              ['kid', 1500, 1000, 1.2, {'pose': 'arms_up', 'face': 'wow'}], ['elder', 300, 990, 1.0, {'pose': 'sit', 'face': 'smile'}]]},
    # --- chiều rảnh
    'rest_tree': {'bg': 'day', 'items': [['tree', 1150, 800, 1.3], ['mascot', 1000, 990, 1.3, {'pose': 'sit', 'face': 'smile'}],
                                            ['woman', 1400, 1000, 1.0, {'pose': 'sleep'}], ['kid', 500, 990, 1.3, {'pose': 'arms_up', 'face': 'smile'}]]},
    'toolmaking': {'bg': 'day', 'items': [['elder', 800, 990, 1.3, {'pose': 'sit', 'face': 'smile', 'prop': 'stone'}], ['kid', 1150, 990, 1.4, {'pose': 'think', 'face': 'wow', 'flip': True}],
                                             ['stone', 1450, 900, .8]]},
    'kids_play': {'bg': 'day', 'items': [['kid', 600, 990, 1.4, {'pose': 'walk', 'face': 'smile'}], ['kid', 950, 990, 1.4, {'pose': 'arms_up', 'face': 'wow'}],
                                            ['kid', 1300, 990, 1.4, {'pose': 'walk', 'face': 'smile', 'flip': True}], ['tree', 1700, 800, .8]]},
    'chat': {'bg': 'day', 'items': [['mascot', 700, 990, 1.2, {'pose': 'point', 'face': 'smile'}], ['woman', 1050, 990, 1.2, {'pose': 'think', 'face': 'wow', 'flip': True}],
                                       ['elder', 1400, 990, 1.1, {'pose': 'sit', 'face': 'smile', 'flip': True}]]},
    'cave_art': {'bg': 'cave', 'items': [['hands', 960, 380, 1.2], ['mascot', 700, 990, 1.1, {'pose': 'arms_up', 'face': 'wow', 'prop': 'torch'}]]},
    'bubble_free': {'bg': 'day', 'items': [['you', 500, 990, 1.2, {'pose': 'think', 'face': 'tired'}], ['bubble', 1250, 420, 1.3, {'inner': ['mascot', 0, 110, .45, {'pose': 'sit', 'face': 'smile'}]}]]},
    # --- đêm
    'night_fire': {'bg': 'night', 'items': [['fire', 960, 930, 1.2], ['mascot', 560, 990, 1.1, {'pose': 'point', 'face': 'smile'}],
                                               ['elder', 1360, 990, 1.0, {'pose': 'sit', 'face': 'wow', 'flip': True}], ['kid', 1600, 1000, 1.2, {'pose': 'sit', 'face': 'wow', 'flip': True}]]},
    'story_bubble': {'bg': 'night', 'items': [['fire', 700, 930, 1.0], ['elder', 1000, 990, 1.1, {'pose': 'sit', 'face': 'smile', 'flip': True}],
                                                 ['bubble', 1450, 380, 1.2, {'inner': ['mammoth', -10, 100, .35]}]]},
    'flute': {'bg': 'night', 'items': [['fire', 1300, 930, .9], ['flute', 760, 520, 1.3], ['notes', 1000, 330, 1.2], ['mascot', 600, 990, 1.0, {'pose': 'sit', 'face': 'smile'}]]},
    'stars': {'bg': 'night', 'items': [['mascot', 800, 990, 1.3, {'pose': 'point', 'face': 'wow'}], ['kid', 1150, 1000, 1.4, {'pose': 'stand', 'face': 'wow'}]]},
    'guard': {'bg': 'night', 'items': [['fire', 800, 930, .9], ['mascot', 1150, 990, 1.2, {'pose': 'spear', 'face': 'neutral'}],
                                          ['woman', 450, 1000, .9, {'pose': 'sleep'}], ['kid', 1600, 1010, 1.0, {'pose': 'sleep'}]]},
    'sleep_group': {'bg': 'night', 'items': [['fire', 960, 930, .7, {'lit': False}], ['mascot', 500, 1000, 1.0, {'pose': 'sleep'}],
                                                ['man', 1350, 1000, 1.0, {'pose': 'sleep'}], ['kid', 1650, 1010, 1.0, {'pose': 'sleep'}]]},
    # --- nông nghiệp & kết
    'farm_start': {'bg': 'day', 'items': [['wheat', 500, 900, 1.2], ['wheat', 900, 900, 1.2], ['man', 1350, 990, 1.2, {'pose': 'carry', 'face': 'tired'}]]},
    'granary': {'bg': 'day', 'items': [['hut', 600, 830, 1.1], ['hut', 1100, 830, 1.1], ['basket', 1500, 980, 1.2, {'full': True}], ['wheat', 1750, 900, .8]]},
    'crowd': {'bg': 'day', 'items': [['man', 300, 990, .9, {'face': 'tired'}], ['woman', 550, 990, .9, {'face': 'sad'}], ['man', 800, 990, .9, {'face': 'tired', 'pose': 'carry'}],
                                        ['woman', 1050, 990, .9, {'face': 'tired'}], ['elder', 1300, 990, .9, {'face': 'sad'}], ['man', 1550, 990, .9, {'face': 'tired'}],
                                        ['wheat', 1800, 900, .8]]},
    'trade_off': {'bg': 'paper', 'items': [['basket', 600, 800, 1.4, {'full': True}], ['clock', 1300, 520, 1.2, {'h': 11, 'm': 55}], ['arrow', 800, 600, 1.0, {'to': (1120, 540)}]]},
    'end_traffic': {'bg': 'city', 'items': [['moto', 800, 1010, 1.5], ['you', 820, 935, 1.15, {'pose': 'ride', 'face': 'neutral'}],
                                              ['bubble', 1400, 360, 1.25, {'inner': ['mascot', 0, 110, .45, {'pose': 'arms_up', 'face': 'smile'}]}]]},
    'end_mascot': {'bg': 'dusk', 'items': [['fire', 1300, 930, 1.0], ['mascot', 800, 990, 1.5, {'pose': 'point', 'face': 'smile'}]]},
}

# Beat = (image, effect, overlays). Overlay fields per content-v3 (x,y in 0..1).
def L(text, x=.5, y=.14, at=0):
    return {'type': 'label', 'text': text, 'x': x, 'y': y, 'at': at}


def CH(text):
    return {'type': 'chapter_title', 'text': text, 'x': .5, 'y': .2, 'at': 0}


SCENES = [
    {'id': 'SC01', 'chapter': 'Mở đầu', 'lines': [
        ('Tám giờ sáng. Bạn đang kẹt giữa một biển xe máy.', ('traffic', 'zoom_in', [L('8:00 SÁNG')])),
        ('Còi xe inh ỏi, khói bụi mù mịt, và điện thoại trong túi thì rung liên tục.', None),
        ('Đó là tin nhắn nhắc bạn về cuộc họp lúc chín giờ, và cái deadline chiều nay.', ('you_phone', 'zoom_in', [L('Cuộc họp 9h • Deadline 17h', y=.1)])),
        ('Rồi bạn sẽ ngồi tám tiếng trước màn hình, về nhà khi trời đã tối.', ('office', 'pan_right', [])),
        ('Sáng mai, mọi thứ lặp lại, từ tiếng chuông báo thức đầu tiên.', ('wake_modern', 'zoom_out', [])),
        ('Bây giờ, hãy tua ngược thời gian.', ('counter_bg', 'fade', [{'type': 'counter', 'text': 'năm trước', 'to': 50000, 'x': .38, 'y': .38, 'at': .2}])),
        ('Không phải một trăm năm, không phải một nghìn năm, mà là năm mươi nghìn năm.', None),
        ('Một người đàn ông mở mắt khi ánh nắng đầu tiên chạm vào mặt.', ('dawn_wake', 'zoom_in', [])),
        ('Không ai đánh thức anh. Không ai chờ anh ở văn phòng. Cũng không có cuộc họp nào cả.', ('dawn_sleepers', 'pan_left', [])),
        ('Anh chỉ có vài người thân, một bếp lửa đã tàn, và cả một ngày dài phía trước.', None),
        ('Câu hỏi là: anh sẽ làm gì với ngày đó?', ('what_do', 'pop', [L('Họ làm gì cả ngày?', y=.12)])),
        ('Và vì sao câu trả lời có thể khiến bạn nhìn lại chính một ngày của mình?', None),
    ]},
    {'id': 'SC02', 'chapter': 'Chúng ta đã nghĩ sai?', 'lines': [
        ('Nếu hỏi một người bất kỳ, bạn sẽ nghe một câu trả lời quen thuộc.', ('myth_scary', 'fade', [CH('Chúng ta đã nghĩ sai?')])),
        ('Người tiền sử sống khổ sở, lúc nào cũng đói, lúc nào cũng sợ.', None),
        ('Họ chạy trốn thú dữ từ sáng đến tối, và chết trẻ vì bệnh tật.', ('myth_chase', 'slide_left', [])),
        ('Trong hình dung đó, mỗi phút của họ đều là cuộc chiến sinh tồn.', None),
        ('Nhưng khi các nhà khảo cổ đào lên những bộ xương cổ, câu chuyện bắt đầu khác đi.', ('skeletons', 'zoom_in', [])),
        ('Hãy thử so sánh hai người.', None),
        ('Một người sống bằng săn bắt và hái lượm. Người kia là một trong những nông dân đầu tiên.', ('skel_q', 'pan_right', [L('Ai khỏe hơn?', x=.78, y=.2)])),
        ('Nhiều người sẽ đoán người nông dân khỏe hơn, vì có nhà, có kho lúa, có bữa ăn ổn định.', ('farmer_tired', 'zoom_in', [])),
        ('Thế nhưng ở nhiều nơi trên thế giới, kết quả lại ngược lại.', ('hunter_fit', 'pop', [])),
        ('Những người nông dân đầu tiên thường thấp hơn, răng sâu nhiều hơn, xương khớp mòn hơn.', ('bars_health', 'zoom_in', [L('Sâu răng • Mòn khớp • Thấp hơn', y=.12)])),
        ('Trong khi người săn bắt hái lượm trước họ lại có bộ xương chắc khỏe đáng ngạc nhiên.', None),
        ('Vậy một ngày của những người ấy thật sự trông như thế nào?', ('what_do', 'zoom_out', [])),
    ]},
    {'id': 'SC03', 'chapter': 'Bình minh không có chuông báo thức', 'lines': [
        ('Ngày của họ bắt đầu theo mặt trời, chứ không theo đồng hồ.', ('dawn_wake', 'fade', [CH('Bình minh không có chuông báo thức')])),
        ('Việc đầu tiên thường là khơi lại bếp lửa từ đống than còn ấm.', ('fire_relight', 'zoom_in', [])),
        ('Giữ được lửa qua đêm là cả một kỹ năng, vì nhóm lửa lại từ đầu tốn công hơn nhiều.', None),
        ('Còn giấc ngủ của họ thì sao?', ('sleep_hours', 'fade', [])),
        ('Khi các nhà nghiên cứu theo dõi những nhóm săn bắt hái lượm ngày nay, họ thấy mọi người thường ngủ khoảng sáu đến bảy tiếng.', ('sleep_hours', 'zoom_in', [L('~6–7 tiếng mỗi đêm', y=.12)])),
        ('Không nhiều hơn chúng ta là mấy.', None),
        ('Điều khác biệt là họ ngủ theo nhịp của bóng tối, và thức dậy theo ánh sáng.', ('sleep_split', 'pan_left', [])),
        ('Một số nhà sử học còn cho rằng ở nhiều nơi, người xưa từng ngủ thành hai giấc, thức dậy một lúc giữa đêm.', None),
        ('Sau bếp lửa là nước.', ('water_trip', 'fade', [L('Việc đầu ngày: lửa và nước', y=.12)])),
        ('Cả nhóm thường chọn nơi dựng trại gần một con suối hay một dòng sông.', None),
        ('Trẻ con đi theo người lớn, vừa chơi vừa học đường đi.', ('water_trip', 'zoom_in', [])),
        ('Rồi mọi người ngồi lại, bàn xem hôm nay ai đi đâu, làm gì.', ('morning_talk', 'pan_right', [])),
        ('Không có ông chủ nào giao việc. Quyết định được đưa ra cùng nhau.', None),
    ]},
    {'id': 'SC04', 'chapter': 'Làm việc bao nhiêu giờ một ngày?', 'lines': [
        ('Và đây là phần bất ngờ nhất.', ('calendar_work', 'fade', [CH('Làm việc bao nhiêu giờ?')])),
        ('Vào những năm sáu mươi, nhà nhân học Richard Lee đã sống cùng người San ở sa mạc Kalahari và ghi lại họ dành bao nhiêu thời gian để kiếm ăn.', ('map_trip', 'zoom_in', [])),
        ('Câu trả lời khiến nhiều người sửng sốt: chỉ khoảng hai đến ba ngày mỗi tuần.', ('calendar_work', 'zoom_in', [L('2–3 ngày kiếm ăn mỗi tuần', y=.1)])),
        ('Tính ra, thời gian săn bắt và hái lượm có khi chỉ vào khoảng mười lăm đến hai mươi giờ một tuần.', ('bars_work', 'pop', [L('Kiếm ăn', x=.37, y=.12), L('Bạn', x=.58, y=.12)])),
        ('Tất nhiên, con số này còn nhiều tranh luận.', None),
        ('Nếu cộng thêm chế tạo công cụ, nấu nướng, lấy nước và kiếm củi, tổng thời gian làm việc sẽ dài hơn.', ('chores', 'pan_left', [])),
        ('Và cuộc sống ở vùng giàu tài nguyên chắc chắn dễ thở hơn ở vùng khắc nghiệt.', None),
        ('Nhưng ngay cả khi tính đủ, bức tranh vẫn rất khác với tám tiếng ngồi văn phòng, cộng thêm hai tiếng kẹt xe.', ('bars_work', 'zoom_out', [])),
        ('Vậy công việc buổi sáng của họ là gì?', ('gather', 'fade', [])),
        ('Phần lớn thức ăn thường đến từ hái lượm: quả mọng, hạt, rau dại, củ và mật ong.', ('gather', 'zoom_in', [L('Quả • Hạt • Củ • Mật ong', y=.12)])),
        ('Công việc này đòi hỏi trí nhớ đáng kinh ngạc.', None),
        ('Họ phải biết cây nào ăn được, cây nào có độc, mùa nào quả chín, và chỗ nào có củ nằm sâu dưới đất.', ('gather_roots', 'pan_right', [])),
        ('Mỗi chuyến đi là một bài học, và người lớn tuổi chính là cuốn sách sống của cả nhóm.', None),
    ]},
    {'id': 'SC05', 'chapter': 'Cuộc săn và luật chia phần', 'lines': [
        ('Săn bắn thì khác. Nó hiếm hơn, nguy hiểm hơn, và thường thất bại.', ('hunt_track', 'fade', [CH('Cuộc săn và luật chia phần')])),
        ('Một nhóm nhỏ đi theo dấu chân thú, đọc từng vết cỏ gãy, từng dấu phân còn mới.', ('hunt_track', 'pan_left', [])),
        ('Con người không nhanh bằng linh dương, cũng không khỏe bằng sư tử.', ('hunt_deer', 'zoom_in', [])),
        ('Nhưng chúng ta có một vũ khí đặc biệt: khả năng chạy bền.', ('hunt_run', 'slide_left', [L('Vũ khí bí mật: chạy bền', y=.12)])),
        ('Cơ thể con người đổ mồ hôi để làm mát, nên có thể đi và chạy hàng giờ dưới nắng.', None),
        ('Có giả thuyết cho rằng tổ tiên ta từng bám theo con mồi cho đến khi nó kiệt sức vì nóng.', None),
        ('Dù vậy, nhiều buổi săn kết thúc tay trắng.', ('hunt_fail', 'zoom_in', [])),
        ('Có ngày, bữa tối là cá bắt được ở sông, chứ không phải thịt thú lớn.', ('fish', 'pop', [])),
        ('Và khi có thịt, điều quan trọng nhất không phải là ai săn được, mà là chia thế nào.', ('share_meat', 'fade', [])),
        ('Ở nhiều nhóm săn bắt hái lượm ngày nay, thịt được chia cho cả nhóm, kể cả người không đi săn.', ('share_meat', 'zoom_in', [L('Thịt chia cho cả nhóm', y=.12)])),
        ('Người khoe khoang chiến công thường bị trêu chọc để giữ cho không ai tự cho mình là hơn người.', None),
        ('Hôm nay bạn chia cho tôi, mai tôi chia lại cho bạn. Đó chính là tấm bảo hiểm của họ.', None),
    ]},
    {'id': 'SC06', 'chapter': 'Buổi chiều của những người rảnh rỗi', 'lines': [
        ('Khi mặt trời lên cao và trời nóng nhất, nhiều nhóm đơn giản là nghỉ ngơi.', ('rest_tree', 'fade', [CH('Buổi chiều rảnh rỗi')])),
        ('Họ ngồi dưới bóng cây, ngủ trưa, trò chuyện, chải tóc cho nhau.', ('rest_tree', 'zoom_in', [])),
        ('Người già dạy trẻ con cách ghè đá để làm dao và mũi giáo.', ('toolmaking', 'pan_right', [])),
        ('Một con dao đá tốt cần nhiều giờ luyện tay, và kinh nghiệm được truyền qua từng thế hệ.', None),
        ('Trẻ con thì có rất nhiều thời gian để chơi.', ('kids_play', 'slide_left', [])),
        ('Chúng chạy nhảy, bắt chước người lớn đi săn, và tự tìm quả ăn gần trại.', None),
        ('Còn người lớn thì làm một việc mà chúng ta hay xem nhẹ: nói chuyện.', ('chat', 'fade', [])),
        ('Họ kể về ai đang giận ai, chỗ nào có nhiều quả, đàn thú đang di chuyển về đâu.', ('chat', 'zoom_in', [])),
        ('Những câu chuyện đó giữ cho cả nhóm gắn bó, và giúp họ sống sót.', None),
        ('Một số người còn dùng thời gian rảnh để làm một thứ hoàn toàn không cần cho sinh tồn: nghệ thuật.', ('cave_art', 'fade', [])),
        ('Trên vách hang ở nhiều nơi, người xưa để lại dấu bàn tay và hình vẽ động vật, có những bức đã hơn bốn mươi nghìn năm tuổi.', ('cave_art', 'zoom_in', [L('Hơn 40.000 năm tuổi', y=.12)])),
        ('Hãy tưởng tượng xem: một người không có deadline, không có tin nhắn, và dành cả buổi chiều để vẽ.', ('bubble_free', 'pop', [])),
    ]},
    {'id': 'SC07', 'chapter': 'Đêm bên ngọn lửa', 'lines': [
        ('Khi trời tối, cả nhóm lại quây quần bên bếp lửa.', ('night_fire', 'fade', [CH('Đêm bên ngọn lửa')])),
        ('Lửa giữ ấm, xua thú dữ, nấu chín thức ăn, và kéo dài thêm vài giờ cho một ngày.', ('night_fire', 'zoom_in', [L('Ấm • An toàn • Nấu chín', y=.12)])),
        ('Nghiên cứu ở một số nhóm săn bắt hái lượm cho thấy câu chuyện ban đêm khác hẳn ban ngày.', ('story_bubble', 'fade', [])),
        ('Ban ngày người ta nói về công việc. Ban đêm, người ta kể chuyện.', None),
        ('Chuyện về những cuộc săn xa xưa, về tổ tiên, về các vì sao và những con vật khổng lồ.', ('story_bubble', 'zoom_in', [])),
        ('Và có cả âm nhạc.', ('flute', 'pop', [])),
        ('Các nhà khảo cổ đã tìm thấy những chiếc sáo làm từ xương chim, có tuổi khoảng bốn mươi nghìn năm.', ('flute', 'zoom_in', [L('Sáo xương ~40.000 năm', y=.12)])),
        ('Nghĩa là từ rất lâu, con người đã ngồi bên lửa và thổi những giai điệu đầu tiên.', None),
        ('Trẻ con nằm ngửa nhìn trời sao, nơi người lớn chỉ cho chúng những hình thù quen thuộc.', ('stars', 'pan_left', [])),
        ('Rồi mọi người ngủ gần nhau, quanh bếp lửa.', ('sleep_group', 'fade', [])),
        ('Luôn có người ngủ chập chờn hoặc thức giấc giữa chừng, như những người canh gác tự nhiên.', ('guard', 'zoom_in', [])),
        ('Không ai phải cô đơn trong bóng tối.', ('sleep_group', 'zoom_out', [])),
    ]},
    {'id': 'SC08', 'chapter': 'Cái giá của sự tiến bộ', 'lines': [
        ('Vậy tại sao chúng ta lại từ bỏ lối sống đó?', ('farm_start', 'fade', [CH('Cái giá của sự tiến bộ')])),
        ('Khoảng mười hai nghìn năm trước, ở một số nơi, con người bắt đầu trồng trọt.', ('farm_start', 'zoom_in', [{'type': 'counter', 'text': 'năm trước', 'to': 12000, 'x': .5, 'y': .2, 'at': 0}])),
        ('Nông nghiệp nuôi được nhiều người hơn trên cùng một mảnh đất, và cho phép tích trữ lương thực.', ('granary', 'pan_right', [])),
        ('Dân số tăng lên. Làng mạc mọc lên. Rồi thành phố, chữ viết, và mọi thứ chúng ta có hôm nay.', ('crowd', 'zoom_in', [])),
        ('Nhưng cái giá phải trả là thời gian.', ('trade_off', 'fade', [L('Đổi thời gian lấy sự ổn định', y=.12)])),
        ('Ruộng đồng cần người chăm từ sáng đến tối. Kho lúa cần người canh. Và một khi dân số đã tăng, không thể quay lại được nữa.', ('farmer_tired', 'pan_left', [])),
        ('Chúng ta đổi sự tự do lấy sự ổn định.', None),
        ('Tất nhiên, không ai nên lãng mạn hóa quá khứ.', ('myth_scary', 'fade', [])),
        ('Người tiền sử không có thuốc men, không có bệnh viện, và trẻ em chết yểu rất nhiều.', None),
        ('Nhưng có một điều họ có nhiều hơn chúng ta: thời gian dành cho nhau.', ('rest_tree', 'zoom_in', [])),
        ('Vậy nên lần tới, khi bạn kẹt giữa biển xe máy lúc tám giờ sáng, hãy thử nghĩ về người đàn ông năm mươi nghìn năm trước.', ('end_traffic', 'fade', [])),
        ('Bạn thì có tất cả mọi thứ, trừ thời gian. Còn anh ấy thì chẳng có gì, trừ thời gian.', ('end_traffic', 'zoom_in', [L('Bạn thì… còn họ thì…', y=.12)])),
        ('Và có lẽ, câu hỏi đáng giá nhất không phải là họ làm gì cả ngày, mà là chúng ta muốn dành ngày của mình cho điều gì.', ('end_mascot', 'zoom_out', [])),
    ]},
]
