from pathlib import Path
import json,hashlib,csv,collections
p=Path(__file__).resolve().parents[3];out=p/'reports/scripts-100-20260929';m=json.loads((out/'manifest.json').read_text())
for sub in ['kich-ban','content','briefs','reviews']:(out/sub).mkdir(exist_ok=True)
full=['# 100 kịch bản tiếp theo — bài 141–240','', 'Mục tiêu khoảng 55 giây. Thời lượng trong tài liệu là ước tính, chưa đo WAV. Chỉ content; chưa tạo âm thanh, ảnh hoặc video.','', 'A: mở bằng tình huống. B: mở bằng câu tiếng Anh dùng ngay. Chưa có số liệu chứng minh cách nào hiệu quả hơn.','']
for e in m:
 j=p/'runs'/e['job'];rev=e.get('content_revision');src=j/f'revisions/content/{rev}/content.json' if rev else j/'draft/content.json';c=json.loads(src.read_text());slug=f"{e['number']}-{e['word'].replace(' ','-')}";meta=json.loads((j/'brief-current.json').read_text());bp=j/f"briefs/{meta['revision']}.json"
 (out/'content'/f'{slug}.json').write_bytes(src.read_bytes());(out/'briefs'/f'{slug}.json').write_bytes(bp.read_bytes())
 lines=[f"# {e['number']}. {e['word']} — {e['title']}",'',f"**Nghĩa:** {e['gloss_vi']}. **Mục tiêu:** {e['objective']}",'',f"**Diễn tiến:** {e['plot']}",'',f"**Kiểu mở:** {'B — câu dùng ngay' if e['opening_type'].startswith('B') else 'A — tình huống'}. **Thời lượng dự kiến:** {e['estimated_seconds']} giây. **Nhân vật chính:** mascot áo xanh chuẩn.",'',f"**Trạng thái:** {'content revision '+str(rev)+(', đã được người dùng duyệt' if e.get('state')=='approved' else ', chờ duyệt') if rev else 'bản nháp chưa nộp'}. Mã bài: `{e['job']}`.",'']
 if rev:
  review=Path(e['review']);relative=f'reviews/{slug}.md';(out/relative).write_bytes(review.read_bytes());lines+=['[Bản duyệt gốc]('+str(review)+')','']
 for sc in c['scenes']:
  lines += [f"## {sc['id']} — {sc['title'].split(' — ')[-1]}",'',sc['narration'],'']
  texts=list(dict.fromkeys(t['text'] for im in sc['images'] for t in im['visible_text']));lines+=['Chữ minh họa cho phép: '+('; '.join('“'+t+'”' for t in texts) if texts else 'không có')+'.','',f"Kế hoạch: {len(sc['images'])} hình; "+('có biến thể giữ góc máy để thể hiện thay đổi.' if len(sc['images'])>1 else 'giữ trọng tâm vào hành động hoặc đồ vật của lời dẫn.'),'']
  if sc['audio_direction']['vi']['learner_pause_seconds']:lines+=['**Chờ người xem trả lời: 5 giây cuối cảnh. Đáp án ở cảnh tiếp theo.**','']
 (out/'kich-ban'/f'{slug}.md').write_text('\n'.join(lines)+'\n');full+=lines+['---','']
 e.update(reader_path=f'kich-ban/{slug}.md',content_path=f'content/{slug}.json',brief_path=f'briefs/{slug}.json',content_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
(out/'KICH-BAN-100.md').write_text('\n'.join(full)+'\n');(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
approved=sum(x.get('state')=='approved' for x in m);complete=sum(x.get('content_revision')==1 for x in m);groups=collections.Counter(x['opening_type'] for x in m)
lines=['# 100 kịch bản A1 tiếp theo — full đến teach','',f'Đã nộp: **{complete}/100 content revision 1**. Đã duyệt: **{approved}/100**. Chưa chạy media/video.','', 'Bài 141–240 nối tiếp 140 kịch bản đã có, không phải làm lại các job đang bị chặn. Kho giữ chỗ qua bank.py start, không sửa ledger thủ công. Bỏ qua free.adj.gratis và classmate.n.peer vì trùng nghĩa với bài đã có.','', '[Đọc toàn bộ 100 kịch bản](KICH-BAN-100.md) · [Theo dõi số liệu sau đăng](THEO-DOI-SO-LIEU.csv)','', '## Những gì có trong lô','', '- 100 bài, 500 cảnh; hai câu mẫu khác nhau trong từng bài, tình huống liên quan và lượt thực hành có đáp án.','- 54 bài mở tình huống, 46 bài mở câu dùng ngay; không ép mọi từ vào cùng một kiểu mở.','- Khoảng chờ 5 giây ở cuối cảnh thực hành; cần nghe WAV thật để kiểm tra nhịp sau này.','- 530 hình dự kiến, trong đó 30 biến thể giữ góc máy. Chưa tạo ảnh; mascot CH01 luôn áo xanh chuẩn, quần áo học được thể hiện bằng vật riêng hoặc nhân vật phụ.','- Thời lượng dự kiến 52,6–59,5 giây, trung bình khoảng 56,5 giây; không phải số đo âm thanh và không bảo đảm giữ chân.','- Brief wear, take off, learn được sửa riêng chỉ dẫn tránh nghĩa trùng qua revise-brief, giữ nguyên mã mục và phạm vi. Xem brief-clarifications.json.','', '## Danh sách và bản duyệt','', '| Số | Từ / nghĩa | Kịch bản | Dự kiến | Duyệt |','|---|---|---|---|---|']
for e in m:
 review='[r1]('+e['review']+')' if e.get('content_revision') else 'chưa nộp'
 lines.append(f"| {e['number']} | {e['word']} — {e['gloss_vi']} | [{e['title']}]({e['reader_path']}) | {e['estimated_seconds']} giây | {review} |")
lines+=['','## Đo sau đăng','', 'Ghi URL, ngày giờ đăng, độ dài MP4 thật và số liệu ở cùng mốc 24h/72h. Để trống chỉ số nền tảng không hiển thị. So sánh giữ chân đầu, thời gian xem và tỷ lệ hoàn thành có xét thời lượng; lưu/chia sẻ/follower là thông tin bổ sung.','', 'Các bài khác chủ đề và thời điểm nên đây là thử nghiệm thăm dò, không phải A/B có kiểm soát. Chưa có dữ liệu mới về tệp người xem; người Việt học A1 là đối tượng mục tiêu theo brief. Không suy ra hiệu quả học chỉ từ lượt xem.','', '## Trước sản xuất','', 'Chỉ các bài có trạng thái approved trong manifest mới đủ điều kiện sang media. Giữ các gate media/video và kiểm tra ảnh, WAV, MP4 thật. Chưa commit/push lô này.']
(out/'README.md').write_text('\n'.join(lines)+'\n')
with (out/'THEO-DOI-SO-LIEU.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['so_bai','tu','nghia','kieu_mo','job','revision','url','ngay_gio_dang','thoi_luong_thuc_giay','moc_do','luot_xem','giu_chan_2s_phan_tram','giu_chan_3s_phan_tram','giu_chan_5s_phan_tram','xem_trung_binh_giay','xem_het_phan_tram','luot_luu','chia_se','follower_moi','ghi_chu'])
 for e in m:
  for t in ['24h','72h']:w.writerow([e['number'],e['word'],e['gloss_vi'],e['opening_type'],e['job'],e.get('content_revision') or '','','','',t]+['']*10)
print('Exported 100 readers;',complete,'submitted')
