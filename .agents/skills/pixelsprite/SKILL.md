---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost anchor) 16-bit chunky low-res pixel-art game animations using strict 5-Dimension Per-Frame Choreography (never vague image prompts!), purposeful physics-driven wide-arena VFX (96x80), auto pixel-fitted Attack Frames / Hitboxes / Hurtboxes, dual-leg kinematic gait guides, and selective hitstop timing.
---

# PixelSprite v2.3 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, locomotion cycles, combat combos, flashy skills, or engine-ready hitbox/frame-data sprite packs.

## v2.3 Golden Rules

0. **SUPREME RULE — NEVER Delegate Action or VFX Design to GPT Image 2.6!**
   - GPT Image 2.6 is ONLY the pixel renderer, NEVER the choreographer!
   - NEVER pass vague prompts ("walk cycle", "cool sword slash", "flashy particles"). Vague prompts cause broken one-legged walks and meaningless random glow blobs!
   - BEFORE calling the API on ANY action, YOU MUST author an explicit **5-Dimension Per-Frame Choreography Spec (`frame_choreography[]`)** for EVERY cell (`F1..F[N]` + `Ghost F[N+1]=F1`) — see `examples/custom_action_template.json`:
     1. **`torso`**: Spine lean, hip height bob/airborne lift, shoulder wind-up/uncoil, head gaze.
     2. **`arms_weapon`**: Exact position & swing plane of BOTH hands + weapon angle + opposite arm-leg counter-swing.
     3. **`legs_feet`**: Explicit separate positions for **Near/Right leg** and **Far/Left leg** (planted, sliding back, toe push-off, vertical center crossover, forward reach, lunge brace, airborne tuck).
     4. **`secondary_motion`**: Hair/ponytail/scarf/cape drag & follow-through.
     5. **`vfx_meaning`**: Strictly `"NONE"` on locomotion; on combat skills, every VFX pixel MUST have explicit **Physical Origin (blade/boots/torso) + Directional Trajectory (matching swing/lunge) + Combat Meaning (Startup telegraph / Active Hitbox readability / Recovery force dissipation)**!
   - Always run `python -m pixelsprite validate <spec>` (or `--strict-choreography`) BEFORE generating!

1. **Chunky Low-Res Character (`34px`) in Wide Combat Arena (`96×80`, Pivot `[30, 71]`)**: Keep the character chunky low-res (2-head chibi, 14–18 flat colors, 1px dark outline), anchored in the left third (`x = 30`) so `66px` wide open VFX space lets purposeful combat effects unfold with ZERO body shrinking or clipping.
2. **Automatic Combat Frame Data (`combat.py`)**: Export clean production strips (`*_96x80.png`) paired with per-frame `frameData[]` in `*_meta.json` (`startup`/`active`/`recovery`, `isAttackFrame`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox`, red pixel-fitted `hitboxes`) plus `*_framedata_audit_3x.png`.
3. **Spacious Closed-Loop Grids (`N + 1` Ghost) + Dual-Leg Color-Coded Kinematic Gait Guides**:
   - For `walk` and `run`, `guide.py` renders an explicit **Yellow (Near/Right) vs Cyan (Far/Left) articulated kinematic leg skeleton** enforcing Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Left/Right Swap (`F5`) with strict zero-VFX isolation (`preserve_vfx=False`).
   - `8+1f` → `3×3` (`1536×1024` combat / `1024×1024` locomotion); `11+1f` → `4×3`; `14+1f` → `5×3`.
4. **Selective Timing & Visual QC**: Keep `walk`/`run` strictly even; apply anticipation holds, snappy strike smears, and climax HITSTOP on combat skills. Always visually inspect `walk`/`run` leg alternation, `*_framedata_audit_3x.png` hitbox tightness & VFX physical meaning, and extracted MP4 frames before delivering.

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite validate examples/custom_action_template.json
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim examples/custom_action_template.json --strict-choreography --out output/hero
python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4
```
