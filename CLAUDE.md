# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## v2.2 Core Workflow Quick Reference
- **Inspect styles & combat attack frames**: `python -m pixelsprite list`
- **Full end-to-end pipeline (`96×80` wide arena, `34px` fixed chibi height, mega multi-layered VFX, auto Hitboxes/Hurtboxes & Attack Frames, 60 FPS Live HUD MP4)**:
  `python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4`
- **Single-action generate or local re-quantize**:
  `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim <anim_id> --out output/hero [--requantize-only]`
- **Render 60 FPS Live Hitbox/Hurtbox + Hitstop Showcase MP4**:
  `python -m pixelsprite showcase-v2 --metas output/hero/anim_*_meta.json --loops 3 --out showcase_v2.mp4`
- **Mandatory QC Gate**: Verify `[AUDIT PASS]` (`maxBodyDX`, `bodyH`, `F[N] → F1`), visually inspect `*_framedata_audit_3x.png` (green Hurtbox tight on body, red Hitbox tight on active VFX, rich multi-layered effects), verify even walk/run timing, and never commit secrets or `_raw_cache/`.
