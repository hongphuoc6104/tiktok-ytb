"""Runs only on Colab: cached models/prompts, bounded T4 batches, measured WAVs.

Imported into the persistent Jupyter kernel, so subsequent jobs reuse weights.
No BetterBox, HTTP server, paid inference API, CPU fallback or torch.compile.
"""
import gc
import hashlib
import json
from pathlib import Path
import time
import zipfile

_MODEL = None
_MODEL_KEY = None
_PROMPTS = {}
SR = 48000


def run(request_path, output_dir):
    import numpy as np
    import soundfile as sf
    import torch
    from scipy.signal import resample_poly
    from omnivoice import OmniVoice
    from huggingface_hub import snapshot_download
    global _MODEL, _MODEL_KEY, _PROMPTS
    req = json.loads(Path(request_path).read_text())
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('COLAB_GPU_REQUIRED: expected an actual NVIDIA T4')
    start = time.monotonic()
    raw = output.parent.parent / 'audio-cache'
    raw.mkdir(exist_ok=True)
    waves, stats = {}, []
    worker_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for lang in sorted(req['profiles']):
        spec = req['models'][lang]
        profile = req['profiles'][lang]
        ref = Path(profile['remote_wav'])
        if hashlib.sha256(ref.read_bytes()).hexdigest() != profile['sha256']:
            raise RuntimeError('Voice reference checksum mismatch')
        model_key = (spec['id'], spec['revision'])
        pending = []
        for i, item in enumerate(req['items']):
            if item['language'] != lang:
                continue
            identity = dict(item=item, model=spec, profile={k: v for k, v in profile.items() if k != 'remote_wav'},
                            seed=req['seed'], steps=req['num_step'], worker=worker_hash)
            key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            cached = raw / (key + '.wav')
            if cached.is_file():
                w, sr = sf.read(cached, dtype='float32')
                if sr != SR or not w.size or not np.isfinite(w).all():
                    raise RuntimeError('Invalid cached waveform')
                waves[i] = w
            else:
                pending.append((i, item, cached))
        if not pending:
            continue
        if _MODEL_KEY != model_key:
            _MODEL = None
            _PROMPTS = {}
            gc.collect()
            torch.cuda.empty_cache()
            local = snapshot_download(spec['id'], revision=spec['revision'])
            _MODEL = OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)
            _MODEL_KEY = model_key
        prompt_key = (profile['sha256'], profile['reference_text'])
        if prompt_key not in _PROMPTS:
            _PROMPTS[prompt_key] = _MODEL.create_voice_clone_prompt(ref_audio=str(ref), ref_text=profile['reference_text'])
        prompt = _PROMPTS[prompt_key]
        # Group retakes so their random seeds differ and their cache cannot collide.
        for take in sorted({x[1]['retake'] for x in pending}):
            group = [x for x in pending if x[1]['retake'] == take]
            size = req['batch_size']
            offset = 0
            while offset < len(group):
                batch = group[offset:offset + size]
                torch.manual_seed(req['seed'] + take)
                try:
                    generated = _MODEL.generate(
                        text=[x[1]['text'] for x in batch], language=[lang] * len(batch),
                        voice_clone_prompt=[prompt] * len(batch),
                        speed=[x[1]['speed'] / profile['source_speed'] for x in batch],
                        num_step=req['num_step'])
                except torch.cuda.OutOfMemoryError:
                    if size == 1:
                        raise RuntimeError('COLAB_GPU_OOM: exhausted bounded batch reduction')
                    size = max(1, size // 2)
                    gc.collect()
                    torch.cuda.empty_cache()
                    continue
                if len(generated) != len(batch):
                    raise RuntimeError('Model returned incomplete batch')
                for (i, item, cached), w in zip(batch, generated):
                    w = np.asarray(w, dtype=np.float32).reshape(-1)
                    if not w.size or not np.isfinite(w).all() or np.max(np.abs(w)) < 1e-5:
                        raise RuntimeError('Model returned empty/nonfinite/silent audio')
                    w = resample_poly(w, 2, 1).astype(np.float32)  # OmniVoice: 24 kHz
                    peak = float(np.max(np.abs(w)))
                    if peak > .89:
                        w *= .89 / peak
                    tmp = cached.with_suffix('.tmp.wav')
                    sf.write(tmp, w, SR, subtype='PCM_16')
                    tmp.replace(cached)
                    waves[i] = sf.read(cached, dtype='float32')[0]
                stats.append(dict(language=lang, batch_size=len(batch), retake=take))
                offset += len(batch)
    def save(name, pieces, pause):
        w = np.concatenate(pieces)
        content = len(w) / SR
        w = np.concatenate([w, np.zeros(round(pause * SR), dtype=np.float32)])
        sf.write(output / name, w, SR, subtype='PCM_16')
        return content
    segments, spans = [], []
    for n, part in enumerate(req['segments']):
        pieces = []
        for i in part['items']:
            if pieces:
                pieces.append(np.zeros(round(req['span_gap'] * SR), dtype=np.float32))
            pieces.append(waves[i])
            item = req['items'][i]
            if item['language'] == 'en':
                spans.append(dict(scene_id=part['scene_id'], text=item['text'], voice=req['profiles']['en']['voice'],
                                  engine='omnivoice', seed=req['seed'] + item['retake'], rate=item['speed'], retake=item['retake'], duration=len(waves[i]) / SR))
        name = f'segment-{n:04d}.wav'
        duration = save(name, pieces, part['pause'])
        segments.append(dict(scene_id=part['scene_id'], text=part['text'], path=name, content_duration=duration))
    engine = dict(backend='colab-omnivoice', precision='float16', device=torch.cuda.get_device_name(0),
                  models=req['models'], batch_size=req['batch_size'], num_step=req['num_step'])
    result = dict(request_id=req['request_id'], voice=req['profiles']['vi']['voice'], engine=engine,
                  segments=segments, english_spans=spans, batches=stats,
                  voice_references={k: dict(voice=v['voice'], sha256=v['sha256'], source_speed=v['source_speed']) for k,v in req['profiles'].items()}, elapsed_seconds=time.monotonic() - start)
    (output / 'tts-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if req['english']:
        scenes = []
        for sc in req['english']:
            name = f'en-{sc["scene_id"]}.wav'
            duration = save(name, [waves[sc['item']]], sc['pause'])
            scenes.append(dict(scene_id=sc['scene_id'], path=name, content_duration=duration,
                               take=dict(retake=sc['retake'], seed=req['seed'] + sc['retake'])))
        en = dict(request_id=req['request_id'], voice=req['profiles']['en']['voice'], engine='colab-omnivoice', scenes=scenes)
        (output / 'en-result.json').write_text(json.dumps(en, ensure_ascii=False, indent=2))
    archive = output.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in output.iterdir():
            if path.suffix in ('.json', '.wav'):
                z.write(path, path.name)
    print(json.dumps({'request_id': req['request_id'], 'archive': str(archive), 'elapsed_seconds': result['elapsed_seconds']}), flush=True)
