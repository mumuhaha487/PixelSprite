---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost) 16-bit chunky low-res pixel-art game animations with 6-Dimension Skeletal-Continuity Choreography, Sub-Action Anticipation Law (every strike has its own chamber/prep frame!), Multi-Part Chained 18+ Frame Combos, purposeful unified-theme wide-arena VFX (96x80), auto pixel-fitted Hitboxes/Hurtboxes, dual-leg kinematic gait guides, and selective hitstop timing.
---

# PixelSprite v2.5 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, locomotion cycles, high-precision multi-hit combat combos, ultimates, or engine-ready hitbox/frame-data sprite packs.

## v2.5 Golden Rules

0. **SUPREME RULE — 6-Dimension Skeletal Choreography + Sub-Action Anticipation Law + Unlimited Chained Frame Counts!**
   - GPT Image 2.6 is ONLY the pixel renderer — YOU design every joint transition, limb pose, and purposeful VFX pixel first!
   - **6 Mandatory Per-Frame Fields (`frame_choreography[]`)**: `transition_from_prev` (bone link from `F[i-1]`), `torso`, `arms_weapon`, `legs_feet` (Near-Right & Far-Left separately!), `secondary_motion`, and `vfx_meaning` (strictly `NONE` on locomotion; ONE unified elemental theme with physical Origin + Trajectory + Combat Meaning on skills!).
   - **Sub-Action Anticipation Law (`子招前摇铁律`)**: EVERY distinct strike inside a multi-hit combo MUST have its own explicit **preparation / chamber frame** before impact (e.g., uppercut → overhead cock-back chamber → floor chop → **waist thrust chamber** → mid-thrust → full lance thrust → retract pull-back → hip-sheath scar ignition → detonation)! NEVER skip prep frames just to squeeze a combo into 8–11 frames!
   - **Multi-Part Chained Sheets (`chained_parts`)**: For complex 15–24+ frame combos, split into spacious chained sheets (`Part 1: 4×3` + `Part 2: 3×3` stamping Part 1's actual quantized bridge frame in Cell 1 & Master Anchor `F1` in Cell 9!) so cells stay `384–512px` wide with ZERO resolution loss!
   - ALWAYS run `python -m pixelsprite validate <spec>` (or `--strict-choreography`) BEFORE calling the API!

1. **Chunky Low-Res Character (`34px`) in Wide Combat Arena (`96×80`, Pivot `[30, 71]`)**: Identical 34px chibi proportions across every action, `66px` forward + `40px` upward open VFX arena.
2. **Automatic Combat Frame Data (`combat.py`)**: Export clean transparent strips (`*_96x80.png`) + `*_meta.json` (`startup`/`active`/`recovery`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox`, red pixel-fitted `hitboxes`) + `*_framedata_audit_3x.png`.
3. **Dual-Leg Color-Coded Kinematic Gait Guides (`guide.py`)**: `walk` & `run` draw Yellow (Near/Right) vs Cyan (Far/Left) leg skeletons enforcing Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Swap (`F5`) with strict zero-VFX isolation.
4. **Selective Timing & Visual QC**: Even `walk`/`run`; anticipation/chamber holds + snappy smears + climax HITSTOP on skills. Always visually inspect every sub-action chamber pose, splice seam, loop seam, and Hitbox tightness before delivery.

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite validate skill_phantom_flurry
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim skill_phantom_flurry --strict-choreography --out output/hero
python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4
```
