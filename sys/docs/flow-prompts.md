# Versioned Google Flow image prompts

The active registry is `sys/flow_prompts/versions/1.0.0/registry.json`. It defines authored instruction strategies for the **observed Flow UI labels** Nano Banana Pro, Nano Banana 2 and Nano Banana 2 Lite; stable registry IDs are `NanoBananaPro`, `NanoBanana2` and `NanoBanana2Lite`. Both exact forms are accepted. Similar names, other models and unknown versions fail before dispatch.

These profiles are different writing strategies, not model benchmarks. The registry does not claim lower costs, better accuracy, shorter latency, a guaranteed output count or model-specific capabilities. The coordinating agent supplied the observed UI labels and the current integration limit: one Character reference and at most one Base scene reference. Compilation does not observe the UI, attach images or verify costs.

## Compile contract

```python
from flow_prompts import compile

result = compile("Nano Banana 2 Lite", "scene", {
    "description": "A bird takes a seed from a bowl; the mascot points at the visible change.",
    "aspect_ratio": "9:16",
    "character_reference": {
        "media_id": "de94a39b-155f-4afe-acbb-d9d4b59ad532",
        "sha256": "54954545162069406075e6d41306428fbcee3cb800c587644ce132d0cf37befd"
    },
    "allowed_text": [{"text": "I took one seed.", "placement": "upper left", "object": "speech bubble"}],
    "caption_clearance": {"edge": "bottom", "fraction": 0.18}
}, "1.0.0")
```

The result is JSON-compatible: `prompt`, `model`, `model_id`, `purpose`, `template_id`, `version`, `sha256` and `provenance`. The prompt hash is SHA-256 of the actual UTF-8 prompt. Provenance includes the registry fingerprint, exact input fingerprint, reference media IDs/hashes and the instruction-strategy source. `attachment_verified`, `quality_verified` and `cost_verified` are false; successful compilation proves none of them.

Purposes:

| Purpose | Instruction function | Reference requirements |
|---|---|---|
| `reference` | Establish the requested base composition, setting and teaching focus | Character mandatory; Base optional when a preserved shot is declared |
| `character` | A clean reference of the single canonical mascot | Character mandatory; reference framing may enlarge the mascot for inspection |
| `scene` | Causal action, state, comparison or diagram in a final teaching/story frame | Character mandatory; Base mandatory when `preserve` is nonempty |
| `variation` | Preserve an actual base shot and make a declared change visible | Character and Base mandatory; nonempty `preserve` and `change` |

Allowed input fields are `description`, `aspect_ratio`, `allowed_text`, `character_reference`, `base_reference`, `preserve`, `change`, `composition`, `mascot_placement` and `caption_clearance`. Other controls such as output count, arbitrary instructions, provider/model switches or negative-prompt fields fail explicitly. References require exactly `media_id` and `sha256`; arrays of references are rejected. A UUID/hash declaration is syntactic provenance, not evidence of a real attachment. The caller must verify the existing artifact bytes, owning Flow project/session, actual Character/Base slot and matching media ID before submit.

`allowed_text` accepts exact strings or records containing `text` and optional `placement`/`object`. No language conversion, spelling correction, case conversion, Unicode normalization or whitespace stripping is applied to these data. Layout metadata is not extra lettering. Empty allowed text means no lettering. Management IDs, scene/character codes, media UUIDs, filenames and hashes are prohibited as visible text. Recognizable instruction-override markers, role delimiters, template delimiters, control characters and unsupported fields fail clearly. This bounded syntactic check is not a claim to detect every possible semantic prompt injection.

Caption clearance supports `top` or `bottom` and a fraction from `0.10` to `0.40`. Placement supports `upper-left`, `upper-right`, `left-margin`, `right-margin`, `above-caption-left` and `above-caption-right`. The prompt keeps the caption band quiet and required text away from crop edges; it does not set subtitle timing or prove phone-size readability.

## Visual contract

All profiles use bright flat 2D illustration with bold outlines and readable props/diagrams. They ask for the canonical mascot's round white navy-outlined head, simple solid-black oval eyes, one light-blue `#8CCFE8` short-sleeve shirt, stick limbs and one torso. Subtle brows, sweat, forehead lines, mouth expressions and rounded hands/feet are allowed by the brand's 80/20 rule. Final scene/variation frames keep the mascot small, visible and useful for directing attention; a character-reference image can use larger inspection framing. The tolerance cannot excuse wrong action, wrong meaning or missing mascot.

The compiler imposes no fixed scene/image count, comedy structure, sound effects or topic. Narration, learner text and current job contracts remain their own data. Actual image inspection, continuity checking and learner-text readability are separate evidence; prompts/hashes do not certify them.

## Freeze before first send; retain legacy prompts

```python
from flow_prompts import freeze, compile_pinned

pin = freeze(model, "1.0.0", existing_pin=saved_pin, request_states=actual_journal_states)
# The official engine operation stores this pin, its source and the event.
result = compile_pinned(pin, purpose, visual_data)
```

`freeze` is pure: it grants no permission, does not inspect or write a job, does not migrate history and does not submit. The authorized caller must collect the complete relevant request states under its normal job ownership lock, then save the pin through the official engine operation **before the first send**. Pass all request states, including reference-generation and cached requests; do not inspect only final scene requests.

An absent pin is refused when any request is submitted, generated, downloaded, cached, unknown, ambiguous, complete or otherwise outside pending/prepared/not_submitted. Thus an already-downloaded legacy reference, such as the existing Alpha reference, retains its original generic prompt and request identity. An existing pin must match the requested model/version and current registry fingerprint exactly. Unknown future versions and changed registry bytes require an explicit versioned development transition, never implicit adoption.

A job missing the new version/pin keeps the legacy requested-prompt path. Previously stored actual prompts, hashes, cached/submitted/unknown requests and old revisions are not recompiled, rewritten or adopted. A repair can create a new request only through the existing job/impact workflow after unknown work is reconciled; changing template metadata does not authorize a resend. `prompt_templates.py` remains unchanged.

## Verification scope

`python3 -m unittest tests.test_flow_prompts -v` checks all three models and four purposes, deterministic prompt/provenance hashes, exact learner data, 80/20 wording, reference/continuity validation, unsupported models/versions/fields, injection markers, forbidden management text, pure freeze semantics and changed-registry rejection. These are compiler contracts, not Flow/T4/media/quality evidence. Provider integration and live artifact evaluation remain the caller's separate work.

## Installed caller integration

New engine-4 jobs whose saved control configuration contains `flow_prompt_version` receive a pin in workflow metadata and `flow/prompts/pin.json`, with a `flow_prompt_frozen` event. The official `execution.new` operation performs that persistence under the job lease before any provider image send. The current configuration selects `1.0.0` for newly created jobs. The effective Flow configuration uses the complete saved control configuration; an old job does not inherit a newly added live-config template field.

`image_pipeline._plan_request` compiles both single and batch requests from the same pin and mapping. Character references resolve exactly as the actual adapter does: canonical bytes/media ID for the canonical reference, or the hash/UUID of the proven downloaded registration artifact. Base references use the exact predecessor's downloaded bytes and sidecar media ID. The request identity retains a `prompt_template` compilation record with pin, visual data, purpose, hashes and provenance. Character-reference and registration frames may use full-body inspection framing; final scenes keep the small mascot. Corrections enter the declared change data without modifying learner lettering.

The Flow send callback validates the current pin and the saved actual compiled prompt immediately before the socket/provider boundary, along with the existing lease/account/project/reference controls. Technical image checks reproduce saved compilation provenance and compare actual Character attachment media ID/hash. These checks do not prove perceived mascot similarity or teaching quality.

An old saved control without `flow_prompt_version` continues through the unchanged legacy requested-prompt wrapper. Its downloaded request bytes/key/actual prompt remain unchanged when the global template version is added. No existing job or downloaded Alpha reference was migrated by this implementation.

`tests.test_flow_prompt_integration` runs a new-job CLI subprocess, official author/engine operations, the real Python Flow adapter and a fake B2 response boundary in a temporary root/home/budget store. It checks pin-before-send, callback guards, model provenance, identical cached replay, legacy bytes/no-resubmit, single/batch/variation mapping and tamper refusal before dispatch. The generated test PNGs are fixtures; no actual Flow/T4/media action is performed.
