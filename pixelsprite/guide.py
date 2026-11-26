"""Pure Pillow spacious Wide-Arena Closed-Loop Guide Renderer (v2.2 — Left-Third Anchor + Huge Multi-Layered VFX Cues)."""

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
    alpha_scale: float = 0.46,
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


def _draw_locomotion_skeleton(
    draw: ImageDraw.ImageDraw,
    cx: int,
    base_y: int,
    sprite_h: int,
    anim_id: str,
    idx: int,
    is_loop_anchor: bool,
) -> None:
    """
    Draw an exact Richard-Williams 8-frame kinematic stick-figure guide with color-coded legs:
      - YELLOW (#facc15) = NEAR (foreground / Right) leg & boot
      - CYAN   (#38bdf8) = FAR  (background / Left) leg & boot
    Guarantees true Left/Right alternation, backward-sliding stance foot, center passing crossover (F3/F7),
    and opposite arm/sword counter-swing!
    """
    # Exact 8-frame gait tables: (hip_lift_ratio, near_knee, near_foot, far_knee, far_foot, sword_dx_ratio)
    # Coords are (dx_ratio, dy_from_ground_ratio) relative to (cx, base_y), scaled by leg_len.
    # Ground is dy=0.0; positive dy is UP off the ground; positive dx is FORWARD (right).
    if anim_id == "walk":
        table = [
            # F1 (Contact 1): Near(Y) extended forward heel-strike, Far(C) extended back toe-push; sword back
            (0.00, ( 0.34, 0.56), ( 0.66, 0.00), (-0.18, 0.52), (-0.64, 0.04), -0.18),
            # F2 (Down 1): Near(Y) planted absorbing weight slightly forward, Far(C) lifting behind
            (-0.06,( 0.24, 0.46), ( 0.28, 0.00), (-0.34, 0.50), (-0.68, 0.24), -0.10),
            # F3 (Passing 1): Near(Y) STRAIGHT VERTICAL planted at x=0; Far(C) knee bent passing through center!
            (0.04, ( 0.04, 0.54), ( 0.00, 0.00), ( 0.28, 0.52), (-0.06, 0.26),  0.02),
            # F4 (High/Push 1): Near(Y) slides BACK pushing off toe; Far(C) swings HIGH FORWARD to land!
            (0.09, (-0.18, 0.54), (-0.48, 0.06), ( 0.44, 0.56), ( 0.56, 0.22),  0.14),
            # F5 (Contact 2 - EXACT SWAP OF F1!): Far(C) forward heel-strike, Near(Y) back toe-push; sword forward
            (0.00, (-0.18, 0.52), (-0.64, 0.04), ( 0.34, 0.56), ( 0.66, 0.00),  0.22),
            # F6 (Down 2 - EXACT SWAP OF F2!): Far(C) planted absorbing weight, Near(Y) lifting behind
            (-0.06,(-0.34, 0.50), (-0.68, 0.24), ( 0.24, 0.46), ( 0.28, 0.00),  0.14),
            # F7 (Passing 2 - EXACT SWAP OF F3!): Far(C) STRAIGHT VERTICAL at x=0; Near(Y) crossing forward!
            (0.04, ( 0.28, 0.52), (-0.06, 0.26), ( 0.04, 0.54), ( 0.00, 0.00),  0.02),
            # F8 (High/Push 2 - EXACT SWAP OF F4!): Far(C) slides back pushing off; Near(Y) swings forward into F9(=F1)!
            (0.09, ( 0.44, 0.56), ( 0.56, 0.22), (-0.18, 0.54), (-0.48, 0.06), -0.10),
        ]
    else:  # run — athletic forward-leaning sprint with 2 true airborne flight phases (F4, F8)
        table = [
            # F1 (R-Strike): Near(Y) landing forward, Far(C) stretched back
            (-0.02,( 0.42, 0.52), ( 0.72, 0.00), (-0.28, 0.48), (-0.82, 0.22), -0.22),
            # F2 (R-Absorb): Near(Y) bent directly under torso absorbing load, Far(C) tucked pulling forward
            (-0.08,( 0.22, 0.44), ( 0.08, 0.00), (-0.12, 0.44), (-0.44, 0.36), -0.08),
            # F3 (R-Pushoff): Near(Y) driving far back off toe; Far(C) knee driving HIGH forward!
            (0.06, (-0.26, 0.48), (-0.72, 0.04), ( 0.52, 0.54), ( 0.28, 0.32),  0.12),
            # F4 (Flight 1): BOTH FEET AIRBORNE! Far(C) reaching far forward, Near(Y) kicked high behind!
            (0.18, (-0.34, 0.56), (-0.86, 0.38), ( 0.54, 0.58), ( 0.76, 0.22),  0.24),
            # F5 (L-Strike - SWAP OF F1!): Far(C) landing forward, Near(Y) stretched back
            (-0.02,(-0.28, 0.48), (-0.82, 0.22), ( 0.42, 0.52), ( 0.72, 0.00),  0.24),
            # F6 (L-Absorb - SWAP OF F2!): Far(C) bent under torso, Near(Y) tucked pulling forward
            (-0.08,(-0.12, 0.44), (-0.44, 0.36), ( 0.22, 0.44), ( 0.08, 0.00),  0.10),
            # F7 (L-Pushoff - SWAP OF F3!): Far(C) pushing far back; Near(Y) knee driving HIGH forward!
            (0.06, ( 0.52, 0.54), ( 0.28, 0.32), (-0.26, 0.48), (-0.72, 0.04), -0.08),
            # F8 (Flight 2 - SWAP OF F4!): BOTH FEET AIRBORNE! Near(Y) reaching forward into F9(=F1), Far(C) kicked back!
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

    # 1. Draw FAR (background / Left) leg FIRST in CYAN
    far_c = (56, 189, 248, 220)
    draw.line([hip_p, fk_p, ff_p], fill=far_c, width=6)
    draw.ellipse([ff_p[0] - 7, ff_p[1] - 5, ff_p[0] + 10, ff_p[1] + 5], fill=(56, 189, 248, 175), outline=far_c, width=2)

    # 2. Draw Torso & Head contour
    body_c = (74, 222, 128, 195) if is_loop_anchor else (148, 163, 184, 155)
    bw = int(head_r * 0.65)
    draw.rounded_rectangle([head_cx - bw, hip_y - torso_h, head_cx + bw, hip_y + 4], radius=10, outline=body_c, width=2)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], outline=body_c, width=2)

    # 3. Draw NEAR (foreground / Right) leg ON TOP in BRIGHT YELLOW
    near_c = (250, 204, 21, 245)
    draw.line([hip_p, nk_p, nf_p], fill=near_c, width=7)
    draw.ellipse([nf_p[0] - 7, nf_p[1] - 5, nf_p[0] + 11, nf_p[1] + 5], fill=(250, 204, 21, 205), outline=near_c, width=2)

    # 4. Draw counter-swinging sword hand cue (white blade clearly outside torso)
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
    idx: int,
) -> None:
    """
    Draw explicit pose, sword angle, and physically meaningful directional VFX vector cues
    for every combat frame so GPT Image 2.6 renders unmistakable martial stances (back-swing,
    uppercut, floor-chop, lance-thrust, hip-sheath, overhead meteor raise, ground-stab slam!)
    instead of a static character next to random rainbow blobs!
    """
    # Per-frame (lift_ratio, crouch_ratio, lean_px, sword_start_rel, sword_end_rel)
    lift_r = 0.0
    crouch_r = 0.0
    lean_px = 0
    sw_angle_deg = -35.0  # 0=right, -90=straight up, +90=straight down, -145=behind head
    sw_behind = False

    if vfx_hint == "steel_horizontal_slash":
        poses = {
            1: (0.0, 0.10, -10, -145.0, True),   # F2: Back-swing behind head!
            2: (0.0, 0.06,  14,  -15.0, False),  # F3: Mid horizontal sweep!
            3: (0.0, 0.08,  18,   18.0, False),  # F4: Full horizontal follow-through!
            4: (0.0, 0.04,  10,   30.0, False),  # F5: Low follow-through!
            5: (0.0, 0.00,   2,  -25.0, False),  # F6: Rising to guard
            6: (0.0, 0.00,   0,  -35.0, False),  # F7: Neutral guard
            7: (0.0, 0.00,   0,  -35.0, False),  # F8: Pre-loop
        }
        lift_r, crouch_r, lean_px, sw_angle_deg, sw_behind = poses.get(idx, (0.0, 0.0, 0, -35.0, False))
    elif vfx_hint == "iaido_three_cut_detonate":
        poses = {
            1: (0.0, 0.16,  12,  165.0, True),   # F2: Deep iaido crouch, sword pulled low-back at hip!
            2: (0.0, 0.10,  22,  155.0, True),   # F3: Steep horizontal dash + cyan afterimage!
            3: (0.04,-0.04, 10,  -75.0, False),  # F4: CUT 1 — High overhead uppercut!
            4: (0.0, 0.14,  16,   62.0, False),  # F5: CUT 2 — Slamming sword down to floor!
            5: (0.0, 0.10,  20,    0.0, False),  # F6: CUT 3 — Full horizontal lance thrust!
            6: (0.0, 0.04,  -4,  150.0, True),   # F7: Reverse-grip hip pull-back (3 scars ignite!)
            7: (0.0, 0.08,  -6,  155.0, True),   # F8: Cool hip-sheath finish (scars detonate!)
            8: (0.0, 0.14,  -4,   12.0, False),  # F9: Low skid brake!
            9: (0.0, 0.02,   0,  -25.0, False),  # F10: Rise to guard
            10:(0.0, 0.00,   0,  -35.0, False),  # F11: Pre-loop
        }
        lift_r, crouch_r, lean_px, sw_angle_deg, sw_behind = poses.get(idx, (0.0, 0.0, 0, -35.0, False))
    elif vfx_hint == "solar_meteor_ground_slam":
        poses = {
            1: (0.00, 0.14,  4,  -65.0, False),  # F2: Deep spring crouch, two-hand hilt
            2: (0.00, 0.16,  4,  -55.0, False),  # F3: Blade ignition hold
            3: (0.42, 0.00,  8,  -80.0, False),  # F4: Explosive vertical leap!
            4: (0.58,-0.04, -6, -135.0, True),   # F5: High airborne arched TWO-HANDED OVERHEAD RAISE!
            5: (0.36, 0.04, 18,   38.0, False),  # F6: Aerial diagonal meteor dive-slash!
            6: (0.00, 0.18, 12,   82.0, False),  # F7: SWORD STABBED POINT-FIRST INTO FLOOR!
            7: (0.00, 0.18, 10,   82.0, False),  # F8: Locked ground-stab pose + flame wave eruption!
            8: (0.00, 0.02, 10,  -48.0, False),  # F9: Yank sword UP out of cracked floor!
            9: (0.00, 0.00,  4,  -15.0, False),  # F10: Shake off embers
            10:(0.00, 0.00,  0,  -40.0, False),  # F11: Clean blade rise
            11:(0.00,-0.04,  0,  -62.0, False),  # F12: Heroic victory flourish!
            12:(0.00, 0.00,  0,  -35.0, False),  # F13: Relax
            13:(0.00, 0.00,  0,  -35.0, False),  # F14: Pre-loop
        }
        lift_r, crouch_r, lean_px, sw_angle_deg, sw_behind = poses.get(idx, (0.0, 0.0, 0, -35.0, False))

    eff_h = int(sprite_h * (1.0 - crouch_r))
    foot_y = base_y - int(round(lift_r * sprite_h))
    head_r = int(sprite_h * 0.24)
    head_cx = cx + lean_px
    head_cy = foot_y - eff_h + head_r
    bw = int(head_r * 0.72)

    # Body contour
    out_c = (56, 189, 248, 130)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], outline=out_c, width=2)
    draw.rounded_rectangle([head_cx - bw, head_cy + int(head_r * 0.7), head_cx + bw, foot_y], radius=10, outline=out_c, width=2)

    # Explicit Sword Vector (thick bright white line so model obeys exact blade angle!)
    hand_x = head_cx + (-10 if sw_behind else 18)
    hand_y = head_cy + int(eff_h * 0.44)
    rad = math.radians(sw_angle_deg)
    blade_len = int(sprite_h * 0.52)
    tip_x = hand_x + int(round(math.cos(rad) * blade_len))
    tip_y = min(base_y, hand_y + int(round(math.sin(rad) * blade_len)))
    draw.line([(hand_x, hand_y), (tip_x, tip_y)], fill=(255, 255, 255, 220), width=5)

    # Purposeful directional VFX trajectory cues (100% matched to the martial stroke!)
    rx0 = cx + bw + 10
    rx1 = ox1 - 14
    mid_y = (head_cy + base_y) // 2
    x_cy = (oy0 + 28 + base_y - 16) // 2

    if vfx_hint == "steel_horizontal_slash":
        if idx == 1:
            draw.ellipse([tip_x - 10, tip_y - 10, tip_x + 10, tip_y + 10], outline=(56, 232, 224, 180), width=2)
        elif idx in (2, 3):
            # Horizontal sweeping crescent strictly along horizontal swing plane!
            draw.arc([cx - 8, head_cy - 6, rx1, base_y - 4], start=-38, end=38, fill=(56, 232, 224, 185), width=9 if idx == 3 else 6)
            draw.line([(rx0, mid_y), (rx1 - 8, mid_y)], fill=(255, 255, 255, 130), width=3)
    elif vfx_hint == "iaido_three_cut_detonate":
        if idx == 2:
            # Translucent cyan afterimage silhouette behind dashing torso
            draw.ellipse([cx - 56 - head_r, head_cy - head_r, cx - 56 + head_r, head_cy + head_r], outline=(56, 232, 224, 135), width=2)
        elif idx == 3:
            # Cut 1: Upward sweeping bottom-left to top-right cyan arc!
            draw.arc([cx, oy0 + 18, rx1, base_y - 6], start=-72, end=18, fill=(56, 232, 224, 185), width=9)
        elif idx == 4:
            # Cut 2: Downward sweeping top-right to floor cyan arc!
            draw.arc([cx, oy0 + 24, rx1, base_y + 2], start=-25, end=68, fill=(56, 232, 224, 185), width=9)
        elif idx == 5:
            # Cut 3: Horizontal lance-beam straight out from sword tip!
            draw.line([(tip_x, tip_y), (rx1, tip_y)], fill=(255, 255, 255, 195), width=8)
            draw.ellipse([tip_x + 18, tip_y - 26, tip_x + 36, tip_y + 26], outline=(56, 232, 224, 175), width=3)
        elif idx in (6, 7):
            # 3 exact intersecting cut scars (up-diag + down-diag + horizontal!) igniting & detonating!
            w_l = 8 if idx == 7 else 4
            draw.line([(rx0 + 6, base_y - 16), (rx1 - 8, oy0 + 28)], fill=(56, 232, 224, 185), width=w_l)
            draw.line([(rx0 + 6, oy0 + 28), (rx1 - 8, base_y - 16)], fill=(56, 232, 224, 185), width=w_l)
            draw.line([(rx0, x_cy), (rx1, x_cy)], fill=(255, 255, 255, 195), width=w_l)
            if idx == 7:
                draw.ellipse([rx0 - 6, oy0 + 22, rx1, base_y - 8], outline=(165, 248, 255, 165), width=4)
    elif vfx_hint == "solar_meteor_ground_slam":
        if idx == 2:
            draw.ellipse([cx - 38, base_y - 10, cx + 44, base_y + 8], outline=(255, 224, 71, 175), width=3)
        elif idx == 3:
            draw.ellipse([cx - 42, base_y - 12, cx + 42, base_y + 8], outline=(240, 230, 210, 155), width=3)
        elif idx == 4:
            # Radiant golden aura around raised overhead sword
            draw.ellipse([tip_x - 24, tip_y - 24, tip_x + 24, tip_y + 24], outline=(255, 224, 71, 190), width=4)
        elif idx == 5:
            # Diagonal meteor dive-slash arcing overhead -> down-right!
            draw.arc([cx - 10, oy0 + 16, rx1, base_y - 6], start=-75, end=52, fill=(251, 146, 60, 190), width=10)
        elif idx in (6, 7):
            # Ground-stab impact pillar & surging golden flame wave erupting from sword stab point!
            draw.line([(tip_x, base_y), (tip_x, oy0 + 26)], fill=(255, 244, 186, 190), width=8)
            if idx == 7:
                draw.arc([tip_x - 20, oy0 + 18, rx1, base_y + 12], start=-115, end=0, fill=(251, 146, 60, 195), width=10)
                draw.ellipse([tip_x - 32, base_y - 14, rx1, base_y + 10], outline=(255, 224, 71, 180), width=4)
        elif idx == 8:
            # Rising flame sweep off yanked-up sword
            draw.arc([cx + 12, oy0 + 24, rx1, base_y - 4], start=-65, end=20, fill=(251, 182, 36, 175), width=8)


def render_variable_action_guide(anim_spec: dict[str, Any], anchor_img: Image.Image | None = None) -> Image.Image:
    """
    Render a wide-arena grid guide (1536x1024 for combat skills / 1024x1024 for locomotion) with:
      - Exact Left-Third character lock axis (`guide_x_ratio = 0.28`) opening 72% of cell width for MASSIVE VFX!
      - Translucent Master Anchor stamped in BOTH Cell 1 (START) and Cell N+1 (GHOST = F1),
      - Explicit visual VFX expansion arcs, magic circles, shockwave ellipses, and airborne jump parabola cues!
    """
    api_size = anim_spec.get("api_size", "1536x1024")
    W, H = (int(x) for x in api_size.split("x"))
    cols, rows = anim_spec["grid"]
    total = int(anim_spec["active_frames"]) + (1 if anim_spec.get("closed_loop", True) else 0)
    cw = W / cols
    ch = H / rows

    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    vfx = anim_spec.get("vfx_hint")
    x_ratio = float(anim_spec.get("guide_x_ratio", anim_spec.get("anchor_x_ratio", 0.30)))
    sp_ratio = float(anim_spec.get("guide_sprite_h_ratio", 0.42))
    active_set = set(int(k) for k in anim_spec.get("combat", {}).get("active_frames", {}).keys())

    for idx in range(total):
        r = idx // cols
        c = idx % cols
        ox0 = int(round(c * cw))
        oy0 = int(round(r * ch))
        ox1 = int(round((c + 1) * cw))
        oy1 = int(round((r + 1) * ch))
        cell_w = ox1 - ox0
        cell_h = oy1 - oy0
        cx = ox0 + int(round(cell_w * x_ratio))
        base_y = int(oy0 + cell_h * 0.87)

        is_start = idx == 0
        is_ghost = bool(anim_spec.get("closed_loop", True)) and (idx == total - 1)
        is_active = (idx + 1) in active_set

        if is_start or is_ghost:
            border = (74, 222, 128, 225)
        elif is_active:
            border = (244, 63, 94, 190)
        else:
            border = (38, 51, 77, 255)
        draw.rectangle([ox0 + 2, oy0 + 2, ox1 - 3, oy1 - 3], fill=(17, 24, 39, 255), outline=border, width=3 if (is_start or is_ghost) else 2)

        # Vertical character lock line + red ground baseline
        draw.line([(cx, oy0 + 18), (cx, base_y)], fill=(148, 163, 184, 48), width=1)
        for x in range(ox0 + 6, ox1 - 6, 12):
            draw.line([(x, base_y), (min(ox1 - 6, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        sprite_h = int(cell_h * sp_ratio)
        if anim_spec["id"] in ("walk", "run"):
            _draw_locomotion_skeleton(draw, cx, base_y, sprite_h, anim_spec["id"], idx, is_start or is_ghost)
        elif (is_start or is_ghost) and anchor_img is not None:
            _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.46)
        elif vfx in ("steel_horizontal_slash", "iaido_three_cut_detonate", "solar_meteor_ground_slam"):
            _draw_combat_choreography_pose(draw, cx, base_y, oy0, ox1, sprite_h, vfx, idx)
        else:
            head_r = int(sprite_h * 0.25)
            foot_y = base_y
            head_cy = foot_y - sprite_h + head_r
            out_c = (74, 222, 128, 160) if (is_start or is_ghost) else (56, 189, 248, 120)
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=out_c, width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, foot_y], radius=12, outline=out_c, width=2)

    return img
