import tempfile
import unittest
from unittest.mock import patch
from podcast.account import invoke_saved, AccountCallPending

SCHEMA = {'type': 'object', 'properties': {'answer': {'type': 'string'}}, 'required': ['answer']}

class AccountRecoveryTests(unittest.TestCase):
    def test_response_reused_and_changed_prompt_rejected(self):
        with tempfile.TemporaryDirectory() as root, patch('scripts.agy_pipeline.invoke', return_value={
                'structured_output': {'answer': 'saved'}}) as invoke:
            self.assertEqual(invoke_saved('one', SCHEMA, root), invoke_saved('one', SCHEMA, root))
            self.assertEqual(invoke.call_count, 1)
            with self.assertRaises(AccountCallPending):
                invoke_saved('different', SCHEMA, root)
            self.assertEqual(invoke.call_count, 1)

    def test_timeout_stays_pending_without_second_request(self):
        with tempfile.TemporaryDirectory() as root, patch('scripts.agy_pipeline.invoke', side_effect=TimeoutError) as invoke:
            with self.assertRaises(TimeoutError):
                invoke_saved('one', SCHEMA, root)
            with self.assertRaises(AccountCallPending):
                invoke_saved('one', SCHEMA, root)
            self.assertEqual(invoke.call_count, 1)
