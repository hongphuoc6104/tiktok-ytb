# Flow quota for layered jobs

- Layered jobs need more images (≈1 background + 2–4 stickers per scene). Budget ≤ ~25 images per job; reuse stickers across scenes.
- `LAYER_QUOTA` blocks more than 4 new stickers per scene.
- "Unusual activity"/quota/CAPTCHA blocks only the dependent images. Never resubmit an ambiguous request; reconcile on its owning profile/session first.
- Switching to another configured Chrome profile is allowed only when the user has explicitly authorized it for the job, and must be recorded with `pilot.py bind-session` (never by editing state).
