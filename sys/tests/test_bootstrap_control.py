"""Control readiness without OAuth, browser launch, GPU or generation."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from scripts.bootstrap import (check, control_dependencies, control_directory, control_start,
                               control_status, install_control, node_runtime, session_socket_path)
from permissions import Grants, PermissionDenied

ROOT = Path(__file__).resolve().parents[1]


class BootstrapControlTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.home=Path(self.temp.name)
        self.root=self.home/'clone/sys';self.root.mkdir(parents=True)
        shutil.copytree(ROOT/'control',self.root/'control')

    def tearDown(self):
        self.temp.cleanup()

    def test_check_is_read_only_and_separates_missing_control_readiness(self):
        before=set(self.home.rglob('*'))
        value=check(self.root,home=self.home)
        self.assertEqual(set(self.home.rglob('*')),before)
        caps=value['capabilities']
        self.assertIn('node_control',caps)
        self.assertEqual(caps['playwright_control']['state'],'missing')
        self.assertEqual(caps['flow_daemon']['state'],'missing')
        self.assertEqual(caps['flow_auth']['state'],'not_tested')
        self.assertTrue(value['no_provider_calls'])

    def test_manifest_contains_only_playwright_and_no_renderer(self):
        manifest=json.loads((ROOT/'control/package.json').read_text())
        lock=json.loads((ROOT/'control/package-lock.json').read_text())
        self.assertEqual(manifest['dependencies'],{'playwright':'1.58.2'})
        packages=set(lock['packages'])- {''}
        self.assertLessEqual(packages,{'node_modules/playwright','node_modules/playwright-core','node_modules/fsevents'})
        self.assertNotIn('scripts',manifest)

    def test_short_socket_matches_runtime_bridge_contract(self):
        import b2_bridge
        self.assertEqual(session_socket_path(self.root),b2_bridge.session_socket_path(self.root))
        self.assertLess(len(str(session_socket_path(self.root)).encode()),108)

    def test_unresponsive_socket_never_promotes_auth_or_starts(self):
        path=session_socket_path(self.root);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('not-a-socket')
        try:
            result=control_status(self.root)
            self.assertEqual(result['state'],'unsafe_owner')
            self.assertFalse(result['browser_connected'])
        finally:path.unlink()

    def test_readonly_status_uses_only_status_command(self):
        path=session_socket_path(self.root);path.parent.mkdir(parents=True,exist_ok=True)
        server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(path));server.listen(1)
        received=[]
        def serve():
            client,_=server.accept()
            with client:
                received.append(client.recv(100))
                client.sendall(b'{"status":"not_connected","identity":null}\n')
        thread=threading.Thread(target=serve,daemon=True);thread.start()
        try:
            result=control_status(self.root)
            self.assertEqual(result['state'],'verified')
            self.assertFalse(result['browser_connected'])
            self.assertEqual(received,[b'status\n'])
            self.assertFalse(result['provider_called'])
        finally:server.close();thread.join(2);path.unlink()

    def test_missing_node_has_official_handoff_without_download(self):
        with patch('scripts.bootstrap.shutil.which',return_value=None):
            result=node_runtime()
        self.assertEqual(result['state'],'missing')
        self.assertEqual(result['official_install'],'https://nodejs.org/en/download')

    def test_daemon_start_requires_explicit_setup_authority(self):
        grant=Grants(self.root).grant('production',source='Synthetic isolated produce',jobs=['test'])['id']
        with self.assertRaises(PermissionDenied):
            control_start(self.root,grant=grant,source='Synthetic isolated produce',home=self.home)


@unittest.skipUnless(os.environ.get('VP_TEST_CONTROL_INSTALL')=='1','Explicit bounded registry install test required')
class IsolatedControlInstall(unittest.TestCase):
    def test_fresh_clone_real_install_import_and_listener_no_browser(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder);root=home/'clone/sys';root.mkdir(parents=True)
            shutil.copytree(ROOT/'control',root/'control')
            experiment=root/'experiments/b2_illustrator';experiment.mkdir(parents=True)
            for source in (ROOT/'experiments/b2_illustrator').glob('*.mjs'):
                shutil.copyfile(source,experiment/source.name)
            (root/'config.json').write_text('{}')
            (experiment/'browser-profiles.json').write_text('{}')
            # Public setup uses the copied clone, not imports from the original
            # checkout. These are the dependency-free official grant/setup APIs.
            for name in ('profile_setup.py','permissions.py','account_catalog.py','session_store.py'):
                shutil.copyfile(ROOT/name,root/name)
            (root/'scripts').mkdir()
            shutil.copyfile(ROOT/'scripts/bootstrap.py',root/'scripts/bootstrap.py')
            self.assertFalse((root/'node_modules').exists())
            result=install_control(root,home=home)
            self.assertEqual(result['state'],'verified')
            self.assertFalse(result['local_renderer_installed'])
            self.assertFalse(result['browser_download'])
            self.assertFalse((home/'.cache/ms-playwright').exists())
            self.assertFalse((root/'node_modules').exists())
            self.assertTrue((control_directory(home)/'node_modules/playwright').is_dir())
            self.assertFalse((control_directory(home)/'node_modules/remotion').exists())
            again=install_control(root,home=home)
            self.assertEqual(again['manifest_sha256'],result['manifest_sha256'])
            grant=Grants(root).grant('setup',source='Synthetic isolated listener test',paths=['experiments/b2_illustrator/session.mjs'])['id']
            processes=[]
            def launch(*args,**kwargs):
                process=subprocess.Popen(*args,**kwargs);processes.append(process);return process
            started=control_start(root,grant=grant,source='Synthetic isolated listener test',home=home,runner=launch)
            try:
                self.assertEqual(started['daemon_status'],'not_connected')
                self.assertFalse(started['browser_started'])
                self.assertFalse(started['provider_called'])
                reused=control_start(root,grant=grant,source='Synthetic isolated listener reuse',home=home)
                self.assertTrue(reused['reused'])
                self.assertEqual(reused['daemon_status'],'not_connected')
                # Public CLI in isolated Python cannot inherit imported modules
                # from this test runner or resolve the original repository.
                cli=[os.sys.executable,'-I','-S',str(root/'scripts/bootstrap.py')]
                response=subprocess.run([*cli,'control-status','--root',str(root)],capture_output=True,text=True,timeout=10,check=True)
                public_status=json.loads(response.stdout)
                self.assertEqual(public_status['daemon_status'],'not_connected')
                response=subprocess.run([*cli,'control-start','--root',str(root),'--home',str(home),
                                         '--grant',grant,'--source','Synthetic isolated public listener reuse'],
                                        capture_output=True,text=True,timeout=15,check=True)
                public_reuse=json.loads(response.stdout)
                self.assertTrue(public_reuse['reused'])
                self.assertFalse(public_reuse['browser_started'])
                self.assertFalse((home/'.config/video-pilot/colab').exists())
                report={'test':'fresh_clone_control_install', 'isolated':True, 'live_provider':False,
                        'runtime':{'playwright':result['version'],'import':result['proof']},
                        'repository_node_modules':False,'local_renderer':False,'browser_download':False,
                        'daemon':{'status':started['daemon_status'],'reused':reused['reused'],'browser_started':False,
                                  'isolated_public_cli_status':public_status['daemon_status'],'isolated_public_cli_reuse':public_reuse['reused']},
                        'socket_length':len(started['socket'].encode()),'manifest_sha256':result['manifest_sha256'],
                        'installed_bytes':sum(file.stat().st_size for file in control_directory(home).rglob('*') if file.is_file())}
                target=ROOT/'reports/normalization/bootstrap-control-proof.json'
                target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2)+'\n')
            finally:
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
                    client.settimeout(3);client.connect(started['socket']);client.sendall(b'stop\n');client.recv(1024)
                deadline=time.monotonic()+3
                while Path(started['socket']).exists() and time.monotonic()<deadline:time.sleep(.05)
                self.assertFalse(Path(started['socket']).exists())
                for process in processes:process.wait(timeout=3)


if __name__=='__main__':unittest.main()
