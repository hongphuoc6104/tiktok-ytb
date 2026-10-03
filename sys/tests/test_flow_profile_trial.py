"""Full default trial→B2 bridge→send-boundary flow with controlled socket peer.

No browser/service calls: the sole transport replacement is the final socket
peer. This tests the public bridge path, rather than injecting a generate stub.
"""
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import b2_bridge
from account_catalog import discover
from flow_profile_trial import Trials, TrialBlocked, metadata_plan
from permissions import Grants
from pilot import ROOT, Blocked
from profile_setup import inventory

URL='https://flow.google.com/project/46e4b782-6bf6-40c1-b484-c17fe6c0a936/tool/f9458f79-f068-476c-848d-c407cfa9fbc1'
MEDIA='de94a39b-155f-4afe-acbb-d9d4b59ad532'


class FlowProfileTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name);self.root=self.home/'project/sys';self.root.mkdir(parents=True)
        ordinary=self.home/'.config/google-chrome'
        managed=self.home/'.config/google-chrome-cdp-profile4'
        for root in (ordinary,managed):
            (root/'Profile 4').mkdir(parents=True)
            (root/'Local State').write_text(json.dumps({'profile':{'info_cache':{'Profile 4':{'name':'Test'}}}}))
        self.source=next(x['id'] for x in inventory(self.root,self.home) if x['browser']=='Chrome')
        self.runtime=next(x['id'] for x in inventory(self.root,self.home) if x['browser']=='Chrome managed')
        shutil.copytree(ROOT/'assets/characters/channel-mascot',self.root/'assets/characters/channel-mascot')
        folder=self.root/'experiments/b2_illustrator';folder.mkdir(parents=True)
        (folder/'acceptance.json').write_text('{"production_ready":false}')
        (self.root/'config.json').write_text('{"flow_queue_trial_enabled":true,"flow_status_retries":0}')
        grant=Grants(self.root).grant('development',source='Synthetic isolated one-image trial authorization',
            paths=['experiments/b2_illustrator/results/profile-trials'])['id']
        self.trials=Trials(self.root,'isolated-trial',home=self.home,budget_store=self.home/'budget')
        sha=hashlib.sha256((self.root/'assets/characters/channel-mascot/reference-v1.png').read_bytes()).hexdigest()
        self.profile_path=str(managed/'Profile 4')
        self.record=self.trials.prepare(self.source,self.runtime,tool_url=URL,project='Test project',model='Nano Banana 2 Lite',
            session='test-session',grant=grant,source='Synthetic isolated one-image trial authorization',reference_media_id=MEDIA,
            reference_evidence={'account':self.runtime,'profile_path':self.profile_path,'media_id':MEDIA,'sha256':sha,
                                'ui_verified_source':'Synthetic isolated attachment evidence'})
        self.connection={'status':'connected','identity':{'observedProfile':self.profile_path,'toolUrl':URL}}
        self.calls=[];self.error=None;self.boundary_connection=None
        self.status_count=0;self.drift_after=None

    def peer(self,command,timeout=120):
        self.calls.append(command)
        if command=='status':
            self.status_count+=1
            if self.drift_after and self.status_count>=self.drift_after:
                return {'status':'connected','identity':{'observedProfile':'/unexpected/profile','toolUrl':URL}}
            return self.connection
        if command.startswith('tool-snapshot:queue:'):
            entries=json.loads(Path(command.split(':',2)[2]).read_text())
            # Exactly one charged request exists when the peer receives send.
            state=self.trials.budget.snapshot(self.runtime)
            self.assertEqual(state['flow']['isolated-trial']['slots'],1)
            self.assertEqual(self.trials.read()['profiles'][self.source]['state'],'submitted')
            if self.error:raise self.error
            results=[]
            for item in entries:
                path=Path(item['outDir'])/'result.png';path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(self.root/'assets/characters/channel-mascot/reference-v1.png',path)
                results.append({'request_id':item['testCase'],'path':str(path),'forgeId':MEDIA})
            return {'status':'completed','items':results}
        raise AssertionError('Unexpected socket command: '+command)

    def context(self):
        stack=ExitStack()
        stack.enter_context(patch('b2_bridge.ROOT',self.root))
        stack.enter_context(patch('b2_bridge.send_raw_command',side_effect=self.peer))
        stack.enter_context(patch('account_catalog.probe_flow',return_value={
            'auth':'verified','identity':'synthetic-stable-google','identity_source':'synthetic isolated Flow account UI'}))
        stack.enter_context(patch('flow_profile_trial.processes',return_value=[{'pid':123,'localhost':True,'cdp_ephemeral':True}]))
        return stack

    def test_default_bridge_preflight_does_not_charge_and_final_send_charges_once(self):
        with self.context():
            result=self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
            again=self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
        self.assertEqual(result['path'],again['path'])
        self.assertEqual(sum(x.startswith('tool-snapshot:queue:') for x in self.calls),1)
        self.assertEqual(self.trials.read()['profiles'][self.source]['state'],'downloaded')
        self.assertEqual(self.trials.budget.snapshot(self.runtime)['flow']['isolated-trial']['slots'],1)

    def test_preflight_profile_mismatch_never_charges_or_sends(self):
        self.connection['identity']['observedProfile']='/different/profile'
        with self.context(),self.assertRaisesRegex(TrialBlocked,'profile/tool'):
            self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
        self.assertFalse(any(x.startswith('tool-snapshot:queue:') for x in self.calls))
        self.assertEqual(self.trials.budget.snapshot(self.runtime)['flow'],{})
        self.assertEqual(self.trials.read()['profiles'][self.source]['state'],'not_submitted')

    def test_unknown_sent_outcome_is_kept_and_never_resubmitted(self):
        self.error=Blocked('Synthetic socket timeout after send')
        with self.context():
            with self.assertRaisesRegex(Blocked,'timeout'):
                self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
            with self.assertRaisesRegex(TrialBlocked,'Already attempted'):
                self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
        self.assertEqual(sum(x.startswith('tool-snapshot:queue:') for x in self.calls),1)
        self.assertEqual(self.trials.read()['profiles'][self.source]['state'],'unknown')
        self.assertEqual(self.trials.budget.snapshot(self.runtime)['flow']['isolated-trial']['slots'],1)

    def test_profile_changes_after_preflight_final_guard_rejects_without_charge(self):
        # First status is the read-only preflight; bridge preparation can take
        # time, so its final observed connection must be checked independently.
        self.drift_after=3
        with self.context(),self.assertRaisesRegex(TrialBlocked,'profile/tool'):
            self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
        self.assertGreaterEqual(self.status_count,3)
        self.assertFalse(any(x.startswith('tool-snapshot:queue:') for x in self.calls))
        self.assertEqual(self.trials.budget.snapshot(self.runtime)['flow'],{})
        self.assertEqual(self.trials.read()['profiles'][self.source]['state'],'not_submitted')

    def test_provider_quota_stops_whole_trial_pool(self):
        self.error=Blocked('Synthetic provider quota exceeded')
        with self.context(),self.assertRaisesRegex(Blocked,'quota'):
            self.trials.submit(self.source,handoff_source='Synthetic isolated serial handoff')
        self.assertEqual(self.trials.read()['blocked']['kind'],'quota')
        with self.context(),self.assertRaisesRegex(TrialBlocked,'Pool service block'):
            self.trials.submit(self.source,handoff_source='Synthetic isolated next account request')
        self.assertEqual(sum(x.startswith('tool-snapshot:queue:') for x in self.calls),1)

    def test_metadata_plan_does_not_promote_flow_auth(self):
        value=metadata_plan(self.root,home=self.home)
        self.assertTrue(value['metadata_only']);self.assertFalse(value['provider_called'])
        self.assertEqual(len(value['profiles']),1)
        row=value['profiles'][0]
        self.assertEqual(row['flow_auth'],'not_tested_for_this_trial')
        self.assertEqual(row['maximum_images'],1)
        self.assertEqual(row['managed_candidates'][0]['runtime_account'],self.runtime)


if __name__=='__main__':unittest.main()
