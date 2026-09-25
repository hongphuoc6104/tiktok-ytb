"""A mode migration preserves artifacts but requires fresh machine decisions."""
import unittest
from unittest.mock import patch
import test_workflow as fixtures
from pilot import Blocked, read, write, digest
import workflow as wf


class ModeMigrationTests(unittest.TestCase):
    setUp = fixtures.WorkflowTests.setUp
    new = fixtures.WorkflowTests.new
    approve = fixtures.WorkflowTests.approve

    def migrate(self):
        return wf.set_mode(self.p, self.job, 'auto', self.job, 'User requested auto')

    def test_existing_content_is_reused_but_user_approval_is_not(self):
        self.new(); self.approve('content')
        original = self.p.job(self.job) / 'workflow.json'
        stamp = digest(original)
        content_revision = self.p.rows(self.job)['content']['revision']
        old = wf.current(self.p, self.job, 'content')
        old_decision = digest(self.p.path(self.job, old['decision']))
        self.migrate()
        self.assertEqual(digest(original), stamp)
        self.assertEqual(wf.settings(self.p, self.job)['mode'], 'auto')
        self.assertFalse(wf.approved(self.p, self.job, 'content'))
        with self.assertRaises(Blocked): self.p.gate(self.job, 'audio')
        fresh = wf.prepare(self.p, self.job, 'content')
        self.assertGreater(fresh['revision'], old['revision'])
        self.assertEqual(self.p.rows(self.job)['content']['revision'], content_revision)
        self.assertEqual(digest(self.p.path(self.job, old['decision'])), old_decision)
        with self.assertRaises(Blocked):
            wf.approve(self.p, self.job, 'content', fresh['revision'], 'not a machine review')
        self.assertEqual(wf.next_step(self.p, self.job)['action'], 'machine_review')
        self.assertFalse(self.migrate()['changed'])

    def test_confirmation_and_clean_code_required(self):
        self.new()
        with self.assertRaises(Blocked):
            wf.set_mode(self.p, self.job, 'auto', 'wrong', 'request')
        with self.assertRaises(Blocked):
            wf.set_mode(self.p, self.job, 'auto', self.job, '')
        with patch.object(self.p, 'clean_code', side_effect=Blocked('dirty')):
            with self.assertRaises(Blocked): self.migrate()
        self.assertEqual(wf.settings(self.p, self.job)['mode'], 'review')

    def test_history_tamper_and_unlogged_file_rejected(self):
        self.new()
        write(self.p.job(self.job)/'workflow-migrations/unlogged.json', {'mode': 'auto'})
        self.assertEqual(wf.settings(self.p, self.job)['mode'], 'review')
        result = self.migrate()
        path = self.p.path(self.job, result['history'])
        record = read(path); record['reason'] = 'edited'; write(path, record)
        with self.assertRaisesRegex(Blocked, 'WORKFLOW_MIGRATION_TAMPER'):
            wf.settings(self.p, self.job)

    def test_existing_media_attempt_prevents_migration(self):
        self.new()
        actual_rows = self.p.rows(self.job)
        rows = {name: dict(row) for name, row in actual_rows.items()}
        rows['audio']['revision'] = 1
        with patch.object(self.p, 'refresh'), patch.object(self.p, 'rows', return_value=rows):
            with self.assertRaisesRegex(Blocked, 'MODE_MIGRATION_AFTER_MEDIA'):
                self.migrate()
        self.assertEqual(wf.settings(self.p, self.job)['mode'], 'review')
