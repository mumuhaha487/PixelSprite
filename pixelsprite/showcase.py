"""Pixel-perfect 60 FPS MP4 showcase renderer (v2.1 — crisp 64x64 zero-teleport stage, 3x loops, proportional Hitstop timeline & Loop Seam Audit)."""

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


def _pick_frame_by_time(durations_ms: list[int], elapsed_ms: float) -> tuple[int, float]:
    total = sum(durations_ms)
    t = elapsed_ms % max(1, total)
    acc = 0.0
    for idx, d in enumerate(durations_ms):
        if t < acc + d:
            return idx, (t - acc) / max(1, d)
        acc += d
    return len(durations_ms) - 1, 1.0


def render_variable_timing_showcase_mp4(
    clips: list[dict[str, Any]],
    out_mp4: Path,
    fps_video: int = 60,
) -> Path:
    W, H = 1280, 720
    f_title = _load_font(19, bold=True)
    f_sub = _load_font(12, bold=False)
    f_h2 = _load_font(16, bold=True)
    f_lbl = _load_font(12, bold=True)
    f_sm = _load_font(11, bold=False)

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps_video), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-movflags", "+faststart",
            str(out_mp4),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert proc.stdin is not None
    ground_offset = 0.0
    total_written = 0

    for clip in clips:
        active: list[Image.Image] = clip["active_frames"]
        ghost: Image.Image | None = clip.get("ghost_frame")
        all_audit = active + ([ghost] if ghost is not None else [])
        n_act = len(active)
        cell_size = active[0].width
        durations: list[int] = clip["durations_ms"]
        hold_tags: dict[int, str] = {int(k): v for k, v in clip.get("hold_tags", {}).items()}
        timing_mode: str = clip.get("timing_mode", "even")
        seam: dict = clip.get("seam_metrics", {})
        scroll_speed: float = float(clip.get("scroll_speed", 0))
        loops: int = int(clip.get("loops", 3))

        g_cols = int(clip.get("audit_grid_cols", len(all_audit)))
        g_rows = int(clip.get("audit_grid_rows", 1))
        audit_atlas = Image.new("RGBA", (g_cols * cell_size, g_rows * cell_size), (0, 0, 0, 0))
        for i, im in enumerate(all_audit):
            audit_atlas.paste(im, ((i % g_cols) * cell_size, (i // g_cols) * cell_size))

        box_w, box_h = 584, 372
        cell_px = min(box_w // g_cols, box_h // g_rows)
        grid_disp_w, grid_disp_h = cell_px * g_cols, cell_px * g_rows
        audit_chk = make_checkerboard_preview(audit_atlas, scale=3).resize((grid_disp_w, grid_disp_h), Image.Resampling.NEAREST)

        cycle_ms = sum(durations)
        total_ms = cycle_ms * loops
        n_vid_frames = max(60, int(round((total_ms / 1000.0) * fps_video)))

        for vf in range(n_vid_frames):
            elapsed_ms = (vf / fps_video) * 1000.0
            cur_idx, _ = _pick_frame_by_time(durations, elapsed_ms)
            ground_offset += scroll_speed / fps_video

            frame = Image.new("RGBA", (W, H), (12, 16, 24, 255))
            draw = ImageDraw.Draw(frame, "RGBA")

            # Header
            draw.rectangle([0, 0, W, 60], fill=(17, 23, 37, 255))
            draw.line([(0, 60), (W, 60)], fill=(34, 47, 71, 255), width=2)
            draw.rounded_rectangle([24, 13, 74, 47], radius=8, fill=(56, 189, 248, 255))
            draw.text((32, 20), "v2.1", fill=(5, 20, 34, 255), font=f_lbl)
            draw.text((86, 11), "PixelSprite v2.1 · 角色主体锁位零瞬移 × N+1 闭环校对 × 非均匀顿帧", fill=(248, 250, 252, 255), font=f_title)
            draw.text(
                (86, 37),
                f"{clip['title']} | {cell_size}x{cell_size}画布(角色恒定34px高) | 有效 {n_act} 帧 + 第{n_act+1}帧闭环校对已剔除 | 单轮 {cycle_ms}ms",
                fill=(148, 163, 184, 255),
                font=f_sub,
            )

            # === LEFT TOP: N+1 AUDIT GRID ===
            lx, ly, lw, lh = 24, 76, 608, 424
            draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            draw.text(
                (lx + 14, ly + 10),
                f"1. 闭环生成网格（{g_cols}x{g_rows}={len(all_audit)}格：橙框=当前播放 · 红框=第{n_act+1}帧[=F1/不计入循环]）",
                fill=(226, 232, 240, 255),
                font=f_lbl,
            )

            gx = lx + (lw - grid_disp_w) // 2
            gy = ly + 36 + (box_h - grid_disp_h) // 2
            frame.paste(audit_chk, (gx, gy))

            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov, "RGBA")
            if ghost is not None:
                gi = len(all_audit) - 1
                gr, gc = gi // g_cols, gi % g_cols
                x0, y0 = gx + gc * cell_px, gy + gr * cell_px
                od.rectangle([x0, y0, x0 + cell_px - 1, y0 + cell_px - 1], fill=(244, 63, 94, 52), outline=(244, 63, 94, 255), width=3)
                od.text((x0 + 4, y0 + 3), f"#{gi+1}=F1", fill=(255, 220, 225, 255), font=f_sm)

            cr, cc = cur_idx // g_cols, cur_idx % g_cols
            cx0, cy0 = gx + cc * cell_px, gy + cr * cell_px
            od.rectangle([cx0 + 1, cy0 + 1, cx0 + cell_px - 2, cy0 + cell_px - 2], fill=(249, 115, 22, 38), outline=(249, 115, 22, 255), width=3)
            frame.alpha_composite(ov)

            # === LEFT BOTTOM: LOOP SEAM & STABILITY METRICS ===
            sy_l, sh_l = 514, 186
            draw.rounded_rectangle([lx, sy_l, lx + lw, sy_l + sh_l], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            fn_g = seam.get("fN_vs_ghost_rgb", seam.get("fN_vs_ghost_iou", 0))
            g_f1 = seam.get("ghost_vs_f1_rgb", seam.get("ghost_vs_f1_iou", 0))
            fn_f1 = seam.get("fN_vs_f1_rgb", seam.get("fN_vs_f1_iou", 0))
            mdx = seam.get("max_body_dx_px", 0.0)
            draw.text(
                (lx + 14, sy_l + 10),
                f"2. 首尾核验：F{n_act}<->F{n_act+1} {int(fn_g*100)}% | F{n_act+1}<->F1 {int(g_f1*100)}% | 回环F{n_act}->F1 {int(fn_f1*100)}% | 最大X偏移 {mdx:.1f}px",
                fill=(74, 222, 128, 255),
                font=f_lbl,
            )

            seam_cards = [
                (f"F{n_act - 1} (倒数第2帧)", active[-2], (148, 163, 184, 255), False),
                (f"F{n_act} (最终末帧)", active[-1], (74, 222, 128, 255), False),
                (f"F{n_act + 1} (幽灵=F1/剔除)", ghost or active[0], (244, 63, 94, 255), True),
                ("F1 (下轮首帧)", active[0], (56, 189, 248, 255), False),
            ]
            card_w, gap, start_x = 132, 16, lx + 16
            for k, (lbl, im_c, col_b, is_gh) in enumerate(seam_cards):
                bx = start_x + k * (card_w + gap)
                by = sy_l + 38
                draw.rounded_rectangle([bx, by, bx + card_w, by + 134], radius=8, fill=(38, 18, 28, 255) if is_gh else (13, 18, 30, 255), outline=col_b, width=2)
                draw.text((bx + 8, by + 6), lbl, fill=col_b, font=f_sm)
                thumb = im_c.resize((96, 96), Image.Resampling.NEAREST)
                frame.alpha_composite(thumb, (bx + (card_w - 96) // 2, by + 28))
                if k < 3:
                    draw.text((bx + card_w + 3, by + 66), "->", fill=(148, 163, 184, 255), font=f_lbl)

            # === RIGHT TOP: LARGE 5x NEAREST-NEIGHBOR LIVE STAGE ===
            rx, ry, rw, rh = 652, 76, 604, 424
            draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12, fill=(18, 25, 40, 255), outline=(44, 61, 94, 255), width=2)
            ix, iy, iw, ih = rx + 8, ry + 8, rw - 16, rh - 16
            floor_y = iy + ih - 62
            draw.rectangle([ix, iy, ix + iw, floor_y], fill=(24, 38, 64, 255))
            draw.rectangle([ix, floor_y, ix + iw, iy + ih], fill=(32, 54, 50, 255))

            tile = 32
            off = int(ground_offset) % tile
            for tx_g in range(ix - tile, ix + iw + tile, tile):
                tx = tx_g - off
                if tx + 16 > ix and tx < ix + iw:
                    draw.rectangle([max(ix, tx), floor_y, min(ix + iw, tx + 16), floor_y + 8], fill=(44, 76, 68, 255))
                if tx + 32 > ix and tx + 16 < ix + iw:
                    draw.rectangle([max(ix, tx + 16), floor_y + 12, min(ix + iw, tx + 32), floor_y + 18], fill=(40, 68, 62, 255))

            stage_body_x = rx + int(rw * 0.45)
            sh_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh_ov, "RGBA").ellipse([stage_body_x - 54, floor_y - 2, stage_body_x + 54, floor_y + 14], fill=(10, 15, 24, 125))
            frame.alpha_composite(sh_ov)

            zoom = 5 if cell_size <= 64 else 4
            draw_sz = cell_size * zoom  # 64*5 = 320px crisp nearest-neighbor!
            cur_sp = active[cur_idx].resize((draw_sz, draw_sz), Image.Resampling.NEAREST)
            anchor_x_ratio = float(clip.get("anchor_x_ratio", 0.44))
            body_off_x = int(round(cell_size * anchor_x_ratio)) * zoom
            foot_off = int(round(cell_size * 0.90)) * zoom
            frame.alpha_composite(cur_sp, (stage_body_x - body_off_x, floor_y + 6 - foot_off))

            draw.rounded_rectangle([ix + 14, iy + 14, ix + 325, iy + 52], radius=8, fill=(10, 15, 28, 255), outline=(56, 189, 248, 255), width=1)
            draw.text((ix + 24, iy + 22), f"{clip['title']}", fill=(56, 189, 248, 255), font=f_h2)

            cur_ms = durations[cur_idx]
            hold_label = hold_tags.get(cur_idx + 1)
            if hold_label:
                pill_fill, pill_out, pill_fg = (62, 34, 14, 255), (251, 191, 36, 255), (253, 224, 71, 255)
                pill_txt = f"[定帧] {hold_label} ({cur_ms}ms)"
            elif timing_mode == "even":
                pill_fill, pill_out, pill_fg = (14, 42, 34, 255), (74, 222, 128, 255), (134, 239, 172, 255)
                pill_txt = f"[匀速] F{cur_idx + 1}/{n_act} ({cur_ms}ms)"
            else:
                pill_fill, pill_out, pill_fg = (14, 28, 48, 255), (56, 189, 248, 255), (186, 230, 253, 255)
                pill_txt = f"[快切] F{cur_idx + 1}/{n_act} ({cur_ms}ms)"

            draw.rounded_rectangle([ix + iw - 238, iy + 14, ix + iw - 14, iy + 50], radius=8, fill=pill_fill, outline=pill_out, width=2)
            draw.text((ix + iw - 226, iy + 24), pill_txt, fill=pill_fg, font=f_lbl)

            # === RIGHT BOTTOM: PROPORTIONAL VARIABLE-TIMING TIMELINE BAR ===
            ty, th = 514, 186
            draw.rounded_rectangle([rx, ty, rx + rw, ty + th], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            mode_desc = "匀速节奏（走路/疾跑不停顿）" if timing_mode == "even" else "非均匀时间轴（橙宽块=蓄力/HITSTOP/定格 · 蓝窄块=快切爆发）"
            draw.text((rx + 14, ty + 10), f"3. 帧时间轴：{mode_desc}", fill=(226, 232, 240, 255), font=f_lbl)

            bar_x, bar_y, bar_w, bar_h = rx + 14, ty + 38, rw - 28, 56
            cursor_x = float(bar_x)
            for idx_f, d_ms in enumerate(durations):
                seg_w = (d_ms / max(1, cycle_ms)) * bar_w
                x0, x1 = int(round(cursor_x)), int(round(cursor_x + seg_w)) - 2
                cursor_x += seg_w
                is_hold = (idx_f + 1) in hold_tags
                is_cur = idx_f == cur_idx
                if is_cur:
                    fc, oc = ((180, 95, 18, 255), (253, 224, 71, 255)) if is_hold else ((22, 82, 130, 255), (56, 189, 248, 255))
                else:
                    fc, oc = ((62, 38, 18, 255), (217, 119, 6, 255)) if is_hold else ((15, 22, 36, 255), (42, 56, 84, 255))
                draw.rounded_rectangle([x0, bar_y, max(x0 + 4, x1), bar_y + bar_h], radius=5, fill=fc, outline=oc, width=2 if is_cur else 1)
                if x1 - x0 >= 22:
                    draw.text((x0 + 4, bar_y + 6), f"F{idx_f + 1}", fill=(248, 250, 252, 255), font=f_sm)
                if x1 - x0 >= 32:
                    draw.text((x0 + 4, bar_y + 24), f"{d_ms}", fill=(253, 224, 71, 255) if is_hold else (148, 163, 184, 255), font=f_sm)
                if is_hold and (x1 - x0) >= 48:
                    draw.text((x0 + 4, bar_y + 39), hold_tags[idx_f + 1][:4], fill=(253, 224, 71, 255), font=f_sm)

            strip_y = ty + 106
            t_slot = bar_w // n_act
            t_sz = min(64, max(36, t_slot - 4))
            for idx_f in range(n_act):
                tx0 = bar_x + idx_f * t_slot
                is_cur = idx_f == cur_idx
                is_hold = (idx_f + 1) in hold_tags
                draw.rounded_rectangle(
                    [tx0 + 1, strip_y, tx0 + t_slot - 2, strip_y + 68],
                    radius=5,
                    fill=(24, 46, 72, 255) if is_cur else (13, 18, 30, 255),
                    outline=(251, 191, 36, 255) if (is_cur and is_hold) else ((56, 189, 248, 255) if is_cur else (34, 46, 68, 255)),
                    width=2 if is_cur else 1,
                )
                im_t = active[idx_f].resize((t_sz, t_sz), Image.Resampling.NEAREST)
                frame.alpha_composite(im_t, (tx0 + (t_slot - t_sz) // 2, strip_y + (68 - t_sz) // 2))

            buf = io.BytesIO()
            frame.convert("RGB").save(buf, format="JPEG", quality=92)
            proc.stdin.write(buf.getvalue())
            total_written += 1

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed (exit {ret}): {stderr_out[-500:]}")
    print(f"[SHOWCASE v2.1] Rendered {out_mp4} ({total_written} frames @ {fps_video} FPS, {out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
    return out_mp4
