"""Downloaded-media binding regressions; no provider or browser invocation."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from pilot import Blocked, digest, write
from adapters import _flow_media_reference


class FlowReferenceBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = self.root / 'runs/trial'
        self.folder = self.job / 'flow/attempts/reference'
        self.folder.mkdir(parents=True)
        self.asset = self.folder / 'reference.jpg'
        self.asset.write_bytes(b'fixture-downloaded-media')
        self.p = SimpleNamespace(job=lambda _: self.job, path=lambda _, name: self.job / name)
        self.record = {'state': 'downloaded', 'sha256': digest(self.asset),
                       'path': str(self.asset.relative_to(self.job)), 'identity': {'target':'ref:CH01'}}
        write(self.folder / 'request.json', self.record)
        write(self.asset.with_suffix('.json'), {'source':'google-flow-browser', 'status':'downloaded', 'forgeId':'real-fixture-media'})

    def test_copied_registration_input_resolves_by_bytes_to_real_media_id(self):
        copied = self.job / 'reference-copy.jpg'
        copied.write_bytes(self.asset.read_bytes())
        self.assertEqual(_flow_media_reference(self.p, 'trial', image=copied), (str(self.asset), 'real-fixture-media'))

    def test_named_scene_reference_uses_registered_download(self):
        self.record['identity']['registration'] = {'name':'canonical-fixture'}
        write(self.folder / 'request.json', self.record)
        self.assertEqual(_flow_media_reference(self.p, 'trial', name='canonical-fixture'), (str(self.asset), 'real-fixture-media'))
        with self.assertRaises(Blocked): _flow_media_reference(self.p, 'trial', name='another-character')

    def test_changed_bytes_or_missing_provider_id_never_invent_a_reference(self):
        self.asset.write_bytes(b'changed')
        with self.assertRaises(Blocked) as caught: _flow_media_reference(self.p, 'trial', image=self.asset)
        self.assertFalse(caught.exception.generation_submitted)
        self.record['sha256'] = digest(self.asset)
        write(self.folder / 'request.json', self.record)
        write(self.asset.with_suffix('.json'), {'source':'google-flow-browser', 'status':'downloaded'})
        with self.assertRaises(Blocked): _flow_media_reference(self.p, 'trial', image=self.asset)
