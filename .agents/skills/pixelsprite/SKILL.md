---
name: pixelsprite
description: Generate seamless closed-loop (N+1 ghost) 16-bit chunky low-res pixel-art game animations with 6-Dimension Skeletal-Continuity Choreography, Sub-Action Anticipation Law, Tri-Phase Power Rhythm (Charge Hold -> Fast Swing -> Impact Hitstop -> Normal Recovery -> Inter-Move Link Pause), Calm Grounded Splice Anchors for 18-24+ frame multi-part chains, Monotonic Airborne Parabolas, wide-arena VFX (96x80), auto pixel-fitted Hitboxes/Hurtboxes, and dual-leg kinematic gait guides.
---

# PixelSprite v2.6 Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game character animations, locomotion cycles, high-precision multi-hit combat combos, ultimates, or engine-ready hitbox/frame-data sprite packs.

## v2.6 Golden Rules

0. **SUPREME RULE — 6-Dim Skeletal Continuity + Sub-Action Anticipation + Tri-Phase Power Rhythm + Calm Splice Anchors!**
   - GPT Image 2.6 is ONLY the pixel renderer — YOU design every joint transition, limb pose, timing beat, and purposeful VFX pixel first!
   - **6 Mandatory Per-Frame Fields (`frame_choreography[]`)**: `transition_from_prev`, `torso`, `arms_weapon`, `legs_feet` (Near-Right & Far-Left separately), `secondary_motion`, and `vfx_meaning` (`NONE` on locomotion & splice frames; ONE unified elemental theme on skills).
   - **Sub-Action Anticipation Law (`子招前摇铁律`)**: EVERY distinct strike MUST have its own **chamber/charge hold** AND **fast-motion swing frame** before impact — NEVER skip anticipation or motion frames!
   - **Tri-Phase Power Rhythm (`三段力量节拍` — `timing_mode: "tri_phase_power"`)**: Structure heavy combos as **`charge_hold` (`190–235ms`) → `motion` (`50–60ms`) → `hitstop` (`225–245ms`) → normal `recovery` (`75–85ms`) → `link_pause` (`130–145ms`)**. Avoid sluggish >250ms holds or mid-recovery freezes!
   - **Calm Grounded Splice Anchor Law (`稳态桥接铁律`)**: For 2-part / 3-part `chained_parts` (`18f` / `24f+`), ALWAYS put `splice_from_prev_frame` on a **calm, grounded, full-height (`34px`), ZERO-VFX stance or `link_pause` frame** — NEVER splice on crouched/airborne/floor-ember VFX frames (prevents Hurtbox bloat & `±6px` X-teleports!).
   - **Monotonic Airborne Parabola Law (`腾空抛物线单调铁律`)**: Airborne jumps MUST follow a smooth curve (`0 → +7 → +14 → +20 APEX → +12 → +4 → 0`, max `|dy| <= 10px`) with distinct ascent vs apex poses and ZERO floor rings underneath grounded boots.
   - ALWAYS run `python -m pixelsprite validate <spec>` (or `--strict-choreography`) BEFORE calling the API!

1. **Chunky Low-Res Character (`34px`) in Wide Combat Arena (`96×80`)**: Identical 34px chibi proportions across every action, generous forward & upward open VFX arena, post-quantization continuity stabilizer guaranteeing `maxBodyDX <= 4.0px`.
2. **Automatic Combat Frame Data (`combat.py`)**: Export clean transparent strips (`*_96x80.png`) + `*_meta.json` (`startup`/`active`/`recovery`/`link_pause`, `rhythmBeats`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox`, red pixel-fitted `hitboxes`) + `*_framedata_audit_3x.png`.
3. **Dual-Leg Color-Coded Kinematic Gait Guides (`guide.py`)**: `walk` & `run` draw Yellow (Near/Right) vs Cyan (Far/Left) leg skeletons with strict zero-VFX isolation.
4. **Hard QC Gate**: NEVER ship `AUDIT WARN` (`seam_smooth: false`), `maxBodyDX > 4.0px`, `maxBodyDY > 12px`, `MaxHurtW > 38px`, or `SPLICE iou < 0.70`. Inspect both `*_framedata_audit_3x.png` and `--power-test` slow-mo MP4 visually before delivery!

## Commands

```bash
python -m pixelsprite list
python -m pixelsprite validate skill_tri_phase_breaker
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim skill_tri_phase_breaker --strict-choreography --out output/hero
python -m pixelsprite showcase-v2 --metas output/hero/anim_skill_tri_phase_breaker_24f_meta.json --power-test --loops 3 --out output/hero/power_test.mp4
python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_tri_phase_breaker,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4
```
