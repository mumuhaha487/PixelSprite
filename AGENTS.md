# AGENTS.md — PixelSprite v2.1 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with **spacious single-action closed-loop grids (`3×3` / `4×3` / `5×3`)**, **body-isolated zero-teleport quantization (`64×64` canvas, fixed `34px` character height)**, **variable action lengths (`8` / `11` / `14+` frames)**, and **selective per-frame millisecond timing & hitstop (`frameDurationsMs`)** using **GPT Image 2.6** (`gpt-image-2.6-sunburst` / `gpt-image-2.6-flare`).

When a user drops this repository into your workspace, follow this exact v2.1 playbook.

---

## Core Design Principles (v2.1 — Battle-Tested Acceptance Rules)

### 1. Low-Res Chunky Pixel Art (`34px` Tall Char inside `64×64` Canvas) — ZERO Shrinking, ZERO Clipping
- **Keep the character chunky low-res** (`34px` logical height, 2-head chibi proportion, 14–18 locked flat colors, 1px dark purplish-brown outline `#26192c`, zero anti-aliasing).
- **NEVER cram a `34px` character + giant skill slashes into a tight `48×48` box** — giant VFX either clip off the right edge or force the quantizer to shrink the character 15–25% on skill frames!
- Instead, default style `gba_chibi` puts the **exact same `34px` chunky chibi character** inside a generous **`64×64` transparent canvas** (anchored slightly left-of-center at `anchor_x_ratio ≈ 0.38–0.48`, feet at `y = 58`), leaving `34–40px` of open space for giant slashes, flame waves, and airborne starfall bursts with **ZERO body shrinking** and **ZERO clipping**.

### 2. Spacious Single-Action Closed-Loop Grids (`N + 1` Ghost Anchor) — NEVER Cramped `9×4`!
- **NEVER squeeze 9 narrow columns across one horizontal strip** (`1536px / 9 = 170px` wide causes progressive rightward squish and chops off held swords on frames 4–8!).
- Give **every action its own spacious grid** (`>= 307px` wide cells!) with **`N + 1` frames** where **Ghost Cell `N + 1` == Cell `1`**:
  - **Short locomotion / idle / basic attack (`8` active frames)**: **`3×3` grid (`1024×1024` = `341×341` px/cell!)** → Cell `9` is Ghost `= F1` (excluded from final strip!).
  - **Medium multi-hit flashy skills (`11` active frames)**: **`4×3` grid (`1536×1024` = `384×341` px/cell)** → Cell `12` is Ghost `= F1`.
  - **Long cinematic ultimates (`14` active frames)**: **`5×3` grid (`1536×1024` = `307×341` px/cell)** → Cell `15` is Ghost `= F1`.
- The guide renderer (`guide.py`) stamps a translucent Master Anchor (`F1`) in **BOTH Cell `1` AND Ghost Cell `N + 1`** (for standing-start actions), plus a vertical character center lock line and true parabolic airborne lift cues.

### 3. Body-Isolated Pixel Quantization (`quantizer.py`) — ZERO Teleporting, True Jump Arcs, Pure Glowing VFX
Standard bbox/foot-centroid quantization breaks badly on flashy combat skills. PixelSprite v2.1 isolates `body_mask` (largest connected non-VFX component matching Master Palette) from `vfx_mask` (white/cyan/gold/neon-pink/violet):
1. **Zero Horizontal Teleporting**: Aligns X strictly from `body_cx` (middle torso+head centroid of `body_mask`, ignoring huge right-hand slashes & left-hand speed lines!).
   - `idle` / `walk` / `run`: `lock_body_x = True` → **`0.0px` horizontal jitter**.
   - Combat skills: organic forward lunge clamped smoothly to `[-3, +6]px` relative to `F1`.
2. **Zero Character Shrinking**: Computes unified `fixed_scale` strictly from standing `body_h` (`char_height_px = 34`), completely immune to tall explosions or ground sparks.
3. **True Airborne Jump Arcs**: Measures airborne vertical lift strictly from `body_foot_y` (ignoring ground launch sparks & downward star rays that touch the cell bottom!).
4. **Pure Glowing VFX (Zero Dark Ink Crust)**: Restricts `patch_1px_outline()` strictly to non-VFX `main_body` pixels so bright cyan/gold/pink/crimson slashes stay luminous without ugly black outline blobs.

### 4. Selective Per-Frame Timing & Hitstop (`frameDurationsMs`)
- **Walk / Run (`timing_mode: "even"`)**: Strictly uniform timing (`[95]*8` / `[75]*8`) — **NEVER** put pauses in locomotion cycles!
- **Idle (`timing_mode: "breath"`)**: Soft breath holds (`165–170ms`) on F1/F5 peaks, `105–110ms` in between.
- **Combat & Skills (`timing_mode: "hitstop"`)**:
  - Anticipation / Charge Hold: `180–195ms`
  - Fast Dash / Strike Smear: `50–60ms`
  - Climax Impact HITSTOP (顿帧): `225–265ms`
  - Stylish Brake / Victory Flourish Hold: `165–215ms`

---

## Exact CLI Workflow (v2.1)

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect built-in styles and spacious closed-loop animations
python -m pixelsprite list

# 2. One-command full pipeline (Anchor -> 6 spacious closed-loop actions -> 60 FPS showcase MP4)
python -m pixelsprite all \
  --desc "<character description>" \
  --style gba_chibi \
  --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash \
  --loops 3 \
  --out output/hero \
  --video output/hero/showcase_v2.mp4

# 3. Re-generate or re-quantize ONLY one specific action if QC catches a flaw
python -m pixelsprite action \
  --anchor output/hero/01_anchor_pixel_64px.png \
  --desc "<character description>" \
  --anim skill_phantom_flurry \
  --out output/hero

# Re-quantize locally without spending API calls:
python -m pixelsprite action --anchor ... --desc "..." --anim skill_phantom_flurry --requantize-only --out output/hero

# 4. Re-render 60 FPS Variable-Timing + Closed-Loop Seam Audit MP4
python -m pixelsprite showcase-v2 \
  --metas output/hero/anim_idle_8f_meta.json \
          output/hero/anim_walk_8f_meta.json \
          output/hero/anim_run_8f_meta.json \
          output/hero/anim_combo1_slash_8f_meta.json \
          output/hero/anim_skill_phantom_flurry_11f_meta.json \
          output/hero/anim_ult_starfall_slash_14f_meta.json \
  --loops 3 \
  --out output/hero/showcase_v2.mp4
```

---

## Mandatory Forensic & Visual QC Gate (DO NOT SHIP WITHOUT PASSING ALL 5!)

Before delivering any generated sprite set to the user, ALWAYS verify:
1. **Body X Stability (`maxBodyDX`)**: `<= 1.5px` on `idle`/`walk`/`run`; `<= 6.0px` smooth forward lunge (ZERO sudden backward teleporting!) on combat skills.
2. **Consistent Body Height (`bodyH`)**: Standing frames stay tightly around `char_height_px` (`~32–36px`) across EVERY animation — zero shrinking on VFX frames!
3. **Intact Weapon & Anatomy**: Inspect every `*_loop_audit_3x.png` visually — sword/weapon MUST stay intact in every frame (never disappearing mid-cycle and popping back on F1!).
4. **Closed-Loop Continuity (`F[N] ↔ F[N+1] Ghost` & `F[N] → F1`)**: Verify RGB similarity AND visually compare green `F[N]`, red `Ghost F[N+1]`, and blue `F1`. If ANY single animation fails, re-run `python -m pixelsprite action --anim <id>` for just that action!
5. **Clean Video & Zero Secret Leaks**: Inspect extracted frames from the rendered 60 FPS MP4 (verify crisp pixel alignment, readable labels with zero `□` missing glyphs, true airborne jump arcs), delete `_raw_cache/`, and verify zero API keys/IPs exist in tracked files.
