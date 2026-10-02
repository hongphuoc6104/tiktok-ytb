from pathlib import Path
import json,hashlib,collections
p=Path(__file__).resolve().parents[3];o=p/'reports/scripts-100-341-440-20260930';m=json.loads((o/'manifest.json').read_text())
assert len(m)==100
for sub in ['kich-ban','content','briefs','reviews']:(o/sub).mkdir(exist_ok=True)
choice={342,344,350,352,354,359,361,365,372,377,380,381,382,384,387,388,392,393,396,400,401,403,404,409,418,426,428}
repeat={341,349,351,353,358,364,366,369,371,378,379,385,389,394,402,405,406,407,408,413,414,415,417,419,421,422,423,425,429,431,432,433,435,436,437,438,440}
transfer={345,347,363,399,412,439}
full=['# 100 kịch bản A1 — bài 341–440','', 'Từ north đến band. Chỉ nội dung, chưa tạo âm thanh, hình ảnh hoặc video. Thời lượng là ước tính, chưa đo WAV.','', 'Tất cả content revision 1 trong lô này chờ người dùng duyệt riêng. Duyệt các lô trước không áp dụng cho lô mới.',''];verification=[]
for e in m:
 assert e['state']=='awaiting_review' and e['content_revision']==1,e
 j=p/'runs'/e['job'];src=j/'revisions/content/1/content.json';c=json.loads(src.read_text());slug=f"{e['number']}-{e['word'].lower().replace(' ','-')}";meta=json.loads((j/'brief-current.json').read_text());bp=j/f"briefs/{meta['revision']}.json"
 for sub,path in [('content',src),('briefs',bp)]: (o/sub/f'{slug}.json').write_bytes(path.read_bytes())
 (o/'reviews'/f'{slug}.md').write_bytes(Path(e['review']).read_bytes())
 n=e['number'];practice='Lựa chọn hoặc nhận diện theo hình/tình huống' if n in choice else 'Nghe, nói lại và gắn với tình huống' if n in repeat else 'Đổi vai, thay câu hoặc trả lời theo sở thích' if n in transfer else 'Hoàn thành hoặc nhớ lại câu có gợi ý'
 e.update(practice_type=practice,reader_path=f'kich-ban/{slug}.md',content_path=f'content/{slug}.json',brief_path=f'briefs/{slug}.json',review_copy=f'reviews/{slug}.md',content_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),planned_images=sum(len(s['images']) for s in c['scenes']))
 lines=[f"# {n}. {e['word']} — {e['title']}",'',f"**Nghĩa:** {e['gloss_vi']}. **Mục tiêu bài:** {e['objective']}",'',f"**Diễn tiến:** {e['plot']}",'',f"**Lượt thực hành:** {practice}. **Dự kiến:** {e['estimated_seconds']} giây.",'',f"**Trạng thái:** content revision 1, chờ duyệt. Mã bài: `{e['job']}`.",'',f"[Bản duyệt gốc]({e['review']}) · [Bản sao trong hồ sơ](../{e['review_copy']})",'']
 for sc in c['scenes']:
  lines += [f"## {sc['id']} — {sc['title'].split(' — ')[-1]}",'',sc['narration'],'']
  texts=list(dict.fromkeys(v['text'] for im in sc['images'] for v in im['visible_text']))
  lines += ['**Chữ minh họa cho phép:** '+(' · '.join('“'+t+'”' for t in texts) if texts else 'Không thêm chữ.'),'',f"**Hình dự kiến:** {len(sc['images'])}"+('; cặp hình giữ góc cho thay đổi trước/sau.' if len(sc['images'])>1 else '; tập trung hành động, đồ vật hoặc quan hệ vị trí được nói tới.'),'']
  pause=sc['audio_direction']['vi']['learner_pause_seconds']
  if pause:lines += [f'**Chờ {pause} giây cuối cảnh** để người xem trả lời hoặc nói lại; phản hồi ở cảnh sau.','']
 reader='\n'.join(lines)+'\n';(o/e['reader_path']).write_text(reader);full += [line.replace('(../reviews/','(reviews/') for line in lines]+['---','']
 assert all(s['narration'] in reader for s in c['scenes'])
 verification.append({'job':e['job'],'number':n,'revision':1,'reader_matches_all_scenes':True,'content_sha256':e['content_sha256']})
(o/'KICH-BAN-100.md').write_text('\n'.join(full)+'\n');(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(o/'export-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
cnt=collections.Counter(e['practice_type'] for e in m);op=collections.Counter(e['opening_type'] for e in m);secs=[e['estimated_seconds'] for e in m];imgs=sum(e['planned_images'] for e in m)
lines=['# 100 kịch bản tiếp theo — bài 341–440','', '**100/100 content revision 1 đã nộp, chờ người dùng duyệt. Chưa chạy media/video.**','', '[Đọc trọn 100 kịch bản](KICH-BAN-100.md) · [Định hướng khai thác đa dạng](DINH-HUONG-NOI-DUNG.md) · [Kiểm tra nội dung](KIEM-TRA-NOI-DUNG.md)','', 'Lô này nối tiếp bài 241–340 đã duyệt. Từ đầu là north, từ cuối là band. Mỗi bài giữ một nghĩa và yêu cầu trong brief đã sinh từ kho.','', '## Kết quả','',f'- 100 mục từ/nghĩa, 500 cảnh; {imgs} hình trong kế hoạch, gồm {imgs-500} biến thể trước/sau. Chưa sinh hình.',f'- Thời lượng dự kiến {min(secs):.1f}–{max(secs):.1f} giây, trung bình {sum(secs)/len(secs):.1f} giây; chưa có WAV để đo thực.', '- 99 từ/cụm khác nhau: game có hai bài cho trận đấu và trò chơi. Các bài cùng chủ đề dùng tình huống và nhiệm vụ riêng.', '- Khoảng chờ 4–6 giây ở cảnh thực hành, đáp án hoặc mẫu phản hồi ở cảnh kế tiếp. Giữ mascot CH01 đúng áo xanh và nhận diện chuẩn.', '- Bản đọc chép đúng lời dẫn từ revision đã lưu; JSON bản sao được đối chiếu checksum với bản gốc.','', '## Cách thực hành','', '| Nhóm hoạt động | Số bài |','|---|---:|']
for k,v in cnt.items():lines.append(f'| {k} | {v} |')
lines+=['','## Danh sách','','| Bài | Từ / nghĩa | Bản đọc | Dự kiến | Bản duyệt |','|---|---|---|---:|---|']
for e in m:lines.append(f"| {e['number']} | {e['word']} — {e['gloss_vi']} | [{e['title']}]({e['reader_path']}) | {e['estimated_seconds']} giây | [r1]({e['review']}) |")
lines+=['','## Phạm vi và kiểm tra','', '- Chọn 100 mục A1 kế tiếp đủ điều kiện, tiếp tục bỏ qua các mục trùng nghĩa free/classmate/waiter/holiday và mục login.v có dạng đầu mục cần chuẩn hóa. Không sửa kho hay ledger thủ công.', '- Mục TV.n được rút bằng bộ lọc chủ đề qua cùng bank start vì bộ lọc --word hạ chữ gây không khớp TV; đã đối chiếu đúng mục và job. Không sửa code hoặc tạo job thay thế.', '- Grow giới hạn ở cây lớn lên; cold là nhiệt độ; chicken và mouse là con vật; fan là người hâm mộ. Không dạy lấn các nghĩa bị loại trong brief.', '- Khóa thao tác từ sản xuất đang chạy được chờ có giới hạn. Không dừng tiến trình khác, không sửa integrity hay file bảo vệ.', '- Ước tính, kiểm tra cấu trúc và số hình không chứng minh hiệu quả giữ chân hoặc học tập. Cần đo trên video thật sau khi được duyệt và sản xuất.', '- Chưa commit/push lô này.']
(o/'README.md').write_text('\n'.join(lines)+'\n');print('Exported',len(m),'readers;',imgs,'planned images; duration',min(secs),max(secs),round(sum(secs)/100,1));print(dict(cnt))
