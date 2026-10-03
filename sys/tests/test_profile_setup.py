import json
import os
import socket
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

from account_catalog import discover
from permissions import Grants, PermissionDenied
from profile_setup import SetupBlocked, configure, endpoint, endpoint_status, inventory, lock_status, plan, processes, start

URL = 'https://flow.google.com/project/41d3d574-907c-4bb0-90a7-c98f85f5e22b/tool/2791e8ba-9ae0-4ca9-9368-b7efe600c53d'


class ProfileSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.root = self.home / 'system'
        self.root.mkdir()
        self.browser = self.home / '.config/google-chrome'
        self.managed = self.home / '.config/google-chrome-cdp-profile4'
        for folder, names in ((self.browser, ('Default', 'Profile 4')), (self.managed, ('Profile 4',))):
            folder.mkdir(parents=True)
            for name in names:
                (folder / name).mkdir()
                (folder / name / 'Cookies').write_bytes(b'secret-never-read')
            (folder / 'Local State').write_text(json.dumps({'profile': {'info_cache': {name: {'name': name} for name in names}}}))
        self.binary = self.home / 'chrome'
        self.binary.write_text('#!/bin/sh\nexit 0\n')
        self.binary.chmod(0o700)
        self.grant = Grants(self.root).grant('setup', source='User requested profile setup',
                                            paths=['experiments/b2_illustrator/machine.local.json'])['id']

    def tearDown(self):
        self.temp.cleanup()

    def account(self, managed=True):
        return next(x['id'] for x in inventory(self.root, self.home)
                    if x['metadata_root'] == str(self.managed if managed else self.browser) and x['profile'] == 'Profile 4')

    def prepared(self):
        value = plan(self.root, self.account(), URL, home=self.home, executable=self.binary)
        configure(self.root, value, grant=self.grant, source='User requested profile setup')
        return value

    def test_custom_roots_discovered_without_credentials(self):
        original = Path.read_text
        def read_metadata(path, *args, **kwargs):
            self.assertNotIn(path.name, ('Cookies', 'Preferences', 'token.json'))
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read_metadata):
            found = discover(self.home, self.root)
        self.assertEqual(len(found['accounts']), 3)
        managed = next(x for x in found['accounts'] if x['browser'] == 'Chrome managed')
        self.assertEqual(managed['auth']['state'], 'not_tested')
        self.assertIsNone(managed['identity'])
        self.assertNotIn('secret-never-read', json.dumps(found))

    def test_ordinary_profile_gets_empty_managed_root_no_copy(self):
        value = plan(self.root, self.account(False), URL, home=self.home, executable=self.binary)
        self.assertTrue(value['fresh_login_required'])
        self.assertEqual(value['flow_profile_directory'], 'Default')
        self.assertNotEqual(value['flow_user_data_dir'], str(self.browser))
        self.assertFalse(Path(value['flow_user_data_dir']).exists())
        self.assertFalse(value['authentication_verified'])

    def test_reuses_exact_existing_root(self):
        value = plan(self.root, self.account(), URL, home=self.home, executable=self.binary)
        self.assertEqual(value['flow_user_data_dir'], str(self.managed))
        self.assertEqual(value['flow_profile_directory'], 'Profile 4')
        self.assertFalse(value['fresh_login_required'])
        with self.assertRaises(SetupBlocked):
            plan(self.root, self.account(), URL, home=self.home, executable=self.binary, managed_root=self.home/'another')

    def test_matching_source_mapping_requires_explicit_reuse_selection(self):
        managed = next(x for x in inventory(self.root, self.home) if x['id'] == self.account())
        self.assertEqual(managed['source_account_candidates'], [self.account(False)])
        value = plan(self.root, self.account(False), URL, home=self.home,
                     executable=self.binary, reuse_account=self.account())
        self.assertEqual(value['source_account'], self.account(False))
        self.assertEqual(value['runtime_account'], self.account())
        self.assertEqual(value['flow_user_data_dir'], str(self.managed))
        self.assertFalse(value['authentication_verified'])

    def test_exact_tool_and_scope_are_required(self):
        with self.assertRaises(ValueError):
            plan(self.root, self.account(), 'https://flow.google.com/', home=self.home, executable=self.binary)
        value = plan(self.root, self.account(), URL, home=self.home, executable=self.binary)
        grant = Grants(self.root).grant('production', source='Produce job', jobs=['j'])['id']
        with self.assertRaises(PermissionDenied):
            configure(self.root, value, grant=grant, source='Produce job')
        with self.assertRaises(PermissionDenied):
            configure(self.root, value, grant=self.grant, source='')

    def test_browser_start_is_bounded_and_localhost_only(self):
        self.prepared()
        running = []
        fake = Mock(pid=54321)
        fake.poll.return_value = None
        def launch(argv, **kwargs):
            self.assertIn('--remote-debugging-port=0', argv)
            self.assertIn('--remote-debugging-address=127.0.0.1', argv)
            self.assertFalse(any('no-sandbox' in x or 'remote-allow-origins' in x for x in argv))
            running.append({'pid': 54321, 'localhost': True, 'cdp_ephemeral': True})
            return fake
        runner = Mock(side_effect=launch)
        result = start(self.root, grant=self.grant, source='User requested opening', runner=runner,
                       inspect_processes=lambda root: running, inspect_endpoint=lambda root: 'ws://127.0.0.1:1234/devtools/browser/abc' if running else None)
        self.assertTrue(result['owned'])
        self.assertEqual(result['auth'], 'not_tested')
        again = start(self.root, grant=self.grant, source='User requested opening', runner=runner,
                      inspect_processes=lambda root: running, inspect_endpoint=lambda root: result['endpoint'])
        self.assertTrue(again['reused'])
        self.assertEqual(runner.call_count, 1)

    def test_stale_owner_and_shared_non_cdp_are_not_deleted_or_killed(self):
        self.prepared()
        marker = self.managed / 'DevToolsActivePort'
        marker.write_text('1234\n/devtools/browser/old\n')
        runner = Mock()
        with self.assertRaises(SetupBlocked):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root: [], inspect_endpoint=lambda root: None)
        self.assertTrue(marker.exists())
        with self.assertRaises(SetupBlocked):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root: [{'pid': 1, 'localhost': False, 'cdp_ephemeral': False}], inspect_endpoint=lambda root: None)
        runner.assert_not_called()

    def test_starting_owner_prevents_concurrent_launch(self):
        self.prepared()
        owner = self.root / '.state/flow-profile-setup.json'
        data = json.loads(owner.read_text())
        data['active'] = {'root': str(self.managed), 'pid': os.getpid(), 'state': 'starting'}
        owner.write_text(json.dumps(data))
        runner = Mock()
        with self.assertRaisesRegex(SetupBlocked, 'STILL_OWNED'):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root: [], inspect_endpoint=lambda root: None)
        runner.assert_not_called()

    def test_proc_matches_exact_root_and_endpoint_exact_port(self):
        proc = self.home/'proc'
        (proc/'11').mkdir(parents=True)
        (proc/'12').mkdir()
        (proc/'11/cmdline').write_bytes(('chrome\0--user-data-dir='+str(self.managed)+'\0--remote-debugging-port=0\0--remote-debugging-address=127.0.0.1\0').encode())
        (proc/'12/cmdline').write_bytes(('chrome\0--user-data-dir='+str(self.managed)+'-other\0').encode())
        self.assertEqual(processes(self.managed, proc), [{'pid':11, 'cdp_ephemeral':True, 'localhost':True}])
        (self.managed/'DevToolsActivePort').write_text('1234\n/devtools/browser/test\n')
        ws = 'ws://127.0.0.1:1234/devtools/browser/test'
        self.assertEqual(endpoint(self.managed, fetch=lambda url: {'webSocketDebuggerUrl':ws}), ws)
        self.assertIsNone(endpoint(self.managed, fetch=lambda url: {'webSocketDebuggerUrl':'ws://evil.com/devtools/browser/test'}))

    def test_endpoint_refusal_is_distinct_from_timeout_or_unknown(self):
        (self.managed/'DevToolsActivePort').write_text('1234\n/devtools/browser/test\n')
        for error, expected in ((ConnectionRefusedError(111, 'refused'), 'refused'),
                                (URLError(ConnectionRefusedError(111, 'refused')), 'refused'),
                                (TimeoutError('timeout'), 'timeout'),
                                (URLError(TimeoutError('timeout')), 'timeout'),
                                (OSError('unexpected socket error'), 'unknown')):
            with self.subTest(expected=expected, error=type(error).__name__):
                self.assertEqual(endpoint_status(self.managed, fetch=Mock(side_effect=error))['state'], expected)

    def test_confirmed_shutdown_allows_explicit_restart_without_deleting_files(self):
        self.prepared()
        marker = self.managed/'DevToolsActivePort'
        marker.write_text('1234\n/devtools/browser/departed\n')
        lock = self.managed/'SingletonLock'
        lock.symlink_to(socket.gethostname() + '-87654321')
        owner = self.root/'.state/flow-profile-setup.json'
        data = json.loads(owner.read_text())
        data['active'] = {'root': str(self.managed), 'pid':87654321, 'owned':True, 'state':'connected_transport'}
        owner.write_text(json.dumps(data))
        running = []
        fake = Mock(pid=54321)
        fake.poll.return_value = None
        def launch(argv, **kwargs):
            self.assertTrue(marker.exists())
            self.assertEqual(os.readlink(lock), socket.gethostname() + '-87654321')
            running.append({'pid':54321, 'localhost':True, 'cdp_ephemeral':True})
            return fake
        with patch('profile_setup._pid_alive', return_value=False):
            result = start(self.root, grant=self.grant, source='User requested start after shutdown', runner=launch,
                           inspect_processes=lambda root:running,
                           inspect_endpoint_status=lambda root:{'state':'refused', 'endpoint':None},
                           inspect_endpoint=lambda root:'ws://127.0.0.1:1234/devtools/browser/new' if running else None)
        self.assertTrue(result['owned'])
        self.assertEqual(result['restart_evidence']['lock']['state'], 'local_dead')
        self.assertEqual(result['restart_evidence']['prior_owned_pid_dead'], 87654321)
        self.assertFalse(result['restart_evidence']['files_removed'])
        self.assertTrue(marker.exists())
        self.assertTrue(lock.is_symlink())

    def test_refused_port_and_absent_lock_allow_existing_unowned_root_restart(self):
        self.prepared()
        (self.managed/'DevToolsActivePort').write_text('1234\n/devtools/browser/departed\n')
        running = []
        fake = Mock(pid=54321)
        fake.poll.return_value = None
        def launch(argv, **kwargs):
            running.append({'pid':54321,'localhost':True,'cdp_ephemeral':True})
            return fake
        result = start(self.root, grant=self.grant, source='User requested existing profile start', runner=launch,
                       inspect_processes=lambda root:running,
                       inspect_endpoint_status=lambda root:{'state':'refused','endpoint':None},
                       inspect_endpoint=lambda root:'ws://127.0.0.1:1234/devtools/browser/new' if running else None)
        self.assertEqual(result['restart_evidence']['lock']['state'], 'absent')
        self.assertIsNone(result['restart_evidence']['prior_owned_pid_dead'])

    def test_timeout_foreign_or_live_lock_never_permit_restart(self):
        self.prepared()
        (self.managed/'DevToolsActivePort').write_text('1234\n/devtools/browser/departed\n')
        runner = Mock()
        with self.assertRaisesRegex(SetupBlocked, 'timeout'):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root:[], inspect_endpoint_status=lambda root:{'state':'timeout','endpoint':None})
        lock = self.managed/'SingletonLock'
        lock.symlink_to('another-computer-1234')
        with self.assertRaisesRegex(SetupBlocked, 'foreign'):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root:[], inspect_endpoint_status=lambda root:{'state':'refused','endpoint':None})
        self.assertEqual(os.readlink(lock), 'another-computer-1234')
        # Only the test fixture changes its own lock to model a different case.
        lock.unlink(); lock.symlink_to(socket.gethostname()+'-'+str(os.getpid()))
        self.assertEqual(lock_status(self.managed)['state'], 'local_live_or_unknown')
        with self.assertRaisesRegex(SetupBlocked, 'local_live_or_unknown'):
            start(self.root, grant=self.grant, source='Open', runner=runner,
                  inspect_processes=lambda root:[], inspect_endpoint_status=lambda root:{'state':'refused','endpoint':None})
        runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
