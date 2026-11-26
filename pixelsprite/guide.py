"""Pure Pillow layout, baseline, VFX hint, AND Closed-Loop Ghost Anchor (F1 == F[N+1]) guide renderer."""

from __future__ import annotations

import math
from typing import Any
from PIL import Image, ImageDraw

from .presets import ANIMATION_SPECS


def _stamp_ghost_anchor(
    canvas: Image.Image,
    anchor_img: Image.Image | None,
    cx: int,
    base_y: int,
    target_h: int,
    alpha_scale: float = 0.42,
) -> None:
    """Stamp a crisp translucent silhouette/reference of the exact Master Anchor onto Cell 1 and Ghost Cell N+1."""
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


def render_batch_8x4_guide(module_spec: dict[str, Any], batch_index: int = 0) -> Image.Image:
    W, H = 1536, 1024
    cols, rows = 8, 4
    cw, ch = W // cols, H // rows

    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    batch_rows = [r for r in module_spec["rows"] if r["batch"] == batch_index]

    for r in range(rows):
        row_meta = batch_rows[r] if r < len(batch_rows) else {"id": f"row_{r}", "vfx_hint": None}
        vfx = row_meta.get("vfx_hint")
        oy = r * ch
        base_y = int(oy + ch * 0.84)
        draw.rectangle([0, oy, W, oy + ch], fill=(17, 24, 39, 255) if r % 2 == 0 else (15, 21, 36, 255))
        for x in range(0, W, 12):
            draw.line([(x, base_y), (min(W, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        for c in range(cols):
            ox = c * cw
            cx = ox + cw // 2
            draw.rectangle([ox + 1, oy + 1, ox + cw - 2, oy + ch - 2], outline=(38, 51, 77, 255), width=2)
            sprite_h = int(ch * 0.52)
            head_r = int(sprite_h * 0.25)
            head_cy = base_y - sprite_h + head_r
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=(56, 189, 248, 110), width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, base_y], radius=10, outline=(56, 189, 248, 110), width=2)
            if vfx and 2 <= c <= 5:
                draw.arc([cx - 28, base_y - 116, ox + cw - 12, base_y - 10], start=-65, end=50, fill=(250, 204, 21, 140), width=5)

    return img


def render_closed_loop_9x4_guide(pack_spec: dict[str, Any], anchor_img: Image.Image | None = None) -> Image.Image:
    """Render a 9-column x 4-row guide stamping exact translucent F1 Anchor in BOTH Column 1 and Column 9 (=F1)!"""
    W, H = 1536, 1024
    cols, rows = 9, 4
    cw = W / cols  # 170.67
    ch = H // rows  # 256

    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    anims = [ANIMATION_SPECS[aid] for aid in pack_spec["anim_ids"]]

    for r in range(rows):
        anim = anims[r]
        oy = r * ch
        base_y = int(oy + ch * 0.85)
        draw.rectangle([0, oy, W, oy + ch], fill=(17, 24, 39, 255) if r % 2 == 0 else (15, 21, 36, 255))
        for x in range(0, W, 12):
            draw.line([(x, base_y), (min(W, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        sprite_h = int(ch * 0.50)
        for c in range(cols):
            ox0 = int(round(c * cw))
            ox1 = int(round((c + 1) * cw))
            cx = (ox0 + ox1) // 2

            is_anchor_col = (c == 0) or (c == cols - 1)
            border_col = (74, 222, 128, 220) if is_anchor_col else (38, 51, 77, 255)
            draw.rectangle([ox0 + 1, oy + 1, ox1 - 2, oy + ch - 2], outline=border_col, width=2 if is_anchor_col else 1)

            if is_anchor_col and anim["id"] in ("idle", "combo1_slash") and anchor_img is not None:
                # Exact standing anchor stamped at BOTH Start (Col 1) and Ghost Loop End (Col 9)!
                _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.45)
            else:
                phase = (c % 8) / 8.0
                bob = -int(abs(math.sin(phase * math.pi * 2)) * (11 if anim["id"] == "run" else 6)) if anim["id"] in ("walk", "run") else 0
                head_r = int(sprite_h * 0.25)
                foot_y = base_y + bob
                head_cy = foot_y - sprite_h + head_r
                out_c = (74, 222, 128, 150) if is_anchor_col else (56, 189, 248, 105)
                draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=out_c, width=2)
                bw = int(head_r * 0.72)
                draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, foot_y], radius=9, outline=out_c, width=2)

            if anim.get("vfx_hint") == "arc_right" and 2 <= c <= 4:
                draw.arc([cx - 24, base_y - 110, ox1 - 8, base_y - 12], start=-60, end=50, fill=(56, 232, 212, 165), width=5)

    return img


def render_variable_action_guide(anim_spec: dict[str, Any], anchor_img: Image.Image | None = None) -> Image.Image:
    """Render a dedicated multi-row (e.g. 4x3 = 11+1f or 5x3 = 14+1f) guide with exact F1 stamped in Cell 1 & Ghost Cell N+1!"""
    W, H = 1536, 1024
    cols, rows = anim_spec["grid"]
    total = anim_spec["active_frames"] + (1 if anim_spec.get("closed_loop", True) else 0)
    cw = W / cols
    ch = H / rows

    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    vfx = anim_spec.get("vfx_hint")

    for idx in range(total):
        r = idx // cols
        c = idx % cols
        ox0 = int(round(c * cw))
        oy0 = int(round(r * ch))
        ox1 = int(round((c + 1) * cw))
        oy1 = int(round((r + 1) * ch))
        cx = (ox0 + ox1) // 2
        cell_h = oy1 - oy0
        base_y = int(oy0 + cell_h * 0.85)

        is_start = idx == 0
        is_ghost = anim_spec.get("closed_loop", True) and (idx == total - 1)
        border = (74, 222, 128, 220) if (is_start or is_ghost) else (38, 51, 77, 255)
        draw.rectangle([ox0 + 2, oy0 + 2, ox1 - 3, oy1 - 3], fill=(17, 24, 39, 255), outline=border, width=3 if (is_start or is_ghost) else 2)

        for x in range(ox0 + 6, ox1 - 6, 12):
            draw.line([(x, base_y), (min(ox1 - 6, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        sprite_h = int(cell_h * 0.48)
        if (is_start or is_ghost) and anchor_img is not None:
            _stamp_ghost_anchor(img, anchor_img, cx, base_y, sprite_h, alpha_scale=0.48)
        else:
            # Subtle jump/levitation cue for ultimate middle frames
            lift = 0
            if vfx == "ultimate" and 3 <= idx <= 9:
                lift = int(math.sin(((idx - 2.5) / 7.5) * math.pi) * (cell_h * 0.14))
            head_r = int(sprite_h * 0.25)
            foot_y = base_y - lift
            head_cy = foot_y - sprite_h + head_r
            draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=(56, 189, 248, 110), width=2)
            bw = int(head_r * 0.72)
            draw.rounded_rectangle([cx - bw, head_cy + int(head_r * 0.7), cx + bw, foot_y], radius=12, outline=(56, 189, 248, 110), width=2)

            if vfx in ("flurry", "ultimate") and 3 <= idx <= 8:
                draw.line([(cx - 12, oy0 + 36), (ox1 - 20, base_y - 24)], fill=(244, 114, 182, 145), width=5)
                draw.line([(cx - 12, base_y - 24), (ox1 - 20, oy0 + 36)], fill=(56, 232, 212, 145), width=5)

    return img
