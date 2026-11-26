"""Style presets, 8x8 (64-frame) action/skill/8-dir modules, and prompt compilers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PIXEL_STYLES: dict[str, dict[str, Any]] = {
    "gba_48": {
        "label": "16-bit GBA Chibi Low-Res (48x48 cell, recommended)",
        "cell_size": 48,
        "palette_colors": 18,
        "fill_ratio": 0.72,
        "prompt": (
            "authentic crisp 16-bit GBA / SNES indie RPG chibi pixel art (Legend of Zelda Minish Cap / "
            "Eastward / Celeste style), chunky low-resolution pixel grid (character ~32-36 logical pixels tall), "
            "cute 2-head chibi proportions with large expressive head and compact limbs, crisp 1-pixel dark "
            "purplish-brown outline (#261a2b), clean flat 2-step cel shading using strictly 14-18 vibrant colors, "
            "ZERO anti-aliasing, ZERO blur, ZERO painterly gradients, ZERO pillow shading"
        ),
    },
    "retro_32": {
        "label": "Ultra-Chunky Retro 32x32 (Stardew / Pico-8 style)",
        "cell_size": 32,
        "palette_colors": 14,
        "fill_ratio": 0.78,
        "prompt": (
            "ultra-chunky 32x32 retro indie pixel art (Stardew Valley / Shovel Knight / Pico-8 style), "
            "bold tiny 2-head chibi sprite (~24 logical pixels tall), crisp 1-pixel dark outline, "
            "strictly 12-14 flat solid colors, unmistakable silhouette, zero fine noise, zero blur"
        ),
    },
    "arpg_64": {
        "label": "16-bit Indie ARPG 64x64 (extra room for giant skill VFX)",
        "cell_size": 64,
        "palette_colors": 20,
        "fill_ratio": 0.62,
        "prompt": (
            "crisp 16-bit indie ARPG chibi pixel art (CrossCode / Sea of Stars / Hyper Light Drifter style), "
            "chunky readable pixel clusters (~40 logical pixels tall inside a 64x64 cell leaving generous space "
            "for huge radiant sword skills and magic spells), 2-head chibi proportions, crisp 1-pixel dark outline, "
            "strictly 16-20 clean vibrant colors, zero blur, zero anti-aliasing"
        ),
    },
}

SHEET_MODULES: dict[str, dict[str, Any]] = {
    "core_8x8": {
        "name": "Core Actions & 3-Hit Combo 8x8 (64 frames)",
        "name_zh": "核心动作与三连剑技 8×8（64帧）",
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "rows": [
            {
                "id": "idle",
                "name": "待机 Idle",
                "key": "IDLE",
                "fps": 8,
                "batch": 0,
                "vfx_hint": None,
                "prompt": (
                    "Row 1 (Frames 1-8): Lively breathing IDLE stance facing right — bouncy chibi chest breathing, "
                    "fluttering scarf/hair tips, slight confident weapon bob, knees softly pulsing, feet firmly planted, smooth 8-frame loop"
                ),
            },
            {
                "id": "walk",
                "name": "行走 Walk",
                "key": "WALK",
                "fps": 10,
                "batch": 0,
                "vfx_hint": None,
                "prompt": (
                    "Row 2 (Frames 1-8): Bouncy energetic WALK cycle facing right — full alternating 2-step stride "
                    "(1:R-foot contact, 2:down cushion, 3:passing, 4:up reach, 5:L-foot contact, 6:down cushion, 7:passing, 8:up reach), "
                    "lively swinging arms, bouncing ponytail and fluttering scarf"
                ),
            },
            {
                "id": "run",
                "name": "疾跑 Run",
                "key": "RUN",
                "fps": 12,
                "batch": 0,
                "vfx_hint": None,
                "prompt": (
                    "Row 3 (Frames 1-8): Fast dynamic SPRINT RUN cycle facing right — forward-leaning chibi torso, "
                    "fast alternating kicking boots, scarf & hair streaming horizontally behind, sword held ready back-low"
                ),
            },
            {
                "id": "combo1_slash",
                "name": "普攻一式·横斩",
                "key": "ATK 1",
                "fps": 13,
                "batch": 0,
                "vfx_hint": "arc_right",
                "prompt": (
                    "Row 4 (Frames 1-8): ATTACK COMBO 1 (Quick Horizontal Slash) facing right — 1-2: quick coiled pull-back anticipation, "
                    "3-5: explosive forward lunge with a bright crisp pixel-art cyan-white horizontal crescent slash smear cutting forward, "
                    "6-8: stylish recoil follow-through back to guard"
                ),
            },
            {
                "id": "combo2_uppercut",
                "name": "普攻二式·上挑斩",
                "key": "ATK 2",
                "fps": 13,
                "batch": 1,
                "vfx_hint": "arc_up",
                "prompt": (
                    "Row 1 (Frames 1-8): ATTACK COMBO 2 (Rising Uppercut Slash) facing right — 1-2: low crouched dip holding blade low-back, "
                    "3-5: leaping upward sweep swinging sword from low to high overhead with a glowing bright gold-white rising pixel slash crescent, "
                    "6-8: graceful aerial settle back to stance"
                ),
            },
            {
                "id": "combo3_spin_cleave",
                "name": "普攻三式·跳劈旋斩",
                "key": "ATK 3",
                "fps": 13,
                "batch": 1,
                "vfx_hint": "slam",
                "prompt": (
                    "Row 2 (Frames 1-8): HEAVY FINISHER (Spinning Jump-Cleave Smash) facing right — 1-2: crouch charge with sparkling blade, "
                    "3-4: mid-air forward 360-degree somersault spin with golden motion arcs, "
                    "5-6: dramatic downward slam cleave with big radiant cyan-gold pixel shockwave wave on the right, 7-8: heroic landing recovery"
                ),
            },
            {
                "id": "jump_dash",
                "name": "跳跃冲刺 Jump",
                "key": "JUMP",
                "fps": 11,
                "batch": 1,
                "vfx_hint": "jump",
                "prompt": (
                    "Row 3 (Frames 1-8): JUMP & AIR-DASH arc facing right — 1: squash crouch anticipation, 2-3: upward launch knees tucked, "
                    "4-5: mid-air horizontal dash stretch with fluttering scarf, 6-7: falling descent arms out, 8: bouncy landing squash"
                ),
            },
            {
                "id": "hurt_ko",
                "name": "受击倒地 Hurt/KO",
                "key": "HURT",
                "fps": 9,
                "batch": 1,
                "vfx_hint": "ko",
                "prompt": (
                    "Row 4 (Frames 1-8): HURT recoil into cute dramatic KO collapse facing right — 1-2: startled knockback leaning back, "
                    "3-4: flying backward losing balance, 5-6: tumbling onto ground, 7-8: cute dizzy defeated collapse lying on floor with spinning golden stars"
                ),
            },
        ],
    },
    "skills_8x8": {
        "name": "Flashy ARPG Skills & Ultimates 8x8 (64 frames)",
        "name_zh": "炫酷技能与终极奥义 8×8（64帧）",
        "view_prompt": "classic 2D side-scrolling 3/4 action RPG view, facing RIGHT consistently in every cell",
        "rows": [
            {
                "id": "skill_iaido_blink",
                "name": "Q·居合瞬闪斩",
                "key": "SKILL Q",
                "fps": 14,
                "batch": 0,
                "vfx_hint": "beam_right",
                "prompt": (
                    "Row 1 (Frames 1-8): SKILL Q — IAIDO BLINK LIGHTNING SLASH facing right — "
                    "1-2: low crouched quick-draw stance gripping glowing cyan-white electrified hilt with electric sparks, "
                    "3-4: blinding high-speed cyan afterimage blur darting forward horizontally, "
                    "5-6: explosive razor-sharp glowing cyan-white horizontal lightning sword beam ripping forward across the cell, "
                    "7-8: cool dramatic low-crouch post-slash pose as cyan sparks dissipate"
                ),
            },
            {
                "id": "skill_flame_wave",
                "name": "W·烈焰剑气波",
                "key": "SKILL W",
                "fps": 13,
                "batch": 0,
                "vfx_hint": "arc_right",
                "prompt": (
                    "Row 2 (Frames 1-8): SKILL W — BLAZING FLAME CRESCENT WAVE facing right — "
                    "1-2: rearing sword back overhead while bright orange-gold pixel fire erupts around the blade, "
                    "3-5: massive sweeping forward strike unleashing a giant roaring orange-yellow-white fiery pixel crescent wave surging right with flying embers, "
                    "6-8: dynamic follow-through as trailing fire sparks swirl around her scarf"
                ),
            },
            {
                "id": "skill_ice_rain",
                "name": "E·冰晶剑雨阵",
                "key": "SKILL E",
                "fps": 12,
                "batch": 0,
                "vfx_hint": "sky_cast",
                "prompt": (
                    "Row 3 (Frames 1-8): SKILL E — FROST SWORD RAIN SUMMON facing right — "
                    "1-2: raising sword straight skyward as a glowing cyan-white pixel magic circle blooms beneath her boots, "
                    "3-5: radiant skyward thrust summoning 3-4 sparkling bright cyan-white crystal pixel ice blades & frost shards raining diagonally down-right, "
                    "6-8: crisp crystalline burst impacts with glittering ice dust settling"
                ),
            },
            {
                "id": "skill_phantom_flurry",
                "name": "R·幻影五连乱舞",
                "key": "SKILL R",
                "fps": 15,
                "batch": 0,
                "vfx_hint": "flurry",
                "prompt": (
                    "Row 4 (Frames 1-8): SKILL R — PHANTOM MULTI-SLASH CROSS FLURRY facing right — "
                    "1: quick forward dash lean, 2-6: rapid dazzling anime blade flurry weaving criss-crossing neon cyan, gold, and bright pink-magenta pixel X-slash arcs and afterimage blurs in front of her, "
                    "7-8: explosive cross-cut sparkle flash and crisp landing stance"
                ),
            },
            {
                "id": "skill_thunder_drop",
                "name": "A·雷霆天降落雷",
                "key": "SKILL A",
                "fps": 13,
                "batch": 1,
                "vfx_hint": "slam",
                "prompt": (
                    "Row 1 (Frames 1-8): SKILL A — THUNDER METEOR PLUNGE SLAM facing right — "
                    "1-2: leaping high upward with blade supercharged in bright yellow-blue pixel lightning, "
                    "3-4: meteoric diving plunge straight downward sword-first wrapped in crackling electric gold aura, "
                    "5-6: violent ground impact summoning jagged electric yellow-cyan pixel lightning bolts erupting upward around her, "
                    "7-8: crouched superhero landing as static sparks crackle off"
                ),
            },
            {
                "id": "skill_parry_counter",
                "name": "S·圣盾格挡反击",
                "key": "SKILL S",
                "fps": 13,
                "batch": 1,
                "vfx_hint": "arc_right",
                "prompt": (
                    "Row 2 (Frames 1-8): SKILL S — GOLDEN AEGIS PARRY & COUNTER-THRUST facing right — "
                    "1-3: bracing sword vertically in front summoning a shimmering golden-white curved pixel energy shield barrier blocking impact with bright star flash, "
                    "4-6: instant explosive golden piercing lunge thrust shooting a radiant lance-like gold-white pixel shock cone straight right, "
                    "7-8: swift composed guard recovery"
                ),
            },
            {
                "id": "skill_aura_burst",
                "name": "D·剑意觉醒爆气",
                "key": "BUFF D",
                "fps": 12,
                "batch": 1,
                "vfx_hint": "aura",
                "prompt": (
                    "Row 3 (Frames 1-8): SKILL D — LIMIT-BREAK AURA AWAKENING BURST facing right — "
                    "1-2: crouching tightly holding sword close while swirling cyan-gold pixel energy particles pull inward, "
                    "3-6: dramatic power-up eruption — scarf and ponytail whipping skyward inside a blazing concentric cyan-gold-white pixel flame aura pillar and ground shockwave ring, "
                    "7-8: empowered heroic stance surrounded by floating golden sparkles"
                ),
            },
            {
                "id": "ult_starfall_slash",
                "name": "F·终极奥义·星陨次元斩",
                "key": "ULT F",
                "fps": 14,
                "batch": 1,
                "vfx_hint": "ultimate",
                "prompt": (
                    "Row 4 (Frames 1-8): ULTIMATE F — STARFALL DIMENSION NOVA SLASH facing right — "
                    "1-2: levitating off the ground charging a brilliant golden-cyan star halo around her raised sword, "
                    "3-5: unleashing an awe-inspiring huge luminous cyan, magenta, and golden-white 4-point star-cross dimensional slash explosion tearing across the front, "
                    "6-7: dazzling bright nova shatter bursts with sparkling starlight pixels, "
                    "8: stylish heroic sword-sheath victory pose facing right"
                ),
            },
        ],
    },
    "topdown_8dir_8x8": {
        "name": "Top-Down 8-Direction RPG Run 8x8 (64 frames)",
        "name_zh": "俯视角 8 方向奔跑 8×8（64帧）",
        "view_prompt": (
            "classic 3/4 top-down 16-bit RPG view (Legend of Zelda Minish Cap / Stardew / Alundra camera angle), "
            "consistent slightly elevated overhead perspective"
        ),
        "rows": [
            {"id": "dir_s", "name": "朝下跑 S (↓)", "key": "S", "fps": 12, "batch": 0, "vfx_hint": None,
             "prompt": "Row 1 (Frames 1-8): Running DOWN toward the camera (South, front view) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_sw", "name": "朝左下跑 SW (↙)", "key": "SW", "fps": 12, "batch": 0, "vfx_hint": None,
             "prompt": "Row 2 (Frames 1-8): Running DOWN-LEFT (South-West 3/4 view) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_w", "name": "朝左跑 W (←)", "key": "W", "fps": 12, "batch": 0, "vfx_hint": None,
             "prompt": "Row 3 (Frames 1-8): Running LEFT (West side profile) — smooth 8-frame alternating run cycle, scarf streaming right"},
            {"id": "dir_nw", "name": "朝左上跑 NW (↖)", "key": "NW", "fps": 12, "batch": 0, "vfx_hint": None,
             "prompt": "Row 4 (Frames 1-8): Running UP-LEFT (North-West 3/4 back-left view) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_n", "name": "朝上跑 N (↑)", "key": "N", "fps": 12, "batch": 1, "vfx_hint": None,
             "prompt": "Row 1 (Frames 1-8): Running UP away from camera (North, pure back view) — smooth 8-frame alternating run cycle showing back of ponytail & scarf"},
            {"id": "dir_ne", "name": "朝右上跑 NE (↗)", "key": "NE", "fps": 12, "batch": 1, "vfx_hint": None,
             "prompt": "Row 2 (Frames 1-8): Running UP-RIGHT (North-East 3/4 back-right view) — smooth 8-frame alternating chibi run cycle"},
            {"id": "dir_e", "name": "朝右跑 E (→)", "key": "E", "fps": 12, "batch": 1, "vfx_hint": None,
             "prompt": "Row 3 (Frames 1-8): Running RIGHT (East side profile) — smooth 8-frame alternating run cycle, scarf streaming left"},
            {"id": "dir_se", "name": "朝右下跑 SE (↘)", "key": "SE", "fps": 12, "batch": 1, "vfx_hint": None,
             "prompt": "Row 4 (Frames 1-8): Running DOWN-RIGHT (South-East 3/4 front-right view) — smooth 8-frame alternating chibi run cycle"},
        ],
    },
}


def load_module_spec(module_id_or_path: str) -> dict[str, Any]:
    """Load a built-in module by ID or a custom 8-row module JSON file."""
    if module_id_or_path in SHEET_MODULES:
        return SHEET_MODULES[module_id_or_path]
    p = Path(module_id_or_path)
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        for idx, row in enumerate(data["rows"]):
            row.setdefault("batch", 0 if idx < 4 else 1)
            row.setdefault("fps", 12)
            row.setdefault("key", f"ROW {idx + 1}")
            row.setdefault("vfx_hint", None)
        return data
    raise ValueError(f"Unknown module '{module_id_or_path}'. Built-ins: {', '.join(SHEET_MODULES.keys())}")


def compile_anchor_prompt(char_desc: str, style_id: str = "gba_48", module_id: str = "core_8x8") -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    mod = load_module_spec(module_id)
    return "\n".join([
        "Single centered Master Character Pixel Sprite on a pure transparent background (NO grid, NO text, NO floor shadow, NO props).",
        f"Character design: {char_desc.strip()}.",
        f"Camera angle: {mod['view_prompt']}.",
        f"Pixel art specification: {style['prompt']}.",
        "Composition: Character centered with generous transparent padding (~65% of image height), crisp chunky oversized square pixels clearly visible, iconic 2-head chibi silhouette so every color, scarf, hairstyle, and weapon reads unmistakably at 32-48 logical pixels tall!",
    ])


def compile_batch_8x4_prompt(
    char_desc: str,
    style_id: str,
    module_spec: dict[str, Any],
    batch_index: int,
    palette_hex: list[str] | None = None,
) -> str:
    style = PIXEL_STYLES.get(style_id, PIXEL_STYLES["gba_48"])
    batch_rows = [r for r in module_spec["rows"] if r["batch"] == batch_index]
    pal_rule = (
        f"STRICTLY LOCK the character's hair, skin, outfit, scarf, boots, and weapon colors to Image 1 ({', '.join(palette_hex[:16])}), "
        "while allowing vivid pure pixel-art VFX energy colors (bright white, cyan, gold, fire-orange, magenta) ONLY for glowing skill/slash effects!"
        if palette_hex
        else "STRICTLY LOCK all character colors 100% identically to Reference Image 1 (bright VFX colors allowed only for magic/slash effects)."
    )
    return "\n".join([
        "EXACT 8 columns by 4 rows (32 frames total) 16-bit CHUNKY LOW-RES PIXEL ART GAME SPRITE SHEET on a pure transparent background.",
        "Reference Image 1 is the EXACT Master Character Pixel Sprite — keep the EXACT same chunky pixel size, 2-head chibi proportion, face, hair, scarf, outfit, boots, weapon, and 1-pixel dark outline in EVERY SINGLE ONE of the 32 frames.",
        "Reference Image 2 is the EXACT 8x4 cell layout & ground baseline guide — place 1 single sprite inside each of the 32 cells with generous empty transparent space between cells so adjacent frames NEVER touch or bleed into each other. DO NOT draw any grid lines, boxes, numbers, or colored guide shapes in the output.",
        f"Character: {char_desc.strip()}.",
        f"Viewpoint: {module_spec['view_prompt']}.",
        "THE 4 ROWS (strictly 8 continuous left-to-right frames per row):",
        *[f"- {r['prompt']}" for r in batch_rows],
        "CRITICAL CONSISTENCY RULES:",
        "1. Keep the EXACT same character chibi height (~32-36 logical pixels tall) and pixel grid density across all 32 frames — NO shrinking, NO zooming, NO realistic anatomy drift.",
        f"2. {pal_rule}",
        "3. Every skill/attack row must look super dynamic, expressive, and impactful with crisp hand-pixelled motion smears, glowing pixel energy arcs, sparks, and readable anticipation -> peak flash -> stylish recovery.",
        f"4. Style lock: {style['prompt']}.",
    ])
