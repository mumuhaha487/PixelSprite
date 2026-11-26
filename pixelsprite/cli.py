"""Command-line interface for PixelSprite — AI-Native 16-bit 8x8 Pixel Sprite & Skill Workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

from .api import edit_images, generate_image, resolve_api_config
from .guide import render_batch_8x4_guide
from .presets import (
    PIXEL_STYLES,
    SHEET_MODULES,
    compile_anchor_prompt,
    compile_batch_8x4_prompt,
    load_module_spec,
)
from .quantizer import (
    combine_halves_to_8x8,
    extract_master_palette,
    make_checkerboard_preview,
    quantize_anchor,
    quantize_grid,
    rgb_to_hex,
    upscale_crisp,
)
from .showcase import render_showcase_mp4


def _save_module_outputs(
    full_8x8: dict,
    mod_spec: dict,
    palette: list[list[int]],
    char_desc: str,
    out_dir: Path,
    prefix: str,
    export_rows: bool = False,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cell = full_8x8["cell_size"]
    atlas_1x: Image.Image = full_8x8["atlas"]

    p_1x = out_dir / f"{prefix}_{cell}px.png"
    p_4x = out_dir / f"{prefix}_4x.png"
    p_chk = out_dir / f"{prefix}_checker_4x.png"
    p_meta = out_dir / f"{prefix}_meta.json"

    atlas_1x.save(p_1x)
    upscale_crisp(atlas_1x, 4).save(p_4x)
    make_checkerboard_preview(atlas_1x, 4).save(p_chk)

    meta = {
        "generator": "PixelSprite 1.0",
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
                "frameCount": 8,
                "y": i * cell,
            }
            for i, r in enumerate(mod_spec["rows"])
        ],
    }
    p_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if export_rows:
        rows_dir = out_dir / f"{prefix}_rows"
        rows_dir.mkdir(exist_ok=True)
        for i, r in enumerate(mod_spec["rows"]):
            strip = atlas_1x.crop((0, i * cell, 8 * cell, (i + 1) * cell))
            strip.save(rows_dir / f"{i + 1:02d}_{r['id']}_8f.png")

    print(f"[EXPORT] 1:1 atlas: {p_1x} ({atlas_1x.width}x{atlas_1x.height})")
    print(f"[EXPORT] 4x preview: {p_chk}")
    print(f"[EXPORT] metadata: {p_meta}")
    return meta


def cmd_list(_args: argparse.Namespace) -> int:
    print("=== Pixel Styles ===")
    for k, v in PIXEL_STYLES.items():
        print(f"  {k:12s} | cell={v['cell_size']}px | colors={v['palette_colors']} | {v['label']}")
    print("\n=== Built-in 8x8 (64-Frame) Modules ===")
    for k, m in SHEET_MODULES.items():
        print(f"  {k:18s} | {m['name']} ({m['name_zh']})")
        for idx, r in enumerate(m["rows"]):
            print(f"      Row {idx + 1}: [{r['key']}] {r['id']} — {r['name']} ({r['fps']} FPS)")
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
            raise ValueError("Provide --desc (text-to-pixel) or --input-image (existing character image).")
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

    anchor_img = Image.open(args.anchor).convert("RGBA")
    if anchor_img.width <= 128:
        palette = extract_master_palette(anchor_img, max_colors=colors)
        zoom = max(1, 440 // anchor_img.width)
        api_ref = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        ds = anchor_img.width * zoom
        api_ref.paste(anchor_img.resize((ds, ds), Image.Resampling.NEAREST), ((512 - ds) // 2, (512 - ds) // 2))
    else:
        q_anc = quantize_anchor(anchor_img, cell_size=cell, fill_ratio=fill, max_colors=colors, outline=not args.no_outline)
        palette = q_anc["palette"]
        api_ref = q_anc["api_ref"]

    pal_hex = [rgb_to_hex(c) for c in palette]
    prefix = args.prefix or Path(args.module).stem

    cfg = None if args.requantize_only else resolve_api_config(args.api_url, args.api_key, args.model)
    raw_halves: list[Image.Image] = []
    for batch_idx in (0, 1):
        raw_path = raw_dir / f"{prefix}_half{batch_idx}_raw_8x4.png"
        if args.requantize_only and raw_path.is_file():
            print(f"[GEN] Reusing cached raw half {batch_idx}: {raw_path}")
            raw_img = Image.open(raw_path).convert("RGBA")
        else:
            assert cfg is not None
            guide_img = render_batch_8x4_guide(mod_spec, batch_index=batch_idx)
            prompt = compile_batch_8x4_prompt(args.desc, args.style, mod_spec, batch_idx, palette_hex=pal_hex)
            print(f"[GEN] Calling {cfg['model']} ({batch_idx + 1}/2) for {prefix} rows {batch_idx * 4 + 1}-{batch_idx * 4 + 4} (32 frames)...")
            raw_img = edit_images(prompt, [api_ref, guide_img], cfg, size="1536x1024")
            raw_img.save(raw_path)
        raw_halves.append(raw_img)

    q_opts = dict(
        cols=8,
        rows=4,
        cell_size=cell,
        fill_ratio=fill,
        inset_pct=args.inset,
        palette=palette,
        lock_palette=not args.no_palette_lock,
        outline=not args.no_outline,
        preserve_vfx=True,
    )
    top_q = quantize_grid(raw_halves[0], **q_opts)
    bot_q = quantize_grid(raw_halves[1], **q_opts)
    full = combine_halves_to_8x8(top_q, bot_q)

    meta = _save_module_outputs(full, mod_spec, palette, args.desc, out_dir, prefix, export_rows=args.export_rows)
    if args.video:
        render_showcase_mp4(
            [{"atlas": full["atlas"], "meta": meta, "loops_per_row": 2}],
            Path(args.video),
        )
    return 0


def cmd_quantize(args: argparse.Namespace) -> int:
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]
    colors = args.colors or style["palette_colors"]
    fill = args.fill or style["fill_ratio"]
    mod_spec = load_module_spec(args.module)
    out_dir = Path(args.out)

    anchor_img = Image.open(args.anchor).convert("RGBA")
    palette = (
        extract_master_palette(anchor_img, max_colors=colors)
        if anchor_img.width <= 128
        else quantize_anchor(anchor_img, cell_size=cell, fill_ratio=fill, max_colors=colors)["palette"]
    )
    q_opts = dict(
        cell_size=cell,
        fill_ratio=fill,
        inset_pct=args.inset,
        palette=palette,
        lock_palette=not args.no_palette_lock,
        outline=not args.no_outline,
        preserve_vfx=True,
    )

    if len(args.raw) == 2:
        top_q = quantize_grid(Image.open(args.raw[0]), cols=8, rows=4, **q_opts)
        bot_q = quantize_grid(Image.open(args.raw[1]), cols=8, rows=4, **q_opts)
        full = combine_halves_to_8x8(top_q, bot_q)
    elif len(args.raw) == 1:
        full = quantize_grid(Image.open(args.raw[0]), cols=8, rows=8, **q_opts)
    else:
        raise ValueError("--raw accepts 1 full 8x8 PNG or 2 half 8x4 PNGs.")

    prefix = args.prefix or Path(args.module).stem
    _save_module_outputs(full, mod_spec, palette, args.desc or "", out_dir, prefix, export_rows=args.export_rows)
    return 0


def cmd_showcase(args: argparse.Namespace) -> int:
    if len(args.sheets) != len(args.metas):
        raise ValueError("Provide an equal number of --sheets and --metas.")
    items = []
    for sp, mp in zip(args.sheets, args.metas):
        items.append({
            "atlas": Image.open(sp).convert("RGBA"),
            "meta": json.loads(Path(mp).read_text(encoding="utf-8")),
            "loops_per_row": args.loops,
        })
    render_showcase_mp4(items, Path(args.out))
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    """One-command full pipeline: Anchor -> N x (8x8 64-frame modules) -> optional MP4 showcase."""
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    style = PIXEL_STYLES.get(args.style, PIXEL_STYLES["gba_48"])
    cell = args.cell or style["cell_size"]

    anchor_1x_path = out_dir / f"01_anchor_pixel_{cell}px.png"
    if not (args.anchor and Path(args.anchor).is_file()):
        anc_ns = argparse.Namespace(
            desc=args.desc,
            input_image=args.input_image,
            style=args.style,
            module=args.modules.split(",")[0].strip(),
            cell=args.cell,
            colors=args.colors,
            fill=args.fill,
            no_outline=args.no_outline,
            out=str(out_dir),
            api_url=args.api_url,
            api_key=args.api_key,
            model=args.model,
        )
        cmd_anchor(anc_ns)
        anchor_path = str(anchor_1x_path)
    else:
        anchor_path = args.anchor

    showcase_items = []
    for idx, mod_id in enumerate([m.strip() for m in args.modules.split(",") if m.strip()]):
        prefix = f"sheet_{idx + 1:02d}_{Path(mod_id).stem}"
        gen_ns = argparse.Namespace(
            anchor=anchor_path,
            desc=args.desc,
            style=args.style,
            module=mod_id,
            cell=args.cell,
            colors=args.colors,
            fill=args.fill,
            inset=args.inset,
            no_palette_lock=args.no_palette_lock,
            no_outline=args.no_outline,
            export_rows=args.export_rows,
            requantize_only=False,
            raw_dir=None,
            prefix=prefix,
            out=str(out_dir),
            video=None,
            api_url=args.api_url,
            api_key=args.api_key,
            model=args.model,
        )
        cmd_generate(gen_ns)
        showcase_items.append({
            "atlas": Image.open(out_dir / f"{prefix}_{cell}px.png").convert("RGBA"),
            "meta": json.loads((out_dir / f"{prefix}_meta.json").read_text(encoding="utf-8")),
            "loops_per_row": 2,
        })

    if args.video:
        render_showcase_mp4(showcase_items, Path(args.video))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pixelsprite",
        description="PixelSprite — AI-Native 16-Bit Low-Res 8x8 (64-Frame) Pixel Sprite & Combat Skill Pipeline",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List built-in pixel styles and 8x8 modules").set_defaults(func=cmd_list)

    def add_common_api(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--api-url", default=None)
        sp.add_argument("--api-key", default=None)
        sp.add_argument("--model", default=None)

    def add_common_quant(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--style", default="gba_48", choices=list(PIXEL_STYLES.keys()))
        sp.add_argument("--cell", type=int, default=None, help="Logical pixel size per frame (32/48/64)")
        sp.add_argument("--colors", type=int, default=None, help="Locked Master Palette size (14-24)")
        sp.add_argument("--fill", type=float, default=None, help="Character height ratio inside cell (0.55-0.85)")
        sp.add_argument("--no-outline", action="store_true")

    # anchor
    sp_a = sub.add_parser("anchor", help="Generate or quantize the Master Pixel Character Anchor")
    sp_a.add_argument("--desc", default="", help="Character appearance description")
    sp_a.add_argument("--input-image", default=None, help="Optional existing character image to pixelize")
    sp_a.add_argument("--module", default="core_8x8")
    sp_a.add_argument("--out", required=True)
    add_common_quant(sp_a)
    add_common_api(sp_a)
    sp_a.set_defaults(func=cmd_anchor)

    # generate
    sp_g = sub.add_parser("generate", help="Generate a full 8x8 (64-frame) module anchored to Master Pixel Anchor")
    sp_g.add_argument("--anchor", required=True, help="Path to quantized Master Anchor PNG")
    sp_g.add_argument("--desc", required=True, help="Character description")
    sp_g.add_argument("--module", default="core_8x8", help="Module ID (core_8x8, skills_8x8, topdown_8dir_8x8) or custom JSON path")
    sp_g.add_argument("--prefix", default=None)
    sp_g.add_argument("--out", required=True)
    sp_g.add_argument("--raw-dir", default=None)
    sp_g.add_argument("--inset", type=float, default=3.0)
    sp_g.add_argument("--no-palette-lock", action="store_true")
    sp_g.add_argument("--export-rows", action="store_true")
    sp_g.add_argument("--requantize-only", action="store_true", help="Skip API calls and re-quantize cached raw 8x4 PNGs")
    sp_g.add_argument("--video", default=None, help="Optional MP4 showcase output path")
    add_common_quant(sp_g)
    add_common_api(sp_g)
    sp_g.set_defaults(func=cmd_generate)

    # quantize
    sp_q = sub.add_parser("quantize", help="Offline quantize 1x(8x8) or 2x(8x4) raw PNGs onto exact pixel grid")
    sp_q.add_argument("--raw", nargs="+", required=True)
    sp_q.add_argument("--anchor", required=True)
    sp_q.add_argument("--module", default="core_8x8")
    sp_q.add_argument("--desc", default="")
    sp_q.add_argument("--prefix", default=None)
    sp_q.add_argument("--out", required=True)
    sp_q.add_argument("--inset", type=float, default=3.0)
    sp_q.add_argument("--no-palette-lock", action="store_true")
    sp_q.add_argument("--export-rows", action="store_true")
    add_common_quant(sp_q)
    sp_q.set_defaults(func=cmd_quantize)

    # showcase
    sp_s = sub.add_parser("showcase", help="Render crisp pixel MP4 showcase with Skill-Bar HUD from quantized 8x8 sheet(s)")
    sp_s.add_argument("--sheets", nargs="+", required=True)
    sp_s.add_argument("--metas", nargs="+", required=True)
    sp_s.add_argument("--loops", type=int, default=2)
    sp_s.add_argument("--out", required=True)
    sp_s.set_defaults(func=cmd_showcase)

    # all
    sp_all = sub.add_parser("all", help="End-to-end: Anchor -> one or more 8x8 modules -> optional MP4 showcase")
    sp_all.add_argument("--desc", required=True)
    sp_all.add_argument("--input-image", default=None)
    sp_all.add_argument("--anchor", default=None, help="Skip anchor generation and reuse an existing anchor PNG")
    sp_all.add_argument("--modules", default="core_8x8,skills_8x8", help="Comma-separated module IDs or JSON paths")
    sp_all.add_argument("--out", required=True)
    sp_all.add_argument("--inset", type=float, default=3.0)
    sp_all.add_argument("--no-palette-lock", action="store_true")
    sp_all.add_argument("--export-rows", action="store_true")
    sp_all.add_argument("--video", default=None)
    add_common_quant(sp_all)
    add_common_api(sp_all)
    sp_all.set_defaults(func=cmd_all)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
