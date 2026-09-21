"""Scratch cleanup must preserve evidence regardless of its name or age."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import clean_production as cleanup


class ScratchCleanupTests(unittest.TestCase):
    def test_preserves_old_media_nested_evidence_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scratch = root / 'scratch'
            scratch.mkdir()
            image = scratch / 'screen.png'
            image.write_bytes(b'UI evidence')
            nested = scratch / 'tmp_capture'
            nested.mkdir()
            (nested / 'evidence.json').write_text('{}')
            outside = root / 'outside'
            outside.mkdir()
            link = scratch / 'tmp_link'
            link.symlink_to(outside, target_is_directory=True)
            for item in (image, nested):
                os.utime(item, (1, 1))
            with patch.object(cleanup, 'SCRATCH_DIR', scratch):
                cleanup.clean_scratch_whitelist()
            self.assertEqual(image.read_bytes(), b'UI evidence')
            self.assertTrue((nested / 'evidence.json').exists())
            self.assertTrue(link.is_symlink())
            self.assertTrue(outside.exists())

    def test_dry_run_and_retention_for_empty_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            old = scratch / 'tmp_old'
            fresh = scratch / 'tmp_fresh'
            unrelated = scratch / 'other'
            for item in (old, fresh, unrelated):
                item.mkdir()
            os.utime(old, (1, 1))
            os.utime(unrelated, (1, 1))
            with patch.object(cleanup, 'SCRATCH_DIR', scratch):
                cleanup.clean_scratch_whitelist(dry_run=True)
                self.assertTrue(old.exists())
                cleanup.clean_scratch_whitelist()
            self.assertFalse(old.exists())
            self.assertTrue(fresh.exists())
            self.assertTrue(unrelated.exists())

    def test_symlink_scratch_root_is_never_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / 'outside'
            outside.mkdir()
            old = outside / 'tmp_old'
            old.mkdir()
            os.utime(old, (1, 1))
            link = root / 'scratch'
            link.symlink_to(outside, target_is_directory=True)
            with patch.object(cleanup, 'SCRATCH_DIR', link):
                cleanup.clean_scratch_whitelist()
            self.assertTrue(old.exists())
