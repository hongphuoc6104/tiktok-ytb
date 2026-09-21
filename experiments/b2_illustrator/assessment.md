# B-2 Illustrator — live assessment

Observed 2026-09-21 in the user-owned Chrome session, project
`7c815425-4625-4afb-ba84-4290d3fa9ea4`, Community tool `B-2 Illustrator`.
The raw UI snapshot is [results/live-ui-assessment.json](results/live-ui-assessment.json)
and the screenshot is [results/b2-live.png](results/b2-live.png). These are
assessment artifacts, not production preflight evidence.

The tool exposes scene tags, an action description, light/dark mode, accent
color, and two character modes (`Profession`, `Ancient`). More options showed
Pin and Report only; no Remix action was visible. Tool Builder was visible,
but no separate editable copy was confirmed and no Community tool edit was
sent.

One isolated image test was authorized under the separate B-2-only ceiling of
1050 credits. The test produced [results/b2-001.jpg](results/b2-001.jpg),
with screenshot [results/b2-attempt-001.png](results/b2-attempt-001.png) and
journal [results/attempt-001.json](results/attempt-001.json). The result was
visually a useful orange-shirt stick figure at a gray table with a blue cup;
the only visible label was `cup` in blue. The tool footer declared
`Style Locked B2 Digital Editorial`, `1920x1080`, and `Nano Banana Pro`.

The downloaded asset was JPEG at 1376×768, despite the tool-declared
1920×1080. The output is therefore not safe to pass through the production
image contract without an explicit export/dimension check. The journal records
`charged_credits: null`; actual spend is unknown and must not be inferred from
the authorization ceiling.

Current recommendation: keep B-2 as an isolated candidate for a custom
wrapper. The style is promising, but the live UI did not expose character
reference uploads, base-scene chaining, batch output, individual-output
mapping, or a Remix action. A custom copy should be considered only after
Tool Builder proves that it creates an independent tool and after the wrapper
captures tool identity/version, expanded prompt provenance, actual dimensions,
and charge evidence. Production configuration and runs remain unchanged.
