---
name: storyboard
description: Create cohesive storyboard frames for product-launch and SaaS motion-graphics videos. Use when the user asks for storyboard frames, product-launch motion-design stills, AI-video-ready frame batches, Gemini/Omni/Higgsfield image batches, or wants screenshots converted into a polished launch-film sequence. Must be paired with Codex `$imagegen` / built-in image_gen for every generated frame.
---

# Storyboard - Product-Launch Motion Frame Director

This skill turns product screenshots, brand assets, and taste references into a cohesive storyboard frame set for short product-launch motion graphics.

It is intentionally opinionated: a storyboard frame is not just an image. It is a production still that must preserve product truth, match the visual system, and imply motion.

## Required Companion Skill

In Codex, this skill must be used together with `$imagegen` / the built-in `image_gen` workflow.

- When this skill activates, explicitly load/use the `imagegen` skill before generating frames.
- Announce the pairing as `videos:storyboard` + `imagegen` so the user knows generation is coming from Codex imagegen.
- Use `imagegen` for every storyboard frame.
- Generate new frames or regenerate failed frames.
- Do not manually edit, composite, patch, overlay, or append to storyboard frames with ImageMagick, HTML/CSS, SVG, canvas, Photoshop automation, or local scripts.
- Do not manually place logos, text, UI, flags, buttons, or corrections onto generated frames.
- If a generated frame mutates a logo, misspells text, uses fake UI, or breaks the visual system, reject it and regenerate with a narrower prompt.

Allowed local file operations:

- create folders
- copy generated image outputs into the project
- rename outputs sequentially
- write prompt logs and storyboard notes
- create contact sheets from final frames for review
- create upload-ready folders that only contain copies of final generated frames

If this skill is invoked from Claude Code or another host that does not have Codex imagegen available, route the generation work to Codex/headless. The host may plan and review, but Codex owns frame generation.

## Activation

Use this skill for requests like:

- "make storyboard frames"
- "create product launch motion graphic frames"
- "turn these screenshots into a SaaS launch storyboard"
- "make Gemini/Omni/Higgsfield frame batches"
- "generate frames and keep checking they align"
- "make it feel like screenshots from a real launch video"

Do not use this skill for finished video rendering, code-native animation, deterministic UI implementation, or simple prompt rewriting unless the user is clearly working toward storyboard frames.

## Prime Directive

Generate, inspect, compare, reject, regenerate, and log.

Never treat the first generated frame as correct by default. Every frame must be judged against:

- product truth
- source screenshots
- brand assets
- taste references
- existing accepted frames in the set
- text policy
- logo policy
- motion-design plausibility

## Inputs To Establish Before Generation

Before generating frames, establish these foundations. Infer low-risk details from local files when possible; ask only when a missing answer would materially change the frame set.

### 1. Product Truth

Identify what the product actually does and the one-sentence promise.

Good:

- "A World Cup predictions app where users make picks with an AI agent."
- "A B2B analytics tool that turns support tickets into launch decisions."

Bad:

- "Make it look cool."
- "Generic SaaS AI platform."

### 2. Narrative Spine

Reduce the video to a short story flow. Do not list every feature.

For a 5-10 second product launch, use 5-8 beats:

```text
entry / setup -> first product action -> agent or system response -> confirmation -> social/proof -> brand resolve
```

For Fantopy-style prediction apps:

```text
name or appoint agent -> make prediction -> agent reacts -> lock score -> invite friends -> leaderboard -> brand
```

### 3. Source Of Visual Truth

Find and inspect the actual product materials before inventing:

- app screenshots
- running app route
- brand kit / real logo files
- existing storyboard frames
- UI component files
- design tokens / CSS variables
- selected reference images or videos

Extract the product's real visual language:

- color palette
- type style
- card radius
- button shape
- spacing density
- border/glow behavior
- screenshot composition patterns

### 4. Taste References: Borrow / Do Not Borrow

For every external reference, separate what to borrow from what not to copy.

Examples:

- Borrow: "soft teal-blue gradient field, crisp glass modules, spacious composition."
- Do not borrow: "the Ask AI search bar, docs wording, unrelated icons, the reference brand's layout."

Never copy reference text, product concepts, or UI metaphors unless the user explicitly asks.

### 5. Text Policy

Choose one text mode before generating.

Default: use minimal exact text only.

Modes:

- `textless plates`: no readable generated text; copy is added later in a motion tool.
- `minimal exact text`: 1-8 short exact strings, no paragraphs.
- `real UI screenshot text`: preserve existing screenshot text as reference.
- `editable motion layer`: generate mostly textless plates and plan copy as a separate layer.

Avoid generated paragraphs, fake microcopy, skeleton bars, placeholder labels, and text-dense UI unless the user explicitly accepts the risk.

### 6. Brand Asset Policy

Real logos and marks come from brand files or uploaded references.

- Attach or reference the real brand asset for imagegen.
- Do not ask the model to invent the logo.
- If the logo mutates, regenerate. Do not manually patch it.
- If logo fidelity is mission-critical and imagegen cannot preserve it after targeted retries, report that limitation rather than compositing a manual fix.

### 7. Avoid List

Always maintain an explicit avoid list based on user taste and product category.

Common avoids for SaaS/product-launch storyboards:

- fake logos
- gibberish UI text
- placeholder bars / skeleton loading rows
- random fake dashboards
- cluttered background graphics
- generic centered hero cards
- realistic footage when the user wants product motion
- overdone 3D/cinematic renders
- copied reference concepts
- neon cyberpunk / glitch / lightning unless requested

For sports-adjacent apps, avoid realistic stadiums, crowds, mascots, grass, broadcast overlays, and live-action football scenes unless the user explicitly wants them.

### 8. Output Constraints

Before batching, determine:

- aspect ratio, usually `9:16`
- duration target
- frame count
- destination folder
- target video or editing tool, if known
- tool constraints, if known: image count, clip duration, keyframe support, start/end support, node workflow, upload size
- whether prompt logs and contact sheets are needed

Known upload planning examples:

- Gemini/Omni: often split into 10-image chat batches.
- Higgsfield: split into 9-image batches when needed.
- Node-based AI video tools: often work better with a master storyboard plus smaller connected keyframe groups, not one huge image dump.
- Manual motion tools: prefer fewer high-quality plates and editable text layers.

For AI video tools, separate the master storyboard from tool limits:

- Master storyboard: enough frames to create rhythm and breathing room, often 12-18 frames for a short product launch.
- Delivery batches: copies grouped for the tool limit or workflow.
- Stitch overlap: repeat one boundary frame between adjacent batches or generated clips when it helps continuity.
- Motion prompts: write separate prompts for each grouped motion arc when the tool supports multi-image or keyframe-based generation.

### 9. Preflight Decision Gate

Before generating a full storyboard or motion-handoff package, make sure the following are either answered by the user or stated as assumptions:

- output purpose: still storyboard only, AI-video input, manual editing reference, or finished-video planning
- target tool/workflow: unknown, Gemini/Omni, Higgsfield, Runway, Krea, manual editor, Remotion/HyperFrames, etc.
- desired final duration or approximate clip length
- master frame count or acceptable range
- whether the user wants strict product screenshots, stylized product frames, or a hybrid
- text policy: exact generated text, textless plates, or editable text later
- motion handoff needed: yes/no, and whether to create prompt files
- batch/grouping constraints, if any
- stitch strategy: clean in/out frames, overlapping boundary frames, or hard cuts

If these decisions are not clear, do not blindly commit to a specific frame count or batching structure. Either ask a concise confirmation question or write an explicit assumption block before proceeding.

Good assumption block:

```text
Assumptions before generating:
- Target: AI-video input, not final rendered video.
- Master storyboard: 12-15 frames.
- Style: product-launch motion stills using real product UI as the source of truth.
- Handoff: create prompt files only after the frame sequence is accepted.
```

Only skip this gate when the user explicitly asks for a fast draft or the missing details have a low impact on the result.

## Frame Strategy

Prefer product-motion frames over literal full screenshots.

Strong frame types:

- full-bleed gradient stage with one cropped UI module
- oversized input/control sliding into view
- fixture or score control cropped at frame edge
- chat bubbles staggered through negative space
- confirmation state with one check/glow
- invite/link module
- leaderboard row slice
- final brand frame
- empty or near-empty stage frames for clean clip in/out
- upright/front-facing UI plates for AI-video interpolation when a tool struggles with angled UI

Weak frame types:

- generic centered SaaS card
- full fake phone screen with many labels
- busy dashboard collage
- realistic cinematic sports scene
- background full of decorative objects
- reference concept copied verbatim
- repeated centered glass cards with equal visual weight
- using the same compositional trick on every frame, such as all angled UI plates or all centered cards

## Generation Workflow

### Step 1 - Study

Inspect source assets and summarize:

- product truth
- narrative spine
- visual language
- taste borrow/do-not-borrow rules
- text policy
- avoid list
- output plan

### Step 2 - Baseline Frame

Generate one baseline frame first.

Use `$imagegen` / built-in `image_gen`. Keep the prompt concise but precise. Do not over-expand; longer prompts can make video and image tools worse.

### Step 3 - Inspect

Open the baseline frame with image inspection.

Judge it in taste language:

- too cardish
- too graphic
- too realistic
- too generic SaaS
- too much background
- not faithful to app
- text disrupts cohesion
- copied reference too literally

If it fails, regenerate with one targeted correction. Do not generate the full set until the baseline direction is acceptable.

### Step 4 - Generate Set

Generate each distinct frame with its own prompt. Keep composition and visual language consistent across prompts.

For each frame:

- name the frame
- state what product module is shown
- state what motion the still implies
- include exact text only if the text policy allows it
- repeat the critical avoid rules

### Step 5 - Save And Log

For every generated frame copied into the workspace, log:

- output filename
- source generated image path when available
- exact prompt
- status: accepted, rejected, regenerated
- short reason

Use a local `prompts.md` or `prompt-log.md` in the storyboard folder.

### Step 6 - Contact Sheet

Create a contact sheet from accepted final frames for visual comparison. This is an index artifact, not manual frame editing.

### Step 7 - Quality Gate

Review the contact sheet and individual frames. Regenerate any frame that breaks cohesion.

Do not manually fix broken frames.

### Step 8 - Upload Batches

If requested, create upload-ready folders with sequential copies only.

Examples:

```text
omni/chat-1/
omni/chat-2/
higgsfield/batch-1/
higgsfield/batch-2/
```

Respect platform image-count limits and preserve story order.

### Step 9 - Motion Handoff Prompts

Create motion-handoff prompts only when the user asks for AI-video input, clip generation prompts, editing guidance, or a tool-specific handoff. Do not make motion prompts a mandatory part of every storyboard.

When making motion prompts, group frames by story arc, not by arbitrary count. Strong groups usually contain one of these arcs:

- setup -> reveal -> resolved object
- question -> product choice -> product action
- action -> reaction -> confirmation
- invitation -> proof -> brand resolve

The grouping can be 2, 3, 4, 5, or more frames depending on the tool and the motion arc. Do not hard-code ranges such as 1-3 or 4-8 into the skill. Ask or infer based on the accepted storyboard.

For each group, save a prompt file with a descriptive name. Examples:

```text
shot-agent-reveal.md
shot-prediction-flow.md
shot-social-proof.md
shot-brand-resolve.md
```

If exact frame ranges are known and useful, include them in the filename, but treat this as project-specific:

```text
frames-04-08-prediction-flow.md
```

Every multi-image motion prompt should explicitly state how the images should be interpreted:

```text
Use the connected images as sequential keyframes in this exact chronological order:
1. <describe keyframe 1>
2. <describe keyframe 2>
3. <describe keyframe 3>

Animate one continuous product-launch motion graphic shot that flows through these keyframes in order.

Do not treat the connected images as separate style references. They are the timeline.
```

When clips will be stitched, add a stitch strategy only if it matches the user's workflow:

```text
Animate the first keyframe in from a clean empty stage, and animate the final keyframe out into a clean empty stage, so this clip can be stitched smoothly with neighboring clips.
```

For UI-heavy keyframes, add stability constraints when needed:

```text
Keep the UI stable and preserve exact text, layout, colors, flags, scores, and typography. Do not warp, redesign, or invent new UI.
```

If the tool's image order is ambiguous, describe the intended order by content. Do not rely on visual node order alone.

## Prompt Pattern

Use this compact pattern for imagegen prompts:

```text
Create ONE production-grade 9:16 storyboard frame for <product/video>.

Frame: <number/name>.

Product truth: <what this product actually does>.

Style: <visual language from real product + taste refs>. Borrow <specific qualities> from references. Do not copy <specific concepts/text/layout>.

Composition: <one clean product-motion frame, with clear crop/stage/module>.

Exact readable text only, if any:
<short lines>

Avoid: <specific avoid list>.

Quality: must feel like a screenshot from a polished SaaS product-launch motion-design video, cohesive with the accepted frames.
```

Keep prompts shorter when the model starts overfitting or adding unwanted detail.

## Quality Gate Checklist

Reject/regenerate if any are true:

- frame looks like a generic template
- frame is too cardish when the taste calls for cropped modules
- background has too much graphic clutter
- product UI does not resemble source screenshots
- generated text is misspelled or gibberish
- there are placeholder bars where real text should be
- logo/brand mark is fake or mutated
- external reference concept was copied too literally
- one frame has a different visual system from the rest
- motion implied by the still is unclear
- it looks like a realistic sports ad instead of product motion
- downstream AI video would likely treat the frame as unstable because the UI is too angled, warped, cramped, or visually ambiguous

For final AI-video-ready storyboards, also check sequence rhythm:

- not every frame should carry the same amount of UI density
- dense product frames should be separated by quieter hook, reaction, confirmation, social, or brand beats
- action, reaction, and confirmation should usually be separate frames, not crammed into one
- leaderboard/proof frames should make one row or one stat the hero rather than showing a busy table

## Voice And Video Prompting

When the user asks for AI-video prompts, keep them short. Over-detailed prompts often make the video worse.

Use 1-2 sentences unless the user asks for a detailed prompt.

Example:

```text
Make a clean SaaS product launch motion-graphics video using the attached screenshots as the visual style and storyboard. Keep it faithful to the screenshots with subtle UI motion, dark teal gradients, crisp product elements, and no extra scenes, people, stadium footage, fake logos, or invented text.
```

## Claude Code / Codex Headless Note

This skill is Codex-native when frame generation is required because it depends on Codex `$imagegen` / built-in `image_gen`.

If a non-Codex host invokes this skill:

1. Plan and inspect source assets locally if possible.
2. Ask Codex/headless to perform imagegen frame generation.
3. Preserve this skill's no-manual-edit rule.
4. Return generated frame paths, prompt logs, and contact sheets to the calling host.
