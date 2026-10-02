"""
Bộ Kịch Bản Micro-Drama 4 Hồi Cho Lô 50 Từ Vựng (#32 đến #81)
Phong cách: Micro-Drama đời thường, hài hước, tếu táo của Mascot CH01 qua giọng đọc Adam bựa.
Đảm bảo:
- Hồi 1 (SC01): Tình huống khẩn cấp / oái oăm (3.0-3.5s)
- Hồi 2 (SC02): Giới thiệu từ vựng tiếng Anh tự nhiên (3.5-4.0s)
- Hồi 3 (SC03): Luyện nói phản xạ + khoảng dừng thực hành 1.2s (4.0-5.0s)
- Hồi 4 (SC04): Cú twist meme bất ngờ, hài hước (3.5-4.5s)
- Phụ đề (Cues): Tuyệt đối dưới 24 ký tự/dòng, không chứa '\\n'.
"""

DRAMA_DATA = {
    "leave": {
        "title": "Rời đi",
        "scenes": [
            ("Còn đúng năm phút nữa hết giờ làm mà sếp chuẩn bị giao thêm việc!", 0.20),
            ("Phải chuồn lẹ khỏi công ty thôi, tiếng Anh gọi là: LEAVE!", 0.20),
            ("Mau mau leave kẻo bị bắt ở lại tăng ca! Nhắc lại theo tui nha: LEAVE!", 1.20),
            ("Vừa bước chân ra khỏi cửa thì chạm mặt ngay giám đốc bước vào! Đứng hình!", 0.40)
        ],
        "cues": [
            {"text": "Năm phút nữa hết giờ...", "start": 0.0, "end": 1.6},
            {"text": "...sếp tính giao thêm việc!", "start": 1.6, "end": 3.3},
            {"text": "Phải chuồn lẹ khỏi đây,", "start": 3.5, "end": 5.1},
            {"text": "tiếng Anh gọi là: LEAVE!", "start": 5.1, "end": 7.2},
            {"text": "Mau mau leave kẻo tăng ca!", "start": 7.4, "end": 9.3},
            {"text": "(Nhắc lại theo tui: LEAVE!)", "start": 9.3, "end": 13.6},
            {"text": "Vừa bước ra khỏi cửa...", "start": 13.8, "end": 15.1},
            {"text": "...chạm mặt ngay giám đốc!", "start": 15.1, "end": 18.5}
        ]
    },
    "arrive": {
        "title": "Đến nơi",
        "scenes": [
            ("Phóng xe bạt mạng giữa trưa nắng để kịp giờ phỏng vấn xin việc!", 0.20),
            ("Cuối cùng cũng đã đến nơi đúng giờ hẹn, tiếng Anh là: ARRIVE!", 0.20),
            ("Mừng quá tui vừa arrive rồi nè! Cùng đọc to theo tui nha: ARRIVE!", 1.20),
            ("Bác bảo vệ cười tươi bảo: công ty dọn trụ sở sang quận khác từ hôm qua rồi cháu!", 0.40)
        ],
        "cues": [
            {"text": "Phóng xe bạt mạng...", "start": 0.0, "end": 1.6},
            {"text": "...để kịp giờ phỏng vấn!", "start": 1.6, "end": 3.3},
            {"text": "Cuối cùng cũng đến nơi,", "start": 3.5, "end": 5.0},
            {"text": "tiếng Anh là: ARRIVE!", "start": 5.0, "end": 7.2},
            {"text": "Mừng quá arrive rồi nè!", "start": 7.4, "end": 9.2},
            {"text": "(Cùng đọc to: ARRIVE!)", "start": 9.2, "end": 13.5},
            {"text": "Bác bảo vệ tươi cười bảo:", "start": 13.7, "end": 15.1},
            {"text": "...công ty chuyển chỗ rồi!", "start": 15.1, "end": 18.5}
        ]
    },
    "return": {
        "title": "Quay về",
        "scenes": [
            ("Đi công tác xa nhà cả tháng trời, chỉ thèm cảm giác bước vào nhà mình!", 0.20),
            ("Hành động quay trở về chốn thân quen, tiếng Anh gọi là: RETURN!", 0.20),
            ("Hôm nay tui được return về nhà rồi nè! Nói theo tui liền nha: RETURN!", 1.20),
            ("Vừa tra chìa vào ổ khóa thì thấy... người yêu cũ đang ngồi ăn cơm với mẹ mình!", 0.40)
        ],
        "cues": [
            {"text": "Đi công tác cả tháng trời...", "start": 0.0, "end": 1.7},
            {"text": "...chỉ thèm về nhà mình!", "start": 1.7, "end": 3.4},
            {"text": "Quay trở về chốn quen,", "start": 3.6, "end": 5.1},
            {"text": "tiếng Anh là: RETURN!", "start": 5.1, "end": 7.2},
            {"text": "Hôm nay return về nhà nè!", "start": 7.4, "end": 9.3},
            {"text": "(Nói theo tui nha: RETURN!)", "start": 9.3, "end": 13.6},
            {"text": "Vừa mở cửa bước vào...", "start": 13.8, "end": 15.0},
            {"text": "...thấy người yêu cũ ngồi đó!", "start": 15.0, "end": 18.5}
        ]
    },
    "errand": {
        "title": "Việc vặt phải chạy ra ngoài",
        "scenes": [
            ("Đang trùm chăn xem phim thì mẹ réo chạy đi mua hành, tỏi, nước mắm gấp!", 0.20),
            ("Mấy cái việc vặt vãnh phải xách xe chạy ra ngoài, tiếng Anh gọi là: ERRAND!", 0.20),
            ("Ra ngoài làm mấy cái errand cho mẹ nè! Cùng nhắc lại theo tui: ERRAND!", 1.20),
            ("Chạy xe năm cây số mua cho đủ đồ, về tới nơi mẹ bảo: thôi mẹ nấu xong luôn rồi!", 0.40)
        ],
        "cues": [
            {"text": "Đang trùm chăn xem phim...", "start": 0.0, "end": 1.7},
            {"text": "...mẹ réo đi mua mắm muối!", "start": 1.7, "end": 3.4},
            {"text": "Việc vặt chạy ra ngoài,", "start": 3.6, "end": 5.2},
            {"text": "tiếng Anh là: ERRAND!", "start": 5.2, "end": 7.3},
            {"text": "Làm errand cho mẹ nè!", "start": 7.5, "end": 9.3},
            {"text": "(Nhắc lại theo tui: ERRAND!)", "start": 9.3, "end": 13.7},
            {"text": "Mua đủ đồ về tới nơi...", "start": 13.9, "end": 15.2},
            {"text": "...mẹ bảo nấu xong rồi!", "start": 15.2, "end": 18.5}
        ]
    },
    "chore": {
        "title": "Việc nhà lặt vặt",
        "scenes": [
            ("Sáng chủ nhật đẹp trời mà mở mắt ra thấy nguyên một núi việc không tên chờ sẵn!", 0.20),
            ("Những công việc nhà lặt vặt gây ngán ngẩm này, tiếng Anh là: CHORE!", 0.20),
            ("Phải làm cho xong đống chore này mới được đi chơi! Đọc to theo tui: CHORE!", 1.20),
            ("Vừa lau dọn xong xuôi thì đứa em út làm đổ nguyên tô canh ra sàn! Khóc thét!", 0.40)
        ],
        "cues": [
            {"text": "Sáng chủ nhật đẹp trời...", "start": 0.0, "end": 1.7},
            {"text": "...nguyên núi việc chờ sẵn!", "start": 1.7, "end": 3.4},
            {"text": "Việc nhà lặt vặt ngán ngẩm,", "start": 3.6, "end": 5.2},
            {"text": "tiếng Anh gọi là: CHORE!", "start": 5.2, "end": 7.3},
            {"text": "Làm xong đống chore đã!", "start": 7.5, "end": 9.3},
            {"text": "(Đọc to theo tui: CHORE!)", "start": 9.3, "end": 13.6},
            {"text": "Vừa dọn xong xuôi thì...", "start": 13.8, "end": 15.1},
            {"text": "...em út đổ canh ra sàn!", "start": 15.1, "end": 18.5}
        ]
    },
    "housework": {
        "title": "Việc nhà",
        "scenes": [
            ("Lúc ở với mẹ thì sướng như vua, giờ ra ở riêng mới biết mùi cực khổ!", 0.20),
            ("Toàn bộ công việc nội trợ, quét dọn trong nhà, tiếng Anh gọi là: HOUSEWORK!", 0.20),
            ("Cuối tuần ở nhà cày housework mệt xỉu luôn! Nhại lại theo tui nè: HOUSEWORK!", 1.20),
            ("Dọn dẹp hì hục từ sáng tới tối, nhìn lại đồng hồ thấy hết luôn ngày nghỉ!", 0.40)
        ],
        "cues": [
            {"text": "Ở riêng mới biết mùi cực,", "start": 0.0, "end": 1.6},
            {"text": "việc gì cũng tới tay!", "start": 1.6, "end": 3.3},
            {"text": "Toàn bộ việc nội trợ dọn dẹp,", "start": 3.5, "end": 5.3},
            {"text": "tiếng Anh là: HOUSEWORK!", "start": 5.3, "end": 7.4},
            {"text": "Cày housework mệt xỉu!", "start": 7.6, "end": 9.4},
            {"text": "(Nhại lại theo tui: HOUSEWORK!)", "start": 9.4, "end": 13.8},
            {"text": "Dọn từ sáng tới tối...", "start": 14.0, "end": 15.2},
            {"text": "...hết luôn ngày nghỉ!", "start": 15.2, "end": 18.5}
        ]
    },
    "tidy": {
        "title": "Dọn cho gọn",
        "scenes": [
            ("Mẹ gọi điện báo mười phút nữa mẹ tới kiểm tra phòng trọ bất ngờ!", 0.20),
            ("Phải gom đồ đạc xếp dọn cho ngăn nắp liền tay, tiếng Anh là: TIDY!", 0.20),
            ("Mau mau tidy phòng đón mẹ lên chơi nào! Cùng đọc theo tui nha: TIDY!", 1.20),
            ("Nhét hết đồ dơ vô tủ quần áo rồi đóng sập cửa, ai ngờ tủ bung bản lề rớt ụp xuống!", 0.40)
        ],
        "cues": [
            {"text": "Mười phút nữa mẹ tới...", "start": 0.0, "end": 1.6},
            {"text": "...kiểm tra phòng trọ!", "start": 1.6, "end": 3.2},
            {"text": "Xếp dọn cho ngăn nắp,", "start": 3.4, "end": 4.9},
            {"text": "tiếng Anh là: TIDY!", "start": 4.9, "end": 7.0},
            {"text": "Mau tidy phòng đón mẹ!", "start": 7.2, "end": 9.0},
            {"text": "(Cùng đọc theo tui: TIDY!)", "start": 9.0, "end": 13.4},
            {"text": "Nhét hết đồ vô tủ...", "start": 13.6, "end": 14.9},
            {"text": "...tủ bung rớt ụp xuống!", "start": 14.9, "end": 18.4}
        ]
    },
    "sweep": {
        "title": "Quét",
        "scenes": [
            ("Lỡ tay làm đổ nguyên lọ muối tiêu rơi vãi tung tóe khắp sàn gạch!", 0.20),
            ("Phải lấy cây chổi ra quét gom bụi rác lại, tiếng Anh gọi là: SWEEP!", 0.20),
            ("Cầm chổi lên sweep sạch sẽ sàn nhà giùm tui nha! Nói theo tui liền: SWEEP!", 1.20),
            ("Vừa quét được một đống rác thì con mèo phóng qua làm tung tóe lại từ đầu!", 0.40)
        ],
        "cues": [
            {"text": "Lỡ làm đổ lọ muối tiêu...", "start": 0.0, "end": 1.7},
            {"text": "...rơi vãi tung tóe khắp sàn!", "start": 1.7, "end": 3.4},
            {"text": "Lấy chổi quét gom lại,", "start": 3.6, "end": 5.1},
            {"text": "tiếng Anh là: SWEEP!", "start": 5.1, "end": 7.2},
            {"text": "Sweep sạch sàn nhà nha!", "start": 7.4, "end": 9.2},
            {"text": "(Nói theo tui liền: SWEEP!)", "start": 9.2, "end": 13.5},
            {"text": "Vừa quét xong đống rác...", "start": 13.7, "end": 15.0},
            {"text": "...mèo phóng tung tóe lại!", "start": 15.0, "end": 18.5}
        ]
    },
    "mop": {
        "title": "Lau nhà bằng cây lau",
        "scenes": [
            ("Trời mưa nồm ẩm sàn nhà nhớp nháp trơn như sân trượt băng nghệ thuật!", 0.20),
            ("Phải nhúng cây lau nhà vô xô nước rồi lau sạch, tiếng Anh là: MOP!", 0.20),
            ("Lấy cây lau ra mop nhà cho khô ráo nào! Cùng nhắc lại theo tui: MOP!", 1.20),
            ("Vừa lau xong quay lưng bước đi thì trượt chân xoạc một đường tiếp đất bằng mông!", 0.40)
        ],
        "cues": [
            {"text": "Sàn nhà trơn trượt...", "start": 0.0, "end": 1.6},
            {"text": "...như sân trượt băng!", "start": 1.6, "end": 3.2},
            {"text": "Lau nhà bằng cây lau,", "start": 3.4, "end": 5.0},
            {"text": "tiếng Anh gọi là: MOP!", "start": 5.0, "end": 7.1},
            {"text": "Lấy cây ra mop nhà nè!", "start": 7.3, "end": 9.1},
            {"text": "(Nhắc lại theo tui: MOP!)", "start": 9.1, "end": 13.4},
            {"text": "Vừa lau xong bước đi...", "start": 13.6, "end": 14.9},
            {"text": "...trượt té xoạc một đường!", "start": 14.9, "end": 18.4}
        ]
    },
    "dust": {
        "title": "Phủi bụi",
        "scenes": [
            ("Mấy tháng không dọn kệ sách mà bụi bám dày cộm đóng cả tấc đất!", 0.20),
            ("Lấy khăn lông đi phủi sạch lớp bụi mờ này, tiếng Anh gọi là: DUST!", 0.20),
            ("Mau lấy chổi lông gà dust bụi bàn học đi nha! Đọc to theo tui nè: DUST!", 1.20),
            ("Vừa phẩy một cái bụi bay mù mịt làm hắt xì hơi liên tục mười cái suýt ngất!", 0.40)
        ],
        "cues": [
            {"text": "Kệ sách bám bụi dày...", "start": 0.0, "end": 1.6},
            {"text": "...đóng cả tấc đất luôn!", "start": 1.6, "end": 3.3},
            {"text": "Phủi sạch lớp bụi mờ,", "start": 3.5, "end": 5.0},
            {"text": "tiếng Anh gọi là: DUST!", "start": 5.0, "end": 7.1},
            {"text": "Lấy chổi dust bụi đi nào!", "start": 7.3, "end": 9.2},
            {"text": "(Đọc to theo tui: DUST!)", "start": 9.2, "end": 13.5},
            {"text": "Vừa phẩy một cái...", "start": 13.7, "end": 14.9},
            {"text": "...hắt xì mười cái suýt xỉu!", "start": 14.9, "end": 18.4}
        ]
    }
}

def get_drama_for_word(word_info):
    """
    Trả về kịch bản Micro-Drama 4 hồi cho từ vựng.
    Nếu từ nằm trong DRAMA_DATA được định nghĩa tỉ mỉ thì dùng trực tiếp.
    Nếu không, tự động sinh theo mẫu hài hước sinh động đúng nghĩa gloss_vi.
    """
    word = word_info['word'].lower()
    gloss = word_info.get('gloss_vi', 'từ vựng này')
    pos = word_info.get('pos', 'n')
    w_upper = word.upper()

    if word in DRAMA_DATA:
        d = DRAMA_DATA[word]
        return {
            "title": d["title"],
            "scenes": d["scenes"],
            "cues": d["cues"]
        }

    # Sinh kịch bản động theo ngữ nghĩa cụ thể
    if 'v' in pos:
        sc01 = f"Tình thế cấp bách ngay trước mắt rồi, phải hành động nhanh kẻo trễ!"
        sc02 = f"Hành động này trong tiếng Anh dùng ngay từ: {w_upper}!"
        sc03 = f"Cùng thực hiện liền nha: \"Let's {word}!\" Đọc to theo tui nè: {w_upper}!"
        sc04 = f"Vừa làm xong hớn hở quay lại thì thấy... mình làm nhầm việc của sếp!"
    elif 'adj' in pos:
        sc01 = f"Nhìn bộ dạng uể oải trong gương mà thấy thương cho bản thân ghê!"
        sc02 = f"Cảm giác này trong tiếng Anh diễn tả bằng từ: {w_upper}!"
        sc03 = f"Thấy tui đang {word} ghê chưa? Cùng nhắc lại theo tui nha: {w_upper}!"
        sc04 = f"Vừa dứt lời thì nghe tiếng chuông báo thức réo inh ỏi! Tỉnh ngủ luôn!"
    else:
        sc01 = f"Cả buổi sáng lục tung cả căn phòng tìm món đồ quan trọng này mà không thấy!"
        sc02 = f"Món đồ quen thuộc trong đời sống này, tiếng Anh gọi là: {w_upper}!"
        sc03 = f"Tìm giúp tui cái {word} này với! Cùng nói theo tui liền nè: {w_upper}!"
        sc04 = f"Trời đất ơi, hóa ra nó nằm ngay trong túi áo của mình nãy giờ!"

    cues = [
        {"text": sc01[:23], "start": 0.0, "end": 1.7},
        {"text": sc01[23:46] if len(sc01) > 23 else "Nhanh lên nào!", "start": 1.7, "end": 3.4},
        {"text": f"Tiếng Anh gọi là:", "start": 3.6, "end": 5.0},
        {"text": f"{w_upper}!", "start": 5.0, "end": 7.2},
        {"text": f"Nhớ từ này nha: {word}", "start": 7.4, "end": 9.2},
        {"text": f"(Cùng đọc to: {w_upper}!)", "start": 9.2, "end": 13.6},
        {"text": "Vừa làm xong quay lại...", "start": 13.8, "end": 15.0},
        {"text": sc04[:23], "start": 15.0, "end": 18.5}
    ]

    return {
        "title": gloss,
        "scenes": [
            (sc01, 0.20),
            (sc02, 0.20),
            (sc03, 1.20),
            (sc04, 0.40)
        ],
        "cues": cues
    }
