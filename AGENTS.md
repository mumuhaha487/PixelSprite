# AGENTS.md — PixelSprite AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution `8×8` (64-frame) pixel-art game sprite sheets and flashy combat skills** using **GPT Image 2.6** (`gpt-image-2.6-sunburst` / `gpt-image-2.6-flare`).

When a user drops this repository into your workspace and asks you to create pixel-art game characters, action sheets, flashy skill combos, or 8-direction top-down RPG sprites, follow this exact playbook.

---

## Core Design Philosophy (Why This Workflow Succeeds)

1. **DO NOT use 2D paper-doll skeletal rigging** or high-resolution (128px–256px) painterly sprites for AI-generated action loops:
   - Paper-doll rigs look stiff/mechanical and bind weapons rigidly to arms.
   - High-resolution per-frame image generation amplifies tiny facial/garment redraw drift ("flicker/popping").
2. **USE Chunky Low-Res Chibi Pixel Art (`32×32`, `48×48`, or `64×64` logical pixels)**:
   - Target character height: **`24–40` logical pixels** (classic 2-head GBA/SNES chibi proportions like *Minish Cap* / *Celeste* / *Stardew Valley*).
   - **14–20 locked flat colors** + **crisp 1px dark colored outline (`#26192c`)** + **zero anti-aliasing**.
   - At this pixel grid density, hand-drawn AI frames feel **lively, expressive, bouncy, and dynamic** (hair bounce, scarf flutter, 360° flips, blazing skills) while the deterministic pixel quantizer absorbs microscopic imperfections cleanly.
3. **Generate `8×8` (64 frames) via TWO `8×4` (32-frame) calls at `1536×1024`**:
   - Never wrap a single 8-frame action across 2 rows of 4 (models tend to repeat row 1 in row 2).
   - Putting all 8 frames of an action on **one horizontal row** across a `1536×1024` `8×4` grid gives `192×256` raw pixels per frame (~4× oversampling for `48×48`!), preventing cell bleeding while keeping strong cross-frame attention.
4. **Always Quantize Master Anchor BEFORE Generating Sheets**:
   - Generate (or import) the character anchor, immediately run `quantize_anchor` to snap it onto exact `48×48` logical pixels with 18 locked colors, then upscale cleanly (`NEAREST` to `512×512`) and pass THAT pixelated image as Reference Image 1 to `/v1/images/edits`. The model immediately mirrors the exact pixel block size and palette!

---

## Environment Setup (Zero Secrets in Git)

```bash
pip install -r requirements.txt
```

Provide API credentials via environment variables (or a gitignored `.env` file — **never commit keys**):

```bash
export PIXELSPRITE_API_URL="https://api.openai.com/v1"   # or compatible gateway URL
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"
```

---

## Exact Step-by-Step Agent Workflow

### Step 1: Inspect Built-In Styles & 8×8 Modules
```bash
python -m pixelsprite list
```

Built-in `8×8` (64-frame) modules:
- `core_8x8`: Idle, Walk, Run, Combo 1 Horizontal Slash, Combo 2 Uppercut Slash, Combo 3 360° Spin Jump-Cleave, Jump/Air-Dash, Hurt/KO.
- `skills_8x8`: **8 Flashy ARPG Skills & Ultimates** — `Q` Iaido Blink Lightning Slash, `W` Blazing Flame Crescent Wave, `E` Frost Sword Rain Summon, `R` Phantom 5-Hit Cross Flurry, `A` Thunder Meteor Plunge, `S` Golden Aegis Parry & Counter, `D` Limit-Break Aura Burst, `F` Ultimate Starfall Dimension Slash.
- `topdown_8dir_8x8`: Top-Down 8-Direction RPG Run (S, SW, W, NW, N, NE, E, SE × 8 frames).

### Step 2: Run the Pipeline

**Option A — Full 128-Frame Hero (Core 8×8 + Flashy Skills 8×8 + MP4 Showcase) in 1 command:**
```bash
python -m pixelsprite all \
  --desc "元气橘发高马尾少女勇者，红围巾，青绿色镶金短风衣，深棕短靴，手持亮银短剑，二头身Q版" \
  --style gba_48 \
  --modules core_8x8,skills_8x8 \
  --export-rows \
  --out output/my_hero \
  --video output/my_hero/showcase.mp4
```

**Option B — Reuse an existing character anchor (or user-uploaded character image):**
```bash
# Convert any user-uploaded character illustration into a crisp 48x48 pixel anchor:
python -m pixelsprite anchor --input-image hero_art.png --style gba_48 --out output/my_hero

# Generate Core 8x8 and/or Skills 8x8 from that exact anchor:
python -m pixelsprite generate --anchor output/my_hero/01_anchor_pixel_48px.png --desc "..." --module core_8x8 --out output/my_hero
python -m pixelsprite generate --anchor output/my_hero/01_anchor_pixel_48px.png --desc "..." --module skills_8x8 --out output/my_hero
```

**Option C — Author a Custom 8-Action / Boss / Magic Module JSON (`custom_skills.json`):**
Pass `--module path/to/custom_skills.json` using this exact schema:
```json
{
  "name": "Custom Mage Skills 8x8",
  "name_zh": "法师技能全集 8×8",
  "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
  "rows": [
    {
      "id": "fireball",
      "name": "Q·爆裂火球",
      "key": "SKILL Q",
      "fps": 12,
      "vfx_hint": "arc_right",
      "prompt": "Row 1 (Frames 1-8): Casting a blazing pixel fireball forward..."
    }
  ]
}
```
(`vfx_hint` supports `null`, `"arc_right"`, `"arc_up"`, `"beam_right"`, `"slam"`, `"sky_cast"`, `"flurry"`, `"aura"`, `"ultimate"`, `"jump"`, `"ko"`.)

### Step 3: Mandatory Agent Visual Verification Checklist
After running `generate` or `all`, **ALWAYS visually inspect** `<prefix>_checker_4x.png` before delivering to the user:
1. Check every row has 8 distinct, continuous frames with zero cell clipping or overlapping neighbors.
2. Check character scale consistency across all 64 cells; if sprites are slightly cramped for huge skills, re-quantize offline with `--requantize-only --cell 64 --fill 0.62` (ZERO extra API calls!).
3. Check that bright glowing VFX (cyan/gold/fire/magenta) kept crisp glow without dark outline crust (handled automatically by `patch_1px_outline` + `snap_palette_perceptual`).
4. Never commit `env.txt`, `.env`, or raw API credentials.
