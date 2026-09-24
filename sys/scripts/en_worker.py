"""English narration: Pocket TTS Alba, natural speed, dynamic INT8 on CPU.

One WAV per scene preserves the renderer's independent English timeline.
The model handles long text internally; no speech-rate postprocessing is used.
Request `mode: spans` instead voices the English words/sentences embedded in
Vietnamese narration (see adapters.english_spans); tts_worker.py splices them.
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


def take_settings(cfg, item):
    """Settings for one take. A retake arrives with an explicit `take` (seed and
    temperature chosen by adapters.span_take), so every rejection changes a
    recorded, controllable knob; without one the legacy seed offset applies.
    Retake 0 resolves to the plain settings, so existing cache keys stay valid."""
    retake = int(item.get('retake', 0))
    take = item.get('take') or {}
    return dict(cfg, en_seed=int(take.get('seed', cfg['en_seed'] + retake)),
                en_temperature=float(take.get('temperature', cfg['en_temperature'])))


def load(cfg):
    torch.set_num_threads(cfg['en_threads'])
    torch.set_num_interop_threads(1)
    torch.manual_seed(cfg['en_seed'])
    model = TTSModel.load_model(language='english', quantize=True, temp=cfg['en_temperature'])
    quantized = sum('quantized' in type(m).__module__ for m in model.modules())
    if not quantized:
        raise RuntimeError('INT8 modules were not loaded; refusing full-precision fallback')
    return model, model.get_state_for_audio_prompt('alba'), quantized


def synth(model, voice, text, s, f, key):
    """Synthesize `text` with take settings `s` into cache file `f` (stamped by key)."""
    stamp = f.with_suffix('.sha256')
    if not (f.exists() and stamp.exists() and stamp.read_text() == key):
        # Reset per take: retries/skipped cached takes cannot change later voices.
        torch.manual_seed(s['en_seed'])
        model.temp = s['en_temperature']
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
    return w


def run_spans(req, out, cfg):
    """English words/sentences embedded in Vietnamese narration. tts_worker.py
    splices these into the VieNeu track; VieNeu itself cannot voice English
    final clusters ('scold' was heard as 'sco')."""
    model, voice, quantized = load(cfg)
    raw = Path(req['cache_dir']) if req.get('cache_dir') else out / 'raw-en-spans'
    raw.mkdir(parents=True, exist_ok=True)
    results = []
    for item in req['spans']:
        name = item['id']
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in name):
            raise ValueError('Invalid span ID')
        text = item['text'].strip()
        if not text:
            raise ValueError('Empty English span')
        s = take_settings(cfg, item)
        key = cache_key(text, s, int(item.get('retake', 0)))
        w = synth(model, voice, text, s, raw / (key + '.wav'), key)
        path = f'en-span-{name}.wav'
        sf.write(out / path, w, SR, subtype='PCM_16')
        results.append(dict(id=name, text=text, path=path, seed=s['en_seed'],
                            temperature=s['en_temperature'], content_duration=len(w) / SR))
    (out / 'en-spans-result.json').write_text(json.dumps(dict(
        engine=ENGINE, voice='alba', settings=cfg, quantized_modules=quantized,
        spans=results), ensure_ascii=False, indent=2))


def run(source, out):
    req = json.loads(source.read_text())
    cfg = settings(req['settings'])
    out.mkdir(parents=True, exist_ok=True)
    if req.get('mode') == 'spans':
        return run_spans(req, out, cfg)
    model, voice, quantized = load(cfg)
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
        # Settings-level seed/temperature per take: retake 0 keys exactly as
        # before; a retake gets a new seed AND a lower temperature, so a
        # rejected read is re-synthesised with a steadier sampler.
        s = take_settings(cfg, sc)
        key = cache_key(text, dict(cfg, en_temperature=s['en_temperature']), retake)
        w = synth(model, voice, text, s, raw / (name + '.wav'), key)
        pad = max(0, int(float(sc['tail']) * SR) - tail_silence(w, SR))
        path = f'en-{name}.wav'
        sf.write(out / path, np.concatenate([w, np.zeros(pad, dtype=np.float32)]), SR, subtype='PCM_16')
        results.append(dict(scene_id=name, path=path, content_duration=len(w) / SR,
                            take=dict(retake=retake, seed=s['en_seed'], temperature=s['en_temperature'])))
    (out / 'en-result.json').write_text(json.dumps(dict(
        engine=ENGINE, voice='alba', settings=cfg, quantized_modules=quantized,
        scenes=results), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]), Path(sys.argv[2]))
