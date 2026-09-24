#!/usr/bin/env python3
"""Kho từ vựng theo chủ đề: build, rút từ ra làm video, đánh dấu từ đã làm.

Một video = một NGHĨA của một từ. Từ nhiều nghĩa được tách thành nhiều mục
(sense) riêng, mỗi mục có id riêng và được đánh dấu riêng trong ledger; khi rút
một nghĩa ra làm kịch bản, các nghĩa anh em được liệt kê để kịch bản không lặp.

Dữ liệu:
  vocab/sources/*.txt  nguồn do người viết, mỗi dòng: word|pos|nghĩa tiếng Việt|cefr[|sense]
  vocab/bank.jsonl     bản biên dịch của nguồn (chạy `build`), một mục mỗi dòng
  vocab/ledger.json    trạng thái reserved/done theo id mục; build không đụng vào
"""
import argparse
import contextlib
import copy
import fcntl
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
BANK = ROOT / 'bank.jsonl'
LEDGER = ROOT / 'ledger.json'
BRIEFS = ROOT / 'briefs'
POS = {'n': 'danh từ', 'v': 'động từ', 'adj': 'tính từ', 'adv': 'trạng từ',
       'prep': 'giới từ', 'conj': 'liên từ', 'pron': 'đại từ', 'det': 'từ hạn định',
       'phr': 'cụm từ', 'num': 'số từ', 'int': 'thán từ'}
LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']


class Stop(Exception):
    """Lỗi người dùng sửa được; in ra rồi thoát mã 2."""


def read_json(path, default=None):
    if not path.exists():
        if default is None:
            raise Stop(f'Thiếu file {path}')
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_args(args, job):
    fresh = copy.copy(args)
    fresh.job = job
    fresh.out = None  # mỗi job ghi brief riêng theo mã job
    return fresh


# Lệnh đọc-sửa-ghi ledger phải nối đuôi nhau: hai phiên chạy song song từng làm mất
# một bản ghi 'done' vì cùng đọc rồi cùng ghi đè.
WRITERS = {'draw', 'start', 'queue', 'mark', 'release'}


@contextlib.contextmanager
def ledger_lock():
    ROOT.mkdir(parents=True, exist_ok=True)
    handle = open(ROOT / '.ledger.lock', 'w')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()


def stamp():
    """Ledger nằm trong git và người đọc trực tiếp, nên ghi ngày giờ đọc được."""
    return time.strftime('%Y-%m-%d %H:%M:%S')


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def topics():
    return read_json(ROOT / 'topics.json')['topics']


# ---------------------------------------------------------------- build

def parse_source(path, topic_id, errors):
    """Đọc một file nguồn; trả về list mục thô theo đúng thứ tự dòng."""
    rows = []
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        parts = [x.strip() for x in line.split('|')]
        if len(parts) not in (4, 5):
            errors.append(f'{path.name}:{number}: cần 4 hoặc 5 cột, có {len(parts)}')
            continue
        word, pos, gloss, cefr = parts[:4]
        sense = parts[4] if len(parts) == 5 else ''
        if not (re.fullmatch(r"[a-zà-ÿ][a-zà-ÿ .'-]*", word) or re.fullmatch(r'[A-Z]{2,5}', word)):
            errors.append(f'{path.name}:{number}: từ khoá viết thường, hoặc viết hoa nếu là '
                          f'từ viết tắt: {word!r}')
            continue
        if pos not in POS:
            errors.append(f'{path.name}:{number}: từ loại lạ {pos!r}, chọn trong {sorted(POS)}')
            continue
        if cefr not in LEVELS:
            errors.append(f'{path.name}:{number}: mức {cefr!r} không thuộc {LEVELS}')
            continue
        if not gloss:
            errors.append(f'{path.name}:{number}: thiếu nghĩa tiếng Việt')
            continue
        if sense and not re.fullmatch(r'[a-z0-9-]+', sense):
            errors.append(f'{path.name}:{number}: khoá nghĩa phải là chữ thường/gạch: {sense!r}')
            continue
        rows.append({'word': word, 'pos': pos, 'gloss_vi': gloss, 'cefr': cefr,
                     'sense': sense, 'topic': topic_id, 'source': f'{path.name}:{number}'})
    return rows


def build(_args=None):
    """Biên dịch sources/*.txt thành bank.jsonl. Id ổn định, trùng nghĩa bị chặn."""
    known = {t['id']: t for t in topics()}
    errors = []
    entries = {}
    order = []
    for topic in known:
        path = ROOT / 'sources' / f'{topic}.txt'
        if not path.exists():
            errors.append(f'Thiếu file nguồn cho chủ đề {topic}')
            continue
        for row in parse_source(path, topic, errors):
            key = f"{row['word']}.{row['pos']}" + (f".{row['sense']}" if row['sense'] else '')
            old = entries.get(key)
            if old is None:
                entries[key] = dict(row, id=key, topics=[topic], sources=[row['source']])
                order.append(key)
            elif old['gloss_vi'] == row['gloss_vi']:
                # Cùng một nghĩa xuất hiện ở chủ đề khác: gộp, không nhân bản.
                if topic not in old['topics']:
                    old['topics'].append(topic)
                old['sources'].append(row['source'])
            else:
                errors.append(f"{row['source']}: id {key} đã dùng cho nghĩa {old['gloss_vi']!r} "
                              f"({old['sources'][0]}). Thêm cột thứ 5 (khoá nghĩa) cho cả hai dòng "
                              f"để tách thành hai mục.")
    for path in sorted((ROOT / 'sources').glob('*.txt')):
        if path.stem not in known:
            errors.append(f'File nguồn {path.name} không có trong topics.json')
    if errors:
        raise Stop('Nguồn từ vựng chưa hợp lệ:\n  ' + '\n  '.join(errors))

    families = {}
    for key in order:
        families.setdefault(entries[key]['word'], []).append(key)
    rank = {key: i for i, key in enumerate(
        sorted(order, key=lambda k: (LEVELS.index(entries[k]['cefr']), order.index(k))), 1)}
    lines = []
    for key in order:
        item = entries[key]
        siblings = [k for k in families[item['word']] if k != key]
        lines.append(json.dumps({
            'id': key, 'word': item['word'], 'pos': item['pos'], 'sense': item['sense'],
            'gloss_vi': item['gloss_vi'], 'cefr': item['cefr'], 'topics': item['topics'],
            'rank': rank[key], 'homograph': bool(siblings), 'siblings': siblings,
            'sources': item['sources']}, ensure_ascii=False, sort_keys=True))
    BANK.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    words = {entries[k]['word'] for k in order}
    return {'entries': len(order), 'words': len(words),
            'senses_split': sum(1 for k in order if len(families[entries[k]['word']]) > 1),
            'topics': len(known), 'bank': str(BANK.relative_to(REPO))}


def bank():
    if not BANK.exists():
        raise Stop('Chưa có bank.jsonl; chạy: python3 vocab/bank.py build')
    return [json.loads(line) for line in BANK.read_text(encoding='utf-8').splitlines() if line.strip()]


def ledger():
    return read_json(LEDGER, {'version': 1, 'entries': {}})


def save_ledger(data):
    write_json(LEDGER, data)


def state_of(led, entry_id):
    return led['entries'].get(entry_id, {}).get('status', 'todo')


# ---------------------------------------------------------------- chọn từ

def select(args, led, items):
    """Lọc rồi sắp xếp ứng viên; chỉ trả về mục chưa reserved/done."""
    # Làm lại một từ đã có video phải nói rõ bằng --redo kèm --word; mặc định thì không.
    allowed = {'todo', 'done'} if getattr(args, 'redo', False) else {'todo'}
    pool = [x for x in items if state_of(led, x['id']) in allowed]
    if args.topic:
        wanted = set(args.topic.split(','))
        unknown = wanted - {t['id'] for t in topics()}
        if unknown:
            raise Stop('Chủ đề không có: ' + ', '.join(sorted(unknown)))
        pool = [x for x in pool if wanted & set(x['topics'])]
    if args.level:
        wanted = set(args.level.split(','))
        if wanted - set(LEVELS):
            raise Stop('Mức CEFR không có: ' + ', '.join(sorted(wanted - set(LEVELS))))
        pool = [x for x in pool if x['cefr'] in wanted]
    if args.pos:
        wanted = set(args.pos.split(','))
        if wanted - set(POS):
            raise Stop('Từ loại không có: ' + ', '.join(sorted(wanted - set(POS))))
        pool = [x for x in pool if x['pos'] in wanted]
    if args.word:
        pool = [x for x in pool if x['word'] == args.word.lower()]
    if args.order == 'topic':
        index = [t['id'] for t in topics()]
        pool.sort(key=lambda x: (index.index(x['topics'][0]), x['rank']))
    else:
        pool.sort(key=lambda x: x['rank'])
    return pool


def sibling_notes(led, items, entry):
    """Câu nhắc về các nghĩa khác của cùng từ, để kịch bản không lặp nghĩa."""
    by_id = {x['id']: x for x in items}
    notes = []
    for sid in entry['siblings']:
        other = by_id[sid]
        status = state_of(led, sid)
        made = ' (ĐÃ CÓ VIDEO RIÊNG)' if status == 'done' else ''
        notes.append(f"Từ \"{entry['word']}\" còn nghĩa khác: {other['gloss_vi']} "
                     f"[{other['pos']}, {sid}]{made}. Video này KHÔNG dạy nghĩa đó.")
    return notes


# ---------------------------------------------------------------- brief

def make_brief(entry, led, items, channel):
    example_count = channel.get('example_count', 2)
    if type(example_count) is not int or not 1 <= example_count <= 4:
        raise Stop('example_count phải là số nguyên từ 1 đến 4')
    word = entry['word']
    display = word.upper()
    gloss = entry['gloss_vi']
    pos_vi = POS[entry['pos']]
    names = {t['id']: t['vi'] for t in topics()}
    topic_vi = ', '.join(names[t] for t in entry['topics'])
    siblings = sibling_notes(led, items, entry)
    brief = {
        'schema_version': '3.0',
        'topic': f'Học từ vựng tiếng Anh {display} ({pos_vi}: {gloss}) qua câu chuyện và ngữ cảnh thực tế',
        'audience': channel['audience'],
        'goal': f'Người xem hiểu đúng nghĩa "{gloss}" của từ {display}, nhớ lâu và biết đặt câu tự nhiên',
        'video_type': channel['video_type'],
        'duration': channel['duration'],
        'scene_count': channel['scene_count'],
        'required_points': [
            {'id': 'R1', 'text': f'Mở bằng một tình huống đời thường dẫn thẳng tới từ {display}'},
            {'id': 'R2', 'text': f'Làm rõ nghĩa lõi "{gloss}" ({pos_vi}) bằng hành động/tình huống rõ ràng; chỉ đối chiếu từ dễ nhầm khi cần'},
            {'id': 'R3', 'text': f'{example_count} câu ví dụ dùng {display}, đọc rõ tiếng Anh và nối bằng diễn tiến hoặc đối chiếu có ý nghĩa'},
            {'id': 'R4', 'text': f'Một lượt người xem dùng hoặc nhớ lại {display}, có khoảng chờ và phản hồi, dẫn tự nhiên tới câu của riêng mình'},
        ],
        'language': channel['language'],
        'tone': channel['tone'],
        'style': channel['style'],
        'aspect_ratio': channel['aspect_ratio'],
        'facts_required': False,
        'sources': [],
        'planning': {
            'success_criteria': [
                f'Người xem nói lại được nghĩa "{gloss}" của {display} mà không cần tra từ điển',
                f'Người xem nghe và nhại được cách dùng {display} trong ít nhất một câu',
                'Người xem có lượt trả lời/nhắc lại và kiểm tra đáp án; hiệu quả học và giữ chân cần đo sau khi có người xem thật',
            ],
            'avoid': list(channel['avoid']) + siblings,
            'prior_knowledge': channel['prior_knowledge'],
            'pacing': channel['pacing'],
            'domain_requirements': list(channel['domain_requirements']) + [
                f'Từ khoá duy nhất của video: {display} ({entry["pos"]}), chỉ dạy nghĩa "{gloss}"',
                f'Mức độ người học: CEFR {entry["cefr"]}; chủ đề: {topic_vi}',
                f'Mã mục trong kho từ vựng: {entry["id"]} (dùng để đánh dấu đã làm)',
            ],
            'assumptions': [
                'Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.',
                'Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.',
            ],
            'text_style': channel['text_style'],
            'speech_rates': {lang: {'units_per_second': rate, 'uncertainty': 0.25,
                                    'includes_pauses': False,
                                    'source': 'initial estimate; replace with measured voice rate'}
                             for lang, rate in [('vi', 3.6), ('en', 2.5)]},
        },
    }
    if entry['homograph']:
        brief['planning']['success_criteria'].append(
            f'Người xem không lẫn {display} với các nghĩa khác của chính từ này')
    return brief


def channel_config(args):
    cfg = read_json(ROOT / 'channel.json')
    for key in ['style', 'tone', 'aspect_ratio']:
        if getattr(args, key, None):
            cfg[key] = getattr(args, key)
    return cfg


# ---------------------------------------------------------------- lệnh

def cmd_topics(args):
    led = ledger()
    items = bank()
    names = {t['id']: t for t in topics()}
    out = []
    for tid, topic in names.items():
        group = [x for x in items if tid in x['topics']]
        done = sum(1 for x in group if state_of(led, x['id']) == 'done')
        held = sum(1 for x in group if state_of(led, x['id']) == 'reserved')
        out.append({'id': tid, 'vi': topic['vi'], 'entries': len(group),
                    'done': done, 'reserved': held, 'todo': len(group) - done - held})
    return {'topics': out}


def cmd_status(args):
    led = ledger()
    items = bank()
    counts = {'todo': 0, 'reserved': 0, 'done': 0}
    levels = {}
    for item in items:
        status = state_of(led, item['id'])
        counts[status] = counts.get(status, 0) + 1
        bucket = levels.setdefault(item['cefr'], {'todo': 0, 'reserved': 0, 'done': 0})
        bucket[status] = bucket.get(status, 0) + 1
    reserved = {k: v for k, v in led['entries'].items() if v.get('status') == 'reserved'}
    return {'entries': len(items), 'words': len({x['word'] for x in items}), **counts,
            'by_level': {lv: levels.get(lv, {'todo': 0, 'reserved': 0, 'done': 0}) for lv in LEVELS},
            'reserved_jobs': sorted({v.get('job', '?') for v in reserved.values()})}


def cmd_next(args):
    """Xem trước ứng viên; không giữ chỗ, không sinh brief."""
    led = ledger()
    pool = select(args, led, bank())
    return {'available': len(pool), 'picked': [
        {'id': x['id'], 'word': x['word'], 'pos': x['pos'], 'gloss_vi': x['gloss_vi'],
         'cefr': x['cefr'], 'topics': x['topics'], 'homograph': x['homograph']}
        for x in pool[:args.count]]}


def cmd_show(args):
    led = ledger()
    items = [x for x in bank() if x['word'] == args.word.lower()]
    if not items:
        raise Stop(f'Không có từ {args.word!r} trong kho')
    return {'word': args.word.lower(), 'senses': [
        {'id': x['id'], 'pos': x['pos'], 'sense': x['sense'], 'gloss_vi': x['gloss_vi'],
         'cefr': x['cefr'], 'topics': x['topics'], 'status': state_of(led, x['id']),
         'job': led['entries'].get(x['id'], {}).get('job')} for x in items]}


def cmd_draw(args):
    """Giữ chỗ một mục cho job và ghi brief; chưa tạo job trong pilot."""
    led = ledger()
    items = bank()
    if any(v.get('job') == args.job for v in led['entries'].values()):
        raise Stop(f'Job {args.job} đã giữ chỗ một từ; dùng `mark` hoặc `release` trước')
    if args.redo and not (args.word and args.note.strip()):
        raise Stop('--redo cần --word và --note nêu lý do làm lại từ đã có video')
    pool = select(args, led, items)
    if not pool:
        raise Stop('Không còn từ nào hợp bộ lọc; nới --topic/--level hoặc bổ sung nguồn')
    entry = pool[0]
    path = Path(args.out) if args.out else BRIEFS / f'{args.job}.json'
    if path.exists():
        raise Stop(f'{path} đã có; xoá hoặc chọn --out khác')
    write_json(path, make_brief(entry, led, items, channel_config(args)))
    record = dict(led['entries'].get(entry['id'], {}))
    if record.get('status') == 'done':
        # Làm lại một từ đã có video là quyết định có ý thức; giữ lại dấu vết bản cũ.
        record.setdefault('previous', []).append(
            {k: record[k] for k in ('job', 'at', 'note', 'video') if k in record})
    record.update({'status': 'reserved', 'job': args.job,
                   'brief': str(path.relative_to(REPO)), 'at': stamp()})
    if args.note.strip():
        record['note'] = args.note.strip()
    led['entries'][entry['id']] = record
    save_ledger(led)
    return {'job': args.job, 'entry': entry['id'], 'word': entry['word'],
            'gloss_vi': entry['gloss_vi'], 'cefr': entry['cefr'], 'homograph': entry['homograph'],
            'siblings': sibling_notes(led, items, entry), 'brief': str(path),
            'next': f'python3 pilot.py new {args.job} --brief {path}'}


def cmd_start(args):
    """draw + pilot new: một lệnh để bắt đầu video cho từ kế tiếp."""
    drawn = cmd_draw(args)
    run = subprocess.run([sys.executable, 'pilot.py', 'new', args.job, '--brief', drawn['brief'],
                          '--mode', args.mode], cwd=REPO, capture_output=True, text=True)
    sys.stderr.write(run.stderr)
    if run.returncode != 0:
        led = ledger()
        led['entries'].pop(drawn['entry'], None)
        save_ledger(led)
        # Brief chỉ có nghĩa khi job tồn tại; để lại sẽ chặn lần start sau của cùng mã job.
        Path(drawn['brief']).unlink(missing_ok=True)
        raise Stop('pilot new thất bại, đã trả từ về kho:\n' + (run.stdout or run.stderr).strip())
    return {**drawn, 'pilot': json.loads(run.stdout)}


def next_job_id(prefix, taken):
    """Mã job kế tiếp dạng prefix + số, bỏ qua mã đã có trong runs/ và trong ledger."""
    if not re.fullmatch(r'[A-Za-z0-9_-]+', prefix):
        raise Stop('Tiền tố job chỉ gồm chữ, số, gạch ngang và gạch dưới')
    used = set(taken)
    runs = REPO / 'runs'
    if runs.is_dir():
        used |= {x.name for x in runs.iterdir() if x.is_dir()}
    used |= {v.get('job') for v in ledger()['entries'].values()}
    number = 1
    while f'{prefix}{number:03}' in used:
        number += 1
    return f'{prefix}{number:03}'


def cmd_queue(args):
    """Tạo nhiều job liền nhau và ghi hàng đợi cho `pilot.py batch`."""
    if args.count < 1:
        raise Stop('queue cần --count ít nhất 1')
    jobs, started = [], []
    for _ in range(args.count):
        job = next_job_id(args.prefix, jobs)
        jobs.append(job)
        try:
            started.append(cmd_start(copy_args(args, job)))
        except Stop as ex:
            if not started:
                raise
            return {'created': started, 'stopped_at': job, 'reason': str(ex),
                    'queue': write_queue(args, [x['job'] for x in started])}
    return {'created': started, 'queue': write_queue(args, [x['job'] for x in started])}


def write_queue(args, jobs):
    path = Path(args.out) if args.out else ROOT / 'queue.json'
    write_json(path, jobs)
    return str(path)


ENTRY_TAG = 'Mã mục trong kho từ vựng: '


def brief_entry(job):
    """Mã mục kho mà brief của job đang dùng, None nếu brief không sinh từ kho."""
    pointer = REPO / 'runs' / job / 'brief-current.json'
    if not pointer.exists():
        return None
    meta = read_json(pointer)
    brief = read_json(REPO / 'runs' / job / 'briefs' / f"{int(meta['revision'])}.json")
    for line in brief.get('planning', {}).get('domain_requirements', []):
        if line.startswith(ENTRY_TAG):
            return line[len(ENTRY_TAG):].split(' (')[0].strip()
    return None


def cmd_audit(args):
    """Đối chiếu runs/ với ledger: job nào ngoài kho, job nào xong mà chưa đánh dấu."""
    led = ledger()
    ids = {x['id'] for x in bank()}
    runs = REPO / 'runs'
    jobs = sorted(x.name for x in runs.iterdir() if x.is_dir()) if runs.is_dir() else []
    outside, unmarked, unknown, linked = [], [], [], []
    for job in jobs:
        entry = brief_entry(job)
        if entry is None:
            outside.append(job)
            continue
        if entry not in ids:
            unknown.append({'job': job, 'entry': entry})
            continue
        linked.append({'job': job, 'entry': entry, 'status': state_of(led, entry)})
        if state_of(led, entry) != 'done' and approved_video(job):
            unmarked.append({'job': job, 'entry': entry})
    missing = [{'entry': k, 'job': v.get('job')} for k, v in led['entries'].items()
               if v.get('job') and v['job'] not in jobs]
    return {'jobs': len(jobs), 'linked': linked, 'outside_bank': outside,
            'entry_not_in_bank': unknown, 'approved_but_unmarked': unmarked,
            'ledger_job_missing': missing,
            'fix': 'Job ngoài kho: tạo bằng `bank.py start`. Video đã duyệt: chạy `bank.py mark JOB`.'}


def approved_video(job):
    """True khi phần video của job đã có quyết định duyệt hợp lệ (người hoặc máy)."""
    sys.path.insert(0, str(REPO))
    from pilot import Pilot
    import workflow
    p = Pilot()
    try:
        workflow.published_videos(p, job)
        return True
    except Exception:
        return False
    finally:
        p.db.close()


def cmd_mark(args):
    """Đánh dấu đã làm video. Mặc định chỉ chấp nhận job có video đã duyệt."""
    led = ledger()
    ids = {x['id'] for x in bank()}
    if args.entry:
        targets = [e for e in args.entry.split(',') if e]
        unknown = [e for e in targets if e not in ids]
        if unknown:
            raise Stop('Mã mục không có trong kho: ' + ', '.join(unknown))
    else:
        targets = [k for k, v in led['entries'].items() if v.get('job') == args.job]
        if not targets:
            raise Stop(f'Job {args.job} chưa giữ chỗ từ nào; dùng --entry để đánh dấu thủ công')
    if args.job and not args.force:
        if not approved_video(args.job):
            raise Stop(f'Job {args.job} chưa có video được duyệt. Duyệt xong hãy mark, '
                       f'hoặc --force kèm --note nếu video làm ngoài pipeline.')
    if args.force and not args.note.strip():
        raise Stop('--force cần --note ghi lý do và nơi video đã phát hành')
    for entry_id in targets:
        record = dict(led['entries'].get(entry_id, {}))
        record.update({'status': 'done', 'at': stamp()})
        if args.job:
            record['job'] = args.job
        if args.note.strip():
            record['note'] = args.note.strip()
        if args.video:
            record['video'] = args.video
        led['entries'][entry_id] = record
    save_ledger(led)
    return {'marked': targets, 'job': args.job, 'done': cmd_status(args)['done']}


def cmd_release(args):
    """Trả các mục đang giữ chỗ về kho (job bị huỷ, không dùng cho mục đã done)."""
    led = ledger()
    freed = [k for k, v in led['entries'].items()
             if v.get('job') == args.job and v.get('status') == 'reserved']
    if not freed:
        raise Stop(f'Job {args.job} không giữ chỗ mục nào đang chờ')
    for key in freed:
        led['entries'].pop(key)
    save_ledger(led)
    return {'released': freed, 'job': args.job}


def gloss_tokens(text):
    return {w for w in re.split(r'[^0-9a-zà-ỹ]+', text.lower()) if len(w) > 1}


def same_sense(a, b):
    """Hai lời giải nghĩa có đang nói về cùng một nghĩa hay không.

    Nghĩa ngắn nằm gọn trong nghĩa dài chỉ tính là một khi phần thừa rất ít:
    "tăng" và "tăng lên" là một, còn "khô" và "khô khan, hài hước" thì không.
    """
    if a.strip().lower() == b.strip().lower():
        return True
    x, y = gloss_tokens(a), gloss_tokens(b)
    if not x or not y:
        return False
    if x <= y or y <= x:
        return abs(len(x) - len(y)) <= 2
    return len(x & y) / len(x | y) >= 0.5


def cmd_lint(args):
    """Tìm hai mục cùng từ và từ loại nhưng thật ra dạy đúng một nghĩa.

    Hai mục như vậy sẽ thành hai video trùng nội dung. Cặp đã xem và cố ý giữ
    riêng thì ghi vào vocab/lint-allow.json để lần sau không báo lại.
    """
    allow = {tuple(sorted(pair)) for pair in read_json(ROOT / 'lint-allow.json',
                                                      {'pairs': []})['pairs']}
    groups = {}
    for item in bank():
        groups.setdefault((item['word'], item['pos']), []).append(item)
    suspects = []
    for group in groups.values():
        for i, first in enumerate(group):
            for second in group[i + 1:]:
                pair = tuple(sorted([first['id'], second['id']]))
                if pair in allow or not same_sense(first['gloss_vi'], second['gloss_vi']):
                    continue
                suspects.append({'ids': list(pair), 'word': first['word'],
                                 'glosses': [first['gloss_vi'], second['gloss_vi']],
                                 'topics': [first['topics'], second['topics']]})
    return {'suspects': suspects, 'count': len(suspects), 'allowed': len(allow),
            'fix': 'Xoá một dòng trong vocab/sources/, hoặc thêm cặp id vào vocab/lint-allow.json'}


COMMANDS = {'build': build, 'topics': cmd_topics, 'status': cmd_status, 'next': cmd_next,
            'show': cmd_show, 'draw': cmd_draw, 'start': cmd_start, 'queue': cmd_queue,
            'mark': cmd_mark, 'release': cmd_release, 'lint': cmd_lint,
            'audit': cmd_audit}


def main():
    ap = argparse.ArgumentParser(description='Kho từ vựng theo chủ đề cho video học tiếng Anh')
    ap.add_argument('command', choices=sorted(COMMANDS))
    ap.add_argument('job', nargs='?', help='mã job của pilot (draw/start/mark/release)')
    ap.add_argument('--count', type=int, default=5)
    ap.add_argument('--topic');ap.add_argument('--level');ap.add_argument('--pos')
    ap.add_argument('--word', help='ép chọn đúng một từ (draw) hoặc tra cứu (show)')
    ap.add_argument('--order', choices=['level', 'topic'], default='level')
    ap.add_argument('--out', help='đường dẫn brief cần ghi')
    ap.add_argument('--mode', choices=['review', 'auto'], default='review')
    ap.add_argument('--style');ap.add_argument('--tone');ap.add_argument('--aspect-ratio', dest='aspect_ratio')
    ap.add_argument('--entry', help='đánh dấu thủ công theo mã mục, cách nhau bằng dấu phẩy')
    ap.add_argument('--video', help='đường dẫn hoặc link video đã phát hành')
    ap.add_argument('--note', default='')
    ap.add_argument('--force', action='store_true', help='mark cho video làm ngoài pipeline')
    ap.add_argument('--prefix', default='vocab-', help='tiền tố mã job cho lệnh queue')
    ap.add_argument('--redo', action='store_true',
                    help='làm lại một từ đã có video; cần --word và --note')
    args = ap.parse_args()
    if args.command in ('draw', 'start', 'release') and not args.job:
        raise Stop(f'Lệnh {args.command} cần mã job')
    if args.command == 'mark' and not (args.job or args.entry):
        raise Stop('mark cần mã job hoặc --entry')
    if args.command == 'show' and not args.word:
        raise Stop('show cần --word')
    with ledger_lock() if args.command in WRITERS else contextlib.nullcontext():
        result = COMMANDS[args.command](args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Stop as ex:
        print(json.dumps({'blocked': str(ex)}, ensure_ascii=False, indent=2))
        sys.exit(2)
