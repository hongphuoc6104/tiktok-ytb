from pathlib import Path
import json,re,shutil,hashlib,subprocess,statistics
root=Path.cwd();p=root/'reports/scripts-60-20260929';m=json.loads((p/'manifest.json').read_text())
for folder in ['kich-ban','content','briefs','reviews']: (p/folder).mkdir(exist_ok=True)
intro='''# 60 kịch bản A1 tiếp theo — bài 81–140\n\nMục tiêu khoảng 55 giây, linh hoạt theo nội dung trong brief 35–75 giây. Lời dẫn tiếng Việt, câu mẫu tiếng Anh; dự kiến khung dọc 9:16.\n\nĐã nộp content revision 1 cho 60 bài và dừng chờ người dùng duyệt. Chưa tạo âm thanh, hình ảnh hoặc video. Kiểm tra kỹ thuật không phải phê duyệt chất lượng. Thời gian trong tài liệu là ước tính, đã tính khoảng chờ trả lời, chưa đo WAV.\n\nĐợt này áp dụng hướng dẫn độ dài mới: viết theo ý và hành động; số ký tự là thông tin tham khảo, không phải trần sáng tạo. Không kéo dài để vượt 256, không cắt ý bắt buộc để dưới 256. Mỗi bài có hai câu mẫu liên hệ, câu hỏi cuối cảnh 4, khoảng chờ trước phản hồi cảnh 5.\n\nChỉ đọc phần “Lời dẫn”. Mô tả hình, chữ học, mốc dự kiến và khoảng chờ là ghi chú sản xuất. Mascot CH01 giữ đầu tròn trắng, mắt oval đen, một thân, áo xanh #8CCFE8. Các ảnh được nhắc tới chỉ là kế hoạch, chưa sinh ảnh thật.\n'''
table=['| Bài | Từ | Câu chuyện | Dự kiến | Bản đọc | Duyệt content |','|---|---|---|---|---|---|'];sections=[];stats=[]
for e in m:
 n=e['number'];j=e['job'];w=e['word'];run=json.loads((p/'operations-local'/f'{n}-run-content.json').read_text());assert run['state']=='awaiting_review' and run['revision']==1
 r=subprocess.run(['.venv/bin/python','pilot.py','status',j],capture_output=True,text=True,check=True);status=json.loads(r.stdout);(p/'operations-local'/f'{n}-status-final.json').write_text(r.stdout);st={s['stage']:s for s in status['stages']};assert st['content']['state']=='awaiting_review';assert st['media']['state']==st['video']['state']=='pending'
 src=root/'runs'/j/'revisions/content/1/content.json';c=json.loads(src.read_text());assert hashlib.sha256('\n'.join(s['narration'] for s in c['scenes']).encode()).hexdigest()==e['narration_sha256']
 meta=json.loads((src.parents[2]/'brief-current.json').read_text()) if False else json.loads((root/'runs'/j/'brief-current.json').read_text())
 brief=root/'runs'/j/'briefs'/f"{meta['revision']}.json";stem=f"{n:03}-{w.replace(' ','-')}";cf=p/'content'/f'{stem}.json';bf=p/'briefs'/f'{stem}.json';rf=p/'reviews'/f'{stem}-review.md';reader=p/'kich-ban'/f'{stem}.md'
 shutil.copyfile(src,cf);shutil.copyfile(brief,bf)
 # Preserve exact pipeline review, with only portable link destinations in this publication copy.
 rev=Path(run['review']).read_text();rev=rev.replace(str(src),'../content/'+cf.name).replace(str(brief),'../briefs/'+bf.name)
 rev=re.sub(r'\[([^\]]+)\]\(/home/[^)]+\)',r'\1 (artifact local; xem mã job)',rev)
 rf.write_text(rev)
 report=json.loads((p/'operations-local'/f'{n}-check-draft-before-run.json').read_text());t=report['duration_estimate']['languages']['vi'];total=sum(s['seconds'] for s in t['scenes']);pause=c['scenes'][3]['audio_direction']['vi']['learner_pause_seconds']
 lines=[f"# {n}. {w} — {e['title']}",'',f"**Kết quả học:** {e['objective']}",'',f"**Mã mục:** `{e['id']}` · **Job:** `{j}` · **Content revision 1, chờ duyệt.**",'',f"**Dự kiến:** khoảng {round(total)} giây; khoảng bất định {round(t['min'])}–{round(t['max'])} giây. Có {pause} giây chờ trả lời; chưa đo âm thanh.",'',f'[Bản duyệt content](../reviews/{rf.name}) · [Nội dung có cấu trúc](../content/{cf.name}) · [Brief hiện tại](../briefs/{bf.name})','']
 cursor=0
 for i,(sc,tm) in enumerate(zip(c['scenes'],t['scenes']),1):
  end=cursor+tm['seconds'];lines += [f'## Cảnh {i}','',f'**Nhịp dự kiến:** {round(cursor)}–{round(end)} giây.','',f"**Hình dự kiến:** {sc['action']}",'',f"**Lời dẫn:** {sc['narration']}",'']
  txt=[x['text'] for x in sc['images'][0]['visible_text']]
  if txt:lines += ['**Chữ học dự kiến:** '+' · '.join(txt),'']
  if len(sc['images'])>1:
   lines += ['**Biến đổi cần nhìn thấy:** '+sc['images'][0]['change']+' → '+sc['images'][1]['change'],'','**Giữ cùng góc và cảnh nền.** Hình sau dùng hình trước làm tham chiếu nền, cùng tham chiếu mascot.','']
  if i==4:lines += [f'**Giữ im lặng {pause} giây sau câu hỏi.** Đáp án chỉ xuất hiện khi sang cảnh 5. Khoảng chờ này là yêu cầu cho lần tạo âm thanh sau.','']
  cursor=end
 reader.write_text('\n'.join(lines));sections.append('\n'.join(lines).replace('# ','## ',1).replace('(../','('))
 table.append(f"| {n} | {w} | {e['title']} | ~{round(total)} giây | [Đọc](kich-ban/{reader.name}) | [R1](reviews/{rf.name}) |")
 e.update(content_revision=1,content_state='awaiting_review',reader_path=f'kich-ban/{reader.name}',content_path=f'content/{cf.name}',brief_path=f'briefs/{bf.name}',review_path=f'reviews/{rf.name}',local_review_path=f'runs/{j}/reviews/content/1/review.md',estimated_seconds=round(total,1),estimate_range_seconds=[t['min'],t['max']],pause_seconds=pause)
 media=[f for f in (root/'runs'/j).rglob('*') if f.is_file() and f.suffix.lower() in ['.png','.jpg','.webp','.mp3','.wav','.mp4']];assert not media
 stats.append(dict(number=n,word=w,revision=1,estimated_seconds=round(total,1),pause_seconds=pause,images_planned=sum(len(s['images']) for s in c['scenes']),longest_scene_chars=max(len(s['narration']) for s in c['scenes']),warnings=report['duration_estimate']['warnings']))
 print(n,w,'đã xác nhận',flush=True)
summary=dict(scripts=len(m),scenes=len(m)*5,planned_images=sum(s['images_planned'] for s in stats),estimated_min=min(s['estimated_seconds'] for s in stats),estimated_max=max(s['estimated_seconds'] for s in stats),estimated_mean=round(statistics.mean(s['estimated_seconds'] for s in stats),1),content_revision=1,quality_approval='pending_user_review',media_files_created=0,all_media_video_pending=True,protected_files_modified_by_this_task=False)
before=json.loads((p/'operations-local/protected-before.json').read_text());changed=[n for n,h in before.items() if not Path(n).is_file() or hashlib.sha256(Path(n).read_bytes()).hexdigest()!=h];summary['previously_inventoried_protected_files_changed']=changed;assert not changed,changed
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(p/'kiem-tra-ban-thao.json').write_text(json.dumps(dict(summary=summary,scripts=stats),ensure_ascii=False,indent=2)+'\n')
(p/'KICH-BAN-60.md').write_text(intro+'\n## Mục lục\n\n'+'\n'.join(table)+'\n\n---\n\n'+'\n\n---\n\n'.join(sections))
(p/'README.md').write_text(intro+f"\n**Kiểm tra:** đủ 60 bài/300 cảnh; {summary['planned_images']} hình dự kiến gồm 12 biến thể trước–sau; 60 bài đạt kiểm tra cấu trúc. Thời lượng trung tâm ước tính {summary['estimated_min']}–{summary['estimated_max']} giây, trung bình {summary['estimated_mean']} giây. Không còn lỗi cấu trúc; chất lượng lời kể chờ duyệt.\n\n[Đọc toàn bộ 60 kịch bản](KICH-BAN-60.md).\n\n"+'\n'.join(table)+'''\n\n## Ghi chú kho từ và bản duyệt\n\nNăm brief được làm rõ qua revise-brief vì ghi chú nghĩa anh em trùng/chồng lấn với chính nghĩa được chọn: healthy, strong, sick, free, waiter. Giữ nguyên mã mục, không sửa bank hay file bảo vệ. Xem [chi tiết làm rõ brief](brief-clarifications.json). Lỗi trùng toàn kho chưa được sửa trong đợt này.\n\nCác file trong content/ và briefs/ là bản sao nguyên văn revision hiện tại; reviews/ là bản sao review.md của pipeline, chỉ đổi liên kết artifact sang đường dẫn đọc được trong gói này. Bản gốc trong runs/ giữ nguyên. Bản đọc lấy lời dẫn trực tiếp từ content revision 1.\n\nCác job mới dừng ở content; không duyệt thay người dùng, không tạo media, không mark hoàn thành video. Không cập nhật 50 job cũ đang lệch integrity. Việc tiếp tục job trên máy khác cần dữ liệu vận hành và quy trình integrity riêng; các bản JSON trong gói là tài liệu bàn giao, không phải bản sao SQLite.\n''')
print(json.dumps(summary,ensure_ascii=False,indent=2))
