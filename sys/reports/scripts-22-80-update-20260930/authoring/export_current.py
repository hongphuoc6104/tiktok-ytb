import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SYS=ROOT/'sys'
OUT=Path(__file__).resolve().parents[1]
rows=json.loads((OUT/'updated-manifest.json').read_text())
assert len(rows)==59
checks=[]
index=['# Kịch bản bài 22–80 đã cập nhật — 30/09/2026','',
 'Đủ 59 kịch bản mới đã lưu qua workflow. Bài 22–30: content revision 1; bài 31–80: content revision 2. Tất cả đang chờ duyệt đúng revision. Media và video chưa chạy.',
 '', 'Lời dẫn Việt, tỷ lệ 9:16; câu mẫu tiếng Anh nằm trong lời dẫn. Thời lượng bên dưới chỉ là ước tính trung tâm theo hồ sơ tốc độ hiện có, đã gồm khoảng chờ người học; chưa đo WAV thật.',
 '', '| Bài | Từ | Tên kịch bản | Mục tiêu | Ước tính | Revision | Bản đọc | Review |', '|---|---|---|---|---|---|---|---|']
combined=['# Toàn bộ lời dẫn mới bài 22–80','', 'Bản đọc này khớp content revision đã lưu. Các ghi chú về khoảng chờ không phải lời đọc; runtime lấy learner_pause_seconds từ JSON. Chưa có WAV thật.','']
for r in rows:
 job=r['job']; rev=r['content_revision']; source=SYS/'runs'/job/'revisions/content'/str(rev)/'content.json'
 c=json.loads(source.read_text()); draft=json.loads((SYS/'runs'/job/'draft/content.json').read_text())
 assert c==draft
 assert c['brief_revision']==r['brief_revision']
 assert r['checks_passed'] and r['content_state']=='awaiting_review'
 stem=f"{r['number']:02}-{r['word'].replace(' ','-')}"
 for dirname in ['kich-ban','content','briefs','loi-dan','audio-plan']:(OUT/dirname).mkdir(exist_ok=True)
 (OUT/'content'/f'{stem}.json').write_text(source.read_text())
 bref=SYS/'runs'/job/'briefs'/f"{r['brief_revision']}.json"
 (OUT/'briefs'/f'{stem}.json').write_text(bref.read_text())
 lines=[f"# {r['number']}. {r['word']} — {r['title']}",'',f"Nghĩa chọn: **{r['selected_gloss']}**.",f"Job: `{job}` · content **r{rev}** · brief **r{r['brief_revision']}** · **chờ duyệt**.",f"Mục tiêu {r['requested_duration']['target_seconds']} giây; ước tính trung tâm {r['estimated_seconds']:.1f} giây. Khoảng bất định {r['estimate_range'][0]}–{r['estimate_range'][1]} giây, chưa đo WAV.",f"5 cảnh · {r['images']} hình/nhịp logic · giọng Việt và câu mẫu Anh · 9:16.",f"[Review revision hiện tại]({r['review_path']})",'']
 combined += [f"## {r['number']}. {r['word']} — {r['title']}",'',f"Content r{rev} · mục tiêu {r['requested_duration']['target_seconds']}s · ước tính {r['estimated_seconds']:.1f}s · nghĩa: {r['selected_gloss']}",'']
 audio=[]
 for s in c['scenes']:
  pause=s['audio_direction']['vi']['learner_pause_seconds']
  section=[f"## {s['id']} — {s['title']}",'',s['narration'],'']
  if pause:section += [f"Khoảng yên lặng cuối cảnh: **{pause} giây** để người học trả lời. Ghi chú này không phải lời đọc.",'']
  lines+=section;combined+=section
  lines += [f"Hình dự kiến: {len(s['images'])}; các nhịp neo vào lời đã chốt. Chi tiết prompt và chữ được phép nằm trong [content JSON](../content/{stem}.json).",'']
  audio.append({'scene_id':s['id'],'narration':s['narration'],'learner_pause_seconds':pause,'intent':s['audio_direction']['vi']['intent'],'pronunciation_notes':s['audio_direction']['vi']['pronunciation_notes']})
 (OUT/'kich-ban'/f'{stem}.md').write_text('\n'.join(lines)+'\n')
 (OUT/'loi-dan'/f'{stem}.txt').write_text('\n\n'.join(s['narration'] for s in c['scenes'])+'\n')
 (OUT/'audio-plan'/f'{stem}.json').write_text(json.dumps({'job':job,'content_revision':rev,'language':'vi','status':'awaiting_content_review_not_synthesized','duration_target_seconds':r['requested_duration']['target_seconds'],'scenes':audio,'note':'Tạo âm thanh qua workflow sau duyệt content; không bỏ khoảng yên lặng và không đọc intent/pronunciation_notes thành lời.'},ensure_ascii=False,indent=2)+'\n')
 r['reader_path']=str(OUT/'kich-ban'/f'{stem}.md');r['content_path']=str(OUT/'content'/f'{stem}.json');r['brief_path']=str(OUT/'briefs'/f'{stem}.json');r['narration_sha256']=hashlib.sha256('\n'.join(s['narration'] for s in c['scenes']).encode()).hexdigest()
 index.append(f"| {r['number']} | {r['word']} | {r['title']} | {r['requested_duration']['target_seconds']}s | {r['estimated_seconds']:.1f}s | r{rev} | [Đọc](kich-ban/{stem}.md) | [Review]({r['review_path']}) |")
 checks.append({'job':job,'revision':rev,'copy_equals_saved_revision':True,'draft_equals_saved_revision':True,'brief_revision':c['brief_revision'],'images':r['images'],'narration_sha256':r['narration_sha256']})
index += ['', '## Phần đã cập nhật','', '- Brief mới qua revise-brief: một nghĩa, mục tiêu học, thời lượng 55–65 / 75–85 / 95–105 giây, hai ví dụ và tiêu chí thực hành.', '- Lời dẫn đã chốt, coverage và anchor tạo lại nguyên văn; đủ phản hồi revision cho các bài sửa.', '- Hình và beats thể hiện hành động/quan hệ/bộ phận; mascot chuẩn, hình phụ cho giải phẫu và quan hệ gia đình. Base scene reference dùng cho biến thể kế thừa cùng cảnh.', '- Lượt nhớ lại ở cảnh 4, có 4–5 giây yên lặng; cảnh 5 cho đáp án và payoff. Chữ gợi ý không đánh dấu đáp án đúng trước khi người học trả lời.', '- Chưa đổi giọng, tốc độ, công cụ, mã kho, ledger hoặc cấu hình sản xuất.', '', '## File dùng sau này','', '- [Toàn bộ lời dẫn](KICH-BAN-22-80.md).', '- `content/`: bản JSON khớp revision đã lưu, gồm lời dẫn, hình, chữ và neo.', '- `briefs/`: bản sao brief hiện tại.', '- `loi-dan/`: chỉ lời đọc, tách cảnh bằng dòng trống; không chứa chỉ dẫn âm thanh.', '- `audio-plan/`: lời từng cảnh và khoảng chờ tương ứng để đối chiếu, không thay workflow.', '', '## Bước tiếp theo','', 'Người dùng duyệt content theo revision hiện tại. Sau quyết định hợp lệ, chạy media qua workflow để tạo WAV/ảnh; đo và nghe WAV thật, kiểm tra ảnh, phụ đề và timeline trước khi duyệt media rồi dựng video. Không coi ước tính hoặc check-draft là duyệt chất lượng.', '', 'Sự đồng ý trước đó trong chat áp dụng hướng chỉnh ý tưởng. Chưa dùng lời đồng ý trước khi các revision này tồn tại để tự ghi duyệt cho lời dẫn mới.']
(OUT/'README.md').write_text('\n'.join(index)+'\n')
(OUT/'KICH-BAN-22-80.md').write_text('\n'.join(combined)+'\n')
(OUT/'updated-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(OUT/'export-verification.json').write_text(json.dumps({'count':len(checks),'status':'passed','checks':checks,'quality_approval':'pending','media_artifacts':'not_created'},ensure_ascii=False,indent=2)+'\n')
print(f'Đã xuất và đối chiếu {len(checks)} kịch bản với revision đã lưu.')
