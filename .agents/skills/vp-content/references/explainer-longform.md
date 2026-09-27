# Long-form prehistoric stories (16:9 Vietnamese)

Use when `brief.channel == "tiensu"`; the adapter loads this file for outline and content. Read the saved brief first. Its duration, character mode, sources and required points outrank new channel defaults. Write Vietnamese narration naturally for the actual era and topic; read [narration-style.md](narration-style.md) before writing it.

## Observed content pattern, not a copied template

A comparison of the channel's high-view examples — [daily life](https://www.youtube.com/watch?v=49_Ph2q6uIM), [a rainy week](https://www.youtube.com/watch?v=SD7XyG2wd1k), [other human species](https://www.youtube.com/watch?v=OCr6NteWSQ8), [alcohol](https://www.youtube.com/watch?v=9AFO6MHy8y4), and [travel](https://www.youtube.com/watch?v=QP1maS6hYn4) — suggests a common function: a concrete situation or sharp question; stakes; a progression of sourced explanations; an answer that changes how the viewer sees the opening question. The examples vary in era, narrator viewpoint and how they group evidence. This is an inference about storytelling, not proof that a template causes views. Do not translate their narration, reproduce their figures, or imitate their thumbnails.

Use the arc that explains this topic best: a day unfolding, a problem and its attempts, a comparison, a timeline, a journey, or several cases. The modern-day contrast, a mistaken belief, a mystery, and a visual callback are tools, not mandatory beats. Never force the setting to 50,000 years ago or force six to eight evidence chapters. Each scene should change the viewer's understanding of the question. Name chapters for the actual transitions rather than splitting by equal time.

New bank briefs use R1–R4: specific opening, question/stakes, evidence-led progression, and an honest payoff. Cover them with quotes from the finished narration. For old briefs, keep their stored R1–R5 and every other saved requirement; revise a brief through Pilot rather than silently changing its contract.

## Length and speech

New channel briefs permit 360–900 seconds. The default writing budget is the midpoint, about 630 seconds, so a normal request does not collapse to six minutes. Choose a narrower brief window before content if the question and evidence justify one; do not stretch a thin idea, omit material to fit, or invent extra claims. The budget is estimated from Vietnamese space-separated units; real VieNeu WAV duration decides whether the media gate passes. Finish narration before placing anchors, coverage, claims or subtitle cues. Keep sentences manageable for local TTS; do not encode pronunciation hacks in the lesson text.

## Research and claims

`facts_required` remains true. A `seed_fact` is only a research lead. Every date, site, quantity, study result or strong historical claim in the narration needs a matching `claims[]` item whose `source_id` and `fact` refer to an actual `sources[]` fact in the brief; quote the exact narration span. If more sources are needed, research them and revise the brief before content. Distinguish archaeological observation, plausible reconstruction and speculation in the wording. Do not make one source stand in for unrelated claims or repeat a claim just to satisfy coverage.

## Storyboard of many stills

For `character_mode: story_cast`, a cast can be empty. A video-specific recurring person or group gets a consistent appearance only when the story needs it; there is no channel-wide lead. Use the `character_ids` of each actual shot, and keep them empty for landscapes, objects, maps or other people-free shots. A dependent shot uses `based_on` to preserve camera and setting; an independent composition starts separately. Every image/beat should show a visible action, consequence, reaction, evidence or change of state. Plan enough distinct stills and optional reaction inserts to make the narration visually legible; reuse a still deliberately for a callback or a hold that serves the story, not to hide an image-generation failure. Beat timing follows the measured narration rather than a fixed number of seconds per image.

Keep `visible_text: []` and put Vietnamese labels/numbers in `beats[].overlays`; verify at phone size. The channel's cream-paper, thick-ink, muted-color doodle style stays consistent across stories without reusing a protagonist. New briefs omit `clips`; use `kind: clip` only when a user-requested brief revision explicitly includes a positive clip budget.

## Packaging and review

Write three accurate title options, an image-based thumbnail plan, a two-sentence hook for the description and relevant tags with the content. The thumbnail uses an existing still and a short Remotion text overlay. Build chapter times from actual WAV scene boundaries. Review the entire Vietnamese script for narrative clarity and source fidelity, then review every generated image, the WAV and the finished MP4 at their proper gates. Technical checks and contact sheets are not substitutes for actual viewing/listening or a valid Pilot decision.
