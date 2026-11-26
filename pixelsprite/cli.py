"""Command-line interface for PixelSprite v2.1 — Spacious Closed-Loop (N+1 Ghost), Body-Isolated Alignment & Selective Hitstop Timing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

from .api import edit_images, generate_image, resolve_api_config
from .guide import render_variable_action_guide
from .presets import (
    ANIMATION_SPECS,
    PIXEL_STYLES,
    compile_anchor_prompt,
    compile_variable_action_prompt,
    load_animation_spec,
)
from .quantizer import (
    audit_closed_loop,
    extract_master_palette,
    make_checkerboard_preview,
    make_loop_audit_preview,
    pack_horizontal_strip,
    quantize_anchor,
    quantize_grid,
    rgb_to_hex,
)
from .showcase import render_variable_timing_showcase_mp4


def _load_anchor_and_palette(anchor_path: str, cell: int, char_h: int, colors: int, outline: bool):
    anchor_img = Image.open(anchor_path).convert("RGBA")
    if anchor_img.width <= 128:
        palette = extract_master_palette(anchor_img, max_colors=colors)
        bbox = anchor_img.getbbox()
        tight = anchor_img.crop(bbox) if bbox else anchor_img
        zoom = max(1, 380 // max(tight.width, tight.height))
        api_ref = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        dw, dh = tight.width * zoom, tight.height * zoom
        api_ref.paste(tight.resize((dw, dh), Image.Resampling.NEAREST), ((512 - dw) // 2, (512 - dh) // 2))
        return anchor_img, api_ref, palette
    q_anc = quantize_anchor(anchor_img, cell_size=cell, char_height_px=char_h, max_colors=colors, outline=outline)
    return q_anc["pixel_1x"], q_anc["api_ref"], q_anc["palette"]


def cmd_list(_args: argparse.Namespace) -> int:
    print("=== Pixel Styles ===")
    for k, v in PIXEL_STYLES.items():
        print(f"  {k:12s} | cell={v['cell_size']}px | charH={v['char_height_px']}px | colors={v['palette_colors']} | {v['label']}")
    print("\n=== v2.1 Spacious Closed-Loop Variable-Length Animations (N Active + 1 Ghost=F1) ===")
    for k, a in ANIMATION_SPECS.items():
        g = f"{a['grid'][0]}x{a['grid'][1]} ({a['api_size']})"
        total_ms = sum(a["frame_durations_ms"])
        holds = ", ".join(f"F{fi}:{tag}({a['frame_durations_ms'][fi-1]}ms)" for fi, tag in a.get("hold_tags", {}).items()) or "匀速 EVEN"
        print(f"  {k:22s} | {a['active_frames']:2d}+1f | {g:16s} | {total_ms:4d}ms | {holds}")
    return 0


def cmd_anchor(args: argparse.Namespace) -> int:
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_chibi"])
    cell = args.cell or style["cell_size"]
    char_h = args.char_height or style["char_height_px"]
    colors = args.colors or style["palette_colors"]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.input_image:
        raw_img = Image.open(args.input_image).convert("RGBA")
        print(f"[ANCHOR] Quantizing existing image: {args.input_image}")
    else:
        if not args.desc:
            raise ValueError("Provide --desc or --input-image.")
        cfg = resolve_api_config(args.api_url, args.api_key, args.model)
        prompt = compile_anchor_prompt(args.desc, args.style)
        print(f"[ANCHOR] Calling {cfg['model']} to generate chunky pixel Master Anchor...")
        raw_img = generate_image(prompt, cfg, size="1024x1024")
        raw_img.save(out_dir / "00_anchor_raw.png")

    res = quantize_anchor(raw_img, cell_size=cell, char_height_px=char_h, max_colors=colors, outline=not args.no_outline)
    res["pixel_1x"].save(out_dir / f"01_anchor_pixel_{cell}px.png")
    res["api_ref"].save(out_dir / "01_anchor_preview_512px.png")
    (out_dir / "01_palette.json").write_text(
        json.dumps({"cellSize": cell, "charHeightPx": char_h, "palette": res["palette"], "paletteHex": res["palette_hex"]}, indent=2),
        encoding="utf-8",
    )
    print(f"[ANCHOR] Saved {cell}x{cell} anchor (charH={char_h}px, {len(res['palette'])} colors) to {out_dir}")
    return 0


def cmd_action(args: argparse.Namespace) -> int:
    """Generate or re-quantize ANY spacious Closed-Loop Variable-Length Action (3x3 = 8+1f, 4x3 = 11+1f, 5x3 = 14+1f)."""
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_chibi"])
    cell = args.cell or style["cell_size"]
    char_h = args.char_height or style["char_height_px"]
    colors = args.colors or style["palette_colors"]
    anim = load_animation_spec(args.anim)

    cols, rows = anim["grid"]
    api_size = anim.get("api_size", "1536x1024")
    n_active = int(anim["active_frames"])
    closed = bool(anim.get("closed_loop", True))
    n_total = n_active + (1 if closed else 0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "_raw_cache"
    raw_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or f"anim_{anim['id']}_{n_active}f"

    anchor_1x, api_ref, palette = _load_anchor_and_palette(args.anchor, cell, char_h, colors, not args.no_outline)
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
        print(f"[ACTION] Calling {cfg['model']} for {anim['id']} ({n_active}+1f on {cols}x{rows} @ {api_size})...")
        raw_img = edit_images(prompt, [api_ref, guide_img], cfg, size=api_size)
        raw_img.save(raw_path)

    q = quantize_grid(
        raw_img,
        cols=cols,
        rows=rows,
        cell_size=cell,
        char_height_px=char_h,
        inset_pct=args.inset,
        palette=palette,
        lock_palette=not args.no_palette_lock,
        outline=not args.no_outline,
        preserve_vfx=True,
        lock_body_x=bool(anim.get("lock_body_x", False)),
        allow_airborne=bool(anim.get("allow_airborne", False)),
        max_lift_px=float(anim.get("max_lift_px", 24.0)),
        anchor_x_ratio=float(anim.get("anchor_x_ratio", 0.44)),
    )

    frames_used = q["frames"][:n_total]
    if closed:
        audited = audit_closed_loop(frames_used, palette=palette)
        active_frames = audited["active_frames"]
        ghost_frame = audited["ghost_frame"]
        m = audited["metrics"]
        status_tag = "PASS" if m["seam_smooth"] else "WARN"
        print(
            f"[AUDIT {status_tag}] {anim['id']:20s} ({n_active}+1f) | "
            f"F{n_active}<->F{n_total} rgb={m['fN_vs_ghost_rgb']:.2f} | "
            f"F{n_total}<->F1 rgb={m['ghost_vs_f1_rgb']:.2f} | "
            f"F{n_active}->F1 rgb={m['fN_vs_f1_rgb']:.2f} | "
            f"maxBodyDX={m['max_body_dx_px']:.1f}px | bodyH={m['body_h_min_max']}"
        )
        audit_img = make_loop_audit_preview(frames_used, cols=cols, rows=rows, scale=3)
        audit_img.save(out_dir / f"{prefix}_loop_audit_3x.png")
    else:
        active_frames = frames_used
        ghost_frame = None
        m = {}

    strip_1x = pack_horizontal_strip(active_frames)
    strip_1x.save(out_dir / f"{prefix}_{cell}px.png")
    make_checkerboard_preview(strip_1x, scale=3).save(out_dir / f"{prefix}_strip_checker_3x.png")
    if ghost_frame is not None:
        ghost_frame.save(out_dir / f"{prefix}_ghost_frame_{cell}px.png")

    meta = {
        "generator": "PixelSprite 2.1 (Body-Isolated Closed-Loop + Variable-Length + Hitstop)",
        "id": anim["id"],
        "name": anim["name"],
        "key": anim.get("key", anim["id"].upper()),
        "cellSize": cell,
        "charHeightPx": char_h,
        "anchorXRatio": float(anim.get("anchor_x_ratio", 0.44)),
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
    print(f"[EXPORT] Strip ({len(active_frames)}f @ {cell}x{cell}): {out_dir / f'{prefix}_{cell}px.png'}")
    return 0


def cmd_showcase_v2(args: argparse.Namespace) -> int:
    clips = []
    for mp in args.metas:
        meta_path = Path(mp)
        base = meta_path.parent
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        cell = int(meta["cellSize"])
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
            "anchor_x_ratio": float(meta.get("anchorXRatio", 0.44)),
            "scroll_speed": meta.get("scrollSpeed", 0),
            "loops": args.loops,
        })

    render_variable_timing_showcase_mp4(clips, Path(args.out), fps_video=60)
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    """One-command v2.1 pipeline: Anchor -> spacious closed-loop animations -> 60 FPS showcase MP4."""
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_chibi"])
    cell = args.cell or style["cell_size"]

    if args.anchor and Path(args.anchor).is_file():
        anchor_path = args.anchor
    else:
        cmd_anchor(argparse.Namespace(
            desc=args.desc, input_image=args.input_image, style=args.style,
            cell=args.cell, char_height=args.char_height, colors=args.colors,
            no_outline=args.no_outline, out=str(out_dir),
            api_url=args.api_url, api_key=args.api_key, model=args.model,
        ))
        anchor_path = str(out_dir / f"01_anchor_pixel_{cell}px.png")

    metas = []
    for aid in [x.strip() for x in args.anims.split(",") if x.strip()]:
        spec = load_animation_spec(aid)
        prefix = f"anim_{spec['id']}_{spec['active_frames']}f"
        cmd_action(argparse.Namespace(
            anchor=anchor_path, desc=args.desc, anim=aid, prefix=prefix, out=str(out_dir),
            style=args.style, cell=args.cell, char_height=args.char_height, colors=args.colors,
            inset=args.inset, no_palette_lock=args.no_palette_lock, no_outline=args.no_outline,
            requantize_only=args.requantize_only, api_url=args.api_url, api_key=args.api_key, model=args.model,
        ))
        metas.append(str(out_dir / f"{prefix}_meta.json"))

    if args.video:
        cmd_showcase_v2(argparse.Namespace(metas=metas, loops=args.loops, out=args.video))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pixelsprite", description="PixelSprite v2.1 — Body-Isolated Closed-Loop (N+1) Variable-Frame & Hitstop Pixel Sprite Pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List pixel styles and spacious closed-loop variable animations").set_defaults(func=cmd_list)

    def add_api(sp):
        sp.add_argument("--api-url", default=None)
        sp.add_argument("--api-key", default=None)
        sp.add_argument("--model", default=None)

    def add_quant(sp):
        sp.add_argument("--style", default="gba_chibi", choices=list(PIXEL_STYLES.keys()))
        sp.add_argument("--cell", type=int, default=None, help="Logical canvas size (default 64 for zero VFX clipping)")
        sp.add_argument("--char-height", type=int, default=None, help="Fixed logical character height in px (default 34)")
        sp.add_argument("--colors", type=int, default=None)
        sp.add_argument("--no-outline", action="store_true")

    sp_a = sub.add_parser("anchor", help="Generate or quantize Master Pixel Anchor")
    sp_a.add_argument("--desc", default="")
    sp_a.add_argument("--input-image", default=None)
    sp_a.add_argument("--out", required=True)
    add_quant(sp_a); add_api(sp_a)
    sp_a.set_defaults(func=cmd_anchor)

    sp_act = sub.add_parser("action", help="Generate spacious Closed-Loop Variable-Length Action (3x3=8+1f, 4x3=11+1f, 5x3=14+1f)")
    sp_act.add_argument("--anchor", required=True)
    sp_act.add_argument("--desc", required=True)
    sp_act.add_argument("--anim", required=True)
    sp_act.add_argument("--prefix", default=None)
    sp_act.add_argument("--out", required=True)
    sp_act.add_argument("--inset", type=float, default=2.5)
    sp_act.add_argument("--no-palette-lock", action="store_true")
    sp_act.add_argument("--requantize-only", action="store_true")
    add_quant(sp_act); add_api(sp_act)
    sp_act.set_defaults(func=cmd_action)

    sp_sv2 = sub.add_parser("showcase-v2", help="Render 60 FPS Variable-Timing + Closed-Loop Seam Audit MP4")
    sp_sv2.add_argument("--metas", nargs="+", required=True)
    sp_sv2.add_argument("--loops", type=int, default=3)
    sp_sv2.add_argument("--out", required=True)
    sp_sv2.set_defaults(func=cmd_showcase_v2)

    sp_all = sub.add_parser("all", help="End-to-end: Anchor -> Closed-Loop Variable Actions -> 60 FPS MP4")
    sp_all.add_argument("--desc", required=True)
    sp_all.add_argument("--input-image", default=None)
    sp_all.add_argument("--anchor", default=None)
    sp_all.add_argument("--anims", default="idle,walk,run,combo1_slash,skill_phantom_flurry,ult_starfall_slash")
    sp_all.add_argument("--out", required=True)
    sp_all.add_argument("--inset", type=float, default=2.5)
    sp_all.add_argument("--no-palette-lock", action="store_true")
    sp_all.add_argument("--requantize-only", action="store_true")
    sp_all.add_argument("--loops", type=int, default=3)
    sp_all.add_argument("--video", default=None)
    add_quant(sp_all); add_api(sp_all)
    sp_all.set_defaults(func=cmd_all)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
