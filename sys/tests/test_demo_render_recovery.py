"""Two-core rendering and exact failed-request reconciliation regression checks."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from colab_bridge.client import Client, ColabError


class DemoRenderRecoveryTests(unittest.TestCase):
    def test_requested_parallelism_is_bounded_by_runtime_cores(self):
        root = Path(__file__).resolve().parents[1]
        code = "import {renderConcurrency as r} from './renderer/outputs.mjs'; console.log(JSON.stringify([r(4,2),r(1,8),r(undefined,2),r(4,0)]));"
        got = subprocess.check_output(['node', '--input-type=module', '-e', code], cwd=root, text=True)
        self.assertEqual(json.loads(got), [2, 1, 2, 1])

    def test_unknown_live_or_completed_render_cannot_be_marked_failed(self):
        for change in ({'exact_failed_exit': False}, {'archive_exists': True}, {'mp4_exists': True}, {'active_renderers': ['123']}, {'returncode': 0}):
            with self.subTest(change=change):
                self._case(change, accepted=False)

    def test_verified_failed_exit_retains_owner_and_previous_state(self):
        self._case({}, accepted=True)

    def _case(self, change, accepted):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); cache = root / 'cache'; request_id = 'a' * 64
            folder = cache / request_id; folder.mkdir(parents=True)
            saved = {'phase': 'ambiguous', 'request_id': request_id, 'account': None,
                     'session': 'original-session', 'remote': '/content/video-pilot-jobs/' + request_id}
            state = folder / 'state.json'; state.write_text(json.dumps(saved))
            client = Client.__new__(Client); client.account = 'different-default'; client.session = 'different-session'
            observed = {'exact_failed_exit': True, 'returncode': 1, 'archive_exists': False,
                        'mp4_exists': False, 'active_renderers': [], **change}
            with patch.object(client, 'ensure_authenticated'), patch.object(client, 'exec', return_value='VP_FAILED_RENDER=' + json.dumps(observed)), patch.object(client, '_settle') as settle:
                if accepted:
                    result = client.reconcile_render_failure({'operation': 'render', 'request_id': request_id}, cache, 'Actual authorized recovery')
                    self.assertEqual(result['session'], 'original-session')
                    self.assertEqual(json.loads(state.read_text())['phase'], 'failed')
                    self.assertEqual(json.loads(Path(result['evidence']).read_text())['previous_state'], saved)
                    settle.assert_called_once_with(request_id)
                else:
                    with self.assertRaises(ColabError):
                        client.reconcile_render_failure({'operation': 'render', 'request_id': request_id}, cache, 'Actual authorized recovery')
                    self.assertEqual(json.loads(state.read_text()), saved)
                    settle.assert_not_called()
