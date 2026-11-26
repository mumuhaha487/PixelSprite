"""PixelSprite v2.1 — Body-Isolated Pixel Quantizer (Zero Teleporting, Zero Shrinking, True Jump Arcs, Pure Glowing VFX & Strict Closed-Loop Audit)."""

from __future__ import annotations

from collections import deque
from typing import Any
import numpy as np
from PIL import Image, ImageDraw


VFX_ACCENT_PALETTE = np.array(
    [
        [255, 255, 255],  # pure white core flash
        [186, 246, 255],  # pale frost / lightning cyan
        [56, 224, 212],   # vivid cyan-teal slash
        [56, 189, 248],   # electric sky blue lightning
        [254, 249, 195],  # bright pale starlight gold
        [250, 204, 21],   # rich golden slash / thunder
        [251, 146, 60],   # blazing flame orange
        [239, 78, 36],    # fiery crimson-orange flame edge
        [255, 82, 172],   # neon hot pink-magenta phantom slash
        [236, 48, 128],   # deep neon magenta-crimson slash
        [244, 114, 182],  # soft pink starfall glow
        [192, 132, 252],  # arcane starfall violet
    ],
    dtype=np.float32,
)


def rgb_to_hex(rgb: tuple[int, int, int] | list[int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(rgb[0]))),
        max(0, min(255, int(rgb[1]))),
        max(0, min(255, int(rgb[2]))),
    )


def _largest_component(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    best_label = 0
    best_size = 0
    cur = 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if labels[y0, x0] != 0:
            continue
        cur += 1
        q: deque[tuple[int, int]] = deque([(x0, y0)])
        labels[y0, x0] = cur
        size = 0
        while q:
            x, y = q.popleft()
            size += 1
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and labels[ny, nx] == 0:
                    labels[ny, nx] = cur
                    q.append((nx, ny))
        if size > best_size:
            best_size = size
            best_label = cur
    return labels == best_label if best_label > 0 else mask


def clean_cell_alpha(img: Image.Image, tolerance: int = 28) -> np.ndarray:
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w, _ = arr.shape

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    opaque_corners = [(x, y) for x, y in corners if arr[y, x, 3] > 200]
    if len(opaque_corners) >= 2:
        visited = np.zeros((h, w), dtype=np.bool_)
        tol_sq = (tolerance * tolerance) * 9
        for cx, cy in opaque_corners:
            if visited[cy, cx]:
                continue
            br, bg, bb = int(arr[cy, cx, 0]), int(arr[cy, cx, 1]), int(arr[cy, cx, 2])
            q: deque[tuple[int, int]] = deque([(cx, cy)])
            visited[cy, cx] = True
            while q:
                x, y = q.popleft()
                arr[y, x, 3] = 0
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx]:
                        a = int(arr[ny, nx, 3])
                        if a < 30:
                            visited[ny, nx] = True
                            q.append((nx, ny))
                        else:
                            dr = int(arr[ny, nx, 0]) - br
                            dg = int(arr[ny, nx, 1]) - bg
                            db = int(arr[ny, nx, 2]) - bb
                            if 2 * dr * dr + 4 * dg * dg + 3 * db * db <= tol_sq:
                                visited[ny, nx] = True
                                q.append((nx, ny))

    mask = arr[:, :, 3] >= 110
    arr[:, :, 3] = np.where(mask, 255, 0)

    labels = np.zeros((h, w), dtype=np.int32)
    comp_sizes = [0]
    comp_edge = [False]
    cur = 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if labels[y0, x0] != 0:
            continue
        cur += 1
        q = deque([(x0, y0)])
        labels[y0, x0] = cur
        size = 0
        edge = False
        while q:
            x, y = q.popleft()
            size += 1
            if x <= 1 or x >= w - 2 or y <= 1 or y >= h - 2:
                edge = True
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and labels[ny, nx] == 0:
                    labels[ny, nx] = cur
                    q.append((nx, ny))
        comp_sizes.append(size)
        comp_edge.append(edge)

    if cur > 0:
        max_size = max(comp_sizes)
        min_keep = max(14, int(max_size * 0.006))
        keep_lut = np.zeros(cur + 1, dtype=np.bool_)
        for l_id in range(1, cur + 1):
            if comp_sizes[l_id] >= min_keep and not (comp_edge[l_id] and comp_sizes[l_id] < max_size * 0.14):
                keep_lut[l_id] = True
        arr[:, :, 3] = np.where(keep_lut[labels], 255, 0)

    return arr


def _compute_vfx_mask(arr: np.ndarray) -> np.ndarray:
    """Identify bright glowing skill VFX pixels (white/cyan/gold/neon-pink/violet + attached flame-gold halo) separately from character body."""
    op = arr[:, :, 3] >= 128
    r = arr[:, :, 0].astype(np.int32)
    g = arr[:, :, 1].astype(np.int32)
    b = arr[:, :, 2].astype(np.int32)

    is_white = (r > 225) & (g > 225) & (b > 215)
    is_cyan = (g > 155) & (b > 170) & (r < 175)
    is_bright_gold = (r > 235) & (g > 200) & (b < 185)
    is_neon_pink = (r > 180) & (b > 105) & (g < 170) & ((r - g) > 55)
    is_violet = (b > 185) & (r > 135) & (g < 170)
    core = op & (is_white | is_cyan | is_bright_gold | is_neon_pink | is_violet)

    # Expand ONLY from glowing white/gold core into adjacent bright flame-gold rim (never touches character's separate orange hair!)
    flame_rim = op & (r > 225) & (g > 135) & (b < 130)
    glow = op & (is_white | is_bright_gold)
    steps = 10 if arr.shape[0] > 96 else 2
    for _ in range(steps):
        p = np.pad(glow, 1, mode="constant")
        adj = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        nxt = glow | (adj & flame_rim)
        if np.array_equal(nxt, glow):
            break
        glow = nxt

    return core | glow


def measure_cell_anatomy(arr: np.ndarray, palette: list[list[int]] | None = None) -> dict[str, Any] | None:
    """
    Measure BOTH full opaque bounds (character + VFX) AND isolated CHARACTER BODY bounds!
    Isolating body_cx, body_h, and body_foot_y strictly from character pixels completely eliminates:
      1. Horizontal teleporting when huge slashes appear on the right or speed lines on the left!
      2. Body shrinking when tall star explosions expand total bbox height!
      3. Grounded pinning when sparks/rays touch the bottom of an airborne jump cell!
    """
    op = arr[:, :, 3] >= 128
    ys, xs = np.nonzero(op)
    if len(xs) == 0:
        return None
    full_min_x, full_max_x = int(xs.min()), int(xs.max())
    full_min_y, full_max_y = int(ys.min()), int(ys.max())
    full_w = full_max_x - full_min_x + 1
    full_h = full_max_y - full_min_y + 1

    # Isolate pure character body pixels (non-VFX + largest connected body cluster)
    vfx = _compute_vfx_mask(arr)
    non_vfx = op & (~vfx)
    if palette:
        # Also filter out disconnected stray pixels far from Master Anchor palette (e.g. orange fire sparks flying far right)
        pts = arr[non_vfx][:, :3].astype(np.float32)
        if len(pts) > 0:
            pal = np.array(palette, dtype=np.float32)
            w_rgb = np.array([2.0, 4.0, 3.0], dtype=np.float32)
            d2 = ((pts[:, None, :] - pal[None, :, :]) ** 2 * w_rgb).sum(axis=2).min(axis=1)
            strict = np.zeros_like(non_vfx)
            strict[non_vfx] = d2 < (46 * 46 * 9)
            if int(strict.sum()) >= max(30, int(op.sum() * 0.12)):
                non_vfx = strict

    body_mask = _largest_component(non_vfx) if int(non_vfx.sum()) >= 30 else op
    bys, bxs = np.nonzero(body_mask)
    if len(bxs) == 0:
        bys, bxs = ys, xs

    b_min_x, b_max_x = int(bxs.min()), int(bxs.max())
    b_min_y, b_max_y = int(bys.min()), int(bys.max())
    b_w = b_max_x - b_min_x + 1
    b_h = b_max_y - b_min_y + 1

    # Use core torso+head X centroid (middle 60% vertically of body_mask) — rock-steady against cape/scarf/foot kick!
    core_y0 = b_min_y + int(b_h * 0.12)
    core_y1 = b_min_y + int(b_h * 0.72)
    core_m = (bys >= core_y0) & (bys <= core_y1)
    body_cx = float(bxs[core_m].mean()) if np.any(core_m) else float(bxs.mean())

    return {
        "min_x": full_min_x,
        "min_y": full_min_y,
        "max_x": full_max_x,
        "max_y": full_max_y,
        "w": full_w,
        "h": full_h,
        "body_min_x": b_min_x,
        "body_max_x": b_max_x,
        "body_min_y": b_min_y,
        "body_max_y": b_max_y,
        "body_w": b_w,
        "body_h": b_h,
        "body_cx": body_cx,
        "body_foot_y": b_max_y,
    }


def extract_master_palette(img: Image.Image, max_colors: int = 18) -> list[list[int]]:
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    opaque = arr[arr[:, :, 3] >= 200][:, :3]
    if len(opaque) == 0:
        return [[38, 26, 43]]

    keys = ((opaque[:, 0].astype(np.int32) >> 3) << 10) | ((opaque[:, 1].astype(np.int32) >> 3) << 5) | (opaque[:, 2].astype(np.int32) >> 3)
    _, inv, counts = np.unique(keys, return_inverse=True, return_counts=True)
    order = np.argsort(-counts)

    candidates = [np.round(opaque[inv == idx].mean(axis=0)).astype(int).tolist() for idx in order]
    chosen: list[list[int]] = []
    min_dist_sq = 28 * 28 * 4
    for r, g, b in candidates:
        if len(chosen) >= max_colors:
            break
        if all(2 * (r - cr) ** 2 + 4 * (g - cg) ** 2 + 3 * (b - cb) ** 2 >= min_dist_sq for cr, cg, cb in chosen):
            chosen.append([r, g, b])

    if len(chosen) < max_colors and not any(r + g + b < 130 for r, g, b in chosen):
        chosen.append([38, 26, 43])
    return chosen


def smart_pixel_downsample(
    src_arr: np.ndarray,
    src_origin_x: float,
    src_origin_y: float,
    scale: float,
    cell_w: int,
    cell_h: int,
    dst_origin_x: float,
    dst_origin_y: float,
) -> np.ndarray:
    """
    Exact scale-preserving majority-vote downsampler!
    Maps logical pixel (lx, ly) directly from source pixel:
      sx = src_origin_x + (lx - dst_origin_x) / scale
      sy = src_origin_y + (ly - dst_origin_y) / scale
    Never distorts aspect ratio and never blurs pixel clusters!
    """
    sh, sw, _ = src_arr.shape
    out = np.zeros((cell_h, cell_w, 4), dtype=np.uint8)
    inv_s = 1.0 / max(1e-6, scale)

    for ly in range(cell_h):
        sy_f0 = src_origin_y + (ly - dst_origin_y) * inv_s
        sy_f1 = src_origin_y + (ly + 1 - dst_origin_y) * inv_s
        if sy_f1 <= 0 or sy_f0 >= sh:
            continue
        sy0 = max(0, int(np.floor(sy_f0)))
        sy1 = min(sh - 1, max(sy0, int(np.ceil(sy_f1)) - 1))
        sy_mid = max(sy0, min(sy1, int(round((sy_f0 + sy_f1) * 0.5))))

        for lx in range(cell_w):
            sx_f0 = src_origin_x + (lx - dst_origin_x) * inv_s
            sx_f1 = src_origin_x + (lx + 1 - dst_origin_x) * inv_s
            if sx_f1 <= 0 or sx_f0 >= sw:
                continue
            sx0 = max(0, int(np.floor(sx_f0)))
            sx1 = min(sw - 1, max(sx0, int(np.ceil(sx_f1)) - 1))
            sx_mid = max(sx0, min(sx1, int(round((sx_f0 + sx_f1) * 0.5))))

            patch = src_arr[sy0 : sy1 + 1, sx0 : sx1 + 1]
            total = patch.shape[0] * patch.shape[1]
            op_mask = patch[:, :, 3] >= 128
            if total == 0 or int(op_mask.sum()) / total < 0.42:
                continue

            yy, xx = np.ogrid[sy0 : sy1 + 1, sx0 : sx1 + 1]
            weights = np.where((np.abs(xx - sx_mid) <= 1) & (np.abs(yy - sy_mid) <= 1), 2, 1)
            rgb = patch[op_mask][:, :3].astype(np.int32)
            w_vals = weights[op_mask]

            keys = ((rgb[:, 0] >> 4) << 8) | ((rgb[:, 1] >> 4) << 4) | (rgb[:, 2] >> 4)
            _, inv = np.unique(keys, return_inverse=True)
            best_idx = int(np.argmax(np.bincount(inv, weights=w_vals)))
            sel = inv == best_idx
            sel_w = w_vals[sel][:, None]
            out[ly, lx, :3] = np.round((rgb[sel] * sel_w).sum(axis=0) / sel_w.sum()).astype(np.uint8)
            out[ly, lx, 3] = 255

    return out


def snap_palette_perceptual(arr: np.ndarray, palette: list[list[int]], preserve_vfx: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Snap to Master Palette DNA while preserving luminous VFX accents; also returns exact boolean `is_vfx` mask!"""
    out = arr.copy()
    mask = out[:, :, 3] >= 128
    is_vfx_full = np.zeros(out.shape[:2], dtype=np.bool_)
    if not palette or not np.any(mask):
        return out, is_vfx_full

    pixels = out[mask][:, :3].astype(np.float32)
    pal = np.array(palette, dtype=np.float32)
    w = np.array([2.0, 4.0, 3.0], dtype=np.float32)

    diff = pixels[:, None, :] - pal[None, :, :]
    dists = (diff * diff * w).sum(axis=2)
    best_idx = np.argmin(dists, axis=1)
    best_dist = dists[np.arange(len(pixels)), best_idx]
    snapped = pal[best_idx]

    if preserve_vfx:
        vfx_diff = pixels[:, None, :] - VFX_ACCENT_PALETTE[None, :, :]
        vfx_dists = (vfx_diff * vfx_diff * w).sum(axis=2)
        vfx_best_idx = np.argmin(vfx_dists, axis=1)
        vfx_best_dist = vfx_dists[np.arange(len(pixels)), vfx_best_idx]
        use_vfx = (best_dist > 34 * 34 * 9) & (vfx_best_dist < best_dist * 0.72)
        snapped = np.where(use_vfx[:, None], VFX_ACCENT_PALETTE[vfx_best_idx], snapped)
        is_vfx_full[mask] = use_vfx

    out[mask, :3] = np.clip(np.round(snapped), 0, 255).astype(np.uint8)
    out[mask, 3] = 255
    return out, is_vfx_full


def despeckle_orphans(arr: np.ndarray) -> np.ndarray:
    out = arr.copy()
    op = (out[:, :, 3] >= 128).astype(np.uint8)
    padded = np.pad(op, 1, mode="constant")
    neighbors = padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:]
    out[(op == 1) & (neighbors == 0), 3] = 0
    return out


def patch_1px_outline(
    arr: np.ndarray,
    vfx_mask: np.ndarray | None = None,
    outline_rgb: tuple[int, int, int] = (38, 25, 44),
) -> np.ndarray:
    """Patch ONLY missing 1px ink gaps on non-VFX character body pixels (ZERO dark crust on ANY slash/flame/star!)."""
    out = arr.copy()
    op = out[:, :, 3] >= 128
    r = out[:, :, 0].astype(np.int32)
    g = out[:, :, 1].astype(np.int32)
    b = out[:, :, 2].astype(np.int32)

    is_dark = (r + g + b) < 155
    is_vfx = _compute_vfx_mask(out)
    if vfx_mask is not None:
        is_vfx = is_vfx | vfx_mask

    # Only body pixels belonging to the main character cluster get outline-gap protection!
    body_non_vfx = op & (~is_vfx)
    main_body = _largest_component(body_non_vfx) if int(body_non_vfx.sum()) >= 20 else body_non_vfx
    needs_ink = main_body & (~is_dark)

    padded = np.pad(needs_ink, 1, mode="constant")
    adj = padded[:-2, 1:-1] | padded[2:, 1:-1] | padded[1:-1, :-2] | padded[1:-1, 2:]
    place = (~op) & adj
    out[place, 0] = outline_rgb[0]
    out[place, 1] = outline_rgb[1]
    out[place, 2] = outline_rgb[2]
    out[place, 3] = 255
    return out


def upscale_crisp(img: Image.Image, factor: int = 4) -> Image.Image:
    return img.resize((img.width * factor, img.height * factor), Image.Resampling.NEAREST)


def make_checkerboard_preview(atlas_1x: Image.Image, scale: int = 4) -> Image.Image:
    up = upscale_crisp(atlas_1x, scale)
    w, h = up.size
    sq = 16
    yy, xx = np.indices((h, w))
    grid = ((xx // sq) + (yy // sq)) & 1
    bg = np.empty((h, w, 4), dtype=np.uint8)
    bg[grid == 0] = [133, 147, 150, 255]
    bg[grid == 1] = [152, 166, 168, 255]
    canvas = Image.fromarray(bg, mode="RGBA")
    canvas.alpha_composite(up)
    return canvas


def _frame_iou_and_rgb(img_a: Image.Image, img_b: Image.Image) -> tuple[float, float]:
    a = np.array(img_a.convert("RGBA"), dtype=np.int32)
    b = np.array(img_b.convert("RGBA"), dtype=np.int32)
    ma = a[:, :, 3] >= 128
    mb = b[:, :, 3] >= 128
    union = int((ma | mb).sum())
    if union == 0:
        return 1.0, 1.0
    iou = float((ma & mb).sum()) / float(union)
    # RGB similarity across union of opaque pixels (catches disappearing swords / shifted eyes even when silhouette IoU is high!)
    rgb_diff = np.abs(a[:, :, :3] - b[:, :, :3]).mean(axis=2) / 255.0
    # Transparent vs opaque counts as 1.0 diff
    pixel_diff = np.where(ma & mb, rgb_diff, np.where(ma | mb, 1.0, 0.0))
    rgb_sim = 1.0 - float(pixel_diff[ma | mb].mean())
    return iou, rgb_sim


def audit_closed_loop(frames_with_ghost: list[Image.Image], palette: list[list[int]] | None = None) -> dict[str, Any]:
    """
    Strict v2.1 Closed-Loop & Stability Auditor:
      - Measures BOTH silhouette IoU AND RGB similarity on F[N]<->F[N+1](Ghost), F[N+1]<->F1, and F[N]->F1!
      - Measures max single-frame body horizontal jump (`max_body_dx`) to prove ZERO teleporting!
      - Measures standing body height stability (`body_h_range`) to prove ZERO shrinking!
      - Returns trimmed active_frames = frames_with_ghost[:-1] (Ghost excluded!).
    """
    if len(frames_with_ghost) < 3:
        return {"active_frames": frames_with_ghost, "ghost_frame": None, "metrics": {}}

    active = frames_with_ghost[:-1]
    ghost = frames_with_ghost[-1]
    f1, fn = active[0], active[-1]

    fn_g_iou, fn_g_rgb = _frame_iou_and_rgb(fn, ghost)
    g_f1_iou, g_f1_rgb = _frame_iou_and_rgb(ghost, f1)
    fn_f1_iou, fn_f1_rgb = _frame_iou_and_rgb(fn, f1)
    step_ious = [_frame_iou_and_rgb(active[i], active[i + 1])[0] for i in range(len(active) - 1)]

    # Measure body X stability & height consistency across active frames
    body_cxs = []
    body_hs = []
    for im in active:
        an = measure_cell_anatomy(np.array(im.convert("RGBA")), palette=palette)
        if an:
            body_cxs.append(an["body_cx"])
            body_hs.append(an["body_h"])
    max_dx = max((abs(body_cxs[i + 1] - body_cxs[i]) for i in range(len(body_cxs) - 1)), default=0.0)
    wrap_dx = abs(body_cxs[-1] - body_cxs[0]) if len(body_cxs) >= 2 else 0.0

    return {
        "active_frames": active,
        "ghost_frame": ghost,
        "metrics": {
            "activeCount": len(active),
            "ghostIndex": len(frames_with_ghost),
            "fN_vs_ghost_iou": round(fn_g_iou, 3),
            "fN_vs_ghost_rgb": round(fn_g_rgb, 3),
            "ghost_vs_f1_iou": round(g_f1_iou, 3),
            "ghost_vs_f1_rgb": round(g_f1_rgb, 3),
            "fN_vs_f1_iou": round(fn_f1_iou, 3),
            "fN_vs_f1_rgb": round(fn_f1_rgb, 3),
            "avg_step_iou": round(float(np.mean(step_ious)) if step_ious else 0.0, 3),
            "max_body_dx_px": round(max(max_dx, wrap_dx), 2),
            "body_h_min_max": [int(min(body_hs)), int(max(body_hs))] if body_hs else [0, 0],
            "seam_smooth": fn_f1_rgb >= 0.72 and max(max_dx, wrap_dx) <= 4.5,
        },
    }


def make_loop_audit_preview(frames_with_ghost: list[Image.Image], cols: int, rows: int, scale: int = 3) -> Image.Image:
    cell = frames_with_ghost[0].width
    atlas = Image.new("RGBA", (cols * cell, rows * cell), (0, 0, 0, 0))
    for i, f in enumerate(frames_with_ghost):
        atlas.paste(f, ((i % cols) * cell, (i // cols) * cell))

    chk = make_checkerboard_preview(atlas, scale=scale)
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    cs = cell * scale

    fn_idx = len(frames_with_ghost) - 2
    gh_idx = len(frames_with_ghost) - 1
    for idx, col_rgba in ((0, (56, 189, 248, 225)), (fn_idx, (74, 222, 128, 235)), (gh_idx, (244, 63, 94, 245))):
        r, c = idx // cols, idx % cols
        x0, y0 = c * cs, r * cs
        if idx == gh_idx:
            od.rectangle([x0, y0, x0 + cs - 1, y0 + cs - 1], fill=(244, 63, 94, 34), outline=col_rgba, width=4)
        else:
            od.rectangle([x0 + 1, y0 + 1, x0 + cs - 2, y0 + cs - 2], outline=col_rgba, width=3)

    chk.alpha_composite(ov)
    return chk


def pack_horizontal_strip(frames: list[Image.Image]) -> Image.Image:
    cell = frames[0].width
    strip = Image.new("RGBA", (len(frames) * cell, cell), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * cell, 0))
    return strip


def quantize_anchor(
    raw_img: Image.Image,
    cell_size: int = 64,
    char_height_px: int = 34,
    max_colors: int = 18,
    outline: bool = True,
) -> dict[str, Any]:
    """Quantize raw anchor at exact fixed `char_height_px` (e.g. 34px tall) inside `cell_size x cell_size` (e.g. 64x64)."""
    cleaned = clean_cell_alpha(raw_img)
    an = measure_cell_anatomy(cleaned)
    if not an:
        raise ValueError("Anchor image has no visible character pixels.")

    scale = char_height_px / max(1, an["body_h"])
    anchor_x = int(round(cell_size * 0.44))
    foot_y = int(round(cell_size * 0.90))

    q_arr = smart_pixel_downsample(cleaned, an["body_cx"], an["body_foot_y"], scale, cell_size, cell_size, anchor_x, foot_y)
    palette = extract_master_palette(Image.fromarray(q_arr, "RGBA"), max_colors=max_colors)
    q_arr, vfx_m = snap_palette_perceptual(q_arr, palette, preserve_vfx=False)
    q_arr = despeckle_orphans(q_arr)
    if outline:
        q_arr = patch_1px_outline(q_arr, vfx_mask=vfx_m)

    pixel_1x = Image.fromarray(q_arr, "RGBA")
    api_ref = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    # Crop tightly around character for clean Reference Image 1
    bbox = pixel_1x.getbbox()
    if bbox:
        tight = pixel_1x.crop(bbox)
        zoom = max(1, 380 // max(tight.width, tight.height))
        dw, dh = tight.width * zoom, tight.height * zoom
        api_ref.paste(tight.resize((dw, dh), Image.Resampling.NEAREST), ((512 - dw) // 2, (512 - dh) // 2))

    return {
        "pixel_1x": pixel_1x,
        "api_ref": api_ref,
        "palette": palette,
        "palette_hex": [rgb_to_hex(c) for c in palette],
    }


def quantize_grid(
    raw_img: Image.Image,
    cols: int = 3,
    rows: int = 3,
    cell_size: int = 64,
    char_height_px: int = 34,
    inset_pct: float = 2.5,
    palette: list[list[int]] | None = None,
    lock_palette: bool = True,
    outline: bool = True,
    preserve_vfx: bool = True,
    tolerance: int = 28,
    lock_body_x: bool = False,
    allow_airborne: bool = False,
    max_lift_px: float = 24.0,
    anchor_x_ratio: float = 0.42,
) -> dict[str, Any]:
    """
    v2.1 Body-Isolated Pixel Quantizer:
      - Locks character scale strictly from `body_h` (NEVER shrinks character on giant VFX frames!).
      - Aligns X strictly from `body_cx` (NEVER yanks character backward when slashes appear on the right!).
      - Computes airborne lift strictly from `body_foot_y` (NEVER pins airborne jumps down to ground sparks!).
      - Patches 1px outline strictly on non-VFX character body (ZERO dark crust on glowing slashes/flames/stars!).
    """
    raw = raw_img.convert("RGBA")
    rw, rh = raw.size
    rcw, rch = rw / cols, rh / rows
    pad_x = int(round(rcw * (inset_pct / 100.0)))
    pad_y = int(round(rch * (inset_pct / 100.0)))

    cells: list[tuple[int, int, np.ndarray, dict[str, Any] | None]] = []
    standing_body_hs: list[float] = []
    for r in range(rows):
        for c in range(cols):
            sx = int(round(c * rcw + pad_x))
            sy = int(round(r * rch + pad_y))
            ex = max(sx + 8, int(round((c + 1) * rcw - pad_x)))
            ey = max(sy + 8, int(round((r + 1) * rch - pad_y)))
            crop = raw.crop((sx, sy, ex, ey))
            cleaned = clean_cell_alpha(crop, tolerance=tolerance)
            an = measure_cell_anatomy(cleaned, palette=palette)
            cells.append((r, c, cleaned, an))
            if an and an["body_h"] > (ey - sy) * 0.22:
                standing_body_hs.append(an["body_h"])

    # Anchor scale tightly from Cell 0 (standing F1) + median standing body height (zero cross-action scale drift!)
    standing_body_hs.sort()
    ref_body_h = (
        cells[0][3]["body_h"]
        if cells[0][3] is not None
        else (standing_body_hs[len(standing_body_hs) // 2] if standing_body_hs else rch * 0.45)
    )
    if standing_body_hs:
        med = standing_body_hs[len(standing_body_hs) // 2]
        ref_body_h = 0.65 * ref_body_h + 0.35 * med

    # FIXED unified pixel scale for the entire animation — NEVER shrinks on VFX cells!
    fixed_scale = char_height_px / max(1.0, ref_body_h)

    # Smart Grounded-Row Baseline: cancels 2-4px row-to-row AI baseline drift while preserving TRUE airborne rows!
    row_max_foot = [
        max((cells[r * cols + c][3]["body_foot_y"] for c in range(cols) if cells[r * cols + c][3] is not None), default=rch * 0.82)
        for r in range(rows)
    ]
    global_max_foot = max(row_max_foot) if row_max_foot else rch * 0.82
    grounded_floors = [f for f in row_max_foot if f >= global_max_foot - rch * 0.085]
    mean_grounded = float(np.mean(grounded_floors)) if grounded_floors else global_max_foot
    row_ground_y = [f if f >= global_max_foot - rch * 0.085 else mean_grounded for f in row_max_foot]

    f1_body_cx = cells[0][3]["body_cx"] if cells[0][3] is not None else (rcw * 0.5)
    dst_anchor_x = int(round(cell_size * anchor_x_ratio))
    dst_foot_y = int(round(cell_size * 0.90))

    frames: list[Image.Image] = []
    atlas = Image.new("RGBA", (cols * cell_size, rows * cell_size), (0, 0, 0, 0))

    for r, c, cleaned, an in cells:
        if an is None:
            q_img = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
        else:
            # Horizontal alignment strictly from character's own torso/head center (`body_cx`)!
            if lock_body_x:
                # Locomotion (idle/walk/run): 0.0px horizontal jitter!
                target_cx = float(dst_anchor_x)
            else:
                # Combat skills: allow natural organic forward lunge relative to F1, tightly clamped so body NEVER teleports!
                lunge_px = (an["body_cx"] - f1_body_cx) * fixed_scale
                lunge_px = max(-1.5, min(3.0, lunge_px))
                target_cx = float(dst_anchor_x) + lunge_px

            # Vertical alignment: grounded actions lock boots to exact floor (0.0px drift!); airborne actions preserve true jump arc!
            if not allow_airborne:
                lift_px = 0.0
            else:
                lift_raw = max(0.0, row_ground_y[r] - an["body_foot_y"])
                lift_thresh = rch * 0.045
                lift_px = (lift_raw - lift_thresh * 0.5) * fixed_scale if lift_raw > lift_thresh else 0.0
                head_above_foot = (an["body_foot_y"] - an["body_min_y"]) * fixed_scale
                max_safe = max(0.0, dst_foot_y - head_above_foot - 3.0)
                lift_px = min(lift_px, float(max_lift_px), max_safe)
            target_foot_y = float(dst_foot_y) - lift_px

            q_arr = smart_pixel_downsample(
                cleaned,
                an["body_cx"],
                an["body_foot_y"],
                fixed_scale,
                cell_size,
                cell_size,
                target_cx,
                target_foot_y,
            )
            if lock_palette and palette:
                q_arr, vfx_m = snap_palette_perceptual(q_arr, palette, preserve_vfx=preserve_vfx)
            else:
                vfx_m = _compute_vfx_mask(q_arr)
            q_arr = despeckle_orphans(q_arr)
            if outline:
                q_arr = patch_1px_outline(q_arr, vfx_mask=vfx_m)
            q_img = Image.fromarray(q_arr, "RGBA")

        frames.append(q_img)
        atlas.paste(q_img, (c * cell_size, r * cell_size))

    return {"frames": frames, "atlas": atlas, "cols": cols, "rows": rows, "cell_size": cell_size}
