# Animation presets (`layers[].fx`)

| fx | Motion | Use |
|---|---|---|
| `pop` | spring scale-in | props, signs, bubbles |
| `pop_wobble` | spring + decaying wobble | surprised/excited figures |
| `bounce` | drop with 2 decaying bounces | objects landing, jumping figures |
| `drop` | falls from top, small settle | heavy things falling |
| `slide_left` | enters from the right with cubic ease | characters running in |
| `spin_grow` | rotating grow from small | portals, explosions, magic |

Extras: `exit_anchor` + `exit_fx: suck` (spins/shrinks away; `none` = cut out), `shake_anchor` (0.6 s shake), `z` 2–9 (higher on top; background is 1). All stickers also breathe (±1.5% scale) and line-boil (small rotation jitter) automatically.

Placement: `x,y` = sticker centre (0–1 of frame), `w` = width fraction. Typical figure w 0.35–0.55, prop 0.2–0.35. Keep important parts above y≈0.8.
