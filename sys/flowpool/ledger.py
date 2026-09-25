"""Credit ledger (ledger.ndjson): balances read from the Flow UI, never invented.

Entry types:
  reading     - a balance observed on a profile (doctor, before/after a batch)
  submission  - one request's share of a batch: credits before/after, delta
A null reading stays null; spend is then counted from the configured estimate
and flagged `estimated`.
"""
import statistics
import time
from datetime import datetime

from .store import append_ndjson, read_ndjson


def month_of(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m')


class Ledger:
    def __init__(self, path):
        self.path = path

    def entries(self):
        return read_ndjson(self.path, strict=False)

    def reading(self, profile, credits, raw=None, method=None, at=None):
        return append_ndjson(self.path, {'type': 'reading', 'profile': profile, 'credits': credits,
                                         'raw': raw, 'method': method, 'at': at or time.time()})

    def submission(self, *, profile, kind, model, request_id, key, job, scene, variants,
                   credits_before, credits_after, batch_size, status, estimate=None, at=None):
        delta = None
        if credits_before is not None and credits_after is not None:
            delta = (credits_before - credits_after) / max(1, batch_size)
        return append_ndjson(self.path, {
            'type': 'submission', 'profile': profile, 'kind': kind, 'model': model,
            'request_id': request_id, 'key': key, 'job': job, 'scene': scene, 'variants': variants,
            'credits_before': credits_before, 'credits_after': credits_after, 'batch_size': batch_size,
            'delta': delta, 'estimated_cost': estimate if delta is None else None,
            'status': status, 'at': at or time.time()})

    def balances(self):
        """Latest observed balance per profile: {profile: (credits, at)}."""
        out = {}
        for e in self.entries():
            if e.get('credits') is not None and e['type'] == 'reading':
                out[e['profile']] = (e['credits'], e['at'])
            elif e['type'] == 'submission' and e.get('credits_after') is not None:
                out[e['profile']] = (e['credits_after'], e['at'])
        return out

    def cost_per_clip(self, model, fallback):
        """Median measured credits per generated clip for `model`; fallback estimate otherwise."""
        measured = [e['delta'] / max(1, e.get('variants') or 1) for e in self.entries()
                    if e['type'] == 'submission' and e.get('kind') == 'clip' and e.get('model') == model
                    and e.get('delta') is not None and e['delta'] > 0 and e.get('status') == 'ok']
        if measured:
            return statistics.median(measured), 'measured'
        return fallback, 'estimate'

    def month_spend(self, month=None, kind=None, profile=None):
        """Credits spent this month (optionally for one profile): measured deltas plus
        estimates where the UI gave none. A new month starts from zero."""
        month = month or month_of(time.time())
        total, estimated = 0.0, False
        for e in self.entries():
            if e['type'] != 'submission' or month_of(e['at']) != month or (kind and e.get('kind') != kind):
                continue
            if profile and e.get('profile') != profile:
                continue
            if e.get('delta') is not None:
                total += max(0.0, e['delta'])
            elif e.get('estimated_cost') is not None:
                total += e['estimated_cost']
                estimated = True
        return total, estimated
