from pathlib import Path
p=Path(__file__).parent
f=p/'241-250.txt';s=f.read_text();start=s.index('@248|');end=s.index('@249|');s=s[:start]+'''@248|Lời mời đang chờ hồi đáp|Dùng answer như danh từ chỉ câu trả lời cho lời mời.|Bàn ăn, hai người xem tin nhắn hẹn bạn.|Gửi lời mời → chờ câu trả lời → nhận đồng ý → thêm chỗ.
Ghế thứ ba để trống hay bày thêm đĩa? Answer là câu trả lời. Bạn đã mời một người bạn tới ăn cùng, nhưng chưa biết người ấy có tới không; câu trả lời sẽ quyết định chỗ còn lại trên bàn.|Mascot and friend look at empty third place setting while checking invitation message on phone.
Bạn hỏi: "Do you have an answer?" Bạn đã có câu trả lời chưa? An answer là một câu trả lời cho điều vừa hỏi; ở đây mình đang chờ hồi đáp cho lời mời ăn cùng.|Mascot asks friend who checks generic incoming-message area on phone.
Tin nhắn tới, người bạn báo: "The answer is yes." Câu trả lời là có. Người được mời đồng ý tới; bạn lấy thêm chiếc đĩa đặt vào chỗ đang để trống, không cần đoán nữa.|Friend shows affirmative response symbol while mascot brings extra plate to empty place.
Người được mời đã đồng ý tới. Bạn nói "The answer is yes." hay "The answer is no." để báo tin? Chọn theo điều vừa xảy ra rồi đọc câu ấy.|Third place setting awaits plate; two answer sentences shown without emphasis.
"The answer is yes." Câu trả lời là có. Bạn bày xong chỗ thứ ba, người bạn đi mở cửa. Một câu trả lời đã giúp cả bàn biết cần chuẩn bị thêm gì.|Three complete place settings on table; mascot places last cup as friend opens door for arriving adult.
''' + s[end:]
s=s.replace('Bạn cần mượn vở của người ngồi cạnh. Hoàn thành câu "Can I use your...?" rồi nói cả lời hỏi. Nhớ vật có nhiều trang đóng thành cuốn nhé.','Bạn có bút nhưng thiếu chỗ ghi bài. Trong vở ghi và cây thước, vật nào là notebook? Chọn vật phù hợp rồi hỏi "Can I use your notebook?".')
s=s.replace('Hold the school desk and unfinished request, without the answer label.','Show notebook and ruler as two unlabelled objects beside mascot; full request may be visible for supported speaking.')
s=s.replace('Từ cần điền là notebook. Bạn trả vở','Notebook là cuốn vở ghi. Bạn trả vở')
s=s.replace('Cần xin cục tẩy, bạn hoàn thành "Can I have an...?" bằng từ gì? Nói trọn câu, giữ an trước tên đồ vật vừa học.','Bạn cần xin cục tẩy. Chọn "a eraser" hay "an eraser", rồi dùng lựa chọn đó trong "Can I have... ?". Nói câu xin lịch sự thành tiếng nhé.')
s=s.replace('Hold intact drawing and question stem without showing the answer word.','Show two text options a eraser and an eraser equally, with intact drawing and mascot; do not mark an answer.')
s=s.replace('Bạn cần kẻ một đường nữa. Hỏi mượn bằng "Can I use your...?" với tên chiếc thước. Nghĩ đến mép thẳng giúp bút đi đúng đường.','Bạn chọn cây thước để kẻ đường thẳng. Hãy nói lại "Can I use your ruler?" như đang nhờ người ngồi cạnh, rồi thử chỉ chiếc thước trong hình.')
s=s.replace('Hold notebook and unfinished request; no answer label.','Show ruler and notebook clearly, with full request for supported repetition.')
s=s.replace('Bạn muốn nhắc người bạn nhìn lên bảng. Điền vào "Look at the..." rồi nói cả câu. Vật đó ở phía trước lớp, không nằm trên bàn.','Bạn đang nhìn xuống vở khi nghe "Look at the board." Bạn sẽ nhìn tới đâu? Chọn đúng chỗ trong hình, rồi nhắc lại lời hướng dẫn ấy.')
s=s.replace('Hold classroom view with empty board and incomplete instruction.','Show classroom board and desk notebook clearly; full model instruction for response, no highlighted location.')
f.write_text(s)
f=p/'261-270.txt';s=f.read_text().replace('Câu này tả tình hình trong câu chuyện, không hứa lúc nào bán hàng cũng dễ. Hai người quay lại đóng gói cẩn thận.','Có người đặt mua, cả hai vui hẳn. Bạn giữ hộp, người bạn chèn giấy quanh chậu để cây không nghiêng trên đường giao.');f.write_text(s)
f=p/'311-320.txt';s=f.read_text().replace('Quiet tả lúc hai người đang ghé thăm, khi quảng trường ít xe và nghe rõ tiếng nói của nhau.','Quiet tả sự yên tĩnh lúc này. Hai người ngồi ở quảng trường ít xe, nghe rõ tiếng chào từ cửa hàng vừa đi qua.');f.write_text(s)
f=p/'321-330.txt';s=f.read_text().replace('"Where is the bus stop."','"Where is the bus stop?"').replace('second rendered as question with question mark in final display.','the second is a question ending with a question mark.');f.write_text(s)
