# AGENTS.md — PixelSprite v2.3 AI Agent Workflow Playbook

This repository is an **AI-native workflow & deterministic CLI pipeline** for generating **16-bit chunky low-resolution pixel-art game animations** with **5-Dimension Per-Frame Structured Choreography (NEVER outsourcing action design to GPT Image 2.6!)**, **purposeful physics-driven VFX**, **wide-arena `96×80` combat frames (`34px` fixed chibi height)**, **automatic pixel-fitted Hitboxes / Hurtboxes / Attack Frames**, **spacious `N+1` closed-loop grids**, and **selective hitstop timing** using **GPT Image 2.6**.

When a user drops this repository into your workspace, follow this exact v2.3 playbook.

---

## Rule #0 (SUPREME LAW): NEVER Let GPT Image 2.6 Improvise Actions or Meaningless VFX!

> **GPT Image 2.6 is ONLY the pixel-art renderer — YOU (the AI Agent) are the Animator & Combat Designer!**

### What is STRICTLY FORBIDDEN (Anti-Pattern)
- **NEVER** send vague prompts like *"generate an 8-frame walk cycle"*, *"generate a sword slash animation"*, *"make a flashy attack with rainbow sparkles"*, or let GPT Image 2.6 invent limb poses and VFX on its own!
- **Why it fails (Battle-Tested Lessons)**:
  1. **Vague locomotion prompts** make image models forget which leg is left vs right, producing an unnatural one-legged "front-foot hopping in place" march instead of true alternating footwork!
  2. **Vague attack prompts** produce stiff arms glued to weapons and **meaningless random glow blobs/explosions** detached from where the weapon actually swung or where the feet actually pushed off!

### What is MANDATORY Before Calling GPT Image 2.6 (5-Dimension Choreography Rule)
Before generating ANY new or modified animation, you **MUST** design a complete, explicit **per-frame 5-Dimension Choreography Spec (`frame_choreography[]`)** covering EVERY cell (`F1..F[N]` + `Ghost F[N+1]=F1`) — see [`examples/custom_action_template.json`](./examples/custom_action_template.json) and run `python -m pixelsprite validate <spec>` (or `--strict-choreography`):

1. **`torso`（躯干、重心与头部视线）**: Exact spine lean angle, hip drop/rise (`-2px` crouch / `+1.5px` peak / `+22px` airborne), shoulder wind-up twist vs follow-through uncoil, head gaze direction.
2. **`arms_weapon`（双手动作、手腕与武器轨迹）**: Exact position & sweep plane of **BOTH** dominant weapon hand and off-hand balance arm (e.g., *pulled low behind knee -> whips bottom-left to top-right -> extended overhead -> lowers to 35° guard*; opposite arm-leg counter-swing on walk/run!).
3. **`legs_feet`（左右腿与双脚独立轨迹 — 严禁笼统！）**: Explicitly specify **BOTH** **Near/Foreground Right leg (近侧右腿)** and **Far/Background Left leg (远侧左腿)** separately in every frame (which foot is planted, sliding back under hip, pushing off toe, bending knee through vertical center crossover, lunging forward to brake, or tucked airborne!).
4. **`secondary_motion`（随动部件：马尾、围巾、衣摆）**: Physical drag & follow-through opposite to movement/acceleration (whipping back on dash, trailing down on upward leap, floating up on descent, settling smoothly on recovery).
5. **`vfx_meaning`（有物理来源与战斗语义的特效 — 绝不堆砌无意义光污染！）**:
   - **Locomotion (`idle`/`walk`/`run`)**: Strictly `"NONE — pure clean character sprite, zero VFX, zero dust, zero floor shadows"`.
   - **Combat & Skills**: Every VFX pixel MUST explicitly answer **3 questions**:
     1. **Physical Origin (物理来源)**: Where does it spawn? (e.g., *blade tip*, *sweeping sword edge*, *bracing/landing boots*, *trailing torso afterimage*).
     2. **Directional Trajectory (物理轨迹)**: Which direction does it move? (e.g., *follows exact bottom-left to top-right upward cut*, *ground dust kicks BACKWARD opposite to lunge/landing*).
     3. **Combat Meaning (战斗语义)**:
        - **Startup 前摇 (Telegraph 预警)**: Blade gleam / ground rune charge circle warns players of incoming attack.
        - **Active 判定帧 (Hitbox Readability 判定区可视化)**: Sweeping blade wave / dimensional rift / nova shockwave directly outlines the exact lethal Hitbox zone!
        - **Recovery 后摇 (Force Dissipation 卸力收势)**: Breaking wind ribbons / cooling embers / braking skid-dust clearly signals the active damage window is OVER!

---

## Core Architecture Rules (v2.3)

### 1. Chunky Low-Res Character (`34px`) Inside Wide Combat Arena (`96×80`, Pivot `[30, 71]`)
- Keep the character chunky low-res (`34px` logical height, 2-head chibi, 14–18 flat colors, 1px dark outline `#261a2b`, zero anti-aliasing).
- Anchor her in the left third (`pivot = [30, 71]`) inside a unified **`96×80`** transparent canvas, giving **`66px` forward + `40px` upward** open arena for huge, purposeful multi-layered VFX with ZERO character shrinking and ZERO clipping.

### 2. Automatic Combat Frame Data: Attack Frames + Pixel-Fitted Hitboxes & Hurtboxes (`combat.py`)
- Every action exports clean transparent production strips (`*_96x80.png`, zero burned-in debug boxes!) PLUS engine-ready `combatSummary` & per-frame `frameData[]` in `*_meta.json` AND `*_framedata_audit_3x.png`:
  - **Attack State Machine**: `neutral` | `startup` (前摇) | `active` (**攻击判定帧**: `isAttackFrame`, `hitId`, `damage`, `hitstopMs`, `knockback`) | `recovery` (后摇).
  - **Green Hurtbox**: Auto-fitted to `body_mask` (trims scarf tips & sword blade), exporting cell coords `[x,y,w,h]` + pivot-relative `rel`.
  - **Red Active Hitbox(es)**: Generated ONLY on `active` frames, pixel-fitted directly to the actual generated sword & glowing VFX pixels!

### 3. Spacious Closed-Loop `N + 1` Grids + Dual-Leg Kinematic Gait Guides + Zero-Teleport Quantizer
- **Dual-Leg Color-Coded Kinematic Guides (`guide.py`)**: NEVER generate `walk`/`run` with a legless blob guide! `guide.py` draws explicit **YELLOW (Near/Right)** vs **CYAN (Far/Left)** articulated leg skeletons enforcing **Contact → Down → Vertical Passing Crossover (`F3`/`F7`) → Push-Off/Reach → Left/Right Swap (`F5`) → Ghost `F9=F1`** with strict zero-VFX isolation (`preserve_vfx=False`).
- **Spacious Grids**: `8+1f` → `3×3` (`1024×1024` locomotion / `1536×1024` widescreen combat); `11+1f` → `4×3` (`1536×1024`); `14+1f` → `5×3` (`1536×1024`). Ghost Cell `N+1 == F1` is audited and stripped from final strips.
- **Body-Isolated Quantization (`quantizer.py`)**: Locks `body_cx`, `body_h`, and grounded baselines strictly from `body_mask` (zero horizontal teleporting, zero shrinking, true airborne parabolas, 24-color arcade VFX ramp with zero black outline crust on VFX).

### 4. Selective Variable Timing & Hitstop (`frameDurationsMs`)
- Keep `walk` (`95ms×8`) and `run` (`75ms×8`) strictly even.
- Apply anticipation holds (`180–195ms`), snappy strike smears (`50–60ms`), heavy climax HITSTOP (`225–275ms`), and stylish finish holds (`165–215ms`) strictly on combat keyframes.

---

## Exact CLI Workflow (v2.3)

```bash
pip install -r requirements.txt
export PIXELSPRITE_API_URL="https://api.openai.com/v1"
export PIXELSPRITE_API_KEY="sk-..."
export PIXELSPRITE_MODEL="gpt-image-2.6-sunburst"

# 1. Inspect built-in specs & 5-dimension choreography verification status
python -m pixelsprite list

# 2. Validate ANY built-in or custom action JSON BEFORE spending API calls!
python -m pixelsprite validate examples/custom_action_template.json

# 3. Generate a single action with --strict-choreography enforcement
python -m pixelsprite action \
  --anchor output/hero/01_anchor_pixel_64px.png \
  --desc "<character description>" \
  --anim examples/custom_action_template.json \
  --strict-choreography \
  --out output/hero

# 4. Full end-to-end pipeline -> 60 FPS Live Hitbox/Hurtbox Showcase MP4
python -m pixelsprite all \
  --desc "<character description>" \
  --style gba_chibi \
  --anims idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash \
  --loops 3 \
  --out output/hero \
  --video output/hero/showcase_v2.mp4
```

---

## Mandatory Forensic & Visual QC Gate
1. **Choreography First**: `python -m pixelsprite validate <anim>` MUST pass (`5-DIM OK`) BEFORE calling GPT Image 2.6.
2. **6/6 `[AUDIT PASS]`**: Check `maxBodyDX`, `bodyH`, intact weapons, and `F[N] → F1` continuity.
3. **Biomechanical & Meaning Visual Inspection**:
   - On `walk`/`run`: verify EVERY frame's near/far boots truly alternate Left↔Right with vertical passing crossover (`F3`/`F7`) and zero stray VFX.
   - On combat skills: inspect `*_framedata_audit_3x.png` — verify green Hurtboxes hug only the body, red Hitboxes hug the active VFX, and every VFX element physically matches the weapon/foot motion!
4. **Clean Repo**: Delete `_raw_cache/` and scan for zero leaked API keys/IPs before committing.
