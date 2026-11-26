"""Pixel-perfect 60 FPS MP4 showcase renderer supporting Variable Frame Counts, Selective Keyframe Holds/Hitstop, and Closed-Loop N+1 Seam Audits."""

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
    """
    Render a 60 FPS 1280x720 pixel-perfect showcase displaying:
      - Left Top: Full N+1 Audit Grid (with Ghost Frame N+1 marked in red = EXCLUDED from loop!)
      - Left Bottom: Closed-Loop Seam Check Strip [F[N-1] -> F[N] -> (Ghost F[N+1]=F1) -> F[1]] + IoU Continuity Scores!
      - Right Top: 6x crisp nearest-neighbor live playback at EXACT millisecond `frameDurationsMs` + live HOLD/HITSTOP indicator!
      - Right Bottom: Proportional Variable-Timing Bar (block width = ms duration!) proving uneven combat holds vs smooth even walk/run!
    Each clip dict:
      {
        "title": str,
        "subtitle": str,
        "active_frames": list[PIL.Image],       # N frames (Ghost excluded!)
        "ghost_frame": PIL.Image | None,        # Frame N+1 (= F1) for audit only
        "audit_grid_cols": int,                 # e.g. 9, 4, or 5
        "audit_grid_rows": int,                 # e.g. 1 or 3
        "durations_ms": list[int],              # length N
        "hold_tags": dict[int, str],            # 1-based frame index -> Chinese hold label
        "timing_mode": "even" | "breath" | "hitstop",
        "seam_metrics": dict,
        "scroll_speed": float,
        "loops": int,
      }
    """
    W, H = 1280, 720
    f_title = _load_font(19, bold=True)
    f_sub = _load_font(12, bold=False)
    f_h2 = _load_font(16, bold=True)
    f_lbl = _load_font(12, bold=True)
    f_sm = _load_font(11, bold=False)
    f_mono = _load_font(12, bold=True)

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
        loops: int = int(clip.get("loops", 2))

        g_cols = int(clip.get("audit_grid_cols", len(all_audit)))
        g_rows = int(clip.get("audit_grid_rows", 1))
        audit_atlas = Image.new("RGBA", (g_cols * cell_size, g_rows * cell_size), (0, 0, 0, 0))
        for i, im in enumerate(all_audit):
            audit_atlas.paste(im, ((i % g_cols) * cell_size, (i // g_cols) * cell_size))

        # Fit audit grid cleanly into Left Top box (588 x 376)
        box_w, box_h = 588, 376
        cell_px = min(box_w // g_cols, box_h // g_rows)
        # Snap to integer multiple of cell_size if >= 1, else clean nearest
        grid_disp_w, grid_disp_h = cell_px * g_cols, cell_px * g_rows
        audit_chk = make_checkerboard_preview(audit_atlas, scale=4).resize((grid_disp_w, grid_disp_h), Image.Resampling.NEAREST)

        cycle_ms = sum(durations)
        total_ms = cycle_ms * loops
        n_vid_frames = max(30, int(round((total_ms / 1000.0) * fps_video)))

        for vf in range(n_vid_frames):
            elapsed_ms = (vf / fps_video) * 1000.0
            cur_idx, _ = _pick_frame_by_time(durations, elapsed_ms)
            ground_offset += scroll_speed / fps_video

            frame = Image.new("RGBA", (W, H), (12, 16, 24, 255))
            draw = ImageDraw.Draw(frame, "RGBA")

            # Header
            draw.rectangle([0, 0, W, 60], fill=(17, 23, 37, 255))
            draw.line([(0, 60), (W, 60)], fill=(34, 47, 71, 255), width=2)
            draw.rounded_rectangle([24, 13, 72, 47], radius=8, fill=(56, 189, 248, 255))
            draw.text((32, 20), "v2.0", fill=(5, 20, 34, 255), font=f_lbl)
            draw.text((84, 11), "PixelSprite v2.0 · 闭环锚点（N+1去尾）× 可变帧数 × 关键帧顿帧实测", fill=(248, 250, 252, 255), font=f_title)
            draw.text(
                (84, 37),
                f"当前动作：{clip['title']}（有效 {n_act} 帧 + 第 {n_act + 1} 帧闭环校对锚点已剔除 · 单轮耗时 {cycle_ms}ms）",
                fill=(148, 163, 184, 255),
                font=f_sub,
            )

            # === LEFT TOP: N+1 AUDIT GRID ===
            lx, ly, lw, lh = 24, 76, 608, 424
            draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            draw.text(
                (lx + 14, ly + 10),
                f"① 闭环生成核验网格（共 {len(all_audit)} 格：橙框=正在播放 · 红框=第{n_act+1}帧[同F1/不计入循环]）",
                fill=(226, 232, 240, 255),
                font=f_lbl,
            )

            gx = lx + (lw - grid_disp_w) // 2
            gy = ly + 36 + (box_h - grid_disp_h) // 2
            frame.paste(audit_chk, (gx, gy))

            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov, "RGBA")
            # Dim & outline Ghost Frame N+1 in red so user clearly sees it's excluded from playback!
            if ghost is not None:
                gi = len(all_audit) - 1
                gr, gc = gi // g_cols, gi % g_cols
                x0, y0 = gx + gc * cell_px, gy + gr * cell_px
                od.rectangle([x0, y0, x0 + cell_px - 1, y0 + cell_px - 1], fill=(244, 63, 94, 52), outline=(244, 63, 94, 255), width=3)
                od.text((x0 + 4, y0 + 3), f"#{gi+1}=F1", fill=(255, 220, 225, 255), font=f_sm)

            # Highlight currently playing active frame in bright orange!
            cr, cc = cur_idx // g_cols, cur_idx % g_cols
            cx0, cy0 = gx + cc * cell_px, gy + cr * cell_px
            od.rectangle([cx0 + 1, cy0 + 1, cx0 + cell_px - 2, cy0 + cell_px - 2], fill=(249, 115, 22, 38), outline=(249, 115, 22, 255), width=3)
            frame.alpha_composite(ov)

            # === LEFT BOTTOM: DEDICATED LOOP SEAM CHECK (F[N-1] -> F[N] -> [Ghost F[N+1]=F1] -> F[1]) ===
            sy_l = 514
            sh_l = 186
            draw.rounded_rectangle([lx, sy_l, lx + lw, sy_l + sh_l], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            fn_g = seam.get("fN_vs_ghost_iou", 0)
            g_f1 = seam.get("ghost_vs_f1_iou", 0)
            fn_f1 = seam.get("fN_vs_f1_iou", 0)
            draw.text(
                (lx + 14, sy_l + 10),
                f"② 首尾闭环重点核验：F{n_act}<->F{n_act+1} 贴合 {int(fn_g*100)}% · F{n_act+1}<->F1 一致 {int(g_f1*100)}% · 真实回环 F{n_act}->F1 贴合 {int(fn_f1*100)}%",
                fill=(74, 222, 128, 255) if fn_f1 >= 0.55 else (251, 191, 36, 255),
                font=f_lbl,
            )

            seam_cards = [
                (f"F{n_act - 1} (倒数第2帧)", active[-2], (148, 163, 184, 255), False),
                (f"F{n_act} (最终末帧)", active[-1], (74, 222, 128, 255), False),
                (f"F{n_act + 1} (幽灵=F1/剔除)", ghost or active[0], (244, 63, 94, 255), True),
                ("F1 (下轮首帧)", active[0], (56, 189, 248, 255), False),
            ]
            card_w = 132
            gap = 16
            start_x = lx + 16
            for k, (lbl, im_c, col_b, is_gh) in enumerate(seam_cards):
                bx = start_x + k * (card_w + gap)
                by = sy_l + 38
                draw.rounded_rectangle(
                    [bx, by, bx + card_w, by + 134],
                    radius=8,
                    fill=(38, 18, 28, 255) if is_gh else (13, 18, 30, 255),
                    outline=col_b,
                    width=2,
                )
                draw.text((bx + 8, by + 6), lbl, fill=col_b, font=f_sm)
                thumb = im_c.resize((96, 96), Image.Resampling.NEAREST)
                frame.alpha_composite(thumb, (bx + (card_w - 96) // 2, by + 28))
                if k < 3:
                    draw.text((bx + card_w + 2, by + 64), "→", fill=(148, 163, 184, 255), font=f_h2)

            # === RIGHT TOP: LARGE 6x LIVE STAGE WITH HITSTOP INDICATOR ===
            rx, ry, rw, rh = 652, 76, 604, 424
            draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12, fill=(18, 25, 40, 255), outline=(44, 61, 94, 255), width=2)
            ix, iy, iw, ih = rx + 8, ry + 8, rw - 16, rh - 16
            floor_y = iy + ih - 72
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

            sh_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh_ov, "RGBA").ellipse(
                [rx + rw // 2 - 54, floor_y - 2, rx + rw // 2 + 54, floor_y + 14], fill=(10, 15, 24, 125)
            )
            frame.alpha_composite(sh_ov)

            zoom = max(4, min(6, 288 // cell_size))
            draw_sz = cell_size * zoom
            cur_sp = active[cur_idx].resize((draw_sz, draw_sz), Image.Resampling.NEAREST)
            foot_off = int(round(cell_size * 0.92)) * zoom
            frame.alpha_composite(cur_sp, (rx + rw // 2 - draw_sz // 2, floor_y + 6 - foot_off))

            # Title pill
            draw.rounded_rectangle([ix + 14, iy + 14, ix + 340, iy + 54], radius=8, fill=(10, 15, 28, 255), outline=(56, 189, 248, 255), width=1)
            draw.text((ix + 24, iy + 23), f"{clip['title']}", fill=(56, 189, 248, 255), font=f_h2)

            # Live Timing / Hold / Hitstop Status Pill!
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

            draw.rounded_rectangle([ix + iw - 234, iy + 14, ix + iw - 14, iy + 50], radius=8, fill=pill_fill, outline=pill_out, width=2)
            draw.text((ix + iw - 222, iy + 24), pill_txt, fill=pill_fg, font=f_lbl)

            # === RIGHT BOTTOM: PROPORTIONAL VARIABLE-TIMING TIMELINE BAR ===
            ty = 514
            th = 186
            draw.rounded_rectangle([rx, ty, rx + rw, ty + th], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            mode_desc = (
                "匀速节奏（走路/疾跑不停顿，保持丝滑）"
                if timing_mode == "even"
                else "非均匀时间轴（橙宽块=蓄力/顿帧/定格停顿 · 蓝窄块=高速出招爆发）"
            )
            draw.text((rx + 14, ty + 10), f"③ 帧时间轴：{mode_desc}", fill=(226, 232, 240, 255), font=f_lbl)

            # Proportional duration blocks across full width (rx + 14 .. rx + rw - 14)
            bar_x = rx + 14
            bar_y = ty + 38
            bar_w = rw - 28
            bar_h = 56
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

            # Active frame mini-thumbnails strip below timing bar (up to 14 frames cleanly!)
            strip_y = ty + 106
            t_slot = bar_w // n_act
            t_sz = min(68, max(36, t_slot - 4))
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
    print(f"[SHOWCASE v2] Rendered {out_mp4} ({total_written} frames @ {fps_video} FPS, {out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
    return out_mp4


def render_showcase_mp4(sheets: list[dict[str, Any]], out_mp4: Path, fps_video: int = 30) -> Path:
    """Legacy 8x8 multi-sheet Skill-Bar HUD showcase renderer (now also honors frameDurationsMs when present!)."""
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
    total_frames = 0

    for item in sheets:
        atlas: Image.Image = item["atlas"].convert("RGBA")
        meta: dict[str, Any] = item["meta"]
        cell_size = int(meta["cellSize"])
        anims = meta["animations"]
        loops_default = int(item.get("loops_per_row", 2))
        rows_to_show = item.get("rows_to_show") or list(range(len(anims)))

        frames_64 = [
            atlas.crop((c * cell_size, r * cell_size, (c + 1) * cell_size, (r + 1) * cell_size))
            for r in range(8)
            for c in range(8)
        ]
        chk_sheet = make_checkerboard_preview(atlas, scale=4).resize((616, 616), Image.Resampling.NEAREST)
        sheet_label = meta.get("moduleNameZh") or meta.get("moduleName") or "8×8 Pixel Sprite Sheet"

        for r_idx in rows_to_show:
            anim = anims[r_idx]
            durs = anim.get("frameDurationsMs") or [int(round(1000 / max(6, int(anim.get("fps", 12)))))] * 8
            row_id = anim["id"]
            scroll_speed = 220 if row_id == "run" else (115 if row_id == "walk" or row_id.startswith("dir_") else (140 if row_id == "jump_dash" else 0))
            n_vid_frames = max(16, int(round(((sum(durs) * loops_default) / 1000.0) * fps_video)))

            for vf in range(n_vid_frames):
                col, _ = _pick_frame_by_time(durs, (vf / fps_video) * 1000.0)
                ground_offset += scroll_speed / fps_video

                frame = Image.new("RGBA", (W, H), (12, 16, 24, 255))
                draw = ImageDraw.Draw(frame, "RGBA")
                draw.rectangle([0, 0, W, 60], fill=(17, 23, 37, 255))
                draw.line([(0, 60), (W, 60)], fill=(34, 47, 71, 255), width=2)
                draw.rounded_rectangle([24, 13, 68, 47], radius=8, fill=(56, 189, 248, 255))
                draw.text((34, 20), "PX", fill=(5, 20, 34, 255), font=f_h2)
                draw.text((82, 11), f"PixelSprite · {sheet_label}", fill=(248, 250, 252, 255), font=f_title)
                draw.text((82, 37), f"{cell_size}×{cell_size} 真逻辑像素 · 支持非均匀关键帧停顿", fill=(148, 163, 184, 255), font=f_sub)

                ax, ay = 24, 78
                draw.rounded_rectangle([ax - 4, ay - 4, ax + 620, ay + 620], radius=10, fill=(20, 28, 44, 255), outline=(41, 55, 82, 255), width=2)
                frame.paste(chk_sheet, (ax, ay))
                step = 616 / 8.0
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov, "RGBA")
                od.rectangle([ax, int(ay + r_idx * step), ax + 616, int(ay + (r_idx + 1) * step)], fill=(56, 189, 248, 46))
                cx0, cy0 = int(ax + col * step), int(ay + r_idx * step)
                od.rectangle([cx0 + 1, cy0 + 1, int(cx0 + step) - 1, int(cy0 + step) - 1], outline=(249, 115, 22, 255), width=3)
                frame.alpha_composite(ov)

                sx, sy, sw, sh = 664, 78, 592, 372
                draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=12, fill=(20, 28, 44, 255), outline=(44, 61, 94, 255), width=2)
                ix, iy, iw, ih = sx + 8, sy + 8, sw - 16, sh - 16
                floor_y = iy + ih - 66
                draw.rectangle([ix, iy, ix + iw, floor_y], fill=(24, 38, 64, 255))
                draw.rectangle([ix, floor_y, ix + iw, iy + ih], fill=(32, 54, 50, 255))

                zoom = max(4, min(6, 288 // cell_size))
                draw_sz = cell_size * zoom
                cur_sprite = frames_64[r_idx * 8 + col].resize((draw_sz, draw_sz), Image.Resampling.NEAREST)
                frame.alpha_composite(cur_sprite, (sx + sw // 2 - draw_sz // 2, floor_y + 6 - int(round(cell_size * 0.92)) * zoom))

                draw.rounded_rectangle([ix + 14, iy + 14, ix + 340, iy + 54], radius=8, fill=(10, 15, 28, 255), outline=(56, 189, 248, 255), width=1)
                draw.text((ix + 26, iy + 23), f"[{anim.get('key', f'R{r_idx+1}')}] {anim['name']}", fill=(56, 189, 248, 255), font=f_h2)
                draw.rounded_rectangle([ix + iw - 156, iy + 14, ix + iw - 14, iy + 46], radius=8, fill=(10, 15, 28, 255))
                draw.text((ix + iw - 144, iy + 22), f"ROW {r_idx + 1} · {col + 1}/8", fill=(74, 222, 128, 255), font=f_mono)

                hy = 462
                draw.rounded_rectangle([sx, hy, sx + sw, hy + 104], radius=10, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
                bw = (sw - 24 - 7 * 6) // 8
                for b_idx in range(8):
                    bx = sx + 12 + b_idx * (bw + 6)
                    by = hy + 10
                    active = b_idx == r_idx
                    draw.rounded_rectangle([bx, by, bx + bw, by + 84], radius=7, fill=(48, 30, 22, 255) if active else (13, 18, 30, 255), outline=(249, 115, 22, 255) if active else (42, 54, 80, 255), width=2 if active else 1)
                    draw.text((bx + 5, by + 4), anims[b_idx].get("key", f"R{b_idx+1}")[:7], fill=(251, 146, 60, 255) if active else (148, 163, 184, 255), font=f_btn_k)
                    icon = frames_64[b_idx * 8 + 4].resize((48, 48), Image.Resampling.NEAREST)
                    frame.alpha_composite(icon, (bx + (bw - 48) // 2, by + 18))
                    draw.text((bx + 6, by + 67), anims[b_idx]["name"].split("·")[-1][:4], fill=(248, 250, 252, 255) if active else (148, 163, 184, 255), font=f_btn_n)

                fy = 578
                draw.rounded_rectangle([sx, fy, sx + sw, fy + 120], radius=10, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
                cw_strip = (sw - 24) // 8
                for c_idx in range(8):
                    cx_s = sx + 12 + c_idx * cw_strip
                    is_c = c_idx == col
                    draw.rounded_rectangle([cx_s + 2, fy + 10, cx_s + cw_strip - 2, fy + 110], radius=6, fill=(20, 42, 64, 255) if is_c else (13, 18, 30, 255), outline=(56, 189, 248, 255) if is_c else (36, 48, 72, 255), width=2 if is_c else 1)
                    thumb = frames_64[r_idx * 8 + c_idx].resize((64, 64), Image.Resampling.NEAREST)
                    frame.alpha_composite(thumb, (cx_s + (cw_strip - 64) // 2, fy + 36))
                    draw.text((cx_s + 7, fy + 15), f"#{c_idx + 1}", fill=(56, 189, 248, 255) if is_c else (100, 116, 139, 255), font=f_btn_k)

                buf = io.BytesIO()
                frame.convert("RGB").save(buf, format="JPEG", quality=92)
                proc.stdin.write(buf.getvalue())
                total_frames += 1

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed (exit {ret}): {stderr_out[-500:]}")
    print(f"[SHOWCASE] Rendered {out_mp4} ({total_frames} frames @ {fps_video} FPS)")
    return out_mp4
