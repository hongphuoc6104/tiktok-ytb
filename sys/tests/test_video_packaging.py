"""GD5 'Dong goi' tests: tiny fixtures only, no Flow/network. Offline PIL images
stand in for approved media; content/audio/render payloads are hand-built dicts
matching the shapes adapters.py actually produces (segments with real
scene-boundary start times, images items with image_id/scene_id/path)."""
import json
import tempfile
import unittest
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw

import video_packaging
from pilot import Blocked


def make_still(path, size=(1000, 1400)):
    """Flat cream background (like the plan's doodle style) with a busy,
    high-contrast band across the vertical middle standing in for a character,
    so the flatness heuristic has a real top-vs-side choice to make."""
    img = Image.new('RGB', size, (235, 225, 200))
    draw = ImageDraw.Draw(img)
    w, h = size
    for y in range(int(h * 0.30), int(h * 0.75), 6):
        draw.line([(0, y), (w, y + 3)], fill=((y * 37) % 255, (y * 91) % 255, (y * 53) % 255), width=4)
    img.save(path, 'JPEG', quality=90)


CONTENT = {
    'scenes': [
        {'id': 'SC01', 'purpose': 'Mo dau', 'chapter': 'Buổi sáng thức dậy'},
        {'id': 'SC02', 'purpose': 'Kiem an', 'chapter': 'Đi săn bắt hái lượm'},
        {'id': 'SC03', 'purpose': 'Ket', 'chapter': 'Quay về hang lúc chạng vạng'},
    ],
    'claims': [
        {'scene_id': 'SC02', 'quote': 'x', 'language': 'vi', 'source_id': 'S1', 'fact': 'y'},
    ],
    'packaging': {
        'titles': ['Người tiền sử làm gì khi đói?', 'Tiêu đề phương án 2', 'Tiêu đề phương án 3'],
        'thumbnail': {'image_id': 'IMG02', 'text': 'đói khát tột cùng', 'emotion': 'shocked'},
        'hook': ('Bạn thức dậy giữa khu rừng 50.000 năm trước, bụng đói cồn cào. '
                  'Người tiền sử làm gì để sống sót đến khi mặt trời lặn?'),
        'tags': ['tiền sử', 'sinh tồn', 'đời sống cổ đại'],
    },
}

IMAGES = {'items': [
    {'scene_id': 'SC01', 'image_id': 'IMG01', 'path': 'sc01.jpg', 'prompt': 'p', 'source': 'google-flow'},
    {'scene_id': 'SC02', 'image_id': 'IMG02', 'path': 'sc02.jpg', 'prompt': 'p', 'source': 'google-flow'},
    {'scene_id': 'SC03', 'image_id': 'IMG03', 'path': 'sc03.jpg', 'prompt': 'p', 'source': 'google-flow'},
]}

AUDIO = {
    'duration': 512.4,
    'segments': [
        {'scene_id': 'SC01', 'text': 'a', 'start': 0.0, 'end': 140.0, 'path': 'sc01.wav'},
        {'scene_id': 'SC02', 'text': 'b', 'start': 145.3, 'end': 400.0, 'path': 'sc02.wav'},
        {'scene_id': 'SC03', 'text': 'c', 'start': 402.8, 'end': 512.4, 'path': 'sc03.wav'},
    ],
}

RENDER = {'video_16x9': 'landscape.mp4', 'duration': 512.4}

BRIEF = {'sources': [
    {'id': 'S1', 'title': 'Nghiên cứu về săn bắt hái lượm', 'reference': 'https://example.org/s1',
     'facts': ['fact 1']},
    {'id': 'S2', 'title': 'Nguồn không dùng tới trong claims', 'reference': 'https://example.org/s2',
     'facts': ['fact 2']},
]}


class PackagingModuleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.job_dir = Path(temp.name) / 'runs/demo'
        self.job_dir.mkdir(parents=True)
        for name in ('sc01.jpg', 'sc02.jpg', 'sc03.jpg'):
            make_still(self.job_dir / name)
        self.folder = Path(temp.name) / 'video/demo'
        self.payloads = {'content': CONTENT, 'images': IMAGES, 'audio': AUDIO, 'render': RENDER}
        self.p = SimpleNamespace(
            path=lambda j, f: self.job_dir / f,
            payload=lambda j, m: self.payloads[m],
            brief=lambda j: (BRIEF, 1, 'hash123'))

    def test_noop_without_packaging_field(self):
        payloads = dict(self.payloads, content={k: v for k, v in CONTENT.items() if k != 'packaging'})
        p = SimpleNamespace(**{**self.p.__dict__, 'payload': lambda j, m: payloads[m]})
        result = video_packaging.build(p, 'demo', self.folder)
        self.assertIsNone(result)
        self.assertFalse(self.folder.exists())

    def test_writes_thumbnail_variants_metadata_and_description(self):
        result = video_packaging.build(self.p, 'demo', self.folder)
        self.assertIsNotNone(result)
        for name in ('thumbnail.jpg', 'thumbnail-b.jpg', 'thumbnail-c.jpg'):
            path = self.folder / name
            self.assertTrue(path.is_file(), name)
            with Image.open(path) as im:
                self.assertEqual(im.size, (1280, 720))
                self.assertEqual(im.format, 'JPEG')

        metadata = json.loads((self.folder / 'metadata.json').read_text())
        self.assertEqual(metadata['titles'], CONTENT['packaging']['titles'])
        self.assertEqual(metadata['title'], CONTENT['packaging']['titles'][0])
        self.assertEqual(metadata['tags'], CONTENT['packaging']['tags'])
        self.assertEqual(metadata['duration'], 512.4)
        self.assertEqual(len(metadata['chapters']), 3)
        self.assertEqual(metadata['chapters'][0]['start_seconds'], 0.0)
        self.assertEqual(metadata['chapters'][0]['label'], 'Buổi sáng thức dậy')
        self.assertEqual(metadata['chapters'][1]['label'], 'Đi săn bắt hái lượm')
        self.assertEqual([s['id'] for s in metadata['sources']], ['S1'])

        description = (self.folder / 'description.txt').read_text()
        self.assertIn(CONTENT['packaging']['hook'], description)
        self.assertIn('0:00 Chương 1: Buổi sáng thức dậy', description)
        self.assertIn('Nguồn tham khảo:', description)
        self.assertIn('Nghiên cứu về săn bắt hái lượm', description)
        self.assertIn('https://example.org/s1', description)
        self.assertIn('AI', description)
        self.assertEqual(metadata['description'], description)

    def test_chapters_drop_scenes_closer_than_min_gap_but_keep_first_at_zero(self):
        close_audio = {
            'duration': 200.0,
            'segments': [
                {'scene_id': 'SC01', 'text': 'a', 'start': 0.3, 'end': 4.0, 'path': 'a.wav'},
                {'scene_id': 'SC02', 'text': 'b', 'start': 4.2, 'end': 50.0, 'path': 'b.wav'},
                {'scene_id': 'SC03', 'text': 'c', 'start': 50.5, 'end': 200.0, 'path': 'c.wav'},
            ],
        }
        chapters = video_packaging.build_chapters(CONTENT, close_audio)
        self.assertEqual([c['scene_id'] for c in chapters], ['SC01', 'SC03'])
        self.assertEqual(chapters[0]['start_seconds'], 0.0)

    def test_chapter_label_falls_back_to_scene_purpose(self):
        content = json.loads(json.dumps(CONTENT))
        del content['scenes'][0]['chapter']
        chapters = video_packaging.build_chapters(content, AUDIO)
        self.assertEqual(chapters[0]['label'], 'Mo dau')

    def test_thumbnail_image_id_falls_back_to_scene_id(self):
        images = {'items': [{'scene_id': 'SC02', 'path': 'sc02.jpg', 'prompt': 'p', 'source': 'google-flow'}]}
        content = json.loads(json.dumps(CONTENT))
        content['packaging']['thumbnail']['image_id'] = 'SC02'
        payloads = dict(self.payloads, images=images, content=content)
        p = SimpleNamespace(**{**self.p.__dict__, 'payload': lambda j, m: payloads[m]})
        result = video_packaging.build(p, 'demo', self.folder)
        self.assertIsNotNone(result)
        self.assertTrue((self.folder / 'thumbnail.jpg').is_file())

    def test_unknown_thumbnail_image_id_is_blocked(self):
        content = json.loads(json.dumps(CONTENT))
        content['packaging']['thumbnail']['image_id'] = 'NOPE'
        payloads = dict(self.payloads, content=content)
        p = SimpleNamespace(**{**self.p.__dict__, 'payload': lambda j, m: payloads[m]})
        with self.assertRaises(Blocked):
            video_packaging.build(p, 'demo', self.folder)

    def test_font_path_exists_and_covers_vietnamese_diacritics(self):
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            self.skipTest('fontTools not installed; glyph coverage was checked manually at authoring time')
        path = video_packaging.thumbnail_font_path()
        self.assertTrue(Path(path).is_file())
        cmap = TTFont(path).getBestCmap()
        sample = 'ƯƠàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
        missing = [c for c in sample if ord(c) not in cmap]
        self.assertEqual(missing, [])


class PublishVideosPackagingHookTests(unittest.TestCase):
    """Exercises workflow.publish_videos' minimal packaging hook end to end."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.job_dir = self.root / 'runs/demo'
        self.job_dir.mkdir(parents=True)
        (self.job_dir / 'landscape.mp4').write_bytes(b'landscape fixture')
        make_still(self.job_dir / 'sc02.jpg')
        payloads = {'content': CONTENT, 'images': IMAGES, 'audio': AUDIO, 'render': RENDER}
        self.p = SimpleNamespace(root=self.root, refresh=lambda j: None,
            job=lambda j: self.job_dir, path=lambda j, f: self.job_dir / f,
            payload=lambda j, m: payloads[m], brief=lambda j: (BRIEF, 1, 'hash123'))
        import workflow
        self.workflow = workflow
        for name, value in [('settings', {}), ('approved', True), ('current', {'revision': 1})]:
            mock = patch.object(workflow, name, return_value=value)
            mock.start()
            self.addCleanup(mock.stop)

    def test_publish_videos_also_writes_packaging_when_content_declares_it(self):
        paths = self.workflow.publish_videos(self.p, 'demo')
        self.assertEqual(len(paths), 1)
        folder = self.root / 'video/demo'
        for name in ('thumbnail.jpg', 'thumbnail-b.jpg', 'thumbnail-c.jpg', 'metadata.json', 'description.txt'):
            self.assertTrue((folder / name).is_file(), name)

    def test_publish_videos_skips_packaging_when_content_has_no_packaging_field(self):
        payloads = {'content': {k: v for k, v in CONTENT.items() if k != 'packaging'},
                    'images': IMAGES, 'audio': AUDIO, 'render': RENDER}
        p = SimpleNamespace(**{**self.p.__dict__, 'payload': lambda j, m: payloads[m]})
        self.workflow.publish_videos(p, 'demo')
        folder = self.root / 'video/demo'
        self.assertTrue((folder / 'demo_r1_16x9.mp4').is_file())
        self.assertFalse((folder / 'metadata.json').exists())


if __name__ == '__main__':
    unittest.main()
