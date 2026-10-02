from pathlib import Path
import json,hashlib,collections
p=Path(__file__).resolve().parents[3];o=p/'reports/scripts-100-20260930';m=json.loads((o/'manifest.json').read_text())
for sub in ['kich-ban','content','briefs','reviews']:(o/sub).mkdir(exist_ok=True)
choices={241,244,248,262,264,267,271,276,277,279,283,285,287,291,297,300,302,304,313,324,329,333,336}
repeat={245,246,272,278,292,303,306,312,318,320,323,327,330,331,332,335,338,339}
transfer={263,269,288,296,307,308,340}
recall={275,286,294,299,301,310,315,325,326,340}
full=['# 100 kịch bản mới — bài 241–340','', 'Tiếp nối lô đã duyệt trước. Chỉ phần nội dung; tất cả bản r1 chờ duyệt riêng.','', 'Thời lượng là ước tính theo brief, chưa phải số đo WAV. Giữ mascot áo xanh; chưa tạo âm thanh, ảnh hoặc video.','']
checks=[]
for e in m:
 assert e['state']=='awaiting_review' and e['content_revision']==1,e
 j=p/'runs'/e['job'];src=j/'revisions/content/1/content.json';c=json.loads(src.read_text());slug=f"{e['number']}-{e['word'].replace(' ','-')}";meta=json.loads((j/'brief-current.json').read_text());bp=j/f"briefs/{meta['revision']}.json"
 (o/'content'/f'{slug}.json').write_bytes(src.read_bytes());(o/'briefs'/f'{slug}.json').write_bytes(bp.read_bytes());(o/'reviews'/f'{slug}.md').write_bytes(Path(e['review']).read_bytes())
 n=e['number'];practice='Chọn hoặc nhận diện theo tình huống' if n in choices else 'Nghe, nói lại và gắn với hành động' if n in repeat else 'Đổi vai hoặc chuyển mẫu sang câu mới' if n in transfer else 'Tự nhớ lại một câu giao tiếp' if n in recall else 'Hoàn thành câu có gợi ý'
 e.update(practice_type=practice,reader_path=f'kich-ban/{slug}.md',content_path=f'content/{slug}.json',brief_path=f'briefs/{slug}.json',review_copy=f'reviews/{slug}.md',content_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),planned_images=sum(len(sc['images']) for sc in c['scenes']))
 lines=[f"# {n}. {e['word']} — {e['title']}",'',f"**Nghĩa trong bài:** {e['gloss_vi']}. **Mục tiêu:** {e['objective']}",'',f"**Diễn tiến:** {e['plot']}",'',f"**Luyện tập:** {practice}. **Thời lượng dự kiến:** {e['estimated_seconds']} giây.",'',f"**Trạng thái:** content revision 1, chờ người dùng duyệt. Mã bài: `{e['job']}`.",'',f"[Bản duyệt gốc]({e['review']}) · [Bản sao trong hồ sơ](../{e['review_copy']})",'']
 for sc in c['scenes']:
  lines += [f"## {sc['id']} — {sc['title'].split(' — ')[-1]}",'',sc['narration'],'']
  texts=list(dict.fromkeys(v['text'] for im in sc['images'] for v in im['visible_text']))
  lines += ['**Chữ minh họa:** '+(' · '.join('“'+x+'”' for x in texts) if texts else 'Không thêm chữ.') ,'',f"**Kế hoạch hình:** {len(sc['images'])} hình"+('; giữ góc máy cho thay đổi trước/sau.' if len(sc['images'])>1 else '; tập trung vào hành động hoặc vị trí được nói tới.'),'']
  wait=sc['audio_direction']['vi']['learner_pause_seconds']
  if wait:lines += [f'**Khoảng chờ:** {wait} giây cuối cảnh để người xem trả lời hoặc nói lại; phản hồi ở cảnh kế tiếp.','']
 (o/'kich-ban'/f'{slug}.md').write_text('\n'.join(lines)+'\n');full += [line.replace('(../reviews/', '(reviews/') for line in lines]+['---','']
 assert all(sc['narration'] in '\n'.join(lines) for sc in c['scenes'])
 checks.append({'number':n,'job':e['job'],'revision':1,'reader_matches_all_scenes':True,'copy_sha256':e['content_sha256'],'planned_images':e['planned_images']})
(o/'KICH-BAN-100.md').write_text('\n'.join(full)+'\n');(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(o/'export-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter(e['practice_type'] for e in m);openings=collections.Counter(e['opening_type'] for e in m);dur=[e['estimated_seconds'] for e in m];imgs=sum(e['planned_images'] for e in m)
lines=['# 100 kịch bản A1 mới — notebook đến get to','', '**Đã nộp 100/100 content revision 1, tất cả chờ duyệt. Chưa chạy media/video.**','', '[Đọc toàn bộ 100 kịch bản](KICH-BAN-100.md) · [Định hướng đa dạng nội dung](DINH-HUONG-NOI-DUNG.md)','', 'Bài 241–340 nối tiếp lô 141–240 đã duyệt. Lần duyệt lô trước không áp dụng cho lô này.','', '## Những điểm đã làm','',f'- 100 mục từ/nghĩa từ kho A1; 500 cảnh, {imgs} hình dự kiến, trong đó {imgs-500} biến thể giữ góc máy. Chỉ lập kế hoạch, chưa tạo ảnh.',f'- Ước tính {min(dur):.1f}–{max(dur):.1f} giây/bài, trung bình {sum(dur)/100:.1f} giây. Thời lượng thực chờ đo âm thanh.',f'- {openings["B-cau-dung-ngay"]} bài mở bằng câu tiếng Anh dùng ngay; các bài còn lại mở bằng tình huống, câu hỏi hoặc sự cố cụ thể. Đây là cách phân loại biên tập, không phải kết quả thử nghiệm giữ chân.', '- Lượt thực hành có khoảng chờ 4–6 giây theo câu và nhiệm vụ; có phản hồi rõ. Mascot giữ nhận diện chuẩn, diễn viên phụ có vai riêng xuyên suốt.', '- Có 99 từ/cụm từ khác nhau: park có hai mục riêng, đỗ xe và công viên. Các từ nhiều nghĩa khác cũng chỉ dạy đúng nghĩa đã giữ chỗ.','', '## Cách luyện tập','', '| Hoạt động | Số bài |','|---|---:|']
for k,v in counts.items():lines.append(f'| {k} | {v} |')
lines+=['','## Danh sách bản đọc và bản duyệt','','| Bài | Từ / nghĩa | Kịch bản | Dự kiến | Bản duyệt |','|---|---|---|---:|---|']
for e in m:lines.append(f"| {e['number']} | {e['word']} — {e['gloss_vi']} | [{e['title']}]({e['reader_path']}) | {e['estimated_seconds']} giây | [r1]({e['review']}) |")
lines+=['','## Đối chiếu kho và phạm vi','', '- Bỏ qua free.adj.gratis, classmate.n.peer, waiter.n.job, holiday.n.vacation vì trùng nghĩa với bài đã có. Bỏ qua login.v vì dạng đầu mục và từ loại cần được chuẩn hóa riêng. Các mục này còn trong kho; không sửa ledger thủ công.', '- Brief travel được sửa qua revise-brief để bỏ riêng một dòng tránh nghĩa trùng mâu thuẫn, giữ nguyên mục travel.v. Xem brief-clarifications.json.', '- Kiểm tra cấu trúc, neo lời dẫn, mục kho và bản sao không thay thế duyệt nội dung của bạn hay nghiệm thu hình/giọng thật.', '- Tệp người Việt học A1 là đối tượng theo brief; chưa có dữ liệu mới để kết luận giữ chân tốt hơn. Sau khi đăng cần so sánh các mốc đo tương đương và xét độ dài thực.', '- Chưa commit/push lô này. Các job cũ và file được bảo vệ được giữ nguyên.']
(o/'README.md').write_text('\n'.join(lines)+'\n');print('Exported 100 readers; images',imgs,'practice',dict(counts),'openings',dict(openings))
