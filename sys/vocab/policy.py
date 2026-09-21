#!/usr/bin/env python3
"""Chính sách brief của kênh học từ vựng, cắm vào pilot qua config.brief_policies.

Bộ điều phối không biết kênh này dạy gì; toàn bộ hiểu biết về từ vựng nằm ở đây.
Luật: job dạy từ vựng phải rút từ kho `vocab/bank.py`, không viết brief bằng tay.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vocab import bank

# Brief nào bị coi là dạy từ vựng. Giữ ở đây để sửa không cần đụng bộ điều phối.
SIGNALS = ('từ vựng', 'tu vung', 'vocabulary', 'học từ ', 'word of the day')
HINT = ('Job dạy từ vựng phải rút từ kho: python3 vocab/bank.py start {job}\n'
        '  (xem danh sách: python3 vocab/bank.py next --count 10; tài liệu: docs/vocabulary.md)')


class PolicyError(Exception):
    """Dùng lại Blocked của pilot khi được gọi trong pilot; ngoài pilot vẫn nêu rõ lý do."""


def teaches_vocabulary(brief):
    text = ' '.join(str(brief.get(k, '')) for k in ('topic', 'goal', 'video_type')).lower()
    return any(signal in text for signal in SIGNALS)


def check(root, job, brief):
    entry_id = None
    for line in brief.get('planning', {}).get('domain_requirements', []):
        if line.startswith(bank.ENTRY_TAG):
            entry_id = line[len(bank.ENTRY_TAG):].split(' (')[0].strip()
            break
    if entry_id is None:
        if teaches_vocabulary(brief):
            fail(HINT.format(job=job))
        return
    entry = next((x for x in bank.bank() if x['id'] == entry_id), None)
    if entry is None:
        fail(f'Mã mục {entry_id} không có trong kho từ vựng. '
             f'Dựng lại brief bằng: python3 vocab/bank.py start {job}')
    record = bank.ledger()['entries'].get(entry_id, {})
    if record.get('job') != job:
        holder = record.get('job')
        fail(f'Mục {entry_id} chưa được giữ chỗ cho job {job}'
             + (f' (đang thuộc job {holder})' if holder else '')
             + f'. Dùng: python3 vocab/bank.py draw {job} --word {entry["word"]}')
    if record.get('status') == 'done' and record.get('job') != job:
        fail(f'Từ {entry["word"]} ({entry_id}) đã có video ở job {record["job"]}')


def fail(message):
    try:
        from pilot import Blocked
    except ImportError:
        raise PolicyError(message) from None
    raise Blocked(message)
