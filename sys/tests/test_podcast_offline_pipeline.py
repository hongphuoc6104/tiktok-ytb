"""Offline coordinator integration; synthetic artifacts are never production evidence."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from podcast.coordinator import Coordinator, _atomic_json
from podcast.direction import locked_content
from podcast.still import copy_selected_still
from podcast.request import prepare_request

SIGNATURE = {'profile_id': 'test-only', 'profile_fingerprint': 'a'*64,
    'profile_wav_sha256': 'b'*64, 'profile_transcript_sha256': 'c'*64,
    'model': 'fake', 'runner_version': 'test', 'speed': .9, 'pitch_shift': 1.,
    'settings': {'tts_voice': 'test-only', 'tts_speed': .9, 'pitch_shift': 1.}}

class OfflinePipelineTests(unittest.TestCase):
    def test_full_run_then_resume_reuses_every_completed_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Coordinator(Path(folder)/'sys')
            shutil.copytree(Path(__file__).resolve().parents[1]/'assets/podcast', c.sys_root/'assets/podcast')
            manifest = prepare_request(c, 'offline-test', 'Một đêm yên')
            episode_id = manifest['episode_id']
            calls = []
            def content(ctx):
                calls.append('content')
                parts = []
                for i in range(1, 5):
                    text = 'Chiếc cốc nằm trên bàn. ' + ' '.join(['yên']*619)
                    parts.append({'id': f'P{i:02}', 'title': 'Yên', 'script': text,
                        'voice_direction': {'delivery': 'Kể chậm và gần gũi.',
                            'ending': 'Nối ý nhẹ nhàng và tự nhiên.',
                            'cues': [{'quote': 'Chiếc cốc nằm trên bàn.', 'intent': 'Giữ nhịp câu tự nhiên.'}]}})
                script = {'title': 'Một đêm yên', 'topic': 'Một đêm yên', 'estimated_wpm': 100,
                          'target_minutes': 25, 'parts': parts}
                _atomic_json(ctx.artifact_path('content/quality/pipeline-state.json'),
                    {'complete': True, 'script': script})
                _atomic_json(ctx.artifact_path('content/locked-input.json'), locked_content(script, SIGNATURE))
                return script
            def audio(ctx, part, chunks, progress_callback, retry_failed=False):
                calls.append(part['id'])
                result = []
                for chunk in chunks:
                    path = ctx.artifact_path('tts/' + chunk['id'] + '.wav')
                    path.write_bytes(b'OFFLINE_TEST_NOT_AUDIO')
                    result.append({'chunk_id': chunk['id'], 'path': str(path), 'duration_seconds': 60})
                return {'status': 'success', 'chunks': result}
            def master(ctx, manifest):
                calls.append('master')
                path=ctx.artifact_path('audio/master.wav'); path.write_bytes(b'OFFLINE_TEST_NOT_AUDIO')
                return {'path': str(path), 'duration_seconds': 1500}
            def image(ctx, manifest):
                calls.append('image')
                return copy_selected_still(ctx, manifest)
            def video(ctx, manifest):
                calls.append('video')
                path=ctx.project_root/'video'/episode_id/'test.mp4';path.parent.mkdir(parents=True)
                path.write_bytes(b'OFFLINE_TEST_NOT_VIDEO')
                return {'path':str(path),'duration_seconds':1500}
            handlers={'generation_signature':SIGNATURE,'content':content,'audio_part':audio,
                      'audio_finalize':master,'image':image,'video':video}
            with patch('podcast.coordinator._wav_duration', return_value=1500), \
                 patch('podcast.coordinator._mp4_probe', return_value=1500):
                result=c.run_episode(episode_id,handlers)
                self.assertEqual(result['status'],'complete',result)
                first=list(calls)
                result=c.resume(episode_id,handlers)
                self.assertEqual(result['status'],'complete',result)
                self.assertEqual(calls,first)
                self.assertEqual(calls,['content','P01','P02','P03','P04','master','image','video'])
