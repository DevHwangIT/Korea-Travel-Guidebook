# -*- coding: utf-8 -*-
"""List 명소 (nature/heritage/port) still using type placeholders."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
TYPES = {"nature", "heritage", "port"}


def sha1(p: Path) -> str:
    h = hashlib.sha1()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = COORDS.read_text(encoding="utf-8")
    type_hashes = {}
    for name in ("nature", "heritage", "port", "city", "mountain", "beach", "lake"):
        f = IMG / "_types" / f"{name}.jpg"
        if f.exists():
            type_hashes[sha1(f)] = name

    recs = re.findall(
        r'slug:\s*"([^"]+)".*?type:\s*"([^"]+)".*?note:\s*"([^"]*)"',
        text,
        re.S,
    )
    missing = []
    placeholder_copy = []
    ok = []
    for slug, typ, note in recs:
        if typ not in TYPES:
            continue
        f = IMG / f"{slug}.jpg"
        png = IMG / f"{slug}.png"
        webp = IMG / f"{slug}.webp"
        path = f if f.exists() else (png if png.exists() else (webp if webp.exists() else None))
        if path is None:
            missing.append((slug, typ, note))
            continue
        digest = sha1(path)
        if digest in type_hashes:
            placeholder_copy.append((slug, typ, note, type_hashes[digest], path.stat().st_size))
        else:
            ok.append(slug)

    print(f"OK unique photos: {len(ok)}")
    print(f"MISSING file (falls back to _types): {len(missing)}")
    for row in missing:
        print(f"  MISS  [{row[1]}] {row[0]} — {row[2]}")
    print(f"PLACEHOLDER COPY: {len(placeholder_copy)}")
    for row in placeholder_copy:
        print(f"  COPY  [{row[1]}={row[3]}] {row[0]} — {row[2]} ({row[4]} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
