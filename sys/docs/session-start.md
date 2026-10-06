# New-chat handoff

1. Read INDEX/AGENTS in the correct checkout; inspect branch and local changes. Select one active role and the corresponding skill.
2. `pilot.py grants` reads persistent authority. A new chat does not expire valid grants; do not ask again for authorized work or fabricate authorization sources.
3. `pilot.py observe JOB` / `next JOB` are read-only, without job refresh or writer leases. Verify job, engine, mode, checkpoint/revision and handoff against current state.
4. Inventory inflight/unknown requests, owner/account/session and counters. A lock file is not proof of a live runner; timeout is not proof of no submission. Inspect Colab accounts before operations; never print tokens.
5. Choose pool/defaults for new work. Submitted requests retain their original account/session/profile. `bind-session JOB --session ID --source TEXT` records an actual session selection; never edit workflow state directly.
6. `resume JOB` continues the authorized checkpoint. `stop JOB --source TEXT` blocks new submissions while retaining submitted work for collection. `takeover JOB --source TEXT` succeeds only when the prior runner is no longer alive. Never create a replacement job to evade unknown work.

A v3 job retains its historical contract until development migrates it through official tools; never edit baseline/DB/decisions. Handoff includes checkout/version, role/scope, job/mode/checkpoint, artifacts/revisions, requests/account/session, issues/micro-plans, permitted next work and timestamp. Exclude secrets and fabricated approval. See [workflow](workflow.md) and [accounts](../../AGENTS.md).
