# Video Pilot

Produce one-sense vocabulary lessons through narration and explanatory illustrations. The current channel targets English B1+ portrait Shorts: 9:16, bright backgrounds, bold outlines, flat colors and anonymous stick figures. One question/situation leads to a payoff; choose scene/image counts per video instead of a fixed comedy template.

New English briefs default to **reference-narrator at 0.92**, using the [user-selected sample](sys/assets/voices/reference-narrator/README.md). Vietnamese Minh Quân Pro and existing jobs retain their own saved voice contracts.

## Getting started

1. Read [INDEX](INDEX.md) to select the task.
2. New machine: [getting-started](sys/docs/getting-started.md). New chat: [session-start](sys/docs/session-start.md).
3. Open the lightweight local dashboard as described in getting-started; eight tabs share actual job/revision/event data.
4. Production: [workflow](sys/docs/workflow.md); upgrades: vp-development; maintenance: [guide](sys/docs/maintenance.md) and vp-maintenance.

Authority is defined by [AGENTS](AGENTS.md) and .agents/rules. One task uses one active role; valid grants survive chat changes. User-facing chat and UI remain Vietnamese.

## Architecture

The machine keeps UI, authentication, plans, metadata, evidence and collected products. Colab performs audio/media/timeline/subtitle/render work; Google Flow generates images. Remote failures do not trigger heavy local fallback. No paid APIs or automatic compute purchases.

Auto plans, executes and recovers through micro-plans without a reviewer. Review waits for the user after each main output. Both modes update real products on the dashboard.

## Data and status

`sys/` contains the system/data; `video/<job>/` contains products. Vocabulary comes from sys/vocab, one sense per entry; repairs retain versions and dependency impact. Do not commit tokens, profiles, models, databases or runtime media.

The upgrade remains in progress; see [verified progress](sys/docs/implementation/normalization-progress.md). Engine v3 and old reports describe historical compatibility, not acceptance of the new auto/English portrait path. Isolated tests do not replace actual Flow/T4/audio/video trials.
