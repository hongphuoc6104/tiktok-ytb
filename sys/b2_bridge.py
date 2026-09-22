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


def query_status() -> dict:
    return send_raw_command("status", timeout=5.0)


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
    timeout: float = 120.0
) -> dict:
    """Generate image via B-2 Illustrator applet and harvest committed result."""
    require_queue_acceptance()
    ensure_connected()

    canonical_mascot = (ROOT / "assets/characters/channel-mascot/reference-v1.png").resolve()
    if char_ref_path is None and canonical_mascot.exists():
        char_ref_path = canonical_mascot
        char_media_id = char_media_id or "de94a39b-155f-4afe-acbb-d9d4b59ad532"

    target_dir = Path(out_dir).resolve() if out_dir else (ROOT / "experiments/b2_illustrator/results/controller").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    char_guidance = (
        " Strict Stickman CH01 canonical anatomy: exactly ONE single torso wearing plain light ocean blue shirt #8CCFE8, "
        "exactly two simple navy stick arms, two simple navy stick legs, round white head with dark navy contour, "
        "two solid black vertical oval eyes, simple open smile with coral tongue, absolutely NO eyebrows, NO teeth, NO white anime pupils. "
        "Maintain identical camera perspective, framing, and furniture structure from the reference."
    )
    enhanced_prompt = prompt if "Stickman CH01" in prompt else (prompt + "\n" + char_guidance)

    spec = {
        "testCase": test_case,
        "testName": f"Pipeline B-2 Generation: {test_case}",
        "prompt": enhanced_prompt,
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
    require_queue_acceptance()
    ensure_connected()
    if not 1 <= len(specs) <= 4:
        raise Blocked("B-2 queue requires one to four independent requests")
    folder = ROOT / "experiments/b2_illustrator/results/controller"
    folder.mkdir(parents=True, exist_ok=True)
    import uuid
    manifest = folder / f"queue-{uuid.uuid4().hex}.json"
    manifest.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    result = send_raw_command(f"tool-snapshot:queue:{manifest}", timeout=max(timeout, 240))
    if result.get("status") == "blocked":
        error = Blocked(result.get("reason", "B-2 queue blocked"))
        error.generation_submitted = result.get("generationSubmitted", True)
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
