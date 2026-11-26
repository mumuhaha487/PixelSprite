# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## v2.0 Core Workflow Quick Reference
- **Inspect presets & frame counts**: `python -m pixelsprite list`
- **Master Anchor (48px chunky pixel)**: `python -m pixelsprite anchor --desc "<character>" --style gba_48 --out output/hero`
- **Closed-Loop 9×4 Core Pack (`8 + 1 Ghost=F1`, drops Col 9)**: `python -m pixelsprite pack9 --anchor <anchor.png> --desc "<character>" --pack core_9x4_closed --out output/hero/v2`
- **Long Variable-Frame Skills (`11+1f` on `4×3`, `14+1f` on `5×3`, or custom JSON)**: `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim ult_starfall_slash --out output/hero/v2`
- **60 FPS Variable-Timing + Seam Audit MP4**: `python -m pixelsprite showcase-v2 --metas <meta1.json> <meta2.json> --out showcase_v2.mp4`
- **Mandatory checks**: Always inspect `F[N] ↔ F[N+1](Ghost=F1)` seam continuity in `*_audit_4x.png`, verify `frameDurationsMs` holds land only on key combat beats (walk/run stay even!), and never commit API keys or `_raw_cache/`.
