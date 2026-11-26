# AGENTS.md — PixelSprite v2.0 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with **seamless closed-loop continuity (`N + 1` Ghost Frame)**, **variable action lengths (`8` / `11` / `14` / `16+` frames)**, and **selective per-frame millisecond timing & hitstop (`frameDurationsMs`)** using **GPT Image 2.6** (`gpt-image-2.6-sunburst` / `gpt-image-2.6-flare`).

When a user drops this repository into your workspace, follow this exact v2.0 playbook.

---

## Core Design Principles (v2.0)

### 1. Low-Res Chunky Pixel Art (`32px` / `48px` / `64px`) — NO Stiff Paper-Doll Rigs
- Use **2-head chibi low-resolution pixel art** (~24–40 logical pixels tall, 14–20 locked flat colors, 1px dark colored outline `#26192c`, zero anti-aliasing).
- Always quantize the **Master Pixel Anchor** first (`python -m pixelsprite anchor`), then feed the crisp nearest-neighbor upscaled anchor (`01_anchor_preview_512px.png`) as Reference Image 1 to `/v1/images/edits`.

### 2. Closed-Loop `N + 1` Ghost Anchor Rule (Solves Start/End Loop Pop!)
- **NEVER generate just `N` frames for a looping animation** — image models treat Frame `N` as an abrupt "ending pose", causing an ugly jump back to Frame `1`.
- **ALWAYS generate `N + 1` frames** (e.g., **9 columns** for an 8-frame loop, **12 cells (`4×3`)** for an 11-frame skill, **15 cells (`5×3`)** for a 14-frame ultimate):
  1. The guide renderer (`guide.py`) stamps a translucent visual copy of the exact **Master Anchor (`F1`)** in **BOTH Cell `1` AND Ghost Cell `N + 1`**!
  2. Frame `N` sits right beside Ghost Cell `N + 1 (= F1)`, forcing the model to draw Frame `N` as a smooth 1-step bridge directly into Frame `1`.
  3. After quantization, `audit_closed_loop()` measures `F[N] ↔ F[N+1]` (Ghost), `F[N+1] ↔ F[1]`, and `F[N] ↔ F[1]` silhouette IoU, saves a visual `*_loop_audit_4x.png` highlighting `F[N]` (green) & `Ghost F[N+1]` (red), and **STRIPS Ghost Frame `N + 1`** from the final exported game strip (`frames[0:N]`)!
- For one-shot non-looping animations (like Death/KO), set `"closed_loop": false`.

### 3. Variable Action Lengths — Choose Frame Count by Action Complexity!
Do NOT force every action into 8 frames! Match frame count to choreography length:
- **Short locomotion & idle (`idle`, `walk`, `run`, quick `combo1_slash`)**: **`8` active frames** (`9` generated on `9×4` closed-loop pack -> drop Col 9).
- **Medium flashy skills (`skill_phantom_flurry`, `skill_iaido_blink`, `skill_flame_wave`)**: **`11–12` active frames** (`4×3` = `11+1` ghost or `12+1` ghost on `5×3`).
- **Long cinematic finishers & ultimates (`ult_starfall_slash`, multi-stage boss attacks)**: **`14–16` active frames** (`5×3` = `14+1` ghost or `6×3` = `16+1` ghost) so anticipation, launch, hangtime, multi-hit nova climax, landing, victory flourish, and recovery ALL breathe naturally!

### 4. Selective Per-Frame Timing & Hitstop (`frameDurationsMs`) — NOT Uniform FPS!
Uniform frame times make combat skills feel rushed and weightless. Always author **selective per-frame millisecond durations** (Aseprite-compatible `frameDurationsMs`):
- **Locomotion (`walk`, `run`)**: Keep **STRICTLY EVEN** (`[95]*8` / `[75]*8`) — **NEVER** put jerky holds inside a walk/run cycle!
- **Idle (`idle`)**: Gentle subtle holds (`150–160ms`) at inhale/exhale peaks, `100–110ms` in between.
- **Combat & Flashy Skills**:
  - **Anticipation / Charge Hold**: `175–195ms` (telegraph reads clearly!)
  - **Fast Dash / Swing Blur**: `50–60ms` (explosive speed!)
  - **Impact Climax Hitstop (顿帧)**: `220–265ms` (heavy, unforgettable punch!)
  - **Stylish Finish / Sheath Hold**: `165–215ms` (cool visual punctuation before smooth bridge `F[N] → F[1]`!)

---

## Exact CLI Workflow

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect built-in styles, variable-length animations, and closed-loop packs
python -m pixelsprite list

# 2. Generate (or pixelize) Master Pixel Anchor
python -m pixelsprite anchor --desc "<character>" --style gba_48 --out output/hero

# 3. Generate Closed-Loop 9x4 Core Pack (8 active + Col 9 Ghost=F1 per row, drops Col 9 automatically)
python -m pixelsprite pack9 \
  --anchor output/hero/01_anchor_pixel_48px.png \
  --desc "<character>" \
  --pack core_9x4_closed \
  --out output/hero/v2

# 4. Generate Long Variable-Length Skills (11+1f on 4x3, 14+1f on 5x3, or custom JSON!)
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_48px.png --desc "<character>" --anim skill_phantom_flurry --out output/hero/v2
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_48px.png --desc "<character>" --anim ult_starfall_slash --out output/hero/v2

# 5. Render 60 FPS Variable-Timing & Closed-Loop Seam Audit MP4 Showcase
python -m pixelsprite showcase-v2 \
  --metas output/hero/v2/core_9x4_closed_meta.json \
          output/hero/v2/anim_skill_phantom_flurry_11f_meta.json \
          output/hero/v2/anim_ult_starfall_slash_14f_meta.json \
  --out output/hero/v2/showcase_v2.mp4
```

### Mandatory Visual & Loop Seam Verification Checklist
1. Inspect `*_9col_audit_4x.png` / `*_loop_audit_4x.png` — specifically compare **Frame `N` (green)** against **Ghost Frame `N+1` (red = `F1`)** and **Frame `1` (blue)**.
2. Check printed `[AUDIT]` IoU metrics (`F[N]<->F[N+1]` and `F[N]->F1`). If a row's Ghost Frame drifted or Frame `N` jumped, adjust the choreography prompt or `--requantize-only` before finalizing.
3. Verify `frameDurationsMs` matches the visual keyframes (holds land on actual anticipation/impact/victory frames, NOT on transition blurs; walk/run stay even!).
4. Never commit `.env`, `env.txt`, `_raw_cache/`, or API keys.
