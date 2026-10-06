"""Layered (background + cut-out sticker) pipeline contracts: registry 1.2.0, plan validation, timeline, remote protocol."""
import copy
import unittest

from pilot import ROOT, read
from content_contract import validate_brief, validate_content, ContractError
from flow_prompts import compile as compile_prompt, PromptError
from scripts.story_plan import image_units, timeline, languages
import colab_bridge.job_protocol as job_protocol


def fixture():
    b = read(ROOT / 'examples/story-v3/brief.json')
    c = read(ROOT / 'examples/story-v3/content.json')
    c['brief_hash'] = 'TEST'
    return b, c


def words(text, count):
    parts = text.split()
    return [parts[min(i * max(1, len(parts) // (count + 1)), len(parts) - 1)] for i in range(count)]


def anchor_for(b, scene, word_index):
    out = {}
    for lang in languages(b):
        text = scene.get('narration_en' if lang == 'en' else 'narration', '')
        out[lang] = {'quote': words(text, 4)[word_index], 'occurrence': 1}
    return out


def make_layered(b, c):
    """Turn scene 0 into one background plus two stickers; scene 1 reuses the first sticker."""
    sc = c['scenes'][0]
    base = sc['images'][0]
    tmpl = dict(base, based_on=None, preserve='', visible_text=[], character_ids=[])
    sc['images'] = [dict(tmpl, id='BG_ONE', kind='background', description='Empty imperial hall with red pillars',
                         change='Empty background plate'),
                    dict(tmpl, id='STK_A', kind='sticker', description='One stick figure emperor in a yellow robe',
                         change='Emperor sticker'),
                    dict(tmpl, id='STK_B', kind='sticker', description='One stick figure goose with a red scarf',
                         change='Goose sticker')]
    sc['beats'] = [dict(sc['beats'][0], id='BEAT_BG', image_id='BG_ONE', effect='hold',
                        anchor=anchor_for(b, sc, 0))]
    sc['layers'] = [
        {'id': 'emperor', 'image_id': 'STK_A', 'anchor': anchor_for(b, sc, 0), 'fx': 'pop_wobble', 'x': 0.4, 'y': 0.55, 'w': 0.4},
        {'id': 'goose', 'image_id': 'STK_B', 'anchor': anchor_for(b, sc, 2), 'fx': 'slide_left', 'x': 0.7, 'y': 0.6, 'w': 0.3,
         'exit_anchor': anchor_for(b, sc, 3), 'exit_fx': 'suck'}]
    sc2 = c['scenes'][1]
    sc2['images'] = [dict(tmpl, id='BG_TWO', kind='background', description='Empty palace garden with pond', change='Empty plate')]
    sc2['beats'] = [dict(sc2['beats'][0], id='BEAT_BG2', image_id='BG_TWO', effect='hold', anchor=anchor_for(b, sc2, 0))]
    sc2['layers'] = [{'id': 'emperor2', 'image_id': 'STK_A', 'anchor': anchor_for(b, sc2, 1), 'fx': 'bounce', 'x': 0.5, 'y': 0.6, 'w': 0.4}]
    return c


class LayerPromptTests(unittest.TestCase):
    data = {'description': 'Empty imperial hall', 'aspect_ratio': '9:16'}

    def test_layer_purposes_compile_under_1_2_0(self):
        for purpose in ('layer_background', 'layer_sticker'):
            result = compile_prompt('NanoBanana2Lite', purpose, dict(self.data), '1.2.0')
            self.assertEqual(result['template_id'], 'flow.NanoBanana2Lite.' + purpose)
            self.assertIn('No Base scene reference is declared', result['prompt'])
        sticker = compile_prompt('NanoBanana2Lite', 'layer_sticker', dict(self.data), '1.2.0')['prompt']
        self.assertIn('pure white', sticker)
        self.assertNotIn('Reserve the specified caption band', sticker)
        background = compile_prompt('NanoBanana2Lite', 'layer_background', dict(self.data), '1.2.0')['prompt']
        self.assertIn('no people', background)

    def test_layer_purposes_rejected_before_1_2_0_and_with_base(self):
        with self.assertRaisesRegex(PromptError, 'FLOW_PURPOSE_UNSUPPORTED'):
            compile_prompt('NanoBanana2Lite', 'layer_sticker', dict(self.data), '1.1.0')
        with self.assertRaisesRegex(PromptError, 'FLOW_LAYER_INVALID'):
            compile_prompt('NanoBanana2Lite', 'layer_sticker', dict(self.data, change=['x']), '1.2.0')

    def test_legacy_versions_unchanged(self):
        before = compile_prompt('NanoBanana2', 'scene', dict(self.data), '1.1.0')
        again = compile_prompt('NanoBanana2', 'scene', dict(self.data), '1.1.0')
        self.assertEqual(before['sha256'], again['sha256'])


class LayeredPlanTests(unittest.TestCase):
    def check(self, b, c):
        validate_brief(ROOT, b)
        validate_content(ROOT, b, 1, 'TEST', c)

    def test_valid_layered_plan(self):
        b, c = fixture()
        make_layered(b, c)
        self.check(b, c)
        kinds = [u['kind'] for u in image_units(c)]
        self.assertEqual(kinds.count('background'), 2)
        self.assertEqual(kinds.count('sticker'), 2)

    def test_flat_scenes_unchanged(self):
        b, c = fixture()
        self.check(b, c)
        self.assertTrue(all(u['kind'] == 'scene' for u in image_units(c)))

    def test_two_backgrounds_rejected(self):
        b, c = fixture()
        make_layered(b, c)
        c['scenes'][0]['images'][1]['kind'] = 'background'
        with self.assertRaises(ContractError):
            self.check(b, c)

    def test_sticker_must_be_used_by_a_layer(self):
        b, c = fixture()
        make_layered(b, c)
        c['scenes'][0]['layers'].pop()
        with self.assertRaisesRegex(ContractError, 'LAYER_UNUSED'):
            self.check(b, c)

    def test_layer_cannot_reference_future_or_unknown_sticker(self):
        b, c = fixture()
        make_layered(b, c)
        c['scenes'][0]['layers'][0]['image_id'] = 'NOPE'
        with self.assertRaisesRegex(ContractError, 'LAYER_IMAGE'):
            self.check(b, c)

    def test_layer_anchor_must_exist_in_narration(self):
        b, c = fixture()
        make_layered(b, c)
        for lang in languages(b):
            c['scenes'][0]['layers'][0]['anchor'][lang]['quote'] = 'zzzzqqqq'
        with self.assertRaisesRegex(ContractError, 'LAYER_ANCHOR'):
            self.check(b, c)

    def test_sticker_quota_per_scene(self):
        b, c = fixture()
        make_layered(b, c)
        sc = c['scenes'][0]
        for i in range(4):
            sc['images'].append(dict(sc['images'][1], id='STK_X%d' % i))
            sc['layers'].append(dict(sc['layers'][0], id='lx%d' % i, image_id='STK_X%d' % i))
        with self.assertRaisesRegex(ContractError, 'LAYER_QUOTA'):
            self.check(b, c)


class LayeredTimelineTests(unittest.TestCase):
    def test_timeline_emits_background_and_timed_stickers(self):
        b, c = fixture()
        make_layered(b, c)
        lang = languages(b)[0]
        items = []
        segments = []
        t = 0.0
        for sc in c['scenes']:
            segments.append({'scene_id': sc['id'], 'start': t, 'end': t + 10.0,
                             'text': sc.get('narration_en' if lang == 'en' else 'narration', '')})
            t += 10.0
            for im in sc['images']:
                items.append({'scene_id': sc['id'], 'image_id': im['id'], 'ratio': '9:16', 'path': 'assets/%s.jpg' % im['id']})
        audio = {'tracks': {lang: {'segments': segments, 'duration': t}}}
        scenes = timeline(c, {'items': items}, audio, lang, '9:16')
        layers = scenes[0]['layers']
        self.assertTrue(layers[0]['bg'])
        self.assertEqual([x['id'] for x in layers[1:]], ['emperor', 'goose'])
        self.assertEqual(layers[1]['start'], 0.0)
        self.assertGreater(layers[2]['start'], layers[1]['start'])
        self.assertGreater(layers[2]['end'], layers[2]['start'])
        self.assertEqual(layers[2]['exitFx'], 'suck')
        self.assertEqual(scenes[1]['layers'][1]['src'], 'assets/STK_A.jpg')  # sticker reused across scenes
        self.assertEqual(len(scenes[0]['images']), 1)
        self.assertNotIn('layers', scenes[2])


class LayeredProtocolTests(unittest.TestCase):
    def test_matte_source_bundled_only_for_layered_jobs(self):
        import inspect
        src = inspect.getsource(job_protocol.build_render_request)
        self.assertIn("tools/matte_sticker.py", src)
        self.assertIn("scene.get('layers')", src)


if __name__ == '__main__':
    unittest.main()
