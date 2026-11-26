"""Pure Pillow spacious single-action Closed-Loop Guide Renderer (3x3 = 8+1f, 4x3 = 11+1f, 5x3 = 14+1f)."""

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
    Render a spacious grid guide (1024x1024 for 3x3, 1536x1024 for 4x3 / 5x3) with:
      - Exact consistent horizontal anchor axis across ALL cells (prevents leftward VFX push!),
      - Translucent Master Anchor stamped in BOTH Cell 1 (START) and Cell N+1 (GHOST = F1) for standing-start actions,
      - True parabolic airborne lift cues on jumps/ultimates!
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
    x_ratio = float(anim_spec.get("anchor_x_ratio", 0.44))

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
        base_y = int(oy0 + cell_h * 0.86)

        is_start = idx == 0
        is_ghost = bool(anim_spec.get("closed_loop", True)) and (idx == total - 1)
        border = (74, 222, 128, 220) if (is_start or is_ghost) else (38, 51, 77, 255)
        draw.rectangle([ox0 + 2, oy0 + 2, ox1 - 3, oy1 - 3], fill=(17, 24, 39, 255), outline=border, width=3 if (is_start or is_ghost) else 2)

        # Vertical character center lock line + red ground baseline
        draw.line([(cx, oy0 + 18), (cx, base_y)], fill=(148, 163, 184, 42), width=1)
        for x in range(ox0 + 6, ox1 - 6, 12):
            draw.line([(x, base_y), (min(ox1 - 6, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        sprite_h = int(cell_h * 0.48)
        if (is_start or is_ghost) and anchor_img is not None and anim_spec["id"] not in ("walk", "run"):
            _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.46)
        else:
            lift = 0
            if anim_spec["id"] in ("walk", "run"):
                phase = (idx % 8) / 8.0
                lift = int(abs(math.sin(phase * math.pi * 2)) * (14 if anim_spec["id"] == "run" else 7))
            elif vfx == "ultimate" and 3 <= idx <= 9:
                lift = int(math.sin(((idx - 2.5) / 7.5) * math.pi) * (cell_h * 0.22))
            head_r = int(sprite_h * 0.25)
            foot_y = base_y - lift
            head_cy = foot_y - sprite_h + head_r
            out_c = (74, 222, 128, 160) if (is_start or is_ghost) else (56, 189, 248, 110)
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=out_c, width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, foot_y], radius=12, outline=out_c, width=2)

            if vfx == "arc_right" and 2 <= idx <= 4:
                draw.arc([cx - 10, base_y - sprite_h, ox1 - 14, base_y - 10], start=-65, end=50, fill=(56, 232, 212, 155), width=5)
            elif vfx in ("flurry", "ultimate") and 3 <= idx <= 8:
                draw.line([(cx + 6, oy0 + 36), (ox1 - 16, base_y - 24)], fill=(244, 114, 182, 145), width=5)
                draw.line([(cx + 6, base_y - 24), (ox1 - 16, oy0 + 36)], fill=(56, 232, 212, 145), width=5)

    return img
