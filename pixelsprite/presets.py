"""Style presets & v2.3 Structured 5-Dimension Per-Frame Choreography Specs (Zero Vague Prompts, Meaningful Physics-Driven VFX, Wide-Arena Hitboxes & Closed-Loop N+1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PIXEL_STYLES: dict[str, dict[str, Any]] = {
    "gba_chibi": {
        "label": "16-bit GBA Chibi (34px tall char inside wide 96x80 combat arena — massive VFX & accurate hitboxes!)",
        "cell_w": 96,
        "cell_h": 80,
        "cell_size": 96,
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


def _fb(
    cell: int,
    role: str,
    torso: str,
    arms_weapon: str,
    legs_feet: str,
    secondary: str,
    vfx_meaning: str = "NONE — pure clean character sprite, zero VFX, zero dust, zero floor shadow",
) -> dict[str, Any]:
    """Structured 5-dimension per-frame choreography builder (NEVER leave choreography vague for GPT Image 2.6!)."""
    return {
        "cell": cell,
        "role": role,
        "torso": torso,
        "arms_weapon": arms_weapon,
        "legs_feet": legs_feet,
        "secondary_motion": secondary,
        "vfx_meaning": vfx_meaning,
    }


def format_choreography_line(entry: dict[str, Any] | str) -> str:
    if isinstance(entry, str):
        return entry
    return (
        f"Cell {entry['cell']} ({entry['role']}): "
        f"[TORSO] {entry['torso']} | "
        f"[ARMS & WEAPON] {entry['arms_weapon']} | "
        f"[LEGS & FEET] {entry['legs_feet']} | "
        f"[SECONDARY] {entry['secondary_motion']} | "
        f"[VFX & PURPOSE] {entry['vfx_meaning']}"
    )


def validate_choreography(anim_spec: dict[str, Any]) -> dict[str, Any]:
    """
    Validate that an animation spec explicitly specifies per-frame torso, arms/weapon, legs/feet,
    secondary motion, and physically meaningful VFX instead of outsourcing choreography to GPT Image 2.6!
    """
    n_active = int(anim_spec["active_frames"])
    closed = bool(anim_spec.get("closed_loop", True))
    expected = n_active + (1 if closed else 0)
    choreo = anim_spec.get("frame_choreography")
    issues: list[str] = []

    if not choreo:
        beats = anim_spec.get("frame_beats", [])
        issues.append(
            "Missing structured `frame_choreography`! Avoid vague `frame_beats` strings — author explicit "
            "`torso`, `arms_weapon`, `legs_feet`, `secondary_motion`, and `vfx_meaning` for every frame."
        )
        if len(beats) != expected:
            issues.append(f"Expected {expected} frame descriptions, found {len(beats)}.")
        return {"ok": False, "structured": False, "frameCount": len(beats), "issues": issues}

    if len(choreo) != expected:
        issues.append(f"Expected {expected} choreography entries ({n_active} active + {1 if closed else 0} ghost), found {len(choreo)}.")

    req_keys = ("torso", "arms_weapon", "legs_feet", "secondary_motion", "vfx_meaning")
    for idx, item in enumerate(choreo):
        if not isinstance(item, dict):
            issues.append(f"Cell {idx+1}: must be a structured dict with keys {req_keys}.")
            continue
        for k in req_keys:
            val = str(item.get(k, "")).strip()
            if len(val) < 10:
                issues.append(f"Cell {idx+1} `{k}` is missing or too vague ('{val}') — describe exact anatomical/physical action!")

    return {"ok": len(issues) == 0, "structured": True, "frameCount": len(choreo), "issues": issues}


# ==============================================================================
# v2.3 STRUCTURED 5-DIMENSION CHOREOGRAPHY ANIMATION SPECS
# NEVER let GPT Image 2.6 guess limbs or invent meaningless glowing blobs!
# Every single frame defines: Torso + Arms/Weapon + Left/Right Legs + Secondary + Purposeful VFX!
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
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.48,
        "guide_sprite_h_ratio": 0.48,
        "timing_mode": "breath",
        "frame_durations_ms": [165, 110, 105, 110, 170, 110, 105, 110],
        "hold_tags": {1: "呼气舒展", 5: "吸气顶点"},
        "combat": {},
        "vfx_hint": None,
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 EXHALE READY",
                "Neutral upright alert stance matching Reference Image 1, chest relaxed, gaze focused right",
                "Right hand grips hilt holding gleaming full-length silver short sword angled 35deg forward-up; left arm relaxed at hip",
                "Both brown boots planted firmly shoulder-width apart on ground baseline (near right boot slightly forward, far left boot slightly back), knees softly bent",
                "Red scarf flows gently behind-left; orange ponytail rests naturally at shoulder height"),
            _fb(2, "F2 INHALE START",
                "Chest begins expanding upward (+0.5px), shoulders gently squaring",
                "Right sword-hand lifts 1px with breath, blade stays exact full length & steady 35deg angle; left hand steady",
                "Both boots stay 100% nailed to ground baseline, knees start gently straightening",
                "Scarf tail lifts softly in light breeze; ponytail lifts slightly"),
            _fb(3, "F3 INHALE MID",
                "Ribcage lifted (+1px), posture proud and alert, chin level",
                "Right sword-hand rises slightly higher (38deg angle), full silver blade crisp and unobstructed",
                "Both boots 100% planted at identical ground positions, knees slightly straighter",
                "Scarf billows smoothly upward-left; ponytail bobs gently higher"),
            _fb(4, "F4 PRE-APEX",
                "Approaching top of inhale (+1.5px), bright confident eyes looking forward",
                "Sword held poised near top of breath arc, golden crossguard clearly visible, off-hand relaxed",
                "Both boots firmly rooted on ground without sliding, stance stable",
                "Scarf reaches high wave curve; ponytail buoyant at top"),
            _fb(5, "F5 BREATH APEX",
                "Gentle inhale peak (+2px max, NEVER stretch legs abnormally tall!), poised heroic readiness",
                "Right sword-hand holds full silver blade steady at peak ready height (40deg), wrist firm",
                "Both boots planted flat on exact same ground coordinates, legs nearly straight yet relaxed",
                "Scarf curls smoothly at top of wind wave; ponytail floating slightly higher"),
            _fb(6, "F6 EXHALE START",
                "Chest begins lowering smoothly (-1px), shoulders relaxing into combat readiness",
                "Right sword-hand lowers 1px smoothly back toward 37deg, full blade intact",
                "Both boots remain fixed on ground, knees begin softening slightly",
                "Scarf begins trailing downward-left with soft lag; ponytail drops slightly"),
            _fb(7, "F7 EXHALE MID",
                "Torso settles down into springy ready posture, weight balanced evenly",
                "Sword lowers smoothly to 35deg ready angle, left arm returns to neutral balance",
                "Both boots planted firmly on ground, knees softly bent matching F1 readiness",
                "Scarf settles into relaxed mid-wave; ponytail bounces softly down"),
            _fb(8, "F8 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 9 — relaxed upright ready chest",
                "Right hand holds full silver sword at exact 35deg Cell 1 angle",
                "Both boots planted in exact Cell 1 stance (zero foot sliding!)",
                "Scarf and ponytail nearly identical to Cell 1, ready for seamless loop"),
            _fb(9, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — neutral upright alert stance matching Reference Image 1",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width on baseline",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
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
        "frame_choreography": [
            _fb(1, "F1 CONTACT 1 (RIGHT LEG FORWARD)",
                "Slight energetic forward walk lean (5deg), neutral mid height, shoulders twisted slightly counter to hips",
                "OPPOSITE ARM-LEG SWING: Right sword-hand swings slightly BACK at hip holding full silver sword angled forward-up; left off-hand swings slightly forward",
                "FOLLOW YELLOW=Near-Right & CYAN=Far-Left SKELETON: Bright gold-cuff NEAR Right leg extended FORWARD heel-striking ground; darker shaded FAR Left leg extended BACKWARD toe pushing off ground",
                "Red scarf trails smoothly left with brisk walk momentum; ponytail bounces horizontally"),
            _fb(2, "F2 DOWN 1 (RIGHT LEG ABSORBS WEIGHT)",
                "Body cushions DOWN (-1.5px lowest point of step!) absorbing landing weight onto right leg",
                "Right sword-hand begins swinging forward past waist; full silver blade completely intact",
                "NEAR Right boot plants FLAT solidly under front torso with knee bent absorbing weight; darker FAR Left boot lifts OFF ground behind her with knee bent back",
                "Ponytail dips slightly down from landing inertia; scarf flows smoothly behind"),
            _fb(3, "F3 PASSING 1 (RIGHT LEG VERTICAL SUPPORT, LEFT CROSSES CENTER)",
                "Body rises upright directly over supporting leg, head straight and confident",
                "Both arms pass neutral beside torso; Right hand holds full silver sword clearly forward-right",
                "CRITICAL PASSING POSE: NEAR Right leg stands STRAIGHT VERTICAL directly under hip planted solidly on ground! Darker FAR Left leg bends knee and swings FORWARD right through center past the right knee! (NEVER lift front foot!)",
                "Scarf waves steadily behind; ponytail rises softly with upright torso"),
            _fb(4, "F4 HIGH/PUSH 1 (RIGHT PUSHES BACK, LEFT REACHES FORWARD)",
                "Body reaches walk HIGH PEAK (+1.5px) propelled upward by back toe push-off",
                "Right sword-hand swings clearly FORWARD as left leg reaches forward (natural counter-swing!), full blade gleaming",
                "NEAR Right leg slides BACKWARD behind hip extending onto pushing toe; darker FAR Left leg swings HIGH & FORWARD ahead of torso preparing heel-strike!",
                "Ponytail arcs up at walk peak; scarf streams crisply left"),
            _fb(5, "F5 CONTACT 2 (LEFT LEG FORWARD — EXACT SWAP OF F1!)",
                "Neutral mid height, slight forward lean, shoulders counter-rotated opposite to F1",
                "OPPOSITE TO F1: Right sword-hand reaches fullest FORWARD-UP swing holding full silver sword; left off-hand swings back",
                "EXACT LEFT/RIGHT SWAP OF F1: Darker shaded FAR Left leg extended FORWARD heel-striking ground; bright gold-cuff NEAR Right leg extended BACKWARD toe pushing ground!",
                "Red scarf ripples in rhythm; ponytail level"),
            _fb(6, "F6 DOWN 2 (LEFT LEG ABSORBS WEIGHT — SWAP OF F2!)",
                "Body cushions DOWN (-1.5px lowest point!) absorbing weight onto left leg",
                "Right sword-hand begins swinging smoothly back toward hip, full silver sword steady",
                "Darker FAR Left boot plants FLAT solidly under front torso with bent knee; bright gold-cuff NEAR Right boot lifts OFF ground behind her with knee bent back!",
                "Ponytail dips softly from cushion impact; scarf undulates smoothly"),
            _fb(7, "F7 PASSING 2 (LEFT LEG VERTICAL SUPPORT, RIGHT CROSSES IN FRONT — SWAP OF F3!)",
                "Body rises upright directly over supporting left leg",
                "Arms cross neutral near waist, full silver sword clearly visible at right side",
                "CRITICAL PASSING POSE (SWAP): Darker FAR Left leg stands STRAIGHT VERTICAL directly under hip planted solidly on ground! Bright gold-cuff NEAR Right leg bends knee and swings FORWARD right IN FRONT OF the left leg at center!",
                "Scarf waves cleanly; ponytail lifts with vertical torso"),
            _fb(8, "F8 HIGH/PUSH 2 (LEFT PUSHES BACK, RIGHT REACHES INTO F1 — SWAP OF F4!)",
                "Body at walk HIGH PEAK (+1.5px) pushing smoothly into next right-foot step",
                "Right sword-hand swings gently back toward F1 ready position, full silver blade crisp",
                "Darker FAR Left leg slides BACKWARD behind hip pushing off toe; bright gold-cuff NEAR Right leg swings HIGH & FORWARD 1 tiny step before heel-striking Cell 9 (= Cell 1)!",
                "Ponytail bounces softly at crest; scarf trailing left"),
            _fb(9, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — slight forward walk lean, mid height",
                "100% IDENTICAL TO CELL 1 — Right sword-hand slightly back at hip, full silver sword intact",
                "100% IDENTICAL TO CELL 1 — Bright NEAR Right leg extended forward heel-on-ground, darker FAR Left leg extended back!",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
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
        "frame_choreography": [
            _fb(1, "F1 R-STRIKE",
                "Dynamic 15deg forward sprint lean, eyes fiercely locked ahead",
                "Right sword-hand pulled back near hip holding full silver sword pointed forward-up; left elbow pumping forward",
                "FOLLOW YELLOW=Near-Right & CYAN=Far-Left SKELETON: Bright NEAR Right boot strikes FORWARD onto ground; darker FAR Left leg kicked back behind hip",
                "Red scarf and orange ponytail stream straight horizontally left from high sprint speed"),
            _fb(2, "F2 R-ABSORB",
                "Torso compresses low (-1.5px) coiled like a spring directly over supporting right leg",
                "Right sword-hand begins driving forward; full silver sword completely intact",
                "NEAR Right leg planted directly underneath torso with deeply bent knee absorbing impact; darker FAR Left leg tucks tightly underneath pulling forward",
                "Ponytail whips tightly behind head; scarf taut horizontal"),
            _fb(3, "F3 R-PUSHOFF",
                "Torso surges upward-forward powered by explosive calf drive",
                "Right sword-hand drives forward across front waist; left arm drives backward",
                "NEAR Right leg extends FAR BACK pushing explosively off toe tip; darker FAR Left knee drives HIGH forward-up!",
                "Scarf snaps high-left; ponytail lifts behind"),
            _fb(4, "F4 AIRBORNE FLIGHT 1",
                "FULL SPRINT SUSPENSION — entire body floats +2px off ground in dynamic forward stride!",
                "Right sword-hand swings to peak forward reach, full silver sword crisp",
                "BOTH BOOTS CLEARLY AIRBORNE OFF GROUND! Darker FAR Left leg stretches far forward ready to strike; bright NEAR Right leg kicks high behind!",
                "Scarf & ponytail floating straight back in mid-air"),
            _fb(5, "F5 L-STRIKE (EXACT SWAP OF F1!)",
                "Forward sprint lean, landing firmly onto opposite leg",
                "Right sword-hand extended forward-up, left arm pulled back (exact opposite of F1!)",
                "EXACT SWAP OF F1: Darker FAR Left boot strikes FORWARD onto ground; bright NEAR Right leg stretched far back!",
                "Scarf streaming horizontally left; ponytail taut"),
            _fb(6, "F6 L-ABSORB (SWAP OF F2!)",
                "Torso compresses low (-1.5px) coiled over planted left leg",
                "Right sword-hand pulls smoothly back toward hip, full silver sword steady",
                "Darker FAR Left leg planted bent directly under torso absorbing impact; bright NEAR Right knee tucks tightly pulling forward in foreground!",
                "Ponytail dips behind; scarf whips taut"),
            _fb(7, "F7 L-PUSHOFF (SWAP OF F3!)",
                "Torso explodes forward-up off left toe push",
                "Right sword-hand pulls back behind waist coiling for F1, left elbow pumps forward",
                "Darker FAR Left leg extends FAR BACK pushing off toe; bright NEAR Right knee drives HIGH forward in foreground!",
                "Scarf billows horizontally; ponytail kicks upward"),
            _fb(8, "F8 AIRBORNE FLIGHT 2 (SWAP OF F4!)",
                "FULL SPRINT SUSPENSION (+2px airborne!) gliding cleanly into F9 (= F1) landing!",
                "Right sword-hand positioned nearly matching Cell 1, full silver sword gleaming",
                "BOTH BOOTS AIRBORNE! Bright NEAR Right boot reaches far forward 1 step before landing in Cell 9 (= F1); darker FAR Left boot kicked high behind!",
                "Scarf & ponytail streaming smoothly left"),
            _fb(9, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — 15deg forward sprint lean",
                "100% IDENTICAL TO CELL 1 — Right sword-hand near hip, full silver sword forward-up",
                "100% IDENTICAL TO CELL 1 — Bright NEAR Right boot striking forward, darker FAR Left leg kicked back!",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail horizontal"),
        ],
    },
    "combo1_slash": {
        "id": "combo1_slash",
        "name": "普攻一式·烈风横斩 (8帧)",
        "key": "ATK 1",
        "active_frames": 8,
        "closed_loop": True,
        "grid": [3, 3],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.28,
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
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral upright ready stance matching Reference Image 1 anchored in LEFT THIRD of cell",
                "Right hand grips full silver sword at 35deg front guard; left arm balanced at side",
                "Both boots planted cleanly shoulder-width apart on ground baseline",
                "Red scarf gently flowing behind-left; ponytail calm"),
            _fb(2, "F2 STARTUP ANTICIPATION COIL",
                "Coiled low crouch (-2px) twisting shoulders CLOCKWISE back-left to store torque, fierce determined stare right",
                "Right arm pulls silver sword tightly BACK near left shoulder/waist (winding up for horizontal draw-cleave!); left hand reaches forward pointing toward target for balance",
                "Left back knee bends deeply loading spring force onto rear boot; front right boot braces heel down",
                "Ponytail swings backward-left with recoil; scarf wraps tightly back",
                "TELEGRAPH VFX: Crisp 4-point golden-cyan blade-charge glint igniting directly at the coiled sword tip + small white wind-gathering swirl ring right under her braced boots (signals imminent slash!)"),
            _fb(3, "F3 ACTIVE HIT#1 SNAP CLEAVE",
                "Explosive torso UNCOIL snapping chest forward-right into deep horizontal attack lunge!",
                "Right arm whips silver sword forward horizontally mid-swing cutting cleanly left-to-right across chest level; left arm pulls back behind ribs for counter-torque",
                "Front right boot lunges forward planting hard to brake momentum; rear left leg extends straight back pushing off toe",
                "Scarf & ponytail whip sharply backward-left from sudden forward burst",
                "ACTIVE SLASH START VFX: Thick white-core -> electric-cyan blade motion-smear crescent extending directly from the moving sword blade edge across right half + small white wind-kick dust puff erupting BACKWARD behind her pushing rear boot!"),
            _fb(4, "F4 ACTIVE HIT#1 CLIMAX HITSTOP",
                "Peak full-extension heroic lunge leaning boldly forward-right, shoulder fully opened into follow-through",
                "Right arm extended straight forward holding gleaming horizontal silver blade at end of cleave; left hand thrown back for dramatic balance",
                "Wide heroic power stance — front right knee bent deeply bearing forward lunge, back left leg anchored straight behind",
                "Red scarf streams straight horizontally behind; ponytail flared wide",
                "ACTIVE HITBOX CLIMAX VFX: MASSIVE multi-layered horizontal GALE-SLASH SHOCKWAVE (pure white leading edge -> vivid electric-cyan -> deep sapphire-blue outer crescent + inner wind ribbons + trailing ground-skimming dust wave) sweeping forward from her sword blade across the ENTIRE right two-thirds — visually defining the lethal 65px melee Hitbox!"),
            _fb(5, "F5 RECOVERY FOLLOW-THROUGH",
                "Weight begins shifting back slightly off front knee as lunge momentum bleeds off",
                "Right arm drops silver sword cleanly downward-front finishing follow-through; left hand swings forward toward guard",
                "Front right boot firmly planted absorbing braking force; rear left boot begins stepping forward slightly to recover stance",
                "Scarf waves downward-left slowing down; ponytail drops forward slightly",
                "DISSIPATION VFX: The gale shockwave breaks into detached fading sapphire wind ribbons & cooling cyan sparks drifting forward-right + low settling dust wisps on ground (visually signals active hitbox is OVER!)"),
            _fb(6, "F6 RECOVERY RECOIL",
                "Torso rises smoothly upright back to neutral center height",
                "Right wrist smoothly lifts gleaming full silver sword upward toward neutral 35deg guard",
                "Feet step smoothly back into balanced shoulder-width neutral stance on ground baseline",
                "Scarf lifts and ripples gently back into idle curve; ponytail settles",
                "FADING VFX: Only 2-3 tiny fading cyan wind specks dissipating far right + tiny settling dust crumb on floor"),
            _fb(7, "F7 RECOVERY GUARD SETTLE",
                "Nearly back to Cell 1 upright posture, breathing steady",
                "Right hand brings full silver sword cleanly into neutral ready guard; left arm relaxed",
                "Both boots planted cleanly in exact neutral stance",
                "Scarf & ponytail settling calmly",
                "NONE — pure clean character settling back to neutral"),
            _fb(8, "F8 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 9 — neutral upright ready posture",
                "Full silver sword held at exact 35deg Cell 1 guard angle",
                "Both boots planted in exact Cell 1 neutral stance",
                "Scarf & ponytail 95% matching Cell 1"),
            _fb(9, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    "skill_phantom_flurry": {
        "id": "skill_phantom_flurry",
        "name": "R·幻影五连乱舞 (11帧)",
        "key": "SKILL R",
        "active_frames": 11,
        "closed_loop": True,
        "grid": [4, 3],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.28,
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
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral ready stance anchored in LEFT THIRD of cell",
                "Right hand grips full silver sword at 35deg forward-up; left arm steady",
                "Both boots planted shoulder-width on baseline",
                "Scarf flowing gently behind-left"),
            _fb(2, "F2 STARTUP PHANTOM STANCE CHARGE",
                "Low explosive iaido sprint-crouch (-3px) leaning forward coiled to blink-dash",
                "Right hand draws silver sword low-tight at waist (ready for lightning draw); left hand steadies scabbard/hip",
                "Both knees deeply bent in sprinter crouch, weight loaded onto toes",
                "Ponytail pressed low behind; scarf tucked close",
                "STARTUP TELEGRAPH VFX: Glowing neon pink & cyan phantom-step energy ring pulsing directly under her boots + crackling cyan/pink sparks along the drawn blade (telegraphs high-speed phantom flurry!)"),
            _fb(3, "F3 STARTUP PHANTOM BLINK DASH",
                "Steep 25deg forward bullet-dash lean darting right at blinding speed",
                "Right sword-arm tucked tight back-right primed for upward draw slash; left arm swept back",
                "Front right knee drives forward hard; back left leg pushes off leaving ground dust",
                "Scarf & ponytail stretched straight behind like speed banners",
                "DASH MOMENTUM VFX: Translucent electric-cyan PIXEL AFTERIMAGE SILHOUETTE trailing directly behind her body + crisp horizontal pink/cyan speed lines + backward-kicked white ground dust (physically visualizes superhuman dash velocity!)"),
            _fb(4, "F4 ACTIVE HIT#1 — RISING AZURE UPPERCUT SLASH",
                "Torso springs UPWARD twisting open from low dash into high rising slash!",
                "Right arm sweeps full silver sword violently BOTTOM-LEFT TO TOP-RIGHT upward diagonal; left arm counter-balances down-left",
                "Front right foot pivots firmly forward; rear heel lifts slightly driving upward torque",
                "Scarf whips down-left opposite to the upward blade arc",
                "HIT#1 DIRECTIONAL VFX: HUGE rising bottom-to-top electric-cyan -> azure -> sapphire crescent blade wave curving directly along her upward sword sweep (pure white hot inner edge + trailing sparks matching upward cut!)"),
            _fb(5, "F5 ACTIVE HIT#2 — DOWNWARD CRIMSON-PINK CLEAVE",
                "Torso slams DOWNWARD leaning aggressively forward-right into heavy chop!",
                "Right arm chops silver sword violently TOP-RIGHT TO BOTTOM-RIGHT downward diagonal finishing low near ground; left arm raised back",
                "Wide braced lunge — front right knee drives low, rear leg extended firmly back",
                "Ponytail & scarf whip upward-left opposite to downward slam",
                "HIT#2 DIRECTIONAL VFX: HUGE downward-arcing neon hot-pink/magenta -> white-core crescent cleave following the exact top-to-bottom blade path, crashing cleanly into a blazing pink-white spark flare where the blade nears the floor!"),
            _fb(6, "F6 ACTIVE HIT#3 — 360 SOLAR CYCLONE SPIN",
                "Full high-speed body spin pivoting rapidly around vertical axis, face glancing intensely right",
                "Right arm swings sword in wide 360-degree horizontal-diagonal cyclone sweeping across front & wrapping around waist",
                "Pivoting sharply on front ball of foot with rear boot sweeping around in martial spin",
                "Scarf spirals dynamically around neck following spin direction",
                "HIT#3 DIRECTIONAL VFX: HUGE swirling 360-degree blazing liquid-gold -> flame-orange -> fiery crimson circular cyclone wave wrapping seamlessly around her spinning blade trajectory + spinning ember sparks (shows full-body spin momentum!)"),
            _fb(7, "F7 ACTIVE HIT#4 — TWIN PHANTOM X-CROSS",
                "Explosive forward double-strike stance braced squarely facing right",
                "Right sword-arm snaps back-to-back diagonal cross slashes while her cyan phantom echo strikes the counter-diagonal simultaneously!",
                "Solid athletic wide-planted stance bracing rapid twin recoil",
                "Scarf flares horizontally behind",
                "HIT#4 DIRECTIONAL VFX: MASSIVE intersecting GIANT X-CROSS slashes (blazing electric-cyan diagonal + hot-pink magenta counter-diagonal) meeting at a glowing white center right in front of her blade + translucent cyan phantom clone overlapping her strike!"),
            _fb(8, "F8 ACTIVE HIT#5 — FINISHER PRISM NOVA HITSTOP",
                "Heroic full-extension thrust lunge locking posture at climax impact!",
                "Right arm thrusts gleaming silver sword straight forward piercing the exact center of the X-cross; left arm flung back for dramatic poise",
                "Deep heroic planted forward lunge bracing against explosive shockwave",
                "Scarf & ponytail blasted violently straight backward-left by the explosion shockwave!",
                "HIT#5 FINISHER CLIMAX VFX: GIGANTIC 5-HIT PRISM NOVA detonating directly from her sword tip across the ENTIRE right two-thirds — blinding 8-point white-hot star core, concentric circular violet-cyan-magenta shockwave ring, bursting crystal shards, and rolling ground-blast dust cloud directly beneath the blast!"),
            _fb(9, "F9 RECOVERY STYLISH SKID BRAKE",
                "Cool low crouched recoil leaning slightly back-left to brake against blast pushback",
                "Right arm holds silver sword low horizontally stabilizing crouch; left hand braces near ground",
                "Both boots planted angled forward skidding cleanly backward across floor",
                "Scarf settles forward slightly then trails back; ponytail drops low",
                "BRAKING VFX: Billowing white-tan ground SKID DUST clouds kicking forward from her braking boot heels + scattered fading pink/cyan/gold embers floating calmly (clearly signals attack hitbox has ended!)"),
            _fb(10, "F10 RECOVERY STANDING GUARD",
                "Rising smoothly back upright from low skid crouch",
                "Right arm raises gleaming full silver sword smoothly toward neutral 35deg guard",
                "Legs step cleanly back into balanced neutral shoulder-width stance",
                "Scarf & ponytail lift smoothly back into calm idle flow",
                "FADING VFX: Only 3 tiny twinkling cooling star sparks fading out cleanly in front"),
            _fb(11, "F11 PRE-LOOP BRIDGE",
                "95% back to Cell 1 upright neutral stance",
                "Full silver sword held steady at exact 35deg ready guard",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 95% identical to Cell 1"),
            _fb(12, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — neutral ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    "ult_starfall_slash": {
        "id": "ult_starfall_slash",
        "name": "F·星陨次元斩 (14帧奥义)",
        "key": "ULT F",
        "active_frames": 14,
        "closed_loop": True,
        "grid": [5, 3],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 28.0,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.29,
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
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral upright stance matching Reference Image 1 anchored in left third",
                "Right hand grips full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted squarely on ground baseline",
                "Scarf gently flowing behind-left"),
            _fb(2, "F2 STARTUP GATHERING CROUCH",
                "Dropping into focused crouch (-2px) gathering cosmic breath",
                "Right hand pulls silver sword close across waist; left hand touches near hilt channeling power",
                "Both knees bend low loading explosive vertical jump energy onto planted boots",
                "Ponytail lowers behind shoulders; scarf curls down",
                "EARLY TELEGRAPH VFX: Faint glowing cyan-gold rune sparks igniting directly beneath her boots"),
            _fb(3, "F3 STARTUP MAGIC CIRCLE CHARGE HOLD",
                "Deepest coiled launch crouch (-3px) eyes glowing with intense focus looking up-right",
                "Right hand angles blazing silver sword upward-right channeling rising starlight into the blade",
                "Both boots planted wide & deeply bent right at the center of the glowing ground rune circle",
                "Scarf & ponytail whipped UPWARD by the rising vertical energy updraft!",
                "ULTIMATE TELEGRAPH VFX: Bright glowing GOLDEN-CYAN PIXEL MAGIC RUNE CIRCLE flat under her boots + spiraling golden-white star-energy ribbon & rising vertical light motes flowing straight up into her sword!"),
            _fb(4, "F4 STARTUP EXPLOSIVE ROCKET LAUNCH",
                "Explosive vertical rocket-leap launching HIGH OFF THE GROUND (+16px airborne!) chest open",
                "Right arm drives gleaming sword sharply upward-right leading the ascent; left arm pulled tight",
                "Front right knee tucked dynamically high; back left leg extended straight down from takeoff thrust — BOTH boots high off floor!",
                "Red scarf & ponytail trail straight DOWNWARD-LEFT against her rapid upward velocity!",
                "LAUNCH THRUST VFX: Blazing golden-white vertical launch flare + billowing twin white-tan ground shockwave dust clouds erupting directly on the floor underneath her takeoff point!"),
            _fb(5, "F5 ACTIVE HIT#1 — AERIAL CELESTIAL STAR HALO",
                "High mid-air levitation (+22px airborne!) hovering effortlessly with proud heroic posture",
                "Right arm raises gleaming silver sword high toward upper-right summoning a celestial star right off the blade tip; left hand poised for balance",
                "Airborne hover tuck — right knee bent cleanly forward, left leg gracefully extended slightly lower in mid-air",
                "Scarf floating weightlessly behind-left; ponytail buoyant",
                "HIT#1 SUMMON VFX: MASSIVE glowing 8-point golden-white & cyan CELESTIAL STAR HALO + orbiting cyan-gold energy rings expanding outward directly around her raised sword tip!"),
            _fb(6, "F6 ACTIVE HIT#2 — AERIAL DIMENSIONAL RIFT SLASH 1",
                "Still high airborne (+24px!), twisting shoulders sharply into sweeping downward-right slash!",
                "Right arm slashes silver sword diagonally TOP-RIGHT TO BOTTOM-LEFT tearing open space itself; left arm swings back",
                "Dynamic mid-air scissor posture balancing slash recoil, both boots clearly off ground",
                "Scarf whips cleanly upward-left opposite to the diagonal slash",
                "HIT#2 DIRECTIONAL RIFT VFX: GIGANTIC full-height diagonal neon-pink, magenta & arcane-violet DIMENSIONAL SPACE-RIFT SLASH with crackling violet lightning arcs following the exact top-right-to-bottom-left cut across the right two-thirds!"),
            _fb(7, "F7 ACTIVE HIT#3 — AERIAL COSMIC CROSS-SLASH 2",
                "Still high airborne (+24px!), snapping shoulders into fierce counter-diagonal slash!",
                "Right arm sweeps silver sword diagonally TOP-LEFT TO BOTTOM-RIGHT intersecting the previous pink rift cleanly into a giant X!",
                "Mid-air combat lunge tuck, legs braced dynamically in air",
                "Scarf streams boldly left from slash torque",
                "HIT#3 DIRECTIONAL CROSS VFX: GIGANTIC blazing golden-white & flame-orange CELESTIAL COUNTER-SLASH intersecting the purple-pink rift into a blinding cosmic X-star with orbiting golden rings!"),
            _fb(8, "F8 ACTIVE HIT#4 — FULL-ARENA DIMENSION NOVA HITSTOP",
                "Peak mid-air heroic posture (+22px airborne!) locking frame at supreme detonation climax!",
                "Right arm extends silver sword squarely forward-right anchoring the epicenter of the dimensional nova; left arm thrown wide back",
                "Classic anime mid-air heroic suspension pose, boots high above ground",
                "Scarf & ponytail blown furiously straight back-left by the shockwave blast!",
                "HIT#4 CLIMAX NOVA VFX: MASSIVE FULL-ARENA 8-POINT RAINBOW CELESTIAL DIMENSION NOVA filling the ENTIRE right two-thirds — blinding pure-white star core radiating electric cyan, hot-pink, starlight gold & arcane violet rays + circular cosmic shockwave ring + fracturing dimensional glass shards!"),
            _fb(9, "F9 ACTIVE HIT#5 — SHATTERING CRYSTAL PRISM RAIN",
                "Beginning graceful descent (+20px airborne) relaxing slightly as nova shatters outward",
                "Right hand angles gleaming silver sword downward-right guiding the cascading crystal storm",
                "Legs begin extending gracefully downward preparing for landing",
                "Scarf floats upward slightly as she begins descending",
                "HIT#5 SHATTER FOLLOW-UP VFX: The nova shatters outward into a dazzling diagonal shower of large glowing cyan, hot-pink, violet & golden pixel crystal prism shards & shooting star streaks raining across the right two-thirds!"),
            _fb(10, "F10 RECOVERY AERIAL DESCENT",
                "Graceful controlled descent (+14px -> dropping toward ground), chin tucked watching landing spot",
                "Right hand twists silver sword cleanly downward-right at side; left arm spreads slightly for landing balance",
                "Both legs extend cleanly downward with toes pointed toward ground baseline",
                "Scarf & ponytail stream UPWARD-LEFT trailing behind her downward fall!",
                "DESCENT TRAIL VFX: Soft fading swirling gold & cyan stardust ribbons curving gently around her falling sword (signals active damage window is over!)"),
            _fb(11, "F11 RECOVERY LANDING SHOCKWAVE SQUASH",
                "Crisp bouncy landing squash (-3px low crouch) firmly absorbing gravity impact on ground!",
                "Right hand holds gleaming silver sword steady low-front bracing crouch; left arm balances near knee",
                "BOTH BOOTS PLANTED SQUARELY BACK ON GROUND BASELINE with deeply bent shock-absorbing knees!",
                "Ponytail & scarf drop downward with landing squash inertia",
                "LANDING IMPACT VFX: Twin billowing white-tan & golden ground impact SHOCKWAVE DUST PUFFS bursting symmetrically left and right directly from beneath her landing boots + 2 tiny golden sparks!"),
            _fb(12, "F12 RECOVERY HEROIC VICTORY FLOURISH HOLD",
                "Standing tall & proud upright (+1px chest proud!), triumphant confident expression",
                "Right arm raises gleaming full silver sword proudly forward-up in classic JRPG victory flourish; left hand on hip",
                "Confident wide heroic standing stance cleanly grounded on baseline",
                "Red scarf billows majestically left; ponytail high & bouncy",
                "VICTORY PUNCTUATION VFX: 4 clean twinkling golden & electric-cyan 4-point pixel stars sparkling gently around her raised blade (heroic finish punctuation!)"),
            _fb(13, "F13 RECOVERY RELAX",
                "Relaxing smoothly from victory flourish back toward neutral ready height",
                "Right arm lowers full silver sword smoothly down toward 35deg neutral guard; left arm relaxes",
                "Boots settle smoothly back into neutral Cell 1 spacing",
                "Scarf & ponytail relax gently",
                "FADING VFX: Only 2 tiny fading golden star motes dissipating cleanly"),
            _fb(14, "F14 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 15 — calm neutral ready posture",
                "Full silver sword held at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 neutral stance",
                "Scarf & ponytail 95% matching Cell 1"),
            _fb(15, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
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
    is_loco = anim_spec["id"] in ("walk", "run")

    if is_combat:
        pal_rule = (
            f"STRICTLY LOCK character body colors to Image 1 ({', '.join(palette_hex[:16])}), "
            "while rendering PURPOSEFUL, MULTI-LAYERED 16-bit arcade pixel-art VFX gradients (pure white core -> ice cyan -> electric azure -> sapphire; "
            "pure white -> pastel pink -> hot magenta -> arcane violet; pure white -> bright starlight gold -> blazing flame orange -> crimson; plus crisp warm dust puffs)!"
            if palette_hex
            else "STRICTLY LOCK all character colors identically to Reference Image 1."
        )
        vfx_boost = (
            "- PURPOSEFUL PHYSICS-DRIVEN VFX MANDATE: Every VFX element MUST obey the exact physical origin, directional trajectory, "
            "and combat phase specified per frame below (Startup telegraph on blade/boots -> Active slash wave following exact sword swing arc "
            "across the open right two-thirds -> Recovery dissipating ribbons & backward braking dust)! "
            "NEVER invent random meaningless glow blobs detached from the weapon/feet, and NEVER draw ugly black outlines around glowing energy VFX!"
        )
    elif is_loco:
        pal_rule = (
            f"STRICTLY LOCK ALL pixels exclusively to Reference Image 1's character palette ({', '.join(palette_hex[:16])}). "
            "ABSOLUTE ZERO VFX: NO magic waves, NO glowing slashes, NO sparkles, NO speed lines, NO dust clouds, NO floor cast shadows — ONLY the clean character sprite on 100% pure transparent background!"
            if palette_hex
            else "STRICTLY LOCK all colors identically to Reference Image 1. ZERO VFX, ZERO dust, ZERO shadows!"
        )
        vfx_boost = (
            "- CRITICAL ANATOMICAL GAIT & LEFT/RIGHT LEG ALTERNATION RULE (FOLLOW REFERENCE IMAGE 2 SKELETON EXACTLY!):\n"
            "  * Reference Image 2 draws a color-coded kinematic leg skeleton in every cell: BRIGHT YELLOW = NEAR (foreground/Right) leg (draw with brighter warm brown boot), CYAN = FAR (background/Left) leg (draw with darker shadow-brown boot partially behind near leg)!\n"
            "  * A foot landing in FRONT (F1 / F5) MUST stay planted and SLIDE BACKWARD underneath her body (F2 -> F3 -> F4 / F6 -> F7 -> F8) while the OTHER leg lifts from behind, crosses vertically through center (F3 / F7), and swings forward to land! NEVER march in place!\n"
            "  * Maintain natural opposite arm-leg counter-swing and full-length gleaming silver sword in EVERY SINGLE CELL.\n"
            "  * PURE CLEAN LOCOMOTION ONLY: Draw ZERO VFX, ZERO glowing arcs, ZERO sparkles, ZERO ground shadows, ZERO dust clouds!"
        )
    else:
        pal_rule = (
            f"STRICTLY LOCK ALL pixels exclusively to Reference Image 1's character palette ({', '.join(palette_hex[:16])}). "
            "ABSOLUTE ZERO VFX: NO magic waves, NO sparkles, NO dust clouds, NO floor shadows!"
            if palette_hex
            else "STRICTLY LOCK all colors identically to Reference Image 1. ZERO VFX, ZERO shadows!"
        )
        vfx_boost = "- Keep clean crisp silhouette with full-length gleaming silver sword intact in EVERY SINGLE CELL. ZERO VFX, ZERO shadows."

    entries = anim_spec.get("frame_choreography") or anim_spec.get("frame_beats", [])
    choreo_lines = [f"- {format_choreography_line(e)}" for e in entries]

    return "\n".join([
        f"EXACT {cols} columns by {rows} rows ({total} frames total, reading strictly left-to-right, top-to-bottom from Cell 1 to Cell {total}) "
        "CLOSED-LOOP 16-bit CHUNKY LOW-RES PIXEL ART SINGLE-ACTION SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, orange ponytail, red scarf, teal tunic, brown boots, FULL-LENGTH silver sword (NEVER shrink or omit the sword!), and crisp 1-pixel dark outline on the character in EVERY SINGLE CELL.",
        f"Reference Image 2 is the EXACT {cols}x{rows} grid & anatomical composition guide showing cell order (1 -> {total}), character anchor axis, and pose/skeleton cues — DO NOT draw any grid lines, boxes, stick-figures, numbers, or guide tints in the final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {anim_spec.get('view_prompt', 'classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell')}.",
        "CRITICAL CLOSED-LOOP, ANATOMY & RENDERING RULES:",
        f"- Cell 1 (START) and Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL poses matching Cell 1!",
        f"- Cell {active} (immediately before Cell {total}) MUST smoothly bridge into Cell {total} (= Cell 1), guaranteeing ZERO loop jump when Cell {total} is later removed!",
        "- Keep the character's body anchored at the EXACT SAME horizontal axis and EXACT SAME chunky chibi height (~34 logical pixels tall) in EVERY cell — NEVER shrink the character to make room for VFX!",
        vfx_boost,
        f"STRICT FRAME-BY-FRAME 5-DIMENSION CHOREOGRAPHY (FOLLOW EVERY TORSO / ARM / LEG / SECONDARY / VFX INSTRUCTION LITERALLY!):",
        *choreo_lines,
        f"- Color lock: {pal_rule}",
        f"- Style lock: {style['prompt']}.",
    ])
