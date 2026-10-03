# Narration length serves the story

Freeze narration before quotes/coverage/anchors. Keep correct English spelling, including I, required meaning, causality and payoff. Do not capitalize whole keywords to repair TTS. A scene may contain multiple images/beats; split scenes at changes in action/meaning/viewpoint, not arbitrary character counts.

The old 256-character threshold selected a Vietnamese local-TTS branch; it is not engine 4's creative ceiling or quality condition. Colab uses its actual request/chunk protocol. Do not infer that shorter text is synthesized in one pass or that arbitrarily long text always works. Preserve the job's brief/voice/rate; do not trim required content to fit a template.

Real WAV supplies duration and joins; pronunciation/emotion require actual listening. Submitted narration changes create a revision and refresh dependent audio, never independent snapshot/anchor edits. Learner pauses apply only when requested by the brief and actually supported; shadowing is not mandatory for every video. See [audio](../../.agents/skills/vp-production/references/audio.md), [story planning](story-planning.md) and the [prior explanation](legacy/narration-length-guidance-before-normalization.md).

In engine 4, planned minimum/maximum seconds guide writing only. Use the actual collected WAV to continue; do not fill, cut, retake or alter voice/rate to satisfy an estimate. A hard limit needs an explicit source-backed user requirement in the saved contract; no new CLI operation for changing that requirement was added here. Legacy v3 keeps its historical range. Invalid/zero/NaN durations or inconsistent PCM/timeline/video remain technical errors.
