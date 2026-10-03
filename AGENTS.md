# Video Pilot — agent instructions

Read [INDEX.md](INDEX.md). System code/data belong in `sys/`; collected products belong in `video/<job>/`. Do not create operational data at the project root.

## Task and authority

Use one active role per task: setup, production, development or maintenance. Identify the assigned scope and actual authorization source; read the [permission matrix](.agents/rules/permissions.md). Valid grants survive chat changes. Do not ask again for work already authorized; outside scope, prepare the micro-plan, proposed diff and impact before requesting the necessary authority.

Current user instructions determine the product. A skill cannot grant authority or silently change the contract. Delegate only when authorized; each worker has an explicit target, owner, input version and deliverable. Never assign two writers to the same target.

## Shared sources

- Roles/file groups: [.agents/rules/permissions.md](.agents/rules/permissions.md).
- Modes, stop and recovery: [.agents/rules/execution.md](.agents/rules/execution.md), [workflow](sys/docs/workflow.md).
- Accounts/runtime: [.agents/rules/accounts.md](.agents/rules/accounts.md).
- Mascot: [.agents/rules/brand_tolerance.md](.agents/rules/brand_tolerance.md), `sys/assets/characters/channel-mascot/reference-v1.png`.
- Channel direction: `sys/vocab/channel.json`; each saved job retains its own contract.
- Procedures: vp-setup, vp-production, vp-development or vp-maintenance; load references only for the current step.

## Language and data

Communicate with the user in Vietnamese. Project definitions, internal instructions and prompts use English. Preserve the actual language/text of narration, captions, visible_text, quotes, anchors, IDs and real feedback. English keeps correct spelling, including I; pronunciation substitutions belong only in synthesis input. Do not change lesson data to repair TTS.

## Execution and bug discipline

- Complete the authorized work end to end. Do not avoid difficult work, substitute trivial changes or leave TODOs/placeholders when completion is possible.
- Reproduce bugs end to end through the actual user flow before fixing them. Unit tests alone are insufficient.
- Record mistakes and proven remedies in `sys/logs/issues/`. When the handbook grows, move rare cases into focused skills with short discovery descriptions and details loaded only when needed.

## Execution and handoff

Content → media → video are product groups. Auto executes without a reviewer; review waits at versioned outline, dialogue, audio, image-set and video outputs. Both modes publish real artifacts to the dashboard/chat. Follow the workflow for engine 4 versus historical v3 jobs; do not silently change mode or fabricate approval.

The machine manages and stores important data. Colab performs audio/media/timeline/subtitle/render processing; Flow generates images. Do not fall back to heavy local processing, silently change provider/voice/mascot, use paid APIs or buy compute. AI video generation is outside this workflow.

Production may repair assigned old or new videos through version/impact operations. Development may change system files within the authorized upgrade. Do not directly edit SQLite, request journals, revision snapshots, evidence or baselines; official tools record history. Preserve fixed `prompt_templates.py` templates unless the requested change specifically covers them.

Before production, verify checkout, job, grant, mode, checkpoint and pending requests. Unknown/ambiguous submissions must be collected/reconciled on their owning account/session, never resubmitted. Do not rotate accounts to evade quota/bot/CAPTCHA restrictions. Stop blocks new submissions while preserving already submitted work.

Each deliverable includes job/group/revision, a real file/link, verified measurements and verification limits. Do not claim inspection, quality or dashboard delivery without evidence. Metadata and fixtures do not prove real voice/image/video quality.

Log each issue in `sys/logs/issues/` and its INDEX. Proven remedies include the established label “Làm gì cho hết lỗi” and evidence. Micro-plan recovery depends on evidence, changed strategy and progress, with no total repair cap. A grant does not override service limits.

## Return and upgrade

Read [session-start](sys/docs/session-start.md) when returning in a new chat. Development checks compatibility and provenance; retain v3 job history and never create a duplicate job to evade state. During migration, use actual capability evidence in [normalization-progress](sys/docs/implementation/normalization-progress.md), not documentation as proof of implementation.
