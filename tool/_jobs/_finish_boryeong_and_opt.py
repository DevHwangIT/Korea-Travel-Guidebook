# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
I18N = ROOT / "i18n" / "pages" / "transport"
MAX = 1280


def optimize_if_needed(path: Path) -> bool:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    if max(w, h) <= MAX and path.stat().st_size < 450_000:
        return False
    if im.mode != "RGB":
        im = im.convert("RGB")
    if max(im.size) > MAX:
        im.thumbnail((MAX, MAX), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85, optimize=True, progressive=True)
    tmp = path.with_suffix(".tmp.jpg")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(path)
    print(f"opt {path.relative_to(IMG)} {w}x{h}", flush=True)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = COORDS.read_text(encoding="utf-8")
    text, n = re.subn(
        r'(slug:\s*"boryeong-lake"[\s\S]*?image:\s*")[^"]*"',
        r'\1Images/places/lake/boryeong-lake.jpg"',
        text,
        count=1,
    )
    print("coords rewrite", n, flush=True)
    old = " * image: local real photograph under Images/places/{slug}.jpg (Wikimedia Commons / free licenses)."
    new = " * image: local real photograph under Images/places/{type}/{slug}.jpg (Wikimedia Commons / free licenses)."
    if old in text:
        text = text.replace(old, new)
        print("coords comment updated", flush=True)
    COORDS.write_text(text, encoding="utf-8")
    for path in I18N.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        rec = (data.get("places") or {}).get("boryeong-lake")
        if isinstance(rec, dict) and rec.get("image"):
            rec["image"] = "Images/places/lake/boryeong-lake.jpg"
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("i18n", path.name, flush=True)

    opt = 0
    for folder in (IMG, IMG / "_types", IMG / "_courses"):
        if not folder.exists():
            continue
        for f in folder.glob("*.jpg"):
            if folder == IMG and not (
                f.name.startswith("food-") or f.name.startswith("quiz-")
            ):
                continue
            if optimize_if_needed(f):
                opt += 1
    print("optimized", opt, flush=True)
    ph = len(re.findall(r'image: "Images/places/_types/', COORDS.read_text(encoding="utf-8")))
    print("placeholders left", ph, flush=True)
    root = [p.name for p in IMG.glob("*.jpg")]
    print("root jpgs", len(root), flush=True)
    print("type dirs", sorted(p.name for p in IMG.iterdir() if p.is_dir()), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
