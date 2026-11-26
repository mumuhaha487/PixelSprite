# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## v2.1 Core Workflow Quick Reference
- **Inspect styles & spacious closed-loop animations**: `python -m pixelsprite list`
- **Full end-to-end pipeline (`64×64` canvas, fixed `34px` chibi height, spacious `3×3`/`4×3`/`5×3` closed-loop grids, 60 FPS showcase MP4)**:
  `python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4`
- **Single-action generate or local re-quantize**:
  `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim <anim_id> --out output/hero [--requantize-only]`
- **60 FPS Variable-Timing + Seam Audit MP4**:
  `python -m pixelsprite showcase-v2 --metas <meta1.json> ... --loops 3 --out showcase_v2.mp4`
- **Mandatory QC Gate**: Always verify `maxBodyDX` (zero teleporting), `bodyH` consistency (zero shrinking), intact weapons across all cells in `*_loop_audit_3x.png`, `F[N] ↔ F[N+1](Ghost=F1)` RGB continuity, even walk/run timing, and zero leaked secrets or `_raw_cache/`.
