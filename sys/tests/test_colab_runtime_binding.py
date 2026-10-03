"""Frozen runtime selection and collection ownership; no live service calls."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from pilot import ROOT, read, write
from colab_bridge import accounts
from colab_bridge.client import Client, ColabError
from session_store import Sessions


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.cfg=read(ROOT/'config.json')
        self.cfg['colab_tts'].update(account='auto',session='old-config-default',management_store=str(self.root/'budget'))
        patcher=patch.object(accounts,'STORE',self.root/'accounts');patcher.start();self.addCleanup(patcher.stop)
        for name in ('account-a','account-b'):
            accounts.add(name);(accounts.folder(name)/'token.json').write_text('{}')
        patcher=patch('colab_bridge.client.cli',return_value='/bin/true');patcher.start();self.addCleanup(patcher.stop)
        self.a={'service':'colab','account':'colab:account-a','runtime_session':'runtime-a'}
        self.b={'service':'colab','account':'colab:account-b','runtime_session':'runtime-b'}
        self.frozen={'pool':['colab:account-a'],'defaults':{'colab':'colab:account-a'},'runtime_bindings':{'colab':self.a}}
        self.global_new={'pool':['colab:account-b'],'defaults':{'colab':'colab:account-b'},'runtime_bindings':{'colab':self.b}}
        write(self.root/'.state/management-session.json',self.global_new)

    def test_frozen_job_binding_wins_over_changed_global_and_config_default(self):
        self.cfg['colab_tts']['management_session']=self.frozen
        client=Client(self.root,self.cfg)
        self.assertEqual((client.account,client.session),('account-a','runtime-a'))
        self.assertEqual(Client(self.root,{**self.cfg,'colab_tts':{k:v for k,v in self.cfg['colab_tts'].items() if k!='management_session'}}).session,'runtime-b')

    def test_binding_wins_over_selected_default_but_explicit_wrong_account_fails(self):
        self.frozen['pool'].append('colab:account-b');self.frozen['defaults']['colab']='colab:account-b'
        self.cfg['colab_tts']['management_session']=self.frozen
        client=Client(self.root,self.cfg);self.assertEqual((client.account,client.session),('account-a','runtime-a'))
        self.cfg['colab_tts']['account']='account-b'
        with self.assertRaisesRegex(ColabError,'ACCOUNT_MISMATCH'):Client(self.root,self.cfg)

    def test_explicit_lifecycle_session_is_not_overridden_by_binding(self):
        self.cfg['colab_tts'].update(account='account-b',session='explicit-cli-runtime',_session_explicit=True)
        client=Client(self.root,self.cfg)
        self.assertEqual((client.account,client.session),('account-b','explicit-cli-runtime'))
        self.cfg['colab_tts']['session']=''
        with self.assertRaisesRegex(ColabError,'SESSION_INVALID'):Client(self.root,self.cfg)

    def test_malformed_or_unselected_binding_is_rejected(self):
        for change in ({'service':'flow'},{'account':'browser-a'},{'runtime_session':'../escape'},{'account':'colab:unselected'}):
            cfg=copy.deepcopy(self.cfg);cfg['colab_tts']['management_session']=copy.deepcopy(self.frozen)
            cfg['colab_tts']['management_session']['runtime_bindings']['colab'].update(change)
            with self.subTest(change=change):
                with self.assertRaises(ColabError):Client(self.root,cfg)

    def test_saved_submitted_owner_wins_over_new_binding_during_collection(self):
        req={'request_id':'fixture-request'};cache=self.root/'cache';folder=cache/req['request_id'];folder.mkdir(parents=True)
        write(folder/'state.json',{'phase':'ambiguous','account':'account-a','session':'saved-runtime-a','remote':'/content/saved','request_id':req['request_id']})
        client=Client(self.root,self.cfg)
        self.assertEqual((client.account,client.session),('account-b','runtime-b'))
        seen=[]
        def call(*args,**kwargs):seen.append((client.account,client.session,args[0]));raise ColabError('fixture pending output')
        with patch.object(client,'ensure_authenticated'),patch.object(client,'call',side_effect=call):
            with self.assertRaisesRegex(ColabError,'fixture pending'):client.render(req,self.root/'out',cache)
        self.assertEqual(seen,[('account-a','saved-runtime-a','download')])

    def test_lifecycle_cli_marks_explicit_session(self):
        import colab_bridge.__main__ as entry
        cfg=copy.deepcopy(self.cfg)
        with patch('sys.argv',['colab_bridge','status','--account','account-b','--session','exact-runtime']),patch.object(entry.json,'loads',return_value=cfg),patch.object(entry,'Client') as factory,patch('builtins.print'):
            entry.main()
        options=factory.call_args.args[1]['colab_tts']
        self.assertTrue(options['_session_explicit']);self.assertEqual(options['session'],'exact-runtime');self.assertEqual(options['account'],'account-b')
