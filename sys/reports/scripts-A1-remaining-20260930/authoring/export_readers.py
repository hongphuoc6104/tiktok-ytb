import json,hashlib,collections,re
from pathlib import Path
from source_utils import ROOT,OUT,records
m=json.loads((OUT/'manifest.json').read_text());recs=records();assert len(m)==331
for sub in ['kich-ban','content','briefs','reviews']:(OUT/sub).mkdir(exist_ok=True)
full=['# 331 kịch bản A1 còn lại — bài 441–771','','Lô mới chờ duyệt content revision 1. Thời lượng là ước tính từ lời dẫn và khoảng chờ, chưa đo WAV.',''];verification=[]
for e in m:
 assert e['state']=='awaiting_review' and e['content_revision']==1,e['job']
 j=ROOT/'runs'/e['job'];src=j/'revisions/content/1/content.json';c=json.loads(src.read_text());assert c==json.loads((j/'draft/content.json').read_text()),e['job']
 assert [s['narration'] for s in c['scenes']]==[r[0] for r in recs[e['number']]['rows']],e['job']
 meta=json.loads((j/'brief-current.json').read_text());bp=j/f"briefs/{meta['revision']}.json";slug=f"{e['number']}-{e['job'].removeprefix('vocab-').rsplit('-script-',1)[0]}"
 for sub,path in [('content',src),('briefs',bp)]: (OUT/sub/f'{slug}.json').write_bytes(path.read_bytes())
 review=Path(e['review']);assert review.is_file();(OUT/'reviews'/f'{slug}.md').write_bytes(review.read_bytes())
 e.update(reader_path=f'kich-ban/{slug}.md',content_path=f'content/{slug}.json',brief_path=f'briefs/{slug}.json',review_copy=f'reviews/{slug}.md',content_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
 practice=c['scenes'][-2]['narration'];activity='Chọn hoặc nhận diện rồi nhận phản hồi' if re.search(r'(?:Chọn|chọn)',practice) else 'Hoàn thành hoặc nhớ lại câu có gợi ý' if re.search(r'(?:Hoàn thành|hoàn thành)',practice) else 'Nói câu theo vai/tình huống, có mẫu và phản hồi'
 e['practice_type']=activity
 lines=[f"# {e['number']}. {e['teaching_form']} — {e['title']}",'',f"**Nghĩa/cách dùng trong bài:** {e.get('selected_gloss_vi',e['gloss_vi'])}.",'',f"**Mục tiêu:** {e['objective']}",'',f"**Diễn tiến:** {e['plot']}",'',f"**Dự kiến:** {e['estimated_seconds']} giây · {e['scene_count']} cảnh · {activity}.",'', '**Hai câu mẫu chính:**','']+['- '+x for x in e['models']]+['',f"**Trạng thái:** chờ duyệt content revision 1. Mã hồ sơ: `{e['job']}`.",'',f"[Bản duyệt gốc]({review}) · [Bản sao hồ sơ](../{e['review_copy']})",'']
 for sc in c['scenes']:
  lines += [f"## {sc['id']} — {sc['title'].split(' — ')[-1]}",'',sc['narration'],'']
  texts=list(dict.fromkeys(v['text'] for im in sc['images'] for v in im['visible_text']))
  lines += ['**Chữ minh họa được phép:** '+(' · '.join('“'+t+'”' for t in texts) if texts else 'Không thêm chữ.'),'',f"**Hình dự kiến:** {len(sc['images'])}"+('; cặp hình giữ góc cho thay đổi trước/sau.' if len(sc['images'])>1 else '; tập trung quan hệ, vật hoặc hành động của cảnh.'),'']
  pause=sc['audio_direction']['vi']['learner_pause_seconds']
  if pause:lines += [f'**Chờ {pause} giây cuối cảnh** để người xem trả lời; phản hồi ở cảnh kế tiếp.','']
 reader='\n'.join(lines)+'\n';(OUT/e['reader_path']).write_text(reader);full += [line.replace('(../reviews/','(reviews/') for line in lines]+['---','']
 assert all(s['narration'] in reader for s in c['scenes'])
 verification.append({'job':e['job'],'number':e['number'],'revision':1,'reader_matches_all_scenes':True,'saved_revision_matches_draft':True,'content_sha256':e['content_sha256']})
(OUT/'KICH-BAN-331.md').write_text('\n'.join(full)+'\n');(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(OUT/'export-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
alias=json.loads((OUT/'covered-aliases.json').read_text())
lines=['# Các mục cùng nghĩa đã có kịch bản','','Chín mục trong danh sách ban đầu có cùng từ/loại từ/nghĩa với bài đã viết. Dẫn về bản cũ, không tạo bài trùng. Có bản đọc không đồng nghĩa đã duyệt hoặc sản xuất.','','| Mục còn lại | Mục đã có | Kịch bản |','|---|---|---|']
for e in alias:
 assert (OUT/e['existing_reader']).is_file()
 lines.append(f"| {e['id']} | {e['covered_by_id']} | [{e['word']}]({e['existing_reader']}) |")
(OUT/'CAC-MUC-DA-CO.md').write_text('\n'.join(lines)+'\n')
secs=[e['estimated_seconds'] for e in m];imgs=sum(e['planned_images'] for e in m);scenes=sum(e['scene_count'] for e in m)
lines=['# Hoàn tất kịch bản cho phần A1 còn lại — bài 441–771','','**331/331 bài mới có content revision 1 và đang chờ người dùng duyệt.**','','[Đọc toàn bộ 331 kịch bản](KICH-BAN-331.md) · [Chín mục dẫn về bài đã có](CAC-MUC-DA-CO.md) · [Kiểm tra nội dung](KIEM-TRA-NOI-DUNG.md) · [Ghi chú nguồn](source-notes.md)','','Lô này tiếp nối bài 341–440 đã duyệt. Phạm vi chốt ban đầu gồm 340 mục A1 còn lại: 331 bài mới và 9 mục cùng nghĩa đã có kịch bản. Không sửa hoặc đánh dấu ledger thủ công.','','## Kết quả','',f'- {scenes} cảnh; {imgs} hình trong kế hoạch, gồm {imgs-scenes} biến thể trước/sau. Chưa tạo hình.',f'- Thời lượng điểm ước tính {min(secs):.1f}–{max(secs):.1f} giây; trung bình {sum(secs)/len(secs):.1f} giây. Sai số vẫn cần đo trên WAV thật.', '- Lời dẫn giữ tiếng Việt hỗ trợ người đầu A1, câu mẫu đúng tiếng Anh; một cách dùng được chọn, hai mẫu có liên hệ, một lượt thực hành và phản hồi.', '- Mascot CH01 là nhân vật chính; kế hoạch giữ ảnh tham chiếu chuẩn và khoảng chờ cuối cảnh thực hành.', '- Bài mới chưa được người dùng duyệt. Duyệt lô trước không áp dụng tự động cho lô này.','','## Nhóm thời lượng','','| Nhóm | Số bài | Số cảnh/bài | Khoảng brief | Điểm ước tính |','|---|---:|---:|---|']
for band,label in [('short','Ngắn'),('medium','Trung bình'),('long','Dài')]:
 group=[e for e in m if e['learning_plan']['duration_band']==band];d=group[0]['learning_plan']['duration'];v=[e['estimated_seconds'] for e in group];lines.append(f"| {label} | {len(group)} | {group[0]['scene_count']} | {d['min_seconds']}–{d['max_seconds']} giây | {min(v):.1f}–{max(v):.1f} giây |")
lines+=['','## Làm rõ cách dùng','', '- login.v giữ mã kho nhưng bài 469 dùng dạng động từ log in; o’clock giữ đúng đầu mục nhưng mã job không có dấu nháy.', '- just chọn nghĩa vừa mới; on chọn bề mặt; for chọn người nhận; by chọn phương tiện. Không trộn các nghĩa khác trong cùng bài.', '- near tính từ luyện is near/is quite near. a/an chọn theo âm đầu của từ kế tiếp, không chỉ chữ đầu.', '- Hai mục fact giữ ngữ cảnh khoa học và thường ngày theo kho; nghĩa lõi chồng lấn, không dạy thành hai nghĩa loại trừ nhau.', '- Holiday kỳ nghỉ được viết riêng; bài holiday cũ nói ngày lễ, nên không coi là trùng nghĩa.','','## Danh sách','','| Bài | Từ / cách dùng | Bản đọc | Dự kiến | Duyệt |','|---|---|---|---:|---|']
for e in m:lines.append(f"| {e['number']} | {e['teaching_form']} — {e.get('selected_gloss_vi',e['gloss_vi'])} | [{e['title']}]({e['reader_path']}) | {e['estimated_seconds']} giây | [r1]({e['review']}) |")
lines+=['','## Trạng thái','', '- Chỉ hoàn tất hồ sơ kịch bản; media/video vẫn pending. Chưa tạo âm thanh, ảnh hoặc video cho lô này.', '- Bản đọc chép nguyên văn lời dẫn từ revision đã lưu; bản JSON sao chép được đối chiếu checksum với bản gốc.', '- Kiểm tra cấu trúc không thay cho duyệt chất lượng, không chứng minh giữ chân hoặc hiệu quả học khi chưa có dữ liệu đăng thật.', '- Chưa commit/push lô này.']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print('Exported',len(m),'readers;',scenes,'scenes;',imgs,'planned images; estimate',min(secs),max(secs),round(sum(secs)/len(secs),1))
