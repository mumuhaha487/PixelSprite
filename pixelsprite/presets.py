"""Style presets & v2.1 Spacious Closed-Loop (N+1 Ghost Frame) Variable-Length Animation Specs with Selective Hitstop Timing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PIXEL_STYLES: dict[str, dict[str, Any]] = {
    "gba_chibi": {
        "label": "16-bit GBA Chibi (34px tall char inside 64x64 cell — zero VFX clip, zero body shrink!)",
        "cell_size": 64,
        "char_height_px": 34,
        "palette_colors": 18,
        "prompt": (
            "authentic crisp 16-bit GBA / SNES indie RPG chibi pixel art (Legend of Zelda Minish Cap / "
            "Eastward / Celeste style), chunky low-resolution pixel grid (character ~34 logical pixels tall), "
            "cute 2-head chibi proportions with large expressive head and compact limbs, crisp 1-pixel dark "
            "purplish-brown outline (#261a2b), clean flat 2-step cel shading using strictly 14-18 vibrant colors, "
            "ZERO anti-aliasing, ZERO blur, ZERO painterly gradients, ZERO pillow shading"
        ),
    },
    "gba_48": {
        "label": "Compact 48x48 GBA Chibi (32px tall char, compact locomotion)",
        "cell_size": 48,
        "char_height_px": 32,
        "palette_colors": 18,
        "prompt": (
            "authentic crisp 16-bit GBA / SNES indie RPG chibi pixel art (Legend of Zelda Minish Cap / "
            "Eastward / Celeste style), chunky low-resolution pixel grid (character ~32 logical pixels tall), "
            "cute 2-head chibi proportions with large expressive head and compact limbs, crisp 1-pixel dark "
            "purplish-brown outline (#261a2b), clean flat 2-step cel shading using strictly 14-18 vibrant colors, "
            "ZERO anti-aliasing, ZERO blur, ZERO painterly gradients"
        ),
    },
    "retro_32": {
        "label": "Ultra-Chunky Retro 32x32 (24px tall char, Stardew / Pico-8 style)",
        "cell_size": 32,
        "char_height_px": 24,
        "palette_colors": 14,
        "prompt": (
            "ultra-chunky 32x32 retro indie pixel art (Stardew Valley / Shovel Knight / Pico-8 style), "
            "bold tiny 2-head chibi sprite (~24 logical pixels tall), crisp 1-pixel dark outline, "
            "strictly 12-14 flat solid colors, unmistakable silhouette, zero fine noise, zero blur"
        ),
    },
}

# ==============================================================================
# v2.1 SPACIOUS CLOSED-LOOP VARIABLE-LENGTH ANIMATION SPECS
# Every action gets its OWN spacious grid (>= 256px wide square/near-square cells!)
# so weapons NEVER get clipped, character scale NEVER drifts, and Ghost Cell N+1 == Cell 1!
#   - 8 active frames  -> 3x3 grid (1024x1024 = 341x341/cell! Cell 9 = Ghost F1)
#   - 11 active frames -> 4x3 grid (1536x1024 = 384x341/cell! Cell 12 = Ghost F1)
#   - 14 active frames -> 5x3 grid (1536x1024 = 307x341/cell! Cell 15 = Ghost F1)
# ==============================================================================

ANIMATION_SPECS: dict[str, dict[str, Any]] = {
    "idle": {
        "id": "idle",
        "name": "待机 Idle (8帧)",
        "key": "IDLE",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1024x1024",
        "lock_body_x": True,
        "allow_airborne": False,
        "anchor_x_ratio": 0.48,
        "timing_mode": "breath",
        "frame_durations_ms": [165, 110, 105, 110, 170, 110, 105, 110],
        "hold_tags": {1: "呼气舒展", 5: "吸气顶点"},
        "vfx_hint": None,
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (full silver sword clearly held forward-up, red scarf flowing left, boots planted)",
            "Cell 2 (F2 INHALE 1): Subtle gentle inhale — chest lifts 1 pixel, scarf tail rises softly, full silver sword clearly visible at same full length",
            "Cell 3 (F3 INHALE 2): Rising softly — ponytail bobs gently up, knees slightly straighter, full silver sword clearly held forward",
            "Cell 4 (F4 PRE-APEX): Nearing soft breath peak, scarf billowing smoothly, eyes bright, full silver sword clearly visible",
            "Cell 5 (F5 BREATH APEX): Gentle inhale peak — chest proudly lifted 1-2 pixels (DO NOT grow taller than normal!), ponytail high-bouncy, full silver sword steady",
            "Cell 6 (F6 EXHALE 1): Relaxing softly back down, scarf waving gently, full silver sword steady at full length",
            "Cell 7 (F7 EXHALE 2): Knees softening slightly into comfortable combat bounce, ponytail settling, full silver sword clearly visible",
            "Cell 8 (F8 PRE-LOOP BRIDGE): 95% back to Cell 1 & Cell 9 — almost identical pose, full silver sword intact at exact same angle & length!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1 with full silver sword!",
        ],
    },
    "walk": {
        "id": "walk",
        "name": "行走 Walk (8帧)",
        "key": "WALK",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1024x1024",
        "lock_body_x": True,
        "allow_airborne": False,
        "anchor_x_ratio": 0.48,
        "timing_mode": "even",
        "frame_durations_ms": [95, 95, 95, 95, 95, 95, 95, 95],
        "hold_tags": {},
        "vfx_hint": None,
        "scroll_speed": 115,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 R-CONTACT): Energetic walk — Right boot forward heel-contact, Left boot back, full silver sword held clearly forward-right, red scarf fluttering",
            "Cell 2 (F2 R-DOWN): Weight cushions down 1 pixel onto flat Right boot, Left boot lifting behind, ponytail bouncing down, full silver sword intact",
            "Cell 3 (F3 R-PASSING): Standing tall over Right boot, Left knee bent passing forward, full silver sword gently swinging, scarf waving",
            "Cell 4 (F4 L-REACH): Pushing off Right toe, Left boot reaching forward-up, bouncing up 1 pixel, full silver sword clearly visible",
            "Cell 5 (F5 L-CONTACT): Mirror of Cell 1 — Left boot forward heel-contact, Right boot back, full silver sword steady and clearly visible at full length",
            "Cell 6 (F6 L-DOWN): Weight cushions down 1 pixel onto flat Left boot, Right boot lifting behind, scarf flowing smoothly",
            "Cell 7 (F7 L-PASSING): Standing tall over Left boot, Right knee bent passing forward, full silver sword clearly visible",
            "Cell 8 (F8 PRE-LOOP BRIDGE): Pushing off Left toe, Right boot swinging forward just 1 tiny step before landing into Cell 9 (= Cell 1)! Full silver sword intact!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — Right boot forward contact, Left boot back, full silver sword clearly held!",
        ],
    },
    "run": {
        "id": "run",
        "name": "疾跑 Run (8帧)",
        "key": "RUN",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1024x1024",
        "lock_body_x": True,
        "allow_airborne": True,
        "max_lift_px": 2.5,
        "anchor_x_ratio": 0.48,
        "timing_mode": "even",
        "frame_durations_ms": [75, 75, 75, 75, 75, 75, 75, 75],
        "hold_tags": {},
        "vfx_hint": None,
        "scroll_speed": 225,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 R-STRIKE): Fast forward-leaning sprint — Right boot striking forward, Left leg stretched back, red scarf & ponytail streaming horizontally left, full silver sword held ready at side",
            "Cell 2 (F2 R-PUSH): Low explosive push-off on Right boot, Left knee driving forward, scarf streaming straight behind, full silver sword intact",
            "Cell 3 (F3 FLIGHT 1): Brief airborne sprint stride (both boots off floor slightly!), legs wide apart, dynamic leaning torso, full silver sword visible",
            "Cell 4 (F4 L-REACH): Left boot reaching forward to land, Right boot kicked high behind, ponytail bouncing",
            "Cell 5 (F5 L-STRIKE): Mirror of Cell 1 — Left boot striking forward, Right leg stretched back, scarf streaming left, full silver sword clearly visible",
            "Cell 6 (F6 L-PUSH): Low explosive push-off on Left boot, Right knee driving forward",
            "Cell 7 (F7 FLIGHT 2): Brief airborne sprint stride (mirror of Cell 3), full silver sword intact",
            "Cell 8 (F8 PRE-LOOP BRIDGE): Right boot snapping forward just 1 tiny step before landing into Cell 9 (= Cell 1)! Full silver sword clearly visible!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — Right boot forward sprint strike, scarf streaming left, full silver sword visible!",
        ],
    },
    "combo1_slash": {
        "id": "combo1_slash",
        "name": "普攻一式·横斩 (8帧)",
        "key": "ATK 1",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1024x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.40,
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 180, 55, 225, 85, 80, 85, 90],
        "hold_tags": {2: "蓄力停顿", 4: "横斩顿帧 HITSTOP"},
        "vfx_hint": "arc_right",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (full silver sword clearly held)",
            "Cell 2 (F2 ANTICIPATION HOLD): Coiled pull-back crouch drawing sword back behind shoulder ready to cleave, determined eyes",
            "Cell 3 (F3 SNAP SWING): Blazing fast forward lunge mid-swing with bright cyan-white pixel motion blur starting across front",
            "Cell 4 (F4 HITSTOP CLIMAX): Full extended heroic forward cleave with a bold glowing cyan-white horizontal pixel crescent slash arc sweeping cleanly to the right of her full silver sword!",
            "Cell 5 (F5 FOLLOW-THROUGH): Sword completed low-front swing as bright cyan pixel slash sparks fade out cleanly",
            "Cell 6 (F6 RECOIL): Shifting weight back upright, raising full silver sword smoothly",
            "Cell 7 (F7 GUARD RETURN): Almost back to ready posture, scarf settling down smoothly",
            "Cell 8 (F8 PRE-LOOP BRIDGE): 95% identical to Cell 1 & Cell 9 (full silver sword clearly held at exact ready angle!)",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
        ],
    },
    "skill_phantom_flurry": {
        "id": "skill_phantom_flurry",
        "name": "R·幻影五连乱舞 (11帧)",
        "key": "SKILL R",
        "active_frames": 11,
        "closed_loop": True,
        "grid": [4, 3],  # 12 cells = 11 active + Cell 12 Ghost (=F1)!
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.38,
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 185, 50, 55, 55, 55, 60, 250, 165, 85, 90],
        "hold_tags": {2: "蓄力起势", 8: "五连终结 HITSTOP", 9: "帅气急停"},
        "vfx_hint": "flurry",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (character anchored slightly left-of-center leaving right side open for slashes)",
            "Cell 2 (F2 ANTICIPATION HOLD): Low coiled sprint-draw crouch, cyan & bright pink sparks crackling on hilt",
            "Cell 3 (F3 BLINK DASH): Blazing forward dash lean with crisp horizontal cyan & pink pixel speed lines behind her",
            "Cell 4 (F4 SLASH 1): Fast upward diagonal neon-cyan pixel slash crescent cutting up-right in front of her",
            "Cell 5 (F5 SLASH 2): Fast downward diagonal bright hot-pink/magenta pixel slash crossing cleanly in front of her",
            "Cell 6 (F6 SLASH 3): Spinning reverse bright golden-yellow pixel crescent sweep with fluttering red scarf",
            "Cell 7 (F7 SLASH 4): Dazzling twin X-cross bright hot-pink & electric-cyan slashes overlapping cleanly in front of her",
            "Cell 8 (F8 FINISHER HITSTOP CLIMAX): Massive explosive 5-hit glowing white-pink-cyan-gold star-cross burst tearing the air on the right!",
            "Cell 9 (F9 STYLISH BRAKE HOLD): Cool crouched landing brake pose as bright pink & gold pixel sparks scatter around her",
            "Cell 10 (F10 RECOVERY): Rising smoothly from crouch, raising full silver sword cleanly toward front guard",
            "Cell 11 (F11 PRE-LOOP BRIDGE): 95% back to neutral ready stance, nearly identical to Cell 1 & Cell 12!",
            "Cell 12 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
        ],
    },
    "ult_starfall_slash": {
        "id": "ult_starfall_slash",
        "name": "F·星陨次元斩 (14帧奥义)",
        "key": "ULT F",
        "active_frames": 14,
        "closed_loop": True,
        "grid": [5, 3],  # 15 cells = 14 active + Cell 15 Ghost (=F1)!
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 24.0,
        "anchor_x_ratio": 0.38,
        "timing_mode": "hitstop",
        "frame_durations_ms": [95, 85, 195, 60, 140, 55, 55, 265, 155, 75, 85, 215, 90, 90],
        "hold_tags": {3: "星辉蓄力停顿", 5: "浮空滞空定格", 8: "次元星爆 HITSTOP", 12: "收剑胜利定格"},
        "vfx_hint": "ultimate",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (boots standing cleanly on baseline)",
            "Cell 2 (F2 CROUCH): Dipping into low crouched anticipation pulling sword close to waist",
            "Cell 3 (F3 CHARGE HOLD): Deep power crouch as bright golden-cyan pixel starlight gathers onto the raised blade",
            "Cell 4 (F4 LAUNCH): Explosive upward leap HIGH OFF THE GROUND with scarf trailing down and golden launch sparks underneath",
            "Cell 5 (F5 AERIAL HANGTIME HOLD): High airborne levitation holding glowing golden-white 4-point star halo above raised sword",
            "Cell 6 (F6 AIR SLASH 1): Still airborne, sweeping first giant diagonal neon-pink & cyan spatial rift slash downward-right",
            "Cell 7 (F7 AIR SLASH 2): Still airborne, sweeping counter-diagonal blazing golden-white slash intersecting into a massive glowing X-star!",
            "Cell 8 (F8 DIMENSION NOVA HITSTOP CLIMAX): Still airborne, peak blazing white-gold-cyan-magenta 4-point dimensional star explosion filling right half of cell!",
            "Cell 9 (F9 SHATTER FLASH): Descending gently as star explosion bursts outward into vivid cyan, pink, and golden pixel starlight shards",
            "Cell 10 (F10 DESCENT): Graceful mid-air descent twisting sword cleanly downward toward floor",
            "Cell 11 (F11 LANDING SQUASH): Crisp bouncy knee-bend landing squarely back on the ground baseline while sparkles float gently",
            "Cell 12 (F12 VICTORY POSE HOLD): Heroic confident standing flourish holding gleaming silver sword proudly with twinkling golden stars",
            "Cell 13 (F13 RELAX): Lowering sword smoothly and relaxing scarf back toward ready posture",
            "Cell 14 (F14 PRE-LOOP BRIDGE): 95% back to neutral ready stance, 1 subtle step before Cell 1 & Cell 15!",
            "Cell 15 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
        ],
    },
}


def load_animation_spec(anim_id_or_path: str) -> dict[str, Any]:
    if anim_id_or_path in ANIMATION_SPECS:
        return ANIMATION_SPECS[anim_id_or_path]
    p = Path(anim_id_or_path)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    raise ValueError(f"Unknown animation '{anim_id_or_path}'. Built-ins: {', '.join(ANIMATION_SPECS.keys())}")


def compile_anchor_prompt(char_desc: str, style_id: str = "gba_chibi") -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_chibi"])
    return "\n".join([
        "Single centered Master Character Pixel Sprite on a pure transparent background (NO grid, NO text, NO floor shadow, NO props).",
        f"Character design: {char_desc.strip()}.",
        "Camera angle: classic 2D side-scrolling 3/4 action RPG view, facing RIGHT.",
        f"Pixel art specification: {style['prompt']}.",
        "Composition: Character centered with generous transparent padding (~60% of image height), crisp chunky oversized square pixels clearly visible, iconic 2-head chibi silhouette!",
    ])


def compile_variable_action_prompt(
    char_desc: str,
    style_id: str,
    anim_spec: dict[str, Any],
    palette_hex: list[str] | None = None,
) -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_chibi"])
    cols, rows = anim_spec["grid"]
    active = int(anim_spec["active_frames"])
    closed = bool(anim_spec.get("closed_loop", True))
    total = active + (1 if closed else 0)
    pal_rule = (
        f"STRICTLY LOCK character colors to Image 1 ({', '.join(palette_hex[:16])}), "
        "while using pure luminous 16-bit pixel VFX colors (white, electric cyan, blazing gold, flame orange, neon pink-magenta) for skill effects!"
        if palette_hex
        else "STRICTLY LOCK all character colors identically to Reference Image 1."
    )
    return "\n".join([
        f"EXACT {cols} columns by {rows} rows ({total} frames total, reading strictly left-to-right, top-to-bottom from Cell 1 to Cell {total}) "
        "CLOSED-LOOP 16-bit CHUNKY LOW-RES PIXEL ART SINGLE-ACTION SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, orange ponytail, red scarf, teal tunic, brown boots, FULL-LENGTH silver sword (NEVER shrink or omit the sword!), and crisp 1-pixel dark outline in EVERY SINGLE CELL.",
        f"Reference Image 2 is the EXACT {cols}x{rows} grid & baseline guide showing the sequence order (1 -> {total}) AND semi-transparent START/LOOP anchor poses stamped in BOTH Cell 1 and Cell {total} — DO NOT draw any grid lines, boxes, numbers, or guide tints in the final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {anim_spec.get('view_prompt', 'classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell')}.",
        "CRITICAL CLOSED-LOOP & CONSISTENCY RULES:",
        f"- Cell 1 (START) and Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL poses matching Reference Image 1!",
        f"- Cell {active} (immediately before Cell {total}) MUST smoothly transition almost all the way into Cell {total} (= Cell 1), guaranteeing ZERO loop jump when Cell {total} is later removed!",
        "- Keep the character's head & body at the EXACT SAME horizontal position inside every cell (slightly left-of-center on skill sheets so VFX unfolds to the right without pushing the character backward!) and the EXACT SAME chibi height (~34 logical pixels tall) in EVERY cell!",
        f"EXACT {total}-FRAME CHOREOGRAPHY (left-to-right, top-to-bottom):",
        *[f"- {b}" for b in anim_spec["frame_beats"]],
        f"- Color lock: {pal_rule}",
        f"- Style lock: {style['prompt']}.",
    ])
