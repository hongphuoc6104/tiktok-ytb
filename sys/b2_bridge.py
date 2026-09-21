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
    return send_raw_command("connect", timeout=15.0)


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

    try:
        cmd = f"tool-snapshot:{spec_file}"
        res = send_raw_command(cmd, timeout=timeout)
        if res.get("status") == "blocked":
            raise Blocked(f"B-2 Illustrator blocked: {res.get('reason', 'Unknown reason')}")

        step2 = res.get("step2Execution") or {}
        if not step2.get("generationCompleted"):
            err = step2.get("errorObserved") or "Generation did not complete in frame"
            raise Blocked(f"B-2 Illustrator generation failed: {err}")

        saved_path = step2.get("savedImagePath")
        if not saved_path or not os.path.isfile(saved_path):
            raise Blocked(f"B-2 Illustrator output image not found: {saved_path}")

        image_hash = digest(Path(saved_path))
        return {
            "path": saved_path,
            "sha256": image_hash,
            "forge_id": step2.get("forgeId"),
            "latency": step2.get("latencySeconds"),
            "evidence": res.get("evidence"),
            "technical_validation": step2.get("technicalValidation")
        }
    finally:
        if spec_file.exists():
            spec_file.unlink(missing_ok=True)
