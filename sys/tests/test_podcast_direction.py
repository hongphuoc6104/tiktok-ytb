import copy
import unittest
from podcast.direction import validate_direction, locked_content
from podcast.writer import script_schema
from podcast.content_review import _validate_review


def part():
    return {'id': 'P01', 'script': 'Mình đặt chiếc cốc xuống bàn. Căn phòng đã yên.',
            'voice_direction': {'delivery': 'Kể nhẹ và gần gũi, không diễn thuyết.',
                                'ending': 'Nối ý nhẹ nhàng sang phần tiếp theo.',
                                'cues': [{'quote': 'chiếc cốc xuống bàn', 'intent': 'Giữ nhịp câu tự nhiên.'}]}}


class DirectionTests(unittest.TestCase):
    def test_anchor_must_remain_exact(self):
        p = part()
        validate_direction(p)
        p['script'] = 'Câu đã thay đổi.'
        with self.assertRaises(ValueError):
            validate_direction(p)

    def test_lock_tracks_direction_and_engine(self):
        p = part()
        original = locked_content({'parts': [p]}, {'speed': 0.9})
        self.assertNotEqual(original['sha256'], locked_content({'parts': [p]}, {'speed': 1})['sha256'])
        p['voice_direction']['ending'] = 'Khép lại thật nhẹ và yên tĩnh.'
        self.assertNotEqual(original['sha256'], locked_content({'parts': [p]}, {'speed': 0.9})['sha256'])

    def test_schema_requires_direction(self):
        self.assertIn('voice_direction', script_schema()['properties']['parts']['items']['required'])

    def test_review_accepts_real_direction_evidence_only(self):
        parts = [dict(copy.deepcopy(part()), id=f'P{i:02}') for i in range(1, 5)]
        findings = [{'id': p['id'], 'findings': []} for p in parts]
        findings[0]['findings'] = [{'category': 'voice_direction', 'evidence': 'Kể nhẹ và gần gũi',
                                  'severity': 'minor', 'issue': 'Chưa rõ nhịp', 'recommendation': 'Sửa cụ thể'}]
        raw = {'verdict': 'revise', 'summary': 'Cần sửa nhịp', 'parts': findings}
        metrics = {'parts': [{'id': p['id']} for p in parts]}
        self.assertEqual(_validate_review(raw, {'parts': parts}, metrics)['verdict'], 'revise')
        findings[0]['findings'][0]['evidence'] = 'Câu không tồn tại'
        with self.assertRaises(RuntimeError):
            _validate_review(raw, {'parts': parts}, metrics)


if __name__ == '__main__':
    unittest.main()
