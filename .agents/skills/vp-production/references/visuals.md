# Storyboard and 2D explanatory images

## Checklist lập beat & ảnh (bắt buộc trước khi tạo prompt)
- Mỗi câu thoại được chia thành mấy beat, cỡ cảnh nào?
- Mọi hiệu ứng chọn đều có trong [render-capabilities](../../../../sys/docs/render-capabilities.md), không dùng whip pan hay parallax.
- Phụ đề không che trọng tâm ảnh 9:16 (dành riêng 1/3 dưới cho phụ đề).
- Prompt ảnh chỉ viết sau khi có kế hoạch beat.

Trước khi chọn cỡ cảnh/beat, bắt buộc xem [cinematography](cinematography.md) để áp dụng ngữ pháp khung hình và [render-capabilities](../../../../sys/docs/render-capabilities.md) để kiểm tra hiệu ứng khả dụng.

Give each image a function: situation, action/state change, diagram, contrast, explanation or payoff. Specify what must be noticed, permitted text, shot/attention, and change from the prior frame in existing images/beats fields.

Current channel: hand-drawn bold outlines, flat colors, bright uncluttered background, recognizable props/diagrams. Avoid textured photorealistic natural-history paintings or dark cinematic lighting. Investment is causal storyboard and useful state changes, not decorative detail or image count.

No main character or recurring presenter inside scenes (prompt registry 1.1.0). Cast consists of anonymous stick figures sharing one construction: large round white head with thick black outline, simple dot/oval eyes with expressive brows/mouth, thin black stick limbs, exactly one torso. Each figure's role comes only from the scene (costume, hair, skin tone, age/size, props). Allowed: exaggerated expressions, sweat drops, simple ?, red hand-drawn focus circles/arrows. Not allowed: anime eyes, realistic faces, muscular bodies, doubled torsos, recurring protagonist/narrator.

Character/style reference is optional and only guides drawing style. Use Base reference for shot/background continuity and based_on only when continuity is needed. Independent composition uses independent generation. No prompt/ref ID alone proves identity. Preserve exact allowed text and caption clearance; no forced yellow highlight/screen shake/comic effect. Historical character assets remain only for legacy 1.0.x/v3 jobs.

Flow remains the image provider. Unknown submissions must reconcile/collect on their owning session, never resend under a renamed target. Report real image IDs/version and evidence; visual sampling during development is not a new auto quality gate.
