from pathlib import Path
import json, subprocess, time

p = Path(__file__).resolve().parents[3]
o = p / 'reports/scripts-A1-remaining-20260930'
entries = json.loads((o / 'selection.json').read_text())

def call(args):
    for attempt in range(1500):
        r = subprocess.run([str(p / '.venv/bin/python'), *args], cwd=p, capture_output=True, text=True)
        d = json.loads(r.stdout)
        if d.get('blocked') == 'Another operation is running':
            if attempt % 100 == 0:
                print('WAIT', args[0:3], flush=True)
            time.sleep(0.4)
            continue
        if r.returncode or d.get('blocked'):
            raise RuntimeError(r.stdout)
        return d
    raise RuntimeError('Bounded operation wait exhausted')

for e in entries:
    j = e['job']
    root = p / 'runs' / j
    if not root.exists():
        d = call(['vocab/bank.py', 'start', j, '--mode', 'review', '--level', 'A1',
                  '--word', e['word'], '--pos', e['pos'], '--topic', e['topics'][0]])
        (o / 'operations-local' / f"{e['number']}-start.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
    ledger = json.loads((p / 'vocab/ledger.json').read_text())['entries']
    assert ledger[e['id']]['job'] == j, e
    meta = json.loads((root / 'brief-current.json').read_text())
    b = json.loads((root / f"briefs/{meta['revision']}.json").read_text())
    marker = 'Biên tập theo kế hoạch A1 bản 2 ngày 30/09/2026.'
    if marker not in b['planning']['assumptions']:
        assert not (root / 'revisions/content/1/content.json').exists(), j
        b['duration'] = {k: e['learning_plan']['duration'][k] for k in ['min_seconds', 'max_seconds']}
        b['scene_count'] = e['scene_count']
        b['audience'] = 'Người Việt đầu A1, hiểu câu ngắn với hỗ trợ tiếng Việt và tình huống nhìn thấy.'
        b['planning']['assumptions'].append(marker)
        b['planning']['domain_requirements'].append('Giữ một nghĩa và một mục tiêu học; thời lượng tăng thêm chỉ cho ngữ cảnh, cách dùng, lượt thực hành và phản hồi, không thêm nghĩa khác hoặc lời lặp.')
        b['planning']['domain_requirements'].append('Phần giải thích dùng tiếng Anh ngắn, quen thuộc có hỗ trợ tình huống; tiếng Việt chốt điểm khó. Hồ sơ đầu A1 tham khảo 20–35% tiếng Anh trong giải thích, không tính câu mẫu; đây không phải ngưỡng chấm máy.')
        b['planning']['assumptions'].append('Thời lượng dự kiến theo nhóm ' + e['learning_plan']['duration_band'] + '; khoảng chờ nằm trong tổng thời lượng. Chưa đo WAV hay hiệu quả học.')
        if e['id'] == 'login.v':
            for key in ['topic', 'goal']:
                b[key] = b[key].replace('LOGIN', 'LOG IN')
            for r in b['required_points']:
                r['text'] = r['text'].replace('LOGIN', 'LOG IN')
            for key in ['success_criteria', 'domain_requirements']:
                b['planning'][key] = [s.replace('LOGIN', 'LOG IN') for s in b['planning'][key]]
            b['planning']['assumptions'].append('Mã kho login.v được giữ nguyên; dạng động từ chuẩn là log in (Cambridge Dictionary: https://dictionary.cambridge.org/dictionary/english/log-in). Không dạy login như động từ, không thay mục bằng mục A2.')
        if e['id'] in {'near.adj.near-basic', 'right.n.direction'}:
            selected = e['id']
            avoid = []
            for line in b['planning']['avoid']:
                if selected == 'near.adj.near-basic' and 'near.prep' in line:
                    line = 'Không chuyển mục tiêu sang cấu trúc near + địa điểm [near.prep] đã có bài; bài này luyện near đứng trước danh từ trong near end / near side với khoảng cách nhìn thấy.'
                if selected == 'right.n.direction' and 'right.adj.direction' in line:
                    line = 'Không chuyển mục tiêu sang tính từ right đứng trước danh từ trong right hand [right.adj.direction] đã có bài; bài này dùng danh từ chỉ phía trong on the right.'
                avoid.append(line)
            b['planning']['avoid'] = avoid
        candidate = o / 'operations-local' / f"{e['number']}-brief-candidate.json"
        candidate.write_text(json.dumps(b, ensure_ascii=False, indent=2) + '\n')
        d = call(['pilot.py', 'revise-brief', j, '--brief', str(candidate), '--note', 'Áp dụng kế hoạch A1 bản 2 và làm rõ mục tiêu sử dụng trước khi viết kịch bản; giữ mã nghĩa, mode và hồ sơ đã có.'])
        (o / 'operations-local' / f"{e['number']}-revise-brief.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print('PREPARED', e['number'], e['word'], flush=True)
