# B-2 experimental acceptance

Approved execution: 2026-09-21. Experimental credit ceiling: 1050 total,
including the earlier attempt whose charge is still unknown. This is not a
production preflight or permission to alter production's zero-credit policy.

## Gates and evidence

1. Private tool: capture actual URL/identity and UI proving independent ownership
   before modifying a community tool. If copying is unsupported, evaluate a new
   private tool; never silently treat a shared tool as a private copy.
2. Cost: observe account and charging information; record before/after balance
   and any competing activity. A balance delta alone is not proof of per-request
   cost. Unknown charges remain unknown, and unresolved submissions are not repeated.
3. References: demonstrate actual character and base-image attachments, including
   their identity. Repeating a description is not proof of image conditioning.
4. Continuity: four frames, one person → add two people → add an object → add
   allowed text. Preserve original characters, clothing, framing and unchanged
   background. Review each image and transitions, not just the final image.
5. Output: inspect actual file signature and dimensions; compare declared and
   downloaded output. Test both requested ratios separately and labels in English,
   Vietnamese, and an empty allowed-text list. No IDs, watermarks or extra words.
6. Queue: independent images can be queued; dependent variants must wait for their
   verified parent. Demonstrate mapping, restart without duplicates, and recovery
   from an uncertain outcome. Simulations must be labelled, not called live proof.
7. Video: only after image gates pass, render an isolated sample with real audio
   and supported transitions. Inspect legibility, continuity and timing.
8. Integration: keep production unchanged until evidence supports the candidate.
   Review and auto readiness are separate; auto requires real artifact assessment.

## Sample and decision rules

Initial capability probe precedes the full set: 3 scenes / 8 logical images,
rendered independently at 9:16 and 16:9 (16 outputs). Topics are test data only.
The four-frame sequence occupies one scene; the other scenes test reuse of the
character elsewhere and an unrelated subject. Record every attempt, including
failures and repairs. Report first-pass success as a fraction with the denominator;
90% is a pilot target, not statistical proof of batch reliability. At most two
repair attempts per failed image; all chosen final images must meet every mandatory
quality criterion. Record time and credit per accepted output.

Any failed prerequisite stops downstream generation. Capability absent in the
observed UI is recorded as unsupported in that interface, not impossible globally.
Do not manufacture evidence for unobservable internal prompts or model selection.

## Existing result nuance

The first asset is JPEG 1376×768 although the UI claimed PNG / 1920×1080.
That is a verified declaration mismatch. The current production image validator
allows a ratio tolerance: its 16:9 check uses an absolute ratio error of 0.04,
so this asset's ratio error (about 0.014) does not alone prove validator failure.
Technical acceptance is distinct from correct advertised output and visual quality.

## Required report

For each gate: pass / fail / unsupported / not tested, evidence paths, actual
tool identity, timestamps, input and reference mapping, cost uncertainty, and
remaining blocker. Final decision: custom B-2 / new private tool / unsuitable /
more evidence needed. Never represent offline scaffold tests as live acceptance.
