"""Isolated, review-gated Minh Quan bilingual TTS experiment. No production writes."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import random
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYSTEM = HERE.parents[1]
DATA = HERE / 'artifacts'
STAGES = ['A', 'B', 'C-speed', 'C-split', 'D', 'E', 'final']
DEFAULT = dict(language='current', punctuation='current', speed=0.92,
               split='scene', temperature=0.65, top_p=0.95, post='level')
LABELS = {'A': 'A — Nhận diện tiếng Anh', 'B': 'B — Giữ dấu câu',
          'C-speed': 'C1 — Tốc độ', 'C-split': 'C2 — Chia lời đọc',
          'D': 'D — Độ ổn định', 'E': 'E — Hậu kỳ', 'final': 'Kiểm tra cuối'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def marked_spans(text, phrases):
    """Explicit exact annotations, longest first; never guess language per token."""
    ranges = []
    for phrase in sorted(phrases, key=len, reverse=True):
        for match in re.finditer(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', text):
            a, b = match.span()
            if not any(a < y and b > x for x, y in ranges):
                ranges.append((a, b))
    return [{'start': a, 'end': b, 'text': text[a:b]} for a, b in sorted(ranges)]


def example(sid, group, text, phrases=(), partition='main', source=None):
    return dict(id=sid, group=group, display_text=text, en_spans=marked_spans(text, phrases),
                partition=partition, source=source)


def prepare():
    if (DATA / 'corpus.json').exists():
        verify_frozen()
        print('Bộ câu đã khóa; giữ nguyên.')
        return
    groups = [
        ('vi-tone', [
            'Ma, má, mà, mả, mã, mạ.', 'Mẹ bảo bé mở cửa rồi nghỉ một lát.',
            'Buổi sáng, tôi thức giấc nhưng chưa ra khỏi giường.',
            'Bạn nhớ giữ giọng rõ ràng, đừng nói quá nhanh.']),
        ('vi-punctuation', ['Bạn tỉnh chưa?', 'Bạn tỉnh chưa.', 'Ôi, đẹp quá!',
                            'Đừng vội, hãy nghe hết câu rồi trả lời.']),
        ('en', ['I wake at six every morning.', 'They wake early on Monday.',
                'A sudden noise wakes the baby.', 'Think about these three things before you leave.']),
        ('mixed', ['Trong tiếng Anh, wake có nghĩa là thức giấc.', 'Đừng nhầm wake với get up.',
                   'Ví dụ: I wake at six every morning. Nghĩa là tôi thức giấc lúc sáu giờ mỗi sáng.',
                   'Bạn nghe nhé: A sudden noise wakes the baby. Một tiếng động bất ngờ làm em bé thức giấc.'])]
    phrases = ['I wake at six every morning.', 'They wake early on Monday.',
               'A sudden noise wakes the baby.', 'Think about these three things before you leave.',
               'Ai wake at six every morning', 'They wake early on Monday',
               'A sudden noise wakes the baby', 'wake', 'get up', 'W']
    corpus = []
    for group, texts in groups:
        for text in texts:
            corpus.append(example(f'T{len(corpus)+1:02}', group, text, phrases))
    real_path = SYSTEM / 'runs/vocab-wake-004/revisions/content/3/content.json'
    real = read(real_path)
    for scene in real['scenes']:
        corpus.append(example('R-' + scene['id'], 'mixed', scene['narration'], phrases, 'real',
                              dict(path=str(real_path.relative_to(SYSTEM)), scene=scene['id'],
                                   sha256=file_hash(real_path))))
    other_path = SYSTEM / 'runs/vocab-wake-up-003/revisions/content/1/content.json'
    other = read(other_path)['scenes']
    vi = [(0, 'Bạn nghe thấy tiếng chuông báo thức và bắt đầu tỉnh táo, sẵn sàng cho ngày mới?'),
          (2, 'tôi thức dậy sớm mỗi sáng.'), (2, 'làm ơn đánh thức các con dậy.'),
          (3, 'một tách cà phê thơm ngon giúp tôi tỉnh táo hẳn.')]
    hold_phrases = ['Ai wake up early every morning', 'Please wake up the children',
                    'A cup of coffee helps me wake up', 'Wake up', 'wake up', 'get up', 'up']
    for i, (idx, text) in enumerate(vi):
        assert text in other[idx]['narration']
        start = other[idx]['narration'].index(text)
        corpus.append(example(f'H{i+1:02}', 'vi', text, (), 'holdout',
                              dict(path=str(other_path.relative_to(SYSTEM)), scene=other[idx]['id'],
                                   start=start, end=start+len(text), sha256=file_hash(other_path))))
    for i, scene in enumerate(other[1:5]):
        corpus.append(example(f'H{i+5:02}', 'mixed', scene['narration'], hold_phrases, 'holdout',
                              dict(path=str(other_path.relative_to(SYSTEM)), scene=scene['id'],
                                   sha256=file_hash(other_path))))
    corpus += [example('P01', 'vi-punctuation', 'Bạn tỉnh chưa? Mình bắt đầu bài học nhé.', partition='probe'),
               example('P02', 'vi-punctuation', 'Bạn tỉnh chưa?', partition='probe'),
               example('P03', 'en', 'wake', ['wake'], 'probe'),
               example('P04', 'en', 'get up', ['get up'], 'probe')]
    for item in corpus:
        for span in item['en_spans']:
            assert item['display_text'][span['start']:span['end']] == span['text']
    protected = [SYSTEM / 'config.json', SYSTEM / 'tts_worker.py', SYSTEM / 'adapters.py', real_path, other_path,
                 SYSTEM.parent / 'AGENTS.md', SYSTEM.parent / '.agents/skills/vp-media/references/audio.md']
    protected += list((SYSTEM / 'runs/vocab-wake-004/revisions/audio/2').glob('*'))
    import importlib.util
    for name in ['vieneu.v3turbo', 'vieneu_utils.phonemize_text', 'vieneu_utils.core_utils']:
        protected.append(Path(importlib.util.find_spec(name).origin))
    write(DATA / 'corpus.json', corpus)
    write(DATA / 'frozen.json', dict(created=now(), corpus_sha256=file_hash(DATA/'corpus.json'),
          protected={str(p): file_hash(p) for p in protected if p.is_file()}))
    # Preserve the exact historical artifact, not a regenerated substitute.
    history = DATA / 'history'
    history.mkdir(exist_ok=True)
    for name in ['narration.wav', 'request.json', 'tts-result.json']:
        src = SYSTEM / 'runs/vocab-wake-004/revisions/audio/2' / name
        shutil.copy2(src, history / name)
    print(f'Đã khóa {len(corpus)} mục: 16 chính, 5 cảnh thật, 8 kiểm tra cuối, 4 chẩn đoán.')


def verify_frozen():
    frozen = read(DATA/'frozen.json')
    if frozen['corpus_sha256'] != file_hash(DATA/'corpus.json'):
        raise ValueError('Bộ câu đã bị thay đổi sau khi khóa.')
    changed = [p for p, sha in frozen['protected'].items() if not Path(p).is_file() or file_hash(p) != sha]
    if changed:
        raise ValueError('Dữ liệu/mã đối chứng đã đổi; không trộn kết quả: ' + ', '.join(changed))


def text_pieces(item, language):
    """Keep display text immutable. Correct I only inside explicitly annotated English."""
    text = item['display_text']
    pieces, cursor = [], 0
    for span in item['en_spans']:
        a, b = span['start'], span['end']
        if cursor < a:
            pieces.append(('vi', text[cursor:a]))
        en = text[a:b]
        if language != 'current':
            en = re.sub(r'^Ai(?=\s+wake\b)', 'I', en)
        pieces.append(('en', en))
        cursor = b
    if cursor < len(text):
        pieces.append(('vi', text[cursor:]))
    return pieces or [('vi', text)]


def speech_text(item, language):
    return ''.join(f'<en>{t}</en>' if lang == 'en' and language == 'tagged' else t
                   for lang, t in text_pieces(item, language))


def criteria(item):
    out = []
    if item['group'] != 'en':
        out += ['vi_tone', 'vi_clear', 'vi_prosody']
    if item['en_spans']:
        out += ['en_sound', 'en_stress', 'en_rhythm']
    out += ['identity']
    if item['en_spans'] and item['group'] != 'en':
        out += ['transition']
    return out


def previous(stage):
    i = STAGES.index(stage)
    return STAGES[i-1] if i else None


def load_decision(stage):
    path = DATA / 'decisions' / f'{stage}.json'
    if not path.exists():
        raise ValueError(f'Chưa có kết quả nghe vòng {stage}; không tự chọn cấu hình.')
    result = read(path)
    plan = read(DATA/'rounds'/stage/'plan.json')
    if result['plan_digest'] != digest(plan):
        raise ValueError('Kết quả nghe không khớp bộ thử.')
    return result


def hardest():
    plan = read(DATA/'rounds/C-split/plan.json')
    decision = load_decision('C-split')
    ratings = read(DATA/'reviews/C-split.json')['ratings']
    by_id = {r['clip_id']: r for r in ratings}
    values = {}
    for clip in plan['clips']:
        if clip['variant'] != decision['selected']:
            continue
        rating = by_id[clip['clip_id']]
        score = sum(rating['scores'].values()) / len(rating['scores'])
        values[clip['sample_id']] = (not bool(rating['errors']), score, clip['sample_id'])
    return sorted(values, key=lambda sid: values[sid])[:8]


def make_plan(stage):
    verify_frozen()
    corpus = read(DATA/'corpus.json')
    cfg = dict(DEFAULT) if not previous(stage) else load_decision(previous(stage))['config'].copy()
    samples = [x for x in corpus if x['partition'] in ('main', 'real')]
    if stage == 'A':
        variants = [('current', dict(language='current')), ('standard', dict(language='standard')),
                    ('tagged', dict(language='tagged'))]
    elif stage == 'B':
        samples += [x for x in corpus if x['id'] in ('P01', 'P02')]
        variants = [('current', dict(punctuation='current')), ('preserve', dict(punctuation='preserve'))]
    elif stage == 'C-speed':
        variants = [(str(s), dict(speed=s)) for s in [0.92, 0.96, 1.0]]
    elif stage == 'C-split':
        samples += [x for x in corpus if x['id'] in ('P03', 'P04')]
        variants = [(s, dict(split=s)) for s in ['scene', 'sentence', 'language']]
    elif stage == 'D':
        ids = hardest()
        samples = [x for x in corpus if x['id'] in ids]
        variants = [(str(t), dict(temperature=t)) for t in [0.65, 0.5, 0.8]]
    elif stage == 'E':
        samples = [x for x in corpus if x['id'] in hardest()]
        variants = [('level', dict(post='level')), ('master', dict(post='master'))]
    else:
        samples = [x for x in corpus if x['partition'] in ('holdout', 'real')]
        variants = [('candidate', {})]
    clips = []
    for item in samples:
        for variant, delta in variants:
            if stage == 'A' and not item['en_spans'] and variant != 'current':
                continue
            for take in range(3 if stage == 'D' else 1):
                settings = dict(cfg, **delta)
                clip_id = digest([stage, item['id'], variant, take])[:20]
                clips.append(dict(clip_id=clip_id, sample_id=item['id'], variant=variant,
                                  take=take, settings=settings, criteria=criteria(item)))
    # Shuffle separately within each sample; letters reveal no global setting order.
    rng = random.Random(20260922 + STAGES.index(stage))
    rng.shuffle(clips)
    for item in samples:
        letters = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        for c in clips:
            if c['sample_id'] == item['id']:
                c['blind_label'] = next(letters)
    return dict(stage=stage, corpus_hash=file_hash(DATA/'corpus.json'), base=cfg,
                variants=[v for v, _ in variants], clips=clips,
                parent_decision=digest(load_decision(previous(stage))) if previous(stage) else None)


def validate_review(plan, review):
    if review.get('plan_digest') != digest(plan):
        raise ValueError('Phiếu không thuộc vòng thử hiện tại.')
    if not str(review.get('reviewer', '')).strip() or review.get('listened') is not True:
        raise ValueError('Cần tên người đánh giá và xác nhận đã nghe.')
    if any('en_sound' in c['criteria'] for c in plan['clips']) and review.get('english_competent') is not True:
        raise ValueError('Chưa xác nhận khả năng đánh giá phát âm tiếng Anh.')
    ratings = review.get('ratings', [])
    by_id = {r['clip_id']: r for r in ratings}
    if len(by_id) != len(ratings) or set(by_id) != {c['clip_id'] for c in plan['clips']}:
        raise ValueError('Phiếu thiếu, trùng hoặc thừa bản nghe.')
    for clip in plan['clips']:
        r = by_id[clip['clip_id']]
        if r.get('heard') is not True or set(r.get('scores', {})) != set(clip['criteria']):
            raise ValueError('Cần nghe và chấm đủ tiêu chí cho từng bản.')
        if any(type(v) is not int or not 1 <= v <= 5 for v in r['scores'].values()):
            raise ValueError('Điểm phải là số nguyên 1–5.')
        if not isinstance(r.get('errors'), list):
            raise ValueError('Cần danh sách lỗi, để [] nếu không có.')
        for error in r['errors']:
            if not isinstance(error, dict) or not str(error.get('description', '')).strip():
                raise ValueError('Lỗi cần mô tả cụ thể.')
            if type(error.get('seconds')) not in (int, float) or error['seconds'] < 0:
                raise ValueError('Lỗi cần thời điểm không âm.')
    return by_id


def meets_threshold(ratings):
    if not ratings or any(r['errors'] for r in ratings):
        return False
    groups = {}
    for r in ratings:
        if min(r['scores'].values()) < 3:
            return False
        for key, score in r['scores'].items():
            groups.setdefault(key, []).append(score)
    return all(sum(v)/len(v) >= 4 for v in groups.values())


def import_review(stage, path):
    verify_frozen()
    plan = read(DATA/'rounds'/stage/'plan.json')
    review = read(path)
    by_id = validate_review(plan, review)
    # A partial/failed synthesis cannot acquire a valid quality decision.
    for clip in plan['clips']:
        result = read(DATA/'rounds'/stage/'clips'/f"{clip['clip_id']}.json")
        if not result['technical']['valid']:
            raise ValueError('Có WAV chưa đạt kiểm tra kỹ thuật.')
    target = DATA/'reviews'/f'{stage}.json'
    if target.exists():
        raise ValueError('Phiếu đã nhập được giữ nguyên; không ghi đè lịch sử.')
    ranked = []
    for i, variant in enumerate(plan['variants']):
        selected = [by_id[c['clip_id']] for c in plan['clips'] if c['variant'] == variant
                    and not (stage == 'A' and 'en_sound' not in c['criteria'])]
        errors = sum(bool(r['errors']) for r in selected)/len(selected)
        avg = sum(sum(r['scores'].values())/len(r['scores']) for r in selected)/len(selected)
        ranked.append(dict(variant=variant, error_rate=errors, mean=avg, order=i))
    # Explicit conservative tie window: 0.1/5, only at equal hard-error rate.
    best_errors = min(r['error_rate'] for r in ranked)
    eligible = [r for r in ranked if r['error_rate'] == best_errors]
    best_mean = max(r['mean'] for r in eligible)
    winner = min((r for r in eligible if best_mean-r['mean'] <= 0.1), key=lambda r:r['order'])['variant']
    config = next(c['settings'] for c in plan['clips'] if c['variant'] == winner)
    chosen = [by_id[c['clip_id']] for c in plan['clips'] if c['variant'] == winner]
    decision = dict(stage=stage, created=now(), plan_digest=digest(plan), reviewer=review['reviewer'],
                    selected=winner, config=config, ranking=ranked, meets_threshold=meets_threshold(chosen))
    if stage == 'final':
        d_decision = load_decision('D')
        decision['verdict'] = 'passed' if decision['meets_threshold'] and d_decision['meets_threshold'] else 'not_passed'
    write(target, review)
    write(DATA/'decisions'/f'{stage}.json', decision)
    build_page(stage)
    report()
    print('Đã lưu đánh giá nghe. Cấu hình chọn:', winner)


def build_page(stage):
    folder = DATA/'rounds'/stage
    plan = read(folder/'plan.json')
    corpus = {x['id']: x for x in read(DATA/'corpus.json')}
    groups = []
    for sid in dict.fromkeys(c['sample_id'] for c in plan['clips']):
        item = corpus[sid]
        group = dict(id=sid, text=item['display_text'], clips=[])
        for c in plan['clips']:
            if c['sample_id'] != sid:
                continue
            path = folder/'clips'/f"{c['clip_id']}.json"
            if not path.exists():
                continue
            result = read(path)
            group['clips'].append(dict(id=c['clip_id'], label=c['blind_label'],
                                      audio=f"audio/{c['clip_id']}.wav", criteria=c['criteria'],
                                      duration=result['technical']['seconds']))
        if group['clips']:
            groups.append(group)
    payload = dict(title=LABELS[stage], stage=stage, plan_digest=digest(plan), groups=groups,
                   expected=len(plan['clips']), ready=sum(len(x['clips']) for x in groups),
                   reviewed=(DATA/'decisions'/f'{stage}.json').exists())
    template = (HERE/'page.html').read_text()
    # Keep configuration, transformed text, scores and variant keys off the blind page.
    encoded = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    (folder/'index.html').write_text(template.replace('__DATA__', encoded), encoding='utf-8')
    index = '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Thử giọng Minh Quân Pro</title><body style="font:18px system-ui;max-width:900px;margin:50px auto;padding:20px"><h1>Minh Quân Pro · Việt & Anh</h1><p>Thử nghiệm riêng. Chưa kết luận chất lượng khi chưa có người nghe đánh giá.</p><ul>'
    for s in STAGES:
        if (DATA/'rounds'/s/'index.html').exists():
            index += f'<li><a href="rounds/{s}/index.html">{html.escape(LABELS[s])}</a></li>'
    index += '</ul><h2>Đối chứng lịch sử</h2><p>Nguyên bản vocab-wake-004, audio revision 2; không cân bằng lại âm lượng.</p><audio controls src="history/narration.wav"></audio><p><a href="report.md">Báo cáo trạng thái</a></p></body></html>'
    (DATA/'index.html').write_text(index, encoding='utf-8')


def report():
    lines = ['# Thử Minh Quân Pro — báo cáo trạng thái', '',
             'Đánh giá nghe tự động: **unsupported trong phiên hiện tại**. Không suy chất lượng từ âm vị, ASR hoặc metadata.', '',
             '| Vòng | WAV hoàn thành | Đánh giá nghe |', '|---|---:|---|']
    for stage in STAGES:
        folder = DATA/'rounds'/stage
        if not (folder/'plan.json').exists():
            lines.append(f'| {LABELS[stage]} | Chưa chạy | Chờ vòng trước |')
            continue
        plan = read(folder/'plan.json')
        n = sum((folder/'clips'/f"{c['clip_id']}.json").exists() for c in plan['clips'])
        dec = DATA/'decisions'/f'{stage}.json'
        status = 'Chưa đánh giá' if not dec.exists() else 'Đã nhập phiếu nghe'
        lines.append(f'| {LABELS[stage]} | {n}/{len(plan["clips"])} | {status} |')
    lines += ['', '## Kết luận', '']
    final = DATA/'decisions/final.json'
    if final.exists():
        d = read(final)
        lines.append('**Đạt bộ thử đã khóa.**' if d['verdict'] == 'passed' else '**Chưa đạt điều kiện áp dụng.** Xem lỗi và phạm vi trong phiếu nghe.')
    else:
        lines.append('**Chưa đủ bằng chứng để kết luận Minh Quân Pro đọc đạt cả Việt và Anh–Mỹ.**')
    lines += ['', 'Không sửa cấu hình sản xuất, thư viện đã cài, Rules hoặc revision. Bộ kiểm tra cuối chưa được dùng để chọn cấu hình.',
              '', 'Phiếu nghe có thời điểm lỗi được lưu nguyên vẹn ở reviews/. Kết quả chọn cấu hình nằm ở decisions/.',
              'WAV nguồn, đầu vào thực tế, âm vị, seed và phép đo nằm trong cache/ và rounds/.',
              'Kiểm tra file không rỗng/không NaN không chứng minh không nuốt âm hoặc cắt lời; cần nghe WAV.', '']
    (DATA/'report.md').write_text('\n'.join(lines), encoding='utf-8')


def run_stage(stage, limit=None):
    verify_frozen()
    folder = DATA/'rounds'/stage
    plan = make_plan(stage)
    if (folder/'plan.json').exists():
        if read(folder/'plan.json') != plan:
            raise ValueError('Kế hoạch đã khóa khác với lựa chọn hiện tại.')
    else:
        write(folder/'plan.json', plan)
    from runtime import Renderer
    engine = Renderer(DATA)
    corpus = {x['id']: x for x in read(DATA/'corpus.json')}
    generated = 0
    for i, clip in enumerate(plan['clips']):
        dest = folder/'clips'/f"{clip['clip_id']}.json"
        if dest.exists():
            saved = read(dest)
            if file_hash(folder/'audio'/f"{clip['clip_id']}.wav") != saved['wav_sha256']:
                raise ValueError('WAV đã thay đổi sau khi lưu.')
            continue
        if limit is not None and generated >= limit:
            break
        print(f'[{stage} {i+1}/{len(plan["clips"])}] {clip["sample_id"]} / {clip["variant"]} / lần {clip["take"]+1}', flush=True)
        result = engine.render(corpus[clip['sample_id']], clip, folder)
        write(dest, result)
        generated += 1
        build_page(stage)
        report()
    verify_frozen()
    build_page(stage)
    report()


def main():
    parser = argparse.ArgumentParser(description='Thử Minh Quân Pro, tách biệt sản xuất')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare')
    p = sub.add_parser('run'); p.add_argument('stage', choices=STAGES); p.add_argument('--limit', type=int)
    p = sub.add_parser('review'); p.add_argument('stage', choices=STAGES); p.add_argument('--file', type=Path, required=True)
    sub.add_parser('report')
    p = sub.add_parser('serve'); p.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    if args.command == 'prepare': prepare()
    elif args.command == 'run': run_stage(args.stage, args.limit)
    elif args.command == 'review': import_review(args.stage, args.file)
    elif args.command == 'report': verify_frozen(); report()
    else:
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
        from functools import partial
        print(f'Trang nghe: http://127.0.0.1:{args.port}/', flush=True)
        ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(DATA))).serve_forever()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        print(f'Dừng: {exc}', file=sys.stderr)
        sys.exit(2)
