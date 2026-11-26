# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite assets.

## Quick Reference
- **Core CLI**: `python -m pixelsprite all --desc "<character>" --modules core_8x8,skills_8x8 --out output/hero --video output/hero/showcase.mp4`
- **Re-quantize offline (0 API cost)**: `python -m pixelsprite generate --requantize-only --anchor <anchor.png> --desc "<character>" --module skills_8x8 --cell 48 --out output/hero`
- **List all built-in styles & 8×8 modules**: `python -m pixelsprite list`
- **Key rules**: Always use chunky low-res chibi pixel grids (`32px`/`48px`/`64px`), lock colors to the quantized anchor palette (while keeping glowing VFX accents), visually inspect `*_checker_4x.png`, and never commit API keys or `.env` / `env.txt`.
