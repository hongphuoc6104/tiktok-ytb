"""Long-form (tiensu) content adapter: budgets, scene-by-scene assembly, bounded repair. Fake agy only."""
import copy,json,math,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,ROOT,read,write
from content_contract import ContractError,validate_content
from scripts import agy_longform
from scripts.agy_pipeline import generate

FIX=Path(__file__).resolve().parent/'fixtures'


def tiensu_brief():return read(FIX/'tiensu-brief.json')
def real_sc02():return read(FIX/'tiensu-001-sc02.json')


def synthetic_scene(b,row,budget):
 """A scene that meets its budget: unique sentences, beats anchored on sentence starts, no ids in prose."""
 sid=row['scene_id'];n=int(sid[2:]);target=budget['units']['vi']['target']
 sentences=[];total=0;k=0
 while total<target:
  k+=1;s=f'Câu số {k} của phần {n} kể tiếp chuyện nhóm người tiền sử quanh bếp lửa.'
  sentences.append(s);total+=len(s.split())
 narration=' '.join(sentences)
 images=[{'id':f'{sid}_I{j:02}','description':'Người tiền sử tóc bù mặc áo da thú ngồi cạnh bếp lửa trong hang','character_ids':['CH01'],
          'based_on':None,'preserve':'','change':'Góc nhìn mới','reason':'Minh hoạ lời dẫn','visible_text':[],'kind':'still'} for j in range(1,budget['images']+1)]
 step=len(sentences)/budget['beats']
 beats=[]
 for j in range(budget['beats']):
  beats.append({'id':f'{sid}_B{j+1:02}','image_id':images[j%len(images)]['id'],'purpose':'Nhịp kể','effect':'cut','focus':{'x':.5,'y':.5},
                'anchor':{'vi':{'quote':f'Câu số {int(j*step)+1} của','occurrence':1}},
                'overlays':[{'type':'label','text':'Bếp lửa giữ ấm','x':.5,'y':.8}]})
 scene={'id':sid,'title':f'Phần {n}','purpose':row['purpose'],'action':'Nhóm lửa','setting':'Hang đá','camera':'Trung cảnh',
        'narration':narration,'requirements':row['requirements'],'character_ids':['CH01'],'source_ids':['S1'],
        'images':images,'beats':beats,'chapter':f'Chương {n}'}
 coverage=[{'requirement_id':r,'quote':sentences[0]} for r in row['requirements']]
 claims=[{'quote':sentences[0],'language':'vi','source_id':'S1','fact':b['sources'][0]['facts'][0]}]
 return {'scene':scene,'coverage':coverage,'claims':claims}


class FakeAgy:
 """Answers by schema shape; `override(label, data)` may replace a scene answer to inject failures."""
 def __init__(self,b,override=None):
  self.b=b;self.outline=real_sc02()['outline'];self.calls=[];self.override=override
 def __call__(self,prompt,schema,workspace,conversation=None,timeout=180):
  props=schema.get('properties',{})
  if 'outline' in props:label='outline';data=self.outline
  elif 'characters' in props:label='cast';data={'characters':[{'id':'CH01','name':'Người tiền sử tóc bù','appearance':'Đầu tròn trắng viền mực đen, tóc bù nâu sẫm','outfit':'Áo da thú nâu, vòng cổ xương'}]}
  elif 'packaging' in props:
   label='packaging';data={'packaging':{'titles':['Người tiền sử ngủ ra sao?','Một ngày thời đồ đá','Họ giữ ấm thế nào?'],
    'thumbnail':{'image_id':'SC01_I01','text':'NGỦ SAO?','emotion':'tò mò'},'hook':'Bạn ngủ trong chăn ấm. Còn họ thì sao?','tags':['tiền sử']},
    'open_questions':[],'revision_response':[]}
  else:
   repair='\nRepair data: ' in prompt
   task=json.loads(prompt.rsplit('\nRepair data: ' if repair else '\nTask data: ',1)[1])
   row=task['outline_row'];label=('repair-' if repair else 'scene-')+row['scene_id']
   data=synthetic_scene(self.b,row,task['budget'])
   if self.override:data=self.override(label,data,len([c for c in self.calls if c['label']==label]))
  self.calls.append({'label':label,'prompt':prompt,'timeout':timeout})
  return {'status':'SUCCESS','conversation_id':'TEST-'+label,'structured_output':copy.deepcopy(data)}
 def labels(self):return [c['label'] for c in self.calls]


class LongformBudgetTests(unittest.TestCase):
 def test_budget_from_duration_and_speech_rate(self):
  b=tiensu_brief();plan=agy_longform.budgets(b,real_sc02()['outline'])
  self.assertEqual(plan['target_seconds'],600)
  self.assertEqual(len(plan['scenes']),8)
  self.assertTrue(1800<=plan['units_total']['vi']<=2400,plan['units_total'])
  self.assertTrue(80<=plan['beats_total']<=150,plan['beats_total'])
  self.assertTrue(40<=plan['images_total']<=70,plan['images_total'])
  self.assertEqual(plan['clips_max'],10)
  first,mid=plan['scenes'][0],plan['scenes'][1]
  self.assertGreater(first['units']['vi']['target'],mid['units']['vi']['target'])  # SC01 carries R1-R3
  for s in plan['scenes']:
   self.assertTrue(s['beats_min']<=s['beats']<=s['beats_max'])
   self.assertLessEqual(s['seconds']/s['beats'],6);self.assertGreaterEqual(s['seconds']/s['beats'],4)
   u=s['units']['vi'];self.assertEqual((u['min'],u['max']),(math.floor(u['target']*.85),math.ceil(u['target']*1.15)))
 def test_longform_detection(self):
  self.assertTrue(agy_longform.is_longform(tiensu_brief()))
  short=read(ROOT/'examples/story-v3/brief.json');self.assertFalse(agy_longform.is_longform(short))
  short['duration']={'min_seconds':200,'max_seconds':450};self.assertTrue(agy_longform.is_longform(short))
  self.assertFalse(agy_longform.is_longform(read(ROOT/'examples/m1/brief.json')))
 def test_real_failure_maps_to_its_scene(self):
  b=tiensu_brief();fx=real_sc02();outline=fx['outline'];plan=agy_longform.budgets(b,outline)
  parts={r['scene_id']:synthetic_scene(b,r,s) for r,s in zip(outline['outline'],plan['scenes'])}
  parts['SC02']={'scene':fx['scene'],'coverage':fx['coverage'],'claims':fx['claims']}
  closing={'packaging':None,'open_questions':[],'revision_response':[]}
  chars=[{'id':'CH01','name':'Người tiền sử','appearance':'Đầu tròn','outfit':'Áo da thú'},{'id':'CH02','name':'Người hái lượm','appearance':'Đầu tròn','outfit':'Tạp dề da'}]
  c=agy_longform.assemble(b,1,'H',outline,chars,parts,closing)
  errors=agy_longform.contract_errors(ROOT,b,1,'H',c)+agy_longform.local_errors(b,c,plan)
  codes={e['code'] for e in errors}
  self.assertTrue({'INTERNAL_LABEL','BUDGET_UNITS'}<=codes,codes)
  targets,other=agy_longform.assign(c,errors)
  self.assertEqual(other,[]);self.assertEqual(set(targets),{'SC02'})


class LongformGenerateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for n in ['schemas','.agents','renderer','tests','examples','scripts']:shutil.copytree(ROOT/n,self.root/n)
  for n in ['pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','content_contract.py','config.json','AGENTS.md','GEMINI.md']:shutil.copy(ROOT/n,self.root/n)
  cfg=read(self.root/'config.json');cfg['brief_policies']=[];write(self.root/'config.json',cfg)  # no topic-bank ledger in the sandbox
  self.b=tiensu_brief();self.p=Pilot(self.root);self.p.new('ts',self.b);self.p.approve('ts','control',1,'TEST ONLY')
 def tearDown(self):self.p.db.close();self.tmp.cleanup()
 def attempt(self):return next((self.p.job('ts')/'agent-attempts').iterdir())
 def test_scene_by_scene_assembly_is_valid_content_v3(self):
  fake=FakeAgy(self.b)
  with patch('scripts.agy_pipeline.invoke',side_effect=fake):self.assertEqual(generate(self.p,'ts')['action'],'review')
  scenes=[f'scene-SC{i:02}' for i in range(1,9)]
  self.assertEqual(fake.labels(),['outline','cast']+scenes+['packaging'])
  self.assertEqual({c['timeout'] for c in fake.calls[1:]},{400})
  draft=read(self.p.job('ts')/'draft/content.json');_,rev,h=self.p.brief('ts')
  validate_content(self.root,self.b,rev,h,draft)
  self.assertEqual(draft['outline'],fake.outline['outline'])
  self.assertEqual([c['scene_id'] for c in draft['coverage']][:3],['SC01']*3)
  sc1=draft['scenes'][0]['narration']
  self.assertNotIn(sc1,fake.calls[2]['prompt']);self.assertIn(sc1,fake.calls[3]['prompt'])  # earlier narration passed on
  self.assertIn('opening_images',fake.calls[9]['prompt'].rsplit('Task data: ',1)[1])
  self.assertIn('<= 40 characters',fake.calls[2]['prompt'])
  att=self.attempt();files=sorted(x.name for x in (att/'calls').iterdir())
  self.assertEqual(len([x for x in files if x.endswith('.request.json')]),10)
  self.assertEqual(len([x for x in files if x.endswith('.response.json')]),10)
  self.assertTrue((att/'budget.json').exists());self.assertEqual(read(att/'attempt.json')['state'],'awaiting_review')
 def test_repair_targets_only_failing_scene(self):
  fx=real_sc02()
  def override(label,data,n):
   if label=='scene-SC02':return {'scene':fx['scene'],'coverage':fx['coverage'],'claims':fx['claims']}
   if label=='scene-SC04':data['scene']['beats'][1]['overlays']=[{'type':'label','text':'Một nhãn quá dài vượt giới hạn bốn mươi ký tự','x':.5,'y':.5}]
   return data
  fake=FakeAgy(self.b,override)
  with patch('scripts.agy_pipeline.invoke',side_effect=fake):generate(self.p,'ts')
  repairs=[x for x in fake.labels() if x.startswith('repair')]
  self.assertEqual(sorted(repairs),['repair-SC02','repair-SC04'])
  prompt=next(c['prompt'] for c in fake.calls if c['label']=='repair-SC02')
  self.assertIn('INTERNAL_LABEL',prompt);self.assertIn('BUDGET_UNITS',prompt)
  self.assertIn('OVERLAY',next(c['prompt'] for c in fake.calls if c['label']=='repair-SC04'))
  draft=read(self.p.job('ts')/'draft/content.json');self.assertNotIn('CH01',draft['scenes'][1]['narration'])
  self.assertTrue(any(x.name.startswith('11-repair1-') for x in (self.attempt()/'calls').iterdir()))
 def test_repair_loop_is_bounded(self):
  def override(label,data,n):
   if label.endswith('SC03'):data['scene']['narration']='Quá ngắn. '+data['scene']['narration'][:40]
   return data
  fake=FakeAgy(self.b,override)
  with patch('scripts.agy_pipeline.invoke',side_effect=fake):
   with self.assertRaises(ContractError) as ctx:generate(self.p,'ts')
  self.assertEqual([x for x in fake.labels() if x.startswith('repair')],['repair-SC03','repair-SC03'])
  self.assertIn('BUDGET_UNITS',{e['code'] for e in ctx.exception.errors})
  att=read(self.attempt()/'attempt.json');self.assertEqual(att['state'],'blocked');self.assertTrue(att['errors'])
  self.assertFalse((self.p.job('ts')/'draft/content.json').exists())
  self.assertEqual(self.p.rows('ts')['content']['revision'],0)
 def test_timeout_stops_without_retry(self):
  from pilot import Blocked
  fake=FakeAgy(self.b)
  def invoke(prompt,schema,workspace,conversation=None,timeout=180):
   if 'scene' in schema.get('properties',{}):raise Blocked('AGY_TIMEOUT')
   return fake(prompt,schema,workspace,timeout=timeout)
  with patch('scripts.agy_pipeline.invoke',side_effect=invoke):
   with self.assertRaisesRegex(Blocked,'AGY_TIMEOUT'):generate(self.p,'ts')
  self.assertEqual(fake.labels(),['outline','cast'])
  self.assertTrue(any(x.name.endswith('.error.json') for x in (self.attempt()/'calls').iterdir()))
  self.assertEqual(read(self.attempt()/'attempt.json')['state'],'blocked')


if __name__=='__main__':unittest.main()
