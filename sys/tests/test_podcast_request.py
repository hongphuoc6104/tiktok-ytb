import json
import tempfile
import unittest
from pathlib import Path
from podcast.coordinator import Coordinator, EpisodeError
from podcast.request import prepare_request


class RequestTests(unittest.TestCase):
    def test_request_reuse_and_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Coordinator(Path(folder) / 'sys')
            first = prepare_request(c, 'user-message-1', 'Căn phòng yên tĩnh')
            again = prepare_request(c, 'user-message-1', 'Căn phòng yên tĩnh')
            self.assertEqual(first['episode_id'], again['episode_id'])
            self.assertEqual(len(c.list_episodes()), 1)
            with self.assertRaises(EpisodeError):
                prepare_request(c, 'user-message-1', 'Chủ đề khác')
            other = prepare_request(c, 'user-message-2', 'Căn phòng yên tĩnh')
            self.assertNotEqual(first['episode_id'], other['episode_id'])

    def test_new_episode_rejects_unreviewed_script(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Coordinator(Path(folder) / 'sys')
            episode = prepare_request(c, 'new-policy', 'Một đêm yên')
            text = ' '.join(['yên'] * 625)
            payload = {'title': 'Một đêm yên', 'topic': 'Một đêm yên', 'estimated_wpm': 100,
                       'parts': [{'id': f'P{i:02}', 'script': text} for i in range(1, 5)]}
            with self.assertRaisesRegex(EpisodeError, 'đã duyệt'):
                c.set_script(episode['episode_id'], payload)
            self.assertEqual(c.get_manifest(episode['episode_id'])['script']['revision'], 0)

    def test_catalog_default_is_reserved_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'sys'
            (root / 'podcast').mkdir(parents=True)
            (root / 'podcast/catalog.json').write_text(json.dumps({'schema_version': 1, 'topics': [
                {'id': 'quiet-room', 'title': 'Căn phòng yên tĩnh', 'editorial_order': 1}]}))
            c = Coordinator(root)
            first = prepare_request(c, 'one')
            again = prepare_request(c, 'one')
            self.assertEqual(first['episode_id'], again['episode_id'])
            self.assertEqual(first['topic_id'], 'quiet-room')
            self.assertEqual(c.next_topics(5), [])


if __name__ == '__main__':
    unittest.main()
