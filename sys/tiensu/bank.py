#!/usr/bin/env python3
"""Kho chủ đề kênh giải thích tiền sử: rút chủ đề ra làm video dài 16:9, đánh dấu đã làm.

Một video = một chủ đề (một câu hỏi kiểu kênh mẫu Ink Explainer, xem docs/tien-su-plan.md).
Không có bước build như vocab/bank.py: tiensu/topics.jsonl đã là kho dùng thẳng, mỗi dòng
một chủ đề với sources thật đã có sẵn (bắt buộc vì channel.json đặt facts_required=true).

Dữ liệu:
  tiensu/topics.jsonl  kho chủ đề, mỗi dòng: {id, question, angle, seed_facts, sources}
  tiensu/channel.json  mặc định kênh khi sinh brief (aspect_ratio, duration, style, domain...)
  tiensu/ledger.json   trạng thái reserved/done theo id chủ đề; sửa qua CLI, không sửa tay

Lệnh: status | next | start | mark | queue | audit (xem main()).
"""
import argparse
import contextlib
import copy
import fcntl
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Tiện ích chung tái dùng từ kho từ vựng thay vì chép lại: lỗi người dùng, đọc/ghi JSON,
# đóng dấu thời gian, kiểm tra video đã có quyết định duyệt hợp lệ hay chưa.
from vocab.bank import Stop, read_json, write_json, stamp, approved_video  # noqa: E402

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
TOPICS = ROOT / 'topics.jsonl'
LEDGER = ROOT / 'ledger.json'
BRIEFS = ROOT / 'briefs'

ENTRY_TAG = 'Mã chủ đề trong kho tiền sử: '

# Lệnh đọc-sửa-ghi ledger phải nối đuôi nhau; hai phiên chạy song song từng làm mất
# bản ghi vì cùng đọc rồi cùng ghi đè (xem vocab/bank.py).
WRITERS = {'start', 'queue', 'mark'}


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


def copy_args(args, job):
    fresh = copy.copy(args)
    fresh.job = job
    fresh.out = None  # mỗi job ghi brief riêng theo mã job
    return fresh


def topics():
    """Đọc topics.jsonl; rank giữ đúng thứ tự dòng trong file (thứ tự ưu tiên mặc định)."""
    if not TOPICS.exists():
        raise Stop(f'Thiếu file {TOPICS}')
    items = []
    for number, raw in enumerate(TOPICS.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as ex:
            raise Stop(f'{TOPICS.name}:{number}: JSON lỗi ({ex})') from None
        for key in ('id', 'question', 'angle'):
            if not item.get(key):
                raise Stop(f'{TOPICS.name}:{number}: thiếu trường {key!r}')
        item.setdefault('seed_facts', [])
        item.setdefault('sources', [])
        item['rank'] = number
        items.append(item)
    ids = [x['id'] for x in items]
    if len(ids) != len(set(ids)):
        dup = sorted({x for x in ids if ids.count(x) > 1})
        raise Stop('topics.jsonl có id trùng lặp: ' + ', '.join(dup))
    return items


def ledger():
    return read_json(LEDGER, {'version': 1, 'entries': {}})


def save_ledger(data):
    write_json(LEDGER, data)


def state_of(led, topic_id):
    return led['entries'].get(topic_id, {}).get('status', 'todo')


def channel_config(args=None):
    cfg = read_json(ROOT / 'channel.json')
    for key in ['style', 'tone']:
        if args is not None and getattr(args, key, None):
            cfg[key] = getattr(args, key)
    return cfg


# ---------------------------------------------------------------- chọn chủ đề

def select(args, led, items):
    """Lọc rồi sắp xếp ứng viên; chỉ trả về mục chưa reserved/done."""
    allowed = {'todo', 'done'} if getattr(args, 'redo', False) else {'todo'}
    pool = [x for x in items if state_of(led, x['id']) in allowed]
    if getattr(args, 'tag', None):
        wanted = set(t.strip() for t in args.tag.split(',') if t.strip())
        pool = [x for x in pool if wanted & set(x.get('tags', []))]
    if getattr(args, 'id', None):
        pool = [x for x in pool if x['id'] == args.id]
    pool.sort(key=lambda x: x['rank'])
    return pool


# ---------------------------------------------------------------- brief

def pick_scene_count(channel, topic):
    """hook + 6-8 chương bằng chứng + kết callback, giới hạn theo channel.scene_count."""
    lo, hi = channel['scene_count']['min'], channel['scene_count']['max']
    chapters = len(topic.get('seed_facts')) or 6
    chapters = max(6, min(8, chapters))
    return max(lo, min(hi, chapters + 2)), chapters


def make_brief(topic, channel):
    question = topic['question']
    angle = topic['angle']
    sources = [dict(s) for s in topic.get('sources', [])]
    if not sources:
        raise Stop(f'Chủ đề {topic["id"]} chưa có sources thật trong topics.jsonl; '
                   'bổ sung nghiên cứu trước khi start (facts_required=true không cho sources rỗng)')
    scene_count, chapters = pick_scene_count(channel, topic)
    brief = {
        'schema_version': '3.0',
        'channel': channel['channel'],
        'voice_language': channel.get('voice_language', 'vi'),
        'subtitles': channel.get('subtitles', True),
        'topic': f'{question} — {angle}',
        'audience': channel['audience'],
        'goal': (f'Người xem trả lời được câu hỏi "{question}" bằng bằng chứng khảo cổ/nghiên '
                 f'cứu thật, không phải suy đoán, và nhớ được niềm tin sai đã bị video phá bỏ'),
        'video_type': channel['video_type'],
        'duration': channel['duration'],
        'scene_count': scene_count,
        'required_points': [
            {'id': 'R1', 'text': (f'Hook 2 ngôi "bạn": đối lập đời sống hiện đại của người xem với '
                                   f'cảnh {angle} khoảng 50.000 năm trước, dẫn thẳng tới câu hỏi mở đầu')},
            {'id': 'R2', 'text': 'Phá một niềm tin phổ biến/sai lầm thường gặp về chủ đề trước khi vào bằng chứng'},
            {'id': 'R3', 'text': f'Nhắc lại rõ ràng câu hỏi bí ẩn cần trả lời: "{question}"'},
            {'id': 'R4', 'text': (f'{chapters} chương bằng chứng (scenes[].chapter đặt tên riêng từng chương), '
                                   'mỗi chương dựng trên đúng một nghiên cứu/di chỉ/số liệu cụ thể có claim trỏ '
                                   'tới một mục trong sources')},
            {'id': 'R5', 'text': ('Kết quay lại đúng hình ảnh mở đầu, chốt bằng đối chiếu '
                                   '"Bạn thì… còn họ thì…" giữa đời sống hiện đại và điều vừa học được')},
        ],
        'language': channel['language'],
        'tone': channel['tone'],
        'style': channel['style'],
        'aspect_ratio': channel['aspect_ratio'],
        'facts_required': True,
        'sources': sources,
        'planning': {
            'success_criteria': [
                f'Người xem trả lời lại được câu hỏi "{question}" bằng ít nhất hai bằng chứng cụ thể có nguồn',
                'Người xem nhớ được niềm tin sai đã bị phá trong video và vì sao nó sai',
                'Mọi số liệu/tuyên bố then chốt trong lời dẫn truy được về đúng một mục trong sources; '
                'hiệu quả giữ chân người xem thật cần đo sau khi có dữ liệu Analytics của pilot',
            ],
            'avoid': list(channel['avoid']),
            'prior_knowledge': channel['prior_knowledge'],
            'pacing': channel['pacing'],
            'domain_requirements': list(channel['domain_requirements']) + [
                f'{ENTRY_TAG}{topic["id"]}',
                f'Góc kể riêng của video này: {angle}',
                'Gợi ý nghiên cứu thêm khi viết kịch bản (không phải bằng chứng đã duyệt, phải tự tìm nguồn thật '
                'trước khi đưa vào claims): ' + '; '.join(topic.get('seed_facts', [])) if topic.get('seed_facts')
                else 'Không có gợi ý nghiên cứu thêm; dựa trên sources đã có trong brief.',
            ],
            'assumptions': [
                'Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.',
                'Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh; hiệu chỉnh ở GĐ6 bằng '
                'scripts/calibrate_speech_rates.py sau khi có video pilot thật.',
            ],
            'text_style': channel['text_style'],
            'speech_rates': {
                'vi': {'units_per_second': channel['speech_rates']['vi']['units_per_second'],
                       'uncertainty': channel['speech_rates']['vi']['uncertainty'],
                       'includes_pauses': False,
                       'source': 'initial estimate; replace with measured voice rate after pilot'},
                # voice_language của kênh là vi nên không cần narration_en/quote_en; giữ mục en ở đây
                # chỉ để thoả schema brief-v3 (planning.speech_rates yêu cầu cả vi và en), không dùng ở runtime.
                'en': {'units_per_second': 2.5, 'uncertainty': 0.25, 'includes_pauses': False,
                       'source': 'unused placeholder; channel voice_language=vi, no narration_en required'},
            },
        },
    }
    if channel.get('clips'):
        brief['clips'] = dict(channel['clips'])
    return brief


# ---------------------------------------------------------------- lệnh

def cmd_status(args):
    led = ledger()
    items = topics()
    counts = {'todo': 0, 'reserved': 0, 'done': 0}
    for item in items:
        status = state_of(led, item['id'])
        counts[status] = counts.get(status, 0) + 1
    reserved = {k: v for k, v in led['entries'].items() if v.get('status') == 'reserved'}
    return {'topics': len(items), **counts,
            'reserved_jobs': sorted({v.get('job', '?') for v in reserved.values()})}


def cmd_next(args):
    """Xem trước ứng viên; không giữ chỗ, không sinh brief."""
    led = ledger()
    pool = select(args, led, topics())
    return {'available': len(pool), 'picked': [
        {'id': x['id'], 'question': x['question'], 'angle': x['angle'],
         'sources': len(x.get('sources', []))} for x in pool[:args.count]]}


def reserve(args):
    """Giữ chỗ một chủ đề cho job và ghi brief; chưa tạo job trong pilot."""
    led = ledger()
    items = topics()
    if any(v.get('job') == args.job for v in led['entries'].values()):
        raise Stop(f'Job {args.job} đã giữ chỗ một chủ đề; dùng `mark` trước nếu muốn làm lại')
    pool = select(args, led, items)
    if not pool:
        raise Stop('Không còn chủ đề nào hợp bộ lọc; nới --tag hoặc bổ sung topics.jsonl')
    topic = pool[0]
    path = Path(args.out) if args.out else BRIEFS / f'{args.job}.json'
    if path.exists():
        raise Stop(f'{path} đã có; xoá hoặc chọn --out khác')
    write_json(path, make_brief(topic, channel_config(args)))
    record = dict(led['entries'].get(topic['id'], {}))
    if record.get('status') == 'done':
        record.setdefault('previous', []).append(
            {k: record[k] for k in ('job', 'at', 'note', 'video') if k in record})
    record.update({'status': 'reserved', 'job': args.job,
                   'brief': str(path.relative_to(REPO)), 'at': stamp()})
    if args.note.strip():
        record['note'] = args.note.strip()
    led['entries'][topic['id']] = record
    save_ledger(led)
    return {'job': args.job, 'topic': topic['id'], 'question': topic['question'],
            'angle': topic['angle'], 'brief': str(path),
            'next': f'python3 pilot.py new {args.job} --brief {path}'}


def cmd_start(args):
    """reserve + pilot new: một lệnh để bắt đầu video cho chủ đề kế tiếp."""
    before = copy.deepcopy(ledger()['entries'])
    drawn = reserve(args)
    run = subprocess.run([sys.executable, 'pilot.py', 'new', args.job, '--brief', drawn['brief'],
                          '--mode', args.mode], cwd=REPO, capture_output=True, text=True)
    sys.stderr.write(run.stderr)
    if run.returncode != 0:
        led = ledger()
        if drawn['topic'] in before:
            led['entries'][drawn['topic']] = before[drawn['topic']]
        else:
            led['entries'].pop(drawn['topic'], None)
        save_ledger(led)
        # Brief chỉ có nghĩa khi job tồn tại; để lại sẽ chặn lần start sau của cùng mã job.
        Path(drawn['brief']).unlink(missing_ok=True)
        raise Stop('pilot new thất bại, đã trả chủ đề về kho:\n' + (run.stdout or run.stderr).strip())
    return {**drawn, 'pilot': json.loads(run.stdout)}


def next_job_id(prefix, taken):
    """Mã job kế tiếp dạng prefix + số, bỏ qua mã đã có trong runs/ và trong ledger."""
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


def cmd_mark(args):
    """Đánh dấu đã làm video. Mặc định chỉ chấp nhận job có video đã duyệt."""
    led = ledger()
    ids = {x['id'] for x in topics()}
    if args.id:
        targets = [e for e in args.id.split(',') if e]
        unknown = [e for e in targets if e not in ids]
        if unknown:
            raise Stop('Mã chủ đề không có trong kho: ' + ', '.join(unknown))
    else:
        targets = [k for k, v in led['entries'].items() if v.get('job') == args.job]
        if not targets:
            raise Stop(f'Job {args.job} chưa giữ chỗ chủ đề nào; dùng --id để đánh dấu thủ công')
    if args.job and not args.force:
        if not approved_video(args.job):
            raise Stop(f'Job {args.job} chưa có video được duyệt. Duyệt xong hãy mark, '
                       f'hoặc --force kèm --note nếu video làm ngoài pipeline.')
    if args.force and not args.note.strip():
        raise Stop('--force cần --note ghi lý do và nơi video đã phát hành')
    for topic_id in targets:
        record = dict(led['entries'].get(topic_id, {}))
        record.update({'status': 'done', 'at': stamp()})
        if args.job:
            record['job'] = args.job
        if args.note.strip():
            record['note'] = args.note.strip()
        if args.video:
            record['video'] = args.video
        led['entries'][topic_id] = record
    save_ledger(led)
    return {'marked': targets, 'job': args.job, 'done': cmd_status(args)['done']}


def brief_topic(job):
    """Mã chủ đề trong kho mà brief của job đang dùng, None nếu brief không sinh từ kho."""
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
    ids = {x['id'] for x in topics()}
    runs = REPO / 'runs'
    jobs = sorted(x.name for x in runs.iterdir() if x.is_dir()) if runs.is_dir() else []
    outside, unmarked, unknown, linked = [], [], [], []
    for job in jobs:
        topic_id = brief_topic(job)
        if topic_id is None:
            outside.append(job)
            continue
        if topic_id not in ids:
            unknown.append({'job': job, 'topic': topic_id})
            continue
        linked.append({'job': job, 'topic': topic_id, 'status': state_of(led, topic_id)})
        if state_of(led, topic_id) != 'done' and approved_video(job):
            unmarked.append({'job': job, 'topic': topic_id})
    missing = [{'topic': k, 'job': v.get('job')} for k, v in led['entries'].items()
               if v.get('job') and v['job'] not in jobs]
    return {'jobs': len(jobs), 'linked': linked, 'outside_bank': outside,
            'topic_not_in_bank': unknown, 'approved_but_unmarked': unmarked,
            'ledger_job_missing': missing,
            'fix': 'Job ngoài kho: tạo bằng `bank.py start`. Video đã duyệt: chạy `bank.py mark JOB`.'}


COMMANDS = {'status': cmd_status, 'next': cmd_next, 'start': cmd_start,
            'mark': cmd_mark, 'queue': cmd_queue, 'audit': cmd_audit}


def main():
    ap = argparse.ArgumentParser(description='Kho chủ đề cho kênh giải thích tiền sử/sinh tồn')
    ap.add_argument('command', choices=sorted(COMMANDS))
    ap.add_argument('job', nargs='?', help='mã job của pilot (start/mark)')
    ap.add_argument('--count', type=int, default=5)
    ap.add_argument('--tag', help='lọc theo tags của chủ đề, cách nhau bằng dấu phẩy')
    ap.add_argument('--id', help='ép chọn đúng một chủ đề (start) hoặc đánh dấu thủ công (mark), '
                                  'cách nhau bằng dấu phẩy khi dùng với mark')
    ap.add_argument('--out', help='đường dẫn brief hoặc hàng đợi cần ghi')
    ap.add_argument('--mode', choices=['review', 'auto'], default='review')
    ap.add_argument('--style')
    ap.add_argument('--tone')
    ap.add_argument('--video', help='đường dẫn hoặc link video đã phát hành')
    ap.add_argument('--note', default='')
    ap.add_argument('--force', action='store_true', help='mark cho video làm ngoài pipeline')
    ap.add_argument('--prefix', default='tiensu-', help='tiền tố mã job cho lệnh queue')
    ap.add_argument('--redo', action='store_true', help='làm lại một chủ đề đã có video; cần --id')
    args = ap.parse_args()
    if args.command in ('start',) and not args.job:
        raise Stop(f'Lệnh {args.command} cần mã job')
    if args.command == 'mark' and not (args.job or args.id):
        raise Stop('mark cần mã job hoặc --id')
    with ledger_lock() if args.command in WRITERS else contextlib.nullcontext():
        result = COMMANDS[args.command](args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Stop as ex:
        print(json.dumps({'blocked': str(ex)}, ensure_ascii=False, indent=2))
        sys.exit(2)
