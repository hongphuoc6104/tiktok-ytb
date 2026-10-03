# Maintenance, archive and Git checkpoints

Use valid maintenance authority. These are operational/provenance checks, not an OS sandbox. Default behavior is preview; execution needs `--execute`, a valid grant and the reviewed plan's `--review-hash`. Do not invent timers, commit/push automatically or clear directories. Commands run from `sys/` with the management interpreter.

## Reproducible cleanup

`maintenance.py cleanup --manifest PATH` returns checked exact files/bytes/hash. A version-1 manifest has `files`, each with project-relative path, sha256, owner_job, recipe, inputs and collected_outputs (proofs contain path/sha256). Only regular generated temporary files qualify, never wildcards/directories. Inputs and durable collected outputs must exist and match hashes; they cannot also be candidates.

Execute the same manifest with `maintenance.py cleanup --manifest PATH --execute --grant ID --review-hash HASH`. The grant covers cleanup, actual job ownership and file paths; manifest labels cannot relabel another job. The tool rechecks hashes, pending requests, runner/leases and references across jobs/video, including referenced cache directories. Unknown/generated-but-uncollected/evidence dependencies are retained. `.state/maintenance/` records intent before deletion and per-file/byte results afterward; interruption is not completion.

Never use cleanup for tokens/profiles/DB/ledger/revisions/journals/evidence. Do not release remote sessions or kill system processes by a generic name/pkill. Collect important outputs before stopping an owned runtime through the bridge; reconcile unknown requests first.

## Archive

`maintenance.py archive --paths FILE... --destination sys/archive/NAME` previews byte-preserving copy into a new directory. `--execute --grant ID --review-hash HASH` copies, verifies source/destination hashes and saves the manifest. Sources remain intact and existing destinations are never overwritten. The grant covers source/destination paths and actual source jobs; archive obtains their leases and protects pending work. Credential/environment/private-key files cannot be copied under a broad artifact grant.

External-disk archive needs an exact destination scope first: `maintenance.py archive-scope --grant ID --destination /ABS/NEW-DIRECTORY --source TEXT`, with actual authorization. Preview/execute archive afterward using that destination. It must be a new directory with no symlink ancestors. External scope does not authorize editing/deleting other files on the disk. Any later temporary cleanup requires its own verified proofs; snapshots/products do not become caches merely because a copy exists.

## Git at the assigned checkpoint

Git grants restrict file allowlists. Record the actual branch/remote authorization: `maintenance.py git-scope --grant ID --branch BRANCH --remote origin --source TEXT`. Add `--push` only when push is authorized. Scope persists across chats and remains subject to grant revocation. Operator-supplied source text is not authenticated user transport evidence.

`maintenance.py git --grant ID --branch BRANCH --paths FILE...` previews HEAD, remote URL, status and file hashes. Only the recorded branch/remote is accepted. Existing staging, conflicts, ignored/runtime/media/model/history/auth/secret files, large/binary data, escaping paths and symlinks are rejected. Preserve unrelated local changes.

`maintenance.py git --grant ID --branch BRANCH --paths FILE... --execute --review-hash HASH --message TEXT` stages the exact allowlist and commits normally. `--push` requires push scope and sends only HEAD to the authorized branch, never force. Check/auth/conflict failures stop with their real cause. Journal a successful local commit before push; a failed push does not erase that commit or justify claiming none exists. No blind `git add .`, silent remote changes, rule changes to repair conflicts or schedules without an agreed cadence.

Before commit/send, inspect all outgoing commits, paths, blob contents, commit messages and actual staged contents, including secrets later removed from working files. Only one authorized push URL/branch is allowed; tags and submodule pushes are excluded. Executable effective commit/push hooks block before mutation until a separate authorized task reviews their integration. Existing validation hooks are neither run implicitly nor silently bypassed.

Tests use temporary jobs/artifacts/repos/bare remotes; they do not clean/commit/push the project or prove GitHub backup. Recorded QA after maintenance fixes: independent 28/28 and worker 20/20, with the exact isolated scope in [QA](../reports/normalization/qa-maintenance.md) and [worker evidence](../reports/normalization/maintenance.md).
