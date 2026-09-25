"""Human choices from the dashboard (decisions.ndjson, fsynced, append-only).

pick        - which variant of a request becomes the scene candidate
regenerate  - the user wants another take (with an optional note)
A pick only chooses the candidate file; media approval still happens through
pilot.py, and a regeneration of a pipeline job still goes through
`pilot.py reject ... --image ...` so the workflow gates are never bypassed.
"""
import time

from .store import append_ndjson, read_ndjson

KINDS = ('pick', 'regenerate')


class Decisions:
    def __init__(self, path):
        self.path = path

    def all(self):
        return read_ndjson(self.path, strict=False)

    def record(self, kind, key, request_id, job=None, scene=None, index=None, file=None, note=None):
        if kind not in KINDS:
            raise ValueError(f'unknown decision {kind}')
        if kind == 'pick' and (index is None or not file):
            raise ValueError('pick needs a variant index and file')
        return append_ndjson(self.path, {'kind': kind, 'key': key, 'request_id': request_id, 'job': job, 'scene': scene,
                                         'index': index, 'file': file, 'note': (note or '').strip() or None,
                                         'at': time.time()})

    def latest(self, kind, request_id=None, key=None):
        for e in reversed(self.all()):
            if e.get('kind') == kind and ((request_id and e.get('request_id') == request_id) or (key and e.get('key') == key)):
                return e
        return None

    def choose(self, result):
        """File to use for a FlowPool result: the user's pick if it names one of the
        result's files, else the ranked best, else the first file."""
        pick = self.latest('pick', request_id=result.get('id'), key=result.get('key'))
        files = result.get('files') or []
        if pick and pick.get('file') in files:
            return pick['file'], 'user_pick'
        if result.get('best') in files:
            return result['best'], 'ranked'
        return (files[0], 'first') if files else (None, None)
