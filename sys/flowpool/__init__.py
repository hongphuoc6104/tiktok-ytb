"""FlowPool: Google Flow automation across the user's own signed-in Chrome profiles.

API (tien-su-plan.md section 8):
    flowpool.run(requests, cfg) -> list[result]
    request = {"id", "kind": "image"|"clip", "prompt", "ratio": "16:9"|"9:16",
               "refs": [paths], "start_frame": path (clip), "variants": n,
               "model": str, "job", "scene"}            (+ optional "out_dir")
    result  = {"id", "status": "ok"|"failed"|"unknown", "files": [..], "profile",
               "credits_before", "credits_after", "error"} (+ media_ids, code, key, state)
CLI (from sys/): python3 -m flowpool status|doctor|run --queue FILE
"""
from .pool import FlowPool, run

__all__ = ['FlowPool', 'run']
