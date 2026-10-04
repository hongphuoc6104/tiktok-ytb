# Start here — Video Pilot

Read [AGENTS.md](AGENTS.md), identify the task and authority, then select the route:

| Task | Guide | Skill |
|---|---|---|
| Download/clone or configure a machine | [Getting started](sys/docs/getting-started.md) | vp-setup |
| New chat or continuing unfinished work | [Session handoff](sys/docs/session-start.md) | Skill for the ongoing task |
| Create or repair a video | [Workflow](sys/docs/workflow.md) | vp-production |
| Upgrade the system | [Implementation plan](sys/docs/plans/20261003-ke-hoach-chuan-hoa-quyen-mode-va-tai-lieu.md) | vp-development |
| Cleanup/archive/Git synchronization | [Maintenance](sys/docs/maintenance.md) | vp-maintenance |

## Layout

- `sys/`: code, docs, schemas, configuration and operational data.
- `sys/vocab/`: one sense per bank entry; [channel profile](sys/vocab/channel.json).
- `sys/runs/<job>/`: content, versions, requests and artifacts.
- `sys/.state/`: local state; `sys/.gflow/`: browser profiles, excluded from Git.
- `sys/assets/`: visual/voice references; `video/<job>/`: collected products.
- `.agents/`: Rules and four skills; corresponding links in sys point to the root.

The root launcher is `python3 pilot.py`; operational examples use `sys/` as their working directory. Do not infer job/revision from MP4 filenames.

## Upgrade status

Authority/modes/Colab and English portrait direction are being normalized; [progress and evidence](sys/docs/implementation/normalization-progress.md) identify verified capabilities. Do not use v3 auto for the new no-reviewer auto task. Existing jobs migrate only through compatibility-checked tools, never direct state/baseline edits.

[Approved experimental UI](sys/docs/plans/20261003-chot-giao-dien-thu-nghiem.md), [active documentation index](sys/docs/INDEX.md). [Layout migration](sys/docs/layout-migration.md) and [branch synchronization](sys/docs/branch-sync.md) are historical records; their old measurements/tests are not current acceptance evidence.
