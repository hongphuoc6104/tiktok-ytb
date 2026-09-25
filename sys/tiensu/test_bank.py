"""Kiểm tra kho chủ đề tiền sử: chọn chủ đề, sinh brief-v3, giữ chỗ, đánh dấu đã làm.

Chạy: python3 -m pytest tiensu/test_bank.py -q
Test dùng thư mục tạm, không đụng tiensu/topics.jsonl hay tiensu/ledger.json thật.
"""
import json
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tiensu import bank as tb  # noqa: E402


def args(**kw):
    base = dict(count=5, tag=None, id=None, out=None, mode='review', style=None, tone=None,
                video=None, note='', force=False, job=None, redo=False)
    base.update(kw)
    return Namespace(**base)


def topic(id, sources=True, seed_facts=None, tags=None):
    item = {'id': id, 'question': f'Câu hỏi cho {id}?', 'angle': f'Góc kể của {id}',
            'seed_facts': seed_facts if seed_facts is not None else ['gợi ý 1', 'gợi ý 2']}
    if tags:
        item['tags'] = tags
    if sources:
        item['sources'] = [{'id': 'S1', 'title': f'Nguồn của {id}', 'reference': 'ref thật',
                            'facts': [f'Một dữ kiện thật về {id}']}]
    return item


class BankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__import__('tempfile').mkdtemp())
        self.patches = [
            patch.object(tb, 'ROOT', self.tmp),
            patch.object(tb, 'TOPICS', self.tmp / 'topics.jsonl'),
            patch.object(tb, 'LEDGER', self.tmp / 'ledger.json'),
            patch.object(tb, 'BRIEFS', self.tmp / 'briefs'),
            patch.object(tb, 'REPO', self.tmp),
        ]
        for p in self.patches:
            p.start()
        channel = json.loads((Path(__file__).resolve().parent / 'channel.json').read_text(encoding='utf-8'))
        tb.write_json(self.tmp / 'channel.json', channel)

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def write_topics(self, items):
        self.tmp.joinpath('topics.jsonl').write_text(
            '\n'.join(json.dumps(x, ensure_ascii=False) for x in items) + '\n', encoding='utf-8')

    def two_topics(self):
        self.write_topics([topic('day-in-the-life'), topic('rainy-week')])

    # ---------------------------------------------------------- topics()/select

    def test_topics_reads_jsonl_in_order_with_rank(self):
        self.two_topics()
        items = tb.topics()
        self.assertEqual(['day-in-the-life', 'rainy-week'], [x['id'] for x in items])
        self.assertEqual([1, 2], [x['rank'] for x in items])

    def test_duplicate_id_is_rejected(self):
        self.write_topics([topic('same'), topic('same')])
        with self.assertRaises(tb.Stop):
            tb.topics()

    def test_missing_required_field_is_rejected(self):
        self.tmp.joinpath('topics.jsonl').write_text(
            json.dumps({'id': 'x', 'question': 'q?'}, ensure_ascii=False) + '\n', encoding='utf-8')
        with self.assertRaises(tb.Stop):
            tb.topics()

    def test_topic_without_sources_cannot_be_reserved(self):
        self.write_topics([topic('no-sources', sources=False)])
        with self.assertRaises(tb.Stop):
            tb.reserve(args(job='v1'))

    def test_tag_filter_narrows_the_pool(self):
        self.write_topics([topic('a', tags=['fire']), topic('b', tags=['water'])])
        picked = tb.cmd_next(args(tag='fire'))['picked']
        self.assertEqual(['a'], [x['id'] for x in picked])

    # ---------------------------------------------------------- brief / reserve

    def test_reserve_writes_brief_v3_with_section8_fields(self):
        self.two_topics()
        drawn = tb.reserve(args(job='v1'))
        self.assertEqual('day-in-the-life', drawn['topic'])
        brief = json.loads(Path(drawn['brief']).read_text(encoding='utf-8'))
        self.assertEqual('3.0', brief['schema_version'])
        self.assertEqual('tiensu', brief['channel'])
        self.assertEqual('vi', brief['voice_language'])
        self.assertTrue(brief['subtitles'])
        self.assertEqual('16:9', brief['aspect_ratio'])
        self.assertTrue(brief['facts_required'])
        self.assertEqual(1, len(brief['sources']))
        self.assertIn('clips', brief)
        self.assertEqual(10, brief['clips']['max'])
        self.assertIn(brief['scene_count'], range(7, 10))
        ids = [r['id'] for r in brief['required_points']]
        self.assertEqual(['R1', 'R2', 'R3', 'R4', 'R5'], ids)
        self.assertTrue(any(l.startswith(tb.ENTRY_TAG) for l in brief['planning']['domain_requirements']))
        self.assertIn('vi', brief['planning']['speech_rates'])
        self.assertIn('en', brief['planning']['speech_rates'])  # schema brief-v3 yêu cầu cả hai

    def test_reserve_twice_for_same_job_is_blocked(self):
        self.two_topics()
        tb.reserve(args(job='v1'))
        with self.assertRaises(tb.Stop):
            tb.reserve(args(job='v1'))

    def test_reserved_topic_leaves_the_pool(self):
        self.two_topics()
        tb.reserve(args(job='v1'))
        self.assertNotIn('day-in-the-life', [x['id'] for x in tb.cmd_next(args())['picked']])

    def test_scene_count_clamped_to_channel_range(self):
        self.write_topics([topic('few-facts', seed_facts=['một gợi ý'])])
        drawn = tb.reserve(args(job='v1'))
        brief = json.loads(Path(drawn['brief']).read_text(encoding='utf-8'))
        self.assertGreaterEqual(brief['scene_count'], 7)
        self.assertLessEqual(brief['scene_count'], 9)

    # ---------------------------------------------------------- mark

    def test_mark_needs_an_approved_video(self):
        self.two_topics()
        tb.reserve(args(job='v1'))
        with patch.object(tb, 'approved_video', return_value=False):
            with self.assertRaises(tb.Stop):
                tb.cmd_mark(args(job='v1'))
        self.assertEqual('reserved', tb.state_of(tb.ledger(), 'day-in-the-life'))
        with patch.object(tb, 'approved_video', return_value=True):
            tb.cmd_mark(args(job='v1', note='xong'))
        self.assertEqual('done', tb.state_of(tb.ledger(), 'day-in-the-life'))

    def test_force_mark_outside_the_pipeline_requires_a_note(self):
        self.two_topics()
        with self.assertRaises(tb.Stop):
            tb.cmd_mark(args(job='old', id='day-in-the-life', force=True))
        tb.cmd_mark(args(job='old', id='day-in-the-life', force=True, note='đã đăng trước đó'))
        self.assertEqual('done', tb.state_of(tb.ledger(), 'day-in-the-life'))

    def test_done_topic_never_comes_back_into_the_pool(self):
        self.two_topics()
        tb.cmd_mark(args(id='day-in-the-life', force=True, note='đã đăng', job=None))
        self.assertNotIn('day-in-the-life', [x['id'] for x in tb.cmd_next(args(count=99))['picked']])
        self.assertEqual(1, tb.cmd_status(args())['done'])

    # ---------------------------------------------------------- start / queue

    def test_failed_start_returns_the_topic_and_leaves_no_brief(self):
        self.two_topics()
        fail = type('R', (), {'returncode': 1, 'stdout': '{"blocked": "x"}', 'stderr': ''})()
        with patch.object(tb.subprocess, 'run', return_value=fail):
            with self.assertRaises(tb.Stop):
                tb.cmd_start(args(job='v1'))
        self.assertEqual({}, tb.ledger()['entries'])
        self.assertFalse((self.tmp / 'briefs' / 'v1.json').exists())
        with patch.object(tb, 'cmd_start', tb.reserve):
            tb.reserve(args(job='v1'))  # mã job dùng lại được ngay

    def test_queue_creates_several_jobs_and_a_queue_file(self):
        self.write_topics([topic('a'), topic('b'), topic('c')])
        starts = []

        def fake_start(a):
            starts.append(a.job)
            return tb.reserve(a)

        with patch.object(tb, 'cmd_start', fake_start):
            result = tb.cmd_queue(args(count=3, prefix='q-'))
        self.assertEqual(['q-001', 'q-002', 'q-003'], starts)
        self.assertEqual(['q-001', 'q-002', 'q-003'],
                         json.loads(Path(result['queue']).read_text(encoding='utf-8')))
        self.assertEqual(3, len({e['job'] for e in tb.ledger()['entries'].values()}))

    def test_queue_stops_cleanly_when_the_pool_runs_out(self):
        self.two_topics()
        with patch.object(tb, 'cmd_start', tb.reserve):
            result = tb.cmd_queue(args(count=5, prefix='q-'))
        self.assertEqual(2, len(result['created']))
        self.assertEqual('q-003', result['stopped_at'])

    # ---------------------------------------------------------- status / audit

    def test_status_counts_by_state(self):
        self.two_topics()
        tb.reserve(args(job='v1'))
        status = tb.cmd_status(args())
        self.assertEqual(2, status['topics'])
        self.assertEqual(1, status['reserved'])
        self.assertEqual(1, status['todo'])
        self.assertEqual(['v1'], status['reserved_jobs'])

    def test_audit_reports_no_runs_directory(self):
        self.two_topics()
        result = tb.cmd_audit(args())
        self.assertEqual(0, result['jobs'])
        self.assertEqual([], result['linked'])

    def test_two_writers_do_not_lose_a_record(self):
        self.two_topics()
        tb.cmd_mark(args(id='day-in-the-life', force=True, note='xong', job='v1'))
        with tb.ledger_lock():
            pass  # khoá nhả được, không kẹt tiến trình
        self.assertEqual('done', tb.state_of(tb.ledger(), 'day-in-the-life'))
        self.assertTrue((self.tmp / '.ledger.lock').exists())


class PilotTopicsAreLoadedTests(unittest.TestCase):
    """Kiểm tra kho thật (không patch) nạp được và ba chủ đề thử khớp mục 5 của kế hoạch."""

    def test_real_topics_file_loads_and_has_pilot_topics(self):
        items = tb.topics()
        self.assertGreaterEqual(len(items), 30)
        ids = [x['id'] for x in items]
        self.assertEqual(len(ids), len(set(ids)))
        for item in items:
            self.assertTrue(item['sources'], f"{item['id']} thiếu sources thật")
        first_three = [x['question'] for x in items[:3]]
        self.assertEqual([
            'Một ngày sống như người săn bắt hái lượm: kiếm ăn, ngủ và giữ ấm ra sao?',
            'Mưa cả tuần khi chưa có nhà: người tiền sử trú ẩn và kiếm ăn thế nào?',
            'Mùa đông khắc nghiệt: tổ tiên sống sót khi chưa có nhà hay áo ấm ra sao?',
        ], first_three)

    def test_real_channel_config_matches_section8_defaults(self):
        cfg = tb.channel_config()
        self.assertEqual('tiensu', cfg['channel'])
        self.assertEqual('16:9', cfg['aspect_ratio'])
        self.assertEqual('vi', cfg['voice_language'])
        self.assertTrue(cfg['subtitles'])
        self.assertEqual(480.0, cfg['duration']['min_seconds'])
        self.assertEqual(720.0, cfg['duration']['max_seconds'])
        self.assertEqual(3.6, cfg['speech_rates']['vi']['units_per_second'])


if __name__ == '__main__':
    unittest.main()
