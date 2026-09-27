---
name: vp-tiensu
description: Create or continue a 16:9 Vietnamese prehistoric story video from the Video Pilot tiensu bank. New briefs use many AI stills over 6–15 minutes; existing briefs retain their saved character and clip requirements. Do not use for vocabulary or 9:16 jobs.
---

# Prehistoric story videos

Paths and commands below are relative to `sys/`. Read `AGENTS.md`, `docs/workflow.md`, the saved brief, and [the long-form story guide](../vp-content/references/explainer-longform.md). The only public gates are **content → media → video**. This skill extends those gates; `doodle.build_ai` and scratch previews never constitute an approved Pilot video.

## Start or resume

For a new video, select a question with real sources from `tiensu/topics.jsonl` and run `python3 tiensu/bank.py start JOB --mode review` (or `--mode auto` only when the user requested auto). Do not handwrite a brief or reserve the same topic twice. For an existing job, run `python3 pilot.py status JOB` and `python3 pilot.py next JOB` first. Its saved brief remains the contract; do not retrofit the new defaults into historical revisions or override integrity failures.

New bank briefs set `character_mode: story_cast`, `duration: 360–900 s`, 16:9 Vietnamese, and no `clips`. The middle of that window gives the writer a roughly 10.5-minute starting budget, not a command to stretch every topic to one length. If the story needs a narrower window or more scenes, revise the brief **before content** through Pilot. Clips require an explicit user request and a valid brief revision; do not infer permission from `config.video_generation`.

## Content

Follow the question and available evidence, not a fixed number of chapters or a required protagonist. Open with a concrete situation or question, establish stakes, develop a causal, chronological, or comparative sequence, and answer with an honest payoff. A modern contrast, misconception, callback, or recurring person is optional when it serves this story. Do not force a 50,000-year setting. Cite real archaeological or research sources in the brief; every named finding, date, or number in narration must map to a source-backed claim. Write Vietnamese narration fully before anchors, coverage, and claims; never change the narration after anchoring it.

For new `story_cast` briefs, `characters` may be empty. Introduce story-specific characters only when the same design must recur within this video; name them in the cast and attach their actual references only to shots where they appear. An old brief without `character_mode` keeps its canonical mascot. Write the image plan as visible actions, state changes, evidence and reactions, with enough distinct stills to show what changes. `images[].kind` is `still`; `visible_text` is empty; Vietnamese labels belong in `beats[].overlays`. Use `based_on` when camera and setting continuity matter. Put packaging and short chapter titles into content.

Run `python3 pilot.py run JOB content`; in review mode stop with the current `review.md` and revision. In auto mode only the actual machine review can pass. A technical check does not approve quality.

## Media and video

After valid content approval, run `python3 pilot.py run JOB media`. Synthesize local Vietnamese narration first and measure the complete WAV. If it misses the saved duration window, repair content through reject/resume; do not pad, cut, or shorten ideas to make the number pass. Then generate the approved still plan with the configured Flow route. An independent composition may have no character reference in `story_cast` mode; use an approved video-specific cast reference where needed and a Base scene reference for dependent shots. Never silently attach the old channel mascot, substitute another image provider, or resend a request whose outcome is unknown. Check model, reference/media ID, journal, aspect ratio and each actual image; reconcile timeouts before another submit. Record a credit assumption as an assumption when UI cost was not verified.

Compare the whole image sequence with the measured WAV: each beat needs a narrative purpose, action or expression is visible, and text has enough reading time. Review all WAVs and images before the media decision. After valid media approval run `python3 pilot.py run JOB video`; inspect the full MP4 for image order, continuity, audio, captions, crop, pacing and ending. Only the current video decision permits export and `python3 tiensu/bank.py mark JOB`. Deliver the actual MP4, SRT, thumbnails, chapters, description and sources from the workflow output.

When this skill or its still-image path changes, perform a separate **new ~15-second smoke video** in `sys/scratch/` using fresh narration and 3–5 fresh Flow stills. Watch/listen to it and compare MP4 duration with WAV. The smoke is test data, never a Pilot job or a substitute for the three production decisions. If Flow is blocked by login, CAPTCHA, unusual activity, upload permission or quota, stop the smoke and report it as incomplete; do not switch accounts or tools to claim success.
