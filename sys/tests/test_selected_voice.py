"""New default vs a frozen old contract at the real remote request boundary.

No model/media service is called. The recorder stops before transport; hearing
the selected historical sample is not claimed as hearing a new generated WAV.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

from pilot import ROOT, Blocked, read
from vocab import bank as vb
from vocab import test_bank as helpers
from colab_bridge.client import ColabError
import remote_audio

SHA = '97d5aee4bc5bbb4a5951a180c04954f5f33b36e901f9a99084ec9f2ebb1817e9'
TEXT = 'A predator is an animal that hunts other animals for food.'


class SelectedVoiceTests(unittest.TestCase):
    source = helpers.BankTests.source

    def setUp(self):
        helpers.BankTests.setUp(self)
        self.addCleanup(helpers.BankTests.tearDown,self)
        self.source('money','bank|n|ngân hàng|A2\n')
        self.source('nature','predator|n|động vật săn mồi|B1\necosystem|n|hệ sinh thái|C1\n')
        vb.write_json(self.tmp/'channel.json',read(ROOT/'vocab/channel.json'))
        vb.build()

    def capture_request(self, brief):
        captured=[]
        job=self.tmp/'isolated-voice-job';job.mkdir(exist_ok=True)
        out=job/'audio';out.mkdir(exist_ok=True)
        class PilotView:
            root=ROOT
            def job(self,name):return job
            def brief(self,name):return brief,None
            def payload(self,name,part):
                return {'scenes':[{'id':'SC01','narration_en':TEXT}]}
        class Recorder:
            def __init__(self,*args,**kwargs):pass
            def synthesize(self,request,*args,**kwargs):
                captured.append(copy.deepcopy(request))
                raise ColabError('ISOLATED_REQUEST_CAPTURE_NO_SUBMISSION')
        with patch('adapters.retakes',return_value={}),patch('colab_bridge.client.Client',Recorder):
            with self.assertRaisesRegex(Blocked,'ISOLATED_REQUEST_CAPTURE_NO_SUBMISSION'):
                remote_audio.produce(PilotView(),'isolated-voice-job',out)
        self.assertEqual(len(captured),1)
        return captured[0]

    def test_selected_asset_identity_checksum_and_real_wav_header(self):
        profile=read(ROOT/'assets/voices/reference-narrator/profile.json')
        wav=ROOT/'assets/voices/reference-narrator/reference.wav'
        self.assertEqual(profile['voice'],'reference-narrator')
        self.assertEqual(profile['reference_text'],TEXT)
        self.assertEqual(profile['sha256'],SHA)
        self.assertEqual(hashlib.sha256(wav.read_bytes()).hexdigest(),SHA)
        with wave.open(str(wav)) as source:
            self.assertEqual((source.getnchannels(),source.getsampwidth(),source.getframerate()),(1,2,48000))
            self.assertAlmostEqual(source.getnframes()/source.getframerate(),3.24,places=6)
        self.assertEqual(read(ROOT/'assets/voices/alba/profile.json')['voice'],'alba')

    def test_new_bank_brief_selects_user_voice_in_actual_remote_request(self):
        result=vb.cmd_draw(helpers.args(job='new-selected-voice',word='predator'))
        brief=vb.read_json(Path(result['brief']))
        request=self.capture_request(brief)
        self.assertEqual(request['primary_language'],'en')
        self.assertEqual(set(request['profiles']),{'en'})
        self.assertEqual(request['profiles']['en']['voice'],'reference-narrator')
        self.assertEqual(request['profiles']['en']['sha256'],SHA)
        self.assertEqual(request['profiles']['en']['reference_text'],TEXT)
        self.assertEqual(request['items'][0]['text'],TEXT)
        self.assertEqual(request['items'][0]['speed'],.92)
        self.assertEqual(read(ROOT/'config.json')['tts_voice'],'Minh Quân Pro')

    def test_frozen_alba_brief_keeps_asset_and_rate_despite_new_default(self):
        # Explicit historical contract is valid; changing defaults must never
        # silently substitute the new reference/rate during actual planning.
        old_channel=read(ROOT/'vocab/channel.json')
        old_channel['voice']='alba';old_channel['speed']=1.
        old_channel['outputs'][0].update(voice='alba',speed=1.)
        vb.write_json(self.tmp/'channel.json',old_channel)
        result=vb.cmd_draw(helpers.args(job='saved-alba-contract',word='predator'))
        old_path=Path(result['brief']);saved=old_path.read_bytes()
        old_brief=json.loads(saved)
        vb.write_json(self.tmp/'channel.json',read(ROOT/'vocab/channel.json'))
        vb.cmd_draw(helpers.args(job='new-after-default-change',word='ecosystem'))
        request=self.capture_request(old_brief)
        self.assertEqual(old_path.read_bytes(),saved)
        self.assertEqual(request['profiles']['en']['voice'],'alba')
        self.assertEqual(request['profiles']['en']['sha256'],read(ROOT/'assets/voices/alba/profile.json')['sha256'])
        self.assertEqual(request['items'][0]['speed'],1.)
        self.assertNotEqual(request['profiles']['en']['sha256'],SHA)


if __name__=='__main__':unittest.main()
