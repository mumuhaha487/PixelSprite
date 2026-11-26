"""Pixel-perfect MP4 showcase renderer with live 8x8 cursor & ARPG Skill-Bar HUD (requires ffmpeg)."""

from __future__ import annotations

import io
import os
import subprocess
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageFont

from .quantizer import make_checkerboard_preview


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def render_showcase_mp4(
    sheets: list[dict[str, Any]],
    out_mp4: Path,
    fps_video: int = 30,
) -> Path:
    """
    Render a crisp 1280x720 MP4 cycling through one or more 8x8 sheets with:
      - Left: full 8x8 checkerboard sheet + live glowing orange frame cursor
      - Right top: 6x nearest-neighbor live pixel arena with ground scroll
      - Right bottom: interactive-style ARPG Skill-Bar buttons lighting up active skill + 8-frame strip!
    Each item in `sheets` must have: {"atlas": PIL.Image, "meta": dict, "loops_per_row": int, "rows_to_show": list[int] | None}
    """
    W, H = 1280, 720
    f_title = _load_font(20, bold=True)
    f_sub = _load_font(12, bold=False)
    f_h2 = _load_font(17, bold=True)
    f_btn_k = _load_font(11, bold=True)
    f_btn_n = _load_font(11, bold=False)
    f_mono = _load_font(13, bold=True)

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-framerate", str(fps_video),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            "-preset", "medium",
            "-movflags", "+faststart",
            str(out_mp4),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    assert proc.stdin is not None
    ground_offset = 0.0
    total_frames = 0

    for item in sheets:
        atlas: Image.Image = item["atlas"].convert("RGBA")
        meta: dict[str, Any] = item["meta"]
        cell_size: int = int(meta["cellSize"])
        anims: list[dict[str, Any]] = meta["animations"]
        loops_default: int = int(item.get("loops_per_row", 2))
        rows_to_show = item.get("rows_to_show") or list(range(len(anims)))

        # Pre-slice all 64 frames & build 8x8 checkerboard display once
        frames_64: list[Image.Image] = []
        for r in range(8):
            for c in range(8):
                frames_64.append(atlas.crop((c * cell_size, r * cell_size, (c + 1) * cell_size, (r + 1) * cell_size)))

        chk_sheet = make_checkerboard_preview(atlas, scale=4).resize((616, 616), Image.Resampling.NEAREST)
        sheet_label = meta.get("moduleNameZh") or meta.get("moduleName") or "8×8 Pixel Sprite Sheet"

        for r_idx in rows_to_show:
            anim = anims[r_idx]
            anim_fps = max(6, int(anim.get("fps", 12)))
            row_id = anim["id"]
            loops = loops_default
            scroll_speed = 220 if row_id == "run" else (115 if row_id == "walk" or row_id.startswith("dir_") else (140 if row_id == "jump_dash" else 0))
            dur_sec = (loops * 8) / anim_fps
            n_vid_frames = max(16, int(round(dur_sec * fps_video)))

            for vf in range(n_vid_frames):
                col = int((vf / fps_video) * anim_fps) % 8
                ground_offset += scroll_speed / fps_video

                frame = Image.new("RGBA", (W, H), (12, 16, 24, 255))
                draw = ImageDraw.Draw(frame, "RGBA")

                # Header bar
                draw.rectangle([0, 0, W, 60], fill=(17, 23, 37, 255))
                draw.line([(0, 60), (W, 60)], fill=(34, 47, 71, 255), width=2)
                draw.rounded_rectangle([24, 13, 68, 47], radius=8, fill=(56, 189, 248, 255))
                draw.text((34, 20), "PX", fill=(5, 20, 34, 255), font=f_h2)
                draw.text((82, 11), f"PixelSprite · {sheet_label}", fill=(248, 250, 252, 255), font=f_title)
                draw.text(
                    (82, 37),
                    f"{cell_size}×{cell_size} 真逻辑像素 · {len(meta.get('palette', []))} 色锁定色板 · 1px 复古轮廓 · 纯手绘动态零骨骼僵硬",
                    fill=(148, 163, 184, 255),
                    font=f_sub,
                )

                # Left: 8x8 Master Sheet + live glowing translucent row tint & orange cell cursor
                ax, ay = 24, 78
                draw.rounded_rectangle([ax - 4, ay - 4, ax + 620, ay + 620], radius=10, fill=(20, 28, 44, 255), outline=(41, 55, 82, 255), width=2)
                frame.paste(chk_sheet, (ax, ay))
                step = 616 / 8.0
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov, "RGBA")
                od.rectangle([ax, int(ay + r_idx * step), ax + 616, int(ay + (r_idx + 1) * step)], fill=(56, 189, 248, 46))
                cx0 = int(ax + col * step)
                cy0 = int(ay + r_idx * step)
                od.rectangle([cx0 + 1, cy0 + 1, int(cx0 + step) - 1, int(cy0 + step) - 1], outline=(249, 115, 22, 255), width=3)
                frame.alpha_composite(ov)

                # Right Top: Large 6x Live Pixel Stage
                sx, sy, sw, sh = 664, 78, 592, 372
                draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=12, fill=(20, 28, 44, 255), outline=(44, 61, 94, 255), width=2)
                ix, iy, iw, ih = sx + 8, sy + 8, sw - 16, sh - 16
                floor_y = iy + ih - 66
                draw.rectangle([ix, iy, ix + iw, floor_y], fill=(24, 38, 64, 255))
                draw.rectangle([ix, floor_y, ix + iw, iy + ih], fill=(32, 54, 50, 255))

                # Retro pixel floor blocks
                tile = 32
                off = int(ground_offset) % tile
                for gx in range(ix - tile, ix + iw + tile, tile):
                    tx = gx - off
                    if tx + 16 > ix and tx < ix + iw:
                        draw.rectangle([max(ix, tx), floor_y, min(ix + iw, tx + 16), floor_y + 8], fill=(44, 76, 68, 255))
                    if tx + 32 > ix and tx + 16 < ix + iw:
                        draw.rectangle([max(ix, tx + 16), floor_y + 12, min(ix + iw, tx + 32), floor_y + 18], fill=(40, 68, 62, 255))

                # Soft translucent contact shadow via alpha_composite
                sh_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(sh_ov, "RGBA").ellipse(
                    [sx + sw // 2 - 52, floor_y - 2, sx + sw // 2 + 52, floor_y + 14], fill=(10, 15, 24, 125)
                )
                frame.alpha_composite(sh_ov)

                # 6x Nearest-neighbor crisp sprite!
                zoom = max(4, min(6, 288 // cell_size))
                draw_sz = cell_size * zoom
                cur_sprite = frames_64[r_idx * 8 + col].resize((draw_sz, draw_sz), Image.Resampling.NEAREST)
                foot_offset = int(round(cell_size * 0.92)) * zoom
                px_x = sx + sw // 2 - draw_sz // 2
                px_y = floor_y + 6 - foot_offset
                frame.alpha_composite(cur_sprite, (px_x, px_y))

                # Stage title pill + frame badge
                draw.rounded_rectangle([ix + 14, iy + 14, ix + 340, iy + 54], radius=8, fill=(10, 15, 28, 255), outline=(56, 189, 248, 255), width=1)
                draw.text((ix + 26, iy + 23), f"[{anim.get('key', f'R{r_idx+1}')}] {anim['name']}", fill=(56, 189, 248, 255), font=f_h2)

                draw.rounded_rectangle([ix + iw - 156, iy + 14, ix + iw - 14, iy + 46], radius=8, fill=(10, 15, 28, 255), outline=(41, 55, 82, 255), width=1)
                draw.text((ix + iw - 144, iy + 22), f"ROW {r_idx + 1} · {col + 1}/8", fill=(74, 222, 128, 255), font=f_mono)

                # Right Middle: ARPG Skill-Bar HUD (8 glowing buttons matching the 8 rows!)
                hy = 462
                draw.rounded_rectangle([sx, hy, sx + sw, hy + 104], radius=10, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
                bw = (sw - 24 - 7 * 6) // 8
                for b_idx in range(8):
                    bx = sx + 12 + b_idx * (bw + 6)
                    by = hy + 10
                    active = b_idx == r_idx
                    fill_c = (48, 30, 22, 255) if active else (13, 18, 30, 255)
                    out_c = (249, 115, 22, 255) if active else (42, 54, 80, 255)
                    draw.rounded_rectangle([bx, by, bx + bw, by + 84], radius=7, fill=fill_c, outline=out_c, width=2 if active else 1)
                    key_lbl = anims[b_idx].get("key", f"R{b_idx + 1}")
                    draw.text((bx + 5, by + 4), key_lbl[:7], fill=(251, 146, 60, 255) if active else (148, 163, 184, 255), font=f_btn_k)
                    icon = frames_64[b_idx * 8 + 4].resize((48, 48), Image.Resampling.NEAREST)
                    frame.alpha_composite(icon, (bx + (bw - 48) // 2, by + 18))
                    short_name = anims[b_idx]["name"].split("·")[-1][:4]
                    draw.text((bx + 6, by + 67), short_name, fill=(248, 250, 252, 255) if active else (148, 163, 184, 255), font=f_btn_n)

                # Right Bottom: Active Row 8-Frame Strip
                fy = 578
                draw.rounded_rectangle([sx, fy, sx + sw, fy + 120], radius=10, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
                cw_strip = (sw - 24) // 8
                for c_idx in range(8):
                    cx_s = sx + 12 + c_idx * cw_strip
                    cy_s = fy + 10
                    is_c = c_idx == col
                    draw.rounded_rectangle(
                        [cx_s + 2, cy_s, cx_s + cw_strip - 2, cy_s + 100],
                        radius=6,
                        fill=(20, 42, 64, 255) if is_c else (13, 18, 30, 255),
                        outline=(56, 189, 248, 255) if is_c else (36, 48, 72, 255),
                        width=2 if is_c else 1,
                    )
                    thumb = frames_64[r_idx * 8 + c_idx].resize((64, 64), Image.Resampling.NEAREST)
                    frame.alpha_composite(thumb, (cx_s + (cw_strip - 64) // 2, cy_s + 26))
                    draw.text((cx_s + 7, cy_s + 5), f"#{c_idx + 1}", fill=(56, 189, 248, 255) if is_c else (100, 116, 139, 255), font=f_btn_k)

                buf = io.BytesIO()
                frame.convert("RGB").save(buf, format="JPEG", quality=92)
                proc.stdin.write(buf.getvalue())
                total_frames += 1

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed (exit {ret}): {stderr_out[-500:]}")
    print(f"[SHOWCASE] Rendered {out_mp4} ({total_frames} frames @ {fps_video} FPS, {out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
    return out_mp4
