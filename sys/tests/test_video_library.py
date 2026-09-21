"""Publication file handling; fake approvals only in a temporary sandbox."""
import tempfile
import unittest
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot import Blocked
import workflow


class VideoLibraryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.job = self.root / 'runs/demo'
        self.job.mkdir(parents=True)
        (self.job / 'portrait.mp4').write_bytes(b'portrait test fixture')
        (self.job / 'landscape.mp4').write_bytes(b'landscape test fixture')
        self.p = SimpleNamespace(root=self.root, refresh=lambda j: None,
            job=lambda j: self.job, path=lambda j, f: self.job / f,
            payload=lambda j, m: {'video': 'portrait.mp4',
                'video_9x16': 'portrait.mp4', 'video_16x9': 'landscape.mp4'})
        for name, value in [('settings', {}), ('approved', True), ('current', {'revision': 2})]:
            mock = patch.object(workflow, name, return_value=value)
            mock.start()
            self.addCleanup(mock.stop)

    def test_dual_exports_only_two_copies_inside_sandbox(self):
        paths = [Path(p) for p in workflow.publish_videos(self.p, 'demo')]
        self.assertEqual({p.name for p in paths}, {'demo_r2_9x16.mp4', 'demo_r2_16x9.mp4'})
        self.assertTrue(all(p.parent == self.root / 'video/demo' for p in paths))
        self.assertEqual(len(list((self.root / 'video/demo').iterdir())), 2)
        paths[0].write_bytes(b'edit published copy')
        self.assertEqual((self.job / 'portrait.mp4').read_bytes(), b'portrait test fixture')

    def test_symlink_output_folder_does_not_write_outside_library(self):
        (self.root / 'video').mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'video/demo').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Blocked):
            workflow.publish_videos(self.p, 'demo')
        self.assertEqual(list(outside.iterdir()), [])

    def test_unapproved_job_creates_no_library(self):
        with patch.object(workflow, 'approved', return_value=False):
            with self.assertRaises(Blocked):
                workflow.publish_videos(self.p, 'demo')
        self.assertFalse((self.root / 'video').exists())

    def test_failed_copy_cleans_up_temporary_file(self):
        with patch.object(workflow.shutil, 'copyfile', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                workflow.publish_videos(self.p, 'demo')
        self.assertEqual(list((self.root / 'video/demo').iterdir()), [])
