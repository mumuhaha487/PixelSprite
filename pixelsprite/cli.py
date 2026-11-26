"""Command-line interface for PixelSprite v2.0 — Closed-Loop (N+1 Ghost), Variable-Length & Hitstop Timing Pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

from .api import edit_images, generate_image, resolve_api_config
from .guide import (
    render_batch_8x4_guide,
    render_closed_loop_9x4_guide,
    render_variable_action_guide,
)
from .presets import (
    ANIMATION_SPECS,
    CLOSED_LOOP_PACKS,
    PIXEL_STYLES,
    SHEET_MODULES,
    compile_anchor_prompt,
    compile_batch_8x4_prompt,
    compile_closed_loop_9x4_prompt,
    compile_variable_action_prompt,
    load_animation_spec,
    load_module_spec,
)
from .quantizer import (
    audit_closed_loop,
    combine_halves_to_8x8,
    extract_master_palette,
    make_checkerboard_preview,
    make_loop_audit_preview,
    pack_horizontal_strip,
    quantize_anchor,
    quantize_grid,
    rgb_to_hex,
    upscale_crisp,
)
from .showcase import render_showcase_mp4, render_variable_timing_showcase_mp4


def _load_anchor_and_palette(anchor_path: str, cell: int, fill: float, colors: int, outline: bool):
    anchor_img = Image.open(anchor_path).convert("RGBA")
    if anchor_img.width <= 128:
        palette = extract_master_palette(anchor_img, max_colors=colors)
        zoom = max(1, 440 // anchor_img.width)
        api_ref = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        ds = anchor_img.width * zoom
        api_ref.paste(anchor_img.resize((ds, ds), Image.Resampling.NEAREST), ((512 - ds) // 2, (512 - ds) // 2))
        return anchor_img, api_ref, palette
    q_anc = quantize_anchor(anchor_img, cell_size=cell, fill_ratio=fill, max_colors=colors, outline=outline)
    return q_anc["pixel_1x"], q_anc["api_ref"], q_anc["palette"]


def cmd_list(_args: argparse.Namespace) -> int:
    print("=== Pixel Styles ===")
    for k, v in PIXEL_STYLES.items():
        print(f"  {k:10s} | cell={v['cell_size']}px | colors={v['palette_colors']} | {v['label']}")

    print("\n=== v2.0 Closed-Loop Variable-Length Animations (N Active + 1 Ghost=F1) ===")
    for k, a in ANIMATION_SPECS.items():
        g = f"{a['grid'][0]}x{a['grid'][1]}"
        total_ms = sum(a["frame_durations_ms"])
        holds = ", ".join(f"F{fi}:{tag}({a['frame_durations_ms'][fi-1]}ms)" for fi, tag in a.get("hold_tags", {}).items()) or "匀速 EVEN"
        print(f"  {k:22s} | {a['active_frames']:2d}+1f ({g}) | {total_ms:4d}ms | {holds}")

    print("\n=== v2.0 Closed-Loop Packs ===")
    for k, pk in CLOSED_LOOP_PACKS.items():
        print(f"  {k:22s} | {pk['name_zh']} -> {', '.join(pk['anim_ids'])}")

    print("\n=== Legacy 8x8 (64-Frame) Modules ===")
    for k, m in SHEET_MODULES.items():
        print(f"  {k:22s} | {m['name_zh']}")
    return 0


def cmd_anchor(args: argparse.Namespace) -> int:
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]
    colors = args.colors or style["palette_colors"]
    fill = args.fill or style["fill_ratio"]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.input_image:
        raw_img = Image.open(args.input_image).convert("RGBA")
        print(f"[ANCHOR] Quantizing existing image: {args.input_image}")
    else:
        if not args.desc:
            raise ValueError("Provide --desc or --input-image.")
        cfg = resolve_api_config(args.api_url, args.api_key, args.model)
        prompt = compile_anchor_prompt(args.desc, args.style, args.module)
        print(f"[ANCHOR] Calling {cfg['model']} to generate chunky pixel Master Anchor...")
        raw_img = generate_image(prompt, cfg, size="1024x1024")
        raw_img.save(out_dir / "00_anchor_raw.png")

    res = quantize_anchor(raw_img, cell_size=cell, fill_ratio=fill, max_colors=colors, outline=not args.no_outline)
    res["pixel_1x"].save(out_dir / f"01_anchor_pixel_{cell}px.png")
    res["api_ref"].save(out_dir / "01_anchor_preview_512px.png")
    (out_dir / "01_palette.json").write_text(
        json.dumps({"cellSize": cell, "palette": res["palette"], "paletteHex": res["palette_hex"]}, indent=2),
        encoding="utf-8",
    )
    print(f"[ANCHOR] Saved {cell}x{cell} anchor & {len(res['palette'])}-color palette DNA to {out_dir}")
    return 0


def cmd_closed_loop_pack(args: argparse.Namespace) -> int:
    """v2.0: Generate a 9x4 Closed-Loop pack (8 active + Col 9 Ghost=F1 per row), audit F8<->F9, and export 8f game strips!"""
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]
    colors = args.colors or style["palette_colors"]
    fill = args.fill or style["fill_ratio"]
    pack_spec = CLOSED_LOOP_PACKS[args.pack]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "_raw_cache"
    raw_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or args.pack

    anchor_1x, api_ref, palette = _load_anchor_and_palette(args.anchor, cell, fill, colors, not args.no_outline)
    pal_hex = [rgb_to_hex(c) for c in palette]
    raw_path = raw_dir / f"{prefix}_raw_9x4.png"

    if args.requantize_only and raw_path.is_file():
        print(f"[9x4] Reusing cached raw 9x4: {raw_path}")
        raw_img = Image.open(raw_path).convert("RGBA")
    else:
        cfg = resolve_api_config(args.api_url, args.api_key, args.model)
        guide_img = render_closed_loop_9x4_guide(pack_spec, anchor_img=anchor_1x)
        guide_img.save(raw_dir / f"{prefix}_guide_9x4.png")
        prompt = compile_closed_loop_9x4_prompt(args.desc, args.style, pack_spec, palette_hex=pal_hex)
        print(f"[9x4] Calling {cfg['model']} for {prefix} (9 cols x 4 rows, Col 9 = Ghost F1)...")
        raw_img = edit_images(prompt, [api_ref, guide_img], cfg, size="1536x1024")
        raw_img.save(raw_path)

    q = quantize_grid(
        raw_img,
        cols=9,
        rows=4,
        cell_size=cell,
        fill_ratio=fill,
        inset_pct=args.inset,
        palette=palette,
        lock_palette=not args.no_palette_lock,
        outline=not args.no_outline,
        preserve_vfx=True,
    )

    # Save 9-column full audit sheet (highlighting Col 9 = Ghost F1 excluded!)
    audit_9x4_chk = make_checkerboard_preview(q["atlas"], scale=4)
    # Mark Col 9 red & Col 8 green on every row of the 9x4 audit image
    from PIL import ImageDraw
    ov = Image.new("RGBA", audit_9x4_chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    cs = cell * 4
    for r in range(4):
        y0 = r * cs
        od.rectangle([0, y0 + 1, cs - 1, y0 + cs - 2], outline=(56, 189, 248, 220), width=3)
        od.rectangle([7 * cs + 1, y0 + 1, 8 * cs - 2, y0 + cs - 2], outline=(74, 222, 128, 235), width=3)
        od.rectangle([8 * cs, y0, 9 * cs - 1, y0 + cs - 1], fill=(244, 63, 94, 42), outline=(244, 63, 94, 245), width=4)
    audit_9x4_chk.alpha_composite(ov)
    audit_9x4_chk.save(out_dir / f"{prefix}_9col_audit_4x.png")

    # Audit each row, drop Ghost Col 9, and export clean 8-frame game strips + 8x4 trimmed atlas!
    trimmed_atlas = Image.new("RGBA", (8 * cell, 4 * cell), (0, 0, 0, 0))
    rows_meta = []
    for r, aid in enumerate(pack_spec["anim_ids"]):
        anim = ANIMATION_SPECS[aid]
        row_9 = q["frames"][r * 9 : (r + 1) * 9]
        audited = audit_closed_loop(row_9)
        active_8 = audited["active_frames"]
        m = audited["metrics"]
        print(f"[AUDIT] {aid:14s} | F8<->F9(Ghost)={m['fN_vs_ghost_iou']:.2f} | F9<->F1={m['ghost_vs_f1_iou']:.2f} | F8->F1={m['fN_vs_f1_iou']:.2f} (avgStep={m['avg_step_iou']:.2f})")

        strip = pack_horizontal_strip(active_8)
        strip.save(out_dir / f"anim_{aid}_{len(active_8)}f_{cell}px.png")
        trimmed_atlas.paste(strip, (0, r * cell))

        rows_meta.append({
            "row": r,
            "id": aid,
            "name": anim["name"],
            "key": anim["key"],
            "frameCount": len(active_8),
            "closedLoop": True,
            "ghostFrameExcluded": True,
            "timingMode": anim["timing_mode"],
            "frameDurationsMs": anim["frame_durations_ms"],
            "holdTags": anim["hold_tags"],
            "scrollSpeed": anim.get("scroll_speed", 0),
            "loopAudit": m,
            "stripFile": f"anim_{aid}_{len(active_8)}f_{cell}px.png",
            "ghostAuditRow": r,
        })

    trimmed_atlas.save(out_dir / f"{prefix}_trimmed_8x4_{cell}px.png")
    q["atlas"].save(out_dir / f"{prefix}_9col_with_ghost_{cell}px.png")
    meta = {
        "generator": "PixelSprite 2.0 (Closed-Loop N+1)",
        "packId": prefix,
        "cellSize": cell,
        "activeCols": 8,
        "generatedCols": 9,
        "rows": 4,
        "palette": pal_hex,
        "animations": rows_meta,
    }
    (out_dir / f"{prefix}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[EXPORT] 9-col audit: {out_dir / f'{prefix}_9col_audit_4x.png'}")
    print(f"[EXPORT] Trimmed 8x4 atlas (Ghost dropped): {out_dir / f'{prefix}_trimmed_8x4_{cell}px.png'}")
    return 0


def cmd_action(args: argparse.Namespace) -> int:
    """v2.0: Generate a dedicated Variable-Length Closed-Loop Action (e.g. 11+1f on 4x3 or 14+1f on 5x3) with Hitstop Timing!"""
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]
    colors = args.colors or style["palette_colors"]
    fill = args.fill or style["fill_ratio"]
    anim = load_animation_spec(args.anim)

    cols, rows = anim["grid"]
    n_active = int(anim["active_frames"])
    closed = bool(anim.get("closed_loop", True))
    n_total = n_active + (1 if closed else 0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "_raw_cache"
    raw_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or f"anim_{anim['id']}_{n_active}f"

    anchor_1x, api_ref, palette = _load_anchor_and_palette(args.anchor, cell, fill, colors, not args.no_outline)
    pal_hex = [rgb_to_hex(c) for c in palette]
    raw_path = raw_dir / f"{prefix}_raw_{cols}x{rows}.png"

    if args.requantize_only and raw_path.is_file():
        print(f"[ACTION] Reusing cached raw {cols}x{rows}: {raw_path}")
        raw_img = Image.open(raw_path).convert("RGBA")
    else:
        cfg = resolve_api_config(args.api_url, args.api_key, args.model)
        guide_img = render_variable_action_guide(anim, anchor_img=anchor_1x)
        guide_img.save(raw_dir / f"{prefix}_guide_{cols}x{rows}.png")
        prompt = compile_variable_action_prompt(args.desc, args.style, anim, palette_hex=pal_hex)
        print(f"[ACTION] Calling {cfg['model']} for {anim['id']} ({n_active} active + {1 if closed else 0} ghost on {cols}x{rows})...")
        raw_img = edit_images(prompt, [api_ref, guide_img], cfg, size="1536x1024")
        raw_img.save(raw_path)

    q = quantize_grid(
        raw_img,
        cols=cols,
        rows=rows,
        cell_size=cell,
        fill_ratio=fill,
        inset_pct=args.inset,
        palette=palette,
        lock_palette=not args.no_palette_lock,
        outline=not args.no_outline,
        preserve_vfx=True,
        global_ground_reference=True,
    )

    frames_used = q["frames"][:n_total]
    if closed:
        audited = audit_closed_loop(frames_used)
        active_frames = audited["active_frames"]
        ghost_frame = audited["ghost_frame"]
        m = audited["metrics"]
        print(f"[AUDIT] {anim['id']} ({n_active}+1f) | F{n_active}<->F{n_total}(Ghost)={m['fN_vs_ghost_iou']:.2f} | F{n_total}<->F1={m['ghost_vs_f1_iou']:.2f} | F{n_active}->F1={m['fN_vs_f1_iou']:.2f} (avgStep={m['avg_step_iou']:.2f})")
        audit_img = make_loop_audit_preview(frames_used, cols=cols, rows=rows, scale=4)
        audit_img.save(out_dir / f"{prefix}_loop_audit_4x.png")
    else:
        active_frames = frames_used
        ghost_frame = None
        m = {}

    strip_1x = pack_horizontal_strip(active_frames)
    strip_1x.save(out_dir / f"{prefix}_{cell}px.png")
    make_checkerboard_preview(strip_1x, scale=4).save(out_dir / f"{prefix}_strip_checker_4x.png")
    if ghost_frame is not None:
        ghost_frame.save(out_dir / f"{prefix}_ghost_frame_{cell}px.png")

    meta = {
        "generator": "PixelSprite 2.0 (Variable-Length Closed-Loop + Hitstop)",
        "id": anim["id"],
        "name": anim["name"],
        "key": anim.get("key", anim["id"].upper()),
        "cellSize": cell,
        "frameCount": len(active_frames),
        "closedLoop": closed,
        "ghostFrameExcluded": closed,
        "auditGrid": [cols, rows],
        "timingMode": anim.get("timing_mode", "hitstop"),
        "frameDurationsMs": anim["frame_durations_ms"],
        "holdTags": anim.get("hold_tags", {}),
        "scrollSpeed": anim.get("scroll_speed", 0),
        "loopAudit": m,
        "palette": pal_hex,
        "stripFile": f"{prefix}_{cell}px.png",
        "ghostFile": f"{prefix}_ghost_frame_{cell}px.png" if ghost_frame else None,
    }
    (out_dir / f"{prefix}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[EXPORT] Clean {len(active_frames)}-frame strip (Ghost dropped): {out_dir / f'{prefix}_{cell}px.png'}")
    print(f"[EXPORT] Closed-loop audit grid: {out_dir / f'{prefix}_loop_audit_4x.png'}")
    return 0


def cmd_showcase_v2(args: argparse.Namespace) -> int:
    """Render a 60 FPS Variable-Timing + Closed-Loop Seam Audit MP4 from a 9x4 pack meta and/or individual action metas!"""
    clips = []
    for mp in args.metas:
        meta_path = Path(mp)
        base = meta_path.parent
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        cell = int(meta["cellSize"])

        if "animations" in meta and meta.get("generatedCols") == 9:
            # 9x4 Closed-Loop pack
            full_9 = Image.open(base / f"{meta['packId']}_9col_with_ghost_{cell}px.png").convert("RGBA")
            for anim in meta["animations"]:
                r = int(anim["row"])
                row_frames = [full_9.crop((c * cell, r * cell, (c + 1) * cell, (r + 1) * cell)) for c in range(9)]
                clips.append({
                    "title": f"[{anim['key']}] {anim['name']} ({anim['frameCount']}帧)",
                    "subtitle": anim["name"],
                    "active_frames": row_frames[:8],
                    "ghost_frame": row_frames[8],
                    "audit_grid_cols": 9,
                    "audit_grid_rows": 1,
                    "durations_ms": anim["frameDurationsMs"],
                    "hold_tags": anim.get("holdTags", {}),
                    "timing_mode": anim.get("timingMode", "even"),
                    "seam_metrics": anim.get("loopAudit", {}),
                    "scroll_speed": anim.get("scrollSpeed", 0),
                    "loops": args.loops,
                })
        else:
            # Single variable-length action meta (e.g. 11f on 4x3 or 14f on 5x3)
            strip = Image.open(base / meta["stripFile"]).convert("RGBA")
            n = int(meta["frameCount"])
            act_frames = [strip.crop((i * cell, 0, (i + 1) * cell, cell)) for i in range(n)]
            ghost_im = Image.open(base / meta["ghostFile"]).convert("RGBA") if meta.get("ghostFile") and (base / meta["ghostFile"]).is_file() else None
            g_cols, g_rows = meta.get("auditGrid", [len(act_frames) + (1 if ghost_im else 0), 1])
            clips.append({
                "title": f"[{meta['key']}] {meta['name']}",
                "subtitle": meta["name"],
                "active_frames": act_frames,
                "ghost_frame": ghost_im,
                "audit_grid_cols": g_cols,
                "audit_grid_rows": g_rows,
                "durations_ms": meta["frameDurationsMs"],
                "hold_tags": meta.get("holdTags", {}),
                "timing_mode": meta.get("timingMode", "hitstop"),
                "seam_metrics": meta.get("loopAudit", {}),
                "scroll_speed": meta.get("scrollSpeed", 0),
                "loops": args.loops,
            })

    render_variable_timing_showcase_mp4(clips, Path(args.out), fps_video=60)
    return 0


# === Legacy v1 8x8 commands preserved for full backward compatibility ===
def _save_module_outputs(full_8x8, mod_spec, palette, char_desc, out_dir: Path, prefix: str, export_rows: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)
    cell = full_8x8["cell_size"]
    atlas_1x = full_8x8["atlas"]
    atlas_1x.save(out_dir / f"{prefix}_{cell}px.png")
    upscale_crisp(atlas_1x, 4).save(out_dir / f"{prefix}_4x.png")
    make_checkerboard_preview(atlas_1x, 4).save(out_dir / f"{prefix}_checker_4x.png")
    meta = {
        "generator": "PixelSprite 2.0",
        "moduleId": prefix,
        "moduleName": mod_spec.get("name", prefix),
        "moduleNameZh": mod_spec.get("name_zh", mod_spec.get("name", prefix)),
        "charDesc": char_desc,
        "cellSize": cell,
        "cols": 8,
        "rows": 8,
        "sheetWidth": atlas_1x.width,
        "sheetHeight": atlas_1x.height,
        "palette": [rgb_to_hex(c) for c in palette],
        "animations": [
            {
                "row": i,
                "id": r["id"],
                "name": r["name"],
                "key": r.get("key", f"R{i + 1}"),
                "fps": r.get("fps", 12),
                "frameDurationsMs": r.get("frame_durations_ms"),
                "frameCount": 8,
                "y": i * cell,
            }
            for i, r in enumerate(mod_spec["rows"])
        ],
    }
    (out_dir / f"{prefix}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    if export_rows:
        rows_dir = out_dir / f"{prefix}_rows"
        rows_dir.mkdir(exist_ok=True)
        for i, r in enumerate(mod_spec["rows"]):
            atlas_1x.crop((0, i * cell, 8 * cell, (i + 1) * cell)).save(rows_dir / f"{i + 1:02d}_{r['id']}_8f.png")
    return meta


def cmd_generate(args: argparse.Namespace) -> int:
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]
    colors = args.colors or style["palette_colors"]
    fill = args.fill or style["fill_ratio"]
    mod_spec = load_module_spec(args.module)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = Path(args.raw_dir) if args.raw_dir else (out_dir / "_raw_cache")
    raw_dir.mkdir(parents=True, exist_ok=True)
    _, api_ref, palette = _load_anchor_and_palette(args.anchor, cell, fill, colors, not args.no_outline)
    pal_hex = [rgb_to_hex(c) for c in palette]
    prefix = args.prefix or Path(args.module).stem

    cfg = None if args.requantize_only else resolve_api_config(args.api_url, args.api_key, args.model)
    raw_halves = []
    for batch_idx in (0, 1):
        raw_path = raw_dir / f"{prefix}_half{batch_idx}_raw_8x4.png"
        if args.requantize_only and raw_path.is_file():
            raw_img = Image.open(raw_path).convert("RGBA")
        else:
            assert cfg is not None
            guide_img = render_batch_8x4_guide(mod_spec, batch_index=batch_idx)
            prompt = compile_batch_8x4_prompt(args.desc, args.style, mod_spec, batch_idx, palette_hex=pal_hex)
            raw_img = edit_images(prompt, [api_ref, guide_img], cfg, size="1536x1024")
            raw_img.save(raw_path)
        raw_halves.append(raw_img)

    q_opts = dict(cols=8, rows=4, cell_size=cell, fill_ratio=fill, inset_pct=args.inset, palette=palette, lock_palette=not args.no_palette_lock, outline=not args.no_outline, preserve_vfx=True)
    full = combine_halves_to_8x8(quantize_grid(raw_halves[0], **q_opts), quantize_grid(raw_halves[1], **q_opts))
    meta = _save_module_outputs(full, mod_spec, palette, args.desc, out_dir, prefix, export_rows=args.export_rows)
    if args.video:
        render_showcase_mp4([{"atlas": full["atlas"], "meta": meta, "loops_per_row": 2}], Path(args.video))
    return 0


def cmd_showcase(args: argparse.Namespace) -> int:
    items = [
        {"atlas": Image.open(sp).convert("RGBA"), "meta": json.loads(Path(mp).read_text(encoding="utf-8")), "loops_per_row": args.loops}
        for sp, mp in zip(args.sheets, args.metas)
    ]
    render_showcase_mp4(items, Path(args.out))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pixelsprite", description="PixelSprite v2.0 — Closed-Loop (N+1) Variable-Frame & Hitstop Pixel Sprite Pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List pixel styles, closed-loop variable animations, packs, and 8x8 modules").set_defaults(func=cmd_list)

    def add_api(sp):
        sp.add_argument("--api-url", default=None)
        sp.add_argument("--api-key", default=None)
        sp.add_argument("--model", default=None)

    def add_quant(sp):
        sp.add_argument("--style", default="gba_48", choices=list(PIXEL_STYLES.keys()))
        sp.add_argument("--cell", type=int, default=None)
        sp.add_argument("--colors", type=int, default=None)
        sp.add_argument("--fill", type=float, default=None)
        sp.add_argument("--no-outline", action="store_true")

    sp_a = sub.add_parser("anchor", help="Generate or quantize Master Pixel Anchor")
    sp_a.add_argument("--desc", default="")
    sp_a.add_argument("--input-image", default=None)
    sp_a.add_argument("--module", default="core_8x8")
    sp_a.add_argument("--out", required=True)
    add_quant(sp_a); add_api(sp_a)
    sp_a.set_defaults(func=cmd_anchor)

    sp_p = sub.add_parser("pack9", help="v2.0: Generate Closed-Loop 9x4 pack (8 active + Col 9 Ghost=F1), audit F8<->F9, drop ghost")
    sp_p.add_argument("--anchor", required=True)
    sp_p.add_argument("--desc", required=True)
    sp_p.add_argument("--pack", default="core_9x4_closed", choices=list(CLOSED_LOOP_PACKS.keys()))
    sp_p.add_argument("--prefix", default=None)
    sp_p.add_argument("--out", required=True)
    sp_p.add_argument("--inset", type=float, default=3.0)
    sp_p.add_argument("--no-palette-lock", action="store_true")
    sp_p.add_argument("--requantize-only", action="store_true")
    add_quant(sp_p); add_api(sp_p)
    sp_p.set_defaults(func=cmd_closed_loop_pack)

    sp_act = sub.add_parser("action", help="v2.0: Generate Variable-Length Closed-Loop Action (e.g. 11+1f or 14+1f) with Hitstop Timing")
    sp_act.add_argument("--anchor", required=True)
    sp_act.add_argument("--desc", required=True)
    sp_act.add_argument("--anim", required=True, help="Animation ID (skill_phantom_flurry, ult_starfall_slash, ...) or custom JSON path")
    sp_act.add_argument("--prefix", default=None)
    sp_act.add_argument("--out", required=True)
    sp_act.add_argument("--inset", type=float, default=2.5)
    sp_act.add_argument("--no-palette-lock", action="store_true")
    sp_act.add_argument("--requantize-only", action="store_true")
    add_quant(sp_act); add_api(sp_act)
    sp_act.set_defaults(func=cmd_action)

    sp_sv2 = sub.add_parser("showcase-v2", help="v2.0: Render 60 FPS Variable-Timing + Closed-Loop Seam Audit MP4")
    sp_sv2.add_argument("--metas", nargs="+", required=True, help="One or more pack9 / action *_meta.json files")
    sp_sv2.add_argument("--loops", type=int, default=2)
    sp_sv2.add_argument("--out", required=True)
    sp_sv2.set_defaults(func=cmd_showcase_v2)

    sp_g = sub.add_parser("generate", help="Generate a legacy 8x8 (64-frame) module")
    sp_g.add_argument("--anchor", required=True)
    sp_g.add_argument("--desc", required=True)
    sp_g.add_argument("--module", default="core_8x8")
    sp_g.add_argument("--prefix", default=None)
    sp_g.add_argument("--out", required=True)
    sp_g.add_argument("--raw-dir", default=None)
    sp_g.add_argument("--inset", type=float, default=3.0)
    sp_g.add_argument("--no-palette-lock", action="store_true")
    sp_g.add_argument("--export-rows", action="store_true")
    sp_g.add_argument("--requantize-only", action="store_true")
    sp_g.add_argument("--video", default=None)
    add_quant(sp_g); add_api(sp_g)
    sp_g.set_defaults(func=cmd_generate)

    sp_s = sub.add_parser("showcase", help="Render legacy 8x8 Skill-Bar HUD MP4")
    sp_s.add_argument("--sheets", nargs="+", required=True)
    sp_s.add_argument("--metas", nargs="+", required=True)
    sp_s.add_argument("--loops", type=int, default=2)
    sp_s.add_argument("--out", required=True)
    sp_s.set_defaults(func=cmd_showcase)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
