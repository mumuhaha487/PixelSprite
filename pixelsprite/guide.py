"""Pure Pillow 8x4 (32-frame) layout, baseline, and VFX silhouette guide renderer."""

from __future__ import annotations

import math
from typing import Any
from PIL import Image, ImageDraw


def render_batch_8x4_guide(module_spec: dict[str, Any], batch_index: int = 0) -> Image.Image:
    W, H = 1536, 1024
    cols, rows = 8, 4
    cw, ch = W // cols, H // rows  # 192 x 256

    img = Image.new("RGBA", (W, H), (14, 19, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    batch_rows = [r for r in module_spec["rows"] if r["batch"] == batch_index]

    for r in range(rows):
        row_meta = batch_rows[r] if r < len(batch_rows) else {"id": f"row_{r}", "vfx_hint": None}
        vfx = row_meta.get("vfx_hint")
        oy = r * ch
        base_y = int(oy + ch * 0.84)

        row_bg = (17, 24, 39, 255) if r % 2 == 0 else (15, 21, 36, 255)
        draw.rectangle([0, oy, W, oy + ch], fill=row_bg)

        # Red foot baseline
        for x in range(0, W, 12):
            draw.line([(x, base_y), (min(W, x + 6), base_y)], fill=(244, 63, 94, 150), width=2)

        for c in range(cols):
            ox = c * cw
            cx = ox + cw // 2

            draw.rectangle([ox + 1, oy + 1, ox + cw - 2, oy + ch - 2], outline=(38, 51, 77, 255), width=2)
            draw.line([(cx, oy + 20), (cx, base_y)], fill=(148, 163, 184, 36), width=1)

            phase = c / cols
            bob_y = 0
            lean_x = 0
            if row_meta["id"] in ("walk", "run") or row_meta["id"].startswith("dir_"):
                bob_y = -int(abs(math.sin(phase * math.pi * 2)) * (12 if row_meta["id"] == "run" else 7))
            elif vfx == "jump":
                bob_y = -int(math.sin(((c - 0.5) / 6.0) * math.pi) * 38) if 1 <= c <= 6 else 4
            elif vfx in ("slam", "ultimate") and 2 <= c <= 4:
                bob_y = -32
            elif vfx in ("arc_right", "arc_up", "beam_right", "flurry"):
                lean_x = 12 if 2 <= c <= 5 else (-8 if c <= 1 else 0)

            sprite_h = int(ch * 0.52)
            head_r = int(sprite_h * 0.25)
            foot_y = base_y + bob_y
            head_cy = foot_y - sprite_h + head_r

            if vfx == "ko" and c >= 6:
                draw.rounded_rectangle(
                    [cx - 52, base_y - 44, cx + 52, base_y],
                    radius=12,
                    fill=(56, 189, 248, 36),
                    outline=(56, 189, 248, 115),
                    width=2,
                )
            else:
                draw.ellipse(
                    [cx + lean_x - head_r, head_cy - head_r, cx + lean_x + head_r, head_cy + head_r],
                    fill=(56, 189, 248, 36),
                    outline=(56, 189, 248, 115),
                    width=2,
                )
                bw = int(head_r * 0.72)
                draw.rounded_rectangle(
                    [cx + lean_x - bw, head_cy + int(head_r * 0.7), cx + lean_x + bw, foot_y],
                    radius=10,
                    fill=(56, 189, 248, 36),
                    outline=(56, 189, 248, 115),
                    width=2,
                )

            # Subtle VFX target area hints on peak strike frames (c=2..5)
            if vfx and 2 <= c <= 6:
                vfx_col = (250, 204, 21, 140)
                if vfx == "beam_right" and 4 <= c <= 6:
                    draw.rounded_rectangle([ox + 16, foot_y - 78, ox + cw - 12, foot_y - 44], radius=10, fill=(56, 232, 212, 70), outline=(56, 232, 212, 180), width=3)
                elif vfx == "arc_right" and 2 <= c <= 5:
                    draw.arc([cx - 32, foot_y - 120, ox + cw - 12, foot_y - 10], start=-60, end=50, fill=vfx_col, width=6)
                elif vfx == "arc_up" and 2 <= c <= 5:
                    draw.arc([cx - 30, oy + 24, ox + cw - 12, foot_y - 12], start=-95, end=25, fill=vfx_col, width=6)
                elif vfx == "slam" and 4 <= c <= 6:
                    draw.ellipse([cx - 60, base_y - 68, ox + cw - 10, base_y + 4], outline=vfx_col, width=4)
                elif vfx == "sky_cast" and 2 <= c <= 6:
                    for k in range(3):
                        sx = cx + 10 + k * 24
                        draw.line([(sx + 14, oy + 26), (sx - 12, base_y - 16)], fill=(56, 232, 212, 160), width=4)
                elif vfx in ("flurry", "ultimate") and 2 <= c <= 6:
                    draw.line([(cx - 10, oy + 32), (ox + cw - 14, base_y - 24)], fill=vfx_col, width=4)
                    draw.line([(cx - 10, base_y - 24), (ox + cw - 14, oy + 32)], fill=(56, 232, 212, 160), width=4)
                elif vfx == "aura" and 2 <= c <= 6:
                    draw.ellipse([cx - 64, oy + 28, cx + 64, base_y + 4], outline=(56, 232, 212, 150), width=4)

    return img
