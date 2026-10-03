import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from account_catalog import discover
from account_budget import Budgets,HOUR,WINDOW
from session_store import Sessions
from scripts.bootstrap import check,plan,apply

class AccountManagementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.b=Budgets(self.root/'global');self.b.bind_identity('a','stable','probe');self.b.bind_identity('alias','stable','probe')
 def tearDown(self):self.tmp.cleanup()
 def test_discovery_reads_only_metadata_token_presence(self):
  browser=self.root/'.config/google-chrome';(browser/'Default').mkdir(parents=True);(browser/'Local State').write_text(json.dumps({'profile':{'info_cache':{'Default':{'name':'Personal','user_name':'email'}}}}));(browser/'Default/Cookies').write_bytes(b'DO-NOT-READ')
  store=self.root/'.config/video-pilot/colab';(store/'profiles/account-02').mkdir(parents=True);(store/'accounts.json').write_text('{"preferred":"account-02","accounts":[{"id":"account-02","enabled":true}]}');(store/'profiles/account-02/token.json').write_bytes(b'DO-NOT-READ-TOKEN')
  original=Path.read_text
  def guard(path,*args,**kwargs):self.assertNotIn(path.name,('token.json','Cookies','Preferences'));return original(path,*args,**kwargs)
  with patch.object(Path,'read_text',guard):d=discover(self.root)
  self.assertEqual(len(d['accounts']),2);self.assertTrue(d['accounts'][0]['configured']);self.assertEqual(d['accounts'][0]['auth']['state'],'not_tested');self.assertNotIn('DO-NOT-READ',json.dumps(d));self.assertGreaterEqual(len(d['roots']),23)
 def test_session_default_pin_immutable(self):
  s=Sessions(self.root);s.select(['a','alias'],{'flow':'a'});s.pin('r',job='j',service='flow',account='a',session='s');s.select(['alias'],{'flow':'alias'});self.assertEqual(Sessions(self.root).read()['pins']['r']['account'],'a');self.assertIsNotNone(s.snapshot()['session_id'])
  with self.assertRaises(ValueError):s.pin('r',job='j',service='flow',account='alias',session='s2')
 def test_unallocated_clock_not_started(self):
  s=self.b.snapshot('a',100);self.assertIsNone(s['window_start']);self.assertEqual(s['used_seconds'],0);self.assertFalse(s['provider_quota_verified'])
  with self.assertRaises(ValueError):self.b.allocated('unknown','s',device='T4',at=100,evidence='probe')
 def test_idle_and_alias_same_usage(self):
  self.b.allocated('a','s',device='T4',at=100,evidence='probe');s=Budgets(self.root/'global').snapshot('alias',100+2*HOUR);self.assertEqual(s['used_seconds'],2*HOUR);self.assertEqual(s['available_seconds'],3*HOUR);self.assertEqual(s['reserve_seconds'],HOUR);self.b.uncertain('alias','s','lost');self.assertTrue(self.b.snapshot('a')['uncertain'])
  with self.assertRaises(ValueError):self.b.allocated('alias','s2',device='T4',at=100,evidence='probe')
 def test_interval_cross_window(self):
  self.b.allocated('a','s',device='T4',at=100,evidence='probe');self.b.released('a','s',at=100+WINDOW+HOUR,evidence='termination');s=self.b.snapshot('a',100+WINDOW+2*HOUR);self.assertEqual(s['used_seconds'],HOUR);self.assertTrue(s['needs_service_recheck']);self.assertFalse(s['provider_quota_verified'])
 def test_reservation_five_hour_stop(self):
  self.b.allocated('a','s',device='T4',at=100,evidence='probe');self.b.reserve('alias','r1',HOUR,now=100+4*HOUR)
  with self.assertRaises(ValueError):self.b.reserve('a','r2',1,now=100+4*HOUR)
  self.b.settle('a','r1')
  with self.assertRaises(ValueError):self.b.reserve('a','r2',1,now=100+5*HOUR)
 def test_flow_unknown_alias_restart_preserves_slots(self):
  self.b.flow_submit('a','op','r1',100,evidence='sent');self.b.flow_state('alias','op','r1','unknown','timeout')
  with self.assertRaises(ValueError):self.b.flow_submit('alias','op','r2',1,evidence='sent')
  with self.assertRaises(ValueError):self.b.flow_submit('alias','op','r1',100,evidence='resubmit')
  self.assertEqual(Budgets(self.root/'global').snapshot('a')['flow']['op']['slots'],100)
 def test_recovery_three_collects_and_hard_stop(self):
  for i in range(3):self.assertEqual(self.b.recover('a','flow','r1:network',action='collect',error='network',submit_state='unknown',evidence=str(i)),i+1)
  with self.assertRaises(ValueError):self.b.recover('alias','flow','r1:network',action='collect',error='network',submit_state='unknown',evidence='4')
  with self.assertRaises(ValueError):self.b.recover('a','flow','r2',action='generate',error='timeout',submit_state='unknown',evidence='timeout')
  with self.assertRaises(ValueError):self.b.recover('a','flow','r3',action='reload',error='bot',submit_state='not_submitted',evidence='bot warning')
  self.assertEqual(self.b.snapshot('alias')['blocks']['flow']['error'],'bot')
 def test_bootstrap_stdlib_no_mutation_and_resume(self):
  before=set(self.root.iterdir());self.assertTrue(check(self.root,home=self.root)['no_provider_calls']);self.assertEqual(before,set(self.root.iterdir()));self.assertIn('local renderer',plan(self.root)['excluded']);calls=[]
  def runner(argv,**kwargs):
   calls.append(argv)
   if argv[1:3]==['-m','venv']:p=Path(argv[-1])/'bin';p.mkdir(parents=True);(p/'python').touch()
  apply(self.root,runner=runner);apply(self.root,runner=runner);self.assertEqual(len(calls),1);apply(self.root,install=True,runner=runner);self.assertIn('install',calls[1]);self.assertIn('pip',calls[1]);self.assertFalse(any('torch' in x or 'ffmpeg' in x for x in calls[1]))

if __name__=='__main__':unittest.main()
