from pathlib import Path
import json,re,subprocess,hashlib,shutil,statistics
root=Path.cwd();p=root/'reports/scripts-50-20260929';m=json.loads((p/'manifest.json').read_text());(p/'kich-ban').mkdir(exist_ok=True);(p/'content').mkdir(exist_ok=True)
intro='''# 50 kịch bản từ vựng A1 tiếp theo — bài 31–80\n\nNgày 29/09/2026 · Bản dọc 9:16 theo mặc định kênh · Lời dẫn tiếng Việt, câu mẫu tiếng Anh.\n\nMục tiêu khoảng 55 giây/bài, linh hoạt 35–75 giây. Thời gian dưới đây chỉ là ước tính, đã cộng khoảng chờ trả lời; chưa tạo âm thanh để đo thực tế.\n\n**Trạng thái: đủ 50 bài ở content revision 1, chờ người dùng duyệt.** Kiểm tra cấu trúc đạt không phải quyết định chất lượng. Không tạo âm thanh, hình ảnh hoặc video.\n\nMỗi bài có một nghĩa trọng tâm, hai câu mẫu trong tình huống có liên hệ, một lượt thực hành cuối cảnh 4 và đáp án ở cảnh 5. Chỉ đọc phần “Lời dẫn”; các tiêu đề, mô tả cảnh, chữ học và khoảng chờ là ghi chú sản xuất.\n\nNhân vật chính là CH01, mascot áo xanh biển nhạt #8CCFE8. Những người thân, bạn bè và hình cơ thể minh họa là nhân vật hoặc hình phụ; không đổi tóc, mắt, mũi, tai hay giải phẫu của mascot để minh họa từ mới.\n'''
table=['| Bài | Từ | Câu chuyện | Dự kiến | Bản đọc | Bản duyệt |','|---|---|---|---|---|---|'];sections=[];stats=[]
for e in m:
 j=e['job'];n=e['number'];w=e['word'];result=json.loads((p/f'{n:02}-run-content-local.json').read_text())
 assert result['state']=='awaiting_review' and result['revision']==1
 r=subprocess.run(['.venv/bin/python','pilot.py','status',j],capture_output=True,text=True,check=True);status=json.loads(r.stdout);(p/f'{n:02}-status-final-local.json').write_text(r.stdout)
 stages={s['stage']:s for s in status['stages']}
 assert stages['content']['state']=='awaiting_review' and stages['content']['revision']==1
 assert stages['media']['state']=='pending' and stages['video']['state']=='pending'
 src=root/'runs'/j/'revisions/content/1/content.json';c=json.loads(src.read_text());review=Path(result['review']);assert review.exists()
 assert hashlib.sha256('\n'.join(s['narration'] for s in c['scenes']).encode()).hexdigest()==e['source_sha256']
 check=json.loads((p/f'{n:02}-checks-local.json').read_text());t=check['duration_estimate']['languages']['vi'];total=sum(s['seconds'] for s in t['scenes']);lo=t['min'];hi=t['max']
 stem=f"{n:02}-{w.replace(' ','-')}";f=p/'kich-ban'/f'{stem}.md';jsonout=p/'content'/f'{stem}.json';shutil.copyfile(src,jsonout)
 lines=[f"# {n:02}. {w} — {e['title']}",'',f"**Kết quả học:** {e['objective']}",'',f"**Dự kiến:** khoảng {round(total)} giây; khoảng bất định {round(lo)}–{round(hi)} giây. Bao gồm {e['pause_seconds']} giây chờ trả lời. Chưa đo WAV.",'',f"**Content revision 1 — chờ duyệt.** [Bản duyệt chính thức]({review}) · Mã job: `{j}`",'']
 cursor=0
 for i,(sc,tm) in enumerate(zip(c['scenes'],t['scenes']),1):
  end=cursor+tm['seconds'];lines += [f"## Cảnh {i} — {sc['title']}",'',f'**Nhịp dự kiến:** {round(cursor)}–{round(end)} giây.','',f"**Hình dự kiến:** {sc['action']}",'',f"**Lời dẫn:** {sc['narration']}",'']
  text=[x['text'] for im in sc['images'] for x in im['visible_text']]
  if text:lines += ['**Chữ học dự kiến:** '+' · '.join(text),'']
  hold=sc['audio_direction']['vi']['learner_pause_seconds']
  if hold:lines += [f'**Sau câu hỏi, giữ im lặng {hold} giây.** Giữ hình câu hỏi; chỉ mở đáp án khi sang cảnh 5. Đây là khoảng chờ yêu cầu cho lần tạo âm thanh sau, chưa phải âm thanh đã được tạo.','']
  cursor=end
 lines += ['**Cần kiểm tra khi làm media sau này:** nghe câu mẫu và các âm cuối; xem rõ quan hệ người nói/người được giới thiệu hoặc bộ phận đang chỉ; giữ chữ học dễ đọc và phụ đề tối đa hai dòng. Lần này chưa thực hiện bước nghe/xem media.','']
 f.write_text('\n'.join(lines));sections.append('\n'.join(lines).replace('# ','## ',1))
 table.append(f"| {n:02} | {w} | {e['title']} | ~{round(total)} giây | [Đọc](kich-ban/{stem}.md) | [R1]({review}) |")
 e.update(content_revision=1,content_state='awaiting_review',reader_path=f'kich-ban/{stem}.md',content_path=f'content/{stem}.json',review_path=str(review),estimated_seconds=round(total,1),estimate_range_seconds=[lo,hi],brief_path=f'{n:02}-brief-proposal.json')
 stats.append(dict(number=n,word=w,job=j,revision=1,state='awaiting_review',estimated_seconds=round(total,1),pause_seconds=e['pause_seconds'],scene_count=len(c['scenes']),images_planned=sum(len(s['images']) for s in c['scenes']),longest_narration_chars=max(len(s['narration']) for s in c['scenes']),warnings=check['duration_estimate']['warnings']))
 media=[str(f) for f in (root/'runs'/j).rglob('*') if f.is_file() and f.suffix.lower() in {'.wav','.mp3','.png','.jpg','.webp','.mp4'}];assert not media,(j,media)
 print(n,w,'bản đọc và R1 đã xác nhận',flush=True)
summary=dict(scripts=50,scenes=sum(e['scene_count'] for e in stats),estimated_min=min(e['estimated_seconds'] for e in stats),estimated_max=max(e['estimated_seconds'] for e in stats),estimated_mean=round(statistics.mean(e['estimated_seconds'] for e in stats),1),longest_narration_chars=max(e['longest_narration_chars'] for e in stats),all_content_revision_1_awaiting_review=True,all_media_video_pending=True,media_files_created=0,technical_checks_passed=50,quality_approval='pending_user_review')
(p/'KICH-BAN-50.md').write_text(intro+'\n## Mục lục\n\n'+'\n'.join(table)+'\n\n---\n\n'+'\n\n---\n\n'.join(sections))
(p/'README.md').write_text(intro+f"\n**Kết quả kiểm tra:** 50 bản nháp hợp lệ, 250 cảnh, thời lượng trung tâm ước tính {summary['estimated_min']}–{summary['estimated_max']} giây; trung bình {summary['estimated_mean']} giây. Mọi đoạn lời dẫn không quá {summary['longest_narration_chars']} ký tự. Không còn lỗi cấu trúc được báo; chất lượng nội dung chờ người dùng duyệt.\n\n[Đọc liền 50 kịch bản](KICH-BAN-50.md).\n\n"+'\n'.join(table)+'\n\n## Dữ liệu để tiếp tục\n\n`content/` là bản sao nguyên văn 50 content revision 1 thật, có outline, lời dẫn, nhân vật, mô tả hình, chữ được phép, điểm neo và khoảng chờ. `manifest.json` liên kết mỗi bài với mã mục kho, job, bản đọc và review.md hiện tại. `authoring/` lưu nguồn biên tập; sau khi có revision, mọi chỉnh sửa cần đi qua reject content và revision mới, không sửa bản đã lưu.\n\nCác đường dẫn bản duyệt trỏ tới job local. Bản tổng hợp và các bản đọc riêng vẫn đọc được độc lập. Nội dung kịch bản trong bản đọc được lấy từ revision đã nộp, không phải nguồn lời dẫn khác.\n\nKhông tự duyệt, không đánh dấu mục từ hoàn thành video. Các bài đang dừng ở đúng gate content.\n')
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(p/'kiem-tra-ban-thao.json').write_text(json.dumps(dict(summary=summary,scripts=stats),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
