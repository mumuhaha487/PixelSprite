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
        "name": "普攻一式·拔剑横斩 (8帧)",
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
        "frame_durations_ms": [90, 185, 55, 225, 85, 80, 85, 90],
        "hold_tags": {2: "回拉蓄力", 4: "横斩命中 HITSTOP"},
        "combat": {
            "startup_frames": [1, 2],
            "active_frames": {
                3: {"hitId": 1, "damage": 16, "hitstopMs": 60,  "knockback": [3.5, -0.5], "kind": "melee_arc", "hitbox_mode": "forward_vfx", "label": "挥剑起效 HIT#1"},
                4: {"hitId": 1, "damage": 24, "hitstopMs": 140, "knockback": [6.5, -1.5], "kind": "melee_arc", "hitbox_mode": "forward_vfx", "label": "烈风横斩 MAX"},
            },
            "recovery_frames": [5, 6, 7, 8],
        },
        "vfx_hint": "steel_horizontal_slash",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral upright stance matching Reference Image 1 anchored in LEFT THIRD of cell",
                "Right hand grips gleaming full silver sword at 35deg forward-up; left arm balanced at side",
                "Both boots planted cleanly shoulder-width apart on ground baseline",
                "Red scarf gently flowing left; ponytail calm"),
            _fb(2, "F2 STARTUP BACK-SWING WIND-UP HOLD",
                "Torso twists firmly CLOCKWISE back-left, leaning slightly back (-2px coil) with fierce focused eyes locked right",
                "CLEAR BACK-SWING POSE: Right arm pulls full silver sword ALL THE WAY BEHIND HER HEAD / LEFT SHOULDER ready to unleash a wide horizontal cut! Left arm extends forward pointing at target for balance",
                "Rear left knee bends deeply loading spring push-off force; front right boot braces heel down",
                "Ponytail & red scarf swing back-left with body wind-up",
                "TELEGRAPH VFX: Sharp compact white-cyan 4-point steel glint flashing right on the pulled-back sword tip (clean, readable telegraph — NO random floor circle!)"),
            _fb(3, "F3 ACTIVE HIT#1 — MID-SWING HORIZONTAL CLEAVE",
                "Explosive torso UNCOIL snapping shoulders violently counter-clockwise forward-right into forward lunge",
                "Right arm whips gleaming silver sword horizontally halfway through the swing plane cutting cleanly left-to-right at chest height; left arm pulls sharply behind ribs",
                "Front right boot lunges boldly forward planting hard; rear left leg drives straight back pushing off toe",
                "Scarf & ponytail whip sharply backward-left from rapid forward burst",
                "ACTIVE SWING SMEAR VFX: Crisp horizontal white-core + electric-cyan curved motion-smear crescent tracing the EXACT path from her shoulder to her mid-swing sword edge + small white dust puff kicking BACKWARD off her pushing rear boot!"),
            _fb(4, "F4 ACTIVE HIT#1 CLIMAX HITSTOP — FULL FOLLOW-THROUGH",
                "Peak heroic forward lunge, chest fully opened right in complete swing follow-through",
                "Right arm swept ALL THE WAY ACROSS forward-low holding silver sword fully extended right; left arm flung back for dynamic balance",
                "Wide heroic power lunge — front right knee bent deeply braking forward momentum, rear left leg braced straight back",
                "Red scarf & ponytail stream straight horizontally left",
                "ACTIVE HITBOX CLIMAX VFX: Bold, razor-sharp HORIZONTAL-CRESCENT cyan-white-azure gale-blade wave sweeping forward cleanly along the EXACT horizontal plane of her sword follow-through across the right half (matching her horizontal cleave — NOT a vertical wall!) + low skimming wind streak & rear boot dust"),
            _fb(5, "F5 RECOVERY FOLLOW-THROUGH DISSIPATE",
                "Momentum settling, weight beginning to shift slightly back off front knee",
                "Right arm lowers silver sword gently at end of follow-through; left hand swings forward toward guard",
                "Front right boot planted braking; rear left boot begins drawing slightly closer",
                "Scarf drops softly slowing down; ponytail settles",
                "DISSIPATION VFX: The horizontal cyan gale-blade breaks into 2-3 thin detached fading azure wind ribbons drifting right + settling ground dust wisps (signals active Hitbox ended!)"),
            _fb(6, "F6 RECOVERY RECOIL TO GUARD",
                "Torso rises smoothly upright back to neutral center height",
                "Right wrist smoothly rotates and lifts full silver sword upward toward neutral 35deg guard",
                "Feet step smoothly back into balanced shoulder-width neutral stance on ground baseline",
                "Scarf ripples calmly back toward idle curve; ponytail settles",
                "NONE — pure clean recovery frame"),
            _fb(7, "F7 RECOVERY GUARD SETTLE",
                "Nearly back to Cell 1 upright posture, breathing steady",
                "Right hand brings full silver sword cleanly into neutral ready guard",
                "Both boots planted cleanly in neutral Cell 1 spacing",
                "Scarf & ponytail calm"),
            _fb(8, "F8 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 9 — neutral upright ready posture",
                "Full silver sword held steady at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 stance",
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
        "name": "R·居合瞬步三连破空斩 (11帧)",
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
        "frame_durations_ms": [90, 185, 55, 65, 65, 70, 70, 260, 165, 85, 90],
        "hold_tags": {2: "居合蓄力", 8: "三斩引爆 HITSTOP", 9: "急停收刀"},
        "combat": {
            "startup_frames": [1, 2, 3],
            "active_frames": {
                4: {"hitId": 1, "damage": 16, "hitstopMs": 50,  "knockback": [2.5, -2.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "一斩·上挑破空"},
                5: {"hitId": 2, "damage": 18, "hitstopMs": 55,  "knockback": [2.5,  1.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "二斩·重劈震地"},
                6: {"hitId": 3, "damage": 22, "hitstopMs": 60,  "knockback": [5.5, -0.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "三斩·贯通突刺"},
                7: {"hitId": 4, "damage": 18, "hitstopMs": 55,  "knockback": [2.0, -1.0], "kind": "scar_ignite", "hitbox_mode": "forward_vfx", "label": "收刀·三痕点亮"},
                8: {"hitId": 5, "damage": 40, "hitstopMs": 185, "knockback": [9.5, -3.0], "kind": "aoe_nova",    "hitbox_mode": "forward_vfx", "label": "三连斩痕爆裂 MAX"},
            },
            "recovery_frames": [9, 10, 11],
        },
        "vfx_hint": "iaido_three_cut_detonate",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral upright ready stance anchored in LEFT THIRD of cell",
                "Right hand grips full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted shoulder-width on baseline",
                "Scarf gently flowing behind-left"),
            _fb(2, "F2 STARTUP IAIDO DRAW CROUCH HOLD",
                "Deep low sprinter iaido crouch (-3px), shoulders coiled tightly forward-low, razor-sharp focus right",
                "CLASSIC IAIDO GRIP: Right hand pulls silver sword LOW & BACK beside left hip horizontally ready for lightning draw; left hand steadies hip",
                "Both knees deeply bent in tight sprinter block crouch, rear heel raised loading explosive forward burst",
                "Ponytail pressed low behind; scarf tucked close",
                "IAIDO TELEGRAPH VFX (UNIFIED CYAN-WHITE STEEL PALETTE ONLY!): Sharp white-cyan steel draw-glint flashing directly at the sword hilt + compact white air-compression ring kicking up behind her coiled rear heel (ZERO random rainbow circles!)"),
            _fb(3, "F3 STARTUP HIGH-SPEED BLINK DASH",
                "Steep 28deg near-horizontal forward dash lean darting forward at blinding speed",
                "Right sword-arm tucked tight back-low primed to whip upward on next frame; left arm swept back",
                "Front right knee drives hard forward; rear left leg extends straight back pushing off ground",
                "Scarf & ponytail whipped razor-straight horizontally behind",
                "DASH VELOCITY VFX (CYAN-WHITE ONLY!): Single crisp translucent electric-cyan pixel AFTERIMAGE SILHOUETTE lagging directly behind her torso + 3 razor-sharp horizontal white-cyan wind lines + backward-kicked white boot dust!"),
            _fb(4, "F4 ACTIVE HIT#1 — CUT 1: BOTTOM-TO-TOP UPPERCUT SLASH",
                "Torso springs UPWARD tall and open from low dash into dramatic rising slash!",
                "UNMISTAKABLE OVERHEAD POSE: Right arm whips gleaming silver sword ALL THE WAY UP HIGH ABOVE HER HEAD (finishing bottom-left to top-right cut!); left arm drives downward-back for torque",
                "Front right foot pivots solidly forward; rear heel lifts driving upward extension",
                "Scarf & ponytail whip sharply DOWNWARD-LEFT opposite to her rising uppercut",
                "CUT 1 DIRECTIONAL VFX (UNIFIED ELECTRIC-CYAN & WHITE): Clean, fierce UPWARD-SWEEPING white-core -> electric-cyan -> deep azure crescent slash curve extending directly from waist height all the way up to her overhead sword tip!"),
            _fb(5, "F5 ACTIVE HIT#2 — CUT 2: OVERHEAD-TO-FLOOR HEAVY CHOP",
                "Torso slams VIOLENTLY DOWNWARD leaning low forward into devastating vertical chop!",
                "UNMISTAKABLE FLOOR-CHOP POSE: Right arm swings silver sword ALL THE WAY DOWNWARD pointing straight toward the ground in front of her boots; left arm lifts high behind back",
                "Deep low power lunge — front knee heavily bent bearing slam, rear leg stretched firmly back",
                "Scarf & ponytail whip HIGH UPWARD-LEFT opposite to the downward chop!",
                "CUT 2 DIRECTIONAL VFX (UNIFIED CYAN-WHITE): Clean, fierce DOWNWARD-SWEEPING white-core -> electric-cyan -> sapphire crescent arc tracing directly from overhead down to the ground in front of her + crisp white ground-impact dust & spark burst where the blade slashes low!"),
            _fb(6, "F6 ACTIVE HIT#3 — CUT 3: FULL-EXTENSION HORIZONTAL PIERCE THRUST",
                "Body stretches FULLY HORIZONTAL FORWARD in a classic fencer's lunging pierce!",
                "UNMISTAKABLE LANCE-THRUST POSE: Right arm thrusts gleaming silver sword STRAIGHT HORIZONTALLY FORWARD at full arm reach; left arm flung straight back for counter-balance",
                "Maximum horizontal fencer lunge — front knee deeply bent forward, back leg locked straight out behind",
                "Scarf & ponytail blown razor-straight back-left along the thrust vector",
                "CUT 3 DIRECTIONAL VFX (UNIFIED CYAN-WHITE): Piercing horizontal white-hot & electric-cyan SWORD-THRUST BEAM shooting straight forward from her blade tip + two crisp concentric white-cyan sonic air-break rings wrapping the beam!"),
            _fb(7, "F7 ACTIVE HIT#4 — REVERSE-GRIP HIP PULL-BACK (3 SLASH SCARS IGNITE!)",
                "Cool composed stance snapping torso slightly back upright, head slightly lowered with fierce confident eyes watching the 3 scars ahead",
                "DISTINCT SHEATH-SNAP POSE: Right hand snaps silver sword cleanly BACK to hip pointing down-back (sheathing/braking gesture!) while the 3 cuts she just made remain suspended in the air ahead!",
                "Balanced athletic stance planting front boot firmly to stop forward lunge",
                "Scarf flares forward slightly then trails back as momentum snaps to a halt",
                "DELAYED SCAR IGNITION VFX (UNIFIED CYAN-WHITE-GOLD): Directly in front of her in mid-air across the right half, the EXACT 3 intersecting razor-thin slash scars from Cuts 1+2+3 (one upward diagonal + one downward diagonal + one horizontal line!) IGNITE simultaneously as blinding pure-white & electric-cyan glowing energy lines with sharp gold glint at their intersection!"),
            _fb(8, "F8 ACTIVE HIT#5 CLIMAX HITSTOP — 3-CUT SCAR DETONATION",
                "Locked heroic low hip-sheath finish pose holding rock-steady as the slash scars shatter in front of her!",
                "Right hand holds gleaming sword steadily tucked at hip pointing back-low; left hand steadies waist (classic anime 'already cut you' pose!)",
                "Rock-solid braced stance planted on floor withstanding blast wind",
                "Scarf & ponytail blasted violently straight backward-left by the shockwave wind from the right!",
                "SCAR DETONATION CLIMAX VFX (UNIFIED ELECTRIC-CYAN, ICE-WHITE & AZURE — ZERO RANDOM FIREBALLS OR PURPLE DISCO!): The 3 intersecting mid-air slash scars DETONATE violently across the right two-thirds into razor-sharp radial white-cyan blade shockwaves, slicing wind-arc ribbons, crisp diamond steel sparks, and a rolling white ground shockwave dust wave sweeping outward!"),
            _fb(9, "F9 RECOVERY STYLISH SKID BRAKE",
                "Cool low crouched recoil leaning slightly back-left absorbing blast wind",
                "Right hand holds silver sword low horizontally stabilizing crouch; left hand near knee",
                "Both boots angled forward braking cleanly on floor",
                "Scarf & ponytail settling forward gently as shockwave wind subsides",
                "BRAKING VFX: Crisp white-tan ground SKID DUST puffs under her front boot heel + 4 thin fading azure wind slivers dissipating right (signals active hitbox over!)"),
            _fb(10, "F10 RECOVERY RISE TO GUARD",
                "Rising smoothly back upright to neutral center height",
                "Right arm smoothly lifts full silver sword upward into 35deg neutral ready guard",
                "Feet step calmly back into shoulder-width neutral stance",
                "Scarf & ponytail lift back into calm idle flow",
                "NONE — pure clean recovery frame"),
            _fb(11, "F11 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 12 — neutral upright ready posture",
                "Full silver sword held steady at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 95% identical to Cell 1"),
            _fb(12, "GHOST LOOP = F1",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    "ult_starfall_slash": {
        "id": "ult_starfall_slash",
        "name": "F·星炎流星坠地斩 (14帧奥义)",
        "key": "ULT F",
        "active_frames": 14,
        "closed_loop": True,
        "grid": [5, 3],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 26.0,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.29,
        "guide_sprite_h_ratio": 0.37,
        "timing_mode": "hitstop",
        "frame_durations_ms": [90, 85, 190, 65, 160, 60, 70, 275, 145, 85, 85, 205, 85, 90],
        "hold_tags": {3: "燃剑蓄力", 5: "高空举剑定格", 8: "贯地星炎爆发 HITSTOP", 12: "收剑胜利定格"},
        "combat": {
            "startup_frames": [1, 2, 3, 4, 5],
            "active_frames": {
                6: {"hitId": 1, "damage": 24, "hitstopMs": 60,  "knockback": [4.0,  3.5], "kind": "dive_slash",   "hitbox_mode": "forward_vfx", "label": "凌空陨落斜斩 HIT#1"},
                7: {"hitId": 2, "damage": 32, "hitstopMs": 80,  "knockback": [5.0, -3.0], "kind": "ground_slam",  "hitbox_mode": "forward_vfx", "label": "剑尖贯地重击 HIT#2"},
                8: {"hitId": 3, "damage": 65, "hitstopMs": 220, "knockback": [12.0,-5.5], "kind": "aoe_nova",     "hitbox_mode": "forward_vfx", "label": "星炎冲击波大爆发 MAX"},
                9: {"hitId": 4, "damage": 26, "hitstopMs": 70,  "knockback": [7.5, -4.0], "kind": "flame_surge",  "hitbox_mode": "forward_vfx", "label": "拔剑烈焰追击 HIT#4"},
            },
            "recovery_frames": [10, 11, 12, 13, 14],
        },
        "vfx_hint": "solar_meteor_ground_slam",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Neutral upright stance matching Reference Image 1 anchored in left third",
                "Right hand grips full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted squarely on ground baseline",
                "Scarf gently flowing behind-left"),
            _fb(2, "F2 STARTUP DEEP SPRING CROUCH",
                "Dropping very low (-3px) into tight athletic spring-jump crouch, head tucked forward determined",
                "TWO-HANDED GRIP: Both hands clasp sword hilt tightly in front of chest pointing blade upright-right",
                "Both knees deeply bent loading explosive vertical jump energy onto planted boots",
                "Ponytail dips behind shoulders; scarf curls down",
                "EARLY TELEGRAPH VFX (UNIFIED SOLAR-GOLD & FLAME ONLY!): Tiny bright golden ember sparks flickering strictly along the raised silver sword blade"),
            _fb(3, "F3 STARTUP BLADE IGNITION HOLD",
                "Deepest coiled takeoff crouch (-3px) eyes fiercely glowing looking up-right",
                "Both hands hold blazing golden-white sword angled forward-up charging solar fire strictly onto the blade",
                "Both boots planted firmly & deeply bent at center of a compact ground pressure ring",
                "Scarf & ponytail lifted gently upward by rising heat updraft",
                "CHARGE TELEGRAPH VFX (UNIFIED SOLAR-GOLD & FLAME): Blazing golden-white star-flame wrapping cleanly ONLY around the sword blade itself + compact golden-white air compression ring flat around her boots (clear physical buildup — NO random floating purple noodles!)"),
            _fb(4, "F4 STARTUP EXPLOSIVE VERTICAL LEAP",
                "Powerful athletic upward leap launching HIGH INTO THE AIR (+16px airborne!) chest rising skyward",
                "Both hands drive the blazing golden sword straight UPWARD leading her jump!",
                "Front right knee tucked dynamically high; rear left leg extends straight down from takeoff push — BOTH boots clearly high off ground!",
                "Red scarf & ponytail trail straight DOWNWARD-LEFT against her upward jump velocity!",
                "TAKEOFF VFX: Crisp white-tan ground jump-dust ring erupting flat on the floor directly beneath her takeoff spot + short trailing golden flame streak from her rising sword blade (NOT a rocket flame shooting out of her boots!)"),
            _fb(5, "F5 STARTUP AERIAL APEX — TWO-HANDED OVERHEAD METEOR RAISE HOLD",
                "High airborne apex (+22px off ground!), spine arched boldly BACKWARD like a drawn bow poised to strike down!",
                "UNMISTAKABLE OVERHEAD RAISE: BOTH HANDS hold the blazing golden-white sword HIGH UP BEHIND HER HEAD pointing up-back, gathering massive solar flame into a crisp radiant golden blade-aura!",
                "Dynamic mid-air bent-knee poise — both boots high in the air cleanly above floor",
                "Scarf & ponytail fanned dramatically out behind-left at zero-gravity jump peak",
                "OVERHEAD METEOR CHARGE VFX (UNIFIED SOLAR-GOLD & FLAME): Blazing golden-white solar flame aura + bright 4-point star flare concentrating strictly around her raised overhead sword blade (100% unmistakable telegraph: she is about to bring this meteor blade crashing down!)"),
            _fb(6, "F6 ACTIVE HIT#1 — AERIAL METEOR DIVE-SLASH",
                "Plunging aggressively FORWARD-DOWNWARD (+14px airborne -> diving toward floor!), torso snapping forward!",
                "UNMISTAKABLE DIVE-SLASH: Both hands swing the blazing golden sword violently OVERHEAD-TO-FORWARD-DOWNWARD in a giant descending meteor cleave!",
                "Legs angled trailing up-left behind her rapid forward-downward plunge!",
                "Scarf & ponytail stream UPWARD-LEFT opposite to her downward dive!",
                "HIT#1 METEOR DIVE VFX (UNIFIED SOLAR-GOLD, FLAME-ORANGE & CRIMSON): HUGE blazing golden-white -> flame-orange -> crimson curving meteor slash crescent sweeping from high overhead diagonally DOWN-RIGHT toward the floor directly following her plunging sword arc!"),
            _fb(7, "F7 ACTIVE HIT#2 — SWORD-STABBED-INTO-GROUND METEOR SLAM!",
                "SLAMMED SQUARELY ONTO THE GROUND (-3px deep heroic superhero impact crouch!), head lowered fiercely!",
                "UNMISTAKABLE GROUND-STAB POSE: Both hands drive the gleaming silver sword POINT-FIRST STRAIGHT DOWN INTO THE GROUND directly in front of her right boot!!",
                "Deep heroic 1-knee ground-slam stance — both boots firmly planted back on the ground baseline absorbing massive downward impact!",
                "Ponytail & scarf whipped violently upward then outward from impact shock!",
                "HIT#2 GROUND-SLAM VFX (UNIFIED SOLAR-GOLD & FLAME): Blinding pure-white & golden vertical impact flash + radial cracking fire-wave & billowing ground shockwave dust erupting directly from the EXACT point where her sword blade pierced the floor!"),
            _fb(8, "F8 ACTIVE HIT#3 CLIMAX HITSTOP — SOLAR FLAME SHOCKWAVE ERUPTION",
                "Locked firmly in the dramatic low sword-planted-in-ground pose bracing against the roaring blast ahead!",
                "Right hand grips the hilt of the sword planted upright-angled in the ground in front of her; left hand braces near knee",
                "Deep braced heroic crouch planted solidly on ground baseline",
                "Red scarf & orange ponytail blasted furiously straight BACKWARD-LEFT by the roaring explosion right in front of her!",
                "HIT#3 CLIMAX ERUPTION VFX (UNIFIED SOLAR-GOLD, BLAZING ORANGE & FIERY CRIMSON — ZERO PURPLE/PINK DISCO!): MASSIVE forward-surging wave of blazing golden-white & flame-orange solar eruption pillars, concentric ground-ripping flame shockwave arcs, and billowing rolling dust & flying golden embers erupting directly from her planted sword across the ENTIRE right two-thirds!"),
            _fb(9, "F9 ACTIVE HIT#4 — YANKING SWORD UP OUT OF FLOOR (RISING FLAME SURGE)",
                "Torso surges upward-right pulling powerfully out of ground-slam crouch!",
                "UNMISTAKABLE SWORD YANK-UP: Right arm rips the gleaming silver sword violently UPWARD-RIGHT out of the floor in a fierce rising follow-through sweep; left arm pulls back",
                "Front right knee straightening from lunge; rear left boot pushing firmly on floor",
                "Scarf whips cleanly down-left as she rises",
                "HIT#4 FOLLOW-THROUGH FLAME VFX (UNIFIED SOLAR-GOLD & FLAME): A sweeping upward curtain of blazing golden flame-arcs, rising fire-sparks, and soaring embers surging upward-right off her yanked-up blade across the right half!"),
            _fb(10, "F10 RECOVERY SHAKE OFF EMBERS",
                "Standing upright smoothly, breathing steady, relaxing combat tension",
                "Right arm swings gleaming silver sword casually outward-right shaking off final fire embers; left arm relaxed",
                "Feet stepping smoothly back into balanced standing stance on ground baseline",
                "Scarf & ponytail swinging gently down into calm motion",
                "DISSIPATION VFX: Flame pillars completely gone — only small cooling orange-gold embers & faint warm dust wisps drifting upward-right (clearly signals active Hitbox ended!)"),
            _fb(11, "F11 RECOVERY CLEAN BLADE RISE",
                "Upright poised standing stance, chin lifting proudly",
                "Right wrist smoothly rotates clean silver sword upright toward victory flourish",
                "Both boots planted cleanly on baseline",
                "Scarf billowing gently left; ponytail bouncing softly",
                "FADING VFX: 2 tiny fading golden embers dissipating cleanly"),
            _fb(12, "F12 RECOVERY HEROIC VICTORY FLOURISH HOLD",
                "Standing tall & proud upright (+1px chest proud!), warm triumphant smile",
                "Right arm holds gleaming full silver sword proudly angled forward-up in classic JRPG victory flourish; left hand on hip",
                "Confident wide heroic standing stance cleanly grounded on baseline",
                "Red scarf billows majestically left; ponytail buoyant",
                "VICTORY PUNCTUATION VFX: 2 crisp clean golden-white 4-point blade-glint stars twinkling right on the clean silver sword blade"),
            _fb(13, "F13 RECOVERY LOWER TO GUARD",
                "Relaxing smoothly back to neutral Cell 1 height",
                "Right arm lowers full silver sword smoothly down to 35deg neutral guard; left arm relaxes",
                "Boots settle smoothly back into neutral Cell 1 spacing",
                "Scarf & ponytail calm",
                "NONE — pure clean recovery frame"),
            _fb(14, "F14 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 & Cell 15 — neutral upright ready posture",
                "Full silver sword held at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 stance",
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

    vfx_hint = anim_spec.get("vfx_hint", "")
    if is_combat:
        if vfx_hint in ("steel_horizontal_slash", "iaido_three_cut_detonate"):
            vfx_pal_desc = (
                "UNIFIED STEEL-WIND VFX PALETTE ONLY: pure white hot core -> ice cyan -> electric cyan -> azure -> deep sapphire + crisp white-tan ground dust "
                "(STRICTLY NO random orange fireballs, NO neon pink/purple disco rainbows!)"
            )
        elif vfx_hint == "solar_meteor_ground_slam":
            vfx_pal_desc = (
                "UNIFIED SOLAR-FLAME METEOR VFX PALETTE ONLY: pure white star core -> pale lemon gold -> bright solar gold -> blazing flame orange -> fiery crimson + crisp warm ground shockwave dust "
                "(STRICTLY NO random cyan/pink/purple disco rainbows!)"
            )
        else:
            vfx_pal_desc = "purposeful multi-layered 16-bit arcade VFX matching the exact weapon/element theme specified per frame"
        pal_rule = (
            f"STRICTLY LOCK character body colors to Image 1 ({', '.join(palette_hex[:16])}), while using {vfx_pal_desc}!"
            if palette_hex
            else f"STRICTLY LOCK all character colors identically to Reference Image 1, using {vfx_pal_desc}!"
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
