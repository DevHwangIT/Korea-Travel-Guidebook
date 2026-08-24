# -*- coding: utf-8 -*-
"""Move leftover root place photos used by Seoul courses into _courses/."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
DEST = IMG / "_courses"
KEEP_PREFIXES = ("food-", "quiz-")
FILES = [
    ROOT / "data" / "courses" / "seoul-curated.js",
    ROOT / "js" / "course-recommend.js",
]
MAX_EDGE = 1280


def optimize_jpeg(src: Path, dest: Path) -> None:
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
    if max(im.size) > MAX_EDGE:
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85, optimize=True, progressive=True)
    tmp = dest.with_suffix(".tmp.jpg")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(dest)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    moved: dict[str, str] = {}
    DEST.mkdir(parents=True, exist_ok=True)
    for f in list(IMG.glob("*.jpg")):
        if f.name.startswith(KEEP_PREFIXES):
            continue
        dest = DEST / f.name
        optimize_jpeg(f, dest)
        f.unlink()
        moved[f.stem] = f"Images/places/_courses/{f.name}"
        print(f"moved {f.name}", flush=True)

    total = 0
    for path in FILES:
        text = path.read_text(encoding="utf-8")

        def repl(m: re.Match[str]) -> str:
            nonlocal total
            dots = m.group(1)
            slug = m.group(2)
            ext = m.group(3)
            if slug.startswith(KEEP_PREFIXES):
                return m.group(0)
            new = moved.get(slug)
            if not new:
                return m.group(0)
            total += 1
            return f"{dots}{new}"

        text2 = re.sub(
            r'((?:\.\./)*)Images/places/([a-z0-9-]+)\.(jpg|png|webp)',
            repl,
            text,
        )
        path.write_text(text2, encoding="utf-8")
    print(f"DONE moved={len(moved)} path_rewrites={total}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
