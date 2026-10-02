import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];out=ROOT/'reports/drama-A1-pilot-20261001';folder=ROOT/'runs/vocab-wait-for-script-738'
b=json.loads((folder/'briefs/2.json').read_text())
(out/'brief-before.json').write_bytes((folder/'briefs/2.json').read_bytes())
(out/'content-before-r2.json').write_bytes((folder/'revisions/content/2/content.json').read_bytes())
b['video_type']='micro-drama episode'
b['duration']={'min_seconds':35,'max_seconds':75}
b['tone']='Buồn nhẹ, gần gũi, tiết chế; kể qua chi tiết và hành động, không bi lụy hoặc giảng bài.'
b['goal']='Người xem theo dõi trọn một lần tiễn mẹ đi xa, nhận ra wait for nghĩa chờ đợi và hoàn thành câu Please wait for me. trong tình huống muốn giữ người thân lại.'
p=b['planning']
p['pacing']='Mở ngay với lời mẹ dặn và hai ly trà cạnh chỗ trống; câu mẫu đầu ở cảnh kế tiếp. Đưa áp lực xe sắp chạy rồi trả lời vì sao mẹ đến muộn. Giữ khoảng chờ thực hành 4 giây trước cái ôm và cảnh kết. Không chào, không title card, không liệt kê ví dụ.'
p['avoid'] += ['Ép chuyện phải có người mất hoặc tai nạn để gây buồn','Câu mở giống tập khác chỉ thay từ khóa','Giấu lời giải của câu mở sang tập sau','Lời bình sáo rỗng, định nghĩa kéo dài, gọi like/follow trước kết quả','Nhét từ khó vào lời thoại để trông như phim']
p['domain_requirements']=[x for x in p['domain_requirements'] if not x.startswith('Phần giải thích dùng tiếng Anh ngắn')]
p['domain_requirements'] += ['Tập thử trong một chuỗi phim ngắn hư cấu, mascot là nhân vật chính; bản 9:16 tiếng Việt xen hai câu tiếng Anh đúng nghĩa chờ đợi.', 'Giữ đủ sáu cảnh và bốn ý R1–R4 của brief kho. Tiếng Anh phục vụ nhu cầu của nhân vật; nghĩa được hỗ trợ bởi tiếng Việt và hình, lượt điền câu có khoảng chờ và đáp án.', 'Mở bằng câu Mẹ bảo đừng chờ nữa. và hai ly trà; đến cuối tập phải giải thích lời mẹ dặn và giải quyết lần tiễn này.', 'Tập này có kết riêng; dùng quan hệ mẹ–con và đồ vật để nối tập sau, không cần mỗi tập đều buồn hoặc cùng motif chờ đợi.']
p['assumptions']=[x for x in p['assumptions'] if not x.startswith('Thời lượng dự kiến theo nhóm medium')]
p['assumptions'] += ['Người dùng yêu cầu thử một video ngày 01/10/2026; chọn job wait for đang chờ duyệt content, chưa có media/video. Không áp hướng drama cho toàn lô trước khi xem tập thử.', 'Hướng khoảng 55 giây, cho phép 35–75 giây theo yêu cầu; ước tính khoảng 52 giây gồm 4 giây thực hành, phải đo WAV thật.', 'Không có nhạc/SFX hay đa giọng được thêm qua hướng dẫn text; lời kể dùng giọng hiện có, hiệu quả cảm xúc phải nghe thật.']
(out/'brief-proposal.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
print('Prepared from bank brief; entry/sense, six scenes and all R1–R4 retained')
