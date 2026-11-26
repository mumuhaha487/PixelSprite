---
name: pixelsprite
description: Generate consistent 16-bit chunky low-resolution 8x8 (64-frame) pixel-art game sprite sheets, flashy ARPG skill combos, and 8-direction top-down RPG sprites using GPT Image 2.6 + deterministic NumPy pixel-grid quantization.
---

# PixelSprite Agent Skill

Use this skill whenever the user asks to create 2D pixel-art game characters, multi-action sprite sheets, flashy combat skills/ultimates, or 8-direction top-down RPG sheets.

## Workflow Summary

1. **Choose logical pixel grid** (`--style`):
   - `gba_48` (default, 48×48 cells, ~34px tall chibi, 18 colors) — best balance of readability & error tolerance.
   - `retro_32` (32×32 cells, ~24px tall chibi, 14 colors) — Stardew / Pico-8 ultra-chunky look.
   - `arpg_64` (64×64 cells, ~40px tall chibi, 20 colors) — extra canvas margin for giant skill VFX.
2. **Choose or compose `8×8` (64-frame) modules** (`--modules`):
   - `core_8x8`: Idle, Walk, Run, 3-Hit Sword Combo, Jump/Dash, Hurt/KO.
   - `skills_8x8`: 8 flashy ARPG skills (`Q` Iaido Blink, `W` Flame Wave, `E` Ice Sword Rain, `R` Phantom 5-Hit Flurry, `A` Thunder Meteor Drop, `S` Golden Parry Counter, `D` Aura Awakening Burst, `F` Ultimate Starfall Slash).
   - `topdown_8dir_8x8`: 8-direction top-down RPG run (S, SW, W, NW, N, NE, E, SE × 8 frames).
   - Or author a custom 8-row JSON spec and pass its file path via `--module custom.json`.
3. **Run the deterministic CLI**:
   ```bash
   python -m pixelsprite all \
     --desc "<concise iconic chibi character description>" \
     --style gba_48 \
     --modules core_8x8,skills_8x8 \
     --export-rows \
     --out output/<hero_name> \
     --video output/<hero_name>/showcase.mp4
   ```
4. **Verify visually**:
   - Inspect `*_checker_4x.png` (and extract frames from `showcase.mp4` if rendered).
   - If cell size / fill ratio / outline needs tuning, re-run with `--requantize-only` (zero API cost).
5. **Deliver game-ready outputs**:
   - `*_48px.png` (1:1 transparent game-engine sprite atlas, e.g., `384×384` for `8×8` @ `48px`),
   - `*_meta.json` (row indices, FPS, frame dimensions, palette hex list),
   - `*_rows/*.png` (per-action horizontal 8-frame strips),
   - `*_checker_4x.png` & `showcase.mp4` (review previews).
