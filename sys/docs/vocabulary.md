# Vocabulary bank and one sense per video

`vocab/sources/*.txt` is the source; `bank.jsonl` compiles one sense per entry. `ledger.json` retains reserved/done/history; `channel.json` selects direction when generating a brief. Vocabulary code is system code; assigned word data is content. Only official tools update the ledger. Profile changes do not rewrite existing job contracts.

The active profile targets English B1+, 9:16, bright explanatory 2D images and anonymous stick figures; the brief freezes voice/rate. Default selection filters profile allowed_levels, then sorts by level/rank. Old A1–A2/bilingual plans are historical, not this channel's default. Level overrides require the actual assigned product choice.

From `sys/`, use the management interpreter:

- `vocab/bank.py status`, `topics`, `show --word WORD`, `next --count 10`: inspect entries/senses without reservation.
- `vocab/bank.py start JOB --mode review|auto --source TEXT` or `--grant ID`: reserve exactly one sense, generate its brief and call engine 4. Use `--session ID` for the selected management session. `--scene-count N` applies only after choosing a job-specific count.
- `draw JOB` generates/reserves a brief only; create the job afterward through the official CLI. Do not handwrite vocabulary briefs or take another job's sense.
- `pilot.py run JOB`; authors submit outline/dialogue through `author`. Review has five outputs; auto has no reviewer. See [workflow](workflow.md).
- `vocab/bank.py mark JOB --note TEXT`: verify completion/export before updating the ledger. Never mark early or edit ledger state directly.
- `build` after source changes regenerates the bank without editing the ledger. `lint` inspects duplicate senses; `audit` checks jobs/bank/mark. Rank/level metadata do not establish learner ability.

Reserved senses stay with the same job during repairs. Release/redo/supersede need an actual lifecycle instruction and retain previous/history; never use them to evade unknown work or service caps. Queues are finite and explicitly assigned, never automatic mass production after setup. The [pre-normalization guide](legacy/vocabulary-before-normalization.md) retains earlier choices.
