---
name: vp-edit-director
description: Biên tập nhịp kể, điểm cắt, thời gian đọc và phụ đề của Video Pilot; dùng khi lập beats, kiểm tra media hoặc xem bản dựng, không tự xuất ngoài workflow.
---

# Editing direction for Video Pilot

Read [the direction contract](../vp-content/references/director-contract.md). Work inside content → media → video with the corresponding vp-* skill.

## Cut for a reason

Give each beat a function: orientation, demonstration, reaction, correction, practice or payoff. More cuts do not automatically improve learning. Let a useful reading or speaking hold finish; remove repetitive visual changes rather than shortening the learner's turn.

Test the opening promise and its payoff. Identify where an example first becomes usable. Judge delay by what the viewer receives during it, not a universal hook deadline. Assess how neighboring shots direct attention and preserve story state.

Use supported effects only: hold, cut, fade, slide_left, zoom_in, zoom_out. Choose a cut before adding an effect. A zoom must retain all learning text, mascot identity and useful action. A transition cannot repair an unrelated shot sequence.

## Timing and captions

Use measured WAV duration. Narration anchors mapped by interpolation are estimates, not forced alignment. Listen to the actual word around each important visual change, and report a timing problem against that evidence.

Subtitle text must preserve the approved narration's spelling, including English I. Keep closing punctuation with its phrase and avoid standalone quotation marks or stranded final words. Prefer meaningful phrase groups across at most two lines; preserve sentence meaning and do not paraphrase a lesson silently. Excess reading speed requires an editorial repair, not hiding words.

Check on the delivered portrait frame at phone size: readable type, sensible line breaks, contrast, clearance from teaching text and platform controls. SRT and burned-in cues must come from the same cue list. A layout test proves geometry only; it does not prove ease of reading or synchronization.

Use `python3 scripts/editorial_audit.py --props PATH` for read-only technical findings. Treat warnings as review prompts and errors as defects; neither constitutes human/machine quality approval.

## Review passes

- Silent picture: story, meaning, identity and visible text.
- Audio only: coherent language, intelligibility and practice time.
- Full playback: actual synchronization, reading, transitions, payoff and final frame.

Record which passes were actually possible. Contact sheets cannot establish full-playback quality. Report findings in Vietnamese with artifact/timestamp, observed issue, impact and repair. Repair narration through content; media through media; rendering through video, preserving gates and history.

Sources: [source notes](../vp-content/references/director-sources.md).
