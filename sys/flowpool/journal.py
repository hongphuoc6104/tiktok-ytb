"""Durable request journal: intent -> submitted -> collected -> validated.

One fsynced ndjson file per request identity. `submitted` is written (and
fsynced) before the only UI action that can start a generation. A journal
that ends in `submitted` when a new run starts is therefore recovered as
`unknown`, and unknown/failed requests are never submitted again unless a
human records a reconciliation (`released`).
"""
import hashlib
import json
import re
import time
from pathlib import Path

from .store import append_ndjson, read_ndjson

STATES = ('intent', 'not_submitted', 'submitted', 'unknown', 'collected', 'validated', 'failed', 'released')
ALLOWED = {
    'intent': {None, 'not_submitted', 'released'},
    'not_submitted': {'intent'},
    'submitted': {'intent'},
    'unknown': {'submitted'},
    'collected': {'submitted', 'unknown'},
    'validated': {'collected'},
    'failed': {'intent', 'submitted', 'unknown', 'collected'},
    'released': {'failed', 'unknown'},
}
UNRESOLVED = ('submitted', 'unknown')
SAFE_ID = re.compile(r'^[\w-]{1,120}$')


class JournalError(Exception):
    def __init__(self, message, code='JOURNAL_ERROR'):
        super().__init__(message)
        self.code = code


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def identity(request):
    """Portable identity of a request: content hashes, never local paths."""
    ident = {
        'id': request['id'], 'kind': request['kind'], 'prompt': request['prompt'],
        'ratio': request['ratio'], 'variants': int(request.get('variants') or 1),
        'model': request.get('model'), 'job': request.get('job'), 'scene': request.get('scene'),
        'refs': [sha256_file(r) for r in request.get('refs') or []],
        'start_frame': sha256_file(request['start_frame']) if request.get('start_frame') else None,
    }
    return ident


def key_for(ident):
    return hashlib.sha256(json.dumps(ident, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


class Journal:
    def __init__(self, directory):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        if not re.fullmatch(r'[a-f0-9]{64}', key or ''):
            raise JournalError('invalid journal key', 'INVALID_KEY')
        return self.dir / f'{key}.ndjson'

    def events(self, key):
        return read_ndjson(self._path(key), strict=False)

    def load(self, key):
        events = self.events(key)
        if not events:
            return None
        snap = {'key': key, 'state': events[-1]['state'], 'events': events,
                'request': events[0].get('request'), 'identity': events[0].get('identity')}
        for e in events:
            for field in ('profile', 'credits_before', 'credits_after', 'queue_ids', 'outputs', 'error', 'code'):
                if field in e:
                    snap[field] = e[field]
        return snap

    def keys(self):
        return sorted(p.stem for p in self.dir.glob('*.ndjson'))

    def all(self):
        return [s for s in (self.load(k) for k in self.keys()) if s]

    def by_request_id(self, request_id):
        return [s for s in self.all() if (s.get('identity') or {}).get('id') == request_id]

    def transition(self, key, state, **payload):
        if state not in STATES:
            raise JournalError(f'unknown state {state}', 'INVALID_STATE')
        current = self.load(key)
        prev = current['state'] if current else None
        if prev not in ALLOWED[state]:
            code = 'UNKNOWN_SUBMISSION' if prev in UNRESOLVED else 'INVALID_TRANSITION'
            raise JournalError(f'cannot move {prev} -> {state}', code)
        if state == 'collected' and prev == 'unknown' and not payload.get('reconciliation'):
            raise JournalError('unknown -> collected requires reconciliation evidence', 'EVIDENCE_REQUIRED')
        if state == 'released' and not payload.get('note'):
            raise JournalError('released requires a human note', 'EVIDENCE_REQUIRED')
        entry = dict(payload, state=state, key=key, seq=len(current['events']) + 1 if current else 1, at=time.time())
        append_ndjson(self._path(key), entry)
        return self.load(key)

    def intent(self, request, ident=None):
        ident = ident or identity(request)
        key = key_for(ident)
        snap = self.load(key)
        if snap and snap['state'] == 'intent':
            return snap
        portable = {k: v for k, v in request.items() if k != 'out_dir'}
        return self.transition(key, 'intent', identity=ident, request=portable)

    def recover(self):
        """Mark every interrupted submission unknown. Call only while holding the run lock."""
        changed = []
        for snap in self.all():
            if snap['state'] == 'submitted':
                self.transition(snap['key'], 'unknown', reason='interrupted-submission', profile=snap.get('profile'))
                changed.append(snap['key'])
        return changed

    def media_lookup(self):
        """sha256 of a FlowPool output -> {profile: media_id}, for dependent requests."""
        found = {}
        for snap in self.all():
            if snap['state'] not in ('collected', 'validated'):
                continue
            for out in snap.get('outputs') or []:
                if out.get('sha256') and out.get('media_id') and snap.get('profile'):
                    found.setdefault(out['sha256'], {})[snap['profile']] = out['media_id']
        return found
