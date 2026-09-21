#!/usr/bin/env python3
"""Read-only assessment harness for the B-2 Illustrator Flow tool.

The module is intentionally conservative: it can inspect local configuration
and non-secret Chrome profile metadata, but it cannot submit a Flow generation.
Live UI evidence must be collected separately through the user's connected
browser session and must never be inferred from this module's output.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


MODULE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_ROOT.parents[1]
DEFAULT_CONFIG = MODULE_ROOT / "config.json"
PRODUCTION_DIR_NAMES = ("runs", "exports", ".state", "revisions", "reviews")
UNKNOWN = None


class AssessmentError(RuntimeError):
    """A fail-closed configuration or safety error."""


def _resolve_from_module(value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (MODULE_ROOT / path).resolve()


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise AssessmentError("config must be a JSON object")
    return config


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_output_dir(config: dict[str, Any], output_override: str | None = None) -> Path:
    requested = output_override or config.get("output_dir", "results")
    output_dir = _resolve_from_module(requested)
    allowed_root = (MODULE_ROOT / "results").resolve()
    if not _is_inside(output_dir, allowed_root):
        raise AssessmentError(
            f"output must stay under {allowed_root}; refused {output_dir}"
        )
    for name in PRODUCTION_DIR_NAMES:
        production_root = (PROJECT_ROOT / name).resolve()
        if _is_inside(output_dir, production_root):
            raise AssessmentError(
                f"production output path is forbidden: {output_dir}"
            )
    return output_dir


def inspect_profile(config: dict[str, Any]) -> dict[str, Any]:
    chrome = config.get("chrome") or {}
    user_data_dir = _resolve_from_module(chrome.get("user_data_dir", ""))
    profile_directory = str(chrome.get("profile_directory", ""))
    if not profile_directory:
        raise AssessmentError("chrome.profile_directory is required")

    local_state = user_data_dir / "Local State"
    profile_path = user_data_dir / profile_directory
    state_exists = local_state.is_file()
    profile_exists = profile_path.is_dir()
    # Only read the profile index. Cookies, Login Data and session files are
    # deliberately never opened or copied.
    selected: dict[str, Any] = {}
    if state_exists:
        try:
            state = json.loads(local_state.read_text(encoding="utf-8"))
            selected = (
                state.get("profile", {})
                .get("info_cache", {})
                .get(profile_directory, {})
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise AssessmentError(f"cannot read profile metadata: {exc}") from exc

    return {
        "user_data_dir": str(user_data_dir),
        "profile_directory": profile_directory,
        "user_data_dir_exists": user_data_dir.is_dir(),
        "local_state_exists": state_exists,
        "profile_directory_exists": profile_exists,
        "candidate_account_name": selected.get("user_name") or None,
        "candidate_display_name": selected.get("gaia_name") or selected.get("name") or None,
        "ui_account_confirmed": False,
        "secret_files_read": False,
    }


def validate_config(config: dict[str, Any], output_override: str | None = None) -> Path:
    if config.get("mode") != "dry-run":
        raise AssessmentError("mode must remain dry-run in the isolated scaffold")
    if (config.get("tool") or {}).get("identity_verified") is not False:
        raise AssessmentError("tool identity must remain unverified until live UI inspection")
    flow = config.get("flow") or {}
    if flow.get("credit_budget") != 0:
        raise AssessmentError("credit_budget must be 0")
    if flow.get("model") != "Nano Banana Pro":
        raise AssessmentError("model must remain Nano Banana Pro")
    if not flow.get("project"):
        raise AssessmentError("Flow project is required")
    budget = config.get("experiment_budget") or {}
    if budget.get("scope") != "B-2 Illustrator only":
        raise AssessmentError("experiment budget must be scoped to B-2 Illustrator only")
    if budget.get("max_credits") != 1050:
        raise AssessmentError("isolated B-2 experiment budget must be capped at 1050 credits")
    if budget.get("spent_credits") is not None or budget.get("spend_status") != "unknown":
        raise AssessmentError("credit spend is unknown until live evidence is recorded")
    if budget.get("tracking_required") is not True or budget.get("allow_generation") is not False:
        raise AssessmentError("generation remains disabled until a reviewed spend tracker exists")
    validate_output_dir(config, output_override)
    return validate_output_dir(config, output_override)


def build_plan(config: dict[str, Any], output_override: str | None = None) -> dict[str, Any]:
    output_dir = validate_config(config, output_override)
    profile = inspect_profile(config)
    flow = config["flow"]
    tool = config["tool"]
    capabilities = {
        name: UNKNOWN for name in config.get("capabilities_to_verify", [])
    }
    return {
        "schema_version": "b2-assessment-1",
        "observed_at": int(time.time()),
        "observation_type": "offline-profile-metadata",
        "read_only": True,
        "generation_submitted": False,
        "tool": {
            "name": tool.get("name"),
            "source": tool.get("source"),
            "version": tool.get("version"),
            "identity_verified": False,
        },
        "flow_constraints": {
            "model": flow["model"],
            "project": flow["project"],
            "credit_budget": flow["credit_budget"],
            "outputs": flow.get("outputs"),
            "ratios": flow.get("ratios", []),
            "live_ui_required": True,
        },
        "experiment_budget": {
            "scope": config["experiment_budget"]["scope"],
            "max_credits": config["experiment_budget"]["max_credits"],
            "spent_credits": None,
            "spend_status": "unknown",
            "tracking_required": True,
            "generation_enabled": False,
        },
        "chrome_profile": profile,
        "output_dir": str(output_dir),
        "capabilities": capabilities,
        "next_action": "inspect B-2 card and remix UI in the connected user-owned Chrome session",
    }


def record_plan(plan: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "dry-run-plan.json"
    destination.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    inspect = sub.add_parser("inspect", help="build a read-only offline assessment plan")
    inspect.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    inspect.add_argument("--format", choices=("text", "json"), default="text")
    inspect.add_argument("--record", action="store_true", help="write the plan under results/")
    inspect.add_argument("--output-dir", help="must remain under experiments/b2_illustrator/results/")
    return parser


def main(argv: list[str] | None = None) -> int:
    # A real CLI invocation must honor sys.argv; the explicit fallback keeps
    # `main([])` useful for an offline smoke call in a Python process.
    if argv is None:
        argv = sys.argv[1:]
    args = _parser().parse_args(argv or ["inspect"])
    if args.command in (None, "inspect"):
        try:
            config = load_config(args.config)
            plan = build_plan(config, args.output_dir)
            if args.record:
                destination = record_plan(plan, Path(plan["output_dir"]))
                plan["recorded_to"] = str(destination)
            if args.format == "json":
                print(json.dumps(plan, ensure_ascii=False, indent=2))
            else:
                print("B-2 Illustrator isolated assessment (read-only)")
                print(f"Profile candidate: {plan['chrome_profile']['profile_directory']} / {plan['chrome_profile']['candidate_account_name'] or 'unknown'}")
                print(f"Flow constraints: {plan['flow_constraints']['model']} / {plan['flow_constraints']['project']} / credit budget {plan['flow_constraints']['credit_budget']}")
                print("Tool identity and live capabilities: unverified")
                print("Generation submitted: no")
                if args.record:
                    print(f"Recorded dry-run plan: {plan['recorded_to']}")
            return 0
        except (AssessmentError, OSError, json.JSONDecodeError) as exc:
            print(f"B2_ASSESSMENT_BLOCKED: {exc}", file=sys.stderr)
            return 2
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
