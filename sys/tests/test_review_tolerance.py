"""80/20 brand-tolerance review gate; replays real scold-002/003 findings as fixtures, never calls agy."""
import copy
import tempfile
import unittest
from unittest.mock import patch

import jsonschema
from pilot import ROOT, Blocked, read
import machine_review as mr
import workflow as wf
from scripts.director_context import context, tolerance_guidance, TOLERANCE_CHECKS
import test_image_repairs as repair_tests

RULE = (ROOT / '.agents/rules/brand_tolerance.md').read_text()
OK = 'TEST fixture only, not production.'


def checks(**over):
    out = {k: {'verdict': 'pass', 'evidence': OK} for k in mr.CRITERIA['media']}
    for k in TOLERANCE_CHECKS:
        if k in out: out[k].update(tolerated_deviations=[], blocking_defects=[])
    for k, v in over.items(): out[k] = dict(out[k], **v)
    return out


def pair(target, ids, same=False):
    return {'target': target, 'before': {'path': 'a', 'sha256': 'a' * 64}, 'after': {'path': 'b', 'sha256': ('a' if same else 'b') * 64},
            'issues': [{'id': i, 'status': 'remaining', 'evidence': OK, 'instruction': 'x'} for i in ids]}


def progress(verdict='pass', resolved=(), remaining=(), new=(), tolerated=None):
    out = {'verdict': verdict, 'evidence': OK, 'resolved': list(resolved), 'remaining': list(remaining), 'new': list(new)}
    if tolerated is not None: out['tolerated'] = list(tolerated)
    return out


def gate(result, pairs=()):
    """Same order as machine_review.review: defaults, schema, deterministic settle."""
    result = copy.deepcopy(result); mr.defaults(result)
    jsonschema.validate(result, mr.build_schema('media', 'ID', pairs))
    return mr.settle(result, pairs)


# Excerpts copied from production responses (read-only evidence), vocab-scold-003 0b3ec5c1 and vocab-scold-002 144e80f6.
OLD_003_CC = {'verdict': 'fail', 'evidence': 'IMG_SC01_01_9x16: Đầu nhân vật bị vẽ thêm lông mày cong, nếp nhăn trán và 5 giọt mồ hôi. '
              'IMG_SC02_01_9x16: Tay chỉ vẽ dạng găng tay trắng; bàn chân là nét que rỗng màu trắng.'}
OLD_002_SC05 = {'verdict': 'fail', 'evidence': "Khuyết điểm cũ 'hands' chưa được giải quyết: găng tay hoạt hình ngón cái chĩa lên. "
                "Lỗi mới 'extra-limbs': hai nhánh que thừa chĩa ngang mọc ra từ hai bên cùi chỏ.",
                'resolved': [], 'remaining': ['hands'], 'new': ['extra-limbs']}


class ToleranceContextTests(unittest.TestCase):
    def test_review_stages_receive_rule_file_and_binding_directive(self):
        for stage in ('media', 'video', 'registration'):
            text = context(ROOT, stage, {'topic': 'Học từ vựng scold'})
            self.assertIn(RULE, text)
            self.assertIn('fail ONLY when blocking_defects is non-empty', text)
            self.assertIn('not a visual_continuity failure', text)
        for stage in ('outline', 'content'):
            self.assertNotIn(RULE, context(ROOT, stage, {'topic': 'Học từ vựng scold'}))

    def test_missing_rule_file_falls_back_to_builtin_summary(self):
        with tempfile.TemporaryDirectory() as root:
            text = tolerance_guidance(root)
        self.assertIn('built-in summary', text)
        self.assertIn('#8CCFE8', text)
        self.assertIn('fail ONLY when blocking_defects is non-empty', text)


class ReplayTests(unittest.TestCase):
    def test_old_fail_without_blocking_structure_is_rejected_not_passed(self):
        old = checks(); old['character_consistency'] = dict(OLD_003_CC)  # verbatim legacy shape: verdict + evidence only
        with self.assertRaisesRegex(jsonschema.ValidationError, 'blocking_defects'):
            gate({'identity': 'ID', 'inspected_files': [], 'checks': old})

    def test_scold003_tolerated_face_hands_feet_become_pass_with_notes(self):
        cc = dict(OLD_003_CC, tolerated_deviations=['IMG_SC01_01: lông mày cong, nếp nhăn trán, giọt mồ hôi',
                                                    'IMG_SC02_01: tay găng trắng, bàn chân viền rỗng'])
        verdicts, overridden = gate({'identity': 'ID', 'inspected_files': [], 'checks': checks(character_consistency=cc)})
        self.assertTrue(all(v == 'pass' for v in verdicts.values()))
        self.assertEqual(overridden, {'character_consistency': {'reviewer': 'fail', 'effective': 'pass'}})

    def test_scold003_unchanged_pixels_tolerated_repair_and_continuity_variation(self):
        # 5557a098: same SHA before/after; residue is eyebrows/creases; continuity failed on hand/foot variation and vase pattern.
        vc = {'verdict': 'fail', 'evidence': 'Bàn tay lúc găng trắng lúc chấm đen; bình hoa đổi hoa văn giữa SC01_01 và SC01_02.',
              'tolerated_deviations': ['biến thiên bàn tay/bàn chân', 'hoa văn bình hoa khác nhẹ, vẫn là bình vỡ']}
        pairs = [pair('IMG_SC01_01_9x16', ['visual'], same=True)]
        result = {'identity': 'ID', 'inspected_files': [], 'checks': checks(visual_continuity=vc),
                  'repair_progress': {'IMG_SC01_01_9x16': progress('fail', tolerated=['visual'])}}
        verdicts, overridden = gate(result, pairs)
        self.assertTrue(all(v == 'pass' for v in verdicts.values()))
        self.assertEqual(set(overridden), {'visual_continuity', 'repair:IMG_SC01_01_9x16'})
        result['repair_progress']['IMG_SC01_01_9x16'] = progress('pass', resolved=['visual'])
        with self.assertRaisesRegex(Blocked, 'ảnh không đổi'):
            gate(result, pairs)

    def test_scold002_extra_limbs_still_blocks_while_mitten_hands_are_tolerated(self):
        cc = {'verdict': 'fail', 'evidence': 'IMG_SC05_01: hai nhánh que thừa chĩa ngang từ cùi chỏ.',
              'tolerated_deviations': ['IMG_SC05_01: tay găng ngón cái', 'IMG_SC01_01: lông mày, bàn chân viền rỗng'],
              'blocking_defects': [{'category': 'extra_or_missing_limbs', 'target': 'IMG_SC05_01_9x16',
                                    'detail': 'Hai nhánh que thừa mọc ra từ cùi chỏ.'}]}
        pairs = [pair('IMG_SC01_01_9x16', ['extra-limbs']), pair('IMG_SC05_01_9x16', ['hands'])]
        result = {'identity': 'ID', 'inspected_files': [], 'checks': checks(character_consistency=cc), 'repair_progress': {
            'IMG_SC01_01_9x16': progress('fail', resolved=['extra-limbs'], tolerated=[]),
            'IMG_SC05_01_9x16': dict(OLD_002_SC05, remaining=[], tolerated=['hands'])}}
        verdicts, overridden = gate(result, pairs)
        self.assertEqual(verdicts['character_consistency'], 'fail')
        self.assertEqual(verdicts['repair:IMG_SC05_01_9x16'], 'fail')
        self.assertEqual(verdicts['repair:IMG_SC01_01_9x16'], 'pass')
        self.assertEqual(set(overridden), {'repair:IMG_SC01_01_9x16'})

    def test_other_criteria_and_contradictions_are_not_weakened(self):
        base = {'identity': 'ID', 'inspected_files': []}
        verdicts, _ = gate(dict(base, checks=checks(pronunciation_and_prosody={'verdict': 'fail'}, image_relevance={'verdict': 'unsupported'})))
        self.assertEqual((verdicts['pronunciation_and_prosody'], verdicts['image_relevance']), ('fail', 'unsupported'))
        defect = {'category': 'wrong_shirt_color', 'target': 'IMG_SC02_01', 'detail': 'Áo màu đỏ thay vì xanh #8CCFE8.'}
        verdicts, overridden = gate(dict(base, checks=checks(character_consistency={'blocking_defects': [defect]})))
        self.assertEqual(overridden, {'character_consistency': {'reviewer': 'pass', 'effective': 'fail'}})
        self.assertEqual(gate(dict(base, checks=checks(visual_continuity={'verdict': 'unsupported'})))[0]['visual_continuity'], 'unsupported')
        with self.assertRaises(jsonschema.ValidationError):
            gate(dict(base, checks=checks(character_consistency={'blocking_defects': [dict(defect, category='eyebrows')]})))
        legacy = dict(base, checks=checks(), repair_progress={'T': progress('fail', remaining=['visual'])})
        self.assertEqual(gate(legacy, [pair('T', ['visual'])])[0]['repair:T'], 'fail')
        with self.assertRaisesRegex(Blocked, 'còn lỗi nhưng báo pass'):
            gate(dict(legacy, repair_progress={'T': progress('pass', remaining=['visual'])}), [pair('T', ['visual'])])
        with self.assertRaisesRegex(Blocked, 'thiếu hoặc mâu thuẫn'):
            gate(dict(legacy, repair_progress={'T': progress('pass', remaining=['visual'], tolerated=['visual'])}), [pair('T', ['visual'])])


class ReviewIntegrationTests(unittest.TestCase):
    setUp = repair_tests.RepairIntegrationTests.setUp
    start = repair_tests.RepairIntegrationTests.start
    items = repair_tests.RepairIntegrationTests.items
    reject = repair_tests.RepairIntegrationTests.reject
    plan = repair_tests.RepairIntegrationTests.plan
    approve = repair_tests.RepairIntegrationTests.approve
    audio = repair_tests.RepairIntegrationTests.audio
    media = repair_tests.RepairIntegrationTests.media
    provider = repair_tests.RepairIntegrationTests.provider
    variant_job = repair_tests.RepairIntegrationTests.variant_job

    def review(self, build, retry=False):
        manifest = wf.current(self.p, self.job, 'media'); seen = {}
        def invoke(prompt, schema, out, **kwargs):
            request = read(out / 'request.json'); seen.update(prompt=prompt, schema=schema)
            return {'structured_output': dict(build(request), identity=request['identity'], inspected_files=list(request['files']))}
        with patch('scripts.agy_pipeline.invoke', side_effect=invoke):
            try: return mr.review(self.p, self.job, 'media', manifest['assets'], manifest['snapshot'], retry), seen
            except Blocked as ex: return ex, seen

    def test_reviewer_receives_policy_and_fail_without_blocking_defect_passes_with_notes(self):
        self.start()
        cc = {'verdict': 'fail', 'evidence': 'TEST: lông mày biểu cảm và giọt mồ hôi.', 'tolerated_deviations': ['lông mày', 'giọt mồ hôi']}
        path, seen = self.review(lambda r: {'checks': checks(character_consistency=cc)})
        self.assertIsInstance(path, str)
        self.assertIn(RULE, seen['prompt'])
        self.assertRegex(seen['prompt'], 'This is (an )?educational')
        props = seen['schema']['properties']['checks']['properties']
        self.assertIn('blocking_defects', props['visual_continuity']['required'])
        self.assertNotIn('blocking_defects', props['exact_visible_text']['properties'])
        attempt = read(self.p.job(self.job) / path.replace('response.json', 'attempt.json'))
        self.assertEqual(attempt['state'], 'passed')
        self.assertEqual(attempt['tolerance_overrides']['character_consistency']['effective'], 'pass')

    def test_blocking_defect_fails_and_same_pixel_tolerated_repair_closes_loop(self):
        self.start(); self.reject(plan=self.plan()); self.media()
        defect = {'category': 'multiple_bodies_or_shirts', 'target': 'IMAGE_EXTRA', 'detail': 'TEST: hai thân áo đè lên nhau.'}
        error, _ = self.review(lambda r: {'checks': checks(character_consistency={'verdict': 'fail', 'blocking_defects': [defect]}),
            'repair_progress': {x['target']: progress('fail', tolerated=['eyebrows']) for x in r['repair_comparisons']}})
        self.assertRegex(str(error), 'MACHINE_REVIEW: chưa đạt')
        path, seen = self.review(lambda r: {'checks': checks(), 'repair_progress': {
            x['target']: progress('fail', tolerated=['eyebrows']) for x in r['repair_comparisons']}}, retry=True)
        self.assertIsInstance(path, str, path)
        self.assertIn('resolved, remaining or tolerated', seen['prompt'])


if __name__ == '__main__':
    unittest.main()
