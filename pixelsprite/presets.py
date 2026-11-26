"""Style presets & v2.2 Wide-Arena Closed-Loop (N+1 Ghost) Combat Specs with Attack Frames, Hitboxes & Ultra-Rich Pixel VFX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PIXEL_STYLES: dict[str, dict[str, Any]] = {
    "gba_chibi": {
        "label": "16-bit GBA Chibi (34px tall char inside wide 96x80 combat arena — massive VFX & accurate hitboxes!)",
        "cell_w": 96,
        "cell_h": 80,
        "cell_size": 96,  # backward-compat alias for width
        "char_height_px": 34,
        "palette_colors": 18,
        "prompt": (
            "authentic crisp 16-bit GBA / NeoGeo / Dead Cells indie action-RPG chibi pixel art, "
            "chunky low-resolution pixel grid (character ~34 logical pixels tall), cute 2-head chibi proportions "
            "with large expressive head and compact limbs, crisp 1-pixel dark purplish-brown outline (#261a2b) on character, "
            "clean flat 2-step cel shading using strictly 14-18 vibrant character colors, "
            "ZERO anti-aliasing, ZERO blur, ZERO painterly airbrush"
        ),
    },
    "gba_64": {
        "label": "Compact 64x64 GBA Chibi (34px tall char)",
        "cell_w": 64,
        "cell_h": 64,
        "cell_size": 64,
        "char_height_px": 34,
        "palette_colors": 18,
        "prompt": (
            "authentic crisp 16-bit GBA / SNES indie RPG chibi pixel art (Legend of Zelda Minish Cap / Eastward style), "
            "chunky low-resolution pixel grid (character ~34 logical pixels tall), cute 2-head chibi proportions, "
            "crisp 1-pixel dark outline (#261a2b), clean flat 2-step cel shading using 14-18 colors, ZERO anti-aliasing, ZERO blur"
        ),
    },
    "retro_32": {
        "label": "Ultra-Chunky Retro 32x32 (24px tall char, Stardew / Pico-8 style)",
        "cell_w": 32,
        "cell_h": 32,
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
# v2.2 WIDE-ARENA CLOSED-LOOP COMBAT & LOCOMOTION SPECS (96x80 Unified Pivot [30, 71])
#   - Character stays EXACTLY 34px tall chunky chibi across ALL 6 actions!
#   - Wide 96x80 arena gives 66px in front of her + 40px above for MASSIVE multi-layered VFX!
#   - Every combat action carries Startup / ACTIVE Hit Frames / Recovery + Auto-Fitted Hitboxes!
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
        "anchor_x_ratio": 0.3125,  # pivotX = 30 inside 96px wide cell
        "guide_x_ratio": 0.48,
        "guide_sprite_h_ratio": 0.48,
        "timing_mode": "breath",
        "frame_durations_ms": [165, 110, 105, 110, 170, 110, 105, 110],
        "hold_tags": {1: "呼气舒展", 5: "吸气顶点"},
        "combat": {},
        "vfx_hint": None,
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (full silver sword clearly held forward-up, red scarf flowing left, boots planted)",
            "Cell 2 (F2 INHALE 1): Subtle gentle inhale — chest lifts 1 pixel, scarf tail rises softly, full silver sword clearly visible",
            "Cell 3 (F3 INHALE 2): Rising softly — ponytail bobs gently up, knees slightly straighter, full silver sword clearly held forward",
            "Cell 4 (F4 PRE-APEX): Nearing soft breath peak, scarf billowing smoothly, eyes bright, full silver sword clearly visible",
            "Cell 5 (F5 BREATH APEX): Gentle inhale peak — chest proudly lifted 1-2 pixels, ponytail high-bouncy, full silver sword steady",
            "Cell 6 (F6 EXHALE 1): Relaxing softly back down, scarf waving gently, full silver sword steady",
            "Cell 7 (F7 EXHALE 2): Knees softening slightly into comfortable combat bounce, ponytail settling, full silver sword intact",
            "Cell 8 (F8 PRE-LOOP BRIDGE): 95% back to Cell 1 & Cell 9 — almost identical pose, full silver sword intact!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — exact neutral ready stance matching Reference Image 1!",
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
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.48,
        "guide_sprite_h_ratio": 0.48,
        "timing_mode": "even",
        "frame_durations_ms": [95, 95, 95, 95, 95, 95, 95, 95],
        "hold_tags": {},
        "combat": {},
        "vfx_hint": None,
        "scroll_speed": 115,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 CONTACT 1 — RIGHT LEG FORWARD): Follow YELLOW=Near-Right leg & CYAN=Far-Left leg! Bright warm-brown NEAR Right boot extended FORWARD heel-on-ground; darker shaded FAR Left boot extended BACKWARD toe-on-ground; Right sword-arm swings slightly BACK (opposite arm-leg counter-swing!)",
            "Cell 2 (F2 DOWN 1 — RIGHT LEG ABSORBS): NEAR Right boot plants FLAT under front torso absorbing weight (body dips 1px down!); FAR Left boot lifts OFF ground behind her; ponytail dips slightly",
            "Cell 3 (F3 PASSING 1 — RIGHT LEG VERTICAL SUPPORT, LEFT CROSSES CENTER): NEAR Right leg stands STRAIGHT VERTICAL directly underneath her body planted solidly on ground! FAR Left leg bends knee and swings FORWARD right past the vertical Right leg at center! (DO NOT lift front leg up!)",
            "Cell 4 (F4 HIGH/PUSH 1 — RIGHT PUSHES BACK, LEFT REACHES FORWARD): NEAR Right boot slides BACK behind hip pushing off toe; FAR Left boot swings HIGH & FORWARD ahead of body ready to land! Body at 1px walk peak; Right sword-arm swings forward",
            "Cell 5 (F5 CONTACT 2 — LEFT LEG FORWARD, EXACT SWAP OF F1!): Darker shaded FAR Left boot now extended FORWARD heel-on-ground; brighter NEAR Right boot now extended BACKWARD toe-on-ground! Right sword-arm swings clearly FORWARD-UP!",
            "Cell 6 (F6 DOWN 2 — LEFT LEG ABSORBS, SWAP OF F2!): FAR Left boot plants FLAT under front torso absorbing weight (body dips 1px down!); NEAR Right boot lifts OFF ground behind her!",
            "Cell 7 (F7 PASSING 2 — LEFT LEG VERTICAL SUPPORT, RIGHT CROSSES CENTER, SWAP OF F3!): FAR Left leg stands STRAIGHT VERTICAL directly underneath her body planted solidly on ground! Brighter NEAR Right leg bends knee and swings FORWARD right across in front of the Left leg at center!",
            "Cell 8 (F8 HIGH/PUSH 2 — LEFT PUSHES BACK, RIGHT REACHES FORWARD, SWAP OF F4!): FAR Left boot slides BACK behind hip pushing off toe; brighter NEAR Right boot swings HIGH & FORWARD just 1 tiny step before landing into Cell 9 (= Cell 1)!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — NEAR Right boot extended forward heel-on-ground, FAR Left boot extended backward, Right sword-arm slightly back!",
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
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.48,
        "guide_sprite_h_ratio": 0.48,
        "timing_mode": "even",
        "frame_durations_ms": [75, 75, 75, 75, 75, 75, 75, 75],
        "hold_tags": {},
        "combat": {},
        "vfx_hint": None,
        "scroll_speed": 225,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 R-STRIKE): Follow YELLOW=Near-Right leg & CYAN=Far-Left leg! Forward-leaning sprint — brighter NEAR Right boot striking FORWARD on ground, darker FAR Left leg kicked back; scarf streaming left; Right sword-arm pulled slightly back",
            "Cell 2 (F2 R-ABSORB): NEAR Right leg bent directly underneath torso absorbing sprint load; darker FAR Left knee tucked pulling forward underneath; body low",
            "Cell 3 (F3 R-PUSHOFF): NEAR Right leg extending FAR BACK pushing explosively off toe; darker FAR Left knee driving HIGH forward! Right sword-arm swinging forward",
            "Cell 4 (F4 FLIGHT 1 — AIRBORNE!): BOTH boots slightly off ground! Darker FAR Left leg reaching far forward to land, brighter NEAR Right boot kicked high behind!",
            "Cell 5 (F5 L-STRIKE — EXACT SWAP OF F1!): Darker FAR Left boot striking FORWARD on ground, brighter NEAR Right leg stretched far back! Right sword-arm swung clearly FORWARD!",
            "Cell 6 (F6 L-ABSORB — EXACT SWAP OF F2!): Darker FAR Left leg bent directly underneath torso absorbing load; brighter NEAR Right knee tucked pulling forward in foreground!",
            "Cell 7 (F7 L-PUSHOFF — EXACT SWAP OF F3!): Darker FAR Left leg pushing explosively FAR BACK off toe; brighter NEAR Right knee driving HIGH forward in foreground!",
            "Cell 8 (F8 FLIGHT 2 — AIRBORNE, SWAP OF F4!): BOTH boots slightly off ground! Brighter NEAR Right boot reaching far forward just 1 tiny step before landing into Cell 9 (= Cell 1), darker FAR Left boot kicked high behind!",
            "Cell 9 (GHOST LOOP = F1): MUST BE 100% IDENTICAL TO CELL 1 — brighter NEAR Right boot striking forward, darker FAR Left leg stretched back, scarf streaming left!",
        ],
    },
    "combo1_slash": {
        "id": "combo1_slash",
        "name": "普攻一式·烈风横斩 (8帧)",
        "key": "ATK 1",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1536x1024",  # Wide 512x341 per cell (1.5:1) for MASSIVE horizontal gale-wave VFX!
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.3125,  # pivotX = 30 inside 96x80!
        "guide_x_ratio": 0.28,     # Character in LEFT THIRD -> 72% wide open VFX runway on the right!
        "guide_sprite_h_ratio": 0.42,
        "timing_mode": "hitstop",
        "frame_durations_ms": [90, 180, 55, 225, 80, 80, 85, 90],
        "hold_tags": {2: "蓄力前摇", 4: "横斩判定 HITSTOP"},
        "combat": {
            "startup_frames": [1, 2],
            "active_frames": {
                3: {"hitId": 1, "damage": 16, "hitstopMs": 60, "knockback": [3.5, -0.5], "kind": "melee_arc", "hitbox_mode": "forward_vfx", "label": "瞬斩起效 HIT#1"},
                4: {"hitId": 1, "damage": 24, "hitstopMs": 140, "knockback": [6.0, -1.5], "kind": "melee_arc", "hitbox_mode": "forward_vfx", "label": "烈风横斩 MAX"},
            },
            "recovery_frames": [5, 6, 7, 8],
        },
        "vfx_hint": "mega_arc_right",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 STARTUP): Exact neutral ready stance matching Reference Image 1 anchored in LEFT THIRD of cell",
            "Cell 2 (F2 ANTICIPATION CHARGE): Low coiled sword pull-back crouch with blazing golden-cyan 4-point gleam flashing on blade tip AND small white wind-swirl ring gathering at boots!",
            "Cell 3 (F3 ACTIVE HIT START): Explosive forward dash-slash unleashing a thick sweeping electric-cyan & white pixel blade trail whipping forward + white ground wind-kick dust cloud behind boots!",
            "Cell 4 (F4 ACTIVE HITSTOP CLIMAX): HUGE, BOLD, MULTI-LAYERED ARCADE GALE-SLASH SHOCKWAVE filling the ENTIRE RIGHT TWO-THIRDS of the cell — thick pure-white core -> vivid electric-cyan -> deep sapphire-blue crescent wave + double secondary inner energy ribbons + bright flying pixel sparks + ground dust trail!",
            "Cell 5 (F5 RECOVERY DISSIPATE): Sword follow-through low-front as the huge cyan-azure shockwave breaks into glowing swirling pixel energy arcs, trailing sparks, and settling dust puffs on the right",
            "Cell 6 (F6 RECOVERY RECOIL): Rising back upright raising gleaming full silver sword with a few tiny fading cyan motes",
            "Cell 7 (F7 GUARD RETURN): Almost back to neutral ready stance, scarf settling smoothly",
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
        "grid": [4, 3],  # 12 cells = 11 active + Cell 12 Ghost (=F1) @ 384x341/cell!
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.3125,  # pivotX = 30 inside 96x80!
        "guide_x_ratio": 0.28,     # Character in LEFT THIRD -> 66px wide VFX battlefield on the right!
        "guide_sprite_h_ratio": 0.40,
        "timing_mode": "hitstop",
        "frame_durations_ms": [90, 185, 50, 55, 55, 55, 60, 260, 165, 85, 90],
        "hold_tags": {2: "影步蓄力", 8: "五连终结 HITSTOP", 9: "滑步急停"},
        "combat": {
            "startup_frames": [1, 2, 3],
            "active_frames": {
                4: {"hitId": 1, "damage": 14, "hitstopMs": 45, "knockback": [2.5, -1.0], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "一闪·苍岚上挑"},
                5: {"hitId": 2, "damage": 14, "hitstopMs": 45, "knockback": [2.5, 0.5],  "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "二闪·绯樱下劈"},
                6: {"hitId": 3, "damage": 16, "hitstopMs": 50, "knockback": [3.0, -0.5], "kind": "multi_slash", "hitbox_mode": "full_vfx",    "label": "三闪·烈阳回旋"},
                7: {"hitId": 4, "damage": 18, "hitstopMs": 55, "knockback": [3.5, -1.0], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "四闪·双影十字"},
                8: {"hitId": 5, "damage": 42, "hitstopMs": 180,"knockback": [9.5, -3.5], "kind": "aoe_nova",    "hitbox_mode": "aoe_nova",    "label": "五连终结·幻影爆裂"},
            },
            "recovery_frames": [9, 10, 11],
        },
        "vfx_hint": "mega_flurry",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 anchored in LEFT THIRD of cell",
            "Cell 2 (F2 CHARGE HOLD): Low explosive sprint-draw crouch with glowing cyan-magenta energy ring pulsing on ground under boots + crackling neon pink & cyan lightning sparks on hilt!",
            "Cell 3 (F3 PHANTOM BLINK DASH): Blazing forward dash leaving a glowing translucent electric-cyan PIXEL AFTERIMAGE SILHOUETTE clone behind her + razor-sharp horizontal neon pink & cyan speed-lines + kicking ground dust!",
            "Cell 4 (F4 ACTIVE HIT 1): HUGE soaring upward electric-cyan & sapphire multi-layered crescent wave sweeping across the RIGHT HALF with glowing white core, double energy trails, cyan ghost trail behind arm, and flying sparks!",
            "Cell 5 (F5 ACTIVE HIT 2): HUGE ferocious downward neon hot-pink/magenta & arcane-violet crescent cleave slamming across the RIGHT HALF with blazing white core, pink afterimage smear, and ground impact spark burst!",
            "Cell 6 (F6 ACTIVE HIT 3): HUGE 360-degree swirling blazing liquid-gold, flame-orange & crimson solar cyclone slash wrapping around her and sweeping huge to the right with flaming pixel embers & swirling ring!",
            "Cell 7 (F7 ACTIVE HIT 4): MASSIVE overlapping twin GIANT X-CROSS slashes (blazing cyan-azure + hot-pink magenta) + translucent glowing phantom afterimage clone striking alongside her, filling the entire right two-thirds with crackling sparks!",
            "Cell 8 (F8 ACTIVE HIT 5 FINISHER HITSTOP CLIMAX): GIGANTIC SCREEN-FILLING 5-HIT PRISM NOVA EXPLOSION filling the ENTIRE RIGHT TWO-THIRDS — blazing 8-point white-hot star core, crisscrossing cyan/magenta/gold shockwave beams, expanding circular pixel energy shockwave ring, ground blast dust, and bursting crystal shards!",
            "Cell 9 (F9 STYLISH SKID BRAKE HOLD): Cool crouched sliding brake with billowing white-tan ground skid dust clouds + glowing pink, cyan, and golden pixel embers scattering cleanly across the air",
            "Cell 10 (F10 RECOVERY): Rising smoothly upright raising gleaming full silver sword toward guard as last tiny sparkles fade",
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
        "grid": [5, 3],  # 15 cells = 14 active + Cell 15 Ghost (=F1) @ 307x341/cell!
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 28.0,
        "anchor_x_ratio": 0.3125,  # pivotX = 30 inside 96x80!
        "guide_x_ratio": 0.29,     # Character left-third -> huge celestial battlefield to the right & above!
        "guide_sprite_h_ratio": 0.37,
        "timing_mode": "hitstop",
        "frame_durations_ms": [90, 85, 195, 60, 145, 55, 55, 275, 155, 75, 90, 215, 85, 90],
        "hold_tags": {3: "星阵蓄力", 5: "浮空召唤", 8: "次元星爆 HITSTOP", 12: "收剑胜利定格"},
        "combat": {
            "startup_frames": [1, 2, 3, 4],
            "active_frames": {
                5: {"hitId": 1, "damage": 15, "hitstopMs": 60,  "knockback": [1.5, -4.0], "kind": "star_halo",    "hitbox_mode": "forward_vfx", "label": "星环震荡 HIT#1"},
                6: {"hitId": 2, "damage": 22, "hitstopMs": 55,  "knockback": [3.0, -2.0], "kind": "rift_slash",   "hitbox_mode": "forward_vfx", "label": "次元裂隙斩 HIT#2"},
                7: {"hitId": 3, "damage": 24, "hitstopMs": 55,  "knockback": [3.5, -2.0], "kind": "rift_slash",   "hitbox_mode": "forward_vfx", "label": "星辉十字斩 HIT#3"},
                8: {"hitId": 4, "damage": 65, "hitstopMs": 220, "knockback": [12.0, -5.0],"kind": "aoe_nova",     "hitbox_mode": "aoe_nova",    "label": "星陨次元大爆发 MAX"},
                9: {"hitId": 5, "damage": 28, "hitstopMs": 80,  "knockback": [8.0, 2.0],  "kind": "star_shatter", "hitbox_mode": "aoe_nova",    "label": "星晶碎裂追加 HIT#5"},
            },
            "recovery_frames": [10, 11, 12, 13, 14],
        },
        "vfx_hint": "mega_ultimate",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_beats": [
            "Cell 1 (F1 START): Exact neutral ready stance matching Reference Image 1 (boots cleanly on ground in left third)",
            "Cell 2 (F2 CROUCH): Low gathering crouch pulling silver sword close as faint glowing cyan-gold rune sparks ignite under her boots",
            "Cell 3 (F3 MAGIC CIRCLE CHARGE HOLD): Deep power crouch standing on a BRIGHT GLOWING GOLDEN-CYAN PIXEL MAGIC RUNE CIRCLE on the ground with spiraling golden-white star-energy pillars & sparks rising onto her blazing sword!",
            "Cell 4 (F4 EXPLOSIVE LAUNCH): Explosive rocket-leap HIGH OFF THE GROUND with huge blazing golden-cyan launch blast flare & circular ground dust shockwave erupting below her boots!",
            "Cell 5 (F5 ACTIVE HIT 1 AERIAL HANGTIME): High airborne levitation summoning a MASSIVE glowing golden-white-cyan 8-point CELESTIAL STAR HALO + orbiting star rings blazing brightly above & in front of her raised sword!",
            "Cell 6 (F6 ACTIVE HIT 2 RIFT SLASH 1): Still high airborne, tearing the sky with a GIGANTIC full-height diagonal neon-pink, magenta & electric-cyan DIMENSIONAL SPACE-RIFT SLASH + crackling violet lightning sparks across the entire right two-thirds!",
            "Cell 7 (F7 ACTIVE HIT 3 RIFT SLASH 2): Still high airborne, sweeping a GIGANTIC counter-diagonal blazing golden-white & flame-orange CELESTIAL CROSS-SLASH intersecting the pink rift into a blinding giant cosmic X-star with orbiting energy rings!",
            "Cell 8 (F8 ACTIVE HIT 4 DIMENSION NOVA HITSTOP CLIMAX): Still high airborne, UNLEASHING A MASSIVE FULL-ARENA CELESTIAL DIMENSION NOVA filling the ENTIRE RIGHT TWO-THIRDS — blinding pure-white core, huge 8-point rainbow cyan/magenta/gold/violet star rays, expanding circular cosmic shockwave ring, and shattering dimensional glass shards!",
            "Cell 9 (F9 ACTIVE HIT 5 SHATTER RAIN): Descending gracefully as the massive nova shatters outward into a dazzling cascade of big glowing cyan, hot-pink, violet & golden pixel crystal prism shards & shooting star trails across the whole right half!",
            "Cell 10 (F10 DESCENT): Graceful mid-air descent twisting gleaming sword downward surrounded by trailing golden-cyan stardust ribbons",
            "Cell 11 (F11 LANDING SHOCKWAVE SQUASH): Crisp bouncy knee-bend landing squarely back on the ground baseline kicking up twin billowing golden-white ground impact shockwave dust puffs left & right!",
            "Cell 12 (F12 VICTORY POSE HOLD): Heroic confident standing flourish holding gleaming silver sword proudly surrounded by floating twinkling golden & cyan 4-point pixel stars",
            "Cell 13 (F13 RELAX): Lowering sword smoothly and relaxing scarf back toward ready posture as final star sparkles fade",
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
    is_combat = bool(anim_spec.get("combat", {}).get("active_frames"))
    if is_combat:
        pal_rule = (
            f"STRICTLY LOCK character body colors to Image 1 ({', '.join(palette_hex[:16])}), "
            "while unleashing HUGE, RICH, MULTI-LAYERED 16-bit arcade pixel-art VFX gradients (pure white core -> ice cyan -> electric azure -> sapphire; "
            "pure white -> pastel pink -> hot magenta -> arcane violet; pure white -> bright starlight gold -> blazing flame orange -> crimson; plus crisp warm dust puffs)!"
            if palette_hex
            else "STRICTLY LOCK all character colors identically to Reference Image 1."
        )
    else:
        pal_rule = (
            f"STRICTLY LOCK ALL pixels exclusively to Reference Image 1's character palette ({', '.join(palette_hex[:16])}). "
            "ABSOLUTE ZERO VFX: NO magic waves, NO glowing slashes, NO sparkles, NO speed lines, NO dust clouds, NO floor cast shadows — ONLY the clean character sprite on 100% pure transparent background!"
            if palette_hex
            else "STRICTLY LOCK all colors identically to Reference Image 1. ZERO VFX, ZERO dust, ZERO shadows!"
        )
    is_loco = anim_spec["id"] in ("walk", "run")
    if is_combat:
        vfx_boost = (
            "- EPIC ARCADE VFX MANDATE: Make combat slashes, energy waves, afterimage clones, magic circles, ground dust shockwaves, and starfall explosions "
            "HUGE, BOLD, MULTI-LAYERED, AND GLOWING — filling the ENTIRE open right two-thirds of every active attack cell with crisp chunky pixel clusters (NEVER tiny timid thin arcs! NEVER draw ugly black outlines around glowing energy VFX!)."
        )
    elif is_loco:
        vfx_boost = (
            "- CRITICAL ANATOMICAL GAIT & LEFT/RIGHT LEG ALTERNATION RULE (FOLLOW REFERENCE IMAGE 2 SKELETON EXACTLY!):\n"
            "  * Reference Image 2 draws a color-coded kinematic leg skeleton in every cell: the BRIGHT YELLOW leg is her NEAR (foreground/Right) leg (draw with brighter warm brown boot), and the CYAN leg is her FAR (background/Left) leg (draw with slightly darker shadow-brown boot partially behind the near leg)!\n"
            "  * A foot that lands in FRONT (F1 / F5) MUST stay planted on the ground and SLIDE BACKWARD underneath her body (F2 -> F3 -> F4 / F6 -> F7 -> F8) while the OTHER leg lifts from behind, crosses through the vertical center (F3 / F7), and swings forward to land! NEVER march in place by lifting the front foot up and down!\n"
            "  * Keep natural opposite arm-leg counter-swing: Right sword-hand swings slightly BACK when Right leg steps forward (F1), and clearly FORWARD when Left leg steps forward (F5)! Keep full-length gleaming silver sword intact in EVERY SINGLE CELL.\n"
            "  * PURE CLEAN LOCOMOTION ONLY: Draw ZERO VFX, ZERO glowing arcs, ZERO sparkles, ZERO ground shadows, ZERO dust clouds — ONLY the pure clean character sprite on transparent background!"
        )
    else:
        vfx_boost = "- Keep clean crisp silhouette with full-length gleaming silver sword intact in EVERY SINGLE CELL. ZERO VFX, ZERO shadows."
    return "\n".join([
        f"EXACT {cols} columns by {rows} rows ({total} frames total, reading strictly left-to-right, top-to-bottom from Cell 1 to Cell {total}) "
        "CLOSED-LOOP 16-bit CHUNKY LOW-RES PIXEL ART SINGLE-ACTION SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, orange ponytail, red scarf, teal tunic, brown boots, FULL-LENGTH silver sword (NEVER shrink or omit the sword!), and crisp 1-pixel dark outline on the character in EVERY SINGLE CELL.",
        f"Reference Image 2 is the EXACT {cols}x{rows} grid & composition guide showing the sequence order (1 -> {total}), character left-third anchor line, VFX expansion zone, AND semi-transparent START/LOOP anchor poses stamped in BOTH Cell 1 and Cell {total} — DO NOT draw any grid lines, boxes, numbers, or guide tints in the final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {anim_spec.get('view_prompt', 'classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell')}.",
        "CRITICAL CLOSED-LOOP, SCALE & VFX RULES:",
        f"- Cell 1 (START) and Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL poses matching Reference Image 1!",
        f"- Cell {active} (immediately before Cell {total}) MUST smoothly transition almost all the way into Cell {total} (= Cell 1), guaranteeing ZERO loop jump when Cell {total} is later removed!",
        "- Keep the character's head & body at the EXACT SAME horizontal anchor position (LEFT THIRD on combat sheets!) and EXACT SAME chunky chibi height (~34 logical pixels tall) in EVERY cell — NEVER shrink the character to make room for VFX, let the VFX explode across the huge open right space!",
        vfx_boost,
        f"EXACT {total}-FRAME CHOREOGRAPHY (left-to-right, top-to-bottom):",
        *[f"- {b}" for b in anim_spec["frame_beats"]],
        f"- Color lock: {pal_rule}",
        f"- Style lock: {style['prompt']}.",
    ])
