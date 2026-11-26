# CLAUDE.md

Read and follow [AGENTS.md](./AGENTS.md) and [.agents/skills/pixelsprite/SKILL.md](./.agents/skills/pixelsprite/SKILL.md) before generating or modifying any pixel-art sprite animations.

## Supreme Rule #0 — 6-Dim Skeletal Continuity + Tri-Phase Power Rhythm + Calm Splice Law!
- **NEVER** pass vague prompts to GPT Image 2.6, skip sub-action chamber/fast-motion frames, splice `chained_parts` on crouched/VFX cells, draw floor rings beneath boots on grounded frames, or ship `AUDIT WARN` (`seam_smooth: false` / `maxBodyDX > 4.0px` / `MaxHurtW > 38px`)!
- **EVERY** frame MUST specify all 6 dimensions: **`transition_from_prev`**, **`torso`**, **`arms_weapon`**, **`legs_feet` (Near-Right & Far-Left separately)**, **`secondary_motion`**, and **unified-theme physically meaningful `vfx_meaning`**.
- **Tri-Phase Power Rhythm (`timing_mode: "tri_phase_power"`)**: Break heavy multi-move combos cleanly into **`charge_hold` (`190–235ms`) → `motion` (`50–60ms`) → `hitstop` (`225–245ms`) → normal `recovery` (`75–85ms`) → `link_pause` (`130–145ms`)**.
- **Calm Grounded Splice Anchor Law**: For 2-part / 3-part chained long combos (`18f`, `24f+`), ALWAYS place `splice_from_prev_frame` on a **calm, grounded, full-height (`34px`), zero-VFX stance or `link_pause` frame**!
- **Monotonic Airborne Parabola Law**: Jump curves MUST rise smoothly to a single highest apex (`0 → +7 → +14 → +20 APEX → +12 → +4 → 0`, max `|dy| <= 10px`) with distinct ascent vs apex sword silhouettes.
- Always run `python -m pixelsprite validate <spec>` (or `--strict-choreography`) before calling GPT Image 2.6.

## v2.6 Core Workflow Quick Reference
- **Inspect presets, `[1P]/[2P]/[3P]` chained combos & validation**: `python -m pixelsprite list`
- **Validate all v2.6 laws**: `python -m pixelsprite validate skill_tri_phase_breaker` / `ult_starfall_slash` / `examples/custom_action_template.json`
- **Generate single or chained 18f/24f+ action**: `python -m pixelsprite action --anchor <anchor.png> --desc "<character>" --anim <id_or_json> --strict-choreography --out output/hero`
- **Render 3-section A/B Power-Feel Test MP4**: `python -m pixelsprite showcase-v2 --metas <meta.json> --power-test --loops 3 --out output/hero/power_test.mp4`
- **Full end-to-end pipeline -> 60 FPS Live Hitbox/Hurtbox Showcase MP4**: `python -m pixelsprite all --desc "<character>" --style gba_chibi --anims idle,walk,run,combo1_slash,skill_tri_phase_breaker,skill_phantom_flurry,ult_starfall_slash --loops 3 --out output/hero --video output/hero/showcase_v2.mp4`
