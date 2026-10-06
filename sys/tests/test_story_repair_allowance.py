"""A repair allowance retains consumed slots and cannot evade provider blocks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from account_budget import Budgets


class StoryRepairAllowanceTests(unittest.TestCase):
    def test_one_extra_slot_preserves_usage_and_stops_at_new_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Budgets(tmp);b.bind_identity('browser-test','identity-test','fixture mapping')
            b.flow_submit('browser-test','session','old',100,evidence='fixture initial slots',budget_session='session')
            with patch('permissions.Grants.require',return_value={'id':'scoped-grant'}):
                b.allow_flow_repair('browser-test','session',extra_slots=1,system_root=tmp,grant='scoped-grant',job='story',source='User authorized whole demo',evidence='Existing image fails the authored scene')
            b.flow_submit('browser-test','session','repair',1,evidence='fixture repair',budget_session='session')
            self.assertEqual(b.snapshot('browser-test')['flow']['session']['slots'],101)
            with self.assertRaises(ValueError):
                b.flow_submit('browser-test','session','too-many',1,evidence='fixture excess',budget_session='session')
            with patch('permissions.Grants.require',return_value={'id':'scoped-grant'}):
                with self.assertRaises(ValueError):
                    b.allow_flow_repair('browser-test','session',extra_slots=1,system_root=tmp,grant='scoped-grant',job='story',source='same job',evidence='Existing image fails the authored scene')

    def test_provider_block_cannot_be_relaxed(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Budgets(tmp);b.bind_identity('browser-test','identity-test','fixture mapping')
            b.flow_submit('browser-test','session','old',100,evidence='fixture',budget_session='session')
            with self.assertRaises(ValueError):
                b.recover('browser-test','flow','episode',action='reconcile',error='quota',submit_state='unknown',evidence='fixture provider quota')
            with patch('permissions.Grants.require',return_value={'id':'scoped-grant'}):
                with self.assertRaisesRegex(ValueError,'blocked'):
                    b.allow_flow_repair('browser-test','session',extra_slots=1,system_root=tmp,grant='scoped-grant',job='story',source='authorized demo',evidence='failed picture')
