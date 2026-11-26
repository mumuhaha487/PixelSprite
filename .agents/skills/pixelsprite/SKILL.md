---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost anchor) 16-bit chunky low-res pixel-art game animations with wide-arena multi-layered arcade VFX (96x80 canvas, 34px fixed character height), automatic pixel-fitted Attack Frames / Hitboxes / Hurtboxes, variable frame counts (8/11/14+), and selective hitstop timing.
---

# PixelSprite v2.2 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, combat combos, flashy skills, or engine-ready hitbox/frame-data sprite packs.

## v2.2 Golden Rules

1. **Chunky Low-Res Character (`34px`) in Wide Combat Arena (`96×80`, Pivot `[30, 71]`)**: Keep the character chunky low-res (2-head chibi, 14–18 flat colors, 1px dark outline), anchored in the left third (`x = 30`) so **`66px` wide open VFX space** lets slashes, afterimages, magic circles, ground dust shockwaves, and starfall novas explode at full arcade scale with ZERO body shrinking or clipping!
2. **Automatic Combat Frame Data (`combat.py`)**: Export clean production strips (`*_96x80.png`) paired with per-frame `frameData[]` in `*_meta.json` (`phase`: `startup`/`active`/`recovery`, `isAttackFrame`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox` from `body_mask`, and red `hitboxes` auto-fitted to actual VFX/weapon pixels on active frames!) plus `*_framedata_audit_3x.png`.
3. **Spacious Single-Action Closed-Loop Grids (`N + 1` Ghost Anchor)**:
   - `8` active frames (`idle`/`walk`/`run`/`combo1_slash`) → `3×3` (`1536×1024` widescreen for `combo1_slash`, `1024×1024` for locomotion).
   - `11` active frames (`skill_phantom_flurry`) → `4×3` (`1536×1024`).
   - `14` active frames (`ult_starfall_slash`) → `5×3` (`1536×1024`).
4. **24-Color Arcade VFX Ramp + Body-Isolated Zero-Teleport Quantizer**: Protect 4–5 step glowing cyan/pink/gold/violet/dust VFX ramps, never outline glowing VFX, isolate `body_mask` cleanly from large flame/nova cores (without touching small hair highlights), and lock grounded baselines while preserving smooth airborne parabolas.
5. **Selective Timing & Forensic QC**: Keep `walk`/`run` strictly even; give combat skills anticipation holds, snappy strike smears, and climax HITSTOP. Inspect every `*_framedata_audit_3x.png` & extracted MP4 frames before shipping.

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim skill_phantom_flurry --out output/hero
python -m pixelsprite showcase-v2 --metas output/hero/anim_*_meta.json --loops 3 --out output/hero/showcase_v2.mp4
```
