"""Python bridge for B-2 Illustrator session communication over Unix domain socket."""
import json
import os
import socket
import time
from pathlib import Path
from pilot import Blocked, digest

ROOT = Path(__file__).resolve().parent
SOCKET_PATH = ROOT / "experiments/b2_illustrator/results/controller/session.sock"


def get_socket_path() -> Path:
    return SOCKET_PATH


def is_session_available() -> bool:
    if not SOCKET_PATH.exists():
        return False
    try:
        res = query_status()
        return res.get("status") == "connected"
    except Exception:
        return False


def _config() -> dict:
    try:
        return json.loads((ROOT / "config.json").read_text())
    except Exception:
        return {}


def _mark_not_submitted(exc: Blocked) -> Blocked:
    """Tag a pre-submission failure so it is never treated as an unresolved
    (ambiguous) Flow submission by callers (image_pipeline.request()/
    batch_submit(), adapters.gflow()'s 'batch' handler). Everything wrapped
    with this -- the queue-acceptance gate, session status/connect, batch
    shape checks -- runs strictly before the one socket call that can ever
    reach Flow's queue ("tool-snapshot:queue:..."), so a failure here proves
    nothing was submitted and the caller is free to retry without a costly
    manual flow-reconcile.
    """
    if getattr(exc, "generation_submitted", None) is None:
        exc.generation_submitted = False
    return exc


def send_raw_command(command: str, timeout: float = 120.0) -> dict:
    if not SOCKET_PATH.exists():
        raise Blocked(
            f"B-2 Illustrator session socket not found at {SOCKET_PATH}. "
            "Ensure b2-session service is running (e.g. systemctl --user start b2-session.service)."
        )
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(str(SOCKET_PATH))
        payload = (command.strip() + "\n").encode("utf-8")
        client.sendall(payload)
        
        response_chunks = []
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            response_chunks.append(chunk)
            if b"\n" in chunk:
                break
        
        response_text = b"".join(response_chunks).decode("utf-8").strip()
        if not response_text:
            raise Blocked("Empty response from B-2 Illustrator session socket")
        return json.loads(response_text)
    except socket.timeout:
        raise Blocked(f"B-2 Illustrator session command timed out after {timeout}s: {command[:50]}")
    except (json.JSONDecodeError, OSError) as exc:
        raise Blocked(f"B-2 Illustrator session communication error: {exc}")
    finally:
        client.close()


def query_status(timeout: float | None = None) -> dict:
    """Read-only session probe. session.mjs answers 'status' immediately
    (it never waits behind a queued tool-snapshot/connect command), but the
    daemon itself can still be mid-restart or cold-starting its browser
    connection, so a couple of retries with backoff are cheap insurance
    against a false timeout -- nothing here ever reaches Flow.
    """
    cfg = _config()
    timeout = timeout if timeout is not None else cfg.get("flow_status_timeout_seconds", 30.0)
    retries = cfg.get("flow_status_retries", 2)
    backoff = cfg.get("flow_status_backoff_seconds", 2.0)
    last_exc: Blocked | None = None
    for attempt in range(retries + 1):
        try:
            return send_raw_command("status", timeout=timeout)
        except Blocked as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
    raise last_exc


def ensure_connected() -> dict:
    status = query_status()
    if status.get("status") == "connected":
        return status
    result = send_raw_command("connect", timeout=75.0)
    if result.get("status") != "connected":
        raise Blocked(f"B-2 connection blocked: {result.get('reason', 'not connected')}")
    return result


def generate_b2_image(
    prompt: str,
    ratio: str = "16:9",
    base_ref_path: str | Path | None = None,
    char_ref_path: str | Path | None = None,
    base_media_id: str | None = None,
    char_media_id: str | None = None,
    preserve: str = "",
    change: str = "",
    literal_text: str = "",
    out_dir: str | Path | None = None,
    test_case: str = "SCENE",
    timeout: float = 120.0,
    collection_only: bool = False,
) -> dict:
    """Generate image via B-2 Illustrator applet and harvest committed result."""
    try:
        require_queue_acceptance()
        ensure_connected()
    except Blocked as exc:
        _mark_not_submitted(exc)
        raise

    canonical_mascot = (ROOT / "assets/characters/channel-mascot/reference-v1.png").resolve()
    if char_ref_path is None and canonical_mascot.exists():
        char_ref_path = canonical_mascot
        char_media_id = char_media_id or "de94a39b-155f-4afe-acbb-d9d4b59ad532"

    target_dir = Path(out_dir).resolve() if out_dir else (ROOT / "experiments/b2_illustrator/results/controller").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    spec = {
        "testCase": test_case,
        "testName": f"Pipeline B-2 Generation: {test_case}",
        "prompt": prompt,
        "collectionOnly": collection_only,
        "preserve": preserve,
        "change": change,
        "literalText": literal_text,
        "ratio": ratio,
        "outDir": str(target_dir),
        "baseRefPath": str(Path(base_ref_path).resolve()) if base_ref_path else None,
        "characterRefPath": str(Path(char_ref_path).resolve()) if char_ref_path else None,
        "baseMediaId": base_media_id,
        "charMediaId": char_media_id,
    }

    spec_file = target_dir / f".spec-{test_case}-{int(time.time() * 1000)}.json"
    spec_file.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    return generate_b2_batch([spec], timeout=timeout)[0]


def generate_b2_batch(specs: list[dict], timeout: float = 240.0) -> list[dict]:
    """Submit immutable groups through the persistent queue UI adapter."""
    try:
        require_queue_acceptance()
        ensure_connected()
        if not 1 <= len(specs) <= 4:
            raise Blocked("B-2 queue requires one to four independent requests")
        for spec in specs:
            # Same check queue-runner.mjs's prepareRequests() makes on the
            # Node side (REFERENCE_MEDIA_ID_REQUIRED there), but done here,
            # before the socket call, so a missing media id (e.g. a base
            # image reconciled/collected without a forgeId sidecar) is a
            # clean, retryable, pre-submit failure instead of an ambiguous
            # one discovered mid-flight inside Flow's queue.
            if spec.get("characterRefPath") and not spec.get("charMediaId"):
                raise Blocked("REFERENCE_MEDIA_ID_REQUIRED: characterRefPath thiếu charMediaId tương ứng")
            if spec.get("baseRefPath") and not spec.get("baseMediaId"):
                raise Blocked("REFERENCE_MEDIA_ID_REQUIRED: baseRefPath thiếu baseMediaId (thiếu sidecar .json chứa forgeId)")
        folder = ROOT / "experiments/b2_illustrator/results/controller"
        folder.mkdir(parents=True, exist_ok=True)
        import uuid
        manifest = folder / f"queue-{uuid.uuid4().hex}.json"
        manifest.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    except Blocked as exc:
        _mark_not_submitted(exc)
        raise
    result = send_raw_command(f"tool-snapshot:queue:{manifest}", timeout=max(timeout, 240))
    if result.get("status") == "blocked":
        error = Blocked(result.get("reason", "B-2 queue blocked"))
        error.generation_submitted = result.get("generationSubmitted", True)
        error.collection_only = result.get("collectionOnly", False)
        error.attempt_states = result.get("attemptStates", [])
        raise error
    items = result.get("items", [])
    if len(items) != len(specs):
        raise Blocked("B-2 incomplete batch; reconcile before retry")
    for spec, item in zip(specs, items):
        if item.get("request_id") != spec["testCase"] or not Path(item["path"]).is_file():
            raise Blocked("B-2 result mapping failed")
        item["sha256"] = digest(Path(item["path"]))
    return items


def require_queue_acceptance():
    record = json.loads((ROOT / "experiments/b2_illustrator/acceptance.json").read_text())
    config = json.loads((ROOT / "config.json").read_text())
    if record.get("production_ready") is not True and config.get("flow_queue_trial_enabled") is not True:
        raise Blocked("B2_QUEUE_NOT_ACCEPTED: see docs/flow-queue-operations.md; production remains blocked")
