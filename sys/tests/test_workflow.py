"""Three public gates with isolated fake providers; never production approvals."""
import json
import shutil
import subprocess
import tempfile
import time
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
from pilot import ROOT, Pilot, Blocked, read, write, digest
import workflow as wf
import machine_review as mr
import adapters


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ['schemas', '.agents', 'renderer', 'examples', 'scripts', 'assets']:
            shutil.copytree(ROOT / name, self.root / name)
        for name in ['pilot.py', 'workflow.py', 'machine_review.py', 'image_pipeline.py', 'characters.py',
                     'content_contract.py', 'prompt_templates.py', 'adapters.py', 'config.json', 'AGENTS.md', 'GEMINI.md']:
            shutil.copy(ROOT / name, self.root / name)
        # This fixture implements serial generation. Batch behavior has its own provider tests.
        cfg=read(self.root/'config.json');cfg['flow_batch']=False;write(self.root/'config.json',cfg)
        self.p = Pilot(self.root)
        self.job = 'three-gates'
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.p.db.close)

    def new(self, mode='review'):
        wf.new(self.p, self.job, read(ROOT / 'examples/m1/brief.json'), mode)
        data = read(ROOT / 'examples/story-v3/content.json')
        _, revision, stamp = self.p.brief(self.job)
        data.update(brief_revision=revision, brief_hash=stamp)
        write(self.p.job(self.job) / 'draft/content.json', data)
        return wf.advance(self.p, self.job, 'content') if mode == 'review' else None

    def approve(self, stage):
        return wf.approve(self.p, self.job, stage, wf.current(self.p, self.job, stage)['revision'], 'TEST explicit user review')

    def provider(self, p, *args, **kwargs):
        folder = Path(args[args.index('--out') + 1])
        chars = list(args[args.index('--character') + 1:]) if '--character' in args else []
        Image.new('RGB', (720, 1280), 'blue').save(folder / 'result.png')
        registration = args[0] == 'character'
        if not registration:
            write(folder / 'result.json', {'jobId': args[args.index('--id') + 1], 'type': 'image',
                'prompt': args[args.index('--prompt') + 1], 'ratio': args[args.index('--ratio') + 1],
                'characters': chars, 'source': 'google-flow-browser', 'status': 'downloaded'})
        write(folder.parent / 'ui-proof.json', {'passed': True, 'mode': 'character-register' if registration else 'image', 'characters': chars})
        Image.new('RGB', (40, 40), 'blue').save(folder.parent / 'before-submit.png')
        return SimpleNamespace(returncode=0, stdout='TEST ONLY', stderr='')

    def audio(self, p, job, out):
        segments = []
        combined = b''
        secs = getattr(self, 'scene_seconds', 8)
        for i, scene in enumerate(p.payload(job, 'content')['scenes']):
            raw = b'\x00\x20' * (48000 * secs)
            name = out / f'{scene["id"]}.wav'
            with wave.open(str(name), 'wb') as f:
                f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed')); f.writeframes(raw)
            combined += raw
            segments.append({'scene_id': scene['id'], 'text': scene['narration'],
                'path': str(name.relative_to(p.job(job))), 'start': i * secs, 'end': (i + 1) * secs})
        wav = out / 'narration.wav'
        with wave.open(str(wav), 'wb') as f:
            f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed')); f.writeframes(combined)
        srt = out / 'subtitles.srt'; srt.write_text(adapters.make_srt(segments))
        return {'voice': 'TEST', 'backend': 'onnx', 'wav': str(wav.relative_to(p.job(job))),
                'srt': str(srt.relative_to(p.job(job))), 'duration': len(segments) * secs, 'segments': segments}

    def media(self, provider=None):
        base = self.p.job(self.job) / 'flow'; base.mkdir(exist_ok=True)
        Image.new('RGB', (40, 40), 'blue').save(base / 'preflight.png')
        cfg = read(self.root / 'config.json')
        write(base / 'preflight.json', {'mode': 'image', 'model': cfg['flow_model'],
            'profile': cfg['flow_profile'], 'project': cfg['flow_project'], 'observed_at': time.time(),
            'account_confirmed': True, 'observer': 'TEST', 'credits_per_generation': 0,
            'operations': ['image', 'character-register'], 'screenshot': 'flow/preflight.png',
            'screenshot_hash': digest(base / 'preflight.png')})
        with patch('adapters.gflow', side_effect=provider or self.provider), patch('adapters.audio', side_effect=self.audio):
            return wf.advance(self.p, self.job, 'media')

    def test_audio_retake_targets_one_scene_and_leaves_images_alone(self):
        """`--part audio --scene SC03` means read that scene again, not redraw it."""
        self.new(); self.approve('content'); self.media()
        revision = wf.current(self.p, self.job, 'media')['revision']
        images_revision = self.p.rows(self.job)['images']['revision']
        wf.reject(self.p, self.job, 'media', revision, 'TEST read SC03 again', part='audio', scene='SC03')
        rows = self.p.db.execute('SELECT scene_id FROM audio_edits WHERE job=?', (self.job,)).fetchall()
        self.assertEqual([r['scene_id'] for r in rows], ['SC03'])
        self.assertEqual(self.p.rows(self.job)['audio']['state'], 'needs_changes')
        self.assertEqual(self.p.rows(self.job)['images']['revision'], images_revision)

    def test_whole_track_retake_bumps_every_scene(self):
        self.new(); self.approve('content'); self.media()
        revision = wf.current(self.p, self.job, 'media')['revision']
        wf.reject(self.p, self.job, 'media', revision, 'TEST read all of it again', part='audio')
        rows = self.p.db.execute('SELECT scene_id FROM audio_edits WHERE job=?', (self.job,)).fetchall()
        self.assertEqual(sorted(r['scene_id'] for r in rows),
                         sorted(s['id'] for s in self.p.payload(self.job, 'content')['scenes']))

    def test_audio_retake_rejects_an_unknown_scene(self):
        self.new(); self.approve('content'); self.media()
        revision = wf.current(self.p, self.job, 'media')['revision']
        with self.assertRaises(Blocked):
            wf.reject(self.p, self.job, 'media', revision, 'TEST', part='audio', scene='SC99')

    def test_over_long_narration_stops_before_any_image_is_generated(self):
        """The reason STAGES['media'] runs audio first: local TTS is free and
        measures the real duration, so narration that misses the brief window
        must fail before a single Flow credit is spent."""
        self.new(); self.approve('content')
        self.scene_seconds = 20  # 6 scenes -> 120s, outside the brief's 45-60s window
        calls = []
        def counting(p, *args, **kwargs):
            calls.append(args); return self.provider(p, *args, **kwargs)
        with self.assertRaises(Blocked) as caught:
            self.media(provider=counting)
        self.assertIn('Duration outside', str(caught.exception))
        self.assertEqual(calls, [])

    def test_only_three_human_gates_and_no_registration_prompt(self):
        step = self.new()
        self.assertEqual((step['stage'], step['action']), ('content', 'review'))
        self.assertEqual(self.p.rows(self.job)['control']['state'], 'approved')
        with self.assertRaises(Blocked): self.p.run(self.job, 'images')
        self.approve('content')
        step = self.media()
        self.assertEqual((step['stage'], step['action']), ('media', 'review'))
        self.assertEqual([x['stage'] for x in wf.status(self.p, self.job)['stages']], ['content', 'media', 'video'])
        self.assertEqual(self.p.rows(self.job)['images']['state'], 'approved')
        self.assertEqual(self.p.rows(self.job)['audio']['state'], 'approved')
        with self.assertRaises(Blocked): self.p.gate(self.job, 'render')
        self.approve('media')
        self.p.gate(self.job, 'render')
        self.assertEqual(wf.next_step(self.p, self.job)['stage'], 'video')
        confirmations = list((self.p.job(self.job) / 'flow/attempts').glob('*/confirmation.json'))
        self.assertTrue(confirmations)
        for path in confirmations:
            self.assertFalse(read(path)['matches_approved_reference'])
            self.assertTrue(read(path)['pending_media_review'])

    def test_wrong_revision_and_missing_note_blocked(self):
        self.new()
        for revision, note in [(99, 'TEST'), (1, '')]:
            with self.assertRaises(Blocked): wf.approve(self.p, self.job, 'content', revision, note)
        self.assertFalse(wf.approved(self.p, self.job, 'content'))

    def test_writing_a_decision_file_alone_cannot_forge_approval(self):
        self.new()
        data = wf.current(self.p, self.job, 'content')
        decision = self.p.path(self.job, data['decision'])
        forged = {'approved': True, 'actor': 'user', 'note': 'TEST forged, no event', 'manifest_hash': wf.hashobj(data), 'at': time.time(), 'report': None}
        write(decision, forged)
        self.assertFalse(wf.approved(self.p, self.job, 'content'))

    def test_editing_a_saved_decision_after_real_approval_is_rejected(self):
        self.new(); self.approve('content')
        self.assertTrue(wf.approved(self.p, self.job, 'content'))
        data = wf.current(self.p, self.job, 'content')
        decision = self.p.path(self.job, data['decision'])
        result = read(decision); result['note'] = 'TAMPERED after approval'; write(decision, result)
        self.assertFalse(wf.approved(self.p, self.job, 'content'))

    def test_forged_machine_decision_without_event_is_rejected(self):
        self.new('auto')
        data = wf.prepare(self.p, self.job, 'content')
        report = self.p.job(self.job) / 'machine-reviews/forged.json'
        write(report, {'test_only': True})
        forged = {'approved': True, 'actor': 'machine', 'note': 'TEST forged machine decision',
                  'manifest_hash': wf.hashobj(data), 'at': time.time(),
                  'report': 'machine-reviews/forged.json', 'report_hash': digest(report)}
        write(self.p.path(self.job, data['decision']), forged)
        self.assertFalse(wf.approved(self.p, self.job, 'content'))

    def test_reject_then_new_revision_can_be_approved_again(self):
        self.new(); self.approve('content'); self.media(); self.approve('media')
        wf.reject(self.p, self.job, 'media', 1, 'TEST fix SC01', scene='SC01')
        self.assertFalse(wf.approved(self.p, self.job, 'media'))
        self.media()
        self.approve('media')
        self.assertTrue(wf.approved(self.p, self.job, 'media'))

    def test_mode_cannot_change_mid_job(self):
        self.new()
        path = self.p.job(self.job) / 'workflow.json'
        data = read(path); data['mode'] = 'auto'; write(path, data)
        with self.assertRaisesRegex(Blocked, 'immutable'):
            wf.advance(self.p, self.job)

    def test_video_is_the_final_gate_and_tamper_invalidates_completion(self):
        self.new(); self.approve('content'); self.media(); self.approve('media')
        def render(p, job, out):
            (out / 'video.mp4').write_bytes(b'TEST ONLY; probe is mocked')
            Image.new('RGB', (720, 1280), 'blue').save(out / 'SC01.png')
            write(out / 'layout.json', {'passed': True, 'checked_frames': 1})
            rel = lambda name: str((out / name).relative_to(p.job(job)))
            return {'video': rel('video.mp4'), 'stills': [rel('SC01.png')],
                    'layout_report': rel('layout.json'), 'duration': 48}
        metadata = {'streams': [dict(codec_type='video', width=720, height=1280,
                    avg_frame_rate='30/1', duration='48'), dict(codec_type='audio', duration='48')],
                    'format': {'duration': '48'}}
        with patch('adapters.render', side_effect=render), patch('pilot.probe', return_value=metadata):
            result = wf.advance(self.p, self.job)
            self.assertEqual((result['stage'], result['action']), ('video', 'review'))
            self.assertFalse(wf.status(self.p, self.job)['complete'])
            self.assertFalse((self.root / 'video').exists())
            with self.assertRaises(Blocked):
                wf.publish_videos(self.p, self.job)
            self.approve('video')
        self.assertTrue(wf.status(self.p, self.job)['complete'])
        published = self.root / 'video' / self.job / f'{self.job}_r1_final.mp4'
        self.assertEqual(published.read_bytes(), b'TEST ONLY; probe is mocked')
        self.assertEqual(wf.publish_videos(self.p, self.job), [str(published)])
        published.write_bytes(b'USER FILE')
        with self.assertRaisesRegex(Blocked, 'overwrite'):
            wf.publish_videos(self.p, self.job)
        self.assertEqual(published.read_bytes(), b'USER FILE')
        self.p.path(self.job, self.p.payload(self.job, 'render')['video']).write_bytes(b'changed')
        self.assertFalse(wf.status(self.p, self.job)['complete'])
        with self.assertRaises(Blocked):
            wf.publish_videos(self.p, self.job)

    def test_media_reject_keeps_other_audio_and_requires_new_gate(self):
        self.new(); self.approve('content'); self.media(); self.approve('media')
        old_audio = self.p.rows(self.job)['audio']['hash']
        wf.reject(self.p, self.job, 'media', 1, 'TEST fix SC01', scene='SC01')
        self.assertFalse(wf.approved(self.p, self.job, 'media'))
        self.media()
        self.assertEqual(self.p.rows(self.job)['audio']['hash'], old_audio)
        self.assertEqual(wf.current(self.p, self.job, 'media')['revision'], 2)
        with self.assertRaises(Blocked): self.p.gate(self.job, 'render')

    def test_content_change_invalidates_public_media_gate(self):
        self.new(); self.approve('content'); self.media(); self.approve('media')
        wf.reject(self.p, self.job, 'content', 1, 'TEST rewrite')
        self.assertFalse(wf.approved(self.p, self.job, 'media'))
        with self.assertRaises(Blocked): self.p.gate(self.job, 'render')

    def test_auto_never_accepts_user_approval_or_unsupported(self):
        self.new('auto'); data = wf.prepare(self.p, self.job, 'content')
        with self.assertRaises(Blocked): wf.approve(self.p, self.job, 'content', 1, 'TEST')
        with patch('machine_review.review', side_effect=Blocked('unsupported audio')):
            with self.assertRaises(Blocked): wf.advance(self.p, self.job)
        self.assertFalse(wf.approved(self.p, self.job, 'content'))
        self.assertFalse(self.p.path(self.job, data['decision']).exists())

    def test_machine_decision_bound_to_actual_report(self):
        self.new('auto')
        report = self.p.job(self.job) / 'machine-reviews/test.json'; write(report, {'test_only': True})
        with patch('machine_review.review', return_value='machine-reviews/test.json'):
            wf.advance(self.p, self.job, 'content')
        data = wf.current(self.p, self.job, 'content')
        self.assertEqual(read(self.p.path(self.job, data['decision']))['actor'], 'machine')
        self.assertTrue(wf.approved(self.p, self.job, 'content'))
        write(report, {'tampered': True})
        self.assertFalse(wf.approved(self.p, self.job, 'content'))

    def test_auto_completes_all_three_gates_without_human_decisions(self):
        self.new('auto')
        reviewed = []
        def reviewer(p, job, stage, paths, snapshot):
            reviewed.append(stage)
            file = p.job(job) / 'machine-reviews' / f'test-{len(reviewed)}.json'
            write(file, {'test_only': True, 'stage': stage})
            return str(file.relative_to(p.job(job)))
        def render(p, job, out):
            (out / 'video.mp4').write_bytes(b'TEST ONLY; probe mocked')
            Image.new('RGB', (720, 1280), 'blue').save(out / 'SC01.png')
            write(out / 'layout.json', {'passed': True, 'checked_frames': 1})
            rel = lambda name: str((out / name).relative_to(p.job(job)))
            return {'video': rel('video.mp4'), 'stills': [rel('SC01.png')],
                    'layout_report': rel('layout.json'), 'duration': 48}
        metadata = {'streams': [dict(codec_type='video', width=720, height=1280,
                    avg_frame_rate='30/1', duration='48'), dict(codec_type='audio', duration='48')],
                    'format': {'duration': '48'}}
        with patch('machine_review.review', side_effect=reviewer):
            wf.advance(self.p, self.job, 'content')
            self.media()
            with patch('adapters.render', side_effect=render), patch('pilot.probe', return_value=metadata):
                self.assertTrue(wf.advance(self.p, self.job)['complete'])
        self.assertEqual([x for x in reviewed if x != 'registration'], ['content', 'media', 'video'])
        for stage in wf.STAGES:
            data = wf.current(self.p, self.job, stage)
            self.assertEqual(read(self.p.path(self.job, data['decision']))['actor'], 'machine')
        count = self.p.db.execute("SELECT count(*) FROM events WHERE job=? AND event='user_approved'", (self.job,)).fetchone()[0]
        self.assertEqual(count, 0)

    def test_batch_continues_job_error_pauses_shared_error(self):
        with patch('workflow.settings', return_value={'mode': 'auto'}), patch('workflow.advance', side_effect=[Blocked('bad narration'), {'complete': True}]) as advance:
            result = wf.batch(self.p, ['a', 'b'])
            self.assertEqual(advance.call_count, 2)
            self.assertTrue(result['results'][0]['needs_attention'])
        with patch('workflow.settings', return_value={'mode': 'auto'}), patch('workflow.advance', side_effect=Blocked('Login required')) as advance:
            result = wf.batch(self.p, ['a', 'b'])
            self.assertEqual(advance.call_count, 1)
            self.assertTrue(result['results'][0]['queue_paused'])

    def test_real_machine_protocol_requires_every_file_and_criterion(self):
        self.new('auto'); manifest = wf.prepare(self.p, self.job, 'content')
        def response(prompt, schema, out, **kwargs):
            request = read(out / 'request.json')
            return {'structured_output': {'identity': request['identity'], 'inspected_files': list(request['files']),
                'checks': {key: {'verdict': 'pass', 'evidence': 'TEST ONLY observed sentence and scene'} for key in mr.CRITERIA['content']}}}
        with patch('scripts.agy_pipeline.invoke', side_effect=response):
            path = mr.review(self.p, self.job, 'content', manifest['assets'], manifest['snapshot'])
            self.assertTrue(self.p.path(self.job, path).exists())
        def unsupported(*args, **kwargs):
            value = response(*args, **kwargs)
            value['structured_output']['checks']['natural_narration']['verdict'] = 'unsupported'
            return value
        with patch('scripts.agy_pipeline.invoke', side_effect=unsupported):
            with self.assertRaises(Blocked): mr.review(self.p, self.job, 'content', manifest['assets'], manifest['snapshot'])
        def missing(*args, **kwargs):
            value = response(*args, **kwargs); value['structured_output']['inspected_files'] = []; return value
        with patch('scripts.agy_pipeline.invoke', side_effect=missing):
            with self.assertRaises(Blocked): mr.review(self.p, self.job, 'content', manifest['assets'], manifest['snapshot'])

    def test_preflight_reads_real_evidence_and_rejects_cost(self):
        self.new(); self.approve('content')
        shot = self.root / 'shot.png'; Image.new('RGB', (40, 40), 'blue').save(shot)
        cfg = read(self.root / 'config.json')
        evidence = dict(mode='image', model=cfg['flow_model'], profile=cfg['flow_profile'],
            project=cfg['flow_project'], observer='TEST', account_confirmed=True, observed_at=time.time(),
            credits_per_generation=0, operations=['image', 'character-register'], screenshot=str(shot))
        path = self.root / 'evidence.json'; write(path, evidence)
        args = SimpleNamespace(job=self.job, command='flow-preflight', evidence=str(path))
        self.assertIn('preflight', adapters.flow_action(self.p, args))
        evidence['credits_per_generation'] = 2; write(path, evidence)
        with self.assertRaises(Blocked): adapters.flow_action(self.p, args)

    def test_renderer_single_english_and_dual_selection(self):
        code = """import {outputPlans} from './renderer/outputs.mjs';
        const p={aspect_ratio:'16:9',duration:48,en_duration:55,scenes:[{id:'SC01'}],en_scenes:[{id:'SC01',end:55}]};
        const a=outputPlans(p,true);const b=outputPlans({...p,aspect_ratio:'dual'},true);
        let blocked=false;try{outputPlans(p,false)}catch{blocked=true}
        console.log(JSON.stringify({a,b,blocked}));"""
        result = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', code], cwd=ROOT, text=True))
        self.assertEqual(result['a'][0]['props']['audioSrc'], 'narration_en.wav')
        self.assertEqual(result['a'][0]['props']['duration'], 55)
        self.assertTrue(result['a'][0]['props']['hideSubtitles'])
        self.assertEqual(len(result['b']), 2)
        self.assertTrue(result['blocked'])

    def test_media_review_puts_pending_character_comparison_first_and_never_claims_a_match(self):
        # AGENTS.md/docs/workflow.md: character comparison is folded into the media
        # gate and must be shown as pending, never implied to already match.
        self.new(); self.approve('content')
        self.media()
        data = wf.current(self.p, self.job, 'media')
        text = self.p.path(self.job, data['review']).read_text()
        self.assertIn('Cần so sánh trước khi duyệt', text)
        self.assertLess(text.index('Cần so sánh trước khi duyệt'), text.index('Bảng ảnh'))
        content = read(ROOT / 'examples/story-v3/content.json')
        for char in content['characters']:
            self.assertIn(f"({char['id']})", text)
        self.assertIn('CHƯA SO SÁNH', text)
        # The single most important assertion: nothing in review.md may assert a
        # match while image_pipeline.register() recorded it as pending (review
        # mode always writes matches_approved_reference=False, observer='technical').
        self.assertNotIn('khớp', text)
        confirmations = list((self.p.job(self.job) / 'flow/attempts').glob('*/confirmation.json'))
        self.assertTrue(confirmations)
        for path in confirmations:
            e = read(path)
            self.assertFalse(e['matches_approved_reference'])
            self.assertTrue(e['pending_media_review'])
        # Manifest/asset_hashes stay valid and approve() still works after the change.
        self.approve('media')
        self.assertTrue(wf.approved(self.p, self.job, 'media'))

    def test_character_comparison_marks_pending_and_never_claims_a_match(self):
        job = 'char-pending'
        jobdir = self.p.job(job); (jobdir / 'media').mkdir(parents=True)
        Image.new('RGB', (10, 10), 'blue').save(jobdir / 'media/ref.png')
        reg_dir = jobdir / 'flow/attempts/reg1'; reg_dir.mkdir(parents=True)
        write(reg_dir / 'request.json', {'path': 'media/registered.png'})
        Image.new('RGB', (10, 10), 'blue').save(jobdir / 'media/registered.png')
        write(reg_dir / 'confirmation.json', {'matches_approved_reference': False, 'pending_media_review': True,
                                               'observer': 'technical', 'report': None})
        images = {'references': [{'character_id': 'C1', 'name': 'char-pending-C1-abc', 'path': 'media/ref.png'}],
                  'items': [{'references': [{'character_id': 'C1', 'registration_journal': 'flow/attempts/reg1/request.json',
                                              'confirmation': 'flow/attempts/reg1/confirmation.json'}]}]}
        text = '\n'.join(wf.character_comparisons(self.p, job, images))
        self.assertIn('CHƯA SO SÁNH', text)
        self.assertIn('kiểm tra kỹ thuật', text)
        self.assertNotIn('khớp', text)
        self.assertIn('![', text)
        self.assertIn(str(self.p.path(job, 'media/ref.png')), text)
        self.assertIn(str(self.p.path(job, 'media/registered.png')), text)

    def test_character_comparison_reports_machine_match_only_in_auto_mode(self):
        job = 'char-auto'
        jobdir = self.p.job(job); (jobdir / 'media').mkdir(parents=True)
        Image.new('RGB', (10, 10), 'red').save(jobdir / 'media/ref.png')
        reg_dir = jobdir / 'flow/attempts/reg1'; reg_dir.mkdir(parents=True)
        write(reg_dir / 'request.json', {'path': 'media/registered.png'})
        Image.new('RGB', (10, 10), 'red').save(jobdir / 'media/registered.png')
        (jobdir / 'machine-reviews').mkdir()
        write(jobdir / 'machine-reviews/reg.json', {'test_only': True})
        write(reg_dir / 'confirmation.json', {'matches_approved_reference': True, 'pending_media_review': False,
                                               'observer': 'machine', 'report': 'machine-reviews/reg.json'})
        images = {'references': [{'character_id': 'C1', 'name': 'char-auto-C1-abc', 'path': 'media/ref.png'}],
                  'items': [{'references': [{'character_id': 'C1', 'registration_journal': 'flow/attempts/reg1/request.json',
                                              'confirmation': 'flow/attempts/reg1/confirmation.json'}]}]}
        text = '\n'.join(wf.character_comparisons(self.p, job, images))
        self.assertIn('khớp', text)
        self.assertNotIn('CHƯA SO SÁNH', text)

    def test_dual_ratio_images_are_grouped_under_one_heading(self):
        job = 'dual-fmt'
        self.p.job(job).mkdir(parents=True)
        items = [
            {'scene_id': 'SC01', 'image_id': 'SC01_I1', 'ratio': '9:16', 'path': 'media/SC01_I1_9x16.png', 'prompt': 'P1'},
            {'scene_id': 'SC01', 'image_id': 'SC01_I1', 'ratio': '16:9', 'path': 'media/SC01_I1_16x9.png', 'prompt': 'P1'},
            {'scene_id': 'SC02', 'image_id': 'SC02_I1', 'ratio': '9:16', 'path': 'media/SC02_I1_9x16.png', 'prompt': 'P2'},
            {'scene_id': 'SC02', 'image_id': 'SC02_I1', 'ratio': '16:9', 'path': 'media/SC02_I1_16x9.png', 'prompt': 'P2'},
        ]
        text = '\n'.join(wf.scene_image_lines(self.p, job, items))
        self.assertEqual(text.count('### SC01_I1'), 1)
        self.assertEqual(text.count('### SC02_I1'), 1)
        h1, h2 = text.index('### SC01_I1'), text.index('### SC02_I1')
        i916, i169 = text.index('SC01_I1_9x16.png'), text.index('SC01_I1_16x9.png')
        self.assertTrue(h1 < i916 < h2 and h1 < i169 < h2)

    def test_single_ratio_image_layout_is_unchanged(self):
        job = 'single-fmt'
        self.p.job(job).mkdir(parents=True)
        items = [{'scene_id': 'SC01', 'image_id': 'SC01_I1', 'ratio': '9:16', 'path': 'media/SC01_I1.png', 'prompt': 'P1'}]
        self.assertEqual(wf.scene_image_lines(self.p, job, items), [
            '## SC01 — SC01_I1 9:16', f"![SC01]({self.p.path(job, 'media/SC01_I1.png')})", 'P1'])
        legacy = [{'scene_id': 'SC01', 'path': 'media/SC01.png', 'prompt': 'P1'}]
        self.assertEqual(wf.scene_image_lines(self.p, job, legacy), [
            '## SC01 —  ', f"![SC01]({self.p.path(job, 'media/SC01.png')})", 'P1'])


if __name__ == '__main__':
    unittest.main()
