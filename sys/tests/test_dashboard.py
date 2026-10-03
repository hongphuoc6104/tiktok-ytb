import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from dashboard.data import Dashboard, safe
from dashboard.server import make_server

class DashboardTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.job=self.root/'runs/test-job';cp=self.job/'checkpoints/audio/1';cp.mkdir(parents=True)
  asset=self.job/'audio/voice.wav';asset.parent.mkdir();asset.write_bytes(b'RIFF1234WAVEfixture')
  (self.job/'brief-current.json').write_text('{"topic":"test"}')
  (cp/'manifest.json').write_text(json.dumps({'phase':'audio','revision':1,'assets':['audio/voice.wav'],'payload':{'duration':1.2},'review':'checkpoints/audio/1/review.md'}));(cp/'review.md').write_text('# Review fixture')
  self.calls=[]
  def cli(argv):
   self.calls.append(argv);return {'job':argv[1],'mode':'review','checkpoints':[{'phase':'audio','state':'awaiting_review','revision':1}]}
  self.app=Dashboard(self.root,cli=cli,home=self.root/'home');self.server=make_server(self.root,dashboard=self.app);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.port=self.server.server_port
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
 def request(self,method,path,data=None,headers=None):
  conn=HTTPConnection('127.0.0.1',self.port);conn.request(method,path,json.dumps(data) if data is not None else None,headers=headers or {});r=conn.getresponse();v=(r.status,r.read(),dict(r.getheaders()));conn.close();return v
 def token_headers(self):
  status,body,_=self.request('GET','/api/state');self.assertEqual(status,200);return {'Origin':'http://127.0.0.1:'+str(self.port),'Content-Type':'application/json','X-VP-CSRF':json.loads(body)['csrf']}
 def test_eight_tabs_and_real_state(self):
  code,page,headers=self.request('GET','/');self.assertEqual(code,200);self.assertIn(b'/app.js',page);self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
  js=(Path(__file__).parents[1]/'dashboard/static/app.js').read_text();self.assertEqual(js.split('const names=')[1].split(';')[0].count("','")+1,8);self.assertEqual(self.app.snapshot()['jobs'][0]['checkpoints'][0]['revision'],1)
 def test_exact_revision_public_cli(self):
  self.assertEqual(self.request('POST','/api/actions/approve',{'job':'test-job','phase':'audio','revision':1,'note':'Đồng ý'},self.token_headers())[0],200)
  self.assertIn(['approve','test-job','audio','--revision','1','--note','Đồng ý'],self.calls)
 def test_csrf_origin_host_cross_site(self):
  h=self.token_headers()
  for change in ({'Origin':'https://evil.example'},{'X-VP-CSRF':'bad'},{'Origin':''},{'Host':'evil.example'},{'Sec-Fetch-Site':'cross-site'}):self.assertEqual(self.request('POST','/api/actions/stop',{'job':'test-job','source':'Dừng'},{**h,**change})[0],403)
  self.assertEqual(self.request('GET','/api/state',headers={'Host':'evil.example'})[0],403);self.assertFalse(any(x[0]=='stop' for x in self.calls))
 def test_media_allowlist_ranges_traversal(self):
  a=self.app.job('test-job')['artifacts'][0];code,body,h=self.request('GET',a['url'],headers={'Range':'bytes=4-7'});self.assertEqual((code,body),(206,b'1234'));self.assertEqual(h['Content-Range'],'bytes 4-7/19')
  for p in ('/media/test-job/../../etc/passwd','/media/test-job/'+'0'*24,'/api/jobs/..%2F..','/etc/passwd','/style.css/../data.py'):self.assertEqual(self.request('GET',p)[0],404)
  outside=self.root/'secret.wav';outside.write_bytes(b'secret');(self.job/'audio/escape.wav').symlink_to(outside);self.assertIsNone(self.app._asset('test-job','audio/escape.wav','audio',1));self.assertIsNone(self.app._asset('test-job','../secret.wav','audio',1))
 def test_observe_no_write_and_no_event_secret(self):
  (self.root/'.state').mkdir();db=self.root/'.state/jobs.sqlite'
  with sqlite3.connect(db) as c:c.execute('CREATE TABLE events(id INTEGER,at REAL,job TEXT,module TEXT,event TEXT,detail TEXT)');c.execute('INSERT INTO events VALUES(1,1,"test-job","audio","remote",?)',(json.dumps({'token':'never-output','request':'r1','nested':{'cookie':'secret'}}),))
  before=hashlib.sha256(db.read_bytes()).hexdigest();self.app.snapshot();self.assertEqual(before,hashlib.sha256(db.read_bytes()).hexdigest());self.assertNotIn('never-output',json.dumps(self.app.events('test-job')));self.assertEqual(safe({'note':'https://accounts.google.com/oauth?code=secret'}),{'note':'[Dữ liệu xác thực đã ẩn]'})
 def test_generated_without_local_file_hidden(self):
  p=self.job/'checkpoints/audio/1/manifest.json';data=json.loads(p.read_text());data['assets'].append('audio/not-downloaded.wav');p.write_text(json.dumps(data));self.assertFalse(any(x['name'].endswith('not-downloaded.wav') for x in self.app.job('test-job')['artifacts']))
 def test_unknown_runtime_allocation_is_visible_and_not_fake_t4(self):
  home=self.root/'home';store=home/'.config/video-pilot/colab';(store/'profiles/account-01').mkdir(parents=True);(store/'accounts.json').write_text('{"accounts":[{"id":"account-01"}]}')
  self.app.budgets.bind_identity('colab:account-01','stable-google','TEST explicit identity');key=hashlib.sha256(json.dumps('stable-google',ensure_ascii=False,sort_keys=True).encode()).hexdigest();journal=self.app.budgets.path.parent/('allocation-'+key+'.json');journal.write_text(json.dumps({'phase':'ambiguous','account':'account-01','session':'original-session','allocation_started_at':1}))
  account=self.app.snapshot()['inventory']['accounts'][0];self.assertEqual(account['capability']['state'],'allocation_ambiguous');self.assertEqual(account['capability']['device'],'not_confirmed');self.assertTrue(account['budget']['uncertain']);self.assertGreater(account['budget']['provisional_runtime_seconds'],0);self.assertEqual(account['budget']['allocated_sessions'],[])
 def test_invalid_revision_and_command(self):
  h=self.token_headers();self.assertEqual(self.request('POST','/api/actions/approve',{'job':'test-job','phase':'audio','revision':'1','note':'x'},h)[0],400);self.assertEqual(self.request('POST','/api/actions/exec',{'job':'test-job','command':'rm'},h)[0],400)

if __name__=='__main__':unittest.main()
