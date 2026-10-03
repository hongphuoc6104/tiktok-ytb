import fcntl
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from maintenance import Maintenance, MaintenanceBlocked, digest
from permissions import Grants, PermissionDenied


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.project = Path(self.tmp.name) / 'project'; self.system = self.project / 'sys'
        self.system.mkdir(parents=True); (self.project / 'pilot.py').write_text('# launcher')
        (self.system / 'runs/job').mkdir(parents=True); (self.system / '.cache').mkdir()
        self.candidate = self.system / '.cache/generated-part.tmp'; self.candidate.write_bytes(b'render bundle')
        self.input = self.system / 'runs/job/input.txt'; self.input.write_text('frozen input')
        self.output = self.system / 'runs/job/final.wav'; self.output.write_bytes(b'durable output')
        self.m = Maintenance(self.system)
        self.grant = Grants(self.system).grant('maintenance', source='User authorizes scoped cleanup/Git', jobs=['job'], paths=['sys/.cache/**', 'sys/archive/**', 'notes.md'])['id']
    def tearDown(self): self.tmp.cleanup()
    def proof(self, p): return {'path': p.relative_to(self.project).as_posix(), 'sha256': digest(p)}
    def manifest(self):
        return {'version': 1, 'files': [{**self.proof(self.candidate), 'owner_job': 'job', 'recipe': 'regenerate saved bundle', 'inputs': [self.proof(self.input)], 'collected_outputs': [self.proof(self.output)]}]}
    def test_dry_run_then_exact_cleanup_preserves_outputs(self):
        manifest = self.manifest(); plan = self.m.cleanup(manifest)
        self.assertTrue(plan['dry_run']); self.assertTrue(self.candidate.exists()); self.assertFalse((self.system / '.state/maintenance').exists())
        result = self.m.cleanup(manifest, execute=True, grant=self.grant, review_hash=plan['review_hash'])
        self.assertTrue(result['complete']); self.assertFalse(self.candidate.exists()); self.assertTrue(self.output.exists()); self.assertTrue(self.input.exists())
    def test_production_and_outside_job_cannot_cleanup(self):
        prod = Grants(self.system).grant('production', source='Make job', jobs=['job'], paths=['sys/.cache/**'])['id']
        plan = self.m.cleanup(self.manifest())
        with self.assertRaises(PermissionDenied): self.m.cleanup(self.manifest(), execute=True, grant=prod, review_hash=plan['review_hash'])
        Grants(self.system).revoke(self.grant, source='Revoke maintenance')
        with self.assertRaises(PermissionDenied): self.m.cleanup(self.manifest(), execute=True, grant=self.grant, review_hash=plan['review_hash'])
    def test_changed_candidate_and_review_hash_rejected(self):
        manifest = self.manifest(); plan = self.m.cleanup(manifest); self.candidate.write_text('changed')
        with self.assertRaises(MaintenanceBlocked): self.m.cleanup(manifest, execute=True, grant=self.grant, review_hash=plan['review_hash'])
        with self.assertRaises(MaintenanceBlocked): self.m.cleanup(self.manifest(), execute=True, grant=self.grant, review_hash='wrong')
    def test_unknown_and_cross_job_evidence_preserved(self):
        p = self.system / 'runs/job/request.json'; p.write_text('{"state":"unknown"}')
        with self.assertRaisesRegex(MaintenanceBlocked, 'pending'): self.m.cleanup(self.manifest())
        p.write_text('{"state":"collected"}'); other = self.system / 'runs/other'; other.mkdir()
        (other / 'evidence.json').write_text(json.dumps({'reference': str(self.candidate)}))
        with self.assertRaisesRegex(MaintenanceBlocked, 'referenced'): self.m.cleanup(self.manifest())
    def test_live_lease_prevents_delete(self):
        plan = self.m.cleanup(self.manifest())
        with (self.system / 'runs/job/execution-lease.lock').open('a') as h:
            fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(MaintenanceBlocked, 'live writer'): self.m.cleanup(self.manifest(), execute=True, grant=self.grant, review_hash=plan['review_hash'])
        self.assertTrue(self.candidate.exists())
    def test_live_other_job_prevents_cross_job_reference_race(self):
        plan = self.m.cleanup(self.manifest()); other = self.system / 'runs/other'; other.mkdir()
        with (other / 'execution-lease.lock').open('a') as h:
            fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(MaintenanceBlocked, 'live writer'):
                self.m.cleanup(self.manifest(), execute=True, grant=self.grant, review_hash=plan['review_hash'])
        self.assertTrue(self.candidate.exists())
    def test_collected_output_in_temporary_storage_is_not_durable_proof(self):
        temporary_output = self.system / '.cache/collected.wav'; temporary_output.write_bytes(b'not durable')
        manifest = self.manifest(); manifest['files'][0]['collected_outputs'] = [self.proof(temporary_output)]
        with self.assertRaisesRegex(MaintenanceBlocked, 'durable storage'): self.m.cleanup(manifest)
    def test_history_secret_symlink_not_candidates(self):
        manifest = self.manifest(); manifest['files'][0].update(self.proof(self.input))
        with self.assertRaisesRegex(MaintenanceBlocked, 'temporary'): self.m.cleanup(manifest)
        token = self.system / '.cache/token.json'; token.write_text('{}'); manifest['files'][0].update(self.proof(token))
        with self.assertRaises(MaintenanceBlocked): self.m.cleanup(manifest)
        link = self.system / '.cache/link.tmp'; link.symlink_to(self.candidate); manifest['files'][0]['path'] = 'sys/.cache/link.tmp'
        with self.assertRaisesRegex(MaintenanceBlocked, 'Symlinks'): self.m.cleanup(manifest)
    def test_inputs_and_durable_output_required(self):
        manifest = self.manifest(); manifest['files'][0]['collected_outputs'] = []
        with self.assertRaises(MaintenanceBlocked): self.m.cleanup(manifest)
        manifest = self.manifest(); self.output.unlink()
        with self.assertRaises(MaintenanceBlocked): self.m.cleanup(manifest)
    def test_archive_verified_without_source_deletion(self):
        paths = ['sys/runs/job/final.wav']; grant = Grants(self.system).grant('maintenance', source='Archive WAV', jobs=['job'], paths=[*paths, 'sys/archive/**'])['id']
        plan = self.m.archive(paths=paths, destination='sys/archive/one')
        result = self.m.archive(paths=paths, destination='sys/archive/one', grant=grant, execute=True, review_hash=plan['review_hash'])
        self.assertTrue(result['verified']); self.assertTrue(self.output.exists()); self.assertEqual(digest(self.output), digest(self.system / 'archive/one/sys/runs/job/final.wav'))
        with self.assertRaises(MaintenanceBlocked): self.m.archive(paths=paths, destination='sys/archive/one')

    def test_external_archive_needs_explicit_destination_scope(self):
        paths = ['sys/runs/job/final.wav']; destination = str(Path(self.tmp.name) / 'external-archive')
        grant = Grants(self.system).grant('maintenance', source='Archive WAV', jobs=['job'], paths=paths)['id']
        plan = self.m.archive(paths=paths, destination=destination)
        with self.assertRaisesRegex(MaintenanceBlocked, 'archive-scope'):
            self.m.archive(paths=paths, destination=destination, grant=grant, execute=True, review_hash=plan['review_hash'])
        self.m.authorize_archive(grant=grant, destination=destination, source='User authorizes this external backup directory')
        result = self.m.archive(paths=paths, destination=destination, grant=grant, execute=True, review_hash=plan['review_hash'])
        self.assertTrue(result['verified']); self.assertTrue(self.output.exists())
        self.assertEqual(digest(self.output), digest(Path(destination) / paths[0]))


class GitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.project = Path(self.tmp.name) / 'project'; self.system = self.project / 'sys'; self.system.mkdir(parents=True)
        (self.project / 'pilot.py').write_text('# launcher'); (self.project / '.gitignore').write_text('sys/.state/\n')
        self.git('init', '-b', 'work'); self.git('config', 'user.name', 'Isolated Test'); self.git('config', 'user.email', 'test@example.invalid')
        for name in ('notes.md', 'other.md'): (self.project / name).write_text('original\n')
        self.git('add', 'notes.md', 'other.md', '.gitignore', 'pilot.py'); self.git('commit', '-m', 'Fixture baseline')
        self.bare = Path(self.tmp.name) / 'remote.git'; subprocess.run(['git', 'init', '--bare', str(self.bare)], check=True, capture_output=True)
        self.git('remote', 'add', 'origin', str(self.bare)); self.git('push', 'origin', 'HEAD:refs/heads/work'); self.m = Maintenance(self.system)
        self.grant = Grants(self.system).grant('maintenance', source='Scoped checkpoint', paths=['notes.md'])['id']
        self.m.authorize_git(grant=self.grant, branch='work', source='User authorizes work, configured origin, commit only')
        (self.project / 'notes.md').write_text('reviewed\n'); (self.project / 'other.md').write_text('unrelated\n')
    def tearDown(self): self.tmp.cleanup()
    def git(self, *args): return subprocess.run(['git', '-C', str(self.project), *args], check=True, capture_output=True, text=True).stdout.strip()
    def plan(self): return self.m.git_plan(branch='work', paths=['notes.md'], grant=self.grant)
    def checkpoint(self, plan, **args): return self.m.git_checkpoint(branch='work', paths=['notes.md'], grant=self.grant, execute=True, review_hash=plan['review_hash'], message='Isolated checkpoint', **args)
    def test_allowlist_commit_keeps_other_edits(self):
        result = self.checkpoint(self.plan()); self.assertFalse(result['pushed']); self.assertEqual(self.git('show', '--pretty=', '--name-only', 'HEAD'), 'notes.md')
        self.assertIn('other.md', self.git('status', '--porcelain')); self.assertEqual(self.git('diff', '--cached', '--name-only'), '')
    def test_reviewed_tracked_deletion_is_staged_without_deleting_other_files(self):
        (self.project / 'notes.md').unlink(); result = self.checkpoint(self.plan())
        self.assertFalse(result['pushed']); self.assertEqual(self.git('show', '--pretty=', '--name-status', 'HEAD'), 'D\tnotes.md')
        self.assertTrue((self.project / 'other.md').exists())
    def test_branch_paths_and_staging_enforced(self):
        with self.assertRaises(MaintenanceBlocked): self.m.git_plan(branch='wrong', paths=['notes.md'], grant=self.grant)
        with self.assertRaises(PermissionDenied): self.m.git_plan(branch='work', paths=['other.md'], grant=self.grant)
        self.git('add', 'other.md')
        with self.assertRaisesRegex(MaintenanceBlocked, 'preexisting'): self.plan()
    def test_secret_and_changed_review_rejected(self):
        (self.project / 'notes.md').write_text('refresh_token="sensitive-looking-token"\n')
        with self.assertRaisesRegex(MaintenanceBlocked, 'secret'): self.plan()
        (self.project / 'notes.md').write_text('ready\n'); plan = self.plan(); (self.project / 'notes.md').write_text('changed\n')
        with self.assertRaisesRegex(MaintenanceBlocked, 'Re-review'): self.checkpoint(plan)
    def test_known_nonfastforward_preflight_preserves_head_and_remote_without_force(self):
        self.git('push', 'origin', 'HEAD:refs/heads/work')
        clone = Path(self.tmp.name) / 'other-clone'
        subprocess.run(['git', 'clone', '--branch', 'work', str(self.bare), str(clone)], check=True, capture_output=True)
        def git_other(*args):
            return subprocess.run(['git', '-C', str(clone), *args], check=True, capture_output=True, text=True).stdout.strip()
        git_other('config', 'user.name', 'Other Fixture'); git_other('config', 'user.email', 'other@example.invalid')
        (clone / 'other.md').write_text('remote advanced\n'); git_other('add', 'other.md'); git_other('commit', '-m', 'Remote advances'); git_other('push', 'origin', 'work')
        remote_head = git_other('rev-parse', 'HEAD'); local_before = self.git('rev-parse', 'HEAD')
        self.m.authorize_git(grant=self.grant, branch='work', source='Normal push only', allow_push=True)
        with self.assertRaisesRegex(MaintenanceBlocked, 'auth/conflict'): self.checkpoint(self.plan(), push=True)
        self.assertEqual(self.git('rev-parse', 'HEAD'), local_before)
        actual_remote = subprocess.run(['git', '--git-dir', str(self.bare), 'rev-parse', 'refs/heads/work'], check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(actual_remote, remote_head)
        records = [json.loads(p.read_text()) for p in (self.system / '.state/maintenance').glob('*.json')]
        self.assertFalse(any(x.get('kind') == 'git_result' for x in records))
    def test_secret_removed_from_allowed_file_still_blocks_historical_push(self):
        (self.project / 'notes.md').write_text('access_token="QA_SYNTHETIC_SECRET_123456789"\n')
        self.git('add', 'notes.md'); self.git('commit', '-m', 'Fixture prior secret')
        (self.project / 'notes.md').write_text('secret removed\n'); self.git('add', 'notes.md'); self.git('commit', '-m', 'Fixture remove secret')
        (self.project / 'notes.md').write_text('current clean change\n')
        self.m.authorize_git(grant=self.grant, branch='work', source='Normal scoped push', allow_push=True)
        with self.assertRaisesRegex(MaintenanceBlocked, 'historical/index'): self.plan()
    def test_index_filter_secret_is_rejected_before_commit(self):
        script = self.project / 'fixture_filter.py'
        script.write_text('import sys\nsys.stdin.read()\nprint("refresh_token=QA_SYNTHETIC_SECRET_123456789")\n')
        self.git('config', 'filter.fixture.clean', 'python3 ' + str(script))
        (self.project / '.gitattributes').write_text('notes.md filter=fixture\n')
        before = self.git('rev-parse', 'HEAD')
        with self.assertRaisesRegex(MaintenanceBlocked, 'historical/index'): self.checkpoint(self.plan())
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
    def test_multiple_push_urls_cannot_expand_remote_scope(self):
        second = Path(self.tmp.name) / 'second.git'
        subprocess.run(['git', 'init', '--bare', str(second)], check=True, capture_output=True)
        self.git('remote', 'set-url', '--add', '--push', 'origin', str(self.bare))
        self.git('remote', 'set-url', '--add', '--push', 'origin', str(second))
        with self.assertRaisesRegex(MaintenanceBlocked, 'exactly one'): self.plan()
    def test_explicit_normal_push_to_isolated_remote(self):
        plan = self.plan()
        with self.assertRaisesRegex(MaintenanceBlocked, 'commit only'): self.checkpoint(plan, push=True)
        self.m.authorize_git(grant=self.grant, branch='work', source='User authorizes normal push to isolated origin', allow_push=True)
        result = self.checkpoint(self.plan(), push=True); self.assertTrue(result['pushed'])
        remote = subprocess.run(['git', '--git-dir', str(self.bare), 'rev-parse', 'refs/heads/work'], check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(remote, result['commit'])

if __name__ == '__main__': unittest.main()
