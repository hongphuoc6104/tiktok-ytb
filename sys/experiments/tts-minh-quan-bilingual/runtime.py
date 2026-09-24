"""Actual local inference; experimental overrides live only in this process."""
from __future__ import annotations

import contextlib
import importlib
import importlib.metadata
import importlib.util
import json
import math
import os
import random
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf

from lab import HERE, SYSTEM, digest, file_hash, read, write, now, speech_text, text_pieces


def preserve_terminal(text):
    """Only fill a missing terminal mark, never turn ?/!/comma into a period."""
    if not text.strip():
        return text
    bare = re.sub(r'</en>\s*$', '', text.rstrip()).rstrip('"\'”’)]} ')
    return text if bare.endswith(('.', ',', '?', '!', ';', ':', '…')) else text.rstrip() + '.'


def restore_terminal(original, normalized):
    match = re.search(r'([.,!?;:…])(?:</en>|[\s"\'”’)\]}])*$', original)
    if not match:
        return normalized
    suffix = '</en>' if normalized.rstrip().endswith('</en>') else ''
    stem = normalized.rstrip()[:-5] if suffix else normalized.rstrip()
    return stem.rstrip('.,!?;:… ') + match.group(1) + suffix


@contextlib.contextmanager
def front_end(policy, trace):
    ph = importlib.import_module('vieneu_utils.phonemize_text')
    v3 = importlib.import_module('vieneu.v3turbo')
    real_chunks = ph.normalize_to_chunks_v3_with_gaps
    real_phones = ph.phonemize_text_with_emotions
    real_normalizer = ph._get_normalizer()

    class PreservedNormalizer:
        def normalize(self, text, punc_norm=False):
            if isinstance(text, list):
                return self.normalize_batch(text, punc_norm)
            return restore_terminal(text, real_normalizer.normalize(text, punc_norm=False))

        def normalize_batch(self, texts, punc_norm=False):
            return [self.normalize(t) for t in texts]

    def chunks(text, **kwargs):
        result, gaps = real_chunks(text, **kwargs)
        trace.append(dict(kind='chunks', input=text, normalized=result, gaps=gaps))
        return result, gaps

    def phones(text):
        if policy == 'preserve':
            if '[' in text or '<|emotion_' in text:
                raise ValueError('Bộ thử dấu câu chưa hỗ trợ thẻ cảm xúc.')
            result = restore_terminal(text, ph._get_pipeline().run(text, punc_norm=False))
        else:
            result = real_phones(text)
        trace.append(dict(kind='phonemes', input=text, phonemes=result))
        return result

    with contextlib.ExitStack() as stack:
        if policy == 'preserve':
            stack.enter_context(patch.object(ph, 'punc_norm', preserve_terminal))
            stack.enter_context(patch.object(ph, '_get_normalizer', lambda: PreservedNormalizer()))
        stack.enter_context(patch.object(v3, 'normalize_to_chunks_v3_with_gaps', chunks))
        stack.enter_context(patch.object(v3, 'phonemize_text_with_emotions', phones))
        yield


def units(item, settings):
    mode, lang = settings['split'], settings['language']
    if mode == 'scene':
        return [speech_text(item, lang)]
    if mode == 'language':
        result = []
        for language, text in text_pieces(item, lang):
            if not re.search(r'\w', text):
                if result:
                    result[-1] += text
                continue
            result.append(f'<en>{text.strip()}</en>' if language == 'en' and lang == 'tagged' else text.strip())
        return result
    from vieneu_utils.core_utils import split_into_sentences
    original = item['display_text']
    result, cursor = [], 0
    for sentence in split_into_sentences(original):
        start = original.find(sentence, cursor)
        if start < 0:
            raise ValueError('Không ánh xạ được câu tách về nguyên bản.')
        end = start + len(sentence)
        spans = []
        for span in item['en_spans']:
            a, b = max(start, span['start']), min(end, span['end'])
            if b > a:
                spans.append(dict(start=a-start, end=b-start, text=original[a:b]))
        result.append(speech_text(dict(display_text=sentence, en_spans=spans), lang))
        cursor = end
    return result


def normalized_worker_text(text):
    # Reuse production sanitation, without importing its coordinator or writing a job.
    spec = importlib.util.spec_from_file_location('lab_production_tts', SYSTEM/'tts_worker.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalize_text_for_tts(text)


def audio_stats(wav, sr):
    from vieneu_utils.core_utils import edge_silence
    valid = bool(wav.size > int(sr*.1) and np.isfinite(wav).all() and np.max(np.abs(wav)) > 1e-5)
    lead, tail = edge_silence(wav, sr)
    return dict(valid=valid, samples=int(wav.size), sample_rate=sr, seconds=wav.size/sr,
                peak=float(np.max(np.abs(wav))) if wav.size else 0,
                rms=float(np.sqrt(np.mean(np.square(wav)))) if wav.size else 0,
                leading_silence=lead/sr, trailing_silence=tail/sr,
                edge_check='Không cắt mẫu nguồn; âm đầu/cuối cần nghe kiểm tra.')


class Renderer:
    def __init__(self, data):
        self.data = Path(data)
        # The installed model must already be available. No model/package upgrades.
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        from vieneu import Vieneu
        self.tts = Vieneu(mode='v3turbo', backend='onnx', precision='fp32')
        self.voice = self.tts.resolve_voice_name('Minh Quân Pro')
        if not self.voice:
            raise ValueError('Không tìm thấy đúng giọng Minh Quân Pro; không dùng giọng thay thế.')
        self.sr = self.tts.sample_rate
        if self.sr != 48000 or self.tts.backend != 'onnx':
            raise ValueError('Môi trường khác cấu hình thử đã chốt.')
        assets = {}
        # Hash loaded graphs and model support files, not an unverified model label.
        directories = set()
        for obj in vars(self.tts.engine).values():
            path = getattr(obj, '_model_path', None)
            if isinstance(path, str) and Path(path).is_file():
                p = Path(path)
                assets[str(p)] = file_hash(p)
                directories.add(p.parent)
        for directory in directories:
            for p in directory.iterdir():
                if p.suffix in ('.npz', '.json', '.data') and p.is_file():
                    assets[str(p)] = file_hash(p)
        # Preset is never cloned or altered.
        preset = self.tts._preset_voices[self.voice]
        voice_digest = digest({k: np.asarray(v).tolist() for k, v in preset.items()
                               if k in ('speaker_emb', 'codes')})
        self.environment = dict(python=sys.version, packages={n: importlib.metadata.version(n)
             for n in ['vieneu', 'sea-g2p', 'onnxruntime', 'numpy', 'soundfile']},
             backend='onnx', precision='fp32', voice=self.voice, voice_digest=voice_digest,
             sample_rate=self.sr, assets=assets,
             implementation={p.name: file_hash(p) for p in [HERE/'lab.py', HERE/'runtime.py', SYSTEM/'tts_worker.py']},
             ffmpeg=subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True).stdout.splitlines()[0])
        if not assets:
            raise ValueError('Không lấy được định danh graph thực tế; dừng thay vì dùng cache không rõ model.')
        env_path = self.data/'environment.json'
        if env_path.exists() and read(env_path) != self.environment:
            raise ValueError('Môi trường thử đã thay đổi; cần một đợt thử mới, không trộn kết quả.')
        if not env_path.exists():
            write(env_path, self.environment)

    def source(self, item, clip):
        settings = clip['settings']
        source_settings = {k:v for k,v in settings.items() if k not in ('speed', 'post')}
        seed = int(digest([item['id'], clip['take'], 'minh-quan-trial'])[:8], 16)
        inputs = [normalized_worker_text(t) for t in units(item, settings)]
        identity = dict(inputs=inputs, settings=source_settings, seed=seed, take=clip['take'],
                        environment=digest(self.environment))
        key = digest(identity)
        folder = self.data/'cache'/key
        if (folder/'source.json').exists():
            info = read(folder/'source.json')
            if file_hash(folder/'raw.wav') != info['sha256']:
                raise ValueError('WAV nguồn trong cache bị thay đổi.')
            w, sr = sf.read(folder/'raw.wav', dtype='float32')
            assert sr == self.sr
            return key, w, info
        folder.mkdir(parents=True, exist_ok=True)
        np.random.seed(seed)
        random.seed(seed)
        trace, parts, boundaries = [], [], []
        from vieneu_utils.core_utils import pause_pad_samples, edge_silence
        with front_end(settings['punctuation'], trace):
            for i, text in enumerate(inputs):
                trace.append(dict(kind='utterance', index=i, input=text))
                wav = self.tts.infer(text, voice=self.voice, temperature=settings['temperature'],
                                     top_p=settings['top_p'])
                wav = np.asarray(wav, dtype=np.float32).reshape(-1)
                if not audio_stats(wav, self.sr)['valid']:
                    raise ValueError('TTS trả âm thanh trống hoặc không hợp lệ.')
                sf.write(folder/f'unit-{i:02}.wav', wav, self.sr, subtype='FLOAT')
                if parts:
                    prev_text = re.sub(r'</?en>', '', inputs[i-1]).rstrip().rstrip('"\'”’ ')
                    target = .5 if prev_text.endswith(('.', '?', '!', '…')) else .3
                    _, tail = edge_silence(parts[-1], self.sr)
                    lead, _ = edge_silence(wav, self.sr)
                    pad = pause_pad_samples(parts[-1], wav, self.sr, target)
                    boundaries.append(dict(before_unit=i, target=target, existing=(tail+lead)/self.sr,
                                           added=pad/self.sr, actual=(tail+lead+pad)/self.sr))
                    parts.append(np.zeros(pad, dtype=np.float32))
                parts.append(wav)
        combined = np.concatenate(parts)
        sf.write(folder/'raw.wav', combined, self.sr, subtype='FLOAT')
        info = dict(identity=identity, created=now(), sha256=file_hash(folder/'raw.wav'), trace=trace,
                    boundaries=boundaries, technical=audio_stats(combined, self.sr),
                    source_scope='Clip thử độc lập; WAV lịch sử riêng là đối chứng sản xuất nguyên bản.')
        write(folder/'source.json', info)
        return key, combined, info

    def ffmpeg(self, args, log):
        result = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-y'] + args,
                                capture_output=True, text=True, timeout=120)
        with log.open('a', encoding='utf-8') as f:
            f.write(json.dumps(args) + '\n' + result.stderr + '\n')
        if result.returncode:
            raise ValueError('Hậu kỳ thất bại; xem nhật ký thử nghiệm.')
        return result

    def render(self, item, clip, folder):
        key, raw, info = self.source(item, clip)
        cfg = clip['settings']
        audio_dir = folder/'audio'
        audio_dir.mkdir(parents=True, exist_ok=True)
        log_dir = folder/'logs'
        log_dir.mkdir(exist_ok=True)
        log = log_dir/f"{clip['clip_id']}.log"
        work = self.data/'processed'/clip['clip_id']
        work.mkdir(parents=True, exist_ok=True)
        src = self.data/'cache'/key/'raw.wav'
        tempo = work/'tempo.wav'
        # Speed alternatives all derive from precisely the same source hash.
        filters = [] if cfg['speed'] == 1.0 else [f"atempo={cfg['speed']}"]
        if cfg['post'] == 'master':
            filters += ['equalizer=f=200:t=q:w=1:g=1.5', 'equalizer=f=7000:t=q:w=2:g=-2.5']
        self.ffmpeg(['-i', str(src), '-af', ','.join(filters) if filters else 'anull',
                     '-ar', str(self.sr), '-c:a', 'pcm_f32le', str(tempo)], log)
        measured = self.ffmpeg(['-i', str(tempo), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], log)
        loud = json.loads(measured.stderr[measured.stderr.rindex('{'):measured.stderr.rindex('}')+1])
        lu, peak = float(loud['input_i']), float(loud['input_tp'])
        if not math.isfinite(lu) or not math.isfinite(peak):
            raise ValueError('Không đo được âm lượng.')
        # Fixed comparison target leaves headroom. If needed lower it identically for a whole round.
        target = -23.0
        gain = (target if cfg['post'] == 'level' else -14.0) - lu
        if cfg['post'] == 'level' and peak + gain > -1.5:
            raise ValueError('Không đủ headroom ở -23 LUFS; cần hạ cùng mục tiêu cho cả bộ, không tự nén một bản.')
        chain = f'volume={gain:.6f}dB'
        if cfg['post'] == 'master':
            # Exercise the limiter at the real production level, then match playback loudness.
            chain += f',alimiter=limit={10**(-1.5/20):.8f}:level=disabled:latency=1'
        dest = audio_dir/f"{clip['clip_id']}.wav"
        production = work/'production-level.wav' if cfg['post'] == 'master' else dest
        self.ffmpeg(['-i', str(tempo), '-af', chain, '-ar', str(self.sr), '-c:a', 'pcm_s16le', str(production)], log)
        if cfg['post'] == 'master':
            analysis = self.ffmpeg(['-i', str(production), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], log)
            level = json.loads(analysis.stderr[analysis.stderr.rindex('{'):analysis.stderr.rindex('}')+1])
            correction = target-float(level['input_i'])
            self.ffmpeg(['-i', str(production), '-af', f'volume={correction:.6f}dB', '-ar', str(self.sr),
                         '-c:a', 'pcm_s16le', str(dest)], log)
        wav, sr = sf.read(dest, dtype='float32')
        technical = audio_stats(wav, sr)
        if wav.size != sf.info(tempo).frames:
            raise ValueError('Hậu kỳ làm đổi số mẫu; cần kiểm tra độ trễ.')
        verify_loud = self.ffmpeg(['-i', str(dest), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], log)
        final_loud = json.loads(verify_loud.stderr[verify_loud.stderr.rindex('{'):verify_loud.stderr.rindex('}')+1])
        if abs(float(final_loud['input_i']) - target) > .5:
            raise ValueError('Âm lượng các bản chưa cân bằng trong 0,5 LUFS.')
        technical['lufs'] = float(final_loud['input_i'])
        technical['true_peak_db'] = float(final_loud['input_tp'])
        technical['valid'] = technical['valid'] and technical['true_peak_db'] <= -1.0
        if not technical['valid']:
            raise ValueError('WAV sau hậu kỳ chưa đạt kiểm tra kỹ thuật.')
        return dict(clip=clip, source_key=key, source_sha256=info['sha256'], wav_sha256=file_hash(dest),
                    technical=technical, loudness_target=target, gain_db=gain,
                    listening_status='not_evaluated', created=now())
