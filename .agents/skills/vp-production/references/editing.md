# Timing, captions and output

Build timelines from real language-track WAVs. Interpolated anchors are estimates, not word alignment. Each cut/hold/diagram/reveal needs a semantic purpose; avoid fixed seconds per image or density quotas.

Language, aspect, subtitles and track selection are independent. English9:16 must render English narration/cues/timeline. Use one cue source for SRT and video, meaningful groups of at most two readable lines, no punctuation-only cue. Keep exact lesson spelling and enough reading time for each actual sentence.

Use supported camera/transition effects (`cut`, `hold`, `fade`, `slide_left`, `zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `shake`) according to render-capabilities.md; preserve teaching text and visual action under crop/zoom. No implicit Foley. Opening question and payoff must remain understandable in the sequence.

Prepare, render and encode on Colab. The machine only manages/collects important outputs. Inspect actual playback when available without treating that craft activity as a machine-review gate. Report files/timestamps and observed problems; do not claim learning/retention without audience data.
