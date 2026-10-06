# Layer breakdown

For each scene, list: setting → background; actors/props that *change* during narration → stickers.

| Narration fragment | Visual event | Layer |
|---|---|---|
| "The emperor yawns" | emperor appears, sleepy | sticker `emperor_sleepy`, fx `pop`, anchor "emperor" |
| "when a goose bursts in" | goose slides in | sticker `goose`, fx `slide_left`, anchor "goose" |
| "and bites his beard" | emperor shakes | `shake_anchor` "bites" on emperor layer |

Rules
- Background never contains figures; describe depth and open floor space.
- Sticker = one figure OR one prop, full body, centred, explicit pose/expression/costume. No scenery, no ground.
- Visible text only through `visible_text` (e.g. a sign); keep it short.
- A new pose = a new sticker; same pose in a later scene = reuse.
- Every sticker must be used by at least one layer (`LAYER_UNUSED`).
- First layer usually anchors on the scene's first word so the frame is never empty.
