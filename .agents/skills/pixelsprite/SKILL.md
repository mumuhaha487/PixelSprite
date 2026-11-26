---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost anchor) 16-bit chunky low-res pixel-art game animations with body-isolated zero-teleport quantization (64x64 canvas, 34px fixed character height), spacious single-action grids (3x3/4x3/5x3), variable frame counts (8/11/14+), and selective hitstop timing.
---

# PixelSprite v2.1 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, combat combos, or flashy skills.

## v2.1 Golden Rules

1. **Chunky Low-Res Character inside Generous Canvas (`34px` char in `64×64` cell)**: Keep the character chunky low-res (2-head chibi, 14–18 flat colors, 1px dark outline), never stiff paper-doll rigs. Use a generous `64×64` transparent canvas (`gba_chibi`) so giant skill VFX NEVER shrink or clip the character!
2. **Spacious Single-Action Closed-Loop Grids (`N + 1` Ghost Anchor)**: NEVER cram 9 narrow columns onto one strip (it squishes sprites & chops off weapons!). Give every action its own spacious grid with Ghost Cell `N + 1 == F1` stamped in the guide and **stripped** from the exported strip:
   - `8` active frames (`idle`, `walk`, `run`, `combo1_slash`) → **`3×3` (`1024×1024` = `341×341`/cell)**
   - `11` active frames (`skill_phantom_flurry`) → **`4×3` (`1536×1024` = `384×341`/cell)**
   - `14` active frames (`ult_starfall_slash`) → **`5×3` (`1536×1024` = `307×341`/cell)**
3. **Body-Isolated Quantization (`quantizer.py`)**: Measure `body_cx`, `body_h`, and `body_foot_y` strictly from non-VFX `body_mask` so:
   - `idle`/`walk`/`run` have `0.0px` X jitter (`lock_body_x=True`) and skills lunge smoothly (`[-3, +6]px`) without teleporting,
   - Character height stays locked (`~34px`) across every action (zero VFX shrinking!),
   - Airborne jumps preserve true mid-air height even when ground sparks/rays appear underneath,
   - 1px ink outline patching touches ONLY non-VFX body pixels (zero dark crust on slashes/flames/stars!).
4. **Selective Per-Frame Timing (`frameDurationsMs`)**: Keep `walk`/`run` strictly even (`95ms` / `75ms`); apply anticipation holds (`180–195ms`), snappy strike smears (`50–60ms`), climax HITSTOP (`225–265ms`), and stylish finish holds (`165–215ms`) only on combat/skill beats.
5. **Forensic + Visual QC Before Delivery**: Inspect every `*_loop_audit_3x.png` and extracted MP4 frames; verify `maxBodyDX`, `bodyH`, weapon intactness, and `F[N] → F1` RGB seam continuity. Re-generate any individual failing action with `python -m pixelsprite action --anim <id>`.

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim skill_phantom_flurry --out output/hero
python -m pixelsprite showcase-v2 --metas output/hero/anim_*_meta.json --loops 3 --out output/hero/showcase_v2.mp4
```
