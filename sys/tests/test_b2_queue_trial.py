import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import b2_bridge
from pilot import Blocked

class QueueTrialGate(unittest.TestCase):
    def test_trial_permission_is_separate_from_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = root / 'experiments/b2_illustrator/acceptance.json'
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({'production_ready': False}))
            with patch.object(b2_bridge, 'ROOT', root):
                for enabled in (False, True):
                    (root / 'config.json').write_text(json.dumps({'flow_queue_trial_enabled': enabled}))
                    if enabled:
                        b2_bridge.require_queue_acceptance()
                    else:
                        with self.assertRaises(Blocked):
                            b2_bridge.require_queue_acceptance()
                self.assertFalse(json.loads(record.read_text())['production_ready'])
