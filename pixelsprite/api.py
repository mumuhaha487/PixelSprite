"""Zero-dependency OpenAI Images 2.6 API client (supports official & compatible gateways)."""

from __future__ import annotations

import base64
import io
import json
import os
import re
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from PIL import Image


def _normalize_base_url(raw: str) -> str:
    u = (raw or "https://api.openai.com/v1").strip().rstrip("/")
    if not u.endswith("/v1") and not re.search(r"/v\d+$", u, re.I):
        u += "/v1"
    return u


def resolve_api_config(
    api_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, str]:
    """Resolve API URL, key, and model from CLI flags -> env vars -> local gitignored .env / env.txt."""
    env_url = api_url or os.environ.get("PIXELSPRITE_API_URL") or os.environ.get("OPENAI_BASE_URL")
    env_key = api_key or os.environ.get("PIXELSPRITE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    env_model = model or os.environ.get("PIXELSPRITE_MODEL")

    # Fallback: check local gitignored .env or ../env.txt if env vars are unset
    if not (env_url and env_key):
        cwd = Path.cwd()
        repo_root = Path(__file__).resolve().parent.parent
        candidates = [
            cwd / ".env",
            cwd / "env.txt",
            repo_root / ".env",
            repo_root / "env.txt",
            repo_root.parent / "env.txt",
        ]
        for cand in candidates:
            if not cand.is_file():
                continue
            text = cand.read_text(encoding="utf-8", errors="ignore")
            if not env_url:
                m = re.search(r"(?:PIXELSPRITE_API_URL|OPENAI_BASE_URL|api_url)\s*[:=：]\s*(\S+)", text, re.I)
                if m:
                    env_url = m.group(1).strip().strip('"').strip("'")
            if not env_key:
                m = re.search(r"(?:PIXELSPRITE_API_KEY|OPENAI_API_KEY|api_key)\s*[:=：]\s*(\S+)", text, re.I)
                if m:
                    env_key = m.group(1).strip().strip('"').strip("'")
            if not env_model:
                m = re.search(r"(?:PIXELSPRITE_MODEL|image_model)\s*[:=：]\s*(.+)", text, re.I)
                if m:
                    parts = [s.strip() for s in re.split(r"[,，\s]+", m.group(1).strip()) if s.strip()]
                    sun = next((x for x in parts if "sunburst" in x), parts[0] if parts else None)
                    if sun:
                        env_model = sun
            if env_url and env_key:
                break

    if not env_key:
        raise RuntimeError(
            "Missing API key. Set PIXELSPRITE_API_KEY (or OPENAI_API_KEY) environment variable, "
            "or create a gitignored .env file with PIXELSPRITE_API_URL and PIXELSPRITE_API_KEY."
        )

    return {
        "base_url": _normalize_base_url(env_url or "https://api.openai.com/v1"),
        "api_key": env_key,
        "model": env_model or "gpt-image-2.6-sunburst",
    }


def _pil_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    return buf.getvalue()


def _extract_image_from_response(parsed: dict) -> Image.Image:
    item = None
    if isinstance(parsed.get("data"), list) and parsed["data"]:
        item = parsed["data"][0]
    elif isinstance(parsed.get("images"), list) and parsed["images"]:
        item = parsed["images"][0]
    elif isinstance(parsed.get("output"), list) and parsed["output"]:
        item = parsed["output"][0]
    else:
        item = parsed

    if isinstance(item, dict) and item.get("b64_json"):
        raw = base64.b64decode(item["b64_json"])
        return Image.open(io.BytesIO(raw)).convert("RGBA")

    url = None
    if isinstance(item, dict):
        url = item.get("url") or item.get("image_url")
    elif isinstance(item, str) and item.startswith("http"):
        url = item

    if url:
        with urllib.request.urlopen(url, timeout=120) as resp:
            return Image.open(io.BytesIO(resp.read())).convert("RGBA")

    raise RuntimeError(f"No image data in API response: {json.dumps(parsed)[:350]}")


def generate_image(
    prompt: str,
    cfg: dict[str, str],
    size: str = "1024x1024",
    background: str = "transparent",
    complexity: str = "high",
) -> Image.Image:
    payload = {
        "model": cfg["model"],
        "prompt": prompt,
        "n": 1,
        "size": size,
        "background": background,
        "complexity": complexity,
        "output_format": "png",
    }
    req = urllib.request.Request(
        f"{cfg['base_url']}/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        return _extract_image_from_response(parsed)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:400]
        raise RuntimeError(f"Images API generate failed (HTTP {e.code}): {body}") from e


def _build_multipart_body(fields: list[tuple[str, str]], files: list[tuple[str, str, bytes]]) -> tuple[bytes, str]:
    boundary = f"----PixelSpriteBoundary{uuid.uuid4().hex}"
    parts: list[bytes] = []
    for name, val in fields:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode("utf-8")
        )
    for field_name, filename, data in files:
        header = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"\r\n"
            f"Content-Type: image/png\r\n\r\n"
        ).encode("utf-8")
        parts.append(header + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def edit_images(
    prompt: str,
    ref_images: list[Image.Image],
    cfg: dict[str, str],
    size: str = "1536x1024",
    background: str = "transparent",
    complexity: str = "high",
) -> Image.Image:
    """Call /v1/images/edits with multipart/form-data (and automatic JSON fallback for custom gateways)."""
    field_name = "image[]" if len(ref_images) > 1 else "image"
    fields = [
        ("model", cfg["model"]),
        ("prompt", prompt),
        ("n", "1"),
        ("size", size),
        ("background", background),
        ("complexity", complexity),
        ("output_format", "png"),
    ]
    files = [(field_name, f"ref_{i}.png", _pil_to_png_bytes(im)) for i, im in enumerate(ref_images)]
    body, content_type = _build_multipart_body(fields, files)

    req = urllib.request.Request(
        f"{cfg['base_url']}/images/edits",
        data=body,
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": content_type,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        return _extract_image_from_response(parsed)
    except urllib.error.HTTPError as e:
        err_text = e.read().decode("utf-8", errors="ignore")
        if e.code in (400, 415, 422):
            # Fallback to JSON edits format supported by some proxy gateways
            json_payload = {
                "model": cfg["model"],
                "prompt": prompt,
                "n": 1,
                "size": size,
                "background": background,
                "complexity": complexity,
                "output_format": "png",
                "images": [
                    {"image_url": "data:image/png;base64," + base64.b64encode(_pil_to_png_bytes(im)).decode("ascii")}
                    for im in ref_images
                ],
            }
            req2 = urllib.request.Request(
                f"{cfg['base_url']}/images/edits",
                data=json.dumps(json_payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req2, timeout=240) as resp2:
                    parsed2 = json.loads(resp2.read().decode("utf-8"))
                return _extract_image_from_response(parsed2)
            except urllib.error.HTTPError as e2:
                body2 = e2.read().decode("utf-8", errors="ignore")[:400]
                raise RuntimeError(f"Images API edit failed (HTTP {e2.code}): {body2}") from e2
        raise RuntimeError(f"Images API edit failed (HTTP {e.code}): {err_text[:400]}") from e
