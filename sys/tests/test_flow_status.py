"""B-2 status probe timing/backoff and pre- vs post-submission classification.

Regression coverage for the ambiguous-loop bug: a read-only 'status' probe
(or any other check that runs strictly before the socket command that can
reach Flow's queue) must never be reported as an unresolved/ambiguous
submission just because it timed out or failed locally. Only a failure
that happens after generate_b2_batch actually sends 'tool-snapshot:queue:...'
may fall back to the default ambiguous classification.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import b2_bridge
from pilot import Blocked


class QueryStatusRetryTests(unittest.TestCase):
    """query_status() must retry a transient failure with backoff and use
    the configured timeout, since session.mjs answers 'status' immediately
    but the daemon itself can still be cold-starting."""

    def _root_with_config(self, tmp, **config):
        root = Path(tmp)
        (root / 'config.json').write_text(json.dumps(config))
        return root

    def test_retries_transient_failure_then_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root_with_config(tmp, flow_status_retries=2, flow_status_backoff_seconds=0)
            with patch.object(b2_bridge, 'ROOT', root), \
                 patch('b2_bridge.time.sleep') as sleep, \
                 patch('b2_bridge.send_raw_command',
                       side_effect=[Blocked('cold start'), Blocked('still cold'), {'status': 'connected'}]) as send:
                result = b2_bridge.query_status()
        self.assertEqual(result, {'status': 'connected'})
        self.assertEqual(send.call_count, 3)
        self.assertEqual(sleep.call_count, 2)  # backoff between attempts, not after the final success

    def test_exhausts_retries_and_raises_last_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root_with_config(tmp, flow_status_retries=1, flow_status_backoff_seconds=0)
            with patch.object(b2_bridge, 'ROOT', root), patch('b2_bridge.time.sleep'), \
                 patch('b2_bridge.send_raw_command', side_effect=[Blocked('first'), Blocked('final')]) as send:
                with self.assertRaises(Blocked) as ctx:
                    b2_bridge.query_status()
        self.assertIn('final', str(ctx.exception))
        self.assertEqual(send.call_count, 2)

    def test_uses_configured_timeout_default_and_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root_with_config(tmp)
            with patch.object(b2_bridge, 'ROOT', root), \
                 patch('b2_bridge.send_raw_command', return_value={'status': 'connected'}) as send:
                b2_bridge.query_status()
        self.assertEqual(send.call_args.kwargs.get('timeout'), 30.0)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._root_with_config(tmp, flow_status_timeout_seconds=12.5)
            with patch.object(b2_bridge, 'ROOT', root), \
                 patch('b2_bridge.send_raw_command', return_value={'status': 'connected'}) as send:
                b2_bridge.query_status()
        self.assertEqual(send.call_args.kwargs.get('timeout'), 12.5)


class PreSubmitClassificationTests(unittest.TestCase):
    """Anything that fails before generate_b2_batch's own socket submission
    call must be tagged generation_submitted=False (a clean, retryable
    failure) -- never the default 'ambiguous' that forces a manual
    flow-reconcile."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'config.json').write_text(json.dumps({'flow_status_retries': 0}))
        self.addCleanup(self.tmp.cleanup)
        self.root_patch = patch.object(b2_bridge, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        # Bypass the acceptance-gate file requirements; not what this class tests.
        self.accept_patch = patch.object(b2_bridge, 'require_queue_acceptance', lambda: None)
        self.accept_patch.start()
        self.addCleanup(self.accept_patch.stop)

    def test_status_timeout_during_connect_is_not_ambiguous(self):
        with patch('b2_bridge.send_raw_command', side_effect=Blocked('timed out after 5.0s: status')) as send:
            with self.assertRaises(Blocked) as ctx:
                b2_bridge.generate_b2_batch([{'testCase': 'X', 'prompt': 'p', 'ratio': '16:9'}])
        self.assertIs(ctx.exception.generation_submitted, False)
        # Only the pre-submit 'status' probe was ever attempted; the queue
        # command that would actually reach Flow was never sent.
        for call in send.call_args_list:
            self.assertNotIn('tool-snapshot:queue:', call.args[0])

    def test_reference_media_id_required_is_caught_before_submission(self):
        with patch.object(b2_bridge, 'ensure_connected', return_value={'status': 'connected'}), \
             patch('b2_bridge.send_raw_command') as send:
            with self.assertRaises(Blocked) as ctx:
                b2_bridge.generate_b2_batch([{
                    'testCase': 'X', 'prompt': 'p', 'ratio': '16:9',
                    'characterRefPath': '/tmp/does-not-matter.png', 'charMediaId': None,
                }])
        self.assertIn('REFERENCE_MEDIA_ID_REQUIRED', str(ctx.exception))
        self.assertIs(ctx.exception.generation_submitted, False)
        send.assert_not_called()

    def test_missing_base_media_id_is_also_caught_before_submission(self):
        with patch.object(b2_bridge, 'ensure_connected', return_value={'status': 'connected'}), \
             patch('b2_bridge.send_raw_command') as send:
            with self.assertRaises(Blocked) as ctx:
                b2_bridge.generate_b2_batch([{
                    'testCase': 'X', 'prompt': 'p', 'ratio': '16:9',
                    'characterRefPath': '/tmp/mascot.png', 'charMediaId': 'known-id',
                    'baseRefPath': '/tmp/base.jpg', 'baseMediaId': None,
                }])
        self.assertIn('REFERENCE_MEDIA_ID_REQUIRED', str(ctx.exception))
        self.assertIs(ctx.exception.generation_submitted, False)
        send.assert_not_called()

    def test_batch_size_violation_is_pre_submit_clean_failure(self):
        with patch.object(b2_bridge, 'ensure_connected', return_value={'status': 'connected'}), \
             patch('b2_bridge.send_raw_command') as send:
            with self.assertRaises(Blocked) as ctx:
                b2_bridge.generate_b2_batch([])
        self.assertIs(ctx.exception.generation_submitted, False)
        send.assert_not_called()

    def test_post_submission_timeout_keeps_default_ambiguous_classification(self):
        """The safety rule must survive: once the real queue command is sent,
        an unknown outcome stays ambiguous (no generation_submitted=False)
        so nothing can silently resubmit against Flow."""
        def fake_send(command, timeout=120.0):
            if command == 'status':
                return {'status': 'connected'}
            raise Blocked('socket timeout mid-submission')
        with patch.object(b2_bridge, 'ensure_connected', return_value={'status': 'connected'}), \
             patch('b2_bridge.send_raw_command', side_effect=fake_send):
            with self.assertRaises(Blocked) as ctx:
                b2_bridge.generate_b2_batch([{
                    'testCase': 'X', 'prompt': 'p', 'ratio': '16:9',
                    'characterRefPath': '/tmp/mascot.png', 'charMediaId': 'known-id',
                }])
        self.assertIsNone(getattr(ctx.exception, 'generation_submitted', None))


if __name__ == '__main__':
    unittest.main()
