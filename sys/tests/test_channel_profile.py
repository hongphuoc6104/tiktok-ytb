"""New channel defaults freeze into briefs without changing old job data."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot import ROOT, read
from content_contract import validate_brief
from vocab import bank as vb
from vocab import test_bank as helpers


class EnglishChannelTests(unittest.TestCase):
    source = helpers.BankTests.source

    def setUp(self):
        helpers.BankTests.setUp(self)
        vb.write_json(self.tmp / 'channel.json', read(ROOT / 'vocab/channel.json'))
        self.source('money', 'pay|v|trả tiền|A1\nbank|n|ngân hàng|A2\n')
        self.source('nature', 'predator|n|động vật săn mồi|B1\necosystem|n|hệ sinh thái|C1\n')
        vb.build()

    def tearDown(self):
        helpers.BankTests.tearDown(self)

    def test_default_selection_is_b1_plus_with_explicit_override(self):
        picked = vb.cmd_next(helpers.args())['picked']
        self.assertEqual([x['word'] for x in picked], ['predator', 'ecosystem'])
        self.assertEqual([x['word'] for x in vb.cmd_next(helpers.args(level='A1'))['picked']], ['pay'])

    def test_brief_has_english_delivery_and_deferred_scene_plan(self):
        result = vb.cmd_draw(helpers.args(job='english', word='predator'))
        brief = vb.read_json(Path(result['brief']))
        validate_brief(ROOT, brief)
        self.assertEqual(brief['language'], 'en')
        self.assertIsNone(brief['scene_count'])
        self.assertEqual(brief['outputs'], [dict(aspect_ratio='9:16', language='en', subtitles=True, voice='reference-narrator', speed=.92)])
        self.assertEqual(brief['channel_profile']['id'], 'english-explanatory-2d')
        self.assertIn('predator.n', ' '.join(brief['planning']['domain_requirements']))
        self.assertFalse(any('Micro-Drama' in x or 'Foley' in x for x in brief['planning']['domain_requirements']))

    def test_scene_count_is_a_per_job_choice_and_saved_brief_is_not_rewritten(self):
        args = helpers.args(job='planned', word='predator', scene_count=7)
        result = vb.cmd_draw(args)
        path = Path(result['brief']); before = path.read_bytes()
        self.assertEqual(vb.read_json(path)['scene_count'], 7)
        profile = vb.read_json(self.tmp / 'channel.json')
        profile['voice'] = 'other'; profile['outputs'][0]['voice'] = 'other'
        vb.write_json(self.tmp / 'channel.json', profile)
        self.assertEqual(path.read_bytes(), before)
