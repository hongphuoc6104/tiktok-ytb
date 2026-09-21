# B-2 Illustrator — isolated experiment

This directory is an assessment harness for the Google Flow Community tool
`B-2 Illustrator`. It is intentionally separate from the production Video
Pilot adapter. The default command is read only and does not open a browser,
upload an asset, submit a generation, or write a production run.

The harness records the questions that must be answered from the live UI:

- whether the Community card can be remixed or customized;
- whether character references can be attached and retained;
- whether a previous scene can be used as a base image;
- whether multiple outputs can be requested and downloaded individually;
- which model, project, ratio, output count and credit state are visible.

The completed live findings are summarized in [assessment.md](assessment.md).

## Core Objective: Progressive Layering & Visual Beats Engine

Mục tiêu dài hạn của công cụ này là chuẩn hóa kỹ thuật:
**"Diễn hoạt phân lớp theo nhịp thoại" (Progressive Layering / Visual Beats) trong video dạng Explainer / Kể chuyện**.
Công cụ chịu trách nhiệm sản xuất ảnh nền/nhân vật gốc (Base Scene / Character) hoàn toàn nhất quán (stasis) kết hợp với các biến thể đồ họa gia tăng (thought bubble, visual icons, typography keywords) đồng bộ chính xác với nhịp âm thanh lời dẫn.

The user-authorized ceiling for isolated B-2 experiments is 1050 credits. It
is separate from production's `credit_budget: 0`, applies only to this tool,
and is fail-closed here: spend remains unknown and generation is disabled
until a reviewed live runner records the actual charge.

The local Chrome data directory is referenced in `config.json`. The harness
does not copy cookies, session files, or browser data. The configured
`Profile 10` is the existing signed-in profile discovered in the data
directory; its account metadata is only a candidate identity and is never
treated as current Flow UI proof.

## Offline inspection

From the project root:

```bash
python3 experiments/b2_illustrator/b2_illustrator.py inspect
python3 experiments/b2_illustrator/b2_illustrator.py inspect --format json
python3 experiments/b2_illustrator/b2_illustrator.py inspect --record
```

`--record` writes a local dry-run plan under `experiments/b2_illustrator/results/`.
It does not create `flow/preflight.json`, modify a job, or submit to Flow.

Generation is deliberately unavailable in this scaffold. A future live UI
probe must be added as a separate, explicitly reviewed capability after the
Community card has been inspected in the user-owned Chrome session. Any
production integration must add tool identity/version and the expanded prompt
to its request provenance before it can reuse a cache key.
