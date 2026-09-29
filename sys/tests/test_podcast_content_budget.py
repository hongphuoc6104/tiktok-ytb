import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from podcast.content_pipeline import generate_reviewed_script, PodcastContentError


class ContentBudgetTests(unittest.TestCase):
    def run_pipeline(self, root):
        return generate_reviewed_script('Đêm yên', brief={}, estimated_wpm=180, output_dir=root)

    def test_shared_three_rounds_survive_restart(self):
        script = {'parts': [{'id': 'P01'}, {'id': 'P02'}]}
        report = {'verdict': 'revise', 'summary': 'Còn lỗi', 'parts': [
            {'id': p, 'findings': ['Sửa lời']} for p in ('P01', 'P02')]}
        with tempfile.TemporaryDirectory() as root, \
             patch('podcast.content_pipeline.generate_script', return_value=script) as writer, \
             patch('podcast.content_pipeline.review_script', return_value=report) as reviewer, \
             patch('podcast.content_pipeline.repair_part', return_value={'repaired_script': script}) as repair, \
             patch('podcast.content_pipeline.validate_script', side_effect=lambda x, **kw: x):
            with self.assertRaises(PodcastContentError):
                self.run_pipeline(root)
            self.assertEqual(repair.call_count, 6)
            self.assertEqual(reviewer.call_count, 4)
            with self.assertRaises(PodcastContentError):
                self.run_pipeline(root)
            self.assertEqual(repair.call_count, 6)
            self.assertEqual(writer.call_count, 1)
            self.assertEqual(reviewer.call_count, 4)

    def test_pass_is_reused(self):
        script = {'parts': [{'id': 'P01'}]}
        report = {'verdict': 'pass', 'summary': 'Đạt', 'parts': []}
        with tempfile.TemporaryDirectory() as root, \
             patch('podcast.content_pipeline.generate_script', return_value=script) as writer, \
             patch('podcast.content_pipeline.review_script', return_value=report) as reviewer:
            self.run_pipeline(root)
            self.run_pipeline(root)
            self.assertEqual(writer.call_count, 1)
            self.assertEqual(reviewer.call_count, 1)

    def test_remote_timeout_does_not_replay(self):
        with tempfile.TemporaryDirectory() as root, \
             patch('podcast.content_pipeline.generate_script', side_effect=TimeoutError) as writer:
            with self.assertRaises(TimeoutError):
                self.run_pipeline(root)
            with self.assertRaisesRegex(PodcastContentError, 'đối chiếu'):
                self.run_pipeline(root)
            self.assertEqual(writer.call_count, 1)

    def test_legacy_history_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / 'reports').mkdir()
            with self.assertRaisesRegex(PodcastContentError, 'lịch sử'):
                self.run_pipeline(root)


if __name__ == '__main__':
    unittest.main()
