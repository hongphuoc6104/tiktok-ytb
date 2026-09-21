# Experimental project controller — current status

Production is unchanged; live generation remains disabled. Do not interpret local
unit tests as acceptance of reference conditioning, image quality or batch work.

## Browser connection

Executable `/opt/google/chrome/google-chrome`, primary profile
`/home/hongphuoc/.config/google-chrome/Profile 10`.

A live probe on 2026-09-21 showed that an existing CDP connection could create a
new tab under Profile 102 despite earlier successful Profile 10 probes. Therefore
connection reuse alone is insufficient. The controller now verifies exact profile
and executable on a probe tab, retains that same tab and uses it for subsequent
inspection. It refuses closed/navigated tabs rather than silently replacing them.
This preserves tool state and avoids repeated new-tab profile selection.

Verified live after the change: connect returned exact Profile 10, followed by two
successful inspections on the retained tab without a new connection. Evidence:
`results/bound-tab-inspect.json` and `results/bound-tab-inspect-reused.json`.
This proves the observed sequence, not all possible Chrome profile-switch behavior.

Use one `session.mjs serve`, followed by `connect`, `inspect`, `status`, `stop`.
The Unix socket is owner-only; commands are serialized. Chrome may request Allow
when a new CDP connection is established. There is no automatic retry after denial
or disconnect. Do not run standalone controller inspect alongside this service.
Client commands now have a timeout and return failure exit status for blocked work.

## Implemented checks

- Local preparation with content identity and preservation of existing records.
- Persistent verified-tab inspection with exact executable/profile checks.
- `check_contract.mjs`: read-only audit of required visible controls.
- `validate_asset.py`: decode actual bytes, validate MIME/ratio and measure real
  dimensions; report visual review separately as pending.

Latest actual UI audit: Style control is missing. Real reference conditioning,
model availability, per-generation credit cost and result recovery are unverified.
The original B-2 image passes technical 16:9 tolerance at JPEG 1376×768; it is not
an output of the custom tool and is not proof of continuity or new tool quality.

## Remaining integration

Wire the durable attempt store into a live adapter only after the contract in
CONTRACT.md is satisfied. Needed: source snapshots/narrow tool corrections, actual
reference selection evidence, immediate mediaId capture, collection/reconciliation,
then bounded queue tests and real Antigravity execution. No production integration
or claim of Antigravity handshake has been made.

The session currently supports connection/inspection commands only. It does not
submit editor changes, generate images, collect results or run batches. Updating
session command handlers requires restarting the service and a new Chrome consent.
