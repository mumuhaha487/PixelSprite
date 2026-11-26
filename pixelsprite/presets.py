"""Style presets & v2.5 6-Dimension Skeletal-Continuity Choreography Specs (Sub-Action Anticipation Law, Multi-Part Chained 18+ Frame Combos, Purposeful VFX & Auto Hitboxes)."""

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
    transition_from_prev: str,
    torso: str,
    arms_weapon: str,
    legs_feet: str,
    secondary: str,
    vfx_meaning: str = "NONE — pure clean character sprite, zero VFX, zero dust, zero floor shadow",
) -> dict[str, Any]:
    """
    6-Dimension Skeletal-Continuity Per-Frame Choreography Builder (v2.5):
      1. transition_from_prev : EXACT bone-to-bone kinematic bridge from F[i-1] (prevents teleporting poses!)
      2. torso                : Spine lean, hip height/airborne lift, shoulder twist
      3. arms_weapon          : Exact position & angle of BOTH hands + weapon trajectory
      4. legs_feet            : Exact separate position of Near/Right leg & Far/Left leg
      5. secondary_motion     : Ponytail, scarf & hem drag opposite to acceleration
      6. vfx_meaning          : Physical origin + directional trajectory + combat purpose (or strictly NONE)
    """
    return {
        "cell": cell,
        "role": role,
        "transition_from_prev": transition_from_prev,
        "torso": torso,
        "arms_weapon": arms_weapon,
        "legs_feet": legs_feet,
        "secondary_motion": secondary,
        "vfx_meaning": vfx_meaning,
    }


def format_choreography_line(entry: dict[str, Any] | str, cell_override: int | None = None) -> str:
    if isinstance(entry, str):
        return entry
    cnum = cell_override if cell_override is not None else entry["cell"]
    tr = entry.get("transition_from_prev", "")
    tr_str = f"[BONE LINK] {tr} | " if tr else ""
    return (
        f"Cell {cnum} ({entry['role']}): "
        f"{tr_str}"
        f"[TORSO] {entry['torso']} | "
        f"[ARMS & WEAPON] {entry['arms_weapon']} | "
        f"[LEGS & FEET] {entry['legs_feet']} | "
        f"[SECONDARY] {entry['secondary_motion']} | "
        f"[VFX & PURPOSE] {entry['vfx_meaning']}"
    )


def validate_choreography(anim_spec: dict[str, Any]) -> dict[str, Any]:
    """
    Strict v2.5 Choreography & Sub-Action Anticipation Validator:
      1. Enforces all 6 mandatory per-frame dimensions (transition_from_prev, torso, arms_weapon, legs_feet, secondary_motion, vfx_meaning).
      2. Enforces the SUB-ACTION ANTICIPATION LAW: two distinct attack strokes (hitId k -> hitId k+1)
         CANNOT appear back-to-back without an explicit chamber/anticipation preparation frame in between
         (unless explicitly marked `same_continuous_motion: true` for a single uninterrupted follow-through!).
    """
    n_active = int(anim_spec["active_frames"])
    closed = bool(anim_spec.get("closed_loop", True))
    expected = n_active + (1 if closed else 0)
    choreo = anim_spec.get("frame_choreography")
    issues: list[str] = []

    if not choreo:
        beats = anim_spec.get("frame_beats", [])
        issues.append("Missing structured 6-dimension `frame_choreography`! Never use vague `frame_beats` strings.")
        return {"ok": False, "structured": False, "frameCount": len(beats), "issues": issues}

    if len(choreo) != expected:
        issues.append(f"Expected {expected} choreography entries ({n_active} active + {1 if closed else 0} ghost), found {len(choreo)}.")

    req_keys = ("transition_from_prev", "torso", "arms_weapon", "legs_feet", "secondary_motion", "vfx_meaning")
    for idx, item in enumerate(choreo):
        if not isinstance(item, dict):
            issues.append(f"Cell {idx+1}: must be a structured dict with keys {req_keys}.")
            continue
        for k in req_keys:
            val = str(item.get(k, "")).strip()
            if len(val) < 10:
                issues.append(f"Cell {idx+1} `{k}` is missing or too vague ('{val}').")

    # Sub-Action Anticipation Law Check on multi-hit combat skills!
    active_map = {int(k): v for k, v in anim_spec.get("combat", {}).get("active_frames", {}).items()}
    if active_map:
        first_atk = min(active_map.keys())
        if first_atk < 2:
            issues.append("First active attack frame cannot be F1 — every attack MUST have at least 1 anticipation/startup frame!")
        for fnum in sorted(active_map.keys()):
            if (fnum - 1) in active_map:
                prev_hit = active_map[fnum - 1].get("hitId")
                cur_hit = active_map[fnum].get("hitId")
                if cur_hit != prev_hit and not active_map[fnum].get("same_continuous_motion", False):
                    issues.append(
                        f"SUB-ACTION ANTICIPATION VIOLATION: F{fnum} (HIT#{cur_hit}) immediately follows F{fnum-1} (HIT#{prev_hit}) "
                        "with ZERO chamber/preparation frame in between! Insert a prep/chamber frame (and expand total frame count / chained_parts)!"
                    )

    return {"ok": len(issues) == 0, "structured": True, "frameCount": len(choreo), "issues": issues}


# ==============================================================================
# v2.5 6-DIMENSION SKELETAL-CONTINUITY ANIMATION SPECS
#   - Short cycles / single slash : 8+1f (single 3x3 sheet)
#   - Complex multi-hit combos    : 18+1f (seamless 2-part chained 4x3 + 3x3 sheets!)
#     Every single strike inside a combo gets its OWN anticipation/chamber frame!
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
                "Loop start matching Master Anchor Reference Image 1",
                "Neutral upright alert stance, chest relaxed, gaze right",
                "Right hand grips gleaming full silver sword angled 35deg forward-up; left arm relaxed",
                "Both brown boots planted firmly shoulder-width on baseline, knees softly bent",
                "Red scarf flows gently behind-left; ponytail rests at shoulder height"),
            _fb(2, "F2 INHALE START",
                "Ribcage & shoulders lift +0.5px smoothly from F1 without sliding feet",
                "Chest begins expanding upward, shoulders squaring gently",
                "Right sword-hand lifts 1px with breath, blade stays exact full length 35deg",
                "Both boots stay 100% nailed to exact F1 ground positions",
                "Scarf tail begins lifting softly in light breeze; ponytail lifts slightly"),
            _fb(3, "F3 INHALE MID",
                "Continues smooth +0.5px upward inhale rise from F2",
                "Ribcage lifted (+1px), posture proud and alert",
                "Right sword-hand rises slightly to 38deg, full silver blade crisp",
                "Both boots fixed on baseline, knees slightly straighter",
                "Scarf billows smoothly upward-left; ponytail bobs gently higher"),
            _fb(4, "F4 PRE-APEX",
                "Smooth deceleration approaching top of breath arc from F3",
                "Approaching inhale peak (+1.5px), bright confident eyes forward",
                "Sword held poised near top of breath arc, golden crossguard crisp",
                "Both boots firmly rooted without sliding",
                "Scarf reaches high wave curve; ponytail buoyant"),
            _fb(5, "F5 BREATH APEX",
                "Soft turning point at peak inhale (+2px max) reversing into exhale",
                "Gentle inhale peak (+2px max, never stretching legs abnormally tall!)",
                "Right sword-hand holds full silver blade steady at 40deg peak",
                "Both boots planted flat on exact ground coordinates",
                "Scarf curls smoothly at top of wind wave; ponytail floating high"),
            _fb(6, "F6 EXHALE START",
                "Chest & sword begin relaxing smoothly -1px down from F5",
                "Chest lowering smoothly, shoulders relaxing into readiness",
                "Right sword-hand lowers 1px toward 37deg, full blade intact",
                "Both boots fixed on ground, knees softening slightly",
                "Scarf trails downward-left with soft lag; ponytail drops slightly"),
            _fb(7, "F7 EXHALE MID",
                "Continues smooth exhale settle from F6 toward F1",
                "Torso settles into springy ready posture, weight even",
                "Sword lowers smoothly to 35deg ready angle, left arm neutral",
                "Both boots planted firmly, knees softly bent matching F1",
                "Scarf settles into relaxed mid-wave; ponytail bounces down"),
            _fb(8, "F8 PRE-LOOP BRIDGE",
                "95% returned to F1 ready posture bridging seamlessly into F9 (=F1)",
                "Relaxed upright ready chest matching F1",
                "Full silver sword at exact 35deg Cell 1 angle",
                "Both boots planted in exact Cell 1 stance",
                "Scarf and ponytail 95% identical to Cell 1"),
            _fb(9, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
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
                "Start of stride — right heel touches ground ahead while left toe pushes off behind",
                "Slight energetic forward walk lean (5deg), neutral mid height",
                "OPPOSITE ARM-LEG SWING: Right sword-hand slightly BACK at hip holding full silver sword; left arm slightly forward",
                "YELLOW=Near-Right & CYAN=Far-Left: Bright gold-cuff NEAR Right leg extended FORWARD heel-striking; darker FAR Left leg extended BACKWARD",
                "Red scarf trails smoothly left; ponytail level"),
            _fb(2, "F2 DOWN 1 (RIGHT LEG ABSORBS)",
                "Right boot flattens onto floor absorbing body drop (-1.5px) while left heel peels off behind",
                "Body cushions DOWN (-1.5px lowest point) onto planted right leg",
                "Right sword-hand swings smoothly forward past waist; full silver blade intact",
                "NEAR Right boot plants FLAT under front torso with knee bent; darker FAR Left boot lifts OFF ground behind",
                "Ponytail dips slightly down from cushion inertia; scarf waves"),
            _fb(3, "F3 PASSING 1 (RIGHT VERTICAL SUPPORT, LEFT CROSSES CENTER)",
                "Planted right leg straightens vertically under hip as lifted left knee swings forward past center",
                "Body rises upright directly over vertical supporting leg",
                "Arms cross neutral beside torso; full silver sword held cleanly forward-right",
                "PASSING POSE: NEAR Right leg stands STRAIGHT VERTICAL planted under hip; darker FAR Left leg bends knee crossing forward through center!",
                "Scarf waves steadily; ponytail rises with vertical torso"),
            _fb(4, "F4 HIGH/PUSH 1 (RIGHT PUSHES BACK, LEFT REACHES FORWARD)",
                "Supporting right leg extends backward off toe pushing hip to +1.5px peak while left foot swings forward",
                "Body reaches walk HIGH PEAK (+1.5px)",
                "Right sword-hand swings clearly FORWARD counter to left leg reaching ahead",
                "NEAR Right leg slides BACKWARD pushing off toe; darker FAR Left leg swings HIGH & FORWARD preparing to land!",
                "Ponytail arcs up at peak; scarf streams crisply left"),
            _fb(5, "F5 CONTACT 2 (LEFT LEG FORWARD — SWAP OF F1!)",
                "Swinging left foot lands heel-first ahead while pushing right leg stretches fully behind",
                "Neutral mid height, shoulders counter-rotated opposite to F1",
                "OPPOSITE TO F1: Right sword-hand at fullest FORWARD-UP swing; left off-hand back",
                "EXACT SWAP OF F1: Darker FAR Left leg extended FORWARD heel-striking; bright gold-cuff NEAR Right leg extended BACKWARD!",
                "Scarf ripples in rhythm; ponytail level"),
            _fb(6, "F6 DOWN 2 (LEFT LEG ABSORBS — SWAP OF F2!)",
                "Planted left boot flattens absorbing -1.5px dip while right heel peels off behind",
                "Body cushions DOWN (-1.5px lowest point) onto planted left leg",
                "Right sword-hand begins swinging back toward hip; full blade intact",
                "Darker FAR Left boot plants FLAT under front torso; bright NEAR Right boot lifts OFF ground behind!",
                "Ponytail dips softly; scarf undulates"),
            _fb(7, "F7 PASSING 2 (LEFT VERTICAL SUPPORT, RIGHT CROSSES — SWAP OF F3!)",
                "Planted left leg straightens vertically under hip as bright right knee crosses forward in front",
                "Body rises upright directly over vertical left leg",
                "Arms cross neutral near waist; full silver sword clearly visible",
                "PASSING POSE (SWAP): Darker FAR Left leg stands STRAIGHT VERTICAL under hip; bright NEAR Right leg bends knee crossing forward IN FRONT!",
                "Scarf waves cleanly; ponytail lifts"),
            _fb(8, "F8 HIGH/PUSH 2 (LEFT PUSHES BACK, RIGHT REACHES INTO F1 — SWAP OF F4!)",
                "Supporting left leg pushes backward off toe as bright right foot reaches forward 1 step before F9 (=F1)",
                "Body at walk HIGH PEAK (+1.5px) gliding into F1 right-heel strike",
                "Right sword-hand swings gently back toward F1 ready position",
                "Darker FAR Left leg slides BACK pushing off toe; bright NEAR Right leg swings HIGH & FORWARD into Cell 9 (=F1)!",
                "Ponytail bounces at crest; scarf trailing left"),
            _fb(9, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — slight forward walk lean",
                "100% IDENTICAL TO CELL 1 — Right sword-hand slightly back at hip",
                "100% IDENTICAL TO CELL 1 — Bright NEAR Right forward heel-strike, darker FAR Left back!",
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
                "Start of sprint stride — near right foot strikes forward while far left leg trails back",
                "Dynamic 15deg forward sprint lean, eyes fiercely ahead",
                "Right sword-hand pulled back near hip holding full silver sword; left elbow pumping forward",
                "YELLOW=Near-Right & CYAN=Far-Left: Bright NEAR Right boot strikes FORWARD; darker FAR Left leg kicked back",
                "Scarf & ponytail stream straight horizontally left"),
            _fb(2, "F2 R-ABSORB",
                "Planted right knee compresses low under hip while far left knee tucks forward underneath",
                "Torso compresses low (-1.5px) coiled directly over right leg",
                "Right sword-hand begins driving forward; full silver sword intact",
                "NEAR Right leg planted deeply bent under torso; darker FAR Left knee tucked pulling forward",
                "Ponytail whips tightly behind head; scarf taut horizontal"),
            _fb(3, "F3 R-PUSHOFF",
                "Right leg snaps straight back off toe launching body forward as far left knee drives high ahead",
                "Torso surges upward-forward powered by explosive push-off",
                "Right sword-hand drives forward across waist; left arm back",
                "NEAR Right leg extends FAR BACK off toe; darker FAR Left knee drives HIGH forward-up!",
                "Scarf snaps high-left; ponytail lifts"),
            _fb(4, "F4 AIRBORNE FLIGHT 1",
                "Push-off launches BOTH boots +2px off ground in wide mid-air stride toward F5 landing",
                "FULL SPRINT SUSPENSION — entire body floats +2px off ground!",
                "Right sword-hand swings to peak forward reach, full blade crisp",
                "BOTH BOOTS CLEARLY AIRBORNE! Darker FAR Left leg stretches far forward; bright NEAR Right leg kicks high behind!",
                "Scarf & ponytail floating straight back"),
            _fb(5, "F5 L-STRIKE (EXACT SWAP OF F1!)",
                "Far left boot touches down forward from F4 flight while bright right leg extends back",
                "Forward sprint lean, landing firmly onto opposite leg",
                "Right sword-hand forward-up, left arm pulled back (opposite of F1!)",
                "EXACT SWAP OF F1: Darker FAR Left boot strikes FORWARD; bright NEAR Right leg stretched far back!",
                "Scarf streaming horizontally left; ponytail taut"),
            _fb(6, "F6 L-ABSORB (SWAP OF F2!)",
                "Planted left knee compresses low under torso while bright right knee tucks forward in foreground",
                "Torso compresses low (-1.5px) coiled over planted left leg",
                "Right sword-hand pulls smoothly back toward hip; full blade steady",
                "Darker FAR Left leg bent directly under torso; bright NEAR Right knee tucked pulling forward in foreground!",
                "Ponytail dips behind; scarf whips taut"),
            _fb(7, "F7 L-PUSHOFF (SWAP OF F3!)",
                "Left leg snaps straight back off toe launching body forward as bright right knee drives high ahead",
                "Torso explodes forward-up off left toe push",
                "Right sword-hand pulls back behind waist coiling for F1; left elbow forward",
                "Darker FAR Left leg pushes FAR BACK off toe; bright NEAR Right knee drives HIGH forward in foreground!",
                "Scarf billows horizontally; ponytail kicks up"),
            _fb(8, "F8 AIRBORNE FLIGHT 2 (SWAP OF F4!)",
                "Push-off launches BOTH boots +2px off ground reaching right boot smoothly into F9 (=F1) strike",
                "FULL SPRINT SUSPENSION (+2px airborne!) gliding into F9 (=F1)!",
                "Right sword-hand positioned nearly matching Cell 1, blade gleaming",
                "BOTH BOOTS AIRBORNE! Bright NEAR Right boot reaches far forward 1 step before Cell 9 (=F1); darker FAR Left kicked back!",
                "Scarf & ponytail streaming left"),
            _fb(9, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — 15deg forward sprint lean",
                "100% IDENTICAL TO CELL 1 — Right sword-hand near hip, full blade",
                "100% IDENTICAL TO CELL 1 — Bright NEAR Right forward, darker FAR Left back!",
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
                "Start neutral ready stance matching Reference Image 1",
                "Neutral upright stance anchored in LEFT THIRD of cell",
                "Right hand grips gleaming full silver sword at 35deg forward-up; left arm balanced",
                "Both boots planted cleanly shoulder-width on baseline",
                "Red scarf gently flowing left; ponytail calm"),
            _fb(2, "F2 STARTUP BACK-SWING WIND-UP HOLD",
                "Shoulders twist clockwise back-left pulling right sword-arm smoothly behind head to load torque",
                "Torso twists firmly back-left (-2px coil) with fierce gaze right",
                "CLEAR BACK-SWING: Right arm pulls full silver sword ALL THE WAY BEHIND HER HEAD / LEFT SHOULDER; left arm points forward aiming at target",
                "Rear left knee bends deeply loading spring push; front right boot braces heel down",
                "Ponytail & scarf swing back-left with wind-up",
                "TELEGRAPH VFX: Crisp compact white-cyan 4-point steel glint flashing right on the pulled-back sword tip"),
            _fb(3, "F3 ACTIVE HIT#1 — MID-SWING HORIZONTAL CLEAVE",
                "Rear leg drives body forward as shoulders snap counter-clockwise whipping sword horizontally from behind head to chest-front",
                "Explosive torso UNCOIL snapping forward-right into horizontal attack lunge",
                "Right arm whips gleaming silver sword horizontally halfway through swing cutting left-to-right at chest height; left arm pulls behind ribs",
                "Front right boot lunges forward planting hard; rear left leg drives straight back off toe",
                "Scarf & ponytail whip sharply backward-left",
                "ACTIVE SWING SMEAR VFX: Crisp horizontal white-core + electric-cyan curved motion-smear crescent tracing exact shoulder-to-blade path + rear boot dust puff!"),
            _fb(4, "F4 ACTIVE HIT#1 CLIMAX HITSTOP — FULL FOLLOW-THROUGH",
                "Completes horizontal sword sweep from F3 to full forward extension and locks at impact climax",
                "Peak heroic forward lunge, chest fully opened right",
                "Right arm swept ALL THE WAY ACROSS forward-low holding silver sword extended straight right; left arm flung back",
                "Wide heroic power lunge — front right knee deeply bent braking, rear left leg braced straight back",
                "Red scarf & ponytail stream straight horizontally left",
                "ACTIVE HITBOX CLIMAX VFX: Bold razor-sharp HORIZONTAL-CRESCENT cyan-white-azure gale-blade wave sweeping forward cleanly along the exact horizontal plane of her sword + low wind streak & rear boot dust"),
            _fb(5, "F5 RECOVERY FOLLOW-THROUGH DISSIPATE",
                "Forward lunge brakes cleanly; wrist relaxes lowering blade slightly from F4",
                "Momentum settling, weight beginning to shift back off front knee",
                "Right arm lowers silver sword gently at end of follow-through; left hand returns forward",
                "Front right boot planted braking; rear left boot begins stepping slightly closer",
                "Scarf drops softly slowing down; ponytail settles",
                "DISSIPATION VFX: Horizontal cyan gale-blade breaks into 2-3 thin fading azure wind ribbons drifting right + settling ground dust wisps"),
            _fb(6, "F6 RECOVERY RECOIL TO GUARD",
                "Front leg pushes torso upright while wrist rotates blade smoothly up toward guard",
                "Torso rises smoothly upright back to neutral height",
                "Right wrist lifts full silver sword upward toward neutral 35deg guard",
                "Feet step smoothly back into balanced shoulder-width neutral stance",
                "Scarf ripples calmly back toward idle curve; ponytail settles"),
            _fb(7, "F7 RECOVERY GUARD SETTLE",
                "Final micro-settle from F6 into exact neutral posture",
                "Nearly back to Cell 1 upright posture",
                "Right hand holds full silver sword cleanly in neutral guard",
                "Both boots planted cleanly in neutral Cell 1 spacing",
                "Scarf & ponytail calm"),
            _fb(8, "F8 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 bridging seamlessly into Ghost F9 (=F1)",
                "Neutral upright ready posture",
                "Full silver sword at exact 35deg Cell 1 angle",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 95% matching Cell 1"),
            _fb(9, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    # ==========================================================================
    # v2.5 HIGH-PRECISION 18-FRAME CHAINED MULTI-HIT COMBO (4x3 Part 1 + 3x3 Part 2!)
    # EVERY SINGLE STRIKE HAS ITS OWN SUB-ACTION ANTICIPATION / CHAMBER FRAME!
    # ==========================================================================
    "skill_phantom_flurry": {
        "id": "skill_phantom_flurry",
        "name": "R·居合瞬步三连破空斩 (18帧精密连招)",
        "key": "SKILL R",
        "active_frames": 18,
        "closed_loop": True,
        "grid": [5, 4],  # Audit visualization grid (18+1 = 19 cells cleanly on 5x4!)
        "chained_parts": [
            # Part 1 (4x3 = 12 cells @ 1536x1024 -> 384x341/cell!): generates F1..F11 (+ F12 preview)
            {"name": "part1", "grid": [4, 3], "api_size": "1536x1024", "frame_indices": list(range(1, 13)), "keep_count": 11, "start_anchor": "master"},
            # Part 2 (3x3 = 9 cells @ 1536x1024 -> 512x341/cell!): Cell 1 = actual quantized F11 bridge, Cells 2..8 = F12..F18, Cell 9 = Ghost F1!
            {"name": "part2", "grid": [3, 3], "api_size": "1536x1024", "frame_indices": [11, 12, 13, 14, 15, 16, 17, 18, 19], "splice_from_prev_frame": 11, "end_anchor": "master"},
        ],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": False,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.28,
        "guide_sprite_h_ratio": 0.40,
        "timing_mode": "hitstop",
        # 18 frames: Prep holds & snappy strikes + 265ms climax HITSTOP!
        "frame_durations_ms": [85, 180, 55, 65, 85, 90, 90, 140, 50, 115, 70, 130, 265, 135, 80, 80, 80, 85],
        "hold_tags": {2: "居合蓄力", 8: "突刺收腰前摇", 13: "三斩引爆 HITSTOP", 14: "滑步急停"},
        "combat": {
            "startup_frames": [1, 2, 3, 4, 6, 8, 11],
            "active_frames": {
                5:  {"hitId": 1, "damage": 16, "hitstopMs": 55,  "knockback": [2.5, -2.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "一斩·上挑破空"},
                7:  {"hitId": 2, "damage": 18, "hitstopMs": 60,  "knockback": [2.5,  1.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "二斩·重劈震地"},
                9:  {"hitId": 3, "damage": 14, "hitstopMs": 45,  "knockback": [3.0,  0.0], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "三斩·突刺破风"},
                10: {"hitId": 3, "damage": 24, "hitstopMs": 75,  "knockback": [6.0, -0.5], "kind": "multi_slash", "hitbox_mode": "forward_vfx", "label": "三斩·贯通突刺 MAX"},
                12: {"hitId": 4, "damage": 18, "hitstopMs": 55,  "knockback": [2.0, -1.0], "kind": "scar_ignite", "hitbox_mode": "forward_vfx", "label": "收刀·三痕点亮"},
                13: {"hitId": 5, "damage": 42, "hitstopMs": 190, "knockback": [9.5, -3.0], "kind": "aoe_nova",    "hitbox_mode": "forward_vfx", "label": "三连斩痕爆裂 MAX", "same_continuous_motion": True},
            },
            "recovery_frames": [14, 15, 16, 17, 18],
        },
        "vfx_hint": "iaido_18f_master",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Start neutral ready stance matching Master Anchor Reference Image 1",
                "Neutral upright stance anchored in LEFT THIRD of cell",
                "Right hand grips gleaming full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted shoulder-width on baseline",
                "Scarf gently flowing behind-left"),
            _fb(2, "F2 STARTUP IAIDO CROUCH HOLD",
                "Knees compress -3px into low sprinter block while right hand drops sword smoothly back to left hip",
                "Deep low iaido sprinter crouch (-3px), shoulders coiled tightly forward-low",
                "IAIDO DRAW GRIP: Right hand pulls silver sword LOW & BACK horizontally beside left hip; left hand steadies hip",
                "Both knees deeply bent, rear heel raised loading explosive forward burst",
                "Ponytail pressed low behind; scarf tucked close",
                "TELEGRAPH VFX (UNIFIED CYAN-WHITE STEEL): Sharp white-cyan steel glint right at the sword hilt + compact white dust puff behind coiled rear heel"),
            _fb(3, "F3 STARTUP HIGH-SPEED BLINK DASH",
                "Rear foot explodes off floor pitching torso into 28deg horizontal sprint while sword stays tucked low at hip",
                "Steep 28deg near-horizontal forward dash lean darting right at blinding speed",
                "Right sword-arm tucked tight low-back primed to dip and whip upward; left arm swept back",
                "Front right knee drives hard forward; rear left leg extends straight back pushing off ground",
                "Scarf & ponytail whipped razor-straight horizontally behind",
                "DASH VELOCITY VFX (CYAN-WHITE ONLY): Crisp translucent electric-cyan pixel AFTERIMAGE SILHOUETTE lagging behind torso + 3 sharp horizontal white-cyan wind lines + rear boot dust"),
            _fb(4, "F4 SUB-PREP 1 — UPPERCUT LOW-SWEEP ENTRY (上挑前摇)",
                "Front boot slams down braking dash as right arm swings sword forward-low past knee coiling upward!",
                "Low braced entry posture shifting momentum from horizontal dash into upward spring",
                "SUB-ANTICIPATION 1: Right hand sweeps silver sword LOW IN FRONT OF RIGHT KNEE angled down-forward, elbow bent ready to rip violently SKYWARD on next frame!",
                "Front right foot plants firmly braking dash; rear left knee bends loading upward spring",
                "Scarf catches forward momentum then drops low behind",
                "SWING ENTRY VFX: Thin bright white-cyan leading wind-trail starting right off the low forward-moving blade tip + front heel brake dust"),
            _fb(5, "F5 ACTIVE HIT#1 — RISING UPPERCUT SLASH (一斩·上挑破空)",
                "From F4's low-knee blade, knees & spine spring tall while right arm whips sword 150deg straight UP OVERHEAD!",
                "Torso springs UPWARD tall and open into dramatic rising cut!",
                "OVERHEAD UPPERCUT: Right arm whips gleaming silver sword ALL THE WAY HIGH OVERHEAD pointing up-right; left arm drives downward-back",
                "Front right leg extends tall pivoting forward; rear heel lifts driving upward torque",
                "Scarf & ponytail whip sharply DOWNWARD-LEFT opposite to rising cut",
                "HIT#1 UPWARD VFX (CYAN-WHITE-AZURE): Bold razor-sharp UPWARD-SWEEPING white-core -> electric-cyan -> deep azure crescent arc curving cleanly from knee height all the way up to her overhead sword tip!"),
            _fb(6, "F6 SUB-PREP 2 — OVERHEAD CHOP COCK-BACK CHAMBER (下劈蓄力前摇!)",
                "From F5's overhead blade, right elbow bends pulling sword FURTHER BACK BEHIND HER HEAD while torso arches slightly back to load heavy downward slam!",
                "Tall coiled back-arch posture raising chest and drawing shoulders back to wind up downward chop!",
                "SUB-ANTICIPATION 2 (CRITICAL CHAMBER!): Right hand draws gleaming silver sword HIGH BEHIND HER HEAD/NECK (blade angled up-back at -135deg!) ready to slam violently down! Left arm points forward-down aiming at target!",
                "Front boot lifts slightly onto ball of foot; rear leg braces firmly storing gravity slam energy",
                "Ponytail & scarf lift and flare behind head ready to whip down",
                "CHOP TELEGRAPH VFX: Faint fading tip of Hit#1 cyan arc high right + crisp sharp white-cyan glint flashing right on her cocked-back overhead sword blade!"),
            _fb(7, "F7 ACTIVE HIT#2 — HEAVY OVERHEAD-TO-FLOOR CHOP (二斩·重劈震地)",
                "From F6's cocked-back overhead sword, spine & right arm slam violently DOWNWARD through a full 180deg arc to floor!",
                "Torso slams VIOLENTLY DOWNWARD leaning aggressively low-forward into heavy chop!",
                "FLOOR CHOP POSE: Right arm swings silver sword ALL THE WAY DOWNWARD pointing straight toward the ground in front of boots; left arm lifts high behind back",
                "Deep low power lunge — front knee heavily bent bearing slam, rear leg braced straight back",
                "Scarf & ponytail whip HIGH UPWARD-LEFT opposite to downward chop!",
                "HIT#2 DOWNWARD VFX (CYAN-WHITE-SAPPHIRE): Bold DOWNWARD-SWEEPING white-core -> electric-cyan crescent arc tracing overhead to floor + crisp white-cyan floor impact spark & dust burst where blade strikes low!"),
            _fb(8, "F8 SUB-PREP 3 — HORIZONTAL THRUST WAIST CHAMBER (突刺收腰蓄力前摇!!)",
                "CRITICAL TRANSITION FROM F7 FLOOR-CHOP: Right elbow RETRACTS STRAIGHT BACK lifting blade off floor and tucking sword horizontally tight beside right ribs/hip (pointing straight forward like a coiled spear!) — NEVER teleporting straight to full thrust!",
                "Compact coiled horizontal fencer stance (-2px low), shoulders turned 45deg side-on aiming straight right",
                "UNMISTAKABLE THRUST CHAMBER POSE: Right hand pulls hilt tightly BACK against right ribs/waist holding silver blade DEAD HORIZONTAL (0deg) pointing right like a loaded lance! Left hand reaches forward aiming along the thrust line!",
                "Rear left knee bends deeply coiling horizontal catapult push; front right boot poised light on toe ready to lunge!",
                "Scarf & ponytail pull back-left tightly with hip retraction",
                "THRUST CHAMBER TELEGRAPH VFX: Crisp glowing white-cyan concentrated spear-point glint sparkling directly on the chambered horizontal sword tip + small white dust swirl under coiling rear boot!"),
            _fb(9, "F9 ACTIVE HIT#3 START — MID-THRUST SURGE (三斩·突刺破风)",
                "From F8's waist-chambered spear, rear leg explodes forward driving torso & right elbow halfway straight out horizontally!",
                "Explosive horizontal forward surge leaning steeply along the thrust axis",
                "Right arm shoots horizontal silver sword HALFWAY FORWARD straight out from ribs; left arm snaps backward for counter-balance",
                "Front right boot lunges forward sliding across air; rear left leg drives explosively straight off toe",
                "Scarf & ponytail snap straight horizontally back",
                "THRUST LAUNCH VFX (CYAN-WHITE): Tight pointed pure-white & electric-cyan piercing wind-cone forming right around the accelerating horizontal blade + rear push-off dust!"),
            _fb(10, "F10 ACTIVE HIT#3 MAX — FULL-EXTENSION LANCE THRUST (三斩·贯通突刺极限)",
                "Completes F9 thrust surge to absolute maximum horizontal arm & leg extension!",
                "Maximum horizontal fencer lunge leaning fully forward-right",
                "FULL LANCE EXTENSION: Right arm thrust 100% STRAIGHT HORIZONTALLY FORWARD at absolute max reach holding gleaming horizontal blade; left arm thrown straight back",
                "Maximum deep fencer lunge — front right knee bent sharply braking lunge, rear left leg locked straight out behind",
                "Scarf & ponytail stretched razor-straight horizontally behind",
                "HIT#3 PIERCE VFX (CYAN-WHITE-AZURE): Piercing horizontal white-hot & electric-cyan SWORD-THRUST BEAM shooting straight forward from blade tip + two crisp concentric white-cyan sonic air-break rings wrapping the beam!"),
            _fb(11, "F11 SUB-TRANSITION — THRUST RETRACT PULL-BACK (收剑回拉过渡)",
                "Smooth retraction from F10 full extension: front leg pushes torso slightly back upright while right elbow bends pulling sword halfway back toward chest!",
                "Torso shifts weight cleanly back toward upright balanced center, head level focused right",
                "RETRACTING POSE: Right elbow bends pulling silver sword HALFWAY BACK toward right hip/chest (transitioning smoothly between F10 full extension and F12 reverse-grip hip sheath!); left hand lowers",
                "Front foot plants firmly pushing weight back; rear foot steps slightly closer to center",
                "Scarf eases off full horizontal tension beginning to wave",
                "TRANSITION VFX: Horizontal pierce beam dissolves into 3 thin faint suspended cyan-white after-scars hanging quietly in mid-air ahead (up-diag + down-diag + horizontal)!"),
            _fb(12, "F12 ACTIVE HIT#4 — REVERSE-GRIP HIP SHEATH SNAP: 3 SCARS IGNITE! (收刀·三痕点亮)",
                "Completes F11 pull-back: right hand snaps sword cleanly BACK behind hip in cool reverse-grip braking pose!",
                "Cool composed stance, chin slightly tucked with fierce confident eyes watching the 3 scars ignite ahead",
                "HIP SHEATH SNAP: Right hand holds gleaming silver sword tucked cleanly BACK at hip pointing down-back; left hand steadies front waist",
                "Solid grounded stance planted steadily on floor",
                "Scarf flares forward slightly from sudden stop then sweeps back",
                "HIT#4 SCAR IGNITION VFX (UNIFIED CYAN-WHITE): Directly in front across the right half, the EXACT 3 intersecting razor-thin slash scars from Cuts 1+2+3 (up-diag + down-diag + horizontal!) IGNITE blinding white-cyan with a sharp bright star flash at their exact center!"),
            _fb(13, "F13 ACTIVE HIT#5 CLIMAX HITSTOP — 3-CUT SCAR DETONATION (三连斩痕爆裂定帧)",
                "Locks F12's iconic hip-sheath finish pose firmly as the 3 ignited scars detonate violently in front!",
                "Locked heroic low hip-sheath finish pose bracing cleanly against blast wind",
                "Right hand holds gleaming sword rock-steady tucked at hip pointing back-low; left hand steadies waist",
                "Rock-solid braced stance rooted on floor withstanding shockwave",
                "Scarf & ponytail blasted violently straight backward-left by explosion wind!",
                "HIT#5 DETONATION CLIMAX VFX (UNIFIED ELECTRIC-CYAN, ICE-WHITE & AZURE — ZERO FIREBALLS OR PURPLE DISCO!): The 3 intersecting slash scars DETONATE violently across the right half into sharp radial white-cyan blade shockwaves, slicing wind-arc ribbons, crisp diamond sparks & rolling white ground shockwave dust!"),
            _fb(14, "F14 RECOVERY — STYLISH SKID BRAKE (滑步急停)",
                "Impact shockwave pushes her smoothly into low crouched braking skid from F13",
                "Cool low crouched recoil leaning slightly back-left braking momentum",
                "Right hand brings silver sword low horizontally in front stabilizing crouch; left hand near knee",
                "Both boots angled forward skidding cleanly on floor",
                "Scarf & ponytail settle forward gently as blast wind dies down",
                "BRAKING VFX: Crisp white-tan ground SKID DUST puff under front boot heel + 4 thin fading azure wind slivers dissipating right (clearly signals active Hitbox ended!)"),
            _fb(15, "F15 RECOVERY — UNCROUCH LIFT",
                "Knees straighten lifting torso smoothly upward out of F14 low brake",
                "Rising smoothly upright from crouch toward neutral height",
                "Right arm smoothly lifts full silver sword upward off low brake toward waist-front",
                "Feet step calmly back toward neutral shoulder-width stance",
                "Scarf & ponytail lifting smoothly back into idle flow"),
            _fb(16, "F16 RECOVERY — GUARD RETURN",
                "Continues smooth stand-up from F15 bringing blade squarely into ready guard",
                "Upright balanced standing posture matching neutral height",
                "Right hand raises gleaming full silver sword into 35deg neutral ready guard; left arm neutral",
                "Both boots planted evenly shoulder-width on baseline",
                "Scarf & ponytail waving gently back into calm idle curve"),
            _fb(17, "F17 RECOVERY — SETTLE",
                "Subtle breath & scarf settle from F16 approaching exact Cell 1",
                "Calm neutral ready posture nearly identical to Cell 1",
                "Full silver sword steady at exact 35deg Cell 1 guard angle",
                "Both boots fixed cleanly in Cell 1 neutral spacing",
                "Scarf & ponytail settling calmly"),
            _fb(18, "F18 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 bridging seamlessly into Ghost F19 (=F1)",
                "Neutral upright ready posture matching Cell 1",
                "Full silver sword held at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 95% identical to Cell 1"),
            _fb(19, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    # ==========================================================================
    # v2.5 HIGH-PRECISION 18-FRAME CHAINED ULTIMATE (4x3 Part 1 + 3x3 Part 2!)
    # Smooth Takeoff -> Overhead Raise -> Dive Entry -> Dive Slash -> Ground Stab ->
    # Flame Wave Eruption -> Wrench-Up Chamber -> Yank-Up Sweep -> Heroic Victory!
    # ==========================================================================
    "ult_starfall_slash": {
        "id": "ult_starfall_slash",
        "name": "F·星炎流星坠地斩 (18帧精密奥义)",
        "key": "ULT F",
        "active_frames": 18,
        "closed_loop": True,
        "grid": [5, 4],  # 18+1 = 19 cells cleanly on 5x4!
        "chained_parts": [
            {"name": "part1", "grid": [4, 3], "api_size": "1536x1024", "frame_indices": list(range(1, 13)), "keep_count": 11, "start_anchor": "master"},
            {"name": "part2", "grid": [3, 3], "api_size": "1536x1024", "frame_indices": [11, 12, 13, 14, 15, 16, 17, 18, 19], "splice_from_prev_frame": 11, "end_anchor": "master"},
        ],
        "api_size": "1536x1024",
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 26.0,
        "anchor_x_ratio": 0.3125,
        "guide_x_ratio": 0.29,
        "guide_sprite_h_ratio": 0.39,
        "timing_mode": "hitstop",
        "frame_durations_ms": [85, 80, 185, 60, 65, 165, 55, 70, 75, 275, 105, 130, 85, 80, 200, 80, 80, 85],
        "hold_tags": {3: "燃剑蓄力", 6: "高空举剑定格", 10: "星炎爆发 HITSTOP", 11: "拔剑蓄力", 15: "持剑胜利定格"},
        "combat": {
            "startup_frames": [1, 2, 3, 4, 5, 6, 7, 11],
            "active_frames": {
                8:  {"hitId": 1, "damage": 24, "hitstopMs": 60,  "knockback": [4.0,  3.5], "kind": "dive_slash",   "hitbox_mode": "forward_vfx", "label": "凌空陨落斜斩 HIT#1"},
                9:  {"hitId": 2, "damage": 32, "hitstopMs": 80,  "knockback": [5.0, -3.0], "kind": "ground_slam",  "hitbox_mode": "forward_vfx", "label": "剑尖贯地重击 HIT#2", "same_continuous_motion": True},
                10: {"hitId": 3, "damage": 65, "hitstopMs": 220, "knockback": [12.0,-5.5], "kind": "aoe_nova",     "hitbox_mode": "forward_vfx", "label": "星炎冲击波大爆发 MAX", "same_continuous_motion": True},
                12: {"hitId": 4, "damage": 28, "hitstopMs": 75,  "knockback": [7.5, -4.5], "kind": "flame_surge",  "hitbox_mode": "forward_vfx", "label": "拔剑烈焰上挑 HIT#4"},
            },
            "recovery_frames": [13, 14, 15, 16, 17, 18],
        },
        "vfx_hint": "solar_18f_master",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 STARTUP READY",
                "Start neutral ready stance matching Reference Image 1",
                "Neutral upright stance anchored in left third",
                "Right hand grips gleaming full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted squarely on ground baseline",
                "Scarf gently flowing left"),
            _fb(2, "F2 STARTUP DEEP SPRING CROUCH",
                "Knees bend low (-3px) while left hand moves across chest to join right hand on hilt",
                "Low athletic spring-jump crouch (-3px), head tucked forward",
                "TWO-HANDED GRIP: Both hands clasp sword hilt tightly in front of chest angling blade upward-right",
                "Both knees deeply bent loading explosive vertical takeoff onto planted boots",
                "Ponytail dips behind shoulders; scarf curls down",
                "EARLY TELEGRAPH VFX (UNIFIED SOLAR-GOLD & FLAME): Tiny bright golden ember sparks flickering strictly along the raised sword blade"),
            _fb(3, "F3 STARTUP BLADE IGNITION HOLD",
                "Holds F2 deep crouch tightening core as golden star-fire wraps blade & ground pressure builds",
                "Deepest coiled takeoff crouch (-3px), eyes glowing fiercely up-right",
                "Both hands hold blazing golden-white sword angled forward-up charging solar fire onto blade",
                "Both boots planted firmly inside compact ground air-pressure ring",
                "Scarf & ponytail lifted gently upward by rising heat updraft",
                "CHARGE TELEGRAPH VFX (SOLAR-GOLD ONLY): Blazing golden-white flame wrapping ONLY around sword blade + compact golden ground pressure ring under boots"),
            _fb(4, "F4 STARTUP TAKEOFF EXTENSION",
                "Legs explode straight downward pushing off floor launching toes off ground (+8px rising!)",
                "Explosive vertical launch extending spine straight skyward (+8px off ground)",
                "Both hands drive blazing golden sword upward-right leading launch",
                "Front right knee begins tucking up; back left leg extends straight down leaving floor",
                "Scarf & ponytail trail straight downward-left against upward surge",
                "TAKEOFF VFX: Crisp white-tan ground jump-dust ring erupting flat on floor directly below takeoff spot + golden trail off rising blade"),
            _fb(5, "F5 STARTUP RISING ASCENT",
                "Continues soaring higher (+18px airborne!) as both hands lift blazing sword overhead toward back-arch",
                "Soaring upward (+18px airborne!), chest opening proudly toward sky",
                "Both hands lift blazing golden sword high above head beginning to pull it behind shoulders",
                "Both knees tucked cleanly in athletic mid-air jump posture high off ground",
                "Scarf & ponytail trailing straight down-left",
                "ASCENT VFX: Golden flame aura intensifying cleanly around the rising overhead sword blade (floor below completely clean)"),
            _fb(6, "F6 STARTUP AERIAL APEX — OVERHEAD METEOR RAISE HOLD (高空举剑蓄力定格!)",
                "Reaches jump apex (+22px airborne!) arching spine back & cocking blazing sword high behind head!",
                "High airborne apex (+22px!), spine arched boldly BACKWARD like a drawn bow poised to smash down!",
                "UNMISTAKABLE OVERHEAD RAISE: BOTH HANDS hold blazing golden-white sword HIGH BEHIND HER HEAD pointing up-back, gathering dense solar fire!",
                "Dynamic mid-air bent-knee suspension cleanly high above ground",
                "Scarf & ponytail fanned dramatically behind-left at zero-gravity peak",
                "OVERHEAD METEOR CHARGE VFX (UNIFIED SOLAR-GOLD & FLAME): Radiant golden-white solar flame aura + bright 4-point star flare concentrating strictly around her raised overhead sword blade!"),
            _fb(7, "F7 SUB-PREP DIVE ENTRY (凌空下劈起势)",
                "From F6's back-arched apex, torso snaps aggressively forward pitching head-first into downward dive while sword swings over crown!",
                "Pivoting sharply forward-downward (+18px -> accelerating down!) torso snapping forward",
                "Both hands whip blazing golden sword forward past the top of her head starting the descending meteor arc!",
                "Legs kick back-upward behind her plunging center of mass",
                "Scarf & ponytail whip straight UPWARD-LEFT opposite to downward plunge!",
                "DIVE ENTRY VFX: Leading streak of white-gold solar fire beginning to arc forward-downward from her accelerating overhead blade tip"),
            _fb(8, "F8 ACTIVE HIT#1 — AERIAL METEOR DIVE-SLASH (凌空陨落斜斩)",
                "Continues F7 dive plunge (+10px descending rapidly!) sweeping sword diagonally down-right across front!",
                "Plunging aggressively forward-downward toward ground baseline!",
                "METEOR DIVE-SLASH: Both hands swing blazing golden sword violently OVERHEAD-TO-FORWARD-DOWNWARD in a giant descending cleave!",
                "Legs trailing cleanly behind her rapid downward dive",
                "Scarf & ponytail stream straight upward-left",
                "HIT#1 METEOR DIVE VFX (SOLAR-GOLD, FLAME-ORANGE & CRIMSON): HUGE blazing golden-white -> flame-orange -> crimson curving meteor crescent sweeping diagonally from overhead down-right directly along her plunging sword!"),
            _fb(9, "F9 ACTIVE HIT#2 — SWORD-STABBED-INTO-GROUND SLAM! (剑尖贯地重击)",
                "Completes F8 downward plunge slamming BOTH boots onto ground and driving sword point-first straight into floor!",
                "SLAMMED SQUARELY ONTO GROUND (-3px deep superhero impact crouch!), head fiercely lowered",
                "GROUND-STAB POSE: Both hands drive gleaming silver sword POINT-FIRST STRAIGHT DOWN INTO THE GROUND directly in front of right boot!",
                "Deep heroic 1-knee ground-slam stance — both boots firmly planted back on ground baseline absorbing impact",
                "Ponytail & scarf whipped violently upward then outward from impact",
                "HIT#2 GROUND-SLAM VFX (SOLAR-GOLD & FLAME): Blinding pure-white & golden vertical impact flash + radial cracking fire sparks & billowing ground shockwave dust erupting directly from the exact sword stab point!"),
            _fb(10, "F10 ACTIVE HIT#3 CLIMAX HITSTOP — SOLAR FLAME WAVE ERUPTION (星炎冲击波大爆发)",
                "Locks F9's dramatic sword-in-ground crouch rock-steady as the ground impact detonates forward into roaring flame wave!",
                "Locked firmly in low sword-planted-in-ground pose bracing against roaring blast ahead",
                "Right hand grips hilt of sword planted straight down in floor; left hand braces near knee",
                "Deep braced heroic crouch planted solidly on ground baseline",
                "Red scarf & ponytail blasted furiously straight BACKWARD-LEFT by roaring blast!",
                "HIT#3 CLIMAX ERUPTION VFX (UNIFIED SOLAR-GOLD, BLAZING ORANGE & CRIMSON): MASSIVE forward-surging wave of blazing golden-white & flame-orange solar eruption pillars, ground-ripping flame shockwave & rolling dust erupting directly from her planted sword across the right two-thirds!"),
            _fb(11, "F11 SUB-PREP — WRENCH-UP CHAMBER (拔剑蓄力前摇!!)",
                "CRITICAL SUB-ANTICIPATION FROM F10 GROUND-STAB: Still crouched low, BOTH knees press down & shoulders twist pulling upward tension onto the embedded hilt BEFORE ripping the sword out on F12!",
                "Deep tense crouched stance leaning slightly back-left pulling hard on the embedded sword hilt",
                "WRENCH-UP CHAMBER POSE: Right hand grips hilt tightly with bent elbow pulling upward strain (blade STILL angled low touching the cracked ground, NOT yanked up yet!); left arm pulls back for leverage",
                "Both boots braced hard into floor pushing legs to stand up explosively",
                "Scarf & ponytail settle slightly then tense behind",
                "CHAMBER VFX: F10's giant flame wave subsides into glowing orange embers & warm ground smoke curling around the still-planted blade tip (telegraphs imminent upward yank-out!)"),
            _fb(12, "F12 ACTIVE HIT#4 — YANKING SWORD UP OUT OF FLOOR (拔剑烈焰上挑)",
                "From F11's tense wrench-coil, legs & spine surge upward-right ripping sword violently UPWARD out of floor!",
                "Torso surges upward-right springing powerfully out of ground-slam crouch!",
                "SWORD YANK-UP: Right arm rips gleaming silver sword violently UPWARD-RIGHT out of the floor in a fierce rising sweep; left arm pulls back",
                "Front right knee straightening from lunge; rear left boot pushing firmly on floor",
                "Scarf whips cleanly down-left as she rises",
                "HIT#4 RISING FLAME VFX (SOLAR-GOLD & FLAME): Sweeping upward curtain of blazing golden-orange flame arcs & soaring embers surging upward-right directly off her yanked-up blade!"),
            _fb(13, "F13 RECOVERY — SHAKE OFF EMBERS",
                "Smooth deceleration from F12 upward yank: stands tall swinging blade lightly forward-right to clear embers",
                "Standing upright smoothly, breathing steady, relaxing combat tension",
                "Right arm swings clean silver sword gently outward-right shaking off final fire sparks; left arm relaxed",
                "Feet stepping smoothly back into balanced standing stance on baseline",
                "Scarf & ponytail swinging gently into calm motion",
                "DISSIPATION VFX: Flame curtain gone — only 5 small cooling orange-gold embers & faint dust wisp drifting upward-right"),
            _fb(14, "F14 RECOVERY — CLEAN BLADE RISE",
                "Smoothly lifts clean silver sword from F13 outward shake into vertical victory presentation",
                "Upright poised standing stance, chin lifting proudly",
                "Right wrist smoothly rotates clean gleaming silver sword upward toward skyward victory flourish",
                "Both boots planted cleanly on baseline",
                "Scarf billowing gently left; ponytail bouncing softly"),
            _fb(15, "F15 RECOVERY — HEROIC VICTORY FLOURISH HOLD",
                "Locks F14 upright flourish in proud triumphant JRPG victory pause!",
                "Standing tall & proud (+1px chest proud!), warm confident smile",
                "Right arm holds gleaming full silver sword proudly angled 60deg forward-up; left hand on hip",
                "Confident heroic standing stance cleanly grounded on baseline",
                "Red scarf billows majestically left; ponytail buoyant",
                "VICTORY PUNCTUATION VFX: 2 crisp clean golden-white 4-point blade-glint stars twinkling right on the clean silver sword blade"),
            _fb(16, "F16 RECOVERY — LOWER TO GUARD",
                "Relaxes smoothly out of F15 victory flourish lowering sword arm down toward ready angle",
                "Relaxing smoothly back toward neutral Cell 1 height",
                "Right arm lowers full silver sword halfway back toward 35deg neutral guard; left hand drops from hip",
                "Boots settle smoothly back into neutral Cell 1 spacing",
                "Scarf & ponytail relaxing gently"),
            _fb(17, "F17 RECOVERY — SETTLE GUARD",
                "Brings sword squarely into exact 35deg neutral guard from F16",
                "Calm neutral ready posture nearly identical to Cell 1",
                "Full silver sword held steady at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 neutral spacing",
                "Scarf & ponytail calm"),
            _fb(18, "F18 PRE-LOOP BRIDGE",
                "95% identical to Cell 1 bridging seamlessly into Ghost F19 (=F1)",
                "Neutral upright ready posture matching Cell 1",
                "Full silver sword at exact 35deg Cell 1 angle",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 95% identical to Cell 1"),
            _fb(19, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
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
    part_cfg: dict[str, Any] | None = None,
) -> str:
    """Compile either a single-sheet action prompt OR one seamless part of a chained 18+ frame action."""
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_chibi"])
    is_combat = bool(anim_spec.get("combat", {}).get("active_frames"))
    is_loco = anim_spec["id"] in ("walk", "run")
    vfx_hint = anim_spec.get("vfx_hint", "")

    if part_cfg is not None:
        cols, rows = part_cfg["grid"]
        f_indices = part_cfg["frame_indices"]
        total = len(f_indices)
        all_entries = anim_spec["frame_choreography"]
        entries = [all_entries[fi - 1] for fi in f_indices]
        is_part2 = bool(part_cfg.get("splice_from_prev_frame"))
    else:
        cols, rows = anim_spec["grid"]
        active = int(anim_spec["active_frames"])
        closed = bool(anim_spec.get("closed_loop", True))
        total = active + (1 if closed else 0)
        entries = anim_spec.get("frame_choreography") or anim_spec.get("frame_beats", [])
        is_part2 = False

    if is_combat:
        if vfx_hint in ("steel_horizontal_slash", "iaido_three_cut_detonate", "iaido_18f_master"):
            vfx_pal_desc = (
                "UNIFIED STEEL-WIND VFX PALETTE ONLY: pure white hot core -> ice cyan -> electric cyan -> azure -> deep sapphire + crisp white-tan ground dust "
                "(STRICTLY NO random orange fireballs, NO neon pink/purple disco rainbows!)"
            )
        elif vfx_hint in ("solar_meteor_ground_slam", "solar_18f_master"):
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
            "- PURPOSEFUL SKELETAL CONTINUITY & PHYSICS-DRIVEN VFX MANDATE: Obey EVERY `[BONE LINK]` transition and sub-action chamber/anticipation frame literally! "
            "Every VFX element MUST originate from the exact sword/boots and match the exact swing direction specified per frame — NEVER invent random glow blobs or draw ugly black outlines around glowing energy VFX!"
        )
    elif is_loco:
        pal_rule = (
            f"STRICTLY LOCK ALL pixels exclusively to Reference Image 1's character palette ({', '.join(palette_hex[:16])}). "
            "ABSOLUTE ZERO VFX: NO magic waves, NO glowing slashes, NO sparkles, NO speed lines, NO dust clouds, NO floor shadows!"
            if palette_hex
            else "STRICTLY LOCK all colors identically to Reference Image 1. ZERO VFX, ZERO dust, ZERO shadows!"
        )
        vfx_boost = (
            "- CRITICAL ANATOMICAL GAIT & LEFT/RIGHT LEG ALTERNATION RULE (FOLLOW REFERENCE IMAGE 2 SKELETON EXACTLY!):\n"
            "  * BRIGHT YELLOW = NEAR (foreground/Right) leg (brighter warm brown boot), CYAN = FAR (background/Left) leg (darker shadow-brown boot)!\n"
            "  * Front landing foot MUST stay planted and SLIDE BACKWARD underneath body while OTHER leg swings vertically through center (F3/F7) and steps forward! NEVER march in place!\n"
            "  * Maintain opposite arm-leg counter-swing and full-length gleaming silver sword in EVERY cell. ZERO VFX, ZERO shadows!"
        )
    else:
        pal_rule = (
            f"STRICTLY LOCK ALL pixels exclusively to Reference Image 1's character palette ({', '.join(palette_hex[:16])}). ZERO VFX, ZERO shadows!"
            if palette_hex
            else "STRICTLY LOCK all colors identically to Reference Image 1. ZERO VFX, ZERO shadows!"
        )
        vfx_boost = "- Keep clean crisp silhouette with full-length gleaming silver sword intact in EVERY SINGLE CELL. ZERO VFX, ZERO shadows."

    if is_part2:
        loop_rules = [
            f"- THIS IS PART 2 OF A SEAMLESS CHAINED ANIMATION: Cell 1 MUST 100% MATCH the translucent splice-bridge pose stamped in Cell 1 of Reference Image 2!",
            f"- Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL to Reference Image 1 (matching the translucent anchor stamped in Cell {total} of Reference Image 2)!",
            f"- Cell {total - 1} MUST smoothly bridge into Cell {total} (= F1) for ZERO loop jump!",
        ]
    elif part_cfg is not None:
        loop_rules = [
            "- THIS IS PART 1 OF A SEAMLESS CHAINED ANIMATION: Cell 1 MUST BE 100% IDENTICAL to Reference Image 1 (matching the translucent anchor stamped in Cell 1 of Reference Image 2)!",
            f"- Every cell 1 -> {total} MUST maintain smooth bone-to-bone skeletal continuity and exact same 34px character height!",
        ]
    else:
        loop_rules = [
            f"- Cell 1 (START) and Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL poses matching Cell 1!",
            f"- Cell {total - 1} MUST smoothly bridge into Cell {total} (= Cell 1) for ZERO loop jump!",
        ]

    choreo_lines = [f"- {format_choreography_line(e, cell_override=i + 1)}" for i, e in enumerate(entries)]

    return "\n".join([
        f"EXACT {cols} columns by {rows} rows ({total} frames total, reading strictly left-to-right, top-to-bottom from Cell 1 to Cell {total}) "
        "16-bit CHUNKY LOW-RES PIXEL ART SINGLE-ACTION SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, orange ponytail, red scarf, teal tunic, brown boots, FULL-LENGTH silver sword (NEVER shrink or omit the sword!), and crisp 1-pixel dark outline on the character in EVERY SINGLE CELL.",
        f"Reference Image 2 is the EXACT {cols}x{rows} grid & anatomical composition guide showing cell order (1 -> {total}), character anchor axis, exact sword vectors, and translucent anchor stamps — DO NOT draw any grid lines, boxes, stick-figures, numbers, or guide tints in the final transparent PNG!",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {anim_spec.get('view_prompt', 'classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell')}.",
        "CRITICAL CONTINUITY, SCALE & RENDERING RULES:",
        *loop_rules,
        "- Keep the character's body anchored at the EXACT SAME horizontal axis and EXACT SAME chunky chibi height (~34 logical pixels tall) in EVERY cell — NEVER shrink the character to make room for VFX!",
        vfx_boost,
        f"STRICT FRAME-BY-FRAME 6-DIMENSION SKELETAL CHOREOGRAPHY (FOLLOW EVERY BONE LINK / TORSO / ARM / LEG / SECONDARY / VFX INSTRUCTION LITERALLY!):",
        *choreo_lines,
        f"- Color lock: {pal_rule}",
        f"- Style lock: {style['prompt']}.",
    ])
