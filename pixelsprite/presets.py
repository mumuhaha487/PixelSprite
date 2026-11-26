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

    # Tri-Phase Power Rhythm Law Check (v2.6): when timing_mode == 'tri_phase_power', verify charge_hold & hitstop & inter-move link_pause!
    if anim_spec.get("timing_mode") == "tri_phase_power":
        beats = {int(k): str(v) for k, v in anim_spec.get("rhythm_beats", {}).items()}
        durations = anim_spec.get("frame_durations_ms", [])
        if not beats:
            issues.append("timing_mode='tri_phase_power' requires explicit `rhythm_beats` mapping (charge_hold / motion / hitstop / recovery / link_pause).")
        else:
            charge_frames = sorted(f for f, b in beats.items() if b == "charge_hold")
            hitstop_frames = sorted(f for f, b in beats.items() if b == "hitstop")
            if not charge_frames or not hitstop_frames:
                issues.append("tri_phase_power animation must declare BOTH `charge_hold` (蓄力停顿) and `hitstop` (命中打击定帧) frames.")
            for cf in charge_frames:
                if cf <= len(durations) and durations[cf - 1] < 160:
                    issues.append(f"Charge hold F{cf} duration ({durations[cf-1]}ms) is too short (<160ms) to convey heavy power!")
            for hf in hitstop_frames:
                if hf <= len(durations) and durations[hf - 1] < 160:
                    issues.append(f"Hitstop freeze F{hf} duration ({durations[hf-1]}ms) is too short (<160ms) to convey strong impact!")

    # Calm Grounded Splice Anchor Law Check (v2.6): multi-part splice bridges MUST NOT be active attacks or VFX-cluttered frames!
    chained = anim_spec.get("chained_parts") or []
    for part in chained:
        sf = part.get("splice_from_prev_frame")
        if sf:
            s_idx = int(sf)
            if s_idx in active_map:
                issues.append(
                    f"CALM SPLICE VIOLATION: Part '{part.get('name')}' splices on ACTIVE attack frame F{s_idx}! "
                    "Move the splice point to a calm, grounded, full-height (34px), zero-VFX stance/link-pause frame!"
                )
            elif 1 <= s_idx <= len(choreo) and isinstance(choreo[s_idx - 1], dict):
                vfx_s = str(choreo[s_idx - 1].get("vfx_meaning", "")).upper()
                if "NONE" not in vfx_s and "ZERO" not in vfx_s and "CLEAN" not in vfx_s:
                    issues.append(
                        f"CALM SPLICE VIOLATION: Splice frame F{s_idx} has active VFX ('{vfx_s[:60]}...')! "
                        "Splice frames MUST be calm grounded 34px zero-VFX stances to prevent Hurtbox bloat & X-teleports!"
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
                "NONE — horizontal pierce beam fully dissolved, pure clean grounded retracting sprite ensuring spotless Part 1 <-> Part 2 splice!"),
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
    # v2.6 FIXED 18-FRAME CHAINED ULTIMATE (4x3 Part 1 + 3x3 Part 2!)
    #   - Monotonic Airborne Parabola: 0 -> +7 (F4) -> +14 (F5) -> +20 APEX (F6) -> +12 (F7) -> +4 (F8) -> 0 SLAM (F9)
    #   - Calm Grounded Zero-VFX Splice Anchor on F11 (Link Pause 1->2!) — ZERO Hurtbox bloat, ZERO X-teleport!
    #   - Full Tri-Phase Power Rhythm: Charge Holds F3/F6/F12 -> Fast Motion F7/F13 -> Hitstop F9/F14 -> Clean Recovery!
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
        "max_lift_px": 22.0,
        "anchor_x_ratio": 0.30,
        "guide_x_ratio": 0.29,
        "guide_sprite_h_ratio": 0.39,
        "timing_mode": "tri_phase_power",
        "frame_durations_ms": [
            80,  75, 190,  60,  60, 220,  55,  55, 245,  80, 135,  # F1..F11 (Move 1 Meteor Slam + Calm Link Pause F11!)
            220, 55, 240,  80,  80,  80,  85,                      # F12..F18 (Move 2 Rising Flame Uppercut + Clean Recovery!)
        ],
        "rhythm_beats": {
            1: "neutral",
            2: "startup",    3: "charge_hold", 4: "motion",  5: "motion",  6: "charge_hold", 7: "motion", 8: "motion", 9: "hitstop", 10: "recovery", 11: "link_pause",
            12: "charge_hold", 13: "motion", 14: "hitstop", 15: "recovery", 16: "recovery", 17: "recovery", 18: "recovery",
        },
        "hold_tags": {
            3: "燃剑深蹲蓄力",
            6: "高空顶点蓄力",
            9: "流星贯地定帧",
            11: "招间换气1→2",
            12: "压膝炎挑蓄力",
            14: "烈焰上挑定帧",
        },
        "combat": {
            "startup_frames": [2, 3, 4, 5, 6, 7, 12, 13],
            "link_pause_frames": [11],
            "active_frames": {
                8:  {"hitId": 1, "damage": 28, "hitstopMs": 55,  "knockback": [4.5,  3.0], "kind": "dive_slash",   "hitbox_mode": "forward_vfx", "label": "临地流星急劈 HIT#1"},
                9:  {"hitId": 2, "damage": 68, "hitstopMs": 245, "knockback": [11.5,-5.0], "kind": "aoe_nova",     "hitbox_mode": "forward_vfx", "label": "星炎贯地大爆发 HIT#2", "same_continuous_motion": True},
                14: {"hitId": 3, "damage": 44, "hitstopMs": 240, "knockback": [8.5, -5.5], "kind": "flame_surge",  "hitbox_mode": "forward_vfx", "label": "烈焰裂空上挑 HIT#3"},
            },
            "recovery_frames": [10, 15, 16, 17, 18],
        },
        "vfx_hint": "solar_18f_master",
        "scroll_speed": 0,
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "frame_choreography": [
            _fb(1, "F1 NEUTRAL ANCHOR",
                "Exact Master Anchor pose initiating Meteor Ultimate",
                "Neutral upright stance anchored in left third, full 34px chibi height",
                "Right hand grips gleaming full silver sword at 35deg forward-up; left arm neutral",
                "Both boots planted squarely on ground baseline",
                "Red scarf & orange ponytail gently resting left"),
            _fb(2, "F2 STARTUP DEEP SPRING CROUCH",
                "From F1 standing guard, knees bend smoothly (-4px) while left hand joins right hand on hilt",
                "Low athletic takeoff crouch (-4px), torso compact, eyes aiming upward-right",
                "TWO-HANDED GRIP: Both hands clasp sword hilt in front of chest angling gleaming silver blade 50deg forward-up",
                "Both knees bent deeply with boots flat and solid on exact ground baseline",
                "Ponytail dips behind shoulders; scarf curls down",
                "EARLY IGNITION VFX: 3 tiny bright golden sparks flickering strictly on the raised sword blade (ZERO marks below boots!)"),
            _fb(3, "F3 CHARGE HOLD #1 — COILED BLADE IGNITION (190ms)",
                "Deepens F2 crouch slightly (-5px) and FREEZES to ignite full blade with golden solar fire before jump!",
                "Deepest coiled takeoff squat (-5px), determined glowing gaze up-right",
                "Both hands hold blazing solar-gold sword angled 50deg forward-up tightly before chest",
                "Both brown boots planted rock-solid flat on EXACT ground baseline (NEVER draw any ring below boot soles!)",
                "Scarf & ponytail lifted gently by heat updraft",
                "CHARGE VFX (SOLAR-GOLD ON BLADE ONLY): Crisp blazing white-gold solar flame wrapping strictly around the sword blade — KEEP GROUND UNDER BOOTS 100% CLEAN!"),
            _fb(4, "F4 FAST LAUNCH — TAKEOFF (+7px LIFT)",
                "Explodes upward out of F3 crouch leaving ground (+7px lift!) while driving blazing sword diagonally forward-up",
                "Rising cleanly off ground (+7px lift!), spine extending straight upward",
                "Both hands hold blazing golden sword angled 62deg forward-up ahead of forehead (NOT behind head yet!)",
                "Front right knee lifting up; rear left boot pushing off leaving visible gap above ground baseline",
                "Scarf & ponytail trailing downward-left against upward launch",
                "TAKEOFF VFX: Small crisp white-tan dust puff flat on floor directly below takeoff point + golden blade flame"),
            _fb(5, "F5 FAST ASCENT — MID-AIR RISE (+14px LIFT)",
                "Continues smooth climb from F4 (+7px -> +14px lift!) raising blazing sword straight VERTICAL above crown!",
                "Clearly higher mid-air (+14px lift!), chest opening toward sky, distinct intermediate height below F6 apex",
                "STRAIGHT VERTICAL RAISE: Both hands lift blazing golden sword straight up at 90deg directly above top of head (CLEARLY distinct from F4 forward & F6 behind-head!)",
                "Both knees tucked cleanly mid-air well above ground baseline",
                "Scarf & ponytail streaming straight downward-left",
                "ASCENT VFX: Bright golden flame wrapping cleanly around the straight vertical overhead blade (empty air below boots)"),
            _fb(6, "F6 CHARGE HOLD #2 — TRUE AERIAL APEX (+20px HIGHEST! 220ms)",
                "Reaches HIGHEST aerial apex (+20px — visibly HIGHER than F5!) arching spine backward & cocking sword behind head!",
                "HIGHEST AIRBORNE APEX (+20px above floor!), spine arched dramatically BACKWARD like a drawn bow!",
                "FULL OVERHEAD COCK-BACK: Both hands pull blazing golden-white sword HIGH BEHIND HER HEAD at -138deg (10 o'clock) gathering massive solar meteor energy!",
                "Dynamic mid-air bent-knee hang at peak altitude — maximum clean empty space below boots!",
                "Scarf & ponytail fanned wide behind-left at zero-gravity peak",
                "APEX CHARGE VFX (UNIFIED SOLAR-GOLD & WHITE): Blazing circular solar-gold sun-halo & 4-point star flare concentrating strictly around the raised sword blade behind head!"),
            _fb(7, "F7 FAST DIVE — MID-AIR PLUNGE (+12px LIFT, 55ms)",
                "Drops smoothly from F6 apex (+20px -> +12px lift!), snapping torso sharply forward as both hands whip sword over forehead!",
                "Descending fast mid-air (+12px lift — halfway down!), torso curling aggressively forward-downward",
                "Both hands whip blazing golden sword rapidly forward past brow (-25deg) launching downward meteor arc",
                "Legs trailing cleanly upward-back behind diving torso",
                "Scarf & ponytail whipping straight UPWARD opposite to downward drop",
                "DIVE STREAK VFX: Tight blazing white-gold & orange downward speed-arc trailing the plunging blade"),
            _fb(8, "F8 ACTIVE HIT#1 — LOW-AIR METEOR CLEAVE (+4px LIFT, 55ms)",
                "Continues F7 smooth descent (+12px -> +4px just above floor — ZERO vertical teleport!) sweeping huge fiery diagonal cleave!",
                "Just above landing (+4px lift!), torso pitched low forward swinging down with full momentum",
                "METEOR CLEAVE: Both hands drive blazing sword steeply forward-downward (+38deg) cleaving right across front!",
                "Front right boot reaching smoothly down toward ground baseline preparing solid landing",
                "Scarf & ponytail streaming high behind-left",
                "HIT#1 METEOR CLEAVE VFX (SOLAR-GOLD & FLAME-ORANGE): Wide blazing curving golden-orange meteor crescent sweeping from upper-front down to ground-front along her descending blade!"),
            _fb(9, "F9 ACTIVE HITSTOP #2 — GROUND SLAM & FLAME WAVE CLIMAX (0px FLOOR, 245ms)",
                "Lands smoothly from F8 (+4px -> 0px solid ground!) stabbing sword point-first into floor & FREEZING as huge solar flame wave erupts forward!",
                "Solid heroic deep ground-slam crouch (-5px crouch, boots firmly on floor baseline!), fierce expression",
                "GROUND-STAB POSE: Both hands drive gleaming sword steeply down-forward (+78deg) point-first into ground right ahead of front boot (full silver blade clearly visible!)",
                "Wide braced superhero 1-knee landing stance planted firmly on ground baseline",
                "Red scarf & orange ponytail blasted sharply BACKWARD-LEFT by forward eruption!",
                "HIT#2 CLIMAX ERUPTION VFX (UNIFIED SOLAR-GOLD, BLAZING ORANGE & WHITE CORE): Blinding white-gold impact pillar at sword tip detonating into a MASSIVE roaring forward-surging flame wave across the right half of the wide arena!"),
            _fb(10, "F10 RECOVERY — LIFT BLADE & FLAME FADE (80ms)",
                "Unwinds smoothly out of F9 deep slam: front knee pushes body upward while lifting clean silver blade off floor as flames subside",
                "Rising smoothly back toward upright posture (-2px), shoulders unwinding calmly",
                "Right hand pulls gleaming full silver sword smoothly up off floor to calm low-horizontal waist level (+12deg); left hand releases hilt",
                "Rear boot steps forward naturally narrowing stance toward shoulder-width on baseline",
                "Scarf & ponytail drifting gently down from blast",
                "DISSIPATION VFX: Giant flame wave completely gone — only 3 tiny fading golden embers drifting right (cleanly prepares calm F11 splice!)"),
            _fb(11, "F11 LINK PAUSE 1->2 — CALM GROUNDED 34px POISE (135ms) [SPLICE ANCHOR!]",
                "Completes F10 rise into a ROCK-SOLID, CALM, GROUNDED, FULL-HEIGHT 34px ZERO-VFX martial breath pause separating Move 1 from Move 2!",
                "Calm grounded upright 34px full-height martial stance anchored cleanly in left third, alert focused gaze right",
                "Right hand holds clean gleaming full silver sword steady at calm low-forward ready angle (-26deg); left fist poised at waist",
                "Both brown boots planted solidly shoulder-width on exact ground baseline",
                "Red scarf & orange ponytail calm and neatly draped left",
                "NONE — pure clean 34px character sprite, ZERO VFX, ZERO floor embers, ZERO dust (ensures spotless Part 1 <-> Part 2 splice!)"),
            _fb(12, "F12 CHARGE HOLD #3 — LOW-KNEE FLAME UPPERCUT CHAMBER (220ms)",
                "Breaks cleanly from F11 calm pause by dropping deep into coiled low-knee squat pulling sword back behind right hip & FREEZING to charge rising uppercut!",
                "Deep coiled squat (-6px crouch), shoulders twisted back storing explosive upward torque",
                "BOTH hands locked tightly on hilt pulled far low-back behind right hip (+158deg), blade tip igniting with condensed golden flame",
                "Wide grounded power squat firmly planted on exact baseline",
                "Scarf & ponytail pulled taut behind coiled shoulders",
                "UPPERCUT CHARGE VFX: Tight radiant white-gold solar spark pulsing strictly around the retracted sword tip (ZERO marks below boots!)"),
            _fb(13, "F13 FAST MOTION — EXPLOSIVE UPWARD FLAME WHIP (55ms)",
                "Explodes upward out of F12 coiled squat whipping blazing sword violently forward-upward at mid-waist height!",
                "Torso surging explosively upward & forward (+5px rise), chest opening powerfully",
                "Right arm whips gleaming blazing sword rapidly forward-upward through horizontal-mid arc (+15deg); left arm trailing back for counterweight",
                "Back boot driving hard off floor while front knee straightens explosively",
                "Scarf & ponytail whipping sharply downward-left trailing rapid upward rise",
                "FAST WHIP VFX: Crisp blazing pale-gold & flame-orange curved motion smear hugging the rapidly rising blade edge"),
            _fb(14, "F14 ACTIVE HITSTOP #3 — RISING SOLAR FLAME UPPERCUT CLIMAX (240ms)",
                "Completes F13 explosive upward whip to towering 1 o'clock full extension & FREEZES on peak rising flame cleave!",
                "Tall stretched heroic uppercut extension, chest thrust forward-right, fierce battle shout",
                "Right arm extended high overhead holding gleaming silver sword soaring at -65deg (1 o'clock); left arm swept low-back for balance",
                "Front right boot planted rock-solid forward, rear boot balanced on toe absorbing upward recoil",
                "Red scarf & orange ponytail streaming dramatically downward-back",
                "HIT#3 RISING FLAME VFX (UNIFIED SOLAR-GOLD, BLAZING ORANGE & WHITE CORE): Towering sweeping molten-gold & flame-orange rising uppercut crescent surging from low-front up to high-front right off her blade!"),
            _fb(15, "F15 RECOVERY 1 — APEX DECELERATION (80ms)",
                "Relaxes naturally out of F14 peak extension as sword coasts gently near vertical overhead and flame arc fades",
                "Torso easing down smoothly from stretched apex to balanced upright height",
                "Right hand lets clean silver sword ease gently near vertical overhead while elbow begins bending smoothly",
                "Rear heel settles cleanly flat onto ground baseline",
                "Scarf & ponytail drifting gently down from upward whip",
                "DISSIPATION VFX: Flame crescent gone — only 4 tiny fading golden-orange sparks drifting upward-right"),
            _fb(16, "F16 RECOVERY 2 — LOWER TO GUARD (80ms)",
                "Smoothly lowers clean silver sword from F15 apex follow-through halfway down toward chest-right ready guard",
                "Calm upright neutral standing posture matching Cell 1 height",
                "Right arm bends cleanly lowering full gleaming silver sword to 42deg forward-up; left arm relaxing to waist",
                "Both boots stepping smoothly into exact Cell 1 shoulder-width spacing",
                "Scarf & ponytail settling calmly left"),
            _fb(17, "F17 RECOVERY 3 — GUARD SETTLE (80ms)",
                "Brings sword squarely into exact 35deg Cell 1 neutral ready guard from F16",
                "Calm neutral ready posture nearly identical to Cell 1",
                "Full silver sword held steady at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 neutral spacing",
                "Scarf & ponytail calm"),
            _fb(18, "F18 PRE-LOOP BRIDGE (85ms)",
                "96% identical to Cell 1 bridging seamlessly into Ghost F19 (=F1)",
                "Neutral upright ready posture matching Cell 1",
                "Full silver sword at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 stance",
                "Scarf & ponytail 96% identical to Cell 1"),
            _fb(19, "GHOST LOOP = F1",
                "100% identical to Cell 1 closed-loop anchor",
                "100% IDENTICAL TO CELL 1 — neutral upright ready stance in left third",
                "100% IDENTICAL TO CELL 1 — full silver sword at 35deg forward-up",
                "100% IDENTICAL TO CELL 1 — both boots planted shoulder-width",
                "100% IDENTICAL TO CELL 1 — scarf and ponytail exact match"),
        ],
    },
    # --------------------------------------------------------------------------
    # 7. EX SKILL Q — TRI-PHASE POWER RHYTHM 24-FRAME MASTERPIECE COMBO (24+1f = 5x5!)
    #    3-Part Seamless Chained Sheet (3x3 Part1 + 3x3 Part2 + 4x3 Part3):
    #      Move 1 (F1..F8):  Wind-up -> CHARGE HOLD #1 (220ms) -> Fast Swing (55ms) -> HITSTOP #1 (230ms) -> Normal Recovery (80/85ms) -> LINK PAUSE 1->2 (140ms)
    #      Move 2 (F9..F14): Takeoff -> AIRBORNE CHARGE HOLD #2 (230ms) -> Fast Dive (55ms) -> HITSTOP #2 (245ms) -> Normal Recovery (85ms) -> LINK PAUSE 2->3 (140ms)
    #      Move 3 (F15..F24): Chamber Entry -> Coil -> MAX CHARGE HOLD #3 (255ms) -> Fast Lunge (50ms) -> HITSTOP #3 (275ms) -> Normal Recovery (80-85ms x5) -> Loop F25=F1
    # --------------------------------------------------------------------------
    "skill_tri_phase_breaker": {
        "id": "skill_tri_phase_breaker",
        "name": "Q·三段蓄力破势连斩 (24帧三段力量节拍)",
        "key": "EX Q",
        "grid": [5, 5],
        "api_size": "1536x1024",
        "active_frames": 24,
        "closed_loop": True,
        "chained_parts": [
            # Part 1 (3x3 @ 1536x1024 = 512x341/cell!): Move 1 complete + Link Pause F8 + F9 preview!
            {"name": "part1", "grid": [3, 3], "api_size": "1536x1024", "frame_indices": [1, 2, 3, 4, 5, 6, 7, 8, 9], "drop_last": 1},
            # Part 2 (3x3 @ 1536x1024 = 512x341/cell!): Splice F8 (calm grounded 34px!) -> Move 2 complete + Link Pause F14 + F15/F16 previews!
            {"name": "part2", "grid": [3, 3], "api_size": "1536x1024", "frame_indices": [8, 9, 10, 11, 12, 13, 14, 15, 16], "splice_from_prev_frame": 8, "drop_last": 2},
            # Part 3 (4x3 @ 1536x1024 = 384x341/cell!): Splice F14 (calm grounded 34px!) -> Move 3 Finisher + Recovery + Ghost F25 (=F1)!
            {"name": "part3", "grid": [4, 3], "api_size": "1536x1024", "frame_indices": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], "splice_from_prev_frame": 14, "end_anchor": "master", "drop_last": 0},
        ],
        "timing_mode": "tri_phase_power",
        # Exact Tri-Phase Power Rhythm tuned to Move 2's crisp sweet spot (Charge Hold 220-230ms | Fast Motion 50-55ms | Hitstop 230-245ms | Normal Recovery 75-85ms | Inter-Move Link Pause 135ms!)
        "frame_durations_ms": [
            80,  85, 220,  55, 230,  80,  85, 135,   # F1..F8  (Move 1 + Link Pause 1->2)
            75, 230,  55, 245,  85, 135,             # F9..F14 (Move 2 + Link Pause 2->3)
            70,  65, 225,  50, 240,  75,  75,  80,  80,  80,  # F15..F24 (Move 3 Finisher tuned crisp like Move 2!)
        ],
        "rhythm_beats": {
            1: "neutral",
            2: "startup",      3: "charge_hold", 4: "motion",  5: "hitstop",  6: "recovery", 7: "recovery", 8: "link_pause",
            9: "startup",     10: "charge_hold",11: "motion", 12: "hitstop", 13: "recovery",14: "link_pause",
            15: "startup",    16: "startup",    17: "charge_hold",18: "motion",19: "hitstop",20: "recovery",21: "recovery",22: "recovery",23: "recovery",24: "recovery",
        },
        "hold_tags": {
            3: "一招蓄力停顿",
            5: "一招上挑定帧",
            8: "招间换气1→2",
            10: "二招滞空蓄力",
            12: "二招砸地定帧",
            14: "招间换气2→3",
            17: "终结收腰死蓄",
            19: "终结贯通定帧",
        },
        "scroll_speed": 0,
        "lock_body_x": False,
        "allow_airborne": True,
        "max_lift_px": 24.0,
        "anchor_x_ratio": 0.28,
        "guide_x_ratio": 0.28,
        "guide_sprite_h_ratio": 0.38,
        "vfx_hint": "tri_phase_24f_master",
        "combat": {
            "startup_frames": [2, 3, 4, 9, 10, 11, 15, 16, 17, 18],
            "link_pause_frames": [8, 14],
            "active_frames": {
                5:  {"hitId": 1, "damage": 28, "hitstopMs": 230, "knockback": [4.5, -5.5], "hitbox_mode": "forward_vfx", "kind": "melee_arc", "label": "一招·裂空上挑定帧"},
                12: {"hitId": 2, "damage": 36, "hitstopMs": 245, "knockback": [6.0, 2.5],  "hitbox_mode": "aoe_nova",    "kind": "slam_aoe",  "label": "二招·陨铁砸地定帧"},
                19: {"hitId": 3, "damage": 58, "hitstopMs": 240, "knockback": [11.5, -1.5],"hitbox_mode": "forward_vfx", "kind": "pierce_beam","label": "终结·烈钢贯通定帧"},
            },
            "recovery_frames": [6, 7, 13, 20, 21, 22, 23, 24],
        },
        "frame_choreography": [
            # --- MOVE 1: Heavy Coiled Uppercut Cleave (F1..F8) ---
            _fb(1, "F1 IDLE ANCHOR",
                "Exact Master Anchor pose initiating Move 1",
                "Upright neutral ready stance in left third, full 34px chibi height, alert expression",
                "Right hand grips gleaming full silver sword angled 35deg forward-up; left fist ready at waist",
                "Both brown boots planted shoulder-width on baseline",
                "Red scarf & orange ponytail resting naturally to the left"),
            _fb(2, "F2 MOVE 1 ENTRY — DROP WEIGHT",
                "From F1 upright stance, knees bend downward and right arm swings sword down behind hip",
                "Lowering torso (-3px) while rotating right shoulder back to prepare deep coil",
                "Right hand drops silver sword diagonally down-back behind right hip; left hand reaches across toward hilt",
                "Front right boot plants forward as left rear knee flexes deeply",
                "Scarf & ponytail swing slightly upward-right from downward body drop"),
            _fb(3, "F3 MOVE 1 CHARGE HOLD — COILED SQUAT (220ms)",
                "Deepens F2 drop into MAXIMUM coiled squat tension and FREEZES to build heavy power!",
                "Lowest heavy coiled squat (-6px), chest hunched over knees, intense narrowed focused eyes",
                "BOTH hands locked tightly on sword hilt pulled far low-back behind right hip, silver blade flat pointing back-down",
                "Wide low power squat: both boots dug firmly into ground bracing explosive upward spring",
                "Scarf & ponytail pulled taut close behind coiled back",
                "CHARGE TENSION VFX: Tight radiant white-gold energy glint pulsing around sword crossguard + small white-tan dust puff beneath back boot showing massive stored spring force"),
            _fb(4, "F4 MOVE 1 FAST MOTION — EXPLOSIVE UP-SWING (55ms)",
                "Explodes violently upward out of F3 coiled squat whipping sword fast from low-back through knee level forward!",
                "Body surging explosively upward & forward (+6px rise), chest opening dramatically",
                "Right arm whips full silver sword rapidly forward-upward at mid-waist height (20deg) mid-acceleration; left arm trailing back for torque",
                "Back leg driving straight off ground, front knee straightening rapidly in explosive launch",
                "Scarf & ponytail whipping sharply downward-left trailing explosive upward surge",
                "MOTION BLUR VFX: Crisp fast pale-gold & white curved kinetic smear ribbon hugging the rapidly rising silver blade edge"),
            _fb(5, "F5 MOVE 1 HITSTOP — RISING UPPERCUT CLEAVE (230ms)",
                "Completes F4 explosive upward arc to towering 1 o'clock full extension and FREEZES on peak impact!",
                "Tall stretched triumphant uppercut extension, chest thrust forward-right, fierce shout expression",
                "Right arm extended high overhead holding gleaming sword soaring at -68deg (1 o'clock) pointing up-forward; left arm swung low behind for counterweight",
                "Front right boot planted rock-solid forward, rear boot balanced on toe absorbing upward recoil",
                "Scarf & ponytail streaming dramatically downward-back",
                "HIT#1 IMPACT VFX: Towering wide molten-gold & blazing white crescent uppercut slash sweeping from floor-front up to high-front + sharp white 4-point impact cross-spark bursting at upper apex!"),
            _fb(6, "F6 MOVE 1 RECOVERY 1 — APEX DECELERATION",
                "Relaxes naturally out of F5 peak extension as sword coasts slightly past top and slash dissipates",
                "Torso easing down from stretched apex to balanced upright height",
                "Right hand lets sword ease gently near vertical overhead while elbow begins bending naturally",
                "Rear heel settles flat onto ground baseline; stable martial stance",
                "Scarf & ponytail drifting gently down from apex whip",
                "DISSIPATION VFX: Main crescent gone — only 4 tiny fading golden-white kinetic sparks floating near upper tip"),
            _fb(7, "F7 MOVE 1 RECOVERY 2 — LOWER GUARD",
                "Smoothly lowers sword arm from F6 high follow-through back down to chest-right guard",
                "Balanced upright torso settling calmly over hips",
                "Right arm bends cleanly bringing silver sword down to chest-right diagonal guard; left hand returning to waist",
                "Both boots stepping smoothly into crisp shoulder-width balance on baseline",
                "Scarf & ponytail settling calmly to the left"),
            _fb(8, "F8 LINK PAUSE 1->2 — BREATH & STANCE RESET (140ms) [SPLICE #1]",
                "Holds F7 calm upright martial poise for a crisp 140ms breathing pause before launching Move 2!",
                "Calm grounded upright 34px martial stance (exact full height!), shoulders relaxed yet focused, eyes locked right",
                "Right hand holds full clean silver sword steady at calm low-forward ready angle (-25deg); left fist poised near waist",
                "Both brown boots planted solidly shoulder-width on baseline — clean grounded stance",
                "Red scarf & orange ponytail calm and gently draped left"),
            # --- MOVE 2: Leaping Overhead Meteor Slam (F9..F14) ---
            _fb(9, "F9 MOVE 2 TAKEOFF — LEAP & HOIST SWORD",
                "Breaks directly out of F8 calm breath pause by springing off ground into air while hoisting sword vertically!",
                "Airborne rising (+9px lift off ground!), torso stretching upward with fierce determination",
                "BOTH hands gripping hilt hoisting gleaming full silver sword straight skyward above forehead (-88deg)",
                "Boots tucked neatly underneath as knees drive upward off floor baseline",
                "Scarf & ponytail trailing straight downward beneath leaping body",
                "TAKEOFF VFX: Crisp small white-tan jump-burst dust ring right on ground floor beneath her launching boots"),
            _fb(10, "F10 MOVE 2 CHARGE HOLD — AIRBORNE APEX OVERHEAD (230ms)",
                "Reaches highest aerial apex (+20px lift!) from F9, arching back dramatically and FREEZING mid-air with sword cocked behind head!",
                "HIGH AIRBORNE APEX (+20px above ground!), back arched dramatically backward like a drawn bow, fierce battle expression",
                "BOTH hands locked on hilt hoisting gleaming sword high behind head at -140deg (10 o'clock) ready to cleave earth!",
                "Knees tucked dynamically mid-air high above baseline — clear generous empty air gap below boots!",
                "Scarf & ponytail floating dramatically outward behind arched back",
                "AIRBORNE CHARGE VFX: Blazing circular solar-gold energy halo & bright white star-core condensing tightly around the raised sword blade overhead!"),
            _fb(11, "F11 MOVE 2 FAST MOTION — AIRBORNE METEOR DIVE (55ms)",
                "Plummets rapidly downward from F10 apex (+10px lift), curling torso violently forward as both hands whip blade down past brow!",
                "Dropping fast downward & forward (+10px lift), torso pitched steeply forward at 35deg",
                "BOTH hands accelerating glowing gold-edged silver sword sharply downward-forward past forehead (-15deg)",
                "Legs unfolding downward preparing to slam onto ground baseline",
                "Scarf & ponytail whipping straight UPWARD trailing rapid downward drop",
                "DIVE SPEED VFX: Tight blazing amber-gold & white downward motion streak tracing the falling blade arc"),
            _fb(12, "F12 MOVE 2 HITSTOP — HEAVY METEOR GROUND-SLAM (245ms)",
                "Slams boots violently onto floor from F11 dive and drives sword tip straight down into ground — FREEZING on thunderous impact!",
                "Deep heavy ground-slam lunge (-6px crouch), shoulders driven low forward, intense impact grit",
                "BOTH hands slamming sword blade steeply down-forward (+52deg) into the ground directly in front of front boot",
                "Wide heavy impact split lunge: front right knee deeply bent planted flat, rear boot braced firmly far back",
                "Scarf & ponytail blown sharply UP-LEFT by ground shockwave blast",
                "HIT#2 IMPACT VFX: Huge towering vertical molten-gold & fiery-orange downward cleave shockwave + explosive bright-white ground-impact burst & crisp flying rock/ember sparks shooting right along floor!"),
            _fb(13, "F13 MOVE 2 RECOVERY — RECOIL & RISE",
                "Rebounds cleanly upward out of F12 ground slam as front knee pushes torso upright and blade lifts off floor",
                "Rising smoothly back toward upright balance (-2px), shoulders unwinding",
                "Right hand lifts silver sword cleanly off the ground to horizontal waist height; left hand releases hilt back to side",
                "Back boot steps forward smoothly pulling stance back toward shoulder-width",
                "Scarf & ponytail drifting downward gently from shockwave blast",
                "DISSIPATION VFX: Ground burst faded — only 4 small warm golden embers & light dust wisp drifting right"),
            _fb(14, "F14 LINK PAUSE 2->3 — CALM POISE RESET (140ms) [SPLICE #2]",
                "Completes F13 rise into a composed grounded 34px breathing pause — calm before the ultimate piercing finisher!",
                "Calm grounded upright 34px martial stance (exact full height!), chin slightly lowered, focused sharp gaze forward",
                "Right hand holds full clean silver sword calmly angled forward (-30deg); left hand relaxed at hip",
                "Both brown boots planted solidly shoulder-width on baseline — crisp grounded poise",
                "Red scarf & orange ponytail calm and neatly draped left"),
            # --- MOVE 3: Finisher — Coiled Waist-Chamber Piercing Lance (F15..F24 + F25 Ghost) ---
            _fb(15, "F15 MOVE 3 ENTRY — FENCER STEP & DRAW",
                "Breaks from F14 calm pause by stepping left foot back into a wide fencer's stance while drawing right elbow back",
                "Torso twisting sideways into sleek aerodynamic fencer profile, lowering slightly (-3px)",
                "Right elbow begins retracting silver sword back toward right hip, blade rotating toward flat horizontal; left hand lifting to guide",
                "Left rear foot sliding cleanly backward on baseline while front right boot plants forward",
                "Scarf & ponytail trailing slightly forward then catching backward shift"),
            _fb(16, "F16 MOVE 3 CHAMBER COIL — LEVEL BLADE AT RIBS",
                "Continues F15 retraction, dropping hips deeper and leveling sword dead-horizontal at waist height",
                "Deep coiled horizontal fencer crouch (-5px), chest angled forward like an arrow on a bowstring",
                "Right fist pulled tight against right ribs holding sword dead-horizontal (0deg) pointing straight right; left hand steadying wrist",
                "Both knees bent deeply in coiled sprinter/fencer stance planted firmly on baseline",
                "Scarf & ponytail pulled straight back horizontally behind shoulders",
                "CHAMBER SPARK VFX: Small crisp white-gold energy spark condensing right onto the horizontal silver sword point"),
            _fb(17, "F17 MOVE 3 CHARGE HOLD — MAX WAIST-CHAMBER LOCK (225ms)",
                "Locks F16 horizontal chamber at MAXIMUM spring compression and FREEZES for 225ms building crisp piercing force!",
                "Deepest coiled horizontal crouch (-6px), head tucked low over shoulder, blazing focused eyes locked straight right",
                "Right fist pinned tightly behind right ribs holding gleaming silver sword DEAD-HORIZONTAL (0deg) pointing dead-right; left palm bracing hip",
                "Rear boot planted on tiptoe like a compressed spring ready to fire; front knee locked forward bearing tension",
                "Scarf & ponytail vibrating taut straight behind her",
                "MAX CHARGE VFX: Blinding condensed white-gold 4-point compression star-flare blazing directly on the horizontal sword tip + tight golden wind ring drawing energy inward!"),
            _fb(18, "F18 MOVE 3 FAST MOTION — ROCKET LUNGE MID-THRUST (50ms)",
                "Unleashes F17 coiled lock in an instantaneous 50ms horizontal bullet-lunge punching sword halfway out!",
                "Body shooting violently forward horizontally, torso pitched low aerodynamic",
                "Right arm punching full silver sword horizontally straight forward at mid-extension (0deg); left arm snapping straight back for balance",
                "Rear leg kicking straight off floor driving forward into long explosive lunge",
                "Scarf & ponytail streaming dead-horizontal backward like racing banners",
                "MID-THRUST VFX: Razor-sharp blazing white-gold needle streak erupting straight right from the surging blade tip"),
            _fb(19, "F19 MOVE 3 HITSTOP — FULL-ARENA PIERCING LANCE FINISHER (240ms)",
                "Hits MAXIMUM full-arm horizontal extension from F18 and FREEZES for 240ms as colossal lance pierces across the entire arena!",
                "Maximum stretched aerodynamic horizontal fencer's lunge, head low & fierce behind thrusting shoulder",
                "Right arm 100% locked straight forward driving silver sword dead-horizontal (0deg) to peak forward reach; left arm extended fully behind",
                "Deepest wide heroic lunge: front right knee bent sharply forward, rear leg stretched completely straight behind on baseline",
                "Scarf & ponytail blasted violently straight backward by piercing sonic recoil",
                "HIT#3 FINISHER VFX: GIGANTIC razor-sharp white-hot core & blazing molten-gold piercing lance beam extending across the entire right arena + TWO concentric golden sonic shockwave rings around the shaft + explosive starburst at the far tip!"),
            _fb(20, "F20 MOVE 3 RECOVERY 1 — LANCE DISSIPATION",
                "Holds F19 extended lunge briefly as piercing lance breaks into trailing golden wind ribbons",
                "Torso easing slightly upward out of full forward stretch, relaxing shoulders",
                "Right arm begins unlocking elbow slightly while keeping sword angled horizontally forward (+4deg)",
                "Front right boot bracing firmly to halt forward lunge momentum",
                "Scarf & ponytail billowing down from full horizontal stream",
                "DISSIPATION VFX: Main lance beam gone — crisp fading thin golden wind-streaks & 5 warm sparks drifting right"),
            _fb(21, "F21 MOVE 3 RECOVERY 2 — RETRACT & STEP BACK",
                "Pushes cleanly back upright off F20 front boot while retracting sword elbow back toward torso",
                "Torso straightening smoothly back to upright neutral height",
                "Right elbow pulls clean silver sword smoothly back toward chest-side; left hand dropping back to waist",
                "Front boot steps smoothly back into balanced standing spacing on baseline",
                "Scarf & ponytail swinging gently left into calm settle"),
            _fb(22, "F22 MOVE 3 RECOVERY 3 — GUARD RESET",
                "Rotates wrist cleanly from F21 retraction into exact Cell 1 diagonal ready guard",
                "Calm upright neutral standing posture matching Cell 1 height",
                "Right hand raises full gleaming silver sword cleanly to exact 35deg forward-up neutral guard",
                "Both boots planted cleanly in exact Cell 1 shoulder-width spacing",
                "Scarf & ponytail settling smoothly left"),
            _fb(23, "F23 BREATH SETTLE",
                "Fine natural settle from F22 matching 95% of Master Anchor Cell 1",
                "Calm neutral ready posture matching Cell 1",
                "Full gleaming silver sword steady at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 neutral stance",
                "Scarf & ponytail gently calm"),
            _fb(24, "F24 PRE-LOOP BRIDGE",
                "98% identical to Cell 1 bridging seamlessly into Ghost F25 (=F1)",
                "Neutral upright ready posture matching Cell 1",
                "Full silver sword at exact 35deg Cell 1 guard angle",
                "Both boots planted cleanly in exact Cell 1 neutral stance",
                "Scarf & ponytail 98% identical to Cell 1"),
            _fb(25, "GHOST LOOP = F1",
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
        elif vfx_hint in ("solar_meteor_ground_slam", "solar_18f_master", "tri_phase_24f_master"):
            vfx_pal_desc = (
                "UNIFIED MOLTEN-GOLD KINETIC STEEL VFX PALETTE ONLY: pure white hot impact core -> pale lemon gold -> bright solar gold -> blazing molten amber -> fiery steel orange + crisp white-tan ground shockwave dust "
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

    if part_cfg is not None:
        has_splice = bool(part_cfg.get("splice_from_prev_frame"))
        ends_master = part_cfg.get("end_anchor") == "master"
        p_label = str(part_cfg.get("name", "PART")).upper()
        loop_rules = []
        if has_splice:
            loop_rules.append(
                f"- THIS IS {p_label} OF A SEAMLESS MULTI-PART CHAINED ANIMATION: Cell 1 MUST 100% MATCH the translucent splice-bridge pose stamped in Cell 1 of Reference Image 2!"
            )
        else:
            loop_rules.append(
                f"- THIS IS {p_label} OF A SEAMLESS MULTI-PART CHAINED ANIMATION: Cell 1 MUST BE 100% IDENTICAL to Reference Image 1 (matching the translucent anchor stamped in Cell 1 of Reference Image 2)!"
            )
        if ends_master:
            loop_rules.append(
                f"- Cell {total} (GHOST LOOP ANCHOR) MUST BE 100% IDENTICAL to Reference Image 1 (matching the translucent anchor stamped in Cell {total} of Reference Image 2)!"
            )
            loop_rules.append(f"- Cell {total - 1} MUST smoothly bridge into Cell {total} (= F1) for ZERO loop jump!")
        else:
            loop_rules.append(
                f"- Every cell 1 -> {total} MUST maintain smooth bone-to-bone skeletal continuity and exact same 34px character height!"
            )
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
