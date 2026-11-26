"""Pixel-perfect 60 FPS MP4 showcase renderer (v2.2 — Wide 96x80 Arena, Live Hitbox/Hurtbox HUD, Startup/Active/Recovery Timeline & Closed-Loop Audit)."""

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
    show_hitboxes: bool = True,
) -> Path:
    W, H = 1280, 720
    f_title = _load_font(18, bold=True)
    f_sub = _load_font(12, bold=False)
    f_h2 = _load_font(15, bold=True)
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
        cw, ch = active[0].size
        durations: list[int] = clip["durations_ms"]
        hold_tags: dict[int, str] = {int(k): v for k, v in clip.get("hold_tags", {}).items()}
        timing_mode: str = clip.get("timing_mode", "even")
        seam: dict = clip.get("seam_metrics", {})
        frame_data: list[dict[str, Any]] = clip.get("frame_data", [])
        combat_sum: dict[str, Any] = clip.get("combat_summary", {})
        pivot: list[int] = clip.get("pivot", [int(cw * 0.3125), int(ch * 0.89)])
        scroll_speed: float = float(clip.get("scroll_speed", 0))
        loops: int = int(clip.get("loops", 3))

        g_cols = int(clip.get("audit_grid_cols", len(all_audit)))
        g_rows = int(clip.get("audit_grid_rows", 1))
        audit_atlas = Image.new("RGBA", (g_cols * cw, g_rows * ch), (0, 0, 0, 0))
        for i, im in enumerate(all_audit):
            audit_atlas.paste(im, ((i % g_cols) * cw, (i // g_cols) * ch))

        box_w, box_h = 584, 372
        grid_scale = min(box_w / (g_cols * cw), box_h / (g_rows * ch))
        cell_dw = max(16, int(cw * grid_scale))
        cell_dh = max(16, int(ch * grid_scale))
        grid_disp_w, grid_disp_h = cell_dw * g_cols, cell_dh * g_rows
        audit_chk = make_checkerboard_preview(audit_atlas, scale=2).resize((grid_disp_w, grid_disp_h), Image.Resampling.NEAREST)

        cycle_ms = sum(durations)
        total_ms = cycle_ms * loops
        n_vid_frames = max(60, int(round((total_ms / 1000.0) * fps_video)))

        for vf in range(n_vid_frames):
            elapsed_ms = (vf / fps_video) * 1000.0
            cur_idx, _ = _pick_frame_by_time(durations, elapsed_ms)
            ground_offset += scroll_speed / fps_video
            cur_fd = frame_data[cur_idx] if cur_idx < len(frame_data) else None
            cur_phase = cur_fd["phase"] if cur_fd else "neutral"
            is_attack = bool(cur_fd and cur_fd.get("isAttackFrame"))

            frame = Image.new("RGBA", (W, H), (12, 16, 24, 255))
            draw = ImageDraw.Draw(frame, "RGBA")

            # Header
            draw.rectangle([0, 0, W, 60], fill=(17, 23, 37, 255))
            draw.line([(0, 60), (W, 60)], fill=(34, 47, 71, 255), width=2)
            draw.rounded_rectangle([24, 13, 74, 47], radius=8, fill=(239, 68, 68, 255) if is_attack else (56, 189, 248, 255))
            draw.text((32, 20), "v2.2", fill=(255, 255, 255, 255) if is_attack else (5, 20, 34, 255), font=f_lbl)
            draw.text((86, 11), "PixelSprite v2.2 · 宽画布华丽特效 × 攻击判定框/攻击帧数据 × N+1闭环零瞬移", fill=(248, 250, 252, 255), font=f_title)
            draw.text(
                (86, 37),
                f"{clip['title']} | {cw}x{ch}宽画布(角色恒定34px) | 有效 {n_act} 帧 + 第{n_act+1}帧闭环已剔除 | 绿框=受击框 · 红框=攻击判定框",
                fill=(148, 163, 184, 255),
                font=f_sub,
            )

            # === LEFT TOP: N+1 AUDIT GRID ===
            lx, ly, lw, lh = 24, 76, 608, 424
            draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            draw.text(
                (lx + 14, ly + 10),
                f"1. 闭环生成网格（{g_cols}x{g_rows}={len(all_audit)}格：橙框=播放 · 红角标=攻击判定帧 · 红遮罩=第{n_act+1}帧[剔除]）",
                fill=(226, 232, 240, 255),
                font=f_lbl,
            )

            gx = lx + (lw - grid_disp_w) // 2
            gy = ly + 36 + (box_h - grid_disp_h) // 2
            frame.paste(audit_chk, (gx, gy))

            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov, "RGBA")
            # Mark every active attack frame with a crisp red corner dot
            for fi_a, fd_a in enumerate(frame_data):
                if fd_a.get("isAttackFrame"):
                    ar, ac = fi_a // g_cols, fi_a % g_cols
                    ax0, ay0 = gx + ac * cell_dw, gy + ar * cell_dh
                    od.rectangle([ax0 + 3, ay0 + 3, ax0 + 28, ay0 + 16], fill=(220, 38, 38, 230))
                    od.text((ax0 + 5, ay0 + 2), f"H{fd_a['hitId']}", fill=(255, 255, 255, 255), font=f_sm)

            if ghost is not None:
                gi = len(all_audit) - 1
                gr, gc = gi // g_cols, gi % g_cols
                x0, y0 = gx + gc * cell_dw, gy + gr * cell_dh
                od.rectangle([x0, y0, x0 + cell_dw - 1, y0 + cell_dh - 1], fill=(244, 63, 94, 52), outline=(244, 63, 94, 255), width=3)
                od.text((x0 + 4, y0 + 3), f"#{gi+1}=F1", fill=(255, 220, 225, 255), font=f_sm)

            cr, cc = cur_idx // g_cols, cur_idx % g_cols
            cx0, cy0 = gx + cc * cell_dw, gy + cr * cell_dh
            od.rectangle([cx0 + 1, cy0 + 1, cx0 + cell_dw - 2, cy0 + cell_dh - 2], fill=(249, 115, 22, 34), outline=(251, 146, 60, 255), width=3)
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
            t_sc = min(116 / cw, 96 / ch)
            tw, th_img = max(16, int(cw * t_sc)), max(16, int(ch * t_sc))
            for k, (lbl, im_c, col_b, is_gh) in enumerate(seam_cards):
                bx = start_x + k * (card_w + gap)
                by = sy_l + 38
                draw.rounded_rectangle([bx, by, bx + card_w, by + 134], radius=8, fill=(38, 18, 28, 255) if is_gh else (13, 18, 30, 255), outline=col_b, width=2)
                draw.text((bx + 8, by + 6), lbl, fill=col_b, font=f_sm)
                thumb = im_c.resize((tw, th_img), Image.Resampling.NEAREST)
                frame.alpha_composite(thumb, (bx + (card_w - tw) // 2, by + 26 + (100 - th_img) // 2))
                if k < 3:
                    draw.text((bx + card_w + 3, by + 66), "->", fill=(148, 163, 184, 255), font=f_lbl)

            # === RIGHT TOP: LARGE 4x NEAREST-NEIGHBOR WIDE COMBAT ARENA + LIVE HITBOX/HURTBOX OVERLAY ===
            rx, ry, rw, rh = 652, 76, 604, 424
            stage_border = (239, 68, 68, 255) if is_attack else (44, 61, 94, 255)
            draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12, fill=(18, 25, 40, 255), outline=stage_border, width=2)
            ix, iy, iw, ih = rx + 8, ry + 8, rw - 16, rh - 16
            floor_y = iy + ih - 66
            sky_col = (34, 24, 52, 255) if (is_attack and cur_idx + 1 in hold_tags) else (22, 34, 58, 255)
            draw.rectangle([ix, iy, ix + iw, floor_y], fill=sky_col)
            draw.rectangle([ix, floor_y, ix + iw, iy + ih], fill=(30, 50, 48, 255))

            tile = 32
            off = int(ground_offset) % tile
            for tx_g in range(ix - tile, ix + iw + tile, tile):
                tx = tx_g - off
                if tx + 16 > ix and tx < ix + iw:
                    draw.rectangle([max(ix, tx), floor_y, min(ix + iw, tx + 16), floor_y + 8], fill=(44, 76, 68, 255))
                if tx + 32 > ix and tx + 16 < ix + iw:
                    draw.rectangle([max(ix, tx + 16), floor_y + 12, min(ix + iw, tx + 32), floor_y + 18], fill=(40, 68, 62, 255))

            # Unified character pivot X in left-third of stage so HUGE 66px VFX unfolds cleanly right!
            stage_body_x = rx + int(rw * 0.32)
            zoom = 4 if cw >= 80 else 5
            draw_w, draw_h = cw * zoom, ch * zoom  # 96*4=384 x 80*4=320 crisp nearest-neighbor!
            sp_x0 = stage_body_x - pivot[0] * zoom
            sp_y0 = floor_y + 6 - pivot[1] * zoom

            sh_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh_ov, "RGBA").ellipse([stage_body_x - 48, floor_y - 2, stage_body_x + 48, floor_y + 13], fill=(10, 15, 24, 130))
            frame.alpha_composite(sh_ov)

            cur_sp = active[cur_idx].resize((draw_w, draw_h), Image.Resampling.NEAREST)
            frame.alpha_composite(cur_sp, (sp_x0, sp_y0))

            # LIVE HITBOX & HURTBOX OVERLAY (Translucent Green Hurtbox + Flashing Red Attack Hitboxes!)
            if show_hitboxes and cur_fd:
                box_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                bd = ImageDraw.Draw(box_ov, "RGBA")
                hb = cur_fd["hurtbox"]
                hx0, hy0 = sp_x0 + hb["x"] * zoom, sp_y0 + hb["y"] * zoom
                hx1, hy1 = sp_x0 + (hb["x"] + hb["w"]) * zoom, sp_y0 + (hb["y"] + hb["h"]) * zoom
                bd.rectangle([hx0, hy0, hx1, hy1], fill=(34, 197, 94, 24), outline=(74, 222, 128, 220), width=2)
                bd.text((hx0 + 3, hy0 - 15), "HURT", fill=(134, 239, 172, 240), font=f_sm)

                for atk in cur_fd["hitboxes"]:
                    ax0, ay0 = sp_x0 + atk["x"] * zoom, sp_y0 + atk["y"] * zoom
                    ax1, ay1 = sp_x0 + (atk["x"] + atk["w"]) * zoom, sp_y0 + (atk["y"] + atk["h"]) * zoom
                    bd.rectangle([ax0, ay0, ax1, ay1], fill=(239, 68, 68, 44), outline=(255, 72, 72, 255), width=3)
                    for cx_p, cy_p in ((ax0, ay0), (ax1, ay0), (ax0, ay1), (ax1, ay1)):
                        bd.rectangle([cx_p - 3, cy_p - 3, cx_p + 3, cy_p + 3], fill=(254, 240, 138, 255))
                    bd.rectangle([ax0, max(iy + 56, ay0 - 18), ax0 + 148, max(iy + 74, ay0)], fill=(185, 28, 28, 235))
                    bd.text((ax0 + 5, max(iy + 57, ay0 - 17)), f"ACTIVE HIT#{cur_fd['hitId']} DMG:{cur_fd['damage']}", fill=(255, 255, 255, 255), font=f_sm)

                frame.alpha_composite(box_ov)

            # Stage Title & Live Combat Phase Pill
            draw.rounded_rectangle([ix + 12, iy + 12, ix + 318, iy + 48], radius=8, fill=(10, 15, 28, 255), outline=(56, 189, 248, 255), width=1)
            draw.text((ix + 22, iy + 20), f"{clip['title']}", fill=(56, 189, 248, 255), font=f_h2)

            cur_ms = durations[cur_idx]
            hold_label = hold_tags.get(cur_idx + 1)
            if is_attack and hold_label:
                pill_fill, pill_out, pill_fg = (127, 29, 29, 255), (253, 224, 71, 255), (254, 240, 138, 255)
                pill_txt = f"[判定定帧] HIT#{cur_fd['hitId']} ({cur_ms}ms)"
            elif is_attack:
                pill_fill, pill_out, pill_fg = (127, 29, 29, 255), (248, 113, 113, 255), (254, 202, 202, 255)
                pill_txt = f"[攻击判定] HIT#{cur_fd['hitId']} ({cur_ms}ms)"
            elif cur_phase == "startup":
                pill_fill, pill_out, pill_fg = (62, 38, 12, 255), (245, 158, 11, 255), (253, 230, 138, 255)
                pill_txt = f"[前摇] {hold_label or f'F{cur_idx+1}'} ({cur_ms}ms)"
            elif cur_phase == "recovery":
                pill_fill, pill_out, pill_fg = (14, 34, 58, 255), (56, 189, 248, 255), (186, 230, 253, 255)
                pill_txt = f"[后摇] {hold_label or f'F{cur_idx+1}'} ({cur_ms}ms)"
            elif timing_mode == "even":
                pill_fill, pill_out, pill_fg = (14, 42, 34, 255), (74, 222, 128, 255), (134, 239, 172, 255)
                pill_txt = f"[匀速] F{cur_idx + 1}/{n_act} ({cur_ms}ms)"
            else:
                pill_fill, pill_out, pill_fg = (32, 38, 54, 255), (148, 163, 184, 255), (226, 232, 240, 255)
                pill_txt = f"[常态] {hold_label or f'F{cur_idx+1}'} ({cur_ms}ms)"

            draw.rounded_rectangle([ix + iw - 246, iy + 12, ix + iw - 12, iy + 48], radius=8, fill=pill_fill, outline=pill_out, width=2)
            draw.text((ix + iw - 234, iy + 22), pill_txt, fill=pill_fg, font=f_lbl)

            # Bottom-of-Stage Live Frame-Data Telemetry Strip
            if combat_sum.get("hasAttack"):
                hb_txt = (
                    f"HITBOX {cur_fd['hitboxes'][0]['w']}x{cur_fd['hitboxes'][0]['h']}px · DMG {cur_fd['damage']} · 击退{cur_fd['knockback']}"
                    if (cur_fd and cur_fd["hitboxes"])
                    else f"当前阶段: {cur_phase.upper()} (无攻击判定框)"
                )
                stat_line = (
                    f"帧数据: 前摇{len(combat_sum['startupFrames'])}f({combat_sum['startupMs']}ms) | "
                    f"攻击判定{len(combat_sum['activeFrames'])}f({combat_sum['activeMs']}ms/{combat_sum['totalHitCount']}段) | "
                    f"后摇{len(combat_sum['recoveryFrames'])}f | 射程{combat_sum['maxReachPx']}px | {hb_txt}"
                )
            else:
                h_box = cur_fd["hurtbox"] if cur_fd else {"w": 0, "h": 0}
                stat_line = f"移动/常态帧: 受击框 HURTBOX {h_box['w']}x{h_box['h']}px | 无攻击判定帧 | 匀速零卡顿循环"
            draw.rectangle([ix, iy + ih - 24, ix + iw, iy + ih], fill=(10, 15, 26, 235))
            draw.text((ix + 10, iy + ih - 20), stat_line, fill=(254, 202, 202, 255) if is_attack else (148, 163, 184, 255), font=f_sm)

            # === RIGHT BOTTOM: PROPORTIONAL COMBAT FRAME-DATA TIMELINE BAR ===
            ty, th = 514, 186
            draw.rounded_rectangle([rx, ty, rx + rw, ty + th], radius=12, fill=(18, 25, 40, 255), outline=(41, 55, 82, 255), width=2)
            mode_desc = (
                "匀速节奏（走路/疾跑无停顿）"
                if timing_mode == "even"
                else "攻击帧时间轴（橙=前摇 · 红=攻击判定ACTIVE · 蓝=后摇 · 块宽=毫秒时长）"
            )
            draw.text((rx + 14, ty + 10), f"3. 帧数据时间轴：{mode_desc}", fill=(226, 232, 240, 255), font=f_lbl)

            bar_x, bar_y, bar_w, bar_h = rx + 14, ty + 38, rw - 28, 56
            cursor_x = float(bar_x)
            for idx_f, d_ms in enumerate(durations):
                seg_w = (d_ms / max(1, cycle_ms)) * bar_w
                x0, x1 = int(round(cursor_x)), int(round(cursor_x + seg_w)) - 2
                cursor_x += seg_w
                fd_i = frame_data[idx_f] if idx_f < len(frame_data) else None
                ph = fd_i["phase"] if fd_i else "neutral"
                is_hold = (idx_f + 1) in hold_tags
                is_cur = idx_f == cur_idx

                if ph == "active":
                    fc = (185, 28, 28, 255) if is_cur else (92, 20, 26, 255)
                    oc = (253, 224, 71, 255) if (is_cur or is_hold) else (239, 68, 68, 255)
                elif ph == "startup":
                    fc = (160, 88, 14, 255) if is_cur else (62, 38, 16, 255)
                    oc = (253, 224, 71, 255) if is_cur else (217, 119, 6, 255)
                elif ph == "recovery":
                    fc = (22, 82, 130, 255) if is_cur else (16, 30, 50, 255)
                    oc = (56, 189, 248, 255) if is_cur else (51, 80, 118, 255)
                else:
                    fc = (22, 88, 70, 255) if (is_cur and timing_mode == "even") else ((28, 68, 108, 255) if is_cur else (16, 24, 38, 255))
                    oc = (74, 222, 128, 255) if (is_cur and timing_mode == "even") else ((56, 189, 248, 255) if is_cur else (42, 56, 84, 255))

                draw.rounded_rectangle([x0, bar_y, max(x0 + 4, x1), bar_y + bar_h], radius=5, fill=fc, outline=oc, width=2 if is_cur else 1)
                if x1 - x0 >= 22:
                    draw.text((x0 + 4, bar_y + 5), f"F{idx_f + 1}", fill=(248, 250, 252, 255), font=f_sm)
                if x1 - x0 >= 30:
                    draw.text((x0 + 4, bar_y + 22), f"{d_ms}", fill=(254, 240, 138, 255) if (ph == "active" or is_hold) else (148, 163, 184, 255), font=f_sm)
                if (x1 - x0) >= 44:
                    sub_tag = f"HIT#{fd_i['hitId']}" if (fd_i and fd_i["isAttackFrame"]) else (hold_tags[idx_f + 1][:4] if is_hold else "")
                    if sub_tag:
                        draw.text((x0 + 4, bar_y + 38), sub_tag, fill=(254, 240, 138, 255), font=f_sm)

            strip_y = ty + 106
            t_slot = bar_w // n_act
            t_scale = min((t_slot - 4) / cw, 62 / ch)
            tsw, tsh = max(16, int(cw * t_scale)), max(16, int(ch * t_scale))
            for idx_f in range(n_act):
                tx0 = bar_x + idx_f * t_slot
                is_cur = idx_f == cur_idx
                fd_i = frame_data[idx_f] if idx_f < len(frame_data) else None
                is_atk_f = bool(fd_i and fd_i.get("isAttackFrame"))
                draw.rounded_rectangle(
                    [tx0 + 1, strip_y, tx0 + t_slot - 2, strip_y + 68],
                    radius=5,
                    fill=(68, 20, 26, 255) if (is_cur and is_atk_f) else ((24, 46, 72, 255) if is_cur else ((34, 16, 22, 255) if is_atk_f else (13, 18, 30, 255))),
                    outline=(253, 224, 71, 255) if (is_cur and is_atk_f) else ((239, 68, 68, 220) if is_atk_f else ((56, 189, 248, 255) if is_cur else (34, 46, 68, 255))),
                    width=2 if (is_cur or is_atk_f) else 1,
                )
                im_t = active[idx_f].resize((tsw, tsh), Image.Resampling.NEAREST)
                frame.alpha_composite(im_t, (tx0 + (t_slot - tsw) // 2, strip_y + (68 - tsh) // 2))

            buf = io.BytesIO()
            frame.convert("RGB").save(buf, format="JPEG", quality=92)
            proc.stdin.write(buf.getvalue())
            total_written += 1

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed (exit {ret}): {stderr_out[-500:]}")
    print(f"[SHOWCASE v2.2] Rendered {out_mp4} ({total_written} frames @ {fps_video} FPS, {out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
    return out_mp4
