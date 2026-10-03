"""Forward maintenance QA on disposable projects and local bare Git remotes.

Real maintenance API/CLI, locks and Git; no production data, services or providers.
"""
import copy
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from maintenance import Maintenance, MaintenanceBlocked, digest
from permissions import Grants, PermissionDenied
from pilot import ROOT


class IndependentRetention(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='independent-retention-')
        self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)/'custom-project';self.system=self.project/'sys';self.system.mkdir(parents=True)
        (self.project/'pilot.py').write_text('# disposable launcher marker\n')
        for job in ('A','B'):(self.system/'runs'/job).mkdir(parents=True)
        self.input=self.make('sys/runs/A/brief.txt','source dialogue')
        self.output=self.make('video/A/final.mp4','collected output fixture')
        self.candidate=self.make('sys/runs/A/scratch/repro.bin','reproducible intermediate')
        self.m=Maintenance(self.system)
        self.grant=Grants(self.system).grant('maintenance',source='TEST: maintain only job A generated data',jobs=['A'],paths=['sys/runs/**','sys/.cache/**','video/**','archive/**'])['id']

    def make(self,relative,value):
        path=self.project/relative;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value);return path

    def proof(self,path):return {'path':str(path.relative_to(self.project)),'sha256':digest(path)}

    def manifest(self,candidate=None,owner='A'):
        candidate=candidate or self.candidate
        return {'version':1,'files':[{**self.proof(candidate),'owner_job':owner,'recipe':'TEST: deterministic fixture rebuild from source','inputs':[self.proof(self.input)],'collected_outputs':[self.proof(self.output)]}]}

    def execute(self,manifest):
        plan=self.m.cleanup(manifest)
        return self.m.cleanup(manifest,execute=True,grant=self.grant,review_hash=plan['review_hash'])

    def cli(self,*args):
        result=subprocess.run([sys.executable,str(ROOT/'maintenance.py'),*args,'--root',str(self.system)],capture_output=True,text=True)
        return result.returncode,json.loads(result.stdout)

    def test_cli_exact_cleanup_keeps_sources_outputs_and_journal(self):
        manifest=self.manifest();path=Path(self.tmp.name)/'reviewed-manifest.json';path.write_text(json.dumps(manifest))
        before={str(x):digest(x) for x in (self.input,self.output)}
        rc,plan=self.cli('cleanup','--manifest',str(path));self.assertEqual(rc,0,plan);self.assertTrue(self.candidate.exists())
        rc,result=self.cli('cleanup','--manifest',str(path),'--execute','--grant',self.grant,'--review-hash',plan['review_hash'])
        self.assertEqual(rc,0,result);self.assertTrue(result['complete']);self.assertFalse(self.candidate.exists())
        self.assertEqual({str(x):digest(x) for x in (self.input,self.output)},before)
        records=[json.loads(p.read_text()) for p in (self.system/'.state/maintenance').glob('*.json')]
        self.assertEqual([r['kind'] for r in sorted(records,key=lambda r:r['kind'])],['cleanup_intent','cleanup_result'])
        self.assertEqual(result['deleted'],[manifest['files'][0]['path']])

    def test_cross_job_absolute_relative_and_basename_references_preserve_cache(self):
        evidence=self.system/'runs/B/evidence.json'
        for reference in (str(self.candidate),self.proof(self.candidate)['path'],self.candidate.name):
            evidence.write_text(json.dumps({'dependency':reference}))
            with self.assertRaisesRegex(MaintenanceBlocked,'referenced'):self.execute(self.manifest())
            self.assertTrue(self.candidate.exists())

    def test_owner_unknown_journals_are_preserved_for_every_pending_state(self):
        request=self.system/'runs/A/request.json'
        for state in ('unknown','ambiguous','submitted','running','inflight','generating','generated','not_collected'):
            request.write_text(json.dumps({'nested':{'submit_state':state,'account':'QA-only','session':'original'}}))
            stamp=digest(request)
            with self.assertRaisesRegex(MaintenanceBlocked,'pending'):self.execute(self.manifest())
            self.assertEqual(digest(request),stamp);self.assertTrue(self.candidate.exists())

    def test_owner_field_cannot_relabel_other_job_cache_and_skip_its_unknown_request(self):
        candidate=self.make('sys/runs/B/scratch/B-only.bin','B still needs this intermediate')
        request=self.make('sys/runs/B/request.json',json.dumps({'state':'unknown','account':'QA-B','session':'QA-original-B'}))
        stamp=digest(request)
        with self.assertRaises((MaintenanceBlocked,PermissionDenied)):
            self.execute(self.manifest(candidate,owner='A'))
        self.assertTrue(candidate.exists());self.assertEqual(digest(request),stamp)

    def test_shared_cache_crossjob_reference_and_hardlinks_survive(self):
        shared=self.make('sys/.cache/shared.bin','shared content-addressed result')
        self.make('sys/runs/B/request.json',json.dumps({'state':'unknown','local_reference':str(shared)}))
        with self.assertRaises(MaintenanceBlocked):self.execute(self.manifest(shared))
        self.assertTrue(shared.exists())
        (self.system/'runs/B/request.json').unlink()
        hardlink=self.system/'runs/B/shared-hardlink.bin';os.link(shared,hardlink)
        with self.assertRaisesRegex(MaintenanceBlocked,'Hard-linked'):self.execute(self.manifest(shared))
        self.assertTrue(shared.exists());self.assertTrue(hardlink.exists())

    def test_crossjob_pending_directory_reference_preserves_shared_cache_members(self):
        shared=self.make('sys/.cache/shared-tts/repro.bin','cache member for unresolved remote request')
        request=self.make('sys/runs/B/request.json',json.dumps({'state':'unknown','cache_dir':str(shared.parent),'account':'QA-B','session':'QA-B-original'}))
        stamp=digest(request)
        with self.assertRaises(MaintenanceBlocked):self.execute(self.manifest(shared,owner='A'))
        self.assertTrue(shared.exists());self.assertEqual(digest(request),stamp)

    def test_auth_history_and_symlink_candidates_are_not_cleanup(self):
        for path in ('sys/runs/A/revisions/1/evidence.json','sys/runs/A/flow/attempts/X/request.json','sys/.gflow/profiles/user/cache.bin','sys/.cache/access_token.json','sys/.cache/session.key','sys/.cache/jobs.sqlite'):
            candidate=self.make(path,'{}')
            with self.assertRaises(MaintenanceBlocked,msg=path):self.execute(self.manifest(candidate))
            self.assertTrue(candidate.exists())
        link=self.system/'runs/A/scratch/link.bin';link.symlink_to(self.candidate)
        with self.assertRaisesRegex(MaintenanceBlocked,'Symlinks'):self.execute(self.manifest(link))
        self.assertTrue(self.candidate.exists())

    def test_cleanup_preserves_preexisting_but_not_named_pending_refs(self):
        plan=self.m.cleanup(self.manifest())
        for lease in (self.system/'runs/A/execution-lease.lock',self.system/'runs/B/execution-lease.lock',self.system/'.state/process.lock'):
            lease.parent.mkdir(parents=True,exist_ok=True)
            with lease.open('a') as handle:
                fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaisesRegex(MaintenanceBlocked,'live writer'):
                    self.m.cleanup(self.manifest(),execute=True,grant=self.grant,review_hash=plan['review_hash'])
                self.assertTrue(self.candidate.exists())

    def test_changed_proof_review_hash_and_revoked_grant_prevent_deletion(self):
        manifest=self.manifest();plan=self.m.cleanup(manifest)
        self.input.write_text('changed source')
        with self.assertRaisesRegex(MaintenanceBlocked,'hash'):self.m.cleanup(manifest,execute=True,grant=self.grant,review_hash=plan['review_hash'])
        manifest=self.manifest();plan=self.m.cleanup(manifest)
        with self.assertRaisesRegex(MaintenanceBlocked,'Re-review'):self.m.cleanup(manifest,execute=True,grant=self.grant,review_hash='not-reviewed')
        Grants(self.system).revoke(self.grant,source='TEST: revoke maintenance')
        with self.assertRaises(PermissionDenied):self.m.cleanup(manifest,execute=True,grant=self.grant,review_hash=plan['review_hash'])
        self.assertTrue(self.candidate.exists())

    def test_archive_external_scope_hash_and_source_preservation(self):
        paths=[self.proof(self.output)['path']];dest=str(Path(self.tmp.name)/'outside-archive')
        plan=self.m.archive(paths=paths,destination=dest)
        with self.assertRaisesRegex(MaintenanceBlocked,'archive-scope'):
            self.m.archive(paths=paths,destination=dest,grant=self.grant,execute=True,review_hash=plan['review_hash'])
        self.m.authorize_archive(grant=self.grant,destination=dest,source='TEST: this exact external backup destination')
        before=digest(self.output)
        result=self.m.archive(paths=paths,destination=dest,grant=self.grant,execute=True,review_hash=plan['review_hash'])
        self.assertTrue(result['verified']);self.assertEqual(digest(self.output),before)
        self.assertEqual(digest(Path(dest)/paths[0]),before)
        with self.assertRaises(MaintenanceBlocked):self.m.archive(paths=paths,destination=dest)

    def test_archive_cannot_expand_job_scope_with_broad_path_allowlist(self):
        other=self.make('video/B/final.mp4','B artifact outside the grant')
        paths=[self.proof(other)['path']];dest='archive/B-copy'
        plan=self.m.archive(paths=paths,destination=dest)
        with self.assertRaises(PermissionDenied):self.m.archive(paths=paths,destination=dest,grant=self.grant,execute=True,review_hash=plan['review_hash'])
        self.assertFalse((self.project/dest).exists());self.assertTrue(other.exists())

    def test_archive_does_not_copy_owned_artifact_while_writer_has_lease(self):
        paths=[self.proof(self.output)['path']];dest='archive/A-copy';plan=self.m.archive(paths=paths,destination=dest)
        with (self.system/'runs/A/execution-lease.lock').open('a') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaisesRegex(MaintenanceBlocked,'live writer'):
                self.m.archive(paths=paths,destination=dest,grant=self.grant,execute=True,review_hash=plan['review_hash'])
        self.assertFalse((self.project/dest).exists())

    def test_archive_does_not_copy_credential_files_under_broad_grant(self):
        broad=Grants(self.system).grant('maintenance',source='TEST archive artifact allowlist must preserve credentials',jobs=['A'],paths=['**'],operations=['archive'])['id']
        for relative,data in (('.env','PASSWORD=QA_SYNTHETIC_SECRET_123456789\n'),('sys/private.pem','-----BEGIN PRIVATE KEY-----\nQA synthetic test only\n-----END PRIVATE KEY-----\n')):
            source=self.make(relative,data);stamp=digest(source)
            with self.assertRaises(MaintenanceBlocked,msg=relative):
                self.m.archive(paths=[relative],destination='archive/no-secrets')
            self.assertEqual(digest(source),stamp)


class IndependentDocumentation(unittest.TestCase):
    def test_advertised_cli_commands_exist_without_provider_calls(self):
        commands={
            ('pilot.py','--help'):('observe','author','stop','takeover','mode','bind-session','micro-plan','micro-result','grant','migrate','rollback-migration','adopt-code'),
            ('maintenance.py','--help'):('cleanup','archive','archive-scope','git-scope','git','--review-hash','--execute','--root'),
            ('scripts/bootstrap.py','--help'):('plan','check','apply','resume','--install'),
            ('vocab/bank.py','--help'):('start','draw','mark','release','audit','--source','--grant','--session','--scene-count'),
            ('-m','colab_bridge','--help'):('status','start','reconcile','setup','stop','synthesize','render','collect','--account','--session'),
            ('-m','dashboard.server','--help'):('--root','--port','--python'),
        }
        for args,tokens in commands.items():
            result=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,(args,result.stderr))
            for token in tokens:self.assertIn(token,result.stdout,(args,token))

    def test_four_skills_and_new_direction_have_concrete_current_sources(self):
        skills=ROOT.parent/'.agents/skills'
        actual=sorted(p.parent.name for p in skills.glob('*/SKILL.md'))
        self.assertEqual(actual,['vp-development','vp-maintenance','vp-production','vp-setup'])
        channel=json.loads((ROOT/'vocab/channel.json').read_text())
        self.assertEqual(channel['language'],'en');self.assertEqual(channel['aspect_ratio'],'9:16')
        self.assertEqual(channel['allowed_levels'],['B1','B2','C1']);self.assertIsNone(channel['scene_count'])
        self.assertEqual(channel['outputs'][0]['speed'],0.92)
        self.assertEqual(channel['outputs'][0]['voice'],'reference-narrator')
        workflow_doc=(ROOT/'docs/workflow.md').read_text()
        for token in ('outline','dialogue','audio','images','video','without a machine reviewer','connected agent/author'):
            self.assertIn(token,workflow_doc)
        production=(skills/'vp-production/SKILL.md').read_text()
        self.assertIn('Profile sys/vocab/channel.json',production)
        from scripts import director_context
        for stage in director_context.REFERENCES:
            context=director_context.context(ROOT,stage,{'video_type':'vocabulary'})
            self.assertIn('vp-production',context)
            self.assertNotIn('Local craft guidance (vp-content',context)

    def test_active_entrypoint_doc_and_skill_file_links_resolve(self):
        paths=[ROOT.parent/p for p in ('INDEX.md','AGENTS.md','README.md','GEMINI.md')]
        paths += [ROOT/'docs'/p for p in ('INDEX.md','getting-started.md','session-start.md','workflow.md','contracts.md','vocabulary.md','story-planning.md','narration-length-guidance.md','director-system.md','colab-tts.md','image-repair-loops.md','maintenance.md','AGY-SETUP.md')]
        paths += list((ROOT.parent/'.agents/skills').rglob('*.md'))
        broken=[]
        for path in paths:
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                target=target.strip('<>').split('#',1)[0]
                if not target or re.match(r'^[A-Za-z]+:',target):continue
                if not (path.parent/target).exists():broken.append((str(path.relative_to(ROOT.parent)),target))
        self.assertEqual(broken,[])


class IndependentGit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='independent-git-');self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)/'repo';self.system=self.project/'sys';self.system.mkdir(parents=True)
        (self.project/'pilot.py').write_text('# isolated launcher\n')
        (self.project/'.gitignore').write_text('sys/.state/\nignored.txt\n')
        for path in ('allowed.md','other-user.md'):(self.project/path).write_text('baseline\n')
        self.git('init','-b','codex/QA');self.git('config','user.name','QA Isolated');self.git('config','user.email','qa@example.invalid')
        self.git('add','pilot.py','.gitignore','allowed.md','other-user.md');self.git('commit','-m','QA baseline')
        self.remote=Path(self.tmp.name)/'remote.git';self.callgit('init','--bare',str(self.remote))
        self.git('remote','add','origin',str(self.remote));self.git('push','origin','HEAD:refs/heads/codex/QA')
        self.baseline=self.git('rev-parse','HEAD')
        self.m=Maintenance(self.system)
        self.grant=Grants(self.system).grant('maintenance',source='TEST: checkpoint allowed.md only on codex/QA origin',paths=['allowed.md'],operations=['git'])['id']
        self.m.authorize_git(grant=self.grant,branch='codex/QA',remote='origin',allow_push=True,source='TEST: normal push of this file allowlist')
        (self.project/'allowed.md').write_text('authorized update\n')
        (self.project/'other-user.md').write_text('other user local edit\n')

    def callgit(self,*args):return subprocess.run(['git',*args],check=True,capture_output=True,text=True).stdout.strip()
    def git(self,*args):return self.callgit('-C',str(self.project),*args)
    def plan(self,paths=None):return self.m.git_plan(branch='codex/QA',paths=paths or ['allowed.md'],grant=self.grant)
    def checkpoint(self,plan,push=False):
        return self.m.git_checkpoint(branch='codex/QA',paths=['allowed.md'],grant=self.grant,execute=True,review_hash=plan['review_hash'],message='QA authorized checkpoint',push=push)
    def remote_head(self):return self.callgit('--git-dir',str(self.remote),'rev-parse','refs/heads/codex/QA')

    def test_normal_push_changes_exact_allowlist_preserving_other_user_edits(self):
        other_hash=digest(self.project/'other-user.md');result=self.checkpoint(self.plan(),push=True)
        self.assertTrue(result['pushed']);self.assertEqual(self.remote_head(),result['commit'])
        self.assertEqual(self.git('show','--pretty=','--name-only','HEAD'),'allowed.md')
        self.assertEqual(digest(self.project/'other-user.md'),other_hash)
        self.assertIn('other-user.md',self.git('status','--porcelain'))
        self.assertEqual(self.git('diff','--cached','--name-only'),'')

    def test_preexisting_staging_and_out_of_scope_files_are_kept(self):
        self.git('add','other-user.md');index=self.git('ls-files','--stage')
        with self.assertRaisesRegex(MaintenanceBlocked,'preexisting'):self.plan()
        self.assertEqual(self.git('ls-files','--stage'),index);self.assertEqual(self.git('rev-parse','HEAD'),self.baseline)
        self.git('reset','--','other-user.md')
        with self.assertRaises(PermissionDenied):self.plan(['other-user.md'])

    def test_symlink_and_secret_plaintext_are_never_checkpointed(self):
        allowed=self.project/'allowed.md';allowed.unlink();allowed.symlink_to('other-user.md')
        with self.assertRaisesRegex(MaintenanceBlocked,'Symlinks'):self.plan()
        allowed.unlink();allowed.write_text('refresh_token=QA_SYNTHETIC_SECRET_123456789\n')
        with self.assertRaisesRegex(MaintenanceBlocked,'secret'):self.plan()

    def test_review_hash_and_remote_identity_cannot_change(self):
        plan=self.plan();(self.project/'allowed.md').write_text('changed after review\n')
        with self.assertRaisesRegex(MaintenanceBlocked,'Re-review'):self.checkpoint(plan)
        second=Path(self.tmp.name)/'other-remote.git';self.callgit('init','--bare',str(second));self.git('remote','set-url','origin',str(second))
        with self.assertRaisesRegex(MaintenanceBlocked,'branch/remote'):self.plan()
        self.assertEqual(self.git('rev-parse','HEAD'),self.baseline)

    def test_unreviewed_outgoing_history_cannot_be_pushed_with_allowed_checkpoint(self):
        hidden=self.project/'other-user-secret.md';hidden.write_text('access_token="QA_SYNTHETIC_SECRET_123456789"\n')
        self.git('add','other-user-secret.md');self.git('commit','-m','Other user unpushed history outside task')
        before=self.remote_head()
        with self.assertRaises((MaintenanceBlocked,PermissionDenied)):
            plan=self.plan();self.checkpoint(plan,push=True)
        self.assertEqual(self.remote_head(),before,'Normal HEAD push must not transfer unauthorized earlier commits')

    def test_outgoing_commit_message_secrets_are_not_pushed(self):
        self.git('add','allowed.md');self.git('commit','-m','access_token="QA_SYNTHETIC_SECRET_123456789"')
        (self.project/'allowed.md').write_text('another safe scoped update\n')
        before=self.remote_head()
        with self.assertRaisesRegex(MaintenanceBlocked,'secret'):
            plan=self.plan();self.checkpoint(plan,push=True)
        self.assertEqual(self.remote_head(),before)

    def test_push_followtags_config_cannot_transfer_ungranted_tag(self):
        self.git('tag','-a','other-user-tag','-m','Other user local annotated tag',self.baseline)
        self.git('config','push.followTags','true')
        result=self.checkpoint(self.plan(),push=True)
        self.assertTrue(result['pushed'])
        tags=self.callgit('--git-dir',str(self.remote),'tag','--list')
        self.assertEqual(tags,'','Granted branch push must not silently include extra tag refs')

    def test_commit_hook_cannot_include_other_user_files_in_allowlist_commit(self):
        hook=self.project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\ngit add -- other-user.md\n');hook.chmod(0o700)
        plan=self.plan()
        try:self.checkpoint(plan)
        except MaintenanceBlocked:pass
        if self.git('rev-parse','HEAD') != self.baseline:
            self.assertEqual(self.git('show','--pretty=','--name-only','HEAD'),'allowed.md')

    def test_failing_existing_hook_is_not_silently_bypassed(self):
        hook=self.project/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o700)
        before=self.remote_head()
        with self.assertRaises(MaintenanceBlocked):self.checkpoint(self.plan(),push=True)
        self.assertEqual(self.git('rev-parse','HEAD'),self.baseline)
        self.assertEqual(self.remote_head(),before)

    def test_known_nonfastforward_rejects_before_commit_without_force(self):
        clone=Path(self.tmp.name)/'other-clone';self.callgit('clone','--branch','codex/QA',str(self.remote),str(clone))
        def other(*args):return self.callgit('-C',str(clone),*args)
        other('config','user.name','QA Other');other('config','user.email','qa-other@example.invalid')
        (clone/'other-user.md').write_text('remote changed\n');other('add','other-user.md');other('commit','-m','QA remote update');other('push','origin','codex/QA')
        remote_before=self.remote_head()
        with self.assertRaisesRegex(MaintenanceBlocked,'remote|outgoing|auth/conflict|ancestor|fast.forward'):self.checkpoint(self.plan(),push=True)
        self.assertEqual(self.remote_head(),remote_before)
        self.assertEqual(self.git('rev-parse','HEAD'),self.baseline,'Known remote conflict must stop before creating a new commit')

    def test_remote_race_after_commit_keeps_local_checkpoint_and_remote_without_force(self):
        clone=Path(self.tmp.name)/'race-clone';self.callgit('clone','--branch','codex/QA',str(self.remote),str(clone))
        def other(*args):return self.callgit('-C',str(clone),*args)
        other('config','user.name','QA Other');other('config','user.email','qa-other@example.invalid')
        plan=self.plan();original=self.m._git;remote_after=[]
        def scheduled_git(*args):
            result=original(*args)
            if args[0]=='commit':
                (clone/'other-user.md').write_text('remote advanced during checkpoint\n')
                other('add','other-user.md');other('commit','-m','QA racing remote update');other('push','origin','codex/QA')
                remote_after.append(self.remote_head())
            return result
        with patch.object(self.m,'_git',side_effect=scheduled_git):
            with self.assertRaisesRegex(MaintenanceBlocked,'auth/conflict'):self.checkpoint(plan,push=True)
        self.assertEqual(len(remote_after),1)
        self.assertEqual(self.remote_head(),remote_after[0]);self.assertNotEqual(self.git('rev-parse','HEAD'),self.baseline)
        records=[json.loads(path.read_text()) for path in (self.system/'.state/maintenance').glob('*.json')]
        self.assertTrue(any(x.get('kind')=='git_result' and x.get('commit')==self.git('rev-parse','HEAD') and x.get('pushed') is False for x in records))

    def test_ignored_binary_runtime_and_auth_paths_denied_even_broad_grant(self):
        broad=Grants(self.system).grant('maintenance',source='TEST broad path does not remove data restrictions',paths=['**'],operations=['git'])['id']
        self.m.authorize_git(grant=broad,branch='codex/QA',source='TEST same branch and origin')
        for path,data in [('ignored.txt',b'ignored'),('sys/runs/A/state.json',b'{}'),('sys/.gflow/profile.json',b'{}'),('sys/models/model.onnx',b'model'),('sys/test.bin',b'\0binary')]:
            file=self.project/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
            with self.assertRaises(MaintenanceBlocked,msg=path):self.m.git_plan(branch='codex/QA',paths=[path],grant=broad)


if __name__=='__main__':unittest.main()
