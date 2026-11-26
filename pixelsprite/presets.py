"""Style presets, Closed-Loop (N+1 Ghost Frame) Variable-Length Animation Specs, Selective Hitstop Timing & Prompt Compilers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PIXEL_STYLES: dict[str, dict[str, Any]] = {
    "gba_48": {
        "label": "16-bit GBA Chibi Low-Res (48x48 cell, recommended)",
        "cell_size": 48,
        "palette_colors": 18,
        "fill_ratio": 0.72,
        "prompt": (
            "authentic crisp 16-bit GBA / SNES indie RPG chibi pixel art (Legend of Zelda Minish Cap / "
            "Eastward / Celeste style), chunky low-resolution pixel grid (character ~32-36 logical pixels tall), "
            "cute 2-head chibi proportions with large expressive head and compact limbs, crisp 1-pixel dark "
            "purplish-brown outline (#261a2b), clean flat 2-step cel shading using strictly 14-18 vibrant colors, "
            "ZERO anti-aliasing, ZERO blur, ZERO painterly gradients, ZERO pillow shading"
        ),
    },
    "retro_32": {
        "label": "Ultra-Chunky Retro 32x32 (Stardew / Pico-8 style)",
        "cell_size": 32,
        "palette_colors": 14,
        "fill_ratio": 0.78,
        "prompt": (
            "ultra-chunky 32x32 retro indie pixel art (Stardew Valley / Shovel Knight / Pico-8 style), "
            "bold tiny 2-head chibi sprite (~24 logical pixels tall), crisp 1-pixel dark outline, "
            "strictly 12-14 flat solid colors, unmistakable silhouette, zero fine noise, zero blur"
        ),
    },
    "arpg_64": {
        "label": "16-bit Indie ARPG 64x64 (extra room for giant skill VFX)",
        "cell_size": 64,
        "palette_colors": 20,
        "fill_ratio": 0.62,
        "prompt": (
            "crisp 16-bit indie ARPG chibi pixel art (CrossCode / Sea of Stars / Hyper Light Drifter style), "
            "chunky readable pixel clusters (~40 logical pixels tall inside a 64x64 cell leaving generous space "
            "for huge radiant sword skills and magic spells), 2-head chibi proportions, crisp 1-pixel dark outline, "
            "strictly 16-20 clean vibrant colors, zero blur, zero anti-aliasing"
        ),
    },
}

# ==============================================================================
# v2.0 VARIABLE-LENGTH CLOSED-LOOP ANIMATION SPECS (N Active + 1 Ghost Loop F[N+1]=F1)
# - Locomotion (walk/run): 8 active frames (generated as 9 cols), STRICTLY EVEN timing (no awkward stops!)
# - Idle: 8 active frames (9 cols), subtle organic breathing holds on inhale/exhale peaks
# - Medium skills: 11 active frames (4x3 = 11+1 ghost), anticipation hold + snappy strikes + hitstop climax!
# - Long cinematic ultimates: 14 active frames (5x3 = 14+1 ghost), multi-stage charge + hangtime + nova hitstop + victory sheath hold!
# ==============================================================================

ANIMATION_SPECS: dict[str, dict[str, Any]] = {
    "idle": {
        "id": "idle",
        "name": "待机 Idle",
        "key": "IDLE",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [9, 1],
        "timing_mode": "breath",
        "frame_durations_ms": [155, 105, 100, 110, 160, 105, 100, 105],
        "hold_tags": {1: "呼气舒展", 5: "吸气顶点"},
        "vfx_hint": None,
        "scroll_speed": 0,
        "row_prompt": (
            "IDLE breathing loop (Frames 1-8 + Frame 9 GHOST IDENTICAL TO FRAME 1): "
            "1: neutral ready stance (=Anchor), 2-4: gentle bouncy inhale lifting chest/ponytail/scarf slightly, "
            "5: soft breath apex, 6-7: relaxed exhale settling knees, 8: almost identical 1 micro-step before Frame 1, "
            "9 (GHOST LOOP): EXACT COPY of Frame 1 neutral ready stance!"
        ),
    },
    "walk": {
        "id": "walk",
        "name": "行走 Walk",
        "key": "WALK",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [9, 1],
        "timing_mode": "even",
        "frame_durations_ms": [95, 95, 95, 95, 95, 95, 95, 95],
        "hold_tags": {},
        "vfx_hint": None,
        "scroll_speed": 115,
        "row_prompt": (
            "WALK 2-step closed loop (Frames 1-8 + Frame 9 GHOST IDENTICAL TO FRAME 1): "
            "1: R-foot forward contact stride, 2: R-foot down cushion, 3: R-stance passing (L-leg tucked), 4: L-foot reaching up-forward, "
            "5: L-foot forward contact stride (mirror of 1), 6: L-foot down cushion, 7: L-stance passing (R-leg tucked), "
            "8: R-foot swinging forward just 1 tiny step before landing into Frame 1, "
            "9 (GHOST LOOP): EXACT COPY of Frame 1 R-foot forward contact stride!"
        ),
    },
    "run": {
        "id": "run",
        "name": "疾跑 Run",
        "key": "RUN",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [9, 1],
        "timing_mode": "even",
        "frame_durations_ms": [75, 75, 75, 75, 75, 75, 75, 75],
        "hold_tags": {},
        "vfx_hint": None,
        "scroll_speed": 225,
        "row_prompt": (
            "SPRINT RUN 2-step closed loop (Frames 1-8 + Frame 9 GHOST IDENTICAL TO FRAME 1): "
            "Forward-leaning energetic chibi sprint, streaming red scarf & ponytail behind, sword held ready low-back; "
            "1: R-leg extended forward strike, 2: push-off low, 3: mid-air flight, 4: L-leg reaching forward, "
            "5: L-leg forward strike, 6: push-off low, 7: mid-air flight, 8: R-leg snapping forward 1 micro-step before Frame 1, "
            "9 (GHOST LOOP): EXACT COPY of Frame 1!"
        ),
    },
    "combo1_slash": {
        "id": "combo1_slash",
        "name": "普攻一式·横斩",
        "key": "ATK 1",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [9, 1],
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 175, 55, 220, 85, 80, 85, 90],
        "hold_tags": {2: "蓄力停顿", 4: "斩击顿帧 HITSTOP"},
        "vfx_hint": "arc_right",
        "scroll_speed": 0,
        "row_prompt": (
            "QUICK HORIZONTAL SLASH closed loop (Frames 1-8 + Frame 9 GHOST IDENTICAL TO FRAME 1): "
            "1: neutral ready stance (=Anchor), 2: coiled pull-back anticipation crouch, "
            "3: explosive forward lunge mid-swing with cyan pixel motion blur, "
            "4: PEAK IMPACT full forward cleave with bright glowing cyan-white horizontal pixel crescent slash, "
            "5: slash energy fading in follow-through, 6: recoil recovery stepping back, "
            "7: raising sword back toward ready guard, 8: 95% settled 1 micro-step before Frame 1, "
            "9 (GHOST LOOP): EXACT COPY of Frame 1 neutral ready stance!"
        ),
    },
    "skill_phantom_flurry": {
        "id": "skill_phantom_flurry",
        "name": "R·幻影五连乱舞 (11帧)",
        "key": "SKILL R",
        "active_frames": 11,
        "closed_loop": True,
        "grid": [4, 3],  # 12 cells = 11 active + Cell 12 Ghost (=F1)!
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 185, 50, 55, 55, 55, 60, 250, 165, 85, 90],
        "hold_tags": {2: "蓄力起势", 8: "五连终结 HITSTOP", 9: "帅气急停"},
        "vfx_hint": "flurry",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1",
            "Cell 2 (F2 ANTICIPATION HOLD): Low coiled sprint-draw crouch, cyan & neon-pink sparks crackling on hilt",
            "Cell 3 (F3 BLINK DASH): Blazing forward dash lean with horizontal cyan-pink pixel speed lines",
            "Cell 4 (F4 SLASH 1): Fast upward diagonal neon-cyan pixel slash crescent cutting up-right",
            "Cell 5 (F5 SLASH 2): Fast downward diagonal hot-pink/magenta pixel slash crossing over the cyan trail",
            "Cell 6 (F6 SLASH 3): Spinning reverse golden-yellow pixel crescent sweep with fluttering red scarf",
            "Cell 7 (F7 SLASH 4): Dazzling twin X-cross neon-pink & electric-cyan slashes overlapping in front",
            "Cell 8 (F8 FINISHER HITSTOP CLIMAX): Massive explosive 5-hit glowing white-pink-cyan-gold star-cross burst tearing the air!",
            "Cell 9 (F9 STYLISH BRAKE HOLD): Cool crouched landing brake pose as bright pink & gold pixel sparks scatter",
            "Cell 10 (F10 RECOVERY): Rising smoothly from crouch, swinging sword back toward front guard",
            "Cell 11 (F11 PRE-LOOP BRIDGE): 95% back to neutral ready stance, nearly identical to Cell 1 & Cell 12 (only tiny scarf settle left!)",
            "Cell 12 (GHOST LOOP = F1): MUST BE IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
        ],
    },
    "ult_starfall_slash": {
        "id": "ult_starfall_slash",
        "name": "F·星陨次元斩 (14帧奥义)",
        "key": "ULT F",
        "active_frames": 14,
        "closed_loop": True,
        "grid": [5, 3],  # 15 cells = 14 active + Cell 15 Ghost (=F1)!
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 85, 195, 60, 140, 55, 55, 265, 155, 75, 85, 215, 90, 90],
        "hold_tags": {3: "星辉蓄力停顿", 5: "浮空滞空定格", 8: "次元星爆 HITSTOP", 12: "收剑胜利定格"},
        "vfx_hint": "ultimate",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1",
            "Cell 2 (F2 CROUCH): Dipping into low crouched anticipation pulling sword close to waist",
            "Cell 3 (F3 CHARGE HOLD): Deep power crouch as bright golden-cyan pixel starlight gathers onto the raised blade",
            "Cell 4 (F4 LAUNCH): Explosive upward leap off the ground with scarf trailing down and sparkling gold trail",
            "Cell 5 (F5 AERIAL HANGTIME HOLD): High airborne levitation holding glowing golden-white 4-point star halo above raised sword",
            "Cell 6 (F6 AIR SLASH 1): Sweeping first giant diagonal neon-cyan & magenta spatial rift slash downward-right",
            "Cell 7 (F7 AIR SLASH 2): Sweeping counter-diagonal blazing golden-white slash intersecting into a massive glowing X-star!",
            "Cell 8 (F8 DIMENSION NOVA HITSTOP CLIMAX): Maximum peak blazing white-gold-cyan-magenta 4-point dimensional star explosion filling right half of cell!",
            "Cell 9 (F9 SHATTER FLASH): Star explosion bursting outward into vivid cyan, pink, and golden pixel starlight shards",
            "Cell 10 (F10 DESCENT): Graceful mid-air descent twisting sword cleanly downward as starlight dust trails",
            "Cell 11 (F11 LANDING SQUASH): Crisp bouncy knee-bend landing on the floor while bright sparkles float gently around her",
            "Cell 12 (F12 VICTORY POSE HOLD): Heroic confident standing flourish holding gleaming sword proudly with twinkling stars",
            "Cell 13 (F13 RELAX): Lowering sword smoothly and relaxing scarf back toward ready posture",
            "Cell 14 (F14 PRE-LOOP BRIDGE): 95% back to neutral ready stance, 1 subtle step before Cell 1 & Cell 15!",
            "Cell 15 (GHOST LOOP = F1): MUST BE IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
        ],
    },
}

CLOSED_LOOP_PACKS: dict[str, dict[str, Any]] = {
    "core_9x4_closed": {
        "name": "Closed-Loop Core 9x4 (4 Actions x 8 Active + Col 9 Ghost=F1)",
        "name_zh": "闭环核心动作 9×4（每行8有效帧 + 第9帧闭环锚点）",
        "cols": 9,
        "rows_count": 4,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "anim_ids": ["idle", "walk", "run", "combo1_slash"],
    },
}

# Legacy v1 8x8 modules kept 100% compatible for quick 64-frame generation
SHEET_MODULES: dict[str, dict[str, Any]] = {
    "core_8x8": {
        "name": "Core Actions & 3-Hit Combo 8x8 (64 frames)",
        "name_zh": "核心动作与三连剑技 8×8（64帧）",
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "rows": [
            {"id": "idle", "name": "待机 Idle", "key": "IDLE", "fps": 8, "batch": 0, "vfx_hint": None,
             "frame_durations_ms": [155, 105, 100, 110, 160, 105, 100, 105],
             "prompt": "Row 1 (Frames 1-8): Lively breathing IDLE stance facing right — bouncy chibi chest breathing, fluttering scarf/hair tips, smooth loop"},
            {"id": "walk", "name": "行走 Walk", "key": "WALK", "fps": 10, "batch": 0, "vfx_hint": None,
             "frame_durations_ms": [95, 95, 95, 95, 95, 95, 95, 95],
             "prompt": "Row 2 (Frames 1-8): Bouncy energetic WALK cycle facing right — full alternating 2-step stride, lively arms and scarf"},
            {"id": "run", "name": "疾跑 Run", "key": "RUN", "fps": 12, "batch": 0, "vfx_hint": None,
             "frame_durations_ms": [75, 75, 75, 75, 75, 75, 75, 75],
             "prompt": "Row 3 (Frames 1-8): Fast dynamic SPRINT RUN cycle facing right — forward-leaning chibi torso, fast alternating boots, scarf streaming behind"},
            {"id": "combo1_slash", "name": "普攻一式·横斩", "key": "ATK 1", "fps": 13, "batch": 0, "vfx_hint": "arc_right",
             "frame_durations_ms": [95, 175, 55, 220, 85, 80, 85, 90],
             "prompt": "Row 4 (Frames 1-8): ATTACK COMBO 1 (Quick Horizontal Slash) facing right — coiled anticipation -> bright cyan-white horizontal pixel crescent slash -> recovery"},
            {"id": "combo2_uppercut", "name": "普攻二式·上挑斩", "key": "ATK 2", "fps": 13, "batch": 1, "vfx_hint": "arc_up",
             "frame_durations_ms": [95, 175, 55, 65, 225, 90, 85, 95],
             "prompt": "Row 1 (Frames 1-8): ATTACK COMBO 2 (Rising Uppercut Slash) facing right — crouched dip -> leaping gold-white rising pixel crescent -> landing"},
            {"id": "combo3_spin_cleave", "name": "普攻三式·跳劈旋斩", "key": "ATK 3", "fps": 13, "batch": 1, "vfx_hint": "slam",
             "frame_durations_ms": [95, 180, 60, 60, 235, 150, 90, 95],
             "prompt": "Row 2 (Frames 1-8): HEAVY FINISHER (360-deg Jump-Cleave Smash) facing right — crouch charge -> mid-air somersault -> downward slam with cyan-gold shockwave -> recovery"},
            {"id": "jump_dash", "name": "跳跃冲刺 Jump", "key": "JUMP", "fps": 11, "batch": 1, "vfx_hint": "jump",
             "frame_durations_ms": [125, 75, 80, 95, 95, 80, 75, 120],
             "prompt": "Row 3 (Frames 1-8): JUMP & AIR-DASH arc facing right — squash crouch -> launch -> mid-air horizontal dash -> falling -> landing squash"},
            {"id": "hurt_ko", "name": "受击倒地 Hurt/KO", "key": "HURT", "fps": 9, "batch": 1, "vfx_hint": "ko",
             "frame_durations_ms": [170, 95, 85, 85, 110, 120, 140, 420],
             "prompt": "Row 4 (Frames 1-8): HURT recoil into cute dramatic KO collapse facing right — knockback -> stumble -> tumble -> dizzy stars lying on floor"},
        ],
    },
    "skills_8x8": {
        "name": "Flashy ARPG Skills & Ultimates 8x8 (64 frames)",
        "name_zh": "炫酷技能与终极奥义 8×8（64帧）",
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "rows": [
            {"id": "skill_iaido_blink", "name": "Q·居合瞬闪斩", "key": "SKILL Q", "fps": 14, "batch": 0, "vfx_hint": "beam_right",
             "frame_durations_ms": [95, 195, 48, 48, 60, 240, 130, 100],
             "prompt": "Row 1 (Frames 1-8): SKILL Q IAIDO BLINK LIGHTNING SLASH facing right — crouched electric charge -> cyan afterimage dash -> blinding horizontal cyan beam cleave -> cool finish"},
            {"id": "skill_flame_wave", "name": "W·烈焰剑气波", "key": "SKILL W", "fps": 13, "batch": 0, "vfx_hint": "arc_right",
             "frame_durations_ms": [95, 185, 58, 225, 165, 95, 90, 95],
             "prompt": "Row 2 (Frames 1-8): SKILL W BLAZING FLAME CRESCENT WAVE facing right — overhead flaming blade -> giant roaring orange-gold-white fiery crescent wave -> ember trail"},
            {"id": "skill_ice_rain", "name": "E·冰晶剑雨阵", "key": "SKILL E", "fps": 12, "batch": 0, "vfx_hint": "sky_cast",
             "frame_durations_ms": [100, 175, 85, 80, 80, 220, 130, 100],
             "prompt": "Row 3 (Frames 1-8): SKILL E FROST SWORD RAIN SUMMON facing right — skyward sword + cyan magic circle -> crystal ice blades raining diagonally -> frost burst"},
            {"id": "skill_phantom_flurry", "name": "R·幻影五连乱舞", "key": "SKILL R", "fps": 15, "batch": 0, "vfx_hint": "flurry",
             "frame_durations_ms": [90, 160, 52, 52, 55, 240, 130, 95],
             "prompt": "Row 4 (Frames 1-8): SKILL R PHANTOM MULTI-SLASH CROSS FLURRY facing right — dash -> rapid criss-crossing neon pink, cyan, gold X-slashes -> explosive star burst"},
            {"id": "skill_thunder_drop", "name": "A·雷霆天降落雷", "key": "SKILL A", "fps": 13, "batch": 1, "vfx_hint": "slam",
             "frame_durations_ms": [95, 85, 135, 55, 65, 250, 140, 100],
             "prompt": "Row 1 (Frames 1-8): SKILL A THUNDER METEOR PLUNGE SLAM facing right — high electric leap -> diving meteor plunge -> towering yellow-cyan lightning pillars"},
            {"id": "skill_parry_counter", "name": "S·圣盾格挡反击", "key": "SKILL S", "fps": 13, "batch": 1, "vfx_hint": "arc_right",
             "frame_durations_ms": [90, 95, 210, 55, 225, 115, 90, 95],
             "prompt": "Row 2 (Frames 1-8): SKILL S GOLDEN AEGIS PARRY & COUNTER-THRUST facing right — glowing golden curved barrier block -> explosive golden piercing lance thrust -> guard"},
            {"id": "skill_aura_burst", "name": "D·剑意觉醒爆气", "key": "BUFF D", "fps": 12, "batch": 1, "vfx_hint": "aura",
             "frame_durations_ms": [110, 180, 75, 140, 220, 140, 110, 110],
             "prompt": "Row 3 (Frames 1-8): SKILL D LIMIT-BREAK AURA AWAKENING BURST facing right — crouch gather -> blazing concentric cyan-gold flame aura pillar eruption -> sparkle buff"},
            {"id": "ult_starfall_slash", "name": "F·终极奥义·星陨次元斩", "key": "ULT F", "fps": 14, "batch": 1, "vfx_hint": "ultimate",
             "frame_durations_ms": [95, 165, 125, 60, 260, 175, 120, 180],
             "prompt": "Row 4 (Frames 1-8): ULTIMATE F STARFALL DIMENSION NOVA SLASH facing right — levitating golden star halo -> giant cyan-magenta-gold 4-point star explosion -> victory sheath"},
        ],
    },
    "topdown_8dir_8x8": {
        "name": "Top-Down 8-Direction RPG Run 8x8 (64 frames)",
        "name_zh": "俯视角 8 方向奔跑 8×8（64帧）",
        "view_prompt": "classic 3/4 top-down 16-bit RPG view (Legend of Zelda Minish Cap / Stardew / Alundra camera angle), consistent slightly elevated overhead perspective",
        "rows": [
            {"id": "dir_s", "name": "朝下跑 S (↓)", "key": "S", "fps": 12, "batch": 0, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 1 (Frames 1-8): Running DOWN toward camera (South) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_sw", "name": "朝左下跑 SW (↙)", "key": "SW", "fps": 12, "batch": 0, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 2 (Frames 1-8): Running DOWN-LEFT (South-West) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_w", "name": "朝左跑 W (←)", "key": "W", "fps": 12, "batch": 0, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 3 (Frames 1-8): Running LEFT (West) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_nw", "name": "朝左上跑 NW (↖)", "key": "NW", "fps": 12, "batch": 0, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 4 (Frames 1-8): Running UP-LEFT (North-West) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_n", "name": "朝上跑 N (↑)", "key": "N", "fps": 12, "batch": 1, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 1 (Frames 1-8): Running UP away from camera (North) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_ne", "name": "朝右上跑 NE (↗)", "key": "NE", "fps": 12, "batch": 1, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 2 (Frames 1-8): Running UP-RIGHT (North-East) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_e", "name": "朝右跑 E (→)", "key": "E", "fps": 12, "batch": 1, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 3 (Frames 1-8): Running RIGHT (East) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_se", "name": "朝右下跑 SE (↘)", "key": "SE", "fps": 12, "batch": 1, "vfx_hint": None, "frame_durations_ms": [85] * 8,
             "prompt": "Row 4 (Frames 1-8): Running DOWN-RIGHT (South-East) — smooth 8-frame alternating chibi run cycle"},
        ],
    },
}


def load_module_spec(module_id_or_path: str) -> dict[str, Any]:
    if module_id_or_path in SHEET_MODULES:
        return SHEET_MODULES[module_id_or_path]
    p = Path(module_id_or_path)
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        for idx, row in enumerate(data["rows"]):
            row.setdefault("batch", 0 if idx < 4 else 1)
            row.setdefault("fps", 12)
            row.setdefault("key", f"ROW {idx + 1}")
            row.setdefault("vfx_hint", None)
        return data
    raise ValueError(f"Unknown module '{module_id_or_path}'. Built-ins: {', '.join(SHEET_MODULES.keys())}")


def load_animation_spec(anim_id_or_path: str) -> dict[str, Any]:
    if anim_id_or_path in ANIMATION_SPECS:
        return ANIMATION_SPECS[anim_id_or_path]
    p = Path(anim_id_or_path)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    raise ValueError(f"Unknown animation '{anim_id_or_path}'. Built-ins: {', '.join(ANIMATION_SPECS.keys())}")


def compile_anchor_prompt(char_desc: str, style_id: str = "gba_48", module_id: str = "core_8x8") -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    mod = load_module_spec(module_id)
    return "\n".join([
        "Single centered Master Character Pixel Sprite on a pure transparent background (NO grid, NO text, NO floor shadow, NO props).",
        f"Character design: {char_desc.strip()}.",
        f"Camera angle: {mod['view_prompt']}.",
        f"Pixel art specification: {style['prompt']}.",
        "Composition: Character centered with generous transparent padding (~65% of image height), crisp chunky oversized square pixels clearly visible, iconic 2-head chibi silhouette so every color, scarf, hairstyle, and weapon reads unmistakably at 32-48 logical pixels tall!",
    ])


def compile_batch_8x4_prompt(
    char_desc: str,
    style_id: str,
    module_spec: dict[str, Any],
    batch_index: int,
    palette_hex: list[str] | None = None,
) -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    batch_rows = [r for r in module_spec["rows"] if r["batch"] == batch_index]
    pal_rule = (
        f"STRICTLY LOCK character colors to Image 1 ({', '.join(palette_hex[:16])}), "
        "allowing pure bright pixel VFX colors (white, cyan, gold, fire-orange, neon-pink) ONLY for skill effects."
        if palette_hex
        else "STRICTLY LOCK all character colors identically to Reference Image 1."
    )
    return "\n".join([
        "EXACT 8 columns by 4 rows (32 frames total) 16-bit CHUNKY LOW-RES PIXEL ART GAME SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, hair, scarf, outfit, boots, weapon, and 1-pixel dark outline in EVERY frame.",
        "Reference Image 2 is the EXACT 8x4 layout & baseline guide — place 1 single sprite inside each cell with generous transparent space between cells. DO NOT draw any grid lines, boxes, numbers, or guide shapes.",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {module_spec['view_prompt']}.",
        "THE 4 ROWS (strictly 8 continuous left-to-right frames per row):",
        *[f"- {r['prompt']}" for r in batch_rows],
        "CRITICAL RULES:",
        "1. Keep exact uniform chibi height (~32-36 logical pixels tall) across all 32 frames.",
        f"2. {pal_rule}",
        f"3. Style lock: {style['prompt']}.",
    ])


def compile_closed_loop_9x4_prompt(
    char_desc: str,
    style_id: str,
    pack_spec: dict[str, Any],
    palette_hex: list[str] | None = None,
) -> str:
    """Compile a 9-column x 4-row Closed-Loop prompt where Column 9 == Column 1 (Ghost Loop Anchor)!"""
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    anims = [ANIMATION_SPECS[aid] for aid in pack_spec["anim_ids"]]
    pal_rule = (
        f"STRICTLY LOCK character colors to Image 1 ({', '.join(palette_hex[:16])}), allowing bright cyan/white/gold ONLY for slash VFX."
        if palette_hex
        else "STRICTLY LOCK all character colors identically to Reference Image 1."
    )
    return "\n".join([
        "EXACT 9 columns by 4 rows (36 frames total) CLOSED-LOOP 16-bit CHUNKY LOW-RES PIXEL ART SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — preserve the EXACT chunky pixel density, 2-head chibi proportion, face, hair, red scarf, outfit, boots, sword, and 1-pixel dark outline in all 36 cells.",
        "Reference Image 2 shows the EXACT 9 columns x 4 rows grid, ground baselines, AND semi-transparent START/LOOP anchor poses stamped in Column 1 AND Column 9 of each row — DO NOT draw any grid borders, numbers, arrows, or guide boxes in your final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {pack_spec['view_prompt']}.",
        "CRITICAL CLOSED-LOOP RULE (MOST IMPORTANT!!):",
        "- In EVERY row, Column 9 (the 9th frame) is a CLOSED-LOOP GHOST ANCHOR that MUST BE 100% IDENTICAL IN POSE AND POSITION TO COLUMN 1!",
        "- Therefore, Column 8 (the 8th frame, immediately before Column 9) MUST be a smooth, subtle 1-step transition that blends seamlessly into Column 9 (= Column 1) with ZERO jarring jump or pose mismatch!",
        "THE 4 ROWS (strictly 9 frames left-to-right per row, Col 9 == Col 1):",
        *[f"- Row {i + 1}: {a['row_prompt']}" for i, a in enumerate(anims)],
        "STRICT QUALITY RULES:",
        "1. Maintain 100% identical character height (~32-36 logical pixels tall) across all 36 cells, leaving clean empty transparent padding so adjacent columns NEVER touch.",
        f"2. {pal_rule}",
        f"3. Style lock: {style['prompt']}.",
    ])


def compile_variable_action_prompt(
    char_desc: str,
    style_id: str,
    anim_spec: dict[str, Any],
    palette_hex: list[str] | None = None,
) -> str:
    """Compile a dedicated multi-row (e.g. 4x3 = 11+1f or 5x3 = 14+1f) Closed-Loop Variable-Length Skill prompt!"""
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    cols, rows = anim_spec["grid"]
    total = anim_spec["active_frames"] + (1 if anim_spec.get("closed_loop", True) else 0)
    active = anim_spec["active_frames"]
    pal_rule = (
        f"STRICTLY LOCK character colors to Image 1 ({', '.join(palette_hex[:16])}), "
        "while using dazzling pure 16-bit pixel VFX colors (pure white, electric cyan, blazing gold, flame orange, neon pink-magenta) for the skill effects!"
        if palette_hex
        else "STRICTLY LOCK all character colors identically to Reference Image 1 (use vivid pure pixel VFX colors for skill effects)."
    )
    return "\n".join([
        f"EXACT {cols} columns by {rows} rows ({total} frames total, reading strictly left-to-right, top-to-bottom from Cell 1 to Cell {total}) "
        "CLOSED-LOOP 16-bit CHUNKY LOW-RES PIXEL ART SINGLE-ACTION SKILL SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, orange ponytail, red scarf, teal tunic, brown boots, silver sword, and crisp 1-pixel dark outline in EVERY SINGLE CELL.",
        f"Reference Image 2 is the EXACT {cols}x{rows} grid & baseline guide showing the sequence order (1 -> {total}) AND semi-transparent START/LOOP anchor poses stamped in BOTH Cell 1 and Cell {total} — DO NOT draw any grid lines, boxes, numbers, or guide tints in the final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {anim_spec.get('view_prompt', 'classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell')}.",
        "CRITICAL CLOSED-LOOP RULE (MOST IMPORTANT!!):",
        f"- Cell 1 (START) and Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL neutral ready poses matching Reference Image 1!",
        f"- Cell {active} (immediately before Cell {total}) MUST smoothly ease almost all the way back into Cell {total} (= Cell 1), guaranteeing a seamless zero-jump loop when Cell {total} is later removed!",
        f"EXACT {total}-FRAME CHOREOGRAPHY (left-to-right, top-to-bottom):",
        *[f"- {b}" for b in anim_spec["frame_beats"]],
        "STRICT QUALITY RULES:",
        f"1. Keep exact uniform chibi character scale (~32-36 logical pixels tall) across all {total} cells; generous transparent space around every cell so no VFX bleeds across cell borders.",
        f"2. {pal_rule}",
        f"3. Style lock: {style['prompt']}.",
    ])
