import tempfile
import unittest
from pathlib import Path
from adapters import copy_optional_flow_screenshot
from pilot import Blocked

class OptionalScreenshotTests(unittest.TestCase):
 def test_missing_optional_source_creates_no_fake_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/'before-submit.png'
   for source in [None, str(Path(d)/'preflight.png')]:
    copy_optional_flow_screenshot(source,dest,required=False)
    self.assertFalse(dest.exists())
 def test_required_missing_source_does_not_accept_stale_destination(self):
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/'before-submit.png';dest.write_bytes(b'old')
   with self.assertRaises(Blocked):
    copy_optional_flow_screenshot(None,dest,required=True)
 def test_real_source_copy_and_same_path(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'real.png';dest=Path(d)/'before-submit.png';src.write_bytes(b'real screenshot bytes')
   copy_optional_flow_screenshot(src,dest,required=True)
   self.assertEqual(src.read_bytes(),dest.read_bytes())
   copy_optional_flow_screenshot(dest,dest,required=True)
