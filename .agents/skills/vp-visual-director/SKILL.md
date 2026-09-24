---
name: vp-visual-director
description: Chỉ đạo storyboard, hành động nhìn thấy, bố cục và tính nhất quán mascot trong Video Pilot; dùng khi lập hình hoặc đánh giá ảnh thật, không thay công cụ tạo ảnh.
---

# Visual direction for Video Pilot

Read [the direction contract](../vp-content/references/director-contract.md). Work through vp-content for planning and vp-media for generation/repair. Operating paths are relative to `sys/`.

## Give every frame a job

Specify what the learner must notice, the visible action/state that demonstrates the meaning, framing, the dominant point of attention, permitted text, and what changes from the previous frame. Encode these in the existing image/beat fields; avoid an extra storyboard format competing with content-v3.

Show the target action, not merely its theme or aftermath. For a verb meaning leaving bed, a character already outside the house is a consequence shot, not the only evidence of that verb. Use before/after images when change is essential and cannot be shown by one still.

Use shot scale and angle to guide attention, not cinematic adjectives. Keep one main semantic task per frame. Reserve space for captions and platform UI, checking actual delivery size. Stable screen position for key learning text reduces unnecessary searching.

## Continuity and performance

The canonical mascot reference at `assets/characters/channel-mascot/reference-v1.png` is authoritative. Apply the 80/20 Brand Tolerance Policy: generated images do not need to match the script 100% or be pixel-perfect. 80% is the non-negotiable core brand identity: single torso, pale-blue short-sleeve shirt (#8CCFE8), round white head with dark navy outline, solid black oval eyes, and minimal stick limbs. Reject severe brand violations: doubled shirts, realistic human muscles/fingers, wrong shirt colors, or cartoon/anime eyes with huge whites and pupils.
20% is acceptable tolerance for situational expression and minor details: subtle expressive eyebrows (slanting downward when scolded/sad, furrowed when concentrating or anxious), minor forehead worry lines, sweat drops, varied mouth expressions (pout, open mouth talking/listening), and slight curvature/rounding of limbs when in motion ARE ACCEPTABLE and MUST NOT be marked as defects or failed in character_consistency review.

Direct emotion through pose, head tilt, gesture, distance, and situational context while honoring the core mascot identity. Prompts and matching media IDs do not prove compliance; actual visible perception does.

Keep line weight, palette, background detail, prop position and scale coherent. Minor props and background variations are acceptable as long as pedagogical clarity is maintained. Choose independent generation for genuinely independent compositions. Use `based_on` for a state change requiring a locked base; it must refer to an earlier image in the same scene. Throughput never decides story continuity.

Attach Character reference for mascot shots and Base reference for inherited shots using the existing Flow route. Never change provider, bypass reference checks or resend an ambiguous request.

## Picture review

Inspect every actual image, not only a contact sheet. Perform a silent sequence pass: can the intended situation and change be inferred without narration? Check exact allowed text, final crop/zoom, caption clearance and identity. Report scene/image IDs, visible evidence and a concrete repair in Vietnamese. If the image cannot be inspected, say unsupported; never mark it matched from filenames.

Read [source notes](../vp-content/references/director-sources.md) for the external craft references; they are not authorization to use video generation or a different image tool.
