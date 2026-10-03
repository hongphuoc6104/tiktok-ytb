"""Modern registration and submission safety without a provider or quality reviewer."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot import Blocked, read, write, digest
import image_pipeline as images


class ModernImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = self.root / 'runs/test'; self.job.mkdir(parents=True)
        self.p = SimpleNamespace(root=self.root, job=lambda j:self.job,
                                 path=lambda j,name:self.job/name)

    def test_registration_auto_records_technical_identity_without_reviewer_claim(self):
        folder=self.job/'flow/attempts/one';folder.mkdir(parents=True)
        artifact=folder/'result.png';artifact.write_bytes(b'fixture-result')
        journal=folder/'request.json';write(journal,{'state':'downloaded'})
        result={'key':'one','path':str(artifact.relative_to(self.job)),
                'journal':str(journal.relative_to(self.job)),'sha256':digest(artifact)}
        ref={'character_id':'CH01','sha256':'ref-sha','name':'canonical','prompt':'fixture','path':'reference.png'}
        with (patch('image_pipeline.request',return_value=result),
              patch('workflow.settings',return_value={'version':4,'mode':'auto'}),
              patch('execution.is_job',return_value=True),
              patch('image_pipeline.requires_ui_evidence',return_value=False),
              patch('machine_review.review',side_effect=AssertionError('Reviewer forbidden'))):
            write(self.job/'workflow.json',{'version':4})
            registered=images.register(self.p,'test',ref)
        confirmation=read(self.job/registered['confirmation'])
        self.assertTrue(confirmation['technical_registration'])
        self.assertFalse(confirmation['matches_approved_reference'])
        self.assertIsNone(confirmation['report'])

    def test_stop_at_submit_boundary_is_known_not_submitted(self):
        error=Blocked('STOP_REQUESTED')
        with patch('execution.is_job',return_value=True),patch('execution.before_submit',side_effect=error):
            with self.assertRaises(Blocked) as raised:
                images._before_generation(self.p,'test')
        self.assertIs(raised.exception.generation_submitted,False)

    def test_modern_prompt_accepts_expression_without_changing_legacy_identity(self):
        content={'schema_version':'3.0','characters':[{'id':'CH01','name':'mascot'}],'scenes':[]}
        units=[{'id':'one','character_ids':['CH01']}]
        with patch('image_pipeline.content',return_value=content),patch('image_pipeline.planned_units',return_value=units):
            with patch('execution.is_job',return_value=True):
                modern=images.requested_prompt(self.p,'test','one','A small mascot explains.','','9:16')
            with patch('execution.is_job',return_value=False):
                legacy=images.requested_prompt(self.p,'test','one','A small mascot explains.','','9:16')
        self.assertIn('Subtle eyebrows',modern)
        self.assertNotIn('do not add eyebrows',modern)
        self.assertNotIn('do not add eyebrows',legacy)
        self.assertIn('do not add teeth',legacy)

    def test_technical_registration_not_accepted_as_legacy_quality_review(self):
        evidence={'technical_registration':True,'observer':'technical'}
        with patch('execution.is_job',return_value=True):
            self.assertTrue(images.registration_accepted(self.p,'test',evidence))
        with patch('execution.is_job',return_value=False):
            self.assertFalse(images.registration_accepted(self.p,'test',evidence))
