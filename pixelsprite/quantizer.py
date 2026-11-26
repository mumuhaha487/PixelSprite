"""PixelSprite v2.2 — Body-Isolated Wide-Arena Pixel Quantizer (96x80 Canvas, Fixed 34px Char, 24-Color Arcade VFX Ramp & Strict Closed-Loop Audit)."""

from __future__ import annotations

from collections import deque
from typing import Any
import numpy as np
from PIL import Image, ImageDraw


# Rich 24-color 16-bit Arcade / NeoGeo / Dead Cells Multi-Layered Pixel VFX Ramp!
VFX_ACCENT_PALETTE = np.array(
    [
        # White / Ice / Starlight Core
        [255, 255, 255],  # pure white hot core
        [232, 250, 255],  # ice-white sheen
        [255, 246, 214],  # warm starlight core
        # Electric Cyan -> Azure -> Deep Sapphire Wave Ramp
        [165, 248, 255],  # pale frost cyan
        [56, 232, 224],   # vivid neon cyan-teal
        [14, 195, 235],   # electric sky cyan
        [37, 138, 245],   # intense azure wave
        [48, 88, 218],    # deep sapphire energy rim
        # Starlight Gold -> Solar Amber -> Blazing Flame -> Fiery Crimson Ramp
        [255, 252, 186],  # pale starlight lemon
        [255, 224, 71],   # bright star gold
        [251, 182, 36],   # solar amber
        [251, 132, 42],   # blazing flame orange
        [242, 72, 34],    # fiery crimson-orange edge
        [204, 34, 54],    # deep flame crimson
        # Soft Pink -> Hot Magenta -> Arcane Violet -> Deep Indigo Rift Ramp
        [255, 186, 232],  # soft sakura pink glow
        [255, 92, 188],   # neon hot pink slash
        [238, 44, 148],   # intense neon magenta
        [212, 68, 248],   # radiant orchid rift
        [156, 88, 248],   # arcane starfall violet
        [104, 54, 208],   # deep dimensional indigo
        # Ground Shockwave Dust & Smoke Puff Ramp
        [240, 232, 214],  # bright wind-kick dust highlight
        [208, 196, 178],  # warm dust midtone
        [162, 154, 146],  # dust shadow
        [118, 114, 122],  # deep smoke shadow
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
        min_keep = max(12, int(max_size * 0.004))
        keep_lut = np.zeros(cur + 1, dtype=np.bool_)
        for l_id in range(1, cur + 1):
            if comp_sizes[l_id] >= min_keep and not (comp_edge[l_id] and comp_sizes[l_id] < max_size * 0.10):
                keep_lut[l_id] = True
        arr[:, :, 3] = np.where(keep_lut[labels], 255, 0)

    return arr


def _filter_large_components(mask: np.ndarray, min_area: int) -> np.ndarray:
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    keep = np.zeros((h, w), dtype=np.bool_)
    cur = 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if labels[y0, x0] != 0:
            continue
        cur += 1
        q: deque[tuple[int, int]] = deque([(x0, y0)])
        labels[y0, x0] = cur
        pts: list[tuple[int, int]] = []
        while q:
            x, y = q.popleft()
            pts.append((x, y))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and labels[ny, nx] == 0:
                    labels[ny, nx] = cur
                    q.append((nx, ny))
        if len(pts) >= min_area:
            for x, y in pts:
                keep[y, x] = True
    return keep


def _compute_vfx_mask(arr: np.ndarray) -> np.ndarray:
    """Identify bright glowing skill VFX pixels (white/cyan/azure/sapphire/gold/neon-pink/violet + attached flame swirl)."""
    op = arr[:, :, 3] >= 128
    r = arr[:, :, 0].astype(np.int32)
    g = arr[:, :, 1].astype(np.int32)
    b = arr[:, :, 2].astype(np.int32)

    is_white = (r > 225) & (g > 225) & (b > 210)
    is_cyan_blue = (b > 165) & (r < 175) & ((b - r) > 35)
    is_bright_gold = (r > 235) & (g > 195) & (b < 185)
    is_neon_pink = (r > 175) & (b > 105) & (g < 175) & ((r - g) > 50)
    is_violet = (b > 170) & (r > 100) & (g < 165) & ((b - g) > 30)
    core = op & (is_white | is_cyan_blue | is_bright_gold | is_neon_pink | is_violet)

    # Seed flame flood-fill ONLY from LARGE bright white/gold VFX cores (never from tiny 2-6px hair highlights or belt trim!),
    # and strictly stop at 1px dark character outlines so orange hair & red scarf remain 100% protected!
    is_dark_outline = (r + g + b) < 155
    flame_rim = op & (~is_dark_outline) & (r > 180) & (g < 215) & (b < 150) & ((r - b) > 55)
    min_core = 320 if arr.shape[0] > 96 else 34
    glow = _filter_large_components(op & (is_white | is_bright_gold), min_area=min_core)
    if np.any(glow):
        steps = 48 if arr.shape[0] > 96 else 18
        for _ in range(steps):
            p = np.pad(glow, 1, mode="constant")
            adj = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
            nxt = glow | (adj & flame_rim)
            if np.array_equal(nxt, glow):
                break
            glow = nxt

    return core | glow


def measure_cell_anatomy(arr: np.ndarray, palette: list[list[int]] | None = None) -> dict[str, Any] | None:
    """Measure BOTH full opaque bounds (character + VFX) AND isolated CHARACTER BODY bounds (immune to VFX & afterimages!)."""
    op = arr[:, :, 3] >= 128
    ys, xs = np.nonzero(op)
    if len(xs) == 0:
        return None
    full_min_x, full_max_x = int(xs.min()), int(xs.max())
    full_min_y, full_max_y = int(ys.min()), int(ys.max())
    full_w = full_max_x - full_min_x + 1
    full_h = full_max_y - full_min_y + 1

    vfx = _compute_vfx_mask(arr)
    non_vfx = op & (~vfx)
    if palette:
        pts = arr[non_vfx][:, :3].astype(np.float32)
        if len(pts) > 0:
            pal = np.array(palette, dtype=np.float32)
            w_rgb = np.array([2.0, 4.0, 3.0], dtype=np.float32)
            d2 = ((pts[:, None, :] - pal[None, :, :]) ** 2 * w_rgb).sum(axis=2).min(axis=1)
            strict = np.zeros_like(non_vfx)
            strict[non_vfx] = d2 < (46 * 46 * 9)
            if int(strict.sum()) >= max(30, int(op.sum() * 0.08)):
                non_vfx = strict

    body_mask = _largest_component(non_vfx) if int(non_vfx.sum()) >= 30 else op
    bys, bxs = np.nonzero(body_mask)
    if len(bxs) == 0:
        bys, bxs = ys, xs

    b_min_x, b_max_x = int(bxs.min()), int(bxs.max())
    b_min_y, b_max_y = int(bys.min()), int(bys.max())
    b_w = b_max_x - b_min_x + 1
    b_h = b_max_y - b_min_y + 1

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
    """Exact scale-preserving majority-vote downsampler supporting wide non-square cells (e.g. 96x80)."""
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
            if total == 0 or int(op_mask.sum()) / total < 0.40:
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
    """Snap to Master Palette DNA while preserving rich 24-color multi-layered VFX gradients & dust puffs!"""
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
        use_vfx = (best_dist > 28 * 28 * 9) & (vfx_best_dist < best_dist * 0.80)
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
    """Patch ONLY missing 1px ink gaps on non-VFX character body pixels (ZERO dark crust on ANY slash/flame/star/dust!)."""
    out = arr.copy()
    op = out[:, :, 3] >= 128
    r = out[:, :, 0].astype(np.int32)
    g = out[:, :, 1].astype(np.int32)
    b = out[:, :, 2].astype(np.int32)

    is_dark = (r + g + b) < 155
    is_vfx = _compute_vfx_mask(out)
    if vfx_mask is not None:
        is_vfx = is_vfx | vfx_mask

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
    rgb_diff = np.abs(a[:, :, :3] - b[:, :, :3]).mean(axis=2) / 255.0
    pixel_diff = np.where(ma & mb, rgb_diff, np.where(ma | mb, 1.0, 0.0))
    rgb_sim = 1.0 - float(pixel_diff[ma | mb].mean())
    return iou, rgb_sim


def audit_closed_loop(frames_with_ghost: list[Image.Image], palette: list[list[int]] | None = None) -> dict[str, Any]:
    if len(frames_with_ghost) < 3:
        return {"active_frames": frames_with_ghost, "ghost_frame": None, "metrics": {}}

    active = frames_with_ghost[:-1]
    ghost = frames_with_ghost[-1]
    f1, fn = active[0], active[-1]

    fn_g_iou, fn_g_rgb = _frame_iou_and_rgb(fn, ghost)
    g_f1_iou, g_f1_rgb = _frame_iou_and_rgb(ghost, f1)
    fn_f1_iou, fn_f1_rgb = _frame_iou_and_rgb(fn, f1)
    step_ious = [_frame_iou_and_rgb(active[i], active[i + 1])[0] for i in range(len(active) - 1)]

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
            "seam_smooth": fn_f1_rgb >= 0.68 and fn_f1_iou >= 0.80 and max(max_dx, wrap_dx) <= 4.5,
        },
    }


def make_loop_audit_preview(frames_with_ghost: list[Image.Image], cols: int, rows: int, scale: int = 3) -> Image.Image:
    cw, ch = frames_with_ghost[0].size
    atlas = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for i, f in enumerate(frames_with_ghost):
        atlas.paste(f, ((i % cols) * cw, (i // cols) * ch))

    chk = make_checkerboard_preview(atlas, scale=scale)
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    scw, sch = cw * scale, ch * scale

    fn_idx = len(frames_with_ghost) - 2
    gh_idx = len(frames_with_ghost) - 1
    for idx, col_rgba in ((0, (56, 189, 248, 225)), (fn_idx, (74, 222, 128, 235)), (gh_idx, (244, 63, 94, 245))):
        r, c = idx // cols, idx % cols
        x0, y0 = c * scw, r * sch
        if idx == gh_idx:
            od.rectangle([x0, y0, x0 + scw - 1, y0 + sch - 1], fill=(244, 63, 94, 34), outline=col_rgba, width=4)
        else:
            od.rectangle([x0 + 1, y0 + 1, x0 + scw - 2, y0 + sch - 2], outline=col_rgba, width=3)

    chk.alpha_composite(ov)
    return chk


def pack_horizontal_strip(frames: list[Image.Image]) -> Image.Image:
    cw, ch = frames[0].size
    strip = Image.new("RGBA", (len(frames) * cw, ch), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * cw, 0))
    return strip


def pad_frame_to_arena(
    frame: Image.Image,
    target_w: int = 96,
    target_h: int = 80,
    dst_pivot_x: int = 30,
    dst_foot_y: int = 71,
    palette: list[list[int]] | None = None,
) -> Image.Image:
    """Losslessly embed an existing 1x pixel frame (e.g. 64x64) onto a unified wide arena (e.g. 96x80) at exact pivot."""
    arr = np.array(frame.convert("RGBA"))
    an = measure_cell_anatomy(arr, palette=palette)
    out = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    if an is None:
        return out
    dx = int(round(dst_pivot_x - an["body_cx"]))
    dy = int(round(dst_foot_y - an["body_foot_y"]))
    out.alpha_composite(frame.convert("RGBA"), (dx, dy))
    return out


def quantize_anchor(
    raw_img: Image.Image,
    cell_size: int = 64,
    char_height_px: int = 34,
    max_colors: int = 18,
    outline: bool = True,
) -> dict[str, Any]:
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
    cell_w: int = 96,
    cell_h: int = 80,
    char_height_px: int = 34,
    inset_pct: float = 2.2,
    palette: list[list[int]] | None = None,
    lock_palette: bool = True,
    outline: bool = True,
    preserve_vfx: bool = True,
    tolerance: int = 28,
    lock_body_x: bool = False,
    allow_airborne: bool = False,
    max_lift_px: float = 28.0,
    anchor_x_ratio: float = 0.3125,
    scale_anchor_cell_idx: int = 0,
) -> dict[str, Any]:
    """
    v2.2 Wide-Arena Body-Isolated Pixel Quantizer:
      - Unified 96x80 wide combat arena with locked 34px chibi character height (66px wide open VFX runway!).
      - Body-isolated `body_cx` & `body_h` alignment (zero teleporting, zero shrinking, ignores afterimages & slashes!).
      - Smart Grounded-Row Baseline canceling AI row drift while preserving true airborne jump parabolas!
      - 24-color multi-layered VFX palette preservation + body-only 1px outline protection!
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
            if an and an["body_h"] > (ey - sy) * 0.20:
                standing_body_hs.append(an["body_h"])

    standing_body_hs.sort()
    ref_cell = cells[scale_anchor_cell_idx] if (-len(cells) <= scale_anchor_cell_idx < len(cells)) else cells[0]
    ref_body_h = (
        ref_cell[3]["body_h"]
        if ref_cell[3] is not None
        else (standing_body_hs[len(standing_body_hs) // 2] if standing_body_hs else rch * 0.40)
    )
    if standing_body_hs:
        med = standing_body_hs[len(standing_body_hs) // 2]
        ref_body_h = 0.65 * ref_body_h + 0.35 * med

    fixed_scale = char_height_px / max(1.0, ref_body_h)

    row_max_foot = [
        max((cells[r * cols + c][3]["body_foot_y"] for c in range(cols) if cells[r * cols + c][3] is not None), default=rch * 0.85)
        for r in range(rows)
    ]
    row_min_foot = [
        min((cells[r * cols + c][3]["body_foot_y"] for c in range(cols) if cells[r * cols + c][3] is not None), default=rch * 0.85)
        for r in range(rows)
    ]
    global_max_foot = max(row_max_foot) if row_max_foot else rch * 0.85
    is_grounded_row = [
        (row_max_foot[r] >= global_max_foot - rch * 0.12) or ((row_max_foot[r] - row_min_foot[r]) < rch * 0.05)
        for r in range(rows)
    ]
    grounded_floors = [row_max_foot[r] for r in range(rows) if is_grounded_row[r]]
    mean_grounded = float(np.mean(grounded_floors)) if grounded_floors else global_max_foot
    row_ground_y = [row_max_foot[r] if is_grounded_row[r] else mean_grounded for r in range(rows)]

    f1_body_cx = ref_cell[3]["body_cx"] if ref_cell[3] is not None else (rcw * 0.30)
    dst_anchor_x = int(round(cell_w * anchor_x_ratio))
    dst_foot_y = int(round(cell_h * 0.89))  # 71 inside 80px tall cell

    frames: list[Image.Image] = []
    atlas = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))

    for r, c, cleaned, an in cells:
        if an is None:
            q_img = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
        else:
            if lock_body_x:
                target_cx = float(dst_anchor_x)
            else:
                lunge_px = (an["body_cx"] - f1_body_cx) * fixed_scale
                lunge_px = max(-0.8, min(2.2, lunge_px))
                target_cx = float(dst_anchor_x) + lunge_px

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
                cell_w,
                cell_h,
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
        atlas.paste(q_img, (c * cell_w, r * cell_h))

    return {
        "frames": frames,
        "atlas": atlas,
        "cols": cols,
        "rows": rows,
        "cell_w": cell_w,
        "cell_h": cell_h,
        "pivot": [dst_anchor_x, dst_foot_y],
    }
