---
name: vp-maintenance
description: Inventory, reproducible cleanup, verified archive and scoped Video Pilot Git checkpoints; excludes production logic changes.
---

# Maintenance

Use maintenance scope from permissions.md and [maintenance operations](../../../sys/docs/maintenance.md). Read-only inspection is the default; official cleanup/archive/Git operations require exact reviewed manifests and grants. Inventory owners, inflight/unknown requests, retention and reproducibility before selecting files. Cleanup is not completion of a video.

Only remove generated files demonstrably reproducible and no longer needed by a job/request/reference/evidence. Record exact candidates and before/after counts. Never clear runs/reviews/browser profile/global cache/trash with a wildcard. Keep credentials, models in use, ledgers and original evidence.

Collect important outputs before releasing a dedicated Colab runtime; stop only owned services with no pending reconciliation. Archiving requires an authorized destination and verification of copied files before any source deletion.

Commit/push only granted repo/branch/path scope at a chosen maintenance checkpoint. Check diff, ignore rules and secrets; stage an allowlist, never git add . blindly. Preserve other local edits, never force-push. Resolve conflicts only within the same granted scope. A clock schedule requires a specified cadence; do not invent one.

If candidates cannot be proved safe, leave them and explain the precise missing evidence. Report actual files/bytes and issues, not generic promises of a reset.
