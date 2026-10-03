"""Confirmed server absence versus unknown auth/network; synthetic identities only."""
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from account_budget import Budgets
from colab_bridge.client import Client, ColabError
from colab_bridge.protocol import stamp
from pilot import ROOT, read, write


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);cfg=read(ROOT/'config.json');cfg['colab_tts']['management_store']=str(self.root/'budget')
        with patch('colab_bridge.client.cli',return_value='/bin/true'),patch('colab_bridge.accounts.STORE',self.root/'auth'):
            self.client=Client(self.root,cfg)
        self.client.account='fixture-account';self.client.session='owned-runtime'
        self.budget=Budgets(self.root/'budget');self.budget.bind_identity('colab:fixture-account','fixture-identity','synthetic identity')
        self.budget.allocated('colab:fixture-account','owned-runtime',device='T4',evidence='synthetic allocation')
        self.journal=self.budget.path.parent/('allocation-'+stamp('fixture-identity')+'.json')
        write(self.journal,{'phase':'allocated','account':'fixture-account','session':'owned-runtime','allocation_started_at':self.budget.snapshot('colab:fixture-account')['allocated_sessions'][0]['start']})

    def reconcile(self,data):
        with patch.object(self.client,'ensure_authenticated'),patch.object(self.client,'_assignment_state',return_value=data),patch.object(self.client,'exec',side_effect=AssertionError('No remote execution on absent/unknown assignment')):
            return self.client.reconcile()

    def test_authenticated_server_absence_releases_exact_owned_runtime(self):
        outcome=self.reconcile({'verified':True,'identity':'fixture-identity','assignment_count':0,'source':'official_list_assignments'})
        self.assertEqual(outcome['state'],'released');self.assertEqual(read(self.journal)['phase'],'released')
        self.assertEqual(self.budget.snapshot('colab:fixture-account')['allocated_sessions'],[])
        self.assertTrue(Path(outcome['evidence']).is_file())

    def test_auth_network_and_local_missing_mapping_never_imply_termination(self):
        for data in ({'verified':False,'reason':'network_unknown'},{'verified':False,'reason':'login_required'},{'verified':False,'reason':'refresh_required'},
                     {'verified':True,'identity':'fixture-identity','assignment_count':1,'named_assignment_active':False,'local_session_present':False}):
            with self.subTest(data=data):
                with self.assertRaises(ColabError):self.reconcile(data)
                self.assertEqual(read(self.journal)['phase'],'allocated')
                self.assertEqual(len(self.budget.snapshot('colab:fixture-account')['allocated_sessions']),1)
                self.assertTrue(self.budget.snapshot('colab:fixture-account')['uncertain'])

    def test_wrong_owner_or_authenticated_identity_cannot_release(self):
        with self.assertRaisesRegex(ColabError,'OWNER_MISMATCH'):
            self.reconcile({'verified':True,'identity':'different-google-identity','assignment_count':0})
        self.assertEqual(read(self.journal)['phase'],'allocated')
        saved=read(self.journal);saved['account']='different-account';write(self.journal,saved)
        with self.assertRaisesRegex(ColabError,'OWNER_MISMATCH'):
            self.reconcile({'verified':True,'identity':'fixture-identity','assignment_count':0})
        self.assertEqual(len(self.budget.snapshot('colab:fixture-account')['allocated_sessions']),1)

    def test_preparation_failure_has_no_submitted_audio_and_can_be_prepared_again(self):
        import copy,re,shutil
        from colab_bridge.protocol import build_request
        shutil.copytree(ROOT/'assets/voices',self.root/'assets/voices')
        cfg=read(ROOT/'config.json')
        request=build_request(self.root,cfg,[{'scene_id':'SC01','texts':['I see a predator.'],'gaps':[],'tail':.5}],primary_language='en')
        request['assemble']=True
        cache=self.root/'cache';calls=[]
        def first(*args,**kwargs):calls.append(args[0]);raise ColabError('COLAB_SESSION_NOT_FOUND')
        with patch.object(self.client,'ensure_authenticated'),patch.object(self.client,'_ready'),patch.object(self.client,'call',side_effect=first):
            with self.assertRaisesRegex(ColabError,'SESSION_NOT_FOUND'):self.client.synthesize(request,self.root/'first',cache)
        self.assertEqual(calls,['exec']);self.assertEqual(list(cache.glob('*/state.json')),[])
        self.assertEqual(list(cache.glob('*/request.json')),[])
        calls.clear();submitted=[]
        def resumed(*args,**kwargs):
            calls.append(args[0]);code=kwargs.get('code','')
            if '].run(' in code:submitted.append(True);raise ColabError('COLAB_TIMEOUT')
            match=re.search(r'VP_EXEC_OK_[a-f0-9]+',code);return match.group() if match else ''
        with patch.object(self.client,'ensure_authenticated'),patch.object(self.client,'_ready'),patch.object(self.client,'_reserve'),patch.object(self.client,'call',side_effect=resumed):
            with self.assertRaisesRegex(ColabError,'TIMEOUT'):self.client.synthesize(request,self.root/'second',cache)
        self.assertEqual(submitted,[True]);self.assertTrue(list(cache.glob('*/state.json')))

    def test_exec_error_exposes_sanitized_session_category_only(self):
        failure=SimpleNamespace(returncode=1,stdout="[colab] Session 'owned-runtime' not found. private-token",stderr='oauth-private-code')
        with patch('colab_bridge.accounts.command',return_value=['fixture']),patch('colab_bridge.client.subprocess.run',return_value=failure):
            with self.assertRaises(ColabError) as got:self.client.call('exec')
        self.assertIn('COLAB_SESSION_NOT_FOUND',str(got.exception));self.assertNotIn('private-token',str(got.exception));self.assertNotIn('oauth-private-code',str(got.exception))

class AssignmentProbeTests(unittest.TestCase):
    def modules(self, credentials, operation):
        import types
        claims={'email':'synthetic@example.invalid','email_verified':True}
        class Session:
            def __init__(self,*args,**kwargs):pass
            def get(self,*args,**kwargs):return SimpleNamespace(status_code=200,json=lambda:claims)
        return {'google':types.ModuleType('google'),'google.oauth2':types.ModuleType('google.oauth2'),
                'google.oauth2.credentials':SimpleNamespace(Credentials=SimpleNamespace(from_authorized_user_file=lambda _:credentials)),
                'google.auth':types.ModuleType('google.auth'),'google.auth.transport':types.ModuleType('google.auth.transport'),
                'google.auth.transport.requests':SimpleNamespace(AuthorizedSession=Session),
                'colab_cli':types.ModuleType('colab_cli'),'colab_cli.common':SimpleNamespace(Client=lambda *a:SimpleNamespace(list_assignments=operation),Prod=lambda:None)}

    def test_official_success_empty_list_is_verified_without_exposing_credentials(self):
        import sys
        from colab_bridge.assignment_probe import probe
        with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,self.modules(SimpleNamespace(valid=True),lambda:[])):
            observed=probe(Path(temp),'missing-local-name')
        self.assertTrue(observed['verified']);self.assertEqual(observed['assignment_count'],0)
        self.assertNotIn('synthetic@example.invalid',json.dumps(observed))

    def test_active_assignment_without_local_name_is_preserved_as_mapping_uncertainty(self):
        import sys
        from colab_bridge.assignment_probe import probe
        with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,self.modules(SimpleNamespace(valid=True),lambda:[SimpleNamespace(endpoint='fixture-endpoint')])):
            profile=Path(temp);observed=probe(profile,'owned-runtime')
            self.assertTrue(observed['verified']);self.assertEqual(observed['assignment_count'],1)
            self.assertFalse(observed['named_assignment_active'])
            write(profile/'sessions.json',{'owned-runtime':{'endpoint':'fixture-endpoint','token':'private-fixture-proxy'}})
            named=probe(profile,'owned-runtime');self.assertTrue(named['named_assignment_active'])
            self.assertNotIn('private-fixture-proxy',json.dumps(named));self.assertNotIn('fixture-endpoint',json.dumps(named))

    def test_network_auth_and_expired_credentials_are_never_empty_server_evidence(self):
        import sys
        from colab_bridge.assignment_probe import probe
        class SDKError(Exception):pass
        for status,reason in ((401,'login_required'),(503,'capacity'),(None,'network_unknown')):
            error=SDKError('private OAuth code');error.response=SimpleNamespace(status_code=status)
            def operation():raise error
            with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,self.modules(SimpleNamespace(valid=True),operation)):
                observed=probe(Path(temp),'runtime')
            self.assertFalse(observed['verified']);self.assertEqual(observed['reason'],reason)
            self.assertNotIn('assignment_count',observed);self.assertNotIn('private OAuth code',json.dumps(observed))
        with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,self.modules(SimpleNamespace(valid=False,refresh_token='fixture'),lambda:self.fail('Do not query assignments with invalid credentials'))):
            observed=probe(Path(temp),'runtime')
        self.assertEqual(observed['reason'],'refresh_required');self.assertFalse(observed['verified'])
