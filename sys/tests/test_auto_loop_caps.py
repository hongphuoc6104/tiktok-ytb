"""Auto-mode repair loops stop at hard caps; isolated jobs, fake reviewers, no production media."""
import json
import os
import time
import unittest
from unittest.mock import patch

from pilot import ROOT, Blocked, read, write
import workflow as wf
from scripts import image_repairs as repairs
import test_workflow as workflow_tests

W = workflow_tests.WorkflowTests  # helpers only; deleted below so discover does not rerun its tests


class LoopCapTests(unittest.TestCase):
    setUp = W.setUp
    new = W.new
    approve = W.approve
    audio = W.audio
    media = W.media
    provider = W.provider

    def make(self, mode='auto', **caps):
        if caps:
            cfg = read(self.root / 'config.json'); cfg.update(caps); write(self.root / 'config.json', cfg)
        wf.new(self.p, self.job, read(ROOT / 'examples/m1/brief.json'), mode)

    def fake_reject(self):
        """Stand-in for the low-level reject: records what the real one records."""
        emit = lambda *a, **k: self.p.event(self.job, 'images', 'image_revision_requested', json.dumps({'targets': ['X']}))
        retake = lambda p, job, note, scene=None: p.event(job, 'audio', 'audio_retake_requested', json.dumps({'scenes': [scene] if scene else ['SC01', 'SC02'], 'note': note}))
        return (patch('workflow.current', return_value={'revision': 1, 'decision': 'none.json', 'review': 'none.md'}), patch.object(self.p, 'reject', side_effect=emit),
                patch('workflow.retake_audio', side_effect=retake))

    def reject(self, **kw):
        return wf.reject(self.p, self.job, 'media', 1, 'TEST fix', **kw)

    def review(self, failing, when):
        folder = self.p.job(self.job) / 'machine-reviews' / f'r{when}'
        write(folder / 'request.json', {'stage': 'media'})
        write(folder / 'response.json', {'structured_output': {'checks': {
            k: {'verdict': 'fail' if k in failing else 'pass', 'evidence': 'TEST ONLY evidence'} for k in ('character_consistency', 'pronunciation_and_prosody', 'scene_coverage')}}})
        write(folder / 'attempt.json', {'state': 'needs_attention' if failing else 'passed'})
        os.utime(folder / 'response.json', (when, when))

    def stopped(self):
        return any(s['stage'] == 'media' and s['state'] == 'needs_attention' for s in wf.status(self.p, self.job)['stages'])

    def test_media_rejections_capped_per_job_until_human_lift(self):
        self.make()
        a, b, c = self.fake_reject()
        with a, b as low, c:
            for i in range(3):
                self.reject(image=f'IMG{i}')  # rotating targets must not dodge the job cap
            self.assertFalse(repairs.attention(self.p, self.job))
            with self.assertRaisesRegex(Blocked, r'AUTO_LOOP_CAP.*3/3.*KHÔNG tạo job mới'):
                self.reject(image='IMG9')
            self.assertEqual(low.call_count, 3)
            self.assertTrue(self.stopped())
            report = read(self.p.path(self.job, repairs.attention(self.p, self.job)))
            self.assertEqual((report['target'], report['history']['kind']), ('auto-loop', 'media_rejections'))
            with self.assertRaisesRegex(Blocked, 'lý do'):
                wf.lift_cap(self.p, self.job, ' ')
            wf.lift_cap(self.p, self.job, 'TEST user inspected the report')
            self.assertFalse(self.stopped())
            self.reject(image='IMG9')
            self.assertEqual(low.call_count, 4)

    def test_audio_retake_caps_per_scene_and_per_job(self):
        self.make()
        a, b, c = self.fake_reject()
        with a, b, c as retake:
            self.reject(part='audio', scene='SC04'); self.reject(part='audio', scene='SC04')
            with self.assertRaisesRegex(Blocked, 'SC04.*2 lần'):
                self.reject(part='audio', scene='SC04')
            wf.lift_cap(self.p, self.job, 'TEST reviewed')
            for scene in ('SC01', 'SC02', 'SC03', 'SC05'):
                self.reject(part='audio', scene=scene)
            with self.assertRaisesRegex(Blocked, '4/4 lượt đọc lại'):
                self.reject(part='audio', scene='SC06')
            self.assertEqual(retake.call_count, 6)
        self.assertTrue(self.stopped())

    def test_configured_caps_override_defaults(self):
        self.make(auto_max_media_rejections=1)
        a, b, c = self.fake_reject()
        with a, b, c:
            self.reject(image='IMG1')
            with self.assertRaisesRegex(Blocked, '1/1'):
                self.reject(image='IMG2')

    def test_review_mode_is_not_capped(self):
        self.make('review')
        a, b, c = self.fake_reject()
        with a, b as low, c:
            for i in range(6):
                self.reject(image=f'IMG{i}')
            for _ in range(4):
                self.reject(part='audio', scene='SC04')
        self.assertEqual(low.call_count, 6)
        self.assertFalse(repairs.attention(self.p, self.job))

    def test_same_criterion_failing_repeatedly_stops_before_reject_cap(self):
        self.make()
        now = time.time()
        self.review({'character_consistency', 'pronunciation_and_prosody'}, now - 30)
        self.review({'character_consistency'}, now - 20)
        a, b, c = self.fake_reject()
        with a, b as low, c:
            self.reject(image='IMG1')
            self.review({'character_consistency', 'scene_coverage'}, now - 10)
            with self.assertRaisesRegex(Blocked, 'character_consistency.*3 lần đánh giá media liên tiếp'):
                self.reject(part='audio', scene='SC01')
            self.assertEqual(low.call_count, 1)
            # A passing review breaks the streak; only reviews after a lift count.
            wf.lift_cap(self.p, self.job, 'TEST reviewed')
            self.reject(image='IMG2')
        self.assertEqual(repairs.repeat_failures(self.p, self.job, 3)[0], ['character_consistency'])
        self.review(set(), now + 10)
        self.assertEqual(repairs.repeat_failures(self.p, self.job, 3), ([], []))

    def test_repeat_failures_ignores_other_stages_and_broken_reviews(self):
        self.make()
        now = time.time()
        for i in range(3):
            self.review({'character_consistency'}, now - 10 + i)
        other = self.p.job(self.job) / 'machine-reviews' / 'video'
        write(other / 'request.json', {'stage': 'video'}); write(other / 'response.json', {'structured_output': {'checks': {}}})
        broken = self.p.job(self.job) / 'machine-reviews' / 'broken'
        write(broken / 'request.json', {'stage': 'media'}); (broken / 'response.json').write_text('{')
        self.assertEqual(repairs.repeat_failures(self.p, self.job, 3)[0], ['character_consistency'])
        self.assertEqual(repairs.repeat_failures(self.p, self.job, 4), ([], []))

    def test_auto_resume_stops_after_third_identical_review_failure(self):
        """End to end: advance itself stops once the streak completes, then never spends another review."""
        self.new('auto')  # writes the draft, so no content generator runs
        calls = []

        def reviewer(p, job, stage, paths, snapshot, retry=False):
            calls.append(stage)
            if stage != 'media':
                file = p.job(job) / 'machine-reviews' / f'ok-{len(calls)}.json'; write(file, {'test_only': True})
                return str(file.relative_to(p.job(job)))
            self.review({'character_consistency'}, time.time() - 1000 + len(calls))
            raise Blocked('MACHINE_REVIEW: chưa đạt (TEST)')
        with patch('machine_review.review', side_effect=reviewer):
            wf.advance(self.p, self.job, 'content')
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW'):
                self.media()
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW'):
                wf.advance(self.p, self.job, retry_review=True)
            with self.assertRaisesRegex(Blocked, 'AUTO_LOOP_CAP.*character_consistency'):
                wf.advance(self.p, self.job, retry_review=True)
            self.assertTrue(self.stopped())
            with patch('adapters.gflow') as provider:
                with self.assertRaisesRegex(Blocked, 'NEEDS_ATTENTION.*DỪNG NGAY'):
                    wf.advance(self.p, self.job, retry_review=True)
            provider.assert_not_called()
            self.assertEqual(calls.count('media'), 3)
            wf.lift_cap(self.p, self.job, 'TEST reviewed')
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW'):
                wf.advance(self.p, self.job, retry_review=True)
            self.assertEqual(calls.count('media'), 4)


del W

if __name__ == '__main__':
    unittest.main()
