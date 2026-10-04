"""Isolated synthetic fixtures: protocol, transport recovery and parallel media."""
import copy
import json
import re
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch
import wave
import zipfile

from pilot import ROOT, Blocked, read, write
from colab_bridge.protocol import build_request, validate_result, file_hash
from colab_bridge.client import Client, ColabError
import workflow
import test_workflow as fixtures


def fake_result(folder, req):
    folder.mkdir(parents=True, exist_ok=True)
    segments = []
    for n, segment in enumerate(req['segments']):
        name = f'segment-{n}.wav'
        with wave.open(str(folder / name), 'wb') as w:
            w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            w.writeframes(b'\x00\x20' * 4800 + b'\0\0' * round(segment['pause'] * 48000))
        segments.append(dict(scene_id=segment['scene_id'], text=segment['text'], path=name, content_duration=.1))
    write(folder / 'tts-result.json', dict(request_id=req['request_id'], voice='Minh Quân Pro', segments=segments, engine={'backend':'colab-omnivoice','models':req['models'],'device':'Tesla T4'}))


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cfg = read(ROOT / 'config.json')
        # This transport fixture retains the historical bilingual Alba 1.0
        # contract. New channel defaults are exercised in test_selected_voice.
        self.cfg.update(en_voice='alba', en_speed=1.)
        self.cfg['colab_tts']['voices']['en'] = 'assets/voices/alba/profile.json'
        shutil.copytree(ROOT / 'assets/voices', self.root / 'assets/voices')
        self.scenes = [dict(scene_id='SC01', narration='Từ weather. I am happy.',
                           texts=['Từ weather.', 'I am happy.'],
                           parts=[[dict(lang='vi', text='Từ'), dict(lang='en', text='weather.')],
                                  [dict(lang='en', text='I am happy.')]],
                           retake=0, gaps=[.5], tail=2.)]
        self.req = build_request(self.root, self.cfg, self.scenes)

    def test_language_voice_speed_pause_and_text_preserved(self):
        self.assertEqual([x['language'] for x in self.req['items']], ['vi', 'en', 'en'])
        self.assertEqual([x['speed'] for x in self.req['items']], [.92, 1., 1.])
        self.assertEqual(self.req['profiles']['vi']['voice'], 'Minh Quân Pro')
        self.assertEqual(self.req['profiles']['en']['voice'], 'alba')
        self.assertEqual(self.req['segments'][-1]['pause'], 2.)
        self.assertEqual(self.req['items'][-1]['text'], 'I am happy.')

    def test_cache_changes_for_retake_and_model_but_not_local_path(self):
        changed = copy.deepcopy(self.scenes)
        changed[0]['retake'] = 1
        self.assertNotEqual(self.req['request_id'], build_request(self.root, self.cfg, changed)['request_id'])
        changed_cfg = copy.deepcopy(self.cfg)
        changed_cfg['colab_tts']['models']['vi']['revision'] = 'a' * 40
        self.assertNotEqual(self.req['request_id'], build_request(self.root, changed_cfg, self.scenes)['request_id'])
        other = self.root / 'other'
        shutil.copytree(self.root / 'assets', other / 'assets')
        self.assertEqual(self.req['request_id'], build_request(other, self.cfg, self.scenes)['request_id'])

    def test_changed_voice_reference_rejected(self):
        (self.root / 'assets/voices/alba/reference.wav').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            build_request(self.root, self.cfg, self.scenes)

    def test_waveform_and_pause_checked_before_import(self):
        folder = self.root / 'result'
        fake_result(folder, self.req)
        self.assertEqual(len(validate_result(folder, self.req)), 3)
        p = folder / 'segment-1.wav'
        data = bytearray(p.read_bytes()); data[-1] = 1; p.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'not silent'):
            validate_result(folder, self.req)

    def test_missing_reordered_or_wrong_provenance_rejected(self):
        folder = self.root / 'result'
        for defect in ['missing', 'order', 'provenance', 'traversal']:
            fake_result(folder, self.req)
            meta = read(folder / 'tts-result.json')
            if defect == 'missing':meta['segments'].pop()
            elif defect == 'order':meta['segments'].reverse()
            elif defect == 'provenance':meta['request_id'] = 'wrong'
            else:meta['segments'][0]['path'] = '../outside.wav'
            write(folder / 'tts-result.json', meta)
            with self.assertRaises(ValueError):validate_result(folder, self.req)

    def test_ambiguous_execution_only_downloads_on_resume(self):
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(self.root, self.cfg)
        calls = []
        def call(*args, **kwargs):
            calls.append((args, kwargs))
            if args[0] == 'exec' and '].run(' in kwargs.get('code', ''):
                raise ColabError('COLAB_TIMEOUT')
            if args[0] == 'download':
                raise ColabError('COLAB_COMMAND_FAILED: output not yet available')
            marker = re.search(r'VP_EXEC_OK_[0-9a-f]+', kwargs.get('code', ''))
            return marker.group() if marker else ''
        with patch.object(client, 'ensure_authenticated'), patch.object(client, 'call', side_effect=call):
            with self.assertRaisesRegex(ColabError, 'TIMEOUT'):
                client.synthesize(self.req, self.root / 'out', self.root / 'cache')
            calls.clear()
            with patch('colab_bridge.client.file_hash', return_value='a'*64):
                with self.assertRaises(ColabError):
                    client.synthesize(self.req, self.root / 'out2', self.root / 'cache')
            self.assertEqual([x[0][0] for x in calls], ['download'])
            calls.clear()
            changed = copy.deepcopy(self.req);changed['request_id'] = 'changed-content'
            with self.assertRaisesRegex(ColabError,'PENDING_OTHER_REQUEST'):
                client.synthesize(changed,self.root/'out3',self.root/'cache')
            self.assertEqual(calls,[])

    def test_archive_traversal_rejected(self):
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(self.root, self.cfg)
        def download(*args, **kwargs):
            with zipfile.ZipFile(args[-1], 'w') as z:z.writestr('../escape.wav', b'bad')
        with patch.object(client, 'call', side_effect=download):
            with self.assertRaisesRegex(ColabError, 'UNSAFE'):
                client._download('/remote', self.root, self.req)
        self.assertFalse((self.root.parent / 'escape.wav').exists())

    def test_success_import_and_local_cache_without_resubmission(self):
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(self.root, self.cfg)
        def download(remote, folder, req):
            fake_result(folder / 'result', req)
        with patch.object(client, 'ensure_authenticated'), patch.object(client, 'call', side_effect=lambda *a, **k: (re.search(r'VP_EXEC_OK_[0-9a-f]+', k.get('code', '')).group() if 'code' in k else '')) as call, patch.object(client, '_download', side_effect=download):
            first = client.synthesize(self.req, self.root / 'out', self.root / 'cache')
            call.reset_mock()
            second = client.synthesize(self.req, self.root / 'out2', self.root / 'cache')
            self.assertEqual(first, second)
            call.assert_not_called()
            self.assertEqual(file_hash(self.root / 'out/segment-0.wav'), file_hash(self.root / 'out2/segment-0.wav'))

    def test_auto_start_invoked_when_session_not_allocated(self):
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(self.root, self.cfg)
        started = []
        with patch.object(client, '_alias', return_value='colab:account-02'), \
             patch.object(client, '_budgets') as mock_budgets, \
             patch.object(client, 'start', side_effect=lambda: started.append(True)):
            snapshot_empty = {
                'identity_configured': True, 'uncertain': False,
                'blocks': {}, 'available_seconds': 3600,
                'allocated_sessions': [], 'needs_service_recheck': False
            }
            snapshot_allocated = {
                'identity_configured': True, 'uncertain': False,
                'blocks': {}, 'available_seconds': 3600,
                'allocated_sessions': [{'session': client.session, 'device': 'T4'}],
                'needs_service_recheck': False
            }
            mock_budgets.return_value.snapshot.side_effect = [snapshot_empty, snapshot_allocated]
            client._ready()
            self.assertEqual(len(started), 1)


class ParallelTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkflowTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.f = self.fixture
        cfg = read(self.f.root / 'config.json')
        cfg['colab_tts']['enabled'] = True
        write(self.f.root / 'config.json', cfg)
        self.f.new()
        self.f.approve('content')

    def test_audio_and_images_overlap_and_review_waits_for_both(self):
        barrier = threading.Barrier(2, timeout=15)
        original = __import__('pilot').Pilot.run
        seen = set()
        def run(p, job, module):
            if module in ('audio', 'images') and module not in seen:
                seen.add(module)
                barrier.wait()
            return original(p, job, module)
        with patch('pilot.Pilot.run', run):
            state = self.f.media()
        self.assertEqual(state['stage'], 'media')
        self.assertEqual(state['state'], 'awaiting_review')
        self.assertFalse(workflow.approved(self.f.p, self.f.job, 'media'))
        self.assertTrue(all(self.f.p.rows(self.f.job)[m]['state'] == 'approved' for m in ['audio','images']))

    def test_one_side_failure_keeps_completed_images_and_resume_does_not_redraw(self):
        original = self.f.audio
        self.f.audio = lambda *a: (_ for _ in ()).throw(Blocked('COLAB_TIMEOUT'))
        with self.assertRaisesRegex(Blocked, 'COLAB_TIMEOUT'):
            self.f.media()
        image_revision = self.f.p.rows(self.f.job)['images']['revision']
        self.assertEqual(self.f.p.rows(self.f.job)['images']['state'], 'approved')
        self.assertIsNone(workflow.current(self.f.p, self.f.job, 'media'))
        self.f.audio = original
        self.f.media(provider=lambda *a, **k: self.fail('Images must not be resubmitted'))
        self.assertEqual(self.f.p.rows(self.f.job)['images']['revision'], image_revision)

    def test_parallel_path_still_requires_content_approval(self):
        # Changing a draft doesn't grant a new content approval.
        self.f.p.db.close()
        self.f.p = __import__('pilot').Pilot(self.f.root)
        self.addCleanup(self.f.p.db.close)
        with patch('workflow.approved', return_value=False), patch('workflow.prepare_parallel_media') as run:
            with self.assertRaises(Blocked):workflow.prepare(self.f.p, self.f.job, 'media')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
