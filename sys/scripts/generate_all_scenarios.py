#!/usr/bin/env python3
"""
Trình tạo kịch bản 50 Micro-Drama sinh động, hài hước, sát nghĩa từ điển cho Lô 50 video.
"""
import json
from pathlib import Path

# Định nghĩa chi tiết cốt truyện riêng biệt cho từng từ
SCENARIOS_MAP = {
    # 32-35: Di chuyển
    "leave": ("Còn đúng năm phút nữa hết giờ làm mà sếp chuẩn bị giao thêm việc!", "Phải chuồn lẹ khỏi công ty thôi, tiếng Anh gọi là: LEAVE!", "Mau mau leave kẻo bị bắt ở lại tăng ca! Nhắc lại theo tui nha: LEAVE!", "Vừa bước chân ra khỏi cửa thì chạm mặt ngay giám đốc bước vào! Đứng hình!", "rời đi"),
    "arrive": ("Phóng xe bạt mạng giữa trưa nắng để kịp giờ phỏng vấn xin việc!", "Cuối cùng cũng đã đến nơi đúng giờ hẹn, tiếng Anh là: ARRIVE!", "Mừng quá tui vừa arrive rồi nè! Cùng đọc to theo tui nha: ARRIVE!", "Bác bảo vệ cười tươi bảo: công ty dọn trụ sở sang quận khác từ hôm qua rồi cháu!", "đến nơi"),
    "return": ("Đi công tác xa nhà cả tháng trời, chỉ thèm cảm giác bước vào nhà mình!", "Hành động quay trở về chốn thân quen, tiếng Anh gọi là: RETURN!", "Hôm nay tui được return về nhà rồi nè! Nói theo tui liền nha: RETURN!", "Vừa tra chìa vào ổ khóa thì thấy người yêu cũ đang ngồi ăn cơm với mẹ mình!", "quay về"),
    "errand": ("Đang trùm chăn xem phim thì mẹ réo chạy đi mua hành, tỏi, nước mắm gấp!", "Mấy cái việc vặt vãnh phải xách xe chạy ra ngoài, tiếng Anh gọi là: ERRAND!", "Ra ngoài làm mấy cái errand cho mẹ nè! Cùng nhắc lại theo tui: ERRAND!", "Chạy xe năm cây số mua cho đủ đồ, về tới nơi mẹ bảo: thôi mẹ nấu xong luôn rồi!", "việc vặt ra ngoài"),

    # 36-41: Dọn dẹp nhà cửa
    "chore": ("Sáng chủ nhật đẹp trời mà mở mắt ra thấy nguyên một núi việc không tên chờ sẵn!", "Những công việc nhà lặt vặt gây ngán ngẩm này, tiếng Anh là: CHORE!", "Phải làm cho xong đống chore này mới được đi chơi! Đọc to theo tui: CHORE!", "Vừa lau dọn xong xuôi thì đứa em út làm đổ nguyên tô canh ra sàn! Khóc thét!", "việc nhà lặt vặt"),
    "housework": ("Lúc ở với mẹ thì sướng như vua, giờ ra ở riêng mới biết mùi cực khổ!", "Toàn bộ công việc nội trợ, quét dọn trong nhà, tiếng Anh gọi là: HOUSEWORK!", "Cuối tuần ở nhà cày housework mệt xỉu luôn! Nhại lại theo tui nè: HOUSEWORK!", "Dọn dẹp hì hục từ sáng tới tối, nhìn lại đồng hồ thấy hết luôn ngày nghỉ!", "việc nhà"),
    "tidy": ("Mẹ gọi điện báo mười phút nữa mẹ tới kiểm tra phòng trọ bất ngờ!", "Phải gom đồ đạc xếp dọn cho ngăn nắp liền tay, tiếng Anh là: TIDY!", "Mau mau tidy phòng đón mẹ lên chơi nào! Cùng đọc theo tui nha: TIDY!", "Nhét hết đồ dơ vô tủ quần áo rồi đóng sập cửa, ai ngờ tủ bung bản lề rớt ụp xuống!", "dọn cho gọn"),
    "sweep": ("Lỡ tay làm đổ nguyên lọ muối tiêu rơi vãi tung tóe khắp sàn gạch!", "Phải lấy cây chổi ra quét gom bụi rác lại, tiếng Anh gọi là: SWEEP!", "Cầm chổi lên sweep sạch sẽ sàn nhà giùm tui nha! Nói theo tui liền: SWEEP!", "Vừa quét được một đống rác thì con mèo phóng qua làm tung tóe lại từ đầu!", "quét nhà"),
    "mop": ("Trời mưa nồm ẩm sàn nhà nhớp nháp trơn như sân trượt băng nghệ thuật!", "Phải nhúng cây lau nhà vô xô nước rồi lau sạch, tiếng Anh là: MOP!", "Lấy cây lau ra mop nhà cho khô ráo nào! Cùng nhắc lại theo tui: MOP!", "Vừa lau xong quay lưng bước đi thì trượt chân xoạc một đường tiếp đất bằng mông!", "lau nhà"),
    "dust": ("Mấy tháng không dọn kệ sách mà bụi bám dày cộm đóng cả tấc đất!", "Lấy khăn lông đi phủi sạch lớp bụi mờ này, tiếng Anh gọi là: DUST!", "Mau lấy chổi lông gà dust bụi bàn học đi nha! Đọc to theo tui nè: DUST!", "Vừa phẩy một cái bụi bay mù mịt làm hắt xì hơi liên tục mười cái suýt ngất!", "phủi bụi"),

    # 42-49: Giặt giũ & Quần áo
    "vacuum": ("Nhà nuôi ba con mèo lông rụng ngập tràn từ sofa cho tới thảm trải sàn!", "Phải lôi ngay máy hút bụi ra dọn dẹp cấp tốc, tiếng Anh là: VACUUM!", "Bật máy lên vacuum cho sạch lông mèo nào! Nhại lại theo tui: VACUUM!", "Hút hăng say quá cuốn luôn cả chiếc tất rách yêu thích của ông bố vào máy nghẹt cứng!", "hút bụi"),
    "laundry": ("Quần áo bẩn tích tụ cả tuần chất đống cao ngất ngưởng như ngọn núi Phú Sĩ!", "Đống đồ bẩn cần phải đem đi giặt giũ, tiếng Anh gọi là: LAUNDRY!", "Đi gom đồ làm mẻ laundry khổng lồ thôi! Cùng đọc to theo tui nè: LAUNDRY!", "Bê thau đồ đi ngang hành lang thì vấp bậc tam cấp, quần áo bay lả tả khắp sân!", "đồ giặt"),
    "wash": ("Chiếc áo thun trắng yêu thích vừa bị dính trúng một giọt cà phê đen thui!", "Phải đem đi chà rửa giặt giũ bằng xà phòng liền tay, tiếng Anh là: WASH!", "Lấy xà phòng ra wash sạch vết bẩn này đi! Nói theo tui nha: WASH!", "Chà mạnh tay quá làm thủng luôn một lỗ to đùng ngay trước ngực! Xong phim!", "giặt rửa"),
    "rinse": ("Giặt xà phòng nổi bọt trắng xóa bám đầy từ trên xuống dưới!", "Phải xả lại nhiều lần bằng nước sạch cho hết xà phòng, tiếng Anh là: RINSE!", "Mở vòi nước mạnh lên để rinse cho sạch bọt nha! Đọc theo tui nè: RINSE!", "Vừa cúi đầu xả nước thì vòi nước bị tuột bắn thẳng một tia nước vào giữa mặt!", "xả nước"),
    "dry": ("Trời mưa bão dầm dề cả tuần quần áo giặt xong phơi mãi không chịu khô!", "Hành động làm khô quần áo bằng máy hoặc sấy, tiếng Anh gọi là: DRY!", "Bật quạt sấy lên để dry quần áo cho mau khô nào! Cùng nhắc lại: DRY!", "Lấy máy sấy tóc sấy nhiệt tình quá làm quéo luôn cái mác áo hàng hiệu!", "làm khô"),
    "iron": ("Sáng nay có buổi thuyết trình quan trọng mà chiếc áo sơ mi nhăn nhúm như bánh tráng!", "Phải cắm bàn ủi lên ủi cho thẳng thớm phẳng phiu, tiếng Anh là: IRON!", "Cầm bàn ủi lên iron cho cái áo thẳng thớm liền! Đọc to theo tui: IRON!", "Đang ủi mải mê bấm điện thoại, quay lại thấy bàn ủi in nguyên hình tam giác đen thui!", "ủi đồ"),
    "fold": ("Quần áo sau khi phơi khô gom vô giường nằm thành một bãi chiến trường!", "Phải ngồi xếp lại ngay ngắn bỏ vô tủ, tiếng Anh gọi là: FOLD!", "Ngồi ngay ngắn lại fold quần áo cho gọn gàng nha! Nhắc lại theo tui nè: FOLD!", "Gấp được ba cái nản quá, gom nguyên đống nhét đại vô góc tủ rồi đóng cửa lại!", "gấp quần áo"),
    "hang": ("Áo khoác xịn mới mua về không thể vứt lung tung trên ghế sofa được!", "Phải lấy cái móc treo nó lên giá đàng hoàng, tiếng Anh gọi là: HANG!", "Lấy móc áo ra hang cái áo khoác lên giùm tui nha! Nói theo tui liền: HANG!", "Móc lên chưa kịp quay đi thì chiếc giá treo quá tải sập rớt ầm xuống sàn!", "treo lên"),

    # 50-52: Rác & Tái chế
    "trash": ("Nấu ăn xong nhìn quanh gian bếp ngập tràn rác vỏ rau củ bốc mùi chua lét!", "Đống rác thải sinh hoạt bừa bãi này, tiếng Anh gọi là: TRASH!", "Gom hết đống trash này đem đi vứt giùm tui với! Cùng đọc to: TRASH!", "Vừa nhấc bọc rác lên thì bọc bị rách toạc đáy, nước rác rỉ tong tỏng ra sàn nhà!", "rác thải"),
    "bin": ("Cầm bọc rác trên tay đi lòng vòng khắp công viên tìm chỗ bỏ mà không thấy!", "Chiếc thùng chứa rác công cộng quen thuộc, tiếng Anh gọi là: BIN!", "Tìm chiếc bin gần nhất để vứt rác văn minh nha! Nhắc lại theo tui: BIN!", "Đứng từ xa ném bọc rác điệu nghệ như bóng rổ, ai ngờ trúng ngay đầu ông bảo vệ!", "thùng rác"),
    "recycle": ("Uống trà sữa xong gom được cả chục cái ly nhựa chất thành chồng trong góc phòng!", "Hành động tái chế đồ nhựa để bảo vệ môi trường, tiếng Anh là: RECYCLE!", "Đem đống chai nhựa này đi recycle cho có ích nha! Đọc to theo tui: RECYCLE!", "Cặm cụi ngồi cắt dán làm chậu trồng cây, tưới nước vô nước xì lung tung ra bàn!", "tái chế"),

    # 53-62: Nghỉ ngơi & Trạng thái thể chất
    "nap": ("Ăn trưa no nê xong hai mí mắt nặng trĩu díp lại không thể nào mở ra nổi!", "Làm một giấc ngủ trưa ngắn mười lăm phút lấy lại sức, tiếng Anh là: NAP!", "Chợp mắt làm một giấc nap nhẹ nhàng thôi nào! Cùng nói theo tui: NAP!", "Tính chợp mắt mười lăm phút, mở mắt ra thấy trời tối thui bảy giờ tối luôn rồi!", "ngủ trưa ngắn"),
    "rest": ("Chạy bộ hùng hục ngoài công viên mệt đứt hơi tim đập thình thịch như đánh trống!", "Phải ngồi xuống ghế đá nghỉ ngơi lấy lại hơi sức, tiếng Anh là: REST!", "Ngồi xuống đây rest một chút cho khỏe người nha! Đọc theo tui nè: REST!", "Vừa ngồi nghỉ nhắm mắt thư giãn thì bầy chim bồ câu bay qua tặng ngay một bãi lên đầu!", "nghỉ ngơi"),
    "relax": ("Cả tuần cày cuốc bù đầu tóc rối với mớ báo cáo và chỉ số công việc căng thẳng!", "Cuối tuần phải thả lỏng đầu óc thư giãn tuyệt đối, tiếng Anh là: RELAX!", "Mở nhạc êm dịu lên để relax tâm hồn nào cả nhà! Nhắc lại theo tui: RELAX!", "Đang đắp mặt nạ nằm thư giãn thì chuông điện thoại réo: sếp yêu cầu sửa file gấp!", "thư giãn"),
    "bedtime": ("Mười một giờ đêm rồi mà mấy đứa nhỏ vẫn chạy nhảy hò hét ầm ĩ khắp nhà!", "Đã tới giờ phải lên giường đi ngủ rồi các con ơi, tiếng Anh là: BEDTIME!", "Đến giờ bedtime rồi mau mau đi ngủ thôi nào! Cùng đọc to: BEDTIME!", "Dỗ con ngủ xong xuôi quay qua giường mình thì thấy bố mẹ đã ngủ say như chết từ bao giờ!", "giờ đi ngủ"),
    "asleep": ("Đặt lưng xuống giường trùm chăn ấm áp, chưa đầy hai phút đã ngáy khò khò!", "Trạng thái đang chìm sâu vào giấc ngủ say sưa, tiếng Anh là: ASLEEP!", "Bé cưng nhà mình đã ngủ say asleep rồi nha! Nói theo tui liền nè: ASLEEP!", "Vừa chìm vào giấc ngủ thì nghe tiếng mèo gào đập cửa làm giật bắn tim thức trắng!", "đang ngủ say"),
    "awake": ("Nằm trằn trọc đếm cừu từ một giờ đến ba giờ sáng mà hai mắt vẫn mở thao láo!", "Tình trạng vẫn đang hoàn toàn tỉnh táo chưa ngủ được, tiếng Anh là: AWAKE!", "Nửa đêm rồi mà tui vẫn còn awake thao láo đây nè! Nhắc lại theo tui: AWAKE!", "Bật dậy tính pha trà sữa uống thì làm rơi cái ly thủy tinh bể tan tành cả nhà thức dậy!", "đang thức tỉnh"),
    "sleepy": ("Ngồi trong tiết học ngữ pháp buổi chiều buồn ngủ rũ rượi đầu gật gà gật gù!", "Cảm giác mí mắt díp lại ngáp ngắn ngáp dài thèm ngủ, tiếng Anh là: SLEEPY!", "Trời ơi sao mà tui thấy sleepy dữ thần vậy nè! Cùng đọc to theo tui: SLEEPY!", "Đang gật gù thì đầu rơi tự do đập đánh bộp xuống mặt bàn gỗ, đau điếng người!", "buồn ngủ"),
    "tired": ("Sau tám tiếng bốc vác dọn kho mệt lả người chân tay rã rời không nhấc nổi!", "Cảm giác mệt mỏi kiệt sức quen thuộc của dân lao động, tiếng Anh là: TIRED!", "Hôm nay tui tired quá rồi không làm nổi gì nữa đâu! Đọc to theo tui: TIRED!", "Tính lết về giường nằm thì thấy đứa bạn cùng phòng nhờ chở đi ăn ốc đêm! Từ chối không kịp!", "mệt mỏi"),
    "exhausted": ("Chạy marathon bốn mươi hai cây số về tới đích thở không ra hơi chân run lẩy bẩy!", "Mức độ kiệt sức hoàn toàn cạn kiệt năng lượng, tiếng Anh là: EXHAUSTED!", "Chạy xong kiệt sức exhausted muốn xỉu ngang luôn á! Nhại lại theo tui: EXHAUSTED!", "Vừa lết được tới vạch đích tính tạo dáng chụp hình thì trượt chân ngã sấp mặt xuống cỏ!", "kiệt sức hoàn toàn"),
    "refreshed": ("Sau một giấc ngủ đẫm mười tiếng kèm ly cà phê sữa đá mát lạnh sảng khoái!", "Cảm giác tràn đầy năng lượng tươi mới sảng khoái trở lại, tiếng Anh là: REFRESHED!", "Uống ngụm cà phê thấy người refreshed hẳn luôn nè! Cùng nói theo tui: REFRESHED!", "Hăng hái bước chân ra đường thì trời đổ cơn mưa rào làm ướt sũng từ đầu tới chân!", "sảng khoái khỏe khoắn"),

    # 63-70: Các mốc thời gian trong ngày
    "morning": ("Chuông báo thức reo inh ỏi lúc sáu giờ khi ánh nắng ban mai chiếu qua khe cửa!", "Khoảng thời gian bắt đầu một ngày mới đầy năng lượng, tiếng Anh là: MORNING!", "Chúc cả nhà một buổi morning tràn đầy năng lượng nha! Đọc to theo tui: MORNING!", "Vừa vươn vai bước xuống giường thì giẫm ngay trúng đuôi con mèo, bị nó cào cho một phát!", "buổi sáng"),
    "afternoon": ("Hai giờ chiều nắng chang chang gay gắt đường phố hầm hập như cái lò lửa!", "Khoảng thời gian buổi chiều oi ả buồn ngủ nhất ngày, tiếng Anh là: AFTERNOON!", "Nắng gắt buổi afternoon ra đường nhớ mang áo khoác nha! Cùng nhắc lại: AFTERNOON!", "Vừa bước ra đường quên mang kính râm, chói mắt đâm sầm vô gốc cây ven đường!", "buổi chiều"),
    "evening": ("Sáu giờ chiều tan tầm hoàng hôn buông xuống dòng người tấp nập kéo nhau về nhà!", "Khoảng thời gian chập tối ăn cơm quây quần gia đình, tiếng Anh là: EVENING!", "Tận hưởng một buổi evening ấm cúng bên gia đình nào! Nhại lại theo tui: EVENING!", "Về tới cửa nhà mừng rỡ tính ăn cơm thì phát hiện quên chìa khóa trong cốp xe!", "buổi tối sớm"),
    "night": ("Mười một giờ đêm đèn đường tắt dần cả thành phố chìm vào bóng tối tĩnh lặng!", "Khoảng thời gian ban đêm yên tĩnh để nghỉ ngơi hồi phục, tiếng Anh là: NIGHT!", "Chúc cả nhà có một đêm night thật ngon giấc nha! Nói theo tui liền nè: NIGHT!", "Vừa nhắm mắt lại thì bầy muỗi đói kéo tới vo ve bên tai như một dàn hợp xướng!", "ban đêm"),
    "midnight": ("Đúng mười hai giờ đêm chuông đồng hồ điểm tích tắc trong căn phòng tối om!", "Thời khắc nửa đêm chuyển giao giữa hai ngày, tiếng Anh gọi là: MIDNIGHT!", "Nửa đêm midnight rồi mà chưa chịu ngủ là già sớm nha! Cùng đọc to: MIDNIGHT!", "Đang lén mò xuống bếp kiếm đồ ăn khuya thì vô tình đụng rớt cái nắp vung kêu keng vang dội!", "nửa đêm"),
    "noon": ("Đúng mười hai giờ trưa mặt trời đứng bóng chiếu thẳng đứng xuống đỉnh đầu!", "Thời điểm giữa trưa tròn bóng nóng bức nhất, tiếng Anh gọi là: NOON!", "Đúng mười hai giờ trưa noon đói cồn cào cả bụng rồi! Nhắc lại theo tui nha: NOON!", "Chạy ra mua cơm trưa chen chúc đứng xếp hàng nửa tiếng đồng hồ thì quán hết sạch đồ ăn!", "giữa trưa"),
    "dawn": ("Năm giờ sáng trời hửng sáng le lói những tia nắng đầu tiên nơi chân trời!", "Khoảng thời gian rạng đông sáng sớm tinh mơ bình yên, tiếng Anh gọi là: DAWN!", "Dậy sớm ngắm cảnh rạng đông dawn đẹp tuyệt vời nè! Đọc to theo tui nha: DAWN!", "Dậy sớm cho cố vô ngắm được hai phút gió lạnh thổi buốt thấu xương hắt xì sụt sùi!", "rạng đông"),
    "dusk": ("Mặt trời lặn dần bóng tối chầm chậm buông xuống cảnh vật mờ ảo chập choạng!", "Khoảng thời gian chạng vạng hoàng hôn bảng lảng, tiếng Anh gọi là: DUSK!", "Khung cảnh lúc hoàng hôn dusk nhìn lãng mạn ghê chưa! Cùng nói theo tui: DUSK!", "Đang đứng ngắm hoàng hôn ngơ ngẩn thì bị trượt chân tụt xuống mương nước đen thui!", "chạng vạng"),

    # 71-77: Chu kỳ & Lịch trình
    "daily": ("Đánh răng rửa mặt lướt điện thoại là những thói quen ngày nào cũng làm!", "Những hoạt động diễn ra đều đặn mỗi ngày, tiếng Anh gọi là: DAILY!", "Tạo lập thói quen tốt daily mỗi ngày nha cả nhà! Nhắc lại theo tui nè: DAILY!", "Lên danh sách việc cần làm cho cố vô xong cuối ngày gạch được đúng dòng đi ngủ!", "hằng ngày"),
    "weekly": ("Cứ đến tối thứ sáu là cả hội bạn lại rủ nhau đi ăn lẩu một lần cho đã!", "Lịch trình diễn ra định kỳ mỗi tuần một lần, tiếng Anh gọi là: WEEKLY!", "Họp mặt tổng kết weekly cuối tuần thôi bà con ơi! Cùng đọc to theo tui: WEEKLY!", "Rủ nhau đi ăn lẩu tưng bừng tới lúc tính tiền đứa nào cũng vờ bấm điện thoại trốn trả!", "hằng tuần"),
    "monthly": ("Cứ đến ngày mười đầu tháng là tin nhắn ngân hàng ting ting báo trừ một đống tiền!", "Những khoản tiền hoặc sự kiện diễn ra hằng tháng, tiếng Anh là: MONTHLY!", "Tới ngày đóng tiền trọ monthly rồi buồn ghê chưa! Đọc to theo tui nha: MONTHLY!", "Vừa nhận lương ting ting được năm phút thì đóng tiền trọ tiền điện hết sạch tiền lương!", "hằng tháng"),
    "weekday": ("Từ thứ hai đến thứ sáu sáng nào cũng dậy sớm chen chúc kẹt xe đi làm sấp mặt!", "Những ngày trong tuần bận rộn với công việc, tiếng Anh gọi là: WEEKDAY!", "Cố gắng cày cuốc qua mấy ngày weekday này nha! Nói theo tui liền nè: WEEKDAY!", "Cứ ngỡ hôm nay là thứ sáu chuẩn bị đi quẩy, ai ngờ xem lại lịch mới là thứ ba!", "ngày trong tuần"),
    "weekend": ("Cả tuần mong ngóng chỉ ước thứ bảy chủ nhật mau tới để được ngủ nướng đã đời!", "Hai ngày cuối tuần quý giá được nghỉ ngơi xả hơi, tiếng Anh là: WEEKEND!", "Cuối tuần weekend xõa hết mình thôi bà con ơi! Cùng nhắc lại theo tui: WEEKEND!", "Sáng thứ bảy tính ngủ tới trưa thì hàng xóm vác máy khoan bê tông ra sửa nhà đục ầm ầm!", "cuối tuần"),
    "holiday": ("Cả năm làm việc vất vả chỉ mong tới mấy ngày lễ lớn được xách ba lô lên đi du lịch!", "Kỳ nghỉ lễ chính thức được nghỉ học nghỉ làm, tiếng Anh gọi là: HOLIDAY!", "Chuẩn bị đi nghỉ lễ holiday thật hoành tráng nào! Đọc to theo tui nè: HOLIDAY!", "Ra tới sân bay hớn hở tính bay thì hãng thông báo hủy chuyến vì bão lớn! Xong luôn!", "kỳ nghỉ lễ"),
    "day off": ("Làm việc liên tục ba mươi ngày cuối cùng cũng được sếp duyệt cho nghỉ một ngày trọn vẹn!", "Một ngày được nghỉ phép không vướng bận công việc, tiếng Anh là: DAY OFF!", "Hôm nay tui được hưởng trọn vẹn một day off rồi nè! Nhại lại theo tui: DAY OFF!", "Vừa tắt chuông báo thức nhắm mắt ngủ thì sếp gọi điện nhờ lên công ty trực hộ!", "ngày được nghỉ"),

    # 78-81: Cửa nẻo & An ninh
    "lock": ("Chuẩn bị đi chơi xa cả tuần phải kiểm tra cổng ngõ cẩn thận đề phòng trộm cắp!", "Hành động khóa then gài chốt cửa cẩn thận, tiếng Anh gọi là: LOCK!", "Nhớ kiểm tra và lock cửa kỹ càng trước khi đi nha! Cùng đọc to: LOCK!", "Khóa cửa ba lớp khóa cẩn thận xong xuôi bước ra ngõ mới nhớ để quên điện thoại trong nhà!", "khóa cửa"),
    "unlock": ("Đi làm về mệt mỏi đứng trước cửa nhà lục tung túi xách tìm chìa mở cửa!", "Hành động tra chìa khóa vào mở khóa cửa, tiếng Anh gọi là: UNLOCK!", "Mau mau lấy chìa ra unlock cửa vô nhà nghỉ ngơi nào! Nói theo tui: UNLOCK!", "Cắm chìa vô vặn thật mạnh một cái thì chìa khóa bị gãy làm đôi kẹt cứng trong ổ!", "mở khóa"),
    "key": ("Đứng trước cửa phòng trọ lúc mười hai giờ đêm mò khắp túi quần không thấy chìa đâu!", "Vật kim loại nhỏ bé quan trọng dùng để mở cửa, tiếng Anh gọi là: KEY!", "Tìm giúp tui cái chìa khóa key quan trọng này với! Cùng đọc to nè: KEY!", "Mò mẫm tìm kiếm khắp nơi hoảng loạn cả buổi, nhìn lại thấy chìa khóa đang cắm sẵn trên ổ!", "chìa khóa"),
    "doorbell": ("Đang ngồi xem phim kinh dị nửa đêm một mình thì ngoài cổng vang lên tiếng chuông reo!", "Chiếc chuông gắn ngoài cửa để khách bấm gọi chủ nhà, tiếng Anh là: DOORBELL!", "Ai đang bấm chuông doorbell ngoài cổng giờ này vậy? Nhắc lại theo tui: DOORBELL!", "Rón rén bước ra mở cửa nhìn qua khe thì thấy một con mèo hoang đang lấy chân cào cái chuông!", "chuông cửa")
}

def generate_script_data():
    bank_file = Path(__file__).resolve().parent.parent / 'vocab/bank.jsonl'
    lines = [json.loads(l) for l in bank_file.read_text().splitlines() if l.strip()]
    selected = lines[31:81] # Từ 32 đến 81

    full_items = []
    for idx_offset, it in enumerate(selected):
        idx = 32 + idx_offset
        word = it['word'].lower()
        eid = it['id']
        gloss = it.get('gloss_vi', '')
        pos = it.get('pos', 'n')

        if word in SCENARIOS_MAP:
            s1, s2, s3, s4, custom_gloss = SCENARIOS_MAP[word]
            title = custom_gloss
        else:
            w_up = word.upper()
            s1 = f"Tình thế cấp bách ngay trước mắt rồi, phải hành động nhanh kẻo trễ!"
            s2 = f"Hành động này trong tiếng Anh dùng ngay từ: {w_up}!"
            s3 = f"Cùng thực hiện liền nha: \"Let's {word}!\" Đọc to theo tui nè: {w_up}!"
            s4 = f"Vừa làm xong hớn hở quay lại thì thấy... mình làm nhầm việc của sếp!"
            title = gloss

        w_upper = word.upper()
        # Tạo 8 cues ngắn < 24 ký tự
        cues = [
            {"text": s1[:23].strip(), "start": 0.0, "end": 1.7},
            {"text": s1[23:46].strip() if len(s1) > 23 else "Nhanh lên nào!", "start": 1.7, "end": 3.4},
            {"text": "Tiếng Anh dùng từ:", "start": 3.6, "end": 5.0},
            {"text": f"{w_upper}!", "start": 5.0, "end": 7.2},
            {"text": f"Nhớ từ này nha: {word}", "start": 7.4, "end": 9.2},
            {"text": f"(Cùng đọc to: {w_upper}!)", "start": 9.2, "end": 13.6},
            {"text": "Vừa xong quay lại...", "start": 13.8, "end": 15.0},
            {"text": s4[:23].strip(), "start": 15.0, "end": 18.5}
        ]

        # Kiểm tra cues không có newline và dưới 24 ký tự
        for c in cues:
            c['text'] = c['text'].replace('\n', ' ').strip()
            if len(c['text']) > 24:
                c['text'] = c['text'][:24]

        item = {
            "index": idx,
            "id": eid,
            "word": word,
            "title": title,
            "scenes": [
                (s1, 0.20),
                (s2, 0.20),
                (s3, 1.20),
                (s4, 0.40)
            ],
            "cues": cues
        }
        full_items.append(item)

    out_file = Path(__file__).resolve().parent / 'drama_scenarios_50.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(full_items, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã tạo thành công {len(full_items)} kịch bản Micro-Drama chi tiết tại {out_file}!")

if __name__ == '__main__':
    generate_script_data()
