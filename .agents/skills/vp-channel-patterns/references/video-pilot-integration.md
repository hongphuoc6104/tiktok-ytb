# Video Pilot integration and self-test

Use this reference when the user asks to turn a channel playbook into a real Video Pilot output. The channel analysis selects storytelling functions; the saved job brief and Video Pilot contracts remain authoritative for language, word sense, cast, output, voice, provider and mode.

## Author against the saved brief

Create new vocabulary jobs through the official bank start command and an authorized production grant. Do not edit the ledger, brief snapshots, request journals or workflow state by hand. After the outline, author the dialogue through `pilot.py author` and check it with `pilot.py check-draft` before `pilot.py run` submits media.

For content-v3, keep these relationships exact:

- `topic`, `duration` and `style` must equal the current saved brief. If the brief needs new sources or a clarified topic, revise it through the official brief operation first, then author against its current revision and hash.
- Content `required_points` is the ordered list of required-point text strings from the brief, not the brief's `{id, text}` objects.
- The content outline must match the saved outline. Every scene's `purpose` and `requirements` must exactly match its outline row; scene IDs and order match the saved scene count.
- Each coverage row uses a requirement ID that appears in that scene's `requirements`, with a verbatim `quote` and, for English content, `quote_en` copied exactly from that scene's English narration.
- The first visual beat in each language anchors at the start of the narration. Later anchors must occur in increasing order, exactly as written. Every image is used by a beat and beats reference images in the same scene.
- `revision_response` is an array even when there are no repair requests. Never use `null` for an empty list.
- Factual claims use sources declared in the brief. `source_id` matches a brief source ID; each scene's `source_ids` references declared sources; each claim's quote occurs verbatim in narration and its fact string matches one of that source's declared facts.

These are contract checks, not quality approval. Fix authored content with a new official author submission; preserve the earlier revision and its failure evidence.

## Bind and use Flow safely

Use a profile that is already in the selected management pool and is connected through the project's existing CDP transport. Verify that the live profile path and tool URL match the runtime binding frozen for the job. When a new job needs a Flow binding, record an exact job-specific runtime target through the official management-session binding operation and snapshot it with `pilot.py bind-session`. Do not edit global configuration or create a replacement browser root for one video.

Keep identity, authentication, provider capability and budget as separate facts. Use only the bound account/session for that request. Do not switch profiles because a request received quota, unusual-activity, bot, CAPTCHA, authentication, service-error or unknown-state feedback.

If any Flow request is `submitted`, `ambiguous`, `unknown` or still queued, collect or reconcile that exact request on its original owner/account/session before new image work. Never clear a queue, retry an ambiguous image, or manufacture a “not submitted” state from a local error message. If the existing UI/owner evidence cannot resolve it, preserve the job and stop only the dependent image/render work until the state is known.

## Synchronize visual effects to narration

Engine 4 supports narration-anchored visual beats. Each beat carries an exact `anchor` quote, an `effect` such as `zoom_in`, `punch_in`, `pan_left`, `pan_right`, `shake` or `hold`, and a focus point. The timeline builder maps the anchor into the measured audio segment and then interpolates within its text span; the renderer starts the selected beat/effect at that time. Layered sticker motion can also use narration anchors for appearance, exit and shake.

This is phrase/segment synchronization, not automatic beat detection from waveform energy, emotion or music. The interpolation is approximate word timing, not forced alignment. Preserve exact narration quotes, use anchors in increasing order, then verify the rendered motion against the actual WAV and captions. Do not claim an effect is synchronized just because a prompt or timeline contains an anchor.

The explicit output contract assigns one language to each aspect-ratio slot. When a project needs two full-language versions at the same aspect ratio, plan separate language-specific outputs/jobs; do not duplicate an aspect slot or silently replace the channel voice. A single mixed-language narration is a distinct authoring choice and should use only the project's supported language-span synthesis path.

For one Vietnamese-led vocabulary clip with English model lines, the brief can select the `vi` output and the `Adam` profile. Keep the Vietnamese explanation in `narration`; wrap each intended English line in quotes so `english_parts` routes it through the configured English profile (in this project, `reference-narrator`, the user-selected clone). A `narration_en` counterpart is not automatically voiced in that single `vi` output. Before remote synthesis, build the request locally and verify it resolves both language profiles and their hashes; after synthesis, verify the actual WAV and timings before rendering.

## Prove the self-test

A skill has not been self-tested by schema validation alone. For a requested demonstration, use one original subject, complete the job through the normal Auto or Review workflow selected for that job, and inspect the actual current artifacts:

- real collected WAV and SRT, with measured duration, voice/rate provenance and scene boundaries;
- every image returned by the configured provider, linked to its original request and visually checked against the job brief;
- the collected MP4, dimensions, audio/video duration alignment and subtitles, followed by playback inspection where available.

Report blocked or unverified stages literally. Do not label an outline, screenshot, prompt, queued request or metadata file as a completed video. Do not claim audience retention or learning outcomes without audience evidence.
