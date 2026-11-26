# AGENTS.md — PixelSprite v2.5 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with **6-Dimension Per-Frame Skeletal-Continuity Choreography**, **Mandatory Sub-Action Anticipation / Chamber Frames (`子招前摇铁律`)**, **Seamless Multi-Part Chained High-Frame-Count Sheets (`18f`, `24f+` at ZERO resolution loss!)**, **purposeful unified-theme wide-arena VFX (`96×80` · fixed `34px` chibi)**, **auto pixel-fitted Hitboxes / Hurtboxes / Attack Frames**, and **Closed-Loop `N+1` & Hitstop Timing**.

When a user drops this repository into your workspace, follow this exact v2.5 playbook.

---

## Rule #0 (SUPREME LAW): NEVER Let GPT Image 2.6 Improvise Actions, Skip Sub-Action Anticipation, or Invent Meaningless VFX!

> **GPT Image 2.6 is ONLY the pixel-art renderer — YOU (the AI Agent) are the Animator, Rigger & Combat Designer!**

### Three Forbidden Anti-Patterns
1. **NEVER send vague prompts** (*"generate an 8-frame walk"*, *"generate a cool sword combo"*) — image models have zero biomechanical reasoning and produce one-legged walks & random disco blobs.
2. **NEVER cram multi-hit combos into 8–11 frames with 1 frame per strike (`Cut1 → Cut2 → Cut3`)!** Jumping directly from a floor-chop to a completed horizontal thrust with ZERO waist-chamber pull-back frame looks robotic and teleporty!
3. **NEVER mix unrelated rainbow VFX themes** (e.g., cyan + pink + random fireball + purple disco wheel inside one skill) or float meaningless glow blobs detached from the weapon/feet!

### Three Mandatory Engineering Laws (Enforced Automatically by `python -m pixelsprite validate`)
1. **6-Dimension Per-Frame Skeletal Choreography (`frame_choreography[]`)** — EVERY single cell (`F1..F[N]` + `Ghost F[N+1]=F1`) MUST explicitly define:
   - **`transition_from_prev`（与上一帧的骨骼衔接链）**: Exact continuous joint/limb path from `F[i-1]` to `F[i]` (e.g., *"From F7 floor-chop, right elbow retracts straight back pulling blade horizontally to right ribs to chamber F9 thrust!"*).
   - **`torso`**: Spine lean, hip height/airborne lift, shoulder twist/uncoil, head gaze.
   - **`arms_weapon`**: Exact position & angle of **BOTH** weapon hand and balance off-hand + opposite arm-leg swing on walk/run.
   - **`legs_feet`**: Explicit separate positions for **Near/Foreground Right leg** and **Far/Background Left leg**!
   - **`secondary_motion`**: Ponytail, scarf & hem physical drag opposite to acceleration.
   - **`vfx_meaning`**: Strictly `"NONE"` on locomotion; on combat skills, ONE unified elemental theme with explicit **Physical Origin + Directional Trajectory + Combat Meaning (Startup telegraph / Active Hitbox readability / Recovery dissipation)**.
2. **Sub-Action Anticipation Law (`子招前摇铁律`)**:
   - **EVERY distinct strike / sub-action inside a combo MUST have its own preparation / chamber frame (`前摇/蓄力过渡帧`)** before its active strike frame!
   - `validate_choreography()` **automatically rejects** any spec where `HIT #(k+1)` immediately follows `HIT #k` without an explicit chamber/prep frame (unless explicitly marked `"same_continuous_motion": true` for an uninterrupted single-swing shockwave!).
3. **Expand Frame Count Freely via Seamless Multi-Part Chained Sheets (`chained_parts` — ZERO Resolution Cramping!)**:
   - **DO NOT artificially restrict complex combos to 8 or 11 frames!** Give every high-difficulty multi-hit skill **16–24+ active frames** so every single strike has `[Chamber/Prep] → [Active Strike] → [Transition]`.
   - When `active_frames > 14`, NEVER squeeze 20 tiny cells into one sheet! Use `chained_parts` (e.g., `Part 1: 4×3 = F1..F11` @ `384×341`/cell + `Part 2: 3×3 = F11_bridge + F12..F18 + Ghost F1` @ `512×341`/cell):
     - `cli.py` automatically stamps **Part 1's actual quantized `F11`** onto Cell 1 of Part 2's guide, stamps **Master Anchor `F1`** onto Cell 9 of Part 2's guide, locks Part 2's pixel scale to Cell 9 (`F1`), audits **BOTH** the mid-action splice seam (`Part1_F11 ↔ Part2_Cell1`) AND the closed-loop wrap (`F18 ↔ Ghost_F19`), strips both duplicates, and exports ONE seamless 18-frame strip!

---

## Core Pipeline Architecture (v2.5)

1. **Wide Combat Arena (`96×80`, Pivot `[30, 71]`, Fixed `34px` Chunky Chibi)**: Identical chunky 34px character across all actions, `66px` forward + `40px` upward VFX arena, zero character shrinking, zero clipping.
2. **Automatic Combat Frame Data (`combat.py`)**: Clean transparent production strips (`*_96x80.png`) + `*_meta.json` (`startup`/`active`/`recovery`, `hitId`, `damage`, `hitstopMs`, `knockback`, green `hurtbox`, red pixel-fitted `hitboxes` excluding face highlights!) + `*_framedata_audit_3x.png`.
3. **Dual-Leg Color-Coded Kinematic Gait Guides (`guide.py`)**: `walk` & `run` draw explicit **YELLOW (Near/Right)** vs **CYAN (Far/Left)** articulated leg skeletons enforcing Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Left/Right Swap (`F5`) with strict zero-VFX isolation (`preserve_vfx=False`).
4. **Body-Isolated Quantizer & Smart Grounded-Row Baseline (`quantizer.py`)**: Zero horizontal teleporting, zero dark outline crust on VFX, flat-row ground snapping + true airborne jump arcs.
5. **Selective Variable Timing (`frameDurationsMs`)**: Strictly uniform `walk`/`run`; anticipation/chamber holds, snappy strike smears, and heavy climax HITSTOP on combat skills.

---

## Exact CLI Workflow (v2.5)

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect styles, frame counts (including [2P] chained 18f combos) & 6-dim status
python -m pixelsprite list

# 2. Validate 6-dimension skeletal choreography & Sub-Action Anticipation Law BEFORE calling API!
python -m pixelsprite validate skill_phantom_flurry
python -m pixelsprite validate examples/custom_action_template.json

# 3. Generate single-sheet OR multi-part chained action with strict enforcement
python -m pixelsprite action \
  --anchor output/hero/01_anchor_pixel_64px.png \
  --desc "<character description>" \
  --anim skill_phantom_flurry \
  --strict-choreography \
  --out output/hero

# 4. Full end-to-end pipeline -> 60 FPS Live Hitbox/Hurtbox Showcase MP4
python -m pixelsprite all \
  --desc "<character description>" \
  --style gba_chibi \
  --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash \
  --loops 3 \
  --out output/hero \
  --video output/hero/showcase_v2.mp4
```

---

## Mandatory Forensic & Visual QC Gate
1. **Choreography & Sub-Anticipation First**: `python -m pixelsprite validate <anim>` MUST pass (`6-DIM OK`, zero Sub-Action Anticipation violations) BEFORE spending API calls.
2. **Audit Seams & Stability**: Check `[SPLICE AUDIT]` on multi-part chained skills, `[AUDIT]` (`F[N]→F1`, `maxBodyDX`, `bodyH`), and intact weapons.
3. **Visual Frame-by-Frame Inspection**: Verify EVERY sub-attack has a visible chamber/prep pose (e.g. sword pulled back to waist BEFORE thrust!), verify `walk`/`run` true Left↔Right leg alternation, verify red Hitboxes hug active VFX cleanly without face false-positives, delete `_raw_cache/`, and run secret scan before committing.
