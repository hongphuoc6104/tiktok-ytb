from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/drama-A1-all-20261001';raw=json.loads((OUT/'narration-attempts/028-039/episodes.json').read_text())['episodes']
updates=[
('Bức ảnh ông chưa nhìn rõ','Ông tìm gương mặt mình trong ảnh gia đình trên màn hình; cháu chờ ông tự nhận ra thay vì chỉ vị trí ngay.','Look at the ___.',[
'Ông nhìn mãi, vẫn chưa thấy mình đâu. "Look at the screen." Ông nhìn lên màn hình nhé. Tôi kéo ghế sang bên, để ông ngồi gần hơn.',
'Em vừa gửi về ảnh chụp cả nhà lần trước. Ông cứ nhìn tấm ảnh nhỏ trên điện thoại, rồi bảo chắc mình đứng ngoài. Tôi mở nó trên màn hình lớn ở bàn làm việc.',
'"This screen is bigger." Màn hình này lớn hơn. Ông chỉ vào góc ảnh, hỏi người đội mũ có phải mình không. Tôi gật đầu. Ông bật cười vì hôm ấy đã quên cởi mũ.',
'Bạn nói giúp tôi câu nhìn lên màn hình bằng tiếng Anh nhé.',
'"Look at the screen." Đúng rồi. Ông tìm thấy thêm người bạn đứng cạnh mình. Tôi định chuyển ảnh khác, ông giữ tay lại: Khoan, để ông nhìn thêm chút nữa.']),
('Chiếc bàn phím được cho mượn','Bàn phím ở quầy gặp trục trặc; đồng nghiệp cho mượn cái đang dùng rồi ở lại đợi người mới xong phần việc.','Can I use your ___?',[
'Chị Mai gõ lại, chữ vẫn chưa hiện. "Can I use your keyboard?" Em dùng bàn phím của chị được không? Tôi đứng ở quầy, không dám hứa khách đợi bao lâu.',
'Tôi mới tới làm nên cứ nghĩ mình đã bấm sai. Chị đưa bàn phím đang dùng sang, bảo thử với cái này trước đã. Tôi kéo ghế lại, hỏi chị có đang cần nó không.',
'"This keyboard is old." Bàn phím này cũ rồi. Chị nói về chiếc vừa đem cất, rồi ngồi cạnh tôi. Dòng chữ đầu hiện lên, tôi mới bớt nhìn ra phía cửa.',
'Nếu cần xin dùng bàn phím của người bên cạnh, bạn nói giúp tôi cả câu bằng tiếng Anh nhé.',
'"Can I use your keyboard?" Đúng rồi. Tôi in xong giấy cho khách, trả lại bàn phím. Chị vẫn ngồi đó, hỏi mai tôi có muốn tới sớm tập thêm không.']),
('Con trỏ bố muốn tự kéo','Bố muốn tự gửi một tờ đăng ký trên máy tính nhưng chuột không phản hồi; con đưa con chuột khác, rồi để bố tự thực hiện bước cuối.','Move the ___.',[
'Bố rê tay, con trỏ vẫn đứng yên. "Move the mouse." Bố di chuyển chuột nhé. Tôi nhìn bàn tay bố đang cố làm chậm hơn bình thường.',
'Bố muốn tự gửi tờ đăng ký, nên không cho tôi làm hộ hết. Tôi đưa con chuột còn dùng được từ bàn bên cạnh sang. Bố đặt tay lại, vẫn giữ tờ ghi chú của mình.',
'"This mouse works." Chuột máy tính này dùng được. Con trỏ đi theo tay bố. Tôi lùi ghế lại một chút, để bố tự tìm nút mình cần nhấn.',
'Bạn nói giúp tôi câu di chuyển chuột bằng tiếng Anh nhé.',
'"Move the mouse." Đúng rồi. Bố kéo con trỏ tới đúng chỗ, nhấn rồi ngồi im nhìn màn hình. Một lúc sau, bố quay sang hỏi: Lần sau con còn ngồi đây với bố không?']),
('Ứng dụng mẹ muốn tự mở','Mẹ muốn tự xem ảnh cháu qua một ứng dụng, thay vì luôn đưa máy cho con; nhân vật giúp mẹ nhớ cách nhờ và tự thử.','Open the ___.',[
'Mẹ đưa máy, rồi lại giữ tay tôi. "Open the app." Mở ứng dụng nhé. Tôi định bấm hộ, mẹ bảo hôm nay để mẹ thử trước.',
'Em gửi ảnh về trong ứng dụng này từ tối qua. Lần nào mẹ cũng chờ tôi về mới xem. Tôi đặt điện thoại lại lên bàn, ngồi cạnh để mẹ có thể tự chạm.',
'Xem xong, mẹ hỏi có thể quay về màn hình đầu không. "Close the app." Đóng ứng dụng nhé. Tôi chỉ biểu tượng, không cầm máy từ tay mẹ.',
'Nếu muốn nhờ ai đó mở ứng dụng, bạn nói giúp mẹ câu ấy bằng tiếng Anh nhé.',
'"Open the app." Đúng rồi. Mẹ mở lại, chọn đúng bức ảnh em đang cười. Tôi đứng lên lấy nước. Lúc quay lại, điện thoại vẫn nằm trong tay mẹ.']),
('Bài học mang ra khỏi mạng','Hai bạn chuẩn bị học ở nơi không có mạng; tải bài về trước, rồi cùng giữ lời hẹn học tiếp khi máy đã rời chỗ kết nối.','Download the ___.',[
'Xe sắp tới, bài học vẫn ở trên mạng. "Download the file." Tải tập tin xuống nhé. Duy hỏi tôi có định mang bài theo hay lại nói mai học tiếp.',
'Hai đứa hẹn tới thư viện ngồi cùng nhau. Tôi thường mở đường dẫn rồi quên, đến lúc cần lại không tìm ra. Duy kéo ghế lại, chờ tôi chọn đúng bài đã hẹn.',
'"Can I download this lesson?" Mình tải bài học này xuống được không? Tôi hỏi, Duy chỉ bản được phép tải của lớp. Tập tin bắt đầu về máy, chúng tôi chưa vội gập nó lại.',
'Bạn nhắc giúp tôi câu tải tập tin xuống bằng tiếng Anh nhé.',
'"Download the file." Đúng rồi. Tập tin đã ở trong máy. Lên xe, Duy hỏi tôi muốn bắt đầu từ trang nào. Lần này, tôi mở bài ra, thay vì nhìn điện thoại.']),
('Bức ảnh mẹ muốn giữ','Mẹ đưa một tấm ảnh vừa nhận, nhờ con lưu lại; con làm ngay thay vì hẹn khi rảnh, để mẹ được xem nó lần nữa.','Save the ___.',[
'Mẹ gửi ảnh, tôi định xem rồi đóng. "Save the file." Lưu tập tin nhé. Mẹ nhắc từ đầu bàn, sợ lần sau lại không biết tìm ở đâu.',
'Trong ảnh là buổi cả nhà cùng ăn cơm đã lâu. Tôi đang làm dở việc, định nói lát nữa con lưu. Mẹ ngồi chờ, chỉ hỏi hôm đó có ai cầm máy chụp nhỉ.',
'"Please save this photo." Lưu bức ảnh này nhé. Tôi nói lại điều mẹ cần, rồi đặt tên dễ nhận cho ảnh. Mẹ hỏi khi nào muốn xem thì gọi con có được không.',
'Bạn nói giúp mẹ câu lưu tập tin bằng tiếng Anh nhé.',
'"Save the file." Đúng rồi. Tôi mở lại ảnh vừa lưu, quay màn hình về phía mẹ. Lần này, tôi không nói lát nữa. Hai mẹ con tìm một gương mặt ở góc ảnh.']),
('Ảnh cũ không phải tệp thừa','Dọn máy với bạn, nhân vật nhận ra ảnh chung suýt bị xóa; hai người xem lại trước khi quyết định bỏ bản trùng còn giữ ảnh gốc.','Do not delete the ___.',[
'Tuấn định xóa, tôi chặn lại một chút. "Do not delete the photo." Đừng xóa bức ảnh. Tôi nhận ra chiếc áo mình mặc trong hình, trước cả gương mặt.',
'Đó là ảnh lần đầu hai đứa đi làm cùng nhau. Tuấn tưởng một bản thừa chưa cần mở. Tôi xin xem lại, chỉ người đứng ngoài mép ảnh mà bạn đã quên.',
'Có một bản trùng khác, hai đứa đã cùng kiểm tra. "Delete this file." Xóa tập tin này nhé. Tuấn đưa tay hỏi lại tôi, không bấm ngay như lúc đầu.',
'Nếu muốn giữ bức ảnh lại, bạn nói giúp tôi câu đừng xóa bức ảnh bằng tiếng Anh nhé.',
'"Do not delete the photo." Đúng rồi. Ảnh cũ vẫn ở đó, bản trùng đã bỏ. Tuấn hỏi người ở mép hình giờ làm đâu. Tôi kéo ghế gần lại, kể thêm một chuyện.']),
('Nút gọi lại của bà','Bà muốn tự gọi người nhà bằng chuột máy tính; lần đầu chưa có người nghe, bà chủ động chọn gọi lại.','Click ___.',[
'Bà đặt tay lên chuột, rồi rút lại. "Click here." Nhấp chuột ở đây nhé. Tôi chỉ biểu tượng cuộc gọi, không nhấc tay bà đặt hộ.',
'Tôi thường gọi xong rồi đưa máy cho bà. Hôm nay, bà muốn tự làm từ đầu. Bà nhìn con trỏ, hỏi bấm một lần vậy đã được chưa. Tôi chờ bà thử.',
'Cuộc gọi chưa có người nhấc. "Click the green button." Nhấp nút màu xanh lá nhé. Tôi chỉ nút gọi lại, bà kéo con trỏ chậm hơn lần trước.',
'Bạn nhắc giúp bà câu nhấp chuột ở đây bằng tiếng Anh nhé.',
'"Click here." Đúng rồi. Bà tự nhấp gọi lại. Người nhà vừa nghe máy, bà kể ngay rằng hôm nay mình đã tự gọi. Tôi ngồi bên cạnh, để bà kể hết.']),
('Tên trên tấm thiệp','Miu muốn tự gõ tên trên thiệp tặng mẹ; mắc một lỗi nhỏ nhưng sửa lại và giữ bản mình đã làm.','Type your ___.',[
'Miu giấu tấm thiệp, chưa có tên mình. "Type your name." Gõ tên của em nhé. Tôi kéo bàn phím tới gần, để em tự tìm chữ đầu.',
'Em muốn mẹ biết thiệp này mình đã làm. Gõ được một chữ, em lại nhìn sang tôi. Tôi định bấm hộ rồi thôi, chỉ vào tấm thẻ có tên em để em tự đối chiếu.',
'"I can type my name." Em có thể gõ tên mình. Miu nói vậy khi đã tìm được chữ cuối. Có một chữ bị lặp, em tự xóa rồi gõ lại, không giấu đi.',
'Nếu muốn nhắc em gõ tên của mình, bạn nói giúp tôi bằng tiếng Anh nhé.',
'"Type your name." Đúng rồi. Thiệp được in ra, tên chưa nằm thật giữa trang. Miu vẫn giữ lấy, bỏ vào phong bì. Em hỏi lúc mẹ mở thì tôi có ngồi cạnh không.']),
('Danh sách còn ở chỗ cũ','Em định gõ lại một danh sách dài; nhân vật cho thấy có thể sao chép mà bản đầu vẫn còn, rồi nhường máy cho em làm phần còn lại.','Copy the ___.',[
'Em mở trang trống, định gõ lại từ đầu. "Copy the text." Sao chép đoạn chữ nhé. Tôi giữ chiếc ghế lại, hỏi em có cần ngồi đây thêm cả buổi không.',
'Danh sách là những câu em đã chọn hôm qua. Em sợ làm hỏng nên muốn chép lại từng chữ. Tôi mở bản đầu cạnh trang mới, để em còn nhìn thấy chỗ mình bắt đầu.',
'"Can I copy this list?" Em sao chép danh sách này được không? Tôi gật đầu. Em lấy một bản vào trang mới, rồi quay lại kiểm tra bản đầu vẫn còn.',
'Bạn giúp tôi nói câu sao chép đoạn chữ bằng tiếng Anh nhé.',
'"Copy the text." Đúng rồi. Em làm tiếp phần còn lại, kéo ghế về phía mình. Tôi đứng lên lấy nước. Lúc trở lại, em chỉ hai bản còn đủ, không gọi tôi làm hộ.']),
('Thêm một người chúc sinh nhật','Cuộc gọi sinh nhật không nối vì thiếu mạng; hai bạn chuyển tới chỗ có kết nối và cùng gửi lời chúc thay vì để một người chờ.','I need the ___.',[
'Cả bàn im, cuộc gọi vẫn không nối. "There is no internet here." Ở đây không có mạng Internet. Tôi nhìn chiếc bánh đã đặt sẵn trước máy.',
'Tôi hẹn chúc sinh nhật em qua máy tính. Em đang đợi ở xa, còn người bạn ngồi cạnh đã viết xong chiếc thiệp. Bạn hỏi mình có chỗ nào khác để nối mạng không.',
'"I need the internet." Tôi cần mạng Internet. Tôi mượn phòng của bạn, nơi có kết nối. Bạn mang hộp bánh theo, đặt lại lên bàn. Hai đứa ngồi chờ máy nối lại.',
'Nếu cần mạng Internet để gọi cho em, bạn nói giúp tôi câu tôi cần mạng Internet bằng tiếng Anh nhé.',
'"I need the internet." Đúng rồi. Cuộc gọi nối được. Em hỏi sao hôm nay có thêm một người. Tôi nhìn người bạn đứng cạnh, bật cười: Vì có thêm một người chúc em.']),
('Người đan rổ trên trang web','Bác muốn biết sản phẩm mình làm có xuất hiện trên trang web chung hay không; được xem ảnh rồi chỉ ra chi tiết tay mình đã sửa.','Visit the ___.',[
'Bác đặt chiếc rổ cạnh máy, chưa dám hỏi. "Visit the website." Mở trang web nhé. Tôi kéo màn hình lại gần, hỏi bác muốn tìm mẫu nào trước.',
'Làng nghề có trang giới thiệu chung, bác chưa xem lần nào. Tôi mở từng ảnh rổ, bác cứ nói đẹp quá mà. Đến tấm ảnh ở cuối, bác chỉ tay vào một chiếc quai.',
'"I like this website." Bác thích trang web này. Bác nhận ra chiếc quai mình đã đan lại, kể vì sao nó khác bản đầu. Tôi dừng chuột ở đúng ảnh ấy.',
'Bạn nhắc giúp tôi câu mở trang web bằng tiếng Anh nhé.',
'"Visit the website." Đúng rồi. Bác xem thêm một lúc, rồi đặt chiếc rổ thật lên bàn: Lần sau chụp cái này nhé. Tôi dịch máy sang bên, để chiếc rổ có chỗ đứng.'])]
for ep,(title,plot,stem,narrs) in zip(raw,updates):
 ep.update(title=title,plot_vi=plot,learner_outcome_vi='Nhận ra nghĩa chọn của từ và dùng một câu ngắn để thực hiện hoặc nhờ hành động.',editorial_review='Reviewed and rewritten by primary agent; narration frozen before anchors.')
 for i,(s,narr) in enumerate(zip(ep['scenes'],narrs)):
  s.update(narration=narr,practice_pause_seconds=4 if i==3 else 0,title_vi=['Chi tiết đầu chuyện','Điều cần hiểu','Hành động làm đổi chuyện','Lời người xem giúp nói','Kết quả'][i],purpose_en=['Open with the visible human need and an early usable English utterance.','Show the relationship and resistance without a procedural lecture.','Use the second English model with correct time/reference and a meaningful visible action.','Invite one supported sentence for the same need; wait before revealing the answer.','Give feedback and a small concrete consequence, without a perfect or generic emotional flourish.'][i])
 ep['scenes'][3]['stem']=stem
 (OUT/'narration-frozen'/f"{ep['job']}.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
print('Frozen twelve technology stories; removed mistranslations, unsafe repair steps and false guarantees before anchors')
