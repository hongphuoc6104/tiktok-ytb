import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from podcast.tts import PodcastColabTTS, CalibrationCacheMiss

class CalibrationTests(unittest.TestCase):
    def test_cache_hit_avoids_transport_and_pitch_change_invalidates(self):
        with tempfile.TemporaryDirectory() as folder:
            client = PodcastColabTTS.__new__(PodcastColabTTS)
            client._profile=SimpleNamespace(fingerprint='a'*64, voice_id='fake',
                voice_config={'model':'test', 'recommended_params':{'pitch_shift':1}})
            client.tts_dir=Path(folder)/'tts'
            client.calibration_cache_dir=Path(folder)/'cache'
            client.generation_signature=lambda **kw: {'settings': kw}
            client.synthesize_part=Mock(side_effect=AssertionError('HTTP must not be called'))
            with self.assertRaises(CalibrationCacheMiss):
                client.calibrate(cache_only=True)
            def synthesize(part_id, chunks, **kwargs):
                path=client.tts_dir/'chunks'/f'{chunks[0].chunk_id}.wav'
                path.parent.mkdir(parents=True)
                with wave.open(str(path),'wb') as wav:
                    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(24000)
                    wav.writeframes(bytes(48000))
            transport=Mock(side_effect=synthesize)
            first=client.calibrate(synthesizer=transport)
            second=client.calibrate(cache_only=True)
            self.assertFalse(first.cache_hit)
            self.assertTrue(second.cache_hit)
            self.assertEqual(transport.call_count,1)
            client._profile.voice_config['recommended_params']['pitch_shift']=.95
            with self.assertRaises(CalibrationCacheMiss):
                client.calibrate(cache_only=True)
            client.synthesize_part.assert_not_called()
