from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/drama-A1-all-20261001';data=json.loads((OUT/'narration-attempts/004-015/episodes.json').read_text())['episodes']
updates=[
('Tấm bảng chờ một cái tên','Một bác lớn tuổi ngập ngừng ở buổi học chữ sau ca làm; người dạy nhường chỗ để bác tự viết nét đầu và muốn quay lại.', 'Look at the ___.',[
'Tấm bảng trống, bác cứ đứng ngoài cửa. "Look at the board." Bác nhìn lên bảng nhé. Tôi kéo chiếc ghế đầu bàn ra, chờ bác ngồi.',
'Bác tới học chữ sau ca làm. Cuốn vở vẫn nguyên trang đầu. Tôi đưa phấn: "Write on the board." Bác viết lên bảng nhé. Bác cười, rồi lại rụt tay về.',
'Tôi viết tên bác ở góc bảng. Bác chỉ từng chữ, ngập ngừng hỏi chữ này nối thế nào. Tôi đứng sang bên, để bác có chỗ tự thử nét đầu tiên.',
'Bác cần nhìn lại dòng tên trên bảng. Bạn nói giúp tôi câu nhìn lên bảng bằng tiếng Anh nhé.',
'"Look at the board." Đúng rồi. Bác viết thêm một nét, rồi quay xuống hỏi: Mai còn học không cháu? Tôi gật đầu. Cuốn vở mới đã được đặt lại trong túi, ngay ngắn.']),
('Ngày đầu được phép hỏi','Người mới học việc giấu điều chưa hiểu rồi làm cháy mẻ bánh; người hướng dẫn khuyến khích hỏi để lần sau không phải giấu nữa.','I have a ___.',[
'Bánh đã khét, tôi vẫn chưa dám hỏi. "I have a question." Em có một câu hỏi. Chị Thảo tắt lò, kéo ghế lại cạnh tôi.',
'Ngày đầu học việc, tôi cứ gật đầu cho xong. Chị hỏi em hiểu chưa, tôi cũng gật. Giờ nhìn mẻ bánh cháy, tôi mới thú nhận mình không biết nút nào.',
'Chị đẩy tờ ghi chú sang: "Ask a question." Chưa rõ thì đặt câu hỏi nhé. Tôi hỏi lại từng bước. Mẻ bột mới còn nguyên, lần này tôi không vội.',
'Chị đang bận, mà tôi vẫn cần hỏi. Bạn nói giúp tôi câu em có một câu hỏi bằng tiếng Anh nhé.',
'"I have a question." Đúng rồi. Chị quay lại nghe. Cuối ca, tôi tự cất tờ ghi chú vào túi. Chị bảo ngày mai cứ hỏi tiếp, cửa tiệm vẫn mở.']),
('Câu trả lời mẹ đã chờ','Nhân vật lần lữa trả lời về nhà ăn cơm; chủ động đổi ca rồi nói rõ có, để mẹ thôi phải chờ một câu chưa thành.','My ___ is yes.',[
'Mẹ hỏi con có về ăn không. "I need an answer." Mẹ cần câu trả lời. Tôi đọc tin nhắn, rồi úp điện thoại xuống. Tôi còn chưa xin nghỉ được.',
'Tháng này, mẹ nhắc chuyện về nhà ba lần. Tôi cứ nói để con xem. Hôm nay, tôi nhìn lịch làm rồi tới hỏi anh quản lý, thay vì lại để mẹ chờ.',
'Anh đổi giúp tôi một ca. Tôi cầm điện thoại, tập câu sẽ nói: "My answer is yes." Câu trả lời của con là có. Lần này, tôi không định nói để con xem nữa.',
'Trước khi gọi mẹ, bạn nói giúp tôi câu câu trả lời của tôi là có bằng tiếng Anh nhé.',
'"My answer is yes." Đúng rồi. Mẹ bảo vậy mẹ đi chợ. Tôi mới nhớ, mình đã để một câu trả lời nhỏ kéo dài cả tháng.']),
('Chiếc áo lấy vào ngày mai','Ghé tiệm giặt lấy áo, nhân vật thấy người chú đau tay vẫn cố làm; ở lại giúp gấp đồ và hẹn quay lại.','I have a lot of ___.',[
'Chú giấu tay đau dưới chồng áo. "I have a lot of work." Chú còn nhiều công việc quá. Tôi đặt cặp xuống, kéo ghế vào cạnh bàn.',
'Tôi chỉ định ghé lấy chiếc áo đã giặt. Nhưng chú cứ đổi tay khi gấp đồ, rồi bảo cháu về đi kẻo muộn. Tôi nhìn chồng áo chưa xong, lấy ra chiếc đầu tiên.',
'Chú hỏi ở đây chán không. "I like this work." Cháu thích công việc này. Tôi chưa gấp đẹp như chú; chú chỉ lại mép áo, lần này chậm hơn.',
'Chú muốn nói mình còn nhiều công việc. Bạn giúp chú nói cả câu đó bằng tiếng Anh nhé.',
'"I have a lot of work." Đúng rồi. Hai chú cháu gấp xong chồng áo. Lúc tôi đứng dậy, chú hỏi mai cháu có ghé không. Tôi để chiếc áo của mình lại: Mai cháu lấy.']),
('Cửa kho ngày đầu','Sau mấy tháng chưa có việc, nhân vật đi nhầm lối vào ngày đầu; được người lao công chỉ đường, hỏi lại điều chưa biết và có lịch ca ngày mai.','This is my new ___.',[
'Ngày đầu, tôi đi nhầm cửa kho. "This is my new job." Đây là việc làm mới của tôi. Tôi nói với bác lao công đang quét trước cửa.',
'Tôi đã nghỉ ở nhà mấy tháng. Sáng nay nhận được ca đầu tiên, tôi kiểm tra túi tới ba lần. Bác chỉ tôi lối vào, rồi nhặt giúp chiếc thẻ vừa rơi.',
'Chị quản lý giao tôi xếp lại một kệ sách. "I need this job." Tôi cần việc làm này. Tôi hỏi chị chỗ nào chưa đúng, thay vì giả vờ đã biết.',
'Nếu muốn kể đây là việc làm mới của tôi, bạn sẽ nói câu nào bằng tiếng Anh?',
'"This is my new job." Đúng rồi. Hết ca, chị đưa tôi lịch ngày mai. Tôi ra cửa kho, đứng lại cảm ơn bác lúc sáng. Lần này, tôi đã biết đường về.']),
('Phong bì bị làm nhăn','Nhân vật tới giao bộ hồ sơ muộn, định quay về; hỏi tìm đúng văn phòng, gõ cửa và được mời ngồi.','Where is the ___?',[
'Cửa đóng rồi, tôi vẫn đứng ngoài. "Where is the office?" Văn phòng ở đâu ạ? Tôi ôm phong bì, hỏi bác bảo vệ ở chân cầu thang.',
'Trong phong bì là bộ hồ sơ còn thiếu của tôi. Tôi đến muộn vì quay về lấy tấm ảnh. Bác nhìn đôi giày ướt của tôi, chỉ lên cầu thang: "Go to the office." Cháu lên văn phòng nhé.',
'Đèn cuối hành lang còn sáng. Tôi đứng trước cửa, định đi về vì nghĩ đã hết giờ. Bên trong có tiếng ghế kéo. Tôi gõ nhẹ, giữ phong bì bằng cả hai tay.',
'Bạn đang tìm đúng văn phòng cần tới. Hỏi giúp tôi câu văn phòng ở đâu bằng tiếng Anh nhé.',
'"Where is the office?" Đúng rồi. Chị trong phòng mở cửa, nhận hồ sơ rồi mời tôi ngồi. Tôi đặt phong bì xuống, mới thấy góc giấy đã bị tay mình làm nhăn.']),
('Ghế ngoài sân xưởng','Người mới vào xưởng không dám buông việc khi tới giờ nghỉ; đồng nghiệp rủ ra sân và hai người bắt đầu trò chuyện.','Take a ___.',[
'Chuông nghỉ reo, anh vẫn cúi đầu. "We have a short break." Mình có giờ nghỉ ngắn rồi anh. Tôi đứng cạnh bàn máy, đợi anh ngẩng lên.',
'Anh mới vào xưởng, sợ làm chậm cả nhóm. Tôi từng ngồi đúng chỗ ấy, cũng không dám buông việc. Tôi đặt ly nước lên bàn, kéo chiếc ghế trống lại gần.',
'Anh nhìn chồng đồ chưa xong. "Take a break." Nghỉ giữa ca chút nhé. Tôi bảo mình ra ghế ngoài sân ngồi, lát quay vào làm tiếp. Anh tháo găng tay chậm chậm.',
'Nếu muốn rủ đồng nghiệp nghỉ giữa ca, bạn nói câu nào bằng tiếng Anh?',
'"Take a break." Đúng rồi. Anh đi cùng tôi ra sân. Lần đầu từ sáng, anh hỏi tên tôi. Hết giờ nghỉ, hai đứa quay vào, bàn máy vẫn ở đó.']),
('Dòng cuối trước khi gửi','Nhân vật viết email xin nghỉ để về gần mẹ, sợ làm người hướng dẫn thất vọng; bấm gửi và nhận một lời dặn bình thường đầy quan tâm.','Send the ___.',[
'Tôi viết xong, vẫn chưa bấm gửi. "Send the email." Gửi thư điện tử đi. Anh ngồi cạnh nhắc, còn tôi cứ đọc lại dòng cuối.',
'Thư này gửi cho người đã nhận tôi học việc. Tôi muốn nói mình sẽ nghỉ để về gần mẹ. Tôi đã tập nói trực tiếp nhiều lần, lần nào cũng im.',
'Tôi đọc lại từ đầu: "This email is for you." Thư điện tử này gửi cho anh. Dòng cuối chỉ có lời cảm ơn; tôi bỏ câu xin lỗi vừa gõ thêm.',
'Tôi vẫn cần một lời nhắc để bấm gửi. Bạn nói giúp anh câu gửi thư điện tử đi bằng tiếng Anh nhé.',
'"Send the email." Đúng rồi. Tôi bấm gửi. Chiều đó, người hướng dẫn trả lời: Về nhà rồi nhớ báo anh. Tôi mở tấm vé xe, lần đầu thấy lòng nhẹ hơn.']),
('Bản nháp trước cả phòng','Nhân vật mở nhầm tập tin trong buổi trình bày, được đồng nghiệp giúp tìm bản cuối và có thêm thời gian bắt đầu lại.','Where is the ___?',[
'Tôi mở nhầm bản nháp trước cả phòng. "Where is the file?" Tập tin đâu rồi? Tôi nhìn màn hình, mặt nóng bừng. Mọi người đang chờ bản cuối.',
'Cả nhóm đã sửa tập tin này tới tối qua. Sáng nay, tôi lại cầm nhầm máy tính cũ. Chị Lan kéo ghế sang, hỏi tôi đã lưu ở đâu, giọng rất nhỏ.',
'Tôi tìm thấy bản cuối trong thư mục chung. "I need this file." Tôi cần tập tin này. Chị bảo cứ mở lên, mọi người có thể đợi thêm một chút.',
'Nếu đang tìm tập tin cần mở, bạn hỏi câu tập tin ở đâu bằng tiếng Anh thế nào?',
'"Where is the file?" Đúng rồi. Tôi mở đúng bản, bắt đầu lại từ trang đầu. Chị Lan ngồi xuống. Tôi nói lời cảm ơn sau buổi họp, khi phòng chỉ còn hai người.']),
('Chỗ ngồi của người mới','Một người lao động mới im lặng đứng ngoài bữa ăn; đồng nghiệp nhận ra đóng góp, mời ngồi và bắt đầu nghe chuyện quê của chú.','He is a good ___.',[
'Chú đứng ngoài, chưa dám vào ăn. "He is a new worker." Chú ấy là người lao động mới. Tôi kéo chiếc ghế trống cạnh mình ra.',
'Sáng nay, chú chỉ im lặng làm việc. Tôi thấy chú nhặt lại những món đồ cả nhóm bỏ sót. Đến giờ ăn, chú vẫn đứng chờ ở cửa, tay ôm chiếc hộp cơm.',
'Anh cùng tổ hỏi chú làm có được không. "He is a good worker." Chú ấy là người lao động tốt. Tôi kể chuyện lúc sáng, rồi gọi chú ngồi cạnh mình.',
'Bạn muốn giới thiệu chú ấy là một người lao động tốt. Hãy nói giúp tôi câu đó bằng tiếng Anh nhé.',
'"He is a good worker." Đúng rồi. Chú mở hộp cơm, đẩy sang tôi một miếng trứng. Lần đầu, chú kể tên quê mình. Tiếng nói quanh bàn cũng nhỏ lại để nghe.']),
('Quả cam bác giữ lại','Sau mưa, người cháu cùng bác nông dân nhặt cam rơi; kết thúc buổi sáng bằng quả cam nhỏ bác nhớ cháu từng thích.','He is a ___.',[
'Bác đem sọt rỗng về, không nói gì. "He is a farmer." Bác ấy là một người nông dân. Tôi cất túi, đi theo bác ra vườn.',
'Đêm qua mưa lớn, vài cành cam đã gãy. Bác dựng lại chiếc ghế cũ rồi nhặt từng quả rơi. Tôi định hỏi bác có buồn không, cuối cùng chỉ đưa thêm một chiếc sọt.',
'"The farmer works hard." Bác nông dân làm việc chăm chỉ. Hôm nay, tôi ngồi cạnh bác nhặt quả suốt buổi sáng. Đến trưa, bác bảo thôi vào ăn, vườn vẫn còn ngày mai.',
'Bạn muốn giới thiệu bác ấy là một người nông dân. Hãy nói giúp tôi câu đó bằng tiếng Anh nhé.',
'"He is a farmer." Đúng rồi. Tôi khiêng chiếc sọt vào cùng bác. Bác giữ lại một quả cam nhỏ: Quả này con thích hồi bé. Tôi ngồi xuống, đợi bác bóc.']),
('Phần hỏng không bị giấu','Một kỹ sư mang mô hình tới giới thiệu nghề cho trẻ nhỏ; khi một chân đỡ lệch, chị sửa cùng các em thay vì giấu lỗi.','She is an ___.',[
'Mô hình đứng yên, không ai nói gì. "She is an engineer." Chị ấy là một kỹ sư. Tôi đứng cạnh chị, nhìn cây cầu nhỏ trên bàn.',
'Chị làm mô hình để giới thiệu việc của mình cho các em nhỏ. Đến lúc thử, một chân đỡ bị lệch. Có em hỏi cầu thật cũng vậy sao. Chị ngồi xuống, sửa từng phần.',
'"Call the engineer." Gọi kỹ sư nhé. Tôi nhắc một em khi mô hình lại nghiêng. Chị quay lại xem, không giấu phần hỏng. Chị bảo muốn làm được phải thử rồi sửa.',
'Nếu cần giới thiệu chị ấy là một kỹ sư, bạn nói câu nào bằng tiếng Anh?',
'"She is an engineer." Đúng rồi. Mô hình đứng được. Em nhỏ vừa hỏi lúc nãy xin thử lại, chị nhường chỗ. Tôi nhìn hai người làm cùng nhau, rồi cất tờ giới thiệu đã in.'])]
for ep,(title,plot,stem,narrs) in zip(data,updates):
 ep.update(title=title,plot_vi=plot,learner_outcome_vi='Nhận ra đúng nghĩa trong chuyện và nói lại một câu cần dùng.',editorial_review='Reviewed and rewritten by primary agent; narration frozen before anchors.')
 for i,(s,narr) in enumerate(zip(ep['scenes'],narrs)):
  s.update(narration=narr,practice_pause_seconds=4 if i==3 else 0,title_vi=['Chi tiết đầu chuyện','Điều cần hiểu','Hành động làm đổi chuyện','Lời người xem giúp nói','Kết quả'][i],purpose_en=['Open on a specific visible need or contradiction and an early English utterance.','Show the relationship, resistance or prior choice that gives the target meaning a purpose.','Use the second English model to change the same situation through a meaningful action or decision.','Invite one manageable full-sentence retrieval for the character\'s need; wait quietly before feedback.','Provide the correct answer, then show the local consequence and ordinary emotional payoff.'][i])
  s['character_ids']=['CH01','CH02']
 ep['scenes'][3]['stem']=stem
 ep['characters']=[ep['characters'][0],{'id':'CH02','name_vi':ep['characters'][1]['name_vi'],'appearance_en':'Minimal ink stick figure with a round white face, solid dark oval eyes, simple hair silhouette and ordinary proportions. Express emotion through posture and a modest facial change; no realistic muscles or fingers.','outfit_en':'Exactly one plain mustard-yellow short-sleeve top and minimal stick limbs; use only the small accessory needed for this role.'}]
 # All visual plans are separately rewritten below; old technical/sense-incompatible instructions are not reused.
 (OUT/'narration-frozen'/f"{ep['job']}.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
print('Rewritten twelve narrations; visual rewrite required before anchors')
