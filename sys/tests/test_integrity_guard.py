"""Integrity guard, human-only code adoption and one open job per vocabulary entry; isolated temp roots only."""
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test helpers, also for `-m unittest tests.x`
import pilot
from pilot import ROOT, Pilot, Blocked, read, write
import workflow as wf
import test_workflow as workflow_tests
from scripts.story_plan import normalize_brief
from vocab import bank as vb
from vocab import test_bank as bank_tests


class IntegrityGuardTests(unittest.TestCase):
    setUp = workflow_tests.WorkflowTests.setUp
    new = workflow_tests.WorkflowTests.new
    approve = workflow_tests.WorkflowTests.approve
    audio = workflow_tests.WorkflowTests.audio
    media = workflow_tests.WorkflowTests.media
    provider = workflow_tests.WorkflowTests.provider

    def tamper(self):
        (self.root / 'AGENTS.md').write_text((self.root / 'AGENTS.md').read_text() + '\nTEST edit\n')
        write(self.root / 'schemas/test-extra.json', {'test_only': True})
        (self.root / 'GEMINI.md').unlink()

    def test_block_lists_changed_paths_and_forbids_a_new_job(self):
        self.new()
        self.tamper()
        with self.assertRaises(Blocked) as ex:
            self.p.refresh(self.job)
        msg = str(ex.exception)
        self.assertTrue(msg.startswith('Protected implementation changed'))
        for part in ('modified: AGENTS.md', 'added: schemas/test-extra.json', 'removed: GEMINI.md',
                     'KHÔNG tạo job mới', 'báo người dùng', f'adopt-code {self.job} --confirm {self.job}'):
            self.assertIn(part, msg)

    def test_block_caps_the_listed_paths(self):
        self.new()
        for i in range(20):
            write(self.root / f'examples/test-extra-{i:02}.json', {'i': i})
        with self.assertRaises(Blocked) as ex:
            self.p.integrity(self.job)
        self.assertIn('20 file bảo vệ', str(ex.exception))
        self.assertIn('… và 5 file khác', str(ex.exception))
        self.assertNotIn('test-extra-19', str(ex.exception))

    def test_integrity_diff_is_read_only(self):
        self.new()
        base = (self.p.job(self.job) / 'integrity.json').read_bytes()
        self.assertEqual(0, self.p.integrity_diff(self.job)['changed'])
        self.tamper()
        d = self.p.integrity_diff(self.job)
        self.assertEqual((d['changed'], d['modified'], d['added'], d['removed']),
                         (3, ['AGENTS.md'], ['schemas/test-extra.json'], ['GEMINI.md']))
        self.assertEqual(base, (self.p.job(self.job) / 'integrity.json').read_bytes())

    def test_adopt_code_needs_exact_confirmation_and_reason(self):
        self.new()
        with self.assertRaisesRegex(Blocked, 'trùng baseline'):
            self.p.adopt_code(self.job, self.job, 'TEST nothing changed')
        self.tamper()
        base = (self.p.job(self.job) / 'integrity.json').read_bytes()
        for confirm, reason in ((None, 'TEST'), ('other-job', 'TEST'), (self.job, '  ')):
            with self.assertRaises(Blocked):
                self.p.adopt_code(self.job, confirm, reason)
        self.assertEqual(base, (self.p.job(self.job) / 'integrity.json').read_bytes())
        self.assertFalse((self.p.job(self.job) / 'integrity-history').exists())
        with self.assertRaisesRegex(Blocked, 'Unknown job'):
            self.p.adopt_code('no-such-job', 'no-such-job', 'TEST')

    def test_adopt_code_archives_old_baseline_and_keeps_approvals(self):
        self.new()
        self.approve('content')
        old = read(self.p.job(self.job) / 'integrity.json')
        rows, decisions = self.p.rows(self.job), sorted((self.p.job(self.job) / 'reviews').rglob('*'))
        self.tamper()
        result = self.p.adopt_code(self.job, self.job, 'TEST user accepts rules edit')
        history = read(result['history'])
        self.assertEqual(old, history['old_baseline'])
        self.assertEqual(['AGENTS.md'], history['diff']['modified'])
        self.assertEqual(('TEST user accepts rules edit', 'user', None), (history['reason'], history['actor'], history['git_head']))
        self.assertEqual(Path(result['history']).parent, self.p.job(self.job) / 'integrity-history')
        self.p.refresh(self.job)  # new baseline accepted
        self.assertEqual(rows, self.p.rows(self.job))
        self.assertEqual(decisions, sorted((self.p.job(self.job) / 'reviews').rglob('*')))
        self.assertTrue(wf.approved(self.p, self.job, 'content'))
        detail = self.p.db.execute("SELECT detail FROM events WHERE job=? AND event='code_adopted'", (self.job,)).fetchone()[0]
        self.assertEqual(3, json.loads(detail)['changed'])

    def test_adoption_reruns_a_stale_machine_review_instead_of_reusing_it(self):
        import machine_review
        self.new()
        self.approve('content')
        self.media()
        manifest = wf.current(self.p, self.job, 'media')

        def invoke(prompt, schema, out, **kwargs):
            request = read(out / 'request.json')  # nothing inspected -> needs_attention
            return {'structured_output': {'identity': request['identity'], 'inspected_files': [],
                    'checks': {k: {'verdict': 'pass', 'evidence': 'TEST fixture only, not production.'}
                               for k in machine_review.CRITERIA['media']}}}
        review = lambda: machine_review.review(self.p, self.job, 'media', manifest['assets'], manifest['snapshot'])
        with patch('scripts.agy_pipeline.invoke', side_effect=invoke) as reviewer:
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW'):
                review()
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW_UNCHANGED'):
                review()
            self.assertEqual(1, reviewer.call_count)
            (self.root / 'AGENTS.md').write_text((self.root / 'AGENTS.md').read_text() + '\nTEST edit\n')
            result = self.p.adopt_code(self.job, self.job, 'TEST continue under new rules')
            self.assertEqual(1, result['superseded_machine_reviews'])
            self.assertEqual(manifest, wf.current(self.p, self.job, 'media'))  # still mid-review, not re-produced
            with self.assertRaisesRegex(Blocked, 'MACHINE_REVIEW: chưa đạt'):
                review()
            self.assertEqual(2, reviewer.call_count)
        attempts = [read(f) for f in (self.p.job(self.job) / 'machine-reviews').glob('*/attempt.json')]
        self.assertEqual(1, len({a['identity'] for a in attempts}))  # identity alone would have reused it
        self.assertEqual(['needs_attention', 'superseded'], sorted(a['state'] for a in attempts))
        archived = read(result['history'])['superseded_machine_reviews']
        self.assertEqual(['needs_attention'], [x['state'] for x in archived.values()])

    def test_cli_integrity_diff_and_adopt_code(self):
        self.new()
        self.tamper()

        def cli(*argv, tty=True):
            out, err = io.StringIO(), io.StringIO()
            with patch('sys.stdin.isatty', return_value=tty), patch.object(pilot, 'ROOT', self.root), patch.object(pilot, 'Pilot', lambda: Pilot(self.root)), \
                    patch('sys.argv', ['pilot.py', *argv]), redirect_stdout(out), redirect_stderr(err):
                pilot.main()
            return json.loads(out.getvalue()), err.getvalue()
        diff, _ = cli('integrity-diff', self.job)
        self.assertEqual(3, diff['changed'])
        with self.assertRaisesRegex(Blocked, '--confirm'):
            cli('adopt-code', self.job, '--reason', 'TEST')
        with self.assertRaisesRegex(Blocked, 'chạy trực tiếp trong terminal'):
            cli('adopt-code', self.job, '--confirm', self.job, '--reason', 'TEST', tty=False)
        result, warning = cli('adopt-code', self.job, '--confirm', self.job, '--reason', 'TEST human decision')
        self.assertTrue(result['adopted'])
        self.assertIn('chỉ dành cho NGƯỜI DÙNG', warning)
        self.assertIn('Agent không bao giờ tự chạy', warning)
        self.assertEqual(0, cli('integrity-diff', self.job)[0]['changed'])

    def brief(self):
        return normalize_brief(read(ROOT / 'examples/m1/brief.json'))

    def test_new_job_records_provenance_and_degrades_without_git(self):
        self.new('auto')  # temp root is not a git repository: never blocks
        meta = read(self.p.job(self.job) / 'integrity-meta.json')
        self.assertEqual((None, None), (meta['git_head'], meta['protected_dirty']))

    def test_auto_job_refused_when_protected_code_is_dirty(self):
        dirty = {'head': 'abc123', 'dirty': True, 'changes': [' M pilot.py', '?? schemas/x.json']}
        with patch.object(Pilot, 'git_state', return_value=dirty):
            with self.assertRaisesRegex(Blocked, 'AUTO_REQUIRES_CLEAN_CODE') as ex:
                self.p.new('auto-dirty', self.brief(), mode='auto')
            self.assertIn('pilot.py', str(ex.exception))
            self.assertFalse(self.p.job('auto-dirty').exists())
            self.p.new('review-dirty', self.brief(), mode='review')
            self.assertEqual(('abc123', True), tuple(read(self.p.job('review-dirty') / 'integrity-meta.json')[k]
                                                     for k in ('git_head', 'protected_dirty')))
            cfg = read(self.root / 'config.json'); cfg['auto_require_clean_code'] = False; write(self.root / 'config.json', cfg)
            self.p.new('auto-allowed', self.brief(), mode='auto')

    def test_git_state_reads_head_and_protected_changes(self):
        git = lambda *a: subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=TEST', '-c', 'user.email=test@example.invalid', *a],
                                        check=True, capture_output=True, text=True)
        git('init', '-q'); git('add', '-A'); git('commit', '-qm', 'TEST')
        state = self.p.git_state()
        self.assertEqual((False, []), (state['dirty'], state['changes']))
        self.assertEqual(git('rev-parse', 'HEAD').stdout.strip(), state['head'])
        (self.root / 'notes.txt').write_text('TEST unprotected file')
        self.assertFalse(self.p.git_state()['dirty'])
        (self.root / 'AGENTS.md').write_text('TEST edit')
        write(self.root / 'schemas/test-extra.json', {})
        changes = self.p.git_state()['changes']
        self.assertTrue(any(x.endswith('AGENTS.md') for x in changes) and any('schemas/' in x for x in changes))
        with self.assertRaisesRegex(Blocked, 'AUTO_REQUIRES_CLEAN_CODE'):
            self.p.new('auto-dirty', self.brief(), mode='auto')


class VocabDuplicateJobTests(unittest.TestCase):
    setUp = bank_tests.BankTests.setUp
    tearDown = bank_tests.BankTests.tearDown
    source = bank_tests.BankTests.source
    two_topics = bank_tests.BankTests.two_topics

    def run_job(self, drawn):
        """What `pilot.py new` leaves behind that brief_entry() reads."""
        folder = self.tmp / 'runs' / drawn['job']
        write(folder / 'briefs/1.json', read(drawn['brief']))
        write(folder / 'brief-current.json', {'revision': 1, 'hash': 'TEST'})

    def draw(self, job, **kw):
        return vb.cmd_draw(bank_tests.args(job=job, **kw))

    def test_release_then_redraw_same_word_is_refused_while_old_job_exists(self):
        self.two_topics()
        self.run_job(self.draw('v1', word='pay'))
        vb.cmd_release(bank_tests.args(job='v1'))
        with self.assertRaises(vb.Stop) as ex:
            self.draw('v2', word='pay')
        self.assertIn('v1', str(ex.exception))
        self.assertIn('--supersede v1', str(ex.exception))
        self.assertNotIn('v2', {v.get('job') for v in vb.ledger()['entries'].values()})
        self.assertNotEqual('pay.v', self.draw('v3')['entry'])  # automatic pick skips it

    def test_supersede_needs_reason_and_is_recorded(self):
        self.two_topics()
        self.run_job(self.draw('v1', word='pay'))
        with self.assertRaisesRegex(vb.Stop, '--reason'):
            self.draw('v2', word='pay', supersede='v1')
        with self.assertRaisesRegex(vb.Stop, 'không phải job dang dở'):
            self.draw('v2', word='pay', supersede='v1,v9', reason='TEST')
        self.draw('v2', word='pay', supersede='v1', reason='TEST user decided to restart')
        record = vb.ledger()['entries']['pay.v']
        self.assertEqual(('reserved', 'v2'), (record['status'], record['job']))
        self.assertEqual([('v1', 'v2', 'TEST user decided to restart')],
                         [(x['job'], x['by'], x['reason']) for x in record['superseded']])
        vb.cmd_release(bank_tests.args(job='v2'))  # v2 never ran: history kept, word back in pool
        self.assertEqual('todo', vb.state_of(vb.ledger(), 'pay.v'))
        self.assertEqual('v1', vb.ledger()['entries']['pay.v']['superseded'][0]['job'])
        self.draw('v3', word='pay')

    def test_finished_job_does_not_block_a_redo(self):
        self.two_topics()
        self.run_job(self.draw('v1', word='pay'))
        vb.cmd_mark(bank_tests.args(job='v1', entry='pay.v', force=True, note='TEST published'))
        self.draw('v2', word='pay', redo=True, note='TEST new version')

    def test_failed_start_restores_the_previous_record(self):
        self.two_topics()
        self.run_job(self.draw('v1', word='pay'))
        before = vb.ledger()['entries']['pay.v']
        fail = type('R', (), {'returncode': 1, 'stdout': '{"blocked": "x"}', 'stderr': ''})()
        with patch.object(vb.subprocess, 'run', return_value=fail):
            with self.assertRaises(vb.Stop):
                vb.cmd_start(bank_tests.args(job='v2', word='pay', supersede='v1', reason='TEST'))
        self.assertEqual(before, vb.ledger()['entries']['pay.v'])


if __name__ == '__main__':
    unittest.main()
