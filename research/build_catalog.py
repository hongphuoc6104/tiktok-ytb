"""Compile explicitly authored topics; never synthesize title permutations."""
import hashlib
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def normalized(text):
    return re.sub(r'[^\w]+', ' ', unicodedata.normalize('NFKC', text).casefold()).strip()

def build(root=ROOT):
    base = Path(root)/'research'
    registry = json.loads((base/'catalog/sources.json').read_text())
    sources = {x['id']:x for x in registry['sources']}
    entries=[]; groups=[]; seen=set()
    for group_index, block in enumerate((base/'catalog/topics.txt').read_text().split('## ')[1:]):
        lines=block.strip().splitlines()
        slug,name,refs,days=lines[0].split('|')
        refs=refs.split(',')
        if slug=='ai': refs.append('ai-policy')
        assert all(x in sources for x in refs), slug
        assert len(lines[1:])==25, (slug,len(lines)-1)
        groups.append(dict(id=slug,name=name,count=25,source_ids=refs))
        for i,title in enumerate(lines[1:]):
            key=normalized(title)
            if key in seen: raise ValueError('Duplicate title: '+title)
            seen.add(key)
            # Stable across file reordering. Renaming a topic is an editorial migration,
            # not a silent ID reassignment; old reserved IDs must remain in the catalog.
            topic_id='RS-'+hashlib.sha256(key.encode()).hexdigest()[:12]
            kind='so-sanh' if any(w in title.lower() for w in ['khác','so sánh','phân biệt']) else 'huong-dan' if any(w in title.lower() for w in ['cách','kiểm tra','tạo ','lập ','viết ','dùng ','tìm ','chọn ','ghi ','đọc ']) else 'giai-thich'
            entry=dict(id=topic_id,category=slug,category_name=name,title=title,
                editorial_order=i*40+group_index+1,priority=1 if i<5 else 2 if i<15 else 3,
                format=kind,central_question=title,
                scope='Một câu hỏi trong tiêu đề; dùng một ví dụ cụ thể, một giới hạn và một việc người xem có thể làm tiếp. Không mở rộng thành cả khóa học.',
                duration_seconds=[90,180],source_ids=refs,refresh_after_days=int(days),
                evidence_status='needs_topic_factcheck',catalog_checked_on=registry['checked_on'])
            entries.append(entry)
    assert len(entries)==1000 and len({e['id'] for e in entries})==1000
    ledger=json.loads((base/'ledger.json').read_text())
    missing=set(ledger['entries'])-{e['id'] for e in entries}
    if missing: raise ValueError('Catalog edit would orphan ledger IDs: '+str(sorted(missing)))
    (base/'topics').mkdir(exist_ok=True)
    for group in groups:
        (base/'topics'/(group['id']+'.jsonl')).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in entries if x['category']==group['id']))
    (base/'categories.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')
    head='# 1.000 đề tài video nghiên cứu\n\nBiên soạn ngày 22/09/2026. Mỗi video 90–180 giây, giải quyết một câu hỏi. Đây là kho ý tưởng, chưa phải kịch bản hay 1.000 bộ nguồn đã nghiệm thu. Trước sản xuất phải kiểm chứng dữ kiện của từng đề tài.\n\n'
    out=[head]
    for group in groups:
        out.append('## '+group['name']+'\n\n| Mã | Ưu tiên | Đề tài |\n|---|---|---|')
        out.extend(f"| {e['id']} | P{e['priority']} | {e['title']} |" for e in entries if e['category']==group['id'])
        out.append('')
    (base/'TOPICS.md').write_text('\n'.join(out))
    launch=sorted(entries,key=lambda e:e['editorial_order'])[:80]
    (base/'FIRST-80.md').write_text('# 80 video khởi động đề xuất\n\nXen kẽ nhóm nội dung; đây là thứ tự biên tập, không phải lịch đăng tự động.\n\n'+'\n'.join(f"{i}. **{e['title']}** — `{e['id']}` ({e['category_name']})" for i,e in enumerate(launch,1))+'\n')
    payload=json.dumps(entries,ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kho 1.000 video nghiên cứu</title><style>body{font:17px system-ui;margin:0;background:#f4f7fa;color:#172033}main{max-width:1150px;margin:auto;padding:32px}h1{font-size:32px}input,select{font:inherit;padding:12px;margin:6px 6px 12px 0;border:1px solid #b5c6d4;border-radius:8px}input{width:min(95%,500px)}article{background:white;padding:18px;margin:12px 0;border-radius:12px;border-left:5px solid #51a7c7}small{color:#526477}h2{font-size:21px;margin:8px 0}a{color:#176487}code{font-size:13px}button{padding:8px;cursor:pointer}#count{font-weight:bold}</style><main><h1>1.000 ý tưởng cho kênh nghiên cứu</h1><p>90–180 giây • Người que áo xanh • 40 nhóm nội dung</p><p>Tra cứu nguồn định hướng: 22/09/2026. Mỗi đề tài cần kiểm chứng riêng trước khi viết kịch bản. Trang này hiển thị kế hoạch tĩnh; trạng thái đã làm xem bằng bank.py status.</p><input id="q" aria-label="Tìm đề tài" placeholder="Tìm: Zotero, tạp chí, dữ liệu, nghiên cứu…"><select id="cat" aria-label="Nhóm"><option value="">Tất cả nhóm</option></select><select id="priority" aria-label="Ưu tiên"><option value="">Mọi ưu tiên</option><option value="1">P1 — làm sớm</option><option value="2">P2 — mở rộng</option><option value="3">P3 — chuyên sâu</option></select><p id="count"></p><div id="results"></div></main><script>const data=PAYLOAD;const q=document.querySelector('#q'),cat=document.querySelector('#cat'),priority=document.querySelector('#priority');for(const [id,name] of new Map(data.map(e=>[e.category,e.category_name]))){const o=document.createElement('option');o.value=id;o.textContent=name;cat.append(o)}function draw(){let rows=data.filter(e=>(!cat.value||e.category===cat.value)&&(!priority.value||String(e.priority)===priority.value)&&e.title.toLocaleLowerCase('vi').includes(q.value.toLocaleLowerCase('vi'))).sort((a,b)=>a.editorial_order-b.editorial_order);document.querySelector('#count').textContent=rows.length+' đề tài';const box=document.querySelector('#results');box.replaceChildren();for(const e of rows){let a=document.createElement('article'),s=document.createElement('small'),h=document.createElement('h2'),c=document.createElement('code');s.textContent=e.category_name+' · P'+e.priority+' · '+e.format;h.textContent=e.title;c.textContent=e.id;a.append(s,h,c);box.append(a)}}q.oninput=cat.onchange=priority.onchange=draw;draw();</script></html>'''.replace('PAYLOAD',payload)
    (base/'index.html').write_text(page)
    return dict(topics=len(entries),categories=len(groups))

if __name__=='__main__': print(build())
