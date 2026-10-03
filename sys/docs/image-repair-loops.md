# Targeted image repair with progress

Engine 4 has no total cap on progressing repairs. Do not repeat failed target/input/strategy/evidence unchanged. Diagnose, consult logs, choose a justified strategy or report needs_attention with the actual cause. Renaming an issue/job cannot reset history. Engine 3 caps belong only to the [historical guide](legacy/image-repair-loops-before-normalization.md).

From `sys/`: `pilot.py repair-status JOB --image IMAGE --ratio 9:16`; inspect the actual file before describing errors. Then `reject JOB images --revision N --image IMAGE --ratio 9:16 --repair-plan PATH --note TEXT`, with actual feedback, followed by `resume JOB`. `--scene` repairs the whole scene; use `--image` for one image. Preserve unaffected audio/images.

Repair plans retain current_sha256, previous_sha256, strategy (pose/composition) and issues with id/status/evidence/instruction. First repair uses previous null/status new; later classify remaining/resolved/new without deleting open errors from history. All-resolved plans do not generate again. Hashes prove bytes, not correct meaning/pose. Mascot-tolerated expressions are not defects; see [brand rules](../../.agents/rules/brand_tolerance.md).

Issue micro-plans retain evidence/error_class/target/input_hash/strategy/success_criteria/rollback/submit_state and real outcome evidence. Auto has no machine reviewer or new quality gate; review waits for the actual image set/revision. Craft inspection may view images but cannot fabricate quality approval.

Submitted/unknown/ambiguous requests permit only original-request collect/reconcile on the owning session/account. Generated-but-uncollected results still need collection, not replacements. Quota/bot/CAPTCHA/auth/capacity/503 blocks dependent work; no rotation or repeated generation for luck. Network recovery has at most three actions per separate episode, not a total video-repair cap. Only collected images become ready on dashboard/chat.
