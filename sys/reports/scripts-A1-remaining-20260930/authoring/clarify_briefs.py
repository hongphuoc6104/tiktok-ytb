import json,subprocess,time
from source_utils import ROOT,OUT,ENTRIES
scope={718:'vừa mới',758:'trên bề mặt',760:'cho, dành cho người nhận',761:'bằng phương tiện đi lại'}
for n in [625,643,*scope]:
 e=ENTRIES[n];j=ROOT/'runs'/e['job'];meta=json.loads((j/'brief-current.json').read_text());b=json.loads((j/f"briefs/{meta['revision']}.json").read_text());assert not (j/'revisions/content/1/content.json').exists()
 marker='Làm rõ phạm vi trước chốt lời dẫn/neo ngày 01/10/2026.'
 if marker in b['planning']['assumptions']:continue
 if n in scope:
  gloss=scope[n];e['selected_gloss_vi']=gloss
  for k in ['goal','topic']:
   b[k]=b[k].replace(e['gloss_vi'],gloss)
  for r in b['required_points']:r['text']=r['text'].replace(e['gloss_vi'],gloss)
  b['planning']['domain_requirements']=[s.replace(e['gloss_vi'],gloss) for s in b['planning']['domain_requirements']]
  b['planning']['avoid'].append({718:'Chỉ luyện just nghĩa vừa mới xảy ra; không luyện nghĩa chỉ/chỉ có.',758:'Chỉ luyện on cho vật đặt trên bề mặt; không luyện ngày trong tuần.',760:'Chỉ luyện for cho người nhận món đồ; không luyện nguyên nhân hay thời lượng.',761:'Chỉ luyện by + phương tiện không có mạo từ; không luyện tác nhân câu bị động.'}[n])
 else:
  b['planning']['avoid']=[s for s in b['planning']['avoid'] if 'fact.n' not in s]
  b['planning']['domain_requirements'].append('Fact có cùng nghĩa lõi sự thật/dữ kiện có căn cứ trong ngữ cảnh khoa học và thường ngày. Hai mã kho tách ngữ cảnh, không phải hai nghĩa từ vựng loại trừ nhau. Bài này giữ ngữ cảnh '+('dự án khoa học; không bịa số đo hoặc kết quả.' if n==625 else 'kiểm thông tin cuộc hẹn hư cấu; không phủ nhận fact trong khoa học.'))
 b['planning']['assumptions'].append(marker)
 f=OUT/'operations-local'/f'{n}-scope-candidate.json';f.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
 for attempt in range(600):
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'pilot.py','revise-brief',e['job'],'--brief',str(f),'--note','Giữ một cách dùng được chọn, loại bỏ chỉ dẫn nghĩa chồng lấn trước revision content.'],cwd=ROOT,capture_output=True,text=True);d=json.loads(r.stdout)
  if d.get('blocked')=='Another operation is running':time.sleep(.5);continue
  (OUT/'operations-local'/f'{n}-scope-result.json').write_text(r.stdout)
  assert r.returncode==0 and not d.get('blocked'),r.stdout
  print('Clarified',n,flush=True);break
 else:raise RuntimeError('Bounded operation wait exhausted')
(OUT/'selection.json').write_text(json.dumps(list(ENTRIES.values()),ensure_ascii=False,indent=2)+'\n')
