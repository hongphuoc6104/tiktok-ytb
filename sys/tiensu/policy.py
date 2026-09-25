#!/usr/bin/env python3
"""Chính sách brief của kênh giải thích tiền sử, cắm vào pilot qua config.brief_policies.

Bộ điều phối không biết kênh này kể chuyện gì; toàn bộ hiểu biết về kho chủ đề nằm ở đây.
Luật: job kênh tiensu phải rút từ kho `tiensu/bank.py`, không viết brief bằng tay.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tiensu import bank

# Brief nào bị coi là thuộc kênh tiền sử khi không có mã chủ đề rõ ràng trong domain_requirements.
SIGNALS = ('tiền sử', 'tien su', 'prehistory', 'người tiền sử', 'thời tiền sử', 'thời đồ đá')
HINT = ('Job kênh tiền sử phải rút từ kho: python3 tiensu/bank.py start {job}\n'
        '  (xem danh sách: python3 tiensu/bank.py next --count 10)')


class PolicyError(Exception):
    """Dùng lại Blocked của pilot khi được gọi trong pilot; ngoài pilot vẫn nêu rõ lý do."""


def is_tiensu_channel(brief):
    if brief.get('channel') == 'tiensu':
        return True
    text = ' '.join(str(brief.get(k, '')) for k in ('topic', 'goal', 'video_type')).lower()
    return any(signal in text for signal in SIGNALS)


def check(root, job, brief):
    topic_id = None
    for line in brief.get('planning', {}).get('domain_requirements', []):
        if line.startswith(bank.ENTRY_TAG):
            topic_id = line[len(bank.ENTRY_TAG):].split(' (')[0].strip()
            break
    if topic_id is None:
        if is_tiensu_channel(brief):
            fail(HINT.format(job=job))
        return
    entry = next((x for x in bank.topics() if x['id'] == topic_id), None)
    if entry is None:
        fail(f'Mã chủ đề {topic_id} không có trong kho tiền sử. '
             f'Dựng lại brief bằng: python3 tiensu/bank.py start {job}')
    record = bank.ledger()['entries'].get(topic_id, {})
    if record.get('job') != job:
        holder = record.get('job')
        fail(f'Chủ đề {topic_id} chưa được giữ chỗ cho job {job}'
             + (f' (đang thuộc job {holder})' if holder else '')
             + f'. Dùng: python3 tiensu/bank.py start {job}')
    if record.get('status') == 'done' and record.get('job') != job:
        fail(f'Chủ đề "{entry["question"]}" ({topic_id}) đã có video ở job {record["job"]}')


def fail(message):
    try:
        from pilot import Blocked
    except ImportError:
        raise PolicyError(message) from None
    raise Blocked(message)
