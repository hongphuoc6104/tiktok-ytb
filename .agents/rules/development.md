---
trigger: always_on
---

# Development planning and quota discipline

Apply this rule when the user asks to develop or repair the project. It does not change the content → media → video gates, protected-job controls, or human-only commands in `AGENTS.md`.

## One overall plan

Before splitting substantive work, keep one concise project-level plan in the task or an existing project plan file. State the full objective, current evidence, phases, dependencies, gate conditions, independent work packages, owner of each package, and the next verifiable action. Update that plan only when a finding changes the route or a phase finishes; do not create parallel copies of the same plan.

## Parallel agents with distinct ownership

Use subagents only when the user has authorized them and at least two bounded tasks can progress independently. Assign each agent a concrete outcome, file or artifact ownership, required evidence, and a focused verification step. Give overlapping code paths one owner; use isolated worktrees when concurrent changes could collide. Do not assign the same investigation, implementation, or test suite to multiple agents. Reuse completed agent findings instead of asking another agent to rediscover them. Integrate each result once after checking its evidence.

## Micro-plan when an issue appears

For each material issue found inside the overall plan, write a short micro-plan in its issue log or the current task: symptom and evidence → smallest cause to confirm → bounded repair → focused verification → stop/escalation condition. Identify the affected stage and whether an existing job revision or approval must be revisited. Return to the overall plan when the issue is resolved; do not let a local repair silently replace the original objective. Record the final fix in `logs/issues/` as required by `AGENTS.md`.

## Development quota

- Read only the relevant files and ranges. Use existing reports and observations; do not reopen unchanged material without a new question.
- Run the narrowest meaningful test for each work package. Run shared integration tests once after merging. Repeat a passing test only after relevant code or environment changes, or to investigate a concrete remaining risk.
- Avoid repeated status polling, equivalent tool calls, broad searches, and duplicate browser checks. Wait on a confirmed live process rather than restarting it because a check timed out.
- Keep agent handoffs short: changed files, result or commit, targeted test outcome, unresolved risk. Spend development tokens on code and evidence that move the full objective forward.
- Do not reduce the required video content, bypass review/integrity gates, or create a replacement job to make a test pass.
