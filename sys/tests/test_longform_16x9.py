"""GĐ2/GĐ3: Vietnamese 16:9 long-form and content-v3 extensions (clips,
overlays, new effects, chapters, packaging). Offline; no generation."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pilot import ROOT, read, write
from content_contract import validate_brief, validate_content, ContractError
from scripts.story_plan import (estimates, image_units, needs_english, review_plan, subtitles_enabled, timeline,
                                voice_language)
from scripts.editorial_audit import audit


def fixture(**brief):
    b = read(ROOT / 'examples/story-v3/brief.json'); c = read(ROOT / 'examples/story-v3/content.json')
    c['brief_hash'] = 'TEST'; b.update(brief)
    return b, c


def add_clip_and_overlays(c):
    sc = c['scenes'][0]
    sc['chapter'] = 'Vì sao góp ý khó'
    sc['images'].append({'id': 'SC01_C1', 'kind': 'clip', 'from_image': 'SC01_I1', 'motion': 'slow push-in on the desk',
                         'description': 'Hai người nhìn bản báo cáo', 'character_ids': ['CH01'], 'based_on': None,
                         'preserve': '', 'change': 'Chuyển động nhẹ', 'reason': 'Mở chương'})
    sc['beats'][0]['overlays'] = [{'type': 'chapter_title', 'text': 'Chương 1: Góp ý', 'x': .5, 'y': .2},
                                  {'type': 'counter', 'text': 'người', 'to': 3000, 'x': .8, 'y': .3, 'at': 1}]
    sc['beats'].append({'id': 'SC01_B2', 'image_id': 'SC01_C1', 'purpose': 'Mở chương', 'effect': 'pan_left',
                        'anchor': {'vi': {'quote': 'Hãy thử', 'occurrence': 1}}, 'focus': {'x': .5, 'y': .5},
                        'overlays': [{'type': 'label', 'text': 'Bản báo cáo', 'x': .3, 'y': .7, 'at': .5},
                                     {'type': 'map_pin', 'text': 'Hà Nội', 'x': .6, 'y': .4},
                                     {'type': 'arrow', 'x': .5, 'y': .5, 'angle': 45}]})
    c['scenes'][1]['beats'][0]['effect'] = 'pop'
    c['scenes'][2]['beats'][0]['effect'] = 'pan_right'
    c['packaging'] = {'titles': ['Người xưa góp ý thế nào?', 'Góp ý không mất lòng', 'Nói sao cho đúng?'],
                      'thumbnail': {'image_id': 'SC01_I1', 'text': 'GÓP Ý?', 'emotion': 'bối rối'},
                      'hook': 'Bạn từng ngại góp ý? Đây là cách nói rõ việc.', 'tags': ['góp ý', 'giao tiếp']}
    return c


class VoiceLanguageTests(unittest.TestCase):
    def check(self, b, c): validate_brief(ROOT, b); validate_content(ROOT, b, 1, 'TEST', c)

    def test_defaults_keep_old_behaviour(self):
        self.assertEqual(voice_language({'aspect_ratio': '16:9'}), 'en')
        self.assertEqual(voice_language({'aspect_ratio': '9:16'}), 'vi')
        self.assertTrue(needs_english({'aspect_ratio': '16:9'}))
        self.assertTrue(needs_english({'aspect_ratio': 'dual'}))
        self.assertFalse(needs_english({'aspect_ratio': '9:16'}))
        self.assertTrue(subtitles_enabled({'aspect_ratio': '9:16'}))
        b, c = fixture(aspect_ratio='16:9')
        with self.assertRaisesRegex(ContractError, 'NARRATION_EN'): self.check(b, c)

    def test_vietnamese_16x9_needs_no_english(self):
        b, c = fixture(aspect_ratio='16:9', voice_language='vi', subtitles=True, channel='tiensu',
                       duration={'min_seconds': 480, 'max_seconds': 780})
        c['duration'] = b['duration']
        self.check(b, c)
        self.assertFalse(needs_english(b))
        self.assertEqual(list(estimates(b, c)['languages']), ['vi'])
        self.assertIn('Giọng bản 16:9: tiếng Việt', review_plan(b, c))
        b['subtitles'] = False
        self.assertFalse(subtitles_enabled(b))
        self.assertIn('Phụ đề tiếng Việt: tắt', review_plan(b, c))

    def test_vertical_cannot_be_english(self):
        b, _ = fixture(voice_language='en')
        with self.assertRaisesRegex(ContractError, 'VOICE_LANGUAGE'): validate_brief(ROOT, b)

    def test_brief_clips_shape(self):
        b, _ = fixture(aspect_ratio='16:9', voice_language='vi', clips={'max': 10, 'model': 'veo-fast', 'variants': 2})
        validate_brief(ROOT, b)
        b['clips']['model'] = 'sora'
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): validate_brief(ROOT, b)

    def test_long_scene_chunks_stay_under_tts_limit(self):
        import adapters
        text = 'Mở đầu. ' + ' '.join(['người tiền sử đi tìm đá lửa'] * 40) + '. Kết thúc.'
        parts = adapters.chunks(text)
        self.assertTrue(all(len(x) <= 240 for x in parts))
        pos = 0
        for x in parts:  # every chunk is a verbatim slice, in order (timeline relies on it)
            pos = text.index(x, pos) + len(x)

    def test_render_vietnamese_16x9_props(self):
        import adapters
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'render'; out.mkdir()
            (root / 'voice.wav').write_bytes(b'TEST'); (root / 'image.png').write_bytes(b'TEST'); (root / 'clip.mp4').write_bytes(b'TEST')
            write(root / 'config.json', {'render_fps': 15})
            audio = {'wav': 'voice.wav', 'duration': 700, 'segments': [{'scene_id': 'SC01', 'text': 'Xin chào.', 'start': 0, 'end': 700}]}
            payloads = {'content': {}, 'images': {}, 'audio': audio}
            brief = {'aspect_ratio': '16:9', 'voice_language': 'vi'}
            p = SimpleNamespace(root=root, path=lambda job, path: root / path, payload=lambda job, module: payloads[module],
                                brief=lambda job: (brief, 1, 'TEST'))
            planned = [{'id': 'SC01', 'title': 'T', 'image': 'image.png', 'start': 0, 'end': 700,
                        'images': [{'id': 'B1', 'src': 'image.png', 'at': 0, 'effect': 'hold'},
                                   {'id': 'B2', 'src': 'clip.mp4', 'at': 5, 'effect': 'pop', 'kind': 'clip'}]}]
            with patch('scripts.story_plan.timeline', return_value=planned) as build, \
                    patch('adapters.subprocess.run', side_effect=RuntimeError('STOP')) as run:
                with self.assertRaisesRegex(RuntimeError, 'STOP'): adapters.render(p, 'TEST', out)
            self.assertEqual(build.call_args.args[-2:], ('vi', '16:9'))
            self.assertGreaterEqual(run.call_args.kwargs['timeout'], 700 * 8)
            props = read(out / 'props.json')
            self.assertEqual((props['voice_language'], props['subtitles'], props['fps']), ('vi', True, 15))
            self.assertNotIn('en_scenes', props)
            self.assertTrue(props['cues'])
            self.assertTrue(props['scenes'][0]['images'][1]['src'].endswith('.mp4'))
            self.assertTrue(adapters.needs_en(p, 'TEST') is False)

    def test_editorial_audit_applies_to_vietnamese_16x9(self):
        cue = [dict(text='"', start=0, end=1)]
        self.assertFalse(audit({'aspect_ratio': '16:9', 'cues': cue})['captions_applicable'])
        self.assertTrue(audit({'aspect_ratio': '16:9', 'voice_language': 'vi', 'cues': cue})['captions_applicable'])
        self.assertFalse(audit({'aspect_ratio': '16:9', 'voice_language': 'vi', 'subtitles': False, 'cues': cue})['captions_applicable'])

    def test_output_plans(self):
        code = """import {outputPlans} from './renderer/outputs.mjs';
        const p={aspect_ratio:'16:9',voice_language:'vi',duration:600,scenes:[{id:'SC01'}]};
        const a=outputPlans(p,false);const b=outputPlans({...p,subtitles:false},false);
        const d=outputPlans({...p,aspect_ratio:'dual',horizontal_scenes:[{id:'H'}]},false);
        let blocked=false;try{outputPlans({...p,voice_language:undefined},false)}catch{blocked=true}
        console.log(JSON.stringify({a,b,d,blocked}));"""
        r = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', code], cwd=ROOT, text=True))
        a = r['a'][0]['props']
        self.assertEqual((a['width'], a['height'], a['audioSrc'], a['hideSubtitles'], a['duration']), (1920, 1080, 'narration.wav', False, 600))
        self.assertTrue(r['b'][0]['props']['hideSubtitles'])
        self.assertEqual(r['d'][1]['props']['scenes'], [{'id': 'H'}])
        self.assertEqual(r['d'][1]['props']['audioSrc'], 'narration.wav')
        self.assertTrue(r['blocked'])


class ContentExtensionTests(unittest.TestCase):
    def check(self, b, c): validate_brief(ROOT, b); validate_content(ROOT, b, 1, 'TEST', c)

    def test_old_content_still_valid(self):
        b, c = fixture(); self.check(b, c)

    def test_clip_overlays_effects_packaging_valid(self):
        b, c = fixture(); add_clip_and_overlays(c); self.check(b, c)
        units = image_units(c)
        clip = next(u for u in units if u['id'] == 'SC01_C1')
        self.assertEqual((clip['kind'], clip['from_image'], clip['visible_text']), ('clip', 'SC01_I1', []))
        self.assertNotIn('kind', units[0])
        text = review_plan(b, c)
        for needle in ['Chương: Vì sao góp ý khó', 'Clip SC01_C1', 'Overlay: chapter_title', '## Đóng gói']:
            self.assertIn(needle, text)

    def test_clip_needs_same_scene_still(self):
        b, c = fixture(); add_clip_and_overlays(c)
        c['scenes'][0]['images'][1]['from_image'] = 'SC02_I1'
        with self.assertRaisesRegex(ContractError, 'CLIP_SOURCE'): self.check(b, c)
        b, c = fixture(); add_clip_and_overlays(c); del c['scenes'][0]['images'][1]['from_image']
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)

    def test_clip_has_no_visible_text_and_still_has_no_motion(self):
        b, c = fixture(); add_clip_and_overlays(c)
        c['scenes'][0]['images'][1]['visible_text'] = [{'text': 'A', 'placement': 'giữa', 'object': 'bảng'}]
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)
        b, c = fixture(); c['scenes'][0]['images'][0]['motion'] = 'pan'
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)
        b, c = fixture(); del c['scenes'][0]['images'][0]['visible_text']
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)

    def test_unknown_effect_rejected(self):
        b, c = fixture(); c['scenes'][0]['beats'][0]['effect'] = 'spin'
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)

    def test_overlay_rules(self):
        cases = [(lambda ov: ov.pop('to'), 'OVERLAY'),
                 (lambda ov: ov.update(type='label', angle=10), 'OVERLAY'),
                 (lambda ov: ov.update(type='label', text=''), 'OVERLAY'),
                 (lambda ov: ov.update(type='label', text='Mã SC01_I1'), 'INTERNAL_LABEL'),
                 (lambda ov: ov.update(type='label', text='x' * 45), 'OVERLAY'),
                 (lambda ov: ov.update(x=1.5), 'SCHEMA'),
                 (lambda ov: ov.update(type='banner'), 'SCHEMA')]
        for change, code in cases:
            b, c = fixture(); add_clip_and_overlays(c)
            change(c['scenes'][0]['beats'][0]['overlays'][1])
            with self.subTest(code=code), self.assertRaisesRegex(ContractError, code): self.check(b, c)

    def test_packaging_shape(self):
        b, c = fixture(); add_clip_and_overlays(c); c['packaging']['thumbnail']['image_id'] = 'SC01_C1'
        with self.assertRaisesRegex(ContractError, 'PACKAGING'): self.check(b, c)
        b, c = fixture(); add_clip_and_overlays(c); c['packaging']['titles'].pop()
        with self.assertRaisesRegex(ContractError, 'SCHEMA'): self.check(b, c)

    def test_timeline_carries_overlays_chapter_and_clip(self):
        b, c = fixture(); add_clip_and_overlays(c); c['scenes'] = c['scenes'][:1]
        sc = c['scenes'][0]
        images = {'items': [{'scene_id': 'SC01', 'image_id': 'SC01_I1', 'ratio': '16:9', 'path': 'media/SC01_I1.png'},
                            {'scene_id': 'SC01', 'image_id': 'SC01_C1', 'ratio': '16:9', 'path': 'media/SC01_C1.mp4'}]}
        audio = {'segments': [{'scene_id': 'SC01', 'start': 0, 'end': 10, 'text': sc['narration']}]}
        out = timeline(c, images, audio, 'vi', '16:9')[0]
        self.assertEqual(out['chapter'], 'Vì sao góp ý khó')
        first, second = out['images']
        self.assertNotIn('kind', first)
        self.assertEqual(first['overlays'][0]['at'], 0)
        self.assertEqual(second['kind'], 'clip')
        self.assertEqual([o['type'] for o in second['overlays']], ['label', 'map_pin', 'arrow'])


if __name__ == '__main__':
    unittest.main()
