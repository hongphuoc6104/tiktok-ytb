"""Probe safety with fake Google/CLI transports; no real OAuth or provider call."""
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from account_catalog import confirm_identity, discover, probe_colab
from account_budget import Budgets
from dashboard.colab_probe import probe, classify


class AccountProbeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.store=self.root/'.config/video-pilot/colab';(self.store/'profiles/account-01').mkdir(parents=True);(self.store/'accounts.json').write_text('{"accounts":[{"id":"account-01"}],"preferred":"account-01"}');(self.store/'profiles/account-01/token.json').write_text('{"private":"never-read-by-inventory"}')
 def tearDown(self):self.tmp.cleanup()
 def test_user_confirmation_never_promotes_auth(self):
  record=confirm_identity('colab:account-01','User@Example.com','TEST user exact confirmation',home=self.root)
  self.assertEqual(record['identity_source'],'user_confirmed');account=discover(self.root)['accounts'][0];self.assertEqual(account['auth']['state'],'not_tested');self.assertTrue(Budgets(self.root/'.config/video-pilot/management').snapshot(account['id'])['identity_configured'])
  self.assertNotIn('user@example.com',(self.root/'.config/video-pilot/management/budgets.json').read_text())
 def test_private_probe_output_allowlist_and_no_gpu_or_login(self):
  binary=self.root/'colab';binary.write_text('#!/private/python\n');calls=[]
  def runner(argv,**kwargs):
   calls.append(argv);return types.SimpleNamespace(returncode=0,stdout=json.dumps({'auth':'verified','capability':'service_access_verified','gpu':'not_tested','identity':'google:test','identity_source':'fixture_verified_identity','source':'TEST fake provider','token':'NEVER-OUTPUT'}))
  value=probe_colab('colab:account-01',home=self.root,runner=runner,binary=binary);self.assertNotIn('token',value);self.assertEqual(value['auth'],'verified');self.assertEqual(len(calls),1);self.assertTrue(calls[0][1].endswith('dashboard/colab_probe.py'));self.assertNotIn('start',calls[0]);self.assertNotIn('NEVER-OUTPUT',json.dumps(discover(self.root)))
 def test_network_does_not_become_logout(self):
  binary=self.root/'colab';binary.write_text('#!/private/python\n')
  def runner(*a,**k):return types.SimpleNamespace(returncode=0,stdout='{"auth":"unknown","capability":"not_tested","reason":"network_unknown","source":"TEST"}')
  value=probe_colab('colab:account-01',home=self.root,runner=runner,binary=binary);self.assertEqual(value['auth'],'unknown');self.assertFalse(Budgets(self.root/'.config/video-pilot/management').snapshot('colab:account-01')['identity_configured'])
 def test_transport_no_refresh_fixed_endpoint_and_sessions_readonly(self):
  calls=[]
  credentials=types.SimpleNamespace(valid=True)
  class Credential:
   @staticmethod
   def from_authorized_user_file(path):return credentials
  class Session:
   def __init__(self,c,max_refresh_attempts):self.assertions=(c,max_refresh_attempts);calls.append(('max_refresh',max_refresh_attempts))
   def get(self,url,**kwargs):calls.append((url,kwargs));return types.SimpleNamespace(status_code=200,json=lambda:{'email':'user@example.com','email_verified':True,'sub':'123'})
  class Client:
   def __init__(self,*args):pass
   def list_assignments(self):calls.append('list_assignments');return []
  modules={'google':types.ModuleType('google'),'google.oauth2':types.ModuleType('google.oauth2'),'google.oauth2.credentials':types.SimpleNamespace(Credentials=Credential),'google.auth':types.ModuleType('google.auth'),'google.auth.transport':types.ModuleType('google.auth.transport'),'google.auth.transport.requests':types.SimpleNamespace(AuthorizedSession=Session),'colab_cli':types.ModuleType('colab_cli'),'colab_cli.common':types.SimpleNamespace(Client=Client,Prod=lambda:None)}
  with patch.dict('sys.modules',modules):value=probe(self.store/'profiles/account-01/token.json')
  self.assertEqual(value['auth'],'verified');self.assertIn(('max_refresh',0),calls);self.assertEqual(calls[1][0],'https://openidconnect.googleapis.com/v1/userinfo');self.assertFalse(calls[1][1]['allow_redirects']);self.assertEqual(calls[2],'list_assignments');self.assertEqual(value['identity'],'google:'+hashlib.sha256(b'user@example.com').hexdigest())
 def test_error_classes_distinct(self):
  for code,expected in ((401,'login_required'),(429,'quota'),(503,'capacity'),(403,'permission_unknown')):
   error=RuntimeError('sanitized');error.response=types.SimpleNamespace(status_code=code);self.assertEqual(classify(error),expected)
  self.assertEqual(classify(RuntimeError('network disconnected')),'network_unknown')

if __name__=='__main__':unittest.main()
