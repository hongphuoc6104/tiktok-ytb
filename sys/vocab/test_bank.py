"""Kiểm tra kho từ vựng: build, tách nghĩa, giữ chỗ, đánh dấu đã làm.

Chạy: python3 -m pytest vocab/test_bank.py -q
Các test dùng thư mục tạm, không đụng vocab/bank.jsonl hay vocab/ledger.json thật.
"""
import json
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vocab import bank as vb  # noqa: E402


def args(**kw):
    base = dict(count=5, topic=None, level=None, pos=None, word=None, order='level',
                out=None, mode='review', style=None, tone=None, aspect_ratio=None,
                entry=None, video=None, note='', force=False, job=None, redo=False)
    base.update(kw)
    return Namespace(**base)


class BankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__import__('tempfile').mkdtemp())
        (self.tmp / 'sources').mkdir()
        self.patches = [
            patch.object(vb, 'ROOT', self.tmp),
            patch.object(vb, 'BANK', self.tmp / 'bank.jsonl'),
            patch.object(vb, 'LEDGER', self.tmp / 'ledger.json'),
            patch.object(vb, 'BRIEFS', self.tmp / 'briefs'),
            patch.object(vb, 'REPO', self.tmp),
        ]
        for p in self.patches:
            p.start()
        vb.write_json(self.tmp / 'topics.json', {'version': 1, 'topics': [
            {'id': 'money', 'vi': 'Tiền bạc', 'en': 'Money', 'angle': 'x'},
            {'id': 'nature', 'vi': 'Thiên nhiên', 'en': 'Nature', 'angle': 'y'}]})
        vb.write_json(self.tmp / 'channel.json', json.loads(
            (Path(__file__).resolve().parent / 'channel.json').read_text(encoding='utf-8')))

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def source(self, topic, text):
        (self.tmp / 'sources' / f'{topic}.txt').write_text(text, encoding='utf-8')

    def two_topics(self):
        self.source('money', 'bank|n|ngân hàng|A2|finance\npay|v|trả tiền|A1\n')
        self.source('nature', 'bank|n|bờ sông|B1|river\nriver|n|con sông|A1\n')
        return vb.build()

    def test_same_word_different_sense_becomes_two_entries(self):
        result = self.two_topics()
        self.assertEqual(result['entries'], 4)
        self.assertEqual(result['words'], 3)
        ids = {x['id'] for x in vb.bank()}
        self.assertEqual({'bank.n.finance', 'bank.n.river', 'pay.v', 'river.n'}, ids)
        finance = next(x for x in vb.bank() if x['id'] == 'bank.n.finance')
        self.assertTrue(finance['homograph'])
        self.assertEqual(['bank.n.river'], finance['siblings'])

    def test_same_sense_in_two_topics_merges_instead_of_duplicating(self):
        self.source('money', 'water|n|nước|A1\n')
        self.source('nature', 'water|n|nước|A1\n')
        self.assertEqual(1, vb.build()['entries'])
        self.assertEqual(['money', 'nature'], vb.bank()[0]['topics'])

    def test_clashing_meanings_without_sense_key_are_blocked(self):
        self.source('money', 'bank|n|ngân hàng|A2\n')
        self.source('nature', 'bank|n|bờ sông|B1\n')
        with self.assertRaises(vb.Stop) as ex:
            vb.build()
        self.assertIn('khoá nghĩa', str(ex.exception))

    def test_bad_lines_are_reported_with_file_and_number(self):
        self.source('money', 'pay|verb|trả tiền|A1\n')
        self.source('nature', 'river|n|con sông|Z9\n')
        with self.assertRaises(vb.Stop) as ex:
            vb.build()
        self.assertIn('money.txt:1', str(ex.exception))
        self.assertIn('nature.txt:1', str(ex.exception))

    def test_draw_reserves_and_writes_a_valid_brief(self):
        self.two_topics()
        drawn = vb.cmd_draw(args(job='v1'))
        self.assertEqual('pay.v', drawn['entry'])  # A1 đi trước
        brief = json.loads(Path(drawn['brief']).read_text(encoding='utf-8'))
        from content_contract import validate_brief
        validate_brief(Path(__file__).resolve().parents[1], brief)
        self.assertEqual(4, len(brief['required_points']))
        self.assertIn('PAY', brief['topic'])
        self.assertEqual('reserved', vb.state_of(vb.ledger(), 'pay.v'))

    def test_drawn_entry_is_not_offered_again(self):
        self.two_topics()
        vb.cmd_draw(args(job='v1'))
        self.assertNotIn('pay.v', [x['id'] for x in vb.cmd_next(args())['picked']])
        second = vb.cmd_draw(args(job='v2'))
        self.assertNotEqual('pay.v', second['entry'])

    def test_brief_of_a_homograph_warns_about_the_other_sense(self):
        self.two_topics()
        drawn = vb.cmd_draw(args(job='v1', word='bank'))
        self.assertEqual('bank.n.finance', drawn['entry'])
        brief = json.loads(Path(drawn['brief']).read_text(encoding='utf-8'))
        avoid = ' '.join(brief['planning']['avoid'])
        self.assertIn('bờ sông', avoid)
        self.assertIn('bank.n.river', avoid)

    def test_mark_needs_an_approved_video(self):
        self.two_topics()
        vb.cmd_draw(args(job='v1'))
        with patch.object(vb, 'approved_video', return_value=False):
            with self.assertRaises(vb.Stop):
                vb.cmd_mark(args(job='v1'))
        self.assertEqual('reserved', vb.state_of(vb.ledger(), 'pay.v'))
        with patch.object(vb, 'approved_video', return_value=True):
            vb.cmd_mark(args(job='v1', note='xong'))
        self.assertEqual('done', vb.state_of(vb.ledger(), 'pay.v'))

    def test_force_mark_outside_the_pipeline_requires_a_note(self):
        self.two_topics()
        with self.assertRaises(vb.Stop):
            vb.cmd_mark(args(job='old', entry='pay.v', force=True))
        vb.cmd_mark(args(job='old', entry='pay.v', force=True, note='đã đăng trước đó'))
        self.assertEqual('done', vb.state_of(vb.ledger(), 'pay.v'))

    def test_done_entry_never_comes_back_into_the_pool(self):
        self.two_topics()
        vb.cmd_mark(args(entry='pay.v', force=True, note='đã đăng', job=None))
        self.assertNotIn('pay.v', [x['id'] for x in vb.cmd_next(args(count=99))['picked']])
        self.assertEqual(1, vb.cmd_status(args())['done'])

    def test_rebuild_keeps_the_ledger(self):
        self.two_topics()
        vb.cmd_mark(args(entry='pay.v', force=True, note='đã đăng', job=None))
        self.source('money', 'bank|n|ngân hàng|A2|finance\npay|v|trả tiền|A1\ncoin|n|đồng xu|A2\n')
        self.assertEqual(5, vb.build()['entries'])
        self.assertEqual('done', vb.state_of(vb.ledger(), 'pay.v'))

    def test_release_frees_a_reservation_but_not_a_finished_word(self):
        self.two_topics()
        vb.cmd_draw(args(job='v1'))
        vb.cmd_release(args(job='v1'))
        self.assertEqual('todo', vb.state_of(vb.ledger(), 'pay.v'))
        vb.cmd_mark(args(entry='pay.v', force=True, note='đã đăng', job='v9'))
        with self.assertRaises(vb.Stop):
            vb.cmd_release(args(job='v9'))

    def test_redrawing_a_finished_word_keeps_the_old_record(self):
        self.two_topics()
        vb.cmd_mark(args(entry='pay.v', force=True, note='bản cũ đã đăng', job='v-old'))
        with self.assertRaises(vb.Stop):
            vb.cmd_draw(args(job='v-new', word='pay'))  # không --redo thì không rút lại được
        vb.cmd_draw(args(job='v-new', word='pay', redo=True, note='làm bản mới'))
        record = vb.ledger()['entries']['pay.v']
        self.assertEqual('reserved', record['status'])
        self.assertEqual('v-new', record['job'])
        self.assertEqual([{'job': 'v-old', 'at': record['previous'][0]['at'],
                           'note': 'bản cũ đã đăng'}], record['previous'])
        self.assertEqual('làm bản mới', record['note'])

    def test_two_writers_do_not_lose_a_record(self):
        self.two_topics()
        vb.cmd_mark(args(entry='pay.v', force=True, note='xong', job='v1'))
        with vb.ledger_lock():
            pass  # khoá nhả được, không kẹt tiến trình
        self.assertEqual('done', vb.state_of(vb.ledger(), 'pay.v'))
        self.assertTrue((self.tmp / '.ledger.lock').exists())

    def test_failed_start_returns_the_word_and_leaves_no_brief(self):
        self.two_topics()
        fail = type('R', (), {'returncode': 1, 'stdout': '{"blocked": "x"}', 'stderr': ''})()
        with patch.object(vb.subprocess, 'run', return_value=fail):
            with self.assertRaises(vb.Stop):
                vb.cmd_start(args(job='v1'))
        self.assertEqual({}, vb.ledger()['entries'])
        self.assertFalse((self.tmp / 'briefs' / 'v1.json').exists())
        with patch.object(vb, 'cmd_start', vb.cmd_draw):
            vb.cmd_draw(args(job='v1'))  # mã job dùng lại được ngay

    def test_queue_creates_several_jobs_and_a_batch_file(self):
        self.two_topics()
        starts = []

        def fake_start(a):
            starts.append(a.job)
            return vb.cmd_draw(a)

        with patch.object(vb, 'cmd_start', fake_start):
            result = vb.cmd_queue(args(count=3, prefix='q-'))
        self.assertEqual(['q-001', 'q-002', 'q-003'], starts)
        self.assertEqual(['q-001', 'q-002', 'q-003'],
                         json.loads(Path(result['queue']).read_text(encoding='utf-8')))
        self.assertEqual(3, len({e['job'] for e in vb.ledger()['entries'].values()}))

    def test_queue_stops_cleanly_when_the_pool_runs_out(self):
        self.source('money', 'pay|v|trả tiền|A1\n')
        self.source('nature', 'river|n|con sông|A1\n')
        vb.build()
        with patch.object(vb, 'cmd_start', vb.cmd_draw):
            result = vb.cmd_queue(args(count=5, prefix='q-'))
        self.assertEqual(2, len(result['created']))
        self.assertEqual('q-003', result['stopped_at'])
        self.assertEqual(['q-001', 'q-002'],
                         json.loads(Path(result['queue']).read_text(encoding='utf-8')))

    def test_filters_narrow_the_pool(self):
        self.two_topics()
        picked = vb.cmd_next(args(topic='nature', count=9))['picked']
        self.assertEqual({'bank.n.river', 'river.n'}, {x['id'] for x in picked})
        self.assertEqual([], vb.cmd_next(args(level='C1'))['picked'])
        with self.assertRaises(vb.Stop):
            vb.cmd_next(args(topic='khong-co'))


    def test_lint_catches_two_entries_that_teach_the_same_thing(self):
        self.source('money', 'pay|v|trả tiền|A1|settle\npay|v|trả tiền|A2|hand-over\n')
        self.source('nature', 'river|n|con sông|A1\n')
        vb.build()
        result = vb.cmd_lint(args())
        self.assertEqual(1, result['count'])
        self.assertEqual(['pay.v.hand-over', 'pay.v.settle'], result['suspects'][0]['ids'])
        vb.write_json(self.tmp / 'lint-allow.json',
                      {'pairs': [['pay.v.settle', 'pay.v.hand-over']]})
        self.assertEqual(0, vb.cmd_lint(args())['count'])

    def test_lint_keeps_genuinely_different_senses(self):
        self.source('money', 'bank|n|ngân hàng|A2|finance\n')
        self.source('nature', 'bank|n|bờ sông|B1|river\n')
        vb.build()
        self.assertEqual(0, vb.cmd_lint(args())['count'])


class PolicyTests(unittest.TestCase):
    """Cổng brief_policies: job dạy từ vựng chỉ được vào pipeline qua kho."""

    def setUp(self):
        self.tmp = Path(__import__('tempfile').mkdtemp())
        (self.tmp / 'sources').mkdir()
        self.patches = [patch.object(vb, 'ROOT', self.tmp), patch.object(vb, 'REPO', self.tmp),
                        patch.object(vb, 'BANK', self.tmp / 'bank.jsonl'),
                        patch.object(vb, 'LEDGER', self.tmp / 'ledger.json'),
                        patch.object(vb, 'BRIEFS', self.tmp / 'briefs')]
        for p in self.patches:
            p.start()
        vb.write_json(self.tmp / 'topics.json', {'version': 1, 'topics': [
            {'id': 'money', 'vi': 'Tiền bạc', 'en': 'Money', 'angle': 'x'}]})
        vb.write_json(self.tmp / 'channel.json', json.loads(
            (Path(__file__).resolve().parent / 'channel.json').read_text(encoding='utf-8')))
        (self.tmp / 'sources' / 'money.txt').write_text('pay|v|trả tiền|A1\n', encoding='utf-8')
        vb.build()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def brief(self, job='v1'):
        vb.cmd_draw(args(job=job))
        return json.loads((self.tmp / 'briefs' / f'{job}.json').read_text(encoding='utf-8'))

    def test_drawn_brief_passes_for_its_own_job(self):
        from vocab import policy
        policy.check(self.tmp, 'v1', self.brief('v1'))

    def test_handmade_vocabulary_brief_is_refused(self):
        from vocab import policy
        brief = self.brief('v1')
        brief['planning']['domain_requirements'] = ['Giữ nét vẽ đồng nhất']
        with self.assertRaises(Exception) as ex:
            policy.check(self.tmp, 'v2', brief)
        self.assertIn('vocab/bank.py start v2', str(ex.exception))

    def test_entry_held_by_another_job_is_refused(self):
        from vocab import policy
        brief = self.brief('v1')
        with self.assertRaises(Exception) as ex:
            policy.check(self.tmp, 'v2', brief)
        self.assertIn('đang thuộc job v1', str(ex.exception))

    def test_invented_entry_id_is_refused(self):
        from vocab import policy
        brief = self.brief('v1')
        brief['planning']['domain_requirements'] = [
            x if not x.startswith(vb.ENTRY_TAG) else vb.ENTRY_TAG + 'khong.co.that'
            for x in brief['planning']['domain_requirements']]
        with self.assertRaises(Exception) as ex:
            policy.check(self.tmp, 'v1', brief)
        self.assertIn('không có trong kho', str(ex.exception))

    def test_brief_that_does_not_teach_vocabulary_is_untouched(self):
        from vocab import policy
        other = {'topic': 'Góp ý với đồng nghiệp', 'goal': 'Nói riêng và cụ thể',
                 'video_type': 'interpersonal', 'planning': {'domain_requirements': []}}
        policy.check(self.tmp, 'v9', other)


class RealBankTests(unittest.TestCase):
    """Kho thật phải build được và mọi mục phải dùng được để sinh brief hợp lệ."""

    def test_shipped_bank_matches_its_sources(self):
        real = Path(__file__).resolve().parent
        if not (real / 'bank.jsonl').exists():
            self.skipTest('chưa build kho thật')
        before = (real / 'bank.jsonl').read_text(encoding='utf-8')
        vb.build()
        self.assertEqual(before, (real / 'bank.jsonl').read_text(encoding='utf-8'),
                         'bank.jsonl lệch với sources; chạy python3 vocab/bank.py build')

    def test_shipped_bank_has_no_duplicate_senses(self):
        real = Path(__file__).resolve().parent
        if not (real / 'bank.jsonl').exists():
            self.skipTest('chưa build kho thật')
        result = vb.cmd_lint(args())
        self.assertEqual([], result['suspects'], 'có hai mục dạy cùng một nghĩa')

    def test_every_entry_produces_a_brief_that_passes_the_contract(self):
        real = Path(__file__).resolve().parent
        if not (real / 'bank.jsonl').exists():
            self.skipTest('chưa build kho thật')
        from content_contract import validate_brief
        items = vb.bank()
        led = {'version': 1, 'entries': {}}
        channel = vb.read_json(real / 'channel.json')
        sample = items[:: max(1, len(items) // 40)] + [x for x in items if x['homograph']][:5]
        for entry in sample:
            validate_brief(Path(__file__).resolve().parents[1],
                           vb.make_brief(entry, led, items, channel))


if __name__ == '__main__':
    unittest.main()
