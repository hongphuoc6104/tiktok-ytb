#!/usr/bin/env python3
"""Rehearse real `agy` content-v3 generation in an isolated sandbox copy of the repo.

This is a diagnostic tool, not part of the production pipeline. It never creates a
job under this repository's own `runs/` (that directory is production state and must
not be touched by a rehearsal). Instead it copies the protected implementation files
(the same set `pilot.Pilot.protected()` hashes for integrity: schemas/, .agents/,
renderer/, tests/, examples/, scripts/, and the top-level pipeline .py/.json/.md
files) into a fresh sandbox directory, creates a job there from a brief-v3 file, and
calls the *real* `scripts.agy_pipeline.generate()` against the real `agy` CLI to see:

  - whether the outline turn passes agy_pipeline's structural checks (scene
    count/order, requirement coverage) on the first try, and if not, how many
    attempts it takes;
  - whether the detailed content-v3 turn passes content_contract.validate_content
    (including the vi/en anchor and quote/quote_en checks), and how many attempts;
  - timing and token usage for every real `agy` call made along the way.

Regeneration between attempts uses the same mechanism agy_pipeline.generate() itself
allows: while content is 'pending'/'blocked'/'needs_changes'/'stale' it can simply be
re-run. Nothing here hand-edits a draft to make it pass. Nothing here approves,
rejects, or judges semantic quality automatically -- that assessment is done by a
human/agent reading the saved artifacts afterward.

Usage:
    python3 scripts/rehearse_content.py run --brief /path/to/brief-v3.json \\
        --job rehearsal-01 --sandbox-root /path/to/scratch/sandbox \\
        --max-attempts 3 --publish-dir examples/rehearsal
"""
import argparse
import copy
import json
import shutil
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PROTECTED_DIRS = ['schemas', '.agents', 'renderer', 'tests', 'examples', 'scripts']
PROTECTED_FILES = [
    'pilot.py', 'workflow.py', 'machine_review.py', 'content_contract.py',
    'image_pipeline.py', 'prompt_templates.py', 'adapters.py', 'tts_worker.py',
    'config.json', 'AGENTS.md', 'GEMINI.md', 'package.json', 'package-lock.json',
    'requirements.txt', 'tts-requirements.lock', 'en-requirements.lock',
]


class RehearsalError(Exception):
    pass


def guard_sandbox_root(root: Path) -> Path:
    """Refuse any sandbox root that overlaps the real repository in any way."""
    root = root.resolve()
    repo = REPO_ROOT.resolve()
    if repo.name == "sys" and (repo.parent / "pilot.py").is_file():
        repo = repo.parent
    if root == repo:
        raise RehearsalError(f'Refusing to sandbox at the real repo root: {repo}')
    if repo in root.parents:
        raise RehearsalError(f'Sandbox root {root} is inside the real repository {repo}')
    if root in repo.parents:
        raise RehearsalError(f'Sandbox root {root} is an ancestor of the real repository {repo}')
    if str(root) == str(repo / 'runs') or (repo / 'runs') in root.parents:
        raise RehearsalError('Refusing to use runs/ of the real repository')
    return root


def build_sandbox(sandbox_root: Path) -> Path:
    sandbox_root = guard_sandbox_root(sandbox_root)
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    sandbox_root.mkdir(parents=True)
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    for name in PROTECTED_DIRS:
        src = REPO_ROOT / name
        if src.exists():
            shutil.copytree(src, sandbox_root / name, ignore=ignore)
    for name in PROTECTED_FILES:
        src = REPO_ROOT / name
        if src.exists():
            shutil.copy(src, sandbox_root / name)
    return sandbox_root


def load_sandbox_modules(sandbox_root: Path):
    """Import pilot/workflow/agy_pipeline etc. from the sandbox copy, not the real repo.

    Any previously-imported copies of these modules (e.g. from a prior call in the
    same process) are dropped first so every import resolves under sandbox_root.
    """
    sandbox_root = str(sandbox_root.resolve())
    # Drop stale sys.path entries that point at the real repo's own scripts/ dir
    # (Python auto-inserts the running script's directory at sys.path[0]).
    sys.path = [p for p in sys.path if Path(p).resolve() != (REPO_ROOT / 'scripts').resolve()]
    if sandbox_root not in sys.path:
        sys.path.insert(0, sandbox_root)
    for name in list(sys.modules):
        if name in ('pilot', 'workflow', 'content_contract', 'image_pipeline', 'adapters') or name.split('.')[0] == 'scripts':
            del sys.modules[name]
    import pilot  # noqa
    import workflow  # noqa
    from scripts import agy_pipeline  # noqa
    return pilot, workflow, agy_pipeline


def instrument_invoke(agy_pipeline, calls_log):
    """Wrap agy_pipeline.invoke to record timing/tokens for every real agy call,
    without altering agy_pipeline.py on disk or changing what it does."""
    original = agy_pipeline.invoke

    def wrapped(prompt, schema, workspace, conversation=None, timeout=180):
        record = {
            'call_index': len(calls_log) + 1,
            'prompt_chars': len(prompt),
            'schema_top_level_keys': sorted(schema.get('properties', {}).keys()) if isinstance(schema, dict) else None,
            'conversation_reused': bool(conversation),
            'wall_started_at': time.time(),
        }
        try:
            result = original(prompt, schema, workspace, conversation, timeout)
            record['ok'] = True
            record['status'] = result.get('status')
            record['agy_duration_seconds'] = result.get('duration_seconds')
            record['usage'] = result.get('usage')
            record['conversation_id'] = result.get('conversation_id')
            return result
        except Exception as ex:
            record['ok'] = False
            record['error'] = str(ex)
            raise
        finally:
            record['wall_seconds'] = round(time.time() - record['wall_started_at'], 3)
            calls_log.append(record)

    agy_pipeline.invoke = wrapped
    return original


def retryable_states(rows_row_state: str) -> bool:
    return rows_row_state in ('pending', 'needs_changes', 'blocked', 'stale')


def run_rehearsal(brief_path: Path, job_id: str, sandbox_root: Path, max_attempts: int,
                   publish_dir: Path, raw_log_dir: Path):
    brief = json.loads(Path(brief_path).read_text())
    if brief.get('aspect_ratio') not in ('9:16', '16:9', 'dual'):
        raise RehearsalError('Brief aspect_ratio must be 9:16, 16:9 or dual')

    sandbox_root = build_sandbox(sandbox_root)
    pilot, workflow, agy_pipeline = load_sandbox_modules(sandbox_root)

    calls_log = []
    instrument_invoke(agy_pipeline, calls_log)

    raw_log_dir.mkdir(parents=True, exist_ok=True)
    report = {
        'job': job_id,
        'sandbox_root': str(sandbox_root),
        'brief_path': str(brief_path),
        'started_at': time.time(),
        'attempts': [],
        'calls': calls_log,  # same list object; instrument_invoke appends into it live
    }

    with pilot.locked(sandbox_root):
        p = pilot.Pilot(sandbox_root)
        try:
            created = workflow.new(p, job_id, copy.deepcopy(brief), mode='review')
            report['job_created'] = created

            final_ok = False
            for attempt_num in range(1, max_attempts + 1):
                calls_before = len(calls_log)
                attempt_start = time.time()
                entry = {'attempt': attempt_num}
                try:
                    result = agy_pipeline.generate(p, job_id)
                    entry['ok'] = True
                    entry['result'] = result
                    final_ok = True
                except Exception as ex:
                    entry['ok'] = False
                    entry['error'] = str(ex)
                    entry['errors'] = getattr(ex, 'errors', [])
                entry['duration_seconds'] = round(time.time() - attempt_start, 3)
                entry['agy_calls_this_attempt'] = len(calls_log) - calls_before
                entry['content_state_after'] = p.rows(job_id)['content']['state']
                report['attempts'].append(entry)
                if entry['ok']:
                    break
                if not retryable_states(entry['content_state_after']):
                    entry['stopped_reason'] = (
                        f"content state '{entry['content_state_after']}' is not one agy_pipeline.generate() "
                        "will regenerate from without an explicit reject; rehearsal does not fabricate a reject."
                    )
                    break

            report['final_ok'] = final_ok
            report['content_state_final'] = p.rows(job_id)['content']['state']

            # Copy every raw agent-attempts/* directory verbatim for human reading.
            attempts_src = p.job(job_id) / 'agent-attempts'
            if attempts_src.exists():
                dest = raw_log_dir / 'agent-attempts'
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(attempts_src, dest)
                report['raw_agent_attempts_copied_to'] = str(dest)

            if final_ok:
                draft = json.loads((p.job(job_id) / 'draft/content.json').read_text())
                report['final_content_path_in_sandbox'] = str(p.job(job_id) / 'draft/content.json')
                publish_dir.mkdir(parents=True, exist_ok=True)
                (publish_dir / 'brief.json').write_text(json.dumps(brief, ensure_ascii=False, indent=2))
                (publish_dir / 'content.json').write_text(json.dumps(draft, ensure_ascii=False, indent=2))
                (publish_dir / 'outline.json').write_text(json.dumps(draft.get('outline', []), ensure_ascii=False, indent=2))
                report['published_to'] = str(publish_dir)
            else:
                publish_dir.mkdir(parents=True, exist_ok=True)
                (publish_dir / 'brief.json').write_text(json.dumps(brief, ensure_ascii=False, indent=2))
                last_bad = None
                for att in reversed(report['attempts']):
                    if not att['ok']:
                        last_bad = att
                        break
                (publish_dir / 'FAILED.json').write_text(json.dumps({
                    'note': 'All attempts failed content_contract.validate_content or agy_pipeline structural checks. '
                            'No content.json/outline.json published: nothing here passed validation.',
                    'last_attempt': last_bad,
                }, ensure_ascii=False, indent=2))
                report['published_to'] = str(publish_dir) + ' (brief + FAILED.json only; no valid content)'
        finally:
            p.db.close()

    report['finished_at'] = time.time()
    report['total_seconds'] = round(report['finished_at'] - report['started_at'], 3)
    (raw_log_dir / 'rehearsal_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['run'])
    ap.add_argument('--brief', required=True, help='Path to a brief-v3 JSON file')
    ap.add_argument('--job', default='rehearsal-' + uuid.uuid4().hex[:8])
    ap.add_argument('--sandbox-root', required=True, help='Directory OUTSIDE this repo to build the sandbox in')
    ap.add_argument('--max-attempts', type=int, default=3)
    ap.add_argument('--publish-dir', default=str(REPO_ROOT / 'examples/rehearsal'))
    ap.add_argument('--raw-log-dir', default=None, help='Where to copy raw agy attempts + report (default: alongside sandbox root)')
    a = ap.parse_args()
    sandbox_root = Path(a.sandbox_root)
    raw_log_dir = Path(a.raw_log_dir) if a.raw_log_dir else sandbox_root.parent / (sandbox_root.name + '-logs')
    report = run_rehearsal(Path(a.brief), a.job, sandbox_root, a.max_attempts, Path(a.publish_dir), raw_log_dir)
    print(json.dumps({
        'job': report['job'],
        'final_ok': report['final_ok'],
        'attempts_made': len(report['attempts']),
        'agy_calls_made': len(report['calls']),
        'total_seconds': report['total_seconds'],
        'published_to': report['published_to'],
        'raw_log_dir': str(raw_log_dir),
    }, ensure_ascii=False, indent=2))
    sys.exit(0 if report['final_ok'] else 1)


if __name__ == '__main__':
    try:
        main()
    except RehearsalError as ex:
        print(json.dumps({'refused': str(ex)}, ensure_ascii=False))
        sys.exit(3)
