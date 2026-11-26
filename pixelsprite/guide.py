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
        if (is_start or is_ghost) and anchor_img is not None and anim_spec["id"] not in ("walk", "run"):
            _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.46)
        else:
            lift = 0
            if anim_spec["id"] in ("walk", "run"):
                phase = (idx % 8) / 8.0
                lift = int(abs(math.sin(phase * math.pi * 2)) * (14 if anim_spec["id"] == "run" else 7))
            elif vfx == "mega_ultimate" and 3 <= idx <= 9:
                lift = int(math.sin(((idx - 2.5) / 7.5) * math.pi) * (cell_h * 0.23))

            head_r = int(sprite_h * 0.25)
            foot_y = base_y - lift
            head_cy = foot_y - sprite_h + head_r
            out_c = (74, 222, 128, 160) if (is_start or is_ghost) else (56, 189, 248, 120)
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=out_c, width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, foot_y], radius=12, outline=out_c, width=2)

            # Generous wide VFX composition cues filling the open right two-thirds!
            rx0 = cx + bw + 4
            rx1 = ox1 - 14
            ry0 = max(oy0 + 18, foot_y - int(sprite_h * 1.45))
            ry1 = min(base_y + 6, foot_y + 10)
            if vfx == "mega_arc_right" and 2 <= idx <= 4:
                draw.arc([cx - 8, ry0, rx1, ry1], start=-72, end=58, fill=(56, 232, 224, 165), width=10)
                draw.arc([cx + 12, ry0 + 14, rx1 - 16, ry1 - 10], start=-65, end=50, fill=(255, 255, 255, 130), width=5)
                draw.ellipse([cx - 46, base_y - 16, cx + 10, base_y + 6], outline=(230, 224, 210, 120), width=3)
            elif vfx == "mega_flurry":
                if idx == 1:
                    draw.ellipse([cx - 50, base_y - 14, cx + 56, base_y + 10], outline=(56, 232, 224, 150), width=3)
                elif idx == 2:
                    draw.ellipse([cx - 64 - head_r, head_cy - head_r, cx - 64 + head_r, head_cy + head_r], outline=(56, 232, 224, 110), width=2)
                elif 3 <= idx <= 7:
                    draw.line([(rx0, ry0 + 6), (rx1, ry1 - 8)], fill=(255, 92, 188, 165), width=8)
                    draw.line([(rx0, ry1 - 8), (rx1, ry0 + 6)], fill=(56, 232, 224, 165), width=8)
                    if idx == 7:
                        draw.ellipse([rx0 - 12, ry0 - 6, rx1, ry1], outline=(255, 224, 71, 175), width=5)
            elif vfx == "mega_ultimate":
                if idx == 2:
                    draw.ellipse([cx - 56, base_y - 14, cx + 62, base_y + 10], outline=(255, 224, 71, 175), width=4)
                elif idx == 3:
                    draw.ellipse([cx - 44, base_y - 16, cx + 44, base_y + 8], outline=(255, 182, 36, 170), width=4)
                elif 4 <= idx <= 8:
                    draw.line([(rx0, oy0 + 18), (rx1, base_y - 10)], fill=(255, 92, 188, 165), width=9)
                    draw.line([(rx0, base_y - 10), (rx1, oy0 + 18)], fill=(255, 224, 71, 165), width=9)
                    if idx == 7:
                        draw.ellipse([rx0 - 16, oy0 + 14, rx1, base_y - 6], outline=(56, 232, 224, 180), width=6)
                elif idx == 10:
                    draw.ellipse([cx - 64, base_y - 14, cx + 68, base_y + 8], outline=(240, 230, 210, 150), width=3)

    return img
