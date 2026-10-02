from pathlib import Path
import json, hashlib

p = Path(__file__).resolve().parents[3]
out = p / 'reports/scripts-100-341-440-20260930'
note = 'tôi đã đọc và duyệt qua, cập nhật đi'
m = json.loads((out / 'manifest.json').read_text())
results = json.loads((out / 'approval-results.json').read_text())
assert len(m) == len(results) == 100
assert all(e['state'] == 'approved' and e['content_revision'] == 1 for e in m)
(out / 'decisions').mkdir(exist_ok=True)
verified = []
for e, r in zip(m, results):
    assert e['job'] == r['job'] and r['note'] == note
    job = p / 'runs' / e['job']
    src = job / 'revisions/content/1/content.json'
    assert src.read_bytes() == (out / e['content_path']).read_bytes()
    assert hashlib.sha256(src.read_bytes()).hexdigest() == e['content_sha256']
    decision_path = job / 'reviews/content/1/decision.json'
    d = json.loads(decision_path.read_text())
    assert d['approved'] and d['actor'] == 'user' and d['note'] == note
    assert r['media'] == r['video'] == 'pending'
    dest = out / 'decisions' / Path(e['content_path']).name
    dest.write_bytes(decision_path.read_bytes())
    assert dest.read_bytes() == decision_path.read_bytes()
    reader = out / e['reader_path']
    text = reader.read_text()
    old = '**Trạng thái:** content revision 1, chờ duyệt.'
    new = '**Trạng thái:** content revision 1, đã được người dùng duyệt.'
    assert old in text
    text = text.replace(old, new)
    c = json.loads(src.read_text())
    assert all(s['narration'] in text for s in c['scenes'])
    reader.write_text(text)
    e['approval_note'] = note
    e['decision_copy'] = 'decisions/' + dest.name
    verified.append({'job': e['job'], 'number': e['number'], 'revision': 1,
                     'state': 'approved', 'actor': 'user', 'note': note,
                     'content_sha256': e['content_sha256'], 'reader_matches': True,
                     'decision_copy_matches': True, 'media': 'pending', 'video': 'pending'})

f = out / 'KICH-BAN-100.md'
s = f.read_text()
old = 'Tất cả content revision 1 trong lô này chờ người dùng duyệt riêng. Duyệt các lô trước không áp dụng cho lô mới.'
assert old in s
s = s.replace(old, 'Tất cả 100 content revision 1 trong lô này đã được người dùng duyệt ngày 30/09/2026. Phản hồi nguyên văn: “' + note + '”.')
old = '**Trạng thái:** content revision 1, chờ duyệt.'
assert s.count(old) == 100
f.write_text(s.replace(old, '**Trạng thái:** content revision 1, đã được người dùng duyệt.'))

f = out / 'README.md'
s = f.read_text()
old = '**100/100 content revision 1 đã nộp, chờ người dùng duyệt. Chưa chạy media/video.**'
assert old in s
s = s.replace(old, '**100/100 content revision 1 đã được người dùng duyệt ngày 30/09/2026. Media/video vẫn pending.**\n\n[Biên bản duyệt](DA-DUYET.md) · [Đối chiếu quyết định duyệt](approval-verification.json)')
s = s.replace('| [r1](', '| [r1 đã duyệt](')
f.write_text(s)

f = out / 'KIEM-TRA-NOI-DUNG.md'
s = f.read_text().replace('[đối chiếu cuối](final-verification.json)', '[đối chiếu trước khi duyệt](final-verification.json)').replace('Tất cả chờ người dùng duyệt; media/video đều pending. Đây là kiểm tra kỹ thuật và biên tập, chưa phải người dùng duyệt.', 'Người dùng đã duyệt cả 100 content revision 1 ngày 30/09/2026; media/video đều pending. Quyết định của người dùng được lưu riêng với kiểm tra kỹ thuật và biên tập.')
s += '\n[Biên bản duyệt](DA-DUYET.md) · [Đối chiếu quyết định duyệt](approval-verification.json).\n'
f.write_text(s)
(out / 'DA-DUYET.md').write_text('# Đã duyệt — lô 341–440\n\nNgày ghi nhận: 30/09/2026.\n\nPhản hồi nguyên văn của người dùng:\n\n> ' + note + '\n\nĐã ghi nhận qua workflow cho đúng 100 content revision 1, từ north đến band, sau khi đối chiếu nội dung với bản đã bàn giao. Cả 100 phần media và video vẫn pending. Lời dẫn đã duyệt được giữ nguyên.\n\n[Bằng chứng ghi nhận duyệt](approval-results.json) · [Đối chiếu quyết định duyệt](approval-verification.json) · [Danh sách kịch bản](README.md)\n')
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
(out / 'approval-verification.json').write_text(json.dumps(verified, ensure_ascii=False, indent=2) + '\n')
print('Updated 100 readers and approval records; narration unchanged; media/video pending')
