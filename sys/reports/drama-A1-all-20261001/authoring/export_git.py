from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];OUT=ROOT/'reports/drama-A1-da-chot-20261001';m=json.loads((P/'manifest.json').read_text());ready=[e for e in m if e.get('state')=='awaiting_review_new'];items=[]
for d in ['content','briefs','kich-ban']:(OUT/d).mkdir(parents=True,exist_ok=True)
for e in ready:
 j=e['job'];source=ROOT/'runs'/j/f"revisions/content/{e['new_content_revision']}/content.json";c=json.loads(source.read_text());f=OUT/'content'/f'{j}.json';shutil.copyfile(source,f)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==hashlib.sha256(source.read_bytes()).hexdigest()
 brief=ROOT/'runs'/j/f"briefs/{c['brief_revision']}.json";shutil.copyfile(brief,OUT/'briefs'/f'{j}.json')
 current_reader=Path(e['reader']).read_text();assert all(s['narration'] in current_reader for s in c['scenes'])
 # Portable Git report links; preserved narration, no production artifact changes.
 current_reader=current_reader.replace(f"[Bản duyệt gốc]({e['review']})",f"[Dữ liệu content đã chốt](../content/{j}.json)")
 current_reader='\n'.join(line.rstrip() for line in current_reader.splitlines()).rstrip()+'\n'
 (OUT/'kich-ban'/f'{j}.md').write_text(current_reader)
 items.append({'job':j,'entry_id':e['entry_id'],'word':e.get('teaching_form',e['word']),'selected_gloss_vi':e.get('selected_gloss_vi',e['gloss_vi']),'content_revision':e['new_content_revision'],'brief_revision':c['brief_revision'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'reader':f'kich-ban/{j}.md','content':f'content/{j}.json','brief':f'briefs/{j}.json','workflow_content_state':'awaiting_review','media_created':False})
(OUT/'manifest.json').write_text(json.dumps({'total_in_scope':len(m),'exported':len(items),'not_yet_exported':len(m)-len(items),'user_request':'chốt kịch bản commit và push github sớm đi','note':'Bản xuất kịch bản cho Git theo yêu cầu người dùng. Đây là bản sao content/brief đã lưu; giữ gates và lịch sử workflow, không tự ghi quyết định approve hay tạo media.','scripts':items},ensure_ascii=False,indent=2)+'\n')
lines=['# Kịch bản A1 — dạng phim ngắn','',f'Đã xuất {len(items)}/{len(m)} kịch bản trong phạm vi cập nhật.','', 'Mỗi tập có mở đầu cụ thể, chuyện có nguyên nhân và kết quả, câu tiếng Anh cần dùng trong tình huống, một lượt trả lời có khoảng chờ và đáp án. Giữ đúng nghĩa trong kho, số cảnh và mascot. Thời lượng là dự kiến; chưa đo WAV hoặc hiệu quả giữ chân.','', 'Bài đã có media/video và mục đã hoàn tất được giữ nguyên. Bản xuất chỉ chứa kịch bản, brief và bản đọc.','', 'Yêu cầu người dùng: “chốt kịch bản commit và push github sớm đi”. Trạng thái workflow trong manifest được ghi đúng thực tế; quyết định duyệt production được lưu qua CLI khi áp dụng đúng revision.','', '| Từ/cách dùng | Nghĩa chọn | Bản đọc | Revision |','| --- | --- | --- | --- |']
for e in items:lines.append(f"| {e['word']} | {e['selected_gloss_vi']} | [{e['job']}]({e['reader']}) | content r{e['content_revision']} |")
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
v=json.loads((P/'verification-current.json').read_text())
assert v['updated']==len(items) and not v['errors'] and not v['warnings'] and not v['duplicate_openings'],v
(OUT/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(OUT/'KIEM-TRA.md').write_text('# Kiểm tra bản kịch bản xuất Git\n\nĐã kiểm tra '+str(len(items))+' kịch bản được xuất. Nội dung JSON sao chép nguyên vẹn từ revision đã lưu, có SHA-256 trong manifest. Số cảnh giữ nguyên, lời trong bản đọc khớp bản lưu, neo trích đúng lời chốt, có một khoảng chờ và đáp án ở cảnh sau. Không trùng nguyên câu mở đầu trong tập đã xuất. Lịch sử content ban đầu còn nguyên.\n\nĐây là kiểm tra nội dung/cấu trúc và đối chiếu dữ liệu. Chưa tạo hoặc nghe WAV, xem ảnh hay đo hiệu quả học/giữ chân của các bản này.\n')
print('EXPORTED',len(items),'/',len(m))
