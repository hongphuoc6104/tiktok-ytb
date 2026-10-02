from pathlib import Path
import json,hashlib,re,collections
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/opening-audit-A1-331-20261001'
m=json.loads((OUT/'manifest.json').read_text());audit={x['number']:x for x in json.loads((OUT/'audit.json').read_text())};base={x['number']:x for x in json.loads((OUT/'baseline.json').read_text())}
assert len(m)==331 and all(e['state'] in ['awaiting_review','skipped_protected'] for e in m)
for sub in ['kich-ban','content','reviews']:(OUT/sub).mkdir(exist_ok=True)
full=['# 331 kịch bản A1 — bản sau rà mở đầu','','Bài 441–771. Đây là bản đọc từ revision hiện tại, chờ người dùng duyệt. Thời lượng là ước tính; chưa tạo media.',''];verify=[]
for e in m:
 n=e['number'];j=ROOT/'runs'/e['job'];rev=e['content_revision'];assert rev in [1,2],e
 p=j/f'revisions/content/{rev}/content.json';c=json.loads(p.read_text());a=audit[n]
 assert c['scenes'][1:]==base[n]['content']['scenes'][1:],n
 assert hashlib.sha256((j/'revisions/content/1/content.json').read_bytes()).hexdigest()==base[n]['saved_r1_sha256'],n
 if e['changed']:assert c['scenes'][0]['narration'].startswith(a['new_opening']),n
 else:assert c==base[n]['content'],n
 assert c==json.loads((j/'draft/content.json').read_text()),n
 slug=f"{n}-{e['job'].removeprefix('vocab-').rsplit('-script-',1)[0]}";rp=Path(e['review']);assert rp.is_file(),n
 (OUT/'content'/f'{slug}.json').write_bytes(p.read_bytes());(OUT/'reviews'/f'{slug}.md').write_bytes(rp.read_bytes())
 e.update(reader_path=f'kich-ban/{slug}.md',content_path=f'content/{slug}.json',review_copy=f'reviews/{slug}.md',content_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 lines=[f"# {n}. {e['teaching_form']} — {e['title']}",'',f"**Nghĩa chọn:** {e.get('selected_gloss_vi',e['gloss_vi'])}.",'',f"**Mục tiêu:** {e['objective']}",'',f"**Mở đầu:** {a['new_opening']}",'',f"**Kết quả rà:** {'Đã sửa lời mở và hình đầu' if e['changed'] else 'Giữ bản đã có tình huống rõ'} · content r{rev}, chờ duyệt.",'',f"**Dự kiến:** {e['estimated_seconds']} giây · {e['scene_count']} cảnh. Chưa đo WAV.",'',f"[Bản duyệt gốc]({rp}) · [Bản sao bản duyệt](../{e['review_copy']})",'']
 for s in c['scenes']:
  lines += [f"## {s['id']}",'',s['narration'],'']
  texts=list(dict.fromkeys(v['text'] for im in s['images'] for v in im['visible_text']))
  lines+=['**Chữ cho phép:** '+(' · '.join('“'+t+'”' for t in texts) if texts else 'Không thêm chữ.'),'']
  if s['id']=='SC01':lines+=['**Điểm chú ý của hình đầu:** '+a['new_opening'],'']
  pause=s['audio_direction']['vi']['learner_pause_seconds']
  if pause:lines += [f'**Chờ {pause} giây cuối cảnh** trước phản hồi ở cảnh sau.','']
 reader='\n'.join(lines)+'\n';(OUT/e['reader_path']).write_text(reader)
 assert all(s['narration'] in reader for s in c['scenes']),n
 full += [l.replace('(../reviews/','(reviews/') for l in lines]+['---','']
 verify.append({'number':n,'job':e['job'],'revision':rev,'saved_content_matches_draft':True,'all_reader_narration_matches_saved_revision':True,'scenes_after_SC01_literal_unchanged':True,'r1_hash_preserved':True,'content_sha256':e['content_sha256']})
(OUT/'KICH-BAN-331.md').write_text('\n'.join(full)+'\n');(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(OUT/'export-verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n')
new=[a for a in audit.values() if a['decision']=='rewrite'];kept=[a for a in audit.values() if a['decision']=='keep']
prefix=collections.Counter(' '.join(a['new_opening'].lower().split()[:2]) for a in audit.values())
report=['# Rà 3 giây đầu của 331 kịch bản A1','','## Kết quả biên tập','',f'- Rà đủ 331 bài 441–771: {len(new)} bài cần sửa; {len(kept)} bài được giữ.', '- Điểm yếu của lô trước: nhiều câu mở kéo dài trước khi tới chi tiết đáng chú ý; nhịp hỏi → định nghĩa → giới thiệu bối cảnh gần giống nhau, nhiều cảnh mở ở bàn/ghế/giấy với điểm chú ý chưa nổi bật.', '- Bản mới vào thẳng việc đang cần: sự cố, lựa chọn, chi tiết trái kỳ vọng, lời nhờ/lời rủ, một câu cần nói, hoặc một vật cần nhận diện. Không ép tất cả vào câu đố.', '- Sửa SC01 gồm lời dẫn, mục đích, hành động, hình đầu, góc nhìn và neo/coverage khớp lời đã chốt. Không chỉ thay một câu hook rồi giữ hình chung chung.', '- Giữ nguyên các cảnh còn lại, nghĩa kho, câu mẫu, lượt thực hành, khoảng chờ và phản hồi. Kết bài giải quyết tình huống mở, không tạo tò mò rồi bỏ lửng.', '', '## Tiêu chí rà','', '1. Có chi tiết cụ thể để chú ý từ câu đầu, không chào/giới thiệu seri.', '2. Từ ngữ dễ hiểu với người Việt đầu A1; không thêm đích học hoặc nghĩa khác.', '3. Hình đầu cho thấy đúng vật, quan hệ hoặc trở ngại của lời mở.', '4. Chi tiết có ích xuất hiện trước giải thích nền, không giấu đáp án chỉ để kéo dài.', '5. Cách vào bài và điểm nhìn thay đổi theo tình huống; tránh câu nguyên văn trùng lặp.', '6. Câu mẫu/lượt luyện có mục đích và phần sau trả được điều đã gợi ra.', '', '## Giới hạn của việc rà','',f'- 321 câu mở mới có 6–9 tiếng theo cách đếm khoảng trắng. Ước tính câu mở {min(a["estimated_opening_seconds"] for a in new):.2f}–{max(a["estimated_opening_seconds"] for a in new):.2f} giây theo brief; không phải số đo giọng.', '- Mười mở đầu giữ lại có thể cần hơn 3 giây để đọc hết nhưng điểm đáng chú ý nằm ngay đầu và hình kế hoạch làm rõ. Không cắt bằng số ký tự để đổi lấy một câu khó hiểu.', '- 331 câu đầu khác nhau nguyên văn; đối chiếu thêm 399 bản nháp khác hiện có cũng không thấy trùng câu đầu. Phạm vi không bao gồm hồ sơ vắng trên máy; trùng chữ không chứng minh cảm giác giống/khác ở video thật. Một số motif giấy/thiệp/túi/bàn và cấu trúc phần giải thích vẫn gần nhau. Cần quan sát độ giống về hình và giọng khi dựng.', '- Ảnh, giọng, khoảng chờ, thời gian đọc chữ và nhịp cắt chưa được xem/nghe vì chưa tạo media trong lượt này.', '- Chưa có dữ liệu đăng các bài này. Không ghi chắc chắn tăng giữ chân hoặc hiệu quả học.', '', '## Những mở đầu được giữ','']
for a in kept:report+=['- '+str(a['number'])+'. '+a['word']+': '+a['new_opening']]
report+=['', '## Cách kiểm tra khi có lượt đăng thử','', '- Dùng cùng phong cách hình, giọng và lịch đăng hợp lý để giảm các khác biệt ngoài kịch bản. Ghi loại mở đầu cùng số liệu từng bài.', '- So tỷ lệ còn xem ở giây 1, 3, 5 nếu nền tảng cung cấp; thêm thời gian xem trung bình/tổng thời lượng, tỷ lệ xem hết, lưu/chia sẻ và follower mới theo lượt xem.', '- Kiểm tra nhiều bài cùng loại; không coi một video nổi bật là bằng chứng cho toàn bộ lô.', '- Nếu rơi mạnh trước giây 3, kiểm hình đầu/âm thanh đầu và độ rõ của câu mở. Nếu qua giây 3 nhưng rơi ở phần giải thích, sửa nhịp thân bài qua revision mới.', '', '## So sánh từng bài','', '| Bài | Từ | Trước | Sau | Xử lý |','|---|---|---|---|']
for e in m:
 a=audit[e['number']];report.append(f"| {e['number']} | {e['teaching_form']} | {a['old_opening']} | {a['new_opening']} | {'Sửa, r2' if e['changed'] else 'Giữ, r1'} |")
(OUT/'BAO-CAO-RA-SOAT.md').write_text('\n'.join(report)+'\n')
lines=['# Kịch bản A1 sau rà phần mở đầu — 01/10/2026','','**Rà đủ 331 bài 441–771; 321 bài có content revision 2, 10 bài giữ revision 1. Tất cả đang chờ người dùng duyệt.**','','[Đọc toàn bộ kịch bản hiện tại](KICH-BAN-331.md) · [Xem trước/sau và tiêu chí rà](BAO-CAO-RA-SOAT.md)','','Đây là bản mới nhất cho lô A1 còn lại. Bản r1 ở scripts-A1-remaining-20260930 được giữ để tra lịch sử. Lượt này chỉ sửa content, không tạo âm thanh/ảnh/video, không commit/push, không ghi quyết định duyệt thay người dùng.','','## Kiểm tra','', '- Tất cả bản nháp đã qua check-draft; integrity-diff không có file bảo vệ thay đổi.', '- Neo/coverage đặt lại sau lời dẫn đã chốt; bản đọc khớp bản saved revision, giữ nguyên dữ liệu r1 và mọi cảnh sau SC01.', '- Mọi điểm ước tính tổng thời lượng còn nằm trong khoảng brief riêng. Thời lượng thật và hiệu quả mở đầu phải kiểm qua WAV/video/số liệu sau.', '', '## Danh sách','', '| Bài | Từ | Kịch bản | Revision | Mở đầu |','|---|---|---|---:|---|']
for e in m:lines.append(f"| {e['number']} | {e['teaching_form']} | [{e['title']}]({e['reader_path']}) | [r{e['content_revision']}]({e['review']}) | {e['opening']} |")
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print('EXPORTED',len(m),'current readers; review r2=',sum(e['content_revision']==2 for e in m),'r1=',sum(e['content_revision']==1 for e in m))
