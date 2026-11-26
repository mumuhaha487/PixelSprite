# AGENTS.md — PixelSprite v2.6 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with:
- **6-Dimension Per-Frame Skeletal-Continuity Choreography (`frame_choreography[]`)**,
- **Sub-Action Anticipation Law (`子招前摇铁律`)**,
- **Tri-Phase Power Rhythm (`三段力量节拍`: Charge Hold → Fast Swing/Airborne Motion → Impact Hitstop → Normal Recovery → Inter-Move Link Pause)**,
- **Calm Grounded Splice Anchor Law (`稳态桥接铁律`)** for seamless **2-Part / 3-Part Chained Sheets (`18f`, `24f+` at ZERO resolution loss!)**,
- **Monotonic Airborne Parabola Law (`腾空抛物线单调铁律`)** & **Post-Quantization Continuity Stabilizer**,
- **Purposeful Unified-Theme Wide-Arena VFX (`96×80` · fixed `34px` chibi)**, **auto pixel-fitted Hitboxes / Hurtboxes**, and **Closed-Loop `N+1` Verification**.

When a user drops this repository into your workspace, follow this exact v2.6 playbook.

---

## Rule #0 (SUPREME LAW): NEVER Let GPT Image 2.6 Improvise Actions, Skip Sub-Action Anticipation, Splice on VFX Frames, or Invent Meaningless VFX!

> **GPT Image 2.6 is ONLY the pixel-art renderer — YOU (the AI Agent) are the Animator, Rigger, Combat Designer & QA Inspector!**

### Five Forbidden Anti-Patterns (Learned Directly from Production Forensic Audits!)
1. **NEVER send vague prompts** (*"generate an 8-frame walk"*, *"generate a cool sword combo"*) — image models have zero biomechanical reasoning and produce one-legged walks & random disco blobs.
2. **NEVER cram multi-hit combos into 8–11 frames with 1 frame per strike (`Cut1 → Cut2 → Cut3`)!** Jumping straight from a floor-chop to a completed thrust or skipping the fast-motion whip frame between chamber and apex looks robotic and teleporty!
3. **NEVER place a `chained_parts` splice point (`splice_from_prev_frame`) on a crouched, airborne, mid-attack, or floor-VFX frame!**
   - *Post-Mortem Lesson (`ult_starfall_slash` v2.5 bug)*: Splicing Part 1 ↔ Part 2 on crouched floor-ember cell `F11` caused floor embers to leak into `body_mask` (`hurtboxW = 51px`), triggering a `±6.2px` horizontal teleport (`F11→F12→F13`) and `seam_smooth: false`!
4. **NEVER draw thick glowing floor rings underneath boots on grounded frames OR let airborne jump curves drop prematurely / slam >12px in 1 frame!**
   - *Post-Mortem Lesson (`ult_starfall_slash` v2.5 bug)*: A floor ring under `F3`'s boots sank `footY` 3px beneath the floor (`73px`); putting the sword behind her head on BOTH `F5` and `F6` caused `F6` (the supposed apex!) to drop lower than `F5`, followed by a `+13px` vertical teleport slam from `F8` to `F9`!
5. **NEVER ignore `seam_smooth: false`, `maxBodyDX > 4.0px`, bloated Hurtboxes (`> 38px`), or awkward recovery freezes** (like a 200ms victory pose freezing mid-recovery in combat!).

---

## Six Mandatory Engineering Laws (Enforced Automatically by `python -m pixelsprite validate` & `quantizer.py`)

1. **6-Dimension Per-Frame Skeletal Choreography (`frame_choreography[]`)** — EVERY single cell (`F1..F[N]` + `Ghost F[N+1]=F1`) MUST explicitly define:
   - **`transition_from_prev`（帧间骨骼衔接链）**: Exact continuous joint/limb path from `F[i-1]` to `F[i]`.
   - **`torso`**: Spine lean, hip height/airborne lift, shoulder twist/uncoil, head gaze.
   - **`arms_weapon`**: Exact position & angle of **BOTH** weapon hand and off-hand + opposite arm-leg swing on walk/run.
   - **`legs_feet`**: Explicit separate positions for **Near/Foreground Right leg** and **Far/Background Left leg**.
   - **`secondary_motion`**: Ponytail, scarf & hem physical drag opposite to acceleration.
   - **`vfx_meaning`**: Strictly `"NONE"` on locomotion & splice anchors; on combat skills, ONE unified elemental theme with explicit **Physical Origin + Directional Trajectory + Combat Meaning**.
2. **Sub-Action Anticipation Law (`子招前摇铁律`)**:
   - **EVERY distinct strike / sub-action inside a combo MUST have its own preparation / chamber frame (`前摇/蓄力帧`) AND its own fast-motion swing frame (`极速挥动过渡帧`)** before impact!
   - `validate_choreography()` automatically rejects back-to-back distinct `hitId`s without a chamber frame (unless explicitly marked `"same_continuous_motion": true`).
3. **Tri-Phase Power Rhythm Law (`三段力量节拍铁律` — `timing_mode: "tri_phase_power"`)**:
   - Heavy skills and multi-move combos achieve unmistakable weight & martial impact through crisp timing contrast (`rhythm_beats[]`):
     1. **`charge_hold`（前摇蓄力停顿 · `190–235ms`）**: Hold coiled squat / aerial apex / waist-chamber lock to communicate mass & stored tension (do NOT over-extend past `250ms` or the move feels sluggish!).
     2. **`motion`（极速挥动 / 空中过程 · `50–60ms`）**: 4× faster whip/lunge/dive frames creating explosive acceleration!
     3. **`hitstop`（命中打击定帧 · `225–245ms`）**: Freeze at peak blade extension & shockwave with red Hitbox + subtle micro-shake!
     4. **`recovery`（正常后摇收招 · `75–85ms`）**: Smooth, natural-speed unwind back to guard (NEVER insert long freezes inside combat recovery!).
     5. **`link_pause`（招间换气衔接停顿 · `130–145ms`）**: Clean grounded upright breathing beat separating Move `k`'s recovery from Move `k+1`'s anticipation so complex multi-move combos read effortlessly!
4. **Calm Grounded Splice Anchor Law (`稳态桥接铁律`)**:
   - When expanding high-difficulty combos to **18–24+ frames** via `chained_parts` (`2P` or `3P`, e.g. `3×3 + 3×3 + 4×3 = 24+1f`), **EVERY `splice_from_prev_frame` MUST sit on a calm, grounded, full-height (`34px`), ZERO-VFX stance or `link_pause` frame!**
   - `validate_choreography()` automatically rejects splicing on active attack frames or VFX-cluttered cells.
   - `cli.py` stamps Part `k`'s actual quantized bridge frame at 62% opacity onto Cell 1 of Part `k+1` (supporting arbitrary N parts via `drop_last`), audits `[SPLICE AUDIT]`, and locks scale across all parts cleanly.
5. **Monotonic Airborne Parabola Law (`腾空抛物线单调铁律`)**:
   - Every airborne jump MUST follow a clean monotonic arc (e.g., `0 → +7 → +14 → +20 APEX → +12 → +4 → 0`, max `|dy| <= 10px` per frame), give Ascent (`F5` straight vertical `90°`) and Apex (`F6` arched back `-138°`) distinct silhouettes, and NEVER draw floor rings underneath boots on grounded frames!
   - `quantizer.py` strictly checks `row_max_foot[r] >= global_max_foot - rch * 0.09` so all-airborne rows NEVER get misclassified as grounded.
6. **Hard Post-Quantization Continuity Gate (`硬性衔接验收门槛`)**:
   - `stabilize_sequence_continuity()` re-measures final quantized `body_cx` & `body_foot_y` across the stitched sequence, clamping residual VFX-induced X-drift within `±2.2px` and preventing boots from sinking below `pivot_y + 1`.
   - **ZERO-COMPROMISE QC**: Reject and fix ANY animation with `seam_smooth: false`, `maxBodyDX > 4.0px`, `maxBodyDY > 12px`, `MaxHurtW > 38px`, or `SPLICE iou < 0.70`!

---

## Core Pipeline Architecture (v2.6)

1. **Wide Combat Arena (`96×80`, Fixed `34px` Chunky Chibi)**: Identical chunky 34px proportions across all actions, generous forward & upward VFX runway, zero shrinking, zero clipping.
2. **Automatic Combat Frame Data (`combat.py`)**: Clean transparent production strips (`*_96x80.png`) + `*_meta.json` (`startup`/`active`/`recovery`/`link_pause`, `rhythmBeats`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox`, red pixel-fitted `hitboxes` excluding face highlights) + `*_framedata_audit_3x.png`.
3. **Dual-Leg Color-Coded Kinematic Gait Guides (`guide.py`)**: `walk` & `run` draw **YELLOW (Near/Right)** vs **CYAN (Far/Left)** articulated leg skeletons enforcing Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Swap (`F5`) with strict zero-VFX isolation.
4. **Power-Feel A/B Showcase Renderer (`showcase.py`)**: Supports `--power-test` generating 3-section verification MP4s (`1/3 Flat 85ms Control` vs `2/3 Tri-Phase Power Rhythm + Hitstop Shake` vs `3/3 0.5x Slow-Mo Skeleton Inspection`) + smart 2-row thumbnail grid for 24+ frame combos!

---

## Exact CLI Workflow (v2.6)

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect presets, chained part counts ([1P]/[2P]/[3P]), 6-dim & calm-splice validation
python -m pixelsprite list

# 2. Validate 6-dim choreography, Sub-Action Anticipation, Tri-Phase Power Rhythm & Calm Splice BEFORE calling API!
python -m pixelsprite validate skill_tri_phase_breaker
python -m pixelsprite validate ult_starfall_slash
python -m pixelsprite validate examples/custom_action_template.json

# 3. Generate single-sheet OR multi-part chained action (18f / 24f+) with strict enforcement
python -m pixelsprite action \
  --anchor output/hero/01_anchor_pixel_64px.png \
  --desc "<character description>" \
  --anim skill_tri_phase_breaker \
  --strict-choreography \
  --out output/hero

# 4. Render 3-section A/B Power-Feel Test MP4 (Even 85ms vs Tri-Phase Power vs 0.5x Slow-Mo)
python -m pixelsprite showcase-v2 \
  --metas output/hero/anim_skill_tri_phase_breaker_24f_meta.json \
  --power-test --loops 3 \
  --out output/hero/power_test.mp4

# 5. Full end-to-end pipeline -> 60 FPS Live Hitbox/Hurtbox Showcase MP4
python -m pixelsprite all \
  --desc "<character description>" \
  --style gba_chibi \
  --anims idle,walk,run,combo1_slash,skill_tri_phase_breaker,skill_phantom_flurry,ult_starfall_slash \
  --loops 3 \
  --out output/hero \
  --video output/hero/showcase_v2.mp4
```

---

## Mandatory Forensic & Visual QC Gate
1. **Validate First**: `python -m pixelsprite validate <anim>` MUST pass (`6-DIM OK`, zero Sub-Action Anticipation, Tri-Phase Power, or Calm Splice violations) BEFORE spending API calls.
2. **Enforce Quantitative Continuity**: Check `[SPLICE AUDIT]` (`iou >= 0.70`), `[AUDIT PASS]` (`seam_smooth == True`, `maxBodyDX <= 4.0px`, `maxBodyDY <= 12px`), and `MaxHurtW <= 38px`. NEVER ship an `AUDIT WARN`!
3. **Visual Frame-by-Frame & Motion Inspection**: Inspect `*_framedata_audit_3x.png` AND rendered MP4 / slow-mo playback to verify monotonic jump arcs, visible chamber/fast-swing/hitstop transitions, clean red Hitboxes, delete `_raw_cache/`, and run secret scan (`sk-` / local IPs) before committing.
