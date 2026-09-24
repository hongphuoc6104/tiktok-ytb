"""Provider boundaries use durable states, never infer a safe retry from a crash."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import adapters
import b2_bridge
from pilot import Blocked, read, write


class QueueRecoveryTests(unittest.TestCase):
    def test_partial_batch_preserves_known_results_and_unattempted_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'out';spec=root/'jobs.json'
            jobs=[{'id':f'image-{i}','prompt':'TEST','ratio':'9:16'} for i in range(5)]
            write(spec,{'jobs':jobs})
            error=Blocked('TEST interrupted batch')
            error.attempt_states=[{'request_id':'image-0','state':'collected'},
                                  {'request_id':'image-1','state':'generated'},
                                  {'request_id':'image-2','state':'unknown'},
                                  {'request_id':'image-3','state':'prepared'}]
            with patch('b2_bridge.generate_b2_batch',side_effect=error) as provider:
                with self.assertRaises(Blocked):
                    adapters.gflow(SimpleNamespace(root=root),'batch',str(spec),'--out',str(out))
            self.assertEqual(provider.call_count,1)
            entries=read(out/'gflow-run.json')['jobs']
            self.assertTrue(entries[0]['collection_only'])
            self.assertTrue(entries[1]['collection_only'])
            self.assertEqual(entries[2]['status'],'failed')
            self.assertEqual(entries[3]['status'],'not_submitted')
            self.assertEqual(entries[4]['status'],'not_submitted')

    def test_bridge_preserves_exact_prompt_in_collection_only_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('b2_bridge.require_queue_acceptance'),patch('b2_bridge.ensure_connected'),patch('b2_bridge.generate_b2_batch',return_value=[{'test_only':True}]) as provider:
                b2_bridge.generate_b2_image('Approved prompt with exact learner text.',out_dir=tmp,
                                           char_ref_path=Path(tmp)/'reference.png',char_media_id='TEST',
                                           collection_only=True)
            request=provider.call_args.args[0][0]
            self.assertEqual(request['prompt'],'Approved prompt with exact learner text.')
            self.assertTrue(request['collectionOnly'])


if __name__=='__main__':unittest.main()
