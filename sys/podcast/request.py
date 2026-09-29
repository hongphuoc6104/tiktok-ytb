"""Map an AI request ID to one durable episode without duplicate reservations."""
from __future__ import annotations
import fcntl
import hashlib
import json
import uuid
from .coordinator import Coordinator, EpisodeError, _atomic_json


def prepare_request(coordinator: Coordinator, request_id: str, topic: str | None = None, minutes: float = 25):
    if not isinstance(request_id, str) or not request_id.strip() or len(request_id) > 256:
        raise EpisodeError('Request ID cần có 1–256 ký tự.')
    if not 20 <= minutes <= 30:
        raise EpisodeError("Thời lượng podcast phải nằm trong 20–30 phút.")
    topic = topic.strip() if topic else None
    directory = coordinator.sys_root / 'podcast' / 'requests'
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(request_id.encode()).hexdigest()
    path = directory / f'{key}.json'
    with (directory / 'create.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            record = json.loads(path.read_text())
            if record['requested_topic'] != topic or record.get('minutes', 25) != minutes:
                raise EpisodeError('Request ID đã dùng cho chủ đề khác.')
        else:
            selected = None
            if not topic:
                candidates = coordinator.next_topics(5)
                if not candidates:
                    raise EpisodeError('Catalog đã hết chủ đề khả dụng; cần bổ sung đề tài.')
                selected = candidates[0]
                selected = coordinator.show_topic(selected['id'])['topic']
            record = {'request_id': request_id, 'requested_topic': topic, 'minutes': minutes,
                      'episode_id': 'podcast-' + uuid.uuid4().hex[:16],
                      'topic_id': selected['id'] if selected else None,
                      'topic': selected['title'] if selected else topic}
            _atomic_json(path, record)
        episode_id = record['episode_id']
        manifest_path = coordinator.episode_dir(episode_id) / 'podcast_manifest.json'
        if manifest_path.exists():
            manifest = coordinator.get_manifest(episode_id)
            if manifest['topic'] != record['topic'] or manifest.get('topic_id') != record['topic_id']:
                raise EpisodeError('Episode không khớp yêu cầu đã lưu.')
            return manifest
        if record['topic_id']:
            selected = coordinator.show_topic(record['topic_id'])
            reservation = selected.get('reservation')
            if not reservation or reservation.get('episode_id') != episode_id:
                coordinator.reserve_topic(record['topic_id'], episode_id)
            return coordinator.start_reserved(episode_id, brief_overrides={"target_minutes": minutes})
        return coordinator.create_episode(topic=record['topic'], episode_id=episode_id, brief={'target_minutes': minutes})
