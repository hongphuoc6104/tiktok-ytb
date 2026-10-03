"""Reproductions from actual desktop startup; no browser/provider invocation."""
import os
from pathlib import Path
import tempfile
import unittest
from profile_setup import processes
from b2_bridge import session_socket_path


class LiveSetupEdges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.proc = self.root / 'proc'
        self.proc.mkdir()
        self.browser_root = self.root / 'Browser with spaces'

    def process(self, title, pid=123):
        item = self.proc / str(pid)
        item.mkdir()
        (item / 'cmdline').write_bytes(title)

    def test_rewritten_chrome_title_preserves_exact_root_and_profile_spaces(self):
        title = f'/opt/google/chrome/chrome --user-data-dir={self.browser_root} --profile-directory=Profile 4 --remote-debugging-address=127.0.0.1 --remote-debugging-port=0 --no-first-run https://flow.google.com/'
        self.process(title.encode() + b'\0\0')
        self.assertEqual(processes(self.browser_root, self.proc), [{'pid':123, 'localhost':True, 'cdp_ephemeral':True}])
        self.assertEqual(processes(str(self.browser_root) + '-other', self.proc), [])

    def test_duplicate_root_options_are_not_a_reusable_browser(self):
        self.process(f'/opt/chrome --user-data-dir={self.browser_root} --user-data-dir=/other --remote-debugging-address=127.0.0.1 --remote-debugging-port=0'.encode())
        record = processes(self.browser_root, self.proc)[0]
        self.assertFalse(record['localhost'])
        self.assertFalse(record['cdp_ephemeral'])

    def test_renderer_process_title_is_excluded(self):
        self.process(f'/opt/chrome --type=renderer --user-data-dir={self.browser_root} --remote-debugging-port=0'.encode())
        self.assertEqual(processes(self.browser_root, self.proc), [])

    def test_long_worktree_uses_short_uid_scoped_distinct_socket(self):
        deep = self.root / ('a' * 80) / ('b' * 80)
        first = session_socket_path(deep)
        self.assertLess(len(os.fsencode(first)), 108)
        self.assertIn('video-pilot-' + str(os.getuid()), str(first))
        self.assertEqual(first, session_socket_path(deep))
        self.assertNotEqual(first, session_socket_path(deep / 'other'))
