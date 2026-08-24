# -*- coding: utf-8 -*-
"""Optimize place photos and group them by map filter type.

Real photos go to Images/places/{type}/{slug}.jpg (max edge 1280px, JPEG).
Placeholder copies of _types are removed; coords.image then points at _types.
Does not touch food-*/quiz-* shared images.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
I18N_TRANSPORT = ROOT / "i18n" / "pages" / "transport"
MAX_EDGE = 1280
JPEG_QUALITY = 85
KEEP_ROOT_PREFIXES = (
    "food-",
    "quiz-",
)
KEEP_ROOT_NAMES = {"_types"}


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()


def type_hashes() -> dict[str, str]:
    out = {}
    tdir = IMG / "_types"
    if not tdir.exists():
        return out
    for f in tdir.glob("*.jpg"):
        out[sha1(f)] = f.stem
    return out


def parse_places() -> list[dict]:
    text = COORDS.read_text(encoding="utf-8")
    recs = re.findall(
        r'\{\s*slug:\s*"([^"]+)"\s*,\s*lat:\s*([^,]+),\s*lng:\s*([^,]+),\s*'
        r'region:\s*"([^"]*)"\s*,\s*type:\s*"([^"]+)"\s*,\s*note:\s*"([^"]*)"'
        r'\s*,\s*image:\s*"([^"]*)"',
        text,
    )
    places = []
    for slug, lat, lng, region, typ, note, image in recs:
        places.append(
            {
                "slug": slug,
                "type": typ,
                "note": note,
                "image": image,
            }
        )
    return places


def find_existing(slug: str) -> Path | None:
    for folder in (IMG, *(p for p in IMG.iterdir() if p.is_dir() and p.name != "_types")):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            cand = folder / f"{slug}{ext}"
            if cand.exists():
                return cand
    return None


def optimize_to_jpeg(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if im.mode == "P":
            im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > MAX_EDGE:
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    data = buf.getvalue()
    tmp = dest.with_suffix(".tmp.jpg")
    tmp.write_bytes(data)
    tmp.replace(dest)


def rewrite_coords(places: list[dict]) -> None:
    text = COORDS.read_text(encoding="utf-8")
    for p in places:
        slug = p["slug"]
        new_image = p["new_image"]
        pat = re.compile(
            rf'(slug:\s*"{re.escape(slug)}"[\s\S]*?image:\s*")[^"]*"'
        )
        text, n = pat.subn(rf'\1{new_image}"', text, count=1)
        if n != 1:
            print(f"WARN coords image not rewritten: {slug}", flush=True)
    COORDS.write_text(text, encoding="utf-8")


def rewrite_i18n(slug_to_image: dict[str, str]) -> int:
    n = 0
    if not I18N_TRANSPORT.exists():
        return 0
    for path in I18N_TRANSPORT.glob("*.json"):
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        places = data.get("places") or {}
        changed = False
        for slug, rec in places.items():
            if not isinstance(rec, dict):
                continue
            img = slug_to_image.get(slug)
            if img and rec.get("image") and rec["image"] != img:
                rec["image"] = img
                changed = True
        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            n += 1
    return n


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = type_hashes()
    places = parse_places()
    moved = skipped_ph = optimized = 0
    slug_to_image = {}
    for p in places:
        slug = p["slug"]
        typ = p["type"]
        src = find_existing(slug)
        if src is None:
            slug_to_image[slug] = f"Images/places/_types/{typ}.jpg"
            p["new_image"] = slug_to_image[slug]
            continue
        if sha1(src) in hashes:
            skipped_ph += 1
            if src.parent != IMG / "_types":
                try:
                    src.unlink()
                except OSError:
                    pass
            slug_to_image[slug] = f"Images/places/_types/{typ}.jpg"
            p["new_image"] = slug_to_image[slug]
            continue
        dest = IMG / typ / f"{slug}.jpg"
        if src.resolve() != dest.resolve():
            optimize_to_jpeg(src, dest)
            if src.resolve() != dest.resolve():
                try:
                    src.unlink()
                except OSError:
                    pass
            moved += 1
        else:
            # already in type folder; re-optimize in place
            optimize_to_jpeg(src, dest)
        optimized += 1
        slug_to_image[slug] = f"Images/places/{typ}/{slug}.jpg"
        p["new_image"] = slug_to_image[slug]
        print(f"OK {typ}/{slug}.jpg", flush=True)

    rewrite_coords(places)
    i18n_n = rewrite_i18n(slug_to_image)
    print(
        f"DONE moved={moved} optimized={optimized} placeholders_removed={skipped_ph} i18n_files={i18n_n}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
