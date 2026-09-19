"""Versioned M1 contracts. Structural evidence is not a semantic approval."""
import json
from pathlib import Path
import jsonschema

class ContractError(ValueError):
 def __init__(self, errors):
  self.errors=errors
  super().__init__(json.dumps(errors,ensure_ascii=False))

def error(code,path,message,fix):
 return dict(code=code,path=path,message=message,fix=fix)

def schema_errors(root,name,data):
 schema=json.loads((Path(root)/'schemas'/name).read_text())
 errors=[]
 for e in jsonschema.Draft202012Validator(schema).iter_errors(data):
  path='/'.join(map(str,e.absolute_path))
  if e.validator=='required':
   for key in e.validator_value:
    if key not in e.instance:errors.append(error('SCHEMA',('/'.join([path,key])).strip('/'),'Thiếu trường bắt buộc','Bổ sung '+key+'.'))
  else:errors.append(error('SCHEMA',path or '$',e.message,'Điền đúng trường theo hợp đồng.'))
 return errors


def validate_brief(root,b):
 errors=schema_errors(root,'brief-v2.json',b)
 if errors: raise ContractError(errors)
 if b['duration']['min_seconds']>b['duration']['max_seconds']:
  errors.append(error('DURATION','duration','Khoảng thời lượng đảo ngược','Sửa min/max.'))
 ids=[x['id'] for x in b['required_points']]
 if len(ids)!=len(set(ids)): errors.append(error('DUPLICATE','required_points','Trùng mã ý','Dùng mã riêng.'))
 ids=[x['id'] for x in b['sources']]
 if len(ids)!=len(set(ids)): errors.append(error('DUPLICATE','sources','Trùng mã nguồn','Dùng mã riêng.'))
 if b['facts_required'] and not b['sources']:
  errors.append(error('SOURCE_REQUIRED','sources','Chưa cung cấp dữ kiện','Bổ sung tài liệu và dữ kiện trước khi viết.'))
 if errors: raise ContractError(errors)

def validate_content(root,b,revision,bhash,p):
 errors=schema_errors(root,'content-v2.json',p)
 if errors: raise ContractError(errors)
 def fail(code,path,msg,fix='Sửa bản nháp theo yêu cầu hiện tại.'):
  errors.append(error(code,path,msg,fix))
 if p['brief_revision']!=revision or p['brief_hash']!=bhash: fail('BRIEF_VERSION','brief_revision','Sai phiên bản yêu cầu')
 for key in ['topic','duration','style']:
  if p[key]!=b[key]: fail('BRIEF_MISMATCH',key,'Khác yêu cầu đã lưu')
 req={x['id']:x['text'] for x in b['required_points']}
 if p['required_points']!=list(req.values()): fail('BRIEF_MISMATCH','required_points','Ý bắt buộc bị thay đổi')
 scenes={s['id']:s for s in p['scenes']}
 if [s['id'] for s in p['scenes']]!=[f'SC{i:02}' for i in range(1,b['scene_count']+1)]: fail('SCENES','scenes','Thiếu, trùng hoặc sai thứ tự mã cảnh')
 chars=[c['id'] for c in p['characters']]
 if len(chars)!=len(set(chars)): fail('CHARACTERS','characters','Trùng mã nhân vật')
 source_ids={s['id'] for s in b['sources']}
 for s in p['scenes']:
  if set(s['character_ids'])-set(chars): fail('CHARACTER_REF',s['id'],'Nhân vật chưa khai báo')
  if set(s['source_ids'])-source_ids: fail('SOURCE_REF',s['id'],'Nguồn chưa khai báo')
  if set(s['requirements'])-set(req): fail('REQUIREMENT_REF',s['id'],'Mã ý không tồn tại')
 covered=set()
 for c in p['coverage']:
  s=scenes.get(c['scene_id'])
  if c['requirement_id'] not in req or not s: fail('COVERAGE_REF','coverage','Sai mã ý hoặc cảnh');continue
  if c['quote'] not in s['narration']: fail('QUOTE','coverage','Trích dẫn không tồn tại trong lời dẫn')
  if c['requirement_id'] not in s['requirements']: fail('COVERAGE_REF','coverage','Cảnh chưa liên kết ý')
  covered.add(c['requirement_id'])
 if covered!=set(req): fail('COVERAGE','coverage','Chưa ánh xạ đủ ý bắt buộc')
 total=sum(s['estimated_seconds'] for s in p['scenes'])
 if not b['duration']['min_seconds']<=total<=b['duration']['max_seconds']: fail('ESTIMATE','scenes','Tổng thời lượng dự kiến ngoài khoảng')
 if errors: raise ContractError(errors)

def review_markdown(job,revision,b,p):
 lines=[f'# Nội dung {job} — phiên bản {revision}',f"Đề tài: {p['topic']}",f"Người xem: {b['audience']}",f"Mục tiêu: {b['goal']}",'Thời lượng dự kiến; chưa được xác nhận bằng WAV.', '## Kịch bản']
 for s in p['scenes']:
  lines += [f"### {s['id']} — {s['title']}",s['narration'],f"Cảnh: {s['action']} | {s['setting']} | {s['camera']}",f"Nhân vật: {', '.join(s['character_ids'])}",f"Prompt: {s['prompt']}"]
 lines += ['## Nhân vật']+[f"- {c['id']}: {c['name']}; {c['appearance']}; {c['outfit']}" for c in p['characters']]
 lines += ['## Ánh xạ ý bắt buộc']+[f"- {c['requirement_id']} → {c['scene_id']}: {c['quote']}" for c in p['coverage']]
 lines += ['## Cần người dùng duyệt','Đủ ý về nghĩa · Lời đọc tự nhiên · Diễn biến hợp lý · Có thể minh họa','Kiểm tra kỹ thuật đạt không thay thế duyệt nội dung.']
 return '\n\n'.join(lines)+'\n'
