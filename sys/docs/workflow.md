# Engine 4 production workflow

Content → media → video are data groups. The five main outputs are **outline → dialogue → audio → images → video**. Engine 4 is the default for `pilot.py new`; `--engine 3` is historical compatibility. Content schema 3 does not imply engine 3.

Read language, aspect ratio, subtitles and voice/rate from `brief.outputs` and the job snapshot. English 9:16 uses English tracks; never infer language from aspect ratio. Channel direction comes from `vocab/channel.json`; craft guidance comes from vp-production/references.

## Create and execute

Commands run from `sys/` with a management interpreter containing required dependencies. `JOB`, `N`, `ID` and example source text below are replaceable parameters, never actual authorization or approval.

- `pilot.py new JOB --brief PATH --mode auto|review --source TEXT`: record the assigned scope and overall plan before execution; reuse `--grant ID` when one exists. Vocabulary videos start through `vocab/bank.py start`, never a handwritten out-of-bank brief.
- `pilot.py observe JOB` / `next JOB`: read state, plans, outputs and the next action. Observation neither creates/refreshes jobs nor takes a writer lease.
- `pilot.py author JOB outline --data PATH --source TEXT`, then `run JOB`; use `author JOB dialogue` for detailed narration. The coordinator writes to the brief and submits through official tools, with no v3-generator fallback. Auto still needs a connected agent/author to provide drafts; missing authorship cannot be fabricated.
- `pilot.py run JOB` / `resume JOB`: execute ready steps and record dashboard events/artifacts. Colab handles audio, assembly/mastering, timeline, SRT, props and rendering; Flow handles images. Remote failure does not trigger heavy local fallback.

Auto records a plan and executes without a machine reviewer or per-output user clicks. Review waits after outline, dialogue, real WAV, image set and real MP4: `approve JOB PHASE --revision N --note TEXT`, with actual user feedback. Decisions cover only existing artifacts/revisions; user approval commands are not used in auto. Technical checks do not prove perceived quality.

## Repair and recovery

`reject JOB PHASE --revision N --note TEXT` records the actual repair instruction and dependency invalidation. Images support `--image`, `--scene`, `--character`, `--ratio` and `--repair-plan`; see [image repair](image-repair-loops.md). Image changes preserve valid WAV; narration changes refresh dependent audio/video. Never overwrite revision snapshots. Repair an old video on its existing job and bank sense.

`micro-plan JOB --data PATH` records symptom, evidence, error_class, target, input_hash, strategy, success_criteria, rollback and submit_state. `micro-result JOB --fingerprint ID --data PATH` records success/evidence. Identical failed input/strategy/evidence is blocked for diagnosis; progressing repairs have no total attempt cap. Consult issues/docs when needed. Outside production authority, prepare scope/diff before requesting development authority. Unknown/ambiguous requests permit only collection/reconciliation of the original request/account/session, never fresh generation.

## Stop, mode and compatibility

`stop JOB --source TEXT` blocks each new submission while collection remains allowed. Resume or a new chat preserves grant/checkpoint/owner and cannot duplicate runners. Takeover rejects a live previous runner. `mode JOB --mode auto|review --source TEXT` records an explicit mode transition; never edit workflow state directly. `bind-session` changes choices for new work while retaining existing request pins.

Development uses `migrate JOB --grant DEV --production-grant PROD --source TEXT` for v3 migration with snapshots/rollback. `rollback-migration JOB --grant DEV --source TEXT` follows the tool's conditions. `adopt-code JOB --grant DEV --confirm JOB --reason TEXT` accepts only authorized changes without a fake human TTY. Guide/test changes do not blanket-lock v4; incompatible schemas still need migration. [v3 workflow](legacy/workflow.md) is historical only.

## Completion and evidence

Both modes share actual job/version/event data on dashboard/chat. Deliver ready artifacts with job/group/revision/path, verified measurements and observation limits. A provider-generated file not yet collected is not a ready local product. Auto requires collected technically valid files; review additionally requires decisions for the five current outputs. Vocabulary `mark` uses the bank after completion/export verification, never direct ledger edits. Fixtures prove logic only; real Flow/T4/image/audio/MP4 acceptance belongs in [progress evidence](implementation/normalization-progress.md).

For engine 4, `brief.duration` is a planning estimate. Continue from the collected positive, finite WAV duration even when it is outside that range; timeline and video must match the actual audio. Do not retake, add narration, cut content or change voice/rate merely to fit estimated seconds. The reader accepts a hard window only from a source-backed `duration_requirement` explicitly recording the user's requirement; this change does not add a CLI operation for setting that field or alter an existing job contract. Legacy v3 keeps its saved hard duration contract.
