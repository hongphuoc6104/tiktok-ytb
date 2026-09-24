---
name: vp-script-director
description: Thiết kế và phản biện câu chuyện, lời thoại và hoạt động học cho kịch bản Video Pilot; dùng cùng vp-content, không vận hành job hoặc tạo media.
---

# Script direction for Video Pilot

Use the current brief as the contract. Read [the direction contract](../vp-content/references/director-contract.md). For vocabulary, also read [vocabulary pedagogy](../vp-content/references/vocab-pedagogy.md). Direct the script inside content; do not introduce another approval stage.

## Decisions before prose

- Name the learner's observable action after watching. “Enjoy the video” is not evidence of learning.
- Choose the smallest story that demonstrates the intended meaning: someone wants something, encounters resistance, acts, and gets a consequence. A change of place or the labels setup/climax/resolution do not establish causality.
- Choose an opening that makes the learning promise perceptible: a recognizable contradiction, consequential action, inner thought, or answerable question. Do not force every word into a bedroom/alarm setup or shame the learner.
- Decide what must remain explicit for this learner. A1 examples may need simple literal explanation; do not hide the lesson behind sophisticated jokes or subtext.
- Use the existing `outline[].purpose/transition`, `scenes[].purpose/action`, `beats[].purpose` to carry these decisions. Each transition should explain what changes or why the next scene follows.

## Write and edit

Write narration first, including full English sentences in correct spelling, then freeze it before attaching quotes/coverage/anchors. Read [narration style](../vp-content/references/narration-style.md).

For each line ask: who needs to say this now, what changes because of it, and what new information does it give? Keep required facts/examples; shorten repetition and filler, not the brief. If the brief is too dense, flag the conflict and use the established revision route.

Make examples actions inside the story. If three are explicitly required, retain all three while connecting them through goal, cause, consequence or a meaningful contrast. Do not relabel three unrelated examples as a narrative arc.

Provide one manageable retrieval opportunity: choose, complete, predict or produce a short sentence. The learner must have a way to check the answer. Match CTA effort to proficiency; a partially supplied sentence can lead to an original comment. Do not make engagement counts stand in for learning.

For end-of-scene practice, set `audio_direction.vi/en.learner_pause_seconds` to the time the learner needs for that utterance, then verify the resulting WAV. It is a deliberate hold, not narration text or a new scene. Omit it outside content-v3. Do not promise a mouth demonstration when the available medium is still images.

## Review evidence

Report in Vietnamese with scene IDs and quoted lines: the actual problem, why it affects this learner, and the smallest repair. If an opening raises a question, locate its payoff. If claiming a causal story, identify the causal links. Distinguish factual errors from taste and alternatives.

Do not approve content, change the selected vocabulary entry, translate narration_en into Vietnamese, or omit required coverage. A technically valid JSON does not prove a good lesson.

Sources and adaptation rationale: [source notes](../vp-content/references/director-sources.md).
