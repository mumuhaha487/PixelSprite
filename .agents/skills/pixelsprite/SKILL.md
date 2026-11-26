---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost anchor) 16-bit chunky low-res pixel-art game animations with variable frame counts (8/11/14/16+ frames) and selective keyframe hitstop timing using GPT Image 2.6 + NumPy pixel quantization.
---

# PixelSprite v2.0 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, combat combos, or flashy skills.

## v2.0 Golden Rules

1. **Chunky Low-Res Chibi Pixel Grid (`32px` / `48px` / `64px`)**: Never use stiff paper-doll rigs or blurry high-res frames. Always quantize the Master Anchor first (`python -m pixelsprite anchor`).
2. **Closed-Loop `N + 1` Ghost Frame**: For every looping animation of `N` active frames, generate `N + 1` cells with the exact translucent `F1` anchor stamped in BOTH Cell `1` and Ghost Cell `N + 1`. Audit `F[N] ↔ F[N+1]` & `F[N+1] ↔ F1` visually + via IoU, then **exclude** Ghost Cell `N + 1` from the final exported strip.
3. **Variable Frame Counts by Action Complexity**:
   - Short locomotion/idle/basic attack: `8` active frames (`9×4` pack via `pack9`).
   - Medium multi-hit skills: `11–12` active frames (`4×3` = `11+1` via `action`).
   - Long cinematic ultimates: `14–16` active frames (`5×3` = `14+1` or `6×3` = `16+1` via `action`, or custom JSON).
4. **Selective Variable Frame Timing (`frameDurationsMs`)**:
   - Keep `walk` / `run` **evenly timed** (no awkward pauses!).
   - Give combat/skill actions **anticipation holds** (`170–195ms`), **snappy strike smears** (`50–60ms`), **impact HITSTOP freezes** (`220–265ms`), and **stylish finish holds** (`165–215ms`).

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite anchor --desc "<character>" --style gba_48 --out output/hero
python -m pixelsprite pack9 --anchor output/hero/01_anchor_pixel_48px.png --desc "<character>" --pack core_9x4_closed --out output/hero/v2
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_48px.png --desc "<character>" --anim skill_phantom_flurry --out output/hero/v2
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_48px.png --desc "<character>" --anim ult_starfall_slash --out output/hero/v2
python -m pixelsprite showcase-v2 --metas output/hero/v2/core_9x4_closed_meta.json output/hero/v2/anim_skill_phantom_flurry_11f_meta.json output/hero/v2/anim_ult_starfall_slash_14f_meta.json --out output/hero/v2/showcase_v2.mp4
```
