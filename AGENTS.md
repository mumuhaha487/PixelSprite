# AGENTS.md — PixelSprite v2.2 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with **wide-arena arcade VFX (`96×80` canvas · fixed `34px` chibi height)**, **automatic pixel-fitted Combat Frame Data (Startup / ACTIVE Attack Frames / Recovery, Green Hurtboxes & Red Multi-Hit Hitboxes)**, **spacious single-action closed-loop grids (`3×3` / `4×3` / `5×3`, `N + 1` Ghost Frame)**, and **selective hitstop timing (`frameDurationsMs`)** using **GPT Image 2.6** (`gpt-image-2.6-sunburst` / `gpt-image-2.6-flare`).

When a user drops this repository into your workspace, follow this exact v2.2 playbook.

---

## Core Design Principles (v2.2)

### 1. Chunky Low-Res Character (`34px`) Inside Wide Combat Arena (`96×80`, Unified Pivot `[30, 71]`)
- Keep the character chunky low-res (`34px` logical height, 2-head chibi, 14–18 locked flat colors, 1px dark outline `#261a2b`, zero anti-aliasing).
- Expand the transparent cell canvas to **`96×80`** with the character anchored in the **left third (`pivot = [30, 71]`)**, opening **`66px` in front of her + `40px` above** for **HUGE, multi-layered arcade pixel VFX** (multi-step cyan/azure/sapphire gale waves, translucent phantom afterimages, blazing solar fire cyclones, ground magic rune circles, dust shockwaves, and full-arena rainbow starfall explosions) — with **ZERO character shrinking** and **ZERO VFX clipping**.

### 2. Automatic Combat Frame Data: Attack Frames (`Startup` / `ACTIVE` / `Recovery`) + Pixel-Fitted Hitboxes & Hurtboxes (`combat.py`)
Every generated action exports engine-ready combat frame data in `*_meta.json` (`combatSummary` + per-frame `frameData[]`) AND a visual verification grid `*_framedata_audit_3x.png` (while keeping the exported game strip `*_96x80.png` 100% clean with zero burned-in debug boxes!):
- **Phase State Machine (`phase`)**: `neutral` (locomotion) | `startup` (前摇/蓄力) | `active` (**攻击判定帧**, `isAttackFrame: true`, carrying `hitId`, `damage`, `hitstopMs`, `knockback`) | `recovery` (后摇/收招).
- **Body Hurtbox (`hurtbox`, Green)**: Automatically computed strictly from non-VFX core body pixels (`body_mask`), trimming floating scarf tips & extended weapons so hits feel fair. Exports both cell `[x, y, w, h]` and pivot-relative `rel: [dx, dy, w, h]` for Unity/Godot/Phaser!
- **Active Attack Hitbox(es) (`hitboxes`, Red)**: Generated ONLY on `active` attack frames, automatically pixel-fitted directly to the generated sword + glowing VFX pixels (`vfx_mask`)! Ignores behind-back speed lines/afterimages on forward swings (`forward_vfx`) and wraps full explosive bursts on AoE finishers (`aoe_nova`).

### 3. Spacious Closed-Loop `N + 1` Grids + Dual-Leg Color-Coded Kinematic Gait Guides + Zero-Teleport Quantizer (`guide.py` / `quantizer.py`)
- **NEVER generate `walk` or `run` with a legless blob guide** — image models lose track of left vs right legs and produce an unnatural one-legged "front-foot hop-in-place" march!
- `guide.py` draws an explicit **Richard-Williams 8-frame dual-leg color-coded kinematic skeleton** (`YELLOW` = Near/Foreground Right leg with bright leather boot; `CYAN` = Far/Background Left leg with darker shaded boot) enforcing exact **Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Left/Right Swap (`F5`) → Ghost `F9=F1`** biomechanics + natural opposite arm-leg counter-swing (with STRICT zero-VFX prompt isolation on locomotion!).
- Give EVERY action its own spacious grid with translucent `F1` anchor stamped in **Cell `1`** AND **Ghost Cell `N + 1`** (auto-stripped after RGB continuity audit):
  - `8` active frames: `3×3` (`1024×1024` for locomotion; `1536×1024` = `512×341`/cell widescreen for `combo1_slash`!).
  - `11` active frames (`skill_phantom_flurry`): `4×3` (`1536×1024` = `384×341`/cell).
  - `14` active frames (`ult_starfall_slash`): `5×3` (`1536×1024` = `307×341`/cell).
- **24-Color Arcade VFX Ramp**: Preserves 4–5 step glowing ramps (White/Cyan/Azure/Sapphire, Starlight/Gold/Flame/Crimson, Pink/Magenta/Violet/Indigo, Warm Dust) while restricting 1px dark outline patching strictly to non-VFX character pixels.
- **Zero Teleporting & True Jump Arcs**: Aligns `body_cx` & `body_h` strictly from `body_mask` (ignoring slashes, afterimages, and large flame cores while never leaking into small hair highlights); smart grounded-row baseline locks grounded boots to `y=70–71` while preserving smooth airborne parabolas.

### 4. Selective Variable Timing & Hitstop (`frameDurationsMs`)
- Keep `walk` (`95ms×8`) and `run` (`75ms×8`) **strictly uniform** (no awkward pauses!).
- Give combat skills clear **anticipation holds** (`180–195ms`), **snappy 50–60ms strike smears**, **heavy climax HITSTOP** (`225–275ms`), and **stylish brake/victory holds** (`165–215ms`).

---

## Exact CLI Workflow (v2.2)

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect wide-arena styles, grids & combat attack frames
python -m pixelsprite list

# 2. One-command full pipeline (Anchor -> 6 wide-arena actions + Hitboxes/FrameData -> 60 FPS Live HUD MP4)
python -m pixelsprite all \
  --desc "<character description>" \
  --style gba_chibi \
  --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash \
  --loops 3 \
  --out output/hero \
  --video output/hero/showcase_v2.mp4

# 3. Single-action generate or local re-quantize
python -m pixelsprite action --anchor output/hero/01_anchor_pixel_64px.png --desc "<character>" --anim skill_phantom_flurry --out output/hero [--requantize-only]

# 4. Losslessly repack an existing verified strip onto unified 96x80 + compute Frame Data
python -m pixelsprite repack --anchor <anchor.png> --anim walk --strip <strip.png> --ghost <ghost.png> --out output/hero

# 5. Render 60 FPS Live Hitbox/Hurtbox + Variable-Timing + Closed-Loop Seam Audit MP4
python -m pixelsprite showcase-v2 --metas output/hero/anim_*_meta.json --loops 3 --out output/hero/showcase_v2.mp4
```

---

## Mandatory Forensic & Visual QC Gate
1. **6/6 `[AUDIT PASS]`**: Check `maxBodyDX` (`<= 1.5px` locomotion, `<= 3.5px` combat), `bodyH` stability, intact sword on every frame, and `F[N] → F1` RGB continuity.
2. **Inspect Every `*_framedata_audit_3x.png`**: Verify green Hurtboxes stay strictly on the character body (never ballooning over fire/slashes!) and red Active Hitboxes tightly hug the actual VFX on EVERY designated active attack frame.
3. **Inspect Extracted 60 FPS MP4 Frames**: Confirm crisp nearest-neighbor rendering, rich multi-layered VFX, readable HUD with zero missing `□` glyphs, delete `_raw_cache/`, and run secret scan before pushing.
