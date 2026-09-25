"""Durable file primitives: fsynced ndjson appends, atomic JSON, process locks."""
import contextlib
import fcntl
import json
import os
import threading
from pathlib import Path

_append_lock = threading.Lock()


def _fsync_dir(path):
    try:
        fd = os.open(str(path), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def append_ndjson(path, entry):
    """Append one JSON line and fsync it before returning."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + '\n'
    with _append_lock:
        new = not path.exists()
        fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, line.encode('utf-8'))
            os.fsync(fd)
        finally:
            os.close(fd)
        if new:
            _fsync_dir(path.parent)
    return entry


def read_ndjson(path, strict=True):
    """Read an ndjson file. A torn last line (crash mid-write) is ignored when
    strict=False and raises otherwise."""
    path = Path(path)
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    out = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            if i == len(lines) - 1 and not strict:
                break
            raise ValueError(f'CORRUPT_NDJSON: {path} line {i + 1}')
    return out


def write_json_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.tmp-{os.getpid()}-{threading.get_ident()}')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    _fsync_dir(path.parent)


@contextlib.contextmanager
def file_lock(path, blocking=True):
    """Exclusive advisory lock (released automatically if the process dies)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, 'a+')
    try:
        flags = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        try:
            fcntl.flock(f.fileno(), flags)
        except BlockingIOError:
            raise RuntimeError(f'FLOWPOOL_LOCKED: another FlowPool process holds {path.name}')
        yield f
    finally:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()
