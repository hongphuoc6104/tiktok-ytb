import shutil
import tempfile
import unittest
from pathlib import Path
from podcast.coordinator import Coordinator, EpisodeContext
from podcast.still import copy_selected_still, selected_still

class SelectedStillTests(unittest.TestCase):
    def test_selected_image_copied_unchanged_and_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'sys'
            shutil.copytree(Path(__file__).resolve().parents[1]/'assets/podcast',root/'assets/podcast')
            c=Coordinator(root);c.create_episode('Đêm yên',episode_id='still-test')
            ctx=EpisodeContext(c,'still-test')
            first=copy_selected_still(ctx)
            source,_=selected_still(root)
            self.assertEqual(Path(first['path']).read_bytes(),source.read_bytes())
            self.assertEqual(copy_selected_still(ctx),first)
            Path(first['path']).write_bytes(b'changed')
            with self.assertRaises(ValueError):
                copy_selected_still(ctx)

    def test_missing_or_changed_default_is_an_error_not_generation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'sys'
            shutil.copytree(Path(__file__).resolve().parents[1]/'assets/podcast',root/'assets/podcast')
            (root/'assets/podcast/sleep-default.png').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                selected_still(root)
