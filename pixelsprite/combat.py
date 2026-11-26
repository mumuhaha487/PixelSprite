"""PixelSprite v2.2 — Automatic Pixel-Fitted Combat Frame Data (Startup/Active/Recovery, Hurtboxes & Multi-Hit Hitboxes)."""

from __future__ import annotations

from collections import deque
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .quantizer import _compute_vfx_mask, _largest_component, make_checkerboard_preview, measure_cell_anatomy


PHASE_COLORS = {
    "neutral": (100, 116, 139, 220),    # slate
    "startup": (245, 158, 11, 240),     # amber
    "active": (239, 68, 68, 250),       # crimson red
    "recovery": (56, 189, 248, 230),    # sky blue
    "link_pause": (168, 85, 247, 235),  # violet inter-move breath beat
}

PHASE_CN = {
    "neutral": "常态",
    "startup": "前摇",
    "active": "判定",
    "recovery": "后摇",
    "link_pause": "换气",
}


def _connected_boxes(mask: np.ndarray, min_area: int = 12) -> list[tuple[int, int, int, int, int]]:
    """Find connected component bounding boxes (x, y, w, h, area) in a boolean mask."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur = 0
    boxes: list[tuple[int, int, int, int, int]] = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if labels[y0, x0] != 0:
            continue
        cur += 1
        q: deque[tuple[int, int]] = deque([(x0, y0)])
        labels[y0, x0] = cur
        min_x = max_x = x0
        min_y = max_y = y0
        area = 0
        while q:
            x, y = q.popleft()
            area += 1
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and labels[ny, nx] == 0:
                    labels[ny, nx] = cur
                    q.append((nx, ny))
        if area >= min_area:
            boxes.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, area))
    boxes.sort(key=lambda b: -b[4])
    return boxes


def _dilate_mask(mask: np.ndarray, steps: int = 2) -> np.ndarray:
    out = mask.copy()
    for _ in range(steps):
        p = np.pad(out, 1, mode="constant")
        out = out | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return out


def compute_hurtbox(arr: np.ndarray, pivot: tuple[int, int], palette: list[list[int]] | None = None) -> dict[str, Any]:
    """Compute a tight game-ready body Hurtbox (trims trailing scarf tip & extended weapon so hits feel fair!)."""
    an = measure_cell_anatomy(arr, palette=palette)
    if an is None:
        return {"x": pivot[0] - 8, "y": pivot[1] - 28, "w": 16, "h": 28, "rel": [-8, -28, 16, 28]}

    op = arr[:, :, 3] >= 128
    vfx = _compute_vfx_mask(arr)
    body = _largest_component(op & (~vfx)) if int((op & (~vfx)).sum()) >= 20 else op

    # Trim thin horizontal outliers (flowing scarf tip on left, sword tip on right) via vertical column density
    col_counts = body.sum(axis=0)
    max_col = int(col_counts.max()) if col_counts.size else 0
    core_cols = np.where(col_counts >= max(4, int(max_col * 0.30)))[0]
    if len(core_cols) >= 6:
        hx0, hx1 = int(core_cols[0]), int(core_cols[-1])
    else:
        hx0, hx1 = an["body_min_x"] + 2, an["body_max_x"] - 2

    hy0 = min(an["body_max_y"] - 8, an["body_min_y"] + 2)
    hy1 = an["body_max_y"]
    hw = max(10, hx1 - hx0 + 1)
    hh = max(14, hy1 - hy0 + 1)
    px, py = pivot
    return {
        "x": int(hx0),
        "y": int(hy0),
        "w": int(hw),
        "h": int(hh),
        "rel": [int(hx0 - px), int(hy0 - py), int(hw), int(hh)],
    }


def compute_active_hitboxes(
    arr: np.ndarray,
    hurtbox: dict[str, Any],
    pivot: tuple[int, int],
    hit_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Auto-fit pixel-accurate Attack Hitbox(es) directly to the generated sword + glowing VFX pixels on ACTIVE frames!
    - Ignores trailing speed-lines / afterimages behind the character on forward melee swings (`mode="forward_vfx"`),
    - Covers full explosive AoE / nova blasts (`mode="aoe_nova"` or `"full_vfx"`),
    - Rejects stray 1-8px ambient sparks so hitboxes stay tight and fair!
    """
    h, w, _ = arr.shape
    op = arr[:, :, 3] >= 128
    vfx = _compute_vfx_mask(arr)
    r, g, b = arr[:, :, 0].astype(np.int32), arr[:, :, 1].astype(np.int32), arr[:, :, 2].astype(np.int32)
    # Include bright silver sword blade & blazing flame/crimson pixels as potential weapon strike pixels
    silver_blade = op & (r > 180) & (g > 180) & (b > 185) & (np.abs(r - b) < 35)
    flame_slash = op & (r > 215) & (g > 70) & (b < 145)

    body_cx = hurtbox["x"] + hurtbox["w"] * 0.5
    body_right = hurtbox["x"] + hurtbox["w"]
    mode = hit_cfg.get("hitbox_mode", "forward_vfx")
    kind = hit_cfg.get("kind", "melee_arc")

    xx = np.broadcast_to(np.arange(w)[None, :], (h, w))
    yy = np.broadcast_to(np.arange(h)[:, None], (h, w))
    # Exclude eye whites & gold belt trim strictly inside character torso so inner body highlights never spawn tiny bogus sub-hitboxes!
    body_inner = (
        (xx >= hurtbox["x"]) & (xx <= hurtbox["x"] + hurtbox["w"] - 4)
        & (yy >= hurtbox["y"]) & (yy <= hurtbox["y"] + hurtbox["h"] - 2)
    )
    if mode == "forward_vfx":
        strike_mask = (vfx | silver_blade) & (xx >= int(body_cx) - 2) & (~body_inner)
        if int(strike_mask.sum()) < 24:
            strike_mask = (vfx | silver_blade | flame_slash) & (xx >= int(body_cx)) & (~body_inner)
    elif mode == "aoe_nova":
        strike_mask = (vfx | silver_blade) & (xx >= max(0, hurtbox["x"] - 10)) & (~body_inner)
    else:
        strike_mask = (vfx | (silver_blade & (xx >= int(body_cx) - 4))) & (~body_inner)

    # Bridge tiny 2px pixel gaps inside a slash ribbon so one sweeping arc forms 1 clean hitbox (or 2 distinct multi-hit zones)
    merged = _dilate_mask(strike_mask, steps=2)
    comps = _connected_boxes(merged, min_area=28)

    px, py = pivot
    hitboxes: list[dict[str, Any]] = []
    if comps:
        # Combine primary cluster + any large secondary cluster (up to 2 boxes if cleanly separated, else tight union)
        main_area = comps[0][4]
        valid = [c for c in comps if c[4] >= max(36, int(main_area * 0.16))]
        if mode == "aoe_nova" or len(valid) == 1:
            x0 = min(c[0] for c in valid)
            y0 = min(c[1] for c in valid)
            x1 = max(c[0] + c[2] - 1 for c in valid)
            y1 = max(c[1] + c[3] - 1 for c in valid)
            # Inset 1px to undo dilation padding
            x0, y0 = min(w - 2, x0 + 1), min(h - 2, y0 + 1)
            x1, y1 = max(x0 + 6, x1 - 1), max(y0 + 6, y1 - 1)
            cov = int(strike_mask[y0 : y1 + 1, x0 : x1 + 1].sum())
            hitboxes.append({
                "x": int(x0), "y": int(y0), "w": int(x1 - x0 + 1), "h": int(y1 - y0 + 1),
                "rel": [int(x0 - px), int(y0 - py), int(x1 - x0 + 1), int(y1 - y0 + 1)],
                "kind": kind,
                "vfxCoveragePx": cov,
            })
        else:
            # Up to 2 distinct active hitboxes (e.g. upper + lower X-slash or main + ground shockwave!)
            for c in valid[:2]:
                x0 = min(w - 2, c[0] + 1)
                y0 = min(h - 2, c[1] + 1)
                x1 = max(x0 + 6, c[0] + c[2] - 2)
                y1 = max(y0 + 6, c[1] + c[3] - 2)
                cov = int(strike_mask[y0 : y1 + 1, x0 : x1 + 1].sum())
                hitboxes.append({
                    "x": int(x0), "y": int(y0), "w": int(x1 - x0 + 1), "h": int(y1 - y0 + 1),
                    "rel": [int(x0 - px), int(y0 - py), int(x1 - x0 + 1), int(y1 - y0 + 1)],
                    "kind": kind,
                    "vfxCoveragePx": cov,
                })
    else:
        # Fallback melee blade box right in front of character torso
        fx0 = min(w - 14, int(body_right) - 2)
        fy0 = max(2, hurtbox["y"] + 2)
        fw = min(w - fx0 - 2, 24)
        fh = max(12, hurtbox["h"] - 6)
        hitboxes.append({
            "x": int(fx0), "y": int(fy0), "w": int(fw), "h": int(fh),
            "rel": [int(fx0 - px), int(fy0 - py), int(fw), int(fh)],
            "kind": kind,
            "vfxCoveragePx": 0,
        })

    return hitboxes


def analyze_animation_combat(
    active_frames: list[Image.Image],
    anim_spec: dict[str, Any],
    pivot: tuple[int, int],
    palette: list[list[int]] | None = None,
) -> dict[str, Any]:
    """Generate complete engine-ready per-frame combat Frame Data (Startup/Active/Recovery, Hurtboxes & Active Hitboxes)."""
    durations = anim_spec["frame_durations_ms"]
    combat_cfg = anim_spec.get("combat", {})
    startup_set = set(combat_cfg.get("startup_frames", []))
    active_map: dict[int, dict[str, Any]] = {int(k): v for k, v in combat_cfg.get("active_frames", {}).items()}
    recovery_set = set(combat_cfg.get("recovery_frames", []))
    link_pause_set = set(combat_cfg.get("link_pause_frames", []))
    rhythm_beats: dict[int, str] = {int(k): str(v) for k, v in anim_spec.get("rhythm_beats", {}).items()}

    frame_data: list[dict[str, Any]] = []
    max_reach = 0
    hit_ids: set[int] = set()

    for idx, im in enumerate(active_frames):
        fnum = idx + 1
        arr = np.array(im.convert("RGBA"))
        hurt = compute_hurtbox(arr, pivot=pivot, palette=palette)
        beat = rhythm_beats.get(fnum, "")

        if fnum in active_map:
            phase = "active"
            hcfg = active_map[fnum]
            hboxes = compute_active_hitboxes(arr, hurt, pivot=pivot, hit_cfg=hcfg)
            for hb in hboxes:
                max_reach = max(max_reach, hb["x"] + hb["w"] - pivot[0])
            hit_id = int(hcfg.get("hitId", 1))
            hit_ids.add(hit_id)
            entry = {
                "frame": fnum,
                "durationMs": int(durations[idx]),
                "phase": phase,
                "beat": beat or "hitstop",
                "isAttackFrame": True,
                "hitId": hit_id,
                "damage": int(hcfg.get("damage", 15)),
                "hitstopMs": int(hcfg.get("hitstopMs", 80)),
                "knockback": list(hcfg.get("knockback", [3.0, -1.0])),
                "label": str(hcfg.get("label", f"攻击判定 HIT #{hit_id}")),
                "pivot": [int(pivot[0]), int(pivot[1])],
                "hurtbox": hurt,
                "hitboxes": hboxes,
            }
        else:
            if fnum in link_pause_set or beat == "link_pause":
                phase = "link_pause"
            elif fnum in startup_set:
                phase = "startup"
            elif fnum in recovery_set:
                phase = "recovery"
            else:
                phase = "neutral"
            entry = {
                "frame": fnum,
                "durationMs": int(durations[idx]),
                "phase": phase,
                "beat": beat or phase,
                "isAttackFrame": False,
                "hitId": None,
                "damage": 0,
                "hitstopMs": 0,
                "knockback": [0.0, 0.0],
                "label": PHASE_CN[phase],
                "pivot": [int(pivot[0]), int(pivot[1])],
                "hurtbox": hurt,
                "hitboxes": [],
            }
        frame_data.append(entry)

    startup_ms = sum(fd["durationMs"] for fd in frame_data if fd["phase"] == "startup")
    active_ms = sum(fd["durationMs"] for fd in frame_data if fd["phase"] == "active")
    recovery_ms = sum(fd["durationMs"] for fd in frame_data if fd["phase"] == "recovery")
    link_pause_ms = sum(fd["durationMs"] for fd in frame_data if fd["phase"] == "link_pause")
    charge_frames = [fd["frame"] for fd in frame_data if fd["beat"] == "charge_hold"]
    hitstop_frames = [fd["frame"] for fd in frame_data if fd["beat"] == "hitstop"]

    summary = {
        "hasAttack": len(active_map) > 0,
        "totalFrames": len(active_frames),
        "startupFrames": sorted(startup_set),
        "activeFrames": sorted(active_map.keys()),
        "recoveryFrames": sorted(recovery_set),
        "linkPauseFrames": sorted(link_pause_set),
        "chargeHoldFrames": charge_frames,
        "hitstopFrames": hitstop_frames,
        "startupMs": int(startup_ms),
        "activeMs": int(active_ms),
        "recoveryMs": int(recovery_ms),
        "linkPauseMs": int(link_pause_ms),
        "totalHitCount": len(hit_ids),
        "maxReachPx": int(max_reach),
    }
    return {"frameData": frame_data, "combatSummary": summary}


def make_framedata_audit_preview(
    frames_with_ghost: list[Image.Image],
    frame_data: list[dict[str, Any]],
    cols: int,
    rows: int,
    scale: int = 3,
) -> Image.Image:
    """
    Render a high-clarity Combat Frame-Data & Hitbox/Hurtbox Audit Grid:
      - Green translucent box  = Character Body Hurtbox
      - Red translucent box    = Active Attack Hitbox (ONLY on Attack Frames!)
      - Top color badge        = STARTUP (Amber) / ACTIVE HIT #k (Crimson) / RECOVERY (Blue) / GHOST=F1 (Rose)
    """
    cw, ch = frames_with_ghost[0].size
    atlas = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for i, f in enumerate(frames_with_ghost):
        atlas.paste(f, ((i % cols) * cw, (i // cols) * ch))

    chk = make_checkerboard_preview(atlas, scale=scale)
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    scw, sch = cw * scale, ch * scale

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
    except OSError:
        font = ImageFont.load_default()

    n_active = len(frame_data)
    for idx in range(len(frames_with_ghost)):
        r, c = idx // cols, idx % cols
        ox, oy = c * scw, r * sch
        is_ghost = idx >= n_active

        if is_ghost:
            od.rectangle([ox, oy, ox + scw - 1, oy + sch - 1], fill=(244, 63, 94, 38), outline=(244, 63, 94, 245), width=3)
            od.rectangle([ox + 3, oy + 3, ox + 112, oy + 20], fill=(159, 18, 57, 235))
            od.text((ox + 7, oy + 4), f"F{idx+1} GHOST=F1", fill=(255, 228, 230, 255), font=font)
            continue

        fd = frame_data[idx]
        phase = fd["phase"]
        p_col = PHASE_COLORS.get(phase, (100, 116, 139, 220))

        # Cell border highlighting Active Attack Frames & Loop Bridge Frame N
        if phase == "active":
            od.rectangle([ox + 1, oy + 1, ox + scw - 2, oy + sch - 2], outline=(239, 68, 68, 240), width=3)
        elif idx == 0:
            od.rectangle([ox + 1, oy + 1, ox + scw - 2, oy + sch - 2], outline=(56, 189, 248, 220), width=2)
        elif idx == n_active - 1:
            od.rectangle([ox + 1, oy + 1, ox + scw - 2, oy + sch - 2], outline=(74, 222, 128, 230), width=2)

        # Draw Green Hurtbox
        hb = fd["hurtbox"]
        hx0, hy0 = ox + hb["x"] * scale, oy + hb["y"] * scale
        hx1, hy1 = ox + (hb["x"] + hb["w"]) * scale, oy + (hb["y"] + hb["h"]) * scale
        od.rectangle([hx0, hy0, hx1, hy1], fill=(34, 197, 94, 34), outline=(34, 197, 94, 225), width=2)

        # Draw Red Active Attack Hitbox(es)
        for atk in fd["hitboxes"]:
            ax0, ay0 = ox + atk["x"] * scale, oy + atk["y"] * scale
            ax1, ay1 = ox + (atk["x"] + atk["w"]) * scale, oy + (atk["y"] + atk["h"]) * scale
            od.rectangle([ax0, ay0, ax1, ay1], fill=(239, 68, 68, 52), outline=(255, 72, 72, 255), width=2)
            # Crisp corner crosshairs
            for cx, cy in ((ax0, ay0), (ax1, ay0), (ax0, ay1), (ax1, ay1)):
                od.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=(254, 240, 138, 255))

        # Top phase/beat badge
        beat = fd.get("beat", "")
        if phase == "active":
            tag = f"F{idx+1} HIT#{fd['hitId']} STOP ({fd['durationMs']}ms)" if beat == "hitstop" else f"F{idx+1} ACTIVE HIT#{fd['hitId']} ({fd['durationMs']}ms)"
            bw = 176
        elif beat == "charge_hold":
            tag = f"F{idx+1} CHARGE HOLD ({fd['durationMs']}ms)"
            bw = 172
            od.rectangle([ox + 1, oy + 1, ox + scw - 2, oy + sch - 2], outline=(251, 191, 36, 235), width=3)
        elif phase == "link_pause":
            tag = f"F{idx+1} LINK PAUSE ({fd['durationMs']}ms)"
            bw = 166
            od.rectangle([ox + 1, oy + 1, ox + scw - 2, oy + sch - 2], outline=(168, 85, 247, 235), width=2)
        elif beat == "motion":
            tag = f"F{idx+1} FAST SWING ({fd['durationMs']}ms)"
            bw = 158
        else:
            tag = f"F{idx+1} {phase.upper()} ({fd['durationMs']}ms)"
            bw = 136
        od.rectangle([ox + 3, oy + 3, ox + bw, oy + 20], fill=(p_col[0] // 2, p_col[1] // 2, p_col[2] // 2, 230), outline=p_col, width=1)
        od.text((ox + 7, oy + 4), tag, fill=(248, 250, 252, 255), font=font)

    chk.alpha_composite(ov)
    return chk
