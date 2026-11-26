# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## Supreme Rule #0 — 6-Dimension Skeletal Choreography + Sub-Action Anticipation Law!
- **NEVER** pass vague prompts to GPT Image 2.6 or cram multi-hit combos into 8–11 frames with 1 frame per strike!
- **EVERY** frame MUST specify all 6 dimensions: **`transition_from_prev` (bone-to-bone continuity)**, **`torso`**, **`arms_weapon`**, **`legs_feet` (Near-Right & Far-Left separately)**, **`secondary_motion`**, and **unified-theme physically meaningful `vfx_meaning`**.
- **EVERY** distinct strike/sub-action inside a combo MUST have its own **preparation/chamber frame** (`前摇/蓄力过渡帧`) — NEVER jump from a floor-chop straight into a completed horizontal thrust! Use **`chained_parts`** (`4×3 Part 1 + 3×3 Part 2` = `18+1f` or more!) so complex combos get generous frame counts with ZERO cell cramping!
- Always run `python -m pixelsprite validate <spec>` (or `--strict-choreography`) before calling GPT Image 2.6.

## v2.5 Core Workflow Quick Reference
- **Inspect presets, `[2P]` chained combos & 6-dim status**: `python -m pixelsprite list`
- **Validate 6-dim choreography & Sub-Action Anticipation Law**: `python -m pixelsprite validate examples/custom_action_template.json`
- **Generate single or chained 18+ frame action**: `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim <id_or_json> --strict-choreography --out output/hero`
- **Full end-to-end pipeline -> 60 FPS Live Hitbox/Hurtbox Showcase MP4**: `python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4`
