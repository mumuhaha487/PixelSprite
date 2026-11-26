# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## Supreme Rule #0 — Design First, NEVER Let GPT Image 2.6 Improvise!
- **NEVER** pass a vague prompt like `"generate a walk cycle"` or `"generate a sword attack with flashy effects"` to GPT Image 2.6!
- **ALWAYS** author a complete **5-Dimension Per-Frame Choreography Spec (`frame_choreography[]`)** first — specifying exact **`torso`**, **`arms_weapon`**, **`legs_feet` (Near-Right & Far-Left separately!)**, **`secondary_motion`**, and **physically meaningful `vfx_meaning` (Origin + Trajectory + Combat Purpose)** for every frame (see [`examples/custom_action_template.json`](./examples/custom_action_template.json)), and verify it with `python -m pixelsprite validate <spec>` before calling the API!

## v2.3 Core Workflow Quick Reference
- **Inspect presets & choreography status**: `python -m pixelsprite list`
- **Validate custom 5-dimension action JSON**: `python -m pixelsprite validate examples/custom_action_template.json`
- **Generate action strictly from 5-dim choreography**: `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim <id_or_json> --strict-choreography --out output/hero`
- **Full end-to-end pipeline (`96×80` wide arena, `34px` chibi, Hitboxes/Hurtboxes, 60 FPS Live HUD MP4)**:
  `python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4`
- **Mandatory QC Gate**: Verify `[CHOREOGRAPHY PASS]` before generation, `[AUDIT PASS]` after quantization, inspect `*_framedata_audit_3x.png` & `walk`/`run` alternating Left/Right leg biomechanics visually, confirm VFX matches weapon/body physics, and never commit secrets or `_raw_cache/`.
