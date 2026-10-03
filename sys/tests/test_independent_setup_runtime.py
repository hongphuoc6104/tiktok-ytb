"""Independent setup/runtime forward QA. Temporary homes, servers and sockets only."""
import copy
import hashlib
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import b2_bridge
from pilot import ROOT, Blocked
from permissions import Grants, PermissionDenied
from account_catalog import discover, probe_flow
from dashboard.data import Dashboard
from dashboard.server import make_server
from session_store import Sessions


class IndependentSetup(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='independent-setup-');self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name);self.root=self.home/'sys';self.root.mkdir()
        profiles=self.home/'.config/video-pilot/colab';(profiles/'profiles/qa-a').mkdir(parents=True);(profiles/'profiles/qa-b').mkdir()
        (profiles/'accounts.json').write_text(json.dumps({'preferred':'qa-b','accounts':[{'id':'qa-a'},{'id':'qa-b'}]}))
        browser=self.home/'.config/google-chrome-cdp-profile4';(browser/'Profile 4').mkdir(parents=True)
        (browser/'Local State').write_text(json.dumps({'profile':{'info_cache':{'Profile 4':{'name':'QA Profile'}}}}))
        (self.root/'config.json').write_text(json.dumps({'colab_tts':{'account':'auto','session':'wrong-global-runtime'},'flow_session_image_cap':150}))
        self.calls=[];self.entered=threading.Event();self.release=threading.Event();self.addCleanup(self.release.set)
        self.app=Dashboard(self.root,home=self.home,client_factory=self.client)
        self.grant=Grants(self.root).grant('setup',source='TEST exact setup instruction',paths=['.state/**','runs/qa-job/**','experiments/b2_illustrator/machine.local.json'])['id']
        self.prod=Grants(self.root).grant('production',source='TEST production scope is not setup',jobs=['qa-job'])['id']
        self.flow=next(x['id'] for x in discover(self.home,self.root)['accounts'] if x['service']=='flow')
        self.app.sessions.select(['colab:qa-a','colab:qa-b',self.flow],{'colab':'colab:qa-b','flow':self.flow})
        self.app.budgets.bind_identity('colab:qa-a','google:QA-same-identity','TEST fixture identity')
        self.app.budgets.bind_identity('colab:qa-b','google:QA-same-identity','TEST fixture alias')
        self.app.budgets.bind_identity(self.flow,'google:QA-flow','TEST fixture identity')

    def client(self,root,cfg):
        owner=self
        class FakeClient:
            account=cfg['colab_tts']['account'];session=cfg['colab_tts']['session']
            def start(self):owner.calls.append(('start',self.account,self.session));owner.entered.set();owner.release.wait(5)
            def setup(self):owner.calls.append(('setup',self.account,self.session))
            def stop(self):owner.calls.append(('stop',self.account,self.session))
            def reconcile(self):owner.calls.append(('reconcile',self.account,self.session))
            def render(self,payload,out,cache,collect_only=False):owner.calls.append(('render',self.account,self.session,collect_only,str(out),str(cache)))
            def synthesize(self,payload,out,cache,collect_only=False):owner.calls.append(('synthesize',self.account,self.session,collect_only,str(out),str(cache)))
        return FakeClient()

    def data(self,**extra):return {'grant':self.grant,'source':'TEST setup request','account':'colab:qa-a','runtime_session':'qa-original-runtime',**extra}
    def finish(self,app,key):
        deadline=time.time()+6
        while time.time()<deadline:
            if app.operations[key]['state']=='finished':return app.operations[key]['result']
            time.sleep(.01)
        self.fail('Isolated setup operation did not finish')

    def start_server(self):
        server=make_server(self.root,dashboard=self.app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        def close():server.shutdown();server.server_close();thread.join(5)
        self.addCleanup(close);return server
    def http(self,server,method,path,body=None,headers=None):
        conn=HTTPConnection('127.0.0.1',server.server_port,timeout=5)
        conn.request(method,path,None if body is None else json.dumps(body),headers or {})
        response=conn.getresponse();data=json.loads(response.read());conn.close();return response.status,data

    def test_http_grant_csrf_async_operation_and_duplicate_same_identity(self):
        server=self.start_server();status,state=self.http(server,'GET','/api/state');self.assertEqual(status,200)
        headers={'Origin':f'http://127.0.0.1:{server.server_port}','Content-Type':'application/json','X-VP-CSRF':state['csrf']}
        for data,head in ((self.data(grant=self.prod),headers),(self.data(source=''),headers),(self.data(),{**headers,'X-VP-CSRF':'wrong'})):
            status,result=self.http(server,'POST','/api/actions/colab-start',data,head);self.assertEqual(status,403,result)
        self.assertEqual(self.calls,[])
        status,operation=self.http(server,'POST','/api/actions/colab-start',self.data(),headers);self.assertEqual(status,200)
        self.assertTrue(self.entered.wait(2))
        status,blocked=self.http(server,'POST','/api/actions/colab-start',self.data(account='colab:qa-b'),headers)
        self.assertEqual(status,400,blocked);self.assertEqual(len(self.calls),1)
        status,state=self.http(server,'GET','/api/state');self.assertEqual(status,200)
        self.assertTrue(any(x['state']=='running' for x in state['operations']))
        self.release.set();result=self.finish(self.app,operation['operation']);self.assertEqual(result['runtime_session'],'qa-original-runtime')

    def test_fresh_controller_account_lock_blocks_duplicate_alias(self):
        first=self.app.mutate('colab-start',self.data());self.assertTrue(self.entered.wait(2))
        fresh=Dashboard(self.root,home=self.home,client_factory=self.client)
        second=fresh.mutate('colab-start',self.data(account='colab:qa-b'))
        result=self.finish(fresh,second['operation']);self.assertIn('blocked',result);self.assertEqual(len(self.calls),1)
        self.release.set();self.finish(self.app,first['operation'])

    def test_collect_is_pinned_owner_collectonly_even_when_defaults_change(self):
        request='c'*64;path=self.root/'runs/qa-job/cache/colab-render'/request;path.mkdir(parents=True)
        (path/'state.json').write_text(json.dumps({'account':'qa-a','session':'qa-original-runtime','phase':'ambiguous','request_id':request}))
        revision=self.root/'runs/qa-job/revisions/render/1';revision.mkdir(parents=True)
        (revision/'request-colab-render.json').write_text(json.dumps({'request_id':request,'operation':'render','worker_sha256':'QA-saved-worker'}))
        self.app.sessions.pin(request,job='qa-job',service='colab',account='colab:qa-a',session='qa-original-runtime')
        before=copy.deepcopy(self.app.sessions.read()['pins'])
        self.app.sessions.select(['colab:qa-a','colab:qa-b',self.flow],{'colab':'colab:qa-b','flow':self.flow})
        op=self.app.mutate('colab-collect',self.data(job='qa-job',request=request));result=self.finish(self.app,op['operation'])
        self.assertEqual(result['operation'],'collect');self.assertEqual(self.calls[0][:4],('render','qa-a','qa-original-runtime',True))
        self.assertEqual(self.app.sessions.read()['pins'],before)
        op=self.app.mutate('colab-collect',self.data(account='colab:qa-b',job='qa-job',request=request));self.assertIn('blocked',self.finish(self.app,op['operation']))
        self.assertEqual(len(self.calls),1)

    def test_collect_output_symlink_escape_rejected_before_provider(self):
        request='d'*64;path=self.root/'runs/qa-job/cache'/request;path.mkdir(parents=True)
        (path/'state.json').write_text(json.dumps({'account':'qa-a','session':'qa-original-runtime','phase':'ambiguous'}))
        (path/'request.json').write_text(json.dumps({'request_id':request,'operation':'synthesize'}))
        outside=self.home/'outside';outside.mkdir();(self.root/'runs/qa-job/colab-collected').symlink_to(outside,target_is_directory=True)
        op=self.app.mutate('colab-collect',self.data(job='qa-job',request=request));self.assertIn('blocked',self.finish(self.app,op['operation']))
        self.assertEqual(self.calls,[]);self.assertEqual(list(outside.iterdir()),[])

    def test_job_runtime_binding_and_pin_remain_frozen_across_global_changes(self):
        s=self.app.sessions;s.bind_runtime('colab','colab:qa-a','job-runtime',grant=self.grant,source='TEST job selection',evidence='TEST selected exact target',job='qa-job')
        s.pin('old-request',job='qa-job',service='colab',account='colab:qa-a',session='old-session')
        frozen=copy.deepcopy(s.snapshot('qa-job'));s.bind_runtime('colab','colab:qa-b','new-default',grant=self.grant,source='TEST new global target',evidence='TEST exact new target')
        self.assertEqual(Sessions(self.root).snapshot('qa-job'),frozen)
        self.assertEqual(s.read()['pins']['old-request']['session'],'old-session')

    def test_flow_probe_does_not_connect_or_inspect_wrong_selected_profile(self):
        with patch('b2_bridge.query_status',return_value={'status':'connected','identity':{'observedProfile':str(self.home/'wrong/Default')}}),patch('b2_bridge.send_raw_command',side_effect=AssertionError('No inspect/generation on a different profile')):
            result=probe_flow(self.flow,system_root=self.root,home=self.home,budget_store=self.app.budgets.path.parent)
        self.assertEqual(result['auth'],'unknown');self.assertEqual(result['reason'],'selected_profile_not_connected')

    def test_matching_flow_probe_reads_exact_account_ui_only(self):
        item=next(x for x in discover(self.home,self.root)['accounts'] if x['id']==self.flow);profile=str(Path(item['metadata_root'])/item['profile'])
        observation={'auth':'verified','capability':'read_only_observation','identity':'google:QA-flow','identity_source':'google_account_ui','observedProfile':profile,'source':'TEST fixture UI'}
        with patch('b2_bridge.query_status',return_value={'status':'connected','identity':{'observedProfile':profile}}),patch('b2_bridge.send_raw_command',return_value=observation) as command:
            result=probe_flow(self.flow,system_root=self.root,home=self.home,budget_store=self.app.budgets.path.parent)
        command.assert_called_once_with('tool-snapshot:account-inspect',timeout=45);self.assertEqual(result['auth'],'verified')

    def test_actual_browser_flow_counts_colab_internal_ring_and_setup_fields(self):
        server=self.start_server();session=self.app.sessions.read()['session_id']
        self.app.budgets.flow_submit(self.flow,'qa-job','QA-request',3,cap=150,budget_session=session,evidence='TEST fixture submitted')
        self.app.budgets.flow_state(self.flow,'qa-job','QA-request','unknown','TEST fixture timeout')
        report=ROOT/'reports/normalization/qa-setup-runtime-browser.json';screenshot=ROOT/'reports/normalization/qa-setup-runtime-browser.png'
        result=subprocess.run(['node',str(ROOT/'tests/test_independent_setup_browser.mjs'),f'http://127.0.0.1:{server.server_port}',str(report),str(screenshot)],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(report.read_text());self.assertTrue(data['fixture']);self.assertEqual(data['flow_ring_count'],0);self.assertGreater(data['colab_ring_count'],0)

    def test_clean_clone_docs_explain_control_dependencies_and_explicit_daemon_setup(self):
        guide=(ROOT/'docs/getting-started.md').read_text()
        for concept in ('Playwright','Node','control-start'):
            self.assertIn(concept,guide,'Fresh clone guide must explain browser-control dependency/listener setup')


class IndependentShortSocket(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='independent-socket-');self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/('long-'+'a'*65)/('deep-'+'b'*65)/'sys';self.root.mkdir(parents=True)
        self.runtime=self.base/'runtime';self.runtime.mkdir(mode=0o700)

    def fake_socket(self,path,mode=0o600):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);listener.bind(str(path));os.chmod(path,mode);listener.listen(2);listener.settimeout(3)
        def serve():
            conn=None
            try:
                conn,_=listener.accept();conn.recv(1024);conn.sendall(b'{"status":"TEST-fixture"}\n');conn.close()
            except OSError:pass
            finally:
                if conn is not None:conn.close()
        thread=threading.Thread(target=serve,daemon=True);thread.start()
        self.addCleanup(listener.close);return listener,thread

    def test_python_refuses_symlink_socket_instead_of_following_it(self):
        original=self.runtime/'real.sock';self.fake_socket(original)
        link=self.runtime/'link.sock';link.symlink_to(original)
        with patch.object(b2_bridge,'SOCKET_PATH',link):
            with self.assertRaises(Blocked) as blocked:b2_bridge.send_raw_command('status',timeout=1)
        self.assertIs(getattr(blocked.exception,'generation_submitted',None),False)

    def test_python_refuses_world_accessible_socket(self):
        path=self.runtime/'public.sock';self.fake_socket(path,0o666)
        with patch.object(b2_bridge,'SOCKET_PATH',path):
            with self.assertRaises(Blocked) as blocked:b2_bridge.send_raw_command('status',timeout=1)
        self.assertIs(getattr(blocked.exception,'generation_submitted',None),False)

    def test_python_refuses_peer_uid_mismatch_on_real_socket(self):
        path=self.runtime/'private.sock';self.fake_socket(path)
        native_socket=socket.socket;peer_checks=[];sent=[]
        class PeerSocket:
            def __init__(self,*args,**kwargs):self.native=native_socket(*args,**kwargs)
            def __getattr__(self,key):return getattr(self.native,key)
            def getsockopt(self,level,option,*args):
                if option==socket.SO_PEERCRED:
                    peer_checks.append(True);return struct.pack('3i',os.getpid(),os.getuid()+1,os.getgid())
                return self.native.getsockopt(level,option,*args)
            def sendall(self,value):sent.append(value);return self.native.sendall(value)
        # The connection is real; only kernel peer-credential response is injected.
        # This verifies refusal logic without operating another user's process.
        with patch.object(b2_bridge,'SOCKET_PATH',path),patch('b2_bridge.socket.socket',PeerSocket):
            with self.assertRaises(Blocked) as blocked:b2_bridge.send_raw_command('status',timeout=1)
        self.assertTrue(peer_checks);self.assertEqual(sent,[])
        self.assertIs(getattr(blocked.exception,'generation_submitted',None),False)

    def test_official_node_short_socket_server_and_python_hash_correspond(self):
        engine=self.root/'experiments/b2_illustrator';engine.mkdir(parents=True);(engine/'results').mkdir()
        for name in ('session.mjs','controller.mjs','attempt-store.mjs'):shutil.copy(ROOT/'experiments/b2_illustrator'/name,engine/name)
        (self.root/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
        (self.root/'config.json').write_text(json.dumps({'flow_tool_url':'https://flow.google.com/project/QA/tool/QA','flow_status_retries':0}))
        (engine/'browser-profiles.json').write_text(json.dumps({'flow_user_data_dir':str(self.base/'fake-browser'),'flow_profile_directory':'Default'}))
        env={**os.environ,'TMPDIR':str(self.runtime)}
        with patch('b2_bridge.tempfile.gettempdir',return_value=str(self.runtime)):expected=b2_bridge.session_socket_path(self.root)
        script="import {sessionSocketPath} from "+json.dumps((engine/'session.mjs').as_uri())+";process.stdout.write(sessionSocketPath("+json.dumps(str(self.root))+"));"
        result=subprocess.run(['node','--input-type=module','-e',script],env=env,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(Path(result.stdout),expected);self.assertLess(len(os.fsencode(expected)),108)
        child=subprocess.Popen(['node',str(engine/'session.mjs'),'serve'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            deadline=time.time()+5
            while not expected.exists() and child.poll() is None and time.time()<deadline:time.sleep(.02)
            self.assertTrue(expected.exists(),child.stderr.read() if child.poll() is not None else 'No isolated socket')
            self.assertEqual(expected.stat().st_mode&0o777,0o600);self.assertEqual(expected.parent.stat().st_mode&0o777,0o700)
            with patch.object(b2_bridge,'SOCKET_PATH',expected),patch.object(b2_bridge,'ROOT',self.root):
                self.assertEqual(b2_bridge.query_status(timeout=1)['status'],'not_connected')
                self.assertEqual(b2_bridge.send_raw_command('inspect',timeout=1)['status'],'blocked')
            from scripts import bootstrap
            with patch('tempfile.gettempdir',return_value=str(self.runtime)):
                self.assertEqual(bootstrap.control_status(self.root)['daemon_status'],'not_connected')
        finally:
            child.terminate();child.wait(timeout=5);child.stdout.close();child.stderr.close()

    def test_official_bootstrap_clean_control_start_creates_listener_without_connection(self):
        from scripts import bootstrap
        engine=self.root/'experiments/b2_illustrator';engine.mkdir(parents=True);(engine/'results').mkdir()
        for name in ('session.mjs','controller.mjs','attempt-store.mjs'):shutil.copy(ROOT/'experiments/b2_illustrator'/name,engine/name)
        shutil.copytree(ROOT/'control',self.root/'control')
        (self.root/'config.json').write_text(json.dumps({'flow_tool_url':'https://flow.google.com/project/QA/tool/QA'}))
        (engine/'browser-profiles.json').write_text(json.dumps({'flow_user_data_dir':str(self.base/'fake-browser'),'flow_profile_directory':'Default'}))
        home=self.base/'fresh-home';home.mkdir()
        runtime=bootstrap.control_directory(home)
        for module in ('playwright','playwright-core'):
            shutil.copytree(ROOT/'node_modules'/module,runtime/'node_modules'/module)
        grant=Grants(self.root).grant('setup',source='TEST official control listener setup',paths=['experiments/b2_illustrator/session.mjs','.state/**'])['id']
        children=[]
        def spawn(*args,**kwargs):
            process=subprocess.Popen(*args,**kwargs);children.append(process);return process
        with patch.dict(os.environ,{'TMPDIR':str(self.runtime)}),patch('tempfile.gettempdir',return_value=str(self.runtime)):
            try:
                result=bootstrap.control_start(self.root,grant=grant,source='TEST listener only',home=home,runner=spawn)
                self.assertEqual(result['daemon_status'],'not_connected');self.assertFalse(result['browser_started']);self.assertFalse(result['provider_called'])
                self.assertFalse((self.root/'node_modules').exists(),'Fresh setup must use control runtime, not repo dependency symlink')
                repeat=bootstrap.control_start(self.root,grant=grant,source='TEST same listener reuse',home=home,runner=spawn)
                self.assertTrue(repeat['reused'])
                self.assertEqual(len(children),1)
            finally:
                for child in children:
                    if child.poll() is None:child.terminate()
                    child.wait(timeout=5)


if __name__=='__main__':unittest.main()
