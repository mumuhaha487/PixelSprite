"""NumPy + Pillow Aseprite-grade low-res pixel quantizer, palette DNA lock, jump-arc preserver, and 1px outline patcher."""

from __future__ import annotations

from collections import deque
from typing import Any
import numpy as np
from PIL import Image


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


def clean_cell_alpha(img: Image.Image, tolerance: int = 28) -> np.ndarray:
    """Return RGBA uint8 array with corner flood-fill bg removal, hard alpha cutoff, and stray border speck removal."""
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w, _ = arr.shape

    # 1. Corner flood-fill if image came back with an opaque background
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

    # 2. Hard alpha threshold kills blurry semi-transparent anti-aliased fringe
    mask = arr[:, :, 3] >= 110
    arr[:, :, 3] = np.where(mask, 255, 0)

    # 3. Connected-component filter removes stray grid borders/numbers/tiny dust while keeping sparks & slash VFX
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
        min_keep = max(14, int(max_size * 0.008))
        keep_lut = np.zeros(cur + 1, dtype=np.bool_)
        for l_id in range(1, cur + 1):
            if comp_sizes[l_id] >= min_keep and not (comp_edge[l_id] and comp_sizes[l_id] < max_size * 0.14):
                keep_lut[l_id] = True
        keep_mask = keep_lut[labels]
        arr[:, :, 3] = np.where(keep_mask, 255, 0)

    return arr


def measure_opaque_bounds(arr: np.ndarray) -> dict[str, float] | None:
    ys, xs = np.nonzero(arr[:, :, 3] > 128)
    if len(xs) == 0:
        return None
    min_x, max_x = int(xs.min()), int(xs.max())
    min_y, max_y = int(ys.min()), int(ys.max())
    bw = max_x - min_x + 1
    bh = max_y - min_y + 1

    # Lower 35% foot centroid X (prevents wide right-hand skill beams from yanking character left!)
    foot_start = max_y - int(round(bh * 0.35))
    foot_mask = ys >= foot_start
    foot_cx = float(xs[foot_mask].mean()) if np.any(foot_mask) else (min_x + max_x) * 0.5
    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "w": bw,
        "h": bh,
        "foot_cx": foot_cx,
    }


def extract_master_palette(img: Image.Image, max_colors: int = 18) -> list[list[int]]:
    """Extract clean perceptual Master Palette DNA from the quantized anchor sprite."""
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    opaque = arr[arr[:, :, 3] >= 200][:, :3]
    if len(opaque) == 0:
        return [[38, 26, 43]]

    # 5-bit color bucketing suppresses rare noise
    keys = ((opaque[:, 0].astype(np.int32) >> 3) << 10) | ((opaque[:, 1].astype(np.int32) >> 3) << 5) | (opaque[:, 2].astype(np.int32) >> 3)
    uniq, inv, counts = np.unique(keys, return_inverse=True, return_counts=True)
    order = np.argsort(-counts)

    candidates: list[list[int]] = []
    for idx in order:
        pix = opaque[inv == idx]
        mean_rgb = np.round(pix.mean(axis=0)).astype(int).tolist()
        candidates.append(mean_rgb)

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
    bounds: dict[str, float],
    cell_size: int,
    dst_x: int,
    dst_y: int,
    dst_w: int,
    dst_h: int,
) -> np.ndarray:
    """Majority-vote center-weighted pixel-grid downsampler (zero blur, zero mixels!)."""
    sh, sw, _ = src_arr.shape
    out = np.zeros((cell_size, cell_size, 4), dtype=np.uint8)

    scale_x = bounds["w"] / max(1, dst_w)
    scale_y = bounds["h"] / max(1, dst_h)
    min_x, min_y = int(bounds["min_x"]), int(bounds["min_y"])

    for ly in range(max(0, dst_y), min(cell_size, dst_y + dst_h)):
        rel_y = ly - dst_y
        sy0 = max(0, int(np.floor(min_y + rel_y * scale_y)))
        sy1 = min(sh - 1, max(sy0, int(np.ceil(min_y + (rel_y + 1) * scale_y)) - 1))
        sy_mid = max(sy0, min(sy1, int(round(min_y + (rel_y + 0.5) * scale_y))))

        for lx in range(max(0, dst_x), min(cell_size, dst_x + dst_w)):
            rel_x = lx - dst_x
            sx0 = max(0, int(np.floor(min_x + rel_x * scale_x)))
            sx1 = min(sw - 1, max(sx0, int(np.ceil(min_x + (rel_x + 1) * scale_x)) - 1))
            sx_mid = max(sx0, min(sx1, int(round(min_x + (rel_x + 0.5) * scale_x))))

            patch = src_arr[sy0 : sy1 + 1, sx0 : sx1 + 1]
            total = patch.shape[0] * patch.shape[1]
            op_mask = patch[:, :, 3] >= 128
            op_cnt = int(op_mask.sum())
            if total == 0 or op_cnt / total < 0.42:
                continue

            # Center-weighted majority color bucket
            yy, xx = np.ogrid[sy0 : sy1 + 1, sx0 : sx1 + 1]
            weights = np.where((np.abs(xx - sx_mid) <= 1) & (np.abs(yy - sy_mid) <= 1), 2, 1)
            rgb = patch[op_mask][:, :3].astype(np.int32)
            w_vals = weights[op_mask]

            keys = ((rgb[:, 0] >> 4) << 8) | ((rgb[:, 1] >> 4) << 4) | (rgb[:, 2] >> 4)
            uniq_k, inv = np.unique(keys, return_inverse=True)
            bucket_w = np.bincount(inv, weights=w_vals)
            best_idx = int(np.argmax(bucket_w))
            sel = inv == best_idx
            sel_w = w_vals[sel][:, None]
            avg = np.round((rgb[sel] * sel_w).sum(axis=0) / sel_w.sum()).astype(np.uint8)
            out[ly, lx, :3] = avg
            out[ly, lx, 3] = 255

    return out


def snap_palette_perceptual(arr: np.ndarray, palette: list[list[int]], preserve_vfx: bool = True) -> np.ndarray:
    """Vectorized human-weighted perceptual palette snap preserving luminous skill VFX accents."""
    if not palette:
        return arr
    out = arr.copy()
    mask = out[:, :, 3] >= 128
    if not np.any(mask):
        return out

    pixels = out[mask][:, :3].astype(np.float32)  # (N, 3)
    pal = np.array(palette, dtype=np.float32)     # (P, 3)

    # Human perceptual RGB weights (2, 4, 3)
    w = np.array([2.0, 4.0, 3.0], dtype=np.float32)
    diff = pixels[:, None, :] - pal[None, :, :]
    dists = (diff * diff * w).sum(axis=2)  # (N, P)
    best_idx = np.argmin(dists, axis=1)
    best_dist = dists[np.arange(len(pixels)), best_idx]
    snapped = pal[best_idx]

    if preserve_vfx:
        vfx_diff = pixels[:, None, :] - VFX_ACCENT_PALETTE[None, :, :]
        vfx_dists = (vfx_diff * vfx_diff * w).sum(axis=2)
        vfx_best_idx = np.argmin(vfx_dists, axis=1)
        vfx_best_dist = vfx_dists[np.arange(len(pixels)), vfx_best_idx]
        use_vfx = (best_dist > 38 * 38 * 9) & (vfx_best_dist < best_dist * 0.68)
        snapped = np.where(use_vfx[:, None], VFX_ACCENT_PALETTE[vfx_best_idx], snapped)

    out[mask, :3] = np.clip(np.round(snapped), 0, 255).astype(np.uint8)
    out[mask, 3] = 255
    return out


def despeckle_orphans(arr: np.ndarray) -> np.ndarray:
    """Remove isolated single-pixel floating dust (0 4-connected opaque neighbors)."""
    out = arr.copy()
    op = (out[:, :, 3] >= 128).astype(np.uint8)
    padded = np.pad(op, 1, mode="constant")
    neighbors = padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:]
    out[(op == 1) & (neighbors == 0), 3] = 0
    return out


def patch_1px_outline(arr: np.ndarray, outline_rgb: tuple[int, int, int] = (38, 25, 44)) -> np.ndarray:
    """Patch ONLY missing 1px silhouette outline gaps on body pixels (never doubles 1px ink or muddies glowing VFX!)."""
    out = arr.copy()
    op = out[:, :, 3] >= 128
    r = out[:, :, 0].astype(np.int32)
    g = out[:, :, 1].astype(np.int32)
    b = out[:, :, 2].astype(np.int32)

    is_dark = (r + g + b) < 155
    is_white_vfx = (r > 225) & (g > 225) & (b > 220)
    is_cyan_vfx = (g > 170) & (b > 195) & (r < 185)
    is_gold_fire_vfx = (r > 205) & (g > 60) & (b < 165) & ((r - b) > 80)
    is_magenta_vfx = (r > 180) & (b > 135) & (g < 175)

    needs_ink = op & (~is_dark) & (~is_white_vfx) & (~is_cyan_vfx) & (~is_gold_fire_vfx) & (~is_magenta_vfx)
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


def quantize_anchor(
    raw_img: Image.Image,
    cell_size: int = 48,
    fill_ratio: float = 0.72,
    max_colors: int = 18,
    outline: bool = True,
) -> dict[str, Any]:
    """Quantize a raw anchor into 1:1 true-pixel sprite + crisp 512x512 nearest-neighbor API ref + Master Palette DNA."""
    cleaned = clean_cell_alpha(raw_img)
    bounds = measure_opaque_bounds(cleaned)
    if not bounds:
        raise ValueError("Anchor image has no visible character pixels.")

    target_h = max(12, int(round(cell_size * fill_ratio)))
    scale = target_h / max(1, bounds["h"])
    dst_w = min(cell_size - 4, max(8, int(round(bounds["w"] * scale))))
    dst_h = min(cell_size - 4, max(8, int(round(bounds["h"] * (dst_w / max(1, bounds["w"]))))))
    dst_x = (cell_size - dst_w) // 2
    foot_y = int(round(cell_size * 0.92))
    dst_y = max(2, foot_y - dst_h)

    q_arr = smart_pixel_downsample(cleaned, bounds, cell_size, dst_x, dst_y, dst_w, dst_h)
    palette = extract_master_palette(Image.fromarray(q_arr, "RGBA"), max_colors=max_colors)
    q_arr = snap_palette_perceptual(q_arr, palette, preserve_vfx=False)
    q_arr = despeckle_orphans(q_arr)
    if outline:
        q_arr = patch_1px_outline(q_arr)

    pixel_1x = Image.fromarray(q_arr, "RGBA")

    # Crisp nearest-neighbor 512x512 Reference Image 1 for GPT Image 2.6 /v1/images/edits
    api_ref = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    zoom = max(1, 440 // cell_size)
    draw_sz = cell_size * zoom
    off = (512 - draw_sz) // 2
    api_ref.paste(pixel_1x.resize((draw_sz, draw_sz), Image.Resampling.NEAREST), (off, off))

    return {
        "pixel_1x": pixel_1x,
        "api_ref": api_ref,
        "palette": palette,
        "palette_hex": [rgb_to_hex(c) for c in palette],
    }


def quantize_grid(
    raw_img: Image.Image,
    cols: int = 8,
    rows: int = 4,
    cell_size: int = 48,
    fill_ratio: float = 0.72,
    inset_pct: float = 3.0,
    palette: list[list[int]] | None = None,
    lock_palette: bool = True,
    outline: bool = True,
    preserve_vfx: bool = True,
    tolerance: int = 28,
) -> dict[str, Any]:
    """Slice & quantize an 8x4 or 8x8 raw sprite sheet with unified chibi scale, jump-arc lift, and palette lock."""
    raw = raw_img.convert("RGBA")
    rw, rh = raw.size
    rcw, rch = rw / cols, rh / rows
    pad_x = int(round(rcw * (inset_pct / 100.0)))
    pad_y = int(round(rch * (inset_pct / 100.0)))

    cells: list[tuple[int, int, np.ndarray, dict[str, float] | None]] = []
    heights: list[float] = []
    for r in range(rows):
        for c in range(cols):
            sx = int(round(c * rcw + pad_x))
            sy = int(round(r * rch + pad_y))
            ex = max(sx + 8, int(round((c + 1) * rcw - pad_x)))
            ey = max(sy + 8, int(round((r + 1) * rch - pad_y)))
            crop = raw.crop((sx, sy, ex, ey))
            cleaned = clean_cell_alpha(crop, tolerance=tolerance)
            bounds = measure_opaque_bounds(cleaned)
            cells.append((r, c, cleaned, bounds))
            if bounds and bounds["h"] > (ey - sy) * 0.25:
                heights.append(bounds["h"])

    # Per-row ground floor Y preserves real airborne leaps/flips while clamping minor <5% standing jitter!
    row_ground_y = [0.0] * rows
    for r in range(rows):
        row_ground_y[r] = max(
            (cells[r * cols + c][3]["max_y"] for c in range(cols) if cells[r * cols + c][3] is not None),
            default=0.0,
        )

    heights.sort()
    median_h = heights[len(heights) // 2] if heights else rch * 0.55
    unified_scale = (cell_size * fill_ratio) / max(1.0, median_h)
    foot_baseline_y = int(round(cell_size * 0.92))

    frames: list[Image.Image] = []
    atlas = Image.new("RGBA", (cols * cell_size, rows * cell_size), (0, 0, 0, 0))

    for r, c, cleaned, bounds in cells:
        if bounds is None:
            q_img = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
        else:
            s = unified_scale
            if bounds["w"] * s > cell_size - 2:
                s = (cell_size - 2) / bounds["w"]
            if bounds["h"] * s > cell_size - 2:
                s = min(s, (cell_size - 2) / bounds["h"])

            dst_w = max(4, int(round(bounds["w"] * s)))
            dst_h = max(4, int(round(bounds["h"] * s)))

            rel_foot_x = (bounds["foot_cx"] - bounds["min_x"]) * s
            dst_x = max(1, min(cell_size - dst_w - 1, int(round(cell_size * 0.5 - rel_foot_x))))

            lift_raw = max(0.0, row_ground_y[r] - bounds["max_y"])
            lift_thresh = rch * 0.055
            lift_px = int(round((lift_raw - lift_thresh * 0.6) * s)) if lift_raw > lift_thresh else 0
            dst_y = max(1, min(cell_size - dst_h - 1, int(round(foot_baseline_y - dst_h - lift_px))))

            q_arr = smart_pixel_downsample(cleaned, bounds, cell_size, dst_x, dst_y, dst_w, dst_h)
            if lock_palette and palette:
                q_arr = snap_palette_perceptual(q_arr, palette, preserve_vfx=preserve_vfx)
            q_arr = despeckle_orphans(q_arr)
            if outline:
                q_arr = patch_1px_outline(q_arr)
            q_img = Image.fromarray(q_arr, "RGBA")

        frames.append(q_img)
        atlas.paste(q_img, (c * cell_size, r * cell_size))

    return {"frames": frames, "atlas": atlas, "cols": cols, "rows": rows, "cell_size": cell_size}


def combine_halves_to_8x8(top_half: dict[str, Any], bot_half: dict[str, Any]) -> dict[str, Any]:
    cell_size = top_half["cell_size"]
    atlas = Image.new("RGBA", (8 * cell_size, 8 * cell_size), (0, 0, 0, 0))
    atlas.paste(top_half["atlas"], (0, 0))
    atlas.paste(bot_half["atlas"], (0, 4 * cell_size))
    return {
        "frames": top_half["frames"] + bot_half["frames"],
        "atlas": atlas,
        "cols": 8,
        "rows": 8,
        "cell_size": cell_size,
    }
