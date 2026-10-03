"""Dashboard observes and changes the official engine's isolated records."""
import json
import threading
import unittest
from http.client import HTTPConnection
from dashboard.data import Dashboard
from dashboard.server import make_server
from pilot import observe_job
import execution as ex
import tests.test_execution_v4 as fixture_module

class DashboardEngineTests(unittest.TestCase):
 def test_review_and_auto_share_exact_artifact_events(self):
  fixture=fixture_module.ExecutionTests(methodName='test_dynamic_scene_count_freezes_from_this_outline');fixture.setUp()
  try:
   fixture.new('review');ex.author(fixture.p,fixture.job,'outline',fixture.outline(),'TEST connected agent');ex.advance(fixture.p,fixture.job)
   def public(argv):
    if argv[0] in ('status','next'):return observe_job(fixture.root,argv[1],next_only=argv[0]=='next')
    if argv[0]=='approve':return ex.approve(fixture.p,argv[1],argv[2],int(argv[4]),argv[6])
    raise AssertionError('Unexpected mutation')
   app=Dashboard(fixture.root,cli=public,home=fixture.root/'home');server=make_server(fixture.root,dashboard=app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   try:
    conn=HTTPConnection('127.0.0.1',server.server_port);conn.request('GET','/api/state');response=conn.getresponse();self.assertEqual(response.status,200);state=json.loads(response.read());conn.close()
    job=state['jobs'][0];self.assertEqual(job['state']['mode'],'review');cp=job['checkpoints'][0];self.assertEqual(cp['revision'],1);self.assertTrue(cp['assets']);self.assertTrue(any(e['event']=='artifact_ready' for e in job['events']))
    conn=HTTPConnection('127.0.0.1',server.server_port);conn.request('POST','/api/actions/approve',json.dumps({'job':fixture.job,'phase':'outline','revision':1,'note':'TEST actual user decision'}),{'Origin':f'http://127.0.0.1:{server.server_port}','Content-Type':'application/json','X-VP-CSRF':state['csrf']});r=conn.getresponse();self.assertEqual(r.status,200);r.read();conn.close();self.assertTrue(ex.accepted(fixture.p,fixture.job,'outline'))
    ex.change_mode(fixture.p,fixture.job,'auto','TEST actual requested mode');new=app.job(fixture.job);self.assertEqual(new['state']['mode'],'auto');self.assertTrue(any(e['event']=='execution_mode_changed' for e in new['events']))
   finally:server.shutdown();server.server_close();thread.join()
  finally:fixture.doCleanups()

if __name__=='__main__':unittest.main()
