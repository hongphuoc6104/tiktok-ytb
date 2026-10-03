"""Observable contract behavior; no providers, speech synthesis or video render."""
import json
import shutil
import subprocess
import unittest

from pilot import ROOT, read
from content_contract import validate_content, ContractError, validate_brief
from output_contract import outputs, languages, voice_settings
from scripts.story_plan import estimates


class OutputContractTests(unittest.TestCase):
    def fixture(self):
        brief = read(ROOT / 'examples/story-v3/brief.json')
        content = read(ROOT / 'examples/story-v3/content.json')
        brief.update(language='en', aspect_ratio='9:16', outputs=[
            {'aspect_ratio': '9:16', 'language': 'en', 'subtitles': True, 'voice': 'Alba', 'speed': .92}])
        content.update(brief_hash='TEST')
        messages = ['A predator hunts other animals for food.', 'The crocodile waits quietly near the water.', 'Small fish move away when danger comes.', 'The hunter needs food to survive.', 'A hawk can also hunt smaller animals.', 'Which animal is the predator in this story?']
        for scene, text in zip(content['scenes'], messages):
            scene['narration_en'] = text
            scene['narration'] = text
            for beat in scene['beats']:
                beat['anchor'] = {'en': {'quote': text, 'occurrence': 1}}
        for coverage in content['coverage']:
            scene = next(s for s in content['scenes'] if s['id'] == coverage['scene_id'])
            coverage['quote_en'] = scene['narration_en']
            coverage['quote'] = coverage['quote_en']
        return brief, content

    def test_portrait_english_validates_english_only_anchors_and_timing(self):
        brief, content = self.fixture()
        validate_brief(ROOT, brief)
        validate_content(ROOT, brief, 1, 'TEST', content)
        self.assertEqual(languages(brief), ['en'])
        self.assertEqual(list(estimates(brief, content)['languages']), ['en'])

    def test_portrait_english_requires_real_english_coverage_and_anchor(self):
        for target in ('coverage', 'anchor'):
            brief, content = self.fixture()
            if target == 'coverage':
                content['coverage'][0]['quote_en'] = 'A quote not in this scene'
            else:
                content['scenes'][0]['beats'][0]['anchor']['en']['quote'] = 'A quote not in this scene'
            with self.assertRaises(ContractError):
                validate_content(ROOT, brief, 1, 'TEST', content)

    def test_job_voice_rate_override_unrelated_defaults(self):
        brief, _ = self.fixture()
        self.assertEqual(voice_settings(brief, 'en', {'en_voice': 'Adam', 'en_speed': 1.08}),
                         {'voice': 'Alba', 'speed': .92})

    def test_aspect_does_not_choose_language_for_explicit_contract(self):
        for aspect in ('9:16', '16:9'):
            for language in ('vi', 'en'):
                brief = {'aspect_ratio': aspect, 'outputs': [dict(aspect_ratio=aspect, language=language, subtitles=False)]}
                self.assertEqual(languages(brief), [language])

    def test_legacy_default_routing_is_preserved(self):
        self.assertEqual(languages({'aspect_ratio': 'dual', 'language': 'vi'}), ['vi', 'en'])
        self.assertEqual(languages({'aspect_ratio': '9:16', 'language': 'vi'}), ['vi'])

    def test_conflicting_voice_and_invalid_contract_are_rejected(self):
        brief = {'aspect_ratio': 'dual', 'outputs': [
            dict(aspect_ratio='9:16', language='en', subtitles=True, speed=.92),
            dict(aspect_ratio='16:9', language='en', subtitles=False, speed=1.08)]}
        with self.assertRaises(ValueError):
            voice_settings(brief, 'en', {})
        for bad in ([], [None], [dict(aspect_ratio='9:16', language='en', subtitles='yes')]):
            with self.assertRaises(ValueError):
                outputs({'aspect_ratio': '9:16', 'outputs': bad})

    @unittest.skipUnless(shutil.which('node'), 'Node required for renderer contract')
    def test_renderer_uses_english_track_cues_and_portrait_timeline(self):
        script = """
import {outputPlans} from './renderer/outputs.mjs';
const props={aspect_ratio:'9:16',duration:99,scenes:[{id:'wrong-vi'}],
 outputs:[{aspect_ratio:'9:16',language:'en',subtitles:true}],
 tracks:{en:{audioSrc:'english.wav',duration:48.5,scenesByAspect:{'9:16':[{id:'english-portrait'}]},cues:[{text:'A predator hunts.',start:0,end:2}]}}};
const actual=outputPlans(props,true)[0];
let missingBlocked=false;
try {outputPlans({...props,tracks:{en:{...props.tracks.en,scenesByAspect:{'16:9':[]}}}},true);} catch {missingBlocked=true;}
console.log(JSON.stringify({actual,missingBlocked}));
"""
        result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=ROOT,
                                check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        actual = data['actual']['props']
        self.assertEqual((actual['width'], actual['height'], actual['audioSrc'], actual['duration']),
                         (1080, 1920, 'english.wav', 48.5))
        self.assertEqual(actual['scenes'][0]['id'], 'english-portrait')
        self.assertEqual(actual['cues'][0]['text'], 'A predator hunts.')
        self.assertFalse(actual['hideSubtitles'])
        self.assertTrue(data['missingBlocked'])
