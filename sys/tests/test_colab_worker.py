"""Real DSP/adapter/schema tests with a synthetic model, never auditory approval."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import jsonschema
import numpy as np
import scipy.signal
import soundfile
from pilot import ROOT, read, write
import adapters
from colab_bridge import worker
from colab_bridge.protocol import build_request, validate_result


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'assets/voices', self.root / 'assets/voices')
        self.cfg = read(ROOT / 'config.json')
        self.cfg['colab_tts']['enabled'] = True
        write(self.root / 'config.json', self.cfg)
        self.generated = []
        self.loaded = []
        self.prompts = []
        class OOM(Exception):pass
        self.oom = OOM
        self.torch = SimpleNamespace(Tensor=type('Tensor', (), {}), float16='float16', manual_seed=lambda n: None,
            cuda=SimpleNamespace(is_available=lambda: True, get_device_name=lambda n: 'Tesla T4',
                                 empty_cache=lambda: None, OutOfMemoryError=OOM))
        def load(*a, **kw):
            self.loaded.append((a,kw))
            return SimpleNamespace(create_voice_clone_prompt=prompt, generate=generate)
        def prompt(**kw):
            self.prompts.append(kw)
            return kw
        def generate(**kw):
            self.generated.append(kw)
            return [(.2*np.sin(np.arange(24000)*.03)).astype(np.float32) for _ in kw['text']]
        self.model = SimpleNamespace(from_pretrained=load)
        self.modules = {'torch':self.torch,'omnivoice':SimpleNamespace(OmniVoice=self.model),
                        'huggingface_hub':SimpleNamespace(snapshot_download=lambda model, revision: model)}
        worker._MODEL = None;worker._MODEL_KEY = None;worker._PROMPTS = {}

    def request(self):
        vi = dict(scene_id='SC01', narration='Đây là weather. Hãy nghe.',
                  texts=['Đây là weather.', 'Hãy nghe.'],
                  parts=[[{'lang':'vi','text':'Đây là'},{'lang':'en','text':'weather.'}],
                         [{'lang':'vi','text':'Hãy nghe.'}]],gaps=[.5],tail=2.,retake=0)
        en = dict(scene_id='SC01', narration_en='I enjoy nice weather.',tail=3.,retake=0)
        return build_request(self.root, self.cfg, [vi], [en])

    def run_worker(self, req, out):
        remote = copy.deepcopy(req)
        for profile in remote['profiles'].values():profile['remote_wav'] = profile.pop('local_wav')
        path = out.parent / 'request.json';write(path, remote)
        with patch.dict(sys.modules, self.modules):worker.run(path, out)

    def test_real_wav_pause_voice_and_cached_batch(self):
        req = self.request();out = self.root / 'remote/job/output'
        self.run_worker(req,out)
        self.assertEqual(len(validate_result(out,req)),5)
        self.assertEqual(len(self.loaded),1)
        self.assertEqual(len(self.prompts),2)
        self.assertTrue(all(v==1. for batch in self.generated for v in batch['speed']))
        self.assertTrue(all(batch['num_step']==32 for batch in self.generated))
        count=len(self.generated)
        self.run_worker(req,self.root/'remote/job2/output')
        self.assertEqual(len(self.generated),count)
        self.assertTrue(out.with_suffix('.zip').is_file())

    def test_no_gpu_stops_instead_of_cpu_fallback(self):
        self.torch.cuda.is_available=lambda:False
        with self.assertRaisesRegex(RuntimeError,'GPU_REQUIRED'):
            self.run_worker(self.request(),self.root/'remote/job/output')
        self.assertFalse(self.loaded)

    def test_oom_halves_batch_then_stops_at_one(self):
        def load(*a,**k):
            def fail(**kw):
                self.generated.append(len(kw['text']))
                raise self.oom()
            return SimpleNamespace(create_voice_clone_prompt=lambda **k:None,generate=fail)
        self.model.from_pretrained=load
        with self.assertRaisesRegex(RuntimeError,'bounded batch reduction'):
            self.run_worker(self.request(),self.root/'remote/job/output')
        self.assertEqual(len(self.generated),3)
        self.assertEqual(self.generated[-1],1)

    def test_full_audio_adapter_matches_schema_without_local_tts(self):
        job=self.root/'runs/test';out=job/'revisions/audio/1';out.mkdir(parents=True)
        content={'scenes':[{'id':'SC01','narration':'Đây là weather. Hãy nghe.',
                    'narration_en':'I enjoy nice weather.', 'vocabulary':[{'word':'weather'}],
                    'audio_direction':{'vi':{'learner_pause_seconds':2},'en':{'learner_pause_seconds':3}}}]}
        p=SimpleNamespace(root=self.root,job=lambda j:job,payload=lambda j,m:content,
                          brief=lambda j:({'aspect_ratio':'dual'},1,'hash'))
        def synth(client,req,destination,cache):
            self.run_worker(req,destination)
            validate_result(destination,req)
        with patch('adapters.retakes',return_value={}), patch('adapters.master'), patch('colab_bridge.client.cli',return_value='/bin/true'), patch('colab_bridge.client.Client.synthesize',synth):
            payload=adapters.audio(p,'test',out)
        jsonschema.validate(payload,read(ROOT/'schemas/audio.json'))
        self.assertEqual(payload['voice'],'Minh Quân Pro')
        self.assertEqual(payload['en']['voice'],'alba')
        self.assertEqual(payload['backend'],'colab-omnivoice')
        self.assertEqual(payload['english_spans'][0]['text'],'weather.')
        self.assertAlmostEqual(payload['segments'][-1]['end']-payload['segments'][-1]['content_end'],2)
        self.assertAlmostEqual(payload['en']['scenes'][0]['end']-payload['en']['scenes'][0]['content_end'],3)
        self.assertFalse((self.root/'.venv-tts').exists())


if __name__=='__main__':unittest.main()
