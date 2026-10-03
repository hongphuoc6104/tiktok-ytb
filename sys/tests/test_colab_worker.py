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
        # Existing DSP/bilingual tests deliberately retain the saved Alba 1.0
        # contract; the selected default gets its own clone-prompt test below.
        self.cfg.update(en_voice='alba', en_speed=1.)
        self.cfg['colab_tts']['voices']['en'] = 'assets/voices/alba/profile.json'
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

    def test_selected_reference_default_reaches_remote_clone_prompt(self):
        cfg = read(ROOT / 'config.json')
        text = 'A predator is an animal that hunts other animals for food.'
        request = build_request(self.root, cfg,
            [dict(scene_id='SC01', narration=text, texts=[text], gaps=[], tail=.2)], primary_language='en')
        # Worker cache lives two levels above output; keep that shared-worker
        # layout inside this fixture rather than accidentally using /tmp/cache.
        out = self.root / 'remote/selected-reference/output'
        self.run_worker(request, out)
        validate_result(out, request)
        self.assertEqual(read(out / 'tts-result.json')['voice'], 'reference-narrator')
        self.assertEqual(request['profiles']['en']['sha256'],
                         '97d5aee4bc5bbb4a5951a180c04954f5f33b36e901f9a99084ec9f2ebb1817e9')
        self.assertEqual([prompt['ref_text'] for prompt in self.prompts], [text])
        self.assertEqual([rate for batch in self.generated for rate in batch['speed']], [.92])

    def run_worker(self, req, out):
        remote = copy.deepcopy(req)
        for profile in remote['profiles'].values():profile['remote_wav'] = profile.pop('local_wav')
        out.parent.mkdir(parents=True,exist_ok=True)
        for support in remote.get('support_files', []):
            source=Path(support.pop('local_path'));destination=out.parent/support['name']
            shutil.copy2(source,destination);support['remote_path']=str(destination)
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

    def copy_processing_sources(self):
        for name in ('audio_processing.py','media_packaging.py'):
            shutil.copy2(ROOT/name,self.root/name)
        (self.root/'scripts').mkdir(exist_ok=True)
        shutil.copy2(ROOT/'scripts/subtitles.py',self.root/'scripts/subtitles.py')

    def test_english_only_request_needs_no_vietnamese_reference(self):
        self.cfg['en_speed']=.92
        shutil.rmtree(self.root/'assets/voices/minh-quan-pro')
        request=build_request(self.root,self.cfg,[dict(scene_id='SC01',texts=['I watch a predator.'],gaps=[],tail=1.5,retake=0)],primary_language='en')
        self.assertEqual(set(request['profiles']),{'en'})
        self.assertEqual([(x['language'],x['speed']) for x in request['items']],[('en',.92)])
        out=self.root/'remote/job/output';self.run_worker(request,out)
        validate_result(out,request)
        self.assertEqual(read(out/'tts-result.json')['voice'],'alba')
        self.assertEqual(self.generated[0]['speed'],[.92])

    def test_explicit_english_audio_is_assembled_remotely_without_local_master(self):
        self.copy_processing_sources()
        job=self.root/'runs/english';out=job/'revisions/audio/1';out.mkdir(parents=True)
        content={'scenes':[{'id':'SC01','narration':'Do not use this unrelated track.',
            'narration_en':'A predator hunts for food.','audio_direction':{'en':{'learner_pause_seconds':1.5}}}]}
        brief={'aspect_ratio':'9:16','language':'en','duration':{'min_seconds':.1,'max_seconds':10.},'outputs':[{'aspect_ratio':'9:16','language':'en','subtitles':True,'voice':'alba','speed':.92}]}
        p=SimpleNamespace(root=self.root,job=lambda j:job,payload=lambda j,m:content,brief=lambda j:(brief,1,'hash'))
        seen=[]
        def synth(client,request,destination,cache,**kwargs):
            seen.append(request);self.run_worker(request,destination);validate_result(destination,request)
        with (patch('adapters.retakes',return_value={}),patch('adapters.master',side_effect=AssertionError('Local mastering forbidden')),
              patch('colab_bridge.client.cli',return_value='/bin/true'),patch('colab_bridge.client.Client.synthesize',synth)):
            payload=adapters.audio(p,'english',out)
        jsonschema.validate(payload,read(ROOT/'schemas/audio.json'))
        self.assertEqual(payload['language'],'en')
        self.assertEqual(set(payload['tracks']),{'en'})
        self.assertEqual(payload['segments'][0]['text'],'A predator hunts for food.')
        self.assertEqual(payload['voice'],'alba')
        self.assertEqual(seen[0]['items'][0]['speed'],.92)
        self.assertEqual(set(seen[0]['profiles']),{'en'})
        self.assertTrue((job/payload['wav']).is_file())
        self.assertIn('predator',(job/payload['srt']).read_text())
        self.assertAlmostEqual(payload['segments'][0]['end']-payload['segments'][0]['content_end'],1.5)
        write(out/'request-colab-effective.json',seen[0])
        p.path=lambda j,name:job/name
        from pilot import Pilot
        from types import MethodType
        p.duration_requirement=MethodType(Pilot.duration_requirement,p)
        p.measured_wav_duration=MethodType(Pilot.measured_wav_duration,p)
        with patch('pilot.probe',side_effect=AssertionError('No local processing during import')):
            accepted=Pilot.remote_checks(p,'english','audio',payload)
        self.assertIn(payload['generation_report'],accepted)
        self.assertTrue(all(segment['path'] in accepted for track in payload['tracks'].values() for segment in track['segments']))
        (job/payload['wav']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'changed'):
            validate_result(out,seen[0])

    def test_english_primary_vietnamese_secondary_independent_of_aspect(self):
        self.copy_processing_sources()
        req = build_request(self.root, self.cfg,
            [dict(scene_id='SC01',texts=['I see a predator.'],gaps=[],tail=1.,retake=0)],
            primary_language='en',assemble=True,
            secondary_scenes=[{'scene_id':'SC01','language':'vi','text':'Tôi nhìn thấy thú săn mồi.','tail':2.,'retake':0}])
        out = self.root/'remote/job/output';self.run_worker(req,out)
        validate_result(out,req)
        report = read(out/'audio-result.json')
        self.assertEqual(report['language'],'en')
        self.assertEqual(set(report['payload']['tracks']),{'en','vi'})
        self.assertEqual(report['payload']['tracks']['vi']['voice'],'Minh Quân Pro')
        self.assertEqual(report['payload']['tracks']['en']['language'],'en')
        self.assertEqual(report['payload']['tracks']['vi']['segments'][0]['text'],'Tôi nhìn thấy thú săn mồi.')
        self.assertAlmostEqual(report['payload']['tracks']['vi']['duration']-report['payload']['tracks']['vi']['segments'][0]['content_end'],2.)

    def test_remote_worker_hash_mismatch_stops_before_loading_model(self):
        req = self.request();req['worker_sha256']='0'*64
        with self.assertRaisesRegex(RuntimeError,'checksum mismatch'):
            self.run_worker(req,self.root/'remote/job/output')
        self.assertFalse(self.loaded)


if __name__=='__main__':unittest.main()
