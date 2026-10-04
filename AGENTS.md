# Video Pilot — Agent Invariants & Governance

Read [INDEX.md](INDEX.md). System code/data belong in `sys/`; collected products belong in `video/<job>/`. Do not create operational data at the project root. The root launcher is `python3 pilot.py`. On return in a new chat, read `sys/docs/session-start.md`.

## 1. Scope & Authority Matrix
Use exactly one active role per task. Grants record scope, actual authorization source and status; chat changes do not expire them. Do not ask again for work already authorized; outside scope, prepare a micro-plan/diff/impact before requesting authority:
- **setup**: First-time machine onboarding, environment bootstrap (`uv`, `.venv`, dependencies), initial interactive account login scripts (`python3 -m colab_bridge.accounts login-many`), Chrome browser profile & credential stores (`~/.config/video-pilot/`). Does not produce videos or alter engine/policy.
- **production**: Create, continue, or repair assigned old or new videos through workflow; manage and ensure needed runtime sessions (Colab T4, Flow) on configured accounts without interrupting workflow. Outside authority: System code, schemas, configuration, Rules, Skills and guides.
- **development**: Upgrade system code, tests, compatibility, migration, rollback, Rules and Skills within authorized assignment. Outside authority: Product goals, services/costs or accounts outside assignment.
- **maintenance**: Inventory, reproducible cleanup/archive, commit/push authorized paths and branch. Outside authority: Delete history/evidence/secrets/pending requests or change product logic.

*History integrity*: Never directly edit SQLite, request journals, revision snapshots, evidence, baselines or state history; official tools record history.

## 2. Hard Boundaries (Ranh giới cấm)
- **Resources**: No paid APIs, compute purchases, heavy local fallback, or AI video generation. AI video generation is outside this workflow.
- **Accounts & Quota**: No account rotation to bypass quota, bot, CAPTCHA, or abuse restrictions. Errors (auth/quota/CAPTCHA/503/unknown) block only their dependent scope. Never resubmit ambiguous or in-flight requests; collect and reconcile on the owning account/session first.
- **Runtime & Environment**: Reuse existing Chrome profiles via CDP project transport only; do not create fresh browser roots, copy cookies, or treat missing CDP as logout. Computer Use is excluded. Remote media/timeline/render runs on Colab GPU T4 preset.
- **Source Code**: Preserve fixed `prompt_templates.py` templates unless the authorized change specifically covers them.

## 3. Execution, Modes & Bug Discipline
- **Execution Modes**:
  - `Auto`: Executes from overall plan to outputs; recovers through micro-plans without a reviewer or total repair cap.
  - `Review`: Waits for actual user instructions after versioned outline, dialogue, audio, image-set, and video outputs.
- **Stop & Runner Handoff**: Stop blocks new submissions while preserving in-flight work, owner, and checkpoint. Resume never duplicates runners; take over only after confirming the previous runner is no longer alive.
- **Bug Discipline**: Reproduce bugs end-to-end through the actual user flow before fixing them. Unit tests alone are insufficient. Record mistakes and proven remedies in `sys/logs/issues/` and its INDEX with the label “Làm gì cho hết lỗi”.

## 4. Visual Cast & Communication
- **Visual Cast**: Anonymous stick-figure cast (prompt registry `1.1.0+`, channel profile v5): large round white head with thick black outline, dot/oval eyes, stick limbs, exactly one torso; no main character, recurring protagonist, or presenter inside scenes. Character/style references guide drawing style only. Legacy character assets are retired. Full details: `.agents/skills/vp-production/references/visuals.md` and `brand_tolerance.md`.
- **Language & Communication**:
  - Communicate with the user in **Vietnamese**.
  - Technical definitions, internal prompts, code and guides use **English**.
  - Preserve the exact language/text of narration, captions, visible_text, quotes, and anchors. English retains correct spelling (including `I`); pronunciation substitutions belong only in synthesis input.
