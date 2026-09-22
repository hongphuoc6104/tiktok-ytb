"""Integration contracts for stable media, publication and isolated rehearsal."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import adapters
import b2_bridge
from pilot import Pilot, ROOT, Blocked
from scripts import clean_production as cleanup
from scripts.rehearse_content import build_sandbox

class RedesignTests(unittest.TestCase):
    def test_single_image_keeps_journal_path_and_one_candidate_on_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'config.json').write_text(json.dumps({'flow_require_ui_evidence': False}))
            out=root/'attempt/download';out.mkdir(parents=True)
            artifact=out/'stable-id.jpg';Image.new('RGB',(160,90)).save(artifact)
            p=SimpleNamespace(root=root)
            args=('image','--id','test','--prompt','scene','--ratio','16:9','--character','CH01','--out',str(out))
            with patch.object(b2_bridge,'generate_b2_image',return_value={'path':str(artifact),'forge_id':'media-id'}):
                for _ in range(2):
                    adapters.gflow(p,*args)
                    self.assertTrue(artifact.is_file())
                    self.assertEqual(list(out.glob('*.jpg')),[artifact])
                    self.assertEqual(json.loads(artifact.with_suffix('.json').read_text())['forgeId'],'media-id')

    def test_integrity_covers_provider_policy_not_ledger(self):
        p=object.__new__(Pilot);p.root=ROOT
        protected=p.protected()
        for name in ('b2_bridge.py','experiments/b2_illustrator/queue-runner.mjs','experiments/b2_illustrator/session.mjs','vocab/policy.py','vocab/bank.py'):
            self.assertIn(name,protected)
        self.assertNotIn('vocab/ledger.json',protected)
        self.assertNotIn('vocab/bank.jsonl',protected)
        self.assertNotIn('experiments/b2_illustrator/machine.local.json',protected)

    def test_sandbox_has_policy_but_no_production_reservations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=build_sandbox(Path(tmp)/'sandbox')
            self.assertTrue((root/'b2_bridge.py').is_file())
            self.assertTrue((root/'experiments/b2_illustrator/queue-runner.mjs').is_file())
            self.assertFalse((root/'experiments/b2_illustrator/machine.local.json').exists())
            self.assertTrue((root/'vocab/policy.py').is_file())
            self.assertTrue((root/'vocab/bank.jsonl').is_file())
            self.assertEqual(json.loads((root/'vocab/ledger.json').read_text()),{'entries':{}})

    def test_cache_cleanup_preserves_browser_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);model=root/'profiles/Default/OptGuideOnDeviceModel/data'
            model.parent.mkdir(parents=True);model.write_bytes(b'keep')
            with patch.object(cleanup,'GFLOW_DIR',root):
                self.assertEqual(cleanup.clean_system_and_browser_cache(False),0)
            self.assertEqual(model.read_bytes(),b'keep')

    def test_legacy_renderer_stops_before_synthesis(self):
        from scripts import rerender_16x9
        with patch.object(rerender_16x9,'synthesize_vieneu') as synth:
            with self.assertRaisesRegex(SystemExit,'LEGACY_RENDER_DISABLED'):
                rerender_16x9.main()
            synth.assert_not_called()

    def test_cleanup_validation_reads_sqlite_without_writes(self):
        import sqlite3
        import workflow
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'runs/demo').mkdir(parents=True)
            db=root/'jobs.sqlite'
            conn=sqlite3.connect(db);conn.execute('create table sentinel (value text)');conn.close()
            before=db.read_bytes()
            video=root/'video/demo/demo_r2_9x16.mp4';video.parent.mkdir(parents=True);video.write_bytes(b'fixture')
            def published(p,job):
                with self.assertRaises(sqlite3.OperationalError):
                    p.db.execute("insert into sentinel values ('forbidden')")
                return [str(video)]
            with patch.object(cleanup,'ROOT',root),patch.object(cleanup,'RUNS_DIR',root/'runs'),patch.object(cleanup,'DB_PATH',db),patch.object(workflow,'published_videos',side_effect=published),patch.object(workflow,'current',return_value={'revision':2}),patch.object(cleanup,'validate_video_integrity',return_value=(True,'ok')):
                valid,_,paths,rev=cleanup.validate_job_deliverables('demo')
            self.assertTrue(valid);self.assertEqual(paths,[video]);self.assertEqual(rev,2)
            self.assertEqual(before,db.read_bytes())

    def test_sandbox_policy_uses_its_own_reservation(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=build_sandbox(Path(tmp)/'sandbox')
            original=(ROOT/'vocab/ledger.json').read_bytes()
            code="""
from pathlib import Path
from vocab import bank, policy
entry=bank.bank()[0]['id']
bank.save_ledger({'entries':{entry:{'job':'isolated-test','status':'reserved'}}})
brief={'planning':{'domain_requirements':[bank.ENTRY_TAG+entry]}}
policy.check(Path.cwd(),'isolated-test',brief)
try:
    policy.check(Path.cwd(),'other-job',brief)
except Exception:
    pass
else:
    raise AssertionError('Reservation ownership must be checked')
assert Path(bank.__file__).resolve().parent == Path.cwd()/'vocab'
"""
            subprocess.run([sys.executable,'-c',code],cwd=root,check=True,capture_output=True,text=True)
            self.assertEqual((ROOT/'vocab/ledger.json').read_bytes(),original)
