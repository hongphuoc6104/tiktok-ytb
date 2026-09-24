"""Regression checks for the real text front end and review gates; no fake quality scores saved."""
import copy
import importlib
import tempfile
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch

import lab
from lab import example, speech_text, text_pieces, digest, validate_review, meets_threshold
from runtime import front_end, preserve_terminal, units, Renderer


class FrontEndTests(unittest.TestCase):
    def test_i_correction_only_inside_annotated_english(self):
        item = example('x', 'mixed', 'Ai gọi vậy? Ai wake at six every morning.', ['Ai wake at six every morning.'])
        before = copy.deepcopy(item)
        self.assertEqual(speech_text(item, 'tagged'), 'Ai gọi vậy? <en>I wake at six every morning.</en>')
        self.assertEqual(item, before)

    def test_longest_annotation_and_no_substring_matches(self):
        item = example('x', 'mixed', 'wake, wakes, awake; I wake at six.', ['wake', 'I wake at six.'])
        self.assertEqual([s['text'] for s in item['en_spans']], ['wake', 'I wake at six.'])

    def test_preserve_question_and_exclamation_through_real_frontend(self):
        v3 = importlib.import_module('vieneu.v3turbo')
        original = v3.phonemize_text_with_emotions
        for text, terminal in [('Bạn tỉnh chưa?', '?'), ('Ôi, đẹp quá!', '!'), ('Mẹ ơi,', ',')]:
            trace = []
            with front_end('preserve', trace):
                chunks, _ = v3.normalize_to_chunks_v3_with_gaps(text)
                phones = [v3.phonemize_text_with_emotions(c) for c in chunks]
                self.assertTrue(chunks[-1].endswith(terminal), chunks)
                self.assertTrue(phones[-1].endswith(terminal), phones)
            self.assertIs(v3.phonemize_text_with_emotions, original)

    def test_frontend_restores_after_failure(self):
        v3 = importlib.import_module('vieneu.v3turbo')
        original = v3.phonemize_text_with_emotions
        with self.assertRaises(RuntimeError):
            with front_end('preserve', []):
                raise RuntimeError('test')
        self.assertIs(v3.phonemize_text_with_emotions, original)

    def test_number_and_acronym_normalization_still_works(self):
        v3 = importlib.import_module('vieneu.v3turbo')
        with front_end('preserve', []):
            chunks, _ = v3.normalize_to_chunks_v3_with_gaps('Bạn có 12 cuốn sách và học IELTS chưa?')
            self.assertNotIn('12', ' '.join(chunks))
            self.assertTrue(v3.phonemize_text_with_emotions(chunks[0]).endswith('?'))

    def test_english_tags_survive_and_are_not_phonemized_as_words(self):
        v3 = importlib.import_module('vieneu.v3turbo')
        with front_end('preserve', []):
            chunks, _ = v3.normalize_to_chunks_v3_with_gaps('Ví dụ: <en>I wake at six every morning.</en> Nghĩa là thức giấc.')
            phones = ' '.join(v3.phonemize_text_with_emotions(c) for c in chunks)
            self.assertIn('aɪ', phones)
            self.assertIn('eɪ', phones)
            self.assertNotIn('<en>', phones)

    def test_language_split_keeps_whole_english_sentence(self):
        item = example('x', 'mixed', 'Ví dụ: I wake at six every morning. Nghĩa là thức giấc.', ['I wake at six every morning.'])
        result = units(item, dict(split='language', language='tagged'))
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1], '<en>I wake at six every morning.</en>')

    def test_sentence_split_preserves_all_text(self):
        item = example('x', 'mixed', 'Ví dụ: "I wake at six." Bạn tỉnh chưa?', ['I wake at six.'])
        result = units(item, dict(split='sentence', language='standard'))
        self.assertEqual(' '.join(result), item['display_text'])


class GateTests(unittest.TestCase):
    def setUp(self):
        self.plan = dict(clips=[dict(clip_id='one', criteria=['en_sound','identity'])])
        self.review = dict(plan_digest=digest(self.plan), reviewer='test fixture', listened=True,
                           english_competent=True, ratings=[dict(clip_id='one', heard=True,
                           scores=dict(en_sound=4, identity=5), errors=[])])

    def test_rejects_unheard_missing_duplicate_and_invalid_scores(self):
        mutations = [lambda r:r.update(listened=False), lambda r:r.update(english_competent=False),
                     lambda r:r.update(ratings=[]), lambda r:r['ratings'].append(r['ratings'][0]),
                     lambda r:r['ratings'][0]['scores'].update(en_sound=6),
                     lambda r:r.update(plan_digest='wrong')]
        for mutate in mutations:
            r = copy.deepcopy(self.review); mutate(r)
            with self.assertRaises(ValueError): validate_review(self.plan, r)

    def test_threshold_rejects_bad_single_item_and_hard_error(self):
        ratings = self.review['ratings']
        self.assertTrue(meets_threshold(ratings))
        ratings[0]['errors'] = [dict(seconds=1, description='wrong word')]
        self.assertFalse(meets_threshold(ratings))
        ratings[0]['errors'] = []; ratings[0]['scores']['en_sound'] = 2
        self.assertFalse(meets_threshold(ratings))

    def test_identity_changes_with_take_and_settings(self):
        a = dict(take=0, punctuation='current')
        self.assertNotEqual(digest(a), digest(dict(a, take=1)))
        self.assertNotEqual(digest(a), digest(dict(a, punctuation='preserve')))


class ExperimentFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(lab, 'DATA', self.root).start()
        self.corpus = [example(f'T{i:02}', 'mixed', 'Bạn đọc wake nhé.', ['wake']) for i in range(1,10)]
        self.corpus += [example('H01', 'vi', 'Chưa dùng để chọn.', partition='holdout'),
                        example('R-SC01', 'mixed', 'Đọc wake.', ['wake'], 'real'),
                        example('P03', 'en', 'wake', ['wake'], 'probe'),
                        example('P04', 'en', 'get up', ['get up'], 'probe')]
        lab.write(self.root/'corpus.json', self.corpus)
        lab.write(self.root/'frozen.json', dict(corpus_sha256=lab.file_hash(self.root/'corpus.json'), protected={}))

    def test_missing_listening_decision_blocks_next_round(self):
        with self.assertRaisesRegex(ValueError, 'Chưa có kết quả nghe'):
            lab.make_plan('B')
        self.assertFalse((self.root/'rounds/B').exists())

    def test_holdout_only_in_final_and_d_has_three_takes(self):
        with patch.object(lab, 'load_decision', return_value=dict(config=lab.DEFAULT.copy(), selected='scene')), \
             patch.object(lab, 'hardest', return_value=[f'T{i:02}' for i in range(1,9)]):
            for stage in lab.STAGES:
                plan = lab.make_plan(stage)
                ids = {c['sample_id'] for c in plan['clips']}
                self.assertEqual('H01' in ids, stage == 'final')
                if stage == 'D':
                    self.assertEqual(len(plan['clips']), 72)
                    self.assertEqual({c['take'] for c in plan['clips']}, {0,1,2})

    def test_corpus_mutation_is_detected(self):
        lab.write(self.root/'corpus.json', [])
        with self.assertRaisesRegex(ValueError, 'Bộ câu'):
            lab.verify_frozen()

    def test_blind_labels_are_unique_per_item_and_stable_on_resume(self):
        a = lab.make_plan('A'); b = lab.make_plan('A')
        self.assertEqual(a, b)
        for item in self.corpus:
            labels = [c['blind_label'] for c in a['clips'] if c['sample_id'] == item['id']]
            self.assertEqual(len(labels), len(set(labels)))

    def test_speed_and_post_reuse_exact_raw_while_takes_do_not(self):
        # Explicit synthetic unit fixture only, never saved into experiment artifacts.
        import numpy as np
        class FakeTTS:
            calls = 0
            def infer(self, text, **kw):
                self.calls += 1
                return np.random.uniform(-.05,.05,12000).astype('float32')
        renderer = Renderer.__new__(Renderer)
        renderer.data = self.root
        renderer.environment = {'test_fixture': True}
        renderer.voice = 'unit-test'
        renderer.sr = 48000
        renderer.tts = FakeTTS()
        item = self.corpus[0]
        clip = dict(take=0, settings=lab.DEFAULT.copy())
        a, wa, _ = renderer.source(item, clip)
        other = copy.deepcopy(clip); other['settings'].update(speed=1.0, post='master')
        b, wb, _ = renderer.source(item, other)
        self.assertEqual(a,b); np.testing.assert_array_equal(wa,wb)
        self.assertEqual(renderer.tts.calls,1)
        other['take'] = 1
        c, wc, _ = renderer.source(item, other)
        self.assertNotEqual(a,c); self.assertEqual(renderer.tts.calls,2)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg unavailable')
    def test_real_postprocessing_matches_levels_and_keeps_sample_count(self):
        import numpy as np
        import soundfile as sf
        renderer = Renderer.__new__(Renderer)
        renderer.data = self.root; renderer.sr = 48000
        t = np.arange(96000)/48000
        wav = (.16*np.sin(2*np.pi*220*t)+.03*np.sin(2*np.pi*4200*t)).astype('float32')
        cache = self.root/'cache'/'synthetic-unit-fixture'; cache.mkdir(parents=True)
        sf.write(cache/'raw.wav',wav,48000,subtype='FLOAT')
        source_hash = lab.file_hash(cache/'raw.wav')
        renderer.source = lambda item,clip: ('synthetic-unit-fixture',wav,{'sha256':source_hash})
        results=[]
        for post in ['level','master']:
            settings = dict(lab.DEFAULT, speed=1.0, post=post)
            results.append(renderer.render(self.corpus[0],dict(clip_id=post,settings=settings),self.root/'round'))
        self.assertEqual(results[0]['source_sha256'],results[1]['source_sha256'])
        for result in results:
            self.assertEqual(result['technical']['samples'],96000)
            self.assertLess(abs(result['technical']['lufs']+23),.5)


if __name__ == '__main__':
    unittest.main()
