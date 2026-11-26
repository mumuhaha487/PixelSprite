"""Pure Pillow Wide-Arena Choreography & Multi-Part Chained Guide Renderer (v2.5 — Dual-Leg Gait + 18-Frame Combat Pose/Sword Vectors + Splice Stamps)."""

from __future__ import annotations

import math
from typing import Any
from PIL import Image, ImageDraw


def _stamp_ghost_anchor(
    canvas: Image.Image,
    anchor_img: Image.Image | None,
    cx: int,
    base_y: int,
    target_h: int,
    alpha_scale: float = 0.48,
) -> None:
    if anchor_img is None:
        return
    anc = anchor_img.convert("RGBA")
    bbox = anc.getbbox()
    if not bbox:
        return
    crop = anc.crop(bbox)
    cw, ch = crop.size
    scale = target_h / max(1, ch)
    nw, nh = max(8, int(round(cw * scale))), max(8, int(round(ch * scale)))
    resized = crop.resize((nw, nh), Image.Resampling.NEAREST)
    r, g, b, a = resized.split()
    a = a.point(lambda v: int(v * alpha_scale))
    ghost = Image.merge("RGBA", (r, g, b, a))
    canvas.alpha_composite(ghost, (cx - nw // 2, base_y - nh))


def _stamp_splice_frame(
    canvas: Image.Image,
    splice_img: Image.Image,
    ox0: int,
    oy0: int,
    cell_w: int,
    cell_h: int,
    cx: int,
    base_y: int,
    target_char_h: int,
    pivot: tuple[int, int] = (30, 71),
    char_h_logical: int = 34,
    alpha_scale: float = 0.62,
) -> None:
    """Stamp an actual quantized 96x80 frame from Part 1 onto Cell 1 of Part 2 at exact scale & ground anchor!"""
    scale = target_char_h / max(1.0, float(char_h_logical))
    nw = max(16, int(round(splice_img.width * scale)))
    nh = max(16, int(round(splice_img.height * scale)))
    resized = splice_img.convert("RGBA").resize((nw, nh), Image.Resampling.NEAREST)
    r, g, b, a = resized.split()
    a = a.point(lambda v: int(v * alpha_scale))
    ghost = Image.merge("RGBA", (r, g, b, a))
    px = cx - int(round(pivot[0] * scale))
    py = base_y - int(round(pivot[1] * scale))
    # Clip cleanly inside cell bounds
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(ghost, (px, py))
    cell_crop = tmp.crop((ox0 + 4, oy0 + 4, ox0 + cell_w - 4, oy0 + cell_h - 4))
    canvas.alpha_composite(cell_crop, (ox0 + 4, oy0 + 4))


def _draw_locomotion_skeleton(
    draw: ImageDraw.ImageDraw,
    cx: int,
    base_y: int,
    sprite_h: int,
    anim_id: str,
    idx: int,
    is_loop_anchor: bool,
) -> None:
    if anim_id == "walk":
        table = [
            (0.00, ( 0.34, 0.56), ( 0.66, 0.00), (-0.18, 0.52), (-0.64, 0.04), -0.18),
            (-0.06,( 0.24, 0.46), ( 0.28, 0.00), (-0.34, 0.50), (-0.68, 0.24), -0.10),
            (0.04, ( 0.04, 0.54), ( 0.00, 0.00), ( 0.28, 0.52), (-0.06, 0.26),  0.02),
            (0.09, (-0.18, 0.54), (-0.48, 0.06), ( 0.44, 0.56), ( 0.56, 0.22),  0.14),
            (0.00, (-0.18, 0.52), (-0.64, 0.04), ( 0.34, 0.56), ( 0.66, 0.00),  0.22),
            (-0.06,(-0.34, 0.50), (-0.68, 0.24), ( 0.24, 0.46), ( 0.28, 0.00),  0.14),
            (0.04, ( 0.28, 0.52), (-0.06, 0.26), ( 0.04, 0.54), ( 0.00, 0.00),  0.02),
            (0.09, ( 0.44, 0.56), ( 0.56, 0.22), (-0.18, 0.54), (-0.48, 0.06), -0.10),
        ]
    else:
        table = [
            (-0.02,( 0.42, 0.52), ( 0.72, 0.00), (-0.28, 0.48), (-0.82, 0.22), -0.22),
            (-0.08,( 0.22, 0.44), ( 0.08, 0.00), (-0.12, 0.44), (-0.44, 0.36), -0.08),
            (0.06, (-0.26, 0.48), (-0.72, 0.04), ( 0.52, 0.54), ( 0.28, 0.32),  0.12),
            (0.18, (-0.34, 0.56), (-0.86, 0.38), ( 0.54, 0.58), ( 0.76, 0.22),  0.24),
            (-0.02,(-0.28, 0.48), (-0.82, 0.22), ( 0.42, 0.52), ( 0.72, 0.00),  0.24),
            (-0.08,(-0.12, 0.44), (-0.44, 0.36), ( 0.22, 0.44), ( 0.08, 0.00),  0.10),
            (0.06, ( 0.52, 0.54), ( 0.28, 0.32), (-0.26, 0.48), (-0.72, 0.04), -0.08),
            (0.18, ( 0.54, 0.58), ( 0.76, 0.22), (-0.34, 0.56), (-0.86, 0.38), -0.20),
        ]

    hip_lift, nk, nf, fk, ff, sw_dx = table[idx % 8]
    leg_len = int(sprite_h * 0.34)
    hip_y = base_y - leg_len - int(round(hip_lift * leg_len))
    lean_x = int(sprite_h * (0.08 if anim_id == "run" else 0.02))
    torso_h = int(sprite_h * 0.28)
    head_r = int(sprite_h * 0.23)
    head_cx = cx + lean_x
    head_cy = hip_y - torso_h - head_r + 4

    def pt(v: tuple[float, float]) -> tuple[int, int]:
        return (cx + int(round(v[0] * leg_len)), base_y - int(round(v[1] * leg_len)))

    fk_p, ff_p = pt(fk), pt(ff)
    nk_p, nf_p = pt(nk), pt(nf)
    hip_p = (cx, hip_y)

    far_c = (56, 189, 248, 220)
    draw.line([hip_p, fk_p, ff_p], fill=far_c, width=6)
    draw.ellipse([ff_p[0] - 7, ff_p[1] - 5, ff_p[0] + 10, ff_p[1] + 5], fill=(56, 189, 248, 175), outline=far_c, width=2)

    body_c = (74, 222, 128, 195) if is_loop_anchor else (148, 163, 184, 155)
    bw = int(head_r * 0.65)
    draw.rounded_rectangle([head_cx - bw, hip_y - torso_h, head_cx + bw, hip_y + 4], radius=10, outline=body_c, width=2)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], outline=body_c, width=2)

    near_c = (250, 204, 21, 245)
    draw.line([hip_p, nk_p, nf_p], fill=near_c, width=7)
    draw.ellipse([nf_p[0] - 7, nf_p[1] - 5, nf_p[0] + 11, nf_p[1] + 5], fill=(250, 204, 21, 205), outline=near_c, width=2)

    sh_p = (head_cx + 4, hip_y - int(torso_h * 0.65))
    hand_p = (head_cx + int(round(sw_dx * sprite_h * 0.45)) + 22, hip_y - int(torso_h * 0.12))
    tip_p = (hand_p[0] + 24, hand_p[1] - 18)
    draw.line([sh_p, hand_p], fill=(244, 114, 182, 170), width=4)
    draw.line([hand_p, tip_p], fill=(248, 250, 252, 190), width=4)


def _draw_combat_choreography_pose(
    draw: ImageDraw.ImageDraw,
    cx: int,
    base_y: int,
    oy0: int,
    ox1: int,
    sprite_h: int,
    vfx_hint: str,
    fnum: int,  # 1-based global frame index (1..19)!
) -> None:
    """Draw explicit pose, sword angle/retraction, and directional VFX trajectory cue using 1-based global frame index `fnum`!"""
    # (lift_r, crouch_r, lean_px, sw_angle_deg, hand_dx_px, blade_len_scale)
    pose = (0.0, 0.0, 0, -35.0, 18, 0.52)

    if vfx_hint == "steel_horizontal_slash":
        poses = {
            2: (0.0, 0.10, -10, -145.0, -10, 0.52),
            3: (0.0, 0.06,  14,  -15.0,  18, 0.52),
            4: (0.0, 0.08,  18,   18.0,  22, 0.54),
            5: (0.0, 0.04,  10,   30.0,  18, 0.50),
            6: (0.0, 0.00,   2,  -25.0,  16, 0.50),
            7: (0.0, 0.00,   0,  -35.0,  18, 0.50),
            8: (0.0, 0.00,   0,  -35.0,  18, 0.50),
        }
        pose = poses.get(fnum, pose)
    elif vfx_hint == "iaido_18f_master":
        poses = {
            2:  (0.00, 0.16,  10,  168.0, -12, 0.52),  # F2: Low iaido crouch, sword back at left hip
            3:  (0.00, 0.10,  22,  160.0, -10, 0.52),  # F3: Steep forward dash + cyan afterimage
            4:  (0.00, 0.14,  12,   48.0,  14, 0.50),  # F4: Sub-Prep 1 — low-knee entry coiling upward!
            5:  (0.04,-0.04,   8,  -75.0,  14, 0.54),  # F5: HIT#1 — high overhead uppercut!
            6:  (0.02,-0.02,  -8, -135.0,  -8, 0.54),  # F6: Sub-Prep 2 — overhead cock-back behind head!
            7:  (0.00, 0.14,  16,   62.0,  18, 0.54),  # F7: HIT#2 — floor-slam chop!
            8:  (0.00, 0.10,  -6,    0.0,  -4, 0.52),  # F8: Sub-Prep 3 — WAIST THRUST CHAMBER (retracted horizontal at ribs!!)!
            9:  (0.00, 0.08,  10,    0.0,  14, 0.54),  # F9: HIT#3 Start — mid-thrust surge!
            10: (0.00, 0.10,  20,    0.0,  28, 0.58),  # F10: HIT#3 Max — full-extension lance thrust!
            11: (0.00, 0.04,   4,   15.0,   8, 0.50),  # F11: Sub-Transition — elbow retracting back toward chest!
            12: (0.00, 0.04,  -4,  152.0, -10, 0.52),  # F12: HIT#4 — hip sheath snap, 3 scars ignite!
            13: (0.00, 0.08,  -6,  156.0, -10, 0.52),  # F13: HIT#5 — locked hip sheath, scars detonate!
            14: (0.00, 0.14,  -4,   12.0,  16, 0.50),  # F14: Stylish skid brake
            15: (0.00, 0.04,   0,  -15.0,  16, 0.50),  # F15: Uncrouch lift
            16: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F16: Guard return
            17: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F17: Settle
            18: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F18: Pre-loop
        }
        pose = poses.get(fnum, pose)
    elif vfx_hint == "solar_18f_master":
        # v2.6 Monotonic Airborne Parabola + Calm Grounded Splice Anchor F11 + Fast Uppercut Motion F13!
        # Airborne curve: 0 -> 0 -> 0 -> +0.20 (F4) -> +0.42 (F5) -> +0.58 APEX (F6) -> +0.34 (F7) -> +0.12 (F8) -> 0 (F9 SLAM!)
        poses = {
            2:  (0.00, 0.14,   2,  -55.0,  14, 0.50),  # F2: Deep spring crouch
            3:  (0.00, 0.18,   2,  -50.0,  14, 0.52),  # F3: CHARGE HOLD #1 — blade ignition crouch (boots flat on ground!)
            4:  (0.20, 0.00,   4,  -62.0,  14, 0.52),  # F4: Takeoff launch (+7px lift, sword angled forward-up)
            5:  (0.42, 0.00,   2,  -90.0,   8, 0.54),  # F5: Mid-ascent (+14px lift, sword straight vertical overhead!)
            6:  (0.58,-0.04,  -6, -138.0,  -8, 0.56),  # F6: CHARGE HOLD #2 — TRUE AERIAL APEX (+20px HIGHEST!), arched back behind head!
            7:  (0.34, 0.02,  10,  -25.0,  18, 0.54),  # F7: FAST MOTION — mid-air downward dive (+12px lift!)
            8:  (0.12, 0.06,  16,   38.0,  22, 0.56),  # F8: HIT#1 — low-air meteor cleave (+4px lift — smooth landing!)
            9:  (0.00, 0.18,  10,   78.0,  20, 0.56),  # F9: HITSTOP #2 — GROUND SLAM + SOLAR FLAME WAVE CLIMAX!
            10: (0.00, 0.06,   4,   12.0,  16, 0.52),  # F10: Recovery unwind — pulling sword off floor as flames fade
            11: (0.00, 0.00,   0,  -26.0,  16, 0.50),  # F11: LINK PAUSE 1->2 — CALM GROUNDED 34px ZERO-VFX SPLICE ANCHOR!
            12: (0.00, 0.18,  -8,  158.0, -10, 0.54),  # F12: CHARGE HOLD #3 — low-knee coiled flame uppercut chamber!
            13: (0.04, 0.04,  10,   15.0,  16, 0.54),  # F13: FAST MOTION — explosive upward flame whip!
            14: (0.06,-0.04,  14,  -65.0,  18, 0.58),  # F14: HITSTOP #3 — RISING SOLAR FLAME UPPERCUT CLIMAX!
            15: (0.00, 0.00,   4,  -78.0,  14, 0.52),  # F15: Recovery 1 — apex deceleration, embers fading
            16: (0.00, 0.00,   2,  -42.0,  16, 0.50),  # F16: Recovery 2 — lower clean silver sword to guard
            17: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F17: Recovery 3 — calm guard settle
            18: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F18: Pre-loop (= F1)
        }
        pose = poses.get(fnum, pose)
    elif vfx_hint == "tri_phase_24f_master":
        # 24-Frame Tri-Phase Power Rhythm Master Pose & Sword Vector Table (3 heavy distinct moves!)
        poses = {
            # MOVE 1: Heavy Coiled Uppercut Cleave (F1..F8)
            2:  (0.00, 0.12,  -6,  140.0,  -6, 0.50),  # F2: Move 1 wind-up entry (dropping low)
            3:  (0.00, 0.20, -10,  165.0, -12, 0.54),  # F3: CHARGE HOLD #1 — deep coiled squat, sword pulled low-back!
            4:  (0.04, 0.04,  10,   20.0,  16, 0.54),  # F4: FAST MOTION #1 — explosive spring upward swing!
            5:  (0.06,-0.04,  14,  -68.0,  18, 0.58),  # F5: HITSTOP #1 — towering uppercut cleave apex!
            6:  (0.00, 0.00,   6,  -82.0,  14, 0.52),  # F6: Recovery 1 — apex settle & spark fade
            7:  (0.00, 0.00,   2,  -40.0,  16, 0.50),  # F7: Recovery 2 — lower sword to chest guard
            8:  (0.00, 0.00,   0,  -25.0,  16, 0.50),  # F8: LINK PAUSE 1->2 — calm grounded 34px stance reset (SPLICE #1!)
            # MOVE 2: Leaping Overhead Meteor Slam (F9..F14)
            9:  (0.24, 0.00,   4,  -88.0,  10, 0.52),  # F9: Move 2 takeoff jump, hoisting sword skyward!
            10: (0.56,-0.04,  -8, -140.0,  -8, 0.56),  # F10: CHARGE HOLD #2 — AIRBORNE APEX high overhead double-hand hold!
            11: (0.28, 0.04,  14,  -15.0,  18, 0.56),  # F11: FAST MOTION #2 — rapid airborne downward dive-swing!
            12: (0.00, 0.20,  16,   52.0,  22, 0.58),  # F12: HITSTOP #2 — heavy ground-slam cleave shockwave!
            13: (0.00, 0.06,   6,   10.0,  16, 0.52),  # F13: Recovery — ground recoil & lift upright
            14: (0.00, 0.00,   0,  -30.0,  16, 0.50),  # F14: LINK PAUSE 2->3 — calm grounded 34px ready poise (SPLICE #2!)
            # MOVE 3: Finisher — Coiled Waist-Chamber Piercing Lance (F15..F24)
            15: (0.00, 0.08,  -4,  -10.0,   4, 0.50),  # F15: Move 3 entry — wide fencer's step back, elbow pulling back
            16: (0.00, 0.14,  -8,    0.0,  -4, 0.52),  # F16: Chamber coil — lowering stance, blade leveling at waist
            17: (0.00, 0.18, -12,    0.0, -10, 0.54),  # F17: CHARGE HOLD #3 — MAX waist-chamber lock, blinding tip star!
            18: (0.00, 0.10,  10,    0.0,  16, 0.56),  # F18: FAST MOTION #3 — rocket lunge mid-thrust!
            19: (0.00, 0.12,  22,    0.0,  30, 0.62),  # F19: HITSTOP #3 — FULL-ARENA PIERCING LANCE BEAM FINISHER!
            20: (0.00, 0.08,  14,    4.0,  22, 0.54),  # F20: Recovery 1 — beam dissipating, holding lunge
            21: (0.00, 0.02,   4,  -12.0,  16, 0.50),  # F21: Recovery 2 — step back & retract elbow
            22: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F22: Recovery 3 — clean guard reset
            23: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F23: Breath settle
            24: (0.00, 0.00,   0,  -35.0,  18, 0.50),  # F24: Pre-loop bridge (= F1)
        }
        pose = poses.get(fnum, pose)

    lift_r, crouch_r, lean_px, sw_angle_deg, hand_dx, bl_scale = pose
    eff_h = int(sprite_h * (1.0 - crouch_r))
    foot_y = base_y - int(round(lift_r * sprite_h))
    head_r = int(sprite_h * 0.24)
    head_cx = cx + lean_px
    head_cy = foot_y - eff_h + head_r
    bw = int(head_r * 0.72)

    out_c = (56, 189, 248, 130)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], outline=out_c, width=2)
    draw.rounded_rectangle([head_cx - bw, head_cy + int(head_r * 0.7), head_cx + bw, foot_y], radius=10, outline=out_c, width=2)

    hand_x = head_cx + hand_dx
    hand_y = head_cy + int(eff_h * 0.46)
    rad = math.radians(sw_angle_deg)
    blade_len = int(sprite_h * bl_scale)
    tip_x = hand_x + int(round(math.cos(rad) * blade_len))
    tip_y = min(base_y, hand_y + int(round(math.sin(rad) * blade_len)))
    draw.line([(hand_x, hand_y), (tip_x, tip_y)], fill=(255, 255, 255, 230), width=5)

    rx0 = cx + bw + 10
    rx1 = ox1 - 14
    mid_y = (head_cy + base_y) // 2
    x_cy = (oy0 + 28 + base_y - 16) // 2

    if vfx_hint == "steel_horizontal_slash":
        if fnum == 2:
            draw.ellipse([tip_x - 10, tip_y - 10, tip_x + 10, tip_y + 10], outline=(56, 232, 224, 180), width=2)
        elif fnum in (3, 4):
            draw.arc([cx - 8, head_cy - 6, rx1, base_y - 4], start=-38, end=38, fill=(56, 232, 224, 185), width=9 if fnum == 4 else 6)
            draw.line([(rx0, mid_y), (rx1 - 8, mid_y)], fill=(255, 255, 255, 130), width=3)
    elif vfx_hint == "iaido_18f_master":
        if fnum == 3:
            draw.ellipse([cx - 56 - head_r, head_cy - head_r, cx - 56 + head_r, head_cy + head_r], outline=(56, 232, 224, 135), width=2)
        elif fnum == 5:
            draw.arc([cx, oy0 + 18, rx1, base_y - 6], start=-72, end=18, fill=(56, 232, 224, 185), width=9)
        elif fnum == 6:
            draw.ellipse([tip_x - 10, tip_y - 10, tip_x + 10, tip_y + 10], outline=(56, 232, 224, 180), width=2)
        elif fnum == 7:
            draw.arc([cx, oy0 + 24, rx1, base_y + 2], start=-25, end=68, fill=(56, 232, 224, 185), width=9)
        elif fnum == 8:
            # Explicit spear-point chamber glint on horizontal blade tip!
            draw.ellipse([tip_x - 11, tip_y - 11, tip_x + 11, tip_y + 11], outline=(56, 232, 224, 210), width=3)
        elif fnum == 9:
            draw.line([(tip_x, tip_y), (min(rx1, tip_x + 70), tip_y)], fill=(165, 248, 255, 180), width=6)
        elif fnum == 10:
            draw.line([(tip_x, tip_y), (rx1, tip_y)], fill=(255, 255, 255, 200), width=8)
            draw.ellipse([tip_x + 16, tip_y - 26, tip_x + 34, tip_y + 26], outline=(56, 232, 224, 175), width=3)
        elif fnum in (12, 13):
            w_l = 8 if fnum == 13 else 4
            draw.line([(rx0 + 6, base_y - 16), (rx1 - 8, oy0 + 28)], fill=(56, 232, 224, 185), width=w_l)
            draw.line([(rx0 + 6, oy0 + 28), (rx1 - 8, base_y - 16)], fill=(56, 232, 224, 185), width=w_l)
            draw.line([(rx0, x_cy), (rx1, x_cy)], fill=(255, 255, 255, 195), width=w_l)
            if fnum == 13:
                draw.ellipse([rx0 - 6, oy0 + 22, rx1, base_y - 8], outline=(165, 248, 255, 165), width=4)
    elif vfx_hint == "solar_18f_master":
        if fnum == 3:
            # Flame glint strictly on sword blade (NO ring underneath boots so boots never sink!)
            draw.ellipse([tip_x - 14, tip_y - 14, tip_x + 14, tip_y + 14], outline=(255, 224, 71, 200), width=3)
        elif fnum == 4:
            draw.ellipse([cx - 38, base_y - 10, cx + 38, base_y + 6], outline=(240, 230, 210, 155), width=2)
        elif fnum == 6:
            draw.ellipse([tip_x - 24, tip_y - 24, tip_x + 24, tip_y + 24], outline=(255, 224, 71, 210), width=4)
        elif fnum == 7:
            draw.arc([cx, oy0 + 18, rx1 - 18, base_y - 14], start=-72, end=12, fill=(255, 224, 120, 180), width=6)
        elif fnum == 8:
            draw.arc([cx - 10, oy0 + 18, rx1, base_y - 4], start=-70, end=55, fill=(251, 146, 60, 200), width=10)
        elif fnum == 9:
            # HITSTOP #2: Ground slam flame pillar + roaring forward wave!
            draw.line([(tip_x, base_y), (tip_x, oy0 + 22)], fill=(255, 244, 186, 205), width=8)
            draw.arc([tip_x - 16, oy0 + 18, rx1, base_y + 10], start=-115, end=0, fill=(251, 146, 60, 205), width=11)
        elif fnum == 12:
            # CHARGE HOLD #3: Coiled low-knee flame tip glint
            draw.ellipse([tip_x - 14, tip_y - 14, tip_x + 14, tip_y + 14], outline=(255, 224, 71, 205), width=3)
        elif fnum == 13:
            # FAST MOTION: Rising golden-orange upward whip ribbon
            draw.arc([cx - 4, oy0 + 26, rx1 - 22, base_y - 4], start=-30, end=42, fill=(255, 230, 140, 185), width=7)
        elif fnum == 14:
            # HITSTOP #3: Towering rising solar flame crescent!
            draw.arc([cx - 4, oy0 + 14, rx1, base_y - 4], start=-78, end=25, fill=(251, 146, 60, 210), width=11)
    elif vfx_hint == "tri_phase_24f_master":
        # Molten-Gold Kinetic Steel VFX Trajectory Guides
        if fnum == 3:
            # Coiled charge #1: tight golden tension spark at blade guard + subtle boot dust
            draw.ellipse([tip_x - 14, tip_y - 14, tip_x + 14, tip_y + 14], outline=(255, 224, 71, 210), width=3)
            draw.ellipse([cx - 34, base_y - 8, cx + 34, base_y + 8], outline=(240, 230, 200, 150), width=2)
        elif fnum == 4:
            # Fast upward motion smear ribbon
            draw.arc([cx - 4, oy0 + 26, rx1 - 24, base_y - 4], start=-30, end=40, fill=(255, 244, 186, 175), width=6)
        elif fnum == 5:
            # HITSTOP #1: Massive molten-gold uppercut crescent arc + apex cross-spark!
            draw.arc([cx - 6, oy0 + 14, rx1, base_y - 4], start=-78, end=25, fill=(251, 182, 36, 210), width=11)
            draw.line([(tip_x + 28, oy0 + 28), (tip_x + 62, oy0 + 62)], fill=(255, 255, 255, 210), width=4)
            draw.line([(tip_x + 62, oy0 + 28), (tip_x + 28, oy0 + 62)], fill=(255, 255, 255, 210), width=4)
        elif fnum == 10:
            # Coiled charge #2: Airborne overhead golden sun-halo around raised sword tip!
            draw.ellipse([tip_x - 24, tip_y - 24, tip_x + 24, tip_y + 24], outline=(255, 224, 71, 220), width=4)
        elif fnum == 11:
            # Fast airborne downward dive speed streak
            draw.arc([cx, oy0 + 18, rx1 - 16, base_y - 10], start=-75, end=15, fill=(255, 230, 140, 185), width=7)
        elif fnum == 12:
            # HITSTOP #2: Heavy overhead meteor slam vertical shockwave + floor eruption burst!
            draw.arc([cx - 4, oy0 + 16, rx1, base_y + 6], start=-55, end=62, fill=(251, 146, 60, 215), width=11)
            draw.ellipse([tip_x - 22, base_y - 16, rx1, base_y + 10], outline=(255, 224, 71, 200), width=4)
        elif fnum == 17:
            # Coiled charge #3: Blinding compressed white-gold star flare on horizontal waist-chamber sword tip!
            draw.ellipse([tip_x - 16, tip_y - 16, tip_x + 16, tip_y + 16], outline=(255, 240, 138, 225), width=3)
            draw.line([(tip_x - 22, tip_y), (tip_x + 22, tip_y)], fill=(255, 255, 255, 220), width=3)
            draw.line([(tip_x, tip_y - 22), (tip_x, tip_y + 22)], fill=(255, 255, 255, 220), width=3)
        elif fnum == 18:
            # Fast rocket lunge mid-thrust needle streak
            draw.line([(tip_x, tip_y), (min(rx1, tip_x + 80), tip_y)], fill=(255, 244, 186, 195), width=7)
        elif fnum == 19:
            # HITSTOP #3: GIGANTIC full-arena golden-white piercing lance beam + double sonic rings!
            draw.line([(tip_x, tip_y), (rx1, tip_y)], fill=(255, 255, 255, 230), width=12)
            draw.line([(tip_x, tip_y - 10), (rx1 - 8, tip_y)], fill=(251, 182, 36, 200), width=5)
            draw.line([(tip_x, tip_y + 10), (rx1 - 8, tip_y)], fill=(251, 182, 36, 200), width=5)
            draw.ellipse([tip_x + 14, tip_y - 32, tip_x + 36, tip_y + 32], outline=(255, 224, 71, 205), width=4)
            draw.ellipse([tip_x + 56, tip_y - 22, tip_x + 74, tip_y + 22], outline=(251, 146, 60, 195), width=3)


def render_variable_action_guide(
    anim_spec: dict[str, Any],
    anchor_img: Image.Image | None = None,
    part_cfg: dict[str, Any] | None = None,
    splice_img: Image.Image | None = None,
    splice_pivot: tuple[int, int] = (30, 71),
    char_h_logical: int = 34,
) -> Image.Image:
    """
    Render either a single-sheet guide OR one part of a seamless multi-part chained guide (e.g. 4x3 Part 1 + 3x3 Part 2)!
    """
    if part_cfg is not None:
        api_size = part_cfg.get("api_size", "1536x1024")
        cols, rows = part_cfg["grid"]
        f_indices = part_cfg["frame_indices"]
    else:
        api_size = anim_spec.get("api_size", "1536x1024")
        cols, rows = anim_spec["grid"]
        total = int(anim_spec["active_frames"]) + (1 if anim_spec.get("closed_loop", True) else 0)
        f_indices = list(range(1, total + 1))

    W, H = (int(x) for x in api_size.split("x"))
    cw, ch = W / cols, H / rows
    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    vfx = anim_spec.get("vfx_hint")
    x_ratio = float(anim_spec.get("guide_x_ratio", anim_spec.get("anchor_x_ratio", 0.30)))
    sp_ratio = float(anim_spec.get("guide_sprite_h_ratio", 0.42))
    active_set = set(int(k) for k in anim_spec.get("combat", {}).get("active_frames", {}).keys())
    n_total_global = int(anim_spec["active_frames"]) + (1 if anim_spec.get("closed_loop", True) else 0)

    for cell_idx, fnum in enumerate(f_indices):
        r = cell_idx // cols
        c = cell_idx % cols
        ox0, oy0 = int(round(c * cw)), int(round(r * ch))
        ox1, oy1 = int(round((c + 1) * cw)), int(round((r + 1) * ch))
        cell_w, cell_h = ox1 - ox0, oy1 - oy0
        cx = ox0 + int(round(cell_w * x_ratio))
        base_y = int(oy0 + cell_h * 0.87)

        is_master_start = (fnum == 1)
        is_master_ghost = bool(anim_spec.get("closed_loop", True)) and (fnum == n_total_global)
        is_splice_cell = (part_cfg is not None and cell_idx == 0 and bool(part_cfg.get("splice_from_prev_frame")) and splice_img is not None)
        is_active = fnum in active_set

        if is_master_start or is_master_ghost or is_splice_cell:
            border = (74, 222, 128, 230)
        elif is_active:
            border = (244, 63, 94, 190)
        else:
            border = (38, 51, 77, 255)
        draw.rectangle([ox0 + 2, oy0 + 2, ox1 - 3, oy1 - 3], fill=(17, 24, 39, 255), outline=border, width=3 if (is_master_start or is_master_ghost or is_splice_cell) else 2)

        draw.line([(cx, oy0 + 18), (cx, base_y)], fill=(148, 163, 184, 48), width=1)
        for x in range(ox0 + 6, ox1 - 6, 12):
            draw.line([(x, base_y), (min(ox1 - 6, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        sprite_h = int(cell_h * sp_ratio)
        if anim_spec["id"] in ("walk", "run"):
            _draw_locomotion_skeleton(draw, cx, base_y, sprite_h, anim_spec["id"], fnum - 1, is_master_start or is_master_ghost)
        elif is_splice_cell and splice_img is not None:
            _stamp_splice_frame(img, splice_img, ox0, oy0, cell_w, cell_h, cx, base_y, sprite_h, pivot=splice_pivot, char_h_logical=char_h_logical, alpha_scale=0.62)
        elif (is_master_start or is_master_ghost) and anchor_img is not None:
            _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.46)
        elif vfx in ("steel_horizontal_slash", "iaido_18f_master", "solar_18f_master", "tri_phase_24f_master"):
            _draw_combat_choreography_pose(draw, cx, base_y, oy0, ox1, sprite_h, vfx, fnum)
        else:
            head_r = int(sprite_h * 0.25)
            head_cy = base_y - sprite_h + head_r
            out_c = (74, 222, 128, 160) if (is_master_start or is_master_ghost) else (56, 189, 248, 120)
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=out_c, width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, base_y], radius=12, outline=out_c, width=2)

    return img
