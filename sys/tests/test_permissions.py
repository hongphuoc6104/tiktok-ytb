"""Persistent authority and scope behavior across fresh controller instances."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from permissions import Grants, PermissionDenied, classify


class GrantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Grants(self.root)

    def test_production_repair_persists_when_a_new_chat_controller_starts(self):
        grant = self.store.grant('production', source='TEST authorization for old-video repair',
                                jobs=['old-video'], paths=['runs/old-video/**'])
        another = Grants(self.root)
        for operation in ('content', 'repair', 'resume', 'stop'):
            self.assertEqual(another.require(grant['id'], 'production', operation, job='old-video')['id'], grant['id'])
        another.require(grant['id'], 'production', 'content', path='runs/old-video/draft/content.json')
        self.assertIsNone(grant['expires_at'])

    def test_production_cannot_upgrade_system_even_with_a_broad_path_scope(self):
        grant = self.store.grant('production', source='TEST broad content scope', jobs=['*'], paths=['*'])
        for name in ('AGENTS.md', 'README.md', '.agents/rules/execution.md', 'renderer/render.mjs', 'vocab/bank.py'):
            with self.assertRaises(PermissionDenied):
                self.store.require(grant['id'], 'production', 'content', path=name)
        with self.assertRaises(PermissionDenied):
            self.store.require(grant['id'], 'production', 'system', job='old-video')

    def test_development_can_edit_granted_system_files_without_tty(self):
        grant = self.store.grant('development', source='TEST normalization upgrade', paths=['*'])
        for name in ('AGENTS.md', 'renderer/render.mjs', 'vocab/bank.py'):
            self.store.require(grant['id'], 'development', 'system', path=name)
        with self.assertRaises(PermissionDenied):
            self.store.require(grant['id'], 'production', 'system', path='AGENTS.md')
        self.assertFalse(grant['source_transport_verified'])

    def test_other_job_revocation_and_path_escape_are_rejected(self):
        grant = self.store.grant('production', source='TEST one job only', jobs=['one'], paths=['runs/one/**'])
        with self.assertRaises(PermissionDenied):
            self.store.require(grant['id'], 'production', 'resume', job='two')
        with self.assertRaises(PermissionDenied):
            self.store.require(grant['id'], 'production', 'content', path=self.root.parent / 'outside')
        self.store.revoke(grant['id'], source='TEST explicit revocation')
        with self.assertRaises(PermissionDenied):
            Grants(self.root).require(grant['id'], 'production', 'resume', job='one')

    def test_limited_operation_grant_cannot_expand_itself(self):
        grant=self.store.grant('production',source='TEST observe/stop only',jobs=['one'],operations=['observe','stop'])
        self.store.require(grant['id'],'production','stop',job='one')
        with self.assertRaises(PermissionDenied):self.store.require(grant['id'],'production','repair',job='one')
        self.assertIsNone(self.store.find('production','execute',job='one'))
        with self.assertRaises(ValueError):self.store.grant('production',source='TEST invalid expansion',jobs=['one'],operations=['system'])
        for name in ('runs/one/checkpoints/audio/1/decision.json','runs/one/flow/attempts/old/request.json','runs/one/micro-plans/1/plan.json'):
            self.assertEqual(classify(name),'history')

    def test_history_auth_and_shared_cache_are_not_content_deletion(self):
        grant = self.store.grant('maintenance', source='TEST maintenance', jobs=['one'], paths=['*'])
        self.store.require(grant['id'], 'maintenance', 'cleanup', path='scratch/rebuildable/cache.bin')
        for path in ('runs/one/revisions/audio/1/output.json', '.state/jobs.sqlite', '.gflow/profiles/Default/Cookies', 'video/one/result.mp4'):
            with self.assertRaises(PermissionDenied):
                self.store.require(grant['id'], 'maintenance', 'cleanup', path=path)
        self.assertEqual(classify('vocab/bank.jsonl'), 'content')
        self.assertEqual(classify('vocab/bank.py'), 'system')
