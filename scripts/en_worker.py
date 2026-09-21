"""English narration: Pocket TTS Alba, natural speed, dynamic INT8 on CPU.

One WAV per scene preserves the renderer's independent English timeline.
The model handles long text internally; no speech-rate postprocessing is used.
"""
import hashlib
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path

# This worker never loads CUDA, including on machines with a larger GPU.
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np
import soundfile as sf
import torch
from pocket_tts import TTSModel
from scipy.signal import resample_poly

SR = 48000
ENGINE = 'pocket-tts'


def tail_silence(w, sr, thresh_db=-40., win_s=0.01):
    win = max(1, int(win_s * sr))
    n = w.size // win
    if n == 0:
        return 0
    env = np.abs(w[:n * win]).reshape(n, win).mean(1)
    loud = np.flatnonzero(env > 10 ** (thresh_db / 20))
    return w.size if not loud.size else w.size - (int(loud[-1]) + 1) * win


def settings(cfg):
    result = dict(en_voice='alba', en_device='cpu', en_quantize=True,
                  en_temperature=0.3, en_threads=4, en_seed=42)
    result.update({k: cfg[k] for k in result if k in cfg})
    if result['en_voice'] != 'alba' or result['en_device'] != 'cpu' or result['en_quantize'] is not True:
        raise ValueError('English narration requires Alba with INT8 on CPU')
    if not isinstance(result['en_threads'], int) or result['en_threads'] < 1:
        raise ValueError('en_threads must be a positive integer')
    return result


def cache_key(text, cfg, retake=0):
    # Legacy Chatterbox WAVs and changed text/settings must never be reused.
    # `retake` counts rejections of this scene's delivery: same words and
    # settings, so without it a retake would resolve to the cached take.
    data = dict(engine=ENGINE, package=version('pocket-tts'), language='english',
                sample_rate=SR, text=text, settings=cfg, retake=retake, cache_version=1)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def run(source, out):
    req = json.loads(source.read_text())
    cfg = settings(req['settings'])
    torch.set_num_threads(cfg['en_threads'])
    torch.set_num_interop_threads(1)
    torch.manual_seed(cfg['en_seed'])
    model = TTSModel.load_model(language='english', quantize=True, temp=cfg['en_temperature'])
    quantized = sum('quantized' in type(m).__module__ for m in model.modules())
    if not quantized:
        raise RuntimeError('INT8 modules were not loaded; refusing full-precision fallback')
    voice = model.get_state_for_audio_prompt('alba')
    out.mkdir(parents=True, exist_ok=True)
    # Job-level cache survives pilot.py's per-revision output dirs; the .sha256
    # stamp below still gates reuse on text/settings, so a relocated cache can
    # never serve audio for an edited narration.
    raw = Path(req['cache_dir']) if req.get('cache_dir') else out / 'raw-en'
    raw.mkdir(parents=True, exist_ok=True)
    results = []
    for sc in req['scenes']:
        name = sc['scene_id']
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in name):
            raise ValueError('Invalid scene ID')
        text = sc['narration_en'].strip()
        if not text:
            raise ValueError('Empty English narration')
        retake = int(sc.get('retake', 0))
        f = raw / (name + '.wav')
        stamp = raw / (name + '.sha256')
        key = cache_key(text, cfg, retake)
        cached = f.exists() and stamp.exists() and stamp.read_text() == key
        if not cached:
            # Reset per scene: retries/skipped cached scenes cannot change later voices.
            # Offset by retake, or this model's fixed seed would hand back the
            # identical waveform and a rejected read could never be improved.
            torch.manual_seed(cfg['en_seed'] + retake)
            # Pocket TTS manages its own inference contexts across decoder threads.
            w = model.generate_audio(voice, text).detach().cpu().numpy().reshape(-1)
            if not w.size or not np.isfinite(w).all() or np.max(np.abs(w)) < 1e-5:
                raise RuntimeError('Invalid or silent English audio')
            if model.sample_rate != SR:
                from math import gcd
                divisor = gcd(SR, model.sample_rate)
                w = resample_poly(w, SR // divisor, model.sample_rate // divisor)
            temp = f.with_suffix('.tmp.wav')
            sf.write(temp, w, SR, subtype='PCM_16')
            temp.replace(f)
            stamp.write_text(key)
        w, sr = sf.read(f, dtype='float32')
        if sr != SR or w.ndim != 1 or not w.size or not np.isfinite(w).all():
            raise RuntimeError('Invalid cached English WAV')
        pad = max(0, int(float(sc['tail']) * SR) - tail_silence(w, SR))
        path = f'en-{name}.wav'
        sf.write(out / path, np.concatenate([w, np.zeros(pad, dtype=np.float32)]), SR, subtype='PCM_16')
        results.append(dict(scene_id=name, path=path))
    (out / 'en-result.json').write_text(json.dumps(dict(
        engine=ENGINE, voice='alba', settings=cfg, quantized_modules=quantized,
        scenes=results), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]), Path(sys.argv[2]))
