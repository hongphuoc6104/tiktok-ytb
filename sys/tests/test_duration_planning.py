"""PCM/manifest import through the authored engine flow; no live provider claim."""
import copy
import json
import wave
import unittest
from pathlib import Path
from unittest.mock import patch
from pilot import ROOT, Blocked, read, write, digest
import execution
import test_execution_v4 as helpers

class DurationPlanningTests(unittest.TestCase):
    setUp = helpers.ExecutionTests.setUp
    new = helpers.ExecutionTests.new
    outline = helpers.ExecutionTests.outline
    approve = helpers.ExecutionTests.approve
    author_inputs = helpers.ExecutionTests.author_inputs

    def produce_audio(self, p, job, out):
        plan = p.brief(job)[0]['outputs'][0]; language = plan['language']
        scenes = p.payload(job, 'content')['scenes']; seconds = getattr(self, 'scene_seconds', 2)
        frames = b'\0\x20' * round(48000 * seconds); segments = []
        for index, scene in enumerate(scenes):
            name = scene['id'] + '.wav'
            with wave.open(str(out / name), 'wb') as f:
                f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed')); f.writeframes(frames)
            segments.append(dict(scene_id=scene['id'], text=scene['narration'], path=name,
                                 start=index * seconds, end=(index + 1) * seconds, content_end=(index + 1) * seconds))
        with wave.open(str(out / 'narration.wav'), 'wb') as f:
            f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed')); f.writeframes(frames * len(scenes))
        (out / 'subtitles.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nPCM fixture\n')
        write(out / 'tts-result.json', {'request_id': 'fixture-effective'})
        track = dict(language=language, voice=plan['voice'], speed=plan['speed'], duration=seconds * len(scenes),
                     wav='narration.wav', srt='subtitles.srt', segments=segments)
        raw = dict(track, backend='colab-omnivoice', generation_report='tts-result.json', tracks={language: track})
        if getattr(self, 'mutate', None): self.mutate(raw)
        names = [path for path in out.iterdir() if path.suffix in ('.wav', '.srt', '.json') and path.name not in ('audio-result.json','request-colab-effective.json')]
        write(out / 'audio-result.json', dict(request_id='fixture-effective', processing_location='colab', language=language,
                                             payload=raw, files={path.name:digest(path) for path in names}))
        write(out / 'request-colab-effective.json', dict(request_id='fixture-effective', profiles={language:{'voice':plan['voice']}},
            items=[dict(language=language, text=s['narration'], speed=plan['speed']) for s in scenes]))
        result = json.loads(json.dumps(raw))
        def localize(value):
            for key in ('wav','srt','generation_report'):
                if key in value: value[key] = str((out / value[key]).relative_to(p.job(job)))
            for segment in value.get('segments',[]): segment['path'] = str((out / segment['path']).relative_to(p.job(job)))
        localize(result)
        for item in result['tracks'].values(): localize(item)
        return result

    def ready_dialogue(self,mode='auto'):
        self.new(mode);self.author_inputs();execution.advance(self.p,self.job,'dialogue')
        if mode=='review':self.approve('dialogue')

    def prepare(self, mode='auto'):
        self.ready_dialogue(mode)
        with patch('adapters.audio', side_effect=self.produce_audio), patch('execution.runtime_ready'):
            return execution.advance(self.p, self.job, 'audio')

    def test_outside_planning_wav_advances_without_retake_or_content_voice_changes(self):
        self.prepare(); audio = self.p.payload(self.job,'audio')
        self.assertEqual(audio['duration'],12); self.assertTrue(execution.accepted(self.p,self.job,'audio'))
        self.assertLess(audio['duration'],self.p.brief(self.job)[0]['duration']['min_seconds'])
        self.assertEqual(audio['tracks']['vi']['speed'],self.p.brief(self.job)[0]['outputs'][0]['speed'])
        self.assertEqual([s['text'] for s in audio['segments']],[s['narration'] for s in self.content['scenes']])
        self.assertEqual(self.p.rows(self.job)['audio']['revision'],1)
        self.assertEqual(self.p.db.execute('SELECT count(*) FROM audio_edits WHERE job=?',(self.job,)).fetchone()[0],0)

    def test_longer_than_estimate_is_also_accepted(self):
        self.scene_seconds=11;self.prepare()
        self.assertEqual(self.p.payload(self.job,'audio')['duration'],66)
        self.assertTrue(execution.accepted(self.p,self.job,'audio'))

    def test_review_waits_for_actual_audio_instead_of_duration_retake(self):
        result=self.prepare('review')
        self.assertEqual((result['phase'],result['action']),('audio','review'))
        self.assertEqual(self.p.rows(self.job)['audio']['revision'],1)

    def test_invalid_numeric_duration_and_boundaries_still_block(self):
        self.ready_dialogue()
        cases=[('duration',float('nan')),('duration',float('inf')),('duration',0),('duration',True),
               ('start',float('nan')),('end',float('inf')),('content_end',float('nan')),('start',-1),('end',0),('start',-.0005)]
        for index,(key,value) in enumerate(cases):
            with self.subTest(key=key,value=value):
                out=self.p.job(self.job)/f'scratch/bad-{index}';out.mkdir(parents=True)
                def mutate(raw):
                    if key=='duration':raw['tracks']['vi'][key]=value
                    else:raw['tracks']['vi']['segments'][0][key]=value
                self.mutate=mutate;payload=self.produce_audio(self.p,self.job,out)
                with self.assertRaises(Blocked):self.p.remote_checks(self.job,'audio',payload)

    def test_required_duration_needs_explicit_source_and_legacy_still_binds(self):
        self.ready_dialogue();cfg=execution.settings(self.p,self.job)
        required=dict(cfg,duration_requirement={'policy':'required','min_seconds':45,'max_seconds':60,'source':'TEST user explicitly requires 45 to 60 seconds'})
        with patch('execution.settings',return_value=required):
            with self.assertRaisesRegex(Blocked,'DURATION_REQUIRED'):self.p.duration_requirement(self.job,12,self.p.brief(self.job)[0])
            self.p.duration_requirement(self.job,48,self.p.brief(self.job)[0])
        missing=dict(cfg,duration_requirement={'policy':'required','min_seconds':45,'max_seconds':60})
        with patch('execution.settings',return_value=missing):
            with self.assertRaisesRegex(Blocked,'actual user requirement source'):self.p.duration_requirement(self.job,48,self.p.brief(self.job)[0])
        with patch('execution.is_job',return_value=False):
            with self.assertRaisesRegex(Blocked,'DURATION_REQUIRED'):self.p.duration_requirement(self.job,12,self.brief)

    def render_manifest(self):
        from colab_bridge.job_protocol import build_render_request
        from scripts.story_plan import timeline
        from scripts.subtitles import subtitle_cues
        self.prepare();audio=self.p.payload(self.job,'audio');content=self.p.payload(self.job,'content');brief=self.p.brief(self.job)[0]
        image=self.p.job(self.job)/'scratch/image.png';image.parent.mkdir(exist_ok=True);image.write_bytes(b'raw image fixture; no encoder claim')
        images={'items':[dict(scene_id=scene['id'],image_id=item['id'],ratio='9:16',path='scratch/image.png') for scene in content['scenes'] for item in scene['images']]}
        request=build_render_request(ROOT,brief,content,images,audio,lambda name:self.p.path(self.job,name))
        out=self.p.job(self.job)/'scratch/render';out.mkdir(parents=True)
        write(out/'request-colab-render.json',request)
        (out/'video.mp4').write_bytes(b'\0\0\0\x18ftypisomfixture-metadata-only')
        track=request['audio']['tracks']['vi'];scenes=timeline(content,request['images'],request['audio'],'vi','9:16')
        for scene in scenes:
            scene['image']=Path(scene['image']).name
            for beat in scene['images']:beat['src']=Path(beat['src']).name
        write(out/'props.json',dict(outputs=brief['outputs'],aspect_ratio='9:16',primary_language='vi',tracks={'vi':dict(audioSrc='vi.wav',duration=track['duration'],cues=subtitle_cues(track['segments']),scenesByAspect={'9:16':scenes})}))
        write(out/'layout.json',{'passed':True});write(out/'editorial-audit.json',{'errors':[]})
        write(out/'render-result.json',dict(request_id=request['request_id'],operation='render',processing_location='colab',device='TEST synthetic T4; not a service observation',outputs=[dict(brief['outputs'][0],file='video.mp4',width=1080,height=1920,duration=12.,video_codec='h264',audio_codec='aac')],files={path.name:dict(sha256=digest(path),size=path.stat().st_size) for path in out.iterdir() if path.name not in ('request-colab-render.json','render-result.json')}))
        path=lambda name:str((out/name).relative_to(self.p.job(self.job)))
        return dict(video=path('video.mp4'),duration=12.,remote_report=path('render-result.json'),layout_report=path('layout.json'),editorial_report=path('editorial-audit.json')),out,request

    def test_video_uses_current_wav_length_outside_estimate_and_rejects_mismatch(self):
        payload,out,request=self.render_manifest()
        self.assertIn(payload['video'],self.p.remote_checks(self.job,'render',payload))
        with self.assertRaisesRegex(Blocked,'REMOTE_DURATION'):self.p.remote_checks(self.job,'render',dict(payload,duration=float('nan')))
        report=read(out/'render-result.json');report['outputs'][0]['duration']=13.;write(out/'render-result.json',report)
        with self.assertRaisesRegex(ValueError,'duration mismatch'):self.p.remote_checks(self.job,'render',dict(payload,duration=13.))
        report['outputs'][0]['duration']=12.;write(out/'render-result.json',report)
        request['audio']['tracks']['vi']['duration']=float('nan');write(out/'request-colab-render.json',request)
        with self.assertRaisesRegex(Blocked,'audio differs'):self.p.remote_checks(self.job,'render',payload)

    def test_pcm_duration_mismatch_and_changed_hash_still_block(self):
        self.ready_dialogue();out=self.p.job(self.job)/'scratch/mismatch';out.mkdir(parents=True)
        self.mutate=lambda raw:raw['tracks']['vi'].update(duration=13)
        payload=self.produce_audio(self.p,self.job,out)
        with self.assertRaisesRegex(Blocked,'DURATION|TIMELINE'):self.p.remote_checks(self.job,'audio',payload)
        self.mutate=lambda raw:raw.update(duration=0)
        payload=self.produce_audio(self.p,self.job,out)
        with self.assertRaisesRegex(Blocked,'REMOTE_DURATION'):self.p.remote_checks(self.job,'audio',payload)
        self.mutate=None;payload=self.produce_audio(self.p,self.job,out);(out/'SC01.wav').write_bytes(b'changed')
        with self.assertRaisesRegex(Blocked,'REMOTE_ARTIFACT'):self.p.remote_checks(self.job,'audio',payload)

if __name__=='__main__':unittest.main()
